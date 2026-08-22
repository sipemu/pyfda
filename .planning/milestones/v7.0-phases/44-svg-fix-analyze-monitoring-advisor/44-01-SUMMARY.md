---
phase: 44-svg-fix-analyze-monitoring-advisor
plan: "01"
subsystem: docs/assets/diagrams
tags: [svg, diagrams, analyze, method-accuracy, visual-fix, xml-cleanup]
status: complete

dependency_graph:
  requires: [phase-43-svg-fix-learn-represent-align]
  provides: [corrected-analyze-diagrams]
  affects: [docs/analyze/ section, Phase 49 site review]

tech_stack:
  added: []
  patterns:
    - Per-element font-size comparison against STYLE_SPEC class sizes (.ttl=17 .sub=12 .lab=13 .sm=11 .mono=12) before stripping inline overrides
    - SVGO@3.3.4 idempotence gate (check-only, never overwrite) + rsvg-convert PNG visual review

key_files:
  modified:
    - docs/assets/diagrams/outlier-detection.svg
    - docs/assets/diagrams/scoring-metrics.svg
    - docs/assets/diagrams/elastic-clustering.svg
    - docs/assets/diagrams/clustering.svg
  created: []

decisions:
  - "KEEP Amplitude taxonomy: outlier-detection.svg 'Magnitude/Shape/Amplitude' taxonomy confirmed canonical against docs/analyze/outlier-detection.md:9 and src/outliers_mod.rs:257-271 (tvdmss returns amplitude_outliers; MUOD detects amplitude outliers)"
  - "REPLACE conformal_prediction_band() with magnitude_shape(): confirmed no conformal_prediction_band in src/conformal_mod.rs; chose magnitude_shape() (src/outliers_mod.rs:93) as it targets both magnitude and shape outliers and is taught in outlier-detection.md:22"
  - "DECLINE elastic-clustering function-name sub-label: adding elastic_self_dist_matrix() as a mono sub-label caused text overflow past the 140px box width even at 9px — declined for Phase 49 rather than accepting layout regression"
  - "COMPRESS scoring-metrics right panel: reduced row spacing from 34px→28px and row height from 26→24px with translate y=112→108, fitting all 5 rows + 2 warnings inside the orange panel rect (last item at absolute y=275, panel bottom at y=278)"

metrics:
  duration_seconds: 507
  duration_label: "8m"
  completed_date: "2026-08-22"
  completed_tasks: 3
  total_tasks: 3
  commits: 1

actuals:
  tokens: 22000
  tasks: 3
  commits: 1
---

# Phase 44 Plan 01: SVG Fix — analyze/ section Summary

Fixed 4 of 6 flagged analyze/ diagrams across method-accuracy, visual/layout, and XML axes. gmm-clustering.svg and seasonal-analysis.svg confirmed byte-unchanged as expected (all inline sizes intentional).

## Per-Diagram Outcome

### outlier-detection.svg — CHANGED

**Status:** Fixed on all three axes.

**Axis A — Method-accuracy (SVGFIX-04):**
- Taxonomy "Magnitude / Shape / Amplitude" confirmed **canonical** against `docs/analyze/outlier-detection.md:7-9` and `src/outliers_mod.rs:257-271`. The Amplitude panel was NOT relabelled.
- `conformal_prediction_band()` confirmed non-existent (no such `pub fn` in `src/conformal_mod.rs`). **Replaced with `magnitude_shape()`** — a real binding at `src/outliers_mod.rs:93`, taught in `docs/analyze/outlier-detection.md:22` (targets magnitude and shape outliers). Caption: `magnitude_shape() → M-S plane`.

**Axis B — Visual/layout (SVGFIX-01):**
- Bottom-row rects widened from 170px to 185px and redistributed (x=10/205/400, previously 20/215/410) to give right-edge headroom.
- Middle box caption shortened from `detect_outliers_lrt() → likelihood test` to `detect_outliers_lrt() → LRT` to eliminate text overflow within the 185px rect.
- All three detection-method labels now sit fully within their rects (verified on PNG).

**Axis C — XML (SVGFIX-02/03):**
- Inline sizes (17.5, 12.5, 10px) all differ from their class values → **zero redundant overrides stripped** (intentional per-element tweaks preserved).

**SVGO:** Idempotent. PNG: renders cleanly.

---

### scoring-metrics.svg — CHANGED

**Status:** Fixed (right panel visual cramping resolved).

**Fix applied:** Compressed right panel row spacing (34px→28px gap, row height 26→24px) and moved group translate from y=112 to y=108. Result: all 5 metric rows plus both `⚠ MAPE` and `⚠ MSLE` warnings now fit inside the orange panel rect (last warning at absolute y=275, panel bottom at y=278 — 3px clearance).

**No XML/STYLE_SPEC changes:** No inline font-size overrides existed in this file; none were introduced.

**SVGO:** Idempotent. PNG: both panels render cleanly with warnings fully visible.

---

### elastic-clustering.svg — CHANGED

**Status:** Redundant overrides stripped; conservative wording enrichment applied; function-name sub-label **declined** for Phase 49 review.

**Override strip (XML):**
- Stripped `font-size="11"` from 6 `.sm` elements (11 = .sm class size → redundant): Step 2 "Elastic Distance"/"Matrix", Step 3 "Distance-Based"/"Clustering", Step 4 "Cluster"/"Assignments"/"Aligned Mean"/"Curves".
- KEPT `.sm font-size="12"` on Step 1 "Raw Curves" (12 ≠ 11 → intentional).
- KEPT `.lab font-size="11"` on "COMPUTATION"/"RESULTS" labels (11 ≠ 13 → intentional smaller size for section headers).
- KEPT all `style="fill:#333"` overrides (#333 ≠ .sm's #495057 → intentional color).

**Wording enrichment (conservative):**
- Step 3 label changed from `"K-Means / Hierarchical"` to `"Distance-Based Clustering"`. Rationale: `docs/analyze/elastic-clustering.md` teaches that plain L² k-means fails on elastic distances; the diagram previously implied it was a valid path. "Distance-Based Clustering" is method-accurate and keeps the 4-box structure intact.
- `aria-label` updated to match: "...distance-based clustering..." (from "K-means or hierarchical clustering...").

**Declined enrichment (Phase 49):**
- Adding `elastic_self_dist_matrix()` as a mono sub-label inside the Step 2 box (140px wide) caused text overflow past the box edge at any legible size. Deferred to Phase 49 human review — the box wording "Elastic Distance Matrix" is accurate without the API name.

**SVGO:** Idempotent. PNG: renders cleanly.

#### Phase 49 Callout: elastic-clustering.svg enrichment

| Item | Decision | Rationale |
|------|----------|-----------|
| Step 3 wording: "K-Means / Hierarchical" → "Distance-Based Clustering" | **Applied** | Method-accuracy: page teaches L² k-means fails; "Distance-Based" is neutral and correct |
| API name sub-label `elastic_self_dist_matrix()` in Step 2 box | **Deferred** | 140px box too narrow for the function name at any readable font size; Phase 49 reviewer may widen the box or use an alternative layout |
| Broader enrichment (add algorithm details, multiple sub-boxes) | **Deferred** | Design judgment — diagram is intentionally sparse (pipeline overview); Phase 49 decides extent |

---

### clustering.svg — CHANGED

**Status:** 2 redundant overrides stripped (exactly as planned).

- `.lab font-size="13"` on "Optimal k" label (line 49) → stripped (13 = .lab class size).
- `.lab font-size="13"` on "Initialization" label (line 57) → stripped (13 = .lab class size).
- All other overrides KEPT: `.ttl font-size="20"` (17≠20), `.sub font-size="14"` (12≠14), `.lab font-size="15"` (13≠15), `.sm font-size="12"` (11≠12).

**Renders visually identical:** Override strip has no visible effect; verified on PNG.

**SVGO:** Idempotent. PNG: renders cleanly.

---

### gmm-clustering.svg — CONFIRMED BYTE-UNCHANGED

Re-inspection confirmed: every inline `font-size=` differs from its class value:
- `.ttl font-size="20"` (17≠20) → intentional
- `.sub font-size="14"` (12≠14) → intentional  
- `.lab font-size="14"` and `font-size="15"` (13≠14, 13≠15) → intentional
- `.sm font-size="12"` (11≠12) → intentional

Zero redundant overrides found. File left byte-unchanged. This is the correct outcome (mirrors Phase 43 "5 files left byte-unchanged" precedent).

---

### seasonal-analysis.svg — CONFIRMED BYTE-UNCHANGED

Re-inspection confirmed: every inline `font-size=` differs from its class value:
- `.ttl font-size="20"` (17≠20) → intentional
- `.sub font-size="14"` (12≠14) → intentional
- `.lab font-size="14"` and `font-size="15"` (13≠14, 13≠15) → intentional
- `.sm font-size="12"` (11≠12) → intentional

Zero redundant overrides found. File left byte-unchanged.

---

## Override Tally Per File

| File | Redundant stripped | Reason kept |
|------|--------------------|-------------|
| outlier-detection.svg | 0 | All inline values differ from class (.ttl 17.5≠17, .sm 10≠11, etc.) |
| scoring-metrics.svg | 0 | No inline font-size overrides present |
| elastic-clustering.svg | 6 × `font-size="11"` on `.sm` | 11=.sm class 11px |
| clustering.svg | 2 × `font-size="13"` on `.lab` | 13=.lab class 13px |
| gmm-clustering.svg | 0 | All differ (confirmed) |
| seasonal-analysis.svg | 0 | All differ (confirmed) |

## Deviations from Plan

### Auto-fixed Deviations

**1. [Rule 1 - Bug] scoring-metrics.svg right panel required more than a nudge**
- **Found during:** Task 2 visual verification
- **Issue:** Moving warnings up by a few px was insufficient — the content (5 rows + 2 warnings) structurally exceeds the 166px available in the translate(452,112) group within the 218px panel
- **Fix:** Compressed row spacing (34→28px gap, 26→24px height, translate y 112→108) — all content now fits with 3px clearance
- **Files modified:** scoring-metrics.svg

**2. [Rule 1 - Bug] elastic-clustering.svg function name sub-label caused overflow**
- **Found during:** Task 2 visual verification  
- **Issue:** `elastic_self_dist_matrix()` in mono font at 9px overflowed the 140px Step 2 box left edge even with `style="font-size:9px"` (CSS class `font` shorthand takes precedence over XML attribute)
- **Fix:** Removed the function name sub-label; deferred to Phase 49; Step 2 label "Elastic Distance Matrix" is method-accurate
- **Files modified:** elastic-clustering.svg

## No-Churn Guard

`git diff --name-only -- docs/assets/diagrams/*.svg` at commit time:
- `docs/assets/diagrams/outlier-detection.svg` ✓
- `docs/assets/diagrams/scoring-metrics.svg` ✓
- `docs/assets/diagrams/elastic-clustering.svg` ✓
- `docs/assets/diagrams/clustering.svg` ✓

The 11 OK diagrams (tolerance-bands, functional-outliers, functional-boxplot, equivalence-testing, covariance-functions, functional-statistics, spm, advanced-spm, profile-partial-monitoring, advisor-loop, advisor-grounding-invariant) and depth-functions.svg are all byte-unchanged.

## Success Criteria

- [x] SC1: Every flagged analyze/ diagram renders cleanly — no overlapping labels, no text overflowing container rect
- [x] SC2: Every diagram conforms to STYLE_SPEC (720 viewBox, five CSS classes, role="img"+aria-label) — preserved on all changed files
- [x] SC3: outlier-detection.svg taxonomy confirmed canonical (Amplitude kept); third detection label corrected from non-existent conformal_prediction_band() to real magnitude_shape()
- [x] SC4: All 4 changed diagrams pass SVGO@3.3.4 idempotence; 11 OK diagrams byte-unchanged
- [x] SC5: analyze/ section passed PNG review before commit (per-diagram gate + visual verification in scratchpad PNGs)
- [x] elastic-clustering.svg enrichment extent surfaced for Phase 49 human diagram review

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| SUMMARY.md exists on disk | FOUND |
| Commit b6e384b exists in git log | FOUND |
| outlier-detection.svg exists | FOUND |
| scoring-metrics.svg exists | FOUND |
| elastic-clustering.svg exists | FOUND |
| clustering.svg exists | FOUND |
| conformal_prediction_band removed | CONFIRMED |
| magnitude_shape() present | CONFIRMED |
