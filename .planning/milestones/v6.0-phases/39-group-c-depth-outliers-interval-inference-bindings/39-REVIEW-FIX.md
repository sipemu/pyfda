---
phase: 39-group-c-depth-outliers-interval-inference-bindings
fixed_at: 2026-08-21T10:30:00Z
review_path: .planning/phases/39-group-c-depth-outliers-interval-inference-bindings/39-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 39: Code Review Fix Report

**Fixed at:** 2026-08-21T10:30:00Z
**Source review:** .planning/phases/39-group-c-depth-outliers-interval-inference-bindings/39-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: `tvdmss` and `depthgram` lack degenerate-input tests (minimum-n guards untested)

**Files modified:** `tests/test_outliers.py`
**Commit:** f852db3
**Applied fix:** Added `test_tvdmss_degenerate_n_too_small` to `TestTvdMss` (passes a 2-row input, asserts `ValueError`) and `test_depthgram_degenerate_n_too_small` to `TestDepthgram` (passes a 1-row input, asserts `ValueError`). Both mirror the existing `TestMuod.test_muod_degenerate` pattern exactly.

### WR-02: ITP seed-contract test only verifies idempotency, not the `seed=None → 0` equivalence

**Files modified:** `tests/test_inference.py`
**Commit:** f852db3
**Applied fix:** Added `test_itp_two_pop_seed_none_equals_seed_zero` to `TestItpTwoPop`. Calls `itp_two_pop` with `seed=None` and `seed=0` on identical inputs and asserts `np.array_equal` on `adjusted_pvalues`. Mirrors the existing `test_seed_none_equals_seed_zero` pattern from `TestTPerm` and `TestFPerm`.

### IN-01: `itp_one_pop` `mu0` non-None path is untested

**Files modified:** `tests/test_inference.py`
**Commit:** f852db3
**Applied fix:** Added `test_itp_one_pop_with_mu0` to `TestItpOnePop`. Passes `mu0=np.zeros(24)` alongside the data matrix and asserts the returned dict contains a valid `adjusted_pvalues` array with shape `(n_basis,)`. This exercises the `Option<Vec<f64>>` → `as_deref()` conversion path in `itp_one_pop`.

### IN-02: `itp_one_pop` and `itp_flm` lack any determinism test

**Files modified:** `tests/test_inference.py`
**Commit:** f852db3
**Applied fix:** Added `test_itp_one_pop_determinism` to `TestItpOnePop` and `test_itp_flm_determinism` to `TestItpFlm`. Both call the function twice with `seed=None` on identical inputs and assert `np.array_equal` on `adjusted_pvalues`, matching the existing `test_itp_two_pop_determinism` pattern.

### IN-03: `sequential_transform_outliers` error message verifies offending token but not valid token list

**Files modified:** `tests/test_outliers.py`
**Commit:** f852db3
**Applied fix:** Strengthened `test_seqtransform_bad_transform` in `TestSeqTransform` to also assert `"t0" in str(exc_info.value)` after the `pytest.raises(ValueError, match="nope")` context manager exits, confirming the error message enumerates valid transform tokens. Mirrors the depth module's `test_unknown_method_lists_new_tokens` contract pattern.

## Verification

**Verification ran in:** isolated git worktree (`.claude/worktrees/rf-39-1676266-1787292531`)

- Tier 1 (re-read): All modified sections confirmed intact after each edit.
- Tier 2 (test run): `python -m pytest tests/test_outliers.py tests/test_inference.py -q` — 10 passed / 82 passed, 0 failed.
- Full suite: `python -m pytest tests/ -q` — 681 passed, 4 skipped, 0 failed.
- Rust gates: `cargo fmt --check` — clean (no output, no Rust files modified).

---

_Fixed: 2026-08-21T10:30:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
