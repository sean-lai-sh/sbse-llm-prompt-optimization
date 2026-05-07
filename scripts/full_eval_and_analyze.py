#!/usr/bin/env python3
"""Re-score every trial's best.json on the FULL 500-function benchmark and
run Wilcoxon + Cliff's delta on the result.

Why: the in-loop fitness uses ``eval_subset=10``, so each trial's reported
``best_blended`` is a noisy 10-function-subsample estimate (different
trials may even see different 10 functions due to seed differences). For
the final paper-grade comparison we want each trial's "winning prompt"
re-evaluated on the *same* full benchmark so the per-trial numbers are
comparable and the noise floor drops.

This script:
  1. Walks every ``<algo>_trial_*/best.json`` under ``--results-root``
  2. Calls ``src.eval.evaluate_prompt`` on the full benchmark for each
  3. Builds per-algorithm distributions of full-benchmark blended/ROUGE-L/
     cosine scores
  4. Runs the same Wilcoxon + Cliff's delta comparison as
     ``analyze_results.py`` and writes ``full_benchmark_summary.json``

Usage:
    python scripts/full_eval_and_analyze.py \\
        --results-root results/experiment_<ts>/ \\
        --output       results/experiment_<ts>/full_benchmark_summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.analysis import discover_trial_dirs
from src.eval import evaluate_prompt
from src.fitness import FitnessConfig
from src.prompt import PromptTemplate
from src.stats import compare_distributions

DEFAULT_FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"
DEFAULT_REFERENCES_DIR = REPO_ROOT / "data" / "references"


def _full_benchmark() -> tuple[list[Path], list[Path]]:
    """Pair every .py/.js/.ts function with its same-stem reference."""
    SUPPORTED_EXT = {".py", ".js", ".ts"}
    fns = sorted(
        p for p in DEFAULT_FUNCTIONS_DIR.iterdir()
        if p.is_file() and p.suffix in SUPPORTED_EXT
    )
    refs_by_stem = {p.stem: p for p in DEFAULT_REFERENCES_DIR.iterdir() if p.is_file()}
    missing = [p.stem for p in fns if p.stem not in refs_by_stem]
    if missing:
        raise ValueError(f"functions missing references: {missing[:5]}...")
    refs = [refs_by_stem[fn.stem] for fn in fns]
    return fns, refs


def _score_trial_on_full_bench(
    trial_dir: Path,
    functions: list[Path],
    references: list[Path],
    cfg: FitnessConfig,
) -> dict:
    """Re-score a trial's best template on the full benchmark.

    Returns a dict with per-metric aggregates *plus* the calibrated cosine
    and the blended fitness, so it lines up with what generations.jsonl
    records.
    """
    template = PromptTemplate.from_dict(
        json.loads((trial_dir / "best.json").read_text(encoding="utf-8"))
    )
    eval_result = evaluate_prompt(template, functions, references)
    rouge_l = eval_result["aggregate"]["rouge_l_mean"]
    cosine_raw = eval_result["aggregate"]["cosine_mean"]
    # Apply the same calibration the GA uses.
    from src.eval import calibrate_cosine
    cosine_calibrated = calibrate_cosine(cosine_raw, cfg.cosine_baseline)
    blended = (
        cfg.alpha * rouge_l
        + (1.0 - cfg.alpha) * cosine_calibrated
    )
    return {
        "trial_dir": str(trial_dir.name),
        "blended": float(blended),
        "rouge_l": float(rouge_l),
        "cosine_raw": float(cosine_raw),
        "cosine_calibrated": float(cosine_calibrated),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True,
                        help="experiment dir containing <algo>_trial_*/")
    parser.add_argument("--output", type=Path, required=True,
                        help="path to write full_benchmark_summary.json")
    parser.add_argument("--target", default="ga",
                        help="target algorithm prefix (default: ga)")
    parser.add_argument("--baseline", default="rs",
                        help="baseline algorithm prefix (default: rs)")
    args = parser.parse_args()

    grouped = discover_trial_dirs(args.results_root)
    if args.target not in grouped or args.baseline not in grouped:
        print(
            f"ERROR: need both '{args.target}' and '{args.baseline}' trial "
            f"dirs in {args.results_root}; found: {sorted(grouped)}",
            file=sys.stderr,
        )
        return 1

    cfg = FitnessConfig.from_yaml()
    functions, references = _full_benchmark()
    print(
        f"Re-scoring {len(grouped[args.target])} {args.target} trials "
        f"and {len(grouped[args.baseline])} {args.baseline} trials on "
        f"the full {len(functions)}-function benchmark...",
        flush=True,
    )

    per_trial: dict[str, list[dict]] = {args.target: [], args.baseline: []}
    columns: dict[str, dict[str, list[float]]] = {
        args.target: {"blended": [], "rouge_l": [], "cosine_raw": [], "cosine_calibrated": []},
        args.baseline: {"blended": [], "rouge_l": [], "cosine_raw": [], "cosine_calibrated": []},
    }
    for algo in (args.target, args.baseline):
        for i, trial_dir in enumerate(grouped[algo], start=1):
            scores = _score_trial_on_full_bench(trial_dir, functions, references, cfg)
            per_trial[algo].append(scores)
            for k in columns[algo]:
                columns[algo][k].append(scores[k])
            print(
                f"  [{algo}] {i}/{len(grouped[algo])} {trial_dir.name}: "
                f"blended={scores['blended']:.4f} "
                f"rougeL={scores['rouge_l']:.4f} "
                f"cosCal={scores['cosine_calibrated']:.4f}",
                flush=True,
            )

    comparisons = {}
    for metric in ("blended", "rouge_l", "cosine_raw", "cosine_calibrated"):
        c = compare_distributions(
            columns[args.target][metric], columns[args.baseline][metric], metric=metric,
        ).to_dict()
        # Match analyze_results.py's algorithm-named schema.
        comparisons[metric] = {
            "metric": c["metric"],
            f"n_{args.target}": c["n_a"],
            f"n_{args.baseline}": c["n_b"],
            f"{args.target}_mean": c["mean_a"],
            f"{args.baseline}_mean": c["mean_b"],
            f"{args.target}_std": c["std_a"],
            f"{args.baseline}_std": c["std_b"],
            "statistic": c["statistic"],
            "p_value": c["p_value"],
            "cliffs_delta": c["cliffs_delta"],
            "delta_label": c["delta_label"],
        }

    summary = {
        "evaluation_kind": "full_benchmark",
        "target_algorithm": args.target,
        "baseline_algorithm": args.baseline,
        "n_trials": {
            args.target: len(grouped[args.target]),
            args.baseline: len(grouped[args.baseline]),
        },
        "n_benchmark_pairs": len(functions),
        "per_trial_full_eval": per_trial,
        "comparisons": comparisons,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    target = args.target
    baseline = args.baseline
    print(
        f"\n{'metric':<22} "
        f"{target+' mean (sd)':>22}  "
        f"{baseline+' mean (sd)':>22}  "
        f"{'p-value':>10}  "
        f"{'cliffs d':>10}  "
        f"{'effect':>12}"
    )
    print("-" * 103)
    for metric in ("blended", "rouge_l", "cosine_raw", "cosine_calibrated"):
        c = comparisons[metric]
        print(
            f"{metric:<22} "
            f"{c[f'{target}_mean']:>11.4f} ({c[f'{target}_std']:.4f})  "
            f"{c[f'{baseline}_mean']:>11.4f} ({c[f'{baseline}_std']:.4f})  "
            f"{c['p_value']:>10.4f}  "
            f"{c['cliffs_delta']:>+10.4f}  "
            f"{c['delta_label']:>12}"
        )
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
