---
phase: 70-multi-domain-data-famm-advanced-clustering
reviewed: 2026-09-04T00:00:00Z
depth: deep
files_reviewed: 10
files_reviewed_list:
  - src/multi_fdata_mod.rs
  - src/famm_mod.rs
  - src/spm_mod.rs
  - src/clustering_mod.rs
  - src/lib.rs
  - python/fdars/__init__.py
  - tests/test_multi_fdata.py
  - tests/test_famm.py
  - tests/test_spm_mfpca.py
  - tests/test_clustering_advanced.py
findings:
  critical: 0
  warning: 1
  info: 5
  total: 6
status: issues_found
---

# Phase 70: Code Review Report

**Reviewed:** 2026-09-04
**Depth:** deep
**Files Reviewed:** 10
**Status:** issues_found — 1 Warning, 5 Info

## Summary

Phase 70 introduces `PyMultiFunData` (new opaque `#[pyclass]` handle), two new
submodules (`fdars.multi_fdata`, `fdars.famm`), and extensions to `fdars.spm`
(`mfpca`, `spe_multivariate`) and `fdars.clustering` (four advanced algorithms).
The core implementation is correct: transposition is handled uniformly via
`numpy2d_to_fdmatrix`; all `#[non_exhaustive]` configs use the `Default::default()` +
mutation pattern; the `Vec<FdMatrix> → Vec<&FdMatrix>` borrow ordering is sound in all
three call sites; `spe_multivariate`'s `Vec<Vec<f64>> → Vec<&[f64]>` lifetime ordering
is correct; `MfpcaResult`'s `pub(super)` fields are not accessed; DBSCAN's
`Vec<Option<usize>>` is mapped to `i64` (None → −1, Some(c) → c as i64) via
`into_pyarray` rather than `usize_vec_to_numpy1d`; and all non-square fixtures (20×30,
20×25) are in place. All four new clustering functions use `usize_vec_to_numpy1d` for
`Vec<usize>` cluster fields, consistent with the existing codebase.

One Warning is raised: the `test_dbscan_fd` test does not include an explicit
assertion that at least one noise point (−1 label) appears, leaving the
`None → −1i64` encoding branch asserted only by transitivity under the specific
fixture's geometry rather than by direct contract. Five Info items note the module
docstring omission, a minor loop-variable name choice, missing `Raises` sections in
four new binding docs, and two test-coverage gaps in the guard tests.

---

## Warnings

### WR-01: `test_dbscan_fd` does not assert that noise encoding (−1) is exercised

**File:** `tests/test_clustering_advanced.py:28-46`

**Issue:** The test checks `labels.dtype == np.int64` and the consistency invariant
`result["n_noise"] == int(np.sum(labels == -1))`, but never asserts `result["n_noise"] > 0`
or `-1 in labels`. The research spec (section 8, Validation table) explicitly requires
"Test asserts a -1 appears for noise." If the fixture ever produces zero noise points
(e.g. after a data-generation change or eps bump), the `None → -1i64` encoding path
goes unexercised and the test still passes. With `eps=0.5` on random standard-normal
data in 30 dimensions (L2 distance ≈ 7–10 >> 0.5) the fixture does produce all-noise
output in practice, but that is a statistical guarantee, not a coded assertion.

**Fix:** Add one explicit line immediately after the consistency check:

```python
# Explicitly assert the None→-1 encoding path fires for this fixture.
assert result["n_noise"] > 0, (
    "Expected at least one noise point with eps=0.5 on 30-dimensional random data"
)
```

---

## Info

### IN-01: Module docstring does not mention the two new submodules

**File:** `python/fdars/__init__.py:1-26`

**Issue:** The package-level docstring was not extended to mention
`multi_fdata` (multi-domain container) or `famm` (functional additive mixed
models), even though every prior phase added its capabilities to the bullet list.
Stale docstrings mislead users browsing `help(fdars)`.

**Fix:** Add two bullets after the `density_fda` line:

```python
# - Multi-domain data (multi_fdata) — PyMultiFunData handle for multi-domain functional data
# - Functional Additive Mixed Models (famm) — dense_flmm, fast_fmm, multi_famm
```

### IN-02: Loop variable `m` in `mfpca` shadows the conventional module-parameter name

**File:** `src/spm_mod.rs:932`

**Issue:** `for m in result.means` uses `m` as a loop variable. In PyO3 code the
letter `m` is universally the `&Bound<'_, PyModule>` parameter in `register` functions.
Although there is no shadowing here (the function signature is `py, variables, ncomp,
weighted` — no `m`), the single-letter name creates momentary confusion when scanning
the file. No compile-time or runtime impact.

**Fix:** Rename the loop variable to something unambiguous:

```rust
for mean_vec in result.means {
    means_list.append(vec_to_numpy1d(py, mean_vec))?;
}
```

### IN-03: Four new clustering bindings missing `Raises` docstring section

**File:** `src/clustering_mod.rs:289-552`

**Issue:** `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, and `align_cluster_fd`
lack a `Raises` / `ValueError` section in their NumPy-style docstrings. All four
can raise `ValueError` when `fdars_core` returns `FdarError` (e.g. `k > n_obs` for
KCFC, `eps ≤ 0` for DBSCAN). The `dense_flmm` and `fast_fmm` bindings in
`famm_mod.rs` do include `Raises` sections; the new clustering docs are inconsistent.

**Fix:** Add a `Raises` section to each function, for example in `dbscan_fd`:

```
Raises
------
ValueError
    If ``data`` or ``argvals`` dimensions are inconsistent, or if the
    fdars-core computation raises an error.
```

### IN-04: `test_multi_fdata.py` does not test the argvals-length mismatch guard

**File:** `tests/test_multi_fdata.py:39-61`

**Issue:** Three of the four builder guards are tested: outer-list length mismatch
(WR-01-adjacent), 1D data rejection, and nrows mismatch. The fourth guard —
`argvals[k].len() != data[k].shape[1]` — is delegated to `MultiFunData::new` and
converted to `PyValueError` via `to_pyresult`, but no test exercises it. This leaves
a gap where a future refactor of the guard chain could regress silently.

**Fix:** Add a test for the argvals-length mismatch:

```python
def test_reject_argvals_length_mismatch():
    """argvals[k] length != data[k].shape[1] → ValueError (from MultiFunData::new)."""
    wrong_av = np.linspace(0, 1, 10)  # 10 points, but VAR1 has 30 columns
    with pytest.raises(ValueError):
        mf.multi_fdata_from_components([VAR1], [wrong_av])
```

### IN-05: `test_multi_fdata.py` does not test the empty-list case

**File:** `tests/test_multi_fdata.py:1-61`

**Issue:** Passing both empty lists (`multi_fdata_from_components([], [])`) reaches
`MultiFunData::new([])` which raises `FdarError::InvalidParameter` (surfaced as
`PyValueError`). This guard path is untested.

**Fix:** Add one guard test:

```python
def test_reject_empty_components():
    """Empty component lists → ValueError (from MultiFunData::new)."""
    with pytest.raises(ValueError):
        mf.multi_fdata_from_components([], [])
```

---

_Reviewed: 2026-09-04_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
