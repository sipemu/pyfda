# Phase 14: Advisor Concept & Diagrams - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a new top-level "AI Advisor" overview page on the MkDocs site that tells a reader what the advisor is, names its three surfaces (Python API / MCP / Agent Skill), states when to use it, and explains the grounding invariant in plain terms — reinforced by two new hand-authored inline SVG diagrams (grounding invariant; advisor loop) that pass the SVGO idempotence + determinism CI gate to `STYLE_SPEC` standard.

Covers requirements CONCEPT-01, CONCEPT-02, CONCEPT-03, ADVDIA-01, ADVDIA-02. The actual nav wiring into `mkdocs.yml` is Phase 18 (NAVDOC-01); this phase authors the page + diagrams and may add the page file, but full nav integration/build-gate lives in Phase 18.

</domain>

<decisions>
## Implementation Decisions

### Overview Page Structure & Content
- Page lives at `docs/advisor/index.md` — a new top-level `advisor/` section directory, matching the existing `learn/index.md`, `represent/index.md`, … pattern.
- The overview stays conceptual: what the advisor is, why (grounding invariant), when to use it, and install/extras. Each of the three surfaces gets a one-paragraph teaser plus a link to its own dedicated page (authored in Phases 15–17).
- No runnable code snippet on the overview — keep it conceptual and diagram-led; the first runnable worked example lives on the Python API page (PYDOC-02, Phase 15).
- "When to use it" is a short bulleted list (parameter tuning, method choice, interpreting diagnostics, before/after comparison), drawn from the shipped `SKILL.md` description.

### Grounding-Invariant Diagram (ADVDIA-01)
- Metaphor: two lanes — "fdars computes numbers" (data → `build_diagnostics` → numeric diagnostics) feeding "LLM interprets & cites" (`advise` → `Advice` with evidence/rationale).
- Make "cites" literal: an arrow from the computed diagnostic values into the evidence/rationale fields of `Advice`.
- Canvas & styling: STYLE_SPEC baseline — `viewBox="0 0 720 300"`, reuse `.ttl/.sub/.lab/.sm/.mono` classes and the muted palette; no new colors.
- Show an explicit "numbers never fabricated by the LLM" divider/boundary between the two lanes.

### Advisor-Loop Diagram (ADVDIA-02)
- Cyclic 4-node flow: interpret → recommend → re-run → compare, with compare feeding back to interpret.
- Depict the agentic loop (MCP / Agent Skill); show the Python API as a "recommend-only" exit branch after the *recommend* node.
- Annotate the compare node with "before/after diagnostics delta".
- Placement: grounding-invariant diagram near the top of the page; advisor-loop diagram inside a "how it works" section lower down.

### Claude's Discretion
- Exact SVG path coordinates, node geometry, and label wording, subject to STYLE_SPEC conformance and the SVGO/determinism gate.
- Section headings and prose wording on the overview page, subject to method-accuracy against the shipped code.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/STYLE_SPEC.md` — the shared SVG style contract (viewBox, `.ttl/.sub/.lab/.sm/.mono` classes, `role="img"` + `aria-label`, muted palette). All new diagrams must conform.
- ~50 existing hand-authored SVGs in `docs/assets/diagrams/*.svg` to model structure/idiom on (e.g. `clustering.svg`, `basis-representation.svg`).
- Existing section landing pages (`docs/learn/index.md`, `docs/represent/index.md`, `docs/align/index.md`) as templates for an `index.md` overview + `!!! info` admonition conventions.
- SVGO idempotence gate + `svgo.config.mjs` and the determinism setup (`svg.hashsalt`, `<dc:date>` suppression) from Phase 1 — new diagrams must pass `svgo` pass2 == pass1.

### Established Patterns
- Diagrams referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`.
- Shipped advisor surface being documented: `python/fdars/advisor.py` (`build_diagnostics`, `advise`, `describe_cluster_differences`, `Advice` schema with `action`/`kind`/`rationale`/`expected_effect`/`evidence`); `python/fdars/mcp/` (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`, `run_stdio`); `.claude/skills/fdars-advisor/SKILL.md`.
- Install extras: `[advisor]` (`anthropic>=0.72.0`, `pydantic>=2.0`), `[mcp]` (`mcp>=2.0.0`, Python 3.10+). Offline core vs env-gated LLM via `ANTHROPIC_API_KEY`.

### Integration Points
- New `docs/advisor/` directory; page file `docs/advisor/index.md`.
- New SVGs under `docs/assets/diagrams/` (e.g. `advisor-grounding-invariant.svg`, `advisor-loop.svg`) — must be picked up by the SVGO/determinism CI gate.
- Full `mkdocs.yml` nav wiring deferred to Phase 18 (NAVDOC-01).

</code_context>

<specifics>
## Specific Ideas

- Grounding invariant phrasing must stay faithful to the shipped invariant: "fdars computes every number; the LLM only interprets and cites diagnostic values — it never fabricates numbers."
- Advisor-loop must make the Python-API-is-recommend-only distinction visible (it stops after *recommend*; MCP/Skill continue through re-run/compare).

</specifics>

<deferred>
## Deferred Ideas

- Per-surface page detail (Python API worked example, MCP tool reference, Agent Skill walkthrough) — Phases 15–17.
- `mkdocs.yml` nav section wiring + full-build gate — Phase 18.
- Diagram accessibility long-form `<title>`/`<desc>` (A11Y-01) — deferred to a future milestone.

</deferred>
