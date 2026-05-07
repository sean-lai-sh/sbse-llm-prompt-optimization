"""Tests for src/stats.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.stats import (
    ComparisonResult,
    cliffs_delta,
    compare_distributions,
    wilcoxon_ranksum,
)


# ---------------------------------------------------------------------------
# Wilcoxon rank-sum
# ---------------------------------------------------------------------------


def test_wilcoxon_same_distribution_high_p() -> None:
    a = [0.5, 0.6, 0.55, 0.52, 0.58, 0.51, 0.57, 0.53, 0.56, 0.54]
    b = [0.5, 0.6, 0.55, 0.52, 0.58, 0.51, 0.57, 0.53, 0.56, 0.54]
    _, p = wilcoxon_ranksum(a, b)
    assert p > 0.5


def test_wilcoxon_clearly_different_distributions_low_p() -> None:
    a = [0.9, 0.92, 0.88, 0.91, 0.93, 0.89, 0.94, 0.9, 0.91, 0.92]
    b = [0.1, 0.12, 0.08, 0.11, 0.13, 0.09, 0.14, 0.1, 0.11, 0.12]
    _, p = wilcoxon_ranksum(a, b)
    assert p < 0.001


def test_wilcoxon_rejects_empty() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        wilcoxon_ranksum([], [0.5])


# ---------------------------------------------------------------------------
# Cliff's delta
# ---------------------------------------------------------------------------


def test_cliffs_delta_identical_is_zero() -> None:
    a = [0.5, 0.6, 0.7]
    delta, label = cliffs_delta(a, a)
    assert delta == 0.0
    assert label == "negligible"


def test_cliffs_delta_a_dominates_is_one() -> None:
    a = [0.9, 0.95, 0.92]
    b = [0.1, 0.2, 0.15]
    delta, label = cliffs_delta(a, b)
    assert delta == pytest.approx(1.0)
    assert label == "large"


def test_cliffs_delta_b_dominates_is_negative_one() -> None:
    a = [0.1, 0.2]
    b = [0.9, 0.95]
    delta, _ = cliffs_delta(a, b)
    assert delta == pytest.approx(-1.0)


def test_cliffs_delta_label_thresholds() -> None:
    # negligible: identical distributions -> delta = 0
    assert cliffs_delta([1, 2, 3], [1, 2, 3])[1] == "negligible"
    # large: full domination -> |delta| = 1
    assert cliffs_delta([1, 2, 3], [-1, -2, -3])[1] == "large"
    # small: ~10% net win rate (delta around 0.2)
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    b = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # shifted by 1
    delta, label = cliffs_delta(a, b)
    assert 0.147 <= abs(delta) < 0.33
    assert label == "small"


def test_cliffs_delta_rejects_empty() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        cliffs_delta([], [0.5])


# ---------------------------------------------------------------------------
# compare_distributions
# ---------------------------------------------------------------------------


def test_compare_distributions_returns_full_result() -> None:
    ga = [0.7, 0.72, 0.75, 0.71, 0.74, 0.73, 0.7, 0.76, 0.72, 0.73]
    rs = [0.6, 0.62, 0.65, 0.61, 0.64, 0.63, 0.6, 0.66, 0.62, 0.63]
    result = compare_distributions(ga, rs, metric="blended")
    assert isinstance(result, ComparisonResult)
    assert result.metric == "blended"
    assert result.n_a == 10
    assert result.n_b == 10
    assert result.mean_a > result.mean_b
    assert result.cliffs_delta > 0  # GA > RS
    assert result.p_value < 0.01  # clearly different


def test_compare_distributions_to_dict_is_serializable() -> None:
    result = compare_distributions([0.5, 0.6], [0.4, 0.5], metric="rouge_l")
    d = result.to_dict()
    assert set(d.keys()) >= {
        "metric", "n_a", "n_b", "mean_a", "mean_b", "std_a", "std_b",
        "statistic", "p_value", "cliffs_delta", "delta_label",
    }
    # All numeric fields are JSON-friendly floats.
    import json
    json.dumps(d)


def test_compare_distributions_rejects_empty() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        compare_distributions([], [0.5], metric="blended")
