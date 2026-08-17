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

    if not has_test_result_keys and not has_tolerance_band_keys:
        raise ValueError(
            "build_diagnostics(method='inference'): raw dict contains neither "
            "TestResult keys ('statistic', 'p_value', 'n_perm') nor ToleranceBand "
            "keys ('half_width', 'center').  Pass the dict returned by an "
            "fdars.inference function directly."
        )

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

    return diag
