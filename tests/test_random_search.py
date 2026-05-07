"""Tests for src/random_search.py.

These tests fully mock the fitness function so no real API or embedding
calls happen. The mock returns a deterministic blended score keyed off the
template's role, which lets us verify reproducibility, schema, budget, and
log file behavior.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from threading import Lock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.prompt import COMPONENT_FIELDS, PromptTemplate, load_component_bank
from src.random_search import (
    _default_benchmark,
    random_template,
    run_rs,
)
from src.search_log import GenerationLog


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def bank() -> dict[str, list[str]]:
    return load_component_bank()


@pytest.fixture
def benchmark(tmp_path: Path) -> tuple[list[Path], list[Path]]:
    """Tiny three-pair benchmark on disk."""
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    fns: list[Path] = []
    refs: list[Path] = []
    for i in range(3):
        fn = fn_dir / f"f_{i:03d}.js"
        rf = ref_dir / f"f_{i:03d}.txt"
        fn.write_text(f"function f{i}(){{}}", encoding="utf-8")
        rf.write_text(f"summary {i}", encoding="utf-8")
        fns.append(fn)
        refs.append(rf)
    return fns, refs


@pytest.fixture
def mini_config() -> dict:
    return {
        "ga": {"population_size": 4, "generations": 3},
        "evaluation": {"eval_subset": None},
    }


def _make_mock_score_fn():
    """Counting / deterministic fitness mock.

    Returns ``(mock, calls)`` where ``calls`` is a thread-safe call counter
    and the score is derived from the template's role so the same template
    deterministically produces the same score.
    """
    calls = {"n": 0}
    lock = Lock()

    def mock(template, functions, references, **kwargs):  # noqa: ARG001
        with lock:
            calls["n"] += 1
        # Deterministic per-template score: hash the role into [0, 1).
        # Stable across runs because PromptTemplate is frozen.
        h = abs(hash(template.role)) % 1000
        blended = h / 1000.0
        return {
            "blended": blended,
            "rouge_l": blended,
            "cosine_raw": blended,
            "cosine_calibrated": blended,
            "length_penalty": 0.0,
            "format_penalty": 0.0,
        }

    return mock, calls


# ---------------------------------------------------------------------------
# random_template
# ---------------------------------------------------------------------------


def test_random_template_returns_valid_prompt_template(bank: dict[str, list[str]]) -> None:
    import random as _r

    rng = _r.Random(123)
    t = random_template(bank, rng)
    assert isinstance(t, PromptTemplate)
    for field in COMPONENT_FIELDS:
        assert getattr(t, field) in bank[field]


def test_random_template_is_deterministic(bank: dict[str, list[str]]) -> None:
    import random as _r

    a = random_template(bank, _r.Random(42))
    b = random_template(bank, _r.Random(42))
    assert a == b


# ---------------------------------------------------------------------------
# run_rs: budget, schema, file outputs
# ---------------------------------------------------------------------------


def test_run_rs_uses_full_p_times_g_budget(
    benchmark, mini_config, tmp_path: Path
) -> None:
    fns, refs = benchmark
    mock, calls = _make_mock_score_fn()

    best, logs = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=tmp_path / "out",
        score_fn=mock,
        seed=0,
        workers=2,
    )
    P = mini_config["ga"]["population_size"]
    G = mini_config["ga"]["generations"]
    assert calls["n"] == P * G
    assert isinstance(best, PromptTemplate)
    assert len(logs) == G


def test_run_rs_log_schema(benchmark, mini_config, tmp_path: Path) -> None:
    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()

    _, logs = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=tmp_path / "out",
        score_fn=mock,
        seed=0,
        workers=2,
    )
    expected = {
        "generation",
        "best_blended",
        "mean_blended",
        "worst_blended",
        "best_rouge_l",
        "best_cosine_raw",
        "best_cosine_calibrated",
        "best_template",
    }
    for i, log in enumerate(logs):
        assert isinstance(log, GenerationLog)
        d = asdict(log)
        assert set(d.keys()) == expected
        assert d["generation"] == i
        assert isinstance(d["best_blended"], float)
        assert isinstance(d["mean_blended"], float)
        assert isinstance(d["worst_blended"], float)
        assert isinstance(d["best_rouge_l"], float)
        assert isinstance(d["best_cosine_raw"], float)
        assert isinstance(d["best_cosine_calibrated"], float)
        assert isinstance(d["best_template"], dict)
        # best_template round-trips through PromptTemplate.from_dict
        PromptTemplate.from_dict(d["best_template"])
        # best >= mean >= worst within a bucket
        assert d["best_blended"] >= d["mean_blended"] >= d["worst_blended"]


def test_run_rs_returned_best_matches_max_log_best(
    benchmark, mini_config, tmp_path: Path
) -> None:
    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()

    best, logs = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=tmp_path / "out",
        score_fn=mock,
        seed=0,
        workers=2,
    )
    # Re-score `best` through the mock to compare to the max log best.
    best_score = mock(best, fns, refs)["blended"]
    assert best_score == pytest.approx(max(log.best_blended for log in logs))


def test_run_rs_writes_generations_jsonl(
    benchmark, mini_config, tmp_path: Path
) -> None:
    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()
    out = tmp_path / "out"
    _, logs = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=out,
        score_fn=mock,
        seed=0,
        workers=2,
    )
    log_file = out / "generations.jsonl"
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == mini_config["ga"]["generations"]
    # Each line round-trips as JSON with the expected keys.
    for i, line in enumerate(lines):
        row = json.loads(line)
        assert row["generation"] == i
        assert row["best_blended"] == pytest.approx(logs[i].best_blended)


def test_run_rs_writes_best_json(benchmark, mini_config, tmp_path: Path) -> None:
    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()
    out = tmp_path / "out"
    best, _ = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=out,
        score_fn=mock,
        seed=0,
        workers=2,
    )
    best_file = out / "best.json"
    assert best_file.exists()
    payload = json.loads(best_file.read_text(encoding="utf-8"))
    round_trip = PromptTemplate.from_dict(payload)
    assert round_trip == best


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------


def test_run_rs_same_seed_is_reproducible(
    benchmark, mini_config, tmp_path: Path
) -> None:
    fns, refs = benchmark
    mock_a, _ = _make_mock_score_fn()
    mock_b, _ = _make_mock_score_fn()

    best_a, logs_a = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=tmp_path / "a",
        score_fn=mock_a,
        seed=99,
        workers=2,
    )
    best_b, logs_b = run_rs(
        mini_config,
        functions=fns,
        references=refs,
        output_dir=tmp_path / "b",
        score_fn=mock_b,
        seed=99,
        workers=2,
    )
    assert best_a == best_b
    assert [asdict(l) for l in logs_a] == [asdict(l) for l in logs_b]


def test_run_rs_different_seed_diverges(
    benchmark, mini_config, tmp_path: Path
) -> None:
    fns, refs = benchmark
    mock_a, _ = _make_mock_score_fn()
    mock_b, _ = _make_mock_score_fn()

    _, logs_a = run_rs(
        mini_config, functions=fns, references=refs,
        output_dir=tmp_path / "a", score_fn=mock_a, seed=1, workers=2,
    )
    _, logs_b = run_rs(
        mini_config, functions=fns, references=refs,
        output_dir=tmp_path / "b", score_fn=mock_b, seed=2, workers=2,
    )
    # Different seeds -> different sampled populations -> at least one log differs.
    assert [asdict(l) for l in logs_a] != [asdict(l) for l in logs_b]


# ---------------------------------------------------------------------------
# _default_benchmark pairing
# ---------------------------------------------------------------------------


def test_default_benchmark_raises_on_unpaired(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (fn_dir / "b.js").write_text("function b(){}")
    (ref_dir / "a.txt").write_text("a summary")
    # b has no reference -> should raise.
    with pytest.raises(ValueError, match="pairing"):
        _default_benchmark(fn_dir, ref_dir)


def test_default_benchmark_ignores_non_benchmark_files(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (fn_dir / "b.py").write_text("def b(): pass")
    (fn_dir / "c.ts").write_text("function c(): void {}")
    (fn_dir / "manifest.json").write_text("{}")
    (ref_dir / "a.txt").write_text("a")
    (ref_dir / "b.txt").write_text("b")
    (ref_dir / "c.txt").write_text("c")
    (ref_dir / ".gitkeep").write_text("")

    fns, refs = _default_benchmark(fn_dir, ref_dir)
    assert [p.name for p in fns] == ["a.js", "b.py", "c.ts"]
    assert [p.name for p in refs] == ["a.txt", "b.txt", "c.txt"]


def test_default_benchmark_pairs_by_stem(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (fn_dir / "b.js").write_text("function b(){}")
    (ref_dir / "a.txt").write_text("a")
    (ref_dir / "b.txt").write_text("b")
    fns, refs = _default_benchmark(fn_dir, ref_dir)
    assert [p.stem for p in fns] == [p.stem for p in refs]
    assert len(fns) == 2


def test_default_benchmark_raises_on_orphan_reference(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    (fn_dir / "a.js").write_text("function a(){}")
    (ref_dir / "a.txt").write_text("a")
    (ref_dir / "b.txt").write_text("b")
    with pytest.raises(ValueError, match="without functions"):
        _default_benchmark(fn_dir, ref_dir)


def test_default_benchmark_raises_on_empty(tmp_path: Path) -> None:
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()
    with pytest.raises(ValueError, match="no benchmark pairs"):
        _default_benchmark(fn_dir, ref_dir)


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


def test_run_rs_requires_ga_keys(benchmark, tmp_path: Path) -> None:
    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()
    with pytest.raises(ValueError, match="population_size"):
        run_rs(
            {"ga": {"generations": 2}},
            functions=fns, references=refs,
            output_dir=tmp_path / "out", score_fn=mock,
        )


def test_run_rs_rejects_non_positive_budget(benchmark, tmp_path: Path) -> None:
    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()
    with pytest.raises(ValueError, match=">= 1"):
        run_rs(
            {"ga": {"population_size": 0, "generations": 2}},
            functions=fns, references=refs,
            output_dir=tmp_path / "out", score_fn=mock,
        )


def test_run_rs_reads_workers_from_ga_config(benchmark, tmp_path: Path) -> None:
    """workers defaults to ga.workers in config so RS matches GA's parallelism."""
    from unittest.mock import patch
    from src import random_search as rs_mod

    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()

    captured: dict = {}

    class _SpyExecutor:
        def __init__(self, *args, **kwargs):
            captured["max_workers"] = kwargs.get("max_workers")

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def map(self, fn, items):
            return [fn(x) for x in items]

    with patch.object(rs_mod, "ThreadPoolExecutor", _SpyExecutor):
        run_rs(
            {"ga": {"population_size": 2, "generations": 1, "workers": 13}},
            functions=fns, references=refs,
            output_dir=tmp_path / "out", score_fn=mock,
        )
    assert captured["max_workers"] == 13


def test_run_rs_workers_kwarg_overrides_config(benchmark, tmp_path: Path) -> None:
    """Explicit workers= kwarg wins over config ga.workers."""
    from unittest.mock import patch
    from src import random_search as rs_mod

    fns, refs = benchmark
    mock, _ = _make_mock_score_fn()
    captured: dict = {}

    class _SpyExecutor:
        def __init__(self, *args, **kwargs):
            captured["max_workers"] = kwargs.get("max_workers")

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def map(self, fn, items):
            return [fn(x) for x in items]

    with patch.object(rs_mod, "ThreadPoolExecutor", _SpyExecutor):
        run_rs(
            {"ga": {"population_size": 2, "generations": 1, "workers": 13}},
            functions=fns, references=refs,
            output_dir=tmp_path / "out", score_fn=mock,
            workers=5,  # should override the config value
        )
    assert captured["max_workers"] == 5
