"""fdars.advisor.aspects.spm — SPM diagnostics builder (ASPECT-05 + ADV-01 Phase 72).

Contains ``_build_spm_diagnostics``.  Accepts three distinct input shapes:

1. **``spm_phase1`` result dict** — has ``t2``, ``spe``, ``t2_limit``,
   ``spe_limit``, ``eigenvalues`` keys (no ``eigenfunctions`` or ``scales``).
2. **``mfpca`` result dict** — has ``eigenfunctions``, ``scales``, ``scores``,
   ``eigenvalues``, ``means``, ``grid_sizes`` keys (discriminated by
   ``eigenfunctions + scales``; unique vs spm_phase1).
3. **``spe_multivariate`` naked array** — a 1-D numpy array returned directly
   by ``fdars.spm.spe_multivariate`` (no dict keys; handled first by
   ``hasattr(raw, "__array__")`` check).

The array path is checked FIRST so no ``raw.get()`` or ``"key" in raw`` call
is ever attempted on an array (T-72-08: STRIDE threat).

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

Security (T-21-07, T-21-08, T-72-08 — ASVS V5)
------------------------------------------------
``raw`` is treated as untrusted.  Every key access is guarded; missing keys
emit ``None`` rather than raising ``KeyError``.  The live call is wrapped in
``try/except`` so a misbehaving extension cannot propagate exceptions to the
caller.
"""

from __future__ import annotations

import numpy as np

from fdars.advisor.aspects._utils import _eigenvalues_to_variance_cumulative


def _build_spm_diagnostics(raw, **kwargs) -> dict:
    """Compute SPM diagnostics from a ``spm_phase1`` result dict, an ``mfpca``
    result dict, or a ``spe_multivariate`` naked numpy array.

    Parameters
    ----------
    raw : dict or numpy.ndarray
        One of:
        - ``spm_phase1`` result dict (keys: ``t2``, ``spe``, ``t2_limit``,
          ``spe_limit``, ``eigenvalues``).
        - ``mfpca`` result dict (keys: ``eigenfunctions``, ``scales``,
          ``scores``, ``eigenvalues``, ``means``, ``grid_sizes``).
        - ``spe_multivariate`` naked 1-D numpy array (shape n,).
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

    # ------------------------------------------------------------------
    # spe_multivariate branch (ADV-01 Phase 72) — MUST be first.
    # Trigger: raw is a naked numpy array (not a dict).
    # CRITICAL: this guard runs BEFORE any raw.get() or "key" in raw
    # accesses, so the dict methods are never called on an ndarray
    # (T-72-08 threat mitigation).
    # CONFIRMED: spe_multivariate returns PyArray1<f64> (naked array)
    # from src/spm_mod.rs:977+.
    # ------------------------------------------------------------------
    has_spe_multivariate = not isinstance(raw, dict) and hasattr(raw, "__array__")
    diag["has_spe_multivariate"] = bool(has_spe_multivariate)
    if has_spe_multivariate:
        a = np.asarray(raw, dtype=float)
        diag["spe_mv_n_obs"] = int(len(a))
        diag["spe_mv_max"] = float(np.max(a))
        diag["spe_mv_mean"] = float(np.mean(a))
        diag["spe_mv_all_nonneg"] = bool(float(np.min(a)) >= 0.0)
        # mfpca and spm_phase1 fields are absent for this input type
        diag["has_mfpca"] = False
        diag["mfpca_ncomp"] = None
        diag["mfpca_n_obs"] = None
        diag["mfpca_n_variables"] = None
        diag["mfpca_eigenvalues"] = None
        diag["mfpca_variance_explained_cumulative"] = None
        # spm_phase1 fields
        diag["n_obs"] = None
        diag["ncomp"] = None
        diag["t2_limit"] = None
        diag["spe_limit"] = None
        diag["t2_max"] = None
        diag["t2_mean"] = None
        diag["t2_exceedance_rate"] = None
        diag["spe_max"] = None
        diag["spe_mean"] = None
        diag["spe_exceedance_rate"] = None
        diag["eigenvalues"] = None
        diag["variance_explained_cumulative"] = None
        diag["spe_kurtosis_excess"] = None
        diag["spe_moment_match_adequate"] = None
        return diag

    # ------------------------------------------------------------------
    # From here raw is guaranteed to be a dict.
    # ------------------------------------------------------------------

    # Compute mfpca discriminator EARLY so spm_phase1 eigenvalue/ncomp
    # fields can be gated on "not has_mfpca" (WR-01: mfpca input must not
    # populate spm_phase1-specific ncomp/eigenvalues fields).
    # Trigger: "eigenfunctions" AND "scales" — unique to mfpca vs spm_phase1.
    has_mfpca = "eigenfunctions" in raw and "scales" in raw

    # -- Observation count + component count ---------------------------------
    t2_raw = raw.get("t2")
    t2_arr = np.asarray(t2_raw, dtype=float) if t2_raw is not None else None
    diag["n_obs"] = int(len(t2_arr)) if t2_arr is not None else None

    eigen_raw = raw.get("eigenvalues")
    eigen_arr = np.asarray(eigen_raw, dtype=float) if eigen_raw is not None else None
    # ncomp is a spm_phase1-specific field — None when input is mfpca (WR-01)
    diag["ncomp"] = int(len(eigen_arr)) if (eigen_arr is not None and not has_mfpca) else None

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
    # Gate on "not has_mfpca": mfpca carries its eigenvalue info under the
    # mfpca-specific keys (mfpca_eigenvalues, mfpca_variance_explained_cumulative)
    # only.  The spm_phase1 sentinel fields must be None for mfpca input (WR-01).
    if eigen_arr is not None and not has_mfpca:
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

    # ------------------------------------------------------------------
    # mfpca branch (ADV-01 Phase 72)
    # Trigger: "eigenfunctions" in raw AND "scales" in raw — unique to
    # mfpca. spm_phase1 has "eigenvalues" but NOT "eigenfunctions" or
    # "scales". CONFIRMED keys from src/spm_mod.rs:918-945.
    # has_mfpca already computed above (early, before spm_phase1 blocks).
    # ------------------------------------------------------------------
    diag["has_mfpca"] = bool(has_mfpca)
    if has_mfpca:
        eigen_raw = raw.get("eigenvalues")
        if eigen_raw is not None:
            mfpca_ev = np.asarray(eigen_raw, dtype=float)
            diag["mfpca_ncomp"] = int(mfpca_ev.shape[0])
            diag["mfpca_eigenvalues"] = [float(v) for v in mfpca_ev]
            diag["mfpca_variance_explained_cumulative"] = (
                _eigenvalues_to_variance_cumulative(mfpca_ev)
            )
        else:
            diag["mfpca_ncomp"] = None
            diag["mfpca_eigenvalues"] = None
            diag["mfpca_variance_explained_cumulative"] = None
        if "scores" in raw:
            scores_arr = np.asarray(raw["scores"])
            diag["mfpca_n_obs"] = int(scores_arr.shape[0])
        else:
            diag["mfpca_n_obs"] = None
        if "eigenfunctions" in raw:
            diag["mfpca_n_variables"] = int(len(raw["eigenfunctions"]))
        else:
            diag["mfpca_n_variables"] = None
    else:
        diag["mfpca_ncomp"] = None
        diag["mfpca_n_obs"] = None
        diag["mfpca_n_variables"] = None
        diag["mfpca_eigenvalues"] = None
        diag["mfpca_variance_explained_cumulative"] = None

    # spe_mv fields are None for dict-input paths (spm_phase1 or mfpca)
    diag["spe_mv_n_obs"] = None
    diag["spe_mv_max"] = None
    diag["spe_mv_mean"] = None
    diag["spe_mv_all_nonneg"] = None

    return diag
