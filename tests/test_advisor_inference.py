"""Tests for the inference diagnostics aspect (ADV-03, plan 34-01).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests mirror the structure of test_advisor_scoring.py:
- check_no_numpy recursive walker
- byte-identical json.dumps(sort_keys=True)
- grounding via _extract_numbers + json.dumps(diag)
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixed TestResult/ToleranceBand dicts used across tests (no RNG, no fdars
# call in the test — the caller-supplied-dict contract means tests pass literal
# numbers matching realistic fdars outputs).
# ---------------------------------------------------------------------------

# A significant permutation result (p_value 0.03 is significant at 0.05/0.10)
_SIG_PERM = {"statistic": 2.5, "p_value": 0.03, "n_perm": 999}

# A non-significant permutation result (p_value 0.62 is not significant at any level)
_NONSIG_PERM = {"statistic": 0.4, "p_value": 0.62, "n_perm": 999}

# An asymptotic result (Hotelling T²-style; n_perm==0 is legitimate here)
_ASYMPTOTIC = {"statistic": 8.1, "p_value": 0.004, "n_perm": 0}

# A ToleranceBand / SCB shaped dict — no p_value; half_width + center present
_SCB_BAND = {
    "lower": [0.1, 0.2, 0.3, 0.2],
    "upper": [0.9, 0.8, 0.7, 0.8],
    "center": [0.5, 0.5, 0.5, 0.5],
    "half_width": [0.4, 0.3, 0.2, 0.3],
}


# ---------------------------------------------------------------------------
# Test 1: Basic correctness — method field, types, json.dumps succeeds.
# ---------------------------------------------------------------------------

class TestInferenceBuildDiagnosticsBasic:
    """Verify the inference diagnostics builder returns well-formed output."""

    def test_inference_build_diagnostics_basic(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SIG_PERM, method="inference")

        assert diag["method"] == "inference"
        # statistic and p_value echoed as native float
        assert isinstance(diag["statistic"], float)
        assert abs(diag["statistic"] - 2.5) < 1e-9
        assert isinstance(diag["p_value"], float)
        assert abs(diag["p_value"] - 0.03) < 1e-9
        # n_perm echoed as native int
        assert isinstance(diag["n_perm"], int)
        assert diag["n_perm"] == 999
        # json.dumps must succeed (no non-serialisable types)
        json.dumps(diag, sort_keys=True)

    def test_inference_output_keys_complete(self):
        """All expected output keys are present for a TestResult input."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SIG_PERM, method="inference")

        expected_keys = {
            "method",
            "statistic",
            "p_value",
            "n_perm",
            "significant_at_0.01",
            "significant_at_0.05",
            "significant_at_0.10",
            "strongest_significance_level",
            "is_permutation_test",
        }
        assert expected_keys.issubset(diag.keys()), (
            f"Missing output keys: {expected_keys - diag.keys()}"
        )


# ---------------------------------------------------------------------------
# Test 2: Significance flags — correct boolean derivation at each alpha level.
# ---------------------------------------------------------------------------

class TestInferenceSignificanceFlags:
    """Verify significance flags are correctly derived from p_value."""

    def test_significant_result_flags(self):
        """p_value=0.03: significant at 0.05 and 0.10, NOT at 0.01."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SIG_PERM, method="inference")

        assert diag["significant_at_0.01"] is False
        assert diag["significant_at_0.05"] is True
        assert diag["significant_at_0.10"] is True
        assert diag["strongest_significance_level"] == pytest.approx(0.05)

    def test_nonsignificant_result_flags(self):
        """p_value=0.62: not significant at any level."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_NONSIG_PERM, method="inference")

        assert diag["significant_at_0.01"] is False
        assert diag["significant_at_0.05"] is False
        assert diag["significant_at_0.10"] is False
        assert diag["strongest_significance_level"] is None

    def test_asymptotic_result_significant_at_0_01(self):
        """p_value=0.004: significant at 0.01 (strongest level)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_ASYMPTOTIC, method="inference")

        assert diag["significant_at_0.01"] is True
        assert diag["significant_at_0.05"] is True
        assert diag["significant_at_0.10"] is True
        assert diag["strongest_significance_level"] == pytest.approx(0.01)

    def test_significance_flag_types_are_bool(self):
        """Significance flags must be native bool (not numpy.bool_ or int)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SIG_PERM, method="inference")

        for key in ("significant_at_0.01", "significant_at_0.05", "significant_at_0.10"):
            val = diag[key]
            assert type(val) is bool, (  # noqa: E721 (exact type check)
                f"{key} must be native bool, got {type(val)!r}"
            )


# ---------------------------------------------------------------------------
# Test 3: Asymptotic vs permutation — n_perm == 0 is legitimate (NOT missing).
# ---------------------------------------------------------------------------

class TestInferenceAsymptoticVsPermutation:
    """Verify the n_perm==0 contract: asymptotic path, not an error."""

    def test_asymptotic_is_not_permutation(self):
        """n_perm==0: is_permutation_test is False (asymptotic, not an error)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_ASYMPTOTIC, method="inference")

        assert diag["n_perm"] == 0
        assert diag["is_permutation_test"] is False

    def test_permutation_is_permutation_test(self):
        """n_perm==999: is_permutation_test is True."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SIG_PERM, method="inference")

        assert diag["is_permutation_test"] is True

    def test_nonsig_permutation_is_permutation_test(self):
        """Non-significant permutation result: is_permutation_test is still True."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_NONSIG_PERM, method="inference")

        assert diag["is_permutation_test"] is True

    def test_is_permutation_test_is_bool(self):
        """is_permutation_test must be native bool (not numpy.bool_)."""
        from fdars.advisor import build_diagnostics

        for fixture in (_SIG_PERM, _ASYMPTOTIC, _NONSIG_PERM):
            diag = build_diagnostics(fixture, method="inference")
            val = diag["is_permutation_test"]
            assert type(val) is bool, (  # noqa: E721
                f"is_permutation_test must be native bool, got {type(val)!r}"
            )


# ---------------------------------------------------------------------------
# Test 4: ToleranceBand tolerance — SCB-shaped input handled gracefully.
# ---------------------------------------------------------------------------

class TestInferenceToleranceBandTolerance:
    """Verify the builder tolerates a ToleranceBand / SCB shaped input."""

    def test_scb_band_returns_inference_method(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SCB_BAND, method="inference")

        assert diag["method"] == "inference"

    def test_scb_band_significance_flags_none(self):
        """ToleranceBand path: all three significance flags are None."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SCB_BAND, method="inference")

        assert diag["significant_at_0.01"] is None
        assert diag["significant_at_0.05"] is None
        assert diag["significant_at_0.10"] is None
        assert diag["p_value"] is None

    def test_scb_band_json_serialisable(self):
        """ToleranceBand output must be JSON-serialisable."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SCB_BAND, method="inference")

        json.dumps(diag, sort_keys=True)

    def test_scb_band_band_present_true(self):
        """band_present is True for a ToleranceBand-shaped input."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SCB_BAND, method="inference")

        assert diag.get("band_present") is True


# ---------------------------------------------------------------------------
# Test 5: Determinism — byte-identical json.dumps + no numpy scalars.
# Mirrors TestScoringDeterministic in test_advisor_scoring.py exactly.
# ---------------------------------------------------------------------------

class TestInferenceDeterministic:
    """Verify the inference builder is deterministic and numpy-scalar-free."""

    def test_inference_deterministic(self):
        """Two calls on the same input produce equal dicts AND byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics

        d1 = build_diagnostics(_SIG_PERM, method="inference")
        d2 = build_diagnostics(_SIG_PERM, method="inference")

        assert d1 == d2, "Two calls produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between calls"

        def check_no_numpy(obj):
            """Recursive walker: fail if any value is a numpy scalar."""
            assert not isinstance(obj, np.generic), (
                f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
            )
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_numpy(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_no_numpy(v)

        check_no_numpy(d1)


# ---------------------------------------------------------------------------
# Test 6: Grounding — every numeric value in the input is discoverable in
# json.dumps(diag).  Mirrors TestScoringGrounding.
# ---------------------------------------------------------------------------

class TestInferenceGrounding:
    """Verify the grounding invariant: builder echoes caller-supplied fdars numbers."""

    def test_inference_grounding(self):
        """Each input numeric value is recoverable from json.dumps(diag).

        This ensures the builder cites real caller-supplied values rather than
        fabricated numbers.
        """
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers

        input_result = {"statistic": 2.5, "p_value": 0.03, "n_perm": 999}
        diag = build_diagnostics(input_result, method="inference")
        diag_json = json.dumps(diag, sort_keys=True)
        found_numbers = set(_extract_numbers(diag_json))

        # Each input value we passed in must be discoverable in the serialised output
        for key, value in input_result.items():
            value_str = str(value)
            assert any(value_str in n or n in value_str for n in found_numbers), (
                f"input value {key}={value} not discoverable in diagnostics json: "
                f"found_numbers={found_numbers!r}"
            )


# ---------------------------------------------------------------------------
# Test 7: Offline — no network, no API key imported as side effect.
# Mirrors TestScoringOfflineNoNetwork.
# ---------------------------------------------------------------------------

class TestInferenceOfflineNoNetwork:
    """Verify build_diagnostics for inference is fully offline."""

    def test_inference_offline_no_network(self):
        """Builder path runs with no ANTHROPIC_API_KEY and no network import."""
        import sys

        # Record modules before — build_diagnostics must not trigger anthropic/openai
        modules_before = set(sys.modules.keys())

        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SIG_PERM, method="inference")

        new_modules = set(sys.modules.keys()) - modules_before
        network_modules = {
            m for m in new_modules
            if m == "anthropic" or m.startswith("anthropic.")
            or m == "openai" or m.startswith("openai.")
        }
        assert not network_modules, (
            f"build_diagnostics imported network modules: {network_modules}"
        )

        # Output is valid and JSON-serialisable
        assert diag["method"] == "inference"
        json.dumps(diag, sort_keys=True)


# ---------------------------------------------------------------------------
# Test 8: Robustness — malformed input raises ValueError loudly.
# ---------------------------------------------------------------------------

class TestInferenceRobustness:
    """Verify defensive input handling."""

    def test_malformed_input_raises_value_error(self):
        """A dict with neither TestResult nor ToleranceBand keys raises ValueError."""
        from fdars.advisor import build_diagnostics

        with pytest.raises(ValueError):
            build_diagnostics({"foo": 1}, method="inference")

    def test_malformed_input_error_names_expected_keys(self):
        """ValueError message names the expected TestResult keys."""
        from fdars.advisor import build_diagnostics

        with pytest.raises(ValueError, match="statistic"):
            build_diagnostics({"foo": 1}, method="inference")

    def test_non_dict_input_coerced(self):
        """Non-dict input with dict-like interface is coerced rather than failing."""
        from fdars.advisor import build_diagnostics

        # dict() on a list-of-pairs is valid coercion
        raw_pairs = [("statistic", 1.2), ("p_value", 0.08), ("n_perm", 199)]
        diag = build_diagnostics(raw_pairs, method="inference")
        assert diag["method"] == "inference"
        assert isinstance(diag["statistic"], float)


# ---------------------------------------------------------------------------
# Test 9: Exact-threshold boundary — pins strict-< semantics of significance
# flags so a future change from < to <= would be caught immediately.
# ---------------------------------------------------------------------------

class TestInferenceExactBoundary:
    """Exact-boundary tests for significance flags.

    p_value == alpha must NOT be significant (strict ``<``, not ``<=``).
    p_value just below alpha (by a value well within float precision) MUST be.
    """

    def test_exact_0_05_not_significant(self):
        """p_value == 0.05: NOT significant at 0.05 (strict <), but IS at 0.10."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            {"statistic": 1.0, "p_value": 0.05, "n_perm": 999},
            method="inference",
        )
        assert diag["significant_at_0.05"] is False
        # 0.05 < 0.10, so the result IS significant at the 0.10 level
        assert diag["significant_at_0.10"] is True
        assert diag["strongest_significance_level"] == pytest.approx(0.10)

    def test_just_below_0_05_is_significant(self):
        """p_value == 0.0499: significant at 0.05 (strict <)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            {"statistic": 1.0, "p_value": 0.0499, "n_perm": 999},
            method="inference",
        )
        assert diag["significant_at_0.05"] is True
        assert diag["significant_at_0.01"] is False
        assert diag["strongest_significance_level"] == pytest.approx(0.05)

    def test_exact_0_01_not_significant(self):
        """p_value == 0.01: NOT significant at 0.01 (strict <)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            {"statistic": 1.0, "p_value": 0.01, "n_perm": 999},
            method="inference",
        )
        assert diag["significant_at_0.01"] is False
        assert diag["significant_at_0.05"] is True
        assert diag["strongest_significance_level"] == pytest.approx(0.05)

    def test_exact_0_10_not_significant(self):
        """p_value == 0.10: NOT significant at 0.10 (strict <)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            {"statistic": 1.0, "p_value": 0.10, "n_perm": 999},
            method="inference",
        )
        assert diag["significant_at_0.10"] is False
        assert diag["significant_at_0.05"] is False
        assert diag["significant_at_0.01"] is False
        assert diag["strongest_significance_level"] is None
