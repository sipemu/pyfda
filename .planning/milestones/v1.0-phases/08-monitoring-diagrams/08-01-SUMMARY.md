---
phase: 08-monitoring-diagrams
plan: 01
status: complete
completed: 2026-08-08
requirements: [DIA-06]
---

# 08-01 SUMMARY — monitoring/ diagrams sweep (lean)

Executed lean per user request.

## GAP-0003 — spm.svg full redraw

The old spm.svg was not an SPM diagram at all: it was a generic "The fdars Toolkit" overview ("Functional Data Analysis in R, powered by Rust", "Rust Backend (extendr)", `autoplot()`, "zero-copy R ↔ Rust", R function names like `fclassif`/`fregre_pls`) — wrong method + heavy R-era content on the Statistical Process Monitoring page.

Replaced with a new STYLE_SPEC-conforming (720×300) three-panel SPM concept diagram, method-verified against the `fdars.spm` API and spm.md:
- Panel 1 — Phase I baseline: `spm_phase1()`, in-control reference curves + mean, "μ̂(t) + K PCs".
- Panel 2 — Two statistics: Hotelling T² (`Σ ξ²ₖ/λₖ`, shift inside FPC subspace) and SPE/Q (`∫ x̃(t)² dt`, residual outside model), control limits at rate α.
- Panel 3 — Phase II monitor: `spm_monitor()` control chart with dashed UCL, green in-control points, and a red out-of-control alarm crossing the limit.

Render-verified. Commit `<spm commit>`.

## Verification (all 3 monitoring/ diagrams)

- SVGO idempotence gate: all 3 OK (SC#1).
- STYLE_SPEC markers: all 3 conform.
- R-era grep: clean (SC#2).
- SC#3: spm.svg shows Phase I (in-control estimation) and Phase II (online monitoring with UCL) as distinct panels.

## Files

- Modified: `docs/assets/diagrams/spm.svg`
- Created: COVERAGE.md
