"""Tests for fdars.inference submodule.

Covers:
- t_perm_test (Task 2 tracer)
- f_perm_test (Task 3)
- two_sample_mean_test (Task 4)
- mean_scb (Task 1 of plan 31-02: INFER-04)
- scb_two_sample_test (Task 2 of plan 31-02: INFER-05)

Dataset: Berkeley Growth Study (93 subjects x 31 age-points).
  Boys: rows 0-38, girls: rows 39-92.
Test slices are small (10 boys, 10 girls) for fast CI.
n_perm is kept to 19-29 in tests to avoid slow CI.

Canadian Weather dataset used for mean_scb (single group).
"""

import json

import numpy as np
import pytest

from fdars.datasets import load_growth


# ---------------------------------------------------------------------------
# Fixture: small Growth subsets for two-sample tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def growth_subsets():
    """Return (boys_X, girls_X, age) — each group has 10 curves."""
    age, X, _ = load_growth(return_fdata=False)
    # Boys are rows 0-38, girls rows 39-92 in the growth dataset.
    boys = X[:10, :]
    girls = X[39:49, :]
    return boys, girls, age


# ---------------------------------------------------------------------------
# Task 2: t_perm_test import and basic shape tests
# ---------------------------------------------------------------------------


class TestImportPaths:
    """Both import styles must resolve the same callable."""

    def test_import_submodule(self):
        import fdars.inference  # noqa: F401

    def test_from_import(self):
        from fdars.inference import t_perm_test  # noqa: F401

    def test_t_perm_test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.t_perm_test)

    def test_f_perm_test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.f_perm_test)

    def test_two_sample_mean_test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.two_sample_mean_test)


class TestTPerm:
    """t_perm_test correctness, shape, and determinism."""

    def test_returns_dict_with_three_keys(self, growth_subsets):
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        result = t_perm_test(boys, girls, age, n_perm=19)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_roundtrip(self, growth_subsets):
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        result = t_perm_test(boys, girls, age, n_perm=23)
        assert result["n_perm"] == 23

    def test_values_are_plain_python_types(self, growth_subsets):
        """json.dumps must not raise (no numpy scalar leakage)."""
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        result = t_perm_test(boys, girls, age, n_perm=19, seed=42)
        # Raises TypeError if numpy scalars are in the dict
        serialized = json.dumps(result, sort_keys=True)
        assert isinstance(serialized, str)

    def test_seed_determinism_explicit(self, growth_subsets):
        """Two calls with the same explicit seed produce byte-identical output."""
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        r1 = t_perm_test(boys, girls, age, n_perm=29, seed=7)
        r2 = t_perm_test(boys, girls, age, n_perm=29, seed=7)
        s1 = json.dumps(r1, sort_keys=True)
        s2 = json.dumps(r2, sort_keys=True)
        assert s1 == s2, "Same explicit seed must give byte-identical result"

    def test_seed_none_equals_seed_zero(self, growth_subsets):
        """seed=None resolves to fixed default 0 (byte-identical to seed=0)."""
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        r_none = t_perm_test(boys, girls, age, n_perm=19, seed=None)
        r_zero = t_perm_test(boys, girls, age, n_perm=19, seed=0)
        s_none = json.dumps(r_none, sort_keys=True)
        s_zero = json.dumps(r_zero, sort_keys=True)
        assert s_none == s_zero, "seed=None must equal seed=0"

    def test_p_value_in_range(self, growth_subsets):
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        result = t_perm_test(boys, girls, age, n_perm=19, seed=1)
        assert 0.0 <= result["p_value"] <= 1.0
        assert result["statistic"] >= 0.0

    def test_raises_on_mismatched_argvals(self, growth_subsets):
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        bad_age = age[:-1]  # one shorter — triggers InvalidDimension
        with pytest.raises(ValueError):
            t_perm_test(boys, girls, bad_age, n_perm=19)

    def test_raises_on_n_perm_zero(self, growth_subsets):
        from fdars.inference import t_perm_test

        boys, girls, age = growth_subsets
        with pytest.raises(ValueError):
            t_perm_test(boys, girls, age, n_perm=0)


# ---------------------------------------------------------------------------
# Task 3: f_perm_test
# ---------------------------------------------------------------------------


class TestFPerm:
    """f_perm_test correctness, shape, and determinism."""

    def test_returns_dict_with_three_keys(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        result = f_perm_test(boys, girls, age, n_perm=19)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_roundtrip(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        result = f_perm_test(boys, girls, age, n_perm=23)
        assert result["n_perm"] == 23

    def test_seed_determinism_explicit(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        r1 = f_perm_test(boys, girls, age, n_perm=29, seed=13)
        r2 = f_perm_test(boys, girls, age, n_perm=29, seed=13)
        s1 = json.dumps(r1, sort_keys=True)
        s2 = json.dumps(r2, sort_keys=True)
        assert s1 == s2, "Same explicit seed must give byte-identical result"

    def test_seed_none_equals_seed_zero(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        r_none = f_perm_test(boys, girls, age, n_perm=19, seed=None)
        r_zero = f_perm_test(boys, girls, age, n_perm=19, seed=0)
        s_none = json.dumps(r_none, sort_keys=True)
        s_zero = json.dumps(r_zero, sort_keys=True)
        assert s_none == s_zero, "seed=None must equal seed=0"

    def test_values_plain_types(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        result = f_perm_test(boys, girls, age, n_perm=19, seed=3)
        serialized = json.dumps(result, sort_keys=True)
        assert isinstance(serialized, str)

    def test_raises_on_mismatched_argvals(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        bad_age = age[:-1]
        with pytest.raises(ValueError):
            f_perm_test(boys, girls, bad_age, n_perm=19)

    def test_raises_on_n_perm_zero(self, growth_subsets):
        from fdars.inference import f_perm_test

        boys, girls, age = growth_subsets
        with pytest.raises(ValueError):
            f_perm_test(boys, girls, age, n_perm=0)


# ---------------------------------------------------------------------------
# Task 4: two_sample_mean_test
# ---------------------------------------------------------------------------


class TestTwoSampleMeanTest:
    """two_sample_mean_test correctness, shape, and asymptotic n_perm==0."""

    def test_returns_dict_with_three_keys(self, growth_subsets):
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        result = two_sample_mean_test(boys, girls, age, ncomp=3)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_is_zero(self, growth_subsets):
        """Asymptotic test always has n_perm == 0."""
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        result = two_sample_mean_test(boys, girls, age, ncomp=3)
        assert result["n_perm"] == 0

    def test_p_value_in_range(self, growth_subsets):
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        result = two_sample_mean_test(boys, girls, age, ncomp=3)
        assert 0.0 <= result["p_value"] <= 1.0
        assert result["statistic"] >= 0.0

    def test_values_plain_types(self, growth_subsets):
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        result = two_sample_mean_test(boys, girls, age, ncomp=3)
        serialized = json.dumps(result, sort_keys=True)
        assert isinstance(serialized, str)

    def test_no_seed_parameter(self, growth_subsets):
        """two_sample_mean_test accepts no seed — must be deterministic without it."""
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        r1 = two_sample_mean_test(boys, girls, age, ncomp=3)
        r2 = two_sample_mean_test(boys, girls, age, ncomp=3)
        assert r1["statistic"] == r2["statistic"]
        assert r1["p_value"] == r2["p_value"]

    def test_raises_on_degenerate_ncomp(self, growth_subsets):
        """ncomp larger than min group size is degenerate."""
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        # min(10, 10) = 10; ncomp=15 > min group size -> clamps or errors
        # ncomp=0 is explicitly invalid per the spec
        with pytest.raises(ValueError):
            two_sample_mean_test(boys, girls, age, ncomp=0)

    def test_raises_on_mismatched_argvals(self, growth_subsets):
        from fdars.inference import two_sample_mean_test

        boys, girls, age = growth_subsets
        bad_age = age[:-1]
        with pytest.raises(ValueError):
            two_sample_mean_test(boys, girls, bad_age, ncomp=3)


# ---------------------------------------------------------------------------
# INFER-04: mean_scb
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def canadian_scb_fixture():
    """Return (X_small, grid) from Canadian Weather for SCB tests.

    Uses a column stride (::30) to keep m small and tests fast.
    n >= 3 required by Degras; we use all 35 stations, stride columns.
    """
    from fdars.datasets import load_canadian_weather

    day, X, _ = load_canadian_weather(variable="temperature", return_fdata=False)
    # Stride to keep m small and speed up nb iterations.
    grid = day[::30].copy()
    X_small = X[:, ::30].copy()
    return X_small, grid


class TestMeanScbImport:
    """mean_scb must be importable from fdars.inference."""

    def test_mean_scb_importable(self):
        import fdars.inference

        assert callable(fdars.inference.mean_scb)

    def test_from_import(self):
        from fdars.inference import mean_scb  # noqa: F401


class TestMeanScb:
    """mean_scb correctness: dict keys, band shapes, finite values, multipliers."""

    def test_returns_dict_with_four_keys(self, canadian_scb_fixture):
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        result = mean_scb(X, grid, 20.0, nb=50)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"lower", "upper", "center", "half_width"}

    def test_band_shape_equals_m(self, canadian_scb_fixture):
        """Each band array has shape (m,) matching the argvals length."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        m = len(grid)
        result = mean_scb(X, grid, 20.0, nb=50)
        for key in ("lower", "upper", "center", "half_width"):
            arr = result[key]
            assert isinstance(arr, np.ndarray), f"{key} must be ndarray"
            assert arr.shape == (m,), f"{key}: expected shape ({m},), got {arr.shape}"

    def test_band_values_are_finite(self, canadian_scb_fixture):
        """All entries in all four band arrays must be finite."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        result = mean_scb(X, grid, 20.0, nb=50)
        for key in ("lower", "upper", "center", "half_width"):
            assert np.all(np.isfinite(result[key])), (
                f"{key}: contains non-finite values"
            )

    def test_multiplier_rademacher_succeeds(self, canadian_scb_fixture):
        """multiplier='rademacher' must succeed and return same shape."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        m = len(grid)
        result = mean_scb(X, grid, 20.0, nb=50, multiplier="rademacher")
        assert set(result.keys()) == {"lower", "upper", "center", "half_width"}
        for key in ("lower", "upper", "center", "half_width"):
            assert result[key].shape == (m,)

    def test_unknown_multiplier_raises_value_error(self, canadian_scb_fixture):
        """An unrecognised multiplier string must raise ValueError."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        with pytest.raises(ValueError, match="multiplier"):
            mean_scb(X, grid, 20.0, nb=50, multiplier="bogus")

    def test_nb_zero_raises_value_error(self, canadian_scb_fixture):
        """nb=0 must raise ValueError (forwarded from fdars-core)."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        with pytest.raises(ValueError):
            mean_scb(X, grid, 20.0, nb=0)

    def test_confidence_out_of_range_raises_value_error(self, canadian_scb_fixture):
        """confidence=1.5 (outside (0, 1)) must raise ValueError."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        with pytest.raises(ValueError):
            mean_scb(X, grid, 20.0, nb=50, confidence=1.5)

    def test_lower_le_center_le_upper(self, canadian_scb_fixture):
        """Ordering invariant: lower <= center <= upper at every grid point."""
        from fdars.inference import mean_scb

        X, grid = canadian_scb_fixture
        result = mean_scb(X, grid, 20.0, nb=50)
        assert np.all(result["lower"] <= result["center"]), (
            "lower must be <= center at every point"
        )
        assert np.all(result["center"] <= result["upper"]), (
            "center must be <= upper at every point"
        )


# ---------------------------------------------------------------------------
# INFER-05: scb_two_sample_test
# ---------------------------------------------------------------------------


class TestScbTwoSampleImport:
    """scb_two_sample_test must be importable from fdars.inference."""

    def test_scb_two_sample_test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.scb_two_sample_test)

    def test_from_import(self):
        from fdars.inference import scb_two_sample_test  # noqa: F401


class TestScbTwoSampleTest:
    """scb_two_sample_test: dict keys, n_perm==0, multiplier dispatch, errors."""

    def test_returns_dict_with_three_keys(self, growth_subsets):
        from fdars.inference import scb_two_sample_test

        boys, girls, age = growth_subsets
        result = scb_two_sample_test(boys, girls, age, 5.0, nb=50)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_is_zero(self, growth_subsets):
        """SCB path always returns n_perm == 0 (asymptotic, not permutation)."""
        from fdars.inference import scb_two_sample_test

        boys, girls, age = growth_subsets
        result = scb_two_sample_test(boys, girls, age, 5.0, nb=50)
        assert result["n_perm"] == 0

    def test_unknown_multiplier_raises_value_error(self, growth_subsets):
        """An unrecognised multiplier string must raise ValueError."""
        from fdars.inference import scb_two_sample_test

        boys, girls, age = growth_subsets
        with pytest.raises(ValueError, match="multiplier"):
            scb_two_sample_test(boys, girls, age, 5.0, nb=50, multiplier="bogus")


# ---------------------------------------------------------------------------
# INFER-06: flm_f_test (FLM overall-significance F-test, re-fit internally)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def tecator_fixture():
    """Return (X_small, fat) from Tecator for FLM inference tests.

    Uses 30 observations and a column stride (::10) to keep m small and tests fast.
    n_comp must stay small (e.g. 3) relative to n for a non-degenerate fit.
    """
    from fdars.datasets import load_tecator

    wav, X, meta = load_tecator(return_fdata=False)
    n = 30
    X_small = X[:n, ::10].copy()
    fat = meta["fat"].values[:n].astype(float)
    return X_small, fat


class TestFlmFTestImport:
    """flm_f_test must be importable from fdars.inference."""

    def test_flm_f_test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.flm_f_test)

    def test_from_import(self):
        from fdars.inference import flm_f_test  # noqa: F401


class TestFlmFTest:
    """flm_f_test correctness: dict keys, n_perm==0, degenerate-fit ValueError."""

    def test_returns_dict_with_three_keys(self, tecator_fixture):
        """flm_f_test must return a dict with keys statistic, p_value, n_perm."""
        from fdars.inference import flm_f_test

        X, fat = tecator_fixture
        result = flm_f_test(X, fat, n_comp=3)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_is_zero(self, tecator_fixture):
        """Asymptotic F-test always has n_perm == 0."""
        from fdars.inference import flm_f_test

        X, fat = tecator_fixture
        result = flm_f_test(X, fat, n_comp=3)
        assert result["n_perm"] == 0

    def test_p_value_in_range(self, tecator_fixture):
        from fdars.inference import flm_f_test

        X, fat = tecator_fixture
        result = flm_f_test(X, fat, n_comp=3)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_statistic_nonnegative(self, tecator_fixture):
        from fdars.inference import flm_f_test

        X, fat = tecator_fixture
        result = flm_f_test(X, fat, n_comp=3)
        assert result["statistic"] >= 0.0

    def test_values_plain_types(self, tecator_fixture):
        """json.dumps must not raise (no numpy scalar leakage)."""
        import json

        from fdars.inference import flm_f_test

        X, fat = tecator_fixture
        result = flm_f_test(X, fat, n_comp=3)
        serialized = json.dumps(result, sort_keys=True)
        assert isinstance(serialized, str)

    def test_degenerate_input_raises_value_error(self):
        """n < 3 rows makes the internal fregre_lm degenerate (raises ValueError).

        The core requires at least 3 observations for a valid fit.
        """
        from fdars.inference import flm_f_test

        X_tiny = np.ones((2, 5))  # only 2 rows — triggers InvalidDimension in fregre_lm
        y_tiny = np.array([1.0, 2.0])
        with pytest.raises(ValueError):
            flm_f_test(X_tiny, y_tiny, n_comp=1)


# ---------------------------------------------------------------------------
# INFER-07: flm_gof_test (Ramsey-RESET goodness-of-fit, symmetric with flm_f_test)
# ---------------------------------------------------------------------------


class TestFlmGofTestImport:
    """flm_gof_test must be importable from fdars.inference."""

    def test_flm_gof_test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.flm_gof_test)

    def test_from_import(self):
        from fdars.inference import flm_gof_test  # noqa: F401


class TestFlmGofTest:
    """flm_gof_test correctness: dict keys, n_perm==0, degenerate ValueError."""

    def test_returns_dict_with_three_keys(self, tecator_fixture):
        from fdars.inference import flm_gof_test

        X, fat = tecator_fixture
        result = flm_gof_test(X, fat, n_comp=3)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_is_zero(self, tecator_fixture):
        from fdars.inference import flm_gof_test

        X, fat = tecator_fixture
        result = flm_gof_test(X, fat, n_comp=3)
        assert result["n_perm"] == 0

    def test_p_value_in_range(self, tecator_fixture):
        from fdars.inference import flm_gof_test

        X, fat = tecator_fixture
        result = flm_gof_test(X, fat, n_comp=3)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_degenerate_input_raises_value_error(self):
        """n <= 4 rows makes the RESET auxiliary regression degenerate (raises ValueError).

        The GoF test requires n > 4 for sufficient auxiliary degrees of freedom.
        """
        from fdars.inference import flm_gof_test

        X_tiny = np.ones((4, 5))  # n=4 — triggers degenerate-df error in flm_gof_test
        X_tiny[:, 0] = [1.0, 2.0, 3.0, 4.0]  # some variation to allow fregre_lm fit
        y_tiny = np.array([1.0, 2.0, 3.0, 4.0])
        with pytest.raises(ValueError):
            flm_gof_test(X_tiny, y_tiny, n_comp=1)


# ---------------------------------------------------------------------------
# INFER-08: oneway_anova_vstat (asymptotic one-way functional ANOVA V-statistic)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def canadian_anova_fixture():
    """Return (X_small, groups_i64, grid) from Canadian Weather for ANOVA tests.

    Maps the meta 'region' column to 0-indexed integer codes.
    Uses a column stride (::30) to keep m small.
    """
    from fdars.datasets import load_canadian_weather

    day, X, meta = load_canadian_weather(variable="temperature", return_fdata=False)
    grid = day[::30].copy()
    X_small = X[:, ::30].copy()
    # Map region strings to 0-indexed integer codes
    _, group_codes = np.unique(meta["region"], return_inverse=True)
    groups_i64 = group_codes.astype(np.int64)
    return X_small, groups_i64, grid


class TestOnewayAnovaVstatImport:
    """oneway_anova_vstat must be importable from fdars.inference."""

    def test_importable(self):
        import fdars.inference

        assert callable(fdars.inference.oneway_anova_vstat)

    def test_from_import(self):
        from fdars.inference import oneway_anova_vstat  # noqa: F401


class TestOnewayAnovaVstat:
    """oneway_anova_vstat: dict keys, n_perm==0, group-label validation."""

    def test_returns_dict_with_three_keys(self, canadian_anova_fixture):
        from fdars.inference import oneway_anova_vstat

        X, groups, grid = canadian_anova_fixture
        result = oneway_anova_vstat(X, groups, grid)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"statistic", "p_value", "n_perm"}

    def test_n_perm_is_zero(self, canadian_anova_fixture):
        """Asymptotic V-statistic always has n_perm == 0."""
        from fdars.inference import oneway_anova_vstat

        X, groups, grid = canadian_anova_fixture
        result = oneway_anova_vstat(X, groups, grid)
        assert result["n_perm"] == 0

    def test_p_value_in_range(self, canadian_anova_fixture):
        from fdars.inference import oneway_anova_vstat

        X, groups, grid = canadian_anova_fixture
        result = oneway_anova_vstat(X, groups, grid)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_statistic_nonnegative(self, canadian_anova_fixture):
        from fdars.inference import oneway_anova_vstat

        X, groups, grid = canadian_anova_fixture
        result = oneway_anova_vstat(X, groups, grid)
        assert result["statistic"] >= 0.0

    def test_values_plain_types(self, canadian_anova_fixture):
        """json.dumps must not raise (no numpy scalar leakage)."""
        import json

        from fdars.inference import oneway_anova_vstat

        X, groups, grid = canadian_anova_fixture
        result = oneway_anova_vstat(X, groups, grid)
        serialized = json.dumps(result, sort_keys=True)
        assert isinstance(serialized, str)

    def test_single_group_raises_value_error(self, canadian_anova_fixture):
        """Fewer than 2 distinct groups raises ValueError."""
        from fdars.inference import oneway_anova_vstat

        X, _, grid = canadian_anova_fixture
        # All observations in group 0
        n = X.shape[0]
        single_group = np.zeros(n, dtype=np.int64)
        with pytest.raises(ValueError):
            oneway_anova_vstat(X, single_group, grid)

    def test_groups_length_mismatch_raises_value_error(self, canadian_anova_fixture):
        """groups.len() != n raises ValueError."""
        from fdars.inference import oneway_anova_vstat

        X, groups, grid = canadian_anova_fixture
        short_groups = groups[:-1]
        with pytest.raises(ValueError):
            oneway_anova_vstat(X, short_groups, grid)
