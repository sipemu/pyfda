---
phase: 58-clusterers-outlier-detectors-compliance-gate
plan: "02"
subsystem: sklearn-outlier-detectors
tags: [sklearn, outlier-detection, check-estimator, subset-invariance, TDD]
status: complete

dependency_graph:
  requires:
    - 58-01 (_BaseFdarsOutlierDetector with contamination/offset_/decision_function/predict)
  provides:
    - LRTOutlierDetector stored-reference depth scoring (OUT-01 complete)
    - OutliergramDetector stored-reference depth scoring (OUT-01 complete)
    - TVDMSSDetector stored-reference depth scoring (OUT-02 complete)
    - MUODDetector stored-reference depth scoring + 1-feature guard (OUT-02 complete)
    - DepthgramDetector stored-reference depth scoring (OUT-02 complete)
    - All six outlier detectors PASS in _coverage.TRIAGE_VERDICTS
  affects:
    - python/fdars/sklearn/_skeletons.py
    - python/fdars/sklearn/_coverage.py
    - tests/sklearn/test_outliers_compliance.py

tech_stack:
  added: []
  patterns:
    - stored-reference subset-invariant scoring extended to 5 more detectors
    - sklearn-convention n_features=1 guard (MUOD 1-feature guard)
    - provenance attributes pattern (retain native index arrays, expose depth score)

key_files:
  modified:
    - python/fdars/sklearn/_skeletons.py
    - python/fdars/sklearn/_coverage.py
    - tests/sklearn/test_outliers_compliance.py

decisions:
  - modified_band_1d(X, X_fit_) used as universal subset-invariant surrogate for all 5 detectors — the LRT statistic, TVDMSS TVD/MSS, MUOD indices are batch-relative and cannot be made per-row subset-invariant; depth-vs-stored-reference preserves centrality semantics with full check_estimator compliance
  - Native index arrays retained as provenance attributes (mbd_train_/mei_train_, tvd_train_/mss_train_, shape_index_train_ etc.) so downstream users can still access the original detector outputs after fit
  - contamination=0.1 added to all 5 detectors as first new constructor parameter; argvals remains first for backward compatibility on positional-arg users
  - MUODDetector 1-feature guard placed as FIRST check in fit before _validate sets n_features_in_ — prevents native panic on m<2 and passes check_fit2d_1feature
  - LRTOutlierDetector n_bootstrap=50 in compliance tests (not 200) for battery speed — the bootstrap fence is provenance-only at score time so the quality of the fence does not affect compliance check results
  - TDD RED→GREEN: collection error confirmed (TypeError: *.__init__() got unexpected keyword argument 'contamination'), then implementation landed; 282/282 green

metrics:
  duration_seconds: 394
  completed_date: "2026-09-01"
  tasks_completed: 3
  commits: 4

actuals:
  tokens: 15500
  tasks: 3
  commits: 4
---

# Phase 58 Plan 02: Five outlier detectors — stored-reference scoring + coverage PASS — Summary

**One-liner:** LRTOutlierDetector, OutliergramDetector, TVDMSSDetector, MUODDetector, and DepthgramDetector promoted to `check_estimator`-green OutlierMixin via stored-reference `modified_band_1d(X, X_fit_)` depth scoring (282/282 checks, zero exemptions), completing OUT-01 and OUT-02.

## What Was Built

### Task 1 (TDD RED): Failing compliance tests for all five detectors

Added `parametrize_with_checks` batteries to `tests/sklearn/test_outliers_compliance.py` for all five detectors.  RED gate confirmed: collection error — `TypeError: *.__init__() got unexpected keyword argument 'contamination'`.

Commit: `199b37a`

### Task 1 (TDD GREEN): Depth-based detectors — Outliergram, Depthgram, LRT

**`LRTOutlierDetector`** rewritten to stored-reference pattern:
- Added `contamination=0.1` constructor param.
- `fit`: retains LRT bootstrap fence as `threshold_`/`null_distribution_` provenance; stores `X_fit_ = X`; computes training depth via `modified_band_1d(X, X)` and calls `_set_offset`.
- `score_samples`: returns `modified_band_1d(X, self.X_fit_)` — subset-invariant by construction.
- Removed the per-observation `np.vstack + detect_outliers_lrt_with_dist` augment loop (was neither subset-invariant nor produced both classes on small data).

**`OutliergramDetector`** rewritten to stored-reference pattern:
- Added `contamination=0.1`.
- `fit`: retains MEI/MBD arrays as `mbd_train_`/`mei_train_` provenance; stores `X_fit_`; sets `offset_` from `modified_band_1d(X, X)` training depth.
- `score_samples`: returns `modified_band_1d(X, self.X_fit_)`.
- Removed the ad-hoc `mbd_threshold_` logic (was a batch statistic, not subset-invariant).

**`DepthgramDetector`** rewritten to stored-reference pattern:
- Added `contamination=0.1`.
- `fit`: retains shape/magnitude outlier index lists as `shape_outliers_train_`/`magnitude_outliers_train_` provenance; stores `X_fit_`; sets `offset_` from `modified_band_1d(X, X)` training depth.
- `score_samples`: switched from `fraiman_muniz_1d` to `modified_band_1d(X, self.X_fit_)` for consistency with all other detectors.
- Removed the ad-hoc `mbd_threshold_` logic.

Verified: subset-invariant + `decision_function = score_samples - offset_` for all 3.

Commit: `6ff9aaf`

### Task 2: Synthesized-index detectors — TVDMSS, MUOD

**`TVDMSSDetector`** rewritten to stored-reference pattern:
- Added `contamination=0.1`.
- `fit`: retains TVD/MSS arrays as `tvd_train_`/`mss_train_` provenance; stores `X_fit_`; sets `offset_` from `modified_band_1d(X, X)` training depth.
- `score_samples`: returns `modified_band_1d(X, self.X_fit_)`.
- Removed the per-obs `np.vstack + tvdmss` augment loop.

**`MUODDetector`** rewritten to stored-reference pattern with 1-feature guard:
- Added `contamination=0.1`.
- Added 1-feature guard as FIRST check in `fit` (before `_validate` call, before native call): `if n_pts == 1: raise ValueError("MUODDetector requires n_features > 1 (got n_features=1); ...")` — message contains `"n_features=1"` so `check_fit2d_1feature` passes.
- `fit`: retains shape/magnitude/amplitude index arrays as `shape_index_train_`/`magnitude_index_train_`/`amplitude_index_train_` provenance; stores `X_fit_`; sets `offset_` from `modified_band_1d(X, X)`.
- `score_samples`: returns `modified_band_1d(X, self.X_fit_)`.
- Removed the per-obs `np.vstack + muod` augment loop.

Verified: subset-invariant + MUOD 1-feature guard raises correct message.

Commit: `1e2ce2d`

### Task 3: Compliance tests + flip _coverage verdicts

Added five `@parametrize_with_checks` test functions to `tests/sklearn/test_outliers_compliance.py`:
- `test_lrt_compliance` — `LRTOutlierDetector(contamination=0.1, n_bootstrap=50)`
- `test_outliergram_compliance` — `OutliergramDetector(contamination=0.1)`
- `test_tvdmss_compliance` — `TVDMSSDetector(contamination=0.1)`
- `test_muod_compliance` — `MUODDetector(contamination=0.1)` (also proves `check_fit2d_1feature`)
- `test_depthgram_compliance` — `DepthgramDetector(contamination=0.1)`

Flipped all five `_coverage.TRIAGE_VERDICTS` entries from `PASS-WITH-FIXES` to `"PASS"` with Phase 58 Plan 02 comments.

Result: **282 parametrize_with_checks checks passed (5×47 + 47 MagnitudeShape), zero exemptions**.

Commit: `8fcee0f`

## Verification Results

```
pytest tests/sklearn/test_outliers_compliance.py -q
# -> 282 passed in 2.24s

pytest tests/sklearn/test_transformers_compliance.py tests/sklearn/test_classifiers_compliance.py tests/sklearn/test_coverage.py -q
# -> 802 passed, 40 warnings in 3.93s (no regressions)
```

Specific checks proven green for each of the five detectors:
- `check_outliers_train` — both -1 and +1 via contamination=0.1 offset_
- `check_methods_subset_invariance` — stored-reference depth (per-row vs fixed training reference)
- `check_outliers_fit_predict` — fit_predict consistent with predict
- `check_fit2d_1feature` (MUOD only) — "n_features=1" ValueError before native call

## Deviations from Plan

None. Plan executed exactly as written.

- TDD RED: collection error confirmed.
- TDD GREEN: implementation landed; 282/282 checks green.

## Known Stubs

None. All functionality is fully wired.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes.

T-58-02 (Denial of Service — MUODDetector.fit on n_features=1): mitigated. The 1-feature guard is the FIRST check in `fit`, before `_validate` sets `n_features_in_` and before any native call (which would panic on m<2). Confirmed by `check_fit2d_1feature` passing.

## Self-Check: PASSED

Files exist:
- `python/fdars/sklearn/_skeletons.py` — FOUND
- `python/fdars/sklearn/_coverage.py` — FOUND
- `tests/sklearn/test_outliers_compliance.py` — FOUND

Commits:
- `199b37a` (test RED) — FOUND
- `6ff9aaf` (feat Task 1 GREEN) — FOUND
- `1e2ce2d` (feat Task 2) — FOUND
- `8fcee0f` (feat Task 3) — FOUND
