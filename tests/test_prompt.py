import json
from pathlib import Path

import pytest

from src.prompt import (
    COMPONENT_FIELDS,
    DEFAULT_BANK_PATH,
    PromptTemplate,
    load_component_bank,
)


@pytest.fixture
def sample_template() -> PromptTemplate:
    return PromptTemplate(
        role="You are a senior software engineer.",
        task="Summarize the following function in 2-4 sentences.",
        guard="Do not include implementation details.",
        format="Respond in plain prose.",
    )


def test_render_includes_all_components(sample_template: PromptTemplate) -> None:
    rendered = sample_template.render("def foo(): return 1")
    for field in COMPONENT_FIELDS:
        assert getattr(sample_template, field) in rendered


def test_render_includes_code(sample_template: PromptTemplate) -> None:
    code = "def add(a, b):\n    return a + b"
    rendered = sample_template.render(code)
    assert code in rendered


def test_render_preserves_component_order(sample_template: PromptTemplate) -> None:
    rendered = sample_template.render("def foo(): pass")
    positions = [rendered.index(getattr(sample_template, f)) for f in COMPONENT_FIELDS]
    assert positions == sorted(positions)


def test_to_dict_roundtrip(sample_template: PromptTemplate) -> None:
    restored = PromptTemplate.from_dict(sample_template.to_dict())
    assert restored == sample_template


def test_to_dict_serialises_to_json(sample_template: PromptTemplate, tmp_path: Path) -> None:
    payload = sample_template.to_dict()
    target = tmp_path / "template.json"
    target.write_text(json.dumps(payload))
    restored = PromptTemplate.from_dict(json.loads(target.read_text()))
    assert restored == sample_template


def test_from_dict_rejects_missing_fields() -> None:
    with pytest.raises(ValueError, match="missing fields"):
        PromptTemplate.from_dict({"role": "r", "task": "t", "guard": "g"})


def test_template_is_hashable_and_immutable(sample_template: PromptTemplate) -> None:
    assert {sample_template} == {sample_template}
    with pytest.raises(Exception):
        sample_template.role = "mutated"  # type: ignore[misc]


def test_component_bank_has_required_fields() -> None:
    bank = load_component_bank()
    assert set(bank.keys()) >= set(COMPONENT_FIELDS)


def test_component_bank_has_at_least_ten_entries_per_field() -> None:
    bank = load_component_bank()
    for field in COMPONENT_FIELDS:
        assert len(bank[field]) >= 10, f"{field} has fewer than 10 alternatives"


def test_component_bank_entries_are_unique_per_field() -> None:
    bank = load_component_bank()
    for field in COMPONENT_FIELDS:
        entries = bank[field]
        assert len(entries) == len(set(entries)), f"{field} has duplicate entries"


def test_default_bank_path_exists() -> None:
    assert DEFAULT_BANK_PATH.exists()
