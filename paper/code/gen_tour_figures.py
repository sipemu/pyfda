"""Capability-tour figure generation pipeline.

One ``tour_<family>()`` function per Capability-Tour subsection (paper Section 4).
Each visualises the *live* output of that method family's representative example
(the same validated call shapes captured in ``gen_snippets.py``), writing a
deterministic PDF to ``paper/figures/tour_<family>.pdf``.

Styling follows the matplotlib-skill aesthetic (tvhahn/matplotlib-skill) applied
with the fdars brand palette: whitegrid + full despine, dimgrey text/ticks,
subtle panel frames, framed white legends, metric boxes (see ``paper_utils``).

Run via::

    PYTHONPATH=scripts:paper/code python paper/code/gen_tour_figures.py

or through ``gen_figures.py`` (wired into ``main()`` so ``make paper`` and the
CI determinism gate cover these figures automatically).

Determinism (PIPE-02): every function seeds ``np.random.seed(42)`` before any
stochastic draw, and ``save_figure`` strips the PDF ``CreationDate`` so
consecutive runs are byte-identical within one environment.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import fdars
from fdars import Fdata

from paper_utils import (
    fig,
    FDARS_COLORS,
    save_figure,
    data_path,
    style_setup,
    clean_ax,
    brand_legend,
    metric_box,
    DIMGREY,
)

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# Neutral grey for supporting (non-primary) curves, per the skill's "grey is a
# color" principle.  FDARS_COLORS[6] is the brand grey.
_GREY = FDARS_COLORS[6]


def _growth() -> tuple[np.ndarray, np.ndarray]:
    """Load the Berkeley growth study as ``(X, ARG)`` — (93 obs x 31 ages)."""
    growth = pd.read_csv(data_path("growth.csv"), index_col=0)
    arg = growth.index.values.astype(float)
    x = growth.values.T.astype(np.float64)
    return x, arg


# Berkeley heights are sampled on only 31 ages (biannual after age 8), too coarse
# for a stable finite-difference velocity.  For the derivative-based analyses
# (alignment, warping) we smooth to B-spline coefficients and re-evaluate the fit
# on a dense age grid before differentiating, which resolves the pubertal spurt
# cleanly.  n_boys=39 (columns M01..M39), then 54 girls (F01..F54).
_DENSE_N = 120


def _growth_velocity_dense(n_basis: int = 12):
    """Return ``(dense_age, velocity, n_boys)`` on a dense grid.

    Smooth the Berkeley height curves with a GCV B-spline penalty, evaluate the
    fit on ``_DENSE_N`` equally spaced ages spanning the original range, then
    differentiate to growth-velocity curves.
    """
    X, ARG = _growth()
    sm = fdars.basis.smooth_basis_gcv(
        X, ARG, n_basis=n_basis, basis_type="bspline"
    )
    dense = np.linspace(float(ARG.min()), float(ARG.max()), _DENSE_N)
    fit = fdars.basis.basis_to_fdata_1d(
        sm["coefficients"], dense, n_basis, "bspline"
    )
    vel = Fdata(fit, argvals=dense).deriv().data
    return dense, vel, 39


def tour_represent() -> None:
    """4.1 Data Representation — raw growth curves with the sample mean."""
    np.random.seed(42)
    X, ARG = _growth()
    fd = Fdata(X, argvals=ARG)
    mean = fd.mean()

    f, ax = fig()
    for row in X:
        ax.plot(ARG, row, color=_GREY, alpha=0.28, linewidth=0.6)
    ax.plot(ARG, mean, color=FDARS_COLORS[0], linewidth=2.6, label="Sample mean")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title(f"Berkeley growth study: {X.shape[0]} height curves + mean")
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_represent.pdf")


def tour_basis() -> None:
    """4.2 Basis Representation and Smoothing — raw vs GCV-smoothed curves."""
    np.random.seed(42)
    X, ARG = _growth()
    sub = X[:5]
    sm = fdars.basis.smooth_basis_gcv(sub, ARG, n_basis=8, basis_type="bspline")
    fitted = sm["fitted"]

    f, ax = fig()
    for i in range(sub.shape[0]):
        col = FDARS_COLORS[i]
        ax.plot(ARG, sub[i], "o", color=col, markersize=2.8, alpha=0.55,
                label="Observed" if i == 0 else None)
        ax.plot(ARG, fitted[i], color=col, linewidth=1.8,
                label="GCV B-spline fit" if i == 0 else None)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title("B-spline smoothing (8 basis functions, GCV penalty)")
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_basis.pdf")


def tour_depth() -> None:
    """4.3 Depth and Outlier Detection — curves shaded by Fraiman--Muniz depth."""
    np.random.seed(42)
    X, ARG = _growth()
    fd = Fdata(X, argvals=ARG)
    depths = fd.depth(method="fraiman_muniz")
    med = int(np.argmax(depths))
    out = fdars.outliers.muod(X)
    outlier_idx = sorted(
        set(out["shape_outliers"])
        | set(out["amplitude_outliers"])
        | set(out["magnitude_outliers"])
    )

    d = depths.astype(float)
    dn = (d - d.min()) / (d.max() - d.min() + 1e-12)

    f, ax = fig()
    for i in range(X.shape[0]):
        if i in outlier_idx or i == med:
            continue
        ax.plot(ARG, X[i], color=FDARS_COLORS[0],
                alpha=0.10 + 0.55 * dn[i], linewidth=0.7)
    for j, i in enumerate(outlier_idx):
        ax.plot(ARG, X[i], color=FDARS_COLORS[3], linewidth=1.3, alpha=0.9,
                label="MUOD outlier" if j == 0 else None)
    ax.plot(ARG, X[med], color=FDARS_COLORS[1], linewidth=2.6,
            label="Deepest (median) curve")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title(
        f"Fraiman--Muniz depth shading; {len(outlier_idx)} MUOD outlier(s)"
    )
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_depth.pdf")


def tour_fpca() -> None:
    """4.4 Functional PCA — mean curve and the first two modes of variation."""
    np.random.seed(42)
    X, ARG = _growth()
    fd = Fdata(X, argvals=ARG)
    pc = fd.to_pc(n_comp=3)
    mean = pc["mean"]
    rot = pc["rotation"]
    sv = pc["singular_values"]
    n = X.shape[0]
    sd = sv / np.sqrt(max(n - 1, 1))
    prop = sv ** 2 / float(np.sum(sv ** 2))

    f, axes = fig(1, 2, figsize=(7.5, 3.6))
    for k, ax in enumerate(axes):
        pert = 2.0 * sd[k] * rot[:, k]
        ax.plot(ARG, mean, color=_GREY, linewidth=1.8, label="Mean")
        ax.plot(ARG, mean + pert, color=FDARS_COLORS[0], linewidth=1.4,
                linestyle="--", label="Mean + 2 SD")
        ax.plot(ARG, mean - pert, color=FDARS_COLORS[1], linewidth=1.4,
                linestyle=":", label="Mean - 2 SD")
        ax.set_title(r"$\bf{(%s)}$ " % chr(ord("a") + k)
                     + f"PC{k + 1} ({prop[k] * 100:.1f}% variance)",
                     loc="left", fontsize=11)
        ax.set_xlabel("Age (years)")
        clean_ax(ax, frame=True)
        if k == 0:
            ax.set_ylabel("Height (cm)")
            brand_legend(ax, fontsize=8)
    f.suptitle("FPCA modes of variation (Berkeley growth)", y=1.03,
               color=DIMGREY)
    save_figure(f, _FIGURES_DIR / "tour_fpca.pdf")


def tour_clustering() -> None:
    """4.5 Clustering — functional k-means partition with cluster centroids."""
    np.random.seed(42)
    X, ARG = _growth()
    km = fdars.clustering.kmeans_fd(X, ARG, k=3, seed=42)
    cluster = km["cluster"]
    centers = km["centers"]
    sizes = np.bincount(cluster)

    f, ax = fig()
    for c in range(centers.shape[0]):
        col = FDARS_COLORS[c]
        for i in np.where(cluster == c)[0]:
            ax.plot(ARG, X[i], color=col, alpha=0.22, linewidth=0.6)
        ax.plot(ARG, centers[c], color=col, linewidth=2.6,
                label=f"Cluster {c + 1} (n={sizes[c]})")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title("Functional k-means (k=3) with cluster centroids")
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_clustering.pdf")


def tour_classification() -> None:
    """4.6 Classification — per-class mean phoneme log-periodogram spectra."""
    np.random.seed(42)
    ph = pd.read_csv(data_path("phoneme.csv"), index_col=0)
    Xp = ph.values.astype(np.float64)
    ARG = np.arange(1, Xp.shape[1] + 1, dtype=np.float64)
    labels = ph.index.tolist()
    uniq = list(dict.fromkeys(labels))

    f, ax = fig()
    for ci, cls in enumerate(uniq):
        idx = [j for j, l in enumerate(labels) if l == cls]
        ax.plot(ARG, Xp[idx].mean(axis=0), color=FDARS_COLORS[ci],
                linewidth=1.8, label=cls)
    ax.set_xlabel("Frequency (log-periodogram index)")
    ax.set_ylabel("Mean log-amplitude")
    ax.set_title(f"Class-mean spectra for {len(uniq)} phonemes")
    clean_ax(ax, frame=True)
    brand_legend(ax, title="Phoneme", ncol=2, fontsize=8, title_fontsize=8)
    save_figure(f, _FIGURES_DIR / "tour_classification.pdf")


def tour_regression() -> None:
    """4.7 Regression — observed vs fitted fat content (scalar-on-function)."""
    np.random.seed(42)
    tec = pd.read_csv(data_path("tecator.csv"), index_col=0)
    Xt = tec.iloc[:, :100].values.astype(np.float64)
    yfat = tec["fat"].values.astype(np.float64)
    sof = fdars.regression.fregre_lm(Xt, yfat, n_comp=5)
    fitted = sof["fitted_values"]
    r2 = sof["r_squared"]
    rmse = float(np.sqrt(np.mean((yfat - fitted) ** 2)))

    lo = float(min(yfat.min(), fitted.min()))
    hi = float(max(yfat.max(), fitted.max()))
    f, ax = fig()
    ax.plot([lo, hi], [lo, hi], color=DIMGREY, linewidth=1.2,
            linestyle="--", label="Perfect fit", zorder=1)
    ax.scatter(yfat, fitted, color=FDARS_COLORS[0], s=18, alpha=0.75,
               edgecolors="none", zorder=3)
    ax.set_xlabel("Observed fat content (%)")
    ax.set_ylabel("Fitted fat content (%)")
    ax.set_title("Scalar-on-function regression (Tecator)")
    clean_ax(ax, frame=True)
    metric_box(ax, f"RMSE = {rmse:.2f}\n$R^2$ = {r2:.3f}", loc="upper left")
    brand_legend(ax, loc="lower right")
    save_figure(f, _FIGURES_DIR / "tour_regression.pdf")


def tour_fts() -> None:
    """4.8 Functional Time Series — daily PM10 curves and next-day forecasts."""
    np.random.seed(42)
    pm = pd.read_csv(data_path("pm10_graz.csv"), index_col=0)
    X = pm.T.values.astype(np.float64)
    ARG = pm.index.values.astype(np.float64)
    hours = (ARG - 1) * 0.5
    fc = fdars.fts.ftsm_forecast(np.sqrt(X), ARG, h=3, ncomp=3)
    forecast = fc["forecast"] ** 2

    f, ax = fig()
    for i in range(X.shape[0]):
        ax.plot(hours, X[i], color=_GREY, alpha=0.12, linewidth=0.5)
    for j in range(forecast.shape[0]):
        ax.plot(hours, forecast[j], color=FDARS_COLORS[j], linewidth=1.9,
                label=f"Forecast day+{j + 1}")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("PM10 (ug/m$^3$)")
    ax.set_xticks([0, 6, 12, 18, 24])
    ax.set_title(f"FTSM forecast of the next {fc['h']} daily PM10 curves (Graz)")
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_fts.pdf")


def tour_spm() -> None:
    """4.9 Statistical Process Monitoring — Hotelling T^2 control chart."""
    np.random.seed(42)
    X, ARG = _growth()
    p1 = fdars.spm.spm_phase1(X[:46], ARG, ncomp=3, alpha=0.05)
    mon = fdars.spm.spm_monitor(
        p1["mean"], p1["loadings"], p1["weights"],
        p1["eigenvalues"], p1["t2_limit"], p1["spe_limit"],
        X[46:], ARG,
    )
    t2 = mon["t2"]
    alarm = mon["t2_alarm"].astype(bool)
    limit = float(p1["t2_limit"])
    idx = np.arange(len(t2))

    f, ax = fig()
    ax.plot(idx, t2, color=FDARS_COLORS[0], linewidth=1.2, marker="o",
            markersize=3, label="$T^2$ statistic")
    ax.scatter(idx[alarm], t2[alarm], color=FDARS_COLORS[3], s=42, zorder=5,
               label="Out-of-control")
    ax.axhline(limit, color=DIMGREY, linestyle="--", linewidth=1.2,
               label=f"UCL = {limit:.2f}")
    ax.set_xlabel("Monitored curve index (Phase 2)")
    ax.set_ylabel("Hotelling $T^2$")
    ax.set_title(f"$T^2$ control chart: {int(alarm.sum())} alarm(s)")
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_spm.pdf")


def tour_tolerance() -> None:
    """4.10 Conformal and Tolerance Bands — 95% simultaneous tolerance band."""
    np.random.seed(42)
    X, ARG = _growth()
    tol = fdars.tolerance.fpca_tolerance_band(
        X, ncomp=3, nb=200, coverage=0.95, seed=42
    )

    f, ax = fig()
    for row in X:
        ax.plot(ARG, row, color=_GREY, alpha=0.22, linewidth=0.5)
    ax.fill_between(ARG, tol["lower"], tol["upper"], color=FDARS_COLORS[0],
                    alpha=0.18, label="95% tolerance band")
    ax.plot(ARG, tol["center"], color=FDARS_COLORS[0], linewidth=2.0,
            label="Centre curve")
    ax.plot(ARG, tol["upper"], color=FDARS_COLORS[0], linewidth=1.0, alpha=0.7)
    ax.plot(ARG, tol["lower"], color=FDARS_COLORS[0], linewidth=1.0, alpha=0.7)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title("Bootstrap FPCA 95% simultaneous tolerance band")
    clean_ax(ax, frame=True)
    brand_legend(ax)
    save_figure(f, _FIGURES_DIR / "tour_tolerance.pdf")


def tour_metric() -> None:
    """4.11 Metrics, Density, and Frechet Analysis — L2 distance heatmap."""
    np.random.seed(42)
    X, ARG = _growth()
    D = fdars.metric.lp_self_1d(X, ARG, p=2.0)

    f, ax = fig()
    im = ax.imshow(D, cmap="viridis", origin="lower", aspect="auto")
    # Heatmap: full despine, no grid, no panel frame (the cell grid is the edge).
    import seaborn as sns
    sns.despine(ax=ax, left=True, bottom=True, right=True, top=True)
    ax.grid(False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor=DIMGREY)
    ax.set_xlabel("Curve index")
    ax.set_ylabel("Curve index")
    ax.set_title(f"Pairwise $L^2$ distance matrix ({D.shape[0]} curves)")
    cbar = f.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("$L^2$ distance", color=DIMGREY)
    cbar.ax.tick_params(labelcolor=DIMGREY, length=0)
    cbar.outline.set_edgecolor(FDARS_COLORS[6])
    save_figure(f, _FIGURES_DIR / "tour_metric.pdf")


def tour_alignment() -> None:
    """4.12 Elastic Alignment — growth-velocity (pubertal-spurt) registration."""
    np.random.seed(42)
    dense, vel, n_boys = _growth_velocity_dense()
    girls_vel = vel[n_boys:]                 # 54 Berkeley girls, dense grid
    mask = dense >= 5.0
    Ar, Vr = dense[mask], girls_vel[:20, mask]
    res = fdars.alignment.karcher_mean(Vr, Ar, max_iter=50)
    aligned = res["aligned_data"]

    f, axes = fig(1, 2, figsize=(7.5, 3.6), sharey=True)
    for i in range(Vr.shape[0]):
        axes[0].plot(Ar, Vr[i], color=FDARS_COLORS[0], alpha=0.5, linewidth=0.9)
        axes[1].plot(Ar, aligned[i], color=FDARS_COLORS[2], alpha=0.5,
                     linewidth=0.9)
    axes[0].plot(Ar, Vr.mean(axis=0), color=FDARS_COLORS[3], linewidth=2.4,
                 label="Cross-sec. mean")
    axes[1].plot(Ar, res["mean"], color=FDARS_COLORS[3], linewidth=2.4,
                 label="Karcher mean")
    axes[0].set_title(r"$\bf{(a)}$ Before alignment", loc="left", fontsize=11)
    axes[1].set_title(r"$\bf{(b)}$ After elastic alignment", loc="left",
                      fontsize=11)
    for ax in axes:
        ax.set_xlabel("Age (years)")
        clean_ax(ax, frame=True)
    axes[0].set_ylabel("Growth velocity (cm/yr)")
    brand_legend(axes[0], fontsize=8)
    brand_legend(axes[1], fontsize=8)
    f.suptitle("Berkeley girls: growth-velocity spurt registration", y=1.03,
               color=DIMGREY)
    save_figure(f, _FIGURES_DIR / "tour_alignment.pdf")


def tour_warping() -> None:
    """4.12 Elastic Alignment (companion) — SRSF warping functions by sex.

    Registering all Berkeley children's growth-velocity curves to a common
    Karcher template returns one warping function gamma per child.  Coloured by
    sex, the gammas separate: girls' gammas lie below the identity (their
    developmental events are reached at an earlier age than the template) and
    boys' above --- the ~2-year-earlier maturation of girls expressed as pure
    phase variation, distinct from any amplitude difference.
    """
    np.random.seed(42)
    dense, vel, n_boys = _growth_velocity_dense()   # dense grid, all 93 children
    mask = dense >= 5.0
    Ar, V = dense[mask], vel[:, mask]
    res = fdars.alignment.karcher_mean(V, Ar, max_iter=50)
    gam = res["gammas"]                     # (93, len(Ar)) warping functions
    boys, girls = gam[:n_boys], gam[n_boys:]

    f, ax = fig()
    for g in boys:
        ax.plot(Ar, g, color=FDARS_COLORS[0], alpha=0.20, linewidth=0.6)
    for g in girls:
        ax.plot(Ar, g, color=FDARS_COLORS[1], alpha=0.20, linewidth=0.6)
    ax.plot(Ar, Ar, color=DIMGREY, linestyle="--", linewidth=1.2,
            label="Identity (no warp)", zorder=2)
    ax.plot(Ar, boys.mean(axis=0), color=FDARS_COLORS[0], linewidth=2.8,
            label=f"Boys mean (n={n_boys})", zorder=5)
    ax.plot(Ar, girls.mean(axis=0), color=FDARS_COLORS[1], linewidth=2.8,
            label=f"Girls mean (n={girls.shape[0]})", zorder=5)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel(r"Warped age $\gamma$(age)")
    ax.set_title("Elastic warping functions by sex (growth velocity)")
    clean_ax(ax, frame=True)
    brand_legend(ax, loc="upper left")
    save_figure(f, _FIGURES_DIR / "tour_warping.pdf")


def tour_advisor() -> None:
    """4.13 Grounded AI Advisor — FPCA scree diagnostic from build_diagnostics."""
    np.random.seed(42)
    X, ARG = _growth()
    fd = Fdata(X, argvals=ARG)
    pc = fd.to_pc(n_comp=3)
    diag = fdars.advisor.build_diagnostics(pc, "fpca", argvals=ARG)
    ratio = np.asarray(diag["explained_variance_ratio"], dtype=float)
    cum = np.asarray(diag["cumulative_variance_explained"], dtype=float)
    comps = np.arange(1, len(ratio) + 1)

    f, ax = fig()
    ax.bar(comps, ratio * 100, color=FDARS_COLORS[0], alpha=0.75,
           label="Per-component", zorder=2)
    ax.plot(comps, cum * 100, color=FDARS_COLORS[1], marker="o", linewidth=1.8,
            label="Cumulative", zorder=3)
    for x, y in zip(comps, cum * 100):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8, color=DIMGREY)
    ax.set_xticks(comps)
    ax.set_ylim(0, 108)
    ax.set_xlabel("Principal component")
    ax.set_ylabel("Variance explained (%)")
    ax.set_title("Advisor FPCA diagnostic: variance scree")
    # Bar chart: keep a light horizontal grid to read percentages.
    clean_ax(ax, grid=True, grid_axis="y")
    brand_legend(ax, loc="center right")
    save_figure(f, _FIGURES_DIR / "tour_advisor.pdf")


# Ordered registry — mirrors the Section 4 subsection order.
TOUR_FIGURES = [
    tour_represent,
    tour_basis,
    tour_depth,
    tour_fpca,
    tour_clustering,
    tour_classification,
    tour_regression,
    tour_fts,
    tour_spm,
    tour_tolerance,
    tour_metric,
    tour_alignment,
    tour_warping,
    tour_advisor,
]


def main() -> None:
    """Regenerate every capability-tour figure."""
    style_setup()
    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for func in TOUR_FIGURES:
        func()


if __name__ == "__main__":
    main()
