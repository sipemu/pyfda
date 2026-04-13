"""Basic tests for fdars package."""

import numpy as np
import pytest


def test_import():
    """Verify the package can be imported."""
    import fdars
    assert hasattr(fdars, "__version__")
    assert fdars.__version__ == "0.1.0"


def test_submodules():
    """Verify all submodules are accessible."""
    from fdars import (
        fdata, depth, metric, basis, smoothing,
        clustering, regression, alignment, outliers,
        seasonal, spm, classification, tolerance,
        conformal, simulation, explain,
    )


class TestFdata:
    def test_mean_1d(self):
        from fdars.fdata import mean_1d
        data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        result = mean_1d(data)
        np.testing.assert_allclose(result, [2.5, 3.5, 4.5])

    def test_center_1d(self):
        from fdars.fdata import center_1d
        data = np.array([[1.0, 2.0, 3.0], [3.0, 4.0, 5.0]])
        result = center_1d(data)
        np.testing.assert_allclose(result, [[-1.0, -1.0, -1.0], [1.0, 1.0, 1.0]])

    def test_norm_lp_1d(self):
        from fdars.fdata import norm_lp_1d
        data = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        argvals = np.linspace(0, 1, 3)
        result = norm_lp_1d(data, argvals)
        assert len(result) == 2
        assert all(r >= 0 for r in result)

    def test_normalize(self):
        from fdars.fdata import normalize
        data = np.random.randn(10, 50)
        result = normalize(data, method="center")
        # centered data should have zero mean per column
        col_means = result.mean(axis=0)
        np.testing.assert_allclose(col_means, 0.0, atol=1e-10)


class TestDepth:
    def setup_method(self):
        np.random.seed(42)
        self.data = np.random.randn(20, 50)

    def test_fraiman_muniz(self):
        from fdars.depth import fraiman_muniz_1d
        depths = fraiman_muniz_1d(self.data, self.data)
        assert depths.shape == (20,)
        assert all(0 <= d <= 1 for d in depths)

    def test_modified_band(self):
        from fdars.depth import modified_band_1d
        depths = modified_band_1d(self.data, self.data)
        assert depths.shape == (20,)

    def test_random_projection(self):
        from fdars.depth import random_projection_1d
        depths = random_projection_1d(self.data, self.data, n_proj=10)
        assert depths.shape == (20,)


class TestMetric:
    def setup_method(self):
        np.random.seed(42)
        self.data = np.random.randn(10, 30)
        self.argvals = np.linspace(0, 1, 30)

    def test_lp_self(self):
        from fdars.metric import lp_self_1d
        dist = lp_self_1d(self.data, self.argvals, p=2.0)
        assert dist.shape == (10, 10)
        np.testing.assert_allclose(np.diag(dist), 0.0, atol=1e-10)

    def test_dtw_self(self):
        from fdars.metric import dtw_self_1d
        dist = dtw_self_1d(self.data)
        assert dist.shape == (10, 10)


class TestClustering:
    def test_kmeans(self):
        from fdars.clustering import kmeans_fd
        np.random.seed(42)
        data = np.vstack([np.random.randn(10, 30), np.random.randn(10, 30) + 3])
        argvals = np.linspace(0, 1, 30)
        result = kmeans_fd(data, argvals, k=2)
        assert "cluster" in result
        assert "centers" in result
        assert len(result["cluster"]) == 20


class TestRegression:
    def test_fregre_lm(self):
        from fdars.regression import fregre_lm
        np.random.seed(42)
        data = np.random.randn(30, 50)
        response = data.mean(axis=1) + 0.1 * np.random.randn(30)
        result = fregre_lm(data, response, n_comp=3)
        assert "fitted_values" in result
        assert "beta_t" in result
        assert "r_squared" in result

    def test_fpca(self):
        from fdars.regression import fpca
        np.random.seed(42)
        data = np.random.randn(20, 50)
        argvals = np.linspace(0, 1, 50)
        result = fpca(data, argvals, n_comp=3)
        assert "scores" in result
        assert "rotation" in result
        assert "singular_values" in result
        assert result["scores"].shape == (20, 3)


class TestAlignment:
    def test_elastic_distance(self):
        from fdars.alignment import elastic_distance
        argvals = np.linspace(0, 1, 100)
        c1 = np.sin(2 * np.pi * argvals)
        c2 = np.sin(2 * np.pi * argvals + 0.5)
        d = elastic_distance(c1, c2, argvals)
        assert d >= 0

    def test_srsf_transform(self):
        from fdars.alignment import srsf_transform
        argvals = np.linspace(0, 1, 100)
        curve = np.sin(2 * np.pi * argvals)
        srsf = srsf_transform(curve, argvals)
        assert len(srsf) == 100

    def test_elastic_align_pair(self):
        from fdars.alignment import elastic_align_pair
        argvals = np.linspace(0, 1, 100)
        c1 = np.sin(2 * np.pi * argvals)
        c2 = np.sin(2 * np.pi * (argvals ** 1.5))
        result = elastic_align_pair(c1, c2, argvals)
        assert "f_aligned" in result
        assert "gamma" in result
        assert "distance" in result


class TestSimulation:
    def test_simulate(self):
        from fdars.simulation import simulate
        argvals = np.linspace(0, 1, 100)
        data = simulate(20, argvals, n_basis=5)
        assert data.shape == (20, 100)

    def test_gaussian_process(self):
        from fdars.simulation import gaussian_process
        argvals = np.linspace(0, 1, 50)
        data = gaussian_process(10, argvals, kernel="gaussian")
        assert data.shape == (10, 50)


class TestOutliers:
    def test_outliergram(self):
        from fdars.outliers import outliergram
        np.random.seed(42)
        data = np.random.randn(20, 50)
        result = outliergram(data)
        assert "mei" in result
        assert "mbd" in result
        assert "outliers" in result


class TestSPM:
    def test_spm_phase1(self):
        from fdars.spm import spm_phase1
        np.random.seed(42)
        data = np.random.randn(30, 50)
        argvals = np.linspace(0, 1, 50)
        result = spm_phase1(data, argvals, ncomp=3)
        assert "t2" in result
        assert "spe" in result
        assert "t2_limit" in result
        assert "spe_limit" in result


class TestTolerance:
    def test_fpca_tolerance_band(self):
        from fdars.tolerance import fpca_tolerance_band
        np.random.seed(42)
        data = np.random.randn(30, 50)
        result = fpca_tolerance_band(data, ncomp=3, nb=100)
        assert "upper" in result
        assert "lower" in result
        assert "center" in result
