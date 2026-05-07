"""Validation of the held-out test-set fixtures: 50 isolated functions paired
with Opus-generated reference summaries under ``data/test/``. The held-out
set is used to score generalization of GA-evolved prompts on inputs the
search never saw.

These tests run in CI under the ``data`` marker so they can be exercised
without the heavier dependencies needed by the wire-loop tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEST_FUNCTIONS_DIR = REPO_ROOT / "data" / "test" / "functions"
TEST_REFERENCES_DIR = REPO_ROOT / "data" / "test" / "references"
TEST_MANIFEST_PATH = REPO_ROOT / "data" / "test" / "manifest.json"

TRAIN_FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"

EXPECTED_FUNCTION_COUNT = 50
EXPECTED_PYTHON_COUNT = 20
EXPECTED_JS_COUNT = 15
EXPECTED_TS_COUNT = 15
ALLOWED_EXTENSIONS = {".py", ".js", ".ts"}

pytestmark = pytest.mark.data


def _function_files() -> list[Path]:
    return sorted(p for p in TEST_FUNCTIONS_DIR.iterdir() if p.suffix in ALLOWED_EXTENSIONS)


def _train_function_files() -> list[Path]:
    return sorted(p for p in TRAIN_FUNCTIONS_DIR.iterdir() if p.suffix in ALLOWED_EXTENSIONS)


def _descriptor(path: Path) -> str:
    """Strip the ``<lang>_<NNN>_`` prefix and the suffix from the stem."""
    parts = path.stem.split("_", 2)
    return parts[2] if len(parts) >= 3 else path.stem


def test_test_functions_directory_exists() -> None:
    assert TEST_FUNCTIONS_DIR.is_dir()


def test_test_references_directory_exists() -> None:
    assert TEST_REFERENCES_DIR.is_dir()


def test_test_function_count_matches_target() -> None:
    assert len(_function_files()) == EXPECTED_FUNCTION_COUNT


def test_test_function_language_split() -> None:
    files = _function_files()
    py = [p for p in files if p.suffix == ".py"]
    js = [p for p in files if p.suffix == ".js"]
    ts = [p for p in files if p.suffix == ".ts"]
    assert len(py) == EXPECTED_PYTHON_COUNT, f"expected {EXPECTED_PYTHON_COUNT} .py, got {len(py)}"
    assert len(js) == EXPECTED_JS_COUNT, f"expected {EXPECTED_JS_COUNT} .js, got {len(js)}"
    assert len(ts) == EXPECTED_TS_COUNT, f"expected {EXPECTED_TS_COUNT} .ts, got {len(ts)}"


def test_every_test_function_has_paired_reference() -> None:
    refs = {p.stem for p in TEST_REFERENCES_DIR.glob("*.txt")}
    missing = sorted({p.stem for p in _function_files()} - refs)
    assert not missing, f"functions missing references (showing up to 5): {missing[:5]}"


def test_no_orphan_test_references() -> None:
    fn_stems = {p.stem for p in _function_files()}
    orphans = sorted({p.stem for p in TEST_REFERENCES_DIR.glob("*.txt")} - fn_stems)
    assert not orphans, f"references without functions (showing up to 5): {orphans[:5]}"


def test_test_function_files_are_non_empty() -> None:
    empties = [p.name for p in _function_files() if p.stat().st_size == 0]
    assert not empties, f"empty function files: {empties}"


def test_test_reference_files_are_non_empty() -> None:
    empties = [p.name for p in TEST_REFERENCES_DIR.glob("*.txt") if p.stat().st_size == 0]
    assert not empties, f"empty reference files: {empties}"


def test_test_manifest_present_and_valid() -> None:
    assert TEST_MANIFEST_PATH.exists(), "data/test/manifest.json must exist"
    manifest = json.loads(TEST_MANIFEST_PATH.read_text())
    assert isinstance(manifest, list), "manifest.json must be a list"
    assert len(manifest) == EXPECTED_FUNCTION_COUNT
    required = {"filename", "language", "complexity_tier"}
    allowed_languages = {"python", "javascript", "typescript"}
    allowed_tiers = {"trivial", "medium", "complex"}
    for entry in manifest:
        assert required <= entry.keys(), f"manifest entry missing keys: {required - entry.keys()}"
        assert entry["language"] in allowed_languages
        assert entry["complexity_tier"] in allowed_tiers


def test_test_manifest_filenames_match_disk() -> None:
    manifest = json.loads(TEST_MANIFEST_PATH.read_text())
    manifest_names = {entry["filename"] for entry in manifest}
    disk_names = {p.name for p in _function_files()}
    assert manifest_names == disk_names, (
        f"manifest/disk mismatch: missing on disk={manifest_names - disk_names}, "
        f"missing in manifest={disk_names - manifest_names}"
    )


def test_no_descriptor_collision_with_training_set() -> None:
    train_descriptors = {_descriptor(p) for p in _train_function_files()}
    test_descriptors = {_descriptor(p) for p in _function_files()}
    overlap = sorted(train_descriptors & test_descriptors)
    assert not overlap, (
        "test-set descriptors collide with training set; pick distinct names: "
        f"{overlap[:10]}"
    )


def test_test_complexity_tier_distribution() -> None:
    """Sanity-check the tier mix matches the brief: ~15 trivial / ~25 medium / ~10 complex."""
    manifest = json.loads(TEST_MANIFEST_PATH.read_text())
    counts = {"trivial": 0, "medium": 0, "complex": 0}
    for entry in manifest:
        counts[entry["complexity_tier"]] += 1
    # Allow ±2 wobble per tier so future curators can rebalance without breaking CI.
    assert 13 <= counts["trivial"] <= 17, f"trivial count out of range: {counts['trivial']}"
    assert 23 <= counts["medium"] <= 27, f"medium count out of range: {counts['medium']}"
    assert 8 <= counts["complex"] <= 12, f"complex count out of range: {counts['complex']}"
