---
phase: 72-advisor-extension
plan: "03"
subsystem: advisor
tags: [advisor, diagnostics, regression, classification, spm, shapelet, mfpca, fof, fam]

requires:
  - phase: 72-advisor-extension
    provides: "72-01 (fts aspect), 72-02 (frechet aspect) — extended aspects share existing guard-sync structure"

provides:
  - "regression.py extended with fof_regression / fof_re_regression / fam / fregre_gkam branches"
  - "classification.py extended with shapelet_classifier opaque-handle branch"
  - "spm.py extended with mfpca dict branch + spe_multivariate naked-array branch"
  - "__init__.py shapelet handle coercion guard before dict(raw)"
  - "tests/test_advisor_regression_v6.py: +TestFofRegression + TestFofReRegression + TestFamGkam"
  - "tests/test_advisor_group_b.py: +TestShapeletClassifier"
  - "tests/test_advisor_spm_v11.py (new): TestMfpca + TestSpeMultivariate + TestSpmPhase1Regression"

affects: [72-advisor-extension, advisor, mcp]

actuals:
  tokens: 10936
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Opaque-handle coercion: hasattr-based detection in __init__.py BEFORE dict(raw) for PyO3 handles without __array__"
    - "Array-first guard: spe_multivariate naked-array path checked first in builder, preventing dict method calls on ndarray"
    - "Multi-branch builder: single builder function dispatches 3+ distinct result shapes via discriminator keys"
    - "TDD: RED (test) then GREEN (impl) for each of the 3 tasks"

key-files:
  created:
    - tests/test_advisor_spm_v11.py
  modified:
    - python/fdars/advisor/aspects/regression.py
    - python/fdars/advisor/aspects/classification.py
    - python/fdars/advisor/aspects/spm.py
    - python/fdars/advisor/__init__.py
    - tests/test_advisor_regression_v6.py
    - tests/test_advisor_group_b.py

key-decisions:
  - "fam/fregre_gsam share the same 7-key dict — single has_fam discriminator covers both (component_fits + fitted_values); no separate gsam branch needed"
  - "gkam also triggers has_fam (shares those keys) — has_fregre_gkam is the specific discriminator; overlap documented as acceptable"
  - "Shapelet coercion in __init__.py not in classification.py — the guard must run before the generic dict(raw) block, so it belongs at the dispatch level"
  - "spe_multivariate array path returns early with all spm_phase1/mfpca fields set to None — avoids any raw.get() on an array"

patterns-established:
  - "Grounding invariant: float()/int()/bool() cast on every numeric; None fallback on every optional key"
  - "has_X discriminator pattern: stable False branch sets all X-fields to None for every result that doesn't trigger"

requirements-completed: [ADV-01, ADV-02]

coverage:
  - id: D1
    description: "regression.py has_fof_regression branch: beta_surface_shape [int,int], beta_surface_max_abs float, fof_r_squared float, fof_ncomp [int,int] — all grounded, JSON-serialisable"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_regression_v6.py::TestFofRegression"
        status: pass
    human_judgment: false
  - id: D2
    description: "regression.py has_fof_re_regression branch: n_subjects int, sigma2_u_max float, re_dims [int,int], sigma2_eps float"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_regression_v6.py::TestFofReRegression"
        status: pass
    human_judgment: false
  - id: D3
    description: "regression.py has_fam + has_fregre_gkam branches: fam_n_obs, fam_n_components, fam_r_squared, fam_ncomp; gkam_converged bool, gkam_bandwidths list[float], gkam_n_predictors int"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_regression_v6.py::TestFamGkam"
        status: pass
    human_judgment: false
  - id: D4
    description: "__init__.py shapelet opaque-handle coercion guard (hasattr train_accuracy + n_shapelets) placed BEFORE dict(raw) — no TypeError on PyShapeletClassifierFit"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_group_b.py::TestShapeletClassifier::test_shapelet_handle_accepted_no_type_error"
        status: pass
      - kind: automated_ui
        ref: "grep line-order verify: guard_line 169 < dict_line 180"
        status: pass
    human_judgment: false
  - id: D5
    description: "classification.py has_shapelet_classifier branch: shapelet_n_shapelets int, shapelet_train_accuracy float [0,1], shapelet_n_classes int"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_group_b.py::TestShapeletClassifier"
        status: pass
    human_judgment: false
  - id: D6
    description: "spm.py has_spe_multivariate branch (array-first guard): spe_mv_n_obs int, spe_mv_max/mean float, spe_mv_all_nonneg bool"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_spm_v11.py::TestSpeMultivariate"
        status: pass
    human_judgment: false
  - id: D7
    description: "spm.py has_mfpca branch: mfpca_ncomp int, mfpca_n_obs int, mfpca_n_variables int, mfpca_eigenvalues list[float], mfpca_variance_explained_cumulative via _eigenvalues_to_variance_cumulative"
    requirement: ADV-01
    verification:
      - kind: unit
        ref: "tests/test_advisor_spm_v11.py::TestMfpca"
        status: pass
    human_judgment: false
  - id: D8
    description: "All new diagnostics grounding invariant: json.dumps deterministic, no np.generic scalars, existing paths unaffected (regression/classification/spm guard tests pass)"
    requirement: ADV-02
    verification:
      - kind: unit
        ref: "tests/test_guard_sync_version_independent.py + tests/test_advisor_grounding.py (185 total, all pass)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-04
status: complete
---

# Phase 72 Plan 03: Advisor Extension — regression / classification / spm Summary

**Extends three existing advisor aspect builders for the v11.0 new methods (fof/fof_re/fam/gkam/shapelet/mfpca/spe_multivariate) with grounded, JSON-serialisable, numpy-scalar-free diagnostics; shapelet opaque-handle TypeError prevented by coercion guard in __init__.py.**

## Performance

- **Duration:** 8 min
- **Tasks:** 3/3 completed
- **Commits:** 3 production commits

## Accomplishments

- **regression.py** extended with four new branches using CONFIRMED keys from Rust bindings:
  - `has_fof_regression` (beta_surface in raw): beta_surface_shape, beta_surface_max_abs, fof_r_squared, fof_ncomp
  - `has_fof_re_regression` (random_effects + n_subjects in raw): n_subjects, sigma2_u_max, sigma2_eps, re_dims
  - `has_fam` (component_fits + fitted_values in raw): fam_n_obs, fam_n_components, fam_r_squared, fam_ncomp (covers fam + fregre_gsam)
  - `has_fregre_gkam` (converged + bandwidths in raw): gkam_converged, gkam_bandwidths, gkam_n_predictors

- **classification.py** extended with `has_shapelet_classifier` branch (n_shapelets in raw): shapelet_n_shapelets, shapelet_train_accuracy, shapelet_n_classes. The PyShapeletClassifierFit opaque handle is converted to a plain dict in `__init__.py` before the generic dict(raw) block runs, preventing TypeError.

- **spm.py** extended with two new result-shape branches:
  - `has_spe_multivariate` (naked array path, checked FIRST): spe_mv_n_obs, spe_mv_max, spe_mv_mean, spe_mv_all_nonneg. Returns early; no dict access on array.
  - `has_mfpca` (eigenfunctions + scales in raw): mfpca_ncomp, mfpca_n_obs, mfpca_n_variables, mfpca_eigenvalues, mfpca_variance_explained_cumulative (reuses `_eigenvalues_to_variance_cumulative`).

- **185 tests pass**: 60 regression (v6) + 55 group_b + 28 spm_v11 + 42 guard_sync/grounding.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Wrong shapelet_classifier_fit kwarg in test fixture**
- **Found during:** Task 2 RED phase
- **Issue:** Plan said `n_shapelets=4` but the function signature uses `max_shapelets`
- **Fix:** Changed to `min_length=3, max_shapelets=4` after reading src/shapelet_mod.rs:386-388
- **Commit:** 0746935

**2. [Rule 3 - Blocking] Wrong fclassif_knn kwarg in regression-guard test**
- **Found during:** Task 2 GREEN phase
- **Issue:** Used `n_neighbors=3` but signature is `k=`
- **Fix:** Changed to `k=3`
- **Commit:** 0746935

**3. [Rule 3 - Blocking] spm_phase1 missing argvals parameter in test fixture**
- **Found during:** Task 3 GREEN phase
- **Issue:** `spm.spm_phase1(data)` fails — requires `argvals` positional arg
- **Fix:** Added `argvals = np.linspace(0.0, 1.0, m)` and passed it
- **Commit:** 0e9d6a2

**4. [Rule 1 - Bug] Comment in __init__.py contained dict(raw) literal**
- **Found during:** Task 2 plan verify
- **Issue:** The plan's verify grep uses `grep -n 'dict(raw)'` to find the actual coercion call; my added comment block also contained the literal, making the first match land on a comment BEFORE the guard line, failing the guard < dict line-order check
- **Fix:** Rewrote the comment to remove `dict(raw)` literal references
- **Commit:** 0746935

## Self-Check: PASSED

All files confirmed on disk:
- `python/fdars/advisor/aspects/regression.py` — FOUND
- `python/fdars/advisor/aspects/classification.py` — FOUND
- `python/fdars/advisor/aspects/spm.py` — FOUND
- `python/fdars/advisor/__init__.py` — FOUND
- `tests/test_advisor_regression_v6.py` — FOUND
- `tests/test_advisor_group_b.py` — FOUND
- `tests/test_advisor_spm_v11.py` — FOUND

Commits confirmed:
- 2516f86: feat(72-03): extend regression aspect for fof/fof_re/fam/gkam branches — FOUND
- 0746935: feat(72-03): add shapelet handle coercion + classification branch — FOUND
- 0e9d6a2: feat(72-03): extend spm aspect for mfpca + spe_multivariate branches — FOUND
