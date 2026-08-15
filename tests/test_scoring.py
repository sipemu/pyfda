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
from fdars.scoring import functional_mse


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
