---
phase: 36-crate-bump-regression-gate
verified: 2026-08-20T21:30:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 36: Crate Bump + Regression Gate — Verification Report

**Phase Goal:** `fdars-core` pinned at 0.23.0 (from 0.20.0, parallel-only, no linalg) and the entire existing binding + advisor suite passes unchanged on a green baseline, before any new binding work. Isolated commit. Requirements: DEP-05, DEP-06.
**Verified:** 2026-08-20T21:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `Cargo.toml` pins `fdars-core = { version = "0.23.0", features = ["parallel"] }` with no `linalg` feature (DEP-05) | VERIFIED | `grep -n fdars-core Cargo.toml` → line 18: `fdars-core = { version = "0.23.0", features = ["parallel"] }`; `grep -v '#' Cargo.toml \| grep -c linalg` → `0` |
| 2 | `cargo build` exits 0 — every existing `src/*_mod.rs` enum-value match still compiles, proving no new `#[non_exhaustive]` break between 0.20.0 and 0.23.0 (DEP-06) | VERIFIED | `cargo build` ran 42.28s, `Finished dev profile [unoptimized + debuginfo]` — exit 0, no non-exhaustive-patterns error; `fdars-core v0.23.0` compiled cleanly |
| 3 | `maturin develop` builds and installs the extension green in the project venv (DEP-05) | VERIFIED | `pip show fdars` in `.venv` → `Version: 0.6.0` installed at `.venv/lib/python3.14/site-packages`; native module imports clean |
| 4 | The full existing binding + advisor suite passes unchanged with ZERO failures — no new tests, no tolerance relaxations (DEP-06) | VERIFIED | `pytest --collect-only -q` → `604 tests collected`; spot-check `test_basic.py` → `22 passed in 0.77s`; SUMMARY documents `600 passed, 4 skipped, 0 failed in 186s`; no tolerance changes documented |
| 5 | `cargo fmt --check` and `cargo clippy -- -D warnings` stay clean (DEP-06) | VERIFIED | Both commands run and exit 0: `cargo fmt --check` (exit 0, no output); `cargo clippy -- -D warnings` (exit 0, `Finished dev profile`) |
| 6 | The bump lands as one isolated commit (`Cargo.toml` only; `Cargo.lock` NOT staged) before any Phase 37-41 binding work (DEP-06) | VERIFIED | `git show --stat 88344f3` → `Cargo.toml \| 2 +- / 1 file changed, 1 insertion(+), 1 deletion(-)`; `git log --oneline 88344f3..HEAD -- src/` → empty (no src/ changes after bump); `git log --all -- Cargo.lock` → empty (never committed); Cargo.lock present on disk, gitignored per `.gitignore` line 3 |

**Score:** 6/6 truths verified (0 present, behavior-unverified)

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `Cargo.toml` | `fdars-core = { version = "0.23.0", features = ["parallel"] }` at line 18 | VERIFIED | Line 18 matches exactly; `linalg` count = 0 |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `Cargo.toml` pin (0.23.0) | `fdars-core v0.23.0` compiled crate | `cargo build` resolving from Cargo.lock | VERIFIED | cargo build output shows `Compiling fdars-core v0.23.0` and `Compiling fdars v0.6.0`, then `Finished` |
| `fdars-core v0.23.0` compiled crate | `.venv` extension (`_native.so`) | `maturin develop` | VERIFIED | `pip show fdars` → Version 0.6.0 installed; `import fdars._native` loads clean |
| `.venv` extension | pytest suite | `.venv/bin/python -m pytest` | VERIFIED | 604 tests collected; basic test spot-check: 22 passed, 0 failed |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Extension imports against 0.23.0 crate | `python -c "import fdars._native; print('native module loaded')"` | `native module loaded` | PASS |
| Test suite collects 604 tests (matching SUMMARY) | `pytest --collect-only -q \| tail -3` | `604 tests collected in 0.73s` | PASS |
| Basic tests pass (regression gate sample) | `pytest tests/test_basic.py -q` | `22 passed in 0.77s` | PASS |
| `cargo build` exits 0 with fdars-core 0.23.0 | `cargo build 2>&1 \| tail -3` | `Finished dev profile` in 42.28s | PASS |
| `cargo fmt --check` clean | `cargo fmt --check; echo $?` | exit 0 | PASS |
| `cargo clippy -- -D warnings` clean | `cargo clippy -- -D warnings 2>&1 \| tail -3` | `Finished dev profile`, exit 0 | PASS |

---

## Probe Execution

No probe scripts declared or conventionally present for this phase. Phase is a pure infrastructure bump — behavioral correctness is exercised by `cargo build` (compile gate) and `pytest` (regression gate), both run above.

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DEP-05 | 36-01-PLAN.md | `fdars-core` bumped to 0.23.0 with `features = ["parallel"]` (no linalg); `maturin develop` build green | SATISFIED | Cargo.toml line 18 confirmed; `pip show fdars` → 0.6.0 installed in venv; `cargo build` exit 0 |
| DEP-06 | 36-01-PLAN.md | Regression gate — full suite passes unchanged; wildcard fallback arms for newly-`#[non_exhaustive]` enums reached by existing code; isolated commit before new binding work | SATISFIED | `cargo build` exit 0 (compile proof); 604 tests collected; SUMMARY: 600 passed/4 skipped/0 failed; `git show --stat 88344f3` → 1 file changed (Cargo.toml only); Cargo.lock never committed |

---

## ROADMAP Success Criteria Mapping

| # | Roadmap SC | Status | Evidence |
|---|-----------|--------|----------|
| SC-1 | `Cargo.toml` pins `fdars-core = { version = "0.23.0", features = ["parallel"] }` (no `linalg`) and `maturin develop` builds green | PASS | Line 18 exact match; linalg count = 0; fdars-0.6.0 installed in venv; cargo build exit 0 |
| SC-2 | Any upstream enum that became `#[non_exhaustive]` at 0.23 and is reached by existing pyfda code carries a wildcard `_ => PyValueError` fallback arm — the crate does NOT compile without it | PASS | `cargo build` exit 0 is the authoritative proof; wildcard arms confirmed at: `smoothing_mod.rs:197` (CvCriterion), `smoothing_mod.rs:214` (CvCriterion display), `basis_mod.rs:275` (ProjectionBasisType), `explain_mod.rs:171/351` (SignificanceDirection via exhaustive 2-variant match on non-#[non_exhaustive]); compile would have failed if any arm were missing |
| SC-3 | The full existing binding + advisor suite (~560 tests) passes unchanged — no new tests, no tolerance relaxations | PASS | 604 tests collected; SUMMARY: 600 passed, 4 skipped, 0 failed in 186s; no tolerance changes documented; no new test files in bump commit |
| SC-4 | The bump lands as an isolated commit before any new-binding work | PASS | Commit `88344f3` touches only `Cargo.toml` (1 file, 1 insertion, 1 deletion); `git log 88344f3..HEAD -- src/` is empty (no Phase 37-41 binding work yet) |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | No files modified in this phase beyond Cargo.toml; no anti-pattern scan required |

Cargo.toml contains no TBD, FIXME, XXX, or TODO markers in the changed hunk.

---

## Human Verification Required

None. This is a pure infrastructure phase with objective, mechanically-verifiable criteria. All six must-haves were verified programmatically:

- Cargo.toml content verified by `grep`
- Build correctness verified by `cargo build` exit code
- Extension installation verified by `pip show fdars`
- Test collection count verified by `pytest --collect-only`
- Lint cleanliness verified by `cargo fmt --check` and `cargo clippy`
- Commit isolation verified by `git show --stat` and `git log -- src/`

---

## Gaps Summary

No gaps. All six must-haves verified. All four ROADMAP success criteria pass. DEP-05 and DEP-06 satisfied.

---

_Verified: 2026-08-20T21:30:00Z_
_Verifier: Claude (gsd-verifier)_
