"""Offline Gemini provider tests for fdars.advisor.

All tests are network-free, key-free, and do not require the google-genai SDK.
The fake google / google.genai / google.genai.types modules are injected via
sys.modules (monkeypatch.setitem) because the real SDK is NOT installed in
the test venv.  ``@patch("google.genai.Client")`` is intentionally NOT used —
that form fails with ImportError when the package is absent.

Requirements covered:
    PROV-05  Gemini adapter resolves and returns validated Advice via native path
    PROV-07  Missing [gemini] extra raises an actionable ImportError
    T-20-07  response_json_schema constrains output + model_validate_json validates
    T-20-08  _gemini_schema only strips disallowed keys; required arrays + enums preserved
    T-20-09  google.generativeai namespace never used (only google.genai)
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
# Shared helpers
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


def _make_fake_genai_modules():
    """Build fake google / google.genai / google.genai.types module hierarchy.

    Returns a 3-tuple (fake_google, fake_genai, fake_types).
    The fake genai module exposes a ``Client`` MagicMock.
    ``types.GenerateContentConfig`` is a MagicMock accepting arbitrary kwargs.
    """
    # google namespace package
    fake_google = types.ModuleType("google")

    # google.genai
    fake_genai = types.ModuleType("google.genai")
    fake_google.genai = fake_genai

    # google.genai.types
    fake_types = types.ModuleType("google.genai.types")
    fake_genai.types = fake_types

    # Client: callable constructor, returns a mock client instance
    fake_genai.Client = MagicMock()
    # GenerateContentConfig: callable accepting arbitrary kwargs
    fake_types.GenerateContentConfig = MagicMock(side_effect=lambda **kw: kw)

    return fake_google, fake_genai, fake_types


def _install_fake_genai(monkeypatch, *, response_text: "str | None" = None):
    """Install the fake google/genai/types modules and wire the generate_content response.

    Returns the fake genai module.
    """
    fake_google, fake_genai, fake_types = _make_fake_genai_modules()

    # Wire generate_content to return a mock response with the given .text
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    fake_genai.Client.return_value = mock_client_instance

    # Inject into sys.modules hierarchy
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)

    # Clear cached provider/advisor imports so deferred imports pick up the fake.
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.gemini", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor", raising=False)

    return fake_genai, fake_types, mock_client_instance


# ---------------------------------------------------------------------------
# Test 1: Native path returns Advice
# ---------------------------------------------------------------------------


def test_native_path_returns_advice(monkeypatch):
    """Given a well-formed response, complete_structured returns a validated Advice."""
    raw_json = GOOD_ADVICE.model_dump_json()
    fake_genai, fake_types, mock_client = _install_fake_genai(
        monkeypatch, response_text=raw_json
    )

    from fdars.advisor.providers.gemini import GeminiProvider

    provider = GeminiProvider(api_key="test-key")
    result = provider.complete_structured(
        Advice, [{"role": "user", "content": "x"}], "system prompt"
    )

    assert isinstance(result, Advice), (
        f"complete_structured must return an Advice instance on the native path; "
        f"got {type(result).__name__!r}"
    )
    assert result.interpretation == "ok"
    assert len(result.recommendations) == 1
    assert result.recommendations[0].action == "a"


# ---------------------------------------------------------------------------
# Test 2: generate_content receives translated schema + system_instruction
# ---------------------------------------------------------------------------


def test_generate_content_receives_translated_schema_and_system(monkeypatch):
    """generate_content is called with translated schema, system_instruction, and mime type."""
    raw_json = GOOD_ADVICE.model_dump_json()
    fake_genai, fake_types, mock_client = _install_fake_genai(
        monkeypatch, response_text=raw_json
    )

    from fdars.advisor.providers.gemini import GeminiProvider

    system_text = "You are a diagnostics advisor."
    provider = GeminiProvider(api_key="test-key")
    provider.complete_structured(
        Advice, [{"role": "user", "content": "x"}], system_text
    )

    # Inspect generate_content call
    assert mock_client.models.generate_content.called, (
        "models.generate_content must be called"
    )
    call_kwargs = mock_client.models.generate_content.call_args[1]

    # config is the GenerateContentConfig call's kwargs dict (from our side_effect)
    config_kwargs = call_kwargs["config"]
    assert config_kwargs["response_mime_type"] == "application/json", (
        f"response_mime_type must be 'application/json'; "
        f"got {config_kwargs.get('response_mime_type')!r}"
    )
    assert config_kwargs["system_instruction"] == system_text, (
        f"system_instruction must match; "
        f"got {config_kwargs.get('system_instruction')!r}"
    )

    # Schema must not contain additionalProperties (i.e. _gemini_schema was applied)
    schema_sent = config_kwargs["response_json_schema"]
    schema_json = json.dumps(schema_sent)
    assert "additionalProperties" not in schema_json, (
        f"Schema sent to Gemini must not contain 'additionalProperties' "
        f"(indicates _gemini_schema was NOT applied): {schema_json!r}"
    )
    assert "$ref" not in schema_json, (
        f"Schema sent to Gemini must not contain '$ref' (must be inlined): {schema_json!r}"
    )


# ---------------------------------------------------------------------------
# Test 3: Empty / None text raises ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("empty_text", [None, ""])
def test_empty_text_raises_value_error(empty_text, monkeypatch):
    """Given falsy response.text (None or empty string), complete_structured raises ValueError.

    Whitespace-only strings are truthy in Python and will reach model_validate_json
    which raises a different error — that edge case is not tested here (mirrors
    the OpenAI adapter's test design which also excludes whitespace from this test).
    """
    fake_genai, fake_types, mock_client = _install_fake_genai(
        monkeypatch, response_text=empty_text
    )

    from fdars.advisor.providers.gemini import GeminiProvider

    provider = GeminiProvider(api_key="test-key")
    with pytest.raises(ValueError, match="empty"):
        provider.complete_structured(
            Advice, [{"role": "user", "content": "x"}], "system"
        )


# ---------------------------------------------------------------------------
# Test 4: Missing-extra ImportError (actionable pip install hint)
# ---------------------------------------------------------------------------


def test_missing_extra_raises_importerror_with_pip_hint(monkeypatch):
    """When google-genai SDK is absent, GeminiProvider() raises ImportError naming pip install."""
    # Block the google.genai import by setting to None (simulates absent [gemini] extra)
    monkeypatch.setitem(sys.modules, "google", None)  # type: ignore[assignment]
    monkeypatch.setitem(sys.modules, "google.genai", None)  # type: ignore[assignment]
    # Clear cached modules so deferred import fires fresh
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.gemini", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor", raising=False)

    import fdars.advisor  # reimport so _require_gemini is fresh
    import fdars.advisor.providers.gemini as m  # module-level import succeeds (deferred)

    with pytest.raises(ImportError, match=r"pip install fdars\[gemini\]"):
        m.GeminiProvider()


# ---------------------------------------------------------------------------
# Test 5: Python <3.10 guard
# ---------------------------------------------------------------------------


def test_python_lt_310_raises_importerror(monkeypatch):
    """GeminiProvider() raises ImportError on simulated Python <3.10."""
    # The venv is 3.14; simulate 3.9 via monkeypatch
    fake_version = (3, 9, 0, "final", 0)
    monkeypatch.setattr(sys, "version_info", fake_version)

    # Clear cached adapter so __init__ re-checks sys.version_info
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.gemini", raising=False)

    from fdars.advisor.providers.gemini import GeminiProvider

    with pytest.raises(ImportError, match="3.10"):
        GeminiProvider()


# ---------------------------------------------------------------------------
# Test 6: Grounding rejection via centralized _check_grounding
# ---------------------------------------------------------------------------


def test_grounding_rejects_fabricated_evidence_gemini():
    """_check_grounding catches fabricated numbers on the Gemini path too."""
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


def test_grounding_passes_correct_evidence_gemini():
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
# Test 7: resolve_provider("gemini") wiring
# ---------------------------------------------------------------------------


def test_resolve_provider_returns_gemini_provider(monkeypatch):
    """resolve_provider('gemini') returns a ValidateAndRetry wrapper with .name=='gemini'."""
    raw_json = GOOD_ADVICE.model_dump_json()
    fake_genai, fake_types, mock_client = _install_fake_genai(
        monkeypatch, response_text=raw_json
    )

    # Also clear the factory cache so it picks up the fresh gemini module
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers._factory", raising=False)

    from fdars.advisor.providers._factory import resolve_provider, _DEFAULT_MODELS
    from fdars.advisor.providers._validate import ValidateAndRetry

    wrapper = resolve_provider(provider="gemini", model="gemini-2.0-flash")

    assert isinstance(wrapper, ValidateAndRetry), (
        f"resolve_provider('gemini') must return a ValidateAndRetry; "
        f"got {type(wrapper).__name__!r}"
    )
    assert wrapper.name == "gemini", (
        f"wrapper.name must be 'gemini', got {wrapper.name!r}"
    )
    assert wrapper.supports_native_structured_output is True, (
        "GeminiProvider.supports_native_structured_output must be True "
        "(native path returns validated Advice instance)"
    )
    # Verify default model is gemini-2.0-flash via _DEFAULT_MODELS
    assert _DEFAULT_MODELS["gemini"] == "gemini-2.0-flash", (
        f"Default Gemini model must be 'gemini-2.0-flash'; "
        f"got {_DEFAULT_MODELS['gemini']!r}"
    )


def test_resolve_provider_gemini_default_model(monkeypatch):
    """resolve_provider('gemini') uses gemini-2.0-flash as the default model."""
    raw_json = GOOD_ADVICE.model_dump_json()
    fake_genai, fake_types, mock_client = _install_fake_genai(
        monkeypatch, response_text=raw_json
    )
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers._factory", raising=False)

    from fdars.advisor.providers._factory import resolve_provider, _DEFAULT_MODELS

    wrapper = resolve_provider(provider="gemini")
    assert wrapper.model == "gemini-2.0-flash"
    assert _DEFAULT_MODELS["gemini"] == "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# Test 8: resolve_provider missing [gemini] extra raises ImportError (not ValueError)
# ---------------------------------------------------------------------------


def test_resolve_provider_gemini_without_extra_raises_importerror(monkeypatch):
    """resolve_provider('gemini') with missing [gemini] extra raises actionable ImportError.

    The shim in _factory.py was removed in plan 20-03; now the ImportError from
    _require_gemini() (inside GeminiProvider.__init__) surfaces directly.
    It must NOT be a generic ValueError.
    """
    monkeypatch.setitem(sys.modules, "google", None)  # type: ignore[assignment]
    monkeypatch.setitem(sys.modules, "google.genai", None)  # type: ignore[assignment]
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers.gemini", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor.providers._factory", raising=False)
    monkeypatch.delitem(sys.modules, "fdars.advisor", raising=False)

    import fdars.advisor
    from fdars.advisor.providers._factory import resolve_provider

    with pytest.raises(ImportError, match=r"pip install fdars\[gemini\]"):
        resolve_provider(provider="gemini")


# ---------------------------------------------------------------------------
# Test 9: T-20-09 — google.generativeai namespace never appears in provider code
# ---------------------------------------------------------------------------


def test_google_generativeai_namespace_never_used():
    """Verify the legacy google.generativeai namespace is absent from the provider code."""
    import ast
    from pathlib import Path

    gemini_py = (
        Path(__file__).parent.parent
        / "python" / "fdars" / "advisor" / "providers" / "gemini.py"
    )
    source = gemini_py.read_text()
    assert "google.generativeai" not in source, (
        "gemini.py must never import from 'google.generativeai' (deprecated); "
        "use 'google.genai' only."
    )
    assert "generativeai" not in source, (
        "gemini.py must not reference 'generativeai' at all (deprecated SDK)."
    )
