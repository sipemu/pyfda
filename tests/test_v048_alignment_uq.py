"""Batch 5 (fdars-core 0.48): elastic uncertainty quantification.

Elastic amplitude / phase box plots, elastic DP-means, amplitude / phase
PERMANOVA (+ ``inference.permanova``), Bayesian group alignment,
exponential-family registration with generalized FPCA, partial-curve
conformal prediction (``conformal``) and elastic conformal anomaly detection
(``tolerance``).

Correctness checks: PERMANOVA against a hand-computed pseudo-F and its
behaviour under H0 / planted amplitude vs phase effects, box-plot refits and
classification parity, DP-means cluster count vs penalty, MCMC warps monotone
and ordered like the planted shifts, tempering K=1 bit-identical to the
default, expfam warps recovering planted shifts (Bernoulli / Poisson),
conformal coverage over seeds, simultaneous vs pointwise bands, observation
patterns consistent with the prefix path, and the ValueError paths. All data
are tiny and seeded so the file runs in seconds.
"""

from __future__ import annotations

import numpy as np
import pytest

from fdars import alignment as al
from fdars import conformal, inference, pace_fpca, tolerance

M = 30
T = np.linspace(0.0, 1.0, M)


def bump(t, c=0.5, w=0.02, a=1.0):
    return a * np.exp(-((t - c) ** 2) / w)


def shifted_bumps(shifts, amps=None, m=M, w=0.02):
    t = np.linspace(0.0, 1.0, m)
    amps = np.ones(len(shifts)) if amps is None else amps
    return np.array([bump(t, 0.5 + s, w, a) for s, a in zip(shifts, amps)])


def exp_warp(s, t=T):
    """Monotone warp (e^{st} - 1)/(e^s - 1) of [0, 1] (identity at s = 0)."""
    if abs(s) < 1e-12:
        return t.copy()
    return (np.exp(s * t) - 1.0) / (np.exp(s) - 1.0)


def two_bump(t):
    return bump(t, 0.35, 0.02) + 0.7 * bump(t, 0.68, 0.016)


def pseudo_f(dist, labels):
    """Anderson (2001) pseudo-F on a distance matrix, computed by hand."""
    n = len(labels)
    groups = np.unique(labels)
    k = len(groups)
    d2 = dist**2
    sst = d2[np.triu_indices(n, 1)].sum() / n
    ssw = 0.0
    for g in groups:
        idx = np.flatnonzero(labels == g)
        sub = d2[np.ix_(idx, idx)]
        ssw += sub[np.triu_indices(len(idx), 1)].sum() / len(idx)
    ssb = sst - ssw
    return (ssb / (k - 1)) / (ssw / (n - k)), ssb, ssw, sst


def euclid(x):
    return np.sqrt(((x[:, None, :] - x[None, :, :]) ** 2).sum(-1))


# ---------------------------------------------------------------------------
# inference.permanova
# ---------------------------------------------------------------------------


class TestPermanova:
    def test_matches_hand_computed_pseudo_f(self):
        rng = np.random.default_rng(0)
        x = rng.normal(size=(15, 3))
        x[10:] += 0.8
        labels = np.array([0] * 5 + [3] * 5 + [7] * 5)
        d = euclid(x)
        r = inference.permanova(d, labels, n_perm=99, seed=1)
        f, ssb, ssw, sst = pseudo_f(d, labels)
        assert r["statistic"] == pytest.approx(f, rel=1e-12)
        assert r["ss_between"] == pytest.approx(ssb, rel=1e-12)
        assert r["ss_within"] == pytest.approx(ssw, rel=1e-12)
        assert r["ss_total"] == pytest.approx(sst, rel=1e-12)
        assert r["r_squared"] == pytest.approx(ssb / sst, rel=1e-12)
        assert (r["df_between"], r["df_within"], r["n_perm"]) == (2, 12, 99)

    def test_null_p_values_not_small_and_planted_effect_detected(self):
        p_null = []
        for s in range(6):
            rng = np.random.default_rng(100 + s)
            x = rng.normal(size=(16, 2))
            p_null.append(
                inference.permanova(euclid(x), np.repeat([0, 1], 8), n_perm=199, seed=s)["p_value"]
            )
        assert np.mean(p_null) > 0.25
        assert min(p_null) > 0.01

        rng = np.random.default_rng(7)
        x = rng.normal(size=(16, 2))
        x[8:] += 2.0
        r = inference.permanova(euclid(x), np.repeat([0, 1], 8), n_perm=199, seed=0)
        # the group-swap relabelling reproduces F exactly, so p can be 2 / 200
        assert r["p_value"] <= 2.0 / 200.0 + 1e-12

    def test_p_value_bounds_and_seed_determinism(self):
        rng = np.random.default_rng(3)
        d = euclid(rng.normal(size=(12, 2)))
        labels = np.repeat([0, 1, 2], 4)
        a = inference.permanova(d, labels, n_perm=50, seed=9)
        b = inference.permanova(d, labels, n_perm=50, seed=9)
        assert a == b
        assert 1.0 / 51.0 <= a["p_value"] <= 1.0
        assert inference.permanova(d, labels, n_perm=0)["p_value"] == 1.0

    @pytest.mark.parametrize(
        "dist, labels, match",
        [
            (np.zeros((4, 3)), [0, 0, 1, 1], "square"),
            (np.ones((4, 4)), [0, 0, 1, 1], "diagonal"),
            (euclid(np.arange(8.0).reshape(4, 2)), [0, 0, 0, 0], "2 distinct groups"),
            (euclid(np.arange(8.0).reshape(4, 2)), [0, -1, 1, 1], "non-negative"),
            (euclid(np.arange(8.0).reshape(4, 2)), [0, 1, 1], "labels"),
        ],
    )
    def test_value_errors(self, dist, labels, match):
        with pytest.raises(ValueError, match=match):
            inference.permanova(dist, np.asarray(labels), n_perm=9)


# ---------------------------------------------------------------------------
# alignment.elastic_phase_amplitude_test
# ---------------------------------------------------------------------------


def amp_phase_data(amp_effect, phase_effect, n_per=7, seed=0):
    rng = np.random.default_rng(seed)
    labels = np.repeat([0, 1], n_per)
    rows = []
    for g in labels:
        s = rng.normal(0.0, 0.3) + (1.5 if (phase_effect and g == 1) else 0.0)
        a = 1.0 + rng.normal(0.0, 0.05) + (0.5 if (amp_effect and g == 1) else 0.0)
        rows.append(a * two_bump(exp_warp(s)))
    return np.array(rows), labels


class TestPhaseAmplitudeTest:
    def test_amplitude_effect_detected_only_in_amplitude(self):
        data, labels = amp_phase_data(True, False)
        r = al.elastic_phase_amplitude_test(data, T, labels, n_perm=199, seed=1)
        assert r["amplitude"]["p_value"] < 0.01
        assert r["phase"]["p_value"] > 0.05
        assert r["joint"]["p_value"] < 0.05

    def test_phase_effect_detected_only_in_phase(self):
        data, labels = amp_phase_data(False, True)
        r = al.elastic_phase_amplitude_test(data, T, labels, n_perm=199, seed=1)
        assert r["phase"]["p_value"] < 0.01
        assert r["amplitude"]["p_value"] > 0.05

    def test_permanova_parity_and_structure(self):
        data, labels = amp_phase_data(True, False, n_per=5)
        labels = np.where(labels == 0, 4, 9)
        r = al.elastic_phase_amplitude_test(data, T, labels, n_perm=49, seed=3, joint=False)
        assert r["joint"] is None
        for key in ("amplitude", "phase"):
            d = r[f"{key}_distances"]
            assert d.shape == (10, 10)
            np.testing.assert_allclose(d, d.T, atol=1e-12)
            assert np.all(np.diag(d) == 0.0)
            assert r[key] == inference.permanova(d, labels, n_perm=49, seed=3)
        np.testing.assert_array_equal(r["group_labels"], [4, 9])
        np.testing.assert_array_equal(r["group_sizes"], [5, 5])
        assert r["alignment"]["gammas"].shape == (10, M)

    def test_template_aligned_metric(self):
        data, labels = amp_phase_data(True, False, n_per=5)
        r = al.elastic_phase_amplitude_test(
            data, T, labels, n_perm=49, amplitude_metric="template_aligned"
        )
        assert r["amplitude"]["p_value"] < 0.05

    def test_value_errors(self):
        data, labels = amp_phase_data(True, False, n_per=3)
        with pytest.raises(ValueError, match="amplitude_metric"):
            al.elastic_phase_amplitude_test(data, T, labels, amplitude_metric="l2")
        with pytest.raises(ValueError, match="labels"):
            al.elastic_phase_amplitude_test(data, T, labels[:-1], n_perm=9)
        with pytest.raises(ValueError, match="lambda"):
            al.elastic_phase_amplitude_test(data, T, labels, lambda_=-1.0, n_perm=9)


# ---------------------------------------------------------------------------
# Elastic box plots
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def boxplot_data():
    rng = np.random.default_rng(5)
    rows = [
        (1.0 + rng.normal(0.0, 0.05)) * two_bump(exp_warp(rng.normal(0.0, 0.4)))
        for _ in range(14)
    ]
    rows.append(2.5 * two_bump(T))  # amplitude outlier (index 14)
    rows.append(two_bump(exp_warp(4.0)))  # phase outlier (index 15)
    return np.array(rows)


class TestElasticBoxplots:
    def test_structure_and_order(self, boxplot_data):
        r = al.elastic_boxplots(boxplot_data, T)
        amp, ph = r["amplitude"], r["phase"]
        n = boxplot_data.shape[0]
        assert r["gammas"].shape == r["aligned_data"].shape == (n, M)
        for bp in (amp, ph):
            assert bp["distances"].shape == (n,)
            assert 0.0 <= bp["r50"] <= bp["ralpha"]
            assert bp["alpha"] == 0.05 and bp["k_a"] == 1.0
        assert 14 in amp["outlier_indices"]
        assert 15 in ph["outlier_indices"]
        assert ph["median"][0] == pytest.approx(0.0) and ph["median"][-1] == pytest.approx(1.0)
        assert np.all(np.diff(ph["median"]) >= -1e-12)

    def test_refits_from_components_are_identical(self, boxplot_data):
        r = al.elastic_boxplots(boxplot_data, T)
        amp = al.amplitude_boxplot_from_aligned(
            r["aligned_data"],
            r["aligned_srsfs"],
            r["amplitude"]["median"],
            r["amplitude"]["median_srsf"],
            T,
        )
        ph = al.elastic_phase_boxplot(r["gammas"], T)
        for key in ("distances", "q1", "q3", "upper_whisker_srsf"):
            np.testing.assert_array_equal(amp[key], r["amplitude"][key])
        for key in ("distances", "median", "shooting_vectors"):
            np.testing.assert_array_equal(ph[key], r["phase"][key])
        cls_a = amp["model"].classify_srsfs(r["aligned_srsfs"], T)
        cls_p = ph["model"].classify_warps(r["gammas"], T)
        np.testing.assert_allclose(cls_a["distances"], amp["distances"], atol=1e-12)
        np.testing.assert_allclose(cls_p["distances"], ph["distances"], atol=1e-10)
        assert cls_a["regions"].dtype == np.int8
        assert cls_a["regions"][14] == 4 and cls_p["regions"][15] == 4
        assert set(cls_a["sides"]) <= {"q1", "q3"}
        # regions are ordered by distance against the fitted radii
        lv = cls_a["regions"]
        d = cls_a["distances"]
        assert np.all(d[lv == 1] <= amp["r50"] + 1e-12)
        assert np.all(d[lv == 4] > amp["whisker_distance"] - 1e-12)

    def test_classify_new_curves(self, boxplot_data):
        r = al.elastic_boxplots(boxplot_data[:14], T, alpha=0.1, k_a=0.5)
        model = r["model"]
        assert isinstance(model, al.PyElasticBoxplots)
        assert model.lambda_ == 0.0
        new = np.vstack([two_bump(T), 4.0 * two_bump(T)])
        c = model.classify(new, T)
        assert c["gammas"].shape == (2, M)
        assert c["amplitude"]["regions"][0] in (1, 2)
        assert c["amplitude"]["regions"][1] == 4

    def test_value_errors(self, boxplot_data):
        with pytest.raises(ValueError, match="alpha"):
            al.elastic_boxplots(boxplot_data, T, alpha=1.5)
        with pytest.raises(ValueError, match="k_a"):
            al.elastic_phase_boxplot(np.tile(T, (5, 1)), T, k_a=0.0)
        bp = al.elastic_phase_boxplot(np.tile(T, (5, 1)), T)
        with pytest.raises(ValueError):
            bp["model"].classify_warps(np.tile(T[:-1], (2, 1)), T[:-1])


# ---------------------------------------------------------------------------
# Elastic DP-means
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def two_shapes():
    rng = np.random.default_rng(2)
    a = [bump(exp_warp(rng.normal(0, 0.3)), 0.5, 0.02) for _ in range(5)]
    b = [two_bump(exp_warp(rng.normal(0, 0.3))) * 0.8 for _ in range(5)]
    return np.array(a + b)


class TestDpMeans:

    def test_penalty_between_scales_recovers_two_clusters(self, two_shapes):
        # within-shape elastic distances are < 0.2, between-shape ones > 0.25
        r = al.elastic_dpmeans(two_shapes, T, penalty=0.5)
        assert r["k"] == 2
        lab = r["labels"]
        assert len(set(lab[:5])) == 1 and len(set(lab[5:])) == 1 and lab[0] != lab[5]
        assert r["templates"].shape == (2, M)
        assert r["gammas"].shape == (10, M)
        assert r["penalty"] == 0.5
        assert len(r["objective"]) == r["n_iter"]
        auto = al.elastic_dpmeans(two_shapes, T)
        assert auto["penalty"] > 0.0 and auto["k"] >= 2

    def test_cluster_count_responds_to_penalty(self, two_shapes):
        ks = [al.elastic_dpmeans(two_shapes, T, penalty=p)["k"] for p in (1e-3, 1.0, 1e3)]
        assert ks[0] > ks[1] >= ks[2]
        assert ks[2] == 1
        assert ks[0] >= 5

    def test_no_alignment_variant(self, two_shapes):
        r = al.elastic_dpmeans(two_shapes, T, align=False, penalty=1e3)
        np.testing.assert_allclose(r["gammas"], np.tile(T, (10, 1)))

    def test_value_errors(self, two_shapes):
        with pytest.raises(ValueError):
            al.elastic_dpmeans(two_shapes, T[:-1])
        with pytest.raises(ValueError):
            al.elastic_dpmeans(two_shapes, T, penalty=-1.0)


# ---------------------------------------------------------------------------
# Bayesian group alignment
# ---------------------------------------------------------------------------

BAYES_SHIFTS = np.array([-0.06, 0.0, 0.06])
BAYES_KW = dict(n_iter=200, burn_in=100, n_warp_harmonics=3, n_template_basis=12)
M_B = 31
T_B = np.linspace(0.0, 1.0, M_B)


@pytest.fixture(scope="module")
def bayes_data():
    return shifted_bumps(BAYES_SHIFTS, m=M_B)


@pytest.fixture(scope="module")
def bayes_default(bayes_data):
    return al.bayesian_align_group(bayes_data, T_B, **BAYES_KW)


class TestBayesianGroup:
    def test_warps_monotone_and_ordered_like_planted_shifts(self, bayes_data, bayes_default):
        r = bayes_default
        g = r["gammas"]
        assert g.shape == (3, M_B)
        np.testing.assert_allclose(g[:, 0], 0.0, atol=1e-12)
        np.testing.assert_allclose(g[:, -1], 1.0, atol=1e-12)
        assert np.all(np.diff(g, axis=1) >= -1e-12)
        # f_i(t) = b(t - s_i) aligns by f_i(gamma_i(t)) = b(t) up to a common
        # warp, so gamma_i(t) - t is about s_i (centred) in the middle
        mid = slice(10, 21)
        disp = (g[:, mid] - T_B[mid]).mean(axis=1)
        assert np.all(np.diff(disp) > 0)
        np.testing.assert_allclose(disp - disp.mean(), BAYES_SHIFTS - BAYES_SHIFTS.mean(), atol=0.03)
        spread_raw = bayes_data.std(axis=0).max()
        spread_al = r["aligned_data"].std(axis=0).max()
        assert spread_al < 0.5 * spread_raw
        assert np.all(r["gammas_lower"] <= r["gammas_upper"] + 1e-12)
        assert np.all(r["template_lower"] <= r["template_upper"] + 1e-12)
        assert r["sigma2_lower"] <= r["sigma2_mean"] <= r["sigma2_upper"]

    def test_draws_shapes_and_chain_summaries(self, bayes_default):
        r = bayes_default
        n_draws = 100
        assert r["gamma_draws"].shape == (3, n_draws, M_B)
        assert r["template_srsf_draws"].shape == (n_draws, M_B)
        assert r["sigma2_draws"].shape == (n_draws,)
        assert len(r["chains"]) == 1
        ch = r["chains"][0]
        assert ch["seed"] == 42
        assert ch["sigma2_trace"].shape == (n_draws,)
        assert ch["swap_acceptance"].shape == (0,)
        assert ch["warp_step_sizes"].shape == (0,)
        assert r["multimodal_curves"].dtype == bool
        assert np.all((r["warp_acceptance"] >= 0) & (r["warp_acceptance"] <= 1))

    def test_one_temperature_is_bit_identical_to_default(self, bayes_data, bayes_default):
        r = al.bayesian_align_group(bayes_data, T_B, n_temperatures=1, pt_min_inv_temp=0.3, **BAYES_KW)
        for key in ("gammas", "template_srsf", "sigma2_draws", "gamma_draws"):
            np.testing.assert_array_equal(r[key], bayes_default[key])

    def test_tempering_swap_acceptance_shape(self, bayes_data):
        r = al.bayesian_align_group(
            bayes_data, T_B, n_temperatures=3, n_chains=2, return_draws=False, **BAYES_KW
        )
        assert len(r["chains"]) == 2
        assert [c["seed"] for c in r["chains"]] == [42, 43]
        for c in r["chains"]:
            sa = c["swap_acceptance"]
            assert sa.shape == (2,)
            assert np.all((sa >= 0) & (sa <= 1))
        assert r["gamma_draws"] is None and r["sigma2_draws"] is None
        assert np.isfinite(r["rhat_sigma2"])
        assert r["mode_spread"].shape == (3,)

    def test_infhmc_sampler(self, bayes_data):
        r = al.bayesian_align_group(bayes_data, T_B, sampler="infhmc", return_draws=False, **BAYES_KW)
        assert r["chains"][0]["warp_step_sizes"].shape == (3,)
        assert np.all(np.diff(r["gammas"], axis=1) >= -1e-12)

    def test_value_errors(self, bayes_data):
        with pytest.raises(ValueError, match="sampler"):
            al.bayesian_align_group(bayes_data, T_B, sampler="nuts", **BAYES_KW)
        with pytest.raises(ValueError, match="burn_in"):
            al.bayesian_align_group(bayes_data, T_B, n_iter=50, burn_in=50)
        with pytest.raises(ValueError):
            al.bayesian_align_group(bayes_data, T_B, pcn_betas=[0.5, 2.0], pcn_probs=[0.5, 0.5], **BAYES_KW)


# ---------------------------------------------------------------------------
# Exponential-family registration and GFPCA
# ---------------------------------------------------------------------------

M_E = 50
T_E = np.linspace(0.0, 1.0, M_E)


def irreg(rows, t=T_E):
    return pace_fpca.irreg_fdata_from_lists([t.copy() for _ in rows], [np.asarray(r, float) for r in rows])


def mid_displacement(t_hat, t=T_E):
    mid = (t > 0.3) & (t < 0.7)
    return np.array([(np.asarray(th)[mid] - t[mid]).mean() for th in t_hat])


class TestExpFamRegistration:
    def test_poisson_counts_recover_planted_shifts(self):
        rng = np.random.default_rng(11)
        shifts = np.linspace(-0.1, 0.1, 12)
        rows = [rng.poisson(np.exp(0.5 + 2.5 * bump(T_E, 0.5 + s, 0.015))) for s in shifts]
        data = irreg(rows)
        r = al.register_expfam(data, family="poisson")
        disp = mid_displacement(r["t_hat"])
        # Y_i(t) = theta(t - s_i) registers by h_i^{-1}(t) ~ t - s_i (centred)
        assert np.corrcoef(disp, shifts)[0, 1] < -0.9
        for th in r["t_hat"]:
            assert th[0] == pytest.approx(0.0, abs=1e-12) and th[-1] == pytest.approx(1.0, abs=1e-12)
            assert np.all(np.diff(th) >= 0.0)
        assert r["converged"].dtype == bool and len(r["curve_loss"]) == 12
        assert r["gamma_scales"] is None
        assert r["loss"] == pytest.approx(r["curve_loss"].sum())

    def test_bernoulli_register_fpca_recovers_planted_shifts(self):
        rng = np.random.default_rng(4)
        shifts = np.repeat(np.linspace(-0.1, 0.1, 6), 3)
        t = np.linspace(0.0, 1.0, 120)
        p = [1.0 / (1.0 + np.exp(-(-2.0 + 5.0 * bump(t, 0.5 + s, 0.015)))) for s in shifts]
        rows = [rng.binomial(1, pi).astype(float) for pi in p]
        r = al.register_fpca(irreg(rows, t), family="binomial", max_iterations=2)
        disp = mid_displacement(r["registration"]["t_hat"], t)
        assert np.corrcoef(disp, shifts)[0, 1] < -0.7
        assert r["fpca"]["em_family"] == "binomial"
        assert r["fpca"]["fpca_type"] == "variational_em"
        assert 1 <= r["iterations"] <= 2
        assert len(r["registration_loss"]) == r["iterations"] + 1

    def test_registered_data_and_inverse_warp_parity(self):
        data_rows = shifted_bumps(np.linspace(-0.08, 0.08, 8), m=M_E)
        r = al.register_expfam(irreg(data_rows))
        handle = r["registered_data"]
        assert isinstance(handle, pace_fpca.PyIrregFdata)
        for i in range(8):
            np.testing.assert_array_equal(r["registered_argvals"][i], r["t_hat"][i])
            np.testing.assert_array_equal(r["registered_values"][i], data_rows[i])
            h = al.evaluate_inverse_warp(r["hinv_beta"][i], r["hinv_inner_knots"][i], 0.0, 1.0, T_E)
            np.testing.assert_allclose(h, r["t_hat"][i], atol=1e-10)

    def test_regular_matches_irregular(self):
        data_rows = shifted_bumps(np.linspace(-0.06, 0.06, 6), m=M_E)
        a = al.register_fpca_regular(data_rows, T_E, max_iterations=2)
        b = al.register_fpca(irreg(data_rows), max_iterations=2)
        for x, y in zip(a["registration"]["t_hat"], b["registration"]["t_hat"]):
            np.testing.assert_array_equal(x, y)
        np.testing.assert_array_equal(a["fpca"]["mean"], b["fpca"]["mean"])
        assert a["fpca"]["efunctions"].shape == (100, 1)
        assert isinstance(a["registered_data"], pace_fpca.PyIrregFdata)

    def test_gfpca_recovers_dominant_component(self):
        rng = np.random.default_rng(8)
        t = np.linspace(0.0, 1.0, 25)
        a = rng.normal(0.0, 1.0, 14)
        rows = [np.sin(2 * np.pi * t) + ai * t + 0.01 * rng.normal(size=t.size) for ai in a]
        v = al.gfpca_variational(irreg(rows, t), npc=1)
        assert v["efunctions"].shape == (100, 1) and v["scores"].shape == (14, 1)
        assert v["sigma2"] < 0.01
        assert abs(np.corrcoef(v["scores"][:, 0], a)[0, 1]) > 0.95
        assert v["yhat"] is None and len(v["fitted"]) == 14
        s = al.gfpca_two_step(irreg(rows, t), npc=2)
        assert s["fpca_type"] == "two_step"
        assert s["evalues"][0] >= s["evalues"][1]
        assert s["yhat"].shape == (14, len(s["t_vec"]))
        assert s["variance_components"] is not None
        assert abs(np.corrcoef(s["scores"][:, 0], a)[0, 1]) > 0.95
        assert isinstance(s["domain"], tuple) and s["domain"] == (0.0, 1.0)

    def test_value_errors(self):
        data = irreg(shifted_bumps([0.0, 0.02, 0.04, 0.06], m=M_E))
        with pytest.raises(ValueError, match="family"):
            al.register_expfam(data, family="beta")
        with pytest.raises(ValueError, match="incompleteness"):
            al.register_fpca(data, incompleteness="middle")
        with pytest.raises(ValueError, match="fpca_type"):
            al.register_fpca(data, fpca_type="pace")
        with pytest.raises(ValueError, match="warping"):
            al.register_expfam(data, warping="spline")
        with pytest.raises(ValueError, match="npc_var_explained"):
            al.gfpca_variational(data, npc_min_component_share=0.1)
        with pytest.raises(ValueError, match="kh"):
            al.register_expfam(data, kh=3)
        with pytest.raises(ValueError):
            al.register_expfam(irreg([np.full(M_E, 2.0)] * 4), family="binomial")
        with pytest.raises(ValueError, match="beta"):
            al.evaluate_inverse_warp(np.zeros(3), np.array([0.5]), 0.0, 1.0, T_E)


# ---------------------------------------------------------------------------
# Partial-curve conformal prediction
# ---------------------------------------------------------------------------


def conformal_curves(n, seed, m=M):
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, m)
    return np.array(
        [
            (0.8 + 0.4 * rng.random()) * bump(t, 0.5 + 0.08 * (rng.random() - 0.5), 0.02)
            for _ in range(n)
        ]
    )


def target_amplitude(model, curve):
    return al.elastic_align_pair(model.template, curve, model.argvals)["f_aligned"]


@pytest.fixture(scope="module")
def fitted():
    data = conformal_curves(30, 0)
    return data, conformal.partial_conformal_fit(data, T, alpha=0.2)


class TestPartialConformal:

    def test_model_handle(self, fitted):
        data, model = fitted
        assert isinstance(model, conformal.PyPartialConformalModel)
        tr, cal = model.training_indices, model.calibration_indices
        assert len(tr) + len(cal) == 30 and not set(tr) & set(cal)
        np.testing.assert_array_equal(model.calibration_data, data[cal])
        assert model.calibration_gammas.shape == (15, M)
        assert model.training_sd.shape == (M,)
        assert model.tuning_data.shape == (0, M)
        assert model.alpha == 0.2 and model.band == "pointwise"

    def test_full_observation_target_matches_elastic_align_pair(self, fitted):
        data, model = fitted
        curve = conformal_curves(1, 99)[0]
        p = conformal.partial_conformal_predict(model, curve)
        assert p["n_observed"] == M
        np.testing.assert_allclose(p["full_registration"]["f_aligned"], target_amplitude(model, curve), atol=1e-12)
        assert p["prediction"].phase_set_contains(p["phase_center"])
        assert np.all(p["amplitude_lower"] <= p["amplitude_center"] + 1e-12)
        assert np.all(p["amplitude_center"] <= p["amplitude_upper"] + 1e-12)
        assert p["weights"].shape == (15,) and p["weights"].sum() == pytest.approx(1.0)
        assert p["amplitude_radius"] is None and p["band"] == "pointwise"

    def test_coverage_near_nominal_over_seeds(self):
        alpha = 0.2
        hits_pw, hits_sim, hits_phase = [], [], []
        for seed in range(4):
            data = conformal_curves(40, seed)
            fit, test = data[:30], data[30:]
            pw = conformal.partial_conformal_fit(fit, T, alpha=alpha, seed=seed)
            sim = conformal.partial_conformal_fit(fit, T, alpha=alpha, seed=seed, band="simultaneous")
            for curve in test:
                y = target_amplitude(pw, curve)
                a = conformal.partial_conformal_predict(pw, curve[:15])
                b = conformal.partial_conformal_predict(sim, curve[:15])
                hits_pw.append(np.mean((y >= a["amplitude_lower"] - 1e-9) & (y <= a["amplitude_upper"] + 1e-9)))
                hits_sim.append(np.all((y >= b["amplitude_lower"] - 1e-9) & (y <= b["amplitude_upper"] + 1e-9)))
                g = al.elastic_align_pair(pw.template, curve, T)["gamma"]
                hits_phase.append(a["prediction"].phase_set_contains(g))
        assert np.mean(hits_pw) >= 1 - alpha - 0.1
        assert np.mean(hits_sim) >= 1 - alpha - 0.15
        assert np.mean(hits_phase) >= 1 - alpha - 0.15

    def test_simultaneous_band_contains_pointwise_band(self):
        data = conformal_curves(30, 3)
        pw = conformal.partial_conformal_fit(data, T, alpha=0.2)
        sim = conformal.partial_conformal_fit(data, T, alpha=0.2, band="simultaneous")
        assert sim.band == "simultaneous"
        for curve in conformal_curves(3, 50):
            a = conformal.partial_conformal_predict(pw, curve[:12])
            b = conformal.partial_conformal_predict(sim, curve[:12])
            np.testing.assert_allclose(a["amplitude_center"], b["amplitude_center"])
            assert np.all(b["amplitude_lower"] <= a["amplitude_lower"] + 1e-9)
            assert np.all(b["amplitude_upper"] >= a["amplitude_upper"] - 1e-9)
            r = b["amplitude_radius"]
            np.testing.assert_allclose(b["amplitude_upper"] - b["amplitude_center"], r, atol=1e-9)

    def test_alpha_override_and_training_sd_scale(self, fitted):
        data, model = fitted
        curve = conformal_curves(1, 7)[0][:15]
        wide = conformal.partial_conformal_predict(model, curve, alpha=0.1)
        narrow = conformal.partial_conformal_predict(model, curve, alpha=0.4)
        assert wide["alpha"] == 0.1 and narrow["alpha"] == 0.4
        assert np.all(wide["amplitude_upper"] - wide["amplitude_lower"] >= narrow["amplitude_upper"] - narrow["amplitude_lower"] - 1e-9)
        sd = conformal.partial_conformal_fit(data, T, alpha=0.2, band="simultaneous", band_scale="training_sd")
        p = conformal.partial_conformal_predict(sd, curve)
        half = (p["amplitude_upper"] - p["amplitude_lower"]) / 2
        scale = half / p["amplitude_radius"]
        assert np.ptp(scale) > 0  # modulated, not constant width
        custom = conformal.partial_conformal_fit(data, T, alpha=0.2, band="simultaneous", band_scale=np.ones(M))
        c = conformal.partial_conformal_fit(data, T, alpha=0.2, band="simultaneous")
        np.testing.assert_allclose(
            conformal.partial_conformal_predict(custom, curve)["amplitude_upper"],
            conformal.partial_conformal_predict(c, curve)["amplitude_upper"],
        )

    def test_observation_patterns_consistent(self, fitted):
        _, model = fitted
        curve = conformal_curves(1, 21)[0]
        a = conformal.partial_conformal_predict(model, curve[:14])
        b = conformal.partial_conformal_predict_observed(model, curve[:14])
        with pytest.raises(ValueError):
            conformal.partial_conformal_predict_observed(model, curve, n_observed=14)
        for key in ("amplitude_lower", "amplitude_upper", "phase_center", "weights"):
            np.testing.assert_array_equal(a[key], b[key])
        frags = np.array([[2, 8], [15, 22]])
        vals = np.concatenate([curve[2:9], curve[15:23]])
        f = conformal.partial_conformal_predict_observed(model, vals, observation="fragments", fragments=frags)
        assert len(f["fragment_registrations"]) == 2
        assert f["amplitude_lower"].shape == (M,)
        times = np.array([0.13, 0.42, 0.55, 0.77])
        s = conformal.partial_conformal_predict_observed(
            model, np.interp(times, T, curve), observation="sparse", times=times
        )
        assert s["n_observed"] == 4
        assert np.all(s["amplitude_lower"] <= s["amplitude_upper"])

    def test_bandwidth_tuning(self):
        data = conformal_curves(40, 5)
        tuned = conformal.partial_conformal_fit(data, T, alpha=0.25, tuning_fraction=0.4)
        assert len(tuned.tuning_indices) > 0
        assert tuned.tuning_data.shape[0] == len(tuned.tuning_indices)
        p = conformal.partial_conformal_predict(tuned, data[0][:15])
        sel = p["bandwidth_selection"]
        assert sel is not None and sel["bandwidth"] == p["bandwidth"]
        assert sel["bandwidth"] in sel["candidates"]
        tm = conformal.partial_conformal_fit_with_template(
            data[:12], T, bump(T), alpha=0.25, bandwidth_candidates=[0.05, 0.1, 0.3]
        )
        assert tm.training_indices.shape == (0,) and tm.training_sd is None
        s = conformal.partial_conformal_select_bandwidth(tm, n_observed=10)
        np.testing.assert_array_equal(s["candidates"], [0.05, 0.1, 0.3])
        assert s["bandwidth"] == s["candidates"][np.argmin(s["mean_width"])]
        assert s["n_tuning"] == 12

    def test_value_errors(self, fitted):
        data, model = fitted
        with pytest.raises(ValueError, match="band"):
            conformal.partial_conformal_fit(data, T, band="uniform")
        with pytest.raises(ValueError, match="distance"):
            conformal.partial_conformal_fit(data, T, distance="dtw")
        with pytest.raises(ValueError, match="band_scale"):
            conformal.partial_conformal_fit(data, T, band_scale="huge")
        with pytest.raises(ValueError, match="fragments"):
            conformal.partial_conformal_predict_observed(model, data[0][:5], observation="fragments")
        with pytest.raises(ValueError, match="observation"):
            conformal.partial_conformal_predict_observed(model, data[0][:5], observation="dense")
        with pytest.raises(ValueError, match="n_observed"):
            conformal.partial_conformal_select_bandwidth(model)
        with pytest.raises(ValueError):
            conformal.partial_conformal_predict(model, data[0][:10], alpha=0.01)
        with pytest.raises(ValueError):
            conformal.partial_conformal_predict(model, data[0][:1])


# ---------------------------------------------------------------------------
# Elastic conformal anomaly detection
# ---------------------------------------------------------------------------


class TestElasticConformalAnomaly:
    def test_nonconformity_variants(self):
        f = two_bump(T)
        assert tolerance.elastic_nonconformity(f, f, T) == pytest.approx(0.0, abs=1e-8)
        scaled = 1.5 * f
        assert tolerance.elastic_nonconformity(scaled, f, T, variant="amplitude") > 0.1
        assert tolerance.elastic_nonconformity(scaled, f, T, variant="phase") < 0.05
        warped = two_bump(exp_warp(2.0))
        ph = tolerance.elastic_nonconformity(warped, f, T, variant="phase")
        amp = tolerance.elastic_nonconformity(warped, f, T, variant="amplitude")
        comb = tolerance.elastic_nonconformity(warped, f, T, variant="combined")
        assert ph > 0.2
        assert comb == pytest.approx(np.hypot(amp, ph), rel=1e-12)

    def test_p_values_match_definition_and_flags_outliers(self):
        rng = np.random.default_rng(1)
        cal = np.array([(1 + rng.normal(0, 0.05)) * two_bump(exp_warp(rng.normal(0, 0.3))) for _ in range(19)])
        test = np.vstack([two_bump(T), 2.0 * two_bump(T), two_bump(exp_warp(4.0))])
        tmpl = two_bump(T)
        r = tolerance.elastic_conformal_anomaly(cal, test, T, alpha=0.1, template=tmpl)
        cal_scores = np.array([tolerance.elastic_nonconformity(c, tmpl, T) for c in cal])
        np.testing.assert_allclose(
            r["scores"], [tolerance.elastic_nonconformity(c, tmpl, T) for c in test], rtol=1e-12
        )
        expected_p = [(1 + np.sum(cal_scores >= s)) / 20.0 for s in r["scores"]]
        np.testing.assert_allclose(r["p_values"], expected_p)
        np.testing.assert_array_equal(r["flags"], [False, True, True])
        assert r["flags"].dtype == bool
        amp = tolerance.elastic_conformal_anomaly(cal, test, T, variant="amplitude", template=tmpl)
        ph = tolerance.elastic_conformal_anomaly(cal, test, T, variant="phase", template=tmpl)
        np.testing.assert_array_equal(amp["flags"], [False, True, False])
        np.testing.assert_array_equal(ph["flags"], [False, False, True])
        km = tolerance.elastic_conformal_anomaly(cal, test, T)
        assert km["flags"][1] and km["threshold"] > 0.0

    def test_value_errors(self):
        f = np.tile(two_bump(T), (3, 1))
        with pytest.raises(ValueError, match="variant"):
            tolerance.elastic_nonconformity(f[0], f[0], T, variant="l2")
        with pytest.raises(ValueError, match="length"):
            tolerance.elastic_nonconformity(f[0][:-1], f[0], T)
        with pytest.raises(ValueError, match="alpha"):
            tolerance.elastic_conformal_anomaly(f, f, T, alpha=1.0)
        with pytest.raises(ValueError, match="template"):
            tolerance.elastic_conformal_anomaly(f, f, T, template=np.ones(5))
        with pytest.raises(ValueError, match="variant"):
            tolerance.elastic_conformal_anomaly(f, f, T, variant="sup")
