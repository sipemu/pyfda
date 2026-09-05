---
phase: 72-advisor-extension
plan: 01
subsystem: advisor
tags: [advisor, fts, frechet, guard-sync, diagnostics, grounding]

requires:
  - phase: 67-functional-time-series-fts
    provides: fts submodule bindings (ftsm, stationarity_test, functional_acf, dpca, fplsr)
  - phase: 69-frechet-regression-density-fda
    provides: frechet submodule bindings (frechet_mean, frechet_anova, frechet_global_reg)
provides:
  - fts advisor aspect: _build_fts_diagnostics handling 6 result shapes (ftsm/stationarity/acf/dpca/fplsr/forecast)
  - frechet advisor aspect stub: _build_frechet_diagnostics (frechet_mean path + None-safe dict; anova/reg in 72-02)
  - both method strings registered atomically across all three guard-sync locations (ADV-02)
  - 37-test fts serialization + grounding suite offline
affects:
  - phase: 72-02 (frechet full branches land here)
  - phase: 72-03 and beyond (pattern for new aspects is proven)

actuals:
  tokens: 32000
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Discriminator hierarchy: independent has_<fn> booleans with None fallback for all sibling fields — dict shape is always complete"
    - "dpca eigenvalues (list of arrays) summarised as max per component — float(np.max(ev)) for ev in list"
    - "Atomic guard-sync commit: 6 files in one feat commit (ADV-02 invariant)"

key-files:
  created:
    - python/fdars/advisor/aspects/fts.py
    - python/fdars/advisor/aspects/frechet.py
    - tests/test_advisor_fts.py
  modified:
    - python/fdars/advisor/__init__.py
    - python/fdars/mcp/server.py
    - tests/test_guard_sync_version_independent.py

key-decisions:
  - "dpca eigenvalues is a list of 1D arrays (one per component) not a flat 1D array — summarise as float(np.max(ev)) per component entry (research assumed flat array; actual shape is list[ndarray])"
  - "test_advisor_fts.py committed in the same atomic feat commit as the aspect files and guard-sync edits (ADV-02 — no separate test commit)"
  - "HUMAN_VERIFY_MODE=end-of-phase + automated-only verify blocks → tracer verified end-to-end, no checkpoint synthesized"

patterns-established:
  - "New aspect file: one public _build_<aspect>_diagnostics function, imports only numpy, no anthropic; all values float/int/bool/list/None"
  - "Multi-result-shape aspects: independent has_<fn> discriminators with None-fallback for fields of non-matching shapes"

requirements-completed: [ADV-01, ADV-02]

coverage:
  - id: D1
    description: "fts aspect builder created: _build_fts_diagnostics handles ftsm/stationarity/acf/dpca/fplsr/forecast result shapes with grounded native scalars"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: tests/test_advisor_fts.py#TestFtsmAspect
        status: pass
      - kind: unit
        ref: tests/test_advisor_fts.py#TestStationarityAspect
        status: pass
      - kind: unit
        ref: tests/test_advisor_fts.py#TestAcfAspect
        status: pass
      - kind: unit
        ref: tests/test_advisor_fts.py#TestDpcaAspect
        status: pass
      - kind: unit
        ref: tests/test_advisor_fts.py#TestFplsrAspect
        status: pass
    human_judgment: false
  - id: D2
    description: "fts and frechet registered atomically across advisor _supported, server _DIAGNOSTICS_METHODS, and test _EXPECTED_DIAGNOSTICS_METHODS in one commit; neither in _RUNNABLE_METHODS"
    requirement: ADV-02
    verification:
      - kind: unit
        ref: tests/test_guard_sync_version_independent.py
        status: pass
      - kind: other
        ref: "atomicity-check: git show HEAD verifies all 3 guard-sync files carry fts+frechet"
        status: pass
    human_judgment: false
  - id: D3
    description: "frechet stub aspect registered and JSON-serialisable (frechet_mean array path + None-safe dict path)"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: tests/test_advisor_fts.py#TestFtsGuardSync::test_unsupported_sentinel_lists_fts_and_frechet
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-09-04
status: complete
---

# Phase 72 Plan 01: fts Aspect + Guard-Sync Registration Summary

**fts aspect builder created and registered end-to-end; frechet stub registered; both method strings added atomically across advisor _supported, server _DIAGNOSTICS_METHODS, and guard-sync test literal in ONE commit; 37 offline serialization tests pass**

## Performance

- **Duration:** 5 min
- **Started:** 2026-09-04T08:51:54Z
- **Completed:** 2026-09-04T08:56:51Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Created `python/fdars/advisor/aspects/fts.py` with `_build_fts_diagnostics` handling 6 fts result shapes via independent `has_<fn>` discriminators; all values cast to native Python float/int/bool/list/None
- Created `python/fdars/advisor/aspects/frechet.py` stub with `_build_frechet_diagnostics`: frechet_mean numpy array path + None-safe dict path (anova/reg branches land in 72-02)
- Registered `"fts"` and `"frechet"` atomically across all three guard-sync locations (`advisor.__init__.py`, `mcp/server.py`, `test_guard_sync_version_independent.py`) in one commit; neither added to `_RUNNABLE_METHODS` (SC3)
- Created `tests/test_advisor_fts.py` with 37 tests across 5 fixture classes (ftsm/stationarity/acf/dpca/fplsr); json.dumps + check_no_numpy + determinism + method-field + p_value-range + ncomp assertions

## Task Commits

Each task was committed atomically (ADV-02 required one single commit for the guard-sync):

1. **Task 1+2: fts aspect + frechet stub + guard-sync + test file** - `15a8e71` (feat)

**Plan metadata:** pending

## Files Created/Modified

- `python/fdars/advisor/aspects/fts.py` - New fts aspect builder, 6 discriminators, grounding-invariant
- `python/fdars/advisor/aspects/frechet.py` - New frechet stub builder, array path + None-safe dict
- `python/fdars/advisor/__init__.py` - Added "fts"/"frechet" to _supported + dispatch branches
- `python/fdars/mcp/server.py` - Added "fts"/"frechet" to _DIAGNOSTICS_METHODS only
- `tests/test_guard_sync_version_independent.py` - Added "fts"/"frechet" to _EXPECTED_DIAGNOSTICS_METHODS
- `tests/test_advisor_fts.py` - 37 offline tests for fts aspect (5 result shapes)

## Decisions Made

1. **dpca eigenvalues are a list of 1D arrays, not a flat array.** Research assumed a flat 1D array per the SUMMARY description ("eigenvalues (array)"), but the actual fdars return is `list[ndarray]` where each element is a per-component frequency-domain eigenvalue spectrum. Fixed by summarising as `float(np.max(ev)) for ev in eigenvalues_raw` (max spectral eigenvalue per component). Discovered during GREEN phase test run.

2. **test_advisor_fts.py committed in the same atomic feat commit as the aspect files.** Plan said Task 2's test file could be committed separately, but since Task 1 required an atomic commit of 5 files including guard-sync edits, merging the test file into that commit satisfied ADV-02 without creating an intermediate inconsistent state.

3. **Tracer feedback gate: no checkpoint synthesized.** HUMAN_VERIFY_MODE=end-of-phase + all-automated verify blocks → re-ran tracer verify end-to-end (both automated verify gates passed), logged success, continued to expansion. No human checkpoint needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] dpca eigenvalues shape mismatch: list[ndarray] not flat 1D array**
- **Found during:** Task 1 GREEN phase (first test run)
- **Issue:** `float(v) for v in np.asarray(raw["eigenvalues"])` raised `TypeError: only 0-dimensional arrays can be converted to Python scalars` — eigenvalues is a Python list of 1D numpy arrays (one per component), not a flat 1D array
- **Fix:** Changed to `float(np.max(np.asarray(ev))) for ev in eigenvalues_raw` — summarises each component's frequency spectrum by its peak eigenvalue
- **Files modified:** python/fdars/advisor/aspects/fts.py
- **Verification:** TestDpcaAspect::test_dpca_eigenvalues_is_list_of_floats passes; check_no_numpy passes
- **Committed in:** 15a8e71 (same feat commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug — actual fdars return shape differs from research assumption)
**Impact on plan:** Fix was minimal (one line change); no architecture change; correct eigenvalue summary semantics preserved.

## Issues Encountered

None beyond the eigenvalues shape deviation documented above.

## Next Phase Readiness

- fts aspect fully registered and tested — ready for 72-02 to extend regression/classification/spm aspects
- frechet method string reserved with a no-op-but-serializable stub — ready for 72-02 to fill anova/reg branches
- Guard-sync invariant holds: `test_guard_sync_version_independent.py` passes (2 tests green)

## Self-Check: PASSED

- `python/fdars/advisor/aspects/fts.py`: FOUND
- `python/fdars/advisor/aspects/frechet.py`: FOUND
- `tests/test_advisor_fts.py`: FOUND
- commit `15a8e71`: FOUND
- guard-sync test: 2 passed
- fts serialization tests: 37 passed

---
*Phase: 72-advisor-extension*
*Completed: 2026-09-04*
