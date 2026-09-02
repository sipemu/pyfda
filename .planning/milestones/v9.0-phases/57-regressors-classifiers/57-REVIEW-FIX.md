---
phase: 57-regressors-classifiers
fixed_at: 2026-08-31T00:00:00Z
review_path: .planning/phases/57-regressors-classifiers/57-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 57: Code Review Fix Report

**Fixed at:** 2026-08-31
**Source review:** `.planning/phases/57-regressors-classifiers/57-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (CR-01, CR-02, WR-01, WR-02, WR-04; CR-03 and WR-03 deferred to Phase 58)
- Fixed: 5
- Skipped: 0

**Verification:** All fixes verified in the main checkout (workflow.use_worktrees=false).
Validation suite: 689 passed, 0 failures.

---

## Fixed Issues

### CR-01: GLMRegressor — one consistent OLS-FPC model

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `ba02d4f`
**Applied fix:** Dropped the redundant `functional_glm` call (and the second `fpca` call that it required). Replaced with a single FPCA decomposition: sign-canonicalized components are used for OLS fitting and for `predict()`. `fitted_values_` is now computed via the same `predict()` path, so `r_squared_` (computed from `fitted_values_`) is exactly consistent with `score(X_train, y_train)`. `intercept_` equals `coef_[0]`. `beta_t_` (stored-but-unused IRLS coefficient from the old GLM call) is removed. `n_iter_ = 1` (OLS has no iterations). Updated docstring with an Attributes section.

**Consistency verified:**
```
r_squared_ = 0.11534117
score(X_train, y_train) = 0.11534117   # exact match
intercept_ == coef_[0]: True
```

---

### CR-02: FPCLDAClassifier/FPCQDAClassifier — guard before sklearn sub-estimator crash

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `d2101de`
**Applied fix:**
- `FPCLDAClassifier.fit()`: after LabelEncoder, check `n_obs <= n_classes` and raise `ValueError` with a clear message before fitting `LinearDiscriminantAnalysis`.
- `FPCQDAClassifier.fit()`: after LabelEncoder, compute `min_per_class = np.bincount(y_enc).min()` and raise `ValueError` if `< 2` before fitting `QuadraticDiscriminantAnalysis`.
Both classifiers remain check_estimator-green (331 classifier tests pass).

---

### WR-01: Remove dead _BaseFdarsClassifier class

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `e2acee1`
**Applied fix:** Removed the entire `_BaseFdarsClassifier` class (93 lines). Confirmed via grep that no concrete estimator inherits from it — only a comment in `_coverage.py` references the name, which is unaffected. The vstack+slice predict pattern the class used was explicitly replaced in Phase 57 by stored-model predict; leaving the class would mislead future maintainers.

---

### WR-02: FPCKNNClassifier — reject k < 1

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `43028d0`
**Applied fix:** Added `if self.k < 1: raise ValueError(...)` in `fit()` before the `n_obs` guard. With `k=0`, `k_=0` caused `argsort[:, :0]` to return empty slices, `bincount` to return all-zeros, and `argmax` to silently predict `classes_[0]` for every input. Guard tested manually:
```
FPCKNNClassifier(k=0).fit(X, y)  # → ValueError: FPCKNNClassifier requires k >= 1; got k=0.
```

---

### WR-04: LogisticFPCClassifier — document n_iter_ limitation

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `772699d`
**Applied fix:** Added `Attributes` section to class docstring explicitly documenting that `n_iter_` is set to `max_iter` unconditionally because the native `functional_logistic` solver does not expose actual iteration count (conservative upper bound; early convergence not reflected). No behavior change; inline comment at the assignment site was already accurate. LogisticFPCClassifier remains check_estimator-green (56 tests pass).

---

## Skipped Issues

None — all in-scope findings were fixed.

---

## Out-of-Scope (Phase 58)

The following findings were explicitly excluded per the fix instructions and left untouched:

- **CR-03** (`MagnitudeShapeDetector.score_samples` subset-invariance violation): outlier detector owned by Phase 58.
- **WR-03** (`FuzzyFunctionalCMeans`/`FunctionalGMM` missing `n_iter_`): clusterer estimators owned by Phase 58.

Neither file location nor behavior of those estimators was modified.

---

_Fixed: 2026-08-31_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
