---
phase: 25-crate-bump-regression-gate
verified: 2026-08-14T10:06:30Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "Cargo.lock is regenerated and committed (ROADMAP SC1)"
    reason: "Cargo.lock is gitignored by repo policy (.gitignore line 3 — standard library-crate convention). The lock was regenerated on disk and correctly resolves fdars-core to 0.17.0, confirmed via `cargo tree` and direct file inspection. The reproducibility intent of SC1 is fully met; only the 'committed' wording is inapplicable to this repo's explicit policy."
    accepted_by: "verifier (gsd-verifier)"
    accepted_at: "2026-08-14T10:06:30Z"
re_verification: null
---

# Phase 25: Crate Bump + Regression Gate Verification Report

**Phase Goal:** The pinned `fdars-core` is upgraded to 0.17.0 and the entire existing binding + advisor suite proves green on the new engine, isolating the sole numeric behavior change (faer FPCA SVD drift) before any new binding work begins.
**Verified:** 2026-08-14T10:06:30Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `Cargo.toml` pins `fdars-core = "0.17.0"` with `features = ["parallel"]` and `linalg` NOT enabled (DEP-01) | VERIFIED | Line 18: `fdars-core = { version = "0.17.0", features = ["parallel"] }`; `grep -c 'linalg' Cargo.toml` returns 0 |
| 2 | `Cargo.lock` resolves `fdars-core` to 0.17.0 and `maturin develop` builds the extension green (DEP-01) | VERIFIED (override) | Lock on disk resolves to 0.17.0 (`grep -A2 'name = "fdars-core"' Cargo.lock` → `version = "0.17.0"`); Cargo.lock gitignored per repo policy (.gitignore:3) — not committed but correct; `cargo tree` → `fdars-core v0.17.0`; `import fdars` succeeds in venv |
| 3 | Full existing binding + advisor suite passes against 0.17.0 with FPCA tolerances relaxed only where faer drift actually broke assertions (DEP-02) | VERIFIED | SUMMARY records 259 passed / 4 skipped / 0 failed; zero tolerance relaxations applied (faer drift did not surface at existing assertion tolerances); Task 3 human-verify checkpoint approved by user |
| 4 | faer FPCA SVD drift (1e-8·σ₁) did not break any assertion; no test file was modified (DEP-02) | VERIFIED | Commit `3bf6e4e` modifies only `Cargo.toml` (one line); `git diff HEAD~2 HEAD -- tests/` produces empty output — zero test file changes across both phase commits |
| 5 | No existing binding signature or public behavior changed — additive/non-breaking confirmed against live suite (DEP-02) | VERIFIED | SUMMARY: "No signature/import/shape errors observed. All submodules imported correctly." Confirmed by zero non-FPCA failures in the 259-test suite; `import fdars` verified locally |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `Cargo.toml` | Single version-string change `0.14.0 → 0.17.0`, `parallel` retained, `linalg` absent | VERIFIED | Line 18 confirmed; `grep -c linalg` = 0 |
| `Cargo.lock` | Regenerated on disk; resolves `fdars-core` to `0.17.0` | VERIFIED (on-disk) | File present (15398 bytes, modified 2026-08-14); resolves to `0.17.0`; gitignored per repo convention |
| Test files (contingent) | Minimally-relaxed FPCA tolerance edits only if Task 1 produced failures | VERIFIED | No test files modified — zero failures observed in Task 1; correct no-op per plan |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `Cargo.toml` version pin (`0.17.0`) | `Cargo.lock` resolution | `cargo update --precise 0.17.0` | WIRED | Lock on disk shows `version = "0.17.0"` under `name = "fdars-core"` |
| `Cargo.lock` resolution | `_native` extension build | `maturin develop` | WIRED | `import fdars` in `.venv` succeeds; commit message confirms `maturin develop exits 0; compiled fdars-core 0.17.0 + fdars 0.4.0 in 22s` |
| `_native` extension (0.17.0) | `pytest tests/` suite | live import at test time | WIRED | Suite: 259 passed / 4 skipped / 0 failed per SUMMARY + human-verify checkpoint |

---

### Data-Flow Trace (Level 4)

Not applicable — this is a pure infrastructure/dependency upgrade phase. No new data-rendering symbols introduced; no static-return stubs to trace.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| fdars extension imports against 0.17.0 | `.venv/bin/python -c "import fdars; print('import OK')"` | `import OK` | PASS |
| Cargo resolves fdars-core to 0.17.0 | `cargo tree \| grep fdars-core` | `fdars-core v0.17.0` | PASS |
| `linalg` feature NOT enabled | `grep -c 'linalg' Cargo.toml` | `0` | PASS |
| Full pytest suite (SUMMARY evidence + human gate) | `pytest tests/ -q` (run by executor) | 259 passed / 4 skipped / 0 failed | PASS (human-verified, not re-run here) |

---

### Probe Execution

No probe scripts declared in the PLAN for this phase. The regression gate ran as `pytest tests/ -q` during execution (Task 1 + Task 3 human-verify checkpoint). Step 7c: SKIPPED (no `probe-*.sh` files declared or found).

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| DEP-01 | 25-01-PLAN.md | `fdars-core` bumped 0.14.0→0.17.0; `Cargo.lock` regenerated; `parallel` retained; `linalg` NOT enabled | SATISFIED | Cargo.toml line 18 + `cargo tree` + on-disk Cargo.lock |
| DEP-02 | 25-01-PLAN.md | Full suite passes against 0.17.0 with FPCA tolerances relaxed to absorb faer SVD drift | SATISFIED | 259 passed / 4 skipped / 0 failed; zero tolerance relaxations (best-case outcome: drift did not surface) |

No orphaned requirements for Phase 25.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None | — | Only `Cargo.toml` was modified; no Python or Rust source files changed |

No debt-marker comments (`TBD`, `FIXME`, `XXX`) found in `Cargo.toml`. No stub indicators. Diff is a single-line version string change.

---

### Human Verification Required

None. The Task 3 blocking `checkpoint:human-verify` gate (suite green on 0.17.0) was approved by the user prior to submission. No additional human verification items identified.

---

### Gaps Summary

No gaps. All five must-have truths are satisfied by direct codebase evidence.

The single structural deviation — `Cargo.lock` not committed to git — is consistent with the repository's own `.gitignore` policy (line 3 explicitly lists `Cargo.lock`, the standard library-crate convention). The lock is correct on disk, resolves to 0.17.0, and the reproducibility intent of ROADMAP SC1 is met. This is recorded as an accepted override rather than a gap.

The best-case outcome (zero FPCA tolerance relaxations needed) is substantiated by the zero diff on test files, confirmed by git log. The faer SVD drift (1e-8·σ₁, introduced in fdars-core 0.15.0) did not surface because the existing test suite's FPCA assertions use structural shape/key checks rather than sub-1e-6 exact numeric comparisons.

---

**Verdict:** Phase 25 goal is achieved. `fdars-core` is pinned to 0.17.0 with `parallel` only, the lock resolves correctly on disk, the compiled `_native` extension imports cleanly, and the full 259-test suite passed with zero failures and zero test modifications — the cleanest possible regression-gate outcome. All downstream binding work (Phases 26–29) may proceed on this proven baseline.

---

_Verified: 2026-08-14T10:06:30Z_
_Verifier: Claude (gsd-verifier)_
