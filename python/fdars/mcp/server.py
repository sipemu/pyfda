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


# ---------------------------------------------------------------------------
# Tool: fdars_run_method
# ---------------------------------------------------------------------------


@mcp.tool()
def fdars_run_method(
    dataset_id: str,
    method: str,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict:
    """Run an fdars method on a registered dataset and return a result handle.

    Dispatches to the appropriate fdars function, stores the raw result in the
    handle registry, and returns **only** the opaque ``result_id`` and
    ``method`` name.  Arrays never leave the tool boundary — they remain in
    the registry until retrieved by :func:`fdars_build_diagnostics` or
    another tool (Pitfall 4, by-reference invariant).

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID returned by ``registry.store_dataset(data, argvals)``.
        The dataset must be pre-registered before calling this tool.
    method : str
        One of ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``.  Case-insensitive.  Raises :exc:`ValueError` on
        unknown method (T-12-02).
    lambda_ : float, optional
        Warp penalty for ``alignment`` (default ``0.0``) or regularisation
        strength for ``smoothing`` (passed to ``pspline_fit_gcv``).
        Ignored for ``fpca``, ``basis``, and ``clustering``.
    n_basis : int, optional
        Number of B-spline basis functions for the ``smoothing`` method
        (``pspline_fit_gcv``).  Default ``15``.  Ignored for other methods.
    n_comp : int, optional
        Number of FPCA components for the ``fpca`` method.  Default ``3``.
        Ignored for other methods.
    k : int, optional
        Number of clusters for the ``clustering`` method (``kmeans_fd``).
        Default ``3``.  Ignored for other methods.
    seed : int, optional
        RNG seed for ``clustering`` (``kmeans_fd``).  Default ``42``.
        Ignored for other methods.

    Returns
    -------
    dict
        ``{"result_id": str, "method": str}`` — the raw fdars result is
        stored in the registry under ``result_id``; only the handle and
        method name are returned so that arrays never appear in JSON output.

    Raises
    ------
    ValueError
        If ``method`` is not in the supported set.
    KeyError
        If ``dataset_id`` is not in the registry.

    Notes
    -----
    **Parameter → method mapping** (only the listed param is used per method;
    others are silently ignored to keep the MCP schema flat):

    - ``alignment``:  ``lambda_`` (default ``0.0``)
    - ``fpca``:       ``n_comp`` (default ``3``)
    - ``basis``:      ``lambda_`` (default ``1.0``)
    - ``smoothing``:  ``n_basis`` (default ``15``)
    - ``clustering``: ``k`` (default ``3``), ``seed`` (default ``42``)

    The tool handlers are **synchronous** (``def``, not ``async def``) because
    fdars methods are synchronous Rust calls that release the GIL via PyO3
    PyReadonly wrappers; wrapping in ``asyncio.run_in_executor`` is
    unnecessary for this scope (Pitfall 2).
    """
    from fdars.mcp._runner import run_method
    from fdars.mcp._registry import registry

    # Delegate dispatch + validation to the runner (T-12-02 validated there)
    result = run_method(
        dataset_id,
        method,
        lambda_=lambda_,
        n_basis=n_basis,
        n_comp=n_comp,
        k=k,
        seed=seed,
    )

    # Store raw result (arrays remain in-process; Pitfall 4)
    result_id = registry.store_result(result)

    # Return only the handle + method — never arrays (by-reference invariant)
    return {"result_id": result_id, "method": method.lower()}


# ---------------------------------------------------------------------------
# stdio entry point — transport-agnostic (tool handlers are NOT coupled here)
# ---------------------------------------------------------------------------


def run_stdio() -> None:
    """Start the fdars MCP server in stdio mode (blocks until EOF).

    This is the console-script entry point for the ``fdars-mcp-server``
    command.  The function calls :meth:`MCPServer.run` with
    ``transport="stdio"``, which handles all JSON-RPC framing and message
    dispatch until stdin is closed.

    The tool handlers (``fdars_build_diagnostics``, ``fdars_run_method``) are
    **transport-agnostic** — they do not reference stdio in any way.  A
    future HTTP/SSE transport would only require changing the transport arg
    here, not in the tool code (CONTEXT locked decision).

    Notes
    -----
    This function blocks the calling thread.  Call it from a console-script
    entrypoint or ``if __name__ == "__main__"`` guard, never from inside a
    tool handler.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
