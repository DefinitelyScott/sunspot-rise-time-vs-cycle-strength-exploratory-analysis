from __future__ import annotations

import pandas as pd
import pytest

from sunspot_cycles import cycles


def test_smooth_window_one_is_identity(toy_series):
    pd.testing.assert_series_equal(cycles.smooth(toy_series, 1), toy_series)


def test_smooth_is_centered_mean_with_nan_edges(toy_series):
    out = cycles.smooth(toy_series, 3)
    assert out.iloc[1] == pytest.approx((0 + 20 + 50) / 3)
    assert pd.isna(out.iloc[0]) and pd.isna(out.iloc[-1])


@pytest.mark.parametrize("window", [0, 2, 4, -3])
def test_smooth_rejects_bad_window(toy_series, window):
    with pytest.raises(ValueError):
        cycles.smooth(toy_series, window)


def test_find_minima_on_toy_series(toy_series):
    assert cycles.find_minima(toy_series) == [2010]


def test_find_minima_enforces_separation():
    s = pd.Series(
        [5.0, 1.0, 3.0, 0.0, 4.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 0.5, 9.0],
        index=range(100, 114),
    )
    # 1 and 3 are 2 years apart: only the lower (103, value 0) survives; 112 is far away.
    assert cycles.find_minima(s) == [103, 112]


def test_measure_cycles_toy_values(toy_series):
    out = cycles.measure_cycles(toy_series, window=1)
    # Endpoints (2000, 2020) are never minima, so only the middle cycle boundaries exist;
    # a single minimum yields no complete cycle.
    assert out.empty


def test_measure_cycles_two_complete_cycles():
    values = [9, 5, 0, 20, 50, 80, 60, 40, 20, 5, 0, 10, 30, 40, 30, 20, 10, 5, 0, 8, 12]
    s = pd.Series([float(v) for v in values], index=range(2000, 2021))
    out = cycles.measure_cycles(s, window=1)
    assert out["start"].tolist() == [2002, 2010]
    assert out["end"].tolist() == [2010, 2018]
    assert out["peak_year"].tolist() == [2005, 2013]
    assert out["rise_years"].tolist() == [3, 3]
    assert out["fall_years"].tolist() == [5, 5]
    assert out["length_years"].tolist() == [8, 8]
    assert out["amplitude"].tolist() == [80.0, 40.0]


def test_real_data_matches_published_cycle_minima(sunspots):
    """Detected minima must sit within 2 years of the commonly published dates
    (List of solar cycles / SILSO; month-resolution dates rounded to year)."""
    published = [
        1755,
        1766,
        1775,
        1785,
        1798,
        1811,
        1823,
        1834,
        1843,
        1856,
        1867,
        1879,
        1890,
        1902,
        1914,
        1923,
        1934,
        1944,
        1954,
        1965,
        1976,
        1987,
        1997,
    ]
    detected = cycles.measure_cycles(sunspots, 3)["start"].tolist()
    for year in published[:-1]:
        assert min(abs(year - d) for d in detected) <= 2, year
