"""Capability-tour figure generation pipeline.

One ``tour_<family>()`` function per Capability-Tour subsection (paper Section 4).
Each visualises the *live* output of that method family's representative example
(the same validated call shapes captured in ``gen_snippets.py``), writing a
deterministic PDF to ``paper/figures/tour_<family>.pdf``.

Run via::

    PYTHONPATH=scripts:paper/code python paper/code/gen_tour_figures.py

or through ``gen_figures.py`` (wired into ``main()`` so ``make paper`` and the
CI determinism gate cover these figures automatically).

Determinism rules (per PIPE-02): every function seeds ``np.random.seed(42)``
before any stochastic draw, and ``save_figure`` strips the PDF ``CreationDate``
so consecutive runs are byte-identical within one environment.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import fdars
from fdars import Fdata

from paper_utils import fig, FDARS_COLORS, save_figure, data_path

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def _growth() -> tuple[np.ndarray, np.ndarray]:
    """Load the Berkeley growth study as ``(X, ARG)`` — (93 obs x 31 ages)."""
    growth = pd.read_csv(data_path("growth.csv"), index_col=0)
    arg = growth.index.values.astype(float)
    x = growth.values.T.astype(np.float64)
    return x, arg


def tour_represent() -> None:
    """4.1 Data Representation — raw growth curves with the sample mean.

    Shows what an ``Fdata`` container holds: an (n_obs x n_points) matrix of
    height curves sharing one age grid, and the pointwise mean the container
    computes via ``fd.mean()``.
    """
    np.random.seed(42)
    X, ARG = _growth()
    fd = Fdata(X, argvals=ARG)
    mean = fd.mean()

    f, ax = fig()
    for row in X:
        ax.plot(ARG, row, color=FDARS_COLORS[6], alpha=0.28, linewidth=0.6)
    ax.plot(ARG, mean, color=FDARS_COLORS[0], linewidth=2.6, label="Sample mean")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title(f"Berkeley growth study: {X.shape[0]} height curves + mean")
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_represent.pdf")


def tour_basis() -> None:
    """4.2 Basis Representation and Smoothing — raw vs GCV-smoothed curves.

    Overlays five raw height curves with their B-spline basis reconstructions
    selected by generalised cross-validation (``smooth_basis_gcv``).
    """
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
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_basis.pdf")


def tour_depth() -> None:
    """4.3 Depth and Outlier Detection — curves shaded by Fraiman--Muniz depth.

    Darker curves are more central; the deepest (median) curve is highlighted,
    and MUOD-flagged shape/amplitude/magnitude outliers are drawn in red.
    """
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

    # Normalise depth to [0, 1] for alpha shading (deeper -> more opaque).
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
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_depth.pdf")


def tour_fpca() -> None:
    """4.4 Functional PCA — mean curve and the first two modes of variation.

    Each mode is the mean perturbed by +/- 2 SD along a principal eigenfunction
    (``rotation`` column scaled by its singular value), the standard FDA way to
    read what each component captures.
    """
    np.random.seed(42)
    X, ARG = _growth()
    fd = Fdata(X, argvals=ARG)
    pc = fd.to_pc(n_comp=3)
    mean = pc["mean"]
    rot = pc["rotation"]              # (n_points, 3)
    sv = pc["singular_values"]
    n = X.shape[0]
    # Per-component score SD ~ singular_value / sqrt(n-1); perturb mean by +/-2 SD.
    sd = sv / np.sqrt(max(n - 1, 1))
    prop = sv ** 2 / float(np.sum(sv ** 2))

    f, axes = fig(1, 2, figsize=(7.5, 3.6))
    for k, ax in enumerate(axes):
        pert = 2.0 * sd[k] * rot[:, k]
        ax.plot(ARG, mean, color=FDARS_COLORS[6], linewidth=1.8, label="Mean")
        ax.plot(ARG, mean + pert, color=FDARS_COLORS[0], linewidth=1.4,
                linestyle="--", label="Mean + 2 SD")
        ax.plot(ARG, mean - pert, color=FDARS_COLORS[1], linewidth=1.4,
                linestyle=":", label="Mean - 2 SD")
        ax.set_title(f"PC{k + 1} ({prop[k] * 100:.1f}% variance)")
        ax.set_xlabel("Age (years)")
        if k == 0:
            ax.set_ylabel("Height (cm)")
            ax.legend(fontsize=8)
    f.suptitle("FPCA modes of variation (Berkeley growth)", y=1.02)
    save_figure(f, _FIGURES_DIR / "tour_fpca.pdf")


def tour_clustering() -> None:
    """4.5 Clustering — functional k-means partition with cluster centroids.

    Curves are coloured by their k-means assignment (k=3, seed=42) and each
    cluster's centroid curve is overlaid in bold.
    """
    np.random.seed(42)
    X, ARG = _growth()
    km = fdars.clustering.kmeans_fd(X, ARG, k=3, seed=42)
    cluster = km["cluster"]
    centers = km["centers"]          # (3, n_points)
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
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_clustering.pdf")


def tour_classification() -> None:
    """4.6 Classification — per-class mean phoneme log-periodogram spectra.

    The FPCA-kNN classifier separates phoneme classes; this plot shows why it
    can: the class-mean spectra are visibly distinct across the frequency band.
    """
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
    ax.legend(title="Phoneme", ncol=2, fontsize=8, title_fontsize=8)
    save_figure(f, _FIGURES_DIR / "tour_classification.pdf")


def tour_regression() -> None:
    """4.7 Regression — observed vs fitted fat content (scalar-on-function).

    ``fregre_lm`` regresses fat on the 100-channel Tecator absorbance curves via
    FPCA projection; the scatter shows fitted vs observed with the live R^2.
    """
    np.random.seed(42)
    tec = pd.read_csv(data_path("tecator.csv"), index_col=0)
    Xt = tec.iloc[:, :100].values.astype(np.float64)
    yfat = tec["fat"].values.astype(np.float64)
    sof = fdars.regression.fregre_lm(Xt, yfat, n_comp=5)
    fitted = sof["fitted_values"]
    r2 = sof["r_squared"]

    lo = float(min(yfat.min(), fitted.min()))
    hi = float(max(yfat.max(), fitted.max()))
    f, ax = fig()
    ax.plot([lo, hi], [lo, hi], color=FDARS_COLORS[6], linewidth=1.2,
            linestyle="--", label="Perfect fit")
    ax.scatter(yfat, fitted, color=FDARS_COLORS[0], s=14, alpha=0.7)
    ax.set_xlabel("Observed fat content (%)")
    ax.set_ylabel("Fitted fat content (%)")
    ax.set_title(f"Scalar-on-function regression (Tecator), $R^2$ = {r2:.3f}")
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_regression.pdf")


def tour_fts() -> None:
    """4.8 Functional Time Series — input curves and FTSM forecast curves.

    ``ftsm_forecast`` projects the input curve sequence onto its leading
    components and forecasts the next ``h`` curves; the forecasts are overlaid
    in bold over the (light) historical curves.
    """
    np.random.seed(42)
    cw = pd.read_csv(data_path("canadian_weather.csv"), index_col=0)
    Xfts = cw.T.values.astype(np.float64)
    ARGd = np.arange(365, dtype=np.float64) + 1.0
    fc = fdars.fts.ftsm_forecast(Xfts, ARGd, h=3, ncomp=3)
    forecast = fc["forecast"]        # (3, 365)

    f, ax = fig()
    for i in range(Xfts.shape[0]):
        ax.plot(ARGd, Xfts[i], color=FDARS_COLORS[6], alpha=0.18, linewidth=0.5)
    for j in range(forecast.shape[0]):
        ax.plot(ARGd, forecast[j], color=FDARS_COLORS[j], linewidth=1.8,
                label=f"Forecast h={j + 1}")
    ax.set_xlabel("Day of year")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title(f"FTSM forecast of the next {fc['h']} curves (3 components)")
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_fts.pdf")


def tour_spm() -> None:
    """4.9 Statistical Process Monitoring — Hotelling T^2 control chart.

    Phase-1 estimates in-control variation on the first half of the curves;
    Phase-2 monitors the rest. The T^2 statistic per monitored curve is plotted
    against its control limit, with out-of-control points flagged.
    """
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
    ax.axhline(limit, color=FDARS_COLORS[3], linestyle="--", linewidth=1.2,
               label=f"UCL = {limit:.2f}")
    ax.set_xlabel("Monitored curve index (Phase 2)")
    ax.set_ylabel("Hotelling $T^2$")
    ax.set_title(f"$T^2$ control chart: {int(alarm.sum())} alarm(s)")
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_spm.pdf")


def tour_tolerance() -> None:
    """4.10 Conformal and Tolerance Bands — 95% simultaneous tolerance band.

    ``fpca_tolerance_band`` bootstraps an FPCA model to build a band expected to
    contain a target fraction of curves; the shaded band is drawn over the data.
    """
    np.random.seed(42)
    X, ARG = _growth()
    tol = fdars.tolerance.fpca_tolerance_band(
        X, ncomp=3, nb=200, coverage=0.95, seed=42
    )

    f, ax = fig()
    for row in X:
        ax.plot(ARG, row, color=FDARS_COLORS[6], alpha=0.22, linewidth=0.5)
    ax.fill_between(ARG, tol["lower"], tol["upper"], color=FDARS_COLORS[0],
                    alpha=0.18, label="95% tolerance band")
    ax.plot(ARG, tol["center"], color=FDARS_COLORS[0], linewidth=2.0,
            label="Centre curve")
    ax.plot(ARG, tol["upper"], color=FDARS_COLORS[0], linewidth=1.0, alpha=0.7)
    ax.plot(ARG, tol["lower"], color=FDARS_COLORS[0], linewidth=1.0, alpha=0.7)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Height (cm)")
    ax.set_title("Bootstrap FPCA 95% simultaneous tolerance band")
    ax.legend()
    save_figure(f, _FIGURES_DIR / "tour_tolerance.pdf")


def tour_metric() -> None:
    """4.11 Metrics, Density, and Frechet Analysis — L2 distance heatmap.

    ``lp_self_1d`` computes the pairwise $L^2$ distance matrix over the growth
    curves; the heatmap exposes the block structure of similar curves.
    """
    np.random.seed(42)
    X, ARG = _growth()
    D = fdars.metric.lp_self_1d(X, ARG, p=2.0)

    f, ax = fig()
    im = ax.imshow(D, cmap="viridis", origin="lower", aspect="auto")
    ax.grid(False)
    ax.set_xlabel("Curve index")
    ax.set_ylabel("Curve index")
    ax.set_title(f"Pairwise $L^2$ distance matrix ({D.shape[0]} curves)")
    cbar = f.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("$L^2$ distance")
    save_figure(f, _FIGURES_DIR / "tour_metric.pdf")


def tour_alignment() -> None:
    """4.12 Elastic Alignment — curves before and after Karcher-mean warping.

    ``karcher_mean`` separates amplitude from phase via SRSF registration; the
    two panels show the raw curves and their phase-aligned counterparts.
    """
    np.random.seed(42)
    X, ARG = _growth()
    sub = X[:10]
    res = fdars.alignment.karcher_mean(sub, ARG)
    aligned = res["aligned_data"]    # (10, n_points)

    f, axes = fig(1, 2, figsize=(7.5, 3.6), sharey=True)
    for i in range(sub.shape[0]):
        axes[0].plot(ARG, sub[i], color=FDARS_COLORS[0], alpha=0.6, linewidth=0.9)
        axes[1].plot(ARG, aligned[i], color=FDARS_COLORS[2], alpha=0.6,
                     linewidth=0.9)
    axes[0].plot(ARG, res["mean"], color=FDARS_COLORS[3], linewidth=2.2,
                 label="Karcher mean")
    axes[1].plot(ARG, res["mean"], color=FDARS_COLORS[3], linewidth=2.2)
    axes[0].set_title("Before alignment")
    axes[1].set_title("After elastic alignment")
    for ax in axes:
        ax.set_xlabel("Age (years)")
    axes[0].set_ylabel("Height (cm)")
    axes[0].legend(fontsize=8)
    save_figure(f, _FIGURES_DIR / "tour_alignment.pdf")


def tour_advisor() -> None:
    """4.13 Grounded AI Advisor — FPCA scree diagnostic from build_diagnostics.

    The offline ``build_diagnostics`` step returns the per-component and
    cumulative variance the advisor reasons over; this scree plot is exactly
    what grounds its (LLM-free) component-count guidance.
    """
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
           label="Per-component")
    ax.plot(comps, cum * 100, color=FDARS_COLORS[1], marker="o", linewidth=1.8,
            label="Cumulative")
    for x, y in zip(comps, cum * 100):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=8)
    ax.set_xticks(comps)
    ax.set_xlabel("Principal component")
    ax.set_ylabel("Variance explained (%)")
    ax.set_title("Advisor FPCA diagnostic: variance scree")
    ax.legend()
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
    tour_advisor,
]


def main() -> None:
    """Regenerate every capability-tour figure."""
    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for func in TOUR_FIGURES:
        func()


if __name__ == "__main__":
    main()
