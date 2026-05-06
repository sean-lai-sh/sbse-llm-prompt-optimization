from __future__ import annotations
from dataclasses import asdict, dataclass, field
from pathlib import Path
import json

from src.prompt import PromptTemplate


@dataclass(frozen=True)
class GenerationLog:
    """One row per generation (GA) or P-evaluation checkpoint (RS).

    Both algorithms emit the same schema so results/<run>/generations.jsonl
    can be loaded uniformly by the analysis stage (issue #11).
    """
    generation: int
    best_blended: float
    mean_blended: float
    worst_blended: float
    # Per-metric breakdown of the best individual at this checkpoint
    best_rouge_l: float
    best_cosine_raw: float
    best_cosine_calibrated: float
    best_template: dict  # PromptTemplate.to_dict()

    @classmethod
    def from_population(cls, generation: int, scored: list[tuple["PromptTemplate", dict]]) -> "GenerationLog":
        """Build a log row from a list of (template, score_dict) pairs."""
        scored_sorted = sorted(scored, key=lambda x: x[1]["blended"], reverse=True)
        best_t, best_s = scored_sorted[0]
        blended = [s["blended"] for _, s in scored_sorted]
        return cls(
            generation=generation,
            best_blended=best_s["blended"],
            mean_blended=sum(blended) / len(blended),
            worst_blended=blended[-1],
            best_rouge_l=best_s["rouge_l"],
            best_cosine_raw=best_s["cosine_raw"],
            best_cosine_calibrated=best_s["cosine_calibrated"],
            best_template=best_t.to_dict(),
        )

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self))


def append_log(path: Path, log: GenerationLog) -> None:
    """Append one log row to a JSONL file, flushing immediately."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(log.to_jsonl() + "\n")
        f.flush()
