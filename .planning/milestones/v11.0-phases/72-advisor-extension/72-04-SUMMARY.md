---
phase: 72-advisor-extension
plan: "04"
subsystem: testing
tags: [advisor, grounding, llm-free, fts, frechet, test-coverage]

# Dependency graph
requires:
  - phase: 72-advisor-extension
    provides: "72-01: fts+frechet aspects; 72-02: regression/classification/spm extensions; 72-03: guard-sync atomic update"
provides:
  - "Grounding coverage extended to fts and frechet aspects (native-scalar proof)"
  - "Explicit LLM-free assertion: subprocess + in-process fallback for build_diagnostics number path"
  - "Combined advisor/guard-sync gate green (273 tests)"
affects: [73-docs-update]

# Actuals (#2632)
actuals:
  tokens: 11000
  tasks: 1
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dual-mode LLM-free assertion: subprocess proof + in-process sys.modules pop fallback"
    - "Module-level diagnostic fixtures built from real fdars calls for grounding tests"

key-files:
  created: []
  modified:
    - tests/test_advisor_grounding.py

key-decisions:
  - "Used module-level fixture factories (_make_fts_diag, _make_frechet_diag) to build real diagnostics from actual fdars calls — avoids synthetic values and proves the full build_diagnostics->_check_grounding chain"
  - "Both subprocess proof (clean interpreter) and in-process fallback (sys.modules.pop) required — neither may be skipped; the plan explicitly forbids silent skips"
  - "Frechet tested via frechet_mean (spherical, 1-D array path) — exercises the array-not-dict branch in _build_frechet_diagnostics and proves it emits grounded native scalars"

patterns-established:
  - "LLM-free dual-proof pattern: subprocess assertion + in-process fallback using sys.modules.pop/restore in a try/finally block"
  - "Grounding test pattern for new aspects: module-level real-diagnostics fixture, positive cases (real values), qualitative case, negative/fabricated case"

requirements-completed: [ADV-01, ADV-02]

# Coverage metadata
coverage:
  - id: D1
    description: "Grounding coverage for fts aspect — native-scalar values accepted by _check_grounding, fabricated values rejected"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_grounding.py#TestGroundingFtsAspect"
        status: pass
    human_judgment: false
  - id: D2
    description: "Grounding coverage for frechet aspect — native-scalar values accepted by _check_grounding, fabricated values rejected"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_grounding.py#TestGroundingFrechetAspect"
        status: pass
    human_judgment: false
  - id: D3
    description: "LLM-free assertion: build_diagnostics number path imports no anthropic/openai — proven by subprocess (clean interpreter) and in-process fallback (sys.modules.pop)"
    requirement: ADV-02
    verification:
      - kind: unit
        ref: "tests/test_advisor_grounding.py#TestLlmFreeNumberPath"
        status: pass
    human_judgment: false
  - id: D4
    description: "Combined advisor/guard-sync gate green: 273 tests covering grounding, guard-sync, fts, frechet, regression, group-b, spm aspects"
    requirement: ADV-02
    verification:
      - kind: integration
        ref: "pytest tests/test_advisor_grounding.py tests/test_guard_sync_version_independent.py tests/test_advisor_fts.py tests/test_advisor_frechet.py tests/test_advisor_regression_v6.py tests/test_advisor_group_b.py tests/test_advisor_spm_v11.py"
        status: pass
    human_judgment: false

# Metrics
duration: 2min
completed: 2026-09-04
status: complete
---

# Phase 72 Plan 04: Grounding Coverage + LLM-Free Assertion Summary

**Extended test_advisor_grounding.py with fts/frechet native-scalar grounding cases and dual-mode LLM-free subprocess+in-process assertion; combined 273-test advisor/guard-sync gate green**

## Performance

- **Duration:** 2 min
- **Started:** 2026-09-04T11:15:00Z
- **Completed:** 2026-09-04T11:17:02Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments

- Added `TestGroundingFtsAspect` (6 tests): builds real fts diagnostics from `fts.ftsm()`, proves `_check_grounding` accepts native-scalar citations (ncomp, n_obs, fitted_rmse), proves it rejects fabricated values
- Added `TestGroundingFrechetAspect` (4 tests): builds real frechet diagnostics from `frechet.frechet_mean(spherical)`, proves the array-not-dict path emits grounded native scalars accepted by `_check_grounding`
- Added `TestLlmFreeNumberPath` (4 tests): proves `build_diagnostics` number path imports no provider — (a) subprocess proof with clean Python interpreter, (b) in-process fallback using `sys.modules.pop`/restore in `try/finally`; both proofs run for `fts` and `frechet`
- Combined advisor gate: 273 tests (259 prior + 14 new) pass in one run covering grounding, guard-sync, fts, frechet, regression_v6, group_b, spm_v11 aspects

## Task Commits

1. **Task 1: grounding coverage + LLM-free assertion** - `33dbd28` (test)
2. **[Rule 1 - Bug Fix] guard-sync no-op count 14→16** - `9cff083` (fix)

**Plan metadata:** committed separately (docs)

## Files Created/Modified

- `tests/test_advisor_grounding.py` — added 3 classes / 14 new tests (299 lines); module-level fixture factories using real fdars calls; subprocess proof + in-process fallback LLM-free assertion
- `tests/test_mcp_compare_methods.py` — updated guard-sync no-op count 14→16 (Rule 1 fix)
- `tests/test_mcp_pipeline_report.py` — updated guard-sync no-op count 14→16 (Rule 1 fix)
- `tests/test_mcp_tuning.py` — updated guard-sync no-op count 14→16 (Rule 1 fix)

## Decisions Made

- Used module-level fixture factories (`_make_fts_diag`, `_make_frechet_diag`) that call real fdars functions and `build_diagnostics` — ensures the diagnostics are always live values, not synthetic, so the grounding test proves the full chain from fdars output through the aspect builder to the grounding guard
- In-process fallback uses `sys.modules.pop` with a `try/finally` restore block to avoid leaking state between tests; both `anthropic.*` and `openai.*` namespace prefixes are cleared
- Tested frechet via the `frechet_mean(spherical)` path because it exercises the non-dict (array) branch in `_build_frechet_diagnostics` — the most structurally distinct code path in the frechet aspect

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated guard-sync no-op count 14→16 in three MCP tests**
- **Found during:** Task 1 (full suite run)
- **Issue:** `tests/test_mcp_compare_methods.py`, `test_mcp_pipeline_report.py`, `test_mcp_tuning.py` each hard-coded `assert len(_DIAGNOSTICS_METHODS) == 14` — correct when written, but Phase 72-01/03 added fts+frechet making the count 16, breaking 3 tests.
- **Fix:** Updated count from 14 to 16 in all three; updated docstrings to note the Phase 72 origin of the count change while preserving the original no-op intent for the respective phases
- **Files modified:** `tests/test_mcp_compare_methods.py`, `tests/test_mcp_pipeline_report.py`, `tests/test_mcp_tuning.py`
- **Verification:** All 3 tests pass; full suite 5647 passed / 0 failed
- **Committed in:** `9cff083`

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug introduced by prior Phase 72 plans)
**Impact on plan:** Necessary fix to unblock the clean full-suite pass. No scope creep.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 72 (Advisor Extension) is complete: all 4 plans have SUMMARYs, all requirements (ADV-01, ADV-02) are proven by a single green gate
- fts and frechet remain diagnostics-only (absent from both `_RUNNABLE_METHODS` frozensets — SC3 preserved)
- Full suite clean; no regressions introduced

## Self-Check: PASSED

- `tests/test_advisor_grounding.py` exists and contains 54 tests (40 prior + 14 new)
- Commit `33dbd28` exists in git log (grounding tests)
- Commit `9cff083` exists in git log (guard-sync no-op count fix)
- Combined gate (273 tests) passed
- Full suite: 5647 passed, 0 failures

---
*Phase: 72-advisor-extension*
*Completed: 2026-09-04*
