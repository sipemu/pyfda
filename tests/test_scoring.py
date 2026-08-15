"""Tests for fdars.scoring — prediction-scoring metrics submodule (STAT-03).

Covers:
- Namespace: both import paths (from fdars.scoring import ... and fdars.scoring.<fn>).
- functional_mse: identical-curve == 0 (hand-checked); known-offset analytic value.
- functional_mae: identical-curve == 0.
- functional_mape: identical-curve ~= 0; ValueError for near-zero y_true.
- functional_msle: identical-curve == 0; ValueError for values <= -1.
- functional_explained_variance: identical-curve == 1.0.
- Argument-order contract: MAPE zero-guard fires on y_true (first arg), not y_pred.
"""

import numpy as np
import pytest

import fdars
from fdars.scoring import (
    functional_mse,
    functional_mae,
    functional_mape,
    functional_msle,
    functional_explained_variance,
)


# ---------------------------------------------------------------------------
# Namespace tests
# ---------------------------------------------------------------------------

class TestNamespace:
    def test_direct_import_functional_mse(self):
        """from fdars.scoring import functional_mse resolves."""
        from fdars.scoring import functional_mse as fn
        assert callable(fn)

    def test_attribute_access_functional_mse(self):
        """fdars.scoring.functional_mse attribute access resolves."""
        assert callable(fdars.scoring.functional_mse)

    def test_mse_importable(self):
        """functional_mse importable from fdars.scoring."""
        assert callable(functional_mse)

    def test_all_five_metrics_accessible_via_attribute(self):
        """All 5 metrics reachable via fdars.scoring attribute access."""
        names = [
            "functional_mae",
            "functional_mse",
            "functional_mape",
            "functional_msle",
            "functional_explained_variance",
        ]
        for name in names:
            fn = getattr(fdars.scoring, name)
            assert callable(fn), f"fdars.scoring.{name} is not callable"

    def test_all_five_importable_from_module(self):
        """All 5 metrics importable from fdars.scoring."""
        fns = [
            functional_mae,
            functional_mse,
            functional_mape,
            functional_msle,
            functional_explained_variance,
        ]
        for fn in fns:
            assert callable(fn)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def grid_and_data():
    """2 curves on a 50-point linspace over [0, 1]."""
    m = 50
    argvals = np.linspace(0.0, 1.0, m)
    y_true = np.ones((2, m), dtype=np.float64)
    y_true[0] = np.sin(np.pi * argvals)
    y_true[1] = np.cos(np.pi * argvals)
    return argvals, y_true


# ---------------------------------------------------------------------------
# functional_mse
# ---------------------------------------------------------------------------

class TestFunctionalMSE:
    def test_identical_curves_zero(self):
        """functional_mse(X, X) == approx(0.0) — hand-checked truth."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y = np.array([[np.sin(np.pi * t) for t in argvals],
                      [np.cos(np.pi * t) for t in argvals]])
        result = functional_mse(y, y, argvals)
        assert result == pytest.approx(0.0, abs=1e-12)

    def test_known_offset_analytic(self):
        """Constant offset c over [0,1] — MSE = c^2 * integral of 1 over [0,1] = c^2."""
        # y_true = 0, y_pred = c (constant) over n=1 curve on [0,1]
        # (y_true - y_pred)^2 = c^2 everywhere
        # ∫ c^2 dt over [0,1] = c^2
        m = 200
        c = 3.0
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.zeros((1, m))
        y_pred = np.full((1, m), c)
        result = functional_mse(y_true, y_pred, argvals)
        # Simpson's rule on 200 points is very accurate for a constant
        assert result == pytest.approx(c ** 2, rel=1e-6)

    def test_two_curves_known_offset(self):
        """Two curves with constant offsets c1, c2: MSE = (c1^2 + c2^2) / 2."""
        m = 200
        argvals = np.linspace(0.0, 1.0, m)
        c1, c2 = 2.0, 4.0
        y_true = np.zeros((2, m))
        y_pred = np.array([np.full(m, c1), np.full(m, c2)])
        result = functional_mse(y_true, y_pred, argvals)
        expected = (c1 ** 2 + c2 ** 2) / 2.0
        assert result == pytest.approx(expected, rel=1e-6)

    def test_attribute_path_gives_same_result(self):
        """fdars.scoring.functional_mse gives identical result."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y = np.ones((2, m))
        r1 = functional_mse(y, y, argvals)
        r2 = fdars.scoring.functional_mse(y, y, argvals)
        assert r1 == pytest.approx(r2)


# ---------------------------------------------------------------------------
# functional_mae
# ---------------------------------------------------------------------------

class TestFunctionalMAE:
    def test_identical_curves_zero(self):
        """functional_mae(X, X) == approx(0.0)."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y = np.ones((2, m))
        result = functional_mae(y, y, argvals)
        assert result == pytest.approx(0.0, abs=1e-12)

    def test_known_offset_analytic(self):
        """Constant offset c over [0,1] — MAE = c."""
        m = 200
        c = 2.5
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.zeros((1, m))
        y_pred = np.full((1, m), c)
        result = functional_mae(y_true, y_pred, argvals)
        assert result == pytest.approx(c, rel=1e-6)

    def test_asymmetric_positive(self):
        """MAE is non-negative for non-identical curves."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.ones((1, m))
        y_pred = np.zeros((1, m))
        result = functional_mae(y_true, y_pred, argvals)
        assert result > 0.0


# ---------------------------------------------------------------------------
# functional_mape
# ---------------------------------------------------------------------------

class TestFunctionalMAPE:
    def test_identical_non_zero_curves_zero(self):
        """functional_mape(X, X) == approx(0.0) for non-zero y_true."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        # Use y_true > 0 everywhere to avoid the near-zero guard
        y = np.ones((2, m)) * 5.0
        result = functional_mape(y, y, argvals)
        assert result == pytest.approx(0.0, abs=1e-12)

    def test_raises_for_zero_y_true(self):
        """MAPE raises ValueError when y_true contains a near-zero value."""
        m = 20
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.zeros((1, m))  # all zeros → near-zero guard fires
        y_pred = np.ones((1, m))
        with pytest.raises(ValueError):
            functional_mape(y_true, y_pred, argvals)

    def test_raises_on_y_true_not_y_pred(self):
        """Zero-guard fires on y_true (first arg), not y_pred.

        y_true = 0, y_pred = 1 → ValueError (zero in y_true).
        y_true = 1, y_pred = 0 → valid (no near-zero in y_true).
        """
        m = 20
        argvals = np.linspace(0.0, 1.0, m)
        # near-zero in y_true → ValueError
        with pytest.raises(ValueError):
            functional_mape(np.zeros((1, m)), np.ones((1, m)), argvals)
        # y_pred = 0, y_true = 1 → should NOT raise
        result = functional_mape(np.ones((1, m)), np.zeros((1, m)), argvals)
        assert result >= 0.0

    def test_known_ratio(self):
        """y_true=4, y_pred=5: |error|/|y_true| = 0.25 over [0,1] → MAPE=0.25."""
        m = 200
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.full((1, m), 4.0)
        y_pred = np.full((1, m), 5.0)
        result = functional_mape(y_true, y_pred, argvals)
        assert result == pytest.approx(0.25, rel=1e-6)


# ---------------------------------------------------------------------------
# functional_msle
# ---------------------------------------------------------------------------

class TestFunctionalMSLE:
    def test_identical_curves_zero(self):
        """functional_msle(X, X) == approx(0.0) for valid values."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y = np.ones((2, m)) * 2.0  # all positive, well above -1
        result = functional_msle(y, y, argvals)
        assert result == pytest.approx(0.0, abs=1e-12)

    def test_raises_for_y_true_le_minus_one(self):
        """MSLE raises ValueError when y_true contains a value <= -1."""
        m = 20
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.full((1, m), -1.5)  # below -1 threshold
        y_pred = np.ones((1, m))
        with pytest.raises(ValueError):
            functional_msle(y_true, y_pred, argvals)

    def test_raises_for_y_pred_le_minus_one(self):
        """MSLE raises ValueError when y_pred contains a value <= -1."""
        m = 20
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.ones((1, m))
        y_pred = np.full((1, m), -1.5)
        with pytest.raises(ValueError):
            functional_msle(y_true, y_pred, argvals)

    def test_known_log_difference(self):
        """y_true=3, y_pred=1 over [0,1]: log_diff = ln(4)-ln(2) = ln(2), MSLE = ln(2)^2."""
        m = 200
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.full((1, m), 3.0)
        y_pred = np.full((1, m), 1.0)
        result = functional_msle(y_true, y_pred, argvals)
        expected = np.log(2.0) ** 2
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# functional_explained_variance
# ---------------------------------------------------------------------------

class TestFunctionalExplainedVariance:
    def test_identical_curves_one(self):
        """functional_explained_variance(X, X) == approx(1.0)."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y = np.array([[np.sin(np.pi * t) for t in argvals],
                      [np.cos(np.pi * t) for t in argvals]])
        result = functional_explained_variance(y, y, argvals)
        assert result == pytest.approx(1.0, abs=1e-10)

    def test_value_le_one(self):
        """Explained variance is always ≤ 1.0."""
        m = 50
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.array([[np.sin(np.pi * t) for t in argvals]])
        y_pred = np.zeros((1, m))  # worst possible prediction
        result = functional_explained_variance(y_true, y_pred, argvals)
        assert result <= 1.0

    def test_constant_pred_non_trivial(self):
        """Zero prediction of sinusoidal y_true gives EV < 1.0."""
        m = 100
        argvals = np.linspace(0.0, 1.0, m)
        y_true = np.array([[np.sin(2 * np.pi * t) for t in argvals]])
        y_pred = np.zeros((1, m))  # predicting zero everywhere
        result = functional_explained_variance(y_true, y_pred, argvals)
        assert result < 1.0  # definitely not a perfect prediction
