"""Load the yearly sunspot series bundled with statsmodels."""

from __future__ import annotations

import pandas as pd
import statsmodels.api as sm


def load_sunspots() -> pd.Series:
    """Return the yearly sunspot numbers 1700-2008, indexed by integer year.

    The table ships inside statsmodels (source: NOAA National Geophysical Data
    Center, public domain), so no download is needed. Pinning statsmodels in
    requirements.txt therefore also pins the data.

    Returns:
        A float Series named ``sunspots`` with a unique, increasing integer index.

    Raises:
        ValueError: If the table is missing values or years are not consecutive.
    """
    raw = sm.datasets.sunspots.load_pandas().data
    series = pd.Series(
        raw["SUNACTIVITY"].to_numpy(dtype=float),
        index=raw["YEAR"].to_numpy(dtype=int),
        name="sunspots",
    )
    validate_series(series)
    return series


def validate_series(series: pd.Series) -> None:
    """Check the series is complete and annual.

    Args:
        series: Candidate sunspot series indexed by year.

    Raises:
        ValueError: On NaNs, an empty series, or a gap between consecutive years.
    """
    if series.empty:
        raise ValueError("series is empty")
    if series.isna().any():
        raise ValueError("series contains missing values")
    if not (series.index.to_series().diff().dropna() == 1).all():
        raise ValueError("series index must be consecutive years")
