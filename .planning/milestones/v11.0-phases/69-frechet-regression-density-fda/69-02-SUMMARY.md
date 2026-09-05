---
phase: 69-frechet-regression-density-fda
plan: "02"
subsystem: frechet
tags: [rust, pyo3, frechet, density-fda, regression, anova, fdars-core-0.33]

# Dependency graph
requires:
  - phase: 69-frechet-regression-density-fda
    plan: "01"
    provides: convert::extract_ragged_vecs in convert.rs
provides:
  - fdars.frechet submodule registered end-to-end
  - frechet_anova binding (9-key PyDict, permutation p-value, group label validation)
  - frechet_global_reg binding (3-key PyDict, predicted shape (N_OUT, M))
  - frechet_local_reg binding (3-key PyDict, required-positional bandwidth)
  - tests/test_frechet.py: 21 tests covering all three functions + negative paths
affects: [69-03, 72-advisor, 73-docs]

# Actuals (#2632)
actuals:
  tokens: 4828   # (17562 + 1750) / 4 — chars over changed files
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Density-default Fréchet binding: numpy2d_to_fdmatrix for 2D I/O, 9/3-key PyDicts for result structs"
    - "Pre-validate contiguous 0..k group labels before upstream call (Pitfall 4)"
    - "fdmatrix_to_numpy2d preserves (n_out, m) row orientation — no manual transposition needed"

key-files:
  created:
    - src/frechet_mod.rs
    - tests/test_frechet.py
  modified:
    - src/lib.rs
    - python/fdars/__init__.py

key-decisions:
  - "All three functions committed in a single atomic commit: tracer (anova) + expansion (global_reg, local_reg) were implemented together and are inseparable at the file boundary"
  - "frechet_mod.rs uses explicit imports (not crate::convert::*) to keep -D warnings clean — only imports used by plan 69-02; frechet_mean imports added in plan 69-03"
  - "np.trapz deprecated in NumPy 2.x — fixture uses np.trapezoid (Rule 1 auto-fix)"
  - "bandwidth echoed from result.bandwidth field — not the input float — preserves any upstream rounding/clamping"

patterns-established:
  - "Fréchet density-default: all 2D matrix args via numpy2d_to_fdmatrix; argvals via numpy1d_to_vec; result FdMatrix via fdmatrix_to_numpy2d"
  - "Non-square test fixtures: N=40, M=50, N_OUT=10, N_PRED=2 (all distinct) — asserts exact (N_OUT, M) predicted shape to catch transposition bugs"

requirements-completed: [FRE-01]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "fdars.frechet submodule importable; frechet_anova returns 9-key PyDict with permutation p-value in [0,1]"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: tests/test_frechet.py::TestFrechetAnova
        status: pass
    human_judgment: false
  - id: D2
    description: "frechet_global_reg returns 3-key PyDict; predicted shape (N_OUT, M) not (M, N_OUT) on non-square fixture"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: tests/test_frechet.py::TestFrechetGlobalReg
        status: pass
    human_judgment: false
  - id: D3
    description: "frechet_local_reg returns 3-key PyDict; bandwidth echoed; non-positive bandwidth raises ValueError"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: tests/test_frechet.py::TestFrechetLocalReg
        status: pass
    human_judgment: false
  - id: D4
    description: "Non-contiguous group labels (e.g. [0,1,3]) raise ValueError with actionable message"
    requirement: FRE-01
    verification:
      - kind: unit
        ref: tests/test_frechet.py::TestFrechetAnova::test_non_contiguous_labels_raise
        status: pass
    human_judgment: false

# Metrics
duration: 3min
completed: 2026-09-03
status: complete
---

# Phase 69 Plan 02: Fréchet Submodule Summary

**New `fdars.frechet` submodule with three density-default Fréchet functions (`frechet_anova` 9-key, `frechet_global_reg` / `frechet_local_reg` 3-key) using `numpy2d_to_fdmatrix` I/O; 21 tests pass on non-square (N=40, M=50, N_OUT=10) fixtures**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-03T19:34:38Z
- **Completed:** 2026-09-03T19:37:45Z
- **Tasks:** 3 (tracer + 2 auto/TDD)
- **Files modified:** 4

## Accomplishments

- Created `src/frechet_mod.rs`: `frechet_anova` with 9-key PyDict result + contiguous 0..k group-label pre-validation; `frechet_global_reg` and `frechet_local_reg` with 3-key PyDicts; `register()` wires all three
- Registered `fdars.frechet` end-to-end: `mod frechet_mod;` + `register_submodule!(m, "frechet", frechet_mod::register)` in `lib.rs`; `"frechet"` added to `_submodule_names` in `__init__.py`
- `tests/test_frechet.py`: 21 tests — non-square shape assertions, all 9/3 PyDict key checks, p-value bounds, bandwidth echo, and negative-path ValueError checks; all pass

## Task Commits

1. **Tasks 1-3: register fdars.frechet + bind all 3 density-default functions** - `196d748` (feat)

**Plan metadata:** (docs commit, see below)

## Files Created/Modified

- `src/frechet_mod.rs` (new) — frechet_anova (9-key), frechet_global_reg (3-key), frechet_local_reg (3-key), register()
- `tests/test_frechet.py` (new) — 21 tests: TestFrechetAnova (8), TestFrechetGlobalReg (6), TestFrechetLocalReg (7)
- `src/lib.rs` — added `mod frechet_mod;` + `register_submodule!(m, "frechet", ...)` after scalar_on_function
- `python/fdars/__init__.py` — added `"frechet"` to `_submodule_names`; added Fréchet bullet to docstring

## Decisions Made

- Implemented all three density-default functions in a single frechet_mod.rs rather than phasing anova separately — the file is the atomic unit; commit message labels the tracer + expansion together
- Used explicit imports (not `crate::convert::*`) so plan 69-03 can add `frechet_mean`-specific imports (`PyList`, `PyArray2`) without this plan accumulating unused imports
- `bandwidth` value echoed from `result.bandwidth` (Rust field) not directly from Python input, which is the correct pattern; upstream may clamp or recompute

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] np.trapz deprecated in NumPy 2.x**
- **Found during:** Task 1 (test collection error)
- **Issue:** `np.trapz` is removed in NumPy 2.x — raises `AttributeError: module 'numpy' has no attribute 'trapz'`. The 69-RESEARCH.md fixture code used `np.trapz`.
- **Fix:** Changed to `np.trapezoid` (the stable NumPy 2.x API for the trapezoidal rule)
- **Files modified:** tests/test_frechet.py
- **Verification:** Test collection succeeds; 21 tests pass
- **Committed in:** `196d748` (same commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in test fixture)
**Impact on plan:** Trivial — NumPy API compatibility fix; no scope change.

## Issues Encountered

None — build succeeded on first attempt after the trapezoid fix.

## Self-Check: PASSED

- `src/frechet_mod.rs` exists: FOUND
- `tests/test_frechet.py` exists: FOUND
- `lib.rs` has `mod frechet_mod;`: FOUND (line 32)
- `lib.rs` has `register_submodule!(..., "frechet", ...)`: FOUND (line 68)
- `__init__.py` has `"frechet"`: FOUND (line 60)
- `196d748` exists in git log: FOUND
- 21 tests pass: VERIFIED

## Next Phase Readiness

- `fdars.frechet` submodule ready; plan 69-03 appends `frechet_mean` (generic dispatch: SPD/spherical/correlation) to the same `frechet_mod.rs`
- No blockers

---
*Phase: 69-frechet-regression-density-fda*
*Completed: 2026-09-03*
