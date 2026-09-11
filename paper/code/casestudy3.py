"""Case Study 3: Functional Time Series Forecasting of Daily PM10 Air Pollution.

Runs a genuine functional-time-series forecast against fdars 0.13.0 on the
Graz PM10 dataset --- a *real* temporal sequence of curves (one per day), so
forecasting the next day's curve is a substantive task, not an illustration.

Pipeline:
1. Load pm10_graz.csv: 48 half-hourly PM10 concentrations (ug/m3) per day for
   182 consecutive days (Graz-Mitte, 2010-10-01 .. 2011-03-31).
2. Variance-stabilising square-root transform (per the dataset documentation).
3. Hold out the last H=7 days. Fit ftsm on the training days; forecast H days
   ahead with ftsm_forecast (GOTCHA: takes the raw data array, not the model
   dict) and back-transform (square) to ug/m3.
4. Validate: RMSE of the FTS forecast vs the held-out actual curves, compared
   against two baselines --- climatology (training mean curve) and persistence
   (last training day).

Writes two deterministic committed figures to paper/figures/:
- cs3_pm10_curves.pdf   -- training daily PM10 curves (grey) + FTS mean curve
- cs3_pm10_forecast.pdf -- (left) 1-day-ahead forecast vs actual vs climatology;
                           (right) RMSE by forecast horizon, FTS vs baselines

Data source: Graz-Mitte PM10, distributed with the R ``ftsa`` package (GPL-3);
the functional-time-series prediction benchmark of Aue, Norinho & Hormann
(2015, JASA).

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy3.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from paper_utils import fig, FDARS_COLORS, save_figure, data_path

import fdars

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# Number of days held out at the end of the record for out-of-sample validation.
_H = 7


def _rmse(a: np.ndarray, b: np.ndarray) -> float:
    """Root-mean-square error between two curves (ug/m3)."""
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main() -> None:
    """Run the Study-3 FTS forecast + validation and write two figures.

    ftsm / ftsm_forecast are deterministic (FPCA + VAR on scores, no stochastic
    step); the seed is a belt-and-suspenders guard for byte-stable output.
    """
    np.random.seed(42)

    # ------------------------------------------------------------------
    # Load PM10: CSV is (48 half-hours x 182 days); transpose so each row is
    # one day's 48-point diurnal PM10 curve.  Xpm.shape: (182, 48).
    # ------------------------------------------------------------------
    pm = pd.read_csv(data_path("pm10_graz.csv"), index_col=0)
    dates = list(pm.columns)                       # ISO day labels
    Xpm = pm.T.values.astype(np.float64)           # (182 days, 48 half-hours)
    ARG = pm.index.values.astype(np.float64)       # half-hour interval 1..48
    hours = (ARG - 1) * 0.5                         # hour of day 0.0 .. 23.5

    # ------------------------------------------------------------------
    # Train / held-out split (last _H days are out-of-sample).
    # Model in sqrt space (variance stabilisation), back-transform for errors.
    # ------------------------------------------------------------------
    train, actual = Xpm[:-_H], Xpm[-_H:]           # (175,48), (7,48)
    train_sqrt = np.sqrt(train)

    # FTS decomposition (mean curve + FPCs) for Figure 1.
    model = fdars.fts.ftsm(train_sqrt, ARG, ncomp=3)
    mean_curve = model["mean"] ** 2                 # back to ug/m3 for display

    # H-step-ahead forecast. GOTCHA: ftsm_forecast takes RAW data + argvals,
    # not the model dict; it re-fits ftsm internally.
    fc = fdars.fts.ftsm_forecast(train_sqrt, ARG, h=_H, ncomp=3)
    pred = fc["forecast"] ** 2                      # (7,48) ug/m3

    # Baselines: climatology (training mean curve) and persistence (last day).
    clim = train.mean(axis=0)
    persist = train[-1]

    fts_rmse = np.array([_rmse(pred[k], actual[k]) for k in range(_H)])
    clim_rmse = np.array([_rmse(clim, actual[k]) for k in range(_H)])
    per_rmse = np.array([_rmse(persist, actual[k]) for k in range(_H)])

    # Deterministic numbers consumed by casestudy3.tex prose.
    print("held-out days:", dates[-_H:])
    print("FTS   mean RMSE:", round(float(fts_rmse.mean()), 2))
    print("Clim  mean RMSE:", round(float(clim_rmse.mean()), 2))
    print("Persist mean RMSE:", round(float(per_rmse.mean()), 2))
    print("day+1 RMSE  FTS/Clim/Persist:",
          round(float(fts_rmse[0]), 2),
          round(float(clim_rmse[0]), 2),
          round(float(per_rmse[0]), 2))

    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: training daily PM10 curves (grey) + FTS mean curve.
    # Shows the diurnal structure (morning + evening traffic peaks) and the
    # day-to-day amplitude variation the FTS model summarises.
    # ------------------------------------------------------------------
    f1, ax1 = fig()
    for i in range(train.shape[0]):
        label = f"Daily curves (n={train.shape[0]})" if i == 0 else None
        ax1.plot(hours, train[i], color="#999999", linewidth=0.5,
                 alpha=0.35, label=label)
    ax1.plot(hours, mean_curve, color=FDARS_COLORS[0], linewidth=2.4,
             label="FTS mean", zorder=5)
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("PM10 concentration (ug/m$^3$)")
    ax1.set_xticks([0, 6, 12, 18, 24])
    ax1.set_title(
        "Graz PM10: daily diurnal curves and FTS mean\n"
        "(ftsm, 3 components; 2010-10-01 to 2011-03-24 training)"
    )
    ax1.legend(fontsize=8)
    save_figure(f1, _FIGURES_DIR / "cs3_pm10_curves.pdf")

    # ------------------------------------------------------------------
    # Figure 2: out-of-sample validation.
    # Left  : 1-day-ahead forecast vs actual vs climatology for the first
    #         held-out day.
    # Right : RMSE by forecast horizon (1..H days) for FTS and both baselines.
    # ------------------------------------------------------------------
    f2, (axL, axR) = fig(1, 2, figsize=(7.6, 3.6))

    axL.plot(hours, actual[0], color=FDARS_COLORS[3], linewidth=2.0,
             label="Actual")
    axL.plot(hours, pred[0], color=FDARS_COLORS[0], linewidth=2.0,
             linestyle="--", label="FTS forecast")
    axL.plot(hours, clim, color=FDARS_COLORS[6], linewidth=1.4,
             linestyle=":", label="Climatology")
    axL.set_xlabel("Hour of day")
    axL.set_ylabel("PM10 (ug/m$^3$)")
    axL.set_xticks([0, 6, 12, 18, 24])
    axL.set_title(f"1-day-ahead forecast ({dates[-_H]})")
    axL.legend(fontsize=8)

    horizon = np.arange(1, _H + 1)
    axR.plot(horizon, fts_rmse, color=FDARS_COLORS[0], marker="o",
             linewidth=1.8, label="FTS")
    axR.plot(horizon, clim_rmse, color=FDARS_COLORS[6], marker="s",
             linewidth=1.4, linestyle=":", label="Climatology")
    axR.plot(horizon, per_rmse, color=FDARS_COLORS[1], marker="^",
             linewidth=1.4, linestyle="--", label="Persistence")
    axR.set_xlabel("Forecast horizon (days ahead)")
    axR.set_ylabel("RMSE (ug/m$^3$)")
    axR.set_xticks(horizon)
    axR.set_title("Out-of-sample RMSE by horizon")
    axR.legend(fontsize=8)

    f2.suptitle(
        "FTS next-day PM10 forecast validation (Graz, 7 held-out days)",
        y=1.03,
    )
    save_figure(f2, _FIGURES_DIR / "cs3_pm10_forecast.pdf")


if __name__ == "__main__":
    main()
