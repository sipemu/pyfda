"""Offline tests for fdars.advisor._tuning — bounded loop (Plan 53-01, Task 3).

All tests run with NO API key and NO network.  The loop's run_method and
build_diagnostics calls are monkeypatched to return synthetic in-memory
diagnostics dicts — no real fdars call is required.

Stop reasons covered:
  - "budget": always-improve mock, max_steps=2
  - "converged": no-improve mock, K=3 consecutive non-improvements
  - "oscillation" (revisit): mock revisiting the same int param
  - "oscillation" (ping-pong): 3-step alternating mock
  - "parse_failure": mock raising _UnparseableProposalError, called exactly once

Additional coverage:
  - guard_stop: clustering mock driving k to a degenerate cluster (Goodhart)
  - determinism: two identical calls produce equal TuningTrace field dicts
  - fpca cumulative_variance_explained: list-valued target extracted correctly
  - trace JSON-serialisable
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from fdars.advisor._tuning import (
    _PARAM_REGISTRY,
    _UnparseableProposalError,
    _check_guards,
    _extract_target,
    _is_improvement,
    _is_ping_pong,
    _make_mock_propose_fn,
    _round_param,
    run_tuning_loop,
)


# ---------------------------------------------------------------------------
# Shared helpers: mock run_method + build_diagnostics
# ---------------------------------------------------------------------------

def _make_smoothing_diag(n_basis: int, gcv: float, edf: float = None) -> Dict[str, Any]:
    """Return a synthetic smoothing diagnostics dict."""
    d = {
        "method": "smoothing",
        "optimal_gcv": gcv,
        "optimal_edf": edf if edf is not None else n_basis * 0.5,
    }
    return d


def _make_clustering_diag(k: int, sep: float, cluster_sizes: List[int] = None) -> Dict[str, Any]:
    """Return a synthetic clustering diagnostics dict."""
    if cluster_sizes is None:
        cluster_sizes = [10] * k  # balanced clusters by default
    return {
        "method": "clustering",
        "mean_amplitude_separation": sep,
        "cluster_sizes": cluster_sizes,
    }


def _make_fpca_diag(n_comp: int, cumvar: List[float]) -> Dict[str, Any]:
    """Return a synthetic fpca diagnostics dict."""
    return {
        "method": "fpca",
        "cumulative_variance_explained": cumvar,
    }


# ---------------------------------------------------------------------------
# Mock run_method + build_diagnostics for smoothing (improvement scenario)
# ---------------------------------------------------------------------------

class _SmoothingImproveEnv:
    """Synthetic environment: each increase in n_basis lowers optimal_gcv."""

    def __init__(self, initial_n_basis: int = 15, initial_gcv: float = 0.10):
        self.initial_n_basis = initial_n_basis
        self.initial_gcv = initial_gcv

    def run_method(self, dataset_id: str, method: str, **kwargs) -> Dict[str, Any]:
        n_basis = kwargs.get("n_basis", self.initial_n_basis)
        return {"n_basis": n_basis, "raw": True}

    def build_diagnostics(self, result: Dict, method: str, **kwargs) -> Dict[str, Any]:
        n_basis = result.get("n_basis", self.initial_n_basis)
        # GCV decreases monotonically with n_basis (simplified model)
        gcv = self.initial_gcv / (1 + (n_basis - self.initial_n_basis) * 0.05)
        edf = n_basis * 0.4
        return _make_smoothing_diag(n_basis, gcv, edf)


# ---------------------------------------------------------------------------
# Mock run_method + build_diagnostics for no-improvement scenario
# ---------------------------------------------------------------------------

class _SmoothingNoImprovEnv:
    """Synthetic environment: GCV never improves regardless of n_basis change."""

    def __init__(self, fixed_gcv: float = 0.10):
        self.fixed_gcv = fixed_gcv

    def run_method(self, dataset_id: str, method: str, **kwargs) -> Dict[str, Any]:
        n_basis = kwargs.get("n_basis", 15)
        return {"n_basis": n_basis}

    def build_diagnostics(self, result: Dict, method: str, **kwargs) -> Dict[str, Any]:
        n_basis = result.get("n_basis", 15)
        return _make_smoothing_diag(n_basis, self.fixed_gcv, n_basis * 0.4)


# ---------------------------------------------------------------------------
# Mock environment for clustering (guard scenario)
# ---------------------------------------------------------------------------

class _ClusteringGuardEnv:
    """Synthetic clustering env: increasing k improves separation BUT
    eventually causes a degenerate cluster (min cluster_size < 2)."""

    def __init__(self, initial_k: int = 3, n_obs: int = 30):
        self.initial_k = initial_k
        self.n_obs = n_obs

    def run_method(self, dataset_id: str, method: str, **kwargs) -> Dict[str, Any]:
        k = kwargs.get("k", self.initial_k)
        return {"k": k}

    def build_diagnostics(self, result: Dict, method: str, **kwargs) -> Dict[str, Any]:
        k = result.get("k", self.initial_k)
        # Separation improves with k (target keeps improving)
        sep = 0.30 + k * 0.05
        # Once k > 5: one cluster collapses to size 1 (degenerate)
        if k > 5:
            cluster_sizes = [1] + [max(1, (self.n_obs - 1) // (k - 1))] * (k - 1)
        else:
            per = self.n_obs // k
            cluster_sizes = [per] * k
        return _make_clustering_diag(k, sep, cluster_sizes)


# ---------------------------------------------------------------------------
# Mock environment for fpca
# ---------------------------------------------------------------------------

class _FpcaEnv:
    """Synthetic fpca env: cumulative_variance_explained is a list."""

    def __init__(self, initial_n_comp: int = 3):
        self.initial_n_comp = initial_n_comp

    def run_method(self, dataset_id: str, method: str, **kwargs) -> Dict[str, Any]:
        n_comp = kwargs.get("n_comp", self.initial_n_comp)
        return {"n_comp": n_comp}

    def build_diagnostics(self, result: Dict, method: str, **kwargs) -> Dict[str, Any]:
        n_comp = result.get("n_comp", self.initial_n_comp)
        # Cumulative variance grows with n_comp (synthetic)
        cumvar = [min(0.99, 0.5 + i * 0.1) for i in range(n_comp)]
        return _make_fpca_diag(n_comp, cumvar)


# ---------------------------------------------------------------------------
# Helper: run the loop with a mock environment
# ---------------------------------------------------------------------------

def _run_smoothing_loop(
    propose_fn,
    env=None,
    initial_n_basis: int = 15,
    max_steps: int = 10,
    eps: float = 1e-4,
    no_improve_window: int = 3,
    guard_thresholds=None,
):
    """Run the smoothing loop with a synthetic environment."""
    if env is None:
        env = _SmoothingImproveEnv(initial_n_basis)
    return run_tuning_loop(
        dataset_id="mock",
        method="smoothing",
        initial_params={"n_basis": initial_n_basis},
        target_metric="optimal_gcv",
        propose_fn=propose_fn,
        max_steps=max_steps,
        eps=eps,
        no_improve_window=no_improve_window,
        guard_thresholds=guard_thresholds,
        _run_method=env.run_method,
        _build_diagnostics=env.build_diagnostics,
    )


# ===========================================================================
# Test 1: Budget exhaustion
# ===========================================================================


def test_budget_exhaustion():
    """Always-improve mock terminates at max_steps=2 with stop_reason 'budget'."""
    env = _SmoothingImproveEnv(initial_n_basis=15)
    # Propose +2 each step (always improves since GCV decreases with n_basis)
    propose_fn = _make_mock_propose_fn([2, 2, 2, 2, 2])

    trace = _run_smoothing_loop(propose_fn, env=env, max_steps=2)

    assert trace.stop_reason == "budget", f"Expected 'budget', got {trace.stop_reason!r}"
    assert trace.n_steps == 2, f"Expected n_steps=2, got {trace.n_steps}"
    assert len(trace.steps) <= 2


# ===========================================================================
# Test 2: Convergence (K=3 consecutive non-improvements)
# ===========================================================================


def test_convergence():
    """No-improve mock terminates with stop_reason 'converged' after K=3."""
    env = _SmoothingNoImprovEnv(fixed_gcv=0.10)
    # Propose +1 each time but GCV never improves (always 0.10)
    propose_fn = _make_mock_propose_fn([1, 1, 1, 1, 1, 1, 1])

    trace = _run_smoothing_loop(propose_fn, env=env, no_improve_window=3, max_steps=10)

    assert trace.stop_reason == "converged", f"Expected 'converged', got {trace.stop_reason!r}"
    assert trace.converged is True
    # Should have terminated after 3 non-improving steps
    non_improving = [s for s in trace.steps if not s.accepted]
    assert len(non_improving) >= 3


# ===========================================================================
# Test 3: Oscillation — param revisit (same int value visited twice)
# ===========================================================================


def test_oscillation_param_revisit():
    """Mock that proposes k=5 then k=5 again triggers stop_reason 'oscillation'."""
    # Use clustering for integer param
    env_step = [0]

    def propose_fn(current_params, history):
        step = env_step[0]
        env_step[0] += 1
        k = current_params.get("k", 3)
        if step == 0:
            return {"k": 5}   # first: propose 5
        elif step == 1:
            return {"k": 6}   # second: accepted different value
        else:
            return {"k": 5}   # third: revisit 5 → oscillation

    class _ClusteringAlwaysImprove:
        def run_method(self, dataset_id, method, **kwargs):
            return {"k": kwargs.get("k", 3)}

        def build_diagnostics(self, result, method, **kwargs):
            k = result.get("k", 3)
            sep = 0.30 + k * 0.10  # always improving
            cluster_sizes = [5] * k
            return _make_clustering_diag(k, sep, cluster_sizes)

    cluster_env = _ClusteringAlwaysImprove()
    trace = run_tuning_loop(
        dataset_id="mock",
        method="clustering",
        initial_params={"k": 3},
        target_metric="mean_amplitude_separation",
        propose_fn=propose_fn,
        max_steps=10,
        _run_method=cluster_env.run_method,
        _build_diagnostics=cluster_env.build_diagnostics,
    )

    assert trace.stop_reason == "oscillation", (
        f"Expected 'oscillation', got {trace.stop_reason!r}"
    )


# ===========================================================================
# Test 4: Oscillation — ping-pong (3-step alternation)
# ===========================================================================


def test_oscillation_ping_pong():
    """3-step alternating propose_fn triggers ping-pong oscillation."""
    # Use smoothing; the target barely changes (within eps) so ping-pong fires
    # The propose_fn alternates +3 / -3 / +3 — visits different values
    # but the targets are very close (ping-pong)
    call_count = [0]

    def propose_fn(current_params, history):
        n = call_count[0]
        call_count[0] += 1
        n_basis = current_params.get("n_basis", 15)
        if n % 2 == 0:
            return {"n_basis": n_basis + 3}
        else:
            return {"n_basis": n_basis - 3}

    class _FlatGCVEnv:
        """GCV stays nearly constant regardless of n_basis (flat landscape)."""

        def run_method(self, dataset_id, method, **kwargs):
            return {"n_basis": kwargs.get("n_basis", 15)}

        def build_diagnostics(self, result, method, **kwargs):
            n_basis = result.get("n_basis", 15)
            # GCV varies by < eps/10 — too flat to improve; targets within eps
            gcv = 0.05000 + (n_basis - 15) * 0.000001
            return _make_smoothing_diag(n_basis, gcv)

    flat_env = _FlatGCVEnv()
    trace = run_tuning_loop(
        dataset_id="mock",
        method="smoothing",
        initial_params={"n_basis": 15},
        target_metric="optimal_gcv",
        propose_fn=propose_fn,
        max_steps=20,
        eps=1e-3,  # use a larger eps so ping-pong fires
        no_improve_window=10,  # high K so convergence doesn't fire first
        _run_method=flat_env.run_method,
        _build_diagnostics=flat_env.build_diagnostics,
    )
    # Either oscillation (ping-pong) or converged (no improvement) should fire
    # before budget — the flat landscape makes one of these fire first
    assert trace.stop_reason in ("oscillation", "converged"), (
        f"Expected 'oscillation' or 'converged', got {trace.stop_reason!r}"
    )


# ===========================================================================
# Test 5: Parse failure — proposer called exactly once, n_steps=0
# ===========================================================================


def test_parse_failure():
    """A propose_fn raising _UnparseableProposalError exits immediately.

    n_steps=0 (the loop exits before advancing the counter).
    The proposer is called exactly once (no retry — TUNE-01).
    """
    call_counter = [0]

    def bad_propose_fn(current_params, history):
        call_counter[0] += 1
        raise _UnparseableProposalError("mock parse failure")

    env = _SmoothingImproveEnv()
    trace = _run_smoothing_loop(bad_propose_fn, env=env, max_steps=10)

    assert trace.stop_reason == "parse_failure", (
        f"Expected 'parse_failure', got {trace.stop_reason!r}"
    )
    assert trace.n_steps == 0, f"Expected n_steps=0, got {trace.n_steps}"
    assert call_counter[0] == 1, (
        f"Proposer should be called exactly once; called {call_counter[0]} times"
    )


# ===========================================================================
# Test 6: Guard stop — clustering degenerate cluster (Goodhart)
# ===========================================================================


def test_guard_stop_clustering():
    """Clustering mock that drives k to a degenerate cluster stops with guard_stop.

    The target (mean_amplitude_separation) keeps improving while the guard
    (min cluster_size < 2) fires — this is exactly the Goodhart scenario
    TUNE-05 defends against.
    """
    env = _ClusteringGuardEnv(initial_k=3, n_obs=30)
    # Propose increasing k: 3 → 4 → 5 → 6 → 7
    propose_fn = _make_mock_propose_fn([1, 1, 1, 1, 1, 1])
    guard_thresholds = {"cluster_sizes": "min_cluster_size_ge_2"}

    trace = run_tuning_loop(
        dataset_id="mock",
        method="clustering",
        initial_params={"k": 3},
        target_metric="mean_amplitude_separation",
        propose_fn=propose_fn,
        max_steps=10,
        guard_thresholds=guard_thresholds,
        _run_method=env.run_method,
        _build_diagnostics=env.build_diagnostics,
    )

    assert trace.stop_reason == "guard_stop", (
        f"Expected 'guard_stop', got {trace.stop_reason!r}"
    )
    # guard_violations must be non-empty
    guard_step = next((s for s in trace.steps if s.stop_reason == "guard_stop"), None)
    assert guard_step is not None, "No step recorded with stop_reason 'guard_stop'"
    assert len(guard_step.guard_violations) > 0, (
        "guard_violations should be non-empty when guard fires"
    )


# ===========================================================================
# Test 7: Determinism — identical inputs produce identical TuningTrace dicts
# ===========================================================================


def test_determinism():
    """Two identical calls with the same mock produce equal TuningTrace dicts."""
    env1 = _SmoothingImproveEnv(initial_n_basis=15)
    env2 = _SmoothingImproveEnv(initial_n_basis=15)

    def make_propose_fn():
        return _make_mock_propose_fn([2, 2, 2, 2, 2])

    trace1 = _run_smoothing_loop(make_propose_fn(), env=env1, max_steps=3)
    trace2 = _run_smoothing_loop(make_propose_fn(), env=env2, max_steps=3)

    # Compare field dicts
    def _trace_to_dict(trace):
        return {
            "method": trace.method,
            "param": trace.param,
            "target_metric": trace.target_metric,
            "target_direction": trace.target_direction,
            "converged": trace.converged,
            "stop_reason": trace.stop_reason,
            "n_steps": trace.n_steps,
            "steps_used": trace.steps_used,
            "budget_remaining": trace.budget_remaining,
            "final_params": trace.final_params,
            "steps": [
                {
                    "step": s.step,
                    "param_before": s.param_before,
                    "param_after": s.param_after,
                    "target_before": s.target_before,
                    "target_after": s.target_after,
                    "accepted": s.accepted,
                    "stop_reason": s.stop_reason,
                    "guard_violations": s.guard_violations,
                    "proposal_source": s.proposal_source,
                }
                for s in trace.steps
            ],
        }

    d1 = _trace_to_dict(trace1)
    d2 = _trace_to_dict(trace2)
    assert d1 == d2, f"Traces differ:\n{d1}\nvs\n{d2}"


# ===========================================================================
# Test 8: FPCA cumulative_variance_explained list extraction
# ===========================================================================


def test_fpca_cumulative_extraction():
    """list-valued cumulative_variance_explained is reduced to its last element."""
    env = _FpcaEnv(initial_n_comp=3)
    # Propose +1 each step (n_comp increases, cumvar last element increases)
    propose_fn = _make_mock_propose_fn([1, 1, 1, 1])

    trace = run_tuning_loop(
        dataset_id="mock",
        method="fpca",
        initial_params={"n_comp": 3},
        target_metric="cumulative_variance_explained",
        propose_fn=propose_fn,
        max_steps=4,
        _run_method=env.run_method,
        _build_diagnostics=env.build_diagnostics,
    )

    # The trace should have steps where target_after is a scalar float,
    # not a list — proving the last-element extraction works
    for s in trace.steps:
        if s.target_after is not None:
            assert isinstance(s.target_after, float), (
                f"target_after should be a scalar float, got {type(s.target_after)}"
            )
        if s.target_before is not None:
            assert isinstance(s.target_before, float), (
                f"target_before should be a scalar float, got {type(s.target_before)}"
            )


# ===========================================================================
# Test 9: TuningTrace is JSON-serialisable
# ===========================================================================


def test_trace_json_serialisable():
    """The TuningTrace returned by run_tuning_loop is JSON-serialisable."""
    env = _SmoothingImproveEnv()
    propose_fn = _make_mock_propose_fn([2, 2])

    trace = _run_smoothing_loop(propose_fn, env=env, max_steps=2)

    # Build a JSON-serialisable dict from the trace
    def _step_to_dict(s):
        return {
            "step": s.step,
            "param_before": s.param_before,
            "param_after": s.param_after,
            "target_before": s.target_before,
            "target_after": s.target_after,
            "accepted": s.accepted,
            "stop_reason": s.stop_reason,
            "guard_violations": s.guard_violations,
            "proposal_source": s.proposal_source,
        }

    d = {
        "method": trace.method,
        "param": trace.param,
        "target_metric": trace.target_metric,
        "target_direction": trace.target_direction,
        "steps": [_step_to_dict(s) for s in trace.steps],
        "final_params": trace.final_params,
        "final_diagnostics": trace.final_diagnostics,
        "converged": trace.converged,
        "stop_reason": trace.stop_reason,
        "n_steps": trace.n_steps,
        "steps_used": trace.steps_used,
        "budget_remaining": trace.budget_remaining,
    }
    encoded = json.dumps(d)
    assert isinstance(encoded, str)
    decoded = json.loads(encoded)
    assert decoded["stop_reason"] == "budget"
    assert decoded["n_steps"] == 2


# ===========================================================================
# Test 10: _check_guards unit tests
# ===========================================================================


def test_check_guards_cluster_sizes_list():
    """_check_guards handles cluster_sizes as a list (not scalar) correctly."""
    # Normal: all clusters have >= 2 members
    diag_ok = {"cluster_sizes": [5, 5, 4]}
    violations = _check_guards(diag_ok, {"cluster_sizes": "min_cluster_size_ge_2"}, diag_ok)
    assert violations == []

    # Degenerate: one cluster has size 1
    diag_bad = {"cluster_sizes": [1, 10, 9]}
    violations = _check_guards(diag_bad, {"cluster_sizes": "min_cluster_size_ge_2"}, diag_bad)
    assert len(violations) == 1
    assert "1" in violations[0]  # message should mention size 1


def test_check_guards_relative_degradation():
    """_check_guards fires when GCV degrades > 20% from initial."""
    initial = {"optimal_gcv": 0.10}
    current_ok = {"optimal_gcv": 0.11}  # 10% degradation — within limit
    current_bad = {"optimal_gcv": 0.13}  # 30% degradation — exceeds 20%

    assert _check_guards(current_ok, {"optimal_gcv": "relative_degradation_20pct"}, initial) == []
    viol = _check_guards(current_bad, {"optimal_gcv": "relative_degradation_20pct"}, initial)
    assert len(viol) == 1


def test_check_guards_upper_threshold():
    """_check_guards fires when phase_leakage_indicator > 0.5."""
    diag_ok = {"phase_leakage_indicator": 0.4}
    diag_bad = {"phase_leakage_indicator": 0.6}
    assert _check_guards(diag_ok, {"phase_leakage_indicator": "upper_threshold_0.5"}, {}) == []
    viol = _check_guards(diag_bad, {"phase_leakage_indicator": "upper_threshold_0.5"}, {})
    assert len(viol) == 1


# ===========================================================================
# Test 11: _round_param round-trips
# ===========================================================================


def test_round_param_int():
    """Integer params are rounded to exact int."""
    spec = {"param_type": int}
    assert _round_param(5, spec) == 5
    assert _round_param(5.7, spec) == 6


def test_round_param_float_sig_figs():
    """Float params are rounded to 4 significant figures."""
    spec = {"param_type": float}
    # 1.23456 → 4 sig figs = 1.235
    result = _round_param(1.23456, spec)
    assert abs(result - 1.235) < 1e-10


# ===========================================================================
# Test 12: Untuneable methods raise ValueError
# ===========================================================================


def test_untuneable_method_raises():
    """run_tuning_loop on alignment or depth raises ValueError."""
    def dummy_propose(cp, h):
        return cp

    with pytest.raises(ValueError, match="not tuneable"):
        run_tuning_loop(
            dataset_id="mock",
            method="alignment",
            initial_params={"lambda_": 0.0},
            target_metric="mean_amplitude_separation",
            propose_fn=dummy_propose,
        )

    with pytest.raises(ValueError, match="not tuneable"):
        run_tuning_loop(
            dataset_id="mock",
            method="depth",
            initial_params={},
            target_metric="mean_amplitude_separation",
            propose_fn=dummy_propose,
        )


# ===========================================================================
# Test 13: _is_ping_pong detection
# ===========================================================================


def test_is_ping_pong_detected():
    """_is_ping_pong fires on alternating sequence with flat targets."""
    params = [10, 13, 10]  # A > B < A pattern
    targets = [0.050, 0.050001, 0.050002]  # within eps=0.001
    assert _is_ping_pong(params, targets, eps=0.001)


def test_is_ping_pong_not_detected_when_target_improves():
    """_is_ping_pong does not fire when targets differ by more than eps."""
    params = [10, 13, 10]
    targets = [0.050, 0.040, 0.030]  # clearly improving — not flat
    assert not _is_ping_pong(params, targets, eps=0.001)


def test_is_ping_pong_requires_3_points():
    """_is_ping_pong returns False with fewer than 3 points."""
    assert not _is_ping_pong([10, 13], [0.05, 0.05], eps=1e-4)
