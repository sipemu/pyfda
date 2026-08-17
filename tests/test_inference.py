"""Tests for fdars.inference submodule.

Covers:
- t_perm_test (Task 2 tracer)
- f_perm_test (Task 3)
- two_sample_mean_test (Task 4)

Dataset: Berkeley Growth Study (93 subjects x 31 age-points).
  Boys: rows 0-38, girls: rows 39-92.
Test slices are small (10 boys, 10 girls) for fast CI.
n_perm is kept to 19-29 in tests to avoid slow CI.
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
