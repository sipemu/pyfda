"""Tests for the fdars MCP server surface (Plan 12-01 tracer).

Requires: fdars[mcp] (mcp>=2.0.0, Python >=3.10) and pytest-asyncio.

All tests in this module are skipped on Python <3.10 via the module-level
``pytestmark``.  No ``ANTHROPIC_API_KEY`` and no network are required.
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
        tools_response = await client.list_tools()
        tool_names = [t.name for t in tools_response]
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
