"""Tests for fdars.regression — concurrent_regression and functional_glm bindings.

Covers:
  - TestConcurrentRegression: varying-coefficient functional regression (REGR-01, REGR-03)
  - TestFunctionalGlm: exponential-family GLM via FPC scores (REGR-02, REGR-03)
  - TestRegressionImportPaths: both import styles work for both new functions
"""

import numpy as np
import pytest
from fdars import regression


class TestConcurrentRegression:
    """Tests for fdars.regression.concurrent_regression."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_data(n=8, m=12, p=1, seed=42):
        """Build synthetic (n, m) functional data with p predictors."""
        rng = np.random.default_rng(seed)
        response = rng.standard_normal((n, m))
        predictors = [rng.standard_normal((n, m)) for _ in range(p)]
        return response, predictors

    # ------------------------------------------------------------------
    # Task 1 — smoke test (tracer)
    # ------------------------------------------------------------------

    def test_smoke(self):
        """Single-predictor smoke: dict keys and all output shapes are correct."""
        n, m = 8, 12
        response, predictors = self._make_data(n=n, m=m, p=1)
        result = regression.concurrent_regression(
            predictors, response, argvals=None, bandwidth=0.2, kernel="gaussian"
        )
        assert set(result.keys()) == {
            "beta_curve",
            "intercept",
            "fitted",
            "residuals",
            "argvals",
        }
        assert result["fitted"].shape == (n, m)
        assert result["beta_curve"].shape == (1, m), (
            f"Expected beta_curve (1, {m}), got {result['beta_curve'].shape}"
        )
        assert result["intercept"].shape == (m,), (
            f"Expected intercept ({m},), got {result['intercept'].shape}"
        )
        assert result["argvals"].shape == (m,), (
            f"Expected argvals ({m},), got {result['argvals'].shape}"
        )
        assert result["residuals"].shape == (n, m), (
            f"Expected residuals ({n}, {m}), got {result['residuals'].shape}"
        )

    # ------------------------------------------------------------------
    # Task 2 — beta_curve (p, m) transposition guard + determinism + guards
    # ------------------------------------------------------------------

    def test_beta_curve_shape_p3(self):
        """beta_curve must be (p, m) for p=3, n=10 — not (n, m)."""
        n, m, p = 10, 12, 3
        assert n != p, "fixture must have p != n so shape is unambiguous"
        response, predictors = self._make_data(n=n, m=m, p=p)
        result = regression.concurrent_regression(predictors, response)
        assert result["beta_curve"].shape == (p, m), (
            f"Expected (p, m) = ({p}, {m}), got {result['beta_curve'].shape}"
        )

    def test_beta_curve_rows_are_curves(self):
        """Each row of beta_curve has length m, matching the returned argvals."""
        n, m, p = 10, 12, 3
        response, predictors = self._make_data(n=n, m=m, p=p)
        result = regression.concurrent_regression(predictors, response)
        beta = result["beta_curve"]
        argvals = result["argvals"]
        assert beta.shape[0] == p
        assert beta.shape[1] == len(argvals)
        for j in range(p):
            assert beta[j, :].shape == (m,)

    def test_determinism(self):
        """Two calls with identical inputs return byte-identical arrays."""
        response, predictors = self._make_data(n=10, m=12, p=2)
        r1 = regression.concurrent_regression(predictors, response)
        r2 = regression.concurrent_regression(predictors, response)
        for key in ("beta_curve", "fitted", "residuals"):
            assert np.array_equal(r1[key], r2[key]), f"{key} not deterministic"

    def test_residuals_consistency(self):
        """residuals == response - fitted element-wise (tight allclose)."""
        n, m = 10, 12
        response, predictors = self._make_data(n=n, m=m, p=2)
        result = regression.concurrent_regression(predictors, response)
        expected = response - result["fitted"]
        assert np.allclose(result["residuals"], expected, atol=1e-10, rtol=1e-10)

    def test_empty_predictors_raises(self):
        """Empty predictor list raises ValueError."""
        response, _ = self._make_data(n=8, m=12, p=1)
        with pytest.raises(ValueError):
            regression.concurrent_regression([], response)

    def test_bad_bandwidth_raises(self):
        """bandwidth <= 0 raises ValueError."""
        response, predictors = self._make_data(n=8, m=12, p=1)
        with pytest.raises(ValueError):
            regression.concurrent_regression(predictors, response, bandwidth=0.0)
        with pytest.raises(ValueError):
            regression.concurrent_regression(predictors, response, bandwidth=-1.0)

    def test_mismatched_predictor_raises(self):
        """Predictor array with wrong shape raises ValueError."""
        n, m = 8, 12
        response, _ = self._make_data(n=n, m=m, p=1)
        rng = np.random.default_rng(99)
        bad_predictor = [rng.standard_normal((n + 1, m))]  # wrong n
        with pytest.raises(ValueError):
            regression.concurrent_regression(bad_predictor, response)


class TestFunctionalGlm:
    """Tests for fdars.regression.functional_glm."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_data(n=20, m=16, seed=42):
        """Build smooth functional data matrix (n, m)."""
        rng = np.random.default_rng(seed)
        t = np.linspace(0, 1, m)
        # Smooth functional data: sine waves with noise
        data = np.array([
            np.sin(2 * np.pi * t * (1 + 0.1 * rng.standard_normal()))
            + 0.1 * rng.standard_normal(m)
            for _ in range(n)
        ])
        return data, t

    # ------------------------------------------------------------------
    # Task 3 — Gaussian smoke test
    # ------------------------------------------------------------------

    def test_gaussian_smoke(self):
        """Gaussian family: 15 keys, no fpca, finite fitted_values, family round-trip."""
        n, m = 20, 16
        data, _ = self._make_data(n=n, m=m)
        rng = np.random.default_rng(0)
        response = data @ rng.standard_normal(m) + 0.1 * rng.standard_normal(n)
        result = regression.functional_glm(data, response, family="gaussian")

        expected_keys = {
            "intercept", "beta_t", "beta_se", "gamma", "fitted_values",
            "linear_predictors", "ncomp", "coefficients", "std_errors",
            "log_likelihood", "deviance", "iterations", "aic", "bic", "family",
        }
        assert set(result.keys()) == expected_keys, (
            f"Key mismatch: got {set(result.keys())}"
        )
        assert "fpca" not in result, "Embedded fpca must not be exposed to Python"
        assert len(result["fitted_values"]) == n
        assert np.all(np.isfinite(result["fitted_values"]))
        assert result["family"] == "gaussian"

    # ------------------------------------------------------------------
    # Task 4 — family coverage + domain guards
    # ------------------------------------------------------------------

    def test_binomial_family(self):
        """Binomial: fitted_values in (0, 1), all finite, family correct, IRLS converges."""
        n, m = 30, 16
        data, _ = self._make_data(n=n, m=m, seed=1)
        rng = np.random.default_rng(202)  # distinct seed from data generation (seed=1)
        # Binary response: half 0.0, half 1.0
        response = np.array([0.0] * (n // 2) + [1.0] * (n - n // 2))
        rng.shuffle(response)
        result = regression.functional_glm(
            data, response, family="binomial", n_comp=3, max_iter=50
        )
        fv = result["fitted_values"]
        assert np.all(np.isfinite(fv)), "fitted_values must be finite"
        assert np.all(fv > 0) and np.all(fv < 1), (
            f"Binomial fitted_values must be in (0, 1), got min={fv.min():.4f} max={fv.max():.4f}"
        )
        assert result["family"] == "binomial"
        assert result["iterations"] <= 50, (
            f"IRLS did not converge within max_iter=50 (iterations={result['iterations']})"
        )

    def test_poisson_family(self):
        """Poisson: fitted_values > 0, all finite, family string correct."""
        n, m = 30, 16
        data, _ = self._make_data(n=n, m=m, seed=2)
        rng = np.random.default_rng(2)
        # Non-negative integer counts
        response = rng.poisson(lam=3.0, size=n).astype(float)
        result = regression.functional_glm(
            data, response, family="poisson", n_comp=3, max_iter=50
        )
        fv = result["fitted_values"]
        assert np.all(np.isfinite(fv)), "fitted_values must be finite"
        assert np.all(fv > 0), (
            f"Poisson fitted_values must be > 0, got min={fv.min():.4f}"
        )
        assert result["family"] == "poisson"

    def test_gamma_family(self):
        """Gamma (inverse link): fitted_values > 0, all finite, family string correct."""
        n, m = 30, 16
        data, _ = self._make_data(n=n, m=m, seed=3)
        rng = np.random.default_rng(3)
        # Strictly positive response
        response = rng.gamma(shape=2.0, scale=1.0, size=n)
        result = regression.functional_glm(
            data, response, family="gamma", n_comp=3, max_iter=50
        )
        fv = result["fitted_values"]
        assert np.all(np.isfinite(fv)), "fitted_values must be finite"
        assert np.all(fv > 0), (
            f"Gamma fitted_values must be > 0, got min={fv.min():.4f}"
        )
        assert result["family"] == "gamma"

    def test_invalid_family(self):
        """Unknown family string raises ValueError mentioning accepted families."""
        n, m = 20, 16
        data, _ = self._make_data(n=n, m=m)
        rng = np.random.default_rng(0)
        response = rng.standard_normal(n)
        with pytest.raises(ValueError, match="binomial|poisson|gamma|gaussian"):
            regression.functional_glm(data, response, family="tweedie")

    def test_binomial_domain_guard(self):
        """Binomial with y=0.5 raises ValueError."""
        n, m = 20, 16
        data, _ = self._make_data(n=n, m=m)
        response = np.full(n, 0.5)
        with pytest.raises(ValueError):
            regression.functional_glm(data, response, family="binomial")

    def test_poisson_domain_guard(self):
        """Poisson with negative response raises ValueError."""
        n, m = 20, 16
        data, _ = self._make_data(n=n, m=m)
        response = np.ones(n)
        response[0] = -1.0
        with pytest.raises(ValueError):
            regression.functional_glm(data, response, family="poisson")

    def test_gamma_domain_guard(self):
        """Gamma with y=0 raises ValueError."""
        n, m = 20, 16
        data, _ = self._make_data(n=n, m=m)
        response = np.ones(n)
        response[0] = 0.0
        with pytest.raises(ValueError):
            regression.functional_glm(data, response, family="gamma")


class TestRegressionImportPaths:
    """Both import paths resolve to callables for the new functions."""

    def test_concurrent_regression_attribute_access(self):
        """fdars.regression.concurrent_regression is callable."""
        assert callable(regression.concurrent_regression)

    def test_functional_glm_attribute_access(self):
        """fdars.regression.functional_glm is callable."""
        assert callable(regression.functional_glm)

    def test_concurrent_regression_direct_import(self):
        """from fdars.regression import concurrent_regression succeeds."""
        from fdars.regression import concurrent_regression  # noqa: F401
        assert callable(concurrent_regression)

    def test_functional_glm_direct_import(self):
        """from fdars.regression import functional_glm succeeds."""
        from fdars.regression import functional_glm  # noqa: F401
        assert callable(functional_glm)
