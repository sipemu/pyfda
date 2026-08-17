---
phase: 34-advisor-extension
reviewed: 2026-08-17T00:00:00Z
depth: deep
files_reviewed: 6
files_reviewed_list:
  - python/fdars/advisor/aspects/inference.py
  - python/fdars/advisor/aspects/__init__.py
  - python/fdars/advisor/__init__.py
  - python/fdars/advisor/_prompts.py
  - python/fdars/mcp/server.py
  - tests/test_advisor_inference.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: resolved
---

# Phase 34: Code Review Report

**Reviewed:** 2026-08-17
**Depth:** deep
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Phase 34 adds the `inference` diagnostics aspect (ADV-03) as a faithful analog of the existing `scoring` aspect. The grounding invariant is upheld: `inference.py` contains no import of `fdars.inference` and performs no recomputation — it only echoes and type-casts caller-supplied values. Determinism and NumPy-scalar exclusion are correct. Guard-sync across `_supported`, `_DIAGNOSTICS_METHODS`, `_ASPECT_PRIMERS`, and the dispatch chain is complete and correct. `inference` is correctly absent from `_RUNNABLE_METHODS`. All significance flags use strict `<` (not `<=`), which is statistically correct and consistent with the primer description.

Two warnings and two info items follow. No blocker-level issues were found.

## Warnings

### WR-01: `build_diagnostics` docstring omits `"inference"` (and `"scoring"`) from the `method` parameter set

**File:** `python/fdars/advisor/__init__.py:97-98`
**Issue:** The `method` parameter's docstring literal enumerates twelve values ending at `"spm"` — both `"scoring"` (added in Phase 28) and `"inference"` (this phase) are missing. The `_supported` set on line 124 is authoritative at runtime, but the docstring is what users and MCP tool introspection see. A caller reading the docstring would not know `"inference"` is valid, and any docstring-scraping tooling (e.g. Sphinx, IDE hover) will show the stale list.
**Fix:** Update line 97-98 to add `"scoring"` and `"inference"` to the method set literal:
```python
method : {"alignment", "fpca", "basis", "smoothing", "clustering", "depth", \
"outliers", "classification", "represent", "regression", "regression_cv", \
"spm", "scoring", "inference"}
```

### WR-02: `server.py` docstring says "twelve supported aspects" but `_DIAGNOSTICS_METHODS` now has fourteen

**File:** `python/fdars/mcp/server.py:112-115`
**Issue:** The `fdars_build_diagnostics` tool docstring reads `"One of the twelve supported aspects (_DIAGNOSTICS_METHODS)"` and lists twelve names, omitting `"scoring"` (Phase 28) and `"inference"` (this phase). The frozenset on line 63-82 is authoritative, but the tool docstring is the contract surfaced to MCP clients. An MCP host that introspects the tool description will advertise an incomplete method list, causing callers to pass `method="inference"` without knowing it is accepted.
**Fix:** Update lines 112-115 to `"fourteen"` and add both omitted entries to the list:
```
One of the fourteen supported aspects (``_DIAGNOSTICS_METHODS``):
``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
``'clustering'``, ``'depth'``, ``'outliers'``, ``'classification'``,
``'represent'``, ``'regression'``, ``'regression_cv'``, ``'spm'``,
``'scoring'``, ``'inference'``.
```

## Info

### IN-01: Ambiguous input dict (has both `p_value` and `half_width`) silently takes the TestResult path with `half_width` ignored

**File:** `python/fdars/advisor/aspects/inference.py:123-138`
**Issue:** The shape-detection condition is:
```python
has_test_result_keys = "p_value" in raw or "statistic" in raw
has_tolerance_band_keys = "half_width" in raw and "center" in raw
```
The ToleranceBand branch is only entered when `not has_test_result_keys`, so a dict containing both `p_value` and `half_width`/`center` silently routes to the TestResult path with `half_width` and `center` ignored. This is unlikely to occur with real fdars outputs (TestResult and ToleranceBand are disjoint in practice), but the behavior is undocumented in the docstring and there is no test for it. No incorrect output is produced — the TestResult path is the correct dominant shape — but a caller mixing shapes would get no warning.
**Fix:** Low priority. Either add a one-line comment in the shape-detection block noting that TestResult takes priority when both key sets are present, or add an assertion/log when `has_tolerance_band_keys` is also true in the TestResult branch.

### IN-02: Test suite has no coverage for `p_value` exactly at a threshold boundary (0.01, 0.05, 0.10)

**File:** `tests/test_advisor_inference.py`
**Issue:** The test fixtures use `p_value` values well away from the three alpha boundaries (0.004, 0.03, 0.62). The strict `<` comparison is correct statistically, but the exact-boundary behavior (`p_value = 0.05` should yield `significant_at_0.05 = False` and `strongest_significance_level = None`) is untested. Given the docstring says `p_value < alpha`, the implementation is correct, but a future maintainer changing `<` to `<=` would not be caught by any existing test.
**Fix:** Add a parameterized or inline test for each of the three exact-threshold cases, e.g.:
```python
def test_significance_exact_boundary_0_05(self):
    """p_value == 0.05: NOT significant at 0.05 (strict <)."""
    from fdars.advisor import build_diagnostics
    diag = build_diagnostics({"statistic": 1.0, "p_value": 0.05, "n_perm": 999},
                             method="inference")
    assert diag["significant_at_0.05"] is False
    assert diag["strongest_significance_level"] is None
```

---

_Reviewed: 2026-08-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
