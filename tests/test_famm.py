"""Tests for fdars.famm — Functional Additive Mixed-Model bindings.

Covers MULTI-02: dense_flmm (14-key dict), fast_fmm (6-key dict, p=0 → (0,m)),
and multi_famm (4-key dict with components list of D per-dimension 14-key dicts).

All fixtures use NON-SQUARE matrices (n_obs ≠ n_points) to guard against silent
row/column-major transposition bugs (research section 8).
"""

import numpy as np
import pytest

import fdars.famm as famm

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

RNG = np.random.default_rng(42)

N_SUBJECTS = 5
N_VISITS = 4
N_TOTAL = N_SUBJECTS * N_VISITS   # 20 curves total
N_GRID = 30                        # 30 evaluation points (NON-SQUARE: 20 ≠ 30)

SUBJECT_IDS = np.repeat(np.arange(N_SUBJECTS), N_VISITS).astype(np.int64)
DATA = RNG.standard_normal((N_TOTAL, N_GRID))   # shape (20, 30)

# Expected keys for dense_flmm result
DENSE_FLMM_KEYS = {
    "mean_function",
    "beta_functions",
    "random_effects",
    "fitted",
    "residuals",
    "random_variance",
    "sigma2_eps",
    "sigma2_u",
    "sigma2_slope",
    "ncomp",
    "n_subjects",
    "eigenvalues",
    "n_iter",
    "converged",
}

# Expected keys for fast_fmm result
FAST_FMM_KEYS = {
    "beta_matrix",
    "t_stats",
    "p_values",
    "sigma2_eps",
    "sigma2_u",
    "n_grid",
}

# Expected keys for multi_famm result
MULTI_FAMM_KEYS = {"n_dims", "stacked_fitted", "stacked_residuals", "components"}


# ---------------------------------------------------------------------------
# test_dense_flmm
# ---------------------------------------------------------------------------


def test_dense_flmm_returns_14_key_dict():
    """dense_flmm returns a dict with exactly the 14 documented keys."""
    result = famm.dense_flmm(DATA, SUBJECT_IDS)
    assert isinstance(result, dict), "Expected a dict"
    assert set(result.keys()) == DENSE_FLMM_KEYS, (
        f"Key mismatch: got {set(result.keys())}, expected {DENSE_FLMM_KEYS}"
    )


def test_dense_flmm_shapes():
    """dense_flmm output shapes match the documented conventions."""
    result = famm.dense_flmm(DATA, SUBJECT_IDS, ncomp=2)
    m = N_GRID
    k = result["ncomp"]   # actual ncomp (may differ from requested)

    assert result["mean_function"].shape == (m,), "mean_function shape"
    # No covariates → p=0; beta_functions is a 2-D array with 0 rows (and 0 cols when p=0)
    assert result["beta_functions"].ndim == 2, "beta_functions must be 2-D"
    assert result["random_effects"].shape == (N_SUBJECTS, m), "random_effects shape"
    assert result["fitted"].shape == (N_TOTAL, m), "fitted shape"
    assert result["residuals"].shape == (N_TOTAL, m), "residuals shape"
    assert result["random_variance"].shape == (m,), "random_variance shape"
    assert isinstance(result["sigma2_eps"], float), "sigma2_eps type"
    assert result["sigma2_u"].shape == (k,), "sigma2_u shape"
    assert result["sigma2_slope"].shape == (k,), "sigma2_slope shape"
    assert result["eigenvalues"].shape == (k,), "eigenvalues shape"
    assert isinstance(result["ncomp"], int), "ncomp type"
    assert isinstance(result["n_subjects"], int), "n_subjects type"
    assert result["n_subjects"] == N_SUBJECTS, "n_subjects value"
    assert isinstance(result["n_iter"], int), "n_iter type"
    assert isinstance(result["converged"], bool), "converged type"


# ---------------------------------------------------------------------------
# test_fast_fmm
# ---------------------------------------------------------------------------


def test_fast_fmm_returns_6_key_dict():
    """fast_fmm returns a dict with exactly the 6 documented keys."""
    result = famm.fast_fmm(DATA, SUBJECT_IDS)
    assert isinstance(result, dict), "Expected a dict"
    assert set(result.keys()) == FAST_FMM_KEYS, (
        f"Key mismatch: got {set(result.keys())}, expected {FAST_FMM_KEYS}"
    )


def test_fast_fmm_no_covariates_gives_zero_p_beta():
    """fast_fmm with p=0 (no covariates) gives zero-row arrays for beta_matrix, t_stats, p_values.

    fdars-core 0.33 returns an FdMatrix with shape (0, 0) when p=0 (no covariates),
    which converts to a (0, 0) numpy array.  The key requirement is that the arrays
    are 2-D with 0 rows, not that the column count matches the grid size.
    """
    result = famm.fast_fmm(DATA, SUBJECT_IDS)
    m = N_GRID
    # p=0 → (0, 0) shape: fdars-core produces a (0, 0) FdMatrix for the inference matrices
    assert result["beta_matrix"].ndim == 2, "beta_matrix must be 2-D"
    assert result["beta_matrix"].shape[0] == 0, (
        f"Expected 0 rows in beta_matrix (p=0), got {result['beta_matrix'].shape[0]}"
    )
    assert result["t_stats"].ndim == 2, "t_stats must be 2-D"
    assert result["t_stats"].shape[0] == 0, (
        f"Expected 0 rows in t_stats (p=0), got {result['t_stats'].shape[0]}"
    )
    assert result["p_values"].ndim == 2, "p_values must be 2-D"
    assert result["p_values"].shape[0] == 0, (
        f"Expected 0 rows in p_values (p=0), got {result['p_values'].shape[0]}"
    )
    assert result["sigma2_eps"].shape == (m,), "sigma2_eps shape"
    assert result["sigma2_u"].shape == (m,), "sigma2_u shape"
    assert result["n_grid"] == m, "n_grid value"


# ---------------------------------------------------------------------------
# test_multi_famm
# ---------------------------------------------------------------------------


def test_multi_famm_returns_4_key_dict():
    """multi_famm returns a dict with exactly the 4 documented keys."""
    data1 = DATA                                           # (20, 30)
    data2 = RNG.standard_normal((N_TOTAL, N_GRID))        # (20, 30)
    result = famm.multi_famm([data1, data2], SUBJECT_IDS)
    assert isinstance(result, dict), "Expected a dict"
    assert set(result.keys()) == MULTI_FAMM_KEYS, (
        f"Key mismatch: got {set(result.keys())}, expected {MULTI_FAMM_KEYS}"
    )


def test_multi_famm_components_list_length():
    """multi_famm components list has length D (one per input variable)."""
    D = 2
    data_list = [RNG.standard_normal((N_TOTAL, N_GRID)) for _ in range(D)]
    result = famm.multi_famm(data_list, SUBJECT_IDS)
    assert result["n_dims"] == D, f"Expected n_dims={D}, got {result['n_dims']}"
    assert len(result["components"]) == D, (
        f"Expected {D} components, got {len(result['components'])}"
    )


def test_multi_famm_each_component_is_14_key_dict():
    """Each element of multi_famm 'components' has the 14 dense_flmm keys."""
    data_list = [DATA, RNG.standard_normal((N_TOTAL, N_GRID))]
    result = famm.multi_famm(data_list, SUBJECT_IDS)
    for i, comp in enumerate(result["components"]):
        assert isinstance(comp, dict), f"components[{i}] is not a dict"
        assert set(comp.keys()) == DENSE_FLMM_KEYS, (
            f"components[{i}] key mismatch: got {set(comp.keys())}"
        )


def test_multi_famm_stacked_shapes():
    """multi_famm stacked_fitted and stacked_residuals have correct shapes."""
    D = 2
    data_list = [DATA, RNG.standard_normal((N_TOTAL, N_GRID))]
    result = famm.multi_famm(data_list, SUBJECT_IDS)
    m = N_GRID
    expected_rows = N_TOTAL * D
    assert result["stacked_fitted"].shape == (expected_rows, m), (
        f"stacked_fitted shape: expected ({expected_rows}, {m}), "
        f"got {result['stacked_fitted'].shape}"
    )
    assert result["stacked_residuals"].shape == (expected_rows, m), (
        f"stacked_residuals shape: expected ({expected_rows}, {m}), "
        f"got {result['stacked_residuals'].shape}"
    )
