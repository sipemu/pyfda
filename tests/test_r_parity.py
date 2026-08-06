"""Tests for the R-parity additions (phase 1 batches A-G + phase 4 ergonomics).

Each test asserts a ground-truth numerical property, mirroring the smoke-test
validations used when the bindings were added.
"""

import numpy as np
import pytest


# ─────────────────────────── Batch A ────────────────────────────────────────
class TestBatchA:
    def test_rpd_depth(self):
        from fdars import depth

        rng = np.random.default_rng(0)
        X = rng.standard_normal((20, 40))
        R = rng.standard_normal((30, 40))
        av = np.linspace(0, 1, 40)
        d = depth.random_projection_deriv_1d(X, R, av, n_proj=30, n_deriv=1, seed=1)
        assert d.shape == (20,)
        assert np.isfinite(d).all()
        # determinism given a seed
        d2 = depth.random_projection_deriv_1d(X, R, av, n_proj=30, n_deriv=1, seed=1)
        np.testing.assert_allclose(d, d2)

    def test_int_simpson(self):
        from fdars import metric

        # integral of the constant 1 over [0,1] == 1
        ones = np.ones((3, 51))
        np.testing.assert_allclose(metric.int_simpson(ones), 1.0, atol=1e-9)
        # integral of t and 2t over [0,1] == 0.5 and 1.0
        t = np.linspace(0, 1, 201)
        ramp = np.vstack([t, 2 * t])
        np.testing.assert_allclose(metric.int_simpson(ramp, t), [0.5, 1.0], atol=1e-6)

    def test_inprod(self):
        from fdars import metric

        ones = np.ones((3, 50))
        g = metric.inprod(ones, ones)
        assert g.shape == (3, 3)
        np.testing.assert_allclose(g, 1.0, atol=1e-9)

    def test_andrews(self):
        from fdars import explain

        X = np.random.default_rng(1).standard_normal((15, 6))
        at = explain.andrews_transform(X, n_grid=64)
        assert at["curves"].shape == (15, 64)
        assert at["argvals"].shape == (64,)
        assert at["n_vars"] == 6
        al = explain.andrews_loadings(X[:3], n_grid=64)
        # one Andrews curve per original variable
        assert al["loadings"].shape == (6, 64)
        assert al["n_vars"] == 3


# ─────────────────────────── Batch B ────────────────────────────────────────
class TestBatchB:
    def _seasonal_data(self, period_frac=1.0):
        t = np.linspace(0, 10, 200)
        rng = np.random.default_rng(3)
        X = np.vstack(
            [np.sin(2 * np.pi * t / period_frac) + 0.1 * rng.standard_normal(200)
             for _ in range(8)]
        )
        return X, t

    def test_estimate_period_acf(self):
        from fdars import seasonal

        X, t = self._seasonal_data()
        acf = seasonal.estimate_period_acf(X, t)
        assert set(acf) >= {"period", "frequency", "power", "confidence"}
        assert acf["period"] == pytest.approx(1.0, abs=0.1)

    def test_detect_multiple_periods(self):
        from fdars import seasonal

        X, t = self._seasonal_data()
        periods = seasonal.detect_multiple_periods(X, t, max_periods=3)
        assert len(periods) >= 1
        assert periods[0]["period"] == pytest.approx(1.0, abs=0.1)
        assert periods[0]["iteration"] == 1


# ─────────────────────────── Batch C ────────────────────────────────────────
class TestBatchC:
    def _shifted_peaks(self):
        t = np.linspace(0, 1, 120)
        rng = np.random.default_rng(0)
        centers = 0.3 + 0.4 * rng.random(10)
        X = np.vstack([np.exp(-((t - c) ** 2) / 0.005) for c in centers])
        return X, t

    def test_detect_landmarks(self):
        from fdars import alignment

        X, t = self._shifted_peaks()
        lms = alignment.detect_landmarks(X[0], t, kind="peak", min_prominence=0.1)
        assert len(lms) == 1
        assert lms[0]["kind"] == "peak"
        assert 0.0 <= lms[0]["position"] <= 1.0

    def test_landmark_detect_and_register(self):
        from fdars import alignment

        X, t = self._shifted_peaks()
        before = t[np.argmax(X, axis=1)].std()
        res = alignment.landmark_detect_and_register(
            X, t, kind="peak", min_prominence=0.1, expected_count=1
        )
        after = t[np.argmax(res["registered"], axis=1)].std()
        assert res["registered"].shape == X.shape
        assert res["gammas"].shape == X.shape
        # registration concentrates the peak locations
        assert after <= before

    def test_landmark_register_explicit(self):
        from fdars import alignment

        X, t = self._shifted_peaks()
        peaks = t[np.argmax(X, axis=1)]
        res = alignment.landmark_register(X, t, [[float(p)] for p in peaks], target=[0.5])
        after = t[np.argmax(res["registered"], axis=1)].std()
        assert after < peaks.std()

    def test_bad_kind_raises(self):
        from fdars import alignment

        t = np.linspace(0, 1, 20)
        with pytest.raises(ValueError):
            alignment.detect_landmarks(np.sin(t), t, kind="nonsense")


# ─────────────────────────── Batch D ────────────────────────────────────────
class TestBatchD:
    def _reg_data(self):
        rng = np.random.default_rng(0)
        n, m = 60, 40
        t = np.linspace(0, 1, m)
        X = np.vstack(
            [np.sin(2 * np.pi * t * (1 + 0.5 * rng.random())) + 0.1 * rng.standard_normal(m)
             for _ in range(n)]
        )
        beta = np.exp(-((t - 0.5) ** 2) / 0.05)
        y = X @ beta / m + 0.05 * rng.standard_normal(n)
        return X, y, t

    def test_fregre_np_cv(self):
        from fdars import regression

        X, y, t = self._reg_data()
        cv = regression.fregre_np_cv(X, y, t, n_folds=5)
        assert cv["optimal_h"] > 0
        assert np.isfinite(cv["min_cv_error"])
        assert cv["h_values"].shape == cv["cv_errors"].shape

    def test_fregre_np_mixed(self):
        from fdars import regression

        X, y, t = self._reg_data()
        mix = regression.fregre_np_mixed(X, y, t, h_func=0.2)
        assert mix["fitted_values"].shape == (X.shape[0],)
        assert mix["r_squared"] <= 1.0 + 1e-9
        # with scalar covariates
        Z = np.random.default_rng(1).standard_normal((X.shape[0], 2))
        mix2 = regression.fregre_np_mixed(X, y, t, h_func=0.2, scalar_covariates=Z)
        assert np.isfinite(mix2["r_squared"])


# ─────────────────────────── Batch E ────────────────────────────────────────
class TestBatchE:
    def _monitoring_data(self):
        m = 50
        t = np.linspace(0, 1, m)
        rng = np.random.default_rng(0)

        def base(n, shift=0.0):
            return np.vstack(
                [np.sin(2 * np.pi * t) + shift + 0.05 * rng.standard_normal(m)
                 for _ in range(n)]
            )

        train = base(80)
        seq = np.vstack([base(20), base(20, shift=0.8)])  # last 20 out-of-control
        return train, seq, t

    def test_spm_cusum_detects_shift(self):
        from fdars import spm

        train, seq, t = self._monitoring_data()
        cu = spm.spm_cusum(train, seq, t, ncomp=4, k=0.5, h=5.0)
        assert cu["cusum_statistic"].shape == (40,)
        # more alarms in the out-of-control half than in-control
        assert cu["alarm"][20:].sum() > cu["alarm"][:20].sum()

    def test_spm_ewma_detects_shift(self):
        from fdars import spm

        train, seq, t = self._monitoring_data()
        ew = spm.spm_ewma(train, seq, t, ncomp=4, lam=0.2)
        assert ew["t2"].shape == (40,)
        assert ew["t2_alarm"][20:].sum() > ew["t2_alarm"][:20].sum()

    def test_robust_limits(self):
        from fdars import spm

        rng = np.random.default_rng(0)
        rl = spm.t2_limit_robust(np.abs(rng.standard_normal(100)) + 2, ncomp=4, method="empirical")
        sl = spm.spe_limit_robust(np.abs(rng.standard_normal(100)), method="parametric")
        assert rl["ucl"] > 0 and sl["ucl"] > 0

    def test_bad_method_raises(self):
        from fdars import spm

        with pytest.raises(ValueError):
            spm.spe_limit_robust(np.ones(20), method="bogus")


# ─────────────────────────── Batch F ────────────────────────────────────────
class TestBatchF:
    def _changepoint_data(self):
        m = 40
        t = np.linspace(0, 1, m)
        rng = np.random.default_rng(0)
        X = np.vstack(
            [1.0 * np.sin(2 * np.pi * t) + 0.05 * rng.standard_normal(m) for _ in range(15)]
            + [2.0 * np.sin(2 * np.pi * t) + 0.05 * rng.standard_normal(m) for _ in range(15)]
        )
        return X, t

    def test_amplitude_changepoint(self):
        from fdars import alignment

        X, t = self._changepoint_data()
        amp = alignment.elastic_changepoint(X, t, kind="amplitude", n_mc=100, seed=1)
        assert 10 <= amp["changepoint"] <= 20
        assert amp["p_value"] < 0.05
        assert amp["cusum_values"].shape == (X.shape[0] - 1,)

    def test_phase_variant_not_significant(self):
        from fdars import alignment

        X, t = self._changepoint_data()
        # an amplitude change should NOT be flagged in phase space
        ph = alignment.elastic_changepoint(X, t, kind="phase", n_mc=100, seed=1)
        assert ph["p_value"] > 0.05

    def test_fpca_variant(self):
        from fdars import alignment

        X, t = self._changepoint_data()
        fp = alignment.elastic_changepoint(
            X, t, kind="fpca", ncomp=3, pca_method="joint", n_mc=100, seed=1
        )
        assert fp["p_value"] < 0.05

    def test_bad_kind_raises(self):
        from fdars import alignment

        t = np.linspace(0, 1, 20)
        with pytest.raises(ValueError):
            alignment.elastic_changepoint(np.random.rand(10, 20), t, kind="bogus")


# ─────────────────────────── Batch G ────────────────────────────────────────
class TestMetrics:
    def test_pred_metrics(self):
        from fdars import metrics

        yt = np.array([1.0, 2, 3, 4])
        yp = np.array([1.1, 1.9, 3.2, 3.7])
        assert metrics.pred_mae(yt, yp) == pytest.approx(0.175)
        assert metrics.pred_mse(yt, yp) == pytest.approx(0.0375)
        assert metrics.pred_rmse(yt, yp) == pytest.approx(np.sqrt(0.0375))
        assert metrics.pred_r2(yt, yt) == pytest.approx(1.0)
        d = metrics.prediction_metrics(yt, yp)
        assert set(d) == {"mae", "mse", "rmse", "r2"}

    def test_r2_zero_variance_is_nan(self):
        from fdars import metrics

        assert np.isnan(metrics.pred_r2(np.ones(5), np.arange(5.0)))

    def test_shape_mismatch_raises(self):
        from fdars import metrics

        with pytest.raises(ValueError):
            metrics.pred_mae(np.ones(3), np.ones(4))


class TestCovariance:
    def test_gaussian_kernel_properties(self):
        from fdars import covariance

        t = np.linspace(0, 1, 40)
        k = covariance.kernel_gaussian(0.1, 1.0)
        K = k(t, t)
        assert K.shape == (40, 40)
        np.testing.assert_allclose(np.diag(K), 1.0)
        np.testing.assert_allclose(K, K.T)

    def test_matern_only_supported_nu(self):
        from fdars import covariance

        t = np.linspace(0, 1, 10)
        covariance.kernel_matern(1.0, 1.5)(t, t)  # ok
        with pytest.raises(ValueError):
            covariance.kernel_matern(1.0, 0.7)(t, t)

    def test_kernel_composition(self):
        from fdars import covariance

        t = np.linspace(0, 1, 20)
        k = covariance.kernel_add(
            covariance.kernel_gaussian(0.2), covariance.kernel_whitenoise(0.1)
        )
        K = k(t, t)
        assert K.shape == (20, 20)
        # white-noise adds only to the diagonal
        assert np.diag(K).min() > (K - np.diag(np.diag(K))).max()

    def test_make_gaussian_process(self):
        from fdars import covariance

        t = np.linspace(0, 1, 50)
        gp = covariance.make_gaussian_process(t, covariance.kernel_gaussian(0.15), n=5, seed=0)
        assert gp.shape == (5, 50)
        assert np.isfinite(gp).all()

    def test_samplers(self):
        from fdars import covariance

        t = np.linspace(0, 1, 60)
        bm = covariance.r_brownian(4, argvals=t, seed=1)
        assert bm.shape == (4, 60)
        np.testing.assert_allclose(bm[:, 0], 0.0)
        br = covariance.r_bridge(4, argvals=t, seed=1)
        np.testing.assert_allclose(br[:, 0], 0.0, atol=1e-9)
        np.testing.assert_allclose(br[:, -1], 0.0, atol=1e-9)
        ou = covariance.r_ou(4, argvals=t, theta=2.0, mu=0.0, sigma=0.5, x0=1.0, seed=1)
        np.testing.assert_allclose(ou[:, 0], 1.0)


class TestClusterTools:
    def _two_clusters(self):
        t = np.linspace(0, 1, 50)
        X = np.vstack(
            [np.sin(2 * np.pi * t) + 0.05 * np.random.default_rng(i).standard_normal(50)
             for i in range(15)]
            + [np.cos(2 * np.pi * t) + 0.05 * np.random.default_rng(i + 100).standard_normal(50)
               for i in range(15)]
        )
        return X, t

    def test_cluster_optim_recovers_k(self):
        from fdars import clustering

        X, t = self._two_clusters()
        opt = clustering.cluster_optim(X, t, k_range=[2, 3, 4], criterion="silhouette")
        assert opt["best_k"] == 2
        assert opt["scores"].shape == (3,)

    def test_cluster_init_kpp(self):
        from fdars import clustering

        X, t = self._two_clusters()
        init = clustering.cluster_init(X, k=3, seed=0)
        assert init["centers"].shape == (3, 50)
        assert init["indices"].shape == (3,)
        assert len(set(init["indices"].tolist())) == 3  # distinct centers


# ─────────────────────────── Phase 4: ergonomics ────────────────────────────
class TestDatasets:
    @pytest.mark.parametrize(
        "loader,shape",
        [("load_growth", (93, 31)), ("load_tecator", (240, 100)), ("load_sonar", (208, 60))],
    )
    def test_dataset_loads_as_fdata(self, loader, shape):
        from fdars import datasets, Fdata

        d = getattr(datasets, loader)()
        assert isinstance(d.data, Fdata)
        assert d.data.shape == shape


class TestResults:
    def test_fregre_wrapper_predict_matches_free_fn(self):
        from fdars import regression, results

        rng = np.random.default_rng(0)
        n, m = 40, 30
        t = np.linspace(0, 1, m)
        X = np.vstack([np.sin(2 * np.pi * t * (1 + rng.random())) for _ in range(n)])
        y = X.mean(axis=1) + 0.01 * rng.standard_normal(n)
        fit = regression.fregre_lm(X, y, n_comp=3)
        wrapped = results.wrap_fregre(fit, "lm", X, y, n_comp=3)
        pred = wrapped.predict(X)
        free = regression.predict_fregre_lm(X, y, X, n_comp=3)
        np.testing.assert_allclose(pred, free, rtol=1e-8)
        assert "FregreResult" in repr(wrapped)
        wrapped.summary()  # prints; must not raise


class TestFdataMethods:
    def test_int_simpson_method(self):
        from fdars import Fdata

        t = np.linspace(0, 1, 201)
        fd = Fdata(np.vstack([t, 2 * t]), argvals=t)
        np.testing.assert_allclose(fd.int_simpson(), [0.5, 1.0], atol=1e-6)

    def test_scale_minmax(self):
        from fdars import Fdata

        t = np.linspace(0, 1, 40)
        fd = Fdata(np.random.default_rng(0).standard_normal((5, 40)), argvals=t)
        sm = fd.scale_minmax()
        assert float(np.min(sm.data)) == pytest.approx(0.0)
        assert float(np.max(sm.data)) == pytest.approx(1.0)

    def test_concat(self):
        from fdars import Fdata

        t = np.linspace(0, 1, 20)
        a = Fdata(np.zeros((3, 20)), argvals=t)
        b = Fdata(np.ones((2, 20)), argvals=t)
        c = a.concat(b)
        assert c.n_obs == 5

    def test_norm_2d_no_longer_raises(self):
        from fdars import Fdata

        t = np.linspace(0, 1, 15)
        fd = Fdata(np.random.default_rng(0).standard_normal((4, 15)), argvals=t)
        assert np.asarray(fd.norm()).shape[0] == 4


class TestPlot:
    def test_plot_fdata_smoke(self):
        matplotlib = pytest.importorskip("matplotlib")
        matplotlib.use("Agg")
        from fdars import plot, Fdata

        t = np.linspace(0, 1, 30)
        fd = Fdata(np.random.default_rng(0).standard_normal((6, 30)), argvals=t)
        ax = plot.plot_fdata(fd)
        assert ax is not None
