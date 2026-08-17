---
phase: 31-group-a-fdars-inference-bindings
plan: "02"
subsystem: inference-bindings
tags: [rust, pyo3, inference, scb, degras, fdars-core-0.20]
status: complete

dependency_graph:
  requires: [31-01]
  provides: [mean_scb, scb_two_sample_test, fdars.inference SCB surface]
  affects: [src/inference_mod.rs, tests/test_inference.py]

tech_stack:
  added: []
  patterns:
    - string→enum dispatch with non_exhaustive wildcard arm
    - ToleranceBand Vec<f64> fields via vec_to_numpy1d (not fdmatrix_to_numpy2d)
    - shared multiplier_from_str helper reused by both bindings

key_files:
  created: []
  modified:
    - src/inference_mod.rs
    - tests/test_inference.py

decisions:
  - "multiplier_from_str() is a private Rust helper (not pub); both mean_scb and scb_two_sample_test reuse it"
  - "ToleranceBand fields (Vec<f64>) converted via vec_to_numpy1d per-field — not fdmatrix_to_numpy2d"
  - "Canadian Weather dataset strided ::30 for fast CI (small m); 35 stations >> 3 minimum for Degras"
  - "scb_two_sample_test uses growth boys/girls subset (same fixture as plan 31-01) to keep test setup lean"
  - "TDD RED commit (c5eb991) then GREEN + format-fix then single feat commit (ef7d197)"

metrics:
  duration_minutes: 4
  completed_date: "2026-08-17"
  tasks_completed: 2
  commits: 3

estimate:
  tokens: 50000

actuals:
  tokens: 11000
  tasks: 2
  commits: 3
---

# Phase 31 Plan 02: SCB Inference Bindings Summary

Bound `mean_scb` and `scb_two_sample_test` from fdars-core 0.20 into `fdars.inference`, completing requirements INFER-04 and INFER-05.

## One-Liner

Degras SCB bindings: `mean_scb` returns `{lower,upper,center,half_width}` 1-D ndarrays; `scb_two_sample_test` returns `{statistic,p_value,n_perm}` with `n_perm==0`; both dispatch `multiplier` string to `MultiplierDistribution` with `ValueError` fallback.

## What Was Built

### Task 1: mean_scb (INFER-04)

Added `multiplier_from_str()` private helper that maps `"gaussian"` → `MultiplierDistribution::Gaussian`, `"rademacher"` → `MultiplierDistribution::Rademacher`, and wildcards to `PyValueError` (required by the non-exhaustive enum). Added `mean_scb` `#[pyfunction]` with default signature `(data, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian")`. Converts data via `numpy2d_to_fdmatrix`, argvals via `numpy1d_to_vec`, resolves multiplier via helper, routes through `to_pyresult`, then accesses each `ToleranceBand` field individually (non-exhaustive struct) and builds a `PyDict` with `vec_to_numpy1d` per field.

### Task 2: scb_two_sample_test (INFER-05)

Added `scb_two_sample_test` `#[pyfunction]` with signature `(data_a, data_b, argvals, bandwidth, nb=200, confidence=0.95, multiplier="gaussian")`. Reuses `multiplier_from_str` from Task 1 and `test_result_to_pydict` from plan 31-01. Routes through `to_pyresult`. Returns `{statistic, p_value, n_perm}` with `n_perm` always `0`.

Both functions registered in `register()`.

## Tests Added

All in `tests/test_inference.py`:

- `canadian_scb_fixture`: loads Canadian Weather temperature, strides columns `::30` for small `m` and fast `nb` iterations; all 35 stations satisfy `n >= 3` Degras requirement
- `TestMeanScbImport`: importability of `mean_scb` from `fdars.inference`
- `TestMeanScb` (8 tests): four-key dict; shape `(m,)` per field; all-finite values; rademacher succeeds; unknown multiplier raises `ValueError`; `nb=0` raises `ValueError`; `confidence=1.5` raises `ValueError`; `lower <= center <= upper` ordering invariant
- `TestScbTwoSampleImport`: importability of `scb_two_sample_test`
- `TestScbTwoSampleTest` (3 tests): three-key dict; `n_perm == 0`; unknown multiplier raises `ValueError`

Total test file: 42 tests (27 from plan 31-01, 15 new).

## Verification Results

```
maturin develop: Finished dev profile [unoptimized + debuginfo] — 1.30s
cargo fmt --check: OK
cargo clippy --all-targets -- -D warnings: OK (no warnings)
pytest tests/test_inference.py: 42 passed in 0.31s
pytest (full suite): 468 passed, 4 skipped in 108.52s
```

## Deviations from Plan

None — plan executed exactly as written.

The plan called for two separate TDD cycles (one per task). Both functions were small enough to implement atomically in `inference_mod.rs` in a single GREEN pass after the RED commit. This is a minor structural deviation (single GREEN commit covers both tasks) that saved a redundant rebuild cycle without changing any observable behavior. Recorded for completeness.

## Known Stubs

None.

## Threat Flags

None. All STRIDE mitigations from the plan's threat model are implemented:

- **T-31-04** (DoS via nb=0/confidence out-of-range): routed through `to_pyresult()`; `pytest.raises` tests for `nb=0` and `confidence=1.5` pass.
- **T-31-05** (Tampering via unknown multiplier): `multiplier_from_str` wildcard arm returns `PyValueError`; `pytest.raises(ValueError, match="multiplier")` tests pass for both functions.
- **T-31-06** (Wrong-shape band arrays): `vec_to_numpy1d` per field used (not `fdmatrix_to_numpy2d`); shape `(m,)` and `np.all(np.isfinite(...))` assertions pass.

## Self-Check: PASSED

- `/home/simonm/projects/rust/pyfda/src/inference_mod.rs` — FOUND (modified)
- `/home/simonm/projects/rust/pyfda/tests/test_inference.py` — FOUND (modified)
- Commit `c5eb991` (test RED) — FOUND
- Commit `ef7d197` (feat GREEN) — FOUND
- 42 inference tests pass; 468 total pass
