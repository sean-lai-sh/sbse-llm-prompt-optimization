"""Tests for src/improver.py — NIM endpoint is fully mocked."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.improver import (
    _parse_variants,
    _prompt_hash,
    improve_prompts,
)


# ---------------------------------------------------------------------------
# Unit tests for pure helpers
# ---------------------------------------------------------------------------


def test_parse_variants_basic():
    raw = "Variant one\nVariant two\nVariant three\n"
    result = _parse_variants(raw, 3)
    assert result == ["Variant one", "Variant two", "Variant three"]


def test_parse_variants_caps_at_max_n():
    raw = "A\nB\nC\nD\nE"
    result = _parse_variants(raw, 2)
    assert result == ["A", "B"]


def test_parse_variants_skips_blank_lines():
    raw = "First\n\nSecond\n\nThird"
    result = _parse_variants(raw, 5)
    assert result == ["First", "Second", "Third"]


def test_prompt_hash_deterministic():
    prompts = ["Summarize this function.", "Be concise."]
    assert _prompt_hash(prompts) == _prompt_hash(prompts)


def test_prompt_hash_differs_on_different_input():
    assert _prompt_hash(["A"]) != _prompt_hash(["B"])


# ---------------------------------------------------------------------------
# improve_prompts — mocked NIM endpoint + isolated cache
# ---------------------------------------------------------------------------


def _make_mock_response(content: str) -> MagicMock:
    """Build a fake openai.ChatCompletion response."""
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


@patch("src.improver.openai.OpenAI")
def test_improve_prompts_returns_variants(mock_openai_cls, tmp_path, monkeypatch):
    """Happy-path: NIM returns three variants, all are parsed and returned."""
    monkeypatch.setattr("src.improver._CACHE_DIR", tmp_path)

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_mock_response(
        "Improved variant 1\nImproved variant 2\nImproved variant 3"
    )

    top = ["Summarize in 2 sentences.", "You are an engineer. Summarize this."]
    result = improve_prompts(
        top_prompts=top,
        n=3,
        generation=0,
        model="meta/llama-3.1-70b-instruct",
        api_key="test-key",
    )

    assert len(result) == 3
    assert result[0] == "Improved variant 1"
    mock_client.chat.completions.create.assert_called_once()


@patch("src.improver.openai.OpenAI")
def test_improve_prompts_empty_input(mock_openai_cls):
    """Empty top_prompts returns empty list without calling the API."""
    result = improve_prompts(top_prompts=[], n=3, generation=0, api_key="test-key")
    assert result == []
    mock_openai_cls.assert_not_called()


@patch("src.improver.openai.OpenAI")
def test_improve_prompts_uses_cache_on_second_call(mock_openai_cls, tmp_path, monkeypatch):
    """Second call with the same prompts/generation reads from disk cache."""
    monkeypatch.setattr("src.improver._CACHE_DIR", tmp_path)

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_mock_response(
        "Cached variant 1\nCached variant 2"
    )

    top = ["Prompt A"]
    improve_prompts(top_prompts=top, n=2, generation=1, api_key="test-key")
    improve_prompts(top_prompts=top, n=2, generation=1, api_key="test-key")

    # API should only be called once; second call hits the cache
    assert mock_client.chat.completions.create.call_count == 1


@patch("src.improver.openai.OpenAI")
def test_improve_prompts_retries_on_server_error(mock_openai_cls, tmp_path, monkeypatch):
    """Transient 500 errors trigger retry logic before succeeding."""
    monkeypatch.setattr("src.improver._CACHE_DIR", tmp_path)
    import openai as oai

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    server_error = oai.APIStatusError(
        "server error",
        response=MagicMock(status_code=500),
        body={},
    )
    good_response = _make_mock_response("Retry succeeded")

    mock_client.chat.completions.create.side_effect = [
        server_error,
        good_response,
    ]

    with patch("src.improver.time.sleep"):
        result = improve_prompts(
            top_prompts=["Some prompt"],
            n=1,
            generation=0,
            api_key="test-key",
            max_retries=3,
        )

    assert result == ["Retry succeeded"]
    assert mock_client.chat.completions.create.call_count == 2


@patch("src.improver.openai.OpenAI")
def test_improve_prompts_raises_on_client_error(mock_openai_cls, tmp_path, monkeypatch):
    """4xx errors (client errors) are not retried and propagate immediately."""
    monkeypatch.setattr("src.improver._CACHE_DIR", tmp_path)
    import openai as oai

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    client_error = oai.APIStatusError(
        "unauthorized",
        response=MagicMock(status_code=401),
        body={},
    )
    mock_client.chat.completions.create.side_effect = client_error

    with pytest.raises(oai.APIStatusError):
        improve_prompts(
            top_prompts=["Some prompt"],
            n=1,
            generation=0,
            api_key="test-key",
        )

    assert mock_client.chat.completions.create.call_count == 1


@patch("src.improver.openai.OpenAI")
def test_improve_prompts_passes_model_and_key(mock_openai_cls, tmp_path, monkeypatch):
    """The configured model and API key are forwarded to the OpenAI client."""
    monkeypatch.setattr("src.improver._CACHE_DIR", tmp_path)

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_mock_response("Variant")

    improve_prompts(
        top_prompts=["Prompt"],
        n=1,
        generation=0,
        model="nvidia/nemotron-4-340b-instruct",
        api_key="my-nvidia-key",
    )

    mock_openai_cls.assert_called_once_with(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="my-nvidia-key",
    )
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "nvidia/nemotron-4-340b-instruct"
