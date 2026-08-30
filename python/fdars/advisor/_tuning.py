"""fdars.advisor._tuning — Bounded closed-loop parameter auto-tuning.

Provides ``run_tuning_loop()``, a deterministic orchestrator that alternates
between proposing a parameter change (via an injectable ``propose_fn``) and
re-running fdars to observe the effect.  The loop is:

- **Fully offline-testable** — ``propose_fn`` is injectable; tests pass a mock.
- **Provably bounded** — terminates on five conditions (budget, converged,
  oscillation, guard_stop, parse_failure) checked in strict precedence order.
- **LLM-free at module load** — no ``anthropic`` / provider import at the top
  level; those imports (when used) live inside the caller's ``propose_fn``
  closure, never inside the loop core (TUNE-01, T-53A-04).
- **Grounding invariant** — fdars computes every number; the loop only
  orchestrates.

Termination precedence (checked each iteration in this exact order):
  1. step >= max_steps                → stop_reason "budget"
  2. propose_fn raises/returns bad   → stop_reason "parse_failure"
  3. rounded param already visited   → stop_reason "oscillation" (revisit)
  4. guard violated after re-run     → stop_reason "guard_stop"
  5. no_improve_count >= no_improve_window → stop_reason "converged"
  6. ping-pong on last 3 params      → stop_reason "oscillation" (ping-pong)

The guard check (step 4) is after the fdars re-run so the diagnostics are
available.  The oscillation-revisit check (step 3) is before the fdars re-run
to avoid a wasted fdars call on a known repeat.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional

from fdars.advisor._compare_methods import _METRIC_REGISTRY, _extract_metric_value

# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class _UnparseableProposalError(Exception):
    """Raised by a propose_fn that cannot produce a valid parameter dict.

    The loop exits immediately with stop_reason "parse_failure" without
    retrying the proposer (no LLM retry in the numeric path — TUNE-01).
    """


# ---------------------------------------------------------------------------
# Tunable-parameter registry
# ---------------------------------------------------------------------------

#: Registry of all six runnable methods.
#: ``tuneable: True`` entries declare the scalar parameter, its valid range,
#: target metric, and optional guard metrics.
#: ``tuneable: False`` entries carry a human-readable ``reason`` string; the
#: loop raises ``ValueError`` when asked to tune them.
_PARAM_REGISTRY: Dict[str, Dict[str, Any]] = {
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
            # key: rule string consumed by _check_guards
            # upper_fraction: current_val > 0.9 * n_obs (overfitting)
            "optimal_edf": "upper_fraction",
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
        "target_direction": "lower",   # from _METRIC_REGISTRY
        "guard_metrics": {
            # relative_degradation_20pct: current > initial * 1.2
            "optimal_gcv": "relative_degradation_20pct",
        },
    },
    "fpca": {
        "tuneable": True,
        "param": "n_comp",
        "param_type": int,
        "default": 3,
        # Upper bound clamped to min(n_obs // 2, 20) at runtime
        "range": (1, 20),
        "log_scale": False,
        "target_metric": "cumulative_variance_explained",  # extract last element
        "target_direction": "higher",  # from _METRIC_REGISTRY
        "guard_metrics": {
            # upper_threshold_0.5: val > 0.5 triggers phase leakage guard
            "phase_leakage_indicator": "upper_threshold_0.5",
        },
    },
    "clustering": {
        "tuneable": True,
        "param": "k",
        "param_type": int,
        "default": 3,
        # Upper bound clamped to min(n_obs // 3, 15) at runtime
        "range": (2, 15),
        "log_scale": False,
        "target_metric": "mean_amplitude_separation",
        "target_direction": "higher",  # from _METRIC_REGISTRY
        "guard_metrics": {
            # min_cluster_size_ge_2: min(cluster_sizes) < 2 → degenerate
            # NOTE: cluster_sizes is a list; guard uses isinstance check + min()
            "cluster_sizes": "min_cluster_size_ge_2",
        },
    },
    "alignment": {
        "tuneable": False,
        "reason": (
            "alignment has no registered metric in _METRIC_REGISTRY for its "
            "diagnostics; use fdars_compare_run to manually explore lambda_ values"
        ),
    },
    "depth": {
        "tuneable": False,
        "reason": "depth has no scalar tunable parameters",
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _round_param(value: Any, spec: Dict[str, Any]) -> Any:
    """Round a param value for the visited_params set.

    Integer params: returned as exact int.
    Float params: rounded to 4 significant figures to catch near-revisits
    without growing the set unboundedly.

    Parameters
    ----------
    value : int or float
        The proposed new param value.
    spec : dict
        The param spec dict from ``_PARAM_REGISTRY``.

    Returns
    -------
    int or float
        The rounded value for set membership tests.
    """
    if spec["param_type"] is int:
        return int(round(value))
    # Float: 4 significant figures
    if value == 0.0:
        return 0.0
    magnitude = math.floor(math.log10(abs(float(value))))
    ndigits = 4 - int(magnitude) - 1
    return round(float(value), ndigits)


def _extract_target(diagnostics: Dict[str, Any], metric: str) -> Optional[float]:
    """Extract a scalar target value from a diagnostics dict.

    Delegates to ``_extract_metric_value`` from ``_compare_methods`` so that
    list-valued metrics (e.g. ``cumulative_variance_explained``) are handled
    correctly (last element extracted as the scalar — Open Question 3).

    Returns ``None`` when the metric is absent or cannot be reduced to float.
    """
    return _extract_metric_value(diagnostics, metric)


def _is_improvement(new_val: float, prev_val: float, direction: str) -> bool:
    """Return True when ``new_val`` is strictly better than ``prev_val``.

    Uses ``direction`` from ``_METRIC_REGISTRY`` — ``"higher"`` means larger
    is better; ``"lower"`` means smaller is better.
    """
    if direction == "higher":
        return new_val > prev_val
    return new_val < prev_val


def _check_guards(
    diag: Dict[str, Any],
    guard_thresholds: Dict[str, str],
    initial_diag: Dict[str, Any],
    n_obs: Optional[int] = None,
) -> List[str]:
    """Check all guard metrics and return a list of violation descriptions.

    Guard rules are deterministic Python — no LLM involved (TUNE-05, T-53A-03).

    Parameters
    ----------
    diag : dict
        Current step's diagnostics dict.
    guard_thresholds : dict
        Mapping from guard metric key to rule string.  Rule strings are:
        ``"upper_fraction"``, ``"relative_degradation_20pct"``,
        ``"upper_threshold_0.5"``, ``"min_cluster_size_ge_2"``.
    initial_diag : dict
        Diagnostics dict from the very first fdars call (loop start).  Used
        by rules that compare against the initial baseline.
    n_obs : int or None
        Number of observations in the dataset.  Required for the
        ``"upper_fraction"`` rule (smoothing EDF guard).

    Returns
    -------
    list[str]
        Human-readable violation descriptions; empty list when all guards ok.
    """
    violations: List[str] = []
    for guard_key, rule in guard_thresholds.items():
        if rule == "upper_fraction":
            # smoothing: optimal_edf > 0.9 * n_obs (overfitting basis)
            edf = diag.get("optimal_edf")
            # n_obs from loop state (not diagnostics — Open Question 1)
            if edf is not None and n_obs is not None:
                threshold = 0.9 * n_obs
                if edf > threshold:
                    violations.append(
                        f"{guard_key}={edf:.3f} exceeds 0.9*n_obs={threshold:.1f}"
                    )
        elif rule == "relative_degradation_20pct":
            # basis: optimal_gcv degraded > 20% from initial
            current = diag.get(guard_key)
            initial = initial_diag.get(guard_key)
            if current is not None and initial is not None and initial > 0:
                if current > initial * 1.2:
                    violations.append(
                        f"{guard_key} degraded "
                        f"{100 * (current / initial - 1):.1f}% from initial"
                    )
        elif rule == "upper_threshold_0.5":
            # fpca: phase_leakage_indicator > 0.5
            val = diag.get(guard_key)
            if val is not None and val > 0.5:
                violations.append(
                    f"{guard_key}={val:.3f} exceeds threshold 0.5"
                )
        elif rule == "min_cluster_size_ge_2":
            # clustering: min(cluster_sizes) < 2 → degenerate cluster
            # T-53A-03: isinstance check prevents silent TypeError
            sizes = diag.get(guard_key)
            if sizes is not None and isinstance(sizes, list) and len(sizes) > 0:
                min_size = min(sizes)
                if min_size < 2:
                    violations.append(
                        f"min cluster size={min_size} below 2 (degenerate cluster)"
                    )
    return violations


def _is_ping_pong(
    recent_param_values: List[float],
    recent_targets: List[float],
    eps: float,
) -> bool:
    """Detect ping-pong oscillation in the last three accepted param values.

    Fires when the last 3 accepted param values alternate direction
    (A > B < A or A < B > A) AND all three target values are within ``eps``
    of each other (flat landscape, oscillating param).

    Parameters
    ----------
    recent_param_values : list[float]
        Last three accepted param values (chronological order).
    recent_targets : list[float]
        Corresponding target values.
    eps : float
        Convergence threshold; targets within eps of each other trigger ping-pong.

    Returns
    -------
    bool
        True when ping-pong oscillation is detected.
    """
    if len(recent_param_values) < 3 or len(recent_targets) < 3:
        return False
    a, b, c = recent_param_values[-3], recent_param_values[-2], recent_param_values[-1]
    # Alternating direction: (A > B < A) or (A < B > A)
    alternating = (a > b < c) or (a < b > c)
    if not alternating:
        return False
    # Targets within eps of each other
    t_a, t_b, t_c = recent_targets[-3], recent_targets[-2], recent_targets[-1]
    t_range = max(t_a, t_b, t_c) - min(t_a, t_b, t_c)
    return t_range <= eps


# ---------------------------------------------------------------------------
# Test seam: mock propose_fn factory
# ---------------------------------------------------------------------------


def _make_mock_propose_fn(deltas: List[float]) -> Callable:
    """Return a mock proposer that replays a fixed list of deltas.

    Each call adds the next delta to the single param value.  Raises
    ``StopIteration`` when the delta list is exhausted (allowing the test to
    detect unexpected extra calls).

    Parameters
    ----------
    deltas : list[float]
        List of delta values to replay.

    Returns
    -------
    callable
        ``propose_fn(current_params: dict, history: list) -> dict``
    """
    deltas_iter = iter(deltas)

    def propose_fn(current_params: Dict[str, Any], history: List[Dict]) -> Dict[str, Any]:
        delta = next(deltas_iter)  # raises StopIteration when exhausted
        param = list(current_params.keys())[0]
        return {param: current_params[param] + delta}

    return propose_fn


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run_tuning_loop(
    dataset_id: str,
    method: str,
    initial_params: Dict[str, Any],
    target_metric: str,
    propose_fn: Callable,
    *,
    max_steps: int = 10,
    eps: float = 1e-4,
    no_improve_window: int = 3,
    guard_thresholds: Optional[Dict[str, str]] = None,
    argvals=None,
    seed: Optional[int] = None,
    propose_fn_label: str = "mock",
    # Test seams: injectable run_method and build_diagnostics
    _run_method: Optional[Callable] = None,
    _build_diagnostics: Optional[Callable] = None,
) -> "TuningTrace":  # noqa: F821
    """Execute the bounded closed-loop tuning orchestration.

    The loop alternates: propose (via ``propose_fn``) → apply → re-run fdars
    → rebuild diagnostics → compare → guard check → termination decision →
    record TuningStep.  Terminates on five conditions checked in strict
    precedence order (see module docstring).

    Parameters
    ----------
    dataset_id : str
        Opaque dataset handle registered in the MCP registry.  May be any
        string when ``_run_method`` and ``_build_diagnostics`` are injected.
    method : str
        The fdars method being tuned (e.g. ``"smoothing"``).
    initial_params : dict
        Starting param dict.  Must contain exactly the tunable scalar key
        declared in ``_PARAM_REGISTRY[method]``.
    target_metric : str
        Diagnostic metric key to optimise (must be in ``_METRIC_REGISTRY``).
    propose_fn : callable
        ``propose_fn(current_params: dict, history: list[dict]) -> dict``.
        Returns a dict with exactly one key — the tunable parameter name —
        mapped to the proposed new scalar value.  Extra keys (e.g. ``seed``)
        are silently ignored so callers do not need to strip them.  Raise
        ``_UnparseableProposalError`` on failure.
    max_steps : int
        Maximum number of loop iterations (hard cap; budget check is FIRST).
    eps : float
        Minimum absolute improvement per accepted step for the convergence
        window; also the ping-pong target-range threshold.
    no_improve_window : int
        Number of consecutive non-improving steps before declaring convergence.
    guard_thresholds : dict or None
        Mapping from guard metric key to rule string.  When ``None``, no guard
        check is performed.
    argvals : array_like or None
        Grid values forwarded to ``build_diagnostics`` for distance-based
        metrics (clustering, alignment).
    seed : int or None
        Fixed random seed forwarded to every ``run_method`` call (for
        clustering reproducibility — Pitfall 7).
    propose_fn_label : str
        Label threaded into every ``TuningStep.proposal_source`` field so the
        trace distinguishes the proposer type in post-hoc analysis.  Callers
        should pass ``"llm"`` (``auto_tune``), ``"heuristic"``
        (``run_tuning_loop_mcp``), or ``"mock"`` (tests).  Defaults to
        ``"mock"`` for backward compatibility.
    _run_method : callable or None
        Test seam: replaces the real fdars run_method.
    _build_diagnostics : callable or None
        Test seam: replaces the real fdars build_diagnostics.

    Returns
    -------
    TuningTrace
        Complete record of the loop run.

    Raises
    ------
    ValueError
        When ``method`` is not in ``_PARAM_REGISTRY``, when the method is not
        tuneable, or when ``target_metric`` is not in ``_METRIC_REGISTRY``.
    """
    from fdars.advisor._schema import TuningStep, TuningTrace  # local: LLM-free path

    # -----------------------------------------------------------------------
    # Validate max_steps (WR-04: must be >= 1 to avoid zero-step edge cases)
    # -----------------------------------------------------------------------
    if max_steps < 1:
        raise ValueError(
            f"run_tuning_loop: max_steps must be >= 1, got {max_steps}."
        )

    # -----------------------------------------------------------------------
    # Validate method and target_metric
    # -----------------------------------------------------------------------
    if method not in _PARAM_REGISTRY:
        raise ValueError(
            f"run_tuning_loop: method {method!r} not in _PARAM_REGISTRY. "
            f"Supported: {sorted(_PARAM_REGISTRY)!r}."
        )
    param_spec = _PARAM_REGISTRY[method]
    if not param_spec.get("tuneable", False):
        raise ValueError(
            f"run_tuning_loop: {method!r} is not tuneable. "
            f"Reason: {param_spec.get('reason', 'no reason given')}."
        )
    if target_metric not in _METRIC_REGISTRY:
        raise ValueError(
            f"run_tuning_loop: target_metric {target_metric!r} not in "
            f"_METRIC_REGISTRY. Supported: {sorted(_METRIC_REGISTRY)!r}."
        )

    target_direction = _METRIC_REGISTRY[target_metric]
    param_name = param_spec["param"]
    lo, hi = param_spec["range"]

    # -----------------------------------------------------------------------
    # Resolve run_method and build_diagnostics (lazy imports for real paths)
    # -----------------------------------------------------------------------
    if _run_method is None:
        from fdars.mcp._runner import run_method as _real_run_method  # noqa: PLC0415
        run_method_fn = _real_run_method
    else:
        run_method_fn = _run_method

    if _build_diagnostics is None:
        from fdars.advisor import build_diagnostics as _real_build_diagnostics  # noqa: PLC0415
        build_diagnostics_fn = _real_build_diagnostics
    else:
        build_diagnostics_fn = _build_diagnostics

    # -----------------------------------------------------------------------
    # Extract seed from initial_params for fixed forwarding (Pitfall 7)
    # -----------------------------------------------------------------------
    if seed is None:
        seed = initial_params.get("seed")
    # fixed_params: params that are NOT the tunable param (e.g. seed for clustering)
    fixed_params: Dict[str, Any] = {
        k: v for k, v in initial_params.items() if k != param_name
    }

    # -----------------------------------------------------------------------
    # Compute initial diagnostics and target value
    # -----------------------------------------------------------------------
    current_params: Dict[str, Any] = dict(initial_params)

    # Determine n_obs for the smoothing guard (Open Question 1)
    # When a real dataset_id is given and no _run_method override, fetch from registry
    n_obs: Optional[int] = None
    if _run_method is None and dataset_id:
        try:
            from fdars.mcp._registry import registry as _registry  # noqa: PLC0415
            _entry = _registry.get(dataset_id)
            if _entry is not None:
                _data = _entry[0] if isinstance(_entry, (tuple, list)) else _entry
                n_obs = int(_data.shape[0]) if hasattr(_data, "shape") else None
        except Exception:
            n_obs = None

    # Run initial fdars call to get the baseline diagnostics
    _call_kwargs: Dict[str, Any] = {**current_params}
    if seed is not None and "seed" not in _call_kwargs:
        _call_kwargs["seed"] = seed
    initial_result = run_method_fn(dataset_id, method, **_call_kwargs)
    initial_diag: Dict[str, Any] = build_diagnostics_fn(
        initial_result, method, argvals=argvals
    )
    initial_target = _extract_target(initial_diag, target_metric)
    if initial_target is None:
        raise ValueError(
            f"run_tuning_loop: target_metric {target_metric!r} absent from "
            f"initial diagnostics for method {method!r}."
        )

    # -----------------------------------------------------------------------
    # Loop state
    # -----------------------------------------------------------------------
    prev_target: float = initial_target
    current_diag: Dict[str, Any] = initial_diag
    no_improve_count: int = 0
    visited_params: set = set()
    # Accepted-step history for ping-pong detection and propose_fn
    accepted_history: List[Dict[str, Any]] = []
    # Recorded steps for TuningTrace
    steps_recorded: List[TuningStep] = []
    stop_reason: str = "budget"
    step: int = 0

    while True:
        # -------------------------------------------------------------------
        # TERMINATION 1: Budget check (FIRST — Pitfall 3, T-53A-01)
        # -------------------------------------------------------------------
        if step >= max_steps:
            stop_reason = "budget"
            break

        param_before = current_params.get(param_name, param_spec["default"])

        # -------------------------------------------------------------------
        # Call propose_fn
        # -------------------------------------------------------------------
        try:
            new_params = propose_fn(current_params, accepted_history)
        except _UnparseableProposalError:
            # -------------------------------------------------------------------
            # TERMINATION 2: Parse failure (no retry — TUNE-01)
            # -------------------------------------------------------------------
            stop_reason = "parse_failure"
            # Record a rejected step with no target_after
            steps_recorded.append(TuningStep(
                step=step,
                param_before=float(param_before),
                param_after=float(param_before),
                target_before=float(prev_target),
                target_after=None,
                accepted=False,
                stop_reason="parse_failure",
                guard_violations=[],
                proposal_source=propose_fn_label,
            ))
            break

        # -------------------------------------------------------------------
        # TERMINATION 2b: Key-set validation (Pitfall 8)
        # WR-03 fix: require the tunable param key; ignore extra keys (e.g.
        # seed) so propose_fn implementations do not need to strip them.
        # -------------------------------------------------------------------
        if param_name not in new_params:
            stop_reason = "parse_failure"
            steps_recorded.append(TuningStep(
                step=step,
                param_before=float(param_before),
                param_after=float(param_before),
                target_before=float(prev_target),
                target_after=None,
                accepted=False,
                stop_reason="parse_failure",
                guard_violations=[],
                proposal_source=propose_fn_label,
            ))
            break

        # Clamp proposed value to declared range
        raw_new_val = new_params[param_name]
        new_val: Any = max(lo, min(hi, raw_new_val))
        if param_spec["param_type"] is int:
            new_val = int(round(new_val))

        # -------------------------------------------------------------------
        # TERMINATION 3: Oscillation — param revisit
        # -------------------------------------------------------------------
        rounded = _round_param(new_val, param_spec)
        if rounded in visited_params:
            stop_reason = "oscillation"
            steps_recorded.append(TuningStep(
                step=step,
                param_before=float(param_before),
                param_after=float(new_val),
                target_before=float(prev_target),
                target_after=None,
                accepted=False,
                stop_reason="oscillation",
                guard_violations=[],
                proposal_source=propose_fn_label,
            ))
            break

        # -------------------------------------------------------------------
        # Apply: re-run fdars with the proposed param
        # -------------------------------------------------------------------
        apply_kwargs: Dict[str, Any] = {**fixed_params, param_name: new_val}
        if seed is not None and "seed" not in apply_kwargs:
            apply_kwargs["seed"] = seed
        new_result = run_method_fn(dataset_id, method, **apply_kwargs)
        new_diag: Dict[str, Any] = build_diagnostics_fn(
            new_result, method, argvals=argvals
        )
        new_target_raw = _extract_target(new_diag, target_metric)
        new_target: float = new_target_raw if new_target_raw is not None else prev_target

        # -------------------------------------------------------------------
        # TERMINATION 4: Guard check (after re-run — Goodhart, TUNE-05)
        # -------------------------------------------------------------------
        guard_violations: List[str] = []
        if guard_thresholds:
            guard_violations = _check_guards(new_diag, guard_thresholds, initial_diag, n_obs)
            if guard_violations:
                stop_reason = "guard_stop"
                steps_recorded.append(TuningStep(
                    step=step,
                    param_before=float(param_before),
                    param_after=float(new_val),
                    target_before=float(prev_target),
                    target_after=float(new_target),
                    accepted=False,
                    stop_reason="guard_stop",
                    guard_violations=guard_violations,
                    proposal_source=propose_fn_label,
                ))
                break

        # -------------------------------------------------------------------
        # Improvement check
        # -------------------------------------------------------------------
        improved = _is_improvement(new_target, prev_target, target_direction)

        if improved:
            no_improve_count = 0
            visited_params.add(rounded)
            # Update accepted history
            accepted_history.append({
                "step": step,
                "param_value": new_val,
                "target_value": new_target,
                "accepted": True,
            })
            # Update current state
            current_params = {**fixed_params, param_name: new_val}
            if seed is not None:
                current_params["seed"] = seed
            prev_target = new_target
            current_diag = new_diag

            # -------------------------------------------------------------------
            # TERMINATION 6: Ping-pong (after improvement, check last 3 accepted)
            # -------------------------------------------------------------------
            recent_params = [h["param_value"] for h in accepted_history]
            recent_targets = [h["target_value"] for h in accepted_history]
            if _is_ping_pong(recent_params, recent_targets, eps):
                stop_reason = "oscillation"
                steps_recorded.append(TuningStep(
                    step=step,
                    param_before=float(param_before),
                    param_after=float(new_val),
                    target_before=float(prev_target if not improved else
                                        accepted_history[-2]["target_value"]
                                        if len(accepted_history) >= 2 else initial_target),
                    target_after=float(new_target),
                    accepted=True,
                    stop_reason="oscillation",
                    guard_violations=[],
                    proposal_source=propose_fn_label,
                ))
                step += 1
                break

            # Normal accepted step
            steps_recorded.append(TuningStep(
                step=step,
                param_before=float(param_before),
                param_after=float(new_val),
                target_before=float(accepted_history[-2]["target_value"]
                                    if len(accepted_history) >= 2 else initial_target),
                target_after=float(new_target),
                accepted=True,
                stop_reason=None,
                guard_violations=[],
                proposal_source=propose_fn_label,
            ))
        else:
            no_improve_count += 1
            # Record rejected step (do NOT add to visited_params)
            steps_recorded.append(TuningStep(
                step=step,
                param_before=float(param_before),
                param_after=float(new_val),
                target_before=float(prev_target),
                target_after=float(new_target),
                accepted=False,
                stop_reason=None,
                guard_violations=[],
                proposal_source=propose_fn_label,
            ))

            # -------------------------------------------------------------------
            # TERMINATION 5: Convergence (K consecutive non-improvements)
            # -------------------------------------------------------------------
            if no_improve_count >= no_improve_window:
                stop_reason = "converged"
                # Tag the last recorded step with the stop_reason
                if steps_recorded:
                    last = steps_recorded[-1]
                    last.stop_reason = "converged"
                break

        step += 1

    # -----------------------------------------------------------------------
    # Assemble TuningTrace
    # -----------------------------------------------------------------------
    final_param_val = current_params.get(param_name, param_spec["default"])
    final_params_out = {param_name: final_param_val}

    # Use len(steps_recorded) as the authoritative step count — covers all
    # stop paths consistently.  The loop variable ``step`` is 0-indexed and
    # is NOT incremented before break for parse_failure, oscillation-revisit,
    # guard_stop, and converged stops, making ``step`` one short of the true
    # count for those paths.  len(steps_recorded) is always exact.
    n_steps_actual = len(steps_recorded)

    return TuningTrace(
        method=method,
        param=param_name,
        target_metric=target_metric,
        target_direction=target_direction,
        steps=steps_recorded,
        final_params=final_params_out,
        final_diagnostics=dict(current_diag),
        converged=(stop_reason == "converged"),
        stop_reason=stop_reason,
        n_steps=n_steps_actual,
        steps_used=n_steps_actual,
        budget_remaining=max(0, max_steps - n_steps_actual),
    )
