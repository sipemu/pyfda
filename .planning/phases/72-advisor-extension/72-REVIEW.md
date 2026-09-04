---
phase: 72-advisor-extension
reviewed: 2026-09-04T00:00:00Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - python/fdars/advisor/aspects/fts.py
  - python/fdars/advisor/aspects/frechet.py
  - python/fdars/advisor/aspects/regression.py
  - python/fdars/advisor/aspects/classification.py
  - python/fdars/advisor/aspects/spm.py
  - python/fdars/advisor/__init__.py
  - python/fdars/mcp/server.py
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: issues_found
---

# Phase 72: Code Review Report

**Reviewed:** 2026-09-04
**Depth:** deep
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Phase 72 adds two new advisor aspects (`fts.py`, `frechet.py`) and extends three
existing aspects (`regression.py`, `classification.py`, `spm.py`), plus updating
the MCP guard-sync in `server.py` and the dispatch table in `__init__.py`.

**Grounding invariant:** No numpy scalar leaks into any returned diagnostics dict
were found. Every `np.max`, `np.mean`, `np.min`, `np.trace`, and array-element
access in the new/extended branches is wrapped in `float()`, `int()`, or `bool()`
before being assigned to the output dict. The `float(1.0 - raw["train_accuracy"])`
subtraction in `classification.py:152` is safe because `raw["train_accuracy"]` is
already a Python float at that point.

**Guard-sync:** `fts` and `frechet` appear in `_supported` (`__init__.py:151-152`),
`_DIAGNOSTICS_METHODS` (`server.py:85-86`), and `_EXPECTED_DIAGNOSTICS_METHODS`
(`test_guard_sync_version_independent.py:56-57`) — and are absent from
`_RUNNABLE_METHODS` everywhere. SC3 is preserved.

**Shapelet handle ordering:** The handle-to-dict coercion in `__init__.py:169-174`
runs before the `dict(raw)` fallback — correct sequencing.

**Array-before-dict guard:** Both `spm.py` (line 92) and `frechet.py` (line 75)
check `isinstance(raw, dict)` / `hasattr(raw, "__array__")` before any dict key
access. No `AttributeError` or `KeyError` on array inputs.

**One critical bug found** and three warnings of varying impact, detailed below.

---

## Critical Issues

### CR-01: Shapelet classifier spuriously triggers `has_elastic_multinomial = True`

**File:** `python/fdars/advisor/aspects/classification.py:148`

**Issue:** The shapelet handle coercion in `__init__.py:169-174` produces the dict:

```python
{
    "train_accuracy": float(raw.train_accuracy),
    "n_shapelets": int(raw.n_shapelets),
    "n_classes": int(raw.n_classes) if hasattr(raw, "n_classes") else None,
}
```

This dict contains the key `"train_accuracy"`. The elastic multinomial
discriminator in `classification.py:148` is:

```python
has_elastic_multinomial = "train_accuracy" in raw
```

Because the coerced shapelet dict has `"train_accuracy"`, the elastic multinomial
branch fires for every shapelet classifier result. The returned dict will have
`has_elastic_multinomial = True` when it should be `False`. The LLM receives a
misleading method-identification signal: it is told an elastic multinomial was run
when a shapelet classifier was run. Additionally, `train_error_rate` is computed
and emitted for the shapelet path via the elastic branch.

This is a logic correctness defect — the `has_*` booleans are the primary
method-type discriminators for the LLM. A wrong `True` here undermines the
grounding premise.

**Fix:** Tighten the elastic multinomial discriminator to exclude shapelet results.
Elastic multinomial returns a key unique to its result shape (not `"n_shapelets"`).
The cleanest fix is to negate the presence of the shapelet key:

```python
# classification.py line 148
has_elastic_multinomial = "train_accuracy" in raw and "n_shapelets" not in raw
```

Alternatively, give the shapelet coercion a sentinel key that elastic multinomial
never produces, e.g. `"__shapelet__": True`, and discriminate on that instead.

---

## Warnings

### WR-01: `spm.py` mfpca input populates `ncomp` and `eigenvalues` fields from mfpca eigenvalues

**File:** `python/fdars/advisor/aspects/spm.py:133-135` and `181-187`

**Issue:** The spm_phase1 fields `ncomp` and `eigenvalues` are populated
unconditionally using `eigen_arr` (lines 135, 181), which for an mfpca input
comes from mfpca's `"eigenvalues"` key. The mfpca branch later writes the same
values into `mfpca_ncomp` and `mfpca_eigenvalues`. The LLM therefore sees:

- `diag["ncomp"]` = mfpca component count (spm_phase1 field, should be None for mfpca)
- `diag["eigenvalues"]` = mfpca eigenvalue list (spm_phase1 field, should be None for mfpca)
- `diag["mfpca_ncomp"]` = same value (correct)
- `diag["mfpca_eigenvalues"]` = same list (correct)

No grounding violation — the values are real. But the spm_phase1 sentinel fields
(intended to signal "no spm_phase1 data") are non-None for mfpca input, which is
semantically incorrect.

**Fix:** Skip the spm_phase1 eigenvalue / ncomp fields when the mfpca discriminator
fires. One approach: compute `has_mfpca` earlier (before the spm_phase1 block) and
gate the spm_phase1 eigenvalue block on `not has_mfpca`:

```python
# Compute discriminator early
has_mfpca = "eigenfunctions" in raw and "scales" in raw

# ... then in the eigenvalue block (line 180):
if eigen_arr is not None and not has_mfpca:
    diag["eigenvalues"] = [float(v) for v in eigen_arr]
    diag["variance_explained_cumulative"] = _eigenvalues_to_variance_cumulative(eigen_arr)
else:
    diag["eigenvalues"] = None
    diag["variance_explained_cumulative"] = None

# Same gate for ncomp (line 135):
diag["ncomp"] = int(len(eigen_arr)) if (eigen_arr is not None and not has_mfpca) else None
```

### WR-02: `fts.py` acf branch accesses `raw["lags"]` without guarding; dpca branch accesses `raw["eigenvalues"]` without guarding

**File:** `python/fdars/advisor/aspects/fts.py:104` and `130`

**Issue:** The acf discriminator at line 101 checks `"acf" in raw and "upper_band" in raw`,
but the branch body at line 104 accesses `raw["lags"]` without a guard. If the key
`"lags"` were absent (malformed input, future API change), this raises `KeyError`
and crashes the diagnostic builder.

Similarly, the dpca discriminator checks `"filter_lag" in raw and "n_freqs" in raw`
but the dpca branch at line 130 accesses `raw["eigenvalues"]` without a guard.

Both keys are confirmed present in real fdars output per the RESEARCH doc, so this
will not crash on valid inputs. But it violates the "all accesses guarded" discipline
stated in the module docstrings (ASVS V5) and will break on malformed or future-
changed fdars results.

**Fix:** Add None-fallback guards:

```python
# fts.py line 104
lags_arr = np.asarray(raw["lags"]) if "lags" in raw else np.array([])
diag["n_lags"] = int(len(lags_arr))

# fts.py line 130
eigenvalues_raw = raw.get("eigenvalues")
if eigenvalues_raw is not None:
    diag["dpca_eigenvalues"] = [
        float(np.max(np.asarray(ev))) for ev in eigenvalues_raw
    ]
else:
    diag["dpca_eigenvalues"] = None
```

### WR-03: `server.py` docstring and `build_diagnostics` docstring not updated for the 16-method set

**File:** `python/fdars/mcp/server.py:117-121` and `python/fdars/advisor/__init__.py:106-109`

**Issue:** Two docstrings still describe the pre-Phase-72 14-method set:

1. `server.py:117`: `"One of the fourteen supported aspects"` — the count is now 16.
   The method list at lines 118-121 omits `"fts"` and `"frechet"`.

2. `__init__.py:106-109`: The `method` parameter docstring lists only
   `"alignment", "fpca", ..., "inference"` — the 14 pre-Phase-72 methods. The
   dispatch code at lines 240-246 correctly handles `"fts"` and `"frechet"` but the
   docstring advertises a stale API contract.

These mismatches will confuse callers consulting the docstring and may cause
automated doc-checking tools to flag drift.

**Fix:**

In `server.py:117`:
```python
        One of the sixteen supported aspects (``_DIAGNOSTICS_METHODS``):
        ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``, ``'depth'``, ``'outliers'``, ``'classification'``,
        ``'represent'``, ``'regression'``, ``'regression_cv'``, ``'spm'``,
        ``'scoring'``, ``'inference'``, ``'fts'``, ``'frechet'``.
```

In `__init__.py:106-109`:
```python
    method : {"alignment", "fpca", "basis", "smoothing", "clustering", "depth", \
"outliers", "classification", "represent", "regression", "regression_cv", \
"spm", "scoring", "inference", "fts", "frechet"}
```

---

## Info

### IN-01: `fts.py` dpca branch comment incorrectly describes eigenvalue structure

**File:** `python/fdars/advisor/aspects/fts.py:128-129`

**Issue:** The inline comment reads:

```python
# eigenvalues is a list of 1-D arrays (one per component).
# Summarise as the max eigenvalue per component (frequency peak).
```

The RESEARCH document (Section 2A) describes dpca `eigenvalues` as a plain flat
`array` — not a list of 1-D arrays. The code happens to work correctly for both
interpretations (iterating a flat array gives scalars, `np.max(scalar)` is that
scalar; iterating nested arrays gives sub-arrays, `np.max(sub-array)` gives the
max). But the misleading comment could cause a future editor to misunderstand the
data shape and write incorrect code when extending this branch.

**Fix:** Update the comment to reflect the confirmed flat-array type, or explicitly
handle both cases with a `isinstance(ev, (list, np.ndarray))` check and note the
ambiguity.

### IN-02: `spm.py` mfpca branch redundantly guards `"eigenfunctions" in raw` inside an already-guarded block

**File:** `python/fdars/advisor/aspects/spm.py:239`

**Issue:** Line 219 checks `has_mfpca = "eigenfunctions" in raw and "scales" in raw`,
and the `if has_mfpca:` block at line 221 runs only when that is True. Line 239
then redundantly checks `if "eigenfunctions" in raw:` again — this condition is
always True inside the `if has_mfpca:` block. The double-check suggests defensive
intent but is dead code that may confuse a future reader into thinking the key
could be absent here.

**Fix:** Remove the inner guard or add a comment explaining it is unreachable:

```python
# eigenfunctions is guaranteed present (part of has_mfpca discriminator)
diag["mfpca_n_variables"] = int(len(raw["eigenfunctions"]))
```

---

_Reviewed: 2026-09-04_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
