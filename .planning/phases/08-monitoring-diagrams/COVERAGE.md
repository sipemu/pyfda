# Phase 08 — API Coverage Declaration

No external API integration: phase edits hand-authored static SVG diagrams and runs local SVGO/mkdocs tooling only.

## Scope verified

- **Redrawn (1):** `spm.svg` — full method-accurate redraw (GAP-0003). The old file was the wrong diagram (a generic R-era "fdars Toolkit" overview) on the SPM page; replaced with a STYLE_SPEC-conforming three-panel SPM concept: Phase I in-control FPCA model (`spm_phase1`), the T² + SPE statistics with formulas and control limits at α, and a Phase II control chart (`spm_monitor`) with UCL + out-of-control alarm.
- **Verified-only (2):** `advanced-spm.svg`, `profile-partial-monitoring.svg` — already conforming; re-proven against the live gate.
- **R-era:** none remain in any monitoring/ diagram (grep clean).
