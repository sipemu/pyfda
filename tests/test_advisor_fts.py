"""Tests for fts advisor diagnostics — Phase 72 (ADV-01).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Covers all five fts result shapes:
  - ftsm (functional time series model)
  - stationarity_test
  - functional_acf
  - dpca (dynamic PCA)
  - fplsr (functional partial least squares regression)
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
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def fts_data():
    """Non-square (N=40, M=25) seeded random data for all fts tests."""
    rng = np.random.default_rng(42)
    N, M = 40, 25
    data = rng.standard_normal((N, M))
    argvals = np.linspace(0.0, 1.0, M)
    return data, argvals


# ---------------------------------------------------------------------------
# TestFtsmAspect — ftsm result shape
# ---------------------------------------------------------------------------

class TestFtsmAspect:
    """Verify build_diagnostics on ftsm result (the FTSM model shape)."""

    @pytest.fixture(scope="class")
    def ftsm_result(self, fts_data):
        from fdars import fts
        data, argvals = fts_data
        return fts.ftsm(data, argvals, ncomp=3)

    def test_ftsm_method_field(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        assert diag["method"] == "fts"

    def test_ftsm_has_ftsm_true(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        assert diag["has_ftsm"] is True

    def test_ftsm_ncomp_equals_3(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        assert isinstance(diag["ncomp"], int)
        assert diag["ncomp"] == 3

    def test_ftsm_n_ar_models_equals_ncomp(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        assert isinstance(diag["n_ar_models"], int)
        assert diag["n_ar_models"] == 3

    def test_ftsm_json_serializable(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        json.dumps(diag, sort_keys=True)  # must not raise

    def test_ftsm_no_numpy_scalars(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        check_no_numpy(diag)

    def test_ftsm_deterministic(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(ftsm_result, method="fts")
        d2 = build_diagnostics(ftsm_result, method="fts")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_ftsm_fitted_rmse_nonneg(self, ftsm_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(ftsm_result, method="fts")
        assert isinstance(diag["fitted_rmse"], float)
        assert diag["fitted_rmse"] >= 0.0


# ---------------------------------------------------------------------------
# TestStationarityAspect — stationarity_test result shape
# ---------------------------------------------------------------------------

class TestStationarityAspect:
    """Verify build_diagnostics on stationarity_test result."""

    @pytest.fixture(scope="class")
    def stat_result(self, fts_data):
        from fdars import fts
        data, argvals = fts_data
        return fts.stationarity_test(data, argvals, n_perm=20, seed=42)

    def test_stationarity_method_field(self, stat_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(stat_result, method="fts")
        assert diag["method"] == "fts"

    def test_stationarity_has_stationarity_true(self, stat_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(stat_result, method="fts")
        assert diag["has_stationarity"] is True

    def test_stationarity_p_value_in_range(self, stat_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(stat_result, method="fts")
        assert isinstance(diag["stationarity_p_value"], float)
        assert 0.0 <= diag["stationarity_p_value"] <= 1.0

    def test_stationarity_n_perm_is_int(self, stat_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(stat_result, method="fts")
        assert isinstance(diag["n_perm"], int)
        assert diag["n_perm"] == 20

    def test_stationarity_json_serializable(self, stat_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(stat_result, method="fts")
        json.dumps(diag, sort_keys=True)

    def test_stationarity_no_numpy_scalars(self, stat_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(stat_result, method="fts")
        check_no_numpy(diag)

    def test_stationarity_deterministic(self, stat_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(stat_result, method="fts")
        d2 = build_diagnostics(stat_result, method="fts")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


# ---------------------------------------------------------------------------
# TestAcfAspect — functional_acf result shape
# ---------------------------------------------------------------------------

class TestAcfAspect:
    """Verify build_diagnostics on functional_acf result."""

    @pytest.fixture(scope="class")
    def acf_result(self, fts_data):
        from fdars import fts
        data, argvals = fts_data
        return fts.functional_acf(data, argvals, max_lag=5, n_sim=20, ci=0.95, seed=42)

    def test_acf_method_field(self, acf_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(acf_result, method="fts")
        assert diag["method"] == "fts"

    def test_acf_has_acf_true(self, acf_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(acf_result, method="fts")
        assert diag["has_acf"] is True

    def test_acf_n_lags_is_int(self, acf_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(acf_result, method="fts")
        assert isinstance(diag["n_lags"], int)
        assert diag["n_lags"] == 5

    def test_acf_json_serializable(self, acf_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(acf_result, method="fts")
        json.dumps(diag, sort_keys=True)

    def test_acf_no_numpy_scalars(self, acf_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(acf_result, method="fts")
        check_no_numpy(diag)

    def test_acf_deterministic(self, acf_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(acf_result, method="fts")
        d2 = build_diagnostics(acf_result, method="fts")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


# ---------------------------------------------------------------------------
# TestDpcaAspect — dpca result shape
# ---------------------------------------------------------------------------

class TestDpcaAspect:
    """Verify build_diagnostics on dpca result."""

    @pytest.fixture(scope="class")
    def dpca_result(self, fts_data):
        from fdars import fts
        data, argvals = fts_data
        return fts.dpca(data, argvals, ncomp=2)

    def test_dpca_method_field(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        assert diag["method"] == "fts"

    def test_dpca_has_dpca_true(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        assert diag["has_dpca"] is True

    def test_dpca_ncomp_is_int(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        assert isinstance(diag["dpca_ncomp"], int)
        assert diag["dpca_ncomp"] == 2

    def test_dpca_filter_lag_is_int(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        assert isinstance(diag["filter_lag"], int)

    def test_dpca_json_serializable(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        json.dumps(diag, sort_keys=True)

    def test_dpca_no_numpy_scalars(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        check_no_numpy(diag)

    def test_dpca_deterministic(self, dpca_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(dpca_result, method="fts")
        d2 = build_diagnostics(dpca_result, method="fts")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_dpca_eigenvalues_is_list_of_floats(self, dpca_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(dpca_result, method="fts")
        assert isinstance(diag["dpca_eigenvalues"], list)
        assert all(isinstance(v, float) for v in diag["dpca_eigenvalues"])


# ---------------------------------------------------------------------------
# TestFplsrAspect — fplsr result shape
# ---------------------------------------------------------------------------

class TestFplsrAspect:
    """Verify build_diagnostics on fplsr result."""

    @pytest.fixture(scope="class")
    def fplsr_result(self, fts_data):
        from fdars import fts
        data, argvals = fts_data
        return fts.fplsr(data, argvals, ncomp=2)

    def test_fplsr_method_field(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fplsr_result, method="fts")
        assert diag["method"] == "fts"

    def test_fplsr_has_fplsr_true(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fplsr_result, method="fts")
        assert diag["has_fplsr"] is True

    def test_fplsr_ncomp_is_int(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fplsr_result, method="fts")
        assert isinstance(diag["fplsr_ncomp"], int)
        assert diag["fplsr_ncomp"] == 2

    def test_fplsr_fitted_rmse_nonneg(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fplsr_result, method="fts")
        assert isinstance(diag["fplsr_fitted_rmse"], float)
        assert diag["fplsr_fitted_rmse"] >= 0.0

    def test_fplsr_json_serializable(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fplsr_result, method="fts")
        json.dumps(diag, sort_keys=True)

    def test_fplsr_no_numpy_scalars(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(fplsr_result, method="fts")
        check_no_numpy(diag)

    def test_fplsr_deterministic(self, fplsr_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(fplsr_result, method="fts")
        d2 = build_diagnostics(fplsr_result, method="fts")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


# ---------------------------------------------------------------------------
# TestFtsGuardSync — method string validation
# ---------------------------------------------------------------------------

class TestFtsGuardSync:
    """Verify 'fts' and 'frechet' are listed in the Supported error message."""

    def test_unsupported_sentinel_lists_fts_and_frechet(self):
        """build_diagnostics ValueError for unknown method must list 'fts' AND 'frechet'."""
        from fdars.advisor import build_diagnostics
        with pytest.raises(ValueError) as exc_info:
            build_diagnostics({}, "__sentinel__")
        msg = str(exc_info.value)
        assert "'fts'" in msg, f"'fts' not in Supported list: {msg}"
        assert "'frechet'" in msg, f"'frechet' not in Supported list: {msg}"
