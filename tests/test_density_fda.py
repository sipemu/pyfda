"""Tests for fdars.density_fda — LQD transform, Wasserstein barycenter, density FPCA.

Plan 69-04 (FRE-02): normalize_density (tracer), lqd_transform, inverse_lqd,
wasserstein_barycenter, and lqd_fpca.
"""

import numpy as np
import pytest
from scipy.stats import beta as sp_beta

import fdars
import fdars.density_fda as d_fda

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

N_DENS, M_DENS = 20, 60  # n densities on m grid points — non-square
argvals_dens = np.linspace(0.0, 1.0, M_DENS)

# Density matrix: each row is a Beta-like density
# Add a small epsilon to ensure all entries are strictly positive (required by lqd_transform)
rng = np.random.default_rng(42)
density_matrix = np.zeros((N_DENS, M_DENS))
for i in range(N_DENS):
    a, b = 1 + i * 0.2, 2.0
    raw = sp_beta.pdf(argvals_dens, a, b) + 1e-8  # epsilon for strict positivity
    density_matrix[i] = raw / np.trapezoid(raw, argvals_dens)

# Single density for normalize/lqd — use first row
density_single_raw = density_matrix[0].copy()  # (M_DENS,) array, may have zero tails

# LQD requires strictly positive density — add small epsilon and renormalize
# (per Pitfall 6: Beta PDF can be zero at the endpoints)
density_single_lqd = density_single_raw + 1e-8
integral_lqd = np.trapezoid(density_single_lqd, argvals_dens)
density_single_lqd = density_single_lqd / integral_lqd
assert (density_single_lqd > 0).all(), "density_single_lqd must be strictly positive"

# density_single_raw can have zeros (used only in normalize_density tests)
density_single = density_single_raw


# ---------------------------------------------------------------------------
# Task 1 (tracer): normalize_density
# ---------------------------------------------------------------------------


def test_normalize_density_returns_1d_array():
    """normalize_density returns a naked numpy 1D array of the correct shape."""
    result = d_fda.normalize_density(density_single, argvals_dens)
    assert isinstance(result, np.ndarray), "result must be a numpy ndarray, not a dict"
    assert result.ndim == 1, f"expected 1D, got {result.ndim}D"
    assert result.shape == (M_DENS,), f"expected shape ({M_DENS},), got {result.shape}"


def test_normalize_density_integrates_to_one():
    """normalize_density output integrates to 1 within 1e-6."""
    # Use an unnormalized density (multiply by 3.7)
    unnorm = density_single * 3.7
    result = d_fda.normalize_density(unnorm, argvals_dens)
    integral = np.trapezoid(result, argvals_dens)
    assert abs(integral - 1.0) < 1e-6, f"integral should be ~1.0, got {integral}"


def test_normalize_density_already_normalized():
    """normalize_density is idempotent on an already-normalized density."""
    result = d_fda.normalize_density(density_single, argvals_dens)
    integral = np.trapezoid(result, argvals_dens)
    assert abs(integral - 1.0) < 1e-6, f"integral should be ~1.0, got {integral}"


def test_normalize_density_negative_value_raises():
    """normalize_density raises ValueError when any density value is negative."""
    bad = density_single.copy()
    bad[10] = -0.01
    with pytest.raises(ValueError):
        d_fda.normalize_density(bad, argvals_dens)


def test_normalize_density_is_callable():
    """Sanity: normalize_density is directly callable on fdars.density_fda."""
    assert callable(fdars.density_fda.normalize_density)


# ---------------------------------------------------------------------------
# Task 2: lqd_transform, inverse_lqd, wasserstein_barycenter
# ---------------------------------------------------------------------------


def test_lqd_transform_returns_1d_array():
    """lqd_transform returns a naked numpy 1D array."""
    result = d_fda.lqd_transform(density_single_lqd, argvals_dens)
    assert isinstance(result, np.ndarray), "result must be a numpy ndarray, not a dict"
    assert result.ndim == 1, f"expected 1D, got {result.ndim}D"
    assert result.shape[0] > 0, "result must be non-empty"


def test_lqd_round_trip():
    """LQD round-trip: inverse_lqd(lqd_transform(density)) recovers the input density.

    Uses a roughly-uniform density (well-behaved interior) for numerical stability.
    The LQD round-trip is approximate — boundary effects from interpolation can cause
    deviations, especially for densities with very small tails.
    """
    # Use a roughly-uniform density on [0, 1] for a well-conditioned round-trip.
    # A small perturbation of the uniform density (which has psi=0 analytically).
    t = argvals_dens
    # Gaussian bump with strictly positive floor — no zero tails
    bump = np.exp(-0.5 * ((t - 0.5) / 0.2) ** 2)
    density_for_rt = 1.0 + 0.3 * bump  # strictly positive perturbation of uniform
    density_for_rt = density_for_rt / np.trapezoid(density_for_rt, argvals_dens)
    assert (density_for_rt > 0).all()

    psi = d_fda.lqd_transform(density_for_rt, argvals_dens)

    # The quantile t-grid is the uniform [0, 1] grid of length len(psi)
    t_grid = np.linspace(0.0, 1.0, len(psi))

    # Reconstruct density on the original argvals
    recon = d_fda.inverse_lqd(psi, t_grid, argvals_dens)

    assert isinstance(psi, np.ndarray), "lqd_transform result must be naked ndarray"
    assert isinstance(recon, np.ndarray), "inverse_lqd result must be naked ndarray"
    assert recon.shape == (M_DENS,), f"expected shape ({M_DENS},), got {recon.shape}"

    # Verify both are normalized
    assert abs(np.trapezoid(recon, argvals_dens) - 1.0) < 1e-6, "reconstructed density should integrate to 1"

    # Compare shapes: the round-trip should approximately recover the input
    # Use L1-style check on the interior to avoid boundary interpolation effects
    interior = slice(5, -5)
    rel_err = np.mean(np.abs(recon[interior] - density_for_rt[interior]))
    assert rel_err < 0.05, (
        f"LQD round-trip interior error too large: {rel_err:.4f} (expected < 0.05)"
    )


def test_lqd_transform_strictly_positive_required():
    """lqd_transform raises ValueError when density has a zero value."""
    bad = density_single_lqd.copy()
    bad[5] = 0.0  # set to zero — not strictly positive
    with pytest.raises(ValueError):
        d_fda.lqd_transform(bad, argvals_dens)


def test_inverse_lqd_returns_1d_array():
    """inverse_lqd returns a naked numpy 1D array."""
    psi = d_fda.lqd_transform(density_single_lqd, argvals_dens)
    t_grid = np.linspace(0.0, 1.0, len(psi))
    recon = d_fda.inverse_lqd(psi, t_grid, argvals_dens)
    assert isinstance(recon, np.ndarray), "result must be a numpy ndarray, not a dict"
    assert recon.ndim == 1, f"expected 1D, got {recon.ndim}D"


def test_wasserstein_barycenter_shape():
    """wasserstein_barycenter returns a 1D array of length M_DENS."""
    bary = d_fda.wasserstein_barycenter(density_matrix, argvals_dens)
    assert isinstance(bary, np.ndarray), "result must be a numpy ndarray, not a dict"
    assert bary.ndim == 1, f"expected 1D, got {bary.ndim}D"
    assert bary.shape == (M_DENS,), f"expected shape ({M_DENS},), got {bary.shape}"


def test_wasserstein_barycenter_integrates_to_one():
    """wasserstein_barycenter output integrates to ~1."""
    bary = d_fda.wasserstein_barycenter(density_matrix, argvals_dens)
    integral = np.trapezoid(bary, argvals_dens)
    assert abs(integral - 1.0) < 1e-3, f"barycenter should integrate to ~1.0, got {integral}"


def test_wasserstein_barycenter_with_weights():
    """wasserstein_barycenter with explicit weights also integrates to ~1."""
    weights = np.ones(N_DENS) / N_DENS
    bary = d_fda.wasserstein_barycenter(density_matrix, argvals_dens, weights=weights)
    assert bary.shape == (M_DENS,), f"expected shape ({M_DENS},), got {bary.shape}"
    integral = np.trapezoid(bary, argvals_dens)
    assert abs(integral - 1.0) < 1e-3, f"barycenter should integrate to ~1.0, got {integral}"


# ---------------------------------------------------------------------------
# Task 3: lqd_fpca
# ---------------------------------------------------------------------------


def test_lqd_fpca_six_keys():
    """lqd_fpca returns a dict with exactly 6 keys."""
    result = d_fda.lqd_fpca(density_matrix, argvals_dens, ncomp=3)
    assert isinstance(result, dict), f"expected dict, got {type(result)}"
    expected_keys = {"mean", "singular_values", "loadings", "scores", "fve", "ncomp"}
    assert set(result.keys()) == expected_keys, (
        f"expected keys {expected_keys}, got {set(result.keys())}"
    )


def test_lqd_fpca_no_internal_keys():
    """lqd_fpca does not expose centered or weights (internal SVD state)."""
    result = d_fda.lqd_fpca(density_matrix, argvals_dens, ncomp=3)
    assert "centered" not in result, "centered should NOT be exposed"
    assert "weights" not in result, "weights should NOT be exposed"
    assert "rotation" not in result, "rotation key should be exposed as 'loadings', not 'rotation'"


def test_lqd_fpca_shapes():
    """lqd_fpca dict entries have correct shapes."""
    result = d_fda.lqd_fpca(density_matrix, argvals_dens, ncomp=3)

    k = result["ncomp"]
    assert isinstance(k, int) or np.issubdtype(type(k), np.integer), (
        f"ncomp must be an int, got {type(k)}"
    )
    k = int(k)
    assert 1 <= k <= 3, f"ncomp should be 1 <= k <= 3, got {k}"

    # mean: 1D (n_q,)
    mean = result["mean"]
    assert mean.ndim == 1, f"mean should be 1D, got {mean.ndim}D"
    n_q = mean.shape[0]
    assert n_q > 0

    # singular_values: 1D (k,)
    sv = result["singular_values"]
    assert sv.shape == (k,), f"singular_values shape: expected ({k},), got {sv.shape}"

    # loadings: 2D (n_q, k) — rotation exposed as "loadings"
    loadings = result["loadings"]
    assert loadings.ndim == 2, f"loadings should be 2D, got {loadings.ndim}D"
    assert loadings.shape == (n_q, k), (
        f"loadings shape: expected ({n_q}, {k}), got {loadings.shape}"
    )

    # scores: 2D (N_DENS, k)
    scores = result["scores"]
    assert scores.ndim == 2, f"scores should be 2D, got {scores.ndim}D"
    assert scores.shape == (N_DENS, k), (
        f"scores shape: expected ({N_DENS}, {k}), got {scores.shape}"
    )

    # fve: 1D (k,)
    fve = result["fve"]
    assert fve.shape == (k,), f"fve shape: expected ({k},), got {fve.shape}"


def test_lqd_fpca_fve_monotone():
    """lqd_fpca fve (fraction of variance explained) should be non-decreasing."""
    result = d_fda.lqd_fpca(density_matrix, argvals_dens, ncomp=3)
    fve = result["fve"]
    for i in range(len(fve) - 1):
        assert fve[i] <= fve[i + 1] + 1e-10, (
            f"fve should be non-decreasing: fve[{i}]={fve[i]:.4f} > fve[{i+1}]={fve[i+1]:.4f}"
        )


# ---------------------------------------------------------------------------
# Sanity: all 5 functions are callable on fdars.density_fda
# ---------------------------------------------------------------------------


def test_all_five_functions_callable():
    """All 5 density_fda functions are present and callable."""
    names = ("normalize_density", "lqd_transform", "inverse_lqd",
             "wasserstein_barycenter", "lqd_fpca")
    count = sum(hasattr(fdars.density_fda, n) for n in names)
    assert count == 5, (
        f"expected 5 functions, found {count}: "
        + str([n for n in names if not hasattr(fdars.density_fda, n)])
    )
