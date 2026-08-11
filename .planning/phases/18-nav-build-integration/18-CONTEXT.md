# Phase 18: Nav & Build Integration - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss grey areas auto-answered with recommended defaults per the autonomous-run instruction; grounded in the current `mkdocs.yml` nav).

<domain>
## Phase Boundary

Wire the four already-authored advisor pages into a new top-level "AI Advisor" section in `mkdocs.yml` nav, then run the full-build gate: the complete docs build succeeds with the new section, every new page's executable fence runs against the current API, and the two new advisor SVGs still pass the SVGO/determinism CI gate. Covers NAVDOC-01, NAVDOC-02. This is the milestone's final integration phase — no new page content is authored.

</domain>

<decisions>
## Implementation Decisions

### Nav Wiring (NAVDOC-01)
- Add ONE new top-level section titled **"AI Advisor"** to `mkdocs.yml` `nav:`, placed immediately after the `- Analyze:` block and before `- Examples:` (it sits naturally with the analytical capability sections; the advisor interprets analysis results).
- Section entries, in this order:
  - `Overview: advisor/index.md`
  - `Python API: advisor/python-api.md`
  - `MCP Server: advisor/mcp.md`
  - `Agent Skill: advisor/agent-skill.md`
- Match the existing nav idiom exactly (2-space indent under `nav:`, `- Label: path` entries, an `index.md` first entry as the section landing — mirrors `- Analyze:` / `analyze/index.md`).

### Full-Build Gate (NAVDOC-02)
- Run the complete docs build (`PYTHONPATH=scripts DOCS_FAST=1 mkdocs build`, and also a non-DOCS_FAST full build if feasible) and confirm exit 0 with all four advisor pages rendered under `site/advisor/`.
- Confirm the Phase 15 offline executed fence still runs in the full build (`FDARS_FENCE_OK` present in built HTML) and that no page unexpectedly requires the `[mcp]`/`[advisor]` extras or an API key.
- Confirm the two new advisor SVGs (`advisor-grounding-invariant.svg`, `advisor-loop.svg`) still pass the SVGO idempotence + determinism gate in the full build context.
- Confirm the cross-links between the four advisor pages resolve (no broken internal links reported by the build).

### Scope
- NO new page content authored; only `mkdocs.yml` nav wiring + build/gate verification. If the build surfaces a genuine broken link or a fence/SVG regression, fixing that minimal issue is in scope (it would be a real integration defect).

### Claude's Discretion
- Exact nav labels ("MCP Server" vs "Tool / MCP", "Agent Skill" vs "Skill") — keep concise and consistent with sibling labels.
- Whether to place the section after Analyze or elsewhere, if a clearly better fit emerges — default is after Analyze.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mkdocs.yml` `nav:` — top-level sections Home / Learn / Represent / Align / Regression / Monitoring / Analyze / Examples / Reference. The advisor section slots after Analyze. Existing idiom: `- Analyze:` then `- analyze/index.md` then `- Label: path` entries.
- `docs/advisor/{index,python-api,mcp,agent-skill}.md` — the four pages authored in Phases 14–17, currently unreachable from the nav.
- `docs/assets/diagrams/advisor-grounding-invariant.svg`, `advisor-loop.svg` — the two Phase 14 diagrams under the SVGO/determinism CI gate.

### Established Patterns
- Full build: `PYTHONPATH=scripts mkdocs build`; `DOCS_FAST=1` is a speed switch, not the determinism source of truth.
- SVGO gate: `svgo@3.3.4 --config svgo.config.mjs` pass2 == pass1.

### Integration Points
- `mkdocs.yml` (the only file edited for content wiring).
- The full `site/` build output.

</code_context>

<specifics>
## Specific Ideas

- This phase must NOT alter the four advisor page bodies — only nav wiring + verification. Keep the diff to `mkdocs.yml` minimal (one added section block).
- The gate is objective/automated (build exit 0 + FDARS_FENCE_OK present + SVGO idempotence + no broken internal links); a human check that the nav renders and the section reads in order is a nice-to-have but the automated gate is authoritative.

</specifics>

<deferred>
## Deferred Ideas

- Diagram accessibility long-form `<title>`/`<desc>` (A11Y-01) — future milestone.
- Examples editorial consolidation (EX2-01) — future milestone.
- HTTP/SSE MCP transport — out of scope.

</deferred>
