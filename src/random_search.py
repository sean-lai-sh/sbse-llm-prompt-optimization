"""Random Search baseline for the GA prompt-optimization loop (issue #9).

Random Search (RS) is the statistical control baseline that proves the GA's
gains aren't just chance exploration. It uses the *same* total evaluation
budget as the GA (P x G fitness evaluations) and emits the *same*
`GenerationLog` schema so the analysis stage (issue #11) can compare them
with Wilcoxon + Cliff's delta.

RS has no notion of generations natively, so the P*G samples are bucketed
into G groups of P. The log for checkpoint g summarizes the g-th group of P
samples (best/mean/worst within that bucket). This makes the per-checkpoint
comparison fair: GA's generation g had P evaluations, RS's checkpoint g had
P samples too.
"""

from __future__ import annotations

import json
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Sequence

import yaml

from src.eval import GenerateSummaryFn, _default_generate_summary
from src.fitness import FitnessConfig, score_prompt
from src.prompt import (
    COMPONENT_FIELDS,
    PromptTemplate,
    load_component_bank,
)
from src.search_log import GenerationLog, append_log

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FUNCTIONS_DIR = REPO_ROOT / "data" / "functions"
DEFAULT_REFERENCES_DIR = REPO_ROOT / "data" / "references"
DEFAULT_RESULTS_DIR = REPO_ROOT / "results"
DEFAULT_CONFIG_PATH = REPO_ROOT / "config.yaml"


def random_template(bank: dict[str, list[str]], rng: random.Random) -> PromptTemplate:
    """Sample a uniformly random PromptTemplate from the component bank.

    Each of the four component fields is drawn independently and uniformly
    from its corresponding bank list using ``rng`` so callers can make the
    sampling reproducible.
    """
    return PromptTemplate(**{field: rng.choice(bank[field]) for field in COMPONENT_FIELDS})


def _default_benchmark(
    functions_dir: Path = DEFAULT_FUNCTIONS_DIR,
    references_dir: Path = DEFAULT_REFERENCES_DIR,
) -> tuple[list[Path], list[Path]]:
    """Pair every function file with its same-stem reference file.

    Fails loud if any function lacks a matching reference (or vice-versa) so
    a missing data file can't silently shrink the benchmark.
    """
    fn_paths = sorted(functions_dir.glob("*"))
    fn_paths = [p for p in fn_paths if p.is_file()]
    ref_by_stem = {p.stem: p for p in references_dir.glob("*") if p.is_file()}

    fns: list[Path] = []
    refs: list[Path] = []
    missing: list[str] = []
    for fn in fn_paths:
        ref = ref_by_stem.get(fn.stem)
        if ref is None:
            missing.append(fn.name)
            continue
        fns.append(fn)
        refs.append(ref)

    if missing:
        raise ValueError(
            f"benchmark pairing failed: {len(missing)} function(s) without a "
            f"matching reference: {missing[:5]}{'...' if len(missing) > 5 else ''}"
        )
    if not fns:
        raise ValueError(
            f"no benchmark pairs found under {functions_dir} / {references_dir}"
        )
    return fns, refs


def _load_config(config: dict | None) -> dict:
    if config is not None:
        return config
    raw = yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(
            f"{DEFAULT_CONFIG_PATH}: expected a top-level mapping, got {type(raw).__name__}"
        )
    return raw


def run_rs(
    config: dict | None = None,
    *,
    generate_summary: Optional[GenerateSummaryFn] = None,
    functions: Optional[Sequence[Path]] = None,
    references: Optional[Sequence[Path]] = None,
    output_dir: Optional[Path] = None,
    seed: int = 0,
    score_fn: Optional[Callable] = None,
    workers: int = 8,
) -> tuple[PromptTemplate, list[GenerationLog]]:
    """Run Random Search with the same total budget as the GA.

    Args:
        config: parsed config dict. When None, loads ``config.yaml`` from the
            repo root. Must contain ``ga.population_size`` and
            ``ga.generations``; ``evaluation.eval_subset`` is honored if set.
        generate_summary: callable forwarded to the fitness function;
            defaults to the OpenRouter-backed implementation in ``src.target_model``.
        functions: ordered function paths. Defaults to the full benchmark.
        references: ordered reference paths paired by stem with ``functions``.
        output_dir: directory for ``generations.jsonl`` and ``best.json``.
            Defaults to ``results/rs_run_<UTC_timestamp>/``.
        seed: RNG seed for template sampling. Same seed -> identical run.
        score_fn: fitness callable matching ``score_prompt``'s signature.
            Defaults to ``score_prompt``; injected for tests.
        workers: thread pool size for parallel fitness evaluation.

    Returns:
        ``(best_template, logs)`` where ``logs`` has length ``G``.
    """
    cfg = _load_config(config)

    ga_cfg = cfg.get("ga") or {}
    try:
        population_size = int(ga_cfg["population_size"])
        generations = int(ga_cfg["generations"])
    except KeyError as exc:
        raise ValueError(f"config missing required ga.{exc.args[0]}") from exc
    if population_size < 1 or generations < 1:
        raise ValueError(
            f"ga.population_size and ga.generations must be >= 1, "
            f"got {population_size} and {generations}"
        )

    eval_cfg = cfg.get("evaluation") or {}
    eval_subset = eval_cfg.get("eval_subset")

    if score_fn is None:
        score_fn = score_prompt
    if generate_summary is None:
        # Lazy: only resolve when we actually need the real backend.
        generate_summary = _default_generate_summary()

    if functions is None or references is None:
        if functions is not None or references is not None:
            raise ValueError(
                "functions and references must both be provided or both be None"
            )
        functions, references = _default_benchmark()
    if len(functions) != len(references):
        raise ValueError(
            f"functions and references must be the same length, "
            f"got {len(functions)} and {len(references)}"
        )

    if output_dir is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = DEFAULT_RESULTS_DIR / f"rs_run_{ts}"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = output_dir / "generations.jsonl"
    best_path = output_dir / "best.json"

    bank = load_component_bank()
    rng = random.Random(seed)

    # Pre-sample all P*G templates up front so the order is fully deterministic
    # under `seed` regardless of thread scheduling.
    total = population_size * generations
    all_templates = [random_template(bank, rng) for _ in range(total)]

    # Cache the loaded fitness config once; passing it in keeps `score_prompt`
    # from re-reading config.yaml on every call.
    fitness_config = FitnessConfig.from_yaml() if score_fn is score_prompt else None

    def _evaluate(template: PromptTemplate) -> tuple[PromptTemplate, dict]:
        kwargs = {
            "generate_summary": generate_summary,
            "eval_subset": eval_subset,
            "seed": seed,
        }
        if fitness_config is not None:
            kwargs["config"] = fitness_config
        scores = score_fn(template, functions, references, **kwargs)
        return template, scores

    logs: list[GenerationLog] = []
    best_seen: tuple[PromptTemplate, dict] | None = None

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for g in range(generations):
            bucket = all_templates[g * population_size : (g + 1) * population_size]
            scored = list(pool.map(_evaluate, bucket))

            log = GenerationLog.from_population(g, scored)
            append_log(log_path, log)
            logs.append(log)

            for template, scores in scored:
                if best_seen is None or scores["blended"] > best_seen[1]["blended"]:
                    best_seen = (template, scores)

    assert best_seen is not None  # generations >= 1 guarantees at least one bucket

    best_path.write_text(
        json.dumps(best_seen[0].to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    return best_seen[0], logs
