---
phase: 58-clusterers-outlier-detectors-compliance-gate
fixed_at: 2026-09-01T19:36:39Z
review_path: .planning/phases/58-clusterers-outlier-detectors-compliance-gate/58-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 58: Code Review Fix Report

**Fixed at:** 2026-09-01T19:36:39Z
**Source review:** `.planning/phases/58-clusterers-outlier-detectors-compliance-gate/58-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 7 (1 Critical, 4 Warning, 2 Info)
- Fixed: 7
- Skipped: 0

**Verification ran in:** main checkout (workflow.use_worktrees=false)

**Test result:** 4294 passed, 0 failures (up from 4293; new regression guard test added)

---

## Fixed Issues

### CR-01: Method-fidelity gap — all six outlier detectors byte-for-byte identical

**Files modified:** `python/fdars/sklearn/_skeletons.py`, `tests/sklearn/test_outliers_compliance.py`
**Commit:** `b4f8074` (_skeletons.py), `cc145f2` (regression guard test)

**Applied fix:**

Two-level fix as recommended:

**Level B (MagnitudeShapeDetector — real characteristic score):**
Replaced the band-depth surrogate with a genuinely method-faithful MS
outlyingness score. In `fit`, the detector now stores `mu_` (pointwise training
mean) and `var_` (pointwise training variance) as the fixed scoring reference.
In `_score_samples_validated`, each new row is scored as
`-(MO² + VO²)` where `MO = mean_t(|x(t) - mu_(t)|)` (magnitude outlyingness)
and `VO = mean_t(|(x(t)-mu_(t))² - var_(t)|)` (shape/variance outlyingness).
Both quantities depend only on the stored training statistics, not on the
current test batch — `check_methods_subset_invariance` passes. The `depth_method`
parameter (unused in the old implementation) was removed along with `X_fit_`
(no longer needed for scoring; only the training statistics are stored).

**Level A (LRT, Outliergram, TVDMSS, MUOD, Depthgram — honest docstrings):**
Each of these detectors' `score_samples` docstrings now clearly states:
(1) the sklearn-facing score is modified band depth vs the stored training
reference (a subset-invariant surrogate); and (2) the eponymous native method
(LRT bootstrap, outliergram MEI/MBD, TVD/MSS, MUOD indices, depthgram) is
a whole-sample quantity that cannot be decomposed per-row — the fit-time
provenance attributes remain available for the true batch-relative analysis.

**Base class refactored (WR-02 co-fix):**
All six detectors were refactored from overriding `score_samples(X)` (with
internal `_validate` + float64 cast) to overriding `_score_samples_validated(X: np.ndarray)`.
The base class `score_samples` validates once and delegates; `decision_function`
validates once and calls `_score_samples_validated` directly — eliminating the
double-validation (previously, `decision_function` called the public
`score_samples` which re-validated).

**Regression guard test added:** `test_magnitude_shape_distinct_from_band_depth`
in `test_outliers_compliance.py` asserts that `MagnitudeShapeDetector.score_samples`
returns values NOT identical to `DepthgramDetector.score_samples` on a
magnitude-outlier dataset, and that outlier curves score below normal curves.

**Which detectors are now method-distinct vs surrogate:**
- `MagnitudeShapeDetector`: **method-faithful MS outlyingness score** (`-(MO²+VO²)` vs stored training mean/variance). Genuinely distinct from all other detectors.
- `LRTOutlierDetector`, `OutliergramDetector`, `TVDMSSDetector`, `MUODDetector`, `DepthgramDetector`: **documented modified-band-depth surrogate** (honest in docstrings). Native methods are batch-relative and have no per-row subset-invariant decomposition.

---

### WR-01: `contamination` parameter never validated in `_set_offset`

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `b4f8074`

Added a `not (0 < self.contamination <= 0.5)` guard at the top of `_set_offset`
that raises `ValueError` with a clear message before `np.percentile` is called.
This prevents silent degenerate behavior (e.g. `contamination=0` labelling
everything inlier, negative values producing obscure percentile errors).
The default `contamination=0.1` passes the guard; `check_estimator` stays green.

---

### WR-02: Double validation of X in `decision_function → score_samples` chain

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `b4f8074`

Resolved as part of the CR-01 base class refactor. The base class now exposes:
- `score_samples(X)`: public entry point — validates once, upcasts to float64,
  calls `_score_samples_validated`.
- `decision_function(X)`: validates once, upcasts to float64, calls
  `_score_samples_validated` directly (never calls the public `score_samples`).
- `_score_samples_validated(X: np.ndarray)`: internal hook for subclasses —
  receives a pre-validated float64 ndarray, no validation performed.

Validation now happens exactly once on each public call path.

---

### WR-03: MagnitudeShapeDetector error message inconsistent/misleading parenthetical

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `b4f8074`

Removed the parenthetical `(1 sample is not enough)` from the `ValueError` in
`MagnitudeShapeDetector.fit`. The message now follows the standard pattern used
by all other estimators:
```
f"n_samples={n_obs} is too small; MagnitudeShapeDetector requires at least {self._min_samples} samples."
```
This is consistent with the codebase style and will remain accurate if
`_min_samples` is ever raised.

---

### WR-04: `FunctionalGMM.predict` recomputes cluster centers on every call

**Files modified:** `python/fdars/sklearn/_skeletons.py`
**Commit:** `b4f8074`

Moved the weighted-centroid computation from `predict` into `fit`. After calling
`gmm_cluster`, `fit` now computes:
```python
_row_sums = self.membership_.sum(axis=0, keepdims=True).T  # (n_clusters, 1)
self.cluster_centers_ = (
    (self.membership_.T @ X) / np.maximum(_row_sums, 1e-10)
)  # (n_clusters, n_pts)
```
`predict` now calls `_pairwise_l2(X, self.cluster_centers_)` directly, matching
the pattern of `FunctionalKMeans` and `FuzzyFunctionalCMeans`. `X_fit_` is no
longer stored (removed from `fit`), removing an O(n_train × n_pts) matrix
multiply from every `predict` call.

---

### IN-01: `TRIAGE_VERDICTS` / `EXCLUDED_METHODS` are mutable module-level dicts

**Files modified:** `python/fdars/sklearn/_coverage.py`, `tests/sklearn/test_foundation.py`
**Commit:** `ca02cf5`

Both dicts are now wrapped in `types.MappingProxyType` making them read-only at
runtime. A stray `TRIAGE_VERDICTS["Foo"] = "PASS"` will now raise `TypeError`
rather than silently corrupting the compliance audit trail.

`test_foundation.py` was updated to check `isinstance(X, collections.abc.Mapping)`
rather than `isinstance(X, dict)` (since `MappingProxyType` is not a `dict`
subclass). All other tests that iterate or key-access the dicts are unaffected —
`MappingProxyType` is fully Mapping-compatible.

---

### IN-02: CI `sklearn-compliance` job two-step pattern undocumented

**Files modified:** `.github/workflows/ci.yml`
**Commit:** `0020c60`

Added an 8-line comment above the `pip install -e ".[sklearn]"` step explaining
that the two-step `maturin develop --release` + `pip install -e ".[sklearn]"`
is intentional: the first step builds the native extension (once, release-optimised);
the second only installs the pure-Python `[sklearn]` extras (scikit-learn etc.)
without triggering a Rust recompile.

---

## Skipped Issues

None.

---

_Fixed: 2026-09-01T19:36:39Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
