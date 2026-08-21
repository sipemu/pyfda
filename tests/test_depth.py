"""Tests for fdars.depth submodule — functional_depth and functional_boxplot.

Covers:
- functional_depth: string dispatch to four DepthMethod variants (Task 1)
- functional_boxplot: 7-key dict contract, layout guard, degenerate inputs (Task 2)

Dataset: Canadian Weather temperature (35 stations × 365 daily points).
Test slices use first 12 stations for fast CI.  RandomProjection tests use
nproj=20 to keep CI times low.
"""

import numpy as np
import pytest

from fdars.datasets import load_canadian_weather


# ---------------------------------------------------------------------------
# Fixture: small Canadian Weather temperature subset
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cw_temp():
    """Return X — shape (12, 365) temperature matrix."""
    _, X, _ = load_canadian_weather("temperature", return_fdata=False)
    return X[:12, :]


# ---------------------------------------------------------------------------
# Task 1: functional_depth import and shape tests
# ---------------------------------------------------------------------------


class TestImportPaths:
    """Both import styles must resolve the same callable."""

    def test_import_submodule(self):
        import fdars.depth  # noqa: F401

    def test_from_import_functional_depth(self):
        from fdars.depth import functional_depth  # noqa: F401

    def test_functional_depth_callable(self):
        import fdars.depth

        assert callable(fdars.depth.functional_depth)

    def test_functional_boxplot_callable(self):
        import fdars.depth

        assert callable(fdars.depth.functional_boxplot)


class TestFunctionalDepthShape:
    """functional_depth returns ndarray of shape (n,) for all four methods."""

    @pytest.mark.parametrize("method", ["fraiman_muniz", "band", "modified_band"])
    def test_shape_standard_methods(self, cw_temp, method):
        import fdars.depth

        X = cw_temp
        n = X.shape[0]
        result = fdars.depth.functional_depth(X, method=method)
        assert isinstance(result, np.ndarray)
        assert result.shape == (n,), f"Expected ({n},), got {result.shape}"
        assert np.isfinite(result).all(), "depth values must all be finite"

    def test_shape_random_projection(self, cw_temp):
        import fdars.depth

        X = cw_temp
        n = X.shape[0]
        result = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=7)
        assert result.shape == (n,)
        assert np.isfinite(result).all()


class TestFunctionalDepthCrossCheck:
    """functional_depth with method='fraiman_muniz' == fraiman_muniz_1d self-depth."""

    def test_fraiman_muniz_crosscheck_scale_true(self, cw_temp):
        import fdars.depth

        X = cw_temp
        d_unified = fdars.depth.functional_depth(X, method="fraiman_muniz", scale=True)
        d_legacy = fdars.depth.fraiman_muniz_1d(X, X, scale=True)
        assert np.allclose(d_unified, d_legacy), (
            "functional_depth(fraiman_muniz, scale=True) must equal fraiman_muniz_1d(X, X, scale=True)"
        )

    def test_fraiman_muniz_crosscheck_scale_false(self, cw_temp):
        import fdars.depth

        X = cw_temp
        d_unified = fdars.depth.functional_depth(X, method="fraiman_muniz", scale=False)
        d_legacy = fdars.depth.fraiman_muniz_1d(X, X, scale=False)
        assert np.allclose(d_unified, d_legacy)


class TestFunctionalDepthDeterminism:
    """random_projection depth is byte-identical across calls with the same seed."""

    def test_explicit_seed_determinism(self, cw_temp):
        import fdars.depth

        X = cw_temp
        d1 = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=7)
        d2 = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=7)
        assert np.array_equal(d1, d2), "Same explicit seed must give byte-identical results"

    def test_seed_none_determinism(self, cw_temp):
        import fdars.depth

        X = cw_temp
        d1 = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=None)
        d2 = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=None)
        assert np.array_equal(d1, d2), "seed=None must resolve to a fixed default giving identical results"

    def test_seed_none_equals_seed_zero(self, cw_temp):
        """Documented contract: seed=None resolves to seed=0."""
        import fdars.depth

        X = cw_temp
        d_none = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=None)
        d_zero = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=0)
        assert np.array_equal(d_none, d_zero), "seed=None must equal seed=0 (documented contract)"


class TestFunctionalDepthValueErrors:
    """Degenerate inputs raise ValueError."""

    def test_unknown_method_raises(self, cw_temp):
        import fdars.depth

        with pytest.raises(ValueError, match="not_a_method"):
            fdars.depth.functional_depth(cw_temp, method="not_a_method")

    def test_unknown_method_lists_new_tokens(self, cw_temp):
        """Rewritten wildcard error message lists all 13 supported methods (incl. new ones)."""
        import fdars.depth

        with pytest.raises(ValueError, match="total_variation"):
            fdars.depth.functional_depth(cw_temp, method="not_a_method")

    def test_empty_data_raises(self):
        import fdars.depth

        empty = np.zeros((0, 365))
        with pytest.raises(ValueError):
            fdars.depth.functional_depth(empty, method="fraiman_muniz")

    def test_single_curve_band_raises(self):
        import fdars.depth

        one_curve = np.random.default_rng(0).standard_normal((1, 20))
        with pytest.raises(ValueError):
            fdars.depth.functional_depth(one_curve, method="band")

    def test_single_curve_modified_band_raises(self):
        import fdars.depth

        one_curve = np.random.default_rng(0).standard_normal((1, 20))
        with pytest.raises(ValueError):
            fdars.depth.functional_depth(one_curve, method="modified_band")

    def test_nproj_zero_raises(self, cw_temp):
        import fdars.depth

        with pytest.raises(ValueError):
            fdars.depth.functional_depth(cw_temp, method="random_projection", nproj=0)


# ---------------------------------------------------------------------------
# Task 2: functional_boxplot dict contract and layout guard
# ---------------------------------------------------------------------------


class TestFunctionalBoxplotDictContract:
    """functional_boxplot returns exactly the 7 required keys."""

    def test_key_set(self, cw_temp):
        import fdars.depth

        res = fdars.depth.functional_boxplot(cw_temp, method="modified_band", factor=1.5)
        assert isinstance(res, dict)
        assert set(res.keys()) == {
            "median",
            "central_lower",
            "central_upper",
            "whisker_lower",
            "whisker_upper",
            "outliers",
            "depths",
        }


class TestFunctionalBoxplotLayoutGuard:
    """Band fields have length m (not n); depths length n; outliers a Python list."""

    def test_band_fields_shape_and_finite(self, cw_temp):
        import fdars.depth

        X = cw_temp
        n, m = X.shape
        res = fdars.depth.functional_boxplot(X, method="modified_band", factor=1.5)
        for key in ("median", "central_lower", "central_upper", "whisker_lower", "whisker_upper"):
            arr = res[key]
            assert isinstance(arr, np.ndarray), f"{key} must be ndarray"
            assert arr.shape == (m,), f"{key}: expected ({m},), got {arr.shape}"
            assert np.isfinite(arr).all(), f"{key} must be all finite"

    def test_depths_shape(self, cw_temp):
        import fdars.depth

        X = cw_temp
        n = X.shape[0]
        res = fdars.depth.functional_boxplot(X, method="modified_band", factor=1.5)
        assert res["depths"].shape == (n,), f"depths: expected ({n},), got {res['depths'].shape}"
        assert np.isfinite(res["depths"]).all()

    def test_outliers_is_python_list_of_ints(self, cw_temp):
        import fdars.depth

        X = cw_temp
        n = X.shape[0]
        res = fdars.depth.functional_boxplot(X, method="modified_band", factor=1.5)
        outliers = res["outliers"]
        assert isinstance(outliers, list), "outliers must be a Python list"
        for o in outliers:
            assert isinstance(o, int), f"each outlier must be a Python int, got {type(o)}"
            assert 0 <= o < n, f"outlier index {o} out of range [0, {n})"

    def test_no_transposition_guard(self, cw_temp):
        """Band field lengths must equal m (cols), not n (rows), when n != m."""
        import fdars.depth

        X = cw_temp
        n, m = X.shape
        assert n != m, "fixture must have n != m for transposition guard to be meaningful"
        res = fdars.depth.functional_boxplot(X, method="modified_band", factor=1.5)
        for key in ("median", "central_lower", "central_upper", "whisker_lower", "whisker_upper"):
            arr = res[key]
            assert arr.shape[0] != n or arr.shape[0] == m, (
                f"{key} length {arr.shape[0]} equals n={n} — possible transposition"
            )
            assert arr.shape == (m,)


class TestFunctionalBoxplotValueErrors:
    """Degenerate inputs raise ValueError."""

    def test_empty_data_raises(self):
        import fdars.depth

        empty = np.zeros((0, 365))
        with pytest.raises(ValueError):
            fdars.depth.functional_boxplot(empty, method="modified_band", factor=1.5)

    def test_single_curve_raises(self):
        import fdars.depth

        one_curve = np.random.default_rng(1).standard_normal((1, 20))
        with pytest.raises(ValueError):
            fdars.depth.functional_boxplot(one_curve, method="modified_band", factor=1.5)

    def test_negative_factor_raises(self, cw_temp):
        import fdars.depth

        with pytest.raises(ValueError):
            fdars.depth.functional_boxplot(cw_temp, method="modified_band", factor=-1.0)

    def test_unknown_method_raises(self, cw_temp):
        import fdars.depth

        with pytest.raises(ValueError, match="not_a_method"):
            fdars.depth.functional_boxplot(cw_temp, method="not_a_method", factor=1.5)

    def test_unknown_method_boxplot_lists_new_tokens(self, cw_temp):
        """Boxplot wildcard error message also lists the new tokens (same dispatcher)."""
        import fdars.depth

        with pytest.raises(ValueError, match="total_variation"):
            fdars.depth.functional_boxplot(cw_temp, method="not_a_method", factor=1.5)

    def test_random_projection_boxplot_small_nproj(self, cw_temp):
        """RandomProjection boxplot with small nproj works and is seed-reproducible."""
        import fdars.depth

        X = cw_temp
        r1 = fdars.depth.functional_boxplot(
            X, method="random_projection", factor=1.5, nproj=20, seed=42
        )
        r2 = fdars.depth.functional_boxplot(
            X, method="random_projection", factor=1.5, nproj=20, seed=42
        )
        assert np.array_equal(r1["depths"], r2["depths"]), "boxplot depths must be seed-reproducible"
        assert np.array_equal(r1["median"], r2["median"])


class TestFunctionalDepthNewVariants:
    """Task 1 tracer + Task 2 extension: 9 new DepthMethod tokens dispatch end-to-end."""

    def test_total_variation_dispatch(self):
        """Tracer: total_variation dispatches through functional_depth to a finite (10,) array."""
        import fdars.depth

        data = np.random.default_rng(0).standard_normal((10, 20))
        result = fdars.depth.functional_depth(data, method="total_variation")
        assert isinstance(result, np.ndarray)
        assert result.shape == (10,)
        assert np.all(np.isfinite(result))

    @pytest.mark.parametrize(
        "method",
        [
            "hypograph_index",
            "modified_hypograph_index",
            "epigraph_index",
            "half_region",
            "modified_half_region",
            "extremal",
            "extreme_rank_length",
            "l_infinity",
            "total_variation",
        ],
    )
    def test_new_variant_finite(self, method):
        """All 9 new tokens return a finite (10,) array (n=10 satisfies every min-n guard)."""
        import fdars.depth

        data = np.random.default_rng(0).standard_normal((10, 20))
        result = fdars.depth.functional_depth(data, method=method)
        assert isinstance(result, np.ndarray)
        assert result.shape == (10,), f"{method}: expected (10,), got {result.shape}"
        assert np.all(np.isfinite(result)), f"{method}: result contains non-finite values"


class TestFunctionalBoxplotNewMethods:
    """Task 2: functional_boxplot accepts the new DepthMethod tokens and returns 7-key dict."""

    @pytest.mark.parametrize("method", ["total_variation", "hypograph_index", "extremal"])
    def test_boxplot_accepts_new_methods(self, method):
        """Representative subset of new tokens accepted by functional_boxplot."""
        import fdars.depth

        data = np.random.default_rng(42).standard_normal((10, 20))
        result = fdars.depth.functional_boxplot(data, method=method)
        assert isinstance(result, dict)
        assert set(result.keys()) == {
            "median",
            "central_lower",
            "central_upper",
            "whisker_lower",
            "whisker_upper",
            "outliers",
            "depths",
        }, f"{method}: unexpected keys {set(result.keys())}"


class TestFunctionalBoxplotDeterminism:
    """seed=None must equal seed=0 for functional_boxplot (documented contract)."""

    def test_boxplot_seed_none_equals_seed_zero(self, cw_temp):
        """Documented contract: seed=None resolves to seed=0 for functional_boxplot."""
        import fdars.depth

        X = cw_temp
        r_none = fdars.depth.functional_boxplot(
            X, method="random_projection", factor=1.5, nproj=20, seed=None
        )
        r_zero = fdars.depth.functional_boxplot(
            X, method="random_projection", factor=1.5, nproj=20, seed=0
        )
        assert np.array_equal(r_none["depths"], r_zero["depths"]), (
            "seed=None must equal seed=0 for boxplot depths (documented contract)"
        )
        assert np.array_equal(r_none["median"], r_zero["median"]), (
            "seed=None must equal seed=0 for boxplot median (documented contract)"
        )
