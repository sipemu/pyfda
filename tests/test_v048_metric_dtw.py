"""Tests for the fdars-core 0.48 DTW family in ``fdars.metric`` (batch 1).

Windowed DTW / soft-DTW are checked against brute-force numpy dynamic
programmes run over the window mask the binding itself reports, lower bounds
against the DTW they bound, nearest-neighbour search against an exhaustive
scan, and SBD against an FFT-free NCC reference.
"""

import numpy as np
import pytest

from fdars import metric as M


# ---------------------------------------------------------------------------
# Brute-force references
# ---------------------------------------------------------------------------


def _dtw_ref(x, y, p=2.0, mask=None):
    n, m = len(x), len(y)
    if mask is None:
        mask = np.ones((n, m), dtype=bool)
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if mask[i - 1, j - 1]:
                c = abs(x[i - 1] - y[j - 1]) ** p
                D[i, j] = c + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return D[n, m]


def _softmin(a, gamma):
    a = np.asarray(a)
    mn = a.min()
    if not np.isfinite(mn):
        return mn
    return mn - gamma * np.log(np.exp(-(a - mn) / gamma).sum())


def _soft_dtw_ref(x, y, gamma=1.0, mask=None):
    n, m = len(x), len(y)
    if mask is None:
        mask = np.ones((n, m), dtype=bool)
    R = np.full((n + 1, m + 1), np.inf)
    R[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if mask[i - 1, j - 1]:
                c = (x[i - 1] - y[j - 1]) ** 2
                R[i, j] = c + _softmin([R[i - 1, j], R[i, j - 1], R[i - 1, j - 1]], gamma)
    return R[n, m]


def _sbd_ref(x, y):
    def z(v):
        sd = v.std()
        return (v - v.mean()) / sd

    xz, yz = z(x), z(y)
    m = len(x)
    ncc = np.array(
        [
            np.dot(xz[max(0, s) : m + min(0, s)], yz[max(0, -s) : m - max(0, s)])
            for s in range(-(m - 1), m)
        ]
    ) / (np.linalg.norm(xz) * np.linalg.norm(yz))
    k = int(np.argmax(ncc))
    return 1.0 - ncc[k], k - (m - 1)


WINDOWS = [
    {"window": "none"},
    {"window": "sakoe_chiba", "radius": 2},
    {"window": "itakura", "max_slope": 2.0},
    {"window": "sakoe_chiba_fraction", "window_fraction": 0.25},
    {"window": "itakura_fraction", "max_slope": 0.6},
]


@pytest.fixture
def rng():
    return np.random.default_rng(20261126)


# ---------------------------------------------------------------------------
# Window kwargs and masks
# ---------------------------------------------------------------------------


def test_window_mask_tslearn_known_answer():
    t, f = True, False
    expected = np.array(
        [[t, t, t, f], [t, t, t, t], [t, t, t, t], [f, t, t, t]], dtype=bool
    )
    mask = M.dtw_window_mask(4, 4, window="sakoe_chiba", radius=2)
    assert mask.dtype == bool and mask.shape == (4, 4)
    np.testing.assert_array_equal(mask, expected)


def test_window_mask_band_equals_abs_index_diff():
    n, r = 9, 3
    i, j = np.indices((n, n))
    np.testing.assert_array_equal(
        M.dtw_window_mask(n, n, window="sakoe_chiba", radius=r), np.abs(i - j) <= r
    )
    assert M.dtw_window_mask(n, 5).all()


def test_window_fraction_equals_radius_for_equal_lengths():
    n = 12
    np.testing.assert_array_equal(
        M.dtw_window_mask(n, n, window="sakoe_chiba_fraction", window_fraction=0.25),
        M.dtw_window_mask(n, n, window="sakoe_chiba", radius=3),
    )


@pytest.mark.parametrize(
    "kwargs, missing",
    [
        ({"window": "sakoe_chiba"}, "radius"),
        ({"window": "itakura"}, "max_slope"),
        ({"window": "sakoe_chiba_fraction"}, "window_fraction"),
        ({"window": "itakura_fraction"}, "max_slope"),
    ],
)
def test_window_missing_parameter_raises(kwargs, missing):
    with pytest.raises(ValueError, match=missing):
        M.dtw_window_mask(5, 5, **kwargs)


def test_window_unknown_name_raises():
    with pytest.raises(ValueError, match="sakoe_chiba"):
        M.dtw_distance_windowed(np.ones(3), np.ones(3), window="band")


def test_window_invalid_slope_raises():
    with pytest.raises(ValueError):
        M.dtw_window_mask(5, 5, window="itakura", max_slope=0.5)


# ---------------------------------------------------------------------------
# Windowed DTW and paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("win", WINDOWS)
@pytest.mark.parametrize("p", [1.0, 2.0])
@pytest.mark.parametrize("lengths", [(10, 10), (10, 13)])
def test_dtw_distance_windowed_matches_bruteforce(rng, win, p, lengths):
    x, y = rng.normal(size=lengths[0]), rng.normal(size=lengths[1])
    mask = M.dtw_window_mask(len(x), len(y), **win)
    got = M.dtw_distance_windowed(x, y, p=p, **win)
    assert got == pytest.approx(_dtw_ref(x, y, p, mask), rel=1e-12)


def test_dtw_unwindowed_matches_existing_dtw_self(rng):
    X = rng.normal(size=(4, 15))
    D = M.dtw_self_1d(X)
    for a in range(4):
        for b in range(a + 1, 4):
            assert M.dtw_distance_windowed(X[a], X[b]) == pytest.approx(D[a, b])


def test_dtw_window_only_increases_cost(rng):
    x, y = rng.normal(size=20), rng.normal(size=20)
    free = M.dtw_distance_windowed(x, y)
    banded = M.dtw_distance_windowed(x, y, window="sakoe_chiba", radius=1)
    assert banded >= free
    assert M.dtw_distance_windowed(x, y, window="sakoe_chiba", radius=0) == pytest.approx(
        np.sum((x - y) ** 2)
    )


def test_dtw_identity_and_symmetry(rng):
    x, y = rng.normal(size=11), rng.normal(size=11)
    assert M.dtw_distance_windowed(x, x) == 0.0
    assert M.dtw_distance_windowed(x, y) == pytest.approx(M.dtw_distance_windowed(y, x))


def test_dtw_path_known_answer():
    x = np.array([0.0, 1.0, 2.0, 1.0])
    y = np.array([0.0, 0.0, 1.0, 2.0])
    res = M.dtw_path(x, y)
    assert set(res) == {"path", "cost"}
    assert res["path"].dtype == np.int64
    np.testing.assert_array_equal(res["path"], [[0, 0], [0, 1], [1, 2], [2, 3], [3, 3]])
    assert res["cost"] == pytest.approx(1.0)


@pytest.mark.parametrize("win", WINDOWS)
def test_dtw_path_is_valid_and_attains_cost(rng, win):
    x, y = rng.normal(size=12), rng.normal(size=15)
    res = M.dtw_path(x, y, p=1.5, **win)
    path = res["path"]
    assert path.shape[1] == 2
    assert tuple(path[0]) == (0, 0) and tuple(path[-1]) == (11, 14)
    steps = {tuple(s) for s in np.diff(path, axis=0)}
    assert steps <= {(0, 1), (1, 0), (1, 1)}
    mask = M.dtw_window_mask(12, 15, **win)
    assert mask[path[:, 0], path[:, 1]].all()
    along = np.sum(np.abs(x[path[:, 0]] - y[path[:, 1]]) ** 1.5)
    assert res["cost"] == pytest.approx(along, rel=1e-12)
    assert res["cost"] == pytest.approx(M.dtw_distance_windowed(x, y, p=1.5, **win))


def test_dtw_rejects_empty_and_bad_p():
    with pytest.raises(ValueError):
        M.dtw_distance_windowed(np.array([]), np.ones(3))
    with pytest.raises(ValueError):
        M.dtw_path(np.ones(3), np.ones(3), p=0.0)


# ---------------------------------------------------------------------------
# Soft-DTW
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("win", WINDOWS[:3])
def test_soft_dtw_windowed_matches_bruteforce(rng, win):
    x, y = rng.normal(size=9), rng.normal(size=9)
    mask = M.dtw_window_mask(9, 9, **win)
    got = M.soft_dtw_distance_windowed(x, y, gamma=0.7, **win)
    assert got == pytest.approx(_soft_dtw_ref(x, y, 0.7, mask), rel=1e-10)


def test_soft_dtw_unwindowed_matches_existing_binding(rng):
    X = rng.normal(size=(3, 10))
    S = M.soft_dtw_self_1d(X, gamma=0.5)
    assert M.soft_dtw_distance_windowed(X[0], X[2], gamma=0.5) == pytest.approx(S[0, 2])


def test_soft_dtw_alignment_value_corners_and_mask(rng):
    x, y = rng.normal(size=8), rng.normal(size=10)
    win = {"window": "sakoe_chiba", "radius": 2}
    res = M.soft_dtw_alignment(x, y, gamma=0.5, **win)
    E = res["alignment"]
    assert E.shape == (8, 10)
    assert res["value"] == pytest.approx(M.soft_dtw_distance_windowed(x, y, gamma=0.5, **win))
    assert E[0, 0] == pytest.approx(1.0) and E[-1, -1] == pytest.approx(1.0)
    mask = M.dtw_window_mask(8, 10, **win)
    assert np.all(E[~mask] == 0.0)
    assert np.all(E >= -1e-12)


def test_soft_dtw_alignment_is_gradient(rng):
    x, y = rng.normal(size=7), rng.normal(size=9)
    gamma = 0.8
    res = M.soft_dtw_alignment(x, y, gamma=gamma)
    grad = (res["alignment"] * 2.0 * (x[:, None] - y[None, :])).sum(axis=1)
    h = 1e-6
    fd = np.empty_like(x)
    for k in range(len(x)):
        e = np.zeros_like(x)
        e[k] = h
        fd[k] = (
            M.soft_dtw_distance_windowed(x + e, y, gamma=gamma)
            - M.soft_dtw_distance_windowed(x - e, y, gamma=gamma)
        ) / (2 * h)
    np.testing.assert_allclose(grad, fd, rtol=1e-5, atol=1e-7)


def test_soft_dtw_alignment_known_answer():
    res = M.soft_dtw_alignment(np.array([1.0, 2, 2, 3]), np.array([1.0, 2, 3, 4]))
    assert res["value"] < -0.89
    assert res["alignment"][0, 0] == pytest.approx(1.0)


def test_soft_dtw_rejects_bad_gamma():
    with pytest.raises(ValueError):
        M.soft_dtw_distance_windowed(np.ones(3), np.ones(3), gamma=0.0)
    with pytest.raises(ValueError):
        M.soft_dtw_alignment(np.ones(3), np.ones(3), gamma=-1.0)


# ---------------------------------------------------------------------------
# Triangular GAK
# ---------------------------------------------------------------------------


def test_gak_triangular_zero_equals_gak(rng):
    x, y = rng.normal(size=12), rng.normal(size=12)
    assert M.gak_triangular(x, y, 1.5) == pytest.approx(M.gak(x, y, 1.5), rel=1e-12)


def test_gak_triangular_properties(rng):
    x, y = rng.normal(size=12), rng.normal(size=12)
    k = M.gak_triangular(x, y, 1.5, 3)
    assert 0.0 <= k <= 1.0
    assert k == pytest.approx(M.gak_triangular(y, x, 1.5, 3))
    assert M.gak_triangular(x, x, 1.5, 3) == pytest.approx(1.0, abs=1e-12)
    assert k != pytest.approx(M.gak_triangular(x, y, 1.5, 0))


def test_gak_gram_triangular_matches_pairwise(rng):
    X = rng.normal(size=(5, 12))
    G = M.gak_gram_matrix(X, sigma=2.0, triangular=3)
    for a in range(5):
        for b in range(5):
            assert G[a, b] == pytest.approx(M.gak_triangular(X[a], X[b], 2.0, 3), abs=1e-12)
    np.testing.assert_allclose(M.gak_gram_matrix(X, sigma=2.0), M.gak_gram_matrix(X, sigma=2.0, triangular=0))


def test_gak_gram_train_triangular_carries_to_predict(rng):
    X, Z = rng.normal(size=(4, 12)), rng.normal(size=(2, 12))
    train = M.gak_gram_train(X, sigma=2.0, triangular=4)
    assert train.triangular == 4
    assert M.gak_gram_train(X).triangular == 0
    np.testing.assert_allclose(train.gram, M.gak_gram_matrix(X, sigma=2.0, triangular=4))
    K = M.gak_gram_predict(train, Z)
    assert K.shape == (2, 4)
    assert K[1, 2] == pytest.approx(M.gak_triangular(Z[1], X[2], 2.0, 4), abs=1e-12)


def test_gak_triangular_empty_raises():
    with pytest.raises(ValueError):
        M.gak_triangular(np.array([]), np.ones(3), 1.0)


# ---------------------------------------------------------------------------
# Barycenters
# ---------------------------------------------------------------------------


def test_soft_dtw_barycenter_identical_rows_small_gamma():
    x = np.array([0.0, 1.0, 2.0, 1.0])
    res = M.soft_dtw_barycenter(np.tile(x, (3, 1)), gamma=0.01)
    assert set(res) == {"barycenter", "n_iter", "converged"}
    np.testing.assert_allclose(res["barycenter"], x, atol=1e-6)


def test_soft_dtw_barycenter_reproducible_and_finite(rng):
    X = rng.normal(size=(6, 15))
    a = M.soft_dtw_barycenter(X, n_restarts=3, seed=7)
    b = M.soft_dtw_barycenter(X, n_restarts=3, seed=7)
    np.testing.assert_array_equal(a["barycenter"], b["barycenter"])
    assert a["barycenter"].shape == (15,) and np.isfinite(a["barycenter"]).all()


def test_soft_dtw_barycenter_restarts_do_not_worsen_cost(rng):
    X = rng.normal(size=(6, 12))

    def total(b):
        return sum(M.soft_dtw_distance_windowed(b, row) for row in X)

    one = M.soft_dtw_barycenter(X, n_restarts=1)["barycenter"]
    many = M.soft_dtw_barycenter(X, n_restarts=8)["barycenter"]
    assert total(many) <= total(one) + 1e-9


def test_soft_dtw_barycenter_errors():
    with pytest.raises(ValueError, match="gamma"):
        M.soft_dtw_barycenter(np.ones((2, 3)), gamma=0.0)
    with pytest.raises(ValueError):
        M.soft_dtw_barycenter(np.empty((0, 3)))


def test_dba_tslearn_known_answer():
    res = M.dtw_barycenter_averaging(np.array([[1.0, 2, 3, 4], [1, 2, 4, 5]]), max_iter=5)
    assert set(res) == {"barycenter", "cost", "n_iter", "converged"}
    np.testing.assert_allclose(res["barycenter"], [1.0, 2.0, 3.5, 4.5])


def test_dba_identical_rows_zero_cost():
    x = np.array([0.0, 2.0, 1.0, 3.0, 0.5])
    res = M.dtw_barycenter_averaging(np.tile(x, (4, 1)))
    np.testing.assert_allclose(res["barycenter"], x)
    assert res["cost"] == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("init", [None, "mean", "medoid"])
def test_dba_cost_is_weighted_mean_dtw(rng, init):
    X = rng.normal(size=(5, 12))
    w = np.array([1.0, 2.0, 0.5, 1.0, 3.0])
    win = {"window": "sakoe_chiba", "radius": 3}
    res = M.dtw_barycenter_averaging(X, init=init, weights=w, **win)
    b = res["barycenter"]
    d = np.array([M.dtw_distance_windowed(b, row, **win) for row in X])
    assert res["cost"] == pytest.approx(np.dot(w, d) / w.sum(), rel=1e-10)


def test_dba_custom_init_and_size(rng):
    X = rng.normal(size=(4, 12))
    res = M.dtw_barycenter_averaging(X, barycenter_size=8)
    assert res["barycenter"].shape == (8,)
    res = M.dtw_barycenter_averaging(X, init=X[1].copy(), max_iter=0)
    np.testing.assert_allclose(res["barycenter"], X[1])


def test_dba_errors(rng):
    X = rng.normal(size=(3, 6))
    with pytest.raises(ValueError, match="medoid"):
        M.dtw_barycenter_averaging(X, init="median")
    with pytest.raises(ValueError):
        M.dtw_barycenter_averaging(X, weights=np.ones(2))
    with pytest.raises(ValueError):
        M.dtw_barycenter_averaging(np.array([[1.0, np.nan, 2.0]]))


# ---------------------------------------------------------------------------
# Envelopes and lower bounds
# ---------------------------------------------------------------------------


def test_lb_envelope_known_answer():
    y = np.array([0.0, 2.0, -1.0, 3.0, 1.0])
    env = M.lb_envelope(y, 1)
    np.testing.assert_array_equal(env["lower"], [0.0, -1.0, -1.0, -1.0, 1.0])
    np.testing.assert_array_equal(env["upper"], [2.0, 2.0, 3.0, 3.0, 3.0])
    w = M.lb_envelope_windowed(y, 5, window="sakoe_chiba", radius=1)
    np.testing.assert_array_equal(w["lower"], env["lower"])
    np.testing.assert_array_equal(w["upper"], env["upper"])


@pytest.mark.parametrize("win", WINDOWS)
def test_lb_envelope_windowed_is_masked_min_max(rng, win):
    y = rng.normal(size=14)
    env = M.lb_envelope_windowed(y, 11, **win)
    mask = M.dtw_window_mask(11, 14, **win)
    np.testing.assert_allclose(env["lower"], [y[row].min() for row in mask])
    np.testing.assert_allclose(env["upper"], [y[row].max() for row in mask])


def test_lb_keogh_matches_envelope_formula(rng):
    q, c = rng.normal(size=16), rng.normal(size=16)
    env = M.lb_envelope(c, 2)
    excess = np.maximum(q - env["upper"], 0) + np.maximum(env["lower"] - q, 0)
    got = M.lb_keogh(q, c, window="sakoe_chiba", radius=2)
    assert got == pytest.approx(np.sum(excess**2), rel=1e-12)


def test_lb_kim_known_answer():
    x = np.array([0.0, 3.0, 1.0, 2.0])
    y = np.array([0.5, 0.0, 0.25, 0.0])
    assert M.lb_kim(x, y) == pytest.approx(6.25)


@pytest.mark.parametrize("win", WINDOWS[:4])
@pytest.mark.parametrize("p", [1.0, 2.0])
def test_lower_bounds_bound_dtw(rng, win, p):
    for _ in range(5):
        x, y = rng.normal(size=16), rng.normal(size=16)
        d = M.dtw_distance_windowed(x, y, p=p, **win)
        keogh = M.lb_keogh(x, y, p=p, **win)
        improved = M.lb_improved(x, y, p=p, **win)
        bounds = {
            "kim": M.lb_kim(x, y, p=p),
            "keogh": keogh,
            "webb": M.lb_webb(x, y, p=p, **win),
            "improved": improved,
            "enhanced": M.lb_enhanced(x, y, 3, p=p, **win),
        }
        for name, lb in bounds.items():
            assert 0.0 <= lb <= d + 1e-9, name
        assert improved >= keogh - 1e-12


def test_lower_bounds_zero_on_identical(rng):
    x = rng.normal(size=10)
    win = {"window": "sakoe_chiba", "radius": 2}
    assert M.lb_kim(x, x) == 0.0
    assert M.lb_keogh(x, x, **win) == 0.0
    assert M.lb_webb(x, x, **win) == 0.0
    assert M.lb_improved(x, x, **win) == 0.0
    assert M.lb_enhanced(x, x, 2, **win) == 0.0


def test_lb_enhanced_requires_positive_v():
    with pytest.raises(ValueError):
        M.lb_enhanced(np.ones(5), np.ones(5), 0)


def test_early_abandon(rng):
    x, y = rng.normal(size=12), rng.normal(size=12)
    win = {"window": "sakoe_chiba", "radius": 2}
    d = M.dtw_distance_windowed(x, y, **win)
    assert M.dtw_distance_early_abandon(x, y, d, **win) == pytest.approx(d)
    assert M.dtw_distance_early_abandon(x, y, np.inf, **win) == pytest.approx(d)
    assert M.dtw_distance_early_abandon(x, y, 0.5 * d, **win) is None
    with pytest.raises(ValueError):
        M.dtw_distance_early_abandon(x, y, np.nan)


# ---------------------------------------------------------------------------
# Nearest-neighbour search
# ---------------------------------------------------------------------------


def _brute_dist(Q, R, **win):
    return np.array([[M.dtw_distance_windowed(q, r, **win) for r in R] for q in Q])


@pytest.mark.parametrize("win", WINDOWS[:2])
def test_dtw_nearest_neighbor_matches_exhaustive(rng, win):
    Q, R = rng.normal(size=(5, 20)), rng.normal(size=(12, 20))
    res = M.dtw_nearest_neighbor(Q, R, **win)
    D = _brute_dist(Q, R, **win)
    assert res["indices"].dtype == np.int64
    np.testing.assert_array_equal(res["indices"], D.argmin(axis=1))
    np.testing.assert_allclose(res["distances"], D.min(axis=1), rtol=1e-12)
    st = res["stats"]
    assert set(st) == {
        "pruned_lb_keogh",
        "pruned_lb_kim",
        "pruned_lb_webb",
        "early_abandoned",
        "dtw_completed",
    }
    assert sum(st.values()) == 5 * 12


def test_dtw_k_nearest_neighbors_matches_exhaustive(rng):
    Q, R = rng.normal(size=(4, 18)), rng.normal(size=(10, 18))
    win = {"window": "sakoe_chiba", "radius": 3}
    res = M.dtw_k_nearest_neighbors(Q, R, k=3, **win)
    D = _brute_dist(Q, R, **win)
    assert res["indices"].shape == (4, 3) and res["distances"].shape == (4, 3)
    np.testing.assert_array_equal(res["indices"], np.argsort(D, axis=1)[:, :3])
    np.testing.assert_allclose(res["distances"], np.sort(D, axis=1)[:, :3], rtol=1e-12)
    assert np.all(np.diff(res["distances"], axis=1) >= 0)
    one = M.dtw_nearest_neighbor(Q, R, **win)
    np.testing.assert_array_equal(res["indices"][:, 0], one["indices"])


def test_dtw_k_nearest_neighbors_bad_k(rng):
    Q, R = rng.normal(size=(2, 5)), rng.normal(size=(3, 5))
    with pytest.raises(ValueError):
        M.dtw_k_nearest_neighbors(Q, R, k=0)
    with pytest.raises(ValueError):
        M.dtw_k_nearest_neighbors(Q, R, k=4)


# ---------------------------------------------------------------------------
# Shape-based distance
# ---------------------------------------------------------------------------


def test_sbd_matches_ncc_reference(rng):
    for _ in range(5):
        x, y = rng.normal(size=17), rng.normal(size=17)
        res = M.sbd(x, y)
        dist, lag = _sbd_ref(x, y)
        assert res["distance"] == pytest.approx(dist, abs=1e-10)
        assert res["shift"] == lag


def test_sbd_invariances(rng):
    x = rng.normal(size=20)
    assert M.sbd(x, 3.0 * x + 10.0)["distance"] == pytest.approx(0.0, abs=1e-9)
    assert M.sbd(x, 3.0 * x + 10.0)["shift"] == 0
    assert M.sbd(x, -x)["distance"] > 0.1
    y = rng.normal(size=20)
    assert M.sbd(x, y)["distance"] == pytest.approx(M.sbd(y, x)["distance"], abs=1e-12)
    assert M.sbd(x, np.full(20, 2.0))["distance"] == pytest.approx(1.0)


def test_sbd_distance_matrix_matches_pairwise(rng):
    X = rng.normal(size=(5, 16))
    D = M.sbd_distance_matrix(X)
    assert D.shape == (5, 5)
    np.testing.assert_allclose(D, D.T, atol=1e-12)
    np.testing.assert_allclose(np.diag(D), 0.0, atol=1e-12)
    for a in range(5):
        for b in range(5):
            assert D[a, b] == pytest.approx(M.sbd(X[a], X[b])["distance"], abs=1e-12)


def test_sbd_empty_raises():
    with pytest.raises(ValueError):
        M.sbd(np.array([]), np.array([]))
