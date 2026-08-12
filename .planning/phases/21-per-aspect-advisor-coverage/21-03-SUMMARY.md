---
phase: 21-per-aspect-advisor-coverage
plan: "03"
subsystem: advisor/aspects
status: complete
tags: [advisor, aspects, represent, fpca, refactor, shared-helper, determinism]
completed: 2026-08-12

dependency_graph:
  requires:
    - 21-02  # outliers + classification builders; dispatcher pattern established
  provides:
    - "_utils._eigenvalues_to_variance_cumulative — imported by fpca.py (done) and spm.py (plan 21-05)"
    - "represent aspect — ASPECT-01 covered"
  affects:
    - "21-05 (spm.py imports _utils)"

tech_stack:
  added:
    - "advisor/aspects/_utils.py — shared NumPy helper module"
    - "advisor/aspects/represent.py — represent diagnostics builder"
  patterns:
    - "Attribute-first, dict-fallback input resolution for Fdata-like objects"
    - "Shared helper module pattern (_utils.py) for reusable NumPy logic"
    - "Output-preserving refactor: extract shared logic, keep all output fields identical"

key_files:
  created:
    - python/fdars/advisor/aspects/_utils.py
    - python/fdars/advisor/aspects/represent.py
  modified:
    - python/fdars/advisor/aspects/fpca.py  # refactored to use shared helper
    - python/fdars/advisor/__init__.py       # added "represent" to _supported + dispatch branch
    - tests/test_advisor.py                  # 5 new tests across 3 tasks

decisions:
  - "_utils.py created with single function (_eigenvalues_to_variance_cumulative) — grows as spm.py needs it"
  - "fpca refactor replaces only the np.cumsum(evr) line with the shared helper; all other logic unchanged"
  - "represent is a new method string (not an extension of basis/fpca) — operates on INPUT data, not method output"
  - "represent prompt clause was pre-existing in _prompts.py from prior planning; confirmed is_uniform_grid token present"
  - "Attribute-first resolution in represent builder: getattr(raw, 'data', None) before dict.get — handles both Fdata and dict without dict(raw) coercion"

estimate:
  tokens: 52000
  tasks: 3
  confidence: med

actuals:
  tokens: 17000   # chars/4 over files actually modified
  tasks: 3
  commits: 3
---

# Phase 21 Plan 03: _utils shared helper + fpca refactor + represent aspect — Summary

Established the `advisor/aspects/_utils.py` shared helper module with the canonical `_eigenvalues_to_variance_cumulative` function, refactored `fpca.py` to use it (output byte-identical after refactor), and implemented `represent` as a new method string (ASPECT-01) with full test coverage.

## What Was Built

### Task 1: _utils.py + fpca refactor

`python/fdars/advisor/aspects/_utils.py` — new shared helper module:
- `_eigenvalues_to_variance_cumulative(eigenvalues)` accepts already-scaled eigenvalues (no `/n-1` step), computes cumulative explained variance, returns `list[float]` with zero-sum guard (`[0.0]*n` when total ≤ 0). Used by `fpca.py` now; will be imported by `spm.py` in plan 21-05.

`python/fdars/advisor/aspects/fpca.py` — output-preserving refactor:
- Imports `_eigenvalues_to_variance_cumulative` from `_utils`
- Replaces the inline `[float(v) for v in np.cumsum(evr)]` with the shared helper
- All other fields (`n_components`, `n_obs`, `eigenvalues`, `explained_variance_ratio`, `total_variance`, `phase_leakage_indicator`, `phase_leakage_flagged`) are unchanged
- `test_fpca_output_unchanged_after_refactor` confirms byte-identical JSON output

### Task 2: represent builder + dispatch + prompt

`python/fdars/advisor/aspects/represent.py` — new aspect builder:
- `_build_represent_diagnostics(raw, **kwargs)` — pre-analysis data-quality check
- Accepts form A (dict with `"data"` + `"argvals"`) or form B (Fdata-like object with `.data`/`.argvals` attrs)
- Attribute-first, dict-fallback resolution: `getattr(raw, "data", None)` then `raw.get("data")`
- Computed fields: `n_obs`, `n_points`, `argvals_min/max`, `argvals_spacing_mean/std`, `is_uniform_grid`, `data_range_min/max/mean`
- `is_uniform_grid` logic: `spacing_std / spacing_mean < 0.01` when `spacing_mean > 0`, else `True`
- All values native Python types; `None` on missing/empty input

`python/fdars/advisor/__init__.py`:
- Added `"represent"` to `_supported` set
- Added lazy dispatch branch: `if method_lc == "represent": from fdars.advisor.aspects.represent import ...`

`python/fdars/advisor/_prompts.py` — represent clause was pre-existing:
- `_ASPECT_PRIMERS["represent"]` already present with `is_uniform_grid` token — confirmed working

### Task 3: determinism tests

Added to `tests/test_advisor.py`:
- `TestBuildDiagnosticsOffline.test_utils_eigenvalues_variance` — normal/zero-sum/single-element cases, all-float check
- `TestBuildDiagnosticsOffline.test_fpca_output_unchanged_after_refactor` — inline expected dict, byte-identical JSON assertion
- `TestBuildDiagnosticsOffline.test_represent_deterministic` — np.ones fixture (no RNG), dict + object form, byte-identical JSON, `check_no_numpy` walker, cross-form equality
- `TestRepresent.test_represent_dict_form_basic` — n_obs/n_points/is_uniform_grid/argvals_range assertions
- `TestRepresent.test_represent_fdata_like_form` — SimpleNamespace proxy; confirms equal output to dict form
- `TestRepresent.test_represent_prompt_clause` — is_uniform_grid present only for aspect='represent'
- `TestPrompts.test_prompt_represent_clause` — is_uniform_grid present, absent from base, differs from depth prompt

## Test Results

```
29 passed, 1 skipped (pre-existing LLM integration test skipped without API key)
Baseline was 22 passed, 1 skipped (start of Wave 3)
7 new tests added across 3 tasks
```

## fpca Behavior Unchanged Confirmation

The refactor replaces exactly one expression in `fpca.py`:

Before: `cum_list = [float(v) for v in np.cumsum(evr)]`
After:  `cum_list = _eigenvalues_to_variance_cumulative(eigenvalues)`

Both produce identical results because `_eigenvalues_to_variance_cumulative` applies the same logic: `evr = ev / total; return [float(v) for v in np.cumsum(evr)]`. The zero-sum guard path is also identical (returns `[0.0]*n` in both old and new code). The regression test `test_fpca_output_unchanged_after_refactor` verifies this with a fixed fixture and byte-identical JSON comparison.

## represent Determinism Confirmation

`test_represent_deterministic` uses `np.ones((20, 50))` + `np.linspace(0, 1, 50)` — no RNG. Two calls on the dict form produce identical dicts and byte-identical `json.dumps(sort_keys=True)`. Same for the Fdata-like object form. Both forms produce equal output to each other. No `np.generic` scalars leak through `check_no_numpy`.

## Deviations from Plan

None — plan executed exactly as written.

The `represent` clause (`is_uniform_grid` token) was already present in `_prompts.py` (written during the planning phase for the full Phase 21 scope). This was a no-op discovery — the clause was verified rather than added.

## Known Stubs

None. All fields in the `represent` builder are fully computed from the input data. No placeholders.

## Self-Check: PASSED

- FOUND: `python/fdars/advisor/aspects/_utils.py`
- FOUND: `python/fdars/advisor/aspects/represent.py`
- FOUND: commit ce9a47b (Task 1 — _utils + fpca refactor)
- FOUND: commit 3794a98 (Task 2 — represent builder + dispatch)
- FOUND: commit 06b6d28 (Task 3 — determinism tests)
