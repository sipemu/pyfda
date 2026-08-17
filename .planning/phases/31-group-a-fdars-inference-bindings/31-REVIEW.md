---
phase: 31-group-a-fdars-inference-bindings
reviewed: 2026-08-17T18:15:55Z
depth: deep
files_reviewed: 4
files_reviewed_list:
  - src/inference_mod.rs
  - src/lib.rs
  - python/fdars/__init__.py
  - tests/test_inference.py
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: resolved
---

# Phase 31: Code Review Report

**Reviewed:** 2026-08-17T18:15:55Z
**Depth:** deep
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 31 adds the `fdars.inference` PyO3 submodule exposing eight inference functions
across three commit groups. The scaffold, registration, and `__init__.py` wiring are
correct and follow established conventions. Error routing through `to_pyresult()` is
consistent — no `.unwrap()` or `.expect()` appears on any fallible path in the module
body. The `TestResult` and `ToleranceBand` structs are accessed field-by-field (no
struct-literal construction). The multiplier string-enum dispatch has the required
wildcard `PyValueError` arm. The FLM re-fit pattern correctly keeps `FregreLmResult`
internal and never crosses the Python boundary.

One correctness defect was found: negative integer group labels for
`oneway_anova_vstat` silently wrap to astronomically large `usize` values via
`numpy1d_to_usize_vec`, producing corrupted group assignments with no error raised at
the binding layer. Two documentation-level issues were identified. Test coverage for
`scb_two_sample_test` is thin relative to sibling test classes.

## Critical Issues

### CR-01: Negative group labels silently wrap to `usize::MAX` in `oneway_anova_vstat`

**File:** `src/inference_mod.rs:528` (and `src/convert.rs:72`)

**Issue:** `numpy1d_to_usize_vec` casts each `i64` element to `usize` with an
unchecked `x as usize`. In Rust this is defined behaviour — a negative value such as
`-1i64` becomes `usize::MAX` (18 446 744 073 709 551 615). A caller passing groups
`[-1, 0, 1]` would have the `-1` silently remapped to `usize::MAX`, which `fdars_core`
then treats as a valid (very large) group index. The core's two-distinct-groups
validation still passes (it sees `usize::MAX`, `0`, and `1` as three distinct values),
so no `ValueError` is raised. The resulting per-group statistics are computed on the
wrong partitioning — a silent data-corruption bug. The docstring reinforces the problem
by claiming "any distinct `int64` values define the groups", implying negative values
are safe.

This path cannot be defended by "the core validates it": the core receives `Vec<usize>`
and has no way to distinguish a legitimately large group index from a wrapped negative.

**Fix:** Add a binding-layer guard before calling `numpy1d_to_usize_vec`:

```rust
// src/inference_mod.rs — inside oneway_anova_vstat, before numpy1d_to_usize_vec
let raw = groups.as_array();
if raw.iter().any(|&x| x < 0) {
    return Err(PyValueError::new_err(
        "groups must contain non-negative integer labels; got at least one negative value",
    ));
}
let grp = raw.iter().map(|&x| x as usize).collect::<Vec<_>>();
```

Also update the docstring to state that negative labels raise `ValueError`:

```text
groups : numpy.ndarray
    1-D integer array of length ``n`` with non-negative 0-indexed group labels
    (dtype int64). Negative values raise ``ValueError``.
```

And add a test:

```python
def test_negative_group_label_raises_value_error(self, canadian_anova_fixture):
    X, _, grid = canadian_anova_fixture
    n = X.shape[0]
    bad_groups = np.array([-1] + [0] * (n - 1), dtype=np.int64)
    with pytest.raises(ValueError):
        oneway_anova_vstat(X, bad_groups, grid)
```

## Warnings

### WR-01: Module-level docstring falsely claims `seed=None -> 0` for all functions

**File:** `src/inference_mod.rs:14`

**Issue:** The module header states:
> `seed=None` resolves to fixed default `0` for byte-identical reproducibility across runs

`mean_scb` (line 274) and `scb_two_sample_test` (line 350) expose **no `seed`
parameter at all**. The claim as written implies those two functions are also
seed-controlled, which is false. Whether `fdars_core::inference::mean_scb` uses a
fixed internal seed or `thread_rng()` is not visible here, but the module doc is
incorrect for those functions regardless.

The test suite does not check determinism for `mean_scb` or `scb_two_sample_test`,
so a future reader relying on the doc's guarantee would have no safety net.

**Fix:** Scope the seed claim to only the functions that accept it:

```rust
//! `seed=None` resolves to fixed default `0` for [`t_perm_test`] and [`f_perm_test`],
//! giving byte-identical results across calls with the same inputs.
//! [`mean_scb`] and [`scb_two_sample_test`] use no external seed (the bootstrap
//! randomness is internal to fdars-core); call determinism for those functions
//! depends on fdars-core's internal seeding strategy.
```

If `fdars_core::inference::mean_scb` in fact accepts a seed argument that the binding
drops, that is also a defect — expose it and route `None -> 0` consistently with the
permutation tests.

### WR-02: `TestScbTwoSampleTest` is under-tested relative to sibling classes

**File:** `tests/test_inference.py:414`

**Issue:** `TestScbTwoSampleTest` has only three test methods (dict-key shape,
`n_perm==0`, bad-multiplier). Compare to sibling classes `TestTPerm` (7 tests) and
`TestMeanScb` (7 tests). Missing cases:

- No `test_p_value_in_range` — does not verify `0 <= p_value <= 1`.
- No `test_statistic_nonnegative` — does not verify the decision statistic is >= 0.
- No `test_values_plain_types` — does not guard against numpy-scalar leakage in the
  returned dict (the `json.dumps` pattern used elsewhere).
- No test for bandwidth <= 0 raising `ValueError` (although the binding delegates this
  to the core, the other bandwidth-consuming function `mean_scb` has this gap too).

The absence of these tests means a regression that returns, say, an f64 NaN or a numpy
scalar as `p_value` would not be caught.

**Fix:** Add the missing test methods:

```python
def test_p_value_in_range(self, growth_subsets):
    boys, girls, age = growth_subsets
    result = scb_two_sample_test(boys, girls, age, 5.0, nb=50)
    assert 0.0 <= result["p_value"] <= 1.0

def test_statistic_nonnegative(self, growth_subsets):
    boys, girls, age = growth_subsets
    result = scb_two_sample_test(boys, girls, age, 5.0, nb=50)
    assert result["statistic"] >= 0.0

def test_values_plain_types(self, growth_subsets):
    import json
    boys, girls, age = growth_subsets
    result = scb_two_sample_test(boys, girls, age, 5.0, nb=50)
    json.dumps(result, sort_keys=True)  # raises TypeError on numpy scalars
```

## Info

### IN-01: `n_perm` type is `usize` — Python callers cannot pass values > `i64::MAX`

**File:** `src/inference_mod.rs:89,149`

**Issue:** `n_perm` is typed as `usize` in the PyO3 signature. PyO3 maps `usize` to
a Python `int` with no upper-bound check beyond the platform native width. On 64-bit
Linux `usize::MAX == u64::MAX`, which is larger than `i64::MAX`. A Python caller
passing `n_perm=2**63` would receive an `OverflowError` from PyO3's coercion, which
is acceptable, but the error message ("can't convert negative int to unsigned") is
misleading for out-of-range positive integers. This is a minor UX rough edge rather
than a correctness defect; `u32` (max ~4 billion) would be a more natural cap and
give a cleaner error at unreachable values.

**Fix (optional):** Change `n_perm: usize` to `n_perm: u32` in the signature and
cast to `usize` inside: `n_perm as usize`. This also constrains the value more
tightly in the docstring.

---

_Reviewed: 2026-08-17T18:15:55Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
