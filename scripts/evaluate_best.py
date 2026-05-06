#!/usr/bin/env python3
"""Evaluate the best PromptTemplate from a results directory on the full benchmark.

Usage:
    python scripts/evaluate_best.py \\
        --results-dir results/<run>/ \\
        --output results/<run>/eval_scores.json

Loads the best PromptTemplate JSON found in --results-dir (any file named
``best_*.json`` or ``best.json``), runs `evaluate_prompt` over the full
500-file benchmark in `data/functions/` + `data/references/`, and writes the
per-file + aggregate breakdown to --output. Prints a short summary table.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DEFAULT_FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"
DEFAULT_REFERENCES_DIR = REPO_ROOT / "data" / "references"


def _find_template_files(results_dir: Path) -> list[Path]:
    """Locate candidate best-template JSON files in a results directory."""
    if not results_dir.exists():
        raise FileNotFoundError(f"results dir not found: {results_dir}")
    candidates: list[Path] = []
    for pattern in ("best_*.json", "best.json"):
        candidates.extend(sorted(results_dir.glob(pattern)))
    return candidates


def _pair_benchmark(
    functions_dir: Path, references_dir: Path
) -> tuple[list[Path], list[Path]]:
    """Pair function files to reference files by stem."""
    functions = sorted(p for p in functions_dir.iterdir() if p.is_file())
    refs_by_stem = {p.stem: p for p in references_dir.iterdir() if p.is_file()}

    paired_fn: list[Path] = []
    paired_ref: list[Path] = []
    for fn in functions:
        ref = refs_by_stem.get(fn.stem)
        if ref is None:
            continue
        paired_fn.append(fn)
        paired_ref.append(ref)
    return paired_fn, paired_ref


def _print_summary(label: str, agg: dict) -> None:
    print(
        f"  {label:<20} "
        f"rouge_l={agg['rouge_l_mean']:.4f}±{agg['rouge_l_std']:.4f}  "
        f"cosine={agg['cosine_mean']:.4f}±{agg['cosine_std']:.4f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the best PromptTemplate(s) in a results directory."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
        help="Directory containing one or more best_*.json template files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to write the combined eval_scores.json.",
    )
    parser.add_argument(
        "--functions-dir",
        type=Path,
        default=DEFAULT_FUNCTIONS_DIR,
        help="Directory of benchmark function files (default: data/functions/).",
    )
    parser.add_argument(
        "--references-dir",
        type=Path,
        default=DEFAULT_REFERENCES_DIR,
        help="Directory of reference summary files (default: data/references/).",
    )
    args = parser.parse_args()

    # Imported here so --help works without sentence-transformers installed.
    from src.eval import evaluate_prompt  # noqa: PLC0415
    from src.prompt import PromptTemplate  # noqa: PLC0415

    template_files = _find_template_files(args.results_dir)
    if not template_files:
        print(
            f"ERROR: no best_*.json or best.json found in {args.results_dir}",
            file=sys.stderr,
        )
        return 1

    functions, references = _pair_benchmark(args.functions_dir, args.references_dir)
    if not functions:
        print(
            f"ERROR: no paired (function, reference) files found "
            f"in {args.functions_dir} / {args.references_dir}",
            file=sys.stderr,
        )
        return 1

    print(f"Evaluating {len(template_files)} template(s) on {len(functions)} pairs...")
    print()

    combined: dict[str, dict] = {}
    for idx, tpl_path in enumerate(template_files, start=1):
        label = tpl_path.stem
        print(f"[{idx}/{len(template_files)}] {label}")
        data = json.loads(tpl_path.read_text(encoding="utf-8"))
        template = PromptTemplate.from_dict(data)
        result = evaluate_prompt(template, functions, references)
        combined[label] = result
        _print_summary(label, result["aggregate"])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print()
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
