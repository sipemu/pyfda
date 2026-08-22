# Phase 42: Diagram Audit - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a ranked, per-section diagram fix list — every concept diagram in `docs/assets/diagrams/` (61 files; `cards/` and `thumb/` excluded) scored on the four fix axes (visual/layout quality, STYLE_SPEC conformance, XML source formatting, method-accuracy against the shipped `fdars` bindings) — plus a confirmed diagram-coverage gap list (which `examples/` and advisor surface pages lack a concept SVG) and a thin-page extension list (the sub-mature v4–v6 method pages DEPTH-01/02 must extend). This phase is **read-only analysis**: it produces the `42-AUDIT.md` evidence document that gates the downstream fix (43–45), coverage (46–47), and depth (48) phases. NO diagram is edited and NO page is rewritten in this phase.

</domain>

<decisions>
## Implementation Decisions

### Audit Report — Format & Scoring
- Deliverable is `.planning/phases/42-diagram-audit/42-AUDIT.md`, mirroring the v1.0 `02-AUDIT.md` precedent: a per-diagram × 4-axis table, a ranked per-section fix list, a coverage-gap list, and a thin-page extension list.
- Each diagram scored per axis on a 3-level severity scale — **OK / Minor / Major** — with a one-line note on every non-OK cell explaining the specific issue.
- The ranked fix list orders diagrams by severity (Major first) then by docs section, so each downstream fix phase (43 learn/represent/align, 44 analyze/monitoring/advisor, 45 regression/inference) gets an explicit, evidence-backed worklist.
- Method-accuracy cells **flag suspected** inaccuracies for verification against the shipped `fdars` bindings during the fix phases — the audit does not fully re-derive each method here (that verification + correction happens in 43–45, confirmed by the Phase 49 blocking human review).

### Assessment Method
- Visual/layout quality is judged by rendering each SVG → PNG with `rsvg-convert` (the established docs-diagram-verify recipe) and eyeballing for overlapping labels, cramped spacing, misalignment, and inconsistent sizing — visual defects are not reliably detectable from SVG source alone.
- The other three axes (STYLE_SPEC conformance, XML formatting, method-accuracy) are judged by reading the SVG source against `docs/assets/diagrams/STYLE_SPEC.md` and the shipped bindings/existing page prose.
- STYLE_SPEC conformance is cross-checked with the pinned SVGO idempotence invocation (`npx svgo@3.3.4 --config svgo.config.mjs`) where useful, but the audit does not rewrite any committed SVG.

### Thin-Page Extension Threshold
- The thin-page list is decided by **section-structure completeness** — a page is flagged when it lacks the mature-page structure (intro, method explanation, worked example, parameters, caveats/interpretation) — using ~200 lines only as a soft signal, not a hard cutoff.
- Seed list to confirm/expand: `regression/concurrent-regression`, `regression/functional-glm`, `represent/pace-fpca`, `inference/interval-inference`, `represent/interpolation`, `represent/imputation`, `analyze/scoring-metrics`, `analyze/functional-statistics`.

### Claude's Discretion
- Exact table columns/ordering within `42-AUDIT.md`, and how the ranked list is chunked to the three fix phases, are at Claude's discretion so long as each fix phase gets a clear worklist.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/STYLE_SPEC.md` — canonical style contract (typography classes `.ttl/.sub/.lab/.sm/.mono`, colour palette, `FDARS_COLORS`, viewBox, aria conventions) — the STYLE_SPEC-conformance rubric.
- `.planning/milestones/v1.0-phases/02-audit/02-AUDIT.md` — the prior audit-report format precedent (pages scored on style/accuracy axes + ranked GAP/EX list).
- `svgo.config.mjs` + pinned `svgo@3.3.4` — the check-only idempotence gate (`svgo(svgo(svg)) == svgo(svg)`); never rewrites committed SVGs.
- `scripts/docs_fig.py` (`FDARS_COLORS`) — data-curve palette referenced by STYLE_SPEC.
- `.planning/codebase/*.md` — codebase maps (CONVENTIONS, STRUCTURE, STACK, TESTING, …).

### Established Patterns
- 61 concept diagrams in `docs/assets/diagrams/`; every method page already references one; the coverage gap is the ~21 `examples/` pages + 5 advisor surface pages (`python-api`/`mcp`/`providers`/`agent-skill`/`aspects`).
- Diagrams are hand-authored inline SVG (standing decision — no programmatic generation).
- Render recipe (memory: docs-diagram-verify-workflow): venv + `PYTHONPATH=scripts` + `DOCS_FAST`, `rsvg-convert` to rasterise SVGs for visual inspection.

### Integration Points
- `42-AUDIT.md` is consumed by the plans for Phases 43–48 as their worklist source.
- Docs sections in scope: learn, represent, align, analyze, monitoring, advisor, regression, inference.

</code_context>

<specifics>
## Specific Ideas

- Reconcile the diagram count: milestone framing said "68" but the working tree has **61** top-level concept SVGs — the audit produces the authoritative inventory and states the true count.

</specifics>

<deferred>
## Deferred Ideas

- `cards/` and `thumb/` SVGs are out of scope for the audit (decorative); only revisited later if a fixed concept diagram's thumbnail visibly diverges (future DIAG-FUT-02).
- Accessibility long-form `<title>`/`<desc>` + `aria-labelledby` pass is deferred (DIAG-FUT-01 / A11Y-01).

</deferred>
