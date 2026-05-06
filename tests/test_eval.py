"""Tests for src/eval.py.

Speed strategy: the real sentence-transformer is loaded ONCE via a
session-scoped fixture and reused across every "real model" test. Math /
shape / aggregation tests bypass the model by mocking
`src.eval.cosine_similarity_batch` or by patching `_get_model`. Target-model
calls (issue #6) are always mocked.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src import eval as eval_mod
from src.prompt import PromptTemplate


# ---------------------------------------------------------------------------
# Session-scoped fixture: load the embedder ONCE for the whole test run.
# Subsequent tests reuse the cached module-level singleton in src.eval.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def loaded_model():
    return eval_mod._get_model()


# ---------------------------------------------------------------------------
# Real-model semantic tests
# ---------------------------------------------------------------------------


def test_identical_strings_cosine_near_one(loaded_model) -> None:
    score = eval_mod.cosine_similarity_score("hello world", "hello world")
    assert score == pytest.approx(1.0, abs=1e-3)


def test_unrelated_strings_cosine_well_below_paraphrase(loaded_model) -> None:
    # BGE-style embedders have a non-trivial baseline (~0.5) even for short
    # unrelated strings, so we assert relative ordering rather than an
    # absolute floor: clearly-unrelated text must score lower than a
    # known paraphrase pair, with a comfortable margin.
    unrelated = eval_mod.cosine_similarity_score(
        "Sorts an array of integers in ascending order using quicksort.",
        "The capital of France is Paris and the Eiffel Tower is famous.",
    )
    paraphrase = eval_mod.cosine_similarity_score(
        "Returns the sum of all numbers in the input array.",
        "Computes the total of every element in the given list.",
    )
    assert unrelated < paraphrase - 0.15
    assert unrelated < 0.7


def test_paraphrase_pair_cosine_above_threshold(loaded_model) -> None:
    # A natural code-summary paraphrase pair: same meaning, different wording.
    a = "Returns the sum of all numbers in the input array."
    b = "Computes the total of every element in the given list."
    score = eval_mod.cosine_similarity_score(a, b)
    assert score > 0.6


def test_batch_matches_single_call(loaded_model) -> None:
    pairs = [
        ("hello world", "hello world"),
        ("sum the array", "add up the list elements"),
        ("hello world", "completely different topic xyz"),
    ]
    gens = [g for g, _ in pairs]
    refs = [r for _, r in pairs]

    batched = eval_mod.cosine_similarity_batch(gens, refs)
    individual = [eval_mod.cosine_similarity_score(g, r) for g, r in pairs]

    assert len(batched) == len(individual)
    for b, i in zip(batched, individual):
        assert b == pytest.approx(i, abs=1e-5)


# ---------------------------------------------------------------------------
# Pure / shape tests (no real model required)
# ---------------------------------------------------------------------------


def test_batch_length_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="same length"):
        eval_mod.cosine_similarity_batch(["a", "b"], ["c"])


def test_batch_empty_inputs_returns_empty_list() -> None:
    # Empty inputs must not even touch the model.
    with patch.object(eval_mod, "_get_model") as mock_get:
        result = eval_mod.cosine_similarity_batch([], [])
        assert result == []
        mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# Calibration: linear baseline rescale.
# ---------------------------------------------------------------------------


def test_calibrate_cosine_identity_maps_to_one() -> None:
    assert eval_mod.calibrate_cosine(1.0, 0.45) == pytest.approx(1.0)


def test_calibrate_cosine_at_baseline_maps_to_zero() -> None:
    assert eval_mod.calibrate_cosine(0.45, 0.45) == pytest.approx(0.0)


def test_calibrate_cosine_below_baseline_clamped_to_zero() -> None:
    assert eval_mod.calibrate_cosine(0.1, 0.45) == 0.0


def test_calibrate_cosine_above_baseline_rescaled() -> None:
    # midpoint between baseline (0.45) and 1.0 should land at 0.5
    midpoint = (0.45 + 1.0) / 2
    assert eval_mod.calibrate_cosine(midpoint, 0.45) == pytest.approx(0.5, abs=1e-6)


def test_calibrate_cosine_rejects_invalid_baseline() -> None:
    with pytest.raises(ValueError, match="baseline"):
        eval_mod.calibrate_cosine(0.8, 1.0)
    with pytest.raises(ValueError, match="baseline"):
        eval_mod.calibrate_cosine(0.8, -0.1)


def test_calibrate_cosine_batch_matches_scalar() -> None:
    raws = [0.1, 0.45, 0.7, 1.0]
    batched = eval_mod.calibrate_cosine_batch(raws, baseline=0.45)
    scalar = [eval_mod.calibrate_cosine(r, 0.45) for r in raws]
    for b, s in zip(batched, scalar):
        assert b == pytest.approx(s, abs=1e-6)


# ---------------------------------------------------------------------------
# evaluate_prompt: target_model is mocked, embedder is mocked for speed/math.
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_benchmark(tmp_path: Path) -> tuple[list[Path], list[Path]]:
    """Write three (function, reference) pairs to a temp dir."""
    fn_dir = tmp_path / "functions"
    ref_dir = tmp_path / "references"
    fn_dir.mkdir()
    ref_dir.mkdir()

    functions = []
    references = []
    for i, (code, ref) in enumerate(
        [
            ("function sumArray(a){return a.reduce((x,y)=>x+y,0);}", "Sums all numbers in the array."),
            ("function maxArray(a){return Math.max(...a);}", "Returns the largest element."),
            ("function reverseStr(s){return s.split('').reverse().join('');}", "Reverses the string."),
        ]
    ):
        fn = fn_dir / f"f_{i:03d}.js"
        rf = ref_dir / f"f_{i:03d}.txt"
        fn.write_text(code, encoding="utf-8")
        rf.write_text(ref, encoding="utf-8")
        functions.append(fn)
        references.append(rf)

    return functions, references


def _mk_template() -> PromptTemplate:
    return PromptTemplate(
        role="You are a senior engineer.",
        task="Summarize the function in one sentence.",
        guard="Do not include code.",
        format="Plain prose.",
    )


def _make_target_model_module(generations: list[str]):
    """Build a fake src.target_model module exposing generate_summary()."""
    fake = MagicMock()
    iterator = iter(generations)

    def _gen(template, code):  # noqa: ARG001
        return next(iterator)

    fake.generate_summary = MagicMock(side_effect=_gen)
    return fake


def test_evaluate_prompt_returns_expected_shape(fake_benchmark) -> None:
    functions, references = fake_benchmark
    template = _mk_template()

    fake_target_model = _make_target_model_module(
        ["Sums an array.", "Returns the maximum.", "Reverses a string."]
    )

    # Mock cosine_similarity_batch with controlled outputs so we can verify math.
    fake_cosines = [0.8, 0.6, 0.7]

    with patch.dict(sys.modules, {"src.target_model": fake_target_model}), patch.object(
        eval_mod, "cosine_similarity_batch", return_value=fake_cosines
    ):
        result = eval_mod.evaluate_prompt(template, functions, references)

    assert set(result.keys()) == {"per_file", "aggregate"}
    assert len(result["per_file"]) == 3
    for entry in result["per_file"]:
        assert set(entry.keys()) == {"filename", "rouge_l", "cosine"}
        assert isinstance(entry["filename"], str)
        assert isinstance(entry["rouge_l"], float)
        assert isinstance(entry["cosine"], float)

    agg = result["aggregate"]
    assert set(agg.keys()) == {
        "rouge_l_mean",
        "rouge_l_std",
        "cosine_mean",
        "cosine_std",
    }
    # Cosine values came straight from our mock; mean/std should match exactly.
    assert agg["cosine_mean"] == pytest.approx(statistics.fmean(fake_cosines))
    assert agg["cosine_std"] == pytest.approx(statistics.stdev(fake_cosines))


def test_evaluate_prompt_aggregates_rouge_correctly(fake_benchmark) -> None:
    """When generation == reference, ROUGE-L is 1.0; mean should be 1.0, std 0.0."""
    functions, references = fake_benchmark
    template = _mk_template()

    # Make the target model echo the reference back, so ROUGE-L = 1.0 for all.
    ref_texts = [p.read_text(encoding="utf-8").strip() for p in references]
    fake_target_model = _make_target_model_module(ref_texts)

    with patch.dict(sys.modules, {"src.target_model": fake_target_model}), patch.object(
        eval_mod, "cosine_similarity_batch", return_value=[0.5, 0.5, 0.5]
    ):
        result = eval_mod.evaluate_prompt(template, functions, references)

    rouge_values = [entry["rouge_l"] for entry in result["per_file"]]
    for v in rouge_values:
        assert v == pytest.approx(1.0)
    assert result["aggregate"]["rouge_l_mean"] == pytest.approx(1.0)
    assert result["aggregate"]["rouge_l_std"] == pytest.approx(0.0)
    assert result["aggregate"]["cosine_mean"] == pytest.approx(0.5)
    assert result["aggregate"]["cosine_std"] == pytest.approx(0.0)


def test_evaluate_prompt_filenames_match_inputs(fake_benchmark) -> None:
    functions, references = fake_benchmark
    template = _mk_template()

    fake_target_model = _make_target_model_module(["a", "b", "c"])

    with patch.dict(sys.modules, {"src.target_model": fake_target_model}), patch.object(
        eval_mod, "cosine_similarity_batch", return_value=[0.1, 0.2, 0.3]
    ):
        result = eval_mod.evaluate_prompt(template, functions, references)

    expected = [p.name for p in functions]
    actual = [entry["filename"] for entry in result["per_file"]]
    assert actual == expected


def test_evaluate_prompt_length_mismatch_raises(tmp_path: Path) -> None:
    fn = tmp_path / "f.js"
    fn.write_text("function f(){}", encoding="utf-8")
    ref1 = tmp_path / "r1.txt"
    ref2 = tmp_path / "r2.txt"
    ref1.write_text("a", encoding="utf-8")
    ref2.write_text("b", encoding="utf-8")

    fake_target_model = _make_target_model_module(["x"])
    with patch.dict(sys.modules, {"src.target_model": fake_target_model}):
        with pytest.raises(ValueError, match="same length"):
            eval_mod.evaluate_prompt(_mk_template(), [fn], [ref1, ref2])
