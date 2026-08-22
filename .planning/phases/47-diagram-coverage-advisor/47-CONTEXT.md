# Phase 47: Diagram Coverage — advisor surface pages - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning
**Mode:** Coverage phase — scope determined by 42-AUDIT.md §3b + DIACOV-02; policy consistent with Phase 46 and the existing advisor-overview diagrams.

<domain>
## Phase Boundary

Add a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG to each of the **5 advisor surface pages** that lack one (DIACOV-02): `advisor/python-api.md`, `advisor/mcp.md`, `advisor/providers.md`, `advisor/agent-skill.md`, `advisor/aspects.md`. (The advisor `index.md` already has 2 diagrams: `advisor-grounding-invariant.svg`, `advisor-loop.svg` — this phase reverses the v2.1 "surface pages diagram-free" choice.) Each new diagram is an **architectural / flow diagram** (the genre of the two existing advisor diagrams), accurate to the SHIPPED advisor code. Create in `docs/assets/diagrams/advisor-<slug>.svg`; embed near the page top via `![alt](../assets/diagrams/advisor-<slug>.svg){ .fdars-diagram }` (the ONLY `.md` edit per page — no prose rewrite). NO whole-site build (Phase 49). No existing diagram/page content changed beyond the embed line.

**The 5 target pages + what each diagram depicts (from 42-AUDIT.md §3b):**
- `advisor/python-api.md` → the `advise()` call pattern + response (`Advice`) structure — recommend-only surface (`fdars.advisor.advise(...)` → schema-validated `Advice` with action/kind/rationale/expected_effect/evidence).
- `advisor/mcp.md` → agent ↔ MCP ↔ fdars boundary with the by-reference **handle model** (`HandleRegistry`, `fdars_build_diagnostics` / `fdars_run_method` / `fdars_compare_run`, stdio); the MCP boundary is provably LLM-free.
- `advisor/providers.md` → provider configuration + selection precedence flow (Anthropic / OpenAI-compatible / Gemini / Ollama adapters behind the `Provider` protocol; extras).
- `advisor/agent-skill.md` → the Agent-Skill execution flow (git-URL install; interpret→recommend→re-run→compare) vs the Python-API mode.
- `advisor/aspects.md` → the per-aspect taxonomy (the 12+ fdars aspects) × the three grounded task families (interpret / parameter-guidance / method-guidance) through one shared schema/prompt.

**Grounding invariant is the hard constraint** (as in the advisor code): fdars computes every number; the LLM only interprets/cites. Any advisor diagram must not imply the LLM computes diagnostics.
</domain>

<decisions>
## Implementation Decisions

### Diagram genre & content
- Architectural/flow diagrams matching the two existing advisor diagrams' look (`advisor-grounding-invariant.svg`, `advisor-loop.svg`). Method-accurate to the SHIPPED advisor code — read the referencing page + the relevant code (`python/fdars/advisor/`, `python/fdars/mcp/`, `.claude/skills/fdars-advisor/SKILL.md`) before drawing. Do NOT depict surfaces/behaviors that don't exist (e.g. MCP stays LLM-free; provider precedence as actually implemented).
- Keep each scoped to a clear flow (2–5 nodes/panels).

### Style & naming
- Hand-authored inline SVG, STYLE_SPEC-conformant: canonical `<style>` block + `.ttl/.sub/.lab/.sm/.mono`, viewBox 720-wide, `role="img"` + descriptive `aria-label`, FDARS palette. Name `docs/assets/diagrams/advisor-<slug>.svg` (advisor-python-api / advisor-mcp / advisor-providers / advisor-agent-skill / advisor-aspects).

### Embedding
- Embed near the page top via `![alt](../assets/diagrams/advisor-<slug>.svg){ .fdars-diagram }` — the ONLY `.md` edit per page. No prose rewrite (Phase 48 is not scoped to advisor pages anyway).

### Per-diagram verification gate
- Per new diagram: SVGO idempotence (`npx svgo@3.3.4 --config svgo.config.mjs`, twice → byte-identical 2nd pass, check-only) + `rsvg-convert` PNG eyeballed (scratchpad, not committed). NO whole-site build. Grep-verify each page references its new SVG. Reuse the Phase 46 gate helpers (`check-ex.sh`-style) if convenient.

### Commit granularity
- One commit for the batch (5 diagrams) or split python-api/mcp vs providers/agent-skill/aspects — planner's judgment; after PNG review.

### Escalation
- Any advisor flow whose "right" depiction is a judgment call → best-supported version + surface in SUMMARY for the Phase 49 blocking human diagram review. Grounding-invariant fidelity is non-negotiable.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/advisor-grounding-invariant.svg`, `advisor-loop.svg` — the STYLE_SPEC-conformant advisor-diagram template (architectural genre).
- `docs/advisor/*.md` — the 5 pages (read each for accuracy); `python/fdars/advisor/` (advise, providers, schema), `python/fdars/mcp/` (server, HandleRegistry, tools), `.claude/skills/fdars-advisor/SKILL.md`.
- `docs/assets/diagrams/STYLE_SPEC.md`; `svgo.config.mjs` + pinned `svgo@3.3.4`; `.venv` + `rsvg-convert`; Phase 46 gate helpers.
- `.planning/phases/42-diagram-audit/42-AUDIT.md` §3b — the per-page depiction rationale.

### Established Patterns
- Embed: `![alt](../assets/diagrams/advisor-<slug>.svg){ .fdars-diagram }` near page top.
- Grounding invariant (v2.0): fdars computes numbers, the LLM only cites them — every advisor diagram must respect this.

### Integration Points
- New SVGs in `docs/assets/diagrams/`; one embed line per advisor page. No nav change. Whole-site build + human review at Phase 49.

</code_context>

<specifics>
## Specific Ideas

- The `advisor/mcp.md` diagram must keep the MCP boundary provably LLM-free (by-reference handles; no LLM in the compute path) — a common place to accidentally misdepict.
- Tracer-first: author ONE advisor diagram end-to-end (recommend `advisor-python-api.svg` — the core recommend-only surface) to prove the pipeline, then the other 4.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (GATE-01) + blocking human diagram review (GATE-02) → Phase 49.
- Advisor page prose depth → not in this milestone's DEPTH scope (Phase 48 targets thin v4–v6 method pages, not advisor pages).
- Accessibility `<title>`/`<desc>` → DIAG-FUT-01.

</deferred>
