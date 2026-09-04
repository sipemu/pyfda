---
phase: 71-shapelets-gak-metric
plan: "01"
subsystem: api
tags: [shapelet, pyo3, rust, pyclass, opaque-handle, enum-dispatch, functional-data]

requires:
  - phase: 70-multi-domain-data-famm-advanced-clustering
    provides: PyMultiFunData opaque handle template + famm module registration pattern

provides:
  - fdars.shapelet submodule with 5 bound functions + 2 pyclass handles
  - PyShapeletFit opaque handle wrapping ShapeletTransformFit
  - PyShapeletClassifierFit opaque handle with predict() and train_accuracy()
  - String-dispatched QualityMeasure and ShapeletClassifier enums with Err arms
  - labels_i64_to_usize guard (negative-label ValueError)
  - max_candidates sentinel mapping (0 → None exhaustive)

affects:
  - phase 72 (advisor extension for shapelet/GAK — ADV-01)
  - phase 73 (shapelet docs page — DOCS-01)
  - tests/sklearn/test_foundation.py (FND-02 superset guard now includes "shapelet")

actuals:
  tokens: 21000
  tasks: 4
  commits: 3

tech-stack:
  added: []
  patterns:
    - "PyShapeletFit opaque #[pyclass] wrapping ShapeletTransformFit (3rd opaque handle in pyfda after PyIrregFdata, PyMultiFunData)"
    - "PyShapeletClassifierFit opaque #[pyclass] with #[pymethods] predict() returning i64 numpy array"
    - "quality_from_str / classifier_from_str: string→enum dispatch with mandatory Err wildcard arm (mirrors penalty_from_str pattern)"
    - "labels_i64_to_usize: per-element guard for negative labels before i64→usize cast"
    - "max_candidates sentinel: Python 0 maps to None (exhaustive) inside binding"

key-files:
  created:
    - src/shapelet_mod.rs
    - tests/test_shapelet.py
  modified:
    - src/lib.rs
    - python/fdars/__init__.py

key-decisions:
  - "shapelet_classifier_fit takes raw data+labels (independent path) matching upstream semantics; does not consume PyShapeletFit — the handle is only for the transform two-step (RESEARCH §1.3 option 1)"
  - "discover_shapelets returns summary PyDict {n_shapelets, quality} — ShapeletSet cannot be returned to Python directly (RESEARCH Open Question 1)"
  - "shapelet_classifier_fit returns PyShapeletClassifierFit opaque handle (not bare dict) so predict() is stateful — mirrors every other fitted model in pyfda (RESEARCH Open Question 2)"
  - "Test fixture for shapelet_distance uses unique spike motif; ascending ramps z-normalize identically at multiple offsets so the trivially-obvious fixture was ambiguous (deviation Rule 1 auto-fix)"

patterns-established:
  - "Opaque handle #[pyclass] for ShapeletTransformFit: wraps inner field, exposes n_shapelets/n_train getters"
  - "Opaque handle #[pyclass] for ShapeletClassifierFit: exposes predict() as #[pymethod] returning int64 numpy via usize_vec_to_numpy1d"
  - "String enum dispatch with mandatory Err arm listing all valid names in the error message"

requirements-completed: [SHAPE-01]

coverage:
  - id: D1
    description: "fdars.shapelet registered; shapelet_transform_fit returns PyShapeletFit handle with n_shapelets > 0 and n_train == 16 on 16-observation training set"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_fit_handle_accessors
        status: pass
    human_judgment: false
  - id: D2
    description: "shapelet_transform(fit, TEST) returns float64 array of shape (4, K) where K=n_shapelets and n_test=4 ≠ n_train=16 (transposition check)"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_transform_shape
        status: pass
    human_judgment: false
  - id: D3
    description: "discover_shapelets returns dict with n_shapelets > 0 and quality == 'info_gain'"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_discover
        status: pass
    human_judgment: false
  - id: D4
    description: "shapelet_distance returns (float, int) tuple; exact z-normalized spike match distance < 1e-6 at correct offset"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_distance
        status: pass
    human_judgment: false
  - id: D5
    description: "quality='bogus' raises ValueError listing info_gain and f_statistic"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_quality_err_arm
        status: pass
    human_judgment: false
  - id: D6
    description: "PyShapeletClassifierFit handle with n_shapelets > 0, train_accuracy in [0,1], int64 classes array, n_classes == 2"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_classifier_handle_accessors
        status: pass
    human_judgment: false
  - id: D7
    description: "handle.predict(TEST) returns 1D int64 array of length 4 (n_test)"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_classifier_predict_shape
        status: pass
    human_judgment: false
  - id: D8
    description: "classifier='lda' fits and predicts without error (unit variant ShapeletClassifier::Lda)"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_classifier_lda
        status: pass
    human_judgment: false
  - id: D9
    description: "classifier='bogus' raises ValueError listing knn and lda"
    requirement: SHAPE-01
    verification:
      - kind: unit
        ref: tests/test_shapelet.py::test_classifier_err_arm
        status: pass
    human_judgment: false
  - id: D10
    description: "FND-02 foundation guard: 'shapelet' in _submodule_names satisfies superset invariant (tests/sklearn/test_foundation.py green)"
    requirement: SHAPE-01
    verification:
      - kind: integration
        ref: tests/sklearn/test_foundation.py
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-09-04
status: complete
---

# Phase 71 Plan 01: fdars.shapelet Submodule Summary

**New `fdars.shapelet` submodule binding five shapelet functions + two opaque handles (`PyShapeletFit` wrapping `ShapeletTransformFit`, `PyShapeletClassifierFit` with `predict()`) + two string-dispatched `#[non_exhaustive]` enums with mandatory Err arms; all 24 shapelet+FND-02 tests green.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-04T07:13:05Z
- **Completed:** 2026-09-04T07:17:28Z
- **Tasks:** 4
- **Files modified:** 4 (src/shapelet_mod.rs created, src/lib.rs, python/fdars/__init__.py, tests/test_shapelet.py)

## Accomplishments

- `fdars.shapelet` submodule registered end-to-end; all 5 functions + 2 pyclass handles callable from Python
- `PyShapeletFit` opaque handle wrapping `ShapeletTransformFit` with `n_shapelets` and `n_train` getters; `shapelet_transform(fit, data)` correctly calls `fit.inner.shapelets()` (RESEARCH Pitfall 1 avoided)
- `PyShapeletClassifierFit` opaque handle with `predict(new_data) → int64 array`, `train_accuracy`, `classes`, `n_classes` — consistent with every other fitted-model handle in pyfda
- `quality_from_str` and `classifier_from_str` with mandatory `_` Err arms listing valid names; `ShapeletClassifier::Lda` unit variant handled correctly
- `labels_i64_to_usize` guard rejects negative labels with index-named `ValueError` (T-71-01 mitigation)
- `max_candidates=0` sentinel maps to `None` in `ShapeletDiscoveryConfig` (exhaustive search, not zero-cap)
- Non-square fixtures (`n_test=4 ≠ n_train=16`) prove no transposition bug in `shapelet_transform` and `predict`
- FND-02 foundation guard passes with `"shapelet"` in `_submodule_names` superset

## Task Commits

1. **TDD RED: failing tests** - `6bcc975` (test)
2. **Task 1+2+3 implementation: shapelet_mod.rs + lib.rs + __init__.py** - `5ab726c` (feat)
3. **Task 2: discover_shapelets + shapelet_distance test fix** - `8e30bf8` (feat)

## Files Created/Modified

- `src/shapelet_mod.rs` — New module: PyShapeletFit, PyShapeletClassifierFit, 5 pyfunction bindings, quality_from_str, classifier_from_str, labels_i64_to_usize, register()
- `src/lib.rs` — Added `mod shapelet_mod;` and `register_submodule!(m, "shapelet", shapelet_mod::register)`
- `python/fdars/__init__.py` — Added `"shapelet"` to `_submodule_names` after `"famm"` (Phase 71 comment)
- `tests/test_shapelet.py` — 8 unit tests covering all SHAPE-01 behaviors

## Decisions Made

- **Independent path for classifier** (`shapelet_classifier_fit` takes raw data+labels, not `PyShapeletFit`): matches upstream `shapelet_classifier_fit` semantics exactly; the handle is only for the transform two-step.
- **discover_shapelets → summary dict**: `ShapeletSet` cannot cross the PyO3 boundary directly; return `{n_shapelets, quality}` as a `PyDict`.
- **PyShapeletClassifierFit opaque handle** (not bare dict): enables `predict()` without refitting; consistent with `PyIrregFdata` / `PyMultiFunData` template.
- **Implementation monolith**: all three functions written in one commit to avoid multiple rebuild cycles; TDD RED was committed first, GREEN followed with the complete module.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed ambiguous test_distance fixture**
- **Found during:** Task 2 (running test_distance)
- **Issue:** Test used an ascending ramp series `[1,2,3,4,5,...]`; windows at offset 0 `[1,2,3,4]` and offset 1 `[2,3,4,5]` z-normalize to the same vector, so the core correctly returns offset 0 (first best match) rather than the expected offset 1
- **Fix:** Replaced fixture with a unique spike motif `[0,0,0,0,0,1,4,1,0,0,0,0]`; the spike at index 5 is the only near-zero-distance window; assertion on offset == 5 is now unambiguous
- **Files modified:** `tests/test_shapelet.py`
- **Verification:** `test_distance` passes with `dist < 1e-6` and `offset == 5`
- **Committed in:** `8e30bf8` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - test fixture bug)
**Impact on plan:** Test fixture corrected to match actual core behavior; no production code changed; acceptance assertion semantics preserved.

## Issues Encountered

None — the Rust code compiled clean on first try. No unused-import warnings under `-D warnings`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SHAPE-01 complete; `fdars.shapelet` submodule fully functional with all 5 functions + 2 handles
- SHAPE-02 (GAK metric extension to `fdars.metric`) is the next plan in Phase 71
- All 24 tests green; FND-02 foundation guard passes with "shapelet" in superset

## Self-Check

- [x] `src/shapelet_mod.rs` exists: FOUND
- [x] `tests/test_shapelet.py` exists: FOUND
- [x] `register_submodule!(m, "shapelet")` in `src/lib.rs`: FOUND
- [x] `"shapelet"` in `python/fdars/__init__.py`: FOUND
- [x] Commits `6bcc975`, `5ab726c`, `8e30bf8`: FOUND in git log
- [x] All 24 tests pass: VERIFIED

## Self-Check: PASSED

---
*Phase: 71-shapelets-gak-metric*
*Completed: 2026-09-04*
