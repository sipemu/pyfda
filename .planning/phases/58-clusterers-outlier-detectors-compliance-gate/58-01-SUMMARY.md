---
phase: 58-clusterers-outlier-detectors-compliance-gate
plan: "01"
subsystem: sklearn-outlier-detectors
tags: [sklearn, outlier-detection, check-estimator, subset-invariance, TDD]
status: complete

dependency_graph:
  requires: []
  provides:
    - _BaseFdarsOutlierDetector with contamination/offset_/decision_function/predict
    - MagnitudeShapeDetector stored-reference depth scoring (CR-03 resolved)
    - tests/sklearn/test_outliers_compliance.py (OUT-01 compliance gate)
  affects:
    - python/fdars/sklearn/_skeletons.py
    - python/fdars/sklearn/_coverage.py
    - tests/sklearn/test_outliers_compliance.py

tech_stack:
  added:
    - parametrize_with_checks per-detector compliance test pattern
  patterns:
    - stored-reference subset-invariant scoring (modified_band_1d(X, X_fit_))
    - contamination -> offset_ -> decision_function -> predict base pattern

key_files:
  modified:
    - python/fdars/sklearn/_skeletons.py
    - python/fdars/sklearn/_coverage.py
  created:
    - tests/sklearn/test_outliers_compliance.py

decisions:
  - contamination=0.1 fixed float (not "auto") — guarantees check_outliers_train sees both {-1,+1} on small battery datasets
  - modified_band_1d(X, X_fit_) over magnitude_shape batch call — functional depth is naturally subset-invariant (each row scored vs fixed reference)
  - offset_ = percentile(train_scores, 100*contamination) placed in _BaseFdarsOutlierDetector._set_offset — shared by all 6 detectors in Plan 02
  - TDD RED→GREEN: test file written first (collection error confirmed), then implementation (47/47 green)

metrics:
  duration_seconds: 223
  completed_date: "2026-09-01"
  tasks_completed: 2
  commits: 3

actuals:
  tokens: 13750
  tasks: 2
  commits: 3
---

# Phase 58 Plan 01: Subset-invariant OutlierMixin base + MagnitudeShapeDetector — Summary

**One-liner:** MagnitudeShapeDetector promoted to `check_estimator`-green `OutlierMixin` via stored-reference `modified_band_1d(X, X_fit_)` depth scoring (47/47 checks, zero exemptions), resolving Phase-57 CR-03 subset-invariance violation.

## What Was Built

### Task 1: Subset-invariant OutlierMixin base + MagnitudeShapeDetector stored-reference scoring

**`_BaseFdarsOutlierDetector`** (lines ~2393–2484 in `_skeletons.py`) was extended to own the full sklearn OutlierMixin contract shared by all six detectors:

- **`_set_offset(train_scores)`** — sets `offset_ = float(np.percentile(train_scores, 100.0 * self.contamination))`. Higher score = more inlier → lowest `contamination` fraction predict as -1.
- **`decision_function(X)`** — returns `score_samples(X) - offset_` (continuous; required by OutlierMixin). Replaces the old threshold-at-0 `predict`.
- **`predict(X)`** — `np.where(decision_function(X) >= 0, 1, -1).astype(np.int64)`.
- **`score_samples`** — still abstract; subclasses MUST score rows against stored `X_fit_` (not batch stats).

**`MagnitudeShapeDetector`** (lines ~2608–2740) rewritten to the stored-reference depth pattern:

- `__init__(self, argvals=None, contamination=0.1, depth_method="modified_band")` — three params stored verbatim.
- `fit`: validates + float64 cast; stores `self.X_fit_ = X`; computes training depth as `train_scores = np.asarray(_native.depth.modified_band_1d(X, X))` (self-depth); calls `_set_offset(train_scores)`.
- `score_samples`: returns `np.asarray(_native.depth.modified_band_1d(X, self.X_fit_))` — each new row scored against the STORED training set. Subset-invariant by construction.

**CR-03 resolved:** `score_samples(X[mask]) == score_samples(X)[mask]` is now True (was False with the batch `magnitude_shape` call).

### Task 2: Compliance test + _coverage.py verdict flip

**`tests/sklearn/test_outliers_compliance.py`** created — mirrors `test_classifiers_compliance.py` pattern:

```python
@parametrize_with_checks([MagnitudeShapeDetector(contamination=0.1)])
def test_magnitude_shape_compliance(estimator, check):
    check(estimator)
```

Result: **47/47 parametrize_with_checks checks passed, zero exemptions**.

Specific checks proven green:
- `check_outliers_train` — both -1 and +1 produced via contamination=0.1 offset
- `check_methods_subset_invariance` — stored-reference depth (CR-03 fix)
- `check_outliers_fit_predict` — fit_predict consistent with predict(fit(X))
- `check_estimators_dtypes` — float32 inputs upcast to float64 before native call

**`_coverage.py`** — `MagnitudeShapeDetector` verdict flipped from `PASS-WITH-FIXES` to `"PASS"` with a comment documenting the Phase 58 Plan 01 fix.

## Verification Results

```
.venv/bin/python -c "...subset-invariant + predict classes + decision_function..."
# -> VERIFY: PASSED

pytest tests/sklearn/test_outliers_compliance.py -q
# -> 47 passed in 0.42s

pytest tests/sklearn/test_transformers_compliance.py tests/sklearn/test_classifiers_compliance.py -q
# -> 706 passed, 40 warnings in 1.89s (no regressions)

pytest tests/sklearn/ (overall)
# -> 753 passed total
```

## Deviations from Plan

None. Plan executed exactly as written.

- TDD RED: test file written first; collection error confirmed (`TypeError: MagnitudeShapeDetector.__init__() got an unexpected keyword argument 'contamination'`).
- TDD GREEN: implementation landed; 47/47 checks green.

## Known Stubs

None. All functionality is fully wired.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes.

T-58-01 (Tampering — MagnitudeShapeDetector.score_samples): mitigated. `X_fit_` validated at fit; `score_samples` re-validates with `reset=False` so shape/dtype-mismatched batches raise before the native call. Confirmed by `check_estimators_dtypes` passing.

## Self-Check: PASSED

Files exist:
- `python/fdars/sklearn/_skeletons.py` — FOUND
- `python/fdars/sklearn/_coverage.py` — FOUND
- `tests/sklearn/test_outliers_compliance.py` — FOUND

Commits:
- `1820889` (test RED) — FOUND
- `617e9a9` (feat GREEN) — FOUND
- `bdf4a23` (feat Task 2) — FOUND
