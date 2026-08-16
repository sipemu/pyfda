"""fdars.advisor.aspects.scoring — Scoring diagnostics builder.

Contains ``_build_scoring_diagnostics``.  Accepts a plain dict of
fdars-computed prediction-scoring metrics supplied by the CALLER (the
builder DOES NOT import fdars.scoring and DOES NOT recompute any metric).

The caller computes the 5 metrics via ``fdars.scoring.*`` functions and
passes them as the ``result`` dict to ``build_diagnostics``; this builder
then summarises / interprets those already-fdars-computed numbers.

Expected metric keys (long-form preferred; short aliases also accepted):

* ``functional_mae``   / ``mae``
* ``functional_mse``   / ``mse``
* ``functional_mape``  / ``mape``
* ``functional_msle``  / ``msle``
* ``functional_explained_variance`` / ``explained_variance``

All returned values are native Python types (float, int, str, bool,
None).  No NumPy scalars.  Two calls on the same input always return an
equal, JSON-serialisable dict.  No network, no RNG, no wall-clock dependency.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_metric(raw: dict, long_key: str, short_key: str) -> "float | None":
    """Return the metric value as a native float, or None if absent.

    Tries the long-form key first, then the short alias.  Casts to ``float``
    unconditionally so no NumPy scalar leaks into the output dict.
    """
    val = raw.get(long_key)
    if val is None:
        val = raw.get(short_key)
    return float(val) if val is not None else None


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------

def _build_scoring_diagnostics(raw, **kwargs) -> dict:
    """Compute scoring diagnostics from a caller-supplied fdars metrics dict.

    Parameters
    ----------
    raw : dict
        Caller-supplied dict of fdars-computed prediction-scoring metrics.
        Recognised keys: ``functional_mae`` / ``mae``,
        ``functional_mse`` / ``mse``, ``functional_mape`` / ``mape``,
        ``functional_msle`` / ``msle``,
        ``functional_explained_variance`` / ``explained_variance``.
        Each present value is cast to a native ``float``; absent keys map
        to ``None`` in the output.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``str``, ``bool``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"scoring"``
        - functional_mae (float or None): functional mean absolute error
        - functional_mse (float or None): functional mean squared error
        - functional_mape (float or None): functional mean absolute pct error
        - functional_msle (float or None): functional mean squared log error
        - functional_explained_variance (float or None): explained variance
        - largest_error_metric (str or None): name of the error metric with
          the largest value among the present error metrics (mae/mse/mape/msle);
          ``None`` when no error metric is present
        - explained_variance_band (str or None): ``"high"`` when
          ``explained_variance >= 0.9``, ``"moderate"`` when
          ``0.5 <= explained_variance < 0.9``, ``"low"`` when
          ``explained_variance < 0.5``; ``None`` when absent
    """
    # Coerce to dict in case a result wrapper slipped through (harmless if
    # already a dict — the dispatcher guard covers this, but be defensive).
    if not isinstance(raw, dict):
        raw = dict(raw)

    diag: dict = {"method": "scoring"}

    # -----------------------------------------------------------------------
    # Resolve each metric — attribute-first / dict-fallback idiom consistent
    # with represent.py.  Here raw is always a plain dict (scoring result),
    # so dict lookup is the only path; we still call _resolve_metric for
    # uniformity and to ensure float() casting on every value.
    # -----------------------------------------------------------------------
    mae = _resolve_metric(raw, "functional_mae", "mae")
    mse = _resolve_metric(raw, "functional_mse", "mse")
    mape = _resolve_metric(raw, "functional_mape", "mape")
    msle = _resolve_metric(raw, "functional_msle", "msle")
    ev = _resolve_metric(raw, "functional_explained_variance", "explained_variance")

    diag["functional_mae"] = mae
    diag["functional_mse"] = mse
    diag["functional_mape"] = mape
    diag["functional_msle"] = msle
    diag["functional_explained_variance"] = ev

    # -----------------------------------------------------------------------
    # Summary: which error metric is largest among the present error metrics?
    # Compares mae/mse/mape/msle by value; picks the name of the maximum.
    # All comparisons use caller-supplied fdars-computed values only — no
    # Python arithmetic is used to synthesise a new metric.
    # -----------------------------------------------------------------------
    error_candidates = {
        "functional_mae": mae,
        "functional_mse": mse,
        "functional_mape": mape,
        "functional_msle": msle,
    }
    present_errors = {k: v for k, v in error_candidates.items() if v is not None}
    if present_errors:
        largest_key = max(present_errors, key=lambda k: present_errors[k])
        diag["largest_error_metric"] = str(largest_key)
    else:
        diag["largest_error_metric"] = None

    # -----------------------------------------------------------------------
    # Summary: explained variance band
    # -----------------------------------------------------------------------
    if ev is not None:
        if ev >= 0.9:
            diag["explained_variance_band"] = "high"
        elif ev >= 0.5:
            diag["explained_variance_band"] = "moderate"
        else:
            diag["explained_variance_band"] = "low"
    else:
        diag["explained_variance_band"] = None

    return diag
