---
phase: 28-advisor-extension
plan: "02"
subsystem: advisor
tags: [advisor, diagnostics, imputation, registration, grounding, alignment, represent]
status: complete

dependency_graph:
  requires:
    - "28-01: scoring aspect + _ASPECT_PRIMERS['scoring'] shipped; guard-sync pattern proven"
    - "27-xx: fdars.alignment.{least_squares_score,pairwise_correlation_score,sobolev_least_squares_score} shipped"
    - "26-xx: fdars.scoring.functional_mae, fdars.represent.impute_missing_values shipped"
  provides:
    - "registration-quality diagnostics on alignment aspect (3 fdars-computed scores)"
    - "imputation-quality diagnostics on represent aspect (imputed_fraction + fdars functional_mae)"
    - "_ASPECT_PRIMERS['alignment'] and extended _ASPECT_PRIMERS['represent'] for advise()"
  affects:
    - "28-03 (if any): advisor docs coverage extended to registration + imputation quality"

tech_stack:
  added: []
  patterns:
    - "TDD RED/GREEN per task — test file committed before implementation"
    - "per-score try/except mapping failures to None (alignment registration scores)"
    - "attribute-first/dict-fallback resolution for 'imputed' matrix (represent extension)"
    - "lazy import inside builder branch (fdars.alignment reuse, fdars.scoring lazy import)"
    - "nan-aware data_range_min/max/mean using non-NaN subset (Rule 1 bug fix)"

key_files:
  created:
    - tests/test_advisor_registration_quality.py
    - tests/test_advisor_represent_imputation.py
  modified:
    - python/fdars/advisor/aspects/alignment.py
    - python/fdars/advisor/aspects/represent.py
    - python/fdars/advisor/_prompts.py

decisions:
  - "Registration-quality scores come from three bound fdars.alignment functions — never numpy arithmetic (grounding invariant)"
  - "imputed_fraction is a structural count (NaN cells / total), acceptable without fdars call; imputation_mae uses bound fdars.scoring.functional_mae as the cited evidence value"
  - "pairwise_correlation_score guarded behind n >= 2; sobolev_score uses lambda_=0.0 for grid-agnostic safety"
  - "Backward-compat: new keys default to None when new inputs absent — no change to _supported or _DIAGNOSTICS_METHODS"
  - "[Rule 1 Bug] data_range_min/max/mean in represent.py fixed to use nan-aware subset so float('nan') never leaks into output (breaks == determinism)"

metrics:
  duration: "7m (2026-08-16T19:09:30Z to 2026-08-16T19:16:29Z)"
  completed: "2026-08-16"
  tasks_completed: 3
  commits: 5

actuals:
  tokens: 11000
  tasks: 3
  commits: 5
---

# Phase 28 Plan 02: Imputation-Quality + Registration-Quality Extensions Summary

ADV-02: imputation-quality diagnostics added to the `represent` aspect and registration-quality diagnostics added to the `alignment` aspect, both grounded in bound fdars functions with determinism, no-numpy-scalar, backward-compat, and TDD proof.

## What Was Built

- **`python/fdars/advisor/aspects/alignment.py`** — `_build_alignment_diagnostics` extended with three fdars-computed registration-quality scores as new dict keys, inserted before the convergence block. All three call bound `fdars.alignment.*` functions reusing the existing lazy import; each is wrapped in a per-score `try/except` that maps failures to `None`. `pairwise_correlation_score` is guarded behind `n >= 2`. `sobolev_score` uses `lambda_=0.0` to avoid the uniform-grid requirement. When `aligned_data` or `argvals` is absent, all three keys are `None` — pre-existing behavior unchanged.
  - New keys: `least_squares_score` (lower is better), `pairwise_correlation_score` (higher is better), `sobolev_score` (lower is better; `lambda_=0.0`).

- **`python/fdars/advisor/aspects/represent.py`** — `_build_represent_diagnostics` extended with two imputation-quality keys detected via the attribute-first / dict-fallback resolution of an optional `"imputed"` matrix. When present, `imputed_fraction` is a structural count of NaN cells / total cells; `imputation_mae` is `fdars.scoring.functional_mae(y_true_clean, imputed_arr, argvals)` — the bound fdars function provides the cited evidence number. Lazy import of `fdars.scoring` inside the branch. When `"imputed"` absent, both keys are `None` — backward-compatible.
  - Also fixed: `data_range_min/max/mean` now use a NaN-aware subset (`data[~np.isnan(data)]`) so NaN cells in the original data matrix (which may be present when imputation context is supplied) do not propagate as `float('nan')` which breaks `==` determinism (Rule 1 auto-fix).

- **`python/fdars/advisor/_prompts.py`** — two primer clauses added / updated:
  - `_ASPECT_PRIMERS["alignment"]` (new): explains `least_squares_score` (lower is better — L2 spread around mean), `pairwise_correlation_score` (higher is better — pairwise alignment), and `sobolev_score` (lower is better; `lambda_=0.0`).
  - `_ASPECT_PRIMERS["represent"]` (extended): adds `imputed_fraction` interpretation (high fraction = risky representation) and `imputation_mae` (non-zero = imputer altered observed cells; larger = less consistent).

- **`tests/test_advisor_registration_quality.py`** — 12 offline tests: basic key presence and types, finite-float checks, pre-existing key preservation, backward-compat (3 tests: no aligned_data, no argvals), determinism, no-numpy-scalar recursive walker, grounding via `_extract_numbers`.

- **`tests/test_advisor_represent_imputation.py`** — 14 offline tests: basic key presence, `imputed_fraction` correctness (NaN count / total), `imputation_mae` as finite float, perfect-imputation → MAE = 0, pre-existing key preservation, backward-compat (3 tests: no imputed, no data at all), determinism, no-numpy-scalar recursive walker, grounding via `_extract_numbers`.

## Task Outcomes

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 RED | registration-quality failing tests | 209dfeb | tests/test_advisor_registration_quality.py |
| 1 GREEN | registration-quality implementation | d4a61bc | aspects/alignment.py, _prompts.py |
| 2 RED | imputation-quality failing tests | 524926b | tests/test_advisor_represent_imputation.py |
| 2 GREEN | imputation-quality implementation + Rule 1 fix | 0eb1e7b | aspects/represent.py, _prompts.py |

## Verification

- Guard-sync: `test_diagnostics_methods_match_advisor_supported` — GREEN (no change to `_supported` or `_DIAGNOSTICS_METHODS`)
- Registration quality suite: `tests/test_advisor_registration_quality.py` — 12 passed, 0 failed (offline, no key)
- Imputation quality suite: `tests/test_advisor_represent_imputation.py` — 14 passed, 0 failed (offline, no key)
- Combined offline run: `ANTHROPIC_API_KEY= pytest tests/test_advisor_registration_quality.py tests/test_advisor_represent_imputation.py -q` — 26 passed
- Full suite: `tests/` — 426 passed, 4 skipped, 0 failures (baseline 400 + 26 new)
- No change to `_supported` set (still 13) or `_DIAGNOSTICS_METHODS` (still 13)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] NaN propagation in represent.py data_range statistics**
- **Found during:** Task 2 GREEN — `test_imputation_quality_deterministic` failed because `data_range_min/max/mean` returned `float('nan')` when the original data matrix contained NaN cells (present when imputation context is supplied). `nan != nan` in Python, so `d1 == d2` fails.
- **Fix:** Changed `np.min/max/mean(data)` to use `data[~np.isnan(data)]` (the non-NaN subset), returning `None` when all cells are NaN. This is the correct behavior: the range of the observed values, not the NaN-contaminated raw matrix.
- **Files modified:** `python/fdars/advisor/aspects/represent.py`
- **Commit:** 0eb1e7b (combined with GREEN implementation)

## Known Stubs

None.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Both builders are pure offline Python functions calling already-shipped bound fdars functions. No threat flags.

Threat mitigations from plan:
- T-28-04 (Information Disclosure — Python arithmetic instead of fdars fn): MITIGATED. `imputation_mae` uses `fdars.scoring.functional_mae`; all three registration scores use `fdars.alignment.*` bound functions. Grounding tests verify each cited number is discoverable in the serialised diagnostics.
- T-28-05 (Tampering — silent pre-existing behavior change): MITIGATED. Backward-compat tests in both files assert pre-existing keys are unchanged when new inputs absent.
- T-28-06 (Tampering — numpy scalar leak): MITIGATED. `float(...)` casts on every score/residual value; `check_no_numpy` recursive walker asserts no `np.generic` in output.

## Self-Check: PASSED

- `python/fdars/advisor/aspects/alignment.py` — FOUND (extended)
- `python/fdars/advisor/aspects/represent.py` — FOUND (extended)
- `python/fdars/advisor/_prompts.py` — FOUND (alignment primer added, represent primer extended)
- `tests/test_advisor_registration_quality.py` — FOUND (12 tests)
- `tests/test_advisor_represent_imputation.py` — FOUND (14 tests)
- Commit 209dfeb (RED registration) — FOUND
- Commit d4a61bc (GREEN registration) — FOUND
- Commit 524926b (RED imputation) — FOUND
- Commit 0eb1e7b (GREEN imputation + Rule 1 fix) — FOUND
- Full suite: 426 passed, 4 skipped, 0 failures — PASSED
- Guard-sync: `test_diagnostics_methods_match_advisor_supported` — PASSED
