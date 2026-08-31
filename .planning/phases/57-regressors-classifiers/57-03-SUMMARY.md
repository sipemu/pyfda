---
phase: 57-regressors-classifiers
plan: "03"
subsystem: sklearn-predictive-pipeline
status: complete
tags: [sklearn, pipeline, gridsearchcv, pred-01, classifier, regressor, capstone]
dependency_graph:
  requires:
    - "FPCATransformer — Phase 56 Plan 01"
    - "Imputer — Phase 56 Plan 01"
    - "BSplineSmoother — Phase 56 Plan 01"
    - "FPCLDAClassifier — Phase 57 Plan 02"
    - "FPCRegressor — Phase 57 Plan 01"
  provides:
    - "test_gridsearch_predictive_pipeline — GridSearchCV over 4-stage predictive pipeline (PRED-01)"
    - "test_regressor_pipeline_smoke — regressor Pipeline compose smoke test (PRED-01)"
  affects:
    - "tests/sklearn/test_predictive_pipeline.py"
tech_stack:
  added:
    - "sklearn.model_selection.GridSearchCV — hyperparameter search over pipeline stages"
    - "sklearn.model_selection.train_test_split — held-out test split"
  patterns:
    - "stage__param convention: fpca__n_components and clf__ncomp as grid keys"
    - "FPCATransformer outputs score matrix; downstream classifier/regressor treats scores as functional input"
    - "FPCLDAClassifier receives (n_obs, n_components) scores, applies its own capped FPCA pass"
    - "FPCRegressor receives (n_obs, n_components) scores, does FPC regression on them"
key_files:
  created:
    - "tests/sklearn/test_predictive_pipeline.py — 2 tests: GridSearchCV classifier pipeline + regressor smoke"
  modified: []
decisions:
  - "FPCLDAClassifier consumed FPCA scores (n_obs, n_comp) as X: its internal FPCA is capped by min(ncomp, n_obs-1, n_comp), so clf__ncomp=[1,2] is safe when fpca__n_components>=2 and n_train>=3."
  - "NaN injection uses stride [::5, 2::7] starting at col 2 (not col 0) to avoid boundary NaN at first/last columns, ensuring linear interpolation can fill without extrapolation."
  - "Regressor pipeline uses FPCATransformer(n_components=4) + FPCRegressor(n_components=3): scores are 4-wide, regressor applies FPC regression with 3 components on those 4-column inputs."
  - "Both tasks baked into a single file creation commit (65eae1d) since the plan put both tests in the same file with full verification passing before commit."
metrics:
  duration: "3m28s"
  completed: "2026-08-31T21:00:21Z"
  tasks_completed: 2
  tasks_total: 2
  commits: 1
actuals:
  tokens: 9500
  tasks: 2
  commits: 1
---

# Phase 57 Plan 03: Predictive Pipeline Capstone — PRED-01

Prove the full predictive story: a functional-data `Pipeline([Imputer, BSplineSmoother, FPCATransformer, FPCLDAClassifier])` driven by `GridSearchCV` fits and predicts end-to-end (PRED-01), plus a regressor-pipeline smoke and a whole-suite regression guard.

## Tasks Completed

| # | Task | Commit | Files | Status |
|---|------|--------|-------|--------|
| 1 | Pipeline([Imputer, smoother, fpca, FPCLDAClassifier]) under GridSearchCV (PRED-01) | `65eae1d` | `test_predictive_pipeline.py` | PASS |
| 2 | Regressor pipeline smoke + whole-suite regression guard (PRED-01) | `65eae1d` | `test_predictive_pipeline.py` | PASS |

## What Was Built

### `tests/sklearn/test_predictive_pipeline.py`

Two tests covering PRED-01:

**`test_gridsearch_predictive_pipeline`**

Constructs `Pipeline([("imputer", Imputer()), ("smoother", BSplineSmoother()), ("fpca", FPCATransformer()), ("clf", FPCLDAClassifier())])` and wraps it in `GridSearchCV` with:

```python
param_grid = {
    "fpca__n_components": [2, 3],
    "clf__ncomp": [1, 2],
}
```

Synthetic dataset: 40 curves over 20 grid points, two separable classes (mean shift = 3.0), sparse NaN at `[::5, 2::7]` so Imputer does real work. Train/test split (30 train, 10 test), stratified, `random_state=7`.

Score flow:
1. Imputer fills NaN → (40, 20)
2. BSplineSmoother smooths → (40, 20)
3. FPCATransformer → (40, n_components) scores (n_components from grid: 2 or 3)
4. FPCLDAClassifier receives scores as X, applies its own FPCA + sklearn LDA

Assertions: `best_estimator_` set; `predict(X_test)` returns 10 labels all in `{0, 1}`; `best_params_` contains both `fpca__n_components` and `clf__ncomp`.

Test duration: 0.30s.

**`test_regressor_pipeline_smoke`**

Constructs `Pipeline([("imputer", Imputer()), ("smoother", BSplineSmoother()), ("fpca", FPCATransformer(n_components=4)), ("reg", FPCRegressor(n_components=3))])`.

Synthetic regression dataset: 40 curves over 20 points, `y = 2*X[:,0] - X[:,1] + noise`.

Flow: same imputer+smoother stages → FPCATransformer produces (40, 4) score matrix → FPCRegressor treats those 4 columns as a functional curve and applies FPC regression with 3 components.

Assertions: `predict(X)` shape `(40,)` with all finite values; `score(X, y)` is finite.

Test duration: 0.17s.

### Whole-Suite Regression Guard

```
pytest tests/sklearn/test_predictive_pipeline.py
      tests/sklearn/test_regressors_compliance.py
      tests/sklearn/test_classifiers_compliance.py
      tests/sklearn/test_transformers_compliance.py
      tests/sklearn/test_coverage.py -q

1064 passed, 40 warnings in 3.66s
```

No cross-plan regression across transformers, regressors, or classifiers.

## Verification Results

```
pytest tests/sklearn/test_predictive_pipeline.py::test_gridsearch_predictive_pipeline -q
1 passed in 0.30s

pytest tests/sklearn/test_predictive_pipeline.py -q
2 passed in 0.35s

pytest tests/sklearn/test_predictive_pipeline.py tests/sklearn/test_regressors_compliance.py
      tests/sklearn/test_classifiers_compliance.py tests/sklearn/test_transformers_compliance.py
      tests/sklearn/test_coverage.py -q
1064 passed, 40 warnings in 3.66s
```

Acceptance criteria:
- GridSearchCV over 4-stage pipeline fits and sets best_estimator_: PASS
- predict(X_test) returns 10 labels, all in set(y_train): PASS
- best_params_ contains fpca__n_components and clf__ncomp: PASS
- Test completes in under a minute (0.30s): PASS
- Regressor pipeline: predict finite float array (40,): PASS
- Regressor pipeline: score(X, y) finite: PASS
- Whole compliance suite (1064 tests) green: PASS
- No cross-plan regression: PASS
- import fdars works, __init__.py diff empty: PASS

## Deviations from Plan

None — plan executed exactly as written.

Both tasks were written into the test file in one pass and committed together (single commit 65eae1d) since the file was created atomically and both tests passed before the commit. The plan placed both tests in the same file, so a single create-commit correctly reflects the work.

## Known Stubs

None. All functionality is wired and verified.

## Threat Surface Scan

T-57-06 (NaN + dtype flowing through pipeline): Imputer fills NaN at stage 1; BSplineSmoother, FPCATransformer, FPCLDAClassifier all upcast to float64 via `_validate`. No raw NaN passes stage boundaries. PASS.

T-57-07 (GridSearchCV cross-product time): 2×2=4 candidates, cv=3, 12 fits total, 40 curves × 20 points. Actual time: 0.30s. PASS.

No new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check: PASSED

- `tests/sklearn/test_predictive_pipeline.py` exists: FOUND
- `tests/sklearn/test_predictive_pipeline.py` contains `test_gridsearch_predictive_pipeline`: FOUND
- `tests/sklearn/test_predictive_pipeline.py` contains `test_regressor_pipeline_smoke`: FOUND
- Commit `65eae1d` exists: FOUND
- 1064 compliance + pipeline tests green: VERIFIED
- `python/fdars/__init__.py` diff empty: VERIFIED
