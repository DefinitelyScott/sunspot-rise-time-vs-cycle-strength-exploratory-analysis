#!/usr/bin/env python3
"""Reproduce every figure and number in the README.

Usage:
    python analysis.py [--output-dir outputs]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sunspot_cycles.report import format_summary, run_analysis  # noqa: E402

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def main(argv: list[str] | None = None) -> int:
    """Run the analysis and print its summary; return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    try:
        results = run_analysis(args.output_dir)
    except ValueError as exc:
        print(f"analysis failed: {exc}", file=sys.stderr)
        return 1
    print(format_summary(results))
    print(f"Figures, cycles.csv and results.json written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
