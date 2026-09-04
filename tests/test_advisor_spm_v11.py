"""Tests for Phase 72 (v11.0) SPM advisor branches — mfpca and spe_multivariate.

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests cover:
  - TestMfpca: mfpca dict branch (has_mfpca, grounded diagnostics)
  - TestSpeMultivariate: spe_multivariate naked array branch (has_spe_multivariate)
  - TestSpmPhase1Regression: spm_phase1 dict path still works (regression guard)

ADV-01 Phase 72.
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
# TestMfpca — mfpca dict branch (ADV-01 Phase 72)
# ---------------------------------------------------------------------------

class TestMfpca:
    """Verify the has_mfpca branch of _build_spm_diagnostics."""

    @pytest.fixture(scope="class")
    def mfpca_result(self):
        """Build a real mfpca result (6-key PyDict)."""
        from fdars import spm
        rng = np.random.default_rng(42)
        n, m1, m2 = 20, 10, 12
        # Two functional variables
        var1 = rng.standard_normal((n, m1))
        var2 = rng.standard_normal((n, m2))
        return spm.mfpca([var1, var2], ncomp=3)

    def test_mfpca_method_field(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        assert diag["method"] == "spm"

    def test_mfpca_has_mfpca_true(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        assert diag["has_mfpca"] is True

    def test_mfpca_ncomp_is_int(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        assert isinstance(diag["mfpca_ncomp"], int)
        assert diag["mfpca_ncomp"] == 3  # ncomp=3 in fixture

    def test_mfpca_n_obs_is_int(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        assert isinstance(diag["mfpca_n_obs"], int)
        assert diag["mfpca_n_obs"] == 20  # n=20 in fixture

    def test_mfpca_n_variables_is_int(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        assert isinstance(diag["mfpca_n_variables"], int)
        assert diag["mfpca_n_variables"] == 2  # P=2 variables in fixture

    def test_mfpca_eigenvalues_is_list_of_float(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        ev = diag["mfpca_eigenvalues"]
        assert isinstance(ev, list)
        assert len(ev) == 3  # ncomp=3
        assert all(isinstance(v, float) for v in ev)

    def test_mfpca_variance_explained_cumulative_is_list(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        vc = diag["mfpca_variance_explained_cumulative"]
        assert isinstance(vc, list)
        assert len(vc) == 3
        # Last entry should be ~1.0 (cumulative of all components)
        assert abs(vc[-1] - 1.0) < 1e-6

    def test_mfpca_no_numpy(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        check_no_numpy(diag)

    def test_mfpca_json_serialisable(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        json.dumps(diag, sort_keys=True)

    def test_mfpca_determinism(self, mfpca_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(mfpca_result, method="spm")
        d2 = build_diagnostics(mfpca_result, method="spm")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_mfpca_spm_phase1_fields_none(self, mfpca_result):
        """spm_phase1-specific fields (t2/spe) must be None for mfpca results."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        # mfpca dict lacks t2/spe/t2_limit/spe_limit keys
        assert diag.get("t2_max") is None
        assert diag.get("spe_max") is None

    def test_mfpca_ncomp_eigenvalues_spm_phase1_fields_none(self, mfpca_result):
        """spm_phase1 ncomp and eigenvalues fields must be None for mfpca (WR-01).

        mfpca carries eigenvalue info under mfpca_ncomp / mfpca_eigenvalues.
        The spm_phase1 sentinel fields diag['ncomp'] and diag['eigenvalues']
        must be None to avoid duplicating mfpca data in the wrong slots.
        """
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mfpca_result, method="spm")
        assert diag["ncomp"] is None, (
            "diag['ncomp'] (spm_phase1 field) must be None for mfpca input (WR-01)"
        )
        assert diag["eigenvalues"] is None, (
            "diag['eigenvalues'] (spm_phase1 field) must be None for mfpca input (WR-01)"
        )
        assert diag["variance_explained_cumulative"] is None, (
            "diag['variance_explained_cumulative'] (spm_phase1) must be None for mfpca (WR-01)"
        )
        # mfpca-specific fields must still carry the real values
        assert diag["mfpca_ncomp"] == 3
        assert isinstance(diag["mfpca_eigenvalues"], list)
        assert diag["mfpca_variance_explained_cumulative"] is not None


# ---------------------------------------------------------------------------
# TestSpeMultivariate — naked array branch (ADV-01 Phase 72)
# ---------------------------------------------------------------------------

class TestSpeMultivariate:
    """Verify the has_spe_multivariate branch of _build_spm_diagnostics."""

    @pytest.fixture(scope="class")
    def spe_mv_result(self):
        """Build a real spe_multivariate result (naked 1-D numpy array)."""
        from fdars import spm
        rng = np.random.default_rng(42)
        n, m1, m2 = 15, 10, 8
        # Need standardized and reconstructed vars (same shape)
        std_vars = [rng.standard_normal((n, m1)), rng.standard_normal((n, m2))]
        # Reconstruct as slight perturbation to keep SPE values non-negative
        recon_vars = [v + 0.1 * rng.standard_normal(v.shape) for v in std_vars]
        argvals_list = [np.linspace(0.0, 1.0, m1), np.linspace(0.0, 1.0, m2)]
        return spm.spe_multivariate(std_vars, recon_vars, argvals_list)

    def test_spe_mv_method_field(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert diag["method"] == "spm"

    def test_spe_mv_has_spe_multivariate_true(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert diag["has_spe_multivariate"] is True

    def test_spe_mv_n_obs_is_int(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert isinstance(diag["spe_mv_n_obs"], int)
        assert diag["spe_mv_n_obs"] == 15  # n=15 in fixture

    def test_spe_mv_max_is_float(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert isinstance(diag["spe_mv_max"], float)
        assert diag["spe_mv_max"] >= 0.0

    def test_spe_mv_mean_is_float(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert isinstance(diag["spe_mv_mean"], float)
        assert diag["spe_mv_mean"] >= 0.0

    def test_spe_mv_all_nonneg_is_true(self, spe_mv_result):
        """spe_multivariate values are non-negative SPE statistics."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert isinstance(diag["spe_mv_all_nonneg"], bool)
        assert diag["spe_mv_all_nonneg"] is True

    def test_spe_mv_no_numpy(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        check_no_numpy(diag)

    def test_spe_mv_json_serialisable(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        json.dumps(diag, sort_keys=True)

    def test_spe_mv_determinism(self, spe_mv_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(spe_mv_result, method="spm")
        d2 = build_diagnostics(spe_mv_result, method="spm")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_spe_mv_mfpca_fields_none(self, spe_mv_result):
        """mfpca-specific fields must be None for a naked array result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(spe_mv_result, method="spm")
        assert diag.get("mfpca_ncomp") is None
        assert diag.get("mfpca_eigenvalues") is None


# ---------------------------------------------------------------------------
# TestSpmPhase1Regression — existing spm_phase1 dict path (regression guard)
# ---------------------------------------------------------------------------

class TestSpmPhase1Regression:
    """Verify the spm_phase1 dict path still works after the new branches are added."""

    @pytest.fixture(scope="class")
    def phase1_result(self):
        from fdars import spm
        rng = np.random.default_rng(42)
        n, m = 30, 15
        data = rng.standard_normal((n, m))
        argvals = np.linspace(0.0, 1.0, m)
        return spm.spm_phase1(data, argvals)

    def test_phase1_method_field(self, phase1_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        assert diag["method"] == "spm"

    def test_phase1_has_mfpca_false(self, phase1_result):
        """spm_phase1 result must not trigger has_mfpca."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        assert diag["has_mfpca"] is False

    def test_phase1_has_spe_multivariate_false(self, phase1_result):
        """spm_phase1 result (dict) must not trigger has_spe_multivariate."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        assert diag["has_spe_multivariate"] is False

    def test_phase1_t2_max_is_float(self, phase1_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        assert isinstance(diag["t2_max"], float)

    def test_phase1_ncomp_is_int(self, phase1_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        assert isinstance(diag["ncomp"], int)

    def test_phase1_no_numpy(self, phase1_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        check_no_numpy(diag)

    def test_phase1_json_serialisable(self, phase1_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(phase1_result, method="spm")
        json.dumps(diag, sort_keys=True)
