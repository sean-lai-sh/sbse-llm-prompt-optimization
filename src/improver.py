"""NIM-powered prompt improver for the GA loop.

Uses the NVIDIA NIM OpenAI-compatible API to rewrite the top-K candidate
prompt templates into N potentially better variants via directed mutation.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Optional

import openai
from dotenv import load_dotenv

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"

_CACHE_DIR = Path(__file__).resolve().parent.parent / ".nim_cache"

_SYSTEM_PROMPT = (
    "You are a prompt engineering expert specializing in code summarization tasks."
)

_IMPROVER_TEMPLATE = """\
Below are the highest-scoring prompt templates for a code summarization task, \
ranked by ROUGE-L fitness.

Top prompts:
{ranked_prompts}

Generate {n} new prompt variants that you predict will score higher. \
Return only the prompt text, one per line, no numbering."""


def _prompt_hash(prompts: list[str]) -> str:
    combined = "\n---\n".join(prompts)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def _cache_path(prompt_hash: str, generation: int, n: int, model: str) -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_model = model.replace("/", "_")
    return _CACHE_DIR / f"{prompt_hash}_gen{generation}_n{n}_{safe_model}.json"


def _load_cache(prompt_hash: str, generation: int, n: int, model: str) -> Optional[list[str]]:
    path = _cache_path(prompt_hash, generation, n, model)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            try:
                path.unlink()
            except OSError:
                pass
            return None
    return None


def _save_cache(prompt_hash: str, generation: int, n: int, model: str, variants: list[str]) -> None:
    _cache_path(prompt_hash, generation, n, model).write_text(
        json.dumps(variants), encoding="utf-8"
    )


def _parse_variants(raw: str, max_n: int) -> list[str]:
    """Extract up to max_n non-empty lines from the model response."""
    lines = [line.strip() for line in raw.splitlines()]
    return [line for line in lines if line][:max_n]


def improve_prompts(
    top_prompts: list[str],
    n: int = 3,
    generation: int = 0,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    max_retries: int = 3,
) -> list[str]:
    """Call NIM to generate improved prompt variants from the top candidates.

    Args:
        top_prompts: Ranked list of highest-scoring prompt strings.
        n: Number of improved variants to request.
        generation: Current GA generation number (used for cache keying).
        model: NIM model identifier (configurable via config.yaml).
        api_key: NVIDIA_API_KEY; falls back to the environment variable if None.
        max_retries: Max number of retries on transient errors (0 = one attempt, no retries; must be >= 0).

    Returns:
        List of up to ``n`` improved prompt strings.
    """
    if max_retries < 0:
        raise ValueError(f"max_retries must be >= 0, got {max_retries}")
    if not top_prompts:
        return []

    ph = _prompt_hash(top_prompts)
    cached = _load_cache(ph, generation, n, model)
    if cached is not None:
        return cached

    if api_key is None:
        load_dotenv()
        api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError(
            "NVIDIA_API_KEY is not set. Add it to your .env file (see .env.example)."
        )

    client = openai.OpenAI(base_url=NIM_BASE_URL, api_key=api_key)

    ranked = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(top_prompts))
    user_content = _IMPROVER_TEMPLATE.format(ranked_prompts=ranked, n=n)

    delay = 2.0
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            raw = response.choices[0].message.content or ""
            variants = _parse_variants(raw, n)
            _save_cache(ph, generation, n, model, variants)
            return variants
        except openai.RateLimitError as exc:
            last_error = exc
        except openai.APIConnectionError as exc:
            last_error = exc
        except openai.APIStatusError as exc:
            if exc.status_code < 500:
                raise
            last_error = exc

        print(
            f"  NIM attempt {attempt + 1}/{max_retries + 1} failed: {last_error}",
            file=sys.stderr,
        )
        if attempt < max_retries:
            sleep_for = delay + random.uniform(0, 1)
            print(f"  Retrying in {sleep_for:.1f}s ...", file=sys.stderr)
            time.sleep(sleep_for)
            delay = min(delay * 2, 60.0)

    assert last_error is not None
    raise last_error
