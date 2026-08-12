"""fdars.advisor.aspects.fpca — FPCA diagnostics builder.

Contains ``_build_fpca_diagnostics``, moved verbatim from
``advisor/__init__.py``.  Logic is unchanged; this is a pure file move.
"""

from __future__ import annotations

import numpy as np


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

        cum_list = [float(v) for v in np.cumsum(evr)]

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

    return diag
