# Coverage & Exclusions

This page is the published coverage/EXCLUDE list for `fdars.sklearn`. Its content
is **derived from `python/fdars/sklearn/_coverage.py`** — the `TRIAGE_VERDICTS` and
`EXCLUDED_METHODS` registries — so it cannot drift from the shipped code.

All 28 wrapped estimators pass the **complete `parametrize_with_checks` battery**
(sklearn's internal `check_estimator` suite) with **zero exemptions** — no
`expected_failed_checks`, no `_xfail_checks`. Methods that could not satisfy the
full battery are excluded, not exempted.

**Verified on:** sklearn 1.8.0 / Python 3.14 — 28 estimators, 1 379 checks total.

## Wrapped Estimators (28 × PASS)

All estimators listed below pass the full `check_estimator` battery.

| Estimator class | Family | sklearn mixin | fdars source | Verdict |
|-----------------|--------|--------------|--------------|---------|
| `FPCATransformer` | Transformers | `TransformerMixin` | `fdars._native.regression.fpca` | PASS |
| `BSplineSmoother` | Transformers | `TransformerMixin` | `fdars._native.smoothing.nadaraya_watson` | PASS |
| `LocalPolynomialSmoother` | Transformers | `TransformerMixin` | `fdars._native.smoothing.local_polynomial` | PASS |
| `BasisRepresentation` | Transformers | `TransformerMixin` | `fdars._native.basis.fdata_to_basis_1d` | PASS |
| `Imputer` | Transformers | `TransformerMixin` | `fdars._native.fdata` (interpolation) | PASS |
| `SplineInterpolator` | Transformers | `TransformerMixin` | `fdars._native.represent.spline_interpolate` | PASS |
| `DepthTransformer` | Transformers | `TransformerMixin` | `fdars._native.depth.fraiman_muniz_1d` | PASS |
| `NormTransformer` | Transformers | `TransformerMixin` | `fdars._native.fdata.norm_lp_1d` | PASS |
| `FPCRegressor` | Regressors | `RegressorMixin` | `fdars._native.regression.fregre_lm` | PASS |
| `PLSRegressor` | Regressors | `RegressorMixin` | `fdars._native.regression.fregre_pls` | PASS |
| `RobustFPCRegressor` | Regressors | `RegressorMixin` | `fdars._native.regression.fregre_l1` / `fregre_huber` | PASS |
| `GLMRegressor` | Regressors | `RegressorMixin` | `fdars._native.regression.fpca` + OLS (Gaussian only) | PASS |
| `NonparametricRegressor` | Regressors | `RegressorMixin` | `fdars._native.regression.fregre_np` | PASS |
| `FPCLDAClassifier` | Classifiers | `ClassifierMixin` | `fdars._native.classification.fclassif_lda` | PASS |
| `FPCQDAClassifier` | Classifiers | `ClassifierMixin` | `fdars._native.classification.fclassif_qda` | PASS |
| `FPCKNNClassifier` | Classifiers | `ClassifierMixin` | `fdars._native.classification.fclassif_knn` | PASS |
| `DDClassifier` | Classifiers | `ClassifierMixin` | `fdars._native.classification.fclassif_dd` (centroid) | PASS |
| `LogisticFPCClassifier` | Classifiers | `ClassifierMixin` | `fdars._native.regression.functional_logistic` | PASS |
| `ElasticMultinomialClassifier` | Classifiers | `ClassifierMixin` | `fdars._native.classification.elastic_multinomial` | PASS |
| `FunctionalKMeans` | Clusterers | `ClusterMixin` | `fdars._native.clustering.kmeans_fd` | PASS |
| `FuzzyFunctionalCMeans` | Clusterers | `ClusterMixin` | `fdars._native.clustering.fuzzy_cmeans_fd` | PASS |
| `FunctionalGMM` | Clusterers | `ClusterMixin` | `fdars._native.clustering.gmm_cluster` | PASS |
| `LRTOutlierDetector` | Outlier Detectors | `OutlierMixin` | `fdars._native.outliers.detect_outliers_lrt_with_dist` | PASS |
| `OutliergramDetector` | Outlier Detectors | `OutlierMixin` | `fdars._native.depth.modified_band_1d` (surrogate) | PASS |
| `MagnitudeShapeDetector` | Outlier Detectors | `OutlierMixin` | `fdars._native.outliers.magnitude_shape` (method-faithful) | PASS |
| `TVDMSSDetector` | Outlier Detectors | `OutlierMixin` | `fdars._native.depth.modified_band_1d` (surrogate) | PASS |
| `MUODDetector` | Outlier Detectors | `OutlierMixin` | `fdars._native.depth.modified_band_1d` (surrogate) | PASS |
| `DepthgramDetector` | Outlier Detectors | `OutlierMixin` | `fdars._native.depth.modified_band_1d` (surrogate) | PASS |

## Excluded Methods

The methods below are **not** wrapped as sklearn estimators. Each has a genuine
structural mismatch with the sklearn estimator contract — they are excluded, not
exempted. All remain fully available in the `fdars` functional API.

The reason codes used below are defined in `python/fdars/sklearn/_coverage.py`:

| Code | Meaning |
|------|---------|
| `ORDER_SENSITIVE` | Output depends on sample ordering within the batch; violates `check_methods_subset_invariance` |
| `IRREGULAR_INPUT` | Requires irregular functional data (`IrregFdata`), not a plain `(n_obs, n_points)` ndarray |
| `RESPONSE_DOMAIN` | Response domain constraints (e.g. y ∈ {0,1}) violated by arbitrary arrays that `check_estimators_dtypes` supplies |
| `NON_STANDARD_INPUT` | Input type is a non-standard container (list-of-matrices, paired arrays) that cannot be expressed as a single 2D ndarray |
| `NON_STANDARD_OUTPUT` | Returns a 2D or non-scalar output (e.g. functional response) incompatible with `RegressorMixin.score()` |
| `HYPERPARAMETER_SEARCH` | The method is itself a hyperparameter search; nesting it inside `GridSearchCV` is structurally wrong |
| `NOT_AN_ESTIMATOR` | A statistical test or inferential procedure with no fit/predict/transform contract |
| `SEQUENTIAL_STREAMING` | A stateful streaming algorithm; cannot be cast to the stateless batch fit/transform pattern |

| fdars method | Reason code | Plain-language reason | Functional API |
|-------------|-------------|-----------------------|----------------|
| `alignment.elastic_align_pair` | `ORDER_SENSITIVE` | Elastic curve registration output depends on batch ordering; violates subset-invariance test | `fdars.alignment.elastic_align_pair` |
| `alignment.karcher_mean` | `ORDER_SENSITIVE` | Fréchet mean of a curve set is a whole-batch statistic; output changes if rows are reordered | `fdars.alignment.karcher_mean` |
| `pace_fpca.pace_fpca` | `IRREGULAR_INPUT` | PACE FPCA operates on irregular observation grids (`IrregFdata`); cannot be expressed as a regular `(n_obs, n_points)` ndarray | `fdars.pace_fpca.pace_fpca` |
| `regression.functional_glm_binomial` | `RESPONSE_DOMAIN` | Binomial GLM requires y ∈ {0,1}; sklearn's `check_estimators_dtypes` supplies arbitrary float y, breaking the response constraint | `fdars.regression.functional_glm` |
| `regression.functional_glm_poisson` | `RESPONSE_DOMAIN` | Poisson GLM requires y ≥ 0 integer counts; arbitrary float y from the battery violates the response domain | `fdars.regression.functional_glm` |
| `regression.concurrent_regression` | `NON_STANDARD_INPUT` | Concurrent regression takes a list-of-matrices (one covariate per time point); cannot be expressed as a single 2D ndarray | `fdars.regression.concurrent_regression` |
| `regression.fosr` | `NON_STANDARD_OUTPUT` | Function-on-scalar regression returns a functional response (coefficient curve), not a scalar — incompatible with `RegressorMixin.score()` | `fdars.regression.fosr` |
| `clustering.cluster_optim` | `HYPERPARAMETER_SEARCH` | `cluster_optim` is itself a k-search procedure; wrapping it inside `GridSearchCV` is structurally circular | `fdars.clustering.cluster_optim` |
| `inference.t_perm_test` | `NOT_AN_ESTIMATOR` | A two-sample permutation t-test; produces a p-value, not a fitted model; no fit/predict/transform contract | `fdars.inference.t_perm_test` |
| `inference.f_perm_test` | `NOT_AN_ESTIMATOR` | A functional ANOVA F-test; produces a p-value, not a fitted model | `fdars.inference.f_perm_test` |
| `inference.oneway_anova_vstat` | `NOT_AN_ESTIMATOR` | One-way ANOVA V-statistic test; inferential procedure with no estimator contract | `fdars.inference.oneway_anova_vstat` |
| `inference.mean_scb` | `NOT_AN_ESTIMATOR` | Simultaneous confidence band for the functional mean; inferential summary, not an estimator | `fdars.inference.mean_scb` |
| `spm.spm_monitor` | `SEQUENTIAL_STREAMING` | Statistical process monitoring accumulates state across sequential observations; cannot be cast to stateless batch fit/transform | `fdars.spm.spm_monitor` |

!!! note "EXCLUDED ≠ EXEMPTED"
    No wrapped estimator carries a `check_estimator` exemption. Methods that cannot
    satisfy the full battery are excluded from the sklearn layer entirely and
    documented here. The functional API in `fdars` (e.g. `fdars.alignment`,
    `fdars.inference`, `fdars.spm`) is always available for excluded methods.

!!! info "Source of truth"
    This page is derived from `python/fdars/sklearn/_coverage.py`
    (`TRIAGE_VERDICTS` + `EXCLUDED_METHODS`). If you see a discrepancy between this
    page and the shipped registry, the registry takes precedence.
