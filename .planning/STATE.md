---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Grounded AI analysis advisor
current_phase: 12
current_phase_name: Tool / MCP Surface
status: executing
stopped_at: Completed 11-03-PLAN.md — examples/advisor_recipe.py recipe script created (PYAPI-03)
last_updated: "2026-08-09T20:57:10.779Z"
last_activity: 2026-08-09
last_activity_desc: Phase 10 execution started
progress:
  total_phases: 13
  completed_phases: 2
  total_plans: 9
  completed_plans: 6
  percent: 15
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-07)

**Core value:** Every recommendation cites fdars-computed diagnostics and states an expected effect; the LLM reasons over computed numbers and never fabricates them
**Current focus:** Phase 11 — python-api-surface

## Current Position

Phase: 12 — Tool / MCP Surface
Plan: Not started
Status: Ready to execute
Last activity: 2026-08-09 — Phase 11 complete, transitioned to Phase 12

## Performance Metrics

**Velocity:**

- Total plans completed: 22
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

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Keep diagrams as hand-authored inline SVG (no programmatic generation)
- Init: Formalize shared SVG style spec before any diagram sweep
- Init: Diagrams prioritized over examples (user priority order)
- Init: Review gate per doc section on built site before moving to next section
- Init: Derive coverage/new-example list from nav + reference-API audit (evidence-based scope)
- [v2.0 roadmap]: Phase numbering CONTINUES from v1.0 (starts at Phase 10; v1.0 ended at Phase 9)
- [v2.0 roadmap]: One deterministic core (`build_diagnostics`, fdars-computed, offline) shared by all three surfaces; the LLM only interprets/reasons over computed numbers
- [v2.0 roadmap]: Grounding invariant enforced by Pydantic schema + system prompt on every surface (evidence cites diagnostic values; no fabricated numbers)
- [v2.0 roadmap]: `anthropic` is an optional `[advisor]` extra; `build_diagnostics` works offline with no network in CI; the LLM integration test is stubbed / env-gated
- [v2.0 roadmap]: Split by surface — Python API is recommend-only; Tool/MCP and Agent Skill are agentic (re-run fdars + compare before/after)
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
- [Phase ?]: CORE-01 complete: all five build_diagnostics method branches (alignment, fpca, basis, smoothing, clustering) offline and deterministic
- [Phase ?]: ADVISE-02 realised: parameter task clause names lambda_/n_basis/bandwidth/n_comp/cluster k/depth method, requires kind=parameter with cited evidence
- [Phase ?]: ADVISE-03 realised: method task clause encodes poor-fit -> alternative mappings (elastic FPCA, pre-smooth, unconstrained transform), requires kind=method with cited evidence
- [Phase ?]: describe_cluster_differences is a thin specialization on build_diagnostics(method='clustering') + advise; run_llm=False offline escape hatch returns raw diagnostics dict
- [Phase ?]: advisor wired via plain Python import + sys.modules injection (not in _submodule_names — pure-Python, not native Rust submodule)
- [Phase ?]: pydantic>=2.0 included in [advisor] extra alongside anthropic>=0.72.0 (anthropic SDK does not auto-install pydantic)
- [Phase ?]: Task 1 and Task 2 implemented atomically in one commit: offline body + LLM guard authored in single pass; kmeans_fd used directly per Pitfall 6; recipe placed in examples/ not docs/examples/ per Pitfall 5 prohibition

### Pending Todos

None yet.

### Blockers/Concerns

- OPEN DECISION (Phase 13): skill execution target — Managed Agents env with `allow_package_managers` (recommended) vs bundled wheel vs Messages-API code-execution container
- OPEN DECISION (Phase 12): MCP transport — stdio (local) vs HTTP/SSE (hosted), or both
- OPEN DECISION (Phase 10/11): `anthropic` SDK version floor — a current version supporting `messages.parse` + `claude-opus-4-8`

- Research flag: regression/ and monitoring/ sweeps need method-semantic verification against `fdars-core` behavior before diagrams can be drawn correctly (β(t), conformal functional bands, SPM Phase I/II)
- Research flag: smoke-test `pytest-markdown-docs` multi-block state on one narrative page in Phase 1 before committing to it as the CI pattern

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |

## Session Continuity

Last session: 2026-08-09T19:45:56.977Z
Stopped at: Completed 11-03-PLAN.md — examples/advisor_recipe.py recipe script created (PYAPI-03)
Resume file: None
