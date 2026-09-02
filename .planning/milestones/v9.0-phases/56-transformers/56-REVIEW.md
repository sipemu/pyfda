---
phase: 56-transformers
reviewed: 2026-08-31T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - python/fdars/sklearn/_skeletons.py
  - python/fdars/sklearn/_coverage.py
  - tests/sklearn/test_transformers_compliance.py
  - tests/sklearn/test_transformer_pipeline.py
findings:
  critical: 0
  warning: 4
  info: 3
  total: 7
status: issues_found
---

# Phase 56: Code Review Report

**Reviewed:** 2026-08-31
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 56 promoted three transformers (Imputer, BasisRepresentation, SplineInterpolator) from PASS-WITH-FIXES to full `check_estimator` compliance via targeted Python-layer guards. The architectural approach is sound. No correctness blockers were found. Four warnings and three info items are reported, focusing on: the TypeError-narrowing logic in Imputer (message-string dependency), the silent order-clamping in SplineInterpolator (semantic mismatch, no warning), a stale tally in the `_coverage.py` module docstring, and a gap in the pipeline test's coverage of cross-transformer invariants.

---

## Warnings

### WR-01: Imputer TypeError narrowing depends on sklearn exception message text

**File:** `python/fdars/sklearn/_skeletons.py:542` (and mirror at line 577)

**Issue:** The cross-version shim in both `Imputer.fit` and `Imputer.transform` narrows the `except TypeError` by inspecting `str(exc)` for the substring `"ensure_all_finite"`. This couples the guard's correctness to sklearn's internal error message wording. If sklearn's `validate_data` ever raises a `TypeError` for a different reason (e.g., an exotic dtype conversion path) whose message coincidentally contains the string `"ensure_all_finite"`, that real error will be silently swallowed and the fallback `_validate` will be called with the wrong keyword, producing a confusing second error rather than the original one. Conversely, if sklearn changes the wording of the "unknown keyword" `TypeError` to omit the keyword name (e.g., "unexpected keyword argument"), the guard condition inverts: old-sklearn TypeError would now be re-raised as if it were a real error, breaking NaN-input handling on old sklearn.

The condition also duplicates the same text-matching logic identically in `fit` and `transform` with no shared helper, doubling the maintenance surface.

**Fix:** Extract the shim into a shared helper in `_base.py` (or as a private method on `Imputer`) so the logic lives in exactly one place. Narrow the guard more precisely: check the exception type reported by Python's `TypeError` for unknown kwargs — which in CPython is `"got an unexpected keyword argument"` — rather than the keyword name itself. This is more stable than checking for the keyword value:

```python
# In _base.py or as a private Imputer helper
def _validate_allow_nan(estimator, X, *, reset):
    """Cross-version shim: validate with NaN allowed, sklearn 1.3-1.8."""
    try:
        return _validate(
            estimator, X, reset=reset, dtype="numeric", ensure_2d=True,
            accept_sparse=False, ensure_all_finite="allow-nan"
        )
    except TypeError as exc:
        msg = str(exc)
        # Only catch the "unknown keyword argument" TypeError from old sklearn.
        # Any other TypeError (dtype mismatch, etc.) must propagate.
        if "unexpected keyword argument" not in msg or "ensure_all_finite" not in msg:
            raise
        return _validate(
            estimator, X, reset=reset, dtype="numeric", ensure_2d=True,
            accept_sparse=False, force_all_finite="allow-nan"
        )
```

---

### WR-02: SplineInterpolator silently clamps order without any warning

**File:** `python/fdars/sklearn/_skeletons.py:691`

**Issue:** When the constructor `order` parameter exceeds `n_pts - 1`, `fit` silently clamps `self.order_` to `n_pts - 1`. For example, a user who constructs `SplineInterpolator(order=3)` (cubic) and then calls `fit` on data with `n_pts=2` will get `order_=1` (linear interpolation) — a dramatically different mathematical result — with no indication that clamping occurred. The docstring says "B-spline order: 1=linear, 2=quadratic, 3=cubic (default 3)" which implies the user's intent will be respected.

The comment in the code ("This is the sklearn-idiomatic approach for data-dependent parameter constraints") is only partially accurate: sklearn idiom uses `warnings.warn(ConvergenceWarning)` or similar for parameter changes induced by data properties; silent clamping is idiomatic only when the clamped value is mathematically equivalent (e.g., capping `n_components` at `min(n_obs-1, n_pts)` for FPCA). For spline order, `order=1` (linear) and `order=3` (cubic) are not equivalent in any limiting sense.

**Fix:** Emit a `sklearn.exceptions.UnderfitWarning` (or `UserWarning`) when clamping occurs, so the user knows their spline order was reduced:

```python
import warnings

effective_order = min(int(self.order), n_pts - 1)
if effective_order < int(self.order):
    warnings.warn(
        f"SplineInterpolator: requested order={self.order} exceeds "
        f"n_pts-1={n_pts - 1}; clamping to order_={effective_order}.",
        UserWarning,
        stacklevel=2,
    )
self.order_ = effective_order
```

---

### WR-03: `_coverage.py` module docstring tally is stale after Phase 56

**File:** `python/fdars/sklearn/_coverage.py:19-22`

**Issue:** The module docstring under "Final verdict tally after reclassification" reads:

```
PASS:            6  (zero failing checks, as of Phase 55)
PASS-WITH-FIXES: 22 (fixable with guard/wrapper/attribute add in Phases 56-58)
EXCLUDE:          0
```

After Phase 56, the actual tally is PASS: 9, PASS-WITH-FIXES: 19 (confirmed by counting `TRIAGE_VERDICTS` directly: 8 transformer PASSes + 1 clusterer PASS = 9 PASS; 5 regressors + 6 classifiers + 2 clusterers + 6 outlier detectors = 19 PASS-WITH-FIXES). The Phase 56 incremental commentary at lines 24-27 is correct, but the header tally — which a reader encounters first — directly contradicts the actual verdicts in the file.

**Fix:** Update the module docstring to reflect the post-Phase-56 state:

```python
"""...
Final verdict tally after reclassification + Phase 56 fixes:
  PASS:            9  (8 transformers + FunctionalKMeans)
  PASS-WITH-FIXES: 19 (fixable with guard/wrapper/attribute add in Phases 57-58)
  EXCLUDE:          0  (among the 28 skeletoned candidates)
...
"""
```

---

### WR-04: `BasisRepresentation.fit` calls `fdata_to_basis_1d` on fit data and discards the result

**File:** `python/fdars/sklearn/_skeletons.py:464-467`

**Issue:** `BasisRepresentation.fit` calls `_native.basis.fdata_to_basis_1d(X, self.argvals_, n_basis, self.basis_type)` solely to obtain `actual_n_basis` from the second return value, discarding the coefficient array. Then `transform` calls the same function again on the transform-time `X` to get both coefficients and `actual_n_basis`.

There are two problems:

1. **Wasted computation**: the full projection is computed twice on the same training data when `fit` is immediately followed by `transform` (as in `fit_transform`).

2. **Fragile `n_basis_` provenance**: `self.n_basis_` is derived from the fit data but applied in transform to a potentially different dataset. If the native function's `actual_n_basis` output is data-dependent (e.g., it reduces `n_basis` when the gram matrix is rank-deficient for the training data), then transforming data where a higher `n_basis` would be valid still uses the fit-time-reduced value — this is correct behavior, but it means the fit-time discard of coefficients is meaningful only if `actual_n_basis` from fit is always `<= actual_n_basis` from any valid transform call. This assumption is not verified.

**Fix:** Store the coefficient array or at least verify the approach is intentional with an explicit comment explaining why fit-time coefficients are discarded:

```python
# fit: project training data to determine the effective n_basis,
# then store it for use in transform. Coefficients from fit are intentionally
# discarded -- transform always re-projects the input data.
coeffs_fit, actual_n_basis = _native.basis.fdata_to_basis_1d(
    X, self.argvals_, n_basis, self.basis_type
)
self.n_basis_ = actual_n_basis
```

Alternatively, store `coeffs_fit` as `self.coeffs_train_` if downstream users of the transformer need it (e.g., for a future `inverse_transform`).

---

## Info

### IN-01: `test_transformers_never_construct_fdata` only inspects subclass source, not base class

**File:** `tests/sklearn/test_transformer_pipeline.py:159`

**Issue:** `inspect.getsource(cls)` on a subclass returns only the source of that subclass's own body — not the source of its base classes (`_BaseFdarsEstimator`, `TransformerMixin`). If a future contributor accidentally adds an `Fdata(` call to `_BaseFdarsEstimator._sign_canonicalize` or `_resolve_argvals`, this test would not catch it.

**Fix:** Also inspect the base class source, or explicitly state in the test docstring that it only guards subclass bodies:

```python
source = inspect.getsource(cls)
# Also check the base class to ensure no Fdata( creeps into shared helpers
base_source = inspect.getsource(_BaseFdarsEstimator)
assert "Fdata(" not in source
assert "Fdata(" not in base_source  # guard shared base helpers too
```

---

### IN-02: `test_smoother_fpca_pipeline_roundtrip` does not test with NaN-containing input through Imputer

**File:** `tests/sklearn/test_transformer_pipeline.py:62`

**Issue:** The pipeline test only covers `BSplineSmoother -> FPCATransformer`. There is no pipeline-level test that exercises `Imputer -> BasisRepresentation` or `Imputer -> FPCATransformer` — the two promoted-to-PASS transformers that most needed their NaN-handling verified across a `fit_transform` boundary. The test for Imputer compliance relies entirely on the `parametrize_with_checks` battery in `test_transformers_compliance.py` (which does not check pipeline composition), while the pipeline test does not exercise Imputer at all.

**Fix:** Add at least one pipeline test that includes `Imputer` as the first step:

```python
def test_imputer_basis_pipeline_roundtrip():
    X = _make_X()
    X[::5, ::7] = np.nan  # inject NaN pattern
    pipe = Pipeline([
        ("imputer", Imputer()),
        ("basis", BasisRepresentation(n_basis=3)),
    ])
    X_out = pipe.fit_transform(X)
    assert X_out.shape == X.shape
    assert np.all(np.isfinite(X_out))
```

---

### IN-03: `SplineInterpolator` `order` parameter type is not enforced; float silently accepted

**File:** `python/fdars/sklearn/_skeletons.py:691`

**Issue:** The constructor accepts `order=3` (documented as `int`) but `fit` casts it with `int(self.order)`. If a user passes `order=2.9` or `order=3.0`, the conversion succeeds silently. While this is unlikely to cause user error in practice, it means `get_params()` returns a float but the docstring says `int`, and `clone()` would reconstruct with a float — which then gets compared unequal in some sklearn equality checks. More importantly, the `< 1` comparison at line 684 works on floats (e.g., `0.5 < 1` is `True`), but a user passing `order=0.5` would hit the ValueError path — which is correct. A user passing `order=1.7` would get clamped to `1`, potentially confusing.

**Fix:** Add an explicit `int` cast or validation in `fit` before the `< 1` check, and update the docstring to note that non-integer values are truncated:

```python
order = int(self.order)
if order < 1:
    raise ValueError(
        f"SplineInterpolator order must be >= 1; got order={self.order}."
    )
self.order_ = min(order, n_pts - 1)
```

---

_Reviewed: 2026-08-31_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
