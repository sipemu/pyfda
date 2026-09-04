"""Tests for the fdars MCP fdars_auto_tune tool (Plan 53-03).

Plan 53-03 tasks:
  - Task 1: heuristic propose_fn + run_tuning_loop_mcp helper (LLM-free).
  - Task 2: fdars_auto_tune @mcp.tool wrapper (validation + delegation).
  - Task 3: This test suite — proves LLM-free invariant, heuristic determinism,
    max_steps cap, by-reference return, and guard-sync no-op.

All tests are skipped on Python <3.10 via the module-level pytestmark.
No ANTHROPIC_API_KEY and no network are required (TUNE-04).

TUNE-04 truths verified:
  - file-scan: mcp/_tuning.py never references the LLM advisor token
  - determinism: two identical heuristic runs produce equal compact result dicts
  - max_steps hard cap: max_steps=21 raises ValueError
  - non-runnable method: raises ValueError naming supported set
  - by-reference: returned dict carries only scalars + handles (no lists/ndarrays)
  - guard-sync no-op: _RUNNABLE_METHODS==6, _DIAGNOSTICS_METHODS==14
"""

from __future__ import annotations

import sys

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Module-level skip guard: Python 3.9 CI runners skip cleanly (mirrors server.py)
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="mcp requires Python 3.10+",
)

# ---------------------------------------------------------------------------
# Autouse fixture: clear the registry after each test (Pitfall 3)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_registry():
    """Reset the handle registry after every test to prevent state leakage."""
    yield
    from fdars.mcp._registry import registry
    registry.clear()


# ---------------------------------------------------------------------------
# Dataset fixture: small synthetic dataset (offline, no API key)
# ---------------------------------------------------------------------------


@pytest.fixture()
def fpca_dataset_id():
    """Register a small synthetic dataset suitable for fpca tuning."""
    from fdars.mcp._registry import registry

    rng = np.random.default_rng(99)
    # 20 observations, 40 grid points — enough for fpca with default n_comp=3
    X = rng.standard_normal((20, 40))
    argvals = np.linspace(0, 1, 40)
    return registry.store_dataset(X, argvals)


# ---------------------------------------------------------------------------
# Task 3, TUNE-04: LLM-free file-scan invariant
# ---------------------------------------------------------------------------


def test_auto_tune_does_not_import_advise():
    """mcp/_tuning.py and the fdars_auto_tune handler must not reference the LLM path.

    File-scan invariant (extends test_tool_never_imports_advise in
    test_mcp_compare_methods.py to the new tuning helper).  The search token
    is built at runtime to avoid this test file self-flagging.
    """
    import pathlib

    # Build the search token at runtime to avoid this file self-flagging.
    _token = "adv" + "ise"

    repo_root = pathlib.Path(__file__).resolve().parents[1]

    # --- Scan mcp/_tuning.py (the new helper) ---
    tuning_helper = repo_root / "python" / "fdars" / "mcp" / "_tuning.py"
    assert tuning_helper.exists(), f"mcp/_tuning.py not found at {tuning_helper}"
    content_tuning = tuning_helper.read_text()
    assert _token not in content_tuning, (
        f"mcp/_tuning.py references '{_token}' (LLM-free invariant violation "
        f"TUNE-04, T-53C-01): the heuristic helper must never import the LLM advisor"
    )

    # --- Scan the fdars_auto_tune handler region of server.py ---
    server_file = repo_root / "python" / "fdars" / "mcp" / "server.py"
    assert server_file.exists(), f"server.py not found at {server_file}"
    server_text = server_file.read_text()

    # Locate the handler body — from its @mcp.tool() decorator to the next
    # top-level definition or end-of-file.  We only need to check that no
    # real advise import appears anywhere in the handler (the tool boundary
    # must stay LLM-free).
    handler_start = server_text.find("def fdars_auto_tune(")
    assert handler_start != -1, "fdars_auto_tune handler not found in server.py"
    # Find the start of the NEXT top-level def/class after the handler
    import re
    next_top = re.search(r"\ndef (run_stdio|[a-z])", server_text[handler_start + 1:])
    if next_top:
        handler_body = server_text[handler_start: handler_start + 1 + next_top.start()]
    else:
        handler_body = server_text[handler_start:]

    assert _token not in handler_body, (
        f"fdars_auto_tune handler in server.py references '{_token}' "
        f"(LLM-free invariant violation TUNE-04, T-53C-01)"
    )


# ---------------------------------------------------------------------------
# Heuristic determinism (TUNE-04)
# ---------------------------------------------------------------------------


def test_heuristic_deterministic(fpca_dataset_id):
    """Two run_tuning_loop_mcp calls with the same dataset + params produce equal dicts.

    Uses fpca (tuneable) with a fixed dataset and no initial_params override.
    The heuristic is deterministic given the same inputs — same result every call.
    """
    from fdars.mcp._tuning import run_tuning_loop_mcp

    kwargs = dict(
        dataset_id=fpca_dataset_id,
        method="fpca",
        initial_params={"n_comp": 3},
        target_metric="cumulative_variance_explained",
        max_steps=4,
    )

    result1 = run_tuning_loop_mcp(**kwargs)
    result2 = run_tuning_loop_mcp(**kwargs)

    # Compact scalar fields must be identical across two independent runs
    scalar_keys = {
        "method", "param", "target_metric", "stop_reason",
        "n_steps", "steps_used", "budget_remaining",
        "improved",
    }
    for key in scalar_keys:
        assert result1[key] == result2[key], (
            f"Determinism violated: result1[{key!r}]={result1[key]!r} "
            f"!= result2[{key!r}]={result2[key]!r}"
        )

    # Numeric fields (allow float tolerance due to floating-point, but should be equal)
    for key in ("initial_target_value", "final_target_value"):
        assert result1[key] == result2[key], (
            f"Determinism violated for {key!r}: {result1[key]} != {result2[key]}"
        )


# ---------------------------------------------------------------------------
# WR-02: seed defaults to 42 (determinism for clustering)
# ---------------------------------------------------------------------------


def test_seed_defaults_to_42_in_signature():
    """WR-02: fdars_auto_tune seed parameter must default to 42, not None.

    A default of None makes clustering runs non-deterministic by default.
    """
    import inspect
    from fdars.mcp.server import fdars_auto_tune

    sig = inspect.signature(fdars_auto_tune)
    seed_default = sig.parameters["seed"].default
    assert seed_default == 42, (
        f"WR-02: fdars_auto_tune seed must default to 42 for clustering "
        f"reproducibility (Pitfall 7); got default={seed_default!r}"
    )


# ---------------------------------------------------------------------------
# max_steps hard cap (TUNE-04, T-53C-02)
# ---------------------------------------------------------------------------


def test_max_steps_hard_cap():
    """fdars_auto_tune with max_steps=21 must raise ValueError (hard cap).

    The cap is enforced at the tool boundary before any loop execution.
    """
    from fdars.mcp.server import fdars_auto_tune

    with pytest.raises(ValueError, match="21"):
        fdars_auto_tune(
            dataset_id="ds-fake",
            method="fpca",
            max_steps=21,
        )


def test_max_steps_at_cap_is_ok(fpca_dataset_id):
    """max_steps=20 (exactly at the cap) must NOT raise ValueError."""
    from fdars.mcp.server import fdars_auto_tune

    # Should not raise — 20 is the hard cap boundary
    result = fdars_auto_tune(
        dataset_id=fpca_dataset_id,
        method="fpca",
        max_steps=20,
    )
    assert "stop_reason" in result


# ---------------------------------------------------------------------------
# Non-runnable method rejection (TUNE-04, T-53C-03)
# ---------------------------------------------------------------------------


def test_rejects_method_not_runnable():
    """fdars_auto_tune must raise ValueError for methods not in _RUNNABLE_METHODS.

    Uses 'regression' which is in _DIAGNOSTICS_METHODS but not _RUNNABLE_METHODS.
    """
    from fdars.mcp.server import fdars_auto_tune

    with pytest.raises(ValueError, match="regression"):
        fdars_auto_tune(
            dataset_id="ds-fake",
            method="regression",
        )


def test_rejects_non_tuneable_method(fpca_dataset_id):
    """fdars_auto_tune must raise ValueError for non-tuneable runnable methods.

    'alignment' and 'depth' are in _RUNNABLE_METHODS but not tuneable.
    The error is raised by run_tuning_loop_mcp after the tool boundary passes.
    """
    from fdars.mcp.server import fdars_auto_tune

    # depth — not tuneable
    with pytest.raises(ValueError, match="depth"):
        fdars_auto_tune(
            dataset_id=fpca_dataset_id,
            method="depth",
        )


# ---------------------------------------------------------------------------
# By-reference return — no arrays (TUNE-04, T-53C-04)
# ---------------------------------------------------------------------------


def test_returns_by_reference_no_arrays(fpca_dataset_id):
    """The returned dict values must be scalars/handles only (no list or ndarray).

    Arrays must stay in the registry under the trace_id handle.
    """
    from fdars.mcp.server import fdars_auto_tune

    result = fdars_auto_tune(
        dataset_id=fpca_dataset_id,
        method="fpca",
        max_steps=3,
    )

    assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    for key, val in result.items():
        assert not isinstance(val, (list, np.ndarray)), (
            f"fdars_auto_tune return contains array-like at key {key!r}: "
            f"type={type(val)}, value={val!r}"
        )
        assert isinstance(val, (str, int, float, bool, type(None))), (
            f"fdars_auto_tune return key {key!r} has unexpected type {type(val)}: "
            f"value={val!r}. Only str/int/float/bool/None allowed (by-reference invariant)."
        )

    # Must be JSON-serialisable (no NumPy scalars, no ndarrays)
    import json
    json.dumps(result)


# ---------------------------------------------------------------------------
# Guard-sync no-op (T-53C-03)
# ---------------------------------------------------------------------------


def test_guard_sync_still_no_op():
    """_RUNNABLE_METHODS and _DIAGNOSTICS_METHODS unchanged by adding fdars_auto_tune.

    Adding fdars_auto_tune must be a guard-sync no-op: the method-set sizes
    must stay at 6 and 16 respectively (T-53C-03).
    Count updated 14→16 in Phase 72 when fts+frechet were added to
    _DIAGNOSTICS_METHODS (ADV-01); fdars_auto_tune remains a no-op.
    """
    from fdars.mcp.server import _DIAGNOSTICS_METHODS, _RUNNABLE_METHODS

    assert len(_RUNNABLE_METHODS) == 6, (
        f"_RUNNABLE_METHODS has {len(_RUNNABLE_METHODS)} entries (expected 6): "
        f"{sorted(_RUNNABLE_METHODS)}"
    )
    assert len(_DIAGNOSTICS_METHODS) == 16, (
        f"_DIAGNOSTICS_METHODS has {len(_DIAGNOSTICS_METHODS)} entries (expected 16): "
        f"{sorted(_DIAGNOSTICS_METHODS)}"
    )


# ---------------------------------------------------------------------------
# Additional: heuristic step behaviour (int rounding, log-scale, direction, bisection)
# ---------------------------------------------------------------------------


def test_heuristic_step_int_rounding():
    """_make_heuristic_propose_fn must return an int for integer params (n_basis)."""
    from fdars.mcp._tuning import _make_heuristic_propose_fn

    spec = {
        "param": "n_basis",
        "param_type": int,
        "range": (4, 60),
        "log_scale": False,
        "default": 15,
    }
    propose_fn = _make_heuristic_propose_fn(spec)
    result = propose_fn({"n_basis": 15}, [])
    assert isinstance(result["n_basis"], int), (
        f"Expected int for n_basis, got {type(result['n_basis'])}: {result['n_basis']}"
    )


def test_heuristic_step_log_scale_multiplicative():
    """_make_heuristic_propose_fn for lambda_ must step multiplicatively (log-scale)."""
    from fdars.mcp._tuning import _make_heuristic_propose_fn

    spec = {
        "param": "lambda_",
        "param_type": float,
        "range": (1e-6, 1e4),
        "log_scale": True,
        "default": 1.0,
    }
    propose_fn = _make_heuristic_propose_fn(spec)
    # Empty history: initial step is *factor (10.0)
    result = propose_fn({"lambda_": 1.0}, [])
    assert result["lambda_"] > 1.0, "log-scale empty-history step should increase lambda_"
    # The result should be multiplicative — approximately 10x the initial value
    # (clamped to range)
    assert result["lambda_"] == pytest.approx(10.0, rel=1e-6), (
        f"Expected lambda_=10.0 (one decade), got {result['lambda_']}"
    )


def test_heuristic_steps_down_for_decreasing_target():
    """CR-01: on a target that improves in the DECREASING direction, the heuristic
    must eventually step in the negative direction (not just monotonically up).

    Scenario: lambda_ starts at 1.0; increasing to 10.0 yields no improvement
    (step rejected — not added to accepted_history).  On the second call the
    accepted_history length has NOT grown (still 0), so the heuristic detects
    rejection and must reverse direction, proposing a value below 1.0.
    """
    from fdars.mcp._tuning import _make_heuristic_propose_fn

    spec = {
        "param": "lambda_",
        "param_type": float,
        "range": (1e-6, 1e4),
        "log_scale": True,
        "default": 1.0,
    }
    propose_fn = _make_heuristic_propose_fn(spec)

    # Step 0: empty accepted_history → first call → initial positive step → 10.0
    p0 = propose_fn({"lambda_": 1.0}, [])
    assert p0["lambda_"] == pytest.approx(10.0), f"Expected 10.0, got {p0['lambda_']}"

    # Simulate: step was REJECTED (target did not improve) so the loop does NOT
    # append to accepted_history.  On the second call, accepted_history is still [].
    # The closure detects: len([]) == prev_accepted_len (0) → rejected → reverse.
    p1 = propose_fn({"lambda_": 1.0}, [])
    assert p1["lambda_"] < 1.0, (
        f"After a rejected step up (accepted_history empty again), "
        f"heuristic must step DOWN; got {p1['lambda_']}"
    )


def test_heuristic_bisection_halves_step():
    """CR-01: bisection must halve the step size after each direction reversal.

    Uses a linear param (n_basis) for easy arithmetic verification.
    The closure detects rejection when accepted_history does not grow.
    """
    from fdars.mcp._tuning import _make_heuristic_propose_fn

    spec = {
        "param": "n_basis",
        "param_type": int,
        "range": (4, 60),
        "log_scale": False,
        "default": 15,
    }
    propose_fn = _make_heuristic_propose_fn(spec)

    # Call 0: empty history → first call → initial positive step
    p0 = propose_fn({"n_basis": 15}, [])
    initial_step_int = p0["n_basis"] - 15
    assert initial_step_int > 0, "First step must be positive"

    # Simulate rejection: accepted_history remains empty (no improvement).
    # Call 1: history still [] → closure detects len([])==prev_accepted_len(0) → reversal
    p1 = propose_fn({"n_basis": 15}, [])
    # After reversal, direction is -1 and step is halved, so p1 < 15
    assert p1["n_basis"] < 15, (
        f"After direction reversal (rejected step detected), proposal must be below 15; got {p1['n_basis']}"
    )

    # Simulate acceptance: accepted_history grew by 1.
    # Call 2: history has 1 entry → no reversal, continue in direction -1 → p2 < p1
    accepted_entry = [{"step": 1, "param_value": p1["n_basis"], "target_value": 0.08, "accepted": True}]
    p2 = propose_fn({"n_basis": p1["n_basis"]}, accepted_entry)
    # Still going down (no reversal), so p2 < p1["n_basis"]
    assert p2["n_basis"] <= p1["n_basis"], (
        f"After acceptance, heuristic continues in same direction; "
        f"expected p2 <= {p1['n_basis']}, got {p2['n_basis']}"
    )


def test_heuristic_terminates_via_loop(fpca_dataset_id):
    """CR-01 (c): the heuristic propose_fn terminates the real loop within budget.

    Verifies that run_tuning_loop_mcp with the heuristic propose_fn stops
    before exhausting the budget when the oscillation-revisit or converged
    detector fires.
    """
    from fdars.mcp._tuning import run_tuning_loop_mcp

    result = run_tuning_loop_mcp(
        dataset_id=fpca_dataset_id,
        method="fpca",
        initial_params={"n_comp": 3},
        target_metric="cumulative_variance_explained",
        max_steps=15,
    )
    # Any valid stop_reason is acceptable — the key invariant is termination
    assert result["stop_reason"] in {
        "budget", "converged", "oscillation", "guard_stop", "parse_failure"
    }, f"Unexpected stop_reason: {result['stop_reason']!r}"
    assert result["n_steps"] <= 15, (
        f"n_steps {result['n_steps']} exceeded max_steps 15"
    )
