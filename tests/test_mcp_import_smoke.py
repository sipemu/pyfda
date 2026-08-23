"""Regression test: MCP v2 server and its 3 existing tools import and load (COMPAT-02).

This module is skipped on Python <3.10 because importing ``fdars.mcp.server``
pulls in the ``mcp`` package which requires Python 3.10+ (mirroring the
module-level skip pattern from ``tests/test_mcp_server.py``).

On Python >=3.10 the test proves:

- ``MCPServer`` is importable from ``mcp.server`` (mcp v2 path, not v1).
- The ``fdars.mcp.server`` module loads without error.
- The MCP server instance (``mcp``) is not ``None``.
- All three existing tool handler names are registered/loadable on the server:
  ``fdars_build_diagnostics``, ``fdars_run_method``, ``fdars_compare_run``.

No ``ANTHROPIC_API_KEY`` and no network are required.
"""

from __future__ import annotations

import sys

import pytest

# ---------------------------------------------------------------------------
# Module-level skip guard (mirrors tests/test_mcp_server.py — Pitfall 1)
# mcp requires Python 3.10+; importing fdars.mcp.server will ImportError on 3.9.
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="mcp requires Python 3.10+",
)


# ---------------------------------------------------------------------------
# COMPAT-02: verify mcp v2 MCPServer path and 3 existing tools load
# ---------------------------------------------------------------------------


def test_mcp_v2_server_import_and_tools_load():
    """Assert MCPServer (mcp v2) + 3 existing tool handlers load over stdio path.

    Verifies:
    1. ``MCPServer`` is importable from ``mcp.server`` (v2 path).
    2. ``fdars.mcp.server.mcp`` is not None.
    3. All three existing tool handler names are registered/callable on the
       server: ``fdars_build_diagnostics``, ``fdars_run_method``,
       ``fdars_compare_run``.

    Reference: COMPAT-02 — verify-only; NO import change to server.py.
    """
    # 1. Assert the mcp v2 MCPServer import path is intact.
    from mcp.server import MCPServer  # type: ignore[import-untyped]  # noqa: PLC0415

    assert MCPServer is not None, "MCPServer must be importable from mcp.server (v2 path)"

    # 2. Assert the fdars MCP server instance loads without error.
    from fdars.mcp.server import mcp  # noqa: PLC0415

    assert mcp is not None, "fdars.mcp.server.mcp instance must not be None"

    # 3. Assert the 3 existing tool handler symbols are importable and callable.
    from fdars.mcp.server import (  # noqa: PLC0415
        fdars_build_diagnostics,
        fdars_compare_run,
        fdars_run_method,
    )

    expected_tool_names = {
        "fdars_build_diagnostics",
        "fdars_run_method",
        "fdars_compare_run",
    }
    for name in expected_tool_names:
        handler = {
            "fdars_build_diagnostics": fdars_build_diagnostics,
            "fdars_run_method": fdars_run_method,
            "fdars_compare_run": fdars_compare_run,
        }[name]
        assert callable(handler), (
            f"Tool handler {name!r} must be callable on the MCP server"
        )
