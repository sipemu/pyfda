# Phase 36: Crate Bump + Regression Gate - Context

**Gathered:** 2026-08-20
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — smart discuss skipped)

<domain>
## Phase Boundary

`fdars-core` is pinned at 0.23.0 (from 0.20.0) and the entire existing binding + advisor suite still passes on a green baseline, before any new binding work begins. Scope is the version pin + rebuild + any wildcard fallback arms needed for newly-`#[non_exhaustive]` upstream enums reached by existing code. No new bindings, no new tests, no tolerance relaxations. Isolated commit before Phases 37–41.

Requirements: DEP-05, DEP-06.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase (crate upgrade + regression gate). Guided by the ROADMAP phase goal, success criteria, the research SUMMARY.md, and codebase conventions.

Established facts from research (`.planning/research/STACK.md`, `SUMMARY.md`):
- Bump is a single-field `Cargo.toml` change: `fdars-core = { version = "0.23.0", features = ["parallel"] }` (from `0.20.0`). Keep `parallel`, do NOT enable `linalg` (still gates only `ridge_regression_fit`; still wants Rust 1.84+ > MSRV 1.83).
- MSRV of fdars-core 0.23.0 is 1.81 (≤ pyfda 1.83) — bump is unblocked.
- Upstream 0.21/0.22/0.23 changes are additive/non-breaking; transitive dependency graph is additive-only (single-field diff upstream).
- Any upstream enum reached by *existing* pyfda code that became `#[non_exhaustive]` at 0.23 needs a wildcard `_ => PyValueError` fallback arm (the crate will not compile without it) — v5.0 Phase 30 hit this with `CvCriterion`.
- The full existing binding + advisor suite (~560 tests) passing unchanged is the sole success criterion.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/convert.rs` — `to_pyresult()` / `to_pyerr()` conversion helpers used by every binding.
- The v5.0 Phase 30 precedent (`.planning/milestones/v5.0-phases/30-*`) — the immediately-prior identical bump (0.17→0.20) that added a `CvCriterion` wildcard arm. Direct template.

### Established Patterns
- Crate version pinned in `Cargo.toml`; build via `maturin develop`.
- Regression gate = existing pytest suite (~560 tests) green with zero changes.
- String-dispatch match helpers over `#[non_exhaustive]` enums carry a wildcard `_ => PyValueError::new_err(...)` arm.

### Integration Points
- `Cargo.toml` (version pin), `Cargo.lock` (regenerated), any `src/*_mod.rs` match arm over a newly-`#[non_exhaustive]` upstream enum reached by existing bindings.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase. Refer to the ROADMAP phase description, its 4 success criteria, and `.planning/research/SUMMARY.md`.

</specifics>

<deferred>
## Deferred Ideas

None — infrastructure phase. All new-binding work is scoped to Phases 37–41.

</deferred>
