from __future__ import annotations

import pandas as pd
import pytest

from sunspot_cycles.data import validate_series


def test_real_series_shape(sunspots):
    assert len(sunspots) == 309
    assert (sunspots.index[0], sunspots.index[-1]) == (1700, 2008)
    assert sunspots.min() >= 0


def test_validate_rejects_gap_and_nan():
    with pytest.raises(ValueError):
        validate_series(pd.Series([1.0, 2.0, 3.0], index=[1, 2, 4]))
    with pytest.raises(ValueError):
        validate_series(pd.Series([1.0, float("nan")], index=[1, 2]))
    with pytest.raises(ValueError):
        validate_series(pd.Series([], dtype=float))
