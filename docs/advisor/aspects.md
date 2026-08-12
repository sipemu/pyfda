# Per-Aspect Coverage

Every fdars analysis aspect follows the same two-stage treatment: an offline
deterministic `build_diagnostics(result, method=…)` report, then grounded
`advise(…, task=…)` task families. The aspect is **always caller-specified** —
`build_diagnostics` never auto-detects it from result keys.

The three task families available for every aspect are:

| `task=` | What you get |
|---|---|
| `"interpretation"` | Plain-language reading of the diagnostic values |
| `"parameter"` | Concrete suggestions for changing hyperparameters |
| `"method"` | Recommendations for switching or combining fdars methods |

## Coverage Table

| Aspect (`method=`) | fdars source(s) | Key diagnostics (count) | Offline fence |
|---|---|---|---|
| `clustering` | `fdars.clustering.kmeans_fd` | k, cluster_means, cluster_sizes, pairwise distances, separations (7) | [python-api.md](python-api.md) |
| `smoothing` | `fdars.basis.smooth_basis_gcv`, `pspline_fit_gcv` | lambda sweep or single-fit GCV scalars (8) | — |
| `alignment` | `fdars.alignment.karcher_mean`, `karcher_mean_elastic` | mean curve stats, amplitude/phase distances, convergence (14) | — |
| `basis` | `fdars.basis.basis_nbasis_cv` | n_basis sweep, GCV curve, optimal n_basis (8) | — |
| `fpca` | `fdars.regression.fpca` | n_components, eigenvalues, cumulative variance, phase leakage (8) | [this page](#fpca) |
| `represent` | raw `Fdata` or `{"data":…,"argvals":…}` dict | grid stats, data range (10) | — |
| `depth` | `fdars.depth.*` score arrays | n_obs, depth statistics, histogram (9) | [this page](#depth) |
| `outliers` | `fdars.outliers.*` result dicts | n_outliers, outlier_fraction, magnitude/shape/outliergram ranges (10) | — |
| `classification` | `fdars.classification.*` result dicts | accuracy, cv_error_rate, fold_error_std, best_ncomp (7) | — |
| `regression` | `fdars.regression.fregre_*`, `fosr`, `fosr_fpc` | r_squared, residual stats, beta_t_range, has_fosr (8) | — |
| `regression_cv` | `fdars.regression.fregre_cv`, `model_selection_ncomp` | optimal_k, cv_curve, elbow_present (6) | — |
| `spm` | `fdars.spm.spm_phase1` | T², SPE stats, exceedance rates, eigenvalues, kurtosis check (14) | — |

---

## clustering

**fdars source:** `fdars.clustering.kmeans_fd`

Returns a dict with `centers`, `cluster`, and `k`. Pass `argvals` to enable
amplitude/phase pairwise distances between cluster means.

| Key | Meaning |
|---|---|
| `method` | Always `"clustering"` |
| `k` | Number of clusters |
| `cluster_means` | List of k mean curves (each a list of floats) |
| `cluster_sizes` | Per-cluster observation counts |
| `pairwise_amplitude_distance` | k×k matrix of amplitude distances between cluster means; `None` when `argvals` absent |
| `pairwise_phase_distance` | k×k matrix of phase distances between cluster means; `None` when `argvals` absent |
| `mean_amplitude_separation` | Mean off-diagonal amplitude distance; `None` when `argvals` absent |
| `mean_phase_separation` | Mean off-diagonal phase distance; `None` when `argvals` absent |

**Task families:** `"interpretation"` (read cluster structure) · `"parameter"` (adjust k)
· `"method"` (switch to elastic alignment + clustering)

---

## smoothing

**fdars source:** `fdars.basis.smooth_basis_gcv`, `fdars.basis.pspline_fit_gcv`

Two input shapes are handled. A lambda-sweep result (`lambda_values` + `gcv` keys in
the dict) fills the curve keys. A single-fit `pspline_fit_gcv` result fills only the
`optimal_*` scalars and leaves the curve keys `None`.

| Key | Meaning |
|---|---|
| `method` | Always `"smoothing"` |
| `lambda_values` | Lambda grid evaluated (list of floats); `None` for single-fit path |
| `gcv_curve` | GCV score at each lambda; `None` for single-fit path |
| `edf` | Effective degrees of freedom at each lambda; `None` for single-fit path |
| `gcv_aic_approx` | AIC-approximation curve (`n·log(GCV) + 2·edf`); `None` when edf absent |
| `gcv_bic_approx` | BIC-approximation curve (`n·log(GCV) + log(n)·edf`); `None` when edf absent |
| `optimal_lambda` | Lambda minimising GCV; `None` for single-fit path |
| `optimal_gcv` | GCV value at the optimal lambda (or the single-fit GCV) |
| `optimal_edf` | EDF at optimal lambda (or the single-fit EDF) |

**Task families:** `"interpretation"` (assess smoothing level) · `"parameter"` (adjust lambda range)
· `"method"` (switch smoother)

---

## alignment

**fdars source:** `fdars.alignment.karcher_mean`, `fdars.alignment.karcher_mean_elastic`

Pass `argvals` to enable per-observation amplitude/phase distance computation.
Without `argvals`, the distance keys are `None` but mean-curve stats are always computed.

| Key | Meaning |
|---|---|
| `method` | Always `"alignment"` |
| `mean_length` | Number of evaluation points in the Karcher mean curve |
| `mean_min` | Minimum value of the mean curve |
| `mean_max` | Maximum value of the mean curve |
| `mean_avg` | Mean value of the mean curve |
| `mean_curve` | Full Karcher mean curve as a list |
| `n_obs` | Number of aligned observations; `None` when `aligned_data` absent |
| `amplitude_distances` | Per-observation amplitude distances from the mean; `None` when `argvals` absent |
| `phase_distances` | Per-observation phase distances from the mean; `None` when `argvals` absent |
| `amplitude_mean` | Mean amplitude distance; `None` when `argvals` absent |
| `amplitude_max` | Maximum amplitude distance; `None` when `argvals` absent |
| `phase_mean` | Mean phase distance; `None` when `argvals` absent |
| `phase_max` | Maximum phase distance; `None` when `argvals` absent |
| `converged` | Whether the Karcher iteration converged; `None` if not reported |
| `n_iter` | Number of Karcher iterations taken; `None` if not reported |

**Task families:** `"interpretation"` (assess phase/amplitude separation) · `"parameter"` (adjust max iterations or tolerance)
· `"method"` (switch between elastic and non-elastic alignment)

---

## basis

**fdars source:** `fdars.basis.basis_nbasis_cv`

Accepts a pre-computed cross-validation result dict (keys `n_basis_values`, `gcv`) or
raw data + `argvals` kwargs to trigger a live `basis_nbasis_cv` call.

| Key | Meaning |
|---|---|
| `method` | Always `"basis"` |
| `n_basis_values` | Basis count grid evaluated (list of ints) |
| `gcv_curve` | GCV score at each n_basis (list of floats) |
| `edf` | Effective degrees of freedom at each n_basis; `None` when absent |
| `gcv_aic_approx` | AIC approximation curve; `None` when edf or n_obs absent |
| `gcv_bic_approx` | BIC approximation curve; `None` when edf or n_obs absent |
| `optimal_n_basis` | n_basis minimising GCV |
| `optimal_gcv` | GCV at optimal n_basis |
| `optimal_edf` | EDF at optimal n_basis |

**Task families:** `"interpretation"` (assess basis complexity) · `"parameter"` (widen/narrow n_basis range)
· `"method"` (switch basis family)

---

## fpca

**fdars source:** `fdars.regression.fpca`

Returns a dict with `scores`, `singular_values`, `rotation`, `mean`. Eigenvalues are
derived as `singular_values² / (n−1)`, matching `FPCAResult.explained_variance`.

| Key | Meaning |
|---|---|
| `method` | Always `"fpca"` |
| `n_components` | Number of retained FPC components |
| `n_obs` | Number of observations (rows in scores) |
| `eigenvalues` | Per-component eigenvalues (list of floats) |
| `explained_variance_ratio` | Per-component fraction of total variance |
| `cumulative_variance_explained` | Running cumulative explained variance |
| `total_variance` | Sum of all eigenvalues |
| `phase_leakage_indicator` | Fraction of variance NOT explained by the first component; high value (≥ 0.5) suggests phase variation leaking into the amplitude decomposition |
| `phase_leakage_flagged` | `True` when `phase_leakage_indicator > 0.5` |

**Task families:** `"interpretation"` (read scree / phase leakage) · `"parameter"` (change n_comp)
· `"method"` (use elastic FPCA instead)

The fence below loads the Canadian Weather dataset, runs `fpca`, and builds the offline
diagnostics report. No API key is required — this runs live in the docs build.

```python exec="1" html="1" source="above"
from docs_data import load_canadian_weather
from fdars import regression
from fdars.advisor import build_diagnostics

day, X, meta = load_canadian_weather("temperature")
fp = regression.fpca(X, day, n_comp=4)
diag = build_diagnostics(fp, method="fpca")

print(f"n_components:                      {diag['n_components']}")
print(f"cumulative_variance_explained[0]:  {diag['cumulative_variance_explained'][0]:.4f}  FDARS_FENCE_OK")
print(f"phase_leakage_indicator:           {diag['phase_leakage_indicator']:.4f}")
print(f"phase_leakage_flagged:             {diag['phase_leakage_flagged']}")
```

---

## represent

**fdars source:** raw `Fdata` object or `{"data": …, "argvals": …}` dict (pre-analysis check)

`represent` is a data-quality check that operates on the **input data**, not on an fdars
method output. Pass either an `Fdata` object or a plain dict with `"data"` and `"argvals"` keys.

| Key | Meaning |
|---|---|
| `method` | Always `"represent"` |
| `n_obs` | Number of functional observations (rows) |
| `n_points` | Number of evaluation grid points (columns) |
| `argvals_min` | Minimum grid value |
| `argvals_max` | Maximum grid value |
| `argvals_spacing_mean` | Mean spacing between adjacent argvals; `None` when fewer than 2 grid points |
| `argvals_spacing_std` | Std of argval spacing; `None` when fewer than 2 grid points |
| `is_uniform_grid` | `True` when `spacing_std / spacing_mean < 0.01` (or trivially uniform) |
| `data_range_min` | Minimum value in the data matrix |
| `data_range_max` | Maximum value in the data matrix |
| `data_range_mean` | Mean value in the data matrix |

**Task families:** `"interpretation"` (assess data quality / grid regularity) · `"parameter"` (adjust grid density or range)
· `"method"` (switch to irregular-grid methods if `is_uniform_grid=False`)

---

## depth

**fdars source:** any `fdars.depth.*` function — `fraiman_muniz_1d`, `modal_1d`,
`random_projection_1d`, etc. All depth functions return a raw `ndarray (n,)` score
array, **not** a dict. Pass the array directly to `build_diagnostics`.

The `method_name` keyword is required: it names the depth variant used.

```python
diag = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")
```

| Key | Meaning |
|---|---|
| `method` | Always `"depth"` |
| `method_name` | Caller-supplied depth method name (e.g. `"fraiman_muniz"`, `"modal"`) |
| `n_obs` | Number of observations |
| `depth_min` | Minimum depth score (most peripheral curve) |
| `depth_max` | Maximum depth score (most central curve) |
| `depth_mean` | Mean depth score |
| `depth_median` | Median depth score |
| `depth_q10` | 10th-percentile depth score (flags peripheral curves) |
| `depth_q90` | 90th-percentile depth score |
| `depth_histogram` | 10-bucket histogram of depth scores (list of 10 ints) |

**Task families:** `"interpretation"` (read depth distribution) · `"parameter"` (adjust depth method parameters)
· `"method"` (switch depth variant)

The fence below loads the Canadian Weather dataset, computes Fraiman–Muniz depth scores,
and builds the offline diagnostics report. No API key is required — this runs live in the
docs build.

```python exec="1" html="1" source="above"
from docs_data import load_canadian_weather
from fdars import depth
from fdars.advisor import build_diagnostics

day, X, meta = load_canadian_weather("temperature")
scores = depth.fraiman_muniz_1d(X, X)
diag = build_diagnostics(scores, method="depth", method_name="fraiman_muniz")

print(f"n_obs:       {diag['n_obs']}")
print(f"depth_mean:  {diag['depth_mean']:.4f}  FDARS_FENCE_OK")
print(f"depth_q10:   {diag['depth_q10']:.4f}")
print(f"depth_q90:   {diag['depth_q90']:.4f}")
```

---

## outliers

**fdars source:** `fdars.outliers.detect_outliers_lrt`,
`fdars.outliers.detect_outliers_lrt_with_dist`,
`fdars.outliers.outliergram`,
`fdars.outliers.magnitude_shape`

Four result shapes are handled by key-presence guards. `magnitude_shape` returns **no**
`"outliers"` key — `n_outliers` and `outlier_fraction` are `None` for that variant.

| Key | Meaning |
|---|---|
| `method` | Always `"outliers"` |
| `n_obs` | Number of observations (inferred from whichever array is present) |
| `n_outliers` | Count of flagged outliers; `None` for `magnitude_shape` results |
| `outlier_fraction` | Fraction flagged; `None` when `"outliers"` key absent |
| `threshold` | LRT threshold when present; `None` otherwise |
| `has_magnitude_shape` | `True` when `"magnitude"` and `"shape"` keys both present |
| `magnitude_range` | `[min, max]` of magnitude scores; `None` when absent |
| `shape_range` | `[min, max]` of shape scores; `None` when absent |
| `has_outliergram` | `True` when `"mei"` and `"mbd"` keys both present |
| `mei_range` | `[min, max]` of MEI scores; `None` when absent |
| `mbd_range` | `[min, max]` of MBD scores; `None` when absent |

**Task families:** `"interpretation"` (read outlier count and type) · `"parameter"` (adjust threshold or alpha)
· `"method"` (combine LRT + magnitude–shape for a richer outlier picture)

---

## classification

**fdars source:** `fdars.classification.fclassif_lda`, `fclassif_qda`, `fclassif_knn`,
`fclassif_kernel`, `fclassif_dd`, `fclassif_cv`

Two result shapes are handled: point-estimate functions return `"accuracy"`;
`fclassif_cv` returns `"error_rate"` (emitted as `cv_error_rate`) and has no `"accuracy"` key.

`n_classes` **cannot be inferred from the result dict** — supply it explicitly:

```python
diag = build_diagnostics(result, method="classification", n_classes=K)
```

| Key | Meaning |
|---|---|
| `method` | Always `"classification"` |
| `n_obs` | Number of observations (from `predicted` length); `None` for CV-only results |
| `n_classes` | Caller-supplied ground-truth class count; `None` when not passed |
| `accuracy` | Proportion correctly classified; derived as `1 - cv_error_rate` when only CV result present |
| `error_rate` | `1 - accuracy` for point-estimate results; `None` for CV-only |
| `cv_error_rate` | CV error rate from `fclassif_cv` (raw key `"error_rate"`); `None` for point-estimate |
| `fold_error_std` | Std of per-fold errors (CV path); `None` for point-estimate |
| `best_ncomp` | Number of FPC components minimising CV error; `None` for point-estimate |

**Task families:** `"interpretation"` (read classification accuracy and CV stability) · `"parameter"` (tune k / n_comp)
· `"method"` (switch classifier)

---

## regression

**fdars source:** `fdars.regression.fregre_lm`, `fregre_pls`, `fregre_l1`,
`fregre_huber`, `fregre_np`, `fosr`, `fosr_fpc`

Note that `fregre_l1` and `fregre_huber` do **not** return `r_squared` — that key is
`None` for robust regression variants. `fosr`/`fosr_fpc` return 2-D residuals (shape
`n × m`); residual summary statistics are computed only for 1-D residual arrays.

| Key | Meaning |
|---|---|
| `method` | Always `"regression"` |
| `n_obs` | Number of observations (inferred from `fitted_values` or `fitted`) |
| `r_squared` | Coefficient of determination; `None` for `fregre_l1` / `fregre_huber` |
| `residual_mean` | Mean residual; `None` for `fosr`/`fosr_fpc` (2-D residuals) |
| `residual_std` | Std of residuals; `None` for `fosr`/`fosr_fpc` |
| `residual_max_abs` | Maximum absolute residual; `None` for `fosr`/`fosr_fpc` |
| `residual_skew` | Pure-NumPy skewness of residuals; `None` for `fosr`/`fosr_fpc` |
| `beta_t_range` | `[min, max]` of `beta_t`; `None` for `fregre_np` and `fosr`/`fosr_fpc` |
| `has_fosr` | `True` only when `"fitted"` key is present AND the array is 2-D |

**Task families:** `"interpretation"` (read model fit and residual behaviour) · `"parameter"` (adjust regularisation)
· `"method"` (switch between scalar-response and function-on-scalar regression)

---

## regression_cv

**fdars source:** `fdars.regression.fregre_cv`, `fdars.regression.model_selection_ncomp`

Two source functions are detected by key presence: `fregre_cv` exposes `"optimal_k"`;
`model_selection_ncomp` exposes `"best_ncomp"` and `"criteria"`.

| Key | Meaning |
|---|---|
| `method` | Always `"regression_cv"` |
| `optimal_k` | Chosen number of components or nearest neighbours |
| `min_cv_error` | Minimum CV error; `None` for `model_selection_ncomp` |
| `cv_curve` | CV error (or GCV) values per k (list of floats) |
| `k_values` | Component counts matching `cv_curve` (list of ints) |
| `cv_curve_range` | `[min, max]` of `cv_curve`; `None` when curve is empty |
| `elbow_present` | `True` when the CV curve has a strict local minimum at an interior index (not at boundary) |

**Task families:** `"interpretation"` (read optimal k and curve shape) · `"parameter"` (widen k range to expose elbow)
· `"method"` (switch CV strategy or regression variant)

---

## spm

**fdars source:** `fdars.spm.spm_phase1`

SPM is the only aspect whose builder makes a live fdars call:
`fdars.spm.spe_moment_match_diagnostic(spe_values)` — a deterministic pure-moment
computation with no RNG, fully offline. The call is wrapped in `try/except` so
`spe_kurtosis_excess` and `spe_moment_match_adequate` degrade to `None` gracefully
when the compiled extension is unavailable.

| Key | Meaning |
|---|---|
| `method` | Always `"spm"` |
| `n_obs` | Number of observations (from T² array length) |
| `ncomp` | Number of PCA components retained |
| `t2_limit` | Hotelling T² control limit |
| `spe_limit` | SPE (Q) control limit |
| `t2_max` | Maximum T² value across all observations |
| `t2_mean` | Mean T² value |
| `t2_exceedance_rate` | Fraction of observations exceeding `t2_limit` |
| `spe_max` | Maximum SPE value |
| `spe_mean` | Mean SPE value |
| `spe_exceedance_rate` | Fraction of observations exceeding `spe_limit` |
| `eigenvalues` | PCA eigenvalues (list of floats, length = ncomp) |
| `variance_explained_cumulative` | Running cumulative variance explained |
| `spe_kurtosis_excess` | Excess kurtosis of the SPE distribution (from `spe_moment_match_diagnostic`); `None` when fdars unavailable |
| `spe_moment_match_adequate` | `True` when the SPE distribution is adequately moment-matched; `None` when fdars unavailable |

**Task families:** `"interpretation"` (read process stability and exceedance rates) · `"parameter"` (adjust ncomp or significance level)
· `"method"` (add UCL monitoring or switch to functional T² variants)
