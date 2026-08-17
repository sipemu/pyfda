---
gsd_state_version: 1.0
milestone: v5.0
milestone_name: fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot + Basis/Smoothing
current_phase: 35
current_phase_name: Docs — Diagrams & Worked Examples
status: planning
stopped_at: Completed 34-01-PLAN.md
last_updated: "2026-08-17T20:09:22.142Z"
last_activity: 2026-08-17
last_activity_desc: Phase 31 Plan 01 complete — fdars.inference submodule with t_perm_test, f_perm_test, two_sample_mean_test
progress:
  total_phases: 6
  completed_phases: 5
  total_plans: 7
  completed_plans: 7
  percent: 83
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-17)

**Core value:** Upgrade `fdars-core` 0.17.0→0.20.0 (parallel-only, no linalg), expose the new functional-inference + depth/boxplot + basis/smoothing surface through PyO3 bindings + the Python API, extend the v3.0 grounded advisor with an `inference` diagnostics aspect, and document everything method-accurately — with the grounding invariant intact throughout.
**Current focus:** Phase 34 — advisor-extension

## Current Position

Phase: 35 — Docs — Diagrams & Worked Examples
Plan: Not started
Status: Ready to plan
Last activity: 2026-08-17 — Phase 34 complete, transitioned to Phase 35

## Performance Metrics

**Velocity:**

- Total plans completed: 7 (this milestone); 11 in v4.0; 19 across v1.0–v3.0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 30 | 1 | - | - |
| 31 | 3 | - | - |
| 32 | 1 | - | - |
| 33 | 1 | - | - |
| 34 | 1 | - | - |
| 35 | - | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 30 P01 | 4 | 2 tasks | 2 files |
| Phase 31 P01 | 6 | 4 tasks | 5 files |
| Phase 31-group-a-fdars-inference-bindings P02 | 4 | 2 tasks | 2 files |
| Phase 31 P03 | 35 | 3 tasks | 2 files |
| Phase 32 P01 | 4 | 2 tasks | 2 files |
| Phase 33-group-c-basis-smoothing-quick-wins P01 | 5m | 3 tasks | 3 files |
| Phase 34-advisor-extension P01 | 8m | 2 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v5.0 roadmap]: Phase numbering CONTINUES from v4.0 (starts at Phase 30; v4.0 ended at Phase 29) — no reset
- [v5.0 roadmap]: Same shape as v4.0 — crate bump + regression gate FIRST (Phase 30, DEP-03/04), then three INDEPENDENT binding groups (Phases 31/32/33, parallel-eligible after Phase 30), advisor on top (Phase 34), docs last (Phase 35)
- [v5.0 roadmap]: Phase 30 BLOCKS all downstream phases; the `CvCriterion` `#[non_exhaustive]` wildcard fallback arm is a compile prerequisite (crate does NOT build without it), not just a robustness nicety
- [v5.0 roadmap]: Three binding groups kept as three separate phases (matches v4.0 per-group review cadence + fine granularity): Group A = `fdars.inference` new submodule (Phase 31, largest/highest-risk), Group B = depth/boxplot extending `fdars.depth` (Phase 32), Group C = basis/smoothing quick wins (Phase 33, smallest)
- [v5.0 roadmap]: Advisor extension (Phase 34, ADV-03) depends on Phase 31 — needs the inference bindings to exist; `inference` is diagnostics-only (NOT in `_RUNNABLE_METHODS`); three-file guard-sync (`advisor/__init__.py` `_supported` + dispatch, `advisor/aspects/inference.py`, `mcp/server.py` `_DIAGNOSTICS_METHODS`) in a SINGLE atomic commit to keep `test_diagnostics_methods_match_advisor_supported` green
- [v5.0 roadmap]: Docs LAST (Phase 35) so executed offline fences + diagrams run against the real shipped bindings
- [research]: Do NOT enable `linalg` (requires Rust 1.84 > MSRV 1.83); `parallel` retained; 0.18 never published — upgrade path is 0.17 → 0.20 directly; 0.18→0.20 additive/non-breaking, zero new Rust/Python deps
- [research]: FLM inference re-fits `fregre_lm` internally (accepts raw data/response/n_comp) — `FregreLmResult` is a non-pyclass Rust struct and never crosses the boundary; matches existing `predict_fregre_lm` pattern
- [research]: Compound results decompose to PyDict (`TestResult`, `ToleranceBand`, `FunctionalBoxplotResult`); enums cross as `&str` + match arms with `_ => PyValueError` `#[non_exhaustive]` fallback (`DepthMethod`, `CvCriterion::Aic`, `MultiplierDistribution`)
- [research]: All permutation-test/random-projection seeds exposed as Python `seed=None` resolving to a fixed default for byte-identical reproducibility
- [Phase ?]: Do NOT enable linalg feature (requires Rust 1.84 > MSRV 1.83; not needed for v5.0 Groups A/B/C)
- [Phase ?]: Bump lands as single isolated commit (Cargo.toml + smoothing_mod.rs only; Cargo.lock gitignored) before Phase 31/32/33 binding work
- [Phase ?]: Zero numeric drift on 0.17->0.20 bump: 426 passed / 4 skipped / 0 failed, no tolerance relaxations
- [Phase 31-01]: seed=None resolves to u64 default 0 (locked); mod inference_mod placed alphabetically in lib.rs (rustfmt); 31-SIGNATURES.md is the plan-time authority for all 8 Group A function signatures
- [Phase ?]: multiplier_from_str() private helper dispatches string to MultiplierDistribution with non_exhaustive wildcard arm returning PyValueError
- [Phase ?]: ToleranceBand Vec<f64> fields converted via vec_to_numpy1d per field (not fdmatrix_to_numpy2d) per INFER-04 locked decision
- [Phase ?]: flm_f_test/flm_gof_test default n_comp=5; core clamps n_comp silently — degenerate-input tests use n<3 (fregre_lm error) and n=4 (GoF degenerate df) respectively
- [Phase ?]: outliers Vec<usize> -> Python list of ints (not ndarray) — matches locked 32-CONTEXT.md decision
- [Phase ?]: seed=None resolves to u64 default 0 inside depth_method_from_str — byte-identical RandomProjection reproducibility
- [Phase ?]: smooth_basis_aic placed in basis_mod.rs beside GCV twin per closest-analog placement rule in 33-CONTEXT.md
- [Phase ?]: CvCriterion::Aic output arm explicit; _ wildcard retained for non_exhaustive enum forward-compat
- [Phase ?]: inference aspect (ADV-03): diagnostics-only, caller supplies TestResult dict; n_perm==0 is legitimate asymptotic test value; ToleranceBand shape detected by half_width+center presence without p_value

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 30 prerequisite]: `optim_bandwidth` binding will NOT compile against 0.20's `#[non_exhaustive]` `CvCriterion` without a wildcard `_ => PyValueError` fallback arm — this is a compile blocker, land it in the bump commit
- [Phase 31 plan-time spikes]: `MultiplierDistribution` variants (docs.rs 404) before INFER-04/05; `flm_f_test`/`flm_gof_test` re-fit strategy + `fdars_core::scalar_on_function::FregreLmResult` cross-module import before INFER-06/07; `oneway_anova_vstat` group-label base (0- vs 1-indexed) before INFER-08; confirm exact `TestResult`/`ToleranceBand` field names before coding
- [Phase 31 risk]: permutation-test determinism — two calls with same seed must return byte-identical `json.dumps`; carry a determinism test
- [Phase 32 plan-time spike]: `DepthMethod` `#[non_exhaustive]` confirmation + exact variant names before DEPTH-01; `FunctionalBoxplotResult` field names / which fields are `FdMatrix` vs `Vec<f64>` before DEPTH-02
- [Phase 32 risk]: numpy(row-major)↔FdMatrix(column-major) transposition (#33 class) on every `FdMatrix`-returning boxplot field — route through `fdmatrix_to_numpy2d` (never `vec_to_numpy1d`), carry a multi-curve round-trip shape test
- [Phase 33 plan-time spike]: `constant_basis` exact signature/dimension (docs.rs 404) before BASIS-01; `smooth_basis_aic` existence + `aic_smoother`/`CvCriterion::Aic` module path before BASIS-02/03 (confirm `CvCriterion` in `fdars_core::smoothing` is the same enum vs a new one)
- [Phase 34 risk]: guard-sync must be atomic (three files, one commit) or `test_diagnostics_methods_match_advisor_supported` goes red on the intermediate state; grounding invariant + offline determinism (no numpy scalars) preserved
- [Phase 35 risk]: docs build ~18 min (executed fences run real compute) — keep fence data small (`n_perm=19`, SCB `nb=50`, synthetic/subset); two-sample tests need two groups — pick worked-example datasets accordingly; SVGO idempotence + determinism gate + blocking human diagram review

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Plotting | PLOT-01: `fdars.plot.plot_functional_boxplot()` helper rendering the `functional_boxplot` numeric result | v2/future | v5.0 init |
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x (FUT-01) | v2.0 close |
| API coverage | Additional upstream methods not in v5.0's three groups; 0.15→0.20 internal perf wins (inherited via the bump, no separate public API) | later coverage milestone | v5.0 init |

## Session Continuity

Last session: 2026-08-17T19:53:00.191Z
Stopped at: Completed 34-01-PLAN.md
Resume file: None

## Operator Next Steps

- Plan the first phase with `/gsd-plan-phase 30`
