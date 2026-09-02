---
phase: 67-functional-time-series-fts
plan: "02"
subsystem: api
tags: [rust, pyo3, numpy, fdars-core, fts, functional-time-series, forecasting, fplsr]

# Dependency graph
requires:
  - phase: 67-functional-time-series-fts
    provides: "67-01 tracer: ftsm bound in fts_mod.rs, non-square (40x25) test fixture"
provides:
  - "ftsm_forecast #[pyfunction]: combined-function pattern, returns {forecast (h,m), h}"
  - "ftsm_forecast_multistep #[pyfunction]: combined-function pattern, h=5 default, same dict shape"
  - "ftsm_update #[pyfunction]: combined-function pattern, returns updated FtsmResult 7-key dict"
  - "fplsr #[pyfunction]: standalone fit, returns {forecast (1,m), fitted (n-1,m), ncomp}"
  - "Private helper ftsm_result_to_dict: reused by ftsm and ftsm_update"
  - "Forecasting-family tests: 6 new tests appended to tests/test_fts.py (9 total pass)"
affects:
  - 67-03-PLAN  # Group B diagnostics will continue appending to fts_mod.rs
  - 67-04-PLAN  # Group C spectral will continue appending to fts_mod.rs

# Actuals (chars/4 over actual diff — 12446 chars / 4)
actuals:
  tokens: 3111
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Combined-function pattern: Python-facing binding fits ftsm internally then calls downstream fn (avoids PyDict-to-FtsmResult deserialization)"
    - "Private ftsm_result_to_dict helper: reused across ftsm and ftsm_update for consistent 7-key PyDict"
    - "fplsr follows standalone fit pattern identical to ftsm (no combined function needed)"

key-files:
  created: []
  modified:
    - src/fts_mod.rs
    - tests/test_fts.py

key-decisions:
  - "Combined-function pattern for &FtsmResult inputs: re-fit ftsm internally rather than #[pyclass] opaque handle or PyDict deserialization — simpler, consistent with thin-wrapper contract"
  - "Private ftsm_result_to_dict helper factored out to avoid duplication between ftsm and ftsm_update"
  - "fplsr is a standalone fit (like ftsm) so no combined function needed — direct call with data+argvals+ncomp"

patterns-established:
  - "Combined-function pattern: whenever fdars-core fn takes &SomeResult, re-fit the producing fn inside the binding"
  - "ftsm_result_to_dict: canonical 7-key PyDict for FtsmResult; reuse for any future binding that returns FtsmResult"

requirements-completed: [FTS-01, FTS-03]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "ftsm_forecast returns {forecast (h,m), h} using combined-function pattern (no #[pyclass] handle)"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_ftsm_forecast_shapes"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_ftsm_forecast_h1_identity"
        status: pass
    human_judgment: false
  - id: D2
    description: "ftsm_forecast_multistep returns {forecast (h,m), h}; h=1 output bit-identical to ftsm_forecast"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_ftsm_forecast_multistep_shapes"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_ftsm_forecast_h1_identity"
        status: pass
    human_judgment: false
  - id: D3
    description: "ftsm_update returns updated FtsmResult 7-key dict with scores extended by new curves"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_ftsm_update_extends_scores"
        status: pass
    human_judgment: false
  - id: D4
    description: "fplsr returns {forecast (1,m), fitted (n-1,m), ncomp} on non-square fixture"
    requirement: FTS-03
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_fplsr_shapes"
        status: pass
    human_judgment: false

# Metrics
duration: 3min
completed: 2026-09-02
status: complete
---

# Phase 67 Plan 02: Forecasting Family Summary

**Four fts forecasting bindings via combined-function pattern: ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr — all transposition-correct on the non-square (40x25) fixture with 9/9 tests passing.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-02T18:31:43Z
- **Completed:** 2026-09-02T18:34:16Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Bound `ftsm_forecast` and `ftsm_forecast_multistep` via the combined-function pattern (fit ftsm internally, then call downstream fn — no `#[pyclass]` handle, no PyDict deserialization)
- Bound `ftsm_update` using the same pattern: re-fits ftsm on original data, converts new_curve, extends scores
- Factored a private `ftsm_result_to_dict` helper reused by both `ftsm` and `ftsm_update`, keeping the 7-key PyDict consistent
- Bound `fplsr` as a standalone fit (direct data+argvals+ncomp call), returning `{forecast (1,m), fitted (n-1,m), ncomp}`
- Added 6 new test functions (h=1 identity check, shape guards for h=1/h=3, update extension, fplsr shapes) — all 9 tests green

## Task Commits

Each task was committed atomically:

1. **Task 1: Bind ftsm_forecast, ftsm_forecast_multistep, ftsm_update** - `44fb69b` (feat)
2. **Task 2: Bind fplsr + forecasting-family tests** - `c9b8324` (feat)

## Files Created/Modified
- `src/fts_mod.rs` — Added ftsm_result_to_dict helper + ftsm_forecast + ftsm_forecast_multistep + ftsm_update + fplsr; updated register(); refactored ftsm to use helper
- `tests/test_fts.py` — Added 6 new test functions for the forecasting family

## Decisions Made
- Combined-function pattern chosen for &FtsmResult inputs (ftsm_forecast, ftsm_forecast_multistep, ftsm_update): re-fit ftsm inside the binding rather than opaque `#[pyclass]` handle — consistent with "thin wrapper" contract and simpler for this use case
- Private `ftsm_result_to_dict` helper factored from the start to avoid copy-pasting the 7-key ar_models assembly between `ftsm` and `ftsm_update`
- `fplsr` needs no combined function since it takes raw data (no &SomeResult input) — identical standalone pattern to `ftsm`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## Next Phase Readiness
- `fdars.fts` forecasting family (FTS-01 + FTS-03) is complete and green
- Plans 67-03 (diagnostics: functional_acf, functional_pacf, functional_difference, stationarity_test, long_run_covariance) and 67-04 (spectral: spectral_density, dpca, dpca_reconstruct) continue appending to the same fts_mod.rs + test_fts.py files
- The combined-function pattern is now established and documented for dpca_reconstruct (same &DpcaResult problem) in Plan 67-04

## Self-Check: PASSED
- `src/fts_mod.rs` exists and contains all 4 new functions + helper
- `tests/test_fts.py` exists with 9 passing tests
- Commits 44fb69b and c9b8324 confirmed in git log
- `pytest tests/test_fts.py -x -q`: 9 passed in 0.44s

---
*Phase: 67-functional-time-series-fts*
*Completed: 2026-09-02*
