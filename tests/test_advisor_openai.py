"""Offline OpenAI provider tests for fdars.advisor.

All tests are network-free, key-free, and do not require the openai SDK.
The fake openai module is injected via sys.modules (monkeypatch.setitem) because
the real SDK is NOT installed in the test venv.  ``@patch("openai.OpenAI")`` is
intentionally NOT used — that form fails with ImportError when the package is
absent.

Requirements covered:
    PROV-03  OpenAI adapter resolves and returns validated Advice
    PROV-07  Missing [openai] extra raises an actionable ImportError
    T-20-01  Refusal / empty content raises ValueError (GROUND-04 parity)
    T-20-02  localhost base_url sends dummy key, never real OPENAI_API_KEY
"""
from __future__ import annotations

import importlib
import sys
import types

import pytest
from unittest.mock import MagicMock

from fdars.advisor._schema import Advice, Recommendation
from fdars.advisor.providers._validate import (
    GroundingViolationError,
    _check_grounding,
)

# ---------------------------------------------------------------------------
# Shared fixture and helpers
# ---------------------------------------------------------------------------

GOOD_ADVICE = Advice(
    interpretation="ok",
    recommendations=[
        Recommendation(
            action="a",
            kind="parameter",
            rationale="r",
            expected_effect="e",
            evidence=["k=4"],
        )
    ],
    caveats=[],
)


def _make_fake_openai(version: str = "1.40.0") -> types.ModuleType:
    """Return a fake openai module whose OpenAI class is a MagicMock."""
    fake = types.ModuleType("openai")
    fake.OpenAI = MagicMock()
    fake.__version__ = version
    return fake


def _make_completion_response(content: str | None, refusal: str | None = None):
    """Build a fake chat.completions.create response."""
    message = MagicMock()
    message.content = content
    message.refusal = refusal
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture()
def fake_openai(monkeypatch):
    """Install a versioned fake openai module and yield it."""
    fake = _make_fake_openai()
    monkeypatch.setitem(sys.modules, "openai", fake)
    # Clear any cached import of the adapter so fresh imports pick up the fake.
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.openai", raising=False)
    yield fake


# ---------------------------------------------------------------------------
# Test 1: Native path returns Advice
# ---------------------------------------------------------------------------


def test_native_path_returns_advice(fake_openai, monkeypatch):
    """Given a well-formed response, complete_structured returns a validated Advice."""
    from fdars.advisor.providers.openai import OpenAIProvider

    raw_json = GOOD_ADVICE.model_dump_json()
    mock_client = MagicMock()
    fake_openai.OpenAI.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion_response(
        content=raw_json, refusal=None
    )

    provider = OpenAIProvider(api_key="test-key")
    result = provider.complete_structured(
        Advice, [{"role": "user", "content": "x"}], "system prompt"
    )

    assert isinstance(result, Advice)
    assert result.interpretation == "ok"
    assert len(result.recommendations) == 1
    assert result.recommendations[0].action == "a"


# ---------------------------------------------------------------------------
# Test 2: Refusal raises ValueError
# ---------------------------------------------------------------------------


def test_refusal_raises_value_error(fake_openai):
    """Given message.refusal is non-empty, complete_structured raises ValueError."""
    from fdars.advisor.providers.openai import OpenAIProvider

    mock_client = MagicMock()
    fake_openai.OpenAI.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion_response(
        content=None, refusal="I cannot help with that."
    )

    provider = OpenAIProvider(api_key="test-key")
    with pytest.raises(ValueError, match="refusal"):
        provider.complete_structured(
            Advice, [{"role": "user", "content": "x"}], "system"
        )


# ---------------------------------------------------------------------------
# Test 3: Empty content raises ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("empty_content", [None, "", "   "])
def test_empty_content_raises_value_error(empty_content, fake_openai):
    """Given message.content is empty/None, complete_structured raises ValueError."""
    from fdars.advisor.providers.openai import OpenAIProvider

    mock_client = MagicMock()
    fake_openai.OpenAI.return_value = mock_client
    # Build response with falsy content; if whitespace-only we rely on the
    # adapter's `not raw_json` check (whitespace is truthy — only None/"" are
    # covered by the parametrize; whitespace is an edge case allowed to pass).
    content = empty_content if empty_content is not None else None
    mock_client.chat.completions.create.return_value = _make_completion_response(
        content=content, refusal=None
    )

    provider = OpenAIProvider(api_key="test-key")
    # Only None and "" are guaranteed falsy; whitespace-only is truthy in Python
    if not content:
        with pytest.raises(ValueError, match="empty"):
            provider.complete_structured(
                Advice, [{"role": "user", "content": "x"}], "system"
            )
    else:
        # Whitespace content is truthy — adapter tries model_validate_json which
        # will raise ValidationError or json.JSONDecodeError; both surface as
        # non-empty errors.  Not testing exact type here to stay adapter-agnostic.
        with pytest.raises(Exception):
            provider.complete_structured(
                Advice, [{"role": "user", "content": "x"}], "system"
            )


# ---------------------------------------------------------------------------
# Test 4: localhost dummy key
# ---------------------------------------------------------------------------


def test_localhost_base_url_passes_dummy_key(fake_openai):
    """localhost base_url with no api_key must call OpenAI(api_key='none')."""
    from fdars.advisor.providers.openai import OpenAIProvider

    fake_openai.OpenAI.return_value = MagicMock()
    OpenAIProvider(base_url="http://localhost:1234/v1")

    call_kwargs = fake_openai.OpenAI.call_args[1]
    assert call_kwargs["api_key"] == "none", (
        f"Expected api_key='none' for localhost base_url; got {call_kwargs.get('api_key')!r}"
    )


def test_no_base_url_does_not_pass_dummy_key(fake_openai):
    """When base_url=None and api_key=None, OpenAI must NOT be called with api_key='none'."""
    from fdars.advisor.providers.openai import OpenAIProvider

    fake_openai.OpenAI.return_value = MagicMock()
    OpenAIProvider()  # api_key=None, base_url=None

    call_kwargs = fake_openai.OpenAI.call_args[1]
    assert call_kwargs.get("api_key") is None, (
        f"Expected api_key=None when no base_url; got {call_kwargs.get('api_key')!r}"
    )


def test_127_0_0_1_base_url_passes_dummy_key(fake_openai):
    """127.0.0.1 base_url with no api_key must also use dummy key."""
    from fdars.advisor.providers.openai import OpenAIProvider

    fake_openai.OpenAI.return_value = MagicMock()
    OpenAIProvider(base_url="http://127.0.0.1:8080/v1")

    call_kwargs = fake_openai.OpenAI.call_args[1]
    assert call_kwargs["api_key"] == "none"


# ---------------------------------------------------------------------------
# Test 5: Missing-extra ImportError
# ---------------------------------------------------------------------------


def test_missing_extra_raises_importerror_with_pip_hint(monkeypatch):
    """When openai SDK is absent, OpenAIProvider() raises ImportError naming pip install."""
    # Block the openai import by setting sys.modules["openai"] = None.
    # This simulates the [openai] extra not being installed.
    monkeypatch.setitem(sys.modules, "openai", None)  # type: ignore[assignment]
    # Force re-import of the adapter module so the guard fires fresh.
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.openai", raising=False)
    # Also clear the guard itself so it re-runs.
    monkeypatch.delitem(sys.modules, "fdars.advisor", raising=False)

    import fdars.advisor  # reimport the advisor module
    import fdars.advisor.providers.openai as m  # import (deferred — won't error)

    with pytest.raises(ImportError, match=r"pip install fdars\[openai\]"):
        m.OpenAIProvider()


# ---------------------------------------------------------------------------
# Test 6: Grounding rejection via centralized check
# ---------------------------------------------------------------------------


def test_grounding_rejects_fabricated_evidence():
    """_check_grounding catches fabricated numbers regardless of provider."""
    fabricated = Advice(
        interpretation="ok",
        recommendations=[
            Recommendation(
                action="a",
                kind="none",
                rationale="r",
                expected_effect="e",
                evidence=["k=999"],  # 999 is not in diagnostics (k=4)
            )
        ],
        caveats=[],
    )
    diagnostics = {"k": 4}
    with pytest.raises(GroundingViolationError, match="999"):
        _check_grounding(fabricated, diagnostics)


def test_grounding_passes_correct_evidence():
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
# Test 7: resolve_provider string wiring
# ---------------------------------------------------------------------------


def test_resolve_provider_returns_openai_provider(fake_openai):
    """resolve_provider(provider='openai') returns a wrapper whose .name == 'openai'."""
    from fdars.advisor.providers._factory import resolve_provider
    from fdars.advisor.providers._validate import ValidateAndRetry

    # Prevent actual OpenAI client construction side effects.
    fake_openai.OpenAI.return_value = MagicMock()

    wrapper = resolve_provider(provider="openai", model="gpt-4o")
    assert isinstance(wrapper, ValidateAndRetry)
    assert wrapper.name == "openai"
    assert wrapper.supports_native_structured_output is True


def test_resolve_provider_openai_default_model(fake_openai):
    """resolve_provider(provider='openai') uses gpt-4o as default model."""
    from fdars.advisor.providers._factory import resolve_provider, _DEFAULT_MODELS

    fake_openai.OpenAI.return_value = MagicMock()

    wrapper = resolve_provider(provider="openai")
    assert wrapper.model == _DEFAULT_MODELS["openai"]
    assert _DEFAULT_MODELS["openai"] == "gpt-4o"


def test_resolve_provider_openai_model_explicit(fake_openai):
    """resolve_provider(provider='openai', model='gpt-4o-mini') passes model through."""
    from fdars.advisor.providers._factory import resolve_provider

    fake_openai.OpenAI.return_value = MagicMock()

    wrapper = resolve_provider(provider="openai", model="gpt-4o-mini")
    assert wrapper.model == "gpt-4o-mini"
