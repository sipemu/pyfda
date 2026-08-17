"""Tests for basis/smoothing quick-wins: BASIS-01, BASIS-02, BASIS-03.

Task 1 (tracer): optim_bandwidth AIC kernel-bandwidth path.
Task 2: constant_basis all-ones intercept column.
Task 3: smooth_basis_aic binding + basis_nbasis_cv("aic") test coverage.
"""
import math
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Task 1 (tracer): optim_bandwidth — AIC kernel-bandwidth selection
# ---------------------------------------------------------------------------

def _make_signal(n=40, seed=0):
    """Small synthetic 1-D regression signal."""
    x = np.linspace(0, 1, n)
    rng = np.random.default_rng(seed)
    y = np.sin(2 * np.pi * x) + 0.1 * rng.standard_normal(n)
    return x, y


def test_optim_bandwidth_aic_reports_criterion():
    """AIC path returns a positive finite h_opt and criterion == 'aic'."""
    import fdars.smoothing as sm
    x, y = _make_signal()
    result = sm.optim_bandwidth(x, y, criterion="aic", n_grid=15)
    assert result["criterion"] == "aic", f"Got criterion={result['criterion']!r}"
    assert math.isfinite(result["h_opt"]) and result["h_opt"] > 0, (
        f"Expected positive finite h_opt, got {result['h_opt']}"
    )


def test_optim_bandwidth_gcv_unchanged():
    """GCV path still returns criterion == 'gcv' (non-regression)."""
    import fdars.smoothing as sm
    x, y = _make_signal()
    result = sm.optim_bandwidth(x, y, criterion="gcv", n_grid=15)
    assert result["criterion"] == "gcv"
    assert math.isfinite(result["h_opt"]) and result["h_opt"] > 0


def test_optim_bandwidth_unknown_criterion_raises():
    """Unknown criterion string raises ValueError."""
    import fdars.smoothing as sm
    x, y = _make_signal()
    with pytest.raises(ValueError):
        sm.optim_bandwidth(x, y, criterion="banana")


# ---------------------------------------------------------------------------
# Task 2: constant_basis — all-ones 1-D intercept column
# ---------------------------------------------------------------------------

def test_constant_basis_all_ones():
    """constant_basis returns all-ones 1-D ndarray of correct length."""
    import fdars.basis as b
    argvals = np.linspace(0, 1, 20)
    result = b.constant_basis(argvals)
    assert result.ndim == 1, f"Expected 1-D array, got ndim={result.ndim}"
    assert result.shape == (20,), f"Expected shape (20,), got {result.shape}"
    assert np.allclose(result, 1.0), f"Expected all ones, got {result}"


def test_constant_basis_empty_input():
    """constant_basis with empty input returns a length-0 array without panicking."""
    import fdars.basis as b
    result = b.constant_basis(np.array([], dtype=float))
    assert result.shape == (0,), f"Expected shape (0,), got {result.shape}"


def test_constant_basis_various_lengths():
    """constant_basis works for different grid sizes."""
    import fdars.basis as b
    for n in [1, 5, 100]:
        argvals = np.linspace(0, 1, n)
        result = b.constant_basis(argvals)
        assert result.shape == (n,)
        assert np.allclose(result, 1.0)


# ---------------------------------------------------------------------------
# Task 3: smooth_basis_aic + basis_nbasis_cv("aic")
# ---------------------------------------------------------------------------

def _load_weather_data():
    """Load Canadian Weather (35x365) as raw arrays."""
    from fdars.datasets import load_canadian_weather
    day, X, _ = load_canadian_weather(return_fdata=False)
    # day is length 365, X is (35, 365)
    return day, X


def test_smooth_basis_aic_returns_valid_dict():
    """smooth_basis_aic returns a dict with all expected keys and finite values."""
    import fdars.basis as b
    day, X = _load_weather_data()
    result = b.smooth_basis_aic(X, day, n_basis=10, n_grid=10)
    expected_keys = {"fitted", "coefficients", "edf", "gcv", "aic", "bic", "nbasis"}
    assert set(result.keys()) >= expected_keys, (
        f"Missing keys: {expected_keys - set(result.keys())}"
    )
    assert result["fitted"].shape == X.shape, (
        f"fitted shape {result['fitted'].shape} != X shape {X.shape}"
    )
    assert math.isfinite(result["aic"]), f"aic not finite: {result['aic']}"
    assert math.isfinite(result["gcv"]), f"gcv not finite: {result['gcv']}"
    assert math.isfinite(result["edf"]) and result["edf"] > 0


def test_smooth_basis_gcv_and_aic_both_valid():
    """Both smooth_basis_gcv and smooth_basis_aic return valid dicts on same data."""
    import fdars.basis as b
    day, X = _load_weather_data()
    gcv_result = b.smooth_basis_gcv(X, day, n_basis=10, n_grid=10)
    aic_result = b.smooth_basis_aic(X, day, n_basis=10, n_grid=10)
    # Both must have the expected keys and finite scalars — lambdas/edf may differ
    for key in ("fitted", "coefficients", "edf", "gcv", "aic", "bic", "nbasis"):
        assert key in gcv_result
        assert key in aic_result


def test_smooth_basis_aic_degenerate_raises():
    """smooth_basis_aic with n_basis=1 (nbasis<2) raises ValueError."""
    import fdars.basis as b
    day, X = _load_weather_data()
    with pytest.raises(ValueError):
        b.smooth_basis_aic(X, day, n_basis=1)


def test_basis_nbasis_cv_aic_criterion():
    """basis_nbasis_cv(criterion='aic') returns a dict with result['criterion'] == 'aic'."""
    import fdars.basis as b
    day, X = _load_weather_data()
    result = b.basis_nbasis_cv(X, day, nbasis_min=4, nbasis_max=8, criterion="aic")
    assert result["criterion"] == "aic", f"Got criterion={result['criterion']!r}"
    assert "optimal_nbasis" in result
    assert result["optimal_nbasis"] >= 4


def test_basis_nbasis_cv_unknown_criterion_raises():
    """basis_nbasis_cv with unknown criterion raises ValueError."""
    import fdars.basis as b
    day, X = _load_weather_data()
    with pytest.raises(ValueError):
        b.basis_nbasis_cv(X, day, criterion="banana")
