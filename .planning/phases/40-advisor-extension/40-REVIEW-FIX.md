---
phase: 40-advisor-extension
fixed_at: 2026-08-21T08:30:00Z
review_path: .planning/phases/40-advisor-extension/40-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 40: Code Review Fix Report

**Fixed at:** 2026-08-21T08:30:00Z
**Source review:** `.planning/phases/40-advisor-extension/40-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01, WR-02, WR-03, IN-01, IN-02; IN-03 explicitly out of scope per fix instructions)
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: Outlier primer references wrong key names for muod counts

**Files modified:** `python/fdars/advisor/_prompts.py`
**Commit:** befa49f
**Applied fix:** Updated the "For muod" clause in the `"outliers"` primer to reference `n_muod_magnitude_outliers` and `n_muod_shape_outliers` (the prefixed keys actually emitted by the code) instead of the bare `n_magnitude_outliers` / `n_shape_outliers` that belong to the tvdmss block. Cross-verified by grep: every key the primer now names exists in `outliers.py`.

---

### WR-02: Outlier primer references wrong key names for depthgram counts and ranges

**Files modified:** `python/fdars/advisor/_prompts.py`
**Commit:** befa49f
**Applied fix:** Updated the "For depthgram" clause to reference `n_depthgram_shape_outliers`, `n_depthgram_magnitude_outliers`, `depthgram_mbd_range`, and `depthgram_mei_range` (all prefixed, matching the actual emitted keys) instead of the unprefixed names that would resolve to tvdmss / outliergram slots. Cross-verified by grep.

---

### WR-03: n_obs=0 edge case emits fabricated 0.0 fraction instead of None

**Files modified:** `python/fdars/advisor/aspects/outliers.py`
**Commit:** befa49f
**Applied fix:** Changed the `else` fallback in the tvdmss block (lines 188-189) and the depthgram block (lines 283-284) from `0.0` to `None`. This matches the existing muod pattern and avoids emitting an ungrounded sentinel value when the denominator is zero. The normal-path fractions (`n_obs > 0`) are unchanged.

---

### IN-01: Function-level docstring in outliers.py not updated for new branches

**Files modified:** `python/fdars/advisor/aspects/outliers.py`
**Commit:** befa49f
**Applied fix:** Rewrote the `_build_outliers_diagnostics` function docstring. The one-liner now correctly says "seven result shapes" (was "four"). The `Parameters` block enumerates all seven result dict shapes (detect_outliers_lrt/with_dist, outliergram, magnitude_shape, tvdmss, muod, sequential_transform_outliers, depthgram). The `Returns` block now lists all ~35 output fields including the new tvdmss, muod, sequential_transform, and depthgram keys with their types and None-emission conditions.

---

### IN-02: Function-level docstring in regression.py not updated for new branches

**Files modified:** `python/fdars/advisor/aspects/regression.py`
**Commit:** befa49f
**Applied fix:** Extended the `_build_regression_diagnostics` docstring. The `Parameters` block now lists `functional_glm` and `concurrent_regression` alongside the original seven functions. The `Returns` block adds 11 new fields: `has_functional_glm`, `deviance`, `aic`, `bic`, `log_likelihood`, `iterations`, `glm_ncomp`, `family`, `has_concurrent_regression`, `concurrent_residual_rms`, `concurrent_residual_max_abs`, and `n_predictors`.

---

## Skipped Issues

None.

---

## Verification

**Ran in:** isolated worktree `rf-40-1750880-1787299006` (branch `gsd-reviewfix/40-1750880`), then fast-forwarded to `main`.

- Tier 1 (re-read): all modified sections confirmed correct after each edit.
- Tier 2 (syntax): `python3 -c "import ast; ast.parse(...)"` passed for all three files.
- Tier 2 (test suite):
  - `pytest tests/ -k advisor -q`: **304 passed, 4 skipped, 0 failed**
  - `pytest tests/ -q`: **772 passed, 4 skipped, 0 failed**
- No tests asserted on old primer key names; no test failures from the `None` fraction change.
- IN-03 (test helper deduplication) was explicitly excluded from scope per fix instructions.

---

_Fixed: 2026-08-21T08:30:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
