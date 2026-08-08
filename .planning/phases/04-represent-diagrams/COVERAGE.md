# Phase 04 — API Coverage Declaration

No external API integration: phase edits hand-authored static SVG diagrams and runs local SVGO/mkdocs tooling only.

The SVGO idempotence lint (`svgo@3.3.4`, check-only, stdout) and the `mkdocs build` are local dev tooling, not networked services — no external API, SDK, credential, or endpoint is involved.

## Scope verified

- **Migrated (1):** `depth-functions.svg` — restyled from legacy-outlier to STYLE_SPEC conformance (five-class `<style>` block, `role="img"`, `aria-label`; inline `font-size`/`font-family` removed). Content-preserving: paths, geometry, colours, and text unchanged (verified by before/after raster comparison).
- **Verified-only (6):** `fpca.svg`, `elastic-fpca.svg`, `basis-representation.svg`, `andrews-transformation.svg`, `streaming-depth.svg`, `distance-metrics.svg` — already accurate + conforming per the Phase 2 audit; re-proven against the live SVGO idempotence gate + STYLE_SPEC marker grep.
- **R-era:** none remain in any represent/ diagram (grep for `extendr`/`autoplot`/`ggplot`/`%>%`/`geom_`/`aes(` is clean; the intentional prose admonition in `andrews-transformation.md` is PROSE-OK and untouched).
