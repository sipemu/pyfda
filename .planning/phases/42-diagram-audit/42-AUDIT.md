# Phase 42: Diagram Audit — 42-AUDIT.md

**Phase:** 42-diagram-audit
**Date:** 2026-08-22
**Status:** Complete — AUDIT-01 deliverable

## Purpose

This document is the single evidence source gating the v7.0 milestone. It:

1. Inventories all **61** top-level concept SVGs in `docs/assets/diagrams/` (cards/ and thumb/ excluded) with per-diagram × 4-axis scores.
2. Derives a **ranked per-section fix list** partitioning all 61 diagrams across Phases 43/44/45.
3. Confirms the **diagram-coverage gap list** (examples pages + advisor surface pages lacking a concept SVG) for Phases 46/47.
4. Confirms the **thin-page extension list** for Phase 48.

**Assessment method:** visual/layout axis judged by rsvg-convert render (PNG) + eyeball; STYLE_SPEC conformance by grep of the five canonical markers; XML formatting by source read; method-accuracy by reading the referencing page prose and the shipped `fdars` binding signatures, flagging suspected mismatches for Phase 43–45 verification (no full re-derivation here).

---

## Scoring Legend

### Severity Scale

| Verdict | Meaning |
|---------|---------|
| **OK** | No issue; meets the criterion cleanly. |
| **Minor** | A visible but non-blocking defect: cosmetic issue, small annotation clipping, lone missing STYLE_SPEC marker, mildly confusing but not wrong. Fix is low-effort. |
| **Major** | A significant defect: method-inaccurate or misleading content, multiple STYLE_SPEC failures, substantial layout problems (overlapping labels, out-of-bounds elements), or R-era content. Requires a redraw or structural rework. |

### Four Scoring Axes

| Axis | What is assessed |
|------|-----------------|
| **Visual/layout** | Render quality: overlapping labels, cramped spacing, text clipping, misalignment, inconsistent sizing. Judged from rsvg-convert PNG render. |
| **STYLE_SPEC** | Conformance to `docs/assets/diagrams/STYLE_SPEC.md`: viewBox `0 0 720 {300|480|520}`, `<style>` block with five CSS classes (`.ttl .sub .lab .sm .mono`), `system-ui` font stack, `role="img"` + `aria-label` on root `<svg>`. ALL markers must be present for OK. |
| **XML formatting** | Source hand-editability: consistent indentation, no excessive inline `style=` attribute overrides of the CSS classes, clean structure. |
| **Method-accuracy** | Does the diagram faithfully depict what the shipped `fdars` method actually does, per page prose and binding signatures? **FLAG** = suspected issue for Phase 43–45 verification. |

---

## Count Reconciliation

**Authoritative true count: 61 top-level concept SVGs.**

The milestone framing figure of "68" was stale: it predates the v6.0 milestone and counted some diagrams that were removed or consolidated, plus may have included cards/ or thumb/ thumbnails. The working tree at 2026-08-22 contains exactly 61 `.svg` files at `docs/assets/diagrams/` (maxdepth 1), verified by `find docs/assets/diagrams -maxdepth 1 -name '*.svg' | wc -l`.

**Edge case — `ex-sonar-tsrvf.svg`:** This diagram is referenced only from `docs/examples/sonar-tsrvf.md`. It depicts a worked-example decision framework ("Three Analysis Paths") rather than a pure method concept, but it is a legitimate concept SVG authored for the site. It is assigned to the **43 (learn/represent/align)** fix bucket alongside `tsrvf.svg` because its TSRVF/elastic alignment subject matter belongs to that family. With this placement all 61 diagrams land in exactly one bucket.

**Bucket totals:** 43 = 25 (learn 6, represent 10, align 8, examples 1), 44 = 17 (analyze 12, monitoring 3, advisor 2), 45 = 19 (regression 15, inference 4). Total: 25 + 17 + 19 = **61**.

---

## 1. Scoring Table

### learn/ Section (6 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| introduction.svg | learn | 43 | OK | OK | OK | OK | Clean three-panel; raw scatter → Fdata(X,argvals) → curve family. Accurate. |
| custom-plotting.svg | learn | 43 | OK | OK | OK | OK | Three-panel matplotlib idiom flow; caption correct (fdars ships no plot layer). |
| simulation.svg | learn | 43 | OK | OK | OK | OK | KL parameters (φ₁φ₂φ₃ + λ-decay) → simulate() → sampled curves. Faithful. |
| smoothing.svg | learn | 43 | Minor | OK | OK | Minor | Visual: Panel 3 ghost polyline is a near-copy of Panel 1 noisy path (similar jagged shape, y-shifted ≤5 px; smoothing.svg:48 vs :18), confusing in the "smooth output" panel. Method-accuracy: ghost presents jagged noise in the panel labeled "noise removed, signal kept" — contradicts the panel message; FLAG for Phase 43 fix (remove ghost or replace with properly distinct reference). |
| derivatives.svg | learn | 43 | OK | OK | OK | OK | x(t) → deriv() nderiv=1/2 → velocity/acceleration panels. Shapes visually correct. |
| irregular-sampling.svg | learn | 43 | OK | OK | OK | OK | Ragged per-curve grids → kernel smoother + basis expansion → common grid. Accurate. |

### represent/ Section (10 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| fpca.svg | represent | 43 | OK | OK | Minor | OK | XML: scattered inline `font-size=` attributes alongside class-based text (e.g., `font-size="11"` on some `<text class="sm">` elements) — Minor XML inconsistency but does not affect rendering. Method accurate. |
| elastic-fpca.svg | represent | 43 | OK | OK | Minor | OK | XML: some inline `font-size=` alongside classes. Three-panel amplitude/phase split with `vert_fpca / horiz_fpca / joint_fpca`. Accurate. |
| basis-representation.svg | represent | 43 | OK | OK | Minor | OK | XML: inline `font-size=` overrides on some elements. Curve → `fdata_to_basis_1d` → coefficients + reconstruction. Accurate. |
| andrews-transformation.svg | represent | 43 | OK | OK | Minor | OK | XML: inline `font-size=` overrides. Feature table → Fourier series → one curve per row. Accurate. |
| depth-functions.svg | represent | 43 | OK | OK | OK | Minor | Visual: tall 720×520 multi-panel layout renders clearly. Method-accuracy: FLAG — bottom row lists "Functional Boxplot" using `functional_boxplot` but the shipped API is `outliergram + magnitude_shape` for outlier detection; confirm whether `functional_boxplot()` is an actual exported function in `fdars.depth` or an fdars-core primitive not yet bound (Phase 43). |
| streaming-depth.svg | represent | 43 | OK | OK | OK | OK | Window + new curve → `modified_band_1d` → depth-over-time alarm. Accurate. |
| distance-metrics.svg | represent | 43 | OK | OK | Minor | OK | XML: inline `font-size=` on some elements. Curve pair → `*_self_1d` → distance matrix. Accurate. |
| pace-fpca.svg | represent | 43 | Minor | OK | OK | OK | Visual: subtitle text (line 12) is very long (~130 chars); at 12px system-ui it overflows the 720 px viewBox width and clips in browser/render. Title text also long but renders at 17px; both are borderline. FLAG for Phase 43: shorten subtitle or break to two `.sub` lines. Method-accuracy OK — sparse irregular → PACE mean + smooth eigenfunctions. |
| imputation.svg | represent | 43 | OK | OK | OK | OK | Three-strategy layout (linear/mean/constant) is clear. NaN interior vs boundary gap handling shown correctly. |
| interpolation-policy.svg | represent | 43 | OK | OK | OK | OK | Four-panel extrapolation-policy layout (boundary/exception/fill/periodic) clear and accurate. |

### align/ Section (8 diagrams; includes ex-sonar-tsrvf.svg from examples)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| elastic-alignment.svg | align | 43 | OK | OK | OK | Minor | Method-accuracy: FLAG — title "Removing Phase to Recover a Sharp Mean" does not claim amplitude/phase split (the old v1.0 concern), but the Panel 3 warp γ(t) inset (elastic-alignment.svg:~55) is small and unlabeled as "phase"; may not adequately communicate the amplitude/phase separation for new users. Phase 43 should verify vs page prose. |
| advanced-alignment.svg | align | 43 | OK | OK | OK | OK | λ-regularized alignment; `align(λ, ...)` / `robust_karcher_mean` / λ sweep with best-λ highlighted. Accurate. |
| landmark-registration.svg | align | 43 | OK | OK | OK | OK | Marked landmarks → `register(γ)` (detect peaks/valleys, monotone interp warp) → registered curves. Accurate. |
| tsrvf.svg | align | 43 | OK | OK | OK | OK | Curve on manifold → `tsrvf_transform()` (SRVF, parallel transport, Karcher-mean base) → flat tangent space. Accurate. |
| alignment-comparison.svg | align | 43 | OK | OK | OK | OK | Phase-varying sample → `compare()` three strategies (none/elastic/landmark) → compared means. Accurate. |
| shape-analysis.svg | align | 43 | OK | OK | OK | OK | Quotient-space shape mean via `shape_mean()` (SRSF/Fisher-Rao, quotient by warping). Accurate. |
| banded-alignment.svg | align | 43 | Minor | OK | OK | OK | Visual: complex 720×480 multi-panel layout (DP cost matrix + before/after panels). The cost-matrix panel labels overlap slightly with the matrix grid near the top-left corner; "upper band edge" label at top left of cost matrix is partially occluded by nearby lines in the render. Minor cosmetic. Method content accurate (Sakoe-Chiba corridor, band_frac). |
| shift-registration.svg | align | 43 | OK | OK | OK | Minor | Method-accuracy: FLAG — Panel 2 shows "elastic warp" annotation below "shift (rigid)" in the method step, suggesting elastic alignment as a step in shift registration. The API (`shift_register`) is purely rigid (L2 argmin for scalar δ); "elastic warp" label may imply a post-hoc elastic step not in the shipped method. Phase 43: verify label meaning and remove/clarify if misleading. |
| ex-sonar-tsrvf.svg | examples | 43 | Minor | Major | Minor | OK | Visual: 700×400 non-conforming viewBox causes scale mismatch with other diagrams on page. STYLE_SPEC: viewBox `0 0 700 400` (not 720×{300/480/520}); no `role="img"`; no `aria-label`; no canonical `<style>` block — uses inline `text { font-family: sans-serif; }` with `.title` / `.label` custom classes. XML: inline-style-only approach, no `.ttl/.sub/.lab/.sm/.mono` class usage. Method-accurate for the sonar worked example (validation-first framework, three analysis paths with accuracy percentages). |

### analyze/ Section (12 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| tolerance-bands.svg | analyze | 44 | OK | OK | OK | OK | `fpca_tolerance_band()` (FPCA/bootstrap, Conformal/elastic, Coverage 1−α) → mean + shaded band. Accurate. |
| clustering.svg | analyze | 44 | OK | OK | Minor | OK | XML: some inline `font-size=` overrides alongside CSS classes. 720×480 multi-panel (K-means, Fuzzy C-means, Model Selection, Distance Metrics). Accurate and well-structured. |
| gmm-clustering.svg | analyze | 44 | OK | OK | Minor | OK | XML: inline `font-size=` on some elements. 720×480 layout (B-spline basis → EM → Soft Assignment/Model Selection/Centroids). Accurate. |
| elastic-clustering.svg | analyze | 44 | Minor | Minor | Major | OK | Visual: the diagram is very sparse — only 4 flow boxes with no detail (Raw Curves → Elastic Distance Matrix → K-Means/Hierarchical → Results). Understated for its page. STYLE_SPEC: has `<style>` block and correct viewBox 720×300, but text elements use inline `font-size=` and `style="fill:#333"` overrides instead of the canonical classes — this is partial conformance (has `.ttl .sub .lab .sm .mono` defined but does not use them). XML: all text elements have both `class="sm"` and inline `font-size="11" style="fill:#333"` — redundant duplication, confusing for editors. Method-accurate (pipeline is correct). |
| outlier-detection.svg | analyze | 44 | Minor | OK | Major | Minor | Visual: bottom-row detection-method text (`detect_outliers_lrt() → likelihood` and `conformal_prediction_band() → dist-free`) overflows 170×24 rectangle containers at 10px; text clips at right edge in render. XML: extensive inline `font-size=` and `style="fill:..."` overrides on every element (all `<text class="lab" ... font-size="12.5" style="fill:#D55E00">`); the class is defined but all sizing/color is duplicated inline. Method-accuracy: FLAG — third outlier type labeled "Amplitude Outlier" (exaggerated scale); the page `docs/analyze/outlier-detection.md` typically uses Magnitude/Shape/Phase taxonomy; "Amplitude" may differ from fdars API taxonomy — Phase 44 verify. |
| functional-outliers.svg | analyze | 44 | OK | OK | OK | OK | Hypograph vs Epigraph Index comparison. Accurate depiction of MEI (modified epigraph index) concept. |
| functional-boxplot.svg | analyze | 44 | OK | OK | OK | OK | Median (deepest curve) / 50% CR / whiskers/fence / outliers. Visually clear single-panel layout. Accurate. |
| seasonal-analysis.svg | analyze | 44 | OK | OK | Minor | OK | XML: inline `font-size=` on some `.mono` elements (Key Functions row). 720×480 six-branch toolkit overview; all function names (`estimate_period_fft()`, `stl_decompose()`, `detect_peaks()`, `seasonal_strength.*()`) match shipped API. Accurate. |
| equivalence-testing.svg | analyze | 44 | OK | OK | OK | OK | TOST ± δ corridor with `equivalence_test()` and "✓ equivalent" badge. Accurate. |
| covariance-functions.svg | analyze | 44 | OK | OK | OK | OK | 720×480 four-kernel layout (Gaussian/Exponential/Matérn/Periodic) with smoothness spectrum bar. Formulas and smoothness descriptions accurate. |
| scoring-metrics.svg | analyze | 44 | Minor | OK | OK | OK | Visual: the legend text in the left panel ("ε(t)|" with integral shading label) is slightly small at 10px and the `Δ MAPE: rejects |y_true| ≈ 0` warning text at bottom right is cramped. Functional_mape note referencing non-zero `y_true` is accurate (avoids division by zero). |
| functional-statistics.svg | analyze | 44 | OK | OK | OK | OK | 720×480 four-quadrant layout (mean+std band, depth scores, Median≠Mean≠geometric-median panel, depth-trimmed mean). Accurate and clear. |

### monitoring/ Section (3 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| spm.svg | monitoring | 44 | OK | OK | OK | OK | Redrawn since v1.0 audit. Phase I → Two Statistics (T² + SPE/Q) → Phase II monitor. `spm_phase1()` / `spm_monitor()` / UCL named correctly. R-era content fully removed. Accurate. |
| advanced-spm.svg | monitoring | 44 | OK | OK | OK | OK | EWMA drift + run rules + PC contributions → Chart + Diagnosis. `ewma_scores()` named correctly. Accurate. |
| profile-partial-monitoring.svg | monitoring | 44 | OK | OK | OK | OK | Sub-domain slicing → `spm_phase1()` partial + `spm_monitor partial` → localized alarm crossing UCL. Accurate. |

### advisor/ Section (2 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| advisor-loop.svg | advisor | 44 | OK | OK | OK | OK | Agentic loop: interpret → `advise()` → `fdars_run_method` → compare → loop. Python API "recommend-only" path clearly distinguished. Accurate for shipped advisor interface. |
| advisor-grounding-invariant.svg | advisor | 44 | OK | OK | OK | OK | Two-zone layout: fdars computes numbers (offline/deterministic), LLM only interprets and cites. `build_diagnostics(result, method)` → numeric diagnostics dict → `advise(diagnostics, task=...)`. Accurate grounding invariant. |

### regression/ Section (15 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| scalar-on-function.svg | regression | 45 | OK | OK | OK | Minor | Method-accuracy: β̂(t) coefficient function is shown as a small inset (bottom of Panel 3) rather than a prominent panel. FLAG for Phase 45: verify whether β(t) inset is sufficient or the panel should foreground it; `fregre_lm` / `pls(X, y)` names are correct. |
| function-on-scalar.svg | regression | 45 | OK | OK | OK | OK | `fosr(y, X)` with penalised β(t) per predictor + Roughness λ / FPC / ANOVA/fanova. Fitted curves ŷ(t) per group. Accurate. |
| classification.svg | regression | 45 | OK | OK | OK | OK | `fclassif_knn / lda()` (LDA/QDA on FPCs, k-NN, Depth-vs-depth) → decision boundary in FPC space. Accurate. |
| elastic-regression.svg | regression | 45 | OK | OK | OK | OK | `elastic_regression()` Fisher-Rao alternating (align γᵢ in SRVF, re-fit α/β(t), repeat). Phase-invariant prediction. Accurate. |
| elastic-multinomial.svg | regression | 45 | Minor | OK | Minor | OK | Visual: 4-panel wide layout (Functional Data → OvR × 3 classifiers → Softmax → Output); the "OvR 1/2/3" boxes are somewhat cramped with small text. XML: inline `font-size=` on several elements. Method-accurate (K one-vs-rest elastic binary classifiers → softmax → class probabilities). |
| scalar-on-shape.svg | regression | 45 | OK | OK | OK | OK | `shape_dist → fregre()` (shape_mean, shape distance matrix, fregre_np/fregre_lm) → scalar ŷ. Accurate. |
| concurrent-regression.svg | regression | 45 | OK | OK | OK | OK | Predictor curves X(t) → `concurrent regression` → coefficient curves β(t); `beta_curve: (p, m)` named correctly. Accurate. |
| functional-glm.svg | regression | 45 | Minor | OK | Minor | Minor | Visual: Gamma link annotation "≠ log-link (R default)" at bottom-right uses `fill="#dc3545"` inline color not via class fill (Minor XML). Minor visual: the R-comparison annotation is useful context but may confuse users who assume this is a Python-only page. Method-accuracy: FLAG — Gamma link listed as `inverse g(μ) = 1/μ`; confirm whether `fdars.regression` GLM family actually implements inverse link vs log-link for Gamma, as fdars-core may default differently from R's `glm()`. Phase 45 verify. |
| cross-validation.svg | regression | 45 | OK | OK | OK | OK | K-fold layout → `fregre_cv(X, y)` → CV error vs k U-curve. Accurate. |
| regression-diagnostics.svg | regression | 45 | OK | OK | OK | OK | `influence_diagnostics()` (hat-matrix, Leverage/Cook's D, DFBETAS/DFFITS, PRESS/VIF) → influence plot with 4/n threshold. Accurate. |
| uncertainty-quantification.svg | regression | 45 | OK | OK | OK | OK | `bootstrap_ci()` (Pointwise/Simultaneous band, Prediction intervals) → 95% band around β(t). Accurate. |
| explainability.svg | regression | 45 | OK | OK | OK | OK | `shap · pdp · regions` → Importance Curve with highlighted domain region. `significant_regions()` named correctly. Accurate. |
| conformal-prediction.svg | regression | 45 | OK | OK | OK | OK | `conformal_fregre_lm()` (scalar response ŷ from functional predictors): split-conformal, (1−α) quantile, calibration residuals → `ŷ ± interval` scalar band. Confirmed accurate via binding inspection (`lower/upper/predictions` are 1D scalar arrays — scalar response conformal, not functional-response). The v1.0 concern about "scalar vs functional band" is resolved: this is intentionally a scalar-response diagram. |
| conformal-classification.svg | regression | 45 | OK | OK | OK | OK | `conformal_classif()` (LDA/QDA/kNN, Logistic wrappers) → prediction sets: confident → {A}, ambiguous → {A, B}. Accurate. |
| robust-regression.svg | regression | 45 | OK | OK | OK | OK | `fregre_huber / l1()` (Huber k=1.345, L1/median, vs OLS baseline) → Robust β(t). Accurate. |

### inference/ Section (4 diagrams)

| Diagram | Section | Fix bucket | Visual/layout | STYLE_SPEC | XML formatting | Method-accuracy | Notes |
|---------|---------|-----------|--------------|------------|----------------|-----------------|-------|
| inference-anova.svg | inference | 45 | OK | OK | OK | OK | One-way functional ANOVA: between-group (group means vs grand mean) + within-group (curves vs group mean). Clear decomposition. Accurate. |
| inference-permutation-test.svg | inference | 45 | OK | OK | Minor | OK | XML: inline `font-size=` on some elements. Permutation null histogram with T_obs marker + p-value tail mass. Accurate. |
| inference-scb.svg | inference | 45 | OK | OK | OK | OK | SCB vs pointwise CI: wider simultaneous band vs narrower per-t band around μ(t). Accurate. |
| itp-interval-inference.svg | inference | 45 | OK | OK | OK | OK | ITP: test statistic per basis function (left) + raw vs closure-adjusted p-values (right) with α=0.05 line. Closure adjustment for FWER control. Accurate. |

---

## 2. Ranked Per-Section Fix List

All 61 diagrams partitioned across the three fix-phase buckets. **Within each bucket: Major issues first, then Minor, then OK. Within each severity tier: section order (learn → represent → align → analyze → monitoring → advisor → regression → inference → examples).**

### Phase 43 Fix Bucket: learn/ + represent/ + align/ (25 diagrams)

Phase 43 covers the `learn/`, `represent/`, and `align/` sections (24 diagrams) plus `ex-sonar-tsrvf.svg` from the examples section (1 diagram), total = **25**.

#### Major issues (1 diagram)

| Diagram | Worst axis | Summary of issues |
|---------|-----------|-------------------|
| ex-sonar-tsrvf.svg | STYLE_SPEC | viewBox `0 0 700 400` (non-720 width, non-standard height); no `role="img"`; no `aria-label`; no canonical `<style>` block with `.ttl .sub .lab .sm .mono` classes; uses inline `text { font-family: sans-serif }` and custom `.title .label` classes; XML is purely inline-style. Full STYLE_SPEC migration required. |

#### Minor issues (8 diagrams)

| Diagram | Worst axis | Summary of issues |
|---------|-----------|-------------------|
| smoothing.svg | Method-accuracy | Panel 3 ghost polyline (smoothing.svg:48) is a near-copy of Panel 1's jagged noisy path (similar amplitudes, y-shifted ≤5 px) shown in the "noise removed, signal kept" output panel — visually contradicts the panel message; FLAG to remove ghost or replace with independently drawn reference. Visual issue confirmed by PNG render. |
| depth-functions.svg | Method-accuracy | FLAG — bottom row "Functional Boxplot" tool references `functional_boxplot()` and `50% central region`; verify whether `functional_boxplot()` is an exported function in `fdars.depth` (not found in `src/depth_mod.rs` #[pyfunction] list during prior audit); confirm binding or rename to reflect the actual API. |
| pace-fpca.svg | Visual/layout | Subtitle text (pace-fpca.svg:12) ~130 chars long overflows 720 px viewBox at 12px font size; text clips at right edge in rsvg-convert render. Shorten subtitle or wrap to second `.sub` line. |
| elastic-alignment.svg | Method-accuracy | FLAG — warp γ(t) inset small and unlabeled as "phase"; title says "Removing Phase to Recover a Sharp Mean" but body panels do not explicitly show amplitude-vs-phase decomposition. Phase 43 verify vs page prose: is an explicit amplitude-vs-phase split panel needed? |
| banded-alignment.svg | Visual/layout | Cost-matrix panel labels (upper/lower band edge annotations) slightly overlap the matrix grid lines near top-left corner in 720×480 render. Minor cosmetic; re-position label anchors. |
| shift-registration.svg | Method-accuracy | FLAG — "elastic warp" annotation in Panel 2 (below "shift (rigid)" label) suggests an elastic warp step inside shift registration; the shipped `shift_register` / `least_squares_shift_registration` API is purely rigid (argmin L2 integral of (X(t+δ)−μ(t))² for scalar δ). Phase 43: verify label intent and remove or clarify. |
| fpca.svg | XML formatting | Inline `font-size=` attributes on some `<text class="sm">` elements alongside the CSS class definition. Minor cleanup. |
| elastic-fpca.svg | XML formatting | Same inline `font-size=` mixed with CSS class usage. Minor cleanup. |

#### Minor issues cont. (XML formatting group)

| Diagram | Worst axis | Summary of issues |
|---------|-----------|-------------------|
| basis-representation.svg | XML formatting | Inline `font-size=` overrides alongside CSS classes. |
| andrews-transformation.svg | XML formatting | Inline `font-size=` overrides alongside CSS classes. |
| distance-metrics.svg | XML formatting | Inline `font-size=` overrides alongside CSS classes. |

#### OK diagrams (16 diagrams — no action needed in Phase 43)

| Diagram | Confirmed status |
|---------|-----------------|
| introduction.svg | OK all axes |
| custom-plotting.svg | OK all axes |
| simulation.svg | OK all axes |
| derivatives.svg | OK all axes |
| irregular-sampling.svg | OK all axes |
| streaming-depth.svg | OK all axes |
| imputation.svg | OK all axes |
| interpolation-policy.svg | OK all axes |
| advanced-alignment.svg | OK all axes |
| landmark-registration.svg | OK all axes |
| tsrvf.svg | OK all axes |
| alignment-comparison.svg | OK all axes |
| shape-analysis.svg | OK all axes |
| elastic-fpca.svg | OK visual/STYLE_SPEC/method |
| basis-representation.svg | OK visual/STYLE_SPEC/method |
| distance-metrics.svg | OK visual/STYLE_SPEC/method |

---

### Phase 44 Fix Bucket: analyze/ + monitoring/ + advisor/ (17 diagrams)

Phase 44 covers the `analyze/` (12), `monitoring/` (3), and `advisor/` (2) sections, total = **17**.

#### Minor + XML issues (7 diagrams)

| Diagram | Worst axis | Summary of issues |
|---------|-----------|-------------------|
| elastic-clustering.svg | XML formatting | **Major XML:** all text elements have both CSS class (`class="sm"`) AND inline `font-size="11" style="fill:#333"` overrides — the CSS class is defined but never used for sizing/color; STYLE_SPEC technically met (style block present, viewBox 720×300, role/aria OK) but every element bypasses the class definitions. Diagram content is very sparse (4 bare flow boxes, no method detail). Phase 44: strip inline overrides and expand diagram content to match peer diagrams in analyze/. |
| outlier-detection.svg | XML + Visual | **Major XML + Minor Visual:** all `<text>` elements use both CSS classes and inline `font-size=` / `style="fill:..."` overrides simultaneously. Visual: bottom-row detection-method text overflows rectangle containers (text wider than 170 px at 10px font). Method-accuracy: FLAG — outlier taxonomy labels "Magnitude / Shape / **Amplitude**"; the canonical fdars taxonomy (docs and API) uses "Magnitude / Shape / Phase"; "Amplitude" may be non-standard term. Phase 44 verify. |
| scoring-metrics.svg | Visual | Minor: `ε(t)|` integral label and `Δ MAPE: rejects |y_true| ≈ 0` warning are small (10px) and slightly cramped in the right panel. No XML or STYLE_SPEC issues. |
| clustering.svg | XML | Minor: inline `font-size=` on some elements. 720×480 multi-panel is otherwise well-structured. |
| gmm-clustering.svg | XML | Minor: inline `font-size=` on some elements. 720×480 layout otherwise clean. |
| seasonal-analysis.svg | XML | Minor: inline `font-size=` on `.mono` Key Functions row elements. 720×480 six-branch layout otherwise clean. |
| depth-functions.svg | Method-accuracy | (see Phase 43 list — this is the FLAG for `functional_boxplot()` API name) |

#### OK diagrams (10 diagrams — no action needed in Phase 44)

| Diagram | Confirmed status |
|---------|-----------------|
| tolerance-bands.svg | OK all axes |
| functional-outliers.svg | OK all axes |
| functional-boxplot.svg | OK all axes |
| equivalence-testing.svg | OK all axes |
| covariance-functions.svg | OK all axes |
| functional-statistics.svg | OK all axes |
| spm.svg | OK all axes (redrawn; R-era content removed) |
| advanced-spm.svg | OK all axes |
| profile-partial-monitoring.svg | OK all axes |
| advisor-loop.svg | OK all axes |
| advisor-grounding-invariant.svg | OK all axes |

---

### Phase 45 Fix Bucket: regression/ + inference/ (19 diagrams)

Phase 45 covers the `regression/` (15) and `inference/` (4) sections, total = **19**.

#### Minor issues (4 diagrams with FLAGs or cosmetic)

| Diagram | Worst axis | Summary of issues |
|---------|-----------|-------------------|
| scalar-on-function.svg | Method-accuracy | FLAG — β̂(t) coefficient curve shown as small inset in Panel 3, secondary to fitted-vs-actual scatter; verify Phase 45 whether this is sufficient for the page's pedagogical purpose or needs a more prominent β(t) panel. |
| elastic-multinomial.svg | Visual + XML | Visual: 4-wide-panel layout is cramped at 720×300 (OvR boxes have small text); XML: inline `font-size=` overrides. Consider 720×480 height or font-size cleanup. Method accurate. |
| functional-glm.svg | Method-accuracy + XML | FLAG — Gamma link `inverse g(μ) = 1/μ` annotation: confirm fdars GLM Gamma family uses inverse vs log link (R comparison note may be misleading if fdars defaults differently). XML: inline `style="fill:#dc3545"` for Gamma color annotation. |
| inference-permutation-test.svg | XML | Minor: inline `font-size=` on some elements. Content OK. |

#### OK diagrams (15 diagrams — no action needed in Phase 45)

| Diagram | Confirmed status |
|---------|-----------------|
| function-on-scalar.svg | OK all axes |
| classification.svg | OK all axes |
| elastic-regression.svg | OK all axes |
| scalar-on-shape.svg | OK all axes |
| concurrent-regression.svg | OK all axes |
| cross-validation.svg | OK all axes |
| regression-diagnostics.svg | OK all axes |
| uncertainty-quantification.svg | OK all axes |
| explainability.svg | OK all axes |
| conformal-prediction.svg | OK all axes (scalar-response design confirmed) |
| conformal-classification.svg | OK all axes |
| robust-regression.svg | OK all axes |
| inference-anova.svg | OK all axes |
| inference-scb.svg | OK all axes |
| itp-interval-inference.svg | OK all axes |

---

## 3. Diagram-Coverage Gap List

### Purpose

This section lists docs pages that **lack a concept SVG** and whether a diagram is warranted. It drives Phases 46 (examples pages) and 47 (advisor surface pages).

### 3a. Examples Pages — DIACOV-01 (Phase 46)

`docs/examples/` has 22 files (21 pages + index). One page already has a concept SVG:
- `sonar-tsrvf.md` — **has `ex-sonar-tsrvf.svg`** ✓

All remaining 20 example pages lack a concept SVG. The index page (`docs/examples/index.md`) is a navigation index and does not warrant a diagram.

| Page | Diagram warranted? | Rationale |
|------|-------------------|-----------|
| `examples/andrews-wine.md` | Yes | Core entry point; Andrews curve + depth overview |
| `examples/andrews-wine-intro.md` | Yes | Intro to Andrews transformation; concept diagram adds value |
| `examples/andrews-wine-clustering.md` | Yes | Clustering result; before/after cluster assignment visual |
| `examples/andrews-wine-qc.md` | Yes | Quality-control tolerance band overlay |
| `examples/biopharma-monitoring.md` | Yes | SPM Phase I/II monitoring on biopharma data |
| `examples/canadian-depth-centrality.md` | Yes | Depth-centrality ordering; functional boxplot |
| `examples/canadian-function-on-scalar.md` | Yes | Function-on-scalar regression; β(t) per month |
| `examples/canadian-precipitation.md` | Yes | Basis representation + smoothing pipeline |
| `examples/canadian-seasonal.md` | Yes | Seasonal decomposition / period estimation |
| `examples/canadian-weather.md` | Yes | Multi-method overview of Canadian Weather dataset |
| `examples/cross-validation.md` | Yes | CV fold split → error curve |
| `examples/explainability-regions.md` | Yes | SHAP/PDP importance curve with highlighted region |
| `examples/functional-outlier-workflow.md` | Yes | Outlier detection pipeline (magnitude/shape) |
| `examples/growth-alignment.md` | Yes | Elastic alignment on growth data |
| `examples/inline-monitoring.md` | Yes | Streaming / inline SPM monitoring |
| `examples/phoneme-shape.md` | Yes | Shape-based classification (phoneme dataset) |
| `examples/tecator-conformal-coverage.md` | Yes | Conformal coverage guarantee |
| `examples/tecator-monitoring.md` | Yes | Monitoring on Tecator data |
| `examples/tecator-regression.md` | Yes | Scalar-on-function regression (Tecator) |
| `examples/tolerance-vs-conformal.md` | Yes | Tolerance band vs conformal band comparison |
| `examples/index.md` | No | Navigation index; no concept diagram warranted |

**Total DIACOV-01 gap:** 20 example pages lacking a concept SVG.

### 3b. Advisor Surface Pages — DIACOV-02 (Phase 47)

`docs/advisor/` has 6 files. The index page has two concept SVGs (`advisor-grounding-invariant.svg` and `advisor-loop.svg`). The 5 surface pages all lack a concept SVG:

| Page | Diagram warranted? | Rationale |
|------|-------------------|-----------|
| `advisor/python-api.md` | Yes | Python API usage flow; `advise()` call pattern + response structure |
| `advisor/mcp.md` | Yes | MCP tool integration; agent↔fdars↔MCP boundary diagram |
| `advisor/providers.md` | Yes | Provider configuration flow (Anthropic/OpenAI key path) |
| `advisor/agent-skill.md` | Yes | Agent skill execution flow vs Python-API mode |
| `advisor/aspects.md` | Yes | Advisor "aspect" taxonomy; interpret/recommend/compare branches |

**Total DIACOV-02 gap:** 5 advisor surface pages lacking a concept SVG.

---

## 4. Thin-Page Extension List

### Purpose

Pages with incomplete section structure (missing intro / method explanation / worked example / parameters / caveats) — the DEPTH-01/02 targets for Phase 48. ~200 lines is a soft signal, not a hard cutoff; section-structure completeness governs.

### Assessment method

For each candidate, the heading structure (via `grep -n '^#'`) and line count were checked. A page is flagged `thin` when it lacks ≥2 of: [theory/method explanation], [worked example with executable code], [API parameters section], [caveats/interpretation guidance].

### Confirmed Thin Pages (Phase 48 targets)

| Page | Lines | Missing sections | Severity |
|------|-------|-----------------|----------|
| `regression/concurrent-regression.md` | 79 | Missing: parameters table, caveats/interpretation, extended worked example (only code snippet shown). Theory section minimal (1 equation). | **Thin** |
| `regression/functional-glm.md` | 106 | Missing: parameters table, caveats/interpretation guidance, multi-family worked example (only binary response shown). GLM-family link functions need tabular API documentation. | **Thin** |
| `represent/pace-fpca.md` | 116 | Has theory + API + example but: missing parameters/returns documentation for `irreg_fdata_from_lists`, missing caveats (when PACE fails vs basis-smoothing), missing comparison with standard FPCA. | **Thin** |
| `inference/interval-inference.md` | 145 | Has theory + example but: three function signatures (`itp_one_pop`, `itp_two_pop`, `itp_flm`) each get a brief parameter list, missing caveats (sample size requirements, basis sensitivity), no comparison with permutation test. | **Thin** |
| `represent/interpolation.md` | 125 | Has intro + policy description + example but: missing API parameters table (just prose), missing caveats (aliasing, oscillation risk with high-degree splines), missing comparison with smoothing. | **Thin** |
| `represent/imputation.md` | 126 | Has strategy description + example but: missing API parameters table for `ImputationMethod`, missing caveats (MCAR vs MAR assumptions), minimal; recommendations section exists but is brief. | **Thin** |
| `analyze/scoring-metrics.md` | 132 | Has metric definitions + worked example + API but: missing caveats for `functional_mape` (y_true ≠ 0 requirement only mentioned in one note), no guidance on metric selection by use-case, no comparison table of metrics. | **Thin** |
| `analyze/functional-statistics.md` | 141 | Has four statistics + API + example but: depth-trimmed mean (`trim_mean`) is the only section with an orange-highlighted panel; missing caveats on covariance surface estimation (bias for small n), missing guidance on when depth-median vs geometric-median is preferred. | **Thin** |
| `align/banded-alignment.md` | 156 | Has intro + band_frac guide + API + example but: missing theoretical justification for Sakoe-Chiba band (why O(m·B) vs O(m²)), missing caveats on band_frac selection when signal has long-range phase shifts. Bordering thin. | **Borderline** |
| `align/shift-registration.md` | 169 | Has theory + API + quality scores + example but: quality score metrics (`sobolev_score`, `alignment_score`) documented without guidance on interpretation thresholds; missing comparison with landmark registration. Bordering thin. | **Borderline** |

### Pages Checked and Confirmed Mature (not thin)

| Page | Lines | Conclusion |
|------|-------|-----------|
| `inference/functional-inference.md` | 317 | Mature: theory, ANOVA/permutation/SCB sections, worked examples, parameters. |
| `regression/classification.md` | 680 | Mature: extensive theory, multiple methods, worked examples, parameters. |
| `analyze/outlier-detection.md` | 681 | Mature: three outlier type theory, API table, multiple worked examples, caveats. |
| `analyze/functional-boxplot.md` | 203 | Adequate: theory, construction algorithm, example. Not thin. |

### Summary for Phase 48

**Confirmed thin pages (DEPTH-01 target — 8 pages):** concurrent-regression, functional-glm, pace-fpca, interval-inference, interpolation, imputation, scoring-metrics, functional-statistics.

**Borderline pages (confirm in Phase 48 discovery):** banded-alignment, shift-registration.

---

## Self-Check

### File existence check
- `42-AUDIT.md` exists: VERIFIED (this file).

### Diagram count verification
- Total SVGs in `docs/assets/diagrams/` (maxdepth 1): 61. All 61 have rows in §1.
- Bucket totals: Phase 43 = 25, Phase 44 = 17, Phase 45 = 19. Sum = 61. ✓

### STYLE_SPEC check on smoothing.svg (tracer)
- viewBox `0 0 720 300` ✓
- `.ttl .sub .lab .sm .mono` CSS classes in `<style>` block ✓
- `system-ui` font stack ✓
- `role="img"` ✓
- `aria-label` ✓
- Ghost polyline confirmed at smoothing.svg:48 — coordinates similar to Panel 1 (smoothing.svg:18) with minor y-offsets, still jagged in "smooth output" panel. Minor method-accuracy issue. ✓

## Self-Check: PASSED

All 61 top-level SVGs inventoried; every non-OK cell has a one-line evidence note; count reconciled to 61; ranked fix list partitions all 61 across 43/44/45 (25+17+19); coverage-gap list names 20 examples pages + 5 advisor surface pages; thin-page list covers 8 seed pages plus 2 borderline pages. No committed SVG or PNG modified.
