---
phase: 26-interpolation-imputation-functional-statistics-bindings
plan: "02"
subsystem: fdata-stats
tags: [rust, pyo3, fdars-core, functional-statistics, variance, covariance, depth-median]
status: complete

dependency_graph:
  requires:
    - 26-01 (Fdata.interpolate/impute already appended to fdata_class.py)
  provides:
    - fdars.fdata.functional_variance (pointwise Bessel-corrected, length-m)
    - fdars.fdata.functional_std (same shape, std²==var)
    - fdars.fdata.functional_covariance (m×m, layout-correct via fdmatrix_to_numpy2d)
    - fdars.fdata.depth_based_median (resolves usize → actual curve row)
    - fdars.fdata.trim_mean (alpha=0 == mean_1d exactly)
    - Fdata.var(), Fdata.std(), Fdata.cov(), Fdata.median() convenience methods
  affects:
    - src/fdata_mod.rs (5 new pyfunctions + register lines)
    - python/fdars/fdata_class.py (4 new Fdata methods)
    - tests/test_fdata_stats.py (33 new tests)

tech_stack:
  added:
    - fdars_core::fdata::functional_variance (Result<Vec<f64>, FdarError>)
    - fdars_core::fdata::functional_std (Result<Vec<f64>, FdarError>)
    - fdars_core::fdata::functional_covariance (Result<FdMatrix, FdarError>)
    - fdars_core::fdata::depth_based_median (Result<usize, FdarError> — index resolved to curve)
    - fdars_core::fdata::trim_mean (Result<Vec<f64>, FdarError>)
  patterns:
    - to_pyresult() on every Result<_, FdarError> — zero .unwrap() calls
    - fdmatrix_to_numpy2d for all 2-D returns (column-major #33 transposition guard)
    - mat.row(idx) to resolve depth_based_median usize → Vec<f64> curve
    - Fdata.median() wraps curve in curve[np.newaxis, :] → single-obs Fdata

key_files:
  modified:
    - src/fdata_mod.rs: 5 new pyfunctions (functional_variance, functional_std,
      functional_covariance, depth_based_median, trim_mean) + 5 register lines
    - python/fdars/fdata_class.py: Fdata.var(), .std(), .cov(), .median() methods
  created:
    - tests/test_fdata_stats.py: 33 tests (variance/std identity, covariance
      transposition guard, depth median resolves curve, trim_mean alpha=0 identity,
      all degenerate-input ValueError tests)

decisions:
  - depth_based_median resolves via mat.row(idx) (FdMatrix::row returns Vec<f64>
    directly — no .to_vec() needed); index never leaks to Python
  - fd.median() returns an Fdata row (n_obs=1) carrying original argvals/rangeval,
    id=["median"], metadata=None — per CONTEXT.md locked decision
  - All 5 pyfunctions follow the same no-suffix naming convention (no _1d) since
    these are statistics over the observation dimension, not function of spatial dims
  - trim_mean test dataset enlarged to 10 obs (from 4) so alpha=0.2 actually
    trims a curve (floor(0.2*n) >= 1 requires n >= 5)

metrics:
  duration: "~6 minutes"
  completed: "2026-08-15"
  tasks: 3
  commits: 3

actuals:
  tokens: 15000
  tasks: 3
  commits: 3
---

# Phase 26 Plan 02: Functional Statistics Bindings Summary

Bound fdars-core 0.17.0 functional statistics — pointwise variance/std, the m×m
covariance surface, the depth-based median (index resolved to the curve), and the
depth-trimmed mean — into the existing `fdars.fdata` submodule, plus `fd.var()`,
`fd.std()`, `fd.cov()`, `fd.median()` convenience methods.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Bind functional_variance/std + Fdata.var()/std() (STAT-01 part) | 295a267 | src/fdata_mod.rs, python/fdars/fdata_class.py, tests/test_fdata_stats.py (NEW) |
| 2 | Bind functional_covariance m×m + Fdata.cov() (STAT-01 part) | a4d4d99 | src/fdata_mod.rs, python/fdars/fdata_class.py |
| 3 | Bind depth_based_median (idx→curve) + trim_mean + Fdata.median() (STAT-02) | 3281562 | src/fdata_mod.rs, python/fdars/fdata_class.py, tests/test_fdata_stats.py |

## What Was Built

**Five new `#[pyfunction]`s in `src/fdata_mod.rs`** (all under `fdars.fdata.*`):

1. `functional_variance(data)` — Bessel-corrected pointwise variance; `Result<Vec<f64>>`;
   raises `ValueError` for n<2.
2. `functional_std(data)` — Bessel-corrected pointwise std; `Result<Vec<f64>>`; raises
   `ValueError` for n<2; satisfies `std²==var` pointwise.
3. `functional_covariance(data)` — Bessel-corrected m×m covariance surface; `Result<FdMatrix>`;
   returned via `fdmatrix_to_numpy2d` (column-major #33 transposition guard); diagonal equals
   `functional_variance`; raises `ValueError` for n<2.
4. `depth_based_median(data)` — Fraiman-Muniz deepest observation; `Result<usize>` from core;
   usize resolved to `mat.row(idx)` before returning — a bare integer never crosses to Python;
   returns a 1-D float array equal to one of the input rows.
5. `trim_mean(data, alpha=0.0)` — depth-trimmed mean; `Result<Vec<f64>>`; alpha=0.0 equals
   `mean_1d` exactly (asserted); raises `ValueError` for alpha outside [0, 1).

**Four new Fdata methods in `python/fdars/fdata_class.py`**:
- `Fdata.var()` — delegates to `functional_variance(self.data)`, returns 1-D array.
- `Fdata.std()` — delegates to `functional_std(self.data)`, returns 1-D array.
- `Fdata.cov()` — delegates to `functional_covariance(self.data)`, returns m×m array.
- `Fdata.median()` — delegates to `depth_based_median(self.data)`, wraps resolved curve
  in a single-row `Fdata` carrying `self.argvals`/`rangeval` (per CONTEXT.md decision).

**Tests `tests/test_fdata_stats.py`** — 33 tests across 4 test classes:
- `TestFunctionalVariance`: std²==var identity, Bessel-corrected hand values (var=2.0 for
  symmetric 2-row dataset), n<2 raises ValueError, Fdata methods return length-m arrays.
- `TestFunctionalCovariance`: shape (m,m), diag==var (layout guard), known off-diagonal
  cov[0,1]=7/3 hand-computed, symmetry, n<2 raises ValueError, multi-curve transposition
  round-trip (5 curves × 4 points with distinct structures).
- `TestDepthBasedMedian`: returns 1-D float array, not int; result equals one of the
  observed rows; fd.median() returns Fdata with n_obs=1, correct n_points and argvals.
- `TestTrimMean`: alpha=0 == mean_1d exactly (two datasets), alpha=0.2 differs from mean
  on outlier dataset (10 obs), alpha outside [0,1) raises ValueError.

## Deviations from Plan

**1. [Rule 1 - Adaptation] trim_mean outlier test dataset size enlarged**
- **Found during:** Task 3 test run
- **Issue:** With n=4 observations, `floor(0.2 * 4) = 0` — no curves get trimmed at
  alpha=0.2. The test `test_trim_mean_alpha_positive_differs_from_mean_with_outlier`
  was correctly failing because no trimming occurred.
- **Fix:** Enlarged X_OUT from 4 to 10 observations (`floor(0.2 * 10) = 2`), ensuring
  the outlier row is actually trimmed at alpha=0.2. Test now reliably passes.
- **Files modified:** tests/test_fdata_stats.py
- **Commit:** 3281562

## Verification

- `fdars.fdata.functional_variance`, `.functional_std`, `.functional_covariance`,
  `.depth_based_median`, `.trim_mean` all reachable.
- `Fdata.var()`, `.std()`, `.cov()`, `.median()` all reachable on an Fdata instance.
- `std(X)**2 == var(X)` pointwise (allclose rtol=1e-12).
- `diag(functional_covariance(X)) == functional_variance(X)` element-wise.
- `depth_based_median(X)` returns shape `(m,)`, dtype float, equal to an observed row.
- `trim_mean(X, 0.0)` equals `mean_1d(X)` (allclose atol=1e-15).
- alpha outside [0, 1) raises ValueError.
- n<2 raises ValueError for variance/covariance.
- `grep -v '^\s*//' src/fdata_mod.rs | grep -c '.unwrap()'` → 0.
- Full suite: **328 passed, 4 skipped** (295 baseline + 33 new — no regressions).

## Known Stubs

None. All functionality is fully wired.

## Threat Flags

None identified beyond the threat model in the plan (T-26-04 through T-26-06 all mitigated).

## Self-Check

- [x] `src/fdata_mod.rs` builds green with 5 new pyfunctions
- [x] `python/fdars/fdata_class.py` has Fdata.var/std/cov/median
- [x] `tests/test_fdata_stats.py` exists with 33 tests, all passing
- [x] Commit 295a267 exists (Task 1)
- [x] Commit a4d4d99 exists (Task 2)
- [x] Commit 3281562 exists (Task 3)
- [x] 328 passed, 4 skipped — no regressions vs 295-baseline
- [x] `.unwrap()` count in new fdata_mod.rs functions: 0
