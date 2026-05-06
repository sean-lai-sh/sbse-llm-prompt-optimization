"""Validation of the on-disk data fixtures: 500 isolated functions paired with
Opus-generated reference summaries, plus the component bank used by the GA.

These tests run in CI under the `data` marker so they can be exercised without
the heavier dependencies needed by the wire-loop tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"
REFERENCES_DIR = REPO_ROOT / "data" / "references"
COMPONENT_BANK_PATH = REPO_ROOT / "data" / "component_bank.json"

EXPECTED_FUNCTION_COUNT = 500
ALLOWED_EXTENSIONS = {".py", ".js", ".ts"}

pytestmark = pytest.mark.data


def _function_files() -> list[Path]:
    return sorted(p for p in FUNCTIONS_DIR.iterdir() if p.suffix in ALLOWED_EXTENSIONS)


def test_functions_directory_exists() -> None:
    assert FUNCTIONS_DIR.is_dir()


def test_references_directory_exists() -> None:
    assert REFERENCES_DIR.is_dir()


def test_function_count_matches_target() -> None:
    assert len(_function_files()) == EXPECTED_FUNCTION_COUNT


def test_every_function_has_paired_reference() -> None:
    refs = {p.stem for p in REFERENCES_DIR.glob("*.txt")}
    missing = sorted({p.stem for p in _function_files()} - refs)
    assert not missing, f"functions missing references (showing up to 5): {missing[:5]}"


def test_no_orphan_references() -> None:
    fn_stems = {p.stem for p in _function_files()}
    orphans = sorted({p.stem for p in REFERENCES_DIR.glob("*.txt")} - fn_stems)
    assert not orphans, f"references without functions (showing up to 5): {orphans[:5]}"


def test_function_files_are_non_empty() -> None:
    empties = [p.name for p in _function_files() if p.stat().st_size == 0]
    assert not empties, f"empty function files: {empties}"


def test_reference_files_are_non_empty() -> None:
    empties = [p.name for p in REFERENCES_DIR.glob("*.txt") if p.stat().st_size == 0]
    assert not empties, f"empty reference files: {empties}"


def test_manifest_present_and_valid() -> None:
    manifest_path = FUNCTIONS_DIR / "manifest.json"
    if not manifest_path.exists():
        pytest.skip("manifest.json not present")
    manifest = json.loads(manifest_path.read_text())
    assert isinstance(manifest, list), "manifest.json must be a list"
    required = {"filename", "language", "complexity_tier"}
    for entry in manifest:
        assert required <= entry.keys(), f"manifest entry missing keys: {required - entry.keys()}"


def test_component_bank_is_valid_json() -> None:
    bank = json.loads(COMPONENT_BANK_PATH.read_text())
    for field in ("role", "task", "guard", "format"):
        assert field in bank, f"component bank missing field: {field}"
        assert isinstance(bank[field], list)
        assert len(bank[field]) >= 10, f"{field} has fewer than 10 entries"
