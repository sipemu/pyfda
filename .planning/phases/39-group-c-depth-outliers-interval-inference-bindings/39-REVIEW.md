---
phase: 39-group-c-depth-outliers-interval-inference-bindings
reviewed: 2026-08-21T10:00:00Z
depth: deep
files_reviewed: 6
files_reviewed_list:
  - src/depth_mod.rs
  - src/outliers_mod.rs
  - src/inference_mod.rs
  - tests/test_depth.py
  - tests/test_outliers.py
  - tests/test_inference.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 39: Code Review Report

**Reviewed:** 2026-08-21T10:00:00Z
**Depth:** deep
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Phase 39 adds 9 new `DepthMethod` arms to `depth_method_from_str`, four new outlier-detection bindings (`tvdmss`, `muod`, `sequential_transform_outliers`, `depthgram`) with their converters and `SeqTransform` string dispatcher, and three ITP bindings (`itp_one_pop`, `itp_two_pop`, `itp_flm`) with `itp_result_to_pydict` and `basis_type_from_str`/`basis_type_variant_str` helpers.

The core implementation is correct and clean. No panics, no `.unwrap()`/`.expect()` in new code. All fallible calls go through `to_pyresult()`. All `#[non_exhaustive]` result structs are accessed field-by-field (never struct-literal matched). All dispatch functions carry the required wildcard arm. Converter key names match the authoritative `#[non_exhaustive]` struct field names exactly. The `mu0: Option<PyReadonlyArray1>` → `Option<Vec<f64>>` → `mu0_vec.as_deref()` chain is lifetime-sound. The `seq_transform_to_pydict` tuple-destructuring pattern correctly serialises `Vec<(SeqTransform, Vec<usize>)>` to `list[dict]`. All 13 depth tokens, all 4 outlier functions, and all 3 ITP functions are correctly registered. `fdars_core::ProjectionBasisType` and `fdars_core::inference::itp_*` are used at the correct re-exported crate-root / inference module paths.

Two warnings affect test coverage: missing degenerate-input guards for `tvdmss` and `depthgram`, and the ITP seed-contract test is weaker than the existing precedent. Three info items cover a missing `mu0` non-None test, a missing `itp_one_pop`/`itp_flm` determinism test, and one minor code-quality note.

## Warnings

### WR-01: `tvdmss` and `depthgram` lack degenerate-input tests (minimum-n guards untested)

**File:** `tests/test_outliers.py`
**Issue:** The research doc specifies `tvdmss` requires `n >= 3` and `depthgram` requires `n >= 2`, with both raising `FdarError::InvalidDimension` (surfaced as `ValueError`) when violated. `TestMuod` includes `test_muod_degenerate` (n=2, expects `ValueError`), setting the pattern. `TestTvdMss` and `TestDepthgram` have no equivalent. This creates an untested gap in the published ASVS V5 input-validation surface: if fdars-core ever changes its guard thresholds, nothing will catch the regression.

**Fix:** Add two tests to `tests/test_outliers.py`:
```python
# In TestTvdMss
def test_tvdmss_degenerate_n_too_small(self):
    """tvdmss raises ValueError when n < 3 (below core minimum)."""
    data = np.zeros((2, 30))
    with pytest.raises(ValueError):
        outl.tvdmss(data)

# In TestDepthgram
def test_depthgram_degenerate_n_too_small(self):
    """depthgram raises ValueError when n < 2 (below core minimum)."""
    data = np.zeros((1, 30))
    with pytest.raises(ValueError):
        outl.depthgram(data)
```

---

### WR-02: ITP seed-contract test only verifies idempotency, not the `seed=None → 0` equivalence

**File:** `tests/test_inference.py:817-831`
**Issue:** `test_itp_two_pop_determinism` calls `itp_two_pop` twice with `seed=None` and asserts the results are byte-identical. This proves idempotency but does **not** verify the documented contract "seed=None resolves to fixed default 0". If the implementation were changed to use `seed.unwrap_or(99)` instead of `seed.unwrap_or(0)`, the test would still pass. The parallel tests for `t_perm_test` (`test_seed_none_equals_seed_zero`, line 110) and `f_perm_test` (`test_seed_none_equals_seed_zero`, line 178) correctly test the `seed=None == seed=0` equivalence. The ITP binding uses `seed.unwrap_or(0)` (line 653 in `inference_mod.rs`) which is correct — but this is untested for ITP. The research doc requires: `seed=None` → fixed default → `itp_one_pop` and `itp_two_pop` produce byte-identical results to explicit `seed=0`.

**Fix:** Replace or supplement `test_itp_two_pop_determinism` with:
```python
def test_itp_two_pop_seed_none_equals_seed_zero(self):
    """Documented contract: seed=None resolves to seed=0 for itp_two_pop."""
    import fdars.inference as inf
    rng = np.random.default_rng(11)
    a = rng.standard_normal((15, 24))
    b = rng.standard_normal((15, 24)) + 0.5
    argvals = np.linspace(0, 1, 24)
    r_none = inf.itp_two_pop(a, b, argvals, n_perm=49)
    r_zero = inf.itp_two_pop(a, b, argvals, n_perm=49, seed=0)
    assert np.array_equal(r_none["adjusted_pvalues"], r_zero["adjusted_pvalues"]), (
        "seed=None must equal seed=0 (documented contract)"
    )
```

---

## Info

### IN-01: `itp_one_pop` `mu0` non-None path is untested

**File:** `tests/test_inference.py:731-779`
**Issue:** `TestItpOnePop` contains three tests (smoke, fourier dispatch, invalid basis). None passes a non-`None` `mu0` array. The `mu0` parameter exercises distinct code in `itp_one_pop` (`let mu0_vec = mu0.map(|a| numpy1d_to_vec(a)); ... mu0_vec.as_deref()`). A test with a non-zero null mean would close this gap and confirm the owned-`Vec` → `as_deref()` conversion reaches core correctly.

**Fix:** Add to `TestItpOnePop`:
```python
def test_itp_one_pop_with_mu0(self):
    """itp_one_pop accepts a non-None mu0 null mean without error."""
    import fdars.inference as inf
    rng = np.random.default_rng(4)
    data = rng.standard_normal((20, 24))
    argvals = np.linspace(0, 1, 24)
    mu0 = np.zeros(24)
    result = inf.itp_one_pop(data, argvals, mu0=mu0, n_perm=49)
    assert isinstance(result["adjusted_pvalues"], np.ndarray)
    assert result["adjusted_pvalues"].shape == (result["n_basis"],)
```

---

### IN-02: `itp_one_pop` and `itp_flm` lack any determinism test

**File:** `tests/test_inference.py`
**Issue:** `itp_two_pop` has `test_itp_two_pop_determinism`. `itp_one_pop` and `itp_flm` have no equivalent — all three bindings use `seed.unwrap_or(0)` and are documented as deterministic. The gap means a future refactor that accidentally removes seed forwarding for these two functions would not be caught.

**Fix:** Add to `TestItpOnePop` and `TestItpFlm`:
```python
# TestItpOnePop
def test_itp_one_pop_determinism(self):
    """Two calls with seed=None produce byte-identical results."""
    import fdars.inference as inf
    rng = np.random.default_rng(5)
    data = rng.standard_normal((20, 24))
    argvals = np.linspace(0, 1, 24)
    r1 = inf.itp_one_pop(data, argvals, n_perm=49)
    r2 = inf.itp_one_pop(data, argvals, n_perm=49)
    assert np.array_equal(r1["adjusted_pvalues"], r2["adjusted_pvalues"])

# TestItpFlm (same pattern with data/y/argvals)
```

---

### IN-03: `sequential_transform_outliers` error message verifies offending token but not valid token list

**File:** `tests/test_outliers.py:100-105`
**Issue:** `test_seqtransform_bad_transform` uses `match="nope"` which confirms the offending token is echoed in the error, but does not verify the list of valid tokens (`t0`, `t1`, `t2`, `d1`, `d2`) is present. This is lower priority than WR-01/WR-02 but mirrors the stronger contract test in `test_depth.py::test_unknown_method_lists_new_tokens` which uses `match="total_variation"` to verify the updated error message lists new tokens.

**Fix:** Optionally add `match="t0"` (or similar valid-token reference) alongside `match="nope"` to prove the error lists all five valid transforms — consistent with the depth test pattern.

---

_Reviewed: 2026-08-21T10:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
