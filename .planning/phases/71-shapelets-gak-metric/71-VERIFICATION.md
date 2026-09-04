---
phase: 71-shapelets-gak-metric
verified: 2026-09-04T10:00:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 71: Shapelets + GAK Metric — Verification Report

**Phase Goal:** Users can discover and apply shapelets (with a fitted-state handle and classifier) and use the Global-Alignment-Kernel metric — including its Gram matrix as a precomputed sklearn kernel.
**Verified:** 2026-09-04T10:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `import fdars.shapelet` works; discover_shapelets, shapelet_transform_fit/shapelet_transform, shapelet_classifier_fit, shapelet_distance callable, with a PyShapeletFit opaque handle (roadmap SC1) | ✓ VERIFIED | Live: `import fdars.shapelet` succeeds; all 5 functions callable; PyShapeletFit returned by transform_fit with n_shapelets=58, n_train=16 on 16-obs training set; shapelet_transform returns (4, 58) on 4-obs test set (n_test ≠ n_train proves no transposition) |
| 2 | QualityMeasure and ShapeletClassifier dispatched by string, each with an Err fallback arm raising ValueError listing valid variants on invalid input (roadmap SC2) | ✓ VERIFIED | Live: `quality='bogus'` raises `ValueError: quality must be 'info_gain' or 'f_statistic', got 'bogus'`; `classifier='bogus'` raises `ValueError: classifier must be 'knn' or 'lda', got 'bogus'`; k=0 raises `ValueError: k must be >= 1 for the 'knn' classifier`; negative label raises `ValueError: labels[0] = -1 is negative; labels must be non-negative integers`. Tests: test_quality_err_arm, test_classifier_err_arm, test_knn_k_zero_rejected, test_negative_label_rejected — all pass |
| 3 | GAK functions (gak, gak_gram_matrix, gak_gram_train/gak_gram_predict, sigma_gak) extend fdars.metric, Gram usable as a precomputed kernel (roadmap SC3) | ✓ VERIFIED | Live: all 5 functions callable on fdars.metric; gak_gram_matrix(TRAIN_MAT) returns (8,8) with diagonal ~1.0 and symmetric (G==G.T within 1e-12); gak_gram_predict(handle, TEST_MAT) returns (3,8) — the (n_test, n_train) sklearn precomputed-kernel contract confirmed with n_test=3 ≠ n_train=8 |
| 4 | shapelet_transform_fit returns a PyShapeletFit opaque handle; shapelet_classifier_fit returns a handle with .predict + .train_accuracy (plan must-have, SHAPE-01) | ✓ VERIFIED | Live: PyShapeletFit type confirmed; PyShapeletClassifierFit.train_accuracy=1.0, n_classes=2, classes dtype=int64, predict returns (4,) int64 array. Tests: test_fit_handle_accessors, test_classifier_handle_accessors, test_classifier_predict_shape — all pass |
| 5 | gak_gram_matrix returns symmetric (n,n) with unit diagonal; gak_gram_predict returns (n_test, n_train) — precomputed-kernel contract (plan must-have, SHAPE-02) | ✓ VERIFIED | Live: (8,8) symmetric unit-diagonal confirmed; (3,8) predict shape confirmed. Tests: test_gram_matrix_shape, test_gram_predict_shape, test_gram_predict_reproduces_train — all pass |
| 6 | PyGakGramTrain opaque handle: gak_gram_train returns handle; gak_gram_predict passes &train.inner without touching pub(crate) fields (plan must-have, SHAPE-02) | ✓ VERIFIED | src/metric_mod.rs:190-196 — PyGakGramTrain wraps GakGramTrain.inner; gak_gram_predict passes &train.inner to core_gak_gram_predict; no direct field access on pub(crate) members. Tests: test_gram_train_handle, test_gram_train_matches_matrix — all pass |
| 7 | Code review findings addressed: WR-01 (negative-label test), IN-01 (comment typo), IN-02 (gak self-similarity call), IN-03 (k=0 guard) — all fixed per REVIEW-FIX.md | ✓ VERIFIED | REVIEW-FIX.md confirms 4/4 fixed; codebase: labels_i64_to_usize at shapelet_mod.rs:60 guards v<0; classifier_from_str checks k==0 at line 45; test_negative_label_rejected and test_knn_k_zero_rejected present in test_shapelet.py; test_gak_self_similarity calls gak(X, X, SIGMA); comment at test_shapelet.py:101 reads "index 5" |

**Score:** 7/7 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/shapelet_mod.rs` | New shapelet binding module | ✓ VERIFIED | 481 lines; PyShapeletFit, PyShapeletClassifierFit, 5 #[pyfunction]s, quality_from_str, classifier_from_str, labels_i64_to_usize, register() |
| `tests/test_shapelet.py` | Phase-01 test suite | ✓ VERIFIED | 10 tests covering all SHAPE-01 behaviors (including post-review-fix test_negative_label_rejected, test_knn_k_zero_rejected) |
| `src/metric_mod.rs` | GAK extension of existing module | ✓ VERIFIED | 705 lines (was 505); PyGakGramTrain, make_gak_config, 5 GAK #[pyfunction]s added to existing register() |
| `tests/test_gak.py` | Phase-02 test suite | ✓ VERIFIED | 7 tests covering gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/lib.rs` | `src/shapelet_mod.rs` | `mod shapelet_mod;` + `register_submodule!(m, "shapelet", shapelet_mod::register)` | ✓ WIRED | lib.rs:36 (mod) and lib.rs:76 (register_submodule) confirmed |
| `python/fdars/__init__.py` | `fdars.shapelet` | `"shapelet"` in `_submodule_names` | ✓ WIRED | __init__.py:67 — `"shapelet",  # Phase 71 — Shapelets ...` |
| `PyShapeletFit.inner` | `ShapeletTransformFit` | `fit.inner.shapelets()` in shapelet_transform (Pitfall 1) | ✓ WIRED | shapelet_mod.rs:343 — `fdars_core::shapelet::shapelet_transform(fit.inner.shapelets(), &mat)` |
| `metric_mod::register` | GAK functions + PyGakGramTrain | `m.add_class`, `m.add_function` lines | ✓ WIRED | metric_mod.rs:698-703 — all 5 GAK functions + class registered in existing register() |
| `PyGakGramTrain.inner` | `gak_gram_predict` | `&train.inner` passed to core (avoiding pub(crate)) | ✓ WIRED | metric_mod.rs:196 — `core_gak_gram_predict(&train.inner, &mat)` |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `shapelet_transform_fit` | fit.inner | `fdars_core::shapelet::shapelet_transform_fit(&mat, &label_vec, &config)` | Yes — core computation, n_shapelets=58 confirmed live | ✓ FLOWING |
| `gak_gram_matrix` | Gram matrix | `core_gak_gram_matrix(&mat, &config)` via to_pyresult | Yes — (8,8) symmetric unit-diagonal confirmed live | ✓ FLOWING |
| `gak_gram_predict` | K_test array | `core_gak_gram_predict(&train.inner, &mat)` | Yes — (3,8) shape confirmed live | ✓ FLOWING |
| `PyShapeletClassifierFit.predict` | labels_usize | `self.inner.predict(&mat)` via to_pyresult | Yes — (4,) int64 array confirmed live | ✓ FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `import fdars.shapelet, fdars.metric` succeeds | `.venv/bin/python -c "import fdars.shapelet, fdars.metric"` | "imports OK" | ✓ PASS |
| All 5 shapelet functions + all 5 GAK functions callable | Python attribute check | All 10 reported OK | ✓ PASS |
| shapelet_transform_fit returns PyShapeletFit; n_shapelets=58, n_train=16 | Live check with TRAIN (16 obs) | Confirmed | ✓ PASS |
| shapelet_transform(fit, TEST) shape (4, 58) — n_test ≠ n_train | Live check with TEST (4 obs) | (4, 58) confirmed | ✓ PASS |
| Enum Err arms: bogus quality/classifier raise ValueError listing valid names | Live check with "bogus" inputs | All 4 guards raised correct ValueError messages | ✓ PASS |
| gak_gram_matrix symmetric (8,8) unit diagonal | Live check | Shape (8,8), diagonal ~1.0, G==G.T within 1e-12 | ✓ PASS |
| gak_gram_predict (n_test, n_train) = (3,8) | Live check with TEST_MAT | (3, 8) confirmed | ✓ PASS |
| Phase tests (test_shapelet.py + test_gak.py) | `.venv/bin/pytest tests/test_shapelet.py tests/test_gak.py -q` | 18 passed | ✓ PASS |
| Full test suite regression | `.venv/bin/pytest tests/ -q` | 5490 passed, 10 skipped, 0 failed | ✓ PASS |
| FND-02 foundation guard | `.venv/bin/pytest tests/sklearn/test_foundation.py -q` | 15 passed | ✓ PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SHAPE-01 | 71-01-PLAN.md | fdars.shapelet submodule with discover_shapelets, shapelet_transform_fit/transform, shapelet_classifier_fit, shapelet_distance; PyShapeletFit handle; QualityMeasure and ShapeletClassifier enum dispatch with Err arms | ✓ SATISFIED | Live import + callable check; 10 tests pass; opaque handles confirmed |
| SHAPE-02 | 71-02-PLAN.md | GAK metric functions extending fdars.metric; Gram usable as precomputed sklearn kernel | ✓ SATISFIED | Live import + callable check; 7 tests pass; (n,n) and (n_test,n_train) shapes confirmed |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | No TBD/FIXME/XXX markers; no return null/empty stubs; no unimplemented guards | — | — |

No debt markers or stub patterns found in any Phase 71 modified files.

---

### Human Verification Required

(none — all observable truths verified programmatically)

---

## Gaps Summary

No gaps. All 7 must-have truths verified. Requirements SHAPE-01 and SHAPE-02 satisfied. Full test suite (5490 tests) passes with no regressions. All four code-review findings (WR-01, IN-01, IN-02, IN-03) confirmed fixed in the codebase.

---

_Verified: 2026-09-04T10:00:00Z_
_Verifier: Claude (gsd-verifier)_
