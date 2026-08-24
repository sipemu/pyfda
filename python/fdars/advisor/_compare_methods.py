"""fdars.advisor._compare_methods — Deterministic comparative method-selection.

Provides ``compare_methods()``, whose offline path (``run_llm=False``) runs
``build_diagnostics`` over N labeled candidates and returns an **fdars-computed**
ranking on a shared metric.  The LLM is never involved in choosing the winner
(COMPARE-01); incommensurable comparisons fail closed with ``ValueError``
(COMPARE-03).

Grounding invariant
-------------------
The winner is the top of the fdars deterministic sort.  The same inputs always
yield the same winner (stable sort on a preserved index breaks ties by insertion
order).  No ``anthropic`` / provider package is imported at module load time;
those imports are deferred into the ``run_llm=True`` path (Plan 02).

Metric registry
---------------
``_METRIC_REGISTRY`` maps each canonical metric key to ``"higher"`` (larger
value = better) or ``"lower"`` (smaller value = better).

``_DEFAULT_METRIC_BY_FAMILY`` maps each task family to its canonical default
metric key.  Both tables are derived from the actually-shipped diagnostics
builders (fdars/advisor/aspects/*.py) — no fabricated keys.

Notes on ``cumulative_variance_explained`` (fpca family)
---------------------------------------------------------
The FPCA diagnostics builder returns ``cumulative_variance_explained`` as a
list (cumulative per component).  When this key is used as a ranking metric
the ranker extracts the last element (total cumulative variance) as the scalar
for comparison.  This extraction is handled in ``_extract_metric_value``.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Metric registry
# ---------------------------------------------------------------------------

# Maps metric key -> "higher" | "lower"
_METRIC_REGISTRY: dict[str, str] = {
    "mean_amplitude_separation": "higher",   # clustering (fdars.advisor.aspects.clustering)
    "mean_phase_separation": "higher",       # clustering (fdars.advisor.aspects.clustering)
    "optimal_gcv": "lower",                  # smoothing + basis (fdars.advisor.aspects.smoothing/basis)
    "optimal_edf": "lower",                  # basis (fdars.advisor.aspects.basis)
    "min_cv_error": "lower",                 # regression_cv (fdars.advisor.aspects.regression_cv)
    "r_squared": "higher",                   # regression (fdars.advisor.aspects.regression)
    "functional_mae": "lower",               # scoring (fdars.advisor.aspects.scoring)
    "functional_mse": "lower",               # scoring (fdars.advisor.aspects.scoring)
    "functional_mape": "lower",              # scoring (fdars.advisor.aspects.scoring)
    "functional_msle": "lower",              # scoring (fdars.advisor.aspects.scoring)
    "functional_explained_variance": "higher",  # scoring (fdars.advisor.aspects.scoring)
    "cumulative_variance_explained": "higher",  # fpca (fdars.advisor.aspects.fpca — last element)
}

# Maps task family -> canonical default metric key
_DEFAULT_METRIC_BY_FAMILY: dict[str, str] = {
    "clustering": "mean_amplitude_separation",
    "smoothing": "optimal_gcv",
    "basis": "optimal_edf",
    "regression_cv": "min_cv_error",
    "regression": "r_squared",
    "scoring": "functional_mse",
    "fpca": "cumulative_variance_explained",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_metric_value(diagnostics: dict, metric: str) -> "float | None":
    """Extract the scalar metric value from a diagnostics dict.

    For most metrics the value is already a scalar.  For
    ``cumulative_variance_explained`` (fpca) the value is a list; the last
    element (total cumulative variance) is the meaningful scalar for ranking.

    Returns ``None`` when the key is absent or when the value cannot be
    reduced to a scalar float.
    """
    val = diagnostics.get(metric)
    if val is None:
        return None
    # List-valued metric: take the last element (e.g. cumulative_variance_explained).
    if isinstance(val, (list, tuple)):
        if not val:
            return None
        val = val[-1]
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _detect_family(diagnostics: dict) -> "str | None":
    """Return the task family from a diagnostics dict's ``method`` key.

    ``build_diagnostics`` always sets ``diagnostics["method"]`` to the
    method string (e.g. ``"clustering"``).  Returns ``None`` for pre-built
    dicts that lack a ``"method"`` key.
    """
    return diagnostics.get("method")


def _normalize_candidates(
    candidates: "dict | list",
    method: "str | None",
    argvals=None,
    **kwargs,
) -> "list[dict]":
    """Normalise the diverse candidate input into a uniform list of labeled blocks.

    Parameters
    ----------
    candidates : dict or list
        Accepted input forms:

        * ``{label: diagnostics_or_result_dict, ...}`` — plain dict mapping
          label -> value.
        * ``[(label, value), ...]`` — list of (label, value) 2-tuples.
        * ``[{"label": ..., "value": ...}, ...]`` — list of spec dicts with
          explicit keys.

        Each *value* is either:

        * A pre-built diagnostics dict (has ``"method"`` key — pass through).
        * A raw fdars result dict without ``"method"`` — call
          ``build_diagnostics(value, method)`` where ``method`` must be
          supplied by the caller.

    method : str or None
        The task family string passed to ``compare_methods``.  Required when
        any candidate value is a raw result dict (lacking ``"method"``).
    argvals : array_like, optional
        Forwarded to ``build_diagnostics`` when building diagnostics from raw
        result dicts.  Required by clustering/alignment aspects to compute
        distance-based metrics (e.g. ``mean_amplitude_separation``).
    **kwargs
        Additional keyword arguments forwarded to ``build_diagnostics`` when
        building diagnostics from raw result dicts.

    Returns
    -------
    list[dict]
        Each element: ``{"label": str, "method": str, "diagnostics": dict}``.
    """
    from fdars.advisor import build_diagnostics  # noqa: PLC0415 — local import, LLM-free

    # Normalise input to a list of (label, raw_value) pairs, preserving
    # insertion order (critical for stable tie-break by candidate order).
    pairs: list[tuple[str, Any]]
    if isinstance(candidates, dict):
        pairs = list(candidates.items())
    elif isinstance(candidates, list):
        normalised: list[tuple[str, Any]] = []
        for item in candidates:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                normalised.append((str(item[0]), item[1]))
            elif isinstance(item, dict) and "label" in item:
                val = item.get("diagnostics") or item.get("value") or item.get("result")
                normalised.append((str(item["label"]), val))
            else:
                raise ValueError(
                    f"compare_methods: unrecognised candidate format {item!r}. "
                    "Expected (label, value) 2-tuple or dict with 'label' key."
                )
        pairs = normalised
    else:
        raise TypeError(
            f"compare_methods: 'candidates' must be a dict or list, got {type(candidates).__name__!r}."
        )

    blocks: list[dict] = []
    for label, value in pairs:
        # Detect whether this is already a built diagnostics dict.
        # build_diagnostics always sets diag["method"] = <family string>.
        if isinstance(value, dict) and "method" in value:
            # Pre-built diagnostics dict — pass through unchanged.
            diag = value
        else:
            # Raw result dict — build diagnostics; method MUST be supplied.
            if method is None:
                raise ValueError(
                    f"compare_methods: candidate {label!r} is a raw result dict "
                    "but no 'method' (task family) was passed to compare_methods(). "
                    "Pass method='clustering' (or the relevant family) or supply "
                    "pre-built diagnostics dicts."
                )
            diag = build_diagnostics(value, method, argvals=argvals, **kwargs)
        family = _detect_family(diag) or method or ""
        blocks.append({"label": label, "method": family, "diagnostics": diag})

    return blocks


def _assert_commensurable(blocks: list[dict], metric: str) -> None:
    """Raise ``ValueError`` if the candidates are incommensurable.

    Two reject conditions (per 51-CONTEXT "Incommensurability guard"):

    1. Candidates span more than one distinct task family (``method`` field).
    2. The resolved ``metric`` key is absent from — or ``None`` in — ANY
       candidate's diagnostics.  The whole comparison is rejected; no candidate
       is silently dropped.

    Parameters
    ----------
    blocks : list[dict]
        Normalised candidate blocks (output of ``_normalize_candidates``).
    metric : str
        The resolved ranking metric key.

    Raises
    ------
    ValueError
        With a description of which families conflict, or which label(s) are
        missing the metric.
    """
    # Guard 1: mixed task families.
    families = {b["method"] for b in blocks}
    if len(families) > 1:
        sorted_families = sorted(families)
        raise ValueError(
            f"compare_methods: incommensurable candidates — candidates span "
            f"multiple task families: {sorted_families}. All candidates must "
            f"share the same task family for a valid comparison."
        )

    # Guard 2: metric absent from any candidate.
    offending: list[str] = []
    for b in blocks:
        val = _extract_metric_value(b["diagnostics"], metric)
        if val is None:
            offending.append(b["label"])
    if offending:
        raise ValueError(
            f"compare_methods: metric {metric!r} is absent or None for "
            f"candidate(s) {offending}. All candidates must have the ranking "
            f"metric present. Pass a different metric= or ensure all candidates "
            f"carry this diagnostic key."
        )


def _rank(blocks: list[dict], metric: str) -> tuple[list[dict], str]:
    """Sort candidates by metric value; return (ordered_ranking, winner_label).

    Sorting uses the registry direction (higher-is-better = descending sort;
    lower-is-better = ascending sort).  Ties are broken by the candidate's
    original insertion index (stable sort — same inputs always yield the same
    winner, COMPARE-01).

    An unknown metric key raises ``ValueError`` (T-51-04: no arbitrary code
    path from the metric string).

    Parameters
    ----------
    blocks : list[dict]
        Normalised candidate blocks.  Assumes ``_assert_commensurable`` has
        already validated them.
    metric : str
        Resolved ranking metric key — must exist in ``_METRIC_REGISTRY``.

    Returns
    -------
    tuple[list[dict], str]
        The ranking list (best -> worst) and the winner label.

    Raises
    ------
    ValueError
        When ``metric`` is not in ``_METRIC_REGISTRY``.
    """
    if metric not in _METRIC_REGISTRY:
        raise ValueError(
            f"compare_methods: metric {metric!r} is not in the metric registry. "
            f"Supported metric keys: {sorted(_METRIC_REGISTRY)!r}."
        )

    direction = _METRIC_REGISTRY[metric]
    reverse = direction == "higher"  # descending for higher-is-better

    # Tag each block with its original index for stable tie-breaking.
    indexed: list[tuple[int, dict]] = list(enumerate(blocks))

    def sort_key(item: tuple[int, dict]) -> tuple[float, int]:
        idx, block = item
        val = _extract_metric_value(block["diagnostics"], metric)
        if val is None:
            raise ValueError(
                f"compare_methods: internal error — metric {metric!r} became None "
                f"for candidate {block['label']!r} during sort. "
                "Do not mutate diagnostics dicts while compare_methods() is running."
            )
        # For descending sort (higher), negate the value so Python's default
        # ascending sort puts the best candidate first.
        sort_val = -val if reverse else val
        return (sort_val, idx)  # idx is the tie-break (insertion order)

    indexed.sort(key=sort_key)

    ranking: list[dict] = []
    for _, block in indexed:
        val = _extract_metric_value(block["diagnostics"], metric)
        ranking.append({
            "label": block["label"],
            "method": block["method"],
            "metric_value": val,
            "diagnostics": block["diagnostics"],
        })

    winner = ranking[0]["label"]
    return ranking, winner


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compare_methods(
    candidates: "dict | list",
    method: "str | None" = None,
    *,
    metric: "str | None" = None,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    provider: "str | object | None" = None,
    run_llm: bool = True,
    argvals=None,
    **kwargs,
) -> dict:
    """Rank candidate fdars methods by a shared diagnostic metric.

    The winner is determined by a **deterministic fdars-computed sort** — the
    LLM never chooses the winner (COMPARE-01).  Incommensurable inputs
    (mixed task families or missing metric) raise ``ValueError`` before any
    ranking is produced (COMPARE-03).

    Parameters
    ----------
    candidates : dict or list
        Labeled candidate inputs.  Accepted forms:

        * ``{"label_a": diag_or_result_dict, "label_b": ..., ...}``
        * ``[("label_a", diag_or_result), ...]`` — list of 2-tuples
        * ``[{"label": "a", "value": ...}, ...]`` — list of spec dicts

        Each value is either a pre-built diagnostics dict (has ``"method"``
        key) or a raw fdars result dict (requires ``method`` param).
    method : str, optional
        Task family (``"clustering"``, ``"smoothing"``, ``"basis"``,
        ``"regression_cv"``, ``"regression"``, ``"scoring"``, ``"fpca"``).
        Required when any candidate value is a raw result dict.  Ignored when
        all candidates are pre-built diagnostics dicts (which carry the family
        in their ``"method"`` key).
    metric : str, optional
        Ranking metric key (must exist in ``_METRIC_REGISTRY``).  When
        omitted the per-family default from ``_DEFAULT_METRIC_BY_FAMILY`` is
        used.  Raises ``ValueError`` when the family has no registered default.
    domain_context : str, optional
        Free-text domain description forwarded to the LLM narration
        (``run_llm=True`` only).
    model : str, optional
        LLM model identifier (``run_llm=True`` only).
    provider : str or Provider or None, optional
        LLM provider (``run_llm=True`` only).
    run_llm : bool, optional
        When ``True`` (default), call the LLM to narrate the ranking via the
        "comparison" task family; the fdars-computed winner is fixed before the
        call and never overridden by the narration.
        When ``False``, return the raw deterministic ranking dict offline.
    argvals : array_like, optional
        Reserved; forwarded to ``build_diagnostics`` when building diagnostics
        from raw result dicts.
    **kwargs
        Forwarded to ``build_diagnostics`` when building diagnostics from raw
        result dicts.

    Returns
    -------
    dict
        Ranking result::

            {
                "method": <task family str>,
                "metric": <metric key str>,
                "ranking": [
                    {"label": <str>, "method": <str>,
                     "metric_value": <float>, "diagnostics": <dict>},
                    ...  # ordered best -> worst
                ],
                "winner": <best label str>,
            }

    Raises
    ------
    ValueError
        * No registered default metric for the resolved task family.
        * Metric key not in ``_METRIC_REGISTRY``.
        * Candidates span more than one task family (COMPARE-03).
        * Any candidate is missing the ranking metric (COMPARE-03).
    NotImplementedError
        When ``run_llm=True`` (Plan 02 not yet implemented).
    """
    # --- 1. Normalise candidates to labeled blocks ---
    blocks = _normalize_candidates(candidates, method, argvals=argvals, **kwargs)

    # --- 2. Resolve the task family (from blocks or caller-supplied method) ---
    # All blocks have their family in the "method" field (set by _normalize_candidates).
    # Use the caller-supplied method as a hint; then verify after the guard.
    families = {b["method"] for b in blocks}

    # --- 2a. Fail-closed family check FIRST (mixed families → ValueError before metric
    # resolution, per 51-CONTEXT "Incommensurability guard") ---
    if len(families) > 1:
        sorted_families = sorted(families)
        raise ValueError(
            f"compare_methods: incommensurable candidates — candidates span "
            f"multiple task families: {sorted_families}. All candidates must "
            f"share the same task family for a valid comparison."
        )

    # Single family confirmed: extract it.
    family = next(iter(families)) if families else (method or "")

    # --- 3. Resolve the ranking metric ---
    if metric is not None:
        # Validate the caller-supplied metric against the registry immediately
        # (T-51-04: unknown metric → ValueError before commensurability guard).
        if metric not in _METRIC_REGISTRY:
            raise ValueError(
                f"compare_methods: metric {metric!r} is not in the metric registry. "
                f"Supported metric keys: {sorted(_METRIC_REGISTRY)!r}."
            )
        resolved_metric = metric
    else:
        if family not in _DEFAULT_METRIC_BY_FAMILY:
            supported = sorted(_DEFAULT_METRIC_BY_FAMILY)
            raise ValueError(
                f"compare_methods: no default ranking metric for task family "
                f"{family!r}. Supported families: {supported!r}. "
                "Pass metric=<key> explicitly or use a supported family."
            )
        resolved_metric = _DEFAULT_METRIC_BY_FAMILY[family]

    # --- 4. Fail-closed metric-presence guard (COMPARE-03) ---
    # (Family already validated above; this checks metric presence per candidate.)
    _assert_commensurable(blocks, resolved_metric)

    # --- 5. Deterministic sort → winner (COMPARE-01) ---
    ranking, winner = _rank(blocks, resolved_metric)

    result: dict = {
        "method": family,
        "metric": resolved_metric,
        "ranking": ranking,
        "winner": winner,
    }

    # --- 6. Offline vs. LLM path ---
    if not run_llm:
        return result

    # --- 7. LLM narration path (COMPARE-01, COMPARE-02) ---
    # The winner is already decided (step 5); the LLM only narrates the ranking.
    # Deferred imports: keep module import side-effect-free.
    import json as _json  # noqa: PLC0415

    from fdars.advisor._prompts import _system_prompt  # noqa: PLC0415
    from fdars.advisor._schema import Advice  # noqa: PLC0415
    from fdars.advisor.providers._factory import resolve_provider  # noqa: PLC0415
    from fdars.advisor.providers._validate import _check_grounding  # noqa: PLC0415

    p = resolve_provider(provider=provider, model=model)
    system = _system_prompt("comparison", aspect=family)

    # Build per-candidate labeled provenance payload (COMPARE-02, PITFALLS 7 & 13).
    # Each block is {"label": ..., "diagnostics": ...} — NEVER a flat-merged dict.
    provenance_blocks = [
        {"label": r["label"], "diagnostics": r["diagnostics"]}
        for r in ranking
    ]

    # Build the user message carrying:
    #   - domain context
    #   - winner (fdars-determined)
    #   - per-candidate labeled diagnostics blocks (preserving provenance)
    candidates_json = _json.dumps(provenance_blocks, sort_keys=True, indent=2)
    user_content = (
        f"Domain context: {domain_context}\n\n"
        f"Task: comparison\n\n"
        f"fdars-computed winner: {winner!r}\n\n"
        f"fdars-computed ranking (best to worst):\n"
        + _json.dumps(
            [{"rank": i + 1, "label": r["label"], "metric": resolved_metric,
              "metric_value": r["metric_value"]}
             for i, r in enumerate(ranking)],
            indent=2,
        )
        + "\n\nPer-candidate diagnostics (one labeled block per candidate):\n"
        + candidates_json
    )

    messages = [{"role": "user", "content": user_content}]
    advice = p.complete_structured(Advice, messages, system)

    # GROUND-03 (per-candidate): run _check_grounding once per candidate block
    # so every cited value is traced to its correct candidate's own diagnostics.
    # A value present only in candidate A's block is NOT a valid citation for a
    # claim grounded in candidate B's block (PITFALLS 7 & 13, COMPARE-02).
    for block in provenance_blocks:
        _check_grounding(advice, block["diagnostics"])

    # Re-assert winner from the fdars sort: the LLM narration cannot override it
    # (COMPARE-01, T-51-05).  The result always carries the pre-computed winner.
    result["advice"] = advice

    return result
