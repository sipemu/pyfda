"""Tests for the fdars MCP fdars_compare_methods tool (Plan 51-03).

Plan 51-03 tasks:
  - Task 1: MCP re-run helper (_compare_methods.compare_methods_mcp) delegating
    to the deterministic ranking core (compare_methods run_llm=False).
  - Task 2: fdars_compare_methods @mcp.tool wrapper + unsupported-method rejection.
  - Task 3: Prove the MCP tool stays LLM-free; guard-sync stays a no-op.

All tests are skipped on Python <3.10 via the module-level pytestmark.
No ANTHROPIC_API_KEY and no network are required.
"""

from __future__ import annotations

import json
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
# Dataset fixture: small synthetic clustering data (offline, no API key)
# ---------------------------------------------------------------------------


@pytest.fixture()
def dataset_id():
    """Register a small synthetic dataset and return its opaque dataset_id."""
    from fdars.mcp._registry import registry

    rng = np.random.default_rng(42)
    # Two well-separated clusters (10 obs each), 30 grid points
    X_cluster0 = rng.standard_normal((10, 30)) + 3.0
    X_cluster1 = rng.standard_normal((10, 30)) - 3.0
    X = np.vstack([X_cluster0, X_cluster1])
    argvals = np.linspace(0, 1, 30)
    return registry.store_dataset(X, argvals)


# ---------------------------------------------------------------------------
# Task 1 tests
# ---------------------------------------------------------------------------


def test_ranking_matches_offline_core(dataset_id):
    """Helper ranking must equal compare_methods(run_llm=False) on same diagnostics.

    Runs two clustering candidates (k=2, k=3) via compare_methods_mcp, then
    independently builds the same diagnostics via registry result_ids and calls
    the advisor core with run_llm=False using the same labels.  Asserts same
    winner and same label order.
    """
    from fdars.mcp._compare_methods import compare_methods_mcp
    from fdars.mcp._registry import registry
    from fdars.advisor import build_diagnostics
    from fdars.advisor._compare_methods import compare_methods as _core_compare

    # Run the helper for two clustering candidates
    candidate_params = [{"k": 2, "seed": 42}, {"k": 3, "seed": 42}]
    result = compare_methods_mcp(dataset_id, "clustering", candidate_params)

    # The full ranking (with diagnostics) is stored in the registry under ranking_id.
    full_ranking = registry.get_result(result["ranking_id"])

    # Build the labeled-diagnostics dict from the stored full ranking's diagnostics,
    # preserving the exact labels that compare_methods_mcp generated.
    labeled_diags = {
        entry["label"]: entry["diagnostics"]
        for entry in full_ranking["ranking"]
    }

    # Call the core independently with the same labels and diagnostics.
    core_result = _core_compare(
        labeled_diags,
        method="clustering",
        run_llm=False,
    )

    assert result["winner"] == core_result["winner"], (
        f"winner mismatch: helper={result['winner']!r}, core={core_result['winner']!r}"
    )
    helper_labels = [r["label"] for r in result["ranking"]]
    core_labels = [r["label"] for r in core_result["ranking"]]
    assert helper_labels == core_labels, (
        f"ranking order mismatch: helper={helper_labels!r}, core={core_labels!r}"
    )


def test_returns_by_reference_no_arrays(dataset_id):
    """Return dict must be JSON-serialisable and carry only handles + scalars.

    Calls compare_methods_mcp and asserts json.dumps succeeds (no NumPy
    arrays in the return) and that result_id handles appear in the ranking.
    """
    from fdars.mcp._compare_methods import compare_methods_mcp

    candidate_params = [{"k": 2, "seed": 42}, {"k": 3, "seed": 42}]
    result = compare_methods_mcp(dataset_id, "clustering", candidate_params)

    # Must be JSON-serialisable (no arrays)
    serialised = json.dumps(result)
    assert serialised, "json.dumps returned empty string"

    # ranking entries must carry result_id handles, not arrays
    assert "ranking" in result, f"'ranking' key missing from {list(result.keys())}"
    for entry in result["ranking"]:
        assert "result_id" in entry, (
            f"ranking entry missing result_id: {list(entry.keys())}"
        )
        assert isinstance(entry["result_id"], str), (
            f"result_id should be a str handle, got {type(entry['result_id'])}"
        )
        assert "metric_value" in entry, (
            f"ranking entry missing metric_value: {list(entry.keys())}"
        )
        # metric_value must be a plain scalar (float or None), not an array
        mv = entry["metric_value"]
        assert mv is None or isinstance(mv, (int, float)), (
            f"metric_value must be a scalar, got {type(mv)}: {mv!r}"
        )

    # Top-level fields present
    assert "ranking_id" in result, f"ranking_id missing from {list(result.keys())}"
    assert "winner" in result, f"winner missing from {list(result.keys())}"
    assert "method" in result, f"method missing from {list(result.keys())}"


def test_rejects_candidate_method_outside_runnable(dataset_id):
    """Helper must raise ValueError for unknown candidate_params keys.

    Passes a candidate_params entry with 'bogus_param' — a key outside the
    allowlist {'lambda_', 'n_basis', 'n_comp', 'k', 'seed'}.
    """
    from fdars.mcp._compare_methods import compare_methods_mcp

    bad_params = [{"k": 2, "seed": 42}, {"k": 3, "bogus_param": 99}]
    with pytest.raises(ValueError, match="bogus_param"):
        compare_methods_mcp(dataset_id, "clustering", bad_params)


# ---------------------------------------------------------------------------
# Task 2 tests
# ---------------------------------------------------------------------------


def test_rejects_method_not_in_runnable(dataset_id):
    """fdars_compare_methods must reject a method not in _RUNNABLE_METHODS.

    Calls the tool handler directly with method='regression' and asserts
    ValueError naming the supported set is raised.
    """
    from fdars.mcp.server import fdars_compare_methods

    with pytest.raises(ValueError, match="regression"):
        fdars_compare_methods(
            dataset_id=dataset_id,
            method="regression",
            candidate_params=[{"k": 2}, {"k": 3}],
        )


def test_tool_handler_returns_ranking(dataset_id):
    """Happy path: fdars_compare_methods returns a by-reference ranking dict.

    Calls the tool handler directly (no async MCP client needed for unit
    testing the synchronous handler).  Asserts the return shape and that
    winner is a string.
    """
    from fdars.mcp.server import fdars_compare_methods

    result = fdars_compare_methods(
        dataset_id=dataset_id,
        method="clustering",
        candidate_params=[{"k": 2, "seed": 42}, {"k": 3, "seed": 42}],
    )

    assert "winner" in result, f"'winner' missing from {list(result.keys())}"
    assert isinstance(result["winner"], str), (
        f"winner should be str, got {type(result['winner'])}"
    )
    assert "ranking" in result, f"'ranking' missing from {list(result.keys())}"
    assert len(result["ranking"]) == 2, (
        f"Expected 2 ranking entries, got {len(result['ranking'])}"
    )
    # Must be JSON-serialisable
    json.dumps(result)


# ---------------------------------------------------------------------------
# Task 3 tests: LLM-free invariant + guard-sync no-op
# ---------------------------------------------------------------------------


def test_tool_never_imports_advise():
    """_compare_methods.py must not reference the advise entrypoint.

    File-scan invariant (mirrors test_mcp_does_not_import_advise in
    test_mcp_server.py): the comparison MCP helper must stay LLM-free.
    Token constructed at runtime to avoid this test file self-flagging.
    """
    import pathlib

    # Build the search token at runtime to avoid this file self-flagging.
    _token = "adv" + "ise"

    target = (
        pathlib.Path(__file__).resolve().parents[1]
        / "python"
        / "fdars"
        / "mcp"
        / "_compare_methods.py"
    )
    assert target.exists(), f"_compare_methods.py not found at {target}"
    content = target.read_text()
    assert _token not in content, (
        f"_compare_methods.py references '{_token}' (LLM-free invariant "
        f"violation — COMPARE-04): file imports advise"
    )


def test_guard_sync_still_no_op():
    """_DIAGNOSTICS_METHODS (14) and _RUNNABLE_METHODS (6) unchanged by this phase.

    Asserts that adding fdars_compare_methods added no new entry to either set
    (guard-sync no-op — 51-CONTEXT hard constraint).
    """
    from fdars.mcp.server import _DIAGNOSTICS_METHODS, _RUNNABLE_METHODS

    assert len(_RUNNABLE_METHODS) == 6, (
        f"_RUNNABLE_METHODS has {len(_RUNNABLE_METHODS)} entries (expected 6): "
        f"{sorted(_RUNNABLE_METHODS)}"
    )
    assert len(_DIAGNOSTICS_METHODS) == 14, (
        f"_DIAGNOSTICS_METHODS has {len(_DIAGNOSTICS_METHODS)} entries (expected 14): "
        f"{sorted(_DIAGNOSTICS_METHODS)}"
    )
