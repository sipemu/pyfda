---
phase: 46-diagram-coverage-examples
plan: "02"
subsystem: docs/examples
tags: [diagrams, svg, examples, diacov-01, tecator, monitoring, cross-validation, explainability, outliers, growth, phoneme, tolerance]
status: complete

requires:
  - 46-01

provides:
  - ex-tecator-regression.svg
  - ex-tecator-conformal-coverage.svg
  - ex-tecator-monitoring.svg
  - ex-biopharma-monitoring.svg
  - ex-inline-monitoring.svg
  - ex-cross-validation.svg
  - ex-explainability-regions.svg
  - ex-functional-outlier-workflow.svg
  - ex-growth-alignment.svg
  - ex-phoneme-shape.svg
  - ex-tolerance-vs-conformal.svg

affects:
  - docs/examples/tecator-regression.md
  - docs/examples/tecator-conformal-coverage.md
  - docs/examples/tecator-monitoring.md
  - docs/examples/biopharma-monitoring.md
  - docs/examples/inline-monitoring.md
  - docs/examples/cross-validation.md
  - docs/examples/explainability-regions.md
  - docs/examples/functional-outlier-workflow.md
  - docs/examples/growth-alignment.md
  - docs/examples/phoneme-shape.md
  - docs/examples/tolerance-vs-conformal.md

tech-stack:
  added: []
  patterns:
    - hand-authored inline SVG (720-wide viewBox, STYLE_SPEC canonical style block)
    - workflow/pipeline genre per ex-sonar-tsrvf.svg precedent
    - .fdars-diagram embed near page top before first ## heading
    - svgo@3.3.4 idempotence gate + rsvg-convert PNG render check
    - heights: 480 for multi-panel workflows, 300 for single-row summaries

key-files:
  created:
    - docs/assets/diagrams/ex-tecator-regression.svg
    - docs/assets/diagrams/ex-tecator-conformal-coverage.svg
    - docs/assets/diagrams/ex-tecator-monitoring.svg
    - docs/assets/diagrams/ex-biopharma-monitoring.svg
    - docs/assets/diagrams/ex-inline-monitoring.svg
    - docs/assets/diagrams/ex-cross-validation.svg
    - docs/assets/diagrams/ex-explainability-regions.svg
    - docs/assets/diagrams/ex-functional-outlier-workflow.svg
    - docs/assets/diagrams/ex-growth-alignment.svg
    - docs/assets/diagrams/ex-phoneme-shape.svg
    - docs/assets/diagrams/ex-tolerance-vs-conformal.svg
  modified:
    - docs/examples/tecator-regression.md (+2 lines: embed)
    - docs/examples/tecator-conformal-coverage.md (+2 lines: embed)
    - docs/examples/tecator-monitoring.md (+2 lines: embed)
    - docs/examples/biopharma-monitoring.md (+2 lines: embed)
    - docs/examples/inline-monitoring.md (+2 lines: embed)
    - docs/examples/cross-validation.md (+2 lines: embed)
    - docs/examples/explainability-regions.md (+2 lines: embed)
    - docs/examples/functional-outlier-workflow.md (+2 lines: embed)
    - docs/examples/growth-alignment.md (+2 lines: embed)
    - docs/examples/phoneme-shape.md (+2 lines: embed)
    - docs/examples/tolerance-vs-conformal.md (+2 lines: embed)

decisions:
  - "Tecator regression: 4-panel flow (deriv_1d → 3-method comparison → beta(λ) + significant_regions_from_se → functional_logistic); all 3 method results shown with R² values"
  - "Conformal coverage: 3-panel (split setup → conformal_fregre_lm band → single-split + multi-split coverage); 720×300 single-row sufficient"
  - "Tecator monitoring: 3-row flow (Phase I FPCA + select_ncomp → Phase II spm_monitor + run rules + ewma_scores → t2_pc_contributions diagnosis)"
  - "Biopharma monitoring: fpca score plot panel added (PC1=yield/PC2=timing) before Phase I/II monitoring; fregre_cv yield prediction in row 2"
  - "Inline monitoring: simulate KL → Phase I calibration → fault injection along φ₁ → power curve + F1 vs fault magnitude"
  - "Cross-validation: emphasizes the in-sample vs OOF R² gap; fregre_cv shown as the primary tool; 3-method OOF comparison at bottom"
  - "Explainability regions: 5-method convergence diagram with a result-convergence green panel showing all 5 point at 930 nm; PDP as addendum"
  - "Functional outlier workflow: two-panel result (MS-plot catches magnitude, outliergram catches shape), explicit 'MISSED' label on each to show complementarity"
  - "Growth alignment: 3-row flow (velocity → alignment_quality phase split → elastic_align_pair → karcher_mean → FPCA → gammas → equivalence_test); karcher_mean convergence note included"
  - "Phoneme shape: cautionary arc (high per-class phase fraction → seems to favour elastic → BUT L² wins purity 84% vs elastic 38%); explicit warning note in bottom"
  - "Tolerance vs conformal: direct two-panel comparison with tighter/wider labels; use_case rule at bottom"

metrics:
  duration: "~8 minutes"
  completed: "2026-08-22"
  tasks: 3
  commits: 3
  files: 22

estimate:
  tokens: 120000

actuals:
  tokens: 98000
  tasks: 3
  commits: 3
---

# Phase 46 Plan 02: Diagram Coverage — Examples Wave 2 Summary

**One-liner:** 11 method-accurate workflow SVGs authored across tecator (regression/conformal/monitoring), monitoring (penicillin/inline), and misc (cross-validation/explainability/outliers/growth/phoneme/tolerance) example pages — completing 20/20 DIACOV-01 gap coverage.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Tecator family — 3 SVGs (regression, conformal, monitoring) | 8a03de8 | 3 SVGs + 3 .md pages |
| 2 | Monitoring family — 2 SVGs (biopharma, inline) | 419a471 | 2 SVGs + 2 .md pages |
| 3 | Misc group — 6 SVGs (cv, explain, outlier, growth, phoneme, tolerance) | 3fc1b15 | 6 SVGs + 6 .md pages |

## New SVG Files and Their Depicted Method Arcs

### Task 1 (Tecator Family)

**`ex-tecator-regression.svg`** (720×480)
Method arc: `load_tecator` → `deriv_1d(nderiv=2)` (2nd derivative, removes baseline) → 170/70 train/test split → `fregre_lm` (n_comp=12, R²≈0.945) + `fregre_pls` (n_comp=5, R²≈0.949) + `fregre_np` via `lp_cross_1d` N-W (R²≈0.980) → `fregre_pls` beta_t coefficient curve + `significant_regions_from_se` (6 bands, 930 nm C–H overtone strongest) → `functional_logistic` (n_comp=5, 100% in-sample accuracy).

**`ex-tecator-conformal-coverage.svg`** (720×300)
Method arc: `load_tecator` → `conformal_fregre_lm` (ncomp=8, cal_fraction=0.3, α=0.10) → train/calibrate/test split → variable-width prediction bands (lower/upper) → single split coverage ≈90–93% → 60 random splits: distribution concentrates at or above 0.90 nominal (one-sided conservative guarantee).

**`ex-tecator-monitoring.svg`** (720×480)
Method arc: `load_tecator` (raw absorbance) → in-spec/out-of-spec split (fat < 25%) → `spm_phase1(ncomp=10, α=0.01)` + `select_ncomp(cumulative_variance, 0.90)` → 1 PC retained → T² UCL + SPE UCL → `spm_monitor` Phase II → `western_electric_rules` + `nelson_rules` (WE1 dominant) → `ewma_scores(λ=0.2)` MEWMA-type stat → `t2_pc_contributions` (PC3 dominates worst sample; points to 930–1000 nm fat band).

### Task 2 (Monitoring Family)

**`ex-biopharma-monitoring.svg`** (720×480)
Method arc: `load_penicillin` (46 batches, 40 normal/6 faulty, synthetic) → `fpca(n_comp=3)` (PC1=yield level, PC2=growth timing) → `spm_phase1` + `select_ncomp(var-90%)` on 30 random normal batches → `spm_monitor` Shewhart T²/SPE (6/6 faulty detected) + `ewma_scores(λ=0.2)` MEWMA (6/6 detected) → false-alarm check on held-out normal batches (precision/recall/F1) → partial trajectory time-to-detection at 10 checkpoints (faulty breach limit early) → `fregre_cv` + `fregre_lm` yield prediction from early 200h window.

**`ex-inline-monitoring.svg`** (720×480)
Method arc: `simulate(200, t, n_basis=8, efun_type="fourier", eval_type="exponential")` + smooth mean function → `spm_phase1` + `select_ncomp(var-90%)` (Phase I calibration) → fresh 200 in-control curves (false-positive check: FPR≈4–6%, above nominal 1% due to finite Phase I) → `eigenfunctions(φ₁)` fault injection at 0, 0.5, 1, 2, 3σ → `spm_monitor` Shewhart vs `ewma_scores(λ=0.2)` MEWMA power curve (EWMA detects earlier on sustained shifts) → F1 vs fault magnitude (EWMA crosses F1>0.5 at smaller fault = minimum detectable fault).

### Task 3 (Misc Group)

**`ex-cross-validation.svg`** (720×300)
Method arc: `load_tecator` + `deriv_1d(nderiv=2)` → `fregre_cv(k_min=1, k_max=25, n_folds=5)` → optimal_k + OOF predictions + CV error curve (dip marks best k) → in-sample R² monotonically rises vs honest OOF R² peaks then falls (optimism gap visualized) → three-method OOF comparison: FPC-LM≈0.956 / PLS≈0.956 / NP≈0.978 (NP edges ahead; both linear methods tied).

**`ex-explainability-regions.svg`** (720×480)
Method arc: `fregre_lm(n_comp=5)` on Tecator D2 → `beta_t` coefficient curve → `bootstrap_ci_fregre_lm(n_boot=200, α=0.05)` → `significant_regions(lower, upper)` (CI excludes zero → 930 nm band strongest) → 4 additional explainers: `pointwise_importance` (normalized importance peaks at 930 nm) + `functional_saliency` (mean |saliency| → same region) + `domain_selection(window_width=5)` (sliding scan brackets 930 nm core) + `beta_decomposition` (PC1/PC2 carry most variance, dictate 930 nm feature) → convergence panel (all 5 methods agree) → `functional_pdp(component=0)` (monotone linear sweep confirms linear model).

**`ex-functional-outlier-workflow.svg`** (720×300)
Method arc: `simulate(45, n_basis=6, seed=5)` normal + 3 magnitude outliers (shift +6σ) + 3 shape outliers (sin(11πt) wiggle, normal level) → `magnitude_shape(X)` → MS-plot MO vs VO axis (magnitude outliers fly right; shape outliers tangled with normal cloud, MISSED) → `outliergram(X)` → MBD vs MEI parabola (shape outliers drop below; magnitude outliers not flagged). Each tool catches what the other misses.

**`ex-growth-alignment.svg`** (720×480)
Method arc: `load_growth` (93 children) → `deriv_1d(nderiv=1)` velocity curves → `alignment_quality(V, age)` (full: ratio≈0.57; pubertal age≥8: ratio≈0.82 — dominant spread is WHEN spurt happens) → `elastic_align_pair(c1, c2, age)` pairwise (γ bends at spurt region) → `karcher_mean(Vp, ap, max_iter=25)` (cross-sectional mean peak 6.4 cm/yr smeared → aligned template peak 8 cm/yr sharp) → `fpca` before/after (alignment redistributes variance; amplitude structure emerges) → `km["gammas"]` as timing scores by sex (boys above diagonal = later; girls below = earlier; boys 13.5 yr vs girls 11.4 yr, Δ=2.1 yr) → `equivalence_test(δ=0.5, nb=500)` (p=1.0, NOT equivalent).

**`ex-phoneme-shape.svg`** (720×480)
Method arc: `load_phoneme` (5 classes: aa/ao/dcl/iy/sh; 256 freq bins) → `alignment_quality` per class (phase fraction 16–28%, all above 15% threshold → seems to favour elastic; but per-class misleads pooled analysis) → `shape_mean` per class (elastic Karcher mean, 5 distinct canonical profiles) → `lp_self_1d(p=2.0)` L² distance matrix (clean block-diagonal) vs `shape_self_distance_matrix` elastic (muddy — warp collapses peak positions) → MDS embeddings (L²: tight clusters; elastic: classes bleed) → `kmedoids_from_distances` purity: L²=84% vs elastic=38% vs `hierarchical_cut`=48%. L² wins: peak positions ARE the signal.

**`ex-tolerance-vs-conformal.svg`** (720×300)
Method arc: `load_canadian_weather` (35 stations, 365 days, temperature) → `fpca_tolerance_band(ncomp=4, nb=600, coverage=0.90)` (FPCA model-based bootstrap; tighter, efficient when model fits) vs `conformal_prediction_band(coverage=0.90)` (distribution-free; wider outer envelope, coverage guaranteed regardless of model) → both breathe with seasonal heteroscedasticity → coverage ≥ 0.90 for both; FPCA band narrower; conformal band pays width for distributional robustness.

## Phase-Wide Coverage Confirmation

**Count:** `ls docs/assets/diagrams/ex-*.svg | wc -l` = **21** (20 new wave-1+wave-2 + pre-existing ex-sonar-tsrvf.svg). Target: 21. PASSED.

**All 20 gap pages covered:** Verification loop `for s in $(ls docs/examples/*.md ...)` prints nothing. PASSED.

**examples/index.md:** No diagram. PASSED.

**git status after final commit:** Clean — only .planning/ files remain (this SUMMARY.md). PASSED.

## Judgment Calls for Phase 49 Human Diagram Review

The following diagrams involved interpretation choices that the Phase 49 blocking human diagram review should verify:

1. **`ex-tecator-regression.svg`** — The page covers 5 separate sections (preprocessing, 3-method comparison, beta(λ), residuals, logistic classification). The diagram emphasizes the main arc (preprocessing → comparison → beta → classification) and omits the residual-diagnostics section (fitted vs residuals, QQ-plot) to keep the flow to 4 clear panels. Reviewer should confirm the residuals section is secondary enough to omit from the workflow diagram.

2. **`ex-biopharma-monitoring.svg`** — The `fregre_cv` yield prediction from early 200h trajectory is included in row 2 alongside the false-alarm check, but it is a secondary section on the page (the main arc is Phase I/II monitoring). Reviewer should confirm it belongs in the diagram or if it should be relegated to a bottom note only.

3. **`ex-explainability-regions.svg`** — The 5-method convergence is depicted with 4 parallel explainer panels + a result convergence box + a PDP row at the bottom. The PDP section is the most distinct from the others (it answers a different question: marginal effect of one FPC score, not wavelength importance). Reviewer should confirm the PDP panel placement and whether it should be separated more clearly from the 4 importance/significance methods.

4. **`ex-phoneme-shape.svg`** — The diagram's main message is a cautionary one (elastic hurts on spectral data) and explicitly shows L² winning. The per-class phase fractions (seeming to favour elastic) are depicted as a setup for the reversal. Reviewer should confirm this "cautionary" narrative is appropriate as the diagram's primary message, or whether the diagram should be more neutral and just show the methods.

5. **`ex-growth-alignment.svg`** — The note about `karcher_mean["converged"]` staying False on this coarse grid is depicted in the bottom note area (as a practical implementation note, not a core method arc step). Reviewer should confirm this is appropriate or whether it should be omitted from the diagram entirely (it's a fdars-core upstream issue, not a method-accuracy point).

## Deviations from Plan

None — plan executed exactly as written. All 3 tasks (3 tecator + 2 monitoring + 6 misc) completed, all 11 diagrams pass the check-ex.sh gate, all 11 pages embed correctly, no-regression guard passes for all batches.

## Self-Check

### Created files exist:
- [x] docs/assets/diagrams/ex-tecator-regression.svg
- [x] docs/assets/diagrams/ex-tecator-conformal-coverage.svg
- [x] docs/assets/diagrams/ex-tecator-monitoring.svg
- [x] docs/assets/diagrams/ex-biopharma-monitoring.svg
- [x] docs/assets/diagrams/ex-inline-monitoring.svg
- [x] docs/assets/diagrams/ex-cross-validation.svg
- [x] docs/assets/diagrams/ex-explainability-regions.svg
- [x] docs/assets/diagrams/ex-functional-outlier-workflow.svg
- [x] docs/assets/diagrams/ex-growth-alignment.svg
- [x] docs/assets/diagrams/ex-phoneme-shape.svg
- [x] docs/assets/diagrams/ex-tolerance-vs-conformal.svg

### Commits exist:
- [x] 8a03de8 (Task 1 tecator family)
- [x] 419a471 (Task 2 monitoring family)
- [x] 3fc1b15 (Task 3 misc group)

### Phase-wide coverage:
- [x] 21 ex-*.svg files (20 new + 1 pre-existing sonar-tsrvf.svg)
- [x] All 20 gap pages carry .fdars-diagram embed (verification loop prints nothing)
- [x] examples/index.md has NO diagram
- [x] git status clean after all task commits

### No-regression guard: PASSED (all 3 batches)

### svgo@3.3.4 idempotence gate: PASSED (all 11 diagrams)

### rsvg-convert PNG non-empty: PASSED (all 11 diagrams)

## Self-Check: PASSED
