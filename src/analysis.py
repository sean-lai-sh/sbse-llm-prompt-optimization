"""Load experiment trial directories and produce the GA-vs-RS comparison.

Sits between `src.experiment` (which produces the per-trial directories) and
`scripts/analyze_results.py` (the CLI). Pure-ish: reads files, returns dicts;
no plotting and no stdout chatter.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

# Trial dir convention from src.experiment: <algo>_trial_<NNN>_<timestamp>
_TRIAL_DIR_RE = re.compile(r"^(?P<algo>[A-Za-z][A-Za-z0-9]*)_trial_\d+_")

from src.search_log import GenerationLog
from src.stats import compare_distributions


# Per-trial values we extract for the statistical comparison.
# `cosine_calibrated` is what enters the blended fitness; `cosine_raw` is
# kept around for transparency / reviewer inspection.
PER_TRIAL_METRICS: tuple[str, ...] = (
    "blended",
    "rouge_l",
    "cosine_raw",
    "cosine_calibrated",
)


def load_generation_logs(run_dir: Path) -> list[GenerationLog]:
    """Read `<run_dir>/generations.jsonl` into a list of `GenerationLog`."""
    path = Path(run_dir) / "generations.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"generations.jsonl missing in {run_dir}")
    logs: list[GenerationLog] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            logs.append(GenerationLog(**data))
    if not logs:
        raise ValueError(f"generations.jsonl in {run_dir} has no rows")
    return logs


def trial_best(logs: Iterable[GenerationLog]) -> dict[str, float]:
    """Pick the row with the highest `best_blended` and return its metrics.

    Returning the per-metric values *of the winning generation* (not, e.g.,
    the max ROUGE-L ever seen across any candidate) keeps the ablation
    honest: we are characterizing the prompt that actually won, not
    fishing for the best-looking number per metric.
    """
    logs = list(logs)
    if not logs:
        raise ValueError("no logs to summarize")
    winner = max(logs, key=lambda l: l.best_blended)
    return {
        "blended": float(winner.best_blended),
        "rouge_l": float(winner.best_rouge_l),
        "cosine_raw": float(winner.best_cosine_raw),
        "cosine_calibrated": float(winner.best_cosine_calibrated),
    }


def discover_trial_dirs(results_root: Path) -> dict[str, list[Path]]:
    """Group trial subdirectories by the algorithm prefix in their name.

    Convention from `src.experiment`: ``<algo>_trial_<n>_<ts>/``.
    """
    root = Path(results_root)
    if not root.is_dir():
        raise FileNotFoundError(f"results root not found: {results_root}")
    grouped: dict[str, list[Path]] = {}
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        match = _TRIAL_DIR_RE.match(child.name)
        if not match:
            continue
        grouped.setdefault(match.group("algo"), []).append(child)
    return grouped


def summarize_trials(
    trial_dirs: Iterable[Path],
) -> dict[str, list[float]]:
    """Read each trial dir and return per-metric value lists for the algo."""
    columns: dict[str, list[float]] = {m: [] for m in PER_TRIAL_METRICS}
    for d in trial_dirs:
        logs = load_generation_logs(d)
        best = trial_best(logs)
        for metric in PER_TRIAL_METRICS:
            columns[metric].append(best[metric])
    return columns


def analyze_results_root(
    results_root: Path,
    *,
    target_algorithm: str = "ga",
    baseline_algorithm: str = "rs",
) -> dict:
    """End-to-end analysis: discover trials, summarize, run all comparisons."""
    grouped = discover_trial_dirs(results_root)
    if target_algorithm not in grouped:
        raise ValueError(
            f"no trial dirs found for algorithm '{target_algorithm}' under "
            f"{results_root}; found: {sorted(grouped)}"
        )
    if baseline_algorithm not in grouped:
        raise ValueError(
            f"no trial dirs found for algorithm '{baseline_algorithm}' under "
            f"{results_root}; found: {sorted(grouped)}"
        )

    target_cols = summarize_trials(grouped[target_algorithm])
    baseline_cols = summarize_trials(grouped[baseline_algorithm])

    per_metric = {}
    for metric in PER_TRIAL_METRICS:
        comparison = compare_distributions(
            target_cols[metric],
            baseline_cols[metric],
            metric=metric,
        )
        per_metric[metric] = comparison.to_dict()

    return {
        "target_algorithm": target_algorithm,
        "baseline_algorithm": baseline_algorithm,
        "n_trials": {
            target_algorithm: len(grouped[target_algorithm]),
            baseline_algorithm: len(grouped[baseline_algorithm]),
        },
        "per_trial_values": {
            target_algorithm: target_cols,
            baseline_algorithm: baseline_cols,
        },
        "comparisons": per_metric,
    }
