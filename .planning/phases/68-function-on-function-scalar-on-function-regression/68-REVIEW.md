---
phase: 68-function-on-function-scalar-on-function-regression
reviewed: 2026-09-02T00:00:00Z
depth: deep
files_reviewed: 6
files_reviewed_list:
  - src/regression_mod.rs
  - src/scalar_on_function_mod.rs
  - src/lib.rs
  - python/fdars/__init__.py
  - tests/test_fof_regression.py
  - tests/test_scalar_on_function.py
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: findings
---

# Phase 68: Code Review Report

**Reviewed:** 2026-09-02
**Depth:** deep
**Files Reviewed:** 6
**Status:** findings

## Summary

Phase 68 adds function-on-function (FOF) regression to `fdars.regression` and creates a new
`fdars.scalar_on_function` submodule. The implementation is structurally sound: both 2D inputs go
through `numpy2d_to_fdmatrix`, `beta_surface` is returned via `fdmatrix_to_numpy2d` (which preserves
the `(m_y, m_x)` orientation from FdMatrix), the combined-refit predict functions reuse the exact
same parameter set used during fitting, `FofReConfig` is constructed by struct literal (correctly — it
is not `#[non_exhaustive]`), the additive configs use `Default::default()` + field mutation (correct
for `#[non_exhaustive]`), and the multi-predictor borrow pattern (`Vec<FdMatrix>` → `Vec<&FdMatrix>`)
is sound.

Three warnings and three info items follow. There are no critical/security/data-loss issues.

---

## Warnings

### WR-01: Negative `subject_ids` values silently produce corrupt usize IDs

**File:** `src/regression_mod.rs:1524` (also `src/regression_mod.rs:1616`)

**Issue:** `numpy1d_to_usize_vec` casts `i64 → usize` with `x as usize`. A negative value such as
`-1_i64` becomes `usize::MAX` (18446744073709551615 on 64-bit). The `validate_subject_ids` helper
does not screen for negatives. Because the negative value passes the length check and counts as a
distinct "subject" in the `sort_unstable + dedup` group-count, it silently reaches
`fdars_core::fof_regression::fof_re_regression` as a valid-looking but enormous subject ID.
The upstream `build_subject_map` typically uses a `HashMap<usize, Vec<usize>>` (or equivalent) so it
will not panic — it creates an entry for `usize::MAX` — but the resulting random-effects fit is
silent data corruption: observations with that ID are treated as a distinct subject group.

The docstring says "Must be non-negative i64 values" but there is no enforcement.

This pattern also exists in the prior `fanova` binding at `regression_mod.rs:404`, but Phase 68
introduced the subject-id validation function that is the natural place to add this guard.

**Fix:**
```rust
fn validate_subject_ids(sid: &[usize], n_obs: usize) -> PyResult<()> {
    // ... existing length check ...

    // Guard against negative i64 values that silently wrapped to huge usize
    // (caller conversion: numpy1d_to_usize_vec casts i64 as usize without sign check)
    const I64_MAX_AS_USIZE: usize = i64::MAX as usize;
    if let Some(&bad) = sid.iter().find(|&&v| v > I64_MAX_AS_USIZE) {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "subject_ids contains a negative value (wrapped to {} after i64→usize cast); \
             all subject IDs must be non-negative integers",
            bad
        )));
    }
    // ... existing group-count check ...
}
```

---

### WR-02: `fof_re_regression` key-set not exhaustively tested — extra fields would be silently exposed

**File:** `tests/test_fof_regression.py:223-258`

**Issue:** `test_fof_regression_key_set` (line 81) uses `assert set(result) == expected_keys` to
guarantee exactly 9 keys for `fof_regression` with no leakage. The analogous test for
`fof_re_regression`, `test_fof_re_regression_shapes`, checks selected field shapes but never asserts
`set(result) == expected_keys` against the complete 13-key set. If an `fpca_x`, `fpca_y`, or any
unexpected field were inadvertently added to the `fof_re_regression` dict assembly, this test would
not catch it — it only checks that certain keys exist and that `"fpca_x"` and `"fpca_y"` are absent.

This is a test-reliability defect: the coverage asymmetry between `fof_regression` and
`fof_re_regression` leaves the RE binding's key contract untested for additions.

**Fix:** Add an exhaustive key-set assertion to `test_fof_re_regression_shapes`:
```python
expected_re_keys = {
    "intercept", "beta_surface", "fitted", "residuals",
    "r_squared_t", "r_squared", "ncomp_x", "ncomp_y",
    "coef_matrix", "random_effects", "sigma2_u", "sigma2_eps", "n_subjects",
}
assert set(result) == expected_re_keys, (
    f"Key mismatch.\n  Got:      {sorted(result)}\n"
    f"  Expected: {sorted(expected_re_keys)}"
)
```

---

### WR-03: `predict_fof_re` single-group validation not tested

**File:** `tests/test_fof_regression.py:274-308`

**Issue:** `test_subject_id_validation` tests the wrong-length error for `predict_fof_re` (line 298)
but does not test the single-group case for `predict_fof_re`. The single-group guard is present in
the implementation (both functions call `validate_subject_ids`), but test coverage only covers
`fof_re_regression` for the single-group case. If a future refactor accidentally removed the
`validate_subject_ids` call from `predict_fof_re`, this gap would let it pass silently.

**Fix:**
```python
# Add to test_subject_id_validation, after the existing predict_fof_re wrong-length block:
with pytest.raises(ValueError, match="at least 2 distinct subjects"):
    reg.predict_fof_re(
        _x_data,
        _y_data,
        np.zeros(N, dtype=np.int64),  # single group
        _new_x,
        _x_argvals,
        _y_argvals,
    )
```

---

## Info

### IN-01: No validation that `predictors` and `argvals_list` have equal length in `fregre_gkam` / `variable_selection`

**File:** `src/scalar_on_function_mod.rs:252-274` (fregre_gkam), `src/scalar_on_function_mod.rs:351-376` (variable_selection)

**Issue:** Both multi-predictor functions accept `Vec<PyReadonlyArray2>` (predictors) and
`Vec<PyReadonlyArray1>` (argvals_list) as separate arguments. If a caller passes
`predictors=[A, B]` but `argvals_list=[a]` (lengths differ), the binding passes mismatched
`pred_refs` and `argvals_refs` slices of different lengths to fdars-core. The upstream function will
produce an `FdarError::InvalidDimension` in most cases, but the error message at that point will not
clearly identify the Python-side mismatch. Adding an explicit pre-call check produces a better
user-facing message. This is the same pattern as the existing `fanova` binding which has no such
guard, so this is consistent with codebase convention — but still a quality gap worth addressing.

**Fix:**
```rust
if pred_mats.len() != argvals_vecs.len() {
    return Err(pyo3::exceptions::PyValueError::new_err(format!(
        "predictors length {} does not match argvals_list length {}",
        pred_mats.len(), argvals_vecs.len()
    )));
}
```

---

### IN-02: `test_scalar_on_function.py` has no error guard tests for `fam`, `fregre_gsam`, `fregre_gkam`

**File:** `tests/test_scalar_on_function.py`

**Issue:** The RESEARCH.md §11 coverage checklist includes testing that invalid inputs raise
`ValueError` for the scalar-on-function functions. Only `variable_selection` has an error guard test
(`test_variable_selection_invalid_penalty_raises`). There are no tests verifying that `fam`,
`fregre_gsam`, or `fregre_gkam` raise `ValueError` on shape mismatches (e.g., `y` length != `n`,
or empty predictor list for `fregre_gkam`). Since these errors are expected to propagate from
fdars-core via `to_pyresult`, the most useful gap to fill is confirming the propagation path works
at the boundary level.

---

### IN-03: `fdmatrix_to_numpy2d` in `convert.rs` contains a bare `unwrap()` that panics on zero-dimension matrix

**File:** `src/convert.rs:57`

**Issue:** `PyArray2::from_vec2` returns `Err` if any row has a different length from others. The
implementation builds rows from slices of the flat `row_major` buffer where each row is exactly
`ncols` elements, so in practice the rows are always equal-length and the unwrap is safe. However,
if `nrows == 0` or `ncols == 0`, `from_vec2` receives an empty or single-row slice and the call
still succeeds — this is not a crash path. The `unwrap()` is pre-existing code (not introduced by
Phase 68), and this note is raised here because Phase 68 adds two new callers
(`fdmatrix_to_numpy2d` for `beta_surface`, `coef_matrix`, `random_effects`) that would surface any
latent panic if upstream ever returned a zero-dimension matrix. No action required from this phase
unless fdars-core is expected to return zero-row results under valid inputs.

---

_Reviewed: 2026-09-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
