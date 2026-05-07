"""Evaluation utilities used inside the GA fitness function.

This module supplies the cosine-similarity term that is blended with ROUGE-L
inside the fitness function (issue #7):

    fitness = alpha * ROUGE-L + (1 - alpha) * cosine
              - lambda_len * length_penalty - lambda_fmt * format_penalty

The GA inner loop hits these helpers ~500 functions x N candidates x N
generations x N trials, so:

* the sentence-transformer model (BAAI/bge-small-en-v1.5) is loaded **once**
  via a lazy module-level cache and runs entirely as a local Hugging Face
  inference -- no network calls per encode
* the batched API encodes both lists in two `model.encode()` calls and
  computes pairwise cosine in numpy

`evaluate_prompt` is a higher-level helper used for offline reporting: it
runs the target model over the full benchmark and returns per-file +
aggregate ROUGE-L and cosine numbers. It is *not* called inside the GA inner
loop; the GA fitness path uses `cosine_similarity_batch` directly.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np

from src.prompt import PromptTemplate

# Type alias for the generation callable that callers must supply to
# evaluate_prompt. Concretely this is `src.target_model.generate_summary`
# from issue #6, but accepting it as a parameter keeps this module
# decoupled from the target-model API surface and trivially testable.
GenerateSummaryFn = Callable[[PromptTemplate, str], str]

_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Lazily-instantiated singleton. We deliberately do NOT load at import time
# because pytest collection should stay fast; the first call to an embedding
# function pays the load cost, every subsequent call reuses the same weights.
#
# The lock prevents a race when the GA's ThreadPoolExecutor calls
# cosine_similarity_batch() from many workers simultaneously on the very
# first generation: without it, multiple threads pass the `is None` check
# and start instantiating SentenceTransformer at the same time, which
# triggers PyTorch's "Cannot copy out of meta tensor" error during the
# concurrent module-to-device move. Double-checked locking ensures exactly
# one initialization; subsequent calls hit the fast path with no lock.
import threading  # noqa: E402

_model = None
_model_lock = threading.Lock()


def _get_model():
    """Return the cached sentence-transformer model, loading it on first use."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:  # re-check inside the lock
                from sentence_transformers import SentenceTransformer  # noqa: PLC0415

                _model = SentenceTransformer(_MODEL_NAME)
    return _model


def _normalize(matrix: np.ndarray) -> np.ndarray:
    """Row-normalize an embedding matrix; rows that are all zero stay zero."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return matrix / norms


def cosine_similarity_batch(generated: list[str], reference: list[str]) -> list[float]:
    """Pairwise cosine similarity between two equal-length lists of strings.

    Encodes each list in a single batched `model.encode()` call to amortize the
    forward-pass cost across the 500-file benchmark. Returns a list of floats
    in [-1.0, 1.0] (in practice [0.0, 1.0] for natural-language inputs).
    """
    if len(generated) != len(reference):
        raise ValueError(
            f"generated and reference must be the same length, "
            f"got {len(generated)} and {len(reference)}"
        )
    if not generated:
        return []

    model = _get_model()
    # convert_to_numpy keeps things light (no torch tensors leaking out)
    gen_emb = np.asarray(
        model.encode(generated, batch_size=32, show_progress_bar=False, convert_to_numpy=True),
        dtype=np.float32,
    )
    ref_emb = np.asarray(
        model.encode(reference, batch_size=32, show_progress_bar=False, convert_to_numpy=True),
        dtype=np.float32,
    )
    gen_n = _normalize(gen_emb)
    ref_n = _normalize(ref_emb)
    sims = np.einsum("ij,ij->i", gen_n, ref_n)
    # Clamp to [-1, 1] to absorb floating-point drift.
    sims = np.clip(sims, -1.0, 1.0)
    return [float(x) for x in sims]


def cosine_similarity_score(generated: str, reference: str) -> float:
    """Cosine similarity between a single (generated, reference) pair.

    Thin wrapper over the batch API so call sites that already have lists
    of texts get the amortized path automatically.
    """
    return cosine_similarity_batch([generated], [reference])[0]


def calibrate_cosine(raw: float, baseline: float) -> float:
    """Linearly rescale raw cosine to [0, 1] given an empirical baseline.

    BGE-style sentence embedders return non-trivial similarity (~0.4-0.5)
    even for unrelated short text, which would let the GA earn fitness for
    producing any plausible English regardless of relevance. Rescaling so
    the baseline maps to 0 and identical inputs map to 1 restores a
    meaningful signal that can be blended cleanly with ROUGE-L (which
    already lives on [0, 1]) under the alpha weight in config.yaml.

        calibrated = max(0, (raw - baseline) / (1 - baseline))

    The default baseline (0.45) is a starting estimate; run
    `scripts/calibrate_cosine_baseline.py` (issue forthcoming) to
    re-derive it empirically from random unmatched pairs in the
    benchmark.
    """
    if not 0.0 <= baseline < 1.0:
        raise ValueError(f"baseline must be in [0, 1), got {baseline}")
    rescaled = (raw - baseline) / (1.0 - baseline)
    return max(0.0, min(1.0, rescaled))


def calibrate_cosine_batch(raw: list[float], baseline: float) -> list[float]:
    """Vectorized calibration for the GA inner loop. See `calibrate_cosine`."""
    if not 0.0 <= baseline < 1.0:
        raise ValueError(f"baseline must be in [0, 1), got {baseline}")
    arr = (np.asarray(raw, dtype=np.float32) - baseline) / (1.0 - baseline)
    arr = np.clip(arr, 0.0, 1.0)
    return [float(x) for x in arr]


def _read_text(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _aggregate(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = statistics.fmean(values)
    # Use sample stdev when n>=2, else 0 (single point has no spread).
    std = statistics.stdev(values) if len(values) >= 2 else 0.0
    return float(mean), float(std)


def _default_generate_summary() -> GenerateSummaryFn:
    """Resolve the production target-model callable from `src.target_model`.

    Imported lazily and wrapped so callers that never invoke `evaluate_prompt`
    do not need `src.target_model` to be installed (it lands in issue #6 /
    PR #15). Raises a clear, actionable error if the module is missing.
    """
    try:
        from src.target_model import generate_summary as _gs  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover -- exercised in scripts
        raise ImportError(
            "src.target_model.generate_summary is unavailable. Either merge "
            "issue #6 (PR #15) or pass an explicit `generate_summary` "
            "callable to evaluate_prompt(...)."
        ) from exc

    def _adapter(template: PromptTemplate, code: str) -> str:
        # PR #15 exposes generate_summary(prompt: str, code: str) where
        # `prompt` is the system message (instructions only) and `code` is
        # the user message. Use render_instructions() so we do not send the
        # function source twice.
        return _gs(template.render_instructions(), code)

    return _adapter


def evaluate_prompt(
    template: PromptTemplate,
    functions: Iterable[Path],
    references: Iterable[Path],
    generate_summary: Optional[GenerateSummaryFn] = None,
    *,
    workers: int = 1,
) -> dict:
    """Run `template` over the benchmark and return per-metric breakdowns.

    For each (function, reference) pair we:
      1. read the function source from disk
      2. ask `generate_summary(template, code)` (or
         `src.target_model.generate_summary` if not supplied) for a summary
      3. score the generation against the reference with both ROUGE-L and
         cosine similarity

    Args:
        template: the prompt template under evaluation
        functions: iterable of function source files
        references: iterable of paired reference summary files
        generate_summary: optional callable `(template, code) -> str`. When
            `None`, this resolves to `src.target_model.generate_summary` from
            issue #6, raising a clear ImportError if that module is absent.
            Passing it explicitly is recommended for tests and for consumers
            who want to swap models or stub the call.
        workers: thread-pool size for parallel ``generate_summary`` calls.
            Default 1 (sequential) preserves the original API. Set higher
            (e.g. 16) for held-out eval where the model dominates wall time.
            ROUGE-L scoring and the cosine batch run after all generations
            are collected, so order is preserved regardless of workers.

    Returns:
        {
          "per_file": [{"filename": str, "rouge_l": float, "cosine": float}, ...],
          "aggregate": {"rouge_l_mean": float, "rouge_l_std": float,
                        "cosine_mean": float, "cosine_std": float},
        }
    """
    from rouge_score import rouge_scorer  # noqa: PLC0415

    if generate_summary is None:
        generate_summary = _default_generate_summary()

    func_paths = [Path(p) for p in functions]
    ref_paths = [Path(p) for p in references]
    if len(func_paths) != len(ref_paths):
        raise ValueError(
            f"functions and references must be the same length, "
            f"got {len(func_paths)} and {len(ref_paths)}"
        )

    # Pre-read every file once so the threaded section only does network IO.
    codes = [_read_text(p) for p in func_paths]
    ref_texts = [_read_text(p).strip() for p in ref_paths]
    filenames = [p.name for p in func_paths]

    def _gen_one(args: tuple[int, str]) -> tuple[int, str]:
        idx, code = args
        return idx, generate_summary(template, code)

    if workers and workers > 1 and len(codes) > 1:
        from concurrent.futures import ThreadPoolExecutor  # noqa: PLC0415

        # Use map() so order is preserved -- ROUGE-L and the cosine batch
        # below depend on generations[i] aligning with ref_texts[i].
        with ThreadPoolExecutor(max_workers=workers) as pool:
            indexed = list(pool.map(_gen_one, enumerate(codes)))
        indexed.sort(key=lambda pair: pair[0])
        generations = [g for _, g in indexed]
    else:
        generations = [generate_summary(template, code) for code in codes]

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    rouge_scores = [
        float(scorer.score(ref, gen)["rougeL"].fmeasure)
        for ref, gen in zip(ref_texts, generations)
    ]

    cosine_scores = cosine_similarity_batch(generations, ref_texts)

    per_file = [
        {"filename": name, "rouge_l": rl, "cosine": co}
        for name, rl, co in zip(filenames, rouge_scores, cosine_scores)
    ]
    rl_mean, rl_std = _aggregate(rouge_scores)
    co_mean, co_std = _aggregate(cosine_scores)
    return {
        "per_file": per_file,
        "aggregate": {
            "rouge_l_mean": rl_mean,
            "rouge_l_std": rl_std,
            "cosine_mean": co_mean,
            "cosine_std": co_std,
        },
    }
