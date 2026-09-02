"""Tests for the fdars.fts submodule — Phases 67-01 through 67-03.

Covers:
- Import smoke (fdars.fts and from fdars.fts import ftsm)
- ftsm end-to-end: non-square (N=40, M=25) fixture + transposition-guard shape assertions
- ar_models list structure (keys per element)
- ncomp=0 error guard (ValueError)
- Plan 67-02: forecasting family (ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr)
- Plan 67-03: diagnostics family (functional_acf, functional_pacf, functional_difference,
              stationarity_test, long_run_covariance) — with seed determinism + symmetry checks

Plan 67-04 will APPEND spectral density and DPCA tests to this same file.
"""

from __future__ import annotations

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Non-square fixture constants (REQUIRED: N != M to detect row/col swap bugs)
# ---------------------------------------------------------------------------

N, M = 40, 25   # N observations, M grid points — deliberately non-square
assert N != M   # Guard: square fixtures hide row/col swap bugs


def make_ar1_curves(n: int, m: int, argvals: np.ndarray, phi: float = 0.7, seed: int = 0) -> np.ndarray:
    """Generate AR(1)-driven functional data curves for meaningful FTS tests."""
    rng2 = np.random.default_rng(seed)
    f1 = np.sin(np.pi * argvals)
    eps = rng2.standard_normal((n, m)) * 0.2
    scores = np.zeros(n)
    scores[0] = rng2.standard_normal()
    for t in range(1, n):
        scores[t] = phi * scores[t - 1] + rng2.standard_normal()
    return scores[:, None] * f1[None, :] + eps


# Module-level fixture data (shared across tests in this file)
_argvals = np.linspace(0.0, 1.0, M)
_data = make_ar1_curves(N, M, _argvals, phi=0.7, seed=0)
assert _data.shape == (N, M)  # (40, 25) — non-square


# ---------------------------------------------------------------------------
# Import smoke tests
# ---------------------------------------------------------------------------

def test_import_fts_module() -> None:
    """Both import styles must succeed."""
    import fdars.fts as fts  # noqa: F401 (import as attribute)
    from fdars.fts import ftsm  # noqa: F401 (direct import)
    assert callable(fts.ftsm)
    assert callable(ftsm)


# ---------------------------------------------------------------------------
# ftsm end-to-end: non-square shape assertions (transposition guard)
# ---------------------------------------------------------------------------

def test_ftsm_shapes_non_square() -> None:
    """ftsm on non-square (40×25) input returns a PyDict with correct shapes.

    If data or results were silently transposed, the (M,) and (N,) assertions
    would swap and the test would fail — catching the bug immediately.
    """
    import fdars.fts as fts

    r = fts.ftsm(_data, _argvals, ncomp=3)

    # Dict keys must all be present
    assert set(r.keys()) == {"mean", "rotation", "scores", "fitted", "weights", "ncomp", "ar_models"}

    # Shapes prove no transposition — M=25 (grid), N=40 (observations)
    assert r["mean"].shape == (M,), f"mean shape {r['mean'].shape} != ({M},)"
    assert r["rotation"].shape == (M, 3), f"rotation shape {r['rotation'].shape} != ({M}, 3)"
    assert r["scores"].shape == (N, 3), f"scores shape {r['scores'].shape} != ({N}, 3)"
    assert r["fitted"].shape == (N, M), f"fitted shape {r['fitted'].shape} != ({N}, {M})"
    assert r["weights"].shape == (M,), f"weights shape {r['weights'].shape} != ({M},)"
    assert r["ncomp"] == 3


def test_ftsm_ar_models_structure() -> None:
    """ar_models is a list of ncomp dicts each with keys order, phi, sigma2."""
    import fdars.fts as fts

    r = fts.ftsm(_data, _argvals, ncomp=3)

    assert len(r["ar_models"]) == 3
    for i, ar in enumerate(r["ar_models"]):
        assert isinstance(ar, dict), f"ar_models[{i}] is not a dict"
        assert set(ar.keys()) == {"order", "phi", "sigma2"}, (
            f"ar_models[{i}] keys {set(ar.keys())} != {{'order','phi','sigma2'}}"
        )
        assert isinstance(ar["order"], int), f"ar_models[{i}]['order'] is not int"
        assert isinstance(ar["sigma2"], float), f"ar_models[{i}]['sigma2'] is not float"
        # phi is a numpy 1D array of length == order (can be 0 if white noise)
        assert ar["phi"].ndim == 1


def test_ftsm_ncomp_zero_raises() -> None:
    """ncomp=0 must raise ValueError (upstream rejects ncomp < 1)."""
    import fdars.fts as fts

    with pytest.raises(ValueError):
        fts.ftsm(_data, _argvals, ncomp=0)


# ---------------------------------------------------------------------------
# Plan 67-02: forecasting family tests
# ---------------------------------------------------------------------------

def test_ftsm_forecast_shapes() -> None:
    """ftsm_forecast returns {forecast (h, M), h} with correct shapes."""
    import fdars.fts as fts

    # h=1 default
    r1 = fts.ftsm_forecast(_data, _argvals, h=1, ncomp=3)
    assert set(r1.keys()) == {"forecast", "h"}
    assert r1["forecast"].shape == (1, M), f"forecast shape {r1['forecast'].shape} != (1, {M})"
    assert r1["h"] == 1

    # h=3
    r3 = fts.ftsm_forecast(_data, _argvals, h=3, ncomp=3)
    assert r3["forecast"].shape == (3, M), f"forecast shape {r3['forecast'].shape} != (3, {M})"
    assert r3["h"] == 3


def test_ftsm_forecast_multistep_shapes() -> None:
    """ftsm_forecast_multistep returns {forecast (h, M), h} with correct shapes."""
    import fdars.fts as fts

    # h=1
    rm1 = fts.ftsm_forecast_multistep(_data, _argvals, h=1, ncomp=3)
    assert set(rm1.keys()) == {"forecast", "h"}
    assert rm1["forecast"].shape == (1, M), f"forecast shape {rm1['forecast'].shape} != (1, {M})"
    assert rm1["h"] == 1

    # h=3
    rm3 = fts.ftsm_forecast_multistep(_data, _argvals, h=3, ncomp=3)
    assert rm3["forecast"].shape == (3, M), f"forecast shape {rm3['forecast'].shape} != (3, {M})"
    assert rm3["h"] == 3


def test_ftsm_forecast_h1_identity() -> None:
    """ftsm_forecast and ftsm_forecast_multistep produce bit-identical output at h=1."""
    import fdars.fts as fts

    r1 = fts.ftsm_forecast(_data, _argvals, h=1, ncomp=3)
    rm1 = fts.ftsm_forecast_multistep(_data, _argvals, h=1, ncomp=3)
    np.testing.assert_array_equal(r1["forecast"], rm1["forecast"])


def test_ftsm_update_extends_scores() -> None:
    """ftsm_update with one new curve extends scores by 1 row."""
    import fdars.fts as fts

    # Build a new curve: last row of data scaled slightly
    new_curve = _data[-1:] * 1.01  # shape (1, M)
    assert new_curve.shape == (1, M)

    upd = fts.ftsm_update(_data, new_curve, _argvals, ncomp=3)

    # Must have the same 7 keys as ftsm
    assert set(upd.keys()) == {"mean", "rotation", "scores", "fitted", "weights", "ncomp", "ar_models"}

    # scores must have N+1 rows
    assert upd["scores"].shape[0] == N + 1, (
        f"scores.shape[0] = {upd['scores'].shape[0]} != {N + 1}"
    )
    assert upd["scores"].shape[1] == 3


def test_fplsr_shapes() -> None:
    """fplsr returns {forecast (1, M), fitted (N-1, M), ncomp} on the non-square fixture."""
    import fdars.fts as fts

    # N=40 >= 3, satisfies fplsr constraint
    r = fts.fplsr(_data, _argvals, ncomp=3)

    assert set(r.keys()) == {"forecast", "fitted", "ncomp"}
    assert r["forecast"].shape == (1, M), f"forecast shape {r['forecast'].shape} != (1, {M})"
    assert r["fitted"].shape == (N - 1, M), (
        f"fitted shape {r['fitted'].shape} != ({N - 1}, {M})"
    )
    assert isinstance(r["ncomp"], int)


# ---------------------------------------------------------------------------
# Plan 67-03: diagnostics family tests (FTS-02)
# ---------------------------------------------------------------------------

def test_functional_acf_keys_and_types() -> None:
    """functional_acf returns a 4-key PyDict; lags dtype must be int64."""
    import fdars.fts as fts

    r = fts.functional_acf(_data, _argvals, seed=42)

    assert set(r.keys()) == {"lags", "acf", "pacf", "upper_band"}, (
        f"keys {set(r.keys())} != expected"
    )
    # lags is Vec<u32> in Rust — must arrive as int64 numpy array (not float64)
    assert r["lags"].dtype == np.int64, (
        f"lags dtype {r['lags'].dtype} != int64 (u32 was not cast to i64)"
    )
    # All arrays must be 1D with matching length
    n_lags = len(r["lags"])
    assert r["acf"].shape == (n_lags,)
    assert r["pacf"].shape == (n_lags,)
    assert r["upper_band"].shape == (n_lags,)


def test_functional_acf_determinism() -> None:
    """Two calls with the same seed produce bit-identical acf, pacf, upper_band."""
    import fdars.fts as fts

    r1 = fts.functional_acf(_data, _argvals, seed=42)
    r2 = fts.functional_acf(_data, _argvals, seed=42)

    assert np.array_equal(r1["acf"], r2["acf"]), "acf differs across identical seeds"
    assert np.array_equal(r1["pacf"], r2["pacf"]), "pacf differs across identical seeds"
    assert np.array_equal(r1["upper_band"], r2["upper_band"]), (
        "upper_band differs across identical seeds"
    )


def test_functional_acf_different_seeds_differ() -> None:
    """Two calls with different seeds produce different Monte Carlo bands."""
    import fdars.fts as fts

    r1 = fts.functional_acf(_data, _argvals, seed=42)
    r2 = fts.functional_acf(_data, _argvals, seed=99)

    # The MC band varies with the seed; acf/pacf are deterministic (no RNG)
    # so we only check upper_band differs
    assert not np.array_equal(r1["upper_band"], r2["upper_band"]), (
        "upper_band identical across different seeds — RNG seed not honoured"
    )


def test_functional_pacf_shapes_match_acf() -> None:
    """functional_pacf returns the same 4-key dict structure as functional_acf."""
    import fdars.fts as fts

    ra = fts.functional_acf(_data, _argvals, seed=42)
    rp = fts.functional_pacf(_data, _argvals, seed=42)

    assert set(rp.keys()) == {"lags", "acf", "pacf", "upper_band"}
    assert rp["lags"].shape == ra["lags"].shape
    assert rp["acf"].shape == ra["acf"].shape
    assert rp["pacf"].shape == ra["pacf"].shape
    assert rp["upper_band"].shape == ra["upper_band"].shape


def test_functional_difference_shape() -> None:
    """functional_difference returns naked 2D array of shape (N-1, M), NOT a PyDict."""
    import fdars.fts as fts

    diff = fts.functional_difference(_data)

    # Must be a numpy array, not a dict
    assert not isinstance(diff, dict), "functional_difference must return a numpy array, not a dict"
    assert diff.shape == (N - 1, M), (
        f"diff shape {diff.shape} != ({N - 1}, {M}) — expected (39, 25)"
    )


def test_functional_difference_cumsum_roundtrip() -> None:
    """Cumulative sum of differenced data recovers original data within 1e-10."""
    import fdars.fts as fts

    diff = fts.functional_difference(_data)
    assert diff.shape == (N - 1, M)

    # Reconstruct: prepend _data[0] and cumsum along the time axis
    reconstructed = np.vstack([_data[:1], diff])
    reconstructed = np.cumsum(reconstructed, axis=0)

    # Compare against original — first row anchors the reconstruction
    # The reconstructed cumsum of the differences starting from _data[0]
    # should equal _data. Verify with tight tolerance.
    np.testing.assert_allclose(
        reconstructed,
        _data,
        atol=1e-10,
        err_msg="cumsum round-trip for functional_difference failed — check row/col convention",
    )


def test_stationarity_test_keys() -> None:
    """stationarity_test returns {statistic (float), p_value (float), n_perm (int)}."""
    import fdars.fts as fts

    r = fts.stationarity_test(_data, _argvals, seed=42)

    assert set(r.keys()) == {"statistic", "p_value", "n_perm"}, (
        f"keys {set(r.keys())} != expected"
    )
    assert isinstance(r["statistic"], float), f"statistic type {type(r['statistic'])}"
    assert isinstance(r["p_value"], float), f"p_value type {type(r['p_value'])}"
    assert isinstance(r["n_perm"], int), f"n_perm type {type(r['n_perm'])}"
    # p_value must be in [0, 1]
    assert 0.0 <= r["p_value"] <= 1.0, f"p_value {r['p_value']} out of [0,1]"


def test_stationarity_test_determinism() -> None:
    """Two calls with the same seed produce an identical p_value."""
    import fdars.fts as fts

    r1 = fts.stationarity_test(_data, _argvals, n_perm=999, seed=42)
    r2 = fts.stationarity_test(_data, _argvals, n_perm=999, seed=42)

    assert r1["p_value"] == r2["p_value"], (
        f"p_value differs across identical seeds: {r1['p_value']} vs {r2['p_value']}"
    )
    assert r1["statistic"] == r2["statistic"], "statistic differs across identical seeds"


def test_stationarity_test_nperm_zero_raises() -> None:
    """n_perm=0 must raise ValueError (upstream validates n_perm >= 1)."""
    import fdars.fts as fts

    with pytest.raises(ValueError):
        fts.stationarity_test(_data, _argvals, n_perm=0)


def test_long_run_covariance_shape_and_symmetry() -> None:
    """long_run_covariance returns cov_matrix (M, M); cov_matrix is symmetric within 1e-10."""
    import fdars.fts as fts

    r = fts.long_run_covariance(_data, _argvals)

    assert set(r.keys()) == {"cov_matrix", "m", "bandwidth", "n_curves"}, (
        f"keys {set(r.keys())} != expected"
    )
    assert isinstance(r["m"], int)
    assert isinstance(r["bandwidth"], int)
    assert isinstance(r["n_curves"], int)
    assert r["m"] == M, f"m={r['m']} != M={M}"
    assert r["n_curves"] == N, f"n_curves={r['n_curves']} != N={N}"

    C = r["cov_matrix"]
    assert C.shape == (M, M), f"cov_matrix shape {C.shape} != ({M}, {M})"

    # Symmetry check proves the column-major → row-major reshape was correct.
    # A transposed matrix would fail this because C_transposed != C for a
    # general non-symmetric matrix.
    np.testing.assert_allclose(
        C,
        C.T,
        atol=1e-10,
        err_msg=(
            "cov_matrix is not symmetric within 1e-10 — "
            "column-major reshape (FdMatrix::from_column_major) may be wrong"
        ),
    )


def test_long_run_covariance_bandwidth_default_vs_explicit() -> None:
    """bandwidth=None and explicit bandwidth give same structure; bandwidth scalar is returned."""
    import fdars.fts as fts

    r_auto = fts.long_run_covariance(_data, _argvals, bandwidth=None)
    r_exp = fts.long_run_covariance(_data, _argvals, bandwidth=r_auto["bandwidth"])

    # Same bandwidth → same cov_matrix
    np.testing.assert_array_equal(
        r_auto["cov_matrix"],
        r_exp["cov_matrix"],
        err_msg="explicit bandwidth matching auto bandwidth gave different cov_matrix",
    )


def test_functional_acf_nsim_zero_raises() -> None:
    """n_sim=0 must raise ValueError (upstream validates n_sim >= 1)."""
    import fdars.fts as fts

    with pytest.raises(ValueError):
        fts.functional_acf(_data, _argvals, n_sim=0)


# ---------------------------------------------------------------------------
# Plan 67-04: spectral / dimension-reduction family (FTS-03)
# ---------------------------------------------------------------------------

def test_spectral_density_keys_and_shapes() -> None:
    """spectral_density returns a 6-key PyDict; freqs (N,), re/im lists of N (M,M) arrays."""
    import fdars.fts as fts

    r = fts.spectral_density(_data, _argvals)

    assert set(r.keys()) == {"freqs", "re", "im", "m", "n_curves", "bandwidth"}, (
        f"keys {set(r.keys())} != expected"
    )
    assert isinstance(r["m"], int)
    assert isinstance(r["n_curves"], int)
    assert isinstance(r["bandwidth"], int)
    assert r["m"] == M, f"m={r['m']} != M={M}"
    assert r["n_curves"] == N, f"n_curves={r['n_curves']} != N={N}"

    # freqs: numpy 1D of length N
    assert r["freqs"].shape == (N,), (
        f"freqs shape {r['freqs'].shape} != ({N},)"
    )

    # re and im are Python lists of length N, each element is a (M, M) 2D numpy array
    assert isinstance(r["re"], list), "re must be a list"
    assert isinstance(r["im"], list), "im must be a list"
    assert len(r["re"]) == N, f"len(re) = {len(r['re'])} != N={N}"
    assert len(r["im"]) == N, f"len(im) = {len(r['im'])} != N={N}"

    # Check a sample of frequency slices for correct shape
    for k in [0, N // 2, N - 1]:
        assert r["re"][k].shape == (M, M), (
            f"re[{k}].shape = {r['re'][k].shape} != ({M}, {M})"
        )
        assert r["im"][k].shape == (M, M), (
            f"im[{k}].shape = {r['im'][k].shape} != ({M}, {M})"
        )


def test_spectral_density_stack() -> None:
    """np.stack(re) yields (N, M, M); demonstrates the 3D use pattern."""
    import fdars.fts as fts

    r = fts.spectral_density(_data, _argvals)
    re_3d = np.stack(r["re"])
    assert re_3d.shape == (N, M, M), (
        f"np.stack(re).shape = {re_3d.shape} != ({N}, {M}, {M})"
    )
    im_3d = np.stack(r["im"])
    assert im_3d.shape == (N, M, M)


def test_spectral_density_bandwidth_zero_raises() -> None:
    """bandwidth=0 raises ValueError (spectral_density rejects Some(0), unlike long_run_covariance)."""
    import fdars.fts as fts

    with pytest.raises(ValueError):
        fts.spectral_density(_data, _argvals, bandwidth=0)


def test_dpca_keys_and_shapes() -> None:
    """dpca returns a 7-key PyDict with computed interior scores rows and ncomp filters."""
    import fdars.fts as fts

    r = fts.dpca(_data, _argvals, ncomp=3)

    assert set(r.keys()) == {"filters", "scores", "eigenvalues", "n_freqs", "filter_lag", "ncomp", "valid_range"}, (
        f"keys {set(r.keys())} != expected"
    )
    assert isinstance(r["n_freqs"], int)
    assert isinstance(r["filter_lag"], int)
    assert isinstance(r["ncomp"], int)
    assert r["ncomp"] == 3

    # scores shape: (N - 2*filter_lag, ncomp) — do NOT hardcode the interior count
    L = r["filter_lag"]
    expected_n_interior = N - 2 * L
    assert r["scores"].shape == (expected_n_interior, 3), (
        f"scores shape {r['scores'].shape} != ({expected_n_interior}, 3) "
        f"(filter_lag={L}, N={N})"
    )

    # filters: list of ncomp 2D arrays
    assert isinstance(r["filters"], list), "filters must be a list"
    assert len(r["filters"]) == 3, f"len(filters) = {len(r['filters'])} != ncomp=3"
    for k, f_arr in enumerate(r["filters"]):
        # Each filter has shape (2L+1, M)
        assert f_arr.ndim == 2, f"filters[{k}].ndim != 2"
        assert f_arr.shape[1] == M, f"filters[{k}].shape[1] = {f_arr.shape[1]} != M={M}"

    # eigenvalues: list of ncomp 1D arrays
    assert isinstance(r["eigenvalues"], list)
    assert len(r["eigenvalues"]) == 3

    # valid_range: a 2-tuple of ints
    assert isinstance(r["valid_range"], tuple), "valid_range must be a tuple"
    assert len(r["valid_range"]) == 2
    assert isinstance(r["valid_range"][0], int)
    assert isinstance(r["valid_range"][1], int)


def test_dpca_reconstruct_keys_and_shapes() -> None:
    """dpca_reconstruct returns merged dict: dpca keys + fitted_reconstruction + reconstruction_error."""
    import fdars.fts as fts

    r = fts.dpca_reconstruct(_data, _argvals, ncomp=3)

    expected_keys = {
        "filters", "scores", "eigenvalues", "n_freqs", "filter_lag", "ncomp", "valid_range",
        "fitted_reconstruction", "reconstruction_error",
    }
    assert set(r.keys()) == expected_keys, (
        f"keys {set(r.keys())} != expected"
    )

    L = r["filter_lag"]
    n_interior = N - 2 * L

    # fitted_reconstruction: (N-2L, M) 2D array
    assert r["fitted_reconstruction"].shape == (n_interior, M), (
        f"fitted_reconstruction shape {r['fitted_reconstruction'].shape} != ({n_interior}, {M})"
    )

    # reconstruction_error: (ncomp,) 1D array
    err = r["reconstruction_error"]
    assert err.shape == (3,), f"reconstruction_error shape {err.shape} != (3,)"

    # Monotone non-increasing: cumulative error decreases as we add components
    diffs = np.diff(err)
    assert np.all(diffs <= 1e-12), (
        f"reconstruction_error is not monotone non-increasing: {err} (diffs={diffs})"
    )


def test_dpca_scores_interior_computed_not_hardcoded() -> None:
    """dpca with ncomp=2 on non-square fixture: scores rows == N - 2*filter_lag (computed)."""
    import fdars.fts as fts

    r = fts.dpca(_data, _argvals, ncomp=2)
    L = r["filter_lag"]
    expected_rows = N - 2 * L
    assert r["scores"].shape[0] == expected_rows, (
        f"scores.shape[0]={r['scores'].shape[0]} != N-2*filter_lag={expected_rows}"
    )
