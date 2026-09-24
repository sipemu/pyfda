"""Case Study 4: Composable scikit-learn pipelines on the Berkeley growth data.

Classifies each child's sex from their height curve with a pipeline that chains
an (optional) fdars velocity step, an fdars ``FPCATransformer`` and a stock
scikit-learn ``LinearDiscriminantAnalysis``.  ``GridSearchCV`` chooses both the
functional *representation* (height vs growth velocity) and the number of FPCA
components; the whole search is wrapped in an outer repeated cross-validation
(nested CV) so the reported accuracy is not biased by the model selection.

Two scalar baselines are scored under the identical outer CV:
- logistic regression on the final (age-18) height;
- logistic regression on the heights at ages 12 and 18 (an expert's hand-picked
  "before and after puberty" pair).

Writes two deterministic committed figures to paper/figures/:
- cs4_growth_gridsearch.pdf -- inner-CV accuracy per (representation, n_components)
- cs4_growth_scores.pdf     -- FPCA scores of the selected model, coloured by sex

Run with::

    PYTHONPATH=scripts:paper/code python paper/code/casestudy4.py          # figures + numbers
    PYTHONPATH=scripts:paper/code python paper/code/casestudy4.py --check  # numbers drift gate

Every number quoted in paper/sections/casestudy4.tex is written to
paper/sections/cs4_numbers.tex (see cs_numbers.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from paper_utils import (
    fig, FDARS_COLORS, save_figure,
    style_setup, clean_ax, brand_legend, metric_box, DIMGREY,
)

import fdars
from fdars import Fdata, datasets
from fdars.sklearn import FPCATransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    GridSearchCV, RepeatedStratifiedKFold, StratifiedKFold, cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from cs_numbers import emit, fmt

_FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

_DS = datasets.load_growth()
_AGES = np.asarray(_DS.data.argvals, dtype=np.float64)       # 31 ages, 1..18


def velocity(X: np.ndarray) -> np.ndarray:
    """Growth-velocity curves: GCV B-spline smoothing then first derivative.

    A module-level function so the ``FunctionTransformer`` wrapping it is
    clonable/picklable inside ``GridSearchCV``.
    """
    smooth = fdars.basis.smooth_basis_gcv(
        X, _AGES, n_basis=12, basis_type="bspline")["fitted"]
    return Fdata(smooth, argvals=_AGES).deriv().data


def main(check: bool = False) -> int:
    """Run the nested-CV pipeline study and write two deterministic figures.

    With ``check=True`` only the number macros are recomputed and compared with
    the committed file (no figures are written); returns 1 on drift.

    All cross-validation splitters are seeded and ``GridSearchCV`` runs with
    ``n_jobs=1``, so split order and results are reproducible.
    """
    np.random.seed(42)
    style_setup()

    X = np.asarray(_DS.data.data, dtype=np.float64)            # (93, 31)
    sex = _DS.data.metadata["sex"].astype(str).str.lower()
    y = sex.str.startswith("f").astype(int).to_numpy()          # 1 = girl
    print("children:", X.shape[0], "girls:", int(y.sum()),
          "boys:", int((1 - y).sum()))

    # ------------------------------------------------------------------
    # Pipeline: [representation] -> fdars FPCA -> sklearn LDA.
    # The "rep" step is either passthrough (height curves) or the velocity
    # transformer; GridSearchCV treats it as an ordinary hyperparameter.
    # ------------------------------------------------------------------
    pipe = Pipeline([
        ("rep", "passthrough"),
        ("fpca", FPCATransformer(argvals=_AGES, n_components=2)),
        ("lda", LinearDiscriminantAnalysis()),
    ])
    reps = {"height": "passthrough", "velocity": FunctionTransformer(velocity)}
    n_grid = [2, 3, 4, 6]
    grid = {"rep": list(reps.values()), "fpca__n_components": n_grid}
    n_inner, n_outer, n_rep = 5, 5, 10
    inner = StratifiedKFold(n_splits=n_inner, shuffle=True, random_state=0)
    search = GridSearchCV(pipe, grid, cv=inner, scoring="accuracy",
                          refit=True, n_jobs=1)

    # Selection on the full sample (drives Figure 1 and the chosen model).
    search.fit(X, y)
    res = search.cv_results_
    scores = {name: [] for name in reps}
    for params, s in zip(res["params"], res["mean_test_score"]):
        name = "height" if params["rep"] == "passthrough" else "velocity"
        scores[name].append(float(s))
    best_rep = ("height" if search.best_params_["rep"] == "passthrough"
                else "velocity")
    best_k = int(search.best_params_["fpca__n_components"])
    print("inner-CV accuracy:", {k: [round(v, 3) for v in vs]
                                 for k, vs in scores.items()})
    print("selected:", best_rep, best_k)

    # ------------------------------------------------------------------
    # Nested CV: the entire GridSearchCV is the estimator being evaluated.
    # Baselines are scored with the identical outer splitter.
    # ------------------------------------------------------------------
    outer = RepeatedStratifiedKFold(n_splits=n_outer, n_repeats=n_rep,
                                    random_state=1)
    nested = cross_val_score(search, X, y, cv=outer, scoring="accuracy")
    i12 = int(np.argmin(np.abs(_AGES - 12.0)))
    base18 = cross_val_score(LogisticRegression(max_iter=1000), X[:, [-1]], y,
                             cv=outer, scoring="accuracy")
    base2 = cross_val_score(LogisticRegression(max_iter=1000),
                            X[:, [i12, X.shape[1] - 1]], y,
                            cv=outer, scoring="accuracy")
    print(f"nested CV (functional pipeline): {nested.mean():.3f} "
          f"+/- {nested.std():.3f}")
    print(f"baseline height@18:              {base18.mean():.3f} "
          f"+/- {base18.std():.3f}")
    print(f"baseline height@12+@18:          {base2.mean():.3f} "
          f"+/- {base2.std():.3f}")

    # ------------------------------------------------------------------
    # Every number quoted in casestudy4.tex (letters-only macro names).
    # ``+/-`` values are standard deviations over the outer folds.
    # ------------------------------------------------------------------
    words = {2: "Two", 3: "Three", 4: "Four", 6: "Six"}
    macros = {
        "csFourNChildren": str(X.shape[0]),
        "csFourNBoys": str(int((1 - y).sum())),
        "csFourNGirls": str(int(y.sum())),
        "csFourNAges": str(X.shape[1]),
        "csFourAgeMin": fmt(_AGES.min(), 0),
        "csFourAgeMax": fmt(_AGES.max(), 0),
        "csFourGrid": ", ".join(str(k) for k in n_grid),
        "csFourNInner": str(n_inner),
        "csFourNOuter": str(n_outer),
        "csFourNRep": str(n_rep),
        "csFourNOuterFolds": str(len(nested)),
    }
    for name in reps:
        for k, v in zip(n_grid, scores[name]):
            macros[f"csFour{name.capitalize()}{words[k]}"] = fmt(v, 3)
    macros.update({
        "csFourBestRep": best_rep,
        "csFourBestK": str(best_k),
        "csFourBestKWord": {2: "two", 3: "three", 4: "four", 6: "six"}[best_k],
        "csFourNested": fmt(nested.mean(), 3),
        "csFourNestedSd": fmt(nested.std(), 3),
        "csFourBaseEighteen": fmt(base18.mean(), 3),
        "csFourBaseEighteenSd": fmt(base18.std(), 3),
        "csFourBaseTwo": fmt(base2.mean(), 3),
        "csFourBaseTwoSd": fmt(base2.std(), 3),
        "csFourAgeEarly": fmt(_AGES[i12], 0),
    })
    status = emit("cs4_numbers.tex", "casestudy4.py", macros, check=check)
    if check:
        return status

    _FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: inner-CV accuracy per representation x n_components.
    # ------------------------------------------------------------------
    f1, ax1 = fig()
    width = 0.38
    xpos = np.arange(len(n_grid))
    for j, (name, color) in enumerate((("height", FDARS_COLORS[0]),
                                       ("velocity", FDARS_COLORS[1]))):
        bars = ax1.bar(xpos + (j - 0.5) * width, scores[name], width=width,
                       color=color, edgecolor="white", linewidth=0.5,
                       label=f"{name.capitalize()} curves")
        for bar, s in zip(bars, scores[name]):
            ax1.text(bar.get_x() + bar.get_width() / 2.0, s + 0.006,
                     f"{s:.3f}", ha="center", va="bottom", fontsize=7,
                     color=DIMGREY)
    ax1.axhline(base18.mean(), color=DIMGREY, linestyle=":", linewidth=1.2,
                label=f"Baseline: final height ({base18.mean():.3f})")
    ax1.set_xticks(xpos)
    ax1.set_xticklabels([str(k) for k in n_grid])
    ax1.set_xlabel("Number of FPCA components")
    ax1.set_ylabel("Mean 5-fold CV accuracy")
    ax1.set_ylim(0.75, 1.03)
    ax1.set_title("GridSearchCV over representation and FPCA dimension\n"
                  "(Berkeley growth: classify sex from the growth curve)")
    clean_ax(ax1, frame=True)
    brand_legend(ax1, fontsize=7, loc="lower right")
    save_figure(f1, _FIGURES_DIR / "cs4_growth_gridsearch.pdf")

    # ------------------------------------------------------------------
    # Figure 2: FPCA scores of the selected (refit) model, coloured by sex,
    # with the LDA decision boundary in the PC1-PC2 plane.
    # ------------------------------------------------------------------
    best = search.best_estimator_
    Z = best[:-1].transform(X)                        # (93, best_k) scores
    lda = best.named_steps["lda"]
    f2, ax2 = fig()
    for lab, name, color, marker in ((0, "Boys", FDARS_COLORS[0], "o"),
                                     (1, "Girls", FDARS_COLORS[3], "s")):
        m = y == lab
        ax2.scatter(Z[m, 0], Z[m, 1], s=22, alpha=0.8, color=color,
                    marker=marker, edgecolors="none",
                    label=f"{name} (n={int(m.sum())})")
    if best_k == 2:
        w, b = lda.coef_[0], float(lda.intercept_[0])
        xs = np.linspace(Z[:, 0].min(), Z[:, 0].max(), 50)
        ax2.plot(xs, -(w[0] * xs + b) / w[1], color=DIMGREY, linestyle="--",
                 linewidth=1.2, label="LDA boundary")
        ax2.set_ylim(Z[:, 1].min() * 1.15, Z[:, 1].max() * 1.15)
    ax2.set_xlabel("FPC 1 score (overall size)")
    ax2.set_ylabel("FPC 2 score (growth timing)")
    ax2.set_title(f"Selected model: {best_rep} curves, {best_k} FPCA "
                  "components + LDA")
    clean_ax(ax2, frame=True)
    metric_box(ax2, f"Nested CV accuracy\n{nested.mean():.3f} "
               f"$\\pm$ {nested.std():.3f}", loc="upper left")
    brand_legend(ax2, fontsize=7, loc="lower right")
    save_figure(f2, _FIGURES_DIR / "cs4_growth_scores.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv))
