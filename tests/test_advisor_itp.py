"""Tests for the ITP (interval-wise testing procedure) branch of the inference
advisor aspect (ASPECT-03, Phase 50 Plan 02).

All tests are OFFLINE — no network, no ANTHROPIC_API_KEY, no fdars.inference
call.  The ITP result is a plain Python dict with a synthetic ``adjusted_pvalues``
list (matches the shape returned by ``itp_result_to_pydict`` in inference_mod.rs,
where adjusted_pvalues is a numpy 1-D array of shape (n_basis,)).

Detection vs localisation contract (PITFALLS #8):
  - Detection:    itp_min_adjusted_pvalue, itp_detected_at_0.05
  - Localisation: itp_n_significant_0.05, itp_fraction_significant_0.05,
                  itp_first_significant_basis
These MUST be emitted together — never a lone global scalar.
"""

from __future__ import annotations

import json

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def itp_significant_dict():
    """Synthetic ITP result dict: 1 of 5 basis intervals significant at 0.05."""
    return {
        "adjusted_pvalues": np.array([0.02, 0.80, 0.90, 0.85, 0.60]),
        "raw_pvalues": np.array([0.01, 0.70, 0.80, 0.75, 0.50]),
        "basis_type": "fourier",
        "n_basis": 5,
        "n_perm": 99,
    }


@pytest.fixture
def itp_none_significant_dict():
    """Synthetic ITP result dict: no basis interval significant at 0.05."""
    return {
        "adjusted_pvalues": np.array([0.10, 0.80, 0.90, 0.85, 0.60]),
        "raw_pvalues": np.array([0.08, 0.70, 0.80, 0.75, 0.50]),
        "basis_type": "fourier",
        "n_basis": 5,
        "n_perm": 99,
    }


@pytest.fixture
def itp_plain_list_dict():
    """Synthetic ITP result with adjusted_pvalues as a plain Python list (no numpy)."""
    return {
        "adjusted_pvalues": [0.02, 0.80, 0.90],
        "raw_pvalues": [0.01, 0.70, 0.80],
        "basis_type": "bspline",
        "n_basis": 3,
        "n_perm": 99,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_no_numpy(obj):
    """Fail if any value in obj is a numpy scalar (np.generic subclass)."""
    assert not isinstance(obj, np.generic), (
        f"numpy scalar leaked into output: {type(obj)!r} = {obj!r}"
    )
    if isinstance(obj, dict):
        for v in obj.values():
            check_no_numpy(v)
    elif isinstance(obj, list):
        for v in obj:
            check_no_numpy(v)


# ---------------------------------------------------------------------------
# TestItpShapeDetection — basic build_diagnostics routing
# ---------------------------------------------------------------------------

class TestItpShapeDetection:
    """ITP result is routed to the ITP branch, not TestResult or ToleranceBand."""

    def test_method_field(self, itp_significant_dict):
        """build_diagnostics on ITP dict returns method == 'inference'."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert diag["method"] == "inference"

    def test_itp_result_present_true(self, itp_significant_dict):
        """itp_result_present must be True for an ITP result."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert diag["itp_result_present"] is True

    def test_itp_result_present_false_for_test_result(self):
        """itp_result_present must be False (not present) for a TestResult dict."""
        from fdars.advisor import build_diagnostics
        test_result = {"p_value": 0.03, "statistic": 4.2, "n_perm": 99}
        diag = build_diagnostics(test_result, method="inference")
        assert diag["itp_result_present"] is False

    def test_adjusted_pvalues_not_in_returned_diag(self, itp_significant_dict):
        """The raw adjusted_pvalues array must NOT be stored in the returned diag."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert "adjusted_pvalues" not in diag, (
            "adjusted_pvalues array must be reduced to scalars, never echoed"
        )

    def test_raw_pvalues_not_in_returned_diag(self, itp_significant_dict):
        """The raw raw_pvalues array must NOT be stored in the returned diag."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert "raw_pvalues" not in diag, (
            "raw_pvalues array must not be stored in the diagnostics dict"
        )


# ---------------------------------------------------------------------------
# TestItpDetectionScalars — DETECTION branch (whether any interval is significant)
# ---------------------------------------------------------------------------

class TestItpDetectionScalars:
    """Detection scalars: itp_min_adjusted_pvalue and itp_detected_at_0.05."""

    def test_detection_min_pvalue_significant(self, itp_significant_dict):
        """itp_min_adjusted_pvalue must equal 0.02 for the significant fixture."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert abs(diag["itp_min_adjusted_pvalue"] - 0.02) < 1e-12

    def test_detection_min_pvalue_is_native_float(self, itp_significant_dict):
        """itp_min_adjusted_pvalue must be a native Python float (not numpy scalar)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert type(diag["itp_min_adjusted_pvalue"]) is float

    def test_detection_detected_at_0_05_true(self, itp_significant_dict):
        """itp_detected_at_0.05 must be True when min adjusted p < 0.05."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert diag["itp_detected_at_0.05"] is True

    def test_detection_detected_at_0_05_false(self, itp_none_significant_dict):
        """itp_detected_at_0.05 must be False when min adjusted p >= 0.05."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_none_significant_dict, method="inference")
        assert diag["itp_detected_at_0.05"] is False

    def test_detection_min_pvalue_none_significant(self, itp_none_significant_dict):
        """itp_min_adjusted_pvalue is the minimum over all intervals (0.10 here)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_none_significant_dict, method="inference")
        assert abs(diag["itp_min_adjusted_pvalue"] - 0.10) < 1e-12


# ---------------------------------------------------------------------------
# TestItpLocalisationScalars — LOCALISATION branch (where and how many)
# ---------------------------------------------------------------------------

class TestItpLocalisationScalars:
    """Localisation scalars: count, fraction, first significant basis index."""

    def test_localisation_n_significant(self, itp_significant_dict):
        """itp_n_significant_0.05 must equal 1 (one of five intervals significant)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert diag["itp_n_significant_0.05"] == 1

    def test_localisation_n_significant_is_native_int(self, itp_significant_dict):
        """itp_n_significant_0.05 must be a native Python int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert type(diag["itp_n_significant_0.05"]) is int

    def test_localisation_fraction_significant(self, itp_significant_dict):
        """itp_fraction_significant_0.05 must equal 0.2 (1 of 5 = 0.2)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert abs(diag["itp_fraction_significant_0.05"] - 0.2) < 1e-12

    def test_localisation_fraction_is_native_float(self, itp_significant_dict):
        """itp_fraction_significant_0.05 must be a native Python float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert type(diag["itp_fraction_significant_0.05"]) is float

    def test_localisation_first_significant_basis(self, itp_significant_dict):
        """itp_first_significant_basis must equal 0 (index of the first significant)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert diag["itp_first_significant_basis"] == 0

    def test_localisation_first_significant_basis_is_native_int(self, itp_significant_dict):
        """itp_first_significant_basis must be a native Python int when significant."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert type(diag["itp_first_significant_basis"]) is int

    def test_localisation_n_significant_zero(self, itp_none_significant_dict):
        """itp_n_significant_0.05 must equal 0 when no intervals significant."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_none_significant_dict, method="inference")
        assert diag["itp_n_significant_0.05"] == 0

    def test_localisation_fraction_zero(self, itp_none_significant_dict):
        """itp_fraction_significant_0.05 must equal 0.0 when no intervals significant."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_none_significant_dict, method="inference")
        assert diag["itp_fraction_significant_0.05"] == 0.0

    def test_localisation_first_basis_none(self, itp_none_significant_dict):
        """itp_first_significant_basis must be None when no intervals significant."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_none_significant_dict, method="inference")
        assert diag["itp_first_significant_basis"] is None

    def test_detection_and_localisation_all_present(self, itp_significant_dict):
        """All five ITP detection+localisation scalars must be non-None on a significant fixture."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert diag["itp_min_adjusted_pvalue"] is not None
        assert diag["itp_detected_at_0.05"] is not None
        assert diag["itp_n_significant_0.05"] is not None
        assert diag["itp_fraction_significant_0.05"] is not None
        # itp_first_significant_basis is None when none significant — valid for 0 count
        # but for the significant fixture it must be non-None
        assert diag["itp_first_significant_basis"] is not None


# ---------------------------------------------------------------------------
# TestItpGrounding — json.dumps clean + _check_grounding survives
# ---------------------------------------------------------------------------

class TestItpGrounding:
    """ITP diagnostics must be JSON-serialisable and survive _check_grounding."""

    def test_json_serialisable_significant(self, itp_significant_dict):
        """json.dumps must succeed on the significant ITP diag (no numpy scalar)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        json.dumps(diag)

    def test_json_serialisable_none_significant(self, itp_none_significant_dict):
        """json.dumps must succeed on the none-significant ITP diag."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_none_significant_dict, method="inference")
        json.dumps(diag)

    def test_no_numpy_scalars(self, itp_significant_dict):
        """No numpy scalar must appear anywhere in the output dict."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        check_no_numpy(diag)

    def test_check_grounding_survives(self, itp_significant_dict):
        """A hand-built Advice citing ITP scalars must pass _check_grounding."""
        from fdars.advisor import build_diagnostics
        from fdars.advisor._schema import Advice, Recommendation
        from fdars.advisor.providers._validate import _check_grounding
        diag = build_diagnostics(itp_significant_dict, method="inference")
        # Build a minimal Advice that cites grounded ITP values
        min_p = diag["itp_min_adjusted_pvalue"]   # 0.02
        n_sig = diag["itp_n_significant_0.05"]     # 1
        advice = Advice(
            interpretation=(
                f"ITP detected significance: itp_min_adjusted_pvalue={min_p:.2f}, "
                f"itp_n_significant_0.05={n_sig}."
            ),
            recommendations=[
                Recommendation(
                    action="Report significant interval",
                    kind="none",
                    rationale=(
                        f"itp_min_adjusted_pvalue={min_p:.2f} < 0.05 indicates detection; "
                        f"itp_n_significant_0.05={n_sig} interval(s) significant."
                    ),
                    expected_effect="No parameter change needed",
                    evidence=[
                        f"itp_min_adjusted_pvalue={min_p}",
                        f"itp_n_significant_0.05={n_sig}",
                    ],
                )
            ],
            caveats=["Significance is at alpha=0.05; interpret in context of sample size."],
        )
        # Must NOT raise — grounding check passes when every cited number
        # matches a value in the diagnostics dict
        _check_grounding(advice, diag)

    def test_plain_list_input_works(self, itp_plain_list_dict):
        """ITP builder handles adjusted_pvalues as a plain Python list (not numpy array)."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_plain_list_dict, method="inference")
        assert diag["itp_result_present"] is True
        assert diag["itp_n_basis"] == 3
        assert abs(diag["itp_min_adjusted_pvalue"] - 0.02) < 1e-12
        json.dumps(diag)
        check_no_numpy(diag)

    def test_type_fraction_is_float(self, itp_significant_dict):
        """type(diag['itp_fraction_significant_0.05']) must be exactly float."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert type(diag["itp_fraction_significant_0.05"]) is float

    def test_type_n_significant_is_int(self, itp_significant_dict):
        """type(diag['itp_n_significant_0.05']) must be exactly int."""
        from fdars.advisor import build_diagnostics
        diag = build_diagnostics(itp_significant_dict, method="inference")
        assert type(diag["itp_n_significant_0.05"]) is int


# ---------------------------------------------------------------------------
# TestItpPrimer — _ASPECT_PRIMERS["inference"] teaches whether-vs-where
# ---------------------------------------------------------------------------

class TestItpPrimer:
    """The inference primer must name the ITP scalars and teach whether-vs-where."""

    def test_primer_contains_localisation(self):
        """The 'inference' primer must contain 'localis' (localisation teaching)."""
        from fdars.advisor._prompts import _ASPECT_PRIMERS
        assert "localis" in _ASPECT_PRIMERS["inference"], (
            "The inference primer must contain 'localis' to teach the "
            "detection-vs-localisation (whether-vs-where) distinction"
        )

    def test_primer_names_n_significant(self):
        """The 'inference' primer must name 'itp_n_significant_0.05'."""
        from fdars.advisor._prompts import _ASPECT_PRIMERS
        assert "itp_n_significant_0.05" in _ASPECT_PRIMERS["inference"], (
            "The inference primer must reference itp_n_significant_0.05 "
            "so the LLM knows this scalar names localisation count"
        )
