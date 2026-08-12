---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Provider-Agnostic Advisor, Full-Library Coverage
current_phase: 19
current_phase_name: first v3.0 phase
status: planning
stopped_at: Completed 19-02-PLAN.md
last_updated: "2026-08-12T06:40:24.807Z"
last_activity: 2026-08-12
last_activity_desc: v3.0 roadmap created (Phases 19–24), 28/28 requirements mapped
progress:
  total_phases: 1
  completed_phases: 0
  total_plans: 3
  completed_plans: 2
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-12)

**Core value:** The fdars AI advisor must work with any LLM backend — cloud or local — while the grounding invariant holds everywhere: fdars computes every number, the LLM only interprets and cites it. Every fdars analysis aspect gets advisor coverage on par with clustering.
**Current focus:** Phase 19 — Provider Foundation & Grounding Contract

## Current Position

Phase: 19 of 24 (Provider Foundation & Grounding Contract) — first v3.0 phase
Plan: — (not yet planned)
Status: Ready to plan
Last activity: 2026-08-12 — v3.0 roadmap created (Phases 19–24), 28/28 requirements mapped

Progress: [███████░░░] 67%

## Performance Metrics

**Velocity:**

- Total plans completed: 32 (v1.0–v2.1)
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 19 | - | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 19 P01 | 46m | 3 tasks | 6 files |
| Phase 19-provider-foundation-grounding-contract P02 | 424 | 3 tasks | 9 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v3.0 roadmap]: Phase numbering CONTINUES from v2.1 (starts at Phase 19; v2.1 ended at Phase 18)
- [v3.0 roadmap]: Foundation FIRST — `Provider` protocol + Anthropic refactor + validate-and-retry + `_check_grounding` (Phase 19) is the single blocking prerequisite; must ship the base grounding/retry machinery before any adapter or aspect so aspects don't each inherit unchecked grounding vulnerabilities
- [v3.0 roadmap]: Adapters (Phase 20) and per-aspect diagnostics (Phase 21) are INDEPENDENT and parallel-eligible after Phase 19
- [v3.0 roadmap]: MCP boundary stays LLM-free (SURF-01); provider selection lives only in the Python `advise()` (SURF-02)
- [v3.0 roadmap]: Packaging/CI (Phase 23) and Docs (Phase 24) come after code ships; docs LAST so executed offline fences run against the real implementation
- [v3.0 roadmap]: Custom `Provider` protocol only — no LiteLLM / pydantic-ai / LangChain; aspect always caller-specified (never auto-detected from result keys)
- [v2.0]: One deterministic `build_diagnostics` core shared by all surfaces; grounding invariant enforced by Pydantic schema + system prompt (fdars computes numbers, LLM only interprets/cites)
- [v2.0]: MCP transport = stdio only; HTTP/SSE deferred
- [Phase ?]: Kept _require_anthropic/_require_pydantic in advisor/__init__.py (not moved to providers/) so the sys.modules monkeypatch chain for ImportError tests remains intact through Phase 19-02 split
- [Phase ?]: providers/__init__.py imports AnthropicProvider at module level (safe: anthropic SDK deferred to AnthropicProvider.__init__ — no SDK import at module load)
- [Phase ?]: _GROUNDING_INVARIANT single constant in _prompts.py; build_diagnostics dispatches to aspects/ lazily; _selfcheck kept in __init__.py per RESEARCH.md Open Q2

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 20 research flag]: Schema portability across providers (OpenAI nullable unions, Gemini `additionalProperties` rejection, Ollama `think+format` conflict) — confirm during Phase 20 planning
- [Phase 21 research flag]: SPM diagnostics are highest-complexity; validate `spe_moment_match_diagnostic` fdars signature during Phase 21 planning

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x (FUT-01) | v2.0 close |

## Session Continuity

Last session: 2026-08-12T06:40:24.799Z
Stopped at: Completed 19-02-PLAN.md
Resume file: None

## Operator Next Steps

- Plan the first phase with `/gsd-plan-phase 19`
