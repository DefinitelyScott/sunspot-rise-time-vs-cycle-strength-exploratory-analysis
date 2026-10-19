"""Matplotlib figures. Each function saves a PNG and returns its path."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

DPI = 130


def plot_series(series: pd.Series, cycles: pd.DataFrame, path: Path) -> Path:
    """Annual series with the detected minima and peaks marked."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(series.index, series.to_numpy(), color="0.35", linewidth=1)
    minima = cycles["start"].tolist() + [int(cycles["end"].iloc[-1])]
    ax.scatter(minima, series.loc[minima], color="tab:blue", zorder=3, label="detected minimum")
    ax.scatter(
        cycles["peak_year"],
        series.loc[cycles["peak_year"]],
        color="tab:red",
        zorder=3,
        label="detected peak",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual sunspot number")
    ax.set_title("Cycle segmentation (3-year smoothing used to locate marks)")
    ax.legend(frameon=False)
    return _save(fig, path)


def plot_rise_vs_amplitude(cycles: pd.DataFrame, rho: float, path: Path) -> Path:
    """Scatter of rise time against amplitude; x jittered because rise time is integer."""
    rng = np.random.default_rng(0)
    jitter = rng.uniform(-0.12, 0.12, len(cycles))
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.scatter(cycles["amplitude"], cycles["rise_years"] + jitter, color="tab:red", alpha=0.8)
    ax.set_xlabel("Cycle amplitude (smoothed peak sunspot number)")
    ax.set_ylabel("Rise time, minimum to peak (years, vertical jitter added)")
    ax.set_title(f"Stronger cycles rise faster (Spearman rho = {rho:.2f}, n = {len(cycles)})")
    return _save(fig, path)


def plot_sensitivity(table: pd.DataFrame, path: Path) -> Path:
    """Spearman rho with bootstrap interval for every analysis specification."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ypos = np.arange(len(table))[::-1]
    err = [table["rho"] - table["ci_low"], table["ci_high"] - table["rho"]]
    ax.errorbar(table["rho"], ypos, xerr=err, fmt="o", color="tab:red", capsize=3)
    ax.axvline(0, color="0.5", linewidth=1)
    ax.set_yticks(ypos, table["label"])
    ax.set_xlabel("Spearman rho, rise time vs amplitude (95% bootstrap interval)")
    ax.set_title("Sensitivity to smoothing window and cycle selection")
    return _save(fig, path)


def _save(fig: plt.Figure, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path
