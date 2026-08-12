"""fdars MCP method runner — dispatches the six supported fdars methods.

This module exposes ``run_method``, which retrieves a dataset from the
handle registry by its opaque ID, calls the appropriate real fdars function,
and returns the raw result dict.  The returned dict is **not** converted to
plain-Python types here — that conversion happens downstream in
``advisor.build_diagnostics`` (Pitfall 4: avoid double-conversion overhead
and keep the runner's responsibility narrow).

Supported methods (``_RUNNABLE_METHODS``):

- ``alignment``  → :func:`fdars.alignment.karcher_mean`
- ``fpca``       → :func:`fdars.regression.fpca`
- ``basis``      → :func:`fdars.basis.basis_nbasis_cv`
- ``smoothing``  → :func:`fdars.basis.pspline_fit_gcv`
  (note: ``pspline_fit_gcv`` is the smoothing runner here; the
  ``smoothing`` branch of ``build_diagnostics`` consumes GCV-curve keys
  such as ``lambda_values`` and ``gcv`` via its Branch B path, which
  re-calls ``pspline_fit_gcv`` internally when only argvals is present —
  this mapping decision keeps the tool boundary handle-only)
- ``clustering`` → :func:`fdars.clustering.kmeans_fd`
- ``depth``      → :func:`fdars.depth.fraiman_muniz_1d` (self-depth:
  ``fraiman_muniz_1d(data, data)``; MCP entry point is hard-coded to
  ``fraiman_muniz`` to avoid string-injection risk; callers needing
  ``modal_1d`` or ``random_projection_1d`` should run those manually and
  pass their result to ``fdars_build_diagnostics``).
  Returns ``{"scores": ndarray(n,), "method_name": "fraiman_muniz"}``.

Only scalar parameters (``float``/``int``/``None``) are accepted as
``run_method`` arguments; no arrays are accepted (threat T-12-03).

Requires the ``fdars[mcp]`` optional extra (Python >=3.10).

Usage::

    from fdars.mcp._runner import run_method
    from fdars.mcp._registry import registry

    ds_id = registry.store_dataset(X, day)
    result = run_method(ds_id, "clustering", k=4, seed=42)
    r_id = registry.store_result(result)
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

__all__ = ["run_method"]

# Closed set of runnable method names — these are the methods that
# run_method can dispatch to fdars.  Widened from 5 to 6 in Plan 22-01
# to include "depth" (SURF-01).  Mirrors server._RUNNABLE_METHODS (T-12-02).
_RUNNABLE_METHODS = frozenset(
    {"alignment", "fpca", "basis", "smoothing", "clustering", "depth"}
)

# Backward-compat alias for any external code that imported _SUPPORTED_METHODS
_SUPPORTED_METHODS = _RUNNABLE_METHODS


def run_method(
    dataset_id: str,
    method: str,
    *,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict:
    """Run an fdars method on a registered dataset and return the raw result dict.

    Retrieves the dataset (data matrix and evaluation grid) from the handle
    registry using ``dataset_id``, then dispatches to the appropriate real
    fdars function.  The returned dict is the unmodified fdars result — it
    contains NumPy arrays that **must** remain in the registry and must not
    be serialised directly to JSON (Pitfall 4).

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID returned by :meth:`HandleRegistry.store_dataset`.
    method : str
        One of ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``, ``'depth'``.  Case-insensitive.  Raises
        :exc:`ValueError` on unknown method (T-12-02).
    lambda_ : float, optional
        Warp penalty for ``alignment`` (``karcher_mean``) or smoothing
        regularisation for ``smoothing`` (``pspline_fit_gcv``).
        Defaults to ``0.0`` for alignment.
    n_basis : int, optional
        Number of B-spline basis functions for the ``smoothing`` method
        (``pspline_fit_gcv``).  Defaults to ``15``.
    n_comp : int, optional
        Number of FPCA components for the ``fpca`` method.  Defaults to ``3``.
    k : int, optional
        Number of clusters for the ``clustering`` method.  Defaults to ``3``.
    seed : int, optional
        RNG seed for ``clustering`` (``kmeans_fd``).  Defaults to ``42``.

    Returns
    -------
    dict
        Raw fdars result dict (method-dependent keys).  Arrays in the dict
        are NumPy ndarrays; they must be stored via
        :meth:`HandleRegistry.store_result` before crossing any
        serialisation boundary.

    Raises
    ------
    ValueError
        If ``method`` is not in the supported set
        ``{'alignment','fpca','basis','smoothing','clustering','depth'}``.
    KeyError
        If ``dataset_id`` is not found in the registry.

    Notes
    -----
    Only scalar parameters (``float | None``, ``int | None``) are accepted.
    Passing arrays via ``lambda_``, ``n_basis``, ``n_comp``, ``k``, or
    ``seed`` is not supported and will raise a :exc:`TypeError` inside the
    fdars call (threat T-12-03 — large-array injection prevention).

    The ``smoothing`` method maps to :func:`fdars.basis.pspline_fit_gcv`.
    This means a stored smoothing result (keys: ``fitted``, ``coefficients``,
    ``edf``, ``rss``, ``gcv``, ``aic``, ``bic``) does not carry
    ``lambda_values`` or ``gcv`` curve keys, so
    ``advisor.build_diagnostics(result, 'smoothing')`` falls through to its
    Branch B path (re-runs ``pspline_fit_gcv`` with data+argvals internally)
    when called from ``fdars_build_diagnostics`` with ``with_argvals=True``.
    This is intentional — the tool boundary carries only handles and scalar
    params, never multi-lambda sweep arrays.

    Examples
    --------
    >>> import numpy as np
    >>> from fdars.mcp._registry import registry
    >>> from fdars.mcp._runner import run_method
    >>> X = np.random.default_rng(0).standard_normal((10, 50))
    >>> day = np.linspace(0, 1, 50)
    >>> ds_id = registry.store_dataset(X, day)
    >>> result = run_method(ds_id, "clustering", k=2, seed=42)
    >>> "cluster" in result
    True
    """
    # V5 input validation — validate method before any fdars call (T-12-02)
    method_lc = method.lower()
    if method_lc not in _RUNNABLE_METHODS:
        raise ValueError(
            f"run_method: unsupported method {method!r}. "
            f"Supported: {sorted(_RUNNABLE_METHODS)!r}."
        )

    from fdars.mcp._registry import registry

    # Resolve dataset handle (T-12-01: unknown id raises KeyError, fail closed)
    data, argvals = registry.get_dataset(dataset_id)

    if method_lc == "clustering":
        from fdars import clustering as _clustering

        return _clustering.kmeans_fd(
            data,
            argvals,
            k=k if k is not None else 3,
            seed=seed if seed is not None else 42,
        )

    if method_lc == "basis":
        from fdars import basis as _basis

        return _basis.basis_nbasis_cv(
            data,
            argvals,
            lambda_=lambda_ if lambda_ is not None else 1.0,
        )

    if method_lc == "smoothing":
        from fdars import basis as _basis

        # pspline_fit_gcv is the smoothing runner here.
        # See module docstring for the mapping rationale (build_diagnostics
        # Branch B path handles the GCV-curve diagnostics).
        return _basis.pspline_fit_gcv(
            data,
            argvals,
            n_basis=n_basis if n_basis is not None else 15,
        )

    if method_lc == "fpca":
        from fdars import regression as _regression

        return _regression.fpca(
            data,
            argvals,
            n_comp=n_comp if n_comp is not None else 3,
        )

    if method_lc == "alignment":
        from fdars import alignment as _alignment

        return _alignment.karcher_mean(
            data,
            argvals,
            lambda_=lambda_ if lambda_ is not None else 0.0,
        )

    if method_lc == "depth":
        from fdars import depth as _depth

        # MCP entry point: fraiman_muniz_1d with self-depth (data as its own
        # reference sample).  String method_name param deliberately omitted
        # to avoid injection risk (T-12-03); hard-coded to fraiman_muniz.
        # For modal_1d or random_projection_1d, callers should run those
        # functions manually and pass the result to fdars_build_diagnostics
        # via result_id.  Note: fraiman_muniz_1d(data, ref_data) — ref_data
        # is the reference sample, NOT argvals; argvals is the evaluation grid.
        scores = _depth.fraiman_muniz_1d(data, data)
        return {"scores": scores, "method_name": "fraiman_muniz"}

    # Unreachable given the check above, but kept for safety.
    raise ValueError(f"Unhandled method: {method!r}")  # pragma: no cover
