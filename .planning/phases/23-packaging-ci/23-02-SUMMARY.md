---
phase: 23-packaging-ci
plan: "02"
subsystem: testing
tags: [pytest, advisor, grounding, offline-testing, parametrize, cross-coverage]

requires:
  - phase: 23-packaging-ci/23-01
    provides: CI matrix + bare-venv smoke test (Phase 23 plan 01)
  - phase: 21-all-aspects
    provides: all aspect builders (clustering, depth, outliers, classification, represent, regression, regression_cv, spm, alignment, fpca, basis, smoothing)
  - phase: 20-additional-provider-adapters
    provides: fake provider pattern (FakeNativeProvider, FakeFallbackProvider in test_advisor_providers.py)
  - phase: 19-provider-foundation
    provides: advise(), build_diagnostics(), _check_grounding(), ValidateAndRetry

provides:
  - "Aspect × provider offline cross-coverage matrix (12 aspects × 2 provider kinds = 24 cells, QUAL-01)"
  - "Live-integration contract confirmation: 1 gated test per provider, clean skip in empty env (QUAL-02)"
  - "No-SDK-import guardrail: asserts anthropic/openai/google.genai/ollama absent from sys.modules after matrix run"

affects: [Phase 23 plan 03 (CI matrix), Phase 24 (docs)]

actuals:
  tokens: 4242   # 16969 chars / 4 (new file only)
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Aspect × provider parametrize pattern: @pytest.mark.parametrize('aspect,result,build_kwargs', fixtures) × @pytest.mark.parametrize('provider_kind', ['native','fallback'])"
    - "Grounded evidence extraction: scan diag dict for first numeric value at module level, build evidence string, verify grounding passes"
    - "Live module introspection: importlib.util.spec_from_file_location to exec live test module under monkeypatched env; check module-level gate booleans"

key-files:
  created:
    - tests/test_aspect_provider_matrix.py
  modified: []

key-decisions:
  - "Evidence construction strategy: scan built diagnostics for first numeric top-level key/value, cite it as 'key=value' in evidence string — robust across all aspects, grounding always passes on real values"
  - "Both tasks in one file: plan specifies tests/test_aspect_provider_matrix.py for both QUAL-01 and QUAL-02; single atomic commit covers both"
  - "Smoothing fixture chosen as pspline scalar path (no lambda sweep) to stay self-contained and offline"
  - "QUAL-02 uses importlib.util to fresh-load the live module under monkeypatched clean env so gate booleans are deterministically evaluated"

patterns-established:
  - "Cross-product matrix test pattern: separate parametrize decorators for aspect and provider_kind produce (aspect, provider_kind) cells explicitly named in output"
  - "_build_grounded_advice_dict(): generic helper that extracts a real diagnostics value to satisfy _check_grounding — reusable for future aspect additions"

requirements-completed: [QUAL-01, QUAL-02]

coverage:
  - id: D1
    description: "Aspect × {native, fallback} provider offline cross-coverage matrix (24 cells across 12 aspects)"
    requirement: QUAL-01
    verification:
      - kind: unit
        ref: "tests/test_aspect_provider_matrix.py::test_aspect_provider_matrix[*]"
        status: pass
      - kind: unit
        ref: "tests/test_aspect_provider_matrix.py::test_matrix_no_provider_sdk_imported"
        status: pass
    human_judgment: false
  - id: D2
    description: "Live-integration contract confirmation: 3 gated tests, gates falsy in clean env, no SDK at import"
    requirement: QUAL-02
    verification:
      - kind: unit
        ref: "tests/test_aspect_provider_matrix.py::test_live_integration_contract"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-08-12
status: complete
---

# Phase 23 Plan 02: Aspect × Provider Offline Cross-Coverage + Live Contract Confirmation Summary

**24-cell aspect × provider grounding matrix (12 aspects × native/fallback) plus live-integration gate confirmation — fully offline, key-free, 26 new tests, 0 regressions**

## Performance

- **Duration:** 2 min
- **Started:** 2026-08-12T13:33:00Z
- **Completed:** 2026-08-12T13:35:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Created `tests/test_aspect_provider_matrix.py` with 26 new tests: 24 parametrized cells (12 aspects × {native, fallback} providers) + 1 SDK-import guardrail + 1 live-contract confirmation (QUAL-02).
- Every supported aspect's diagnostics (clustering, depth, outliers, classification, represent, regression, regression_cv, spm, alignment, fpca, basis, smoothing) flows through both a native and a fallback fake provider and asserts a grounded `Advice` is returned — exercising the full `build_diagnostics → advise → _check_grounding` path with no network, no API key, no provider SDK.
- QUAL-02 confirmation: introspects `test_advisor_live_integration.py` using `importlib.util` under a monkeypatched clean env, asserting exactly 3 live tests (one per provider), all 3 gate booleans (`_OPENAI_GATE`, `_GEMINI_GATE`, `_OLLAMA_GATE`) are `False` with no env vars set, and no SDK is imported at collection time.
- Full suite: **259 passed, 4 skipped** (baseline was 233 passed, 4 skipped — 26 new tests, 0 regressions, live tests still skip cleanly).

## Task Commits

1. **Task 1 + Task 2: Aspect × provider matrix + live contract confirmation** — `f18ed0f` (feat)

Both tasks produce output in the same file (`tests/test_aspect_provider_matrix.py`); committed as one atomic feat commit per plan instructions.

## Files Created/Modified

- `tests/test_aspect_provider_matrix.py` — 26 tests: QUAL-01 cross-product matrix (24 parametrized cells × 2 guardrails) + QUAL-02 live-integration contract introspection

## Decisions Made

- Evidence construction uses a generic `_build_grounded_advice_dict()` helper that scans the built diagnostics dict for the first numeric top-level key/value and cites it as `"key=value"` in the evidence string. This approach is robust across all 12 aspects without hardcoding per-aspect evidence strings.
- Both QUAL-01 and QUAL-02 live in the same file (`tests/test_aspect_provider_matrix.py`) per plan specification; both committed in one atomic commit.
- QUAL-02 uses `importlib.util.spec_from_file_location` to fresh-load the live module under `monkeypatch` env, ensuring gate booleans are re-evaluated with the clean env regardless of prior imports in the process.
- Fake providers are defined locally (not imported from `test_advisor_providers.py`) to keep the file self-contained per plan instructions.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. All 26 tests passed on first run. Grounding check passed for all 24 aspect × provider cells because `_build_grounded_advice_dict()` correctly cites real diagnostics values.

## Known Stubs

None.

## Threat Flags

None. No new network endpoints, auth paths, or security-relevant surfaces introduced. This plan only adds test-only code.

## Self-Check

- [x] `tests/test_aspect_provider_matrix.py` exists and has 26 tests
- [x] Commit `f18ed0f` exists in git log
- [x] Full suite: 259 passed, 4 skipped (no regressions)
- [x] QUAL-01 verify: `.venv/bin/python -m pytest tests/test_aspect_provider_matrix.py -q` → 26 passed
- [x] QUAL-02 verify: `.venv/bin/python -m pytest tests/test_aspect_provider_matrix.py -q -k "live or contract"` → 1 passed

## Self-Check: PASSED

## Next Phase Readiness

- QUAL-01 and QUAL-02 requirements are complete.
- Phase 23 plan 03 (CI matrix expansion) can proceed independently — this plan is file-disjoint from `.github/workflows/ci.yml`.

---
*Phase: 23-packaging-ci*
*Completed: 2026-08-12*
