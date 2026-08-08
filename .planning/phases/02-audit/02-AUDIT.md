# Phase 2: Audit Master Document

**Phase:** 02-audit
**Date:** 2026-08-07
**Status:** In progress — learn/ section complete; remaining sections populated by Plans 02–03.

## Purpose

This document is the single git-diffable source of truth for the Phase 2 audit. It scopes all diagram-sweep phases (Phases 3–9) by providing:

1. A **Page→Diagram Coverage Table** — classifying every nav content page on two independent axes (style, accuracy) plus a rollup label.
2. An **R-era Grep Report** — every R-era hit with file:line, grouped by section.
3. A **Ranked Gap + New-Example List** — user-selectable candidates (GAP-#### for coverage/style/accuracy gaps; EX-#### for new-example candidates).

### D-02 Rollup Rule (explicit)

For each page with a diagram:
- **`accurate`** — BOTH axes clean: style axis = `conforms` AND accuracy axis = `accurate`.
- **`inconsistent`** — at least one axis is off: style is `legacy-outlier` OR accuracy is `inaccurate/misleading` (or both).
- **`missing`** — no diagram exists for a page that warrants one.

This two-axis detail exists so sweeps can distinguish a **restyle** (legacy-outlier but accurate, lower effort) from a **redraw** (inaccurate, higher effort).

### D-06 Selection Gate

The `Selection` column in Section 3 is blank by default. **The user marks it before Phase 3 begins.** Phase 3 planning reads only the selected items.

---

## 1. Page→Diagram Coverage Table

**Columns:** `Page` | `Diagram` | `Style axis` | `Accuracy axis` | `Rollup` | `Warrants diagram?` | `Needs method-verification`

**Style-axis verdicts are grep-reproducible** against `docs/assets/diagrams/*.svg` by checking:
- `viewBox="0 0 720` — width 720 (grep: `viewBox="0 0 720`)
- Five CSS classes: `.ttl`, `.sub`, `.lab`, `.sm`, `.mono` (grep each in the `<style>` block)
- `system-ui` font stack (grep: `system-ui`)
- `role="img"` and `aria-label` on the root `<svg>` element

`conforms` = all markers present. `legacy-outlier` = one or more markers absent (with names of failing markers recorded).

### learn/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| learn/introduction.md | introduction.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — three-panel input→Fdata→output flow correctly depicts the constructor call `Fdata(X, argvals)` and the resulting curve family. Dots in Panel 1 represent raw point observations; Panel 3 shows multiple curves with a mean highlighted. Matches API semantics. | accurate | yes — essential orientation diagram showing the core abstraction (raw data → functional object) that the whole library rests on. | — |
| learn/custom-plotting.md | custom-plotting.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — the diagram correctly shows that fdars provides no built-in plot layer (the text caption states this explicitly) and the three panels show the matplotlib workflow: plain curve set → `ax.plot(...)` idioms → styled figure with mean±sd band and median. Consistent with the page's content. | accurate | yes — the page is explicitly a plotting recipe guide; an overview diagram anchoring the matplotlib workflow adds clear value. | — |
| learn/simulation.md | simulation.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — KL parameters panel shows basis eigenfunctions (φ₁ φ₂ φ₃) and a λ-decay bar chart; method panel names `simulate()`, KL expansion, and gaussian_process; output panel shows a family of random curves. Faithfully depicts the Karhunen-Loève simulation pipeline. | accurate | yes — simulation is a technical entry point; showing the KL parameter→sampling pipeline prevents misuse. | — |
| learn/smoothing.md | smoothing.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | inaccurate/misleading — **FINDING CONFIRMED with evidence.** Panel 3 ("Smooth Curve") draws a faint ghost path (the "before" reference) that reuses the noisy coordinates from Panel 1 verbatim, shifted only by 8 px in y. Panel 1 (line 18): `M0 92 L8 70 L16 100 L24 62 ... L156 58`. Panel 3 ghost (line 48): `M0 84 L8 70 L16 100 L24 62 ... L156 58`. Sequences from L8 onward are identical — the Panel 3 ghost is not an independently drawn noisy reference; it is a copy of the jagged polyline from Panel 1. The smooth curve itself (line 49, a cubic Bézier) is correct, but the ghost underlay misrepresents what the noisy data looks like on the smoothed-output panel. Needs a **redraw** (replace the ghost polyline with a path whose coordinates genuinely differ from Panel 1, or remove the ghost entirely). | inconsistent | yes — smoothing is the foundational pre-processing step; a concept diagram is essential. Current diagram warrants a redraw (accuracy axis fails). | — |
| learn/derivatives.md | derivatives.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a monotone rising curve x(t); Panel 2 names `fd.deriv(nderiv)` with nderiv=1→velocity, nderiv=2→accel.; Panel 3 shows two sub-panels with x'(t) velocity and x''(t) acceleration curves with visually appropriate shapes (velocity increasing, acceleration with an inflection). Consistent with finite-differences semantics. | accurate | yes — distinguishing the level, velocity, and acceleration interpretation is non-obvious and frequently misunderstood; the diagram adds clear pedagogical value. | — |
| learn/irregular-sampling.md | irregular-sampling.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows two curves with points on uneven individual grids (different x-positions per curve, tick marks showing the irregular spacing); Panel 2 names the pipeline (kernel smoother → basis expansion → evaluate on common grid); Panel 3 shows the result: curves on a regular shared grid with dots at the common grid points. Faithfully depicts the smooth→regrid operation. | accurate | yes — irregular sampling is a common real-world complication; showing the ragged→common-grid transform is essential to the page's concept. | — |
| learn/index.md | — | — | — | — | no — the learn/ landing page is a section index listing page links. An overview diagram is not warranted; navigation tiles serve the same orientation purpose. | — |

### represent/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| represent/fpca.md | fpca.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a curve sample; Panel 2 names `fpca(X, t, n_comp)` with Karhunen-Loève, three steps (mean μ̂(t), eigenfunctions φₖ, scores ξᵢₖ); Panel 3 shows modes-of-variation inset (μ̂ ± 2√λₖ · φₖ) and a score scatter. Faithfully depicts the FPCA decomposition pipeline. | accurate | yes — FPCA is the primary dimensionality reduction entry point; the three-panel concept diagram is essential. | — |
| represent/elastic-fpca.md | elastic-fpca.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows time-shifted (warped) curves with label "peaks shifted in time"; Panel 2 names `*_fpca(X, t)` with square-root-slope and three variants (vert_fpca, horiz_fpca, joint_fpca); Panel 3 labels "Amplitude + Phase" with amplitude modes and phase (warps) sub-panels. Correctly depicts the elastic FPCA amplitude/phase split. | accurate | yes — elastic FPCA is a technically distinct method from standard FPCA; the diagram clarifying the amplitude/phase split is essential. | — |
| represent/basis-representation.md | basis-representation.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows one curve (200 grid points); Panel 2 names `fdata_to_basis_1d` with B-spline/Fourier options and basis function bell-curves; Panel 3 shows coefficient bars (15 coefficients) and a reconstruction curve. No R-era identifiers found in SVG — all text references `fdata_to_basis_1d` (the current Python fdars API name). The prose page (basis-representation.md) exclusively uses the Python API (`from fdars.basis import fdata_to_basis_1d`). NOT confirmed as R-era (the preliminary finding was not found). | accurate | yes — basis representation is the foundational preprocessing step for most downstream analyses; the diagram is essential. | not-found: the preliminary "R-era content" finding for basis-representation.svg is not confirmed. All text in the SVG uses the current fdars Python API (`fdata_to_basis_1d`). The prose page (lines 33–164) uses only Python calls. No R-era identifiers present. |
| represent/andrews-transformation.md | andrews-transformation.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a feature table (rows=observations, columns x1–x4 with numeric values); Panel 2 shows the Andrews formula `x1/√2 + x2 sin t + x3 cos t + ...` as a Fourier series on t ∈ [−π, π]; Panel 3 shows one curve per row. Faithfully depicts the Andrews curve encoding. | accurate | yes — the Andrews transformation is a non-obvious encoding; the table→formula→curve diagram is essential to understanding the method. | — |
| represent/depth-functions.md | depth-functions.svg | legacy-outlier (viewBox 720 ✓; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses inline font-size attributes; missing: role=img; missing: aria-label; font-family is inline `'Segoe UI', system-ui, sans-serif` not the `.ttl/.sub/.lab/.sm/.mono` class structure) | accurate — The diagram correctly depicts the depth-centrality concept: deep curves (blue, central) vs shallow curves (grey) vs outlier (red); `fd.depth(method)` unified interface with three method categories (Pointwise: FM/MBD/BD/MEI, Projection: RP/RT/RPD, Kernel/Spatial: mode/FSD/KFSD); depth values in [0,1] per curve with a bar chart. Bottom row shows depth-based tools (outliergram, functional boxplot, robust statistics, tolerance bands, streaming). Matches fdars API semantics. | inconsistent | yes — depth is a core method supporting outlier detection, robust estimation, and monitoring; the multi-panel concept diagram is essential. | — |
| represent/streaming-depth.md | streaming-depth.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a window of reference curves (grey) plus a new arriving curve (red); Panel 2 names `modified_band_1d` with ref_data/data/roll-window steps; Panel 3 shows depth over time with a drift drop triggering an alarm. Faithfully depicts the streaming depth anomaly-detection pipeline. | accurate | yes — streaming depth is a technically distinct variant; the window→score→alarm flow diagram is essential. | — |
| represent/distance-metrics.md | distance-metrics.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a pair of curves with the question "how far apart?"; Panel 2 names `*_self_1d(data)` with three geometry options (lp_self_1d, dtw_self_1d, hausdorff_self_1d); Panel 3 shows a symmetric distance matrix with zero diagonal. Faithfully depicts the pairwise distance computation pipeline. | accurate | yes — the choice of metric has major downstream consequences; the diagram explaining geometry choice is essential. | — |
| represent/index.md | — | — | — | — | no — the represent/ landing page is a section index with navigation tiles. An overview diagram is not warranted; the hero card (cards/represent.svg) serves the orientation purpose. | — |

### align/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| align/elastic-alignment.md | elastic-alignment.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate (with evidence on phase/amplitude finding) — Panel 1 shows misaligned peaks with a blurred cross-sectional mean (dashed); Panel 2 names `karcher_mean()` with Fisher-Rao/SRSF and three steps (SRSF representation, Warp search DP, Iterate to template); Panel 3 shows aligned curves converging to a sharp mean plus a warp γ(t) inset (top-right box shows monotone warp paths). **Phase-vs-amplitude finding (elastic-alignment.svg:47, line 47):** Panel 3 label reads "Aligned + Warps γ" — the warps γ(t) are shown as a separate inset (lines 55–61, a small box with monotone curves), not interleaved with amplitude variation. The diagram's subtitle (line 10): "Warp curves to a common template; the mean recovers a sharp profile." The title (line 9): "Elastic Alignment: Separating Amplitude from Phase." The amplitude/phase split is labeled in the title and aria-label (line 1: "separating amplitude from phase variation") but the body panels emphasize the alignment result rather than explicitly separating amplitude vs phase variation plots side-by-side. The warp γ(t) inset (lines 55–61) is present but small and unlabeled as "phase." | inconsistent | yes — elastic alignment is the core method in this section; the concept diagram is essential. | confirm diagram visually separates phase variation (γ(t)) from amplitude variation in the output panel — the warp inset at elastic-alignment.svg:55 shows γ(t) paths but lacks an explicit amplitude-vs-phase decomposition panel; verify whether this is sufficient or needs an amplitude curve comparison panel added. |
| align/advanced-alignment.md | advanced-alignment.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a phase-varying sample; Panel 2 names `align(λ, ...)` with three steps (robust_karcher_mean, constrained warp, select λ penalty); Panel 3 shows aligned curves and a λ sweep with the optimal λ highlighted. Faithfully depicts the regularized elastic alignment pipeline. | accurate | yes — advanced alignment with λ regularization is a distinct and non-obvious variant; the diagram is essential. | — |
| align/landmark-registration.md | landmark-registration.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows curves with marked landmarks at different positions; Panel 2 names `register(γ)` with detect peaks/valleys, target=mean(times), monotone interp warp; Panel 3 shows registered curves with aligned landmarks. Faithfully depicts the landmark detection → warp → register pipeline. | accurate | yes — landmark registration is a distinct alternative to elastic alignment; the diagram is essential. | — |
| align/tsrvf.md | tsrvf.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a curve on a curved manifold space; Panel 2 names `tsrvf_transform()` with SRVF representation, parallel transport, Karcher-mean base; Panel 3 shows the flat tangent space result with "means, PCA valid" caption. Faithfully depicts the TSRVF linearization concept. | accurate | yes — TSRVF is the theoretical foundation for elastic analysis; the manifold-to-tangent-space concept diagram is essential. | — |
| align/alignment-comparison.md | alignment-comparison.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a phase-varying sample; Panel 2 names `compare()` with three strategies (none/cross-sectional, elastic/karcher_mean, landmark/interp); Panel 3 shows compared means with none (blurred), elastic (sharp, orange), landmark (sharp, orange). Faithfully depicts the three-way alignment comparison. | accurate | yes — the comparison page motivates choosing among methods; a side-by-side result diagram is essential. | — |
| align/shape-analysis.md | shape-analysis.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows curves with both amplitude and phase variation (label: "amplitude + phase vary"); Panel 2 names `shape_mean()` with SRSF/Fisher-Rao, quotient by warping, shape_distance; Panel 3 shows the mean shape result with label "one sharp template." Faithfully depicts the quotient-space shape analysis. | accurate | yes — shape analysis is distinct from elastic alignment (it factors out both timing and amplitude scale); the quotient-space concept is non-obvious and the diagram is essential. | — |
| align/index.md | — | — | — | — | no — the align/ landing page is a section index with navigation tiles. An overview diagram is not warranted; the hero card (cards/align.svg) serves the orientation purpose. | — |

### analyze/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| analyze/tolerance-bands.md | tolerance-bands.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a curve sample; Panel 2 names `fpca_tolerance_band()` with FPCA/bootstrap, Conformal/elastic, Coverage 1−α; Panel 3 shows mean plus shaded tolerance region. Faithfully depicts the tolerance band construction. | accurate | yes — tolerance bands are the primary coverage tool; the diagram is essential. | — |
| analyze/clustering.md | clustering.svg | legacy-outlier (viewBox 720 ✓; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses inline font-size/font-weight attributes; missing: role=img; missing: aria-label; font-family inline `'Segoe UI', system-ui, sans-serif`) | accurate — the diagram shows Unlabeled Curves input, two method boxes (K-Means with `kmeans_fd(fd, ncl)` and Fuzzy C-Means with `fuzzy_cmeans_fd(fd, ncl, m)`), and a Model Selection box (`cluster.optim()` with silhouette, Calinski-Harabasz, elbow). No R-era identifiers. Uses current fdars API names. | inconsistent | yes — clustering is a primary analysis entry point; the diagram is essential. | — |
| analyze/gmm-clustering.md | gmm-clustering.svg | legacy-outlier (viewBox 720 ✓; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses inline font-size/font-weight attributes; missing: role=img; missing: aria-label; font-family inline `'Segoe UI', system-ui, sans-serif`) | accurate — the diagram shows functional data input with curves colored by cluster, a GMM fit box, and posterior probability output. No R-era identifiers. Depicts the EM-on-basis-coefficients approach correctly. | inconsistent | yes — GMM clustering is a distinct soft-assignment method; the diagram is essential. | — |
| analyze/elastic-clustering.md | elastic-clustering.svg | legacy-outlier (viewBox `0 0 700 250` — non-720 width ✗; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses `font-family="sans-serif"` with inline font-size; missing: role=img; missing: aria-label; no system-ui font stack) | accurate — the diagram shows a four-step pipeline: Raw Curves → Elastic Distance Matrix → K-Means/Hierarchical → Cluster Assignments + Aligned Mean Curves. No R-era identifiers. Correctly depicts the elastic distance-based clustering flow. | inconsistent | yes — elastic clustering is the main phase-invariant clustering method; the diagram is essential. | — |
| analyze/outlier-detection.md | outlier-detection.svg | legacy-outlier (viewBox `0 0 600 350` — non-720 width ✗; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses inline font-size/font-weight; missing: role=img; missing: aria-label; font-family inline `'Segoe UI', system-ui, sans-serif`) | accurate — the diagram shows three outlier types (Magnitude: shifted up/down; Shape: different shape/pattern; Phase: timing-shifted peak) with visual curve examples and detection method labels. No R-era identifiers. Faithfully depicts the magnitude/shape/phase outlier taxonomy. | inconsistent | yes — the three-type outlier taxonomy is non-obvious; the diagram is essential. | — |
| analyze/seasonal-analysis.md | seasonal-analysis.svg | legacy-outlier (viewBox 720 ✓; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses inline font-size/font-weight; missing: role=img; missing: aria-label; font-family inline `'Segoe UI', system-ui, sans-serif`) | accurate — the diagram shows a Seasonal Signal x(t) input with three output branches (Period Estimation, Seasonal Decomposition, Amplitude Monitoring), plus a bottom row of additional tools. No R-era identifiers found. Correctly depicts the seasonal analysis toolkit. | inconsistent | yes — seasonal analysis is a multi-method domain; the overview diagram showing the toolkit branches is essential. | — |
| analyze/equivalence-testing.md | equivalence-testing.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows two curve samples (group 1, group 2); Panel 2 names `equivalence_test()` with TOST + multiplier SCB, T = sup |μ₁ − μ₂|, Band vs margin δ, Bootstrap p-value; Panel 3 shows a ±δ corridor with the difference band and a "✓ equivalent" verdict. Faithfully depicts the equivalence testing procedure. | accurate | yes — equivalence testing is conceptually distinct from hypothesis testing; the corridor concept is non-obvious and the diagram is essential. | — |
| analyze/covariance-functions.md | covariance-functions.svg | legacy-outlier (viewBox `0 0 600 425` — non-720 width ✗; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — uses inline font-size/font-weight; missing: role=img; missing: aria-label; font-family inline `'Segoe UI', system-ui, sans-serif`) | accurate — the diagram shows four covariance kernel types (Gaussian, Exponential, Matérn, Periodic) with kernel shape illustrations and corresponding sample path smoothness descriptions. No R-era identifiers. Faithfully depicts the kernel→smoothness relationship. | inconsistent | yes — the kernel→sample-path-smoothness connection is non-obvious; the diagram is essential. | — |
| analyze/index.md | — | — | — | — | no — the analyze/ landing page is a section index with navigation tiles. An overview diagram is not warranted; the hero card (cards/analyze.svg) serves the orientation purpose. | — |

### regression/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| regression/scalar-on-function.md | scalar-on-function.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate (with β(t) finding) — Panel 1 shows predictor curves X(t); Panel 2 names `fregre_lm / pls(X, y)` with FPC/PLS/Kernel method list; Panel 3 shows a fitted-vs-actual scatter ("Scalar Response ŷ") plus a β̂(t) inset box (lines 59–64: a rect with β̂(t) label and a curve). The β(t) coefficient function IS present as an inset in Panel 3 at scalar-on-function.svg:62–63 — the inset shows β̂(t) with a curve path. However the inset is small and secondary relative to the fitted-vs-actual plot which is the main Panel 3 content. | accurate | yes — scalar-on-function regression is the primary regression model; the diagram is essential. | confirm scalar-on-function shows β(t) coefficient curve prominently — β̂(t) is present as a small inset at scalar-on-function.svg:59–64 but is secondary to the fitted-vs-actual scatter; verify during Phase 7 sweep whether the β(t) inset is sufficient or the diagram needs a more prominent β(t) panel. |
| regression/function-on-scalar.md | function-on-scalar.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows scalar/group predictors (group A x=0, group B x=1, dose/age labels); Panel 2 names `fosr(y, X)` with "Penalised β(t) per predictor" and three method steps (Roughness penalty λ, FPC/fosr_fpc, ANOVA/fanova); Panel 3 shows fitted curves ŷ(t) with one curve per group (labels A, B). Faithfully depicts the function-on-scalar regression model. | accurate | yes — function-on-scalar is a distinct model where the response is functional; the diagram is essential. | — |
| regression/classification.md | classification.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows labelled curves (class 0 blue, class 1 red); Panel 2 names `fclassif_knn / lda()` with LDA/QDA on FPCs, k-NN/logistic, Depth-vs-depth; Panel 3 shows a "Predicted Class" label with "decision boundary in FPC space." Faithfully depicts the functional classification pipeline. | accurate | yes — functional classification is a primary supervised method; the diagram is essential. | — |
| regression/elastic-regression.md | elastic-regression.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows phase-warped X(t) with "peaks misaligned →" label; Panel 2 names `elastic_regression()` with Fisher-Rao alternating and three steps (align γᵢ in SRVF, re-fit α/β(t), repeat to converge); Panel 3 shows prediction ŷ with "aligned → same ŷ" label confirming phase-invariance. Faithfully depicts the elastic regression iterative alignment-regression pipeline. | accurate | yes — elastic regression is a key phase-invariant prediction method; the diagram is essential. | — |
| regression/scalar-on-shape.md | scalar-on-shape.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows curve shapes with "same shape, phase varies" label; Panel 2 names `shape dist → fregre()` with shape_mean, shape distance matrix, fregre_np/fregre_lm; Panel 3 shows scalar response ŷ with fitted-vs-actual scatter. Faithfully depicts the SRSF quotient → scalar regression pipeline. | accurate | yes — scalar-on-shape is a distinct method combining shape analysis with regression; the diagram is essential. | — |
| regression/cross-validation.md | cross-validation.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows K data folds with held-out (red) and train (grey) indicators; Panel 2 names `fregre_cv(X, y)` with split/n_folds, out-of-fold MSE, fclassif_cv for labels; Panel 3 shows a CV error vs k curve with a U-shape and optimal k marked. Faithfully depicts the k-fold cross-validation for component selection. | accurate | yes — cross-validation for functional data has specific considerations; the diagram showing the fold split and U-curve is essential. | — |
| regression/regression-diagnostics.md | regression-diagnostics.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a fitted model (y = Zβ + ε); Panel 2 names `influence_diagnostics()` with hat-matrix diagnostics, Leverage/Cook's D, DFBETAS/DFFITS, PRESS/VIF; Panel 3 shows an influence plot with flagged points and a 4/n Cook's D threshold line. Faithfully depicts regression diagnostics. | accurate | yes — regression diagnostics are non-obvious for functional data; the diagram is essential. | — |
| regression/uncertainty-quantification.md | uncertainty-quantification.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a fitted model with β̂(t) and "point estimate" label; Panel 2 names `bootstrap_ci()` with Pointwise band, Simultaneous band, Prediction intervals; Panel 3 shows a "Confidence Band" result with "95% band around β(t)" and β(t) ± band labels. Faithfully depicts bootstrap CI construction for coefficient functions. | accurate | yes — uncertainty quantification for functional regression is non-standard; the diagram is essential. | — |
| regression/explainability.md | explainability.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows a fitted model with f(X) → ŷ label; Panel 2 names `shap · pdp · regions` with SHAP/PDP/ALE, Pointwise importance, `significant_regions()`; Panel 3 shows an "Importance Curve" with a highlighted important domain region. Faithfully depicts the explainability attribution pipeline. | accurate | yes — model explainability in FDA is non-obvious; the domain-attribution concept diagram is essential. | — |
| regression/conformal-prediction.md | conformal-prediction.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | inaccurate/misleading — **FINDING CONFIRMED with evidence.** Panel 3 label (line 52): "Prediction Interval"; sub-label (line 53): "point ŷ with a band"; the output graphic (lines 54–62) shows a single vertical rectangle spanning [lower, upper] with a dot at ŷ and label "ŷ ± interval" (line 61). The output depicts a **scalar constant interval** — a single fixed numeric band of the form [ŷ − q, ŷ + q] — rather than a time-varying functional band ŷ(t) ± q(t) spanning the domain [0, T]. This is misleading for `fdars.conformal` which operates on functional responses. | inconsistent | yes — conformal prediction is a key capability; the diagram is essential but currently needs a redraw. | confirm conformal band is time-varying ŷ(t)±q(t) against `fdars.conformal` — the current output panel (conformal-prediction.svg:54–62) shows a scalar constant interval `[ŷ − q, ŷ + q]`, not a time-varying band over the domain. Verify during Phase 7 sweep whether the API produces a scalar or functional band, then redraw the output panel accordingly. |
| regression/conformal-classification.md | conformal-classification.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows model+calibration with class A (blue) and class B (orange) points; Panel 2 names `conformal_classif()` with LDA/QDA/kNN, Logistic wrappers, P(y∈Ĉ)≥1−α; Panel 3 shows prediction sets: confident → {A}, ambiguous → {A, B}. Faithfully depicts the conformal classification prediction-set construction. | accurate | yes — conformal classification is a distinct coverage-guaranteed method; the diagram is essential. | — |
| regression/robust-regression.md | robust-regression.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows contaminated curves with an outlier highlighted; Panel 2 names `fregre_huber / l1()` with Huber (k=1.345), L1/median/50% BP, vs OLS baseline; Panel 3 shows "Robust β(t)" output, contrasting the robust estimate (stable) against OLS drift (affected by outlier). Faithfully depicts the robust regression pipeline. | accurate | yes — robust regression is essential for contaminated data; showing the contrast with OLS is key. | — |
| regression/index.md | — | — | — | — | no — the regression/ landing page is a section index with navigation tiles. An overview diagram is not warranted; the hero card (cards/regression.svg) serves the orientation purpose. | — |

### monitoring/ Section

| Page | Diagram | Style axis | Accuracy axis | Rollup | Warrants diagram? | Needs method-verification |
|------|---------|------------|---------------|--------|-------------------|--------------------------|
| monitoring/spm.md | spm.svg | legacy-outlier (viewBox 720 ✓; missing: .ttl/.sub/.lab/.sm/.mono CSS class block — no `<style>` block, uses inline font-size/font-weight attributes throughout; missing: role=img; missing: aria-label; font-family inline `'Segoe UI', system-ui, sans-serif`) | inaccurate/misleading — **FINDING CONFIRMED with evidence.** The SVG is a wholesale R-era artifact reused for the Python SPM page. Line 5: `"Functional Data Analysis in R, powered by Rust"` — explicitly describes an R package, not the Python `fdars` package. Line 31: `autoplot() — visualization` (R/ggplot2 idiom; no `autoplot` in Python fdars). Line 55: `"Rust Backend (extendr)"` — `extendr` is the R-to-Rust binding library; the Python equivalent is PyO3 (used in pyfda). Line 56: `"zero-copy R ↔ Rust"` — describes R/Rust interop, not Python/Rust. Furthermore the diagram depicts a general toolkit overview ("The fdars Toolkit") rather than an SPM-specific Phase I/Phase II monitoring concept. The actual SPM page covers `spm_phase1()` / `spm_monitor()` and Phase I/II control limits — none of which appear in the diagram. | inconsistent | yes — SPM is the core monitoring method; a concept diagram is essential. Current diagram needs a full **redraw** (wrong section entirely, R-era content, wrong method depicted). | confirm SPM shows distinct Phase I / Phase II limits — the current spm.svg (lines 4–56) is an R-era general toolkit overview completely unrelated to SPM; it contains `extendr`, `autoplot`, and "Functional Data Analysis in R" text. Phase 7 sweep must verify the new diagram depicts Phase I (in-control model fit) and Phase II (monitoring with UCL). |
| monitoring/advanced-spm.md | advanced-spm.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows reference curves plus a drift stream with "drift ↑" annotation; Panel 2 names `ewma_scores()` with EWMA/SPE-Q, Run rules/ARL, PC contributions; Panel 3 shows a chart with UCL, drift trajectory, fault contributions, and PC4 label. Faithfully depicts the EWMA drift-detection and fault-diagnosis pipeline. | accurate | yes — advanced SPM with EWMA and contribution charts is a distinct capability; the diagram is essential. | — |
| monitoring/profile-partial-monitoring.md | profile-partial-monitoring.svg | conforms (viewBox 720 ✓, .ttl/.sub/.lab/.sm/.mono ✓, system-ui ✓, role=img ✓, aria-label ✓) | accurate — Panel 1 shows curves plus a sub-domain window with a "bump" annotation; Panel 2 names `spm_phase1()` with slice argvals [lo, hi], Refit FPCA/limits, spm_monitor partial; Panel 3 shows a localised alarm with UCL line and "alarm" label crossing the threshold. Faithfully depicts the partial-domain monitoring pipeline. | accurate | yes — partial-domain monitoring for localised faults is a non-obvious technique; the diagram is essential. | — |
| monitoring/index.md | — | — | — | — | no — the monitoring/ landing page is a section index with navigation tiles. An overview diagram is not warranted; the hero card (cards/monitoring.svg) serves the orientation purpose. | — |

---

## 2. R-era Grep Report

**Scope:** `docs/assets/diagrams/*.svg` AND `docs/**/*.md` (all sections including `reference/` and `examples/`). Patterns searched: `extendr`, `autoplot`, `ggplot`, `%>%`, `<-` (R assignment), `library(`, `require(`, R package names (`fda`, `dplyr`, `tidyr`, `purrr`, `magrittr`, `ggplot2`), `.R` file extension references, plus broader `R package` narrative text.

**Reproducible grep commands:**
```bash
# Diagrams
grep -rn "extendr\|autoplot\|ggplot\|%>%\| <- \|library(\|require(\|zero-copy R" docs/assets/diagrams/
grep -rn "Functional Data Analysis in R" docs/assets/diagrams/
# Prose (all sections)
grep -rn "extendr\|autoplot\|ggplot\|%>%\| <- \|library(\|require(\|\bfda\b\|\bdplyr\b\|\bggplot2\b\|\broahd\b\|\bfdasrvf\b" docs/**/*.md
grep -rn "R package" docs/**/*.md
```

**Full cross-section report (Plan 03 — complete):**

### learn/

**Diagrams** (`docs/assets/diagrams/introduction.svg`, `custom-plotting.svg`, `simulation.svg`, `smoothing.svg`, `derivatives.svg`, `irregular-sampling.svg`):

(no R-era hits in learn/ diagrams)

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/learn/introduction.md | 52 | `mirroring the R package's \`fdata\`` | Legitimate narrative prose — explaining the conceptual origin of the `Fdata` class. Not an R-era leftover to remove; it is an intentional cross-reference explaining fdars's design lineage. |
| docs/learn/introduction.md | 81 | `It mirrors the R package's \`fdata\` S3 class.` | Same as above — intentional design explanation. Retain. |
| docs/learn/introduction.md | 238 | `Unlike R's \`var(fd)\`, fdars does not expose...` | Intentional API comparison note informing Python users. Retain. |
| docs/learn/introduction.md | 567 | `Functional Data Analysis: The R Package \`fda.usc\`. *Journal of Statistical Software*` | Citation in references section for the fda.usc R package. Standard academic citation. Retain. |
| docs/learn/custom-plotting.md | 13 | `mirrors the ggplot2 walkthrough from the R package` | Intentional narrative comparison — the page explicitly translates R/ggplot2 plotting idioms to matplotlib. This ggplot2 mention is the page's stated purpose. **Warrants review**: the page frames its own content as a "translation from ggplot2" which may be R-era framing rather than Python-first authoring. Not a remove-immediately item but flagged for editorial review during the learn/ sweep (Phase 3). |
| docs/learn/custom-plotting.md | 67 | `because ggplot2 maps *columns* of a data frame to aesthetics` | Same page, same framing — part of the ggplot2→matplotlib translation narrative. See above flag. |
| docs/learn/custom-plotting.md | 88 | `This is the matplotlib translation of ggplot2's \`color = group\` aesthetic` | Same. |
| docs/learn/custom-plotting.md | 128 | `In ggplot2 this is \`scale_color_viridis_c\`` | Same. |

| docs/learn/derivatives.md | 502 | `The R package additionally offers \`fdata.gradient()\`, a 5-point-stencil gradient...` | PROSE-OK — admonition box documenting a capability gap (no Python binding yet). Intentional user-guidance note; not an R-era leftover. |
| docs/learn/simulation.md | 404 | `The R package ships a \`sparsify()\` helper...` | PROSE-OK — admonition box documenting a missing Python binding (`sparsify()`). Intentional user-guidance note; retain. |
| docs/learn/irregular-sampling.md | 29 | `The R package ships an \`irregFdata\` class...` | PROSE-OK — admonition box explaining that the Python fdars has no `irregFdata` container and documenting the workaround. Intentional. |
| docs/learn/irregular-sampling.md | 100 | `The R package wraps this in \`sparsify()\`; in Python it is a two-line helper...` | PROSE-OK — API comparison informing Python users of the workaround; intentional design-comparison prose. |
| docs/learn/smoothing.md | 240 | `This is exactly the workflow the R package exposes as \`S.NW(tt, h)\` followed by \`S %*% curve\`.` | PROSE-OK — one-line cross-reference after a Python code example; contextualises the smoothing-matrix idiom for users migrating from R. Retain. |

**Summary for learn/:** No SVG diagrams have R-era hits. The learn/ prose contains two categories of R-era text: (a) design-lineage and citation references in introduction.md (all PROSE-OK, retain); (b) admonition boxes in derivatives.md, simulation.md, and irregular-sampling.md documenting missing Python bindings — all PROSE-OK as intentional user-guidance notes; (c) one API-comparison sentence in smoothing.md (PROSE-OK). custom-plotting.md uses ggplot2 extensively as a comparative framing device — PROSE-OK but flagged for editorial review during Phase 3 to reframe Python-first. No `extendr`, `autoplot`, `%>%`, or hard R code identifiers appear anywhere in learn/.

### represent/

**Diagrams** (`docs/assets/diagrams/fpca.svg`, `elastic-fpca.svg`, `basis-representation.svg`, `andrews-transformation.svg`, `depth-functions.svg`, `streaming-depth.svg`, `distance-metrics.svg`):

(no R-era hits in represent/ diagrams — basis-representation.svg confirmed clean: all text uses current Python fdars API names)

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/represent/andrews-transformation.md | 7 | `The R package ships a dedicated \`andrews_transform()\`, but the Python \`fdars\` has no Andrews-curve function.` | PROSE-OK — warning admonition documenting that Python fdars lacks the R package's `andrews_transform()`. Intentional user-guidance; retain. |

**Summary for represent/:** No SVG diagrams have R-era hits. One prose admonition in andrews-transformation.md (PROSE-OK, documents a missing Python binding). No `extendr`, `autoplot`, `ggplot`, `%>%`, or hard R identifiers.

### align/

**Diagrams** (`docs/assets/diagrams/elastic-alignment.svg`, `advanced-alignment.svg`, `landmark-registration.svg`, `tsrvf.svg`, `alignment-comparison.svg`, `shape-analysis.svg`):

(no R-era hits in align/ diagrams)

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/align/elastic-alignment.md | 699 | `The R package exposes a \`periodic=True\` mode...The \`fdars\` Python bindings enforce fixed boundaries and have no periodic-alignment binding.` | PROSE-OK — admonition documenting a missing Python binding (periodic Karcher mean). Intentional; retain. |
| docs/align/advanced-alignment.md | 325 | `The R package also exposes a \`periodic=True\` circular-rotation mode...` | PROSE-OK — same category as above; one-paragraph admonition documenting a capability gap. Retain. |
| docs/align/alignment-comparison.md | 515 | `vignette("elastic-alignment")...in the R package (https://sipemu.github.io/fdars-r/)` | PROSE-OK — footer cross-reference linking to the R package documentation site for users who want deeper reading. Standard cross-reference; retain. |

**Summary for align/:** No SVG diagrams have R-era hits. Three prose references (all PROSE-OK): two admonitions documenting missing periodic-alignment binding, one cross-reference footer link. No `extendr`, `autoplot`, `ggplot`, `%>%`, or hard R identifiers.

### analyze/

**Diagrams** (`docs/assets/diagrams/tolerance-bands.svg`, `clustering.svg`, `gmm-clustering.svg`, `elastic-clustering.svg`, `outlier-detection.svg`, `seasonal-analysis.svg`, `equivalence-testing.svg`, `covariance-functions.svg`):

(no R-era hits in analyze/ diagrams)

**Prose pages:**

(no R-era hits in analyze/ prose — grep found zero matches)

**Summary for analyze/:** No R-era content anywhere in analyze/ (diagrams or prose). Clean.

### regression/

**Diagrams** (`docs/assets/diagrams/scalar-on-function.svg`, `function-on-scalar.svg`, `classification.svg`, `elastic-regression.svg`, `scalar-on-shape.svg`, `cross-validation.svg`, `regression-diagnostics.svg`, `uncertainty-quantification.svg`, `explainability.svg`, `conformal-prediction.svg`, `conformal-classification.svg`, `robust-regression.svg`):

(no R-era hits in regression/ diagrams)

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/regression/scalar-on-function.md | 396 | `!!! note "Methods available in the R package but not (yet) in Python"` | PROSE-OK — admonition documenting three fdars-R capabilities (`fregre.basis`, pure-R `fregre.pc`, `flm.test`) not yet in the Python binding. Standard capability-gap note; retain. |
| docs/regression/scalar-on-shape.md | 16 | `The R package ships a purpose-built \`scalar.on.shape()\` estimator...` | PROSE-OK — warning admonition explaining that Python fdars has no single `scalar_on_shape` function and documenting the composition approach. Intentional; retain. |
| docs/regression/cross-validation.md | 214 | `single \`cv.fdata\` harness (the R package does), but the \`predict_*\` functions...` | PROSE-OK — inline sentence documenting that Python fdars has no `cv.fdata` equivalent and showing the Python workaround. Retain. |
| docs/regression/conformal-classification.md | 334 | `The R package exposes a \`score.type\` argument (LAC vs. APS) and CV+...` | PROSE-OK — admonition documenting Python binding limitations vs the R package (`score_type`, CV+). Retain. |

**Summary for regression/:** No SVG diagrams have R-era hits. Four prose admonitions documenting Python-vs-R capability gaps (all PROSE-OK; intentional user-guidance). No `extendr`, `autoplot`, `ggplot`, `%>%`, or hard R identifiers.

### monitoring/

**Diagrams** (`docs/assets/diagrams/spm.svg`, `advanced-spm.svg`, `profile-partial-monitoring.svg`):

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/assets/diagrams/spm.svg | 5 | `Functional Data Analysis in R, powered by Rust` | **LEFTOVER** — R-era artifact. This is the subtitle of the entire diagram, declaring it an R-package overview. Must be removed in the Phase 8 monitoring/ sweep when the diagram is redrawn. |
| docs/assets/diagrams/spm.svg | 31 | `autoplot() — visualization` | **LEFTOVER** — `autoplot()` is an R/ggplot2 idiom with no Python fdars equivalent. Hard R-era identifier in the "Explore" capability list. Remove in Phase 8 sweep. |
| docs/assets/diagrams/spm.svg | 55 | `Rust Backend (extendr)` | **LEFTOVER** — `extendr` is the R-to-Rust binding library. The Python equivalent is PyO3. Hard R-era identifier. Remove in Phase 8 sweep (full redraw). |
| docs/assets/diagrams/spm.svg | 56 | `zero-copy R ↔ Rust` | **LEFTOVER** — describes R/Rust interop, not Python/Rust. Remove in Phase 8 sweep (full redraw). |

**Prose pages:**

(no R-era hits in monitoring/ prose — grep found zero matches)

**Summary for monitoring/:** `spm.svg` contains four confirmed LEFTOVER R-era strings (lines 5, 31, 55, 56). This SVG is the only diagram in the entire codebase with genuine R-era leftovers-to-remove. All four hits are inside a single diagram that must be fully redrawn (Phase 8). No other monitoring/ diagrams or prose pages have R-era content.

### examples/

**Diagrams** (`docs/assets/diagrams/ex-sonar-tsrvf.svg`):

(no R-era hits in examples/ diagram)

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/examples/cross-validation.md | 426 | `Statistical computing in functional data analysis: fda.usc. JSS 51(4):1-28.` | PROSE-OK — academic citation for the fda.usc R package in the References section. Standard bibliographic reference; retain. |
| docs/examples/tecator-regression.md | 426 | `Statistical computing in functional data analysis: the R package fda.usc. Journal of Statistical Software 51(4):1-28.` | PROSE-OK — same citation, longer form. Standard bibliographic reference; retain. |
| docs/examples/canadian-weather.md | 391 | `Statistical computing in functional data analysis: fda.usc. JSS 51(4):1-28.` | PROSE-OK — same citation. Standard bibliographic reference; retain. |

**Summary for examples/:** No SVG R-era hits. Three prose references are all bibliographic citations for the fda.usc R package in References sections (all PROSE-OK). No `extendr`, `autoplot`, `ggplot`, `%>%`, or hard R identifiers in examples/ prose.

### reference/

**Diagrams:** None (reference pages have no diagrams — confirmed by audit).

**Prose pages:**

| File | Line | Matched text | Assessment |
|------|------|-------------|------------|
| docs/reference/fdata.md | 15 | `mirroring the R package's \`fdata\` class` | PROSE-OK — one-sentence design-lineage note in the module overview. Intentional; retain. |

**Summary for reference/:** No SVG diagrams. One brief design-lineage reference in fdata.md (PROSE-OK). No `extendr`, `autoplot`, `ggplot`, `%>%`, or hard R identifiers.

### Preliminary Findings Reconciliation

The six named preliminary findings from the ROADMAP/CONTEXT are reconciled below:

| Finding | Status | Evidence |
|---------|--------|----------|
| `spm.svg` — `autoplot()` R-era hit | **CONFIRMED** | `docs/assets/diagrams/spm.svg:31` — `autoplot() — visualization` (LEFTOVER) |
| `spm.svg` — `extendr` R-era hit | **CONFIRMED** | `docs/assets/diagrams/spm.svg:55` — `Rust Backend (extendr)` (LEFTOVER) |
| `basis-representation.svg` — R-era content | **NOT FOUND** | Grep of `docs/assets/diagrams/basis-representation.svg` shows no R-era identifiers. All text uses Python API name `fdata_to_basis_1d`. Prose page `docs/represent/basis-representation.md` uses only Python calls. Preliminary finding not confirmed. |
| `elastic-alignment.svg` — phase-vs-amplitude split unclear | **CONFIRMED (needs verification)** | `docs/assets/diagrams/elastic-alignment.svg:55–61` — warp γ(t) inset present but small and unlabeled as "phase variation." Title/aria-label declare "Separating Amplitude from Phase" but body panels do not show an explicit side-by-side decomposition. Flagged for Phase 5 method-verification. |
| `conformal-prediction.svg` — scalar interval instead of functional band | **CONFIRMED** | `docs/assets/diagrams/conformal-prediction.svg:54–62` — output panel shows `ŷ ± interval` as a scalar constant band, not a time-varying `ŷ(t) ± q(t)` band over [0,T]. LEFTOVER inaccuracy; needs redraw. |
| `scalar-on-function.svg` — β(t) not prominent | **CONFIRMED (partial)** | `docs/assets/diagrams/scalar-on-function.svg:59–64` — β̂(t) present as a small inset in Panel 3, but secondary to the fitted-vs-actual scatter. Not a clear LEFTOVER; flagged for Phase 7 method-verification (verify whether inset is sufficient or panel needs to foreground β(t) more prominently). |

### R-era Grep Report Summary

**Total LEFTOVER items to remove:** 4 — all in `docs/assets/diagrams/spm.svg` (lines 5, 31, 55, 56). Target: Phase 8 monitoring/ sweep (full redraw).

**Total PROSE-OK items:** All other hits across learn/, represent/, align/, regression/, examples/, and reference/ sections are intentional design-lineage notes, capability-gap admonitions, API-comparison notes, or bibliographic citations. None should be deleted by automated sweeps.

**Sections with zero R-era hits:** analyze/ (diagrams and prose), monitoring/ prose only.

---

## 3. Ranked Gap + New-Example List

### Reference-API Coverage Sweep (reference-API sweep)

**Purpose:** Compare the `fdars` exported function surface (16 reference modules) against documented examples (`docs/examples/`) and concept diagrams (`§1` coverage table) to identify under-documented capabilities as candidate new-example targets.

**Method:** For each of the 16 reference modules, the exported functions were enumerated from `src/*_mod.rs` `#[pyfunction]` registrations and `python/fdars/*.py` `__all__` / submodule exports. Each capability was then checked against the 17 example pages and the §1 diagram table.

**Legend:** `has-example? ✓` = at least one docs/examples/ page exercises this capability; `has-accurate-diagram? ✓` = §1 rollup is `accurate` for the concept page(s) associated with this module.

| Module | Key capabilities (exported functions) | has-example? | has-accurate-diagram? | Under-documented capabilities |
|--------|--------------------------------------|-------------|----------------------|-------------------------------|
| `fdata` | `mean_1d/2d`, `center_1d`, `deriv_1d/2d`, `norm_lp_1d`, `geometric_median_1d/2d`, `normalize`, `normalize_with_argvals` | ✓ (used in most examples) | ✓ (introduction.svg) | `geometric_median_*`, `normalize_with_argvals` — no dedicated example demonstrating robust central tendency vs mean |
| `depth` | `fraiman_muniz_1d/2d`, `modal_1d/2d`, `random_projection_1d/2d`, `random_tukey_1d/2d`, `band_1d`, `modified_band_1d`, `modified_epigraph_index_1d`, `functional_spatial_1d/2d`, `kernel_functional_spatial_1d/2d`, `random_projection_deriv_1d` | ✓ (andrews-wine*, depth EX-0005 baseline) | inconsistent (depth-functions.svg needs restyle) | `kernel_functional_spatial_*`, `random_projection_deriv_1d`, `modified_epigraph_index_1d` — no worked example for the advanced depth variants |
| `metric` | `lp_self/cross_1d/2d`, `hausdorff_self/cross_1d/2d`, `dtw_self/cross_1d`, `soft_dtw_*`, `fourier_self/cross_1d`, `hshift_self/cross_1d`, `int_simpson`, `inprod` | ✓ (phoneme-shape, sonar-tsrvf) | ✓ (distance-metrics.svg) | `fourier_self_1d`, `hshift_self_1d` (spectral/horizontal shift metrics) — no dedicated example; `inprod` (inner product) — no example |
| `basis` | `fdata_to_basis_1d`, `basis_to_fdata_1d`, `pspline_fit_1d`, `pspline_fit_gcv`, `select_basis_auto_1d`, `bspline_basis`, `fourier_basis`, `smooth_basis_gcv`, `basis_nbasis_cv`, `fourier_basis_with_period`, `bspline_basis_from_knots`, `construct_bspline_knots`, `fourier_fit_1d`, `select_fourier_nbasis_gcv` | ✓ (canadian-precipitation) | ✓ (basis-representation.svg) | `pspline_fit_gcv`, `smooth_basis_gcv`, `basis_nbasis_cv` — automated smoothing-parameter selection functions have no dedicated worked example beyond the concept page |
| `smoothing` | `nadaraya_watson`, `local_linear`, `local_polynomial`, `knn_smoother`, `optim_bandwidth`, `smoothing_matrix_nw`, `cv_smoother`, `gcv_smoother`, `knn_gcv`, `knn_lcv` | **None** | inconsistent (smoothing.svg needs redraw) | **ENTIRE MODULE under-documented** — no worked example exists for any smoothing function. Core pre-processing step used in virtually every FDA workflow. |
| `simulation` | `simulate`, `gaussian_process`, `covariance_matrix`, `add_error_pointwise`, `add_error_curve`, `eigenfunctions`, `eigenvalues`, `sim_kl` | ✓ (biopharma-monitoring, tecator-monitoring, others) | ✓ (simulation.svg) | `sim_kl`, `eigenfunctions`, `eigenvalues` — Karhunen-Loève simulation primitives exercised internally but no dedicated example foregrounding the KL approach |
| `alignment` | `elastic_align_pair`, `karcher_mean`, `karcher_median`, `robust_karcher_mean`, `elastic_distance`, `srsf_transform/inverse`, `compose_warps`, `invert_warp`, `shape_distance`, `vert_fpca`, `horiz_fpca`, `joint_fpca`, `elastic_regression`, `elastic_logistic`, `landmark_register`, `detect_landmarks`, `tsrvf_transform`, `shape_mean`, `elastic_depth`, `gauss_model`, `bayesian_align_pair`, `phase_boxplot`, `peak_persistence`, and 20+ more | ✓ (growth-alignment, sonar-tsrvf, phoneme-shape) | ✓ (elastic-alignment.svg, others) | `bayesian_align_pair`, `gauss_model` / `joint_gauss_model` (Gaussian process alignment model), `phase_boxplot` (functional boxplot for phase variation), `elastic_partial_match` — advanced alignment functions with no worked example |
| `clustering` | `kmeans_fd`, `fuzzy_cmeans_fd`, `gmm_cluster`, `silhouette_score`, `calinski_harabasz`, `silhouette_score_data`, `calinski_harabasz_data` | ✓ (andrews-wine-clustering) | inconsistent (clustering.svg needs restyle) | `gmm_cluster` — exercised in andrews-wine-clustering but no focused GMM example; `fuzzy_cmeans_fd` — fuzzy membership has no dedicated example |
| `outliers` | `detect_outliers_lrt`, `outliergram`, `magnitude_shape`, `detect_outliers_lrt_with_dist` | ✓ (andrews-wine, andrews-wine-qc) | inconsistent (outlier-detection.svg needs restyle) | `outliergram` — used but no dedicated example explaining the outliergram scatter plot; `magnitude_shape` — used but no standalone worked example |
| `regression` | `fpca`, `fpls`, `fregre_lm`, `fregre_pls`, `fregre_np`, `fregre_l1`, `fregre_huber`, `functional_logistic`, `fosr`, `fanova`, `model_selection_ncomp`, `predict_*`, `fregre_cv`, `bootstrap_ci_*`, `fosr_fpc`, `fregre_np_mixed` | ✓ (tecator-regression, canadian-weather, cross-validation, others) | ✓ (scalar-on-function.svg, function-on-scalar.svg, others) | `fregre_l1` / `fregre_huber` (robust regression) — referenced in concept page, no dedicated worked example; `fosr` / `fanova` (function-on-scalar / functional ANOVA) — concept page present but no worked example with real data; `fregre_np_mixed` — no example |
| `classification` | `fclassif_lda`, `fclassif_qda`, `fclassif_knn`, `fclassif_kernel`, `fclassif_cv`, `fclassif_dd`, `knn_classify_from_distances`, `kernel_classify_from_distances` | ✓ (canadian-weather, sonar-tsrvf) | ✓ (classification.svg) | `fclassif_dd` (depth-vs-depth classification) — no dedicated example demonstrating the depth-based classifier |
| `conformal` | `conformal_fregre_lm`, `conformal_fregre_np`, `conformal_classif`, `conformal_elastic_regression`, `conformal_elastic_pcr`, `conformal_logistic`, `conformal_elastic_logistic` | **None** | inconsistent (conformal-prediction.svg needs redraw) | **ENTIRE MODULE under-documented** — no worked example for any conformal function. Includes EX-0001 (baseline-locked). |
| `tolerance` | `fpca_tolerance_band`, `conformal_prediction_band`, `scb_mean_degras`, `equivalence_test`, `elastic_tolerance_band`, `phase_tolerance_band`, `elastic_tolerance_band_with_config`, `equivalence_test_one_sample`, `exponential_family_tolerance_band` | ✓ (andrews-wine-qc, growth-alignment) | ✓ (tolerance-bands.svg) | `phase_tolerance_band` (phase-aware tolerance band) — no worked example; `exponential_family_tolerance_band`, `equivalence_test_one_sample` — no examples |
| `spm` | `spm_phase1`, `spm_monitor`, `hotelling_t2`, `hotelling_t2_regularized`, `t2_control_limit`, `spe_control_limit`, `ewma_scores`, `western_electric_rules`, `nelson_rules`, `spm_cusum`, `spm_ewma`, `select_ncomp`, `arl0_t2`, `arl1_t2`, and 10+ more | ✓ (biopharma-monitoring, tecator-monitoring, inline-monitoring) | inconsistent (spm.svg is R-era artifact; needs full redraw) | `western_electric_rules`, `nelson_rules` (run-rule methods) — no dedicated example; `spm_cusum` / `spm_ewma` (CUSUM/EWMA charts) — no dedicated example; `arl0_t2`/`arl1_t2` (ARL calculations) — no example |
| `seasonal` | `sazed`, `autoperiod`, `cfd_autoperiod`, `detect_peaks`, `stl_decompose`, `seasonal_strength`, `estimate_period_fft`, `lomb_scargle_fdata`, `matrix_profile_fdata`, `ssa_fdata`, `instantaneous_period`, `detect_seasonality_changes`, `classify_seasonality`, `analyze_peak_timing`, `seasonal_strength_wavelet/windowed`, `estimate_period_acf`, `detect_multiple_periods` | ✓ (canadian-seasonal) | inconsistent (seasonal-analysis.svg needs restyle) | `lomb_scargle_fdata`, `matrix_profile_fdata`, `ssa_fdata`, `detect_multiple_periods`, `classify_seasonality` — advanced period-detection functions with no dedicated worked example |
| `explain` | `fpc_permutation_importance`, `functional_pdp`, `fpc_shap_values`, `significant_regions`, `beta_decomposition`, `influence_diagnostics`, `dfbetas_dffits`, `prediction_intervals`, `loo_cv_press`, `lime_explanation`, `sobol_indices`, `functional_saliency`, `counterfactual_regression`, `prototype_criticism`, `calibration_diagnostics`, and 15+ more | ✓ (explainability-regions, tecator-regression) | ✓ (explainability.svg) | `lime_explanation`, `sobol_indices`, `functional_saliency`, `counterfactual_regression`, `prototype_criticism` — advanced XAI methods with no dedicated example; `calibration_diagnostics` / `expected_calibration_error` — no example |

**Under-documented capability summary (candidates for additional EX-#### rows):**

The most significant under-documented areas across the 16 modules are:

1. **`smoothing` module — zero examples** (critical gap: pre-processing used in every FDA workflow)
2. **`conformal` module — zero examples** (EX-0001 already baseline-locked; the broader conformal elastic/logistic variants also uncovered)
3. **`fosr` / ANOVA (function-on-scalar regression with real data)** — concept page exists, no example
4. **`fclassif_dd` (depth-vs-depth classification)** — distinct method, no example
5. **`spm_cusum` / `spm_ewma` / run rules** — advanced SPM variants no example

---

### ID Schemes

- **`GAP-####`** — a coverage, style, or accuracy gap: a page that warrants a diagram but has none (`missing`), a diagram whose rollup is `inconsistent` (style or accuracy fails), or a significant documentation gap surfaced during section sweeps.
- **`EX-####`** — a new worked example candidate: a capability or method that lacks a worked example and would benefit from one.
- **`Selection`** column — **left blank here; marked by the user before Phase 3 begins** (D-06). Options: `selected`, `deferred`, `dropped`, or `[baseline-locked]` for the five Phase 9 examples.

**Ranking signals (applied to all items below):**
1. Capability has zero accurate diagram AND zero worked example (highest urgency).
2. Method centrality / user value (core methods first).
3. Authoring effort (lower effort → earlier).

**To the user: mark the `Selection` column in this document before Phase 3 begins. Phase 3 planning reads only the selected items. Baseline-locked rows are already committed and do not need marking.**

### Ranked List

**Priority rank key:** `P1` = zero accurate diagram AND zero example (highest); `P2` = core method, one axis covered; `P3` = restyle (style only, accurate content); `P4` = advanced/specialist, at least one axis covered.

| Priority | ID | Type | Section | Description | Zero-example / Zero-accurate-diagram | Method centrality | Authoring effort | Selection |
|----------|----|------|---------|-------------|--------------------------------------|-------------------|------------------|-----------|
| P1 | GAP-0003 | accuracy gap — full redraw | monitoring/ | `spm.svg` — confirmed R-era artifact: `spm.svg:5` "Functional Data Analysis in R, powered by Rust"; `spm.svg:31` `autoplot()`; `spm.svg:55` "Rust Backend (extendr)"; `spm.svg:56` "zero-copy R ↔ Rust". The SVG is a general toolkit overview for the R package, depicts none of the Phase I/II SPM concept (`spm_phase1`, `spm_monitor`, UCL). Needs a **full redraw** (highest priority monitoring gap). | zero accurate diagram + no dedicated SPM example | high — SPM is the core monitoring method | med (full redraw after Phase 8 method verification) | selected |
| P1 | GAP-0004 | accuracy gap — redraw | regression/ | `conformal-prediction.svg` — output panel (`conformal-prediction.svg:54–62`) depicts a scalar constant interval `ŷ ± interval`, not a time-varying functional band `ŷ(t) ± q(t)`. The conformal page covers functional responses; the interval must span the domain [0,T]. Needs a **redraw** of the output panel (needs Phase 7 method verification). | zero accurate diagram + zero conformal examples | high — conformal prediction is the key coverage-guarantee method | med (output panel redraw) | selected |
| P1 | EX-0001 | new example | Phase 9 (baseline-locked) | **Conformal Coverage Guarantee** — `fdars.conformal.conformal_fregre_lm` / `conformal_fregre_np` producing a time-varying prediction band `ŷ(t)±q(t)` with guaranteed coverage, contrasted against a naive scalar interval. Exercises the conformal module (zero examples). | zero examples in conformal module | high | med | [baseline-locked] |
| P1 | GAP-0001 | accuracy gap — redraw | learn/ | `smoothing.svg` — Panel 3 ghost path (`smoothing.svg:48`) reuses Panel 1's noisy polyline verbatim (sequences from L8 onward identical to `smoothing.svg:18`). Misrepresents the noisy reference on the output panel. Needs a **redraw** of the ghost path (or removal). | only diagram for the smoothing page; smoothing module zero examples | high — smoothing is the foundational pre-processing step | low (ghost path fix is a small authoring change) | selected |
| P1 | EX-0006 | new example | smoothing/ | **Kernel Smoothing Workflow** — end-to-end example using `fdars.smoothing` (`nadaraya_watson`, `local_linear`, `optim_bandwidth`, `cv_smoother`) to denoise functional observations, with bandwidth selection and comparison of smoothing methods. Exercises the smoothing module (zero examples across all 17 example pages). | zero examples in smoothing module; zero accurate diagram | high — pre-processing used in virtually every FDA pipeline | med | selected |
| P2 | GAP-0011 | accuracy gap — verify | align/ | `elastic-alignment.svg` — title/aria-label declare "Separating Amplitude from Phase" but Panel 3 warp inset (`elastic-alignment.svg:55–61`) is small and unlabeled as "phase variation." Phase-vs-amplitude decomposition may not be visually clear. Needs Phase 5 method verification. | one accurate diagram (elastic-alignment.svg, with caveat); worked examples exist | high — elastic alignment is the core align/ method | low-med (depends on method verification outcome) | selected |
| P2 | EX-0002 | new example | Phase 9 (baseline-locked) | **Function-on-Scalar Regression** — worked example using `fdars.regression.fosr` to model a functional response from scalar predictors, foregrounding the `β(t)` coefficient curve per predictor. Exercises `fosr`, `fanova`, `predict_fosr`. | no dedicated fosr worked example | high — function-on-scalar is a primary regression model | med | [baseline-locked] |
| P2 | EX-0003 | new example | Phase 9 (baseline-locked) | **Outlier-Detection Workflow** — end-to-end example using `fdars.outliers` (`detect_outliers_lrt`, `outliergram`, `magnitude_shape`) to identify functional outliers, with interpretation guidance (magnitude vs shape vs phase outliers). | existing andrews-wine examples touch outliers but no dedicated diagnostic workflow | high — outlier detection is a primary use-case | med | [baseline-locked] |
| P2 | EX-0004 | new example | Phase 9 (baseline-locked) | **Tolerance Bands vs Conformal Comparison** — side-by-side comparison of `fdars.tolerance.fpca_tolerance_band` and `fdars.conformal.conformal_fregre_lm` bands, illustrating the distributional vs coverage-guarantee distinction. | no conformal examples; tolerance has partial coverage | high — both methods are primary coverage tools | med | [baseline-locked] |
| P2 | EX-0005 | new example | Phase 9 (baseline-locked) | **Functional Depth Centrality Ordering** — example using `fdars.depth.fraiman_muniz_1d` and `modified_band_1d` to rank curves by centrality with a visualization of the depth ordering. Demonstrates functional boxplot / robust summary. | depth is exercised in andrews-wine* but no standalone centrality-ordering example | high — depth is the core rank/outlier primitive | low-med | [baseline-locked] |
| P2 | GAP-0002 | style gap — restyle | represent/ | `depth-functions.svg` — legacy-outlier on style (no CSS class block, no `role=img`, no `aria-label`, inline font-size attributes, inline font-family). Method content is accurate; restyle only, not redraw. | one diagram (inconsistent on style axis); multiple depth examples | high — depth functions are central to outlier detection, boxplots, and robust statistics | med (add `<style>` block, role/aria) | selected |
| P3 | GAP-0005 | style gap — restyle | analyze/ | `elastic-clustering.svg` — non-720 viewBox (`0 0 700 250`), no CSS class block, no `role=img`, no `aria-label`, bare `font-family="sans-serif"`. Restyle to 720×300 conforming layout. Method is accurate. | inconsistent on style axis; worked example exists | med — elastic clustering is primary phase-invariant clustering | med | selected |
| P3 | GAP-0006 | style gap — restyle | analyze/ | `outlier-detection.svg` — non-720 viewBox (`0 0 600 350`), no CSS class block, no `role=img`, no `aria-label`. Restyle to 720×300 (or 720×480) conforming layout. Method is accurate. | inconsistent on style axis; partial example coverage | med — the three-type outlier taxonomy is essential | med | selected |
| P3 | GAP-0007 | style gap — restyle | analyze/ | `covariance-functions.svg` — non-720 viewBox (`0 0 600 425`), no CSS class block, no `role=img`, no `aria-label`. Restyle to 720×480 conforming layout. Method is accurate. | inconsistent on style axis; no dedicated covariance example | med — kernel→smoothness relationship is pedagogically important | med | selected |
| P3 | GAP-0008 | style gap — restyle | analyze/ | `clustering.svg` — viewBox 720 ✓ but no CSS class block, no `role=img`, no `aria-label`, inline font-size/font-weight. Restyle to add `<style>` block and accessibility attrs. Method is accurate. | inconsistent on style axis; worked example exists | med — clustering is a primary analysis entry point | low-med | selected |
| P3 | GAP-0009 | style gap — restyle | analyze/ | `gmm-clustering.svg` — viewBox 720 ✓ but no CSS class block, no `role=img`, no `aria-label`, inline font attributes. Restyle to add `<style>` block and accessibility attrs. Method is accurate. | inconsistent on style axis; partial example coverage | med — GMM clustering is a distinct soft-assignment method | low-med | selected |
| P3 | GAP-0010 | style gap — restyle | analyze/ | `seasonal-analysis.svg` — viewBox 720 ✓ but no CSS class block, no `role=img`, no `aria-label`, inline font-size/font-weight. Restyle to add `<style>` block and accessibility attrs. Method is accurate. | inconsistent on style axis; canadian-seasonal example exists | med — seasonal analysis is a multi-method domain | low-med | selected |
| P4 | EX-0007 | new example | regression/ | **Robust Regression Comparison** — worked example using `fdars.regression.fregre_huber` and `fregre_l1` vs `fregre_lm` on contaminated data, demonstrating breakdown-point advantage. Exercises the robust regression functions that have a concept page but no worked example. | no dedicated robust regression example; concept page exists | med — robust regression is important for contaminated functional data | med | selected |
| P4 | EX-0008 | new example | classification/ | **Depth-vs-Depth Classification** — worked example using `fdars.classification.fclassif_dd` (depth-vs-depth classifier) demonstrating its depth-based decision boundary vs `fclassif_lda`. A distinctly under-documented method with no worked example. | no worked example for `fclassif_dd`; classification is covered elsewhere | med — depth-based classification is a conceptually distinct approach | med | selected |
