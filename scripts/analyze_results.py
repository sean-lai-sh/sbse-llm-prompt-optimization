#!/usr/bin/env python3
"""Analyze a finished experiment directory: Wilcoxon + Cliff's delta + table.

Usage:
    python scripts/analyze_results.py \
        --results-root results/experiment_<ts>/ \
        --output results/experiment_<ts>/statistical_summary.json

Loads every `<algo>_trial_*/` subdirectory, extracts the per-trial blended
plus per-metric breakdown of the winning generation, and runs the same
two-sided Wilcoxon rank-sum + Cliff's delta on each metric (blended,
ROUGE-L, raw cosine, calibrated cosine). Writes a JSON summary and prints
a stdout table.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.analysis import PER_TRIAL_METRICS, analyze_results_root


def _print_table(summary: dict) -> None:
    target = summary["target_algorithm"]
    baseline = summary["baseline_algorithm"]
    n_target = summary["n_trials"][target]
    n_baseline = summary["n_trials"][baseline]
    print(f"\nTrials: {target}={n_target}  {baseline}={n_baseline}")
    print(f"\n{'metric':<22} "
          f"{target+' mean (sd)':>22}  "
          f"{baseline+' mean (sd)':>22}  "
          f"{'p-value':>10}  "
          f"{'cliffs d':>10}  "
          f"{'effect':>12}")
    print("-" * 103)
    target_mean_key = f"{target}_mean"
    target_std_key = f"{target}_std"
    baseline_mean_key = f"{baseline}_mean"
    baseline_std_key = f"{baseline}_std"
    for metric in PER_TRIAL_METRICS:
        c = summary["comparisons"][metric]
        print(
            f"{metric:<22} "
            f"{c[target_mean_key]:>11.4f} ({c[target_std_key]:.4f})  "
            f"{c[baseline_mean_key]:>11.4f} ({c[baseline_std_key]:.4f})  "
            f"{c['p_value']:>10.4f}  "
            f"{c['cliffs_delta']:>+10.4f}  "
            f"{c['delta_label']:>12}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True,
                        help="experiment directory containing <algo>_trial_*/")
    parser.add_argument("--output", type=Path, required=True,
                        help="path to write statistical_summary.json")
    parser.add_argument("--target", default="ga",
                        help="target algorithm prefix (default: ga)")
    parser.add_argument("--baseline", default="rs",
                        help="baseline algorithm prefix (default: rs)")
    args = parser.parse_args()

    summary = analyze_results_root(
        args.results_root,
        target_algorithm=args.target,
        baseline_algorithm=args.baseline,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _print_table(summary)
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
