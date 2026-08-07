---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 4
current_phase_name: represent/ Diagrams
status: planning
stopped_at: Completed 03-02-PLAN.md — all 6 learn/ diagrams verified, COVERAGE.md authored
last_updated: "2026-08-07T23:46:39.939Z"
last_activity: 2026-08-08
last_activity_desc: Phase 03 complete, transitioned to Phase 4
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 9
  completed_plans: 9
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-07)

**Core value:** Every diagram faithfully depicts what the method actually does; every example runs against the current API
**Current focus:** Phase 03 — learn-diagrams

## Current Position

Phase: 4 — represent/ Diagrams
Plan: Not started
Status: Ready to plan
Last activity: 2026-08-08 — Phase 03 complete, transitioned to Phase 4

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 9
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 4 | - | - |
| 02 | 3 | - | - |
| 03 | 2 | - | - |

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

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Keep diagrams as hand-authored inline SVG (no programmatic generation)
- Init: Formalize shared SVG style spec before any diagram sweep
- Init: Diagrams prioritized over examples (user priority order)
- Init: Review gate per doc section on built site before moving to next section
- Init: Derive coverage/new-example list from nav + reference-API audit (evidence-based scope)
- [Phase ?]: SVGO gate uses idempotence check (svgo pass 2 == pass 1), not diff-vs-source, because svgo's serialiser always normalises whitespace
- [Phase ?]: All 43 diagrams pass the SVGO gate; no exclusion list required
- [Phase ?]: svg.hashsalt='fdars-docs' set at module-import time in docs_fig.py to ensure byte-identical SVG IDs across full builds (FND-03)
- [Phase ?]: fast(full, fast_value) is the single DOCS_FAST switch in docs_fig.py; fast mode is speed-only and NOT the determinism source of truth (FND-06, D-07, D-08)
- [Phase ?]: Snippet files contain only plain Python lines (no HTML comments) — comments cause SyntaxError when substituted into exec fences by pymdownx.snippets
- [Phase ?]: [Phase 01]: pytest-markdown-docs LOCKED IN as doc-test harness (D-04); cross-fence-state risk did not materialise
- [Phase ?]: [Phase 01]: FND-04 snippets (--8<--) expanded for pytest-markdown-docs via conftest pytest_markdown_docs_markdown_it() hook — no example .md edited (Phase 9's domain)
- [Phase ?]: [02-01] Two-axis audit method locked: style axis (grep-checkable STYLE_SPEC markers) independent of accuracy axis (expert inspection); D-02 rollup derives from both
- [Phase ?]: [02-01] smoothing.svg confirmed as redraw (not restyle): Panel 3 ghost polyline reuses Panel 1 noisy coordinates verbatim from L8 onward (file:line evidence)
- [Phase ?]: [02-01] custom-plotting.md R-first framing flagged for Phase 3 editorial review — ggplot2 mentions intentional but page structure warrants Python-first reframing
- [Phase ?]: basis-representation.svg R-era finding not confirmed: SVG uses current Python API throughout
- [Phase ?]: spm.svg confirmed R-era artifact: extendr/autoplot/'in R' text, wrong method — requires full redraw (GAP-0003)
- [Phase ?]: conformal-prediction.svg scalar-not-band finding confirmed: output shows scalar interval not time-varying band ŷ(t)±q(t) (GAP-0004)
- [Phase ?]: All R-era LOFEFOVERs are confined to spm.svg (4 lines, lines 5/31/55/56). All other R package references across prose are PROSE-OK intentional notes.
- [Phase ?]: basis-representation.svg preliminary R-era finding was NOT confirmed — the SVG uses current Python API names. No R-era content present.
- [Phase ?]: Smoothing module has zero worked examples across all 17 example pages — added as EX-0006 (P1 priority), highest-urgency new-example gap.
- [Phase ?]: GAP-0001: Panel 3 ghost underlay redrawn as genuinely-distinct noisy path (not removed) to preserve pedagogical before/after contrast
- [Phase ?]: New Panel 3 ghost coordinate string: M0 96 L8 78 L16 106 L24 74 L32 98 L40 66 L48 88 L56 56 L64 82 L72 52 L80 76 L88 50 L96 72 L104 44 L112 66 L120 46 L128 64 L136 48 L144 56 L152 52 L156 64
- [Phase ?]: All 6 learn/ diagrams proven idempotent under svgo@3.3.4 + svgo.config.mjs
- [Phase ?]: All 6 learn/ diagrams carry full STYLE_SPEC marker set — zero legacy outliers in learn/
- [Phase ?]: COVERAGE.md authored: no external API integration for phase 03

### Pending Todos

None yet.

### Blockers/Concerns

- Research flag: regression/ and monitoring/ sweeps need method-semantic verification against `fdars-core` behavior before diagrams can be drawn correctly (β(t), conformal functional bands, SPM Phase I/II)
- Research flag: smoke-test `pytest-markdown-docs` multi-block state on one narrative page in Phase 1 before committing to it as the CI pattern

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |

## Session Continuity

Last session: 2026-08-07T22:13:14.406Z
Stopped at: Completed 03-02-PLAN.md — all 6 learn/ diagrams verified, COVERAGE.md authored
Resume file: None
