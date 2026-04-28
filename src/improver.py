"""NIM-hosted LLM improver for directed GA mutation.

Uses the NVIDIA NIM OpenAI-compatible endpoint to rewrite the fittest
candidate prompts, producing improved offspring for the next generation.
Responses are cached per (content-hash, generation) to avoid redundant
API calls on re-runs.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import openai

from src.prompt import PromptTemplate

logger = logging.getLogger(__name__)

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"

_SYSTEM_PROMPT = (
    "You are a prompt engineering expert specializing in code summarization tasks. "
    "Analyze the given prompt templates and generate improved variants that produce "
    "higher-quality, more precise code summaries."
)

_USER_TEMPLATE = """\
You are a prompt engineering expert. Below are the highest-scoring prompt \
templates for a code summarization task, ranked by ROUGE-L fitness.

Top prompts:
{ranked_prompts}

Generate {n} new prompt variants that you predict will score higher.
Each variant must be a JSON object on its own line with keys: \
role, task, guard, format.
Return exactly {n} lines, one JSON object per line, no extra text."""


def _parse_variants(raw_text: str, expected: int) -> list[str]:
    """Extract non-empty lines from the model output.

    Pads with copies of the last line if fewer than *expected* are returned.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("NIM returned an empty response")
    while len(lines) < expected:
        lines.append(lines[-1])
    return lines[:expected]


class NIMImprover:
    """LLM-guided prompt improver using NVIDIA NIM."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        cache_dir: Path | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self._client = openai.OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=api_key or os.environ["NVIDIA_API_KEY"],
        )
        self._mem_cache: dict[str, list[str]] = {}
        self._cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def improve(
        self,
        top_templates: list[PromptTemplate],
        num_variants: int,
        generation: int = 0,
    ) -> list[PromptTemplate]:
        """Return *num_variants* improved PromptTemplates derived from *top_templates*.

        Results are cached per (content-hash, generation).
        """
        cache_key = self._make_cache_key(top_templates, num_variants, generation)
        cached = self._load_cache(cache_key)
        if cached is not None:
            logger.debug("improver cache hit for generation %d", generation)
            return [PromptTemplate.from_raw(s) for s in cached]

        raw_strings = self._call_nim(top_templates, num_variants)
        self._save_cache(cache_key, raw_strings)
        return [PromptTemplate.from_raw(s) for s in raw_strings]

    # ------------------------------------------------------------------
    # NIM call
    # ------------------------------------------------------------------

    def _build_user_message(
        self, top_templates: list[PromptTemplate], num_variants: int
    ) -> str:
        ranked = "\n".join(
            f"{i + 1}. {t.render_compact()}" for i, t in enumerate(top_templates)
        )
        return _USER_TEMPLATE.format(ranked_prompts=ranked, n=num_variants)

    def _call_nim(
        self,
        top_templates: list[PromptTemplate],
        num_variants: int,
        max_retries: int = 3,
    ) -> list[str]:
        user_msg = self._build_user_message(top_templates, num_variants)
        delay = 2.0

        last_exc: Exception | None = None
        for attempt in range(max_retries):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                )
                raw_text = response.choices[0].message.content or ""
                return self._parse_variants(raw_text, num_variants)
            except openai.RateLimitError as exc:
                logger.warning("NIM rate limit on attempt %d: %s", attempt + 1, exc)
                last_exc = exc
            except openai.APIConnectionError as exc:
                logger.warning("NIM connection error on attempt %d: %s", attempt + 1, exc)
                last_exc = exc
            except openai.APIStatusError as exc:
                if exc.status_code < 500:
                    raise
                logger.warning("NIM server error on attempt %d: %s", attempt + 1, exc)
                last_exc = exc

            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2

        raise RuntimeError(
            f"NIM improver failed after {max_retries} attempts"
        ) from last_exc

    @staticmethod
    def _parse_variants(raw_text: str, expected: int) -> list[str]:
        return _parse_variants(raw_text, expected)

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _make_cache_key(
        self,
        top_templates: list[PromptTemplate],
        num_variants: int,
        generation: int,
    ) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "templates": [t.to_dict() for t in top_templates],
                "num_variants": num_variants,
                "generation": generation,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def _load_cache(self, key: str) -> list[str] | None:
        if key in self._mem_cache:
            return self._mem_cache[key]
        if self._cache_dir:
            path = self._cache_dir / f"{key}.json"
            if path.exists():
                data: list[str] = json.loads(path.read_text())
                self._mem_cache[key] = data
                return data
        return None

    def _save_cache(self, key: str, variants: list[str]) -> None:
        self._mem_cache[key] = variants
        if self._cache_dir:
            path = self._cache_dir / f"{key}.json"
            path.write_text(json.dumps(variants, indent=2))


# ------------------------------------------------------------------
# Factory
# ------------------------------------------------------------------

def create_improver_from_config(config: dict[str, Any]) -> NIMImprover:
    """Build a NIMImprover from the ``improver`` section of config.yaml."""
    cfg = config.get("improver", {})
    cache_dir = Path(cfg["cache_dir"]) if "cache_dir" in cfg else None
    return NIMImprover(
        model=cfg.get("model", DEFAULT_MODEL),
        cache_dir=cache_dir,
    )
