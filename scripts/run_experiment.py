#!/usr/bin/env python3
"""Run the GA-vs-RS experiment: N trials of each algorithm, then analyze.

Usage:
    python scripts/run_experiment.py --trials 10 --algorithm both \
        --config config.yaml --output-root results/

After all trials complete the script invokes scripts/analyze_results.py
automatically so the run finishes with a populated `statistical_summary.json`
in the same `results/experiment_<ts>/` directory.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.experiment import TrialResult, run_experiment


def _load_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _make_progress(start: float):
    """Return a callback that prints a one-line update per completed trial."""
    last = {"count": 0}

    def _cb(result: TrialResult) -> None:
        last["count"] += 1
        elapsed = time.perf_counter() - start
        marker = "[resumed]" if result.resumed else "         "
        print(
            f"[{last['count']:3d}] {marker} {result.algorithm:>2} trial {result.trial_index:02d} "
            f"seed={result.seed:<4d} best_blended={result.best_blended:.4f}  "
            f"elapsed={elapsed:6.1f}s -> {result.output_dir.name}",
            flush=True,
        )

    return _cb


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=10,
                        help="independent runs per algorithm (default: 10)")
    parser.add_argument("--algorithm", choices=["ga", "rs", "both"], default="both",
                        help="which algorithms to run (default: both)")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "config.yaml",
                        help="path to config.yaml")
    parser.add_argument("--output-root", type=Path, default=None,
                        help="directory to drop trial subdirs into; "
                             "default results/experiment_<UTC_ts>/")
    parser.add_argument("--base-seed", type=int, default=0,
                        help="trial i uses seed = base_seed + i (default 0)")
    parser.add_argument("--skip-analysis", action="store_true",
                        help="don't auto-run scripts/analyze_results.py at the end")
    parser.add_argument("--no-resume", action="store_true",
                        help="re-run every trial even if --output-root already "
                             "contains completed trial directories. Default is "
                             "to load completed trials from disk and only run "
                             "the missing ones.")
    args = parser.parse_args()

    if args.algorithm == "both":
        algos = ["ga", "rs"]
    else:
        algos = [args.algorithm]

    config = _load_config(args.config)

    output_root = args.output_root
    if output_root is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = REPO_ROOT / "results" / f"experiment_{ts}"

    resume = not args.no_resume
    print(
        f"Running {args.trials} trial(s) of {algos} -> {output_root}\n"
        f"Config: {args.config}  base_seed={args.base_seed}  resume={resume}",
        flush=True,
    )

    start = time.perf_counter()
    results = run_experiment(
        config,
        trials=args.trials,
        algorithms=algos,
        output_root=output_root,
        base_seed=args.base_seed,
        progress=_make_progress(start),
        resume=resume,
    )
    total = time.perf_counter() - start

    # Write a manifest so the analysis script (and anyone reading the dir) has
    # provenance.
    manifest = {
        "trials": args.trials,
        "algorithms": algos,
        "base_seed": args.base_seed,
        "wall_seconds": total,
        "trial_results": [
            {
                "algorithm": r.algorithm,
                "trial_index": r.trial_index,
                "seed": r.seed,
                "output_dir": str(r.output_dir.relative_to(output_root)),
                "best_blended": r.best_blended,
            }
            for r in results
        ],
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nDone. {len(results)} trials in {total:.1f}s. Manifest: {output_root}/manifest.json",
          flush=True)

    if args.skip_analysis or len(algos) < 2:
        return 0

    print("\n--- Running analysis ---", flush=True)
    return subprocess.call(
        [
            sys.executable, str(REPO_ROOT / "scripts" / "analyze_results.py"),
            "--results-root", str(output_root),
            "--output", str(output_root / "statistical_summary.json"),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
