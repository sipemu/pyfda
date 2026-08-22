---
gsd_state_version: 1.0
milestone: v7.0
milestone_name: Documentation Quality Pass — SVG Audit, Diagram Coverage & Page Depth
current_phase: 48
current_phase_name: Page Depth
status: executing
stopped_at: Completed 48-01-PLAN.md
last_updated: "2026-08-22T21:37:50.328Z"
last_activity: 2026-08-22
last_activity_desc: Phase 48 execution started
state_head: ea3b2c1b12c8b2cd75faeca4cc6a18e6bb051379
progress:
  total_phases: 8
  completed_phases: 6
  total_plans: 9
  completed_plans: 8
  percent: 75
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-22)

**Core value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.
**Current focus:** Phase 48 — Page Depth

## Current Position

Phase: 48 (Page Depth) — EXECUTING
Plan: 2 of 2
Status: Ready to execute
Last activity: 2026-08-22 — Phase 48 execution started

Progress: [████████░░] 75%

## Performance Metrics

**Velocity:**

- Total plans completed: 7 (this milestone); prior: 11 (v6.0), 11 (v5.0), 11 (v4.0), 19 across v1.0–v3.0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 42 | 1 | - | - |
| 43 | 1 | - | - |
| 44 | 1 | - | - |
| 45 | 1 | - | - |
| 46 | 2 | - | - |
| 47 | 1 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 42 P01 | 9m | 3 tasks | 1 files |
| Phase 43 P01 | 4m | 3 tasks | 4 files |
| Phase 44 P01 | 507 | 3 tasks | 4 files |
| Phase 45-svg-fix-regression-inference P01 | 159 | 3 tasks | 2 files |
| Phase 46 P01 | 9m | 3 tasks | 18 files |
| Phase 46-diagram-coverage-examples P02 | 8 minutes | 3 tasks | 22 files |
| Phase 47 P01 | 7 minutes | 2 tasks | 11 files |
| Phase 48 P01 | 4 | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v7.0 roadmap]: Phase numbering CONTINUES from v6.0 (starts at Phase 42; v6.0 ended at Phase 41) — no reset
- [v7.0 roadmap]: Same shape as the v1.0 overhaul — AUDIT first (Phase 42, AUDIT-01, gates everything), then SVG fixes batched by docs section (Phases 43–45), then new-diagram coverage (Phases 46–47), then page depth (Phase 48), then a whole-site + human review gate LAST (Phase 49)
- [v7.0 roadmap]: SVG fix batched into three balanced section groups per built-site review cadence + fine granularity — Phase 43 learn/represent/align (~24 diagrams), Phase 44 analyze/monitoring/advisor (~17), Phase 45 regression/inference (~19); each batch applies all four fix axes (SVGFIX-01..04) to its diagrams
- [v7.0 roadmap]: DIACOV split into two coverage phases — Phase 46 examples pages (DIACOV-01), Phase 47 advisor surface pages (DIACOV-02, reversing the v2.1 diagram-free choice); both depend only on the audit (Phase 42), not on the fix phases
- [v7.0 roadmap]: Phase 49 (GATE-01/02) depends on ALL of 43–48 — it is the whole-site strict build + per-section review + blocking human diagram method-accuracy review before close
- [standing v6.0]: Docs phases run sequentially on `main`, NOT in worktrees — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path (`use_worktrees: false` in config)
- [standing v6.0]: Blocking human diagram method-accuracy review before milestone close — the v6.0 lesson (inverted hypograph/epigraph asymmetry slipped past executors + verifier, caught only by human review)
- [Phase 42]: Canonical diagram count is 61 (not 68); ex-sonar-tsrvf.svg assigned to Phase 43 bucket
- [Phase 42]: conformal-prediction.svg confirmed accurate for scalar-response API; v1.0 misleading finding resolved
- [Phase 42]: spm.svg confirmed fully redrawn (R-era content removed); was Phase 44 Major, now OK
- [Phase 43]: depth-functions.svg: functional_boxplot confirmed exported at src/depth_mod.rs:625 — diagram reference correct
- [Phase 43]: 5 represent/ XML-cleanup files left byte-unchanged: inline font-size= are intentional size reductions, not CSS-class-size duplicates
- [Phase 43]: ex-sonar-tsrvf.svg migrated to viewBox 0 0 720 480 with canonical STYLE_SPEC five-class block
- [Phase 44]: KEEP Amplitude taxonomy in outlier-detection.svg (confirmed canonical against docs + src)
- [Phase 44]: REPLACE conformal_prediction_band() with magnitude_shape() (real binding at src/outliers_mod.rs:93)
- [Phase 44]: DEFER elastic-clustering function-name sub-label to Phase 49 (140px box too narrow)
- [Phase 45]: elastic-multinomial.svg height bumped 300→480; OvR rows re-spaced to h=74 each; method content preserved
- [Phase 45]: scalar-on-function.svg β̂(t) inset enlarged conservatively and surfaced for Phase 49 human review
- [Phase 45]: functional-glm.svg byte-unchanged: Gamma inverse g(μ)=1/μ confirmed correct vs src/regression_mod.rs:1091,1143 and docs md:34,36-37
- [Phase 45]: inference-permutation-test.svg byte-unchanged: lone font-size=11 on .mono (class=12) is intentional
- [Phase 46]: Tracer-first approach: authored ex-canadian-weather.svg end-to-end to prove the per-diagram pipeline before scaling to 8 more diagrams
- [Phase 46]: SVG height 480 for multi-row workflows (canadian-weather, canadian-seasonal, andrews-wine*, andrews-wine-clustering, andrews-wine-qc); 300 for single-row flows
- [Phase 47]: All 5 advisor diagrams use 720×480 viewBox — all needed the space for accurate multi-stage flows
- [Phase 47]: advisor-mcp.svg places Agent/LLM OUTSIDE MCP boundary with 6 _RUNNABLE_METHODS per server.py (not 5 per prose)
- [Phase 47]: advisor-aspects.svg lists 14 aspects per build_diagnostics._supported (not 12+ per intro prose)
- [Phase 48]: Task 1: Added Poisson as second GLM family (preferred over Gamma; no positivity trick)
- [Phase 48]: Task 2: PACE vs standard FPCA comparison section + new fence verifies eigenfunction consistency from sparse data
- [Phase 48]: Task 3: ITP-vs-t_perm_test fence demonstrates localisation (WHERE) vs detection (WHETHER) on same synthetic data

### Pending Todos

None yet.

### Blockers/Concerns

- [milestone-wide]: Every phase inherits the hard constraints — diagrams stay hand-authored inline SVG; SVGO idempotence + build-determinism CI gate must stay green; worked-example fences run OFFLINE against the current `fdars` API emitting `FDARS_FENCE_OK` with small data (synthetic `n ≤ 20` / subsampled datasets); whole-site `mkdocs build --strict` green offline
- [build time]: docs build is ~19–25 min with executed fences (real compute) — keep any NEW fence data small to hold total build time down (DEPTH-03)
- [Phase 42]: the milestone framing cites 68 concept diagrams; the working tree currently has 61 top-level concept SVGs in `docs/assets/diagrams/` — the audit produces the authoritative inventory and reconciles the count (cards/ and thumb/ excluded)
- [scope]: cards/ and thumb/ SVGs are OUT of audit scope unless a fixed concept diagram's thumb visibly diverges (→ DIAG-FUT-02)

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Diagrams | DIAG-FUT-01 (A11Y-01): Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | future | v7.0 init |
| Diagrams | DIAG-FUT-02: Regenerate thumb/ & cards/ SVGs to mirror any materially-changed concept diagram (only if a thumb visibly diverges) | future | v7.0 init |
| Plotting | PLOT-01: `fdars.plot.plot_functional_boxplot()` helper rendering the `functional_boxplot` numeric result | v2/future | v5.0 init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01 / FUT-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x | v2.0 close |
| Advisor | PACE-ADV / MULTINOM-ADV: dedicated advisor aspects for PACE-FPCA and elastic multinomial | future | v6.0 init |
| Core | `linalg`-gated `ridge_regression_fit` (Rust 1.84+ > MSRV 1.83) + HEAD 0.24-bound work | out of scope | v6.0 init |

## Session Continuity

Last session: 2026-08-22T21:37:50.204Z
Stopped at: Completed 48-01-PLAN.md
Resume file: None

## Operator Next Steps

- Plan Phase 42 (Diagram Audit) with /gsd-plan-phase 42
