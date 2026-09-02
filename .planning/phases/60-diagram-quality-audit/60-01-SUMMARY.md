---
phase: 60-diagram-quality-audit
plan: "01"
subsystem: docs-audit
tags: [svg, audit, accessibility, design-geometry, style-spec]
status: complete

dependency_graph:
  requires: []
  provides:
    - .planning/phases/60-diagram-quality-audit/60-AUDIT.md (90-diagram 4-axis scored inventory)
  affects:
    - .planning/phases/60-diagram-quality-audit/ (60-02 consumes this as input)
    - Phases 61/62/63 correction worklists (driven by 60-AUDIT.md)

tech_stack:
  added: []
  patterns:
    - rsvg-convert PNG render for visual inspection of SVG design/geometry
    - OK/Minor/Major/Critical 4-axis scoring (design/geometry, STYLE_SPEC, accessibility, sync)
    - Section-to-bucket partition for phase-gated correction workflow

key_files:
  created:
    - .planning/phases/60-diagram-quality-audit/60-AUDIT.md
  modified: []

decisions:
  - "STYLE_SPEC baseline: all 90 concept diagrams now fully conform (viewBox 720px width, five CSS classes, role/aria present) — the 4 formerly non-conforming diagrams were migrated in Phases 43–45; no diagram has a STYLE_SPEC-axis defect in v10.0 audit"
  - "Accessibility: universal Minor on A11Y-01 (aria-label text is a paraphrase of the title, not an exact match) and A11Y-02 (no long-form title/desc/aria-labelledby on any diagram — universal gap to close in Phases 61–63)"
  - "5 Major design/geometry defects identified: elastic-clustering.svg (non-standard visual style), concurrent-regression.svg (inter-panel label overflow), ex-canadian-precipitation.svg, ex-canadian-depth-centrality.svg, ex-canadian-seasonal.svg (text clipped at viewBox edge)"
  - "sklearn-pipeline-dataflow.svg assigned to Phase 62 bucket (closest surface-family fit; predates CONTEXT bucket list authored before v9.0 sklearn section)"
  - "Partition: 24 + 26 + 40 = 90 — all diagrams in exactly one bucket"

metrics:
  duration: "~3 hours"
  completed: "2026-09-02"
  tasks_completed: 3
  commits: 1

estimate:
  tokens: 115000

actuals:
  tokens: 96000
  tasks: 3
  commits: 1
---

# Phase 60 Plan 01: Concept Diagram Audit Summary

**One-liner:** 90 concept SVGs scored on 4 axes (design/geometry rsvg-render-backed, STYLE_SPEC grep-verified, accessibility text-matched, sync deferred) — 5 Major geometry defects found, STYLE_SPEC universally clean, A11Y gap universal Minor.

---

## What Was Built

Created `.planning/phases/60-diagram-quality-audit/60-AUDIT.md` — the milestone-gating artifact for v10.0 — containing:

1. **Scoring legend:** OK/Minor/Major/Critical scale with definitions for all four axes and the overall-verdict rule (worst axis wins).

2. **90-row concept scoring table** grouped by docs section (learn, represent, align, analyze, monitoring, advisor, sklearn, regression, inference, examples), with per-row verdicts on:
   - Design/geometry: backed by rsvg-convert PNG render of each SVG — the only reliable detection method for mismatched lines, misaligned endpoints, text overflow, label/element overlap.
   - STYLE_SPEC conformance: grep-verified markers (viewBox 720×{300|480|520}, five CSS classes, system-ui, role/aria).
   - Accessibility: aria-label vs title text comparison + long-form desc/title/aria-labelledby presence check.
   - Sync: deferred to Plan 60-02 (thumb/card comparison).

3. **Authoritative section-to-concept map:** all 90 diagrams listed by name under their owning docs section with correct tallies (learn 6, represent 10, align 8, analyze 12, monitoring 3, advisor 10, sklearn 1, regression 15, inference 4, examples 21 = 90).

4. **Correction-phase bucket assignment:** Phase 61 = learn+represent+align (24), Phase 62 = analyze+monitoring+advisor+sklearn (26, sklearn edge case explicitly resolved), Phase 63 = regression+inference+examples (40). Partition arithmetic: 24 + 26 + 40 = 90.

5. **Placeholder sections** for Plan 60-02: ranked per-phase fix worklists, COVER-01 coverage-gap list, SYNC-01/SYNC-02 drift list.

---

## Key Findings

### Design/Geometry (Primary Audit Axis)

**5 Major defects** (structural fixes required):

| Diagram | Defect | Phase |
|---------|--------|-------|
| `elastic-clustering.svg` | Non-standard visual style: all-caps section headers, bare white boxes, no CSS-class rendering — inconsistent with all 89 peer diagrams; sparse content (only 4 flow boxes on 720×300 canvas with large empty margins) | 62 |
| `concurrent-regression.svg` | "concurrent / regression" label centered at x=360 overflows ±60px into both adjacent panels (left panel right edge x=338, right panel left edge x=382) | 63 |
| `ex-canadian-precipitation.svg` | Rightmost "Geographic drivers" panel text clipped at viewBox right edge (x=720) | 63 |
| `ex-canadian-depth-centrality.svg` | Rightmost "Ranked centrality" panel text clipped at viewBox right edge | 63 |
| `ex-canadian-seasonal.svg` | Bottom-right result badge "summer peak day constant; level rise" truncated at right edge | 63 |

**10+ Minor defects** (low-effort fixes):
- `shift-registration.svg`: "elastic warp" label in a purely rigid-shift diagram — method-accuracy FLAG (Phase 61)
- `advisor-mcp.svg`: "handle + scalars" label straddles the dashed stdio boundary line (Phase 62)
- `advisor-comparative-selection.svg`: "fdars-authoritative" text clips at box right edge (Phase 62)
- `sklearn-pipeline-dataflow.svg`: "FPCLDAClassifier" overflows Predictor box right edge (Phase 62)
- `functional-glm.svg`: "binomial"/"logit" text near-collision at y=147 (Phase 63)
- `itp-interval-inference.svg`: right-panel legend text crowded with bar chart (Phase 63)
- `banded-alignment.svg`: cost-matrix edge labels slightly cramped (Phase 61)
- `ex-explainability-regions.svg`: low-contrast text in dark consensus banner (Phase 63)
- `ex-tecator-regression.svg`: bottom caption overflows viewBox right edge (Phase 63)
- `pace-fpca.svg`: subtitle length near clipping threshold (Phase 61)

### STYLE_SPEC Conformance

**All 90 diagrams: OK.** The 4 formerly non-conforming diagrams (`elastic-clustering.svg`, `outlier-detection.svg`, `covariance-functions.svg`, `ex-sonar-tsrvf.svg`) were migrated in Phases 43–45. STYLE_SPEC axis has zero defects in v10.0.

### Accessibility

**Universal Minor** on two sub-axes:
- **A11Y-01:** Every `aria-label` is a paraphrase of the title text, not a verbatim match. Phase 61/62/63 must align `aria-label` to the exact `.ttl` content.
- **A11Y-02:** Zero diagrams have `<title>`, `<desc>`, or `aria-labelledby`. Complex/multi-panel diagrams especially need long-form descriptions. Gap is universal and systematic.

---

## Deviations from Plan

**None** — plan executed exactly as written. All 90 diagrams rendered, inspected, and scored; section map and bucket partition recorded; 60-AUDIT.md satisfies AUDIT-01 and AUDIT-02 criteria.

Note: The plan's context stated 4 known non-720 diagrams would need STYLE_SPEC flagging. Those diagrams were migrated in prior phases; the audit confirmed all 90 are now conforming. This finding is documented in 60-AUDIT.md as a STYLE_SPEC baseline note.

---

## Self-Check

Automated verifications passed:

- `test -f .planning/phases/60-diagram-quality-audit/60-AUDIT.md` — EXISTS
- All 90 concept SVG filenames present in 60-AUDIT.md — scored-rows=90, missing=0
- `grep -qE 'Critical|Major|Minor' ...` — severity verdicts present
- `git diff --quiet -- docs/assets/` — no committed SVG or STYLE_SPEC.md modified
- `git log ... | grep '\.png'` — no PNG committed
- sklearn edge case present; "24 + 26 + 40 = 90" partition arithmetic present; Phase 61/62/63 labels present

## Self-Check: PASSED
