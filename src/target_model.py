"""Fixed target model for the GA fitness evaluation loop.

This module wraps the NVIDIA NIM OpenAI-compatible chat completions API and
exposes a single function, :func:`generate_summary`, that the fitness module
(issue #7) calls once per (function x candidate prompt) in the GA inner loop.

The target model is held FIXED across the entire experiment -- only the
prompt template evolves. Determinism (``temperature=0``) and reliability
(retries with exponential backoff) are therefore important.

Contract
--------
``generate_summary(prompt, code)`` builds the OpenAI messages list as::

    [
        {"role": "system", "content": prompt},
        {"role": "user",   "content": code},
    ]

That is, ``prompt`` is the assembled instruction block (role/task/guard/
format -- see :meth:`src.prompt.PromptTemplate.render_instructions`) and
``code`` is the raw function body to summarize. Callers should NOT pre-embed
the code in ``prompt``; pass the components separately.
"""

from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

import openai
from dotenv import load_dotenv

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 512
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_INITIAL_BACKOFF = 1.0

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = _REPO_ROOT / "config.yaml"

logger = logging.getLogger(__name__)

# Match a fenced code block at the start/end of the response, e.g.
#     ```python\n...\n```
# or  ```\n...\n```
# Captures the inner content.
_FENCE_BLOCK_RE = re.compile(
    r"^\s*```[a-zA-Z0-9_+-]*\s*\n(?P<body>.*?)\n?```\s*$",
    re.DOTALL,
)


def _load_target_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """Lazily load the ``target_model`` section from ``config.yaml``.

    Missing file or missing section -> empty dict (callers fall back to
    module-level defaults). PyYAML import is also lazy so importing this
    module does not require yaml at import time for callers that pass all
    settings explicitly.
    """
    path = config_path or _DEFAULT_CONFIG_PATH
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        return {}
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        return {}
    section = data.get("target_model") or {}
    return section if isinstance(section, dict) else {}


def _strip_markdown_fences(text: str) -> str:
    """Remove a single surrounding markdown code fence and inline backticks.

    Handles the two common shapes models produce:
      - block fence:  ```lang\\n...\\n```
      - inline fence: `...`
    Any leading/trailing whitespace on the result is also stripped.
    """
    s = text.strip()
    match = _FENCE_BLOCK_RE.match(s)
    if match:
        s = match.group("body").strip()
    elif len(s) >= 2 and s.startswith("`") and s.endswith("`") and "\n" not in s:
        # Inline single-backtick fence, e.g. `summary text`.
        s = s[1:-1].strip()
    return s


def _is_transient_error(exc: BaseException) -> bool:
    """Return True if ``exc`` is a transient error worth retrying.

    Transient = network/connection error, rate limit, or HTTP 5xx. 4xx
    surfaces immediately because retrying will not change the outcome.
    """
    if isinstance(exc, (openai.APIConnectionError, openai.APITimeoutError)):
        return True
    if isinstance(exc, openai.RateLimitError):
        return True
    if isinstance(exc, openai.APIStatusError):
        return exc.status_code >= 500
    return False


def generate_summary(
    prompt: str,
    code: str,
    *,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    config_path: Optional[Path] = None,
    client: Optional[Any] = None,
) -> str:
    """Call the NIM target model to produce a summary for ``code``.

    Args:
        prompt: Assembled instruction block (role/task/guard/format). Sent as
            the ``system`` message. Does NOT need to embed the code.
        code: Raw function body to summarize. Sent as the ``user`` message.
        model: Override the model id; defaults to the value in
            ``config.yaml``'s ``target_model.model`` section, or
            :data:`DEFAULT_MODEL`.
        api_key: Override the NVIDIA API key; defaults to the
            ``NVIDIA_API_KEY`` environment variable (loaded from ``.env``).
        config_path: Override the path to ``config.yaml`` (mainly for tests).
        client: Optional pre-built OpenAI-compatible client (mainly for
            tests). When provided, ``api_key`` is not required.

    Returns:
        The model's summary, with surrounding markdown code fences and
        whitespace stripped.

    Raises:
        ValueError: ``NVIDIA_API_KEY`` is missing and no ``client`` was
            provided.
        openai.APIStatusError: HTTP 4xx response (surfaced immediately).
        openai.APIError: After ``retry_attempts`` transient failures.
    """
    cfg = _load_target_config(config_path)
    chosen_model = model or cfg.get("model") or DEFAULT_MODEL
    temperature = cfg.get("temperature", DEFAULT_TEMPERATURE)
    max_tokens = cfg.get("max_tokens", DEFAULT_MAX_TOKENS)
    retry_attempts = int(cfg.get("retry_attempts", DEFAULT_RETRY_ATTEMPTS))
    initial_backoff = float(
        cfg.get("retry_initial_backoff_seconds", DEFAULT_RETRY_INITIAL_BACKOFF)
    )
    if retry_attempts < 1:
        raise ValueError(
            f"retry_attempts must be >= 1, got {retry_attempts}"
        )

    if client is None:
        if api_key is None:
            load_dotenv()
            api_key = os.environ.get("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError(
                "NVIDIA_API_KEY is not set. Add it to your .env file "
                "(see .env.example)."
            )
        client = openai.OpenAI(base_url=NIM_BASE_URL, api_key=api_key, max_retries=0)

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": code},
    ]

    last_error: Optional[BaseException] = None
    for attempt in range(1, retry_attempts + 1):
        start = time.monotonic()
        try:
            response = client.chat.completions.create(
                model=chosen_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except openai.APIStatusError as exc:
            elapsed = time.monotonic() - start
            logger.debug(
                "target_model call failed in %.3fs (attempt %d/%d): %s",
                elapsed, attempt, retry_attempts, exc,
            )
            if not _is_transient_error(exc):
                # 4xx -> surface immediately, no further retries.
                raise
            last_error = exc
        except (openai.APIConnectionError, openai.APITimeoutError,
                openai.RateLimitError) as exc:
            elapsed = time.monotonic() - start
            logger.debug(
                "target_model call failed in %.3fs (attempt %d/%d): %s",
                elapsed, attempt, retry_attempts, exc,
            )
            last_error = exc
        else:
            elapsed = time.monotonic() - start
            logger.debug(
                "target_model call succeeded in %.3fs (attempt %d/%d, model=%s)",
                elapsed, attempt, retry_attempts, chosen_model,
            )
            raw = response.choices[0].message.content or ""
            return _strip_markdown_fences(raw)

        if attempt < retry_attempts:
            sleep_for = initial_backoff * (2 ** (attempt - 1))
            time.sleep(sleep_for)

    assert last_error is not None
    raise last_error
