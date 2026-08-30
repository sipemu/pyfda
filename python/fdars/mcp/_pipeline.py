"""fdars MCP pipeline helper — multi-stage deterministic diagnostic report.

This module exposes ``build_pipeline_report_mcp``, the core logic for the
``fdars_build_pipeline_report`` MCP tool (PIPE-04).  Given a dataset handle
and a list of per-stage spec dicts, it:

1. Validates all stage param keys against the allowlist (before any run).
2. Validates each stage's aspect against ``_RUNNABLE_METHODS`` (before any run).
3. Re-runs the fdars method for each stage via ``run_method``.
4. Stores each raw result in the handle registry.
5. Builds diagnostics for each stage via ``advisor.build_diagnostics``.
6. Delegates aggregation to ``fdars.advisor._pipeline.build_pipeline_report``
   with ``run_llm=False`` (the deterministic offline core — LLM-free path).
7. Returns a by-reference report dict: only handles + scalar values cross the
   MCP boundary (no arrays — Anti-Pattern 4, T-52-10).

The compute path is **fully deterministic and LLM-free** — fdars produces
every number; no ``anthropic`` / provider package is ever imported.
``ANTHROPIC_API_KEY`` is never required here (PIPE-04, T-52-08).

Requires the ``fdars[mcp]`` optional extra (Python >=3.10).

Call chain::

    fdars_build_pipeline_report  (server.py — @mcp.tool boundary)
        -> build_pipeline_report_mcp  (this module)
            -> (validate params + aspects BEFORE any run)
            -> run_method (per stage)  (_runner.py)
            -> registry.store_result       (_registry.py)
            -> build_diagnostics           (advisor.__init__)
            -> build_pipeline_report(run_llm=False)  (advisor._pipeline)
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "fdars[mcp] requires Python 3.10+. "
        "The mcp package (mcp>=2.0.0) does not support Python 3.9."
    )

__all__ = ["build_pipeline_report_mcp"]

# Allowlist of valid stage-param keys — mirrors _compare_methods._ALLOWED_PARAMS
# and the fdars_run_method signature (T-52-09 allowlist).
_ALLOWED_PARAMS = frozenset({"lambda_", "n_basis", "n_comp", "k", "seed"})


def build_pipeline_report_mcp(
    dataset_id: str,
    stages: list[dict],
) -> dict:
    """Re-run each stage and return the deterministic pipeline report by-reference.

    For each entry in ``stages`` (a list of stage-spec dicts), validates the
    param keys and aspect name, calls ``run_method``, stores the raw result,
    builds diagnostics, and delegates aggregation to the deterministic offline
    core ``build_pipeline_report(run_llm=False)``.

    This function is **provably LLM-free** — it never imports or calls
    the advisor entrypoint or any LLM provider (PIPE-04, T-52-08).

    Parameters
    ----------
    dataset_id : str
        Opaque handle ID for the dataset stored in the handle registry.
        Obtain via ``registry.store_dataset(data, argvals)``.
    stages : list[dict]
        Ordered list of stage-spec dicts.  Each dict must contain:

        * ``"stage_name"`` (str) — human label for this pipeline stage
          (e.g. ``"smooth"``, ``"decompose"``).
        * ``"aspect"`` (str) — one of the six ``_RUNNABLE_METHODS`` aspects.
          Any aspect outside that set raises :exc:`ValueError` before any run
          (T-52-09: fail closed).
        * ``"params"`` (dict, optional) — flat scalar-param dict whose keys
          must be a subset of ``{'lambda_', 'n_basis', 'n_comp', 'k', 'seed'}``.
          Any unknown key raises :exc:`ValueError` before any run (T-52-09).

    Returns
    -------
    dict
        JSON-serialisable by-reference report dict with keys:

        ``report_id`` : str
            Opaque handle ID for the full aggregate report stored in the registry.
        ``stages`` : list[dict]
            Ordered list (one entry per input stage), each containing:
            ``{"stage": str, "aspect": str, "result_id": str}``.
            Arrays stay in the registry — only handles appear here
            (Anti-Pattern 4 / T-52-10).

    Raises
    ------
    ValueError
        * If any stage-params dict contains a key outside the allowlist (T-52-09).
        * If any stage's ``aspect`` is not in ``_RUNNABLE_METHODS``, naming the
          supported set.
    KeyError
        If ``dataset_id`` is not in the registry (T-12-01: fail closed).
    """
    # Import _RUNNABLE_METHODS from the runner (single source of truth).
    # Deferred to keep module import side-effect-free at load time.
    from fdars.mcp._runner import _RUNNABLE_METHODS

    # --- T-52-09: allowlist-validate ALL stage param dicts BEFORE any run. ---
    # Also validate all aspects before any run (fail-closed allowlist).
    for i, stage_spec in enumerate(stages):
        params = stage_spec.get("params") or {}
        unknown_params = set(params) - _ALLOWED_PARAMS
        if unknown_params:
            raise ValueError(
                f"build_pipeline_report_mcp: stage[{i}] ({stage_spec.get('stage_name')!r}) "
                f"contains unknown param key(s) {sorted(unknown_params)!r}. "
                f"Allowed keys: {sorted(_ALLOWED_PARAMS)!r}."
            )
        aspect = str(stage_spec.get("aspect", ""))
        aspect_lc = aspect.lower()
        if aspect_lc not in _RUNNABLE_METHODS:
            raise ValueError(
                f"build_pipeline_report_mcp: stage[{i}] ({stage_spec.get('stage_name')!r}) "
                f"has aspect {aspect!r} which is not in _RUNNABLE_METHODS. "
                f"Supported: {sorted(_RUNNABLE_METHODS)!r}."
            )

    # --- Deferred imports: keep module import side-effect-free and LLM-free. ---
    from fdars.mcp._runner import run_method
    from fdars.mcp._registry import registry
    from fdars.advisor import build_diagnostics
    from fdars.advisor._pipeline import build_pipeline_report as _offline_core

    # Resolve dataset (needed for build_diagnostics argvals).
    data, argvals = registry.get_dataset(dataset_id)

    # --- Step 1: run each stage, store result, build diagnostics. ---
    # Track result_ids and diagnostic dicts per stage for by-reference return.
    stage_result_ids: list[str] = []
    stage_diag_entries: list[dict] = []

    for stage_spec in stages:
        stage_name: str = str(stage_spec.get("stage_name", ""))
        aspect: str = str(stage_spec.get("aspect", "")).lower()
        params: dict = dict(stage_spec.get("params") or {})

        # Run the fdars method for this stage.
        raw_result = run_method(dataset_id, aspect, **params)

        # Store raw result (arrays remain in-process; by-reference invariant).
        result_id = registry.store_result(raw_result)
        stage_result_ids.append(result_id)

        # Build diagnostics — pass argvals for distance metrics
        # (mirrors _compare_methods.py CR-01 lesson: missing argvals causes
        # metric=None for clustering).
        diag = build_diagnostics(raw_result, aspect, argvals=argvals)

        # Build a stage entry for the offline core (uses "stage_name" + "aspect"
        # + "diagnostics" keys — precomputed passthrough: has "method" key so
        # _normalize_stages detects it as pre-built diagnostics, no re-run).
        stage_diag_entries.append({
            "stage_name": stage_name,
            "aspect": aspect,
            "diagnostics": diag,
        })

    # --- Step 2: delegate aggregation to the deterministic offline core. ---
    # build_pipeline_report(run_llm=False) aggregates the list of per-stage
    # labeled blocks; the LLM is never involved (PIPE-04).
    # Passing pre-built diagnostics dicts (each carrying the "method" key)
    # avoids double-running (mirrors _compare_methods.py Step 2 pattern).
    core_result = _offline_core(
        stage_diag_entries,
        argvals=argvals,
        run_llm=False,
    )

    # --- Step 3: build the by-reference return (no arrays). ---
    # Store the full aggregate in the registry for callers needing the detail.
    report_id = registry.store_result(core_result)

    # Per-stage entries: stage name, aspect, result_id handle only.
    stages_by_ref = [
        {
            "stage": str(stage_spec.get("stage_name", "")),
            "aspect": str(stage_spec.get("aspect", "")).lower(),
            "result_id": result_id,
        }
        for stage_spec, result_id in zip(stages, stage_result_ids)
    ]

    return {
        "report_id": report_id,
        "stages": stages_by_ref,
    }
