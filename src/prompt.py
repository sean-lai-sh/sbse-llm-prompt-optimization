"""Prompt template data structure.

A PromptTemplate is the gene the GA operates on — four discrete components
that are assembled into the full prompt sent to the target model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class PromptTemplate:
    role: str = ""
    task: str = ""
    guard: str = ""
    format: str = ""

    # ------------------------------------------------------------------
    # Assembly
    # ------------------------------------------------------------------

    def render(self, code: str) -> str:
        """Assemble the four components into a complete prompt for the target model."""
        parts = [p for p in [self.role, self.task, self.guard, self.format] if p.strip()]
        parts.append(f"\n{code}")
        return "\n".join(parts)

    def render_compact(self) -> str:
        """One-line representation for display (no code injection)."""
        return " | ".join(p for p in [self.role, self.task, self.guard, self.format] if p.strip())

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "task": self.task, "guard": self.guard, "format": self.format}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptTemplate":
        return cls(
            role=data.get("role", ""),
            task=data.get("task", ""),
            guard=data.get("guard", ""),
            format=data.get("format", ""),
        )

    @classmethod
    def from_raw(cls, raw: str) -> "PromptTemplate":
        """Parse a raw string into a PromptTemplate.

        Tries JSON first (keys: role/task/guard/format); falls back to
        treating the whole string as the task field.
        """
        raw = raw.strip()
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return cls.from_dict(data)
        except (json.JSONDecodeError, ValueError):
            pass
        return cls(task=raw)
