---
phase: 71-shapelets-gak-metric
plan: "02"
subsystem: api
tags: [rust, pyo3, gak, global-alignment-kernel, metric, sklearn, precomputed-kernel]

requires:
  - phase: 71-01
    provides: shapelet_mod.rs with PyShapeletFit opaque handle pattern

provides:
  - "gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict in fdars.metric"
  - "PyGakGramTrain opaque #[pyclass] handle (pyfda's 4th opaque handle)"
  - "sklearn precomputed-kernel contract: gak_gram_matrix→(n,n), gak_gram_predict→(n_test,n_train)"

affects:
  - fdars.metric module users
  - sklearn integration (metric='precomputed' workflows)
  - Phase 72 (advisor extension for GAK)

actuals:
  tokens: 76750
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "make_gak_config() helper to construct #[non_exhaustive] GakConfig from Option<f64>"
    - "PyGakGramTrain opaque handle: pub inner: GakGramTrain (pub(crate) fields accessible in-crate)"
    - "Infallible returns (gak, sigma_gak) use Ok(core_fn()) directly — no to_pyresult"

key-files:
  created:
    - tests/test_gak.py
  modified:
    - src/metric_mod.rs

key-decisions:
  - "make_gak_config(sigma: Option<f64>) helper required because GakConfig is #[non_exhaustive]: no struct literal from outside crate; use GakConfig::with_sigma(s) / GakConfig::default()"
  - "All 3 tasks committed together in one feat commit (all additions in same file src/metric_mod.rs)"
  - "PyGakGramTrain.inner stores the full GakGramTrain struct — gak_gram_predict passes &train.inner to core which reads pub(crate) fields directly"

patterns-established:
  - "make_gak_config() pattern: wraps #[non_exhaustive] external struct construction behind an inline helper to avoid code duplication"
  - "Infallible core function return: Ok(core_fn()) without to_pyresult for functions that never return Err"

requirements-completed: [SHAPE-02]

coverage:
  - id: D1
    description: "gak(x, y, sigma) returns float in [0,1]; gak(X, X, sigma)==1.0 exactly"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_gak_self_similarity"
        status: pass
    human_judgment: false
  - id: D2
    description: "sigma_gak(data) returns positive float bandwidth heuristic"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_sigma_gak"
        status: pass
    human_judgment: false
  - id: D3
    description: "gak_gram_matrix returns symmetric (n,n) PSD numpy array with unit diagonal"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_gram_matrix_shape"
        status: pass
    human_judgment: false
  - id: D4
    description: "gak_gram_train returns PyGakGramTrain handle with .gram (n_train,n_train), .sigma>0, .n_train correct"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_gram_train_handle"
        status: pass
    human_judgment: false
  - id: D5
    description: "handle.gram matches gak_gram_matrix output within 1e-12"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_gram_train_matches_matrix"
        status: pass
    human_judgment: false
  - id: D6
    description: "gak_gram_predict(handle, TEST_MAT) returns shape (n_test, n_train) = (3, 8) — precomputed-kernel contract"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_gram_predict_shape"
        status: pass
    human_judgment: false
  - id: D7
    description: "gak_gram_predict(handle, TRAIN_MAT) reproduces handle.gram within 1e-12"
    requirement: SHAPE-02
    verification:
      - kind: unit
        ref: "tests/test_gak.py::test_gram_predict_reproduces_train"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-04
status: complete
---

# Phase 71 Plan 02: GAK Metric Extension Summary

**PyGakGramTrain opaque handle + 5 GAK functions (gak, sigma_gak, gak_gram_matrix, gak_gram_train, gak_gram_predict) added to fdars.metric with (n,n) and (n_test,n_train) sklearn precomputed-kernel shape contracts verified**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-04T07:20:36Z
- **Completed:** 2026-09-04T07:24:06Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Extended `src/metric_mod.rs` with `PyGakGramTrain` `#[pyclass]` handle (pyfda's 4th opaque handle) wrapping `fdars_core::metric::gak::GakGramTrain`; exposes `.gram`, `.sigma`, `.n_train` getters
- Bound all 5 GAK functions on `fdars.metric`: `gak` (pairwise scalar), `sigma_gak` (bandwidth heuristic), `gak_gram_matrix` (one-shot (n,n) symmetric Gram), `gak_gram_train` (returns `PyGakGramTrain`), `gak_gram_predict` ((n_test,n_train) incremental prediction)
- Added `tests/test_gak.py` with 7 tests covering all functions and both Gram shape contracts; all 22 tests in `test_gak.py` + `tests/sklearn/test_foundation.py` green

## Task Commits

Each task was committed atomically:

1. **Task 1 (tracer): gak_gram_matrix + gak + sigma_gak** - `d315fc9` (feat) — includes Tasks 2 and 3 code since all additions live in the same file and were implemented together

**Plan metadata:** _(docs commit follows)_

_Note: All three tasks were implemented in a single feat commit since the entire implementation lives in src/metric_mod.rs._

## Files Created/Modified

- `src/metric_mod.rs` — Extended with PyGakGramTrain #[pyclass], make_gak_config() helper, and 5 GAK #[pyfunction] bindings; existing register() extended
- `tests/test_gak.py` — 7 tests: test_gak_self_similarity, test_sigma_gak, test_gram_matrix_shape, test_gram_train_handle, test_gram_train_matches_matrix, test_gram_predict_shape, test_gram_predict_reproduces_train

## Decisions Made

- **make_gak_config() helper:** `GakConfig` is `#[non_exhaustive]` — struct literal `GakConfig { sigma }` fails to compile from outside the crate. Used `GakConfig::with_sigma(s)` / `GakConfig::default()` behind a helper function to avoid repetition.
- **Single feat commit for all 3 tasks:** All implementation lives in `src/metric_mod.rs` and `tests/test_gak.py`; splitting into separate commits would require incremental partial-file edits that add no clarity.
- **pub(crate) fields are invisible from pyfda — by design:** `gak_gram_predict` passes `&train.inner` to `core_gak_gram_predict` which reads `log_self`/`train_rows` directly; pyfda never touches those fields.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] GakConfig struct literal fails for #[non_exhaustive] structs**
- **Found during:** Task 1 (gak_gram_matrix / gak_gram_train implementation)
- **Issue:** RESEARCH Pitfall 7 said `GakConfig { sigma }` (setting all named fields) would work even for `#[non_exhaustive]`, but Rust E0639 prohibits struct literals for `#[non_exhaustive]` structs from outside the crate regardless of whether all fields are named.
- **Fix:** Added `make_gak_config(sigma: Option<f64>) -> GakConfig` helper that dispatches to `GakConfig::with_sigma(s)` or `GakConfig::default()`.
- **Files modified:** `src/metric_mod.rs`
- **Verification:** `RUSTFLAGS="-D warnings" cargo check` clean; all tests pass
- **Committed in:** d315fc9 (feat commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - compile error)
**Impact on plan:** Minimal — single helper function addition; no scope change. The RESEARCH correctly identified `GakConfig::with_sigma` as the fallback; the fix applied it.

## Issues Encountered

None — build succeeded after the GakConfig construction fix; all 7 new tests and 15 existing foundation tests green.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 71 complete (SHAPE-01 done in 71-01, SHAPE-02 done in 71-02)
- `fdars.metric` now has the full GAK suite usable as a precomputed sklearn kernel
- Ready for Phase 72: advisor extension for shapelet/GAK

---
*Phase: 71-shapelets-gak-metric*
*Completed: 2026-09-04*

## Self-Check: PASSED

- `tests/test_gak.py` exists on disk: FOUND
- `src/metric_mod.rs` modified: FOUND
- Commit d315fc9 exists: FOUND (`git log --oneline -1 d315fc9` = `d315fc9 feat(71-02): add GAK metric bindings to fdars.metric (SHAPE-02)`)
- All 7 GAK tests pass: PASSED
- All 22 tests (test_gak.py + test_foundation.py) pass: PASSED
- `cargo check` clean under `-D warnings`: PASSED
