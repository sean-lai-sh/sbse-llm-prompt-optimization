"""Tests for src/analysis.py.

Build synthetic trial directories on a tmp_path and verify the loader,
trial summarizer, and end-to-end analysis pipeline.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.analysis import (
    PER_TRIAL_METRICS,
    analyze_results_root,
    discover_trial_dirs,
    load_generation_logs,
    summarize_trials,
    trial_best,
)
from src.prompt import PromptTemplate
from src.search_log import GenerationLog


def _mk_log(gen: int, blended: float, rouge: float = 0.5, cos: float = 0.7) -> GenerationLog:
    tmpl = PromptTemplate(role="r", task="t", guard="g", format="f")
    return GenerationLog(
        generation=gen,
        best_blended=blended,
        mean_blended=blended * 0.9,
        worst_blended=blended * 0.8,
        best_rouge_l=rouge,
        best_cosine_raw=cos,
        best_cosine_calibrated=cos * 0.7,
        best_template=tmpl.to_dict(),
    )


def _write_trial(root: Path, name: str, logs: list[GenerationLog]) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    with (d / "generations.jsonl").open("w") as f:
        for log in logs:
            f.write(json.dumps(asdict(log)) + "\n")
    return d


# ---------------------------------------------------------------------------
# load_generation_logs
# ---------------------------------------------------------------------------


def test_load_generation_logs_round_trip(tmp_path: Path) -> None:
    logs = [_mk_log(0, 0.5), _mk_log(1, 0.6)]
    d = _write_trial(tmp_path, "ga_trial_000_x", logs)
    loaded = load_generation_logs(d)
    assert len(loaded) == 2
    assert loaded[0] == logs[0]
    assert loaded[1] == logs[1]


def test_load_generation_logs_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="generations.jsonl"):
        load_generation_logs(tmp_path)


def test_load_generation_logs_empty_file_raises(tmp_path: Path) -> None:
    d = tmp_path / "empty"
    d.mkdir()
    (d / "generations.jsonl").write_text("")
    with pytest.raises(ValueError, match="no rows"):
        load_generation_logs(d)


# ---------------------------------------------------------------------------
# trial_best
# ---------------------------------------------------------------------------


def test_trial_best_picks_highest_blended() -> None:
    logs = [
        _mk_log(0, 0.4, rouge=0.1, cos=0.2),
        _mk_log(1, 0.9, rouge=0.7, cos=0.8),  # winner
        _mk_log(2, 0.6, rouge=0.5, cos=0.6),
    ]
    best = trial_best(logs)
    assert best["blended"] == pytest.approx(0.9)
    assert best["rouge_l"] == pytest.approx(0.7)
    assert best["cosine_raw"] == pytest.approx(0.8)
    assert best["cosine_calibrated"] == pytest.approx(0.8 * 0.7)


def test_trial_best_rejects_empty() -> None:
    with pytest.raises(ValueError, match="no logs"):
        trial_best([])


# ---------------------------------------------------------------------------
# discover_trial_dirs
# ---------------------------------------------------------------------------


def test_discover_trial_dirs_groups_by_prefix(tmp_path: Path) -> None:
    _write_trial(tmp_path, "ga_trial_000_a", [_mk_log(0, 0.5)])
    _write_trial(tmp_path, "ga_trial_001_b", [_mk_log(0, 0.6)])
    _write_trial(tmp_path, "rs_trial_000_c", [_mk_log(0, 0.4)])
    (tmp_path / "not_a_trial_dir").mkdir()  # should be ignored
    grouped = discover_trial_dirs(tmp_path)
    assert set(grouped.keys()) == {"ga", "rs"}
    assert len(grouped["ga"]) == 2
    assert len(grouped["rs"]) == 1


def test_discover_trial_dirs_missing_root_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="results root"):
        discover_trial_dirs(tmp_path / "nope")


# ---------------------------------------------------------------------------
# summarize_trials
# ---------------------------------------------------------------------------


def test_summarize_trials_returns_per_metric_columns(tmp_path: Path) -> None:
    d1 = _write_trial(tmp_path, "ga_trial_000_x", [_mk_log(0, 0.5)])
    d2 = _write_trial(tmp_path, "ga_trial_001_y", [_mk_log(0, 0.7)])
    cols = summarize_trials([d1, d2])
    assert set(cols.keys()) == set(PER_TRIAL_METRICS)
    assert cols["blended"] == pytest.approx([0.5, 0.7])


# ---------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------


def test_analyze_results_root_full_pipeline(tmp_path: Path) -> None:
    # GA wins clearly: blended values 0.7-0.8 vs RS 0.3-0.4.
    for i in range(5):
        _write_trial(tmp_path, f"ga_trial_{i:03d}_x", [_mk_log(0, 0.7 + i * 0.02)])
        _write_trial(tmp_path, f"rs_trial_{i:03d}_x", [_mk_log(0, 0.3 + i * 0.02)])

    result = analyze_results_root(tmp_path)

    assert result["target_algorithm"] == "ga"
    assert result["baseline_algorithm"] == "rs"
    assert result["n_trials"] == {"ga": 5, "rs": 5}
    assert "blended" in result["comparisons"]

    blended = result["comparisons"]["blended"]
    # Schema uses algorithm-named keys (matches issue #11 spec).
    assert blended["ga_mean"] > blended["rs_mean"]
    assert blended["n_ga"] == 5
    assert blended["n_rs"] == 5
    assert "ga_std" in blended and "rs_std" in blended
    assert blended["cliffs_delta"] == pytest.approx(1.0)
    assert blended["delta_label"] == "large"
    assert blended["p_value"] < 0.05  # n=5 vs n=5 with full domination


def test_analyze_results_root_schema_uses_custom_algorithm_names(tmp_path: Path) -> None:
    """Field-name renaming honors the actual --target / --baseline names."""
    for i in range(3):
        _write_trial(tmp_path, f"foo_trial_{i:03d}_x", [_mk_log(0, 0.5)])
        _write_trial(tmp_path, f"bar_trial_{i:03d}_x", [_mk_log(0, 0.4)])

    result = analyze_results_root(tmp_path, target_algorithm="foo", baseline_algorithm="bar")
    blended = result["comparisons"]["blended"]
    assert "foo_mean" in blended and "bar_mean" in blended
    assert "foo_std" in blended and "bar_std" in blended
    assert "n_foo" in blended and "n_bar" in blended


def test_analyze_results_root_missing_algorithm_raises(tmp_path: Path) -> None:
    _write_trial(tmp_path, "ga_trial_000_x", [_mk_log(0, 0.5)])
    with pytest.raises(ValueError, match="rs"):
        analyze_results_root(tmp_path)


def test_analyze_results_root_per_trial_values_exposed(tmp_path: Path) -> None:
    for i in range(3):
        _write_trial(tmp_path, f"ga_trial_{i:03d}_x", [_mk_log(0, 0.5 + i * 0.1)])
        _write_trial(tmp_path, f"rs_trial_{i:03d}_x", [_mk_log(0, 0.3 + i * 0.1)])
    result = analyze_results_root(tmp_path)
    assert result["per_trial_values"]["ga"]["blended"] == pytest.approx([0.5, 0.6, 0.7])
    assert result["per_trial_values"]["rs"]["blended"] == pytest.approx([0.3, 0.4, 0.5])
