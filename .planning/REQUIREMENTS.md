# Requirements: pyfda — scikit-learn API Compatibility (v9.0)

**Defined:** 2026-08-31
**Core Value:** Functional-data methods in `fdars` plug natively into scikit-learn's `Pipeline`/`GridSearchCV`/`cross_val_score`, interoperate with native sklearn estimators, and offer familiar `fit`/`transform`/`predict` ergonomics — with every wrapped estimator passing the full `check_estimator` battery, no exemptions.

## v9.0 Requirements

### Foundation & Packaging

- [x] **FND-01**: `scikit-learn` is an optional extra (`[sklearn]`, pinned `>=1.3,<1.7`); the base package imports with zero sklearn installed, and importing `fdars.sklearn` without it raises an actionable `ImportError` (mirrors the `advisor`/`mcp` extras pattern).
- [x] **FND-02**: A new `python/fdars/sklearn/` subpackage is gated exactly like `advisor`/`mcp` (deferred import in its own `__init__.py`); `python/fdars/__init__.py` is not modified.
- [x] **FND-03**: A shared `_BaseFdarsEstimator(BaseEstimator)` enforces the sklearn contract: `argvals` (and all constructor args) stored verbatim in `__init__`, resolved to `self.argvals_` (defaulting to `np.arange(n_features)`) in `fit`, `n_features_in_` set via `validate_data`, float32→float64 casting before native calls, and a tags-API compat shim spanning sklearn 1.3–1.6.
- [x] **FND-04**: Estimators call `fdars._native.*` directly with validated numpy arrays — they never construct an `Fdata` internally (avoids dtype side-effects that break check_estimator).

### Compliance Triage & Coverage

- [x] **TRIAGE-01**: Every candidate estimator (~30 across the five families) is skeletoned and run through `check_estimator`/`parametrize_with_checks`, producing a definitive PASS / PASS-WITH-FIXES / EXCLUDE verdict per estimator before full implementation.
- [x] **TRIAGE-02**: A reason-coded `_coverage.py` `EXCLUDED_METHODS` registry records every fdars method excluded from the sklearn layer (with the failing check / structural reason); excluded methods remain available through the existing functional API.
- [x] **TRIAGE-03**: A go/no-go gate confirms a viable core passes before proceeding (≈1 FPCA, 2 smoothers, 2 regressors, 2 classifiers, 1 clusterer, 2 outlier detectors).

### Transformers

- [x] **XFORM-01**: `FPCATransformer` (`TransformerMixin`) maps `(n_obs, n_points)` → `(n_obs, n_components)` scores with SVD sign canonicalization (idempotent fit); passes full `check_estimator`.
- [x] **XFORM-02**: Smoothing transformers (B-spline and local-polynomial) wrapped as `TransformerMixin` estimators.
- [x] **XFORM-03**: Imputation and spline-interpolation transformers wrapped as `TransformerMixin` estimators.
- [ ] **XFORM-04**: Basis-representation transformer wrapped as a `TransformerMixin` estimator.
- [x] **XFORM-05**: Depth transformer wrapped as a `TransformerMixin` estimator.
- [ ] **XFORM-06**: A `Pipeline([smoother, fpca])` end-to-end test passes (grid-changing chain works).

### Regressors & Classifiers

- [ ] **REG-01**: FPC-based functional regression and PLS regression wrapped as `RegressorMixin` estimators with a `score()` method.
- [ ] **REG-02**: Differentiator regressors that pass triage (robust FPC regression, Gaussian-only GLM, nonparametric regression) wrapped as `RegressorMixin` estimators.
- [ ] **CLF-01**: FPC-based classifiers (logistic, LDA, QDA, KNN) wrapped as `ClassifierMixin` estimators, each using `LabelEncoder` in `fit` and storing `X_fit_`/`y_fit_` where the underlying method re-fits at predict time.
- [ ] **CLF-02**: Differentiator classifiers that pass triage (DD-classifier, elastic-multinomial) wrapped as `ClassifierMixin` estimators.
- [ ] **PRED-01**: A `Pipeline([imputer, smoother, fpca, classifier])` + `GridSearchCV` end-to-end test passes.

### Clusterers & Outlier Detectors

- [ ] **CLUS-01**: `FunctionalKMeans` wrapped as a `ClusterMixin` estimator, deterministic under a fixed `random_state`.
- [ ] **CLUS-02**: Differentiator clusterers that pass triage (fuzzy c-means, functional GMM) wrapped as `ClusterMixin` estimators.
- [ ] **OUT-01**: The classic outlier trio (LRT, outliergram, magnitude-shape) wrapped as `OutlierMixin` estimators with a continuous `decision_function` and `predict`.
- [ ] **OUT-02**: Newer outlier detectors (tvdmss, muod, depthgram) that pass triage wrapped as `OutlierMixin` estimators, synthesizing a continuous `decision_function` from the underlying method.

### Compliance Gate & Interop

- [ ] **COMPLY-01**: Every wrapped estimator passes the full `check_estimator` battery with zero exemptions, run as a `parametrize_with_checks` CI job across the Python 3.9–3.14 matrix (sklearn 1.3–1.6 API paths both exercised).
- [ ] **COMPLY-02**: Interop is proven — an fdars transformer feeds a native sklearn estimator (e.g. `FPCATransformer` scores → `RandomForestClassifier`) inside one `Pipeline`.

### Documentation

- [ ] **DOCS-01**: A new "scikit-learn API" docs section is wired into MkDocs nav: a concept/overview page + per-family reference pages, plus the published coverage/EXCLUDE list.
- [ ] **DOCS-02**: Offline `FDARS_FENCE_OK` worked examples (including a `Pipeline` example and a `GridSearchCV` example); whole-site `mkdocs build --strict` green offline.
- [ ] **DOCS-03**: Method-accurate hand-authored inline SVG diagram(s) (layer architecture / data flow) meeting the v7.0 STYLE_SPEC + SVGO-idempotence bar; blocking human diagram review before close.

### Release

- [ ] **REL-01**: Package version bumped at close (0.8.0 → 0.9.0); `[sklearn]` extra documented in packaging.

## Future Requirements

Deferred to a future release. Tracked but not in this roadmap.

### sklearn layer extensions

- **FUT-01**: `set_output(transform="pandas")` / DataFrame output API support.
- **FUT-02**: Re-evaluate EXCLUDED methods for compliance if fdars-core exposes stored-model / template-free variants (e.g. a fitted-model handle for GLM, a templated registration transformer).
- **FUT-03**: sklearn 1.7+ support once Python 3.9 is dropped (drops the `<1.7` cap; single tags-API path).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Wrapping non-estimator-shaped aspects (inference tests, SPM monitoring, the advisor) as fit/predict estimators | No `fit`/`predict` contract; forcing them distorts both the API and check_estimator |
| Any `check_estimator` exemption / `expected_failed_checks` allowance | Milestone bar is full compliance, no exemptions; non-compliant methods are EXCLUDED, not exempted |
| scikit-fda as a dependency | Its `FDataGrid` input contract conflicts with the plain-ndarray requirement; reference only |
| `fdars-core` bump | This milestone is a pure-Python layer over the current 0.23.0 bindings |
| Advisor / MCP changes | Orthogonal surface; untouched this milestone |
| Fdata-typed input to sklearn estimators | Estimators take plain `(n_obs, n_points)` ndarrays; Fdata input can't traverse check_estimator |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 55 | Complete |
| FND-02 | Phase 55 | Complete |
| FND-03 | Phase 55 | Complete |
| FND-04 | Phase 55 | Complete |
| TRIAGE-01 | Phase 55 | Complete |
| TRIAGE-02 | Phase 55 | Complete |
| TRIAGE-03 | Phase 55 | Complete |
| XFORM-01 | Phase 56 | Complete |
| XFORM-02 | Phase 56 | Complete |
| XFORM-03 | Phase 56 | Complete |
| XFORM-04 | Phase 56 | Pending |
| XFORM-05 | Phase 56 | Complete |
| XFORM-06 | Phase 56 | Pending |
| REG-01 | Phase 57 | Pending |
| REG-02 | Phase 57 | Pending |
| CLF-01 | Phase 57 | Pending |
| CLF-02 | Phase 57 | Pending |
| PRED-01 | Phase 57 | Pending |
| CLUS-01 | Phase 58 | Pending |
| CLUS-02 | Phase 58 | Pending |
| OUT-01 | Phase 58 | Pending |
| OUT-02 | Phase 58 | Pending |
| COMPLY-01 | Phase 58 | Pending |
| COMPLY-02 | Phase 58 | Pending |
| DOCS-01 | Phase 59 | Pending |
| DOCS-02 | Phase 59 | Pending |
| DOCS-03 | Phase 59 | Pending |
| REL-01 | Phase 59 | Pending |

**Coverage:**

- v9.0 requirements: 24 total
- Mapped to phases: 24 ✓
- Unmapped: 0

**Per-phase distribution:**

- Phase 55 (Compliance-Triage & Foundation): FND-01..04, TRIAGE-01..03 (7)
- Phase 56 (Transformers): XFORM-01..06 (6)
- Phase 57 (Regressors & Classifiers): REG-01/02, CLF-01/02, PRED-01 (5)
- Phase 58 (Clusterers & Outlier Detectors + Compliance Gate): CLUS-01/02, OUT-01/02, COMPLY-01/02 (6)
- Phase 59 (Documentation & Docs Gate): DOCS-01..03, REL-01 (4)

---
*Requirements defined: 2026-08-31*
*Last updated: 2026-08-31 — roadmap created; all 24 requirements mapped across Phases 55–59*
