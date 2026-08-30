---
phase: 52-pipeline-diagnostic-report
fixed_at: 2026-08-30T00:00:00Z
review_path: .planning/phases/52-pipeline-diagnostic-report/52-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 52: Code Review Fix Report

**Fixed at:** 2026-08-30
**Source review:** .planning/phases/52-pipeline-diagnostic-report/52-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 7
- Fixed: 7
- Skipped: 0

## Fixed Issues

### WR-01: Dead import `_check_grounding` in `pipeline_report()`

**Files modified:** `python/fdars/advisor/_pipeline.py`
**Commit:** ba966c4
**Applied fix:** Removed the dead `from fdars.advisor.providers._validate import _check_grounding` import at line 666 (deferred inside `pipeline_report()`). The actual call uses `_check_grounding_pipeline` (the adapter defined in the same file); `_check_grounding` was never referenced after the import.

---

### WR-02: Dead code in `build_pipeline_report()` when `run_llm=True`

**Files modified:** `python/fdars/advisor/_pipeline.py`
**Commit:** 5e3f996
**Applied fix:** Moved `_normalize_stages()` call and result assembly inside the `if not run_llm:` branch only. The LLM path now delegates directly to `pipeline_report()` without first building `blocks`/`result` that were immediately discarded. `build_diagnostics` is now called at most once per stage regardless of which path is taken.

---

### WR-03: Dead parameter `argvals_from_dataset` in `build_pipeline_report_mcp()`

**Files modified:** `python/fdars/mcp/_pipeline.py`
**Commit:** 69b3281
**Applied fix:** Removed the `argvals_from_dataset: bool = True` parameter from the function signature and its corresponding docstring entry. `argvals` are always resolved from the dataset and forwarded to `build_diagnostics` unconditionally, which is the correct and documented behavior. Option (a) from the REVIEW.md was chosen (removal is simpler; no caller passes this flag).

---

### WR-04: Tautological `elif` in Rule-2 fallback chain

**Files modified:** `python/fdars/advisor/_pipeline.py`
**Commit:** d796762
**Applied fix:** Replaced `elif n_out is not None:` (always True inside the `elif n_out is not None and n_obs is None:` outer branch) with `else:` and added a comment clarifying that `n_out is not None` is guaranteed by the outer condition. The logic is semantically identical; the intent is now expressed directly.

---

### WR-05: Silent caveat miss when `n_obs=0` and `n_union_outliers` absent

**Files modified:** `python/fdars/advisor/_pipeline.py`, `tests/test_pipeline_report_advise.py`
**Commit:** 46acef6
**Applied fix:** Added an explicit `elif n_out is not None and n_obs is not None and n_obs == 0 and int(n_out) > 0:` branch in Rule-2. When `n_obs=0` with outliers flagged, the stage is treated as 100% outlier fraction (`fraction_value = 1.0`). If `n_union_outliers` is present it is used as the raw count; otherwise `n_out` is used. Two new tests cover the fix: `test_n_obs_zero_with_outliers_fires_caveat` and `test_n_obs_zero_with_n_union_outliers_fires_caveat`.

---

### WR-06: Missing result key in stage entry raises `TypeError` instead of `ValueError`

**Files modified:** `python/fdars/advisor/_pipeline.py`, `tests/test_pipeline_report.py`
**Commit:** b83a68c
**Applied fix:** Added a `if value is None: raise ValueError(...)` guard in `_normalize_stages` immediately after `_resolve_result()` returns. The error message names the stage index and `stage_name`. Two new tests cover the fix: `test_missing_result_key_raises_value_error_not_type_error` (asserts `ValueError` with stage name in message) and `test_missing_result_key_error_names_stage_index`.

---

### IN-01: `assert` used for runtime invariant enforcement in production code

**Files modified:** `python/fdars/advisor/_pipeline.py`
**Commit:** 55dcab0
**Applied fix:** Replaced `assert raw_value is not None` with an explicit `if raw_value is None: raise AssertionError(...)` guarded by `# pragma: no cover — structural invariant; unreachable by construction`. This is consistent with the Phase-51 CR-02 convention and survives Python `-O` optimized mode. The `AssertionError` type is used (not `ValueError`) to signal a logic bug rather than a user error.

---

## Skipped Issues

None — all findings were fixed.

---

**Verification:** All tests run in the main checkout (no isolated worktree — `workflow.use_worktrees=false` mode). Final run: `85 passed, 1 skipped` (the skip is the live API-key-gated test, present before this phase).

_Fixed: 2026-08-30_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
