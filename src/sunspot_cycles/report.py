"""Run the full analysis, write figures and results, and format a text summary."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from sunspot_cycles import cycles as cyc
from sunspot_cycles import figures, stats
from sunspot_cycles.data import load_sunspots

PRIMARY_WINDOW = 3
SENSITIVITY_WINDOWS = (1, 3, 5)
NUMBERED_CYCLES_START = 1755
"""Cycle 1 begins in 1755; earlier cycles rest on sparser observations."""


def sensitivity_table(series: pd.Series) -> pd.DataFrame:
    """Rise-time vs amplitude correlation under every window and cycle selection."""
    rows = []
    for window in SENSITIVITY_WINDOWS:
        measured = cyc.measure_cycles(series, window)
        for label, subset in (
            ("all cycles", measured),
            (f"from {NUMBERED_CYCLES_START}", measured[measured["start"] >= NUMBERED_CYCLES_START]),
        ):
            result = stats.rank_correlation(
                subset["amplitude"].to_numpy(), subset["rise_years"].to_numpy()
            )
            rows.append({"label": f"window {window}, {label}", **asdict(result)})
    return pd.DataFrame(rows)


def run_analysis(output_dir: Path) -> dict[str, Any]:
    """Reproduce every number and figure in the README.

    Args:
        output_dir: Directory for PNGs, ``cycles.csv`` and ``results.json``.

    Returns:
        The results dictionary that is also written to ``results.json``.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    series = load_sunspots()
    cycles = cyc.measure_cycles(series, PRIMARY_WINDOW)
    if len(cycles) < 10:
        raise ValueError(f"only {len(cycles)} cycles detected; segmentation failed")

    amp = cycles["amplitude"].to_numpy()
    outcomes = {
        name: stats.rank_correlation(amp, cycles[column].to_numpy())
        for name, column in (
            ("rise_years", "rise_years"),
            ("fall_years", "fall_years"),
            ("length_years", "length_years"),
        )
    }
    loo_low, loo_high = stats.leave_one_out_range(amp, cycles["rise_years"].to_numpy())
    sensitivity = sensitivity_table(series)

    results: dict[str, Any] = {
        "n_cycles": len(cycles),
        "first_start": int(cycles["start"].iloc[0]),
        "last_end": int(cycles["end"].iloc[-1]),
        "mean_rise_years": round(float(cycles["rise_years"].mean()), 2),
        "mean_fall_years": round(float(cycles["fall_years"].mean()), 2),
        "mean_length_years": round(float(cycles["length_years"].mean()), 2),
        "rise_shorter_than_fall": int((cycles["rise_years"] < cycles["fall_years"]).sum()),
        "correlation_with_amplitude": {k: _round(asdict(v)) for k, v in outcomes.items()},
        "rise_leave_one_out_rho": [round(loo_low, 3), round(loo_high, 3)],
        "sensitivity": [_round(r) for r in sensitivity.to_dict("records")],
    }

    cycles.to_csv(output_dir / "cycles.csv", index=False)
    (output_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    figures.plot_series(series, cycles, output_dir / "fig1_cycles.png")
    figures.plot_rise_vs_amplitude(
        cycles, outcomes["rise_years"].rho, output_dir / "fig2_rise_vs_amplitude.png"
    )
    figures.plot_sensitivity(sensitivity, output_dir / "fig3_sensitivity.png")
    return results


def _round(record: dict[str, Any]) -> dict[str, Any]:
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in record.items()}


def _fmt_p(p: float) -> str:
    """Format a permutation p-value; the smallest attainable value is ~1e-4."""
    return "< 0.0001" if p < 1.5e-4 else f"= {p:.4f}"


def format_summary(results: dict[str, Any]) -> str:
    """Human-readable summary of ``run_analysis`` output."""
    lines = [
        f"{results['n_cycles']} complete cycles, {results['first_start']}-{results['last_end']}",
        f"mean rise {results['mean_rise_years']} y, mean fall {results['mean_fall_years']} y, "
        f"mean length {results['mean_length_years']} y; rise shorter than fall in "
        f"{results['rise_shorter_than_fall']} of {results['n_cycles']} cycles",
        "Spearman rho vs amplitude (permutation p, 95% bootstrap interval):",
    ]
    for name, r in results["correlation_with_amplitude"].items():
        lines.append(
            f"  {name:<13} rho={r['rho']:+.3f}  p {_fmt_p(r['p_value'])}  "
            f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]"
        )
    lo, hi = results["rise_leave_one_out_rho"]
    lines.append(f"rise-time rho dropping any one cycle: {lo:+.3f} to {hi:+.3f}")
    lines.append("Sensitivity (rise time):")
    for r in results["sensitivity"]:
        lines.append(
            f"  {r['label']:<24} n={r['n']:>2} rho={r['rho']:+.3f}  p {_fmt_p(r['p_value'])}  "
            f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]"
        )
    return "\n".join(lines)
