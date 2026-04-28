#!/usr/bin/env python3
"""Run the genetic algorithm to optimise prompt templates.

The full GA implementation lives in src/ga.py (issue #8). This script
is the entry-point that wires together config, data paths, and the
optional NIM improver, then delegates to the GA loop.

Usage:
    python scripts/run_ga.py
    python scripts/run_ga.py --use-improver
    python scripts/run_ga.py --config path/to/config.yaml --use-improver
    python scripts/run_ga.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_config(path: Path) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the GA prompt optimisation experiment."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "config.yaml",
        help="Path to config.yaml (default: repo root config.yaml).",
    )
    parser.add_argument(
        "--use-improver",
        action="store_true",
        help=(
            "Enable the NIM-guided directed mutation step. "
            "Requires NVIDIA_API_KEY to be set. "
            "Toggle off for ablation (GA-only baseline)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved configuration and exit without running the GA.",
    )
    args = parser.parse_args()

    load_dotenv()

    if not args.config.exists():
        print(f"ERROR: config file not found: {args.config}", file=sys.stderr)
        return 1

    config = load_config(args.config)
    config["use_improver"] = args.use_improver

    if args.dry_run:
        import json
        print("Resolved configuration:")
        print(json.dumps(config, indent=2, default=str))
        print(f"\n--use-improver: {args.use_improver}")
        return 0

    if args.use_improver:
        if not os.environ.get("NVIDIA_API_KEY"):
            print(
                "ERROR: --use-improver requires NVIDIA_API_KEY to be set.",
                file=sys.stderr,
            )
            return 1
        from src.improver import create_improver_from_config
        improver = create_improver_from_config(config)
        print(f"NIM improver enabled (model: {improver.model})")
    else:
        improver = None
        print("NIM improver disabled (GA-only mode).")

    # GA loop will be implemented in issue #8 (src/ga.py).
    # Placeholder: import and call run_ga once it exists.
    try:
        from src.ga import run_ga  # noqa: F401
        best_template, logs = run_ga(config, improver=improver)
        print(f"Best template: {best_template.render_compact()}")
        print(f"Best fitness:  {logs[-1].best_fitness:.4f}")
    except ImportError:
        print(
            "src/ga.py not yet implemented (see issue #8). "
            "Re-run after completing that issue.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
