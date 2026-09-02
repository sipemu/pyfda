---
phase: 67-functional-time-series-fts
plan: "03"
subsystem: api
tags: [rust, pyo3, numpy, fdars-core, functional-time-series, diagnostics]

requires:
  - phase: 67-functional-time-series-fts
    provides: "67-01 ftsm tracer + 67-02 forecasting family (ftsm_forecast, ftsm_forecast_multistep, ftsm_update, fplsr) in src/fts_mod.rs; 9 passing tests"

provides:
  - "functional_acf: PyDict {lags (int64), acf, pacf, upper_band} with seed=42 default"
  - "functional_pacf: identical signature/return to functional_acf (delegates upstream)"
  - "functional_difference: naked numpy 2D (n-1, m) — not a PyDict"
  - "stationarity_test: PyDict {statistic, p_value, n_perm} with seed=42 default, deterministic"
  - "long_run_covariance: PyDict {cov_matrix (m,m symmetric), m, bandwidth, n_curves}"
  - "12 new diagnostics tests; all 21 fts tests passing"

affects: [67-04-spectral-dpca, 67-SUMMARY, FTS-02]

actuals:
  tokens: 4759
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Vec<u32> lags cast: explicit `as i64` map to Vec<i64> before PyArray1::from_vec (not vec_to_numpy1d which expects f64)"
    - "Column-major covariance reshape: FdMatrix::from_column_major(flat_vec, m, m) then fdmatrix_to_numpy2d — never reshape a flat Vec directly"
    - "Naked array return: functional_difference returns Bound<PyArray2<f64>> not PyDict"

key-files:
  created: []
  modified:
    - src/fts_mod.rs
    - tests/test_fts.py

key-decisions:
  - "All five diagnostics functions added in one Rust edit (Tasks 1+2 stacked in fts_mod.rs) for build efficiency — committed in two separate git commits per task"
  - "Vec<u32> lags cast to i64 (not u32 numpy) for consistency with usize_vec_to_numpy1d i64 pattern (§13 per 67-RESEARCH.md)"
  - "functional_difference returns naked PyArray2<f64> — the plan requires NOT a PyDict; this is the only fts function returning a bare array"
  - "LongRunCovResult.cov_matrix reshape via FdMatrix::from_column_major to avoid silent transposition (Pitfall 2 from 67-RESEARCH.md)"

requirements-completed: [FTS-02]

coverage:
  - id: D1
    description: "functional_acf bound: 4-key PyDict with int64 lags, seed-deterministic MC band"
    requirement: FTS-02
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_functional_acf_keys_and_types"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_functional_acf_determinism"
        status: pass
    human_judgment: false
  - id: D2
    description: "functional_pacf bound: same 4-key dict structure as functional_acf"
    requirement: FTS-02
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_functional_pacf_shapes_match_acf"
        status: pass
    human_judgment: false
  - id: D3
    description: "functional_difference returns naked numpy 2D (n-1, m), shape (39, 25) on non-square fixture"
    requirement: FTS-02
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_functional_difference_shape"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_functional_difference_cumsum_roundtrip"
        status: pass
    human_judgment: false
  - id: D4
    description: "stationarity_test bound: PyDict {statistic, p_value, n_perm}; same seed gives identical p_value"
    requirement: FTS-02
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_stationarity_test_keys"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_stationarity_test_determinism"
        status: pass
    human_judgment: false
  - id: D5
    description: "long_run_covariance bound: cov_matrix shape (M, M) symmetric within 1e-10 (column-major reshape correct)"
    requirement: FTS-02
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_long_run_covariance_shape_and_symmetry"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_long_run_covariance_bandwidth_default_vs_explicit"
        status: pass
    human_judgment: false
  - id: D6
    description: "Error guards: n_perm=0 and n_sim=0 raise ValueError"
    requirement: FTS-02
    verification:
      - kind: unit
        ref: "tests/test_fts.py#test_stationarity_test_nperm_zero_raises"
        status: pass
      - kind: unit
        ref: "tests/test_fts.py#test_functional_acf_nsim_zero_raises"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-02
status: complete
---

# Phase 67 Plan 03: Diagnostics Family Summary

**Five FTS diagnostics functions bound: functional_acf/pacf (seed=42, int64 lags), functional_difference (naked array), stationarity_test (permutation p-value, deterministic), long_run_covariance (col-major reshape, symmetric 1e-10); FTS-02 complete with 21 passing tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-02T18:36:57Z
- **Completed:** 2026-09-02T18:40:01Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Bound `functional_acf` and `functional_pacf` returning PyDict `{lags (int64), acf, pacf, upper_band}` with `seed=42` default — deterministic under a fixed seed
- Handled `FacfResult.lags: Vec<u32>` by explicit `as i64` cast (not `vec_to_numpy1d` which is f64-only) — Pitfall 4 from research avoided
- Bound `functional_difference` returning a **naked** `Bound<PyArray2<f64>>` (shape `(n-1, m)`), the only fts function that does not return a PyDict
- Bound `stationarity_test` with permutation-based p-value; identical seeds give bit-identical p-value
- Bound `long_run_covariance` with correct column-major reshape: `FdMatrix::from_column_major(flat_cov, m, m)` then `fdmatrix_to_numpy2d` — symmetry test confirms the reshape is not transposed (Pitfall 2 from research avoided)
- Appended 12 diagnostics tests; all 21 fts tests pass (9 prior + 12 new)

## Task Commits

1. **Task 1: functional_acf, functional_pacf, functional_difference** — `074167d` (feat)
2. **Task 2: stationarity_test, long_run_covariance + diagnostics tests** — `760e8a5` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `src/fts_mod.rs` — five new `#[pyfunction]`s appended (Group B diagnostics); all added to `register()`
- `tests/test_fts.py` — 12 new test functions for the diagnostics family; module docstring updated

## Decisions Made

- Vec<u32> lags cast to i64 (not u32) for consistency with the `usize_vec_to_numpy1d` i64 pattern established in `convert.rs`
- `functional_difference` returns `PyResult<Bound<'py, numpy::PyArray2<f64>>>` — no PyDict wrapper, matching the plan requirement exactly and the upstream return type (`FdMatrix` directly, not a struct)
- Column-major covariance reshape uses `FdMatrix::from_column_major` then `fdmatrix_to_numpy2d` — reuses the project's existing path-safe conversion, not a manual Vec reshaping

## Deviations from Plan

None — plan executed exactly as written. Both conversion gotchas (u32 lags, column-major cov_matrix) and the naked-array requirement for `functional_difference` were handled exactly as specified in 67-RESEARCH.md §10/§13 and the plan action blocks.

## Issues Encountered

None. Build compiled cleanly on first attempt. All 21 tests passed on the first run.

## Known Stubs

None — all five functions are fully wired to fdars-core 0.33 implementations.

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns introduced. Five pure-numerical functions added at the PyO3 boundary. Threat mitigations T-67-05 (col-major reshape via FdMatrix::from_column_major), T-67-06 (u32→i64 cast), T-67-07 (n_perm/n_sim error guards) all implemented and tested.

## Next Phase Readiness

FTS-02 is complete. Plan 67-04 (spectral density + dynamic FPCA) can proceed; it extends `register()` with three more functions (`spectral_density`, `dpca`, `dpca_reconstruct`) and appends their tests to the same `tests/test_fts.py` file.

---
*Phase: 67-functional-time-series-fts*
*Completed: 2026-09-02*

## Self-Check: PASSED

- [x] `src/fts_mod.rs` exists and has the five new pyfunction definitions
- [x] `tests/test_fts.py` has 12 new test functions starting with `test_functional_acf_`, `test_functional_pacf_`, `test_functional_difference_`, `test_stationarity_test_`, `test_long_run_covariance_`
- [x] Commit `074167d` exists (Task 1)
- [x] Commit `760e8a5` exists (Task 2)
- [x] `pytest tests/test_fts.py -x -q` exits 0 with 21 passed
