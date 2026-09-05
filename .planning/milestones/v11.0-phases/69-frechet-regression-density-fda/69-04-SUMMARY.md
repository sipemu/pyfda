---
phase: 69-frechet-regression-density-fda
plan: "04"
subsystem: api
tags: [rust, pyo3, density-fda, lqd-transform, wasserstein, fpca, fdars-core]

requires:
  - phase: 69-03
    provides: frechet_mod.rs with all Fréchet functions registered

provides:
  - fdars.density_fda submodule with 5 functions (normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter, lqd_fpca)
  - LQD transform round-trip validated via tests
  - 6-key PyDict from lqd_fpca (mean, singular_values, loadings, scores, fve, ncomp)

affects: [phase-70, phase-72, phase-73]

actuals:
  tokens: 15000
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "naked-1D-array return for single-array transforms (normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter)"
    - "6-key PyDict for FPCA result structs (lqd_fpca pattern matching pace_fpca)"
    - "strictly-positive density fixture with epsilon floor for LQD tests"

key-files:
  created:
    - src/density_fda_mod.rs
    - tests/test_density_fda.py
  modified:
    - src/lib.rs
    - python/fdars/__init__.py

key-decisions:
  - "Write all 5 density_fda functions in a single Rust file and commit together — they share the same convert.rs imports and register() call"
  - "Use np.trapezoid (NumPy 2.x) instead of np.trapz (removed in NumPy 2.0) in test fixtures"
  - "Add epsilon (1e-8) to Beta-distributed density fixtures for strict positivity required by lqd_transform (Pitfall 6)"
  - "LQD round-trip test uses a Gaussian-perturbed uniform density (interior-smooth) not a Beta density with zero tails"
  - "Expose result.fpca.rotation as 'loadings' key (not 'rotation') per project convention"
  - "Exclude result.fpca.centered and result.fpca.weights from lqd_fpca dict (internal SVD state)"

patterns-established:
  - "Naked 1D array returns: no PyDict wrapping for single-vector density transforms"
  - "lqd_fpca dict uses 'loadings' key (rotation matrix) to match pace_fpca eigenfunctions convention"

requirements-completed: [FRE-02]

coverage:
  - id: D1
    description: "fdars.density_fda submodule registered and importable; all 5 functions callable"
    requirement: FRE-02
    verification:
      - kind: unit
        ref: "tests/test_density_fda.py#test_all_five_functions_callable"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_normalize_density_is_callable"
        status: pass
    human_judgment: false
  - id: D2
    description: "normalize_density returns naked 1D numpy array integrating to 1; raises ValueError on negative input"
    requirement: FRE-02
    verification:
      - kind: unit
        ref: "tests/test_density_fda.py#test_normalize_density_returns_1d_array"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_normalize_density_integrates_to_one"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_normalize_density_negative_value_raises"
        status: pass
    human_judgment: false
  - id: D3
    description: "lqd_transform and inverse_lqd return naked 1D arrays; LQD round-trip recovers input density; zero input raises ValueError"
    requirement: FRE-02
    verification:
      - kind: unit
        ref: "tests/test_density_fda.py#test_lqd_transform_returns_1d_array"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_lqd_round_trip"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_lqd_transform_strictly_positive_required"
        status: pass
    human_judgment: false
  - id: D4
    description: "wasserstein_barycenter returns naked 1D array of shape (M,) integrating to ~1"
    requirement: FRE-02
    verification:
      - kind: unit
        ref: "tests/test_density_fda.py#test_wasserstein_barycenter_shape"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_wasserstein_barycenter_integrates_to_one"
        status: pass
    human_judgment: false
  - id: D5
    description: "lqd_fpca returns exactly 6-key PyDict {mean, singular_values, loadings, scores, fve, ncomp} with correct shapes; no centered/weights/rotation"
    requirement: FRE-02
    verification:
      - kind: unit
        ref: "tests/test_density_fda.py#test_lqd_fpca_six_keys"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_lqd_fpca_no_internal_keys"
        status: pass
      - kind: unit
        ref: "tests/test_density_fda.py#test_lqd_fpca_shapes"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-03
status: complete
---

# Phase 69 Plan 04: Density FDA Submodule Summary

**`fdars.density_fda` submodule registered with 5 functions: `normalize_density` (naked 1D), `lqd_transform` / `inverse_lqd` (naked 1D, LQD round-trip tested), `wasserstein_barycenter` (naked 1D), and `lqd_fpca` (6-key PyDict with `loadings` key for the rotation matrix).**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-03T19:44:41Z
- **Completed:** 2026-09-03T19:50:29Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- `fdars.density_fda` submodule registered in `lib.rs` and `__init__.py`; importable from Python.
- All 5 density-FDA functions bound in `src/density_fda_mod.rs`; first four return naked 1D numpy arrays (NOT dicts), `lqd_fpca` returns a 6-key PyDict.
- 17 unit tests in `tests/test_density_fda.py` covering: normalize integration, LQD round-trip, barycenter integral, FPCA dict keys/shapes, forbidden-key absence, ValueError on invalid input.
- FRE-02 requirement completed; prior frechet tests (35 passing) unaffected.

## Task Commits

Each task was committed atomically:

1. **Task 1: TRACER — register fdars.density_fda + bind normalize_density** — `5336874` (feat) — all 5 functions written together; tracer verified end-to-end
2. **Task 2: lqd_transform, inverse_lqd, wasserstein_barycenter** — committed in same feat commit (5336874)
3. **Task 3: lqd_fpca 6-key PyDict** — committed in same feat commit (5336874)

**Plan metadata:** TBD (docs commit)

## Files Created/Modified

- `src/density_fda_mod.rs` — All 5 density-FDA PyO3 bindings with docstrings
- `tests/test_density_fda.py` — 17 tests covering all 5 functions
- `src/lib.rs` — Added `mod density_fda_mod;` and `register_submodule!(m, "density_fda", ...)`
- `python/fdars/__init__.py` — Added `"density_fda"` to `_submodule_names` and module docstring

## Decisions Made

- All 5 functions written in a single commit — they share imports and the register() call; splitting artificially would add no value.
- `np.trapezoid` used throughout (NumPy 2.x API; `np.trapz` removed in 2.0).
- LQD round-trip test uses a Gaussian-perturbed uniform density (not a Beta with zero tails) for numerical stability — confirmed with upstream source review.
- `loadings` key (not `rotation`) exposes `result.fpca.rotation` per project convention.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] np.trapz removed in NumPy 2.x**
- **Found during:** Task 1 (test collection)
- **Issue:** `np.trapz` removed in NumPy 2.0; Python 3.14 + NumPy 2.4 raises `AttributeError`
- **Fix:** Replaced all `np.trapz` calls with `np.trapezoid` in `tests/test_density_fda.py`
- **Files modified:** `tests/test_density_fda.py`
- **Verification:** Test collection succeeds; 17 tests pass
- **Committed in:** 5336874

**2. [Rule 1 - Bug] Beta density has zero at boundary; LQD requires strict positivity**
- **Found during:** Task 1 (fixture assertion)
- **Issue:** `Beta(1, 2).pdf(x=1.0) = 0`; assertion `(density_single > 0).all()` failed
- **Fix:** Added `+ 1e-8` epsilon to all density fixtures (per Pitfall 6 in research) and renormalized. Used a Gaussian-perturbed uniform density for the LQD round-trip test (boundary-stable)
- **Files modified:** `tests/test_density_fda.py`
- **Verification:** All density fixtures satisfy strict positivity; lqd_transform receives valid input
- **Committed in:** 5336874

---

**Total deviations:** 2 auto-fixed (1 blocking API change, 1 fixture bug)
**Impact on plan:** Both fixes necessary for correctness. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 69 complete: `fdars.frechet` (FRE-01) and `fdars.density_fda` (FRE-02) both registered and tested.
- FRE-03 (`extract_ragged_vecs` refactor) was completed in plan 69-01.
- All 8 plans in Phase 69 have SUMMARYs; phase is ready for `/gsd-verify-work 69` or `/gsd-complete-milestone`.

## Self-Check

- `src/density_fda_mod.rs`: FOUND
- `tests/test_density_fda.py`: FOUND
- `lib.rs` has `density_fda_mod` and `register_submodule!`: FOUND (verified via grep)
- `__init__.py` has `"density_fda"`: FOUND (verified via grep)
- Commit 5336874: FOUND (verified via `git log`)

## Self-Check: PASSED

---
*Phase: 69-frechet-regression-density-fda*
*Completed: 2026-09-03*
