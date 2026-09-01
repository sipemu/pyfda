# GridSearchCV Example

<div class="fdars-section-hero" markdown>
Tune every stage of a functional `Pipeline` simultaneously — smoothing bandwidth,
number of FPC components, classifier hyperparameters — with a single
`GridSearchCV` call. No glue code required.
</div>

## When to use GridSearchCV with a functional Pipeline

`GridSearchCV` treats the entire `Pipeline` as a single estimator and searches over
any stage's hyperparameters using the double-underscore (`stage__param`) addressing
convention. For a functional Pipeline this means you can jointly optimise:

- **Smoothing bandwidth** — `smoother__bandwidth` controls how aggressively noise is
  removed before FPCA.
- **Number of FPC components** — `fpca__n_components` controls how many principal
  components the `FPCATransformer` retains for the downstream predictor.
- **Predictor hyperparameters** — `clf__ncomp` or `reg__n_components` control the
  classifier's or regressor's own dimensionality.

Because `fdars.sklearn` estimators follow the full sklearn API, `GridSearchCV`
requires no special handling — the exact same call you would write for a
tabular-data pipeline works unchanged on functional data.

## Worked Example

The fence below builds a four-stage classification pipeline, defines a 2×2
hyperparameter grid (`fpca__n_components` × `clf__ncomp`), runs 3-fold cross-
validation (12 fits total), and plots the mean CV score per candidate.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.sklearn._skeletons import (
    BSplineSmoother,
    FPCATransformer,
    FPCLDAClassifier,
    Imputer,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

# --- Small synthetic two-class dataset (40 obs × 20 pts) ------------------
rng = np.random.default_rng(7)
half = 20
X0 = rng.standard_normal((half, 20))          # class 0: baseline noise
X1 = rng.standard_normal((half, 20)) + 3.0   # class 1: mean-shifted +3

X = np.vstack([X0, X1])
y = np.array([0] * half + [1] * half, dtype=int)

# Inject sparse NaN so the Imputer stage does real work (stride avoids col 0)
X_nan = X.copy()
X_nan[::5, 2::7] = np.nan

X_train, X_test, y_train, y_test = train_test_split(
    X_nan, y, test_size=0.25, stratify=y, random_state=7
)

# --- Four-stage Pipeline --------------------------------------------------
pipe = Pipeline([
    ("imputer",  Imputer()),
    ("smoother", BSplineSmoother()),
    ("fpca",     FPCATransformer()),
    ("clf",      FPCLDAClassifier()),
])

# --- 2×2 grid: 4 candidates, cv=3 → 12 fits (fast, offline) --------------
param_grid = {
    "fpca__n_components": [2, 3],
    "clf__ncomp":         [1, 2],
}

grid = GridSearchCV(pipe, param_grid, cv=3, refit=True)
grid.fit(X_train, y_train)

# --- Plot CV mean score per candidate -------------------------------------
results = grid.cv_results_
mean_scores = results["mean_test_score"]
params = results["params"]
labels = [
    f"fpca={p['fpca__n_components']}\nclf={p['clf__ncomp']}"
    for p in params
]

f, ax = fig(figsize=(7, 4))
bars = ax.bar(labels, mean_scores, color="#3f51b5", alpha=0.82, width=0.5)
ax.set_ylim(0, 1.05)
ax.set_xlabel("Hyperparameter candidate")
ax.set_ylabel("Mean CV accuracy")
ax.set_title("GridSearchCV: mean CV accuracy per candidate")
for bar, score in zip(bars, mean_scores):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{score:.2f}",
        ha="center", va="bottom", fontsize=10,
    )

print(render(f))
print("best_params:", grid.best_params_, " FDARS_FENCE_OK")
```

## What the output shows

- **Bars** — mean 3-fold CV accuracy for each of the four `(fpca__n_components,
  clf__ncomp)` combinations.
- **`best_params_`** — the winning combination that `GridSearchCV` refits on the
  full training set before `predict`.

The two classes are separated by a mean shift of 3.0 standard deviations, so even
the smallest grid candidate achieves high accuracy. In a realistic setting the
score differences across candidates guide the choice of FPC dimensionality.

## Evaluating the best pipeline

After `GridSearchCV.fit`, the `best_estimator_` is already refit on the full
training set and ready for `predict` / `score`:

```python
y_pred = grid.predict(X_test)
test_acc = grid.score(X_test, y_test)
```

This is identical to calling `.predict` on a plain `Pipeline` — `GridSearchCV`
wraps the best pipeline transparently.

## Searching over smoother bandwidth

Extend the grid to include the `BSplineSmoother` bandwidth by adding a
`smoother__bandwidth` key:

```python
param_grid = {
    "smoother__bandwidth": [0.1, 0.3],
    "fpca__n_components":  [2, 3],
    "clf__ncomp":          [1, 2],
}
```

A 2×2×2 grid with `cv=3` is 24 fits — still fast on small data. Larger grids
benefit from `n_jobs=-1` (parallel CV folds) or `HalvingGridSearchCV` for
early-stopping.

## See also

- [Pipeline Example](index.md#worked-example-pipeline) — fitting without grid search
- [Transformers](transformers.md) — the preprocessing stages available
- [Regressors & Classifiers](regressors-classifiers.md) — the predictor families
