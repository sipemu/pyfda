---
phase: 67-functional-time-series-fts
plan: 01
subsystem: api
tags: [rust, pyo3, fts, ftsm, fdars-core, numpy, functional-time-series]

# Dependency graph
requires:
  - phase: 66-isolated-crate-bump-regression-gate
    provides: fdars-core 0.33.0 in Cargo.toml with fts module available
provides:
  - fdars.fts PyO3 submodule registered and importable
  - ftsm binding returning transposition-correct PyDict on non-square input
  - src/fts_mod.rs skeleton for plans 67-02/03/04 to extend
  - tests/test_fts.py non-square fixture + ftsm shape assertions
affects: [67-02, 67-03, 67-04]

# Actuals (#2632)
actuals:
  tokens: 8500   # chars/4 over src/fts_mod.rs + src/lib.rs + __init__.py + tests/test_fts.py
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "fts_mod.rs: thin #[pyfunction] wrappers with required argvals (no default_grid) — matches regression_mod.rs pattern"
    - "ar_models: Vec<ArModelResult> serialized inline as PyList of PyDicts (order/phi/sigma2) — no separate helper needed"
    - "numpy2d_to_fdmatrix for all 2D inputs — transposition-safe by design"

key-files:
  created:
    - src/fts_mod.rs
    - tests/test_fts.py
  modified:
    - src/lib.rs
    - python/fdars/__init__.py

key-decisions:
  - "Removed unused PyArray1 import from fts_mod.rs (Rule 1 - would cause warning in CI -D warnings)"
  - "argvals is a required positional parameter (not Option<...> with default_grid) — matches upstream fts validation"

patterns-established:
  - "fts_mod.rs skeleton: register() only registers ftsm in tracer; later plans append wrap_pyfunction! lines"
  - "Non-square fixture (N=40, M=25) + assert N != M guard: established pattern for all fts expansion tests"

requirements-completed: [FTS-01]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "fdars.fts submodule registered and importable via both import styles"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: tests/test_fts.py#test_import_fts_module
        status: pass
    human_judgment: false
  - id: D2
    description: "ftsm on non-square (40x25) input returns transposition-correct PyDict — mean(25,), rotation(25,3), scores(40,3), fitted(40,25)"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: tests/test_fts.py#test_ftsm_shapes_non_square
        status: pass
    human_judgment: false
  - id: D3
    description: "ar_models is a list of ncomp dicts each with keys order, phi, sigma2"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: tests/test_fts.py#test_ftsm_ar_models_structure
        status: pass
    human_judgment: false
  - id: D4
    description: "ftsm with ncomp=0 raises ValueError (upstream validation propagated via to_pyresult)"
    requirement: FTS-01
    verification:
      - kind: unit
        ref: tests/test_fts.py#test_ftsm_ncomp_zero_raises
        status: pass
    human_judgment: false

# Metrics
duration: 3min
completed: 2026-09-02
status: complete
---

# Phase 67 Plan 01: Functional Time Series Tracer Summary

**fdars.fts PyO3 submodule registered end-to-end with ftsm binding proven transposition-correct on a non-square (40x25) AR(1) fixture — 4 tests pass, build green, no warnings**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-02T18:25:43Z
- **Completed:** 2026-09-02T18:28:43Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- New `src/fts_mod.rs` with `//!` doc comment, `#[pyfunction] ftsm` (required `data`, `argvals`, `ncomp=3`), and `pub fn register()` skeleton for expansion by plans 67-02/03/04
- `ftsm` PyDict return: `mean` (m,), `rotation` (m, ncomp), `scores` (n, ncomp), `fitted` (n, m), `weights` (m,), `ncomp` int, `ar_models` list of dicts
- `ar_models` assembled inline using `PyList` of `PyDict`s (order/phi/sigma2 per AR component)
- `src/lib.rs` and `python/fdars/__init__.py` registration wired: `import fdars.fts` works
- `tests/test_fts.py` with non-square (N=40, M=25) AR(1)-driven fixture, `assert N != M` guard, full shape assertions, ar_models structure check, and `ncomp=0` error guard

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "import fdars.fts + ftsm" — one path through every layer** - `68a2991` (feat)
2. **Task 2: Non-square ftsm transposition test — prove the shape mapping** - `6e19fca` (test)

## Files Created/Modified

- `src/fts_mod.rs` - New PyO3 submodule: ftsm binding + register() skeleton
- `src/lib.rs` - Added `mod fts_mod;` + `register_submodule!(m, "fts", fts_mod::register)`
- `python/fdars/__init__.py` - Added `"fts"` to `_submodule_names` + docstring bullet
- `tests/test_fts.py` - Non-square fixture + ftsm shape assertions (4 tests, all pass)

## Decisions Made

- **argvals is required**: accepted as `PyReadonlyArray1<'py, f64>` (not `Option<...>` with `default_grid`) — matches upstream fdars-core validation that rejects argvals.len() != n_points
- **Unused import removed**: `PyArray1` was in the initial import list for future expansion; removed immediately when maturin warned (Rule 1 auto-fix — CI uses `-D warnings`)
- **register() is a skeleton**: only `ftsm` registered in tracer; remaining 12 functions added by plans 67-02/03/04 which will append `wrap_pyfunction!` lines

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused `PyArray1` import**
- **Found during:** Task 1 (maturin develop build output)
- **Issue:** `use numpy::{PyArray1, ...}` triggered `warning: unused import` — project CI uses `-D warnings` so this would fail release builds
- **Fix:** Removed `PyArray1` from the import list; it will be re-added when plans 67-02/03/04 bind functions that need it (e.g., `FacfResult.lags` as `Vec<u32> -> Vec<i64>`)
- **Files modified:** `src/fts_mod.rs`
- **Verification:** maturin develop rebuilt clean with no warnings
- **Committed in:** `68a2991` (Task 1 commit, after fix)

---

**Total deviations:** 1 auto-fixed (1 unused import / Rule 1)
**Impact on plan:** Necessary correctness fix. No scope creep.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `src/fts_mod.rs` skeleton is ready for plan 67-02 to extend with forecasting functions (`ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, `fplsr`)
- `tests/test_fts.py` shared fixture is ready for plan 67-02 to append tests
- FTS-01 partially complete (ftsm fit path proven); remaining FTS-01 coverage (forecast) lands in 67-02

---
*Phase: 67-functional-time-series-fts*
*Completed: 2026-09-02*

## Self-Check

- [x] `src/fts_mod.rs` exists: PASS
- [x] `tests/test_fts.py` exists: PASS
- [x] `src/lib.rs` has `mod fts_mod;` + `register_submodule!(m, "fts", fts_mod::register)`: PASS
- [x] `python/fdars/__init__.py` has `"fts"` in `_submodule_names`: PASS
- [x] `import fdars.fts` works + `fdars.fts.ftsm` callable: PASS
- [x] `pytest tests/test_fts.py -x -q` exits 0 (4 passed): PASS
- [x] Commits `68a2991` and `6e19fca` exist in git log: PASS

## Self-Check: PASSED
