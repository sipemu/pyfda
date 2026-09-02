---
phase: 68-function-on-function-scalar-on-function-regression
plan: "01"
subsystem: regression
tags: [pyo3, rust, fdars-core, fof-regression, pydict, numpy, functional-data]

requires:
  - phase: 67-functional-time-series
    provides: established dual-2D binding architecture and non-square fixture convention

provides:
  - "fof_regression bound into fdars.regression (9-key PyDict, dual numpy2d_to_fdmatrix path)"
  - "Non-square (N=30, MX=25, MY=18) test fixture proving beta_surface (m_y, m_x) orientation"

affects:
  - 68-02 (plan 02 extends regression_mod.rs with predict_fof, fof_cv, fof_re_regression, predict_fof_re)

actuals:
  tokens: 3200
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Dual-2D FOF binding: both x_data and y_data converted via numpy2d_to_fdmatrix; argvals via numpy1d_to_vec"
    - "9-key PyDict assembly excluding embedded FpcaResult fields (fpca_x, fpca_y intentionally omitted)"
    - "Non-square 3-distinct-dim test fixture (N, MX, MY all different) as transposition guard"

key-files:
  created:
    - tests/test_fof_regression.py
  modified:
    - src/regression_mod.rs

key-decisions:
  - "Exclude fpca_x/fpca_y from PyDict: internal FPCA state not needed by callers; test confirms absence"
  - "beta_surface shape (m_y, m_x): rows=response grid, cols=predictor grid; documented in docstring and asserted in test"
  - "Placed fof_regression after functional_glm in both code and register() — consistent ordering for plan 02 additions"

patterns-established:
  - "FOF dual-2D input: always pass both functional inputs through numpy2d_to_fdmatrix independently"
  - "3-distinct-dim fixture: N=30, MX=25, MY=18 — all three deliberately different to catch row/col swap"

requirements-completed: [REG-01]

coverage:
  - id: D1
    description: "fof_regression bound into fdars.regression, returning a 9-key PyDict with dual-2D input path"
    requirement: REG-01
    verification:
      - kind: integration
        ref: "tests/test_fof_regression.py#test_fof_regression_returns_dict"
        status: pass
      - kind: integration
        ref: "tests/test_fof_regression.py#test_fof_regression_key_set"
        status: pass
    human_judgment: false
  - id: D2
    description: "beta_surface shape (18, 25) proven on (N=30, MX=25, MY=18) fixture — transposition guard"
    requirement: REG-01
    verification:
      - kind: integration
        ref: "tests/test_fof_regression.py#test_fof_regression_shapes"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-09-02
status: complete
---

# Phase 68 Plan 01: Function-on-Function Regression Tracer Summary

**fof_regression bound into fdars.regression via dual numpy2d_to_fdmatrix path, returning a 9-key PyDict with beta_surface shape (m_y, m_x) = (18, 25) proven on a 3-distinct-dim non-square fixture**

## Performance

- **Duration:** 2 min
- **Started:** 2026-09-02T21:03:37Z
- **Completed:** 2026-09-02T21:05:43Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `fof_regression` added to `src/regression_mod.rs` and registered in `regression_mod.rs::register()` — callable via `fdars.regression.fof_regression` after `maturin develop`
- Dual-2D input path proven: both `x_data (N×MX)` and `y_data (N×MY)` converted independently through `numpy2d_to_fdmatrix` with `numpy1d_to_vec` for argvals
- Returned 9-key PyDict excludes `fpca_x`/`fpca_y` (internal FPCA state); key-set assertion in test enforces this
- `beta_surface` shape `(m_y, m_x) = (18, 25)` proven correct: test with 3-distinct dims (N=30, MX=25, MY=18) catches a transposition bug that a square fixture would hide
- Build clean with zero warnings (`-D warnings` enforced)

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "fof_regression via fdars.regression"** - `d503786` (feat)
2. **Task 2: Non-square end-to-end test proving beta_surface (m_y, m_x) shape** - `8b9fb6d` (test)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/src/regression_mod.rs` — added `fof_regression` #[pyfunction] (80 lines) and its registration in `register()`
- `/home/simonm/projects/rust/pyfda/tests/test_fof_regression.py` — new test file with 4 tests; structured for plan 02 to append predict/cv/re tests

## Decisions Made

- **Excluded fpca_x/fpca_y from PyDict** — 68-RESEARCH Pitfall 1; these are internal FPCA state consumed by `predict_fof` internally (plan 02); test asserts absence
- **beta_surface shape rows=response, cols=predictor** — `fdmatrix_to_numpy2d` preserves the `(m_y, m_x)` FdMatrix layout; documented in NumPy docstring; asserted in test
- **Placed fof_regression after functional_glm** — preserves existing register() ordering and leaves a natural insertion point for plan 02's four additional FOF functions

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 01 tracer complete; `fof_regression` end-to-end proven on non-square fixture
- Ready for Plan 02: `predict_fof`, `fof_cv`, `fof_re_regression`, `predict_fof_re` to be added to `regression_mod.rs` and appended to `tests/test_fof_regression.py`

## Self-Check: PASSED

- `src/regression_mod.rs` — FOUND
- `tests/test_fof_regression.py` — FOUND
- Commit `d503786` (Task 1) — FOUND
- Commit `8b9fb6d` (Task 2) — FOUND
- `maturin develop` — zero warnings
- `pytest tests/test_fof_regression.py -x -q` — 4 passed

---
*Phase: 68-function-on-function-scalar-on-function-regression*
*Completed: 2026-09-02*
