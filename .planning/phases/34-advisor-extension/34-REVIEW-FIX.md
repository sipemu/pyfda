---
phase: 34-advisor-extension
fixed_at: 2026-08-17T00:00:00Z
review_path: .planning/phases/34-advisor-extension/34-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 34: Code Review Fix Report

**Fixed at:** 2026-08-17
**Source review:** .planning/phases/34-advisor-extension/34-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: `build_diagnostics` docstring drift — `method` parameter enumeration

**Files modified:** `python/fdars/advisor/__init__.py`
**Commit:** 555cf7c
**Applied fix:** Added `"scoring"` and `"inference"` to the `method` parameter's set literal in the NumPy-style docstring (line 97-99), replacing the twelve-value list that ended at `"spm"` with a fourteen-value list on three continuation lines matching the review suggestion.

### WR-02: MCP tool docstring drift — `fdars_build_diagnostics` lists twelve instead of fourteen

**Files modified:** `python/fdars/mcp/server.py`
**Commit:** 555cf7c
**Applied fix:** Changed `"twelve"` to `"fourteen"` in the parameter description and appended ``'scoring'``, ``'inference'`` to the backtick-quoted method list, so the tool docstring matches `_DIAGNOSTICS_METHODS` (14 members).

### IN-01: Undocumented routing precedence when input dict has both TestResult and ToleranceBand keys

**Files modified:** `python/fdars/advisor/aspects/inference.py`
**Commit:** 555cf7c
**Applied fix:** Added a four-line `#` comment immediately after the `has_tolerance_band_keys` assignment (lines 125-128) documenting that TestResult takes priority when both key sets are present, and that this is intentional because fdars TestResult and ToleranceBand are disjoint outputs in practice. No behavior change.

### IN-02: No coverage for `p_value` exactly at significance threshold boundaries

**Files modified:** `tests/test_advisor_inference.py`
**Commit:** 555cf7c
**Applied fix:** Added `TestInferenceExactBoundary` class with four tests pinning the strict-`<` semantics:
- `test_exact_0_05_not_significant`: `p_value == 0.05` yields `significant_at_0.05 is False`, `significant_at_0.10 is True`, `strongest_significance_level == 0.10`
- `test_just_below_0_05_is_significant`: `p_value == 0.0499` yields `significant_at_0.05 is True`
- `test_exact_0_01_not_significant`: `p_value == 0.01` yields `significant_at_0.01 is False`, `significant_at_0.05 is True`
- `test_exact_0_10_not_significant`: `p_value == 0.10` yields all three flags `False`, `strongest_significance_level is None`

Note: the initial test draft incorrectly expected `strongest_significance_level is None` for `p_value == 0.05`. This was caught by running the suite before committing (0.05 < 0.10 so level 0.10 applies). The test was corrected to assert `significant_at_0.10 is True` and `strongest_significance_level == pytest.approx(0.10)`.

## Verification

Verification ran in the isolated worktree (`gsd-reviewfix/34-942812`) against the main-checkout venv (`.venv`), which holds the compiled `fdars._native` extension. The worktree has no `node_modules`; Python tests were run by invoking pytest from the main checkout (`/home/simonm/projects/rust/pyfda`) with the worktree test file passed as an explicit path for the inference module.

**Full suite result:** 560 passed, 4 skipped (556 pre-existing passes + 4 new boundary tests).

---

_Fixed: 2026-08-17_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
