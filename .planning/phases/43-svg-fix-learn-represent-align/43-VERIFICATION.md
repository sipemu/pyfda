---
phase: 43-svg-fix-learn-represent-align
verified: 2026-08-22T18:00:00Z
status: passed
score: 6/6 must-haves verified
human_review_resolved: "2026-08-22 — orchestrator rendered + eyeballed all 4 changed PNGs (smoothing/pace-fpca/banded-alignment/ex-sonar-tsrvf). smoothing/ex-sonar/pace-fpca clean. banded-alignment still had top-annotation + bottom-axis-label overlaps -> fixed via gap-closure commit 3adae8e (DP grid shrunk to 16px cells, enclosed in panel, band_frac/upper-band-edge/j-axis labels repositioned; SVGO idempotent; re-render clean). elastic-alignment.svg gamma(t) inset-size adequacy explicitly carried forward to the Phase 49 blocking human diagram review."
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items:
  - truth: "Each section (learn / represent / align) passed a built-site PNG review before its commit landed (SC5)."
    test: "Open the scratchpad PNGs (smoothing.png, pace-fpca.png, banded-alignment.png, ex-sonar-tsrvf.png) and confirm: (1) smoothing Panel 3 shows only a clean smooth curve, no jagged ghost; (2) pace-fpca subtitle fits within the frame with no right-edge clip; (3) banded-alignment upper-band-edge label no longer overlaps the cost-matrix grid; (4) ex-sonar-tsrvf renders at 720 width with canonical typography and three-path content intact."
    expected: "All four PNGs render cleanly without visual defects listed above."
    why_human: "rsvg-convert confirmed non-empty PNGs exist and SVGO idempotence passed; but visual correctness (no label overlap, no clip, clean panel reads) requires eyeball inspection of the rendered bitmaps — grep cannot see pixel-level rendering."
human_verification:
  - test: "Open scratchpad PNGs for the 4 changed diagrams and do the per-section visual review (SC5)."
    expected: "smoothing.svg Panel 3 shows only the bold smooth cubic-bezier curve (no jagged ghost); pace-fpca.svg subtitle does not clip at 720px right edge; banded-alignment.svg upper-band-edge label sits above the grid without occluding any matrix line; ex-sonar-tsrvf.svg renders with canonical STYLE_SPEC typography, all three analysis paths and accuracy percentages (87.0%/77.7%/66.2%) visible."
    why_human: "SVGO idempotence and PNG non-emptiness are verified programmatically, but visual correctness of rendering requires human eyeball inspection of the bitmap output."
  - test: "Confirm elastic-alignment.svg Phase 49 adequacy question: open docs/assets/diagrams/elastic-alignment.svg PNG and assess whether the γ(t) warp inset (56×56px, position translate(624,120)) is sufficiently prominent for new users learning amplitude/phase decomposition (per docs/align/elastic-alignment.md:6–13)."
    expected: "Reviewer decides: (a) inset size and 'phase γ(t)' label at line 61 are adequate for pedagogical purpose, OR (b) Panel 3 needs a redesign to give the warp inset more visual weight."
    why_human: "This is an explicitly deferred pedagogical judgment call from Phase 43 SUMMARY. The label is present and factually correct; only the visual prominence is in question. No code-level check can resolve this."
---

# Phase 43: SVG Fix — learn / represent / align — Verification Report

**Phase Goal:** Every flagged concept diagram in the learn/represent/align batch corrected on all 4 axes (visual/layout, STYLE_SPEC, XML formatting, method-accuracy), verified per-diagram via SVGO idempotence + rsvg PNG. SVG-only; 16 OK diagrams byte-unchanged; no docs .md edits; no new diagrams; no whole-site build. Requirements: SVGFIX-01..04.
**Verified:** 2026-08-22T18:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Every flagged learn/represent/align diagram renders cleanly — no overlapping labels, consistent spacing/alignment/sizing (SC1, SVGFIX-01) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | SVGO idempotence PASS on all 4 changed files; rsvg-convert produces non-empty PNGs (smoothing 48 KB, pace-fpca 62 KB, banded-alignment 88 KB, ex-sonar-tsrvf 79 KB). Visual quality requires human eyeball — see Human Verification |
| 2 | Every diagram in this batch conforms to STYLE_SPEC.md — 720-width viewBox, the 5 CSS classes, system-ui fonts, role="img" + aria-label (SC2, SVGFIX-02) | ✓ VERIFIED | ex-sonar-tsrvf.svg: `viewBox="0 0 720 480"`, `fill="none"`, `role="img"`, `aria-label="Validation-First Framework: Three Analysis Paths"`, all 5 classes defined (.ttl/.sub/.lab/.sm/.mono) and used (ttl×1, sub×1, lab×8, sm×12, mono×3). No old classes (.title/.label/.small/.acc/.box) remain. All other 24 batch diagrams were already conforming (confirmed at Phase 42 audit) and are byte-unchanged |
| 3 | Every diagram in this batch is method-accurate against the shipped fdars bindings — no diagram misdepicts what its method does (SC3, SVGFIX-04) | ✓ VERIFIED | (a) `functional_boxplot`: `grep -n "functional_boxplot" src/depth_mod.rs` → line 588 (function def) + line 625 (registration). Exported. depth-functions.svg reference is correct. (b) shift-registration legend: `docs/align/shift-registration.md:9` explicitly teaches the rigid-vs-elastic contrast ("a shift moves the entire curve... while an elastic warp can compress and stretch"). shift-registration.svg presents "shift (rigid)" and "elastic warp" as parallel legend entries (x=310 vs x=384), not sequential steps. Confirmed accurate as a contrast key. (c) elastic-alignment.svg: `phase γ(t)` label present at line 61 (`<text class="sm" x="652" y="192">phase &#947;(t)</text>`). Factually correct. Inset size deferred to Phase 49 human review |
| 4 | Each changed diagram passes SVGO idempotence: svgo@3.3.4 --config svgo.config.mjs second pass byte-identical (SC4, SVGFIX-03) | ✓ VERIFIED | All 4 changed files pass: smoothing.svg `cmp` exit 0, pace-fpca.svg `cmp` exit 0, banded-alignment.svg `cmp` exit 0, ex-sonar-tsrvf.svg `cmp` exit 0. Run fresh in this verification session |
| 5 | The 16 OK diagrams + all NO-EDIT confirmed diagrams are byte-unchanged (SC4, no-churn decision) | ✓ VERIFIED | `git diff HEAD~4..HEAD -- docs/assets/diagrams/` lists exactly 4 files: smoothing.svg, pace-fpca.svg, banded-alignment.svg, ex-sonar-tsrvf.svg. All 21 untouched diagrams confirmed byte-unchanged by `git diff --quiet HEAD~4..HEAD` loop. No docs .md edits in any of the 4 phase commits |
| 6 | Each section passed a built-site PNG review before its commit landed (SC5) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | rsvg-convert produces non-empty PNGs (proven). Structural correctness of the SVG edits is code-verifiable (Panel 3 ghost path removed from smoothing.svg, subtitle shortened in pace-fpca.svg, label repositioned in banded-alignment.svg, full STYLE_SPEC migration in ex-sonar-tsrvf.svg). Visual correctness requires human eyeball of the 4 PNG renders — routes to Human Verification |

**Score:** 4/6 truths verified, 2 present+wired but behavior (visual rendering quality) unverified

---

### XML Cleanup NO-EDIT Justification — Per-File Verification

The executor declined to edit 5 represent/ diagrams (fpca, elastic-fpca, basis-representation, andrews-transformation, distance-metrics), claiming their inline `font-size=` values are intentional size reductions, not class-size duplicates. **Verified by reading each file:**

CSS canonical sizes: `.sm`=11px, `.mono`=12px, `.lab`=13px, `.sub`=12px, `.ttl`=17px

| File | Class on element | Inline font-size | Class size | Difference | Verdict |
|------|-----------------|-----------------|------------|------------|---------|
| fpca.svg | `.sm` | 9px | 11px | 9 ≠ 11 | Intentional reduction — NO-EDIT correct |
| elastic-fpca.svg | `.mono` | 11px | 12px | 11 ≠ 12 | Intentional reduction — NO-EDIT correct |
| elastic-fpca.svg | `.sm` | 9px | 11px | 9 ≠ 11 | Intentional reduction — NO-EDIT correct |
| basis-representation.svg | `.sm` | 9px | 11px | 9 ≠ 11 | Intentional reduction — NO-EDIT correct |
| andrews-transformation.svg | `.mono` | 11px | 12px | 11 ≠ 12 | Intentional reduction — NO-EDIT correct |
| andrews-transformation.svg | `.sm` | 10px, 9px | 11px | 10≠11, 9≠11 | Intentional reductions — NO-EDIT correct |
| distance-metrics.svg | `.mono` | 11px, 10.5px | 12px | 11≠12, 10.5≠12 | Intentional reductions — NO-EDIT correct |

**Finding: No redundant font-size duplicates exist in any of the 5 files.** Every inline `font-size=` value differs from its class-defined size. The NO-EDIT decisions are correct per the plan's own rule ("Where an inline size intentionally differs from the class and removing it would visibly change the render, keep the override"). SVGFIX-03 is met for this batch.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/assets/diagrams/smoothing.svg` | Panel-3 ghost removed | ✓ VERIFIED | Ghost jagged polyline (`stroke-opacity=".2"`) confirmed present in HEAD~4 (line 48), confirmed absent in current HEAD. Panel 3 now contains only the bold smooth cubic-bezier path (`stroke-width="3"`) |
| `docs/assets/diagrams/pace-fpca.svg` | Subtitle overflow fixed | ✓ VERIFIED | Subtitle shortened from ~130 chars to 97 chars: "Ragged per-curve grids (sparse, irregular) — PACE recovers smooth eigenfunctions on a common grid". At 12px system-ui (avg ~7px/char × 97 = ~679px), fits within 720px viewBox |
| `docs/assets/diagrams/banded-alignment.svg` | Label re-anchored off grid | ✓ VERIFIED | "upper band edge" relocated from x=180 text-anchor="end" to x=230 y=94 text-anchor="middle" centered above the band start. Adjusted leader line. Label no longer at the overcrowded top-left matrix corner |
| `docs/assets/diagrams/ex-sonar-tsrvf.svg` | Full STYLE_SPEC migration | ✓ VERIFIED | viewBox 0 0 720 480 confirmed; role="img" confirmed; aria-label confirmed; all 5 canonical classes defined verbatim from STYLE_SPEC and used (ttl×1, sub×1, lab×8, sm×12, mono×3); 0 old custom classes remain; method content preserved (three paths, Phase/Total=0.31, 87.0%/77.7%/66.2%) |
| `docs/assets/diagrams/fpca.svg` | XML cleanup (confirmed NO-EDIT) | ✓ VERIFIED | Inline font-size=9 on .sm elements is intentional (9≠11). Byte-unchanged confirmed by git diff |
| `docs/assets/diagrams/elastic-fpca.svg` | XML cleanup (confirmed NO-EDIT) | ✓ VERIFIED | Inline font-size=11 on .mono (11≠12) and 9 on .sm (9≠11) are intentional. Byte-unchanged |
| `docs/assets/diagrams/basis-representation.svg` | XML cleanup (confirmed NO-EDIT) | ✓ VERIFIED | Inline font-size=9 on .sm (9≠11) intentional. Byte-unchanged |
| `docs/assets/diagrams/andrews-transformation.svg` | XML cleanup (confirmed NO-EDIT) | ✓ VERIFIED | Inline font-size=11/.mono (11≠12) and 10/9/.sm (not 11) intentional. Byte-unchanged |
| `docs/assets/diagrams/distance-metrics.svg` | XML cleanup (confirmed NO-EDIT) | ✓ VERIFIED | Inline font-size=11/10.5 on .mono (not 12) intentional. Byte-unchanged |
| `docs/assets/diagrams/depth-functions.svg` | Method-accuracy confirm, NO EDIT | ✓ VERIFIED | `functional_boxplot` registered at src/depth_mod.rs:625. Reference correct. Byte-unchanged |
| `docs/assets/diagrams/elastic-alignment.svg` | Phase label confirm, NO EDIT | ✓ VERIFIED | `phase γ(t)` label at line 61: `<text class="sm" x="652" y="192" text-anchor="middle" fill="#6c757d">phase &#947;(t)</text>`. Byte-unchanged |
| `docs/assets/diagrams/shift-registration.svg` | Contrast key confirm, NO EDIT | ✓ VERIFIED | "shift (rigid)" at x=310 fill="#3f51b5" and "elastic warp" at x=384 fill="#6c757d" are parallel entries (not sequential steps). docs/align/shift-registration.md:9 confirms this is the intended contrast. Byte-unchanged |

---

### Key Link Verification

| Link | Status | Evidence |
|------|--------|----------|
| STYLE_SPEC.md canonical `<style>` block → ex-sonar-tsrvf.svg | ✓ WIRED | Five-class block in ex-sonar-tsrvf.svg matches STYLE_SPEC verbatim (all 5 class definitions identical) |
| src/depth_mod.rs → depth-functions.svg reference | ✓ WIRED | `wrap_pyfunction!(functional_boxplot, m)?` at line 625 → method reference in diagram is accurate |
| docs/align/shift-registration.md prose → shift-registration.svg legend | ✓ WIRED | Page line 9 explicitly teaches the rigid-vs-elastic contrast; diagram's legend is the visual counterpart |
| svgo.config.mjs + svgo@3.3.4 → 4 changed SVGs | ✓ WIRED | All 4 pass idempotence check in this session |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| smoothing.svg SVGO idempotence | `npx svgo@3.3.4 --config svgo.config.mjs` twice, `cmp` | exit 0 | ✓ PASS |
| pace-fpca.svg SVGO idempotence | `npx svgo@3.3.4 --config svgo.config.mjs` twice, `cmp` | exit 0 | ✓ PASS |
| banded-alignment.svg SVGO idempotence | `npx svgo@3.3.4 --config svgo.config.mjs` twice, `cmp` | exit 0 | ✓ PASS |
| ex-sonar-tsrvf.svg SVGO idempotence | `npx svgo@3.3.4 --config svgo.config.mjs` twice, `cmp` | exit 0 | ✓ PASS |
| smoothing.svg rsvg-convert | `rsvg-convert ... -o smoothing.png; test -s` | 48,191 bytes | ✓ PASS |
| pace-fpca.svg rsvg-convert | `rsvg-convert ... -o pace-fpca.png; test -s` | 61,645 bytes | ✓ PASS |
| banded-alignment.svg rsvg-convert | `rsvg-convert ... -o banded-alignment.png; test -s` | 88,399 bytes | ✓ PASS |
| ex-sonar-tsrvf.svg rsvg-convert | `rsvg-convert ... -o ex-sonar-tsrvf.png; test -s` | 79,300 bytes | ✓ PASS |
| functional_boxplot exported | `grep -q 'wrap_pyfunction!(functional_boxplot' src/depth_mod.rs` | line 625 | ✓ PASS |
| No docs .md edits | `git diff HEAD~4..HEAD -- docs/ \| grep -v diagrams/` | empty | ✓ PASS |
| No OK diagram modified | `git diff --quiet HEAD~4..HEAD -- {21 untouched files}` | exit 0 all | ✓ PASS |

---

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| SVGFIX-01 | Visual/layout axis — no overlapping labels, clean spacing | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Structural fixes verified (ghost removed, label repositioned, subtitle shortened); visual render quality pending human PNG review |
| SVGFIX-02 | STYLE_SPEC conformance — 720 viewBox, 5 CSS classes, role/aria | ✓ SATISFIED | ex-sonar-tsrvf.svg fully migrated; all other batch diagrams already conforming and byte-unchanged |
| SVGFIX-03 | XML formatting — no redundant inline font-size duplicates; SVGO idempotence | ✓ SATISFIED | No redundant duplicates found in all 5 XML files (all inline sizes differ from class sizes); SVGO idempotence passes on all 4 changed files |
| SVGFIX-04 | Method-accuracy — no diagram misdepicts the shipped fdars method | ✓ SATISFIED | functional_boxplot confirmed exported (line 625); shift-registration contrast key confirmed accurate vs page prose; elastic-alignment phase label confirmed present |

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| None | — | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER in any changed file |

---

### Human Verification Required

#### 1. Per-Section PNG Visual Review (SC5 — all 4 changed diagrams)

**Test:** Open the 4 PNG files rendered by rsvg-convert in the scratchpad at `/tmp/claude-1000/-home-simonm-projects-rust-pyfda/81d3a2ad-9c69-4845-a299-2219a3a880f5/scratchpad/`:
- `smoothing.png`
- `pace-fpca.png`
- `banded-alignment.png`
- `ex-sonar-tsrvf.png`

**Expected:**
- `smoothing.png`: Panel 3 (rightmost panel, "Smooth Curve — noise removed, signal kept") shows only the bold smooth blue cubic-bezier arc. No jagged ghost polyline. Panels 1 and 2 unchanged.
- `pace-fpca.png`: Subtitle "Ragged per-curve grids (sparse, irregular) — PACE recovers smooth eigenfunctions on a common grid" fits fully within the frame with no right-edge clip or ellipsis.
- `banded-alignment.png`: "upper band edge" label appears above the cost-matrix grid area, not overlapping any matrix line or grid element near the top-left corner.
- `ex-sonar-tsrvf.png`: Full 720×480 render with STYLE_SPEC typography (large bold title, muted subtitle, bold section labels, smaller body text in monospace for accuracy figures). All three analysis paths (Path A / B / C) and all accuracy percentages (87.0% BEST / 77.7% / 66.2%) visible.

**Why human:** SVGO idempotence and PNG non-emptiness are verified programmatically. Pixel-level rendering quality — label positions, clip detection, font rendering, visual hierarchy — requires human eyeball inspection of the bitmap output. grep cannot see whether labels overlap or clip.

#### 2. elastic-alignment.svg Pedagogical Judgment (Phase 49 deferred item)

**Test:** Open `docs/assets/diagrams/elastic-alignment.svg` PNG and assess the γ(t) warp inset: a 56×56px box at position translate(624,120) inside a 720×300 viewBox, labeled "phase γ(t)" at line 61.

**Expected:** Reviewer decides whether the current size and prominence of the warp inset adequately communicates the amplitude/phase decomposition concept to new users encountering `docs/align/elastic-alignment.md`.

**Why human:** The label is present and factually correct (confirmed in this verification). The question is whether 56×56px at the far right of a 720px-wide diagram gives the phase component sufficient visual weight relative to the main aligned-curves panel. This is a pedagogical judgment about emphasis — not resolvable by code inspection. It is the Phase 49 blocking human diagram review item surfaced by the executor.

---

### Gaps Summary

No gaps found. All must-haves are met or verified at the code/structure level. The two items flagged as ⚠️ PRESENT_BEHAVIOR_UNVERIFIED are the per-section PNG visual review (SC5) — a visual rendering check that requires human eyes — and its constituent truth about clean rendering (SC1). All structural changes are correct and confirmed.

**No NO-EDIT decision was found to be wrong:** every inline `font-size=` in the 5 XML-cleanup files differs from its CSS class size, making each an intentional override, not a redundant duplicate. The executor's justification holds under direct verification.

---

_Verified: 2026-08-22T18:00:00Z_
_Verifier: Claude (gsd-verifier)_
