"""Statistical utilities for the GA-vs-RS comparison (issue #11).

Two pure functions plus a thin combinator. They take two equal-purpose lists
of best-of-trial fitness values (e.g. GA blended scores vs RS blended scores)
and return the test statistics the paper reports.

The functions deliberately do not log, plot, or read files; that lives in
``scripts/analyze_results.py``. Keeping them pure makes them trivial to unit
test and keeps the experiment harness reusable for follow-up studies.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Sequence

from scipy.stats import ranksums


# Romano et al. 2006 thresholds for Cliff's delta effect size.
_CLIFFS_DELTA_THRESHOLDS = (
    (0.147, "negligible"),
    (0.33, "small"),
    (0.474, "medium"),
)


@dataclass(frozen=True)
class ComparisonResult:
    """Wilcoxon rank-sum + Cliff's delta for one metric."""

    metric: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    std_a: float
    std_b: float
    statistic: float
    p_value: float
    cliffs_delta: float
    delta_label: str

    def to_dict(self) -> dict:
        return asdict(self)


def wilcoxon_ranksum(a: Sequence[float], b: Sequence[float]) -> tuple[float, float]:
    """Two-sided Wilcoxon rank-sum test.

    Returns ``(statistic, p_value)``. Wraps ``scipy.stats.ranksums`` so callers
    do not import scipy directly.
    """
    if len(a) == 0 or len(b) == 0:
        raise ValueError("both samples must be non-empty")
    result = ranksums(list(a), list(b))
    return float(result.statistic), float(result.pvalue)


def cliffs_delta(a: Sequence[float], b: Sequence[float]) -> tuple[float, str]:
    """Cliff's delta non-parametric effect size in [-1, 1].

    Positive values mean A tends to be larger than B; magnitude is bucketed
    using the Romano et al. (2006) thresholds (negligible / small / medium /
    large) reported by the SBSE community.
    """
    if len(a) == 0 or len(b) == 0:
        raise ValueError("both samples must be non-empty")
    n = len(a) * len(b)
    greater = 0
    less = 0
    for x in a:
        for y in b:
            if x > y:
                greater += 1
            elif x < y:
                less += 1
    delta = (greater - less) / n
    label = _delta_label(delta)
    return float(delta), label


def _delta_label(delta: float) -> str:
    abs_d = abs(delta)
    for threshold, name in _CLIFFS_DELTA_THRESHOLDS:
        if abs_d < threshold:
            return name
    return "large"


def compare_distributions(
    a: Sequence[float],
    b: Sequence[float],
    *,
    metric: str = "blended",
) -> ComparisonResult:
    """Run Wilcoxon + Cliff's delta and bundle the descriptive stats."""
    if len(a) == 0 or len(b) == 0:
        raise ValueError(f"{metric}: both samples must be non-empty")
    statistic, p = wilcoxon_ranksum(a, b)
    delta, label = cliffs_delta(a, b)
    return ComparisonResult(
        metric=metric,
        n_a=len(a),
        n_b=len(b),
        mean_a=float(sum(a) / len(a)),
        mean_b=float(sum(b) / len(b)),
        std_a=_std(a),
        std_b=_std(b),
        statistic=statistic,
        p_value=p,
        cliffs_delta=delta,
        delta_label=label,
    )


def _std(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return float((sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5)
