---
gsd_state_version: 1.0
milestone: v6.0
milestone_name: fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference
current_phase: 40
current_phase_name: Advisor Extension
status: planning
stopped_at: Phase 39 complete, ready to plan Phase 40
last_updated: "2026-08-21T06:19:54.169Z"
last_activity: 2026-08-21
last_activity_desc: Phase 39 complete, transitioned to Phase 40
state_head: f852db3639dc870a9279ba6efdc7b49ffe2b29f7
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 6
  completed_plans: 6
  percent: 67
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-20)

**Core value:** Bump `fdars-core` 0.20.0→0.23.0 (parallel-only, no linalg), expose the new upstream surface through PyO3 bindings + the Python API across three capability groups (Group A Regression, Group B PACE-FPCA & Classification, Group C Depth/Outliers/Interval-Inference), extend the grounded advisor where a real grounded scalar exists, and document everything method-accurately — with the grounding invariant intact throughout. Same shape as v4.0/v5.0.
**Current focus:** Phase 39 — Group C — Depth/Outliers/Interval-Inference Bindings

## Current Position

Phase: 40 — Advisor Extension
Plan: Not started
Status: Ready to plan
Last activity: 2026-08-21 — Phase 39 complete, transitioned to Phase 40

## Performance Metrics

**Velocity:**

- Total plans completed: 6 (this milestone); 11 in v5.0; 11 in v4.0; 19 across v1.0–v3.0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 36 | 1 | - | - |
| 37 | 1 | - | - |
| 38 | 1 | - | - |
| 39 | 3 | - | - |
| 40 | TBD | - | - |
| 41 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v6.0 roadmap]: Phase numbering CONTINUES from v5.0 (starts at Phase 36; v5.0 ended at Phase 35) — no reset
- [v6.0 roadmap]: Same shape as v4.0/v5.0 — crate bump + regression gate FIRST (Phase 36, DEP-05/06), then three INDEPENDENT binding groups (Phases 37/38/39, parallel-eligible after Phase 36 — distinct `src/*_mod.rs` files), advisor on top (Phase 40), docs last (Phase 41)
- [v6.0 roadmap]: Phase 36 BLOCKS all downstream phases; wildcard fallback arms for any upstream enum that became `#[non_exhaustive]` at 0.23 and is reached by existing code are a compile prerequisite (crate does NOT build without them), landed in the bump commit
- [v6.0 roadmap]: Three binding groups kept as three separate phases (matches v4.0/v5.0 per-group review cadence + fine granularity): Group A = regression extension (Phase 37), Group B = PACE-FPCA + elastic_multinomial incl. the novel IrregFdata input + new `src/pace_fpca_mod.rs` (Phase 38, highest-novelty), Group C = depth/outliers/interval-inference (Phase 39, largest pitfall surface)
- [v6.0 roadmap]: Advisor extension (Phase 40, ADV-04/05) depends on Phase 37 + Phase 39 — needs the regression + outlier-detector result dicts to exist; extends the EXISTING `outliers` and `regression` aspects (no new aspect key by default), closing the v5.0 Phase-34 boxplot-outlier deferral; any `_DIAGNOSTICS_METHODS`/`_supported` change in a SINGLE atomic commit to keep `test_diagnostics_methods_match_advisor_supported` green
- [v6.0 roadmap]: Docs LAST (Phase 41) so executed offline fences + diagrams run against the real shipped bindings
- [research]: Do NOT enable `linalg` (still gates only `ridge_regression_fit`, still wants Rust 1.84 > MSRV 1.83); `parallel` retained; 0.20→0.23 additive/non-breaking (single-field Cargo.toml diff upstream), MSRV actually drops to 1.81 ≤ pyfda's 1.83 pin; zero new Python extras / datasets / CI-matrix changes
- [research]: Group B's `pace_fpca` takes `&IrregFdata` — a CSR-layout sparse type with NO existing Python binding precedent; needs a new `src/pace_fpca_mod.rs` + a lists-of-arrays builder (`fdars.irreg_fdata_from_lists`); a plain dense 2-D array compiles but silently produces wrong results
- [research]: Compound results decompose to PyDict via 5 new helpers following the canonical `test_result_to_pydict()` pattern (`ConcurrentRegrResult`, `FunctionalGlmResult`, `PaceFpcaResult`, `ElasticMultinomialResult`, `ItpResult` — the last is a NEW `itp_result_to_pydict` because ITP p-values are vectors not scalars)
- [research]: Four enum dispatch patterns need wildcard `_ => PyValueError` arms AND matching Python string maps: `DepthMethod` (extend +9 variants), `GlmFamily`, `SeqTransform`, `ProjectionBasisType`; Rust catches a missing arm but NOT a missing Python string mapping
- [research]: `functional_glm` and `itp_flm` re-fit internally (raw data in, no persistent handle); Gamma GLM uses inverse canonical link 1/μ and its AIC is NOT comparable to R `glm()` (document both in Phase 41)

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 36 prerequisite]: any upstream enum newly `#[non_exhaustive]` at 0.23 and reached by existing pyfda code needs a wildcard `_ => PyValueError` fallback arm — compile blocker, land in the bump commit; verify MSRV 1.81 ≤ 1.83 and that `linalg` stays off
- [Phase 37 plan-time spike]: confirm `ConcurrentRegrResult.beta_curve` orientation `(p, m)` (predictors × grid, NOT `(n_obs, m)`) against a multi-predictor (`p ≥ 2`) transposition guard test before REGR-01; confirm `FunctionalGlmResult` field names + `GlmFamily` variants
- [Phase 38 plan-time spike]: `IrregFdata` list-of-arrays PyO3 constructor interface — NO existing pyfda precedent (recommend `fdars.irreg_fdata_from_lists(argvals_list, values_list)`); resolve before writing `pace_fpca` (PACE-01/02). Confirm `PaceFpcaResult` 10 fields + `PaceFpcaConfig` struct-literal safety + `ElasticMultinomialResult` field names
- [Phase 38 risk]: `elastic_multinomial` negative/non-contiguous labels wrap `i64→usize` to `usize::MAX` (v5.0 CR-01) — add the 0-indexed contiguous label guard → helpful `ValueError`; `train_probabilities` `(n, K)` transposition guard at `K ≥ 3`; `pace_fpca` `eigenfunctions (m,ncomp)`/`scores (n,ncomp)` transposition guards
- [Phase 39 plan-time spike]: audit `outliers_mod.rs` / fdars-core 0.23 outlier signatures for existing `seed` params; add `seed=None`→fixed default where random components exist (OUTL-01..04). Confirm exact `DepthMethod` (+9), `SeqTransform`, `ProjectionBasisType` variant names + `ItpResult` field names
- [Phase 39 risk]: ITP determinism + numpy-scalar leak — permutation seed defaults to 0 for offline determinism; reduce `ItpResult` vectors to `float()`/1-D arrays (not `np.float64`) for JSON/grounding; new `itp_result_to_pydict` distinct from `test_result_to_pydict`
- [Phase 40 plan-time spike]: confirm whether `pace_fpca` / `elastic_multinomial` expose a genuinely grounded scalar diagnostic before committing Group B advisor coverage (ADV-05 — otherwise bindings + docs only); finalize the exact outlier scalar spec (n_outliers, fraction, score/threshold ranges — never raw index lists or numpy aggregates)
- [Phase 40 risk]: guard-sync must be atomic (advisor `_supported`/dispatch + MCP `_DIAGNOSTICS_METHODS` in one commit) or `test_diagnostics_methods_match_advisor_supported` goes red on the intermediate state; grounding invariant + offline determinism (no numpy scalars, byte-identical `json.dumps`) preserved
- [Phase 41 risk]: docs build ~19 min (executed fences run real compute) — keep fence data small (PACE/ITP synthetic `n ≤ 20`; phoneme subsampled to 3 classes, `m ≤ 64`), keep total build under ~25 min; SVGO idempotence + determinism gate + blocking human diagram method-accuracy review (depth asymmetry, PACE irregular observations, ITP closure direction)

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Plotting | PLOT-01: `fdars.plot.plot_functional_boxplot()` helper rendering the `functional_boxplot` numeric result | v2/future | v5.0 init |
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01 / FUT-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x | v2.0 close |
| Advisor | PACE-ADV / MULTINOM-ADV: dedicated advisor aspects for PACE-FPCA and elastic multinomial, if ADV-05's plan-time feasibility check defers them | future | v6.0 init |
| Core | `linalg`-gated `ridge_regression_fit` (Rust 1.84+ > MSRV 1.83) + HEAD 0.24-bound work (FAM, mixed models, FoF-RE) — not in published 0.23.0 | out of scope | v6.0 init |

## Session Continuity

Last session: 2026-08-20 — v6.0 roadmap created
Stopped at: Phase 39 complete, ready to plan Phase 40
Resume file: .planning/ROADMAP.md

## Operator Next Steps

- Plan the first phase with `/gsd-plan-phase 36`
