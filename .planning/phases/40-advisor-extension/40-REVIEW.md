---
phase: 40-advisor-extension
reviewed: 2026-08-21T07:54:48Z
depth: deep
files_reviewed: 8
files_reviewed_list:
  - python/fdars/advisor/aspects/outliers.py
  - python/fdars/advisor/aspects/regression.py
  - python/fdars/advisor/aspects/classification.py
  - python/fdars/advisor/aspects/fpca.py
  - python/fdars/advisor/_prompts.py
  - tests/test_advisor_outliers_v6.py
  - tests/test_advisor_regression_v6.py
  - tests/test_advisor_group_b.py
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: issues_found
---

# Phase 40: Advisor Extension — Code Review

**Reviewed:** 2026-08-21T07:54:48Z
**Depth:** deep
**Files Reviewed:** 8
**Status:** issues_found (no blockers; 3 warnings, 3 info)

## Summary

Phase 40 extends four existing advisor aspect builders (`outliers`, `regression`, `classification`, `fpca`) to surface grounded scalar diagnostics for eight new v6.0 result shapes. The **grounding invariant is intact**: every emitted numeric value is a native Python `float`/`int`/`bool` reduction of an fdars-computed field; no numpy scalars leak; `json.dumps(sort_keys=True)` is byte-identical across calls; `_check_grounding` passes for all new branches; no new aspect keys are added; MCP guard files are untouched.

The full test suite (772 passed, 4 skipped, 0 failed) is green. The drift-lock test `test_diagnostics_methods_match_advisor_supported` remains green without any edit to `server.py`, `_runner.py`, or `advisor/__init__.py`.

The three warnings are all primer/key-name mismatches in `_prompts.py`: the LLM is instructed to reference diagnostic key names that do not exist in the output dict, which will cause the LLM to misinterpret muod and depthgram diagnostics. These are not fabrication violations (the grounding check validates cited numbers, not key names) but they actively mislead the LLM about what to cite, reducing advisor quality for both affected detectors.

---

## Warnings

### WR-01: Outlier primer references wrong key names for muod counts

**File:** `python/fdars/advisor/_prompts.py:63-66`
**Issue:** The `"outliers"` primer clause tells the LLM that muod exposes `n_magnitude_outliers` and `n_shape_outliers` as its three distinct outlier counts. But the code emits `n_muod_magnitude_outliers` and `n_muod_shape_outliers` (prefixed to avoid collision with tvdmss, which uses `n_magnitude_outliers` and `n_shape_outliers`). When the LLM follows the primer and looks for `n_magnitude_outliers` in a muod diagnostics dict, it will find the tvdmss slot which is `None` for a muod input. The actual muod counts under `n_muod_magnitude_outliers` and `n_muod_shape_outliers` will be ignored.

Primer text (stale):
```
"For muod: n_magnitude_outliers, n_shape_outliers, and n_amplitude_outliers "
"are the three distinct outlier counts; ..."
```

Actual emitted keys (outliers.py:174-175):
```python
diag["n_muod_magnitude_outliers"] = n_mag
diag["n_muod_shape_outliers"] = n_shp
diag["n_amplitude_outliers"] = n_amp
```

**Fix:** Update the primer to reference the actual key names:
```python
"For muod: n_muod_magnitude_outliers, n_muod_shape_outliers, and n_amplitude_outliers "
"are the three distinct outlier counts; magnitude_index_range, "
"shape_index_range, and amplitude_index_range summarise the respective "
"outlyingness score spans. "
```

---

### WR-02: Outlier primer references wrong key names for depthgram counts and ranges

**File:** `python/fdars/advisor/_prompts.py:67-70`
**Issue:** The primer says depthgram exposes `n_shape_outliers`, `n_magnitude_outliers`, `mbd_range`, and `mei_range`. The code emits `n_depthgram_shape_outliers`, `n_depthgram_magnitude_outliers`, `depthgram_mbd_range`, and `depthgram_mei_range` (all prefixed to avoid collision with outliergram's `mei_range`/`mbd_range` and tvdmss's `n_shape_outliers`/`n_magnitude_outliers`). The LLM will look for the unprefixed names, find `None` (the tvdmss slot), and miss the actual depthgram data.

Primer text (stale):
```
"For depthgram: n_shape_outliers and n_magnitude_outliers are the "
"depthgram-identified counts; mbd_range and mei_range span the "
"MBD and MEI depth scores. "
```

Actual emitted keys (outliers.py:238-247):
```python
diag["n_depthgram_shape_outliers"] = dg_n_shp
diag["n_depthgram_magnitude_outliers"] = dg_n_mag
diag["depthgram_mbd_range"] = [...]
diag["depthgram_mei_range"] = [...]
```

**Fix:** Update the primer clause:
```python
"For depthgram: n_depthgram_shape_outliers and n_depthgram_magnitude_outliers are the "
"depthgram-identified counts; depthgram_mbd_range and depthgram_mei_range span the "
"MBD and MEI depth scores. "
```

---

### WR-03: n_obs=0 edge case emits fabricated 0.0 fraction instead of None

**File:** `python/fdars/advisor/aspects/outliers.py:148-150, 243-245`
**Issue:** When `n_obs` is zero (degenerate input: empty score arrays), the tvdmss and depthgram fraction computations fall back to `0.0` rather than `None`. If outlier count lists are non-empty but the score array is empty (e.g. mismatched raw dict from a corrupt fdars result), a fraction of `0.0` is emitted even though the computation `n / 0` was avoided. `0.0` is not a grounded fdars-computed value in this case — it is a fabricated sentinel.

The muod branch correctly uses `None` for the same edge case (line 184-186).

Affected code:
```python
# tvdmss (lines 148-150)
else:
    diag["magnitude_outlier_fraction"] = 0.0   # wrong — should be None
    diag["shape_outlier_fraction"] = 0.0        # wrong — should be None

# depthgram (lines 243-245)
else:
    diag["depthgram_shape_outlier_fraction"] = 0.0    # wrong — should be None
    diag["depthgram_magnitude_outlier_fraction"] = 0.0 # wrong — should be None
```

**Fix:** Use `None` to be consistent with muod and to avoid emitting an ungrounded `0.0` for a degenerate case:
```python
else:
    diag["magnitude_outlier_fraction"] = None
    diag["shape_outlier_fraction"] = None
```
and
```python
else:
    diag["depthgram_shape_outlier_fraction"] = None
    diag["depthgram_magnitude_outlier_fraction"] = None
```

---

## Info

### IN-01: Function-level docstring in outliers.py not updated for new branches

**File:** `python/fdars/advisor/aspects/outliers.py:33-73`
**Issue:** The function docstring for `_build_outliers_diagnostics` says "Handles four result shapes (`detect_outliers_lrt`, `outliergram`, `magnitude_shape`, and `detect_outliers_lrt_with_dist`)" and the `Returns` section lists only the original 11 output fields. The four new branches (tvdmss, muod, sequential_transform_outliers, depthgram) and their 15+ new output keys are undocumented at the function signature level. The module-level docstring was updated (lists all 7 shapes), but it claims "Eight distinct result shapes" while listing 7 bullet points.

**Fix:** Update the function docstring `Returns` block to list the new output fields, and correct "four result shapes" in the one-liner. Correct the module docstring count ("Eight" → "Seven", or split `detect_outliers_lrt` / `detect_outliers_lrt_with_dist` into separate bullets to reach 8).

---

### IN-02: Function-level docstring in regression.py not updated for new branches

**File:** `python/fdars/advisor/aspects/regression.py:33-55`
**Issue:** The function docstring says the function handles `fregre_lm/pls/l1/huber/np/fosr/fosr_fpc` and the `Returns` section lists only the original 9 output fields. The `functional_glm` and `concurrent_regression` branches and their output keys (`deviance`, `aic`, `bic`, `log_likelihood`, `iterations`, `glm_ncomp`, `family`, `has_functional_glm`, `concurrent_residual_rms`, `concurrent_residual_max_abs`, `n_predictors`, `has_concurrent_regression`) are not documented.

**Fix:** Extend the `Returns` block to include the new fields and add `functional_glm`/`concurrent_regression` to the supported function list in the `Parameters` section.

---

### IN-03: check_no_numpy helper is duplicated across all three new test files

**File:** `tests/test_advisor_outliers_v6.py:23-33`, `tests/test_advisor_regression_v6.py:27-37`, `tests/test_advisor_group_b.py:24-34`
**Issue:** The `check_no_numpy` helper is copy-pasted verbatim into all three new test files and also exists in `test_advisor_inference.py`. This is already a known pattern from the precedent file, but the proliferation across 4 test files creates maintenance burden when the canonical pattern needs to change (e.g., to handle `np.generic` subclasses added in future NumPy versions).

**Fix:** Extract to a shared test helper module (e.g., `tests/_test_helpers.py`) and import from there, following the same pattern as `_utils.py` in the production code.

---

_Reviewed: 2026-08-21T07:54:48Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
