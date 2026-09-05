---
phase: 69-frechet-regression-density-fda
reviewed: 2026-09-03T00:00:00Z
depth: deep
files_reviewed: 8
files_reviewed_list:
  - src/frechet_mod.rs
  - src/density_fda_mod.rs
  - src/convert.rs
  - src/pace_fpca_mod.rs
  - src/lib.rs
  - python/fdars/__init__.py
  - tests/test_frechet.py
  - tests/test_density_fda.py
  - tests/test_convert_ragged.py
findings:
  critical: 1
  warning: 3
  info: 3
  total: 7
status: issues_found
---

# Phase 69: Code Review Report

**Reviewed:** 2026-09-03
**Depth:** deep
**Files Reviewed:** 9 (including test_convert_ragged.py)
**Status:** issues_found

## Summary

Phase 69 delivers two new native submodules (`fdars.frechet`, `fdars.density_fda`) and the `extract_ragged_vecs` refactor from `pace_fpca_mod.rs` into `convert.rs`. The overall structure is solid: column-major flattening is correct, FRE-03 refactor is behaviorally equivalent, return types match the RESEARCH spec, and the monomorphized space dispatch includes the mandatory `Err` wildcard arm. However, one critical issue was found (a panic path in `flat_col_major_to_numpy2d` on adversarial input), plus three warnings (private-fn visibility inconsistency with CI impact, misleading k=0 error message, and an untested symmetry code path in correlation validation).

---

## Critical Issues

### CR-01: `flat_col_major_to_numpy2d` panics on mismatched `d` vs `result.len()`

**File:** `src/frechet_mod.rs:303-309`

**Issue:** `PyArray2::from_vec2(...).unwrap()` panics unconditionally if any row has a length that differs from the others. In `flat_col_major_to_numpy2d`, the outer iterator is `(0..d).map(|r| (0..d).map(|c| result[r + c * d]).collect())`. If `result.len()` is not `d*d` — which can happen if the upstream `frechet_mean` returns a `Vec<f64>` of unexpected length due to a future fdars-core change, or if `d` is misspecified versus the space's actual dimension — the inner index `result[r + c * d]` will panic with an out-of-bounds access *before* `from_vec2` can return `Err`. The upstream is expected to return a `Vec` of length `d*d` for SPD/correlation spaces, but there is no length assertion between `to_pyresult(...)` and the reshape, so any mismatch produces a Rust panic rather than a Python `ValueError`.

The identical pattern exists in `convert.rs:52-58` for `fdmatrix_to_numpy2d`, but that function asserts shape from the `FdMatrix` struct (which tracks its own dimensions), making it safer. Here, `result` is a raw `Vec<f64>` with no embedded dimension metadata.

**Fix:** Assert the length contract before indexing, converting a potential panic to a Python `ValueError`:

```rust
fn flat_col_major_to_numpy2d<'py>(
    py: Python<'py>,
    result: Vec<f64>,
    d: usize,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    if result.len() != d * d {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "frechet_mean: internal error — expected {d}*{d}={} elements from upstream, \
             got {}; check that d={d} matches the object dimension",
            d * d, result.len()
        )));
    }
    Ok(PyArray2::from_vec2(
        py,
        &(0..d)
            .map(|r| (0..d).map(|c| result[r + c * d]).collect())
            .collect::<Vec<_>>(),
    )
    .unwrap())  // safe: all rows have exactly d elements
}
```

Update the three call sites to propagate the `PyResult`:
```rust
Ok(flat_col_major_to_numpy2d(py, mean, d)?.into_any())
```

---

## Warnings

### WR-01: `density_fda_mod.rs` functions are private (`fn`) — inconsistent with project convention and potentially silently broken by future Rust linting

**File:** `src/density_fda_mod.rs:42,92,134,180,237`

**Issue:** Every `#[pyfunction]`-decorated function in `density_fda_mod.rs` is declared as `fn` (module-private), while every other module in the codebase declares them `pub fn`. The project convention documented in CLAUDE.md is explicit: "All public functions are `#[pyfunction]` macros; no private functions visible to Python." `wrap_pyfunction!` works on private fns in current PyO3 0.28, but:

1. This is a drift from the project convention that makes the module look incomplete.
2. A future PyO3 version or clippy lint could enforce `pub` for `#[pyfunction]`-decorated functions.
3. It will confuse any developer who compares `frechet_mod.rs` (uses `pub fn`) with `density_fda_mod.rs` (uses `fn`).

For comparison, the identical five-function structure in `frechet_mod.rs` uses `pub fn` throughout, as do all 20+ existing modules.

**Fix:** Add `pub` to all five function declarations:
```rust
pub fn normalize_density<'py>(...) { ... }
pub fn lqd_transform<'py>(...) { ... }
pub fn inverse_lqd<'py>(...) { ... }
pub fn wasserstein_barycenter<'py>(...) { ... }
pub fn lqd_fpca<'py>(...) { ... }
```

---

### WR-02: Symmetry validation for `space='correlation'` has zero test coverage

**File:** `src/frechet_mod.rs:451-458`, `tests/test_frechet.py`

**Issue:** `TestFrechetMeanCorrelation` tests `test_result_shape`, `test_result_unit_diagonal`, and `test_non_unit_diagonal_raises`, but there is no test for a non-symmetric correlation object. The symmetry check code at lines 451-458 is exercised only for the SPD space (via `test_non_symmetric_raises` in `TestFrechetMeanSpd`). The correlation symmetry path is a distinct code path in the `"correlation"` match arm and is completely untested.

A future refactor could accidentally remove the symmetry check from the correlation arm without any test failure, allowing non-symmetric inputs to silently reach `frechet_core::CorrelationMatrixSpace`.

**Fix:** Add a test to `TestFrechetMeanCorrelation`:
```python
def test_non_symmetric_raises(self):
    """A correlation object with M[i,j] != M[j,i] raises ValueError."""
    bad = _make_corr(_RNG2, D_COR).copy()
    bad[0, 1] += 0.5
    bad[1, 0] -= 0.5   # break symmetry while keeping diagonal at 1
    with pytest.raises(ValueError, match="symmetric"):
        frechet.frechet_mean([bad] + _OBJECTS_COR[1:], space="correlation", d=D_COR)
```

---

### WR-03: `frechet_anova` contiguity error message is misleading for empty `group_labels` input

**File:** `src/frechet_mod.rs:77-82`

**Issue:** When `group_labels` is an empty array (k=0), the error message reads:
```
"frechet_anova: group_labels must be contiguous integers starting at 0
 (i.e., 0, 1, …, 0); got labels []"
```
The phrase `0, 1, …, 0` is grammatically nonsensical. This is caused by `k.saturating_sub(1)` on `usize` — when `k=0`, saturating subtraction yields `0` instead of the intended `-1` (which is why saturating subtraction was used, but the result is still misleading). In practice, `k=0` means the `group_labels` array was empty, which can happen if the user accidentally passes an empty array.

The upstream will also raise `FdarError::InvalidParameter` for `n < 2` observations, so the user will eventually get *some* error, but the pre-validation message is confusing.

**Fix:** Add an explicit k=0 check with a targeted message:
```rust
if k == 0 {
    return Err(PyValueError::new_err(
        "frechet_anova: group_labels is empty — at least 2 groups required"
    ));
}
if !contiguous {
    return Err(PyValueError::new_err(format!(
        "frechet_anova: group_labels must be contiguous integers starting at 0 \
         (i.e., 0, 1, …, {}); got labels {sorted:?}",
        k - 1
    )));
}
```

---

## Info

### IN-01: Shared mutable `_RNG2` in `test_frechet.py` makes negative-path tests order-dependent

**File:** `tests/test_frechet.py:228,284,291,332`

**Issue:** `_RNG2 = np.random.default_rng(0)` is created at module scope and consumed both during module-level fixture construction (`_OBJECTS_SPD`, `_OBJECTS_SPH`, `_OBJECTS_COR`) and inside individual test methods (`test_non_symmetric_raises`, `test_non_positive_diagonal_raises`, `test_non_unit_diagonal_raises`). The "bad" objects generated in these tests draw from the advanced state of `_RNG2`, so their values change if pytest's execution order changes. The tests are currently robust because the perturbation applied (`bad[0,1] += 10.0`, `bad[0,0] = -1.0`) is extreme enough to guarantee the validation fires regardless of the base matrix. But this is fragile by design.

**Fix:** Use a fresh, isolated `np.random.default_rng(seed)` inside each negative-path test method, or use a fixed `np.eye(d)` as the base "bad" object.

---

### IN-02: `frechet_mean` lacks empty-object-list and `d=0` input validation at the binding level

**File:** `src/frechet_mod.rs:349-477`

**Issue:** Passing `objects=[]` (empty list) or `d=0` reaches `fdars_core::frechet::frechet_mean` with no binding-level guard. If fdars-core does not validate these (e.g., panics on empty slice or zero-size space construction), the result is an uncontrolled Rust panic rather than a Python `ValueError`. Passing `d=0` to `SpdMatrixSpace::new(0, Frobenius)` would construct a zero-dimensional space — behavior is upstream-defined and unspecified in the RESEARCH.

**Fix:** Add explicit guards before the match dispatch:
```rust
if objects.is_empty() {
    return Err(PyValueError::new_err(
        "frechet_mean: objects list must contain at least 1 object"
    ));
}
if d == 0 {
    return Err(PyValueError::new_err(
        "frechet_mean: d must be at least 1"
    ));
}
```

---

### IN-03: `frechet_anova` contiguity pre-validation redundantly re-implements upstream logic, but without a test for wrong `group_labels` length

**File:** `tests/test_frechet.py`, `src/frechet_mod.rs:69-83`

**Issue:** The binding correctly pre-validates label contiguity (Pitfall 4). However, there is no test covering `group_labels.shape[0] != responses.shape[0]` (length mismatch). This is handled by the upstream (`validate_reg_input` raises `FdarError::InvalidDimension`), but since the contiguity error is tested as binding-level behavior, the length mismatch should also be tested to confirm upstream validation propagates correctly.

**Fix:** Add to `TestFrechetAnova`:
```python
def test_wrong_label_length_raises(self):
    """group_labels length != n_obs raises ValueError."""
    short_labels = _GROUP_LABELS[:-5]  # 35 labels for 40 observations
    with pytest.raises(ValueError):
        frechet.frechet_anova(_RESPONSES, _ARGVALS, short_labels)
```

---

## FRE-03 Refactor Equivalence Verdict

**PASS.** `extract_ragged_vecs` in `convert.rs:108-138` is behaviorally identical to the original `extract_list_of_vecs` from `pace_fpca_mod.rs`. The only change is the added `caller_name: &str` parameter used exclusively in the error message format string. Both `pace_fpca_mod.rs` call sites have been correctly rewired to `crate::convert::extract_ragged_vecs(av_list, "irreg_fdata_from_lists")?` and `crate::convert::extract_ragged_vecs(vl_list, "irreg_fdata_from_lists")?`. The unused `PyTuple` import was removed from `pace_fpca_mod.rs` and added to `convert.rs`. No logic drift detected.

## Column-Major Flattening Verdict

**PASS — with caveat CR-01.** The flattening in `spd_object_from_numpy` and `corr_object_from_numpy` correctly stores `flat[r + c * d] = a[[r, c]]` (column-major: column c, row r → index r + c*d). The inverse reshape in `flat_col_major_to_numpy2d` correctly reconstructs row r as `(0..d).map(|c| result[r + c*d])`. For symmetric matrices (SPD, correlation), row-major vs column-major flattening produces the SAME flat vector, so a row/col mixup would not corrupt the result for these specific spaces. However, the implementation is still correctly column-major as required by fdars-core, regardless of the symmetry accident.

## Return Type Audit

| Function | Expected | Actual | Status |
|---|---|---|---|
| `normalize_density` | naked 1D array | `vec_to_numpy1d` → naked 1D | PASS |
| `lqd_transform` | naked 1D array | `vec_to_numpy1d` → naked 1D | PASS |
| `inverse_lqd` | naked 1D array | `vec_to_numpy1d` → naked 1D | PASS |
| `wasserstein_barycenter` | naked 1D array | `vec_to_numpy1d` → naked 1D | PASS |
| `lqd_fpca` | 6-key PyDict | 6 keys: mean, singular_values, loadings, scores, fve, ncomp | PASS |
| `frechet_global_reg` | 3-key PyDict | 3 keys: predicted, xout, x_bar | PASS |
| `frechet_local_reg` | 3-key PyDict | 3 keys: predicted, xout, bandwidth | PASS |
| `frechet_anova` | 9-key PyDict | 9 keys match RESEARCH §4 | PASS |
| `frechet_mean(space='spd')` | (d,d) numpy 2D | `flat_col_major_to_numpy2d` → 2D | PASS (modulo CR-01) |
| `frechet_mean(space='spherical')` | (d,) numpy 1D | `vec_to_numpy1d` → 1D | PASS |
| `frechet_mean(space='correlation')` | (d,d) numpy 2D | `flat_col_major_to_numpy2d` → 2D | PASS (modulo CR-01) |

Note: `lqd_fpca` correctly exposes `rotation` as `"loadings"` (not `"rotation"`) per the RESEARCH §7 convention, and correctly omits `centered` and `weights` (internal SVD state).

## Registration Verdict

**PASS.** Both `frechet_mod` and `density_fda_mod` are declared in `src/lib.rs` (lines 32-33) and registered via `register_submodule!` (lines 69-70). Both names are present in `python/fdars/__init__.py`'s `_submodule_names` tuple (lines 62-63). The module docstring was updated. The FND-02 guard (subset+registration invariant) is automatically satisfied.

---

_Reviewed: 2026-09-03_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
