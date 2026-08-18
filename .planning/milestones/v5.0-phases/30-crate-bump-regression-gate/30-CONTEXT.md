# Phase 30: Crate Bump + Regression Gate - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — smart discuss skipped)

<domain>
## Phase Boundary

`fdars-core` is pinned at 0.20.0 and the entire existing binding + advisor suite still passes, on a green baseline, before any new binding work begins. This phase makes exactly the sole numeric/dependency change and proves the existing surface is unaffected — no new bindings, no new tests, no tolerance relaxations. Covers DEP-03 and DEP-04.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase (crate version bump + compile-fix + regression gate). Guided by the research (`.planning/research/`) and the v4.0 Phase 25 precedent, the shape is already fully determined:

- Bump `Cargo.toml`: `fdars-core = { version = "0.20.0", features = ["parallel"] }` (was `0.17.0`). Do NOT enable `linalg` (needs Rust 1.84 > MSRV 1.83). 0.18 was never published; 0.17 → 0.20 is a direct path.
- 0.20 made `CvCriterion` `#[non_exhaustive]`. The EXISTING `optim_bandwidth` binding's `match` on `CvCriterion` will NOT compile without a wildcard fallback arm — add `_ => Err(PyValueError::new_err(...))` (mirrors the existing `InterpolationMethod`/`BasisCriterion` string-dispatch fallback pattern). This is a compile prerequisite, not new behavior.
- Rebuild via `maturin develop`; regenerate `Cargo.lock` on disk (Cargo.lock is gitignored per repo policy — do not commit it).
- Run the full existing binding + advisor suite (~426 tests). It must pass unchanged — no new tests, no tolerance changes. If any faer/FPCA numeric drift surfaces (it did not in v4.0's 0.14→0.17 bump), relax only the minimum FPCA tolerances and record it — but the expectation is zero changes.
- Land as an isolated commit before any Phase 31/32/33 binding work, so a downstream binding issue cannot hide behind an upgrade regression.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Cargo.toml:18` — current pin `fdars-core = { version = "0.17.0", features = ["parallel"] }`.
- `src/smoothing_mod.rs` — the `optim_bandwidth` binding with the `CvCriterion` match that needs the wildcard arm (confirm exact location at plan time).
- Established string-enum dispatch + `#[non_exhaustive]` fallback pattern already used across `src/*_mod.rs` (e.g. `InterpolationMethod`, `BasisCriterion`).

### Established Patterns
- Crate-bump-as-isolated-regression-gate (v4.0 Phase 25): bump → maturin → full suite green as the sole gate, zero test changes.
- `.planning/codebase/` holds the codebase map; `.planning/research/{STACK,PITFALLS}.md` detail this bump.

### Integration Points
- Build: `maturin develop` in the project venv; test: full `pytest` suite (~426 tests). Docs build not exercised in this phase.

</code_context>

<specifics>
## Specific Ideas

No specific requirements beyond the research-verified plan — infrastructure phase. See `.planning/research/STACK.md` (MSRV 1.81 safe, zero new deps) and `.planning/research/PITFALLS.md` (CvCriterion non-exhaustive compile trap) for the verified details.

</specifics>

<deferred>
## Deferred Ideas

None — infrastructure phase, stayed within scope.

</deferred>
