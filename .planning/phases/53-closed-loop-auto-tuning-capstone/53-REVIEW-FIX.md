---
phase: 53-closed-loop-auto-tuning-capstone
fixed_at: 2026-08-30T14:00:00Z
review_path: .planning/phases/53-closed-loop-auto-tuning-capstone/53-REVIEW.md
iteration: 1
findings_in_scope: 9
fixed: 9
skipped: 0
status: all_fixed
---

# Phase 53: Code Review Fix Report

**Fixed at:** 2026-08-30T14:00:00Z
**Source review:** .planning/phases/53-closed-loop-auto-tuning-capstone/53-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 9
- Fixed: 9
- Skipped: 0

## Fixed Issues

### CR-01: Heuristic propose_fn direction reversal is dead code

**Files modified:** `python/fdars/mcp/_tuning.py`, `tests/test_mcp_tuning.py`
**Commit:** c5f1664
**Applied fix:** Replaced the standalone `_heuristic_step` function (which derived
direction from `accepted_history` — always-True entries, so reversal never fired) with
a closure-based `_make_heuristic_propose_fn` that tracks its own `direction`,
`factor`/`step`, and `prev_accepted_len` state. Rejection is detected by comparing
`len(accepted_history)` at successive calls: if the count has not grown, the last
proposal was rejected and the closure reverses direction and halves the step size.
Updated existing tests to use `_make_heuristic_propose_fn` directly; added three
new behavioural tests: (a) steps down after a rejected upward step, (b) bisection
halves the step after reversal, (c) terminates within budget via `run_tuning_loop_mcp`.

**Hard invariants preserved:** LLM-free scan (`advise` token absent), determinism
(same inputs → same trace), MCP boundary (no numpy across MCP), guard-sync no-op.

---

### CR-02: n_steps / steps_used / budget_remaining off by one

**Files modified:** `python/fdars/advisor/_tuning.py`, `tests/test_advisor_tuning.py`
**Commit:** 342832d
**Applied fix:** Replaced `n_steps=step` (0-indexed loop variable, not incremented
before break for parse_failure, oscillation-revisit, guard_stop, and converged paths)
with `n_steps_actual = len(steps_recorded)` — the authoritative count of actually
recorded steps. `budget_remaining` derived as `max(0, max_steps - n_steps_actual)`.
Updated `test_parse_failure` (old assert `n_steps==0` → correct `n_steps==1` since
the failed step is recorded before break). Added four new invariant tests:
`n_steps == len(trace.steps)` for budget, converged, guard_stop stops, and
`budget_remaining` consistency.

---

### WR-01: improvement_pct sign inverted for lower-is-better metrics

**Files modified:** `python/fdars/advisor/__init__.py`, `tests/test_advisor_tuning_llm.py`
**Commit:** d68b34c
**Applied fix:** Changed raw pct computation from always using the arithmetic sign to
sign-aware: `improvement_pct = raw_pct if direction == "higher" else -raw_pct`. Also
switched `_METRIC_REGISTRY.get(target_metric, "lower")` to `_METRIC_REGISTRY[target_metric]`
(IN-03 partial fix for this site). Added two new tests: lower-is-better (GCV: 0.10→0.08)
and higher-is-better (clustering separation: 0.5→0.65) both assert `improvement_pct > 0`.

**Note:** Logic change (sign flip for lower-is-better metrics) — requires human
verification that the direction inversion is correct for all metric types.

---

### WR-02: seed docstring vs code — default seed to 42

**Files modified:** `python/fdars/mcp/server.py`, `tests/test_mcp_tuning.py`
**Commit:** 7dabc5f
**Applied fix:** Changed `fdars_auto_tune` signature from `seed: int | None = None` to
`seed: int | None = 42` so the code matches the docstring ("Defaults to 42") and
clustering tuning runs are reproducible by default (Pitfall 7). Added
`test_seed_defaults_to_42_in_signature` using `inspect.signature` to pin the default.

---

### WR-03: propose_fn key-set contract contradiction

**Files modified:** `python/fdars/advisor/_tuning.py`, `tests/test_advisor_tuning.py`
**Commit:** 31c73b8
**Applied fix:** Corrected the `propose_fn` docstring to say "Returns a dict with
exactly one key — the tunable parameter name — mapped to the proposed new scalar value.
Extra keys (e.g. seed) are silently ignored." Relaxed validation from
`set(new_params.keys()) != {param_name}` to `param_name not in new_params` so extra
keys are tolerated instead of triggering parse_failure. Added
`test_propose_fn_extra_keys_ignored`: propose_fn returning `{n_basis, seed}` must
complete without parse_failure.

---

### WR-04: max_steps=0 TypeError on fpca list fallback

**Files modified:** `python/fdars/advisor/__init__.py`, `python/fdars/advisor/_tuning.py`,
`tests/test_advisor_tuning.py`, `tests/test_advisor_tuning_llm.py`
**Commit:** 93fc750
**Applied fix:** Two fixes: (1) `max_steps >= 1` validated at both `auto_tune()` and
`run_tuning_loop()` entry — raises `ValueError` with clear message before any fdars call.
(2) Fixed `initial_target` fallback in `auto_tune()` when `trace.steps` is empty: extracts
last element from list-valued metrics before `float()` cast to prevent `TypeError`.
Added tests for both entry points with `max_steps=0` and `max_steps=-1`.

---

### IN-01: All TuningStep.proposal_source fields hardcoded to "mock"

**Files modified:** `python/fdars/advisor/_tuning.py`, `python/fdars/advisor/__init__.py`,
`python/fdars/mcp/_tuning.py`
**Commit:** 6d8aa16
**Applied fix:** Added `propose_fn_label: str = "mock"` parameter to `run_tuning_loop`
and replaced all hardcoded `proposal_source="mock"/"unknown"` in TuningStep constructors
with `proposal_source=propose_fn_label`. `auto_tune()` passes `"llm"`;
`run_tuning_loop_mcp` passes `"heuristic"`; tests use the default `"mock"`.

---

### IN-02: Dead no-op assignment at mcp/_tuning.py

**Files modified:** `python/fdars/mcp/_tuning.py`
**Commit:** 4b2ee5c
**Applied fix:** Removed tautological conditional `first_step = steps[0] if
hasattr(steps[0], "target_before") else steps[0]` — both branches assign `steps[0]`.
Simplified to `first_step = steps[0]`.

---

### IN-03: Inconsistent unreachable _METRIC_REGISTRY.get() defaults

**Files modified:** `python/fdars/mcp/_tuning.py`
**Commit:** 7429296
**Applied fix:** Replaced `_METRIC_REGISTRY.get(target_metric, "higher")` with direct
subscript `_METRIC_REGISTRY[target_metric]` in `mcp/_tuning.py`. The `advisor/__init__.py`
site was already fixed in the WR-01 commit (changed `.get(target_metric, "lower")` to
`[target_metric]`).

---

## Skipped Issues

None — all 9 findings were fixed.

---

## Test Results

**Final test run (all in-scope test files):**

```
tests/test_advisor_tuning.py + tests/test_advisor_tuning_llm.py + tests/test_mcp_tuning.py
57 passed in 0.88s
```

Verification ran in the **main checkout** (no isolated worktree — `workflow.use_worktrees=false`
per project configuration). Numbers are reproducible from the main checkout.

**Hard invariants verified (all green):**
- `test_auto_tune_does_not_import_advise` — LLM-free scan passes (no `advise` token in mcp/_tuning.py or fdars_auto_tune handler)
- `test_guard_sync_still_no_op` — `_RUNNABLE_METHODS==6`, `_DIAGNOSTICS_METHODS==14` unchanged
- `test_heuristic_deterministic` — two identical heuristic runs produce equal compact result dicts
- `test_returns_by_reference_no_arrays` — returned dict contains only scalars/handles, JSON-serialisable

---

_Fixed: 2026-08-30T14:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
