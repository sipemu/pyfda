---
phase: 51-comparative-method-selection
plan: "01"
subsystem: advisor
tags: [compare-methods, deterministic-ranking, offline-core, tracer, COMPARE-01, COMPARE-03]
dependency_graph:
  requires: [advisor._schema, advisor.__init__ (build_diagnostics)]
  provides: [fdars.advisor.compare_methods (offline ranking core)]
  affects: [Plan 02 (LLM narration path), Plan 03 (MCP tool fdars_compare_methods)]
tech_stack:
  added: []
  patterns:
    - "Metric registry (_METRIC_REGISTRY) mapping metric key → direction (higher/lower)"
    - "Dual-input normalizer: pre-built diagnostics dicts + raw result dicts via build_diagnostics"
    - "Fail-closed family + metric-presence guard before sort (COMPARE-03)"
    - "Stable sort with index tie-break for determinism (COMPARE-01)"
key_files:
  created:
    - python/fdars/advisor/_compare_methods.py
    - tests/test_compare_methods.py
  modified:
    - python/fdars/advisor/__init__.py
decisions:
  - "_METRIC_REGISTRY includes 12 keys across 7 task families (all keys verified against shipped diagnostics builders)"
  - "Family-conflict check moved before metric resolution so mixed-family inputs get the correct ValueError before a fallback default-metric lookup fails"
  - "cumulative_variance_explained (fpca) is a list; _extract_metric_value takes the last element as the ranking scalar"
  - "Explicit caller-supplied metric validated against registry before the commensurability guard (T-51-04: no code path from arbitrary metric strings)"
metrics:
  duration_seconds: 362
  completed_date: "2026-08-24"
  tasks_completed: 3
  commits: 1
estimate:
  tokens: 62000
actuals:
  tokens: 23500
  tasks: 3
  commits: 1
status: complete
---

# Phase 51 Plan 01: Deterministic compare_methods() Offline Core Summary

Delivered the TRACER: deterministic offline ranking core for `compare_methods()` (offline path only, `run_llm=False`). The winner is the top of an fdars-computed sort — the LLM is never involved. Same inputs always yield the same winner (stable insertion-order tie-break). Incommensurable inputs fail closed with `ValueError` before any ranking is produced.

## What Was Built

### `python/fdars/advisor/_compare_methods.py`

New module implementing:

- **`_METRIC_REGISTRY`** — 12 metric keys across 7 task families, each mapped to `"higher"` or `"lower"`. All keys verified to exist in the shipped `aspects/*.py` diagnostics builders (e.g. `mean_amplitude_separation` from `clustering.py`, `optimal_gcv` from `smoothing.py`, `r_squared` from `regression.py`).
- **`_DEFAULT_METRIC_BY_FAMILY`** — per-family canonical default metric key (clustering→`mean_amplitude_separation`, smoothing→`optimal_gcv`, basis→`optimal_edf`, regression_cv→`min_cv_error`, regression→`r_squared`, scoring→`functional_mse`, fpca→`cumulative_variance_explained`).
- **`_normalize_candidates()`** — accepts three input forms: `{label: value}` dict, `[(label, value)]` tuples, or `[{"label": ..., "value": ...}]` spec dicts. Pre-built diagnostics dicts (identified by presence of `"method"` key) pass through unchanged; raw result dicts are passed to `build_diagnostics(value, method)`.
- **`_assert_commensurable()`** — fail-closed guard: (1) rejects mixed task families; (2) rejects any candidate where the resolved metric key is absent or None, naming the offending label(s).
- **`_rank()`** — deterministic sort using registry direction + stable insertion-order tie-break. Unknown metric keys raise `ValueError` (T-51-04).
- **`compare_methods()`** — public entry point. Offline path (`run_llm=False`): normalise → family check → metric resolution (with registry validation for explicit keys) → commensurability guard → sort → return `{method, metric, ranking, winner}`. `run_llm=True` raises `NotImplementedError` (Plan 02 hook).

### `python/fdars/advisor/__init__.py`

Added `compare_methods` to `__all__` and imported it from `_compare_methods` (mirrors the `_schema` re-export style; no LLM/provider import at module load time).

### `tests/test_compare_methods.py`

21 offline tests covering:
- `test_ranking_is_deterministic` — json.dumps equal across two calls
- `test_winner_is_top_of_sort` — winner equals `ranking[0]["label"]` and metric extremum
- `test_winner_is_lowest_for_lower_is_better` — lower-is-better direction verified
- `test_dual_input_specs_and_precomputed` — mix of pre-built diagnostics dicts
- `test_dual_input_raw_result_dict` — raw regression result dict → build_diagnostics → ranking
- `test_labeled_output_keyed_by_label` — labels preserved in output
- `test_output_schema_shape` — `{method, metric, ranking, winner}` shape
- `test_compare_methods_in_all` — `compare_methods` in `fdars.advisor.__all__`
- `test_default_metric_resolved_by_family` — per-family default used when no metric given
- `test_explicit_metric_overrides_default` — caller metric overrides default
- `test_reject_mixed_task_families` — clustering + smoothing → ValueError
- `test_reject_missing_metric_on_any_candidate` — offending label named in error
- `test_reject_missing_metric_names_all_offenders` — all offending labels named
- `test_commensurable_passes` — valid same-family candidates rank without error
- `test_unknown_metric_raises` — unregistered metric → ValueError naming "metric registry"
- `test_guard_runs_before_sort` — mixed-family comparison never returns a ranking
- `test_core_is_llm_free` — `_compare_methods.py` has no module-level anthropic/providers import
- `test_stable_tiebreak_by_candidate_order` — tied metrics resolve by insertion order
- `test_stable_tiebreak_is_deterministic` — repeated calls on tied inputs yield same winner
- `test_spec_driven_build_diagnostics_path` — raw regression results exercised offline
- `test_full_suite_offline_no_api_key` — confirms no API key needed

## Verification Results

```
.venv/bin/python -m pytest tests/test_compare_methods.py -q
21 passed in 0.30s

.venv/bin/python -m pytest tests/test_compare_methods.py -q -k "deterministic or winner or dual_input or labeled"
7 passed in 0.23s

.venv/bin/python -m pytest tests/test_compare_methods.py -q -k "reject or commensurable"
4 passed in 0.23s

Full suite (837 tests): 837 passed, 7 skipped
```

## Deviations from Plan

### Auto-fixed: family-conflict check ordering

**Found during:** Task 1 (tracer) implementation and test run.

**Issue:** Original implementation resolved the metric default (`_DEFAULT_METRIC_BY_FAMILY[family]`) before calling `_assert_commensurable`. When candidates span two families, `family` becomes `""`, triggering the "no default for family" ValueError rather than the intended "multiple task families" ValueError. The `test_reject_mixed_task_families` test caught this.

**Fix:** Moved the family-conflict check (extracting distinct `method` values across blocks) to occur immediately after normalization, BEFORE metric resolution. The commensurability guard function `_assert_commensurable` retains its own family check as a secondary safety net for callers who invoke it directly (e.g. from Plan 02's LLM path).

**Rule:** Rule 1 (auto-fix bug).

### Auto-added: extended `_METRIC_REGISTRY`

**Found during:** Task 1 test writing — `test_explicit_metric_overrides_default` uses `functional_mae` as an override metric.

**Issue:** Plan specified 7 minimum registry keys; `functional_mae` (and other scoring metrics: `functional_mape`, `functional_msle`, `functional_explained_variance`, `mean_phase_separation`) are real keys in the shipped diagnostics builders but were not in the minimum set.

**Fix:** Extended `_METRIC_REGISTRY` to 12 keys — added `functional_mae`, `functional_mape`, `functional_msle`, `functional_explained_variance` (all from `scoring.py`) and `mean_phase_separation` (from `clustering.py`). All keys verified against `aspects/*.py` sources.

**Rule:** Rule 2 (auto-add missing critical functionality — registry completeness is a correctness requirement for the metric-validation guard T-51-04).

## Known Stubs

None — all plan goals achieved in the offline path. `run_llm=True` raises `NotImplementedError` as the Plan 02 hook; this is intentional, not a stub.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Self-Check: PASSED

| Artifact | Status |
|----------|--------|
| `python/fdars/advisor/_compare_methods.py` | FOUND |
| `tests/test_compare_methods.py` | FOUND |
| Commit `07435b8` | FOUND |
| `compare_methods` in `fdars.advisor.__all__` | VERIFIED |
| Determinism (same inputs → same winner) | VERIFIED |
| Winner == ranking[0]["label"] | VERIFIED |
| Fail-closed guard (COMPARE-03) | VERIFIED |
| LLM-free offline core (COMPARE-01) | VERIFIED |
| Full suite 837 tests pass | VERIFIED |
