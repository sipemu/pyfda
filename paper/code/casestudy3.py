"""Case Study 3: Functional Time Series Forecasting on Canadian Weather Precipitation.

Runs the validated Study-3 FTS pipeline against fdars 0.12.0:
1. Load canadian_weather_precip.csv (365 days x 35 stations).
2. Transpose to (35, 365) — treat each station as a functional observation
   (a 365-point daily precipitation curve over the year).
3. Decompose with ftsm (3 components) to obtain the FTS mean curve.
4. Forecast 3 steps ahead with ftsm_forecast (GOTCHA: takes raw data array,
   not the model dict — Pitfall 3 from 89-RESEARCH.md).

Writes two deterministic committed figures to paper/figures/:
- cs3_precip_curves.pdf   -- 35 station curves (grey) + FTS mean (highlighted)
- cs3_precip_forecast.pdf -- 3 forecast curves alongside the observed mean

Note on sample size: 35 stations is a shallow sample for functional time-series
modelling (ftsm fits a VAR model on the FTS scores; VAR estimation with only 35
observations is illustrative, not statistically optimal).  This is acknowledged
honestly in casestudy3.tex.

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


def main() -> None:
    """Run the Study-3 FTS pipeline and write two deterministic figures.

    Seeds the RNG first (ftsm / ftsm_forecast are deterministic linear algebra
    + VAR fitting with no stochastic step; seed is a belt-and-suspenders guard).
    """
    np.random.seed(42)

    # ------------------------------------------------------------------
    # Load data: (365, 35) — rows = days 1..365, columns = weather stations
    # ------------------------------------------------------------------
    cw = pd.read_csv(data_path("canadian_weather_precip.csv"), index_col=0)
    # cw.shape: (365, 35)

    # Transpose: treat each station as one functional observation (a 365-day
    # daily precipitation profile).  Xfts.shape: (35, 365).
    Xfts = cw.T.values.astype(np.float64)   # (35 stations, 365 days)
    ARGd = np.arange(1, 366, dtype=np.float64)   # day 1..365

    # ------------------------------------------------------------------
    # FTS decomposition (ftsm) — gives the mean curve and FPC scores
    # GOTCHA: ftsm takes raw data (Xfts) + argvals, returns a model dict
    # ------------------------------------------------------------------
    model = fdars.fts.ftsm(Xfts, ARGd, ncomp=3)
    # model keys: mean, rotation, scores, fitted, weights, ncomp, ar_models
    # model["mean"].shape: (365,)
    # model["scores"].shape: (35, 3)

    # ------------------------------------------------------------------
    # FTS forecast: 3 steps ahead
    # GOTCHA (Pitfall 3): ftsm_forecast takes RAW DATA + argvals, NOT the
    # model dict.  Passing the model dict is wrong; always pass Xfts + ARGd.
    # Signature: ftsm_forecast(data, argvals, h=1, ncomp=3)
    # NOTE (IN-01): ftsm_forecast internally re-fits ftsm from scratch (Rust
    # API; fts_mod.rs).  The `model` dict above is used only for Figure 1
    # (mean curve); the two fits are byte-identical given the same inputs.
    # ------------------------------------------------------------------
    fc = fdars.fts.ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)
    # fc keys: forecast, h
    # fc["forecast"].shape: (3, 365)   fc["h"]: 3

    forecast = fc["forecast"]   # (3, 365)
    fc_preview = np.round(forecast[0, :5], 3)
    print("forecast shape:", forecast.shape)
    print("forecast[0, :5]:", fc_preview)

    # ------------------------------------------------------------------
    # Create output directory before first save
    # ------------------------------------------------------------------
    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: cs3_precip_curves.pdf
    # 35 observed station precipitation curves (grey) + FTS mean (highlighted)
    # Demonstrates the functional structure of the dataset.
    # ------------------------------------------------------------------
    mean_curve = model["mean"]   # (365,)

    f1, ax1 = fig()
    for i in range(Xfts.shape[0]):
        label = "Stations" if i == 0 else None
        ax1.plot(ARGd, Xfts[i], color="#999999", linewidth=0.6,
                 alpha=0.55, label=label)
    ax1.plot(ARGd, mean_curve, color=FDARS_COLORS[0], linewidth=2.2,
             label="FTS mean", zorder=5)
    ax1.set_xlabel("Day of year")
    ax1.set_ylabel("Daily precipitation (mm)")
    ax1.set_title(
        "Canadian weather precipitation: 35 station curves\n"
        "and FTS mean (ftsm, 3 components)"
    )
    ax1.legend(fontsize=7)
    save_figure(f1, _FIGURES_DIR / "cs3_precip_curves.pdf")

    # ------------------------------------------------------------------
    # Figure 2: cs3_precip_forecast.pdf
    # 3 forecast curves (h=1, 2, 3) alongside the observed mean
    # Demonstrates the 3-step-ahead FTS forecast.
    # ------------------------------------------------------------------
    forecast_colors = FDARS_COLORS[1:4]   # 3 distinct colours for h=1,2,3

    f2, ax2 = fig()
    ax2.plot(ARGd, mean_curve, color="#999999", linewidth=1.6,
             linestyle="--", label="Observed mean", zorder=2)
    for h_idx, col in enumerate(forecast_colors):
        ax2.plot(ARGd, forecast[h_idx], color=col, linewidth=1.4,
                 label=f"Forecast h={h_idx + 1}", zorder=3)
    ax2.set_xlabel("Day of year")
    ax2.set_ylabel("Daily precipitation (mm)")
    ax2.set_title(
        "FTS 3-step-ahead forecast: Canadian precipitation\n"
        f"(35 stations × 365 days, ftsm_forecast h=3, ncomp=3)"
    )
    ax2.legend(fontsize=7)
    save_figure(f2, _FIGURES_DIR / "cs3_precip_forecast.pdf")


if __name__ == "__main__":
    main()
