"""fdars.advisor.aspects.fts — FTS diagnostics builder.

Contains ``_build_fts_diagnostics``.  Accepts any fdars ``fts`` submodule
result produced by ``ftsm``, ``stationarity_test``, ``functional_acf``/
``functional_pacf``, ``dpca``, ``fplsr``, or ``ftsm_forecast``/
``ftsm_forecast_multistep``.

All values in the returned dict are native Python types (float, int, bool,
list, None).  No NumPy scalars.  Two calls on the same input always return
an equal, JSON-serialisable dict.

Discriminator hierarchy (tested in order so overlapping keys don't
mislabel):
  1. stationarity_test — unique key ``"n_perm"``
  2. functional_acf/pacf — unique key ``"upper_band"``
  3. dpca — unique key ``"filter_lag"``
  4. fplsr — ``"fitted" in raw and "forecast" in raw and "ncomp" in raw
              and forecast.shape[0] == 1``
  5. ftsm — unique key ``"ar_models"``
  6. ftsm_forecast — ``"forecast" in raw and "h" in raw``
"""

from __future__ import annotations

import numpy as np


def _build_fts_diagnostics(raw, **kwargs) -> dict:
    """Compute fts diagnostics from an fdars fts submodule result.

    Parameters
    ----------
    raw : dict
        Native fdars output dict from any of: ``ftsm``, ``stationarity_test``,
        ``functional_acf``, ``functional_pacf``, ``dpca``, ``fplsr``,
        ``ftsm_forecast``, ``ftsm_forecast_multistep``.
        Keys vary by function — all accesses are guarded.
    **kwargs
        Reserved for future per-method options (ignored).

    Returns
    -------
    dict
        Plain-Python dict with JSON-serialisable values (``float``, ``int``,
        ``bool``, ``list``, ``None``).  No NumPy scalars.  Fields:

        - method (str): always ``"fts"``
        - has_stationarity (bool): True when result is from ``stationarity_test``
        - stationarity_statistic (float or None): test statistic
        - stationarity_p_value (float or None): permutation p-value in [0,1]
        - n_perm (int or None): number of permutations used
        - has_acf (bool): True when result is from ``functional_acf``/``pacf``
        - n_lags (int or None): number of lags computed
        - acf_at_lag1 (float or None): first-lag autocorrelation
        - acf_decay (float or None): last-lag value (proxy for decay)
        - has_dpca (bool): True when result is from ``dpca``
        - dpca_ncomp (int or None): dynamic PCA components
        - n_freqs (int or None): frequency count
        - filter_lag (int or None): lag window
        - dpca_eigenvalues (list[float] or None): dynamic eigenvalue spectrum
        - has_fplsr (bool): True when result is from ``fplsr``
        - fplsr_ncomp (int or None): PLS components used
        - fplsr_fitted_rmse (float or None): leave-one-out fit quality
        - has_ftsm (bool): True when result is from ``ftsm``
        - ncomp (int or None): number of FTS components fitted
        - n_obs (int or None): number of observations (from scores)
        - n_points (int or None): evaluation grid size (from mean)
        - n_ar_models (int or None): number of AR models (== ncomp)
        - ar_max_order (int or None): maximum AR lag order across models
        - ar_sigma2_max (float or None): largest residual variance
        - fitted_rmse (float or None): overall reconstruction RMSE
        - has_forecast (bool): True when result is from ``ftsm_forecast``
        - h (int or None): forecast horizon
        - forecast_mean (float or None): average forecast value
    """
    diag: dict = {"method": "fts"}

    # ------------------------------------------------------------------
    # 1. stationarity_test — discriminator: "n_perm" in raw
    # Keys: statistic, p_value, n_perm
    # ------------------------------------------------------------------
    has_stationarity = "n_perm" in raw and "statistic" in raw and "p_value" in raw
    diag["has_stationarity"] = bool(has_stationarity)
    if has_stationarity:
        diag["stationarity_statistic"] = (
            float(raw["statistic"]) if "statistic" in raw else None
        )
        diag["stationarity_p_value"] = (
            float(raw["p_value"]) if "p_value" in raw else None
        )
        diag["n_perm"] = int(raw["n_perm"])
    else:
        diag["stationarity_statistic"] = None
        diag["stationarity_p_value"] = None
        diag["n_perm"] = None

    # ------------------------------------------------------------------
    # 2. functional_acf / functional_pacf — discriminator: "upper_band" in raw
    # Keys: lags (int64), acf, pacf, upper_band
    # ------------------------------------------------------------------
    has_acf = "acf" in raw and "upper_band" in raw
    diag["has_acf"] = bool(has_acf)
    if has_acf:
        lags_arr = np.asarray(raw["lags"])
        diag["n_lags"] = int(len(lags_arr))
        acf_arr = np.asarray(raw["acf"])
        if acf_arr.size > 0:
            diag["acf_at_lag1"] = float(acf_arr[0])
            diag["acf_decay"] = float(acf_arr[-1])
        else:
            diag["acf_at_lag1"] = None
            diag["acf_decay"] = None
    else:
        diag["n_lags"] = None
        diag["acf_at_lag1"] = None
        diag["acf_decay"] = None

    # ------------------------------------------------------------------
    # 3. dpca — discriminator: "filter_lag" in raw and "n_freqs" in raw
    # Keys: filters, scores, eigenvalues, n_freqs, filter_lag, ncomp, valid_range
    # ------------------------------------------------------------------
    has_dpca = "filter_lag" in raw and "n_freqs" in raw
    diag["has_dpca"] = bool(has_dpca)
    if has_dpca:
        diag["dpca_ncomp"] = int(raw["ncomp"])
        diag["n_freqs"] = int(raw["n_freqs"])
        diag["filter_lag"] = int(raw["filter_lag"])
        # eigenvalues is a list of 1-D arrays (one per component).
        # Summarise as the max eigenvalue per component (frequency peak).
        eigenvalues_raw = raw["eigenvalues"]
        diag["dpca_eigenvalues"] = [
            float(np.max(np.asarray(ev))) for ev in eigenvalues_raw
        ]
    else:
        diag["dpca_ncomp"] = None
        diag["n_freqs"] = None
        diag["filter_lag"] = None
        diag["dpca_eigenvalues"] = None

    # ------------------------------------------------------------------
    # 4. fplsr — discriminator: fitted + forecast + ncomp + forecast.shape[0] == 1
    # Keys: forecast (1, m), fitted (n-1, m), ncomp
    # Test fplsr BEFORE the bare forecast branch to avoid mislabeling.
    # ------------------------------------------------------------------
    _has_fplsr_keys = (
        "fitted" in raw
        and "forecast" in raw
        and "ncomp" in raw
    )
    if _has_fplsr_keys:
        _forecast_arr = np.asarray(raw["forecast"])
        _has_fplsr_shape = _forecast_arr.ndim == 2 and _forecast_arr.shape[0] == 1
    else:
        _has_fplsr_shape = False
    has_fplsr = _has_fplsr_keys and _has_fplsr_shape
    diag["has_fplsr"] = bool(has_fplsr)
    if has_fplsr:
        diag["fplsr_ncomp"] = int(raw["ncomp"])
        fitted_arr = np.asarray(raw["fitted"])
        diag["fplsr_fitted_rmse"] = float(
            np.sqrt(np.mean(fitted_arr ** 2))
        )
    else:
        diag["fplsr_ncomp"] = None
        diag["fplsr_fitted_rmse"] = None

    # ------------------------------------------------------------------
    # 5. ftsm — discriminator: "ar_models" in raw
    # Keys: mean (m,), rotation (m, ncomp), scores (n, ncomp), fitted (n, m),
    #       weights (m,), ncomp (int), ar_models (list of dicts)
    # ------------------------------------------------------------------
    has_ftsm = "ar_models" in raw
    diag["has_ftsm"] = bool(has_ftsm)
    if has_ftsm:
        diag["ncomp"] = int(raw["ncomp"])
        diag["n_obs"] = int(np.asarray(raw["scores"]).shape[0])
        diag["n_points"] = int(np.asarray(raw["mean"]).shape[0])
        ar_models = raw["ar_models"]
        diag["n_ar_models"] = int(len(ar_models))
        if ar_models:
            diag["ar_max_order"] = int(
                max(int(m["order"]) for m in ar_models)
            )
            diag["ar_sigma2_max"] = float(
                max(float(m["sigma2"]) for m in ar_models)
            )
        else:
            diag["ar_max_order"] = None
            diag["ar_sigma2_max"] = None
        fitted_arr = np.asarray(raw["fitted"])
        diag["fitted_rmse"] = float(np.sqrt(np.mean(fitted_arr ** 2)))
    else:
        diag["ncomp"] = None
        diag["n_obs"] = None
        diag["n_points"] = None
        diag["n_ar_models"] = None
        diag["ar_max_order"] = None
        diag["ar_sigma2_max"] = None
        diag["fitted_rmse"] = None

    # ------------------------------------------------------------------
    # 6. ftsm_forecast / ftsm_forecast_multistep — discriminator: "h" in raw
    # Keys: forecast (h, m), h (int)
    # Only reached when fplsr discriminator (step 4) was False.
    # ------------------------------------------------------------------
    has_forecast = "forecast" in raw and "h" in raw
    diag["has_forecast"] = bool(has_forecast)
    if has_forecast:
        diag["h"] = int(raw["h"])
        forecast_arr = np.asarray(raw["forecast"])
        diag["forecast_mean"] = float(np.mean(forecast_arr))
    else:
        diag["h"] = None
        diag["forecast_mean"] = None

    return diag
