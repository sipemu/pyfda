---
phase: 57-regressors-classifiers
plan: "01"
subsystem: sklearn-regressors
status: complete
tags: [sklearn, regressors, compliance, fpc, pls, parametrize_with_checks]
dependency_graph:
  requires: []
  provides:
    - "_require_y(estimator, y) — shared y=None guard at module scope in _skeletons.py"
    - "FPCRegressor: stored-model predict, n_components=10 default, PASS"
    - "PLSRegressor: _require_y guard, PASS"
    - "tests/sklearn/test_regressors_compliance.py — per-estimator compliance harness"
  affects:
    - "python/fdars/sklearn/_skeletons.py"
    - "python/fdars/sklearn/_coverage.py"
    - "tests/sklearn/test_regressors_compliance.py"
tech_stack:
  added: []
  patterns:
    - "stored-model predict: predict_fregre_lm(X_fit_, y_fit_, X_new, n_comp) re-fits on stored train only — subset-invariant by construction, no vstack"
    - "shared _require_y(estimator, y) guard raises ValueError with sklearn-required substring before any array coercion"
    - "n_components default raised to 10 (FPCRegressor) to clear check_regressors_train R2 > 0.5 threshold on battery data"
key_files:
  created:
    - "tests/sklearn/test_regressors_compliance.py — per-estimator parametrize_with_checks harness for FPCRegressor + PLSRegressor"
  modified:
    - "python/fdars/sklearn/_skeletons.py — _require_y helper added; FPCRegressor n_components default 3→10 + _require_y in fit; PLSRegressor _require_y in fit"
    - "python/fdars/sklearn/_coverage.py — FPCRegressor + PLSRegressor verdicts flipped to PASS with Phase-57 fix notes"
decisions:
  - "Raise FPCRegressor default n_components from 3 to 10: with min(n_components, n_obs-1, n_pts) cap in fit, this gives R2>0.5 on battery data while keeping small-sample edge cases safe"
  - "PLSRegressor keeps n_components=3 default: PLS converges fast enough to pass check_regressors_train at this value"
  - "_require_y message uses sklearn-required substring 'requires y to be passed, but the target y is None' verbatim"
  - "score() not overridden in either regressor: RegressorMixin.score(X, y) = r2_score(y, self.predict(X)) is correct as-is"
metrics:
  duration: "4m24s"
  completed: "2026-08-31T20:24:43Z"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
actuals:
  tokens: 8500
  tasks: 3
  commits: 3
---

# Phase 57 Plan 01: Regressors Tracer — FPCRegressor + PLSRegressor Full Compliance

Promote FPCRegressor to `parametrize_with_checks`-green via stored-model predict + raised `n_components` default + shared `_require_y` guard; bring PLSRegressor to full compliance with the same guard; establish the shared helper for every remaining predictor in Plans 02+; flip both verdicts to PASS in `_coverage.py`.

## Tasks Completed

| # | Task | Commit | Files | Status |
|---|------|--------|-------|--------|
| 1 | _require_y helper + FPCRegressor full compliance | `686f350` | `_skeletons.py`, `test_regressors_compliance.py` | PASS |
| 2 | PLSRegressor _require_y guard + full compliance | `eb9b73a` | `_skeletons.py` | PASS |
| 3 | Flip verdicts to PASS + harness verification | `ffbe751` | `_coverage.py` | PASS |

## What Was Built

### `_require_y(estimator, y)` — shared y=None guard

Added at module scope next to `_pairwise_l2` in `_skeletons.py`. Raises:
```python
ValueError(f"{type(estimator).__name__} requires y to be passed, but the target y is None.")
```
The message contains the sklearn-required substring `"requires y to be passed, but the target y is None"` so `check_requires_y_none` passes. Called as the first statement in `fit` before `_validate` — fires before any array coercion.

### FPCRegressor changes

- `n_components` default raised from `3` to `10`: with the existing `n_comp = min(self.n_components, n_obs-1, n_pts)` cap in `fit`, this achieves R² > 0.5 on sklearn's battery data (~100 obs, ~20 features) while remaining safe for tiny samples.
- `_require_y(self, y)` added as first statement in `fit`.
- `predict` unchanged: `predict_fregre_lm(X_fit_, y_fit_, X, n_components_)` re-fits on stored train only — subset-invariant, no `vstack`.
- `score()` not overridden; inherited from `RegressorMixin`.

### PLSRegressor changes

- `_require_y(self, y)` added as first statement in `fit` — single-line fix.
- Everything else unchanged: `predict_fregre_pls(X_fit_, argvals_, y_fit_, X, n_comp_)` already subset-invariant; `n_components=3` already achieves R² > 0.5.

### Compliance harness

`tests/sklearn/test_regressors_compliance.py` mirrors `test_transformers_compliance.py`:
- `test_fpc_regressor_compliance` — `@parametrize_with_checks([FPCRegressor()])` — 52/52 green
- `test_pls_regressor_compliance` — `@parametrize_with_checks([PLSRegressor()])` — 52/52 green

### Coverage verdicts

`_coverage.py` `TRIAGE_VERDICTS`:
- `"FPCRegressor": "PASS"` — with Phase-57 fix notes
- `"PLSRegressor": "PASS"` — with Phase-57 fix notes

## Verification Results

```
pytest tests/sklearn/test_regressors_compliance.py -q
104 passed in 0.50s

pytest tests/sklearn/test_coverage.py -q
96 passed in 0.14s

python -c "from fdars.sklearn._coverage import TRIAGE_VERDICTS as v;
           assert v['FPCRegressor']=='PASS' and v['PLSRegressor']=='PASS'"
verdicts: OK
```

Acceptance criteria:
- `_require_y` at module scope: PASS
- `FPCRegressor().fit(X, None)` raises `ValueError("...requires y to be passed, but the target y is None...")`): PASS
- `FPCRegressor.predict` contains no `vstack`: PASS
- `predict(X[mask]) == predict(X)[mask]` for both: PASS
- `score()` not defined on FPCRegressor or PLSRegressor (inherited from `RegressorMixin`): PASS
- Both verdicts read `"PASS"` in `_coverage.py`: PASS
- `test_coverage.py` still green: PASS

## Deviations from Plan

None — plan executed exactly as written. The check message required the full substring `"requires y to be passed, but the target y is None"` (sklearn 1.8.0 exact match) which is what the plan's `_require_y` implementation produces.

## Known Stubs

None. All functionality is wired and verified.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Pure Python over existing native bindings.

## Self-Check: PASSED

- `python/fdars/sklearn/_skeletons.py` contains `_require_y` at module scope: FOUND
- `tests/sklearn/test_regressors_compliance.py` exists: FOUND
- `python/fdars/sklearn/_coverage.py` has `"FPCRegressor": "PASS"` and `"PLSRegressor": "PASS"`: FOUND
- Commit `686f350` exists: FOUND
- Commit `eb9b73a` exists: FOUND
- Commit `ffbe751` exists: FOUND
