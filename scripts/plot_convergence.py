#!/usr/bin/env python3
"""Plot per-generation convergence (mean +/- std across trials), GA vs RS.

Usage:
    python scripts/plot_convergence.py \
        --results-root results/experiment_<ts>/ \
        --output results/experiment_<ts>/convergence.png

Three panels: blended fitness, ROUGE-L (raw), and calibrated cosine. Each
panel shows the mean across trials with a +/- 1 std shaded band, GA in one
color and RS in the other. The last generation's mean is annotated for the
caption you'd write into the paper.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no interactive backend; we only save to PNG
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.analysis import discover_trial_dirs, load_generation_logs


# (panel title, GenerationLog field name)
PANELS = (
    ("Blended fitness", "best_blended"),
    ("ROUGE-L (best individual)", "best_rouge_l"),
    ("Cosine calibrated (best individual)", "best_cosine_calibrated"),
)

ALGO_COLORS = {"ga": "tab:blue", "rs": "tab:orange"}


def _stack_metric(trial_dirs: list[Path], field: str) -> np.ndarray:
    """Return an ``(n_trials, n_generations)`` array of cumulative best per
    trial, truncated to the shortest run.

    Cumulative max along the generation axis matters for Random Search: its
    per-checkpoint ``best_*`` values describe the best in *that bucket*, not
    the best seen so far. Without `np.maximum.accumulate`, an RS trial that
    finds its winner mid-run would visually regress in later checkpoints
    and the figure would understate the baseline. GA already preserves the
    best via elitism, so the cumulative max is a no-op for it -- safe to
    apply uniformly.
    """
    series = []
    for d in trial_dirs:
        logs = load_generation_logs(d)
        series.append([float(getattr(log, field)) for log in logs])
    if not series:
        return np.empty((0, 0))
    min_len = min(len(s) for s in series)
    raw = np.array([s[:min_len] for s in series], dtype=float)
    return np.maximum.accumulate(raw, axis=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", default="GA vs Random Search convergence",
                        help="figure suptitle")
    args = parser.parse_args()

    grouped = discover_trial_dirs(args.results_root)
    if "ga" not in grouped or "rs" not in grouped:
        print(
            f"ERROR: need both 'ga' and 'rs' trial dirs in {args.results_root}; "
            f"found: {sorted(grouped)}",
            file=sys.stderr,
        )
        return 1

    fig, axes = plt.subplots(1, len(PANELS), figsize=(15, 4.5), sharex=True)
    if len(PANELS) == 1:
        axes = [axes]

    for ax, (title, field) in zip(axes, PANELS):
        for algo in ("ga", "rs"):
            arr = _stack_metric(grouped[algo], field)
            if arr.size == 0:
                continue
            mean = arr.mean(axis=0)
            std = arr.std(axis=0)
            x = np.arange(1, len(mean) + 1)
            ax.plot(x, mean, color=ALGO_COLORS[algo], label=algo.upper(), linewidth=2)
            ax.fill_between(x, mean - std, mean + std,
                            color=ALGO_COLORS[algo], alpha=0.18)
            ax.annotate(
                f"{mean[-1]:.3f}",
                xy=(x[-1], mean[-1]),
                xytext=(4, 0),
                textcoords="offset points",
                color=ALGO_COLORS[algo],
                fontsize=9,
                va="center",
            )
        ax.set_title(title)
        ax.set_xlabel("Generation")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=9)

    axes[0].set_ylabel("Best individual score (mean ± std)")
    fig.suptitle(args.title, fontsize=12)
    fig.tight_layout()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=150)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
