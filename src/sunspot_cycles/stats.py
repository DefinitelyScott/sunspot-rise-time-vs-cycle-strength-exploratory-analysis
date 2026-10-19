"""Rank correlation with a permutation test and a bootstrap interval."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import rankdata

N_RESAMPLES = 10_000
SEED = 20261015


@dataclass(frozen=True)
class RankCorrelation:
    """Spearman correlation plus uncertainty, for one pair of variables."""

    rho: float
    p_value: float
    ci_low: float
    ci_high: float
    n: int


def _check(x: np.ndarray, y: np.ndarray) -> None:
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("x and y must be 1-D arrays of equal length")
    if len(x) < 4:
        raise ValueError("need at least 4 observations")
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        raise ValueError("a constant variable has no rank correlation")


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman's rho: Pearson correlation of the average ranks (ties allowed)."""
    _check(x, y)
    return _pearson(rankdata(x), rankdata(y))


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    return float((a @ b) / np.sqrt((a @ a) * (b @ b)))


def permutation_p_value(
    x: np.ndarray, y: np.ndarray, n_resamples: int = N_RESAMPLES, seed: int = SEED
) -> float:
    """Two-sided permutation p-value for Spearman's rho.

    Shuffles ``y`` n_resamples times and counts correlations at least as extreme
    as observed. Uses the +1 correction so the p-value is never exactly zero.
    """
    _check(x, y)
    rng = np.random.default_rng(seed)
    rx, ry = rankdata(x), rankdata(y)
    observed = abs(_pearson(rx, ry))
    extreme = sum(
        abs(_pearson(rx, rng.permutation(ry))) >= observed - 1e-12 for _ in range(n_resamples)
    )
    return (extreme + 1) / (n_resamples + 1)


def bootstrap_interval(
    x: np.ndarray, y: np.ndarray, n_resamples: int = N_RESAMPLES, seed: int = SEED
) -> tuple[float, float]:
    """95% percentile bootstrap interval for rho, resampling whole cycles.

    Resamples that happen to make either variable constant are skipped.
    """
    _check(x, y)
    rng = np.random.default_rng(seed)
    n = len(x)
    draws = []
    while len(draws) < n_resamples:
        idx = rng.integers(0, n, n)
        if np.ptp(x[idx]) == 0 or np.ptp(y[idx]) == 0:
            continue
        draws.append(_pearson(rankdata(x[idx]), rankdata(y[idx])))
    low, high = np.percentile(draws, [2.5, 97.5])
    return float(low), float(high)


def rank_correlation(x: np.ndarray, y: np.ndarray) -> RankCorrelation:
    """Spearman rho with permutation p-value and bootstrap 95% interval."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    low, high = bootstrap_interval(x, y)
    return RankCorrelation(
        rho=spearman(x, y),
        p_value=permutation_p_value(x, y),
        ci_low=low,
        ci_high=high,
        n=len(x),
    )


def leave_one_out_range(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Smallest and largest rho when each single observation is dropped in turn."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    _check(x, y)
    rhos = [spearman(np.delete(x, i), np.delete(y, i)) for i in range(len(x))]
    return min(rhos), max(rhos)
