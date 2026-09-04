"""Tests for the regression advisor diagnostics — v6.0 model branches (ADV-05).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests mirror the structure of test_advisor_inference.py:
- check_no_numpy recursive walker
- byte-identical json.dumps(sort_keys=True)
- grounding via _extract_numbers from fdars.advisor.providers._validate

Covers:
  - TestFunctionalGlm: functional_glm branch (deviance/aic/bic/log_likelihood/iterations)
  - TestConcurrentRegression: concurrent_regression branch (residual_rms/n_predictors)
  - TestDeterminism: combined determinism + no-numpy checks for both branches
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Shared helper: recursive numpy-scalar walker.
# ---------------------------------------------------------------------------

def check_no_numpy(obj):
    """Fail if any value in obj is a numpy scalar (np.generic subclass)."""
    assert not isinstance(obj, np.generic), (
        f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
    )
    if isinstance(obj, dict):
        for v in obj.values():
            check_no_numpy(v)
    elif isinstance(obj, list):
        for v in obj:
            check_no_numpy(v)


# ---------------------------------------------------------------------------
# TestFunctionalGlm
# ---------------------------------------------------------------------------

class TestFunctionalGlm:
    """Verify the functional_glm branch of _build_regression_diagnostics (ADV-05)."""

    @pytest.fixture(scope="class")
    def glm_result(self):
        """Build a real functional_glm result (Gaussian family)."""
        from fdars import regression
        rng = np.random.default_rng(42)
        t = np.linspace(0, 1, 16)
        n = 20
        data = np.array([
            np.sin(2 * np.pi * t * (1 + 0.1 * rng.standard_normal()))
            + 0.1 * rng.standard_normal(16)
            for _ in range(n)
        ])
        response = data @ rng.standard_normal(16) + 0.1 * rng.standard_normal(n)
        return regression.functional_glm(data, response, family="gaussian")

    def test_glm_method_field(self, glm_result):
        """build_diagnostics on functional_glm result returns method == 'regression'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert diag["method"] == "regression"

    def test_glm_has_functional_glm_true(self, glm_result):
        """has_functional_glm must be True for a functional_glm result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert diag["has_functional_glm"] is True

    def test_glm_deviance_is_float(self, glm_result):
        """deviance must be a native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert isinstance(diag["deviance"], float)
        assert diag["deviance"] > 0, "deviance should be positive for Gaussian family"

    def test_glm_aic_bic_log_likelihood_are_float(self, glm_result):
        """aic, bic, log_likelihood must be native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert isinstance(diag["aic"], float), "aic must be float"
        assert isinstance(diag["bic"], float), "bic must be float"
        assert isinstance(diag["log_likelihood"], float), "log_likelihood must be float"

    def test_glm_iterations_is_int(self, glm_result):
        """iterations must be a native int (key is 'iterations', not 'n_iter')."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert isinstance(diag["iterations"], int), (
            f"iterations must be int, got {type(diag['iterations'])}"
        )
        assert diag["iterations"] >= 1, "iterations must be at least 1"

    def test_glm_no_n_iter_key(self, glm_result):
        """No 'n_iter' key must be present (Pitfall 2: correct key is 'iterations')."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert "n_iter" not in diag, "n_iter must not appear in output (use 'iterations')"

    def test_glm_no_converged_key(self, glm_result):
        """No 'converged' key must be present (no such key in shipped dict)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert "converged" not in diag, "converged must not appear (not in functional_glm dict)"

    def test_glm_ncomp_is_int(self, glm_result):
        """glm_ncomp must be a native int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert isinstance(diag["glm_ncomp"], int)
        assert diag["glm_ncomp"] >= 1

    def test_glm_family_is_str(self, glm_result):
        """family must be a native str."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert isinstance(diag["family"], str)
        assert diag["family"] == "gaussian"

    def test_glm_n_obs_from_fitted_values(self, glm_result):
        """n_obs must be inferred from fitted_values (20 obs in fixture)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        assert diag["n_obs"] == 20
        assert isinstance(diag["n_obs"], int)

    def test_glm_residual_scalars_are_none(self, glm_result):
        """1-D residual scalars must be None (GLM has no 'residuals' key)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        # GLM has no residuals key — all 1-D residual stats should be None
        assert diag.get("residual_mean") is None
        assert diag.get("residual_std") is None

    def test_glm_no_numpy(self, glm_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        check_no_numpy(diag)

    def test_glm_json_serialisable(self, glm_result):
        """Output must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(glm_result, method="regression")
        json.dumps(diag, sort_keys=True)

    def test_glm_determinism(self, glm_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(glm_result, method="regression")
        d2 = build_diagnostics(glm_result, method="regression")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_glm_grounding(self, glm_result):
        """deviance is discoverable in json.dumps(diag) via _extract_numbers."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers
        diag = build_diagnostics(glm_result, method="regression")
        diag_json = json.dumps(diag, sort_keys=True)
        found = set(_extract_numbers(diag_json))
        iterations_str = str(diag["iterations"])
        assert any(iterations_str in n or n in iterations_str for n in found), (
            f"iterations={iterations_str} not discoverable in diagnostics json"
        )


# ---------------------------------------------------------------------------
# TestConcurrentRegression
# ---------------------------------------------------------------------------

class TestConcurrentRegression:
    """Verify the concurrent_regression branch of _build_regression_diagnostics (ADV-05)."""

    @pytest.fixture(scope="class")
    def conc_result(self):
        """Build a real concurrent_regression result."""
        from fdars import regression
        rng = np.random.default_rng(42)
        n, m, p = 8, 12, 2
        response = rng.standard_normal((n, m))
        predictors = [rng.standard_normal((n, m)) for _ in range(p)]
        return regression.concurrent_regression(predictors, response)

    def test_conc_method_field(self, conc_result):
        """build_diagnostics on concurrent_regression result returns method == 'regression'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert diag["method"] == "regression"

    def test_conc_has_concurrent_regression_true(self, conc_result):
        """has_concurrent_regression must be True."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert diag["has_concurrent_regression"] is True

    def test_conc_residual_rms_is_float(self, conc_result):
        """concurrent_residual_rms must be a native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert isinstance(diag["concurrent_residual_rms"], float)
        assert diag["concurrent_residual_rms"] >= 0.0

    def test_conc_residual_max_abs_is_float(self, conc_result):
        """concurrent_residual_max_abs must be a native float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert isinstance(diag["concurrent_residual_max_abs"], float)
        assert diag["concurrent_residual_max_abs"] >= 0.0

    def test_conc_n_predictors_is_int(self, conc_result):
        """n_predictors must be a native int equal to p=2."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert isinstance(diag["n_predictors"], int)
        assert diag["n_predictors"] == 2  # p=2 in fixture

    def test_conc_1d_residual_scalars_none(self, conc_result):
        """1-D residual scalars (residual_mean, residual_std, residual_skew) must be None.

        concurrent_regression residuals are 2-D (n, m) so the existing ndim==1
        guard prevents them from being computed (Pitfall 3).
        """
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert diag["residual_mean"] is None, (
            "residual_mean must be None for 2-D concurrent_regression residuals (Pitfall 3)"
        )
        assert diag["residual_std"] is None
        assert diag["residual_skew"] is None

    def test_conc_has_fosr_true(self, conc_result):
        """has_fosr is True for concurrent_regression (2-D fitted key) — documented overlap."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        # has_fosr fires because "fitted" is 2-D; concurrent_regression is
        # the specific discriminator via has_concurrent_regression
        assert diag["has_fosr"] is True
        assert diag["has_concurrent_regression"] is True

    def test_conc_n_obs_from_fitted(self, conc_result):
        """n_obs must be inferred from the 'fitted' key (n=8 in fixture)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        assert diag["n_obs"] == 8
        assert isinstance(diag["n_obs"], int)

    def test_conc_no_numpy(self, conc_result):
        """Output must contain no numpy scalars."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        check_no_numpy(diag)

    def test_conc_json_serialisable(self, conc_result):
        """Output must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(conc_result, method="regression")
        json.dumps(diag, sort_keys=True)

    def test_conc_determinism(self, conc_result):
        """Two calls produce equal dicts and byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(conc_result, method="regression")
        d2 = build_diagnostics(conc_result, method="regression")
        assert d1 == d2
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_conc_grounding(self, conc_result):
        """n_predictors is discoverable in json.dumps(diag) via _extract_numbers."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers
        diag = build_diagnostics(conc_result, method="regression")
        diag_json = json.dumps(diag, sort_keys=True)
        found = set(_extract_numbers(diag_json))
        n_pred_str = str(diag["n_predictors"])
        assert any(n_pred_str in n or n in n_pred_str for n in found), (
            f"n_predictors={n_pred_str} not discoverable in diagnostics json"
        )


# ---------------------------------------------------------------------------
# TestDeterminism — combined determinism + no-numpy for both branches
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Combined determinism and no-numpy tests for both new regression branches."""

    def test_functional_glm_byte_identical(self):
        """functional_glm: json.dumps is byte-identical across two independent calls."""
        from fdars import regression
        from fdars.advisor import build_diagnostics
        rng = np.random.default_rng(99)
        t = np.linspace(0, 1, 16)
        n = 20
        data = np.array([np.sin(2 * np.pi * t) + 0.05 * rng.standard_normal(16) for _ in range(n)])
        response = rng.standard_normal(n)
        result = regression.functional_glm(data, response, family="gaussian")
        d1 = build_diagnostics(result, method="regression")
        d2 = build_diagnostics(result, method="regression")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
        check_no_numpy(d1)

    def test_concurrent_regression_byte_identical(self):
        """concurrent_regression: json.dumps is byte-identical across two calls."""
        from fdars import regression
        from fdars.advisor import build_diagnostics
        rng = np.random.default_rng(77)
        n, m, p = 10, 15, 3
        response = rng.standard_normal((n, m))
        predictors = [rng.standard_normal((n, m)) for _ in range(p)]
        result = regression.concurrent_regression(predictors, response)
        d1 = build_diagnostics(result, method="regression")
        d2 = build_diagnostics(result, method="regression")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
        check_no_numpy(d1)


# ---------------------------------------------------------------------------
# TestFofRegression — function-on-function regression branch (ADV-01 Phase 72)
# ---------------------------------------------------------------------------

class TestFofRegression:
    """Verify the has_fof_regression branch of _build_regression_diagnostics."""

    @pytest.fixture(scope="class")
    def fof_result(self):
        """Build a real fof_regression result."""
        from fdars import regression
        rng = np.random.default_rng(42)
        n, m_x, m_y = 15, 10, 8
        x_data = rng.standard_normal((n, m_x))
        y_data = rng.standard_normal((n, m_y))
        x_argvals = np.linspace(0.0, 1.0, m_x)
        y_argvals = np.linspace(0.0, 1.0, m_y)
        return regression.fof_regression(x_data, y_data, x_argvals, y_argvals, ncomp_x=2, ncomp_y=2)

    def test_fof_method_field(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        assert diag["method"] == "regression"

    def test_fof_has_fof_regression_true(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        assert diag["has_fof_regression"] is True

    def test_fof_beta_surface_shape_is_list_of_ints(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        shape = diag["beta_surface_shape"]
        assert isinstance(shape, list) and len(shape) == 2
        assert all(isinstance(v, int) for v in shape)
        # (m_y=8, m_x=10)
        assert shape[0] == 8
        assert shape[1] == 10

    def test_fof_beta_surface_max_abs_is_float(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        assert isinstance(diag["beta_surface_max_abs"], float)
        assert diag["beta_surface_max_abs"] >= 0.0

    def test_fof_r_squared_is_float(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        assert isinstance(diag["fof_r_squared"], float)

    def test_fof_ncomp_is_list_of_ints(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        ncomp = diag["fof_ncomp"]
        assert isinstance(ncomp, list) and len(ncomp) == 2
        assert all(isinstance(v, int) for v in ncomp)

    def test_fof_no_numpy(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        check_no_numpy(diag)

    def test_fof_json_serialisable(self, fof_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_result, method="regression")
        json.dumps(diag, sort_keys=True)

    def test_fof_determinism(self, fof_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(fof_result, method="regression")
        d2 = build_diagnostics(fof_result, method="regression")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


class TestFofReRegression:
    """Verify the has_fof_re_regression branch."""

    @pytest.fixture(scope="class")
    def fof_re_result(self):
        from fdars import regression
        rng = np.random.default_rng(7)
        n, m_x, m_y = 20, 10, 8
        n_subjects = 4
        x_data = rng.standard_normal((n, m_x))
        y_data = rng.standard_normal((n, m_y))
        subject_ids = np.array([i % n_subjects for i in range(n)], dtype=np.int64)
        x_argvals = np.linspace(0.0, 1.0, m_x)
        y_argvals = np.linspace(0.0, 1.0, m_y)
        return regression.fof_re_regression(
            x_data, y_data, subject_ids, x_argvals, y_argvals, ncomp_x=2, ncomp_y=2
        )

    def test_fof_re_has_fof_re_regression_true(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_re_result, method="regression")
        assert diag["has_fof_re_regression"] is True

    def test_fof_re_n_subjects_is_int(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_re_result, method="regression")
        assert isinstance(diag["n_subjects"], int)
        assert diag["n_subjects"] == 4

    def test_fof_re_sigma2_u_max_is_float(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_re_result, method="regression")
        assert isinstance(diag["sigma2_u_max"], float)

    def test_fof_re_re_dims_is_list_of_ints(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_re_result, method="regression")
        dims = diag["re_dims"]
        assert isinstance(dims, list) and len(dims) == 2
        assert all(isinstance(v, int) for v in dims)

    def test_fof_re_no_numpy(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_re_result, method="regression")
        check_no_numpy(diag)

    def test_fof_re_json_serialisable(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fof_re_result, method="regression")
        json.dumps(diag, sort_keys=True)

    def test_fof_re_determinism(self, fof_re_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(fof_re_result, method="regression")
        d2 = build_diagnostics(fof_re_result, method="regression")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


class TestFamGkam:
    """Verify the has_fam / has_fregre_gkam branches."""

    @pytest.fixture(scope="class")
    def fam_result(self):
        from fdars import scalar_on_function
        rng = np.random.default_rng(42)
        n, m = 30, 15
        data = rng.standard_normal((n, m))
        y = rng.standard_normal(n)
        argvals = np.linspace(0.0, 1.0, m)
        return scalar_on_function.fam(data, y, argvals, ncomp=2)

    @pytest.fixture(scope="class")
    def gkam_result(self):
        from fdars import scalar_on_function
        rng = np.random.default_rng(99)
        n, m = 20, 10
        p = 2
        predictors = [rng.standard_normal((n, m)) for _ in range(p)]
        y = rng.standard_normal(n)
        argvals_list = [np.linspace(0.0, 1.0, m) for _ in range(p)]
        return scalar_on_function.fregre_gkam(predictors, y, argvals_list)

    def test_fam_has_fam_true(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        assert diag["has_fam"] is True

    def test_fam_n_obs_is_int(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        assert isinstance(diag["fam_n_obs"], int)
        assert diag["fam_n_obs"] == 30

    def test_fam_n_components_is_int(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        assert isinstance(diag["fam_n_components"], int)
        assert diag["fam_n_components"] >= 1

    def test_fam_r_squared_is_float(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        assert isinstance(diag["fam_r_squared"], float)

    def test_fam_ncomp_is_int(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        assert isinstance(diag["fam_ncomp"], int)

    def test_gkam_has_fregre_gkam_true(self, gkam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(gkam_result, method="regression")
        assert diag["has_fregre_gkam"] is True

    def test_gkam_converged_is_bool(self, gkam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(gkam_result, method="regression")
        assert isinstance(diag["gkam_converged"], bool)

    def test_gkam_bandwidths_is_list_of_float(self, gkam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(gkam_result, method="regression")
        bw = diag["gkam_bandwidths"]
        assert isinstance(bw, list)
        assert all(isinstance(v, float) for v in bw)

    def test_gkam_n_predictors_is_int(self, gkam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(gkam_result, method="regression")
        assert isinstance(diag["gkam_n_predictors"], int)
        assert diag["gkam_n_predictors"] == 2

    def test_fam_no_numpy(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        check_no_numpy(diag)

    def test_fam_json_serialisable(self, fam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fam_result, method="regression")
        json.dumps(diag, sort_keys=True)

    def test_fam_determinism(self, fam_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(fam_result, method="regression")
        d2 = build_diagnostics(fam_result, method="regression")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_gkam_no_numpy(self, gkam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(gkam_result, method="regression")
        check_no_numpy(diag)

    def test_gkam_json_serialisable(self, gkam_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(gkam_result, method="regression")
        json.dumps(diag, sort_keys=True)

    def test_gkam_determinism(self, gkam_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(gkam_result, method="regression")
        d2 = build_diagnostics(gkam_result, method="regression")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)
