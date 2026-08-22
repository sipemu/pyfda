---
phase: 36-crate-bump-regression-gate
plan: "01"
subsystem: infra
tags: [cargo, fdars-core, pyo3, maturin, pytest, regression-gate]

# Dependency graph
requires: []
provides:
  - fdars-core pinned at 0.23.0 (parallel-only, no linalg) with maturin develop green
  - Full pytest suite (600 passed, 4 skipped, 0 failed) against rebuilt 0.23.0 extension
  - cargo fmt --check and cargo clippy -D warnings clean
  - Isolated bump commit (Cargo.toml only; Cargo.lock NOT committed) establishing green baseline for Phases 37-41
affects: [37-regression-bindings, 38-pace-fpca-bindings, 39-outlier-bindings, 40-monitoring-bindings, 41-inference-bindings]

# Actuals (#2632)
actuals:
  tokens: 134
  tasks: 2
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-field Cargo.toml bump for fdars-core version upgrades (parallel-only, no linalg)"
    - "maturin develop (not cargo build alone) used for extension rebuild to exercise real regression gate"
    - "Cargo.lock gitignored and never committed; only Cargo.toml staged for bump commits"

key-files:
  created: []
  modified:
    - Cargo.toml

key-decisions:
  - "Do NOT enable linalg feature: it requires Rust 1.84+ (above pyfda MSRV 1.83) and activates faer/anofox-regression; parallel-only is sufficient for Phases 37-41"
  - "No src/*.rs edits required: enum-site audit confirmed all five existing match sites already have wildcard arms or match non-#[non_exhaustive] enums; 0.20.0-to-0.23.0 diff is additive-only for existing pyfda code"
  - "Single isolated commit for the bump before any Phase 37-41 binding work, per DEP-06 isolation requirement"

patterns-established:
  - "Bump-then-gate pattern: pin Cargo.toml version, cargo build to prove compile correctness, maturin develop to install extension, pytest to gate regression"

requirements-completed: [DEP-05, DEP-06]

coverage:
  - id: D1
    description: "fdars-core pinned at 0.23.0 (parallel-only) in Cargo.toml with no linalg token; cargo build exits 0 proving no non-exhaustive match break"
    requirement: DEP-05
    verification:
      - kind: integration
        ref: "cargo build (exit 0, no non-exhaustive patterns error)"
        status: pass
    human_judgment: false
  - id: D2
    description: "maturin develop rebuilds and installs fdars-0.6.0 into .venv against fdars-core 0.23.0"
    requirement: DEP-05
    verification:
      - kind: integration
        ref: "maturin develop (exit 0, Installed fdars-0.6.0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full pytest suite: 600 passed, 4 skipped, 0 failures against rebuilt 0.23.0 extension"
    requirement: DEP-06
    verification:
      - kind: integration
        ref: ".venv/bin/python -m pytest tests/ -q (600 passed, 4 skipped, 0 failed in 186s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "cargo fmt --check and cargo clippy -- -D warnings both exit 0 (no Rust source changed)"
    requirement: DEP-06
    verification:
      - kind: integration
        ref: "cargo fmt --check (exit 0); cargo clippy -- -D warnings (exit 0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Isolated bump commit: only Cargo.toml staged; Cargo.lock NOT committed"
    requirement: DEP-06
    verification:
      - kind: other
        ref: "git diff --cached --name-only showed only Cargo.toml (1 file, 1 insertion, 1 deletion)"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-08-20
status: complete
---

# Phase 36 Plan 01: Crate Bump + Regression Gate Summary

**fdars-core bumped 0.20.0 to 0.23.0 (parallel-only, no linalg); 600 pytest tests pass green against rebuilt PyO3 extension with no tolerance changes and no src/*.rs edits**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-20T20:47:00Z
- **Completed:** 2026-08-20T20:52:26Z
- **Tasks:** 2
- **Files modified:** 1 (Cargo.toml only)

## Accomplishments

- Bumped fdars-core dependency pin from 0.20.0 to 0.23.0 in Cargo.toml (single-field change, features=["parallel"], no linalg)
- cargo build exits 0 confirming no non-exhaustive match break in any of the five existing enum-value match sites (CvCriterion, ProjectionBasisType, BasisCriterion, SignificanceDirection, Option<T>) per the compile-break audit in 36-RESEARCH.md
- maturin develop rebuilt and installed fdars-0.6.0 into .venv against fdars-core 0.23.0
- Full regression gate: 600 passed, 4 skipped, 0 failed in 186s — zero tolerance changes and zero new tests required
- cargo fmt --check and cargo clippy -- -D warnings both clean (trivially, as no Rust source was modified)
- Isolated bump commit: only Cargo.toml staged; Cargo.lock regenerated on disk but NOT committed (gitignored per policy)

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump fdars-core 0.20.0 to 0.23.0 and rebuild extension end-to-end via maturin develop** - `88344f3` (chore)

Task 2 (regression gate + lint checks) verified against the same Task 1 commit — no additional source changes required.

## Files Created/Modified

- `Cargo.toml` - fdars-core version string changed from "0.20.0" to "0.23.0" (line 18, one-line diff)

## Decisions Made

- Do NOT enable linalg feature: activates faer 0.23 and anofox-regression 0.4 which require Rust 1.84+ (above pyfda MSRV 1.83); parallel-only is the correct pin for Phases 37-41
- No src/*.rs edits required: the 36-RESEARCH.md compile-break audit confirmed all five existing enum-value match sites already have wildcard arms or match non-#[non_exhaustive] enums; all new #[non_exhaustive] annotations in the 0.20.0→0.23.0 diff are on NEW types (GlmFamily, PaceFpcaResult, TvdMssOutliers, etc.) not yet matched by any existing pyfda binding code

## Deviations from Plan

None - plan executed exactly as written. The compile-break audit prediction held: zero wildcard arms needed, zero tolerance changes in the test suite, one isolated Cargo.toml commit.

## Issues Encountered

None. The bump went cleanly:
- cargo build: clean compile on first attempt (43.82s)
- maturin develop: installed fdars-0.6.0 on first attempt (8.85s build + install)
- pytest: 600 passed, 4 skipped, 0 failed on first run (186s)
- cargo fmt + clippy: both clean (no Rust source changed)

## Known Stubs

None — this is a pure infrastructure phase with no user-facing output.

## Next Phase Readiness

- Green 0.23.0 baseline is established; Phases 37-41 can now add new bindings onto this foundation
- Any future regression in Phases 37-41 is isolated to the new binding work, not the version bump
- Test count is now 600 passed / 4 skipped (up from 558 passed / 1 skipped cited in research — 4 additional live-provider tests counted as skipped rather than excluded in this run)

---
*Phase: 36-crate-bump-regression-gate*
*Completed: 2026-08-20*

## Self-Check: PASSED

- FOUND: Cargo.toml (fdars-core = { version = "0.23.0", features = ["parallel"] })
- FOUND: .planning/phases/36-crate-bump-regression-gate/36-01-SUMMARY.md
- FOUND commit 88344f3 (chore(36-01): bump fdars-core 0.20.0 -> 0.23.0)
