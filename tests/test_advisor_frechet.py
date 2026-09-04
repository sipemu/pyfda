"""Tests for fdars.advisor frechet aspect diagnostics — Phase 72-02 (ADV-01).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Covers: frechet_mean (spd array), frechet_anova, frechet_global_reg, frechet_local_reg.
"""
from __future__ import annotations

import json

import numpy as np
import pytest
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Helpers
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
# Shared density fixtures (mirrors test_frechet.py)
# ---------------------------------------------------------------------------

N, M = 40, 50       # n_obs=40 densities on m=50 grid points
N_OUT = 10          # prediction output points
N_PRED = 2          # predictor dimension p=2

_RNG = np.random.default_rng(42)
_ARGVALS = np.linspace(-3.0, 3.0, M)
_PREDICTORS = _RNG.standard_normal((N, N_PRED))

_RESPONSES = np.zeros((N, M))
for _i in range(N):
    _mu = _PREDICTORS[_i, 0]
    _raw = norm.pdf(_ARGVALS, loc=_mu, scale=0.8)
    _RESPONSES[_i] = _raw / np.trapezoid(_raw, _ARGVALS)

_XOUT = _RNG.standard_normal((N_OUT, N_PRED))
_GROUP_LABELS = np.array([i // (N // 3) for i in range(N)], dtype=np.int64)
_GROUP_LABELS = np.clip(_GROUP_LABELS, 0, 2)

# SPD fixtures (mirrors test_frechet.py _make_spd + _OBJECTS_SPD)
_RNG2 = np.random.default_rng(0)
D_SPD = 3


def _make_spd(rng, d):
    A = rng.standard_normal((d, d))
    return A @ A.T + np.eye(d) * 0.1


_OBJECTS_SPD = [_make_spd(_RNG2, D_SPD) for _ in range(5)]


# ===========================================================================
# TestFrechetMeanAspect — frechet_mean returns a numpy array (not a dict)
# ===========================================================================

class TestFrechetMeanAspect:
    """Verify the frechet_mean array path in the advisor builder."""

    @pytest.fixture(scope="class")
    def mean_result(self):
        from fdars import frechet
        return frechet.frechet_mean(_OBJECTS_SPD, space="spd", d=D_SPD)

    def test_json_serializable(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        json.dumps(diag, sort_keys=True)  # must not raise

    def test_no_numpy_scalars(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        check_no_numpy(diag)

    def test_deterministic(self, mean_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(mean_result, method="frechet")
        d2 = build_diagnostics(mean_result, method="frechet")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_method_field(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        assert diag["method"] == "frechet"

    def test_has_frechet_mean_true(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        assert diag["has_frechet_mean"] is True

    def test_frechet_mean_ndim_is_2(self, mean_result):
        """SPD mean is a 2D matrix, so ndim == 2."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        assert diag["frechet_mean_ndim"] == 2

    def test_frechet_mean_dim(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        assert diag["frechet_mean_dim"] == D_SPD

    def test_frechet_mean_trace_is_float(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        assert isinstance(diag["frechet_mean_trace"], float)

    def test_anova_flags_false(self, mean_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(mean_result, method="frechet")
        assert diag["has_anova"] is False
        assert diag["has_global_reg"] is False
        assert diag["has_local_reg"] is False


# ===========================================================================
# TestFrechetAnovaAspect — frechet_anova returns a 9-key dict
# ===========================================================================

class TestFrechetAnovaAspect:
    """Verify the frechet_anova dict path in the advisor builder."""

    @pytest.fixture(scope="class")
    def anova_result(self):
        from fdars import frechet
        return frechet.frechet_anova(
            _RESPONSES, _ARGVALS, _GROUP_LABELS, n_perm=99, seed=0
        )

    def test_json_serializable(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        json.dumps(diag, sort_keys=True)

    def test_no_numpy_scalars(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        check_no_numpy(diag)

    def test_deterministic(self, anova_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(anova_result, method="frechet")
        d2 = build_diagnostics(anova_result, method="frechet")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_method_field(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert diag["method"] == "frechet"

    def test_has_anova_true(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert diag["has_anova"] is True

    def test_p_value_permutation_range(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        p = diag["anova_p_value_permutation"]
        assert isinstance(p, float)
        assert 0.0 <= p <= 1.0

    def test_p_value_asymptotic_range(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        p = diag["anova_p_value_asymptotic"]
        assert p is None or (isinstance(p, float) and 0.0 <= p <= 1.0)

    def test_n_perm_is_int(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert isinstance(diag["n_perm"], int)

    def test_n_groups_is_int(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert isinstance(diag["n_groups"], int)
        assert diag["n_groups"] == 3  # 3 groups in our fixture

    def test_pooled_variance_is_float(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert isinstance(diag["pooled_frechet_variance"], float)

    def test_group_variance_max_is_float(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert isinstance(diag["group_frechet_variance_max"], float)

    def test_reg_flags_false(self, anova_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(anova_result, method="frechet")
        assert diag["has_global_reg"] is False
        assert diag["has_local_reg"] is False
        assert diag["has_frechet_mean"] is False


# ===========================================================================
# TestFrechetGlobalRegAspect — frechet_global_reg returns {predicted, xout, x_bar}
# ===========================================================================

class TestFrechetGlobalRegAspect:
    """Verify the frechet_global_reg dict path in the advisor builder."""

    @pytest.fixture(scope="class")
    def global_reg_result(self):
        from fdars import frechet
        return frechet.frechet_global_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT
        )

    def test_json_serializable(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        json.dumps(diag, sort_keys=True)

    def test_no_numpy_scalars(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        check_no_numpy(diag)

    def test_deterministic(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(global_reg_result, method="frechet")
        d2 = build_diagnostics(global_reg_result, method="frechet")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_method_field(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        assert diag["method"] == "frechet"

    def test_has_global_reg_true(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        assert diag["has_global_reg"] is True

    def test_has_local_reg_false(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        assert diag["has_local_reg"] is False

    def test_predicted_n_obs(self, global_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        assert isinstance(diag["predicted_n_obs"], int)
        assert diag["predicted_n_obs"] == N_OUT

    def test_bandwidth_none(self, global_reg_result):
        """Global reg has no bandwidth key — bandwidth diagnostic is None."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(global_reg_result, method="frechet")
        assert diag["bandwidth"] is None


# ===========================================================================
# TestFrechetLocalRegAspect — frechet_local_reg returns {predicted, xout, bandwidth}
# ===========================================================================

class TestFrechetLocalRegAspect:
    """Verify the frechet_local_reg dict path in the advisor builder."""

    BANDWIDTH = 0.5

    @pytest.fixture(scope="class")
    def local_reg_result(self):
        from fdars import frechet
        return frechet.frechet_local_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, self.BANDWIDTH
        )

    def test_json_serializable(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        json.dumps(diag, sort_keys=True)

    def test_no_numpy_scalars(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        check_no_numpy(diag)

    def test_deterministic(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        d1 = build_diagnostics(local_reg_result, method="frechet")
        d2 = build_diagnostics(local_reg_result, method="frechet")
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_method_field(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        assert diag["method"] == "frechet"

    def test_has_local_reg_true(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        assert diag["has_local_reg"] is True

    def test_has_global_reg_false(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        assert diag["has_global_reg"] is False

    def test_bandwidth_is_float(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        assert isinstance(diag["bandwidth"], float)
        assert diag["bandwidth"] == pytest.approx(self.BANDWIDTH)

    def test_predicted_n_obs(self, local_reg_result):
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(local_reg_result, method="frechet")
        assert isinstance(diag["predicted_n_obs"], int)
        assert diag["predicted_n_obs"] == N_OUT
