"""Tests for imputation-quality diagnostics on the represent aspect (ADV-02, plan 28-02).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests mirror test_depth_deterministic in test_advisor.py:
- check_no_numpy recursive walker
- byte-identical json.dumps(sort_keys=True)
- grounding via _extract_numbers + json.dumps(diag)
- backward-compat: pre-existing keys unchanged when new inputs absent
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixed literal arrays — no RNG, deterministic across runs.
# Two observations (rows), three grid points (cols).
# orig has two NaN cells; imp is the imputed version.
# ---------------------------------------------------------------------------

_ARGVALS = [0.0, 0.5, 1.0]

# Original data with NaN cells (2 out of 6 total = imputed_fraction = 1/3)
_ORIG_WITH_NAN = [
    [0.0, float("nan"), 2.0],
    [1.0, 1.0, float("nan")],
]

# Imputed version — NaN cells filled in
_IMPUTED = [
    [0.0, 1.0, 2.0],
    [1.0, 1.0, 1.0],
]

# Input dict with imputation context
_IMPUTED_INPUT = {
    "data": _ORIG_WITH_NAN,
    "imputed": _IMPUTED,
    "argvals": _ARGVALS,
}

# Plain represent input — no NaN, no imputed key (backward-compat)
_PLAIN_INPUT = {
    "data": [[0.0, 1.0, 2.0], [1.0, 1.0, 1.0]],
    "argvals": _ARGVALS,
}


# ---------------------------------------------------------------------------
# Test 1: basic — imputation-quality keys present and correct types.
# ---------------------------------------------------------------------------

class TestImputationQualityBasic:
    """Verify the imputation-quality keys are added to the represent builder."""

    def test_imputation_keys_present_when_imputed_supplied(self):
        """build_diagnostics returns imputed_fraction and imputation_mae."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")

        assert "imputed_fraction" in diag
        assert "imputation_mae" in diag

    def test_imputed_fraction_is_correct_float(self):
        """imputed_fraction = count(NaN cells) / total cells."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")

        frac = diag["imputed_fraction"]
        assert frac is not None, "imputed_fraction should not be None when imputed supplied"
        assert isinstance(frac, float), f"expected float, got {type(frac)!r}"
        assert not isinstance(frac, np.generic), "numpy scalar leaked into imputed_fraction"
        # 2 NaN cells / 6 total = 1/3
        assert abs(frac - (2 / 6)) < 1e-9, f"expected ~0.333, got {frac}"

    def test_imputation_mae_is_finite_float_from_fdars(self):
        """imputation_mae is a finite float (fdars.scoring.functional_mae, not np arithmetic)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")

        val = diag["imputation_mae"]
        assert val is not None, "imputation_mae should not be None when imputed supplied"
        assert isinstance(val, float), f"expected float, got {type(val)!r}"
        assert not isinstance(val, np.generic), "numpy scalar leaked into imputation_mae"
        assert float("-inf") < val < float("inf"), "imputation_mae is not finite"

    def test_imputation_mae_is_zero_for_perfect_imputation(self):
        """functional_mae = 0 when imputed == original (no residual error)."""
        from fdars.advisor import build_diagnostics

        # No NaN cells; imputed == original → residual = 0
        perfect_input = {
            "data": [[0.0, 1.0, 2.0], [1.0, 1.0, 1.0]],
            "imputed": [[0.0, 1.0, 2.0], [1.0, 1.0, 1.0]],
            "argvals": _ARGVALS,
        }
        diag = build_diagnostics(perfect_input, method="represent")

        assert abs(diag["imputation_mae"]) < 1e-9, (
            f"expected 0.0 for perfect imputation, got {diag['imputation_mae']}"
        )

    def test_method_field_is_represent(self):
        """method field is always 'represent'."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")
        assert diag["method"] == "represent"

    def test_json_serialisable(self):
        """Output is JSON-serialisable when imputation context present."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")
        json.dumps(diag, sort_keys=True)  # must not raise

    def test_all_pre_existing_represent_keys_still_present(self):
        """Pre-existing represent keys are all still present when imputation provided."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")

        for key in (
            "method",
            "n_obs",
            "n_points",
            "argvals_min",
            "argvals_max",
            "argvals_spacing_mean",
            "argvals_spacing_std",
            "is_uniform_grid",
            "data_range_min",
            "data_range_max",
            "data_range_mean",
        ):
            assert key in diag, f"pre-existing key {key!r} missing from output"

        assert diag["method"] == "represent"
        assert diag["n_obs"] == 2
        assert diag["n_points"] == 3


# ---------------------------------------------------------------------------
# Test 2: backward-compat — new keys are None when imputation context absent.
# ---------------------------------------------------------------------------

class TestImputationQualityBackwardCompat:
    """New imputation-quality keys default to None; pre-existing behavior unchanged."""

    def test_new_keys_are_none_when_no_imputed(self):
        """When no 'imputed' key in input, new keys are None (backward-compatible)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_PLAIN_INPUT, method="represent")

        assert diag.get("imputed_fraction") is None
        assert diag.get("imputation_mae") is None

    def test_pre_existing_keys_unchanged_when_no_imputed(self):
        """All pre-existing represent keys retain their computed values."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_PLAIN_INPUT, method="represent")

        assert diag["method"] == "represent"
        assert diag["n_obs"] == 2
        assert diag["n_points"] == 3
        assert abs(diag["argvals_min"] - 0.0) < 1e-9
        assert abs(diag["argvals_max"] - 1.0) < 1e-9
        assert diag["is_uniform_grid"] is True

    def test_new_keys_are_none_when_no_data_at_all(self):
        """Minimal input without data returns None for new keys and does not crash."""
        from fdars.advisor import build_diagnostics

        # A result dict with no data key at all (edge case)
        diag = build_diagnostics({"converged": True}, method="represent")

        assert diag.get("imputed_fraction") is None
        assert diag.get("imputation_mae") is None
        assert diag["method"] == "represent"


# ---------------------------------------------------------------------------
# Test 3: determinism — byte-identical json.dumps + no numpy scalars.
# ---------------------------------------------------------------------------

class TestImputationQualityDeterministic:
    """Verify the imputation-quality branch is deterministic and numpy-scalar-free."""

    def test_imputation_quality_deterministic(self):
        """Two calls on the same input produce equal dicts AND byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics

        d1 = build_diagnostics(_IMPUTED_INPUT, method="represent")
        d2 = build_diagnostics(_IMPUTED_INPUT, method="represent")

        assert d1 == d2, "Two calls produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between calls"

    def test_imputation_quality_no_numpy_scalars(self):
        """Recursive walker: no numpy scalar leaks into the output dict."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")

        def check_no_numpy(obj):
            assert not isinstance(obj, np.generic), (
                f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
            )
            if isinstance(obj, dict):
                for v in obj.values():
                    check_no_numpy(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_no_numpy(v)

        check_no_numpy(diag)


# ---------------------------------------------------------------------------
# Test 4: grounding — imputation_mae is discoverable via _extract_numbers.
# ---------------------------------------------------------------------------

class TestImputationQualityGrounding:
    """Verify grounding: the fdars-computed imputation_mae appears in serialised diagnostics."""

    def test_imputation_mae_discoverable_via_extract_numbers(self):
        """imputation_mae from fdars.scoring.functional_mae is in json.dumps(diag)."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")
        diag_json = json.dumps(diag, sort_keys=True)
        found_numbers = set(_extract_numbers(diag_json))

        val = diag["imputation_mae"]
        assert val is not None, "imputation_mae is None — cannot verify grounding"

        # The value must appear in the serialised form
        val_str = str(val)
        assert any(
            val_str in n or n in val_str or abs(float(n) - val) < 1e-4
            for n in found_numbers
            if n.replace(".", "").isdigit()
        ), (
            f"imputation_mae={val} not discoverable in diagnostics json: "
            f"found_numbers={found_numbers!r}"
        )

    def test_imputed_fraction_discoverable(self):
        """imputed_fraction appears in json.dumps(diag)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_IMPUTED_INPUT, method="represent")
        diag_json = json.dumps(diag, sort_keys=True)

        frac = diag["imputed_fraction"]
        # The value should be serialised in the JSON output
        assert str(frac) in diag_json or f"{frac:.4f}" in diag_json or f"{frac:.3f}" in diag_json, (
            f"imputed_fraction={frac} not found in serialised diagnostics"
        )
