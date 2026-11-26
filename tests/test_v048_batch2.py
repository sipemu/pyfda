"""Tests for the fdars-core 0.48 batch-2 bindings.

``fdars.metric``: multivariate (d, m) DTW / DBA and the aeon elastic-distance
family (``elastic_ts_*`` dispatchers, univariate and multivariate).
``fdars.clustering``: k-Shape, SBD k-medoids, DTW k-means (uni/multivariate).

Distances are checked against brute-force numpy dynamic programmes where the
recurrence is standard (multichannel DTW, DDTW, WDTW, ADTW, ERP, LCSS, MSM),
the multivariate twins against the univariate functions bit-for-bit at
``d = 1``, and the clusterers on planted clusters with fixed seeds.
"""

import numpy as np
import pytest

from fdars import alignment as A
from fdars import clustering as C
from fdars import metric as M

ELASTIC = ["ddtw", "wdtw", "wddtw", "adtw", "erp", "edr", "twe", "msm", "lcss", "shape_dtw"]
# Metrics whose distance is the last cell of the cost matrix (no normalisation,
# no descriptor lattice).
LAST_CELL = ["ddtw", "wdtw", "wddtw", "adtw", "erp", "twe", "msm"]
WINDOWS = [
    {"window": "none"},
    {"window": "sakoe_chiba", "radius": 3},
    {"window": "sakoe_chiba_fraction", "window_fraction": 0.3},
    {"window": "itakura_fraction", "max_slope": 0.8},
]


@pytest.fixture
def rng():
    return np.random.default_rng(20261127)


# ---------------------------------------------------------------------------
# Brute-force references
# ---------------------------------------------------------------------------


def _dp(n, m, cost, step=lambda D, i, j: min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])):
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = cost(i - 1, j - 1) + step(D, i, j)
    return D[n, m]


def _dtw_mv_ref(x, y, p=2.0):
    """Dependent multichannel DTW: local cost (sum_c (x_ci - y_cj)^2)^(p/2)."""
    return _dp(
        x.shape[1],
        y.shape[1],
        lambda i, j: np.sum((x[:, i] - y[:, j]) ** 2) ** (p / 2),
    )


def _slope_deriv(x):
    return ((x[1:-1] - x[:-2]) + (x[2:] - x[:-2]) / 2) / 2


def _wdtw_ref(x, y, g):
    n, m = len(x), len(y)
    mx = max(n, m)
    w = lambda k: 1.0 / (1.0 + np.exp(-g * (k - mx / 2)))  # noqa: E731
    return _dp(n, m, lambda i, j: (x[i] - y[j]) ** 2 * w(abs(i - j)))


def _adtw_ref(x, y, wp):
    return _dp(
        len(x),
        len(y),
        lambda i, j: (x[i] - y[j]) ** 2,
        step=lambda D, i, j: min(D[i - 1, j - 1], D[i - 1, j] + wp, D[i, j - 1] + wp),
    )


def _erp_ref(x, y, g):
    # aeon's border: every padded first-column / first-row entry holds the
    # *total* gap cost, not a running sum (reproduced by fdars-core).
    n, m = len(x), len(y)
    D = np.zeros((n + 1, m + 1))
    D[1:, 0] = np.abs(x - g).sum()
    D[0, 1:] = np.abs(y - g).sum()
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(
                D[i - 1, j - 1] + abs(x[i - 1] - y[j - 1]),
                D[i - 1, j] + abs(x[i - 1] - g),
                D[i, j - 1] + abs(y[j - 1] - g),
            )
    return D[n, m]


def _lcss_ref(x, y, eps):
    n, m = len(x), len(y)
    L = np.zeros((n + 1, m + 1))
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if abs(x[i - 1] - y[j - 1]) <= eps:
                L[i, j] = L[i - 1, j - 1] + 1
            else:
                L[i, j] = max(L[i - 1, j], L[i, j - 1])
    return 1.0 - L[n, m] / min(n, m)


def _msm_ref(x, y, c):
    def C_(a, b, d):
        if b <= a <= d or b >= a >= d:
            return c
        return c + min(abs(a - b), abs(a - d))

    n, m = len(x), len(y)
    D = np.zeros((n, m))
    D[0, 0] = abs(x[0] - y[0])
    for i in range(1, n):
        D[i, 0] = D[i - 1, 0] + C_(x[i], x[i - 1], y[0])
    for j in range(1, m):
        D[0, j] = D[0, j - 1] + C_(y[j], x[0], y[j - 1])
    for i in range(1, n):
        for j in range(1, m):
            D[i, j] = min(
                D[i - 1, j - 1] + abs(x[i] - y[j]),
                D[i - 1, j] + C_(x[i], x[i - 1], y[j]),
                D[i, j - 1] + C_(y[j], x[i], y[j - 1]),
            )
    return D[n - 1, m - 1]


# ---------------------------------------------------------------------------
# Multivariate DTW
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("p", [1.0, 2.0, 3.0])
def test_dtw_multivariate_matches_bruteforce(rng, p):
    x = rng.normal(size=(3, 9))
    y = rng.normal(size=(3, 7))
    assert M.dtw_distance_multivariate(x, y, p=p) == pytest.approx(
        _dtw_mv_ref(x, y, p), rel=1e-12
    )


@pytest.mark.parametrize("win", WINDOWS)
def test_dtw_multivariate_one_channel_is_univariate_bitwise(rng, win):
    x = rng.normal(size=14)
    y = rng.normal(size=11)
    assert M.dtw_distance_multivariate(x[None], y[None], **win) == M.dtw_distance_windowed(
        x, y, **win
    )
    pm = M.dtw_path_multivariate(x[None], y[None], **win)
    pu = M.dtw_path(x, y, **win)
    assert pm["cost"] == pu["cost"]
    np.testing.assert_array_equal(pm["path"], pu["path"])


def test_dtw_path_multivariate_is_valid_and_attains_cost(rng):
    x = rng.normal(size=(2, 10))
    y = rng.normal(size=(2, 8))
    res = M.dtw_path_multivariate(x, y)
    path = res["path"]
    assert path.dtype == np.int64 and path.shape[1] == 2
    assert tuple(path[0]) == (0, 0) and tuple(path[-1]) == (9, 7)
    steps = np.diff(path, axis=0)
    assert np.all((steps >= 0) & (steps <= 1)) and np.all(steps.sum(axis=1) >= 1)
    cost = sum(np.sum((x[:, i] - y[:, j]) ** 2) for i, j in path)
    assert res["cost"] == pytest.approx(cost, rel=1e-12)
    assert res["cost"] == pytest.approx(M.dtw_distance_multivariate(x, y), rel=1e-12)


def test_dtw_pairwise_multivariate_ragged_list_and_3d(rng):
    series = [rng.normal(size=(2, m)) for m in (8, 10, 7, 9)]
    D = M.dtw_pairwise_distance_multivariate(series)
    assert D.shape == (4, 4)
    np.testing.assert_array_equal(np.diag(D), 0.0)
    np.testing.assert_allclose(D, D.T, rtol=1e-12)
    for i in range(4):
        for j in range(4):
            assert D[i, j] == pytest.approx(
                M.dtw_distance_multivariate(series[i], series[j]), rel=1e-12
            )
    other = [rng.normal(size=(2, 6)) for _ in range(3)]
    X = M.dtw_pairwise_distance_multivariate(series, other, radius=2, window="sakoe_chiba")
    assert X.shape == (4, 3)
    assert X[1, 2] == pytest.approx(
        M.dtw_distance_multivariate(series[1], other[2], window="sakoe_chiba", radius=2)
    )
    arr = rng.normal(size=(5, 3, 12))
    np.testing.assert_array_equal(
        M.dtw_pairwise_distance_multivariate(arr),
        M.dtw_pairwise_distance_multivariate(list(arr)),
    )


def test_dtw_multivariate_errors(rng):
    with pytest.raises(ValueError):
        M.dtw_distance_multivariate(rng.normal(size=(2, 5)), rng.normal(size=(3, 5)))
    with pytest.raises(ValueError, match="element \\[1\\]"):
        M.dtw_pairwise_distance_multivariate([rng.normal(size=(2, 5)), np.ones(5)])
    with pytest.raises(ValueError, match="list of 2-D"):
        M.dtw_pairwise_distance_multivariate(np.ones((3, 4)))
    with pytest.raises(ValueError):
        M.dtw_pairwise_distance_multivariate([rng.normal(size=(2, 5)), rng.normal(size=(3, 5))])


# ---------------------------------------------------------------------------
# Multivariate DBA
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("init", [None, "medoid"])
def test_dba_multivariate_one_channel_is_univariate_bitwise(rng, init):
    X = rng.normal(size=(5, 12))
    win = {"window": "sakoe_chiba", "radius": 3}
    uni = M.dtw_barycenter_averaging(X, init=init, **win)
    mv = M.dtw_barycenter_averaging_multivariate(X[:, None, :], init=init, **win)
    assert mv["barycenter"].shape == (1, 12)
    np.testing.assert_array_equal(mv["barycenter"][0], uni["barycenter"])
    assert mv["cost"] == uni["cost"]
    assert mv["n_iter"] == uni["n_iter"] and mv["converged"] == uni["converged"]


def test_dba_multivariate_identical_series_and_cost(rng):
    x = rng.normal(size=(3, 10))
    res = M.dtw_barycenter_averaging_multivariate([x, x.copy(), x.copy()])
    np.testing.assert_allclose(res["barycenter"], x)
    assert res["cost"] == pytest.approx(0.0, abs=1e-12)

    series = [rng.normal(size=(2, m)) for m in (10, 12, 9, 11)]
    w = np.array([1.0, 2.0, 0.5, 1.5])
    res = M.dtw_barycenter_averaging_multivariate(series, weights=w)
    b = res["barycenter"]
    assert b.shape == (2, 12)  # mean init: longest length
    d = np.array([M.dtw_distance_multivariate(b, s) for s in series])
    assert res["cost"] == pytest.approx(np.dot(w, d) / w.sum(), rel=1e-10)


def test_dba_multivariate_custom_init_and_errors(rng):
    series = rng.normal(size=(4, 2, 10))
    res = M.dtw_barycenter_averaging_multivariate(series, init=series[2].copy(), max_iter=0)
    np.testing.assert_allclose(res["barycenter"], series[2])
    assert M.dtw_barycenter_averaging_multivariate(series, barycenter_size=6)["barycenter"].shape == (2, 6)
    with pytest.raises(ValueError, match="2-D"):
        M.dtw_barycenter_averaging_multivariate(series, init="median")
    with pytest.raises(ValueError):
        M.dtw_barycenter_averaging_multivariate(series, init=np.ones((3, 10)))
    with pytest.raises(ValueError):
        M.dtw_barycenter_averaging_multivariate([])


# ---------------------------------------------------------------------------
# Elastic-distance family: references
# ---------------------------------------------------------------------------


def test_ddtw_is_dtw_on_slope_derivatives(rng):
    x, y = rng.normal(size=13), rng.normal(size=10)
    ref = M.dtw_distance_windowed(_slope_deriv(x), _slope_deriv(y))
    assert M.elastic_ts_distance(x, y, "ddtw") == pytest.approx(ref, rel=1e-12)


@pytest.mark.parametrize("g", [0.05, 0.3])
def test_wdtw_matches_bruteforce(rng, g):
    x, y = rng.normal(size=11), rng.normal(size=9)
    assert M.elastic_ts_distance(x, y, "wdtw", g=g) == pytest.approx(_wdtw_ref(x, y, g), rel=1e-12)
    dx, dy = _slope_deriv(x), _slope_deriv(y)
    assert M.elastic_ts_distance(x, y, "wddtw", g=g) == pytest.approx(
        _wdtw_ref(dx, dy, g), rel=1e-12
    )


def test_wdtw_zero_g_is_half_dtw(rng):
    x, y = rng.normal(size=10), rng.normal(size=12)
    assert M.elastic_ts_distance(x, y, "wdtw", g=0.0) == pytest.approx(
        0.5 * M.dtw_distance_windowed(x, y), rel=1e-12
    )


@pytest.mark.parametrize("wp", [0.0, 0.7, 5.0])
def test_adtw_matches_bruteforce(rng, wp):
    x, y = rng.normal(size=10), rng.normal(size=8)
    assert M.elastic_ts_distance(x, y, "adtw", warp_penalty=wp) == pytest.approx(
        _adtw_ref(x, y, wp), rel=1e-12
    )


def test_adtw_zero_penalty_is_dtw(rng):
    x, y = rng.normal(size=9), rng.normal(size=12)
    assert M.elastic_ts_distance(x, y, "adtw", warp_penalty=0.0) == pytest.approx(
        M.dtw_distance_windowed(x, y), rel=1e-12
    )


@pytest.mark.parametrize("g", [None, 0.0, 0.5])
def test_erp_matches_bruteforce(rng, g):
    x, y = rng.normal(size=9), rng.normal(size=11)
    assert M.elastic_ts_distance(x, y, "erp", g=g) == pytest.approx(
        _erp_ref(x, y, 0.0 if g is None else g), rel=1e-12
    )


@pytest.mark.parametrize("eps", [None, 0.3])
def test_lcss_matches_bruteforce(rng, eps):
    x, y = rng.normal(size=10), rng.normal(size=12)
    assert M.elastic_ts_distance(x, y, "lcss", epsilon=eps) == pytest.approx(
        _lcss_ref(x, y, 1.0 if eps is None else eps), rel=1e-12
    )


@pytest.mark.parametrize("c", [0.1, 1.0])
def test_msm_matches_bruteforce(rng, c):
    x, y = rng.normal(size=9), rng.normal(size=8)
    assert M.elastic_ts_distance(x, y, "msm", c=c) == pytest.approx(_msm_ref(x, y, c), rel=1e-12)


def test_edr_known_answers(rng):
    x = rng.normal(size=10)
    assert M.elastic_ts_distance(x, x, "edr") == 0.0
    # Every pair farther apart than epsilon: all n edits, normalised by n.
    assert M.elastic_ts_distance(np.zeros(6), np.full(6, 5.0), "edr", epsilon=1.0) == 1.0
    d = M.elastic_ts_distance(x, x + 0.01, "edr", epsilon=0.1)
    assert d == 0.0


def test_twe_known_answers(rng):
    x = rng.normal(size=10)
    assert M.elastic_ts_distance(x, x, "twe") == 0.0
    # Equal lengths, pure match path: sum of |x_i - y_i| + |x_{i-1} - y_{i-1}|
    # with the leading zero pad, i.e. 2 * sum|x - y| - |x_n - y_n| for a
    # constant offset that is the cheapest alignment when nu, lmbda are huge.
    y = x + 0.25
    d = M.elastic_ts_distance(x, y, "twe", nu=1e6, lmbda=1e6)
    assert d == pytest.approx(0.25 * (2 * 10 - 1), rel=1e-9)


def test_shape_dtw_reach_zero_identity_is_dtw(rng):
    x, y = rng.normal(size=11), rng.normal(size=9)
    assert M.elastic_ts_distance(x, y, "shape_dtw", reach=0) == pytest.approx(
        M.dtw_distance_windowed(x, y), rel=1e-12
    )


# ---------------------------------------------------------------------------
# Elastic-distance family: properties shared by all metrics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("metric", ELASTIC)
def test_elastic_identity_symmetry_nonnegative(rng, metric):
    x, y = rng.normal(size=14), rng.normal(size=14)
    assert M.elastic_ts_distance(x, x, metric) == pytest.approx(0.0, abs=1e-12)
    d = M.elastic_ts_distance(x, y, metric)
    assert d >= 0.0
    assert d == pytest.approx(M.elastic_ts_distance(y, x, metric), rel=1e-12)


@pytest.mark.parametrize("metric", ELASTIC)
def test_elastic_alignment_path_valid_and_distance(rng, metric):
    x, y = rng.normal(size=12), rng.normal(size=10)
    res = M.elastic_ts_alignment_path(x, y, metric)
    assert set(res) == {"path", "distance"}
    path = res["path"]
    assert path.dtype == np.int64 and path.ndim == 2 and path.shape[1] == 2
    steps = np.diff(path, axis=0)
    assert np.all(steps >= 0) and np.all(steps.sum(axis=1) >= 1)
    if metric != "lcss":
        n, m = (10, 8) if metric in ("ddtw", "wddtw") else (12, 10)
        assert tuple(path[0]) == (0, 0) and tuple(path[-1]) == (n - 1, m - 1)
        assert np.all(steps <= 1)
        assert res["distance"] == pytest.approx(M.elastic_ts_distance(x, y, metric), rel=1e-12)


def test_lcss_path_lists_matched_pairs_only():
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([0.0, 10.0, 2.0, 3.0])
    res = M.elastic_ts_alignment_path(x, y, "lcss", epsilon=0.1)
    np.testing.assert_array_equal(res["path"], [[0, 0], [2, 2], [3, 3]])
    assert res["distance"] == pytest.approx(0.25)
    empty = M.elastic_ts_alignment_path(np.zeros(5), np.full(5, 10.0), "lcss")
    assert empty["path"].shape == (0, 2)
    assert empty["distance"] == pytest.approx(1.0)


@pytest.mark.parametrize("metric", LAST_CELL)
def test_elastic_cost_matrix_last_cell_is_distance(rng, metric):
    x, y = rng.normal(size=12), rng.normal(size=10)
    cm = M.elastic_ts_cost_matrix(x, y, metric)
    expected = (10, 8) if metric in ("ddtw", "wddtw") else (12, 10)
    assert cm.shape == expected
    assert cm[-1, -1] == pytest.approx(M.elastic_ts_distance(x, y, metric), rel=1e-12)


def test_elastic_cost_matrix_lcss_and_edr_shapes(rng):
    x, y = rng.normal(size=12), rng.normal(size=10)
    lc = M.elastic_ts_cost_matrix(x, y, "lcss")
    assert lc.shape == (13, 11)
    assert 1.0 - lc[-1, -1] / 10 == pytest.approx(M.elastic_ts_distance(x, y, "lcss"))
    ed = M.elastic_ts_cost_matrix(x, y, "edr")
    assert ed.shape == (12, 10)
    assert ed[-1, -1] / 12 == pytest.approx(M.elastic_ts_distance(x, y, "edr"))


@pytest.mark.parametrize("metric", ELASTIC)
@pytest.mark.parametrize("win", WINDOWS[1:])
def test_elastic_window_respected(rng, metric, win):
    x, y = rng.normal(size=16), rng.normal(size=16)
    cm = M.elastic_ts_cost_matrix(x, y, metric, **win)
    fill = 0.0 if metric == "lcss" else np.inf
    if metric == "lcss":
        cm = cm[1:, 1:]
    n, m = cm.shape
    mask = M.dtw_window_mask(n, m, **win)
    assert np.all(cm[~mask] == fill)
    assert M.elastic_ts_alignment_path(x, y, metric, **win)["path"].shape[0] > 0 or metric == "lcss"


@pytest.mark.parametrize("metric", ["ddtw", "wdtw", "adtw", "erp", "twe", "msm", "shape_dtw"])
def test_elastic_window_never_decreases_distance(rng, metric):
    x, y = rng.normal(size=15), rng.normal(size=15)
    free = M.elastic_ts_distance(x, y, metric)
    band = M.elastic_ts_distance(x, y, metric, window="sakoe_chiba", radius=1)
    assert band >= free - 1e-12


@pytest.mark.parametrize("metric", ELASTIC)
def test_elastic_pairwise_matches_pointwise(rng, metric):
    X = rng.normal(size=(4, 12))
    Y = rng.normal(size=(3, 12))
    D = M.elastic_ts_pairwise_distance(X, metric)
    assert D.shape == (4, 4)
    np.testing.assert_array_equal(np.diag(D), 0.0)
    np.testing.assert_allclose(D, D.T, rtol=1e-12)
    Dxy = M.elastic_ts_pairwise_distance(X, metric, Y)
    assert Dxy.shape == (4, 3)
    for i in range(4):
        for j in range(3):
            assert Dxy[i, j] == pytest.approx(M.elastic_ts_distance(X[i], Y[j], metric), rel=1e-12)


@pytest.mark.parametrize(
    "descriptor,param", [("identity", None), ("paa", 4), ("dwt", 2), ("slope", 3), ("derivative", None)]
)
def test_shape_dtw_descriptors(rng, descriptor, param):
    x, y = rng.normal(size=20), rng.normal(size=18)
    kw = {"descriptor": descriptor, "descriptor_param": param, "reach": 4}
    d = M.elastic_ts_distance(x, y, "shape_dtw", **kw)
    assert d >= 0.0 and np.isfinite(d)
    assert M.elastic_ts_distance(x, x, "shape_dtw", **kw) == pytest.approx(0.0, abs=1e-12)
    assert M.elastic_ts_alignment_path(x, y, "shape_dtw", **kw)["distance"] == pytest.approx(d)


def test_shape_dtw_descriptor_param_default_and_bounds(rng):
    x, y = rng.normal(size=20), rng.normal(size=18)
    assert M.elastic_ts_distance(x, y, "shape_dtw", descriptor="paa") == M.elastic_ts_distance(
        x, y, "shape_dtw", descriptor="paa", descriptor_param=8
    )
    with pytest.raises(ValueError):
        M.elastic_ts_distance(x, y, "shape_dtw", descriptor="paa", descriptor_param=10, reach=2)
    with pytest.raises(ValueError):
        M.elastic_ts_distance(x, y, "shape_dtw", descriptor="slope", descriptor_param=0)
    # The distance is the raw cost along the alignment found in descriptor
    # space: with near-degenerate slope segments (8 on a 9-point window)
    # descriptors tie and d(x, x) need not vanish (sktime semantics).
    assert M.elastic_ts_distance(x, x, "shape_dtw", descriptor="slope", reach=4) > 0.0


def test_elastic_unused_params_ignored(rng):
    x, y = rng.normal(size=10), rng.normal(size=10)
    assert M.elastic_ts_distance(x, y, "twe") == M.elastic_ts_distance(
        x, y, "twe", g=3.0, c=9.0, warp_penalty=4.0, descriptor="paa"
    )


def test_elastic_errors(rng):
    x, y = rng.normal(size=10), rng.normal(size=10)
    with pytest.raises(ValueError, match="shape_dtw"):
        M.elastic_ts_distance(x, y, "dtw")
    with pytest.raises(ValueError, match="derivative"):
        M.elastic_ts_distance(x, y, "shape_dtw", descriptor="raw")
    with pytest.raises(ValueError, match="radius"):
        M.elastic_ts_distance(x, y, "wdtw", window="sakoe_chiba")
    with pytest.raises(ValueError):
        M.elastic_ts_distance(np.ones(2), np.ones(2), "ddtw")
    with pytest.raises(ValueError):
        M.elastic_ts_distance(x, y, "twe", nu=-1.0)


# ---------------------------------------------------------------------------
# Elastic-distance family: multivariate twins
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("metric", ELASTIC)
def test_elastic_multivariate_one_channel_is_univariate_bitwise(rng, metric):
    x, y = rng.normal(size=13), rng.normal(size=11)
    win = {"window": "sakoe_chiba", "radius": 4}
    X1, Y1 = x[None], y[None]
    assert M.elastic_ts_distance_multivariate(X1, Y1, metric, **win) == M.elastic_ts_distance(
        x, y, metric, **win
    )
    np.testing.assert_array_equal(
        M.elastic_ts_cost_matrix_multivariate(X1, Y1, metric, **win),
        M.elastic_ts_cost_matrix(x, y, metric, **win),
    )
    pm = M.elastic_ts_alignment_path_multivariate(X1, Y1, metric, **win)
    pu = M.elastic_ts_alignment_path(x, y, metric, **win)
    np.testing.assert_array_equal(pm["path"], pu["path"])
    assert pm["distance"] == pu["distance"]
    data = rng.normal(size=(4, 12))
    np.testing.assert_array_equal(
        M.elastic_ts_pairwise_distance_multivariate(data[:, None, :], metric, **win),
        M.elastic_ts_pairwise_distance(data, metric, **win),
    )


@pytest.mark.parametrize("metric", ELASTIC)
def test_elastic_multivariate_pairwise_matches_pointwise(rng, metric):
    series = [rng.normal(size=(2, m)) for m in (12, 14, 11)]
    other = rng.normal(size=(2, 2, 13))
    D = M.elastic_ts_pairwise_distance_multivariate(series, metric)
    np.testing.assert_array_equal(np.diag(D), 0.0)
    Dxo = M.elastic_ts_pairwise_distance_multivariate(series, metric, other)
    assert Dxo.shape == (3, 2)
    for i in range(3):
        assert D[i, (i + 1) % 3] == pytest.approx(
            M.elastic_ts_distance_multivariate(series[i], series[(i + 1) % 3], metric), rel=1e-12
        )
        for j in range(2):
            assert Dxo[i, j] == pytest.approx(
                M.elastic_ts_distance_multivariate(series[i], other[j], metric), rel=1e-12
            )


def test_wdtw_multivariate_uses_dependent_squared_cost(rng):
    x, y = rng.normal(size=(3, 9)), rng.normal(size=(3, 8))
    # g = 0 makes the weight a constant 1/2: half the dependent multichannel DTW.
    assert M.elastic_ts_distance_multivariate(x, y, "wdtw", g=0.0) == pytest.approx(
        0.5 * _dtw_mv_ref(x, y), rel=1e-12
    )


def test_msm_multivariate_independent_sums_channels(rng):
    x, y = rng.normal(size=(3, 9)), rng.normal(size=(3, 8))
    total = sum(M.elastic_ts_distance(x[c], y[c], "msm") for c in range(3))
    assert M.elastic_ts_distance_multivariate(x, y, "msm") == pytest.approx(total, rel=1e-12)
    dep = M.elastic_ts_distance_multivariate(x, y, "msm", independent=False)
    assert np.isfinite(dep) and dep != pytest.approx(total)


def test_elastic_multivariate_channel_mismatch_raises(rng):
    with pytest.raises(ValueError):
        M.elastic_ts_distance_multivariate(rng.normal(size=(2, 8)), rng.normal(size=(3, 8)), "erp")
    with pytest.raises(ValueError):
        M.elastic_ts_pairwise_distance_multivariate(
            [rng.normal(size=(2, 8)), rng.normal(size=(3, 8))], "erp"
        )


# ---------------------------------------------------------------------------
# Clustering: planted data
# ---------------------------------------------------------------------------


def _planted_shapes(rng, n_per=8, m=60):
    """Sines and square waves with random phase shifts and amplitude/offset."""
    t = np.linspace(0, 1, m)
    rows, labels = [], []
    for g in range(2):
        for _ in range(n_per):
            s = rng.uniform(-0.15, 0.15)
            base = np.sin(2 * np.pi * (t + s)) if g == 0 else np.sign(np.sin(4 * np.pi * (t + s)))
            rows.append(rng.uniform(0.5, 3.0) * base + rng.uniform(-2, 2) + 0.05 * rng.normal(size=m))
            labels.append(g)
    return np.array(rows), np.array(labels)


def _planted_bumps(rng, n_per=6, m=40, d=1):
    """Up-bumps vs. down-bumps (in channel 0 / last channel) at jittered positions."""
    t = np.linspace(0, 1, m)
    series, labels = [], []
    for g in range(2):
        for _ in range(n_per):
            c = rng.uniform(0.3, 0.7)
            b = np.exp(-(((t - c) / 0.08) ** 2))
            s = 0.02 * rng.normal(size=(d, m))
            if g == 0:
                s[0] += b
            else:
                s[-1] -= b
            series.append(s)
            labels.append(g)
    return np.array(series), np.array(labels)


def _same_partition(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return np.array_equal(a[:, None] == a[None, :], b[:, None] == b[None, :])


# ---------------------------------------------------------------------------
# k-Shape and SBD k-medoids
# ---------------------------------------------------------------------------


def test_kshape_recovers_planted_shapes(rng):
    X, truth = _planted_shapes(rng)
    res = C.kshape_fd(X, n_clusters=2, seed=3)
    assert set(res) == {"centroids", "cluster", "inertia", "iter", "converged", "n_init_best", "model"}
    assert _same_partition(res["cluster"], truth)
    assert res["centroids"].shape == (2, X.shape[1])
    assert res["cluster"].dtype == np.int64
    assert 0 <= res["n_init_best"] < 10


def test_kshape_centroids_znormalized_and_inertia_is_sbd_sum(rng):
    X, _ = _planted_shapes(rng)
    res = C.kshape_fd(X, n_clusters=2, seed=1)
    cent = res["centroids"]
    np.testing.assert_allclose(cent.mean(axis=1), 0.0, atol=1e-10)
    np.testing.assert_allclose(cent.std(axis=1), 1.0, rtol=1e-8)
    inertia = sum(M.sbd(X[i], cent[k])["distance"] for i, k in enumerate(res["cluster"]))
    assert res["inertia"] == pytest.approx(inertia, rel=1e-8)


def test_kshape_model_predict_and_determinism(rng):
    X, truth = _planted_shapes(rng)
    res = C.kshape_fd(X, n_clusters=2, seed=5)
    model = res["model"]
    assert type(model).__name__ == "PyKShapeFit"
    np.testing.assert_array_equal(model.predict(X), res["cluster"])
    np.testing.assert_array_equal(model.cluster, res["cluster"])
    np.testing.assert_array_equal(model.centroids, res["centroids"])
    assert model.inertia == res["inertia"] and model.n_clusters == 2
    # Fresh draws of each shape land with their training group.
    Xn, tn = _planted_shapes(np.random.default_rng(99), n_per=3)
    pred = model.predict(Xn)
    lab = {g: res["cluster"][truth == g][0] for g in (0, 1)}
    np.testing.assert_array_equal(pred, [lab[g] for g in tn])
    again = C.kshape_fd(X, n_clusters=2, seed=5)
    np.testing.assert_array_equal(again["cluster"], res["cluster"])
    assert again["inertia"] == res["inertia"]


def test_kshape_errors(rng):
    X, _ = _planted_shapes(rng, n_per=2)
    with pytest.raises(ValueError):
        C.kshape_fd(X, n_clusters=10)
    with pytest.raises(ValueError):
        C.kshape_fd(X, n_init=0)
    model = C.kshape_fd(X)["model"]
    with pytest.raises(ValueError):
        model.predict(X[:, :10])


def test_sbd_kmedoids_matches_explicit_flow_and_recovers(rng):
    X, truth = _planted_shapes(rng)
    res = C.sbd_kmedoids(X, k=2, seed=7)
    assert set(res) == {
        "labels", "medoid_indices", "within_distances", "total_within_distance", "n_iter", "converged"
    }
    manual = A.kmedoids_from_distances(M.sbd_distance_matrix(X), 2, 100, 7)
    for key in ("labels", "medoid_indices", "within_distances"):
        np.testing.assert_array_equal(res[key], manual[key])
    assert res["total_within_distance"] == manual["total_within_distance"]
    assert _same_partition(res["labels"], truth)
    np.testing.assert_array_equal(res["labels"][res["medoid_indices"]], np.arange(2))


def test_sbd_kmedoids_errors(rng):
    X, _ = _planted_shapes(rng, n_per=2)
    with pytest.raises(ValueError):
        C.sbd_kmedoids(X, k=10)


# ---------------------------------------------------------------------------
# DTW k-means
# ---------------------------------------------------------------------------


def test_dtw_kmeans_recovers_planted_bumps(rng):
    S, truth = _planted_bumps(rng)
    X = S[:, 0, :]
    res = C.dtw_kmeans(X, n_clusters=2, seed=0)
    assert set(res) == {"centroids", "cluster", "inertia", "iter", "converged", "n_init_best", "model"}
    assert _same_partition(res["cluster"], truth)
    assert res["centroids"].shape == (2, X.shape[1])


def test_dtw_kmeans_inertia_and_assignment_are_dtw(rng):
    S, _ = _planted_bumps(rng)
    X = S[:, 0, :]
    win = {"window": "sakoe_chiba", "radius": 6}
    res = C.dtw_kmeans(X, n_clusters=2, seed=2, **win)
    cent = res["centroids"]
    D = np.array([[M.dtw_distance_windowed(x, c, **win) for c in cent] for x in X])
    np.testing.assert_array_equal(res["cluster"], D.argmin(axis=1))
    assert res["inertia"] == pytest.approx(D.min(axis=1).mean(), rel=1e-10)


def test_dtw_kmeans_model_predict(rng):
    S, truth = _planted_bumps(rng)
    X = S[:, 0, :]
    res = C.dtw_kmeans(X, n_clusters=2, seed=0, window="sakoe_chiba", radius=8)
    model = res["model"]
    assert type(model).__name__ == "PyDtwKMeansFit"
    np.testing.assert_array_equal(model.predict(X), res["cluster"])
    np.testing.assert_array_equal(model.centroids, res["centroids"])
    assert model.inertia == res["inertia"]
    Sn, tn = _planted_bumps(np.random.default_rng(5), n_per=3)
    lab = {g: res["cluster"][truth == g][0] for g in (0, 1)}
    np.testing.assert_array_equal(model.predict(Sn[:, 0, :]), [lab[g] for g in tn])


def test_dtw_kmeans_explicit_init(rng):
    S, truth = _planted_bumps(rng)
    X = S[:, 0, :]
    init = X[[0, len(X) - 1]].copy()
    res = C.dtw_kmeans(X, n_clusters=2, init=init, n_init=1)
    assert res["cluster"][0] == 0 and res["cluster"][-1] == 1
    assert _same_partition(res["cluster"], truth)
    with pytest.raises(ValueError, match="k-means"):
        C.dtw_kmeans(X, init="random")
    with pytest.raises(ValueError):
        C.dtw_kmeans(X, n_clusters=2, init=X[:3])
    with pytest.raises(ValueError):
        C.dtw_kmeans(X, n_clusters=len(X) + 1)
    with pytest.raises(ValueError):
        C.dtw_kmeans(X, window="itakura")


def test_dtw_kmeans_multivariate_one_channel_is_univariate_bitwise(rng):
    S, _ = _planted_bumps(rng)
    uni = C.dtw_kmeans(S[:, 0, :], n_clusters=2, seed=4, n_init=3)
    mv = C.dtw_kmeans_multivariate(S, n_clusters=2, seed=4, n_init=3)
    np.testing.assert_array_equal(mv["cluster"], uni["cluster"])
    assert mv["inertia"] == uni["inertia"]
    assert len(mv["centroids"]) == 2
    for k in range(2):
        assert mv["centroids"][k].shape == (1, S.shape[2])
        np.testing.assert_array_equal(mv["centroids"][k][0], uni["centroids"][k])


def test_dtw_kmeans_multivariate_recovers_and_predicts(rng):
    S, truth = _planted_bumps(rng, d=2)
    res = C.dtw_kmeans_multivariate(list(S), n_clusters=2, seed=0)
    assert _same_partition(res["cluster"], truth)
    model = res["model"]
    assert type(model).__name__ == "PyDtwKMeansMultivariateFit"
    np.testing.assert_array_equal(model.predict(S), res["cluster"])
    np.testing.assert_array_equal(model.predict(list(S)), res["cluster"])
    for a, b in zip(model.centroids, res["centroids"]):
        np.testing.assert_array_equal(a, b)
    D = np.array([[_dtw_mv_ref(s, c) for c in res["centroids"]] for s in S])
    assert res["inertia"] == pytest.approx(D.min(axis=1).mean(), rel=1e-9)
    with pytest.raises(ValueError):
        model.predict(S[:, :1, :])


def test_dtw_kmeans_multivariate_explicit_init(rng):
    S, truth = _planted_bumps(rng, d=2)
    init = S[[0, len(S) - 1]].copy()
    res = C.dtw_kmeans_multivariate(S, n_clusters=2, init=init, n_init=1)
    assert res["cluster"][0] == 0 and res["cluster"][-1] == 1
    res_list = C.dtw_kmeans_multivariate(S, n_clusters=2, init=list(init), n_init=1)
    np.testing.assert_array_equal(res_list["cluster"], res["cluster"])
    with pytest.raises(ValueError):
        C.dtw_kmeans_multivariate(S, n_clusters=2, init=S[:2, :1, :])
    with pytest.raises(ValueError, match="k-means"):
        C.dtw_kmeans_multivariate(S, init="kmeans")
