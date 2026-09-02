"""Tests for fdars.regression FOF functions — Phase 68, Plans 01-02.

Covers (plan 01):
- Import smoke: fdars.regression exposes fof_regression
- fof_regression end-to-end on non-square (N=30, MX=25, MY=18) fixture
- beta_surface shape (MY, MX) = (18, 25) — transposition guard (MX != MY catches swap)
- Returned dict key-set excludes fpca_x / fpca_y
- Shape assertions for all returned arrays

Plan 02 will APPEND predict_fof, fof_cv, fof_re_regression, predict_fof_re tests
to this same file.
"""

from __future__ import annotations

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Non-square fixture constants (REQUIRED: all three dims distinct)
# ---------------------------------------------------------------------------

N, MX, MY = 30, 25, 18   # n_obs=30, m_x=25, m_y=18 — all three deliberately different
assert N != MX and N != MY and MX != MY, (
    "Fixture must have three distinct dims to catch row/col swap bugs"
)

# ---------------------------------------------------------------------------
# Shared fixture construction
# ---------------------------------------------------------------------------

_rng = np.random.default_rng(42)
_x_argvals = np.linspace(0.0, 1.0, MX)
_y_argvals = np.linspace(0.0, 1.0, MY)

# FOF training data: X drives Y via integral coupling
_x_data = _rng.standard_normal((N, MX))
# Y constructed to have a true FOF signal
_x_scores = _x_data @ np.sin(np.pi * _x_argvals[:, None]).reshape(-1, 1)
_y_data = (
    _x_scores @ np.cos(np.pi * _y_argvals[None, :])
    + 0.1 * _rng.standard_normal((N, MY))
)
assert _x_data.shape == (N, MX), f"Expected ({N}, {MX}), got {_x_data.shape}"
assert _y_data.shape == (N, MY), f"Expected ({N}, {MY}), got {_y_data.shape}"

# new_x for predict tests (n_new=10, same m_x=25)
_new_x = _rng.standard_normal((10, MX))

# subject_ids for RE: 5 subjects × 6 obs each
_subject_ids = np.array([i // 6 for i in range(N)], dtype=np.int64)
assert len(np.unique(_subject_ids)) == 5

# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------


def test_import_regression_module() -> None:
    """fdars.regression must expose fof_regression after plan 01."""
    import fdars.regression as reg  # noqa: F401

    assert callable(reg.fof_regression), "fof_regression must be callable"


# ---------------------------------------------------------------------------
# fof_regression end-to-end
# ---------------------------------------------------------------------------


def test_fof_regression_returns_dict() -> None:
    """fof_regression must return a dict on the non-square fixture."""
    import fdars.regression as reg

    result = reg.fof_regression(
        _x_data, _y_data, _x_argvals, _y_argvals, ncomp_x=3, ncomp_y=3
    )
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"


def test_fof_regression_key_set() -> None:
    """Returned dict must have exactly the 9 documented keys; fpca_x/fpca_y excluded."""
    import fdars.regression as reg

    result = reg.fof_regression(
        _x_data, _y_data, _x_argvals, _y_argvals, ncomp_x=3, ncomp_y=3
    )
    expected_keys = {
        "intercept",
        "beta_surface",
        "fitted",
        "residuals",
        "r_squared_t",
        "r_squared",
        "ncomp_x",
        "ncomp_y",
        "coef_matrix",
    }
    assert set(result) == expected_keys, (
        f"Key mismatch.\n  Got:      {sorted(result)}\n"
        f"  Expected: {sorted(expected_keys)}"
    )
    # Explicitly confirm no FPCA internals leaked
    assert "fpca_x" not in result, "fpca_x must not appear in the returned dict"
    assert "fpca_y" not in result, "fpca_y must not appear in the returned dict"


def test_fof_regression_shapes() -> None:
    """Shape assertions — the load-bearing transposition guard.

    beta_surface must be (MY, MX) = (18, 25).
    A transposition bug would produce (MX, MY) = (25, 18), which this test catches
    because MX != MY (25 != 18).
    """
    import fdars.regression as reg

    result = reg.fof_regression(
        _x_data, _y_data, _x_argvals, _y_argvals, ncomp_x=3, ncomp_y=3
    )

    # --- Primary transposition guard ---
    assert result["beta_surface"].shape == (MY, MX), (
        f"beta_surface shape must be (MY, MX) = ({MY}, {MX}), "
        f"got {result['beta_surface'].shape} — rows=response grid, cols=predictor grid"
    )

    # --- Supporting shape assertions ---
    assert result["fitted"].shape == (N, MY), (
        f"fitted shape must be (N, MY) = ({N}, {MY}), got {result['fitted'].shape}"
    )
    assert result["residuals"].shape == (N, MY), (
        f"residuals shape must be (N, MY) = ({N}, {MY}), got {result['residuals'].shape}"
    )
    assert result["intercept"].shape == (MY,), (
        f"intercept shape must be (MY,) = ({MY},), got {result['intercept'].shape}"
    )
    assert result["r_squared_t"].shape == (MY,), (
        f"r_squared_t shape must be (MY,) = ({MY},), got {result['r_squared_t'].shape}"
    )
    # coef_matrix shape: (ncomp_x, ncomp_y)
    assert result["coef_matrix"].shape == (3, 3), (
        f"coef_matrix shape must be (ncomp_x, ncomp_y) = (3, 3), "
        f"got {result['coef_matrix'].shape}"
    )

    # --- Scalar fields ---
    assert isinstance(result["r_squared"], float), (
        f"r_squared must be float, got {type(result['r_squared'])}"
    )
    assert isinstance(result["ncomp_x"], int), (
        f"ncomp_x must be int, got {type(result['ncomp_x'])}"
    )
    assert isinstance(result["ncomp_y"], int), (
        f"ncomp_y must be int, got {type(result['ncomp_y'])}"
    )


# ---------------------------------------------------------------------------
# Plan 02 tests: predict_fof, fof_cv, fof_re_regression, predict_fof_re
# ---------------------------------------------------------------------------


def test_predict_fof_shape() -> None:
    """predict_fof returns numpy array of shape (10, MY) = (10, 18)."""
    import fdars.regression as reg

    pred = reg.predict_fof(
        _x_data, _y_data, _new_x, _x_argvals, _y_argvals, ncomp_x=3, ncomp_y=3
    )
    assert hasattr(pred, "shape"), f"predict_fof must return an array, got {type(pred)}"
    assert pred.shape == (10, MY), (
        f"predict_fof shape must be (10, MY) = (10, {MY}), got {pred.shape}"
    )


def test_fof_cv() -> None:
    """fof_cv returns a dict with candidates, cv_errors, optimal, min_cv_mse."""
    import fdars.regression as reg

    result = reg.fof_cv(
        _x_data, _y_data, _x_argvals, _y_argvals,
        ncomp_x_max=3, ncomp_y_max=3, n_folds=5, seed=42,
    )
    assert isinstance(result, dict), f"fof_cv must return dict, got {type(result)}"

    # Key presence
    assert "candidates" in result, "fof_cv result must have 'candidates'"
    assert "cv_errors" in result, "fof_cv result must have 'cv_errors'"
    assert "optimal" in result, "fof_cv result must have 'optimal'"
    assert "min_cv_mse" in result, "fof_cv result must have 'min_cv_mse'"

    # candidates: list of 2-tuples of ints
    assert isinstance(result["candidates"], list), (
        f"candidates must be a list, got {type(result['candidates'])}"
    )
    assert len(result["candidates"]) > 0, "candidates must be non-empty"
    for cand in result["candidates"]:
        assert isinstance(cand, tuple) and len(cand) == 2, (
            f"each candidate must be a 2-tuple, got {cand!r}"
        )
        assert isinstance(cand[0], int) and isinstance(cand[1], int), (
            f"candidate elements must be ints, got {type(cand[0])}, {type(cand[1])}"
        )

    # optimal: a 2-tuple of ints
    opt = result["optimal"]
    assert isinstance(opt, tuple) and len(opt) == 2, (
        f"optimal must be a 2-tuple, got {opt!r}"
    )
    assert isinstance(opt[0], int) and isinstance(opt[1], int), (
        f"optimal elements must be ints, got {type(opt[0])}, {type(opt[1])}"
    )

    # min_cv_mse: positive float
    assert isinstance(result["min_cv_mse"], float), (
        f"min_cv_mse must be float, got {type(result['min_cv_mse'])}"
    )
    assert result["min_cv_mse"] > 0, (
        f"min_cv_mse must be > 0, got {result['min_cv_mse']}"
    )


def test_fof_re_regression_shapes() -> None:
    """fof_re_regression returns correct shapes for RE-specific fields."""
    import fdars.regression as reg

    result = reg.fof_re_regression(
        _x_data, _y_data, _subject_ids, _x_argvals, _y_argvals,
        ncomp_x=3, ncomp_y=3,
    )
    assert isinstance(result, dict), f"fof_re_regression must return dict, got {type(result)}"

    # random_effects: (n_subjects, m_y) = (5, 18)
    assert result["random_effects"].shape == (5, MY), (
        f"random_effects shape must be (5, MY) = (5, {MY}), got {result['random_effects'].shape}"
    )
    # sigma2_u: (ncomp_y,) = (3,)
    assert result["sigma2_u"].shape == (3,), (
        f"sigma2_u shape must be (ncomp_y,) = (3,), got {result['sigma2_u'].shape}"
    )
    # n_subjects: 5 distinct groups
    assert result["n_subjects"] == 5, (
        f"n_subjects must be 5, got {result['n_subjects']}"
    )
    # Standard FOF fields present and correctly shaped
    assert result["fitted"].shape == (N, MY), (
        f"fitted shape must be (N, MY) = ({N}, {MY}), got {result['fitted'].shape}"
    )
    assert result["beta_surface"].shape == (MY, MX), (
        f"beta_surface shape must be (MY, MX) = ({MY}, {MX}), got {result['beta_surface'].shape}"
    )
    assert isinstance(result["sigma2_eps"], float), (
        f"sigma2_eps must be float, got {type(result['sigma2_eps'])}"
    )
    # fpca internals must NOT be exposed
    assert "fpca_x" not in result, "fpca_x must not appear in fof_re_regression result"
    assert "fpca_y" not in result, "fpca_y must not appear in fof_re_regression result"


def test_predict_fof_re_shape() -> None:
    """predict_fof_re returns numpy array of shape (10, MY) = (10, 18)."""
    import fdars.regression as reg

    pred = reg.predict_fof_re(
        _x_data, _y_data, _subject_ids, _new_x, _x_argvals, _y_argvals,
        ncomp_x=3, ncomp_y=3,
    )
    assert hasattr(pred, "shape"), f"predict_fof_re must return an array, got {type(pred)}"
    assert pred.shape == (10, MY), (
        f"predict_fof_re shape must be (10, MY) = (10, {MY}), got {pred.shape}"
    )


def test_subject_id_validation() -> None:
    """Subject-id validation: wrong length and single group both raise ValueError."""
    import fdars.regression as reg

    # Wrong length: 3 ids for 30 observations
    with pytest.raises(ValueError, match="subject_ids length"):
        reg.fof_re_regression(
            _x_data,
            _y_data,
            np.array([0, 1, 2], dtype=np.int64),
            _x_argvals,
            _y_argvals,
        )

    # Single group: all observations in group 0
    with pytest.raises(ValueError, match="at least 2 distinct subjects"):
        reg.fof_re_regression(
            _x_data,
            _y_data,
            np.zeros(N, dtype=np.int64),
            _x_argvals,
            _y_argvals,
        )

    # predict_fof_re also validates (wrong length)
    with pytest.raises(ValueError, match="subject_ids length"):
        reg.predict_fof_re(
            _x_data,
            _y_data,
            np.array([0, 1, 2], dtype=np.int64),
            _new_x,
            _x_argvals,
            _y_argvals,
        )


def test_fof_error_guards() -> None:
    """Error guards: ncomp_x=0 and n_folds > n both raise ValueError."""
    import fdars.regression as reg

    # ncomp_x=0 is invalid — upstream raises InvalidParameter → ValueError
    with pytest.raises(ValueError):
        reg.fof_regression(_x_data, _y_data, _x_argvals, _y_argvals, ncomp_x=0)

    # n_folds > n is invalid — upstream raises InvalidDimension → ValueError
    with pytest.raises(ValueError):
        reg.fof_cv(
            _x_data, _y_data, _x_argvals, _y_argvals,
            ncomp_x_max=2, ncomp_y_max=2, n_folds=N + 1,
        )
