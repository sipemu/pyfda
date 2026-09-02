# Phase 60: Diagram Quality Audit - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a scored inventory of all 156 hand-authored SVGs — 90 concept (`docs/assets/diagrams/`), 8 section cards (`docs/assets/cards/`), 58 gallery thumbnails (`docs/assets/thumb/`) — as the milestone-gating artifact. Each SVG is scored on four axes: design/geometry quality, STYLE_SPEC conformance, accessibility, and thumb/card-to-concept sync. This phase produces evidence and worklists ONLY — no diagram is corrected here. Corrections happen in Phases 61–63 (concept), sync/coverage in Phase 64, gate/refresh in Phase 65.

</domain>

<decisions>
## Implementation Decisions

### Audit Rubric & Method
- **Scoring:** per-axis severity scale — `OK` / `Minor` / `Major` / `Critical` — plus an overall per-diagram verdict. Actionable for triage (Major/Critical drive the correction worklists).
- **Visual inspection:** render all 156 SVGs to PNG with `rsvg-convert` and visually score each — the only reliable way to catch mismatched-line / misaligned-endpoint / overlapping-element / layout defects (source/XML inspection alone misses them). Follows the project's diagram-verify workflow.
- **Artifact:** a single `60-AUDIT.md` in the phase dir, containing: (a) per-section scored tables covering all 156 SVGs, (b) ranked per-section fix worklists mapped to the correction phases — 61 (learn/represent/align), 62 (analyze/monitoring/advisor), 63 (regression/inference/examples), (c) the COVER-01 coverage-gap list (pages/methods lacking a concept diagram) for Phase 64, and (d) the SYNC-01/SYNC-02 drift list (thumbs/cards that no longer match their concept diagrams) for Phase 64.
- **Drift detection:** map each thumbnail and card to its corresponding concept diagram, compare rendered PNGs, and flag content/visual mismatch as drift.

### Four scoring axes (per success criteria)
- **Design/geometry quality** — mismatched lines, misaligned endpoints, overlapping/misplaced elements, layout/spacing/label-overlap/panel-sizing.
- **STYLE_SPEC conformance** — viewBox conventions, canonical `<style>` block, colour palette, stroke weights, panel patterns (per `docs/assets/diagrams/STYLE_SPEC.md`).
- **Accessibility** — `role="img"`, title-matching `aria-label`, and presence/adequacy of long-form `<title>`/`<desc>`/`aria-labelledby` on complex diagrams.
- **Sync** — thumb-to-concept and card-to-concept fidelity.

### Claude's Discretion
- Exact table columns/format within `60-AUDIT.md`, PNG render resolution, how findings are ranked within a section, and any helper scripting used to batch-render — all at Claude's discretion, provided the four success criteria are met.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/STYLE_SPEC.md` — the conformance rubric source (note: its status counts, e.g. "34 of 43", are stale against today's 90 concept diagrams; SPEC-02 in Phase 65 refreshes them — do NOT fix the spec here, just score against its rules).
- `rsvg-convert` — available for SVG→PNG rendering (per the project diagram-verify workflow).
- v7.0 Phase 42 produced a comparable 61-diagram 4-axis scored inventory — the direct precedent for this phase's artifact shape (archived under `.planning/milestones/v7.0-phases`).

### Established Patterns
- Diagrams are hand-authored inline SVG referenced as `![...](../assets/diagrams/NAME.svg){ .fdars-diagram }`.
- Section index gallery pages (`docs/*/index.md`) reference `../assets/cards/<section>.svg` and `../assets/thumb/<name>.svg` — the mapping source for card/thumb → section and thumb → concept association.

### Integration Points
- Downstream phases 61/62/63/64 consume the worklists and gap/drift lists this phase produces.

</code_context>

<specifics>
## Specific Ideas

- Docs sections for per-section grouping: learn, represent, align, analyze, monitoring, advisor, regression, inference, examples.
- Docs-only phase — NO diagram edits, NO fdars-core/binding/advisor changes, NO package version bump.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
