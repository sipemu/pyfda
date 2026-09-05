---
phase: 67-functional-time-series-fts
reviewed: 2026-09-02T00:00:00Z
depth: deep
files_reviewed: 4
files_reviewed_list:
  - src/fts_mod.rs
  - src/lib.rs
  - python/fdars/__init__.py
  - tests/test_fts.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: clean
---

# Phase 67: Code Review Report

**Reviewed:** 2026-09-02
**Depth:** deep
**Files Reviewed:** 4
**Status:** clean (0 critical, 0 warnings, 2 info)

## Summary

Phase 67 adds the `fdars.fts` PyO3 submodule binding all 13 public functions from fdars-core 0.33's `fts` module. This is a thin binding layer using the established project patterns: `numpy2d_to_fdmatrix` for all 2D inputs, `fdmatrix_to_numpy2d` for all FdMatrix outputs, `to_pyresult` for error propagation, and `PyDict` returns with struct fields as keys.

The marshalling is correct across the board:

**Transposition correctness.** Every 2D numpy input passes through `convert::numpy2d_to_fdmatrix`. Every FdMatrix result is returned via `convert::fdmatrix_to_numpy2d`. The test fixture is deliberately non-square (40×25) to expose row/col swap bugs; a transposed result would break the shape assertions. No hand-rolled reshape was found.

**Three documented conversion gotchas — all correct.**
- `FacfResult.lags` `Vec<u32>` is cast to `Vec<i64>` before `PyArray1::from_vec`. The `vec_to_numpy1d` helper (for `Vec<f64>`) is correctly avoided.
- `LongRunCovResult.cov_matrix` (flat column-major) is reshaped via `FdMatrix::from_column_major(cov_matrix, m, m)` then `fdmatrix_to_numpy2d`. The symmetry test in `test_long_run_covariance_shape_and_symmetry` would catch a naive row-major reshape.
- `SpectralDensityResult.re`/`im` (per-frequency `Vec<Vec<f64>>`) are each processed with `FdMatrix::from_column_major(freq_re.clone(), m, m)` before `fdmatrix_to_numpy2d`. This is the correct column-major reshape.

**Combined-function pattern.** `ftsm_forecast`, `ftsm_forecast_multistep`, `ftsm_update`, and `dpca_reconstruct` all correctly call the internal fit function first, then the downstream function, using the same `ncomp`/`argvals`/`bandwidth`/`filter_lag` parameters in both calls. No mismatch found.

**PyDict field names.** All 13 functions' PyDict keys were cross-checked against the verbatim struct field tables in the research document (§4 and §11). Every key matches exactly. `functional_difference` correctly returns a naked `PyArray2<f64>` (no PyDict).

**Error handling.** All 13 functions propagate errors via `to_pyresult(fdars_core::fts::<fn>(...)?)`. No `unwrap()`, `expect()`, or `panic!()` were found in `fts_mod.rs`. The pre-existing `unwrap()` in `convert::fdmatrix_to_numpy2d` (line 57) is not introduced by this phase.

**Rust quality.** All imports are used. The `fdars_core::matrix::FdMatrix::from_column_major` fully-qualified path is an established pattern (precedent in `smoothing_mod.rs:250`). `numpy::PyArray1::from_vec` is correctly used with the full `numpy::` namespace since `PyArray1` is not in scope from the import list. Both private helpers (`ftsm_result_to_dict`, `dpca_result_to_dict`) take `&ref` (not by value), which is correct — `dpca` and `dpca_reconstruct` both need to borrow `DpcaResult` after the dict is built.

**Registration.** `mod fts_mod;` and `register_submodule!(m, "fts", fts_mod::register)` in `lib.rs`, and `"fts"` in `__init__.py`'s `_submodule_names`, are consistent and correctly ordered relative to each other.

**Tests.** All 14 test categories from the research §12 requirements are covered. Error-guard tests for `ncomp=0`, `n_perm=0`, and `n_sim=0` are present. The cumsum round-trip test logic is correct. The `reconstruction_error` monotone check uses a 1e-12 tolerance appropriate for floating-point non-increasing values. The symmetry check for `cov_matrix` correctly validates the column-major reshape.

Two stale doc comment strings are noted below; they are the only findings.

---

## Info

### IN-01: Stale module doc comment claims Plan 67-04 is future work

**File:** `src/fts_mod.rs:11`
**Issue:** The module-level doc comment reads:
```
//! Plan 67-04 will extend `register()` with spectral density and DPCA functions.
```
In the delivered implementation, `spectral_density`, `dpca`, and `dpca_reconstruct` are already registered in `register()` (lines 731-733). The "will extend" language is a vestige of incremental plan drafting and is now factually incorrect.
**Fix:** Replace line 11 with:
```rust
//! Plan 67-04: `spectral_density`, `dpca`, `dpca_reconstruct` added.
```

### IN-02: Stale test file docstring claims Plan 67-04 tests are not yet written

**File:** `tests/test_fts.py:12`
**Issue:** The module docstring says:
```
Plan 67-04 will APPEND spectral density and DPCA tests to this same file.
```
Those tests are already present in the file (lines 386-528). The comment contradicts the file content.
**Fix:** Update line 12 to:
```python
Plan 67-04: spectral density and DPCA tests added below (lines 386-528).
```

---

_Reviewed: 2026-09-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
