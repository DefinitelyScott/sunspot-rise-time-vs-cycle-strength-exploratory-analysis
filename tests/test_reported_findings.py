"""Pin the numbers quoted in README.md so docs and code cannot drift apart."""

from __future__ import annotations

import pytest

from sunspot_cycles import cycles, stats


@pytest.fixture(scope="module")
def measured(sunspots):
    return cycles.measure_cycles(sunspots, 3)


def test_cycle_count_and_span(measured):
    assert len(measured) == 26
    assert (measured["start"].iloc[0], measured["end"].iloc[-1]) == (1712, 1996)


def test_headline_rise_time_correlation(measured):
    rho = stats.spearman(measured["amplitude"].to_numpy(), measured["rise_years"].to_numpy())
    assert rho == pytest.approx(-0.574, abs=5e-4)


def test_fall_time_has_no_comparable_relationship(measured):
    rho = stats.spearman(measured["amplitude"].to_numpy(), measured["fall_years"].to_numpy())
    assert abs(rho) < 0.2


def test_mean_rise_shorter_than_fall(measured):
    assert measured["rise_years"].mean() == pytest.approx(4.88, abs=0.005)
    assert measured["fall_years"].mean() == pytest.approx(6.04, abs=0.005)
