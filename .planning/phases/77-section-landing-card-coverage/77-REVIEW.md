---
phase: 77-section-landing-card-coverage
reviewed: 2026-09-06T00:00:00Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - docs/assets/thumb/shift-registration.svg
  - docs/assets/thumb/banded-alignment.svg
  - docs/assets/thumb/pace-fpca.svg
  - docs/assets/thumb/interpolation.svg
  - docs/assets/thumb/imputation.svg
  - docs/assets/thumb/concurrent-regression.svg
  - docs/assets/thumb/functional-glm.svg
  - docs/assets/thumb/function-on-function.svg
  - docs/assets/thumb/additive-sof.svg
  - docs/assets/thumb/frechet-regression.svg
  - docs/assets/thumb/functional-time-series.svg
  - docs/assets/thumb/density-fda.svg
  - docs/assets/thumb/advanced-clustering.svg
  - docs/assets/thumb/multi-domain.svg
  - docs/assets/thumb/shapelets.svg
  - docs/assets/thumb/functional-boxplot.svg
  - docs/assets/thumb/functional-statistics.svg
  - docs/assets/thumb/scoring-metrics.svg
  - docs/assets/thumb/functional-outlier-workflow.svg
  - docs/assets/thumb/canadian-depth-centrality.svg
  - docs/assets/thumb/tolerance-vs-conformal.svg
  - docs/align/index.md
  - docs/represent/index.md
  - docs/regression/index.md
  - docs/analyze/index.md
  - docs/examples/index.md
findings:
  critical: 0
  warning: 1
  info: 3
  total: 4
status: resolved
resolution: |
  0 Critical. WR-01 fixed — added the three missing rows (functional-outlier-workflow,
  canadian-depth-centrality, tolerance-vs-conformal) to the "What each example shows"
  reference table in docs/examples/index.md. IN-01 fixed — function-on-function.svg
  y-axis/surface-box top moved 25→28 to meet the STYLE_SPEC y≥28 corpus convention
  (idempotence + rsvg render re-confirmed). IN-02 (FTS forecast segment indistinct) and
  IN-03 (density-fda LQD curve reads as a bell) are subjective visual-accuracy calls
  FORWARDED to the Phase 79 blocking human diagram review (GATE-03) — recorded here so
  the human reviewer evaluates them against the built site.
---

# Phase 77: Code Review Report

**Reviewed:** 2026-09-06
**Depth:** standard
**Files Reviewed:** 26 (21 SVG thumbnails + 5 section index.md files)
**Status:** issues_found

## Summary

Phase 77 delivers 21 new hand-authored inline-SVG thumbnails and corresponding
`fdars-gallery` card entries across five section landing pages. The work is
structurally sound: all 21 target SVG files exist on disk, all 21 card `href`
values point to existing `.md` pages, all thumbnails use the correct 320×180
viewBox, correct section hue, `role="img"` + non-empty `aria-label`, and the
`<img>` card elements all carry `class="fdars-gallery-thumb" aria-hidden="true"
alt=""`. No forbidden SVG constructs (`<script>`, `<foreignObject>`, `<title>`,
`<desc>`, `<style>`, `aria-labelledby`) appear in any of the 21 files. The sole
gradient ID (`id="fs"` in `functional-statistics.svg`) is unique across the full
thumb directory — no cross-file collision. No `ex-` prefix was applied to the
three examples thumbnails, which is correct. Insertion order across all five
galleries matches the RESEARCH.md specification.

One quality issue was found: the three newly carded examples pages are absent from
the "What each example shows" reference table at the bottom of `examples/index.md`,
which documents all carded examples and their `fdars` techniques. Two info-level
notes are raised for Phase 79 diagram review awareness, and one STYLE_SPEC
coordinate guideline minor deviation is noted.

## Warnings

### WR-01: Three new examples pages absent from the "What each example shows" table

**File:** `docs/examples/index.md:177-197`

**Issue:** The bottom of `examples/index.md` contains a table titled "What each
example shows" that lists every carded example page with its dataset and `fdars`
techniques used. Phase 77 adds gallery cards for `functional-outlier-workflow`,
`canadian-depth-centrality`, and `tolerance-vs-conformal`, but none of the three
appear as rows in this table. Every other carded example page (19 entries,
including the three Phase 76 flagships that are table-only) has a row. The
inconsistency means the table is now stale as a reference: readers who follow a
gallery link and want to cross-reference the technique inventory will find the
page missing.

**Fix:** Add three rows immediately after the existing 16 pre-Phase-76 rows (before
the Phase 76 flagships) — or group them logically beside related entries:

```markdown
| [Functional outlier workflow](functional-outlier-workflow.md) | Canadian Weather / synthetic | `magnitude_shape`, `outliergram`, `fraiman_muniz_1d` |
| [Canadian depth &amp; centrality](canadian-depth-centrality.md) | Canadian Weather | `fraiman_muniz_1d`, `modified_band_depth_1d` |
| [Tolerance vs conformal](tolerance-vs-conformal.md) | Canadian Weather | `fpca_tolerance_band`, `conformal_prediction_band` |
```

(Verify exact technique names against the page code blocks before inserting.)

---

## Info

### IN-01: function-on-function.svg — y-axis top coordinate 3 px above STYLE_SPEC guideline

**File:** `docs/assets/thumb/function-on-function.svg:3`

**Issue:** The y-axis line reads `x1="50" y1="155" x2="50" y2="25"`. The RESEARCH.md
specifies the usable coordinate region as `y∈[28,150]` (matching the corpus standard of
`y2="28"` for axis tops). At `y=25` the line top sits 3 px above the guideline boundary.
In practice the SVG renders fine within the 0–180 viewBox, and the deviation is
imperceptible at gallery thumbnail size, but it is a minor non-conformance with the
documented coordinate convention that the Phase 79 SVGO/visual gate may flag.

**Fix:** Change the y-axis line to `y2="28"` to match the corpus standard:

```xml
<line x1="50" y1="155" x2="50" y2="28" stroke="#dc3545" stroke-opacity=".35" stroke-width="1.4"/>
```

Note: the accompanying top edge path `M50 25 L278 25 L278 155` also touches `y=25`.
Changing both to `y=28` would keep all coordinates within the documented usable region.

---

### IN-02: functional-time-series.svg — forecast dashed segment nearly coincides with the bold curve's tail

**File:** `docs/assets/thumb/functional-time-series.svg:7-8`

**Issue:** (Method-accuracy note — defer final judgment to the Phase 79 human diagram review.)

The "forecast" dashed path (line 8: `M270 70 C282 65 292 52 298 46`) diverges by only
4 px in y from the bold solid curve's tail (line 7 ends at `298 50`). At 320×180 rendered
size the two lines are barely distinguishable; the forecast appears as a faint duplicate
of the current curve rather than a clearly extrapolated step. The RESEARCH concept sketch
calls for the forecast to be "projected beyond" the training curves as a clearly separate
segment. The intent reads correctly in the SVG source but may not translate to a clear
visual at thumbnail scale.

**Fix for Phase 79:** Consider diverging the dashed forecast path by at least 10–15 px
in y from the solid curve's endpoint (e.g., `M270 70 C282 58 292 44 298 36`) to make the
extrapolation visually unambiguous at small size.

---

### IN-03: density-fda.svg — LQD-transformed curve concept ambiguity at thumbnail scale

**File:** `docs/assets/thumb/density-fda.svg:7`

**Issue:** (Method-accuracy note — defer final judgment to the Phase 79 human diagram review.)

The three faint bell curves (lines 4–6) and the bold LQD-transformed curve (line 7)
are all rendered with similar curvature; the bold curve reads as a "broader, flatter"
variant of the same bell rather than as a visually distinct unconstrained-domain object.
The RESEARCH concept sketch describes the LQD curve as "flatter/straighter — the
LQD-transformed version in an unconstrained domain." At 320×180 thumbnail size the
distinction between "flatter bell" and "more nearly linear/monotone LQD log-quantile
density" is subtle, which could undermine the educational value.

**Fix for Phase 79:** Consider making the LQD bold path more distinctly non-bell-shaped
(e.g., a monotone rising arc `M40 120 C100 105 200 80 298 65`) to better convey that
the LQD transform moves densities to an unconstrained domain, or add a light horizontal
baseline that the bell curves approach but the LQD curve crosses.

---

_Reviewed: 2026-09-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
