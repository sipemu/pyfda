# Stack Research

**Domain:** PyO3 binding layer — fdars-core 0.20.0 → 0.23.0 upgrade
**Researched:** 2026-08-20
**Confidence:** HIGH — all findings read directly from the v0.23.0 git tag in the local fdars-core checkout at `/home/simonm/projects/rust/fdars`; no inference from secondary sources.

---

## Summary Verdicts

| Question | Verdict | Evidence |
|----------|---------|----------|
| MSRV raised above Rust 1.83? | **NO — MSRV is 1.81** | `fdars-core/Cargo.toml` `rust-version = "1.81"` at v0.23.0 tag, unchanged from v0.20.0 |
| `linalg` feature required for new capabilities? | **NO** | All new 0.21–0.23 functions are in default-feature or `parallel`-only code paths; `linalg` still gates only `ridge_regression_fit` + `faer`/`anofox-regression` (unchanged) |
| Dependency graph additive? | **YES — zero new direct deps** | `git diff v0.20.0 v0.23.0 -- fdars-core/Cargo.toml` shows only the version field changed; every dependency entry is byte-for-byte identical |
| New Python extras needed? | **NO** | All new capabilities bind through the existing numpy/FdMatrix boundary; no new Python packages are implied |
| Pinned version string to use | `fdars-core = { version = "0.23.0", features = ["parallel"] }` | Direct read of v0.23.0 Cargo.toml |

---

## Recommended Stack

### Core Technologies — unchanged, bump version pin only

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| fdars-core | **0.23.0** (was 0.20.0) | Upstream FDA computation engine | Single version bump; zero dependency graph change |
| PyO3 | 0.28 | Rust↔Python bridge, abi3-py39 stable ABI | No change; not touched by the 0.21–0.23 crate series |
| numpy (crate) | 0.28 | Zero-copy ndarray ↔ FdMatrix conversion | No change |
| maturin | 1.0–2.0 | Build backend | No change |
| Rust toolchain | stable / 1.83 MSRV | pyfda's own MSRV (Cargo.toml `rust-version = "1.83"`) | fdars-core dropped to 1.81 at 0.23, so pyfda's 1.83 pin remains the binding constraint and is still satisfied |

### Transitive Rust Dependencies — resolved versions unchanged

The `git diff` between v0.20.0 and v0.23.0 on `fdars-core/Cargo.toml` shows only the `version` field changed.
Every dependency spec (rayon 1.10, rand 0.8, rand_distr 0.4, rustfft 6.2, num-complex 0.4, nalgebra 0.33, faer 0.23 optional, anofox-regression 0.4 optional) is identical.

Current `Cargo.lock` resolved versions that will carry forward:
- `nalgebra` 0.33.3
- `rayon` 1.11.0
- `rand` 0.8.5
- `rustfft` 6.4.1
- `num-complex` 0.4.6

`cargo update` after the version bump may resolve to later patch versions of rayon/rand/etc. within the same SemVer range; that is normal and safe. No major version jumps are introduced.

`faer`/`anofox-regression` remain optional and gated behind `linalg`; they are not activated by pyfda's `parallel`-only build.

### New Rust Modules Added 0.20→0.23

Two new top-level `pub mod` entries appear in `fdars-core/src/lib.rs` at v0.23.0 (absent at v0.20.0):

| Module | Added in | What it provides |
|--------|----------|-----------------|
| `concurrent_regression` | 0.21 | `concurrent_regression()` + `ConcurrentRegrResult` |
| `pace_fpca` | 0.22 | `pace_fpca()` + `PaceFpcaConfig` + `PaceFpcaResult` |

All other new capabilities (elastic_multinomial, functional_glm, depth variants, outlier detectors, ITP inference) are **additions inside existing modules**, not new modules.

### New Public Surface by Capability Group

#### Group A — Regression (extend `fdars.regression` + new concurrent binding)

| Symbol | Module in fdars-core | Type | Notes |
|--------|---------------------|------|-------|
| `concurrent_regression` | `concurrent_regression` | fn | `(response: &FdMatrix, predictors: &[FdMatrix], argvals: Option<&[f64]>, bandwidth: f64, kernel: &str) -> Result<ConcurrentRegrResult>` |
| `ConcurrentRegrResult` | `concurrent_regression` | struct (#[non_exhaustive]) | fields: `beta_curve: FdMatrix`, `intercept: Vec<f64>`, `fitted: FdMatrix`, `residuals: FdMatrix`, `argvals: Vec<f64>` |
| `functional_glm` | `scalar_on_function` | fn | `(data: &FdMatrix, y: &[f64], family: GlmFamily, scalar_covariates: Option<&FdMatrix>, ncomp: usize, max_iter: usize, tol: f64) -> Result<FunctionalGlmResult>` |
| `predict_functional_glm` | `scalar_on_function` | fn | takes `fit: &FunctionalGlmResult` + `new_data` + optional `new_scalar`; **uses fitted handle, does NOT re-fit** |
| `FunctionalGlmResult` | `scalar_on_function` | struct | fields: `intercept`, `beta_t`, `beta_se`, `gamma`, `fitted_values`, `linear_predictors`, `ncomp`, `coefficients`, `std_errors`, `log_likelihood`, `deviance`, `iterations`, `fpca` (embedded FpcaResult), `aic`, `bic` |
| `GlmFamily` | `scalar_on_function` | enum (#[non_exhaustive]) | variants: `Binomial`, `Poisson`, `Gamma`, `Gaussian` |

`concurrent_regression` is in `fdars_core::concurrent_regression`, not `fdars_core::scalar_on_function`. It extends `fdars.regression` on the Python side (not a new submodule). `functional_glm`/`predict_functional_glm` are in `fdars_core::scalar_on_function` alongside the existing `fregre_lm` etc.; they also extend `fdars.regression`.

#### Group B — FPCA & Classification

| Symbol | Module in fdars-core | Type | Notes |
|--------|---------------------|------|-------|
| `pace_fpca` | `pace_fpca` | fn | `(data: &IrregFdata, config: &PaceFpcaConfig) -> Result<PaceFpcaResult>` |
| `PaceFpcaConfig` | `pace_fpca` | struct (has Default) | fields: `ncomp: usize` (default 3), `bandwidth: f64` (default 0.1), `sigma2: f64` (default 0.01, **must be strictly positive**), `work_grid: Vec<f64>` (default 51-point [0,1]), `alpha: f64` (default 0.05) |
| `PaceFpcaResult` | `pace_fpca` | struct (#[non_exhaustive]) | fields: `mean: Vec<f64>`, `eigenvalues: Vec<f64>`, `eigenfunctions: FdMatrix` (m×ncomp), `scores: FdMatrix` (n×ncomp), `fitted: FdMatrix` (n×m), `fitted_lower: FdMatrix` (n×m), `fitted_upper: FdMatrix` (n×m), `argvals: Vec<f64>`, `sigma2: f64`, `ncomp: usize` |
| `IrregFdata` | `irreg_fdata` | struct | CSR-layout sparse functional data; constructed via `IrregFdata::from_lists(argvals_list, values_list)`; **NOT currently exposed in pyfda** — must add Python constructor |
| `elastic_multinomial` | `elastic_regression` | fn | `(data: &FdMatrix, y: &[usize], argvals: &[f64], ncomp_beta: usize, lambda: f64, max_iter: usize, tol: f64) -> Result<ElasticMultinomialResult>` |
| `predict_elastic_multinomial` | `elastic_regression` | fn | takes `fit: &ElasticMultinomialResult` + `new_data` + `new_argvals` |
| `ElasticMultinomialResult` | `elastic_regression` | struct (#[non_exhaustive]) | fields: `n_classes: usize`, `classes: Vec<usize>`, `class_models: Vec<ElasticLogisticResult>`, `train_probabilities: FdMatrix` (n×K), `predicted_classes: Vec<usize>`, `train_accuracy: f64` |

**Key design note on IrregFdata:** `pace_fpca` is the only new function requiring `IrregFdata`. This type uses CSR-style storage with `offsets: Vec<usize>`, `argvals: Vec<f64>`, `values: Vec<f64>`, `rangeval: [f64; 2]`. The Python binding must accept lists-of-arrays (one per observation) and construct `IrregFdata::from_lists`. This is a new binding pattern not present in any existing pyfda module.

#### Group C — Depth / Outliers / Interval Inference

**Depth:** `DepthMethod` enum extended with 10 new variants (was 4 at v0.20.0, is 14 at v0.23.0):

New variants: `HypographIndex`, `ModifiedHypographIndex`, `EpigraphIndex`, `ModifiedEpigraphIndex`, `HalfRegion`, `ModifiedHalfRegion`, `Extremal`, `ExtremeRankLength`, `LInfinity`, `TotalVariation`

New standalone functions added to `depth` module (callable directly, not only via dispatcher):
- `hypograph_index_1d`, `modified_hypograph_index_1d`
- `epigraph_index_1d`, `modified_epigraph_index_1d`
- `half_region_depth_1d`, `modified_half_region_depth_1d`
- `extremal_depth_1d`, `extreme_rank_length_depth_1d`, `linfinity_depth_1d`
- `total_variation_depth_1d` — returns `TvdMssResult { tvd: Vec<f64>, mss: Vec<f64> }` (not `Vec<f64>`)

`TvdMssResult` is a new struct type, re-exported from lib.rs at v0.23.0.

The existing `functional_depth` dispatcher in `depth_mod.rs` has a string-matching `parse_depth_method` helper — it must be extended with all 10 new string keys and a `#[non_exhaustive]` wildcard arm. The error message in the fallback must list all 14 variants.

**Outliers:** Four new detectors added to `fdars_core::outliers` (was 3 functions at v0.20.0):

| Symbol | Type | Key fields |
|--------|------|-----------|
| `tvdmss(data, TvdMssConfig)` | fn -> `TvdMssOutliers` | config: `emp_factor_mss` (1.5), `emp_factor_tvd` (1.5), `central_region_tvd` (0.5); result: `magnitude_outliers: Vec<usize>`, `shape_outliers: Vec<usize>`, `tvd: Vec<f64>`, `mss: Vec<f64>` |
| `muod(data, MuodConfig)` | fn -> `MuodResult` | config: `emp_factor` (1.5); result: `shape_outliers`, `magnitude_outliers`, `amplitude_outliers`, `shape_index`, `magnitude_index`, `amplitude_index` (all `Vec<usize>` or `Vec<f64>`) |
| `sequential_transform_outliers(data, SeqTransformConfig)` | fn -> `SeqTransformOutliers` | `SeqTransform` enum: `T0`, `T1`, `T2`, `T3`; result: `per_transform_outliers: Vec<(SeqTransform, Vec<usize>)>`, `union_outliers: Vec<usize>` |
| `depthgram(data, DepthgramConfig)` | fn -> `DepthgramResult` | config: `emp_factor` (1.5); result: `mbd_mei_d`, `mei_mbd_d`, `mbd_mei_t`, `mei_mbd_t`, `mbd_mei_t2`, `mei_mbd_t2` (all `Vec<f64>`), `shape_outliers`, `magnitude_outliers`, `mbd`, `mei` |

**ITP Inference** (extend `fdars.inference`):

| Symbol | Signature | Notes |
|--------|-----------|-------|
| `itp_one_pop` | `(data, argvals, mu0: Option<&[f64]>, basis_type: ProjectionBasisType, nbasis: usize, n_perm: usize, seed: u64)` | One-sample pointwise interval test |
| `itp_two_pop` | `(data_a, data_b, argvals, basis_type, nbasis, n_perm, seed)` | Two-sample pointwise interval test |
| `itp_flm` | `(data, y: &[f64], argvals, basis_type, nbasis, n_perm, seed)` | Functional linear model ITP |
| `ItpResult` | struct | `adjusted_pvalues: Vec<f64>`, `raw_pvalues: Vec<f64>`, `basis_type: ProjectionBasisType`, `n_basis: usize`, `n_perm: usize` |
| `ProjectionBasisType` | enum | `Bspline`, `Fourier` — from `basis::projection`, re-exported via inference module |

`ItpResult.basis_type` is a `ProjectionBasisType` enum value. The Python binding should serialize it as a string (`"bspline"` / `"fourier"`). The Python API should accept a `basis_type: str` parameter mapping to the enum, consistent with how `DepthMethod` is handled via string dispatch.

### Python-side Dependencies — no changes

| Package | Current Constraint | Change for v6.0 |
|---------|-------------------|-----------------|
| numpy | (pinned in pyproject.toml) | None |
| pandas | (dependency) | None |
| scipy | docs only | None — existing datasets/examples sufficient for new capabilities |
| scikit-learn | docs only | None |
| matplotlib | `[plot]` extra | None |
| anthropic | `[advisor]` extra | None |

No new Python extras are added. The new capabilities (PACE FPCA, concurrent regression, GLM, depth variants, outlier detectors, ITP) can all be demonstrated using existing datasets in `docs/data/` (canadian weather, growth, tecator, phoneme). The `pace_fpca` example should use a subsampled irregular form of an existing dataset (e.g., canadian weather with sparse observations per station); no new dataset file is needed.

---

## Cargo.toml Change

Only one line changes in `/home/simonm/projects/rust/pyfda/Cargo.toml`:

```toml
# Before
fdars-core = { version = "0.20.0", features = ["parallel"] }

# After
fdars-core = { version = "0.23.0", features = ["parallel"] }
```

Do NOT add `linalg`. Do NOT change pyo3, numpy, or any other dependency.

---

## Binding Patterns for New Capabilities

### Standard pattern (Groups A partial, C partial)
All new functions taking `&FdMatrix` inputs follow the existing `numpy2d_to_fdmatrix` / `vec_to_numpy1d` / `fdmatrix_to_numpy2d` round-trip. No new conversion helpers are needed.

### New pattern: IrregFdata constructor (Group B: pace_fpca)
The Python caller passes `argvals_list: list[np.ndarray]` and `values_list: list[np.ndarray]`. The binding iterates over these, constructs `Vec<Vec<f64>>`, and calls `IrregFdata::from_lists`. This is the only structural binding novelty in v6.0.

### New pattern: SeqTransform per-step result (Group C: sequential_transform_outliers)
`SeqTransformOutliers.per_transform_outliers` is `Vec<(SeqTransform, Vec<usize>)>`. The binding should serialize this as a Python list of `(str, list[int])` tuples, with the `SeqTransform` enum serialized as its string name (`"T0"`, `"T1"`, `"T2"`, `"T3"`).

### Existing pattern extended: DepthMethod string dispatch
The `parse_depth_method` helper in `depth_mod.rs` currently handles 4 variants. It must be extended to handle 14 variants with new string keys matching the new enum variants. The wildcard `other =>` error arm must be updated to list all valid strings.

### Existing pattern extended: non_exhaustive structs
`ConcurrentRegrResult`, `PaceFpcaResult`, `ElasticMultinomialResult` are all `#[non_exhaustive]`. Access fields individually; never struct-literal them. This is the same pattern already in use for `FunctionalBoxplotResult`.

---

## What NOT to Add

| Avoid | Reason |
|-------|--------|
| `linalg` feature | Requires Rust 1.84+ (faer 0.23 dep), above pyfda MSRV 1.83; gates only `ridge_regression_fit`, nothing in the v6.0 scope |
| `serde` feature | Optional serialization; not needed for PyO3 dict conversions |
| New Python runtime dependencies | All new capabilities serialize to numpy arrays + Python dicts; no new packages required |
| New Python extras | Scope is binding-layer + advisor; existing `[advisor]`, `[mcp]`, `[plot]` extras are sufficient |
| New dataset files | Existing `docs/data/` datasets cover all new worked-example scenarios |

---

## Version Compatibility

| Component | Constraint | Status |
|-----------|-----------|--------|
| fdars-core 0.23.0 MSRV | Rust 1.81 | Satisfied by pyfda's 1.83 toolchain |
| pyfda MSRV | Rust 1.83 | Unchanged; CI matrix `[stable, "1.83"]` unaffected |
| PyO3 0.28 + abi3-py39 | Python 3.9–3.14 | Unchanged; fdars-core 0.23 adds no new Python constraints |
| fdars-core 0.23 parallel feature | rayon 1.10+ | Resolved: rayon 1.11.0 in current Cargo.lock; within the ^1.10 range |
| fdars-core 0.23 nalgebra | 0.33 | Resolved: nalgebra 0.33.3; within range |

---

## Sources

All findings verified directly from the local fdars-core git repository at `/home/simonm/projects/rust/fdars`:

- `git show v0.23.0:fdars-core/Cargo.toml` — MSRV, features, all dependency specs
- `git diff v0.20.0 v0.23.0 -- fdars-core/Cargo.toml` — confirmed single-line version-only change
- `git log --oneline v0.20.0..v0.23.0 -- fdars-core/Cargo.toml` — 3 release commits, none touch deps
- `git diff v0.20.0 v0.23.0 --name-only -- fdars-core/src/` — new/changed source files
- `git show v0.23.0:fdars-core/src/lib.rs` — full public API re-export diff
- `git show v0.23.0:fdars-core/src/{concurrent_regression,pace_fpca,outliers,depth/dispatch,depth/tvd,inference/itp,scalar_on_function/glm,elastic_regression/logistic}.rs` — struct fields and function signatures
- `/home/simonm/projects/rust/pyfda/Cargo.lock` — resolved transitive dependency versions (nalgebra 0.33.3, rayon 1.11.0, rand 0.8.5, rustfft 6.4.1, num-complex 0.4.6)
- `/home/simonm/projects/rust/pyfda/src/depth_mod.rs` — existing DepthMethod dispatch pattern to extend
- `/home/simonm/projects/rust/pyfda/Cargo.toml` — current pyfda dependency declarations and MSRV

Confidence: HIGH — all data read from local source files at the exact tagged version; no web lookups required.

---
*Stack research for: pyfda v6.0 — fdars-core 0.20.0 → 0.23.0 upgrade*
*Researched: 2026-08-20*
