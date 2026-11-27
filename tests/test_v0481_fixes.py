"""Regression tests for the fdars-core 0.48.1 bug fixes reachable from Python.

Each test reproduces a sipemu/fdars issue (#77-#84) and asserts the corrected
behaviour.  #82 (wcr/wnet symmetric ``beta_t``) and #83 (continuous
registration ``termination``) are covered in ``test_v048_modelling.py`` and
``test_v048_alignment_registration.py``.
"""

import numpy as np
import pytest

from fdars import alignment as A

T101 = np.linspace(0.0, 1.0, 101)


def _two_peaks(s):
    return np.exp(-((s - 0.3) ** 2) / 0.004) + 0.6 * np.exp(-((s - 0.7) ** 2) / 0.004)


def test_transfer_alignment_composes_within_then_bridge():
    """#77: the total warp is gamma_i o gamma_b.  The 0.48.0 order
    gamma_b o gamma_i left errors of [0.175, 0.141] on this example."""
    t = T101
    warp = lambda a: t + a * t * (1 - t)  # noqa: E731
    source = np.array([_two_peaks(t)] * 2)
    target = np.array([_two_peaks(warp(0.5)), _two_peaks(warp(-0.5))])
    r = A.transfer_alignment(source, target, t)
    err = np.abs(r["aligned_data"] - _two_peaks(t)).max(axis=1)
    np.testing.assert_allclose(err, [0.049, 0.073], atol=0.01)
    assert np.all(err < 0.1)


@pytest.mark.parametrize(
    "m_argvals, landmarks",
    [(61, [[0.4], [0.5]]), (60, [[0.4], [0.5], [0.5]])],
    ids=["landmarks_length", "argvals_length"],
)
def test_landmark_register_identity_on_bad_input(m_argvals, landmarks):
    """#78: inconsistent input returns the curves unchanged with identity warps
    on [argvals[0], argvals[-1]] (0.48.0 returned all-zero gammas)."""
    data = np.ones((3, 61))
    t = np.linspace(0.0, 1.0, 61)[:m_argvals]
    r = A.landmark_register(data, t, landmarks)
    identity = np.linspace(t[0], t[-1], 61)
    np.testing.assert_allclose(r["gammas"], np.tile(identity, (3, 1)), atol=1e-12)
    np.testing.assert_array_equal(r["registered"], data)


def test_tsrvf_ladders_match_log_map():
    """#79: pole ladder returned exactly 0 and Schild's ladder exactly 2x the
    log-map tangent vectors; all three transports now agree."""
    rng = np.random.default_rng(0)
    t = T101
    X = np.array(
        [
            (1 + 0.3 * rng.standard_normal()) * np.exp(-(((t - 0.5 - 0.08 * rng.standard_normal()) / 0.12) ** 2))
            for _ in range(8)
        ]
    )
    v = {
        mth: A.tsrvf_transform_with_method(X, t, max_iter=10, tol=1e-3, method=mth)["tangent_vectors"]
        for mth in ("log_map", "schilds_ladder", "pole_ladder")
    }
    scale = np.abs(v["log_map"]).max()
    assert scale > 0.1
    for mth in ("schilds_ladder", "pole_ladder"):
        assert np.abs(v[mth] - v["log_map"]).max() < 1e-6 * scale, mth


def test_joint_gauss_model_keeps_amplitude_phase_correlation():
    """#80: height and peak location are perfectly linked in training; the
    samples keep the correlation (0.48.0: -0.02, diagonal score Gaussian)."""
    rng = np.random.default_rng(1)
    t = T101
    z = rng.standard_normal(40)
    X = np.array([a * np.exp(-(((t - c) / 0.1) ** 2)) for a, c in zip(1 + 0.25 * z, 0.5 + 0.08 * z)])
    assert np.corrcoef(X.max(1), t[X.argmax(1)])[0, 1] > 0.99
    S = A.joint_gauss_model(X, t, ncomp=2, n_samples=500, seed=7)["samples"]
    assert np.corrcoef(S.max(1), t[S.argmax(1)])[0, 1] > 0.9


def _multires_case():
    m = 400
    t = np.linspace(0.0, 1.0, m)
    base = np.sin(4 * np.pi * t) + 0.5 * np.sin(10 * np.pi * t)
    f2 = np.interp(np.clip(t + 0.09 * np.sin(np.pi * t), 0, 1), t, base)
    return base, f2, t


def _penalised_objective(r, t, lam):
    g = r["gamma"]
    pen = np.sum((np.diff(g) / np.diff(t) - 1) ** 2 * np.diff(t))
    return r["distance"] ** 2 + lam * pen


@pytest.mark.parametrize("kw", [{}, {"n_refine_steps": 40, "step_size": 0.1}])
def test_multires_refinement_never_worsens(kw):
    """#81: refinement used to raise the distance of the coarse-DP warp
    (0.354 -> 0.639 with defaults); it now only accepts strict decreases."""
    f1, f2, t = _multires_case()
    coarse = A.elastic_align_pair_multires(f1, f2, t, n_refine_steps=0)["distance"]
    refined = A.elastic_align_pair_multires(f1, f2, t, **kw)["distance"]
    assert refined <= coarse + 1e-12
    assert refined < 0.25 < coarse


def test_multires_refinement_honours_lambda():
    """#81: the refinement minimises the lambda-penalised objective (it used
    to ignore lambda_), so that objective does not increase."""
    f1, f2, t = _multires_case()
    lam = 0.5
    coarse = A.elastic_align_pair_multires(f1, f2, t, n_refine_steps=0, lambda_=lam)
    refined = A.elastic_align_pair_multires(f1, f2, t, lambda_=lam)
    assert _penalised_objective(refined, t, lam) < _penalised_objective(coarse, t, lam)


def test_jfpca_automatic_balance_c_keeps_phase():
    """#84: on pure phase variation the automatic balance_c collapsed to
    c ≈ 3e-4 and the first joint score ignored the shift (|corr| 0.42)."""
    rng = np.random.default_rng(0)
    t = T101
    z = rng.standard_normal(30)
    X = np.array([np.exp(-(((t - 0.5 - 0.1 * zi) / 0.08) ** 2)) for zi in z])
    r = A.jfpca_fit(X, t, ncomp=2)
    assert r["balance_c"] > 0.1
    assert abs(np.corrcoef(r["scores"][:, 0], z)[0, 1]) > 0.95
    assert A.joint_fpca(X, t, n_comp=2)["balance_c"] == pytest.approx(r["balance_c"])
