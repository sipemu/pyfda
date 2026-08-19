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
