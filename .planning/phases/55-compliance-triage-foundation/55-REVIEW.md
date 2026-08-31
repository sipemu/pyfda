---
phase: 55-compliance-triage-foundation
reviewed: 2026-08-31T18:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - python/fdars/sklearn/__init__.py
  - python/fdars/sklearn/_base.py
  - python/fdars/sklearn/_coverage.py
  - python/fdars/sklearn/_skeletons.py
  - pyproject.toml
  - tests/sklearn/conftest.py
  - tests/sklearn/test_foundation.py
  - tests/sklearn/test_triage.py
  - tests/sklearn/test_coverage.py
  - tests/sklearn/test_go_no_go.py
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: fixes_applied
---

# Phase 55: Code Review Report

**Reviewed:** 2026-08-31T18:00:00Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Phase 55 ships the fdars sklearn layer foundation: gating (`__init__.py`), the base class and compat shims (`_base.py`), the coverage/triage registries (`_coverage.py`), and 28 skeleton estimators (`_skeletons.py`). Per the review brief, skeleton limitations that are tracked as PASS-WITH-FIXES (re-fit at predict, missing `decision_function`, missing `n_iter_`) are not flagged.

The declared support range is sklearn 1.3 through 1.8. One critical bug exists: `Imputer.__sklearn_tags__` is defined unconditionally and calls `super().__sklearn_tags__()`, which crashes on sklearn 1.3-1.5 where that method does not exist on `BaseEstimator`. The rest of the production-quality code (`_BaseFdarsEstimator`, the validate-data shim, clone contract, sign canonicalization) is correct.

Four warnings cover: the `_sign_canonicalize` all-zeros corner case, double-validation in outlier detectors' predict chain, duplication of `_pairwise_l2` across four classes, and a test reliability gap. Three info items address minor code quality points.

---

## Critical Issues

### CR-01: `Imputer.__sklearn_tags__` crashes on sklearn 1.3-1.5

**File:** `python/fdars/sklearn/_skeletons.py:546-549`

**Issue:** `Imputer` defines `__sklearn_tags__` unconditionally and calls `super().__sklearn_tags__()`. On sklearn 1.3-1.5, `BaseEstimator` does not have a `__sklearn_tags__` method — the tags API was introduced in 1.6. `_BaseFdarsEstimator` correctly guards with `_HAS_TAGS_DATACLASS` and only defines `__sklearn_tags__` when the Tags dataclass is available (lines 223-228 in `_base.py`). `Imputer` bypasses this guard, so any code path that calls `Imputer().__sklearn_tags__()` (including sklearn's own `check_estimator` battery when `_HAS_TAGS_DATACLASS=False`) raises `AttributeError: 'super' object has no attribute '__sklearn_tags__'`.

The supported range in `pyproject.toml` is `scikit-learn>=1.3`, meaning the package explicitly claims to support 1.3-1.5. This breaks the `Imputer` estimator on those versions.

**Fix:** Guard `Imputer.__sklearn_tags__` with `_HAS_TAGS_DATACLASS`, mirroring the pattern in `_BaseFdarsEstimator`. For the old-tags path, set `allow_nan` via `_more_tags()`:

```python
# In Imputer class body:
if _HAS_TAGS_DATACLASS:
    def __sklearn_tags__(self):
        """Override tags to declare NaN input is allowed (sklearn 1.6+)."""
        tags = super().__sklearn_tags__()
        tags.input_tags.allow_nan = True
        return tags
else:
    def _more_tags(self):  # type: ignore[override]
        """Override tags to declare NaN input is allowed (sklearn 1.3-1.5)."""
        return {"allow_nan": True}
```

This requires `_HAS_TAGS_DATACLASS` to be imported in `_skeletons.py` from `_base.py`. It is already imported via `from fdars.sklearn._base import _BaseFdarsEstimator, _validate`, so add it to that import line:

```python
from fdars.sklearn._base import _BaseFdarsEstimator, _validate, _HAS_TAGS_DATACLASS
```

---

## Warnings

### WR-01: `_sign_canonicalize` produces zero-vector components when a row is all-zero

**File:** `python/fdars/sklearn/_base.py:213-217`

**Issue:** `np.sign(0.0)` returns `0.0`. If any FPCA component row is numerically all-zero (degenerate decomposition from a rank-deficient input), `signs[k] = 0.0` and the multiplication `components * signs[:, np.newaxis]` zeroes out that entire component row. The corresponding score column is also zeroed. This silently corrupts the output without raising an error. The check `check_fit_idempotent` would pass (zero * zero = zero is stable), but downstream consumers would receive meaningless zero components.

This cannot happen from a mathematically correct SVD (orthonormal components have unit norm), but can happen if the native `fpca` function returns a degenerate result on near-zero or constant input.

**Fix:** Add a fallback: when `sign == 0`, keep the component unflipped (sign → 1):

```python
signs = np.sign(components[np.arange(len(components)), max_abs_idx])
signs = np.where(signs == 0, 1.0, signs)  # keep unflipped if all-zero component
components = components * signs[:, np.newaxis]
scores = scores * signs[np.newaxis, :]
```

---

### WR-02: Double-validation in `_BaseFdarsOutlierDetector.predict`

**File:** `python/fdars/sklearn/_skeletons.py:1878-1894`

**Issue:** `_BaseFdarsOutlierDetector.predict` validates `X` (line 1891) and then calls `self.score_samples(X)` passing the already-validated float64 ndarray. Every concrete `score_samples` implementation (e.g., `OutliergramDetector.score_samples` at line 2068, `MagnitudeShapeDetector.score_samples` at line 2138, `TVDMSSDetector.score_samples` at line 2227, `MUODDetector.score_samples` at line 2310, `DepthgramDetector.score_samples` at line 2394) validates `X` again with `_validate(self, X, reset=False, ...)` and calls `.astype(np.float64)`. This means `validate_data` is called twice with `reset=False` and a dtype cast is applied to an already-float64 array.

The second call is harmless in the current sklearn implementation since `validate_data(reset=False)` is idempotent on a valid ndarray, but the pattern is incorrect: `predict` should either validate and pass raw data to a private `_score_samples_unsafe` method, or not validate at all and rely on `score_samples` doing it (since `score_samples` is itself a public API endpoint that users may call directly).

**Fix:** Remove the duplicate validation/cast from `predict` and let `score_samples` be the single validation point, since `score_samples` is also a public method:

```python
def predict(self, X):
    check_is_fitted(self)
    scores = self.score_samples(X)  # score_samples handles validation internally
    return np.where(scores >= 0, 1, -1).astype(np.int64)
```

---

### WR-03: `_pairwise_l2` duplicated in four unrelated classes

**File:** `python/fdars/sklearn/_skeletons.py:1173, 1648, 1744, 1853`

**Issue:** The identical `_pairwise_l2` static method (computing pairwise L2 distances via the `||a-b||^2 = ||a||^2 + ||b||^2 - 2a·bᵀ` identity, with `np.maximum(..., 0)` clamp) is copied verbatim four times:
- `NonparametricRegressor._pairwise_l2` (line 1173)
- `FunctionalKMeans._pairwise_l2` (line 1648)
- `FuzzyFunctionalCMeans._pairwise_l2` (line 1744)
- `FunctionalGMM._pairwise_l2` (line 1853)

Code duplication means any future fix (e.g., numerical stability improvement) must be applied in four places. A bug introduced in one copy silently does not propagate to others.

**Fix:** Extract to a module-level function in `_skeletons.py`, above the class definitions:

```python
def _pairwise_l2(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute pairwise L2 distances between rows of A and rows of B."""
    a2 = np.sum(A ** 2, axis=1, keepdims=True)
    b2 = np.sum(B ** 2, axis=1, keepdims=True)
    dist2 = a2 + b2.T - 2.0 * (A @ B.T)
    return np.sqrt(np.maximum(dist2, 0.0))
```

Each class then calls the module-level function directly.

---

### WR-04: `test_fdars_init_unchanged` cannot detect committed modifications

**File:** `tests/sklearn/test_foundation.py:56-68`

**Issue:** The test runs `git diff --quiet -- python/fdars/__init__.py` to verify Phase 55 did not modify `python/fdars/__init__.py`. `git diff` without a ref compares the working tree to the index (staged area). If Phase 55 committed a change to `python/fdars/__init__.py`, the working tree and index would both reflect the new content — `git diff` would show no diff and the test would pass, incorrectly reporting FND-02 as satisfied.

The test was intended to prove "Phase 55 did not touch `python/fdars/__init__.py`", but it only proves "the file has no uncommitted changes right now". Any committed modification escapes detection.

**Fix:** Pin a base commit (the pre-Phase-55 HEAD) and diff against it:

```python
# Use the Phase 55 base commit stored in the phase plan or diff_base
BASE_COMMIT = "b5b8297ffa02f177b28c1205d116cedc0abf7a8f"

result = subprocess.run(
    ["git", "diff", "--quiet", BASE_COMMIT, "HEAD", "--", "python/fdars/__init__.py"],
    capture_output=True,
)
assert result.returncode == 0, (
    "python/fdars/__init__.py was modified between the Phase 55 base and HEAD "
    "(FND-02 violation)."
)
```

---

## Info

### IN-01: `ElasticMultinomialClassifier` uses `lambda_` as a constructor parameter name

**File:** `python/fdars/sklearn/_skeletons.py:1414`

**Issue:** `lambda_` ends with a trailing underscore, which is the sklearn convention for *fitted attributes* set during `fit()`. Using it as a constructor parameter stored in `__init__` does not cause a functional bug (sklearn's `get_params()` introspects the `__init__` signature and returns `lambda_` correctly), but it creates a misleading signal — `check_dont_overwrite_parameters` treats attributes ending in `_` as private/fitted and would not flag `self.lambda_` as a public parameter added during `fit`. The parameter is also not flagged by `check_params_default_constructible`. In effect the code works, but violates the sklearn naming convention in a way that can confuse future maintainers.

**Fix:** Rename to `lambda_param` or `roughness_penalty` in the constructor signature and store it as `self.lambda_` (private by sklearn convention) only as a fit attribute alias, or use `lambda_penalty`:

```python
def __init__(self, argvals=None, ncomp_beta=5, lambda_penalty=0.1, max_iter=100, tol=1e-4):
    super().__init__(argvals=argvals)
    self.ncomp_beta = ncomp_beta
    self.lambda_penalty = lambda_penalty  # no trailing underscore
    ...
```

---

### IN-02: `TestExcludeConsistency` generates zero test cases and is effectively inert

**File:** `tests/sklearn/test_coverage.py:101-130`

**Issue:** `TestExcludeConsistency.test_excluded_class_has_excluded_methods_entry` is parametrized over `[k for k, v in TRIAGE_VERDICTS.items() if v.startswith("EXCLUDE")]`. After the 2026-08-31 reclassification all 28 verdicts are PASS or PASS-WITH-FIXES, so this list is empty. pytest collects zero test cases from this class; the body never executes. The fallback `test_excluded_methods_nonempty` (line 133) covers the registry being non-empty, so the intent is partially preserved, but the class-level consistency check is dead.

**Fix:** Either document explicitly that this test class is intentionally dormant until future EXCLUDE verdicts are assigned, or replace it with a structural shape check that always has at least one case:

```python
def test_exclude_consistency_registry_vs_verdicts() -> None:
    """EXCLUDED_METHODS count must not fall below EXCLUDE verdict count."""
    exclude_verdict_count = sum(
        1 for v in TRIAGE_VERDICTS.values() if v.startswith("EXCLUDE")
    )
    assert len(EXCLUDED_METHODS) >= max(exclude_verdict_count, 1), (
        "EXCLUDED_METHODS must have at least one entry (design-time exclusions exist)"
    )
```

---

### IN-03: `FunctionalGMM` docstring still says "EXCLUDE predicted"

**File:** `python/fdars/sklearn/_skeletons.py:1752`

**Issue:** The class docstring reads: `"GMM clustering for functional data (triage candidate -- EXCLUDE predicted)."` After the 2026-08-31 reclassification, `FunctionalGMM` has verdict `PASS-WITH-FIXES: add n_iter_ attribute to fit()`. The docstring is stale and will mislead future maintainers about the estimator's status. Similarly, `TVDMSSDetector` (line 2149), `MUODDetector` (line 2249), and `DepthgramDetector` (line 2327) carry the same stale `-- EXCLUDE predicted` suffix.

**Fix:** Update the four class docstring one-liners to remove or replace the stale prediction:

```python
# FunctionalGMM -- line 1752:
"""GMM clustering for functional data.
```

```python
# TVDMSSDetector -- line 2149:
"""TVD-MSS functional outlier detector.
```

```python
# MUODDetector -- line 2249:
"""MUOD functional outlier detector.
```

```python
# DepthgramDetector -- line 2327:
"""Depthgram functional outlier detector.
```

---

_Reviewed: 2026-08-31T18:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
