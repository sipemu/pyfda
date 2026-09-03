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


# ===========================================================================
# Plan 69-03: frechet_mean — generic Fréchet mean with 3-space string dispatch
# ===========================================================================

# ---------------------------------------------------------------------------
# Per-space fixtures (§10 of 69-RESEARCH.md)
# ---------------------------------------------------------------------------

_RNG2 = np.random.default_rng(0)  # separate seed so fixtures are independent

D_SPD = 3      # 3×3 SPD matrices
D_SPH = 4      # unit vectors on S^3
D_COR = 3      # 3×3 correlation matrices


def _make_spd(rng, d):
    """Make a random d×d SPD matrix (guaranteed PD via A @ A.T + 0.1*I)."""
    A = rng.standard_normal((d, d))
    return A @ A.T + np.eye(d) * 0.1


def _make_unit_vec(rng, d):
    """Make a random unit vector of length d."""
    v = rng.standard_normal(d)
    return v / np.linalg.norm(v)


def _make_corr(rng, d):
    """Make a random d×d correlation matrix."""
    A = rng.standard_normal((d, d))
    C = A @ A.T + np.eye(d) * 0.5
    D_diag = np.sqrt(np.diag(C))
    return C / np.outer(D_diag, D_diag)


_OBJECTS_SPD = [_make_spd(_RNG2, D_SPD) for _ in range(5)]   # 5 (3,3) SPD matrices
_OBJECTS_SPH = [_make_unit_vec(_RNG2, D_SPH) for _ in range(6)]  # 6 (4,) unit vecs
_OBJECTS_COR = [_make_corr(_RNG2, D_COR) for _ in range(4)]   # 4 (3,3) correlation mats


class TestFrechetMeanSpd:
    """Test frechet_mean with space='spd' — returns symmetric (d,d) array."""

    def test_callable(self):
        assert callable(frechet.frechet_mean)

    def test_result_shape(self):
        result = frechet.frechet_mean(_OBJECTS_SPD, space="spd", d=D_SPD)
        assert result.shape == (D_SPD, D_SPD), (
            f"Expected ({D_SPD}, {D_SPD}), got {result.shape}"
        )

    def test_result_is_symmetric(self):
        result = frechet.frechet_mean(_OBJECTS_SPD, space="spd", d=D_SPD)
        assert np.allclose(result, result.T), "SPD Fréchet mean must be symmetric"

    def test_with_weights(self):
        """Weighted call (uniform weights) produces the same shape."""
        weights = np.ones(len(_OBJECTS_SPD)) / len(_OBJECTS_SPD)
        result = frechet.frechet_mean(_OBJECTS_SPD, space="spd", d=D_SPD, weights=weights)
        assert result.shape == (D_SPD, D_SPD)

    def test_non_symmetric_raises(self):
        """An SPD object with |M[i,j]-M[j,i]| > 1e-8 raises ValueError."""
        bad = _make_spd(_RNG2, D_SPD).copy()
        bad[0, 1] += 10.0   # break symmetry
        with pytest.raises(ValueError, match="symmetric"):
            frechet.frechet_mean([bad] + _OBJECTS_SPD[1:], space="spd", d=D_SPD)

    def test_non_positive_diagonal_raises(self):
        """An object with a non-positive diagonal raises ValueError."""
        bad = _make_spd(_RNG2, D_SPD).copy()
        bad[0, 0] = -1.0
        bad[1, 0] = bad[0, 1]  # keep symmetric
        with pytest.raises(ValueError, match="non-positive"):
            frechet.frechet_mean([bad] + _OBJECTS_SPD[1:], space="spd", d=D_SPD)


class TestFrechetMeanSpherical:
    """Test frechet_mean with space='spherical' — returns (d,) unit-norm vector."""

    def test_result_shape(self):
        result = frechet.frechet_mean(_OBJECTS_SPH, space="spherical", d=D_SPH)
        assert result.shape == (D_SPH,), (
            f"Expected ({D_SPH},), got {result.shape}"
        )

    def test_result_is_unit_norm(self):
        result = frechet.frechet_mean(_OBJECTS_SPH, space="spherical", d=D_SPH)
        assert abs(np.linalg.norm(result) - 1.0) < 1e-4, (
            f"Spherical Fréchet mean must be unit-norm, got norm={np.linalg.norm(result)}"
        )


class TestFrechetMeanCorrelation:
    """Test frechet_mean with space='correlation' — returns (d,d) unit-diagonal array."""

    def test_result_shape(self):
        result = frechet.frechet_mean(_OBJECTS_COR, space="correlation", d=D_COR)
        assert result.shape == (D_COR, D_COR), (
            f"Expected ({D_COR}, {D_COR}), got {result.shape}"
        )

    def test_result_unit_diagonal(self):
        result = frechet.frechet_mean(_OBJECTS_COR, space="correlation", d=D_COR)
        for i in range(D_COR):
            assert abs(result[i, i] - 1.0) < 1e-6, (
                f"Correlation Fréchet mean diagonal[{i},{i}]={result[i,i]} != 1.0"
            )

    def test_non_unit_diagonal_raises(self):
        """A correlation object with diagonal != 1 raises ValueError."""
        bad = _make_corr(_RNG2, D_COR).copy()
        bad[0, 0] = 0.5  # break unit diagonal
        with pytest.raises(ValueError, match="diagonal"):
            frechet.frechet_mean([bad] + _OBJECTS_COR[1:], space="correlation", d=D_COR)


class TestFrechetMeanInvalidSpace:
    """Test frechet_mean invalid-space and shape-mismatch negative paths."""

    def test_invalid_space_raises_valueerror(self):
        """An unknown space name raises ValueError listing all valid names."""
        with pytest.raises(ValueError) as exc_info:
            frechet.frechet_mean(_OBJECTS_SPD, space="banana", d=D_SPD)
        msg = str(exc_info.value)
        assert "spd" in msg
        assert "spherical" in msg
        assert "correlation" in msg

    def test_bad_norm_spherical_raises(self):
        """A non-unit-norm spherical object raises ValueError."""
        bad_vec = np.array([1.0, 2.0, 0.0, 0.0])   # norm=sqrt(5) != 1
        with pytest.raises(ValueError, match="norm"):
            frechet.frechet_mean([bad_vec] + _OBJECTS_SPH[1:], space="spherical", d=D_SPH)

    def test_wrong_shape_spd_raises(self):
        """An SPD object with shape != (d,d) raises ValueError."""
        bad = np.eye(D_SPD + 1)  # (4,4) but d=3
        with pytest.raises(ValueError):
            frechet.frechet_mean([bad], space="spd", d=D_SPD)
