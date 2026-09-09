"""Case Study 1: Smoothing, FPCA, and Classification on Phoneme Data.

Runs the validated Study-1 pipeline against fdars 0.12.0:
1. GCV B-spline smoothing of log-periodogram spectra.
2. FPCA (4 components) over all 400 observations.
3. 5-fold cross-validated classification (FPCATransformer + FPCLDAClassifier).

Writes two deterministic committed figures to paper/figures/:
- cs1_phoneme_smooth.pdf  -- raw spectra + smoothed curves per class
- cs1_phoneme_fpca.pdf    -- FPCA scores scatter (PC1 vs PC2) colour-coded by class

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy1.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from paper_utils import fig, FDARS_COLORS, save_figure, data_path

import fdars
from fdars.sklearn._skeletons import FPCATransformer, FPCLDAClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def main() -> None:
    """Run the Study-1 pipeline and write two deterministic figures.

    Seeds the RNG first (per Determinism Pinning Summary in 89-RESEARCH).
    FPCATransformer, FPCLDAClassifier, and KFold(5, shuffle=False) are
    all deterministic; no additional random_state arguments are required.
    """
    np.random.seed(42)

    # ------------------------------------------------------------------
    # Load phoneme data (400 obs x 256 frequency points, 5 balanced classes)
    # ------------------------------------------------------------------
    ph = pd.read_csv(data_path("phoneme.csv"), index_col=0)
    X = ph.values.astype(np.float64)              # (400, 256)
    ARG = np.arange(1, 257, dtype=np.float64)     # frequency points 1..256

    # ------------------------------------------------------------------
    # Smooth a representative subset with B-spline GCV (n_basis=15)
    # Select 4 rows PER CLASS by actual class membership (not positional
    # block): rows 0-19 in phoneme.csv are NOT sorted class-blocks.
    # ------------------------------------------------------------------
    uniq_pre = sorted(set(ph.index.tolist()))   # pre-compute for smooth selection
    class_rows_pre = {
        cls: [j for j, l in enumerate(ph.index.tolist()) if l == cls]
        for cls in uniq_pre
    }
    # First 4 row indices per class, in sorted class order (aa, ao, dcl, iy, sh)
    selected = [
        idx
        for cls in uniq_pre
        for idx in class_rows_pre[cls][:4]
    ]   # 20 indices total (4 per class × 5 classes)
    sm = fdars.basis.smooth_basis_gcv(X[selected], ARG, n_basis=15, basis_type="bspline")
    # sm["fitted"].shape: (20, 256) — rows 0-3 = aa, 4-7 = ao, 8-11 = dcl, 12-15 = iy, 16-19 = sh

    # ------------------------------------------------------------------
    # FPCA: 4 components over all 400 observations
    # NOTE: Fdata.to_pc uses n_comp (not n_components)
    # ------------------------------------------------------------------
    fd = fdars.Fdata(X, argvals=ARG)
    pc = fd.to_pc(n_comp=4)
    # pc["scores"].shape: (400, 4)
    # variance explained (live, from sv^2/sum(sv^2)): [0.693, 0.230, 0.054, 0.023]
    # cumulative: [0.693, 0.922, 0.977, 1.000]

    # ------------------------------------------------------------------
    # Build int64 class labels from the index (GOTCHA: must be int64 ndarray)
    # ------------------------------------------------------------------
    labels_str = ph.index.tolist()
    uniq = uniq_pre                           # ['aa', 'ao', 'dcl', 'iy', 'sh']
    lut = {l: i for i, l in enumerate(uniq)}
    y = np.array([lut[l] for l in labels_str], dtype=np.int64)

    # ------------------------------------------------------------------
    # 5-fold CV: FPCATransformer (n_components) + FPCLDAClassifier (ncomp)
    # GOTCHA: FPCATransformer uses n_components; FPCLDAClassifier uses ncomp
    # DO NOT pipe FPCATransformer -> FPCKNNClassifier (double-applies FPCA)
    # ------------------------------------------------------------------
    pipe = Pipeline([
        ("fpca", FPCATransformer(n_components=4)),
        ("lda", FPCLDAClassifier(ncomp=4)),
    ])
    cv_scores = cross_val_score(pipe, X, y, cv=5, scoring="accuracy")
    # REAL OUTPUT: [0.850, 0.850, 0.8625, 0.875, 0.875]  mean: 0.8625
    # round(acc, 3) = 0.863 (Python float rounding); round(acc * 100, 1) = 86.2
    acc = float(cv_scores.mean())
    print("CV accuracy:", round(acc, 3))
    print("CV fold scores:", [round(float(s), 4) for s in cv_scores])

    # ------------------------------------------------------------------
    # Create output directory
    # ------------------------------------------------------------------
    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: raw spectra + GCV-smoothed curves (one colour per class)
    # ------------------------------------------------------------------
    colors = FDARS_COLORS[:5]

    f1, ax1 = fig()
    for ci, (cls, col) in enumerate(zip(uniq, colors)):
        idx = [j for j, l in enumerate(labels_str) if l == cls]
        # Plot a few raw curves (lighter alpha)
        for j in idx[:3]:
            ax1.plot(ARG, X[j], color=col, alpha=0.18, linewidth=0.7)
        # Overlay smoothed curves: sm["fitted"] is ordered class-by-class
        # (rows ci*4 .. ci*4+3 correspond to class cls — see `selected` above).
        smooth_start = ci * 4
        smooth_end = smooth_start + 4
        for row in range(smooth_start, smooth_end):
            label = cls if row == smooth_start else None
            ax1.plot(ARG, sm["fitted"][row], color=col, linewidth=1.4,
                     label=label)

    ax1.set_xlabel("Frequency (log-periodogram index)")
    ax1.set_ylabel("Log-amplitude")
    ax1.set_title("Phoneme log-periodogram spectra: raw and GCV-smoothed")
    ax1.legend(title="Phoneme", fontsize=7, title_fontsize=7)
    save_figure(f1, _FIGURES_DIR / "cs1_phoneme_smooth.pdf")

    # ------------------------------------------------------------------
    # Figure 2: FPCA scores scatter (PC1 vs PC2), colour-coded by class
    # ------------------------------------------------------------------
    scores = pc["scores"]    # (400, 4)

    # Compute variance-explained fractions live from singular values (WR-01).
    # prop_var[i] = sv[i]^2 / sum(sv^2); no hardcoded magic numbers.
    sv = pc["singular_values"]                   # shape (4,)
    prop_var = sv ** 2 / float(np.sum(sv ** 2))  # fraction per component
    print("Variance explained:", [round(float(v), 3) for v in prop_var])

    f2, ax2 = fig()
    for ci, (cls, col) in enumerate(zip(uniq, colors)):
        mask = y == ci
        ax2.scatter(scores[mask, 0], scores[mask, 1], color=col, s=12,
                    alpha=0.7, label=cls)

    ax2.set_xlabel(
        f"PC1 ({round(float(prop_var[0]) * 100, 1)}% var. explained)"
    )
    ax2.set_ylabel(
        f"PC2 ({round(float(prop_var[1]) * 100, 1)}% var. explained)"
    )
    # Use round(acc, 3) for consistent %-display with the printed CV accuracy.
    ax2.set_title(
        "Phoneme FPCA scores (PC1 vs PC2)\n"
        "5-fold CV accuracy: " + str(round(round(acc, 3) * 100, 1)) + "%"
    )
    ax2.legend(title="Phoneme", fontsize=7, title_fontsize=7)
    save_figure(f2, _FIGURES_DIR / "cs1_phoneme_fpca.pdf")


if __name__ == "__main__":
    main()
