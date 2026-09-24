"""Case Study 3: Functional Time Series Forecasting of Daily PM10 Air Pollution.

Runs a genuine functional-time-series forecast against fdars 0.13.0 on the
Graz PM10 dataset --- a *real* temporal sequence of curves (one per day), so
forecasting the next day's curve is a substantive task, not an illustration.

Pipeline:
1. Load pm10_graz.csv: 48 half-hourly PM10 concentrations (ug/m3) per day for
   182 consecutive days (Graz-Mitte, 2010-10-01 .. 2011-03-31).
2. Variance-stabilising square-root transform, as applied to this dataset by
   Aue, Norinho & Hormann (2015).
3. Rolling-origin evaluation: for each of the last 30 forecast origins, fit on
   all days before the origin (expanding window) and forecast H=7 days ahead
   with ftsm_forecast (GOTCHA: takes the raw data array, not the model dict);
   back-transform (square) to ug/m3.
4. Validate: RMSE of each forecast curve against the actual curve, averaged over
   origins per horizon, compared against climatology (mean curve of the days
   before the origin) and persistence (the day before the origin).

Writes two deterministic committed figures to paper/figures/:
- cs3_pm10_curves.pdf   -- all daily PM10 curves (grey) + FTS mean curve
- cs3_pm10_forecast.pdf -- (left) 1-day-ahead forecast vs actual vs climatology
                           at the final origin; (right) mean RMSE by horizon over
                           the 30 rolling origins, FTS vs baselines (+/- 1 SE)

Data source: Graz-Mitte PM10, distributed with the R ``ftsa`` package (GPL-3);
the functional-time-series prediction benchmark of Aue, Norinho & Hormann
(2015, JASA).

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy3.py          # figures + numbers
    PYTHONPATH=scripts:paper/code python paper/code/casestudy3.py --check  # numbers drift gate

Every number quoted in paper/sections/casestudy3.tex is written to
paper/sections/cs3_numbers.tex (see cs_numbers.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from paper_utils import (
    fig, FDARS_COLORS, save_figure, data_path,
    style_setup, clean_ax, brand_legend, DIMGREY,
)

import fdars

from cs_numbers import emit, fmt

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# Forecast horizon (days) and number of rolling forecast origins.
_H = 7
_N_ORIGINS = 30
_NCOMP = 3
# Aue, Norinho & Hormann (2015) drop the New-Year week and analyse 175 curves.
_N_ANH = 175


def _rmse(a: np.ndarray, b: np.ndarray) -> float:
    """Root-mean-square error between two curves (ug/m3)."""
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main(check: bool = False) -> int:
    """Run the Study-3 FTS forecast + validation and write two figures.

    With ``check=True`` only the number macros are recomputed and compared with
    the committed file (no figures are written); returns 1 on drift.

    ftsm / ftsm_forecast are deterministic (FPCA followed by an independent
    univariate AR model per score series, fitted by Yule-Walker with AIC order
    selection; no stochastic step); the seed is a belt-and-suspenders guard.
    """
    np.random.seed(42)
    style_setup()

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
    # FTS decomposition of the full record (sqrt scale) for Figure 1.
    # ------------------------------------------------------------------
    n_days = Xpm.shape[0]
    model = fdars.fts.ftsm(np.sqrt(Xpm), ARG, ncomp=_NCOMP)
    mean_curve = model["mean"] ** 2                 # back to ug/m3 for display

    # ------------------------------------------------------------------
    # Rolling-origin evaluation.  Origin t = index of the first forecast day;
    # the model sees days [0, t) only (expanding window).  The last origin is
    # chosen so that all _H forecast days exist.
    # ------------------------------------------------------------------
    origins = list(range(n_days - _H - _N_ORIGINS + 1, n_days - _H + 1))
    fts_err = np.zeros((_N_ORIGINS, _H))
    clim_err = np.zeros((_N_ORIGINS, _H))
    per_err = np.zeros((_N_ORIGINS, _H))
    for i, t in enumerate(origins):
        past = Xpm[:t]
        fc = fdars.fts.ftsm_forecast(np.sqrt(past), ARG, h=_H, ncomp=_NCOMP)
        pred = fc["forecast"] ** 2                  # (H, 48) ug/m3
        clim, persist = past.mean(axis=0), past[-1]
        for k in range(_H):
            actual_k = Xpm[t + k]
            fts_err[i, k] = _rmse(pred[k], actual_k)
            clim_err[i, k] = _rmse(clim, actual_k)
            per_err[i, k] = _rmse(persist, actual_k)
    last_pred, last_clim = pred, clim               # final origin, for Fig. 2a
    last_t = origins[-1]

    def _se(e: np.ndarray) -> np.ndarray:
        return e.std(axis=0, ddof=1) / np.sqrt(e.shape[0])

    # Deterministic numbers consumed by casestudy3.tex prose.
    print("origins:", len(origins), "first forecast days:",
          dates[origins[0]], "..", dates[origins[-1]])
    print("mean RMSE over all horizons  FTS/Clim/Persist:",
          round(float(fts_err.mean()), 2), round(float(clim_err.mean()), 2),
          round(float(per_err.mean()), 2))
    print("1-day-ahead mean RMSE        FTS/Clim/Persist:",
          round(float(fts_err[:, 0].mean()), 2),
          round(float(clim_err[:, 0].mean()), 2),
          round(float(per_err[:, 0].mean()), 2))
    print("1-day-ahead wins: FTS beats climatology on",
          int((fts_err[:, 0] < clim_err[:, 0]).sum()), "/", len(origins),
          "origins; beats persistence on",
          int((fts_err[:, 0] < per_err[:, 0]).sum()), "/", len(origins))
    print("per-horizon FTS:", np.round(fts_err.mean(axis=0), 2).tolist())
    print("per-horizon Clim:", np.round(clim_err.mean(axis=0), 2).tolist())
    print("per-horizon Pers:", np.round(per_err.mean(axis=0), 2).tolist())

    # ------------------------------------------------------------------
    # Every number quoted in casestudy3.tex (letters-only macro names).
    # ------------------------------------------------------------------
    m_f, m_c, m_p = (e.mean(axis=0) for e in (fts_err, clim_err, per_err))
    macros = {
        "csThreeNDays": str(n_days),
        "csThreeNPoints": str(Xpm.shape[1]),
        "csThreeFirstDate": dates[0],
        "csThreeLastDate": dates[-1],
        "csThreeNAnh": str(_N_ANH),
        "csThreeNComp": str(_NCOMP),
        "csThreeNOrigins": str(len(origins)),
        "csThreeFirstOrigin": dates[origins[0]],
        "csThreeLastOrigin": dates[origins[-1]],
        "csThreeH": str(_H),
        "csThreeOneFts": fmt(m_f[0], 2),
        "csThreeOneClim": fmt(m_c[0], 2),
        "csThreeOnePers": fmt(m_p[0], 2),
        "csThreeWinsClim": str(int((fts_err[:, 0] < clim_err[:, 0]).sum())),
        "csThreeWinsPers": str(int((fts_err[:, 0] < per_err[:, 0]).sum())),
        "csThreeAllFts": fmt(fts_err.mean(), 2),
        "csThreeAllClim": fmt(clim_err.mean(), 2),
        "csThreeAllPers": fmt(per_err.mean(), 2),
        "csThreeGapOne": fmt(m_c[0] - m_f[0], 1),
        "csThreeGapLast": fmt(m_c[-1] - m_f[-1], 1),
    }
    status = emit("cs3_numbers.tex", "casestudy3.py", macros, check=check)
    if check:
        return status

    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: training daily PM10 curves (grey) + FTS mean curve.
    # Shows the diurnal structure (morning + evening traffic peaks) and the
    # day-to-day amplitude variation the FTS model summarises.
    # ------------------------------------------------------------------
    f1, ax1 = fig()
    for i in range(n_days):
        label = f"Daily curves (n={n_days})" if i == 0 else None
        ax1.plot(hours, Xpm[i], color=FDARS_COLORS[6], linewidth=0.5,
                 alpha=0.30, label=label)
    ax1.plot(hours, mean_curve, color=FDARS_COLORS[0], linewidth=2.4,
             label="FTS mean", zorder=5)
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("PM10 concentration (ug/m$^3$)")
    ax1.set_xticks([0, 6, 12, 18, 24])
    ax1.set_title(
        "Graz PM10: daily diurnal curves and FTS mean\n"
        "(ftsm, 3 components; 2010-10-01 to 2011-03-31)"
    )
    clean_ax(ax1, frame=True)
    brand_legend(ax1, fontsize=8)
    save_figure(f1, _FIGURES_DIR / "cs3_pm10_curves.pdf")

    # ------------------------------------------------------------------
    # Figure 2: out-of-sample validation.
    # Left  : 1-day-ahead forecast vs actual vs climatology for the first
    #         held-out day.
    # Right : RMSE by forecast horizon (1..H days) for FTS and both baselines.
    # ------------------------------------------------------------------
    f2, (axL, axR) = fig(1, 2, figsize=(7.6, 3.6))

    axL.plot(hours, Xpm[last_t], color=FDARS_COLORS[3], linewidth=2.0,
             label="Actual")
    axL.plot(hours, last_pred[0], color=FDARS_COLORS[0], linewidth=2.0,
             linestyle="--", label="FTS forecast")
    axL.plot(hours, last_clim, color=FDARS_COLORS[6], linewidth=1.4,
             linestyle=":", label="Climatology")
    axL.set_xlabel("Hour of day")
    axL.set_ylabel("PM10 (ug/m$^3$)")
    axL.set_xticks([0, 6, 12, 18, 24])
    axL.set_title(r"$\bf{(a)}$ " + f"1-day-ahead forecast ({dates[last_t]})",
                  loc="left", fontsize=11)
    clean_ax(axL, frame=True)
    brand_legend(axL, fontsize=8)

    horizon = np.arange(1, _H + 1)
    for err, color, marker, ls, name in (
            (fts_err, FDARS_COLORS[0], "o", "-", "FTS"),
            (clim_err, FDARS_COLORS[6], "s", ":", "Climatology"),
            (per_err, FDARS_COLORS[1], "^", "--", "Persistence")):
        m, se = err.mean(axis=0), _se(err)
        axR.plot(horizon, m, color=color, marker=marker, linewidth=1.6,
                 linestyle=ls, label=name)
        axR.fill_between(horizon, m - se, m + se, color=color, alpha=0.12,
                         linewidth=0)
    axR.set_xlabel("Forecast horizon (days ahead)")
    axR.set_ylabel("Mean RMSE (ug/m$^3$)")
    axR.set_xticks(horizon)
    axR.set_title(r"$\bf{(b)}$ " + f"RMSE by horizon ({len(origins)} origins)",
                  loc="left", fontsize=11)
    clean_ax(axR, frame=True)
    brand_legend(axR, fontsize=8)

    f2.suptitle(
        "FTS PM10 forecast validation (Graz, rolling-origin, "
        f"{len(origins)} origins, $\\pm$1 SE)",
        y=1.03, color=DIMGREY,
    )
    save_figure(f2, _FIGURES_DIR / "cs3_pm10_forecast.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv))
