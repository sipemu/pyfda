---
phase: 53-closed-loop-auto-tuning-capstone
plan: "03"
subsystem: mcp
tags: [mcp, auto-tuning, heuristic, llm-free, by-reference, determinism, guard-sync]

requires:
  - phase: 53-closed-loop-auto-tuning-capstone
    plan: "01"
    provides: run_tuning_loop + _PARAM_REGISTRY (shared loop core delegated to)

provides:
  - _heuristic_step + _make_heuristic_propose_fn (gradient-sign line search in mcp/_tuning.py)
  - run_tuning_loop_mcp (LLM-free MCP helper: resolves spec, builds heuristic, delegates to loop core, returns by-reference)
  - fdars_auto_tune @mcp.tool in server.py (validation + max_steps cap 20 + delegation)
  - test_mcp_tuning.py (LLM-free scan, determinism, cap, by-reference, guard-sync)

affects:
  - Phase 54 (eval harness can call fdars_auto_tune via trace_id for trace-level evaluation)

actuals:
  tokens: 14000
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Heuristic propose_fn: gradient-sign line search with bisection step-size decay (n_reversals from history)"
    - "Log-scale step: multiplicative factor=10/2^reversals with floor 1.01 for lambda_"
    - "Integer rounding: round-then-int at clamp boundary for n_basis/n_comp/k"
    - "LLM-free token discipline: docstrings avoid literal provider/advisor token sequences that would self-flag grep checks"
    - "By-reference return: TuningTrace stored via registry.store_result; only trace_id + scalar summary cross MCP boundary"

key-files:
  created:
    - python/fdars/mcp/_tuning.py
    - tests/test_mcp_tuning.py
  modified:
    - python/fdars/mcp/server.py

key-decisions:
  - "Heuristic step size decays with direction reversals: factor=10/2^n_reversals (log-scale), (hi-lo)/(10*2^n_reversals) (linear)"
  - "Initial step is always coarse-positive (log: *10; linear: +(hi-lo)/10); direction refinement starts from history[1:]"
  - "run_tuning_loop_mcp fills in the param default from spec if initial_params omits the tunable param key"
  - "final_target_value derived from final_diagnostics via _extract_target (authoritative) not from step trace history"
  - "LLM-free token discipline: docstrings rephrase to avoid literal 'advise'/'anthropic' sequences; verified by grep-0 check"
  - "fdars_auto_tune validates against _RUNNABLE_METHODS FIRST, then delegates; non-tuneable methods (alignment/depth) raise in run_tuning_loop_mcp"

metrics:
  duration: "12 minutes"
  completed: "2026-08-30"

status: complete

requirements-completed: [TUNE-04]
---

# Phase 53 Plan 03: MCP Tool + Heuristic propose_fn Summary

**LLM-free `fdars_auto_tune` MCP tool driving the wave-1 loop core with a deterministic gradient-sign heuristic (bisection step decay; log-scale lambda_; int rounding); file-scan + determinism + by-reference + guard-sync confirmed offline.**

## Performance

- **Duration:** ~12 minutes
- **Started:** 2026-08-30T20:30Z (approx)
- **Completed:** 2026-08-30T20:42Z (approx)
- **Tasks:** 3
- **Files created:** 2 / modified: 1

## Accomplishments

- `python/fdars/mcp/_tuning.py` — NEW: `_heuristic_step` (gradient-sign line search + bisection decay, log-scale for lambda_, int rounding), `_make_heuristic_propose_fn` (closure), `run_tuning_loop_mcp` (spec resolution, default fill, heuristic proposer, loop delegation, by-reference return)
- `python/fdars/mcp/server.py` — MODIFIED: `fdars_auto_tune @mcp.tool` added with flat scalar params (`lambda_/n_basis/n_comp/k/seed`), method validation against `_RUNNABLE_METHODS`, `max_steps` hard cap 20 (`ValueError`), delegation to `run_tuning_loop_mcp`; guard-sync no-op confirmed (_RUNNABLE_METHODS stays 6, _DIAGNOSTICS_METHODS stays 14)
- `tests/test_mcp_tuning.py` — NEW: 10 tests covering all TUNE-04 must-haves offline
- All 4 commits atomic; no blockers; zero regressions in existing MCP suite (21 tests pass)

## Task Commits

1. `371c78a` `feat(53-03): heuristic propose_fn + run_tuning_loop_mcp helper (LLM-free)` — Task 1
2. `458333c` `feat(53-03): add fdars_auto_tune @mcp.tool to server.py` — Task 2
3. `09ae1ad` `test(53-03): MCP tuning tests — LLM-free scan, determinism, cap, by-reference, guard-sync` — Task 3
4. `5460528` `fix(53-03): remove provider name from _tuning.py docstring to satisfy grep-0 check` — Rule 1 (bug: grep check would fail with provider name in docstring)

## Files Created/Modified

- `python/fdars/mcp/_tuning.py` — NEW: LLM-free heuristic helper (381 lines)
- `python/fdars/mcp/server.py` — MODIFIED: `fdars_auto_tune` tool added (+157 lines, -1)
- `tests/test_mcp_tuning.py` — NEW: 10 offline tests (329 lines)

## Decisions Made

- Heuristic step size decays with direction reversals: `factor = 10 / 2^n_reversals` (log-scale), `(hi-lo) / (10 * 2^n_reversals)` (linear). Floor: 1.01 (log), 1 (int linear), `(hi-lo)*1e-4` (float linear).
- Initial step is always coarse-positive (log: `*10`; linear: `+(hi-lo)/10`); direction refinement kicks in from `history[1:]`.
- `run_tuning_loop_mcp` fills in the tunable param default from `_PARAM_REGISTRY` spec if `initial_params` omits the key; this keeps the tool interface minimal.
- `final_target_value` is derived from `final_diagnostics` via `_extract_target` (authoritative) rather than from the step trace to correctly handle list-valued metrics (`cumulative_variance_explained`).
- LLM-free token discipline: docstrings rephrase `advise`/`anthropic` to avoid literal sequences that would self-flag grep-0 checks; this is an explicit design choice, not a workaround.
- `fdars_auto_tune` validates `_RUNNABLE_METHODS` first (tool boundary), then `run_tuning_loop_mcp` validates `tuneable=True` (spec boundary); alignment/depth raise at the spec boundary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed literal provider name from docstring**
- **Found during:** Task 3 verification (`grep -v '^#' | grep -c anthropic`)
- **Issue:** The module docstring contained the word "anthropic" (the provider name) in a line describing what NOT to import. While this is not a code-level LLM import, the plan's acceptance criterion requires `grep -c anthropic` to return 0 on all non-comment lines including docstrings.
- **Fix:** Rephrased docstring to "LLM advisor or any provider package" avoiding the literal sequence.
- **Files modified:** `python/fdars/mcp/_tuning.py`
- **Commit:** `5460528`

## Known Stubs

None — all 10 tests pass against the real fdars loop core with synthetic datasets (offline). The by-reference invariant, determinism, cap, and guard-sync are all verified against production-quality implementation.

## Threat Flags

None — the plan's threat model (T-53C-01 through T-53C-04) is fully mitigated:
- T-53C-01 (LLM leaking into MCP path): `mcp/_tuning.py` passes grep-0 for both `advise` and `anthropic` tokens; file-scan test enforces it.
- T-53C-02 (DoS via max_steps): hard cap 20 enforced at tool boundary; test_max_steps_hard_cap verifies.
- T-53C-03 (guard-sync drift): _RUNNABLE_METHODS and _DIAGNOSTICS_METHODS sizes asserted unchanged (6/14).
- T-53C-04 (arrays crossing MCP boundary): test_returns_by_reference_no_arrays confirms all values are str/int/float/bool/None.

## Self-Check: PASSED

**Files exist:**
- `[ -f python/fdars/mcp/_tuning.py ]` → FOUND
- `[ -f python/fdars/mcp/server.py ]` → FOUND (modified)
- `[ -f tests/test_mcp_tuning.py ]` → FOUND

**Commits exist (git log verified):**
- `371c78a` feat(53-03): heuristic propose_fn + run_tuning_loop_mcp — FOUND
- `458333c` feat(53-03): add fdars_auto_tune @mcp.tool — FOUND
- `09ae1ad` test(53-03): MCP tuning tests — FOUND
- `5460528` fix(53-03): remove provider name — FOUND

**Test results:**
- `tests/test_mcp_tuning.py` — 10 passed
- `tests/test_mcp_server.py` — passes (no regression, 21 total with compare_methods)
- `tests/test_mcp_compare_methods.py` — passes (no regression)
- LLM-free: `grep -v '^#' python/fdars/mcp/_tuning.py | grep -c anthropic` → 0
- LLM-free: `grep -v '^#' python/fdars/mcp/_tuning.py | grep -c "advise"` → 0
- Guard-sync: `_RUNNABLE_METHODS` = 6, `_DIAGNOSTICS_METHODS` = 14

## Issues Encountered

None beyond the docstring fix (Rule 1 auto-fix).

---
*Phase: 53-closed-loop-auto-tuning-capstone*
*Completed: 2026-08-30*
