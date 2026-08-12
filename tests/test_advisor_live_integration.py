"""Env-gated live integration tests for fdars.advisor providers.

Each test exercises one provider end-to-end using a real API call / real daemon.
All three tests are ``skipif``-gated on BOTH:
  1. ``FDARS_INTEGRATION == "1"`` (master gate for any live test in this file)
  2. A provider-specific credential / daemon check

With no environment variables set, ``pytest -q`` MUST collect and SKIP all
three cleanly with no ImportError (SDK imports are inside test bodies only,
never at module level).

Usage:
    # Run all live tests (requires keys + running Ollama):
    FDARS_INTEGRATION=1 OPENAI_API_KEY=sk-... GEMINI_API_KEY=AI... pytest tests/test_advisor_live_integration.py -q

    # Without any env, all three skip:
    pytest tests/test_advisor_live_integration.py -q  # expected: 3 skipped

Provider-specific gates:
    - OpenAI  : FDARS_INTEGRATION=="1" AND OPENAI_API_KEY is non-empty
    - Gemini  : FDARS_INTEGRATION=="1" AND GEMINI_API_KEY is non-empty
    - Ollama  : FDARS_INTEGRATION=="1" AND a reachable Ollama daemon at localhost:11434

Requirements covered:
    PROV-03  OpenAI live integration (gated)
    PROV-04  Ollama live integration (gated)
    PROV-05  Gemini live integration (gated)
    PROV-07  All three skip cleanly in CI with no keys / no daemon
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
