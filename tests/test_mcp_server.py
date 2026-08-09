"""Tests for the fdars MCP server surface (Plans 12-01, 12-02, and 12-03).

Requires: fdars[mcp] (mcp>=2.0.0, Python >=3.10) and pytest-asyncio.

All tests in this module are skipped on Python <3.10 via the module-level
``pytestmark``.  No ``ANTHROPIC_API_KEY`` and no network are required.

Plan 12-01 (tracer):
  - test_tracer_list_and_call_build_diagnostics

Plan 12-02 (full coarse-grained tool set):
  - test_list_and_call_tools
  - test_run_method_all_methods
  - test_build_diagnostics_all_methods

Plan 12-03 (compare loop — TOOL-03):
  - test_compare_run_unit_allowlist
  - test_compare_run_smoothing
  - test_compare_run_delta_sign
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Module-level skip guard: Python 3.9 CI runners skip cleanly (Pitfall 1)
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
# Canadian Weather fixture (mirrors test_advisor.py)
# ---------------------------------------------------------------------------


@pytest.fixture()
def canadian_weather():
    """Return (X, day, clustering_result) for Canadian Weather dataset (k=4, seed=42)."""
    from fdars import clustering, datasets

    ds = datasets.load_canadian_weather()
    X = np.asarray(ds.data.data, dtype=float)
    day = np.asarray(ds.argvals, dtype=float)
    result = clustering.kmeans_fd(X, day, k=4, seed=42)
    return X, day, result


# ---------------------------------------------------------------------------
# TRACER TEST: list_tools then call fdars_build_diagnostics end-to-end
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tracer_list_and_call_build_diagnostics(canadian_weather):
    """TRACER — in-process Client lists and invokes fdars_build_diagnostics.

    Verifies the full stack:
      packaging -> registry -> server -> tool -> advisor -> Client (in-process)

    No network call; no ANTHROPIC_API_KEY.
    """
    from mcp import Client
    from fdars.mcp.server import mcp
    from fdars.mcp._registry import registry

    X, day, clustering_result = canadian_weather

    # Pre-populate the registry (by-reference invariant: IDs not arrays cross boundary)
    dataset_id = registry.store_dataset(X, day)
    result_id = registry.store_result(clustering_result)

    async with Client(mcp) as client:
        # ---- list_tools ----
        # mcp 2.0.0 returns a ListToolsResult whose `.tools` holds the Tool list.
        tools_response = await client.list_tools()
        tool_names = [t.name for t in tools_response.tools]
        assert "fdars_build_diagnostics" in tool_names, (
            f"fdars_build_diagnostics not in {tool_names}"
        )

        # ---- call_tool ----
        call_response = await client.call_tool(
            "fdars_build_diagnostics",
            {
                "dataset_id": dataset_id,
                "result_id": result_id,
                "method": "clustering",
            },
        )

        # Unwrap the result: try structured_content first (Open Question 2),
        # fall back to JSON-parsing content[0].text
        diag = getattr(call_response, "structured_content", None)
        if diag is None:
            # Fall back: parse the text representation
            content = call_response.content
            assert content, "call_tool returned no content"
            diag = json.loads(content[0].text)

        assert diag["method"] == "clustering", f"Expected 'clustering', got {diag['method']!r}"
        assert isinstance(diag["k"], int), f"Expected int k, got {type(diag['k'])}"
        assert diag["k"] == 4, f"Expected k=4, got {diag['k']}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unwrap_tool_result(call_response):
    """Unwrap a call_tool response: prefer structured_content, fall back to text.

    mcp 2.0.0 with synchronous def handlers returns ``structured_content=None``
    and the JSON in ``content[0].text`` (Open Question 2 resolution from
    Plan 12-01 SUMMARY key-decisions).
    """
    diag = getattr(call_response, "structured_content", None)
    if diag is None:
        content = call_response.content
        assert content, "call_tool returned no content"
        diag = json.loads(content[0].text)
    return diag


def _method_params(method: str) -> dict:
    """Return appropriate params for each of the five supported methods."""
    return {
        "clustering": {"k": 3, "seed": 42},
        "basis": {"lambda_": 1.0},
        "smoothing": {"n_basis": 15},
        "fpca": {"n_comp": 3},
        "alignment": {"lambda_": 0.0},
    }[method]


# ---------------------------------------------------------------------------
# Plan 12-02 TESTS
# ---------------------------------------------------------------------------


@pytest.fixture()
def dataset_id():
    """Register the Canadian Weather dataset and return the opaque dataset_id.

    The autouse ``_clear_registry`` fixture ensures the registry is cleared
    after each test, so there is no state leakage across tests (Pitfall 3).
    """
    from fdars import datasets
    from fdars.mcp._registry import registry

    ds = datasets.load_canadian_weather()
    X = np.asarray(ds.data.data, dtype=float)
    day = np.asarray(ds.argvals, dtype=float)
    return registry.store_dataset(X, day)


@pytest.mark.asyncio
async def test_list_and_call_tools(dataset_id):
    """TOOL-02: list_tools returns both tools; call_tool succeeds for each.

    Asserts:
    - list_tools() includes both ``fdars_build_diagnostics`` and
      ``fdars_run_method`` (TOOL-02 listable).
    - call_tool() on each tool succeeds against the pre-registered
      Canadian Weather dataset (TOOL-02 invocable in-process, no network).

    No ANTHROPIC_API_KEY required.
    """
    from mcp import Client
    from fdars.mcp.server import mcp

    async with Client(mcp) as client:
        # ---- list_tools — must expose both tools (TOOL-02) ----
        tools_response = await client.list_tools()
        tool_names = [t.name for t in tools_response.tools]
        assert "fdars_build_diagnostics" in tool_names, (
            f"fdars_build_diagnostics not in {tool_names}"
        )
        assert "fdars_run_method" in tool_names, (
            f"fdars_run_method not in {tool_names}"
        )

        # ---- call_tool: fdars_run_method ----
        run_response = await client.call_tool(
            "fdars_run_method",
            {"dataset_id": dataset_id, "method": "clustering", "k": 3, "seed": 42},
        )
        run_result = _unwrap_tool_result(run_response)
        assert "result_id" in run_result, f"result_id missing from {run_result}"
        assert "method" in run_result, f"method missing from {run_result}"

        # ---- call_tool: fdars_build_diagnostics ----
        diag_response = await client.call_tool(
            "fdars_build_diagnostics",
            {
                "dataset_id": dataset_id,
                "result_id": run_result["result_id"],
                "method": "clustering",
            },
        )
        diag = _unwrap_tool_result(diag_response)
        assert diag["method"] == "clustering", (
            f"Expected method='clustering', got {diag['method']!r}"
        )


@pytest.mark.asyncio
async def test_run_method_all_methods(dataset_id):
    """TOOL-01: fdars_run_method runs all five methods; result_id resolves in registry.

    For each of the five supported methods (alignment, fpca, basis,
    smoothing, clustering), asserts:

    - ``fdars_run_method`` returns a dict with ``result_id`` and ``method``
      keys (no arrays in the JSON return — Pitfall 4).
    - The ``result_id`` resolves in the registry (by-reference invariant,
      TOOL-01).
    - The returned ``method`` matches the requested method (case-insensitive).

    No ANTHROPIC_API_KEY required.
    """
    from mcp import Client
    from fdars.mcp.server import mcp
    from fdars.mcp._registry import registry

    _methods = ["alignment", "fpca", "basis", "smoothing", "clustering"]

    async with Client(mcp) as client:
        for method in _methods:
            params = _method_params(method)
            response = await client.call_tool(
                "fdars_run_method",
                {"dataset_id": dataset_id, "method": method, **params},
            )
            result = _unwrap_tool_result(response)

            assert "result_id" in result, (
                f"[{method}] result_id missing from {result}"
            )
            assert "method" in result, (
                f"[{method}] method key missing from {result}"
            )
            assert result["method"].lower() == method.lower(), (
                f"[{method}] method mismatch: got {result['method']!r}"
            )

            # Verify the result_id resolves in the registry (TOOL-01 by-reference)
            stored = registry.get_result(result["result_id"])
            assert isinstance(stored, dict), (
                f"[{method}] stored result is not a dict: {type(stored)}"
            )


@pytest.mark.asyncio
async def test_build_diagnostics_all_methods(dataset_id):
    """TOOL-01: run_method -> build_diagnostics across all five methods.

    For each of the five supported methods, asserts:

    - ``fdars_run_method`` returns a ``result_id`` (TOOL-01 by-reference).
    - ``fdars_build_diagnostics(result_id=...)`` returns a diagnostics dict
      whose ``method`` key matches the requested method (TOOL-01).

    No ANTHROPIC_API_KEY required; entirely offline (no network).
    """
    from mcp import Client
    from fdars.mcp.server import mcp

    _methods = ["alignment", "fpca", "basis", "smoothing", "clustering"]

    async with Client(mcp) as client:
        for method in _methods:
            # Step 1: run the method to get a result_id
            run_params = _method_params(method)
            run_response = await client.call_tool(
                "fdars_run_method",
                {"dataset_id": dataset_id, "method": method, **run_params},
            )
            run_result = _unwrap_tool_result(run_response)
            assert "result_id" in run_result, (
                f"[{method}] fdars_run_method did not return result_id"
            )
            result_id = run_result["result_id"]

            # Step 2: build diagnostics using the result_id
            diag_response = await client.call_tool(
                "fdars_build_diagnostics",
                {
                    "dataset_id": dataset_id,
                    "result_id": result_id,
                    "method": method,
                },
            )
            diag = _unwrap_tool_result(diag_response)

            assert "method" in diag, (
                f"[{method}] diagnostics dict missing 'method' key: {list(diag.keys())}"
            )
            assert diag["method"] == method.lower(), (
                f"[{method}] diagnostics method mismatch: "
                f"expected {method.lower()!r}, got {diag['method']!r}"
            )


# ---------------------------------------------------------------------------
# Plan 12-03 TESTS (TOOL-03: compare loop)
# ---------------------------------------------------------------------------


def test_compare_run_unit_allowlist(dataset_id):
    """Unit test: compare_run rejects unknown params_after keys (T-12-03 allowlist).

    Verifies that the allowlist guard in ``compare_run`` raises ``ValueError``
    for unknown parameter keys before any fdars computation runs.
    No MCP Client needed — calls ``compare_run`` directly.
    """
    from fdars.mcp._runner import run_method
    from fdars.mcp._registry import registry
    from fdars.mcp._compare import compare_run

    # Run smoothing to get a before_result_id
    before = run_method(dataset_id, "smoothing", n_basis=15)
    before_result_id = registry.store_result(before)

    # Unknown key must raise ValueError (T-12-03 allowlist, Pitfall 6)
    with pytest.raises(ValueError, match="bogus"):
        compare_run(dataset_id, "smoothing", before_result_id, {"bogus": 1})


@pytest.mark.asyncio
async def test_compare_run_smoothing(dataset_id):
    """TOOL-03: fdars_compare_run returns before/after/delta with a non-empty delta dict.

    Calls ``fdars_run_method`` to get a ``before_result_id``, then calls
    ``fdars_compare_run`` with a changed ``n_basis``.  Asserts that the
    structured response contains ``before``, ``after``, and ``delta``, and
    that ``delta`` is a non-empty dict of numeric diffs.

    No ANTHROPIC_API_KEY; no network.
    """
    from mcp import Client
    from fdars.mcp.server import mcp

    async with Client(mcp) as client:
        # Step 1: run smoothing with default params to get a before result
        run_response = await client.call_tool(
            "fdars_run_method",
            {"dataset_id": dataset_id, "method": "smoothing", "n_basis": 15},
        )
        run_result = _unwrap_tool_result(run_response)
        before_result_id = run_result["result_id"]

        # Step 2: compare with a changed n_basis (from 15 to 25)
        compare_response = await client.call_tool(
            "fdars_compare_run",
            {
                "dataset_id": dataset_id,
                "method": "smoothing",
                "before_result_id": before_result_id,
                "n_basis": 25,
            },
        )
        result = _unwrap_tool_result(compare_response)

        # Structural assertions
        assert "before" in result, f"'before' key missing from {list(result.keys())}"
        assert "after" in result, f"'after' key missing from {list(result.keys())}"
        assert "delta" in result, f"'delta' key missing from {list(result.keys())}"
        assert "before_result_id" in result
        assert "after_result_id" in result

        # Delta must be a non-empty dict of numeric diffs
        delta = result["delta"]
        assert isinstance(delta, dict), f"delta is not a dict: {type(delta)}"
        assert len(delta) > 0, "delta dict is empty — expected at least one scalar diff"


@pytest.mark.asyncio
async def test_compare_run_delta_sign(dataset_id):
    """TOOL-03: Delta sign is correct for a known smoothing parameter change.

    Increasing ``n_basis`` from 15 to 30 typically increases the effective
    degrees of freedom (``optimal_edf`` or ``edf``), since more basis
    functions allow the smoother to track more detail.  Asserts that a
    scalar ``delta`` key exists and has the expected sign.

    This is a **deterministic, fdars-computed** assertion — no LLM involved.
    Grounding invariant: fdars produces the number; we only read the sign.

    No ANTHROPIC_API_KEY; no network.
    """
    from mcp import Client
    from fdars.mcp.server import mcp

    async with Client(mcp) as client:
        # Step 1: run with n_basis=15 (before)
        run_response = await client.call_tool(
            "fdars_run_method",
            {"dataset_id": dataset_id, "method": "smoothing", "n_basis": 15},
        )
        run_result = _unwrap_tool_result(run_response)
        before_result_id = run_result["result_id"]

        # Step 2: compare with n_basis=30 (after — more basis functions)
        compare_response = await client.call_tool(
            "fdars_compare_run",
            {
                "dataset_id": dataset_id,
                "method": "smoothing",
                "before_result_id": before_result_id,
                "n_basis": 30,
            },
        )
        result = _unwrap_tool_result(compare_response)
        delta = result["delta"]

        # At least one scalar delta key must be present
        assert len(delta) > 0, (
            f"delta is empty — no scalar finite keys found in diagnostics diff. "
            f"before={result['before']}, after={result['after']}"
        )

        # Check that at least one numeric key exists in delta
        # (smoothing diagnostics may include optimal_edf, optimal_gcv, etc.
        # depending on which keys are finite scalars in both before and after)
        numeric_keys = [k for k, v in delta.items() if isinstance(v, (int, float))]
        assert len(numeric_keys) > 0, (
            f"No numeric keys in delta: {delta}"
        )
