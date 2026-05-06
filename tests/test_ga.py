"""Tests for src/ga.py.

Fitness is mocked end-to-end (no API, no embedder) via the ``score_fn``
dependency-injection kwarg on :func:`run_ga`. The mock rewards a specific
``role`` value so we can assert the GA actually converges instead of merely
returning *something*.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from src.ga import (
    _default_benchmark,
    crossover,
    mutate,
    random_template,
    run_ga,
    tournament_select,
)
from src.prompt import COMPONENT_FIELDS, PromptTemplate
from src.search_log import GenerationLog


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


TARGET_ROLE = "You are a senior engineer."


@pytest.fixture
def tiny_bank() -> dict[str, list[str]]:
    """A bank with multiple alternatives per field so mutation has options."""
    return {
        "role": [
            TARGET_ROLE,
            "You are a junior engineer.",
            "You are a product manager.",
            "You are a designer.",
        ],
        "task": [f"task_{i}" for i in range(4)],
        "guard": [f"guard_{i}" for i in range(4)],
        "format": [f"format_{i}" for i in range(4)],
    }


@pytest.fixture
def benchmark_paths(tmp_path: Path) -> tuple[list[Path], list[Path]]:
    """A trivial paired benchmark; the mock fitness ignores its contents."""
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    fns, refs = [], []
    for i in range(2):
        fn = fn_dir / f"f_{i}.js"
        rf = ref_dir / f"f_{i}.txt"
        fn.write_text("function f(){}", encoding="utf-8")
        rf.write_text("trivial", encoding="utf-8")
        fns.append(fn)
        refs.append(rf)
    return fns, refs


def _mock_score(template: PromptTemplate, functions, references, **kwargs) -> dict:
    """Reward `TARGET_ROLE`; punish everything else. No I/O, fast, deterministic."""
    blended = 0.9 if template.role == TARGET_ROLE else 0.1
    return {
        "blended": blended,
        "rouge_l": blended,
        "cosine_raw": blended,
        "cosine_calibrated": blended,
        "length_penalty": 0.0,
        "format_penalty": 0.0,
    }


def _config(**ga_overrides) -> dict:
    base = {
        "ga": {
            "population_size": 8,
            "generations": 4,
            "elite_count": 2,
            "crossover_rate": 0.7,
            "mutation_rate": 0.3,
            "tournament_k": 3,
            "workers": 1,  # serial for deterministic test ordering
        },
        "evaluation": {"eval_subset": None},
    }
    base["ga"].update(ga_overrides)
    return base


# ---------------------------------------------------------------------------
# random_template
# ---------------------------------------------------------------------------


def test_random_template_uses_only_bank_entries(tiny_bank) -> None:
    rng = random.Random(0)
    for _ in range(50):
        t = random_template(tiny_bank, rng)
        for f in COMPONENT_FIELDS:
            assert getattr(t, f) in tiny_bank[f]


# ---------------------------------------------------------------------------
# crossover
# ---------------------------------------------------------------------------


def test_crossover_fields_come_from_either_parent(tiny_bank) -> None:
    rng = random.Random(1)
    a = PromptTemplate(role="rA", task="tA", guard="gA", format="fA")
    b = PromptTemplate(role="rB", task="tB", guard="gB", format="fB")
    for _ in range(50):
        child = crossover(a, b, rng)
        for f in COMPONENT_FIELDS:
            assert getattr(child, f) in {getattr(a, f), getattr(b, f)}


def test_crossover_actually_swaps_at_least_one_field() -> None:
    """Distinct parents → child must differ from parent_a in at least one field."""
    rng = random.Random(2)
    a = PromptTemplate(role="rA", task="tA", guard="gA", format="fA")
    b = PromptTemplate(role="rB", task="tB", guard="gB", format="fB")
    for _ in range(20):
        child = crossover(a, b, rng)
        assert child != a


# ---------------------------------------------------------------------------
# mutate
# ---------------------------------------------------------------------------


def test_mutate_p_zero_is_identity(tiny_bank) -> None:
    rng = random.Random(3)
    t = PromptTemplate(role=TARGET_ROLE, task="task_0", guard="guard_0", format="format_0")
    assert mutate(t, tiny_bank, rng, p_mut=0.0) == t


def test_mutate_p_one_changes_every_field(tiny_bank) -> None:
    rng = random.Random(4)
    t = PromptTemplate(role=TARGET_ROLE, task="task_0", guard="guard_0", format="format_0")
    mutated = mutate(t, tiny_bank, rng, p_mut=1.0)
    for f in COMPONENT_FIELDS:
        assert getattr(mutated, f) != getattr(t, f)
        assert getattr(mutated, f) in tiny_bank[f]


def test_mutate_singleton_bank_is_identity() -> None:
    """A field with only one alternative cannot mutate to a different value."""
    bank = {f: ["only"] for f in COMPONENT_FIELDS}
    rng = random.Random(5)
    t = PromptTemplate(role="only", task="only", guard="only", format="only")
    assert mutate(t, bank, rng, p_mut=1.0) == t


# ---------------------------------------------------------------------------
# tournament_select
# ---------------------------------------------------------------------------


def test_tournament_favors_higher_scores() -> None:
    """Over many trials with k=3, the top-scored individual wins more often than the lowest."""
    rng = random.Random(6)
    pop = [PromptTemplate(role=str(i), task="t", guard="g", format="f") for i in range(5)]
    scores = [0.1, 0.2, 0.3, 0.8, 0.9]  # idx 4 is best, idx 0 worst
    wins = [0] * len(pop)
    trials = 1000
    for _ in range(trials):
        winner = tournament_select(pop, scores, k=3, rng=rng)
        wins[pop.index(winner)] += 1
    # The two highest-scored should dominate the two lowest.
    assert wins[4] + wins[3] > wins[0] + wins[1]
    # Best should win a clear majority of single-best matchups vs worst.
    assert wins[4] > wins[0] * 5


def test_tournament_k_one_is_uniform_random() -> None:
    """k=1 reduces to uniform sampling — every individual reachable."""
    rng = random.Random(7)
    pop = [PromptTemplate(role=str(i), task="t", guard="g", format="f") for i in range(4)]
    scores = [0.0, 0.0, 0.0, 1.0]
    seen = {tournament_select(pop, scores, k=1, rng=rng) for _ in range(200)}
    assert seen == set(pop)


# ---------------------------------------------------------------------------
# run_ga: outputs, schema, evolution, reproducibility
# ---------------------------------------------------------------------------


def test_run_ga_writes_logs_and_best(tiny_bank, benchmark_paths, tmp_path) -> None:
    fns, refs = benchmark_paths
    out = tmp_path / "run"
    config = _config(generations=3, population_size=6)

    best, logs = run_ga(
        config,
        score_fn=_mock_score,
        functions=fns,
        references=refs,
        bank=tiny_bank,
        output_dir=out,
        seed=0,
    )

    assert isinstance(best, PromptTemplate)
    assert len(logs) == 3
    assert all(isinstance(l, GenerationLog) for l in logs)

    # generations.jsonl: one row per generation, each parses back to the schema.
    log_path = out / "generations.jsonl"
    assert log_path.exists()
    rows = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    assert len(rows) == 3
    expected_keys = {
        "generation", "best_blended", "mean_blended", "worst_blended",
        "best_rouge_l", "best_cosine_raw", "best_cosine_calibrated",
        "best_template",
    }
    for row in rows:
        assert set(row.keys()) == expected_keys
        assert set(row["best_template"].keys()) == set(COMPONENT_FIELDS)

    # best.json deserializes to a valid PromptTemplate.
    best_path = out / "best.json"
    assert best_path.exists()
    restored = PromptTemplate.from_dict(json.loads(best_path.read_text()))
    assert restored == best


def test_run_ga_converges_toward_target_role(tiny_bank, benchmark_paths, tmp_path) -> None:
    """With a fitness that strongly rewards a specific role, the GA should
    surface the high-fitness role as the winner."""
    fns, refs = benchmark_paths
    config = _config(
        population_size=10,
        generations=8,
        elite_count=2,
        mutation_rate=0.2,
        crossover_rate=0.7,
    )

    best, logs = run_ga(
        config,
        score_fn=_mock_score,
        functions=fns,
        references=refs,
        bank=tiny_bank,
        output_dir=tmp_path / "run",
        seed=0,
    )

    # With elitism + selection pressure, the best at the final generation
    # must be at least as good as at the first.
    assert logs[-1].best_blended >= logs[0].best_blended
    # And convergence: best individual carries the high-fitness role.
    assert best.role == TARGET_ROLE
    assert logs[-1].best_blended == pytest.approx(0.9)


def test_run_ga_elitism_preserves_best(tiny_bank, benchmark_paths, tmp_path) -> None:
    """best_blended is monotonically non-decreasing across generations when elite_count >= 1."""
    fns, refs = benchmark_paths
    config = _config(
        population_size=8,
        generations=6,
        elite_count=2,
        mutation_rate=0.5,  # high mutation to stress elitism
        crossover_rate=0.7,
    )
    _, logs = run_ga(
        config,
        score_fn=_mock_score,
        functions=fns,
        references=refs,
        bank=tiny_bank,
        output_dir=tmp_path / "run",
        seed=0,
    )
    best_curve = [l.best_blended for l in logs]
    for prev, curr in zip(best_curve, best_curve[1:]):
        assert curr >= prev, f"elitism violated: {best_curve}"


def test_run_ga_is_reproducible(tiny_bank, benchmark_paths, tmp_path) -> None:
    """Same seed → identical winner and identical generation logs."""
    fns, refs = benchmark_paths
    config = _config(generations=4, population_size=8)

    best1, logs1 = run_ga(
        config, score_fn=_mock_score, functions=fns, references=refs,
        bank=tiny_bank, output_dir=tmp_path / "run1", seed=42,
    )
    best2, logs2 = run_ga(
        config, score_fn=_mock_score, functions=fns, references=refs,
        bank=tiny_bank, output_dir=tmp_path / "run2", seed=42,
    )

    assert best1 == best2
    assert len(logs1) == len(logs2)
    for a, b in zip(logs1, logs2):
        assert a == b


def test_run_ga_different_seeds_can_diverge(tiny_bank, benchmark_paths, tmp_path) -> None:
    """Sanity: seeded RNG actually drives variation (otherwise reproducibility is vacuous)."""
    fns, refs = benchmark_paths
    config = _config(generations=2, population_size=6, mutation_rate=0.5)

    _, logs1 = run_ga(
        config, score_fn=_mock_score, functions=fns, references=refs,
        bank=tiny_bank, output_dir=tmp_path / "a", seed=1,
    )
    _, logs2 = run_ga(
        config, score_fn=_mock_score, functions=fns, references=refs,
        bank=tiny_bank, output_dir=tmp_path / "b", seed=2,
    )
    # At least one row should differ across runs with different seeds.
    assert any(a != b for a, b in zip(logs1, logs2))


def test_run_ga_threadpool_path(tiny_bank, benchmark_paths, tmp_path) -> None:
    """workers > 1 exercises the ThreadPoolExecutor branch and still returns a valid run."""
    fns, refs = benchmark_paths
    config = _config(workers=4, population_size=6, generations=2)
    best, logs = run_ga(
        config, score_fn=_mock_score, functions=fns, references=refs,
        bank=tiny_bank, output_dir=tmp_path / "run", seed=0,
    )
    assert isinstance(best, PromptTemplate)
    assert len(logs) == 2


# ---------------------------------------------------------------------------
# _default_benchmark
# ---------------------------------------------------------------------------


def test_default_benchmark_pairs_by_stem(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (fn_dir / "b.py").write_text("def b(): pass")
    (ref_dir / "a.txt").write_text("ref a")
    (ref_dir / "b.txt").write_text("ref b")

    fns, refs = _default_benchmark(fn_dir, ref_dir)
    assert [p.stem for p in fns] == [p.stem for p in refs]
    assert len(fns) == 2


def test_default_benchmark_raises_on_unpaired_function(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (fn_dir / "orphan.py").write_text("def b(): pass")
    (ref_dir / "a.txt").write_text("ref a")

    with pytest.raises(ValueError, match="missing references"):
        _default_benchmark(fn_dir, ref_dir)


def test_default_benchmark_raises_on_orphan_reference(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (ref_dir / "a.txt").write_text("ref a")
    (ref_dir / "orphan.txt").write_text("orphan")

    with pytest.raises(ValueError, match="without functions"):
        _default_benchmark(fn_dir, ref_dir)
