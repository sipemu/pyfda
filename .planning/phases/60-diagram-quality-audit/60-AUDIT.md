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

**Sync axis:** All concept rows carry `Deferred-60-02` — drift detection performed in Plan 60-02.

---

### learn/ Section (6 diagrams → Phase 61 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| introduction.svg | learn | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "From raw measurements to a functional-data object" vs title "From Raw Measurements to a Functional-Data Object" — paraphrase mismatch. A11Y-02: no long-form desc; three-panel layout is simple. Render: clean three-panel (scatter→Fdata constructor→curve family). |
| custom-plotting.svg | learn | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Styling a functional sample with matplotlib" vs title "Custom Plotting: Styling a Curve Family" — paraphrase. A11Y-02: no long-form desc; three-panel simple. Render: clean. |
| simulation.svg | learn | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Simulating functional data from Karhunen-Loeve parameters" vs title "Simulation: Synthetic Curves with Known Ground Truth" — paraphrase. A11Y-02: absent; moderate complexity. Render: clean; KL parameters → simulate() → sampled curves. |
| smoothing.svg | learn | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Smoothing a noisy curve into a smooth functional representation" vs title "Smoothing: Recovering the Signal Behind the Noise" — paraphrase (smoothing.svg:1). A11Y-02: absent; three-panel moderate. Render: clean — Panel 3 ghost polyline from v7.0 is resolved; smooth curve output is distinct from noisy input. |
| derivatives.svg | learn | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Differentiating curves into velocity and acceleration" vs title "Derivatives: When and How Fast a Curve Changes" — paraphrase. A11Y-02: absent. Render: clean; velocity/acceleration stacked in Panel 3 is clear. |
| irregular-sampling.svg | learn | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Regridding sparse irregular curves onto a common grid" vs title "Irregular Sampling: Recovering a Common Grid" — paraphrase. A11Y-02: absent. Render: clean; sparse points → smooth → common grid. |

---

### represent/ Section (10 diagrams → Phase 61 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| fpca.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Functional PCA: mean plus modes of variation" vs title "Functional PCA: Mean + Modes of Variation" — paraphrase. A11Y-02: absent; three-panel moderate. Render: clean; green theme; μ(t) + eigenfunctions + score scatter. |
| elastic-fpca.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Elastic FPCA: separating amplitude and phase variation" vs title "Elastic FPCA: Splitting Amplitude from Phase" — paraphrase. A11Y-02: absent. Render: clean; vert_fpca/horiz_fpca/joint_fpca listed; amplitude+phase panel. |
| basis-representation.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Basis representation: project a curve onto basis functions" vs title "Basis Representation: Curve to Coefficients" — paraphrase. A11Y-02: absent. Render: clean; B-spline basis functions in Panel 2 clearly shown. |
| andrews-transformation.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Andrews transformation: from feature tables to curves" vs title "Andrews Transformation: Tables to Curves" — paraphrase. A11Y-02: absent. Render: clean; feature table → Fourier formula → one curve per row. |
| depth-functions.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Functional depth: ranking curves by centrality" (paraphrase). A11Y-02: absent on a complex 720×520 multi-panel diagram — this is the most complex diagram in represent/; should have long-form desc (Major A11Y-02 gap). Render: clean 720×520 multi-panel; depth ranking bar chart + Depth-Based Tools grid clear. Overall upgraded to Minor (A11Y-02 gap on complex diagram). |
| streaming-depth.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Streaming depth: score each new curve against a rolling window" vs title "Streaming Depth: Scoring Against a Rolling Window" — paraphrase. A11Y-02: absent; three-panel. Render: clean; depth-over-time alarm panel clear. |
| distance-metrics.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Distance metrics: curve pairs to a distance matrix" vs title "Distance Metrics: Curves to a Distance Matrix" — paraphrase. A11Y-02: absent. Render: clean; green distance matrix heat-map in Panel 3. |
| pace-fpca.svg | represent | 61 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: PACE FPCA uses a two-panel layout (scatter input left, eigenfunction curves right). Title text "PACE FPCA — Sparse, Irregular Observations to Smooth Eigenfunctions" is 60+ chars; subtitle is ~80 chars — both render acceptably at 720px but subtitle is near the clipping edge. Render shows it renders cleanly; downgraded from v7.0 Major (subtitle overflow resolved). Remains Minor for subtitle length risk. A11Y-01: paraphrase mismatch. A11Y-02: absent. |
| imputation.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Missing-value imputation: three strategies for filling NaN gaps in functional data" vs title "Missing-Value Imputation — Three Strategies" — paraphrase. A11Y-02: absent. Render: clean; linear/mean/constant three panels clear with NaN shading. |
| interpolation-policy.svg | represent | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Spline interpolation and extrapolation policy: four policy variants on a single curve" vs title "Spline Interpolation — Extrapolation Policy" — paraphrase. A11Y-02: absent; four-panel. Render: clean; boundary/exception/fill/periodic policies clearly shown with colored panels. |

---

### align/ Section (8 diagrams → Phase 61 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| elastic-alignment.svg | align | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Elastic alignment: removing phase variation by warping curves..." vs title "Elastic Alignment: Removing Phase to Recover a Sharp Mean" — paraphrase. A11Y-02: absent. Render: clean three-panel; misaligned peaks → karcher_mean() → sharp mean + phase γ(t) inset. The γ(t) inset is small but labeled. |
| advanced-alignment.svg | align | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Advanced alignment: penalized and constrained elastic registration" vs title "Advanced Alignment: Penalized & Constrained Warps" — paraphrase mismatch including "Penalized" → "penalized". A11Y-02: absent. Render: clean; λ colour-swatch in Panel 3 effective. |
| landmark-registration.svg | align | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Landmark registration: warping marked features to common targets" vs title "Landmark Registration: Pinning Features to Targets" — paraphrase. A11Y-02: absent. Render: clean; orange peak markers in Panel 1/3 match well. |
| tsrvf.svg | align | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "TSRVF: linearizing elastic analysis into a flat tangent space" vs title "TSRVF: Linearizing Elastic Analysis" — paraphrase. A11Y-02: absent. Render: clean; manifold curve → tsrvf_transform() → flat tangent space with radial arrows. |
| alignment-comparison.svg | align | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Comparing alignment methods: none, elastic, and landmark" vs title "Comparing Alignment Methods" — paraphrase (shorter than title). A11Y-02: absent. Render: clean; three strategy dashed lines in Panel 3 clearly distinguished. |
| shape-analysis.svg | align | 61 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Shape analysis: a mean shape in the quotient space" vs title "Shape Analysis: The Mean Shape in Quotient Space" — paraphrase. A11Y-02: absent. Render: clean; SRSF/Fisher-Rao quotient pipeline clear. |
| banded-alignment.svg | align | 61 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: 720×480 multi-panel (DP cost matrix top, before/after panels bottom). The "upper band edge" label at the top-left of the cost-matrix plot is positioned very close to the dashed band-edge line and the axis labels; in the render it appears slightly cramped but readable. The "band_frac × m = B" label at top-right overflows slightly beyond the orange dashed line endpoint. Minor geometry. A11Y-01: paraphrase mismatch. A11Y-02: absent on complex diagram. |
| shift-registration.svg | align | 61 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: Panel 2 shows "shift (rigid)" label arrow and beneath it "elastic warp" arrow label — the "elastic warp" text (shift-registration.svg:~55) implies an elastic warp step inside shift registration, but `shift_register` is purely rigid (scalar δ argmin). The label is a method-accuracy concern (FLAG for Phase 61 fix: remove "elastic warp" arrow or clarify it is NOT part of the method). Visual: two arrows and labels in a 44px-wide gap between panels make the gap crowded. A11Y-01: paraphrase mismatch. |

---

### analyze/ Section (12 diagrams → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| tolerance-bands.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Tolerance bands: a region expected to contain most future curves" vs title "Tolerance Bands: Where Future Curves Will Fall" — paraphrase. A11Y-02: absent. Render: clean; purple theme; FPCA/bootstrap/conformal methods listed. |
| clustering.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 four-quadrant diagram — should have long-form desc. Render: clean 720×480 multi-panel (K-means, Fuzzy C-means, Model Selection, Distance Metrics). Well-structured. |
| gmm-clustering.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on 720×480 three-row diagram. Render: clean; B-spline → EM → outputs layout clear. |
| elastic-clustering.svg | analyze | 62 | Major | OK | Minor | Deferred-60-02 | Major | Design/geometry: **Major** — diagram uses a non-standard visual style completely inconsistent with all 89 peer diagrams. Four bare white rounded-rectangle flow boxes (Raw Curves → Elastic Distance Matrix → Distance-Based Clustering → Results) on an otherwise blank canvas, with section labels "COMPUTATION" and "RESULTS" in all-caps blue/green with no `.ttl`/`.sub`/`.lab`/`.sm`/`.mono` class-based text. The diagram occupies only ~40% of the 720×300 canvas with large empty margins. This is a visual design defect — excessive whitespace, sparse content, non-standard typography (all-caps uppercase labels, no class-based text rendering). While STYLE_SPEC classes ARE defined in the `<style>` block, the rendered text bypasses them entirely (inline `style="fill:..."` overrides). Requires a full redraw to match peer diagram quality. A11Y-02: absent; diagram is simple but the visual deficiency is the primary concern. |
| outlier-detection.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on 720×300 two-row layout. Render: clean; three-panel (Magnitude/Shape/Amplitude outlier types) + detection-method strip below. Text in detection strip fits within bounds. NOTE: "Amplitude Outlier" taxonomy differs from canonical "Phase" taxonomy used in fdars docs (FLAG for Phase 62: verify whether "Amplitude" is the correct term or should be "Phase"). |
| functional-outliers.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent; two-panel layout with bottom caption. Render: clean; hypograph/epigraph panel comparison clear. |
| functional-boxplot.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean single-panel; median/50%CR/whiskers/outliers clearly shown. |
| seasonal-analysis.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 six-branch taxonomy diagram. Render: clean; six panels + Key Functions row. |
| equivalence-testing.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; ±δ corridor panel clear with "✓ equivalent" badge. |
| covariance-functions.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Covariance Functions: Shape to Sample Path Smoothness" vs title "Covariance Functions: Shape → Sample Path Smoothness" — the → arrow is rendered as HTML entity in title (&#8594;) but spelled out in aria-label; Minor mismatch. A11Y-02: absent on 720×480 four-kernel layout. Render: clean; Gaussian/Exponential/Matérn/Periodic kernel panels + smoothness spectrum bar. |
| scoring-metrics.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent; two-panel layout. Render: clean; integrated residual shading in left panel + scoring function list in right panel. Warning text "▲ MAPE: rejects |y_true| ≈ 0" and "▲ MSLE: rejects values ≤ −1" are small but legible. |
| functional-statistics.svg | analyze | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Functional summary statistics: pointwise variance band, depth-based median as observed curve, and covariance surface" vs title "Functional Summary Statistics" — paraphrase (aria is more descriptive than title). A11Y-02: absent on complex 720×480 four-quadrant diagram. Render: clean; four-quadrant layout (mean+std band, depth scores bar, Median≠Mean≠geom.median, depth-trimmed mean) clear. |

---

### monitoring/ Section (3 diagrams → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| spm.svg | monitoring | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Functional Statistical Process Monitoring: learn an in-control FPCA model in Phase I, then chart Hotelling T-squared and SPE against control limits in Phase II" vs title "Functional Statistical Process Monitoring" — aria is more detailed but not verbatim match. A11Y-02: absent. Render: clean three-panel; Phase I/II split clear; Hotelling T² + SPE alarm visible. |
| advanced-spm.svg | monitoring | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Advanced SPM: drift-sensitive charts and fault diagnosis" vs title "Advanced SPM: Catching Drift, Diagnosing the Fault" — paraphrase. A11Y-02: absent. Render: clean; ewma_scores() + run rules + PC contributions bar chart in Panel 3. |
| profile-partial-monitoring.svg | monitoring | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Partial-domain monitoring: restrict the model to the sub-interval that matters" vs title "Partial-Domain Monitoring: Watch the Interval That Matters" — paraphrase. A11Y-02: absent. Render: clean; sub-domain shading in Panel 1 + alarm crossing UCL in Panel 3. |

---

### advisor/ Section (10 diagrams → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| advisor-loop.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Advisor loop: interpret, recommend, re-run, compare — cyclic agentic workflow with Python API recommend-only exit" vs title "Advisor Loop" — more descriptive but paraphrase. A11Y-02: absent on a process-flow diagram with 4+ stages. Render: clean; loop arrows and Python API "recommend-only" exit box clear. |
| advisor-grounding-invariant.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Grounding Invariant". A11Y-02: absent; two-zone boundary diagram. Render: clean; dashed boundary line between fdars zone and LLM zone; "cites" arrow + "no fabrication" label clear. |
| advisor-aspects.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Per-Aspect Taxonomy". A11Y-02: absent on complex 720×480 three-column diagram (14 aspects × 3 task families × shared pipeline). Render: clean; three columns with pipeline in centre clear. |
| advisor-agent-skill.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Agent Skill — Full Agentic Loop". A11Y-02: absent on complex 720×480 flow diagram. Render: clean; step numbering (Step 1+3, Step 2+5, Step 4, Step 5) flow and Python API exit box clear. |
| advisor-auto-tuning.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Auto-Tuning Loop". A11Y-02: absent on complex 720×480 flow diagram with 5 stop-reason boxes. Render: clean; budget check → LLM propose → clamp → re-run → compare → Goodhart guard flow clear; bounded termination strip at bottom. |
| advisor-comparative-selection.svg | advisor | 62 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: the "Winner" box at top-right has a `result["winner"] / fdars-authoritative` label where the text at the right edge of the box is slightly clipped in the render — "fdars-authoritative" label runs close to the right panel edge. Minor text overflow at element boundary. A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: otherwise clean; per-candidate build_diagnostics blocks and fdars sort flow clear. |
| advisor-mcp.svg | advisor | 62 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: "handle + / scalars" label (advisor-mcp.svg:34-35) is centered at x=178, overlapping the dashed stdio boundary line at x=175. The text visually straddles the boundary line making it hard to read which side of the boundary the return path belongs to. Also "stdio" boundary label at x=175 y=54 appears very close to the top edge. Minor misalignment. A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 boundary-model diagram. |
| advisor-pipeline-report.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Pipeline Diagnostic Report". A11Y-02: absent on complex 720×480 three-row pipeline diagram. Render: clean; per-stage blocks → cross-stage caveats → LLM narration row clear. |
| advisor-providers.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Provider Setup — Selection and Precedence". A11Y-02: absent; two-row flow (precedence → four backends). Render: clean; Anthropic/OpenAI/Gemini/Ollama backend cards with install extras. |
| advisor-python-api.svg | advisor | 62 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title "Python API — Recommend-Only Surface". A11Y-02: absent on two-stage boundary diagram. Render: clean; Stage 1 offline / Stage 2 LLM / Advice output box clear. |

---

### sklearn/ Section (1 diagram → Phase 62 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| sklearn-pipeline-dataflow.svg | sklearn | 62 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: the "Predictor" box label "FPCLDAClassifier" (sklearn-pipeline-dataflow.svg:~58) overflows the right edge of the "Predictor" panel — the text width exceeds the panel width at the font size used; in the render "FPCLDAClassifier" is visibly cut at the right edge of the orange panel. Minor text overflow. A11Y-01: aria-label "Functional sklearn Pipeline data flow: (n_obs, n_points) ndarray through transformer stages to FPC scores to predictor" vs title "Functional sklearn Pipeline" — paraphrase. A11Y-02: absent; five-stage pipeline diagram — should have long-form desc. |

---

### regression/ Section (15 diagrams → Phase 63 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| scalar-on-function.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Scalar-on-function regression: predictor curves map to a scalar response" vs title "Scalar-on-Function Regression" — paraphrase. A11Y-02: absent. Render: clean; β(t) inset in Panel 3 is small but visible. |
| function-on-scalar.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Function-on-scalar regression: scalar predictors produce fitted response curves" vs title "Function-on-Scalar Regression" — paraphrase. A11Y-02: absent. Render: clean; group A/B curves in Panel 3 clearly labelled. |
| classification.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Functional classification: labelled curves train a classifier that predicts a class label" vs title "Functional Classification" — paraphrase. A11Y-02: absent. Render: clean; decision boundary in FPC scatter clear. |
| elastic-regression.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Elastic regression: phase-warped curves are aligned then regressed for a phase-invariant prediction" vs title "Elastic Regression" — paraphrase. A11Y-02: absent. Render: clean; alternating Fisher-Rao steps listed in Panel 2. |
| elastic-multinomial.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent on 720×480 four-panel diagram. Render: clean; OvR1/OvR2/OvR3 classifiers → Softmax → Output chain clear. Class labels (aa/ao/dcl) in OvR boxes are legible. |
| scalar-on-shape.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; three-panel (Curve Shapes → shape dist → fregre() → Scalar Response). |
| concurrent-regression.svg | regression | 63 | Major | OK | Minor | Deferred-60-02 | Major | Design/geometry: **Major** — the 44px gap between left panel (x=18, w=320, right edge=338) and right panel (x=382, w=320) contains a "→" arrow at x=360 and two lines of text ("concurrent" / "regression") centered at x=360 in 11px font. The text extends approximately ±60px from center (360±60 = 300 to 420), overflowing into both panels. In the render the label text visually overlaps both panel borders. The transition label is illegible in context. FLAG for Phase 63: either widen the gap, reduce font, or reposition the label outside the overlap zone (concurrent-regression.svg:47-49). |
| functional-glm.svg | regression | 63 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: the "binomial" label (font-size="10", x=452, fill="#e8710a") at y=147 and the "logit g(μ) = log(μ/1−μ)" text (class="sm", x=558 text-anchor="middle") at the same y=147 are adjacent in the render but "binomial" at x=452 in 10px mono font ends near x=500, and the sm-class text anchored at x=558 extends to roughly x=460 leftward — creating a visual near-collision ("binomia**l**ogit") in the rendered PNG. Minor text proximity defect (functional-glm.svg:69-70). A11Y-01: paraphrase. A11Y-02: absent. |
| cross-validation.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; K-fold grid in Panel 1 well-designed; CV error U-curve in Panel 3 clear. |
| regression-diagnostics.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; influence plot with 4/n threshold line clear. |
| uncertainty-quantification.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Uncertainty quantification: confidence bands on the coefficient function" vs title "Uncertainty Quantification: Bands on β(t)" — paraphrase. A11Y-02: absent. Render: clean; shaded band around β(t) in Panel 3 clear. |
| explainability.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Model explainability: attributing predictions to regions of the domain" vs title "Model Explainability: Why the Prediction?" — paraphrase. A11Y-02: absent. Render: clean; highlighted domain region in Panel 3 effective. |
| conformal-prediction.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; scalar interval ŷ ± band in Panel 3 (horizontal bar) clear. |
| conformal-classification.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean; confident {A} vs ambiguous {A,B} prediction sets with badge boxes clear. |
| robust-regression.svg | regression | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Robust regression: down-weighting outliers to recover an unaffected coefficient" vs title "Robust Regression: Resisting Contamination" — paraphrase. A11Y-02: absent. Render: clean; robust vs OLS drift in Panel 3 clear. |

---

### inference/ Section (4 diagrams → Phase 63 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| inference-anova.svg | inference | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "One-way Functional ANOVA — between-group and within-group variation decomposition" vs title "One-way Functional ANOVA — Variance Decomposition" — paraphrase. A11Y-02: absent; two-panel diagram with between-group and within-group panels. Render: clean; μ₁/μ₂/μ₃ group curves + grand mean dashed line in left panel; individual deviations from group mean in right panel. |
| inference-permutation-test.svg | inference | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Permutation Test — observed statistic vs permutation null distribution" vs title "Permutation Test — Null Distribution vs Observed Statistic" — paraphrase (order reversed). A11Y-02: absent. Render: clean; T_obs dashed vertical line + red tail mass clear. |
| inference-scb.svg | inference | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Simultaneous Confidence Band — SCB is wider than pointwise CI" vs title "Simultaneous Confidence Band vs Pointwise CI" — paraphrase. A11Y-02: absent. Render: clean; SCB (blue shaded) wider than pointwise CI (orange shaded) around μ(t) curve clear. |
| itp-interval-inference.svg | inference | 63 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: right panel legend labels ("raw p-value" at x=400, "closure-adjusted (≥ raw)" at x=400) are left-anchored and extend toward x=530+; at 11px system-ui font the "closure-adjusted (≥ raw)" text (~21 chars) ends near x=526, which is within the right-panel bounds (x=356, width=340, right edge x=696). However in the render the legend area appears visually cramped with the legend items overlapping slightly with bar chart bars underneath. Minor layout crowding. A11Y-01: paraphrase mismatch. A11Y-02: absent on two-panel ITP diagram. |

---

### examples/ Section (21 diagrams → Phase 63 bucket)

| Diagram | Section | Fix bucket | Design/geometry | STYLE_SPEC | Accessibility | Sync | Overall | Notes |
|---------|---------|-----------|-----------------|------------|---------------|------|---------|-------|
| ex-sonar-tsrvf.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Validation-First Framework: Three Analysis Paths" (matches title verbatim — this is the ONLY diagram where aria-label exactly matches the title; however the aria-label is shorter than the full SVG title text). A11Y-02: absent on complex decision-tree diagram. Render: clean 720×480; Phase Elasticity Check → Signal Conditioning → three-path decision tree with accuracy badges. Previously non-conforming viewBox (0 0 700 400) and missing role/aria — fully migrated in Phase 43. |
| ex-canadian-weather.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent on complex 720×480 three-row pipeline diagram. Render: clean; FOSR/fanova/fclassif workflow with result badges clear. |
| ex-canadian-precipitation.svg | examples | 63 | Major | OK | Minor | Deferred-60-02 | Major | Design/geometry: **Major** — the rightmost "Geographic drivers" panel (dark green, x≈566) contains multiple text items that are visibly clipped at the right viewBox edge (x=720). Text items including "For: some error driv...", "Concurrent: multiple...", "Geographic confirmed..." are cut at the panel right edge. The panel contents are illegible in the render. Text overflow outside viewBox bounds (ex-canadian-precipitation.svg, rightmost panel). FLAG for Phase 63: widen this panel or reduce font / text density. A11Y-01: paraphrase. A11Y-02: absent on complex diagram. |
| ex-canadian-depth-centrality.svg | examples | 63 | Major | OK | Minor | Deferred-60-02 | Major | Design/geometry: **Major** — the rightmost "Ranked centrality" panel (dark blue) contains text that is clipped at the right viewBox edge. "deepest = most central", "2nd shallowest...", "last... peripheral" labels are cut — the panel extends past x=720 or the text is too long. In the render, the right panel text is visibly truncated (ex-canadian-depth-centrality.svg, right panel). FLAG for Phase 63: shrink font, narrow text, or add line breaks. A11Y-01: paraphrase. A11Y-02: absent. |
| ex-canadian-function-on-scalar.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on four-panel diagram. Render: clean; FOSR → β_lat(t)/β_lon(t) → predict_fosr chain clear; β_lat(t) curve panel and predict_fosr orange panel well-structured. |
| ex-canadian-seasonal.svg | examples | 63 | Major | OK | Minor | Deferred-60-02 | Major | Design/geometry: **Major** — bottom-right result badge ("StableSeasonal · timing fixed") has its full text truncated: "summer peak day constant; level rise" is cut at the right viewBox edge in the render (ex-canadian-seasonal.svg, bottom-right badge). The text "level rise" is the meaningful conclusion but is cut. FLAG for Phase 63: shorten this label or reduce font. A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 six-panel diagram. |
| ex-andrews-wine.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent on complex 720×480 five-box pipeline + consensus + result-badge diagram. Render: clean; four detector blocks + Mahalanobis comparison + consensus text + result badges clear. |
| ex-andrews-wine-intro.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean 720×300; row→curve encoding pipeline with fdars toolbox panel. |
| ex-andrews-wine-clustering.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: clean; kmeans_fd/fuzzy_cmeans_fd + FPCA/FANOVA blocks + before/after cluster diagram. |
| ex-andrews-wine-qc.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 QC pipeline diagram. Render: clean; Phase I boxplot/tolerance band → Phase II spm_monitor → Off-cultivar alarm panel. |
| ex-biopharma-monitoring.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 three-row SPM pipeline. Render: clean; Phase I FPCA → spm_phase1/monitor + ewma_scores → False-alarm + yield prediction row clear. |
| ex-cross-validation.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean 720×300; five-panel (Tecator → fregre_cv → optimal_k → FPC-LM/PLS/NP R² badges). R² badges with OOF values clear. |
| ex-explainability-regions.svg | examples | 63 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: the dark-green consensus banner ("All five explainers converge...") has a second line "Convergence across independent methods · trustworthy..." in a colour that provides very low contrast against the dark green background — text is barely legible. Minor contrast issue (ex-explainability-regions.svg, consensus banner, line 2). A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 five-explainer diagram. |
| ex-functional-outlier-workflow.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent. Render: clean 720×300; simulate+inject → two outlier types → two-detector workflow → MS-plot + outliergram panels clear. |
| ex-growth-alignment.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 six-box alignment analysis diagram. Render: clean; alignment_quality → karcher_mean → FPCA before/after → equivalence_test pipeline clear. |
| ex-inline-monitoring.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: clean; simulate → Phase I → fault injection → Shewhart vs EWMA → detection power + F1 panels clear. |
| ex-phoneme-shape.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 diagram. Render: clean; lp_self_1d vs shape_self_distance_matrix comparison + clustering purity badges clear. |
| ex-tecator-conformal-coverage.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label "Conformal Coverage Guarantee — split conformal prediction on Tecator NIR spectra" vs title "The Conformal Coverage Guarantee" — paraphrase. A11Y-02: absent. Render: clean 720×300; conformal_fregre_lm → single split + 60 random splits coverage distribution clear. |
| ex-tecator-monitoring.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: paraphrase mismatch. A11Y-02: absent on complex 720×480 three-section SPM diagram. Render: clean; Phase I → Phase II (spm_monitor/run-rules/ewma) → fault diagnosis row clear. |
| ex-tecator-regression.svg | examples | 63 | Minor | OK | Minor | Deferred-60-02 | Minor | Design/geometry: the bottom caption text (ex-tecator-regression.svg, last `<text>` element) "...smoother on L² distances) is strongest. PLS β(λ) readable: 930–970 nm C–H band. Logistic β(λ) same region drives go/no–go cl..." is cut at the right viewBox edge — the long single-line text overflows past x=720. Minor text overflow at viewBox boundary. A11Y-01: paraphrase. A11Y-02: absent on complex 720×480 diagram. |
| ex-tolerance-vs-conformal.svg | examples | 63 | OK | OK | Minor | Deferred-60-02 | Minor | A11Y-01: aria-label paraphrase of title. A11Y-02: absent. Render: clean 720×300; FPCA tolerance band vs conformal prediction band comparison (tighter vs outer envelope) clear. |

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

## 3. Ranked Fix Worklists by Phase (placeholder — filled by Plan 60-02)

_This section is populated by Plan 60-02, which ranks diagrams within each bucket by severity (Major first, then Minor) and assembles the actionable fix worklist for each correction phase._

### Phase 61 Fix Worklist (placeholder)
### Phase 62 Fix Worklist (placeholder)
### Phase 63 Fix Worklist (placeholder)

---

## 4. COVER-01 Coverage-Gap List (placeholder — filled by Plan 60-02)

_Plan 60-02 enumerates methods/pages in each docs section that lack a concept diagram. Those gaps are tracked here as the worklist for Phase 64._

---

## 5. SYNC-01/SYNC-02 Drift List (placeholder — filled by Plan 60-02)

_Plan 60-02 compares rendered concept PNGs against their corresponding thumb/card assets and flags visual drift. Results recorded here as the worklist for Phase 64._

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
