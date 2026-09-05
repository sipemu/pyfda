# Phase 66: Isolated Crate Bump + Regression Gate - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — smart discuss skipped)

<domain>
## Phase Boundary

The pinned `fdars-core` crate moves 0.23.0 → 0.33.0 on a proven-green baseline. This
phase isolates the sole numeric change (a 10-minor drift jump) from all binding work so
that binding-correctness issues in later phases cannot hide behind an upgrade regression.

In scope:
- Bump `fdars-core` to `0.33.0` (parallel feature only, no linalg) in `Cargo.toml` + `Cargo.lock`
- `maturin develop` builds green (MSRV 1.83 unchanged)
- Full existing Python suite (~772 tests) passes with zero new failures; document any numeric-tolerance change (expected: none)
- Record a 0.24→0.33 changelog + API audit confirming every existing `match`-arm / enum-variant string in `src/*_mod.rs` still exists at 0.33; flag the four 0.30-deprecated 2D depth functions for later migration

Out of scope (hard boundary):
- NO new bindings
- NO test edits
- Only `Cargo.toml` and `Cargo.lock` change

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — this is a pure infrastructure /
upgrade phase (dependency bump + regression gate). Use the ROADMAP phase goal, success
criteria, and codebase conventions to guide decisions. The one non-negotiable is the
scope boundary: only `Cargo.toml` / `Cargo.lock` may change, and the full test suite is
the regression gate (`cargo build` alone is insufficient — run the ~772-test Python suite).

</decisions>

<code_context>
## Existing Code Insights

- `Cargo.toml` pins `fdars-core` at 0.23.0 (parallel feature); this is the only version bump.
- Enum/`match`-arm strings live in `src/*_mod.rs` (18 modules) — the API audit checks these against 0.33.
- Four 0.30-deprecated 2D depth functions must be flagged (not migrated) here — migration is later-phase work.
- Codebase context will be gathered in more detail during plan-phase research.

</code_context>

<specifics>
## Specific Ideas

- 10-minor jump (0.23→0.33) triples silent numeric-drift risk vs prior 3-minor waves — the full Python suite is the gate, not `cargo build`.
- 0.31/0.32 changelog was absent from the published CHANGELOG and some 0.33 config-struct fields 404'd on docs.rs; confirm result-struct / config field names against 0.33 source during the audit.

</specifics>

<deferred>
## Deferred Ideas

- Migration of the four 0.30-deprecated 2D depth functions — flagged here, migrated in a later phase.
- All new-binding work (fts, regression, Fréchet/density, multi-domain/FAMM, shapelet/GAK) — Phases 67–71.

</deferred>
