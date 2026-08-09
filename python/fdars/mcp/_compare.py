"""fdars MCP compare helper — before/after diagnostics delta builder.

This module exposes ``compare_run``, the core logic for the TOOL-03 agentic
re-run/compare loop.  Given a prior ``before_result_id``, a method name, and
a set of ``params_after``, it:

1. Fetches the before result from the handle registry.
2. Re-runs the fdars method with the new parameters (via ``run_method``).
3. Stores the after result in the registry and obtains its handle.
4. Builds diagnostics for both before and after via ``advisor.build_diagnostics``.
5. Computes a ``delta`` dict: scalar finite numeric diffs (after - before).

The compute path is **fully deterministic** — fdars produces every number, the
model only orchestrates.  No LLM, no network, no RNG beyond any method's own
seeded path.  ``ANTHROPIC_API_KEY`` is never required here.

Requires the ``fdars[mcp]`` optional extra (Python >=3.10).

Usage::

    from fdars.mcp._registry import registry
    from fdars.mcp._compare import compare_run

    ds_id = registry.store_dataset(X, day)
    before = run_method(ds_id, "smoothing", n_basis=15)
    before_id = registry.store_result(before)

    result = compare_run(ds_id, "smoothing", before_id, {"n_basis": 25})
    print(result["delta"])  # e.g. {"optimal_edf": 2.3, ...}
"""

from __future__ import annotations

import math
import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

__all__ = ["compare_run"]

# Allowlist of valid after-param keys (mirrors fdars_run_method signature — T-12-03)
_ALLOWED_PARAMS = frozenset({"lambda_", "n_basis", "n_comp", "k", "seed"})


def compare_run(
    dataset_id: str,
    method: str,
    before_result_id: str,
    params_after: dict,
) -> dict:
    """Re-run an fdars method with new parameters and return a before/after delta.

    Fetches the before result from the handle registry by ``before_result_id``,
    re-runs the method with ``params_after``, builds diagnostics for both before
    and after, and returns a dict containing the full diagnostics and a scalar
    numeric delta (after − before).

    The ``delta`` dict includes only keys where **both** before and after
    diagnostics values are a finite scalar ``float`` or ``int`` (booleans are
    excluded; non-scalar, non-finite, or absent keys are excluded).

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID for the dataset (data + argvals) stored in the registry.
        Obtain via ``registry.store_dataset(data, argvals)``.
    method : str
        One of ``'alignment'``, ``'fpca'``, ``'basis'``, ``'smoothing'``,
        ``'clustering'``.  Case-insensitive.  Raises :exc:`ValueError` on
        unknown method (T-12-02).
    before_result_id : str
        Opaque handle ID for the prior run result stored in the registry.
        Raises :exc:`KeyError` if the ID is unknown (T-12-01: fail closed).
    params_after : dict
        Mapping of parameter overrides for the after run.  Keys must be a
        subset of ``{'lambda_', 'n_basis', 'n_comp', 'k', 'seed'}``.
        Raises :exc:`ValueError` for any unknown key (T-12-03 allowlist).

    Returns
    -------
    dict
        Plain-Python, JSON-serialisable dict with keys:

        ``before_result_id`` : str
            The handle ID of the before result (same as the input arg).
        ``after_result_id`` : str
            The handle ID of the newly stored after result.
        ``before`` : dict
            Full diagnostics dict from ``advisor.build_diagnostics`` for the
            before run.
        ``after`` : dict
            Full diagnostics dict from ``advisor.build_diagnostics`` for the
            after run.
        ``delta`` : dict
            Scalar numeric difference per key: ``after[key] - before[key]``.
            Only keys where both values are a finite ``float`` or ``int``
            (not bool) are included.

    Raises
    ------
    ValueError
        If ``method`` is not in the supported set, or if ``params_after``
        contains an unknown key (T-12-02, T-12-03).
    KeyError
        If ``dataset_id`` or ``before_result_id`` is not in the registry
        (T-12-01: fail closed).

    Notes
    -----
    The ``smoothing`` method maps to ``pspline_fit_gcv`` in ``_runner``.
    The stored before result may lack ``lambda_values`` (a GCV sweep), so
    ``build_diagnostics`` falls through to its Branch B path (re-runs with
    data + argvals internally) when ``with_argvals=True`` is the default.
    This ensures diagnostics are always complete for the compare loop.

    Examples
    --------
    >>> import numpy as np
    >>> from fdars.mcp._registry import registry
    >>> from fdars.mcp._runner import run_method
    >>> from fdars.mcp._compare import compare_run
    >>> X = np.random.default_rng(0).standard_normal((10, 50))
    >>> day = np.linspace(0, 1, 50)
    >>> ds_id = registry.store_dataset(X, day)
    >>> before = run_method(ds_id, "smoothing", n_basis=15)
    >>> before_id = registry.store_result(before)
    >>> result = compare_run(ds_id, "smoothing", before_id, {"n_basis": 25})
    >>> isinstance(result["delta"], dict)
    True
    """
    # T-12-03: allowlist-validate params_after keys before any computation
    unknown_keys = set(params_after) - _ALLOWED_PARAMS
    if unknown_keys:
        raise ValueError(
            f"compare_run: unknown params_after key(s) {sorted(unknown_keys)!r}. "
            f"Allowed keys: {sorted(_ALLOWED_PARAMS)!r}."
        )

    from fdars.mcp._registry import registry
    from fdars.mcp._runner import run_method
    from fdars.advisor import build_diagnostics

    # T-12-01: resolve before result — KeyError if unknown (fail closed)
    before_result = registry.get_result(before_result_id)

    # Resolve dataset (needed for build_diagnostics argvals and for the after run)
    data, argvals = registry.get_dataset(dataset_id)

    # Re-run with after parameters (T-12-02: method validated inside run_method)
    after_result = run_method(dataset_id, method, **params_after)
    after_result_id = registry.store_result(after_result)

    # Build diagnostics for before and after
    # Pass argvals so Branch B (smoothing/basis) can re-run the GCV sweep if needed
    before_diag = build_diagnostics(before_result, method, argvals=argvals)
    after_diag = build_diagnostics(after_result, method, argvals=argvals)

    # Compute delta: after - before for every finite scalar numeric key present in both
    delta: dict = {}
    for key in before_diag:
        if key not in after_diag:
            continue
        v_before = before_diag[key]
        v_after = after_diag[key]
        # Exclude booleans, non-scalars (lists, dicts, str, None)
        if isinstance(v_before, bool) or isinstance(v_after, bool):
            continue
        if not isinstance(v_before, (int, float)):
            continue
        if not isinstance(v_after, (int, float)):
            continue
        # Exclude non-finite values (inf, nan)
        if not math.isfinite(v_before) or not math.isfinite(v_after):
            continue
        delta[key] = v_after - v_before

    return {
        "before_result_id": before_result_id,
        "after_result_id": after_result_id,
        "before": before_diag,
        "after": after_diag,
        "delta": delta,
    }
