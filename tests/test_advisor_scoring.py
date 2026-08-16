"""Tests for the scoring diagnostics aspect (ADV-01, plan 28-01).

All tests are offline (no network, no ANTHROPIC_API_KEY required).
Tests mirror the structure of test_depth_deterministic in test_advisor.py:
- check_no_numpy recursive walker
- byte-identical json.dumps(sort_keys=True)
- grounding via _extract_numbers + json.dumps(diag)
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixed metric dicts used across tests (no RNG, no fdars call in the test —
# the caller-supplied-metrics contract means tests pass literal numbers).
# ---------------------------------------------------------------------------

_FULL_METRICS = {
    "functional_mae": 0.42,
    "functional_mse": 0.87,
    "functional_mape": 0.15,
    "functional_msle": 0.31,
    "functional_explained_variance": 0.93,
}

_PARTIAL_METRICS = {
    "functional_mae": 1.05,
    "functional_mse": 2.30,
    # mape / msle absent — tests None handling
    "functional_explained_variance": 0.62,
}

_SHORT_ALIAS_METRICS = {
    "mae": 0.55,
    "mse": 0.99,
    "mape": 0.22,
    "msle": 0.44,
    "explained_variance": 0.88,
}


# ---------------------------------------------------------------------------
# Test 1: basic correctness — method field, present metrics echoed as float,
# json.dumps succeeds.
# ---------------------------------------------------------------------------

class TestScoringBuildDiagnosticsBasic:
    """Verify the scoring diagnostics builder returns well-formed output."""

    def test_scoring_build_diagnostics_basic(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_FULL_METRICS, method="scoring")

        assert diag["method"] == "scoring"
        # Each present metric is echoed as a native float
        assert isinstance(diag["functional_mae"], float)
        assert abs(diag["functional_mae"] - 0.42) < 1e-9
        assert isinstance(diag["functional_mse"], float)
        assert abs(diag["functional_mse"] - 0.87) < 1e-9
        assert isinstance(diag["functional_explained_variance"], float)
        assert abs(diag["functional_explained_variance"] - 0.93) < 1e-9
        # json.dumps must succeed (no non-serialisable types)
        json.dumps(diag, sort_keys=True)

    def test_scoring_absent_keys_are_none(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_PARTIAL_METRICS, method="scoring")

        assert diag["method"] == "scoring"
        assert diag["functional_mape"] is None
        assert diag["functional_msle"] is None
        assert diag["functional_mae"] is not None

    def test_scoring_short_aliases_resolved(self):
        """Short-form keys (mae/mse/…) are accepted alongside long-form."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_SHORT_ALIAS_METRICS, method="scoring")

        assert diag["method"] == "scoring"
        assert isinstance(diag["functional_mae"], float)
        assert abs(diag["functional_mae"] - 0.55) < 1e-9
        assert isinstance(diag["functional_explained_variance"], float)
        assert abs(diag["functional_explained_variance"] - 0.88) < 1e-9

    def test_scoring_summary_fields_present(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_FULL_METRICS, method="scoring")

        assert "largest_error_metric" in diag
        assert "explained_variance_band" in diag

    def test_scoring_explained_variance_band_high(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics({"functional_explained_variance": 0.95}, method="scoring")
        assert diag["explained_variance_band"] == "high"

    def test_scoring_explained_variance_band_moderate(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics({"functional_explained_variance": 0.70}, method="scoring")
        assert diag["explained_variance_band"] == "moderate"

    def test_scoring_explained_variance_band_low(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics({"functional_explained_variance": 0.35}, method="scoring")
        assert diag["explained_variance_band"] == "low"

    def test_scoring_largest_error_metric_picks_max(self):
        """largest_error_metric names the error metric with the highest value."""
        from fdars.advisor import build_diagnostics

        # mse=2.30 is the largest
        diag = build_diagnostics(_PARTIAL_METRICS, method="scoring")
        assert diag["largest_error_metric"] == "functional_mse"

    def test_scoring_no_error_metrics_returns_none(self):
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics({"functional_explained_variance": 0.80}, method="scoring")
        assert diag["largest_error_metric"] is None
        assert diag["explained_variance_band"] == "moderate"


# ---------------------------------------------------------------------------
# Test 2: determinism — byte-identical json.dumps + no numpy scalars.
# Mirrors test_depth_deterministic in test_advisor.py exactly.
# ---------------------------------------------------------------------------

class TestScoringDeterministic:
    """Verify the scoring builder is deterministic and numpy-scalar-free."""

    def test_scoring_deterministic(self):
        """Two calls on the same input produce equal dicts AND byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics

        d1 = build_diagnostics(_FULL_METRICS, method="scoring")
        d2 = build_diagnostics(_FULL_METRICS, method="scoring")

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
# Test 3: grounding — every metric value in the built diagnostics is
# discoverable via _extract_numbers(json.dumps(diag)).
# ---------------------------------------------------------------------------

class TestScoringGrounding:
    """Verify the grounding invariant: builder echoes real fdars-supplied numbers."""

    def test_scoring_grounding(self):
        """Every numeric value in the built dict is recoverable from json.dumps(diag).

        This ensures the builder cites real caller-supplied metrics rather than
        fabricated numbers.  Uses _extract_numbers from the grounding validator
        to confirm each metric value's string form appears in the serialised dict.
        """
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers

        input_metrics = {
            "functional_mae": 0.42,
            "functional_mse": 0.87,
            "functional_mape": 0.15,
            "functional_msle": 0.31,
            "functional_explained_variance": 0.93,
        }
        diag = build_diagnostics(input_metrics, method="scoring")
        diag_json = json.dumps(diag, sort_keys=True)
        found_numbers = set(_extract_numbers(diag_json))

        # Each metric value we passed in must be discoverable in the serialised output
        for key, value in input_metrics.items():
            # Use the same formatting _extract_numbers would see
            value_str = str(value)
            # _extract_numbers uses \b\d+\.?\d*\b — check integer or decimal form
            assert any(value_str in n or n in value_str for n in found_numbers), (
                f"metric {key}={value} not discoverable in diagnostics json: "
                f"found_numbers={found_numbers!r}"
            )


# ---------------------------------------------------------------------------
# Test 4: offline — whole builder path runs with no network, no API key.
# ---------------------------------------------------------------------------

class TestScoringOfflineNoNetwork:
    """Verify build_diagnostics for scoring is fully offline."""

    def test_scoring_offline_no_network(self):
        """Builder path runs with no ANTHROPIC_API_KEY and no network import."""
        # Do NOT import anthropic/openai/requests — build_diagnostics must
        # not require any network module for the offline core.
        import sys

        # Ensure anthropic is NOT imported as a side-effect of build_diagnostics
        modules_before = set(sys.modules.keys())

        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_FULL_METRICS, method="scoring")

        # build_diagnostics import must not have triggered anthropic/openai
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
        assert diag["method"] == "scoring"
        json.dumps(diag, sort_keys=True)
