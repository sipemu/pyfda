# Phase 07 — API Coverage Declaration

No external API integration: phase edits hand-authored static SVG diagrams and runs local SVGO/mkdocs tooling only. (This phase made no diagram edits — it was verify-only.)

The SVGO idempotence lint (`svgo@3.3.4`, check-only, stdout) and `mkdocs build` are local dev tooling, not networked services. The `fdars.conformal` calls used for method verification are local library calls (the compiled extension), not an external API.

## Scope verified

- **Verified-only (12):** all regression/ diagrams (classification, conformal-classification, conformal-prediction, cross-validation, elastic-regression, explainability, function-on-scalar, regression-diagnostics, robust-regression, scalar-on-function, scalar-on-shape, uncertainty-quantification) — already conforming; re-proven against the live SVGO gate + STYLE_SPEC markers.
- **Method verification:** `conformal_fregre_lm` confirmed scalar-response (GAP-0004 false positive — no redraw). scalar-on-function.svg confirmed to show the β̂(t) coefficient inset.
- **R-era:** none remain (grep clean). The conformal-classification.md prose admonition (R `score.type`/CV+) is PROSE-OK.
