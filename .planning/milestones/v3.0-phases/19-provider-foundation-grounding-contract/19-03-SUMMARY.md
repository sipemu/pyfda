---
phase: 19-provider-foundation-grounding-contract
plan: "03"
subsystem: testing
tags: [pytest, provider-protocol, grounding, tdd, offline-tests, fake-providers]

requires:
  - phase: 19-01
    provides: Provider protocol, AnthropicProvider, ValidateAndRetry, _check_grounding, resolve_provider
  - phase: 19-02
    provides: _schema.py, _prompts.py, advisor package structure, aspects/

provides:
  - "Offline test suite tests/test_advisor_providers.py covering PROV-01, PROV-06, GROUND-01–04"
  - "FakeNativeProvider / FakeFallbackProvider / FakeRefusalProvider test doubles (in-file)"
  - "19 green offline tests; combined 23+1skip with tests/test_advisor.py"

affects: [19-advisor-testing, phase-20-providers]

actuals:
  tokens: 6136
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Test-only fake providers implement the Provider protocol via duck-typing (no inheritance)"
    - "Sequence-of-responses FakeFallbackProvider for retry testing (call_count tracking)"
    - "Patched resolve_provider closure for env-var precedence tests (avoids real Anthropic client)"

key-files:
  created:
    - tests/test_advisor_providers.py
  modified: []

key-decisions:
  - "Fake providers are defined at module level in test_advisor_providers.py (not conftest.py) — keeps test context self-contained per RESEARCH.md Test Organization Principle"
  - "FakeFallbackProvider accepts a list of responses to simulate one-bad-one-good retry sequence (call_count tracked for assertion)"
  - "resolve_provider precedence tests use a local _patched_resolve closure rather than deep monkeypatching of the lazy import chain inside _factory.py — cleaner and avoids import-order issues"
  - "test_grounding_runs_on_native_path is duplicated as TestAdviseIntegration.test_advise_grounding_check_runs_on_native_path to cover both _check_grounding direct call and the full advise() call chain"

patterns-established:
  - "Offline fake providers: duck-typed class with name/model/supports_native_structured_output attributes + complete_structured method — satisfies @runtime_checkable Provider without inheritance"
  - "Retry sequence testing: FakeFallbackProvider([bad_dict, good_dict]) + assert fake._call_count == 2"

requirements-completed:
  - PROV-01
  - PROV-06
  - GROUND-01
  - GROUND-02
  - GROUND-03
  - GROUND-04

coverage:
  - id: D1
    description: "Duck-typed fake providers (native, fallback, refusal) satisfy isinstance(_, Provider) via @runtime_checkable"
    requirement: PROV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestProviderProtocol::test_fake_native_satisfies_protocol"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestProviderProtocol::test_fake_fallback_satisfies_protocol"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestProviderProtocol::test_fake_refusal_satisfies_protocol"
        status: pass
    human_judgment: false

  - id: D2
    description: "ValidateAndRetry native path returns Advice directly; fallback validates raw dict"
    requirement: GROUND-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestValidateAndRetry::test_native_path_returns_advice_directly"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestValidateAndRetry::test_fallback_path_validates_raw_dict"
        status: pass
    human_judgment: false

  - id: D3
    description: "ValidateAndRetry retry: single-retry recovery works; after MAX_RETRIES=2 raises deterministically (no fabricated Advice)"
    requirement: GROUND-02
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestValidateAndRetry::test_fallback_retry_on_bad_json"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestValidateAndRetry::test_fallback_raises_after_max_retries"
        status: pass
    human_judgment: false

  - id: D4
    description: "Provider refusal raises ValueError, never returns a vacuous Advice (GROUND-04)"
    requirement: GROUND-04
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestValidateAndRetry::test_refusal_raises"
        status: pass
    human_judgment: false

  - id: D5
    description: "_check_grounding passes grounded and qualitative evidence; raises GroundingViolationError on fabricated number; runs on native provider path via advise()"
    requirement: GROUND-03
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestCheckGrounding::test_grounding_passes_when_all_numbers_in_diagnostics"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestCheckGrounding::test_grounding_rejects_fabricated_number"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestCheckGrounding::test_grounding_passes_qualitative_evidence"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestCheckGrounding::test_grounding_runs_on_native_path"
        status: pass
    human_judgment: false

  - id: D6
    description: "resolve_provider() precedence: explicit Provider instance passthrough; env FDARS_ADVISOR_PROVIDER/MODEL; unknown provider raises ValueError"
    requirement: PROV-06
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestResolveProvider::test_explicit_provider_instance_passthrough"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestResolveProvider::test_env_var_model_override"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestResolveProvider::test_env_var_provider_selection"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestResolveProvider::test_unknown_provider_raises"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestResolveProvider::test_default_returns_anthropic_wrapped"
        status: pass
    human_judgment: false

  - id: D7
    description: "advise(provider=fake) integration: returns Advice; grounding check fires on native path"
    requirement: GROUND-03
    verification:
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestAdviseIntegration::test_advise_with_fake_provider_returns_advice"
        status: pass
      - kind: unit
        ref: "tests/test_advisor_providers.py::TestAdviseIntegration::test_advise_grounding_check_runs_on_native_path"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-08-12
status: complete
---

# Phase 19 Plan 03: Offline Provider & Grounding Test Suite Summary

**19 offline tests in tests/test_advisor_providers.py covering Provider protocol, ValidateAndRetry retry-cap, _check_grounding centralization, and resolve_provider precedence — all network-free using in-memory fake providers**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-08-12T06:41:42Z
- **Completed:** 2026-08-12T06:49:02Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- Added `tests/test_advisor_providers.py` with 5 test classes and 19 test methods, all offline
- Protocol conformance verified: `FakeNativeProvider`, `FakeFallbackProvider`, `FakeRefusalProvider` all pass `isinstance(_, Provider)` via `@runtime_checkable`
- ValidateAndRetry contract fully tested: native path, fallback validate, single-retry recovery, retry-cap raise (exactly `MAX_RETRIES=2` calls), refusal propagation
- `_check_grounding` tested directly and via `advise()` — grounding runs on every provider path (GROUND-03 centralization proven)
- `resolve_provider()` precedence tested: explicit instance passthrough, env `FDARS_ADVISOR_PROVIDER` / `FDARS_ADVISOR_MODEL`, unknown provider raises
- Combined gate: `pytest tests/test_advisor.py tests/test_advisor_providers.py` → 23 passed, 1 skipped (live API test), no changes to `tests/test_advisor.py`

## Task Commits

All three tasks were built incrementally into a single commit (tests for code already built in waves 1 & 2):

1. **Task 1: Fake providers + protocol + ValidateAndRetry tests** — `89c6757` (test)
2. **Task 2: _check_grounding tests** — included in `89c6757`
3. **Task 3: resolve_provider + advise() integration tests** — included in `89c6757`

**Plan metadata commit:** `(docs commit follows)`

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/tests/test_advisor_providers.py` — 19 offline tests across 5 classes (591 lines)

## Decisions Made

- Fake providers are defined at module level in `test_advisor_providers.py` (not conftest.py) — keeps test context self-contained; allows each test file to fail in isolation as the RESEARCH.md Test Organization Principle requires
- `FakeFallbackProvider` accepts a list of responses (`[bad_dict, good_dict]`) to enable deterministic retry-sequence testing; exposes `_call_count` for assertion
- `resolve_provider` precedence tests use a local `_patched_resolve` closure rather than deep monkeypatching of the lazy-import chain inside `_factory.py` — avoids import-order races and is more readable
- `test_grounding_runs_on_native_path` appears in both `TestCheckGrounding` (direct `_check_grounding` call) and `TestAdviseIntegration` (via `advise()`) to prove both the unit and integration call chains

## Deviations from Plan

None - plan executed exactly as written. All tasks completed without auto-fixes or deviations.

## Issues Encountered

None. The provider code from waves 1 & 2 was complete and correct; all 19 tests passed on first run.

## Known Stubs

None — the test file contains no stubs. All test helper functions (`_valid_advice_dict`, `_fabricated_advice_dict`, etc.) produce fully-formed, validated data.

## Threat Flags

None — test file introduces no new network endpoints, auth paths, file access patterns, or schema changes.

## Next Phase Readiness

- Phase 19 is now fully complete: all 7 requirements (PROV-01, PROV-02, PROV-06, GROUND-01–04) are implemented (waves 1–2) and verified by offline tests (wave 3)
- Phase 20 can add `providers/openai.py`, `providers/gemini.py`, `providers/ollama.py` — the fake-provider pattern in this test suite serves as the template for testing those adapters offline too
- The `test_advisor_providers.py` test file is a stable regression suite: any future refactor that breaks the Provider protocol or ValidateAndRetry contract will be caught immediately

## Self-Check: PASSED

- `tests/test_advisor_providers.py` — FOUND
- Commit `89c6757` — FOUND (`git log --oneline | grep 89c6757`)
- `tests/test_advisor.py` unchanged — confirmed via `git diff tests/test_advisor.py` (empty output)
- Final combined run: 23 passed, 1 skipped

---
*Phase: 19-provider-foundation-grounding-contract*
*Completed: 2026-08-12*
