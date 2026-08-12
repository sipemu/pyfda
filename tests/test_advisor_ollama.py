"""Offline Ollama provider tests for fdars.advisor.

All tests are network-free, key-free, and do not require the ollama SDK.
The fake ollama module is injected via sys.modules (monkeypatch.setitem) because
the real SDK is NOT installed in the test venv.  ``@patch("ollama.chat")`` is
intentionally NOT used — that form fails with ImportError when the package is
absent.

Requirements covered:
    PROV-04  Ollama adapter resolves and returns validated Advice (no API key)
    PROV-07  Missing [ollama] extra raises an actionable ImportError
    T-20-04  format= constrained decoding + ValidateAndRetry (retry + grounding)
    T-20-05  No conflicting generation-control params alongside format= (tested
             by asserting "think" is absent from chat call_args)
    T-20-06  Non-native path re-validates every dict; failure retries then raises
"""
from __future__ import annotations

import importlib
import json
import sys
import types

import pytest
from unittest.mock import MagicMock

from fdars.advisor._schema import Advice, Recommendation
from fdars.advisor.providers._validate import (
    GroundingViolationError,
    ValidateAndRetry,
    _check_grounding,
)

# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------

GOOD_ADVICE = Advice(
    interpretation="Clustering looks good.",
    recommendations=[
        Recommendation(
            action="Keep k=4.",
            kind="parameter",
            rationale="k=4 clusters show clear separation.",
            expected_effect="No change needed.",
            evidence=["k=4 clusters were identified."],
        )
    ],
    caveats=[],
)


def _make_fake_ollama(version: str = "0.6.2") -> types.ModuleType:
    """Return a fake ollama module whose ``chat`` attribute is a MagicMock."""
    fake = types.ModuleType("ollama")
    fake.chat = MagicMock()
    fake.__version__ = version
    return fake


def _make_chat_response(content: str) -> object:
    """Build a fake ``ollama.chat`` response with the given message content."""
    message = MagicMock()
    message.content = content
    response = MagicMock()
    response.message = message
    return response


@pytest.fixture()
def fake_ollama(monkeypatch):
    """Install a versioned fake ollama module and yield it.

    Clears any cached adapter/advisor imports so each test gets a fresh
    deferred-import resolution that picks up the injected fake module.
    """
    fake = _make_fake_ollama()
    monkeypatch.setitem(sys.modules, "ollama", fake)
    # Clear cached adapter so the deferred 'import ollama' fires fresh.
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.ollama", raising=False)
    yield fake


# ---------------------------------------------------------------------------
# Test 1: Returns raw dict (not an Advice instance)
# ---------------------------------------------------------------------------


def test_complete_structured_returns_raw_dict(fake_ollama, monkeypatch):
    """OllamaProvider.complete_structured returns a plain dict, not an Advice.

    Verifies the non-native path: the adapter returns json.loads(content) which
    is a dict; ValidateAndRetry._fallback_with_retry runs schema validation.
    """
    from fdars.advisor.providers.ollama import OllamaProvider

    good_json = json.dumps(GOOD_ADVICE.model_dump())
    fake_ollama.chat.return_value = _make_chat_response(good_json)

    provider = OllamaProvider()
    result = provider.complete_structured(
        Advice, [{"role": "user", "content": "diagnose"}], "system prompt"
    )

    assert isinstance(result, dict), (
        f"OllamaProvider.complete_structured must return a dict (raw), "
        f"not {type(result).__name__!r}"
    )
    assert not isinstance(result, Advice), (
        "OllamaProvider must NOT return a validated Advice instance directly; "
        "that is ValidateAndRetry's job."
    )


# ---------------------------------------------------------------------------
# Test 2: No conflicting generation-control params alongside format=
# ---------------------------------------------------------------------------


def test_no_conflicting_generation_param_in_call(fake_ollama, monkeypatch):
    """After complete_structured, chat call_args must not contain 'think'.

    Verifies T-20-05: no conflicting generation-control param is passed
    alongside format= (some Ollama builds silently disable format= when such
    params are present — Ollama issue #10929).
    """
    from fdars.advisor.providers.ollama import OllamaProvider

    good_json = json.dumps(GOOD_ADVICE.model_dump())
    fake_ollama.chat.return_value = _make_chat_response(good_json)

    provider = OllamaProvider()
    provider.complete_structured(
        Advice, [{"role": "user", "content": "x"}], "system"
    )

    call_kwargs = fake_ollama.chat.call_args[1]
    assert "think" not in call_kwargs, (
        f"chat() must not receive a 'think' kwarg (disables format= on some builds); "
        f"found keys: {list(call_kwargs.keys())!r}"
    )
    assert "format" in call_kwargs, (
        f"chat() must receive 'format' for constrained decoding; "
        f"found keys: {list(call_kwargs.keys())!r}"
    )


# ---------------------------------------------------------------------------
# Test 3: ValidateAndRetry validates the raw dict → returns Advice
# ---------------------------------------------------------------------------


def test_validate_and_retry_validates_raw_dict(fake_ollama, monkeypatch):
    """ValidateAndRetry wrapping OllamaProvider validates the raw dict into Advice.

    Tests the complete non-native fallback path:
      OllamaProvider → raw dict → ValidateAndRetry._fallback_with_retry
        → schema.model_validate(dict) → Advice instance
    """
    from fdars.advisor.providers.ollama import OllamaProvider

    good_json = json.dumps(GOOD_ADVICE.model_dump())
    fake_ollama.chat.return_value = _make_chat_response(good_json)

    provider = OllamaProvider()
    wrapper = ValidateAndRetry(provider)

    result = wrapper.complete_structured(
        Advice, [{"role": "user", "content": "x"}], "system"
    )

    assert isinstance(result, Advice), (
        f"ValidateAndRetry wrapping OllamaProvider must return a validated Advice; "
        f"got {type(result).__name__!r}"
    )
    assert result.interpretation == GOOD_ADVICE.interpretation


# ---------------------------------------------------------------------------
# Test 4: Retry then deterministic raise after MAX_RETRIES
# ---------------------------------------------------------------------------


def test_retry_then_raises_after_max_retries(fake_ollama, monkeypatch):
    """ValidateAndRetry raises ValueError after MAX_RETRIES when dict is always invalid.

    Verifies T-20-06: non-native path retries then raises deterministically;
    never fabricates a result.
    """
    from fdars.advisor.providers.ollama import OllamaProvider

    # Always returns a dict missing required fields — will fail Pydantic validation
    bad_json = json.dumps({"interpretation": "incomplete"})
    fake_ollama.chat.return_value = _make_chat_response(bad_json)

    provider = OllamaProvider()
    wrapper = ValidateAndRetry(provider)

    with pytest.raises(ValueError, match="failed to return valid structured output"):
        wrapper.complete_structured(
            Advice, [{"role": "user", "content": "x"}], "system"
        )

    # Exactly MAX_RETRIES calls were made
    assert fake_ollama.chat.call_count == ValidateAndRetry.MAX_RETRIES, (
        f"Expected {ValidateAndRetry.MAX_RETRIES} ollama.chat calls "
        f"before giving up, got {fake_ollama.chat.call_count}"
    )


# ---------------------------------------------------------------------------
# Test 5: Empty content raises ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("empty_content", [None, "", b"", 0])
def test_empty_content_raises_value_error(empty_content, fake_ollama, monkeypatch):
    """Given falsy message content, complete_structured raises ValueError.

    Verifies GROUND-04 parity: the adapter must not silently return an empty
    dict or raise a confusing json.JSONDecodeError.
    """
    from fdars.advisor.providers.ollama import OllamaProvider

    fake_ollama.chat.return_value = _make_chat_response(empty_content)

    provider = OllamaProvider()
    with pytest.raises((ValueError, Exception)):
        provider.complete_structured(
            Advice, [{"role": "user", "content": "x"}], "system"
        )


def test_none_content_raises_value_error_message(fake_ollama, monkeypatch):
    """Given None message content, ValueError mentions 'empty'."""
    from fdars.advisor.providers.ollama import OllamaProvider

    fake_ollama.chat.return_value = _make_chat_response(None)

    provider = OllamaProvider()
    with pytest.raises(ValueError, match="empty"):
        provider.complete_structured(
            Advice, [{"role": "user", "content": "x"}], "system"
        )


# ---------------------------------------------------------------------------
# Test 6: Missing-extra ImportError (actionable pip install hint)
# ---------------------------------------------------------------------------


def test_missing_extra_raises_importerror_with_pip_hint(monkeypatch):
    """When ollama SDK is absent, OllamaProvider() raises ImportError with pip hint.

    Sets sys.modules["ollama"] = None to simulate the [ollama] extra not being
    installed.  The error message must name 'pip install fdars[ollama]'.
    """
    monkeypatch.setitem(sys.modules, "ollama", None)  # type: ignore[assignment]
    # Clear cached adapter so the deferred _require_ollama() fires fresh.
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.ollama", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor", raising=False)

    import fdars.advisor  # reimport so _require_ollama is fresh
    import fdars.advisor.providers.ollama as m  # module-level import succeeds (deferred)

    with pytest.raises(ImportError, match=r"pip install fdars\[ollama\]"):
        m.OllamaProvider()


# ---------------------------------------------------------------------------
# Test 7: Grounding rejection via centralized check
# ---------------------------------------------------------------------------


def test_grounding_rejects_fabricated_evidence_ollama():
    """_check_grounding catches fabricated numbers on the Ollama path too.

    Verifies that the centralized grounding invariant is inherited by the
    Ollama path — the adapter itself does not need to implement it.
    """
    fabricated = Advice(
        interpretation="ok",
        recommendations=[
            Recommendation(
                action="a",
                kind="none",
                rationale="r",
                expected_effect="e",
                evidence=["k=999"],  # 999 not in diagnostics (k=4)
            )
        ],
        caveats=[],
    )
    diagnostics = {"k": 4}
    with pytest.raises(GroundingViolationError, match="999"):
        _check_grounding(fabricated, diagnostics)


def test_grounding_passes_correct_evidence_ollama():
    """_check_grounding passes when evidence cites values present in diagnostics."""
    advice = Advice(
        interpretation="ok",
        recommendations=[
            Recommendation(
                action="a",
                kind="parameter",
                rationale="r",
                expected_effect="e",
                evidence=["k=4 clusters identified"],
            )
        ],
        caveats=[],
    )
    diagnostics = {"k": 4}
    _check_grounding(advice, diagnostics)  # must not raise


# ---------------------------------------------------------------------------
# Test 8: resolve_provider("ollama") wiring
# ---------------------------------------------------------------------------


def test_resolve_provider_returns_ollama_provider(fake_ollama, monkeypatch):
    """resolve_provider('ollama') returns a ValidateAndRetry wrapper with .name=='ollama'."""
    from fdars.advisor.providers._factory import resolve_provider

    wrapper = resolve_provider(provider="ollama", model="llama3.2")

    assert isinstance(wrapper, ValidateAndRetry), (
        f"resolve_provider('ollama') must return a ValidateAndRetry, "
        f"got {type(wrapper).__name__!r}"
    )
    assert wrapper.name == "ollama", (
        f"wrapper.name must be 'ollama', got {wrapper.name!r}"
    )
    assert wrapper.supports_native_structured_output is False, (
        "OllamaProvider.supports_native_structured_output must be False "
        "(routes through _fallback_with_retry)"
    )


def test_resolve_provider_ollama_default_model(fake_ollama, monkeypatch):
    """resolve_provider('ollama') uses 'llama3.2' as the default model."""
    from fdars.advisor.providers._factory import resolve_provider, _DEFAULT_MODELS

    wrapper = resolve_provider(provider="ollama")
    assert wrapper.model == _DEFAULT_MODELS["ollama"]
    assert _DEFAULT_MODELS["ollama"] == "llama3.2"


def test_resolve_provider_ollama_host_from_base_url(fake_ollama, monkeypatch):
    """resolve_provider('ollama', base_url=...) threads the host into OllamaProvider.

    Verifies that resolved_base_url is forwarded as the 'host' constructor
    argument so that callers can point at a remote Ollama daemon.  We inspect
    the constructed adapter's _host attribute through the ValidateAndRetry
    wrapper's _provider reference.
    """
    from fdars.advisor.providers._factory import resolve_provider

    wrapper = resolve_provider(provider="ollama", base_url="http://remote-host:11434")

    # The wrapper._provider is the OllamaProvider instance.
    adapter = wrapper._provider
    assert adapter._host == "http://remote-host:11434", (
        f"OllamaProvider._host must be 'http://remote-host:11434', "
        f"got {adapter._host!r}"
    )


def test_resolve_provider_ollama_without_extra_raises_importerror(monkeypatch):
    """resolve_provider('ollama') with missing [ollama] extra raises actionable ImportError.

    This replaces the old Phase 19 test_unknown_provider_raises('ollama')
    expectation.  Now that 'ollama' is a recognised provider, the factory
    imports the adapter (succeeds — ollama.py exists), but OllamaProvider.__init__
    calls _require_ollama() which raises ImportError naming pip install fdars[ollama].

    Uses sys.modules["ollama"] = None to simulate the absent SDK.
    """
    monkeypatch.setitem(sys.modules, "ollama", None)  # type: ignore[assignment]
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.ollama", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers._factory", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor", raising=False)

    import fdars.advisor  # ensure _require_ollama is defined fresh
    from fdars.advisor.providers._factory import resolve_provider

    with pytest.raises(ImportError, match=r"pip install fdars\[ollama\]"):
        resolve_provider(provider="ollama")
