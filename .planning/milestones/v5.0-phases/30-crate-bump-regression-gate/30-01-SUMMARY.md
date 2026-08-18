---
phase: 30-crate-bump-regression-gate
plan: 01
subsystem: infra
tags: [rust, pyo3, fdars-core, cargo, maturin, regression-gate]

requires: []
provides:
  - "fdars-core pinned at 0.20.0 (parallel-only, no linalg) in Cargo.toml"
  - "CvCriterion #[non_exhaustive] wildcard fallback arm in optim_bandwidth (smoothing_mod.rs)"
  - "Green baseline: 426 passed / 4 skipped / 0 failed against the rebuilt extension"
affects:
  - "31-inference-bindings"
  - "32-depth-boxplot-bindings"
  - "33-basis-smoothing-bindings"

actuals:
  tokens: 17
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Non-exhaustive enum fallback: _ => \"unknown\" arm on enum-to-string CvCriterion match in optim_bandwidth — same pattern as InterpolationMethod and BasisCriterion elsewhere in the codebase"

key-files:
  created: []
  modified:
    - Cargo.toml
    - src/smoothing_mod.rs

key-decisions:
  - "Do NOT enable linalg feature (requires Rust 1.84 > MSRV 1.83; pulls faer + anofox-regression; not needed for v5.0 Groups A/B/C)"
  - "Bump lands as a single isolated commit (Cargo.toml + smoothing_mod.rs only; Cargo.lock gitignored, not committed) before any Phase 31/32/33 binding work"
  - "No tolerance relaxations required: 0.17.0 -> 0.20.0 bump produced zero numeric drift on existing suite, matching the v4.0 0.14->0.17 pattern"

patterns-established:
  - "Isolated crate bump commit pattern: pin change + compile-fix land together, suite gate is a separate verification step (no new tests committed in this phase)"

requirements-completed: [DEP-03, DEP-04]

coverage:
  - id: D1
    description: "fdars-core pinned at 0.20.0 (parallel-only) in Cargo.toml; linalg feature absent"
    requirement: DEP-03
    verification:
      - kind: integration
        ref: "grep 'fdars-core = { version = \"0.20.0\", features = [\"parallel\"] }' Cargo.toml && ! grep linalg Cargo.toml && cargo build exits 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "CvCriterion #[non_exhaustive] wildcard fallback arm in optim_bandwidth enum-to-string match"
    requirement: DEP-04
    verification:
      - kind: integration
        ref: "cargo build exits 0 (no 'non-exhaustive patterns' error); cargo clippy -- -D warnings exits 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full existing binding + advisor suite (426 passed / 4 skipped / 0 failed) passes unchanged"
    requirement: DEP-04
    verification:
      - kind: integration
        ref: ".venv/bin/python -m pytest -q — 426 passed, 4 skipped in 109.73s"
        status: pass
    human_judgment: false
  - id: D4
    description: "cargo fmt --check and cargo clippy -- -D warnings both clean on edited Rust"
    requirement: DEP-04
    verification:
      - kind: integration
        ref: "cargo fmt --check exits 0; cargo clippy -- -D warnings exits 0"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-08-17
status: complete
---

# Phase 30 Plan 01: Crate Bump Regression Gate Summary

**fdars-core pinned at 0.20.0 (parallel-only) with CvCriterion #[non_exhaustive] wildcard arm; 426-test regression baseline confirmed green with zero numeric drift**

## Performance

- **Duration:** ~4 min (build 16s + test suite 110s)
- **Started:** 2026-08-17T13:15:35Z
- **Completed:** 2026-08-17T13:19:15Z
- **Tasks:** 2 (tracer + gate)
- **Files modified:** 2 (Cargo.toml, src/smoothing_mod.rs)

## Accomplishments

- Bumped `fdars-core` from 0.17.0 to 0.20.0 (parallel feature only; linalg excluded per MSRV 1.83 constraint)
- Added `_ => "unknown"` wildcard arm to the enum-to-string `CvCriterion` match in `optim_bandwidth` (smoothing_mod.rs line 212), satisfying 0.20.0's `#[non_exhaustive]` compile requirement; the string-to-enum direction already had a wildcard `_` arm (returns `PyValueError`) and required no change
- `maturin develop` built the extension green in `.venv` (16.12s); `cargo build`, `cargo fmt --check`, `cargo clippy -- -D warnings` all exit 0
- Full test suite: **426 passed, 4 skipped, 0 failed** — identical to the v4.0 close baseline; zero numeric drift, zero tolerance relaxations
- `Cargo.lock` regenerated on disk but NOT committed (gitignored per repo policy)

## Task Commits

1. **Task 1 (tracer): Bump fdars-core 0.17.0 -> 0.20.0 + CvCriterion wildcard arm** - `1f7a0fb` (feat)

Task 2 (regression gate + lint verification) produced no new source changes — it validated the work committed in Task 1 and is documented here in the SUMMARY.

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `Cargo.toml` - fdars-core version string changed from `"0.17.0"` to `"0.20.0"`; no other change
- `src/smoothing_mod.rs` - Added `_ => "unknown"` wildcard arm to the `result.criterion` enum-to-string match in `optim_bandwidth` (line 212); no other change

## Decisions Made

- Do NOT enable `linalg` feature: requires Rust 1.84 which exceeds pyfda's MSRV 1.83; also pulls in `faer` and `anofox-regression` as new transitive deps; not needed for any v5.0 Group A/B/C binding target
- Single isolated bump commit before any Phase 31/32/33 binding work; `Cargo.lock` gitignored and not staged
- No tolerance relaxations: zero numeric drift on the 0.17->0.20 bump (matching the v4.0 0.14->0.17 pattern where zero changes were also needed)

## Deviations from Plan

None - plan executed exactly as written.

The string-to-enum `CvCriterion` direction (match on `criterion: &str`) already had a wildcard `_ => return Err(PyValueError...)` arm in the pre-bump code (lines 193-200), so it was already forward-compatible with `#[non_exhaustive]`. Only the enum-to-string direction (match on `result.criterion`) needed the new `_ => "unknown"` arm. The plan's task description correctly identified both directions; only one needed a code change.

## Issues Encountered

None. The build was clean on the first attempt; the suite passed on the first run.

## Regression Gate Results

| Metric | Expected | Actual | Pass? |
|--------|----------|--------|-------|
| pytest passed | ~426 | 426 | YES |
| pytest skipped | 4 | 4 | YES |
| pytest failed | 0 | 0 | YES |
| cargo build | exit 0 | exit 0 | YES |
| cargo fmt --check | exit 0 | exit 0 | YES |
| cargo clippy -D warnings | exit 0 | exit 0 | YES |
| maturin develop | exit 0 | exit 0 | YES |
| Cargo.lock committed | NO | NOT committed | YES |
| linalg in Cargo.toml | NO | absent | YES |
| FPCA tolerance relaxations | 0 | 0 | YES |

## Known Stubs

None — this phase introduces no Python surface changes.

## Threat Flags

None — only a version bump of an existing first-party dependency (same maintainer, sipemu). No new packages, no new network endpoints, no new trust boundaries. See threat model in PLAN.md for T-30-01/T-30-02 (both accepted).

## Next Phase Readiness

- Phase 30 is complete and the green baseline is established
- Phases 31, 32, and 33 are now unblocked: the `CvCriterion` compile blocker is resolved, and the regression gate confirms the bump introduced no regressions
- The `CvCriterion::Aic` variant (visible but not yet bound) will be wired in Phase 33 Group C basis/smoothing bindings

---
*Phase: 30-crate-bump-regression-gate*
*Completed: 2026-08-17*
