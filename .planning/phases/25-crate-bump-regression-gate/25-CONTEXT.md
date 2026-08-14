# Phase 25: Crate Bump + Regression Gate - Context

**Gathered:** 2026-08-14
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — smart discuss skipped)

<domain>
## Phase Boundary

Upgrade the pinned `fdars-core` dependency from 0.14.0 to 0.17.0 and prove the entire existing binding + advisor suite green on the new engine BEFORE any new binding work begins. This phase changes no public API and adds no new bindings — it isolates the sole numeric behavior change introduced upstream (the faer FPCA SVD path, whose results are equivalent only within `1e-8·σ₁`) so that Phases 26–29 build on a known-green baseline.

Delivers (DEP-01, DEP-02):
- `Cargo.toml` pins `fdars-core = "0.17.0"` with the `parallel` feature retained and `linalg` NOT enabled (MSRV 1.83 preserved).
- `Cargo.lock` regenerated and committed; `maturin develop` builds the extension green.
- The full existing Rust + Python test suite (259+ tests) passes against 0.17.0, with FPCA-related exact-equality tolerances relaxed to absorb the `1e-8·σ₁` drift.
- Confirmation (against the live suite, not assumed) that the additive/non-breaking 0.15→0.17 diff disturbs no existing binding signature or public behavior.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure/upgrade phase. Guidance from research (`.planning/research/SUMMARY.md`, `STACK.md`, `PITFALLS.md`):
- The Cargo change is a single line: `version = "0.14.0"` → `"0.17.0"`. Caret semantics (`^0.14.0` = `<0.15.0`) mean the lock never resolves 0.17 without this explicit bump.
- Keep `features = ["parallel"]`; do NOT add `linalg` (needs Rust 1.84 > pyfda MSRV 1.83; WASM-incompatible; no exclusively-gated public API).
- No new Rust or Python dependencies expected ("no new dependencies" per upstream 0.15/0.16 notes).
- When relaxing FPCA tolerances, prefer the minimal change that absorbs the documented `1e-8·σ₁` drift (e.g. `atol≈1e-6`), scoped to the affected FPCA/SVD-derived assertions and any exact-equality doc fences — do not blanket-loosen unrelated tests.
- Discover the empirical drift magnitude by running the suite; adjust only what actually breaks.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Cargo.toml` — the single dependency pin to edit; `pyproject.toml` — extras (unchanged this phase).
- Build/test harness: `maturin develop` for the extension; `cargo test` for Rust; `pytest` for Python. `DOCS_FAST` helper and the docs doc-test harness exist but docs are out of scope until Phase 29.
- Codebase maps in `.planning/codebase/` (STACK, TESTING, CONCERNS) and research reports in `.planning/research/`.

### Established Patterns
- Thin PyO3 wrappers in `src/*_mod.rs` over `fdars_core::*`; `src/convert.rs` marshals numpy(row-major)↔FdMatrix(column-major); errors via `to_pyresult()`.
- Advisor suite in `python/fdars/advisor/` + MCP in `python/fdars/mcp/` with a guard-sync test — must stay green through the bump (no changes expected this phase).

### Integration Points
- The bump touches only `Cargo.toml` + `Cargo.lock`; everything else is verification. FPCA-derived outputs (`fdata_to_pc_1d` and downstream FPCA/SPM aspects) are the surfaces where the faer SVD drift can surface in tests.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure/upgrade phase. The gate is: bump applied, extension builds, full suite green with minimally-relaxed FPCA tolerances, and a confirmed no-behavior-change for existing bindings.

</specifics>

<deferred>
## Deferred Ideas

None — all new bindings, advisor extension, and docs are explicitly later phases (26–29). Enabling `linalg` / raising MSRV to 1.84 is out of scope (see REQUIREMENTS.md Out of Scope).

</deferred>
