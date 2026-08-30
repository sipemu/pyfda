---
gsd_state_version: 1.0
milestone: v8.0
milestone_name: "Advisor: New Capabilities"
current_phase: 52
current_phase_name: Pipeline Diagnostic Report
status: executing
stopped_at: Phase 51 complete, ready to plan Phase 52
last_updated: "2026-08-30T18:35:09.942Z"
last_activity: 2026-08-24
last_activity_desc: Phase 51 complete, transitioned to Phase 52
state_head: 5e314545402e1d1ca7441917e812c113eefd0950
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 9
  completed_plans: 6
  percent: 40
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-23)

**Core value:** Extend the fdars AI advisor with new agentic capabilities while holding the grounding invariant (fdars computes every number; the LLM only interprets/cites) and the MCP-LLM-free compute boundary as hard constraints.
**Current focus:** Phase 51 — Comparative Method-Selection

## Current Position

Phase: 52 (Pipeline Diagnostic Report) — READY TO EXECUTE
Plan: Not started
Status: Ready to execute
Last activity: 2026-08-24 — Phase 51 complete, transitioned to Phase 52

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**

- Total plans completed: 6 (this milestone); prior: 9 (v7.0), 11 (v6.0), 11 (v5.0), 11 (v4.0), 19 across v1.0–v3.0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 50 | 3 | - | - |
| 51 | 3 | - | - |
| 52 | TBD | - | - |
| 53 | TBD | - | - |
| 54 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 50 P01 | 3min | 3 tasks | 3 files |
| Phase 50-deferred-advisor-aspects-compat-pre-flight P02 | 10min | 4 tasks | 6 files |
| Phase 50 P03 | 3min | 2 tasks | 2 files |
| Phase 51 P01 | 362 | 3 tasks | 3 files |
| Phase 51-comparative-method-selection P02 | 10min | 3 tasks | 4 files |
| Phase 51-comparative-method-selection P03 | 12 | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v8.0 roadmap]: Phase numbering CONTINUES from v7.0 (starts at Phase 50; v7.0 ended at Phase 49) — no reset
- [v8.0 roadmap]: Foundation-first 5-phase structure per research — deferred aspects FIRST (Phase 50, unblocks accurate diagnostics for every later LLM call), then comparative → pipeline (Phases 51–52, strict complexity/dependency gradient; pipeline proves per-stage isolation), auto-tuning capstone (Phase 53), eval + docs gate LAST (Phase 54)
- [v8.0 roadmap]: COMPAT-01..03 folded into Phase 50 as a pre-flight (anthropic pin >=0.72,<1.0; mcp v2 MCPServer import; version-independent guard-sync test) — blocking fixes on the existing surface must land before new aspect work
- [v8.0 roadmap]: EVAL-01..02 folded into the Phase 54 docs gate — eval signals defined alongside the capstone/close, not a standalone thin phase
- [v8.0 roadmap]: Phase 53 (auto-tuning) flagged for research-phase during planning — convergence/oscillation/guard interaction + heuristic-proposal param spec + MCP param-schema decision are the milestone's genuine unknowns
- [standing v6.0]: Docs phase (54) runs sequentially on `main`, NOT in worktrees — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path (`use_worktrees: false` in config)
- [standing v6.0]: Blocking human diagram method-accuracy review before milestone close (the hypograph/epigraph lesson)
- [Phase 50]: COMPAT-01: Pin anthropic<1.0 in [advisor] extra; full 1.x migration (which drops Python 3.9) deferred to its own milestone
- [Phase 50]: COMPAT-02: MCP server.py import already correct (MCPServer from mcp.server); test-only regression test added, no production change
- [Phase 50]: COMPAT-03: Guard-sync split: primary test uses ValueError parse (no mcp import, runs 3.9+); companion test internally guarded to 3.10+ via importorskip keeps hard-coded literal honest
- [Phase 50]: ASPECT-03: ITP emits detection AND localisation together — lone min_p misleads LLM (PITFALLS #8)
- [Phase 50]: ASPECT-02: overfitting_gap is None when holdout_accuracy not supplied (grounding invariant, T-50B-03)
- [Phase 50]: ASPECT-04: fpca added as new _ASPECT_PRIMERS key (absent from 10-key dict); len=11 <= 14 gate passes
- [Phase 50]: Guard-sync no-op: no new _DIAGNOSTICS_METHODS or _supported key — confirmed empty git diff
- [Phase 50]: ASPECT-05: Live aspect tests named test_aspect_live_* (not test_live_*) to preserve QUAL-02 contract asserting exactly 3 test_live_* provider tests
- [Phase 50]: ASPECT-05: holdout_accuracy=0.72 forwarded in elastic fixture so overfitting_gap is non-None and citable by the grounding scanner
- [Phase 51]: compare_methods offline core: metric registry + dual-input normalizer + fail-closed guard + stable deterministic sort (COMPARE-01, COMPARE-03)
- [Phase 51]: Per-candidate grounding: _check_grounding(advice, block_diagnostics) per labeled block — cross-candidate citation raises GroundingViolationError (COMPARE-02)
- [Phase 51]: compare_methods(run_llm=True): result['winner'] always from fdars sort (pre-LLM); result['advice'] carries LLM Advice object; LLM cannot override winner (T-51-05, COMPARE-01)
- [Phase 51]: fdars_compare_methods validates method at tool boundary before delegating to helper — fail fast with clear ValueError naming _RUNNABLE_METHODS
- [Phase 51]: No ranking logic inlined in server.py — 3-line handler delegates entirely to compare_methods_mcp (Anti-Pattern 5 / Single Responsibility)
- [Phase 51]: guard-sync no-op confirmed: _RUNNABLE_METHODS=6, _DIAGNOSTICS_METHODS=14 unchanged by adding fdars_compare_methods

### Pending Todos

None yet.

### Blockers/Concerns

- [milestone-wide]: Grounding invariant is a hard constraint on every phase — every emitted scalar must be fdars-computed native `float`/`int` (no numpy scalars, no fabricated numbers); the LLM only interprets/cites and (in auto-tune) proposes via a schema-validated numeric `parameter_delta`
- [milestone-wide]: MCP boundary must stay provably LLM-free — no new MCP tool (`fdars_compare_methods`, `fdars_build_pipeline_report`, `fdars_auto_tune`) may call `advise()`; MCP proposals are heuristic; guard-sync (`_DIAGNOSTICS_METHODS` ↔ `build_diagnostics._supported`) edits stay atomic (a no-op for all four capabilities — no new method slot)
- [Phase 50]: ITP vector→scalar reduction must emit detection AND localisation scalars together (min adjusted p; count + proportion significant; first significant basis; detected-at-0.05) — a lone `min_p` misleads the LLM into treating local significance as global
- [Phase 50 unknowns]: best PACE quality scalar beyond sigma2/ncomp (reconstruction-quality from `fitted`?); ITP small-sample (n_basis=2) behavior — resolve in Phase 50 plan
- [Phase 53 unknowns]: heuristic proposal grid width/steps per method; static allowlist vs `**kwargs` for the MCP tool; whether the 6 `_RUNNABLE_METHODS` suffice or regression/inference must become runnable; `max_steps` cost ceiling (~20 suggested — confirm with user)
- [build time]: docs build is ~19–25 min with executed fences — keep any NEW auto-tune/comparison/pipeline fence data small and use the offline/injectable path (no network in docs build)
- [packaging]: package currently 0.7.0; a code milestone bumps it (semver `vX.Y.Z` tag triggers PyPI publish) — decide the bump at close; full anthropic 1.x migration deferred out of v8.0 (drops Python 3.9)

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| SDK | ANTHROPIC-1X: full `anthropic` 1.x migration (drops Python 3.9; `output_config`, httpx2) — its own milestone once Python 3.9 is dropped | future | v8.0 init |
| Transport | HTTP-01 / FUT-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x/future | v2.0 close |
| Diagrams | DIAG-FUT-01 (A11Y-01): Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | future | v7.0 init |
| Diagrams | DIAG-FUT-02: Regenerate thumb/ & cards/ SVGs to mirror any materially-changed concept diagram | future | v7.0 init |
| Plotting | PLOT-01: `fdars.plot.plot_functional_boxplot()` helper | v2/future | v5.0 init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Core | `linalg`-gated `ridge_regression_fit` (Rust 1.84+ > MSRV 1.83) + HEAD 0.24-bound work | out of scope | v6.0 init |

## Session Continuity

Last session: 2026-08-24T09:37:33.252Z
Stopped at: Phase 51 complete, ready to plan Phase 52
Resume file: None

## Operator Next Steps

- Plan the first phase with /gsd-plan-phase 50
