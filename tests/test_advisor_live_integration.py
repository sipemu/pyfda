"""Env-gated live integration tests for fdars.advisor providers.

Each test exercises one provider end-to-end using a real API call / real daemon.
All three provider tests are ``skipif``-gated on BOTH:
  1. ``FDARS_INTEGRATION == "1"`` (master gate for any live test in this file)
  2. A provider-specific credential / daemon check

Three additional aspect live tests (ASPECT-05) cover PACE-FPCA, elastic-multinomial,
and ITP end-to-end via the Anthropic provider (gated on ``ANTHROPIC_API_KEY``).

With no environment variables set, ``pytest -q`` MUST collect and SKIP all
tests cleanly with no ImportError (SDK imports are inside test bodies only,
never at module level).

Usage:
    # Run all live tests (requires keys + running Ollama):
    FDARS_INTEGRATION=1 OPENAI_API_KEY=sk-... GEMINI_API_KEY=AI... pytest tests/test_advisor_live_integration.py -q

    # Run aspect live tests (requires Anthropic key):
    FDARS_INTEGRATION=1 ANTHROPIC_API_KEY=sk-ant-... pytest tests/test_advisor_live_integration.py -q -k "aspect_live"

    # Without any env, all tests skip:
    pytest tests/test_advisor_live_integration.py -q  # expected: all skipped

Provider-specific gates:
    - OpenAI     : FDARS_INTEGRATION=="1" AND OPENAI_API_KEY is non-empty
    - Gemini     : FDARS_INTEGRATION=="1" AND GEMINI_API_KEY is non-empty
    - Ollama     : FDARS_INTEGRATION=="1" AND a reachable Ollama daemon at localhost:11434
    - Anthropic  : FDARS_INTEGRATION=="1" AND ANTHROPIC_API_KEY is non-empty (aspect tests)

Requirements covered:
    PROV-03   OpenAI live integration (gated)
    PROV-04   Ollama live integration (gated)
    PROV-05   Gemini live integration (gated)
    PROV-07   All provider tests skip cleanly in CI with no keys / no daemon
    ASPECT-05 PACE-FPCA, elastic-multinomial, ITP live coverage (env-gated, network-free in CI)
"""
from __future__ import annotations

import os
import socket

import pytest  # needed at module level for @pytest.mark.skipif decorators


# ---------------------------------------------------------------------------
# Helper: check whether an Ollama daemon is reachable
# ---------------------------------------------------------------------------

def _ollama_reachable(host: str = "localhost", port: int = 11434) -> bool:
    """Return True if a TCP connection to ``host:port`` succeeds within 0.5 s."""
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except (OSError, socket.timeout):
        return False


# ---------------------------------------------------------------------------
# Shared minimal diagnostics for integration tests
# ---------------------------------------------------------------------------

_MINIMAL_DIAGNOSTICS = {
    "method": "clustering",
    "k": 2,
    "cluster_sizes": [5, 5],
    "mean_amplitude_separation": 0.42,
}

_DOMAIN_CONTEXT = (
    "Integration test — minimal clustering result with k=2 clusters and "
    "mean amplitude separation 0.42."
)


# ---------------------------------------------------------------------------
# Module-level gate expressions (evaluated at collection time, no SDK imports)
# ---------------------------------------------------------------------------

_INTEGRATION_MASTER = os.environ.get("FDARS_INTEGRATION") == "1"

_OPENAI_GATE = _INTEGRATION_MASTER and bool(os.environ.get("OPENAI_API_KEY"))
_GEMINI_GATE = _INTEGRATION_MASTER and bool(os.environ.get("GEMINI_API_KEY"))
_OLLAMA_GATE = _INTEGRATION_MASTER and _ollama_reachable()
# Anthropic gate — used by ASPECT-05 live coverage (PACE-FPCA, elastic-multinomial, ITP)
_ANTHROPIC_GATE = _INTEGRATION_MASTER and bool(os.environ.get("ANTHROPIC_API_KEY"))


# ---------------------------------------------------------------------------
# Live test 1: OpenAI
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _OPENAI_GATE,
    reason=(
        "Live OpenAI test skipped — set FDARS_INTEGRATION=1 and OPENAI_API_KEY to run."
    ),
)
def test_live_openai_returns_validated_advice():
    """Live OpenAI integration: advise() returns a validated Advice via OpenAI.

    Requires:
        FDARS_INTEGRATION=1
        OPENAI_API_KEY=<valid key>
        openai SDK installed (pip install fdars[openai])
    """
    # All provider SDK imports deferred inside the test body so that collection
    # succeeds with no SDK installed.
    from fdars.advisor import advise  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415
    from fdars.advisor.providers._factory import resolve_provider  # noqa: PLC0415
    from fdars.advisor.providers._validate import ValidateAndRetry  # noqa: PLC0415

    provider = resolve_provider(provider="openai")
    assert isinstance(provider, ValidateAndRetry), (
        f"resolve_provider('openai') must return ValidateAndRetry; "
        f"got {type(provider).__name__!r}"
    )

    result = advise(
        _MINIMAL_DIAGNOSTICS,
        task="interpretation",
        domain_context=_DOMAIN_CONTEXT,
        provider="openai",
    )

    assert isinstance(result, Advice), (
        f"advise() with OpenAI must return an Advice instance; "
        f"got {type(result).__name__!r}"
    )
    assert result.interpretation, "Advice.interpretation must be non-empty"
    assert isinstance(result.recommendations, list), (
        "Advice.recommendations must be a list"
    )
    assert isinstance(result.caveats, list), "Advice.caveats must be a list"


# ---------------------------------------------------------------------------
# Live test 2: Gemini
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _GEMINI_GATE,
    reason=(
        "Live Gemini test skipped — set FDARS_INTEGRATION=1 and GEMINI_API_KEY to run."
    ),
)
def test_live_gemini_returns_validated_advice():
    """Live Gemini integration: advise() returns a validated Advice via GeminiProvider.

    Requires:
        FDARS_INTEGRATION=1
        GEMINI_API_KEY=<valid key>
        Python >=3.10 and google-genai installed (pip install fdars[gemini])
    """
    import sys  # noqa: PLC0415

    from fdars.advisor import advise  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415
    from fdars.advisor.providers._factory import resolve_provider  # noqa: PLC0415
    from fdars.advisor.providers._validate import ValidateAndRetry  # noqa: PLC0415

    if sys.version_info < (3, 10):
        pytest.skip("Gemini adapter requires Python >=3.10")

    provider = resolve_provider(provider="gemini")
    assert isinstance(provider, ValidateAndRetry), (
        f"resolve_provider('gemini') must return ValidateAndRetry; "
        f"got {type(provider).__name__!r}"
    )

    result = advise(
        _MINIMAL_DIAGNOSTICS,
        task="interpretation",
        domain_context=_DOMAIN_CONTEXT,
        provider="gemini",
    )

    assert isinstance(result, Advice), (
        f"advise() with Gemini must return an Advice instance; "
        f"got {type(result).__name__!r}"
    )
    assert result.interpretation, "Advice.interpretation must be non-empty"
    assert isinstance(result.recommendations, list), (
        "Advice.recommendations must be a list"
    )
    assert isinstance(result.caveats, list), "Advice.caveats must be a list"


# ---------------------------------------------------------------------------
# Live test 3: Ollama
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _OLLAMA_GATE,
    reason=(
        "Live Ollama test skipped — set FDARS_INTEGRATION=1 and start the Ollama "
        "daemon (https://ollama.com) on localhost:11434 to run."
    ),
)
def test_live_ollama_returns_validated_advice():
    """Live Ollama integration: advise() returns a validated Advice via OllamaProvider.

    Requires:
        FDARS_INTEGRATION=1
        Ollama daemon running on localhost:11434
        ollama installed (pip install fdars[ollama])
        The default model (llama3.2) pulled: ollama pull llama3.2
    """
    from fdars.advisor import advise  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415
    from fdars.advisor.providers._factory import resolve_provider  # noqa: PLC0415
    from fdars.advisor.providers._validate import ValidateAndRetry  # noqa: PLC0415

    provider = resolve_provider(provider="ollama")
    assert isinstance(provider, ValidateAndRetry), (
        f"resolve_provider('ollama') must return ValidateAndRetry; "
        f"got {type(provider).__name__!r}"
    )
    assert provider.supports_native_structured_output is False, (
        "OllamaProvider must route through ValidateAndRetry._fallback_with_retry "
        "(supports_native_structured_output=False)"
    )

    result = advise(
        _MINIMAL_DIAGNOSTICS,
        task="interpretation",
        domain_context=_DOMAIN_CONTEXT,
        provider="ollama",
    )

    assert isinstance(result, Advice), (
        f"advise() with Ollama must return an Advice instance; "
        f"got {type(result).__name__!r}"
    )
    assert result.interpretation, "Advice.interpretation must be non-empty"
    assert isinstance(result.recommendations, list), (
        "Advice.recommendations must be a list"
    )
    assert isinstance(result.caveats, list), "Advice.caveats must be a list"


# ---------------------------------------------------------------------------
# ASPECT-05 live tests — PACE-FPCA, elastic-multinomial, ITP (Anthropic provider)
#
# These tests exercise the three new aspect diagnostic branches end-to-end via a
# live Anthropic call.  They are named test_aspect_live_* (not test_live_*) so
# that the QUAL-02 contract assertion in test_aspect_provider_matrix.py (which
# counts exactly 3 test_live_* functions — one per provider) remains valid.
#
# Each test:
#   1. Builds diagnostics from a synthetic fixture (same shapes as Task 1 in 50-03)
#   2. Calls advise() against the live Anthropic provider
#   3. Asserts a valid grounded Advice is returned (no GroundingViolationError;
#      interpretation non-empty)
#
# Gate: FDARS_INTEGRATION=="1" AND ANTHROPIC_API_KEY is non-empty.
# CI stays network-free when neither env var is set.
# ---------------------------------------------------------------------------

# Reuse fixture shapes from test_aspect_provider_matrix.py (identical to Task 1)
_PACE_FPCA_FIXTURE = {
    "eigenvalues": [3.0, 1.5, 0.5],
    "ncomp": 2,
    "sigma2": 0.05,
    "fitted_lower": [[0.1, 0.2, 0.15], [0.05, 0.1, 0.08]],
    "fitted_upper": [[0.5, 0.6, 0.55], [0.45, 0.5, 0.48]],
}

_ELASTIC_FIXTURE = {
    "train_accuracy": 0.95,
    "n_classes": 3,
}

_ITP_FIXTURE = {
    "adjusted_pvalues": [0.02, 0.8, 0.9, 0.85, 0.6],
    "raw_pvalues": [0.01, 0.6, 0.7, 0.65, 0.4],
    "n_basis": 5,
    "n_perm": 99,
}


@pytest.mark.skipif(
    not _ANTHROPIC_GATE,
    reason=(
        "Live PACE-FPCA aspect test skipped — set FDARS_INTEGRATION=1 and "
        "ANTHROPIC_API_KEY to run (ASPECT-05)."
    ),
)
def test_aspect_live_pace_fpca():
    """ASPECT-05 live: advise() returns grounded Advice for PACE-FPCA diagnostics.

    Exercises the pace_fpca branch (eigenvalues/ncomp/sigma2/fitted_lower/fitted_upper)
    through the full advise() path including _check_grounding, via the Anthropic provider.

    Requires:
        FDARS_INTEGRATION=1
        ANTHROPIC_API_KEY=<valid key>
        anthropic SDK installed (pip install fdars[advisor])
    """
    from fdars.advisor import advise, build_diagnostics  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415

    # Build diagnostics offline — the pace_fpca branch populates the three new scalars
    diag = build_diagnostics(_PACE_FPCA_FIXTURE, method="fpca")

    # Verify the new ASPECT-01 scalars are present before the live call
    assert "pace_noise_signal_ratio" in diag, (
        "pace_noise_signal_ratio must be present in PACE-FPCA diagnostics"
    )
    assert "pace_truncated_rank_flagged" in diag, (
        "pace_truncated_rank_flagged must be present in PACE-FPCA diagnostics"
    )
    assert "pace_mean_prediction_band_width" in diag, (
        "pace_mean_prediction_band_width must be present in PACE-FPCA diagnostics"
    )

    result = advise(
        diag,
        task="interpretation",
        domain_context=(
            "Live aspect test — PACE-FPCA result with 3 eigenvalues, ncomp=2, sigma2=0.05."
        ),
        provider="anthropic",
    )

    assert isinstance(result, Advice), (
        f"advise() for PACE-FPCA must return Advice; got {type(result).__name__!r}"
    )
    assert result.interpretation, "Advice.interpretation must be non-empty"
    assert isinstance(result.recommendations, list), (
        "Advice.recommendations must be a list"
    )


@pytest.mark.skipif(
    not _ANTHROPIC_GATE,
    reason=(
        "Live elastic-multinomial aspect test skipped — set FDARS_INTEGRATION=1 and "
        "ANTHROPIC_API_KEY to run (ASPECT-05)."
    ),
)
def test_aspect_live_elastic_multinomial():
    """ASPECT-05 live: advise() returns grounded Advice for elastic-multinomial diagnostics.

    Exercises the elastic_multinomial branch (train_accuracy/n_classes) with a caller-
    supplied holdout_accuracy so overfitting_gap is populated and citable by the LLM.

    Requires:
        FDARS_INTEGRATION=1
        ANTHROPIC_API_KEY=<valid key>
        anthropic SDK installed (pip install fdars[advisor])
    """
    from fdars.advisor import advise, build_diagnostics  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415

    # Build diagnostics offline with holdout_accuracy so overfitting_gap is populated
    diag = build_diagnostics(
        _ELASTIC_FIXTURE,
        method="classification",
        holdout_accuracy=0.72,
    )

    # Verify the new ASPECT-02 scalars are present before the live call
    assert "overfitting_gap" in diag, (
        "overfitting_gap must be present in elastic-multinomial diagnostics"
    )
    assert "n_classes_flagged" in diag, (
        "n_classes_flagged must be present in elastic-multinomial diagnostics"
    )
    assert diag["overfitting_gap"] is not None, (
        "overfitting_gap must be non-None when holdout_accuracy is supplied"
    )

    result = advise(
        diag,
        task="interpretation",
        domain_context=(
            "Live aspect test — elastic-multinomial with train_accuracy=0.95, "
            "holdout_accuracy=0.72, n_classes=3."
        ),
        provider="anthropic",
    )

    assert isinstance(result, Advice), (
        f"advise() for elastic-multinomial must return Advice; "
        f"got {type(result).__name__!r}"
    )
    assert result.interpretation, "Advice.interpretation must be non-empty"
    assert isinstance(result.recommendations, list), (
        "Advice.recommendations must be a list"
    )


@pytest.mark.skipif(
    not _ANTHROPIC_GATE,
    reason=(
        "Live ITP aspect test skipped — set FDARS_INTEGRATION=1 and "
        "ANTHROPIC_API_KEY to run (ASPECT-05)."
    ),
)
def test_aspect_live_itp():
    """ASPECT-05 live: advise() returns grounded Advice for ITP diagnostics.

    Exercises the ITP branch (adjusted_pvalues vector → detection+localisation scalars)
    through the full advise() path including _check_grounding.  The raw p-value array
    is never stored — only the reduced native-float/int DETECTION and LOCALISATION scalars
    survive into the diagnostics dict.

    Requires:
        FDARS_INTEGRATION=1
        ANTHROPIC_API_KEY=<valid key>
        anthropic SDK installed (pip install fdars[advisor])
    """
    from fdars.advisor import advise, build_diagnostics  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415

    # Build diagnostics offline — the ITP branch reduces the vector to grounded scalars
    diag = build_diagnostics(_ITP_FIXTURE, method="inference")

    # Verify the new ASPECT-03 scalars are present before the live call
    assert "itp_min_adjusted_pvalue" in diag, (
        "itp_min_adjusted_pvalue (DETECTION) must be in ITP diagnostics"
    )
    assert "itp_n_significant_0.05" in diag, (
        "itp_n_significant_0.05 (LOCALISATION) must be in ITP diagnostics"
    )
    assert "itp_fraction_significant_0.05" in diag, (
        "itp_fraction_significant_0.05 (LOCALISATION) must be in ITP diagnostics"
    )
    # Confirm the raw array is NOT in the diagnostics (grounding + JSON invariant)
    assert "adjusted_pvalues" not in diag, (
        "raw adjusted_pvalues array must NOT be stored in diagnostics"
    )

    result = advise(
        diag,
        task="interpretation",
        domain_context=(
            "Live aspect test — ITP result with n_basis=5, n_perm=99, "
            "1 of 5 bases significant at alpha=0.05."
        ),
        provider="anthropic",
    )

    assert isinstance(result, Advice), (
        f"advise() for ITP must return Advice; got {type(result).__name__!r}"
    )
    assert result.interpretation, "Advice.interpretation must be non-empty"
    assert isinstance(result.recommendations, list), (
        "Advice.recommendations must be a list"
    )
