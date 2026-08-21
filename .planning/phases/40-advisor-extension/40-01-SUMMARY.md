---
phase: 40-advisor-extension
plan: "01"
subsystem: advisor-aspects
tags: [advisor, diagnostics, grounding, outliers, regression, classification, fpca, python-only]
status: complete

dependency_graph:
  requires:
    - 39-03  # v6.0 bindings (tvdmss, muod, depthgram, seq-transform, functional_glm, concurrent_regression, elastic_multinomial, pace_fpca)
  provides:
    - grounded scalar diagnostics for all 6 new v6.0 result dict shapes
  affects:
    - python/fdars/advisor/aspects/outliers.py
    - python/fdars/advisor/aspects/regression.py
    - python/fdars/advisor/aspects/classification.py
    - python/fdars/advisor/aspects/fpca.py
    - python/fdars/advisor/_prompts.py

tech_stack:
  added: []
  patterns:
    - key-presence branch detection (unique trigger key per detector/model)
    - float()/int()/bool() coercion invariant (no numpy scalars in diagnostic output)
    - _eigenvalues_to_variance_cumulative shared helper reuse (pace_fpca)
    - offline-deterministic json.dumps(sort_keys=True) across all new branches

key_files:
  created:
    - tests/test_advisor_outliers_v6.py
    - tests/test_advisor_regression_v6.py
    - tests/test_advisor_group_b.py
  modified:
    - python/fdars/advisor/aspects/outliers.py
    - python/fdars/advisor/aspects/regression.py
    - python/fdars/advisor/aspects/classification.py
    - python/fdars/advisor/aspects/fpca.py
    - python/fdars/advisor/_prompts.py
    - tests/test_advisor.py

decisions:
  - "depthgram branch placed after tvdmss/muod/seq-transform with outliergram block guarded by 'mbd_mei_d' not in raw — mutual exclusion guaranteed"
  - "sequential_transform_outliers emits NO fraction — n_obs unrecoverable from that dict (Pitfall 4)"
  - "regression branch uses key 'iterations' not 'n_iter' and emits NO 'converged' (Pitfall 2 confirmed from Rust source)"
  - "concurrent_regression residuals stay out of 1-D path — existing ndim==1 guard yields None; 2-D summary via concurrent_residual_rms"
  - "has_fosr=True for concurrent_regression is documented overlap; has_concurrent_regression is the specific discriminator"
  - "pace_fpca eigenvalues passed directly to _eigenvalues_to_variance_cumulative (already scaled)"
  - "elastic_multinomial n_classes overrides caller-supplied parameter with fdars-computed count"
  - "ITP NOT added — deferred per plan (vector adjusted_pvalues, no grounded scalar without arbitrary reduction)"

metrics:
  duration: "~60 minutes"
  completed: "2026-08-21T07:37:00Z"
  tasks_completed: 5
  commits: 5

actuals:
  tokens: 68000
  tasks: 5
  commits: 5
---

# Phase 40 Plan 01: Advisor Extension — v6.0 Grounded Scalar Diagnostics Summary

Grounded scalar diagnostics added to four existing advisor aspect builders for all
six new v6.0 result dict shapes: tvdmss/muod/sequential_transform_outliers/depthgram
(ADV-04, outliers aspect), functional_glm/concurrent_regression (ADV-05, regression
aspect), elastic_multinomial (Group B, classification aspect), pace_fpca (Group B,
fpca aspect). Every emitted value is a native float/int/bool reduction of an
fdars-computed value; the grounding invariant and MCP guard-sync are preserved.

## Completed Tasks

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | tvdmss branch + primer + test (tracer) | 6c5357a | outliers.py, _prompts.py, test_advisor_outliers_v6.py |
| 2 | muod/sequential_transform/depthgram + ordering guard | a5ba3c0 | outliers.py, test_advisor_outliers_v6.py |
| 3 | functional_glm + concurrent_regression branches | a7792e3 | regression.py, _prompts.py, test_advisor_regression_v6.py |
| 4 | elastic_multinomial + pace_fpca Group B branches | fdaea98 | classification.py, fpca.py, _prompts.py, test_advisor_group_b.py |
| 5 | Full-suite gate + regression fix for fpca test | 6b70df1 | tests/test_advisor.py |

## What Was Built

### ADV-04: Outliers Aspect — 4 new detector branches

**tvdmss** (trigger `"tvd" in raw and "mss" in raw`):
- `n_magnitude_outliers`, `n_shape_outliers` (int = len of index lists)
- `magnitude_outlier_fraction`, `shape_outlier_fraction` (float = count/n_obs)
- `tvd_range`, `mss_range` ([float, float] = [min, max] of score arrays)
- `has_tvdmss = True`

**muod** (trigger `"amplitude_outliers" in raw`):
- `n_muod_magnitude_outliers`, `n_muod_shape_outliers`, `n_amplitude_outliers` (int)
- Three fractions (float) and three `*_index_range` ([float, float]) entries
- `has_muod = True`

**sequential_transform_outliers** (trigger `"union_outliers" in raw`):
- `n_union_outliers` (int), `n_transforms` (int)
- NO fraction emitted (n_obs unrecoverable — Pitfall 4)
- `has_sequential_transform = True`

**depthgram** (trigger `"mbd_mei_d" in raw`):
- `n_depthgram_shape_outliers`, `n_depthgram_magnitude_outliers` (int)
- Two fractions, `depthgram_mbd_range`, `depthgram_mei_range` ([float, float])
- `has_depthgram = True`
- Outliergram block guarded with `"mbd_mei_d" not in raw` — ordering invariant enforced

### ADV-05: Regression Aspect — 2 new model branches

**functional_glm** (trigger `"deviance" in raw`):
- `deviance`, `aic`, `bic`, `log_likelihood` (float)
- `iterations` (int — key is `"iterations"` NOT `"n_iter"`)
- `glm_ncomp` (int), `family` (str)
- `has_functional_glm = True`

**concurrent_regression** (trigger `"beta_curve" in raw`):
- `concurrent_residual_rms`, `concurrent_residual_max_abs` (float from 2-D residuals)
- `n_predictors` (int = rows of beta_curve = number of predictor functions)
- `has_concurrent_regression = True`
- 1-D residual scalars remain None (2-D residuals never enter the ndim==1 path)

### ADV-05 Group B: Classification + FPCA

**elastic_multinomial** in classification aspect (trigger `"train_accuracy" in raw`):
- `train_accuracy` (float), `train_error_rate` (float = 1 - train_accuracy)
- `n_classes` (int — overrides caller-supplied param with fdars-computed count)
- `has_elastic_multinomial = True`

**pace_fpca** in fpca aspect (trigger `"eigenvalues" in raw`):
- `pace_ncomp` (int), `pace_sigma2` (float)
- `pace_variance_explained_cumulative` (list[float] via `_eigenvalues_to_variance_cumulative`)
- `pace_variance_explained_first` (float)
- `has_pace_fpca = True`
- Standard FPCA singular_values path unaffected

### ITP Deferred

ITP (`itp_one_pop`, `itp_two_pop`, `itp_flm`) returns vector `adjusted_pvalues` with
no grounded scalar summary — deferred per plan.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_advisor.py::test_fpca_output_unchanged_after_refactor failed**
- **Found during:** Task 5 full-suite gate
- **Issue:** Existing regression test compared exact fpca dict output; new pace_fpca branch
  adds keys (`has_pace_fpca`, `pace_ncomp`, etc.; all `None` for standard FPCA input) that
  were absent from the expected dict
- **Fix:** Added the five new None-valued keys to the test's `expected` dict so it reflects
  the current canonical output shape
- **Files modified:** `tests/test_advisor.py:311-321`
- **Commit:** 6b70df1

**2. [Setup deviation] Compiled extension (.so) not present in this worktree**
- **Found during:** Task 1 setup
- **Issue:** The `.venv` editable install pointed to a different worktree (`agent-a2d658478cc54558b`);
  this worktree had no `_native.abi3.so` and the pth file shadowed the package
- **Fix:** Copied the v6.0 `.so` from `agent-a2d658478cc54558b` into this worktree's
  `python/fdars/` and updated `fdars.pth` to point to this worktree's python dir
- **Impact:** Tests now correctly exercise the code in this worktree

### No New Aspect Key (confirmed)

No change to `python/fdars/mcp/server.py`, `python/fdars/mcp/_runner.py`, or
`python/fdars/advisor/__init__.py` (`_supported` set). `test_diagnostics_methods_match_advisor_supported`
passes with 0 edits to the guard files. Guard file diff confirms no change across all 5 commits.

## Test Results

- `tests/test_advisor_outliers_v6.py`: 37 tests passed
- `tests/test_advisor_regression_v6.py`: 29 tests passed
- `tests/test_advisor_group_b.py`: 25 tests passed (+ 2 in TestDeterminism = 27 total, but fixture sharing counted as 25 collection)
- Full suite (excluding live/gemini/ollama/openai): 711 passed, 1 skipped
- MCP server tests: 13 passed (including `test_diagnostics_methods_match_advisor_supported`)

## Self-Check: PASSED

All 8 key files exist on disk. All 5 task commits exist in git history.

| Check | Result |
|-------|--------|
| python/fdars/advisor/aspects/outliers.py | FOUND |
| python/fdars/advisor/aspects/regression.py | FOUND |
| python/fdars/advisor/aspects/classification.py | FOUND |
| python/fdars/advisor/aspects/fpca.py | FOUND |
| python/fdars/advisor/_prompts.py | FOUND |
| tests/test_advisor_outliers_v6.py | FOUND |
| tests/test_advisor_regression_v6.py | FOUND |
| tests/test_advisor_group_b.py | FOUND |
| Commit 6c5357a (Task 1) | FOUND |
| Commit a5ba3c0 (Task 2) | FOUND |
| Commit a7792e3 (Task 3) | FOUND |
| Commit fdaea98 (Task 4) | FOUND |
| Commit 6b70df1 (Task 5) | FOUND |
