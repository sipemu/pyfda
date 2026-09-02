---
phase: 66-isolated-crate-bump-regression-gate
plan: 01
subsystem: build
tags: [fdars-core, cargo, maturin, pytest, dependency-bump, regression-gate]

# Dependency graph
requires:
  - phase: none
    provides: clean v6.0 baseline (772-test suite green at fdars-core 0.23.0)
provides:
  - fdars-core 0.33.0 pin in Cargo.toml (parallel only, no linalg)
  - Refreshed Cargo.lock on disk (0.33.0 checksum)
  - Proven zero-drift regression gate (5339 passed, 0 failed)
  - 0.24→0.33 changelog record + per-enum API audit (66-AUDIT.md)
  - Six deprecated call sites suppressed with #[allow(deprecated)] (CONTINGENCY)
affects:
  - phases 67-71 (binding groups) — build on this proven 0.33.0 baseline
  - phases 72-73 (advisor + docs) — depend on 0.33.0 being build-green

# Actuals (#2632)
actuals:
  tokens: 14000
  tasks: 4
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "#[allow(deprecated)] at function level for soft-deprecated upstream calls under RUSTFLAGS=-D warnings"

key-files:
  created:
    - .planning/phases/66-isolated-crate-bump-regression-gate/66-AUDIT.md
  modified:
    - Cargo.toml
    - src/depth_mod.rs
    - src/fdata_mod.rs
    - src/regression_mod.rs

key-decisions:
  - "fdars-core bumped to 0.33.0 (parallel only, no linalg) — sole Cargo.toml change"
  - "CONTINGENCY applied: 6 #[allow(deprecated)] at call sites under RUSTFLAGS=-D warnings (soft-deprecated at 0.33, not removed)"
  - "mean_2d deprecation (fdata_mod.rs) was not in research — discovered at build time; treated identically to the four documented depth functions"
  - "Migration of all 6 deprecated call sites deferred to a later phase — out of scope for Phase 66"
  - "0.31/0.32 changelog gap closed: GAK+kernel-kmeans (additive); 0.33 adds shapelet module only"

patterns-established:
  - "CONTINGENCY pattern: check deprecated-vs-removed before editing src/; add #[allow(deprecated)] at function level only, never globally"

requirements-completed: [DEP-01, DEP-02, DEP-03]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "fdars-core pinned at 0.33.0 (parallel only) in Cargo.toml; Cargo.lock refreshed on disk"
    requirement: DEP-01
    verification:
      - kind: other
        ref: "grep 'fdars-core' Cargo.toml → version = 0.33.0; grep -A2 'name = fdars-core' Cargo.lock → version = 0.33.0"
        status: pass
    human_judgment: false
  - id: D2
    description: "maturin develop --release builds green under RUSTFLAGS=-D warnings; import fdars works; MSRV 1.83 unchanged"
    requirement: DEP-01
    verification:
      - kind: other
        ref: "RUSTFLAGS=-D warnings maturin develop --release exits 0; python -c 'import fdars; print(ok)' → IMPORT_OK"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full Python suite passes with zero new failures against fdars-core 0.33.0"
    requirement: DEP-02
    verification:
      - kind: integration
        ref: "pytest tests/ -x -q → 5339 passed, 10 skipped, 0 failed in 48.84s"
        status: pass
    human_judgment: false
  - id: D4
    description: "0.24→0.33 changelog + per-enum API audit recorded in 66-AUDIT.md; four 0.30-deprecated 2D depth functions flagged"
    requirement: DEP-03
    verification:
      - kind: other
        ref: "grep -qi keywords in 66-AUDIT.md → AUDIT_COMPLETE"
        status: pass
    human_judgment: false

# Metrics
duration: 9min
completed: 2026-09-02
status: complete
---

# Phase 66 Plan 01: Isolated Crate Bump + Regression Gate Summary

**fdars-core bumped 0.23.0→0.33.0 (parallel only) with zero numeric drift confirmed by 5339-test green gate; 6 deprecated call sites suppressed via CONTINGENCY #[allow(deprecated)]; full API audit recorded in 66-AUDIT.md**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-02T13:58:30Z
- **Completed:** 2026-09-02T14:07:30Z
- **Tasks:** 4
- **Files modified:** 4 (Cargo.toml, depth_mod.rs, fdata_mod.rs, regression_mod.rs) + 1 created (66-AUDIT.md)

## Accomplishments

- Bumped `fdars-core` pin from 0.23.0 to 0.33.0 in `Cargo.toml` (single line edit, parallel feature only, no linalg); `cargo update -p fdars-core` refreshed `Cargo.lock` on disk
- Applied CONTINGENCY: `RUSTFLAGS="-D warnings" maturin develop --release` initially failed because 6 deprecated call sites became hard errors; confirmed all 6 are SOFT-deprecated (not removed) at 0.33.0 via registry source read; added minimal `#[allow(deprecated)]` at function level at each call site; build then exits 0
- Discovered `mean_2d` (fdata_mod.rs:45) as a 6th deprecated call site not in the original research list — handled identically to the four documented depth functions
- Full Python suite (5339 tests) passed with zero new failures and zero numeric tolerance changes, confirming no drift across the 10-minor jump
- Wrote `66-AUDIT.md` recording the 0.24→0.33 changelog (closing the 0.31/0.32 gap), per-enum audit with ALL CONFIRMED-PRESENT verdicts, the six flagged deprecated functions, and the CONTINGENCY deviation

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump the fdars-core pin and refresh the lockfile** - `1cce589` (chore)
2. **Task 2: Build gate — maturin develop --release green under CI flags** - `e32878f` (fix — CONTINGENCY)
3. **Task 3: Regression gate — full Python suite, zero new failures** - _(no tracked file changes; gate result recorded in Task 4's 66-AUDIT.md)_
4. **Task 4: API audit + changelog record (66-AUDIT.md)** - `6fe0f62` (docs)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `Cargo.toml` — fdars-core version string changed from 0.23.0 to 0.33.0
- `src/depth_mod.rs` — Added `#[allow(deprecated)]` at fraiman_muniz_2d, modal_2d, random_projection_2d, random_tukey_2d (CONTINGENCY)
- `src/fdata_mod.rs` — Added `#[allow(deprecated)]` at mean_2d (CONTINGENCY — new discovery)
- `src/regression_mod.rs` — Added `#[allow(deprecated)]` at fanova (CONTINGENCY)
- `.planning/phases/66-isolated-crate-bump-regression-gate/66-AUDIT.md` — 0.24→0.33 changelog + full API audit + deprecation flags + CONTINGENCY doc + regression gate result

## Decisions Made

- **CONTINGENCY applied:** Build failed under `RUSTFLAGS="-D warnings"` because 6 deprecated functions became hard errors. Confirmed soft-deprecated (not removed) at 0.33.0 via `~/.cargo/registry/src/.../fdars-core-0.33.0/src/` inspection. Added `#[allow(deprecated)]` at 6 call sites — the minimal, documented deviation per PLAN.md CONTINGENCY spec.
- **mean_2d is a 6th deprecated site:** Not in the original research audit list. `fdars_core::fdata::mean_2d` was deprecated at the same time as the four depth functions (0.30 era, "redundant with `mean(…, Dim::Two)`"). Treated identically — `#[allow(deprecated)]` added; flagged for later migration.
- **Deferred migration:** All 6 deprecated call sites stay as-is. Their replacement (e.g., `mean(…, Dim::Two)`, `fraiman_muniz(…, Dim::Two)`, `fanova_seeded`) uses the new `Dim` enum that was not bound at the time these functions were written. Migration is Phase 67+ work.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added #[allow(deprecated)] to 6 call sites (CONTINGENCY)**
- **Found during:** Task 2 (Build gate)
- **Issue:** `RUSTFLAGS="-D warnings" maturin develop --release` promoted 6 soft-deprecated function calls to hard errors, failing the build
- **Fix:** Added `#[allow(deprecated)]` at the function level (before `#[pyfunction]`) at exactly 6 call sites in 3 files. No global suppression. No migration. Scope: depth_mod.rs (4 fns), fdata_mod.rs (1 fn), regression_mod.rs (1 fn)
- **CONTINGENCY note:** `mean_2d` was an additional deprecated site not listed in the research — discovered at build time; handled identically to the four documented depth functions
- **Files modified:** src/depth_mod.rs, src/fdata_mod.rs, src/regression_mod.rs
- **Verification:** `RUSTFLAGS="-D warnings" maturin develop --release` exits 0; `python -c "import fdars; print('ok')"` → ok
- **Committed in:** e32878f

---

**Total deviations:** 1 auto-fixed (1 build-blocking contingency — documented per PLAN.md)
**Impact on plan:** The `#[allow(deprecated)]` additions were the explicitly anticipated CONTINGENCY. Six lines added across 3 files. No behavior changes. Scope boundary maintained (no migration, no new symbols, no test edits).

## Issues Encountered

- `mean_2d` in `fdata_mod.rs` was soft-deprecated at 0.33.0 but not listed in the research audit table. The research RESEARCH.md listed only the four depth functions plus `fanova`. This was caught cleanly at Task 2 build time. Impact: zero — handled by the same CONTINGENCY mechanism.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 66 COMPLETE: fdars-core 0.33.0 is build-green (RUSTFLAGS="-D warnings"), import-clean, and regression-gate-green (5339 passed / 0 failed)
- Phases 67–71 (binding groups) can now fork from this proven 0.33.0 baseline — the upgrade isolation guarantee holds
- The six deprecated call sites are documented in 66-AUDIT.md; their migration should be included in whichever binding phase touches depth/fdata/regression

---
*Phase: 66-isolated-crate-bump-regression-gate*
*Completed: 2026-09-02*
