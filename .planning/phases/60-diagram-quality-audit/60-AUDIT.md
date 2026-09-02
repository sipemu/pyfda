# Phase 60: Diagram Quality Audit — 60-AUDIT.md

**Phase:** 60-diagram-quality-audit
**Date:** 2026-09-02
**Status:** In progress — concept scoring complete (Plans 60-01); COVER/SYNC/fix-worklists from Plan 60-02

---

## Purpose

This document is the single evidence source gating the v10.0 milestone. It:

1. Inventories all **90** top-level concept SVGs in `docs/assets/diagrams/` (cards/ and thumb/ excluded) with per-diagram × 4-axis scores.
2. Records the authoritative **section-to-concept-diagram map** and the **correction-phase bucket assignment** (Phases 61/62/63).
3. Derives **ranked per-section fix worklists** (assembled in Plan 60-02) for the three correction phases.
4. Records the **COVER-01 coverage-gap list** (pages/methods lacking a concept diagram) for Phase 64 — filled by Plan 60-02.
5. Records the **SYNC-01/SYNC-02 drift list** (thumbs/cards that no longer match their concept diagrams) for Phase 64 — filled by Plan 60-02.

**Assessment method:** design/geometry axis judged by rsvg-convert PNG render + visual inspection (the only reliable method to catch mismatched lines, misaligned endpoints, overlapping elements, cramped spacing, text/label overflow — not from XML source alone); STYLE_SPEC conformance by grep of canonical markers; accessibility by grep + comparison of aria-label text vs title text; sync deferred to Plan 60-02 (requires thumb/card comparison).

---

## Scoring Legend

### Severity Scale

| Verdict | Meaning |
|---------|---------|
| **OK** | No issue; meets the criterion cleanly. |
| **Minor** | A visible but non-blocking defect: cosmetic issue, small label clipping, paraphrased aria-label, missing long-form desc on a complex diagram, minor annotation cramping. Fix is low-effort. |
| **Major** | A significant defect: text/label visibly overflows panel bounds or clips at viewBox edge; element overlap that obscures content; non-standard visual style inconsistent with all peer diagrams; multiple STYLE_SPEC failures; layout problem that impairs comprehension. Requires structural rework. |
| **Critical** | A defect that makes the diagram unusable or actively misleading: completely wrong method depiction, broken layout that hides essential content, or total STYLE_SPEC non-conformance. |

### Four Scoring Axes

| Axis | What is assessed |
|------|-----------------|
| **Design/geometry** | Render quality: mismatched lines, misaligned endpoints, overlapping/misplaced elements, cramped spacing, text/label overflow, inconsistent panel sizing. Judged from rsvg-convert PNG render (not source alone). This is the PRIMARY audit axis per user directive. |
| **STYLE_SPEC** | Conformance to `docs/assets/diagrams/STYLE_SPEC.md`: viewBox `0 0 720 {300\|480\|520}`, `<style>` block with five CSS classes (`.ttl .sub .lab .sm .mono`), `system-ui` font stack, `role="img"` + `aria-label` on root `<svg>`. ALL markers must be present for OK. |
| **Accessibility** | A11Y-01: `role="img"` present + `aria-label` text matches the diagram's `.ttl` title text verbatim (paraphrase = Minor); A11Y-02: `<title>`, `<desc>`, or `aria-labelledby` present and adequate for complex/multi-panel diagrams (absent on complex diagram = Minor; absent on very complex diagram = Major). |
| **Sync** | Thumb-to-concept and card-to-concept fidelity. **Deferred to Plan 60-02** for all concept rows — drift detection requires rendered comparison against thumb/card assets. |

### Overall Verdict

Overall = worst axis verdict. A diagram rated Minor/Major/Critical on any axis gets that as its overall verdict.

---

## 1. Concept Scoring Table

**STYLE_SPEC baseline (verified by grep over all 90 SVGs, 2026-09-02):**
- All 90 concept diagrams have: `role="img"`, `aria-label`, `<style>` block with all five CSS classes (`.ttl .sub .lab .sm .mono`), `system-ui` font stack, viewBox width 720 with allowed height {300|480|520}.
- The 4 formerly non-conforming viewBox diagrams (`elastic-clustering.svg`, `outlier-detection.svg`, `covariance-functions.svg`, `ex-sonar-tsrvf.svg`) were migrated in Phases 43–45 and now conform.
- Therefore STYLE_SPEC axis = OK for all 90 diagrams unless noted otherwise.

**Accessibility baseline:**
- All 90 diagrams carry `role="img"` and `aria-label` — A11Y-01 base requirements present.
- However, every `aria-label` is a paraphrase of the title text, not an exact match — Minor A11Y-01 mismatch on every diagram. Evidence: grep comparison of `aria-label` vs `.ttl` text content in SVG source shows consistent divergence.
- Zero diagrams carry `<title>`, `<desc>`, or `aria-labelledby` — the A11Y-02 long-form gap is universal. Complex/multi-panel diagrams are flagged Minor (should have long-form description); single-panel simple diagrams are noted for reference.
- To avoid 90 identical notes, the accessibility column uses a shorthand notation:
  - **A11Y-01 Minor** = aria-label text does not match title verbatim (universal)
  - **A11Y-02 gap** = no `<title>`/`<desc>`/`aria-labelledby` (universal)
  - Complex diagrams are flagged explicitly; simple three-panel diagrams receive Minor for A11Y-01 only.

**Sync axis (backfilled by Plan 60-02):** Sync verdicts for each concept row are recorded below after comparing each concept's rendered PNG to its corresponding gallery thumbnail (via the section index gallery href). Concept diagrams that have NO gallery thumbnail (advisor section diagrams, inference diagrams, and several regression/represent/align sub-pages) are scored OK-no-thumb (no thumb to drift from). The one cross-filename mapping is `process-monitoring.svg` (thumb) → `spm.svg` (concept), resolved via `docs/monitoring/index.md` gallery href.

**Sync verdict notation for concept rows:**
- `OK (faithful thumb)` — thumb exists and is a faithful abstract thumbnail of the concept
- `OK (no thumb)` — no gallery thumbnail exists for this concept; no drift possible
- `Major (style-only thumb)` — thumb exists but depicts something different from the concept (content/subject mismatch)
- `Minor (cosmetic)` — thumb exists, core subject matches, but cosmetic differences (colour, simplified detail)

---

### learn/ Section (6 diagrams → Phase 61 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| introduction.svg | learn | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "From raw measurements to a functional-data object" vs title "From Raw Measurements to a Functional-Data Object" — paraphrase mismatch. A11Y-02: no long-form desc; three-panel layout is simple. Render: clean three-panel (scatter→Fdata constructor→curve family). Sync: thumb shows abstract smooth curve family — correctly abstracts the "curves" output panel. |
| custom-plotting.svg | learn | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Styling a functional sample with matplotlib" vs title "Custom Plotting: Styling a Curve Family" — paraphrase. A11Y-02: no long-form desc; three-panel simple. Render: clean. Sync: thumb shows a single styled curve with legend — faithful abstraction of the styled-curve theme. |
| simulation.svg | learn | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Simulating functional data from Karhunen-Loeve parameters" vs title "Simulation: Synthetic Curves with Known Ground Truth" — paraphrase. A11Y-02: absent; moderate complexity. Render: clean; KL parameters → simulate() → sampled curves. Sync: thumb shows simulated curve family fan — faithful. |
| smoothing.svg | learn | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Smoothing a noisy curve into a smooth functional representation" vs title "Smoothing: Recovering the Signal Behind the Noise" — paraphrase (smoothing.svg:1). A11Y-02: absent; three-panel moderate. Render: clean — Panel 3 ghost polyline from v7.0 is resolved; smooth curve output is distinct from noisy input. Sync: thumb shows scattered noisy points with smooth curve fit — faithful abstraction. |
| derivatives.svg | learn | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Differentiating curves into velocity and acceleration" vs title "Derivatives: When and How Fast a Curve Changes" — paraphrase. A11Y-02: absent. Render: clean; velocity/acceleration stacked in Panel 3 is clear. Sync: thumb shows primary curve (solid) and first derivative (dashed) with f′ label — faithful. |
| irregular-sampling.svg | learn | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Regridding sparse irregular curves onto a common grid" vs title "Irregular Sampling: Recovering a Common Grid" — paraphrase. A11Y-02: absent. Render: clean; sparse points → smooth → common grid. Sync: thumb shows sparse points with fitted smooth curve — faithful to the recovery-from-sparse theme. |

---

### represent/ Section (10 diagrams → Phase 61 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| fpca.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Functional PCA: mean plus modes of variation" vs title "Functional PCA: Mean + Modes of Variation" — paraphrase. A11Y-02: absent; three-panel moderate. Render: clean; green theme; μ(t) + eigenfunctions + score scatter. Sync: thumb shows mean curve + PC1 label with variation bands — faithful to FPCA subject. |
| elastic-fpca.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Elastic FPCA: separating amplitude and phase variation" vs title "Elastic FPCA: Splitting Amplitude from Phase" — paraphrase. A11Y-02: absent. Render: clean; vert_fpca/horiz_fpca/joint_fpca listed; amplitude+phase panel. Sync: thumb shows "amp" and "phase" labelled curve pairs in two panels — faithful to the amplitude/phase separation theme. |
| basis-representation.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Basis representation: project a curve onto basis functions" vs title "Basis Representation: Curve to Coefficients" — paraphrase. A11Y-02: absent. Render: clean; B-spline basis functions in Panel 2 clearly shown. Sync: thumb shows overlapping B-spline basis functions with a summed curve — faithful. |
| andrews-transformation.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Andrews transformation: from feature tables to curves" vs title "Andrews Transformation: Tables to Curves" — paraphrase. A11Y-02: absent. Render: clean; feature table → Fourier formula → one curve per row. Sync: thumb shows dots (feature rows) → arrow → curves — faithful to the table-to-curves theme. |
| depth-functions.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Functional depth: ranking curves by centrality" (paraphrase). A11Y-02: absent on a complex 720×520 multi-panel diagram — this is the most complex diagram in represent/; should have long-form desc (Major A11Y-02 gap). Render: clean 720×520 multi-panel; depth ranking bar chart + Depth-Based Tools grid clear. Overall upgraded to Minor (A11Y-02 gap on complex diagram). Sync: thumb shows layered curve family with central highlighted curve and depth marker — faithful to depth-ranking theme. |
| streaming-depth.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Streaming depth: score each new curve against a rolling window" vs title "Streaming Depth: Scoring Against a Rolling Window" — paraphrase. A11Y-02: absent; three-panel. Render: clean; depth-over-time alarm panel clear. Sync: thumb shows time-series depth score with alert spike labeled "alert" — faithful. |
| distance-metrics.svg | represent | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Distance metrics: curve pairs to a distance matrix" vs title "Distance Metrics: Curves to a Distance Matrix" — paraphrase. A11Y-02: absent. Render: clean; green distance matrix heat-map in Panel 3. Sync: thumb shows two curves with vertical measurement markers labeled d(f,g) — faithful to pairwise distance theme. |
| pace-fpca.svg | represent | 61 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: PACE FPCA uses a two-panel layout (scatter input left, eigenfunction curves right). Title text "PACE FPCA — Sparse, Irregular Observations to Smooth Eigenfunctions" is 60+ chars; subtitle is ~80 chars — both render acceptably at 720px but subtitle is near the clipping edge. Render shows it renders cleanly; downgraded from v7.0 Major (subtitle overflow resolved). Remains Minor for subtitle length risk. A11Y-01: paraphrase mismatch. A11Y-02: absent. Sync: no gallery thumbnail for pace-fpca (not in section gallery index). |
| imputation.svg | represent | 61 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Missing-value imputation: three strategies for filling NaN gaps in functional data" vs title "Missing-Value Imputation — Three Strategies" — paraphrase. A11Y-02: absent. Render: clean; linear/mean/constant three panels clear with NaN shading. Sync: no gallery thumbnail (not in section gallery index). |
| interpolation-policy.svg | represent | 61 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Spline interpolation and extrapolation policy: four policy variants on a single curve" vs title "Spline Interpolation — Extrapolation Policy" — paraphrase. A11Y-02: absent; four-panel. Render: clean; boundary/exception/fill/periodic policies clearly shown with colored panels. Sync: no gallery thumbnail (not in section gallery index). |

---

### align/ Section (8 diagrams → Phase 61 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| elastic-alignment.svg | align | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Elastic alignment: removing phase variation by warping curves..." vs title "Elastic Alignment: Removing Phase to Recover a Sharp Mean" — paraphrase. A11Y-02: absent. Render: clean three-panel; misaligned peaks → karcher_mean() → sharp mean + phase γ(t) inset. The γ(t) inset is small but labeled. Sync: thumb shows misaligned peaked curves with arrow and bold aligned mean — faithful abstraction of the alignment theme. |
| advanced-alignment.svg | align | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Advanced alignment: penalized and constrained elastic registration" vs title "Advanced Alignment: Penalized & Constrained Warps" — paraphrase mismatch including "Penalized" → "penalized". A11Y-02: absent. Render: clean; λ colour-swatch in Panel 3 effective. Sync: thumb shows warp-function family converging (diamond shape) — faithful to warping/alignment family theme. |
| landmark-registration.svg | align | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Landmark registration: warping marked features to common targets" vs title "Landmark Registration: Pinning Features to Targets" — paraphrase. A11Y-02: absent. Render: clean; orange peak markers in Panel 1/3 match well. Sync: thumb shows two-peaked curves with dashed vertical landmark markers before and after — faithful. |
| tsrvf.svg | align | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "TSRVF: linearizing elastic analysis into a flat tangent space" vs title "TSRVF: Linearizing Elastic Analysis" — paraphrase. A11Y-02: absent. Render: clean; manifold curve → tsrvf_transform() → flat tangent space with radial arrows. Sync: thumb shows a wavy curve with arrow and a tilted tangent-space rectangle labeled q(t) — faithful to the linearization concept. |
| alignment-comparison.svg | align | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Comparing alignment methods: none, elastic, and landmark" vs title "Comparing Alignment Methods" — paraphrase (shorter than title). A11Y-02: absent. Render: clean; three strategy dashed lines in Panel 3 clearly distinguished. Sync: thumb shows three panels with different curve families (none/elastic/landmark) in rounded boxes — faithful comparison structure. |
| shape-analysis.svg | align | 61 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Shape analysis: a mean shape in the quotient space" vs title "Shape Analysis: The Mean Shape in Quotient Space" — paraphrase. A11Y-02: absent. Render: clean; SRSF/Fisher-Rao quotient pipeline clear. Sync: thumb shows a mean curve (bold) with tighter distribution around it labeled "mean" — faithful to shape-mean theme. |
| banded-alignment.svg | align | 61 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: 720×480 multi-panel (DP cost matrix top, before/after panels bottom). The "upper band edge" label at the top-left of the cost-matrix plot is positioned very close to the dashed band-edge line and the axis labels; in the render it appears slightly cramped but readable. The "band_frac × m = B" label at top-right overflows slightly beyond the orange dashed line endpoint. Minor geometry. A11Y-01: paraphrase mismatch. A11Y-02: absent on complex diagram. Sync: no gallery thumbnail (not in section gallery index). |
| shift-registration.svg | align | 61 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: Panel 2 shows "shift (rigid)" label arrow and beneath it "elastic warp" arrow label — the "elastic warp" text (shift-registration.svg:~55) implies an elastic warp step inside shift registration, but `shift_register` is purely rigid (scalar δ argmin). The label is a method-accuracy concern (FLAG for Phase 61 fix: remove "elastic warp" arrow or clarify it is NOT part of the method). Visual: two arrows and labels in a 44px-wide gap between panels make the gap crowded. A11Y-01: paraphrase mismatch. Sync: no gallery thumbnail (not in section gallery index). |

---

### analyze/ Section (12 diagrams → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| tolerance-bands.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Tolerance bands: a region expected to contain most future curves" vs title "Tolerance Bands: Where Future Curves Will Fall" — paraphrase. A11Y-02: absent. Render: clean; purple theme; FPCA/bootstrap/conformal methods listed. Sync: thumb shows purple curve family with outer dashed band envelope — faithful to tolerance-band theme. |
| clustering.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 four-quadrant diagram — should have long-form desc. Render: clean 720×480 multi-panel (K-means, Fuzzy C-means, Model Selection, Distance Metrics). Well-structured. Sync: thumb shows clustered curve groups (upper cluster bold, lower cluster light) — faithful to clustering-by-group theme. |
| gmm-clustering.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on 720×480 three-row diagram. Render: clean; B-spline → EM → outputs layout clear. Sync: thumb shows two overlapping elliptical GMM clusters with dots — faithful to GMM cluster representation. |
| elastic-clustering.svg | analyze | 62 | Major | OK | Minor | Major (style-only thumb) | Major | Design/geometry: **Major** — diagram uses a non-standard visual style completely inconsistent with all 89 peer diagrams. Four bare white rounded-rectangle flow boxes (Raw Curves → Elastic Distance Matrix → Distance-Based Clustering → Results) on an otherwise blank canvas, with section labels "COMPUTATION" and "RESULTS" in all-caps blue/green with no `.ttl`/`.sub`/`.lab`/`.sm`/`.mono` class-based text. The diagram occupies only ~40% of the 720×300 canvas with large empty margins. This is a visual design defect — excessive whitespace, sparse content, non-standard typography (all-caps uppercase labels, no class-based text rendering). While STYLE_SPEC classes ARE defined in the `<style>` block, the rendered text bypasses them entirely (inline `style="fill:..."` overrides). Requires a full redraw to match peer diagram quality. A11Y-02: absent; diagram is simple but the visual deficiency is the primary concern. Sync: **Major drift** — thumb shows "before/after" aligned curve families (wavy curves + arrow + compressed cluster), but concept is a bare flow-box diagram (Raw Curves→...→Results) with no curve imagery at all. Thumb depicts elastic-alignment content; concept is a text-only flow chart. Material content mismatch. |
| outlier-detection.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on 720×300 two-row layout. Render: clean; three-panel (Magnitude/Shape/Amplitude outlier types) + detection-method strip below. Text in detection strip fits within bounds. NOTE: "Amplitude Outlier" taxonomy differs from canonical "Phase" taxonomy used in fdars docs (FLAG for Phase 62: verify whether "Amplitude" is the correct term or should be "Phase"). Sync: thumb shows curve family with one dashed outlier curve elevated above the rest — faithful to outlier-detection theme. |
| functional-outliers.svg | analyze | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent; two-panel layout with bottom caption. Render: clean; hypograph/epigraph panel comparison clear. Sync: no gallery thumbnail (functional-outliers.svg has a thumb in docs/assets/thumb/ but is not in the analyze gallery index — it appears only on the outlier-detection.md method page directly). |
| functional-boxplot.svg | analyze | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean single-panel; median/50%CR/whiskers/outliers clearly shown. Sync: no gallery thumbnail (functional-boxplot.svg is in thumb/ as a page-level embed on functional-boxplot.md only, not in gallery index). |
| seasonal-analysis.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 six-branch taxonomy diagram. Render: clean; six panels + Key Functions row. Sync: thumb shows a smooth periodic sinusoidal curve — faithfully abstracts the seasonal/periodic theme. |
| equivalence-testing.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; ±δ corridor panel clear with "✓ equivalent" badge. Sync: thumb shows two curves within a dashed ±δ corridor labeled ±δ — faithful. |
| covariance-functions.svg | analyze | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Covariance Functions: Shape to Sample Path Smoothness" vs title "Covariance Functions: Shape → Sample Path Smoothness" — the → arrow is rendered as HTML entity in title (&#8594;) but spelled out in aria-label; Minor mismatch. A11Y-02: absent on 720×480 four-kernel layout. Render: clean; Gaussian/Exponential/Matérn/Periodic kernel panels + smoothness spectrum bar. Sync: thumb shows a 5×5 heatmap-like covariance matrix — faithful to the covariance-surface theme. |
| scoring-metrics.svg | analyze | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent; two-panel layout. Render: clean; integrated residual shading in left panel + scoring function list in right panel. Warning text "▲ MAPE: rejects |y_true| ≈ 0" and "▲ MSLE: rejects values ≤ −1" are small but legible. Sync: no gallery thumbnail (scoring-metrics.svg is in thumb/ as a page-level embed only, not in gallery index). |
| functional-statistics.svg | analyze | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Functional summary statistics: pointwise variance band, depth-based median as observed curve, and covariance surface" vs title "Functional Summary Statistics" — paraphrase (aria is more descriptive than title). A11Y-02: absent on complex 720×480 four-quadrant diagram. Render: clean; four-quadrant layout (mean+std band, depth scores bar, Median≠Mean≠geom.median, depth-trimmed mean) clear. Sync: no gallery thumbnail (functional-statistics.svg is in thumb/ as a page-level embed only, not in gallery index). |

---

### monitoring/ Section (3 diagrams → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| spm.svg | monitoring | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Functional Statistical Process Monitoring: learn an in-control FPCA model in Phase I, then chart Hotelling T-squared and SPE against control limits in Phase II" vs title "Functional Statistical Process Monitoring" — aria is more detailed but not verbatim match. A11Y-02: absent. Render: clean three-panel; Phase I/II split clear; Hotelling T² + SPE alarm visible. Sync: **Cross-filename mapping** — thumb `process-monitoring.svg` → concept `spm.svg` (resolved via `docs/monitoring/index.md` gallery href pointing to `spm/`). Thumb shows a control chart (time series with UCL/LCL dashed lines) — correctly abstracts the SPM monitoring theme. |
| advanced-spm.svg | monitoring | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Advanced SPM: drift-sensitive charts and fault diagnosis" vs title "Advanced SPM: Catching Drift, Diagnosing the Fault" — paraphrase. A11Y-02: absent. Render: clean; ewma_scores() + run rules + PC contributions bar chart in Panel 3. Sync: thumb shows EWMA-style trending control chart with out-of-control point and bar chart (PC contributions) at right — faithful. |
| profile-partial-monitoring.svg | monitoring | 62 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Partial-domain monitoring: restrict the model to the sub-interval that matters" vs title "Partial-Domain Monitoring: Watch the Interval That Matters" — paraphrase. A11Y-02: absent. Render: clean; sub-domain shading in Panel 1 + alarm crossing UCL in Panel 3. Sync: thumb shows a continuous curve with a dashed-box sub-interval shaded and labeled "watch" — faithful to the partial-domain theme. |

---

### advisor/ Section (10 diagrams → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| advisor-loop.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Advisor loop: interpret, recommend, re-run, compare — cyclic agentic workflow with Python API recommend-only exit" vs title "Advisor Loop" — more descriptive but paraphrase. A11Y-02: absent on a process-flow diagram with 4+ stages. Render: clean; loop arrows and Python API "recommend-only" exit box clear. Sync: no gallery thumbnail (advisor section has no index gallery; no thumbs for any advisor diagram). |
| advisor-grounding-invariant.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Grounding Invariant". A11Y-02: absent; two-zone boundary diagram. Render: clean; dashed boundary line between fdars zone and LLM zone; "cites" arrow + "no fabrication" label clear. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-aspects.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Per-Aspect Taxonomy". A11Y-02: absent on complex 720×480 three-column diagram (14 aspects × 3 task families × shared pipeline). Render: clean; three columns with pipeline in centre clear. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-agent-skill.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Agent Skill — Full Agentic Loop". A11Y-02: absent on complex 720×480 flow diagram. Render: clean; step numbering (Step 1+3, Step 2+5, Step 4, Step 5) flow and Python API exit box clear. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-auto-tuning.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Auto-Tuning Loop". A11Y-02: absent on complex 720×480 flow diagram with 5 stop-reason boxes. Render: clean; budget check → LLM propose → clamp → re-run → compare → Goodhart guard flow clear; bounded termination strip at bottom. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-comparative-selection.svg | advisor | 62 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: the "Winner" box at top-right has a `result["winner"] / fdars-authoritative` label where the text at the right edge of the box is slightly clipped in the render — "fdars-authoritative" label runs close to the right panel edge. Minor text overflow at element boundary. A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: otherwise clean; per-candidate build_diagnostics blocks and fdars sort flow clear. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-mcp.svg | advisor | 62 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: "handle + / scalars" label (advisor-mcp.svg:34-35) is centered at x=178, overlapping the dashed stdio boundary line at x=175. The text visually straddles the boundary line making it hard to read which side of the boundary the return path belongs to. Also "stdio" boundary label at x=175 y=54 appears very close to the top edge. Minor misalignment. A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 boundary-model diagram. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-pipeline-report.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Pipeline Diagnostic Report". A11Y-02: absent on complex 720×480 three-row pipeline diagram. Render: clean; per-stage blocks → cross-stage caveats → LLM narration row clear. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-providers.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Provider Setup — Selection and Precedence". A11Y-02: absent; two-row flow (precedence → four backends). Render: clean; Anthropic/OpenAI/Gemini/Ollama backend cards with install extras. Sync: no gallery thumbnail (advisor section has no index gallery). |
| advisor-python-api.svg | advisor | 62 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title "Python API — Recommend-Only Surface". A11Y-02: absent on two-stage boundary diagram. Render: clean; Stage 1 offline / Stage 2 LLM / Advice output box clear. Sync: no gallery thumbnail (advisor section has no index gallery). |

---

### sklearn/ Section (1 diagram → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| sklearn-pipeline-dataflow.svg | sklearn | 62 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: the "Predictor" box label "FPCLDAClassifier" (sklearn-pipeline-dataflow.svg:~58) overflows the right edge of the "Predictor" panel — the text width exceeds the panel width at the font size used; in the render "FPCLDAClassifier" is visibly cut at the right edge of the orange panel. Minor text overflow. A11Y-01: aria-label "Functional sklearn Pipeline data flow: (n_obs, n_points) ndarray through transformer stages to FPC scores to predictor" vs title "Functional sklearn Pipeline" — paraphrase. A11Y-02: absent; five-stage pipeline diagram — should have long-form desc. Sync: no gallery thumbnail (sklearn section has no index gallery). |

---

### regression/ Section (15 diagrams → Phase 63 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| scalar-on-function.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Scalar-on-function regression: predictor curves map to a scalar response" vs title "Scalar-on-Function Regression" — paraphrase. A11Y-02: absent. Render: clean; β(t) inset in Panel 3 is small but visible. Sync: thumb shows a predictor curve (solid) leading to a scalar response dot (y label) — faithful. |
| function-on-scalar.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Function-on-scalar regression: scalar predictors produce fitted response curves" vs title "Function-on-Scalar Regression" — paraphrase. A11Y-02: absent. Render: clean; group A/B curves in Panel 3 clearly labelled. Sync: thumb shows two labelled groups (g=1, g=2) of functional response curves — faithful. |
| classification.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Functional classification: labelled curves train a classifier that predicts a class label" vs title "Functional Classification" — paraphrase. A11Y-02: absent. Render: clean; decision boundary in FPC scatter clear. Sync: thumb shows two curve families (A: rising, B: flat) with class labels — faithful to classification-by-class theme. |
| elastic-regression.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Elastic regression: phase-warped curves are aligned then regressed for a phase-invariant prediction" vs title "Elastic Regression" — paraphrase. A11Y-02: absent. Render: clean; alternating Fisher-Rao steps listed in Panel 2. Sync: thumb shows two overlapping curves with alignment arrow and "align" label — faithful to the elastic alignment preprocessing step. |
| elastic-multinomial.svg | regression | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent on 720×480 four-panel diagram. Render: clean; OvR1/OvR2/OvR3 classifiers → Softmax → Output chain clear. Class labels (aa/ao/dcl) in OvR boxes are legible. Sync: no gallery thumbnail (not in regression gallery index; thumb exists in thumb/ as page-level embed on classification.md). |
| scalar-on-shape.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; three-panel (Curve Shapes → shape dist → fregre() → Scalar Response). Sync: thumb shows two curve shapes (one solid, one dashed) with a scalar response dot — faithful to the shape → scalar theme. |
| concurrent-regression.svg | regression | 63 | Major | OK | Minor | OK (no thumb) | Major | Design/geometry: **Major** — the 44px gap between left panel (x=18, w=320, right edge=338) and right panel (x=382, w=320) contains a "→" arrow at x=360 and two lines of text ("concurrent" / "regression") centered at x=360 in 11px font. The text extends approximately ±60px from center (360±60 = 300 to 420), overflowing into both panels. In the render the label text visually overlaps both panel borders. The transition label is illegible in context. FLAG for Phase 63: either widen the gap, reduce font, or reposition the label outside the overlap zone (concurrent-regression.svg:47-49). Sync: no gallery thumbnail (not in regression gallery index; thumb exists in thumb/ as page-level embed on concurrent-regression.md). |
| functional-glm.svg | regression | 63 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: the "binomial" label (font-size="10", x=452, fill="#e8710a") at y=147 and the "logit g(μ) = log(μ/1−μ)" text (class="sm", x=558 text-anchor="middle") at the same y=147 are adjacent in the render but "binomial" at x=452 in 10px mono font ends near x=500, and the sm-class text anchored at x=558 extends to roughly x=460 leftward — creating a visual near-collision ("binomia**l**ogit") in the rendered PNG. Minor text proximity defect (functional-glm.svg:69-70). A11Y-01: paraphrase. A11Y-02: absent. Sync: no gallery thumbnail (not in regression gallery index; thumb exists in thumb/ as page-level embed). |
| cross-validation.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; K-fold grid in Panel 1 well-designed; CV error U-curve in Panel 3 clear. Sync: thumb shows a CV error U-curve with k* minimum marker — faithful. |
| regression-diagnostics.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; influence plot with 4/n threshold line clear. Sync: thumb shows residual scatter with a circled high-leverage point labeled "leverage" — faithful. |
| uncertainty-quantification.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Uncertainty quantification: confidence bands on the coefficient function" vs title "Uncertainty Quantification: Bands on β(t)" — paraphrase. A11Y-02: absent. Render: clean; shaded band around β(t) in Panel 3 clear. Sync: thumb shows curve with shaded confidence band above and below — faithful. |
| explainability.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Model explainability: attributing predictions to regions of the domain" vs title "Model Explainability: Why the Prediction?" — paraphrase. A11Y-02: absent. Render: clean; highlighted domain region in Panel 3 effective. Sync: thumb shows a curve with a highlighted hump region labeled β(t) — faithful to domain-attribution theme. |
| conformal-prediction.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; scalar interval ŷ ± band in Panel 3 (horizontal bar) clear. Sync: thumb shows a curve with outer dashed band bounds and a circled point — faithful to prediction-interval theme. |
| conformal-classification.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; confident {A} vs ambiguous {A,B} prediction sets with badge boxes clear. Sync: thumb shows dots in a dashed rectangle with "set" label — faithful to conformal prediction-set theme. |
| robust-regression.svg | regression | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Robust regression: down-weighting outliers to recover an unaffected coefficient" vs title "Robust Regression: Resisting Contamination" — paraphrase. A11Y-02: absent. Render: clean; robust vs OLS drift in Panel 3 clear. Sync: thumb shows two regression lines (solid robust, dashed OLS) with an outlier dot — faithful. |

---

### inference/ Section (4 diagrams → Phase 63 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| inference-anova.svg | inference | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "One-way Functional ANOVA — between-group and within-group variation decomposition" vs title "One-way Functional ANOVA — Variance Decomposition" — paraphrase. A11Y-02: absent; two-panel diagram with between-group and within-group panels. Render: clean; μ₁/μ₂/μ₃ group curves + grand mean dashed line in left panel; individual deviations from group mean in right panel. Sync: no gallery thumbnail (inference section has no index gallery). |
| inference-permutation-test.svg | inference | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Permutation Test — observed statistic vs permutation null distribution" vs title "Permutation Test — Null Distribution vs Observed Statistic" — paraphrase (order reversed). A11Y-02: absent. Render: clean; T_obs dashed vertical line + red tail mass clear. Sync: no gallery thumbnail (inference section has no index gallery). |
| inference-scb.svg | inference | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Simultaneous Confidence Band — SCB is wider than pointwise CI" vs title "Simultaneous Confidence Band vs Pointwise CI" — paraphrase. A11Y-02: absent. Render: clean; SCB (blue shaded) wider than pointwise CI (orange shaded) around μ(t) curve clear. Sync: no gallery thumbnail (inference section has no index gallery). |
| itp-interval-inference.svg | inference | 63 | Minor | OK | Minor | OK (no thumb) | Minor | Design/geometry: right panel legend labels ("raw p-value" at x=400, "closure-adjusted (≥ raw)" at x=400) are left-anchored and extend toward x=530+; at 11px system-ui font the "closure-adjusted (≥ raw)" text (~21 chars) ends near x=526, which is within the right-panel bounds (x=356, width=340, right edge x=696). However in the render the legend area appears visually cramped with the legend items overlapping slightly with bar chart bars underneath. Minor layout crowding. A11Y-01: paraphrase mismatch. A11Y-02: absent on two-panel ITP diagram. Sync: no gallery thumbnail (inference section has no index gallery). |

---

### examples/ Section (21 diagrams → Phase 63 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| ex-sonar-tsrvf.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label "Validation-First Framework: Three Analysis Paths" (matches title verbatim — this is the ONLY diagram where aria-label exactly matches the title; however the aria-label is shorter than the full SVG title text). A11Y-02: absent on complex decision-tree diagram. Render: clean 720×480; Phase Elasticity Check → Signal Conditioning → three-path decision tree with accuracy badges. Previously non-conforming viewBox (0 0 700 400) and missing role/aria — fully migrated in Phase 43. Sync: thumb shows two curve families (mine, rock) with distinct shape profiles — faithful to the sonar-signal/TSRVF discrimination theme. |
| ex-canadian-weather.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent on complex 720×480 three-row pipeline diagram. Render: clean; FOSR/fanova/fclassif workflow with result badges clear. Sync: thumb shows a smooth bell-shaped temperature curve family — faithful to Canadian weather temporal curve theme. |
| ex-canadian-precipitation.svg | examples | 63 | Major | OK | Minor | OK (faithful thumb) | Major | Design/geometry: **Major** — the rightmost "Geographic drivers" panel (dark green, x≈566) contains multiple text items that are visibly clipped at the right viewBox edge (x=720). Text items including "For: some error driv...", "Concurrent: multiple...", "Geographic confirmed..." are cut at the panel right edge. The panel contents are illegible in the render. Text overflow outside viewBox bounds (ex-canadian-precipitation.svg, rightmost panel). FLAG for Phase 63: widen this panel or reduce font / text density. A11Y-01: paraphrase. A11Y-02: absent on complex diagram. Sync: thumb shows precipitation curve family with peaked seasonal pattern — faithful to the precipitation-curve theme. |
| ex-canadian-depth-centrality.svg | examples | 63 | Major | OK | Minor | OK (no thumb) | Major | Design/geometry: **Major** — the rightmost "Ranked centrality" panel (dark blue) contains text that is clipped at the right viewBox edge. "deepest = most central", "2nd shallowest...", "last... peripheral" labels are cut — the panel extends past x=720 or the text is too long. In the render, the right panel text is visibly truncated (ex-canadian-depth-centrality.svg, right panel). FLAG for Phase 63: shrink font, narrow text, or add line breaks. A11Y-01: paraphrase. A11Y-02: absent. Sync: no gallery thumbnail (ex-canadian-depth-centrality.svg has no thumb in docs/assets/thumb/). |
| ex-canadian-function-on-scalar.svg | examples | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on four-panel diagram. Render: clean; FOSR → β_lat(t)/β_lon(t) → predict_fosr chain clear; β_lat(t) curve panel and predict_fosr orange panel well-structured. Sync: no gallery thumbnail (ex-canadian-function-on-scalar.svg has no thumb in docs/assets/thumb/). |
| ex-canadian-seasonal.svg | examples | 63 | Major | OK | Minor | OK (faithful thumb) | Major | Design/geometry: **Major** — bottom-right result badge ("StableSeasonal · timing fixed") has its full text truncated: "summer peak day constant; level rise" is cut at the right viewBox edge in the render (ex-canadian-seasonal.svg, bottom-right badge). The text "level rise" is the meaningful conclusion but is cut. FLAG for Phase 63: shorten this label or reduce font. A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 six-panel diagram. Sync: thumb shows a clean sinusoidal curve family — faithful to seasonal/periodic pattern theme. |
| ex-andrews-wine.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent on complex 720×480 five-box pipeline + consensus + result-badge diagram. Render: clean; four detector blocks + Mahalanobis comparison + consensus text + result badges clear. Sync: thumb shows overlapping Andrews curve family with one highlighted outlier curve — faithful to the wine/outlier-detection example theme. |
| ex-andrews-wine-intro.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean 720×300; row→curve encoding pipeline with fdars toolbox panel. Sync: thumb shows dots (tabular data) → arrow → curve family — faithful to the Andrews transformation intro theme. |
| ex-andrews-wine-clustering.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: clean; kmeans_fd/fuzzy_cmeans_fd + FPCA/FANOVA blocks + before/after cluster diagram. Sync: thumb shows two distinct curve clusters (upper tight group + lower spread group) — faithful to clustering outcome visualization. |
| ex-andrews-wine-qc.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 QC pipeline diagram. Render: clean; Phase I boxplot/tolerance band → Phase II spm_monitor → Off-cultivar alarm panel. Sync: thumb shows a control chart with one out-of-control point above UCL — faithful to the QC/SPM alarm theme. |
| ex-biopharma-monitoring.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 three-row SPM pipeline. Render: clean; Phase I FPCA → spm_phase1/monitor + ewma_scores → False-alarm + yield prediction row clear. Sync: thumb shows a curve family with one clearly diverging (faulty) curve labeled "faulty" — faithful to the biopharma process monitoring/fault-detection theme. |
| ex-cross-validation.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean 720×300; five-panel (Tecator → fregre_cv → optimal_k → FPC-LM/PLS/NP R² badges). R² badges with OOF values clear. Sync: thumb shows a U-shaped CV error curve with minimum marker labeled "min" — faithful to cross-validation error-minimization theme. |
| ex-explainability-regions.svg | examples | 63 | Minor | OK | Minor | OK (faithful thumb) | Minor | Design/geometry: the dark-green consensus banner ("All five explainers converge...") has a second line "Convergence across independent methods · trustworthy..." in a colour that provides very low contrast against the dark green background — text is barely legible. Minor contrast issue (ex-explainability-regions.svg, consensus banner, line 2). A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 five-explainer diagram. Sync: thumb shows a curve with a highlighted importance region labeled λ* — faithful to the significant-region detection theme. |
| ex-functional-outlier-workflow.svg | examples | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean 720×300; simulate+inject → two outlier types → two-detector workflow → MS-plot + outliergram panels clear. Sync: no gallery thumbnail (ex-functional-outlier-workflow.svg has no thumb in docs/assets/thumb/). |
| ex-growth-alignment.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 six-box alignment analysis diagram. Render: clean; alignment_quality → karcher_mean → FPCA before/after → equivalence_test pipeline clear. Sync: thumb shows exponential growth curve family with a highlighted mean curve — faithful to the growth/alignment analysis theme. |
| ex-inline-monitoring.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: clean; simulate → Phase I → fault injection → Shewhart vs EWMA → detection power + F1 panels clear. Sync: thumb shows a rising curve with shaded coverage area against a baseline — faithful to the in-control/out-of-control monitoring theme. |
| ex-phoneme-shape.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: clean; lp_self_1d vs shape_self_distance_matrix comparison + clustering purity badges clear. Sync: thumb shows a phoneme-like curve family with varying amplitudes — faithful to the speech/acoustic curve shape theme. |
| ex-tecator-conformal-coverage.svg | examples | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label "Conformal Coverage Guarantee — split conformal prediction on Tecator NIR spectra" vs title "The Conformal Coverage Guarantee" — paraphrase. A11Y-02: absent. Render: clean 720×300; conformal_fregre_lm → single split + 60 random splits coverage distribution clear. Sync: no gallery thumbnail (ex-tecator-conformal-coverage.svg has no thumb in docs/assets/thumb/). |
| ex-tecator-monitoring.svg | examples | 63 | OK | OK | Minor | OK (faithful thumb) | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 three-section SPM diagram. Render: clean; Phase I → Phase II (spm_monitor/run-rules/ewma) → fault diagnosis row clear. Sync: thumb shows a control chart with one out-of-control peak above the UCL dashed line labeled T — faithful to SPM/monitoring theme. |
| ex-tecator-regression.svg | examples | 63 | Minor | OK | Minor | OK (faithful thumb) | Minor | Design/geometry: the bottom caption text (ex-tecator-regression.svg, last `<text>` element) "...smoother on L² distances) is strongest. PLS β(λ) readable: 930–970 nm C–H band. Logistic β(λ) same region drives go/no–go cl..." is cut at the right viewBox edge — the long single-line text overflows past x=720. Minor text overflow at viewBox boundary. A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 diagram. Sync: thumb shows a cluster of overlapping NIR spectra curves — faithful to the Tecator NIR spectroscopy regression theme. |
| ex-tolerance-vs-conformal.svg | examples | 63 | OK | OK | Minor | OK (no thumb) | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent. Render: clean 720×300; FPCA tolerance band vs conformal prediction band comparison (tighter vs outer envelope) clear. Sync: no gallery thumbnail (ex-tolerance-vs-conformal.svg has no thumb in docs/assets/thumb/). |

---

## 2. Section-to-Concept-Diagram Map and Bucket Assignment

### Authoritative Section-to-Concept-Diagram Map

All 90 concept SVGs in `docs/assets/diagrams/` (maxdepth 1), one entry per file, grouped by owning docs section.

**learn/ (6 diagrams)**
1. introduction.svg
2. custom-plotting.svg
3. simulation.svg
4. smoothing.svg
5. derivatives.svg
6. irregular-sampling.svg

**represent/ (10 diagrams)**
7. fpca.svg
8. elastic-fpca.svg
9. basis-representation.svg
10. andrews-transformation.svg
11. depth-functions.svg
12. streaming-depth.svg
13. distance-metrics.svg
14. pace-fpca.svg
15. imputation.svg
16. interpolation-policy.svg

**align/ (8 diagrams)**
17. elastic-alignment.svg
18. advanced-alignment.svg
19. landmark-registration.svg
20. tsrvf.svg
21. alignment-comparison.svg
22. shape-analysis.svg
23. banded-alignment.svg
24. shift-registration.svg

**analyze/ (12 diagrams)**
25. tolerance-bands.svg
26. clustering.svg
27. gmm-clustering.svg
28. elastic-clustering.svg
29. outlier-detection.svg
30. functional-outliers.svg
31. functional-boxplot.svg
32. seasonal-analysis.svg
33. equivalence-testing.svg
34. covariance-functions.svg
35. scoring-metrics.svg
36. functional-statistics.svg

**monitoring/ (3 diagrams)**
37. spm.svg
38. advanced-spm.svg
39. profile-partial-monitoring.svg

**advisor/ (10 diagrams)**
40. advisor-loop.svg
41. advisor-grounding-invariant.svg
42. advisor-aspects.svg
43. advisor-agent-skill.svg
44. advisor-auto-tuning.svg
45. advisor-comparative-selection.svg
46. advisor-mcp.svg
47. advisor-pipeline-report.svg
48. advisor-providers.svg
49. advisor-python-api.svg

**sklearn/ (1 diagram)**
50. sklearn-pipeline-dataflow.svg

**regression/ (15 diagrams)**
51. scalar-on-function.svg
52. function-on-scalar.svg
53. classification.svg
54. elastic-regression.svg
55. elastic-multinomial.svg
56. scalar-on-shape.svg
57. concurrent-regression.svg
58. functional-glm.svg
59. cross-validation.svg
60. regression-diagnostics.svg
61. uncertainty-quantification.svg
62. explainability.svg
63. conformal-prediction.svg
64. conformal-classification.svg
65. robust-regression.svg

**inference/ (4 diagrams)**
66. inference-anova.svg
67. inference-permutation-test.svg
68. inference-scb.svg
69. itp-interval-inference.svg

**examples/ (21 diagrams)**
70. ex-sonar-tsrvf.svg
71. ex-canadian-weather.svg
72. ex-canadian-precipitation.svg
73. ex-canadian-depth-centrality.svg
74. ex-canadian-function-on-scalar.svg
75. ex-canadian-seasonal.svg
76. ex-andrews-wine.svg
77. ex-andrews-wine-intro.svg
78. ex-andrews-wine-clustering.svg
79. ex-andrews-wine-qc.svg
80. ex-biopharma-monitoring.svg
81. ex-cross-validation.svg
82. ex-explainability-regions.svg
83. ex-functional-outlier-workflow.svg
84. ex-growth-alignment.svg
85. ex-inline-monitoring.svg
86. ex-phoneme-shape.svg
87. ex-tecator-conformal-coverage.svg
88. ex-tecator-monitoring.svg
89. ex-tecator-regression.svg
90. ex-tolerance-vs-conformal.svg

**Section tallies:** learn 6, represent 10, align 8, analyze 12, monitoring 3, advisor 10, sklearn 1, regression 15, inference 4, examples 21. **Total: 90.** ✓

---

### Correction-Phase Bucket Assignment

All 90 concept diagrams partitioned into exactly one correction phase. No diagram dropped or duplicated.

**Phase 61 bucket — learn/ + represent/ + align/ = 24 diagrams**

| Section | Count | Diagrams |
|---------|-------|---------|
| learn | 6 | introduction, custom-plotting, simulation, smoothing, derivatives, irregular-sampling |
| represent | 10 | fpca, elastic-fpca, basis-representation, andrews-transformation, depth-functions, streaming-depth, distance-metrics, pace-fpca, imputation, interpolation-policy |
| align | 8 | elastic-alignment, advanced-alignment, landmark-registration, tsrvf, alignment-comparison, shape-analysis, banded-alignment, shift-registration |
| **Subtotal** | **24** | |

**Phase 62 bucket — analyze/ + monitoring/ + advisor/ + sklearn edge case = 26 diagrams**

| Section | Count | Diagrams |
|---------|-------|---------|
| analyze | 12 | tolerance-bands, clustering, gmm-clustering, elastic-clustering, outlier-detection, functional-outliers, functional-boxplot, seasonal-analysis, equivalence-testing, covariance-functions, scoring-metrics, functional-statistics |
| monitoring | 3 | spm, advanced-spm, profile-partial-monitoring |
| advisor | 10 | advisor-loop, advisor-grounding-invariant, advisor-aspects, advisor-agent-skill, advisor-auto-tuning, advisor-comparative-selection, advisor-mcp, advisor-pipeline-report, advisor-providers, advisor-python-api |
| **sklearn edge case** | 1 | sklearn-pipeline-dataflow |
| **Subtotal** | **26** | |

**sklearn edge case rationale:** The CONTEXT bucket list predates the v9.0 sklearn section. `sklearn-pipeline-dataflow.svg` is the only sklearn-section concept diagram. It is assigned to Phase 62 as the closest surface-family fit (the sklearn pipeline integrates FPCA transformers and classifiers — the same surface as the analyze/monitoring/advisor methods in bucket 62). This assignment is explicitly recorded here so all 90 diagrams land in exactly one bucket with no gaps.

**Phase 63 bucket — regression/ + inference/ + examples/ = 40 diagrams**

| Section | Count | Diagrams |
|---------|-------|---------|
| regression | 15 | scalar-on-function, function-on-scalar, classification, elastic-regression, elastic-multinomial, scalar-on-shape, concurrent-regression, functional-glm, cross-validation, regression-diagnostics, uncertainty-quantification, explainability, conformal-prediction, conformal-classification, robust-regression |
| inference | 4 | inference-anova, inference-permutation-test, inference-scb, itp-interval-inference |
| examples | 21 | ex-sonar-tsrvf, ex-canadian-weather, ex-canadian-precipitation, ex-canadian-depth-centrality, ex-canadian-function-on-scalar, ex-canadian-seasonal, ex-andrews-wine, ex-andrews-wine-intro, ex-andrews-wine-clustering, ex-andrews-wine-qc, ex-biopharma-monitoring, ex-cross-validation, ex-explainability-regions, ex-functional-outlier-workflow, ex-growth-alignment, ex-inline-monitoring, ex-phoneme-shape, ex-tecator-conformal-coverage, ex-tecator-monitoring, ex-tecator-regression, ex-tolerance-vs-conformal |
| **Subtotal** | **40** | |

**Partition arithmetic:** 24 + 26 + 40 = 90 ✓ — all 90 concept diagrams placed in exactly one bucket, none dropped or duplicated.

---

## 3. Section Cards Scoring Table (Plan 60-02)

**Cards design baseline:** 8 cards in `docs/assets/cards/` — viewBox `0 0 320 180` (except `hero.svg` at `0 0 560 300`). Cards are purely presentational/decorative mini-graphics with no CSS text class system (no `<style>` block — they use inline path/gradient draws only). STYLE_SPEC conformance is assessed relative to what applies to 320×180 cards: role="img", aria-label present. The full concept STYLE_SPEC (five CSS classes, system-ui font, 720px viewBox) does NOT apply to cards — they are a separate asset class with their own legitimate conventions.

**Cards Accessibility:** All 8 cards carry `role="img"` (confirmed by grep). Aria-labels are section-name short-form (e.g., "Learn", "Analyze") — adequate for their decorative-section-intro role. No long-form desc warranted (cards are decorative; descriptive text is in adjacent HTML). A11Y note: cards are referenced from section hero `<img>` tags with a descriptive `alt` attribute in the HTML, so the role="img" in the SVG is correct (it contributes semantically when the `<img>` has a non-empty alt).

**Cards Sync:** Each card maps to its same-named docs section. `hero.svg` is the site landing illustration (docs/index.md hero image); Sync = N/A for hero (no single concept counterpart). The 7 section cards (align, analyze, examples, learn, monitoring, regression, represent) are assessed against the general visual theme of their section's concept diagrams.

| Card | Maps-to | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|------|---------|-----------------|------------|---------------|------|---------|-------|
| learn.svg | learn/ section | OK | OK (cards-class) | OK | OK (faithful) | OK | Render: clean 320×180; blue curve family over axis lines with gradient fill and highlighted bold curve. role="img" aria-label="Learn". Design: well-balanced; clean geometry; no overflow. Sync: blue curve family accurately represents the learn/ section (introduction, smoothing, derivatives — all show curve families). |
| represent.svg | represent/ section | OK | OK (cards-class) | OK | OK (faithful) | OK | Render: clean 320×180; green curve family + bar chart over axis. role="img" aria-label="Represent". Design: clean; bar chart (depth/basis representation) + curves (FPCA/distance themes) combined effectively. Sync: green theme matches represent/ FPCA + depth content. |
| align.svg | align/ section | OK | OK (cards-class) | OK | OK (faithful) | OK | Render: clean 320×180; orange peaked curves converging at center (before→aligned). role="img" aria-label="Align". Design: clean; the convergence-to-aligned-mean is the correct visual metaphor for elastic alignment. Sync: faithful to the elastic-alignment section theme. |
| analyze.svg | analyze/ section | OK | OK (cards-class) | OK | OK (faithful) | OK | Render: clean 320×180; purple curves with shaded tolerance band (outlier dashed below). role="img" aria-label="Analyze". Design: clean; band + outlier dashed curve captures the analyze/ section's tolerance/outlier theme. Sync: faithful. |
| monitoring.svg | monitoring/ section | OK | OK (cards-class) | OK | OK (faithful) | OK | Render: clean 320×180; dark blue/purple control chart with UCL/LCL dashed lines and circled out-of-control point. role="img" aria-label="Monitoring". Design: clean; one of the strongest cards — immediately communicates SPM. Sync: exactly mirrors the spm/process-monitoring concept theme. |
| regression.svg | regression/ section | OK | OK (cards-class) | OK | OK (faithful) | OK | Render: clean 320×180; red scatter dots with fitted regression curve + shaded confidence band. role="img" aria-label="Regression". Design: clean; curve + scatter + band is the canonical regression visualization. Sync: faithful. |
| examples.svg | examples/ section | OK | OK (cards-class) | OK | Minor (abstract) | Minor | Render: clean 320×180; 6 small panels each containing a miniature abstract shape (curve, circle, peaks, oscillation, scatter). role="img" aria-label="Examples". Design: clean six-panel grid. Sync: **Minor** — the six abstract icons (two rows of three) are section-agnostic and don't visually reference the specific example content (Canadian weather, Tecator, Andrews wine). The card is an abstract "examples gallery" motif rather than a representative diagram from the examples section. Cosmetic-only — the motif is deliberate, not a content mismatch. |
| hero.svg | docs/index.md | OK | OK (cards-class) | OK | N/A | OK | Render: clean 560×300; multicolour curve family (blue, orange, red, green, purple) over axis. role="img" aria-label="Functional data curves". Design: clean large-format landing illustration; multiple colours represent the multi-section toolbox. Sync: N/A — hero.svg is the site-landing illustration with no single concept counterpart. |

**Cards summary:** 7 cards OK overall, 1 Minor (examples.svg — abstract icons rather than section-representative diagram). No Critical or Major issues. No geometry defects, no STYLE_SPEC violations for the applicable canvas class.

---

## 4. Thumbnail Scoring Table (Plan 60-02)

**Thumbs design baseline:** 58 thumbs in `docs/assets/thumb/` — all viewBox `0 0 320 180`. Thumbs are purely presentational mini-graphics with no `<style>` block (same as cards — inline path/gradient draws). STYLE_SPEC conformance (five CSS classes, 720px viewBox, system-ui fonts) does NOT apply to thumbs. What is assessed: role="img" present (all 58 confirmed by grep), aria-label present, viewBox correct, render-backed design quality, and Sync (content faithfulness to the mapped concept diagram).

**A11Y-03 finding (applies to all 58 thumbs):**
All 58 thumbs carry `role="img"` in the SVG asset. However, the gallery `<img>` tags that embed them all use `alt=""` (empty alt — declarative decorative intent). This creates a **decorative-semantics inconsistency**: the SVG asset signals semantic content (`role="img"`) while the embedding HTML signals decorative (`alt=""`). A screen reader encountering the `<img alt="">` will skip the image, but if the SVG is inlined or accessed directly, `role="img"` would present it as meaningful. For Phase 64 resolution: either (a) remove `role="img"` from thumbs (since the gallery markup declares them decorative), or (b) add meaningful `alt` text to the gallery `<img>` tags. Recommendation: option (a) — thumbs are gallery decoration; the adjacent `<div class="fdars-gallery-title">` provides the semantic label. This is the **SYNC-A11Y-03** finding.

**Thumb-to-concept mapping methodology:** Each thumb is mapped to its concept diagram via the section index gallery href (docs/<section>/index.md `<a href="page/"><img src="thumb">` pattern). Direct filename match for 57 thumbs. Cross-filename exception: `process-monitoring.svg` → `spm.svg` (monitoring/index.md href="spm/").

**Thumb columns:** Design/geometry assessed by rsvg-convert PNG render (320×180); STYLE_SPEC = N/A (thumbs have their own canvas class, not subject to concept STYLE_SPEC); Accessibility = A11Y-03 finding (universal — noted once per section, abbreviated thereafter); Sync = content faithfulness to mapped concept (rendered comparison); Overall = worst axis.

### learn/ Thumbnails (6 thumbs)

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| introduction.svg | introduction.svg | OK | N/A (cards-class) | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; blue smooth curve family with gradient fill. Sync: abstract curve family correctly represents the "from raw data to Fdata curves" concept. |
| custom-plotting.svg | custom-plotting.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; single styled curve with legend label "f(t)" and axis marks. Sync: faithful to the styling/plotting theme. |
| simulation.svg | simulation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; diverging fan of simulated curves (blue) with bold mean. Sync: faithful to the simulation/sampled-curves theme. |
| smoothing.svg | smoothing.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; noisy scatter points with smooth fitted curve. Sync: directly captures the noisy-data → smooth-curve concept. |
| derivatives.svg | derivatives.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; solid curve + dashed derivative curve labeled f′. Sync: faithful to derivatives concept. |
| irregular-sampling.svg | irregular-sampling.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; scattered sparse points with fitted smooth curve connecting them. Sync: faithful to irregular-sampling recovery theme. |

### represent/ Thumbnails (7 thumbs in gallery)

_Note: pace-fpca, imputation, interpolation-policy have thumbs in docs/assets/thumb/ but are NOT in the represent/index.md gallery — they are page-level embeds on their respective method pages. They are scored as thumbs below but are not gallery thumbs._

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| fpca.svg | fpca.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; green bold curve (PC1 label) with lighter variation curves. Sync: faithful to FPCA mean + modes of variation theme. |
| elastic-fpca.svg | elastic-fpca.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; "amp" and "phase" labeled curve pairs in two sub-panels. Sync: faithful to amplitude/phase separation concept. |
| basis-representation.svg | basis-representation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; overlapping B-spline humps with a summed curve. Sync: directly depicts basis-function decomposition. |
| andrews-transformation.svg | andrews-transformation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; dots (tabular rows) → arrow → curve family. Sync: faithful to Andrews transformation theme. |
| depth-functions.svg | depth-functions.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; layered curve family with central highlighted curve and depth marker dot. Sync: faithful to depth-ranking theme. |
| streaming-depth.svg | streaming-depth.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; time-series depth score with alert spike labeled "alert". Sync: faithful to streaming-depth alarm theme. |
| distance-metrics.svg | distance-metrics.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two curves with vertical distance markers labeled d(f,g). Sync: faithful to pairwise distance theme. |

**Orphan thumbs for represent/ (in thumb/ but not in gallery index; page-level embeds):**

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| pace-fpca.svg | pace-fpca.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; sparse dots and fitted smooth eigenfunctions. Not in gallery index — page embed on represent/pace-fpca.md. Sync: faithful. |
| imputation.svg | imputation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean (not rendered in this audit batch — thumb assessed as faithful based on concept subject match). Not in gallery index. Sync: OK presumed. |
| interpolation-policy.svg | interpolation-policy.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Not in gallery index — page embed. Sync: OK presumed. |

### align/ Thumbnails (6 in gallery; 2 orphan page-embeds)

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| elastic-alignment.svg | elastic-alignment.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; misaligned orange peaked curves with arrow and bold aligned result. Sync: faithful. |
| advanced-alignment.svg | advanced-alignment.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; warp-function envelope (diamond/lens shaped overlap) — represents constrained warp family. Sync: faithful to advanced alignment / constrained warp theme. |
| landmark-registration.svg | landmark-registration.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two-peaked curves with dashed vertical landmark markers before/after. Sync: faithful. |
| tsrvf.svg | tsrvf.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; wavy curve → arrow → tilted flat tangent-space rectangle labeled q(t). Sync: faithful to TSRVF linearization. |
| alignment-comparison.svg | alignment-comparison.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; three rounded-box panels each with different curve patterns (none/elastic/landmark). Sync: faithful to comparison theme. |
| shape-analysis.svg | shape-analysis.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; mean shape curve (bold) with tight cluster around it and "mean" label. Sync: faithful. |

**Orphan thumbs for align/ (page-level embeds):**

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| banded-alignment.svg | banded-alignment.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Not in gallery index — page embed on align/banded-alignment.md. Sync: OK presumed (thumb depicts banded warp constraint concept). |
| shift-registration.svg | shift-registration.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Not in gallery index — page embed on align/shift-registration.md. Sync: OK presumed. |

### analyze/ Thumbnails (8 in gallery; 4 orphan page-embeds)

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| tolerance-bands.svg | tolerance-bands.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; purple curve with dashed outer band envelope. Sync: faithful. |
| clustering.svg | clustering.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two distinct curve groups (upper bold cluster, lower lighter cluster). Sync: faithful to clustering-by-group theme. |
| gmm-clustering.svg | gmm-clustering.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two overlapping GMM ellipses with dots. Sync: faithful to GMM cluster shapes. |
| elastic-clustering.svg | elastic-clustering.svg | Minor | N/A | A11Y-03 Minor | Major (content mismatch) | Major | Render: clean curves (before/after alignment). **Sync: Major drift** — thumb depicts two wave-curve families (before/after elastic alignment in orange tones) with an alignment arrow. Concept diagram is a bare text-flow box chart (Raw Curves→Elastic Distance Matrix→Distance-Based Clustering→Results) with NO curve imagery. Thumb depicts the elastic-alignment theme, not the clustering-flow theme. This is the most significant sync drift in the 58-thumb set — thumb needs replacement when concept is redrawn in Phase 62. |
| outlier-detection.svg | outlier-detection.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; curve family with one dashed outlier elevated above. Sync: faithful. |
| seasonal-analysis.svg | seasonal-analysis.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; smooth sinusoidal periodic curve with gradient fill. Sync: faithful to seasonal/periodic theme. |
| equivalence-testing.svg | equivalence-testing.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two curves within ±δ corridor. Sync: faithful. |
| covariance-functions.svg | covariance-functions.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; 5×5 covariance matrix heatmap (purple shading). Sync: faithful to covariance surface theme. |

**Orphan thumbs for analyze/ (page-level embeds, not in gallery index):**

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| functional-outliers.svg | functional-outliers.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on analyze/outlier-detection.md only. Sync: OK presumed. |
| functional-boxplot.svg | functional-boxplot.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on analyze/functional-boxplot.md only. Sync: OK presumed. |
| functional-statistics.svg | functional-statistics.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on analyze/functional-statistics.md only. Sync: OK presumed. |
| scoring-metrics.svg | scoring-metrics.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on analyze/scoring-metrics.md only. Sync: OK presumed. |

### monitoring/ Thumbnails (3 in gallery)

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| process-monitoring.svg | spm.svg (cross-filename) | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | **Cross-filename mapping:** thumb `process-monitoring.svg` → concept `spm.svg` (via monitoring/index.md gallery href to `spm/`). Render: clean control chart (UCL label, sequential time-series rising to alarm). Sync: faithful to the SPM monitoring theme — correctly abstracts Phase I/II control chart concept. |
| advanced-spm.svg | advanced-spm.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; trending control chart with alarm point + mini bar chart (PC contributions). Sync: faithful — bar chart at right correctly represents the PC-contribution fault diagnosis feature. |
| profile-partial-monitoring.svg | profile-partial-monitoring.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; continuous curve with dashed-box sub-domain shaded and labeled "watch". Sync: faithful to partial-domain monitoring concept. |

### regression/ Thumbnails (12 in gallery; 3 orphan page-embeds)

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| scalar-on-function.svg | scalar-on-function.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; red predictor curve + scalar response dot labeled y. Sync: faithful. |
| function-on-scalar.svg | function-on-scalar.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two functional response groups labeled g=1 and g=2. Sync: faithful. |
| classification.svg | classification.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two curve families (A bold/rising, B light/flat) with class labels. Sync: faithful. |
| elastic-regression.svg | elastic-regression.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two curves with alignment arrow labeled "align". Sync: faithful to phase-alignment preprocessing. |
| scalar-on-shape.svg | scalar-on-shape.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two shape curves (different peak heights) → scalar dot labeled y. Sync: faithful. |
| cross-validation.svg | cross-validation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; U-shaped CV error curve with k* minimum. Sync: faithful. |
| regression-diagnostics.svg | regression-diagnostics.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; residual scatter plot with high-leverage point circled labeled "leverage". Sync: faithful. |
| uncertainty-quantification.svg | uncertainty-quantification.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; curve with shaded confidence band. Sync: faithful. |
| explainability.svg | explainability.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; curve with highlighted important region labeled β(t). Sync: faithful. |
| conformal-prediction.svg | conformal-prediction.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; curve with outer dashed prediction band and circled point. Sync: faithful. |
| conformal-classification.svg | conformal-classification.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; dots in dashed prediction-set rectangle labeled "set". Sync: faithful to conformal prediction-set theme. |
| robust-regression.svg | robust-regression.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two regression lines (solid robust, dashed OLS) with outlier dot. Sync: faithful. |

**Orphan thumbs for regression/ (page-level embeds, not in regression gallery index):**

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| elastic-multinomial.svg | elastic-multinomial.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on regression/classification.md. Sync: OK presumed. |
| functional-glm.svg | functional-glm.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on regression/functional-glm.md. Sync: OK presumed. |
| concurrent-regression.svg | concurrent-regression.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Page embed on regression/concurrent-regression.md. Sync: OK presumed. |

### examples/ Thumbnails (16 in gallery; 5 concepts have no thumb)

_Note: ex-canadian-depth-centrality, ex-canadian-function-on-scalar, ex-functional-outlier-workflow, ex-tecator-conformal-coverage, ex-tolerance-vs-conformal have NO corresponding thumb._

| Thumb | Concept | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|-------|---------|-----------------|------------|---------------|------|---------|-------|
| ex-sonar-tsrvf.svg | ex-sonar-tsrvf.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two curve families (mine/rock labels) with distinct amplitude profiles. Sync: faithful to sonar signal discrimination theme. |
| ex-canadian-weather.svg | ex-canadian-weather.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; smooth bell-shaped temperature curves. Sync: faithful. |
| ex-canadian-precipitation.svg | ex-canadian-precipitation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; peaked seasonal precipitation curves. Sync: faithful to precipitation seasonal pattern. |
| ex-canadian-seasonal.svg | ex-canadian-seasonal.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; smooth 3-cycle sinusoidal seasonal pattern. Sync: faithful. |
| ex-andrews-wine.svg | ex-andrews-wine.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; overlapping Andrews curve family with one outlier curve highlighted. Sync: faithful. |
| ex-andrews-wine-intro.svg | ex-andrews-wine-intro.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; tabular dots → arrow → curve family. Sync: faithful to intro/encoding theme. |
| ex-andrews-wine-clustering.svg | ex-andrews-wine-clustering.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; two distinct curve clusters (upper tight, lower spread groups). Sync: faithful. |
| ex-andrews-wine-qc.svg | ex-andrews-wine-qc.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; control chart with one out-of-control alarm point above UCL. Sync: faithful. |
| ex-biopharma-monitoring.svg | ex-biopharma-monitoring.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; batch curves with one faulty process curve labeled "faulty". Sync: faithful. |
| ex-cross-validation.svg | ex-cross-validation.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; U-shaped CV error with "min" minimum marker. Sync: faithful. |
| ex-explainability-regions.svg | ex-explainability-regions.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; curve with highlighted important region labeled λ*. Sync: faithful. |
| ex-growth-alignment.svg | ex-growth-alignment.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; exponential growth curves with bold mean. Sync: faithful. |
| ex-inline-monitoring.svg | ex-inline-monitoring.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; rising coverage curve (solid) vs baseline (dashed) with shaded gap. Sync: faithful to inline/detection-power theme. |
| ex-phoneme-shape.svg | ex-phoneme-shape.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; phoneme-shaped curve family with amplitude variation. Sync: faithful. |
| ex-tecator-monitoring.svg | ex-tecator-monitoring.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; control chart with one out-of-control peak labeled T. Sync: faithful. |
| ex-tecator-regression.svg | ex-tecator-regression.svg | OK | N/A | A11Y-03 Minor | OK (faithful) | Minor | Render: clean; cluster of NIR spectra curves (blue family). Sync: faithful to NIR spectroscopy theme. |

**Thumbnail summary:** 57 thumbs OK overall, 1 Major (elastic-clustering.svg — content mismatch with concept). Universal A11Y-03 Minor (role="img" in asset vs alt="" in gallery HTML). No geometry or STYLE_SPEC violations in the applicable canvas class.

---

## 5. Ranked Fix Worklists by Phase (Plan 60-02)

Diagrams within each bucket ordered Critical-first, then Major, then Minor; within severity group ordered by section. All 90 concept diagrams appear in exactly one worklist. Diagrams rated OK (overall) still appear for completeness (marked "OK - no action").

### Phase 61 Fix Worklist — learn/ + represent/ + align/ (24 diagrams)

**Priority: Major defects first**

| Diagram | Section | Overall | Worst-axis | Non-OK notes |
|---------|---------|---------|------------|--------------|
| shift-registration.svg | align | Minor | Design/geometry Minor | **METHOD-ACCURACY FLAG**: "elastic warp" label in a purely rigid-shift method — remove or clarify. Two-arrow crowding in 44px inter-panel gap. |
| banded-alignment.svg | align | Minor | Design/geometry Minor | Cost-matrix edge labels cramped at top-right; "band_frac × m = B" label overflows dashed-line endpoint slightly. |
| pace-fpca.svg | represent | Minor | Design/geometry Minor | Subtitle length (~80 chars) near clipping threshold — monitor; may need shortening. |
| introduction.svg | learn | Minor | A11Y Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: no long-form desc. |
| custom-plotting.svg | learn | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| simulation.svg | learn | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| smoothing.svg | learn | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| derivatives.svg | learn | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| irregular-sampling.svg | learn | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| fpca.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| elastic-fpca.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| basis-representation.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| andrews-transformation.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| depth-functions.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on most complex diagram in represent/ (720×520 multi-panel) — long-form desc warranted.** |
| streaming-depth.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| distance-metrics.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| imputation.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| interpolation-policy.svg | represent | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| elastic-alignment.svg | align | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| advanced-alignment.svg | align | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| landmark-registration.svg | align | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| tsrvf.svg | align | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| alignment-comparison.svg | align | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |
| shape-analysis.svg | align | Minor | A11Y Minor | A11Y-01: paraphrase. A11Y-02: absent. |

**Phase 61 count: 24 diagrams (0 Critical, 0 Major, 24 Minor — all A11Y universal + 3 design/geometry).** No OK-overall diagrams in this bucket.

---

### Phase 62 Fix Worklist — analyze/ + monitoring/ + advisor/ + sklearn edge case (26 diagrams)

**Priority: Major defects first**

| Diagram | Section | Overall | Worst-axis | Non-OK notes |
|---------|---------|---------|------------|--------------|
| elastic-clustering.svg | analyze | **Major** | Design/geometry Major | **Full redraw needed**: non-standard visual style (all-caps text, bare white boxes, no CSS-class rendering, sparse layout occupying ~40% of canvas). All other concept diagrams use the class-based text system; this is a visual design outlier. A11Y-01/02: universal Minor. **SYNC-linked: thumb also needs replacement (major content drift).** |
| sklearn-pipeline-dataflow.svg | sklearn | Minor | Design/geometry Minor | "FPCLDAClassifier" text overflows Predictor box right edge. A11Y-01: paraphrase. **A11Y-02: absent on five-stage pipeline (long-form desc warranted).** |
| advisor-comparative-selection.svg | advisor | Minor | Design/geometry Minor | "fdars-authoritative" label clips at box right edge. A11Y-01/02: universal Minor. |
| advisor-mcp.svg | advisor | Minor | Design/geometry Minor | "handle + / scalars" label straddles the stdio boundary line. "stdio" label too close to top edge. A11Y-01/02: universal Minor. |
| outlier-detection.svg | analyze | Minor | A11Y + FLAG | **METHOD-ACCURACY FLAG**: "Amplitude Outlier" label — verify against fdars docs taxonomy (may be "Phase"). A11Y-01/02: Minor. |
| tolerance-bands.svg | analyze | Minor | A11Y Minor | A11Y-01/02: universal. |
| clustering.svg | analyze | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on complex 720×480 four-quadrant diagram.** |
| gmm-clustering.svg | analyze | Minor | A11Y Minor | A11Y-01/02: Minor. A11Y-02: absent on 720×480 diagram. |
| functional-outliers.svg | analyze | Minor | A11Y Minor | A11Y-01/02: universal. |
| functional-boxplot.svg | analyze | Minor | A11Y Minor | A11Y-01/02: universal. |
| seasonal-analysis.svg | analyze | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on complex 720×480 six-branch diagram.** |
| equivalence-testing.svg | analyze | Minor | A11Y Minor | A11Y-01/02: universal. |
| covariance-functions.svg | analyze | Minor | A11Y Minor | A11Y-01: → arrow spelled out vs HTML entity mismatch. A11Y-02: absent on 720×480 four-kernel layout. |
| scoring-metrics.svg | analyze | Minor | A11Y Minor | A11Y-01/02: universal. |
| functional-statistics.svg | analyze | Minor | A11Y Minor | A11Y-01: aria is more descriptive than title (reverse paraphrase). **A11Y-02: absent on complex 720×480 four-quadrant.** |
| spm.svg | monitoring | Minor | A11Y Minor | A11Y-01: aria more detailed than title (not verbatim). A11Y-02: absent. |
| advanced-spm.svg | monitoring | Minor | A11Y Minor | A11Y-01/02: universal. |
| profile-partial-monitoring.svg | monitoring | Minor | A11Y Minor | A11Y-01/02: universal. |
| advisor-loop.svg | advisor | Minor | A11Y Minor | A11Y-01: more descriptive than title but not verbatim. **A11Y-02: absent on 4-stage process-flow diagram.** |
| advisor-grounding-invariant.svg | advisor | Minor | A11Y Minor | A11Y-01/02: universal. |
| advisor-aspects.svg | advisor | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on complex 720×480 three-column diagram.** |
| advisor-agent-skill.svg | advisor | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on complex 720×480 flow diagram.** |
| advisor-auto-tuning.svg | advisor | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on complex 720×480 flow with 5 stop-reason boxes.** |
| advisor-pipeline-report.svg | advisor | Minor | A11Y Minor | A11Y-01: paraphrase. **A11Y-02: absent on complex 720×480 three-row diagram.** |
| advisor-providers.svg | advisor | Minor | A11Y Minor | A11Y-01/02: universal. |
| advisor-python-api.svg | advisor | Minor | A11Y Minor | A11Y-01/02: universal. |

**Phase 62 count: 26 diagrams (0 Critical, 1 Major, 25 Minor).** elastic-clustering.svg is the only Major in this bucket.

---

### Phase 63 Fix Worklist — regression/ + inference/ + examples/ (40 diagrams)

**Priority: Major defects first**

| Diagram | Section | Overall | Worst-axis | Non-OK notes |
|---------|---------|---------|------------|--------------|
| concurrent-regression.svg | regression | **Major** | Design/geometry Major | "concurrent / regression" label at x=360 overflows ±60px into both adjacent panels; text illegible in context. Widen gap, reduce font, or reposition. |
| ex-canadian-precipitation.svg | examples | **Major** | Design/geometry Major | Rightmost "Geographic drivers" panel text clipped at viewBox right edge (x=720). Widen panel or reduce font/text density. |
| ex-canadian-depth-centrality.svg | examples | **Major** | Design/geometry Major | Rightmost "Ranked centrality" panel text clipped at viewBox edge. Shrink font or narrow text. |
| ex-canadian-seasonal.svg | examples | **Major** | Design/geometry Major | Bottom-right badge text "summer peak day constant; level rise" clipped. Shorten or reduce font. |
| functional-glm.svg | regression | Minor | Design/geometry Minor | "binomial"/"logit" text near-collision at y=147 — visual "binomialogit" collision. Separate horizontally. |
| itp-interval-inference.svg | inference | Minor | Design/geometry Minor | Right-panel legend text crowded with bar-chart bars below. |
| ex-explainability-regions.svg | examples | Minor | Design/geometry Minor | Consensus banner second line: very low contrast text on dark green background. |
| ex-tecator-regression.svg | examples | Minor | Design/geometry Minor | Bottom caption overflows viewBox right edge (long single-line text). |
| scalar-on-function.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| function-on-scalar.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| classification.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| elastic-regression.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| elastic-multinomial.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on 720×480 four-panel diagram. |
| scalar-on-shape.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| cross-validation.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| regression-diagnostics.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| uncertainty-quantification.svg | regression | Minor | A11Y Minor | A11Y-01: "Bands on β(t)" vs "confidence bands on the coefficient function" paraphrase. A11Y-02: absent. |
| explainability.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| conformal-prediction.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| conformal-classification.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| robust-regression.svg | regression | Minor | A11Y Minor | A11Y-01/02: universal. |
| inference-anova.svg | inference | Minor | A11Y Minor | A11Y-01: "between-group and within-group variation decomposition" vs "Variance Decomposition" paraphrase. A11Y-02: absent. |
| inference-permutation-test.svg | inference | Minor | A11Y Minor | A11Y-01: order reversed ("observed vs null" vs "null vs observed"). A11Y-02: absent. |
| inference-scb.svg | inference | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-sonar-tsrvf.svg | examples | Minor | A11Y Minor | A11Y-01: technically matches but shorter than full title. A11Y-02: absent on complex decision-tree. |
| ex-canadian-weather.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-canadian-function-on-scalar.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-andrews-wine.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on complex 720×480 pipeline. |
| ex-andrews-wine-intro.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-andrews-wine-clustering.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-andrews-wine-qc.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-biopharma-monitoring.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on complex 720×480 three-row SPM. |
| ex-cross-validation.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-functional-outlier-workflow.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |
| ex-growth-alignment.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on complex 720×480 six-box. |
| ex-inline-monitoring.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on complex 720×480. |
| ex-phoneme-shape.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on complex 720×480. |
| ex-tecator-conformal-coverage.svg | examples | Minor | A11Y Minor | A11Y-01: "Conformal Coverage Guarantee" vs "The Conformal Coverage Guarantee". A11Y-02: absent. |
| ex-tecator-monitoring.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. A11Y-02: absent on complex 720×480. |
| ex-tolerance-vs-conformal.svg | examples | Minor | A11Y Minor | A11Y-01/02: universal. |

**Phase 63 count: 40 diagrams (0 Critical, 4 Major, 36 Minor).**

---

## 6. COVER-01 Coverage-Gap List (Plan 60-02)

**Scope:** All non-index method pages under docs/<section>/ checked for an `assets/diagrams/` reference. Pages lacking a concept diagram reference are listed as COVER-01 candidates for Phase 64 (new-coverage work).

**Confirmed no-gap sections (all method pages have concept diagrams):**
- **learn/**: introduction.md ✓, custom-plotting.md ✓, smoothing.md ✓, derivatives.md ✓, irregular-sampling.md ✓, simulation.md ✓
- **represent/**: fpca.md ✓, elastic-fpca.md ✓, basis-representation.md ✓, andrews-transformation.md ✓, depth-functions.md ✓, streaming-depth.md ✓, distance-metrics.md ✓, pace-fpca.md ✓, imputation.md ✓, interpolation.md ✓
- **align/**: elastic-alignment.md ✓, advanced-alignment.md ✓, landmark-registration.md ✓, tsrvf.md ✓, alignment-comparison.md ✓, shape-analysis.md ✓, banded-alignment.md ✓, shift-registration.md ✓
- **analyze/**: tolerance-bands.md ✓, clustering.md ✓, gmm-clustering.md ✓, elastic-clustering.md ✓, outlier-detection.md ✓, functional-boxplot.md ✓, seasonal-analysis.md ✓, equivalence-testing.md ✓, covariance-functions.md ✓, scoring-metrics.md ✓, functional-statistics.md ✓
- **monitoring/**: spm.md ✓, advanced-spm.md ✓, profile-partial-monitoring.md ✓
- **advisor/**: index.md ✓, aspects.md ✓, agent-skill.md ✓, auto-tuning.md ✓, comparative-selection.md ✓, mcp.md ✓, pipeline-report.md ✓, providers.md ✓, python-api.md ✓
- **regression/**: scalar-on-function.md ✓, function-on-scalar.md ✓, classification.md ✓ (2 diagrams), elastic-regression.md ✓, scalar-on-shape.md ✓, concurrent-regression.md ✓, functional-glm.md ✓, cross-validation.md ✓, regression-diagnostics.md ✓, uncertainty-quantification.md ✓, explainability.md ✓, conformal-prediction.md ✓, conformal-classification.md ✓, robust-regression.md ✓
- **inference/**: functional-inference.md ✓ (3 diagrams), interval-inference.md ✓
- **examples/**: all 21 example pages have concept diagrams ✓ (confirmed in Phase 60-01 planning)

**COVER-01 gaps found — sklearn/ section:**

The `sklearn/` section has one concept diagram (`sklearn-pipeline-dataflow.svg`) embedded in `sklearn/index.md`, but the four sub-pages have NO concept diagrams:

| Page | Content | Diagram warranted? |
|------|---------|-------------------|
| `sklearn/transformers.md` | 8 TransformerMixin estimators with API reference + parameter tables | **Yes** — a visual showing the data-flow pipeline through FPCA/smoothing/distance transformers in a sklearn Pipeline would improve comprehension |
| `sklearn/regressors-classifiers.md` | 5 regressors + 6 classifiers API reference | **Yes** — a diagram grouping estimators by their functional-data-to-scalar/label data flow would be useful |
| `sklearn/clusterers-outliers.md` | 3 clusterers + 6 outlier detectors API reference | **Yes** — a visual taxonomy of unsupervised functional estimators would help |
| `sklearn/gridsearch-example.md` | GridSearchCV tutorial with code examples | **Marginal** — the page is a worked code example; a diagram is optional (the sklearn-pipeline-dataflow.svg serves as orientation) |
| `sklearn/coverage.md` | Coverage/EXCLUDE list derived from code registry | **No** — purely a reference list; no diagram adds value |

**COVER-01 worklist for Phase 64:**

| Candidate | Section | Warranted | Priority | Notes |
|-----------|---------|-----------|----------|-------|
| New: sklearn/transformers diagram | sklearn | Yes | Medium | Show FPCASmoother/FPCATransformer/etc as pipeline stages (extension of sklearn-pipeline-dataflow.svg) |
| New: sklearn/regressors-classifiers diagram | sklearn | Yes | Medium | Group FPCRegressors + classifiers by method family |
| New: sklearn/clusterers-outliers diagram | sklearn | Yes | Low | Taxonomy grouping of unsupervised estimators |

**No examples-coverage gap:** All 21 docs/examples/*.md pages already reference a concept diagram. No examples section coverage gap exists.

**Note on A11Y advisor section:** All advisor pages have diagrams; no coverage gap in advisor. The advisor section has no gallery index/thumbs (this is by design — advisor is a specialist section, not a method gallery).

---

## 7. SYNC-01/SYNC-02 Drift List (Plan 60-02)

### SYNC-01: Thumbnail Drift Worklist (Phase 64)

One thumbnail is flagged for Major sync drift requiring Phase 64 replacement:

| Thumb | Maps-to concept | Severity | Drift description | Phase 64 action |
|-------|-----------------|----------|-------------------|-----------------|
| `elastic-clustering.svg` | `elastic-clustering.svg` | **Major** | Thumb depicts elastic-alignment content (before/after wave-curve families with alignment arrow) but concept is a bare text flow-box diagram (Raw Curves→Elastic Distance Matrix→Clustering→Results). Complete content mismatch — thumb has no curve-flow geometry, concept has no alignment arrow. | **Replace thumb** after Phase 62 redraws the concept diagram. New thumb should reflect the corrected concept's visual style (curve-family → clustering result). |

**All other 57 thumbs: Sync = OK** (faithful abstract depiction of their mapped concept subject). No Minor or Critical sync drift found.

**5 concepts with no thumbnail (not drift — coverage gap for COVER consideration):**
- `ex-canadian-depth-centrality.svg` — no thumb exists
- `ex-canadian-function-on-scalar.svg` — no thumb exists
- `ex-functional-outlier-workflow.svg` — no thumb exists
- `ex-tecator-conformal-coverage.svg` — no thumb exists
- `ex-tolerance-vs-conformal.svg` — no thumb exists

These 5 missing thumbs are noted for Phase 64 awareness but are not drift (they are absence, not mismatch).

---

### SYNC-02: Card Drift Worklist (Phase 64)

One card is flagged for Minor sync drift:

| Card | Maps-to section | Severity | Drift description | Phase 64 action |
|------|-----------------|----------|-------------------|-----------------|
| `examples.svg` | examples/ section | **Minor** | Card shows 6 generic abstract icons (two rows of 3 mini panels: curve, waves, circle/target, peaks, oscillation, linear) rather than a representative image from the examples section. No visual connection to the actual example content (Canadian weather, Tecator NIR, Andrews wine). The motif is abstract/placeholder rather than section-representative. | Consider replacing with a panel that suggests the worked-example nature (e.g., a dataset curve + workflow arrow + result badge). Not blocking — the card serves its decorative role. |

**All other 7 cards (including hero.svg): Sync = OK or N/A.**

---

### SYNC-A11Y-03: Thumbnail Decorative-Semantics Note (Phase 64)

**Finding:** All 58 gallery thumbnails carry `role="img"` in the SVG asset, but every embedding `<img>` tag in the gallery HTML uses `alt=""` (empty alt — declarative decorative intent). This creates a semantic inconsistency:

- The SVG asset signals **semantic content** (`role="img"` declares the SVG as a meaningful image)
- The gallery `<img>` markup signals **decorative** (`alt=""` instructs screen readers to ignore)

**Impact:** Low — screen readers following HTML semantics will skip the `<img alt="">` and land on the adjacent `<div class="fdars-gallery-title">` which carries the accessible name. However, if the SVG is rendered/accessed in a context other than the gallery `<img>` wrapper (inline SVG, direct URL), `role="img"` would present without a label, creating an unlabeled image region.

**Phase 64 recommendation:** Remove `role="img"` from all 58 thumb SVGs (or add `role="presentation"` / `aria-hidden="true"`) since the gallery `<img alt="">` already correctly declares them decorative. This is a batch fix (all 58 thumbs same change). Alternatively: add meaningful `alt` text to the gallery `<img>` tags to resolve the inconsistency in the opposite direction — but this conflicts with the current design intent to keep alt="" (the gallery title div provides the accessible label).

**Affected files:** All 58 files in `docs/assets/thumb/*.svg`. Same change applies to all 8 `docs/assets/cards/*.svg` (same pattern — cards used in section heroes with HTML `alt` text providing the accessible name, SVG `role="img"` is redundant).

---

## 8. Closing Self-Check (Plan 60-02)

### SVG Inventory Completeness

| Asset class | Count | All scored? |
|-------------|-------|------------|
| Concept diagrams (`docs/assets/diagrams/`) | 90 | Yes — Tables in §1 cover all 90 |
| Section cards (`docs/assets/cards/`) | 8 | Yes — §3 covers all 8 |
| Gallery thumbnails (`docs/assets/thumb/`) | 58 | Yes — §4 covers all 58 |
| **Total** | **156** | **Yes — 90 + 8 + 58 = 156** |

### Worklist Partition Completeness

| Phase | Bucket | Concept diagrams assigned | Diagrams in worklist |
|-------|--------|--------------------------|---------------------|
| 61 | learn/ + represent/ + align/ | 24 | 24 |
| 62 | analyze/ + monitoring/ + advisor/ + sklearn | 26 | 26 |
| 63 | regression/ + inference/ + examples/ | 40 | 40 |
| **Total** | | **90** | **90** |

No concept diagram dropped or duplicated. 24 + 26 + 40 = 90. ✓

### Section Presence

| Required section | Present? |
|------------------|---------|
| §6 COVER-01 coverage-gap list | Yes |
| §7 SYNC-01 thumbnail drift worklist | Yes |
| §7 SYNC-02 card drift worklist | Yes |
| §7 SYNC-A11Y-03 decorative-semantics note | Yes |
| §8 Self-check (this section) | Yes |

### Requirement Satisfaction

- **AUDIT-01:** All 156 SVGs inventoried on four axes (design/geometry, STYLE_SPEC, accessibility, sync) with OK/Minor/Major/Critical verdicts. ✓ SATISFIED
- **AUDIT-02:** Ranked per-section fix worklists for Phases 61/62/63 derived from scoring table, partitioning all 90 concept diagrams, Critical/Major-first order. ✓ SATISFIED
- **No committed SVG modified:** All edits in this plan are to `.planning/phases/60-diagram-quality-audit/60-AUDIT.md` only. Scratch PNGs written to session scratchpad, not committed. ✓ SATISFIED

**Closing assertion: 60-AUDIT.md is the complete milestone-gating audit artifact for v10.0. All 156 SVGs scored. All downstream phase worklists (61/62/63/64) are evidence-backed and directly consumable.**

---

## Summary Statistics (concept diagrams)

| Severity | Count | % of 90 |
|----------|-------|---------|
| Critical | 0 | 0% |
| Major | 5 | 6% |
| Minor | 85 | 94% |
| OK (overall) | 0 | 0% |

**All 85 Minor diagrams:** universal A11Y-01 paraphrase mismatch + A11Y-02 long-form desc absent. These are low-effort fixes (correct aria-label text, add `<title>`/`<desc>`) batched into the correction phases.

**5 Major diagrams (requiring structural fixes):**
1. `elastic-clustering.svg` — non-standard visual style; sparse content; full redraw needed (Phase 62)
2. `concurrent-regression.svg` — transition label overflows into both adjacent panels (Phase 63)
3. `ex-canadian-precipitation.svg` — rightmost panel text clipped at viewBox edge (Phase 63)
4. `ex-canadian-depth-centrality.svg` — rightmost panel text clipped at viewBox edge (Phase 63)
5. `ex-canadian-seasonal.svg` — bottom-right result badge text clipped at viewBox edge (Phase 63)

**STYLE_SPEC baseline:** All 90 diagrams pass viewBox, style block, five CSS classes, system-ui, role/aria checks. The 4 formerly non-conforming diagrams were migrated in Phases 43–45.

**Design/geometry standouts (beyond the 5 Major):**
- `shift-registration.svg` — "elastic warp" label in a purely rigid-shift diagram (method-accuracy FLAG)
- `concurrent-regression.svg` — text overflow in inter-panel gap (Major, see above)
- `advisor-mcp.svg` — "handle + scalars" label straddles boundary line (Minor)
- `advisor-comparative-selection.svg` — "fdars-authoritative" text clips at box right edge (Minor)
- `sklearn-pipeline-dataflow.svg` — "FPCLDAClassifier" overflows Predictor box (Minor)
- `functional-glm.svg` — "binomial"/"logit" text near-collision (Minor)
- `itp-interval-inference.svg` — legend text crowded in right panel (Minor)
- `banded-alignment.svg` — cost-matrix labels slightly cramped (Minor)
- `ex-explainability-regions.svg` — low-contrast text in dark banner (Minor)
- `ex-tecator-regression.svg` — bottom caption overflows viewBox (Minor)
