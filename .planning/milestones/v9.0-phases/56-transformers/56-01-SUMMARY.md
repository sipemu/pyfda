---
phase: 56-transformers
plan: "01"
subsystem: sklearn-compliance
tags: [sklearn, transformers, compliance, imputer, fpca, check-estimator]
dependency_graph:
  requires: [55-compliance-triage-foundation]
  provides: [imputer-pass, transformer-compliance-harness]
  affects: [python/fdars/sklearn/_skeletons.py, python/fdars/sklearn/_coverage.py, tests/sklearn/]
tech_stack:
  added: []
  patterns:
    - "Narrowed except TypeError to shim-keyword-only in ensure_all_finite/force_all_finite cross-version compat"
    - "accept_sparse=False in validate_data calls to reject sparse input with sklearn-convention TypeError"
    - "Per-transformer parametrize_with_checks harness (one decorated function per estimator)"
key_files:
  modified:
    - python/fdars/sklearn/_skeletons.py
    - python/fdars/sklearn/_coverage.py
  created:
    - tests/sklearn/test_transformers_compliance.py
decisions:
  - "Narrowed except TypeError to check 'ensure_all_finite' in str(exc) rather than catching all TypeErrors — prevents dtype/sparse TypeErrors from being swallowed and re-raised as the wrong error"
  - "accept_sparse=False added to both branches of both try/except blocks in Imputer.fit and Imputer.transform — ensures sparse rejection happens before the shim fallback path"
  - "Separate parametrize_with_checks function per transformer (not a shared list) — each transformer's battery is independently selectable without re-running the full 28-estimator triage"
metrics:
  duration: "4m 5s"
  completed: "2026-08-31"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
status: complete
actuals:
  tokens: 8200
  tasks: 3
  commits: 3
---

# Phase 56 Plan 01: Tracer — Imputer Promotion + Compliance Harness Summary

Promoted Imputer to full `parametrize_with_checks`-green (46/46 checks) and built the per-transformer compliance harness regression-guarding all 5 already-PASS transformers (281 checks total).

## What Was Built

**Imputer fix (`_skeletons.py`):** Two changes to `Imputer.fit` and `Imputer.transform`:

1. Added `accept_sparse=False` to all four `_validate` calls (both branches of both try/except blocks). This causes sparse input to raise sklearn's built-in "Sparse data was passed for X, but dense data is required" TypeError at the `validate_data` layer — exactly the message the compliance checks look for.

2. Narrowed the `except TypeError` clause to only re-try with `force_all_finite` when the error is specifically about the `ensure_all_finite` keyword being unexpected (i.e., on sklearn 1.3-1.5). On sklearn 1.8, any other TypeError (dtype conversion failure when object dtype contains dicts, sparse rejection) now propagates correctly instead of being swallowed and re-raised as a wrong-keyword error.

**Per-transformer compliance harness (`tests/sklearn/test_transformers_compliance.py`):** One `@parametrize_with_checks([...])` function per transformer. Each function's battery runs independently, so a single transformer can be re-run without touching others. Placeholders left for Plan 02 (BasisRepresentation, SplineInterpolator).

**Coverage verdict (`_coverage.py`):** `TRIAGE_VERDICTS["Imputer"]` updated from `"PASS-WITH-FIXES: ..."` to `"PASS"`. Tally comment updated to `7 PASS + 21 PASS-WITH-FIXES`.

## Verification Results

| Check | Result |
|-------|--------|
| `test_imputer_compliance` (46 checks) | 46/46 PASS |
| `test_fpca_compliance` (47 checks) | 47/47 PASS |
| `test_bspline_smoother_compliance` (47 checks) | 47/47 PASS |
| `test_local_poly_smoother_compliance` (47 checks) | 47/47 PASS |
| `test_depth_transformer_compliance` (47 checks) | 47/47 PASS |
| `test_norm_transformer_compliance` (47 checks) | 47/47 PASS |
| `test_coverage.py` (96 checks) | 96/96 PASS |
| `import fdars` | OK |
| Imputer constructs no Fdata | OK |
| `__init__.py` git-diff | empty |

## Deviations from Plan

None — plan executed exactly as written. The test file for Task 2 was created before running Task 1's verify (since Task 1's `<verify>` targets `test_transformers_compliance.py::test_imputer_compliance`); the Imputer fix was verified via triage first, then formally via the compliance harness. No extra changes were required.

## Self-Check: PASSED

All files present. All 3 commits verified in git history. 281 compliance checks green.
