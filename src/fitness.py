"""Fitness function for the GA prompt-optimization loop (issue #7).

`score_prompt` returns the blended fitness for a candidate `PromptTemplate`
along with the per-metric breakdown the analysis stage (issue #11) needs for
ablation. The GA selects on the `blended` scalar:

    fitness = alpha * ROUGE-L + (1 - alpha) * cosine_calibrated
            - lambda_len * length_penalty
            - lambda_fmt * format_penalty

Cosine is rescaled against an empirical baseline (see `src.eval.calibrate_cosine_batch`)
so it lives on roughly the same scale as ROUGE-L and `alpha` actually means
"half lexical, half semantic" the way the brief reads.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import yaml
from rouge_score import rouge_scorer

from src.eval import (
    GenerateSummaryFn,
    _default_generate_summary,
    calibrate_cosine_batch,
    cosine_similarity_batch,
)
from src.prompt import PromptTemplate

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


@dataclass(frozen=True)
class FitnessConfig:
    alpha: float = 0.5
    cosine_baseline: float = 0.45
    lambda_len: float = 0.1
    lambda_fmt: float = 0.2
    max_prompt_tokens: int = 200

    @classmethod
    def from_yaml(cls, path: Path = DEFAULT_CONFIG_PATH) -> "FitnessConfig":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        section = raw.get("fitness", {})
        # Drop unknown keys so a future config addition doesn't crash old code.
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in section.items() if k in known})


_TOKEN_RE = re.compile(r"\w+|[^\s\w]")


def _approx_token_count(text: str) -> int:
    """Lightweight token estimate (words + punctuation marks).

    Avoids pulling in tiktoken for what is only used to gate the length
    penalty -- relative ordering is what matters, not absolute accuracy.
    """
    return len(_TOKEN_RE.findall(text))


def _format_violation_penalty(generated: str, reference: str) -> float:
    """Returns 1.0 if `generated` is degenerate, else 0.0.

    A summary is degenerate if it is empty, contains a code fence, or runs
    more than 10x the reference length (which inflates ROUGE-L recall while
    being unusable as documentation).
    """
    stripped = generated.strip()
    if not stripped:
        return 1.0
    if "```" in generated:
        return 1.0
    if len(stripped) > 10 * max(1, len(reference.strip())):
        return 1.0
    return 0.0


def _length_penalty(prompt_token_count: int, max_tokens: int) -> float:
    excess = max(0, prompt_token_count - max_tokens)
    return excess / max_tokens if max_tokens > 0 else 0.0


def score_prompt(
    template: PromptTemplate,
    functions: Sequence[Path],
    references: Sequence[Path],
    *,
    generate_summary: Optional[GenerateSummaryFn] = None,
    config: Optional[FitnessConfig] = None,
    eval_subset: Optional[int] = None,
    seed: int = 0,
) -> dict:
    """Score `template` across the (function, reference) benchmark.

    Args:
        template: candidate prompt under evaluation.
        functions: iterable of function source paths.
        references: iterable of paired reference summary paths.
        generate_summary: callable `(template, code) -> str`; defaults to
            `src.target_model.generate_summary` via the lazy resolver in
            `src.eval`. Pass explicitly for tests or alternate models.
        config: weights and thresholds. Loaded from `config.yaml` when None.
        eval_subset: when set, randomly sample this many (fn, ref) pairs for
            cheap inner-loop evaluation. The full benchmark is used for the
            final scoring of the best individual.
        seed: subsample RNG seed; same seed yields the same subset across
            generations so candidates compete on identical inputs.

    Returns:
        Dict with `blended`, `rouge_l`, `cosine_raw`, `cosine_calibrated`,
        `length_penalty`, `format_penalty`. The GA optimizes `blended`; the
        rest is preserved for ablation reporting (issue #11).
    """
    if config is None:
        config = FitnessConfig.from_yaml()
    if generate_summary is None:
        generate_summary = _default_generate_summary()

    fns = [Path(p) for p in functions]
    refs = [Path(p) for p in references]
    if len(fns) != len(refs):
        raise ValueError(
            f"functions and references must be the same length, "
            f"got {len(fns)} and {len(refs)}"
        )
    if not fns:
        raise ValueError("benchmark is empty")

    if eval_subset is not None and eval_subset < len(fns):
        rng = random.Random(seed)
        chosen = rng.sample(range(len(fns)), eval_subset)
        fns = [fns[i] for i in chosen]
        refs = [refs[i] for i in chosen]

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

    generations: list[str] = []
    ref_texts: list[str] = []
    rouge_scores: list[float] = []
    format_penalties: list[float] = []

    for fn_path, ref_path in zip(fns, refs):
        code = fn_path.read_text(encoding="utf-8")
        ref_text = ref_path.read_text(encoding="utf-8").strip()
        gen = generate_summary(template, code)

        generations.append(gen)
        ref_texts.append(ref_text)
        rouge_scores.append(float(scorer.score(ref_text, gen)["rougeL"].fmeasure))
        format_penalties.append(_format_violation_penalty(gen, ref_text))

    cosines_raw = cosine_similarity_batch(generations, ref_texts)
    cosines_cal = calibrate_cosine_batch(cosines_raw, config.cosine_baseline)

    n = len(fns)
    rouge_mean = sum(rouge_scores) / n
    cosine_raw_mean = sum(cosines_raw) / n
    cosine_cal_mean = sum(cosines_cal) / n
    fmt_pen_mean = sum(format_penalties) / n

    prompt_tokens = _approx_token_count(template.render_instructions())
    len_pen = _length_penalty(prompt_tokens, config.max_prompt_tokens)

    blended = (
        config.alpha * rouge_mean
        + (1.0 - config.alpha) * cosine_cal_mean
        - config.lambda_len * len_pen
        - config.lambda_fmt * fmt_pen_mean
    )

    return {
        "blended": float(blended),
        "rouge_l": float(rouge_mean),
        "cosine_raw": float(cosine_raw_mean),
        "cosine_calibrated": float(cosine_cal_mean),
        "length_penalty": float(len_pen),
        "format_penalty": float(fmt_pen_mean),
    }
