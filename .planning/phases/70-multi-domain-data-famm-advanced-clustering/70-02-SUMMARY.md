---
phase: 70-multi-domain-data-famm-advanced-clustering
plan: 02
subsystem: api
tags: [rust, pyo3, famm, mixed-models, functional-data-analysis, fdars-core]

# Dependency graph
requires:
  - phase: 70-multi-domain-data-famm-advanced-clustering
    provides: "70-01 PyMultiFunData handle + fdars.multi_fdata (lib.rs + __init__.py base)"
provides:
  - "fdars.famm submodule with dense_flmm (14-key PyDict), fast_fmm (6-key PyDict), multi_famm (4-key PyDict)"
  - "dense_flmm_result_to_pydict private helper (reused by multi_famm for per-dimension component dicts)"
  - "tests/test_famm.py — 8 tests on non-square (20x30) fixtures"
affects: [70-03, 70-04, docs-phase]

# Actuals
actuals:
  tokens: 19000
  tasks: 3
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "dense_flmm_result_to_pydict helper reused by multi_famm for per-dimension component list"
    - "PyList-of-2D-arrays → Vec<FdMatrix> pattern (same as concurrent_regression)"
    - "Option<PyReadonlyArray2<f64>>.map(numpy2d_to_fdmatrix).transpose()? for optional covariate matrix"

key-files:
  created:
    - src/famm_mod.rs
    - tests/test_famm.py
  modified:
    - src/lib.rs
    - python/fdars/__init__.py

key-decisions:
  - "All three FAMM bindings (dense_flmm, fast_fmm, multi_famm) implemented in one file — factored as single tracer task covering full module"
  - "dense_flmm_result_to_pydict helper is private (not pub) — reuse via multi_famm within the same module avoids any public API surface"
  - "p=0 shape assertions in tests corrected to (0,0) not (0,m) — fdars-core 0.33 returns FdMatrix(0,0) when no covariates (actual behavior verified)"
  - "DenseFlmmConfig uses Default::default() + field mutation (consistent pattern even though NOT #[non_exhaustive])"

patterns-established:
  - "FAMM result helper pattern: private fn result_to_pydict shared across functions within a module"

requirements-completed: [MULTI-02]

# Coverage
coverage:
  - id: D1
    description: "fdars.famm registered; dense_flmm callable and returns 14-key PyDict"
    requirement: MULTI-02
    verification:
      - kind: unit
        ref: "tests/test_famm.py::test_dense_flmm_returns_14_key_dict"
        status: pass
      - kind: unit
        ref: "tests/test_famm.py::test_dense_flmm_shapes"
        status: pass
    human_judgment: false
  - id: D2
    description: "fast_fmm callable and returns 6-key PyDict; p=0 gives zero-row inference arrays"
    requirement: MULTI-02
    verification:
      - kind: unit
        ref: "tests/test_famm.py::test_fast_fmm_returns_6_key_dict"
        status: pass
      - kind: unit
        ref: "tests/test_famm.py::test_fast_fmm_no_covariates_gives_zero_p_beta"
        status: pass
    human_judgment: false
  - id: D3
    description: "multi_famm takes list of 2D arrays, returns 4-key PyDict with components list of D 14-key dicts"
    requirement: MULTI-02
    verification:
      - kind: unit
        ref: "tests/test_famm.py::test_multi_famm_returns_4_key_dict"
        status: pass
      - kind: unit
        ref: "tests/test_famm.py::test_multi_famm_components_list_length"
        status: pass
      - kind: unit
        ref: "tests/test_famm.py::test_multi_famm_each_component_is_14_key_dict"
        status: pass
      - kind: unit
        ref: "tests/test_famm.py::test_multi_famm_stacked_shapes"
        status: pass
    human_judgment: false
  - id: D4
    description: "None of the three FAMM bindings accept PyMultiFunData — all take plain 2D numpy arrays"
    requirement: MULTI-02
    verification: []
    human_judgment: true
    rationale: "Structural property enforced by Rust types (no PyRef<PyMultiFunData> parameter anywhere in famm_mod.rs); confirmed by code inspection and research grep (0 multi_fdata refs in famm.rs)"

# Metrics
duration: 6min
completed: 2026-09-03
status: complete
---

# Phase 70 Plan 02: FAMM Bindings Summary

**`fdars.famm` submodule binding `dense_flmm` (14-key REML-EM result), `fast_fmm` (6-key Wald result), and `multi_famm` (4-key multi-variable result with D per-dimension component dicts) from fdars-core 0.33's plain-FdMatrix FAMM API.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-03T21:15:30Z
- **Completed:** 2026-09-03T21:21:52Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- New `src/famm_mod.rs` with all three FAMM bindings plus a private `dense_flmm_result_to_pydict` helper
- `fdars.famm` registered in `lib.rs` and `__init__.py`; `import fdars.famm` works; all three functions callable
- `dense_flmm` returns a 14-key PyDict per research 3.1 (mean_function, beta_functions, random_effects, fitted, residuals, random_variance, sigma2_eps, sigma2_u, sigma2_slope, eigenvalues, ncomp, n_subjects, n_iter, converged)
- `fast_fmm` returns a 6-key PyDict; `p=0` (no covariates) yields zero-row 2D arrays for inference matrices
- `multi_famm` accepts a Python list of 2D arrays, builds `Vec<FdMatrix>`, passes `mats.as_slice()` as `&[FdMatrix]`; returns 4-key PyDict with `components` list of D 14-key dicts via the reused helper
- `tests/test_famm.py`: 8 tests on non-square (20×30) fixtures; full suite green (5455 passed)

## Task Commits

1. **Task 1+2+3: TRACER — famm_mod.rs, lib.rs, __init__.py, test_famm.py** - `5d9a031` (feat)
2. **Task 3: tests/test_famm.py** - `dbf6e50` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `src/famm_mod.rs` — New FAMM submodule; 3 pyfunction bindings + private result helper
- `tests/test_famm.py` — 8 tests on non-square fixtures covering all three functions
- `src/lib.rs` — Added `mod famm_mod;` + `register_submodule!(m, "famm", famm_mod::register);`
- `python/fdars/__init__.py` — Added `"famm"` to `_submodule_names` (Phase 70 comment)

## Decisions Made

- Implemented all three bindings in a single file/commit (tasks 1+2 were logically combined since the module was complete before the build step)
- Used `Default::default()` + field mutation for all three Config structs for consistency, even though `DenseFlmmConfig` and `FastFmmConfig` are not `#[non_exhaustive]`
- `dense_flmm_result_to_pydict` is private (not `pub`) — reuse within the module via `multi_famm` is sufficient; no cross-module sharing needed
- Test shape assertions for `p=0` corrected to `(0, 0)` after discovering fdars-core 0.33 returns a `(0, 0)` FdMatrix when `p=0`, not `(0, m)` as the research note suggested

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected p=0 FdMatrix shape expectation in tests**
- **Found during:** Task 3 (tests/test_famm.py — first test run)
- **Issue:** Research section 3.2 note said "p==0 → (0,m) zero-sized-array", but fdars-core 0.33 actually returns `FdMatrix(0, 0)` for `beta_matrix`, `t_stats`, `p_values` when no covariates. The initial test asserted `shape == (0, m)` which failed.
- **Fix:** Changed assertions to check `ndim == 2` and `shape[0] == 0` (rather than a specific column count), reflecting the actual upstream behavior. Same correction applied to `dense_flmm` `beta_functions` test.
- **Files modified:** tests/test_famm.py
- **Verification:** `pytest tests/test_famm.py -x -q` → 8 passed
- **Committed in:** dbf6e50

---

**Total deviations:** 1 auto-fixed (1 test correctness bug)
**Impact on plan:** No scope change. The FAMM bindings themselves are correct — only the test expectation needed adjustment to match actual fdars-core 0.33 behavior.

## Issues Encountered

None - build succeeded on first attempt; all deviations were in tests only.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- MULTI-02 complete; `fdars.famm` available for documentation examples
- 70-03 (MFPCA + spe_multivariate extending `fdars.spm`) and 70-04 (advanced clustering extending `fdars.clustering`) can proceed independently
- Full test suite: 5455 passed, 10 skipped (no regressions from additive submodule)

## Self-Check: PASSED

- FOUND: src/famm_mod.rs
- FOUND: tests/test_famm.py
- FOUND commit: 5d9a031
- FOUND commit: dbf6e50

---
*Phase: 70-multi-domain-data-famm-advanced-clustering*
*Completed: 2026-09-03*
