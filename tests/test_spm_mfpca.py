"""Tests for fdars.spm — mfpca and spe_multivariate bindings.

MULTI-03: mfpca (6-key PyDict, P-length eigenfunctions/means lists) +
spe_multivariate ((n,) 1-D array) extend fdars.spm, both taking plain 2-D
array lists (neither consuming PyMultiFunData).
"""

import numpy as np
import pytest

import fdars.spm as spm

# ---------------------------------------------------------------------------
# Non-square multi-variable fixtures (research section 8)
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(42)

N_OBS = 20
# Variable 1: 30 grid points
VAR1 = RNG.standard_normal((N_OBS, 30))   # non-square: 20 obs × 30 pts
# Variable 2: 25 grid points (different domain)
VAR2 = RNG.standard_normal((N_OBS, 25))   # non-square: 20 obs × 25 pts
AV1 = np.linspace(0, 1, 30)
AV2 = np.linspace(0, 2, 25)

NCOMP = 4

# ---------------------------------------------------------------------------
# test_mfpca — 6-key dict, correct shapes, no pub(super) keys
# ---------------------------------------------------------------------------

def test_mfpca_returns_six_key_dict():
    """mfpca returns exactly the 6 public-field keys (no pub(super) fields)."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    expected_keys = {"scores", "eigenfunctions", "eigenvalues", "means", "scales", "grid_sizes"}
    assert set(result.keys()) == expected_keys


def test_mfpca_scores_shape():
    """scores shape is (n_obs, ncomp)."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    assert result["scores"].shape == (N_OBS, NCOMP)


def test_mfpca_eigenfunctions_list_length():
    """eigenfunctions is a list with one entry per variable (P=2)."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    ef = result["eigenfunctions"]
    assert isinstance(ef, list)
    assert len(ef) == 2
    # Each entry is (n_points_p, ncomp)
    assert ef[0].shape == (30, NCOMP)
    assert ef[1].shape == (25, NCOMP)


def test_mfpca_eigenvalues_shape():
    """eigenvalues shape is (ncomp,)."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    assert result["eigenvalues"].shape == (NCOMP,)


def test_mfpca_means_list_length():
    """means is a list with one entry per variable (P=2)."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    means = result["means"]
    assert isinstance(means, list)
    assert len(means) == 2
    # Each entry is (n_points_p,)
    assert means[0].shape == (30,)
    assert means[1].shape == (25,)


def test_mfpca_scales_shape():
    """scales shape is (P,) — one per-variable std-dev."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    assert result["scales"].shape == (2,)


def test_mfpca_grid_sizes_list():
    """grid_sizes is a list of P ints matching the variable domains."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    gs = result["grid_sizes"]
    assert isinstance(gs, list)
    assert len(gs) == 2
    assert gs[0] == 30
    assert gs[1] == 25


def test_mfpca_no_pub_super_keys():
    """combined_rotation and scale_threshold (pub(super)) must NOT appear in result."""
    result = spm.mfpca([VAR1, VAR2], ncomp=NCOMP)
    assert "combined_rotation" not in result
    assert "scale_threshold" not in result


# ---------------------------------------------------------------------------
# test_spe_multivariate — naked (n,) 1-D array
# ---------------------------------------------------------------------------

def test_spe_multivariate_shape():
    """spe_multivariate returns a 1-D (n_obs,) array."""
    # Reconstruct from mfpca to get proper inputs for spe_multivariate.
    # For testing purposes, use VAR1/VAR2 themselves as both standardized
    # and reconstructed (SPE will be close to zero, but shape must be correct).
    result = spm.spe_multivariate(
        [VAR1, VAR2],           # standardized_vars
        [VAR1, VAR2],           # reconstructed_vars (same → SPE ~ 0)
        [AV1, AV2],             # argvals_list
    )
    assert isinstance(result, np.ndarray)
    assert result.ndim == 1
    assert result.shape == (N_OBS,)


def test_spe_multivariate_is_not_dict():
    """spe_multivariate returns a naked array, not a dict."""
    result = spm.spe_multivariate([VAR1, VAR2], [VAR1, VAR2], [AV1, AV2])
    assert not isinstance(result, dict)


def test_spe_multivariate_nonnegative_when_identical():
    """SPE must be >= 0; when standardized == reconstructed, residuals are zero."""
    result = spm.spe_multivariate([VAR1, VAR2], [VAR1, VAR2], [AV1, AV2])
    assert np.all(result >= -1e-10), "SPE values must be non-negative"
