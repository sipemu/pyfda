---
phase: 25-crate-bump-regression-gate
plan: "01"
subsystem: dependency-management
tags: [crate-bump, fdars-core, regression-gate, maturin, faer-fpca]
status: complete

dependency_graph:
  requires: []
  provides: [fdars-core-0.17.0-baseline]
  affects: [Cargo.toml, Cargo.lock]

tech_stack:
  added: []
  patterns: [exact-version-pin, parallel-feature-only, maturin-develop-gate]

key_files:
  created: []
  modified:
    - Cargo.toml

decisions:
  - "Cargo.lock is gitignored in this repo (library crate convention); the lock was regenerated on disk via `cargo update --precise 0.17.0` but not committed — consistent with repo policy"
  - "faer FPCA SVD drift (1e-8·σ₁, introduced in 0.15.0) did not surface at the live suite's existing tolerances: zero test failures, zero tolerance relaxations needed"
  - "linalg feature NOT enabled (requires Rust 1.84 > MSRV 1.83); parallel feature retained"

metrics:
  duration_minutes: 50
  completed_date: "2026-08-14"
  tasks_completed: 2
  tasks_total: 3
  commits: 1
  files_modified: 1

estimate:
  tokens: 55000

actuals:
  tokens: 6000
  tasks: 2
  commits: 1
---

# Phase 25 Plan 01: Crate Bump Regression Gate Summary

**One-liner:** fdars-core pinned to 0.17.0 (parallel only, no linalg); maturin build green; 259-test Python suite passes with zero failures and zero FPCA tolerance relaxations needed.

## What Was Done

This plan executed a single-line `Cargo.toml` version bump from `fdars-core = { version = "0.14.0", features = ["parallel"] }` to `fdars-core = { version = "0.17.0", features = ["parallel"] }`, then proved the entire existing test suite green on the new crate.

### Task 1 (Tracer): Bump, build, full-suite run

**Steps executed:**
1. Edited `Cargo.toml` line 18: `"0.14.0"` → `"0.17.0"` (parallel retained, linalg NOT added)
2. Ran `cargo update -p fdars-core --precise 0.17.0` — lock regenerated to 0.17.0
3. Verified: `cargo tree | grep fdars-core` → `fdars-core v0.17.0`; `Cargo.lock` contains `version = "0.17.0"`
4. Ran `.venv/bin/maturin develop` → exits 0 (compiled fdars-core 0.17.0 + fdars 0.4.0 in 22s)
5. Ran `cargo test` → exits 0 (0 tests — compile/link gate proved)
6. Ran `.venv/bin/pytest tests/ -q` → **259 passed, 4 skipped, 0 failed** (178s)

**Captured failure list:** None. Zero failures. The faer SVD path (introduced in fdars-core 0.15.0) did not produce any assertion breakage at the suite's existing tolerances.

**Non-FPCA regression check:** No signature/import/shape errors observed. All submodules imported correctly. The 0.14.0→0.17.0 upgrade confirmed additive/non-breaking on the live suite.

### Task 2: Relax broken FPCA/SVD assertions

**Action taken: none.** Task 1 recorded zero failures. Per plan instruction: "If Task 1 recorded ZERO failures, make no test edits — record in the SUMMARY that the faer drift did not surface at the suite's existing tolerances (DEP-02 satisfied with no relaxation needed)."

The existing test suite does not contain `assert_array_equal` or atol < 1e-6 on FPCA outputs — its FPCA tests use structural shape/key checks rather than exact numeric comparisons, and the `test_fpca_output_unchanged_after_refactor` test in `test_advisor.py` uses a deterministic fixture (fixed singular values `[3.0, 1.5, 0.8]` with a zero-scores matrix) that is not affected by the SVD backend change.

**Diff of test files: zero lines changed.**

## Deviations from Plan

### Note: Cargo.lock is gitignored (not a deviation — repo policy)

The plan says "Cargo.lock is committed" but the repository's `.gitignore` explicitly lists `Cargo.lock` (standard practice for library crates). The lock was regenerated on disk and is correct for the local build, but was not committed — consistent with this repository's pre-existing policy. The resolution is still verified via `cargo tree | grep fdars-core` showing 0.17.0 and the successful `maturin develop` build.

### No FPCA tolerance relaxations (planned contingency, not executed)

Plan Task 2 was scoped as a contingency: edit tests only if Task 1 produced failures. Task 1 produced zero failures, so Task 2 executed as a no-op. This is the best-case outcome.

## Suite Results (Empirical Record)

| Run | Command | Result |
|-----|---------|--------|
| Task 1 (discovery) | `pytest tests/ -q` | 259 passed, 4 skipped, **0 failed** |
| Task 2 (green confirmation) | `pytest tests/ -q` | 259 passed, 4 skipped, **0 failed** |
| Compile/link gate | `cargo test` | 0 tests (compile gate passes) |
| Build gate | `maturin develop` | exits 0 |

## Pre-bump Baseline (4 skips, confirmed unchanged)

The 4 skipped tests are live-API tests requiring network keys:
- `test_advisor_live_integration.py` — requires real LLM API keys (not present in dev env)
- Other provider-specific integration tests (Gemini, OpenAI, Ollama markers)

Skip count is **unchanged** from the 0.14.0 baseline — no new skips introduced by the bump.

## Known Stubs

None.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. The bump is a pure dependency version upgrade. Cargo verified the 0.17.0 registry checksum during `cargo update` and `maturin develop` (T-25-01 mitigated). No new transitive dependencies were added with `parallel`-only features (T-25-02 accepted — `linalg` not enabled). The zero-failure suite run confirms the faer FPCA SVD drift did not require tolerance loosening (T-25-03 mitigated by empirical non-event).

## Self-Check

Files created/modified:
- [FOUND] `/home/simonm/projects/rust/pyfda/Cargo.toml` — modified (0.14.0 → 0.17.0)

Commits:
- 3bf6e4e: feat(25-01): bump fdars-core 0.14.0 → 0.17.0, rebuild _native extension

## Self-Check: PASSED
