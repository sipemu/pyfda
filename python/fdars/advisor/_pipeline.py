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
``run_llm=True`` produces a grounded narrative report via the "pipeline"
advise task family (see :func:`pipeline_report`): deterministic Python
caveats are computed first, per-stage labeled blocks are sent to the LLM,
and grounding is checked once against the ``{"_stages": [...]}`` union.  No
``anthropic`` / provider package is imported at module load time; those
imports are deferred into the ``run_llm=True`` path.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Cross-stage caveat threshold constants (PIPE-03)
#
# Conservative defaults — prefer to warn when in doubt.  Override any default
# via the ``thresholds`` dict param of ``_compute_cross_stage_caveats``.
#
# _IMPUTED_FRACTION_CAVEAT_THRESHOLD : float
#     When a represent-aspect stage's ``imputed_fraction`` exceeds this value,
#     emit a Rule-1 caveat about FPCA/clustering reliability.  Default 0.2
#     (20 % imputed cells) is conservative — even modest imputation at scale
#     can bias FPCA decomposition.
#
# _OUTLIER_FRACTION_CAVEAT_THRESHOLD : float
#     When an outliers-aspect stage's derived fraction of flagged observations
#     exceeds this value, emit a Rule-2 downstream caveat.  Default 0.15
#     (15 % flagged).  A 15 % outlier rate meaningfully distorts group-level
#     statistics and downstream clustering/regression.
#
# _LOW_CUMULATIVE_VARIANCE_THRESHOLD : float
#     When an fpca-aspect stage's LAST ``cumulative_variance_explained`` element
#     is BELOW this value, emit a Rule-3 clustering-reliability caveat.  Default
#     0.80 (80 % cumulative variance).  Clustering in a subspace that captures
#     less than 80 % of total functional variance risks ignoring amplitude
#     patterns that drive cluster separation.
# ---------------------------------------------------------------------------

_IMPUTED_FRACTION_CAVEAT_THRESHOLD: float = 0.20
"""Rule-1 threshold: imputed_fraction above this fires an FPCA/clustering caveat."""

_OUTLIER_FRACTION_CAVEAT_THRESHOLD: float = 0.15
"""Rule-2 threshold: outlier fraction above this fires a downstream caveat."""

_LOW_CUMULATIVE_VARIANCE_THRESHOLD: float = 0.80
"""Rule-3 threshold: last cumulative_variance_explained below this fires a clustering caveat."""


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
# Cross-stage caveat rule table (PIPE-03)
# ---------------------------------------------------------------------------

def _compute_cross_stage_caveats(
    blocks: "list[dict]",
    *,
    thresholds: "dict | None" = None,
) -> "list[dict]":
    """Compute DETERMINISTIC cross-stage caveats from per-stage diagnostic blocks.

    This function is **pure Python on real fdars-computed scalars** — the LLM
    is never involved.  The returned caveats are authoritative; the LLM is only
    asked to narrate them (see ``pipeline_report``).

    Rules applied (each may emit at most one caveat per qualifying stage block):

    * **Rule 1 (R1)**: A ``represent``-aspect block with
      ``imputed_fraction > _IMPUTED_FRACTION_CAVEAT_THRESHOLD`` emits a caveat
      about FPCA/clustering reliability, citing the real ``imputed_fraction``
      value.
    * **Rule 2 (R2)**: An ``outliers``-aspect block whose derived outlier
      fraction exceeds ``_OUTLIER_FRACTION_CAVEAT_THRESHOLD`` emits a
      downstream-analysis caveat.  Fraction preference order:
      ``outlier_fraction`` → ``n_outliers / n_obs`` → ``n_union_outliers`` as
      raw count (fires when count > ``_OUTLIER_FRACTION_CAVEAT_THRESHOLD *
      100``, i.e. more than 15 outliers by default).
    * **Rule 3 (R3)**: An ``fpca``-aspect block whose **last element** of
      ``cumulative_variance_explained`` is below
      ``_LOW_CUMULATIVE_VARIANCE_THRESHOLD`` emits a clustering-reliability
      caveat, citing the real last-element value.

    Parameters
    ----------
    blocks : list[dict]
        Per-stage labeled blocks as produced by ``_normalize_stages`` — each
        element is ``{"stage": str, "aspect": str, "diagnostics": dict}``.
        The function reads only the ``diagnostics`` sub-dict for each block
        and never flat-merges blocks.
    thresholds : dict or None, optional
        Override any default threshold constant for this call.  Keys:

        * ``"imputed_fraction"`` — overrides ``_IMPUTED_FRACTION_CAVEAT_THRESHOLD``
        * ``"outlier_fraction"`` — overrides ``_OUTLIER_FRACTION_CAVEAT_THRESHOLD``
        * ``"cumulative_variance"`` — overrides ``_LOW_CUMULATIVE_VARIANCE_THRESHOLD``

        Other keys are silently ignored.

    Returns
    -------
    list[dict]
        Ordered list of structured caveat dicts.  Each dict has keys:

        * ``"stage"`` (str) — source stage name
        * ``"aspect"`` (str) — source aspect name
        * ``"rule"`` (str) — rule identifier (``"R1"``, ``"R2"``, ``"R3"``)
        * ``"value"`` (float or int) — the real diagnostic value that triggered
          the rule (native Python type; no NumPy scalars)
        * ``"message"`` (str) — plain-language caveat description

        An empty list means no thresholds were exceeded.
    """
    t = thresholds or {}
    imputed_thresh = float(t.get("imputed_fraction", _IMPUTED_FRACTION_CAVEAT_THRESHOLD))
    outlier_thresh = float(t.get("outlier_fraction", _OUTLIER_FRACTION_CAVEAT_THRESHOLD))
    variance_thresh = float(t.get("cumulative_variance", _LOW_CUMULATIVE_VARIANCE_THRESHOLD))

    caveats: list[dict] = []

    for block in blocks:
        stage: str = block["stage"]
        aspect: str = block["aspect"]
        diag: dict = block["diagnostics"]

        # -- Rule 1: high imputed_fraction in represent stage ------------------
        if aspect == "represent":
            imputed = diag.get("imputed_fraction")
            if imputed is not None and float(imputed) > imputed_thresh:
                caveats.append({
                    "stage": stage,
                    "aspect": aspect,
                    "rule": "R1",
                    "value": float(imputed),
                    "message": (
                        f"The '{stage}' stage has a high imputed_fraction of "
                        f"{float(imputed):.3g} (threshold: {imputed_thresh}). "
                        "A high proportion of imputed values can bias FPCA decomposition "
                        "and clustering reliability — downstream results should be "
                        "interpreted cautiously."
                    ),
                })

        # -- Rule 2: high outlier fraction in outliers stage -------------------
        elif aspect == "outliers":
            # Derive the outlier fraction in preference order:
            # 1. outlier_fraction directly
            # 2. n_outliers / n_obs
            # 3. n_union_outliers as a raw count (fallback when no fraction or n_obs)
            fraction_value: "float | None" = None
            raw_value: "float | int | None" = None

            outlier_frac = diag.get("outlier_fraction")
            if outlier_frac is not None:
                fraction_value = float(outlier_frac)
                raw_value = float(outlier_frac)
            else:
                n_out = diag.get("n_outliers")
                n_obs = diag.get("n_obs")
                if n_out is not None and n_obs is not None and n_obs > 0:
                    fraction_value = float(n_out) / float(n_obs)
                    raw_value = fraction_value
                elif n_out is not None and n_obs is None:
                    # Only count available — use union count
                    n_union = diag.get("n_union_outliers")
                    if n_union is not None:
                        # Count-based: fire when count itself is large enough to be
                        # proportionally above the threshold at a typical N=100 study
                        fraction_value = float(n_union) / 100.0
                        raw_value = int(n_union)
                    elif n_out is not None:
                        fraction_value = float(n_out) / 100.0
                        raw_value = int(n_out)

            # Also check n_union_outliers when no other fraction was available
            if fraction_value is None:
                n_union = diag.get("n_union_outliers")
                if n_union is not None:
                    fraction_value = float(n_union) / 100.0
                    raw_value = int(n_union)

            if fraction_value is not None and fraction_value > outlier_thresh:
                assert raw_value is not None  # guaranteed by the logic above
                caveats.append({
                    "stage": stage,
                    "aspect": aspect,
                    "rule": "R2",
                    "value": raw_value if isinstance(raw_value, (float, int)) else float(raw_value),
                    "message": (
                        f"The '{stage}' stage flagged a high proportion of outliers "
                        f"({float(fraction_value):.3g} above threshold {outlier_thresh}). "
                        "A substantial outlier rate can distort downstream FPCA, "
                        "clustering, and regression analyses — review outlier removal "
                        "or robust method alternatives before proceeding."
                    ),
                })

        # -- Rule 3: low cumulative variance in fpca stage ----------------------
        elif aspect == "fpca":
            cumvar = diag.get("cumulative_variance_explained")
            if isinstance(cumvar, (list, tuple)) and len(cumvar) > 0:
                last_cumvar = float(cumvar[-1])
                if last_cumvar < variance_thresh:
                    caveats.append({
                        "stage": stage,
                        "aspect": aspect,
                        "rule": "R3",
                        "value": last_cumvar,
                        "message": (
                            f"The '{stage}' FPCA stage achieves only "
                            f"{last_cumvar:.3g} cumulative variance explained "
                            f"(threshold: {variance_thresh}). "
                            "Clustering in a subspace capturing less than "
                            f"{variance_thresh:.0%} of total functional variance risks "
                            "ignoring amplitude patterns that drive cluster separation — "
                            "consider increasing n_components before clustering."
                        ),
                    })

    return caveats


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
    per-stage labeled blocks.  With ``run_llm=True`` it delegates to
    :func:`pipeline_report` for a grounded narrative report over the same
    per-stage blocks.

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
        blocks.  When ``True``, delegate to :func:`pipeline_report` for a
        grounded narrative report (deterministic caveats + union grounding).
    domain_context : str, optional
        Free-text domain description forwarded to the LLM narration
        (``run_llm=True`` only).
    model : str, optional
        LLM model identifier (``run_llm=True`` only).
    provider : str or Provider or None, optional
        LLM provider (``run_llm=True`` only).
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

        When ``run_llm=True``: returns the :func:`pipeline_report` result
        (a validated ``PipelineReport`` with narrative + deterministic caveats).

    Raises
    ------
    ValueError
        * ``stages`` is empty.
        * A stage entry is missing ``"stage_name"`` or ``"aspect"``.
    GroundingViolationError
        When ``run_llm=True`` and the narration cites a value absent from every
        stage's diagnostics (fabrication).

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

    # --- 5. LLM narrative path — delegate to pipeline_report() (Plan 02) ---
    return pipeline_report(
        stages,
        argvals=argvals,
        domain_context=domain_context,
        model=model,
        provider=provider,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Grounding adapter for PipelineReport (PIPE-02, T-52-05)
# ---------------------------------------------------------------------------

def _check_grounding_pipeline(report: "Any", diagnostics: dict) -> None:
    """Run the union grounding check over a PipelineReport's text fields.

    ``_check_grounding`` in ``providers._validate`` expects an object with a
    ``.recommendations`` attribute (the ``Advice`` schema).  ``PipelineReport``
    has ``.stages`` (list[str]) and ``.narrative`` (str) instead.

    This adapter extracts every numeric token from the narrative and per-stage
    strings, then delegates to ``_flatten_diagnostics_numbers`` +
    ``_is_grounded_number`` from the same validate module to apply exactly the
    same check.  Raises ``GroundingViolationError`` on the first ungrounded
    numeric citation — same semantics as ``_check_grounding``.

    Parameters
    ----------
    report : PipelineReport
        The schema-validated (or stand-in) report object returned by the LLM.
    diagnostics : dict
        The union-grounding payload ``{"_stages": [<diag>, ...]}``.

    Raises
    ------
    GroundingViolationError
        When any narrative text cites a numeric value absent from all stage
        diagnostics.
    """
    from fdars.advisor.providers._validate import (  # noqa: PLC0415
        GroundingViolationError,
        _extract_numbers,
        _flatten_diagnostics_numbers,
        _is_grounded_number,
    )

    diag_numbers = _flatten_diagnostics_numbers(diagnostics)

    # Collect all text to check: the overall narrative + each per-stage string
    texts_to_check: list[str] = []
    if hasattr(report, "narrative") and report.narrative:
        texts_to_check.append(str(report.narrative))
    if hasattr(report, "stages"):
        for stage_text in report.stages:
            if stage_text:
                texts_to_check.append(str(stage_text))

    for text in texts_to_check:
        for token in _extract_numbers(text):
            if not _is_grounded_number(token, diag_numbers):
                raise GroundingViolationError(
                    f"PipelineReport narrative cites value {token!r} not found "
                    f"in any stage's diagnostics: {text[:120]!r}"
                )


# ---------------------------------------------------------------------------
# LLM narrative entry point (Plan 02 — PIPE-02)
# ---------------------------------------------------------------------------

def pipeline_report(
    stages: list,
    *,
    argvals=None,
    domain_context: str = "",
    model: str = "claude-opus-4-8",
    provider: "str | object | None" = None,
    thresholds: "dict | None" = None,
    **kwargs,
) -> "Any":
    """Narrate a multi-stage FDA pipeline diagnostic report via the 'pipeline' task family.

    This is the LLM narrative path for :func:`build_pipeline_report`.  It:

    1. Normalises stages to per-stage labeled blocks (calling
       ``build_diagnostics`` where needed — same as the offline path).
    2. Computes cross-stage caveats via ``_compute_cross_stage_caveats``
       **before** any LLM call (PIPE-03: caveats are Python-authoritative,
       never LLM-invented).
    3. Sends per-stage labeled blocks (NEVER flat-merged) plus the structured
       caveats to the LLM for narration under the ``"pipeline"`` task family.
    4. Runs ``_check_grounding`` ONCE against the ``{"_stages": [...]}`` UNION
       of all stages' diagnostics — catches fabrication while preserving
       cross-stage narration (T-52-05, Phase-51 WR-03 lesson: no per-stage-
       strict over-rejection).
    5. Attaches the Python-computed caveats to the returned result so callers
       get authoritative caveats regardless of what the LLM narrated.

    Parameters
    ----------
    stages : list
        Ordered list of stage entry dicts (same schema as
        :func:`build_pipeline_report`).  Each entry must have ``"stage_name"``
        and ``"aspect"`` keys, plus a result value under ``"diagnostics"``,
        ``"result"``, or ``"value"``.
    argvals : array_like, optional
        Shared evaluation grid forwarded to ``build_diagnostics`` for raw
        result dicts.
    domain_context : str, optional
        Free-text domain description included in the LLM user message to help
        ground the narration in the study context.
    model : str, optional
        LLM model identifier.  Default ``"claude-opus-4-8"``.
    provider : str or Provider or None, optional
        LLM provider.  ``None`` (default) uses the Anthropic default via
        ``resolve_provider``.  Pass a mock provider in tests.
    thresholds : dict or None, optional
        Override caveat thresholds (forwarded to
        ``_compute_cross_stage_caveats``).  Keys: ``"imputed_fraction"``,
        ``"outlier_fraction"``, ``"cumulative_variance"``.
    **kwargs
        Forwarded to ``build_diagnostics`` for raw result dicts.

    Returns
    -------
    PipelineReport
        Schema-validated pipeline report with ``stages`` (per-stage narrative
        sections), ``narrative`` (overall summary), and ``caveats``
        (Python-computed structured cross-stage caveats — authoritative).

    Raises
    ------
    ValueError
        When ``stages`` is empty or a stage entry is malformed.
    GroundingViolationError
        When the LLM narration cites a numeric value absent from all stages'
        diagnostics (fabrication detected by union grounding check).

    Notes
    -----
    **Union grounding (T-52-05, Phase-51 WR-03):** grounding is checked
    ONCE against ``{"_stages": [<diag>, ...]}``.  A cited value is grounded
    when it appears in ANY stage's diagnostics.  This allows cross-stage
    narration (e.g. citing the FPCA cumulative variance in the context of
    the clustering stage) without false-rejecting legitimate comparative
    statements — the WR-03 over-rejection lesson from Phase 51.

    **LLM-free module load (T-52-07):** provider, schema, and
    ``_check_grounding`` are imported inside this function, never at module
    load time.  ``from fdars.advisor._pipeline import build_pipeline_report``
    never touches the anthropic SDK.
    """
    # --- 1. Fail fast on empty stages list ---
    if not stages:
        raise ValueError(
            "pipeline_report: 'stages' is empty. "
            "Pass at least one stage entry."
        )

    # --- 2. Normalise stages to labeled blocks ---
    blocks = _normalize_stages(stages, argvals=argvals, **kwargs)

    # --- 3. Compute caveats BEFORE the LLM call (PIPE-03 — Python-authoritative) ---
    computed_caveats = _compute_cross_stage_caveats(blocks, thresholds=thresholds)

    # --- 4. Deferred imports (T-52-07 — keep module LLM-free at load time) ---
    import json as _json  # noqa: PLC0415

    from fdars.advisor._prompts import _system_prompt  # noqa: PLC0415
    from fdars.advisor._schema import PipelineReport  # noqa: PLC0415
    from fdars.advisor.providers._factory import resolve_provider  # noqa: PLC0415

    p = resolve_provider(provider=provider, model=model)
    system = _system_prompt("pipeline")

    # --- 5. Build per-stage labeled provenance payload (NEVER flat-merged) ---
    # Each block is {"stage": ..., "aspect": ..., "diagnostics": {...}}.
    # The list preserves per-stage provenance for the LLM's per-stage attribution.
    provenance_blocks = [
        {"stage": b["stage"], "aspect": b["aspect"], "diagnostics": b["diagnostics"]}
        for b in blocks
    ]
    stages_json = _json.dumps(provenance_blocks, sort_keys=True, indent=2)
    caveats_json = _json.dumps(computed_caveats, sort_keys=True, indent=2)

    user_content = (
        f"Domain context: {domain_context}\n\n"
        "Task: pipeline\n\n"
        "Per-stage diagnostics (one labeled block per stage, in pipeline order):\n"
        + stages_json
        + "\n\nPython-computed cross-stage caveats (authoritative — narrate these, "
        "do NOT invent additional caveats):\n"
        + caveats_json
    )

    messages = [{"role": "user", "content": user_content}]

    # --- 6. LLM call with PipelineReport schema ---
    report = p.complete_structured(PipelineReport, messages, system)

    # --- 7. Union grounding check (T-52-05, Phase-51 WR-03 lesson) ---
    # Check ONCE against the union of ALL stages' diagnostics.
    # Do NOT run per-stage-strict checks — that caused WR-03 over-rejection
    # in Phase 51 when cross-stage narration cited a real value from a
    # different stage than the one being described.
    union_diagnostics: dict = _build_stages_union(blocks)

    # _check_grounding expects an object with .recommendations; PipelineReport
    # has .stages/.narrative/.caveats (not .recommendations).  We use a
    # lightweight adapter so the existing grounding machinery applies to the
    # narrative text without needing a Recommendation list.
    _check_grounding_pipeline(report, union_diagnostics)

    # --- 8. Attach Python-computed caveats authoritatively (PIPE-03) ---
    # Replace the LLM-returned caveats with the Python-computed ones so the
    # caller always gets the authoritative, grounded caveats regardless of
    # what the LLM emitted.
    report.caveats = computed_caveats

    return report
