---
phase: 21-per-aspect-advisor-coverage
plan: "04"
subsystem: advisor
tags: [regression, regression_cv, diagnostics, aspect, tdd]
status: complete

dependency_graph:
  requires: [21-03]
  provides: [regression-aspect, regression_cv-aspect]
  affects: [advisor/__init__.py, advisor/aspects/regression.py, advisor/aspects/regression_cv.py]

tech_stack:
  added: []
  patterns:
    - pure-NumPy skewness (m3/m2^1.5, no scipy)
    - pure-NumPy elbow detection (interior strict minimum, no signal library)
    - guarded key access pattern for variably-shaped result dicts

key_files:
  created:
    - python/fdars/advisor/aspects/regression.py
    - python/fdars/advisor/aspects/regression_cv.py
  modified:
    - python/fdars/advisor/__init__.py
    - tests/test_advisor.py

decisions:
  - regression and regression_cv builders placed in dedicated aspect files
    matching the established aspects/ pattern (one file per aspect)
  - Tests placed in new TestRegression class matching the per-wave class
    convention (TestOutliersAndClassification, TestRepresent from prior waves)
  - elbow_present computed with strict interior-minimum check: arr[i] < arr[i-1]
    AND arr[i] < arr[i+1] for i in [1, n-2]; no peak-finding library needed
  - _prompts.py already had regression + regression_cv primer clauses from
    prior work — no changes needed there; only __init__.py required the new
    dispatch branches and _supported set additions

metrics:
  duration: ~20 minutes
  completed: "2026-08-12"
  tasks_completed: 3
  commits: 2
  files_created: 2
  files_modified: 2

actuals:
  tokens: 8500
  tasks: 3
  commits: 2

requirements: [ASPECT-04, ASPECT-06]
---

# Phase 21 Plan 04: Regression + Regression CV Aspects Summary

Implemented two MEDIUM-complexity advisor aspects covering functional regression and regression cross-validation diagnostics (ASPECT-04), with all four RESEARCH-identified corrections applied.

## What Was Built

**`python/fdars/advisor/aspects/regression.py`** — `_build_regression_diagnostics(raw, **kwargs) -> dict`

Handles all six regression variants from fdars:
- `fregre_lm` / `fregre_pls` — fitted_values (1-D), r_squared present
- `fregre_l1` / `fregre_huber` — no r_squared (guarded, correction #3)
- `fregre_np` — fitted_values + h_func, no beta_t
- `fosr` / `fosr_fpc` — 2-D fitted + 2-D residuals, key "fitted" not "fitted_values" (corrections #4, #5)

Fields emitted: `method`, `n_obs`, `r_squared`, `residual_mean`, `residual_std`, `residual_max_abs`, `residual_skew`, `beta_t_range`, `has_fosr`.

**`python/fdars/advisor/aspects/regression_cv.py`** — `_build_regression_cv_diagnostics(raw, **kwargs) -> dict`

Handles both CV source functions:
- `fregre_cv` — numpy array casts to Python lists (correction #7), elbow detection
- `model_selection_ncomp` — GCV extracted from `criteria` tuple index 3

Fields emitted: `method`, `optimal_k`, `min_cv_error`, `cv_curve`, `k_values`, `cv_curve_range`, `elbow_present`.

**`python/fdars/advisor/__init__.py`** — `_supported` set extended with `"regression"` and `"regression_cv"` + two lazy-import dispatch branches.

**`tests/test_advisor.py`** — `TestRegression` class with 10 tests.

## Key Guards Implemented (Corrections from RESEARCH)

### Correction #3 — r_squared guarded (l1/huber have no r_squared)
```python
diag["r_squared"] = float(raw["r_squared"]) if "r_squared" in raw else None
```
Proven by `test_regression_fregre_l1_no_r_squared`: r_squared=None, no KeyError.

### Correction #4 — 1-D residual guard (fosr residuals are 2-D)
```python
res = np.asarray(raw.get("residuals", []))
if res.ndim == 1 and res.size > 0:
    # compute residual_mean/std/max_abs/skew
else:
    # emit None for all residual stats
```
Proven by `test_regression_fosr_2d_residuals`: `residual_mean=None` when residuals are shape (4,6).

### Correction #5 — fosr detection via "fitted" key + ndim==2 guard
```python
has_fosr = "fitted" in raw and np.asarray(raw["fitted"]).ndim == 2
```
Proven by two tests:
- `test_regression_fosr_2d_residuals`: 2-D fitted → `has_fosr=True`
- `test_regression_1d_fitted_not_fosr`: 1-D fitted → `has_fosr=False` (the critical guard)

### Correction #7 — numpy array to Python list cast (fregre_cv)
```python
diag["cv_curve"] = [float(v) for v in raw.get("cv_errors", [])]
diag["k_values"] = [int(v) for v in raw.get("k_values", [])]
```
Proven by `test_regression_cv_fregre_cv_basic`: `k_values == [1,2,3,4,5]` (native ints).

## Determinism Confirmed

- `test_regression_deterministic`: fregre_lm fixture → equal dicts, byte-identical `json.dumps(sort_keys=True)`, no numpy scalars; l1 fixture → r_squared=None confirmed.
- `test_regression_cv_deterministic`: fregre_cv fixture → equal dicts, byte-identical JSON, no numpy scalars, elbow_present=True.

## Prompt Clauses (ASPECT-06)

`_prompts.py` already had the `regression` and `regression_cv` clauses (added in prior wave work):
- `_system_prompt("interpretation", "regression")` contains `"r_squared"` ✓
- `_system_prompt("interpretation", "regression_cv")` contains `"optimal_k"` ✓
- Both tokens absent from base prompt (aspect="") ✓

## Test Results

Full suite: **221 passed, 4 skipped** (0 failures).

TestRegression suite: **10/10 passed**.

```
tests/test_advisor.py::TestRegression::test_regression_fregre_lm_basic PASSED
tests/test_advisor.py::TestRegression::test_regression_fregre_l1_no_r_squared PASSED
tests/test_advisor.py::TestRegression::test_regression_fosr_2d_residuals PASSED
tests/test_advisor.py::TestRegression::test_regression_1d_fitted_not_fosr PASSED
tests/test_advisor.py::TestRegression::test_regression_deterministic PASSED
tests/test_advisor.py::TestRegression::test_regression_cv_fregre_cv_basic PASSED
tests/test_advisor.py::TestRegression::test_regression_cv_model_selection_ncomp PASSED
tests/test_advisor.py::TestRegression::test_regression_cv_deterministic PASSED
tests/test_advisor.py::TestRegression::test_regression_prompt_clause PASSED
tests/test_advisor.py::TestRegression::test_regression_cv_prompt_clause PASSED
```

## Deviations from Plan

### Minor — Test class naming (no behavior change)

**Task 3 verify command** in the plan specified:
```
pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_regression_deterministic
```

**Actual placement:** Tests went into a new `TestRegression` class, matching the convention established by waves 2/3 (`TestOutliersAndClassification`, `TestRepresent` as separate classes per wave). `TestBuildDiagnosticsOffline` is the original class that holds pre-wave-1 baseline tests; adding 10 regression-specific tests there would have been inconsistent with the pattern.

The tests cover all behaviors specified: two-call equality, byte-identical JSON, no numpy scalars, r_squared=None path, elbow_present assertion.

## Known Stubs

None. All fields are wired to real computation; no placeholder or hardcoded values.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. The regression builder makes no fdars live calls (unlike the upcoming SPM builder). Only pure NumPy computation over caller-supplied dicts. Threat T-21-06 mitigated: all key accesses guarded with `if "key" in raw else None` pattern.

## Self-Check

- FOUND: python/fdars/advisor/aspects/regression.py
- FOUND: python/fdars/advisor/aspects/regression_cv.py
- FOUND commit ff4b417: feat(21-04): regression + regression_cv builders, dispatch, prompt clause
- FOUND commit 0519da9: test(21-04): add failing RED-gate tests for regression + regression_cv aspects
- Full suite: 221 passed, 4 skipped

## Self-Check: PASSED
