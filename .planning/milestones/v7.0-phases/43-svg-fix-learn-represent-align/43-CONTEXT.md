# Phase 43: SVG Fix — learn / represent / align - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Correct every flagged concept diagram in the **learn/ + represent/ + align/** batch (25 diagrams, the Phase 43 bucket in `42-AUDIT.md`) on all four fix axes — visual/layout, STYLE_SPEC conformance, XML source formatting, method-accuracy — and verify each on the built site (rendered PNG). This is the first of three section-batched SVG-fix phases (43 learn/represent/align, 44 analyze/monitoring/advisor, 45 regression/inference); the decisions below set the pattern for all three. Only `docs/assets/diagrams/*.svg` files in this batch are edited — no docs `.md` page content, no new diagrams (those are Phases 46+), no whole-site build (that is Phase 49).

**Phase 43 worklist (from `42-AUDIT.md` §2, Phase 43 bucket):**
- **Major (1):** `ex-sonar-tsrvf.svg` — full STYLE_SPEC migration (non-720 viewBox `0 0 700 400`; no `role="img"`/`aria-label`; no canonical `<style>` block with `.ttl/.sub/.lab/.sm/.mono`; inline-style/custom classes throughout).
- **Minor incl. method-accuracy FLAGs (8):** `smoothing.svg` (Panel-3 ghost polyline duplicates Panel-1 noise — remove/replace), `depth-functions.svg` (FLAG: verify `functional_boxplot()` is exported — it IS, added in v5.0 `fdars.depth`; confirm and keep or correct), `pace-fpca.svg` (subtitle ~130 chars overflows 720px — shorten/wrap), `elastic-alignment.svg` (FLAG: amplitude-vs-phase decomposition clarity), `banded-alignment.svg` (cost-matrix label overlap), `shift-registration.svg` (FLAG: "elastic warp" label contradicts the rigid `shift_register`/`least_squares_shift_registration` API — clarify/remove), `fpca.svg` + `elastic-fpca.svg` (inline `font-size=` mixed with CSS classes).
- **XML cleanup (3):** `basis-representation.svg`, `andrews-transformation.svg`, `distance-metrics.svg` (inline `font-size=` overrides alongside CSS classes).
- **OK (16):** left byte-unchanged (introduction, custom-plotting, simulation, derivatives, irregular-sampling, streaming-depth, imputation, interpolation-policy, advanced-alignment, landmark-registration, tsrvf, alignment-comparison, shape-analysis, + elastic-fpca/basis-representation/distance-metrics on the non-XML axes).

**Audit prose caveat to carry to the planner:** the verifier flagged 3 editorial nits in `42-AUDIT.md`'s ranked-list PROSE (not the authoritative scoring table): `depth-functions.svg` is cross-referenced under the Phase 44 block but BELONGS to Phase 43 (represent/); two Phase-44 block headers miscount; one diagram appears in both a Minor and an OK sublist. The scoring table + bucket totals (25/17/19=61) are correct — treat the scoring table as authoritative when the prose disagrees.
</domain>

<decisions>
## Implementation Decisions

### Fix Scope
- Fix **all Major + Minor** flagged issues in the batch; leave the 16 OK diagrams **byte-unchanged** (do not "polish" passing diagrams — churn risks regressions and breaks determinism).
- Every axis flagged for a diagram is addressed (a diagram flagged on multiple axes is fully corrected in one pass).

### Method-Accuracy FLAGs
- Resolve each method-accuracy FLAG **against the shipped `fdars` bindings** (read the referencing docs page + the relevant `src/*_mod.rs` / Python API), not by guessing:
  - `depth-functions.svg` — confirm `functional_boxplot()` is exported in `fdars.depth` (added v5.0 Phase 32); if confirmed, the reference is correct → no change beyond any other axis.
  - `shift-registration.svg` — the shipped shift-registration API is purely rigid (argmin over scalar δ); remove/relabel any "elastic warp" annotation that implies otherwise.
  - `smoothing.svg` — the Panel-3 "signal kept" ghost curve must not be a y-shifted copy of the Panel-1 noisy path; redraw as an independent smooth reference or remove.
  - `elastic-alignment.svg` — clarify amplitude-vs-phase per page prose if a factual mismatch; if it's a pedagogical judgment (not a factual error), fix conservatively and **escalate to the Phase 49 human review**.
- Genuine pedagogical judgment calls (not factual errors) are fixed conservatively and **surfaced in the phase SUMMARY for the Phase 49 blocking human diagram review** — do not silently guess a redesign.

### Per-Phase Verification Gate
- Per changed diagram: **SVGO idempotence** (`npx svgo@3.3.4 --config svgo.config.mjs --quiet --input <f> --output -`, run twice → byte-identical second pass) **+ `rsvg-convert` → PNG render** eyeballed for the visual/"built-site" check (overlaps, spacing, alignment, sizing). PNGs go to the scratchpad, never committed.
- **Defer the whole-site `mkdocs build --strict` to Phase 49 (GATE-01).** SVG-only edits do not change page builds, so a ~20-min strict build per fix phase is wasted; the per-diagram SVGO+PNG gate is the correct per-phase proof. (SC1's "built site" is satisfied by the PNG render in the fix phases; the true whole-site build is consolidated in Phase 49.)
- STYLE_SPEC conformance (SC2) checked by grep for the canonical markers (viewBox 720, the 5 CSS classes, `system-ui`, `role="img"`, `aria-label`) + reading source against `STYLE_SPEC.md`.

### Commit Granularity
- One commit per section (learn / represent / align), each landed after that section's per-section built-site (PNG) review passes (SC5). `ex-sonar-tsrvf.svg` commits with the align/ section (its audit bucket).

### Claude's Discretion
- Exact SVG edit details (label re-anchoring, subtitle wording, redrawn paths) at the executor's discretion so long as STYLE_SPEC holds, the method stays accurate, and SVGO idempotence + determinism pass.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/phases/42-diagram-audit/42-AUDIT.md` — the authoritative per-diagram scoring table + Phase 43 worklist.
- `docs/assets/diagrams/STYLE_SPEC.md` — canonical `<style>` block, palette, viewBox, aria conventions (copy the canonical style block verbatim for the `ex-sonar-tsrvf.svg` migration).
- `svgo.config.mjs` + pinned `svgo@3.3.4` — the check-only idempotence gate.
- Render recipe (memory: docs-diagram-verify-workflow): `.venv` + `rsvg-convert` to rasterise SVGs for visual inspection.
- Shipped bindings for method-accuracy checks: `src/depth_mod.rs`, `src/alignment_mod.rs`, `src/smoothing_mod.rs`, `python/fdars/` + the referencing docs pages under `docs/learn/`, `docs/represent/`, `docs/align/`.

### Established Patterns
- Diagrams are hand-authored inline SVG (no programmatic generation).
- Canonical baseline: `viewBox="0 0 720 300"` (or 720×480 for multi-panel), inline `<style>` classes, system-ui fonts, `role="img"` + `aria-label`.

### Integration Points
- Only diagrams in the learn/represent/align batch change; the referencing `.md` pages are NOT edited in this phase.
- Whole-site strict build + blocking human diagram review happen in Phase 49.

</code_context>

<specifics>
## Specific Ideas

- `ex-sonar-tsrvf.svg` is the one Major: it needs a full STYLE_SPEC migration (canonical `<style>` block, 720-width viewBox, `role="img"`+`aria-label`, replace inline-style/custom classes with `.ttl/.sub/.lab/.sm/.mono`) while preserving its TSRVF-shape-analysis method content and visual meaning.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (GATE-01) and the blocking human diagram method-accuracy review (GATE-02) → Phase 49.
- Accessibility long-form `<title>`/`<desc>` pass → future DIAG-FUT-01.
- `thumb/` regeneration if a fixed diagram's thumbnail visibly diverges → future DIAG-FUT-02 (only if it diverges).

</deferred>
