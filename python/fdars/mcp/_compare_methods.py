"""fdars MCP compare-methods helper — multi-candidate deterministic ranking.

This module exposes ``compare_methods_mcp``, the core logic for the
``fdars_compare_methods`` MCP tool (COMPARE-04).  Given a dataset handle and a
list of per-candidate scalar-param dicts for a single runnable method, it:

1. Validates each candidate's parameter keys against the allowlist.
2. Re-runs the fdars method for each candidate via ``run_method``.
3. Stores each raw result in the handle registry.
4. Builds diagnostics for each candidate via ``advisor.build_diagnostics``.
5. Delegates ranking to ``fdars.advisor._compare_methods.compare_methods``
   with ``run_llm=False`` (the deterministic offline core — never calls advise).
6. Returns a by-reference ranking dict: only handles + scalar metric values
   cross the MCP boundary (no arrays — Anti-Pattern 4).

The compute path is **fully deterministic and LLM-free** — fdars produces
every number; no ``anthropic`` / provider package is ever imported.
``ANTHROPIC_API_KEY`` is never required here (COMPARE-04, T-51-09).

Requires the ``fdars[mcp]`` optional extra (Python >=3.10).

Call chain::

    fdars_compare_methods  (server.py — @mcp.tool boundary)
        -> compare_methods_mcp  (this module)
            -> run_method (per candidate)  (_runner.py)
            -> registry.store_result       (_registry.py)
            -> build_diagnostics           (advisor.__init__)
            -> compare_methods(run_llm=False)  (advisor._compare_methods)
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

__all__ = ["compare_methods_mcp"]

# Allowlist of valid candidate-param keys — mirrors _compare._ALLOWED_PARAMS
# and the fdars_run_method signature (T-12-03 / T-51-10 allowlist).
_ALLOWED_PARAMS = frozenset({"lambda_", "n_basis", "n_comp", "k", "seed"})


def _make_label(method: str, params: dict, index: int) -> str:
    """Derive a stable, human-readable label for a candidate.

    Format: ``"method(key=val, ...)"`` — e.g. ``"clustering(k=3)"``.
    When no params are supplied the label is ``"method[N]"`` where N is the
    index (0-based).  The index is appended as a suffix when two candidates
    happen to share the same param string (uniqueness guarantee).
    """
    if not params:
        return f"{method}[{index}]"
    parts = ", ".join(f"{k}={v!r}" for k, v in sorted(params.items()))
    return f"{method}({parts})"


def compare_methods_mcp(
    dataset_id: str,
    method: str,
    candidate_params: list[dict],
    metric: str | None = None,
) -> dict:
    """Re-run each candidate and return the deterministic ranking by-reference.

    For each entry in ``candidate_params`` (a list of flat scalar-param dicts),
    validates the keys, calls ``run_method``, stores the raw result, builds
    diagnostics, and delegates ranking to the deterministic offline core
    ``compare_methods(run_llm=False)``.

    This function is **provably LLM-free** — it never imports or calls
    ``advise()`` or any provider (COMPARE-04, T-51-09).

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID for the dataset stored in the handle registry.
        Obtain via ``registry.store_dataset(data, argvals)``.
    method : str
        One of the six runnable methods (``'alignment'``, ``'fpca'``,
        ``'basis'``, ``'smoothing'``, ``'clustering'``, ``'depth'``).
        Validated against ``_runner._RUNNABLE_METHODS`` inside ``run_method``.
    candidate_params : list[dict]
        List of flat scalar-param dicts — one per candidate.  Each dict's
        keys must be a subset of
        ``{'lambda_', 'n_basis', 'n_comp', 'k', 'seed'}``; any unknown key
        raises :exc:`ValueError` before any run (T-51-10 allowlist).
        An empty dict is valid (runs the method with all defaults).
    metric : str, optional
        Ranking metric key (must exist in the metric registry).  When
        omitted the per-family default is used (e.g. ``'mean_amplitude_separation'``
        for clustering).

    Returns
    -------
    dict
        JSON-serialisable ranking dict with keys:

        ``ranking_id`` : str
            Opaque handle ID for the full ranking dict stored in the registry.
        ``method`` : str
            The task family / method name (normalised to lowercase).
        ``metric`` : str
            The ranking metric key used.
        ``winner`` : str
            Label of the best candidate (deterministic fdars sort, COMPARE-01).
        ``ranking`` : list[dict]
            Ordered list (best → worst), each entry containing:
            ``{"label": str, "result_id": str, "metric_value": float|None}``.
            Arrays stay in the registry — only handles + scalar metric values
            appear here (Anti-Pattern 4 / T-51-11).

    Raises
    ------
    ValueError
        If any candidate-params dict contains a key outside the allowlist
        (T-51-10), or if the metric / family is invalid (propagated from the
        ranking core).
    KeyError
        If ``dataset_id`` is not in the registry (T-12-01: fail closed).

    Notes
    -----
    Labels are derived from the method name + sorted param key=value pairs
    (e.g. ``"clustering(k=3, seed=42)"``).  When two candidates share
    identical params an index suffix is appended to guarantee uniqueness.
    """
    # T-51-10: allowlist-validate all candidate param dicts BEFORE any run.
    for i, params in enumerate(candidate_params):
        unknown = set(params) - _ALLOWED_PARAMS
        if unknown:
            raise ValueError(
                f"compare_methods_mcp: candidate[{i}] contains unknown param key(s) "
                f"{sorted(unknown)!r}. "
                f"Allowed keys: {sorted(_ALLOWED_PARAMS)!r}."
            )

    # Deferred imports: keep module import side-effect-free and LLM-free.
    from fdars.mcp._runner import run_method
    from fdars.mcp._registry import registry
    from fdars.advisor import build_diagnostics
    from fdars.advisor._compare_methods import compare_methods as _rank_core

    method_lc = method.lower()

    # Resolve dataset (needed for build_diagnostics argvals).
    data, argvals = registry.get_dataset(dataset_id)

    # --- Step 1: run each candidate, store result, build diagnostics. ---
    # Track result_ids alongside labels for the by-reference return.
    labeled_result_ids: dict[str, str] = {}      # label -> result_id
    labeled_diagnostics: dict[str, dict] = {}    # label -> diagnostics dict

    # Generate labels and ensure uniqueness.
    raw_labels: list[str] = []
    for i, params in enumerate(candidate_params):
        raw_labels.append(_make_label(method_lc, params, i))

    # Uniquify labels: append _[index] if two candidates share the same label.
    seen: dict[str, int] = {}
    labels: list[str] = []
    for raw in raw_labels:
        if raw_labels.count(raw) > 1:
            count = seen.get(raw, 0)
            seen[raw] = count + 1
            labels.append(f"{raw}[{count}]")
        else:
            labels.append(raw)

    for label, params in zip(labels, candidate_params):
        raw_result = run_method(dataset_id, method_lc, **params)
        result_id = registry.store_result(raw_result)
        labeled_result_ids[label] = result_id

        # Build diagnostics — pass argvals for distance metrics (mirrors _compare.py).
        diag = build_diagnostics(raw_result, method_lc, argvals=argvals)
        labeled_diagnostics[label] = diag

    # --- Step 2: delegate ranking to the deterministic offline core. ---
    # compare_methods(run_llm=False) sorts candidates by metric; the LLM is
    # never involved (COMPARE-01).  Passing pre-built diagnostics dicts avoids
    # double-running (the dicts already carry the "method" key).
    core_result = _rank_core(
        labeled_diagnostics,
        method=method_lc,
        metric=metric,
        run_llm=False,
    )

    # --- Step 3: build the by-reference return (no arrays). ---
    # Each ranking entry replaces the diagnostics dict with a result_id handle
    # and exposes only the scalar metric_value (Anti-Pattern 4 / T-51-11).
    ranking_by_ref = [
        {
            "label": entry["label"],
            "result_id": labeled_result_ids[entry["label"]],
            "metric_value": entry["metric_value"],
        }
        for entry in core_result["ranking"]
    ]

    # Store the full ranking dict (with diagnostics) in the registry for callers
    # that need the full picture; return only its handle.
    ranking_id = registry.store_result(core_result)

    return {
        "ranking_id": ranking_id,
        "method": core_result["method"],
        "metric": core_result["metric"],
        "winner": core_result["winner"],
        "ranking": ranking_by_ref,
    }
