"""fdars.advisor.aspects.spm — SPM Phase I diagnostics builder (ASPECT-05).

Contains ``_build_spm_diagnostics``, the HIGH-complexity advisor branch for
Statistical Process Monitoring results from ``fdars.spm.spm_phase1``.

This is the ONLY advisor builder that makes a live fdars call:
``fdars.spm.spe_moment_match_diagnostic(spe_values)`` — a deterministic, pure
moment computation with no RNG.  When ``fdars`` is unavailable (not compiled),
the call is guarded by a try/except that sets the kurtosis fields to ``None``
rather than raising.

Stochastic ARL (``arl0_t2``) is explicitly EXCLUDED — it breaks the offline
determinism guarantee (FUT-02).

Shared helper
-------------
``_eigenvalues_to_variance_cumulative`` is imported from ``_utils.py`` rather
than copied here.  ``spm_phase1`` returns eigenvalues directly (not singular
values), so the ``sv**2 / (n-1)`` step used in ``fpca.py`` is NOT needed.

Security (T-21-07, T-21-08 — ASVS V5)
---------------------------------------
``raw`` is treated as untrusted.  Every key access is guarded; missing keys
emit ``None`` rather than raising ``KeyError``.  The live call is wrapped in
``try/except`` so a misbehaving extension cannot propagate exceptions to the
caller.
"""

from __future__ import annotations

import numpy as np

from fdars.advisor.aspects._utils import _eigenvalues_to_variance_cumulative


def _build_spm_diagnostics(raw: dict, **kwargs) -> dict:
    """Compute SPM Phase I diagnostics from a ``spm_phase1`` result dict.

    Parameters
    ----------
    raw : dict
        Result dict from ``fdars.spm.spm_phase1``.  Expected keys:
        ``t2`` (ndarray n,), ``spe`` (ndarray n,), ``t2_limit`` (float),
        ``spe_limit`` (float), ``eigenvalues`` (ndarray ncomp,).
        Missing keys are tolerated: affected fields are set to ``None``.
    **kwargs
        Reserved for future per-method options; currently ignored.

    Returns
    -------
    dict
        Plain-Python dict.  All values are native Python types (``float``,
        ``int``, ``bool``, ``list``, ``str``, ``None``).  No NumPy scalars.
        ``json.dumps(result, sort_keys=True)`` succeeds without a custom
        encoder.

    Notes
    -----
    The ``spe_kurtosis_excess`` and ``spe_moment_match_adequate`` fields
    come from a live call to ``fdars.spm.spe_moment_match_diagnostic``.
    When ``fdars`` is not importable (no compiled extension), both are
    ``None``.  The key rename follows RESEARCH correction #8: the native
    Rust function returns key ``excess_kurtosis``; the builder emits it
    as ``spe_kurtosis_excess`` for clarity in LLM prompts.
    """
    diag: dict = {"method": "spm"}

    # -- Observation count + component count ---------------------------------
    t2_raw = raw.get("t2")
    t2_arr = np.asarray(t2_raw, dtype=float) if t2_raw is not None else None
    diag["n_obs"] = int(len(t2_arr)) if t2_arr is not None else None

    eigen_raw = raw.get("eigenvalues")
    eigen_arr = np.asarray(eigen_raw, dtype=float) if eigen_raw is not None else None
    diag["ncomp"] = int(len(eigen_arr)) if eigen_arr is not None else None

    # -- Control limits (direct scalar floats from spm_phase1) ---------------
    t2_limit_raw = raw.get("t2_limit")
    diag["t2_limit"] = float(t2_limit_raw) if t2_limit_raw is not None else None

    spe_limit_raw = raw.get("spe_limit")
    diag["spe_limit"] = float(spe_limit_raw) if spe_limit_raw is not None else None

    # -- T² summary statistics + exceedance rate ------------------------------
    if t2_arr is not None:
        diag["t2_max"] = float(np.max(t2_arr))
        diag["t2_mean"] = float(np.mean(t2_arr))
        if diag["t2_limit"] is not None:
            diag["t2_exceedance_rate"] = float(
                np.mean(t2_arr > float(diag["t2_limit"]))
            )
        else:
            diag["t2_exceedance_rate"] = None
    else:
        diag["t2_max"] = None
        diag["t2_mean"] = None
        diag["t2_exceedance_rate"] = None

    # -- SPE summary statistics + exceedance rate -----------------------------
    spe_raw = raw.get("spe")
    spe_arr = np.asarray(spe_raw, dtype=float) if spe_raw is not None else None

    if spe_arr is not None:
        diag["spe_max"] = float(np.max(spe_arr))
        diag["spe_mean"] = float(np.mean(spe_arr))
        if diag["spe_limit"] is not None:
            diag["spe_exceedance_rate"] = float(
                np.mean(spe_arr > float(diag["spe_limit"]))
            )
        else:
            diag["spe_exceedance_rate"] = None
    else:
        diag["spe_max"] = None
        diag["spe_mean"] = None
        diag["spe_exceedance_rate"] = None

    # -- Eigenvalues + cumulative variance via shared helper ------------------
    # SPM returns eigenvalues directly (not singular values), so no sv^2/(n-1)
    # scaling step is needed before calling the helper.
    if eigen_arr is not None:
        diag["eigenvalues"] = [float(v) for v in eigen_arr]
        diag["variance_explained_cumulative"] = _eigenvalues_to_variance_cumulative(
            eigen_arr
        )
    else:
        diag["eigenvalues"] = None
        diag["variance_explained_cumulative"] = None

    # -- Live fdars call: spe_moment_match_diagnostic (correction #8) ---------
    # The ONE live call in any builder.  Pure moment computation, no RNG —
    # deterministic and offline-safe.  Guard: "spe" must be present; wrap in
    # try/except so any ImportError or exception degrades to None gracefully
    # (T-21-07, T-21-08).
    spe_kurtosis_excess = None
    spe_moment_match_adequate = None

    if spe_arr is not None:
        try:
            from fdars import spm as _spm  # noqa: PLC0415
            mmd = _spm.spe_moment_match_diagnostic(
                np.asarray(spe_arr, dtype=float)
            )
            # Correction #8: native key is "excess_kurtosis"; emit as
            # "spe_kurtosis_excess" for LLM-context clarity.
            spe_kurtosis_excess = float(mmd["excess_kurtosis"])
            spe_moment_match_adequate = bool(mmd["is_adequate"])
        except Exception:  # noqa: BLE001 — ImportError, RuntimeError, etc.
            pass

    diag["spe_kurtosis_excess"] = spe_kurtosis_excess
    diag["spe_moment_match_adequate"] = spe_moment_match_adequate

    return diag
