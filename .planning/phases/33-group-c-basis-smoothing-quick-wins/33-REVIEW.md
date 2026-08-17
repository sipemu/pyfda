---
phase: 33-group-c-basis-smoothing-quick-wins
reviewed: 2026-08-17T19:13:58Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - src/basis_mod.rs
  - src/smoothing_mod.rs
  - tests/test_basis_smoothing.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: resolved
---

# Phase 33: Code Review Report

**Reviewed:** 2026-08-17T19:13:58Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Three commits reviewed covering the AIC quick-wins: `optim_bandwidth` criterion dispatch and output arm (`src/smoothing_mod.rs`), `constant_basis` and `smooth_basis_aic` additions (`src/basis_mod.rs`), and the new test module (`tests/test_basis_smoothing.py`).

The implementations are structurally sound. `smooth_basis_aic` is a faithful copy of `smooth_basis_gcv`: every PyDict field is present and in the same order (`fitted`, `coefficients`, `edf`, `gcv`, `aic`, `bic`, `nbasis`), the `Option<_> => PyValueError` error path is preserved identically, and no `.unwrap()` was introduced. `constant_basis` is correct: `vec_to_numpy1d` is used, the function delegates entirely to `fdars_core::basis::constant_basis`, and the empty-input case is safe by construction. The output `crit_str` match in `optim_bandwidth` now covers `Cv`, `Gcv`, and `Aic` explicitly and retains the required `_ => "unknown"` wildcard — mandatory because `CvCriterion` is `#[non_exhaustive]` in fdars-core 0.20. The input dispatch correctly raises `ValueError` for unknown strings.

One test-coverage gap and one documentation inaccuracy are reported below.

## Warnings

### WR-01: `criterion="cv"` path has no non-regression test

**File:** `tests/test_basis_smoothing.py:35-43`
**Issue:** The Phase 33 test suite adds a GCV non-regression guard (`test_optim_bandwidth_gcv_unchanged`) but omits the equivalent guard for `criterion="cv"`. The `"cv"` dispatch arm in `optim_bandwidth` was present before Phase 33 and was not structurally touched, but the new match arm for `"aic"` sits immediately above the `"cv"` arm in the input match and immediately below it in the output match. Any future reordering or merge error would silently swap `Cv` and `Aic` in one of the two match arms without a red test. A one-liner non-regression test (analogous to `test_optim_bandwidth_gcv_unchanged`) would close this gap.

**Fix:**
```python
def test_optim_bandwidth_cv_unchanged():
    """CV path still returns criterion == 'cv' (non-regression)."""
    import fdars.smoothing as sm
    x, y = _make_signal()
    result = sm.optim_bandwidth(x, y, criterion="cv", n_grid=15)
    assert result["criterion"] == "cv"
    assert math.isfinite(result["h_opt"]) and result["h_opt"] > 0
```

## Info

### IN-01: `smooth_basis_aic` docstring omits that `gcv` in the output dict is the GCV score at the AIC-optimal lambda

**File:** `src/basis_mod.rs:447-448`
**Issue:** The Returns docstring reads `edf, gcv, aic, bic, nbasis` without clarifying that `gcv` is the GCV score evaluated at the AIC-optimal lambda (not the criterion used for selection). A caller who only reads the function name and the docstring may be surprised to find a `gcv` key in the result of an AIC function and wonder if the key is a copy-paste error. `smooth_basis_gcv` has the same keys — both functions return all four criterion scores from `SmoothBasisResult` — so this is intentional, but unstated.

**Fix:** Add a clarifying sentence in the Returns block:

```text
/// Returns
/// -------
/// dict
///     Dictionary with keys: fitted (n, m), coefficients (n, nbasis),
///     edf, gcv, aic, bic, nbasis.
///     All criterion scores (gcv, aic, bic) are evaluated at the
///     AIC-optimal lambda; the penalty was selected by minimising aic.
```

---

_Reviewed: 2026-08-17T19:13:58Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
