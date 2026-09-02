# Phase 57: Regressors & Classifiers - Context

**Gathered:** 2026-08-31
**Status:** Ready for planning
**Mode:** Auto-generated (smart-discuss) — determined-implementation phase; the ONE open question (native predictor API supports fit-once/predict-many?) is resolved by a targeted research spike before planning.

<domain>
## Phase Boundary

Ship the regressor and classifier families as fully `check_estimator`-compliant `RegressorMixin` / `ClassifierMixin` estimators, reusing the Phase-55/56 base-class + FPCATransformer patterns, and prove a full predictive `Pipeline` under `GridSearchCV`. Delivers REG-01, REG-02, CLF-01, CLF-02, PRED-01.

The Phase-55 triage marked all 11 predictors PASS-WITH-FIXES. The dominant fix is **stored-model predict**: fit once, store the model (FPC basis + coefficients, or training data), and predict WITHOUT re-fitting — this is what makes `check_regressors_train` (R²>0.5) and `check_methods_subset_invariance` (predict(X[mask]) == predict(X)[mask]) pass. The Phase-55 skeletons used a `vstack(X_fit, X_new)`-then-slice anti-pattern that contaminated train with test and broke subset-invariance; Phase 57 replaces it with a genuine stored-model predict.

Out of scope: clusterers/outliers + full-matrix compliance gate (Phase 58), docs (Phase 59), fdars-core bump, advisor changes, `python/fdars/__init__.py` edits. Non-Gaussian GLM / list-of-matrices / IrregFdata-input methods that triage EXCLUDED stay in `_coverage.py`.
</domain>

<decisions>
## Implementation Decisions

### Predictor roster & per-estimator fixes (from `_coverage.py` verdicts)
Regressors (`RegressorMixin`, must expose working `score()`):
- **FPCRegressor / RobustFPCRegressor / GLMRegressor (Gaussian only)** — fit once + store model/coeffs; predict without re-fit (fixes check_regressors_train + subset_invariance).
- **NonparametricRegressor** — store training data; predict without re-fit contaminating.
- **PLSRegressor** — add `y=None` guard with sklearn-convention message (mostly already PASS).

Classifiers (`ClassifierMixin`, `LabelEncoder` in fit, store `X_fit_`/`y_fit_` where native re-fits):
- **FPCLDA / FPCQDA / DDClassifier** — stored-model predict (no vstack re-fit).
- **FPCKNNClassifier** — add label-type validation (check_type_of_target) + `y=None` guard.
- **LogisticFPCClassifier** — LabelEncoder to native {0,1} domain + ensure fit returns self (root cause of the 20-check cascade); document multiclass limitation if native is binary-only.
- **ElasticMultinomialClassifier** — add `check_is_fitted` before predict + 1-feature/argvals≥2 guard (sklearn-convention message) + stored-model predict.

### THE key strategy question (resolved by the Phase-57 research spike)
How to achieve fit-once/predict-many with the native combined fit+predict functions (`fregre_lm`, `fclassif_lda/qda/knn`, etc.):
- **If the native signature takes separate (train_X, train_y, test_X):** pass the STORED train + the incoming test → each test point predicted independently of other test points → subset-invariant. This is the preferred fix.
- **If native is transductive-only (fits on the union each call):** reconstruct predict in the Python wrapper from a stored representation — e.g. store FPC scores/eigenfunctions + fitted linear/discriminant coefficients and implement `predict` in numpy from those. Research must confirm which fdars functions expose enough to do this.
The research spike reads the EXISTING skeletons (which already call these natives) + native signatures and prescribes the exact per-method stored-model-predict recipe.

### Contract (unchanged, re-assert)
- Subclass `_BaseFdarsEstimator`; store constructor args verbatim; resolve `argvals_` in fit; `n_features_in_` via `validate_data(dtype="numeric")` then `.astype(np.float64)`; call `fdars._native.*` directly; NEVER construct `Fdata`.
- After promoting each predictor to full PASS, flip its `_coverage.py` verdict to PASS.
- Compliance test: fast per-estimator `parametrize_with_checks` (not the 28-estimator battery).
- PRED-01: `Pipeline([imputer, smoother, fpca, classifier])` inside `GridSearchCV` fits + predicts.

### Claude's Discretion
Module organization, exact stored representation per method, and test layout are at Claude's discretion, guided by the research spike, `55-RESEARCH.md`, and sklearn conventions.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/sklearn/_base.py` — `_BaseFdarsEstimator`, tags/validate shim, float cast.
- `python/fdars/sklearn/_skeletons.py` — existing regressor/classifier skeletons (they already call the native predictor funcs — read them to learn the current native usage + the vstack anti-pattern to replace); module-level `_pairwise_l2`.
- FPCATransformer (Phase 56, full PASS) — the FPC-scores hub the FPC-based predictors build on; reuse its FPCA extraction / sign-canonicalization approach for stored FPC representations.
- `python/fdars/sklearn/_coverage.py` — TRIAGE_VERDICTS (flip predictors to PASS), EXCLUDED_METHODS.
- `tests/sklearn/` — compliance harness pattern from Phase 56.

### Established Patterns
- `LabelEncoder` in classifier fit for arbitrary check_estimator labels; store `classes_`.
- Native compute via `fdars._native.*`; sklearn 1.8 dev env; shim spans 1.3→1.8.

### Integration Points
- `python/fdars/sklearn/` (predictors + tests). No `__init__.py`/Rust/advisor/mcp changes.
</code_context>

<specifics>
## Specific Ideas
- Per-predictor fixes are the exact strings in `_coverage.py` `TRIAGE_VERDICTS`.
- Hard constraints: FULL check_estimator, no exemptions; plain `(n_obs, n_points)` ndarray + `argvals` constructor param; no fdars-core bump.
- `test_triage.py` currently red for these predictors (expected) — turns green as they promote; reconcile the whole-suite gate at Phase 58.
</specifics>

<deferred>
## Deferred Ideas
- Clusterers/outliers + full-matrix compliance gate (Phase 58); docs (Phase 59).
- Multiclass logistic if native is binary-only (document as limitation, not a blocker).
- `set_output(transform="pandas")` (FUT-01).
</deferred>
