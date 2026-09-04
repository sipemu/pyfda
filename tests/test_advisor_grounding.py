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


# ---------------------------------------------------------------------------
# Redesign (debug session advisor-grounding-redesign): the SIXTH — and general —
# false-positive class. Two prior patches (dict-key ints, array subscripts) were
# special cases of one problem: digit-runs that belong to an IDENTIFIER, not to a
# cited value, were extracted and validated. This surfaced on the depth and spm
# aspects, whose field names embed digits:
#   depth_q90 / depth_q10  → spurious '90' / '10' (quantile labels)
#   t2_max / t2_limit / t2_mean → spurious '2'    (Hotelling T²)
# Fix: _NUMBER_RE's lookbehind now rejects a numeric literal glued to a preceding
# identifier char (letter/underscore/digit/dot), so only the VALUE (right of the
# =/:/space) is ever extracted. Fabrications in value position must STILL raise.
# ---------------------------------------------------------------------------

# Diagnostics modelled on the actual depth aspect (Fraiman–Muniz quantile band)
# and spm aspect (Hotelling T² monitoring): field NAMES embed digits, values do
# not equal those embedded digits.
DEPTH_DIAG = {
    "method": "depth",
    "depth_q10": 0.5,
    "depth_q90": 0.7845009784735811,
    "median_depth": 0.6421,
    "n_obs": 35,
}

SPM_DIAG = {
    "method": "spm",
    "t2_max": 22.451286505855457,
    "t2_mean": 8.1037,
    "t2_limit": 15.086,
    "spe_max": 3.14,
    "arl0": 200,
    "n_flagged": 4,
}


class TestGroundingDigitsInIdentifierCleared:
    """Class 6: digit-runs inside field NAMES are never treated as cited values."""

    def test_depth_q90_identifier_digits_not_grounded(self):
        """`depth_q90=0.7845…` cites 0.7845…, not the label digits 90."""
        advice = _advice(["depth_q90=0.7845009784735811 marks the upper band"])
        _check_grounding(advice, DEPTH_DIAG)

    def test_depth_q10_identifier_digits_not_grounded(self):
        """`depth_q10=0.5` cites 0.5, not the label digits 10."""
        advice = _advice(["depth_q10=0.5 marks the lower band"])
        _check_grounding(advice, DEPTH_DIAG)

    def test_depth_quantiles_in_prose(self):
        """Both quantile labels cited in prose still ground on their values."""
        advice = _advice(
            ["the depth_q10 floor is 0.5 while depth_q90 reaches 0.7845"]
        )
        _check_grounding(advice, DEPTH_DIAG)

    def test_hotelling_t2_field_digit_not_grounded(self):
        """`t2_max: 22.45…` cites 22.45…, not the Hotelling-T² label digit 2."""
        advice = _advice(["t2_max: 22.451286505855457 exceeds the limit"])
        _check_grounding(advice, SPM_DIAG)

    def test_hotelling_t2_multiple_fields(self):
        """t2_max / t2_mean / t2_limit all cited; only their values are checked."""
        advice = _advice(
            ["t2_max is 22.451286505855457, t2_mean is 8.1037, t2_limit is 15.086"]
        )
        _check_grounding(advice, SPM_DIAG)

    def test_arl0_identifier_digit_not_grounded(self):
        """`arl0=200`: the label's trailing 0 must not be a spurious citation."""
        advice = _advice(["arl0=200 is the in-control run length"])
        _check_grounding(advice, SPM_DIAG)

    def test_extract_numbers_skips_identifier_digits(self):
        """Unit: the label digits of t2_/q90/q10 are never extracted."""
        assert _extract_numbers("t2_max: 22.451286505855457") == [
            "22.451286505855457"
        ]
        assert _extract_numbers("depth_q90=0.7845009784735811") == [
            "0.7845009784735811"
        ]
        assert _extract_numbers("depth_q10=0.5") == ["0.5"]
        assert _extract_numbers("arl0=200") == ["200"]

    def test_extract_numbers_glued_trailing_digits_skipped(self):
        """A digit-run glued to a preceding identifier (no separator) is skipped."""
        # 'chi2' / 'pc1' style: trailing label digits must not leak as citations.
        assert _extract_numbers("component pc1 explains most variance") == []
        assert _extract_numbers("the chi2 statistic is large") == []


class TestGroundingFabricatedValueInValuePositionStillRaises:
    """The redesign must NOT blind the guard to a fabricated right-hand value.

    The identifier (`t2_max`) is legitimate, but the value to the RIGHT of the
    separator is fabricated — value-position extraction must still surface it.
    """

    def test_fabricated_value_after_legit_identifier_raises(self):
        """`t2_max = 999.9` when no diagnostic equals 999.9 must raise."""
        advice = _advice(["t2_max = 999.9 breaches the control limit"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, SPM_DIAG)

    def test_fabricated_depth_quantile_value_raises(self):
        """`depth_q90 = 0.99` when the stored value is 0.7845… must raise."""
        advice = _advice(["depth_q90 = 0.99 marks the upper band"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, DEPTH_DIAG)

    def test_fabricated_value_in_prose_after_digit_field_raises(self):
        """Prose citing t2_max then a fabricated number still raises."""
        advice = _advice(["t2_max reaches 77.7 at the worst sample"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, SPM_DIAG)

    def test_fabricated_k_still_raises_on_spm_diag(self):
        """A fabricated k=7 (no such diagnostic) still raises on spm diagnostics."""
        advice = _advice(["the analysis chose k=7 groups"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, SPM_DIAG)


# ---------------------------------------------------------------------------
# Phase 72 additions: grounding coverage for new aspects — fts and frechet.
#
# These classes lock ADV-01: every value emitted by build_diagnostics for the
# new aspects is a native Python scalar (float/int/bool/list/None), accepted
# by _check_grounding without GroundingViolationError, while fabricated values
# still raise.
# ---------------------------------------------------------------------------

import sys  # needed by the LLM-free test at the bottom


# Build real fts diagnostics via the shipped aspect builder.
# The ftsm fixture is representative: it exercises ncomp, n_obs, fitted_rmse,
# ar_sigma2_max — all converted to native Python types by _build_fts_diagnostics.
def _make_fts_diag() -> dict:
    import numpy as np
    from fdars import fts
    from fdars.advisor import build_diagnostics

    rng = np.random.default_rng(42)
    N, M = 40, 25
    data = rng.standard_normal((N, M))
    argvals = np.linspace(0.0, 1.0, M)
    ftsm_result = fts.ftsm(data, argvals, ncomp=3)
    return build_diagnostics(ftsm_result, method="fts")


FTS_DIAG = _make_fts_diag()


# Build real frechet diagnostics via the shipped aspect builder.
# The frechet_mean(spherical) fixture is representative: result is a 1-D
# numpy array that the builder converts to plain-Python ints/floats.
def _make_frechet_diag() -> dict:
    import numpy as np
    import fdars.frechet as frechet
    from fdars.advisor import build_diagnostics

    rng = np.random.default_rng(42)
    n_obs, d = 20, 3
    data_raw = [rng.standard_normal(d) for _ in range(n_obs)]
    data_sph = [v / np.linalg.norm(v) for v in data_raw]
    mean_result = frechet.frechet_mean(data_sph, "spherical", d)
    return build_diagnostics(mean_result, method="frechet")


FRECHET_DIAG = _make_frechet_diag()


class TestGroundingFtsAspect:
    """Grounding harness accepts real fts diagnostics; rejects fabrications.

    Locks ADV-01: build_diagnostics("fts") emits only native-scalar values.
    The _check_grounding path is the final proof that the grounding discipline
    holds end-to-end.
    """

    def test_fts_ncomp_citation_is_grounded(self):
        """A citation of the real ncomp (3) passes without raising."""
        advice = _advice([f"the fts model fitted ncomp={FTS_DIAG['ncomp']} components"])
        _check_grounding(advice, FTS_DIAG)

    def test_fts_n_obs_citation_is_grounded(self):
        """Citing the real observation count passes without raising."""
        advice = _advice([f"the dataset contains {FTS_DIAG['n_obs']} observations"])
        _check_grounding(advice, FTS_DIAG)

    def test_fts_fitted_rmse_citation_is_grounded(self):
        """Citing the real fitted_rmse (rounded) passes without raising."""
        # Use 2-decimal rounding — the grounding tolerance accepts this.
        rmse_cited = round(FTS_DIAG["fitted_rmse"], 2)
        advice = _advice([f"fitted RMSE is approximately {rmse_cited}"])
        _check_grounding(advice, FTS_DIAG)

    def test_fts_qualitative_evidence_passes(self):
        """Evidence with no numeric citations is always grounded."""
        advice = _advice(["the FTS model captures the dominant temporal patterns"])
        _check_grounding(advice, FTS_DIAG)

    def test_fts_fabricated_ncomp_raises(self):
        """A fabricated ncomp (99) not in the diagnostics must raise."""
        advice = _advice(["the fts model used ncomp=99 components"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, FTS_DIAG)

    def test_fts_fabricated_rmse_raises(self):
        """A fabricated fitted_rmse absent at its cited precision must raise."""
        advice = _advice(["fitted RMSE is 9.87"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, FTS_DIAG)


class TestGroundingFrechetAspect:
    """Grounding harness accepts real frechet diagnostics; rejects fabrications.

    Locks ADV-01: build_diagnostics("frechet") emits only native-scalar values
    for both the array (frechet_mean) and dict (anova/reg) result shapes.
    """

    def test_frechet_mean_ndim_citation_is_grounded(self):
        """Citing the real ndim (1 for spherical) passes without raising."""
        advice = _advice(
            [f"the Fréchet mean is a {FTS_DIAG['ncomp']}-component estimate"]  # ncomp from fts — use frechet
        )
        # Use frechet_mean_dim for the actual frechet citation.
        ndim = FRECHET_DIAG["frechet_mean_ndim"]
        advice = _advice([f"the Fréchet mean has ndim={ndim}"])
        _check_grounding(advice, FRECHET_DIAG)

    def test_frechet_mean_dim_citation_is_grounded(self):
        """Citing the real frechet_mean_dim (3) passes without raising."""
        dim = FRECHET_DIAG["frechet_mean_dim"]
        advice = _advice([f"the Fréchet mean lies in dimension {dim}"])
        _check_grounding(advice, FRECHET_DIAG)

    def test_frechet_qualitative_evidence_passes(self):
        """Evidence with no numbers is always grounded."""
        advice = _advice(["the Fréchet mean is the geodesic centroid of the sample"])
        _check_grounding(advice, FRECHET_DIAG)

    def test_frechet_fabricated_dim_raises(self):
        """A fabricated dimension (99) not in the diagnostics must raise."""
        advice = _advice(["the Fréchet mean lies in dimension 99"])
        with pytest.raises(GroundingViolationError):
            _check_grounding(advice, FRECHET_DIAG)


# ---------------------------------------------------------------------------
# LLM-free assertion for the number path (ADV-02 / SC3).
#
# The build_diagnostics number path MUST NOT import any LLM provider module
# (anthropic, openai, etc.).  The separation is architectural: provider
# imports are deferred into advise(), which is only called AFTER
# build_diagnostics returns.
#
# Two complementary proofs are required so the LLM-free property is verified
# regardless of runtime availability:
#
# Proof A (subprocess) — spawn a fresh Python interpreter, call
# build_diagnostics there, and assert "anthropic" is not in sys.modules.
# A clean interpreter has no pre-loaded modules, so any import triggered by
# build_diagnostics is immediately visible.
#
# Proof B (in-process fallback) — in the current process, pop any provider
# modules that may have been loaded by other tests earlier in the session,
# call build_diagnostics, and assert neither "anthropic" nor "openai" is in
# sys.modules afterward.  This fallback ensures the assertion never silently
# skips if subprocess is unavailable for any reason.
# ---------------------------------------------------------------------------

class TestLlmFreeNumberPath:
    """build_diagnostics never imports an LLM provider on the number path.

    Locks ADV-02 / SC3: the number path is provably LLM-free.  Both the
    subprocess proof and the in-process fallback must run — neither may
    silently skip.
    """

    def test_subprocess_no_anthropic_import(self):
        """Proof A: build_diagnostics in a fresh subprocess imports no anthropic."""
        import subprocess
        code = (
            "import sys, numpy as np, json\n"
            "from fdars import fts\n"
            "from fdars.advisor import build_diagnostics\n"
            "rng = np.random.default_rng(42)\n"
            "N, M = 40, 25\n"
            "data = rng.standard_normal((N, M))\n"
            "argvals = np.linspace(0.0, 1.0, M)\n"
            "result = fts.ftsm(data, argvals, ncomp=3)\n"
            "diag = build_diagnostics(result, method='fts')\n"
            "providers = ['anthropic', 'openai', 'google.generativeai']\n"
            "leaked = [p for p in providers if p in sys.modules]\n"
            "if leaked:\n"
            "    raise AssertionError(f'provider import leaked into number path: {leaked}')\n"
            "print('OK')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"Subprocess LLM-free check failed.\n"
            f"stdout: {result.stdout!r}\n"
            f"stderr: {result.stderr!r}"
        )
        assert "OK" in result.stdout

    def test_subprocess_no_anthropic_import_frechet(self):
        """Proof A (frechet): build_diagnostics in a fresh subprocess imports no anthropic."""
        import subprocess
        code = (
            "import sys, numpy as np, json\n"
            "import fdars.frechet as frechet\n"
            "from fdars.advisor import build_diagnostics\n"
            "rng = np.random.default_rng(42)\n"
            "n_obs, d = 20, 3\n"
            "data_raw = [rng.standard_normal(d) for _ in range(n_obs)]\n"
            "import numpy as _np\n"
            "data_sph = [v / _np.linalg.norm(v) for v in data_raw]\n"
            "mean_result = frechet.frechet_mean(data_sph, 'spherical', d)\n"
            "diag = build_diagnostics(mean_result, method='frechet')\n"
            "providers = ['anthropic', 'openai', 'google.generativeai']\n"
            "leaked = [p for p in providers if p in sys.modules]\n"
            "if leaked:\n"
            "    raise AssertionError(f'provider import leaked into number path: {leaked}')\n"
            "print('OK')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"Subprocess LLM-free check (frechet) failed.\n"
            f"stdout: {result.stdout!r}\n"
            f"stderr: {result.stderr!r}"
        )
        assert "OK" in result.stdout

    def test_inprocess_no_provider_import_after_fts(self):
        """Proof B (in-process fallback): build_diagnostics does not import provider modules.

        Pops any pre-loaded provider modules from sys.modules before calling
        build_diagnostics, then asserts they are absent afterward.  This proof
        runs in-process so the LLM-free property is verified even if subprocess
        is unavailable.
        """
        import numpy as np
        from fdars import fts
        from fdars.advisor import build_diagnostics

        # Remove any provider modules that earlier tests may have loaded
        # into the current process's sys.modules.
        _provider_keys = [
            k for k in list(sys.modules.keys())
            if k == "anthropic" or k.startswith("anthropic.")
            or k == "openai" or k.startswith("openai.")
            or k == "google.generativeai"
        ]
        _saved = {k: sys.modules.pop(k) for k in _provider_keys}

        try:
            rng = np.random.default_rng(42)
            N, M = 40, 25
            data = rng.standard_normal((N, M))
            argvals = np.linspace(0.0, 1.0, M)
            result = fts.ftsm(data, argvals, ncomp=3)
            build_diagnostics(result, method="fts")

            assert "anthropic" not in sys.modules, (
                "build_diagnostics imported 'anthropic' on the number path"
            )
            assert "openai" not in sys.modules, (
                "build_diagnostics imported 'openai' on the number path"
            )
        finally:
            # Restore previously loaded provider modules (test isolation).
            sys.modules.update(_saved)

    def test_inprocess_no_provider_import_after_frechet(self):
        """Proof B (in-process, frechet): build_diagnostics does not import provider modules.

        Same in-process fallback as above, exercising the frechet aspect path.
        """
        import numpy as np
        import fdars.frechet as frechet
        from fdars.advisor import build_diagnostics

        _provider_keys = [
            k for k in list(sys.modules.keys())
            if k == "anthropic" or k.startswith("anthropic.")
            or k == "openai" or k.startswith("openai.")
            or k == "google.generativeai"
        ]
        _saved = {k: sys.modules.pop(k) for k in _provider_keys}

        try:
            rng = np.random.default_rng(42)
            n_obs, d = 20, 3
            data_raw = [rng.standard_normal(d) for _ in range(n_obs)]
            data_sph = [v / np.linalg.norm(v) for v in data_raw]
            mean_result = frechet.frechet_mean(data_sph, "spherical", d)
            build_diagnostics(mean_result, method="frechet")

            assert "anthropic" not in sys.modules, (
                "build_diagnostics imported 'anthropic' on the number path (frechet)"
            )
            assert "openai" not in sys.modules, (
                "build_diagnostics imported 'openai' on the number path (frechet)"
            )
        finally:
            sys.modules.update(_saved)
