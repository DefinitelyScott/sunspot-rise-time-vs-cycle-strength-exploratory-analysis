"""Split a yearly sunspot series into cycles and measure each one."""

from __future__ import annotations

import pandas as pd

MIN_SEPARATION_YEARS = 7
"""Two cycle minima closer than this are treated as one (cycles last ~9-14 years)."""


def smooth(series: pd.Series, window: int) -> pd.Series:
    """Centered rolling mean; ``window=1`` returns the series unchanged.

    Edge years without a full window become NaN rather than being extrapolated.

    Args:
        series: Yearly values.
        window: Odd window width in years.

    Raises:
        ValueError: If ``window`` is not a positive odd integer.
    """
    if window < 1 or window % 2 == 0:
        raise ValueError("window must be a positive odd integer")
    if window == 1:
        return series.astype(float)
    return series.rolling(window, center=True, min_periods=window).mean()


def find_minima(smoothed: pd.Series, min_separation: int = MIN_SEPARATION_YEARS) -> list[int]:
    """Find cycle-minimum years in a smoothed series.

    A candidate is a year no higher than both neighbours. Candidates are then
    accepted lowest-first, skipping any within ``min_separation`` years of one
    already accepted, which removes noise wiggles near a minimum. The first and
    last years can never be minima because they lack a neighbour.

    Args:
        smoothed: Smoothed yearly series (NaN edges allowed).
        min_separation: Minimum gap in years between accepted minima.

    Returns:
        Accepted minimum years, sorted ascending.
    """
    years = smoothed.index
    candidates = [
        int(y)
        for y in years[1:-1]
        if pd.notna(smoothed[y])
        and smoothed[y] <= smoothed[y - 1]
        and smoothed[y] <= smoothed[y + 1]
    ]
    accepted: list[int] = []
    for year in sorted(candidates, key=lambda y: (smoothed[y], y)):
        if all(abs(year - other) >= min_separation for other in accepted):
            accepted.append(year)
    return sorted(accepted)


def measure_cycles(series: pd.Series, window: int = 3) -> pd.DataFrame:
    """Measure every complete cycle (minimum to next minimum).

    Args:
        series: Yearly sunspot numbers.
        window: Smoothing window used for locating minima and the peak.

    Returns:
        One row per complete cycle with columns ``start``, ``peak_year``, ``end``,
        ``rise_years`` (start to peak), ``fall_years`` (peak to end),
        ``length_years`` and ``amplitude`` (smoothed value at the peak).
        Partial cycles at either end of the series are excluded.
    """
    smoothed = smooth(series, window)
    minima = find_minima(smoothed)
    rows = []
    for start, end in zip(minima[:-1], minima[1:], strict=True):
        segment = smoothed.loc[start:end]
        peak_year = int(segment.idxmax())
        rows.append(
            {
                "start": start,
                "peak_year": peak_year,
                "end": end,
                "rise_years": peak_year - start,
                "fall_years": end - peak_year,
                "length_years": end - start,
                "amplitude": float(segment.max()),
            }
        )
    return pd.DataFrame(rows)
