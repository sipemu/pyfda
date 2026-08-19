"""Regression tests for the advisor grounding guard (``_check_grounding``).

These lock the behaviour fixed in debug session ``advisor-grounding-false-pos``:
the guard used to reject the advisor's *own valid grounded output* on three
classes of citation, while its intent — rejecting fabricated statistics — must
be preserved.

The three false-positive classes (each MUST pass the guard):

1. **Index/label references** — ``"cluster 2"`` cites the integer ``2``, a
   cluster identifier (a numeric dict key), not a fabricated statistic.
2. **Rounded citations** — ``"near 5.4"`` for a stored value ``5.4034827``; a
   1-decimal citation must be grounded by rounding tolerance.
3. **Negative numbers** — ``"-28.9375"`` must match the stored ``-28.9375``
   (the old regex dropped the leading sign).

The true-positive (MUST still raise): a fabricated value absent from the
diagnostics at its cited precision (e.g. ``silhouette = 0.87``).

All tests are fully offline — no network, no anthropic package, no API key.
"""

from __future__ import annotations

import pytest

from fdars.advisor._schema import Advice, Recommendation
from fdars.advisor.providers._validate import (
    GroundingViolationError,
    _check_grounding,
    _extract_numbers,
    _flatten_diagnostics_numbers,
    _is_grounded_number,
)


# Diagnostics modelled on Canadian Weather k=4 clustering: numeric cluster-id
# keys, a NEGATIVE winter trough, and float values with precision beyond .4f.
DIAG = {
    "method": "clustering",
    "k": 4,
    "silhouette": 0.4158306524766444,
    "clusters": {
        "0": {"winter_trough": -28.9375, "summer_peak": 16.7},
        # winter_mean is NOT near 2 — so "cluster 2" can only ground via the
        # numeric key "2", never by rounding a nearby value.
        "2": {"winter_mean": 5.4034827, "summer_mean": 16.7},
    },
}


def _advice(evidence: list[str]) -> Advice:
    """Wrap evidence strings in a minimal single-recommendation Advice."""
    return Advice(
        interpretation="interpretation",
        recommendations=[
            Recommendation(
                action="action",
                kind="none",
                rationale="rationale",
                expected_effect="effect",
                evidence=evidence,
            )
        ],
        caveats=[],
    )


class TestGroundingFalsePositivesCleared:
    """The guard must accept the advisor's own valid grounded citations."""

    def test_index_reference_is_grounded(self):
        """Class 1: 'cluster 2' cites the integer cluster-id key 2, not a stat."""
        advice = _advice(
            ["cluster 2 shows winter mean near 5.4 and summer values near 16.7"]
        )
        # Must not raise.
        _check_grounding(advice, DIAG)

    def test_rounded_citation_is_grounded(self):
        """Class 2: a 1-decimal citation of a higher-precision stored value."""
        advice = _advice(["cluster 2 winter mean is near 5.4"])
        _check_grounding(advice, DIAG)

    def test_negative_number_is_grounded(self):
        """Class 3: a negative citation must match the stored negative value."""
        advice = _advice(["cluster 0 winter trough is approximately -28.9375"])
        _check_grounding(advice, DIAG)

    def test_negative_number_rounded_is_grounded(self):
        """A rounded negative citation ('-28.9') is grounded by tolerance."""
        advice = _advice(["cluster 0 winter trough near -28.9"])
        _check_grounding(advice, DIAG)

    def test_loose_citation_of_real_value_is_grounded(self):
        """Citing the real silhouette 0.4158… loosely as 0.42 is grounded."""
        advice = _advice(["overall silhouette is around 0.42"])
        _check_grounding(advice, DIAG)

    def test_qualitative_evidence_passes(self):
        """Evidence with no numbers is always grounded."""
        advice = _advice(["clusters separate cleanly with no overlap"])
        _check_grounding(advice, DIAG)


class TestGroundingTruePositivePreserved:
    """The guard must still reject genuinely fabricated statistics."""

    def test_fabricated_silhouette_raises(self):
        """A silhouette value absent at its cited precision must raise."""
        advice = _advice(["the silhouette score is 0.87"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, DIAG)

    def test_fabricated_k_raises(self):
        """A cluster count k=7 that appears nowhere must raise."""
        advice = _advice(["the analysis chose k=7 clusters"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, DIAG)

    def test_fabricated_precise_value_raises(self):
        """A precise value absent from diagnostics raises even if plausible."""
        advice = _advice(["cluster 0 trough is exactly -30.1234"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, DIAG)


class TestGroundingHelpers:
    """Unit-level checks on the extraction and matching primitives."""

    def test_extract_numbers_preserves_sign(self):
        """Leading '-' must be captured so negatives can match."""
        assert _extract_numbers("trough approx -28.9375") == ["-28.9375"]

    def test_extract_numbers_multiple_tokens(self):
        assert _extract_numbers("cluster 2 near 5.4") == ["2", "5.4"]

    def test_extract_numbers_ignores_hyphenated_words(self):
        """A hyphen inside a word is not a numeric sign."""
        assert _extract_numbers("well-separated into 3 groups") == ["3"]

    def test_flatten_includes_numeric_keys(self):
        nums = _flatten_diagnostics_numbers(DIAG)
        assert 0.0 in nums  # cluster-id key "0"
        assert 2.0 in nums  # cluster-id key "2"
        assert -28.9375 in nums  # negative value

    def test_is_grounded_number_precision_scaling(self):
        """Match tolerance follows the citation's own decimal precision."""
        nums = [5.4034827]
        assert _is_grounded_number("5.4", nums)  # 1 dp — 5.4 rounds to 5.4
        assert _is_grounded_number("5.40", nums)  # 2 dp — 5.40 rounds to 5.40
        assert _is_grounded_number("5.4035", nums)  # 4 dp — accurate citation
        assert not _is_grounded_number("5.41", nums)  # 2 dp — 5.40 != 5.41
        assert not _is_grounded_number("5.5", nums)  # 1 dp — 5.4 != 5.5


# ---------------------------------------------------------------------------
# Follow-up (debug session advisor-grounding-fp-part2): two MORE false-positive
# classes surfaced by the first real FPCA example (Tecator NIR spectra). The
# guard from d427da5 still rejected valid grounded citations that used:
#   4. positional array subscripts  — "explained_variance_ratio[2]=0.9987"
#   5. scientific notation           — "explained_variance_ratio[4]=5.22e-05"
# Diagnostics modelled on the actual FPCA diagnostics dict: list-valued fields
# and a sub-1e-4 explained-variance-ratio entry.
# ---------------------------------------------------------------------------

FPCA_DIAG = {
    "method": "fpca",
    "n_components": 10,
    "n_obs": 240,
    "eigenvalues": [52.91, 0.4685],
    "explained_variance_ratio": [
        0.9862,
        0.0087,
        0.0038,
        0.0012,
        5.2269939358072166e-05,  # the tiny sci-notation entry
    ],
    "cumulative_variance_explained": [0.9862, 0.9949, 0.9986859982552292, 0.9999, 1.0],
    "total_variance": 53.653,
    "phase_leakage_indicator": 0.01384,
    "phase_leakage_flagged": False,
}


class TestGroundingArraySubscriptCleared:
    """Class 4: positional list subscripts are references, not cited values."""

    def test_subscript_index_not_treated_as_value(self):
        """`[2]` is a positional index; only the value 0.9987 is a citation."""
        advice = _advice(
            ["cumulative_variance_explained[2]=0.9986859982552292 at component three"]
        )
        _check_grounding(advice, FPCA_DIAG)

    def test_subscript_with_rounded_value(self):
        """Subscript stripped; a rounded value citation still grounds."""
        advice = _advice(["cumulative_variance_explained[2] is about 0.9987"])
        _check_grounding(advice, FPCA_DIAG)

    def test_multidigit_subscript_stripped(self):
        """A two-digit index (e.g. [10]) is also stripped, not grounded."""
        advice = _advice(["eigenvalues[0]=52.91 dominates the spectrum"])
        _check_grounding(advice, FPCA_DIAG)

    def test_extract_numbers_strips_subscript(self):
        assert _extract_numbers("cumulative_variance_explained[2]=0.9987") == [
            "0.9987"
        ]

    def test_extract_numbers_strips_multidigit_subscript(self):
        assert _extract_numbers("field[10]=3.14") == ["3.14"]


class TestGroundingScientificNotationCleared:
    """Class 5: scientific-notation floats parse whole and match by tolerance."""

    def test_scientific_notation_exact_is_grounded(self):
        """The full-precision sci citation matches the stored float."""
        advice = _advice(
            ["explained_variance_ratio[4]=5.2269939358072166e-05 is negligible"]
        )
        _check_grounding(advice, FPCA_DIAG)

    def test_scientific_notation_rounded_is_grounded(self):
        """A rounded sci citation (5.22e-05) grounds via relative tolerance."""
        advice = _advice(
            ["the fifth component explains only 5.22e-05 of the variance"]
        )
        _check_grounding(advice, FPCA_DIAG)

    def test_scientific_notation_positive_exponent(self):
        """Sci notation with a positive exponent parses as one token."""
        # 5.22e+01 == 52.2 which rounds to eigenvalue 52.91? no — assert extract only.
        assert _extract_numbers("scale is 5.22e+01 units") == ["5.22e+01"]

    def test_extract_numbers_sci_single_token(self):
        assert _extract_numbers("ratio 5.2269939358072166e-05") == [
            "5.2269939358072166e-05"
        ]

    def test_extract_numbers_sci_no_decimal_point(self):
        """Sci notation without a mantissa decimal point still parses whole."""
        assert _extract_numbers("about 5e-05 of variance") == ["5e-05"]

    def test_is_grounded_number_sci_rejects_fabrication(self):
        """A fabricated small value at the same magnitude must NOT ground."""
        nums = [5.2269939358072166e-05]
        assert _is_grounded_number("5.22e-05", nums)  # grounded
        assert _is_grounded_number("5.2e-05", nums)  # grounded (coarser)
        assert not _is_grounded_number("9.99e-05", nums)  # fabricated
        assert not _is_grounded_number("5.30e-05", nums)  # fabricated at 2 dp


class TestGroundingFabricationsStillRejectedAfterFpcaFix:
    """Re-confirm the true-positive case survives the part-2 fix (no regression)."""

    def test_fabricated_silhouette_still_raises_on_fpca_diag(self):
        advice = _advice(["the silhouette score is 0.87"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, FPCA_DIAG)

    def test_fabricated_k_still_raises_on_fpca_diag(self):
        advice = _advice(["the analysis chose k=7 clusters"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, FPCA_DIAG)

    def test_fabricated_sci_value_raises(self):
        """A sci-notation value absent from diagnostics must still raise."""
        advice = _advice(
            ["the fifth component explains 9.99e-05 of the variance"]
        )
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, FPCA_DIAG)
