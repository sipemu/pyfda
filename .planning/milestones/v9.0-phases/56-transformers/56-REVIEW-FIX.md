---
phase: 56-transformers
fixed_at: 2026-08-31T19:48:47Z
review_path: .planning/phases/56-transformers/56-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 56: Code Review Fix Report

**Fixed at:** 2026-08-31T19:48:47Z
**Source review:** `.planning/phases/56-transformers/56-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 7
- Fixed: 7
- Skipped: 0

## Fixed Issues

### WR-01: Imputer TypeError narrowing

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** ca4c748
**Applied fix:** Extracted a module-level `_validate_allow_nan(estimator, X, *, reset)` helper that
checks BOTH `"unexpected keyword argument"` AND `"ensure_all_finite"`/`"force_all_finite"` in the
exception message before swallowing the old-sklearn TypeError. The two duplicated try/except blocks
in `Imputer.fit` and `Imputer.transform` are replaced with single calls to `_validate_allow_nan`.

### WR-02: SplineInterpolator silent order clamp

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** ca4c748
**Applied fix:** Added `warnings.warn(..., UserWarning, stacklevel=2)` when `effective_order <
order` (i.e., when the grid is too small for the requested spline order). The clamp behavior is
preserved so `check_estimator` still passes on small datasets. The warning appears in the test
output (28 warnings from sklearn battery runs, all expected).

### WR-03: Stale docstring tally in `_coverage.py`

**Files modified:** `python/fdars/sklearn/_coverage.py`
**Commit:** 9d5e005
**Applied fix:** Updated the module docstring header tally from the Phase-55 baseline (`PASS: 6,
PASS-WITH-FIXES: 22`) to the post-Phase-56 values (`PASS: 9, PASS-WITH-FIXES: 19`). Removed the
redundant incremental commentary lines (Phase 56 Plan 01/02) and replaced with a single
authoritative tally. Now matches `TRIAGE_VERDICTS` exactly.

### WR-04: BasisRepresentation.fit discards coefficients without comment

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** ca4c748
**Applied fix:** Added a clear multi-line comment in `BasisRepresentation.fit` explaining the
intentional discard: fit calls `fdata_to_basis_1d` only to learn `actual_n_basis`; coefficients
from fit are never reused because `transform` always re-projects its own input. Renamed the discard
variable from `_` to `_coeffs_fit` to make the intent explicit in the code. No semantics changed.

### IN-01: `test_transformers_never_construct_fdata` missed base class

**Files modified:** `tests/sklearn/test_transformer_pipeline.py`
**Commit:** c1c6573
**Applied fix:** Added `from fdars.sklearn._base import _BaseFdarsEstimator` import and a
`base_source = inspect.getsource(_BaseFdarsEstimator)` check inside the parametrized test. Both
`"Fdata(" not in source` (subclass) and `"Fdata(" not in base_source` (shared base) are now
asserted.

### IN-02: No pipeline test exercising Imputer

**Files modified:** `tests/sklearn/test_transformer_pipeline.py`
**Commit:** c1c6573
**Applied fix:** Added `test_imputer_basis_pipeline_roundtrip()` that injects a sparse NaN pattern
(`X[::5, ::7] = np.nan`) and runs `Pipeline([Imputer(), BasisRepresentation(n_basis=3)])` through
both `fit+transform` and `fit_transform`. Asserts output shape equals input shape and all values
are finite. A second pipeline instance is used to verify `fit_transform` consistency.

### IN-03: SplineInterpolator order int/float handling not deterministic

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** ca4c748
**Applied fix:** Extracted `order = int(self.order)` before the `< 1` validation check so that
float truncation is deterministic and occurs before any comparison. Updated the docstring to note
that non-integer values are truncated to `int`. The `< 1` rejection and the clamping now both
operate on the int-cast value consistently.

---

**Verification:** Ran in main checkout (no worktree — `workflow.use_worktrees=false`).

```
.venv/bin/pytest tests/sklearn/test_transformers_compliance.py \
    tests/sklearn/test_transformer_pipeline.py \
    tests/sklearn/test_coverage.py -q

482 passed, 28 warnings in 2.60s
```

All 8 transformers continue to pass their full `parametrize_with_checks` battery. The 28 warnings
are the new `UserWarning` clamping notifications from `SplineInterpolator.fit` — expected and
correct. The new `test_imputer_basis_pipeline_roundtrip` passes. `git diff --quiet HEAD` is clean.

---

_Fixed: 2026-08-31T19:48:47Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
