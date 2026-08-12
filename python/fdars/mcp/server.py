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

Tools exposed (Plans 12-01/02/03 + 22-01 + 22-02):

- ``fdars_build_diagnostics`` — deterministic offline diagnostics (TOOL-01/02)
- ``fdars_run_method`` — run any of six fdars methods; returns result handle (TOOL-01)
- ``fdars_compare_run`` — re-run with new params; return before/after delta (TOOL-03)
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
# Validated method sets
# ---------------------------------------------------------------------------

# Methods that run_method can dispatch (and fdars_compare_run can re-run).
# Must mirror _runner._RUNNABLE_METHODS (T-12-02).  Widened to 6 in Plan 22-01.
_RUNNABLE_METHODS = frozenset(
    {"alignment", "fpca", "basis", "smoothing", "clustering", "depth"}
)

# Backward-compat alias (used only in this file; external code should import
# _runner._RUNNABLE_METHODS directly).
_SUPPORTED_METHODS = _RUNNABLE_METHODS

# All methods that fdars_build_diagnostics can accept — mirrors
# advisor.build_diagnostics._supported (T-22-05 / T-22-07 drift lock).
# Superset of _RUNNABLE_METHODS: adds the six diagnostics-only aspects
# (outliers, classification, represent, regression, regression_cv, spm) whose
# fdars bindings need caller-supplied inputs (reference sample, labels, y,
# etc.) that the MCP dataset model cannot provide at run_method time.
_DIAGNOSTICS_METHODS = frozenset(
    {
        # Runnable aspects (also in _RUNNABLE_METHODS)
        "alignment",
        "fpca",
        "basis",
        "smoothing",
        "clustering",
        "depth",
        # Diagnostics-only aspects — reachable via fdars_build_diagnostics
        # over a caller-supplied result dict; NOT dispatchable by run_method.
        "outliers",
        "classification",
        "represent",
        "regression",
        "regression_cv",
        "spm",
    }
)

# ---------------------------------------------------------------------------
# Tool: fdars_build_diagnostics
# ---------------------------------------------------------------------------


@mcp.tool()
def fdars_build_diagnostics(
    dataset_id: str,
    method: str,
    result_id: str | None = None,
    with_argvals: bool = True,
    n_classes: int | None = None,
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
        One of the twelve supported aspects (``_DIAGNOSTICS_METHODS``):
        ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``, ``'depth'``, ``'outliers'``, ``'classification'``,
        ``'represent'``, ``'regression'``, ``'regression_cv'``, ``'spm'``.
        Passed directly to ``build_diagnostics``.
    result_id : str, optional
        Handle to a stored result dict (e.g. from a prior ``fdars_run_method``
        call).  If ``None``, ``build_diagnostics`` is called with a fallback
        result assembled from the dataset.
    with_argvals : bool, optional
        When ``True`` (default), pass the dataset's ``argvals`` array to
        ``build_diagnostics`` for distance metrics.
    n_classes : int, optional
        Ground-truth class count.  **Required for** ``method="classification"``
        (cannot be inferred from the result dict).  Ignored by all other
        methods.  Passed directly to ``build_diagnostics(..., n_classes=K)``.

    Returns
    -------
    dict
        JSON-serialisable diagnostics dict (see ``advisor.build_diagnostics``
        for per-method key descriptions).  Also stored in the registry as a
        new result handle (not returned, but available via the registry).

    Raises
    ------
    ValueError
        If ``method`` is not in the supported set (``_DIAGNOSTICS_METHODS``).
    KeyError
        If ``dataset_id`` or ``result_id`` is not found in the registry.
    """
    # V5 input validation — validate method before any fdars call (T-22-05)
    # Uses _DIAGNOSTICS_METHODS (12), NOT _RUNNABLE_METHODS (6).
    method_lc = method.lower()
    if method_lc not in _DIAGNOSTICS_METHODS:
        raise ValueError(
            f"fdars_build_diagnostics: unsupported method {method!r}. "
            f"Supported: {sorted(_DIAGNOSTICS_METHODS)!r}."
        )

    from fdars.mcp._registry import registry
    from fdars.advisor import build_diagnostics

    # Resolve dataset handle (T-12-01: unknown id raises KeyError, fail closed)
    data, argvals = registry.get_dataset(dataset_id)

    # Resolve result handle (or build a fallback from dataset arrays).
    if result_id is not None:
        result = registry.get_result(result_id)
    elif method_lc == "represent":
        # Represent builder reads raw.get("argvals") to compute grid statistics
        # (Pitfall 4 / argvals-injection fix).  Inject argvals into the fallback
        # dict so _build_represent_diagnostics finds the evaluation grid.
        result = {"data": data, "argvals": argvals}
    else:
        # For all other methods, the raw data matrix is sufficient.
        result = {"data": data}

    # Depth unwrap (Pitfall 2 / T-22-04): the depth runner returns a dict
    # {"scores": ndarray, "method_name": str}; _build_depth_diagnostics
    # expects the raw ndarray (np.asarray(raw)).  Unwrap before delegating.
    depth_kwargs: dict = {}
    if method_lc == "depth" and isinstance(result, dict) and "scores" in result:
        depth_kwargs["method_name"] = result.get("method_name", "unknown")
        result = result["scores"]

    # Delegate to advisor — do NOT reimplement diagnostics here (Anti-Pattern)
    kwargs: dict = {}
    if with_argvals:
        kwargs["argvals"] = argvals
    kwargs.update(depth_kwargs)

    # Forward n_classes for the classification aspect (cannot be inferred from
    # the result dict; forwarded as a scalar int — no array-injection risk T-22-06).
    if n_classes is not None:
        kwargs["n_classes"] = n_classes

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
        ``'clustering'``, ``'depth'``.  Case-insensitive.  Raises
        :exc:`ValueError` on unknown method (T-12-02).
    lambda_ : float, optional
        Warp penalty for ``alignment`` (default ``0.0``) or regularisation
        strength for ``smoothing`` (passed to ``pspline_fit_gcv``).
        Ignored for ``fpca``, ``basis``, ``clustering``, and ``depth``.
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
    - ``depth``:      no scalar params (always ``fraiman_muniz_1d``)

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
# Tool: fdars_compare_run (TOOL-03)
# ---------------------------------------------------------------------------


@mcp.tool()
def fdars_compare_run(
    dataset_id: str,
    method: str,
    before_result_id: str,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict:
    """Re-run an fdars method with new parameters and return an observable before/after delta.

    This is the TOOL-03 agentic re-run/compare tool.  It fetches the before
    result from the handle registry, re-runs the fdars method with the
    specified after-parameters, builds diagnostics for both runs, and returns
    a dict containing the full diagnostics and a scalar numeric delta.

    The compute path is **fully deterministic** — fdars computes every number;
    the model only orchestrates.  No ``ANTHROPIC_API_KEY`` is required; no
    network connection is made.

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID for the dataset (data + argvals) stored in the
        handle registry.  Pre-populate via ``registry.store_dataset``.
    method : str
        One of ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``.  Raises :exc:`ValueError` on unknown method
        (T-12-02 — validated at the tool boundary and again in the runner).
    before_result_id : str
        Handle ID for the prior run result (from ``fdars_run_method`` or
        ``fdars_build_diagnostics``).  Raises :exc:`KeyError` if not found
        in the registry (T-12-01: fail closed).
    lambda_ : float, optional
        After-run warp penalty for ``alignment`` or smoothing regularisation
        for ``smoothing``.  Ignored for ``fpca``, ``basis``, ``clustering``.
    n_basis : int, optional
        After-run number of B-spline basis functions for ``smoothing``.
        Default ``15``.  Ignored for other methods.
    n_comp : int, optional
        After-run number of FPCA components for ``fpca``.  Default ``3``.
        Ignored for other methods.
    k : int, optional
        After-run number of clusters for ``clustering``.  Default ``3``.
        Ignored for other methods.
    seed : int, optional
        After-run RNG seed for ``clustering``.  Default ``42``.
        Ignored for other methods.

    Returns
    -------
    dict
        Plain-Python, JSON-serialisable dict with keys:

        ``before_result_id`` : str
            The handle ID of the before result (same as input).
        ``after_result_id`` : str
            The handle ID of the newly stored after result.
        ``before`` : dict
            Full diagnostics dict (``advisor.build_diagnostics``) for the
            before run.
        ``after`` : dict
            Full diagnostics dict for the after run.
        ``delta`` : dict
            Scalar numeric difference per key: ``after[key] - before[key]``.
            Only keys where both values are finite ``float`` or ``int``
            (not bool) are included (TOOL-03 observable delta).

    Raises
    ------
    ValueError
        If ``method`` is not in the supported set (T-12-02).
    KeyError
        If ``dataset_id`` or ``before_result_id`` is unknown in the registry
        (T-12-01).

    Notes
    -----
    After-params are **flattened** as top-level typed arguments (NOT a nested
    ``params_after: dict``) so the MCP schema is fully specified from type
    hints (Pitfall 6).  Non-``None`` args are assembled into ``params_after``
    inside the handler before delegating to ``_compare.compare_run``.

    Tool handlers are **synchronous** (``def``, not ``async def``) because
    fdars methods are synchronous Rust calls (Pitfall 2).
    """
    # V5: validate method at tool boundary before delegating (T-12-02; fail fast)
    # compare_run is restricted to _RUNNABLE_METHODS only (Pitfall 3: you can
    # only compare before/after on re-runnable methods, not diagnostics-only ones).
    method_lc = method.lower()
    if method_lc not in _RUNNABLE_METHODS:
        raise ValueError(
            f"fdars_compare_run: unsupported method {method!r}. "
            f"Supported: {sorted(_RUNNABLE_METHODS)!r}."
        )

    # Assemble params_after from non-None typed args (Pitfall 6: flat schema)
    params_after: dict = {}
    if lambda_ is not None:
        params_after["lambda_"] = lambda_
    if n_basis is not None:
        params_after["n_basis"] = n_basis
    if n_comp is not None:
        params_after["n_comp"] = n_comp
    if k is not None:
        params_after["k"] = k
    if seed is not None:
        params_after["seed"] = seed

    from fdars.mcp._compare import compare_run

    # Delegate to _compare — no inline delta logic here (Single Responsibility)
    return compare_run(dataset_id, method_lc, before_result_id, params_after)


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
