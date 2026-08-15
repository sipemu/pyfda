"""Tests for functional statistics bindings: variance, std, covariance,
depth_based_median, trim_mean — and the corresponding Fdata convenience methods.

Phase 26, Plan 02 (STAT-01, STAT-02).
"""

import numpy as np
import pytest

import fdars
from fdars import Fdata

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

# Small dataset: 3 observations, 4 grid points.
# Chosen so hand-computed Bessel-corrected values are easy to verify.
#   row 0: [1, 2, 3, 4]
#   row 1: [3, 4, 5, 6]
#   row 2: [5, 6, 7, 8]
X3 = np.array([
    [1.0, 2.0, 3.0, 4.0],
    [3.0, 4.0, 5.0, 6.0],
    [5.0, 6.0, 7.0, 8.0],
], dtype=np.float64)

# 2-observation minimum to allow Bessel correction.
X2 = np.array([
    [1.0, 2.0, 3.0],
    [3.0, 4.0, 5.0],
], dtype=np.float64)

# Single-observation (should raise ValueError for variance/covariance).
X1 = np.array([[1.0, 2.0, 3.0]], dtype=np.float64)

ARGVALS4 = np.linspace(0.0, 1.0, 4)
ARGVALS3 = np.linspace(0.0, 1.0, 3)


# ===========================================================================
# TASK 1: functional_variance / functional_std
# ===========================================================================


class TestFunctionalVariance:
    """STAT-01 part: pointwise variance."""

    def test_std_squared_equals_variance_pointwise(self):
        """std² == var pointwise (the core identity)."""
        var = fdars.fdata.functional_variance(X3)
        std = fdars.fdata.functional_std(X3)
        np.testing.assert_allclose(std**2, var, rtol=1e-12,
                                   err_msg="std² must equal var element-wise")

    def test_variance_hand_computed_bessel(self):
        """Bessel-corrected variance on X2 = [[1,2,3],[3,4,5]].

        Pointwise: col0 mean=2, deviations=[-1,1], var=(1+1)/(2-1)=2.
                   col1 mean=3, deviations=[-1,1], var=2.
                   col2 mean=4, deviations=[-1,1], var=2.
        """
        var = fdars.fdata.functional_variance(X2)
        expected = np.array([2.0, 2.0, 2.0])
        np.testing.assert_allclose(var, expected, rtol=1e-12,
                                   err_msg="Bessel-corrected variance mismatch")

    def test_std_hand_computed_bessel(self):
        """Bessel-corrected std matches sqrt(var)."""
        std = fdars.fdata.functional_std(X2)
        expected = np.full(3, np.sqrt(2.0))
        np.testing.assert_allclose(std, expected, rtol=1e-12,
                                   err_msg="Bessel-corrected std mismatch")

    def test_variance_n1_raises_valueerror(self):
        """n=1 should raise ValueError (not enough obs for Bessel correction)."""
        with pytest.raises(ValueError):
            fdars.fdata.functional_variance(X1)

    def test_std_n1_raises_valueerror(self):
        """n=1 should raise ValueError."""
        with pytest.raises(ValueError):
            fdars.fdata.functional_std(X1)

    def test_variance_returns_length_m(self):
        """functional_variance returns a 1-D array of length n_points."""
        var = fdars.fdata.functional_variance(X3)
        assert var.ndim == 1
        assert var.shape == (X3.shape[1],)

    def test_std_returns_length_m(self):
        """functional_std returns a 1-D array of length n_points."""
        std = fdars.fdata.functional_std(X3)
        assert std.ndim == 1
        assert std.shape == (X3.shape[1],)

    def test_fdata_var_returns_array_of_length_n_points(self):
        """fd.var() returns a 1-D numpy array of length fd.n_points."""
        fd = Fdata(X3, ARGVALS4)
        v = fd.var()
        assert isinstance(v, np.ndarray)
        assert v.ndim == 1
        assert v.shape == (fd.n_points,)

    def test_fdata_std_returns_array_of_length_n_points(self):
        """fd.std() returns a 1-D numpy array of length fd.n_points."""
        fd = Fdata(X3, ARGVALS4)
        s = fd.std()
        assert isinstance(s, np.ndarray)
        assert s.ndim == 1
        assert s.shape == (fd.n_points,)

    def test_fdata_var_matches_module_level(self):
        """fd.var() equals fdars.fdata.functional_variance(fd.data)."""
        fd = Fdata(X3, ARGVALS4)
        np.testing.assert_array_equal(fd.var(),
                                      fdars.fdata.functional_variance(fd.data))

    def test_fdata_std_matches_module_level(self):
        """fd.std() equals fdars.fdata.functional_std(fd.data)."""
        fd = Fdata(X3, ARGVALS4)
        np.testing.assert_array_equal(fd.std(),
                                      fdars.fdata.functional_std(fd.data))


# ===========================================================================
# TASK 2: functional_covariance (m×m) — layout-correctness guard
# ===========================================================================


class TestFunctionalCovariance:
    """STAT-01 part: m×m covariance surface with transposition guard."""

    # Build a dataset with DISTINCT per-column behaviour so a row/column swap
    # produces a clearly wrong diagonal.
    #
    # 4 curves, 3 grid points.  Values chosen so each grid point has a
    # distinctly different variance (col 0 variance != col 1 != col 2).
    #
    #   col 0: [1, 2, 3, 4]   mean=2.5, deviations=[-1.5,-0.5,+0.5,+1.5], var=5/3
    #   col 1: [0, 0, 2, 4]   mean=1.5, deviations=[-1.5,-1.5,+0.5,+2.5], var=10/3
    #   col 2: [3, 3, 3, 3]   mean=3.0, deviations=[0,0,0,0], var=0
    X_COV = np.array([
        [1.0, 0.0, 3.0],
        [2.0, 0.0, 3.0],
        [3.0, 2.0, 3.0],
        [4.0, 4.0, 3.0],
    ], dtype=np.float64)

    # Hand-computed Bessel-corrected variances (n=4, divisor=3):
    # col0: sum_sq_dev = 1.5²+0.5²+0.5²+1.5² = 2.25+0.25+0.25+2.25 = 5.0  → var=5/3
    # col1: deviations: -1.5,-1.5,+0.5,+2.5  → sq = 2.25+2.25+0.25+6.25=11  → var=11/3
    # col2: all same → var=0
    VAR_EXPECTED = np.array([5.0 / 3.0, 11.0 / 3.0, 0.0])

    def test_covariance_shape(self):
        """functional_covariance returns shape (m, m)."""
        cov = fdars.fdata.functional_covariance(self.X_COV)
        m = self.X_COV.shape[1]
        assert cov.shape == (m, m), f"expected ({m},{m}), got {cov.shape}"

    def test_covariance_diagonal_equals_variance(self):
        """diag(cov) equals functional_variance — the key layout-correctness guard.

        A transposed covariance matrix would map column indices to row indices,
        swapping the meaning of each diagonal entry.  Since our columns have
        DISTINCT variances, any transposition makes at least one diagonal wrong.
        """
        cov = fdars.fdata.functional_covariance(self.X_COV)
        var = fdars.fdata.functional_variance(self.X_COV)
        np.testing.assert_allclose(
            np.diag(cov), var, rtol=1e-12,
            err_msg="diag(cov) must equal functional_variance — layout guard"
        )

    def test_covariance_diagonal_hand_computed(self):
        """diag(cov) matches hand-computed Bessel-corrected variances."""
        cov = fdars.fdata.functional_covariance(self.X_COV)
        np.testing.assert_allclose(
            np.diag(cov), self.VAR_EXPECTED, rtol=1e-12,
            err_msg="diagonal entries must match hand-computed variances"
        )

    def test_covariance_known_off_diagonal(self):
        """A specific off-diagonal entry matches the hand-computed value.

        cov[0,1] = (1/3) * sum_i (x_i0 - mean0) * (x_i1 - mean1)
        deviations_col0: [-1.5, -0.5, +0.5, +1.5]
        deviations_col1: [-1.5, -1.5, +0.5, +2.5]
        cross: 2.25 + 0.75 + 0.25 + 3.75 = 7.0  → cov[0,1] = 7/3
        """
        cov = fdars.fdata.functional_covariance(self.X_COV)
        expected_01 = 7.0 / 3.0
        np.testing.assert_allclose(
            cov[0, 1], expected_01, rtol=1e-12,
            err_msg="cov[0,1] must match the hand-computed cross-covariance"
        )

    def test_covariance_symmetry(self):
        """Covariance matrix is symmetric."""
        cov = fdars.fdata.functional_covariance(self.X_COV)
        np.testing.assert_allclose(cov, cov.T, rtol=1e-12,
                                   err_msg="covariance matrix must be symmetric")

    def test_covariance_n1_raises_valueerror(self):
        """n=1 should raise ValueError."""
        with pytest.raises(ValueError):
            fdars.fdata.functional_covariance(X1)

    def test_fdata_cov_returns_m_by_m(self):
        """fd.cov() returns a 2-D numpy array of shape (n_points, n_points)."""
        fd = Fdata(self.X_COV, np.linspace(0, 1, 3))
        c = fd.cov()
        m = fd.n_points
        assert isinstance(c, np.ndarray)
        assert c.ndim == 2
        assert c.shape == (m, m)

    def test_fdata_cov_matches_module_level(self):
        """fd.cov() equals fdars.fdata.functional_covariance(fd.data)."""
        fd = Fdata(self.X_COV, np.linspace(0, 1, 3))
        np.testing.assert_array_equal(fd.cov(),
                                      fdars.fdata.functional_covariance(fd.data))

    def test_multi_curve_transposition_round_trip(self):
        """Dedicated multi-curve transposition guard (mandated layout test #33).

        Build 5 curves across 4 grid points with distinct-per-curve structure
        (each curve follows a different analytic pattern) so that the covariance
        matrix is NOT the identity — a column-major/row-major swap would produce
        distinctly wrong values.  Assert BOTH:
          (i)  diag(cov) == functional_variance(X) element-wise
          (ii) cov[0, 1] matches the hand/numpy Bessel-corrected cross-covariance
        """
        rng = np.random.default_rng(42)
        # 5 observations, 4 grid points — each obs follows a different slope
        t = np.array([0.0, 1.0, 2.0, 3.0])
        X = np.stack([
            np.array([1.0, 3.0, 6.0, 10.0]),   # quadratic-ish
            np.array([2.0, 5.0, 8.0, 11.0]),   # linear
            np.array([4.0, 2.0, 1.0, 0.5]),    # decreasing
            np.array([0.0, 1.0, 4.0, 9.0]),    # squares
            np.array([3.0, 3.0, 3.0, 3.0]),   # constant
        ], axis=0).astype(np.float64)

        cov = fdars.fdata.functional_covariance(X)
        var = fdars.fdata.functional_variance(X)

        # (i) diagonal == variance
        np.testing.assert_allclose(np.diag(cov), var, rtol=1e-12,
                                   err_msg="multi-curve: diag(cov) != functional_variance")

        # (ii) cov[0,1] matches numpy Bessel-corrected cross-covariance
        col0 = X[:, 0]
        col1 = X[:, 1]
        expected_01 = np.dot(col0 - col0.mean(), col1 - col1.mean()) / (len(col0) - 1)
        np.testing.assert_allclose(cov[0, 1], expected_01, rtol=1e-12,
                                   err_msg="multi-curve: cov[0,1] layout mismatch")


# ===========================================================================
# TASK 3: depth_based_median + trim_mean + Fdata.median()
# ===========================================================================


class TestDepthBasedMedian:
    """STAT-02 part: depth-based median returns the resolved curve, not an int."""

    def test_returns_length_m_array(self):
        """depth_based_median must return a 1-D array of length n_points."""
        result = fdars.fdata.depth_based_median(X3)
        assert result.ndim == 1, "must be 1-D (a curve), not a scalar/int"
        assert result.shape == (X3.shape[1],), \
            f"expected shape ({X3.shape[1]},), got {result.shape}"

    def test_result_not_an_int(self):
        """Result must not be an integer (the usize index must be resolved)."""
        result = fdars.fdata.depth_based_median(X3)
        # Should be a float array, not int
        assert hasattr(result, 'shape'), "result must be a numpy array, not a bare int"
        assert np.issubdtype(result.dtype, np.floating), \
            f"result dtype must be floating, got {result.dtype}"

    def test_result_equals_an_observed_row(self):
        """Resolved median curve must be byte-equal to one of the input rows."""
        result = fdars.fdata.depth_based_median(X3)
        is_observed = any(np.array_equal(result, X3[i]) for i in range(len(X3)))
        assert is_observed, (
            "depth_based_median result must equal one of the observed curves; "
            f"got {result!r} but rows are {X3!r}"
        )

    def test_fdata_median_is_fdata_row(self):
        """fd.median() returns an Fdata with n_obs=1 and n_points=fd.n_points."""
        fd = Fdata(X3, ARGVALS4)
        med = fd.median()
        assert isinstance(med, Fdata), "fd.median() must return an Fdata"
        assert med.n_obs == 1, \
            f"median Fdata must have exactly 1 observation, got {med.n_obs}"
        assert med.n_points == fd.n_points, \
            f"median n_points must match source ({fd.n_points}), got {med.n_points}"

    def test_fdata_median_argvals_match(self):
        """fd.median() carries the same argvals as the source."""
        fd = Fdata(X3, ARGVALS4)
        med = fd.median()
        np.testing.assert_array_equal(med.argvals, fd.argvals,
                                      err_msg="median Fdata argvals must match source")

    def test_fdata_median_data_is_observed_row(self):
        """fd.median() data is one of the original observed rows."""
        fd = Fdata(X3, ARGVALS4)
        med = fd.median()
        curve = med.data[0]
        is_observed = any(np.array_equal(curve, X3[i]) for i in range(len(X3)))
        assert is_observed, (
            f"fd.median() data row {curve!r} must equal one of the source curves"
        )


class TestTrimMean:
    """STAT-02 part: trim_mean with α=0 identity and degenerate inputs."""

    # Dataset with outlier in row 2 to make trim_mean meaningful.
    X_OUT = np.array([
        [1.0, 2.0, 3.0],
        [1.5, 2.5, 3.5],
        [1.2, 2.2, 3.2],
        [9.0, 9.0, 9.0],   # outlier
    ], dtype=np.float64)

    def test_trim_mean_alpha_zero_equals_mean(self):
        """trim_mean(X, alpha=0.0) must equal mean_1d(X) exactly."""
        tm = fdars.fdata.trim_mean(X3, 0.0)
        mn = fdars.fdata.mean_1d(X3)
        np.testing.assert_allclose(tm, mn, rtol=1e-12, atol=1e-15,
                                   err_msg="trim_mean(α=0) must equal mean_1d exactly")

    def test_trim_mean_alpha_zero_equals_mean_outlier(self):
        """trim_mean(α=0) equals mean_1d even on outlier dataset."""
        tm = fdars.fdata.trim_mean(self.X_OUT, 0.0)
        mn = fdars.fdata.mean_1d(self.X_OUT)
        np.testing.assert_allclose(tm, mn, rtol=1e-12, atol=1e-15,
                                   err_msg="trim_mean(α=0) must equal mean_1d on outlier data")

    def test_trim_mean_alpha_positive_differs_from_mean_with_outlier(self):
        """trim_mean(α=0.2) differs from mean_1d on outlier-contaminated data."""
        tm = fdars.fdata.trim_mean(self.X_OUT, 0.2)
        mn = fdars.fdata.mean_1d(self.X_OUT)
        # With the outlier row trimmed, means should differ
        assert not np.allclose(tm, mn, rtol=1e-3), (
            "trim_mean(α=0.2) should differ from mean on outlier-contaminated data"
        )

    def test_trim_mean_returns_length_m(self):
        """trim_mean returns a 1-D array of length n_points."""
        tm = fdars.fdata.trim_mean(X3, 0.0)
        assert tm.ndim == 1
        assert tm.shape == (X3.shape[1],)

    def test_trim_mean_alpha_negative_raises_valueerror(self):
        """alpha < 0 should raise ValueError."""
        with pytest.raises(ValueError):
            fdars.fdata.trim_mean(X3, -0.1)

    def test_trim_mean_alpha_one_raises_valueerror(self):
        """alpha >= 1.0 should raise ValueError."""
        with pytest.raises(ValueError):
            fdars.fdata.trim_mean(X3, 1.0)

    def test_trim_mean_alpha_gt_one_raises_valueerror(self):
        """alpha > 1.0 should raise ValueError."""
        with pytest.raises(ValueError):
            fdars.fdata.trim_mean(X3, 1.5)
