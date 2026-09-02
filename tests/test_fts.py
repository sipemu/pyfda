"""Tests for the fdars.fts submodule — Phase 67 tracer slice.

Covers:
- Import smoke (fdars.fts and from fdars.fts import ftsm)
- ftsm end-to-end: non-square (N=40, M=25) fixture + transposition-guard shape assertions
- ar_models list structure (keys per element)
- ncomp=0 error guard (ValueError)

Plans 67-02/03/04 will APPEND their own test functions to this same file.
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
