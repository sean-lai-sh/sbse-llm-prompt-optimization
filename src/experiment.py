"""Experiment orchestration for the GA-vs-RS comparison (issue #11).

`run_experiment` loops trials x algorithms, calling `run_ga` and `run_rs` with
distinct seeds and writing each run to its own subdirectory. The Wilcoxon /
Cliff's delta analysis (`scripts/analyze_results.py`) consumes those
subdirectories afterwards.

The orchestrator is split out from `scripts/run_experiment.py` so it can be
unit-tested with mocked algorithms (no real fitness, no real LLM).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Optional

from src.ga import run_ga
from src.prompt import PromptTemplate
from src.random_search import run_rs
from src.search_log import GenerationLog


# Trial dir convention: <algo>_trial_<NNN>_<UTC_timestamp>
_TRIAL_DIR_RE = re.compile(r"^(?P<algo>[A-Za-z][A-Za-z0-9]*)_trial_(?P<idx>\d+)_")


# Type alias: any callable matching `run_ga(config, *, seed=..., output_dir=..., ...)`
AlgorithmFn = Callable[..., tuple[PromptTemplate, list[GenerationLog]]]


_ALGORITHMS: dict[str, AlgorithmFn] = {
    "ga": run_ga,
    "rs": run_rs,
}


@dataclass(frozen=True)
class TrialResult:
    """One algorithm run (one trial). Mirrors what's persisted on disk."""

    algorithm: str
    trial_index: int
    seed: int
    output_dir: Path
    best_template: PromptTemplate
    best_blended: float
    resumed: bool = False


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _resolve_algorithms(
    algorithms: Iterable[str] | None,
    overrides: dict[str, AlgorithmFn] | None,
) -> dict[str, AlgorithmFn]:
    """Pick which algorithms to run, allowing test injection."""
    available = dict(_ALGORITHMS)
    if overrides:
        available.update(overrides)
    if algorithms is None:
        return available
    chosen = {}
    for name in algorithms:
        if name not in available:
            raise ValueError(
                f"unknown algorithm '{name}'; available: {sorted(available)}"
            )
        chosen[name] = available[name]
    return chosen


def _find_completed_trials(output_root: Path, algo: str) -> dict[int, Path]:
    """Discover trial dirs that finished successfully.

    A trial is "complete" iff both ``best.json`` and ``generations.jsonl``
    are present. ``best.json`` is written only at the end of ``run_ga`` /
    ``run_rs``, so its presence is a reliable end-of-run marker.
    """
    completed: dict[int, Path] = {}
    if not output_root.is_dir():
        return completed
    for child in sorted(output_root.iterdir()):
        if not child.is_dir():
            continue
        match = _TRIAL_DIR_RE.match(child.name)
        if not match or match.group("algo") != algo:
            continue
        if (child / "best.json").exists() and (child / "generations.jsonl").exists():
            completed[int(match.group("idx"))] = child
    return completed


def _load_completed_trial(run_dir: Path) -> tuple[PromptTemplate, list[GenerationLog]]:
    """Reconstruct an algorithm's return value from a finished trial dir."""
    best_template = PromptTemplate.from_dict(
        json.loads((run_dir / "best.json").read_text(encoding="utf-8"))
    )
    logs: list[GenerationLog] = []
    with (run_dir / "generations.jsonl").open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                logs.append(GenerationLog(**json.loads(line)))
    return best_template, logs


def run_experiment(
    config: dict,
    *,
    trials: int,
    algorithms: Optional[Iterable[str]] = None,
    output_root: Optional[Path] = None,
    progress: Optional[Callable[[TrialResult], None]] = None,
    algorithm_overrides: Optional[dict[str, AlgorithmFn]] = None,
    base_seed: int = 0,
    resume: bool = True,
    **algorithm_kwargs,
) -> list[TrialResult]:
    """Run `trials` independent runs of each algorithm with distinct seeds.

    Args:
        config: parsed config dict (passed straight to `run_ga` / `run_rs`).
        trials: how many independent runs per algorithm.
        algorithms: which algorithms to run; default both ``ga`` and ``rs``.
        output_root: where to drop trial subdirectories. Default
            ``results/experiment_<UTC_ts>/``.
        progress: optional callback invoked after each trial completes -- the
            CLI uses it to print a live progress table.
        algorithm_overrides: test hook -- inject mock callables in place of
            ``run_ga`` / ``run_rs``.
        base_seed: starting seed; trial ``i`` of each algorithm uses
            ``base_seed + i``. Same algorithm + same trial index -> same
            seed across algorithms by design (each trial is matched).
        resume: when True (default) and ``output_root`` already contains
            completed trial directories (each with ``best.json`` AND
            ``generations.jsonl``), those trials are loaded from disk and
            their TrialResults are returned alongside any newly-run trials.
            Pass ``False`` to force re-running every trial regardless.
        **algorithm_kwargs: forwarded to every algorithm call (e.g.
            ``score_fn``, ``generate_summary``, ``functions``, ``references``).

    Returns:
        Flat list of ``TrialResult`` entries, one per (algorithm, trial),
        in algorithm-then-trial-index order.
    """
    if trials < 1:
        raise ValueError(f"trials must be >= 1, got {trials}")

    chosen = _resolve_algorithms(algorithms, algorithm_overrides)
    if output_root is None:
        output_root = Path("results") / f"experiment_{_utc_timestamp()}"
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    results: list[TrialResult] = []
    for algo_name, algo_fn in chosen.items():
        prior = _find_completed_trials(output_root, algo_name) if resume else {}
        for i in range(trials):
            seed = base_seed + i
            if i in prior:
                # Resume: rebuild the TrialResult from the on-disk trial dir.
                run_dir = prior[i]
                best_template, logs = _load_completed_trial(run_dir)
            else:
                ts = _utc_timestamp()
                run_dir = output_root / f"{algo_name}_trial_{i:03d}_{ts}"
                best_template, logs = algo_fn(
                    config,
                    seed=seed,
                    output_dir=run_dir,
                    **algorithm_kwargs,
                )
            best_blended = max(
                (log.best_blended for log in logs), default=float("-inf")
            )

            result = TrialResult(
                algorithm=algo_name,
                trial_index=i,
                seed=seed,
                output_dir=run_dir,
                best_template=best_template,
                best_blended=best_blended,
                resumed=(i in prior),
            )
            results.append(result)
            if progress is not None:
                progress(result)

    return results
