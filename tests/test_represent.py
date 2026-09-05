"""Tests for the fdars.represent submodule.

Covers:
- spline_interpolate: multi-curve round-trip + transposition guard (Task 1 tracer)
- spline_interpolate_with_policy: four policies + error paths (Task 2)
- fdata_interpolate_with_policy: policy dispatch (Task 2)
- impute_missing_values: linear/mean/constant + error paths (Task 3)
- Fdata.interpolate() and Fdata.impute() convenience methods (Task 3)
"""

import numpy as np
import pytest

import fdars
from fdars import Fdata
import fdars.represent as represent
from fdars.represent import (
    spline_interpolate,
    spline_interpolate_with_policy,
    fdata_interpolate_with_policy,
    impute_missing_values,
)


# ---------------------------------------------------------------------------
# Task 1 tracer: namespace + multi-curve round-trip (transposition guard)
# ---------------------------------------------------------------------------

class TestNamespace:
    """fdars.represent namespace is reachable via both import patterns."""

    def test_import_submodule(self):
        import fdars.represent  # noqa: F401

    def test_from_import(self):
        from fdars.represent import spline_interpolate  # noqa: F401

    def test_package_attribute(self):
        assert hasattr(fdars, "represent")


class TestSplineInterpolateTracer:
    """Multi-curve round-trip: distinct per-curve shapes, verifies no transposition.

    Each curve is sin((i+1)*pi*t) on a coarse grid.  After spline interpolation
    onto a finer grid the per-curve values are tested individually — a swap of
    rows/columns would make curve 0 look like curve 1 and vice-versa.
    """

    N_OBS = 3
    M_COARSE = 20  # More points for smoother sin curves with higher frequencies
    M_FINE = 41

    @pytest.fixture
    def dataset(self):
        t_coarse = np.linspace(0.0, 1.0, self.M_COARSE)
        t_fine = np.linspace(0.0, 1.0, self.M_FINE)
        data = np.stack(
            [np.sin((i + 1) * np.pi * t_coarse) for i in range(self.N_OBS)],
            axis=0,
            dtype=np.float64,
        )
        return data, t_coarse, t_fine

    def test_output_shape(self, dataset):
        data, t_coarse, t_fine = dataset
        result = spline_interpolate(data, t_coarse, t_fine, order=4)
        assert result.shape == (self.N_OBS, self.M_FINE)

    def test_per_curve_values_curve0(self, dataset):
        """Curve 0 (sin(pi*t)) interpolated values match analytic reference."""
        data, t_coarse, t_fine = dataset
        result = spline_interpolate(data, t_coarse, t_fine, order=4)
        expected = np.sin(1 * np.pi * t_fine)
        np.testing.assert_allclose(result[0], expected, atol=2e-3)

    def test_per_curve_values_curve1(self, dataset):
        """Curve 1 (sin(2*pi*t)) has distinct values from curve 0."""
        data, t_coarse, t_fine = dataset
        result = spline_interpolate(data, t_coarse, t_fine, order=4)
        expected = np.sin(2 * np.pi * t_fine)
        np.testing.assert_allclose(result[1], expected, atol=2e-3)

    def test_per_curve_values_curve2(self, dataset):
        """Curve 2 (sin(3*pi*t)) is distinct from the others."""
        data, t_coarse, t_fine = dataset
        result = spline_interpolate(data, t_coarse, t_fine, order=4)
        expected = np.sin(3 * np.pi * t_fine)
        np.testing.assert_allclose(result[2], expected, atol=2e-2)

    def test_transposition_guard(self, dataset):
        """Swapping rows and columns would fail at least one per-curve check.

        Curve 0 is sin(pi*t) and curve 1 is sin(2*pi*t).  A transposition
        (row/column swap) would put the wrong shape under result[0]; the
        per-curve allclose checks above catch that, but this asserts the
        curves themselves are distinguishably different.
        """
        data, t_coarse, t_fine = dataset
        result = spline_interpolate(data, t_coarse, t_fine, order=4)
        # Curves must differ significantly to serve as a transposition sentinel.
        assert not np.allclose(result[0], result[1], atol=0.05), (
            "Curves 0 and 1 should differ; near-identical values suggest a transposition bug"
        )
        assert not np.allclose(result[0], result[2], atol=0.05), (
            "Curves 0 and 2 should differ; near-identical values suggest a transposition bug"
        )

    def test_reproduces_argvals_shape_and_range(self, dataset):
        """Interpolating at the original argvals returns the same shape and stays within range."""
        data, t_coarse, _ = dataset
        result = spline_interpolate(data, t_coarse, t_coarse, order=4)
        assert result.shape == data.shape
        # Values should be in a reasonable range (all sin values lie in [-1,1])
        assert np.all(result >= -1.1)
        assert np.all(result <= 1.1)

    def test_default_order_is_cubic(self, dataset):
        """Calling without explicit order= uses cubic (4) and produces the same result."""
        data, t_coarse, t_fine = dataset
        result_default = spline_interpolate(data, t_coarse, t_fine)
        result_explicit = spline_interpolate(data, t_coarse, t_fine, order=4)
        np.testing.assert_array_equal(result_default, result_explicit)


# ---------------------------------------------------------------------------
# Task 2: ExtrapolationPolicy string dispatch
# ---------------------------------------------------------------------------

class TestSplineInterpolateWithPolicy:
    """Four-arm + fallback string-enum mapping."""

    @pytest.fixture
    def simple(self):
        """Single curve y=t on [0, 1], coarse grid."""
        t = np.linspace(0.0, 1.0, 11, dtype=np.float64)
        data = t[np.newaxis, :]  # shape (1, 11)
        return data, t

    def test_in_domain_same_regardless_of_policy(self, simple):
        data, t = simple
        q = np.linspace(0.1, 0.9, 9, dtype=np.float64)
        ref = spline_interpolate(data, t, q)
        for policy in ("boundary", "exception", "fill", "periodic"):
            result = spline_interpolate_with_policy(data, t, q, policy=policy)
            np.testing.assert_allclose(result, ref, atol=1e-8,
                                       err_msg=f"Policy '{policy}' diverged for in-domain points")

    def test_boundary_clamps_to_boundary_value(self, simple):
        """OOB query with 'boundary' returns the spline value at the nearest boundary."""
        data, t = simple
        # t=1.0 is the right boundary; y(1.0) = 1.0 for y=t curve.
        q_ood = np.array([1.1], dtype=np.float64)
        result = spline_interpolate_with_policy(data, t, q_ood, policy="boundary")
        # Should equal the boundary value y(1.0) ≈ 1.0
        np.testing.assert_allclose(result[0, 0], 1.0, atol=1e-6)

    def test_fill_returns_constant_for_ood_query(self, simple):
        """OOB query with 'fill' returns fill_value=-1.0 in the out-of-domain cells."""
        data, t = simple
        q_mixed = np.array([-0.1, 0.5, 1.2], dtype=np.float64)
        result = spline_interpolate_with_policy(
            data, t, q_mixed, policy="fill", fill_value=-1.0
        )
        # cells 0 and 2 are OOB
        assert result[0, 0] == pytest.approx(-1.0)
        assert result[0, 2] == pytest.approx(-1.0)
        # cell 1 is in-domain — should be ~0.5 (y=t curve)
        assert result[0, 1] == pytest.approx(0.5, abs=1e-3)

    def test_exception_raises_for_ood_query(self, simple):
        """OOB query with 'exception' raises ValueError."""
        data, t = simple
        q_ood = np.array([1.5], dtype=np.float64)
        with pytest.raises(ValueError):
            spline_interpolate_with_policy(data, t, q_ood, policy="exception")

    def test_unknown_policy_raises(self, simple):
        """Unrecognised policy string raises ValueError (fallback arm)."""
        data, t = simple
        q = np.array([0.5], dtype=np.float64)
        with pytest.raises(ValueError, match="policy must be"):
            spline_interpolate_with_policy(data, t, q, policy="bogus")

    def test_periodic_wraps_query(self, simple):
        """'periodic' policy wraps t=1.1 to t=0.1 on a [0,1] domain (y=t => ~0.1)."""
        data, t = simple
        q_ood = np.array([1.1], dtype=np.float64)
        result = spline_interpolate_with_policy(data, t, q_ood, policy="periodic")
        # wrapped: 1.1 - 1.0 = 0.1; y(0.1) = 0.1
        np.testing.assert_allclose(result[0, 0], 0.1, atol=1e-3)


class TestFdataInterpolateWithPolicy:
    """fdata_interpolate_with_policy uses linear/cubic_hermite + policy."""

    @pytest.fixture
    def simple(self):
        t = np.linspace(0.0, 1.0, 11, dtype=np.float64)
        data = t[np.newaxis, :]
        return data, t

    def test_in_domain_linear(self, simple):
        data, t = simple
        q = np.linspace(0.0, 1.0, 21, dtype=np.float64)
        result = fdata_interpolate_with_policy(data, t, q, policy="boundary", method="linear")
        np.testing.assert_allclose(result[0], q, atol=1e-8)

    def test_fill_policy_linear(self, simple):
        data, t = simple
        q = np.array([-0.5, 0.5, 1.5], dtype=np.float64)
        result = fdata_interpolate_with_policy(
            data, t, q, policy="fill", fill_value=99.0, method="linear"
        )
        assert result[0, 0] == pytest.approx(99.0)
        assert result[0, 2] == pytest.approx(99.0)
        assert result[0, 1] == pytest.approx(0.5, abs=1e-6)

    def test_exception_policy_raises(self, simple):
        data, t = simple
        q = np.array([1.5], dtype=np.float64)
        with pytest.raises(ValueError):
            fdata_interpolate_with_policy(data, t, q, policy="exception")

    def test_unknown_policy_raises(self, simple):
        data, t = simple
        q = np.array([0.5], dtype=np.float64)
        with pytest.raises(ValueError, match="policy must be"):
            fdata_interpolate_with_policy(data, t, q, policy="nope")

    def test_unknown_method_raises(self, simple):
        data, t = simple
        q = np.array([0.5], dtype=np.float64)
        with pytest.raises(ValueError, match="method must be"):
            fdata_interpolate_with_policy(data, t, q, method="rbf")


# ---------------------------------------------------------------------------
# Task 3: impute_missing_values + Fdata.interpolate() / Fdata.impute()
# ---------------------------------------------------------------------------

class TestImputeMissingValues:
    """Module-level impute_missing_values with linear/mean/constant strategies."""

    @pytest.fixture
    def two_curve_with_nan(self):
        """Two curves with interior NaN; distinct non-NaN values per curve."""
        t = np.array([0.0, 1.0, 2.0, 3.0, 4.0], dtype=np.float64)
        # curve 0: linear 0,1,?,3,4 — interior gap at index 2
        # curve 1: linear 10,20,?,40,50 — interior gap at index 2
        data = np.array(
            [[0.0, 1.0, np.nan, 3.0, 4.0],
             [10.0, 20.0, np.nan, 40.0, 50.0]],
            dtype=np.float64,
        )
        return data, t

    def test_linear_fills_interior_gap(self, two_curve_with_nan):
        data, t = two_curve_with_nan
        result = impute_missing_values(data, t, method="linear")
        assert not np.isnan(result).any()
        # Curve 0: linear between 1 and 3 → 2.0
        np.testing.assert_allclose(result[0, 2], 2.0, atol=1e-6)
        # Curve 1: linear between 20 and 40 → 30.0
        np.testing.assert_allclose(result[1, 2], 30.0, atol=1e-6)

    def test_linear_preserves_non_nan_entries(self, two_curve_with_nan):
        data, t = two_curve_with_nan
        result = impute_missing_values(data, t, method="linear")
        # Non-NaN entries must be unchanged
        mask = ~np.isnan(data)
        np.testing.assert_array_equal(result[mask], data[mask])

    def test_mean_fills_with_curve_mean(self, two_curve_with_nan):
        data, t = two_curve_with_nan
        result = impute_missing_values(data, t, method="mean")
        assert not np.isnan(result).any()
        # Curve 0 non-NaN mean: (0+1+3+4)/4 = 2.0
        curve0_mean = np.nanmean(data[0])
        np.testing.assert_allclose(result[0, 2], curve0_mean, atol=1e-6)
        # Curve 1 non-NaN mean: (10+20+40+50)/4 = 30.0
        curve1_mean = np.nanmean(data[1])
        np.testing.assert_allclose(result[1, 2], curve1_mean, atol=1e-6)

    def test_constant_fills_with_given_value(self, two_curve_with_nan):
        data, t = two_curve_with_nan
        result = impute_missing_values(data, t, method="constant", constant_value=999.0)
        assert not np.isnan(result).any()
        np.testing.assert_allclose(result[0, 2], 999.0, atol=1e-12)
        np.testing.assert_allclose(result[1, 2], 999.0, atol=1e-12)

    def test_all_nan_row_raises(self):
        """A fully-NaN curve raises ValueError (not a panic)."""
        t = np.array([0.0, 1.0, 2.0], dtype=np.float64)
        data = np.array([[np.nan, np.nan, np.nan]], dtype=np.float64)
        with pytest.raises(ValueError):
            impute_missing_values(data, t, method="linear")

    def test_unknown_method_raises(self):
        t = np.array([0.0, 1.0, 2.0], dtype=np.float64)
        data = np.array([[1.0, np.nan, 3.0]], dtype=np.float64)
        with pytest.raises(ValueError, match="method must be"):
            impute_missing_values(data, t, method="bogus")

    def test_multi_curve_distinct_fill_values(self, two_curve_with_nan):
        """Linear fill on distinct curves yields distinct filled values."""
        data, t = two_curve_with_nan
        result = impute_missing_values(data, t, method="linear")
        # Curve 0 filled 2.0, curve 1 filled 30.0 — not the same
        assert not np.isclose(result[0, 2], result[1, 2])


class TestFdataInterpolateMethods:
    """Fdata.interpolate() and Fdata.impute() convenience methods."""

    @pytest.fixture
    def fd_linear(self):
        """Simple Fdata object: two curves, y_i = (i+1)*t on [0,1]."""
        t = np.linspace(0.0, 1.0, 11, dtype=np.float64)
        data = np.stack(
            [(i + 1) * t for i in range(2)],
            axis=0, dtype=np.float64
        )
        return Fdata(data, argvals=t)

    @pytest.fixture
    def fd_with_nan(self):
        t = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.float64)
        data = np.array(
            [[0.0, 1.0, np.nan, 3.0],
             [10.0, np.nan, 30.0, 40.0]],
            dtype=np.float64,
        )
        return Fdata(data, argvals=t)

    def test_interpolate_returns_fdata(self, fd_linear):
        finer = np.linspace(0.0, 1.0, 21, dtype=np.float64)
        out = fd_linear.interpolate(finer)
        assert isinstance(out, Fdata)

    def test_interpolate_n_obs_unchanged(self, fd_linear):
        finer = np.linspace(0.0, 1.0, 21, dtype=np.float64)
        out = fd_linear.interpolate(finer)
        assert out.n_obs == fd_linear.n_obs

    def test_interpolate_argvals_equals_query_grid(self, fd_linear):
        finer = np.linspace(0.0, 1.0, 21, dtype=np.float64)
        out = fd_linear.interpolate(finer)
        np.testing.assert_array_equal(out.argvals, finer)

    def test_interpolate_per_curve_values(self, fd_linear):
        """fd.interpolate() delegates correctly to spline_interpolate_with_policy."""
        finer = np.linspace(0.0, 1.0, 21, dtype=np.float64)
        out = fd_linear.interpolate(finer)
        # Curve 0: y = 1*t, curve 1: y = 2*t
        np.testing.assert_allclose(out.data[0], finer, atol=1e-3)
        np.testing.assert_allclose(out.data[1], 2 * finer, atol=1e-3)

    def test_impute_returns_fdata(self, fd_with_nan):
        out = fd_with_nan.impute()
        assert isinstance(out, Fdata)

    def test_impute_removes_all_nan(self, fd_with_nan):
        out = fd_with_nan.impute()
        assert not np.isnan(out.data).any()

    def test_impute_argvals_unchanged(self, fd_with_nan):
        out = fd_with_nan.impute()
        np.testing.assert_array_equal(out.argvals, fd_with_nan.argvals)

    def test_impute_constant_method(self, fd_with_nan):
        out = fd_with_nan.impute(method="constant", constant_value=-99.0)
        assert not np.isnan(out.data).any()
        # NaN at (0, 2) → -99
        np.testing.assert_allclose(out.data[0, 2], -99.0, atol=1e-12)


class TestFdataResampleMethods:
    """Fdata.resample(), Fdata.upsample(), and Fdata.downsample() convenience methods."""

    @pytest.fixture
    def fd_11(self):
        """Two linear curves on [0, 1] with 11 evaluation points."""
        t = np.linspace(0.0, 1.0, 11, dtype=np.float64)
        data = np.stack(
            [(i + 1) * t for i in range(2)],
            axis=0, dtype=np.float64,
        )
        return Fdata(data, argvals=t)

    @pytest.fixture
    def fd_10(self):
        """Two linear curves on [0, 1] with 10 evaluation points."""
        t = np.linspace(0.0, 1.0, 10, dtype=np.float64)
        data = np.stack(
            [(i + 1) * t for i in range(2)],
            axis=0, dtype=np.float64,
        )
        return Fdata(data, argvals=t)

    # ---- resample(n_points=...) ----

    def test_resample_n_points_count(self, fd_11):
        out = fd_11.resample(n_points=5)
        assert out.n_points == 5

    def test_resample_n_points_argvals_linspace(self, fd_11):
        out = fd_11.resample(n_points=5)
        expected = np.linspace(fd_11.rangeval[0], fd_11.rangeval[1], 5)
        np.testing.assert_allclose(out.argvals, expected, atol=1e-12)

    def test_resample_n_obs_preserved(self, fd_11):
        out = fd_11.resample(n_points=5)
        assert out.n_obs == fd_11.n_obs

    def test_resample_returns_new_object(self, fd_11):
        out = fd_11.resample(n_points=5)
        assert out is not fd_11

    def test_resample_returns_fdata(self, fd_11):
        out = fd_11.resample(n_points=5)
        assert isinstance(out, Fdata)

    # ---- resample(factor=...) ----

    def test_resample_factor_count(self, fd_11):
        out = fd_11.resample(factor=2)
        assert out.n_points == 22  # round(11 * 2) = 22

    def test_resample_factor_obs_preserved(self, fd_11):
        out = fd_11.resample(factor=2)
        assert out.n_obs == fd_11.n_obs

    # ---- resample error paths ----

    def test_resample_neither_arg_raises(self, fd_11):
        with pytest.raises(ValueError):
            fd_11.resample()

    def test_resample_both_args_raises(self, fd_11):
        with pytest.raises(ValueError):
            fd_11.resample(n_points=5, factor=2)

    def test_resample_target_less_than_2_raises(self, fd_11):
        with pytest.raises(ValueError):
            fd_11.resample(n_points=1)

    # ---- upsample ----

    def test_upsample_count_ceil(self, fd_11):
        out = fd_11.upsample(2)
        assert out.n_points == 22  # ceil(11 * 2) = 22

    def test_upsample_strictly_greater(self, fd_11):
        out = fd_11.upsample(2)
        assert out.n_points > fd_11.n_points

    def test_upsample_n_obs_preserved(self, fd_11):
        out = fd_11.upsample(2)
        assert out.n_obs == fd_11.n_obs

    def test_upsample_returns_fdata(self, fd_11):
        out = fd_11.upsample(2)
        assert isinstance(out, Fdata)

    def test_upsample_factor_equal_1_raises(self, fd_11):
        with pytest.raises(ValueError):
            fd_11.upsample(1.0)

    def test_upsample_factor_less_than_1_raises(self, fd_11):
        with pytest.raises(ValueError):
            fd_11.upsample(0.5)

    # ---- downsample ----

    def test_downsample_count(self, fd_10):
        out = fd_10.downsample(2)
        assert out.n_points == 5  # int(10 / 2) = 5

    def test_downsample_strictly_fewer(self, fd_10):
        out = fd_10.downsample(2)
        assert out.n_points < fd_10.n_points

    def test_downsample_n_obs_preserved(self, fd_10):
        out = fd_10.downsample(2)
        assert out.n_obs == fd_10.n_obs

    def test_downsample_returns_fdata(self, fd_10):
        out = fd_10.downsample(2)
        assert isinstance(out, Fdata)

    def test_downsample_factor_equal_1_raises(self, fd_10):
        with pytest.raises(ValueError):
            fd_10.downsample(1.0)

    def test_downsample_large_factor_clamps_to_2(self, fd_10):
        # int(10 / 100) = 0 — clamped to 2
        out = fd_10.downsample(100)
        assert out.n_points == 2
