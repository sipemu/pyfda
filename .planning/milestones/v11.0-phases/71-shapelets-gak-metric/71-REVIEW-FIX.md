---
phase: 71-shapelets-gak-metric
fixed_at: 2026-09-04T00:00:00Z
review_path: .planning/phases/71-shapelets-gak-metric/71-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 71: Code Review Fix Report

**Fixed at:** 2026-09-04T00:00:00Z
**Source review:** .planning/phases/71-shapelets-gak-metric/71-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (WR-01 + IN-01 + IN-02 + IN-03)
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: No test exercises the negative-label ValueError guard

**Files modified:** `tests/test_shapelet.py`
**Commit:** 599376a
**Applied fix:** Added `test_negative_label_rejected` at the end of the test file. The test copies `TRAIN_Y`, sets `bad_labels[0] = -1`, and asserts all three entry points (`shapelet_transform_fit`, `discover_shapelets`, `shapelet_classifier_fit`) raise `ValueError` matching `"negative"` — which is the word present in the guard message at `shapelet_mod.rs:60` (`"labels[{i}] = {v} is negative; labels must be non-negative integers"`).

### IN-01: test_distance comment claims spike starts at index 4, code correctly uses 5

**Files modified:** `tests/test_shapelet.py`
**Commit:** 50e0854
**Applied fix:** Corrected the comment on line 101 from `"starting at index 4"` to `"starting at index 5"` and updated the trailing description from `"The spike [0,1,4,1,0] at index 4"` to `"The spike [1,4,1] at index 5"` to match the actual `series` array and `window_start = 5`. Code was already correct; comment only.

### IN-02: test_gak_self_similarity error message says gak(X, X, sigma) but calls gak(X, Y, sigma)

**Files modified:** `tests/test_gak.py`
**Commit:** b92f683
**Applied fix:** Changed `m.gak(X, Y, SIGMA)` to `m.gak(X, X, SIGMA)` with an inline comment `# same variable — true self-similarity`. Updated the assertion message from `"should be ~1.0"` to `"should be exactly 1.0"`. The assertion value (`abs(val_self - 1.0) < 1e-9`) is unchanged. `Y` is still in the fixture and used by the cross-similarity assertion (`m.gak(X, Z, SIGMA)`) via `Z` — no fixture change needed.

### IN-03: No binding-level guard for k=0 with the knn classifier

**Files modified:** `src/shapelet_mod.rs`, `tests/test_shapelet.py`
**Commit:** 11d0a81
**Applied fix:**
- `src/shapelet_mod.rs`: Expanded the `"knn"` arm in `classifier_from_str` to check `k == 0` before constructing `ShapeletClassifier::Knn { k }`. Returns `PyValueError("k must be >= 1 for the 'knn' classifier")` on `k=0`. The `"lda"` arm and the wildcard `Err` arm are untouched.
- `tests/test_shapelet.py`: Added `test_knn_k_zero_rejected` asserting `sh.shapelet_classifier_fit(TRAIN, TRAIN_Y, classifier="knn", k=0)` raises `ValueError` matching `"k must be >= 1"`.
- Build: `maturin develop` passed under `-D warnings` (Rust 1.83+).

---

## Verification

All fixes were verified with:

1. Targeted suite after each pure-test fix: `pytest tests/test_shapelet.py tests/test_gak.py -x -q` — passed.
2. After IN-03 (Rust change): `maturin develop` compiled without warnings or errors; targeted suite passed (18 tests).
3. Full suite after all fixes: `pytest tests/ -q` — **5490 passed, 10 skipped, 0 failed** (164 s).

Verification ran in the main checkout (workflow.use_worktrees=false).

---

_Fixed: 2026-09-04T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
