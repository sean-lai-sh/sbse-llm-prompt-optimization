"""Core Genetic Algorithm for prompt optimization (issue #8).

The GA evolves a population of :class:`PromptTemplate` individuals using
tournament selection, single-/two-field crossover, per-field mutation drawn
from the component bank, and elitism. Each generation is scored in parallel
via a thread pool because :func:`src.fitness.score_prompt` is dominated by
target-model latency, not CPU.

Determinism: every random choice flows through a single :class:`random.Random`
seeded by the ``seed`` kwarg of :func:`run_ga`. Identical seed + identical
``score_fn`` produce identical logs and identical winners.

Coordination with issue #9 (Random Search): both algorithms emit the shared
:class:`src.search_log.GenerationLog` schema so the analysis stage (issue #11)
can load ``generations.jsonl`` uniformly without branching on algorithm.
"""

from __future__ import annotations

import json
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Sequence

from src.fitness import score_prompt as _default_score_prompt
from src.prompt import COMPONENT_FIELDS, PromptTemplate, load_component_bank
from src.search_log import GenerationLog, append_log

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"
DEFAULT_REFERENCES_DIR = REPO_ROOT / "data" / "references"
DEFAULT_RESULTS_DIR = REPO_ROOT / "results"

ScoreFn = Callable[..., dict]


# ---------------------------------------------------------------------------
# Genetic operators (exposed for direct unit testing)
# ---------------------------------------------------------------------------


def random_template(bank: dict[str, list[str]], rng: random.Random) -> PromptTemplate:
    """Sample one component per field uniformly at random from the bank."""
    return PromptTemplate(**{f: rng.choice(bank[f]) for f in COMPONENT_FIELDS})


def crossover(
    parent_a: PromptTemplate,
    parent_b: PromptTemplate,
    rng: random.Random,
) -> PromptTemplate:
    """Swap a random subset of 1-2 component fields between two parents.

    Returns a new ``PromptTemplate`` whose every field came from either
    ``parent_a`` or ``parent_b``. The base parent is ``parent_a``; the
    selected swap fields are taken from ``parent_b``.
    """
    n_swap = rng.randint(1, 2)
    swap_fields = rng.sample(COMPONENT_FIELDS, n_swap)
    values = {f: getattr(parent_a, f) for f in COMPONENT_FIELDS}
    for f in swap_fields:
        values[f] = getattr(parent_b, f)
    return PromptTemplate(**values)


def mutate(
    template: PromptTemplate,
    bank: dict[str, list[str]],
    rng: random.Random,
    p_mut: float,
) -> PromptTemplate:
    """Per-field mutation: with probability ``p_mut`` replace the component.

    The replacement is drawn from the bank and is guaranteed to differ from
    the current value when the bank holds more than one alternative.
    """
    values = {f: getattr(template, f) for f in COMPONENT_FIELDS}
    for f in COMPONENT_FIELDS:
        if rng.random() >= p_mut:
            continue
        choices = bank[f]
        current = values[f]
        if len(choices) > 1:
            alternatives = [c for c in choices if c != current]
            values[f] = rng.choice(alternatives)
        else:
            values[f] = choices[0]
    return PromptTemplate(**values)


def tournament_select(
    population: list[PromptTemplate],
    scores: list[float],
    k: int,
    rng: random.Random,
) -> PromptTemplate:
    """k-tournament: sample ``k`` individuals with replacement, return the best.

    Ties are broken by the first occurrence (stable ``max``).
    """
    if not population:
        raise ValueError("tournament_select called on empty population")
    if k < 1:
        raise ValueError(f"tournament_k must be >= 1, got {k}")
    indices = [rng.randrange(len(population)) for _ in range(k)]
    best_idx = max(indices, key=lambda i: scores[i])
    return population[best_idx]


# ---------------------------------------------------------------------------
# Benchmark plumbing
# ---------------------------------------------------------------------------


def _default_benchmark(
    functions_dir: Path = DEFAULT_FUNCTIONS_DIR,
    references_dir: Path = DEFAULT_REFERENCES_DIR,
) -> tuple[list[Path], list[Path]]:
    """Pair every function file to its reference by stem.

    Mirrors the strict pairing contract used by ``scripts/evaluate_best.py``:
    any unpaired file raises so silent benchmark drift can't infect a run.
    """
    SUPPORTED_EXT = {".py", ".js", ".ts"}
    functions = sorted(
        p for p in functions_dir.iterdir()
        if p.is_file() and p.suffix in SUPPORTED_EXT
    )
    refs_by_stem = {p.stem: p for p in references_dir.iterdir() if p.is_file()}

    fn_stems = {p.stem for p in functions}
    missing_refs = sorted(fn_stems - refs_by_stem.keys())
    orphan_refs = sorted(refs_by_stem.keys() - fn_stems)

    if missing_refs or orphan_refs:
        details = []
        if missing_refs:
            preview = ", ".join(missing_refs[:5])
            suffix = "..." if len(missing_refs) > 5 else ""
            details.append(
                f"{len(missing_refs)} function(s) missing references: {preview}{suffix}"
            )
        if orphan_refs:
            preview = ", ".join(orphan_refs[:5])
            suffix = "..." if len(orphan_refs) > 5 else ""
            details.append(
                f"{len(orphan_refs)} reference(s) without functions: {preview}{suffix}"
            )
        raise ValueError(
            "benchmark pairing is incomplete; cannot run GA. "
            + " | ".join(details)
        )

    paired_fn = list(functions)
    paired_ref = [refs_by_stem[fn.stem] for fn in functions]
    return paired_fn, paired_ref


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def _evaluate_population(
    population: list[PromptTemplate],
    score_fn: ScoreFn,
    functions: Sequence[Path],
    references: Sequence[Path],
    *,
    generate_summary,
    eval_subset: Optional[int],
    seed: int,
    workers: int,
) -> list[dict]:
    """Run ``score_fn`` over the population in parallel and return one dict per individual."""
    def _eval(template: PromptTemplate) -> dict:
        return score_fn(
            template,
            functions,
            references,
            generate_summary=generate_summary,
            eval_subset=eval_subset,
            seed=seed,
        )

    if workers <= 1 or len(population) <= 1:
        return [_eval(t) for t in population]

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_eval, population))


def run_ga(
    config: dict,
    *,
    score_fn: ScoreFn = _default_score_prompt,
    generate_summary=None,
    functions: Optional[Sequence[Path]] = None,
    references: Optional[Sequence[Path]] = None,
    output_dir: Optional[Path] = None,
    seed: int = 0,
    bank: Optional[dict[str, list[str]]] = None,
) -> tuple[PromptTemplate, list[GenerationLog]]:
    """Evolve a population of prompt templates with a tournament-elitism GA.

    Args:
        config: parsed ``config.yaml`` dict. Reads ``config["ga"]`` for
            ``population_size``, ``generations``, ``elite_count``,
            ``crossover_rate``, ``mutation_rate``, ``tournament_k`` and the
            optional ``workers`` (default 8). Reads
            ``config["evaluation"]["eval_subset"]`` for cheap inner-loop
            evaluation; pass ``None`` for the full benchmark.
        score_fn: pluggable fitness function with the same signature as
            :func:`src.fitness.score_prompt`. Tests inject a deterministic
            mock; production uses the real blended fitness.
        generate_summary: forwarded to ``score_fn`` so callers can inject a
            mock target model. Default ``None`` resolves to the NIM client
            inside the fitness function.
        functions / references: paired benchmark paths. Default to the full
            500-file benchmark via :func:`_default_benchmark`.
        output_dir: directory for ``generations.jsonl`` and ``best.json``.
            Default ``results/ga_run_<UTC_timestamp>/``.
        seed: master RNG seed; the same seed yields identical logs and the
            identical best individual.
        bank: component bank override (tests pass a tiny bank). Default
            loads from ``data/component_bank.json``.

    Returns:
        ``(best_template, logs)`` where ``best_template`` is the highest
        ``blended`` individual seen across the entire run (not just the last
        generation) and ``logs`` has one entry per generation.
    """
    ga_cfg = config.get("ga", {}) or {}
    eval_cfg = config.get("evaluation", {}) or {}

    population_size = int(ga_cfg.get("population_size", 20))
    generations_n = int(ga_cfg.get("generations", 30))
    elite_count = int(ga_cfg.get("elite_count", 2))
    crossover_rate = float(ga_cfg.get("crossover_rate", 0.7))
    mutation_rate = float(ga_cfg.get("mutation_rate", 0.3))
    tournament_k = int(ga_cfg.get("tournament_k", 3))
    workers = int(ga_cfg.get("workers", min(population_size, 8)))
    eval_subset = eval_cfg.get("eval_subset")
    if eval_subset is not None:
        eval_subset = int(eval_subset)

    if population_size < 1:
        raise ValueError(f"population_size must be >= 1, got {population_size}")
    if generations_n < 1:
        raise ValueError(f"generations must be >= 1, got {generations_n}")
    if elite_count < 0 or elite_count > population_size:
        raise ValueError(
            f"elite_count must be in [0, population_size]; got {elite_count}"
        )

    if bank is None:
        bank = load_component_bank()
    if functions is None or references is None:
        functions, references = _default_benchmark()

    if output_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = DEFAULT_RESULTS_DIR / f"ga_run_{timestamp}"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "generations.jsonl"
    best_path = output_dir / "best.json"

    rng = random.Random(seed)

    population: list[PromptTemplate] = [
        random_template(bank, rng) for _ in range(population_size)
    ]

    logs: list[GenerationLog] = []
    best_overall: tuple[Optional[PromptTemplate], Optional[dict]] = (None, None)

    for gen in range(generations_n):
        scores = _evaluate_population(
            population,
            score_fn,
            functions,
            references,
            generate_summary=generate_summary,
            eval_subset=eval_subset,
            seed=seed,
            workers=workers,
        )
        scored = list(zip(population, scores))

        log = GenerationLog.from_population(gen, scored)
        logs.append(log)
        append_log(log_path, log)

        # Track the all-time best so a single great individual lost to a
        # mutation in a later generation isn't forgotten.
        gen_best_t, gen_best_s = max(scored, key=lambda x: x[1]["blended"])
        if best_overall[1] is None or gen_best_s["blended"] > best_overall[1]["blended"]:
            best_overall = (gen_best_t, gen_best_s)

        if gen == generations_n - 1:
            break

        # Elitism: top-E preserved unchanged into the next population.
        ranked = sorted(scored, key=lambda x: x[1]["blended"], reverse=True)
        elites = [t for t, _ in ranked[:elite_count]]

        blended_scores = [s["blended"] for s in scores]

        next_pop: list[PromptTemplate] = list(elites)
        while len(next_pop) < population_size:
            parent_a = tournament_select(population, blended_scores, tournament_k, rng)
            if rng.random() < crossover_rate:
                parent_b = tournament_select(population, blended_scores, tournament_k, rng)
                child = crossover(parent_a, parent_b, rng)
            else:
                child = parent_a
            child = mutate(child, bank, rng, mutation_rate)
            next_pop.append(child)

        population = next_pop[:population_size]

    assert best_overall[0] is not None  # generations_n >= 1 guaranteed
    best_template = best_overall[0]
    best_path.write_text(json.dumps(best_template.to_dict(), indent=2), encoding="utf-8")

    return best_template, logs
