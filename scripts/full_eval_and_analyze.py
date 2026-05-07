#!/usr/bin/env python3
"""Re-score every trial's best.json on the held-out test benchmark and run
Wilcoxon + Cliff's delta on the result.

Why a held-out test set: the GA's in-loop fitness uses ``eval_subset=10``
sampled from the *training* set ``data/functions/``, so even a "full
benchmark" eval against the same 500 functions would still be a train-set
score (just with less subsampling noise). To make a generalization claim
we evaluate on ``data/test/`` -- 50 functions and Opus-generated
references the GA never saw during search.

This script:
  1. Walks every ``<algo>_trial_*/best.json`` under ``--results-root``
  2. Calls ``src.eval.evaluate_prompt`` on the held-out test set for each
  3. Builds per-algorithm distributions of test-set blended/ROUGE-L/
     cosine scores
  4. Runs the same Wilcoxon + Cliff's delta comparison as
     ``analyze_results.py`` and writes ``test_benchmark_summary.json``

Usage:
    python scripts/full_eval_and_analyze.py \\
        --results-root results/experiment_<ts>/ \\
        --output       results/experiment_<ts>/test_benchmark_summary.json
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

DEFAULT_FUNCTIONS_DIR = REPO_ROOT / "data" / "test" / "functions"
DEFAULT_REFERENCES_DIR = REPO_ROOT / "data" / "test" / "references"


def _benchmark_pairs(
    functions_dir: Path, references_dir: Path
) -> tuple[list[Path], list[Path]]:
    """Pair every .py/.js/.ts function with its same-stem reference.

    Same strict-pairing contract as the in-loop benchmark: any unpaired
    file raises so a missing data file can't silently shrink the test set.
    """
    SUPPORTED_EXT = {".py", ".js", ".ts"}
    if not functions_dir.is_dir():
        raise FileNotFoundError(f"functions dir not found: {functions_dir}")
    if not references_dir.is_dir():
        raise FileNotFoundError(f"references dir not found: {references_dir}")
    fns = sorted(
        p for p in functions_dir.iterdir()
        if p.is_file() and p.suffix in SUPPORTED_EXT
    )
    refs_by_stem = {p.stem: p for p in references_dir.iterdir() if p.is_file()}
    missing = [p.stem for p in fns if p.stem not in refs_by_stem]
    if missing:
        raise ValueError(
            f"functions missing references in {references_dir}: {missing[:5]}..."
        )
    if not fns:
        raise ValueError(f"no benchmark pairs found under {functions_dir}")
    refs = [refs_by_stem[fn.stem] for fn in fns]
    return fns, refs


def _score_trial_on_test_bench(
    trial_dir: Path,
    functions: list[Path],
    references: list[Path],
    cfg: FitnessConfig,
    *,
    generate_summary=None,
    call_progress=None,
    workers: int = 16,
) -> dict:
    """Re-score a trial's best template on the held-out test benchmark.

    Returns a dict with per-metric aggregates *plus* the calibrated cosine
    and the blended fitness, so it lines up with what generations.jsonl
    records.

    When ``call_progress`` is provided, it's invoked once per
    generate_summary call so the caller can drive a tqdm bar across the
    whole eval pass.
    """
    template = PromptTemplate.from_dict(
        json.loads((trial_dir / "best.json").read_text(encoding="utf-8"))
    )

    # If the caller wants live progress, wrap generate_summary so each call
    # ticks the bar after returning.
    eval_kwargs = {}
    if call_progress is not None:
        from src.eval import _default_generate_summary  # noqa: PLC0415
        inner = generate_summary if generate_summary is not None else _default_generate_summary()

        def _counted(*args, **kwargs):
            try:
                return inner(*args, **kwargs)
            finally:
                call_progress()

        eval_kwargs["generate_summary"] = _counted
    elif generate_summary is not None:
        eval_kwargs["generate_summary"] = generate_summary

    eval_result = evaluate_prompt(
        template, functions, references, workers=workers, **eval_kwargs
    )
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
                        help="path to write test_benchmark_summary.json")
    parser.add_argument("--target", default="ga",
                        help="target algorithm prefix (default: ga)")
    parser.add_argument("--baseline", default="rs",
                        help="baseline algorithm prefix (default: rs)")
    parser.add_argument("--functions-dir", type=Path, default=None,
                        help="directory of function source files. "
                             "Default: data/test/functions/ (held-out test set). "
                             "Overrides --use-training-set if both are given.")
    parser.add_argument("--references-dir", type=Path, default=None,
                        help="directory of reference summaries. "
                             "Default: data/test/references/ (held-out test set). "
                             "Overrides --use-training-set if both are given.")
    parser.add_argument("--use-training-set", action="store_true",
                        help="DEPRECATED / TRAIN-SET-LEAKY: re-score on "
                             "data/functions/ + data/references/ -- the same "
                             "set the GA's eval_subset sampled from during "
                             "search. Use only for ablation; the headline "
                             "GA-vs-RS claim should come from the default "
                             "held-out test set under data/test/. Prints a "
                             "loud warning and writes its summary with "
                             "evaluation_kind = 'training_set_resample'.")
    parser.add_argument("--no-progress", action="store_true",
                        help="suppress the tqdm progress bar")
    parser.add_argument("--workers", type=int, default=16,
                        help="parallel generate_summary calls per template "
                             "(default: 16). Each template's 50 calls are "
                             "fanned out via ThreadPoolExecutor before the "
                             "single cosine batch + ROUGE-L pass.")
    args = parser.parse_args()

    grouped = discover_trial_dirs(args.results_root)
    if args.target not in grouped or args.baseline not in grouped:
        print(
            f"ERROR: need both '{args.target}' and '{args.baseline}' trial "
            f"dirs in {args.results_root}; found: {sorted(grouped)}",
            file=sys.stderr,
        )
        return 1

    # Resolve functions_dir / references_dir with this precedence:
    #   1. explicit --functions-dir / --references-dir flags
    #   2. --use-training-set => data/functions + data/references (with warning)
    #   3. default: held-out test set under data/test/
    if args.use_training_set:
        if args.functions_dir is None:
            args.functions_dir = REPO_ROOT / "data" / "functions"
        if args.references_dir is None:
            args.references_dir = REPO_ROOT / "data" / "references"
        evaluation_kind = "training_set_resample"
        print(
            "\n*** WARNING: --use-training-set is TRAIN-SET-LEAKY. ***\n"
            "    Each trial's GA search drew its eval_subset from\n"
            "    data/functions/, so re-scoring on the same directory\n"
            "    is a training-set re-evaluation (less subsampling noise,\n"
            "    same overfitting risk). For the headline generalization\n"
            "    claim, run without --use-training-set so it uses the\n"
            "    held-out test set under data/test/.\n",
            flush=True,
        )
    else:
        if args.functions_dir is None:
            args.functions_dir = DEFAULT_FUNCTIONS_DIR
        if args.references_dir is None:
            args.references_dir = DEFAULT_REFERENCES_DIR
        evaluation_kind = "held_out_test_set"

    cfg = FitnessConfig.from_yaml()
    functions, references = _benchmark_pairs(args.functions_dir, args.references_dir)
    n_trials = len(grouped[args.target]) + len(grouped[args.baseline])
    expected_calls = n_trials * len(functions)
    print(
        f"Re-scoring {len(grouped[args.target])} {args.target} trials "
        f"and {len(grouped[args.baseline])} {args.baseline} trials on "
        f"the {len(functions)}-function held-out test set "
        f"({expected_calls} total LLM calls)...",
        flush=True,
    )

    # Single tqdm bar across the whole re-eval -- one tick per generate_summary
    # call so the user sees live progress through all 20 templates x 50
    # functions = 1000 calls.
    if args.no_progress:
        bar_ctx = None
        tick = None
    else:
        from tqdm import tqdm  # noqa: PLC0415
        bar_ctx = tqdm(
            total=expected_calls,
            desc="held-out eval",
            unit="call",
            dynamic_ncols=True,
            mininterval=0.25,
            smoothing=0.1,
        )
        tick = bar_ctx.update

    per_trial: dict[str, list[dict]] = {args.target: [], args.baseline: []}
    columns: dict[str, dict[str, list[float]]] = {
        args.target: {"blended": [], "rouge_l": [], "cosine_raw": [], "cosine_calibrated": []},
        args.baseline: {"blended": [], "rouge_l": [], "cosine_raw": [], "cosine_calibrated": []},
    }
    for algo in (args.target, args.baseline):
        for i, trial_dir in enumerate(grouped[algo], start=1):
            scores = _score_trial_on_test_bench(
                trial_dir, functions, references, cfg,
                call_progress=(lambda: tick(1)) if tick is not None else None,
                workers=args.workers,
            )
            per_trial[algo].append(scores)
            for k in columns[algo]:
                columns[algo][k].append(scores[k])
            line = (
                f"  [{algo}] {i}/{len(grouped[algo])} {trial_dir.name}: "
                f"blended={scores['blended']:.4f} "
                f"rougeL={scores['rouge_l']:.4f} "
                f"cosCal={scores['cosine_calibrated']:.4f}"
            )
            # Use tqdm.write so the bar isn't fragmented by per-trial prints.
            if bar_ctx is not None:
                bar_ctx.write(line)
            else:
                print(line, flush=True)

    if bar_ctx is not None:
        bar_ctx.close()

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
        "evaluation_kind": evaluation_kind,
        "target_algorithm": args.target,
        "baseline_algorithm": args.baseline,
        "functions_dir": str(args.functions_dir),
        "references_dir": str(args.references_dir),
        "n_trials": {
            args.target: len(grouped[args.target]),
            args.baseline: len(grouped[args.baseline]),
        },
        "n_benchmark_pairs": len(functions),
        "per_trial_test_eval": per_trial,
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
