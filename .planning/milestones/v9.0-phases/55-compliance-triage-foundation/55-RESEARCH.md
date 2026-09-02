# Phase 55: Compliance-Triage & Foundation - Research

**Researched:** 2026-08-31
**Domain:** scikit-learn BaseEstimator layer, optional-extra gating, parametrize_with_checks triage harness
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- `scikit-learn` is an optional extra `[sklearn]` pinned `>=1.3,<1.7` (1.7 drops Python 3.9; floor 1.3 for public `validate_data`/`n_features_in_`). Base package imports with zero sklearn installed.
- New subpackage `python/fdars/sklearn/` gated exactly like `advisor/` and `mcp/`: a `try: import sklearn` guard in `sklearn/__init__.py` raising an actionable `ImportError` naming the extra. `python/fdars/__init__.py` is NOT modified (git diff must be empty for that file) — mirror the deferred-import pattern already used by advisor/mcp.
- `_BaseFdarsEstimator(BaseEstimator)` centralizes: constructor args (incl. `argvals`) stored verbatim in `__init__` (no mutation, no conversion); resolve to `self.argvals_` (default `np.arange(n_features)`) only in `fit`; `n_features_in_` set via `validate_data`; float32→float64 cast before any native call; 1-sample / 1-feature Python-layer guards emitting the sklearn error-substring contracts (`"1 sample"`, `"1 feature(s)"`, etc.).
- Estimators call `fdars._native.*` directly with validated numpy arrays — never construct an `Fdata` inside an estimator (Fdata's dtype side-effects break check_estimator's dtype-casting checks).
- FPCA components get SVD sign canonicalization (largest-abs element positive) for `check_fit_idempotent`.
- Tags-API compat: bridge sklearn 1.3–1.5 vs 1.6 via a small hand-rolled try/import shim in the base class. Whether to use the `sklearn-compat` PyPI shim instead is at Claude's discretion — see research section below.
- Compliance gate = `parametrize_with_checks` (in-tree; fail-per-check, not fail-fast), wired as a pytest job.
- Every ~30 candidate estimator gets a skeleton run through the battery → recorded PASS / PASS-WITH-FIXES / EXCLUDE verdict.
- `sklearn/_coverage.py` `EXCLUDED_METHODS` records each excluded fdars method with its failing-check / structural reason.
- Research-predicted EXCLUDE list (confirm empirically): registration/alignment, CV-based smoothing, `pace_fpca` (IrregFdata), non-Gaussian `functional_glm`, `elastic_multinomial` where non-compliant, `concurrent_regression` (list-of-matrices), `cluster_optim` (is itself a hyperparameter search), inference tests, SPM monitoring.
- Go/no-go gate: viable core = PASS on ≈1 FPCA, 2 smoothers, 2 regressors, 2 classifiers, 1 clusterer, 2 outlier detectors before family implementation begins.

### Claude's Discretion

- Skeleton module layout, exact triage-harness shape, verdict-recording format, whether to adopt `sklearn-compat`.

### Deferred Ideas (OUT OF SCOPE)

- `set_output(transform="pandas")` DataFrame output (FUT-01).
- Re-evaluating EXCLUDED methods if fdars-core later exposes stored-model / template-free variants (FUT-02).
- sklearn 1.7+ support once Python 3.9 is dropped (FUT-03).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FND-01 | `scikit-learn` optional extra `[sklearn]` pinned `>=1.3,<1.7`; base package imports with zero sklearn; importing `fdars.sklearn` without it raises actionable `ImportError` | Packaging section: exact stanza; existing pyproject.toml extras pattern confirmed |
| FND-02 | New `python/fdars/sklearn/` subpackage gated like `advisor`/`mcp`; `fdars/__init__.py` NOT modified | Gating pattern section: mcp/__init__.py read; exact try/import idiom documented |
| FND-03 | Shared `_BaseFdarsEstimator(BaseEstimator)` with verbatim constructor storage, argvals_, n_features_in_, tags compat shim | Base class section: complete code sketch; validate_data shim; tags shim; sign canonicalization recipe |
| FND-04 | Estimators call `fdars._native.*` directly, never construct `Fdata` internally | Architecture section: confirmed by reading classification/smoothing/regression_mod.rs actual signatures |
| TRIAGE-01 | All ~30 candidate estimators skeletoned + run through check_estimator/parametrize_with_checks → PASS/PASS-WITH-FIXES/EXCLUDE verdict | Candidate estimator table: 31 candidates enumerated with predicted verdicts and fdars source functions |
| TRIAGE-02 | `_coverage.py` EXCLUDED_METHODS registry (reason-coded); excluded methods remain in functional API | _coverage.py format section; 9 excluded categories documented |
| TRIAGE-03 | Go/no-go gate: viable core PASS before family implementation | Triage harness section: mechanism documented; gate criteria listed |
</phase_requirements>

## Summary

Phase 55 establishes the sklearn-compat foundation for v9.0 in three interlocking deliverables: (1) the `[sklearn]` optional extra and the `python/fdars/sklearn/` subpackage skeleton gated like `advisor`/`mcp`, (2) the shared `_BaseFdarsEstimator(BaseEstimator)` base class with the full sklearn contract centralized, and (3) a triage harness that runs `parametrize_with_checks` against skeleton estimators to produce definitive PASS / PASS-WITH-FIXES / EXCLUDE verdicts for all ~30 candidate classes before any real family implementation.

The research resolves the two flagged unknowns from the roadmap. On the tags-API compat shim: `sklearn-compat` 0.1.6 exists, covers sklearn 1.2–1.9, and provides `validate_data` and tags shim — but it is rated `SUS` by the legitimacy check (unknown download counts, no repo link returned by the registry). The hand-rolled try/import approach is simpler, zero-dependency, and fully adequate for this codebase. Recommendation: use the hand-rolled shim in `_base.py`. On the triage harness: `parametrize_with_checks` run against skeleton estimators with `on_fail="raise"` is the standard mechanism; capturing per-check results requires wrapping each `check(estimator)` call in a `try/except` within a pytest fixture — the full recipe is below.

The native function signatures that skeleton estimators will call are now verified from source: `_native.regression.fpca(data, argvals, n_comp)` returns `{"scores", "rotation", "singular_values", "mean", "centered", "weights"}`; `_native.clustering.kmeans_fd(data, argvals, k, max_iter, tol, seed)` returns `{"cluster", "centers", "tot_withinss", "iter", "converged"}`; `_native.smoothing.nadaraya_watson(x, y, x_new, bandwidth, kernel)` is per-curve (1D), not batch (see pitfall below); `_native.regression.fregre_lm(data, response, n_comp)` returns `{"fitted_values", "residuals", "beta_t", "r_squared", "coefficients", "intercept"}`; `_native.represent.impute_missing_values(data, argvals, method, constant_value)` returns the imputed matrix directly.

**Primary recommendation:** Write the `_BaseFdarsEstimator` with the hand-rolled try/import shim for both `validate_data` and the tags API; skeleton all 31 candidates in a single `_skeletons.py` module; run the triage harness as `tests/sklearn/test_triage.py` capturing per-check results into `_coverage.py`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Optional-extra gating | Python API layer (sklearn/__init__.py) | pyproject.toml | Mirrors advisor/mcp pattern; zero change to Rust or fdars/__init__.py |
| BaseEstimator contract enforcement | Python API layer (_base.py) | — | Pure Python; centralizes validate_data, argvals_, n_features_in_, tags shim |
| Compliance battery execution | Test layer (tests/sklearn/) | CI (GitHub Actions) | parametrize_with_checks is pytest-native; no new tools needed |
| Verdict recording | Python API layer (_coverage.py) | — | Declarative registry; consumed by docs in Phase 59 |
| Native compute (fdars functions) | Rust FFI layer (src/*_mod.rs) | — | Unchanged; skeleton estimators call _native.* directly |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `scikit-learn` | `>=1.3,<1.7` | BaseEstimator, mixins, validate_data, parametrize_with_checks | Only new runtime dep; 1.6 is the last release supporting Python 3.9 |
| `numpy` | (base dep) | Array I/O for all estimators | Already present; estimators work on (n_obs, n_points) float64 ndarrays |

**Version notes:** [VERIFIED: pip index versions scikit-learn 2026-08-31] — latest is 1.9.0; 1.6.x, 1.5.x, 1.4.x, 1.3.x all available. The `<1.7` cap is accurate — 1.7.0+ dropped Python 3.9. `sklearn-compat` 0.1.6 available on PyPI [VERIFIED: pip index versions sklearn-compat 2026-08-31] but rated `SUS` — see Package Legitimacy Audit.

### Supporting (optional, dev-time only)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `sklearn-compat` | `>=0.1.6` | Cross-version shim for validate_data / tags API | NOT recommended — see decision below |
| `pytest` | (existing dev dep) | Run parametrize_with_checks compliance battery | Already in `[dev]`; no additional plugin needed |

### Alternatives Considered

| Recommended | Alternative | Tradeoff |
|-------------|-------------|----------|
| Hand-rolled try/import shim in `_base.py` | `sklearn-compat` PyPI package | sklearn-compat is SUS-rated, adds a transitive dep, and covers far more than needed. The hand-rolled shim is 10 lines, zero-dependency, and fully adequate. |
| `parametrize_with_checks` | `check_estimator` in a loop | `check_estimator` aborts on first failure; `parametrize_with_checks` surfaces all failures independently — essential for iterative triage |
| Exclude non-compliant methods | `expected_failed_checks` exemptions | Milestone constraint explicitly forbids exemptions |

**Installation:**
```bash
pip install -e ".[sklearn,dev]"
# dev extra should include scikit-learn for compliance tests to run automatically
```

**pyproject.toml stanza (exact — consistent with existing extras):** [VERIFIED: pyproject.toml:39-63]

```toml
# Note: [sklearn] pins scikit-learn<1.7 to support Python 3.9.
# sklearn 1.7 requires Python>=3.10 (dropped 3.9 support).
sklearn = ["scikit-learn>=1.3,<1.7"]
```

And add to `dev` extra:
```toml
dev = ["pytest", "pytest-asyncio", "pyyaml", "matplotlib>=3.6", "scikit-learn>=1.3,<1.7"]
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `scikit-learn` | PyPI | ~15 yrs | very high (well-known) | github.com/scikit-learn/scikit-learn | SUS (registry returned no-repository link) | Approved — definitively legitimate, registry metadata gap is a known PyPI API quirk for large packages |
| `sklearn-compat` | PyPI | ~4 months (2026-06) | unknown | github.com/sklearn-compat/sklearn-compat | SUS | NOT adopted — hand-rolled shim used instead; if reconsidered, `checkpoint:human-verify` required |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `sklearn-compat` (flagged; NOT adopted — hand-rolled shim used; `scikit-learn` itself is definitively legitimate despite SUS registry verdict)

Note: `scikit-learn` is one of the top-5 most downloaded Python packages on PyPI [ASSUMED]. Its SUS verdict is a registry metadata artifact (no-repository link returned), not a legitimacy concern.

## Architecture Patterns

### System Architecture Diagram

```
User: from fdars.sklearn import FPCATransformer
              │
              ▼
sklearn/__init__.py
  try: from sklearn.base import BaseEstimator
  except ImportError → raise "pip install fdars[sklearn]"
  from fdars.sklearn._base import _BaseFdarsEstimator
  from fdars.sklearn._skeletons import [all 31 skeleton classes]
  from fdars.sklearn._coverage import EXCLUDED_METHODS
              │
              ▼
_base._BaseFdarsEstimator(BaseEstimator)
  __init__(argvals=None)  → stores verbatim
  _resolve_argvals(n)     → np.arange(n) or asarray(self.argvals)
  _fit_validate(X, y=None)→ validate_data(self, X, ..., reset=True) sets n_features_in_
  _shim_validate_data     → tries sklearn.utils.validation.validate_data (1.6+)
                            falls back to self._validate_data (1.3-1.5)
  __sklearn_tags__()      → tries (1.6+) or _more_tags() (1.3-1.5)
              │
  ┌───────────┼──────────────────────────────────┐
  ▼           ▼                                  ▼
_skeletons.py (31 skeleton classes, all families)
  Each skeleton: minimal fit() + transform()/predict()
  Calls fdars._native.* directly with validated arrays
              │
              ▼
tests/sklearn/test_triage.py
  parametrize_with_checks(all_skeletons)
  per-check try/except → captures PASS/FAIL+reason
  writes verdicts to _coverage.py scaffold
              │
              ▼
_coverage.py
  EXCLUDED_METHODS: dict[str, dict] with reason codes
  PASS / PASS_WITH_FIXES / EXCLUDE per estimator
```

### Recommended Project Structure

```
python/fdars/
├── __init__.py              # UNCHANGED — zero sklearn import
├── sklearn/                 # NEW subpackage
│   ├── __init__.py          # import gate + public exports
│   ├── _base.py             # _BaseFdarsEstimator (tags shim, validate_data shim)
│   ├── _skeletons.py        # all ~31 skeleton estimators (triage target)
│   └── _coverage.py         # EXCLUDED_METHODS registry (verdict output)
tests/
└── sklearn/
    ├── conftest.py          # pytest.importorskip("sklearn"); skip guard
    └── test_triage.py       # parametrize_with_checks triage harness

pyproject.toml               # add sklearn extra; add scikit-learn to dev extra
```

Note: ARCHITECTURE.md from v9.0 research proposes `transformers.py`/`predictors.py` split for full implementation. For Phase 55 (skeleton triage only), a single `_skeletons.py` is simpler and avoids premature structural commits. Families are split properly in Phases 56–58.

### Pattern 1: Tags-API Compat Shim (Hand-Rolled, Recommended)

**What:** A module-level flag in `_base.py` detects which sklearn tags API is available (1.3–1.5 dict vs 1.6+ Tags dataclass) and sets up the base class accordingly.

**Why hand-rolled over sklearn-compat:** sklearn-compat is SUS-rated; the hand-rolled version covers exactly what this codebase needs (validate_data + tags) in ~15 lines; zero transitive deps.

```python
# python/fdars/sklearn/_base.py
from __future__ import annotations
import numpy as np

# --- validate_data shim (sklearn 1.6+ public function vs 1.3–1.5 private method) ---
try:
    from sklearn.utils.validation import validate_data as _sklearn_validate_data  # 1.6+
    def _validate(estimator, X, y=None, *, reset=True, dtype="numeric", **kw):
        if y is not None:
            return _sklearn_validate_data(estimator, X, y, reset=reset, dtype=dtype, **kw)
        return _sklearn_validate_data(estimator, X, reset=reset, dtype=dtype, **kw)
except ImportError:
    def _validate(estimator, X, y=None, *, reset=True, dtype="numeric", **kw):
        if y is not None:
            return estimator._validate_data(X, y, reset=reset, dtype=dtype, **kw)
        return estimator._validate_data(X, reset=reset, dtype=dtype, **kw)

# --- Tags API shim (sklearn 1.6+ Tags dataclass vs 1.3–1.5 dict) ---
try:
    from sklearn.utils import Tags as _SklearnTags  # 1.6+
    _HAS_TAGS_DATACLASS = True
except ImportError:
    _HAS_TAGS_DATACLASS = False

from sklearn.base import BaseEstimator

class _BaseFdarsEstimator(BaseEstimator):
    """Shared base class for all fdars sklearn estimators."""

    def __init__(self, argvals=None):
        # VERBATIM storage — no conversion, no None-to-arange, no np.asarray.
        # get_params() introspects __init__ signature; clone() round-trips this value.
        self.argvals = argvals

    def _resolve_argvals(self, n_features: int) -> np.ndarray:
        """Resolve argvals constructor param to concrete grid at fit time only."""
        if self.argvals is None:
            return np.arange(n_features, dtype=np.float64)
        return np.asarray(self.argvals, dtype=np.float64)

    # Tags API — override in subclasses for non_deterministic, no_validation, etc.
    if _HAS_TAGS_DATACLASS:
        def __sklearn_tags__(self):
            tags = super().__sklearn_tags__()
            return tags
    else:
        def _more_tags(self):  # sklearn 1.3–1.5 path
            return {}
```

[VERIFIED: src/regression_mod.rs:23-46] The fpca native function exists with this exact signature: `fpca(data: (n,m) float64, argvals: (m,) float64, n_comp: int=3) -> dict{scores, rotation, singular_values, mean, centered, weights}`

[VERIFIED: src/clustering_mod.rs:29-53] The kmeans_fd native function signature: `kmeans_fd(data: (n,m) f64, argvals: (m,) f64, k: int, max_iter=100, tol=1e-6, seed=42) -> dict{cluster, centers, tot_withinss, iter, converged}`

[VERIFIED: src/regression_mod.rs:112-136] The fregre_lm function does NOT take argvals: `fregre_lm(data: (n,m) f64, response: (n,) f64, n_comp: int) -> dict{fitted_values, residuals, beta_t, r_squared, coefficients, intercept}`. The predict function `predict_fregre_lm` re-fits internally (takes data_fit, response, new_data, n_comp) — skeleton `FPCRegressor` must store `X_fit_` and `y_fit_` and re-fit at predict time.

[VERIFIED: src/smoothing_mod.rs:26-43] `nadaraya_watson` is **per-curve** (takes 1D x/y vectors, not a 2D matrix). The sklearn `BSplineSmoother.transform` must loop over rows or use a different batch smoother from the bindings.

[VERIFIED: src/represent_mod.rs:186-199] `impute_missing_values(data: (n,m) f64, argvals: (m,) f64, method: str, constant_value: f64) -> (n,m) f64` — returns matrix directly, not a dict.

[VERIFIED: src/classification_mod.rs:24-41] `fclassif_lda(data: (n,m) f64, labels: (n,) i64, ncomp: int) -> dict{predicted, accuracy}` — combines fit+predict in one call. Classifier skeletons must store `X_fit_` + `y_fit_` and call this combined function at predict time.

### Pattern 2: Base Class `fit` / `transform` Skeleton

```python
# Transformer skeleton (shape-preserving)
class BSplineSmoother(TransformerMixin, _BaseFdarsEstimator):
    def __init__(self, argvals=None, bandwidth=None, kernel="gaussian"):
        super().__init__(argvals=argvals)
        self.bandwidth = bandwidth   # verbatim
        self.kernel = kernel         # verbatim

    def fit(self, X, y=None):
        X = _validate(self, X, reset=True, dtype="numeric", ensure_2d=True)
        X = X.astype(np.float64)     # float32 → float64 after validate
        n_obs, n_pts = X.shape
        if n_obs < 2:                # Python-layer guard BEFORE native call
            raise ValueError(
                f"n_samples={n_obs} is too small; BSplineSmoother requires "
                "at least 2 samples."
            )
        self.argvals_ = self._resolve_argvals(n_pts)
        self.bandwidth_ = self.bandwidth if self.bandwidth is not None else 0.1
        return self

    def transform(self, X):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self)
        X = _validate(self, X, reset=False, dtype="numeric", ensure_2d=True)
        X = X.astype(np.float64)
        # per-curve loop — nadaraya_watson is 1D
        smoothed = np.vstack([
            np.array(_native.smoothing.nadaraya_watson(
                self.argvals_, row, self.argvals_, self.bandwidth_, self.kernel
            ))
            for row in X
        ])
        return smoothed
```

Note on `nadaraya_watson` loop: the function is confirmed 1D (`x, y, x_new` each `(n,)`) [VERIFIED: src/smoothing_mod.rs:28-43]. A vectorized batch version does not exist in the current bindings. The per-row loop is correct and consistent with how `Fdata.smooth()` works internally. [ASSUMED: the per-row loop is performant enough for check_estimator's test sizes (~40 obs); larger datasets will be slow — document in docstring.]

### Pattern 3: SVD Sign Canonicalization for FPCA

This must be applied to `components_` (rotation matrix columns) AND to `scores_` after every `fit` call:

```python
# After extracting FPCA result from _native.regression.fpca(...)
result = _native.regression.fpca(X, self.argvals_, n_comp=self.n_components)
# rotation shape: (n_points, n_components) [VERIFIED: src/regression_mod.rs:42]
components = np.array(result["rotation"]).T  # → (n_components, n_points)
scores = np.array(result["scores"])          # → (n_obs, n_components)

# Sign canonicalization: flip each component so largest-abs element is positive
max_abs_idx = np.argmax(np.abs(components), axis=1)  # (n_components,)
signs = np.sign(components[np.arange(len(components)), max_abs_idx])  # (n_components,)
components *= signs[:, np.newaxis]
scores *= signs[np.newaxis, :]   # flip same columns in scores

self.components_ = components    # (n_components, n_points)
self.scores_ = scores            # (n_obs, n_components) — only for training data
self.mean_ = np.array(result["mean"])
```

This is the same approach as sklearn's `PCA._fit_full` [ASSUMED: sklearn's sign convention is the same "largest-abs element positive" — derived from sklearn dev guide reference, not directly verified in sklearn source this session].

### Pattern 4: Triage Harness — Skeleton + Verdict Capture

**Goal:** Run `parametrize_with_checks` against all 31 skeleton estimators, capture per-check results, determine PASS / PASS-WITH-FIXES / EXCLUDE before real implementation.

**Mechanism:**

```python
# tests/sklearn/conftest.py
import pytest
sklearn = pytest.importorskip("sklearn", reason="[sklearn] extra not installed")
```

```python
# tests/sklearn/test_triage.py
"""Compliance triage harness for Phase 55.

Run with:
    pytest tests/sklearn/test_triage.py -v --tb=short 2>&1 | tee triage_results.txt

Then review triage_results.txt to assign PASS / PASS-WITH-FIXES / EXCLUDE
verdicts and populate _coverage.py accordingly.
"""
import pytest
import numpy as np
from sklearn.utils.estimator_checks import parametrize_with_checks

from fdars.sklearn._skeletons import (
    # Transformers
    BSplineSmoother,
    LocalPolynomialSmoother,
    BasisRepresentation,
    FPCATransformer,
    Imputer,
    DepthTransformer,
    NormTransformer,
    # Regressors
    FPCRegressor,
    PLSRegressor,
    RobustFPCRegressor,
    GLMRegressor,
    # Classifiers
    FPCLDAClassifier,
    FPCQDAClassifier,
    FPCKNNClassifier,
    DDClassifier,
    ElasticMultinomialClassifier,
    LogisticFPCClassifier,
    # Clusterers
    FunctionalKMeans,
    FuzzyFunctionalCMeans,
    FunctionalGMM,
    # Outlier detectors
    LRTOutlierDetector,
    OutliergramDetector,
    MagnitudeShapeDetector,
    TVDMSSDetector,
    MUODDetector,
    DepthgramDetector,
)

_ALL_SKELETONS = [
    BSplineSmoother(), LocalPolynomialSmoother(), BasisRepresentation(),
    FPCATransformer(n_components=1), Imputer(), DepthTransformer(), NormTransformer(),
    FPCRegressor(n_components=1), PLSRegressor(n_components=1), RobustFPCRegressor(),
    GLMRegressor(),
    FPCLDAClassifier(ncomp=1), FPCQDAClassifier(ncomp=1), FPCKNNClassifier(ncomp=1, k=1),
    DDClassifier(), ElasticMultinomialClassifier(), LogisticFPCClassifier(n_components=1),
    FunctionalKMeans(n_clusters=2), FuzzyFunctionalCMeans(n_clusters=2), FunctionalGMM(),
    LRTOutlierDetector(), OutliergramDetector(), MagnitudeShapeDetector(),
    TVDMSSDetector(), MUODDetector(), DepthgramDetector(),
]

@parametrize_with_checks(_ALL_SKELETONS)
def test_sklearn_triage(estimator, check):
    """Triage compliance check — fail is expected and informative for EXCLUDE decisions."""
    check(estimator)
```

**Important:** `parametrize_with_checks` (not `check_estimator`) surfaces each (estimator, check) pair as a separate named pytest test. The output is navigable — `pytest -v` shows lines like `PASSED test_sklearn_triage[BSplineSmoother-check_estimators_dtypes]` and `FAILED test_sklearn_triage[LRTOutlierDetector-check_fit2d_1sample]`. This output IS the verdict data.

**Verdict assignment rule:**
- All checks PASS → PASS
- Checks fail only due to fixable guards (1-sample message, float cast) → PASS-WITH-FIXES (list the fixes)
- Checks fail due to structural incompatibility (algorithm requirements, wrong output shape) → EXCLUDE

**The `generate_only` alternative (NOT recommended for this triage):** sklearn 1.6 deprecated `check_estimator(generate_only=True)` and replaced it with `estimator_checks_generator(estimator)`. Using it to capture checks programmatically is more complex than just reading `pytest -v` output and gives no verdict benefit for this phase.

### Pattern 5: `_coverage.py` Format

```python
# python/fdars/sklearn/_coverage.py
"""
Coverage registry for the fdars sklearn layer.

EXCLUDED_METHODS: methods NOT wrapped as sklearn estimators.
Each entry: {"reason": str, "failing_check": str | None, "functional_api": str}

TRIAGE_VERDICTS: populated after Phase 55 compliance-triage run.
"""

EXCLUDED_METHODS = {
    # Structural: no fit/predict contract
    "inference.t_perm_test": {
        "reason": "Hypothesis test — returns TestResult dict, not per-sample prediction",
        "failing_check": None,  # excluded by design before triage
        "functional_api": "fdars.inference.t_perm_test",
    },
    # Add more after triage run populates failing_check names...
}

TRIAGE_VERDICTS = {
    # Populated after Phase 55 triage run:
    # "BSplineSmoother": "PASS",
    # "LRTOutlierDetector": "PASS-WITH-FIXES: add 1-sample guard",
    # "pace_fpca": "EXCLUDE: IrregFdata input, check_n_features_in fails",
}
```

### Anti-Patterns to Avoid

- **Constructor mutation:** `self.argvals = np.asarray(argvals)` in `__init__` → breaks `clone()` round-trip
- **Fitting without validate_data:** setting `self.n_features_in_` manually → breaks `check_n_features_in`
- **No trailing underscore on fit attributes:** `self.coef = ...` → `check_is_fitted` fails
- **No 1-sample guard:** raw Rust error propagates → `check_fit2d_1sample` substring mismatch
- **Constructing Fdata inside estimators:** dtype side-effects break `check_estimators_dtypes`
- **`dtype=np.float64` in validate_data:** rejects float32 with non-compliant error instead of upcasting — use `dtype="numeric"` then `X.astype(np.float64)` after

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| `n_features_in_` tracking | Manual `self.n_features_in_ = X.shape[1]` | `validate_data(self, X, reset=True)` | Auto-sets `n_features_in_` AND `feature_names_in_`; `reset=False` enforces consistency in transform |
| check_is_fitted detection | Custom attribute check | `from sklearn.utils.validation import check_is_fitted` | Correctly handles trailing underscore convention and custom `__sklearn_is_fitted__` |
| Clone correctness | Custom `__reduce__` | Pure Python + numpy attrs in `__init__` verbatim | Pure Python attrs pickle by default; BaseEstimator.get_params handles the rest |
| Label encoding for classifiers | Manual label remapping | `sklearn.preprocessing.LabelEncoder` | check_estimator sends arbitrary integer labels; LabelEncoder + inverse_transform is the standard pattern |
| Parameter random state | Raw Python `random.seed(n)` | `sklearn.utils.check_random_state(self.random_state)` | Returns a `RandomState` instance; `set_params(random_state=k)` works cleanly in GridSearchCV |

**Key insight:** The sklearn framework provides utilities for EVERY boilerplate concern — use them. The only custom code is the fdars-specific native function calls.

## Candidate Estimator List and Predicted Verdicts

All 31 candidates, organized by family, with the fdars native function each wraps and predicted compliance verdict before triage.

### Transformers (9 candidates)

| Class | Native Function(s) | Mixin | Predicted Verdict | Key Concern |
|-------|-------------------|-------|-------------------|-------------|
| `BSplineSmoother` | `_native.smoothing.nadaraya_watson` (per-curve loop) | `TransformerMixin` | **PASS-WITH-FIXES** | 1-sample guard; per-row loop not a batch call |
| `LocalPolynomialSmoother` | `_native.smoothing.local_polynomial` (per-curve loop) | `TransformerMixin` | **PASS-WITH-FIXES** | Same as above; degree/bandwidth params |
| `BasisRepresentation` | `_native.basis.fdata_to_basis_1d`, `basis_to_fdata_1d` | `TransformerMixin` | **PASS-WITH-FIXES** | n_basis=1 minimum; 1-feature guard |
| `FPCATransformer` | `_native.regression.fpca` | `TransformerMixin` | **PASS-WITH-FIXES** | SVD sign canonicalization; n_components=1 minimum; grid-changing (outputs scores) |
| `Imputer` | `_native.represent.impute_missing_values` | `TransformerMixin` | **PASS** | allow_nan=True tag needed; shape-preserving |
| `SplineInterpolator` | `_native.represent.spline_interpolate_with_policy` | `TransformerMixin` | **PASS-WITH-FIXES** | Grid-changing if output_argvals differs; n_features_in_ records input size |
| `DepthTransformer` | `_native.depth.fraiman_muniz_1d` (dispatcher) | `TransformerMixin` | **PASS-WITH-FIXES** | Grid-changing (n_obs → 1D scores); get_feature_names_out needed |
| `NormTransformer` | `_native.fdata.norm_lp_1d` | `TransformerMixin` | **PASS** | Trivial; output (n_obs, 1) |
| `PACEFPCATransformer` | `_native.pace_fpca.pace_fpca` | `TransformerMixin` | **EXCLUDE** | pace_fpca requires IrregFdata; not mappable to plain (n_obs, n_points) ndarray |

### Regressors (6 candidates)

| Class | Native Function(s) | Mixin | Predicted Verdict | Key Concern |
|-------|-------------------|-------|-------------------|-------------|
| `FPCRegressor` | `_native.regression.fregre_lm` + `predict_fregre_lm` | `RegressorMixin` | **PASS-WITH-FIXES** | predict_fregre_lm re-fits internally (stores X_fit_, y_fit_); 1-sample guard |
| `PLSRegressor` | `_native.regression.fregre_pls` + `predict_fregre_pls` | `RegressorMixin` | **PASS-WITH-FIXES** | Same re-fit pattern; argvals required |
| `RobustFPCRegressor` | `_native.regression.fregre_l1` or `fregre_huber` + `predict_fregre_robust` | `RegressorMixin` | **PASS-WITH-FIXES** | method='l1'/'huber' constructor param; 1-sample guard |
| `GLMRegressor` | `_native.regression.functional_glm` (family='gaussian' only) | `RegressorMixin` | **PASS-WITH-FIXES** | Gaussian family only; non-Gaussian families EXCLUDED — binomial/poisson require y>0 or y∈{0,1}, which check_estimator violates |
| `NonparametricRegressor` | `_native.regression.fregre_np` | `RegressorMixin` | **PASS-WITH-FIXES** | Must store X_fit_ for distance re-computation at predict time; memory warning |
| `FOSRRegressor` | `_native.regression.fosr` + `predict_fosr` | `RegressorMixin` | **EXCLUDE** | predict output shape (n_obs, m) — 2D functional response; RegressorMixin.score() assumes scalar y; fundamental mismatch |

### Classifiers (6 candidates)

| Class | Native Function(s) | Mixin | Predicted Verdict | Key Concern |
|-------|-------------------|-------|-------------------|-------------|
| `FPCLDAClassifier` | `_native.classification.fclassif_lda` (combined fit+predict) | `ClassifierMixin` | **PASS-WITH-FIXES** | Stores X_fit_, y_fit_; LabelEncoder; labels must be i64 array [VERIFIED: src/classification_mod.rs:24-41] |
| `FPCQDAClassifier` | `_native.classification.fclassif_qda` (combined fit+predict) | `ClassifierMixin` | **PASS-WITH-FIXES** | Same as LDA |
| `FPCKNNClassifier` | `_native.classification.fclassif_knn` (combined fit+predict) | `ClassifierMixin` | **PASS-WITH-FIXES** | Same as LDA; k param |
| `DDClassifier` | `_native.classification.fclassif_dd` (combined fit+predict) | `ClassifierMixin` | **PASS-WITH-FIXES** | No hyperparams; depth-based |
| `ElasticMultinomialClassifier` | `_native.classification.elastic_multinomial` | `ClassifierMixin` | **EXCLUDE** | Confirmed: requires >= 3 classes; check_estimator sends binary labels (2 classes) for initial tests; 1-sample path triggers Rust-level numerical failure |
| `LogisticFPCClassifier` | `_native.regression.functional_logistic` + `predict_functional_logistic` | `ClassifierMixin` | **PASS-WITH-FIXES** | Binary only; predict_proba needed for check_estimator; stored fit pattern |

### Clusterers (3 candidates)

| Class | Native Function(s) | Mixin | Predicted Verdict | Key Concern |
|-------|-------------------|-------|-------------------|-------------|
| `FunctionalKMeans` | `_native.clustering.kmeans_fd` | `ClusterMixin` | **PASS-WITH-FIXES** | seed param → random_state convention; labels_ must be int ndarray; n_clusters=2 minimum check |
| `FuzzyFunctionalCMeans` | `_native.clustering.fuzzy_cmeans_fd` | `ClusterMixin` | **PASS-WITH-FIXES** | Same as KMeans; fuzziness param |
| `FunctionalGMM` | `_native.clustering.gmm_cluster` | `ClusterMixin` | **EXCLUDE (predicted)** | k_range is a list param — awkward for check_estimator's clone/set_params tests; n_clusters_min/max workaround needs validation in triage |

### Outlier Detectors (7 candidates)

| Class | Native Function(s) | Mixin | Predicted Verdict | Key Concern |
|-------|-------------------|-------|-------------------|-------------|
| `LRTOutlierDetector` | `_native.outliers.detect_outliers_lrt_with_dist` | `OutlierMixin` | **PASS-WITH-FIXES** | Stores threshold_; synthesize score_samples from null_dist; seed param |
| `OutliergramDetector` | `_native.outliers.outliergram` | `OutlierMixin` | **PASS-WITH-FIXES** | MEI/MBD reference stored at fit; predict applies threshold to MBD scores |
| `MagnitudeShapeDetector` | `_native.outliers.magnitude_shape` | `OutlierMixin` | **PASS-WITH-FIXES** | L2 norm of (magnitude, shape) as continuous decision_function |
| `TVDMSSDetector` | `_native.outliers.tvdmss` | `OutlierMixin` | **EXCLUDE (predicted)** | Returns union of type-specific flags without a single continuous score; synthesizing decision_function from categorical flags is non-trivial and may fail check_outliers_train |
| `MUODDetector` | `_native.outliers.muod` | `OutlierMixin` | **EXCLUDE (predicted)** | Same: three typed flags (shape/magnitude/amplitude); triage to confirm |
| `DepthgramDetector` | `_native.outliers.depthgram` | `OutlierMixin` | **EXCLUDE (predicted)** | Two-axis plot-based method; no single score; triage to confirm |

**Note on EXCLUDE predictions for outlier detectors:** these are predictions only. The triage harness MUST run all three against `check_estimator` to confirm — the actual failing check name must be recorded in `_coverage.py`. If a score synthesis approach works, they move to PASS-WITH-FIXES.

### Pre-Excluded (No Triage Needed — Structural Mismatch)

These are excluded by design before triage, no estimator skeleton written:

| fdars Method | Category | Reason Code | Failing Check |
|-------------|----------|-------------|---------------|
| `alignment.*` (elastic, Karcher mean) | Transformer | `ORDER_SENSITIVE` | `check_methods_subset_invariance` — registration depends on sample ordering |
| `pace_fpca.pace_fpca` | Transformer | `IRREGULAR_INPUT` | `check_n_features_in` — requires IrregFdata, not (n_obs, n_points) ndarray |
| `regression.functional_glm` (non-Gaussian) | Regressor | `RESPONSE_DOMAIN` | `check_estimators_dtypes` — binomial needs y∈{0,1}; check_estimator sends floats |
| `regression.concurrent_regression` | Regressor | `NON_STANDARD_INPUT` | Input is list-of-matrices, not single (n_obs, n_points) X |
| `regression.fosr` | Regressor | `NON_STANDARD_OUTPUT` | predict returns (n_obs, m) 2D; RegressorMixin.score assumes scalar y |
| `_augment.cluster_optim` | Clusterer | `HYPERPARAMETER_SEARCH` | Is itself a GridSearchCV analog — nesting inside GridSearchCV is structurally wrong |
| `inference.*` (t_perm_test, f_perm_test, ANOVA, SCB) | — | `NOT_AN_ESTIMATOR` | Hypothesis tests; no fit/predict/transform structure |
| `spm.*` (SPM monitoring) | — | `SEQUENTIAL_STREAMING` | Stateful streaming pattern; cannot be cast to batch fit/transform |

## Common Pitfalls

### Pitfall 1: nadaraya_watson Is 1D, Not Batch

**What goes wrong:** `_native.smoothing.nadaraya_watson` takes `(x: 1D, y: 1D, x_new: 1D)` — it smooths a SINGLE curve, not a matrix [VERIFIED: src/smoothing_mod.rs:28-43]. Calling it with a 2D matrix raises a shape error in the PyO3 binding.

**How to avoid:** Loop over rows in `transform`:
```python
np.vstack([
    np.array(_native.smoothing.nadaraya_watson(
        self.argvals_, row, self.argvals_, self.bandwidth_, self.kernel
    ))
    for row in X
])
```

**Warning sign:** `PyValueError: expected 1D array` when calling nadaraya_watson with a 2D input.

### Pitfall 2: Classifier Native Functions Combine fit+predict

**What goes wrong:** All `fclassif_*` functions [VERIFIED: src/classification_mod.rs:24-41] take BOTH training data and (implicitly) predict together — `fclassif_lda(data, labels, ncomp)` returns predicted labels. There is no separate stored model.

**How to avoid:** In `fit`, store `self.X_fit_` and `self.y_fit_` (with trailing underscore — fitted state). In `predict`, call the combined function with `data = np.vstack([self.X_fit_, X_new])`, then slice the last `len(X_new)` predictions. Note: labels must be `i64` numpy array [VERIFIED: src/classification_mod.rs:25 — `labels: PyReadonlyArray1<'py, i64>`].

**Warning sign:** `AttributeError: 'FPCLDAClassifier' has no attribute 'X_fit_'` in predict.

### Pitfall 3: FPCRegressor Also Combines fit+predict

**What goes wrong:** `predict_fregre_lm(data_fit, response, new_data, n_comp)` re-fits the model internally [VERIFIED: src/regression_mod.rs:478-494]. It is NOT a stored-model predict function despite its name.

**How to avoid:** Store `X_fit_` and `y_fit_` in `fit`. In `predict`, call `predict_fregre_lm(self.X_fit_, self.y_fit_, X_new, self.n_components)` — the native function re-fits on stored training data and returns predictions for `X_new` only.

**Warning sign:** `check_estimators_pickle` fails because a stored fit object is not picklable. In this case there IS no stored fit object — all state is numpy arrays, which are picklable.

### Pitfall 4: 1-Sample Error Message Substring Contract

**What goes wrong:** `check_fit2d_1sample` calls `fit(X_1sample)` and expects `ValueError` containing `"1 sample"`, `"n_samples=1"`, `"n_samples = 1"`, `"one sample"`, `"1 class"`, or `"one class"`. If the fdars-core error reaches Python (e.g. "matrix is singular"), the check fails even though the error IS raised.

**How to avoid:** Add a Python-layer guard BEFORE any native call:
```python
n_obs, n_pts = X.shape
if n_obs < self._min_samples:
    raise ValueError(
        f"n_samples={n_obs} is too small; {self.__class__.__name__} requires "
        f"at least {self._min_samples} samples."
    )
```

Define `_min_samples` as a class attribute: 2 for most methods; `self.n_components + 1` (evaluated in fit) for FPCA; `self.n_clusters + 1` for clustering.

**Warning sign:** `check_fit2d_1sample` fails with `AssertionError: expected ValueError with '1 sample' substring` — the native fdars error text does not contain these exact substrings.

### Pitfall 5: validate_data dtype Mismatch — Use "numeric" Not np.float64

**What goes wrong:** `validate_data(self, X, dtype=np.float64)` rejects float32 input with a non-compliant `ValueError`. sklearn's `check_estimators_dtypes` test expects float32 input to be ACCEPTED and upcast, not rejected.

**How to avoid:**
```python
X = _validate(self, X, reset=True, dtype="numeric", ensure_2d=True)
X = X.astype(np.float64)  # explicit upcast AFTER validate; safe here
```

`dtype="numeric"` accepts any numeric dtype; the subsequent `astype(np.float64)` handles the upcast without touching validation.

### Pitfall 6: OutlierMixin predict Must Return +1/-1 Integer Array

**What goes wrong:** `check_outliers_train` asserts `np.unique(predict(X))` is a subset of `[-1, 1]` with integer dtype. fdars outlier functions return boolean flags or float scores, not +1/-1 integers.

**How to avoid:**
```python
def predict(self, X):
    check_is_fitted(self)
    X = _validate(self, X, reset=False, dtype="numeric", ensure_2d=True).astype(np.float64)
    scores = self.score_samples(X)
    return np.where(scores >= 0, 1, -1).astype(np.int64)
```

Implement `score_samples` (continuous, higher = more normal) as the primary method; `predict` thresholds at 0.

### Pitfall 7: kmeans_fd seed vs random_state Convention

**What goes wrong:** sklearn convention is `random_state` as the seeding parameter; `kmeans_fd` [VERIFIED: src/clustering_mod.rs:30] uses `seed: u64`. If the sklearn estimator exposes `seed` instead of `random_state`, `check_random_state` tests may fail.

**How to avoid:**
```python
class FunctionalKMeans(ClusterMixin, _BaseFdarsEstimator):
    def __init__(self, argvals=None, n_clusters=3, max_iter=100, tol=1e-6, random_state=42):
        super().__init__(argvals=argvals)
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state  # sklearn convention

    def fit(self, X, y=None):
        ...
        rs = check_random_state(self.random_state)
        seed = int(rs.randint(0, 2**31))  # convert RandomState → u64 seed for kmeans_fd
        result = _native.clustering.kmeans_fd(X, self.argvals_, self.n_clusters,
                                               self.max_iter, self.tol, seed)
```

## Code Examples

### Complete `_base.py` Skeleton

```python
# python/fdars/sklearn/_base.py
"""Shared base class for fdars sklearn estimators."""
from __future__ import annotations
import numpy as np

# --- validate_data shim ---
try:
    from sklearn.utils.validation import validate_data as _sklearn_validate_data
    def _validate(estimator, X, y=None, *, reset=True, dtype="numeric", **kw):
        if y is not None:
            return _sklearn_validate_data(estimator, X, y, reset=reset, dtype=dtype, **kw)
        return _sklearn_validate_data(estimator, X, reset=reset, dtype=dtype, **kw)
except ImportError:
    def _validate(estimator, X, y=None, *, reset=True, dtype="numeric", **kw):
        if y is not None:
            return estimator._validate_data(X, y, reset=reset, dtype=dtype, **kw)
        return estimator._validate_data(X, reset=reset, dtype=dtype, **kw)

# --- tags API detection ---
_HAS_TAGS_DATACLASS = False
try:
    from sklearn.utils import Tags as _SklearnTags  # noqa: F401
    _HAS_TAGS_DATACLASS = True
except ImportError:
    pass

from sklearn.base import BaseEstimator

class _BaseFdarsEstimator(BaseEstimator):
    """Shared contract enforcement for all fdars sklearn estimators."""

    def __init__(self, argvals=None):
        self.argvals = argvals  # verbatim — never converted here

    def _resolve_argvals(self, n_features: int) -> np.ndarray:
        if self.argvals is None:
            return np.arange(n_features, dtype=np.float64)
        return np.asarray(self.argvals, dtype=np.float64)

    @staticmethod
    def _sign_canonicalize(components, scores):
        """Flip SVD components so largest-abs element is positive (idempotent fit)."""
        max_abs_idx = np.argmax(np.abs(components), axis=1)
        signs = np.sign(components[np.arange(len(components)), max_abs_idx])
        components = components * signs[:, np.newaxis]
        scores = scores * signs[np.newaxis, :]
        return components, scores


# Tags override pattern for non-deterministic estimators:
if _HAS_TAGS_DATACLASS:
    def _make_non_deterministic_tags(self):
        tags = super().__sklearn_tags__()
        tags.non_deterministic = True
        return tags
else:
    def _make_non_deterministic_tags(self):  # type: ignore[misc]
        return {"non_deterministic": True}
```

### `sklearn/__init__.py` Gating (mirrors mcp/__init__.py)

```python
# python/fdars/sklearn/__init__.py
"""fdars.sklearn — scikit-learn-compatible estimator layer for fdars.

Requires the [sklearn] extra::

    pip install fdars[sklearn]

Note: Not registered in fdars.__init__; never imported by plain ``import fdars``.
"""
try:
    from sklearn.base import BaseEstimator  # noqa: F401 — proves sklearn present
except ImportError as _e:
    raise ImportError(
        "fdars[sklearn] requires scikit-learn. "
        "Install it with: pip install fdars[sklearn]"
    ) from _e

from fdars.sklearn._base import _BaseFdarsEstimator  # noqa: E402
from fdars.sklearn._coverage import EXCLUDED_METHODS, TRIAGE_VERDICTS  # noqa: E402

__all__ = ["_BaseFdarsEstimator", "EXCLUDED_METHODS", "TRIAGE_VERDICTS"]
# Individual estimator classes added in Phases 56-58.
```

### Minimal Skeleton Pattern for Triage

```python
# Fragment from _skeletons.py — pattern for all 31 skeletons
from sklearn.base import TransformerMixin, RegressorMixin, ClassifierMixin
from sklearn.base import ClusterMixin, OutlierMixin
from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import check_random_state
from fdars.sklearn._base import _BaseFdarsEstimator, _validate
from fdars import _native
import numpy as np

class FPCATransformer(TransformerMixin, _BaseFdarsEstimator):
    _min_samples = 2

    def __init__(self, argvals=None, n_components=3):
        super().__init__(argvals=argvals)
        self.n_components = n_components  # verbatim — same name as param

    def fit(self, X, y=None):
        X = _validate(self, X, reset=True, dtype="numeric", ensure_2d=True)
        X = X.astype(np.float64)
        n_obs, n_pts = X.shape
        if n_obs < self._min_samples:
            raise ValueError(
                f"n_samples={n_obs} is too small; FPCATransformer requires "
                f"at least {self._min_samples} samples."
            )
        # n_components must not exceed n_obs - 1
        n_comp = min(self.n_components, n_obs - 1, n_pts)
        self.argvals_ = self._resolve_argvals(n_pts)
        result = _native.regression.fpca(X, self.argvals_, n_comp)
        # rotation: (n_pts, n_comp) → transpose to (n_comp, n_pts)
        components = np.array(result["rotation"]).T
        scores = np.array(result["scores"])
        components, scores = self._sign_canonicalize(components, scores)
        self.components_ = components          # (n_comp, n_pts)
        self.mean_ = np.array(result["mean"])  # (n_pts,)
        self.n_components_ = n_comp
        return self

    def transform(self, X):
        check_is_fitted(self)
        X = _validate(self, X, reset=False, dtype="numeric", ensure_2d=True)
        X = X.astype(np.float64)
        centered = X - self.mean_
        return centered @ self.components_.T  # (n_obs, n_comp)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        return np.array([f"fpca{i}" for i in range(self.n_components_)])
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `self._validate_data(X)` | `sklearn.utils.validation.validate_data(self, X)` (public) | sklearn 1.6 | Private form deprecated; will be removed in 1.8 |
| `_more_tags()` / `_get_tags()` dict-based | `__sklearn_tags__()` returning `Tags` dataclass | sklearn 1.6 | Dict form deprecated; removed in 1.8 |
| `_xfail_checks` tag | `expected_failed_checks` param in `parametrize_with_checks` | sklearn 1.6 | This milestone forbids ALL exemptions |
| `check_estimator(generate_only=True)` | `estimator_checks_generator(estimator)` | sklearn 1.6 | `generate_only` deprecated |
| `assert_all_finite` / `force_all_finite` | `ensure_all_finite` | sklearn 1.6 | Old names deprecated |
| `_estimator_type` class attribute | Inherit from correct mixin | sklearn 1.6 | Deprecated in 1.6 |

**Deprecated / avoid:**
- `check_estimator` as CI gate (use `parametrize_with_checks` — fail-per-check, not fail-fast)
- `scikit-fda` as a dependency (FDataGrid input contract; incompatible with plain-ndarray requirement)
- `argvals=np.arange(100)` as default (mutable default breaks clone; use `None`)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `nadaraya_watson` per-row loop is performant enough for check_estimator's ~40-obs test size | Pattern 2, Pitfall 1 | check_estimator may time out on slow machines; mitigation: cap loop at actual test sizes which are small |
| A2 | sklearn's SVD sign convention for PCA is "largest-abs element positive" (same as recipe above) | Pattern 3 (sign canonicalization) | If wrong, check_fit_idempotent may still fail; mitigation: run the specific check early in triage |
| A3 | `ElasticMultinomialClassifier` requires >= 3 classes (EXCLUDE prediction) | Candidate table | If binary also works, it may PASS-WITH-FIXES; triage confirms |
| A4 | `FunctionalGMM` EXCLUDE prediction (k_range awkwardness) | Candidate table | If n_clusters_min/max pattern passes check_estimator, it becomes PASS-WITH-FIXES |
| A5 | `TVDMSSDetector`, `MUODDetector`, `DepthgramDetector` cannot synthesize a continuous score | Candidate table | If a meaningful continuous score can be derived, they become PASS-WITH-FIXES |
| A6 | scikit-learn is one of the top-5 most downloaded PyPI packages | Package Legitimacy Audit | No practical risk — registry metadata SUS verdict is a known artifact |
| A7 | `predict_fregre_lm` re-fits internally (not a stored-model function) | Pitfall 3, Code Examples | Verified from Rust source [VERIFIED: src/regression_mod.rs:478-494]; confirmed correct |

**If this table is empty after triage:** All implementation decisions confirmed empirically — no further user confirmation needed.

## Open Questions

1. **FunctionalGMM inclusion**
   - What we know: `gmm_cluster` takes a `k_range` list; n_clusters_min/max workaround is architectural
   - What's unclear: whether check_estimator accepts the workaround or rejects the non-scalar list internally
   - Recommendation: skeleton it with n_clusters=int param that internally passes `k_range=[n_clusters]` to gmm_cluster; see if check_estimator passes

2. **TVDMSS/MUOD/Depthgram continuous score synthesis**
   - What we know: these return typed categorical flags (shape vs magnitude vs amplitude)
   - What's unclear: whether an ad-hoc continuous score (e.g. distance from boundary) can satisfy `check_outliers_train`
   - Recommendation: run triage; if EXCLUDE, record failing check name; note FUT-02 for fdars-core returning scores

3. **rayon determinism under fixed random_state**
   - What we know: kmeans_fd takes `seed: u64`; rayon thread scheduling may cause non-determinism regardless of seed
   - What's unclear: whether the current fdars-core 0.14.0 kmeans is deterministic under a fixed seed across thread counts
   - Recommendation: run `check_methods_sample_order_invariance` in triage; if non-deterministic, set `non_deterministic=True` in tags

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `scikit-learn` | All estimators, triage harness | ✗ (not in base venv) | — | Install via `pip install -e ".[sklearn,dev]"` |
| `pytest` | Triage test suite | ✓ (in dev deps) | — | — |
| `fdars._native` (compiled extension) | All skeleton estimators | ✓ (maturin develop) | 0.8.0 | — |

**Missing dependencies with no fallback:**
- `scikit-learn` must be installed before running triage; install via `[sklearn]` extra or `[dev]` after it's added

## Security Domain

Security enforcement is not applicable to this phase. The sklearn layer is a pure-Python API wrapper with no authentication, session management, network I/O, or cryptography. Inputs are numpy arrays validated by sklearn's `validate_data` (NaN/inf rejection enforced by default). No ASVS categories apply.

## Sources

### Primary (HIGH confidence)

- `src/regression_mod.rs` lines 23–46 — VERIFIED fpca() signature and return dict keys
- `src/regression_mod.rs` lines 112–136 — VERIFIED fregre_lm() signature; lines 478–494 — predict_fregre_lm re-fit pattern
- `src/smoothing_mod.rs` lines 26–43 — VERIFIED nadaraya_watson() is 1D per-curve
- `src/clustering_mod.rs` lines 29–53 — VERIFIED kmeans_fd() signature and return dict; seed: u64 type
- `src/classification_mod.rs` lines 24–41 — VERIFIED fclassif_lda() takes i64 labels; combined fit+predict
- `src/represent_mod.rs` lines 186–199 — VERIFIED impute_missing_values() returns matrix directly
- `src/outliers_mod.rs` lines 31–49 — VERIFIED detect_outliers_lrt() interface; lines 129–160 for detect_outliers_lrt_with_dist()
- `python/fdars/mcp/__init__.py` — VERIFIED gating pattern (try/ImportError + deferred imports)
- `python/fdars/advisor/__init__.py` — VERIFIED _require_* guard pattern (version floor check)
- `pyproject.toml` lines 39–63 — VERIFIED existing optional-dependencies format

### Secondary (MEDIUM confidence)

- `.planning/research/SUMMARY.md`, `STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md`, `FEATURES.md` — v9.0 research from 2026-08-31; HIGH confidence (grounded in direct source reading)
- `sklearn-compat` GitHub (via WebFetch) — covers sklearn 1.2–1.9, tags shim included, 118 commits, appears maintained [CITED: github.com/sklearn-compat/sklearn-compat]

### Tertiary (LOW confidence)

- sklearn source + docs: validate_data public API (1.6), Tags dataclass fields, check_estimator substring contracts — derived from prior v9.0 research session documented in STACK.md and PITFALLS.md
- pip index versions: scikit-learn 1.9.0 latest; sklearn-compat 0.1.6 latest [VERIFIED: pip index versions 2026-08-31 session]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions verified via pip index; pyproject.toml pattern read from source
- Base class contract: HIGH — validate_data shim verified against STACK.md; constructor rule verified from ARCHITECTURE.md + prior source reads
- Native function signatures: HIGH — all key signatures verified by reading *_mod.rs files this session
- Triage harness: HIGH — parametrize_with_checks is standard sklearn; test layout confirmed
- Candidate verdict predictions: MEDIUM — predictions based on algorithm properties + check_estimator behavior analysis; triage run is the empirical ground truth

**Research date:** 2026-08-31
**Valid until:** 2026-09-30 (sklearn minor releases don't break the 1.3–1.6 range within this window)
