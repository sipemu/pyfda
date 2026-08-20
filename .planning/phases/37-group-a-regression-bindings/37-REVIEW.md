---
phase: 37-group-a-regression-bindings
reviewed: 2026-08-20T00:00:00Z
depth: deep
files_reviewed: 2
files_reviewed_list:
  - src/regression_mod.rs
  - tests/test_regression.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 37: Code Review Report

**Reviewed:** 2026-08-20
**Depth:** deep
**Files Reviewed:** 2 (`src/regression_mod.rs`, `tests/test_regression.py`)
**Status:** issues_found

## Summary

Phase 37 adds two PyO3 bindings — `concurrent_regression` and `functional_glm` — to `src/regression_mod.rs`, plus a new test file `tests/test_regression.py`. The core implementation is structurally sound: field names match the authoritative v0.23.0 signatures, the `#[non_exhaustive]` wildcard arms are present in both `family_from_str` and the reverse family match, `r.fpca` is correctly excluded from the dict, `beta_curve` is faithfully converted as `(p, m)` via `fdmatrix_to_numpy2d`, `functional_glm` has no `argvals` parameter (correct per core API), and all fallible paths route through `to_pyresult()` with no `.unwrap()`/`.expect()` in the new code.

Three warnings and two info items require attention. The most actionable is a wrong key-count claim ("14 keys") appearing in both the code comment and a test docstring when 15 keys are actually inserted — this is an off-by-one in documentation that will confuse anyone maintaining this code. A test coverage gap in the smoke test and a potential test-stability concern around the binomial family fixture round out the warnings.

No blocking correctness, security, or data-loss issues were found.

---

## Warnings

### WR-01: Code comment and test docstring both claim "14 keys" but 15 keys are inserted

**File:** `src/regression_mod.rs:1083-1086` and `tests/test_regression.py:139`

**Issue:** The block comment above `functional_glm_result_to_pydict` reads:

```
// 14 keys are exposed; r.fpca is intentionally NOT inserted
```

The actual code inserts 15 keys: `intercept`, `beta_t`, `beta_se`, `gamma`, `fitted_values`, `linear_predictors`, `ncomp`, `coefficients`, `std_errors`, `log_likelihood`, `deviance`, `iterations`, `aic`, `bic`, `family`. The count is 15, not 14 — consistent with the authoritative RESEARCH table (which also says "14 keys" in its heading but lists 15 rows).

The test docstring repeats the error: `"""Gaussian family: 14 keys, no fpca, finite fitted_values, family round-trip."""` while the `expected_keys` set below it has 15 members. The test assertion is correct (15 keys), but the docstring will mislead maintainers.

The root cause is that `family` was added as a 15th key (correct per RESEARCH table and struct) but the "14 keys" heading was never updated.

**Fix:**

```rust
// src/regression_mod.rs — update the block comment:
// 15 keys are exposed; r.fpca is intentionally NOT inserted — the embedded
// FpcaResult is consumed internally for fit only (mirrors flm_f_test pattern).
```

```python
# tests/test_regression.py:139 — update docstring:
"""Gaussian family: 15 keys, no fpca, finite fitted_values, family round-trip."""
```

---

### WR-02: `test_smoke` for `concurrent_regression` does not assert output shapes beyond `fitted`

**File:** `tests/test_regression.py:35-54`

**Issue:** `test_smoke` (p=1 single-predictor) verifies the five dict keys are present and `fitted.shape == (n, m)`, but does not assert:
- `result["beta_curve"].shape == (1, m)` — for p=1 the shape `(1, m)` is ambiguous (indistinguishable from `(m, 1)` being unreported), but the absence of any shape check means a silent `(m, 1)` return would not be caught here.
- `result["intercept"].shape == (m,)` — unchecked; a scalar intercept or wrong-dimension array would pass.
- `result["argvals"].shape == (m,)` — unchecked.

The transposition guard in `test_beta_curve_shape_p3` (p=3, n=10) covers the critical ambiguity for the multi-predictor case, but the smoke test adds no value for shape sanity of the other three output arrays.

**Fix:**

```python
def test_smoke(self):
    n, m = 8, 12
    response, predictors = self._make_data(n=n, m=m, p=1)
    result = regression.concurrent_regression(
        predictors, response, argvals=None, bandwidth=0.2, kernel="gaussian"
    )
    assert set(result.keys()) == {
        "beta_curve", "intercept", "fitted", "residuals", "argvals",
    }
    assert result["fitted"].shape == (n, m)
    assert result["beta_curve"].shape == (1, m)   # p=1 predictor, m grid points
    assert result["intercept"].shape == (m,)
    assert result["argvals"].shape == (m,)
    assert result["residuals"].shape == (n, m)
```

---

### WR-03: `test_binomial_family` uses uncorrelated data and response with the same seed for both

**File:** `tests/test_regression.py:169-187`

**Issue:** The binomial test builds functional data with `seed=1` and then creates a fresh `rng = np.random.default_rng(1)` — the same seed — for shuffling the response labels. Because both generators start at the same state, the shuffle sequence may accidentally have partial correlation with the data generation sequence, producing subtly dependent data/label pairs. This is not intentional. More critically, the test asserts `np.all(fv > 0) and np.all(fv < 1)` without allowing for the case where the IRLS converges to a degenerate intercept-only solution with `fv ≈ 0.5 ± epsilon` but some values land on the boundary — this assertion is actually fine for logit-link (sigmoid maps all reals to open interval), but the fixture relies on core IRLS converging without checking `result["iterations"] < max_iter` (non-convergence would not fail the test).

**Fix:** Use a different seed for response generation to avoid the identical-seed coincidence, and optionally assert that IRLS converged:

```python
def test_binomial_family(self):
    n, m = 30, 16
    data, _ = self._make_data(n=n, m=m, seed=1)
    rng = np.random.default_rng(99)   # different seed from data generation
    response = np.array([0.0] * (n // 2) + [1.0] * (n - n // 2))
    rng.shuffle(response)
    result = regression.functional_glm(
        data, response, family="binomial", n_comp=3, max_iter=50
    )
    fv = result["fitted_values"]
    assert np.all(np.isfinite(fv)), "fitted_values must be finite"
    assert np.all(fv > 0) and np.all(fv < 1), (
        f"Binomial fitted_values must be in (0, 1), got min={fv.min():.4f} max={fv.max():.4f}"
    )
    assert result["family"] == "binomial"
    assert result["iterations"] <= 50, "IRLS should converge within max_iter"
```

---

## Info

### IN-01: `n_comp` (input parameter) vs `"ncomp"` (dict key) naming asymmetry is undocumented

**File:** `src/regression_mod.rs:1171` and `1105`

**Issue:** `functional_glm` accepts `n_comp: usize` as the Python parameter name (consistent with all other functions in the module) but inserts the result as `"ncomp"` in the returned dict (matching the Rust struct field `r.ncomp`). The Python API therefore has an asymmetry: you pass `n_comp=3` and read back `result["ncomp"]`. This pattern already exists in the codebase (e.g., `model_selection_ncomp` returns `"best_ncomp"`) but is not noted in the docstring.

**Fix:** Add a line to the Returns docstring noting the asymmetry:

```rust
/// Returns
/// -------
/// dict
///     intercept, beta_t (m,), beta_se (m,), gamma (q,), fitted_values (n,),
///     linear_predictors (n,), ncomp (note: input param is ``n_comp``), ...
```

---

### IN-02: `fdmatrix_to_numpy2d` in `convert.rs` contains an `.unwrap()` called by new code

**File:** `src/convert.rs:57`

**Issue:** `fdmatrix_to_numpy2d` uses `.unwrap()` on `PyArray2::from_vec2(...)`. This pre-existing pattern is called by both new converter functions (`concurrent_regr_result_to_pydict` and `functional_glm_result_to_pydict`) via `fdmatrix_to_numpy2d(py, &r.beta_curve)` etc. In practice the unwrap cannot panic because `from_vec2` only fails on ragged inner vecs, and the row slices are always exactly `ncols` elements. However, the project convention (CLAUDE.md) is "no `.unwrap()`", and the new phase's code paths now exercise this pre-existing violation more broadly.

This is pre-existing code, not introduced in Phase 37, but the review scope includes functions called by the new bindings.

**Fix:** Track as a pre-existing tech debt item; convert `fdmatrix_to_numpy2d` to return `PyResult<Bound<'py, PyArray2<f64>>>` and propagate with `?` in a follow-up cleanup phase. No immediate action required for Phase 37 correctness.

---

_Reviewed: 2026-08-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
