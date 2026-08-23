---
phase: 50-deferred-advisor-aspects-compat-pre-flight
reviewed: 2026-08-23T00:00:00Z
depth: deep
files_reviewed: 9
files_reviewed_list:
  - python/fdars/advisor/aspects/fpca.py
  - python/fdars/advisor/aspects/classification.py
  - python/fdars/advisor/aspects/inference.py
  - python/fdars/advisor/_prompts.py
  - pyproject.toml
  - tests/test_mcp_import_smoke.py
  - tests/test_guard_sync_version_independent.py
  - tests/test_advisor_itp.py
  - tests/test_advisor_group_b.py
findings:
  critical: 0
  warning: 4
  info: 1
  total: 5
status: issues_found
---

# Phase 50: Code Review Report

**Reviewed:** 2026-08-23T00:00:00Z
**Depth:** deep
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Phase 50 delivers three new advisor aspect diagnostic branches (PACE-FPCA extra scalars, elastic-multinomial overfitting gap, ITP vector-to-scalar reduction), the `anthropic<1.0` compatibility pin, and four new test files. The grounding invariant is upheld throughout: every new scalar is derived from fdars-computed values, `float()` casts prevent numpy scalar leaks, and the raw `adjusted_pvalues` array is never stored in the output dict.

The implementation is structurally sound and the overwhelming majority of edge cases are handled correctly. Four warnings were found — none are crashes in the happy path, but three involve silent data corruption or incorrect scalar values under specific input conditions that fdars itself should never produce but that callers or future tests might trigger. The fourth is a routing-precedence gap where ITP data is silently discarded without any warning.

No critical issues (security vulnerabilities, data loss, or authentication bypasses) were found.

## Critical Issues

None.

## Warnings

### WR-01: `pace_mean_prediction_band_width` emits `NaN` for empty or zero-element fitted arrays

**File:** `python/fdars/advisor/aspects/fpca.py:133-136`
**Issue:** When `fitted_lower` or `fitted_upper` is present in `raw` but resolves to a zero-element array (e.g., `[]`), the computation `float((fu_arr - fl_arr).mean())` produces `float('nan')`. Python's `json.dumps` outputs `NaN` for this value — a non-RFC-8259-compliant token. The diagnostics dict then contains a `NaN` float rather than `None`, which corrupts the JSON prompt sent to the LLM (line 454 of `advisor/__init__.py` serialises `diagnostics` directly). The same issue arises if `fitted_lower` and `fitted_upper` have mismatched shapes, which causes a numpy broadcast error (unhandled exception).

```python
# Current code — no shape or emptiness guard:
fl_arr = np.asarray(fl, dtype=float)
fu_arr = np.asarray(fu, dtype=float)
diag["pace_mean_prediction_band_width"] = float((fu_arr - fl_arr).mean())

# Fix: guard for emptiness and shape mismatch
if fl_arr.size == 0 or fu_arr.size == 0 or fl_arr.shape != fu_arr.shape:
    diag["pace_mean_prediction_band_width"] = None
else:
    diag["pace_mean_prediction_band_width"] = float((fu_arr - fl_arr).mean())
```

### WR-02: ITP fraction denominator uses `raw["n_basis"]` while numerator counts against `len(pvalues_list)` — silent mismatch produces incorrect fraction

**File:** `python/fdars/advisor/aspects/inference.py:193,211-216`
**Issue:** `n_basis` is read from `raw["n_basis"]` when present; `sig_indices` and `n_sig` are computed by iterating over `pvalues_list` (whose length is `len(raw["adjusted_pvalues"])`). If `raw["n_basis"] != len(raw["adjusted_pvalues"])` (e.g., a caller passes a truncated array or a stale metadata value), the fraction `n_sig / n_basis` uses a wrong denominator. The `itp_n_significant_0.05` count and `itp_fraction_significant_0.05` ratio are then inconsistent with each other. The extreme case `raw["n_basis"] = 0` produces `n_sig > 0` alongside `fraction = 0.0`.

```python
# Current (line 193, 215-216):
n_basis = int(raw["n_basis"]) if "n_basis" in raw else len(pvalues_list)
...
if n_basis > 0:
    diag["itp_fraction_significant_0.05"] = float(n_sig / n_basis)

# Fix: always derive n_basis from the actual array length;
# store raw["n_basis"] separately if metadata is desired.
actual_n_basis = len(pvalues_list)
n_basis_meta = int(raw["n_basis"]) if "n_basis" in raw else actual_n_basis
diag["itp_n_basis"] = actual_n_basis  # use actual length consistently
...
if actual_n_basis > 0:
    diag["itp_fraction_significant_0.05"] = float(n_sig / actual_n_basis)
else:
    diag["itp_fraction_significant_0.05"] = 0.0
```

### WR-03: ITP data silently discarded when `raw` contains both `"adjusted_pvalues"` and `"p_value"` / `"statistic"` keys

**File:** `python/fdars/advisor/aspects/inference.py:172`
**Issue:** The ITP branch guard is `if has_itp_keys and not has_test_result_keys`. When both ITP keys and TestResult keys are present simultaneously (`"adjusted_pvalues"` alongside `"p_value"` or `"statistic"`), the ITP branch is skipped entirely and the dict is routed to the TestResult path. All ITP data is silently discarded — no warning, no log, no exception. The routing-precedence comment at lines 145–148 documents `TestResult` winning over `ToleranceBand`, but says nothing about `TestResult` winning over ITP. There is no test covering this ambiguous input. If a future fdars ITP result dict also carries a summary `p_value`, the advisor will silently emit wrong diagnostics.

**Fix:** Document the precedence explicitly in the routing comment and add a warning (or raise) when both key sets are detected:

```python
# At line 172 — before the ITP branch:
if has_itp_keys and has_test_result_keys:
    # Ambiguous: both ITP vector and TestResult scalar keys present.
    # Route to ITP branch (vector data is more specific than scalar summary).
    # Alternatively, raise ValueError here to force the caller to disambiguate.
    pass  # fall through to ITP branch below (or raise)

if has_itp_keys and not has_test_result_keys:
    ...
```

At minimum, add a comment and a test verifying the routing outcome. The current silent discard violates the "fail loudly" principle for pathological inputs.

### WR-04: `itp_detected_at_0.05` emits `False` (not `None`) for an empty `adjusted_pvalues` array — type contract inconsistency

**File:** `python/fdars/advisor/aspects/inference.py:207-208`
**Issue:** When `pvalues_list` is empty (i.e., `raw["adjusted_pvalues"] == []`), the detection block at line 207 sets `itp_detected_at_0.05 = False`. In the non-ITP paths (TestResult and ToleranceBand), the field is `None`. The docstring and type hints specify `bool or None`, with `None` meaning "not applicable". An empty p-value array is "not testable" — the correct sentinel is `None`, not `False`. `False` implies "we tested and found no significance," which is semantically incorrect when there was nothing to test.

```python
# Current (lines 202-208):
if pvalues_list:
    itp_min_p = float(min(pvalues_list))
    diag["itp_min_adjusted_pvalue"] = itp_min_p
    diag["itp_detected_at_0.05"] = bool(itp_min_p < _ALPHA)
else:
    diag["itp_min_adjusted_pvalue"] = None
    diag["itp_detected_at_0.05"] = False   # <-- should be None

# Fix:
else:
    diag["itp_min_adjusted_pvalue"] = None
    diag["itp_detected_at_0.05"] = None    # no data → unknown, not False
```

## Info

### IN-01: `itp_n_significant_0.05 = 0` is emitted even when `pvalues_list` is empty — numerically ambiguous alongside `itp_detected_at_0.05 = None` (after WR-04 fix)

**File:** `python/fdars/advisor/aspects/inference.py:211-213`
**Issue:** The `sig_indices` list comprehension runs unconditionally on `pvalues_list`, so when the array is empty, `n_sig = 0` is stored in `itp_n_significant_0.05`. After fixing WR-04 (setting `itp_detected_at_0.05 = None` for empty input), `itp_n_significant_0.05 = 0` alongside `itp_detected_at_0.05 = None` is inconsistent. Consider emitting `None` for all ITP scalars when `pvalues_list` is empty:

```python
# After line 192 (pvalues_list definition):
if not pvalues_list:
    diag["itp_min_adjusted_pvalue"] = None
    diag["itp_detected_at_0.05"] = None
    diag["itp_n_significant_0.05"] = None
    diag["itp_fraction_significant_0.05"] = None
    diag["itp_first_significant_basis"] = None
    return diag
```

This is a minor style point — `n_sig=0` for empty input is not mathematically wrong, it is just semantically muddled when paired with `None` detection fields.

---

_Reviewed: 2026-08-23T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
