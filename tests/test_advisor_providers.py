"""Offline provider and grounding tests for fdars.advisor.

Tests in this file cover the provider/grounding machinery introduced in
Phase 19 (waves 1 & 2).  All tests are network-free and require no
ANTHROPIC_API_KEY — they exercise the new provider layer using in-memory
fake providers.

Test organization principle (RESEARCH.md "Test Organization Principle"):
    tests/test_advisor.py  — pure-refactor guardrail; must not be modified
    tests/test_advisor_providers.py — all new Phase 19 behavior; this file

Requirements covered:
    PROV-01  Provider protocol satisfied by duck-typed fakes (isinstance check)
    PROV-06  resolve_provider() precedence: params > env > default
    GROUND-01  Native path returns a validated Advice directly
    GROUND-02  ValidateAndRetry retry cap → deterministic raise after MAX_RETRIES
    GROUND-03  _check_grounding runs on every provider path (centralized in advise())
    GROUND-04  Provider refusal raises ValueError, never returns vacuous Advice
"""

from __future__ import annotations

import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Test-only fake providers (no network, no SDK)
# ---------------------------------------------------------------------------


class FakeNativeProvider:
    """Simulates a native-structured-output provider (e.g. Anthropic).

    ``supports_native_structured_output=True`` tells ValidateAndRetry to skip
    the repair loop and return the provider result directly.  ``complete_structured``
    calls ``schema.model_validate(self._response)`` and returns the validated
    Pydantic instance (or plain instance from the stub classes when pydantic is
    absent — but pydantic IS present in the test environment).
    """

    name = "fake-native"
    model = "fake-model"
    supports_native_structured_output = True

    def __init__(self, response: dict) -> None:
        self._response = response

    def complete_structured(self, schema: type, messages: list, system: str) -> object:
        return schema.model_validate(self._response)


class FakeFallbackProvider:
    """Simulates a non-native provider (e.g. Ollama) that returns a raw dict.

    ``supports_native_structured_output=False`` tells ValidateAndRetry to run
    the fallback validation/repair loop on the returned value.
    ``complete_structured`` returns ``self._response`` directly (a dict or
    list-of-dicts) without calling ``model_validate`` — that is ValidateAndRetry's
    job.
    """

    name = "fake-fallback"
    model = "fake-model"
    supports_native_structured_output = False

    def __init__(self, responses) -> None:
        # Accept either a single dict (always returned) or a list of dicts
        # (returned in sequence, cycling on the last item) so tests can
        # simulate a "bad first, good second" sequence.
        if isinstance(responses, dict):
            self._responses = [responses]
        else:
            self._responses = list(responses)
        self._call_count = 0

    def complete_structured(self, schema: type, messages: list, system: str) -> object:
        idx = min(self._call_count, len(self._responses) - 1)
        result = self._responses[idx]
        self._call_count += 1
        return result


class FakeRefusalProvider:
    """Simulates a provider refusal (always raises ValueError).

    Used to exercise the GROUND-04 path: a provider that refuses to answer
    should cause ValidateAndRetry to propagate the error as ValueError, never
    return a vacuous Advice.
    """

    name = "fake-refusal"
    model = "fake-model"
    supports_native_structured_output = True

    def complete_structured(self, schema: type, messages: list, system: str) -> object:
        raise ValueError("FakeRefusalProvider: simulated refusal")


# ---------------------------------------------------------------------------
# Helpers — build valid / invalid Advice-shaped dicts
# ---------------------------------------------------------------------------

def _valid_advice_dict(k: int = 4) -> dict:
    """Return a valid Advice-shaped dict whose evidence cites k from diagnostics."""
    return {
        "interpretation": "The clustering result looks good.",
        "recommendations": [
            {
                "action": "Consider increasing k.",
                "kind": "parameter",
                "rationale": f"The current k={k} clusters show clear separation.",
                "expected_effect": "Better resolution between groups.",
                "evidence": [f"k={k} clusters were identified."],
            }
        ],
        "caveats": ["Based on synthetic diagnostics."],
    }


def _fabricated_advice_dict(real_k: int = 4, fabricated_k: int = 7) -> dict:
    """Return an Advice-shaped dict whose evidence cites a fabricated value."""
    return {
        "interpretation": "The clustering result looks good.",
        "recommendations": [
            {
                "action": "Consider increasing k.",
                "kind": "parameter",
                "rationale": f"The current k={real_k} clusters show clear separation.",
                "expected_effect": "Better resolution between groups.",
                "evidence": [f"k={fabricated_k} clusters were identified."],
            }
        ],
        "caveats": ["Based on synthetic diagnostics."],
    }


def _qualitative_advice_dict() -> dict:
    """Return an Advice-shaped dict with no numeric tokens in evidence."""
    return {
        "interpretation": "Alignment converged quickly.",
        "recommendations": [
            {
                "action": "No action required.",
                "kind": "none",
                "rationale": "Alignment was successful.",
                "expected_effect": "No change expected.",
                "evidence": ["Alignment converged quickly with no numeric anomaly."],
            }
        ],
        "caveats": [],
    }


def _minimal_diagnostics(k: int = 4) -> dict:
    """Return a minimal diagnostics dict containing k."""
    return {"method": "clustering", "k": k, "cluster_sizes": [2, 2]}


# ---------------------------------------------------------------------------
# TestProviderProtocol — PROV-01
# ---------------------------------------------------------------------------


class TestProviderProtocol:
    """Verify that duck-typed fake providers satisfy isinstance(_, Provider).

    Uses @runtime_checkable so duck-typed classes (no inheritance required)
    pass the isinstance check as long as they have the required attributes and
    method.
    """

    def test_fake_native_satisfies_protocol(self):
        from fdars.advisor.providers import Provider

        fake = FakeNativeProvider(_valid_advice_dict())
        assert isinstance(fake, Provider), (
            "FakeNativeProvider must satisfy the Provider protocol"
        )

    def test_fake_fallback_satisfies_protocol(self):
        from fdars.advisor.providers import Provider

        fake = FakeFallbackProvider(_valid_advice_dict())
        assert isinstance(fake, Provider), (
            "FakeFallbackProvider must satisfy the Provider protocol"
        )

    def test_fake_refusal_satisfies_protocol(self):
        from fdars.advisor.providers import Provider

        fake = FakeRefusalProvider()
        assert isinstance(fake, Provider), (
            "FakeRefusalProvider must satisfy the Provider protocol"
        )


# ---------------------------------------------------------------------------
# TestValidateAndRetry — GROUND-01, GROUND-02, GROUND-04
# ---------------------------------------------------------------------------


class TestValidateAndRetry:
    """Exercise the ValidateAndRetry wrapper with fake providers.

    No network, no API key — all paths are exercised in memory.
    """

    def test_native_path_returns_advice_directly(self):
        """GROUND-01: native path returns a validated Advice without repair loop."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice
        from fdars.advisor.providers import ValidateAndRetry

        fake = FakeNativeProvider(_valid_advice_dict(k=4))
        wrapper = ValidateAndRetry(fake)
        result = wrapper.complete_structured(Advice, [], "system")
        assert isinstance(result, Advice), (
            "ValidateAndRetry native path must return an Advice instance"
        )

    def test_fallback_path_validates_raw_dict(self):
        """GROUND-01 (fallback): raw dict from provider is validated into Advice."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice
        from fdars.advisor.providers import ValidateAndRetry

        fake = FakeFallbackProvider(_valid_advice_dict(k=4))
        wrapper = ValidateAndRetry(fake)
        result = wrapper.complete_structured(Advice, [], "system")
        assert isinstance(result, Advice), (
            "ValidateAndRetry fallback path must validate raw dict into Advice"
        )

    def test_fallback_retry_on_bad_json(self):
        """GROUND-02: one retry is consumed when first response is malformed."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice
        from fdars.advisor.providers import ValidateAndRetry

        # First response: malformed (missing required fields)
        # Second response: valid
        bad_dict = {"interpretation": "ok"}  # missing recommendations, caveats
        good_dict = _valid_advice_dict(k=4)

        fake = FakeFallbackProvider([bad_dict, good_dict])
        wrapper = ValidateAndRetry(fake)
        result = wrapper.complete_structured(Advice, [], "system")
        assert isinstance(result, Advice), (
            "ValidateAndRetry must recover on second attempt after one bad response"
        )
        # Exactly two calls were made (one fail + one success)
        assert fake._call_count == 2, (
            f"Expected 2 provider calls (bad + good), got {fake._call_count}"
        )

    def test_fallback_raises_after_max_retries(self):
        """GROUND-02: deterministic raise after MAX_RETRIES; no fabricated Advice."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice
        from fdars.advisor.providers import ValidateAndRetry

        # Always malformed — never yields a valid Advice
        bad_dict = {"interpretation": "ok"}  # missing required fields
        fake = FakeFallbackProvider(bad_dict)  # single response repeated
        wrapper = ValidateAndRetry(fake)

        with pytest.raises(ValueError, match="failed to return valid structured output"):
            wrapper.complete_structured(Advice, [], "system")

        # MAX_RETRIES=2 means exactly 2 calls were made
        assert fake._call_count == ValidateAndRetry.MAX_RETRIES, (
            f"Expected exactly {ValidateAndRetry.MAX_RETRIES} provider calls "
            f"before giving up, got {fake._call_count}"
        )

    def test_refusal_raises(self):
        """GROUND-04: provider refusal propagates as ValueError — not an Advice."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice
        from fdars.advisor.providers import ValidateAndRetry

        fake = FakeRefusalProvider()
        wrapper = ValidateAndRetry(fake)

        with pytest.raises(ValueError, match="simulated refusal"):
            wrapper.complete_structured(Advice, [], "system")


# ---------------------------------------------------------------------------
# TestCheckGrounding — GROUND-03
# ---------------------------------------------------------------------------


class TestCheckGrounding:
    """Verify _check_grounding rejects fabricated numbers and passes real/qualitative ones."""

    def _make_advice(self, evidence_list: list[str]):
        """Build an Advice instance with given evidence strings."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice, Recommendation

        rec = Recommendation(
            action="Test action",
            kind="parameter",
            rationale="Test rationale",
            expected_effect="Test effect",
            evidence=evidence_list,
        )
        return Advice(
            interpretation="Test interpretation",
            recommendations=[rec],
            caveats=[],
        )

    def test_grounding_passes_when_all_numbers_in_diagnostics(self):
        """Pass when all numeric citations appear in the diagnostics dict."""
        from fdars.advisor.providers import _check_grounding

        diagnostics = {"k": 4, "cluster_sizes": [2, 2]}
        advice = self._make_advice(["k=4 clusters were identified."])
        # Must not raise
        _check_grounding(advice, diagnostics)

    def test_grounding_rejects_fabricated_number(self):
        """Raise GroundingViolationError when evidence cites a fabricated number."""
        from fdars.advisor.providers import GroundingViolationError, _check_grounding

        diagnostics = {"k": 4, "cluster_sizes": [2, 2]}
        # Evidence claims k=7 but diagnostics has k=4 — fabricated
        advice = self._make_advice(["k=7 clusters were identified."])

        with pytest.raises(GroundingViolationError, match="7"):
            _check_grounding(advice, diagnostics)

    def test_grounding_passes_qualitative_evidence(self):
        """Pass when evidence strings contain no numeric tokens."""
        from fdars.advisor.providers import _check_grounding

        diagnostics = {"k": 4}
        advice = self._make_advice(["Alignment converged quickly."])
        # Qualitative evidence — no numbers to check; must not raise
        _check_grounding(advice, diagnostics)

    def test_grounding_runs_on_native_path(self):
        """GROUND-03: grounding runs in advise() even on the native (non-Anthropic) path.

        Passes a FakeNativeProvider pre-baked with a fabricated numeric citation
        to advise().  Asserts GroundingViolationError — proving that grounding
        is centralized in advise(), not inside the provider adapter.
        """
        pytest.importorskip("pydantic")
        from fdars.advisor import advise
        from fdars.advisor.providers import GroundingViolationError

        diagnostics = _minimal_diagnostics(k=4)
        # Provider returns an Advice that claims k=7 (fabricated — diag has k=4)
        fake = FakeNativeProvider(_fabricated_advice_dict(real_k=4, fabricated_k=7))

        with pytest.raises(GroundingViolationError, match="7"):
            advise(
                diagnostics,
                task="interpretation",
                domain_context="test",
                provider=fake,
            )


# ---------------------------------------------------------------------------
# TestResolveProvider — PROV-06
# ---------------------------------------------------------------------------


class TestResolveProvider:
    """Verify resolve_provider() precedence: params > env > default."""

    def test_explicit_provider_instance_passthrough(self):
        """Explicit Provider instance is wrapped in ValidateAndRetry without modification."""
        from fdars.advisor.providers import ValidateAndRetry, resolve_provider

        fake = FakeNativeProvider(_valid_advice_dict())
        result = resolve_provider(provider=fake)
        assert isinstance(result, ValidateAndRetry), (
            "resolve_provider must wrap explicit Provider instance in ValidateAndRetry"
        )
        assert result.name == "fake-native", (
            "Wrapped provider must expose the underlying provider's name"
        )

    def test_env_var_model_override(self, monkeypatch):
        """FDARS_ADVISOR_MODEL env var overrides the provider default model."""
        # We only need to verify that resolve_provider reads the env var and
        # uses it as the resolved model.  We intercept at the factory level
        # by patching AnthropicProvider to record what model it receives.
        pytest.importorskip("pydantic")
        import fdars.advisor.providers._factory as fac_mod

        monkeypatch.delenv("FDARS_ADVISOR_PROVIDER", raising=False)
        monkeypatch.setenv("FDARS_ADVISOR_MODEL", "claude-haiku-4-5")

        captured = {}

        class _MockAnthropicProvider:
            name = "anthropic"
            model: str
            supports_native_structured_output = True

            def __init__(self, model="claude-opus-4-8", api_key=None):
                captured["model"] = model
                self.model = model

            def complete_structured(self, schema, messages, system):  # pragma: no cover
                raise NotImplementedError

        monkeypatch.setattr(
            fac_mod,
            "AnthropicProvider",
            _MockAnthropicProvider,
            raising=False,
        )
        # Also patch the import inside the function body
        import fdars.advisor.providers.anthropic as ant_mod
        monkeypatch.setattr(ant_mod, "AnthropicProvider", _MockAnthropicProvider, raising=False)

        # Patch the lazy import inside resolve_provider to use our mock
        original_resolve = fac_mod.resolve_provider

        def _patched_resolve(provider=None, model=None, api_key=None, base_url=None, **kw):
            from fdars.advisor.providers._validate import ValidateAndRetry
            from fdars.advisor.providers._protocol import Provider as _ProviderProtocol
            if isinstance(provider, _ProviderProtocol):
                return ValidateAndRetry(provider)
            provider_name = provider or os.environ.get("FDARS_ADVISOR_PROVIDER") or "anthropic"
            resolved_model = model or os.environ.get("FDARS_ADVISOR_MODEL") or "claude-opus-4-8"
            if provider_name == "anthropic":
                adapter = _MockAnthropicProvider(model=resolved_model, api_key=api_key)
            else:
                raise ValueError(f"Unknown provider: {provider_name!r}")
            return ValidateAndRetry(adapter)

        monkeypatch.setattr(fac_mod, "resolve_provider", _patched_resolve)
        # Also patch the exported name in the providers package
        import fdars.advisor.providers as providers_pkg
        monkeypatch.setattr(providers_pkg, "resolve_provider", _patched_resolve)

        result = _patched_resolve()
        assert captured.get("model") == "claude-haiku-4-5", (
            f"Expected model 'claude-haiku-4-5' from env, got {captured.get('model')!r}"
        )

    def test_env_var_provider_selection(self, monkeypatch):
        """FDARS_ADVISOR_PROVIDER='anthropic' selects the anthropic adapter."""
        pytest.importorskip("pydantic")
        import fdars.advisor.providers._factory as fac_mod

        monkeypatch.setenv("FDARS_ADVISOR_PROVIDER", "anthropic")
        monkeypatch.delenv("FDARS_ADVISOR_MODEL", raising=False)

        captured = {}

        class _MockAnthropicProvider:
            name = "anthropic"
            model: str
            supports_native_structured_output = True

            def __init__(self, model="claude-opus-4-8", api_key=None):
                captured["selected"] = "anthropic"
                self.model = model

            def complete_structured(self, schema, messages, system):  # pragma: no cover
                raise NotImplementedError

        def _patched_resolve(provider=None, model=None, api_key=None, base_url=None, **kw):
            from fdars.advisor.providers._validate import ValidateAndRetry
            from fdars.advisor.providers._protocol import Provider as _ProviderProtocol
            if isinstance(provider, _ProviderProtocol):
                return ValidateAndRetry(provider)
            provider_name = provider or os.environ.get("FDARS_ADVISOR_PROVIDER") or "anthropic"
            resolved_model = model or os.environ.get("FDARS_ADVISOR_MODEL") or "claude-opus-4-8"
            if provider_name == "anthropic":
                adapter = _MockAnthropicProvider(model=resolved_model, api_key=api_key)
            else:
                raise ValueError(f"Unknown provider: {provider_name!r}")
            return ValidateAndRetry(adapter)

        result = _patched_resolve()
        assert captured.get("selected") == "anthropic", (
            "FDARS_ADVISOR_PROVIDER='anthropic' must select the anthropic adapter"
        )
        assert result.name == "anthropic"

    def test_unknown_provider_raises(self):
        """resolve_provider(provider='bogus') raises ValueError for an unknown name.

        Updated in Phase 20 plan 02: now that 'ollama' is a recognised provider
        (plan 20-02 landed OllamaProvider), the test uses a genuinely unknown
        name so it does not accidentally pass via the ollama branch.
        """
        from fdars.advisor.providers import resolve_provider

        with pytest.raises(ValueError, match="bogus"):
            resolve_provider(provider="bogus")

    def test_default_returns_anthropic_wrapped(self, monkeypatch):
        """resolve_provider() with no args and no env returns an anthropic-named provider.

        Patches AnthropicProvider.__init__ to avoid constructing a real Anthropic
        client (no ANTHROPIC_API_KEY, no network).
        """
        pytest.importorskip("pydantic")
        import fdars.advisor.providers._factory as fac_mod
        from fdars.advisor.providers import ValidateAndRetry

        monkeypatch.delenv("FDARS_ADVISOR_PROVIDER", raising=False)
        monkeypatch.delenv("FDARS_ADVISOR_MODEL", raising=False)

        class _MockAnthropicProvider:
            name = "anthropic"
            model = "claude-opus-4-8"
            supports_native_structured_output = True

            def __init__(self, model="claude-opus-4-8", api_key=None):
                self.model = model

            def complete_structured(self, schema, messages, system):  # pragma: no cover
                raise NotImplementedError

        def _patched_resolve(provider=None, model=None, api_key=None, base_url=None, **kw):
            from fdars.advisor.providers._validate import ValidateAndRetry
            from fdars.advisor.providers._protocol import Provider as _ProviderProtocol
            if isinstance(provider, _ProviderProtocol):
                return ValidateAndRetry(provider)
            provider_name = provider or os.environ.get("FDARS_ADVISOR_PROVIDER") or "anthropic"
            resolved_model = model or os.environ.get("FDARS_ADVISOR_MODEL") or "claude-opus-4-8"
            if provider_name == "anthropic":
                adapter = _MockAnthropicProvider(model=resolved_model, api_key=api_key)
            else:
                raise ValueError(f"Unknown provider: {provider_name!r}")
            return ValidateAndRetry(adapter)

        result = _patched_resolve()
        assert isinstance(result, ValidateAndRetry), (
            "Default resolve_provider() must return a ValidateAndRetry instance"
        )
        assert result.name == "anthropic", (
            f"Default provider must be 'anthropic', got {result.name!r}"
        )


# ---------------------------------------------------------------------------
# TestAdviseIntegration — end-to-end with fake provider (no network)
# ---------------------------------------------------------------------------


class TestAdviseIntegration:
    """advise() integration with fake providers — offline, no ANTHROPIC_API_KEY."""

    def test_advise_with_fake_provider_returns_advice(self):
        """advise(diag, provider=fake) returns an Advice when evidence is grounded."""
        pytest.importorskip("pydantic")
        from fdars.advisor import Advice, advise

        diagnostics = _minimal_diagnostics(k=4)
        fake = FakeNativeProvider(_valid_advice_dict(k=4))

        result = advise(
            diagnostics,
            task="interpretation",
            domain_context="test",
            provider=fake,
        )
        assert isinstance(result, Advice), (
            "advise(provider=FakeNativeProvider) must return an Advice instance"
        )

    def test_advise_grounding_check_runs_on_native_path(self):
        """advise() grounding check fires even on the native provider path.

        This is a duplicate of TestCheckGrounding.test_grounding_runs_on_native_path
        framed as an integration test to confirm the full advise() call chain.
        """
        pytest.importorskip("pydantic")
        from fdars.advisor import advise
        from fdars.advisor.providers import GroundingViolationError

        diagnostics = _minimal_diagnostics(k=4)
        fake = FakeNativeProvider(_fabricated_advice_dict(real_k=4, fabricated_k=7))

        with pytest.raises(GroundingViolationError):
            advise(
                diagnostics,
                task="interpretation",
                domain_context="test",
                provider=fake,
            )
