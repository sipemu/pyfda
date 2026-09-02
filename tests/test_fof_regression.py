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
