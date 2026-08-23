"""fdars.advisor.aspects.fpca — FPCA diagnostics builder.

Contains ``_build_fpca_diagnostics``, moved verbatim from
``advisor/__init__.py``.  Logic is unchanged except that the
``cumulative_variance_explained`` computation now delegates to the shared
``_eigenvalues_to_variance_cumulative`` helper in ``_utils.py`` to avoid
duplicating the pattern across fpca and spm.
"""

from __future__ import annotations

import numpy as np

from fdars.advisor.aspects._utils import _eigenvalues_to_variance_cumulative


def _build_fpca_diagnostics(raw: dict) -> dict:
    """Compute FPCA-specific diagnostics from an fpca-style result dict.

    Accepts the raw dict from ``fdars.regression.fpca`` (keys ``scores``,
    ``singular_values``, ``rotation``, ``mean``) or from an
    ``fdars.results.FPCAResult`` (already unwrapped by the caller).

    Computes per-component eigenvalues, explained-variance ratio, cumulative
    variance explained, component count, and a deterministic phase-leakage
    indicator.  All values are cast to plain Python types for byte-identical
    repeats across runs.
    """
    diag: dict = {"method": "fpca"}

    sv_raw = raw.get("singular_values")
    scores_raw = raw.get("scores")

    if sv_raw is not None and scores_raw is not None:
        sv = np.asarray(sv_raw, dtype=float)
        scores = np.asarray(scores_raw, dtype=float)
        n_obs = int(scores.shape[0])
        n_comp = int(sv.shape[0])
        denom = max(n_obs - 1, 1)

        # Eigenvalues = singular_values^2 / (n-1), matching FPCAResult.explained_variance
        eigenvalues = (sv ** 2) / denom
        total_var = float(eigenvalues.sum())
        if total_var > 0.0:
            evr = eigenvalues / total_var
        else:
            evr = np.zeros_like(eigenvalues)

        # Delegate cumulative variance to the shared helper (reused by spm.py).
        cum_list = _eigenvalues_to_variance_cumulative(eigenvalues)

        diag["n_components"] = n_comp
        diag["n_obs"] = n_obs
        diag["eigenvalues"] = [float(v) for v in eigenvalues]
        diag["explained_variance_ratio"] = [float(v) for v in evr]
        diag["cumulative_variance_explained"] = cum_list
        diag["total_variance"] = total_var

        # Phase-leakage indicator: a deterministic scalar that signals when a
        # linear/vertical FPCA is absorbing phase variation.  The indicator is
        # based on the proportion of variance concentrated in higher components
        # relative to the leading component.  A high value (>= 0.5) suggests
        # that later components carry a disproportionate share of variance,
        # which may reflect phase variation leaking into the amplitude
        # decomposition rather than being handled by elastic alignment.
        # Guard: with only one component the indicator is 0.0 (no higher comps).
        if n_comp > 1:
            leading_var = float(evr[0])
            remaining_var = float(evr[1:].sum())
            # Fraction of total variance NOT explained by the first component.
            phase_leakage_indicator = float(remaining_var)
        else:
            phase_leakage_indicator = 0.0
        diag["phase_leakage_indicator"] = phase_leakage_indicator

        # Flag when leakage looks substantial (> 50 % of variance in higher comps).
        diag["phase_leakage_flagged"] = bool(phase_leakage_indicator > 0.5)
    else:
        diag["n_components"] = None
        diag["n_obs"] = None
        diag["eigenvalues"] = None
        diag["explained_variance_ratio"] = None
        diag["cumulative_variance_explained"] = None
        diag["total_variance"] = None
        diag["phase_leakage_indicator"] = None
        diag["phase_leakage_flagged"] = None

    # -- pace_fpca branch (ADV-05 Group B) -----------------------------------
    # Trigger: "eigenvalues" in raw — unique to pace_fpca.  The standard FPCA
    # result (from fdars.regression.fpca) carries "singular_values" (not
    # "eigenvalues"), so detection is unambiguous.
    # The pace_fpca eigenvalues are ALREADY SCALED (returned directly by
    # the PACE algorithm) — pass them directly to _eigenvalues_to_variance_cumulative
    # without any additional sv**2/(n-1) scaling.
    has_pace_fpca = "eigenvalues" in raw
    diag["has_pace_fpca"] = bool(has_pace_fpca)
    if has_pace_fpca:
        diag["pace_ncomp"] = int(raw["ncomp"]) if "ncomp" in raw else None
        diag["pace_sigma2"] = float(raw["sigma2"]) if "sigma2" in raw else None
        ev_raw = raw["eigenvalues"]
        cum_list = _eigenvalues_to_variance_cumulative(ev_raw)
        diag["pace_variance_explained_cumulative"] = cum_list
        diag["pace_variance_explained_first"] = float(cum_list[0]) if cum_list else None

        # ASPECT-01 — three additional grounded PACE scalars: ---------------------

        # 1. pace_noise_signal_ratio: sigma2 / total_signal_variance.
        #    total_signal_variance = sum of eigenvalues (fdars-computed).
        #    Guard: emit None when total variance is 0 (degenerate decomposition).
        pace_sigma2 = diag["pace_sigma2"]
        ev_arr = np.asarray(ev_raw, dtype=float)
        total_signal_variance = float(ev_arr.sum())
        if pace_sigma2 is not None and total_signal_variance > 0.0:
            diag["pace_noise_signal_ratio"] = float(pace_sigma2 / total_signal_variance)
        else:
            diag["pace_noise_signal_ratio"] = None

        # 2. pace_truncated_rank_flagged: True when ncomp < number of available
        #    eigenvalues, i.e. the decomposition was truncated below full rank.
        #    Derived only from fdars-computed ncomp and eigenvalue counts.
        n_eigenvalues = int(len(ev_arr))
        pace_ncomp = diag["pace_ncomp"]
        if pace_ncomp is not None:
            diag["pace_truncated_rank_flagged"] = bool(pace_ncomp < n_eigenvalues)
        else:
            diag["pace_truncated_rank_flagged"] = None

        # 3. pace_mean_prediction_band_width: mean over all (n, m) cells of
        #    (fitted_upper - fitted_lower).  Both are 2-D numpy arrays.
        #    Reduce to a single native float; emit None when either array absent.
        fl = raw.get("fitted_lower")
        fu = raw.get("fitted_upper")
        if fl is not None and fu is not None:
            fl_arr = np.asarray(fl, dtype=float)
            fu_arr = np.asarray(fu, dtype=float)
            diag["pace_mean_prediction_band_width"] = float((fu_arr - fl_arr).mean())
        else:
            diag["pace_mean_prediction_band_width"] = None

    else:
        diag["pace_ncomp"] = None
        diag["pace_sigma2"] = None
        diag["pace_variance_explained_cumulative"] = None
        diag["pace_variance_explained_first"] = None
        # ASPECT-01 extra scalars — None in the non-pace path (stable key set)
        diag["pace_noise_signal_ratio"] = None
        diag["pace_truncated_rank_flagged"] = None
        diag["pace_mean_prediction_band_width"] = None

    return diag
