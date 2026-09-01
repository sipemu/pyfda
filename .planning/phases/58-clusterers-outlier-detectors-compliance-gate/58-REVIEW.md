---
phase: 58-clusterers-outlier-detectors-compliance-gate
reviewed: 2026-09-01T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - python/fdars/sklearn/_skeletons.py
  - python/fdars/sklearn/_coverage.py
  - .github/workflows/ci.yml
findings:
  critical: 1
  warning: 4
  info: 2
  total: 7
status: issues_found
---

# Phase 58: Code Review Report

**Reviewed:** 2026-09-01
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Phase 58 adds `n_iter_` to `FuzzyFunctionalCMeans` and `FunctionalGMM`, introduces
`_BaseFdarsOutlierDetector` with the shared contamination → offset_ → decision_function
→ predict pattern, and ships six OutlierMixin estimators.  The compliance gate
(`_coverage.py`) records all 28 estimators as PASS.

The CI YAML, the clusterer fixes, the `_coverage.py` finalization, and the base-class
mechanics are structurally sound.  The primary defect is a **method-fidelity gap**: all
six outlier detectors produce byte-for-byte identical `score_samples` results, making
the choice of detector a no-op from the user's perspective.  Two secondary bugs are
also present: an unvalidated `contamination` parameter that silently accepts values
outside `(0, 0.5]`, and a double-validation of X inside the
`decision_function → score_samples` call chain.  Several quality issues round out the
report.

---

## Critical Issues

### CR-01: All Six Outlier Detectors Are Functionally Identical

**File:** `python/fdars/sklearn/_skeletons.py:2581-2601, 2668-2688, 2759-2780, 2863-2883, 2969-2989, 3064-3084`

**Issue:** Every `score_samples` implementation across all six detectors is the same
single-line body:

```python
return np.asarray(_native.depth.modified_band_1d(X, self.X_fit_))
```

The provenance attributes computed at fit time (LRT threshold, outliergram MEI/MBD,
TVDMSS TVD/MSS scores, MUOD shape/magnitude/amplitude indices, depthgram indices) are
**never consulted during scoring**.  Choosing `TVDMSSDetector` over `DepthgramDetector`
over `MUODDetector` produces exactly the same predictions and decision scores for every
input.  The class names, docstrings, and fit-time provenance computations all strongly
imply method-specific scoring, but the actual sklearn contract (score_samples, predict)
does not honour that implication.

This violates the project's "method-accurate" core value stated in `CLAUDE.md`: *every
diagram and example must faithfully depict what the method actually does*.  The same
standard applies to estimator classes.

**What the native API can supply (feasibility check):**

- `MagnitudeShapeDetector` — `_native.outliers.magnitude_shape(X)` returns per-row
  `magnitude` and `shape` outlyingness indices.  A method-faithful score could be
  `-(magnitude**2 + shape**2)` (negated combined outlyingness, higher = more normal).
  This is per-row against the training distribution by construction (no batch
  dependence) once the training statistics are stored.

- `MUODDetector` — `_native.outliers.muod` returns per-row `shape_index`,
  `magnitude_index`, `amplitude_index` arrays.  A method-faithful combined score
  (already stored in `shape_index_train_` etc.) could be used if the native function
  can score new curves against stored training reference indices.  However, if `muod`
  requires a complete batch (cannot score new X vs stored training indices), then
  subset-invariance requires the stored-reference depth fallback.

- `OutliergramDetector`, `TVDMSSDetector`, `DepthgramDetector`, `LRTDetector` —
  the native outlier functions (`outliergram`, `tvdmss`, `depthgram`, LRT) are
  whole-batch statistics and have no per-row-vs-stored-reference scoring variant.
  For these, stored-reference depth is the only subset-invariant option.

**Minimal honest fix (two levels):**

**Level A — rename and honest docstrings (minimum viable):** Where true per-method
scoring is impossible, the class names and docstrings must not overclaim.  Each class
should be documented as "an outlier detector that uses modified band depth vs the
training reference, initialised via the [method] provenance procedure at fit time."
The current wording ("TVD-MSS functional outlier detector", "Depthgram functional
outlier detector", etc.) implies the scoring uses the eponymous method, which is false.

**Level B — implement real per-row scoring where feasible:**  
`MagnitudeShapeDetector.score_samples` can use the negated combined outlyingness from
`_native.outliers.magnitude_shape`, making it the only detector that truly differs.
`MUODDetector.score_samples` can use a combined magnitude/shape/amplitude index if the
native call is per-row (it appears to be: `muod(X, factor)` takes any 2-D array).

**Severity: BLOCKER** — The user-visible API makes six distinct promises and delivers
one.  This is a correctness/fidelity defect against the project's stated accuracy
standard, not a style issue.

---

## Warnings

### WR-01: `contamination` Parameter Is Never Validated

**File:** `python/fdars/sklearn/_skeletons.py:2432-2442`

**Issue:** `_set_offset` computes `np.percentile(train_scores, 100.0 * self.contamination)`
without verifying that `contamination` is in `(0, 0.5]`.  Passing
`contamination=0` silently sets `offset_` to the minimum training score, causing
`predict` to label everything as an inlier (+1).  Passing `contamination=1.0` sets
`offset_` to the maximum, labelling everything as an outlier (-1).  Passing a negative
value or a value > 1 causes `np.percentile` to raise an obscure
`ValueError: Percentiles must be in the range [0, 100]` rather than a meaningful
estimator error.

**Fix:**

```python
def _set_offset(self, train_scores: np.ndarray) -> None:
    if not (0 < self.contamination <= 0.5):
        raise ValueError(
            f"contamination must be in (0, 0.5]; got {self.contamination!r}."
        )
    self.offset_ = float(
        np.percentile(train_scores, 100.0 * self.contamination)
    )
```

---

### WR-02: Double Validation of X in `decision_function → score_samples` Call Chain

**File:** `python/fdars/sklearn/_skeletons.py:2458-2459, 2598-2602`

**Issue:** `decision_function` calls `self.score_samples(X)` directly.  Every
`score_samples` override begins with `_validate(self, X, reset=False, ...)`, so X is
validated twice when `decision_function` (or `predict`, which calls `decision_function`)
is invoked.  `_validate` is not free: it invokes `validate_data` on every call.  More
importantly, calling `_validate` inside `score_samples` with `reset=False` on the raw
user-supplied array-like is correct only because `score_samples` is the public entry
point in the OutlierMixin contract.  When called via `decision_function`, the same
array has already been checked and converted, so the second call is a correctness-
neutral no-op for well-formed input — but it means the OutlierMixin's `score_samples`
contract is silently implemented with input handling inside the method rather than
delegated to the caller, making the chain fragile if someone overrides
`decision_function` to pass a pre-validated array.

The preferred fix is to have `score_samples` accept an already-validated `np.ndarray`
and move validation into the public entry points:

```python
def score_samples(self, X):
    check_is_fitted(self)
    X = _validate(self, X, reset=False, dtype="numeric", ensure_2d=True)
    X = X.astype(np.float64)
    return self._score_samples_validated(X)

def _score_samples_validated(self, X: np.ndarray) -> np.ndarray:
    # subclasses override this, X is already float64 ndarray
    raise NotImplementedError

def decision_function(self, X):
    check_is_fitted(self)
    X = _validate(self, X, reset=False, dtype="numeric", ensure_2d=True)
    X = X.astype(np.float64)
    return self._score_samples_validated(X) - self.offset_
```

At minimum, document the current behaviour explicitly so future overriders know
`score_samples` always receives raw user input, not a pre-validated array.

---

### WR-03: `MagnitudeShapeDetector` Error Message Does Not Contain Required "1 sample" Substring

**File:** `python/fdars/sklearn/_skeletons.py:2744-2746`

**Issue:** The `check_fit2d_1sample` compliance check expects the error message to
contain the substring `"1 sample"`.  All other estimators produce messages like
`"n_samples=1 is too small; Foo requires at least 2 samples."` which contains
`"1 sample"` (from the numeric `1` and the word `samples`).

`MagnitudeShapeDetector` uses a slightly different format:

```python
f"n_samples={n_obs} is too small; MagnitudeShapeDetector requires "
f"at least {self._min_samples} samples. (1 sample is not enough)"
```

When `n_obs=1` the message expands to contain both `"n_samples=1"` and
`"1 sample is not enough"`, so the test passes — but only for the single-sample
boundary case.  The parenthetical note `(1 sample is not enough)` is not present in
any other estimator and is inconsistent with the codebase style.  More importantly,
if a future reader changes `_min_samples` to 3 and the user passes 2 samples, the
error message will say `"n_samples=2 is too small … (1 sample is not enough)"`, which
is factually misleading (2 samples were provided, the threshold is 3).

**Fix:** Remove the parenthetical; the standard pattern is sufficient and consistent:

```python
raise ValueError(
    f"n_samples={n_obs} is too small; MagnitudeShapeDetector requires "
    f"at least {self._min_samples} samples."
)
```

---

### WR-04: `FunctionalGMM.predict` Computes Cluster Centers from Soft Membership, Not Native Centers

**File:** `python/fdars/sklearn/_skeletons.py:2386-2393`

**Issue:** `FunctionalGMM.fit` calls `_native.clustering.gmm_cluster` but does not
inspect whether the result dict contains a `"centers"` key (the way `FunctionalKMeans`
and `FuzzyFunctionalCMeans` do).  Instead, `predict` recomputes centers on every call:

```python
centers = self.membership_.T @ self.X_fit_   # (n_clusters, n_pts)
row_sums = self.membership_.sum(axis=0, keepdims=True).T
centers = centers / np.maximum(row_sums, 1e-10)
```

This is correct **only if `membership_` is hard-normalized** (columns sum to 1 over
rows).  For a GMM, `membership_` is a soft responsibility matrix; each column sums to
the total soft weight assigned to that cluster, not 1.  The division by `row_sums`
(which is `np.maximum(membership_.sum(axis=0), 1e-10)` reshaped) correctly recovers
the weighted centroid — so the math is right.  However, the approach depends on whether
`gmm_cluster` returns a `centers` key that could be used directly (as a stored
attribute) to avoid recomputing centroids on every `predict` call.

If `gmm_cluster` returns `"centers"`, storing it as `self.cluster_centers_` in `fit`
and using it in `predict` (as the two other clusterers do) would be both more efficient
and consistent with the pattern.  If no `"centers"` key exists, the current weighted-
centroid approach should be documented and `cluster_centers_` should be computed once
in `fit` and stored for reuse:

```python
# In fit(), after calling gmm_cluster:
row_sums = self.membership_.sum(axis=0, keepdims=True).T   # (n_clusters, 1)
self.cluster_centers_ = (
    (self.membership_.T @ X) / np.maximum(row_sums, 1e-10)
)  # (n_clusters, n_pts)

# In predict(), use stored centers:
dists = _pairwise_l2(X, self.cluster_centers_)
return np.argmin(dists, axis=1).astype(np.intp)
```

This removes `self.X_fit_` as a dependency for `predict`, consistent with all other
clusterers and avoiding an O(n_train * n_pts) matrix multiply on every predict call.

---

## Info

### IN-01: `_coverage.py` TRIAGE_VERDICTS Is a Mutable Module-Level Dict

**File:** `python/fdars/sklearn/_coverage.py:163-321`

**Issue:** `TRIAGE_VERDICTS` and `EXCLUDED_METHODS` are plain `dict` objects defined
at module level.  Any importer can mutate them at runtime (add, remove, or overwrite
entries).  Given that these dicts serve as the compliance registry — the authoritative
record of what has passed — a stray assignment (`TRIAGE_VERDICTS["Foo"] = "PASS"`)
would silently corrupt the audit trail.

**Fix:** Replace with `types.MappingProxyType` to make them read-only:

```python
import types
TRIAGE_VERDICTS: types.MappingProxyType = types.MappingProxyType({
    "FPCATransformer": "PASS",
    ...
})
```

---

### IN-02: CI `sklearn-compliance` Job Installs `sklearn` Extra After `maturin develop`

**File:** `.github/workflows/ci.yml:110-118`

**Issue:** The `sklearn-compliance` job runs `maturin develop --release` (line 114)
and then in a separate step installs the `[sklearn]` extra via `pip install -e ".[sklearn]"`
(line 118).  Because `maturin develop` already builds and installs the native extension
in editable mode, the second `pip install -e` will re-trigger an editable reinstall
that may recompile the Rust extension in debug mode (if `maturin develop` without
`--release` is the default triggered by pip), depending on how pip resolves the
build backend.  In practice this is harmless because `pip install -e` for a maturin
project without explicit `--release` in the pip invocation uses whatever the backend
defaults to (typically debug).

The safe, idiomatic pattern for maturin projects is:

```yaml
- name: Install all extras (including sklearn)
  run: |
    source .venv/bin/activate
    maturin develop --release
    pip install -e ".[sklearn]"
```

Which is what the job already does — so this is advisory only.  However, a comment
documenting why the two-step pattern is safe would benefit future maintainers.

---

_Reviewed: 2026-09-01_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
