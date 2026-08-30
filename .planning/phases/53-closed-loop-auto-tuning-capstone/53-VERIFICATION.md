---
phase: 53-closed-loop-auto-tuning-capstone
verified: 2026-08-30T21:00:00Z
status: passed
score: 15/15 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 53: Closed-Loop Auto-Tuning CAPSTONE Verification Report

**Phase Goal:** An autonomous bounded tuning loop (propose→apply→re-run fdars→compare→check budget→iterate); Python API auto_tune() (LLM structured numeric delta) + LLM-free MCP fdars_auto_tune (heuristic); compute path LLM-free; grounding invariant holds.
**Verified:** 2026-08-30T21:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | run_tuning_loop() terminates at max_steps with always-improve mock (stop_reason='budget', n_steps=2 at max_steps=2) | ✓ VERIFIED | test_budget_exhaustion passes; step>=max_steps checked FIRST at line 511 of _tuning.py before any propose_fn call |
| 2 | K=3 consecutive non-improvements triggers stop_reason='converged' | ✓ VERIFIED | test_convergence passes; n_steps=2 confirmed live (initial_target not None path) |
| 3 | Param revisit triggers stop_reason='oscillation' | ✓ VERIFIED | test_oscillation_param_revisit passes; _round_param + visited_params set verified in code |
| 4 | _UnparseableProposalError exits immediately with stop_reason='parse_failure' and n_steps=0; proposer called exactly once, no retry | ✓ VERIFIED | test_parse_failure passes; live smoke confirms n_steps=0 on first-step parse_failure |
| 5 | clustering degenerate cluster (min cluster_sizes < 2) stops loop with stop_reason='guard_stop' and non-empty guard_violations while target was improving (Goodhart) | ✓ VERIFIED | test_guard_stop_clustering passes; isinstance-list guard at _tuning.py:253; live smoke confirms |
| 6 | Two identical (propose_fn, initial params, mocked diagnostics) calls produce equal TuningTrace field dicts (determinism) | ✓ VERIFIED | test_determinism passes; live smoke confirms equal dicts |
| 7 | TuneProposal/TuningStep/TuningTrace/TuneResult importable and JSON-serialisable under both pydantic and ImportError-fallback | ✓ VERIFIED | test_tune_schema_json_serialisable passes; both branches present in _schema.py; live round-trip confirmed |
| 8 | Recommendation.parameter_delta defaults to None; existing five-field Recommendation construction unchanged | ✓ VERIFIED | test_recommendation_parameter_delta_optional passes; backward-compat live confirmed |
| 9 | auto_tune() LLM propose_fn reads parameter_delta.new_value (schema-validated), clamps to range before any fdars call, raises _UnparseableProposalError on absent/wrong-param, no second advise() call | ✓ VERIFIED | test_auto_tune_parse_failure_no_retry, test_auto_tune_clamps_above_range, test_auto_tune_clamps_below_range all pass; code path verified in __init__.py lines 812-841 |
| 10 | parameter_proposal system-prompt clause contains explicit no-numeric-prediction STRICT PROHIBITION for expected_effect; all five prior task families unchanged | ✓ VERIFIED | test_advisor_prompts_parameter_proposal suite passes; _prompts.py line 434: 'STRICT PROHIBITION'; five prior families verified live |
| 11 | fdars_auto_tune MCP tool: mcp/_tuning.py and server.py handler contain zero 'advise' token (LLM-free invariant confirmed by runtime-built token scan) | ✓ VERIFIED | test_auto_tune_does_not_import_advise passes; grep-0 verified live for both 'advise' and 'anthropic' tokens |
| 12 | fdars_auto_tune enforces max_steps hard cap of 20 (ValueError above 20) and validates method against _RUNNABLE_METHODS | ✓ VERIFIED | test_max_steps_hard_cap passes; live confirmed ValueError with '20' in message |
| 13 | fdars_auto_tune returns by-reference: all values in result dict are str/int/float/bool/None (no arrays) | ✓ VERIFIED | test_returns_by_reference_no_arrays passes |
| 14 | guard-sync no-op: _RUNNABLE_METHODS=6, _DIAGNOSTICS_METHODS=14 after adding fdars_auto_tune | ✓ VERIFIED | test_guard_sync_still_no_op passes; live: _RUNNABLE_METHODS=['alignment','basis','clustering','depth','fpca','smoothing'] (6), _DIAGNOSTICS_METHODS=14 |
| 15 | Grounding invariant holds: _METRIC_REGISTRY and _extract_metric_value imported from _compare_methods (no local direction dict); list-valued cumulative_variance_explained extracted via _extract_metric_value | ✓ VERIFIED | import statement at _tuning.py line 34; no local direction dict found; live fpca list-extraction returns last element (0.92 from [0.5,0.7,0.85,0.92]) |

**Score:** 15/15 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/advisor/_tuning.py` | Loop core, _PARAM_REGISTRY, _UnparseableProposalError, helpers | ✓ VERIFIED | 725 lines; all helpers present; 6-method registry with correct tuneable flags |
| `python/fdars/advisor/_schema.py` | TuneProposal/TuningStep/TuningTrace/TuneResult + Recommendation.parameter_delta | ✓ VERIFIED | Both pydantic and ImportError-fallback branches implemented |
| `python/fdars/advisor/__init__.py` | auto_tune() + _make_llm_propose_fn in __all__ | ✓ VERIFIED | auto_tune in __all__ at line 71; LLM closure at lines 753-842 |
| `python/fdars/advisor/_prompts.py` | parameter_proposal task clause with STRICT PROHIBITION | ✓ VERIFIED | Clause at lines 414-447 with explicit no-numeric-prediction prohibition |
| `python/fdars/mcp/_tuning.py` | _heuristic_step + _make_heuristic_propose_fn + run_tuning_loop_mcp | ✓ VERIFIED | 382 lines; gradient-sign + bisection; log-scale lambda_; int rounding |
| `python/fdars/mcp/server.py` | fdars_auto_tune @mcp.tool (max_steps cap 20, method validation) | ✓ VERIFIED | Handler at line 590; max_steps>20 raises ValueError |
| `tests/test_advisor_tuning.py` | Offline test suite for all 5 stop reasons + determinism + guard | ✓ VERIFIED | 18 tests, all pass |
| `tests/test_advisor_schema.py` | Schema import and JSON-serialisability tests | ✓ VERIFIED | 7 tests, all pass |
| `tests/test_advisor_tuning_llm.py` | LLM path tests with FakeProvider (offline) | ✓ VERIFIED | 14 tests, all pass |
| `tests/test_mcp_tuning.py` | MCP tool tests (LLM-free scan, determinism, cap, by-reference, guard-sync) | ✓ VERIFIED | 10 tests, all pass |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| run_tuning_loop | budget check | step>=max_steps BEFORE propose_fn | ✓ WIRED | Line 511 is the first action in the while-True loop body; confirmed by code read and test |
| run_tuning_loop | _METRIC_REGISTRY direction | imported from _compare_methods | ✓ WIRED | Line 34: `from fdars.advisor._compare_methods import _METRIC_REGISTRY, _extract_metric_value` |
| run_tuning_loop | _extract_metric_value | list-valued targets via _extract_target delegate | ✓ WIRED | _extract_target delegates to _extract_metric_value at line 176 |
| _round_param | visited_params set | 4 significant figures for floats | ✓ WIRED | Lines 160-164; int exact, float 4 sig figs |
| _check_guards | cluster_sizes | isinstance-list guard before min() | ✓ WIRED | Line 253: `isinstance(sizes, list) and len(sizes) > 0` before `min(sizes)` |
| auto_tune | _make_llm_propose_fn | advise(task='parameter_proposal') reads parameter_delta | ✓ WIRED | Lines 802-841; only new_value (clamped) returns to loop core |
| auto_tune | _UnparseableProposalError | absent/wrong-param raises immediately | ✓ WIRED | Lines 818, 826, 839: three exit paths, no retry |
| fdars_auto_tune | run_tuning_loop_mcp | delegation with no inlined loop logic | ✓ WIRED | server.py line 735: `return run_tuning_loop_mcp(...)` |
| mcp/_tuning.py | advisor._tuning | deferred import of run_tuning_loop | ✓ WIRED | Lines 252-258: deferred import inside run_tuning_loop_mcp body |
| mcp/_tuning.py | (nothing from advisor LLM path) | no advise/provider import | ✓ WIRED | grep-0 confirmed: zero 'advise' token in non-comment lines |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| run_tuning_loop | target direction | _METRIC_REGISTRY (imported from _compare_methods) | Yes — dict lookup | ✓ FLOWING |
| run_tuning_loop | new_val | propose_fn return → clamp | Yes — clamped numeric | ✓ FLOWING |
| _check_guards | guard_violations | Python deterministic rules over diagnostics dict | Yes | ✓ FLOWING |
| auto_tune | parameter_delta.new_value | Recommendation.parameter_delta field from advise() response | Yes — schema-validated | ✓ FLOWING |
| run_tuning_loop_mcp | trace_id | registry.store_result(trace_dict) | Yes — real registry handle | ✓ FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Budget terminates at max_steps=2 | test_budget_exhaustion (named test) | PASS | ✓ PASS |
| K=3 convergence | test_convergence (named test) | PASS | ✓ PASS |
| Param revisit = oscillation | test_oscillation_param_revisit (named test) | PASS | ✓ PASS |
| parse_failure exits n_steps=0, proposer called once | test_parse_failure (named test) | PASS | ✓ PASS |
| Guard stops degenerate cluster while target improving | test_guard_stop_clustering (named test) | PASS | ✓ PASS |
| Determinism: identical inputs → identical traces | test_determinism (named test) | PASS | ✓ PASS |
| LLM-free token scan (mcp/_tuning.py) | test_auto_tune_does_not_import_advise (named test) | PASS | ✓ PASS |
| max_steps=21 raises ValueError | test_max_steps_hard_cap (named test) | PASS | ✓ PASS |
| By-reference: result values are scalars/handles only | test_returns_by_reference_no_arrays (named test) | PASS | ✓ PASS |
| Guard-sync: _RUNNABLE_METHODS=6, _DIAGNOSTICS_METHODS=14 | test_guard_sync_still_no_op (named test) | PASS | ✓ PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| TUNE-01 | 53-01 | Shared _tuning.py loop core with injectable propose_fn, fully offline-testable without API key | ✓ SATISFIED | run_tuning_loop has _run_method/_build_diagnostics test seams; 49 tests pass offline |
| TUNE-02 | 53-01 | Bounded termination — max_steps, convergence, oscillation; loop never runs unbounded | ✓ SATISFIED | 5 stop reasons tested; budget-first confirmed at line 511 before propose_fn |
| TUNE-03 | 53-02 | auto_tune() LLM proposals via schema-validated numeric parameter_delta — never parsed from prose; LLM never sets number directly in numeric path | ✓ SATISFIED | Clamped new_value only numeric contribution; STRICT PROHIBITION in prompt; 14 offline LLM tests pass |
| TUNE-04 | 53-03 | fdars_auto_tune MCP tool uses heuristic (LLM-free) proposal; provably LLM-free MCP boundary | ✓ SATISFIED | grep-0 for 'advise' token; file-scan test passes; 10 MCP tests pass |
| TUNE-05 | 53-01 | Optional guard diagnostics detect off-target degradation (Goodhart) during tuning | ✓ SATISFIED | _check_guards with 4 rule types; isinstance-list guard for cluster_sizes; Goodhart test passes |
| TUNE-06 | 53-01 | TuningTrace/TuneProposal/TuneResult schemas + optional Recommendation.parameter_delta, backward-compatible | ✓ SATISFIED | Twin-definition (pydantic + ImportError fallback); parameter_delta defaults None; backward compat confirmed |

All 6 TUNE requirements satisfied. REQUIREMENTS.md marks all as complete.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | No TBD/FIXME/XXX found in any phase-modified file | — | — |

No stub patterns, empty implementations, or unresolved debt markers found in any of the 10 phase-modified files.

---

### Human Verification Required

None. All truths are verified programmatically. No visual, real-time, or external-service behavior involved.

---

### Gaps Summary

None. All 15 must-have truths verified against actual codebase. All 6 TUNE requirements satisfied. All 49 targeted tests pass. The phase goal is fully achieved.

---

## Summary of Hard Constraint Verification

**TUNE-01/02 — Bounded loop:**
- `step >= max_steps` checked at line 511, the FIRST action in the while-True loop body, before any `propose_fn` call.
- Five stop reasons confirmed: budget, converged, oscillation (revisit + ping-pong), guard_stop, parse_failure.
- `_UnparseableProposalError` exits immediately with `n_steps=0`; proposer not called a second time.

**TUNE-03 — LLM numeric path:**
- LLM's sole numeric contribution: `Recommendation.parameter_delta.new_value`, schema-validated, then `max(lo, min(hi, raw_val))` clamped at `__init__.py:832` before reaching `run_tuning_loop`.
- Missing/wrong-param `parameter_delta` → `_UnparseableProposalError` → `parse_failure`; no second `advise()` call.
- `parameter_proposal` clause contains `STRICT PROHIBITION` forbidding numeric predictions in `expected_effect`.
- `advise()` called once per step; the loop core, not the LLM, drives all numeric decisions.

**TUNE-04 — LLM-free MCP path:**
- `grep-0` confirmed: `advise` and `anthropic` tokens absent from `mcp/_tuning.py` non-comment lines.
- `fdars_auto_tune` handler in `server.py` delegates entirely to `run_tuning_loop_mcp`; no advise import.
- `max_steps > 20` → `ValueError` at tool boundary (line 708).
- `_RUNNABLE_METHODS = 6`, `_DIAGNOSTICS_METHODS = 14` unchanged (guard-sync no-op confirmed live).

**TUNE-05 — Guard/Goodhart:**
- Four guard rules implemented: `upper_fraction`, `relative_degradation_20pct`, `upper_threshold_0.5`, `min_cluster_size_ge_2`.
- `isinstance(sizes, list) and len(sizes) > 0` guard at line 253 prevents silent TypeError.
- `n_obs` sourced from dataset registry, not from diagnostics dict.
- `cumulative_variance_explained` extracted via `_extract_metric_value` (last element of list).

**TUNE-06 — Schemas:**
- Twin-definition pattern (pydantic + ImportError fallback) for all four new types.
- `Recommendation.parameter_delta` added as last field with `Optional[TuneProposal] = None`; existing five-field constructions valid without it.
- JSON round-trip confirmed.

**Grounding invariant:**
- `_METRIC_REGISTRY` and `_extract_metric_value` imported from `_compare_methods`; no local direction dict.
- All numeric results (target values, guard thresholds) come from fdars diagnostics, not LLM prose.

---

_Verified: 2026-08-30T21:00:00Z_
_Verifier: Claude (gsd-verifier)_
