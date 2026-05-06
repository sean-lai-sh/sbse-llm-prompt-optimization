#!/usr/bin/env python3
"""Run the Genetic Algorithm for prompt optimization.

Usage:
    python scripts/run_ga.py                        # standard GA run
    python scripts/run_ga.py --use-improver         # GA + NIM-guided directed mutation
    python scripts/run_ga.py --config path/to/config.yaml
    python scripts/run_ga.py --dry-run              # validate config, no API calls
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_config(config_path: Path) -> dict:
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("ERROR: PyYAML is required. Run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    with config_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def run_ga(config: dict, use_improver: bool, dry_run: bool) -> None:
    """Placeholder GA loop — wired to accept the improver when --use-improver is set."""
    ga_cfg = config.get("ga", {})
    imp_cfg = config.get("improver", {})

    print("GA configuration:")
    for key, val in ga_cfg.items():
        print(f"  {key}: {val}")

    if use_improver:
        print("\nNIM improver enabled:")
        for key, val in imp_cfg.items():
            print(f"  {key}: {val}")

    if dry_run:
        print("\nDry run — exiting before any API calls.")
        return

    if use_improver:
        from src.improver import improve_prompts  # noqa: PLC0415

    print("\nGA loop not yet fully implemented (pending issues #5 and #8).")
    print("Improver module is ready and will be wired in when the GA is complete.")

    if use_improver:
        print("\nImprover configuration preview (no API call is being made):")
        example_prompts = [
            "Summarize the function in 2-4 sentences.",
            "You are a senior engineer. Describe what this function does.",
        ]
        print(f"  Planned improve_prompts(top_k={imp_cfg.get('top_k', 3)}, "
              f"n={imp_cfg.get('n_variants', 3)}, model={imp_cfg.get('model')!r})")
        print(f"  Example prompt count: {len(example_prompts)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the GA prompt optimizer."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "config.yaml",
        help="Path to config.yaml (default: repo root config.yaml)",
    )
    parser.add_argument(
        "--use-improver",
        action="store_true",
        help="Enable NIM-guided directed mutation after each selection step.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and print plan without making API calls.",
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"ERROR: config file not found: {args.config}", file=sys.stderr)
        return 1

    config = load_config(args.config)
    run_ga(config, use_improver=args.use_improver, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
