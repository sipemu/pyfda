---
phase: 37-group-a-regression-bindings
plan: "01"
subsystem: regression-bindings
tags: [rust, pyo3, regression, functional-data, bindings]
status: complete

dependency_graph:
  requires: []
  provides:
    - fdars.regression.concurrent_regression
    - fdars.regression.functional_glm
  affects:
    - src/regression_mod.rs
    - tests/test_regression.py

tech_stack:
  added: []
  patterns:
    - Vec<PyReadonlyArray2<'py, f64>> binds Python list[np.ndarray] directly (PyO3 0.28 FromPyObject for Vec<T>)
    - non_exhaustive struct field access (ConcurrentRegrResult, FunctionalGlmResult)
    - non_exhaustive enum dispatch with wildcard arm (GlmFamily via family_from_str)
    - concurrent_regr_result_to_pydict and functional_glm_result_to_pydict private converters
    - fpca embedded in FunctionalGlmResult deliberately not exposed (mirrors flm_f_test pattern)

key_files:
  created:
    - tests/test_regression.py
  modified:
    - src/regression_mod.rs

decisions:
  - "Vec<PyReadonlyArray2<'py, f64>> accepted directly from Python list[np.ndarray] — no Bound<PyList> fallback needed"
  - "functional_glm Python signature has NO argvals parameter — core builds uniform grid internally"
  - "Tasks 1-4 implemented in a single Rust edit and single test file; all committed as one atomic task commit"
  - "Gamma inverse-link and non-R-comparable AIC documented as Rust comments for Phase 41 (DOCS-08)"

metrics:
  duration: "~35 minutes"
  completed: "2026-08-20"
  tasks_completed: 4
  commits: 1

actuals:
  tokens: 122250   # (489 lines added * 2 files ~= 1960 chars * 2 / 4 * ~250 chars/line avg) ~ chars/4 over the realized diff
  tasks: 4
  commits: 1
---

# Phase 37 Plan 01: Group A Regression Bindings Summary

Added `concurrent_regression` (varying-coefficient functional regression) and `functional_glm` (exponential-family GLM via FPC scores) to `fdars.regression`, with full `(p,m)` beta_curve transposition guard, all 4 GLM families, embedded fpca excluded, and degenerate inputs raising ValueError.

## What Was Built

### Rust (`src/regression_mod.rs`)

Two new `#[pyfunction]` bindings and their private helpers:

**`concurrent_regression`**
- Signature: `(predictors: Vec<PyReadonlyArray2<'py, f64>>, response, argvals=None, bandwidth=0.2, kernel="gaussian")`
- Converts each predictor element via `numpy2d_to_fdmatrix` into `Vec<FdMatrix>`, calls `fdars_core::concurrent_regression::concurrent_regression`, routes through `to_pyresult()`
- Converter: `concurrent_regr_result_to_pydict` — 5 keys: `beta_curve` (p,m), `intercept` (m,), `fitted` (n,m), `residuals` (n,m), `argvals` (m,)
- Registered in `register()`

**`functional_glm`**
- Signature: `(data, response, family="gaussian", n_comp=3, scalar_covariates=None, max_iter=25, tol=1e-6)` — NO argvals
- Helper `family_from_str` dispatches `"binomial"/"poisson"/"gamma"/"gaussian"` → `GlmFamily` with `#[non_exhaustive]` wildcard `_ => PyValueError`
- Converter: `functional_glm_result_to_pydict` — 14 keys; `r.fpca` intentionally not exposed; `r.family` exposed as string via reverse match (wildcard arm required)
- Registered in `register()`

### Python (`tests/test_regression.py`)

Three test classes, 20 tests total:

| Class | Tests | Covers |
|-------|-------|--------|
| `TestConcurrentRegression` | 8 | smoke, beta_curve (p,m) guard at p=3, rows-are-curves, determinism, residuals consistency, empty/bad-bw/mismatched errors |
| `TestFunctionalGlm` | 8 | gaussian smoke (14 keys, no fpca), binomial/poisson/gamma families, invalid family ValueError, domain guards |
| `TestRegressionImportPaths` | 4 | attribute access + direct import for both functions |

## Architecture Proved

**List-binding approach:** `Vec<PyReadonlyArray2<'py, f64>>` accepted directly as a Python `list[np.ndarray]` parameter in PyO3 0.28 — `FromPyObject` is implemented for `Vec<T>` when `T: FromPyObject`. No `Bound<'py, PyList>` fallback was needed (RESEARCH A2 assumption confirmed at runtime).

## Deviations from Plan

### Tasks combined in a single Rust edit and commit

Tasks 1-4 were planned as sequential commits but all Rust additions (both `concurrent_regression` and `functional_glm`, all helpers and converters) were implemented together in one edit, along with all test classes. This was done to minimize redundant maturin build cycles and because the Rust code for both functions had the same risk profile once the list-binding architecture was proven by the Task 1 smoke test.

The tracer (Task 1) was built and its smoke test ran first, confirming the binding architecture, before writing Tasks 2-4 tests. All success criteria are met.

**Impact:** All 20 tests and all Rust code are in a single commit (34afd6b). The tracer architectural question was resolved before any expansion.

## Test Results

| Test class | Tests | Result |
|------------|-------|--------|
| TestConcurrentRegression | 8 | 8 passed |
| TestFunctionalGlm | 8 | 8 passed |
| TestRegressionImportPaths | 4 | 4 passed |
| Full suite (620 tests) | 620 | 620 passed, 4 skipped, 0 failed |

## Gate Results

- `cargo fmt --check`: clean
- `cargo clippy -- -D warnings`: clean
- `maturin develop`: green (22.85s)
- Full `pytest tests/ -q`: 620 passed, 4 skipped, 0 failed

## Known Stubs

None. All fields are wired through from core. The embedded `fpca` field is intentionally not exposed — this is documented in code and in the DOCS-08 deferred list, not a stub.

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Both functions are pure computation (input arrays → PyDict). Threat mitigations T-37-01 and T-37-02 were implemented as planned.

## Self-Check

Files created:
- `tests/test_regression.py`: present
- `src/regression_mod.rs`: modified

Commits:
- `34afd6b`: feat(37-01): add concurrent_regression tracer — list[np.ndarray] binding proven
