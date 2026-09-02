---
phase: 55-compliance-triage-foundation
plan: "02"
subsystem: sklearn-layer
tags: [sklearn, triage, skeletons, parametrize_with_checks, functional-data, compliance]
dependency_graph:
  requires:
    - python/fdars/sklearn/_base.py
    - python/fdars/sklearn/_skeletons.py (FPCATransformer from Plan 01)
    - tests/sklearn/test_triage.py (Plan 01 scaffold)
  provides:
    - python/fdars/sklearn/_skeletons.py (expanded to 28 estimators)
    - tests/sklearn/test_triage.py (all 28 candidates)
    - triage_results.txt (raw verdict data for Plan 03)
  affects:
    - python/fdars/sklearn/_coverage.py (Plan 03 reads triage_results.txt to populate verdicts)
tech_stack:
  added: []
  patterns:
    - _BaseFdarsClassifier shared base (vstack+slice pattern for combined fit+predict natives)
    - _BaseFdarsOutlierDetector shared base (score_samples + threshold->+1/-1 predict)
    - check_random_state -> u64 seed conversion (FunctionalKMeans, FuzzyFunctionalCMeans, FunctionalGMM)
    - LabelEncoder (classifiers); predict_proba (LogisticFPCClassifier)
    - ensure_all_finite compat shim (Imputer: sklearn 1.3 force_all_finite vs 1.8 ensure_all_finite)
key_files:
  created:
    - triage_results.txt
  modified:
    - python/fdars/sklearn/_skeletons.py
    - tests/sklearn/test_triage.py
decisions:
  - "FunctionalGMM.predict synthesizes cluster centers as membership-weighted centroids from X_fit_"
  - "Imputer.fit/transform use try/except for ensure_all_finite vs force_all_finite (sklearn 1.3-1.8 compat)"
  - "_BaseFdarsClassifier vstack pattern: vstack([X_fit_, X_new]), slice last len(X_new) predictions"
  - "LRTOutlierDetector score_samples augments training data per-observation and re-runs detection (O(n_new * n_train * n_bootstrap))"
  - "GLMRegressor.predict re-fits functional_glm on vstack([X_fit_, X_new]) and slices last n_new rows"
metrics:
  duration_minutes: 40
  completed_date: "2026-08-31"
  tasks_completed: 3
  commits: 3
status: complete
actuals:
  tokens: 68000
  tasks: 3
  commits: 3
---

# Phase 55 Plan 02: Full Skeleton Expansion + Triage Battery Summary

One-liner: Expanded `_skeletons.py` from 1 to 28 candidates across all five sklearn families, ran the full `parametrize_with_checks` battery (1272 passed, 107 failed), and produced `triage_results.txt` as empirical ground truth for Plan 03 verdict assignment.

## What Was Built

### Task 1: Transformer + Regressor Skeletons (12 classes)

**Transformers added (7 new + 1 from Plan 01 = 8 total):**

| Class | Native Function | Key Notes |
|-------|----------------|-----------|
| `BSplineSmoother` | `_native.smoothing.nadaraya_watson` | Per-row loop (1D function) |
| `LocalPolynomialSmoother` | `_native.smoothing.local_polynomial` | Per-row loop (1D function) |
| `BasisRepresentation` | `_native.basis.fdata_to_basis_1d` + `basis_to_fdata_1d` | Shape-preserving via project+reconstruct |
| `Imputer` | `_native.represent.impute_missing_values` | NaN-allowed tags; ensure_all_finite compat shim |
| `SplineInterpolator` | `_native.represent.spline_interpolate` | Supports grid-changing output_argvals |
| `DepthTransformer` | `_native.depth.fraiman_muniz_1d` | Output (n_obs, 1) depth scores |
| `NormTransformer` | `_native.fdata.norm_lp_1d` | Output (n_obs, 1) Lp norms |

**Regressors added (5 new):**

| Class | Native Function | Key Pattern |
|-------|----------------|-------------|
| `FPCRegressor` | `_native.regression.fregre_lm` + `predict_fregre_lm` | Stores X_fit_/y_fit_; re-fits at predict |
| `PLSRegressor` | `_native.regression.fregre_pls` + `predict_fregre_pls` | Same re-fit pattern; argvals required |
| `RobustFPCRegressor` | `_native.regression.fregre_l1`/`fregre_huber` + `predict_fregre_robust` | method='l1'/'huber' param |
| `GLMRegressor` | `_native.regression.functional_glm` (family='gaussian') | Gaussian-only; re-fits on vstack |
| `NonparametricRegressor` | `_native.regression.fregre_np` | Distance-matrix based; pairwise L2 computed inline |

### Task 2: Classifier + Clusterer + Outlier-Detector Skeletons (16 classes)

**Classifiers added (6 new, sharing `_BaseFdarsClassifier`):**

| Class | Native Function | Key Pattern |
|-------|----------------|-------------|
| `FPCLDAClassifier` | `_native.classification.fclassif_lda` | vstack X_fit_+X_new, slice last n_new predictions |
| `FPCQDAClassifier` | `_native.classification.fclassif_qda` | Same combined fit+predict pattern |
| `FPCKNNClassifier` | `_native.classification.fclassif_knn` | k param; same combined pattern |
| `DDClassifier` | `_native.classification.fclassif_dd` | No hyperparams; depth-based |
| `LogisticFPCClassifier` | `_native.regression.functional_logistic` + `predict_functional_logistic` | float64 labels required; has predict_proba |
| `ElasticMultinomialClassifier` | `_native.classification.elastic_multinomial` | Triage EXCLUDE candidate; argvals required |

**Clusterers added (3 new):**

| Class | Native Function | Key Pattern |
|-------|----------------|-------------|
| `FunctionalKMeans` | `_native.clustering.kmeans_fd` | check_random_state -> u64 seed; predict by nearest center |
| `FuzzyFunctionalCMeans` | `_native.clustering.fuzzy_cmeans_fd` | Same seed pattern; membership_ stored |
| `FunctionalGMM` | `_native.clustering.gmm_cluster` | k_range=[n_clusters]; predict via membership-weighted centers |

**Outlier Detectors added (6 new, sharing `_BaseFdarsOutlierDetector`):**

| Class | Native Function | Score Synthesis |
|-------|----------------|----------------|
| `LRTOutlierDetector` | `_native.outliers.detect_outliers_lrt_with_dist` | Per-obs augment + re-detect; +1/-1 from outlier flag |
| `OutliergramDetector` | `_native.outliers.outliergram` | MBD - threshold (higher = more normal) |
| `MagnitudeShapeDetector` | `_native.outliers.magnitude_shape` | threshold - L2(magnitude, shape) outlyingness |
| `TVDMSSDetector` | `_native.outliers.tvdmss` | tvd + mss combined; per-obs augment score |
| `MUODDetector` | `_native.outliers.muod` | mean(shape+magnitude+amplitude indices) per-obs augment |
| `DepthgramDetector` | `_native.outliers.depthgram` | fraiman_muniz_1d as MBD proxy - threshold |

### Task 3: Triage Harness Expansion + Full Battery Run

- `_ALL_SKELETONS` expanded to all 28 candidates with minimal valid hyperparameters.
- Full `parametrize_with_checks` battery run: **1272 PASSED, 107 FAILED**.
- `triage_results.txt` captured at repo root (Plan 03 input).
- 28 distinct estimators triaged (success criterion: >= 20).

## Triage Results Summary (Plan 03 input)

### Estimators with no failures (PASS candidates):

| Estimator | Status |
|-----------|--------|
| `FPCATransformer(n_components=1)` | All checks PASS (47/47 from Plan 01, confirmed) |
| `BSplineSmoother()` | All checks PASS |
| `LocalPolynomialSmoother()` | All checks PASS |
| `PLSRegressor(n_components=1)` | check_requires_y_none only fail |
| `FunctionalKMeans(n_clusters=2)` | All checks PASS |

### Estimators with fixable failures (PASS-WITH-FIXES candidates):

| Estimator | Failing Checks | Fix Required |
|-----------|---------------|-------------|
| `BasisRepresentation(n_basis=3)` | check_fit2d_1feature | 1-feature guard |
| `FPCRegressor(n_components=1)` | check_regressors_train x3, check_requires_y_none | Prediction accuracy / refit accuracy |
| `RobustFPCRegressor(n_components=1)` | check_regressors_train x3, check_requires_y_none | Same |
| `FPCKNNClassifier(ncomp=1, k=1)` | check_classifiers_regression_target, check_requires_y_none | Minor |
| `FuzzyFunctionalCMeans(n_clusters=2)` | check_non_transformer_estimators_n_iter | Add n_iter_ attribute |
| `FunctionalGMM(n_clusters=2)` | check_non_transformer_estimators_n_iter | Add n_iter_ attribute |
| `Imputer()` | check_dtype_object, sparse checks | Object dtype + sparse tag handling |
| `DepthgramDetector()` | check_outliers_train x2 | Score synthesis adjustment |
| `TVDMSSDetector()` | check_outliers_train x2 | Score synthesis adjustment |
| `FPCLDAClassifier(ncomp=1)` | check_classifiers_train x4, check_requires_y_none, check_methods_subset_invariance | Prediction consistency |
| `FPCQDAClassifier(ncomp=1)` | Same as LDA | Same |
| `DDClassifier()` | Multiple | check_classifiers_regression_target, subset_invariance |
| `OutliergramDetector()` | check_outliers_train x2 | Score threshold calibration |
| `MagnitudeShapeDetector()` | check_outliers_train x3, check_methods_subset_invariance | Subset invariance violation |

### Estimators with structural failures (EXCLUDE candidates):

| Estimator | Failing Checks | Structural Reason |
|-----------|---------------|-------------------|
| `SplineInterpolator()` | 13 checks | output_argvals stored as fitted attr; causes non-idempotency and pickle issues |
| `LogisticFPCClassifier(n_components=1)` | 21 checks | functional_logistic stability/dict mutation issues |
| `ElasticMultinomialClassifier(ncomp_beta=3)` | 10 checks | Non-contiguous label handling, unfitted check, argvals sensitivity |
| `LRTOutlierDetector(n_bootstrap=50)` | 3 checks | Per-obs re-detection is non-deterministic / too slow |
| `MUODDetector()` | check_fit2d_1feature + outliers_train | 1-feature guard + score synthesis |
| `GLMRegressor(n_components=1)` | 6 checks | Re-fit at predict is non-idempotent for subset invariance |
| `NonparametricRegressor()` | 4 checks | Distance-based re-fit; subset invariance violation |
| `FPCRegressor(n_components=1)` | 4 checks | Re-fit accuracy gap; check_requires_y_none |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] FunctionalGMM.predict had broken placeholder**
- **Found during:** Task 2 implementation and smoke testing
- **Issue:** Initial implementation of `FunctionalGMM.predict` had a broken placeholder with `if False else X` and `raise AttributeError` that always returned zeros.
- **Fix:** Rewrote predict to recover cluster centers as membership-weighted centroids: `centers = membership_.T @ X_fit_ / row_sums`. Added `X_fit_` to `fit` as stored attribute.
- **Files modified:** `python/fdars/sklearn/_skeletons.py`
- **Commit:** `ac68665`

**2. [Rule 1 - Bug] Imputer force_all_finite vs ensure_all_finite deprecation**
- **Found during:** Task 1 smoke testing
- **Issue:** sklearn 1.8.0 renamed `force_all_finite` to `ensure_all_finite` as a keyword argument to `check_array`/`validate_data`. Using the old name raised `TypeError`.
- **Fix:** Added try/except to try `ensure_all_finite="allow-nan"` first (1.8+), fall back to `force_all_finite="allow-nan"` (1.3-1.5).
- **Files modified:** `python/fdars/sklearn/_skeletons.py`
- **Commit:** `c48d7df`

**3. [Rule 2 - Missing attribute] FunctionalGMM X_fit_ not stored**
- **Found during:** FunctionalGMM.predict fix
- **Issue:** `predict` needed `X_fit_` to compute membership-weighted centers but it wasn't stored in `fit`.
- **Fix:** Added `self.X_fit_ = X` to `FunctionalGMM.fit`.
- **Files modified:** `python/fdars/sklearn/_skeletons.py`
- **Commit:** `ac68665`

**4. [Rule 1 - Discovery] functional_logistic requires float64 labels, not int64**
- **Found during:** Task 2 testing
- **Issue:** `_native.regression.functional_logistic` raises `'ndarray' object is not an instance of 'ndarray'` when passed int64, int32, or bool labels. It requires float64 labels (0.0 / 1.0).
- **Fix:** `LogisticFPCClassifier.fit` converts encoded labels to float64: `y_f64 = y_enc.astype(np.float64)`.
- **Files modified:** `python/fdars/sklearn/_skeletons.py`
- **Commit:** `c48d7df`

**5. [Rule 1 - Discovery] ElasticMultinomialClassifier works with 2 classes (contrary to RESEARCH A3)**
- **Found during:** Empirical testing
- **Issue:** RESEARCH predicted elastic_multinomial requires >= 3 classes. Empirical test showed it works with 2 classes (binary).
- **Finding:** The triage confirms it fails on check_classifiers_train due to label-consistency issues (non-contiguous int labels), not due to 2-class restriction. RESEARCH A3 assumption was wrong.
- **Impact:** Does not change verdict (still EXCLUDE candidate due to other checks failing), but revises the reason.

## Verification Results

| Check | Result |
|-------|--------|
| All 28 skeleton classes import | PASS |
| No Fdata construction in _skeletons.py | PASS |
| python/fdars/__init__.py unchanged | PASS |
| triage_results.txt exists at repo root | PASS |
| >= 20 distinct estimators triaged | PASS (28 distinct) |
| Total checks run | 1379 (1272 PASS + 107 FAIL) |

## Key Architecture Decisions

1. **`_BaseFdarsClassifier` vstack pattern:** All fdars classification natives combine fit+predict. The shared base handles: LabelEncoder -> int64 y_fit_ storage; vstack([X_fit_, X_new]) at predict; slice last n_new predictions; inverse_transform. Subclasses only implement `_call_native(X, y)`.

2. **`_BaseFdarsOutlierDetector` score_samples pattern:** Continuous score (higher = normal) computed by each subclass; base class `predict` thresholds at 0 for +1/-1 int64 output. Satisfies `check_outliers_train` which requires unique predict values in {-1, 1}.

3. **`FunctionalGMM` n_clusters -> k_range:** The native `gmm_cluster` takes `k_range: list[int]`; the skeleton passes `k_range=[n_clusters]` to force fixed K. This satisfies clone/get_params/set_params but adds `check_non_transformer_estimators_n_iter` as a minor failing check (GMM doesn't expose n_iter_).

4. **`LogisticFPCClassifier` float64 labels:** Native `functional_logistic` requires float64 labels (0.0/1.0), not int64. LabelEncoder encodes to 0/1 then `.astype(float64)` before calling native. This is a fdars-native quirk specific to the logistic function.

## Known Stubs

`triage_results.txt` is the raw discovery data for Plan 03.  All verdict assignments (PASS / PASS-WITH-FIXES / EXCLUDE) are deferred to Plan 03 which populates `_coverage.py`. The following are pre-identified as likely EXCLUDE based on triage:

- `SplineInterpolator`: 13 failing checks; `output_argvals_` stored as fitted attr causes idempotency/pickle failures -- structural redesign needed.
- `LogisticFPCClassifier`: 21 failing checks; likely native function instability and dict mutation.
- `LRTOutlierDetector` score_samples: per-obs augment+re-detect is computationally expensive for CI and non-deterministic across runs.

## Threat Surface Scan

No new network endpoints, auth paths, or trust boundary crossings. The expanded skeleton layer adds new array input surfaces for 27 additional estimators -- all validated by `_validate(dtype="numeric")` before any native call. T-55-01 (input tampering) is mitigated across all 28 skeletons.

## Self-Check: PASSED

- `python/fdars/sklearn/_skeletons.py`: FOUND (28 estimator classes)
- `tests/sklearn/test_triage.py`: FOUND (28 in _ALL_SKELETONS)
- `triage_results.txt`: FOUND (2010 lines, 1379 test results)
- Commit `c48d7df`: FOUND (transformer + regressor skeletons)
- Commit `ac68665`: FOUND (classifier + clusterer + outlier-detector skeletons)
- Commit `8cd1367`: FOUND (triage harness + battery results)
- 28 distinct estimators triaged: CONFIRMED
- `git diff --quiet -- python/fdars/__init__.py` returns 0: CONFIRMED
