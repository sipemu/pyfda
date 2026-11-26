"""Tests for the fdars-core 0.48 batch-3 bindings (``fdars.alignment``).

* ``*_with_config``: the elastic engine with a full ``WarpOptimConfig``.  With
  default options every twin is checked bit-for-bit against the classic
  binding; the options are checked for their documented effects.
* SRSF pre-smoothing, rigid shift / iterative shift / landmark shift
  registration, Ramsay-Li continuous registration (incl. periodic), affine /
  dilation registration, Tang-Mueller pairwise synchronisation and phase box
  plot classification: planted shifts, warps and dilations are recovered from
  synthetic data with fixed seeds.
* Updated existing bindings: ``phase_boxplot`` fences,
  ``elastic_outlier_detection`` threshold rules, ``clustering.align_cluster_fd``
  linear warp classes.
"""

import numpy as np
import pytest

from fdars import alignment as A
from fdars import clustering as C


@pytest.fixture
def rng():
    return np.random.default_rng(20261126)


T61 = np.linspace(0.0, 1.0, 61)


def _bump(t, c, w=0.01):
    return np.exp(-((t - c) ** 2) / w)


@pytest.fixture
def pair():
    return _bump(T61, 0.4), _bump(T61, 0.55)


@pytest.fixture
def bumps(rng):
    centres = rng.uniform(0.4, 0.6, 6)
    amps = rng.uniform(0.8, 1.2, 6)
    return np.array([a * _bump(T61, c) for a, c in zip(amps, centres)])


def _assert_same(a, b):
    """Bit-identical comparison of two result dicts on the keys of ``a``."""
    for k in a:
        assert np.array_equal(np.asarray(a[k]), np.asarray(b[k])), k


def _assert_warp(g, t):
    g = np.asarray(g)
    assert g[..., 0] == pytest.approx(t[0])
    assert g[..., -1] == pytest.approx(t[-1])
    assert np.all(np.diff(g, axis=-1) >= -1e-12)


# ---------------------------------------------------------------------------
# *_with_config: default options are bit-identical to the classic bindings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lam", [0.0, 0.05])
class TestWithConfigParity:
    def test_pair_and_distance(self, pair, lam):
        f1, f2 = pair
        _assert_same(
            A.elastic_align_pair(f1, f2, T61, lam),
            A.elastic_align_pair_with_config(f1, f2, T61, lambda_=lam),
        )
        assert A.elastic_distance_with_config(f1, f2, T61, lambda_=lam) == A.elastic_distance(
            f1, f2, T61, lam
        )

    def test_distance_matrices(self, bumps, lam):
        assert np.array_equal(
            A.elastic_self_distance_matrix(bumps, T61, lam),
            A.elastic_self_distance_matrix_with_config(bumps, T61, lambda_=lam),
        )
        assert np.array_equal(
            A.elastic_cross_distance_matrix(bumps[:2], bumps[2:], T61, lam),
            A.elastic_cross_distance_matrix_with_config(bumps[:2], bumps[2:], T61, lambda_=lam),
        )

    def test_karcher_family(self, bumps, lam):
        _assert_same(
            A.karcher_mean(bumps, T61, lam, 10, 1e-4),
            A.karcher_mean_with_config(bumps, T61, max_iter=10, tol=1e-4, lambda_=lam),
        )
        _assert_same(
            A.karcher_median(bumps, T61, lam, 10, 1e-3),
            A.karcher_median_with_config(bumps, T61, max_iter=10, tol=1e-3, lambda_=lam),
        )
        _assert_same(
            A.robust_karcher_mean(bumps, T61, lam, 10, 1e-3, 0.2),
            A.robust_karcher_mean_with_config(
                bumps, T61, max_iter=10, tol=1e-3, trim_fraction=0.2, lambda_=lam
            ),
        )

    def test_align_to_target(self, bumps, lam):
        _assert_same(
            A.align_to_target(bumps, bumps[0], T61, lam),
            A.align_to_target_with_config(bumps, bumps[0], T61, lambda_=lam),
        )

    def test_closed(self, lam):
        t = np.linspace(0, 1, 40)
        f1 = np.sin(2 * np.pi * t)
        f2 = np.sin(2 * np.pi * (t - 0.1)) + 0.1 * np.sin(4 * np.pi * t)
        _assert_same(
            A.elastic_align_pair_closed(f1, f2, t, lam),
            A.elastic_align_pair_closed_with_config(f1, f2, t, lambda_=lam),
        )
        assert A.elastic_distance_closed_with_config(
            f1, f2, t, lambda_=lam
        ) == A.elastic_distance_closed(f1, f2, t, lam)
        data = np.array([np.sin(2 * np.pi * (t - d)) for d in (0.0, 0.05, 0.1)])
        _assert_same(
            A.karcher_mean_closed(data, t, 5, 1e-4, lam),
            A.karcher_mean_closed_with_config(data, t, max_iter=5, tol=1e-4, lambda_=lam),
        )

    def test_constrained(self, pair, lam):
        f1, f2 = pair
        classic = A.elastic_align_pair_constrained(f1, f2, T61, [0.4], [0.55], lam)
        cfg = A.elastic_align_pair_constrained_with_config(f1, f2, T61, [0.4], [0.55], lambda_=lam)
        _assert_same(classic, cfg)
        assert cfg["enforced_landmarks"].shape == (1, 2)
        tgt, src = cfg["enforced_landmarks"][0]
        assert np.interp(tgt, T61, cfg["gamma"]) == pytest.approx(src)


def test_band_frac_matches_banded_bindings(bumps):
    assert np.array_equal(
        A.elastic_self_distance_matrix_with_band(bumps, T61, 0.0, 0.2),
        A.elastic_self_distance_matrix_with_config(bumps, T61, band_frac=0.2),
    )
    _assert_same(
        A.karcher_mean_with_band(bumps, T61, 0.0, 5, 1e-4, 0.2),
        A.karcher_mean_with_config(bumps, T61, max_iter=5, band_frac=0.2),
    )


def test_band_confines_warp(pair):
    f1, f2 = pair
    r = A.elastic_align_pair_with_config(f1, f2, T61, band_frac=0.05)
    radius = np.ceil(0.05 * len(T61)) * (T61[1] - T61[0])
    assert np.max(np.abs(r["gamma"] - T61)) <= radius + 1e-12


# ---------------------------------------------------------------------------
# *_with_config: options
# ---------------------------------------------------------------------------


def test_dp_prune_is_exact(pair, bumps):
    f1, f2 = pair
    _assert_same(
        A.elastic_align_pair_with_config(f1, f2, T61, lambda_=0.02),
        A.elastic_align_pair_with_config(f1, f2, T61, lambda_=0.02, dp_prune=False),
    )
    assert np.array_equal(
        A.elastic_self_distance_matrix_with_config(bumps, T61),
        A.elastic_self_distance_matrix_with_config(bumps, T61, dp_prune=False),
    )


def test_larger_neighbourhood_never_worse(pair):
    f1, f2 = pair
    d = [A.elastic_distance_with_config(f1, f2, T61, nbhd_dim=k) for k in (1, 3, 5, 7, 10)]
    assert all(b <= a + 1e-12 for a, b in zip(d, d[1:]))
    # nbhd_dim = 1 allows only the identity warp.
    r = A.elastic_align_pair_with_config(f1, f2, T61, nbhd_dim=1)
    assert np.allclose(r["gamma"], T61)


def test_lambda_scale_irrelevant_without_penalty(pair):
    f1, f2 = pair
    ref = A.elastic_align_pair_with_config(f1, f2, T61, method="rbfgs")
    for scale in ("dp", "fdasrsf"):
        _assert_same(ref, A.elastic_align_pair_with_config(f1, f2, T61, method="rbfgs", lambda_scale=scale))


@pytest.mark.parametrize(
    "kw",
    [
        {"method": "rbfgs"},
        {"method": "rbfgs", "penalty": "roughness", "lambda_": 1e-4},
        {"method": "rbfgs", "penalty": "geodesic", "lambda_": 0.1},
        {"penalty": "l2psi", "lambda_": 0.1},
        {"dp_cost": "piecewise_linear", "nbhd_dim": 10},
        {"dp_scl": 4},
    ],
)
def test_options_give_valid_warps(pair, kw):
    f1, f2 = pair
    r = A.elastic_align_pair_with_config(f1, f2, T61, **kw)
    _assert_warp(r["gamma"], T61)
    assert np.isfinite(r["distance"]) and r["distance"] >= 0
    assert np.allclose(r["f_aligned"], np.interp(r["gamma"], T61, f2))


def test_penalty_shrinks_warp(pair):
    f1, f2 = pair
    dt = np.diff(T61)

    def l2psi(lam):
        g = A.elastic_align_pair_with_config(f1, f2, T61, penalty="l2psi", lambda_=lam)["gamma"]
        return np.sum((np.sqrt(np.diff(g) / dt) - 1.0) ** 2 * dt)

    # The penalty at the optimum is non-increasing in its weight.
    pen = [l2psi(lam) for lam in (0.0, 0.01, 0.1, 1.0, 10.0)]
    assert all(b <= a + 1e-12 for a, b in zip(pen, pen[1:]))
    assert pen[-1] < 0.5 * pen[0]


@pytest.mark.parametrize(
    "kw, match",
    [
        ({"method": "newton"}, "method must be one of"),
        ({"penalty": "l1"}, "penalty must be one of"),
        ({"dp_cost": "cubic"}, "dp_cost must be one of"),
        ({"lambda_scale": "x"}, "lambda_scale must be one of"),
        ({"penalty": "roughness", "lambda_": 0.1}, "penalty"),
        ({"penalty": "geodesic", "lambda_": 0.1}, "penalty"),
        ({"lambda_": -1.0}, "lambda"),
        ({"nbhd_dim": 0}, "nbhd_dim"),
        ({"nbhd_dim": 65}, "nbhd_dim"),
        ({"dp_scl": 0}, "dp_scl"),
        ({"scl": 0}, "scl"),
        ({"band_frac": -0.1}, "band_frac"),
    ],
)
def test_warp_options_value_errors(pair, kw, match):
    f1, f2 = pair
    with pytest.raises(ValueError, match=match):
        A.elastic_distance_with_config(f1, f2, T61, **kw)


def test_constrained_rejects_band(pair):
    f1, f2 = pair
    with pytest.raises(ValueError, match="band_frac"):
        A.elastic_align_pair_constrained_with_config(f1, f2, T61, [0.4], [0.55], band_frac=0.2)


# ---------------------------------------------------------------------------
# R^d *_with_config
# ---------------------------------------------------------------------------


def _curve_nd(t, g):
    s = g(t)
    return np.vstack([np.sin(6 * s), np.cos(4 * s) + s])


def test_nd_pair_recovers_shared_warp():
    t = np.linspace(0, 1, 60)
    f1 = _curve_nd(t, lambda s: s)
    f2 = _curve_nd(t, lambda s: s + 0.15 * s * (1 - s))
    dp = A.elastic_align_pair_nd_with_config(f1, f2, t)
    assert dp["f_aligned"].shape == (2, 60)
    _assert_warp(dp["gamma"], t)
    assert np.allclose(dp["f_aligned"], np.array([np.interp(dp["gamma"], t, row) for row in f2]))
    unaligned = np.abs(f2 - f1).max()
    assert np.abs(dp["f_aligned"] - f1).max() < 0.2 * unaligned
    assert A.elastic_distance_nd_with_config(f1, f2, t) == dp["distance"]
    # Core doc example: RBFGS lowers the alignment cost below DP here.
    rb = A.elastic_align_pair_nd_with_config(f1, f2, t, method="rbfgs")
    _assert_warp(rb["gamma"], t)
    assert rb["distance"] < dp["distance"]


def test_nd_d1_matches_univariate_warp(pair):
    f1, f2 = pair
    nd = A.elastic_align_pair_nd_with_config(f1[None, :], f2[None, :], T61)
    uni = A.elastic_align_pair_with_config(f1, f2, T61)
    assert np.allclose(nd["gamma"], uni["gamma"])


def test_karcher_mean_nd(rng):
    t = np.linspace(0, 1, 50)
    a = rng.uniform(-0.15, 0.15, 5)
    data = np.stack([_curve_nd(t, lambda s, ai=ai: s + ai * s * (1 - s)) for ai in a])
    r = A.karcher_mean_nd_with_config(data, t, max_iter=10)
    assert r["mean"].shape == (2, 50)
    assert r["mean_srsf"].shape == (2, 50)
    assert r["gammas"].shape == (5, 50)
    assert r["aligned_data"].shape == (5, 2, 50)
    _assert_warp(r["gammas"], t)
    # Aligned curves are closer to each other than the raw curves.
    assert r["aligned_data"].std(axis=0).max() < data.std(axis=0).max()


def test_nd_value_errors():
    t = np.linspace(0, 1, 30)
    f = np.vstack([t, t**2])
    with pytest.raises(ValueError):
        A.elastic_align_pair_nd_with_config(f, np.vstack([t, t, t]), t)
    with pytest.raises(ValueError):
        A.elastic_distance_nd_with_config(f, f, t[:-1])
    with pytest.raises(ValueError):
        A.karcher_mean_nd_with_config(f[None], t)  # n < 2


# ---------------------------------------------------------------------------
# SRSF pre-smoothing
# ---------------------------------------------------------------------------


def test_srsf_smoothing_none_is_srsf_transform(rng):
    t = np.linspace(0, 1, 30)
    data = rng.normal(size=(3, 30)).cumsum(axis=1)
    q = A.srsf_transform_smoothed(data, t)
    for i in range(3):
        assert np.array_equal(q[i], A.srsf_transform(data[i], t))
    assert np.array_equal(A.srsf_presmooth(data, t), data)


def test_box_filter():
    t = np.linspace(0, 1, 5)
    assert np.array_equal(
        A.srsf_presmooth(np.array([[0, 0, 4, 0, 0.0]]), t, "box", 1), [[0, 1, 2, 1, 0]]
    )
    data = np.array([[1.0, 5.0, -2.0, 3.0, 0.0]])
    assert np.array_equal(A.srsf_presmooth(data, t, "box", 0), data)
    many = A.srsf_presmooth(data, t, "box", 200)
    assert many[0, 0] == 1.0 and many[0, -1] == 0.0  # endpoints fixed
    assert np.allclose(many[0], np.linspace(1.0, 0.0, 5), atol=1e-6)  # converges to the chord


@pytest.mark.parametrize("smoothing, passes", [("box", 3), ("spline", 1)])
def test_smoothed_srsf_is_srsf_of_presmoothed(rng, smoothing, passes):
    t = np.linspace(0, 1, 40)
    data = np.sin(2 * np.pi * t) + 0.1 * rng.normal(size=(2, 40))
    s = A.srsf_presmooth(data, t, smoothing, passes)
    q = A.srsf_transform_smoothed(data, t, smoothing, passes)
    for i in range(2):
        assert np.allclose(q[i], A.srsf_transform(s[i], t))
    # Smoothing reduces roughness.
    assert np.abs(np.diff(s, 2)).sum() < np.abs(np.diff(data, 2)).sum()


def test_smoothing_value_errors():
    t3 = np.linspace(0, 1, 3)
    with pytest.raises(ValueError, match="smoothing must be one of"):
        A.srsf_presmooth(np.zeros((1, 3)), t3, "gauss")
    with pytest.raises(ValueError):
        A.srsf_presmooth(np.zeros((1, 3)), t3, "spline")  # needs m >= 4
    with pytest.raises(ValueError):
        A.srsf_transform_smoothed(np.zeros((1, 2)), t3[:2], "box")  # needs m >= 3


# ---------------------------------------------------------------------------
# Rigid shift and iterative shift registration
# ---------------------------------------------------------------------------

T101 = np.linspace(0.0, 1.0, 101)


def test_shift_curves_sign_and_extrapolation():
    t = np.linspace(0, 1, 11)
    out = A.shift_curves(t[None, :], t, [0.2], extrapolation="linear")
    assert out["data"][0, 5] == pytest.approx(0.3)  # f(0.5 - 0.2)
    assert out["data"][0, 0] == pytest.approx(-0.2)
    assert A.shift_curves(t[None, :], t, [0.2])["data"][0, 0] == pytest.approx(0.0)  # boundary
    assert A.shift_curves(t[None, :], t, [0.2], extrapolation="zeros")["data"][0, 0] == 0.0
    restricted = A.shift_curves(t[None, :], t, [0.2], restrict_domain=True)
    assert np.allclose(restricted["argvals"], t[2:])
    assert restricted["data"].shape == (1, 9)


def test_shift_curves_moves_peak_and_periodic_roundtrip():
    g = _bump(T101, 0.4, 0.005)[None, :]
    moved = A.shift_curves(g, T101, [0.1])["data"][0]
    assert T101[np.argmax(moved)] == pytest.approx(0.5)
    data = np.array([np.sin(2 * np.pi * T101), np.cos(2 * np.pi * T101)])
    d = np.array([0.13, -0.27])  # multiples of the grid step: exact
    there = A.shift_curves(data, T101, d, extrapolation="periodic")["data"]
    back = A.shift_curves(there, T101, -d, extrapolation="periodic")["data"]
    assert np.allclose(back, data, atol=1e-12)


def _shifted_sines(d):
    return np.array([np.sin(2 * np.pi * (T101 - di)) for di in d])


def test_iterative_shift_recovers_planted_shifts_fixed_template():
    d = np.array([0.04, -0.03, 0.0, 0.02])
    r = A.iterative_shift_registration(
        _shifted_sines(d),
        T101,
        template=np.sin(2 * np.pi * T101),
        max_iter=50,
        tol=1e-10,
        extrapolation="periodic",
    )
    assert np.allclose(r["shifts"], -d, atol=1e-6)
    assert r["converged"]
    assert np.allclose(r["registered_data"], np.sin(2 * np.pi * T101), atol=1e-3)
    assert np.allclose(r["registered_argvals"], T101)


@pytest.mark.parametrize("template", [None, "mean", lambda y: np.median(y, axis=0)])
def test_iterative_shift_estimated_template_recovers_relative_shifts(rng, template):
    d = rng.uniform(-0.05, 0.05, 6)
    r = A.iterative_shift_registration(
        _shifted_sines(d), T101, template=template, max_iter=50, tol=1e-10, extrapolation="periodic"
    )
    rel = r["shifts"] + d  # = common offset for every curve
    assert np.ptp(rel) < 2e-3
    assert r["template"].shape == (101,)


def test_iterative_shift_initial_and_errors():
    d = np.array([0.04, -0.03])
    data = _shifted_sines(d)
    r = A.iterative_shift_registration(data, T101, template=np.sin(2 * np.pi * T101), max_iter=0, initial=[-0.04, 0.03])
    assert r["n_iter"] == 0 and np.allclose(r["shifts"], -d)
    with pytest.raises(ValueError):
        A.iterative_shift_registration(data, T101, initial=[0.0])
    with pytest.raises(ValueError, match="template must be"):
        A.iterative_shift_registration(data, T101, template="median")
    with pytest.raises(ValueError):
        A.iterative_shift_registration(data, T101, template=lambda y: y[0, :10])  # wrong length
    with pytest.raises(ValueError):
        A.iterative_shift_registration(data, T101, template=np.zeros(5))
    with pytest.raises(ValueError, match="step_size"):
        A.iterative_shift_registration(data, T101, step_size=0.0)
    with pytest.raises(ValueError, match="extrapolation must be one of"):
        A.iterative_shift_registration(data, T101, extrapolation="mirror")


def test_template_callable_exception_propagates():
    def boom(_):
        raise ZeroDivisionError("from template")

    with pytest.raises(ZeroDivisionError, match="from template"):
        A.iterative_shift_registration(_shifted_sines([0.0, 0.01]), T101, template=boom)
    with pytest.raises(ZeroDivisionError, match="from template"):
        A.affine_registration(_shifted_sines([0.0, 0.01]), T101, template=boom)


# ---------------------------------------------------------------------------
# Landmark shift registration
# ---------------------------------------------------------------------------


def test_landmark_shift_deltas_locations():
    lm = [0.2, 0.4, 0.9]
    assert np.allclose(A.landmark_shift_deltas(lm), np.mean(lm) - np.array(lm))
    assert np.allclose(A.landmark_shift_deltas(lm, "mean"), np.mean(lm) - np.array(lm))
    assert np.allclose(A.landmark_shift_deltas(lm, "midrange"), [0.35, 0.15, -0.35])
    assert np.allclose(A.landmark_shift_deltas(lm, 0.5), [0.3, 0.1, -0.4])
    assert np.allclose(A.landmark_shift_deltas(lm, np.median), [0.2, 0.0, -0.5])


def test_landmark_shift_deltas_multi():
    lm = [[0.2, 0.6], [0.3, 0.7]]
    assert np.allclose(A.landmark_shift_deltas_multi(lm, [0.25, 0.65]), [0.05, -0.05])
    assert np.allclose(A.landmark_shift_deltas_multi(np.array(lm)), [0.05, -0.05])
    # K = 1 without targets equals the single-landmark mean rule.
    single = [0.2, 0.45, 0.6]
    assert np.allclose(
        A.landmark_shift_deltas_multi(np.array(single)[:, None]), A.landmark_shift_deltas(single)
    )


def test_landmark_shift_registration_aligns_peaks():
    peaks = [0.4, 0.5, 0.6]
    data = np.array([_bump(T101, p, 0.005) for p in peaks])
    r = A.landmark_shift_registration(data, T101, peaks)
    assert r["target"] == pytest.approx(0.5)
    assert np.allclose(r["shifts"], [0.1, 0.0, -0.1])
    assert np.allclose(r["registered_data"][:, 50], 1.0, atol=1e-9)
    r2 = A.landmark_shift_registration(data, T101, peaks, location=0.45, restrict_domain=True)
    assert r2["target"] == 0.45
    assert r2["registered_data"].shape[1] == len(r2["registered_argvals"]) < 101


def test_landmark_value_errors():
    with pytest.raises(ValueError):
        A.landmark_shift_deltas([])
    with pytest.raises(ValueError):
        A.landmark_shift_deltas([0.1, np.nan])
    with pytest.raises(ValueError, match="location must be"):
        A.landmark_shift_deltas([0.1], "median")
    with pytest.raises(ValueError):
        A.landmark_shift_deltas([0.1, 0.2], lambda lm: np.inf)
    with pytest.raises(KeyError):
        A.landmark_shift_deltas([0.1, 0.2], lambda lm: {}["x"])
    with pytest.raises(ValueError, match="2 landmarks per curve"):
        A.landmark_shift_deltas_multi([[0.2, 0.6], [0.3]])
    with pytest.raises(ValueError):
        A.landmark_shift_deltas_multi([[0.2, 0.6]], targets=[0.1])
    with pytest.raises(ValueError):
        A.landmark_shift_registration(np.zeros((3, 101)), T101, [0.1, 0.2])


# ---------------------------------------------------------------------------
# Continuous (Ramsay-Li) registration
# ---------------------------------------------------------------------------

T51 = np.linspace(0.0, 1.0, 51)


def _g(s):
    return np.exp(-((s - 0.5) ** 2) / 0.02)


@pytest.fixture
def warped():
    a = np.array([-0.2, 0.0, 0.2])
    w = np.array([T51 + ai * T51 * (1 - T51) for ai in a])  # planted warps
    return np.array([_g(wi) for wi in w]), w


def test_continuous_registration_warps_and_recovery(warped):
    data, w = warped
    r = A.continuous_registration(data, T51, target=_g(T51), criterion="least_squares")
    assert r["registered_data"].shape == (3, 51)
    assert r["w_coefficients"].shape == (3, 6)
    assert len(r["w_knots"]) == 6 + 4
    assert np.all(r["w_coefficients"][:, 0] == 0.0)
    assert np.all(r["shift"] == 0.0)
    for i in range(3):
        assert r["warps"][i, 0] == 0.0 and r["warps"][i, -1] == 1.0
        assert np.all(np.diff(r["warps"][i]) > 0)
        # y_i(h_i(t)) = g(w_i(h_i(t))) = g(t)  =>  w_i(h_i(t)) = t.
        assert np.allclose(np.interp(r["warps"][i], T51, w[i]), T51, atol=5e-3)
    assert np.abs(r["registered_data"] - _g(T51)).max() < 0.02
    assert np.array_equal(r["target"], _g(T51))


@pytest.mark.parametrize("criterion", ["min_eigenvalue", "least_squares"])
def test_continuous_criterion_non_increasing(warped, criterion):
    data, _ = warped
    crit = np.array(
        [A.continuous_registration(data, T51, criterion=criterion, max_iter=k)["criterion"] for k in range(9)]
    )
    assert np.all(np.diff(crit, axis=0) <= 1e-15)
    assert np.all(crit[-1] < crit[0])
    r0 = A.continuous_registration(data, T51, max_iter=0)
    assert np.allclose(r0["warps"], T51) and np.all(r0["n_iter"] == 0)


def test_continuous_least_squares_criterion_value(warped):
    data, _ = warped
    y0 = _g(T51)
    r = A.continuous_registration(data, T51, target=y0, criterion="least_squares", n_fine=51)
    # On a fine grid equal to argvals the criterion is mean((y0 - y o h)^2).
    assert np.allclose(r["criterion"], ((r["registered_data"] - y0) ** 2).mean(axis=1), rtol=1e-6, atol=1e-12)


def test_continuous_periodic_recovers_phase_shift():
    t = np.linspace(0, 1, 101)
    d = np.array([0.05, -0.08, 0.0, 0.12])
    data = np.array([np.sin(2 * np.pi * (t - di)) + 0.3 * np.cos(4 * np.pi * (t - di)) for di in d])
    target = np.sin(2 * np.pi * t) + 0.3 * np.cos(4 * np.pi * t)
    r = A.continuous_registration(data, t, target=target, periodic=True, criterion="least_squares")
    assert np.allclose(r["shift"], d, atol=1e-3)
    # Periodic warps are h_i(t) + delta_i: endpoints a + delta, b + delta.
    assert np.allclose(r["warps"][:, 0], r["shift"])
    assert np.allclose(r["warps"][:, -1], 1.0 + r["shift"])
    assert np.all(np.diff(r["warps"], axis=1) > 0)
    assert np.abs(r["registered_data"] - target).max() < 1e-2


def test_continuous_r_defaults_and_overrides(warped):
    data, _ = warped
    r = A.continuous_registration(data, T51, r_defaults=True)
    assert r["w_coefficients"].shape == (3, 2) and len(r["w_knots"]) == 4
    assert np.all(r["n_iter"] <= 20)
    r2 = A.continuous_registration(data, T51, r_defaults=True, nbasis=5, norder=3, lfd_order=1)
    assert r2["w_coefficients"].shape == (3, 5) and len(r2["w_knots"]) == 8


def test_continuous_template_passes_and_initial(warped):
    data, _ = warped
    r = A.continuous_registration(data, T51, max_template_iter=3)
    assert 1 <= r["n_template_iter"] <= 3
    warm = A.continuous_registration(data, T51, max_iter=0, initial_coefficients=r["w_coefficients"])
    assert np.allclose(warm["warps"], r["warps"])


def test_continuous_converged_is_true_on_stall(warped):
    """Documents core behaviour: ``converged`` is also set when the LM step
    control stalls.  With ``tol=0`` no accepted step can satisfy the relative
    decrease rule, yet every curve reports ``converged`` well before
    ``max_iter`` (fdars-core 0.48 ``register_curve``: ``Stalled => converged = true``)."""
    data, _ = warped
    r = A.continuous_registration(data, T51, tol=0.0, max_iter=1000)
    assert np.all(r["n_iter"] < 1000)
    assert np.all(r["converged"])


@pytest.mark.parametrize(
    "kw",
    [
        {"criterion": "l1"},
        {"nbasis": 3, "norder": 4},
        {"lfd_order": 4},
        {"lambda_": -1.0},
        {"n_fine": 2},
        {"max_template_iter": 0},
        {"initial_coefficients": np.zeros((3, 2))},
        {"target": np.zeros(10)},
    ],
)
def test_continuous_value_errors(warped, kw):
    data, _ = warped
    with pytest.raises(ValueError):
        A.continuous_registration(data, T51, **kw)


def test_continuous_needs_four_points():
    with pytest.raises(ValueError):
        A.continuous_registration(np.ones((2, 3)), np.linspace(0, 1, 3))


# ---------------------------------------------------------------------------
# Shift / dilation / affine registration
# ---------------------------------------------------------------------------


def _mu(s):
    return np.exp(-(((s - 0.5) / 0.1) ** 2))


@pytest.fixture
def affine_data():
    a = np.array([1.06, 0.95, 1.0])
    b = np.array([-0.04, 0.03, 0.01])
    return np.array([_mu(ai * T101 + bi) for ai, bi in zip(a, b)]), a, b


def test_affine_recovers_planted_warps_fixed_template(affine_data):
    data, a, b = affine_data
    r = A.affine_registration(data, T101, template=_mu(T101))
    assert np.allclose(r["dilations"], a, atol=1e-3)
    assert np.allclose(r["shifts"], b, atol=1e-3)
    assert r["converged"]
    assert np.abs(r["registered_data"] - _mu(T101)).max() < 1e-2
    assert np.allclose(r["distances"], 0.0, atol=1e-2)
    # The registered curves are exactly affine_warp_curves at the fitted warps.
    assert np.array_equal(A.affine_warp_curves(data, T101, r["dilations"], r["shifts"]), r["registered_data"])


def test_affine_mean_template_is_centred(affine_data):
    data, a, b = affine_data
    r = A.affine_registration(data, T101)
    assert np.mean(r["dilations"]) == pytest.approx(1.0, abs=1e-9)
    assert np.mean(r["shifts"]) == pytest.approx(0.0, abs=1e-9)
    # Relative warps h_i o h_0^{-1} are frame-invariant: slopes a_i / a_0.
    assert np.allclose(r["dilations"] / r["dilations"][0], a / a[0], atol=5e-3)
    rc = A.affine_registration(data, T101, template=lambda y: y.mean(axis=0))
    assert rc["converged"] and np.isfinite(rc["distances"]).all()


@pytest.mark.parametrize(
    "warp_class, a, b",
    [("shift", [1.0, 1.0], [-0.05, 0.03]), ("dilation", [1.08, 0.93], [0.0, 0.0])],
)
def test_affine_single_parameter_classes(warp_class, a, b):
    data = np.array([_mu(ai * T101 + bi) for ai, bi in zip(a, b)])
    r = A.affine_registration(data, T101, warp_class=warp_class, template=_mu(T101))
    assert np.allclose(r["dilations"], a, atol=1e-3)
    assert np.allclose(r["shifts"], b, atol=1e-3)


def test_affine_none_class_and_metrics(affine_data):
    data, _, _ = affine_data
    r = A.affine_registration(data, T101, warp_class="none")
    assert np.all(r["dilations"] == 1.0) and np.all(r["shifts"] == 0.0)
    assert np.allclose(r["registered_data"], data)
    for metric in ("normalized_l2", "pearson"):
        rm = A.affine_registration(data, T101, metric=metric, domain="overlap", template=_mu(T101))
        assert np.allclose(rm["dilations"], [1.06, 0.95, 1.0], atol=5e-3)


def test_affine_warp_curves_formula():
    t = np.linspace(0, 1, 11)
    g = A.affine_warp_curves((t**2)[None, :], t, [2.0], [0.1])
    assert g[0, 5] == pytest.approx(0.04)  # f((0.5 - 0.1) / 2) = f(0.2)


@pytest.mark.parametrize(
    "kw",
    [
        {"warp_class": "rigid"},
        {"metric": "l1"},
        {"domain": "partial"},
        {"metric": "l2", "domain": "overlap"},  # L2 on the overlap is not dilation-invariant
        {"max_dilation": 1.0},
        {"max_shift": -0.1},
        {"grid_size": 2},
        {"template": np.zeros(7)},
    ],
)
def test_affine_value_errors(affine_data, kw):
    data, _, _ = affine_data
    with pytest.raises(ValueError):
        A.affine_registration(data, T101, **kw)


def test_affine_warp_curves_value_errors():
    t = np.linspace(0, 1, 11)
    with pytest.raises(ValueError):
        A.affine_warp_curves(np.zeros((1, 11)), t, [0.0], [0.0])
    with pytest.raises(ValueError):
        A.affine_warp_curves(np.zeros((2, 11)), t, [1.0], [0.0, 0.0])


# ---------------------------------------------------------------------------
# Tang-Mueller pairwise synchronisation
# ---------------------------------------------------------------------------


@pytest.fixture
def wfda_data():
    t = np.linspace(0, 1, 41)
    a = [-0.3, -0.1, 0.0, 0.1, 0.3]
    return np.array([0.2 + _mu(t + ai * t * (1 - t)) for ai in a]), t


def test_pairwise_synchronization(wfda_data):
    data, t = wfda_data
    r = A.pairwise_synchronization(data, t, subset_prop=1.0)
    n, m = data.shape
    for key in ("warps", "inverse_warps", "aligned"):
        assert r[key].shape == (n, m)
    _assert_warp(r["warps"], t)
    _assert_warp(r["inverse_warps"], t)
    assert len(r["partners"]) == len(r["pairwise_warps"]) == len(r["pairwise_costs"]) == n
    for i in range(n):
        assert sorted(r["partners"][i].tolist()) == [k for k in range(n) if k != i]
        assert r["pairwise_warps"][i].shape == (n - 1, m)
        assert r["pairwise_costs"][i].shape == (n - 1,)
        # warps and inverse warps are mutual inverses.
        assert np.allclose(np.interp(r["warps"][i], t, r["inverse_warps"][i]), t, atol=0.03)
    assert r["aligned"].std(axis=0).max() < 0.5 * data.std(axis=0).max()
    assert r["lambda"] > 0 and r["costs"].shape == (n,)


def test_pairwise_synchronization_options(wfda_data):
    data, t = wfda_data
    a = A.pairwise_synchronization(data, t, seed=7)
    b = A.pairwise_synchronization(data, t, seed=7)
    _assert_same({k: a[k] for k in ("warps", "aligned", "costs")}, b)
    assert all(len(p) == 2 for p in a["partners"])  # round(0.5 * 4)
    w = A.pairwise_synchronization(data, t, choice="weighted", lambda_=0.0, cost_measure="fdapace_legacy")
    assert w["lambda"] == 0.0
    _assert_warp(w["warps"], t)


@pytest.mark.parametrize(
    "kw",
    [{"choice": "median"}, {"cost_measure": "x"}, {"subset_prop": 0.0}, {"nknots": 8}, {"lambda_": -1.0}],
)
def test_pairwise_synchronization_value_errors(wfda_data, kw):
    data, t = wfda_data
    with pytest.raises(ValueError):
        A.pairwise_synchronization(data, t, **kw)


def test_pairwise_synchronization_needs_two_curves(wfda_data):
    data, t = wfda_data
    with pytest.raises(ValueError):
        A.pairwise_synchronization(data[:1], t)


# ---------------------------------------------------------------------------
# Phase box plot: fences and classification
# ---------------------------------------------------------------------------


@pytest.fixture
def warps(rng):
    t = np.linspace(0, 1, 40)
    a = rng.uniform(-0.3, 0.3, 15)
    g = np.array([t + ai * t * (1 - t) for ai in a])
    g[0] = t**3  # extreme warp
    return g, t


def test_phase_boxplot_fences(warps):
    g, t = warps
    bp = A.phase_boxplot(g, t)
    assert bp["fence_lower"].shape == bp["fence_upper"].shape == (40,)
    assert np.all(bp["fence_lower"] <= bp["central_lower"] + 1e-12)
    assert np.all(bp["fence_upper"] >= bp["central_upper"] - 1e-12)
    assert np.all(bp["fence_lower"] >= t[0] - 1e-12) and np.all(bp["fence_upper"] <= t[-1] + 1e-12)


def test_phase_boxplot_classify_matches_fit(warps):
    g, t = warps
    bp = A.phase_boxplot(g, t)
    levels = A.phase_boxplot_classify(g, t, g)
    assert levels.dtype == np.int8
    assert set(np.flatnonzero(levels == 4)) == set(bp["outlier_indices"].tolist())
    assert 0 in bp["outlier_indices"]
    assert set(levels.tolist()) <= {1, 3, 4}
    assert levels[bp["median_index"]] == 1
    new = np.vstack([t, t**4])
    assert A.phase_boxplot_classify(g, t, new).tolist() == [1, 4]


def test_phase_boxplot_classify_value_error(warps):
    g, t = warps
    with pytest.raises(ValueError):
        A.phase_boxplot_classify(g, t, g[:, :-1])


# ---------------------------------------------------------------------------
# elastic_outlier_detection threshold rules
# ---------------------------------------------------------------------------


@pytest.fixture
def outlier_data(rng):
    data = np.array([_bump(T61, c) for c in rng.uniform(0.4, 0.6, 12)])
    data[0] = np.sin(8 * T61)
    return data


def test_outlier_tukey_default_unchanged(outlier_data):
    a = A.elastic_outlier_detection(outlier_data, T61)
    b = A.elastic_outlier_detection(outlier_data, T61, threshold_method="tukey", tukey_k=1.5)
    _assert_same(a, b)
    assert 0 in a["outlier_indices"]
    d = a["distances"]
    q1, q3 = np.percentile(d, [25, 75])
    assert a["threshold"] == pytest.approx(q3 + 1.5 * (q3 - q1))
    assert A.elastic_outlier_detection(outlier_data, T61, tukey_k=1e3)["outlier_indices"].size == 0


def test_outlier_quantile_rule(outlier_data):
    r = A.elastic_outlier_detection(outlier_data, T61, threshold_method="quantile", alpha=0.25)
    assert r["threshold"] == pytest.approx(np.quantile(r["distances"], 0.75))
    assert set(r["outlier_indices"].tolist()) == set(np.flatnonzero(r["distances"] > r["threshold"]))


def test_outlier_value_errors(outlier_data):
    with pytest.raises(ValueError, match="threshold_method must be one of"):
        A.elastic_outlier_detection(outlier_data, T61, threshold_method="mad")
    with pytest.raises(ValueError):
        A.elastic_outlier_detection(outlier_data, T61, tukey_k=-1.0)


# ---------------------------------------------------------------------------
# clustering.align_cluster_fd linear warp classes
# ---------------------------------------------------------------------------


def _two_shape_clusters():
    def m1(s):
        return np.exp(-(((s - 0.3) / 0.07) ** 2))

    def m2(s):
        return np.exp(-(((s - 0.7) / 0.07) ** 2))

    b = [-0.03, 0.0, 0.03]
    return np.array([m1(T61 + bi) for bi in b] + [m2(T61 + bi) for bi in b]), np.array(b * 2)


def test_align_cluster_fd_elastic_has_no_linear_warps(outlier_data):
    r = C.align_cluster_fd(outlier_data, T61)
    assert r["dilations"] is None and r["shifts"] is None


def test_align_cluster_fd_shift_class_recovers_clusters_and_shifts():
    data, b = _two_shape_clusters()
    r = C.align_cluster_fd(data, T61, warp_class="shift")
    lab = r["cluster"]
    assert len(set(lab[:3])) == 1 and len(set(lab[3:])) == 1 and lab[0] != lab[3]
    assert np.all(r["dilations"] == 1.0)
    assert np.allclose(r["shifts"], b, atol=1e-3)
    ra = C.align_cluster_fd(data, T61, warp_class="affine", affine_metric="pearson", affine_domain="overlap")
    assert ra["dilations"].shape == (6,) and np.isfinite(ra["shifts"]).all()


def test_align_cluster_fd_value_errors():
    data, _ = _two_shape_clusters()
    with pytest.raises(ValueError, match="warp_class must be one of"):
        C.align_cluster_fd(data, T61, warp_class="bpd")
    with pytest.raises(ValueError, match="metric must be one of"):
        C.align_cluster_fd(data, T61, warp_class="shift", affine_metric="l1")
