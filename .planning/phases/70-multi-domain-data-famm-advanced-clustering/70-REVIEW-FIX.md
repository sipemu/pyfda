---
phase: 70-multi-domain-data-famm-advanced-clustering
fixed_at: 2026-09-04T00:00:00Z
review_path: .planning/phases/70-multi-domain-data-famm-advanced-clustering/70-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 70: Code Review Fix Report

**Fixed at:** 2026-09-04
**Source review:** `.planning/phases/70-multi-domain-data-famm-advanced-clustering/70-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (WR-01, IN-01, IN-04, IN-05; IN-02 and IN-03 out of scope per objective)
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: `test_dbscan_fd` does not assert that noise encoding (−1) is exercised

**Files modified:** `tests/test_clustering_advanced.py`
**Commit:** b2bc409
**Applied fix:** Added `assert result["n_noise"] > 0` with an explanatory message
immediately after the existing consistency-invariant check. The assertion is
a coded contract that the `None → -1i64` encoding path fires with `eps=0.5`
on 30-dimensional standard-normal data (where L2 distances of ≈ 7–10 >> 0.5
ensure all-noise output deterministically).

---

### IN-01: Module docstring does not mention the two new submodules

**Files modified:** `python/fdars/__init__.py`
**Commit:** 3ed8472
**Applied fix:** Added two bullet lines after the `density_fda` entry in the
package-level docstring:
- `- Multi-domain data (multi_fdata) — PyMultiFunData handle for multi-domain functional data`
- `- Functional Additive Mixed Models (famm) — dense_flmm, fast_fmm, multi_famm`

Note: the `_submodule_names` tuple already contained both entries (lines 63–65);
only the prose docstring was missing them.

---

### IN-04: `test_multi_fdata.py` does not test the argvals-length mismatch guard

**Files modified:** `tests/test_multi_fdata.py`
**Commit:** 8e581e4
**Applied fix:** Added `test_reject_argvals_length_mismatch` — passes a 10-point
`argvals` array against `VAR1` which has 30 columns. This exercises the fourth
builder guard (`argvals[k].len() != data[k].shape[1]`) delegated to
`MultiFunData::new` and converted to `PyValueError` via `to_pyresult`.

---

### IN-05: `test_multi_fdata.py` does not test the empty-list case

**Files modified:** `tests/test_multi_fdata.py`
**Commit:** 8e581e4 (same commit as IN-04 — both are additions to the same file)
**Applied fix:** Added `test_reject_empty_components` — passes `[], []` to
`multi_fdata_from_components`. Probed actual behavior before writing the test:

> **IN-05 actual behavior:** `multi_fdata_from_components([], [])` raises
> `ValueError: invalid parameter 'components': MultiFunData requires at least
> one component` — a clean Python exception, no panic. The test asserts
> `pytest.raises(ValueError)` which matches the observed behavior.

## Skipped Issues

None — all four in-scope findings were fixed.

## Out-of-scope Findings (not attempted)

- **IN-02** (`src/spm_mod.rs` — loop variable rename): cosmetic Rust change, excluded per objective.
- **IN-03** (`src/clustering_mod.rs` — missing `Raises` docstring sections): Rust-only doc change, excluded per objective.

## Verification

All fixes verified with:
- Tier 1 (re-read): confirmed fix text present and surrounding code intact.
- Tier 2 (test run): `.venv/bin/pytest tests/test_clustering_advanced.py tests/test_multi_fdata.py -x -q` → **10 passed**.

Verification ran in the **main checkout** (not an isolated worktree;
`workflow.use_worktrees` is `false`).

**Full suite after all fixes:**
`.venv/bin/pytest tests/ -q` → **5472 passed, 10 skipped, 120 warnings** in 167s.

---

_Fixed: 2026-09-04_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
