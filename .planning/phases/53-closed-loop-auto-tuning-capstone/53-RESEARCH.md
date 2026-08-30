# Phase 53: Closed-Loop Auto-Tuning (Capstone) - Research

**Researched:** 2026-08-30
**Domain:** Autonomous bounded tuning loop — propose → apply → re-run fdars → compare → check → iterate
**Confidence:** HIGH — all claims grounded in direct source reading of the actual codebase

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Loop core**: new `python/fdars/advisor/_tuning.py` with `run_tuning_loop(initial, method, target_metric, propose_fn, max_steps, ...)`; `propose_fn` is INJECTABLE (LLM for the API, heuristic for MCP, mock for tests).
- **Termination (bounded)**: required `max_steps` PLUS convergence detection (Δtarget < ε for K consecutive steps) PLUS oscillation detection (param revisit / metric ping-pong). The loop NEVER runs unbounded.
- **"Improve" direction**: reuse the Phase-51 metric registry (higher/lower-is-better); the caller names the target metric.
- **"Apply" step**: mutate the method's scalar param by the proposed delta WITHIN a declared valid range → re-run via fdars (run_method) → rebuild diagnostics → compare.
- **Python API proposal**: the LLM returns a STRUCTURED numeric `parameter_delta` (schema-validated, within the declared range) — NEVER parsed from prose; the LLM never sets a number directly in the numeric path.
- **MCP proposal**: a DETERMINISTIC heuristic (LLM-free) — gradient-sign / grid step on the target metric.
- **Schema**: new `TuneProposal {param, delta-or-new_value, rationale}`; new `TuneResult` + `TuningTrace`; plus an OPTIONAL `Recommendation.parameter_delta` field (backward-compatible).
- **Range safety**: each tunable param declares a valid range; out-of-range proposals are clamped/rejected; an unparseable proposal exits the loop (no numeric-path retry).
- **Guard diagnostics (TUNE-05)**: optional watched non-target metrics; if a guard metric degrades past a threshold while the target improves, flag/stop.
- **TuningTrace**: records each step {proposal, params, target before/after, guards, accepted} → returned in `TuneResult`.
- **Accept policy**: accept a step only if the target improves AND guards don't degrade; else reject/terminate.
- **Determinism**: a fixed `propose_fn` + fixed data ⇒ fully deterministic and offline-testable.
- **Tunable methods**: a small tunable-param registry over the EXISTING 6 runnable methods.
- **MCP `fdars_auto_tune`**: orchestrates run_method + compare + heuristic proposal; provably LLM-free (never calls `advise()`); returns by-reference.
- **`max_steps`**: default 10, hard cap 20.
- **Eval hook**: `auto_tune()` returns a trace rich enough for the Phase-54 eval.

### Claude's Discretion

- Exact convergence ε / K, oscillation-detection algorithm, heuristic step rule, the tunable-param registry contents + ranges, schema field names, and test fixtures — at Claude's discretion, informed by RESEARCH.md, consistent with the grounding invariant + LLM-free-MCP boundary.

### Deferred Ideas (OUT OF SCOPE)

- Python-API-only cut (defer the MCP tool) — rejected; ship both.
- `max_steps` cap above 20 — rejected.
- Multi-parameter / joint tuning — single scalar param per loop this phase.
- Eval harness — Phase 54.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TUNE-01 | Shared `_tuning.py` loop core with injectable `propose_fn`; fully offline-testable without API key | §Tunable-Param Registry, §Injectable seam, §Offline testability |
| TUNE-02 | Bounded termination: `max_steps` + convergence (Δ < ε for K steps) + oscillation detection | §Convergence algorithm |
| TUNE-03 | Python API `auto_tune()` uses LLM via structured `parameter_delta` field; LLM never in numeric path | §LLM proposal path |
| TUNE-04 | `fdars_auto_tune` MCP tool uses deterministic heuristic; never calls `advise()` | §Heuristic proposal |
| TUNE-05 | Optional guard diagnostics detect Goodhart degradation | §Guard diagnostics |
| TUNE-06 | `TuneProposal`/`TuneResult`/`TuningTrace` schemas + optional `Recommendation.parameter_delta` backward-compatible | §Schema design |
</phase_requirements>

---

## Summary

Phase 53 is the capstone of the v8.0 milestone. Its core novelty is a **bounded tuning orchestrator** — a Python loop that alternates between proposing a parameter change (LLM or heuristic) and running fdars to observe the effect. The fundamental design challenge is not the loop mechanics (those are simple) but the **safety guarantees**: the loop must terminate, must never let the LLM touch the numeric path, must detect oscillation, and must be testable offline with a mock.

The six `_RUNNABLE_METHODS` define the space of what can be auto-tuned: `alignment`, `fpca`, `basis`, `smoothing`, `clustering`, `depth`. Of these, four have a clear scalar tuning param with a diagnostic target that the metric registry already tracks. Two (`alignment`, `depth`) lack a meaningful scalar parameter to tune — they should be in the registry but marked as not-tuneable, with a `ValueError` at call time that explains why. This is safer than silently accepting a tuning call with no effect.

The main architectural answer this research provides: the loop's `propose_fn` seam is the single correct abstraction. All complexity — LLM proposal, heuristic proposal, mock proposal — reduces to "give me the next param value." Everything else (apply, re-run, compare, terminate) is deterministic Python that the planner can task-ify directly.

**Primary recommendation:** Build `_tuning.py` as a pure state-machine around `propose_fn(current_params, history) -> new_params`, with termination checked by the orchestrator before every call. The LLM proposal path wraps `advise()` into a `propose_fn` closure; the heuristic path is a gradient-sign stepper. Both surfaces — Python API and MCP tool — share exactly one loop core.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Tuning loop orchestration | `advisor/_tuning.py` | `advisor/__init__.py` (entry point) | Loop core is pure Python; shared by both surfaces |
| LLM proposal | `advisor/_tuning.py` (closure over `advise()`) | `advisor/_prompts.py` (new task clause) | LLM is called inside the closure; never inside the loop core itself |
| Heuristic proposal | `mcp/_tuning.py` | `advisor/_tuning.py` (imported) | Deterministic stepper belongs in MCP layer; uses same loop core |
| Schema types | `advisor/_schema.py` | — | `TuneProposal`, `TuneResult`, `TuningTrace` alongside existing `Advice` |
| Method re-run | `mcp/_runner.py` (existing `run_method`) | — | Loop re-runs via the existing runner; no duplication |
| Diagnostics rebuild | `advisor/__init__.py` (`build_diagnostics`) | — | Same function as the rest of the advisor |
| Target comparison | `advisor/_compare_methods.py` (`_METRIC_REGISTRY`) | — | Direction (higher/lower) already registered |
| Guard check | `advisor/_tuning.py` | — | Pure Python range check; deterministic |
| MCP tool | `mcp/server.py` (`fdars_auto_tune`) | `mcp/_tuning.py` | Tool validates method, delegates to `_tuning_loop_mcp()` |

---

## Tunable-Param Registry

This section answers Question 1 concretely from the actual source files.

### Source basis

The six `_RUNNABLE_METHODS` are defined at `python/fdars/mcp/server.py:51-53` as:
`{"alignment", "fpca", "basis", "smoothing", "clustering", "depth"}` [VERIFIED: python/fdars/mcp/server.py:51-53]

The metric registry `_METRIC_REGISTRY` is defined at `python/fdars/advisor/_compare_methods.py:42-55`. The full verbatim registry as read:
```python
_METRIC_REGISTRY: dict[str, str] = {
    "mean_amplitude_separation": "higher",
    "mean_phase_separation": "higher",
    "optimal_gcv": "lower",
    "optimal_edf": "lower",
    "min_cv_error": "lower",
    "r_squared": "higher",
    "functional_mae": "lower",
    "functional_mse": "lower",
    "functional_mape": "lower",
    "functional_msle": "lower",
    "functional_explained_variance": "higher",
    "cumulative_variance_explained": "higher",
}
```
[VERIFIED: python/fdars/advisor/_compare_methods.py:42-55]

The per-family defaults at `python/fdars/advisor/_compare_methods.py:58-66`:
```python
_DEFAULT_METRIC_BY_FAMILY: dict[str, str] = {
    "clustering": "mean_amplitude_separation",
    "smoothing": "optimal_gcv",
    "basis": "optimal_edf",
    "regression_cv": "min_cv_error",
    "regression": "r_squared",
    "scoring": "functional_mse",
    "fpca": "cumulative_variance_explained",
}
```
[VERIFIED: python/fdars/advisor/_compare_methods.py:58-66]

The `fdars_run_method` param-to-method mapping from `python/fdars/mcp/server.py:268-277`:
```
alignment:  lambda_   (default 0.0)
fpca:       n_comp    (default 3)
basis:      lambda_   (default 1.0)
smoothing:  n_basis   (default 15)
clustering: k         (default 3), seed (default 42)
depth:      no scalar params (always fraiman_muniz_1d)
```
[VERIFIED: python/fdars/mcp/server.py:268-277]

### Per-method tuning analysis

**`smoothing`** — TUNEABLE
- Tunable param: `n_basis` (int), the B-spline knot count passed to `pspline_fit_gcv`
- Default: 15. Valid range: `[4, 60]`. Step granularity: 1 (integer steps)
- Target metric: `optimal_gcv` — direction `"lower"` [VERIFIED: python/fdars/advisor/_compare_methods.py:45]
- Rationale: `pspline_fit_gcv` is re-runnable with different `n_basis`; `optimal_gcv` is the GCV at the optimal lambda for that basis count — directly comparable across runs. The smoothing diagnostics builder emits `optimal_gcv` as a plain float at `python/fdars/advisor/aspects/smoothing.py:34` [VERIFIED: python/fdars/advisor/aspects/smoothing.py:34]
- Guard metric: `optimal_edf` — upper bound 0.9 × n_obs prevents over-fitting the basis

**`basis`** — TUNEABLE  
- Tunable param: `lambda_` (float), the regularisation strength for basis fitting
- Default: 1.0. Valid range: `[1e-6, 1e4]` on a log scale. Step: multiply/divide by 10 (log-step heuristic)
- Target metric: `optimal_edf` — direction `"lower"` [VERIFIED: python/fdars/advisor/_compare_methods.py:46]
- Rationale: `basis_nbasis_cv` sweeps over n_basis values for a given lambda_; adjusting lambda_ changes the regularisation-edf tradeoff. `optimal_edf` is the edf at the minimum GCV point, directly comparable. Emitted at `python/fdars/advisor/aspects/basis.py:48` [VERIFIED: python/fdars/advisor/aspects/basis.py:48]
- Guard metric: `optimal_gcv` — must not degrade by more than 20% relative from the initial value

**`fpca`** — TUNEABLE
- Tunable param: `n_comp` (int), the number of FPCA components
- Default: 3. Valid range: `[1, min(n_obs//2, 20)]`. Step granularity: 1
- Target metric: `cumulative_variance_explained` (last element of list) — direction `"higher"` [VERIFIED: python/fdars/advisor/_compare_methods.py:54]
- Rationale: FPCA is re-runnable with different `n_comp`; the cumulative variance explained increases monotonically with n_comp (adding components never reduces variance captured). This is the only method where the target is guaranteed monotone — the loop can detect if it isn't (noise/numerical issue) and stop.
- Guard metric: `phase_leakage_indicator` — must stay below 0.5 (already flagged in diagnostics [VERIFIED: python/fdars/advisor/aspects/fpca.py:71-77])
- Note: `cumulative_variance_explained` is a list; the ranker already extracts the last element as the scalar via `_extract_metric_value`. The tuning loop must do the same extraction.

**`clustering`** — TUNEABLE
- Tunable param: `k` (int), the cluster count
- Default: 3. Valid range: `[2, min(n_obs//3, 15)]`. Step granularity: 1 (integer steps)
- Target metric: `mean_amplitude_separation` — direction `"higher"` [VERIFIED: python/fdars/advisor/_compare_methods.py:43]
- Rationale: Larger k separates clusters further by amplitude; the loop searches for k that maximises inter-cluster amplitude separation. `mean_amplitude_separation` requires `argvals` — the loop must pass argvals through.
- Guard metric: `min_cluster_size` (derived from `cluster_sizes` list: `min(cluster_sizes)`) — must be >= 2. The cluster sizes are in `diagnostics["cluster_sizes"]` as a plain list [VERIFIED: python/fdars/advisor/aspects/clustering.py:42-44]. The guard check extracts `min(diag["cluster_sizes"])`.
- Special: `seed` is held fixed across the loop (caller supplies once, loop uses it for every re-run). Varying seed would make the oscillation detector spuriously fire.

**`alignment`** — NOT TUNEABLE (this loop)
- The only parameter is `lambda_` (warp penalty), but the alignment diagnostics (`amplitude_mean`, `phase_mean`, `least_squares_score`) are not in `_METRIC_REGISTRY` [VERIFIED: python/fdars/advisor/_compare_methods.py:42-55 — none of these keys appear]
- `pairwise_correlation_score` and `least_squares_score` exist in alignment diagnostics [VERIFIED: python/fdars/advisor/aspects/alignment.py:101-131] but are not in the metric registry. Adding them to the metric registry is outside this phase's scope.
- **Verdict**: register `"alignment"` in the tunable-param registry with `tuneable: False`; `auto_tune(method="alignment")` raises `ValueError("alignment has no registered tunable parameter in this phase; use fdars_compare_run to manually explore lambda_ values")`

**`depth`** — NOT TUNEABLE
- No scalar parameters at all — `fdars_run_method` for depth always runs `fraiman_muniz_1d` with no knobs [VERIFIED: python/fdars/mcp/server.py:274-276]
- Depth diagnostics (`depth_mean`, `depth_q10`, etc.) are not in the metric registry [VERIFIED: python/fdars/advisor/_compare_methods.py:42-55]
- **Verdict**: register `"depth"` with `tuneable: False`; raise `ValueError` at call time

### Recommended Tunable-Param Registry

```python
# python/fdars/advisor/_tuning.py

_PARAM_REGISTRY: dict[str, dict] = {
    "smoothing": {
        "tuneable": True,
        "param": "n_basis",
        "param_type": int,
        "default": 15,
        "range": (4, 60),
        "log_scale": False,
        "target_metric": "optimal_gcv",
        "target_direction": "lower",   # from _METRIC_REGISTRY
        "guard_metrics": {
            # key: (threshold_fn, description)
            # threshold_fn(initial_val, current_val) -> bool (True = guard violated)
            "optimal_edf": "upper_fraction",  # current > 0.9 * n_obs
        },
    },
    "basis": {
        "tuneable": True,
        "param": "lambda_",
        "param_type": float,
        "default": 1.0,
        "range": (1e-6, 1e4),
        "log_scale": True,
        "target_metric": "optimal_edf",
        "target_direction": "lower",
        "guard_metrics": {
            "optimal_gcv": "relative_degradation_20pct",
        },
    },
    "fpca": {
        "tuneable": True,
        "param": "n_comp",
        "param_type": int,
        "default": 3,
        "range": (1, 20),   # upper bound clamped to min(n_obs//2, 20) at runtime
        "log_scale": False,
        "target_metric": "cumulative_variance_explained",  # extract last element
        "target_direction": "higher",
        "guard_metrics": {
            "phase_leakage_indicator": "upper_threshold_0.5",
        },
    },
    "clustering": {
        "tuneable": True,
        "param": "k",
        "param_type": int,
        "default": 3,
        "range": (2, 15),   # upper bound clamped to min(n_obs//3, 15) at runtime
        "log_scale": False,
        "target_metric": "mean_amplitude_separation",
        "target_direction": "higher",
        "guard_metrics": {
            "cluster_sizes": "min_cluster_size_ge_2",  # special: min(list) >= 2
        },
    },
    "alignment": {
        "tuneable": False,
        "reason": "no registered metric in _METRIC_REGISTRY for alignment diagnostics",
    },
    "depth": {
        "tuneable": False,
        "reason": "depth has no scalar tunable parameters",
    },
}
```

**Claim provenance:**
- `param` values derived from `fdars_run_method` docstring [VERIFIED: python/fdars/mcp/server.py:206-278]
- `target_metric` values from `_METRIC_REGISTRY` and `_DEFAULT_METRIC_BY_FAMILY` [VERIFIED: python/fdars/advisor/_compare_methods.py:42-66]
- `default` values from `fdars_run_method` docstring [VERIFIED: python/fdars/mcp/server.py:268-277]
- Guard metric keys from aspect diagnostics builders [VERIFIED: python/fdars/advisor/aspects/clustering.py, fpca.py, smoothing.py, basis.py]

---

## Architecture Patterns

### System Architecture Diagram

```
auto_tune() call (Python API or MCP)
         │
         ▼
_tuning_loop(dataset_id, method, propose_fn, max_steps, ...) ← _tuning.py
         │
         │  iteration start
         ├─ check termination FIRST (step >= max_steps → exit "budget")
         │
         ├─ propose_fn(current_params, history) → new_params
         │         │
         │         ├─ LLM path: calls advise(diag, task="parameter_proposal")
         │         │            extracts TuneProposal.new_value via schema
         │         │            clamps to valid range
         │         │            returns {param: clamped_value}
         │         │
         │         └─ heuristic path: gradient-sign step on param
         │                            no LLM call
         │                            returns {param: stepped_value}
         │
         ├─ apply: run_method(dataset_id, method, **new_params) → result
         │
         ├─ build_diagnostics(result, method, ...) → new_diag
         │
         ├─ extract target_value from new_diag (scalar)
         ├─ compute delta = new_target - prev_target
         │
         ├─ guard check (deterministic range check, NO LLM)
         │       IF any guard violated → exit "guard_stop", step rejected
         │
         ├─ improvement check (_METRIC_REGISTRY direction)
         │       IF not improved → step rejected; check convergence window
         │
         ├─ oscillation check (visited-param set / ping-pong detector)
         │       IF oscillation → exit "oscillation"
         │
         ├─ convergence check (|delta| < ε for K consecutive accepted steps)
         │       IF converged → exit "converged"
         │
         ├─ append step to TuningTrace
         └─ advance to next iteration
```

### Recommended Project Structure

```
python/fdars/advisor/
├── _tuning.py          # NEW: shared loop core + _PARAM_REGISTRY + TuneProposal/TuneResult/TuningTrace
├── _schema.py          # EXTEND: add TuneProposal, TuneResult, TuningTrace Pydantic models
├── _prompts.py         # EXTEND: add "parameter_proposal" task clause
├── __init__.py         # EXTEND: export auto_tune()
...
python/fdars/mcp/
├── _tuning.py          # NEW: heuristic_propose + _tuning_loop_mcp (wraps shared core)
├── server.py           # EXTEND: fdars_auto_tune @mcp.tool()
```

### Pattern 1: Injectable `propose_fn` seam

The loop core in `_tuning.py` accepts:

```python
# Source: design decision from 53-CONTEXT.md + ARCHITECTURE.md
def run_tuning_loop(
    dataset_id: str,
    method: str,
    initial_params: dict,
    target_metric: str,
    propose_fn,          # callable(current_params: dict, history: list[dict]) -> dict
    *,
    max_steps: int = 10,
    eps: float = 1e-4,
    no_improve_window: int = 3,
    guard_thresholds: "dict | None" = None,
    argvals=None,
    seed: "int | None" = None,
) -> "TuningTrace":
```

`propose_fn` receives `(current_params: dict, history: list[dict])` and returns `dict` with the single param key → new value. History entries are compact: `{"step": int, "param_value": scalar, "target_value": float, "accepted": bool}`.

LLM closure (Python API):
```python
def _make_llm_propose_fn(method, target_metric, param_spec, domain_context, model, provider):
    def propose_fn(current_params, history):
        diag = build_diagnostics(...)   # already computed; passed in via closure
        advice = advise(diag, task="parameter_proposal", domain_context=domain_context,
                        model=model, provider=provider, aspect=method)
        # Extract TuneProposal from Recommendation.parameter_delta (new optional field)
        for rec in advice.recommendations:
            if rec.parameter_delta is not None:
                raw_val = rec.parameter_delta.new_value
                # Clamp to valid range
                lo, hi = param_spec["range"]
                clamped = max(lo, min(hi, raw_val))
                return {param_spec["param"]: clamped}
        # No structured proposal → exit signal
        raise _UnparseableProposalError("LLM returned no parameter_delta")
    return propose_fn
```

Heuristic closure (MCP, LLM-free):
```python
def _make_heuristic_propose_fn(param_spec):
    def propose_fn(current_params, history):
        return _heuristic_step(current_params, history, param_spec)
    return propose_fn
```

Mock closure (tests):
```python
def _make_mock_propose_fn(deltas: list):
    """Replay a fixed list of delta values. Raises StopIteration when exhausted."""
    deltas_iter = iter(deltas)
    def propose_fn(current_params, history):
        delta = next(deltas_iter)
        param = list(current_params.keys())[0]
        return {param: current_params[param] + delta}
    return propose_fn
```

### Pattern 2: Convergence + Oscillation Detection Algorithm

**Concretely recommended algorithm (for planner to implement verbatim):**

```
Constants (at Claude's discretion per locked decision):
  ε = 1e-4   (min meaningful absolute Δtarget)
  K = 3      (consecutive-no-improvement window — fires before max_steps on flat landscape)
  
State variables:
  no_improve_count = 0
  visited_params = set()       # frozenset of (param_name, rounded_value) tuples
  prev_target_values = []      # circular buffer of last K accepted target values
  
TERMINATION CONDITIONS (checked in this precedence order every iteration):
  
  1. step >= max_steps          → stop_reason = "budget"         [HIGHEST PRIORITY]
  2. guard violated             → stop_reason = "guard_stop"     [before propose]
  3. UnparseableProposalError   → stop_reason = "parse_failure"  [after propose]
  4. param already in visited_params → stop_reason = "oscillation" (param revisit)
  5. |target_new - target_prev| <= ε AND no_improve_count >= K  → stop_reason = "converged"
  6. Ping-pong: last 3 accepted param values alternate direction (A > B < A or A < B > A)
     AND |target values| all within ε of each other → stop_reason = "oscillation"
  
  None of the above fired → continue
```

**Rounding for visited_params set:** For integer params (n_basis, n_comp, k), use the exact int. For float params (lambda_), round to 4 significant figures: `round(val, 4 - int(math.floor(math.log10(abs(val)))) - 1)`. This prevents the set from growing unboundedly on near-revisits while still catching exact revisits.

**No-improve count update:**
- If step is accepted (target improved AND guards ok): reset `no_improve_count = 0`; append target_value to `prev_target_values`
- If step is rejected (target did not improve OR guard violated): increment `no_improve_count`; do NOT add param to `visited_params`
- At K consecutive non-improvements → convergence (return `"converged"`)

**History passed to propose_fn:** Only accepted steps. Rejected steps are not in the history list. This prevents the LLM from inferring a trend from rejected moves that the loop has already discarded.

### Pattern 3: Heuristic (LLM-free) Proposal for MCP

**Gradient-sign line search — the deterministic step rule:**

```python
def _heuristic_step(current_params: dict, history: list[dict], param_spec: dict) -> dict:
    """Single-param gradient-sign step toward improving target.
    
    Step logic:
    1. If history is empty: use step_size = (range_hi - range_lo) / 10 in the
       positive direction for "higher" target, negative for "lower" target.
    2. If history has >= 1 entry:
       - Determine direction: if last accepted step improved the target,
         continue in same direction; else reverse direction.
       - Halve the step size on each direction reversal (bisection-style decay).
       - Minimum step size: 1 for integer params, (range_hi - range_lo) * 1e-4 for float.
    3. Apply step; clamp to [range_lo, range_hi].
    4. For log-scale params (lambda_): multiply/divide by factor = 10^(1/step_count)
       rather than add/subtract.
    """
    param = param_spec["param"]
    lo, hi = param_spec["range"]
    log_scale = param_spec["log_scale"]
    current_val = current_params[param]
    
    if not history:
        # Initial step: coarse step in the "improving" direction
        if log_scale:
            factor = 10.0  # one decade
            new_val = current_val * factor
        else:
            step = (hi - lo) / 10.0
            new_val = current_val + step
    else:
        last = history[-1]
        # Compute direction from last move
        last_param_val = last["param_value"]
        last_target_improved = last["accepted"]
        direction = 1 if current_val >= last_param_val else -1
        if not last_target_improved:
            direction = -direction   # reverse if last move didn't help
        # Step size: decay with reversals
        n_reversals = sum(
            1 for i in range(1, len(history))
            if history[i]["accepted"] != history[i-1]["accepted"]
        )
        if log_scale:
            factor = 10.0 / (2 ** n_reversals)
            factor = max(factor, 1.01)  # min step ~1%
            new_val = current_val * factor if direction > 0 else current_val / factor
        else:
            step = (hi - lo) / (10.0 * (2 ** n_reversals))
            step = max(step, 1.0 if param_spec["param_type"] == int else (hi - lo) * 1e-4)
            new_val = current_val + direction * step
    
    # Clamp to range
    new_val = max(lo, min(hi, new_val))
    if param_spec["param_type"] == int:
        new_val = int(round(new_val))
    
    return {param: new_val}
```

This is reproducible, requires no LLM, and converges on the boundary when the target is monotone (guaranteed for FPCA's cumulative variance explained).

### Pattern 4: LLM Proposal Path (grounding)

**Schema for `TuneProposal` (new Pydantic model in `_schema.py`):**

```python
class TuneProposal(BaseModel):
    """Structured parameter proposal from the LLM. Never in the numeric path."""
    param: str           # the param name being changed (e.g. "n_basis")
    new_value: float     # proposed new value — CLAMPED by orchestrator before use
    rationale: str       # qualitative justification; must NOT cite predicted future values
```

**Optional field on `Recommendation` (backward-compatible):**

```python
class Recommendation(BaseModel):
    action: str
    kind: Literal["parameter", "method", "none"]
    rationale: str
    expected_effect: str          # qualitative only — no numeric predictions
    evidence: List[str]
    parameter_delta: Optional[TuneProposal] = None   # NEW; None for existing tasks
```

**How current diagnostics + param range are presented to the LLM:**

In `_prompts.py`, the `"parameter_proposal"` task clause instructs:

```
You are proposing a SINGLE parameter change for the fdars method "{method}".
The tunable parameter is "{param}" (current value: {current_val}).
Valid range: [{range_lo}, {range_hi}].
Target metric: "{target_metric}" (improve direction: {direction}).
Current diagnostics are provided. Do NOT predict the numeric value of the
target metric after your proposed change — you will observe the actual result
in the next step.
Populate `parameter_delta.new_value` with a single numeric value within the
valid range. Populate `parameter_delta.param` with "{param}" exactly.
Populate `parameter_delta.rationale` with a qualitative reason only — no numbers
not present in the current diagnostics.
```

**Validation/clamping pipeline:**

```
LLM returns Advice with Recommendation.parameter_delta.new_value = X
        │
        ├─ Is parameter_delta present? NO → raise _UnparseableProposalError → exit loop
        │
        ├─ Does parameter_delta.param == expected param? NO → raise _UnparseableProposalError
        │
        ├─ Is new_value within [range_lo, range_hi]? 
        │        NO → CLAMP (do not exit; clamped value is still a valid proposal)
        │
        ├─ Is new_value same as current_value? 
        │        YES → treat as no-op proposal; increment no_improve_count
        │
        └─ Cast to int if param_type == int; use as new param value
```

**On unparseable/out-of-range proposals:**
- Unparseable (None parameter_delta, wrong param name, non-numeric value): exit immediately with `stop_reason = "parse_failure"`. Do NOT retry with another LLM call — that would put the LLM in the numeric path indirectly.
- Out-of-range numeric value: clamp silently; log the clamping in the TuningTrace step.
- The LLM never touches fdars directly. The clamped `new_value` is the ONLY number from the LLM that enters the numeric path.

### Pattern 5: Guard Diagnostics (Goodhart)

**Per-method guard metric rules (concrete, deterministic):**

| Method | Target | Guard Metric | Guard Rule | Source |
|--------|--------|--------------|-----------|--------|
| smoothing | `optimal_gcv` lower | `optimal_edf` | `current_edf > 0.9 * n_obs` — overfitting basis | [VERIFIED: aspects/smoothing.py] |
| basis | `optimal_edf` lower | `optimal_gcv` | `current_gcv > initial_gcv * 1.2` — GCV degraded >20% | [VERIFIED: aspects/basis.py] |
| fpca | `cumulative_variance_explained` last | `phase_leakage_indicator` | `current > 0.5` — phase leakage threshold | [VERIFIED: aspects/fpca.py:71-77] |
| clustering | `mean_amplitude_separation` | `cluster_sizes` (min) | `min(cluster_sizes) < 2` — degenerate cluster | [VERIFIED: aspects/clustering.py:42-44] |

Guard check is pure Python — no LLM involved:

```python
def _check_guards(diag: dict, guard_thresholds: dict, initial_diag: dict) -> "list[str]":
    """Return list of violated guard descriptions, or empty list if all OK."""
    violations = []
    for guard_key, rule in guard_thresholds.items():
        if rule == "upper_fraction":
            # optimal_edf > 0.9 * n_obs
            edf = diag.get("optimal_edf")
            n_obs = diag.get("n_obs") or initial_diag.get("n_obs")
            if edf is not None and n_obs is not None:
                if edf > 0.9 * n_obs:
                    violations.append(f"{guard_key}={edf:.3f} exceeds 0.9*n_obs={0.9*n_obs:.1f}")
        elif rule == "relative_degradation_20pct":
            current = diag.get(guard_key)
            initial = initial_diag.get(guard_key)
            if current is not None and initial is not None and initial > 0:
                if current > initial * 1.2:
                    violations.append(f"{guard_key} degraded {100*(current/initial-1):.1f}% from initial")
        elif rule == "upper_threshold_0.5":
            val = diag.get(guard_key)
            if val is not None and val > 0.5:
                violations.append(f"{guard_key}={val:.3f} exceeds threshold 0.5")
        elif rule == "min_cluster_size_ge_2":
            sizes = diag.get(guard_key)
            if sizes is not None and isinstance(sizes, list) and min(sizes) < 2:
                violations.append(f"min cluster size={min(sizes)} below 2 (degenerate cluster)")
    return violations
```

**Accept policy:** A step is accepted ONLY when:
1. Target metric improved (direction-aware comparison using `_METRIC_REGISTRY`)
2. No guard violations

If a step is rejected, it is recorded in `TuningTrace` as `accepted=False` with the rejection reason. The loop continues until `max_steps` or convergence/oscillation.

---

## Schema Design

### New types for `_schema.py`

```python
class TuneProposal(BaseModel):
    """Structured parameter proposal — never directly in the numeric path."""
    param: str              # exact param name from _PARAM_REGISTRY
    new_value: float        # proposed value; orchestrator clamps before use
    rationale: str          # qualitative only; no numeric predictions

class TuningStep(BaseModel):
    """One iteration of the tuning loop — recorded whether accepted or not."""
    step: int
    param_before: float     # scalar param value entering this step
    param_after: float      # scalar param value proposed this step (may == before if clamped-same)
    target_before: float    # target metric value before re-run
    target_after: float     # target metric value after re-run (or None if step rejected pre-run)
    accepted: bool          # True iff target improved AND guards ok
    stop_reason: "str | None"   # non-None only for the final step: "budget"/"converged"/"oscillation"/etc.
    guard_violations: "list[str]"   # empty if guards ok
    proposal_source: str    # "llm" | "heuristic" | "mock"

class TuningTrace(BaseModel):
    """Complete record of a run_tuning_loop() call."""
    method: str
    param: str
    target_metric: str
    target_direction: str   # "higher" | "lower"
    steps: List[TuningStep]
    final_params: dict
    final_diagnostics: dict
    converged: bool
    stop_reason: str        # "budget" | "converged" | "oscillation" | "guard_stop" | "parse_failure"
    n_steps: int
    steps_used: int         # same as n_steps; named for MCP return dict consistency
    budget_remaining: int   # max_steps - n_steps

class TuneResult(BaseModel):
    """Returned by auto_tune() and fdars_auto_tune."""
    trace: TuningTrace
    improved: bool          # True iff final target is better than initial target
    initial_target_value: float
    final_target_value: float
    improvement_pct: "float | None"   # (final - initial) / abs(initial) * 100; None if initial=0
```

**Backward compatibility:** `Recommendation.parameter_delta: Optional[TuneProposal] = None` — default None means all existing tasks (interpretation, parameter, method, comparison, pipeline) are unaffected. The `parameter_proposal` task is the only one that populates this field.

---

## Offline Testability

### The injectable `propose_fn` seam

The seam is `propose_fn: callable(current_params: dict, history: list[dict]) -> dict`.

Three fixtures for CI:

```python
# tests/test_advisor_tuning.py — all offline, no API key required

import pytest
from fdars.advisor._tuning import run_tuning_loop, _PARAM_REGISTRY

# Fixture 1: monotone improvement → converges
def _always_improve_propose_fn(step_size):
    """Always steps in the improving direction."""
    def propose(current_params, history):
        param, val = next(iter(current_params.items()))
        return {param: val + step_size}
    return propose

# Fixture 2: oscillation → terminates with "oscillation"
def _oscillating_propose_fn(up, down):
    """Alternates between two delta values."""
    import itertools
    deltas = itertools.cycle([up, down])
    def propose(current_params, history):
        param, val = next(iter(current_params.items()))
        delta = next(deltas)
        return {param: val + delta}
    return propose

# Fixture 3: always rejects (target never improves) → terminates with "converged" at K
def _no_improve_propose_fn():
    def propose(current_params, history):
        return current_params   # no change → no improvement → converge
    return propose

# Fixture 4: immediately unparseable → parse_failure
def _bad_propose_fn():
    def propose(current_params, history):
        raise _UnparseableProposalError("mock parse failure")
    return propose
```

### Test matrix (all offline, no API key)

| Test | propose_fn | Expected stop_reason | Assertions |
|------|-----------|---------------------|------------|
| `test_budget_exhaustion` | always_improve but max_steps=2 | `"budget"` | `n_steps == 2`, trace has 2 steps |
| `test_convergence` | no_improve_propose_fn, K=3 | `"converged"` | `no_improve_count >= K`, `converged=True` |
| `test_oscillation_param_revisit` | oscillating (visits same int twice) | `"oscillation"` | param in `visited_params` detected |
| `test_oscillation_ping_pong` | oscillating (3-step alternation) | `"oscillation"` | ping-pong detector fires |
| `test_guard_stop_clustering` | always_improve (k increases to degenerate cluster) | `"guard_stop"` | guard_violations non-empty |
| `test_guard_stop_smoothing` | always_improve (n_basis grows to edf > 0.9*n_obs) | `"guard_stop"` | edf guard violation logged |
| `test_parse_failure` | bad_propose_fn | `"parse_failure"` | loop exits immediately, n_steps=0 |
| `test_accept_reject_logged` | oscillating | — | rejected steps in trace with `accepted=False` |
| `test_determinism` | fixed mock | — | two calls with same inputs → identical TuningTrace |
| `test_fpca_cumulative_extraction` | always_improve | — | `cumulative_variance_explained` last-element extracted correctly |
| `test_clustering_min_cluster_size_guard` | always_improve k too high | `"guard_stop"` | `min(cluster_sizes) < 2` detected |
| `test_history_compact` | any | — | history entries contain only: step, param_value, target_value, accepted |

All tests use **synthetic in-memory diagnostics dicts** (no fdars call needed) by mocking `run_method` and `build_diagnostics` in the loop. This is the correct pattern: test the orchestrator logic independently of fdars.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Metric direction (improve check) | custom direction dict | `_METRIC_REGISTRY` from `_compare_methods.py` | Already correct; adding a new dict risks drift [VERIFIED: python/fdars/advisor/_compare_methods.py:42-55] |
| List-valued metric extraction | `diag["cumulative_variance_explained"][-1]` inline | `_extract_metric_value()` from `_compare_methods.py` | Already handles list→scalar, None, TypeError [VERIFIED: python/fdars/advisor/_compare_methods.py:73-94] |
| Method re-run | inline fdars calls | `run_method()` from `mcp/_runner.py` | Already validated, tested, handles all 6 methods |
| Dataset registration | custom handle management | `registry` from `mcp/_registry.py` | Already the source of truth for handle IDs |
| Param schema validation | manual `isinstance` checks | Pydantic `TuneProposal` model | Type errors caught at model construction; consistent with existing advisor schema |
| MCP param allowlist | new allowlist | existing flat-scalar pattern from `fdars_compare_run` | Pattern already established [VERIFIED: python/fdars/mcp/server.py:397-420] |

**Key insight:** The loop core is new, but everything it calls is already tested and shipped. The planner should wire together existing primitives rather than reimplementing them.

---

## Common Pitfalls

### Pitfall 1: LLM proposal carrying history numbers (Goodhart/fabrication hybrid)
**What goes wrong:** The loop history (compact dict with previous target values) is passed in the user message. The LLM reads `target_before=0.042` in the history and cites "0.042" in its next evidence. `_check_grounding` finds 0.042 in the diagnostics dict (if it coincidentally equals another diagnostic value) and passes — but the citation is from history, not from the current diagnostics.
**How to avoid:** Pass history in a clearly labeled separate section OUTSIDE the `Diagnostics` block. The `_check_grounding` guard reads `diagnostics` (the current step's dict); it does not check the history block. Keep history entries as `{"step": int, "param_value": scalar, "target_value": float, "accepted": bool}` — no full diagnostics dict in the history.
**Concrete guard:** `_check_grounding` receives `current_diag` (the current step's `build_diagnostics` output), NOT a merged dict with history. The system prompt says: "The history is for your reference only; cite values from the Diagnostics section."

### Pitfall 2: `expected_effect` in `Recommendation` containing numeric predictions
**What goes wrong:** The LLM writes `expected_effect: "optimal_gcv should drop to 0.031"`. The loop system prompt did not forbid this. `_check_grounding` may or may not catch it depending on whether 0.031 appears elsewhere in the diagnostics.
**How to avoid:** The `"parameter_proposal"` task clause in `_prompts.py` must contain an explicit prohibition: `"Do NOT predict the numeric value of the target metric. Write expected_effect as a qualitative direction only: 'should decrease', 'should increase', 'likely to improve'."` Add a CI assertion: `assert not any(re.search(r'\d+\.\d{2,}', rec.expected_effect) for rec in advice.recommendations)` in the loop's post-advise check.

### Pitfall 3: `max_steps` checked after `propose_fn` (LLM cost waste)
**What goes wrong:** The loop calls `propose_fn` (LLM) THEN checks `step >= max_steps`. One extra LLM call happens on the step that hits the cap.
**How to avoid:** Check `step >= max_steps` as the FIRST thing in each iteration — before calling `propose_fn`. This is also required for the MCP tool to return `budget_remaining` accurately.

### Pitfall 4: `cluster_sizes` guard uses the list directly
**What goes wrong:** The guard check for clustering tries `diag["cluster_sizes"] < 2` — but `cluster_sizes` is a list, not a scalar [VERIFIED: python/fdars/advisor/aspects/clustering.py:42-44]. This raises `TypeError` silently caught.
**How to avoid:** Guard code uses `min(diag["cluster_sizes"])` with an explicit `isinstance(sizes, list) and len(sizes) > 0` check before calling `min`.

### Pitfall 5: Float param (`lambda_`) in `visited_params` set causes spurious non-oscillation
**What goes wrong:** Float param values like 0.9999999 and 1.0000001 are treated as different and never trigger the param-revisit oscillation detector, even though they are functionally identical.
**How to avoid:** Round float params to 4 significant figures before adding to `visited_params`. For log-scale params, round the log10 value.

### Pitfall 6: `fdars_auto_tune` MCP tool imports `advise`
**What goes wrong:** Developer adds `from fdars.advisor import advise` inside `mcp/_tuning.py` for convenience. The `test_mcp_does_not_import_advise` test needs to cover this new file.
**How to avoid:** `mcp/_tuning.py` and `mcp/server.py` must NEVER import anything from `fdars.advisor._prompts`, `fdars.advisor.providers`, or `fdars.advisor.advise`. The heuristic propose_fn is self-contained in `mcp/_tuning.py`. The existing `test_mcp_does_not_import_advise` test must be extended to also walk the import graph of `fdars.mcp._tuning`.

### Pitfall 7: Non-deterministic loop when `seed` is not forwarded to clustering re-runs
**What goes wrong:** The loop changes `k` for clustering but forgets to pass `seed` to `run_method`. `kmeans_fd` with no seed picks a random seed → two loop runs with the same initial params produce different traces.
**How to avoid:** The loop stores `seed` from the initial `initial_params` dict and passes it to every clustering re-run. The `_PARAM_REGISTRY` for clustering marks `seed` as a fixed parameter (not a tunable one). The loop must extract and forward `seed` from `current_params` on every `run_method` call.

### Pitfall 8: Incommensurable diagnostic comparison (method changed mid-loop)
**What goes wrong:** `auto_tune()` is called with `method="smoothing"` but the `propose_fn` returns a dict with a different method key. The loop re-runs `run_method(dataset_id, "fpca", ...)`, builds FPCA diagnostics, then subtracts `optimal_gcv` from FPCA diagnostics — but FPCA doesn't emit `optimal_gcv`.
**How to avoid:** The loop validates that `propose_fn` never changes the method — it only changes the scalar param value. Add assertion: `assert set(new_params.keys()) == set(initial_params.keys())` before `run_method`. If the keys differ, raise `ValueError("propose_fn changed the param key set — only the value of the declared tunable param may change")`.

---

## Code Examples

### Guard check call site in the loop

```python
# Source: design from CONTEXT.md + PITFALLS.md; verified guard keys from aspect files
if guard_thresholds:
    violations = _check_guards(new_diag, guard_thresholds, initial_diag)
    if violations:
        step_record = TuningStep(
            step=step_num,
            param_before=current_param_val,
            param_after=proposed_param_val,
            target_before=prev_target_val,
            target_after=new_target_val,
            accepted=False,
            stop_reason="guard_stop",
            guard_violations=violations,
            proposal_source=proposal_source,
        )
        trace.append(step_record)
        break  # terminate loop; guard stop is final
```

### MCP tool skeleton

```python
# Source: CONTEXT.md locked decision + server.py flat-scalar pattern
# [VERIFIED: python/fdars/mcp/server.py:306-420 for flat-scalar param pattern]

@mcp.tool()
def fdars_auto_tune(
    dataset_id: str,
    method: str,
    target_metric: str | None = None,
    max_steps: int = 10,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict:
    """Closed-loop auto-tuning via heuristic proposal. Fully LLM-free."""
    method_lc = method.lower()
    if method_lc not in _RUNNABLE_METHODS:
        raise ValueError(
            f"fdars_auto_tune: unsupported method {method!r}. "
            f"Supported: {sorted(_RUNNABLE_METHODS)!r}."
        )
    if max_steps > 20:
        raise ValueError("fdars_auto_tune: max_steps cannot exceed 20 (hard cap).")
    
    from fdars.mcp._tuning import run_tuning_loop_mcp  # no advise import here
    
    initial_params: dict = {}
    if lambda_ is not None:
        initial_params["lambda_"] = lambda_
    if n_basis is not None:
        initial_params["n_basis"] = n_basis
    if n_comp is not None:
        initial_params["n_comp"] = n_comp
    if k is not None:
        initial_params["k"] = k
    if seed is not None:
        initial_params["seed"] = seed
    
    return run_tuning_loop_mcp(dataset_id, method_lc, initial_params,
                                target_metric=target_metric, max_steps=max_steps)
```

### Convergence check (termination precedence)

```python
# Termination condition precedence — implement in this exact order
if step >= max_steps:
    stop_reason = "budget"
    break
    
new_params = propose_fn(current_params, history)  # propose AFTER budget check

# Validate new_params keys unchanged
if set(new_params.keys()) != {param_spec["param"]}:
    stop_reason = "parse_failure"
    break

# Check oscillation: param revisit
rounded = _round_param(new_params[param_spec["param"]], param_spec)
if rounded in visited_params:
    stop_reason = "oscillation"
    break

# Run fdars
result = run_method(dataset_id, method, **{**fixed_params, **new_params})
new_diag = build_diagnostics(result, method, argvals=argvals)

# Extract target scalar
new_target = _extract_target(new_diag, target_metric)

# Guard check (before improvement check — guard violation stops regardless)
if guard_thresholds:
    violations = _check_guards(new_diag, guard_thresholds, initial_diag)
    if violations:
        # Record rejected step and stop
        stop_reason = "guard_stop"
        break

# Improvement check
improved = _is_improvement(new_target, prev_target, target_direction)
if improved:
    no_improve_count = 0
    visited_params.add(rounded)
    # Ping-pong detection (last 3 param values)
    if _is_ping_pong(history + [{"param_value": new_params[param_spec["param"]]}]):
        stop_reason = "oscillation"
        break
else:
    no_improve_count += 1
    if no_improve_count >= no_improve_window:
        stop_reason = "converged"
        break
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing; no new dep) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/test_advisor_tuning.py -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TUNE-01 | Injectable propose_fn; loop fully offline | unit | `pytest tests/test_advisor_tuning.py -q` | ❌ Wave 0 |
| TUNE-02 | max_steps fires; convergence fires after K; oscillation fires | unit | `pytest tests/test_advisor_tuning.py::test_budget_exhaustion tests/test_advisor_tuning.py::test_convergence tests/test_advisor_tuning.py::test_oscillation_param_revisit -q` | ❌ Wave 0 |
| TUNE-03 | TuneProposal schema present; Recommendation.parameter_delta backward-compat | unit | `pytest tests/test_advisor_schema.py::test_recommendation_parameter_delta_optional -q` | ❌ Wave 0 |
| TUNE-04 | fdars_auto_tune does not import advise | import-graph | `pytest tests/test_mcp_llm_free.py::test_auto_tune_does_not_import_advise -q` | ❌ Wave 0 |
| TUNE-05 | Guard fires when clustering produces singleton cluster | unit | `pytest tests/test_advisor_tuning.py::test_guard_stop_clustering -q` | ❌ Wave 0 |
| TUNE-06 | TuningTrace/TuneResult JSON-serialisable | unit | `pytest tests/test_advisor_tuning.py::test_trace_json_serialisable -q` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_advisor_tuning.py tests/test_mcp_llm_free.py -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_advisor_tuning.py` — covers TUNE-01, TUNE-02, TUNE-05, TUNE-06 with all offline mock fixtures
- [ ] `tests/test_mcp_tuning.py` — covers TUNE-04, MCP tool schema validation, LLM-free boundary
- [ ] `tests/test_advisor_schema.py` — extend with `test_recommendation_parameter_delta_optional` (existing file)

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | `TuneProposal` Pydantic model validates type; range clamp |
| V4 Access Control | no | Library; no auth layer |
| V2 Authentication | no | Library; no auth layer |

### Known Threat Patterns for this Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| LLM prompt injection via `domain_context` | Tampering | `domain_context` is free text; system prompt is not user-controllable — existing pattern |
| LLM fabricates `new_value` outside range | Tampering | Clamp at orchestrator before any fdars call |
| `propose_fn` raising arbitrary exceptions | Tampering | Wrap in `try/except`; map unknown exceptions to `parse_failure` stop |
| MCP tool receives `max_steps > 20` | DoS | Hard cap enforced at tool boundary with `ValueError` |

---

## Open Questions

1. **`n_obs` availability for smoothing guard** — the smoothing diagnostics builder emits `optimal_edf` but NOT `n_obs` in the dict [VERIFIED: python/fdars/advisor/aspects/smoothing.py]. The guard `edf > 0.9 * n_obs` requires `n_obs`. **Recommendation:** The loop passes `n_obs` as a parameter derived from the dataset shape at loop start (from `registry.get_dataset(dataset_id)` → `data.shape[0]`). Store it in the loop state, not in the diagnostics dict. Alternatively, relax the smoothing guard to `edf > 30` (absolute ceiling for typical FDA datasets) — this avoids the n_obs dependency but is less dataset-adaptive.

2. **`argvals` availability for clustering** — `mean_amplitude_separation` requires `argvals` [VERIFIED: python/fdars/advisor/aspects/clustering.py:48]. The loop must pass `argvals` from the dataset registration through every clustering `build_diagnostics` call. `registry.get_dataset(dataset_id)` returns `(data, argvals)` — the loop should extract argvals at loop start and hold it in loop state.

3. **`cumulative_variance_explained` for fpca** — this is a list; `_extract_metric_value` takes the last element [VERIFIED: python/fdars/advisor/_compare_methods.py:83-94]. The loop must use `_extract_metric_value(diag, "cumulative_variance_explained")`, not direct dict access. The heuristic for FPCA: step monotonically (more components = more variance explained), so the loop should always converge; if it doesn't, the FPCA result is degenerate.

4. **Schema Pydantic fallback** — existing `_schema.py` has a non-Pydantic fallback class for offline use [VERIFIED: python/fdars/advisor/_schema.py:102-194]. The new `TuneProposal`, `TuneResult`, `TuningTrace` classes must also have fallback stand-ins following the same pattern. The loop core must be usable without Pydantic installed (offline tests must not require pydantic).

---

## Environment Availability

Step 2.6 check: Phase 53 is pure Python code + existing fdars bindings. No new external services or tools.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python fdars package (compiled) | Loop re-runs fdars | ✓ (existing) | 0.4.0+ | — |
| pytest | Test suite | ✓ (existing) | — | — |
| pydantic | TuneProposal schema | ✓ (existing, optional) | 2.x | Fallback stand-in class (same pattern as Advice) |

No new environment dependencies.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `n_basis` range `[4, 60]` is sensible for typical FDA datasets | Tunable-Param Registry | Too narrow for very high-dimensional grids; caller can override via initial_params |
| A2 | `lambda_` range `[1e-6, 1e4]` covers typical basis regularisation | Tunable-Param Registry | Missing values outside range; caller can override |
| A3 | FPCA upper bound `min(n_obs//2, 20)` prevents trivial decomposition | Tunable-Param Registry | May be too restrictive for large datasets; hard-code 20 as a safe default |
| A4 | ε = 1e-4 is a meaningful minimum Δtarget across all four methods | Convergence algorithm | For GCV values near 0, 1e-4 may be too large; for `mean_amplitude_separation` near 1.0, too small. Suggest making ε method-specific or per-loop-configurable |
| A5 | K = 3 (no-improve window) is appropriate | Convergence algorithm | Too small → premature convergence on noisy targets; too large → wastes LLM budget |
| A6 | Gradient-sign halving bisection is adequate for the heuristic | Heuristic proposal | May not converge on non-monotone targets; but all four tuneable methods have sufficiently well-behaved target surfaces |
| A7 | `registry.get_dataset(dataset_id)` returns `(data, argvals)` | Open Questions | Must verify against `mcp/_registry.py` before implementing the loop |

---

## Sources

### Primary (HIGH confidence)

- `python/fdars/advisor/_compare_methods.py` — `_METRIC_REGISTRY`, `_DEFAULT_METRIC_BY_FAMILY`, `_extract_metric_value` — read directly this session [VERIFIED]
- `python/fdars/mcp/server.py` — `_RUNNABLE_METHODS`, `fdars_run_method` param mapping, flat-scalar MCP pattern — read directly this session [VERIFIED]
- `python/fdars/advisor/__init__.py` — `build_diagnostics`, `advise`, `_supported` set — read directly this session [VERIFIED]
- `python/fdars/advisor/_schema.py` — `Advice`, `Recommendation`, fallback pattern — read directly this session [VERIFIED]
- `python/fdars/advisor/_prompts.py` — `_GROUNDING_INVARIANT`, `_system_prompt`, existing task clauses — read directly this session [VERIFIED]
- `python/fdars/advisor/aspects/smoothing.py` — `optimal_gcv`, `optimal_edf` keys — read directly this session [VERIFIED]
- `python/fdars/advisor/aspects/basis.py` — `optimal_n_basis`, `optimal_gcv`, `optimal_edf` keys — read directly this session [VERIFIED]
- `python/fdars/advisor/aspects/clustering.py` — `mean_amplitude_separation`, `cluster_sizes`, argvals dependency — read directly this session [VERIFIED]
- `python/fdars/advisor/aspects/fpca.py` — `cumulative_variance_explained`, `phase_leakage_indicator` threshold — read directly this session [VERIFIED]
- `python/fdars/advisor/aspects/alignment.py` — `least_squares_score`, `pairwise_correlation_score` present but NOT in metric registry — read directly this session [VERIFIED]
- `python/fdars/advisor/aspects/depth.py` — no tunable params confirmed — read directly this session [VERIFIED]
- `.planning/phases/53-closed-loop-auto-tuning-capstone/53-CONTEXT.md` — locked decisions, Claude's discretion — read directly this session
- `.planning/research/ARCHITECTURE.md` — loop architecture, proposal_fn seam design — read directly this session
- `.planning/research/PITFALLS.md` — P1–P9 codebase-derived pitfalls for auto-tuning — read directly this session
- `.planning/research/SUMMARY.md` — Phase-53 gaps (convergence math, param spec, max_steps cost) — read directly this session

### Tertiary (LOW confidence — assumptions)

- Convergence ε = 1e-4, K = 3 — [ASSUMED] based on typical hyper-param tuning conventions; no authoritative source for this specific application
- Param ranges [4, 60] for n_basis, [1e-6, 1e4] for lambda_, [1, 20] for n_comp, [2, 15] for k — [ASSUMED] based on general FDA practice; not verified against fdars-core constraints
- Bisection halving heuristic — [ASSUMED] adequate for these target surfaces; not formally verified

---

## Project Constraints (from CLAUDE.md)

Extracted from `/home/simonm/projects/rust/pyfda/.claude/CLAUDE.md`:

- **No new runtime dependencies** — confirmed: Phase 53 adds no new packages
- **MCP layer provably LLM-free** — `fdars_auto_tune` must not import `advise`; existing `test_mcp_does_not_import_advise` must be extended
- **Guard-sync no-op** — no new `build_diagnostics` method slot; `_DIAGNOSTICS_METHODS` unchanged
- **Python 3.9+ compatibility** — `TuneProposal` etc. must have Pydantic fallback stand-ins (same pattern as existing `Advice`/`Recommendation`)
- **By-reference invariant** — MCP tool returns `trace_id` (stored in registry) + compact summary; full `TuningTrace` stored by handle, not returned as inline JSON
- **Flat scalar MCP params** — `fdars_auto_tune` uses flat `lambda_`, `n_basis`, `n_comp`, `k`, `seed` (not nested `initial_params: dict`) matching the existing `fdars_compare_run` pattern [VERIFIED: python/fdars/mcp/server.py:397-420]

---

**Research date:** 2026-08-30
**Valid until:** 2026-09-30 (stable codebase; no upstream changes expected)
