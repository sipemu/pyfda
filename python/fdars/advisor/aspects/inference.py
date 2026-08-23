"""fdars.advisor.aspects.inference — Inference diagnostics builder.

Contains ``_build_inference_diagnostics``.  Accepts a plain dict of
fdars-computed inference results supplied by the CALLER (the builder
DOES NOT import fdars.inference and DOES NOT recompute any statistic —
grounding invariant preserved throughout).

The caller obtains a ``TestResult`` dict from one of the Phase 31 inference
functions (``fdars.inference.t_perm_test``, ``fdars.inference.f_perm_test``,
``fdars.inference.two_sample_mean_test``, etc.) and passes it as the ``result``
dict to ``build_diagnostics``; this builder then summarises those already-
fdars-computed numbers and derives boolean significance flags from the
caller-supplied p-value.

Expected input shapes:

TestResult (primary shape):
    * ``statistic``  — the fdars-computed test statistic (float)
    * ``p_value``    — the fdars-computed permutation or asymptotic p-value (float)
    * ``n_perm``     — number of permutations used; **0 is a legitimate value**
      indicating the asymptotic path (e.g. Hotelling T² in
      ``two_sample_mean_test``), NOT a missing value

ToleranceBand / SCB (secondary shape, tolerated but not deeply summarised):
    * ``lower``, ``upper``, ``center``, ``half_width``
    When this shape is detected (``p_value`` absent AND ``half_width`` present)
    the builder echoes basic summary scalars and leaves all significance fields
    ``None``.

ITP interval-wise testing result (ASPECT-03):
    * ``adjusted_pvalues`` — numpy array of shape (n_basis,), one p-value per basis
    * ``raw_pvalues``      — numpy array of shape (n_basis,), unadjusted p-values
    * ``basis_type``       — str identifying the projection basis
    * ``n_basis``          — int, number of projection basis functions
    * ``n_perm``           — int, number of permutations used

    The raw array is REDUCED to grounded DETECTION + LOCALISATION scalars (ASPECT-03,
    PITFALLS #8 — emitting a lone global scalar would mislead the LLM into treating
    local significance as global significance):
      Detection:    itp_min_adjusted_pvalue, itp_detected_at_0.05
      Localisation: itp_n_significant_0.05, itp_fraction_significant_0.05,
                    itp_first_significant_basis
    The raw ``adjusted_pvalues``/``raw_pvalues`` arrays are NEVER stored in the
    returned dict (breaks JSON serialisation + grounding invariant).

All returned values are native Python types (float, int, str, bool, None).
No NumPy scalars.  Two calls on the same input always return an equal,
JSON-serialisable dict.  No network, no RNG, no wall-clock dependency.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_float(raw: dict, key: str) -> "float | None":
    """Return raw[key] as a native float, or None if absent.

    Casts to ``float`` unconditionally so no NumPy scalar leaks into the
    output dict.
    """
    val = raw.get(key)
    return float(val) if val is not None else None


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------

def _build_inference_diagnostics(raw, **kwargs) -> dict:
    """Compute inference diagnostics from a caller-supplied fdars TestResult dict.

    Parameters
    ----------
    raw : dict
        Caller-supplied dict of fdars-computed inference results.
        Primary shape (TestResult): ``statistic``, ``p_value``, ``n_perm``.
        Secondary shape (ToleranceBand / SCB): ``lower``, ``upper``, ``center``,
        ``half_width`` — tolerated; significance fields set to ``None``.
        Each present value is cast to a native Python type; absent keys map
        to ``None`` in the output.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``str``, ``bool``, ``None``).  No NumPy scalars.  Fields:

        method (str):
            Always ``"inference"``.
        statistic (float or None):
            The fdars-computed test statistic.
        p_value (float or None):
            The fdars-computed permutation or asymptotic p-value.
        n_perm (int or None):
            Number of permutations used.  ``0`` denotes the asymptotic path
            (e.g. Hotelling T²) and is a legitimate value, NOT missing.
        significant_at_0.01 (bool or None):
            ``p_value < 0.01``; ``None`` when ``p_value`` is absent.
        significant_at_0.05 (bool or None):
            ``p_value < 0.05``; ``None`` when ``p_value`` is absent.
        significant_at_0.10 (bool or None):
            ``p_value < 0.10``; ``None`` when ``p_value`` is absent.
        strongest_significance_level (float or None):
            The smallest alpha at which the result is significant (0.01, 0.05,
            or 0.10), or ``None`` when not significant at any level or when
            ``p_value`` is absent.
        is_permutation_test (bool or None):
            ``True`` when ``n_perm > 0`` (permutation test path); ``False``
            when ``n_perm == 0`` (asymptotic path, e.g. Hotelling T²); ``None``
            when ``n_perm`` is absent.
        band_present (bool or None):
            ``True`` when the input is a ToleranceBand-shaped dict; absent from
            the dict in the TestResult path.
        half_width (float or None):
            Present only in the ToleranceBand path: scalar summary of the SCB
            half-width if available (takes the mean of the ``half_width`` array
            field when it is a sequence, or casts directly when a scalar).

    Raises
    ------
    ValueError
        When ``raw`` contains neither the TestResult keys (``statistic``,
        ``p_value``) nor the ToleranceBand keys (``half_width``, ``center``).
    """
    # Coerce to dict in case a result wrapper slipped through (harmless if
    # already a dict — the dispatcher guard covers this, but be defensive).
    if not isinstance(raw, dict):
        raw = dict(raw)

    # ------------------------------------------------------------------
    # Detect input shape
    # ------------------------------------------------------------------

    has_test_result_keys = "p_value" in raw or "statistic" in raw
    has_tolerance_band_keys = "half_width" in raw and "center" in raw
    # ITP result is uniquely identified by "adjusted_pvalues" — the vector-valued
    # per-basis p-value array.  TestResult uses "p_value"/"statistic" (scalar);
    # ToleranceBand uses "half_width"/"center".  These are disjoint fdars outputs.
    has_itp_keys = "adjusted_pvalues" in raw
    # Routing precedence: TestResult wins when both key sets are present (a dict
    # mixing p_value and half_width/center is pathological in practice — fdars
    # TestResult and ToleranceBand are disjoint outputs — so half_width is silently
    # ignored on the TestResult path rather than raising an ambiguity error.

    if not has_test_result_keys and not has_tolerance_band_keys and not has_itp_keys:
        raise ValueError(
            "build_diagnostics(method='inference'): raw dict contains neither "
            "TestResult keys ('statistic', 'p_value', 'n_perm') nor ToleranceBand "
            "keys ('half_width', 'center') nor ITP keys ('adjusted_pvalues').  "
            "Pass the dict returned by an fdars.inference function directly."
        )

    # ------------------------------------------------------------------
    # ITP (interval-wise testing procedure) path  — ASPECT-03
    # ------------------------------------------------------------------
    # Detected by the presence of "adjusted_pvalues" (a numpy array, shape (n_basis,))
    # which is unique to the fdars ITP result dict (TestResult uses scalar p_value,
    # ToleranceBand uses half_width/center).
    #
    # PITFALLS #8: emit DETECTION AND LOCALISATION scalars together.  A lone
    # itp_min_adjusted_pvalue would mislead the LLM into treating local
    # significance as global significance.
    # Detection:    itp_min_adjusted_pvalue, itp_detected_at_0.05
    # Localisation: itp_n_significant_0.05, itp_fraction_significant_0.05,
    #               itp_first_significant_basis

    if has_itp_keys and not has_test_result_keys:
        diag = {"method": "inference"}

        # Stable None-valued fields from the other paths (stable key set)
        diag["statistic"] = None
        diag["p_value"] = None
        diag["n_perm"] = None
        diag["significant_at_0.01"] = None
        diag["significant_at_0.05"] = None
        diag["significant_at_0.10"] = None
        diag["strongest_significance_level"] = None
        diag["is_permutation_test"] = None

        # Signal that this is an ITP result
        diag["itp_result_present"] = True

        # Reduce the vector-valued adjusted_pvalues array to native scalars.
        # Iterate over the array (any array-like); cast each element to float()
        # so no numpy scalar leaks into the output (grounding invariant: only
        # native Python types in the diagnostics dict).
        pvalues_list = [float(v) for v in raw["adjusted_pvalues"]]
        n_basis = int(raw["n_basis"]) if "n_basis" in raw else len(pvalues_list)
        n_perm_itp = int(raw["n_perm"]) if "n_perm" in raw else None

        diag["itp_n_basis"] = n_basis
        diag["itp_n_perm"] = n_perm_itp

        _ALPHA = 0.05  # fixed significance threshold (CONTEXT.md decision)

        # ---- DETECTION scalars ----
        if pvalues_list:
            itp_min_p = float(min(pvalues_list))
            diag["itp_min_adjusted_pvalue"] = itp_min_p
            diag["itp_detected_at_0.05"] = bool(itp_min_p < _ALPHA)
        else:
            diag["itp_min_adjusted_pvalue"] = None
            # WR-04: empty p-curve is "not applicable", not "tested, not detected".
            diag["itp_detected_at_0.05"] = None

        # ---- LOCALISATION scalars ----
        sig_indices = [i for i, p in enumerate(pvalues_list) if p < _ALPHA]
        n_sig = int(len(sig_indices))
        diag["itp_n_significant_0.05"] = n_sig

        # WR-02: derive the fraction denominator from the ACTUAL p-value array
        # length, not the raw["n_basis"] metadata — they can disagree, producing
        # a fraction inconsistent with the count (n_basis=0 + non-empty array gave
        # n_sig>0 alongside fraction=0.0). Emit None when nothing was tested.
        n_tested = len(pvalues_list)
        if n_tested > 0:
            diag["itp_fraction_significant_0.05"] = float(n_sig / n_tested)
        else:
            diag["itp_fraction_significant_0.05"] = None

        # First basis index with adjusted p < alpha, or None when none significant
        diag["itp_first_significant_basis"] = int(sig_indices[0]) if sig_indices else None

        return diag

    # ------------------------------------------------------------------
    # ToleranceBand / SCB path
    # ------------------------------------------------------------------

    if not has_test_result_keys and has_tolerance_band_keys:
        diag: dict = {"method": "inference"}
        diag["statistic"] = None
        diag["p_value"] = None
        diag["n_perm"] = None
        diag["significant_at_0.01"] = None
        diag["significant_at_0.05"] = None
        diag["significant_at_0.10"] = None
        diag["strongest_significance_level"] = None
        diag["is_permutation_test"] = None
        diag["band_present"] = True

        # Summarise half_width: take mean when a sequence, cast directly when scalar
        hw_raw = raw.get("half_width")
        if hw_raw is not None:
            try:
                # Sequence path: compute mean from plain-Python loop to avoid numpy dep
                vals = [float(v) for v in hw_raw]
                diag["half_width"] = float(sum(vals) / len(vals)) if vals else None
            except TypeError:
                # Scalar path
                diag["half_width"] = float(hw_raw)
        else:
            diag["half_width"] = None

        # Stable ITP fields — None in the ToleranceBand path
        diag["itp_result_present"] = False
        diag["itp_min_adjusted_pvalue"] = None
        diag["itp_detected_at_0.05"] = None
        diag["itp_n_significant_0.05"] = None
        diag["itp_fraction_significant_0.05"] = None
        diag["itp_first_significant_basis"] = None
        diag["itp_n_basis"] = None
        diag["itp_n_perm"] = None

        return diag

    # ------------------------------------------------------------------
    # TestResult path
    # ------------------------------------------------------------------

    diag = {"method": "inference"}

    statistic = _resolve_float(raw, "statistic")
    p_value = _resolve_float(raw, "p_value")

    # n_perm: int or None.  n_perm == 0 is legitimate (asymptotic test).
    n_perm_raw = raw.get("n_perm")
    n_perm = int(n_perm_raw) if n_perm_raw is not None else None

    diag["statistic"] = statistic
    diag["p_value"] = p_value
    diag["n_perm"] = n_perm

    # ------------------------------------------------------------------
    # Derived significance flags — p_value < alpha for alpha in {0.01, 0.05, 0.10}
    # All values come from the caller-supplied p_value: no new statistic computed.
    # ------------------------------------------------------------------

    if p_value is not None:
        diag["significant_at_0.01"] = bool(p_value < 0.01)
        diag["significant_at_0.05"] = bool(p_value < 0.05)
        diag["significant_at_0.10"] = bool(p_value < 0.10)

        # Strongest significance level: smallest alpha at which significant
        if p_value < 0.01:
            diag["strongest_significance_level"] = float(0.01)
        elif p_value < 0.05:
            diag["strongest_significance_level"] = float(0.05)
        elif p_value < 0.10:
            diag["strongest_significance_level"] = float(0.10)
        else:
            diag["strongest_significance_level"] = None
    else:
        diag["significant_at_0.01"] = None
        diag["significant_at_0.05"] = None
        diag["significant_at_0.10"] = None
        diag["strongest_significance_level"] = None

    # ------------------------------------------------------------------
    # is_permutation_test: True when n_perm > 0, False when n_perm == 0
    # (asymptotic path), None when n_perm absent.
    # ------------------------------------------------------------------

    if n_perm is not None:
        diag["is_permutation_test"] = bool(n_perm > 0)
    else:
        diag["is_permutation_test"] = None

    # Stable ITP fields — None in the TestResult path
    diag["itp_result_present"] = False
    diag["itp_min_adjusted_pvalue"] = None
    diag["itp_detected_at_0.05"] = None
    diag["itp_n_significant_0.05"] = None
    diag["itp_fraction_significant_0.05"] = None
    diag["itp_first_significant_basis"] = None
    diag["itp_n_basis"] = None
    diag["itp_n_perm"] = None

    return diag
