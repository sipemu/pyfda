"""Case Study 2: Registration and Scalar-on-Function Regression on Tecator Data.

Runs the validated Study-2 pipeline against fdars 0.12.0:
1. Elastic Karcher-mean registration (karcher_mean + align_to_target) on near-infrared
   meat spectra from the tecator dataset.
2. Scalar-on-function FPC regression (fregre_lm, 5 components) to predict fat content.
3. 5-fold cross-validated regression (FPCRegressor) to assess generalisation.

Writes two deterministic committed figures to paper/figures/:
- cs2_tecator_align.pdf  -- raw spectra + aligned spectra with Karcher mean highlighted
- cs2_tecator_fit.pdf    -- actual vs fitted fat content scatter with R^2 annotated

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy2.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from paper_utils import (
    fig, FDARS_COLORS, save_figure, data_path,
    style_setup, clean_ax, brand_legend, metric_box, DIMGREY,
)

import fdars
from fdars import Fdata
from fdars.sklearn._skeletons import FPCRegressor
from sklearn.model_selection import cross_val_score

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def main() -> None:
    """Run the Study-2 pipeline and write two deterministic figures.

    Seeds the RNG first (per Determinism Pinning Summary in 89-RESEARCH).
    karcher_mean and fregre_lm are deterministic (iterative / linear algebra);
    FPCRegressor with default KFold(5, shuffle=False) is also deterministic.

    Notes
    -----
    karcher_mean is called on a subset of 30 curves (Xt[:30]) for computational
    efficiency.  ``converged: False`` is expected and documented — max_iter=20 is
    reached before the 1e-4 tolerance threshold, but the aligned data are still
    valid and the registration is illustrative.  The km["converged"] flag is
    printed informationally; checking it as a hard requirement is not valid
    (Pitfall 4 in 89-RESEARCH).
    """
    np.random.seed(42)
    style_setup()

    # ------------------------------------------------------------------
    # Load tecator data (240 meat samples x 100 spectral channels, fat response)
    # ------------------------------------------------------------------
    tec = pd.read_csv(data_path("tecator.csv"), index_col=0)
    Xt = tec.iloc[:, :100].values.astype(np.float64)     # (240, 100) spectra
    yfat = tec["fat"].values.astype(np.float64)           # scalar response
    ARGt = np.arange(1, 101, dtype=np.float64)            # 100 spectral channels

    # ------------------------------------------------------------------
    # Step 1: Elastic Karcher-mean registration (subset for speed)
    # km["converged"] is False when max_iter=20 is reached (expected; not an error).
    # The aligned result is still valid — do not treat this as a failure condition.
    # ------------------------------------------------------------------
    km = fdars.alignment.karcher_mean(Xt[:30], ARGt, max_iter=20)
    # km keys: mean, mean_srsf, aligned_data, gammas, n_iter, converged
    print("karcher_mean converged:", km["converged"], "(max_iter=20; expected False)")

    # Align ALL 240 curves to the estimated Karcher mean
    aligned = fdars.alignment.align_to_target(Xt, km["mean"], ARGt)
    # aligned keys: aligned_data, gammas, distances
    Xa = aligned["aligned_data"]   # (240, 100)

    # ------------------------------------------------------------------
    # Step 2: Scalar-on-function FPC regression on 2nd-DERIVATIVE spectra.
    # Standard NIR preprocessing: smooth the absorbance curves with a B-spline
    # basis, then differentiate twice to remove baseline/scatter and expose the
    # fat absorption bands.  This substantially lifts R^2 over the raw spectra.
    # NOTE: fregre_lm uses n_comp (NOT n_components — different from FPCRegressor)
    # NOTE: result key is "fitted_values" (NOT "fitted" — unlike to_pc's "fitted")
    # ------------------------------------------------------------------
    sm = fdars.basis.smooth_basis_gcv(
        Xt, ARGt, n_basis=40, basis_type="bspline")["fitted"]
    d2 = Fdata(sm, argvals=ARGt).deriv().deriv().data   # 2nd-derivative spectra
    sof = fdars.regression.fregre_lm(d2, yfat, n_comp=15)
    r2_train = float(sof["r_squared"])
    fitted = sof["fitted_values"]   # (240,)
    print("train R2:", round(r2_train, 3))

    # ------------------------------------------------------------------
    # Step 3: FPCRegressor 5-fold cross-validation (on the same 2nd-deriv spectra)
    # NOTE: FPCRegressor uses n_components (NOT n_comp — sklearn convention)
    # ------------------------------------------------------------------
    cv = cross_val_score(FPCRegressor(n_components=15), d2, yfat, cv=5, scoring="r2")
    cv_mean = float(cv.mean())
    print("CV R2:", round(cv_mean, 3))
    print("CV fold scores:", [round(float(s), 3) for s in cv])

    # ------------------------------------------------------------------
    # Create output directory
    # ------------------------------------------------------------------
    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: raw spectra + aligned spectra + Karcher mean highlighted
    # Shows what elastic registration does to the spectral curves.
    # Use a representative subset (30 curves) to keep the plot readable.
    # ------------------------------------------------------------------
    n_show = 30
    mean_color = FDARS_COLORS[0]   # highlight the Karcher mean prominently
    aligned_color = FDARS_COLORS[1]

    f1, ax1 = fig()
    # Raw spectra (grey, low alpha)
    for i in range(n_show):
        ax1.plot(ARGt, Xt[i], color="0.75", linewidth=0.6, alpha=0.6,
                 label="Raw" if i == 0 else None)
    # Aligned spectra (coloured, low alpha)
    for i in range(n_show):
        ax1.plot(ARGt, Xa[i], color=aligned_color, linewidth=0.6, alpha=0.4,
                 label="Aligned" if i == 0 else None)
    # Karcher mean (bold, prominent)
    ax1.plot(ARGt, km["mean"], color=mean_color, linewidth=2.2, label="Karcher mean",
             zorder=5)
    ax1.set_xlabel("Spectral channel")
    ax1.set_ylabel("Absorbance")
    ax1.set_title(
        "Tecator near-infrared spectra: raw and elastically registered\n"
        "(30 curves shown; alignment iterations capped at 20)"
    )
    clean_ax(ax1, frame=True)
    brand_legend(ax1, fontsize=7)
    save_figure(f1, _FIGURES_DIR / "cs2_tecator_align.pdf")

    # ------------------------------------------------------------------
    # Figure 2: actual vs fitted fat content scatter with R^2 annotated
    # Demonstrates the quality of the scalar-on-function FPC regression.
    # ------------------------------------------------------------------
    f2, ax2 = fig()
    # Reference line y = x
    lo = float(min(yfat.min(), fitted.min()))
    hi = float(max(yfat.max(), fitted.max()))
    margin = (hi - lo) * 0.04
    ref_vals = np.array([lo - margin, hi + margin])
    ax2.plot(ref_vals, ref_vals, color=DIMGREY, linewidth=1.2,
             linestyle="--", label="Perfect fit ($y = x$)", zorder=1)
    ax2.scatter(yfat, fitted, color=FDARS_COLORS[0], s=14, alpha=0.7,
                edgecolors="none", label="Meat samples", zorder=3)
    ax2.set_xlabel("Actual fat content (%)")
    ax2.set_ylabel("Fitted fat content (%)")
    ax2.set_title("Scalar-on-function regression: actual vs fitted fat content")
    clean_ax(ax2, frame=True)
    metric_box(
        ax2,
        f"Training $R^2$ = {round(r2_train, 3)}\n"
        f"5-fold CV $R^2$ = {round(cv_mean, 3)}",
        loc="upper left",
    )
    brand_legend(ax2, fontsize=8, loc="lower right")
    save_figure(f2, _FIGURES_DIR / "cs2_tecator_fit.pdf")


if __name__ == "__main__":
    main()
