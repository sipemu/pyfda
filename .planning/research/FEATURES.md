# Feature Landscape — v6.0 fdars-core 0.23 New Bindings

**Domain:** PyO3 binding layer for functional data analysis (Rust → Python)
**Researched:** 2026-08-20
**Source:** fdars-core v0.23.0 git tag — every signature and field enumerated directly from source

---

## Table Stakes

Features that complete the expected surface of an existing submodule or close a known gap. Users of the existing `fdars` package would expect these.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| New `DepthMethod` variants in `functional_depth` / `functional_boxplot` dispatcher | v5.0 introduced the dispatcher with 4 variants; 9 new variants are already in the core enum at v0.23 | Low per variant — dispatcher pattern already exists | Wildcard arm already present; just extend the `depth_method_from_str` match |
| `tvdmss` outlier detector in `fdars.outliers` | Closes the v5.0 Phase-34 deferral: functional boxplot ships but its natural downstream outlier method (TVD-MSS) did not | Medium — two config structs, four-field result dict | Depends on `total_variation_depth_1d` already in `fdars.depth` |
| `muod` outlier detector in `fdars.outliers` | Natural companion to existing `outliergram` and `magnitude_shape_outlyingness` | Low — single config float, six-field result dict | No upstream depth dependency; pure regression on the pointwise mean |
| `sequential_transform_outliers` in `fdars.outliers` | Completes the fdaoutlier parity set; documented alongside tvdmss/muod in the upstream module | Medium — `SeqTransform` enum string-dispatch, nested result | Depends on existing `functional_boxplot`; SeqTransform variants must be string-dispatched on the Python side |
| `depthgram` in `fdars.outliers` | Completes the fdaoutlier parity set | Medium — 12-field result dict, two config floats | Univariate-only at v0.23; three `_d / _t / _t2` field triplets are identical for p=1 |
| `itp_one_pop`, `itp_two_pop`, `itp_flm` in `fdars.inference` | Interval-wise testing is the natural follow-on to the v5.0 permutation tests; same module | Medium — `ProjectionBasisType` string-dispatch, five-field result dict | Same `TestResult`-to-dict pattern as v5.0, but `ItpResult` is a different struct with `adjusted_pvalues`/`raw_pvalues` arrays instead of scalars |
| `concurrent_regression` in `fdars.regression` | Varying-coefficient FDA regression is a standard FDA method; no existing equivalent in `fdars.regression` | Medium — slice-of-matrices input (Python: list of 2D arrays), five-field result dict | Most structurally novel input shape: `predictors` is `&[FdMatrix]` -> Python `list[np.ndarray]` |

## Differentiators

Features that require a new submodule or a structurally new approach, distinguishing this milestone from routine extension.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `pace_fpca` / `PaceFpcaConfig` / `PaceFpcaResult` — new submodule | PACE FPCA is the only FDA method for sparse/irregular data; no existing equivalent in `fdars` | High — `IrregFdata` CSR format must be exposed at the Python boundary (ragged list-of-lists input), two-struct config+result, nine-field result | `IrregFdata` has no prior Python-side representation; creates a new Python input pattern |
| `functional_glm` in `fdars.regression` | Exponential-family GLM over FPC scores; covers Binomial/Poisson/Gamma/Gaussian responses; closes a gap vs. the existing binary-only `functional_logistic` | Medium-High — family string-dispatch, optional scalar covariates, 15-field result dict + predict function | Internal IRLS, re-fits FPCA internally; the `family` string must dispatch to `GlmFamily` enum |
| `elastic_multinomial` in `fdars.classification` | OvR multinomial elastic classifier extending the existing binary `elastic_logistic`; completes the classification surface for K >= 2 | Medium — five-field result dict, `class_models` as a Python list of per-class dicts | `class_models: Vec<ElasticLogisticResult>` requires nested dict serialisation; `train_probabilities` FdMatrix -> 2D ndarray |

## Anti-Features

Features to explicitly not build in v6.0.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| HTTP/SSE MCP transport | Still deferred per PROJECT.md decision | Keep stdio only; not related to v6.0 scope |
| `predict_pace_fpca` prediction for new sparse curves | Not present in v0.23 API; PACE predicts on the training set only | Document fitted/lower/upper on the training set; defer prediction to a future milestone if upstreamed |
| Automatic sigma2 estimation in PACE FPCA | Upstream defers auto-estimation: "Automatic sigma2 estimation from the raw-vs-smoothed diagonal is deferred" (pace_fpca.rs doc comment) | Caller supplies `sigma2`; document the choice |
| `linalg` feature (ridge_regression_fit) | Requires Rust 1.84+ > MSRV 1.83; not WASM-compatible | Keep `parallel`-only at v0.23 |
| Gamma family AIC comparison to R `glm()` | Module doc explicitly warns AIC magnitudes are not directly comparable (dispersion phi not folded in) | Document the divergence in the worked example |
| `serde` feature in pyfda builds | Not currently enabled; would add weight with no Python-side benefit | Not needed for PyO3 dict output |

---

## Detailed Capability Specifications

### Group A — Regression

#### A1. `concurrent_regression` -> `ConcurrentRegrResult`

**Public function at v0.23.0:**

```rust
pub fn concurrent_regression(
    response: &FdMatrix,       // n x m functional response
    predictors: &[FdMatrix],   // p matrices each n x m
    argvals: Option<&[f64]>,   // length m; None -> uniform 0..1
    bandwidth: f64,            // kernel bandwidth for beta(t) smoothing
    kernel: &str,              // "gaussian" | "epanechnikov" | "tricube"
) -> Result<ConcurrentRegrResult, FdarError>
```

**`ConcurrentRegrResult` fields (all `#[non_exhaustive]`):**

| Field | Rust type | Meaning |
|-------|-----------|---------|
| `beta_curve` | `FdMatrix` (p x m) | Smoothed varying-coefficient curves beta_k(t), one row per predictor |
| `intercept` | `Vec<f64>` (length m) | Smoothed time-varying intercept beta_0(t) |
| `fitted` | `FdMatrix` (n x m) | Fitted functional response curves |
| `residuals` | `FdMatrix` (n x m) | response - fitted |
| `argvals` | `Vec<f64>` (length m) | Shared grid used (echoed from input or uniform) |

**Python dict layout (proposed):**
- `beta_curve` -> ndarray (p, m)
- `intercept` -> ndarray (m,)
- `fitted` -> ndarray (n, m)
- `residuals` -> ndarray (n, m)
- `argvals` -> ndarray (m,)

**Input shape:** Python-side `predictors` will be `list[np.ndarray]` -> convert each element via `numpy2d_to_fdmatrix`, collect into `Vec<FdMatrix>`.

**Validation errors:** n < 2, n <= p (underdetermined), any predictor shape != (n, m), bandwidth <= 0 or non-finite, argvals length mismatch.

**Category:** Table stakes for `fdars.regression` extension. Adds varying-coefficient regression where both response and predictors are functional (same grid). No new submodule needed.

**Dependency on existing bindings:** None beyond `numpy2d_to_fdmatrix` / `fdmatrix_to_numpy2d` converters already in `convert.rs`.

#### A2. `functional_glm` -> `FunctionalGlmResult`

**Public function at v0.23.0:**

```rust
pub fn functional_glm(
    data: &FdMatrix,                         // n x m functional predictors
    y: &[f64],                               // scalar response length n
    family: GlmFamily,                       // Binomial | Poisson | Gamma | Gaussian
    scalar_covariates: Option<&FdMatrix>,    // n x q optional scalar predictors
    ncomp: usize,                            // FPC components (clamped to min(n-1, m))
    max_iter: usize,                         // IRLS max iterations
    tol: f64,                                // IRLS convergence tolerance (deviance-change)
) -> Result<FunctionalGlmResult, FdarError>
```

**`GlmFamily` variants (not `#[non_exhaustive]` — exhaustive at v0.23):**
- `Binomial` — logit link, binary y in {0.0, 1.0}
- `Poisson` — log link, non-negative integer y
- `Gamma` — inverse link (canonical, NOT log), y > 0
- `Gaussian` — identity link, converges in one IRLS step

**`FunctionalGlmResult` fields (all `#[non_exhaustive]`):**

| Field | Rust type | Meaning |
|-------|-----------|---------|
| `intercept` | `f64` | Intercept alpha |
| `beta_t` | `Vec<f64>` (m) | Functional coefficient beta(t) on the original grid |
| `beta_se` | `Vec<f64>` (m) | Pointwise standard errors of beta(t) |
| `gamma` | `Vec<f64>` (q) | Scalar covariate coefficients (empty if no scalar_covariates) |
| `fitted_values` | `Vec<f64>` (n) | Fitted means mu = g^{-1}(eta) |
| `linear_predictors` | `Vec<f64>` (n) | Linear predictors eta = X*beta |
| `ncomp` | `usize` | FPC components actually used |
| `coefficients` | `Vec<f64>` | All regression coefficients [intercept, gamma_1...gamma_K, z_1...z_P] |
| `std_errors` | `Vec<f64>` | Standard errors of all coefficients |
| `log_likelihood` | `f64` | Log-likelihood kernel at convergence |
| `deviance` | `f64` | GLM deviance D = 2(LL_saturated - LL_fitted) |
| `iterations` | `usize` | IRLS iterations performed |
| `fpca` | `FpcaResult` | Embedded FPCA for new-data projection (does NOT cross Python boundary) |
| `aic` | `f64` | -2*log_likelihood + 2*p |
| `bic` | `f64` | -2*log_likelihood + p*ln(n) |
| `family` | `GlmFamily` | Family used |

**Python dict layout (proposed):** Keys: `intercept`, `beta_t`, `beta_se`, `gamma`, `fitted_values`, `linear_predictors`, `ncomp`, `coefficients`, `std_errors`, `log_likelihood`, `deviance`, `iterations`, `aic`, `bic`, `family` (as string). The embedded `fpca` is consumed internally for predict and NOT exposed to Python — same pattern as `flm_f_test` / `flm_gof_test` in v5.0 `inference_mod.rs`, where `FregreLmResult` never crosses the Python boundary.

**`family` Python API:** string parameter (`"binomial"`, `"poisson"`, `"gamma"`, `"gaussian"`) dispatched to `GlmFamily` enum in the wrapper, returning `ValueError` on unknown strings.

**Re-fits internally:** Yes — FPCA is re-fit from `data` inside `functional_glm`. No fitted handle needed from the caller. Same internal-refit pattern as `flm_f_test`.

**AIC comparability caveat:** Gamma and Gaussian AIC magnitudes are NOT comparable to R `glm()` because phi is not folded into the log-likelihood kernel. Must be documented in the worked example.

**Category:** Differentiator — closes the gap between binary-only `functional_logistic` (already bound) and full exponential-family GLM. Extends `fdars.regression`.

**Dependency on existing bindings:** Reuses `numpy2d_to_fdmatrix`, `numpy1d_to_vec`. The optional `scalar_covariates` adds a second optional 2D array parameter — same pattern used by `fregre_lm` with `scalar_covariates`.

---

### Group B — FPCA & Classification

#### B1. `pace_fpca` / `PaceFpcaConfig` / `PaceFpcaResult`

**Public function at v0.23.0:**

```rust
pub fn pace_fpca(
    data: &IrregFdata,
    config: &PaceFpcaConfig,
) -> Result<PaceFpcaResult, FdarError>
```

**`IrregFdata` — how sparse/irregular input works:**

`IrregFdata` is a CSR-like (Compressed Sparse Row) struct with three flat `Vec<f64>` fields and an `offsets: Vec<usize>` of length n+1. Curve i has evaluation points `argvals[offsets[i]..offsets[i+1]]` and values `values[offsets[i]..offsets[i+1]]`. Each curve can have a different number of points (ragged per-curve grids — NOT a shared dense grid). The public constructor is `IrregFdata::from_lists(argvals_list: &[Vec<f64>], values_list: &[Vec<f64>])`.

**Python-side input model:** The Python wrapper must accept two Python lists of 1D ndarrays (one per curve), convert each to a `Vec<f64>`, then call `IrregFdata::from_lists`. This is a new input shape with no prior pyfda precedent — it is NOT a 2D ndarray.

**`PaceFpcaConfig` fields (no `#[non_exhaustive]` — allows struct literal in tests):**

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `ncomp` | `usize` | 3 | FPC components to extract |
| `bandwidth` | `f64` | 0.1 | Kernel bandwidth for mean/covariance smoothing |
| `sigma2` | `f64` | 0.01 | Measurement-error variance (must be > 0; required for Sigma_yi positive-definite) |
| `work_grid` | `Vec<f64>` | 51 uniform points on [0,1] | Common evaluation grid for all outputs |
| `alpha` | `f64` | 0.05 | Confidence level for bands (95% pointwise bands) |

**Python constructor:** Config struct is not `#[non_exhaustive]`, so the wrapper exposes it as keyword arguments that are converted field-by-field.

**`PaceFpcaResult` fields (all `#[non_exhaustive]`):**

| Field | Rust type | Python shape | Meaning |
|-------|-----------|-------------|---------|
| `mean` | `Vec<f64>` (m) | ndarray (m,) | Kernel-smoothed mean on the work grid |
| `eigenvalues` | `Vec<f64>` (ncomp) | ndarray (ncomp,) | Variance explained per component |
| `eigenfunctions` | `FdMatrix` (m x ncomp) | ndarray (m, ncomp) | Orthonormal eigenfunctions on the work grid |
| `scores` | `FdMatrix` (n x ncomp) | ndarray (n, ncomp) | BLUP (conditional-expectation) FPC scores |
| `fitted` | `FdMatrix` (n x m) | ndarray (n, m) | Fitted trajectories on the work grid |
| `fitted_lower` | `FdMatrix` (n x m) | ndarray (n, m) | Lower pointwise confidence band |
| `fitted_upper` | `FdMatrix` (n x m) | ndarray (n, m) | Upper pointwise confidence band |
| `argvals` | `Vec<f64>` (m) | ndarray (m,) | Work grid used (echoed from config) |
| `sigma2` | `f64` | float | Measurement-error variance used |
| `ncomp` | `usize` | int | Components actually extracted (may be < config.ncomp if fewer positive eigenvalues) |

**Result ncomp note:** `result.ncomp` may be less than `config.ncomp` when the smoothed covariance yields fewer positive eigenvalues than requested — a finite-sample artefact on sparse data. The binding must echo `result.ncomp` in the dict, not assume it matches the input.

**Validation errors:** n=0, any curve has < 2 points, work_grid < 2 points, ncomp=0, bandwidth <= 0 or non-finite, sigma2 <= 0 or non-finite, alpha not in (0,1), work_grid not sorted or contains non-finite values. Computation errors: `mean_irreg` returns non-finite values, no positive eigenvalues, Cholesky solve fails.

**Category:** Differentiator — the only FDA method for sparse/irregular longitudinal data in `fdars`. Requires a new Python input format (`IrregFdata` via list-of-lists). Belongs in a dedicated `fdars.pace_fpca` submodule (separate from `fdars.regression`) given the structurally different input format and the two-struct config+result pattern.

**Dependency on existing bindings:** None directly, but the column-major FdMatrix layout convention applies to `eigenfunctions`, `scores`, `fitted`, `fitted_lower`, `fitted_upper` — each requires `fdmatrix_to_numpy2d` conversion with transposition. The `mean` and `argvals` Vec fields use `vec_to_numpy1d`.

#### B2. `elastic_multinomial` -> `ElasticMultinomialResult`

**Public function at v0.23.0:**

```rust
pub fn elastic_multinomial(
    data: &FdMatrix,       // n x m functional data
    y: &[usize],           // class labels in 0..K (contiguous), length n
    argvals: &[f64],       // evaluation points, length m
    ncomp_beta: usize,     // B-spline basis functions for beta per OvR model
    lambda: f64,           // roughness penalty on beta
    max_iter: usize,       // IRLS max iterations per OvR model
    tol: f64,              // convergence tolerance
) -> Result<ElasticMultinomialResult, FdarError>
```

**`ElasticMultinomialResult` fields (not `#[non_exhaustive]`):**

| Field | Rust type | Python shape | Meaning |
|-------|-----------|-------------|---------|
| `n_classes` | `usize` | int | Number of classes K |
| `classes` | `Vec<usize>` | list[int] | Sorted distinct class labels (always 0..K) |
| `class_models` | `Vec<ElasticLogisticResult>` | list[dict] | One OvR binary model per class, with at minimum `alpha` and `beta_t` |
| `train_probabilities` | `FdMatrix` (n x K) | ndarray (n, K) | Row-normalised OvR posteriors |
| `predicted_classes` | `Vec<usize>` | ndarray (n,) int | Training predictions |
| `train_accuracy` | `f64` | float | Fraction correctly classified on training data |

**Label constraint:** Labels must be the contiguous range `0..K`; non-contiguous or non-zero-based labels raise `ValueError`. This must be documented.

**`class_models` serialisation:** Each `ElasticLogisticResult` should be serialised as a Python dict with at minimum `alpha: float`, `beta_t: ndarray (m,)`. Full field list can be expanded in later phases if needed; a partial dict is acceptable for v6.0.

**Prediction:** `predict_elastic_multinomial(fit, new_data, argvals) -> Vec<usize>` exists upstream but can be deferred for v6.0. `predicted_classes` in the training result dict is sufficient for worked examples.

**Category:** Differentiator — extends `fdars.classification` to K >= 2 classes with elastic (SRSF-warping) feature extraction. The existing `elastic_logistic` binary classifier is already bound.

**Dependency on existing bindings:** `numpy2d_to_fdmatrix`, `numpy1d_to_usize_vec`, `fdmatrix_to_numpy2d`. The `class_models` nested structure is new — requires manual field-by-field dict construction.

---

### Group C — Depth / Outliers / Interval Inference

#### C1. New `DepthMethod` variants in the existing dispatcher

**At v0.23.0, `DepthMethod` has 9 new variants beyond the 4 already bound:**

| New variant | String key (proposed) | Underlying function | Min-n constraint |
|-------------|----------------------|---------------------|-----------------|
| `HypographIndex` | `"hypograph_index"` | `hypograph_index_1d` | n >= 2 |
| `ModifiedHypographIndex` | `"modified_hypograph_index"` | `modified_hypograph_index_1d` | n >= 1 |
| `EpigraphIndex` | `"epigraph_index"` | `epigraph_index_1d` | n >= 2 |
| `HalfRegion` | `"half_region"` | `half_region_depth_1d` | n >= 2 |
| `ModifiedHalfRegion` | `"modified_half_region"` | `modified_half_region_depth_1d` | n >= 1 |
| `Extremal` | `"extremal"` | `extremal_depth_1d` | n >= 3 |
| `ExtremeRankLength` | `"extreme_rank_length"` | `extreme_rank_length_depth_1d` | n >= 2 |
| `LInfinity` | `"linfinity"` | `linfinity_depth_1d` | n >= 1 |
| `TotalVariation` | `"total_variation"` | `total_variation_depth_1d` (TVD component only) | n >= 3 |

**How they slot into the dispatcher:** The existing `depth_method_from_str` in `src/depth_mod.rs` is a `match` on a `&str` with a wildcard arm that raises `ValueError`. Adding the 9 new string variants extends that match. `functional_depth` and `functional_boxplot` both use `depth_method_from_str` so both pick up all 9 new methods for free once the match is extended. The error message listing accepted strings must also be updated.

**TotalVariation note:** The dispatcher dispatches only the TVD (magnitude depth) component — not the MSS shape component. The full `TvdMssResult` (both tvd and mss) is returned by the standalone `total_variation_depth_1d` function, which is separate from the dispatcher path.

**No new function parameters needed** for any of the 9 new variants — all take only `data` and `ref_data` (or just `data` for self-depth). The dispatcher already has `scale` and `nproj` for the FM/RP variants; these are unused for the new variants.

**Category:** Table stakes — natural extension of the v5.0 dispatcher pattern. Zero structural change to `functional_depth` / `functional_boxplot` Python signatures.

#### C2. New outlier detectors in `fdars.outliers`

**tvdmss:**

```
tvdmss(data: &FdMatrix, config: TvdMssConfig) -> Result<TvdMssOutliers, FdarError>
```

`TvdMssConfig` fields: `emp_factor_mss: f64` (default 1.5), `emp_factor_tvd: f64` (default 1.5), `central_region_tvd: f64` (default 0.5, informational only).

`TvdMssOutliers` fields -> Python dict:
- `magnitude_outliers` -> `list[int]` (row indices)
- `shape_outliers` -> `list[int]` (row indices)
- `tvd` -> ndarray (n,) — total variation depth per curve
- `mss` -> ndarray (n,) — modified shape similarity index per curve

Min-n: 3 curves and >= 1 column.

**muod:**

```
muod(data: &FdMatrix, config: MuodConfig) -> Result<MuodResult, FdarError>
```

`MuodConfig` fields: `factor: f64` (default 1.5, IQR multiplier).

`MuodResult` fields -> Python dict:
- `shape_outliers` -> `list[int]`
- `magnitude_outliers` -> `list[int]`
- `amplitude_outliers` -> `list[int]`
- `shape_index` -> ndarray (n,) — |corr(X_i, mu) - 1|
- `magnitude_index` -> ndarray (n,) — |intercept_i|
- `amplitude_index` -> ndarray (n,) — |slope_i - 1|

Min-n: 3 curves, >= 2 columns.

**sequential_transform_outliers:**

```
sequential_transform_outliers(
    data: &FdMatrix,
    sequence: &[SeqTransform],
    config: SeqTransformConfig,
) -> Result<SeqTransformOutliers, FdarError>
```

`SeqTransform` enum variants (to be string-dispatched on Python side):
- `T0` -> `"t0"` (identity / raw data)
- `T1` -> `"t1"` (vertical centering — subtract per-curve mean)
- `T2` -> `"t2"` (L2 normalisation)
- `D1` -> `"d1"` (lag-1 first difference)
- `D2` -> `"d2"` (identical to D1 in this implementation)

`SeqTransformConfig` fields: `depth_method: DepthMethod` (default ModifiedBand), `emp_factor: f64` (default 1.5).

`SeqTransformOutliers` fields -> Python dict:
- `per_transform_outliers` -> `list[tuple[str, list[int]]]` — (transform_name, indices) per step
- `union_outliers` -> `list[int]` — sorted deduplicated union across all steps

Python signature: `sequence` should be a `list[str]` of transform names; `depth_method` and `emp_factor` as keyword args.

Note: `SeqTransformConfig` carries a `DepthMethod` (not serde-serializable — not relevant for PyO3); the Python wrapper builds it from `depth_method` string + `emp_factor` float using the existing `depth_method_from_str` helper.

Min-n: 2 curves.

**depthgram:**

```
depthgram(data: &FdMatrix, config: DepthgramConfig) -> Result<DepthgramResult, FdarError>
```

`DepthgramConfig` fields: `outliergram_factor: f64` (default 1.5), `boxplot_factor: f64` (default 1.5).

`DepthgramResult` fields -> Python dict:
- `mbd_mei_d` / `mbd_mei_t` / `mbd_mei_t2` -> ndarray (n,) — all identical for p=1 (univariate)
- `mei_mbd_d` / `mei_mbd_t` / `mei_mbd_t2` -> ndarray (n,) — all identical for p=1
- `shape_outliers` -> `list[int]`
- `magnitude_outliers` -> `list[int]`
- `mbd` -> ndarray (n,)
- `mei` -> ndarray (n,)

Total 12 keys. For clarity in docs, the `_d/_t/_t2` triplets can be documented as "all equal for univariate data (p=1); multivariate support is a future upstream addition".

Min-n: 2 curves, >= 1 column.

**Shared `iqr_fence` helper:** The `iqr_fence` function is private in `fdars-core`. It is NOT a public binding target. No Python exposure needed.

**Category:** All four outlier detectors are table stakes (completing the fdaoutlier parity set that includes the already-bound LRT, outliergram, magnitude-shape). `tvdmss` closes the v5.0 Phase-34 deferral explicitly.

#### C3. Interval-wise testing in `fdars.inference`

**Three public functions at v0.23.0:**

```rust
pub fn itp_one_pop(
    data: &FdMatrix,                    // n x m
    argvals: &[f64],                    // length m
    mu0: Option<&[f64]>,                // optional null-hypothesis mean, length m
    basis_type: ProjectionBasisType,    // Bspline | Fourier
    nbasis: usize,                      // >= 2; actual n_basis may differ for B-splines
    n_perm: usize,                      // >= 1
    seed: u64,
) -> Result<ItpResult, FdarError>

pub fn itp_two_pop(
    data_a: &FdMatrix,                  // n_a x m
    data_b: &FdMatrix,                  // n_b x m; same m as data_a
    argvals: &[f64],                    // length m
    basis_type: ProjectionBasisType,
    nbasis: usize,
    n_perm: usize,
    seed: u64,
) -> Result<ItpResult, FdarError>

pub fn itp_flm(
    data: &FdMatrix,                    // n x m functional predictors
    y: &[f64],                          // scalar response, length n
    argvals: &[f64],                    // length m
    basis_type: ProjectionBasisType,
    nbasis: usize,
    n_perm: usize,
    seed: u64,
) -> Result<ItpResult, FdarError>
```

**`ItpResult` fields (all `#[non_exhaustive]`):**

| Field | Rust type | Python shape | Meaning |
|-------|-----------|-------------|---------|
| `adjusted_pvalues` | `Vec<f64>` (n_basis) | ndarray (n_basis,) | Interval-wise closure-adjusted p-values per basis component |
| `raw_pvalues` | `Vec<f64>` (n_basis) | ndarray (n_basis,) | Raw per-component permutation p-values (+1 correction) |
| `basis_type` | `ProjectionBasisType` | str | `"bspline"` or `"fourier"` |
| `n_basis` | `usize` | int | Actual basis functions used (may differ from requested `nbasis` for B-splines) |
| `n_perm` | `usize` | int | Permutations used |

**Python dict layout:** `{"adjusted_pvalues": ndarray, "raw_pvalues": ndarray, "basis_type": str, "n_basis": int, "n_perm": int}`.

**`ProjectionBasisType` Python dispatch:** `"bspline"` -> `Bspline`, `"fourier"` -> `Fourier`. Unknown string -> `ValueError`. Default should be `"bspline"` (matches the R `fdatest` default).

**`mu0` in `itp_one_pop`:** Python `None` maps to `Option::None` (test H_0: mu(t) = 0). Python array of length m maps to `Option::Some`.

**Relationship to v5.0 `TestResult` pattern:** `ItpResult` is structurally different from `TestResult`. `TestResult` has three scalar fields (`statistic: f64`, `p_value: f64`, `n_perm: usize`). `ItpResult` has two vector fields (`adjusted_pvalues`, `raw_pvalues`) plus metadata. The mapping function must be `itp_result_to_pydict` — a NEW helper distinct from `test_result_to_pydict`. The `fdars.inference` Python module gains three new functions alongside the existing eight.

**`seed` convention:** Same as v5.0 permutation tests — `seed=None` (Python) resolves to `0` (Rust) for deterministic byte-identical results; explicit integer overrides.

**`itp_flm` does NOT re-fit FPCA:** Unlike `flm_f_test` / `flm_gof_test` which re-fit `fregre_lm` internally, `itp_flm` projects `data` onto a basis, then permutes the scalar response `y`. The functional predictor design matrix (basis coefficients) is computed once and reused. No FPCA re-fit.

**Category:** Table stakes extension of `fdars.inference`. Same module, same PyDict output pattern (though different struct). The interval-wise adjusted p-values are novel output (vectors not scalars) but the pattern mirrors existing TestResult handling.

---

## Feature Dependencies

```
concurrent_regression
  -> numpy2d_to_fdmatrix (existing)
  -> fdmatrix_to_numpy2d (existing)
  -> vec_to_numpy1d (existing)

functional_glm
  -> numpy2d_to_fdmatrix (existing)
  -> numpy1d_to_vec (existing)
  -> GlmFamily string dispatch (new in wrapper)

pace_fpca
  -> IrregFdata::from_lists (new Python-side input format)
  -> fdmatrix_to_numpy2d (existing, for eigenfunctions/scores/fitted matrices)
  -> vec_to_numpy1d (existing)

elastic_multinomial
  -> numpy2d_to_fdmatrix (existing)
  -> numpy1d_to_usize_vec (existing)
  -> fdmatrix_to_numpy2d (existing, for train_probabilities)
  -> usize_vec_to_numpy1d (existing)

new DepthMethod variants
  -> depth_method_from_str (existing, extend the match)
  -> functional_depth / functional_boxplot (existing, unchanged signatures)

tvdmss / muod / sequential_transform_outliers / depthgram
  -> numpy2d_to_fdmatrix (existing)
  -> vec_to_numpy1d (existing)
  -> depth_method_from_str (existing, for SeqTransformConfig.depth_method)

itp_one_pop / itp_two_pop / itp_flm
  -> numpy2d_to_fdmatrix (existing)
  -> numpy1d_to_vec (existing)
  -> vec_to_numpy1d (existing)
  -> ProjectionBasisType string dispatch (new in wrapper)
  -> itp_result_to_pydict (new helper, analogous to test_result_to_pydict)
```

---

## Advisor Extension Scope

**Where grounded diagnostics make sense:**

| Capability | Advisor relevance | Rationale |
|------------|------------------|-----------|
| `tvdmss` / `muod` / `depthgram` | HIGH — closes v5.0 Phase-34 deferral | Outlier indices + depth scores are directly interpretable grounded diagnostics; `n_outliers`, `shape_vs_magnitude` breakdown; all numbers fdars-computed |
| `itp_*` tests | HIGH — natural extension of existing `inference` aspect (#14) | `adjusted_pvalues` array summarised as "significant interval count" + "minimum adjusted p-value" — fully grounded |
| `concurrent_regression` | MEDIUM | Grounded: `beta_curve.argmax()` per predictor as a computed diagnostic |
| `functional_glm` | MEDIUM | Grounded: `aic`, `deviance`, `iterations` (convergence flag) directly fdars-computed |
| `pace_fpca` | LOW | Grounded but specialised: `eigenvalues`, `ncomp` actual vs requested; advisor would rarely reach PACE scenarios |
| `elastic_multinomial` | LOW | `train_accuracy` is grounded but classification accuracy is already covered by existing `fclassif_*` aspects |

**Recommended advisor scope for v6.0:** Add outlier detection as a new aspect (#15) covering `tvdmss` / `muod` / `depthgram` (closes the Phase-34 deferral). Extend existing `inference` aspect (#14) to include ITP interval significance counts. Concurrent regression and GLM can be folded into the existing `regression` aspect diagnostics (AIC, deviance as additional fields). Skip PACE and elastic_multinomial from advisor — not enough grounding surface and specialised use-case.

---

## MVP Recommendation

**Phase ordering within v6.0:**

1. **Crate bump + regression gate** — bump `fdars-core` 0.20.0 -> 0.23.0, keep `parallel`, verify the ~560-test baseline green; this is the prerequisite for everything else.

2. **Bind all three groups in parallel** — Group A (concurrent_regression, functional_glm), Group B (pace_fpca, elastic_multinomial), Group C (depth variants + outlier detectors + ITP tests) can be worked in parallel once the crate bump is green.

3. **Advisor extension** — extend outlier detector aspect and ITP inference aspect after bindings are tested.

4. **Docs sweep** — new pages + SVGs + worked examples after advisor is in place.

**Prioritise within each group:**

- Group A: `concurrent_regression` before `functional_glm` (simpler result dict, no family dispatch)
- Group B: `elastic_multinomial` before `pace_fpca` (reuses existing FdMatrix input format; PACE needs the new IrregFdata Python input pattern)
- Group C: depth dispatcher extension before outlier detectors (one-line match extension); ITP tests after outlier detectors

**Defer:**
- `predict_elastic_multinomial` as a Python function — `predicted_classes` is already in the training result dict; cross-validated prediction can wait
- Any PACE "predict on new sparse data" — not in v0.23.0 upstream API

---

## Worked Example Data Needs

| Capability | Data needed | Available in `docs/data/`? |
|------------|------------|--------------------------|
| `concurrent_regression` | Functional response + >= 1 functional predictor, shared dense grid | Yes — canadian_weather (temperature as response, precipitation as predictor, 365-point grid) |
| `functional_glm` Binomial | Binary scalar y + functional predictor | Yes — tecator (fat content thresholded at 20% -> binary; 100-column spectra) |
| `functional_glm` Poisson | Integer count y + functional predictor | Not directly. Recommend small synthetic count data inline in the fence |
| `functional_glm` Gamma | Positive continuous y + functional predictor | Yes — tecator (fat content as continuous positive response) |
| `functional_glm` Gaussian | Continuous y + functional predictor | Yes — standard FLM example, same as `flm_f_test` in v5.0 docs |
| `pace_fpca` | Sparse/irregular longitudinal curves (list-of-lists, ragged) | NO — all existing datasets are on a dense shared grid. Must generate small synthetic sparse data inline. Keep n <= 20, <= 8 points per curve so the fence runs fast |
| `elastic_multinomial` | K >= 3 class labels + functional predictors | Yes — phoneme.csv has 5 classes (aa, ao, dcl, iy, sh) and 256 evaluation points. Subsample to 2-3 classes (e.g. "sh", "aa", "iy") and m <= 64 for fence speed |
| new depth methods (HI/MHI/EI/HRD/MHRD/Extremal/ERL/LInf/TVD) | Dense functional sample, n >= 3 | Yes — canadian_weather temperature is the standard example |
| `tvdmss` | Dense functional sample, n >= 3 | Yes — canadian_weather or tecator |
| `muod` | Dense functional sample, n >= 3, >= 2 columns | Yes — same |
| `sequential_transform_outliers` | Dense functional sample, n >= 2 | Yes — same |
| `depthgram` | Dense functional sample, n >= 2 | Yes — same |
| `itp_one_pop` | One functional sample + optional null mean | Yes — canadian_weather (test if mean temperature == 0, or any group) |
| `itp_two_pop` | Two functional samples | Yes — canadian_weather split into coast/inland groups (same split used in v5.0 two-sample tests) |
| `itp_flm` | Functional X + scalar y | Yes — tecator (fat content as scalar y + spectra as X, same as flm_f_test example) |

**Critical data note for PACE:** No existing dataset is sparse/irregular. The fence must use inline-generated synthetic data (e.g. 10 Brownian bridge curves sampled at 3-7 random points each). Keep the fence small enough that the docs build (~19 min) does not regress. The `DOCS_FAST` path must also work.

**Phoneme for elastic_multinomial:** phoneme.csv has 400 observations x 256 evaluation points x 5 classes. For the fence, subsample to 3 classes (e.g. "sh", "aa", "iy") and m <= 64 to keep SRSF warping tractable in the docs build.

---

## Sources

- `fdars-core v0.23.0:fdars-core/src/concurrent_regression.rs` — `ConcurrentRegrResult` fields, `concurrent_regression` signature; verified directly from `git show v0.23.0:`
- `fdars-core v0.23.0:fdars-core/src/scalar_on_function/mod.rs` — `GlmFamily` enum, `FunctionalGlmResult` struct (all 15 fields confirmed)
- `fdars-core v0.23.0:fdars-core/src/scalar_on_function/glm.rs` — `functional_glm` signature (7 parameters confirmed)
- `fdars-core v0.23.0:fdars-core/src/pace_fpca.rs` — `PaceFpcaConfig` (5 fields), `PaceFpcaResult` (10 fields), `pace_fpca` signature; validation errors enumerated from source
- `fdars-core v0.23.0:fdars-core/src/irreg_fdata/mod.rs` — `IrregFdata` CSR layout, `from_lists` constructor
- `fdars-core v0.23.0:fdars-core/src/elastic_regression/logistic.rs` — `ElasticMultinomialResult` (6 fields), `elastic_multinomial` signature (7 parameters), label contiguity constraint
- `fdars-core v0.23.0:fdars-core/src/depth/dispatch.rs` — `DepthMethod` enum with all 13 variants (4 existing + 9 new); `functional_depth` dispatch body
- `fdars-core v0.23.0:fdars-core/src/depth/mod.rs` — all depth module re-exports confirming which functions are public
- `fdars-core v0.23.0:fdars-core/src/outliers.rs` — `TvdMssConfig`, `TvdMssOutliers`, `MuodConfig`, `MuodResult`, `SeqTransform`, `SeqTransformConfig`, `SeqTransformOutliers`, `DepthgramConfig`, `DepthgramResult`; all function signatures; `iqr_fence` confirmed private
- `fdars-core v0.23.0:fdars-core/src/inference/itp.rs` — `ItpResult` (5 fields), `itp_one_pop` / `itp_two_pop` / `itp_flm` signatures; seed convention; itp_flm basis-projection-not-FPCA confirmed
- `fdars-core v0.23.0:fdars-core/src/inference/mod.rs` — confirmed `itp_*` functions exported from `inference`
- `fdars-core v0.23.0:fdars-core/src/basis/projection.rs` — `ProjectionBasisType` enum (Bspline, Fourier)
- `pyfda:src/inference_mod.rs` — `test_result_to_pydict` helper pattern; seed convention (`None -> 0`); existing 8 registered functions
- `pyfda:src/depth_mod.rs` — `depth_method_from_str` wildcard arm; 4 existing variants; `boxplot_result_to_pydict` pattern
- `pyfda:python/fdars/__init__.py` — submodule registration pattern; 19 existing submodules
- `pyfda/docs/data/` — dataset inventory; phoneme classes (aa, ao, dcl, iy, sh) and wine classes (1, 2, 3) confirmed via Python csv parsing
