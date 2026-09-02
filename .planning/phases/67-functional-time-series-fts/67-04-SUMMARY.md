---
phase: 67-functional-time-series-fts
plan: "04"
subsystem: fts
tags: [rust, pyo3, fts, spectral-density, dpca, dimension-reduction, functional-time-series]

requires:
  - phase: 67-functional-time-series-fts
    provides: "10 of 13 fts functions bound in fts_mod.rs (67-01/02/03)"

provides:
  - "spectral_density #[pyfunction] with per-frequency Vec<Vec<f64>> reshape to Python lists of (m,m) arrays"
  - "dpca #[pyfunction] returning PyDict with filters, scores, eigenvalues, valid_range tuple"
  - "dpca_reconstruct #[pyfunction] via combined-function pattern (fit dpca internally, then reconstruct)"
  - "All 13 fdars.fts functions bound and importable"
  - "6 new tests covering spectral/DR shape assertions, bandwidth=0 error, and monotone reconstruction_error"

affects: [67-SUMMARY, FTS-03, phase-68, phase-73]

actuals:
  tokens: 12000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Per-frequency column-major reshape: FdMatrix::from_column_major(inner_vec, m, m) -> fdmatrix_to_numpy2d per freq, collected into PyList"
    - "Combined-function pattern for &DpcaResult: fit dpca internally, call dpca_reconstruct, merge dicts"
    - "dpca_result_to_dict private helper reused by both dpca and dpca_reconstruct"

key-files:
  created: []
  modified:
    - src/fts_mod.rs
    - tests/test_fts.py

key-decisions:
  - "Returned re/im as Python lists of (m,m) arrays rather than (N,m,m) 3D numpy — simpler, users can np.stack() if needed"
  - "dpca_result_to_dict private helper DRYs the dict assembly shared by dpca and dpca_reconstruct"
  - "reconstruction_error monotone check uses 1e-12 tolerance (not strict 0) to handle floating-point"

patterns-established:
  - "Vec<Vec<f64>> per-frequency reshape: iterate inner Vecs, FdMatrix::from_column_major each, fdmatrix_to_numpy2d, append to PyList"
  - "Merged-dict pattern: build base dict from dpca_result_to_dict, then set_item additional reconstruction fields"

requirements-completed: [FTS-03]

coverage:
  - id: D1
    description: "spectral_density bound returning {freqs(N,), re list N×(m,m), im list N×(m,m), m, n_curves, bandwidth}"
    requirement: FTS-03
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_spectral_density_keys_and_shapes"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_spectral_density_stack"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_spectral_density_bandwidth_zero_raises"
        status: pass
    human_judgment: false
  - id: D2
    description: "dpca bound returning {filters, scores (N-2L, ncomp), eigenvalues, n_freqs, filter_lag, ncomp, valid_range tuple}"
    requirement: FTS-03
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_dpca_keys_and_shapes"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_dpca_scores_interior_computed_not_hardcoded"
        status: pass
    human_judgment: false
  - id: D3
    description: "dpca_reconstruct bound via combined-function pattern returning merged dict with fitted_reconstruction (N-2L, m) and monotone reconstruction_error (ncomp,)"
    requirement: FTS-03
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_dpca_reconstruct_keys_and_shapes"
        status: pass
    human_judgment: false
  - id: D4
    description: "All 13 fts functions importable (sanity check prints [])"
    requirement: FTS-03
    verification:
      - kind: integration
        ref: "python -c \"import fdars.fts; print([n for n in (...) if not hasattr(fdars.fts,n)])\""
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-09-02
status: complete
---

# Phase 67 Plan 04: Spectral / Dimension-Reduction Family Summary

**`spectral_density` (per-frequency col-major reshape), `dpca`, and `dpca_reconstruct` (combined-function pattern) complete the 13-function `fdars.fts` submodule; all 27 fts tests pass on the non-square (N=40, M=25) fixture**

## Performance

- **Duration:** 2 min
- **Started:** 2026-09-02T18:42:37Z
- **Completed:** 2026-09-02T18:44:55Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Appended `spectral_density` `#[pyfunction]` with per-frequency `Vec<Vec<f64>>` reshape: each inner flat column-major m×m buffer reshaped via `FdMatrix::from_column_major` then `fdmatrix_to_numpy2d`, collected into Python lists of (m,m) arrays.
- Added private `dpca_result_to_dict` helper reused by both `dpca` and `dpca_reconstruct`.
- Appended `dpca` (standalone fit returning filters/scores/eigenvalues/valid_range) and `dpca_reconstruct` (combined-function pattern: fits dpca internally, calls dpca_reconstruct, returns merged dict).
- Updated `register()` to include all three new functions; all 13 fts functions now bound and importable.
- Added 6 new tests covering: spectral shapes on non-square fixture, np.stack usage, bandwidth=0 ValueError, dpca interior-row computation (not hardcoded), reconstruction_error monotonicity (1e-12 tolerance), and ncomp=2 variant.

## Task Commits

Each task was committed atomically:

1. **Task 1: spectral_density + dpca helper + dpca/dpca_reconstruct** - `d69afb8` (feat)
2. **Task 2: spectral/DR tests** - `5585a3c` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `src/fts_mod.rs` — Group C: spectral_density, dpca_result_to_dict helper, dpca, dpca_reconstruct + updated register()
- `tests/test_fts.py` — 6 new spectral/DR tests appended (tests 22–27)

## Decisions Made

- Returned `re`/`im` as Python lists of (m,m) arrays rather than a 3D (N,m,m) numpy array — simpler binding, users can `np.stack(result["re"])` for the 3D form (tested).
- `dpca_result_to_dict` private helper DRYs the shared dict assembly for `dpca` and `dpca_reconstruct`.
- `reconstruction_error` monotone check uses `<= 1e-12` tolerance to avoid floating-point failures on exact-zero differences.

## Deviations from Plan

None - plan executed exactly as written. All three functions implemented per the combined-function pattern specified in 67-RESEARCH.md §6 and §10.

## Issues Encountered

None. Build succeeded on first attempt; all 27 tests passed immediately.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- FTS-03 complete: all 13 `fdars.fts` functions bound, tested, and importable.
- Phase 67 complete (plans 01–04 all have SUMMARYs).
- Ready for Phase 68 (next planned phase).

## Known Stubs

None — all three functions return fully wired PyDicts using fdars-core 0.33 result structs.

## Self-Check: PASSED

- `src/fts_mod.rs` exists on disk: FOUND
- `tests/test_fts.py` exists on disk: FOUND
- Commit `d69afb8` exists: FOUND
- Commit `5585a3c` exists: FOUND
- `pytest tests/test_fts.py -x -q` → 27 passed
- All 13 fts functions importable: sanity check prints []

---
*Phase: 67-functional-time-series-fts*
*Completed: 2026-09-02*
