"""fdars.advisor._pipeline — Offline multi-stage pipeline diagnostic aggregation.

Provides ``build_pipeline_report()``, whose offline path (``run_llm=False``)
runs ``build_diagnostics`` over an ordered list of pipeline stage entries
and returns an **fdars-computed**, per-stage labeled list of diagnostic blocks.

Aggregation invariant
---------------------
Each stage's diagnostics live in their own labeled block::

    {"stage": str, "aspect": str, "diagnostics": dict}

They are NEVER flat-merged (``{**a, **b}``).  Same-keyed diagnostic values
in different stages are preserved independently in their own list elements.

Union-grounding payload
-----------------------
``_build_stages_union(blocks)`` returns ``{"_stages": [<diag>, <diag>, ...]}``,
the exact analog of Phase-51's ``{"_candidates": [...]}`` wrapper.
``_flatten_diagnostics_numbers`` recurses into the list and collects every
stage's numbers without key-collision loss.

LLM path
---------
``run_llm=True`` is reserved for Plan 02 (narrative + schema).  It raises
``NotImplementedError`` here so the Plan 02 hook is explicit.  No
``anthropic`` / provider package is imported at module load time; those
imports are deferred into the ``run_llm=True`` path when Plan 02 lands.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_result(entry: dict, key_tried: str) -> "Any | None":
    """Extract the result/diagnostics value from a stage entry dict.

    Accepted keys (in preference order): ``"diagnostics"``, ``"result"``,
    ``"value"`` — mirroring ``_normalize_candidates`` in
    ``_compare_methods.py`` for caller convenience.

    Parameters
    ----------
    entry : dict
        Stage entry dict.
    key_tried : str
        The stage_name, used only in error messages.

    Returns
    -------
    Any or None
        The resolved value, or ``None`` when no recognised key is present.
    """
    for key in ("diagnostics", "result", "value"):
        if key in entry:
            return entry[key]
    return None


def _normalize_stages(
    stages: list,
    argvals=None,
    **kwargs,
) -> "list[dict]":
    """Normalise an ordered list of stage entries into labeled diagnostic blocks.

    Per stage IN CALLER ORDER:

    * If the resolved value is a dict with a ``"method"`` key — it is a
      pre-built diagnostics dict; pass it through unchanged.
    * Otherwise — treat it as a raw fdars result dict and call
      ``build_diagnostics(value, aspect, argvals=argvals, **kwargs)`` via a
      DEFERRED local import to keep the module LLM-free at load time.

    Parameters
    ----------
    stages : list
        Ordered list of stage entry dicts.  Each entry must have
        ``"stage_name"`` (str) and ``"aspect"`` (str) keys, plus a result
        value under ``"diagnostics"``, ``"result"``, or ``"value"``.
    argvals : array_like, optional
        Forwarded to ``build_diagnostics`` for raw result dicts that need
        an evaluation grid (e.g. clustering/alignment aspects).
    **kwargs
        Forwarded to ``build_diagnostics`` for raw result dicts.

    Returns
    -------
    list[dict]
        Each element: ``{"stage": str, "aspect": str, "diagnostics": dict}``.

    Raises
    ------
    ValueError
        When a stage entry is missing ``"stage_name"`` or ``"aspect"``.
    """
    from fdars.advisor import build_diagnostics  # noqa: PLC0415 — deferred, LLM-free

    blocks: list[dict] = []
    for i, entry in enumerate(stages):
        if not isinstance(entry, dict):
            raise ValueError(
                f"build_pipeline_report: stage entry at index {i} must be a dict, "
                f"got {type(entry).__name__!r}."
            )
        if "stage_name" not in entry:
            raise ValueError(
                f"build_pipeline_report: stage entry at index {i} is missing "
                f"'stage_name'. Each stage must have 'stage_name' and 'aspect' keys."
            )
        if "aspect" not in entry:
            raise ValueError(
                f"build_pipeline_report: stage entry at index {i} (stage_name="
                f"{entry.get('stage_name')!r}) is missing 'aspect'. "
                "Each stage must have 'stage_name' and 'aspect' keys."
            )

        stage_name: str = str(entry["stage_name"])
        aspect: str = str(entry["aspect"])
        value = _resolve_result(entry, stage_name)

        # Detect whether this is already a built diagnostics dict.
        # build_diagnostics always sets diag["method"] = <aspect string>.
        if isinstance(value, dict) and "method" in value:
            # Pre-built diagnostics dict — pass through unchanged (no re-run).
            diag = value
        else:
            # Raw result dict (or Fdata-like) — build diagnostics now.
            # IMPORTANT: forward argvals and **kwargs exactly as Phase-51 CR-01
            # lesson requires (missing argvals causes metric=None for clustering).
            diag = build_diagnostics(value, aspect, argvals=argvals, **kwargs)

        blocks.append({
            "stage": stage_name,
            "aspect": aspect,
            "diagnostics": diag,
        })

    return blocks


def _build_stages_union(blocks: "list[dict]") -> dict:
    """Return the union-grounding payload for the pipeline stages.

    Mirrors Phase-51's ``{"_candidates": [...]}`` wrapper exactly:

        {"_stages": [block["diagnostics"] for block in blocks]}

    ``_flatten_diagnostics_numbers`` recurses into the list, collecting every
    numeric value from every stage without any key-collision loss (a plain
    ``dict.update()`` would silently drop same-keyed values from earlier stages).

    Parameters
    ----------
    blocks : list[dict]
        Per-stage labeled blocks (output of ``_normalize_stages``).

    Returns
    -------
    dict
        ``{"_stages": [<diagnostics_dict>, ...]}``.
    """
    return {"_stages": [b["diagnostics"] for b in blocks]}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_pipeline_report(
    stages: list,
    *,
    argvals=None,
    run_llm: bool = True,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    provider: "str | object | None" = None,
    **kwargs,
) -> dict:
    """Aggregate per-stage diagnostics into an offline pipeline diagnostic report.

    The offline path (``run_llm=False``) runs ``build_diagnostics`` per stage
    (or accepts pre-built diagnostics dicts) and returns an ordered list of
    per-stage labeled blocks.  The LLM narrative path is reserved for Plan 02
    and raises ``NotImplementedError`` when ``run_llm=True``.

    Parameters
    ----------
    stages : list
        Ordered list of stage entry dicts.  Each entry must contain:

        * ``"stage_name"`` (str) — human label for this pipeline stage
          (e.g. ``"represent"``, ``"smooth"``, ``"fpca"``, ``"clustering"``).
        * ``"aspect"`` (str) — the ``build_diagnostics`` aspect key for this
          stage (e.g. ``"represent"``, ``"smoothing"``, ``"fpca"``,
          ``"clustering"``).
        * A result value under one of the keys ``"diagnostics"``, ``"result"``,
          or ``"value"`` (accepted in that preference order), being either:

          - A pre-built diagnostics dict (has ``"method"`` key — passed through
            unchanged without re-running ``build_diagnostics``).
          - A raw fdars result dict (no ``"method"`` key — passed to
            ``build_diagnostics(value, aspect, argvals=argvals, **kwargs)``).

    argvals : array_like, optional
        Shared evaluation grid.  Forwarded to ``build_diagnostics`` for stages
        whose aspect needs it (e.g. ``"clustering"`` for amplitude/phase
        separation).
    run_llm : bool, optional
        When ``False`` (offline), return the raw aggregated dict of per-stage
        blocks.  When ``True``, call the LLM to narrate the pipeline report —
        **not yet implemented** (Plan 02 hook); raises ``NotImplementedError``.
    domain_context : str, optional
        Free-text domain description forwarded to the LLM narration
        (``run_llm=True`` only — Plan 02).
    model : str, optional
        LLM model identifier (``run_llm=True`` only — Plan 02).
    provider : str or Provider or None, optional
        LLM provider (``run_llm=True`` only — Plan 02).
    **kwargs
        Forwarded to ``build_diagnostics`` for raw result dicts.

    Returns
    -------
    dict
        Offline aggregation result::

            {
                "stages": [
                    {"stage": <str>, "aspect": <str>, "diagnostics": <dict>},
                    ...  # one block per input stage, in caller-declared order
                ]
            }

        When ``run_llm=True``: raises ``NotImplementedError`` (Plan 02 hook).

    Raises
    ------
    ValueError
        * ``stages`` is empty.
        * A stage entry is missing ``"stage_name"`` or ``"aspect"``.
    NotImplementedError
        When ``run_llm=True`` (LLM narrative path reserved for Plan 02).

    Notes
    -----
    **Aggregation invariant:** per-stage diagnostics are NEVER flat-merged.
    Two stages sharing a same-named diagnostic key (e.g. ``"n_obs"``) both
    survive — each in its own labeled list element.  A plain ``dict.update()``
    or ``{**a, **b}`` would silently overwrite earlier values; this is the
    primary security concern for pipeline grounding (T-52-01).

    **Union grounding:** the companion helper ``_build_stages_union(blocks)``
    returns ``{"_stages": [<diag>, ...]}`` — the exact analog of Phase-51's
    ``{"_candidates": [...]}`` wrapper — so ``_flatten_diagnostics_numbers``
    recurses into the list and collects every stage's numbers without key-
    collision loss (T-52-02).
    """
    # --- 1. Fail fast on empty stages list ---
    if not stages:
        raise ValueError(
            "build_pipeline_report: 'stages' is empty. "
            "Pass at least one stage entry."
        )

    # --- 2. Normalise stages to labeled blocks (IN CALLER ORDER) ---
    blocks = _normalize_stages(stages, argvals=argvals, **kwargs)

    # --- 3. Assemble the offline result ---
    result: dict = {"stages": blocks}

    # --- 4. Offline vs. LLM path ---
    if not run_llm:
        return result

    # --- 5. LLM narrative path — reserved for Plan 02 ---
    raise NotImplementedError(
        "build_pipeline_report(run_llm=True) is not yet implemented. "
        "The LLM narrative path will be added in Plan 02 (pipeline_report()). "
        "Call build_pipeline_report(run_llm=False) for the offline aggregation."
    )
