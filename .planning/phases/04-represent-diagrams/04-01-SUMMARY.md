---
phase: 04-represent-diagrams
plan: 01
status: complete
completed: 2026-08-08
requirements: [DIA-02]
---

# 04-01 SUMMARY — Migrate depth-functions.svg to STYLE_SPEC (GAP-0002)

Executed lean (direct edit, no subagent ceremony) per user request.

## What was done

Restyled `docs/assets/diagrams/depth-functions.svg` from legacy-outlier to STYLE_SPEC conformance — a **content-preserving** change:
- Added the canonical five-class `<style>` block (`.ttl/.sub/.lab/.sm/.mono`, `system-ui`).
- Added `role="img"` and `aria-label="Functional Depth: Ranking Curves by Centrality"` to the root; removed the inline `font-family="'Segoe UI'…"`.
- Replaced every `<text>` element's inline `font-size`/`font-weight` with the matching class (bold→`.lab`, regular→`.sm`, title→`.ttl`, subtitle→`.sub`), keeping original sizes via `font-size` overrides.
- **Colour fidelity:** preserved each element's meaningful colour (blue=central, red/orange=outlier, green=depth, purple=boxplot, orange=tolerance) via inline `style="fill:#…"`. This was necessary because a CSS class `fill` overrides a `fill=` presentation attribute (empirically verified with a raster test) — the peer diagrams' `fill=` attributes actually render grey; `style=` wins.

## Verification (all green)

- SVGO idempotence gate on depth-functions.svg: **SVGO_OK**.
- STYLE_SPEC markers present: viewBox 0 0 720, `.ttl .sub .lab .sm .mono`, system-ui, role=img, aria-label — all OK. `Segoe UI` count 0, `font-family=` count 0.
- Before/after raster render (rsvg-convert) compared: **visually identical** except the intended Segoe UI→system-ui font swap. Colours, geometry, layout, text unchanged.
- User approved the rendered result ("fine, go on").

## Design decision

Migrated (restyled), NOT redrawn — the diagram's content was rated accurate by the Phase 2 audit; only the typography/accessibility axis was non-conforming.

## Files

- Modified: `docs/assets/diagrams/depth-functions.svg` (commit `60d9c39`)
