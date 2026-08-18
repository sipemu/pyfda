---
phase: 31-group-a-fdars-inference-bindings
fixed_at: 2026-08-17T20:26:00Z
review_path: .planning/phases/31-group-a-fdars-inference-bindings/31-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 31: Code Review Fix Report

**Fixed at:** 2026-08-17T20:26:00Z
**Source review:** `.planning/phases/31-group-a-fdars-inference-bindings/31-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (CR-01, WR-01, WR-02; IN-01 excluded per user instruction)
- Fixed: 3
- Skipped: 0

## Fixed Issues

### CR-01: Negative group labels silently wrap to `usize::MAX` in `oneway_anova_vstat`

**Files modified:** `src/inference_mod.rs`, `tests/test_inference.py`
**Commit:** `6c66a98`
**Applied fix:**
- Added binding-layer guard in `oneway_anova_vstat` before converting `i64` labels to `usize`:
  iterates the raw i64 array and returns `PyValueError` if any element is `< 0`.
- Replaced the `numpy1d_to_usize_vec(groups)` call with an explicit inline `.map(|&x| x as usize)`
  after the guard, so the unchecked converter is no longer on this path.
- Updated the `groups` docstring paragraph: removed the overclaim "any distinct `int64` values define
  the groups"; replaced with "non-negative 0-indexed group labels (dtype int64). Negative values raise
  `ValueError`."
- Updated the `Raises` section to include "or if any group label is negative."
- Added `test_negative_group_label_raises_value_error` to `TestOnewayAnovaVstat` in
  `tests/test_inference.py` covering the `[-1, 0, 0, ...]` case.

### WR-01: Module-level docstring falsely claims `seed=None -> 0` for all functions

**Files modified:** `src/inference_mod.rs`
**Commit:** `6c66a98` (committed with CR-01 since the same file was being edited)
**Applied fix:**
- Replaced the module-level `//!` claim "seed=None resolves to fixed default `0` for
  byte-identical reproducibility across runs" with a scoped version:
  `` `seed=None` resolves to fixed default `0` for [`t_perm_test`] and [`f_perm_test`] ``
  followed by an explicit note that `mean_scb` and `scb_two_sample_test` accept no `seed`
  parameter and their bootstrap randomness is internal to fdars-core.

### WR-02: `TestScbTwoSampleTest` is under-tested relative to sibling classes

**Files modified:** `tests/test_inference.py`
**Commit:** `6c66a98` (committed with CR-01 since the same file was being edited)
**Applied fix:**
- Added three new test methods to `TestScbTwoSampleTest`:
  - `test_p_value_in_range`: asserts `0.0 <= result["p_value"] <= 1.0`.
  - `test_statistic_nonnegative`: asserts `result["statistic"] >= 0.0`.
  - `test_values_plain_types`: calls `json.dumps(result, sort_keys=True)` to detect numpy
    scalar leakage (matching the pattern used in sibling test classes).
- Tests use `nb=50` to keep bootstrap iterations fast in CI.

## Skipped Issues

None.

## Build and Test Results

- `cargo fmt --check`: clean (no formatting changes required)
- `cargo clippy -- -D warnings`: clean (0 warnings or errors)
- `.venv/bin/maturin develop`: compiled successfully
- `.venv/bin/python -m pytest -q`: **495 passed, 4 skipped** (was 491 passed, 4 skipped before fixes)
- Verification ran in the isolated worktree (`rf-31-903234`); re-confirmed green from main after
  fast-forward merge and rebuild.

## Deferred

**IN-01** (`n_perm: usize` UX nit) — excluded per explicit user instruction. Left as-is.

---

_Fixed: 2026-08-17T20:26:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
