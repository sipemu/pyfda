---
phase: 69-frechet-regression-density-fda
fixed_at: 2026-09-03T00:00:00Z
review_path: .planning/phases/69-frechet-regression-density-fda/69-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 69: Code Review Fix Report

**Fixed at:** 2026-09-03
**Source review:** `.planning/phases/69-frechet-regression-density-fda/69-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (1 Critical + 3 Warning; Info findings excluded per constraint)
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-03: Misleading `frechet_anova` k=0 error message

**Files modified:** `src/frechet_mod.rs`
**Commit:** 3c74d93
**Applied fix:** Split the merged `if !contiguous || k == 0` branch into two separate
checks. The new `k == 0` branch returns `"group_labels is empty — at least 2 groups required"`.
The `!contiguous` branch now safely uses `k - 1` (no `saturating_sub` needed since k > 0 is
guaranteed at that point), yielding correct text like `"0, 1, …, 2"`.

---

### CR-01: `flat_col_major_to_numpy2d` panics on mismatched `d` vs `result.len()`

**Files modified:** `src/frechet_mod.rs`
**Commit:** 2978fd0
**Applied fix:** Changed the helper return type from `Bound<'py, PyArray2<f64>>` to
`PyResult<Bound<'py, PyArray2<f64>>>`. Added a `result.len() != d * d` guard at the
top of the function that returns a descriptive `PyValueError` before any indexing.
Updated both call sites (SPD arm line ~414, correlation arm line ~484) from
`.into_any()` to `?.into_any()` to propagate the error. The `.unwrap()` inside the
function is now safe because it is only reached when all rows have exactly `d` elements.

---

### WR-01: `density_fda_mod.rs` functions declared `fn` instead of `pub fn`

**Files modified:** `src/density_fda_mod.rs`
**Commit:** ca3e53a
**Applied fix:** Added `pub` to all five `#[pyfunction]`-decorated functions:
`normalize_density`, `lqd_transform`, `inverse_lqd`, `wasserstein_barycenter`, `lqd_fpca`.
No behavior change; this aligns the module with all 20+ other modules in the codebase
and with the CLAUDE.md convention.

---

### WR-02: Symmetry validation for `space='correlation'` has zero test coverage

**Files modified:** `tests/test_frechet.py`
**Commit:** c5fb768
**Applied fix:** Added `test_non_symmetric_raises` to `TestFrechetMeanCorrelation`.
The test constructs a valid correlation matrix, breaks symmetry by setting
`bad[0,1] += 0.5` and `bad[1,0] -= 0.5` (diagonal stays 1), then asserts that
`frechet_mean(..., space="correlation", ...)` raises `ValueError` matching `"symmetric"`.
This exercises the code path at `frechet_mod.rs:451-458` that was previously untested.

## Skipped Issues

None.

---

## Verification

All fixes verified in the **main checkout** (not an isolated worktree; `workflow.use_worktrees=false`).

- **Tier 2 (build):** `maturin develop` completed with 0 warnings after each Rust change.
- **Tier 2 (targeted tests):** `pytest tests/test_frechet.py tests/test_density_fda.py -x -q`
  — 53 passed after all fixes (52 before + 1 new WR-02 test).
- **Full suite:** `pytest tests/ -q` — **5443 passed, 10 skipped, 0 failures**
  (warnings are pre-existing sklearn compatibility notices, unrelated to phase 69 changes).

---

_Fixed: 2026-09-03_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
