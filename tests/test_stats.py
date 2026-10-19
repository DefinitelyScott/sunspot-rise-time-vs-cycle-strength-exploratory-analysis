from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr

from sunspot_cycles import stats

X = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])


def test_spearman_perfect_monotone():
    assert stats.spearman(X, X**3) == pytest.approx(1.0)
    assert stats.spearman(X, -X) == pytest.approx(-1.0)


def test_spearman_matches_scipy_with_ties():
    y = np.array([3.0, 3.0, 1.0, 5.0, 5.0, 5.0, 2.0, 4.0])
    assert stats.spearman(X, y) == pytest.approx(spearmanr(X, y).statistic)


def test_constant_variable_rejected():
    with pytest.raises(ValueError):
        stats.spearman(X, np.ones_like(X))


def test_too_few_observations_rejected():
    with pytest.raises(ValueError):
        stats.spearman(X[:3], X[:3])


def test_permutation_p_small_for_strong_and_large_for_noise():
    assert stats.permutation_p_value(X, X, n_resamples=2000) < 0.01
    rng = np.random.default_rng(1)
    noise = rng.normal(size=40)
    assert stats.permutation_p_value(noise, rng.normal(size=40), n_resamples=2000) > 0.05


def test_permutation_p_is_deterministic():
    y = np.array([2.0, 1.0, 4.0, 3.0, 6.0, 5.0, 8.0, 7.0])
    assert stats.permutation_p_value(X, y, 500) == stats.permutation_p_value(X, y, 500)


def test_bootstrap_interval_contains_estimate_and_is_ordered():
    y = np.array([2.0, 1.0, 4.0, 3.0, 6.0, 5.0, 8.0, 7.0])
    low, high = stats.bootstrap_interval(X, y, n_resamples=1000)
    assert low <= stats.spearman(X, y) <= high


def test_leave_one_out_range_perfect_monotone_is_one():
    assert stats.leave_one_out_range(X, X**2) == pytest.approx((1.0, 1.0))


def test_leave_one_out_range_is_ordered():
    y = np.array([2.0, 1.0, 4.0, 3.0, 6.0, 5.0, 8.0, 7.0])
    low, high = stats.leave_one_out_range(X, y)
    assert low <= high
