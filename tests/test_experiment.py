"""Tests for src/experiment.py.

The orchestrator is exercised with mock algorithm callables so we don't pay
fitness cost or hit the LLM. We just verify trial counts, seed sequencing,
output-dir layout, and that the progress callback fires.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.experiment import TrialResult, run_experiment
from src.prompt import PromptTemplate
from src.search_log import GenerationLog


def _mk_template(role: str = "r") -> PromptTemplate:
    return PromptTemplate(role=role, task="t", guard="g", format="f")


def _mk_logs(best_blended: float, n: int = 3) -> list[GenerationLog]:
    return [
        GenerationLog(
            generation=i,
            best_blended=best_blended,
            mean_blended=best_blended * 0.9,
            worst_blended=best_blended * 0.8,
            best_rouge_l=best_blended * 0.7,
            best_cosine_raw=best_blended * 0.8,
            best_cosine_calibrated=best_blended * 0.6,
            best_template=_mk_template().to_dict(),
        )
        for i in range(n)
    ]


def _make_mock_algo(score: float, captured: list[dict]):
    """Return an algorithm fn that records its kwargs and writes nothing."""
    def _fn(config, *, seed, output_dir, **kwargs):  # noqa: ARG001
        captured.append({"seed": seed, "output_dir": output_dir, **kwargs})
        # Mimic the real algorithms: create the dir even if no files written.
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return _mk_template(role=f"score-{score}"), _mk_logs(score)
    return _fn


# ---------------------------------------------------------------------------
# Core behavior
# ---------------------------------------------------------------------------


def test_run_experiment_runs_each_algorithm_n_times(tmp_path: Path) -> None:
    ga_calls: list[dict] = []
    rs_calls: list[dict] = []

    results = run_experiment(
        {"ga": {"population_size": 2, "generations": 2}},
        trials=3,
        output_root=tmp_path,
        algorithm_overrides={
            "ga": _make_mock_algo(0.8, ga_calls),
            "rs": _make_mock_algo(0.5, rs_calls),
        },
    )

    assert len(results) == 6  # 3 trials × 2 algos
    assert len(ga_calls) == 3
    assert len(rs_calls) == 3


def test_run_experiment_seed_increments_per_trial(tmp_path: Path) -> None:
    seen: list[dict] = []
    run_experiment(
        {},
        trials=3,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.7, seen)},
        base_seed=42,
    )
    assert [c["seed"] for c in seen] == [42, 43, 44]


def test_run_experiment_matched_seeds_across_algorithms(tmp_path: Path) -> None:
    """GA trial i and RS trial i share a seed so each pair sees the same RNG."""
    ga_seen: list[dict] = []
    rs_seen: list[dict] = []
    run_experiment(
        {},
        trials=3,
        output_root=tmp_path,
        algorithm_overrides={
            "ga": _make_mock_algo(0.8, ga_seen),
            "rs": _make_mock_algo(0.5, rs_seen),
        },
    )
    ga_seeds = [c["seed"] for c in ga_seen]
    rs_seeds = [c["seed"] for c in rs_seen]
    assert ga_seeds == rs_seeds == [0, 1, 2]


def test_run_experiment_writes_per_trial_subdirs(tmp_path: Path) -> None:
    run_experiment(
        {},
        trials=2,
        output_root=tmp_path,
        algorithm_overrides={
            "ga": _make_mock_algo(0.8, []),
            "rs": _make_mock_algo(0.5, []),
        },
    )
    children = sorted(p.name for p in tmp_path.iterdir() if p.is_dir())
    assert len(children) == 4
    assert sum(1 for c in children if c.startswith("ga_trial_")) == 2
    assert sum(1 for c in children if c.startswith("rs_trial_")) == 2


def test_run_experiment_returns_best_blended_from_logs(tmp_path: Path) -> None:
    results = run_experiment(
        {},
        trials=2,
        output_root=tmp_path,
        algorithm_overrides={
            "ga": _make_mock_algo(0.85, []),
            "rs": _make_mock_algo(0.55, []),
        },
    )
    ga = [r for r in results if r.algorithm == "ga"]
    rs = [r for r in results if r.algorithm == "rs"]
    assert all(r.best_blended == pytest.approx(0.85) for r in ga)
    assert all(r.best_blended == pytest.approx(0.55) for r in rs)


def test_run_experiment_progress_callback_fires_per_trial(tmp_path: Path) -> None:
    seen: list[TrialResult] = []
    run_experiment(
        {},
        trials=2,
        output_root=tmp_path,
        algorithm_overrides={
            "ga": _make_mock_algo(0.8, []),
            "rs": _make_mock_algo(0.5, []),
        },
        progress=seen.append,
    )
    assert len(seen) == 4
    assert all(isinstance(r, TrialResult) for r in seen)


def test_run_experiment_forwards_algorithm_kwargs(tmp_path: Path) -> None:
    captured: list[dict] = []
    run_experiment(
        {},
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.9, captured)},
        score_fn="my-score-fn",  # arbitrary marker
        functions=["a.py"],
    )
    assert captured[0]["score_fn"] == "my-score-fn"
    assert captured[0]["functions"] == ["a.py"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_run_experiment_rejects_zero_trials(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="trials"):
        run_experiment(
            {}, trials=0, output_root=tmp_path,
            algorithm_overrides={"ga": _make_mock_algo(0.8, [])},
        )


def test_run_experiment_rejects_unknown_algorithm(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown algorithm"):
        run_experiment(
            {}, trials=1, output_root=tmp_path, algorithms=["does-not-exist"],
        )
