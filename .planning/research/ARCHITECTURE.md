# Architecture Research

**Domain:** sklearn-compatible estimator layer over fdars (functional-data PyO3 bindings)
**Researched:** 2026-08-31
**Confidence:** HIGH (architecture derived from reading actual source files; sklearn contracts verified against upstream docs)

## Standard Architecture

### System Overview — With the New sklearn Layer

The new `fdars.sklearn` layer sits entirely inside the Python API layer, parallel to `fdars.advisor` and `fdars.mcp`. It does not touch the Rust FFI layer.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Python API Layer                              │
│                       python/fdars/                                   │
│                                                                       │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │  Fdata OOP   │ │  _augment  │ │    advisor/  │ │   sklearn/   │  │
│  │ fdata_class  │ │  helpers   │ │  (optional)  │ │  (optional)  │  │
│  └──────┬───────┘ └─────┬──────┘ └──────┬───────┘ └──────┬───────┘  │
│         │               │               │                │           │
│         └───────────────┴───────────────┴────────────────┘           │
│                                    │                                  │
│           ALL paths call the same native functions:                   │
│           fdars._native.{smoothing,basis,regression,...}             │
└──────────────────────────────────────────────────────────────────────┤
                                     │ PyO3
                                     ▼
┌────────────────────────────────────────────────────────────────────┐
│              Rust FFI Layer  (src/*_mod.rs)  — UNCHANGED           │
│              fdars-core  (external crate) — NO BUMP                │
└────────────────────────────────────────────────────────────────────┘
```

### Subpackage Location and File Layout

```
python/fdars/
├── __init__.py                  # does NOT import fdars.sklearn (stays sklearn-free)
├── fdata_class.py               # Fdata container — UNCHANGED
├── advisor/                     # [advisor] optional extra — existing pattern
├── mcp/                         # [mcp] optional extra — existing pattern
└── sklearn/                     # [sklearn] optional extra — NEW, mirrors advisor/mcp
    ├── __init__.py              # gating: ImportError if scikit-learn not installed
    ├── _base.py                 # _BaseFdarsEstimator shared base class
    ├── transformers.py          # FdarsSmoother, FdarsBasisTransformer, FdarsFPCA,
    │                            #   FdarsImputer, FdarsDepthTransformer
    ├── predictors.py            # FdarsFunctionalRegressor, FdarsClassifier,
    │                            #   FdarsClustering, FdarsOutlierDetector
    └── _coverage.py             # EXCLUDED_METHODS registry (declarative documentation)
```

### Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `sklearn/__init__.py` | Import gate: raises `ImportError` when scikit-learn not installed; exports all public estimator classes | `sklearn/__init__.py` |
| `_BaseFdarsEstimator` | Shared base: stores `argvals` as constructor param; provides `_resolve_argvals()` helper; `_fit_validate()` / `_transform_validate()` call sklearn validation functions | `sklearn/_base.py` |
| Transformers | `TransformerMixin + _BaseFdarsEstimator` subclasses for smoothing, basis, FPCA, imputation, depth scoring | `sklearn/transformers.py` |
| Predictors | `RegressorMixin / ClassifierMixin / ClusterMixin / OutlierMixin + _BaseFdarsEstimator` subclasses | `sklearn/predictors.py` |
| `_coverage.py` | Declarative registry of excluded fdars methods with reason codes | `sklearn/_coverage.py` |

## Recommended Project Structure — Rationale

- **`sklearn/` as subpackage, not a top-level module:** Mirrors `advisor/` and `mcp/`; users do `from fdars.sklearn import FdarsFPCA`; the subpackage is an island with its own `__init__.py` that handles the sklearn import gate.
- **`_base.py` separate from mixins:** `_BaseFdarsEstimator` is depended on by both `transformers.py` and `predictors.py`; separating it avoids circular imports and makes the dependency graph strictly one-directional (`predictors` → `_base`; `transformers` → `_base`; `_base` → nothing in sklearn/).
- **`_coverage.py` as a declarative registry:** The excluded-methods list is a milestone deliverable per PROJECT.md. A separate file makes it easy to maintain without cluttering estimator code.

## Gating and Registration — Mirroring `advisor`/`mcp`

### 1. `pyproject.toml` optional extra

Add one entry:
```toml
sklearn = ["scikit-learn>=1.3"]
```

`scikit-learn` must NOT appear in `[project.dependencies]` (base package stays sklearn-free). Floor at 1.3 because `validate_data` (the standalone function form replacing `check_array` in fit/transform) was introduced there. Note: `__sklearn_tags__()` as a dataclass arrived in 1.6; the base class should detect which tags API is available and use `_get_tags()` as a fallback for 1.3–1.5.

### 2. `sklearn/__init__.py` import gate

```python
# python/fdars/sklearn/__init__.py

# --- import gate (mirrors fdars/mcp/__init__.py) ---
try:
    from sklearn.base import BaseEstimator  # noqa: F401 — proves sklearn present
except ImportError as _e:
    raise ImportError(
        "fdars[sklearn] requires scikit-learn. "
        "Install it with: pip install fdars[sklearn]"
    ) from _e

from fdars.sklearn._base import _BaseFdarsEstimator            # noqa: E402
from fdars.sklearn.transformers import (                        # noqa: E402
    FdarsSmoother, FdarsBasisTransformer, FdarsFPCA,
    FdarsImputer, FdarsDepthTransformer,
)
from fdars.sklearn.predictors import (                          # noqa: E402
    FdarsFunctionalRegressor, FdarsClassifier,
    FdarsClustering, FdarsOutlierDetector,
)

__all__ = [
    "_BaseFdarsEstimator",
    "FdarsSmoother", "FdarsBasisTransformer", "FdarsFPCA",
    "FdarsImputer", "FdarsDepthTransformer",
    "FdarsFunctionalRegressor", "FdarsClassifier",
    "FdarsClustering", "FdarsOutlierDetector",
]
```

### 3. `fdars/__init__.py` — NOT modified

`fdars.sklearn` is NOT added to `_submodule_names` and is NOT imported in `fdars/__init__.py`. This is identical to how `fdars.mcp` works — its own docstring reads: "not registered in `fdars.__init__` and is never imported by a plain `import fdars`." Users who want the sklearn layer do `from fdars.sklearn import FdarsFPCA` explicitly. `import fdars` never touches scikit-learn.

## Shared Base Class Design — `_BaseFdarsEstimator`

### The Constructor Rule (Hard Constraint from sklearn)

`BaseEstimator.get_params()` introspects `__init__`'s signature via `inspect.signature` and maps each parameter name to the identically-named instance attribute. `clone()` then calls `type(est)(**est.get_params())` to produce an unfitted copy.

This means: **every constructor param must be stored verbatim on `self` with the same name**.

```python
class _BaseFdarsEstimator(BaseEstimator):
    def __init__(self, argvals=None):
        # MUST store exactly as passed:
        #   - no conversion (np.asarray breaks None round-trip)
        #   - no copy
        #   - no None-to-arange substitution here
        self.argvals = argvals
```

If `self.argvals = np.asarray(argvals)` were done in `__init__`, then `clone()` would pass a numpy array back into `__init__`, and `check_estimator` would catch the mutation in its parameter round-trip tests.

Subclasses add their own params but must call `super().__init__(argvals=argvals)` and store everything with the same name:

```python
class FdarsSmoother(TransformerMixin, _BaseFdarsEstimator):
    def __init__(self, argvals=None, bandwidth=None, kernel="gaussian"):
        super().__init__(argvals=argvals)
        self.bandwidth = bandwidth   # stored as-is, no mutation
        self.kernel = kernel         # stored as-is
```

### `n_features_in_` and Validation at Fit Time

The fit method follows the sklearn contract exactly:

```python
def fit(self, X, y=None):
    from sklearn.utils.validation import validate_data
    # validate_data with reset=True:
    #   - converts X to float64 ndarray (or validated dtype)
    #   - sets self.n_features_in_ = X.shape[1]
    #   - sets self.feature_names_in_ if X is a DataFrame
    X = validate_data(self, X, dtype=np.float64, ensure_2d=True, reset=True)
    # resolve argvals AFTER validation, using fit-time data shape
    argvals_ = self._resolve_argvals(X.shape[1])
    # ... functional computation using argvals_ and X ...
    # store all fit-time state with trailing underscores:
    self.argvals_ = argvals_      # resolved grid — fit artifact, not cloned
    self.mean_ = ...              # any other fit-time state
    return self                   # always return self
```

Key distinction: `self.argvals` (no trailing underscore) is the constructor param, untouched through the entire object lifetime. `self.argvals_` (trailing underscore) is the resolved grid created at fit time. `clone()` copies `self.argvals` and discards `self.argvals_`.

### `_resolve_argvals` Helper

```python
def _resolve_argvals(self, n_features: int) -> np.ndarray:
    """Resolve argvals constructor param to a concrete grid at fit time."""
    if self.argvals is None:
        return np.arange(n_features, dtype=np.float64)
    return np.asarray(self.argvals, dtype=np.float64)
```

Called only inside `fit()`, never in `__init__`. This keeps the constructor param pure and the resolution lazy (the correct sklearn pattern).

### Validation in Transform/Predict

```python
def transform(self, X):
    from sklearn.utils.validation import check_is_fitted, validate_data
    check_is_fitted(self)          # checks for any trailing-underscore attr
    # reset=False enforces X.shape[1] == self.n_features_in_
    X = validate_data(self, X, dtype=np.float64, ensure_2d=True, reset=False)
    # ... call fdars native functions with X and self.argvals_ ...
    return result
```

### Tags Override for Special Contracts

For stochastic or otherwise non-standard estimators:

```python
def __sklearn_tags__(self):
    tags = super().__sklearn_tags__()
    tags.non_deterministic = True   # for k-means-based estimators with random init
    return tags
```

For sklearn 1.3–1.5 compatibility, `_base.py` detects the available API:
```python
_HAS_SKLEARN_TAGS_DATACLASS = hasattr(BaseEstimator, "__sklearn_tags__")
```

## numpy↔Fdata Boundary Decision

**Decision: call array-level native functions directly; do NOT construct `Fdata` inside estimator methods.**

Rationale:

1. `check_estimator` passes plain ndarrays. The native functions (`_native.smoothing.nadaraya_watson`, `_native.regression.fpca`, etc.) already accept raw numpy arrays — the same entry points that `Fdata` methods call internally. There is no functional need to wrap in `Fdata`.

2. The existing architecture is: `numpy → PyO3 binding → numpy`. The sklearn layer reuses this exact path, bypassing the Fdata OOP wrapper layer. Constructing `Fdata` would add allocation overhead (IDs, metadata, rangeval) for no benefit.

3. `Fdata` always casts to `float64` and constructs auxiliary data (default IDs, default rangeval). These side effects would interfere with `check_estimator` dtype-casting tests that verify estimators handle e.g. `float32` input by converting to their working dtype internally.

Concrete boundary (correct vs wrong):

```python
# CORRECT — call native directly with validated raw array and resolved grid
smoothed = _native.smoothing.nadaraya_watson(X, self.argvals_, bandwidth=self.bandwidth_)

# WRONG — Fdata construction inside transform breaks check_estimator dtype tests
fd = Fdata(X, argvals=self.argvals_)
smoothed = fd.something()
```

The `Fdata` class remains the recommended user-facing API for interactive workflows. Sklearn estimators use the low-level native bindings.

## clone/get_params/set_params Rules

Four hard rules, all derived from `BaseEstimator`:

### Rule 1: Constructor params stored with exact same attribute name

```python
class FdarsFPCA(TransformerMixin, _BaseFdarsEstimator):
    def __init__(self, argvals=None, n_components=3):
        super().__init__(argvals=argvals)
        self.n_components = n_components  # attribute name == param name — CORRECT

# WRONG: misnamed attribute breaks get_params() introspection
    def __init__(self, argvals=None, n_components=3):
        self.n_comp = n_components  # different name — breaks clone()
```

### Rule 2: No param mutation in `__init__`

```python
# WRONG — mutation in __init__ breaks clone() round-trip
def __init__(self, argvals=None, n_components=3):
    self.argvals = np.asarray(argvals) if argvals is not None else None
    self.n_components = max(1, n_components)  # mutation — clone passes mutated value back

# CORRECT — store verbatim; derive in fit()
def __init__(self, argvals=None, n_components=3):
    self.argvals = argvals
    self.n_components = n_components
```

### Rule 3: Mutable args copied before use in fit, not in __init__

```python
def fit(self, X, y=None):
    X = validate_data(self, X, dtype=np.float64, reset=True)
    # argvals may be a user-supplied list or ndarray — resolve/copy at fit time only
    argvals_ = self._resolve_argvals(X.shape[1])
    self.argvals_ = argvals_      # trailing underscore — fit artifact
    # NEVER modify self.argvals here
    return self
```

### Rule 4: set_params must work — no __init__-cached derived values

`GridSearchCV` calls `set_params(n_components=k)` between fits without calling `__init__`. If `__init__` had cached a derived value (e.g. `self._adjusted_n = n_components + 1`), `set_params` would not update it. All derived values must be computed inside `fit()`, stored with trailing underscores.

## Data Flow Through fit/transform/predict

### Transformer: FdarsSmoother (concrete example)

```
User: smoother = FdarsSmoother(argvals=t, bandwidth=0.1)
      # t stored as self.argvals=t, bandwidth stored as self.bandwidth=0.1
      # no computation here

User: X_smooth = smoother.fit_transform(X)  # X: (n_obs, n_points)
  │
  fit(X):
  ├─ validate_data(self, X, dtype=float64, reset=True) → X validated; n_features_in_=n_points set
  ├─ argvals_ = _resolve_argvals(n_points) → t (user's grid)
  ├─ bandwidth_ = t if self.bandwidth is None else self.bandwidth  (fit-time resolution)
  ├─ _native.smoothing.nadaraya_watson(X, argvals_, bandwidth_)  ← numpy→Rust→numpy
  └─ self.argvals_ = argvals_; self.bandwidth_ = bandwidth_; return self
  │
  transform(X):
  ├─ check_is_fitted(self)
  ├─ validate_data(self, X, reset=False) → shape check vs n_features_in_
  └─ return _native.smoothing.nadaraya_watson(X, self.argvals_, self.bandwidth_)
```

### Predictor: FdarsFunctionalRegressor (FPCA + scalar linear model)

```
User: reg = FdarsFunctionalRegressor(argvals=t, n_components=5)
User: reg.fit(X, y)        # X: (n, p) curves, y: (n,) scalar targets
  │
  ├─ X, y = validate_data(self, X, y, dtype=float64, reset=True)
  ├─ argvals_ = _resolve_argvals(p)
  ├─ fpca_result = _native.regression.fpca(X, argvals_, n_comp=self.n_components)
  │    # numpy→Rust→numpy; returns dict with "scores" (n, n_comp), "rotation" (p, n_comp)
  ├─ # fit linear model on scores:
  │    from numpy.linalg import lstsq
  │    self.coef_, *_ = lstsq(fpca_result["scores"], y, rcond=None)
  └─ self.fpca_result_ = fpca_result; self.argvals_ = argvals_; return self

User: y_pred = reg.predict(X_new)
  ├─ check_is_fitted(self); validate_data(self, X_new, reset=False)
  ├─ scores_new = (X_new - self.fpca_result_["mean"]) @ self.fpca_result_["rotation"]
  └─ return scores_new @ self.coef_
```

### Classifier: FdarsClassifier (functional kNN)

```
User: clf = FdarsClassifier(argvals=t, method="knn", k=5)
User: clf.fit(X, y)
  │
  ├─ X, y = validate_data(self, X, y, dtype=float64, reset=True)
  ├─ self.classes_ = np.unique(y)        ← required by ClassifierMixin.score()
  ├─ argvals_ = _resolve_argvals(p)
  └─ self.X_train_ = X.copy(); self.y_train_ = y.copy(); self.argvals_ = argvals_

User: y_pred = clf.predict(X_new)
  ├─ check_is_fitted(self); validate_data(self, X_new, reset=False)
  ├─ labels = _native.classification.knn_classify_1d(
  │      X_new, self.X_train_, self.argvals_, k=self.k)
  └─ return self.classes_[labels]
```

### Clusterer: FdarsClustering (functional k-means)

```
User: clust = FdarsClustering(argvals=t, k=4, seed=42)
User: clust.fit(X)       ← y accepted but ignored (ClusterMixin requirement)
  │
  ├─ X, _ = validate_data(self, X, None, dtype=float64, reset=True)
  ├─ argvals_ = _resolve_argvals(p)
  ├─ result = _native.clustering.kmeans_fd(X, argvals_, k=self.k, seed=self.seed)
  └─ self.labels_ = np.asarray(result["labels"])    ← required by ClusterMixin
     self.argvals_ = argvals_; return self

User: clust.fit_predict(X)  → calls fit, returns self.labels_
```

## Build Order (Dependency Graph)

Build in strict dependency order — each phase's tests must be green before the next begins:

```
Phase A — Packaging + Shared Base
│  pyproject.toml: add [sklearn] optional extra
│  python/fdars/sklearn/__init__.py  (import gate)
│  python/fdars/sklearn/_base.py     (_BaseFdarsEstimator)
│  python/fdars/sklearn/_coverage.py (excluded methods registry, populated as B/C build)
│  tests/test_sklearn_base.py        (check_estimator on a minimal toy estimator)
│
Phase B — Transformers  (depends on A; depends on native smoothing/basis/regression)
│  python/fdars/sklearn/transformers.py
│  tests/test_sklearn_transformers.py
│  check_estimator run per transformer: FdarsSmoother, FdarsBasisTransformer,
│    FdarsFPCA, FdarsImputer, FdarsDepthTransformer
│
Phase C — Predictors  (depends on A; depends on native regression/classification/clustering)
│  python/fdars/sklearn/predictors.py
│  tests/test_sklearn_predictors.py
│  check_estimator run per predictor: FdarsFunctionalRegressor, FdarsClassifier,
│    FdarsClustering, FdarsOutlierDetector
│
Phase D — Docs  (depends on B and C being check_estimator green)
   docs/sklearn/index.md            (concept + layer overview)
   docs/sklearn/transformers.md     (per-transformer reference)
   docs/sklearn/predictors.md       (per-predictor reference)
   docs/sklearn/pipeline-example.md (Pipeline + GridSearchCV worked example)
   SVG diagrams for the sklearn layer
   mkdocs.yml: add "scikit-learn API" nav section
```

`__init__.py` and `pyproject.toml` changes belong to Phase A (no functional dependencies; do them first so `from fdars.sklearn import ...` works throughout B and C).

## Architectural Patterns

### Pattern 1: Lazy sklearn Import Inside Each Module

Each file in `fdars/sklearn/` imports sklearn at module level — safe because the `__init__.py` gate already proved sklearn is present before any submodule is loaded. `fdars/__init__.py` never imports sklearn.

```python
# python/fdars/sklearn/transformers.py — safe at module level
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import validate_data, check_is_fitted
import numpy as np
from fdars import _native   # same import path as fdata_class.py uses
```

### Pattern 2: argvals Resolution at Fit Time, Not Construction

`_resolve_argvals(n_features)` converts `None → np.arange` and any array-like `→ np.asarray` inside `fit()` only, storing the result as `self.argvals_`.

This is the mandatory pattern for `clone()` correctness. Users who want `argvals` validated at object construction time will not get it — this is the right trade-off because sklearn's design enforces verbatim constructor param storage.

### Pattern 3: Direct Native Calls (Skip Fdata Wrapper)

Estimators import `from fdars import _native` and call `_native.smoothing.nadaraya_watson`, `_native.regression.fpca`, etc. directly with numpy arrays — the same entry points that `Fdata` methods call internally.

This is the correct approach. The `Fdata` wrapper layer adds nothing here and introduces shape/dtype side effects that conflict with `check_estimator`.

### Pattern 4: Exclude Rather Than Exempt

Any fdars method that cannot pass the full `check_estimator` battery is recorded in `_coverage.py` as `EXCLUDED` with a reason code. It remains accessible via the existing functional API but is not wrapped as an sklearn estimator.

```python
# python/fdars/sklearn/_coverage.py
EXCLUDED = {
    "inference.t_perm_test":      "returns TestResult dict, not per-sample prediction",
    "inference.f_perm_test":      "same as above",
    "inference.mean_scb":         "returns confidence band, not estimator-shaped output",
    "inference.oneway_anova":     "group-level test, not per-sample",
    "spm.*":                      "stateful Phase I/II monitoring, not fit/predict-shaped",
    "alignment.karcher_mean":     "group-level operation, output shape changes with n_obs",
    # ...
}
```

## Anti-Patterns

### Anti-Pattern 1: Constructing Fdata Inside Estimator Methods

**What people do:** `fd = Fdata(X, argvals=self.argvals_); return fd.smooth_result()`

**Why it's wrong:** Fdata always casts to float64 and adds allocation overhead (IDs, rangeval, metadata). `check_estimator` passes various dtypes (float32, int) to test estimator dtype handling — Fdata's internal cast would hide failures. The native functions accept numpy directly; Fdata wrapping is never needed inside an sklearn estimator.

**Do this instead:** `result = _native.smoothing.nadaraya_watson(X, self.argvals_, ...)`

### Anti-Pattern 2: Converting argvals in `__init__`

**What people do:** `self.argvals = np.asarray(argvals) if argvals is not None else None`

**Why it's wrong:** `get_params()` returns the stored value. `clone()` passes it back to `__init__`. If the original was `None`, fine. But if the original was a Python list `[0, 0.5, 1.0]`, `get_params()` returns an ndarray (not the original list), breaking the round-trip test that `check_estimator` runs. Any dtype coercion in `__init__` also breaks the test.

**Do this instead:** `self.argvals = argvals` verbatim; convert only in `_resolve_argvals()` at fit time.

### Anti-Pattern 3: Shared State Between `__init__` and `transform`

**What people do:** Computing and caching `self._argvals_array = np.arange(100)` during `__init__` using a hardcoded default, then using it in `transform()`.

**Why it's wrong:** `n_features` is not known at `__init__` time when `argvals=None`. More critically, `GridSearchCV` calls `set_params(n_components=k)` then `fit()` — any `__init__`-cached derived state will be stale. All derived state must be set in `fit()` with trailing underscore names.

**Do this instead:** All derived/resolved state in `fit()`, stored as `self.argvals_`, `self.coef_`, etc.

### Anti-Pattern 4: Registering sklearn in `fdars/__init__.py`

**What people do:** Adding `from fdars import sklearn` or adding `"sklearn"` to `_submodule_names` in `fdars/__init__.py`.

**Why it's wrong:** Makes `import fdars` fail for users without scikit-learn installed, breaking the base-package-stays-sklearn-free constraint (a hard requirement from PROJECT.md).

**Do this instead:** Keep `fdars/__init__.py` unchanged. Users do `from fdars.sklearn import FdarsFPCA` explicitly, same as `from fdars.mcp.server import mcp`.

### Anti-Pattern 5: Storing Fitted State Without Trailing Underscore

**What people do:** `self.coef = coefs` (no underscore) inside `fit()`.

**Why it's wrong:** `check_is_fitted(self)` looks for any attribute with a trailing underscore to determine if the estimator is fitted. If no such attribute exists, it falls back to `__sklearn_is_fitted__`. Having fit-time state stored without trailing underscores means the estimator appears unfitted, causing `check_is_fitted` to raise before `transform` or `predict`.

**Do this instead:** All fit-time state: `self.coef_`, `self.argvals_`, `self.n_components_`, etc.

## Integration Points with Existing Architecture

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `fdars.sklearn` → `fdars._native` | Direct import: `from fdars import _native` | Same import path used by `fdata_class.py` and `_augment.py`; zero change needed in native layer |
| `fdars.sklearn` → `fdars.fdata_class` | NOT imported | Estimators bypass the Fdata OOP wrapper; call native functions directly |
| `fdars.sklearn` → `fdars.advisor` | NOT imported | Parallel optional packages with no cross-dependency |
| `fdars.__init__` → `fdars.sklearn` | NOT imported (by design) | Base package stays sklearn-free |
| `fdars.sklearn.transformers` → `fdars.sklearn._base` | Direct import | One-directional; `_base.py` has no deps on transformers |
| `fdars.sklearn.predictors` → `fdars.sklearn._base` | Direct import | Same one-directional pattern |

### MkDocs Nav Integration

Add a top-level nav section (same pattern as "AI Advisor"):

```yaml
nav:
  # ... existing sections ...
  - scikit-learn API:
    - sklearn/index.md                       # concept page: layer overview, Pipeline/GridSearchCV
    - Transformers: sklearn/transformers.md  # per-transformer reference
    - Predictors: sklearn/predictors.md      # per-predictor reference
    - Pipeline Example: sklearn/pipeline-example.md
  # ... Reference, Examples unchanged ...
```

### Offline Fence Pattern for Docs

The same `FDARS_FENCE_OK` mechanism used in the advisor docs applies. Fences using `fdars.sklearn` run fully offline (sklearn has no network dependency). The docs-build environment must have `scikit-learn` installed. Add `scikit-learn` to the `[dev]` extra or a `[docs]` extra in `pyproject.toml`.

Minimal example fence:

```python
# exec="1" html="1" source="above"
import numpy as np
from fdars.datasets import load_canadian_weather
from fdars.sklearn import FdarsFPCA
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge

day, X, meta = load_canadian_weather("temperature")
pipe = Pipeline([("fpca", FdarsFPCA(argvals=day, n_components=5)), ("ridge", Ridge())])
y = meta["latitude"].values
pipe.fit(X, y)
print(f"R2 = {pipe.score(X, y):.4f}  FDARS_FENCE_OK")
```

This fence is identical in structure to the existing advisor `python-api.md` fence — online import, offline execution, `FDARS_FENCE_OK` sentinel.

## Scalability Considerations

This is a library layer, not a service. "Scalability" means maintainability as the estimator surface grows.

| Concern | v9.0 initial | Future additions |
|---------|-------------|-----------------|
| Adding a new transformer | One class in `transformers.py`, one `check_estimator` test block | O(1); `_BaseFdarsEstimator` handles boilerplate |
| Adding a new predictor | One class in `predictors.py` | O(1) |
| 2D (surface) argvals support | Extend `_resolve_argvals` for tuple argvals | Single change point in `_base.py` |
| sklearn 1.6 `__sklearn_tags__` dataclass | Already handled in `_base.py` via capability detection | No estimator-level changes needed |
| `set_output` API / `get_feature_names_out` | Add `get_feature_names_out()` to each transformer that outputs interpretable features | Opt-in per estimator; no breaking change |

## Sources

- scikit-learn Developing Estimators guide: https://scikit-learn.org/stable/developers/develop.html (MEDIUM confidence — verified against stable docs 2026-08-31)
- fdars codebase source files read directly: `python/fdars/__init__.py`, `python/fdars/fdata_class.py`, `python/fdars/advisor/__init__.py`, `python/fdars/mcp/__init__.py`, `pyproject.toml`, `mkdocs.yml` (HIGH confidence — first-party source, read directly)
- scikit-fda FPCA docs: https://fda.readthedocs.io/en/latest/modules/preprocessing/autosummary/skfda.preprocessing.dim_reduction.FPCA.html (MEDIUM confidence — key insight: scikit-fda takes FDataGrid not plain arrays; fdars takes the opposite approach for check_estimator compliance)

---

*Architecture research for: fdars v9.0 sklearn-compatible estimator layer*
*Researched: 2026-08-31*
*Confidence: HIGH — grounded in direct source reading of all relevant fdars modules and sklearn upstream docs*
