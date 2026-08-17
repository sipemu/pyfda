---
phase: 27-scoring-metrics-alignment-registration-bindings
plan: "01"
subsystem: scoring
tags: [rust, pyo3, fdars-core, scoring, functional-data, STAT-03]

dependency_graph:
  requires:
    - Phase 25 (fdars-core 0.17.0 upgrade baseline — 328 passed / 4 skipped)
    - Phase 26 (fdars.represent reference pattern for new submodules)
  provides:
    - fdars.scoring submodule with 5 Simpson-integrated prediction-scoring metrics
    - STAT-03 requirement satisfied
  affects:
    - src/lib.rs (new mod + register_submodule!)
    - python/fdars/__init__.py (_submodule_names tuple extended)

tech_stack:
  added:
    - src/scoring_mod.rs (NEW PyO3 module; 5 #[pyfunction]s)
  patterns:
    - Thin PyO3 wrappers: PyReadonlyArray2 inputs → numpy2d_to_fdmatrix → fdars_core::functional_* → to_pyresult → f64
    - TDD RED/GREEN for Task 2 expansion

key_files:
  created:
    - src/scoring_mod.rs
    - tests/test_scoring.py
  modified:
    - src/lib.rs (mod scoring_mod + register_submodule! entry)
    - python/fdars/__init__.py ("scoring" added to _submodule_names)

decisions:
  - Tracer bound only functional_mse end-to-end before expanding; integration gate passed before Task 2 began
  - All 5 metrics share identical wrapper shape: (y_true, y_pred, argvals) → PyResult<f64>; no matrix output, so fdmatrix_to_numpy2d not used
  - _py parameter kept as Python<'py> in signature for PyO3 lifetime consistency despite not being used in scalar-return functions
  - TDD cycle used for Task 2: RED commit (d6582fe) then GREEN commit (c24c0ae)

metrics:
  duration: "7m"
  completed: "2026-08-15"
  tasks_completed: 2
  tasks_total: 2
  commits: 3
  files_changed: 4

status: complete

actuals:
  tokens: 9800
  tasks: 2
  commits: 3
---

# Phase 27 Plan 01: Scoring Metrics Submodule Summary

**One-liner:** Five Simpson-integrated prediction-scoring metrics (`functional_mae/mse/mape/msle/explained_variance`) bound in a new `fdars.scoring` PyO3 submodule with MAPE/MSLE `ValueError` guards and zero `.unwrap()` calls.

## What Was Built

Implemented STAT-03: new `fdars.scoring` native submodule binding all 5 fdars-core 0.17.0 functional scoring metrics.

### Artifacts Produced

| Artifact | Description |
|----------|-------------|
| `src/scoring_mod.rs` (NEW) | PyO3 module: 5 `#[pyfunction]`s + `register()` fn; no `.unwrap()` |
| `tests/test_scoring.py` (NEW) | 23 pytest tests: namespace, hand-checked MSE=0, analytic values, ValueError guards, argument-order contract |
| `src/lib.rs` | `mod scoring_mod;` + `register_submodule!(m, "scoring", scoring_mod::register)` |
| `python/fdars/__init__.py` | `"scoring"` added to `_submodule_names` tuple |

### Functions Bound

| Function | Description | Fallible input |
|----------|-------------|---------------|
| `functional_mae` | Simpson-integrated MAE over (y_true, y_pred, argvals) | shape mismatch |
| `functional_mse` | Simpson-integrated MSE | shape mismatch |
| `functional_mape` | Simpson-integrated MAPE | near-zero y_true → ValueError |
| `functional_msle` | Simpson-integrated MSLE | y_true or y_pred ≤ -1 → ValueError |
| `functional_explained_variance` | 1 − SS_res/SS_tot averaged over curves | shape mismatch |

## Verification Results

All acceptance criteria passed:

- `fdars.scoring.functional_mse(X, X, argvals) == pytest.approx(0.0, abs=1e-12)` for 2-curve sinusoidal data
- Known-offset analytic: constant offset c → MSE = c², two-curve average = (c1² + c2²)/2
- `pytest.raises(ValueError)` for MAPE with y_true = 0 (near-zero guard fires on y_true, not y_pred)
- `pytest.raises(ValueError)` for MSLE with y_true = -1.5 and y_pred = -1.5
- `functional_explained_variance(X, X)` = pytest.approx(1.0, abs=1e-10)
- `grep -v '^\s*//' src/scoring_mod.rs | grep -c 'unwrap()'` returns `0`
- Both import paths resolve: `from fdars.scoring import functional_mse` and `fdars.scoring.functional_mse`
- Full suite: **351 passed, 4 skipped** (baseline 328 + 23 new scoring tests; zero regressions)

## Commits

| Hash | Type | Description |
|------|------|-------------|
| f5db529 | feat (tracer) | Stand up fdars.scoring with functional_mse + hand-checked assertions |
| d6582fe | test (RED) | Add failing tests for 4 remaining scoring metrics |
| c24c0ae | feat (GREEN) | Expand — bind 4 remaining metrics with MAPE/MSLE ValueError guards |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Fix] Test file initially imported all 5 functions at module level**

- **Found during:** Task 1 tracer test run
- **Issue:** `tests/test_scoring.py` imported `functional_mae/mape/msle/explained_variance` in the module-level import block, causing `ImportError` before tracer tests could run (only `functional_mse` was registered at that point)
- **Fix:** Limited the tracer-phase test file to `from fdars.scoring import functional_mse` only; the 4 additional test classes and imports were added in the RED commit of Task 2 (the correct TDD order)
- **Files modified:** `tests/test_scoring.py`
- **Commits:** All 3 plan commits

## TDD Gate Compliance

Task 2 completed the full RED/GREEN cycle:
- RED gate commit: d6582fe (`test(27-01): add failing tests for 4 remaining scoring metrics`)
- GREEN gate commit: c24c0ae (`feat(27-01): expand — bind 4 remaining metrics`)
- REFACTOR: No structural refactoring needed; code was clean from the start.

## Known Stubs

None. All 5 metrics are fully wired to fdars-core 0.17.0 functions. No placeholder returns.

## Threat Mitigations Applied

| Threat ID | Status | Evidence |
|-----------|--------|---------|
| T-27-01-01 | Mitigated | `grep -c 'unwrap()'` = 0; `pytest.raises(ValueError)` for MAPE and MSLE |
| T-27-01-02 | Mitigated | `test_raises_on_y_true_not_y_pred` confirms zero-guard fires on first positional arg (y_true) |
| T-27-01-03 | Mitigated | Hand-checked `functional_mse(X,X)==0`; analytic constant-offset MSE = c² verified |

## Self-Check: PASSED

| Item | Status |
|------|--------|
| src/scoring_mod.rs | FOUND |
| tests/test_scoring.py | FOUND |
| 27-01-SUMMARY.md | FOUND |
| commit f5db529 | FOUND |
| commit d6582fe | FOUND |
| commit c24c0ae | FOUND |
