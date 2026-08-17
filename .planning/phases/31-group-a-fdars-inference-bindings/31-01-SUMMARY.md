---
phase: 31-group-a-fdars-inference-bindings
plan: "01"
subsystem: inference-bindings
tags: [rust, pyo3, inference, two-sample, permutation, hotelling, bindings]
status: complete

dependency_graph:
  requires: [30-01-PLAN.md]
  provides:
    - fdars.inference submodule (importable both as fdars.inference.fn and from fdars.inference import fn)
    - t_perm_test binding (seed-deterministic permutation t-test)
    - f_perm_test binding (seed-deterministic permutation F-test)
    - two_sample_mean_test binding (asymptotic Hotelling-T², n_perm==0)
    - 31-SIGNATURES.md (authoritative signatures for all 8 Group A functions)
  affects: [31-02-PLAN.md, 31-03-PLAN.md, 34-PLAN.md, 35-PLAN.md]

tech_stack:
  added:
    - fdars.inference PyO3 submodule (src/inference_mod.rs)
    - fdars_core::inference::{t_perm_test, f_perm_test, two_sample_mean_test}
  patterns:
    - TestResult->PyDict helper (non_exhaustive struct field access)
    - seed=None->0 fixed default for byte-identical reproducibility
    - TDD RED/GREEN commits per task

key_files:
  created:
    - src/inference_mod.rs
    - tests/test_inference.py
    - .planning/phases/31-group-a-fdars-inference-bindings/31-SIGNATURES.md
  modified:
    - src/lib.rs (mod inference_mod + register_submodule! for inference)
    - python/fdars/__init__.py (_submodule_names += "inference")

decisions:
  - seed=None resolves to u64 default 0 (not 42) per locked plan decision D
  - mod inference_mod placed alphabetically in lib.rs mod list (rustfmt compliance)
  - All three functions implemented in single file/commit since they share test file and helper

metrics:
  duration_minutes: 6
  completed_date: "2026-08-17"
  tasks_completed: 4
  commits: 4

actuals:
  tokens: 14000
  tasks: 4
  commits: 4
---

# Phase 31 Plan 01: fdars.inference Submodule — Summary

New `fdars.inference` PyO3 submodule exposing three two-sample inference functions (permutation t-test, permutation F-test, asymptotic Hotelling-T²) with seed-deterministic byte-identical reproducibility and a verified-source signatures reference for all 8 Group A functions.

## What Was Built

### Task 1: Verification Spike (31-SIGNATURES.md)

Read vendored fdars-core 0.20.0 source directly and recorded:
- Full Rust signatures for all 8 Group A functions
- `TestResult` and `ToleranceBand` field names (both `#[non_exhaustive]`)
- `MultiplierDistribution` variants (`Gaussian`, `Rademacher`) and their Python string names
- `fregre_lm` signature (no argvals — uses uniform grid internally)
- `oneway_anova_vstat` group-label conventions (0-indexed, sort/dedup internally)
- `DEFAULT_N_PERM = 999`; `n_perm==0` raises `InvalidParameter`

### Task 2: Tracer — End-to-End fdars.inference Submodule

- `src/inference_mod.rs`: module doc comment, `use crate::convert::*`, private `test_result_to_pydict` helper (accesses `TestResult` fields individually — struct is `#[non_exhaustive]`), `t_perm_test` binding
- `src/lib.rs`: `mod inference_mod` added alphabetically; `register_submodule!(m, "inference", inference_mod::register)` after scoring
- `python/fdars/__init__.py`: `"inference"` appended to `_submodule_names`
- TDD RED commit: failing tests for all three functions; GREEN commit: implementation

### Task 3: f_perm_test Binding

Added `f_perm_test` to `src/inference_mod.rs` mirroring `t_perm_test` exactly (same signature shape, same seed strategy, reuses `test_result_to_pydict` helper). Registered in `register()`. Tests: dict shape, n_perm roundtrip, seed determinism, seed=None==seed=0, ValueError for bad inputs.

### Task 4: two_sample_mean_test Binding

Added `two_sample_mean_test` to `src/inference_mod.rs` with `#[pyo3(signature = (data_a, data_b, argvals, ncomp=5))]` — no seed parameter (asymptotic chi-square test). Tests assert: n_perm==0 invariant, determinism without seed, ValueError for ncomp==0, ValueError for mismatched argvals.

## Verification Results

```
maturin develop: Finished `dev` profile — build clean
clippy -D warnings: Finished (no warnings)
cargo fmt --check: OK
python -c "import fdars.inference; from fdars.inference import t_perm_test, f_perm_test, two_sample_mean_test": ok
pytest tests/test_inference.py -x -q: 27 passed
pytest (full suite): 453 passed, 4 skipped (0 failed — no regression)
```

## Deviations from Plan

None — plan executed exactly as written, with one minor deviation:

**1. [Rule 3 - Build fix] rustfmt placement of mod inference_mod**
- **Found during:** Task 2 GREEN verify
- **Issue:** `mod inference_mod` was added after `mod regression_mod` but rustfmt requires alphabetical ordering of mod declarations
- **Fix:** Moved `mod inference_mod` between `mod fdata_mod` and `mod metric_mod` (alphabetical)
- **Files modified:** `src/lib.rs`
- **Commit:** 74aca22 (included in same commit)

## Known Stubs

None — all three functions are fully implemented and wired end-to-end.

## Threat Surface Scan

No new network endpoints, auth paths, or file access patterns introduced.
All threat mitigations from the plan's threat register are in place:
- T-31-01: `to_pyresult()` used throughout; `pytest.raises(ValueError)` tests for n_perm==0 and mismatched grids
- T-31-02: `seed.unwrap_or(0)` fixed default; byte-identical json.dumps determinism test asserts stability
- T-31-03: PyO3 f64→float conversion is native; json.dumps test confirms no numpy scalar leakage

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| src/inference_mod.rs exists | FOUND |
| tests/test_inference.py exists | FOUND |
| 31-SIGNATURES.md exists | FOUND |
| d6e5642 (spike commit) | FOUND |
| 519b20a (test RED commit) | FOUND |
| 74aca22 (feat GREEN commit) | FOUND |
