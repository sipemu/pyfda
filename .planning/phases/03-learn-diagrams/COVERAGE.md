# API Coverage Declaration — Phase 03: learn-diagrams

**Phase:** 03-learn-diagrams
**Scope:** All 6 learn/ concept diagrams (introduction.svg, custom-plotting.svg, simulation.svg, smoothing.svg, derivatives.svg, irregular-sampling.svg)
**Gate:** api-coverage (required before seal)

## Declaration

No external API integration: phase edits hand-authored static SVG diagrams and runs local SVGO/mkdocs tooling only.

**Note:** The SVGO lint gate (`npx svgo@3.3.4 --config svgo.config.mjs --quiet --input <file> --output -`) and the mkdocs build (`PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build`) are local developer tooling only — they run fully offline against files in the working tree, make no network requests during the gate checks, and do not require credentials or external service access.
