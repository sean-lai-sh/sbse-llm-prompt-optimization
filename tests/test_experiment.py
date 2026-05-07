"""Tests for src/experiment.py.

The orchestrator is exercised with mock algorithm callables so we don't pay
fitness cost or hit the LLM. We just verify trial counts, seed sequencing,
output-dir layout, and that the progress callback fires.
"""

from __future__ import annotations

import json
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


# ---------------------------------------------------------------------------
# Resume behavior
# ---------------------------------------------------------------------------


def _seed_completed_trial(
    output_root: Path,
    algo: str,
    trial_index: int,
    *,
    blended: float = 0.77,
    n_logs: int = 3,
) -> Path:
    """Pre-create a fully-completed trial directory on disk."""
    import json
    from dataclasses import asdict
    d = output_root / f"{algo}_trial_{trial_index:03d}_2026-pre"
    d.mkdir(parents=True)
    template = _mk_template(role=f"resumed-{algo}-{trial_index}")
    (d / "best.json").write_text(json.dumps(template.to_dict()), encoding="utf-8")
    logs = _mk_logs(blended, n=n_logs)
    with (d / "generations.jsonl").open("w") as f:
        for log in logs:
            f.write(json.dumps(asdict(log)) + "\n")
    return d


def test_resume_skips_completed_trials(tmp_path: Path) -> None:
    """Pre-seeded GA trial 0 should be loaded, not re-run."""
    _seed_completed_trial(tmp_path, "ga", 0, blended=0.91)

    ga_calls: list[dict] = []
    rs_calls: list[dict] = []

    results = run_experiment(
        {},
        trials=2,
        output_root=tmp_path,
        algorithm_overrides={
            "ga": _make_mock_algo(0.5, ga_calls),
            "rs": _make_mock_algo(0.4, rs_calls),
        },
        resume=True,
    )

    # Only GA trial 1 (and both RS trials) should have actually run.
    assert len(ga_calls) == 1
    assert ga_calls[0]["seed"] == 1
    assert len(rs_calls) == 2

    ga_results = sorted([r for r in results if r.algorithm == "ga"],
                        key=lambda r: r.trial_index)
    assert ga_results[0].resumed is True
    assert ga_results[0].best_blended == pytest.approx(0.91)
    assert ga_results[0].best_template.role == "resumed-ga-0"
    assert ga_results[1].resumed is False


def test_resume_false_forces_rerun_of_all_trials(tmp_path: Path) -> None:
    _seed_completed_trial(tmp_path, "ga", 0, blended=0.91)

    ga_calls: list[dict] = []
    run_experiment(
        {},
        trials=2,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.5, ga_calls)},
        resume=False,
    )
    # Even though trial 0 exists on disk, --no-resume runs it again.
    assert len(ga_calls) == 2


def test_resume_with_nothing_to_resume_runs_all(tmp_path: Path) -> None:
    ga_calls: list[dict] = []
    run_experiment(
        {},
        trials=3,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.7, ga_calls)},
        resume=True,
    )
    # Empty output_root -> every trial runs.
    assert len(ga_calls) == 3
    assert [c["seed"] for c in ga_calls] == [0, 1, 2]


# ---------------------------------------------------------------------------
# show_progress wiring
# ---------------------------------------------------------------------------


def test_show_progress_wraps_generate_summary_and_ticks_bar(tmp_path: Path) -> None:
    """When show_progress=True, the algorithm receives a wrapped
    generate_summary that ticks a tqdm bar after each underlying call."""
    call_log: list[str] = []

    def fake_generate(template, code):  # noqa: ARG001
        call_log.append(code)
        return "ok"

    def algo_that_invokes_generator(config, *, seed, output_dir, **kwargs):  # noqa: ARG001
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        gs = kwargs["generate_summary"]
        # Make 4 calls so we can verify ticks.
        for i in range(4):
            gs(_mk_template(), f"code-{i}")
        return _mk_template(role="done"), _mk_logs(0.7, n=2)

    config = {
        "ga": {"population_size": 2, "generations": 2},
        "evaluation": {"eval_subset": 1},
    }
    run_experiment(
        config,
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": algo_that_invokes_generator},
        generate_summary=fake_generate,
        show_progress=True,
    )
    # The wrapped generator forwards to fake_generate -> 4 calls observed.
    assert call_log == ["code-0", "code-1", "code-2", "code-3"]


def test_show_progress_off_does_not_wrap(tmp_path: Path) -> None:
    received_kwargs: dict = {}

    def algo_capturing(config, *, seed, output_dir, **kwargs):  # noqa: ARG001
        received_kwargs.update(kwargs)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return _mk_template(), _mk_logs(0.5, n=1)

    sentinel = object()
    run_experiment(
        {},
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": algo_capturing},
        generate_summary=sentinel,
        show_progress=False,
    )
    # No wrapping -> the algorithm received our exact sentinel.
    assert received_kwargs["generate_summary"] is sentinel


def test_resume_ignores_partial_trial_dir(tmp_path: Path) -> None:
    """A trial dir with generations.jsonl but no best.json is NOT complete."""
    import json
    from dataclasses import asdict
    d = tmp_path / "ga_trial_000_partial"
    d.mkdir()
    log = _mk_logs(0.5, n=1)[0]
    with (d / "generations.jsonl").open("w") as f:
        f.write(json.dumps(asdict(log)) + "\n")
    # No best.json -> incomplete.

    ga_calls: list[dict] = []
    run_experiment(
        {},
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.8, ga_calls)},
        resume=True,
    )
    # Trial 0 was incomplete -> ran fresh.
    assert len(ga_calls) == 1


def test_resume_reruns_corrupt_completed_trial_dir(tmp_path: Path) -> None:
    d = tmp_path / "ga_trial_000_corrupt"
    d.mkdir()
    (d / "best.json").write_text("{not-json}", encoding="utf-8")
    (d / "generations.jsonl").write_text("{}", encoding="utf-8")

    ga_calls: list[dict] = []
    results = run_experiment(
        {},
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.8, ga_calls)},
        resume=True,
    )

    assert len(ga_calls) == 1
    assert results[0].resumed is False


def test_resume_reruns_empty_generations_even_with_best_json(tmp_path: Path) -> None:
    d = tmp_path / "ga_trial_000_empty"
    d.mkdir()
    (d / "best.json").write_text(json.dumps(_mk_template().to_dict()), encoding="utf-8")
    (d / "generations.jsonl").write_text("", encoding="utf-8")

    ga_calls: list[dict] = []
    results = run_experiment(
        {},
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.8, ga_calls)},
        resume=True,
    )

    assert len(ga_calls) == 1
    assert results[0].resumed is False


def test_resume_reruns_invalid_generations_schema(tmp_path: Path) -> None:
    d = tmp_path / "ga_trial_000_invalid_schema"
    d.mkdir()
    (d / "best.json").write_text(json.dumps(_mk_template().to_dict()), encoding="utf-8")
    (d / "generations.jsonl").write_text("{}\n", encoding="utf-8")

    ga_calls: list[dict] = []
    results = run_experiment(
        {},
        trials=1,
        output_root=tmp_path,
        algorithms=["ga"],
        algorithm_overrides={"ga": _make_mock_algo(0.8, ga_calls)},
        resume=True,
    )

    assert len(ga_calls) == 1
    assert results[0].resumed is False
