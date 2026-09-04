---
phase: 71-shapelets-gak-metric
reviewed: 2026-09-04T00:00:00Z
depth: deep
files_reviewed: 6
files_reviewed_list:
  - src/shapelet_mod.rs
  - src/metric_mod.rs
  - src/lib.rs
  - python/fdars/__init__.py
  - tests/test_shapelet.py
  - tests/test_gak.py
findings:
  critical: 0
  warning: 1
  info: 3
  total: 4
status: findings
---

# Phase 71: Code Review Report

**Reviewed:** 2026-09-04T00:00:00Z
**Depth:** deep
**Files Reviewed:** 6
**Status:** findings

## Summary

Phase 71 adds the `fdars.shapelet` submodule (`src/shapelet_mod.rs`, 474 lines, new) and
extends `fdars.metric` with GAK functions (`src/metric_mod.rs`, +~200 lines). The implementation
is architecturally sound: both opaque handles (`PyShapeletFit`, `PyShapeletClassifierFit`,
`PyGakGramTrain`) wrap their core types correctly; both enum string dispatchers have mandatory
wildcard Err arms listing all valid names; label conversion uses the guarded `labels_i64_to_usize`
(not the unguarded `convert::numpy1d_to_usize_vec`); `gak_gram_predict` passes `&train.inner`
to the core function and never touches `pub(crate)` fields; `ShapeletDiscoveryConfig` (not
`#[non_exhaustive]`) is built via struct literal, while `GakConfig` (IS `#[non_exhaustive]`)
is correctly built through `make_gak_config` using `GakConfig::with_sigma` / `GakConfig::default()`.

The Gram shape contract is correctly tested — the non-square `(3, 8)` predict shape and
`(8, 8)` train-Gram shape are both exercised against fixtures where `n_test ≠ n_train`.
`shapelet_transform` correctly calls `fit.inner.shapelets()` (not `&fit.inner` directly),
satisfying Pitfall 1 from the research. No `unwrap`/`expect`/`panic!` calls appear in the new
Phase 71 code; the pre-existing `unwrap()` in `convert::fdmatrix_to_numpy2d` is out of scope.

One warning (missing test for a documented guard) and three info items (comment inaccuracy,
misleading test assertion message, unguarded k=0 delegation) are reported below.

---

## Warnings

### WR-01: No test exercises the negative-label `ValueError` guard

**File:** `tests/test_shapelet.py` — test suite (no specific line; gap in coverage)
**Issue:** `labels_i64_to_usize` in `shapelet_mod.rs:53-68` correctly rejects negative label
values with a descriptive `ValueError`. The research explicitly required this guard (Pitfall 5,
Security §V5). However, no test in `test_shapelet.py` passes a negative label to
`shapelet_transform_fit`, `discover_shapelets`, or `shapelet_classifier_fit`. The analogous
test for invalid quality/classifier strings IS present (`test_quality_err_arm`,
`test_classifier_err_arm`), making the omission asymmetric — a future refactor that
accidentally removes the negativity check would go undetected.

**Fix:** Add a test parallel to the existing Err-arm tests:

```python
def test_negative_label_rejected():
    """Negative labels raise ValueError from labels_i64_to_usize guard."""
    import fdars.shapelet as sh
    bad_labels = TRAIN_Y.copy()
    bad_labels[0] = -1
    with pytest.raises(ValueError, match="negative"):
        sh.shapelet_transform_fit(TRAIN, bad_labels)
    with pytest.raises(ValueError, match="negative"):
        sh.discover_shapelets(TRAIN, bad_labels)
    with pytest.raises(ValueError, match="negative"):
        sh.shapelet_classifier_fit(TRAIN, bad_labels)
```

---

## Info

### IN-01: `test_distance` comment claims spike starts at index 4, code correctly uses 5

**File:** `tests/test_shapelet.py:101`
**Issue:** The comment reads `"unique spike motif starting at index 4 (not at 0 to be unambiguous)"`,
but the series is `[0,0,0,0,0,1,4,1,0,0,0,0]` — the non-zero values start at **index 5**
(0-based). The code at line 105 sets `window_start = 5` which is correct. The comment is
wrong and would mislead anyone debugging a test failure.

**Fix:**

```python
# Series with a unique spike motif starting at index 5 (not at 0 to be unambiguous)
```

---

### IN-02: `test_gak_self_similarity` error message says `gak(X, X, sigma)` but calls `gak(X, Y, sigma)`

**File:** `tests/test_gak.py:38-41`
**Issue:** The docstring and the `assert` failure message both say `"gak(X, X, sigma) should be ~1.0"`,
but the actual call at line 40 is `m.gak(X, Y, SIGMA)`. `X` and `Y` happen to be
value-identical (`[0,1,2,3]`), so the assertion passes and the semantic is correct. However,
if a future maintainer changes `Y` to a distinct series, the test would silently become a
cross-similarity test while the message still claims self-similarity, causing a confusing failure.

**Fix:** Either test `gak(X, X, SIGMA)` explicitly or update the message:

```python
val_self = m.gak(X, X, SIGMA)   # same variable — true self-similarity
assert abs(val_self - 1.0) < 1e-9, f"gak(X, X, sigma) should be exactly 1.0, got {val_self}"
```

---

### IN-03: No binding-level guard for `k=0` with the `"knn"` classifier; silently delegated to core

**File:** `src/shapelet_mod.rs:42-49`
**Issue:** `classifier_from_str("knn", 0)` constructs `ShapeletClassifier::Knn { k: 0 }` without
checking `k >= 1`. Whether this produces a user-visible `FdarError` (converted to `ValueError`)
or a silent degenerate result depends entirely on fdars-core's internal guard — there is no
binding-level defense. The `k` parameter defaults to `1` in the Python signature, so ordinary
callers are safe, but `sh.shapelet_classifier_fit(TRAIN, TRAIN_Y, k=0)` reaches core
unchecked. An explicit early guard would be more defensive and consistent with how negative
labels are handled.

**Fix:**

```rust
fn classifier_from_str(classifier: &str, k: usize) -> PyResult<ShapeletClassifier> {
    match classifier {
        "knn" => {
            if k == 0 {
                return Err(PyValueError::new_err(
                    "k must be >= 1 for the 'knn' classifier"
                ));
            }
            Ok(ShapeletClassifier::Knn { k })
        }
        "lda" => Ok(ShapeletClassifier::Lda),
        _ => Err(PyValueError::new_err(format!(
            "classifier must be 'knn' or 'lda', got '{classifier}'"
        ))),
    }
}
```

---

_Reviewed: 2026-09-04T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
