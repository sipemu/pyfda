# Phase 66: fdars-core 0.24→0.33 API Audit + Changelog Record

**Generated:** 2026-09-02
**Bump:** fdars-core 0.23.0 → 0.33.0 (parallel feature only, no linalg)
**Method:** Registry source read at `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/fdars-core-0.33.0/` after `cargo update -p fdars-core`; build output analysis; pytest regression gate results.

---

## 1. 0.24→0.33 Changelog Summary

The CHANGELOG.md was read directly from the 0.33.0 registry source. Entries that were absent from the 0.23.0 cache (the "0.31/0.32 gap" noted in research) are now confirmed present. Below is the version-by-version summary for 0.24→0.33; entries PRIOR to 0.23.0 are omitted as they were the pre-bump baseline.

Note: The research CHANGELOG summary table used a different numbering than the actual crate — the crate's published versions skip from 0.22.0 to 0.33.0 directly in terms of _pyfda_-relevant releases (0.23–0.31 were subversions within the pyfda build pipeline). The CHANGELOG directly contains entries for 0.22.0, 0.21.0, 0.20.0, and 0.19.0 as the most recent batch before 0.33.0.

**Key observation:** The CHANGELOG at 0.33.0 confirms entries 0.32.0 and 0.31.0 ARE present — these were the "0.31/0.32 gap" noted in research as absent from the 0.23.0 cache. The gap is now closed:

| Version | Breaking changes to existing pyfda bindings | New modules/functions |
|---------|---------------------------------------------|----------------------|
| 0.24→0.28 | None (within v6.0 baseline — already bound) | pace_fpca, elastic_multinomial, concurrent_regression, functional_glm, etc. — all already bound in prior phases |
| 0.29.0–0.30.0 | **Soft `#[deprecated]`** on 4 depth fns + `fanova`; no breakage | Performance/consolidation; `fanova` deprecated in `function_on_scalar` |
| 0.31.0 (as 0.31.x) | None — additive only | `GAK` metric (`metric::gak`): Triangular Global Alignment Kernel + `gak_gram_matrix` + `GakConfig`; Kernel k-means on curves (`kernel_kmeans_fd`); `KernelKmeansResult` |
| 0.32.0 | None — additive only | `GAK` and kernel-kmeans completion (see 0.31.0 note above — CHANGELOG entry is `[0.32.0]`) |
| 0.33.0 | None — additive only | New `shapelet` module: `z_normalize_window`, `shapelet_distance`, `discover_shapelets`, `shapelet_transform`, `shapelet_transform_fit`, `shapelet_classifier_fit`, `ShapeletSet`, `ShapeletTransformFit`, `ShapeletClassifierFit`, `ShapeletDiscoveryConfig`, `QualityMeasure` (InfoGain/FStatistic), `ShapeletClassifier` (kNN/LDA) |

**0.31/0.32 gap resolution:** The CHANGELOG entry `[0.32.0]` contains GAK + kernel k-means; `[0.31.0]` is listed separately for GAK initial additions. Both are fully additive — no existing pyfda binding signatures were touched in these versions. This is confirmed by the clean compilation of `maturin develop --release` and the zero-failure regression gate.

**Conclusion:** No breaking changes to any existing pyfda binding across the full 0.24→0.33 span. All changes are additive (new modules/functions). The existing `src/*_mod.rs` binding surface is unaffected except for the soft deprecation of 6 functions (handled via CONTINGENCY below).

---

## 2. Enum / Match-Arm Audit Result

**Method:** Registry source read of fdars-core-0.33.0; confirmation by successful compile under `RUSTFLAGS="-D warnings" maturin develop --release` (which would fail on removed enum variants in non-wildcard match arms).

### `depth_mod.rs` — `DepthMethod` enum

Source confirmed at: `fdars-core-0.33.0/src/depth/dispatch.rs:31`

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"fraiman_muniz"` | `DepthMethod::FraimanMuniz { scale }` | **CONFIRMED-PRESENT** |
| `"band"` | `DepthMethod::Band` | **CONFIRMED-PRESENT** |
| `"modified_band"` | `DepthMethod::ModifiedBand` | **CONFIRMED-PRESENT** |
| `"random_projection"` | `DepthMethod::RandomProjection { nproj, seed }` | **CONFIRMED-PRESENT** |
| `"total_variation"` | `DepthMethod::TotalVariation` | **CONFIRMED-PRESENT** |
| `"hypograph_index"` | `DepthMethod::HypographIndex` | **CONFIRMED-PRESENT** |
| `"modified_hypograph_index"` | `DepthMethod::ModifiedHypographIndex` | **CONFIRMED-PRESENT** |
| `"epigraph_index"` | `DepthMethod::EpigraphIndex` | **CONFIRMED-PRESENT** |
| `"half_region"` | `DepthMethod::HalfRegion` | **CONFIRMED-PRESENT** |
| `"modified_half_region"` | `DepthMethod::ModifiedHalfRegion` | **CONFIRMED-PRESENT** |
| `"extremal"` | `DepthMethod::Extremal` | **CONFIRMED-PRESENT** |
| `"extreme_rank_length"` | `DepthMethod::ExtremeRankLength` | **CONFIRMED-PRESENT** |
| `"l_infinity"` | `DepthMethod::LInfinity` | **CONFIRMED-PRESENT** |

Evidence: `dispatch.rs` line 31 defines the enum; test files (`extremal.rs:236`, `linf.rs:172`, `half_region.rs:268`) exercise all variants at 0.33.

### `fdata_mod.rs` — `NormalizationMethod` enum

Source confirmed at: `fdars-core-0.33.0/src/fdata.rs:548`

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"center"` | `NormalizationMethod::Center` | **CONFIRMED-PRESENT** |
| `"autoscale"` | `NormalizationMethod::Autoscale` | **CONFIRMED-PRESENT** |
| `"pareto"` | `NormalizationMethod::Pareto` | **CONFIRMED-PRESENT** |
| `"range"` | `NormalizationMethod::Range` | **CONFIRMED-PRESENT** |
| `"curve_center"` | `NormalizationMethod::CurveCenter` | **CONFIRMED-PRESENT** |
| `"curve_standardize"` | `NormalizationMethod::CurveStandardize` | **CONFIRMED-PRESENT** |
| `"curve_range"` | `NormalizationMethod::CurveRange` | **CONFIRMED-PRESENT** |
| `"curve_lp"` | `NormalizationMethod::CurveLp(p)` | **CONFIRMED-PRESENT** |

Evidence: enum defined at `fdata.rs:548`; CHANGELOG v0.13.0 documents all 8 variants; present at 0.33.

### `smoothing_mod.rs` — `CvCriterion` enum

Source confirmed at: `fdars-core-0.33.0/src/smoothing.rs:531–539`

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"cv"` | `CvCriterion::Cv` | **CONFIRMED-PRESENT** |
| `"gcv"` | `CvCriterion::Gcv` | **CONFIRMED-PRESENT** |
| `"aic"` | `CvCriterion::Aic` | **CONFIRMED-PRESENT** |

Note: `CvCriterion` is `#[non_exhaustive]` (added in v0.20.0). The wildcard arm `_ => CvCriterion::Gcv` in `smoothing_mod.rs` is correct for forward compatibility. Pre-existing silent-default behavior documented; not changed.

### `basis_mod.rs` — `BasisType` / `BasisCriterion`

Source confirmed via compile success and CHANGELOG continuity (v0.8.0 and prior).

| String | Target | Status at 0.33 |
|--------|--------|----------------|
| `"bspline"` | `BasisType::Bspline` | **CONFIRMED-PRESENT** |
| `"fourier"` | `BasisType::Fourier` | **CONFIRMED-PRESENT** |
| `"gcv"` | `BasisCriterion::Gcv` | **CONFIRMED-PRESENT** |
| `"cv"` | `BasisCriterion::Cv` | **CONFIRMED-PRESENT** |
| `"aic"` | `BasisCriterion::Aic` | **CONFIRMED-PRESENT** |
| `"bic"` | `BasisCriterion::Bic` | **CONFIRMED-PRESENT** |

### `regression_mod.rs` — `GlmFamily` / `SelectionCriterion`

Source confirmed at: `fdars-core-0.33.0/src/scalar_on_function/glm.rs` + `mod.rs:268`

| String | Enum / Target | Status at 0.33 |
|--------|--------------|----------------|
| `"aic"` | `SelectionCriterion::Aic` | **CONFIRMED-PRESENT** |
| `"bic"` | `SelectionCriterion::Bic` | **CONFIRMED-PRESENT** |
| `"gcv"` (wildcard default) | `SelectionCriterion::Gcv` | **CONFIRMED-PRESENT** |
| `"huber"` | `fregre_huber(...)` | **CONFIRMED-PRESENT** |
| `"binomial"` | `GlmFamily::Binomial` | **CONFIRMED-PRESENT** |
| `"poisson"` | `GlmFamily::Poisson` | **CONFIRMED-PRESENT** |
| `"gamma"` | `GlmFamily::Gamma` | **CONFIRMED-PRESENT** |
| `"gaussian"` | `GlmFamily::Gaussian` | **CONFIRMED-PRESENT** |

Evidence: `glm.rs` module-level doc table lists all 4 variants; CHANGELOG v0.21.0 confirms they were added non-breakingly.

### `inference_mod.rs` — `MultiplierDistribution` / `ProjectionBasisType`

Source confirmed via CHANGELOG (v0.19.0 inference module, v0.8.4 `ProjectionBasisType` enum) + compile success.

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"gaussian"` | `MultiplierDistribution::Gaussian` | **CONFIRMED-PRESENT** |
| `"rademacher"` | `MultiplierDistribution::Rademacher` | **CONFIRMED-PRESENT** |
| `"bspline"` | `ProjectionBasisType::Bspline` | **CONFIRMED-PRESENT** |
| `"fourier"` | `ProjectionBasisType::Fourier` | **CONFIRMED-PRESENT** |

### `represent_mod.rs` — `ExtrapolationPolicy` / `InterpolationMethod` / `ImputationMethod`

Source confirmed via CHANGELOG (v4.0/pyfda Phase 26 additions, v0.14.0 era) + compile success.

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"boundary"` | `ExtrapolationPolicy::Boundary` | **CONFIRMED-PRESENT** |
| `"exception"` | `ExtrapolationPolicy::Exception` | **CONFIRMED-PRESENT** |
| `"fill"` | `ExtrapolationPolicy::Fill(fill_value)` | **CONFIRMED-PRESENT** |
| `"periodic"` | `ExtrapolationPolicy::Periodic` | **CONFIRMED-PRESENT** |
| `"linear"` | `InterpolationMethod::Linear` | **CONFIRMED-PRESENT** |
| `"cubic_hermite"` | `InterpolationMethod::CubicHermite` | **CONFIRMED-PRESENT** |
| `"linear"` | `ImputationMethod::Linear` | **CONFIRMED-PRESENT** |
| `"mean"` | `ImputationMethod::Mean` | **CONFIRMED-PRESENT** |
| `"constant"` | `ImputationMethod::Constant(constant_value)` | **CONFIRMED-PRESENT** |

### `alignment_mod.rs` — multiple enums

Source confirmed via compile success (the binding exercises `TransportMethod`, `Linkage`, `WarpPenaltyType`, `ShapeQuotient`, `LandmarkKind`, `PcaMethod`) + CHANGELOG continuity.

| String | Enum Variant / Target | Status at 0.33 |
|--------|---------------------|----------------|
| `"schilds_ladder"` | `TransportMethod::SchildsLadder` | **CONFIRMED-PRESENT** |
| `"pole_ladder"` | `TransportMethod::PoleLadder` | **CONFIRMED-PRESENT** |
| `"complete"` | `Linkage::Complete` | **CONFIRMED-PRESENT** |
| `"average"` | `Linkage::Average` | **CONFIRMED-PRESENT** |
| `"second_order"` | `WarpPenaltyType::SecondOrder` | **CONFIRMED-PRESENT** |
| `"combined"` | `WarpPenaltyType::Combined { ... }` | **CONFIRMED-PRESENT** |
| `"reparameterization_translation"` | `ShapeQuotient::ReparameterizationTranslation` | **CONFIRMED-PRESENT** |
| `"reparameterization_translation_scale"` | `ShapeQuotient::ReparameterizationTranslationScale` | **CONFIRMED-PRESENT** |
| `"peak"` / `"peaks"` / `"max"` | `LandmarkKind::Peak` | **CONFIRMED-PRESENT** |
| `"valley"` / `"valleys"` / `"min"` | `LandmarkKind::Valley` | **CONFIRMED-PRESENT** |
| `"zero_crossing"` / `"zerocrossing"` / `"zero"` | `LandmarkKind::ZeroCrossing` | **CONFIRMED-PRESENT** |
| `"inflection"` | `LandmarkKind::Inflection` | **CONFIRMED-PRESENT** |
| `"custom"` | `LandmarkKind::Custom` | **CONFIRMED-PRESENT** |
| `"amplitude"` / `"amp"` | `elastic_amp_changepoint(...)` | **CONFIRMED-PRESENT** |
| `"phase"` / `"ph"` | `elastic_ph_changepoint(...)` | **CONFIRMED-PRESENT** |
| `"fpca"` | `elastic_fpca_changepoint(...)` | **CONFIRMED-PRESENT** |
| `"vertical"` / `"vert"` | `PcaMethod::Vertical` | **CONFIRMED-PRESENT** |
| `"horizontal"` / `"horiz"` | `PcaMethod::Horizontal` | **CONFIRMED-PRESENT** |
| `"joint"` | `PcaMethod::Joint` | **CONFIRMED-PRESENT** |

Note: Several alignment wildcard arms silently default (Linkage → Single, TransportMethod → LogMap). This is pre-existing behavior; not changed.

### `conformal_mod.rs` — `PcaMethod`

**CONFIRMED-PRESENT** — same `PcaMethod` enum as alignment_mod; variants Vertical/Horizontal/Joint confirmed.

### `simulation_mod.rs` — `EFunType` / `EValType` / `CovKernel`

Source confirmed via compile success + CHANGELOG (added in v0.8.5 covariance/GP module).

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"fourier"` | `EFunType::Fourier` | **CONFIRMED-PRESENT** |
| `"poly"` | `EFunType::Poly` | **CONFIRMED-PRESENT** |
| `"poly_high"` | `EFunType::PolyHigh` | **CONFIRMED-PRESENT** |
| `"wiener"` | `EFunType::Wiener` | **CONFIRMED-PRESENT** |
| `"linear"` | `EValType::Linear` | **CONFIRMED-PRESENT** |
| `"exponential"` | `EValType::Exponential` | **CONFIRMED-PRESENT** |
| `"wiener"` | `EValType::Wiener` | **CONFIRMED-PRESENT** |
| `"gaussian"` | `CovKernel::Gaussian { ... }` | **CONFIRMED-PRESENT** |
| `"exponential"` | `CovKernel::Exponential { ... }` | **CONFIRMED-PRESENT** |
| `"matern"` | `CovKernel::Matern { ... }` | **CONFIRMED-PRESENT** |
| `"periodic"` | `CovKernel::Periodic { ... }` | **CONFIRMED-PRESENT** |

### `spm_mod.rs` — `NcompMethod` / `ControlLimitMethod`

Source confirmed via CHANGELOG (v0.9.0 SPM module) + compile success.

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"cumulative_variance"` | `NcompMethod::CumulativeVariance(threshold)` | **CONFIRMED-PRESENT** |
| `"elbow"` | `NcompMethod::Elbow` | **CONFIRMED-PRESENT** |
| `"kaiser"` | `NcompMethod::Kaiser` | **CONFIRMED-PRESENT** |
| `"fixed"` | `NcompMethod::Fixed(threshold as usize)` | **CONFIRMED-PRESENT** |
| `"parametric"` | `ControlLimitMethod::Parametric` | **CONFIRMED-PRESENT** |
| `"empirical"` | `ControlLimitMethod::Empirical` | **CONFIRMED-PRESENT** |

### `tolerance_mod.rs` — `BandType` / `ExponentialFamily`

Source confirmed via CHANGELOG (v0.6.0 tolerance module) + compile success.

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"simultaneous"` | `BandType::Simultaneous` | **CONFIRMED-PRESENT** |
| `"pointwise"` | `BandType::Pointwise` | **CONFIRMED-PRESENT** |
| `"gaussian"` | `ExponentialFamily::Gaussian` | **CONFIRMED-PRESENT** |
| `"binomial"` | `ExponentialFamily::Binomial` | **CONFIRMED-PRESENT** |
| `"poisson"` | `ExponentialFamily::Poisson` | **CONFIRMED-PRESENT** |

### `seasonal_mod.rs` — `StrengthMethod`

Source confirmed via CHANGELOG (v0.3.0 seasonal module) + compile success.

| String | Enum Variant / Target | Status at 0.33 |
|--------|---------------------|----------------|
| `"variance"` | `StrengthMethod::Variance` / `seasonal_strength_variance(...)` | **CONFIRMED-PRESENT** |
| `"spectral"` | `StrengthMethod::Spectral` / `seasonal_strength_spectral(...)` | **CONFIRMED-PRESENT** |

### `explain_mod.rs` — `DepthType`

Source confirmed at: `fdars-core-0.33.0/src/explain/advanced.rs:365`; three variants used in kernel helpers at `explain/helpers/kernel.rs:128/131/132`.

| String | Enum Variant | Status at 0.33 |
|--------|-------------|----------------|
| `"modified_band"` | `DepthType::ModifiedBand` | **CONFIRMED-PRESENT** |
| `"functional_spatial"` | `DepthType::FunctionalSpatial` | **CONFIRMED-PRESENT** |
| `DepthType::FraimanMuniz` (literal, not string dispatch) | — | **CONFIRMED-PRESENT** |

---

## 3. The Four 0.30-Deprecated 2D Depth Functions (+ fanova + mean_2d) — FLAGGED FOR LATER MIGRATION

**These functions are soft-deprecated (`#[deprecated]` attribute) at fdars-core 0.33.0 — they remain callable. Do NOT migrate in Phase 66.**

| Binding function | Call site (file:line) | Calls deprecated upstream function | Deprecation reason |
|-----------------|----------------------|-----------------------------------|--------------------|
| `fraiman_muniz_2d` | `depth_mod.rs:50` | `fdars_core::depth::fraiman_muniz_2d` | "redundant with `fraiman_muniz(…, Dim::Two)`; body just forwards to `fraiman_muniz_1d`" |
| `modal_2d` | `depth_mod.rs:94` | `fdars_core::depth::modal_2d` | "redundant with `modal(…, Dim::Two)`; body just forwards to `modal_1d`" |
| `random_projection_2d` | `depth_mod.rs:138` | `fdars_core::depth::random_projection_2d` | "redundant with `random_projection(…, Dim::Two)`; body just forwards to `random_projection_1d`" |
| `random_tukey_2d` | `depth_mod.rs:182` | `fdars_core::depth::random_tukey_2d` | "redundant with `random_tukey(…, Dim::Two)`; body just forwards to `random_tukey_1d`" |
| `fanova` | `regression_mod.rs:404` | `fdars_core::function_on_scalar::fanova` | "use `fanova_seeded` for reproducible permutation p-values; `fanova` delegates with the legacy fixed seed 42" |
| `mean_2d` | `fdata_mod.rs:45` | `fdars_core::fdata::mean_2d` | "redundant with `mean(…, Dim::Two)`; body just forwards to `mean_1d`" (NOTE: not in original research list — discovered at build time) |

**Status at 0.33.0:** All 6 functions have `#[deprecated]` attribute confirmed in registry source:
- `fdars-core-0.33.0/src/depth/fraiman_muniz.rs:61`
- `fdars-core-0.33.0/src/depth/modal.rs:62`
- `fdars-core-0.33.0/src/depth/random_projection.rs:82`
- `fdars-core-0.33.0/src/depth/random_tukey.rs:56`
- `fdars-core-0.33.0/src/function_on_scalar.rs:912`
- `fdars-core-0.33.0/src/fdata.rs:202`

**Note:** `mean_2d` was NOT listed in the research as a deprecated function — it was discovered at build time when `RUSTFLAGS="-D warnings" maturin develop --release` surfaced it as an additional deprecated call site. It has been handled identically to the research-documented four depth functions. Migration of all 6 is deferred to a later phase.

"Deprecation warnings expected; migration deferred to a later phase."

---

## 4. Phase 66 CONTINGENCY — #[allow(deprecated)] Scope Deviation

**Trigger:** `RUSTFLAGS="-D warnings" maturin develop --release` promotes all 6 `#[deprecated]` call sites to hard errors, causing the build to fail.

**Determination:** Confirmed SOFT-DEPRECATED (not removed) at 0.33.0 by direct registry source inspection (see Section 3). Compiler error message is "use of deprecated function" — not "not found in this scope" — confirming the functions still exist.

**Resolution:** Added `#[allow(deprecated)]` at the function level (on the `pub fn` wrapper, before `#[pyfunction]`) at exactly and only the 6 affected call sites:

| File | Function | Line (post-edit) |
|------|----------|-----------------|
| `src/depth_mod.rs` | `fraiman_muniz_2d` | ~40 |
| `src/depth_mod.rs` | `modal_2d` | ~84 |
| `src/depth_mod.rs` | `random_projection_2d` | ~128 |
| `src/depth_mod.rs` | `random_tukey_2d` | ~172 |
| `src/fdata_mod.rs` | `mean_2d` | ~39 |
| `src/regression_mod.rs` | `fanova` | ~394 |

**What was NOT done:**
- No global `#![allow(deprecated)]` at crate root
- No RUSTFLAGS unsetting as the solution
- No migration of the deprecated functions to their replacements
- No other src/ changes

**Commit:** `e32878f` — "fix(66-01): add #[allow(deprecated)] at 6 deprecated call sites for fdars-core 0.33.0"

**Scope assessment:** This is the minimal change needed to satisfy the CI gate (`RUSTFLAGS="-D warnings"`) while deferring migration to a later phase. The six `#[allow(deprecated)]` attributes add 6 lines across 3 files; no behavior changes.

---

## 5. Regression Gate Result (Task 3)

**Command:** `pytest tests/ -x -q` (run against the 0.33.0 extension built with `RUSTFLAGS="-D warnings" maturin develop --release`)

**Final summary line:**
```
5339 passed, 10 skipped, 120 warnings in 48.84s
```

**Baseline comparison:** Prior baseline was 772 passed / 4 skipped (v6.0 Phase 36). The higher count (5339) reflects the inclusion of the sklearn compliance suite (`tests/sklearn/`) added in v9.0 (Phase 58). Zero failures across the full suite.

**Numeric tolerance changes needed:** **None.** The 10-minor jump (0.23→0.33) produced zero numeric drift detectable by the suite. All 0.33.0 algorithmic additions are new modules/functions; the existing bound surface shows identical behavior.

**Tests modified:** **None.** No file under `tests/` was edited. Confirmed: `git status --porcelain -- tests/ | grep -c . | grep -qx 0 → TESTS_UNTOUCHED`.

**Gate verdict:** PASSED — zero new failures; scope boundary intact.

---

## Summary

| Check | Result |
|-------|--------|
| Changelog 0.24→0.33 — breaking changes to existing bindings | None confirmed |
| 0.31/0.32 gap closed | Yes — GAK+kernel-kmeans (0.32) and GAK initial (0.31) confirmed additive |
| Enum/match-arm audit — all variants present at 0.33 | **ALL CONFIRMED-PRESENT** (0 flagged as removed/renamed) |
| Four 0.30-deprecated 2D depth functions — soft or hard? | SOFT (`#[deprecated]`, still callable) |
| `fanova` deprecation — soft or hard? | SOFT (`#[deprecated]`, still callable) |
| `mean_2d` deprecation (new discovery) — soft or hard? | SOFT (`#[deprecated]`, still callable) |
| CONTINGENCY applied | Yes — 6 `#[allow(deprecated)]` at call sites; commit e32878f |
| Regression gate | PASSED — 5339 passed, 0 failed |
| Numeric tolerance changes | None |
| MSRV | Unchanged at 1.83 (0.33.0 requires ≥ 1.81) |
