"""fdars MCP server — exposes fdars advisor tools via the Model Context Protocol.

This module defines the ``MCPServer`` instance (``mcp``) and all ``@mcp.tool()``
decorated handlers.  The tool layer is **transport-agnostic**: it does not wire
stdio here — see ``run_stdio()`` (added in Plan 02) for the entry point.

Requires the ``fdars[mcp]`` optional extra (Python >=3.10, ``mcp>=2.0.0``).

Usage (in-process test)::

    from fdars.mcp.server import mcp
    from mcp import Client

    async with Client(mcp) as client:
        tools = await client.list_tools()
        result = await client.call_tool("fdars_build_diagnostics", {...})
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

from mcp.server import MCPServer  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = MCPServer("fdars-advisor")

# ---------------------------------------------------------------------------
# Validated method set (mirrors advisor.build_diagnostics _supported)
# ---------------------------------------------------------------------------

_SUPPORTED_METHODS = frozenset({"alignment", "fpca", "basis", "smoothing", "clustering"})

# ---------------------------------------------------------------------------
# Tool: fdars_build_diagnostics
# ---------------------------------------------------------------------------


@mcp.tool()
def fdars_build_diagnostics(
    dataset_id: str,
    method: str,
    result_id: str | None = None,
    with_argvals: bool = True,
) -> dict:
    """Build offline diagnostics for an fdars result.

    Retrieves the dataset (and optionally a prior result) from the handle
    registry by their opaque IDs, then delegates to
    ``advisor.build_diagnostics`` to produce a deterministic,
    JSON-serialisable diagnostics dict.  **No network call; no
    ``ANTHROPIC_API_KEY`` required.**

    Parameters
    ----------
    dataset_id : str
        Handle to the dataset stored in the registry (data + argvals arrays).
        Obtain via ``registry.store_dataset(data, argvals)``.
    method : str
        One of ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``.  Passed directly to ``build_diagnostics``.
    result_id : str, optional
        Handle to a stored result dict (e.g. from a prior ``fdars_run_method``
        call).  If ``None``, ``build_diagnostics`` is called with the raw
        dataset data matrix as ``result``.
    with_argvals : bool, optional
        When ``True`` (default), pass the dataset's ``argvals`` array to
        ``build_diagnostics`` for distance metrics.

    Returns
    -------
    dict
        JSON-serialisable diagnostics dict (see ``advisor.build_diagnostics``
        for per-method key descriptions).  Also stored in the registry as a
        new result handle (not returned, but available via the registry).

    Raises
    ------
    ValueError
        If ``method`` is not in the supported set.
    KeyError
        If ``dataset_id`` or ``result_id`` is not found in the registry.
    """
    # V5 input validation — validate method before any fdars call (T-12-02)
    method_lc = method.lower()
    if method_lc not in _SUPPORTED_METHODS:
        raise ValueError(
            f"fdars_build_diagnostics: unsupported method {method!r}. "
            f"Supported: {sorted(_SUPPORTED_METHODS)!r}."
        )

    from fdars.mcp._registry import registry
    from fdars.advisor import build_diagnostics

    # Resolve dataset handle (T-12-01: unknown id raises KeyError, fail closed)
    data, argvals = registry.get_dataset(dataset_id)

    # Resolve result handle (or use data matrix directly)
    if result_id is not None:
        result = registry.get_result(result_id)
    else:
        # When no result_id is given, use the raw data matrix as the result
        # so build_diagnostics can extract what it needs (e.g. for smoothing).
        result = {"data": data}

    # Delegate to advisor — do NOT reimplement diagnostics here (Anti-Pattern)
    kwargs: dict = {}
    if with_argvals:
        kwargs["argvals"] = argvals

    diagnostics = build_diagnostics(result, method_lc, **kwargs)

    # Store diagnostics for potential chaining (does not affect the return value)
    registry.store_result(diagnostics)

    return diagnostics
