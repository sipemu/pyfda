---
phase: 51-comparative-method-selection
verified: 2026-08-24T00:00:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: null
---

# Phase 51: Comparative Method-Selection Verification Report

**Phase Goal:** A user can rank/pick among candidate methods; the winner is chosen by an fdars-computed deterministic sort (never the LLM), with the LLM narrating from per-candidate grounded diagnostics. Delivers compare_methods(), a "comparison" task family, and an LLM-free fdars_compare_methods MCP tool.
**Verified:** 2026-08-24
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | compare_methods(run_llm=False) returns a deterministic fdars-computed ranking; same inputs yield the identical winner across repeated calls (COMPARE-01) | ✓ VERIFIED | test_ranking_is_deterministic (21 passed); `json.dumps(r1) == json.dumps(r2)` asserted; stable sort with index tie-break in `_rank()` at line 277 |
| 2 | The winner is the top of the fdars sort — never chosen by an LLM; the deterministic core does not import anthropic or any provider at module level (COMPARE-01) | ✓ VERIFIED | Module-level imports in `_compare_methods.py`: only `from __future__ import annotations` and `from typing import Any`; `winner = ranking[0]["label"]` at line 299; test_core_is_llm_free passes |
| 3 | Candidates that do not share one task family, or where the ranking metric is absent from ANY candidate, are rejected with ValueError before any sort (COMPARE-03) | ✓ VERIFIED | `_assert_commensurable()` at line 189; family check at line 401 runs before `_rank()`; test_reject_mixed_task_families and test_reject_missing_metric_on_any_candidate pass |
| 4 | "comparison" task family in `_system_prompt()` narrates the fdars-computed ranking; LLM narration does NOT override the winner; winner is set from the sort before the LLM call and validated after (COMPARE-02, COMPARE-01 winner authority) | ✓ VERIFIED | `"comparison"` in `_supported_tasks` at line 284; winner captured at line 437 before any LLM call; `result["advice"] = advice` at line 502 does NOT overwrite `result["winner"]`; test_winner_set_before_llm_and_preserved and test_llm_cannot_override_winner pass |
| 5 | Diagnostics reach the LLM as a list of {label, diagnostics} blocks — never a flat-merged dict; `_check_grounding` runs per-candidate (COMPARE-02) | ✓ VERIFIED | `provenance_blocks` built as list of `{"label", "diagnostics"}` at lines 465–468; `for block in provenance_blocks: _check_grounding(advice, block["diagnostics"])` at lines 497–498; test_provenance_is_per_candidate_not_flat_merged and test_grounding_runs_per_candidate pass |
| 6 | `fdars_compare_methods` MCP tool is provably LLM-free (never imports or calls advise); `_compare_methods.py` file-scan clean; re-runs via the 6 _RUNNABLE_METHODS; rejects non-runnable candidate methods; returns by-reference (COMPARE-04) | ✓ VERIFIED | `python/fdars/mcp/_compare_methods.py` module-level imports: only `from __future__ import annotations` and `import sys`; no "advise" token anywhere in file; test_tool_never_imports_advise passes; test_rejects_method_not_in_runnable passes; test_returns_by_reference_no_arrays passes |
| 7 | Guard-sync no-op: _DIAGNOSTICS_METHODS unchanged (14), _RUNNABLE_METHODS unchanged (6) (COMPARE-04) | ✓ VERIFIED | `_RUNNABLE_METHODS` count = 6, `_DIAGNOSTICS_METHODS` count = 14 (confirmed by live import); test_guard_sync_still_no_op passes |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/advisor/_compare_methods.py` | Deterministic ranking core, metric registry, incommensurability guard | ✓ VERIFIED | 505 lines; _METRIC_REGISTRY (12 keys), _DEFAULT_METRIC_BY_FAMILY (7 families), _normalize_candidates, _assert_commensurable, _rank, compare_methods fully implemented |
| `compare_methods` in `fdars.advisor.__all__` | Exported symbol | ✓ VERIFIED | Line 68 in `__init__.py`; import confirmed at line 73 |
| `tests/test_compare_methods.py` | 21 offline determinism + guard tests | ✓ VERIFIED | 21 passed in 0.28s |
| `python/fdars/advisor/_prompts.py` | "comparison" task clause in `_system_prompt()` | ✓ VERIFIED | `"comparison"` in `_supported_tasks` at line 284; clause at lines 357–379 instructs narration-only, references winner being supplied by fdars |
| `python/fdars/advisor/_compare_methods.py` run_llm=True path | LLM narration with fdars-authoritative winner + per-candidate provenance | ✓ VERIFIED | Step 7 at lines 450–504 fully implemented; winner never derived from LLM output |
| `tests/test_compare_methods_advise.py` | 8 offline + 1 env-gated live tests | ✓ VERIFIED | 8 passed, 1 skipped (no API key) in 0.27s |
| `python/fdars/mcp/_compare_methods.py` | MCP re-run helper delegating to ranking core | ✓ VERIFIED | 218 lines; compare_methods_mcp fully implemented; delegates to `_rank_core(run_llm=False)`; by-reference return |
| `python/fdars/mcp/server.py` fdars_compare_methods | @mcp.tool wrapper, flat schema, LLM-free | ✓ VERIFIED | Lines 427–507; validates method against _RUNNABLE_METHODS before delegating; no provider/model arg; synchronous |
| `tests/test_mcp_compare_methods.py` | 7 tests covering ranking, by-reference, LLM-free, guard-sync | ✓ VERIFIED | 7 passed (plus 13 test_mcp_server.py) = 20 total in 90s |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `compare_methods()` | `build_diagnostics()` | `_normalize_candidates` local import at line 140; called when candidate value lacks "method" key | ✓ WIRED | Confirmed at line 182: `diag = build_diagnostics(value, method)` |
| ranking sort key | metric registry direction | `_METRIC_REGISTRY[metric]` at line 272; direction sets `reverse` flag for sort | ✓ WIRED | Deterministic winner confirmed by test |
| incommensurability guard | sort | Guard at line 434 (`_assert_commensurable`) runs before `_rank` at line 437 | ✓ WIRED | Mixed-family ValueError confirmed before ranking returns |
| `fdars_compare_methods` tool | `compare_methods_mcp` helper | Lazy import + call at lines 504–507 | ✓ WIRED | `from fdars.mcp._compare_methods import compare_methods_mcp` inside handler |
| `compare_methods_mcp` | `compare_methods(run_llm=False)` | `from fdars.advisor._compare_methods import compare_methods as _rank_core` at line 147 | ✓ WIRED | Single ranking implementation reused; no duplicate sort logic in MCP layer |
| deterministic winner (sort step 5) | result["winner"] field | Set at line 443 from `_rank()` return; never overwritten from LLM output | ✓ WIRED | Post-LLM code only sets `result["advice"]` at line 502; winner preserved |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `compare_methods()` winner | `winner` | `_rank(blocks, resolved_metric)[1]` — fdars sort | Yes — float from candidate diagnostics | ✓ FLOWING |
| `_rank()` metric_value | `val` | `_extract_metric_value(block["diagnostics"], metric)` — reads from diagnostics dict | Yes — real float/int scalar | ✓ FLOWING |
| `compare_methods_mcp` diagnostics | `diag` | `build_diagnostics(raw_result, method_lc, argvals=argvals)` — fdars computation | Yes — real fdars output | ✓ FLOWING |
| MCP return ranking | `ranking_by_ref` | `core_result["ranking"]` from `compare_methods(run_llm=False)` | Yes — result_id handles + scalar metric_value only | ✓ FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| 21 offline determinism + guard tests | `pytest tests/test_compare_methods.py -q` | 21 passed in 0.28s | ✓ PASS |
| 8 advise-path + 1 env-gated tests | `pytest tests/test_compare_methods_advise.py -q` | 8 passed, 1 skipped in 0.27s | ✓ PASS |
| 7 MCP + 13 existing MCP server tests | `pytest tests/test_mcp_compare_methods.py tests/test_mcp_server.py -q` | 20 passed in 90s | ✓ PASS |
| compare_methods in __all__ | `python -c "import fdars.advisor as a; assert 'compare_methods' in a.__all__"` | exits 0 | ✓ PASS |
| _RUNNABLE_METHODS=6, _DIAGNOSTICS_METHODS=14 | live import + len() check | 6 and 14 confirmed | ✓ PASS |
| comparison prompt narrates, not chooses winner | `_system_prompt("comparison")` contains "narrat", "winner", "not choose" | all True | ✓ PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| COMPARE-01 | Plan 01 + Plan 02 | compare_methods() returns deterministic fdars-computed ranking; winner is the sort result, never LLM-chosen; run_llm=True cannot override | ✓ SATISFIED | `_rank()` returns `ranking[0]["label"]` as winner; result["winner"] set before LLM call; result["advice"] added after, result["winner"] never re-assigned; mock tests confirm LLM narration naming a different winner is ignored |
| COMPARE-02 | Plan 02 | "comparison" task family narrates ranking with per-candidate labeled provenance; `_check_grounding` runs per-candidate | ✓ SATISFIED | "comparison" in `_supported_tasks`; provenance_blocks is a list of {label, diagnostics} blocks; `_check_grounding` loops per block; cross-candidate citation raises GroundingViolationError |
| COMPARE-03 | Plan 01 | Fail-closed incommensurability guard — mixed families or metric absent from any candidate → ValueError; no silent candidate dropping | ✓ SATISFIED | `_assert_commensurable()` and inline family check in `compare_methods()` at line 401; both conditions tested and passing |
| COMPARE-04 | Plan 03 | fdars_compare_methods MCP tool; provably LLM-free (never imports advise); re-runs via 6 _RUNNABLE_METHODS; rejects non-runnable methods; returns by-reference | ✓ SATISFIED | `python/fdars/mcp/_compare_methods.py` has zero "advise" references; `fdars_compare_methods` tool validates method against _RUNNABLE_METHODS; ranking returned as {ranking_id handle, result_id handles, scalar metric_values}; guard-sync no-op confirmed |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `python/fdars/advisor/_compare_methods.py` | 355–356 (docstring) | Stale docstring says "Plan 02 not yet implemented" for run_llm=True | INFO | Cosmetic only — the run_llm=True path IS fully implemented at lines 450–504; Plan 02 code was added in commit 8147d41 but the Plan 01 docstring text was not updated. No functional impact. |

No TBD/FIXME/XXX/HACK markers found in any phase-modified file. The stale docstring is informational only — the implementation is complete and all tests pass.

---

### Human Verification Required

None. All must-haves are verified programmatically with passing behavioral tests. The env-gated live test (`test_live_comparison_narration`) is correctly skipped offline and requires no human action for CI.

---

## Gaps Summary

No gaps. All 7 truths VERIFIED, all 4 requirements SATISFIED, all artifacts exist and are substantive and wired, all behavioral tests pass.

**One informational note:** The docstring in `python/fdars/advisor/_compare_methods.py` at lines 355–356 still reads "Plan 02 not yet implemented" for the `run_llm=True` path. This is a stale copy from Plan 01 (when run_llm=True was a NotImplementedError stub). Plan 02 completed the implementation in commit `8147d41` but did not update this docstring line. The code is correct; only the docstring is stale. Not a gap.

---

_Verified: 2026-08-24_
_Verifier: Claude (gsd-verifier)_
