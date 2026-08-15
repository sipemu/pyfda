---
gsd_state_version: 1.0
milestone: v4.0
milestone_name: fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs
current_phase: 27
current_phase_name: scoring-metrics-alignment-registration-bindings
status: verifying
stopped_at: Completed 27-02-PLAN.md
last_updated: "2026-08-15T21:36:03.234Z"
last_activity: 2026-08-15
last_activity_desc: Phase 26 complete, transitioned to Phase 27
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 5
  completed_plans: 5
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-13)

**Core value:** Upgrade `fdars-core` 0.14.0→0.17.0, expose the new functional-data capabilities (interpolation/imputation, functional statistics/scoring, shift registration/registration-quality/banded elastic alignment) through PyO3 bindings + the Python API, extend the v3.0 grounded advisor to cover the relevant new capabilities, and document everything method-accurately — with the grounding invariant intact throughout.
**Current focus:** Phase 27 — scoring-metrics-alignment-registration-bindings

## Current Position

Phase: 27 (scoring-metrics-alignment-registration-bindings) — EXECUTING
Plan: 2 of 2
Status: Phase complete — ready for verification
Last activity: 2026-08-15 — Phase 27 execution started

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 3 (this milestone); 19 across v1.0–v3.0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 25 | 1 | - | - |
| 26 | 2 | - | - |
| 27 | TBD | - | - |
| 28 | TBD | - | - |
| 29 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 25 P01 | 50 | 2 tasks | 1 files |
| Phase 26-interpolation-imputation-functional-statistics-bindings P01 | 25min | 3 tasks | 5 files |
| Phase 26-interpolation-imputation-functional-statistics-bindings P02 | 6 minutes | 3 tasks | 3 files |
| Phase 27 P01 | 7m | 2 tasks | 4 files |
| Phase 27 P02 | 364 | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v4.0 roadmap]: Phase numbering CONTINUES from v3.0 (starts at Phase 25; v3.0 ended at Phase 24)
- [v4.0 roadmap]: Crate bump + regression gate FIRST (Phase 25, DEP-01/02) — isolates the sole numeric change (faer FPCA SVD drift, relax FPCA tolerances to `1e-8·σ₁`) and unblocks all binding work
- [v4.0 roadmap]: Phases 26 (REPR + functional-stats) and 27 (scoring + ALGN) are INDEPENDENT binding groups, parallel-eligible after Phase 25; both must precede the advisor
- [v4.0 roadmap]: Advisor extension (Phase 28) depends on the binding phases (calls the bound functions); MCP guard-sync (`_DIAGNOSTICS_METHODS` + `_supported`) must land in a single atomic commit to keep `test_diagnostics_methods_match_advisor_supported` green; `_RUNNABLE_METHODS` unchanged (scoring needs caller-supplied y_true/y_pred)
- [v4.0 roadmap]: Docs LAST (Phase 29) so executed offline fences + diagrams run against the real shipped bindings
- [research]: Do NOT enable `linalg` feature (requires Rust 1.84 > MSRV 1.83); `parallel` retained; 0.15→0.17 perf wins inherited via the bump, no API to bind
- [research]: Enums cross the boundary as string params + `match` arms with a `#[non_exhaustive]` fallback; compound results return as PyDict; `fd.interpolate()`/`fd.impute()` become Fdata methods, stats/scoring stay module-level
- [Phase ?]: Cargo.lock gitignored (library crate convention); regenerated on disk but not committed — consistent with repo policy
- [Phase ?]: faer FPCA SVD drift (1e-8·σ₁, fdars-core 0.15+) did not surface at suite's existing tolerances: zero test failures, zero tolerance relaxations; DEP-02 satisfied
- [Phase ?]: New fdars.represent submodule for interpolation+imputation (per CONTEXT.md locked decision — not extending fdata_mod)
- [Phase ?]: ExtrapolationPolicy/ImputationMethod cross as plain &str + match arms with _ => PyValueError fallback (Python 3.9 safe, no StrEnum)
- [Phase ?]: functional_covariance returns m×m via fdmatrix_to_numpy2d; diagonal==variance guards layout correctness
- [Phase ?]: depth_based_median resolves usize via mat.row(idx); never returns bare int
- [Phase ?]: fd.median() returns Fdata row (n_obs=1) with original argvals, per CONTEXT.md
- [Phase ?]: fdars.scoring: new PyO3 submodule for 5 Simpson-integrated prediction-scoring metrics (STAT-03)
- [Phase ?]: TDD RED/GREEN used for Task 2 expansion of 4 metrics after tracer gate
- [Phase ?]: Bind *_with_band variants (band_frac: Option<f64>=None) NOT *_banded — consistent with CONTEXT.md locked decision; None disables band cleanly
- [Phase ?]: ShiftRegistrationResult marshalled as PyDict {registered_data, shifts} — mirrors karcher_mean dict convention
- [Phase ?]: fd.shift_register() returns (Fdata, ndarray) 2-tuple preserving argvals/rangeval/names/id/metadata

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 25 risk]: faer FPCA SVD drift magnitude on the live suite is unverified (release-note prose, not run) — discover empirically and relax FPCA tolerances (~`atol=1e-6`) before new binding work
- [Phase 26/27 risk]: numpy(row-major)↔FdMatrix(column-major) transposition (#33 class) on every matrix-returning binding (`functional_covariance`, banded distance matrices) — route through `fdmatrix_to_numpy2d`, carry a multi-curve round-trip test
- [Phase 26 risk]: `depth_based_median` returns a `usize` index — resolve to the actual curve row in the binding
- [Phase 27 risk]: all 10 new scoring/quality fns return `Result` — no `.unwrap()`, route through `to_pyresult()`, add ValueError tests (MAPE has no epsilon guard; Sobolev needs a uniform grid); bind `*_with_band` (`band_frac: Option<f64>`) NOT the 0.14 `*_banded`
- [Phase 28 research flag]: guard-sync interdependencies + grounding-invariant patterns for the new aspects/method — deeper planning-time research
- [Phase 29 research flag]: SVGO/determinism gate workflow + per-diagram method-accuracy review checklist
- [Gaps]: module placement (helpers/scoring vs extend fdata/metric) decided in Phase 26/27; confirm `ShiftRegistrationResult` / `impute_missing_values` field names against crate source after the bump

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x (FUT-01) | v2.0 close |
| API coverage | Additional 0.14.0-era upstream methods not in this milestone's three groups (Bayesian/closed-curve/partial-match alignment, GP/covariance kernels) | later coverage milestone | v4.0 roadmap |

## Session Continuity

Last session: 2026-08-15T21:36:03.226Z
Stopped at: Completed 27-02-PLAN.md
Resume file: None

## Operator Next Steps

- Review the v4.0 roadmap draft (`.planning/ROADMAP.md`), then plan Phase 25 with `/gsd-plan-phase 25`
