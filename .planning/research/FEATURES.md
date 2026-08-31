# Feature Research

**Domain:** scikit-learn-compatible estimator layer over functional-data library (fdars v9.0)
**Researched:** 2026-08-31
**Confidence:** HIGH

---

## Scope Note

This file maps the EXISTING fdars functional API onto scikit-learn estimator shapes. It does not re-research how fdars methods work internally — only how to expose them as `BaseEstimator` subclasses. The canonical reference for what a compliant sklearn layer looks like is scikit-fda 0.10.x; the canonical rules for `check_estimator` compliance come from sklearn 1.9's developer docs.

---

## Categorized Feature Table

Each row: fdars source function(s), target sklearn mixin, table-stakes vs differentiator, complexity, notes.

### Category A — Transformers (`TransformerMixin + BaseEstimator`)

Transformers take `(n_obs, n_points)` X in `fit` and `transform`, return a transformed array. `argvals` is a constructor param defaulting to `np.arange(n_features)`. All must set `n_features_in_` via `validate_data` in `fit`.

| Estimator class | fdars source function(s) | Mixin | Priority | Complexity | Notes |
|----------------|--------------------------|-------|----------|------------|-------|
| `BSplineSmoother` | `smoothing.optim_bandwidth` + `smoothing.nadaraya_watson` (per-curve applied at transform-time) | `TransformerMixin` | **Table stakes** | MEDIUM | Bandwidth is a constructor param; `argvals` for output grid. Output shape `(n_obs, n_points)` — same grid. `fit` finds optimal `h_` via GCV/CV/AIC over training data. Straightforward. |
| `LocalPolynomialSmoother` | `smoothing.local_polynomial` | `TransformerMixin` | Table stakes | LOW | Wraps per-curve local_polynomial; `degree`, `bandwidth`, `kernel` as constructor params. |
| `BasisRepresentation` | `basis.fdata_to_basis_1d` + `basis.basis_to_fdata_1d` | `TransformerMixin` | **Table stakes** | MEDIUM | `n_basis`, `basis_type` as constructor params. `transform` returns reconstructed curves at the original `argvals` grid — same output shape, no grid change. Stores `basis_repr_` fitted state. |
| `FPCATransformer` | `regression.fpca` | `TransformerMixin` | **Table stakes** | MEDIUM | Most important transformer. `n_components` constructor param. `fit` runs FPCA, stores `components_` (eigenfunctions), `mean_`, `explained_variance_ratio_`. `transform` returns scores `(n_obs, n_components)` — this IS a grid-changing transform (functional → scalar scores). Use `ClassNamePrefixFeaturesOutMixin` for `get_feature_names_out`. Enables FPCA → sklearn RandomForest in one Pipeline. |
| `PACEFPCATransformer` | `pace_fpca.pace_fpca` + `pace_fpca.irreg_fdata_from_lists` | `TransformerMixin` | Differentiator | HIGH | Sparse/irregular PACE FPCA. Input must be dense `(n_obs, n_points)` per the v9.0 constraint (IrregFdata is awkward — see Awkward section). Can still expose for dense regular data. `n_components`, `argvals` params. |
| `Imputer` | `represent.impute_missing_values` | `TransformerMixin` | Table stakes | LOW | `method` ('linear'/'mean'/'constant'), `constant_value` as constructor params. Same output shape. Used first in Pipeline to fill NaNs before smoothing/FPCA. |
| `SplineInterpolator` | `represent.spline_interpolate_with_policy` | `TransformerMixin` | Table stakes | MEDIUM | `output_argvals` constructor param (the new grid); `policy`, `fill_value`, `order`. This IS a grid-changing transformer (output shape changes if `output_argvals` has different length). `n_features_in_` is the input grid size; output grid size differs. Must NOT use `validate_data(reset=False)` for grid count — only validate that the feature count matches what was seen at fit. |
| `DepthTransformer` | `depth.functional_depth` (dispatcher) | `TransformerMixin` | **Table stakes** | LOW | `method` constructor param (e.g. `"fraiman_muniz"`, `"modified_band"`, `"random_projection"`). `transform` returns depth scores `(n_obs, 1)` — functional → scalar. Enables depth → sklearn threshold in Pipeline. Grid-changing: functional → 1D. Use `get_feature_names_out` returning `["depth"]`. |
| `NormTransformer` | `fdata.norm_lp_1d` | `TransformerMixin` | Differentiator | LOW | `p` param. Transforms each curve to its Lp norm. Output `(n_obs, 1)`. Simple utility. |

**Grid-changing transformer convention:** When `transform` changes the number of output features (FPCA scores, depth scalars, Lp norms), `n_features_in_` records the input feature count; `get_feature_names_out()` must be implemented; downstream sklearn estimators see the scalar output naturally. `set_output` API activates automatically when `get_feature_names_out` is present and `TransformerMixin` is inherited.

**Pipeline chaining with grid-changing transforms:**

```
Pipeline([
    ("impute", Imputer(method="linear")),          # (n, m) → (n, m)
    ("smooth", BSplineSmoother(argvals=t)),         # (n, m) → (n, m)
    ("fpca",   FPCATransformer(n_components=5)),    # (n, m) → (n, 5) scores
    ("clf",    sklearn.ensemble.RandomForestClassifier()),
])
```

FPCA scores feed directly into any sklearn estimator that accepts `(n_obs, n_features)`. The pipeline is seamless because FPCATransformer outputs a plain 2D ndarray.

---

### Category B — Regressors (`RegressorMixin + BaseEstimator`)

Regressors: `fit(X, y)` where `X` is `(n_obs, n_points)` and `y` is `(n_obs,)` scalar; `predict(X)` returns `(n_obs,)`. `score(X, y)` inherits R² from `RegressorMixin`.

| Estimator class | fdars source function(s) | Mixin | Priority | Complexity | Notes |
|----------------|--------------------------|-------|----------|------------|-------|
| `FPCRegressor` | `regression.fregre_lm` + `regression.predict_fregre_lm` | `RegressorMixin` | **Table stakes** | LOW | Scalar-on-function via FPC scores. `n_comp` constructor param. `fit` stores the fitted model internals (`coef_`, `intercept_`, `beta_t_`). `predict` calls predict_fregre_lm. Simplest regressor. |
| `PLSRegressor` | `regression.fregre_pls` + `regression.predict_fregre_pls` | `RegressorMixin` | Table stakes | LOW | Like FPCRegressor but PLS. `n_comp`, `argvals` params. |
| `RobustFPCRegressor` | `regression.fregre_l1` + `regression.predict_fregre_robust` OR `regression.fregre_huber` + `regression.predict_fregre_robust` | `RegressorMixin` | Differentiator | LOW | `method` ('l1'/'huber'), `n_comp`, `huber_k` params. |
| `GLMRegressor` | `regression.functional_glm` (family='gaussian'/'poisson'/'gamma') | `RegressorMixin` | Differentiator | MEDIUM | `family`, `n_comp`, `max_iter`, `tol` params. For non-gaussian families, `score()` default R² may be misleading — consider overriding to deviance-based score. Families binomial/poisson/gamma add awkward response-domain constraints check_estimator may fail on random inputs (see Awkward section). |
| `NonparametricRegressor` | `regression.fregre_np` (from distance matrix) | `RegressorMixin` | Differentiator | HIGH | Requires precomputing a distance matrix internally during fit AND at predict time. `h`, `argvals` params. The fit+predict pattern requires re-computing distances to training data at predict time (stored as `X_fit_`). Awkward but doable. |
| `FOSRRegressor` | `regression.fosr` + `regression.predict_fosr` | `RegressorMixin` | Differentiator | MEDIUM | Function-on-scalar: `X` is `(n_obs, p)` scalar predictors; `y` is `(n_obs, m)` functional response. Unusual sklearn shape — output of `predict` is `(n_obs, m)`. Works with `MultiOutputRegressor` wrapper. `lambda_` param. |

**`score()` method:** All regressors inherit `RegressorMixin.score(X, y)` which computes R². For GLM families, R² is still valid for gaussian but odd for poisson/gamma — document clearly but do not override (preserves `check_estimator` compliance).

---

### Category C — Classifiers (`ClassifierMixin + BaseEstimator`)

Classifiers: `fit(X, y)` with integer class labels; `predict(X)` returns labels; `score(X, y)` accuracy. Must set `classes_` in `fit`.

| Estimator class | fdars source function(s) | Mixin | Priority | Complexity | Notes |
|----------------|--------------------------|-------|----------|------------|-------|
| `FPCLDAClassifier` | `classification.fclassif_lda` + internal predict (re-fit at predict time) | `ClassifierMixin` | **Table stakes** | MEDIUM | LDA via FPC scores. `ncomp` param. Must store training data for predict (no separate predict function in fdars — classification functions re-fit internally). Store `X_fit_` + `y_fit_` → call fclassif_lda(X_new) at predict using stored data. |
| `FPCQDAClassifier` | `classification.fclassif_qda` | `ClassifierMixin` | Table stakes | MEDIUM | Like LDA. `ncomp` param. |
| `FPCKNNClassifier` | `classification.fclassif_knn` | `ClassifierMixin` | **Table stakes** | MEDIUM | `ncomp`, `k` params. |
| `DDClassifier` | `classification.fclassif_dd` | `ClassifierMixin` | Differentiator | MEDIUM | Depth-based DD-classifier. No hyperparams. |
| `ElasticMultinomialClassifier` | `classification.elastic_multinomial` | `ClassifierMixin` | Differentiator | MEDIUM | `ncomp_beta`, `lambda_`, `max_iter`, `tol`, `argvals` params. Multi-class via OvR. Must handle 0-indexed contiguous labels — add label remapping (like `LabelEncoder`) in `fit` to ensure check_estimator's arbitrary label inputs work. Store `label_encoder_` in fit. |
| `LogisticFPCClassifier` | `regression.functional_logistic` + `regression.predict_functional_logistic` | `ClassifierMixin` | Table stakes | MEDIUM | Binary only (y in {0,1}). `n_comp`, `max_iter`, `tol` params. `predict_proba` returns `[[1-p, p]]` for check_estimator compliance. |

**Critical check_estimator issue for classifiers:** fdars classification functions that take training+test data together (re-fit at test time) fail the standard split-fit/predict contract. Workaround: in `fit`, store `X_fit_` and `y_fit_` (training arrays). In `predict`, concatenate `[X_fit_, X_new]`, call the fdars function, then slice out only the new predictions. This is the same pattern scikit-fda uses for its distance-based classifiers.

**Label handling:** `check_estimator` sends arbitrary integer labels including negative values. Use `sklearn.preprocessing.LabelEncoder` inside `fit` to remap labels to 0..K, store the encoder as `label_encoder_`, and inverse-transform in `predict`.

---

### Category D — Clusterers (`ClusterMixin + BaseEstimator`)

Clusterers: `fit(X)` sets `labels_`; `fit_predict(X)` returns labels.

| Estimator class | fdars source function(s) | Mixin | Priority | Complexity | Notes |
|----------------|--------------------------|-------|----------|------------|-------|
| `FunctionalKMeans` | `clustering.kmeans_fd` | `ClusterMixin` | **Table stakes** | LOW | `n_clusters`, `argvals`, `max_iter`, `tol`, `random_state` params. Sets `labels_`, `cluster_centers_`, `inertia_`. `random_state` → `seed`. |
| `FuzzyFunctionalCMeans` | `clustering.fuzzy_cmeans_fd` | `ClusterMixin` | Differentiator | LOW | `n_clusters`, `fuzziness`, `argvals`, `max_iter`, `tol`, `random_state`. Sets `labels_`, `membership_`, `cluster_centers_`. |
| `FunctionalGMM` | `clustering.gmm_cluster` | `ClusterMixin` | Differentiator | MEDIUM | `k_range` param (list) makes GridSearchCV awkward — `k_range` is not a single int. Wraps as `n_clusters_min`/`n_clusters_max` constructor params internally converted to range. Sets `labels_`, `n_clusters_`. |

**Awkward: `cluster_optim`** — the `_augment.py` `cluster_optim` function is itself a hyperparameter search loop (tries k=2..K, picks best by silhouette). Exposing it as a `ClusterMixin` creates a nested-search problem in GridSearchCV. Better pattern: exclude `cluster_optim` from the sklearn layer; instead expose `FunctionalKMeans` and let users run `GridSearchCV(FunctionalKMeans(), {"n_clusters": range(2, 10)})` which is idiomatically correct sklearn.

---

### Category E — Outlier Detectors (`OutlierMixin + BaseEstimator`)

Outlier detectors: `fit(X)` then `predict(X)` returns +1 (inlier) / -1 (outlier). `score_samples(X)` returns per-sample scores (higher = more normal). `OutlierMixin.predict` threshold uses `decision_function`. `fit_predict(X)` is inherited.

| Estimator class | fdars source function(s) | Mixin | Priority | Complexity | Notes |
|----------------|--------------------------|-------|----------|------------|-------|
| `LRTOutlierDetector` | `outliers.detect_outliers_lrt_with_dist` | `OutlierMixin` | **Table stakes** | MEDIUM | `alpha`, `n_bootstrap`, `trim`, `smo`, `random_state` params. `fit` stores threshold. `predict` applies threshold. `score_samples` returns negative LRT statistic (higher = more normal for OutlierMixin convention). |
| `OutliergramDetector` | `outliers.outliergram` | `OutlierMixin` | Table stakes | LOW | `factor` param. `fit` computes MEI/MBD reference distribution. `predict` applies outliergram flags. `score_samples` returns outliergram score. |
| `MagnitudeShapeDetector` | `outliers.magnitude_shape` | `OutlierMixin` | Table stakes | LOW | No params. Returns dual scores (magnitude + shape); for `score_samples`, use the combined L2-norm of both scores. |
| `TVDMSSDetector` | `outliers.tvdmss` | `OutlierMixin` | Differentiator | MEDIUM | `emp_factor_mss`, `emp_factor_tvd`, `central_region_tvd` params. Separates magnitude vs shape outliers; combine for `predict` (union flag). |
| `MUODDetector` | `outliers.muod` | `OutlierMixin` | Differentiator | MEDIUM | `factor` param. Three outlier types (shape/magnitude/amplitude); combine for `predict` (union flag). `score_samples` = min of three scores (most conservative). |
| `DepthgramDetector` | `outliers.depthgram` | `OutlierMixin` | Differentiator | MEDIUM | `outliergram_factor`, `boxplot_factor` params. Separate shape/magnitude; combine union. |

**OutlierMixin contract:** `OutlierMixin.predict` calls `decision_function` and thresholds at 0 (positive = inlier, negative = outlier). For fdars detectors that return binary flags (not continuous scores), you must synthesize a continuous `decision_function`: use the underlying score (e.g. depth value, MEI distance) so that the threshold is meaningful. The binary-flag-only detectors (tvdmss/muod/depthgram) must store score vectors at fit time, then use scores for `decision_function` and the binary flags for the trained threshold at `predict`.

---

## Awkward-to-Wrap Aspects and Reasons

| fdars aspect | Awkwardness | Recommended handling |
|-------------|-------------|---------------------|
| **PACE FPCA (`pace_fpca`)** | Requires `IrregFdata` opaque handle (ragged lists), not plain ndarray. v9.0 constraint says estimators take plain `(n_obs, n_points)` arrays. | Expose for DENSE regular input only: internally build IrregFdata from the regular grid data. PACE for sparse/irregular data is outside scope of the sklearn layer (keep the raw API). |
| **Registration/elastic alignment (`alignment.elastic_fpca`, `karcher_mean`)** | Registration requires a TEMPLATE (Karcher mean must be computed from training data). The template IS a fitted attribute (`template_`). But `check_estimator` tests include tiny-sample (n=2,3) checks — elastic FPCA/Karcher mean may fail on n<5. | Expose `ShiftRegistrationTransformer` (least-squares shift, well-behaved on small n). Exclude full elastic FPCA from the sklearn layer unless it passes check_estimator. |
| **`classification.fclassif_kernel`** | Requires `argvals` AND separate `h_func`/`h_scalar` bandwidth parameters — no automatic bandwidth selection in the binding, so users must supply `h_func`. Not `check_estimator`-safe without a sensible default. | Include with `h_func=1.0` default. Flag in docs that CV-optimal bandwidth requires calling `fregre_np_cv` separately (or via GridSearchCV over h_func). |
| **`clustering.gmm_cluster` k_range** | `k_range` is a list, not a scalar — GridSearchCV can't vary it cleanly. | Expose `FunctionalGMM(n_clusters_min, n_clusters_max)` instead, internally building the range. |
| **`regression.concurrent_regression`** | Takes a LIST of predictor matrices (one per predictor), not a single `(n_obs, n_points)` X. Not mappable to standard sklearn regressor shape. | Exclude from sklearn layer. Keep only in the functional API. |
| **`regression.fosr` (function-on-scalar)** | Output of `predict` is `(n_obs, m)` — a 2D functional response. sklearn's `RegressorMixin.score` assumes scalar y. | Expose as `MultiOutputRegressor`-compatible but do NOT use `RegressorMixin.score` — override `score` to return mean R² across grid points, and document. |
| **`outliers.*` binary-flag results (tvdmss, muod, depthgram)** | These detectors categorize by TYPE (shape vs magnitude vs amplitude) — no single continuous decision score by design. `OutlierMixin.decision_function` assumes a single score. | Pick the most meaningful continuous score for each detector (e.g., TVD for tvdmss, shape_index for muod) to drive `decision_function`; union flags for `predict`. |
| **`regression.fregre_np` (nonparametric)** | Needs the training data at predict time to compute distances to new points — must store `X_fit_` (potentially large). | Include but document the memory cost. `n_jobs` parameter for distance computation not available (Rust is parallel internally). |
| **`inference.*` tests (permutation, SCB, ANOVA)** | Hypothesis tests don't have a fit/predict contract. They answer "is there a difference?" not "what class/value is this?". | Out of scope. Do not wrap as estimators. |
| **SPM monitoring** | Temporal/sequential monitoring — not a batch fit/predict estimator. | Out of scope. |
| **`regression.functional_glm` check_estimator** | Non-gaussian families (binomial, poisson, gamma) have response-domain constraints (y > 0, y in {0,1}) that `check_estimator` violates by sending random float inputs. | For `GLMRegressor(family="binomial")`, add sklearn's `__sklearn_tags__` to indicate `requires_positive_y` (poisson/gamma) or binary y constraints, OR exclude non-gaussian families and expose only `family="gaussian"` (Gaussian GLM = standard functional regression). |
| **`classification` functions re-fit at predict time** | All fclassif_* functions take both training and test data together — no stored model state from fit. To implement predict, store `X_fit_`, `y_fit_` at fit time and concatenate at predict time. | Store training arrays in fit; slice new predictions from concatenated call. Documents as a known overhead (O(n_train + n_test) per predict call). |

---

## sklearn Contract — Pipeline/GridSearchCV Usage Conventions

### `argvals` as a constructor param

```python
class FPCATransformer(TransformerMixin, BaseEstimator):
    def __init__(self, n_components=3, argvals=None):
        self.n_components = n_components
        self.argvals = argvals  # stored as-is, resolved in fit

    def fit(self, X, y=None):
        argvals = np.arange(X.shape[1]) if self.argvals is None else np.asarray(self.argvals)
        X = validate_data(self, X, dtype=np.float64)  # sets n_features_in_
        ...
```

`argvals=None` + resolve-in-fit is the correct pattern: it is clone-safe (no ndarray in `__init__` default), `get_params()` returns `None` (or the user-supplied array), and `set_params(argvals=t)` works cleanly in GridSearchCV.

### `n_features_in_` and grid-changing transforms

- All estimators call `validate_data(self, X, dtype=np.float64)` in `fit` — this automatically sets `n_features_in_` to `X.shape[1]`.
- For `transform(X)`, call `validate_data(self, X, reset=False)` to verify input shape matches fit-time shape.
- For grid-changing transformers (FPCA, DepthTransformer, SplineInterpolator with different output grid), `n_features_in_` records the input grid size; a separate attribute records the output size (e.g., `n_components_` for FPCA, `n_output_features_` for interpolator).
- `get_feature_names_out()` must be implemented for all transformers that change feature count; this enables `set_output(transform="pandas")`.

### `score()` methods

- Transformers: no `score()` needed.
- Regressors: `RegressorMixin.score(X, y)` provides R² out of the box — do not override unless the output is non-scalar (FOSRRegressor).
- Classifiers: `ClassifierMixin.score(X, y)` provides accuracy — standard.
- Clusterers: `ClusterMixin` has no `score()`; users access `inertia_` or call `silhouette_score` from sklearn separately.
- Outlier detectors: `OutlierMixin` provides `score_samples(X)` via `decision_function(X)` — implement `decision_function`, inherit `score_samples`.

### `clone` safety

- `__init__` must assign constructor params with exactly the same name: `self.n_components = n_components`. No transformation.
- `argvals=None` default is clone-safe (None is immutable); a numpy array default would NOT be clone-safe.
- `random_state` (not `seed`) should be the sklearn-convention param name; convert to `seed: u64` inside `fit`.

### `check_estimator` small-sample and dtype checks

The most likely failures:

1. **n_obs=1 check** — fdars functions that require n >= 2 or n >= 3 (muod, tvdmss, etc.) will raise ValueError on the single-sample test. Solution: add `check_is_fitted` and an explicit `n >= 2` check in `fit` that raises `ValueError("n_samples=1 is insufficient")`.
2. **dtype cast** — `check_estimator` sends float32 inputs. All fdars functions require float64 (Rust binding). Solution: use `validate_data(self, X, dtype=np.float64)` which handles coercion automatically.
3. **n_features mismatch** — `validate_data(reset=False)` in `transform`/`predict` enforces this.
4. **Classes not in `classes_`** — classifiers must store `classes_` via `unique_labels(y)` in `fit`; fdars expects 0-indexed contiguous labels, so wrap with `LabelEncoder`.
5. **Non-finite input** — fdars functions may panic or produce NaN on non-finite inputs that check_estimator sends. Solution: `validate_data(..., force_all_finite=True)` raises before reaching Rust.

---

## Feature Dependencies

```
Imputer                          (no deps)
    feeds BSplineSmoother        (no deps, but Imputer should come first in Pipeline)
    feeds LocalPolynomialSmoother

BSplineSmoother feeds FPCATransformer
FPCATransformer feeds FPCRegressor (FPCA scores → LM coefficients)
FPCATransformer feeds any sklearn estimator (scores are plain ndarray)

DepthTransformer requires depth.functional_depth dispatcher (already bound)
OutliergramDetector requires outliers.outliergram (already bound)

LabelEncoder wrapper required by all Classifiers (for check_estimator label remapping)
validate_data pattern required by ALL estimators (n_features_in_)
_resolve_argvals helper required by every estimator calling an fdars argvals-taking function
```

### Dependency notes

- **FPCATransformer** is the central hub: almost all regression/classification pipelines go through it. Build and validate FPCATransformer first; then regression/classification wrappers are straightforward.
- **LabelEncoder** dependency in all classifiers: fdars elastic_multinomial requires 0-indexed contiguous labels; other classifiers (fclassif_lda, etc.) expect usize labels. All must go through LabelEncoder in fit to be check_estimator-safe.
- **`argvals` resolution pattern** (None → arange in fit) is shared by EVERY estimator that calls an fdars function requiring argvals — implement once as a module-level helper `_resolve_argvals(argvals, n_features)`.

---

## MVP Definition

### Phase 1 — Foundation + Core Transformers (build first)

- [ ] Module skeleton `python/fdars/sklearn/` with `__init__.py`, `_base.py` (shared helpers: `_resolve_argvals`, `_validate_fit_data`)
- [ ] `FPCATransformer` — the central hub; validates the entire Pipeline integration story
- [ ] `Imputer` — upstream preprocessing, needed for realistic pipelines
- [ ] `BSplineSmoother` — the primary smoothing transformer
- [ ] `DepthTransformer` — depth → scalar, tests the grid-changing transformer pattern

### Phase 2 — Regression + Classification (core predictors)

- [ ] `FPCRegressor` — simplest and most common regression use case
- [ ] `PLSRegressor` — PLS alternative
- [ ] `FPCLDAClassifier`, `FPCQDAClassifier`, `FPCKNNClassifier` — discriminant + kNN
- [ ] `LogisticFPCClassifier` — binary classification
- [ ] `FunctionalKMeans` — clustering

### Phase 3 — Outlier Detectors + Differentiators

- [ ] `LRTOutlierDetector`, `OutliergramDetector`, `MagnitudeShapeDetector` — classic three
- [ ] `BasisRepresentation`, `LocalPolynomialSmoother` — additional transformers
- [ ] `RobustFPCRegressor` — L1/Huber
- [ ] `TVDMSSDetector`, `MUODDetector`, `DepthgramDetector` — newer outlier methods
- [ ] `GLMRegressor` (gaussian family only), `DDClassifier`, `ElasticMultinomialClassifier`

### Defer / Future

- `PACEFPCATransformer` — needs IrregFdata → dense bridge; complex; do after Phase 1 validates
- `FOSRRegressor` — non-standard output shape; address after core is solid
- `ShiftRegistrationTransformer` — registration compliant with check_estimator on small n: research needed before planning

---

## Competitor Feature Analysis (scikit-fda reference)

| Estimator type | scikit-fda (0.10.x) | fdars sklearn layer (planned) |
|---------------|---------------------|-------------------------------|
| Smoothers | `KernelSmoother`, `BasisSmoother` | `BSplineSmoother`, `LocalPolynomialSmoother` |
| Dimensionality reduction | `FPCA`, `FPLS`, `DiffusionMap` | `FPCATransformer`, `PACEFPCATransformer` (differentiator) |
| Registration | `LeastSquaresShiftRegistration`, `FisherRaoElasticRegistration` | `ShiftRegistrationTransformer` (elastic: deferred) |
| Missing values | `MissingValuesInterpolation` | `Imputer` |
| Classifiers | `KNeighbors`, `NearestCentroid`, `MaximumDepth`, `DDClassifier`, `LogisticRegression`, `QDA` | All of the above + `ElasticMultinomialClassifier` (differentiator) |
| Regressors | `LinearRegression`, `KNeighbors`, `KernelRegression`, `FPCARegression`, `FPLSRegression` | All of the above + `RobustFPCRegressor`, `GLMRegressor` (differentiators) |
| Clusterers | `KMeans`, `FuzzyCMeans` | Both + `FunctionalGMM` |
| Outlier detectors | `BoxplotOutlierDetector`, `MSPlotOutlierDetector` | LRT + outliergram + MS + TVDMSS + MUOD + Depthgram (broader coverage) |
| Depth transforms | Depth methods exposed as functions | `DepthTransformer` (unified transformer over 13 methods) |

---

## Table Stakes vs Differentiators — Summary

### Table Stakes

Missing any of these = the sklearn layer feels incomplete to an FDA practitioner:

1. `BSplineSmoother` / `LocalPolynomialSmoother` — smoothing transformers
2. `FPCATransformer` — functional PCA → scores; enables the entire sklearn pipeline ecosystem
3. `Imputer` — NaN handling upstream of smoothers
4. `FPCRegressor` / `PLSRegressor` — scalar-on-function regression (most common FDA task)
5. `LogisticFPCClassifier` — binary functional classification
6. `FPCLDAClassifier` / `FPCKNNClassifier` — functional discriminant / k-NN classifiers
7. `FunctionalKMeans` — functional clustering (most requested after regression)
8. `LRTOutlierDetector` / `OutliergramDetector` / `MagnitudeShapeDetector` — the "classic three"
9. `DepthTransformer` — depth as feature (depth → scalar for downstream models)

### Differentiators

Go beyond scikit-fda's coverage or use fdars' Rust performance advantage:

1. `BasisRepresentation` — basis projection as sklearn transformer (fdars' Rust speed is the differentiator)
2. `FuzzyFunctionalCMeans` — fuzzy clustering (scikit-fda has it, fdars adds Rust speed)
3. `TVDMSSDetector` / `MUODDetector` / `DepthgramDetector` — newer outlier methods beyond classic three
4. `RobustFPCRegressor` (L1/Huber) — robust regression scikit-fda lacks
5. `GLMRegressor` — functional GLM (binomial/poisson/gamma) — scikit-fda lacks this
6. `PACEFPCATransformer` — PACE FPCA for dense data (scikit-fda doesn't have PACE)
7. `DDClassifier` — depth-based DD-classifier
8. `ElasticMultinomialClassifier` — elastic multinomial OvR
9. `NormTransformer` — functional norm as scalar feature
10. `SplineInterpolator` — grid-resampling transformer

### Anti-Features

| Feature | Why Avoid | What to Do Instead |
|---------|-----------|-------------------|
| Wrapping `cluster_optim` as ClusterMixin | It is itself a grid search loop — nesting inside GridSearchCV creates double-search confusion | Expose FunctionalKMeans; let users use GridSearchCV over n_clusters |
| Exposing inference tests (permutation, SCB, ANOVA) as estimators | Hypothesis tests don't have fit/predict contracts | Keep only in the native fdars API |
| Wrapping `concurrent_regression` as RegressorMixin | Takes a list of predictor matrices — incompatible with sklearn's single-X input contract | Keep in native API only |
| Exempting any estimator from check_estimator | Any exemption propagates into Pipeline/GridSearchCV failures at user sites | Exclude non-compliant methods, document coverage list |
| Accepting Fdata objects as estimator input | Fdata is an OOP container, incompatible with sklearn's column slicing, ColumnTransformer, cross_val_score | Accept only plain (n_obs, n_points) ndarrays; argvals is a constructor param |
| numpy array as default for argvals in __init__ | Mutable default breaks clone() and set_params() | Use argvals=None default, resolve in fit |

---

## Sources

- [Scikit-fda and scikit-learn tutorial (0.10.1)](https://fda.readthedocs.io/en/stable/auto_tutorial/plot_skfda_sklearn.html)
- [scikit-fda API Reference (0.10.2.dev0)](https://fda.readthedocs.io/en/latest/apilist.html)
- [Developing scikit-learn estimators — sklearn 1.9.0](https://scikit-learn.org/stable/developers/develop.html)
- [scikit-fda: A Python Package for Functional Data Analysis (arxiv 2022)](https://arxiv.org/pdf/2211.02566)
- fdars source modules reviewed: `regression_mod.rs`, `classification_mod.rs`, `clustering_mod.rs`, `outliers_mod.rs`, `smoothing_mod.rs`, `basis_mod.rs`, `alignment_mod.rs`, `pace_fpca_mod.rs`, `depth_mod.rs`, `python/fdars/_augment.py`, `python/fdars/fdata_class.py`, `python/fdars/__init__.py`

---
*Feature research for: scikit-learn-compatible estimator layer over fdars (v9.0)*
*Researched: 2026-08-31*
