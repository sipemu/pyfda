# Stack Research — v9.0 scikit-learn API Compatibility

**Domain:** scikit-learn-compatible estimator layer over a PyO3/Rust functional-data library (pure Python)
**Researched:** 2026-08-31
**Confidence:** MEDIUM (sklearn version facts verified via official docs and release notes; behavioral details from developer guide and parametrize_with_checks docs)

> **Scope:** This document covers ONLY the stack additions and choices needed for v9.0. The baseline stack (PyO3 0.28, numpy 0.28, fdars-core 0.23.0, pydantic, anthropic, mcp, pytest) is already validated and is not re-researched here.

---

## Decision Summary

1. **`scikit-learn>=1.3,<1.7`** is the correct `[sklearn]` extra pin. sklearn 1.6 is the last release to support Python 3.9; 1.7 requires Python 3.10+. The ABI3-py39 guarantee and the existing 3.9–3.14 CI matrix make `<1.7` a hard upper bound.
2. **`sklearn-compat`** (optional, dev-time or vendored) smooths the `validate_data`/`__sklearn_tags__` API differences across 1.3–1.6. It is not a mandatory runtime dep — the estimator code can use a small try/import guard instead — but it removes fragile version-detection logic.
3. **`parametrize_with_checks`** (from `sklearn.utils.estimator_checks`, already inside scikit-learn) is the CI compliance gate. No additional pytest plugin is needed.
4. **scikit-fda** is a design reference only, not a dependency. Its `FDataGrid`-based input contract is incompatible with the plain-ndarray requirement of this milestone.
5. **No new runtime deps** beyond `scikit-learn` itself are required. All other tooling is already present.

---

## Recommended Stack

### Core Technologies

| Technology | Version Constraint | Purpose | Why |
|------------|-------------------|---------|-----|
| `scikit-learn` | `>=1.3,<1.7` | Base classes (`BaseEstimator`, `TransformerMixin`, etc.), compliance test harness | 1.6 is the last release supporting Python 3.9 (1.7 requires 3.10+). Lower bound 1.3 covers `n_features_in_` (SLEP010, present since 1.0), `set_output` API (1.2+), and `feature_names_in_` (1.0+). Users on 3.10+ who need sklearn ≥1.7 features can install it separately — the estimator code remains compatible. |
| `numpy` | (already a base dep) | Array input/output for all estimators | Already present. Estimators operate on `(n_obs, n_points)` float64 ndarrays. No pin change needed. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `sklearn-compat` | `>=0.1` | Cross-version shim for `validate_data`, `get_tags`, and `parametrize_with_checks` `expected_failed_checks` across sklearn 1.2–1.6+ | Use in estimator implementation files if the codebase needs to call both `self._validate_data` (pre-1.6) and `sklearn.utils.validation.validate_data` (1.6+). Maintained alongside sklearn releases; zero transitive deps beyond sklearn itself. Can be vendored if preferred. |
| `pytest` | (already in `[dev]`) | Test runner for `parametrize_with_checks` compliance gate | Already in `[dev]` extra. No change needed. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `parametrize_with_checks` | Pytest-parametrized compliance gate — one test per (estimator, check) pair | Import from `sklearn.utils.estimator_checks`. Preferred over `check_estimator` in CI because it surfaces each check as a named test case, supports `pytest -k` filtering, and fails fast per check. |
| `check_estimator` | One-shot inline validation during development | Use interactively with `on_fail="warn"` to see all failures for a single estimator at once. Do not use as the CI gate — `parametrize_with_checks` is better for that. |

---

## pyproject.toml Integration

### The `[sklearn]` extra

```toml
[project.optional-dependencies]
# Note: [sklearn] pins scikit-learn<1.7 to support Python 3.9.
# sklearn 1.7 requires Python>=3.10 (dropped 3.9 support).
# On Python 3.10+, users may install scikit-learn>=1.7 separately;
# the estimator layer is compatible with both ranges.
sklearn = ["scikit-learn>=1.3,<1.7"]
```

This follows the exact same pattern already established for `[mcp]` (which has a matching Python 3.10+ comment). Users on Python 3.10+ who manually install `scikit-learn>=1.7` will find the estimators still work — the `<1.7` upper bound is a packaging floor for the extra, not a hard runtime cap.

### Dev extra update

```toml
dev = ["pytest", "pytest-asyncio", "pyyaml", "matplotlib>=3.6", "scikit-learn>=1.3,<1.7"]
```

Adding `scikit-learn` to `[dev]` ensures the compliance tests run in the development environment without separately installing `[sklearn]`.

---

## Version-Specific API Changes to Handle

### Critical: validate_data vs _validate_data

| sklearn version | API |
|----------------|-----|
| 1.3–1.5 | `self._validate_data(X, ...)` (private, still present) |
| 1.6 | `sklearn.utils.validation.validate_data(self, X, ...)` (public) — `_validate_data` will be removed in a future release |

`validate_data` automatically sets `n_features_in_` and `feature_names_in_` on `reset=True` (called in `fit`) and validates against them on `reset=False` (called in `transform`/`predict`).

**Recommended approach:** Use a one-time module-level try/import guard in `python/fdars/sklearn/_base.py`:

```python
try:
    from sklearn.utils.validation import validate_data as _sklearn_validate_data
    def _validate(estimator, X, **kwargs):
        return _sklearn_validate_data(estimator, X, **kwargs)
except ImportError:
    def _validate(estimator, X, **kwargs):
        return estimator._validate_data(X, **kwargs)
```

All estimators call `_validate(self, X, ...)` instead of calling either form directly. This is the same pattern `sklearn-compat` provides if preferred.

### Critical: Tags API — __sklearn_tags__ vs _more_tags

| sklearn version | Tag mechanism |
|----------------|--------------|
| 1.3–1.5 | `_more_tags()` / `_get_tags()` dict-based |
| 1.6 | `__sklearn_tags__()` returning `sklearn.utils.Tags` dataclass; old `_more_tags`/`_get_tags`/`_safe_tags` raise `DeprecationWarning` |
| 1.6 | `_xfail_checks` tag removed; use `expected_failed_checks` in `parametrize_with_checks` |
| 1.6 | `_estimator_type` attribute deprecated; use mixins or Tags instead |

**Recommended approach:** Inherit from `BaseEstimator` (provides `__sklearn_tags__` from 1.6; `_more_tags` from 1.3–1.5). Do NOT implement `_more_tags` in custom estimators — it warns on 1.6. Use `__sklearn_tags__` for genuine capability flags only:

```python
def __sklearn_tags__(self):
    tags = super().__sklearn_tags__()
    # example: mark as non-deterministic if fdars method uses random init
    # tags.non_deterministic = True
    return tags
```

For reading tags portably, use `sklearn-compat`'s `get_tags()` or guard with a version check.

### Important: check_estimator / parametrize_with_checks API changes

| Feature | 1.3–1.5 | 1.6 |
|---------|---------|-----|
| `generate_only=True` | Supported | Deprecated; use `estimator_checks_generator(estimator)` |
| `expected_failed_checks` param | Not present | Added to `parametrize_with_checks` |
| `_xfail_checks` tag | Works | Removed |
| `on_skip`, `on_fail`, `callback` | Not present | Added to `check_estimator` |
| `legacy` param | Not present | Added to both functions |

**This milestone forbids exemptions.** Therefore `expected_failed_checks` will not be used. The compliance test file targets the 1.3+ API subset that works without deprecation warnings:

```python
@parametrize_with_checks([MyEstimator()])
def test_sklearn_compliance(estimator, check):
    check(estimator)
```

### Minor: set_output API (TransformerMixin, sklearn 1.2+)

`set_output(transform="pandas")` is available since sklearn 1.2 (already within our `>=1.3` bound). `TransformerMixin` auto-wraps `transform` and `fit_transform` to honour it if `get_feature_names_out()` is defined. For functional transformers that change the feature dimension (e.g., FPCA: n_points → n_components), implement `get_feature_names_out()` returning `np.arange(self.n_components_)` so that `Pipeline(...).set_output(transform="pandas")` works correctly.

---

## Compliance Test Harness

### Structure

```
tests/
  sklearn/
    test_compliance.py   # parametrize_with_checks gate
    conftest.py          # [sklearn] guard: skip if sklearn not installed
```

```python
# tests/sklearn/conftest.py
import pytest
sklearn = pytest.importorskip("sklearn", reason="[sklearn] extra not installed")
```

```python
# tests/sklearn/test_compliance.py
from sklearn.utils.estimator_checks import parametrize_with_checks
from fdars.sklearn import (
    FunctionalSmoother,
    FPCATransformer,
    FunctionalDepthTransformer,
    FunctionalRegressor,
    FunctionalClassifier,
    FunctionalClusterer,
    FunctionalOutlierDetector,
    # all wrapped estimators...
)

@parametrize_with_checks([
    FunctionalSmoother(),
    FPCATransformer(n_components=1),
    FunctionalDepthTransformer(),
    FunctionalRegressor(),
    FunctionalClassifier(),
    FunctionalClusterer(n_clusters=2),
    FunctionalOutlierDetector(),
])
def test_sklearn_compliance(estimator, check):
    check(estimator)
```

### CI integration

Add a separate CI job:

```yaml
# .github/workflows/sklearn-compliance.yml
- name: Install sklearn extra
  run: pip install -e ".[sklearn,dev]"
- name: Run compliance gate
  run: pytest tests/sklearn/ -v --tb=short
```

This keeps the compliance gate separate from the main test suite, which must remain sklearn-free for the base package.

### Why parametrize_with_checks over check_estimator

- Each check appears as a named pytest test case, enabling `pytest -k check_n_features_in` to debug a specific failure.
- `check_estimator` stops on the first failure; `parametrize_with_checks` continues, revealing the full failure set in one CI run.
- Integrates naturally with `--tb=short -x` for fail-fast and with `--tb=long` for full traces.
- The test IDs are human-readable (estimator class name + check name), making CI reports navigable.

---

## Mixin Contract Cheatsheet

Each estimator type has mandatory attributes and methods verified by `check_estimator`:

| Mixin | Must implement | Attributes set in fit | Key check_estimator checks |
|-------|---------------|----------------------|---------------------------|
| `TransformerMixin` | `fit(X, y=None)→self`, `transform(X)→array` | `n_features_in_`, trailing-`_` learned params | dtype preservation (float32 in → float32 out), sample count invariance (rows unchanged), `set_output` compat |
| `RegressorMixin` | `fit(X, y)→self`, `predict(X)→1-D array` | `n_features_in_`, learned params | float output, shape `(n_samples,)`, MSE-compatible |
| `ClassifierMixin` | `fit(X, y)→self`, `predict(X)→array`, `predict_proba` optional | `classes_`, `n_features_in_` | integer labels, binary minimum, no NaN output |
| `ClusterMixin` | `fit(X, y=None)→self` | `labels_` (int ndarray, shape `(n_samples,)`) | `fit_predict` provided by mixin; no `predict` required; labels_ non-negative for inliers |
| `OutlierMixin` | `fit(X, y=None)→self`, `score_samples(X)→array` | `offset_`, `n_features_in_` | `decision_function` derived from `score_samples`; `predict` returns `{+1, -1}` |

**`argvals` constructor parameter:** Because it is a constructor param (not passed to `fit`), `clone()` preserves it correctly via `get_params()`/`set_params()`. Do NOT set `argvals` as a fitted attribute (no trailing `_`). It is a hyper-parameter with default `np.arange(n_features)`, resolved in `fit()` if not supplied. The check_estimator `check_parameters_default_constructible` and `check_get_params_invariance` checks will verify this round-trips correctly.

---

## Hardest check_estimator Checks for Functional Data

These checks are most likely to require fdars method exclusions from the sklearn layer:

| Check | Why hard for FDA estimators | Mitigation |
|-------|---------------------------|-----------|
| `check_estimators_dtypes` | Tests float32 passthrough; fdars Rust layer operates on float64 | Accept float32; cast to float64 before calling fdars in `fit`/`transform`; return float64. The check verifies the output dtype is preserved — float64 in → float64 out passes; float32 in → float64 out fails. Use `X = X.astype(np.float64)` after `validate_data`. |
| `check_n_features_in` | Validates estimator raises on wrong feature count at transform/predict time | Call `validate_data(self, X, reset=False)` in `transform`/`predict`. Auto-handled — do not skip. |
| `check_estimators_nan_inf` | NaN/inf input must raise `ValueError` | Do not set `allow_nan=True` in tags; `validate_data` enforces by default. |
| `check_pipeline_consistency` | Cloned estimator in pipeline must produce identical result | Ensure `argvals` round-trips through `get_params`/`set_params` without mutation. Keep `argvals` as constructor param only. |
| `check_methods_subset_invariance` | Same rows in different order → same result | Problematic for order-sensitive algorithms. Registration/alignment methods that depend on sample ordering must be excluded. |
| `check_n_samples_minimum` (clustering) | Checks run with as few as 2 samples | FPCA with `n_components` > n_samples fails in fdars-core. Default `n_components=1`; guard: `n_components = min(self.n_components, n_samples - 1)` in `fit()`. |
| `check_fit_score_takes_y` (clusterers) | `fit` must accept `y` even if unused | Accept `y=None` in `fit` signature; silently ignore it. |
| `check_estimators_pickle` | Estimator must be picklable before and after fit | Pure Python + numpy attributes → picklable by default. Do not store live fdars handles in fitted attributes. |

### Methods that cannot comply and must be excluded

These remain in the existing functional API. They are recorded in the v9.0 coverage list as excluded-by-design:

| fdars method | Reason for exclusion |
|-------------|---------------------|
| `least_squares_shift_registration`, elastic alignment | Order-sensitive; `check_methods_subset_invariance` will fail. No deterministic result for permuted samples. |
| `pace_fpca` | Requires `IrregFdata` sparse/irregular input — not a `(n_obs, n_points)` ndarray. Fundamentally incompatible with the ndarray contract. |
| `functional_glm` | Requires a pre-fitted FPCA basis handle as input — not a standalone fit/predict cycle compatible with sklearn. |
| `t_perm_test`, `f_perm_test`, `oneway_anova_vstat`, SCB bands | Hypothesis tests, not estimators. No natural fit/transform structure. |
| SPM monitoring functions | Stateful streaming pattern (update-per-observation). Cannot be cast to batch fit/transform. |
| `itp_one_pop`, `itp_two_pop`, `itp_flm` | Interval-wise tests returning p-curve arrays — not a predict output shape sklearn understands. |

---

## scikit-fda: Dependency vs Design Reference

**Decision: design reference only, NOT a dependency.**

Rationale:
- scikit-fda uses `FDataGrid` as its estimator input type, which bypasses sklearn's `check_estimator` array validation. fdars' milestone constraint is the opposite: estimators must accept plain `(n_obs, n_points)` ndarrays and pass the full battery without any array-bypass.
- scikit-fda's Pipeline examples and `FPCA` class structure are instructive for the API shape — parameter naming, `get_feature_names_out()` implementation, `fit_transform` patterns — but the implementation cannot be reused because the input contract differs.
- Adding scikit-fda as a dependency pulls in 8+ transitive dependencies and its own array-conversion layer, creating a conflict with the fdars Rust data path.

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| `scikit-learn>=1.3,<1.7` | `>=1.3` (no upper cap) | sklearn 1.7 drops Python 3.9; the `[sklearn]` extra would silently become unusable on 3.9 if 1.7 is resolved |
| `scikit-learn>=1.3,<1.7` | `>=1.6,<1.7` | Excludes users on 1.3–1.5 who have sklearn pinned (common in older conda/pyenv setups); the extra compat work is small |
| `parametrize_with_checks` | `check_estimator` in a loop | `check_estimator` aborts on first failure; `parametrize_with_checks` surfaces all failures independently — essential for iterative compliance work |
| `sklearn-compat` shim (optional) | Hand-rolled `if sklearn.__version__ >= "1.6"` guards | Version-detection logic in third-party libraries is fragile across patch releases; `sklearn-compat` is maintained by the same community |
| Exclude non-compliant methods | `expected_failed_checks` exemptions | Milestone constraint explicitly forbids exemptions. Any method requiring an exemption is excluded from the sklearn layer, not exempted. |
| scikit-fda as design reference only | scikit-fda as runtime dep | Different input contract; transitive deps conflict; adds maintenance burden without benefit |

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `scikit-learn>=1.7` in `[sklearn]` extra | Drops Python 3.9 users silently | `<1.7` upper bound |
| `scikit-fda` as runtime dep | FDataGrid input contract incompatible with ndarray requirement; 8+ transitive deps | Use as design reference for API shape only |
| `sktime`, `tslearn` | Time-series-oriented wrappers with different domain models and dependencies | Implement directly on sklearn base classes |
| `_validate_data` (private sklearn method) | Deprecated in sklearn 1.6, scheduled for removal | `sklearn.utils.validation.validate_data` (1.6+) or try/import guard |
| `_more_tags()` / `_get_tags()` | Raise `DeprecationWarning` in 1.6 | `__sklearn_tags__()` from `BaseEstimator` |
| `_xfail_checks` tag | Removed in sklearn 1.6 | `expected_failed_checks` in `parametrize_with_checks` (but milestone forbids exemptions) |
| `generate_only=True` in `check_estimator` | Deprecated in sklearn 1.6 | `estimator_checks_generator(estimator)` |
| `_estimator_type` attribute directly | Deprecated in sklearn 1.6 | Inherit from correct mixin (`ClassifierMixin`, `RegressorMixin`, etc.) |
| Custom `__reduce__` or pickle logic | Unnecessary complexity | Pure Python + numpy attributes pickle by default |

---

## Installation

```bash
# Install fdars with the sklearn extra
pip install fdars[sklearn]

# Dev environment (adds pytest, sklearn, matplotlib)
pip install -e ".[sklearn,dev]"

# Run the compliance gate
pytest tests/sklearn/ -v --tb=short

# Debug a single check interactively
python -c "
from sklearn.utils.estimator_checks import check_estimator
from fdars.sklearn import FPCATransformer
check_estimator(FPCATransformer(n_components=1), on_fail='warn')
"
```

---

## Version Compatibility Matrix

| Package | Constraint | Python | Notes |
|---------|-----------|--------|-------|
| `scikit-learn` | `>=1.3,<1.7` | 3.9–3.14 | 1.6 supports 3.9–3.13; 1.7 would require 3.10+. Upper bound protects 3.9. |
| `numpy` | (base dep, any) | 3.9–3.14 | Already present; estimators consume/return numpy arrays; no new constraint |
| `pandas` | (base dep, any) | 3.9–3.14 | Already present; `set_output("pandas")` works with sklearn 1.2+ |
| `sklearn-compat` | `>=0.1` | 3.9+ | Supports sklearn 1.2+ per SPEC0; optional/dev-only use |
| `pytest` | (dev dep, any) | 3.9–3.14 | Already in `[dev]`; `parametrize_with_checks` requires no extra pytest plugins |

---

## Sources

- [scikit-learn install page](https://scikit-learn.org/stable/install.html) — Python version support matrix per release (1.3–1.7); confirmed 1.6 is last with Python 3.9 support (LOW confidence / official page, verified)
- [scikit-learn v1.6 release notes](https://scikit-learn.org/stable/whats_new/v1.6.html) — `__sklearn_tags__`, `validate_data` public API, `parametrize_with_checks` `expected_failed_checks`, `generate_only` deprecation, PyPy support dropped (LOW confidence / official changelog)
- [scikit-learn developer guide](https://scikit-learn.org/stable/developers/develop.html) — BaseEstimator contract, `validate_data` usage, `check_is_fitted`, Tags, mixin requirements (LOW confidence / official docs)
- [parametrize_with_checks docs](https://scikit-learn.org/stable/modules/generated/sklearn.utils.estimator_checks.parametrize_with_checks.html) — full signature, `expected_failed_checks` parameter, version history (LOW confidence / official docs)
- [check_estimator docs](https://scikit-learn.org/stable/modules/generated/sklearn.utils.estimator_checks.check_estimator.html) — `on_skip`/`on_fail`/`callback` parameters, check categories (LOW confidence / official docs)
- [sklearn-compat docs](https://sklearn-compat.readthedocs.io/) — cross-version utility wrapper, supported sklearn range (1.2+), SPEC0 policy (LOW confidence / project docs)
- [scikit-fda sklearn tutorial](https://fda.readthedocs.io/en/stable/auto_tutorial/plot_skfda_sklearn.html) — design reference for FDA + sklearn integration patterns (LOW confidence / project docs)
- [sklearn v1.7 release highlights](https://scikit-learn.org/stable/auto_examples/release_highlights/plot_release_highlights_1_7_0.html) — Python 3.10+ requirement confirmed (LOW confidence / official docs)

---

*Stack research for: fdars v9.0 — scikit-learn API Compatibility estimator layer*
*Researched: 2026-08-31*
