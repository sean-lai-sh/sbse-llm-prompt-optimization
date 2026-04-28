"""Integration tests for src/improver.py.

The NIM endpoint is mocked so no real API key is required.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.improver import NIMImprover, _parse_variants
from src.prompt import PromptTemplate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_template(role: str = "You are an engineer.", task: str = "Summarise.", guard: str = "", fmt: str = "") -> PromptTemplate:
    return PromptTemplate(role=role, task=task, guard=guard, format=fmt)


def _nim_response(lines: list[str]) -> MagicMock:
    """Build a mock openai ChatCompletion response returning *lines* joined by newlines."""
    choice = MagicMock()
    choice.message.content = "\n".join(lines)
    response = MagicMock()
    response.choices = [choice]
    return response


# ---------------------------------------------------------------------------
# _parse_variants unit tests
# ---------------------------------------------------------------------------

class TestParseVariants:
    def test_exact_count(self):
        raw = "line one\nline two\nline three"
        result = _parse_variants(raw, 3)
        assert result == ["line one", "line two", "line three"]

    def test_pads_when_too_few(self):
        raw = "only one"
        result = _parse_variants(raw, 3)
        assert result == ["only one", "only one", "only one"]

    def test_truncates_when_too_many(self):
        raw = "a\nb\nc\nd\ne"
        result = _parse_variants(raw, 2)
        assert result == ["a", "b"]

    def test_skips_blank_lines(self):
        raw = "alpha\n\nbeta\n\ngamma"
        result = _parse_variants(raw, 3)
        assert result == ["alpha", "beta", "gamma"]

    def test_empty_response_raises(self):
        with pytest.raises(ValueError, match="empty response"):
            _parse_variants("   \n   ", 2)


# ---------------------------------------------------------------------------
# NIMImprover.improve — mocking the OpenAI client
# ---------------------------------------------------------------------------

class TestNIMImprover:
    def _build_improver(self, tmp_path: Path | None = None) -> NIMImprover:
        with patch("src.improver.openai.OpenAI"):
            imp = NIMImprover(model="test-model", cache_dir=tmp_path, api_key="fake-key")
        return imp

    # -- output parsing --

    def test_improve_returns_prompt_templates(self, tmp_path):
        imp = self._build_improver(tmp_path)
        json_variants = [
            json.dumps({"role": "You are a senior engineer.", "task": "Summarise briefly.", "guard": "Be concise.", "format": "Plain prose."}),
            json.dumps({"role": "You are an expert.", "task": "Describe the function.", "guard": "", "format": ""}),
            json.dumps({"role": "", "task": "Give a technical summary.", "guard": "No code.", "format": ""}),
        ]
        imp._client.chat.completions.create.return_value = _nim_response(json_variants)

        templates = [_make_template()]
        result = imp.improve(templates, num_variants=3, generation=1)

        assert len(result) == 3
        assert all(isinstance(t, PromptTemplate) for t in result)
        assert result[0].role == "You are a senior engineer."
        assert result[0].task == "Summarise briefly."

    def test_improve_parses_raw_string_fallback(self, tmp_path):
        imp = self._build_improver(tmp_path)
        imp._client.chat.completions.create.return_value = _nim_response(
            ["not json at all", "also not json"]
        )
        result = imp.improve([_make_template()], num_variants=2, generation=0)
        assert len(result) == 2
        assert result[0].task == "not json at all"
        assert result[1].task == "also not json"

    # -- caching --

    def test_improve_caches_result_in_memory(self, tmp_path):
        imp = self._build_improver(tmp_path)
        imp._client.chat.completions.create.return_value = _nim_response(
            [json.dumps({"role": "", "task": "T", "guard": "", "format": ""})]
        )
        templates = [_make_template()]
        imp.improve(templates, num_variants=1, generation=5)
        imp.improve(templates, num_variants=1, generation=5)

        # Second call should be served from cache — API called exactly once.
        assert imp._client.chat.completions.create.call_count == 1

    def test_improve_caches_to_disk(self, tmp_path):
        imp = self._build_improver(tmp_path)
        imp._client.chat.completions.create.return_value = _nim_response(
            [json.dumps({"role": "", "task": "cached", "guard": "", "format": ""})]
        )
        templates = [_make_template()]
        imp.improve(templates, num_variants=1, generation=2)

        cache_files = list(tmp_path.glob("*.json"))
        assert len(cache_files) == 1

    def test_improve_loads_from_disk_cache(self, tmp_path):
        imp = self._build_improver(tmp_path)
        imp._client.chat.completions.create.return_value = _nim_response(
            [json.dumps({"role": "", "task": "original", "guard": "", "format": ""})]
        )
        templates = [_make_template()]
        imp.improve(templates, num_variants=1, generation=3)

        # Create a fresh improver that shares the same cache directory.
        imp2 = self._build_improver(tmp_path)
        result = imp2.improve(templates, num_variants=1, generation=3)

        assert imp2._client.chat.completions.create.call_count == 0
        assert result[0].task == "original"

    # -- retry behaviour --

    def test_improve_retries_on_rate_limit(self, tmp_path):
        import openai as _openai

        imp = self._build_improver(tmp_path)
        good_response = _nim_response(
            [json.dumps({"role": "", "task": "retry success", "guard": "", "format": ""})]
        )
        imp._client.chat.completions.create.side_effect = [
            _openai.RateLimitError("rate limit", response=MagicMock(), body={}),
            good_response,
        ]

        with patch("src.improver.time.sleep"):
            result = imp.improve([_make_template()], num_variants=1, generation=0)

        assert result[0].task == "retry success"
        assert imp._client.chat.completions.create.call_count == 2

    def test_improve_raises_after_max_retries(self, tmp_path):
        import openai as _openai

        imp = self._build_improver(tmp_path)
        imp._client.chat.completions.create.side_effect = _openai.RateLimitError(
            "rate limit", response=MagicMock(), body={}
        )

        with patch("src.improver.time.sleep"):
            with pytest.raises(RuntimeError, match="failed after"):
                imp.improve([_make_template()], num_variants=1, generation=0)

    # -- different generations get different cache keys --

    def test_different_generations_have_different_cache_keys(self):
        with patch("src.improver.openai.OpenAI"):
            imp = NIMImprover(model="m", api_key="k")
        templates = [_make_template()]
        key1 = imp._make_cache_key(templates, 3, generation=1)
        key2 = imp._make_cache_key(templates, 3, generation=2)
        assert key1 != key2
