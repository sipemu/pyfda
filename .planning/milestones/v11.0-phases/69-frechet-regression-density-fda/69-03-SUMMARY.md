---
phase: 69-frechet-regression-density-fda
plan: "03"
subsystem: frechet
tags: [rust, pyo3, frechet-mean, metric-spaces, spd, spherical, correlation, monomorphized-dispatch]

requires:
  - phase: 69-frechet-regression-density-fda
    provides: "69-02: frechet_mod.rs skeleton with frechet_anova, frechet_global_reg, frechet_local_reg + register(); tests/test_frechet.py with 21 passing tests"

provides:
  - "frechet_mean(objects, space, d, weights=None) bound to fdars.frechet with monomorphized 3-space string dispatch"
  - "Per-space input helpers: spd_object_from_numpy, spherical_object_from_numpy, corr_object_from_numpy, flat_col_major_to_numpy2d"
  - "In-binding validation: SPD symmetric + positive diagonal; spherical unit-norm; correlation unit-diagonal + symmetric"
  - "Wildcard arm raises ValueError listing all 3 valid space names"
  - "14 new tests covering all 3 spaces + invalid-space + bad-norm/shape negatives"

affects: [69-04, 72-advisor-frechet-aspect, 73-frechet-docs]

actuals:
  tokens: 8500
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Monomorphized string dispatch: match space { arm => frechet_mean::<ConcreteSpace>(...) } — no trait objects, no dynamic dispatch"
    - "Per-space object marshalling: per-object extract + flatten col-major + structural validation before upstream call"
    - "PyAny return type with .into_any() per branch — branches yield PyArray2 (spd/corr) or PyArray1 (spherical)"
    - "flat_col_major_to_numpy2d helper: Vec<f64> col-major d*d → (d,d) numpy 2D via PyArray2::from_vec2"

key-files:
  created: []
  modified:
    - src/frechet_mod.rs
    - tests/test_frechet.py

key-decisions:
  - "Monomorphized dispatch (not trait objects): frechet_mean::<SpdMatrixSpace>/SphericalSpace/CorrelationMatrixSpace per match arm — required because MetricSpace trait is not object-safe"
  - "SpdMetric::Frobenius only: no metric parameter exposed; Power/LogCholesky deferred to a later phase per CONTEXT.md locked decision"
  - "d: usize parameter for ambient dimension rather than inferring from first object — explicit is safer and matches research recommendation"
  - "PyAny return type: branches return different numpy types (PyArray2 vs PyArray1); .into_any() unifies the return"
  - "Per-object validation in binding (not upstream): diagonal positivity check for SPD; unit-norm for spherical; unit-diagonal + symmetry for correlation"

requirements-completed: [FRE-01]

coverage:
  - id: D1
    description: "frechet_mean bound with monomorphized spd/spherical/correlation dispatch + Err wildcard arm"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpd::test_callable"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanInvalidSpace::test_invalid_space_raises_valueerror"
        status: pass
    human_judgment: false
  - id: D2
    description: "SPD returns symmetric (d,d) array; in-binding validation raises on non-symmetric or non-positive diagonal"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpd::test_result_shape"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpd::test_result_is_symmetric"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpd::test_non_symmetric_raises"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpd::test_non_positive_diagonal_raises"
        status: pass
    human_judgment: false
  - id: D3
    description: "Spherical returns (d,) unit-norm vector; non-unit-norm input raises ValueError"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpherical::test_result_shape"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanSpherical::test_result_is_unit_norm"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanInvalidSpace::test_bad_norm_spherical_raises"
        status: pass
    human_judgment: false
  - id: D4
    description: "Correlation returns (d,d) unit-diagonal array; non-unit-diagonal input raises ValueError"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanCorrelation::test_result_shape"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanCorrelation::test_result_unit_diagonal"
        status: pass
      - kind: unit
        ref: "tests/test_frechet.py::TestFrechetMeanCorrelation::test_non_unit_diagonal_raises"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-03
status: complete
---

# Phase 69 Plan 03: Frechet Mean Monomorphized Dispatch Summary

**`frechet_mean` bound with monomorphized SPD/spherical/correlation string dispatch, per-space column-major marshalling, structural validation, and a ValueError wildcard arm — 35 tests green**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-03T19:39:30Z
- **Completed:** 2026-09-03T19:42:06Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `frechet_mean(objects, space, d, weights=None)` bound as a `#[pyfunction]` with monomorphized `match space { ... }` dispatch — concrete `frechet_mean::<SpdMatrixSpace>`, `frechet_mean::<SphericalSpace>`, `frechet_mean::<CorrelationMatrixSpace>` per arm (no trait objects)
- Per-space input marshalling: `spd_object_from_numpy` and `corr_object_from_numpy` flatten (d,d) numpy arrays to column-major `Vec<f64>`; `spherical_object_from_numpy` extracts (d,) arrays
- In-binding structural validation before each upstream call: SPD symmetric + positive diagonal; spherical unit-norm (|norm−1| < 1e-6); correlation unit-diagonal (|diag−1| < 1e-8) + symmetric
- Wildcard `_ =>` arm raises `ValueError` listing all three valid names (`spd`, `spherical`, `correlation`) — mandatory per locked STATE decision
- 14 new tests (3 spaces + invalid-space/bad-norm/bad-shape negatives); all 35 `test_frechet.py` tests pass

## Task Commits

1. **Task 1: Bind frechet_mean with monomorphized 3-space dispatch** - `c4c21d5` (feat)
2. **Task 2: Per-space frechet_mean tests** - `e3be19b` (test)

## Files Created/Modified

- `src/frechet_mod.rs` — Appended 4 private helpers + `frechet_mean` `#[pyfunction]` (258 lines added); added `PyArray2` and `PyList` to imports; added `frechet_mean` to `register()`
- `tests/test_frechet.py` — Appended 4 test classes: `TestFrechetMeanSpd`, `TestFrechetMeanSpherical`, `TestFrechetMeanCorrelation`, `TestFrechetMeanInvalidSpace` (143 lines added)

## Decisions Made

- **Monomorphized dispatch** (not trait objects): `MetricSpace` is not object-safe in fdars-core 0.33, so trait-object dispatch would not compile — `match space` with a concrete type per arm is the only valid approach.
- **`d: usize` explicit parameter**: ambient dimension passed explicitly rather than inferred from first object; avoids edge-case panics on empty lists and is clearer at the call site.
- **`PyAny` return type**: SPD/correlation return `PyArray2`, spherical returns `PyArray1` — both converted with `.into_any()` to unify the `PyResult<Bound<'py, PyAny>>` return type.
- **`SpdMetric::Frobenius` only**: no `metric` parameter exposed; Power/LogCholesky deferred per CONTEXT.md locked constraint.
- **Validation in binding**: the upstream `frechet_mean` for Frobenius SPD does not validate positive-definiteness (no Cholesky in the Frobenius path). The binding adds a fast diagonal-positivity check, which catches the most common mistakes without the full O(d³) Cholesky cost.

## Deviations from Plan

None — plan executed exactly as written. The implementation follows §5 of 69-RESEARCH.md verbatim: helper names, flattening loop, validation thresholds, result reshape pattern, and wildcard arm message all match the research spec.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- FRE-01 is complete: `fdars.frechet` submodule exposes all 4 functions (`frechet_anova`, `frechet_global_reg`, `frechet_local_reg`, `frechet_mean`) with correct signatures and 35 passing tests.
- Phase 69 continues with plan 69-04 (density_fda submodule — FRE-02).
- No blockers.

## Self-Check

- `src/frechet_mod.rs` modified: FOUND
- `tests/test_frechet.py` modified: FOUND
- Task 1 commit `c4c21d5`: FOUND
- Task 2 commit `e3be19b`: FOUND
- `pytest tests/test_frechet.py -x -q`: 35 passed

## Self-Check: PASSED

---
*Phase: 69-frechet-regression-density-fda*
*Completed: 2026-09-03*
