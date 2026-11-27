"""Localised group-difference testing of fdars-core 0.48.1 (sipemu/fdars#76):
``alignment.elastic_local_difference_test``, ``inference.scb_two_sample_band``,
``inference.itp_pointwise_pvalues`` and ``inference.itp_two_pop_regions``.
"""

import numpy as np
import pytest

from fdars import alignment as A
from fdars import inference as I

T = np.linspace(0.0, 1.0, 60)
REGION_KEYS = {"start_idx", "end_idx", "t_start", "t_end", "direction", "min_adjusted_pvalue"}


def _groups(seed, n=15, h_a=1.0, d_a=0.0, d_b=0.0):
    """Two bumps at 0.3 and 0.7 with a common random shift; group A (label 0)
    gets height ``h_a`` and offset ``d_a`` on the second bump, group B offset
    ``d_b``."""
    rng = np.random.default_rng(seed)
    X, labels = [], []
    for g, (h, d) in enumerate([(h_a, d_a), (1.0, d_b)]):
        for _ in range(n):
            s = 0.02 * rng.normal()
            f = np.exp(-(((T - 0.3 - s) / 0.1) ** 2)) * (1 + 0.05 * rng.normal())
            f = f + h * (1 + 0.05 * rng.normal()) * np.exp(-(((T - 0.7 - d - s) / 0.1) ** 2))
            X.append(f + 0.01 * rng.normal(size=T.size))
            labels.append(g)
    return np.array(X), np.array(labels)


def _ldt(X, labels, **kw):
    kw.setdefault("n_perm", 199)
    kw.setdefault("scb_nb", 199)
    kw.setdefault("max_iter", 5)
    return A.elastic_local_difference_test(X, T, labels, **kw)


def _covers(region, t):
    return region["t_start"] <= t <= region["t_end"]


# ---------------------------------------------------------------------------
# elastic_local_difference_test
# ---------------------------------------------------------------------------


def test_local_difference_result_structure():
    X, labels = _groups(1, h_a=1.5)
    r = _ldt(X, labels)
    assert set(r) == {"amplitude", "phase", "phase_data", "alignment", "group_labels", "group_sizes"}
    np.testing.assert_array_equal(r["group_labels"], [0, 1])
    np.testing.assert_array_equal(r["group_sizes"], [15, 15])
    for part in ("amplitude", "phase"):
        p = r[part]
        assert set(p) == {"regions", "effect", "pointwise_adjusted_pvalues", "itp", "lower", "upper"}
        assert p["effect"].shape == p["pointwise_adjusted_pvalues"].shape == (60,)
        assert p["lower"] is None and p["upper"] is None
        assert p["itp"]["basis_type"] == "bspline" and p["itp"]["n_perm"] == 199
    al = r["alignment"]
    assert al["gammas"].shape == al["aligned_data"].shape == X.shape
    # displacement phase quantity is gamma(t) - t
    np.testing.assert_allclose(r["phase_data"], al["gammas"] - T, atol=1e-12)
    # amplitude effect is the raw mean difference A - B of the aligned curves
    aligned = al["aligned_data"]
    np.testing.assert_allclose(
        r["amplitude"]["effect"], aligned[labels == 0].mean(0) - aligned[labels == 1].mean(0), atol=1e-10
    )


@pytest.mark.parametrize("h_a, direction", [(1.5, "positive"), (0.6, "negative")])
def test_local_difference_finds_planted_amplitude_difference(h_a, direction):
    X, labels = _groups(1, h_a=h_a)
    r = _ldt(X, labels)
    regions = r["amplitude"]["regions"]
    assert regions, "planted amplitude difference not found"
    for reg in regions:
        assert set(reg) == REGION_KEYS
        assert reg["direction"] == direction
        assert 0.5 <= reg["t_start"] <= reg["t_end"] <= 0.95
        assert reg["min_adjusted_pvalue"] < 0.05
        pw = r["amplitude"]["pointwise_adjusted_pvalues"][reg["start_idx"] : reg["end_idx"] + 1]
        assert reg["min_adjusted_pvalue"] == pytest.approx(pw.min())
        assert reg["t_start"] == T[reg["start_idx"]] and reg["t_end"] == T[reg["end_idx"]]
    assert any(_covers(reg, 0.7) for reg in regions)
    assert r["phase"]["regions"] == []


@pytest.mark.parametrize(
    "d_a, d_b, direction, timing",
    [(0.04, -0.04, "positive", "a_later"), (-0.04, 0.04, "negative", "a_earlier")],
)
def test_local_difference_flags_timing_as_phase(d_a, d_b, direction, timing):
    """A's second bump later than B's -> displacement gamma_A - t > gamma_B - t
    -> phase region ``positive`` with timing ``a_later`` (and vice versa)."""
    X, labels = _groups(1, d_a=d_a, d_b=d_b)
    r = _ldt(X, labels)
    regions = r["phase"]["regions"]
    assert len(regions) == 1
    reg = regions[0]
    assert set(reg) == REGION_KEYS | {"timing"}
    assert reg["direction"] == direction and reg["timing"] == timing
    assert _covers(reg, 0.7) and reg["t_start"] >= 0.45
    assert r["amplitude"]["regions"] == []


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_local_difference_no_regions_under_h0(seed):
    X, labels = _groups(seed)
    r = _ldt(X, labels)
    assert r["amplitude"]["regions"] == [] and r["phase"]["regions"] == []
    assert np.all(r["amplitude"]["pointwise_adjusted_pvalues"] >= 0.05)


def test_local_difference_scb():
    X, labels = _groups(1, h_a=1.5)
    r = _ldt(X, labels, test="scb")
    amp = r["amplitude"]
    assert amp["itp"] is None and amp["pointwise_adjusted_pvalues"] is None
    assert np.all(amp["lower"] <= amp["effect"]) and np.all(amp["effect"] <= amp["upper"])
    assert amp["regions"] and all(reg["direction"] == "positive" for reg in amp["regions"])
    assert all(reg["min_adjusted_pvalue"] is None for reg in amp["regions"])
    assert any(_covers(reg, 0.7) for reg in amp["regions"])
    assert r["phase"]["regions"] == []
    # null: no regions
    X0, labels0 = _groups(1)
    r0 = _ldt(X0, labels0, test="scb")
    assert r0["amplitude"]["regions"] == [] and r0["phase"]["regions"] == []


def test_local_difference_psi_and_labels():
    X, labels = _groups(1, d_a=0.04, d_b=-0.04)
    r = _ldt(X, labels * 3 + 2, phase_representation="psi")
    np.testing.assert_array_equal(r["group_labels"], [2, 5])
    assert np.all(r["phase_data"] >= 0)
    assert all("timing" not in reg for reg in r["phase"]["regions"])
    # deterministic for fixed seeds
    r2 = _ldt(X, labels * 3 + 2, phase_representation="psi")
    np.testing.assert_array_equal(r["phase"]["pointwise_adjusted_pvalues"], r2["phase"]["pointwise_adjusted_pvalues"])


@pytest.mark.parametrize(
    "kw",
    [
        {"test": "anova"},
        {"phase_representation": "warp"},
        {"mapping": "nearest"},
        {"multiplier": "uniform"},
        {"method": "newton"},
        {"alpha": 0.0},
        {"alpha": 1.0},
        {"max_iter": 0},
        {"test": "scb", "scb_bandwidth": -0.1},
    ],
)
def test_local_difference_value_errors(kw):
    X, labels = _groups(1)
    with pytest.raises(ValueError):
        _ldt(X, labels, **kw)


def test_local_difference_label_errors():
    X, labels = _groups(1, n=4)
    with pytest.raises(ValueError):
        _ldt(X, np.zeros(8, dtype=int))  # one label
    with pytest.raises(ValueError):
        _ldt(X, np.arange(8) % 3)  # three labels
    with pytest.raises(ValueError):
        _ldt(X, labels[:-1])  # length mismatch
    with pytest.raises(ValueError):
        _ldt(X, -labels)  # negative label
    with pytest.raises(ValueError):
        _ldt(X, np.r_[0, 0, 1, 1, 1, 1, 1, 1], test="scb")  # 2 < 3 curves for SCB
    bad = X.copy()
    bad[0, 3] = np.nan
    with pytest.raises(ValueError):
        _ldt(bad, labels)


# ---------------------------------------------------------------------------
# inference.scb_two_sample_band
# ---------------------------------------------------------------------------


def _shifted_samples(seed, n=25, effect=1.0):
    """Two samples with iid noise; ``a`` is raised by ``effect`` on [0.6, 1]
    (logistic step).  The ITP has little power for narrow differences (the
    interval-wise closure takes the maximum over every interval containing a
    component), hence a broad step."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, 50)
    diff = effect / (1 + np.exp(-(t - 0.6) / 0.03))

    def sample():
        return np.sin(np.pi * t) + 0.3 * rng.normal(size=(n, t.size))

    return sample() + diff, sample(), t, diff


def test_scb_two_sample_band_contains_true_difference():
    a, b, t, diff = _shifted_samples(3)
    r = I.scb_two_sample_band(a, b, t, 0.05, nb=500)
    assert set(r) == {
        "estimate", "lower", "upper", "half_width", "critical_value",
        "confidence", "statistic", "rejected", "regions",
    }  # fmt: skip
    np.testing.assert_allclose(r["upper"] - r["lower"], 2 * r["half_width"], atol=1e-12)
    np.testing.assert_allclose(r["estimate"], (r["lower"] + r["upper"]) / 2, atol=1e-12)
    assert np.all((r["lower"] <= diff) & (diff <= r["upper"]))
    assert r["rejected"] and r["confidence"] == 0.95 and r["critical_value"] > 0
    assert len(r["regions"]) == 1
    reg = r["regions"][0]
    assert reg["direction"] == "positive" and reg["min_adjusted_pvalue"] is None
    assert _covers(reg, 0.75) and 0.5 <= reg["t_start"]
    excl = (r["lower"] > 0) | (r["upper"] < 0)
    assert excl[reg["start_idx"] : reg["end_idx"] + 1].all() and excl.sum() == reg["end_idx"] - reg["start_idx"] + 1
    # identical decision and statistic to scb_two_sample_test
    test = I.scb_two_sample_test(a, b, t, 0.05, nb=500)
    assert test["statistic"] == pytest.approx(r["statistic"], rel=1e-12)
    assert (test["p_value"] == 0.0) == r["rejected"]
    # swapping the groups flips the direction
    rs = I.scb_two_sample_band(b, a, t, 0.05, nb=500)
    assert [x["direction"] for x in rs["regions"]] == ["negative"]


def test_scb_two_sample_band_null_and_errors():
    a, b, t, _ = _shifted_samples(4, effect=0.0)
    r = I.scb_two_sample_band(a, b, t, 0.05, nb=500)
    assert not r["rejected"] and r["regions"] == []
    with pytest.raises(ValueError):
        I.scb_two_sample_band(a, b, t, 0.05, multiplier="uniform")
    with pytest.raises(ValueError):
        I.scb_two_sample_band(a, b[:, :-1], t, 0.05)
    with pytest.raises(ValueError):
        I.scb_two_sample_band(a, b, t, 0.05, confidence=1.0)
    with pytest.raises(ValueError):
        I.scb_two_sample_band(a, b, t, 0.05, nb=0)


# ---------------------------------------------------------------------------
# inference.itp_two_pop_regions / itp_pointwise_pvalues
# ---------------------------------------------------------------------------


def test_itp_two_pop_regions_localises_difference():
    a, b, t, _ = _shifted_samples(3)
    r = I.itp_two_pop_regions(a, b, t, n_perm=499)
    assert set(r) == {"itp", "pointwise_adjusted_pvalues", "mean_difference", "regions"}
    np.testing.assert_allclose(r["mean_difference"], a.mean(0) - b.mean(0), atol=1e-12)
    assert r["itp"]["n_basis"] == 15 and r["itp"]["n_perm"] == 499
    assert r["regions"]
    for reg in r["regions"]:
        assert set(reg) == REGION_KEYS
        assert reg["direction"] == "positive" and 0.55 <= reg["t_start"]
        assert reg["min_adjusted_pvalue"] < 0.05
    assert any(_covers(reg, 0.75) for reg in r["regions"])
    pw = r["pointwise_adjusted_pvalues"]
    flagged = np.zeros(t.size, bool)
    for reg in r["regions"]:
        flagged[reg["start_idx"] : reg["end_idx"] + 1] = True
    np.testing.assert_array_equal(flagged, pw < 0.05)
    # a stricter alpha only shrinks the regions
    strict = I.itp_two_pop_regions(a, b, t, n_perm=499, alpha=0.01)
    np.testing.assert_array_equal(strict["pointwise_adjusted_pvalues"], pw)
    assert sum(x["end_idx"] - x["start_idx"] + 1 for x in strict["regions"]) <= flagged.sum()


def test_itp_two_pop_regions_null():
    a, b, t, _ = _shifted_samples(4, effect=0.0)
    r = I.itp_two_pop_regions(a, b, t, n_perm=499)
    assert r["regions"] == [] and np.all(r["pointwise_adjusted_pvalues"] >= 0.05)


def test_itp_pointwise_pvalues_consistent_with_itp_two_pop():
    a, b, t, _ = _shifted_samples(3)
    reg = I.itp_two_pop_regions(a, b, t, n_perm=299, seed=7)
    itp = I.itp_two_pop(a, b, t, nbasis=15, n_perm=299, seed=7)
    np.testing.assert_array_equal(itp["adjusted_pvalues"], reg["itp"]["adjusted_pvalues"])
    dom = I.itp_pointwise_pvalues(itp, t)
    np.testing.assert_array_equal(dom, reg["pointwise_adjusted_pvalues"])
    np.testing.assert_array_equal(I.itp_pointwise_pvalues(reg["itp"], t, mapping="dominant"), dom)
    assert dom.shape == (50,) and np.isin(dom, itp["adjusted_pvalues"]).all()
    sup = I.itp_pointwise_pvalues(itp, t, mapping="support")
    assert np.all(sup >= dom)
    sup_reg = I.itp_two_pop_regions(a, b, t, n_perm=299, seed=7, mapping="support")
    np.testing.assert_array_equal(sup_reg["pointwise_adjusted_pvalues"], sup)
    # one-population results map the same way
    one = I.itp_one_pop(a - b, t, nbasis=8, n_perm=99)
    assert I.itp_pointwise_pvalues(one, t).shape == (50,)


def test_itp_regions_and_pointwise_errors():
    a, b, t, _ = _shifted_samples(3, n=6)
    with pytest.raises(ValueError):
        I.itp_two_pop_regions(a, b, t, alpha=1.5)
    with pytest.raises(ValueError):
        I.itp_two_pop_regions(a, b, t, mapping="nearest")
    with pytest.raises(ValueError):
        I.itp_two_pop_regions(a, b[:, :-1], t)
    with pytest.raises(ValueError):
        I.itp_two_pop_regions(a[:1], b, t)
    itp = I.itp_two_pop(a, b, t, nbasis=10, n_perm=49)
    fourier = I.itp_two_pop(a, b, t, basis_type="fourier", nbasis=7, n_perm=49)
    with pytest.raises(ValueError, match="B-spline"):
        I.itp_pointwise_pvalues(fourier, t)
    with pytest.raises(ValueError):
        I.itp_pointwise_pvalues(itp, t, mapping="nearest")
    with pytest.raises(ValueError, match="adjusted_pvalues"):
        I.itp_pointwise_pvalues({"n_basis": 10, "basis_type": "bspline"}, t)
    with pytest.raises(ValueError):
        I.itp_pointwise_pvalues(dict(itp, adjusted_pvalues=itp["adjusted_pvalues"][:-1]), t)
    with pytest.raises(ValueError):
        I.itp_pointwise_pvalues(dict(itp, n_basis=3, adjusted_pvalues=np.ones(3)), t)
