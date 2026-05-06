"""Prompt representation: a `PromptTemplate` is the GA's gene, an ordered set
of four discrete components (role, task, guard, format) that are assembled
into the final prompt sent to the target model. Crossover and mutation in the
GA work at the component level, never on raw strings.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_BANK_PATH = Path(__file__).resolve().parent.parent / "data" / "component_bank.json"

COMPONENT_FIELDS: tuple[str, ...] = ("role", "task", "guard", "format")


@dataclass(frozen=True)
class PromptTemplate:
    role: str
    task: str
    guard: str
    format: str

    def render(self, code: str) -> str:
        return (
            f"{self.role}\n\n"
            f"{self.task}\n\n"
            f"{self.guard}\n\n"
            f"{self.format}\n\n"
            f"Function:\n{code}"
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "PromptTemplate":
        missing = [f for f in COMPONENT_FIELDS if f not in data]
        if missing:
            raise ValueError(f"PromptTemplate.from_dict missing fields: {missing}")
        return cls(**{f: data[f] for f in COMPONENT_FIELDS})


def load_component_bank(path: Path | str = DEFAULT_BANK_PATH) -> dict[str, list[str]]:
    bank = json.loads(Path(path).read_text())
    for field in COMPONENT_FIELDS:
        if field not in bank or not isinstance(bank[field], list) or not bank[field]:
            raise ValueError(f"Component bank missing or empty field: {field}")
    return bank
