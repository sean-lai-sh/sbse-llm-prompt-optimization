"""Tests for src/fitness.py.

The fitness function is the only signal driving the GA, so we exercise the
math (penalty terms, blend, calibration plumbing) directly with mocked
embeddings and a stub `generate_summary` callable. The only "real" thing
this module pulls in is `rouge_score`, which is fast and deterministic.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src import fitness as fitness_mod
from src.fitness import FitnessConfig, score_prompt
from src.prompt import PromptTemplate


def _mk_template(role: str = "You are a senior engineer.") -> PromptTemplate:
    return PromptTemplate(
        role=role,
        task="Summarize the function in one sentence.",
        guard="Do not include code.",
        format="Plain prose.",
    )


@pytest.fixture
def benchmark(tmp_path: Path) -> tuple[list[Path], list[Path]]:
    """Three (function, reference) pairs."""
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()

    pairs = [
        ("function sumArray(a){return a.reduce((x,y)=>x+y,0);}", "Sums all numbers in the array."),
        ("function maxArray(a){return Math.max(...a);}", "Returns the largest element."),
        ("function reverseStr(s){return s.split('').reverse().join('');}", "Reverses the string."),
    ]
    fns: list[Path] = []
    refs: list[Path] = []
    for i, (code, ref) in enumerate(pairs):
        fn = fn_dir / f"f_{i:03d}.js"
        rf = ref_dir / f"f_{i:03d}.txt"
        fn.write_text(code, encoding="utf-8")
        rf.write_text(ref, encoding="utf-8")
        fns.append(fn)
        refs.append(rf)
    return fns, refs


def _make_gen(generations: Iterable[str]):
    iterator = iter(generations)

    def _gen(template: PromptTemplate, code: str) -> str:  # noqa: ARG001
        return next(iterator)

    return _gen


# ---------------------------------------------------------------------------
# Returned dict shape and scalar invariants
# ---------------------------------------------------------------------------


def test_score_prompt_returns_expected_keys(benchmark) -> None:
    fns, refs = benchmark
    template = _mk_template()
    config = FitnessConfig()

    gen = _make_gen(["a summary"] * len(fns))
    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.7] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=gen, config=config,
        )

    assert set(result.keys()) == {
        "blended", "rouge_l", "cosine_raw", "cosine_calibrated",
        "length_penalty", "format_penalty",
    }
    for v in result.values():
        assert isinstance(v, float)


def test_perfect_match_scores_near_one(benchmark) -> None:
    """Generation == reference: ROUGE-L = 1.0, calibrated cosine = 1.0,
    no penalties → blended = 1.0."""
    fns, refs = benchmark
    template = _mk_template()
    ref_texts = [p.read_text().strip() for p in refs]

    # Mock cosine to return 1.0 (perfect semantic match).
    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[1.0] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(ref_texts),
            config=FitnessConfig(),
        )

    assert result["rouge_l"] == pytest.approx(1.0)
    assert result["cosine_raw"] == pytest.approx(1.0)
    assert result["cosine_calibrated"] == pytest.approx(1.0)
    assert result["format_penalty"] == 0.0
    assert result["length_penalty"] == 0.0
    assert result["blended"] == pytest.approx(1.0)


def test_empty_output_triggers_format_penalty(benchmark) -> None:
    fns, refs = benchmark
    template = _mk_template()

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["", "", ""]),
            config=FitnessConfig(),
        )
    assert result["format_penalty"] == pytest.approx(1.0)


def test_code_fence_triggers_format_penalty(benchmark) -> None:
    fns, refs = benchmark
    template = _mk_template()

    bad = "```python\ndef foo(): pass\n```"
    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen([bad, bad, bad]),
            config=FitnessConfig(),
        )
    assert result["format_penalty"] == pytest.approx(1.0)


def test_mixed_format_penalty_is_averaged(benchmark) -> None:
    fns, refs = benchmark
    template = _mk_template()

    # 1 of 3 outputs degenerate -> mean penalty = 1/3
    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["good summary", "", "another good summary"]),
            config=FitnessConfig(),
        )
    assert result["format_penalty"] == pytest.approx(1 / 3)


def test_overlong_prompt_triggers_length_penalty(benchmark) -> None:
    fns, refs = benchmark
    long_role = "word " * 500
    template = PromptTemplate(role=long_role, task="t", guard="g", format="f")
    config = FitnessConfig(max_prompt_tokens=50)

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["s", "s", "s"]),
            config=config,
        )
    assert result["length_penalty"] > 0


def test_short_prompt_has_no_length_penalty(benchmark) -> None:
    fns, refs = benchmark
    template = _mk_template()

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["short", "short", "short"]),
            config=FitnessConfig(max_prompt_tokens=200),
        )
    assert result["length_penalty"] == 0.0


def test_length_penalty_quadratic_growth_past_floor() -> None:
    """Default exponent=2.0 -> 25% over yields ~0.0625, doubled length yields 1.0."""
    from src.fitness import _length_penalty
    assert _length_penalty(200, 200, exponent=2.0) == 0.0          # at floor
    assert _length_penalty(150, 200, exponent=2.0) == 0.0          # below floor
    assert _length_penalty(250, 200, exponent=2.0) == pytest.approx(0.0625)  # 25% over
    assert _length_penalty(400, 200, exponent=2.0) == pytest.approx(1.0)     # 2x floor
    assert _length_penalty(600, 200, exponent=2.0) == pytest.approx(4.0)     # 3x floor


def test_length_penalty_linear_when_exponent_is_one() -> None:
    """exponent=1.0 recovers the original linear penalty for backwards comparison."""
    from src.fitness import _length_penalty
    assert _length_penalty(250, 200, exponent=1.0) == pytest.approx(0.25)
    assert _length_penalty(400, 200, exponent=1.0) == pytest.approx(1.0)
    assert _length_penalty(600, 200, exponent=1.0) == pytest.approx(2.0)


def test_length_penalty_exponent_is_read_from_config(benchmark) -> None:
    """A higher exponent makes the same overage hurt more in the blended score."""
    fns, refs = benchmark
    long_role = "word " * 500
    template = PromptTemplate(role=long_role, task="t", guard="g", format="f")

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        soft = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["s"] * len(fns)),
            config=FitnessConfig(max_prompt_tokens=50, length_penalty_exponent=1.0),
        )
        harsh = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["s"] * len(fns)),
            config=FitnessConfig(max_prompt_tokens=50, length_penalty_exponent=3.0),
        )
    assert harsh["length_penalty"] > soft["length_penalty"]


# ---------------------------------------------------------------------------
# Calibration is wired through correctly
# ---------------------------------------------------------------------------


def test_cosine_calibration_applied(benchmark) -> None:
    """Raw cosine 0.45 (== baseline) → calibrated 0.0."""
    fns, refs = benchmark
    template = _mk_template()
    config = FitnessConfig(cosine_baseline=0.45)

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.45] * len(fns)):
        result = score_prompt(
            template, fns, refs,
            generate_summary=_make_gen(["s"] * len(fns)),
            config=config,
        )
    assert result["cosine_raw"] == pytest.approx(0.45)
    assert result["cosine_calibrated"] == pytest.approx(0.0)


def test_cosine_above_baseline_is_rescaled(benchmark) -> None:
    """Midpoint between baseline (0.45) and 1.0 → calibrated 0.5."""
    fns, refs = benchmark
    midpoint = (0.45 + 1.0) / 2

    with patch.object(
        fitness_mod, "cosine_similarity_batch", return_value=[midpoint] * len(fns)
    ):
        result = score_prompt(
            _mk_template(), fns, refs,
            generate_summary=_make_gen(["s"] * len(fns)),
            config=FitnessConfig(cosine_baseline=0.45),
        )
    assert result["cosine_calibrated"] == pytest.approx(0.5, abs=1e-6)


# ---------------------------------------------------------------------------
# Subsample mode
# ---------------------------------------------------------------------------


def test_eval_subset_runs_on_subset_only(benchmark) -> None:
    fns, refs = benchmark
    calls: list[str] = []

    def counting_gen(template: PromptTemplate, code: str) -> str:  # noqa: ARG001
        calls.append(code)
        return "ok"

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5, 0.5]):
        score_prompt(
            _mk_template(), fns, refs,
            generate_summary=counting_gen,
            config=FitnessConfig(),
            eval_subset=2,
            seed=42,
        )
    assert len(calls) == 2


def test_eval_subset_seed_is_reproducible(benchmark) -> None:
    fns, refs = benchmark
    seen_a: list[str] = []
    seen_b: list[str] = []

    def gen_a(t, c):  # noqa: ARG001
        seen_a.append(c)
        return "ok"

    def gen_b(t, c):  # noqa: ARG001
        seen_b.append(c)
        return "ok"

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5, 0.5]):
        score_prompt(_mk_template(), fns, refs, generate_summary=gen_a,
                     config=FitnessConfig(), eval_subset=2, seed=7)
        score_prompt(_mk_template(), fns, refs, generate_summary=gen_b,
                     config=FitnessConfig(), eval_subset=2, seed=7)
    assert seen_a == seen_b


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_length_mismatch_raises(tmp_path: Path) -> None:
    fn = tmp_path / "f.js"
    fn.write_text("function f(){}", encoding="utf-8")
    r1 = tmp_path / "r1.txt"
    r2 = tmp_path / "r2.txt"
    r1.write_text("a")
    r2.write_text("b")
    with pytest.raises(ValueError, match="same length"):
        score_prompt(_mk_template(), [fn], [r1, r2],
                     generate_summary=_make_gen(["x"]),
                     config=FitnessConfig())


def test_empty_benchmark_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        score_prompt(_mk_template(), [], [],
                     generate_summary=_make_gen([]),
                     config=FitnessConfig())


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_eval_subset_rejects_non_positive(benchmark, bad) -> None:
    fns, refs = benchmark
    with pytest.raises(ValueError, match="eval_subset"):
        score_prompt(_mk_template(), fns, refs,
                     generate_summary=_make_gen(["x"] * len(fns)),
                     config=FitnessConfig(),
                     eval_subset=bad)


def test_eval_subset_larger_than_benchmark_uses_full(benchmark) -> None:
    fns, refs = benchmark
    calls: list[str] = []

    def gen(t, c):  # noqa: ARG001
        calls.append(c)
        return "ok"

    with patch.object(fitness_mod, "cosine_similarity_batch", return_value=[0.5] * len(fns)):
        score_prompt(_mk_template(), fns, refs,
                     generate_summary=gen,
                     config=FitnessConfig(),
                     eval_subset=999, seed=0)
    assert len(calls) == len(fns)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def test_fitness_config_loads_from_yaml(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "fitness:\n"
        "  alpha: 0.7\n"
        "  cosine_baseline: 0.4\n"
        "  lambda_len: 0.2\n"
        "  lambda_fmt: 0.3\n"
        "  max_prompt_tokens: 150\n",
        encoding="utf-8",
    )
    config = FitnessConfig.from_yaml(cfg)
    assert config.alpha == 0.7
    assert config.cosine_baseline == 0.4
    assert config.lambda_len == 0.2
    assert config.lambda_fmt == 0.3
    assert config.max_prompt_tokens == 150


def test_fitness_config_ignores_unknown_keys(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "fitness:\n"
        "  alpha: 0.6\n"
        "  some_future_key: 99\n",
        encoding="utf-8",
    )
    config = FitnessConfig.from_yaml(cfg)
    assert config.alpha == 0.6
    # Default for unspecified known keys
    assert config.cosine_baseline == 0.45


def test_repo_config_yaml_loads_cleanly() -> None:
    """Smoke test: the actual config.yaml in the repo loads without error."""
    config = FitnessConfig.from_yaml()
    assert 0.0 <= config.alpha <= 1.0
    assert 0.0 <= config.cosine_baseline < 1.0


def test_fitness_config_handles_empty_yaml(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("", encoding="utf-8")
    # Empty file -> all defaults.
    config = FitnessConfig.from_yaml(cfg)
    assert config == FitnessConfig()


def test_fitness_config_rejects_non_mapping_top_level(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        FitnessConfig.from_yaml(cfg)


def test_fitness_config_rejects_non_mapping_fitness_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("fitness: not_a_dict\n", encoding="utf-8")
    with pytest.raises(ValueError, match="fitness"):
        FitnessConfig.from_yaml(cfg)


def test_fitness_config_handles_missing_fitness_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("ga:\n  population_size: 20\n", encoding="utf-8")
    config = FitnessConfig.from_yaml(cfg)
    assert config == FitnessConfig()
