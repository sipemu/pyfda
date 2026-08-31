---
phase: 57-regressors-classifiers
reviewed: 2026-08-31T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - python/fdars/sklearn/_skeletons.py
  - python/fdars/sklearn/_coverage.py
findings:
  critical: 3
  warning: 4
  info: 0
  total: 7
status: issues_found
---

# Phase 57: Code Review Report

**Reviewed:** 2026-08-31
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

This phase implemented stored-model `predict` for 11 functional regressors and
classifiers that previously returned only training-set predictions. The
transformer, clusterer, and outlier-detector families are unchanged here (their
PASS-WITH-FIXES items carry forward to Phase 58). Review focused on the new
predict logic, subset-invariance, numerical robustness, label-encoder
correctness, and the GLM reconstruction path.

The six standalone classifiers (FPCLDAClassifier through LogisticFPCClassifier)
and NonparametricRegressor are structurally sound and subset-invariant. Three
critical defects are present: an internal model split in GLMRegressor, an
unguarded crash in FPCQDAClassifier/FPCLDAClassifier at their minimum sample
count, and a genuine subset-invariance violation in MagnitudeShapeDetector.

---

## Critical Issues

### CR-01: GLMRegressor stores two inconsistent models — fitted_values_/r_squared_/intercept_/beta_t_ are from functional_glm (IRLS-FPC) while predict() uses a separate OLS-FPC model

**File:** `python/fdars/sklearn/_skeletons.py:1324-1367`

**Issue:** `fit()` calls `functional_glm(...)` (IRLS with functional PCA
internally) and stores its output as `fitted_values_`, `r_squared_`,
`intercept_`, and `beta_t_`. It then makes a **second independent call** to
`fpca(X, argvals_, n_comp)`, sign-canonicalizes those components, and fits a
plain OLS (`np.linalg.lstsq`) on the resulting FPC scores to produce `coef_`.
`predict()` uses **only** `components_`, `mean_`, and `coef_` — the OLS-FPC
model — and has no connection to `functional_glm`.

Consequences:

1. `est.r_squared_` (from IRLS-FPC) != `est.score(X_train, y_train)` (from
   OLS-FPC via `RegressorMixin.score()`). A user comparing the two gets
   contradictory R² values for the same estimator on the same training data.

2. `est.intercept_` (from functional_glm) != `est.coef_[0]` (OLS intercept).
   Both are stored, and their values can differ when IRLS converges to a
   different parameterization than OLS.

3. `est.beta_t_` (the IRLS coefficient function) is not used by `predict()` at
   all; it describes a different model.

4. `functional_glm` and `fpca` are both called on `X` with `n_comp`: this
   duplicates the (expensive) FPCA computation.

The mathematical correctness of `predict()` itself is not in question — OLS on
FPC scores is a valid Gaussian functional regression — but the stored diagnostic
attributes are misleading because they describe a different (IRLS-FPC) model.

**Fix:** Choose one model and store diagnostics from it consistently.

Option A (preferred — keeps the native GLM fit for diagnostics): after calling
`functional_glm`, reuse `fpca` components for `predict` but derive `coef_` by
projecting `beta_t_` onto the same FPC basis, or store `beta_t_` and use it
directly in `predict` (bypassing the separate OLS fit). Remove `r_squared_` /
`intercept_` / `fitted_values_` stored from the IRLS call if they do not match
what `predict` produces. Alternatively…

Option B (minimal): drop the `functional_glm` call entirely (OLS on FPC scores
IS the Gaussian GLM with identity link), derive `fitted_values_` and
`r_squared_` from OLS, remove `beta_t_`. The one `fpca` call is sufficient.

```python
# Option B sketch (replaces lines 1324-1343):
fpca_result = _native.regression.fpca(X, self.argvals_, n_comp)
components = np.array(fpca_result["rotation"]).T       # (n_comp, n_pts)
scores     = np.array(fpca_result["scores"])           # (n_obs, n_comp)
components, scores = self._sign_canonicalize(components, scores)
self.components_ = components
self.mean_        = np.array(fpca_result["mean"])
S                 = np.column_stack([np.ones(n_obs), scores])
self.coef_, _, _, _ = np.linalg.lstsq(S, y, rcond=None)
self.fitted_values_  = S @ self.coef_           # from the same model predict() uses
ss_res               = np.sum((y - self.fitted_values_) ** 2)
ss_tot               = np.sum((y - y.mean()) ** 2)
self.r_squared_      = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
self.intercept_      = float(self.coef_[0])     # now consistent with predict()
self.n_iter_         = 1  # OLS has no iterations; set to 1 for sklearn compliance
```

---

### CR-02: FPCQDAClassifier and FPCLDAClassifier crash with sklearn ValueError at minimum sample count (_min_samples=2, binary labels)

**File:** `python/fdars/sklearn/_skeletons.py:1592-1631` (FPCLDAClassifier), `1672-1711` (FPCQDAClassifier)

**Issue:** Both estimators set `_min_samples = 2`. With exactly 2 training
samples and a binary target (one sample per class, which is the only possible
binary arrangement at n=2), the sklearn sub-estimators fail:

- `LinearDiscriminantAnalysis.fit(scores_2x1, [0, 1])` raises
  `ValueError: The number of samples must be more than the number of classes.`
- `QuadraticDiscriminantAnalysis.fit(scores_2x1, [0, 1])` raises
  `ValueError: y has only 1 sample in class 0, covariance is ill defined.`

These exceptions originate inside the sklearn discriminant analysis objects and
propagate as unguarded crashes from `FPCLDAClassifier.fit()` and
`FPCQDAClassifier.fit()` whenever n_obs equals the stated minimum. The
estimators advertise `_min_samples=2` as safe but will reliably fail at exactly
that bound with binary classification.

The same problem exists for `FPCLDAClassifier` with any n_obs where `n_obs <=
n_classes`: LDA requires `n_obs > n_classes`.

**Verified:** Running `QuadraticDiscriminantAnalysis().fit(np.array([[0.5],
[1.0]]), [0, 1])` raises the cited error in sklearn 1.8.

**Fix:** Raise `_min_samples` or add an explicit pre-fit guard:

```python
# In FPCQDAClassifier.fit(), after label encoding (before _fpc_fit_scores):
n_classes = len(le.classes_)
min_per_class = min(np.bincount(y_enc.astype(int)))
if min_per_class < 2:
    raise ValueError(
        f"FPCQDAClassifier requires at least 2 samples per class for QDA "
        f"covariance estimation; smallest class has {min_per_class} sample(s)."
    )
# For FPCLDAClassifier:
if n_obs <= n_classes:
    raise ValueError(
        f"FPCLDAClassifier requires n_samples > n_classes; "
        f"got n_samples={n_obs}, n_classes={n_classes}."
    )
```

Alternatively, raise `_min_samples` to at least 3 for FPCQDAClassifier (which
also requires the per-class count ≥ 2) and document the dependency on class
distribution explicitly.

---

### CR-03: MagnitudeShapeDetector.score_samples is not subset-invariant — magnitude_shape is called on the test batch without reference to training data

**File:** `python/fdars/sklearn/_skeletons.py:2697-2716`

**Issue:** `score_samples(X)` calls `_native.outliers.magnitude_shape(X)` on
the new observations alone, without passing `X_fit_` as a reference
distribution. `magnitude_shape` computes outlyingness statistics **relative to
the batch statistics of its input**. As a result:

```
score_samples(X[[0, 1, 2]])[0]  !=  score_samples(X[[0]])[0]
```

because the batch statistics (central tendency, spread) used to define
"magnitude" and "shape" differ between the two calls. This violates
`check_methods_subset_invariance`, which is listed as a PASS-WITH-FIXES
failure mode for this estimator.

The stored `threshold_` (computed from training data at fit time) is compared
against outlyingness values computed from test-batch statistics, making the
threshold meaningless for subsets of different sizes.

**Fix:** If the native `magnitude_shape` API accepts a reference distribution,
pass `self.X_fit_` as reference for new observations. If not, compute the
outlyingness of each test observation independently by augmenting it into the
training set one at a time (as `LRTOutlierDetector.score_samples` does), or
compute the threshold from the training-set outlyingness and apply the same
scale transformation to test observations that uses only the training statistics.

---

## Warnings

### WR-01: _BaseFdarsClassifier is dead code with a defective vstack predict

**File:** `python/fdars/sklearn/_skeletons.py:1478-1568`

**Issue:** `_BaseFdarsClassifier` defines `fit()`, `predict()`, and
`_call_native()` but no concrete estimator in this file (or presumably anywhere
else) inherits from it. All six production classifiers inherit directly from
`ClassifierMixin, _BaseFdarsEstimator`. The `predict()` implementation in this
dead class uses `np.vstack([self.X_fit_, X_new])` and slices `predicted_all[-n_new:]`,
which is exactly the pattern replaced by the stored-model approach in Phase 57 because
it violates `check_methods_subset_invariance`. Additionally, the `fit()` method
is missing both `_require_y` and `_reject_continuous_target` guards.

If this class exists as a future base for new estimators, its predict must be
rewritten. As-is it is misleading: a future maintainer who inherits from it will
inherit a broken predict.

**Fix:** Remove `_BaseFdarsClassifier` entirely, or if it is intended as a
template, rewrite `predict()` to use the stored-model pattern and add the
missing guards.

---

### WR-02: FPCKNNClassifier accepts k=0, silently predicting the first class for all inputs

**File:** `python/fdars/sklearn/_skeletons.py:1756-1821`

**Issue:** `k` is capped at `min(self.k, n_obs - 1)` to produce `k_`. When a
user passes `k=0`, `k_=0`. In `predict()`, `np.argsort(d, axis=1)[:, :0]`
returns an empty index array for every test point. `np.bincount([], minlength=n_classes)`
returns all-zeros counts, and `np.argmax` of all-zeros returns 0 — so
`predict()` returns `classes_[0]` for every input with no error or warning.

**Fix:** Validate `k >= 1` at fit time:

```python
# In FPCKNNClassifier.fit(), before the n_obs guard:
if self.k < 1:
    raise ValueError(
        f"FPCKNNClassifier requires k >= 1; got k={self.k}."
    )
```

---

### WR-03: FuzzyFunctionalCMeans and FunctionalGMM lack n_iter_ attribute — known PASS-WITH-FIXES gap not fixed in Phase 57

**File:** `python/fdars/sklearn/_skeletons.py:2276-2312` (FuzzyFunctionalCMeans), `2368-2404` (FunctionalGMM)

**Issue:** `TRIAGE_VERDICTS` records both as `PASS-WITH-FIXES: add n_iter_
attribute to fit()`. Neither estimator sets `self.n_iter_` in `fit()`, so
`check_non_transformer_estimators_n_iter` will fail. This was deferred to Phase
58 but is mechanically a one-liner in each fit. Since Phase 57 touched the same
file and the fix is trivial, the omission increases technical debt.

**Fix:**

```python
# FuzzyFunctionalCMeans.fit() — after self.cluster_centers_ = ...:
self.n_iter_ = 1  # fuzzy_cmeans_fd does not expose iteration count

# FunctionalGMM.fit() — after self.X_fit_ = X:
self.n_iter_ = 1  # gmm_cluster does not expose iteration count
```

---

### WR-04: LogisticFPCClassifier stores n_iter_ = max_iter regardless of actual convergence

**File:** `python/fdars/sklearn/_skeletons.py:2110-2112`

**Issue:** `self.n_iter_ = self.max_iter` is set unconditionally. If the native
`functional_logistic` converges in 5 iterations with `max_iter=25`, the stored
`n_iter_` reports 25. This is explicitly documented as "conservative upper bound"
but means any downstream code inspecting `n_iter_` will think the solver always
runs to the limit, masking early convergence and making convergence diagnostics
unreliable.

The native function does not expose the actual iteration count, so a perfect fix
requires an API change in `fdars-core`. A pragmatic workaround: store `n_iter_`
from a convergence-detection heuristic (e.g. compare `probabilities_` to a
re-call with fewer iterations) or document the limitation prominently.

**Fix (pragmatic):** Accept the current behavior but add a comment making clear
that `n_iter_` is a ceiling, not the actual count, and update the docstring
`Attributes` section:

```python
# n_iter_ is the maximum allowed iterations (actual count not exposed by native).
self.n_iter_ = self.max_iter
```

Document in the class docstring `Attributes` section:
```
n_iter_ : int
    Set to ``max_iter``. The native solver does not expose actual iteration count;
    this is a conservative upper bound. Early convergence is not reflected here.
```

---

_Reviewed: 2026-08-31_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
