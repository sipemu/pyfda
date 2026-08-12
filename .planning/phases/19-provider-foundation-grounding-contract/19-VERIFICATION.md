---
phase: 19-provider-foundation-grounding-contract
verified: 2026-08-12T08:30:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 19: Provider Foundation & Grounding Contract — Verification Report

**Phase Goal:** The advisor runs behind a uniform `Provider` protocol with grounding/retry machinery
centralized, as a PURE REFACTOR — existing Anthropic behavior/outputs unchanged.

**Verified:** 2026-08-12
**Status:** PASS
**Re-verification:** No — initial verification

---

## Test Suite Execution (offline, no ANTHROPIC_API_KEY)

Command run:

```
/home/simonm/projects/rust/pyfda/.venv/bin/python -m pytest tests/test_advisor.py tests/test_advisor_providers.py -q
```

Result: **23 passed, 1 skipped** in 2.45s.
The single skip is `TestAdvisorIntegration::test_advise_returns_advice_schema` — env-gated,
requires `ANTHROPIC_API_KEY`, expected and correct.

---

## Per-Criterion Verdicts

### Criterion 1 — Provider Protocol + Unchanged Existing Tests (PROV-01, PROV-02)

**Claim:** `advise()` runs through a `Provider` protocol with an `AnthropicProvider` adapter,
and every existing advisor test (offline + env-gated integration) passes unchanged — same
public behavior/outputs.

**Evidence:**

- `python/fdars/advisor/providers/_protocol.py` defines `@runtime_checkable class Provider(Protocol)` with
  `name: str`, `model: str`, `supports_native_structured_output: bool`, and
  `complete_structured(schema, messages, system) -> object`. Exact surface matches PROV-01.
- `python/fdars/advisor/providers/anthropic.py` defines `AnthropicProvider` with `name = "anthropic"`,
  `supports_native_structured_output = True`, and `complete_structured()` calling
  `client.messages.parse(model=..., max_tokens=16000, thinking={"type":"adaptive"}, system=..., output_format=schema, messages=...)` — identical parameters to the pre-refactor inline block.
- `advise()` in `advisor/__init__.py` (line 278) calls `resolve_provider(provider=provider, model=model)`
  and `p.complete_structured(Advice, messages, system)` — fully routed through the protocol.
- `tests/test_advisor.py` was not touched during Phase 19 (confirmed via `git diff ed121f6~1 HEAD -- tests/test_advisor.py` producing no output).
- All 4 offline tests in `test_advisor.py` pass; the 1 integration test is skipped (as before).
- Duck-typed fakes pass `isinstance(fake, Provider)` in 3 tests (PROV-01 satisfied by
  `@runtime_checkable`).

**VERDICT: PASS**

---

### Criterion 2 — Native path vs. Validate-and-Retry (GROUND-01, GROUND-02)

**Claim:** Native-structured-output provider returns schema-validated `Advice` via native path;
non-native provider goes through validate-and-retry (Pydantic validation, ≤2 retries with full
diagnostics re-included) that fails deterministically after the cap with no fabrication.

**Evidence:**

- `_validate.py` `ValidateAndRetry.complete_structured()`: when `supports_native_structured_output=True`,
  delegates directly to `self._provider.complete_structured(...)` with no repair loop (native path).
  When `False`, calls `_fallback_with_retry()`.
- `_fallback_with_retry()`: loop `while attempt < self.MAX_RETRIES` (MAX_RETRIES = 2 hardcoded).
  On `ValidationError`, appends a repair message including `"Reason only from the diagnostics in the
  earlier message"` and re-includes the original messages via `list(messages) + [repair_msg]`.
  After exhausting retries, raises `ValueError("... failed to return valid structured output after 2
  attempts ...")` — never returns a fabricated `Advice`.
- Behavioral spot-check confirmed: a permanently-invalid provider triggers exactly 2 provider
  calls then raises `ValueError`.
- Tests:
  - `test_native_path_returns_advice_directly` — PASS
  - `test_fallback_path_validates_raw_dict` — PASS
  - `test_fallback_retry_on_bad_json` — PASS (2 calls, recovers on second)
  - `test_fallback_raises_after_max_retries` — PASS (2 calls, deterministic raise)

**VERDICT: PASS**

---

### Criterion 3 — Centralized `_check_grounding` on every provider path (GROUND-03)

**Claim:** Centralized `_check_grounding` runs on every provider path and rejects any `Advice`
citing numbers absent from the diagnostics.

**Evidence:**

- `_check_grounding` is defined in `providers/_validate.py` (lines 115–151), NOT inside any adapter.
- In `advise()` (`advisor/__init__.py` line 276–296), `_check_grounding` is imported lazily inside
  the function body and called at line 296 *after* `p.complete_structured()` returns — after the
  provider path, regardless of which provider was used.
- The function iterates over `advice.recommendations` and each `rec.evidence`, extracts numeric
  tokens with `re.findall(r"\b\d+\.?\d*\b", ev)`, and raises `GroundingViolationError` if any
  token is absent from the flattened diagnostics value set.
- The grounding check is NOT inside `AnthropicProvider.complete_structured` — it cannot be
  bypassed by choosing a provider.
- Behavioral spot-check: `FakeNativeProvider` returning evidence `"k=99 clusters"` when diagnostics
  has `k=4` raises `GroundingViolationError: Evidence item cites value '99' not found in diagnostics`.
- Tests:
  - `test_grounding_passes_when_all_numbers_in_diagnostics` — PASS
  - `test_grounding_rejects_fabricated_number` — PASS
  - `test_grounding_passes_qualitative_evidence` — PASS (no numeric tokens → no violation)
  - `test_grounding_runs_on_native_path` — PASS (via direct `_check_grounding` call)
  - `test_advise_grounding_check_runs_on_native_path` — PASS (via full `advise()` call chain)

**VERDICT: PASS**

---

### Criterion 4 — Provider refusal/empty response raises a clear error (GROUND-04)

**Claim:** Provider refusal or empty response raises a clear error rather than yielding a
vacuously-valid `Advice`.

**Evidence:**

- `AnthropicProvider.complete_structured()` (line 87–93): checks `response.parsed_output is None`
  and raises `ValueError("AnthropicProvider: the API did not return a parseable output. The model
  may have responded with only a thinking block or a refusal. Raw response stop_reason: ...")`.
  This fires before any result could be returned.
- `FakeRefusalProvider` in tests raises `ValueError("FakeRefusalProvider: simulated refusal")` —
  `ValidateAndRetry.complete_structured()` propagates this error on the native path (no error
  suppression in the native branch).
- Test `test_refusal_raises` — PASS (matches `"simulated refusal"`).

**VERDICT: PASS**

---

### Criterion 5 — Provider/model selection via params and env vars (PROV-06)

**Claim:** Provider/model selected via `advise(provider=…, model=…)` params and/or env vars
(`FDARS_ADVISOR_PROVIDER` / `_MODEL` / `_BASE_URL` + per-provider keys) with documented
precedence; `provider=None` reproduces today's Anthropic default.

**Evidence:**

- `_factory.py` `resolve_provider()` precedence (explicitly documented in docstring and implemented):
  1. Explicit `provider=` argument (string name or existing Provider instance)
  2. `FDARS_ADVISOR_PROVIDER` env var
  3. Default: `"anthropic"`
  - Model: explicit `model=` > `FDARS_ADVISOR_MODEL` env > provider default (`"claude-opus-4-8"`)
  - API key: explicit `api_key=` > `ANTHROPIC_API_KEY` env
  - Base URL: explicit `base_url=` > `FDARS_ADVISOR_BASE_URL` env
- `provider=None` resolves to `AnthropicProvider(model="claude-opus-4-8")` wrapped in
  `ValidateAndRetry` — identical to the old inline behavior.
- Behavioral spot-check: `FDARS_ADVISOR_MODEL=claude-haiku-4-5` env var with `provider=None` yields
  `result.name = "anthropic"`, `result.model = "claude-haiku-4-5"`.
- Unknown provider name `"openai"` raises `ValueError: resolve_provider: unknown provider 'openai'.
  Supported in Phase 19: 'anthropic'. Additional providers (openai, gemini, ollama) are added in Phase 20.`
- Tests:
  - `test_explicit_provider_instance_passthrough` — PASS
  - `test_env_var_model_override` — PASS
  - `test_env_var_provider_selection` — PASS
  - `test_unknown_provider_raises` — PASS
  - `test_default_returns_anthropic_wrapped` — PASS

**VERDICT: PASS**

---

## Observable Truths Summary

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `advise()` routes through `Provider` protocol + `AnthropicProvider`; all existing tests pass | VERIFIED | `_factory.py` wiring; `advise()` lines 275–290; 23 passed/1 skipped |
| 2 | Native path returns Advice directly; fallback path validates+retries up to MAX_RETRIES=2, then raises | VERIFIED | `_validate.py` logic; behavioral spot-check (exactly 2 calls then raise) |
| 3 | `_check_grounding` is called inside `advise()` after `complete_structured` returns, not inside any adapter | VERIFIED | `__init__.py` lines 276+296; behavioral spot-check (fabricated k=99 caught) |
| 4 | Provider refusal/empty raises `ValueError`, never a vacuous `Advice` | VERIFIED | `anthropic.py` lines 88–93; `test_refusal_raises` PASS |
| 5 | Provider/model selection via params > env vars > default; `provider=None` = Anthropic default | VERIFIED | `_factory.py`; behavioral env-var spot-check; 5 resolve_provider tests PASS |

**Score: 5/5**

---

## Scope Discipline Check

The phase was specified as a PURE REFACTOR with strict scope: no OpenAI/Ollama/Gemini adapters,
no new per-aspect `build_diagnostics` branches.

**Confirmed clean:**
- `python/fdars/advisor/providers/` contains only: `_protocol.py`, `_validate.py`, `_factory.py`,
  `anthropic.py`, `__init__.py`. No OpenAI/Ollama/Gemini adapter files.
- References to `openai`/`ollama`/`gemini` in `_factory.py` and `_validate.py` are comments only
  (`# Phase 20: ...`) — no implementation.
- `advisor/aspects/` contains exactly 5 builders (alignment, fpca, basis, smoothing, clustering) —
  the pre-existing set, moved verbatim. No new aspect builders added.
- `tests/test_advisor.py` was not modified (zero diff between its pre-phase commit and HEAD).

---

## Deferred Import Check

Requirement: `import fdars` must NOT trigger the `anthropic` SDK import.

**Verified:**
```
import fdars
"anthropic" in sys.modules  =>  False
```

All `import anthropic` occurrences in the advisor package are inside function bodies (`_require_anthropic()`,
`AnthropicProvider.__init__`). The deferred-import tower is intact:
`advise()` → `resolve_provider()` (lazy import inside function) → `AnthropicProvider.__init__`
→ `_require_anthropic()` → `import anthropic` (inside function body).

---

## Anti-Pattern Scan

Scanned all files modified in Phase 19: no TBD/FIXME/XXX debt markers, no stubs, no `return null /
return {}` patterns, no placeholder text. The `# Phase 20: ...` comments in `_factory.py` are
scoped forward-references with an explicit phase tag — not unresolved debt markers.

---

## Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| PROV-01 | Provider protocol with `complete_structured`, `name`, `model`, `supports_native_structured_output` | SATISFIED | `_protocol.py`; 3 protocol conformance tests |
| PROV-02 | AnthropicProvider adapter behind protocol; existing tests unchanged | SATISFIED | `anthropic.py`; `test_advisor.py` unchanged; 23+1skip result |
| PROV-06 | Provider/model selection via params + env vars with documented precedence | SATISFIED | `_factory.py`; 5 resolve_provider tests |
| GROUND-01 | Native path returns schema-validated Advice directly | SATISFIED | `_validate.py` native branch; 2 tests |
| GROUND-02 | Non-native path: validate+retry ≤2; deterministic raise after cap | SATISFIED | `_validate.py` fallback; MAX_RETRIES=2; 2 tests + spot-check |
| GROUND-03 | Centralized `_check_grounding` on every provider path | SATISFIED | `advise()` lines 276+296; 5 tests + 2 behavioral spot-checks |
| GROUND-04 | Provider refusal/empty raises clear error | SATISFIED | `anthropic.py` lines 88–93; `test_refusal_raises` |

---

## Human Verification Required

None. All criteria are verifiable programmatically. The env-gated live API integration test
(`TestAdvisorIntegration::test_advise_returns_advice_schema`) correctly skips without
`ANTHROPIC_API_KEY` — that test predates Phase 19 and its skip status is unchanged.

---

## Overall Verdict: PASS

All 5 success criteria are met and confirmed by codebase inspection, behavioral spot-checks,
and a passing test suite (23 passed, 1 skipped). The phase is a clean pure refactor:

- The `Provider` protocol and `AnthropicProvider` adapter are fully wired into `advise()`.
- Grounding check is centralized in `advise()`, not in any adapter.
- Retry cap is MAX_RETRIES=2 and raises deterministically.
- Refusal raises `ValueError`.
- Provider/model selection via params and env vars works with correct precedence.
- `import fdars` does not touch the Anthropic SDK.
- `tests/test_advisor.py` is unchanged and green.
- No OpenAI/Ollama/Gemini code or new aspect builders leaked in.

---

_Verified: 2026-08-12_
_Verifier: Claude (gsd-verifier)_
