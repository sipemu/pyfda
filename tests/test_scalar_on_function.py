"""Tests for fdars.scalar_on_function — scalar-on-function additive/selection regression.

Covers:
- fam (Functional Additive Model)
- fregre_gsam (Generalised Structured Additive Model)
- fregre_gkam (Generalised Kernel Additive Model, multi-predictor)
- variable_selection (group-lasso variable selection)
- model_selection_ncomp (AIC/BIC/GCV component selection)

Non-square fixtures per project conventions: N=30, M=20 (n_obs ≠ n_points).
Multi-predictor: 2 predictors with M1=20, M2=15 (different grid sizes).
"""

import numpy as np
import pytest

import fdars.scalar_on_function as sof

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_rng = np.random.default_rng(42)

# Single-predictor fixture: (N=30, M=20) — non-square
_N, _M = 30, 20
_ARGVALS = np.linspace(0.0, 1.0, _M)
_DATA = _rng.standard_normal((_N, _M))
_Y = np.sin(np.pi * _DATA.mean(axis=1)) + 0.1 * _rng.standard_normal(_N)

# Second predictor: M2=15 (different grid size)
_M2 = 15
_DATA2 = _rng.standard_normal((_N, _M2))
_ARGVALS2 = np.linspace(0.0, 1.0, _M2)

# Verify fixture is genuinely non-square
assert _N != _M and _N != _M2 and _M != _M2, "Fixture must be non-square"


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------


def test_import_smoke():
    """fdars.scalar_on_function must import and expose all five functions."""
    assert callable(sof.fam)
    assert callable(sof.fregre_gsam)
    assert callable(sof.fregre_gkam)
    assert callable(sof.variable_selection)
    assert callable(sof.model_selection_ncomp)


# ---------------------------------------------------------------------------
# fam
# ---------------------------------------------------------------------------


def test_fam_returns_correct_keys_and_shapes():
    """fam on (30, 20) fixture: fitted_values.shape==(30,), component_fits is a list."""
    result = sof.fam(_DATA, _Y, _ARGVALS)
    expected_keys = {
        "fitted_values",
        "residuals",
        "component_fits",
        "intercept",
        "bandwidths",
        "ncomp",
        "r_squared",
    }
    assert set(result.keys()) == expected_keys, f"Unexpected keys: {set(result.keys())}"
    assert "fpca" not in result, "fpca should not be exposed"
    assert result["fitted_values"].shape == (_N,), (
        f"fitted_values shape wrong: {result['fitted_values'].shape}"
    )
    assert result["residuals"].shape == (_N,), (
        f"residuals shape wrong: {result['residuals'].shape}"
    )
    assert isinstance(result["component_fits"], list), (
        "component_fits must be a Python list"
    )
    assert isinstance(result["intercept"], float)
    assert result["ncomp"] >= 1, "ncomp must be at least 1"
    assert 0.0 <= result["r_squared"] <= 1.0


# ---------------------------------------------------------------------------
# fregre_gsam
# ---------------------------------------------------------------------------


def test_fregre_gsam_matches_fam_keys():
    """fregre_gsam (single predictor) returns the same 7 keys as fam."""
    result = sof.fregre_gsam(_DATA, _Y, _ARGVALS)
    fam_keys = {
        "fitted_values",
        "residuals",
        "component_fits",
        "intercept",
        "bandwidths",
        "ncomp",
        "r_squared",
    }
    assert set(result.keys()) == fam_keys, f"Unexpected keys: {set(result.keys())}"
    assert result["fitted_values"].shape == (_N,)
    assert isinstance(result["component_fits"], list)


# ---------------------------------------------------------------------------
# fregre_gkam
# ---------------------------------------------------------------------------


def test_fregre_gkam_two_predictors():
    """fregre_gkam with [(30,20),(30,15)] returns converged as bool, bandwidths.shape==(2,)."""
    result = sof.fregre_gkam(
        [_DATA, _DATA2],
        _Y,
        [_ARGVALS, _ARGVALS2],
    )
    expected_keys = {
        "fitted_values",
        "residuals",
        "component_fits",
        "intercept",
        "bandwidths",
        "iterations",
        "converged",
        "r_squared",
    }
    assert set(result.keys()) == expected_keys, f"Unexpected keys: {set(result.keys())}"
    assert isinstance(result["converged"], bool), (
        f"converged must be bool, got {type(result['converged'])}"
    )
    assert result["bandwidths"].shape == (2,), (
        f"bandwidths shape must be (2,), got {result['bandwidths'].shape}"
    )
    assert result["fitted_values"].shape == (_N,)
    assert isinstance(result["component_fits"], list)
    assert len(result["component_fits"]) == 2, (
        "component_fits must have one entry per predictor"
    )


# ---------------------------------------------------------------------------
# variable_selection
# ---------------------------------------------------------------------------


def test_variable_selection_group_lasso():
    """variable_selection with group_lasso returns active_predictors.shape==(2,)."""
    result = sof.variable_selection(
        [_DATA, _DATA2],
        _Y,
        [_ARGVALS, _ARGVALS2],
        penalty="group_lasso",
    )
    expected_keys = {
        "active_predictors",
        "coefficients",
        "fitted_values",
        "residuals",
        "intercept",
        "lambda",
        "r_squared",
        "iterations",
        "converged",
    }
    assert set(result.keys()) == expected_keys, f"Unexpected keys: {set(result.keys())}"
    assert "fpcas" not in result, "fpcas should not be exposed"
    assert result["active_predictors"].shape == (2,), (
        f"active_predictors shape must be (2,), got {result['active_predictors'].shape}"
    )
    assert result["active_predictors"].dtype == bool, (
        f"active_predictors must be bool dtype, got {result['active_predictors'].dtype}"
    )
    assert isinstance(result["coefficients"], list), "coefficients must be a list"
    # Each element in coefficients is a numpy 1D array of floats
    assert all(hasattr(c, "shape") for c in result["coefficients"]), (
        "each coefficient entry must be a numpy array"
    )


def test_variable_selection_penalty_ls():
    """variable_selection with penalty='ls' (OLS, no penalisation) succeeds."""
    result = sof.variable_selection(
        [_DATA, _DATA2],
        _Y,
        [_ARGVALS, _ARGVALS2],
        penalty="ls",
    )
    assert result["active_predictors"].shape == (2,)


def test_variable_selection_invalid_penalty_raises():
    """variable_selection with an invalid penalty raises ValueError."""
    with pytest.raises(ValueError, match="penalty must be"):
        sof.variable_selection(
            [_DATA, _DATA2],
            _Y,
            [_ARGVALS, _ARGVALS2],
            penalty="group_mcp",
        )


# ---------------------------------------------------------------------------
# model_selection_ncomp
# ---------------------------------------------------------------------------


def test_model_selection_ncomp_gcv():
    """model_selection_ncomp returns best_ncomp >= 1 and criteria as a list of tuples."""
    result = sof.model_selection_ncomp(_DATA, _Y, criterion="gcv")
    assert "best_ncomp" in result and "criteria" in result
    assert result["best_ncomp"] >= 1, (
        f"best_ncomp must be >= 1, got {result['best_ncomp']}"
    )
    assert isinstance(result["criteria"], list), "criteria must be a list"
    assert len(result["criteria"]) > 0
    # Each entry is a (ncomp, aic, bic, gcv) tuple
    first = result["criteria"][0]
    assert len(first) == 4, f"Each criteria entry must be a 4-tuple, got {len(first)}"


def test_model_selection_ncomp_aic():
    """model_selection_ncomp with criterion='aic' returns best_ncomp >= 1."""
    result = sof.model_selection_ncomp(_DATA, _Y, criterion="aic")
    assert result["best_ncomp"] >= 1


def test_model_selection_ncomp_bic():
    """model_selection_ncomp with criterion='bic' returns best_ncomp >= 1."""
    result = sof.model_selection_ncomp(_DATA, _Y, criterion="bic")
    assert result["best_ncomp"] >= 1
