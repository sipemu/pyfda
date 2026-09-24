"""Case Study 1: Smoothing, FPCA, and Classification on Phoneme Data.

Runs the Study-1 pipeline against fdars 0.13.0:
1. GCV B-spline smoothing of log-periodogram spectra.
2. FPCA (4 components) over all 400 observations; variance shares are shares
   of the TOTAL (quadrature-weighted) variance, not of the retained components.
3. 5-fold cross-validated classification: FPCATransformer followed by
   scikit-learn's LinearDiscriminantAnalysis (FPCA applied once), cross-checked
   against the one-step FPCLDAClassifier.

Every number quoted in paper/sections/casestudy1.tex is written to
paper/sections/cs1_numbers.tex (see cs_numbers.py).

Writes two deterministic committed figures to paper/figures/:
- cs1_phoneme_smooth.pdf  -- raw spectra + smoothed curves per class
- cs1_phoneme_fpca.pdf    -- FPCA scores scatter (PC1 vs PC2) colour-coded by class

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy1.py          # figures + numbers
    PYTHONPATH=scripts:paper/code python paper/code/casestudy1.py --check  # numbers drift gate
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from paper_utils import (
    fig, FDARS_COLORS, save_figure, data_path,
    style_setup, clean_ax, brand_legend, metric_box,
)

import fdars
from fdars.sklearn import FPCATransformer, FPCLDAClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_predict, cross_val_score

from cs_numbers import emit, fmt, pct as _pct

# Size of the full ESL phoneme.data file the balanced 400-curve subset was drawn
# from (docs/data/README.md: 4509 rows; subset with numpy seed 0).
_N_FULL_ESL = 4509
_N_BASIS = 15          # B-spline basis size for the smoothing illustration
_N_RAW_SHOWN = 3       # raw curves per class drawn in Figure 1

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def main(check: bool = False) -> int:
    """Run the Study-1 pipeline and write two deterministic figures.

    With ``check=True`` only the number macros are recomputed and compared with
    the committed file (no figures are written); returns 1 on drift.

    Seeds the RNG first (per Determinism Pinning Summary in 89-RESEARCH).
    FPCATransformer, FPCLDAClassifier, and KFold(5, shuffle=False) are
    all deterministic; no additional random_state arguments are required.
    """
    np.random.seed(42)
    style_setup()

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
    sm = fdars.basis.smooth_basis_gcv(X[selected], ARG, n_basis=_N_BASIS, basis_type="bspline")
    # sm["fitted"].shape: (20, 256) — rows 0-3 = aa, 4-7 = ao, 8-11 = dcl, 12-15 = iy, 16-19 = sh

    # ------------------------------------------------------------------
    # FPCA: 4 components over all 400 observations
    # NOTE: Fdata.to_pc uses n_comp (not n_components)
    # ------------------------------------------------------------------
    fd = fdars.Fdata(X, argvals=ARG)
    pc = fd.to_pc(n_comp=4)
    # pc["scores"].shape: (400, 4)
    # Variance shares of the TOTAL variance: the denominator is the full
    # quadrature-weighted variance trace(Xc^T W Xc) = sum of ALL squared singular
    # values of Xc*sqrt(w), not just the 4 retained ones.
    sv = np.asarray(pc["singular_values"])                      # shape (4,)
    w = np.asarray(pc["weights"])
    total_var = float(np.sum((X - X.mean(axis=0)) ** 2 * w))
    prop_var = sv ** 2 / total_var
    cum_var = np.cumsum(prop_var)
    print("Variance explained (share of total):",
          [round(float(v), 3) for v in prop_var])

    # ------------------------------------------------------------------
    # Build int64 class labels from the index (GOTCHA: must be int64 ndarray)
    # ------------------------------------------------------------------
    labels_str = ph.index.tolist()
    uniq = uniq_pre                           # ['aa', 'ao', 'dcl', 'iy', 'sh']
    lut = {l: i for i, l in enumerate(uniq)}
    y = np.array([lut[l] for l in labels_str], dtype=np.int64)

    # ------------------------------------------------------------------
    # 5-fold CV: FPCATransformer (n_components) -> sklearn LDA.
    # FPCA is applied exactly once.  (FPCLDAClassifier performs its own FPCA,
    # so piping FPCATransformer into it would apply FPCA twice.)
    # GOTCHA: FPCATransformer uses n_components; FPCLDAClassifier uses ncomp.
    # ------------------------------------------------------------------
    pipe = Pipeline([
        ("fpca", FPCATransformer(n_components=4)),
        ("lda", LinearDiscriminantAnalysis()),
    ])
    cv_scores = cross_val_score(pipe, X, y, cv=5, scoring="accuracy")
    acc = float(cv_scores.mean())
    print("CV accuracy (FPCATransformer + LDA):", round(acc, 4))
    print("CV fold scores:", [round(float(s), 4) for s in cv_scores])
    # Cross-check: the one-step fdars classifier on the same folds.
    cv_one = cross_val_score(FPCLDAClassifier(ncomp=4), X, y, cv=5,
                             scoring="accuracy")
    acc_one = float(cv_one.mean())
    print("CV accuracy (FPCLDAClassifier alone):", round(acc_one, 4))

    # ------------------------------------------------------------------
    # How separable are the classes in the PC1-PC2 plane alone?  5-fold CV
    # LDA on the first two scores; per-class recall and the aa<->ao confusion.
    # ------------------------------------------------------------------
    pred2 = cross_val_predict(LinearDiscriminantAnalysis(), pc["scores"][:, :2],
                              y, cv=5)
    cm2 = confusion_matrix(y, pred2, labels=list(range(len(uniq))))
    recall2 = {cls: int(cm2[i, i]) for i, cls in enumerate(uniq)}
    per_class = int(np.bincount(y).min())
    aa, ao = lut["aa"], lut["ao"]
    aa_ao_confused = int(cm2[aa, ao] + cm2[ao, aa])
    print("PC1-PC2 LDA recall per class:", recall2,
          "aa<->ao confusions:", aa_ao_confused)

    # ------------------------------------------------------------------
    # Every number quoted in casestudy1.tex (letters-only macro names).
    # ------------------------------------------------------------------
    words = ["One", "Two", "Three", "Four", "Five"]
    macros: dict[str, str] = {
        "csOneNCurves": str(X.shape[0]),
        "csOneNPerClass": str(per_class),
        "csOneNClasses": str(len(uniq)),
        "csOneNFull": f"{_N_FULL_ESL:,}".replace(",", "{,}"),
        "csOneNPoints": str(X.shape[1]),
        "csOneSmoothNBasis": str(_N_BASIS),
        "csOneSmoothN": str(len(selected)),
        "csOneRawShown": str(_N_RAW_SHOWN),
        "csOneNComp": str(len(sv)),
    }
    for k in range(len(sv)):
        macros[f"csOneVarPC{words[k]}"] = _pct(prop_var[k])
    macros["csOneCumVarThree"] = _pct(cum_var[2])
    macros["csOneCumVarFour"] = _pct(cum_var[3])
    macros["csOneCVAcc"] = _pct(acc)
    macros["csOneCVFolds"] = ", ".join(fmt(v, 3) for v in cv_scores)
    macros["csOneCVAccFPCLDA"] = _pct(acc_one)
    for cls in uniq:
        macros[f"csOneRecall{cls.capitalize()}"] = str(recall2[cls])
    macros["csOneAaAoConfused"] = str(aa_ao_confused)
    macros["csOneAaAoTotal"] = str(2 * per_class)
    status = emit("cs1_numbers.tex", "casestudy1.py", macros, check=check)
    if check:
        return status

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
        for j in idx[:_N_RAW_SHOWN]:
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
    clean_ax(ax1, frame=True)
    brand_legend(ax1, title="Phoneme", fontsize=7, title_fontsize=7)
    save_figure(f1, _FIGURES_DIR / "cs1_phoneme_smooth.pdf")

    # ------------------------------------------------------------------
    # Figure 2: FPCA scores scatter (PC1 vs PC2), colour-coded by class
    # ------------------------------------------------------------------
    scores = pc["scores"]    # (400, 4)

    f2, ax2 = fig()
    for ci, (cls, col) in enumerate(zip(uniq, colors)):
        mask = y == ci
        ax2.scatter(scores[mask, 0], scores[mask, 1], color=col, s=12,
                    alpha=0.7, label=cls)

    ax2.set_xlabel(f"PC1 ({_pct(prop_var[0])}% of total variance)")
    ax2.set_ylabel(f"PC2 ({_pct(prop_var[1])}% of total variance)")
    ax2.set_title("Phoneme FPCA scores (PC1 vs PC2)")
    clean_ax(ax2, frame=True)
    metric_box(
        ax2,
        f"5-fold CV accuracy\n(FPCA + LDA): {_pct(acc)}%",
        loc="upper right",
    )
    brand_legend(ax2, title="Phoneme", fontsize=7, title_fontsize=7,
                 loc="lower right")
    save_figure(f2, _FIGURES_DIR / "cs1_phoneme_fpca.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv))
