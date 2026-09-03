"""Tests for fdars.frechet — density-default Fréchet regression and ANOVA.

Plan 69-02: frechet_anova (tracer), frechet_global_reg, frechet_local_reg.
Plan 69-03: frechet_mean (generic dispatch) — appended later.
"""

import numpy as np
import pytest
from scipy.stats import norm

import fdars
import fdars.frechet as frechet

# ---------------------------------------------------------------------------
# Shared density-default fixtures (§10 of 69-RESEARCH.md)
# N=40, M=50, N_OUT=10, N_PRED=2 — all three dims are distinct (non-square)
# ---------------------------------------------------------------------------

N, M = 40, 50       # n_obs=40 densities on m=50 grid points
N_OUT = 10          # prediction output points
N_PRED = 2          # predictor dimension p=2

RNG = np.random.default_rng(42)
_ARGVALS = np.linspace(-3.0, 3.0, M)   # strictly increasing grid

# Scalar predictor matrix (N, N_PRED)
_PREDICTORS = RNG.standard_normal((N, N_PRED))

# Density responses: each row is a normalised Gaussian density shifted by predictor[i, 0]
_RESPONSES = np.zeros((N, M))
for _i in range(N):
    _mu = _PREDICTORS[_i, 0]
    _raw = norm.pdf(_ARGVALS, loc=_mu, scale=0.8)
    _RESPONSES[_i] = _raw / np.trapezoid(_raw, _ARGVALS)

# Prediction points (N_OUT, N_PRED) — distinct from N and M
_XOUT = RNG.standard_normal((N_OUT, N_PRED))

# Group labels for ANOVA: contiguous 0, 1, 2 (3 groups)
_GROUP_LABELS = np.array([i // (N // 3) for i in range(N)], dtype=np.int64)
_GROUP_LABELS = np.clip(_GROUP_LABELS, 0, 2)

# Sanity-check fixture dimensions
assert _PREDICTORS.shape == (N, N_PRED)
assert _RESPONSES.shape == (N, M)
assert _XOUT.shape == (N_OUT, N_PRED)
assert N != M and N != N_OUT and M != N_OUT   # all three dims are distinct
assert set(_GROUP_LABELS.tolist()) == {0, 1, 2}


# ===========================================================================
# Task 1 (TRACER): frechet_anova
# ===========================================================================

class TestFrechetAnova:
    """Test frechet_anova — 9-key PyDict, permutation p-value in [0,1], shape checks."""

    def test_submodule_importable(self):
        """fdars.frechet is importable and frechet_anova is callable."""
        assert callable(frechet.frechet_anova)

    def test_returns_9_keys(self):
        result = frechet.frechet_anova(
            _RESPONSES, _ARGVALS, _GROUP_LABELS, n_perm=99, seed=0
        )
        expected_keys = {
            "statistic",
            "p_value_asymptotic",
            "p_value_permutation",
            "n_perm",
            "group_frechet_variances",
            "pooled_frechet_variance",
            "fn_statistic",
            "un_statistic",
            "group_labels",
        }
        assert set(result.keys()) == expected_keys

    def test_p_value_in_unit_interval(self):
        result = frechet.frechet_anova(
            _RESPONSES, _ARGVALS, _GROUP_LABELS, n_perm=99, seed=7
        )
        assert 0.0 <= result["p_value_permutation"] <= 1.0
        assert 0.0 <= result["p_value_asymptotic"] <= 1.0

    def test_group_frechet_variances_shape(self):
        result = frechet.frechet_anova(
            _RESPONSES, _ARGVALS, _GROUP_LABELS, n_perm=99, seed=1
        )
        assert result["group_frechet_variances"].shape == (3,)

    def test_group_labels_echo(self):
        """result['group_labels'] echoes the sorted unique 0..k labels."""
        result = frechet.frechet_anova(
            _RESPONSES, _ARGVALS, _GROUP_LABELS, n_perm=99, seed=1
        )
        # The result group_labels is an n-length echo of the sorted input labels
        assert result["group_labels"].shape == (_GROUP_LABELS.shape[0],)

    def test_n_perm_echoed(self):
        result = frechet.frechet_anova(
            _RESPONSES, _ARGVALS, _GROUP_LABELS, n_perm=49, seed=2
        )
        assert result["n_perm"] == 49

    def test_non_contiguous_labels_raise(self):
        """Non-contiguous group labels (e.g. [0, 1, 3]) raise ValueError."""
        bad_labels = np.array([0] * 15 + [1] * 15 + [3] * 10, dtype=np.int64)  # skips 2
        with pytest.raises(ValueError, match="contiguous"):
            frechet.frechet_anova(_RESPONSES, _ARGVALS, bad_labels)

    def test_non_zero_start_labels_raise(self):
        """Labels starting from 1 instead of 0 raise ValueError."""
        bad_labels = np.array([1] * 20 + [2] * 20, dtype=np.int64)
        with pytest.raises(ValueError, match="contiguous"):
            frechet.frechet_anova(_RESPONSES, _ARGVALS, bad_labels)


# ===========================================================================
# Task 2: frechet_global_reg
# ===========================================================================

class TestFrechetGlobalReg:
    """Test frechet_global_reg — 3-key PyDict, (N_OUT, M) shape, non-square."""

    def test_callable(self):
        assert callable(frechet.frechet_global_reg)

    def test_returns_3_keys(self):
        result = frechet.frechet_global_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT
        )
        assert set(result.keys()) == {"predicted", "xout", "x_bar"}

    def test_predicted_shape_is_n_out_m(self):
        """Transposition correctness: predicted must be (N_OUT, M), NOT (M, N_OUT)."""
        result = frechet.frechet_global_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT
        )
        assert result["predicted"].shape == (N_OUT, M), (
            f"Expected (N_OUT={N_OUT}, M={M}), got {result['predicted'].shape}"
        )

    def test_xout_shape(self):
        result = frechet.frechet_global_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT
        )
        assert result["xout"].shape == (N_OUT, N_PRED)

    def test_x_bar_shape(self):
        result = frechet.frechet_global_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT
        )
        assert result["x_bar"].shape == (N_PRED,)

    def test_mismatched_argvals_raises(self):
        """argvals length != responses.shape[1] raises ValueError (upstream validation)."""
        bad_argvals = np.linspace(-3.0, 3.0, M + 5)   # wrong length
        with pytest.raises(ValueError):
            frechet.frechet_global_reg(
                _PREDICTORS, _RESPONSES, bad_argvals, _XOUT
            )


# ===========================================================================
# Task 3: frechet_local_reg
# ===========================================================================

class TestFrechetLocalReg:
    """Test frechet_local_reg — 3-key PyDict, bandwidth required positional, (N_OUT, M)."""

    BANDWIDTH = 0.5

    def test_callable(self):
        assert callable(frechet.frechet_local_reg)

    def test_returns_3_keys(self):
        result = frechet.frechet_local_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, self.BANDWIDTH
        )
        assert set(result.keys()) == {"predicted", "xout", "bandwidth"}

    def test_predicted_shape_is_n_out_m(self):
        """Transposition correctness: predicted must be (N_OUT, M), NOT (M, N_OUT)."""
        result = frechet.frechet_local_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, self.BANDWIDTH
        )
        assert result["predicted"].shape == (N_OUT, M), (
            f"Expected (N_OUT={N_OUT}, M={M}), got {result['predicted'].shape}"
        )

    def test_xout_shape(self):
        result = frechet.frechet_local_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, self.BANDWIDTH
        )
        assert result["xout"].shape == (N_OUT, N_PRED)

    def test_bandwidth_echoed(self):
        """result['bandwidth'] echoes the input bandwidth value."""
        result = frechet.frechet_local_reg(
            _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, self.BANDWIDTH
        )
        assert result["bandwidth"] == pytest.approx(self.BANDWIDTH)

    def test_non_positive_bandwidth_raises(self):
        """bandwidth <= 0.0 raises ValueError (upstream validation)."""
        with pytest.raises(ValueError):
            frechet.frechet_local_reg(
                _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, -1.0
            )

    def test_zero_bandwidth_raises(self):
        """bandwidth == 0.0 raises ValueError."""
        with pytest.raises(ValueError):
            frechet.frechet_local_reg(
                _PREDICTORS, _RESPONSES, _ARGVALS, _XOUT, 0.0
            )
