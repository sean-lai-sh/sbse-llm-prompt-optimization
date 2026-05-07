#!/usr/bin/env python3
"""Generate ground-truth reference summaries for every benchmark function.

Calls Claude Opus (model `claude-opus-4-7`) once per file in the input
directory, writing the resulting 2-4 sentence summary to the output
directory as ``<basename>.txt``. Resumes by skipping files whose reference
already exists. Logs token usage and estimated cost on completion.

Usage:
    python scripts/generate_references.py                 # data/functions -> data/references
    python scripts/generate_references.py --dry-run       # list calls, no API requests
    python scripts/generate_references.py --limit 5       # cap to N files (debugging)
    python scripts/generate_references.py \\               # held-out test set
        --functions-dir data/test/functions \\
        --references-dir data/test/references
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"
DEFAULT_REFERENCES_DIR = REPO_ROOT / "data" / "references"

MODEL = "claude-opus-4-7"
MAX_TOKENS = 1024

SYSTEM_PROMPT = (
    "You are a senior software engineer. Summarize the following function in 2-4 sentences.\n"
    "Cover: what it does, its inputs/outputs, and any notable algorithmic or edge-case behavior.\n"
    "Be precise and technical. Output the summary as plain prose with no markdown wrappers, "
    "no headings, and no code fences."
)

# Opus 4.7 list pricing (USD per 1M tokens). See shared/models.md.
INPUT_PRICE_PER_M = 5.00
OUTPUT_PRICE_PER_M = 25.00
CACHE_WRITE_PRICE_PER_M = INPUT_PRICE_PER_M * 1.25
CACHE_READ_PRICE_PER_M = INPUT_PRICE_PER_M * 0.10

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
}


def discover_function_files(functions_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in functions_dir.iterdir()
        if path.is_file() and path.suffix in LANGUAGE_BY_EXTENSION
    )


def reference_path_for(function_path: Path, references_dir: Path) -> Path:
    return references_dir / f"{function_path.stem}.txt"


def build_user_message(function_path: Path) -> str:
    code = function_path.read_text(encoding="utf-8")
    language = LANGUAGE_BY_EXTENSION[function_path.suffix]
    return f"```{language}\n{code}\n```"


def summarize_with_backoff(
    client: anthropic.Anthropic,
    function_path: Path,
    max_retries: int = 6,
) -> anthropic.types.Message:
    """Call the Messages API with exponential backoff on retryable failures."""
    user_content = build_user_message(function_path)
    delay = 2.0
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_content}],
            )
        except anthropic.RateLimitError as e:
            last_error = e
        except anthropic.APIConnectionError as e:
            last_error = e
        except anthropic.APIStatusError as e:
            if e.status_code < 500:
                raise
            last_error = e

        sleep_for = delay + random.uniform(0, 1)
        print(
            f"  retry {attempt + 1}/{max_retries} after {sleep_for:.1f}s: {last_error}",
            file=sys.stderr,
        )
        time.sleep(sleep_for)
        delay = min(delay * 2, 60.0)

    assert last_error is not None
    raise last_error


def extract_summary(message: anthropic.types.Message) -> str:
    parts: list[str] = []
    for block in message.content:
        if block.type == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    cache_write_tokens: int,
    cache_read_tokens: int,
) -> float:
    return (
        input_tokens * INPUT_PRICE_PER_M / 1_000_000
        + output_tokens * OUTPUT_PRICE_PER_M / 1_000_000
        + cache_write_tokens * CACHE_WRITE_PRICE_PER_M / 1_000_000
        + cache_read_tokens * CACHE_READ_PRICE_PER_M / 1_000_000
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Opus reference summaries for benchmark functions."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the calls that would be made without contacting the API.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N files (after skip filtering). Useful for debugging.",
    )
    parser.add_argument(
        "--functions-dir",
        type=Path,
        default=DEFAULT_FUNCTIONS_DIR,
        help="Directory of source function files to summarize "
        "(default: data/functions).",
    )
    parser.add_argument(
        "--references-dir",
        type=Path,
        default=DEFAULT_REFERENCES_DIR,
        help="Directory to write reference summaries into "
        "(default: data/references).",
    )
    args = parser.parse_args()

    load_dotenv()

    functions_dir: Path = args.functions_dir
    references_dir: Path = args.references_dir

    if not functions_dir.is_dir():
        print(f"ERROR: {functions_dir} does not exist.", file=sys.stderr)
        return 1

    references_dir.mkdir(parents=True, exist_ok=True)

    function_files = discover_function_files(functions_dir)
    pending: list[Path] = []
    skipped = 0
    for fp in function_files:
        if reference_path_for(fp, references_dir).exists():
            skipped += 1
            continue
        pending.append(fp)

    if args.limit is not None:
        pending = pending[: args.limit]

    print(
        f"Found {len(function_files)} function files; "
        f"{skipped} already summarized; {len(pending)} pending."
    )

    if args.dry_run:
        print(f"\nDry run — would call {MODEL} on:")
        for fp in pending:
            ref_path = reference_path_for(fp, references_dir)
            try:
                ref_display = ref_path.relative_to(REPO_ROOT)
            except ValueError:
                ref_display = ref_path
            print(f"  {fp.name} -> {ref_display}")
        return 0

    if not pending:
        print("Nothing to do.")
        return 0

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in.",
            file=sys.stderr,
        )
        return 1

    client = anthropic.Anthropic(api_key=api_key)

    total_input = 0
    total_output = 0
    total_cache_write = 0
    total_cache_read = 0
    failures: list[tuple[Path, Exception]] = []

    for index, fp in enumerate(pending, start=1):
        print(f"[{index}/{len(pending)}] {fp.name}")
        try:
            message = summarize_with_backoff(client, fp)
        except Exception as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)
            failures.append((fp, exc))
            continue

        summary = extract_summary(message)
        if not summary:
            print("  WARNING: empty summary, skipping write", file=sys.stderr)
            failures.append((fp, RuntimeError("empty summary returned")))
            continue

        reference_path_for(fp, references_dir).write_text(summary + "\n", encoding="utf-8")

        usage = message.usage
        cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        total_input += usage.input_tokens
        total_output += usage.output_tokens
        total_cache_write += cache_write
        total_cache_read += cache_read

        print(
            f"  ok (in={usage.input_tokens}, out={usage.output_tokens}, "
            f"cache_w={cache_write}, cache_r={cache_read})"
        )

    cost = estimate_cost(total_input, total_output, total_cache_write, total_cache_read)
    print()
    print("=" * 60)
    print(f"Processed: {len(pending) - len(failures)}/{len(pending)}")
    print(f"Failures:  {len(failures)}")
    for fp, err in failures:
        print(f"  - {fp.name}: {err}")
    print(f"Tokens — input: {total_input:,}, output: {total_output:,}")
    print(f"         cache write: {total_cache_write:,}, cache read: {total_cache_read:,}")
    print(f"Estimated cost: ${cost:.4f}")
    print("=" * 60)

    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
