---
phase: 46-diagram-coverage-examples
verified: 2026-08-22T20:42:10Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps_resolved: "2026-08-22 — Part A passed at verification. Part B's 12 DEFECT-level layout issues fixed via gap-closure commit 5637232 (overflowing subtitles/captions shortened or wrapped to fit the 720 canvas; canadian-weather box overlap removed; andrews-wine/functional-outlier text-overflow fixed; tolerance-vs-conformal dark-on-dark invisible text recolored to white). All 12 re-rendered clean + SVGO-idempotent; orchestrator spot-checked the 3 worst (canadian-weather, tolerance-vs-conformal, andrews-wine) = clean. The 3 MINOR-CLIP + 6 CLEAN diagrams unchanged. Full diagram method-accuracy is the remit of the Phase 49 blocking human review."
gaps:
  - truth: "Each of the 20 gap pages carries a method-accurate, STYLE_SPEC-conformant SVG embedded via .fdars-diagram"
    status: partial
    reason: "All 20 SVGs exist and are embedded correctly; all pass STYLE_SPEC and SVGO gates. However, 14 of the 20 new diagrams have layout defects (box overlap, text overflowing container, text clipping beyond viewBox edge) that occlude or truncate content — see Part B catalog below. The diagrams are present and technically well-formed but visually defective in specific areas."
    artifacts:
      - path: "docs/assets/diagrams/ex-canadian-weather.svg"
        issue: "DEFECT: 'Pairwise fanova' box (x=338,w=172) overlaps 'fclassif' box (x=442,w=254) by 68 px; result-row mono texts clip left and right edges; 161-char bottom caption clips both edges"
      - path: "docs/assets/diagrams/ex-canadian-depth-centrality.svg"
        issue: "DEFECT: 141-char bottom caption (line 73) clips both left and right edges at x=360 centered on 720-wide viewBox"
      - path: "docs/assets/diagrams/ex-canadian-precipitation.svg"
        issue: "MINOR-CLIP: 'Geographic drivers' result box (x=574,w=122) text sits within box geometrically but is very tight; some text items approach box right edge"
      - path: "docs/assets/diagrams/ex-canadian-seasonal.svg"
        issue: "MINOR-CLIP: rightmost result box ('StableSeasonal · timing fixed') mono sub-text 'level rise' clips at right edge"
      - path: "docs/assets/diagrams/ex-andrews-wine.svg"
        issue: "DEFECT: 'Consensus' panel (x=204,w=492) — .lab text at line 83 is ~83 chars at 13px bold, far wider than the 492px panel; .sm detail texts (lines 84-87) similarly overflow; text rendered outside panel bounds and truncated at viewBox right edge"
      - path: "docs/assets/diagrams/ex-andrews-wine-clustering.svg"
        issue: "DEFECT: row-1 box label 'silhouette_score_data + calinski_harabasz_data' clips right viewBox edge; bottom orange result box 'accuracy ≈ 0.95 (near-diagonal cross-ta...' clips right edge"
      - path: "docs/assets/diagrams/ex-tecator-regression.svg"
        issue: "MINOR-CLIP: 2-line bottom caption clips at left edge (caption 2 starts mid-sentence at 'smoother on L² distances')"
      - path: "docs/assets/diagrams/ex-tecator-monitoring.svg"
        issue: "DEFECT: subtitle (132 chars at x=360 centered) clips both left and right edges; bottom caption (2nd line ~128 chars) clips both edges"
      - path: "docs/assets/diagrams/ex-cross-validation.svg"
        issue: "DEFECT: 'optimal_k · OOF predictions' box — row-1 sm text 'in-sample R² keeps rising · OOF R² peaks then falls' extends ~14px beyond 720 viewBox; bottom caption line 2 (132 chars) clips both edges"
      - path: "docs/assets/diagrams/ex-explainability-regions.svg"
        issue: "DEFECT: subtitle (131 chars) clips both edges; 'functional_saliency' mono text bleeds into 'domain_selection' box gap; 'beta_decomposition' box text 'sum = β(λ); variance_proportion' clips right; convergence box sub-text clips both edges"
      - path: "docs/assets/diagrams/ex-functional-outlier-workflow.svg"
        issue: "DEFECT: MS-plot mono text 'shape outliers: tangled with normal cloud → MISSED' (centered x=187, ~360px wide mono) extends beyond box right edge (x=350) into 20px gap, collides with outliergram 'flagged:' text; 147-char bottom caption clips both edges"
      - path: "docs/assets/diagrams/ex-growth-alignment.svg"
        issue: "DEFECT: subtitle (138 chars) clips both edges; two-line bottom caption each >140 chars clip both edges with significant content loss"
      - path: "docs/assets/diagrams/ex-phoneme-shape.svg"
        issue: "DEFECT: subtitle (136 chars) clips both edges; row-1 'alignment_quality per class' text bleeds into 'shape_mean per class' box territory; two-line bottom caption clips both edges"
      - path: "docs/assets/diagrams/ex-inline-monitoring.svg"
        issue: "DEFECT: two-line bottom caption clips both left and right edges with content loss"
      - path: "docs/assets/diagrams/ex-tolerance-vs-conformal.svg"
        issue: "DEFECT: subtitle (156 chars) clips both edges; FPCA result box .sm texts at y=214,228 rendered in dark #495057 on dark blue background (invisible/unreadable); 166-char bottom caption clips both edges"
    missing:
      - "Shorten or wrap all subtitles longer than ~100 chars (14 diagrams affected) — use two .sub lines or abbreviate"
      - "Fix ex-canadian-weather.svg: reduce 'Pairwise fanova' box width or shift 'fclassif' box right to eliminate 68px overlap"
      - "Fix ex-canadian-weather.svg: shorten result-row mono texts or widen result boxes"
      - "Fix ex-andrews-wine.svg: shorten 'Consensus' panel .lab and .sm texts to fit within 492px; break long .sm lines"
      - "Fix ex-andrews-wine-clustering.svg: shorten row-1 box label; shorten bottom result box mono text"
      - "Fix ex-functional-outlier-workflow.svg: reduce mono text in MS-plot bottom line; increase gap between the two panels (currently 20px)"
      - "Fix ex-tolerance-vs-conformal.svg: add fill='white' to .sm texts inside dark result boxes (lines 47-48)"
      - "All 14 DEFECT diagrams: shorten bottom captions to < ~120 chars per line, or split into two lines within the viewBox height"
---

# Phase 46: Diagram Coverage — Examples Verification Report

**Phase Goal (DIACOV-01):** Each of the 20 `docs/examples/*.md` gap pages carries a method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG (workflow genre) named `docs/assets/diagrams/ex-<slug>.svg`, embedded via `![...](...){ .fdars-diagram }`. `examples/index.md` and `sonar-tsrvf.md` excluded. No whole-site build. No existing method-page diagram or other page changed beyond the embed lines.

**Verified:** 2026-08-22T20:42:10Z
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Part A — Code-Verifiable Goal Checks

### A1. Coverage: All 20 Gap Pages

**SVG files on disk:** 21 ex-*.svg files exist at `docs/assets/diagrams/`:
- 20 new Phase 46 diagrams (both waves)
- 1 pre-existing: `ex-sonar-tsrvf.svg`

Count confirmed: `ls docs/assets/diagrams/ex-*.svg | wc -l` = 21. PASSED.

**Embed lines in all 20 gap pages:**

| Page | SVG on disk | .fdars-diagram embed | Embed matches SVG |
|------|-------------|---------------------|-------------------|
| `andrews-wine.md` | ex-andrews-wine.svg | 1 match | VERIFIED |
| `andrews-wine-intro.md` | ex-andrews-wine-intro.svg | 1 match | VERIFIED |
| `andrews-wine-clustering.md` | ex-andrews-wine-clustering.svg | 1 match | VERIFIED |
| `andrews-wine-qc.md` | ex-andrews-wine-qc.svg | 1 match | VERIFIED |
| `biopharma-monitoring.md` | ex-biopharma-monitoring.svg | 1 match | VERIFIED |
| `canadian-depth-centrality.md` | ex-canadian-depth-centrality.svg | 1 match | VERIFIED |
| `canadian-function-on-scalar.md` | ex-canadian-function-on-scalar.svg | 1 match | VERIFIED |
| `canadian-precipitation.md` | ex-canadian-precipitation.svg | 1 match | VERIFIED |
| `canadian-seasonal.md` | ex-canadian-seasonal.svg | 1 match | VERIFIED |
| `canadian-weather.md` | ex-canadian-weather.svg | 1 match | VERIFIED |
| `cross-validation.md` | ex-cross-validation.svg | 1 match | VERIFIED |
| `explainability-regions.md` | ex-explainability-regions.svg | 1 match | VERIFIED |
| `functional-outlier-workflow.md` | ex-functional-outlier-workflow.svg | 1 match | VERIFIED |
| `growth-alignment.md` | ex-growth-alignment.svg | 1 match | VERIFIED |
| `inline-monitoring.md` | ex-inline-monitoring.svg | 1 match | VERIFIED |
| `phoneme-shape.md` | ex-phoneme-shape.svg | 1 match | VERIFIED |
| `tecator-conformal-coverage.md` | ex-tecator-conformal-coverage.svg | 1 match | VERIFIED |
| `tecator-monitoring.md` | ex-tecator-monitoring.svg | 1 match | VERIFIED |
| `tecator-regression.md` | ex-tecator-regression.svg | 1 match | VERIFIED |
| `tolerance-vs-conformal.md` | ex-tolerance-vs-conformal.svg | 1 match | VERIFIED |

**Exclusions confirmed:**
- `examples/index.md`: zero `.fdars-diagram` embeds — VERIFIED
- `examples/sonar-tsrvf.md`: pre-existing `ex-sonar-tsrvf.svg` embed unchanged — VERIFIED (last git commit on that file: Phase 43 migration, no Phase 46 touches)

**Coverage: PASSED — 20/20 gap pages covered.**

### A2. STYLE_SPEC Conformance for All 20 New SVGs

Checked: `viewBox="0 0 720 {300|480}"`, `role="img"`, `aria-label`, canonical 5 CSS classes (`.ttl .sub .lab .sm .mono`).

| SVG | viewBox | role="img" | aria-label | 5 classes | Result |
|-----|---------|-----------|------------|-----------|--------|
| ex-andrews-wine-clustering.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-andrews-wine-intro.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-andrews-wine.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-andrews-wine-qc.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-biopharma-monitoring.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-canadian-depth-centrality.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-canadian-function-on-scalar.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-canadian-precipitation.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-canadian-seasonal.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-canadian-weather.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-cross-validation.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-explainability-regions.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-functional-outlier-workflow.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-growth-alignment.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-inline-monitoring.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-phoneme-shape.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-tecator-conformal-coverage.svg | 0 0 720 300 | yes | yes | all 5 | PASS |
| ex-tecator-monitoring.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-tecator-regression.svg | 0 0 720 480 | yes | yes | all 5 | PASS |
| ex-tolerance-vs-conformal.svg | 0 0 720 300 | yes | yes | all 5 | PASS |

**STYLE_SPEC: PASSED — 20/20.**

### A3. SVGO Idempotence

All 20 new SVGs: `npx svgo@3.3.4 --config svgo.config.mjs --quiet --input <f> --output -` twice → byte-identical second pass.

**Result: PASSED — 20/20.**

### A4. No Churn

`git diff --name-only 3d29e2d^..HEAD` outside `.planning/` and `docs/assets/diagrams/ex-*` and `docs/examples/`:
- **Zero files.** No method-page diagrams, no mkdocs.yml, no Rust/Python source touched.

Spot-checks (3 pages): diffs show exactly 1 image line added (`+![...](../assets/diagrams/ex-<slug>.svg){ .fdars-diagram }`) and 1 blank line — no prose rewrites.

**No-churn: PASSED.**

### Observable Truths — Part A

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 20 gap pages have an ex-\<slug\>.svg on disk | VERIFIED | 20 files confirmed |
| 2 | All 20 gap pages carry a `.fdars-diagram` embed | VERIFIED | grep count = 1 for all 20 |
| 3 | STYLE_SPEC: viewBox 720-wide, role="img", aria-label, 5 CSS classes | VERIFIED | checked all 20 |
| 4 | SVGO idempotence on all 20 new SVGs | VERIFIED | all pass |
| 5 | No method-page or other file changed | VERIFIED | git diff = empty outside expected scope |

**Score: 5/5 code-verifiable truths — all PASS.**

---

## Part B — Layout Defect Catalog

Rendered with `rsvg-convert -z 1.4` and inspected via Read tool (PNG image view). All 21 ex-*.svg rendered successfully (non-zero file sizes).

### Defect Classification Key

- **CLEAN** — no layout issue
- **MINOR-CLIP** — a label or caption just kisses the edge; text is still readable / meaning not lost
- **DEFECT** — box overlap, text occluded at boundary, or caption loss so severe that meaning is lost

### Catalog Table

| Diagram | Verdict | Specific Issue |
|---------|---------|----------------|
| ex-sonar-tsrvf.svg | CLEAN | Pre-existing Phase 43 diagram; renders cleanly |
| ex-canadian-weather.svg | DEFECT | (1) "Pairwise fanova" rect (x=338,w=172,end=510) overlaps "fclassif" rect (x=442) by 68 px — text inside both panels mutually occluded. (2) Result-row left box: yellow mono "F(t) peaks Jan–Mar · Sep-Dec" clips left edge; middle box "β_lat(t) most negative in Ja..." clips right edge. (3) Bottom .sm caption (161 chars, x=360 centered) clips both left and right edges. |
| ex-canadian-depth-centrality.svg | DEFECT | Bottom .sm caption line 73 (141 chars, x=360 centered) clips both left and right edges — approximately 40% of text lost at each side. |
| ex-canadian-function-on-scalar.svg | CLEAN | All panels and captions render within viewBox bounds |
| ex-canadian-precipitation.svg | MINOR-CLIP | "Geographic drivers" result box text (x=574,w=122) is very tight; content visible but "predict_fosr:" / "hypothetical / station profiles" lines near box boundary |
| ex-canadian-seasonal.svg | MINOR-CLIP | Rightmost result box ("StableSeasonal · timing fixed"): mono sub-text "level rise" clips a few chars at right edge; main message readable |
| ex-andrews-wine.svg | DEFECT | "Consensus" panel (.lab line 83: ~83 chars at 13px bold font, centered in 492px panel) — text extends far beyond panel width; sm detail lines 84-87 (~80-90 chars each) also overflow; text visible outside box and truncated at viewBox right edge. Content loss is severe. |
| ex-andrews-wine-intro.svg | CLEAN | All panels and captions render cleanly |
| ex-andrews-wine-clustering.svg | DEFECT | (1) Row-1 panel label "silhouette_score_data + calinski_harabasz_data" clips right viewBox edge — last ~4 chars lost. (2) Bottom orange result box: mono text "accuracy ≈ 0.95 (near-diagonal cross-ta..." clips right edge with substantial content loss. |
| ex-andrews-wine-qc.svg | CLEAN | All panels and captions render cleanly |
| ex-tecator-regression.svg | MINOR-CLIP | Bottom 2-line caption: line 2 starts mid-sentence at visible left edge ("smoother on L² distances) is strongest..."); the first portion is clipped left — partial context loss |
| ex-tecator-conformal-coverage.svg | CLEAN | All panels and captions render cleanly |
| ex-tecator-monitoring.svg | DEFECT | (1) Subtitle (132 chars, x=360 centered): clips both left ("hase1 + select_ncomp...") and right ("...dia") — most of the subtitle text lost. (2) Bottom caption line 2 (128 chars): clips both left ("ec baselines...") and right ("...back to s"). |
| ex-biopharma-monitoring.svg | CLEAN | All panels and captions render cleanly |
| ex-inline-monitoring.svg | DEFECT | Bottom two-line caption: line 1 visible as ")  below ~1σ neither chart..." (leading "(" clipped left), line 2 "arl1_t2(eigenvalues, ucl, shift)..." clips left. Both lines clip right. Content from preceding sentence lost. |
| ex-cross-validation.svg | DEFECT | (1) "optimal_k · OOF predictions" box sm text line (51 chars, x=565 centered in 262px box): extends ~14px beyond 720-wide viewBox right edge — "falls" partially clipped. (2) Bottom caption line 2 (132 chars, x=360 centered): clips both edges with ~30% content lost each side. |
| ex-explainability-regions.svg | DEFECT | (1) Subtitle (131 chars, x=360): clips both edges ("egre_lm β(λ)..." and "...beta_decompositio"). (2) "functional_saliency" box bottom mono text "mean\|saliency\| → 930 nm" bleeds into "domain_selection" box gap. (3) "beta_decomposition" box text "sum = β(λ); variance_proportion" clips right. (4) Convergence-box green sub-text clips both edges. |
| ex-functional-outlier-workflow.svg | DEFECT | (1) MS-plot mono text "shape outliers: tangled with normal cloud → MISSED" (x=187, ~360px wide at 12px mono) extends from ~x=7 to ~x=367 — overflows box right edge (x=350); collides with outliergram "flagged:" text across the 20px gap. (2) Bottom .sub caption (147 chars, x=360): clips both edges. |
| ex-growth-alignment.svg | DEFECT | (1) Subtitle (138 chars, x=360): clips both edges. (2) Bottom caption line 1 (150 chars) clips both edges. (3) Bottom caption line 2 (146 chars) clips both edges. Approximately 25% of each caption line lost. |
| ex-phoneme-shape.svg | DEFECT | (1) Subtitle (136 chars, x=360): clips both edges. (2) "alignment_quality per class" box bottom text and "shape_mean per class" box top text overlap/bleed into each other across box boundary. (3) Two-line bottom caption clips both edges. |
| ex-tolerance-vs-conformal.svg | DEFECT | (1) Subtitle (156 chars, x=360): clips both edges. (2) FPCA result box (left, dark blue fill): .sm texts at y=214 and y=228 use CSS .sm class which renders fill:#495057 (dark grey) on dark blue background — effectively invisible/unreadable. (3) Bottom .sub caption (166 chars, x=360): clips both edges. |

### Summary Count

| Verdict | Count | Diagrams |
|---------|-------|---------|
| CLEAN | 6 | ex-sonar-tsrvf, ex-canadian-function-on-scalar, ex-andrews-wine-intro, ex-andrews-wine-qc, ex-tecator-conformal-coverage, ex-biopharma-monitoring |
| MINOR-CLIP | 3 | ex-canadian-precipitation, ex-canadian-seasonal, ex-tecator-regression |
| DEFECT | 12 | ex-canadian-weather, ex-canadian-depth-centrality, ex-andrews-wine, ex-andrews-wine-clustering, ex-tecator-monitoring, ex-inline-monitoring, ex-cross-validation, ex-explainability-regions, ex-functional-outlier-workflow, ex-growth-alignment, ex-phoneme-shape, ex-tolerance-vs-conformal |

---

## Root Cause Analysis

Two recurring root causes account for nearly all defects:

**Root Cause 1 — Overlong centered captions (11 diagrams):**
Subtitle and bottom-note `.sub`/`.sm` texts are centered at x=360 and exceed ~100 chars. At 11-12px system-ui, 100 chars ≈ ~680px. Centering at x=360 means any text wider than 720px clips both edges. Texts of 130-156 chars lose 20-30% at each edge. Fix: shorten captions, wrap to two lines with y-offsets, or increase viewBox height to accommodate text below the main diagram area.

**Root Cause 2 — Panel content overflowing box geometry (4 diagrams):**
- `ex-canadian-weather`: "Pairwise fanova" and "fclassif" boxes placed with overlapping x-ranges.
- `ex-andrews-wine`: "Consensus" panel text far wider than the containing rect.
- `ex-functional-outlier-workflow`: MS-plot mono text extends beyond box edge into the 20px inter-panel gap.
- `ex-tolerance-vs-conformal`: `.sm` texts inside dark-fill result boxes lack explicit `fill="white"`, rendering invisible against dark background.

---

## Diagrams Needing a Layout Fix Pass

The following 12 diagrams have DEFECT-level issues requiring targeted fixes:

1. **ex-canadian-weather.svg** — Fix Pairwise fanova / fclassif overlap + shorten result-row texts + shorten bottom caption
2. **ex-canadian-depth-centrality.svg** — Shorten 141-char bottom caption (split into 2 lines)
3. **ex-andrews-wine.svg** — Shorten "Consensus" panel .lab and .sm texts to fit within 492px panel
4. **ex-andrews-wine-clustering.svg** — Shorten row-1 label; shorten bottom result box text
5. **ex-tecator-monitoring.svg** — Shorten 132-char subtitle; shorten bottom captions
6. **ex-inline-monitoring.svg** — Shorten or wrap two-line bottom caption
7. **ex-cross-validation.svg** — Shorten row-1 "optimal_k" box sm text; shorten bottom caption line 2
8. **ex-explainability-regions.svg** — Shorten 131-char subtitle; reduce "functional_saliency" mono text; shorten convergence-box sub-text
9. **ex-functional-outlier-workflow.svg** — Shorten MS-plot mono text or reduce font size; increase panel gap; shorten bottom caption
10. **ex-growth-alignment.svg** — Shorten 138-char subtitle; shorten both bottom caption lines
11. **ex-phoneme-shape.svg** — Shorten 136-char subtitle; fix row-1 box text bleed; shorten bottom captions
12. **ex-tolerance-vs-conformal.svg** — Shorten 156-char subtitle; add `fill="white"` to .sm texts in dark result boxes; shorten bottom caption

---

## Gaps Summary

**Part A (code-verifiable checks): PASSED.** All 20 SVG files exist, all 20 embed lines are correct, all 20 pass STYLE_SPEC and SVGO idempotence, zero file churn outside scope.

**Part B (layout visual inspection): FAILED — 12 DEFECT-level diagrams.** The root causes are consistent: (1) subtitle and bottom-note texts are too long for a 720-wide viewBox when centered at x=360, and (2) four diagrams have specific box-geometry or text-fill issues. The method-accuracy content is all present and the diagrams communicate their analytical arcs, but the layout defects mean readers lose subtitle context and bottom-note details on more than half the new diagrams.

**Overall status: gaps_found.** The phase goal requires STYLE_SPEC-conformant SVGs, and STYLE_SPEC §viewBox says "Fixed width: always 720" — content that overflows the 720-wide canvas violates this constraint in practice even if the viewBox attribute is set correctly.

---

_Verified: 2026-08-22T20:42:10Z_
_Verifier: Claude (gsd-verifier)_
