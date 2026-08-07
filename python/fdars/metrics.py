"""Scalar prediction-accuracy metrics (R ``pred.MAE``/``pred.MSE``/``pred.RMSE``/``pred.R2``).

These are lightweight NumPy helpers with no fdars-core counterpart; they mirror the
R ``pred.*`` family so model output can be scored with the same names.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "pred_mae",
    "pred_mse",
    "pred_rmse",
    "pred_r2",
    "prediction_metrics",
]


def _pair(y_true, y_pred):
    yt = np.asarray(y_true, dtype=float).ravel()
    yp = np.asarray(y_pred, dtype=float).ravel()
    if yt.shape != yp.shape:
        raise ValueError(f"shape mismatch: y_true {yt.shape} vs y_pred {yp.shape}")
    if yt.size == 0:
        raise ValueError("empty inputs")
    return yt, yp


def pred_mae(y_true, y_pred) -> float:
    """Mean absolute error (R ``pred.MAE``)."""
    yt, yp = _pair(y_true, y_pred)
    return float(np.mean(np.abs(yt - yp)))


def pred_mse(y_true, y_pred) -> float:
    """Mean squared error (R ``pred.MSE``)."""
    yt, yp = _pair(y_true, y_pred)
    return float(np.mean((yt - yp) ** 2))


def pred_rmse(y_true, y_pred) -> float:
    """Root mean squared error (R ``pred.RMSE``)."""
    return float(np.sqrt(pred_mse(y_true, y_pred)))


def pred_r2(y_true, y_pred) -> float:
    """Coefficient of determination R^2 (R ``pred.R2``).

    Returns ``nan`` when the response has zero variance.
    """
    yt, yp = _pair(y_true, y_pred)
    ss_tot = float(np.sum((yt - yt.mean()) ** 2))
    if ss_tot == 0.0:
        return float("nan")
    ss_res = float(np.sum((yt - yp) ** 2))
    return 1.0 - ss_res / ss_tot


def prediction_metrics(y_true, y_pred) -> dict:
    """All four ``pred.*`` metrics as a dict (``mae``, ``mse``, ``rmse``, ``r2``)."""
    return {
        "mae": pred_mae(y_true, y_pred),
        "mse": pred_mse(y_true, y_pred),
        "rmse": pred_rmse(y_true, y_pred),
        "r2": pred_r2(y_true, y_pred),
    }
