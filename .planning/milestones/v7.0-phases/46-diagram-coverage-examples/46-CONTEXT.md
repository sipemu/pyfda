# Phase 46: Diagram Coverage — examples pages - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning
**Mode:** Coverage phase — scope determined by 42-AUDIT.md §3a + DIACOV-01; policy set below (no new grey areas; consistent with the shipped `ex-sonar-tsrvf.svg` precedent).

<domain>
## Phase Boundary

Add a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG to each of the **20 `docs/examples/*.md` pages** that currently lack one (DIACOV-01). Each new diagram is a **workflow/pipeline diagram** for that specific analysis (dataset → fdars methods → result/insight) — the genre established by the one existing example diagram `ex-sonar-tsrvf.svg` ("validation framework" flow), NOT a generic method concept diagram. Create the SVG in `docs/assets/diagrams/ex-<page-slug>.svg` and embed it near the top of its page. `docs/examples/index.md` gets no diagram (navigation index). NO method-page diagrams change; NO whole-site `mkdocs build --strict` (Phase 49).

**The 20 target pages + what each diagram depicts (from 42-AUDIT.md §3a):**
- `andrews-wine.md` → Andrews curve + depth overview (core entry point)
- `andrews-wine-intro.md` → intro to the Andrews transformation
- `andrews-wine-clustering.md` → before/after cluster assignment
- `andrews-wine-qc.md` → QC tolerance-band overlay
- `biopharma-monitoring.md` → SPM Phase I/II monitoring
- `canadian-depth-centrality.md` → depth-centrality ordering / functional boxplot
- `canadian-function-on-scalar.md` → function-on-scalar β(t) per month
- `canadian-precipitation.md` → basis representation + smoothing pipeline
- `canadian-seasonal.md` → seasonal decomposition / period estimation
- `canadian-weather.md` → multi-method overview of the dataset
- `cross-validation.md` → CV fold split → error curve
- `explainability-regions.md` → importance curve with highlighted region
- `functional-outlier-workflow.md` → outlier-detection pipeline (magnitude/shape)
- `growth-alignment.md` → elastic alignment on growth data
- `inline-monitoring.md` → streaming / inline SPM monitoring
- `phoneme-shape.md` → shape-based classification
- `tecator-conformal-coverage.md` → conformal coverage guarantee
- `tecator-monitoring.md` → monitoring on Tecator data
- `tecator-regression.md` → scalar-on-function regression
- `tolerance-vs-conformal.md` → tolerance band vs conformal band comparison

Already covered (no action): `sonar-tsrvf.md` (has `ex-sonar-tsrvf.svg`).
</domain>

<decisions>
## Implementation Decisions

### Diagram genre & content
- Each example diagram is a **workflow/pipeline** view of that example's actual analysis: the dataset it loads (`docs/data/`), the specific fdars methods it calls, and the result/insight the page teaches — matching the `ex-sonar-tsrvf.svg` precedent. Method-accurate to what the example page ACTUALLY does: read each `docs/examples/<page>.md` (and the fdars methods it invokes) before drawing. Do NOT invent steps the example doesn't perform.
- Keep each diagram appropriately scoped (2–5 panels / a clear left-to-right or staged flow) — not maximal; enough to make the example's arc visually clear. Consistency across the 20 matters more than per-diagram ambition.

### Style & naming
- Hand-authored inline SVG, STYLE_SPEC-conformant: canonical `<style>` block with `.ttl/.sub/.lab/.sm/.mono`, viewBox 720-wide (720×300 or 720×480 per content), `role="img"` + descriptive `aria-label`, system-ui fonts, FDARS palette.
- File name `docs/assets/diagrams/ex-<page-slug>.svg` (e.g. `ex-canadian-weather.svg`), mirroring `ex-sonar-tsrvf.svg`.

### Embedding
- Embed near the top of each page (after the H1 / intro para) via `![<page title> — <short caption>](../assets/diagrams/ex-<slug>.svg){ .fdars-diagram }`, matching the `sonar-tsrvf.md` pattern (line ~22). This is the ONE `.md` edit per page allowed in this phase (adding the image reference) — do NOT otherwise rewrite page prose (page depth is Phase 48).

### Per-diagram verification gate
- Per new diagram: SVGO idempotence (`npx svgo@3.3.4 --config svgo.config.mjs`, twice → byte-identical 2nd pass, check-only) + `rsvg-convert` PNG render eyeballed (scratchpad, not committed). NO whole-site build (Phase 49).
- Grep-verify each page now references its new SVG.

### Commit granularity
- Batched by dataset/theme family (e.g. andrews-wine group, canadian group, tecator group, misc) — one commit per batch, after that batch's PNG review.

### Escalation
- Any example whose method is ambiguous or where the "right" depiction is a judgment call → draw the best-supported version and surface it in the SUMMARY for the Phase 49 blocking human diagram review.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/assets/diagrams/ex-sonar-tsrvf.svg` — the one existing example concept diagram (workflow genre) + its migration in Phase 43 = the STYLE_SPEC template to copy.
- `docs/assets/diagrams/STYLE_SPEC.md` — style contract; `svgo.config.mjs` + pinned `svgo@3.3.4`; `.venv` + `rsvg-convert`.
- `docs/examples/*.md` — the pages (read each to make its diagram method-accurate); `docs/data/` datasets; `docs/includes/load-*.md` snippet includes show which datasets/methods each example uses.
- `.planning/phases/42-diagram-audit/42-AUDIT.md` §3a — the per-page depiction rationale (authoritative worklist).

### Established Patterns
- Embed: `![alt](../assets/diagrams/NAME.svg){ .fdars-diagram }` near page top.
- Existing method-page diagrams (learn/represent/align/analyze/regression/inference) are the visual-quality bar; example diagrams match STYLE_SPEC but use the workflow/pipeline genre.

### Integration Points
- New SVGs in `docs/assets/diagrams/`; one image-reference line added per example page. No nav/mkdocs.yml change (pages already in nav). Whole-site build + human review at Phase 49.

</code_context>

<specifics>
## Specific Ideas

- 20 bespoke method-accurate SVGs is the heaviest phase — a tracer-first approach (author ONE exemplar end-to-end, e.g. `ex-canadian-weather.svg`, prove the create→embed→SVGO→PNG pipeline, then scale by dataset family) keeps it manageable.
- `thumb/ex-*.svg` navigation thumbnails already exist and are OUT of scope (decorative); do not touch them.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (GATE-01) + blocking human diagram review (GATE-02) → Phase 49.
- Page prose depth/rewrites → Phase 48 (this phase only adds the diagram + its embed line).
- Accessibility long-form `<title>`/`<desc>` → DIAG-FUT-01.

</deferred>
