---
phase: 68-function-on-function-scalar-on-function-regression
fixed_at: 2026-09-02T00:00:00Z
review_path: .planning/phases/68-function-on-function-scalar-on-function-regression/68-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 68: Code Review Fix Report

**Fixed at:** 2026-09-02
**Source review:** .planning/phases/68-function-on-function-scalar-on-function-regression/68-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03 — Info findings excluded per fix_scope)
- Fixed: 3
- Skipped: 0

## Fixed Issues

### WR-01: Negative `subject_ids` values silently produce corrupt usize IDs

**Files modified:** `src/regression_mod.rs`, `tests/test_fof_regression.py`
**Commit:** 86cface
**Applied fix:** Added `I64_MAX_AS_USIZE` sentinel check inside `validate_subject_ids` between the
length check and the group-count check. If any element exceeds `i64::MAX as usize` (indicating a
wrapped negative i64), the function returns `PyValueError` with a "non-negative integers" message.
Both `fof_re_regression` and `predict_fof_re` share `validate_subject_ids` so both benefit.
Also added a test case in `test_subject_id_validation` that passes `[-1, 0, 0, ...]` and asserts
`ValueError` matching "non-negative".

**Verification:** `maturin develop` clean (no `-D warnings` violations); `pytest tests/test_fof_regression.py -x -q` 10 passed.

---

### WR-02: `fof_re_regression` key-set not exhaustively tested

**Files modified:** `tests/test_fof_regression.py`
**Commit:** 5ea7023
**Applied fix:** Added an exhaustive `set(result) == expected_re_keys` assertion to
`test_fof_re_regression_shapes`, using the exact 13 key names from the PyDict construction in
`regression_mod.rs` (intercept, beta_surface, fitted, residuals, r_squared_t, r_squared, ncomp_x,
ncomp_y, coef_matrix, random_effects, sigma2_u, sigma2_eps, n_subjects). The explicit
`fpca_x`/`fpca_y` absence checks are retained after the set assertion. This mirrors the
exact-match style of `test_fof_regression_key_set`.

**Verification:** `pytest tests/test_fof_regression.py -x -q` 10 passed.

---

### WR-03: `predict_fof_re` single-group validation not tested

**Files modified:** `tests/test_fof_regression.py`
**Commit:** 84ba2e8
**Applied fix:** Added a `pytest.raises(ValueError, match="at least 2 distinct subjects")` block
for `predict_fof_re` with `np.zeros(N, dtype=np.int64)` (single group) inside
`test_subject_id_validation`, immediately after the existing wrong-length block for
`predict_fof_re`. This closes the coverage gap: if a future refactor removed the
`validate_subject_ids` call from `predict_fof_re`, the test would fail.

**Verification:** `pytest tests/test_fof_regression.py -x -q` 10 passed.

---

## Full-Suite Results

After all three fixes, full suite ran in the main checkout:

```
5386 passed, 10 skipped, 120 warnings in 149.78s (0:02:29)
```

Verification ran in the **main checkout** (workflow.use_worktrees=false; no isolated worktree).
No regressions introduced.

---

_Fixed: 2026-09-02_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
