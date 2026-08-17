---
phase: 32-group-b-depth-boxplot-bindings
reviewed: 2026-08-17T00:00:00Z
depth: deep
files_reviewed: 2
files_reviewed_list:
  - src/depth_mod.rs
  - tests/test_depth.py
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: resolved
resolved_note: WR-01/02/03 fixed in commit a33522d; IN-01 (docstring wording nit) deferred
---

# Phase 32: Code Review Report

**Reviewed:** 2026-08-17
**Depth:** deep
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Phase 32 adds `functional_depth` and `functional_boxplot` to `src/depth_mod.rs`, with two
internal helpers (`depth_method_from_str`, `boxplot_result_to_pydict`) and a new test file
`tests/test_depth.py`.

The binding structure is clean and follows every project convention correctly:

- `DepthMethod` and `FunctionalBoxplotResult` are accessed field-by-field — no struct-literal
  construction against `#[non_exhaustive]` types.
- The `_ =>` wildcard fallback in `depth_method_from_str` is present and produces a descriptive
  `PyValueError` that names the bad method string.
- `seed=None` resolves to `seed.unwrap_or(0)` — matches the Phase 31 seed contract and
  `random_projection_1d_seeded` delegates `Some(0)` to a deterministic `StdRng`, giving
  byte-identical results on repeated `seed=None` calls.
- The `usize as i64` cast on outlier indices (line 456) is safe: row indices are bounded by
  the matrix row count, which is a `usize` allocated in memory — values above `i64::MAX`
  (~9.2 × 10^18) are physically impossible. The pattern matches `convert.rs:77`
  (`usize_vec_to_numpy1d`), the project's established convention.
- `numpy2d_to_fdmatrix` correctly performs the row-major → column-major transpose before
  passing data to `fdars_core`; band fields emerge from the core in evaluation-point order
  (length `m`), `depths` in curve order (length `n`). No transposition error.
- All error paths route through `to_pyresult()`; no `.unwrap()` or `.expect()` on fallible
  paths in the new code.

Three warnings and one info item follow.

---

## Warnings

### WR-01: `let m` shadows the conventional column-count meaning in `depth_method_from_str` calls

**File:** `src/depth_mod.rs:512` and `src/depth_mod.rs:577`

**Issue:** Throughout `depth_mod.rs`, the binding `let m = d.ncols()` is the canonical idiom
for "number of evaluation points" (see line 390, `random_projection_deriv_1d`). In
`functional_depth` (line 512) and `functional_boxplot` (line 577), `m` is instead bound to
the `DepthMethod` enum value returned by `depth_method_from_str`. The two bindings never
co-exist in the same scope, so there is no actual bug — but anyone reading line 512 in context
will expect `m` to be a `usize`, not a `DepthMethod`, increasing maintenance risk.

**Fix:** Rename to `depth_method` (or `dm`) to match the parameter and type semantics:

```rust
// functional_depth, line 512
let depth_method = depth_method_from_str(method, scale, nproj, seed)?;
let result = to_pyresult(fdars_core::depth::functional_depth(&d, depth_method))?;

// functional_boxplot, line 577
let depth_method = depth_method_from_str(method, scale, nproj, seed)?;
let result = to_pyresult(fdars_core::depth::functional_boxplot(&d, depth_method, factor))?;
```

---

### WR-02: `functional_boxplot` unknown-method test does not verify error message content

**File:** `tests/test_depth.py:257–261`

**Issue:** `TestFunctionalBoxplotValueErrors.test_unknown_method_raises` only asserts that a
`ValueError` is raised — it does not check that the error message names the bad method string.
The parallel test for `functional_depth` (line 127) correctly uses `match="not_a_method"`.
Without a `match=` parameter, any `ValueError` from any code path (e.g. an empty-data check
before the method dispatch) would satisfy the assertion, making the test weaker than intended.

**Fix:**

```python
def test_unknown_method_raises(self, cw_temp):
    import fdars.depth

    with pytest.raises(ValueError, match="not_a_method"):
        fdars.depth.functional_boxplot(cw_temp, method="not_a_method", factor=1.5)
```

---

### WR-03: No test verifies that `seed=None` and `seed=0` produce byte-identical results

**File:** `tests/test_depth.py` (gap — no line covers this)

**Issue:** The code comment (line 411) and both docstrings explicitly state the contract:
`seed=None` resolves to `0`, giving byte-identical results across calls. `TestFunctionalDepthDeterminism.test_seed_none_determinism` (line 111) only checks that two
`seed=None` calls match each other — it does not verify the documented fixed-value mapping.
If the default were changed from `0` to, say, `42`, `test_seed_none_determinism` would still
pass, silently breaking the documented API contract.

The same gap exists for `functional_boxplot`: no `seed=None` determinism test is present at
all in `TestFunctionalBoxplotValueErrors` or elsewhere.

**Fix:** Add two assertions:

```python
def test_seed_none_equals_seed_zero(self, cw_temp):
    """Documented contract: seed=None resolves to seed=0."""
    import fdars.depth

    X = cw_temp
    d_none = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=None)
    d_zero = fdars.depth.functional_depth(X, method="random_projection", nproj=20, seed=0)
    assert np.array_equal(d_none, d_zero), "seed=None must equal seed=0 (documented contract)"

def test_boxplot_seed_none_determinism(self, cw_temp):
    import fdars.depth

    X = cw_temp
    r1 = fdars.depth.functional_boxplot(X, method="random_projection", factor=1.5, nproj=20, seed=None)
    r2 = fdars.depth.functional_boxplot(X, method="random_projection", factor=1.5, nproj=20, seed=None)
    assert np.array_equal(r1["depths"], r2["depths"]), "seed=None boxplot must be deterministic"
```

---

## Info

### IN-01: `scale` parameter description wording differs between the two new functions

**File:** `src/depth_mod.rs:480` (`functional_depth`) and `src/depth_mod.rs:537` (`functional_boxplot`)

**Issue:** `functional_depth` documents `scale` as "Applies only to `fraiman_muniz`"; `functional_boxplot` documents it as "Passed to `fraiman_muniz`". Both mean the same thing, but consistency across sibling functions reduces confusion when the docstrings are rendered side-by-side in MkDocs.

**Fix:** Use identical wording in both docstrings:

```
scale : bool, optional
    Applies only to ``"fraiman_muniz"``: whether to scale depths to
    ``2·min(Fn, 1-Fn)`` form (default ``True``). Ignored for all other methods.
```

---

_Reviewed: 2026-08-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
