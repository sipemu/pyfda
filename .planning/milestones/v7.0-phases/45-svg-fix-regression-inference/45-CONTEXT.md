# Phase 45: SVG Fix — regression / inference - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning
**Mode:** Fix-phase policy carried from Phase 43 (43-CONTEXT.md) — same decisions apply to 43/44/45; no new grey areas.

<domain>
## Phase Boundary

Correct every flagged concept diagram in the **regression/ + inference/** batch (19-diagram Phase 45 bucket in `42-AUDIT.md`; completes the full 61-diagram sweep) on all four fix axes — visual/layout, STYLE_SPEC conformance, XML source formatting, method-accuracy — verified per-diagram via SVGO idempotence + `rsvg-convert` PNG render. SVG-only edits; the 15 OK diagrams stay byte-unchanged; no docs `.md` page content, no new diagrams, NO whole-site `mkdocs build --strict` (Phase 49).

**Phase 45 worklist (42-AUDIT.md §2 Phase 45 bucket — 4 flagged):**
- `scalar-on-function.svg` — **Method-accuracy FLAG (pedagogical):** β̂(t) coefficient curve is a small inset in Panel 3, secondary to the fitted-vs-actual scatter. Verify against `docs/regression/scalar-on-function.md` whether the β(t) panel is prominent enough; if it's a factual issue, fix; if it's a design judgment, apply a conservative improvement (or leave) and **surface for the Phase 49 human review**.
- `elastic-multinomial.svg` — **Visual + XML:** 4-wide OvR panel layout is cramped at 720×300 (small text); inline `font-size=` overrides. Consider giving it more vertical room (720×480) and/or re-spacing so the OvR boxes read cleanly; strip only REDUNDANT overrides (keep intentional distinct values). Method content is accurate — preserve it.
- `functional-glm.svg` — **Method-accuracy FLAG + XML:** the Gamma-family link annotation `inverse g(μ) = 1/μ` — **verify against the shipped fdars GLM** (`src/regression_mod.rs` / `python/fdars` + `docs/regression/functional-glm.md`) whether the Gamma family uses the inverse canonical link (1/μ) or log link, and whether the R-comparison note is misleading; correct if wrong. XML: inline `style="fill:#dc3545"` on the Gamma color annotation — keep if it's a semantic color (intentional), it is not a redundant font-size.
- `inference-permutation-test.svg` — **XML (Minor):** inline `font-size=` on some elements; strip only redundant ones (keep intentional distinct values). Content OK.

**OK (15, byte-unchanged):** function-on-scalar, classification, elastic-regression, scalar-on-shape, concurrent-regression, cross-validation, regression-diagnostics, uncertainty-quantification, explainability, conformal-prediction, conformal-classification, robust-regression, inference-anova, inference-scb, itp-interval-inference.

**Audit prose caveat:** §1 scoring table is authoritative over §2 prose.
</domain>

<decisions>
## Implementation Decisions (carried from Phase 43 — user-approved for 43/44/45)

### Fix Scope
- Fix all **Major + Minor** flagged issues; leave the 15 OK diagrams **byte-unchanged**.
- XML "inline font-size" flags: strip only overrides whose value **duplicates** the CSS class size; **keep** intentional distinct values and semantic `style="fill:…"` colors (the Phase 43/44 lesson — verify per element against STYLE_SPEC class sizes `.ttl=17 .sub=12 .lab=13 .sm=11 .mono=12`).

### Method-Accuracy FLAGs
- `functional-glm.svg` Gamma link: verify the actual fdars Gamma canonical link (inverse `1/μ` vs log) against `src/regression_mod.rs`/`python/fdars` + `docs/regression/functional-glm.md`; correct the annotation if it misstates the shipped behavior. (Note: PROJECT.md records a v6.0 research finding that "Gamma GLM uses inverse canonical link 1/μ and its AIC is NOT comparable to R glm()" — cross-check the diagram against this.)
- `scalar-on-function.svg` β(t) prominence: pedagogical judgment → conservative fix or leave + **surface for Phase 49 human review**.
- Genuine judgment calls surfaced in the SUMMARY for the Phase 49 blocking human diagram review — do not guess a redesign.

### Per-Phase Verification Gate
- Per changed diagram: SVGO idempotence (`npx svgo@3.3.4 --config svgo.config.mjs`, twice → byte-identical 2nd pass, check-only) + `rsvg-convert` PNG render eyeballed (PNGs to scratchpad, never committed). NO whole-site build (Phase 49).
- STYLE_SPEC conformance via grep for the canonical markers (viewBox 720, 5 CSS classes, system-ui, `role="img"`, `aria-label`). Note: if `elastic-multinomial.svg` height changes 300→480, the viewBox width stays 720 — keep STYLE_SPEC conformant.

### Commit Granularity
- One commit per section (regression / inference).

### Claude's Discretion
- Exact edit details at the executor's discretion within STYLE_SPEC + method-accuracy + SVGO idempotence.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/phases/42-diagram-audit/42-AUDIT.md` — §1 scoring table (authoritative) + §2 Phase 45 worklist.
- `.planning/phases/43-svg-fix-*/43-01-PLAN.md` + `44-*/44-01-PLAN.md` — established fix-phase plan shape + the intentional-override precedent.
- `docs/assets/diagrams/STYLE_SPEC.md`; `svgo.config.mjs` + pinned `svgo@3.3.4`; `.venv` + `rsvg-convert`.
- Method-accuracy sources: `src/regression_mod.rs`, `python/fdars/`, `docs/regression/functional-glm.md`, `docs/regression/scalar-on-function.md`.

### Established Patterns
- Canonical baseline: viewBox 720-wide, `.ttl/.sub/.lab/.sm/.mono` classes, system-ui, `role="img"`+`aria-label`. Hand-authored inline SVG.

### Integration Points
- Only regression/inference flagged diagrams change; referencing `.md` pages NOT edited; whole-site build + human review at Phase 49.

</code_context>

<specifics>
## Specific Ideas

- `functional-glm.svg` Gamma-link is the load-bearing method-accuracy check — resolve it against the shipped bindings, not R conventions.
- `elastic-multinomial.svg` may warrant a height bump (720×300 → 720×480) to de-cramp the OvR panels — acceptable as long as viewBox width stays 720 and STYLE_SPEC holds.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (GATE-01) + blocking human diagram review (GATE-02) → Phase 49.
- Accessibility `<title>`/`<desc>` pass → DIAG-FUT-01. thumb regeneration if diverged → DIAG-FUT-02.

</deferred>
