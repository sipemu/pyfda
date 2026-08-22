# Phase 44: SVG Fix — analyze / monitoring / advisor - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning
**Mode:** Fix-phase policy carried from Phase 43 (43-CONTEXT.md) — same decisions apply to 43/44/45; no new grey areas.

<domain>
## Phase Boundary

Correct every flagged concept diagram in the **analyze/ + monitoring/ + advisor/** batch (17-diagram Phase 44 bucket in `42-AUDIT.md`) on all four fix axes — visual/layout, STYLE_SPEC conformance, XML source formatting, method-accuracy — verified per-diagram via SVGO idempotence + `rsvg-convert` PNG render. SVG-only edits; the 10 OK diagrams stay byte-unchanged; no docs `.md` page content, no new diagrams, NO whole-site `mkdocs build --strict` (Phase 49).

**Phase 44 worklist (42-AUDIT.md §2 Phase 44 bucket — 7 flagged):**
- `elastic-clustering.svg` — **XML:** all text elements carry inline `font-size="11" style="fill:#333"` overrides bypassing the CSS classes; **content:** very sparse (4 bare flow boxes, little method detail vs analyze/ peers). Strip *redundant* overrides (keep any inline value that genuinely differs from its class — the Phase 43 lesson); if the diagram is genuinely thin vs peers, add modest method detail to match the section bar. Content enrichment that is a design judgment (not a factual fix) → do conservatively and surface for the Phase 49 human review.
- `outlier-detection.svg` — **XML:** inline `font-size=`/`style="fill:..."` overrides; **Visual:** bottom-row detection-method text overflows its rectangle containers (>170px at 10px); **Method-accuracy FLAG:** taxonomy labels read "Magnitude / Shape / **Amplitude**" — verify against `docs/analyze/outlier-detection.md` + the shipped `fdars.outliers` API whether the canonical term is "Phase" (or "magnitude/shape" only); correct if "Amplitude" is non-standard.
- `scoring-metrics.svg` — **Visual (Minor):** `ε(t)|` integral label and `Δ MAPE: rejects |y_true| ≈ 0` warning are cramped in the right panel; re-space/enlarge slightly. No XML/STYLE_SPEC issue.
- `clustering.svg`, `gmm-clustering.svg`, `seasonal-analysis.svg` — **XML (Minor):** inline `font-size=` on some elements; strip only the *redundant* ones (keep intentional distinct-value overrides). Layouts otherwise clean.
- `depth-functions.svg` — already resolved in Phase 43 (`functional_boxplot` confirmed exported at `src/depth_mod.rs:625`); **NO re-touch in Phase 44** (it belongs to represent/ = Phase 43; its appearance in the §2 Phase-44 prose is the known audit editorial nit).

**OK (10, byte-unchanged):** tolerance-bands, functional-outliers, functional-boxplot, equivalence-testing, covariance-functions, functional-statistics, spm (redrawn), advanced-spm, profile-partial-monitoring, advisor-loop, advisor-grounding-invariant.

**Audit prose caveat:** §1 scoring table is authoritative over §2 prose (verifier found miscounted §2 Phase-44 headers + the depth-functions cross-ref).
</domain>

<decisions>
## Implementation Decisions (carried from Phase 43 — user-approved for 43/44/45)

### Fix Scope
- Fix all **Major + Minor** flagged issues in the batch; leave the 10 OK diagrams **byte-unchanged**.
- For XML "inline font-size" flags: strip only overrides whose value **duplicates** the CSS class size (redundant cruft); **keep** any inline value that genuinely differs from its class (intentional per-element size/color — the confirmed Phase 43 lesson: e.g. `.sm` is 11px but an element sets 9px). Verify per element before removing.

### Method-Accuracy FLAGs
- `outlier-detection.svg` "Amplitude" taxonomy: verify against `docs/analyze/outlier-detection.md` + `fdars.outliers` / shipped bindings; if the canonical taxonomy is "magnitude / shape" (or "…/ phase"), correct the label; do not guess.
- Genuine pedagogical/design judgment calls (e.g. how much to enrich `elastic-clustering.svg`) → fixed conservatively and **surfaced in the SUMMARY for the Phase 49 blocking human diagram review**.

### Per-Phase Verification Gate
- Per changed diagram: SVGO idempotence (`npx svgo@3.3.4 --config svgo.config.mjs`, twice → byte-identical 2nd pass, check-only) + `rsvg-convert` PNG render eyeballed (PNGs to scratchpad, never committed). NO whole-site build (Phase 49).
- STYLE_SPEC conformance via grep for the canonical markers (viewBox 720, 5 CSS classes, system-ui, `role="img"`, `aria-label`).

### Commit Granularity
- One commit per section (analyze / monitoring / advisor). (monitoring & advisor have no flagged diagrams → likely a single analyze/ commit; use judgment.)

### Claude's Discretion
- Exact edit details (label re-spacing, override stripping, elastic-clustering enrichment extent) at the executor's discretion within STYLE_SPEC + method-accuracy + SVGO idempotence.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/phases/42-diagram-audit/42-AUDIT.md` — §1 scoring table (authoritative) + §2 Phase 44 worklist.
- `.planning/phases/43-svg-fix-learn-represent-align/43-CONTEXT.md` + `43-01-SUMMARY.md` — the established fix-phase pattern + the "intentional inline font-size" precedent.
- `docs/assets/diagrams/STYLE_SPEC.md` — conformance rubric.
- `svgo.config.mjs` + pinned `svgo@3.3.4`; `.venv` + `rsvg-convert`.
- Method-accuracy sources: `docs/analyze/outlier-detection.md`, `docs/analyze/elastic-clustering.md`, `src/outliers_mod.rs`, `python/fdars/`.

### Established Patterns
- Canonical baseline: viewBox 720-wide, `.ttl/.sub/.lab/.sm/.mono` classes, system-ui, `role="img"`+`aria-label`. Hand-authored inline SVG.

### Integration Points
- Only analyze/monitoring/advisor flagged diagrams change; referencing `.md` pages NOT edited; whole-site build + human review at Phase 49.

</code_context>

<specifics>
## Specific Ideas

- `elastic-clustering.svg` is the fuzziest item: it's both an XML-override cleanup AND a possible content-enrichment (it's sparse vs analyze/ peers). Keep the fix bounded — strip redundant overrides, add modest method detail only if clearly warranted, and flag the enrichment extent for Phase 49 rather than a speculative redesign.
- `outlier-detection.svg` needs a real taxonomy verification ("Amplitude" vs canonical) plus fixing bottom-row text overflow.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (GATE-01) + blocking human diagram review (GATE-02) → Phase 49.
- Accessibility `<title>`/`<desc>` pass → DIAG-FUT-01. thumb regeneration if diverged → DIAG-FUT-02.

</deferred>
