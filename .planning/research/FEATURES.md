# Feature Research: fdars-core 0.24.0 → 0.33.0 New Capabilities

**Domain:** PyO3 binding layer — functional data analysis (Rust → Python)
**Researched:** 2026-09-02
**Confidence:** MEDIUM (docs.rs API pages + CHANGELOG cross-verified; function signatures confirmed from struct pages; linalg gating inferred from docs annotations and Cargo.toml features section)

---

## Scope

This file covers **only** capabilities added in fdars-core 0.24.0 through 0.33.0. All capabilities present in 0.23.0 are already bound in pyfda and are excluded.

**Version map** (versions that actually exist on crates.io):

| Version | Released | What it added |
|---------|----------|---------------|
| 0.24.0 | 2026-08-20 | Clustering advanced + FAMM extensions + SoF extensions + FoF RE |
| 0.27.0 | 2026-08-22 | Multi-FData + PDA + Density FDA + Frechet + FTS + FPCA variants |
| 0.28.0 | 2026-08-22 | FEM smoothing |
| 0.29.0 | 2026-08-30 | No new public modules (internal fixes) |
| 0.30.0 | 2026-09-01 | No new public modules (internal fixes) |
| 0.32.0 | 2026-09-02 | GAK metric + kernel k-means (in metric module) |
| 0.33.0 | 2026-09-02 | Shapelet discovery & classification |

Versions 0.25, 0.26, 0.31 do not exist on crates.io (version numbers skipped).

**MSRV at 0.33.0:** Rust 1.81 — unchanged from 0.23.0. pyfda's MSRV constraint (1.83) is satisfied.

**linalg feature at 0.33.0:** Still activates `faer 0.23` and `anofox-regression 0.4`. pyfda does NOT enable linalg. Items gated behind linalg are flagged `[LINALG-GATED]` below; they are **out of scope for this milestone**.

---

## Capability Inventory by Family

### Group A — Advanced Clustering (introduced 0.24.0)

**Module:** `fdars_core::clustering_advanced`

Four new paradigms beyond the existing k-means/fuzzy-c-means. All operate on `&FdMatrix` + `&[f64]` argvals + config struct.

#### A1. Elastic K-Means with Joint Alignment — `align_cluster_fd`

- **What it does:** Jointly aligns and clusters functional curves using Karcher-mean templates and elastic distance. Each iteration re-estimates templates via elastic mean and reassigns curves by elastic distance.
- **Why table stakes:** Elastic clustering is a standard FDA operation; aligns shape and amplitude simultaneously, unlike plain L2 k-means.
- **Signature:** `align_cluster_fd(data: &FdMatrix, argvals: &[f64], config: &AlignClusterConfig) -> Result<AlignClusterResult, FdarError>`
- **Result struct** `AlignClusterResult`:
  - `cluster: Vec<usize>` — 0-based assignments, length n
  - `templates: Vec<Vec<f64>>` — per-cluster Karcher-mean curves (k entries, each length m)
  - `distances: FdMatrix` — n x k elastic-distance matrix
  - `iterations: usize`
  - `converged: bool`
- **Config struct** `AlignClusterConfig` — k, max_iter, tol, seed, alignment sub-config
- **linalg gated?** No

#### A2. Functional DBSCAN — `dbscan_fd`

- **What it does:** Density-based clustering over functional L2 distances. Discovers clusters of arbitrary shape; labels noise curves as `None`.
- **Why table stakes:** Completes the clustering family; DBSCAN handles non-convex cluster shapes that k-means misses.
- **Signature:** `dbscan_fd(data: &FdMatrix, argvals: &[f64], config: &DbscanConfig) -> Result<DbscanResult, FdarError>`
- **Result struct** `DbscanResult`:
  - `cluster: Vec<Option<usize>>` — `None` = noise; `Some(c)` = cluster c
  - `n_clusters: usize`
  - `n_noise: usize`
  - `distances: FdMatrix` — precomputed n x n L2 distance matrix
- **Config struct** `DbscanConfig` — eps (neighborhood radius), min_samples
- **linalg gated?** No

#### A3. Per-Cluster FPCA Clustering (kCFC) — `kcfc_cluster`

- **What it does:** Assigns curves by reconstruction error under per-cluster FPCA models; iterates until labels stabilize.
- **Signature:** `kcfc_cluster(data: &FdMatrix, argvals: &[f64], config: &KcfcConfig) -> Result<KcfcResult, FdarError>`
- **Result struct** `KcfcResult`:
  - `cluster: Vec<usize>`
  - `fpca_models: Vec<Option<FpcaResult>>` — per-cluster FPCA (None if cluster empty)
  - `reconstruction_errors: FdMatrix` — n x k squared L2 errors
  - `iterations: usize`
  - `converged: bool`
- **linalg gated?** No

#### A4. Fisher-EM Discriminative-Subspace Clustering — `funfem_cluster`

- **What it does:** GMM in a discriminative subspace estimated by Fisher's criterion. Produces soft memberships and the discriminative direction matrix.
- **Signature:** `funfem_cluster(data: &FdMatrix, argvals: &[f64], config: &FunFemConfig) -> Result<FunFemResult, FdarError>`
- **Result struct** `FunFemResult` (`#[non_exhaustive]`):
  - `cluster: Vec<usize>`
  - `membership: FdMatrix` — n x k soft membership
  - `disc_subspace: FdMatrix` — discriminative directions (ncomp_eff x p_disc_eff)
  - `log_likelihood: f64`
  - `iterations: usize`
  - `converged: bool`
- **linalg gated?** No (uses nalgebra, which is always available)

**Binding priority for Group A:** Table stakes. Fills the clustering gap that existed up to 0.23. All four are bindable without linalg.

---

### Group B — Scalar-on-Function Regression Extensions (introduced 0.24.0)

**Module:** `fdars_core::scalar_on_function` — extensions to the existing `fregre_lm`/`functional_logistic` surface.

#### B1. Functional Additive Model (FAM) — `fam`

- **What it does:** Additive nonlinear scalar-on-function regression. Y_i = mu + sum_k f_k(xi_{ik}) + epsilon, where xi_{ik} are FPC scores and f_k are estimated via kernel smoothing (Muller & Yao 2008).
- **Signature:** `fam(data: &FdMatrix, y: &[f64], argvals: &[f64], scalar_covariates: Option<&FdMatrix>, config: &FamConfig) -> Result<FamResult, FdarError>`
- **Result struct** `FamResult`:
  - `fitted_values: Vec<f64>` — length n
  - `residuals: Vec<f64>`
  - `component_fits: Vec<Vec<f64>>` — per-FPC component fit
  - `intercept: f64`
  - `bandwidths: Vec<f64>`
  - `ncomp: usize`
  - `r_squared: f64`
  - `fpca: FpcaResult`
- **linalg gated?** No

#### B2. Generalized Kernel Additive Model (GKAM) — `fregre_gkam`

- **What it does:** Backfitting-based nonparametric regression over multiple functional predictors on different grids; allows scalar covariates.
- **Signature:** `fregre_gkam(predictors: &[&FdMatrix], y: &[f64], argvals_list: &[&[f64]], scalar_covariates: Option<&FdMatrix>, config: &GkamConfig) -> Result<GkamResult, FdarError>`
- **Result struct** `GkamResult`:
  - `fitted_values: Vec<f64>`
  - `residuals: Vec<f64>`
  - `component_fits: Vec<Vec<f64>>` — q x n
  - `intercept: f64`
  - `bandwidths: Vec<f64>`
  - `iterations: usize`
  - `converged: bool`
  - `r_squared: f64`
- **linalg gated?** No (uses nalgebra)

#### B3. Generalized Spectral Additive Model (GSAM) — `fregre_gsam`

- **What it does:** Additive regression using spectral (Fourier/eigenfunction) decomposition instead of kernel smoothing; single functional predictor with scalar covariates.
- **Signature:** `fregre_gsam(data: &FdMatrix, y: &[f64], argvals: &[f64], scalar_covariates: Option<&FdMatrix>, config: &GsamConfig) -> Result<GsamResult, FdarError>`
- **Result struct** `GsamResult`:
  - `fitted_values: Vec<f64>`, `residuals: Vec<f64>`, `component_fits: Vec<Vec<f64>>`, `intercept: f64`, `bandwidths: Vec<f64>`, `ncomp: usize`, `r_squared: f64`, `fpca: FpcaResult`
- **linalg gated?** No

#### B4. History-Index Scalar-on-Function Estimator — `history_index`

- **What it does:** Models response as a function of a weighted integral over the recent history of the predictor: Y_i = beta_0 + beta_1 * (sum_l gamma_l * X_i(T-u_l) * Delta_u) + epsilon.
- **Signature:** `history_index(data: &FdMatrix, y: &[f64], argvals: &[f64], config: &HistoryIndexConfig) -> Result<HistoryIndexResult, FdarError>`
- **Result struct** `HistoryIndexResult`:
  - `fitted_values: Vec<f64>`, `residuals: Vec<f64>`, `intercept: f64`, `slope: f64`
  - `gamma: Vec<f64>` — history weight function
  - `lag_grid: Vec<f64>` — lag discretisation points
  - `history_scores: Vec<f64>` — integral scores per observation
  - `r_squared: f64`
- **linalg gated?** No

#### B5. Model Selection (AIC/BIC/GCV) — `model_selection_ncomp`

- **What it does:** Selects optimal number of FPC components for `fregre_lm` via AIC, BIC, or GCV.
- **Result** `ModelSelectionResult`
- **linalg gated?** No

#### B6. GroupLasso Variable Selection — `variable_selection`

- **What it does:** Selects among multiple functional predictors via GroupLasso coordinate-descent over FPC scores.
- **Signature:** `variable_selection(predictors: &[&FdMatrix], y: &[f64], argvals_list: &[&[f64]], scalar_covariates: Option<&FdMatrix>, config: &VarSelectConfig) -> Result<VarSelectResult, FdarError>`
- **Result struct** `VarSelectResult`:
  - `active_predictors: Vec<bool>`, `coefficients: Vec<Vec<f64>>`, `fitted_values: Vec<f64>`, `residuals: Vec<f64>`, `intercept: f64`, `lambda: f64`, `r_squared: f64`, `iterations: usize`, `converged: bool`, `fpcas: Vec<FpcaResult>`
- **linalg gated?** No (uses Cholesky via nalgebra)

#### B7. FAM Permutation Test — `permutation_test_fam`

- **What it does:** Permutation significance test for each FAM additive component.
- **Config** `PermTestConfig`, **result** `PermTestResult`
- **linalg gated?** No

**Binding priority for Group B:** Table stakes (B1-B4 fill major gaps in the regression surface). B5-B7 are supporting utilities, lower priority.

---

### Group C — Functional Mixed Models: FAMM Extensions (introduced 0.24.0)

**Module:** `fdars_core::famm` — extensions to existing `fmm`/`fmm_predict`/`fmm_test_fixed`.

#### C1. Dense Functional Linear Mixed Model — `dense_flmm`

- **What it does:** FPC-score decomposition of a longitudinal/repeated-measures functional dataset with per-subject random effects (random intercept + optional random slope). Fits REML via EM.
- **Signature:** `dense_flmm(data: &FdMatrix, subject_ids: &[usize], covariates: Option<&FdMatrix>, config: &DenseFlmmConfig) -> Result<DenseFlmmResult, FdarError>`
- **Result struct** `DenseFlmmResult` (14 fields):
  - `mean_function: Vec<f64>`, `beta_functions: FdMatrix` (p x m), `random_effects: FdMatrix` (n_subjects x m)
  - `fitted: FdMatrix`, `residuals: FdMatrix`
  - `random_variance: Vec<f64>`, `sigma2_eps: f64`, `sigma2_u: Vec<f64>`, `sigma2_slope: Vec<f64>`
  - `ncomp: usize`, `n_subjects: usize`, `eigenvalues: Vec<f64>`, `n_iter: usize`, `converged: bool`
- **linalg gated?** No

#### C2. Fast Massively-Univariate Functional Mixed Model — `fast_fmm`

- **What it does:** Pointwise mixed model fitting (no FPCA basis step) — scales to large grids where `dense_flmm` is slow; optionally computes pointwise Wald inference.
- **Signature:** `fast_fmm(data: &FdMatrix, subject_ids: &[usize], covariates: Option<&FdMatrix>, config: &FastFmmConfig) -> Result<FastFmmResult, FdarError>`
- **Result struct** `FastFmmResult`:
  - `beta_matrix: FdMatrix` (p x m), `t_stats: FdMatrix` (p x m), `p_values: FdMatrix` (p x m)
  - `sigma2_eps: Vec<f64>` (length m), `sigma2_u: Vec<f64>` (length m), `n_grid: usize`
- **linalg gated?** No

#### C3. Multivariate FAMM — `multi_famm`

- **What it does:** Fits a separate `dense_flmm` per response dimension; stacks results. For multivariate functional response (e.g., D-dimensional functional phenotype).
- **Signature:** `multi_famm(data: &[FdMatrix], subject_ids: &[usize], covariates: Option<&FdMatrix>, config: &MultiFammConfig) -> Result<MultiFammResult, FdarError>`
- **Result struct** `MultiFammResult` (`#[non_exhaustive]`):
  - `components: Vec<DenseFlmmResult>` — D per-dimension models
  - `stacked_fitted: FdMatrix` — (n_total x D) x m
  - `stacked_residuals: FdMatrix` — (n_total x D) x m
  - `n_dims: usize`
- **linalg gated?** No

**Binding priority for Group C:** Differentiators. Longitudinal/repeated-measures functional data is an important use case not addressed by the existing `fmm`. Dense flmm (C1) is the core capability; fast_fmm (C2) and multi_famm (C3) are enhancements.

---

### Group D — Function-on-Function Regression: Random Effects (introduced 0.24.0)

**Module:** `fdars_core::fof_regression` — extension to existing `fof_regression`/`fof_cv`/`predict_fof`.

#### D1. Random-Effects FoF Regression — `fof_re_regression`

- **What it does:** Extends plain FoF double-FPCA regression with per-subject random intercept functions; handles repeated-measures functional data.
- **Signature:** `fof_re_regression(predictors: &FdMatrix, responses: &FdMatrix, subject_ids: &[usize], argvals_x: &[f64], argvals_y: &[f64], config: &FofReConfig) -> Result<FofReResult, FdarError>`
- **Predict:** `predict_fof_re(result: &FofReResult, new_x: &FdMatrix) -> Result<FdMatrix, FdarError>`
- **Result struct** `FofReResult` (15 fields):
  - `intercept: Vec<f64>`, `beta_surface: FdMatrix` (m_y x m_x), `fitted: FdMatrix` (n x m_y), `residuals: FdMatrix`
  - `r_squared_t: Vec<f64>`, `r_squared: f64`
  - `ncomp_x: usize`, `ncomp_y: usize`
  - `fpca_x: FpcaResult`, `fpca_y: FpcaResult`
  - `coef_matrix: FdMatrix` (ncomp_x x ncomp_y)
  - `random_effects: FdMatrix` (n_subjects x m_y)
  - `sigma2_u: Vec<f64>` (length ncomp_y), `sigma2_eps: f64`, `n_subjects: usize`
- **linalg gated?** No

**Binding priority:** Table stakes. Completes the FoF regression surface (repeated-measures is a common FDA scenario).

---

### Group E — Multivariate Functional Data Container (introduced 0.27.0)

**Module:** `fdars_core::multi_fdata`

#### E1. MultiFunData / FdComponent

- **What it does:** Stores D functional components that may live on different evaluation grids; enforces uniform observation count across components. Mirrors R `funData`.
- **Key structs:**
  - `MultiFunData` — methods: `new(components: Vec<FdComponent>) -> Result`, `n_obs()`, `n_components()`
  - `FdComponent { data: FdMatrix, argvals: Vec<f64> }`
- **linalg gated?** No
- **Binding note:** Required by `multi_famm` input and potentially by other multi-domain functions. Expose as a Python class (`FdComponent`) and factory function.

**Binding priority:** Table stakes (dependency for C3 and future multivariate methods).

---

### Group F — Principal Differential Analysis (introduced 0.27.0)

**Module:** `fdars_core::pda`

#### F1. `principal_differential_analysis`

- **What it does:** Estimates coefficient functions beta_k(t) of a linear ODE L*x(t)=0 from observed solution curves (pointwise least squares per grid point). Returns the recovered ODE operator.
- **Signature:** `principal_differential_analysis(data: &FdMatrix, argvals: &[f64], order: usize, ...) -> Result<PdaResult, FdarError>`
- **Result struct** `PdaResult` (`#[non_exhaustive]`):
  - `coefficients: Vec<Vec<f64>>` — length-`order` outer Vec; `coefficients[k]` = beta_k(t) sampled at argvals
  - `order: usize`
  - `residuals: Option<FdMatrix>` — currently always None
- **Struct** `Lfd { coefs: Vec<Vec<f64>> }` — represents the linear differential operator
- **linalg gated?** No

**Binding priority:** Differentiator. Niche but genuine new capability; no equivalent in existing bindings.

---

### Group G — Density Functional Data Analysis (introduced 0.27.0)

**Module:** `fdars_core::density_fda`

#### G1. Log-Quantile-Density (LQD) FPCA — `lqd_fpca`

- **What it does:** FPCA on density-valued functional data via the LQD embedding (maps densities to unconstrained L^2 space before PCA). Delegates SVD to existing `fdata_to_pc_1d`.
- **Signature:** `lqd_fpca(density_matrix: &FdMatrix, argvals: &[f64], ncomp: usize, n_quantile_pts: Option<usize>) -> Result<LqdFpcaResult, FdarError>`
- **Result struct** `LqdFpcaResult`: `fpca: FpcaResult`, `fve: Vec<f64>` (cumulative fraction of variance explained)
- **linalg gated?** No

#### G2. Supporting transforms

- `normalize_density(density: &[f64], argvals: &[f64]) -> Result<Vec<f64>>` — trapezoidal normalization to unit integral
- `lqd_transform(density: &[f64], argvals: &[f64], n_grid: Option<usize>) -> Result<Vec<f64>>` — forward LQD mapping
- `inverse_lqd(psi: &[f64], t_grid: &[f64], target_argvals: &[f64]) -> Result<Vec<f64>>` — inverse LQD
- `wasserstein_barycenter(densities: &[Vec<f64>], argvals: &[f64], weights: Option<&[f64]>) -> Result<Vec<f64>>` — 1D Wasserstein Frechet mean via quantile averaging

**Binding priority:** Differentiator. Density-on-density FDA is a specialized but growing area; LQD FPCA is the key entry point.

---

### Group H — Frechet Statistics on Metric Spaces (introduced 0.27.0)

**Module:** `fdars_core::frechet`

#### H1. Frechet Regression — `frechet_global_reg`, `frechet_local_reg`

- **What they do:** Regression when the response lives in a metric space (e.g., Wasserstein space of densities). Global = linear predictor weight, local = Gaussian kernel-weighted.
- **Global signature:** `frechet_global_reg(predictors: &FdMatrix, responses: &FdMatrix, argvals: &[f64], xout: &FdMatrix) -> Result<FrechetGlobalRegResult, FdarError>`
  - **Result** `FrechetGlobalRegResult`: `predicted: FdMatrix` (n_out x m), `xout: FdMatrix` (n_out x p), `x_bar: Vec<f64>` (length p)
- **Local signature:** `frechet_local_reg(predictors: &FdMatrix, responses: &FdMatrix, argvals: &[f64], xout: &FdMatrix, bandwidth: f64) -> Result<FrechetLocalRegResult, FdarError>`
  - **Result** `FrechetLocalRegResult`: `predicted: FdMatrix`, `xout: FdMatrix`, `bandwidth: f64`
- **linalg gated?** No (uses nalgebra for covariance inversion)

#### H2. Frechet Mean and Variance — `frechet_mean`, `frechet_variance`

- **What they do:** Compute the Frechet mean (weighted barycenter) and mean-squared-distance from objects to the Frechet mean in a metric space.
- **linalg gated?** No

#### H3. Frechet ANOVA — `frechet_anova`

- **What it does:** Group-difference test for metric-space responses (Dubey-Muller test). Seeded permutation for primary p-value; asymptotic chi-squared secondary.
- **Signature:** `frechet_anova(groups: &[usize], responses: &FdMatrix, argvals: &[f64], n_perm: usize, seed: u64) -> Result<FrechetAnovaResult, FdarError>`
- **Result struct** `FrechetAnovaResult`:
  - `statistic: f64`, `p_value_asymptotic: f64`, `p_value_permutation: f64`, `n_perm: usize`
  - `group_frechet_variances: Vec<f64>` (length k), `pooled_frechet_variance: f64`
  - `fn_statistic: f64`, `un_statistic: f64`, `group_labels: Vec<usize>`
- **linalg gated?** No

#### H4. Wasserstein Distance — `wasserstein2_distance`

- **What it does:** 1D 2-Wasserstein distance between two densities.
- **Trait** `MetricSpace` — defines distance measurement and weighted-Frechet-mean solving; regression/statistical routines are generic over this trait.

**Binding priority:** Differentiator. Frechet regression and ANOVA on density-valued data are genuinely new analysis capabilities not available in any existing pyfda module.

---

### Group I — Functional Time Series (introduced 0.27.0)

**Module:** `fdars_core::fts`

#### I1. Functional Time Series Model (FPCA-AR) — `ftsm`

- **What it does:** Fits FPCA + per-component AR(p) models to a time-ordered curve series. Supports h-step-ahead forecasting, multi-step iterative forecasting, and online updates.
- **Core functions:**
  - `ftsm(data: &FdMatrix, ncomp: usize, argvals: &[f64]) -> Result<FtsmResult>`
  - `ftsm_forecast(result: &FtsmResult, h: usize) -> Result<FtsmForecastResult>`
  - `ftsm_forecast_multistep(result: &FtsmResult, h: usize) -> Result<Vec<FtsmForecastResult>>`
  - `ftsm_update(result: &FtsmResult, new_curve: &[f64]) -> Result<FtsmResult>`
- **Result structs:**
  - `FtsmResult` (`#[non_exhaustive]`): `mean: Vec<f64>`, `rotation: FdMatrix` (m x ncomp), `scores: FdMatrix` (n x ncomp), `fitted: FdMatrix`, `weights: Vec<f64>`, `ncomp: usize`, `ar_models: Vec<ArModelResult>`
  - `FtsmForecastResult`: `forecast: FdMatrix` (h x m), `h: usize`
  - `ArModelResult` — per-FPC AR diagnostics
- **linalg gated?** No

#### I2. Functional PLS Forecasting — `fplsr`

- **What it does:** PLS-score-based alternative to FPCA-score AR for curve forecasting.
- **Result** `FplsrResult`
- **linalg gated?** No

#### I3. Functional ACF/PACF — `functional_acf`, `functional_pacf`

- **What they do:** Lag-h functional autocorrelation (trace of lag-h functional covariance normalized by lag-0 trace) and partial autocorrelation.
- **Result** `FacfResult`
- **linalg gated?** No

#### I4. Long-Run Covariance — `long_run_covariance`

- **What it does:** Bartlett kernel-sandwich estimator of the long-run covariance function; used in stationarity tests.
- **Result** `LongRunCovResult`
- **linalg gated?** No

#### I5. Functional Stationarity Test — `stationarity_test`

- **What it does:** KPSS-style partial-sum L2 statistic with Monte-Carlo permutation p-value.
- **Result struct** `StationarityResult` (`#[non_exhaustive]`): `statistic: f64`, `p_value: f64`, `n_perm: usize`
- **linalg gated?** No

#### I6. Functional First-Difference — `functional_difference`

- **What it does:** Functional first-difference operator (produces a curve series of length n-1).
- **linalg gated?** No

**Binding priority:** Differentiator. The complete FTS pipeline (fit -> ACF check -> stationarity test -> forecast) is a genuinely new analysis dimension not covered by existing bindings.

---

### Group J — FPCA Variants (introduced 0.27.0)

**Module:** `fdars_core::fpca_variants`

#### J1. Functional SVD / Cross-FPCA — `fsvd`

- **What it does:** Functional SVD between two paired functional datasets (X, Y on different grids); decomposes cross-covariance into singular functions and scores.
- **Signature:** `fsvd(x: &FdMatrix, argvals_x: &[f64], y: &FdMatrix, argvals_y: &[f64], ncomp: usize) -> Result<FsvdResult, FdarError>`
- **Result struct** `FsvdResult`:
  - `singular_values: Vec<f64>` (length ncomp, non-increasing)
  - `left_functions: FdMatrix` (p x ncomp, unit L2 norm on argvals_x)
  - `right_functions: FdMatrix` (q x ncomp, unit L2 norm on argvals_y)
  - `left_scores: FdMatrix` (n x ncomp)
  - `right_scores: FdMatrix` (n x ncomp)
- **linalg gated?** No (docs annotations show no feature gate)

#### J2. FPCA of Derivatives — `fpca_der`

- **What it does:** FPCA applied to the derivatives of a functional sample. Pre-differentiates curves, then runs standard FPCA.
- **linalg gated?** No

#### J3. Cross-Covariance Surface — `cross_covariance`

- **What it does:** Estimates the cross-covariance surface between two paired functional datasets.
- **linalg gated?** No

#### J4. Dynamical Correlation — `dynamical_correlation`

- **What it does:** Computes dynamical (functional) correlation between two paired samples (normalized cross-covariance trace).
- **linalg gated?** No

#### J5. Sandwich-Smoother FPCA — `ssvd`

- **What it does:** Sparse-SVD / sandwich-smoother FPCA path for noisy/sparse data.
- **linalg gated?** No (no feature annotations)

**Binding priority:** Table stakes (J1 fsvd and J3 cross_covariance) as common FDA operations. J2, J4, J5 are differentiators.

---

### Group K — FEM Surface Smoothing (introduced 0.28.0 / confirmed 0.29.0)

**Module:** `fdars_core::fem_smoothing`

#### K1. FEM/PDE-Regularized Surface Smoothing — `fem_smooth`, `fem_smooth_gcv`

- **What it does:** Laplacian-penalty smoothing over triangulated 2D domains. Assembles mass (M) and stiffness (K) matrices from P1 Lagrange elements; solves (M + lambda*K)c = y. `fem_smooth` takes fixed lambda; `fem_smooth_gcv` selects lambda via GCV on log grid.
- **Signatures:**
  - `fem_smooth(nodes: &[[f64;2]], triangles: &[[usize;3]], observations: &[(f64, f64, f64)], lambda: f64) -> Result<FemSmoothResult>`
  - `fem_smooth_gcv(nodes: &[[f64;2]], triangles: &[[usize;3]], observations: &[(f64, f64, f64)]) -> Result<FemSmoothResult>`
  - `assemble_fem_matrices(nodes: &[[f64;2]], triangles: &[[usize;3]]) -> (Vec<Vec<f64>>, Vec<Vec<f64>>)` — returns (M, K) mass and stiffness matrices
  - `fem_basis_eval(nodes, triangles, query_points: &[[f64;2]]) -> Vec<Vec<f64>>` — P1 hat function values
  - `fem_predict(nodes, triangles, coefficients: &[f64], query_points: &[[f64;2]]) -> Vec<f64>` — interpolate at new points
- **Result struct** `FemSmoothResult` — fitted surface values, lambda used, GCV score
- **linalg gated?** No (docs note: "Dense in-house assembly — no new crate dependencies; sparse solvers are deferred")

**Binding priority:** Differentiator. FEM smoothing for 2D surface-valued functional data over irregular triangulated domains is a genuinely advanced capability with no existing pyfda equivalent. Mesh input shape (nodes + triangles arrays) requires custom PyO3 conversion logic.

---

### Group L — GAK Metric + Kernel K-Means (introduced 0.32.0)

**Module:** `fdars_core::metric` (new `gak` submodule added to existing metric module)

#### L1. Global Alignment Kernel (GAK) — `gak`, `gak_gram_matrix`

- **What it does:** Triangular Global Alignment Kernel (Cuturi 2011) — a PSD similarity measure on time-series sequences. Computed via log-domain forward DP. `gak_gram_matrix` builds symmetric n x n PSD Gram matrix (unit diagonal).
- **Signatures:**
  - `gak(x: &[f64], y: &[f64], sigma: f64) -> f64` — normalized pairwise similarity [0,1]
  - `gak_gram_matrix(data: &FdMatrix, config: &GakConfig) -> Result<FdMatrix>`
  - `sigma_gak(data: &FdMatrix) -> f64` — median-distance bandwidth heuristic
- **Config struct** `GakConfig { sigma: Option<f64> }` — None = auto via `sigma_gak`

#### L2. GAK Train/Predict Gram (sklearn precomputed-kernel convention) — `gak_gram_train`, `gak_gram_predict`

- **What they do:** Training Gram (with stored self-kernels and resolved sigma) and prediction Gram (n_test x n_train); follows sklearn's precomputed kernel API.
- **Signatures:**
  - `gak_gram_train(data: &FdMatrix, config: &GakConfig) -> Result<GakGramTrain>`
  - `gak_gram_predict(train: &GakGramTrain, new_data: &FdMatrix) -> Result<FdMatrix>`
- **Result** `GakGramTrain` — stores training data reference and self-kernels
- **linalg gated?** No

**Binding priority:** Table stakes (GAK is a widely-used kernel for time-series/FDA; enables kernel SVM via `fdars.sklearn`). The train/predict split is critical for sklearn precomputed-kernel integration.

---

### Group M — Shapelet Discovery & Classification (introduced 0.33.0)

**Module:** `fdars_core::shapelet`

#### M1. Shapelet Discovery — `discover_shapelets`

- **What it does:** Finds discriminative subsequences via candidate generation across length ranges, quality scoring (information gain or F-statistic), and self-similarity pruning. Produces a ranked `ShapeletSet`.
- **Signature:** `discover_shapelets(data: &FdMatrix, labels: &[usize], config: &ShapeletDiscoveryConfig) -> Result<ShapeletSet, FdarError>`
- **Config struct** `ShapeletDiscoveryConfig` (serde-enabled, sktime-compatible defaults) — min_len, max_len, max_shapelets, quality_measure, seed, n_candidates
- **Result** `ShapeletSet` — ranked collection of `Shapelet` structs with z-normalized values + provenance

#### M2. Shapelet Transform — `shapelet_transform`, `shapelet_transform_fit`

- **What they do:** Maps curves to an n x K distance-feature matrix using a fitted `ShapeletSet`. `shapelet_transform_fit` discovers + transforms training set in one call; the resulting `ShapeletTransformFit` applies to out-of-sample curves.
- **Signatures:**
  - `shapelet_transform(shapelets: &ShapeletSet, data: &FdMatrix) -> Result<FdMatrix>` — n x K distance matrix
  - `shapelet_transform_fit(data: &FdMatrix, labels: &[usize], config: &ShapeletDiscoveryConfig) -> Result<ShapeletTransformFit>`
  - `ShapeletTransformFit::transform(data: &FdMatrix) -> Result<FdMatrix>` — out-of-sample
  - `shapelet_distance(shapelet: &Shapelet, curve: &[f64]) -> f64` — sliding-window z-normalized Euclidean distance

#### M3. Shapelet Classifier — `shapelet_classifier_fit`

- **What it does:** End-to-end discover -> transform -> classify pipeline. Inner classifier: kNN (default) or LDA.
- **Signature:** `shapelet_classifier_fit(data: &FdMatrix, labels: &[usize], argvals: &[f64], config: &ShapeletClassifierConfig) -> Result<ShapeletClassifierFit, FdarError>`
- **`ShapeletClassifierFit::predict(new_data: &FdMatrix) -> Result<Vec<usize>>`**
- **Enums:** `QualityMeasure` (InfoGain | FStatistic)
- **linalg gated?** No

#### M4. Normalization helpers — `z_normalize_window`, `z_normalize_into`

- **What they do:** Z-score normalization on a windowed segment (in-place and windowed variants).

**Binding priority:** Differentiator. Shapelet-based classification is a genuinely new analysis paradigm in pyfda (time-series/functional data classification via discriminative subsequences).

---

## Feature Classification Summary

### Table Stakes (fills obvious gaps in the existing binding surface)

| Feature | Group | Complexity | Notes |
|---------|-------|------------|-------|
| Elastic k-means joint alignment (`align_cluster_fd`) | A1 | MEDIUM | Extends existing clustering surface |
| Functional DBSCAN (`dbscan_fd`) | A2 | LOW | Simple config, familiar paradigm |
| kCFC per-cluster FPCA clustering (`kcfc_cluster`) | A3 | MEDIUM | Returns per-cluster FpcaResult |
| Function-on-function random effects (`fof_re_regression`) | D1 | HIGH | 15-field result struct; subject_ids required |
| MultiFunData container (`multi_fdata`) | E1 | LOW | Data structure only; dependency for C3 |
| Functional SVD / cross-FPCA (`fsvd`) | J1 | MEDIUM | 5-field result; cross-grid binding |
| Cross-covariance surface (`cross_covariance`) | J3 | LOW | Returns FdMatrix |
| FPCA of derivatives (`fpca_der`) | J2 | LOW | Thin wrapper |
| GAK gram matrix (`gak_gram_matrix`, `gak_gram_train`, `gak_gram_predict`) | L1/L2 | MEDIUM | sklearn precomputed-kernel convention critical |
| Model selection AIC/BIC/GCV (`model_selection_ncomp`) | B5 | LOW | Wraps existing `fregre_lm` |

### Differentiators (genuinely new analysis capability)

| Feature | Group | Complexity | Notes |
|---------|-------|------------|-------|
| Functional Additive Model (`fam`) | B1 | HIGH | Nonlinear SoF regression; new result struct |
| GKAM multi-predictor (`fregre_gkam`) | B2 | HIGH | Multiple grids; backfitting; slice-of-slice input |
| GSAM spectral additive model (`fregre_gsam`) | B3 | MEDIUM | Single-predictor variant of GKAM |
| History-index estimator (`history_index`) | B4 | MEDIUM | New lag-based model class |
| GroupLasso variable selection (`variable_selection`) | B6 | HIGH | Coordinate descent; multi-predictor |
| Dense functional mixed model (`dense_flmm`) | C1 | HIGH | Longitudinal/repeated-measures FDA; 14-field result |
| Fast pointwise mixed model (`fast_fmm`) | C2 | MEDIUM | Large-grid alternative to C1 |
| Multivariate FAMM (`multi_famm`) | C3 | HIGH | Depends on C1 + E1 |
| Principal Differential Analysis (`principal_differential_analysis`) | F1 | MEDIUM | ODE estimation from curves |
| LQD density FPCA + transforms | G1/G2 | HIGH | Density-valued data new paradigm; new module |
| Frechet regression + ANOVA | H1-H3 | HIGH | Metric space; new module; FrechetAnovaResult |
| Functional time series (ftsm + forecast + ACF + stationarity) | I1-I5 | HIGH | Multi-function new module; online update |
| Functional PLS forecasting (`fplsr`) | I2 | MEDIUM | Part of FTS group |
| Dynamical correlation (`dynamical_correlation`) | J4 | LOW | Single scalar result |
| Sandwich-smoother FPCA (`ssvd`) | J5 | MEDIUM | Sparse data path |
| FEM surface smoothing (`fem_smooth`, `fem_smooth_gcv`) | K | HIGH | Mesh input; no Python precedent in pyfda |
| Shapelet discovery + transform + classifier | M | HIGH | New classification paradigm; QualityMeasure enum |
| Fisher-EM discriminative clustering (`funfem_cluster`) | A4 | HIGH | Discriminative subspace; soft memberships |

### Anti-Features (do NOT bind this milestone)

| Anti-Feature | Why | What Instead |
|--------------|-----|--------------|
| `fregre_gsam` as first priority | Spectral additive model very niche vs GKAM | Bind `fregre_gkam` (B2) first; defer B3 if needed |
| FEM mesh helpers as primary surface | `fem_basis_eval` and `assemble_fem_matrices` are internal utilities | Expose only `fem_smooth` / `fem_smooth_gcv` / `fem_predict` |
| `explain` module additions | No new public items detected 0.23 -> 0.33 in explain | Skip |
| `function_on_scalar_2d` additions | API unchanged from 0.23 | Skip |
| Streaming depth additions | API unchanged from 0.23 | Skip |
| Landmark module additions | API unchanged from 0.23 | Skip |

---

## linalg-Gated Items (OUT OF SCOPE — pyfda does not enable linalg)

Research found **no items explicitly feature-gated behind `linalg`** in 0.24-0.33 based on docs.rs annotations and Cargo.toml inspection. The `linalg` feature enables `faer 0.23` and `anofox-regression 0.4` but the new modules (fts, frechet, density_fda, clustering_advanced, fpca_variants, fem_smoothing, shapelet, metric::gak) all use only nalgebra (always available) or in-house dense assembly.

**Conclusion:** No new capability in 0.24-0.33 is linalg-gated. All groups (A-M) are bindable with the existing `parallel`-only build.

---

## Breaking Changes to Existing Bindings

The CHANGELOG confirms **no breaking changes** in 0.24-0.33 to the public API surface that pyfda binds. Specifically:

- `scalar_on_function::fregre_lm`, `functional_logistic`, `fregre_lm_multi`, and their predict variants: signatures unchanged
- `fof_regression::fof_regression`, `fof_cv`, `predict_fof`: unchanged (new RE functions added alongside)
- `famm::fmm`, `fmm_predict`, `fmm_test_fixed`: unchanged (new functions added alongside)
- `gmm`: unchanged (funhddC_cluster verified present in 0.23)
- All previously bound modules (depth, inference, alignment, smoothing, classification, outliers, etc.): no signature drift

**Regression gate approach:** Bump `fdars-core` to 0.33.0 in Cargo.toml first as an isolated commit; run the 772-test suite; expect zero failures before adding any new bindings.

---

## Feature Dependencies

```
MultiFunData (E1) ──required-by──> multi_famm (C3)
dense_flmm (C1) ──required-by──> multi_famm (C3)
discover_shapelets (M1) ──feeds──> shapelet_transform_fit (M2) ──feeds──> shapelet_classifier_fit (M3)
lqd_transform (G2) ──feeds──> lqd_fpca (G1)
GakGramTrain (L2) ──required-by──> gak_gram_predict (L2)
ftsm (I1) ──required-by──> ftsm_forecast (I1)
ftsm (I1) ──required-by──> ftsm_update (I1)
```

---

## Suggested Binding Groups for Roadmap Phasing

Based on coupling and complexity, the capabilities cluster into four natural binding groups:

**Group 1 — Regression Depth** (extends existing `fdars.scalar_on_function` and `fdars.fof_regression`):
B1-B7 (fam, gkam, gsam, history_index, model_selection_ncomp, variable_selection, permutation_test_fam) + D1 (fof_re_regression/predict_fof_re). No new submodule needed; medium result structs.

**Group 2 — Clustering + Mixed Models** (new `fdars.clustering_advanced` submodule + FAMM extensions):
A1-A4 (clustering_advanced) + E1 (multi_fdata) + C1-C3 (dense_flmm/fast_fmm/multi_famm). High complexity; C3 depends on E1; new `fdars.clustering_advanced` submodule required.

**Group 3 — Time Series + FPCA Variants + Density + Frechet** (four new submodules, shared theme of "new analysis paradigm"):
I (fts: new `fdars.fts` submodule) + J (fpca_variants: new `fdars.fpca_variants` submodule) + G (density_fda: new `fdars.density_fda` submodule) + H (frechet: new `fdars.frechet` submodule). High complexity; fully self-contained.

**Group 4 — Advanced Methods** (GAK metric + shapelet + FEM smoothing):
L (GAK: extends `fdars.metric`) + M (shapelet: new `fdars.shapelet` submodule) + K (FEM: new `fdars.fem_smoothing` submodule). Advanced/deferrable; FEM has non-standard mesh input shape.

---

## Sources

- [fdars-core API docs 0.23.0](https://docs.rs/fdars-core/0.23.0/fdars_core/) — baseline confirmation (LOW confidence, webfetch)
- [fdars-core API docs 0.24.0](https://docs.rs/fdars-core/0.24.0/fdars_core/) — Group A/B/C/D/E attribution (LOW confidence, webfetch)
- [fdars-core API docs 0.27.0](https://docs.rs/fdars-core/0.27.0/fdars_core/) — Group F/G/H/I/J attribution (LOW confidence, webfetch)
- [fdars-core API docs 0.28.0](https://docs.rs/fdars-core/0.28.0/fdars_core/) — Group K attribution (LOW confidence, webfetch)
- [fdars-core API docs 0.32.0](https://docs.rs/fdars-core/0.32.0/fdars_core/) — Group L attribution (LOW confidence, webfetch)
- [fdars-core API docs 0.33.0](https://docs.rs/fdars-core/0.33.0/fdars_core/) — Group M + MSRV + linalg feature confirmation (LOW confidence, webfetch)
- [crates.io version list](https://crates.io/api/v1/crates/fdars-core/versions) — version dates/existence confirmation (LOW confidence, webfetch)
- [CHANGELOG.md source view](https://docs.rs/crate/fdars-core/0.33.0/source/CHANGELOG.md) — breaking-change assessment (LOW confidence, webfetch)
- Per-struct docs pages (docs.rs) — field names/types for AlignClusterResult, DbscanResult, KcfcResult, FunFemResult, FamResult, GkamResult, GsamResult, HistoryIndexResult, VarSelectResult, DenseFlmmResult, FastFmmResult, MultiFammResult, FofReResult, PdaResult, LqdFpcaResult, FrechetGlobalRegResult, FrechetLocalRegResult, FrechetAnovaResult, FtsmResult, FtsmForecastResult, FsvdResult, FemSmoothResult (LOW confidence, webfetch; cross-verified across struct + module index pages)

---

*Feature research for: pyfda v11.0 — fdars-core 0.33.0 upgrade*
*Researched: 2026-09-02*
*Confidence: MEDIUM — function signatures sourced directly from docs.rs struct/function pages; version attribution based on presence/absence checks across per-version index pages; linalg gating based on feature annotations in docs; no items fabricated.*
