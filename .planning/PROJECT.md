# pyfda — Documentation Overhaul

## What This Is

pyfda is the PyO3 binding layer that exposes the Rust `fdars-core` functional-data-analysis library to Python as the `fdars` package (represent, smooth, align, analyze, regress, monitor). This milestone is a **documentation overhaul**: reworking the MkDocs site's hand-authored SVG diagrams and its worked example pages to a consistently high, method-accurate standard.

## Core Value

The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.

## Current State

**Shipped milestones:**
- ✅ **v1.0 — Documentation Overhaul** (Phases 1–9): shared SVG `STYLE_SPEC.md` + SVGO/determinism CI guardrails, a nav+reference-API audit that derived the gap/example scope, six section diagram sweeps (learn/represent/align/analyze/regression/monitoring — all method-accurate and R-era-free), and an examples sweep (all pages run against the current API, plus five new worked examples).
- ✅ **v2.0 — Grounded AI analysis advisor** (Phases 10–13): a deterministic, offline `build_diagnostics` core + grounded `advise()` (Claude structured outputs, `claude-opus-4-8`) exposed across four surfaces — Python API (recommend-only), Tool/MCP (agentic re-run/compare over stdio), and an Anthropic Agent Skill. The grounding invariant holds throughout: fdars computes every number, the LLM only interprets and cites diagnostic values. Human UAT (2026-08-10) confirmed the real-key path produces grounded advice.

**Grounding invariant (v2.0):** every recommendation cites computed diagnostics and states an expected effect; the LLM never fabricates numbers.

**Design source of truth (v2.0):** `.planning/design/llm-cluster-narration.md`

## Current Milestone: v2.1 Document the AI Advisor

**Goal:** Give the published MkDocs site first-class, method-accurate coverage of the v2.0 grounded AI advisor — closing the gap where the feature shipped but its user-facing docs did not.

**Target features:**
- New top-level nav section for the advisor on the docs site.
- Concept + grounding-invariant overview page (what it is, the fdars-computes / LLM-interprets guarantee, when to use it).
- Python API page — `build_diagnostics` / `advise` / `describe_cluster_differences` with a runnable worked example.
- Tool / MCP server page — tools, stdio setup, the re-run/compare loop.
- Agent Skill page — install + the interpret→recommend→re-run→compare walkthrough.
- New hand-authored inline SVG diagrams to STYLE_SPEC standard (e.g. grounding invariant, the advisor loop).

**Key context:** Documentation-only milestone — no advisor code changes unless the docs expose a genuine bug. Must stay method-accurate against the shipped v2.0 code (`python/fdars/advisor.py`, `python/fdars/mcp/`, `.claude/skills/fdars-advisor/`) and use existing datasets in `docs/data/`. Deferred backlog carried forward: diagram accessibility (A11Y-01), examples editorial consolidation (EX2-01), HTTP/SSE MCP transport (deferred from v2.0).

## Requirements

### Validated

<!-- Existing capabilities inferred from the codebase map — the product being documented. -->

- ✓ PyO3 binding layer exposing `fdars-core` compute to Python (`fdars` package) — existing
- ✓ MkDocs (Material) documentation site with sections: learn, represent, smooth, align, analyze, regression, monitoring, reference, examples — existing
- ✓ ~50 hand-authored inline SVG concept diagrams in `docs/assets/diagrams/` (plus cards/ and thumb/) — existing
- ✓ Build-time inline figures via `markdown-exec` + `scripts/docs_fig.py` (`PYTHONPATH=scripts`) — existing
- ✓ 17 narrative example pages in `docs/examples/*.md` backed by datasets in `docs/data/` — existing
- ✓ Released at v0.2.0 with R-parity phase 1 complete — existing
- ✓ Documentation tooling foundation — `STYLE_SPEC.md`, SVGO check-only lint gate in CI (idempotence, all 43 diagrams), build determinism (`svg.hashsalt` + `<dc:date>` suppression — verified byte-identical across builds for deterministic content), `pymdownx.snippets` dataset includes, `pytest-markdown-docs` doc-test harness (one-page CI gate), and the `DOCS_FAST` helper — Phase 1
- ✓ Nav + reference-API audit — `02-AUDIT.md` maps all 42 method-section pages on style/accuracy axes (D-02 rollup), a full R-era grep report (4 leftovers, all in `spm.svg`), and a ranked GAP-0001..0011 / EX-0001..0008 list with a user Selection column gating Phase 3 — Phase 2
- ✓ Tool / MCP surface (TOOL-01, TOOL-02, TOOL-03) — `fdars.mcp` subpackage (optional `[mcp]` extra, Python 3.10+): `HandleRegistry` (by-reference handles, fail-closed), `MCPServer("fdars-advisor")` exposing `fdars_build_diagnostics`, `fdars_run_method` (5-method dispatch), and `fdars_compare_run` (observable before/after delta) over a transport-agnostic handler layer with a stdio entry point; grounding invariant preserved (fdars does the numbers, no LLM in the compute path). Verified 4/4 must-haves, 111 tests pass — Phase 12
- ✓ Agent Skill surface (SKILL-01, SKILL-02) — `.claude/skills/fdars-advisor/` packages the interpret→recommend→re-run→compare loop as an Anthropic Agent Skill: spec-valid `SKILL.md` (git-URL install documented as the authoritative execution environment) + an offline walkthrough script (Canadian Weather → smoothing → deterministic before/after delta) with an env-gated `advise()` grounded-advice step, driven by `tests/test_skill.py` (6 tests). Human UAT (2026-08-10) confirmed the LLM path produces grounded advice citing diagnostics values with a real key — Phase 13

**v2.0 — Grounded AI analysis advisor (Phases 10–13):**
- ✓ Deterministic, offline `build_diagnostics(result, method, …)` core — fdars-computed, no LLM/network dependency (CORE-01/04) — v2.0
- ✓ Grounded `advise()` returning a schema-validated `Advice` via Claude structured outputs, every recommendation carrying `action`/`kind`/`rationale`/`expected_effect`/`evidence` (CORE-02/03) — v2.0
- ✓ Three advisor task families — interpretation, parameter guidance, method guidance — plus `describe_cluster_differences` specialization (CORE-05, ADVISE-01/02/03) — v2.0
- ✓ Python API surface (recommend-only): advisor registered in the public `fdars` API, offline + env-gated integration tests, `examples/advisor_recipe.py` (PYAPI-01/02/03) — v2.0
- ✓ Tool/MCP surface (agentic): coarse-grained tools + stdio MCP server + re-run/compare before/after loop (TOOL-01/02/03) — v2.0
- ✓ Agent Skill surface: `SKILL.md` + walkthrough packaging the interpret→recommend→re-run→compare loop, execution environment documented (SKILL-01/02) — v2.0

**v1.0 — Documentation Overhaul (Phases 1–9):**
- ✓ Shared SVG style spec + SVGO/determinism/doc-test CI guardrails and `DOCS_FAST` path (FND-01..06) — v1.0
- ✓ Nav + reference-API audit deriving the diagram-gap / new-example scope, incl. R-era grep report (AUD-01/02/03) — v1.0
- ✓ Six section diagram sweeps — learn/represent/align/analyze/regression/monitoring, all method-accurate and style-conformant (DIA-01..06) — v1.0
- ✓ Examples sweep — every page runs against the current API, richer narratives, improved figures, five new worked examples (EX-01..04) — v1.0
- ✓ All diagrams remain hand-authored inline SVG (no programmatic generation) — v1.0

### Active

<!-- v2.1 — Document the AI Advisor. Requirements defined in REQUIREMENTS.md, mapped to roadmap phases. -->

- [x] Advisor concept + grounding-invariant overview page on the docs site — Phase 14 (CONCEPT-01/02/03)
- [x] New hand-authored inline SVG diagram(s) for the advisor, to STYLE_SPEC standard — Phase 14 (ADVDIA-01/02: grounding-invariant + advisor-loop)
- [ ] Python API advisor page with a runnable worked example
- [ ] Tool / MCP server page (tools, stdio setup, re-run/compare loop)
- [ ] Agent Skill page (install + interpret→recommend→re-run→compare walkthrough)
- [ ] New top-level "AI Advisor" nav section wired into `mkdocs.yml`

### Out of Scope

- Programmatic/tool-generated diagrams — user chose to keep diagrams hand-authored inline SVG
- Dark-mode / theming rework of SVGs — not part of this milestone's intent
- Library/runtime code changes to `fdars` or `fdars-core` — this is a documentation milestone; code fixes only if an example exposes a genuine binding bug
- R-parity feature work — tracked separately (see `PARITY_PLAN.md`)

## Context

- **Site build:** MkDocs Material (`mkdocs.yml`); diagrams referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`. Inline figures use `markdown-exec` importing `docs_fig` from `scripts/` (canonical mechanism is `PYTHONPATH=scripts`; `docs/hooks.py` is a fallback). A `site/` build output and a docs CI workflow already exist.
- **Diagram style today:** `viewBox="0 0 720 300"`, inline `<style>` classes (`.ttl/.sub/.lab/.sm/.mono`), system-ui fonts, muted Bootstrap-ish palette, `role="img"` + `aria-label`. This is the de-facto baseline the shared style spec will formalize.
- **Datasets:** `docs/data/` (canadian weather, growth, phoneme, tecator, sonar, wine) drive the narrative examples; standalone scripts also live in top-level `examples/`.
- **Codebase map:** see `.planning/codebase/` (ARCHITECTURE, STRUCTURE, STACK, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS).

## Constraints

- **Authoring**: Diagrams stay hand-authored inline SVG — max conceptual control, edited by hand against a shared style spec.
- **Accuracy**: Diagrams and example outputs must be method-accurate; correctness is validated by section review on the built site, not assumed.
- **Compatibility**: Examples must run against the *current* `fdars` API and existing datasets in `docs/data/`.
- **Process**: Work proceeds section-by-section (learn/, align/, analyze/, regression/, monitoring/, represent/, examples/) with a review gate per section before moving on.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep diagrams as hand-authored inline SVG | Max control over the conceptual look; matches existing baseline | ✓ Good — held through all six v1.0 sweeps |
| Formalize a shared SVG style spec before rollout | Consistency across ~50 diagrams needs one standard | ✓ Good — `STYLE_SPEC.md` + SVGO idempotence gate (all 43 diagrams) |
| Full sweep of all diagrams + all example pages | User wants the whole doc set brought to one bar | ✓ Good — v1.0 shipped all six diagram sections + examples sweep |
| Review per doc section via the built site | User validates accuracy/style in batches before rollout continues | ✓ Good — per-section review gates held |
| Derive coverage/new-example list from nav + reference-API audit | Systematic gap detection over guesswork | ✓ Good — `02-AUDIT.md` (Phase 2): ranked GAP/EX list + Selection gate |
| Diagrams prioritized over examples | User's stated priority order | ✓ Good — diagrams (Phases 3–8) before examples (Phase 9) |
| One deterministic core shared by all advisor surfaces | fdars computes numbers; the LLM only interprets — grounding invariant | ✓ Good — `build_diagnostics` shared by Python/MCP/Skill (v2.0) |
| Grounding invariant enforced by Pydantic schema + system prompt | Evidence must cite diagnostic values; no fabricated numbers | ✓ Good — `Advice` schema + human UAT confirmed (v2.0) |
| `anthropic`/`mcp` as optional extras; core works offline | Keep CI network-free; LLM tests env-gated | ✓ Good — offline tests pass, integration skips without key (v2.0) |
| MCP transport = stdio only; HTTP/SSE deferred | Matches local/CI usage; keep tool layer transport-agnostic | ✓ Good — stdio shipped; HTTP deferred to a future milestone (v2.0) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-11 after Phase 14 (Advisor Concept & Diagrams — overview page + two SVG diagrams shipped)*
