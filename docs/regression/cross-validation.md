# Cross-Validation for Functional Data

Every functional regression and classifier in `fdars` has a tuning knob — most often the
number of components $k$ (FPC, PLS, or shape components). Choosing $k$ by looking at the
*training* error is a trap: error falls monotonically as $k$ grows, so you always pick the
most complex, most over-fit model. **Cross-validation** breaks this by scoring each model
on data it never saw during fitting, giving an honest estimate of out-of-sample error and
a principled way to select $k$.

`fdars` ships dedicated cross-validators — `fregre_cv` for scalar-on-function regression
and `fclassif_cv` for functional classification — that do the fold splitting, refitting,
and out-of-fold scoring for you across a grid of component counts.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.regression import fregre_cv

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=40, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

cv = fregre_cv(X, y, k_min=1, k_max=10, n_folds=5)
k = np.asarray(cv["k_values"])
err = np.asarray(cv["cv_errors"])

f, ax = fig()
ax.plot(k, err, "-o", color="#3f51b5", lw=2, ms=6)
ax.axvline(cv["optimal_k"], color="#e8710a", ls="--", lw=1.5,
           label=f"optimal k = {cv['optimal_k']}")
ax.set(title="5-fold CV error vs. number of components",
       xlabel="number of components k", ylabel="CV MSE")
ax.legend()
print(render(f))
```

The curve has the classic U-shape: too few components under-fit (high bias), too many
over-fit (high variance). The minimum marks the sweet spot — often an *elbow* rather than
a sharp valley.

## Concepts

In **$K$-fold cross-validation** the sample is partitioned into $K$ folds. For each fold
$j$, the model is trained on the other $K-1$ folds and predicts the held-out fold $j$. The
**out-of-fold (OOF)** predictions $\hat y_i^{(-j(i))}$ — each made by a model that never saw
observation $i$ — are collected across all folds and scored:

$$
\text{CV}(k) = \frac{1}{n}\sum_{i=1}^{n}\big(y_i - \hat y_i^{(-j(i))}\big)^2 .
$$

Because every prediction is genuinely out-of-sample, $\text{CV}(k)$ is an (approximately)
unbiased estimate of test error. Selecting $\hat k = \arg\min_k \text{CV}(k)$ is **model
selection**: we search the grid of component counts and keep the one with the lowest honest
error. This is the resampling counterpart to the information criteria in
[`model_selection_ncomp`](scalar-on-function.md#4-model-selection) (GCV/AIC/BIC), which
approximate the same quantity analytically without refitting.

!!! warning "Only the *number* of components is tuned on CV"
    Cross-validation here selects $k$. It does not, by itself, protect against leaking
    information via preprocessing done on the full sample before splitting (e.g. centering,
    scaling, or FPCA on all $n$ curves). `fregre_cv` refits the whole pipeline inside each
    fold, so its OOF predictions are clean.

## Regression: `fregre_cv`

```python
import numpy as np
from fdars.simulation import simulate
from fdars.regression import fregre_cv

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=40, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

cv = fregre_cv(X, y, k_min=1, k_max=10, n_folds=5)

print(f"optimal components: {cv['optimal_k']}")
print(f"min CV error:       {cv['min_cv_error']:.4f}")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional predictors |
| `response` | `ndarray (n,)` | Scalar response |
| `k_min`, `k_max` | `int` | Range of component counts to search |
| `n_folds` | `int` | Number of CV folds (default 5) |

| Return key | Type | Description |
|------------|------|-------------|
| `optimal_k` | `int` | Component count with lowest CV error |
| `min_cv_error` | `float` | CV MSE at `optimal_k` |
| `k_values` | `ndarray` | Grid of component counts tested |
| `cv_errors` | `ndarray` | CV MSE for each $k$ |
| `oof_predictions` | `ndarray (n,)` | Out-of-fold prediction for each observation |
| `fold_assignments` | `ndarray (n,)` | Which fold each observation belongs to |
| `fold_errors` | `ndarray (n_folds,)` | Error contributed by each fold |

The `oof_predictions` are the honest predictions — plot them against the observed response
to see the model's true generalization, not its optimistic training fit.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.regression import fregre_cv

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=40, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

cv = fregre_cv(X, y, k_min=1, k_max=10, n_folds=5)
oof = np.asarray(cv["oof_predictions"])
folds = np.asarray(cv["fold_assignments"])
r2_oof = 1 - np.sum((y - oof) ** 2) / np.sum((y - y.mean()) ** 2)

f, ax = fig()
sc = ax.scatter(y, oof, c=folds, cmap="viridis", s=36, alpha=0.9)
lim = [min(y.min(), oof.min()), max(y.max(), oof.max())]
ax.plot(lim, lim, color="#6c757d", ls="--", lw=1.5)
ax.set(title=f"Out-of-fold predictions (OOF R² = {r2_oof:.2f})",
       xlabel="observed y", ylabel="out-of-fold prediction")
f.colorbar(sc, ax=ax, label="fold")
print(render(f))
```

## Classification: `fclassif_cv`

For classifiers, the analogue is the cross-validated **misclassification rate**.
`fclassif_cv` sweeps the number of components internally and reports the best count along
with the per-fold error.

```python
import numpy as np
from fdars.simulation import simulate
from fdars.classification import fclassif_cv

np.random.seed(1)
t = np.linspace(0, 1, 60)
Xa = np.asarray(simulate(n=20, argvals=t, n_basis=6, efun_type="fourier", seed=1))
Xb = np.asarray(simulate(n=20, argvals=t, n_basis=6, efun_type="fourier", seed=2))
Xa = 0.5 * Xa + np.sin(2 * np.pi * t)            # class 0 mean shape
Xb = 0.5 * Xb + np.sin(2 * np.pi * t) + 1.2 * t  # class 1 mean shape
X = np.vstack([Xa, Xb])
labels = np.r_[np.zeros(20, int), np.ones(20, int)]

cv = fclassif_cv(X, t, labels, method="lda", ncomp=3, nfold=5)

print(f"CV error rate: {cv['error_rate']:.3f}")
print(f"best ncomp:    {cv['best_ncomp']}")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional predictors |
| `argvals` | `ndarray (m,)` | Evaluation grid |
| `labels` | `ndarray (n,)` | Integer class labels |
| `method` | `str` | Base classifier (`"lda"`, `"qda"`, `"knn"`, …) |
| `ncomp` | `int` | Max number of components to consider |
| `nfold` | `int` | Number of folds |

| Return key | Type | Description |
|------------|------|-------------|
| `error_rate` | `float` | Cross-validated misclassification rate |
| `fold_errors` | `ndarray (nfold,)` | Error rate within each fold |
| `best_ncomp` | `int` | Component count minimizing CV error |

!!! tip "Reading the fold-error spread"
    A large spread in `fold_errors` signals an unstable model — the estimate of test error
    is itself noisy, often because $n$ is small relative to the model complexity. Prefer the
    simpler model (fewer components) when two settings are within one fold-standard-error of
    each other (the "one-standard-error rule").

## Related pages

- [Scalar-on-function regression](scalar-on-function.md) — the models being tuned, plus
  `model_selection_ncomp` for information-criterion selection.
- [Regression diagnostics](regression-diagnostics.md) — leave-one-out PRESS, a per-point
  cousin of CV.
- [Conformal prediction](conformal-prediction.md) — turning honest error into finite-sample
  coverage guarantees.
