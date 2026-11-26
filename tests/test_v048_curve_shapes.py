"""Batch 4 (fdars-core 0.48): R^d curve shape space, (a, b) elastic metrics,
exact piecewise-linear distance and sparse / irregular elastic curves.

Correctness checks: quotient invariances (rotation, scale, translation,
reparametrisation, closed-curve seed), metric axioms, (a, b) = (1, 1/2)
reducing to the SRVF, exact PL distance vs the dense DP, sparse vs dense
elastic distance, and the ValueError paths.
"""

from __future__ import annotations

import numpy as np
import pytest

from fdars import alignment as al
from fdars import pace_fpca

M = 60
T = np.linspace(0.0, 1.0, M)


def wave(m=M, amp=0.3, freq=6.0, warp=None):
    t = np.linspace(0.0, 1.0, m)
    s = t if warp is None else warp(t)
    return np.vstack([s, amp * np.sin(freq * s)])


def rot2(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def ellipse(m, a=1.5, b=0.8, phase=0.0):
    th = 2 * np.pi * np.arange(m) / (m - 1) + phase
    return np.vstack([a * np.cos(th), b * np.sin(th)])


def bump_family(n=6, m=30, base=0.1, step=0.08):
    t = np.linspace(0.0, 1.0, m)
    return np.stack([np.vstack([t, (base + step * i) * np.sin(np.pi * t)]) for i in range(n)])


def turtle(angles, lengths):
    pts = [np.zeros(2)]
    for a, l in zip(angles, lengths):
        pts.append(pts[-1] + l * np.array([np.cos(a), np.sin(a)]))
    return np.array(pts).T


def sample_polygon(c, m):
    """Sample a polygon uniformly in arc length (vertices are hit when m is fine)."""
    seg = np.diff(c, axis=1)
    lens = np.hypot(*seg)
    cum = np.concatenate([[0.0], np.cumsum(lens)])
    s = np.linspace(0.0, cum[-1], m)
    return np.vstack([np.interp(s, cum, c[k]) for k in range(c.shape[0])])


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


class TestGeometry:
    def test_curve_srvf_straight_segment(self):
        m = 11
        beta = np.vstack([2 * np.linspace(0, 1, m), np.zeros(m)])
        q = al.curve_srvf(beta, scale=False)
        assert q.shape == (2, m)
        np.testing.assert_allclose(q[0], np.sqrt(2.0), atol=1e-12)
        np.testing.assert_allclose(q[1], 0.0, atol=1e-12)

    def test_curve_srvf_scale_unit_norm_and_scale_free(self):
        beta = wave()
        q = al.curve_srvf(beta)
        # scale removed: 5x the curve has the same unit-norm SRVF
        np.testing.assert_allclose(al.curve_srvf(5.0 * beta), q, atol=1e-12)
        assert np.trapezoid(np.sum(q**2, axis=0), T) == pytest.approx(1.0, abs=0.02)

    def test_srvf_round_trip(self):
        beta = wave()
        back = al.srvf_to_curve(al.curve_srvf(beta, scale=False))
        np.testing.assert_allclose(back, beta - beta[:, :1], atol=5e-3)

    def test_closure_residual_is_displacement(self):
        beta = wave()
        r = al.closure_residual(al.curve_srvf(beta, scale=False))
        np.testing.assert_allclose(r, beta[:, -1] - beta[:, 0], atol=5e-3)

    def test_project_closed_srvf(self):
        th = 1.5 * np.pi * np.linspace(0, 1, 101)
        q = al.curve_srvf(np.vstack([np.cos(th), np.sin(th)]))
        qc = al.project_closed_srvf(q)
        assert np.abs(al.closure_residual(qc)).max() < 1e-9
        assert np.abs(al.closure_residual(q)).max() > 0.1
        n = lambda x: np.sqrt(np.trapezoid(np.sum(x**2, axis=0), np.linspace(0, 1, 101)))
        assert n(qc) == pytest.approx(n(q), rel=1e-3)

    def test_project_closed_needs_d2(self):
        with pytest.raises(ValueError):
            al.project_closed_srvf(np.ones((1, 20)))

    def test_ab_srvf_special_case(self):
        beta = wave()
        np.testing.assert_allclose(
            al.ab_transform(beta, 1.0, 0.5), al.curve_srvf(beta, scale=False), atol=1e-12
        )
        f = al.ab_transform(beta, 1.0, 0.5)
        np.testing.assert_allclose(
            al.ab_closure_residual(f, 1.0, 0.5), al.closure_residual(f), atol=1e-12
        )

    @pytest.mark.parametrize("ab", [(1.0, 1.0), (1.0, 2.0)])
    def test_ab_inverse_round_trip(self, ab):
        # lambda = a/(2b) <= 1: left inverse up to translation and quadrature
        beta = wave()
        back = al.ab_transform_inverse(al.ab_transform(beta, *ab), *ab)
        np.testing.assert_allclose(back, beta - beta[:, :1], atol=1e-2)

    def test_ab_project_closed(self):
        th = 1.5 * np.pi * np.linspace(0, 1, 101)
        beta = np.vstack([np.cos(th), np.sin(th)])
        a, b = 1.0, 2.0
        f = al.ab_project_closed(al.ab_transform(beta, a, b), a, b)
        assert np.abs(al.ab_closure_residual(f, a, b)).max() < 1e-9
        c = al.ab_transform_inverse(f, a, b)
        np.testing.assert_allclose(c[:, -1], c[:, 0], atol=1e-9)

    def test_ab_errors(self):
        with pytest.raises(ValueError):
            al.ab_transform(np.ones((3, 20)), 1.0, 1.0)  # planar only
        with pytest.raises(ValueError):
            al.ab_transform(wave(), 0.0, 1.0)
        with pytest.raises(ValueError):
            al.ab_closure_residual(wave(), 1.0, -1.0)

    def test_optimal_rotation_recovers_rotation(self):
        q2 = np.vstack([1 + T, np.sin(3 * T)])
        R0 = rot2(0.6)
        R = al.optimal_rotation(R0 @ q2, q2)
        np.testing.assert_allclose(R, R0, atol=1e-12)
        assert np.linalg.det(R) == pytest.approx(1.0)

    def test_optimal_rotation_reflection(self):
        q2 = np.vstack([1 + T, np.sin(3 * T)])
        F = np.diag([1.0, -1.0])
        assert np.linalg.det(al.optimal_rotation(F @ q2, q2)) == pytest.approx(1.0)
        Rr = al.optimal_rotation(F @ q2, q2, allow_reflection=True)
        np.testing.assert_allclose(Rr, F, atol=1e-12)

    def test_optimal_rotation_shape_mismatch(self):
        with pytest.raises(ValueError):
            al.optimal_rotation(np.ones((2, 10)), np.ones((2, 11)))


# ---------------------------------------------------------------------------
# Pairwise shape distance: invariances and metric axioms
# ---------------------------------------------------------------------------


class TestShapeDistance:
    def test_align_pair_keys_and_similarity_invariance(self):
        b1 = wave()
        R0 = rot2(1.0)
        b2 = 3.0 * (R0 @ b1) + np.array([[5.0], [-2.0]])
        r = al.curve_shape_align_pair(b1, b2)
        assert set(r) == {
            "beta1", "beta2_aligned", "q1", "q2_aligned", "rotation", "gamma",
            "seed", "length1", "length2", "distance",
        }
        assert r["beta1"].shape == r["beta2_aligned"].shape == (2, M)
        assert r["rotation"].shape == (2, 2) and r["gamma"].shape == (M,)
        assert r["distance"] < 1e-6
        # the rotation undoes R0
        np.testing.assert_allclose(r["rotation"], R0.T, atol=1e-6)
        assert r["length2"] == pytest.approx(3.0 * r["length1"], rel=1e-10)
        assert r["seed"] == 0
        np.testing.assert_allclose(r["beta2_aligned"], r["beta1"], atol=1e-6)

    def test_rotation_and_scale_quotients_matter(self):
        b1 = wave()
        b2 = 2.0 * (rot2(0.8) @ b1)
        assert al.curve_shape_distance(b1, b2) < 1e-6
        assert al.curve_shape_distance(b1, b2, rotation=False) > 0.3
        # without the scale quotient, L2 distance of the unscaled SRVFs > 0
        assert al.curve_shape_distance(b1, b2, scale=False) > 0.1
        assert al.curve_shape_distance(b1, rot2(0.8) @ b1, scale=False) < 1e-6

    def test_reparametrisation_invariance(self):
        b1 = wave()
        b2 = wave(warp=lambda t: t + 0.25 * t * (1 - t))
        d_rigid = al.curve_shape_distance(b1, b2, reparam=False)
        d_dp = al.curve_shape_distance(b1, b2)
        d_rbfgs = al.curve_shape_distance(
            b1, b2, align_iter=4, warp_optim={"method": "rbfgs"}
        )
        assert d_rigid > 0.1
        assert d_dp < 0.05  # DP slope-quantisation floor (~0.02)
        assert d_rbfgs < d_dp

    def test_metric_axioms(self):
        b1, b2 = wave(), wave(amp=0.5, freq=4.0)
        assert al.curve_shape_distance(b1, b1) == pytest.approx(0.0, abs=1e-8)
        # rigid Procrustes distance is exactly symmetric
        d12 = al.curve_shape_distance(b1, b2, reparam=False)
        d21 = al.curve_shape_distance(b2, b1, reparam=False)
        assert d12 == pytest.approx(d21, abs=1e-10)
        # the elastic one up to the DP discretisation
        e12 = al.curve_shape_distance(b1, b2)
        e21 = al.curve_shape_distance(b2, b1)
        assert e12 == pytest.approx(e21, rel=0.1)
        assert 0 < e12 <= d12 + 1e-12

    def test_closed_seed_invariance_rigid(self):
        m = 41
        shift = 2 * np.pi * 7 / (m - 1)
        d = al.curve_shape_distance(
            ellipse(m), ellipse(m, 3.0, 1.6, shift), closed=True, reparam=False
        )
        assert d < 1e-8

    def test_closed_seed_invariance_elastic(self):
        m = 61
        c1 = ellipse(m, 1.5, 0.8) + np.vstack([np.zeros(m), 0.2 * np.sin(3 * np.linspace(0, 2 * np.pi, m))])
        c2 = np.roll(c1[:, :-1], 13, axis=1)
        c2 = np.hstack([c2, c2[:, :1]])  # still closed, starting 13 samples later
        r = al.curve_shape_align_pair(c1, c2, closed=True)
        assert r["distance"] < 0.05
        d_noseed = al.curve_shape_distance(c1, c2, closed=True, seed_search=False)
        assert d_noseed > 5 * r["distance"]

    def test_ab_half_matches_srvf(self):
        b1, b2 = wave(), wave(amp=0.5, freq=4.0)
        d_srvf = al.curve_shape_distance(b1, b2)
        d_ab = al.curve_shape_distance(b1, b2, metric="elastic", a=1.0, b=0.5)
        assert d_ab == pytest.approx(d_srvf, abs=1e-9)
        d_11 = al.curve_shape_distance(b1, b2, metric="elastic", a=1.0, b=1.0)
        assert d_11 > 0 and abs(d_11 - d_srvf) > 1e-6

    def test_ab_similarity_invariance(self):
        b1 = wave()
        b2 = 2.5 * (rot2(-0.7) @ b1) + 1.0
        assert al.curve_shape_distance(b1, b2, metric="elastic", a=1.0, b=1.0) < 1e-6

    def test_branch_search(self):
        m = 50
        t = np.linspace(0, 1, m)
        b1 = np.vstack([-t, 0.02 * t])
        b2 = np.vstack([-t, -0.02 * t])
        kw = dict(metric="elastic", a=1.0, b=1.0, rotation=False, reparam=False)
        assert al.curve_shape_distance(b1, b2, **kw) > 1.0
        assert al.curve_shape_distance(b1, b2, branch_search=True, **kw) < 0.1

    def test_include_length(self):
        b1 = wave()
        d = al.curve_shape_distance(b1, 2.0 * b1, include_length=True)
        # sqrt(theta^2 + ln^2(||q1||/||q2||)); ||q|| scales as sqrt(length)
        assert d == pytest.approx(abs(np.log(np.sqrt(2.0))), rel=1e-6)

    def test_option_errors(self):
        b = wave()
        with pytest.raises(ValueError, match="requires both a and b"):
            al.curve_shape_distance(b, b, metric="elastic", a=1.0)
        with pytest.raises(ValueError, match="only used with metric='elastic'"):
            al.curve_shape_distance(b, b, a=1.0, b=0.5)
        with pytest.raises(ValueError, match="metric must be one of"):
            al.curve_shape_distance(b, b, metric="l2")
        with pytest.raises(ValueError):
            al.curve_shape_distance(np.ones((3, 20)), np.ones((3, 20)), metric="elastic", a=1.0, b=1.0)
        with pytest.raises(ValueError):
            al.curve_shape_distance(b, b, seed_step=0)
        with pytest.raises(ValueError):
            al.curve_shape_distance(b, b, align_iter=0)
        with pytest.raises(ValueError):
            al.curve_shape_distance(b, b, lambda_=-1.0)
        with pytest.raises(ValueError):
            al.curve_shape_distance(b, wave(m=M + 1))
        with pytest.raises(ValueError):
            al.curve_shape_distance(b, np.zeros_like(b))  # zero-length curve

    def test_warp_optim_dict_errors(self):
        b = wave()
        with pytest.raises(ValueError, match="unknown key 'nope'"):
            al.curve_shape_distance(b, b, warp_optim={"nope": 1})
        with pytest.raises(ValueError, match="lambda"):
            al.curve_shape_distance(b, b, warp_optim={"lambda_": 0.1})
        with pytest.raises(ValueError, match="band_frac"):
            al.curve_shape_distance(b, b, warp_optim={"band_frac": 0.1})
        with pytest.raises(ValueError, match="method must be one of"):
            al.curve_shape_distance(b, b, warp_optim={"method": "newton"})
        with pytest.raises(ValueError, match="warp_optim\\['scl'\\]"):
            al.curve_shape_distance(b, b, warp_optim={"scl": "three"})

    def test_self_distance_matrix(self):
        curves = bump_family(4)
        D = al.curve_shape_self_distance_matrix(curves)
        assert D.shape == (4, 4)
        np.testing.assert_allclose(D, D.T, atol=0)
        np.testing.assert_allclose(np.diag(D), 0.0)
        for i, j in [(0, 1), (1, 3)]:
            assert D[i, j] == pytest.approx(al.curve_shape_distance(curves[i], curves[j]), abs=1e-12)
        # a list of (d, m) arrays is accepted too
        np.testing.assert_allclose(al.curve_shape_self_distance_matrix(list(curves)), D)
        # monotone family: neighbours are closer than the extremes
        assert D[0, 1] < D[0, 3]

    def test_collection_errors(self):
        with pytest.raises(ValueError):
            al.curve_shape_self_distance_matrix([wave(), wave(m=M + 2)])
        with pytest.raises(ValueError):
            al.curve_shape_self_distance_matrix(np.ones((2, 3)))


# ---------------------------------------------------------------------------
# Karcher mean / median, covariance, PCA, TSRVF
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def family():
    return bump_family(6)


@pytest.fixture(scope="module")
def km(family):
    return al.curve_shape_karcher_mean(family, max_iter=10)


class TestKarcher:
    def test_keys_and_shapes(self, km):
        n, d, m = 6, 2, 30
        assert km["mean"].shape == km["mean_srvf"].shape == (d, m)
        assert km["aligned_curves"].shape == km["aligned_srvfs"].shape == (n, d, m)
        assert km["rotations"].shape == (n, d, d)
        assert km["gammas"].shape == (n, m)
        assert km["seeds"].shape == (n,)
        assert km["shooting_vectors"].shape == (n, d * m)
        assert km["distances"].shape == km["lengths"].shape == (n,)
        assert isinstance(km["model"], al.PyCurveShapeKarcher)
        # the mean shape sits in the middle of the one-parameter family
        assert int(np.argmin(km["distances"])) in (2, 3)
        assert km["distances"][0] > km["distances"][2] and km["distances"][5] > km["distances"][3]
        np.testing.assert_allclose(km["model"].mean, km["mean"])
        assert km["model"].converged == km["converged"]
        assert set(km["model"].to_dict()) == set(km) - {"model"}

    def test_mean_is_similarity_invariant(self, family, km):
        # rotate / scale / translate every curve differently: same mean shape
        moved = np.stack(
            [(1 + 0.5 * i) * (rot2(0.3 * i) @ c) + i for i, c in enumerate(family)]
        )
        km2 = al.curve_shape_karcher_mean(moved, max_iter=10)
        np.testing.assert_allclose(km2["distances"], km["distances"], atol=1e-3)
        d = al.curve_shape_distance(km["mean"], km2["mean"])
        assert d < 1e-3

    def test_rotations_are_orthogonal(self, km):
        for R in km["rotations"]:
            np.testing.assert_allclose(R @ R.T, np.eye(2), atol=1e-10)
            assert np.linalg.det(R) == pytest.approx(1.0)

    def test_tsrvf_reproduces_shooting_vectors(self, family, km):
        ts = al.curve_shape_tsrvf(km["model"], family)
        np.testing.assert_allclose(ts["tangent_vectors"], km["shooting_vectors"], atol=1e-10)
        assert ts["aligned_srvfs"].shape == (6, 2, 30)
        assert ts["rotations"].shape == (6, 2, 2)
        np.testing.assert_allclose(ts["distances"], km["distances"], atol=1e-10)

    def test_tangent_to_curve_round_trip(self, family, km):
        ts = al.curve_shape_tsrvf(km["model"], family)
        beta = al.curve_shape_tangent_to_curve(km["model"], ts["tangent_vectors"][2])
        assert beta.shape == (2, 30)
        # the reconstruction has the shape of curve 2
        assert al.curve_shape_distance(beta, family[2]) < 0.05
        # the zero tangent vector is the mean
        beta0 = al.curve_shape_tangent_to_curve(km["model"], np.zeros(60))
        assert al.curve_shape_distance(beta0, km["mean"]) < 1e-6
        with pytest.raises(ValueError):
            al.curve_shape_tangent_to_curve(km["model"], np.zeros(59))
        with pytest.raises(ValueError):
            al.curve_shape_tangent_to_curve(km["model"], np.full(60, np.nan))

    def test_covariance(self, km):
        C = al.curve_shape_karcher_covariance(km["model"])
        assert C.shape == (60, 60)
        np.testing.assert_allclose(C, C.T, atol=1e-12)
        assert np.linalg.eigvalsh(C).min() > -1e-10

    def test_pca(self, km):
        pca = al.curve_shape_pca(km["model"], ncomp=2)
        assert pca["scores"].shape == (6, 2)
        assert pca["components"].shape == (2, 2, 30)
        assert pca["mean_tangent"].shape == (2, 30)
        assert pca["cumulative_variance"][0] > 0.9  # one-parameter family
        assert np.all(np.diff(pca["eigenvalues"]) <= 0)
        model = pca["model"]
        assert isinstance(model, al.PyCurveShapePca)
        np.testing.assert_allclose(model.scores, pca["scores"])
        b0 = model.mode_shape(km["model"], 0, 0.0)
        assert b0.shape == (2, 30)
        assert al.curve_shape_distance(b0, km["mean"]) < 1e-2
        b_plus = model.mode_shape(km["model"], 0, 2.0)
        b_minus = model.mode_shape(km["model"], 0, -2.0)
        # the principal mode moves along the family (bump height)
        assert np.ptp(b_plus[1]) != pytest.approx(np.ptp(b_minus[1]), rel=0.05)
        with pytest.raises(ValueError):
            model.mode_shape(km["model"], 5, 0.0)
        with pytest.raises(ValueError):
            al.curve_shape_pca(km["model"], ncomp=0)

    def test_median_and_boxplot(self, family):
        med = al.curve_shape_karcher_median(family, max_iter=10)
        assert isinstance(med["model"], al.PyCurveShapeKarcher)
        bp = al.curve_shape_boxplot(med["model"])
        assert bp["r50"] <= bp["ralpha"]
        assert bp["q1_index"] != bp["q3_index"]
        for key in ("median", "q1", "q3", "q1a", "q3a", "upper_whisker", "lower_whisker",
                    "minimum", "maximum", "median_srvf"):
            assert bp[key].shape == (2, 30), key
        assert bp["distances"].shape == (6,)
        bp2 = al.curve_shape_boxplot_from_aligned(
            med["mean_srvf"], med["aligned_srvfs"], med["aligned_curves"]
        )
        np.testing.assert_allclose(bp2["distances"], bp["distances"], atol=1e-12)
        assert bp2["r50"] == pytest.approx(bp["r50"])
        np.testing.assert_allclose(bp2["q1"], bp["q1"], atol=1e-12)


# ---------------------------------------------------------------------------
# Depth, outliers, confidence regions
# ---------------------------------------------------------------------------


def zigzag_set(n=8, m=40, outlier=5):
    t = np.linspace(0.0, 1.0, m)
    curves = [np.vstack([t, (0.3 + 0.01 * i) * np.sin(np.pi * t)]) for i in range(n)]
    curves[outlier] = np.vstack([t, 0.3 * np.sin(8 * np.pi * t)])
    return np.stack(curves)


class TestDownstream:
    def test_depth(self):
        curves = zigzag_set()
        r = al.curve_shape_depth(curves)
        assert r["amplitude_depth"].shape == r["phase_depth"].shape == (8,)
        A = r["amplitude_distances"]
        assert A.shape == (8, 8)
        np.testing.assert_allclose(A, A.T)
        assert int(np.argmin(r["amplitude_depth"])) == 5

    def test_outlier_detection(self):
        curves = zigzag_set()
        r = al.curve_shape_outlier_detection(curves)
        assert list(r["outlier_indices"]) == [5]
        assert r["distances"][5] > r["threshold"]
        assert r["centre"]["mean"].shape == (2, 40)
        assert isinstance(r["centre_model"], al.PyCurveShapeKarcher)
        # invariant to a similarity transform of every curve
        moved = np.stack([2.0 * (rot2(0.4 * i) @ c) - i for i, c in enumerate(curves)])
        r2 = al.curve_shape_outlier_detection(moved)
        assert list(r2["outlier_indices"]) == [5]
        np.testing.assert_allclose(r2["distances"], r["distances"], atol=1e-3)
        r_mean = al.curve_shape_outlier_detection(curves, centre="mean", threshold_method="quantile", alpha=0.2)
        assert 5 in r_mean["outlier_indices"]

    def test_outlier_errors(self):
        curves = zigzag_set()
        with pytest.raises(ValueError, match="centre"):
            al.curve_shape_outlier_detection(curves, centre="mode")
        with pytest.raises(ValueError, match="threshold_method"):
            al.curve_shape_outlier_detection(curves, threshold_method="iqr")
        with pytest.raises(ValueError):
            al.curve_shape_outlier_detection(curves, tukey_k=-1.0)
        with pytest.raises(ValueError):
            al.curve_shape_outlier_detection(curves[:1])

    def test_confidence_interval_bootstrap(self, family):
        r = al.curve_shape_confidence_interval(family, n_bootstrap=5, max_iter=5)
        assert r["bootstrap_means"].shape == (5, 2, 30)
        assert r["bootstrap_distances"].shape == (5,)
        assert r["radius"] >= 0.0
        assert r["lower_band"].shape == r["upper_band"].shape == (2, 30)
        assert r["model"] is None
        assert isinstance(r["mean_model"], al.PyCurveShapeKarcher)
        r2 = al.curve_shape_confidence_interval(family, n_bootstrap=5, max_iter=5)
        np.testing.assert_allclose(r2["bootstrap_distances"], r["bootstrap_distances"])

    def test_confidence_interval_model_based(self, family):
        r = al.curve_shape_confidence_interval(
            family, method="model_based", n_samples=10, n_components=2,
            n_warp_components=2, max_iter=5,
        )
        mc = r["model"]
        assert set(mc) == {
            "q1a", "q3a", "boxplot", "pca", "scores", "shape_samples",
            "shape_samples_srvf", "samples", "samples_srvf", "warps", "rotations",
        }
        assert mc["samples"].shape == (10, 2, 30)
        assert mc["q1a"].shape == (2, 30)
        assert "r50" in mc["boxplot"] and "eigenvalues" in mc["pca"]
        with pytest.raises(ValueError, match="method"):
            al.curve_shape_confidence_interval(family, method="jackknife")


# ---------------------------------------------------------------------------
# Exact piecewise-linear (a, b) distance
# ---------------------------------------------------------------------------


POLY_A = turtle([0.1, 0.5, -0.2, 0.3], [1.0, 0.6, 0.9, 0.5])
POLY_B = turtle([-0.3, 0.2, 0.6, -0.1, 0.4], [0.7, 0.8, 0.4, 0.6, 0.5])


class TestPiecewiseLinear:
    def test_closed_form_one_segment(self):
        c1 = np.array([[0.0, 1.0], [0.0, 0.0]])
        s, c = np.sin(0.3), np.cos(0.3)
        c2 = np.array([[0.0, c, 2 * c], [0.0, s, 0.0]])
        a, b = 1.0, 1.0
        r = al.ab_elastic_match_pl(c1, c2, a, b)
        k = np.cos(0.5 * 0.3)
        s_exact = np.sqrt(2.0 * k * k)
        assert r["similarity"] == pytest.approx(s_exact, abs=1e-12)
        assert r["distance"] == pytest.approx(2 * b * np.sqrt(1 + 2 - 2 * s_exact), abs=1e-12)
        assert r["length1"] == pytest.approx(1.0) and r["length2"] == pytest.approx(2.0)
        path = r["path"]
        assert path.shape[1] == 2
        np.testing.assert_array_equal(path[0], [0.0, 0.0])
        np.testing.assert_array_equal(path[-1], [1.0, 1.0])
        assert np.all(np.diff(path, axis=0) >= -1e-15)

    @pytest.mark.parametrize("ab", [(1.0, 0.5), (1.0, 1.0), (3.0, 1.0)])
    def test_metric_axioms_and_invariances(self, ab):
        d = lambda x, y: al.ab_elastic_distance_pl(x, y, *ab)
        assert d(POLY_A, POLY_A) < 1e-7
        assert d(POLY_A, POLY_B) == pytest.approx(d(POLY_B, POLY_A), abs=1e-12)
        assert d(POLY_A + 3.0, POLY_B - 1.0) == pytest.approx(d(POLY_A, POLY_B), abs=1e-12)
        # subdividing a segment (reparametrisation) does not change the distance
        sub = np.insert(POLY_B, 1, 0.5 * (POLY_B[:, 0] + POLY_B[:, 1]), axis=1)
        assert d(POLY_A, sub) == pytest.approx(d(POLY_A, POLY_B), abs=1e-9)
        # translation-only quotient: rotation changes the distance
        assert d(POLY_A, rot2(0.5) @ POLY_A) > 0.1

    @pytest.mark.parametrize("ab", [(1.0, 0.5), (1.0, 1.0), (3.0, 1.0)])
    def test_exact_lower_bounds_dense_dp(self, ab):
        exact = al.ab_elastic_distance_pl(POLY_A, POLY_B, *ab)
        gaps = []
        for m in (101, 401):
            dp = al.curve_shape_distance(
                sample_polygon(POLY_A, m), sample_polygon(POLY_B, m),
                metric="elastic", a=ab[0], b=ab[1], rotation=False, scale=False,
            )
            gaps.append((dp - exact) / exact)
        assert abs(gaps[1]) < abs(gaps[0])
        assert gaps[1] > -5e-3  # exact <= DP up to the corner-rounding error
        assert gaps[1] < 0.05  # DP slope-quantisation floor

    def test_errors(self):
        c = POLY_A
        with pytest.raises(ValueError):
            al.ab_elastic_distance_pl(c, c, 0.0, 1.0)
        with pytest.raises(ValueError):
            al.ab_elastic_distance_pl(c, c, 1.0, np.nan)
        with pytest.raises(ValueError):
            al.ab_elastic_distance_pl(c, np.zeros((3, 4)), 1.0, 1.0)
        with pytest.raises(ValueError):
            al.ab_elastic_distance_pl(c, np.zeros((2, 1)), 1.0, 1.0)
        with pytest.raises(ValueError):
            al.ab_elastic_match_pl(c, np.zeros((2, 3)), 1.0, 1.0)  # zero length


# ---------------------------------------------------------------------------
# Sparse / irregular elastic curves
# ---------------------------------------------------------------------------


def elasdics_pair():
    c1 = np.array([[1.0, 0.5, -1.0, -1.0], [1.0, -0.5, -1.0, 1.0]])
    i = np.arange(1, 7)
    c2 = np.vstack([np.where(i % 2 == 1, 0.1, 0.7) * np.sin(i), np.cos(i)])
    return c1, c2


class TestSparse:
    def test_align_pair_elasdics_reference(self):
        c1, c2 = elasdics_pair()
        r = al.sparse_elastic_align_pair(c1, c2)
        assert r["distance"] == pytest.approx(1.3121782758, abs=1e-8)  # elasdics 1.1.3
        assert np.all(np.diff(r["param_optim"]) >= 0)
        assert r["template_points"].shape == (2, 4) and r["points"].shape == (2, 6)
        assert r["closed"] is False and r["removed_duplicates"] is False

    def test_align_pair_axioms(self):
        c1, c2 = elasdics_pair()
        assert al.sparse_elastic_align_pair(c1, c1)["distance"] < 1e-8
        d = al.sparse_elastic_align_pair(c1, c2)["distance"]
        assert al.sparse_elastic_align_pair(c1 + 4.0, c2 - 2.0)["distance"] == pytest.approx(d, abs=1e-10)
        # a user parametrisation is only a starting point: same optimum here
        p2 = np.linspace(0.0, 1.0, 6)
        assert al.sparse_elastic_align_pair(c1, c2, param2=p2)["distance"] == pytest.approx(d, rel=0.05)
        # duplicates are removed and reported
        dup = np.insert(c2, 2, c2[:, 2], axis=1)
        rd = al.sparse_elastic_align_pair(c1, dup)
        assert rd["removed_duplicates"] is True
        assert rd["points"].shape == (2, 6)

    def test_sparse_on_dense_grid_matches_dense_elastic(self):
        # Densely sampled curves treated as polygons: the sparse (elasdics)
        # distance and the dense SRVF DP (no rotation / scale quotient) are two
        # discretisations of the same elastic distance.
        b1 = wave(m=201)
        b2 = wave(m=201, amp=0.45, freq=5.0, warp=lambda t: t + 0.2 * t * (1 - t))
        dense = al.curve_shape_distance(b1, b2, rotation=False, scale=False)
        sparse = al.sparse_elastic_align_pair(b1, b2, eps=1e-4)["distance"]
        assert sparse == pytest.approx(dense, rel=0.05)

    def test_closed_pair_start_invariance(self):
        m = 30
        th = 2 * np.pi * np.arange(m) / m
        c1 = np.vstack([1.5 * np.cos(th), np.sin(th)])
        c2 = np.roll(c1, 9, axis=1)
        r = al.sparse_elastic_align_pair(c1, c2, closed=True)
        assert r["closed"] is True
        assert r["distance"] < 1e-6
        assert al.sparse_elastic_align_pair(c1, c2)["distance"] > 0.5

    def test_align_pair_errors(self):
        c1, c2 = elasdics_pair()
        with pytest.raises(ValueError):
            al.sparse_elastic_align_pair(c1, c2, eps=0.0)
        with pytest.raises(ValueError):
            al.sparse_elastic_align_pair(c1, np.ones((3, 5)))
        with pytest.raises(ValueError):
            al.sparse_elastic_align_pair(c1, c2[:, :1])
        with pytest.raises(ValueError):
            al.sparse_elastic_align_pair(c1, c2, param2=np.array([0.0, 0.5, 0.4, 0.6, 0.8, 1.0]))

    def test_mean_half_circle(self):
        curves = []
        for m in (25, 32, 40):
            s = np.pi * np.linspace(0, 1, m) ** 1.2
            curves.append(np.vstack([np.cos(s), np.sin(s)]))
        r = al.sparse_elastic_mean(curves, knots=np.linspace(0, 1, 9))
        assert r["coefs"].shape == (2, 9)
        assert len(r["curves"]) == len(r["params"]) == len(r["params_optim"]) == 3
        assert r["mean_type"] == "smooth" and r["closed"] is False
        assert np.all(r["distances"] < 0.15)
        model = r["model"]
        assert isinstance(model, al.PySparseElasticMean)
        mean = model.mean_curve(np.array([0.0, 0.5, 1.0]), centering=False)
        assert mean.shape == (2, 3)
        assert mean[0, 2] == pytest.approx(-2.0, abs=0.05)
        assert mean[1, 2] == pytest.approx(0.0, abs=0.05)
        assert model.srv_eval(np.linspace(0, 1, 7)).shape == (2, 7)
        np.testing.assert_allclose(model.closure_residual(), mean[:, 2], atol=1e-6)
        for p in r["params_optim"]:
            assert p[0] == 0.0 and p[-1] == pytest.approx(1.0) and np.all(np.diff(p) >= 0)

    def test_mean_of_identical_curves_is_the_curve(self):
        base = wave(m=200)
        curves = [base[:, ::k] + k for k in (3, 4, 5)]  # differently sampled + translated
        # the subsampled polygons differ from each other by ~0.05 (discretisation)
        pair = max(al.sparse_elastic_align_pair(curves[0], c)["distance"] for c in curves)
        r = al.sparse_elastic_mean(curves, knots=np.linspace(0, 1, 21))
        assert r["coefs"].shape == (2, 21)
        assert np.all(r["distances"] < pair + 0.02)
        mean = r["model"].mean_curve(np.linspace(0, 1, 50), centering=False)
        np.testing.assert_allclose(mean[:, -1], base[:, -1] - base[:, 0], atol=0.03)
        # polygon SRV splines: the fit improves with more knots
        poly = [
            al.sparse_elastic_mean(curves, knots=np.linspace(0, 1, k + 1), mean_type="polygon")
            for k in (10, 40)
        ]
        assert poly[0]["coefs"].shape == (2, 10)
        assert poly[0]["mean_type"] == "polygon"
        assert poly[1]["distances"].mean() < poly[0]["distances"].mean()

    def test_closed_mean(self):
        curves = []
        for m, start in ((30, 0.0), (36, 0.3), (42, 0.7)):
            s = 2 * np.pi * (start + np.arange(m) / m)
            curves.append(np.vstack([1.5 * np.cos(s), np.sin(s)]))
        r = al.sparse_elastic_mean(curves, knots=np.linspace(0, 1, 13), closed=True, closure_steps=10)
        assert r["converged"] and r["closed"]
        assert r["coefs"].shape == (2, 12)
        assert np.hypot(*r["model"].closure_residual()) < 1e-10
        mean = r["model"].mean_curve(np.linspace(0, 1, 201))
        assert np.ptp(mean[0]) == pytest.approx(3.0, abs=0.05)
        assert np.ptp(mean[1]) == pytest.approx(2.0, abs=0.05)

    def test_mean_with_params(self):
        c1, c2 = elasdics_pair()
        r = al.sparse_elastic_mean([c1, c2], params=[None, np.linspace(0, 1, 6)])
        np.testing.assert_allclose(r["params"][1], np.linspace(0, 1, 6))

    def test_mean_errors(self):
        c1, c2 = elasdics_pair()
        with pytest.raises(ValueError, match="mean_type"):
            al.sparse_elastic_mean([c1, c2], mean_type="cubic")
        with pytest.raises(ValueError, match="params has 1 entries"):
            al.sparse_elastic_mean([c1, c2], params=[None])
        with pytest.raises(ValueError, match="params\\[1\\]"):
            al.sparse_elastic_mean([c1, c2], params=[None, "x"])
        with pytest.raises(ValueError):
            al.sparse_elastic_mean([c1, c2], knots=np.array([0.0, 0.6, 0.5, 1.0]))
        with pytest.raises(ValueError):
            al.sparse_elastic_mean([c1, c2], max_iter=0)
        with pytest.raises(ValueError):
            al.sparse_elastic_mean([c1, c2], closed=True, knots=np.array([0.0, 1.0]))
        with pytest.raises(ValueError):
            al.sparse_elastic_mean([])
        with pytest.raises(ValueError):
            al.sparse_elastic_mean([c1, np.ones((3, 4))])
        r = al.sparse_elastic_mean([c1, c2])
        with pytest.raises(ValueError):
            r["model"].mean_curve(np.array([0.5, 0.2]))

    def test_sparse_curves_from_irreg(self):
        data = pace_fpca.irreg_fdata_from_lists(
            [np.array([0.0, 0.5, 1.0]), np.array([0.2, 0.4, 0.9, 1.2])],
            [np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.5, 0.8, 0.0])],
        )
        curves = al.sparse_curves_from_irreg(data)
        assert len(curves) == 2
        assert curves[1]["points"].shape == (1, 4)
        np.testing.assert_allclose(curves[1]["points"][0], [0.0, 0.5, 0.8, 0.0])
        np.testing.assert_allclose(curves[1]["param"], (np.array([0.2, 0.4, 0.9, 1.2]) - 0.2) / 1.0)
        # feeds the sparse elastic functions directly (1-D functions as curves)
        r = al.sparse_elastic_align_pair(
            curves[0]["points"], curves[1]["points"], curves[0]["param"], curves[1]["param"]
        )
        assert r["distance"] >= 0.0
