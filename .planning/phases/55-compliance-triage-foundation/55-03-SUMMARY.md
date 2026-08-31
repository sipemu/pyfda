---
phase: 55-compliance-triage-foundation
plan: "03"
subsystem: sklearn-layer
tags: [sklearn, triage, coverage-registry, verdicts, go-no-go, TRIAGE-02, TRIAGE-03]
dependency_graph:
  requires:
    - triage_results.txt (Plan 02 raw output)
    - python/fdars/sklearn/_coverage.py (Plan 01 scaffold)
    - python/fdars/sklearn/_skeletons.py (Plan 02 -- 28 skeletons)
  provides:
    - python/fdars/sklearn/_coverage.py (fully populated)
    - tests/sklearn/test_coverage.py (registry integrity + excluded-still-callable)
    - tests/sklearn/test_go_no_go.py (viable-core gate)
  affects:
    - Phase 56 (Transformers): GO -- proceed, transformers/smoothers/clusterers/outliers meet minimums
    - Phase 57 (Regressors + Classifiers): NO-GO -- regressor and classifier families are short
    - Phase 58 (Clusterers + Outliers): GO -- clusterer and outlier families meet minimums
tech_stack:
  added: []
  patterns:
    - TRIAGE_VERDICTS dict with PASS/PASS-WITH-FIXES/EXCLUDE verdicts derived from triage_results.txt
    - EXCLUDED_METHODS with reason codes (ORDER_SENSITIVE, LABEL_DOMAIN, ACCURACY_STRUCTURAL, etc.)
    - importlib-based functional-API reachability test (no actual calls, symbol resolution only)
    - per-family minimum viable-core gate with gap-naming failure messages
key_files:
  created:
    - tests/sklearn/test_coverage.py
    - tests/sklearn/test_go_no_go.py
  modified:
    - python/fdars/sklearn/_coverage.py
decisions:
  - "FPCRegressor/RobustFPCRegressor EXCLUDE: re-fit-at-predict vstack pattern cannot achieve R2>0.5 on sklearn battery; stored-model predict required for Phase 57"
  - "LogisticFPCClassifier EXCLUDE: native functional_logistic enforces y in {0.0, 1.0}; sklearn battery passes arbitrary integer labels; label domain constraint is structural"
  - "LRTOutlierDetector EXCLUDE: per-obs augment always predicts +1 on small normal battery data; check_outliers_train requires {-1, 1} present"
  - "MUODDetector upgraded to PASS-WITH-FIXES: both missing decision_function and 1-feature guard are guard/attribute adds, not structural redesigns"
  - "elastic_registration API correction: fdars.alignment has no elastic_registration function; correct entry is elastic_align_pair (the pair-wise elastic alignment primitive)"
  - "anova_perm_test API correction: fdars.inference has oneway_anova_vstat not anova_perm_test; spm_monitoring corrected to spm_monitor"
  - "Phase 56 GO: FPCATransformer(1), smoothers(7), clusterers(3), outliers(4) all meet minimums"
  - "Phase 57 NO-GO: regressors(1/2), classifiers(1/2) -- blocked until stored-model predict adopted"
metrics:
  duration_minutes: 98
  completed_date: "2026-08-31"
  tasks_completed: 3
  commits: 3
status: complete
actuals:
  tokens: 52000
  tasks: 3
  commits: 3
---

# Phase 55 Plan 03: Triage Verdicts + Go/No-Go Gate Summary

One-liner: Derived 28 per-estimator PASS/PASS-WITH-FIXES/EXCLUDE verdicts from triage_results.txt, populated the coverage registry with reason-coded EXCLUDED_METHODS, verified all 26 excluded methods are still callable via the functional API, and ran the viable-core gate which returned NO-GO for regressors (1/2) and classifiers (1/2) due to the re-fit-at-predict structural pattern.

## What Was Built

### Task 1: TRIAGE_VERDICTS + EXCLUDED_METHODS Populated

Source: `triage_results.txt` (sklearn 1.8.0 / Python 3.14, 1379 checks: 1272 PASS, 107 FAIL across 28 estimators).

#### Final Verdict Tally

| Verdict | Count | Estimators |
|---------|-------|-----------|
| PASS | 6 | FPCATransformer, BSplineSmoother, LocalPolynomialSmoother, FunctionalKMeans, DepthTransformer, NormTransformer |
| PASS-WITH-FIXES | 10 | BasisRepresentation, Imputer, PLSRegressor, FPCKNNClassifier, FuzzyFunctionalCMeans, FunctionalGMM, OutliergramDetector, TVDMSSDetector, MUODDetector, DepthgramDetector |
| EXCLUDE | 12 | SplineInterpolator, FPCRegressor, RobustFPCRegressor, GLMRegressor, NonparametricRegressor, FPCLDAClassifier, FPCQDAClassifier, DDClassifier, LogisticFPCClassifier, ElasticMultinomialClassifier, LRTOutlierDetector, MagnitudeShapeDetector |

#### EXCLUDED_METHODS Registry (26 entries, reason-coded)

Pre-excludes (design-level, no skeleton):

| Method | Reason | Failing Check |
|--------|--------|---------------|
| `alignment.elastic_align_pair` | ORDER_SENSITIVE | check_methods_subset_invariance |
| `alignment.karcher_mean` | ORDER_SENSITIVE | check_methods_subset_invariance |
| `pace_fpca.pace_fpca` | IRREGULAR_INPUT | check_n_features_in |
| `regression.functional_glm_binomial` | RESPONSE_DOMAIN | check_estimators_dtypes |
| `regression.functional_glm_poisson` | RESPONSE_DOMAIN | check_estimators_dtypes |
| `regression.concurrent_regression` | NON_STANDARD_INPUT | (by design) |
| `regression.fosr` | NON_STANDARD_OUTPUT | check_estimators_dtypes |
| `clustering.cluster_optim` | HYPERPARAMETER_SEARCH | (by design) |
| `inference.t_perm_test` | NOT_AN_ESTIMATOR | (by design) |
| `inference.f_perm_test` | NOT_AN_ESTIMATOR | (by design) |
| `inference.oneway_anova_vstat` | NOT_AN_ESTIMATOR | (by design) |
| `inference.mean_scb` | NOT_AN_ESTIMATOR | (by design) |
| `spm.spm_monitor` | SEQUENTIAL_STREAMING | (by design) |

Triage-discovered excludes:

| Method | Reason | Failing Check |
|--------|--------|---------------|
| `represent.spline_interpolate` | NON_STANDARD_INPUT | check_fit_score_takes_y |
| `regression.functional_logistic` | LABEL_DOMAIN | check_estimators_fit_returns_self |
| `classification.elastic_multinomial` | UNFITTED_CHECK_MISSING | check_estimators_unfitted |
| `outliers.detect_outliers_lrt_with_dist` | OUTLIER_SCORE_STRUCTURAL | check_outliers_fit_predict |
| `outliers.muod` | MISSING_DECISION_FUNCTION | check_outliers_train |
| `regression.functional_glm` | ACCURACY_STRUCTURAL | check_regressors_train |
| `regression.fregre_np` | ACCURACY_STRUCTURAL | check_regressors_train |
| `regression.fregre_lm` | ACCURACY_STRUCTURAL | check_regressors_train |
| `regression.fregre_l1` | ACCURACY_STRUCTURAL | check_regressors_train |
| `classification.fclassif_lda` | ACCURACY_STRUCTURAL | check_classifiers_train |
| `classification.fclassif_qda` | ACCURACY_STRUCTURAL | check_classifiers_train |
| `classification.fclassif_dd` | ACCURACY_STRUCTURAL | check_classifiers_train |
| `outliers.magnitude_shape` | OUTLIER_SCORE_STRUCTURAL | check_outliers_fit_predict |

### Task 2: Registry Integrity Test (TRIAGE-02)

`tests/sklearn/test_coverage.py` -- 172 tests, all PASS:
- Shape: every EXCLUDED_METHODS entry has `reason`, `failing_check`, `functional_api` (non-empty `reason`)
- Verdict domain: every TRIAGE_VERDICTS value starts with PASS, PASS-WITH-FIXES, or EXCLUDE
- Consistency: EXCLUDE verdicts accompanied by EXCLUDED_METHODS coverage
- Excluded-still-callable: all 26 EXCLUDED_METHODS `functional_api` paths resolve and are callable via `import fdars` -- exclusion from the sklearn layer does NOT remove functional-API access

### Task 3: Go/No-Go Viable-Core Gate (TRIAGE-03)

`tests/sklearn/test_go_no_go.py` -- per-family gate tests:

| Family | Viable | Minimum | Status |
|--------|--------|---------|--------|
| fpca | 1 (FPCATransformer) | 1 | GO |
| smoother | 7 | 2 | GO |
| regressor | 1 (PLSRegressor) | 2 | **NO-GO** |
| classifier | 1 (FPCKNNClassifier) | 2 | **NO-GO** |
| clusterer | 3 | 1 | GO |
| outlier | 4 | 2 | GO |

**Overall gate: NO-GO** -- regressor (1/2) and classifier (1/2) families fall short.

`test_overall_go_no_go` fails with explicit gap message:
```
VIABLE CORE GATE: NO-GO -- the following families fall short of their minimum:
  - regressor: 1/2 viable (members: ['PLSRegressor'])
  - classifier: 1/2 viable (members: ['FPCKNNClassifier'])
```

Root cause: The re-fit-at-predict vstack pattern in the skeletons cannot achieve the accuracy thresholds required by `check_regressors_train` (R2 > 0.5) and `check_classifiers_train` (accuracy > 0.83). This is a structural design choice in the Phase 55 skeletons -- Phase 57 must adopt stored-model predict (fit once, predict from stored coefficients) to bring these families into compliance.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Correction] elastic_registration -> elastic_align_pair**
- **Found during:** Task 1 API verification
- **Issue:** The pre-existing `EXCLUDED_METHODS` entry used key `"alignment.elastic_registration"` and `functional_api: "fdars.alignment.elastic_registration"` -- but `fdars.alignment` has no `elastic_registration` function. The correct primitive is `elastic_align_pair`.
- **Fix:** Corrected to `"alignment.elastic_align_pair"` with `functional_api: "fdars.alignment.elastic_align_pair"`.
- **Files modified:** `python/fdars/sklearn/_coverage.py`
- **Commit:** `0a4a020`

**2. [Rule 1 - Correction] anova_perm_test / scb -> oneway_anova_vstat / mean_scb**
- **Found during:** Task 1 API verification
- **Issue:** Pre-existing EXCLUDED_METHODS used `"inference.anova_perm_test"` and `"inference.scb"` -- neither exists in `fdars.inference`. The actual functions are `oneway_anova_vstat` and `mean_scb`.
- **Fix:** Corrected keys and functional_api paths to `fdars.inference.oneway_anova_vstat` and `fdars.inference.mean_scb`.
- **Files modified:** `python/fdars/sklearn/_coverage.py`
- **Commit:** `0a4a020`

**3. [Rule 1 - Correction] spm_monitoring -> spm_monitor**
- **Found during:** Task 1 API verification
- **Issue:** Pre-existing EXCLUDED_METHODS used `"spm.spm_monitoring"` / `"fdars.spm.spm_monitoring"` but the actual function is `spm_monitor`.
- **Fix:** Corrected to `"spm.spm_monitor"` / `"fdars.spm.spm_monitor"`.
- **Files modified:** `python/fdars/sklearn/_coverage.py`
- **Commit:** `0a4a020`

**4. [Rule 2 - Refinement] MUODDetector upgraded from EXCLUDE to PASS-WITH-FIXES**
- **Found during:** Task 1 failure analysis
- **Issue:** SUMMARY-02 listed MUODDetector as EXCLUDE. Re-examining: it fails `check_outliers_train` (missing `decision_function`) and `check_fit2d_1feature` (wrong error message). Both are fixable guard/attribute additions, not structural redesigns.
- **Fix:** Verdict changed to PASS-WITH-FIXES; added to viable outlier count.
- **Impact:** Outlier family count improved from 3 to 4 viable (still well above minimum 2).
- **Files modified:** `python/fdars/sklearn/_coverage.py`
- **Commit:** `0a4a020`

## Go/No-Go Decision

**PARTIAL GO** -- Phase 56 (Transformers) may proceed; Phase 57 (Regressors + Classifiers) is BLOCKED.

| Phase | Family Coverage | Decision |
|-------|----------------|----------|
| Phase 56: Transformers | fpca=1/1, smoother=7/2 | GO |
| Phase 57: Regressors | regressor=1/2 | NO-GO -- stored-model predict required |
| Phase 57: Classifiers | classifier=1/2 | NO-GO -- stored-model predict + label validation required |
| Phase 58: Clusterers | clusterer=3/1 | GO |
| Phase 58: Outlier Detectors | outlier=4/2 | GO |

**Phase 57 unblocking path:** The 4 EXCLUDE regressors and 3 EXCLUDE classifiers all use the `_BaseFdarsClassifier` vstack re-fit pattern. Phase 57 must replace this with:
1. A fit that calls the native once and stores the result (dict/weights).
2. A predict that uses the stored result (no re-fit, no vstack).
This would resolve `check_regressors_train`, `check_classifiers_train`, `check_methods_subset_invariance`, and `check_requires_y_none` in one design change.

## Phase 56-58 Coverage Plan

Based on PASS + PASS-WITH-FIXES verdicts:

**Phase 56 (Transformers):** FPCATransformer, BSplineSmoother, LocalPolynomialSmoother, BasisRepresentation, Imputer, DepthTransformer, NormTransformer *(SplineInterpolator excluded)*

**Phase 57 (Regressors + Classifiers):** PLSRegressor (PASS-WITH-FIXES), FPCKNNClassifier (PASS-WITH-FIXES) *+ regressors/classifiers pending stored-model redesign*

**Phase 58 (Clusterers + Outliers):** FunctionalKMeans, FuzzyFunctionalCMeans, FunctionalGMM, OutliergramDetector, TVDMSSDetector, MUODDetector, DepthgramDetector *(LRTOutlierDetector, MagnitudeShapeDetector excluded)*

## Verification Results

| Check | Result |
|-------|--------|
| `_coverage.py` AST parse | PASS |
| `import fdars` unchanged | PASS (git diff empty on `__init__.py`) |
| TRIAGE_VERDICTS count | PASS (28 verdicts) |
| EXCLUDED_METHODS shape | PASS (26 entries, all have reason/failing_check/functional_api) |
| `pytest test_coverage.py` | PASS (172/172) |
| `pytest test_go_no_go.py` | PARTIAL -- 5/8 pass (3 fail: regressor, classifier, overall -- correct NO-GO signal) |
| `pytest test_foundation.py` | PASS (15/15, unchanged) |
| `python/fdars/__init__.py` unchanged | PASS |

## Threat Flags

No new network endpoints, auth paths, or trust boundary crossings. T-55-03 (verdict provenance) mitigated: all 28 TRIAGE_VERDICTS entries trace to `triage_results.txt` failure lines. T-55-04 (excluded method reachability) mitigated: `test_coverage.py` confirms all 26 EXCLUDED_METHODS functional_api paths are callable.

## Self-Check: PASSED

- `python/fdars/sklearn/_coverage.py`: FOUND (28 verdicts, 26 EXCLUDED_METHODS)
- `tests/sklearn/test_coverage.py`: FOUND (172 tests)
- `tests/sklearn/test_go_no_go.py`: FOUND (8 tests; 3 correct failures)
- Commit `0a4a020`: FOUND (feat(55-03): populate TRIAGE_VERDICTS + EXCLUDED_METHODS)
- Commit `b80f027`: FOUND (test(55-03): registry integrity + excluded-still-callable)
- Commit `7af0d70`: FOUND (test(55-03): go/no-go viable-core gate)
- `git diff --quiet -- python/fdars/__init__.py` returns 0: CONFIRMED
