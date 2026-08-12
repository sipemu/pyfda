"""fdars.advisor.aspects.smoothing — Smoothing diagnostics builder.

Contains ``_build_smoothing_diagnostics``, moved verbatim from
``advisor/__init__.py``.  Logic is unchanged; this is a pure file move.
"""

from __future__ import annotations

import numpy as np


def _build_smoothing_diagnostics(raw: dict, **kwargs) -> dict:
    """Compute smoothing diagnostics from a lambda_ GCV-curve result.

    Accepts either an already-computed result dict with keys
    ``lambda_values``, ``gcv``, ``edf`` (pass-through, offline) or raw
    data + argvals via kwargs for a live ``fdars.basis.smooth_basis_gcv``
    or ``fdars.basis.pspline_fit_gcv`` call.

    All values are cast to plain Python types.
    """
    diag: dict = {"method": "smoothing"}

    # Branch A-prime: single-fit pspline_fit_gcv result (no lambda sweep).
    # pspline_fit_gcv returns scalar keys ('gcv', 'edf', 'rss', 'aic', 'bic')
    # rather than a GCV curve — map to optimal_* scalars directly.
    if "gcv" in raw and "edf" in raw and "lambda_values" not in raw:
        diag["lambda_values"] = None
        diag["gcv_curve"] = None
        diag["edf"] = None
        diag["gcv_aic_approx"] = None
        diag["gcv_bic_approx"] = None
        diag["optimal_lambda"] = None
        diag["optimal_gcv"] = float(raw["gcv"])
        diag["optimal_edf"] = float(raw["edf"])
        # aic and bic from the fit are already scalar (store under gcv_aic_approx)
        if "aic" in raw and raw["aic"] is not None:
            try:
                diag["gcv_aic_approx"] = float(raw["aic"])
            except (TypeError, ValueError):
                pass
        if "bic" in raw and raw["bic"] is not None:
            try:
                diag["gcv_bic_approx"] = float(raw["bic"])
            except (TypeError, ValueError):
                pass
        return diag

    # Branch A: pre-computed smoothing GCV curve supplied in the result dict.
    if "lambda_values" in raw and "gcv" in raw:
        lambda_values = [float(v) for v in raw["lambda_values"]]
        gcv_values = [float(v) for v in raw["gcv"]]
        edf_values = (
            [float(v) for v in raw["edf"]] if "edf" in raw else None
        )

        if not gcv_values:
            diag["lambda_values"] = lambda_values
            diag["gcv_curve"] = gcv_values
            diag["edf"] = edf_values
            diag["gcv_aic_approx"] = None
            diag["gcv_bic_approx"] = None
            diag["optimal_lambda"] = None
            diag["optimal_gcv"] = None
            diag["optimal_edf"] = None
            return diag
        min_gcv_idx = int(np.argmin(gcv_values))
        optimal_lambda = lambda_values[min_gcv_idx]
        optimal_gcv = gcv_values[min_gcv_idx]
        optimal_edf = (
            edf_values[min_gcv_idx] if edf_values is not None else None
        )

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

        diag["lambda_values"] = lambda_values
        diag["gcv_curve"] = gcv_values
        diag["edf"] = edf_values
        diag["gcv_aic_approx"] = aic_values
        diag["gcv_bic_approx"] = bic_values
        diag["optimal_lambda"] = optimal_lambda
        diag["optimal_gcv"] = optimal_gcv
        diag["optimal_edf"] = optimal_edf
        return diag

    # Branch B: raw data via kwargs — call fdars.basis.pspline_fit_gcv.
    data_raw = kwargs.get("data")
    argvals_raw = kwargs.get("argvals")
    if data_raw is not None and argvals_raw is not None:
        from fdars import basis as _basis  # noqa: PLC0415

        data_arr = np.asarray(data_raw, dtype=float)
        av_arr = np.asarray(argvals_raw, dtype=float)
        gcv_result = _basis.pspline_fit_gcv(data_arr, av_arr)
        return _build_smoothing_diagnostics(gcv_result)

    # Fallback: no usable inputs.
    diag["lambda_values"] = None
    diag["gcv_curve"] = None
    diag["edf"] = None
    diag["gcv_aic_approx"] = None
    diag["gcv_bic_approx"] = None
    diag["optimal_lambda"] = None
    diag["optimal_gcv"] = None
    diag["optimal_edf"] = None
    return diag
