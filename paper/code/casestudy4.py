"""Case Study 4: sklearn Pipeline + GridSearchCV on Wine Data.

Runs the validated Study-4 pipeline against fdars 0.12.0:
1. Load wine.csv (178 samples x 13 features, 3 classes).
2. Build a Pipeline of FPCATransformer + sklearn LinearDiscriminantAnalysis.
3. Tune the FPCA dimensionality via GridSearchCV (n_components in {2, 3, 5, 8}).
4. Report honest best CV accuracy and grid results.

Writes two deterministic committed figures to paper/figures/:
- cs4_wine_gridsearch.pdf  -- mean CV accuracy vs n_components (bar chart)
- cs4_wine_scores.pdf      -- FPCA scores scatter (PC1 vs PC2) coloured by class

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy4.py

Design notes:
- Pipeline is FPCATransformer -> sklearn LDA, NOT FPCATransformer -> FPCKNNClassifier.
  FPCKNNClassifier applies FPCA internally, so chaining with FPCATransformer
  double-applies FPCA and degrades accuracy (89-RESEARCH Pitfall 2).
- Wine class labels are 1-indexed (1, 2, 3); subtract 1 for 0-indexed int64
  (89-RESEARCH Pitfall 5; sklearn convention).
- n_jobs=1 in GridSearchCV prevents parallel-ordering nondeterminism (Pitfall 7).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from paper_utils import (
    fig, FDARS_COLORS, save_figure, data_path,
    style_setup, clean_ax, brand_legend, metric_box, DIMGREY,
)

from fdars.sklearn._skeletons import FPCATransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def main() -> None:
    """Run the Study-4 GridSearchCV pipeline and write two deterministic figures.

    Seeds the RNG first (per Determinism Pinning Summary in 89-RESEARCH).
    LDA is deterministic; n_jobs=1 in GridSearchCV prevents parallel-ordering
    nondeterminism; KFold(5, shuffle=False) is also deterministic.
    """
    np.random.seed(42)
    style_setup()

    # ------------------------------------------------------------------
    # Load wine data (178 samples x 13 features; index IS the class: 1,2,3)
    # ------------------------------------------------------------------
    wn = pd.read_csv(data_path("wine.csv"), index_col=0)
    Xw = wn.values.astype(np.float64)                        # (178, 13)
    # Subtract 1: convert 1-indexed class labels to 0-indexed int64
    # (Pitfall 5 — sklearn convention; LDA works with both but 0-indexed is standard)
    yw = np.array(wn.index.tolist(), dtype=np.int64) - 1     # 0, 1, 2

    # ------------------------------------------------------------------
    # Build Pipeline: FPCATransformer -> sklearn LinearDiscriminantAnalysis
    # GOTCHA: FPCATransformer uses n_components (sklearn convention)
    # DO NOT use FPCKNNClassifier here — it re-applies FPCA (Pitfall 2)
    # n_jobs=1 for GridSearchCV determinism (Pitfall 7)
    # ------------------------------------------------------------------
    pipe = Pipeline([
        ("fpca", FPCATransformer(n_components=3)),
        ("lda", LinearDiscriminantAnalysis()),
    ])

    param_grid = {"fpca__n_components": [2, 3, 5, 8]}
    gs = GridSearchCV(
        pipe, param_grid, cv=5, scoring="accuracy", refit=True, n_jobs=1
    )
    gs.fit(Xw, yw)

    # Real output from 89-RESEARCH:
    #   best_params_: {'fpca__n_components': 8}  best_score_: 0.961
    #   mean_test_score: [0.697, 0.759, 0.916, 0.961] for n_components = 2, 3, 5, 8
    best_acc = round(float(gs.best_score_), 3)
    best_nc = int(gs.best_params_["fpca__n_components"])
    print("best:", gs.best_params_, best_acc)

    mean_scores = gs.cv_results_["mean_test_score"]
    n_components_grid = param_grid["fpca__n_components"]

    # ------------------------------------------------------------------
    # Create output directory
    # ------------------------------------------------------------------
    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: mean CV accuracy vs n_components (bar chart)
    # ------------------------------------------------------------------
    f1, ax1 = fig()
    bars = ax1.bar(
        [str(n) for n in n_components_grid],
        mean_scores,
        color=FDARS_COLORS[:len(n_components_grid)],
        width=0.6,
        edgecolor="white",
        linewidth=0.5,
    )
    # Annotate each bar with its mean accuracy value
    for bar, score in zip(bars, mean_scores):
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.008,
            str(round(float(score), 3)),
            ha="center",
            va="bottom",
            fontsize=8,
            color=DIMGREY,
        )
    ax1.set_xlabel("Number of FPCA components")
    ax1.set_ylabel("Mean 5-fold CV accuracy")
    ax1.set_title(
        "GridSearchCV: FPCATransformer + LDA on wine data\n"
        "Best: n = " + str(best_nc)
        + ", CV accuracy = " + str(best_acc)
    )
    ax1.set_ylim(0.0, 1.08)
    ax1.axhline(best_acc, color=DIMGREY, linewidth=0.8, linestyle="--")
    clean_ax(ax1, grid=True, grid_axis="y")
    save_figure(f1, _FIGURES_DIR / "cs4_wine_gridsearch.pdf")

    # ------------------------------------------------------------------
    # Figure 2: FPCA scores scatter (PC1 vs PC2) at best n_components
    # Equivalent to gs.best_estimator_.named_steps["fpca"].transform(Xw)
    # since FPCATransformer is deterministic given the same data and
    # n_components (GridSearchCV refit=True re-fits on the full dataset).
    # An independent fit is used here for clarity (IN-02).
    # ------------------------------------------------------------------
    fpca_best = FPCATransformer(n_components=best_nc)
    Xw_transformed = fpca_best.fit_transform(Xw)  # (178, best_nc)

    class_names = ["Class 1", "Class 2", "Class 3"]
    colors = FDARS_COLORS[:3]

    f2, ax2 = fig()
    for ci, (cname, col) in enumerate(zip(class_names, colors)):
        mask = yw == ci
        ax2.scatter(
            Xw_transformed[mask, 0],
            Xw_transformed[mask, 1],
            color=col,
            s=18,
            alpha=0.75,
            label=cname,
        )
    ax2.set_xlabel("FPCA component 1")
    ax2.set_ylabel("FPCA component 2")
    ax2.set_title(
        "Wine data: FPCA scores (n = "
        + str(best_nc)
        + " components, best GridSearchCV)"
    )
    clean_ax(ax2, frame=True)
    brand_legend(ax2, title="Wine class", fontsize=7, title_fontsize=7)
    save_figure(f2, _FIGURES_DIR / "cs4_wine_scores.pdf")


if __name__ == "__main__":
    main()
