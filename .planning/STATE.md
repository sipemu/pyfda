---
gsd_state_version: 1.0
milestone: v2.1
milestone_name: Document the AI Advisor
status: Awaiting next milestone
stopped_at: Completed 18-01-PLAN.md
last_updated: "2026-08-11T19:54:14.945Z"
last_activity: 2026-08-11
last_activity_desc: Phase 14 execution started
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 5
  completed_plans: 5
  percent: 100
current_phase: 18
current_phase_name: nav-build-integration
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-11)

**Core value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method does, every example runs against the current API
**Current focus:** Phase 18 — nav-build-integration

## Current Position

Phase: Milestone v2.1 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-08-11 — Milestone v2.1 completed and archived

## Performance Metrics

**Velocity:**

- Total plans completed: 32
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 4 | - | - |
| 02 | 3 | - | - |
| 03 | 2 | - | - |
| 4 | 2 | - | - |
| 5 | 1 | - | - |
| 6 | 1 | - | - |
| 7 | 1 | - | - |
| 8 | 1 | - | - |
| 9 | 1 | - | - |
| 10 | 3 | - | - |
| 11 | 3 | - | - |
| 12 | 3 | - | - |
| 13 | 2 | - | - |
| 14 | 1 | - | - |
| 15 | 1 | - | - |
| 16 | 1 | - | - |
| 17 | 1 | - | - |
| 18 | 1 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 12min | 5 tasks | 3 files |
| Phase 01 P02 | 2min | 2 tasks | 1 files |
| Phase 01 P03 | 12m | 3 tasks | 7 files |
| Phase 01 P04 | 5min | 4 tasks | 3 files |
| Phase 02-audit P01 | 45min | 2 tasks | 1 files |
| Phase 02 P02 | 11 | 3 tasks | 1 files |
| Phase 02 P03 | 488 | 3 tasks | 1 files |
| Phase 03-learn-diagrams P01 | 20min | 3 tasks | 1 files |
| Phase 03 P02 | 8min | 4 tasks | 1 files |
| Phase 10 P02 | 3min | 3 tasks | 1 files |
| Phase 10 P03 | 2 | 2 tasks | 1 files |
| Phase 11 P01 | 2min | 3 tasks | 4 files |
| Phase 11 P03 | 3min | 2 tasks | 1 files |
| Phase 12 P01 | 5min | 2 tasks | 5 files |
| Phase 12 P02 | 4min | 3 tasks | 3 files |
| Phase 12 P03 | 7min | 3 tasks | 5 files |
| Phase 13 P01 | 4min | 3 tasks | 3 files |
| Phase 13 P02 | 2min | 3 tasks | 0 files |
| Phase 14 P01 | 4min | 4 tasks | 3 files |
| Phase 15 P01 | 13min | 2 tasks | 1 files |
| Phase 16 P01 | 8min | 2 tasks | 1 files |
| Phase 17-agent-skill-page P01 | 8m | 2 tasks | 1 files |
| Phase 18 P01 | 14min | 2 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v2.1 roadmap]: Phase numbering CONTINUES from v2.0 (starts at Phase 14; v2.0 ended at Phase 13)
- [v2.1 roadmap]: Documentation-only milestone — no advisor code changes unless the docs expose a genuine binding bug
- [v2.1 roadmap]: Phasing follows the per-section review-gate process — concept+diagrams first (Phase 14), then one phase per surface (Python API / MCP / Agent Skill), then nav+build integration
- [v2.1 roadmap]: Concept overview page and both new SVG diagrams live in one phase (Phase 14) — diagrams illustrate the concept and share a review gate
- [v2.1 roadmap]: New top-level "AI Advisor" nav section; all pages must build cleanly with executable fences running against the current API
- Init: Keep diagrams as hand-authored inline SVG (no programmatic generation)
- Init: Formalize shared SVG style spec before any diagram sweep
- Init: Review gate per doc section on built site before moving to next section
- [v2.0 roadmap]: One deterministic core (`build_diagnostics`, fdars-computed, offline) shared by all three surfaces; the LLM only interprets/reasons over computed numbers
- [v2.0 roadmap]: Grounding invariant enforced by Pydantic schema + system prompt on every surface (evidence cites diagnostic values; no fabricated numbers)
- [v2.0 roadmap]: `anthropic` is an optional `[advisor]` extra; `build_diagnostics` works offline with no network in CI; the LLM integration test is stubbed / env-gated
- [v2.0]: MCP transport = stdio only; HTTP/SSE deferred to a future milestone
- [v2.0]: skill execution target = Managed Agents env; git-URL install documented as authoritative until `[mcp]`/`[advisor]` extras ship on PyPI
- [Phase ?]: Two-lane metaphor for grounding-invariant diagram (fdars computes / LLM cites) with explicit cites arrow into Advice.evidence
- [Phase ?]: Overview page stays conceptual/diagram-led; no runnable code fence; first worked example deferred to Phase 15
- [Phase ?]: Schema table rows use plain text field names (no backtick wrapping) to match exec grep patterns in acceptance criteria
- [Phase ?]: MCP fences illustrative-only (no exec="1"): docs build does not require [mcp] extra or Python 3.10+
- [Phase ?]: Page written as complete document in tracer task — both Task 1 (skeleton+tools) and Task 2 (handle model, stdio, compare loop) content in single authoring pass
- [Phase ?]: Wrote agent-skill.md with verbatim git-URL install from SKILL.md, 5-step walkthrough mirroring fdars_advisor_walkthrough.py, and zero exec= fences — docs build passes without Python 3.10+, extras, or API key
- [Phase ?]: AI Advisor nav section placed after Analyze and before Examples in mkdocs.yml, matching the Analyze idiom; advisor/index.md maps to site/advisor/index.html (MkDocs standard)

### Pending Todos

None yet.

### Blockers/Concerns

None open.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v2 | v2.0 close |

## Session Continuity

Last session: 2026-08-11T19:38:18.762Z
Stopped at: Completed 18-01-PLAN.md
Resume file: None

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
