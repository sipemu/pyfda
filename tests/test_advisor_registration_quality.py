"""Tests for registration-quality diagnostics on the alignment aspect (ADV-02, plan 28-02).

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
# Fixed literal arrays used across tests — no RNG, no side effects.
# ---------------------------------------------------------------------------

# A small registered dataset: 3 curves over 5 evaluation points.
# Chosen so n >= 2 (pairwise_correlation_score requires n >= 2).
_ARGVALS = [0.0, 0.25, 0.5, 0.75, 1.0]

_REGISTERED = [
    [0.0, 1.0, 2.0, 1.0, 0.0],
    [0.1, 1.1, 2.0, 0.9, 0.0],
    [0.05, 0.95, 1.95, 1.05, 0.05],
]

_REGISTERED_N2 = [
    [0.0, 1.0, 2.0, 1.0, 0.0],
    [0.1, 1.1, 2.0, 0.9, 0.0],
]

# Full input dict including a mean (simulates a karcher_mean result).
_ALIGNED_INPUT = {
    "aligned_data": _REGISTERED,
    "mean": [0.05, 1.02, 1.98, 0.98, 0.02],
    "converged": True,
    "n_iter": 5,
}

# Input without registered data — backward-compat: pre-existing keys only.
_KARCHER_ONLY_INPUT = {
    "converged": True,
    "n_iter": 3,
}


# ---------------------------------------------------------------------------
# Test 1: basic — registration-quality keys present and correct types.
# ---------------------------------------------------------------------------

class TestRegistrationQualityBasic:
    """Verify the registration-quality keys are added to the alignment builder."""

    def test_registration_scores_present_when_aligned_data_and_argvals_given(self):
        """build_diagnostics returns the three registration-quality scores."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )

        # New registration-quality keys must exist
        assert "least_squares_score" in diag
        assert "pairwise_correlation_score" in diag
        assert "sobolev_score" in diag

    def test_least_squares_score_is_finite_float(self):
        """least_squares_score is a finite native float (not numpy, not None)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )

        val = diag["least_squares_score"]
        assert val is not None, "least_squares_score should not be None when data supplied"
        assert isinstance(val, float), f"expected float, got {type(val)!r}"
        assert not isinstance(val, np.generic), "numpy scalar leaked into output"
        assert float("-inf") < val < float("inf"), "least_squares_score is not finite"

    def test_pairwise_correlation_score_is_finite_float_when_n_ge_2(self):
        """pairwise_correlation_score is a finite float when n >= 2."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            {"aligned_data": _REGISTERED_N2, "mean": [0.05, 1.02, 1.98, 0.98, 0.02]},
            method="alignment",
            argvals=_ARGVALS,
        )

        val = diag["pairwise_correlation_score"]
        assert val is not None
        assert isinstance(val, float)
        assert not isinstance(val, np.generic)
        assert float("-inf") < val < float("inf")

    def test_sobolev_score_is_finite_float(self):
        """sobolev_score is a finite float (lambda_=0.0, so identical to LS)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )

        val = diag["sobolev_score"]
        assert val is not None
        assert isinstance(val, float)
        assert not isinstance(val, np.generic)
        assert float("-inf") < val < float("inf")

    def test_all_pre_existing_alignment_keys_still_present(self):
        """Pre-existing alignment keys are all still present when new inputs provided."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )

        for key in (
            "method",
            "mean_length",
            "mean_min",
            "mean_max",
            "mean_avg",
            "mean_curve",
            "n_obs",
            "amplitude_distances",
            "phase_distances",
            "amplitude_mean",
            "amplitude_max",
            "phase_mean",
            "phase_max",
            "converged",
            "n_iter",
        ):
            assert key in diag, f"pre-existing key {key!r} missing from output"

        assert diag["method"] == "alignment"

    def test_json_serialisable(self):
        """Output is JSON-serialisable (no non-serialisable types)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )
        json.dumps(diag, sort_keys=True)  # must not raise


# ---------------------------------------------------------------------------
# Test 2: backward-compat — new keys are None when new inputs absent.
# ---------------------------------------------------------------------------

class TestRegistrationQualityBackwardCompat:
    """New registration-quality keys default to None; pre-existing behavior unchanged."""

    def test_new_keys_are_none_when_no_aligned_data(self):
        """When no aligned_data, new keys are None (backward-compatible)."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_KARCHER_ONLY_INPUT, method="alignment")

        assert diag["least_squares_score"] is None
        assert diag["pairwise_correlation_score"] is None
        assert diag["sobolev_score"] is None

    def test_pre_existing_keys_unchanged_when_no_aligned_data(self):
        """Pre-existing key values are byte-for-byte unchanged when no registered data."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(_KARCHER_ONLY_INPUT, method="alignment")

        assert diag["method"] == "alignment"
        assert diag["converged"] is True
        assert diag["n_iter"] == 3
        # All pre-existing keys that depend on aligned_data remain None
        assert diag["n_obs"] is None
        assert diag["amplitude_distances"] is None
        assert diag["phase_distances"] is None

    def test_new_keys_are_none_when_argvals_absent(self):
        """When argvals is not supplied, new registration-quality keys are None."""
        from fdars.advisor import build_diagnostics

        # aligned_data present but no argvals — existing behavior: amp/phase → None
        # new behavior: registration scores must also → None (not crash)
        diag = build_diagnostics(
            {"aligned_data": _REGISTERED, "mean": [0.0, 1.0, 2.0, 1.0, 0.0]},
            method="alignment",
            # no argvals kwarg
        )

        assert diag["least_squares_score"] is None
        assert diag["pairwise_correlation_score"] is None
        assert diag["sobolev_score"] is None


# ---------------------------------------------------------------------------
# Test 3: determinism — byte-identical json.dumps + no numpy scalars.
# Mirrors test_depth_deterministic in test_advisor.py.
# ---------------------------------------------------------------------------

class TestRegistrationQualityDeterministic:
    """Verify the registration-quality branch is deterministic and numpy-scalar-free."""

    def test_registration_quality_deterministic(self):
        """Two calls on the same input produce equal dicts AND byte-identical json.dumps."""
        from fdars.advisor import build_diagnostics

        d1 = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )
        d2 = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )

        assert d1 == d2, "Two calls produced different dicts"
        s1 = json.dumps(d1, sort_keys=True)
        s2 = json.dumps(d2, sort_keys=True)
        assert s1 == s2, "json.dumps not byte-identical between calls"

    def test_registration_quality_no_numpy_scalars(self):
        """Recursive walker: no numpy scalar leaks into the output dict."""
        from fdars.advisor import build_diagnostics

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )

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
# Test 4: grounding — each registration score is discoverable via _extract_numbers.
# ---------------------------------------------------------------------------

class TestRegistrationQualityGrounding:
    """Verify grounding: each fdars-computed score appears in the serialised diagnostics."""

    def test_registration_scores_discoverable_via_extract_numbers(self):
        """Each score value returned by fdars is discoverable in json.dumps(diag)."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor.providers._validate import _extract_numbers

        diag = build_diagnostics(
            _ALIGNED_INPUT, method="alignment", argvals=_ARGVALS
        )
        diag_json = json.dumps(diag, sort_keys=True)
        found_numbers = set(_extract_numbers(diag_json))

        # Each new registration score must be discoverable
        for key in ("least_squares_score", "sobolev_score"):
            val = diag[key]
            assert val is not None, f"{key} is None — cannot verify grounding"
            val_str = str(round(val, 4))
            assert any(val_str in n or n in val_str or abs(float(n) - val) < 1e-4
                       for n in found_numbers if n.replace(".", "").isdigit()), (
                f"{key}={val} not discoverable in diagnostics json: "
                f"found_numbers={found_numbers!r}"
            )

        # pairwise_correlation_score — verify it is in the JSON
        pc_val = diag["pairwise_correlation_score"]
        assert pc_val is not None
        assert str(pc_val) in diag_json or f"{pc_val:.4f}" in diag_json or f"{pc_val:.3f}" in diag_json, (
            f"pairwise_correlation_score={pc_val} not found in serialised diagnostics"
        )
