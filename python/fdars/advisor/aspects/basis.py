"""fdars.advisor.aspects.basis — Basis diagnostics builder.

Contains ``_build_basis_diagnostics``, moved verbatim from
``advisor/__init__.py``.  Logic is unchanged; this is a pure file move.
"""

from __future__ import annotations

import numpy as np


def _build_basis_diagnostics(raw: dict, **kwargs) -> dict:
    """Compute basis-selection diagnostics from an n_basis GCV-curve result.

    Accepts either an already-computed result dict with keys
    ``n_basis_values``, ``gcv``, ``edf`` (pass-through, offline) or, when
    raw data + argvals are provided via kwargs, calls
    ``fdars.basis.basis_nbasis_cv`` deterministically.

    All values are cast to plain Python types.
    """
    diag: dict = {"method": "basis"}

    # Branch A: pre-computed GCV curve supplied directly in the result dict.
    if "n_basis_values" in raw and "gcv" in raw:
        n_basis_values = [int(v) for v in raw["n_basis_values"]]
        gcv_values = [float(v) for v in raw["gcv"]]
        edf_values = (
            [float(v) for v in raw["edf"]] if "edf" in raw else None
        )

        # Optimal: index of minimum GCV value.
        if not gcv_values:
            diag["n_basis_values"] = n_basis_values
            diag["gcv_curve"] = gcv_values
            diag["edf"] = edf_values
            diag["gcv_aic_approx"] = None
            diag["gcv_bic_approx"] = None
            diag["optimal_n_basis"] = None
            diag["optimal_gcv"] = None
            diag["optimal_edf"] = None
            return diag
        min_gcv_idx = int(np.argmin(gcv_values))
        optimal_n_basis = n_basis_values[min_gcv_idx]
        optimal_gcv = gcv_values[min_gcv_idx]
        optimal_edf = (
            edf_values[min_gcv_idx] if edf_values is not None else None
        )

        # GCV-based AIC/BIC approximation from GCV + edf when edf is available.
        # These approximate AIC/BIC using log(GCV) rather than log(RSS/n); they
        # are labelled gcv_aic_approx/gcv_bic_approx to make the approximation
        # explicit (standard AIC/BIC use log(RSS/n), which differs from log(GCV)
        # by a (1 - edf/n)^2 denominator factor).
        # AIC_approx  ≈ n * log(GCV) + 2 * edf
        # BIC_approx  ≈ n * log(GCV) + log(n) * edf
        n_obs_raw = raw.get("n_obs")
        aic_values = None
        bic_values = None
        if edf_values is not None and n_obs_raw is not None:
            n_obs = float(n_obs_raw)
            aic_values = [
                float(n_obs * np.log(max(g, 1e-300)) + 2.0 * e)
                for g, e in zip(gcv_values, edf_values)
            ]
            bic_values = [
                float(n_obs * np.log(max(g, 1e-300)) + np.log(n_obs) * e)
                for g, e in zip(gcv_values, edf_values)
            ]

        diag["n_basis_values"] = n_basis_values
        diag["gcv_curve"] = gcv_values
        diag["edf"] = edf_values
        diag["gcv_aic_approx"] = aic_values
        diag["gcv_bic_approx"] = bic_values
        diag["optimal_n_basis"] = optimal_n_basis
        diag["optimal_gcv"] = optimal_gcv
        diag["optimal_edf"] = optimal_edf
        return diag

    # Branch B: raw data provided via kwargs — call fdars.basis.basis_nbasis_cv.
    data_raw = kwargs.get("data")
    argvals_raw = kwargs.get("argvals")
    if data_raw is not None and argvals_raw is not None:
        from fdars import basis as _basis  # noqa: PLC0415

        data_arr = np.asarray(data_raw, dtype=float)
        av_arr = np.asarray(argvals_raw, dtype=float)
        # basis_nbasis_cv returns a dict with gcv, n_basis_values, etc.
        cv_result = _basis.basis_nbasis_cv(data_arr, av_arr)
        return _build_basis_diagnostics(cv_result)

    # Fallback: no usable inputs.
    diag["n_basis_values"] = None
    diag["gcv_curve"] = None
    diag["edf"] = None
    diag["gcv_aic_approx"] = None
    diag["gcv_bic_approx"] = None
    diag["optimal_n_basis"] = None
    diag["optimal_gcv"] = None
    diag["optimal_edf"] = None
    return diag
