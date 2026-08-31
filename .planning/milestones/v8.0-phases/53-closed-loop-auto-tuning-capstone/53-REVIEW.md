---
phase: 53-closed-loop-auto-tuning-capstone
reviewed: 2026-08-30T12:00:00Z
depth: deep
files_reviewed: 8
files_reviewed_list:
  - python/fdars/advisor/_tuning.py
  - python/fdars/advisor/_schema.py
  - python/fdars/advisor/__init__.py
  - python/fdars/advisor/_prompts.py
  - python/fdars/mcp/_tuning.py
  - python/fdars/mcp/server.py
  - tests/test_advisor_schema.py
  - tests/test_advisor_prompts_parameter_proposal.py
findings:
  critical: 2
  warning: 4
  info: 3
  total: 9
status: resolved
---

# Phase 53: Code Review Report

**Reviewed:** 2026-08-30T12:00:00Z
**Depth:** deep
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Phase 53 introduces the closed-loop auto-tuning capstone: `run_tuning_loop` core
(`_tuning.py`), schema types (`_schema.py`), the LLM-backed `auto_tune()` API
(`__init__.py`), a system-prompt clause (`_prompts.py`), and the LLM-free MCP
tool (`mcp/_tuning.py`, `server.py`).

The core termination state machine, the grounding-invariant boundary (LLM numeric
contribution clamped to range before fdars), and the guard-check logic are
structurally sound. Two critical defects were found: the heuristic proposer in
`mcp/_tuning.py` is behaviourally broken because the direction-reversal logic can
never fire, and `n_steps`/`steps_used`/`budget_remaining` are off by one for four
of the six stop reasons. Four warnings and three info items round out the
findings.

## Critical Issues

### CR-01: Heuristic propose_fn direction reversal is dead code — search never explores lower values

**File:** `python/fdars/mcp/_tuning.py:104-123`

**Issue:** `_heuristic_step` infers direction and computes step-size decay from
`history`, but `history` is `accepted_history` from the loop core — a list that
contains **only accepted steps**, with `"accepted": True` on every entry. As a
result:

1. **Direction never reverses.** The reversal branch is `if not last_accepted:
   direction = -direction`. Since `last_accepted` is always `True`, the branch
   never executes.  `direction` is additionally always `1` because
   `current_val >= last_param_val` is always true: both quantities track the same
   accepted-state cursor.

2. **Step-size never decays.** `n_reversals` counts `accepted != rejected`
   alternations in `accepted_history`; a list of all-`True` entries produces
   `n_reversals = 0` every call. For log-scale params the factor stays at `10.0`
   indefinitely; for linear params the step stays at `(hi - lo) / 10`.

3. **Net behaviour:** the heuristic monotonically increases the parameter toward
   `hi`, accepting each improvement along the way. Once it hits the ceiling,
   clamping produces a repeated value that fires the oscillation-revisit detector.
   The lower half of the search space is never explored. For `lambda_` (basis
   smoothing, range `[1e-6, 1e4]`), starting from `1.0` the heuristic proposes
   `10, 100, 1000, 10000`, then terminates — a six-decade lower region is
   invisible.

**Fix:** The heuristic must track direction and reversal count in its own closure
state, not in `accepted_history`. Replace the closure with one that holds a
`direction` and `step_size` variable updated on each call:

```python
def _make_heuristic_propose_fn(param_spec: dict):
    param = param_spec["param"]
    lo, hi = param_spec["range"]
    log_scale = param_spec["log_scale"]
    is_int = param_spec["param_type"] is int

    # Mutable closure state (correct: not derived from accepted_history)
    state = {
        "direction": 1,
        "factor": 10.0,          # log-scale only
        "step": (hi - lo) / 10.0,  # linear only
        "last_target": None,
    }

    def propose_fn(current_params: dict, history: list) -> dict:
        current_val = current_params[param]
        if not history:
            # Initial coarse step (positive direction)
            if log_scale:
                new_val = current_val * state["factor"]
            else:
                new_val = current_val + state["step"]
        else:
            last_target = history[-1]["target_value"]
            prev_target = state["last_target"]
            # Reverse direction when target did not improve vs the step before
            if prev_target is not None and last_target <= prev_target:
                state["direction"] = -state["direction"]
                if log_scale:
                    state["factor"] = max(1.01, state["factor"] / 2.0)
                else:
                    state["step"] = max(
                        1.0 if is_int else (hi - lo) * 1e-4,
                        state["step"] / 2.0,
                    )
            state["last_target"] = last_target
            if log_scale:
                new_val = (
                    current_val * state["factor"]
                    if state["direction"] > 0
                    else current_val / state["factor"]
                )
            else:
                new_val = current_val + state["direction"] * state["step"]

        new_val = max(lo, min(hi, new_val))
        if is_int:
            new_val = int(round(new_val))
        return {param: new_val}

    return propose_fn
```

---

### CR-02: `n_steps` / `steps_used` / `budget_remaining` off by one for four stop reasons

**File:** `python/fdars/advisor/_tuning.py:517-729`

**Issue:** The step counter `step` (0-indexed) is incremented at the **bottom** of
the loop body (`step += 1`, line 703). For the budget and ping-pong stop paths
`step` is either already the correct count (budget fires when
`step >= max_steps`) or incremented explicitly before `break` (ping-pong, line
661). For all other stop paths — `parse_failure`, `oscillation`-revisit,
`guard_stop`, `converged` — the loop `break`s without incrementing `step`, so
`n_steps = step` is the **0-indexed current step**, not the count of executed
steps. A concrete example: with `no_improve_window=3` and three non-improving
steps (indices 0, 1, 2), convergence fires during step 2 with `step=2`;
`n_steps=2` but `len(trace.steps)==3`.

Downstream effects:
- `steps_used` is the same value — equally wrong.
- `budget_remaining = max(0, max_steps - step)` is inflated by one; callers
  believe one more slot is available than actually is.
- `run_tuning_loop_mcp` reads `n_steps` and `budget_remaining` directly from the
  trace and propagates the error to the MCP return dict.
- Tests at line 716 (`assert trace.n_steps == 0` for `parse_failure`) pass only
  because they are written to match the incorrect behaviour, masking the bug.

**Fix:** Use `step + 1` when the current step was recorded (all non-budget stops
except the case where `step` was already incremented):

```python
# At the TuningTrace construction (replace the four occurrences):
# All non-budget, non-ping-pong stops: step was NOT incremented before break
# n_steps should reflect steps actually recorded.
n_steps_actual = step + 1  # current step was recorded before the break

return TuningTrace(
    ...
    n_steps=n_steps_actual,
    steps_used=n_steps_actual,
    budget_remaining=max(0, max_steps - n_steps_actual),
)
```

For the budget path (step is already `max_steps` when the break fires, with no
step recorded for that index), the count is already correct (`step == max_steps ==
len(trace.steps)`), so the budget branch does not need this adjustment — handle
it by computing the count before returning:

```python
n_steps_actual = len(steps_recorded)   # authoritative: count what was recorded

return TuningTrace(
    ...
    n_steps=n_steps_actual,
    steps_used=n_steps_actual,
    budget_remaining=max(0, max_steps - n_steps_actual),
)
```

## Warnings

### WR-01: `improvement_pct` sign is inverted for lower-is-better metrics

**File:** `python/fdars/advisor/__init__.py:874-876`

**Issue:** `improvement_pct` is computed as
`(final_target - initial_target) / abs(initial_target) * 100`. For `"lower"`
direction metrics (GCV, EDF) the expected improvement is `final < initial`, so
`improvement_pct` is negative when things got **better**. The field name implies
positive means good regardless of direction. A caller checking
`result.improvement_pct > 0` to determine success would invert the answer for
smoothing and basis tuning.

**Fix:** Normalise by direction so positive always means improvement:

```python
raw_pct = (final_target - initial_target) / abs(initial_target) * 100.0
target_direction = _METRIC_REGISTRY.get(target_metric, "lower")
improvement_pct = raw_pct if target_direction == "higher" else -raw_pct
```

Or document clearly in the schema docstring that the sign follows the raw
arithmetic difference (not the improvement direction), and add the `improved` bool
as the authoritative signal.

---

### WR-02: `fdars_auto_tune` seed docstring says "Defaults to 42" but code defaults to `None`

**File:** `python/fdars/mcp/server.py:648-650`

**Issue:** The docstring reads "Fixed RNG seed for clustering (held constant across
all loop steps for reproducibility — Pitfall 7). Defaults to 42." The actual
parameter signature is `seed: int | None = None`. When no seed is supplied for a
clustering tuning run, `seed=None` propagates through to every `run_method` call,
making the loop non-deterministic. The docstring directly contradicts the code,
giving callers false confidence that clustering runs are reproducible by default.

**Fix:** Either:
```python
seed: int | None = 42,   # enforce documented default
```
or correct the docstring to state "Defaults to None (no fixed seed)".

---

### WR-03: `propose_fn` docstring contract contradicts key-set validation

**File:** `python/fdars/advisor/_tuning.py:373-376`

**Issue:** The `propose_fn` parameter docstring says:

> "Returns a dict with the **same key set as `initial_params`** and a new scalar
> value."

But the key-set validation at line 544–563 requires `set(new_params.keys()) ==
{param_name}` — exactly **one key**. If `initial_params` contains `seed` (which
it does when the caller passes it for clustering), a propose_fn that dutifully
mirrors `initial_params` will fail with `parse_failure`. The `_make_mock_propose_fn`
implementation is consistent with the validation (returns single key), so the
docstring is wrong, not the code.

**Fix:** Correct the docstring to:

> "Returns a dict with exactly one key — the tunable parameter name — mapped to the
> proposed new scalar value.  Fixed params such as `seed` must not be included."

---

### WR-04: `initial_target` fallback uses raw list for list-valued metrics when `trace.steps` is empty

**File:** `python/fdars/advisor/__init__.py:862-864`

**Issue:**

```python
initial_target = trace.steps[0].target_before if trace.steps else (
    trace.final_diagnostics.get(target_metric, 0.0)
)
```

When `max_steps=0` (or any value that produces zero recorded steps), the fallback
evaluates `trace.final_diagnostics.get(target_metric, 0.0)`. For the `fpca`
method, `final_diagnostics["cumulative_variance_explained"]` is a Python list, not
a scalar. Subsequent code does not apply the `isinstance(initial_target, list)`
extraction before the arithmetic at line 872 or the `float()` cast at line 882,
causing a `TypeError`. The `max_steps <= 0` path is additionally not validated in
`run_tuning_loop` or `auto_tune`, so a caller passing `max_steps=0` triggers the
crash.

**Fix:**

```python
if trace.steps:
    initial_target = trace.steps[0].target_before
else:
    raw = trace.final_diagnostics.get(target_metric, 0.0)
    if isinstance(raw, (list, tuple)):
        raw = raw[-1] if raw else 0.0
    initial_target = float(raw)
```

Also add validation in `auto_tune`:
```python
if max_steps < 1:
    raise ValueError(f"auto_tune: max_steps must be >= 1, got {max_steps}.")
```

## Info

### IN-01: All `TuningStep.proposal_source` fields hardcoded to `"mock"` in loop core

**File:** `python/fdars/advisor/_tuning.py:539,562,585,613,652,665,689`

**Issue:** Every `TuningStep` constructed inside `run_tuning_loop` uses
`proposal_source="mock"`, regardless of whether the caller is `auto_tune` (LLM),
`run_tuning_loop_mcp` (heuristic), or a test mock. The `TuningTrace` therefore
cannot be used to distinguish proposer types in post-hoc analysis.

**Fix:** Add a `propose_fn_label: str = "mock"` parameter to `run_tuning_loop`
and thread it through to the `TuningStep` constructors. `auto_tune` passes
`"llm"`, `run_tuning_loop_mcp` passes `"heuristic"`, tests pass `"mock"`.

---

### IN-02: Dead no-op assignment at `mcp/_tuning.py:333`

**File:** `python/fdars/mcp/_tuning.py:333`

**Issue:**

```python
first_step = steps[0] if hasattr(steps[0], "target_before") else steps[0]
```

Both branches assign `steps[0]`; the conditional is meaningless. The intent was
likely to choose between attribute access and dict `.get()`, but that distinction
is handled correctly on the lines immediately following (134–137).

**Fix:** Remove the conditional and write simply:

```python
first_step = steps[0]
```

---

### IN-03: `_METRIC_REGISTRY.get(target_metric, "lower"/"higher")` defaults are unreachable dead code

**File:** `python/fdars/advisor/__init__.py:871`, `python/fdars/mcp/_tuning.py:325`

**Issue:** Both sites use a `.get()` default for `target_metric` that can never be
reached: `run_tuning_loop` validates that `target_metric` is in `_METRIC_REGISTRY`
and raises `ValueError` otherwise. The two sites use **opposite** defaults
(`"lower"` in `__init__.py`, `"higher"` in `mcp/_tuning.py`), which would produce
wrong `improved` results for any hypothetical caller who bypassed validation — a
latent inconsistency.

**Fix:** Use `_METRIC_REGISTRY[target_metric]` (direct subscript) at both sites to
make the code self-documenting and eliminate the inconsistent defaults:

```python
target_direction = _METRIC_REGISTRY[target_metric]  # already validated above
```

---

_Reviewed: 2026-08-30T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
