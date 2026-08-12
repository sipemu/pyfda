---
phase: 20-additional-provider-adapters
verified: 2026-08-12T10:45:00Z
status: passed
score: 4/4 success criteria verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 20: Additional Provider Adapters — Verification Report

**Phase Goal:** OpenAI (+OpenAI-compatible via `base_url`), Ollama (local, no key), and Gemini can each back the advisor through the Phase 19 `Provider` protocol, each an optional extra, with the grounding invariant holding on every backend.

**Verified:** 2026-08-12T10:45:00Z
**Status:** PASS
**Re-verification:** No — initial verification

---

## Test Suite Execution

```
pytest tests/test_advisor_openai.py tests/test_advisor_ollama.py tests/test_advisor_gemini_schema.py tests/test_advisor_gemini.py tests/test_advisor_live_integration.py tests/test_advisor_providers.py tests/test_advisor.py -q
71 passed, 4 skipped in 3.05s
```

All 71 offline tests pass. 4 live integration tests skip cleanly with no env variables set (no `FDARS_INTEGRATION=1`, no provider API keys, no Ollama daemon). No `ImportError` during collection.

---

## Per-Criterion Verdicts

### SC-1 — VERIFIED: OpenAI + OpenAI-compatible via `base_url`

**Claim:** `advise(provider="openai", …)` works against OpenAI and any OpenAI-compatible endpoint via configurable `base_url` (vLLM/LM Studio/LocalAI).

**Evidence:**

`python/fdars/advisor/providers/openai.py` exists and is fully substantive (187 lines, no stubs).

- `OpenAIProvider.name = "openai"`, `supports_native_structured_output = True`
- `__init__` accepts `base_url` and threads it to `openai.OpenAI(api_key=..., base_url=base_url)`
- Localhost/127.0.0.1 detection: when `base_url` matches `r"localhost|127\.0\.0\.1"` and no explicit `api_key` is provided, resolves `api_key = "none"` (dummy key for keyless local endpoints — T-20-02 mitigated)
- `complete_structured`: injects system as first message, builds `json_schema` response_format with `strict=True`, checks `choice.message.refusal` (GROUND-04 parity), checks content not empty, returns `schema.model_validate_json(content)` — a validated `Advice` instance

Factory wiring in `_factory.py` (lines 91–98): `resolve_provider("openai")` creates `OpenAIProvider(model=..., api_key=..., base_url=resolved_base_url)` where `resolved_base_url` comes from the `base_url` argument or `FDARS_ADVISOR_BASE_URL` env var.

Tests confirming: `test_localhost_base_url_passes_dummy_key`, `test_127_0_0_1_base_url_passes_dummy_key`, `test_no_base_url_does_not_pass_dummy_key`, `test_resolve_provider_returns_openai_provider`, `test_resolve_provider_openai_model_explicit` — all pass.

**Verdict: VERIFIED**

---

### SC-2 — VERIFIED: Ollama fully local with no API key

**Claim:** `advise(provider="ollama", …)` produces grounded advice fully locally with no API key.

**Evidence:**

`python/fdars/advisor/providers/ollama.py` exists and is fully substantive (169 lines, no stubs).

- `OllamaProvider.name = "ollama"`, `supports_native_structured_output = False`
- `__init__(model="llama3.2", host=None)`: no `api_key` parameter at all; calls `_require_ollama()` then `_require_pydantic()`; stores `self.model` and `self._host`
- `complete_structured`: deferred `import ollama`; prepends system message; appends JSON-schema hint to last user message; calls `ollama.chat(model=..., messages=..., format=json_schema, options={"temperature":0})` — with `host=self._host` only when non-None; returns `json.loads(content)` (raw dict, not Pydantic instance)
- No conflicting generation-control params alongside `format=` (no `think`, no extra params — T-20-05 mitigated)
- `supports_native_structured_output = False` routes through `ValidateAndRetry._fallback_with_retry` which owns schema validation and up to 2 repair retries

Factory wiring: `resolve_provider("ollama")` creates `OllamaProvider(model=..., host=resolved_base_url)` — no api_key. `_KEY_ENV` dict has no entry for `"ollama"`.

Grounding: `advise()` calls `_check_grounding()` centrally after `p.complete_structured()` returns — verified by `test_grounding_rejects_fabricated_evidence_ollama` and `test_grounding_passes_correct_evidence_ollama`.

Tests confirming: `test_complete_structured_returns_raw_dict`, `test_no_conflicting_generation_param_in_call`, `test_validate_and_retry_validates_raw_dict`, `test_retry_then_raises_after_max_retries`, `test_resolve_provider_ollama_host_from_base_url` — all pass.

**Verdict: VERIFIED**

---

### SC-3 — VERIFIED: Gemini with Pydantic→Gemini schema translation

**Claim:** `advise(provider="gemini", …)` works against Google Gemini with the Pydantic→Gemini schema translation applied so structured output validates.

**Evidence:**

`python/fdars/advisor/providers/gemini.py` exists and is fully substantive (286 lines, no stubs).

- `GeminiProvider.name = "gemini"`, `supports_native_structured_output = True`
- Python <3.10 guard in `__init__`: `if sys.version_info < (3, 10): raise ImportError("… Python >=3.10 …")` checked before SDK import
- `_gemini_schema()` translation pipeline:
  1. `deepcopy(model_cls.model_json_schema())` — never mutates Pydantic's cached schema
  2. `defs = schema.pop("$defs", {})` — extracts definitions
  3. `_resolve_refs(schema, defs)` — recursively inlines all `$ref` pointers
  4. `_strip_key(schema, "additionalProperties")` — strips SDK-rejected key recursively
  5. `_strip_key(schema, "title")` — keeps wire payload lean
- Spot-check result (live): `additionalProperties` absent, `$ref` absent, `$defs` absent, `kind` enum `['parameter', 'method', 'none']` preserved, `required` arrays present on root and inlined Recommendation
- `complete_structured`: calls `_gemini_schema(schema)`, joins user-role messages as `contents=`, calls `self._client.models.generate_content(config=GenerateContentConfig(system_instruction=..., response_mime_type="application/json", response_json_schema=gemini_schema))`, raises `ValueError` on empty `response.text`, returns `schema.model_validate_json(text)`
- `google.generativeai` namespace never used (only `google.genai`) — verified by AST test `test_google_generativeai_namespace_never_used` and direct grep of `gemini.py`

6 schema translation tests in `test_advisor_gemini_schema.py` (offline, pydantic-only): all pass.
12 offline adapter tests in `test_advisor_gemini.py`: all pass (fake `google/google.genai/google.genai.types` module hierarchy via `monkeypatch.setitem`).

**Verdict: VERIFIED**

---

### SC-4 — VERIFIED: Optional extras with actionable ImportError

**Claim:** Each provider installs as an optional extra (`[openai]`, `[gemini]`, `[ollama]`); the base package imports and the offline core runs with no provider installed, and a missing extra raises an actionable ImportError naming `pip install fdars[<extra>]`.

**Evidence (extras in pyproject.toml):**

```toml
openai = ["openai>=1.40,<2.0", "pydantic>=2.0"]
gemini = ["google-genai>=1.0,<3.0", "pydantic>=2.0"]
ollama = ["ollama>=0.6.2", "pydantic>=2.0"]
all-providers = ["fdars[advisor]", "fdars[openai]", "fdars[gemini]", "fdars[ollama]"]
```

All four extras confirmed present in `pyproject.toml` lines 51–62.

**Base package import with no provider SDK:** `import fdars` confirmed OK in bare venv (no openai, no google-genai, no ollama installed). All SDK imports are deferred to `__init__` / method bodies in each adapter — module-level imports are limited to `from __future__ import annotations` only.

**Actionable ImportError for each missing extra:**

- `_require_openai()`: raises `ImportError` with `"pip install fdars[openai]"` — tested by `test_missing_extra_raises_importerror_with_pip_hint` in `test_advisor_openai.py`
- `_require_gemini()`: raises `ImportError` with `"pip install fdars[gemini]"` — tested by `test_missing_extra_raises_importerror_with_pip_hint` and `test_resolve_provider_gemini_without_extra_raises_importerror` in `test_advisor_gemini.py`
- `_require_ollama()`: raises `ImportError` with `"pip install fdars[ollama]"` — tested by `test_missing_extra_raises_importerror_with_pip_hint` and `test_resolve_provider_ollama_without_extra_raises_importerror` in `test_advisor_ollama.py`

**No generic "unknown provider" masking:** Factory shims (the temporary `try/except ImportError → ValueError` wrappers added in plan 20-01 for gemini and ollama) were removed in plans 20-02 and 20-03 respectively. The factory now imports each adapter module at the `elif provider_name == "xxx":` branch and the `_require_xxx()` guard in `__init__` surfaces the actionable `ImportError` directly.

- `resolve_provider("bogus")` → `ValueError` (genuinely unknown) — confirmed live
- `resolve_provider(provider=None)` → defaults to `"anthropic"` — confirmed via factory code path (`or "anthropic"` fallback on line 72)
- `resolve_provider("openai")` with missing extra → `ImportError("pip install fdars[openai]")` — tested
- `resolve_provider("gemini")` with missing extra → `ImportError("pip install fdars[gemini]")` — tested (not `ValueError`)
- `resolve_provider("ollama")` with missing extra → `ImportError("pip install fdars[ollama]")` — tested (not `ValueError`)

**Verdict: VERIFIED**

---

## Cross-Cutting Invariant Checks

### Grounding Invariant Holds on Every Backend

`_check_grounding()` and `_protocol.py` were NOT modified by Phase 20. Both files have a single commit predating Phase 20:

```
00c73b7 feat(19-01): add providers/ layer — Provider protocol, AnthropicProvider, ValidateAndRetry, _check_grounding, resolve_provider
```

No Phase 20 commit touched `_validate.py` or `_protocol.py`. Grounding check is called centrally in `advise()` (line 384: `_check_grounding(advice, diagnostics)`) after every `p.complete_structured()` call, regardless of provider.

Grounding tests exercised on all three new provider paths: fabricated `k=999` rejected, correct `k=4` passes. Tests in `test_advisor_openai.py`, `test_advisor_ollama.py`, and `test_advisor_gemini.py`.

### Provider Protocol Conformance

All three adapters implement the `Provider` protocol from `_protocol.py`:
- `name: str` — class attribute, set on all three
- `model: str` — instance attribute, set in `__init__`
- `supports_native_structured_output: bool` — class attribute on all three (OpenAI: True, Ollama: False, Gemini: True)
- `complete_structured(schema, messages, system) -> object` — implemented on all three

Duck-typing confirmed: protocol is `@runtime_checkable`; instances would pass `isinstance(adapter, Provider)`.

### No Phase 21/22/23 Scope Leakage

Phase 20 adapter files contain no references to MCP, streaming, batch, per-aspect coverage, or packaging concerns that belong to Phases 21–24. Zero matches in grep scan.

---

## Artifact Inventory

| Artifact | Status | Notes |
|---|---|---|
| `python/fdars/advisor/providers/openai.py` | VERIFIED | 187 lines, fully wired |
| `python/fdars/advisor/providers/ollama.py` | VERIFIED | 169 lines, fully wired |
| `python/fdars/advisor/providers/gemini.py` | VERIFIED | 286 lines, fully wired |
| `python/fdars/advisor/providers/_factory.py` | VERIFIED | Four-branch, no shims remaining |
| `python/fdars/advisor/__init__.py` | VERIFIED | Three version constants + three deferred guards |
| `pyproject.toml` | VERIFIED | `[openai]`, `[gemini]`, `[ollama]`, `[all-providers]` extras |
| `tests/test_advisor_openai.py` | VERIFIED | 8 tests pass |
| `tests/test_advisor_ollama.py` | VERIFIED | 11 tests pass |
| `tests/test_advisor_gemini_schema.py` | VERIFIED | 6 tests pass |
| `tests/test_advisor_gemini.py` | VERIFIED | 12 tests pass |
| `tests/test_advisor_live_integration.py` | VERIFIED | 3 tests skip cleanly with no env |
| `tests/test_openai_adapter_tdd.py` | VERIFIED | 2 regression guard tests pass |

**No modified Phase 19 files:** `_protocol.py` and `_validate.py` untouched by all Phase 20 commits.

---

## Requirements Coverage

| Requirement | Description | Status | Evidence |
|---|---|---|---|
| PROV-03 | OpenAI adapter + `base_url` compat endpoint | SATISFIED | `openai.py` + factory wiring; localhost dummy key; 8 offline tests |
| PROV-04 | Ollama adapter, local, no API key | SATISFIED | `ollama.py` no `api_key` param; non-native path via ValidateAndRetry; 11 offline tests |
| PROV-05 | Gemini adapter with Pydantic→Gemini schema translation | SATISFIED | `gemini.py` + `_gemini_schema`; 18 offline tests (6 schema + 12 adapter) |
| PROV-07 | Optional extras; base import clean; actionable ImportError | SATISFIED | All 4 extras in pyproject.toml; bare-venv import confirmed; pip-install hints tested |

---

## Anti-Patterns Scan

No `TBD`, `FIXME`, or `XXX` markers found in any Phase 20 adapter files, factory, or `__init__.py`. No `TODO`, `HACK`, or `PLACEHOLDER` markers found. No `return null`, empty implementations, or hardcoded stub data. All three adapter `complete_structured` implementations make real SDK calls (deferred imports), build real request payloads, and perform real validation.

---

## Overall Verdict

**PASS — All 4 success criteria verified. Phase goal achieved.**

The three adapters (OpenAI, Ollama, Gemini) each implement the Phase 19 `Provider` protocol without modifying it, each ships as an optional extra, the base package imports cleanly with no SDK installed, missing extras raise actionable `ImportError` messages naming the correct `pip install fdars[<extra>]` hint, and the grounding invariant runs centrally on every provider path. 71 offline tests pass; 4 env-gated live tests skip cleanly.

---

_Verified: 2026-08-12T10:45:00Z_
_Verifier: Claude (gsd-verifier)_
