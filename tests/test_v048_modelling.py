"""Batch 6 (fdars-core 0.48): modelling.

PEER / LPEER structured-penalty scalar-on-function regression
(``scalar_on_function``), the wavelet DWT primitive (``basis``) and the
wavelet-domain WCR / WNET regressors, the jfPCA fit/transform model
(``alignment``), elastic permutation importance and the VEESA pipeline with
Python predictors (``explain``), and PACE-based optimal design
(``pace_fpca``).

Correctness checks: DWT perfect reconstruction and energy preservation over
families / levels / boundary modes / odd lengths, Haar known answers, wavelet
denoising by band replacement; planted beta(t) recovered by PEER / LPEER /
WCR / WNET with predict == fitted on training data; GCV / REML lambda finite;
LPEER variance components positive and close to the planted ones; jfPCA
training scores reproduced exactly, c = 0 principal direction = Karcher mean;
PFI flags the informative component (incl. a scikit-learn predictor) and
propagates Python exceptions; greedy optimal design beats random designs; and
the ValueError paths. All data are small and seeded.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import simpson

from fdars import alignment as al
from fdars import basis
from fdars import explain as ex
from fdars import pace_fpca as pf
from fdars import scalar_on_function as sof

# ---------------------------------------------------------------------------
# Wavelet DWT primitive
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("wavelet", ["haar", "db2", "db4", "db7", "db10"])
@pytest.mark.parametrize("mode", ["periodic", "symmetric"])
@pytest.mark.parametrize("n", [64, 75, 101, 128])
def test_dwt_perfect_reconstruction(wavelet, mode, n):
    rng = np.random.default_rng(n)
    x = rng.normal(size=n)
    max_level = basis.wavelet_max_level(n, wavelet)
    for level in sorted({1, max_level}):
        d = basis.wavelet_decompose(x, wavelet=wavelet, mode=mode, level=level)
        assert d["levels"] == level
        assert d["signal_len"] == n
        assert len(d["details"]) == level
        xr = basis.wavelet_reconstruct(d["coeffs"])
        assert xr.shape == (n,)
        np.testing.assert_allclose(xr, x, atol=1e-10)


@pytest.mark.parametrize("wavelet", ["haar", "db3", "db6"])
def test_dwt_periodic_even_preserves_energy(wavelet):
    x = np.random.default_rng(1).normal(size=128)
    d = basis.wavelet_decompose(x, wavelet=wavelet)
    energy = np.sum(d["approx"] ** 2) + sum(np.sum(b**2) for b in d["details"])
    assert energy == pytest.approx(np.sum(x**2), rel=1e-12)
    # band lengths halve finest-first; total = n for an even periodic pyramid
    lens = [len(b) for b in d["details"]]
    assert lens == sorted(lens, reverse=True)
    assert sum(lens) + len(d["approx"]) == 128


def test_haar_known_answers():
    x = np.array([1.0, 3.0, 5.0, 11.0])
    s = np.sqrt(2.0)
    d1 = basis.wavelet_decompose(x, wavelet="haar", level=1)
    np.testing.assert_allclose(d1["approx"], [4 / s, 16 / s], atol=1e-14)
    np.testing.assert_allclose(d1["details"][0], [-2 / s, -6 / s], atol=1e-14)
    d2 = basis.wavelet_decompose(x, wavelet="haar")  # max level = log2(4) = 2
    assert d2["levels"] == 2
    np.testing.assert_allclose(d2["approx"], [10.0], atol=1e-13)  # sum / 2
    np.testing.assert_allclose(d2["details"][1], [-6.0], atol=1e-13)
    # a constant signal has zero detail at every level
    dc = basis.wavelet_decompose(np.full(16, 2.5), wavelet="haar")
    for band in dc["details"]:
        np.testing.assert_allclose(band, 0.0, atol=1e-14)
    np.testing.assert_allclose(dc["approx"], [2.5 * 4.0], atol=1e-13)


def test_db1_is_haar_and_names_echoed():
    x = np.random.default_rng(2).normal(size=32)
    a = basis.wavelet_decompose(x, wavelet="db1", mode="symmetric")
    b = basis.wavelet_decompose(x, wavelet="haar", mode="symmetric")
    np.testing.assert_array_equal(a["approx"], b["approx"])
    assert a["wavelet"] == "haar" and a["mode"] == "symmetric"
    c = a["coeffs"]
    assert (c.wavelet, c.mode, c.levels, c.signal_len) == ("haar", "symmetric", 5, 32)
    np.testing.assert_array_equal(c.approx, a["approx"])
    for u, v in zip(c.details, a["details"]):
        np.testing.assert_array_equal(u, v)


def test_wavelet_max_level_formula():
    assert basis.wavelet_max_level(64, "haar") == 6
    assert basis.wavelet_max_level(100, "haar") == 6
    # db4: filter length 8 -> floor(log2(n / 7))
    assert basis.wavelet_max_level(64, "db4") == int(np.floor(np.log2(64 / 7)))
    assert basis.wavelet_max_level(1000, "db10") == int(np.floor(np.log2(1000 / 19)))


def test_decompose_matrix_matches_rows():
    X = np.random.default_rng(3).normal(size=(4, 50))
    rows = basis.wavelet_decompose_matrix(X, wavelet="db3", mode="symmetric", level=2)
    assert len(rows) == 4
    for i, d in enumerate(rows):
        single = basis.wavelet_decompose(X[i], wavelet="db3", mode="symmetric", level=2)
        np.testing.assert_array_equal(d["approx"], single["approx"])
        np.testing.assert_allclose(basis.wavelet_reconstruct(d["coeffs"]), X[i], atol=1e-10)


def test_reconstruct_with_replaced_bands_denoises():
    t = np.linspace(0, 1, 128, endpoint=False)
    clean = np.where(t < 0.5, 1.0, -1.0)  # piecewise constant: sparse in Haar
    noisy = clean + 0.2 * np.random.default_rng(4).normal(size=128)
    d = basis.wavelet_decompose(noisy, wavelet="haar")
    thr = 0.2 * np.sqrt(2 * np.log(128))
    soft = [np.sign(b) * np.maximum(np.abs(b) - thr, 0.0) for b in d["details"]]
    den = basis.wavelet_reconstruct(d["coeffs"], details=soft)
    assert np.mean((den - clean) ** 2) < 0.25 * np.mean((noisy - clean) ** 2)
    # replacing nothing / everything with the stored bands is the identity
    same = basis.wavelet_reconstruct(d["coeffs"], approx=d["approx"], details=d["details"])
    np.testing.assert_allclose(same, noisy, atol=1e-12)
    # the handle is not mutated by a replacement
    np.testing.assert_allclose(basis.wavelet_reconstruct(d["coeffs"]), noisy, atol=1e-12)


def test_wavelet_errors():
    x = np.ones(64)
    with pytest.raises(ValueError, match="wavelet"):
        basis.wavelet_decompose(x, wavelet="db11")
    with pytest.raises(ValueError, match="wavelet"):
        basis.wavelet_decompose(x, wavelet="sym4")
    with pytest.raises(ValueError, match="mode"):
        basis.wavelet_decompose(x, mode="zero")
    with pytest.raises(ValueError, match="level"):
        basis.wavelet_decompose(x, level=0)
    with pytest.raises(ValueError, match="level"):
        basis.wavelet_decompose(x, wavelet="haar", level=7)
    with pytest.raises(ValueError):
        basis.wavelet_decompose(np.array([]))
    with pytest.raises(ValueError, match="too short"):
        basis.wavelet_max_level(16, "db10")
    with pytest.raises(ValueError):
        basis.wavelet_decompose_matrix(np.zeros((0, 8)))
    d = basis.wavelet_decompose(x, wavelet="haar", level=2)
    with pytest.raises(ValueError, match="approx must have length"):
        basis.wavelet_reconstruct(d["coeffs"], approx=np.zeros(3))
    with pytest.raises(ValueError, match="2 bands"):
        basis.wavelet_reconstruct(d["coeffs"], details=[np.zeros(32)])
    with pytest.raises(ValueError, match=r"details\[1\]"):
        basis.wavelet_reconstruct(d["coeffs"], details=[np.zeros(32), np.zeros(5)])


# ---------------------------------------------------------------------------
# PEER / LPEER
# ---------------------------------------------------------------------------

N, M = 80, 41
T = np.linspace(0.0, 1.0, M)
BETA = 2.0 * np.sin(np.pi * T)


def _fourier_curves(n, rng):
    basis_fns = [np.ones(M)] + [
        f(2 * np.pi * k * T) for k in range(1, 5) for f in (np.sin, np.cos)
    ]
    return rng.normal(size=(n, len(basis_fns))) @ np.array(basis_fns)


@pytest.fixture(scope="module")
def peer_data():
    rng = np.random.default_rng(1)
    X = _fourier_curves(N, rng)
    y = simpson(X * BETA, x=T, axis=1) + 0.5 + 0.01 * rng.normal(size=N)
    return X, y


@pytest.mark.parametrize("lam", [None, "gcv", "reml", 1e-3])
def test_peer_recovers_planted_beta(peer_data, lam):
    X, y = peer_data
    r = sof.peer(X, y, T, lambda_=lam)
    assert np.corrcoef(r["beta"], BETA)[0, 1] > 0.999
    assert np.linalg.norm(r["beta"] - BETA) / np.linalg.norm(BETA) < 0.02
    assert np.isfinite(r["lambda_"]) and r["lambda_"] > 0
    assert r["penalty_type"] == "difference"
    expected = {None: "gcv", "gcv": "gcv", "reml": "reml", 1e-3: "fixed"}[lam]
    assert r["lambda_method"] == expected
    assert (r["gcv"] is not None) == (expected == "gcv")
    if expected == "fixed":
        assert r["lambda_"] == 1e-3
    assert r["intercept"] == pytest.approx(y.mean())
    model = r["model"]
    np.testing.assert_allclose(model.predict(X, T), r["fitted_values"], atol=1e-9)
    np.testing.assert_array_equal(model.beta, r["beta"])
    assert model.lambda_ == r["lambda_"] and model.intercept == r["intercept"]
    assert 0 < r["effective_df"] <= M


def test_peer_predict_formula_on_new_curves(peer_data):
    X, y = peer_data
    r = sof.peer(X, y, T, lambda_="reml")
    Xn = _fourier_curves(5, np.random.default_rng(9))
    # y* = (intercept - w_bar . beta) + integral x*(t) beta(t) dt (Simpson)
    manual = r["intercept"] - r["w_bar"] @ r["beta"] + simpson(Xn * r["beta"], x=T, axis=1)
    np.testing.assert_allclose(r["model"].predict(Xn, T), manual, atol=1e-9)


def test_peer_decree_identity_equals_ridge(peer_data):
    X, y = peer_data
    a = sof.peer(X, y, T, penalty="decree", decree_q=np.eye(M), lambda_=1e-3)
    b = sof.peer(X, y, T, penalty="ridge", lambda_=1e-3)
    assert a["penalty_type"] == "decree" and b["penalty_type"] == "ridge"
    np.testing.assert_allclose(a["beta"], b["beta"], atol=1e-12)


def test_peer_large_lambda_shrinks_ridge(peer_data):
    X, y = peer_data
    small = sof.peer(X, y, T, penalty="ridge", lambda_=1e-6)
    big = sof.peer(X, y, T, penalty="ridge", lambda_=1e4)
    assert np.linalg.norm(big["beta"]) < 0.01 * np.linalg.norm(small["beta"])
    assert big["effective_df"] < small["effective_df"]


def test_lpeer_recovers_beta_and_variance_components(peer_data):
    X, y = peer_data
    rng = np.random.default_rng(5)
    n_subj = 20
    sid = np.repeat(np.arange(n_subj), N // n_subj)
    u = 0.5 * rng.normal(size=n_subj)
    y2 = y + u[sid]
    r = sof.lpeer(X, y2, T, sid * 7 + 3)  # arbitrary labels are re-indexed
    assert r["n_subjects"] == n_subj
    assert r["sigma2_subject"] > 0 and r["sigma2_resid"] > 0
    assert r["sigma2_subject"] > 10 * r["sigma2_resid"]
    assert 0.05 < r["sigma2_subject"] < 1.0  # planted 0.25
    assert np.corrcoef(r["beta"], BETA)[0, 1] > 0.99
    assert np.isfinite(r["lambda_"]) and r["lambda_method"] == "gcv"
    np.testing.assert_allclose(r["model"].predict(X, T), r["fitted_values"], atol=1e-9)
    # labels of any int dtype give the same fit
    r32 = sof.lpeer(X, y2, T, (sid * 7 + 3).astype(np.int32))
    np.testing.assert_array_equal(r32["beta"], r["beta"])


def test_lpeer_reml_and_fixed(peer_data):
    X, y = peer_data
    sid = np.repeat(np.arange(10), 8)
    for lam, method in [("reml", "reml"), (0.5, "fixed")]:
        r = sof.lpeer(X, y, T, sid, lambda_=lam)
        assert r["lambda_method"] == method and r["gcv"] is None
        assert np.isfinite(r["lambda_"]) and r["lambda_"] >= 0


def test_peer_errors(peer_data):
    X, y = peer_data
    with pytest.raises(ValueError, match="penalty must be"):
        sof.peer(X, y, T, penalty="lasso")
    with pytest.raises(ValueError, match="requires decree_q"):
        sof.peer(X, y, T, penalty="decree")
    with pytest.raises(ValueError, match="only used with penalty='decree'"):
        sof.peer(X, y, T, penalty="ridge", decree_q=np.eye(M))
    with pytest.raises(ValueError, match="square"):
        sof.peer(X, y, T, penalty="decree", decree_q=np.eye(M)[:5])
    with pytest.raises(ValueError):
        sof.peer(X, y, T, penalty="decree", decree_q=np.eye(M - 1))
    with pytest.raises(ValueError, match="lambda_"):
        sof.peer(X, y, T, lambda_="aic")
    with pytest.raises(ValueError, match="lambda_"):
        sof.peer(X, y, T, lambda_=-1.0)
    with pytest.raises(ValueError):
        sof.peer(X, y[:-1], T)
    with pytest.raises(ValueError):
        sof.peer(X, y, T[:-1])
    with pytest.raises(ValueError):
        sof.peer(X, y, T).get("model").predict(X[:, :-1], T[:-1])
    with pytest.raises(ValueError, match="non-negative"):
        sof.lpeer(X, y, T, -np.ones(N, dtype=int))
    with pytest.raises(ValueError, match="2 distinct subjects"):
        sof.lpeer(X, y, T, np.zeros(N, dtype=int))
    with pytest.raises(ValueError):
        sof.lpeer(X, y, T, np.arange(N - 1))


# ---------------------------------------------------------------------------
# WCR / WNET
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def wcr_data():
    rng = np.random.default_rng(2)
    n, m = 60, 64
    t = np.arange(m) / m
    B = np.array(
        [np.sin(2 * np.pi * k * t + ph) for k, ph in [(1, 0), (1, 1.3), (2, 0), (2, 1.1), (3, 0.5)]]
    )
    X = (rng.normal(size=(n, 5)) * np.array([3, 2.5, 2, 1.5, 1])) @ B
    beta = 10 * B.T @ np.array([1.0, -0.5, 0.3, 0.2, -0.1]) / m  # in the row space of X
    y = X @ beta + 1.0 + 0.001 * rng.normal(size=n)
    return X, y, beta


@pytest.mark.parametrize("method", ["pcr", "pls"])
@pytest.mark.parametrize("wavelet", ["haar", "db4"])
def test_wcr_recovers_planted_beta(wcr_data, method, wavelet):
    X, y, beta = wcr_data
    r = sof.wcr(X, y, wavelet=wavelet, ncomp=5, method=method)
    assert r["method"] == method and r["wavelet"] == wavelet and r["mode"] == "periodic"
    assert r["ncomp"] == 5 and r["level"] == basis.wavelet_max_level(64, wavelet)
    assert len(r["coeff_weights"]) == 64
    assert np.corrcoef(r["beta_t"], beta)[0, 1] > 0.9999
    assert np.linalg.norm(r["beta_t"] - beta) / np.linalg.norm(beta) < 1e-2
    assert r["intercept"] == pytest.approx(1.0, abs=1e-2)
    np.testing.assert_allclose(r["fitted_values"] + r["residuals"], y, atol=1e-12)
    np.testing.assert_allclose(r["model"].predict(X), r["fitted_values"], atol=1e-8)
    # periodic: beta_t is the exact time-domain coefficient of the fitted values
    np.testing.assert_allclose(X @ r["beta_t"] + r["intercept"], r["fitted_values"], atol=1e-8)
    np.testing.assert_array_equal(r["model"].beta_t, r["beta_t"])


def test_wcr_symmetric_predict_self_consistent(wcr_data):
    X, y, _ = wcr_data
    r = sof.wcr(X, y, mode="symmetric", ncomp=5)
    assert r["mode"] == "symmetric"
    assert len(r["coeff_weights"]) > 64  # symmetric extension doubles each level
    np.testing.assert_allclose(r["model"].predict(X), r["fitted_values"], atol=1e-8)
    np.testing.assert_allclose(r["fitted_values"], y, atol=0.01)


@pytest.mark.xfail(
    strict=True,
    reason="fdars-core 0.48: under mode='symmetric' beta_t = reconstruct(coeff_weights) "
    "truncates the mirror extension instead of applying the adjoint, so "
    "X @ beta_t + intercept != fitted_values (predict itself is correct)",
)
@pytest.mark.parametrize("fit", ["wcr", "wnet"])
def test_symmetric_beta_t_matches_fitted(wcr_data, fit):
    X, y, _ = wcr_data
    r = sof.wcr(X, y, mode="symmetric", ncomp=5) if fit == "wcr" else sof.wnet(X, y, mode="symmetric")
    np.testing.assert_allclose(X @ r["beta_t"] + r["intercept"], r["fitted_values"], atol=1e-6)


def _sparse_haar_beta(m):
    d = basis.wavelet_decompose(np.zeros(m), wavelet="haar")
    details = [np.zeros_like(b) for b in d["details"]]
    details[2][1] = 3.0
    details[3][0] = -2.0
    return basis.wavelet_reconstruct(d["coeffs"], approx=np.zeros_like(d["approx"]), details=details)


@pytest.fixture(scope="module")
def wnet_data():
    rng = np.random.default_rng(6)
    n, m = 150, 32
    X = rng.normal(size=(n, m))
    beta = _sparse_haar_beta(m)
    y = X @ beta + 0.5 + 0.05 * rng.normal(size=n)
    return X, y, beta


@pytest.mark.parametrize("alpha", [1.0, 0.5])
def test_wnet_recovers_sparse_beta(wnet_data, alpha):
    X, y, beta = wnet_data
    r = sof.wnet(X, y, wavelet="haar", alpha=alpha)
    assert r["alpha"] == alpha and r["level"] == 5
    assert np.isfinite(r["lambda_"]) and r["lambda_"] > 0
    assert np.corrcoef(r["beta_t"], beta)[0, 1] > 0.9999
    assert np.linalg.norm(r["beta_t"] - beta) / np.linalg.norm(beta) < 0.02
    cw = r["coeff_weights"]
    np.testing.assert_array_equal(r["selected"], np.flatnonzero(cw))
    assert r["selected"].dtype == np.int64
    assert len(r["selected"]) < 32  # genuinely sparse
    np.testing.assert_allclose(r["model"].predict(X), r["fitted_values"], atol=1e-10)
    np.testing.assert_allclose(X @ r["beta_t"] + r["intercept"], r["fitted_values"], atol=1e-8)
    assert r["intercept"] == pytest.approx(0.5, abs=0.05)


def test_wnet_lasso_selects_planted_coefficients(wnet_data):
    X, y, _ = wnet_data
    r = sof.wnet(X, y, wavelet="haar", alpha=1.0)
    # the two largest weights are the two planted Haar atoms
    top = np.argsort(-np.abs(r["coeff_weights"]))[:2]
    assert set(top) <= set(r["selected"])
    big = np.abs(r["coeff_weights"][top])
    assert np.all(big > 1.5)
    rest = np.delete(r["coeff_weights"], top)
    assert np.max(np.abs(rest)) < 0.1


def test_wnet_explicit_grid_and_determinism(wnet_data):
    X, y, _ = wnet_data
    a = sof.wnet(X, y, wavelet="haar", lambda_grid=[0.5, 0.05, 0.005], seed=3)
    b = sof.wnet(X, y, wavelet="haar", lambda_grid=[0.5, 0.05, 0.005], seed=3)
    assert a["lambda_"] in (0.5, 0.05, 0.005)
    np.testing.assert_array_equal(a["coeff_weights"], b["coeff_weights"])


def test_wcr_wnet_errors(wcr_data):
    X, y, _ = wcr_data
    with pytest.raises(ValueError, match="method must be"):
        sof.wcr(X, y, method="ols")
    with pytest.raises(ValueError, match="ncomp"):
        sof.wcr(X, y, ncomp=0)
    with pytest.raises(ValueError):
        sof.wcr(X[:2], y[:2])
    with pytest.raises(ValueError, match="wavelet"):
        sof.wcr(X, y, wavelet="coif1")
    with pytest.raises(ValueError, match="level"):
        sof.wcr(X, y, level=20)
    with pytest.raises(ValueError):
        sof.wcr(X, y).get("model").predict(X[:, :32])
    with pytest.raises(ValueError, match="alpha"):
        sof.wnet(X, y, alpha=1.5)
    with pytest.raises(ValueError, match="n_folds"):
        sof.wnet(X, y, n_folds=1)
    with pytest.raises(ValueError, match="lambda_grid"):
        sof.wnet(X, y, lambda_grid=[])
    with pytest.raises(ValueError, match="mode"):
        sof.wnet(X, y, mode="reflect")


# ---------------------------------------------------------------------------
# jfPCA model
# ---------------------------------------------------------------------------

MJ = 30
TJ = np.linspace(0.0, 1.0, MJ)


def _bumps(n, seed, m=MJ):
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, m)
    amps = 1 + 0.5 * rng.normal(size=n)
    shifts = 0.08 * rng.normal(size=n)
    return np.array([a * np.exp(-((t - 0.5 - s) ** 2) / 0.02) for a, s in zip(amps, shifts)])


@pytest.fixture(scope="module")
def jfpca():
    X = _bumps(14, 3)
    return X, al.jfpca_fit(X, TJ, ncomp=3)


def test_jfpca_fit_keys_and_shapes(jfpca):
    X, r = jfpca
    n, m = X.shape
    assert r["ncomp"] == 3
    assert r["scores"].shape == (n, 3)
    assert r["vert_component"].shape == (3, m + 1)
    assert r["horiz_component"].shape == (3, m)
    assert r["mean_q"].shape == (m + 1,)
    assert r["training_gammas"].shape == r["training_aligned"].shape == (n, m)
    assert np.all(np.diff(r["eigenvalues"]) <= 0) and np.all(r["eigenvalues"] > 0)
    assert np.all(np.diff(r["cumulative_variance"]) >= 0)
    assert r["lambda_"] == 0.0 and r["balance_c"] > 0
    model = r["model"]
    assert model.ncomp == 3 and model.balance_c == r["balance_c"] and model.lambda_ == 0.0
    np.testing.assert_array_equal(model.argvals, TJ)
    np.testing.assert_array_equal(model.eigenvalues, r["eigenvalues"])
    d = model.to_dict()
    assert set(d) == set(r) - {"model"}
    np.testing.assert_array_equal(d["scores"], r["scores"])


def test_jfpca_scores_match_joint_fpca(jfpca):
    X, r = jfpca
    jf = al.joint_fpca(X, TJ, n_comp=3)
    np.testing.assert_allclose(r["scores"], jf["scores"], atol=1e-8)
    np.testing.assert_allclose(r["eigenvalues"], jf["eigenvalues"], atol=1e-10)


def test_jfpca_score_training_round_trip(jfpca):
    _, r = jfpca
    st = r["model"].score_training()
    np.testing.assert_allclose(st["scores"], r["scores"], atol=1e-8)
    np.testing.assert_array_equal(st["aligned"], r["training_aligned"])
    np.testing.assert_array_equal(st["warping"], r["training_gammas"])


def test_jfpca_transform_training_curves(jfpca):
    X, r = jfpca
    tr = r["model"].transform(X)
    assert tr["scores"].shape == (14, 3)
    assert tr["aligned"].shape == tr["warping"].shape == X.shape
    # re-alignment to the fixed template differs from the Karcher post-centred
    # warps, so only the well-determined leading component agrees closely
    s, s0 = tr["scores"][:, 0], r["scores"][:, 0]
    assert np.corrcoef(s, s0)[0, 1] > 0.999
    assert np.max(np.abs(s - s0)) < 0.05 * np.max(np.abs(s0))
    # warps are monotone and fix the end points
    assert np.all(np.diff(tr["warping"], axis=1) >= -1e-12)
    np.testing.assert_allclose(tr["warping"][:, [0, -1]], np.tile([0.0, 1.0], (14, 1)), atol=1e-12)


def test_jfpca_principal_directions(jfpca):
    _, r = jfpca
    model = r["model"]
    pd = model.principal_directions(0, [-2.0, -1.0, 0.0, 1.0, 2.0])
    assert pd["pc_index"] == 0
    np.testing.assert_array_equal(pd["c_values"], [-2, -1, 0, 1, 2])
    assert pd["amplitude_curves"].shape == pd["phase_curves"].shape == (5, MJ)
    np.testing.assert_allclose(pd["amplitude_curves"][2], model.karcher_mean, atol=1e-10)
    # c = 0 phase is (numerically) the identity warp
    np.testing.assert_allclose(pd["phase_curves"][2], TJ, atol=1e-2)
    # opposite directions move the amplitude curve symmetrically away from the mean
    up = pd["amplitude_curves"][3] - model.karcher_mean
    down = pd["amplitude_curves"][1] - model.karcher_mean
    assert np.linalg.norm(up) > 1e-3
    assert np.corrcoef(up, down)[0, 1] < -0.9


def test_jfpca_errors(jfpca):
    X, r = jfpca
    model = r["model"]
    with pytest.raises(ValueError):
        al.jfpca_fit(X, TJ, ncomp=0)
    with pytest.raises(ValueError):
        al.jfpca_fit(X, TJ[:-1])
    with pytest.raises(ValueError):
        al.jfpca_fit(X[:1], TJ)
    with pytest.raises(ValueError):
        model.transform(X[:, :-1])
    with pytest.raises(ValueError, match="pc_index"):
        model.principal_directions(3, [1.0])
    with pytest.raises(ValueError, match="c_values"):
        model.principal_directions(0, [])


# ---------------------------------------------------------------------------
# Elastic PFI / VEESA
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pfi_data(jfpca):
    _, r = jfpca
    S = r["model"].score_training()["scores"]
    coef = np.array([0.0, 3.0, 0.0])  # only the 2nd component is informative
    y = S @ coef + 1.0
    return S, y, coef


def test_elastic_pfi_flags_informative_component(pfi_data):
    S, y, coef = pfi_data
    r = ex.elastic_pfi(S, y, lambda s: s @ coef + 1.0)
    assert r["baseline_metric"] == pytest.approx(0.0, abs=1e-20)
    imp = r["importance"]
    assert imp.shape == (3,)
    assert imp[1] < 0  # mse: informative -> negative
    np.testing.assert_allclose(imp[[0, 2]], 0.0, atol=1e-20)
    np.testing.assert_allclose(r["permuted_metric"], r["baseline_metric"] - imp)
    # deterministic in the seed, different across seeds
    again = ex.elastic_pfi(S, y, lambda s: s @ coef + 1.0)
    np.testing.assert_array_equal(again["importance"], imp)
    other = ex.elastic_pfi(S, y, lambda s: s @ coef + 1.0, seed=7)
    assert other["importance"][1] != imp[1]


def test_elastic_pfi_metrics(pfi_data):
    S, y, coef = pfi_data

    def pred(s):
        return s @ coef + 1.0

    mse = ex.elastic_pfi(S, y, pred, metric="mse")
    neg = ex.elastic_pfi(S, y, pred, metric=lambda a, b: -np.mean((a - b) ** 2))
    np.testing.assert_allclose(neg["importance"], -mse["importance"], atol=1e-12)
    mae = ex.elastic_pfi(S, y, pred, metric="mae")
    assert mae["importance"][1] < 0
    labels = (S[:, 1] > 0).astype(float)
    acc = ex.elastic_pfi(S, labels, lambda s: (s[:, 1] > 0).astype(float), metric="accuracy")
    assert acc["baseline_metric"] == 1.0
    assert acc["importance"][1] > 0
    np.testing.assert_allclose(acc["importance"][[0, 2]], 0.0)


def test_elastic_pfi_with_sklearn_predictor(pfi_data):
    LinearRegression = pytest.importorskip("sklearn.linear_model").LinearRegression
    S, y, _ = pfi_data
    reg = LinearRegression().fit(S, y)
    r = ex.elastic_pfi(S, y, reg.predict, n_repeats=20)
    assert np.argmin(r["importance"]) == 1
    assert abs(r["importance"][1]) > 100 * max(abs(r["importance"][0]), abs(r["importance"][2]))


class _Boom(RuntimeError):
    pass


def test_elastic_pfi_python_exceptions_propagate(pfi_data):
    S, y, coef = pfi_data
    calls = []

    def bad_predict(s):
        calls.append(1)
        if len(calls) > 3:
            raise _Boom("predict exploded")
        return s @ coef

    with pytest.raises(_Boom, match="predict exploded"):
        ex.elastic_pfi(S, y, bad_predict)
    assert len(calls) == 4  # stops calling Python after the first error

    def bad_metric(a, b):
        raise _Boom("metric exploded")

    with pytest.raises(_Boom, match="metric exploded"):
        ex.elastic_pfi(S, y, lambda s: s @ coef, metric=bad_metric)
    with pytest.raises(_Boom, match="predict exploded"):
        ex.veesa_pipeline(_bumps(14, 3), TJ, y, lambda s: (_ for _ in ()).throw(_Boom("predict exploded")))


def test_elastic_pfi_errors(pfi_data):
    S, y, coef = pfi_data
    with pytest.raises(ValueError, match="callable"):
        ex.elastic_pfi(S, y, "not callable")
    with pytest.raises(ValueError, match="metric"):
        ex.elastic_pfi(S, y, lambda s: s @ coef, metric="r2")
    with pytest.raises(ValueError, match="metric"):
        ex.elastic_pfi(S, y, lambda s: s @ coef, metric=3)
    with pytest.raises(ValueError, match="n_repeats"):
        ex.elastic_pfi(S, y, lambda s: s @ coef, n_repeats=0)
    with pytest.raises(ValueError):
        ex.elastic_pfi(S, y[:-1], lambda s: s @ coef)
    with pytest.raises(ValueError, match="predictions"):
        ex.elastic_pfi(S, y, lambda s: (s @ coef)[:-1])
    # a wrong length only on permuted calls is caught as well
    n_calls = []

    def short_later(s):
        n_calls.append(1)
        out = s @ coef
        return out if len(n_calls) == 1 else out[:-1]

    with pytest.raises(ValueError, match="predictions"):
        ex.elastic_pfi(S, y, short_later)
    with pytest.raises(ValueError, match="could not convert"):
        ex.elastic_pfi(S, y, lambda s: "nope")


def test_veesa_pipeline_matches_two_step(jfpca, pfi_data):
    X, r = jfpca
    S, y, coef = pfi_data
    v = ex.veesa_pipeline(X, TJ, y, lambda s: s @ coef + 1.0, ncomp=3)
    assert set(v) == {"model", "jfpca", "training_scores", "pfi"}
    np.testing.assert_allclose(v["jfpca"]["scores"], r["scores"], atol=1e-12)
    np.testing.assert_allclose(v["training_scores"]["scores"], S, atol=1e-12)
    two_step = ex.elastic_pfi(S, y, lambda s: s @ coef + 1.0)
    np.testing.assert_allclose(v["pfi"]["importance"], two_step["importance"], atol=1e-10)
    assert type(v["model"]).__name__ == "PyJfpcaModel"
    assert v["model"].ncomp == 3


# ---------------------------------------------------------------------------
# PACE model handle + optimal design
# ---------------------------------------------------------------------------

GRID = list(np.linspace(0.0, 1.0, 21))


@pytest.fixture(scope="module")
def pace_model():
    rng = np.random.default_rng(4)
    avs, vals = [], []
    for _ in range(40):
        k = rng.integers(4, 8)
        ti = np.sort(rng.uniform(0, 1, k))
        xi = (
            rng.normal() * np.sin(2 * np.pi * ti)
            + 0.5 * rng.normal() * np.cos(2 * np.pi * ti)
            + 0.05 * rng.normal(size=k)
        )
        avs.append(ti)
        vals.append(xi)
    h = pf.irreg_fdata_from_lists(avs, vals)
    return h, pf.pace_fpca_fit(h, ncomp=2, bandwidth=0.15, work_grid=GRID)


def test_pace_fpca_fit_matches_pace_fpca(pace_model):
    h, model = pace_model
    assert type(model).__name__ == "PyPaceFpcaFit"
    assert model.ncomp == 2 and model.sigma2 == 0.01
    np.testing.assert_allclose(model.argvals, GRID)
    d = pf.pace_fpca(h, ncomp=2, bandwidth=0.15, work_grid=GRID)
    md = model.to_dict()
    assert set(md) == set(d)
    for k in d:
        np.testing.assert_array_equal(np.asarray(md[k]), np.asarray(d[k]))
    np.testing.assert_array_equal(model.eigenvalues, d["eigenvalues"])


def test_design_criterion_baselines_and_monotone(pace_model):
    _, model = pace_model
    lam = model.eigenvalues
    assert pf.design_criterion(model, []) == pytest.approx(lam.sum())
    assert pf.design_criterion(model, [], "a") == pytest.approx(lam.sum())
    assert pf.design_criterion(model, [], "d") == pytest.approx(np.log(lam).sum())
    for crit in ["trajectory", "a", "d"]:
        vals = [pf.design_criterion(model, list(range(0, k * 4, 4)), crit) for k in range(6)]
        assert np.all(np.diff(vals) <= 1e-12)
    # orthonormal eigenfunctions: integrated trajectory MSE = trace of score posterior
    sel = [2, 9, 15]
    assert pf.design_criterion(model, sel) == pytest.approx(pf.design_criterion(model, sel, "a"), rel=1e-10)


@pytest.mark.parametrize("criterion", ["trajectory", "a", "d"])
def test_optimal_design_valid_and_beats_random(pace_model, criterion):
    _, model = pace_model
    r = pf.optimal_design(model, budget=4, criterion=criterion)
    idx = r["selected_indices"]
    assert idx.dtype == np.int64 and len(idx) == 4 and len(set(idx)) == 4
    assert np.all((idx >= 0) & (idx < len(GRID)))
    np.testing.assert_allclose(r["selected_argvals"], np.asarray(GRID)[idx])
    trace = r["criterion_trace"]
    assert np.all(np.diff(trace) <= 1e-12)
    assert trace[-1] == pytest.approx(pf.design_criterion(model, idx, criterion), rel=1e-12)
    rng = np.random.default_rng(0)
    rand = [pf.design_criterion(model, rng.choice(len(GRID), 4, replace=False), criterion) for _ in range(50)]
    assert trace[-1] <= np.median(rand)
    assert trace[-1] < pf.design_criterion(model, [0, 1, 2, 3], criterion)
    # deterministic
    again = pf.optimal_design(model, budget=4, criterion=criterion)
    np.testing.assert_array_equal(again["selected_indices"], idx)


def test_optimal_design_candidate_grid(pace_model):
    _, model = pace_model
    cand = [1.0, 0.5, 0.0, 0.25, 0.75, 0.25]  # unordered, with a duplicate
    r = pf.optimal_design(model, budget=3, candidate_grid=cand)
    assert set(r["selected_argvals"]) <= set(cand)
    assert len(set(r["selected_indices"])) == 3
    one = pf.optimal_design(model)
    assert len(one["selected_indices"]) == 1
    # the single best point of the full grid is no worse than the best restricted one
    best_restricted = pf.optimal_design(model, budget=1, candidate_grid=cand)
    assert one["criterion_trace"][0] <= best_restricted["criterion_trace"][0] + 1e-15


def test_optimal_design_errors(pace_model):
    _, model = pace_model
    with pytest.raises(ValueError, match="criterion"):
        pf.design_criterion(model, [1], "e")
    with pytest.raises(ValueError, match="out of range"):
        pf.design_criterion(model, [21])
    with pytest.raises(ValueError, match="non-negative"):
        pf.design_criterion(model, [-1])
    with pytest.raises(ValueError, match="budget"):
        pf.optimal_design(model, budget=0)
    with pytest.raises(ValueError, match="budget"):
        pf.optimal_design(model, budget=3, candidate_grid=[0.0, 0.5])
    with pytest.raises(ValueError, match="distinct"):
        pf.optimal_design(model, budget=2, candidate_grid=[0.5, 0.5])
    with pytest.raises(ValueError, match="not found"):
        pf.optimal_design(model, budget=1, candidate_grid=[0.123])
    with pytest.raises(ValueError, match="criterion"):
        pf.optimal_design(model, criterion="trace")
