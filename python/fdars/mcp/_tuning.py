"""fdars MCP tuning helper — LLM-free heuristic auto-tuning.

This module exposes ``run_tuning_loop_mcp``, the core logic for the
``fdars_auto_tune`` MCP tool (TUNE-04).  Given a dataset handle, a runnable
method, and optional initial params, it:

1. Resolves the tunable-param spec from ``advisor._tuning._PARAM_REGISTRY``.
2. Validates that the method is tuneable (raises ``ValueError`` for alignment/depth).
3. Builds a DETERMINISTIC heuristic ``propose_fn`` (gradient-sign line search
   with bisection-style step-size decay on direction reversal).
4. Calls ``advisor._tuning.run_tuning_loop`` with the heuristic proposer.
5. Stores the full ``TuningTrace`` in the handle registry.
6. Returns a compact by-reference dict (trace handle + scalar summary only —
   no arrays across the MCP boundary).

The compute path is **fully deterministic and LLM-free** — this module never
imports or calls the LLM advisor or any provider package.
``ANTHROPIC_API_KEY`` is never required here (TUNE-04, T-53C-01).

Requires the ``fdars[mcp]`` optional extra (Python >=3.10).

Call chain::

    fdars_auto_tune  (server.py — @mcp.tool boundary)
        -> run_tuning_loop_mcp  (this module)
            -> advisor._tuning.run_tuning_loop (shared loop core)
                -> run_method (per step)   (_runner.py)
                -> build_diagnostics       (advisor.__init__)
            -> registry.store_result       (_registry.py)
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

__all__ = ["run_tuning_loop_mcp"]


# ---------------------------------------------------------------------------
# Heuristic proposal helpers
# ---------------------------------------------------------------------------


def _make_heuristic_propose_fn(param_spec: dict):
    """Return a deterministic, LLM-free heuristic propose_fn closure.

    The returned callable satisfies the ``propose_fn(current_params, history)``
    interface required by ``run_tuning_loop``.

    The closure tracks its own direction and step-size state so that
    direction reversal and bisection-style decay actually fire — unlike
    approaches that derive direction from ``accepted_history`` (which
    contains only accepted steps, so ``"accepted": True`` on every entry
    and reversal can never be detected).

    Step logic:

    1. If history is empty: initial coarse step in the positive direction.
       - Log-scale (``lambda_``): multiply by factor (default 10.0).
       - Linear: step by ``(range_hi - range_lo) / 10``.
    2. If history has >= 1 entry:
       - Compare the latest ``target_value`` to the previously seen target.
       - If the target did NOT improve (target <= prev_target for "higher"
         metrics, or target >= prev_target for "lower" metrics — here we
         use a direction-agnostic heuristic: target worsened or equal):
         reverse ``direction`` and halve the step size (bisection).
       - Apply capped minimum: factor >= 1.01 for log-scale; 1 for int,
         ``(hi-lo)*1e-4`` for float on linear scale.
    3. Apply step; clamp to ``[range_lo, range_hi]``.
    4. Integer params: round-then-int.

    Parameters
    ----------
    param_spec : dict
        Entry from ``_PARAM_REGISTRY`` for the method being tuned.

    Returns
    -------
    callable
        ``propose_fn(current_params: dict, history: list[dict]) -> dict``
    """
    param = param_spec["param"]
    lo, hi = param_spec["range"]
    log_scale = param_spec["log_scale"]
    is_int = param_spec["param_type"] is int

    # Mutable closure state — updated on every call, NOT derived from
    # accepted_history entries (which always carry ``"accepted": True``, so
    # reversal could never fire from reading that field).  Instead the closure
    # detects rejection by tracking how many accepted entries existed at the
    # previous call: if the count has not grown, the last proposal was rejected.
    state = {
        "direction": 1,
        "factor": 10.0,                       # log-scale step multiplier
        "step": (hi - lo) / 10.0,             # linear step size
        "prev_accepted_len": -1,               # len(history) at the previous call (-1 = never called)
    }

    def propose_fn(current_params: dict, history: list) -> dict:
        current_val = current_params[param]
        accepted_len = len(history)

        if state["prev_accepted_len"] == -1:
            # First call — initial coarse step in positive direction
            state["prev_accepted_len"] = accepted_len
            if log_scale:
                new_val = current_val * state["factor"]
            else:
                new_val = current_val + state["step"]
        else:
            # Detect rejection: accepted_len did NOT grow since the previous call
            # means the last proposal was not accepted (target did not improve).
            last_proposal_rejected = (accepted_len == state["prev_accepted_len"])
            state["prev_accepted_len"] = accepted_len

            if last_proposal_rejected:
                state["direction"] = -state["direction"]
                if log_scale:
                    state["factor"] = max(1.01, state["factor"] / 2.0)
                else:
                    min_step = 1.0 if is_int else (hi - lo) * 1e-4
                    state["step"] = max(min_step, state["step"] / 2.0)

            if log_scale:
                if state["direction"] > 0:
                    new_val = current_val * state["factor"]
                else:
                    new_val = current_val / state["factor"]
            else:
                new_val = current_val + state["direction"] * state["step"]

        # Clamp to declared range
        new_val = max(lo, min(hi, new_val))
        # Integer rounding
        if is_int:
            new_val = int(round(new_val))
        return {param: new_val}

    return propose_fn


# ---------------------------------------------------------------------------
# Main MCP helper
# ---------------------------------------------------------------------------


def run_tuning_loop_mcp(
    dataset_id: str,
    method: str,
    initial_params: dict,
    *,
    target_metric: str | None = None,
    max_steps: int = 10,
) -> dict:
    """Execute the LLM-free heuristic tuning loop and return a by-reference result.

    Resolves the param spec for the given method, validates it is tuneable,
    builds the deterministic heuristic ``propose_fn``, calls the shared
    ``run_tuning_loop`` core, stores the full trace in the handle registry,
    and returns a compact by-reference dict (scalars + trace handle only —
    no arrays cross the MCP boundary).

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID for the dataset stored in the handle registry.
        Obtain via ``registry.store_dataset(data, argvals)``.
    method : str
        One of the six runnable methods (already lowercased by the tool
        boundary).  Raises ``ValueError`` for non-tuneable methods
        (``"alignment"``, ``"depth"``).
    initial_params : dict
        Flat scalar-param dict assembled at the tool boundary from the
        non-``None`` typed arguments (``lambda_``, ``n_basis``, ``n_comp``,
        ``k``, ``seed``).  May be empty (all defaults from spec are used).
    target_metric : str or None
        Diagnostic metric to optimise.  When ``None``, the per-method default
        from ``_PARAM_REGISTRY`` is used.
    max_steps : int
        Maximum loop iterations.  Default 10; hard-capped to 20 at the tool
        boundary before this function is called.

    Returns
    -------
    dict
        JSON-serialisable, by-reference result with keys:

        ``trace_id`` : str
            Opaque handle to the full ``TuningTrace`` stored in the registry.
        ``method`` : str
            The method name (normalised lowercase).
        ``param`` : str
            The tunable parameter name (e.g. ``"n_basis"``).
        ``target_metric`` : str
            The metric being optimised.
        ``stop_reason`` : str
            One of ``"budget"``, ``"converged"``, ``"oscillation"``,
            ``"guard_stop"``, ``"parse_failure"``.
        ``n_steps`` : int
            Number of loop iterations executed.
        ``steps_used`` : int
            Same as ``n_steps`` (alias for MCP return dict consistency).
        ``budget_remaining`` : int
            ``max_steps - n_steps``.
        ``initial_target_value`` : float
            Target metric value at loop start.
        ``final_target_value`` : float
            Target metric value at loop end.
        ``improved`` : bool
            ``True`` iff ``final_target_value`` is strictly better than
            ``initial_target_value`` (direction-aware).

    Raises
    ------
    ValueError
        If ``method`` is not in ``_PARAM_REGISTRY`` or is not tuneable
        (``"alignment"``, ``"depth"``).
    KeyError
        If ``dataset_id`` is not in the registry.
    """
    # Deferred imports: LLM-free — nothing from advisor._prompts, providers, or the LLM path.
    from fdars.advisor._tuning import (
        _PARAM_REGISTRY,
        _METRIC_REGISTRY,
        run_tuning_loop,
        _extract_target,
        _is_improvement,
    )
    from fdars.mcp._registry import registry

    # Validate method is in registry
    if method not in _PARAM_REGISTRY:
        raise ValueError(
            f"run_tuning_loop_mcp: method {method!r} not in _PARAM_REGISTRY. "
            f"Supported: {sorted(_PARAM_REGISTRY)!r}."
        )
    param_spec = _PARAM_REGISTRY[method]

    # Validate method is tuneable
    if not param_spec.get("tuneable", False):
        raise ValueError(
            f"run_tuning_loop_mcp: {method!r} is not tuneable. "
            f"Reason: {param_spec.get('reason', 'no reason given')}."
        )

    # Resolve target_metric from spec default if not provided
    if target_metric is None:
        target_metric = param_spec["target_metric"]

    # Resolve guard_thresholds from param_spec
    guard_thresholds: dict | None = param_spec.get("guard_metrics") or None

    # Build initial_params: fill in missing param default from spec
    param_name = param_spec["param"]
    if not initial_params or param_name not in initial_params:
        merged_params = {param_name: param_spec["default"]}
        merged_params.update(initial_params)
        initial_params = merged_params

    # Extract seed for determinism (Pitfall 7)
    seed = initial_params.get("seed")

    # Retrieve dataset for argvals
    data, argvals = registry.get_dataset(dataset_id)

    # Build heuristic propose_fn (LLM-free, deterministic)
    propose_fn = _make_heuristic_propose_fn(param_spec)

    # Call the shared loop core
    trace = run_tuning_loop(
        dataset_id=dataset_id,
        method=method,
        initial_params=initial_params,
        target_metric=target_metric,
        propose_fn=propose_fn,
        max_steps=max_steps,
        guard_thresholds=guard_thresholds,
        propose_fn_label="heuristic",
        argvals=argvals,
        seed=seed,
    )

    # Store full trace in registry (by-reference invariant — T-53C-04)
    # TuningTrace is a pydantic model or fallback; store as dict
    try:
        trace_dict = trace.model_dump()
    except AttributeError:
        trace_dict = dict(trace.__dict__)
    trace_id = registry.store_result(trace_dict)

    # Extract initial and final target values from the trace
    # The trace records the initial target as the target_before of step 0 (if any steps)
    # or we can derive from the accepted steps.
    # We need to re-extract from the trace's final_diagnostics and initial run.
    # Use trace fields directly.
    target_direction = _METRIC_REGISTRY[target_metric]  # already validated in run_tuning_loop

    # Reconstruct initial target from first step's target_before (if steps exist)
    initial_target_value: float | None = None
    final_target_value: float | None = None

    steps = trace.steps if hasattr(trace, "steps") else trace_dict.get("steps", [])
    if steps:
        first_step = steps[0]
        if hasattr(first_step, "target_before"):
            initial_target_value = first_step.target_before
        else:
            initial_target_value = first_step.get("target_before")

        # Final target: last accepted step's target_after, or last step's target_before
        # if nothing was accepted
        final_target_value = initial_target_value
        for s in steps:
            t_after = s.target_after if hasattr(s, "target_after") else s.get("target_after")
            accepted = s.accepted if hasattr(s, "accepted") else s.get("accepted", False)
            if accepted and t_after is not None:
                final_target_value = t_after

    # Extract from final_diagnostics as the canonical source
    final_diag = (
        trace.final_diagnostics
        if hasattr(trace, "final_diagnostics")
        else trace_dict.get("final_diagnostics", {})
    )
    final_target_from_diag = _extract_target(final_diag, target_metric)
    if final_target_from_diag is not None:
        final_target_value = final_target_from_diag

    # Determine improvement (direction-aware)
    improved = False
    if initial_target_value is not None and final_target_value is not None:
        improved = _is_improvement(final_target_value, initial_target_value, target_direction)

    n_steps = trace.n_steps if hasattr(trace, "n_steps") else trace_dict.get("n_steps", 0)
    steps_used = trace.steps_used if hasattr(trace, "steps_used") else trace_dict.get("steps_used", 0)
    budget_remaining = trace.budget_remaining if hasattr(trace, "budget_remaining") else trace_dict.get("budget_remaining", 0)
    stop_reason = trace.stop_reason if hasattr(trace, "stop_reason") else trace_dict.get("stop_reason", "budget")

    # By-reference return: only scalars + trace handle (no arrays — T-53C-04)
    return {
        "trace_id": trace_id,
        "method": method,
        "param": param_name,
        "target_metric": target_metric,
        "stop_reason": stop_reason,
        "n_steps": n_steps,
        "steps_used": steps_used,
        "budget_remaining": budget_remaining,
        "initial_target_value": float(initial_target_value) if initial_target_value is not None else None,
        "final_target_value": float(final_target_value) if final_target_value is not None else None,
        "improved": improved,
    }
