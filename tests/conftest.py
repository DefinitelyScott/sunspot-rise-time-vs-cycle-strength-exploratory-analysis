"""Shared fixtures. Puts ``src/`` on the path so tests run without installing."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sunspot_cycles.data import load_sunspots  # noqa: E402


@pytest.fixture(scope="session")
def sunspots() -> pd.Series:
    """The real bundled yearly series."""
    return load_sunspots()


@pytest.fixture
def toy_series() -> pd.Series:
    """Two hand-built cycles: minima at 2000, 2010, 2020; peaks 2004 (80) and 2013 (40)."""
    values = [0, 20, 50, 70, 80, 60, 40, 25, 10, 4, 0, 10, 30, 40, 30, 20, 10, 6, 3, 1, 0]
    return pd.Series([float(v) for v in values], index=range(2000, 2021), name="sunspots")
