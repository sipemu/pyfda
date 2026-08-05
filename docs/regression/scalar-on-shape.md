# Scalar-on-Shape Regression

Ordinary [scalar-on-function regression](scalar-on-function.md) predicts a scalar
response from the *amplitude* of a curve — its value at each fixed $t$. But sometimes
the response depends on the curve's **shape**: the pattern of peaks and troughs,
independent of how the curve is stretched or shifted along the $t$-axis. Two curves
that are warped versions of one another have the same shape and, for a shape-driven
response, should predict the same value.

Scalar-on-shape regression handles exactly this. We first quotient out warping with the
elastic (SRSF) machinery in `fdars.alignment`, then regress the response on either a
**shape distance matrix** (nonparametric) or **shape principal-component scores**
(linear). This page builds both pipelines on a seeded example.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.alignment import shape_mean

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=30, argvals=t, n_basis=6, efun_type="fourier", seed=1))

sm = shape_mean(X, t)                       # elastic (shape) Karcher mean
mean = np.asarray(sm["mean"])
aligned = np.asarray(sm["aligned_data"])    # curves warped onto the mean

f, ax = fig()
ax.plot(t, aligned.T, color="#3f51b5", lw=1, alpha=0.35)
ax.plot(t, mean, color="#e8710a", lw=2.6, label="shape mean")
ax.set(title="Curves aligned to the shape (Karcher) mean",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

## Concepts

A functional observation $x(t)$ can be split into an **amplitude** component (the shape
of the curve) and a **phase** component (a warping $\gamma$ of the $t$-axis). Two curves
$x_1$ and $x_2$ share a shape when there exists a warping $\gamma$ with
$x_1 \approx x_2 \circ \gamma$. The elastic (Fisher–Rao) framework makes this precise via
the square-root velocity function (SRVF); the resulting **shape distance**

$$
d_{\text{shape}}(x_1, x_2) = \min_{\gamma}\; \big\lVert q_1 - (q_2 \circ \gamma)\sqrt{\dot\gamma}\big\rVert_2
$$

is invariant to warping. The scalar-on-shape model then assumes the response depends on
the curve *only through its shape*:

$$
y_i = g\!\left(\text{shape}(x_i)\right) + \varepsilon_i .
$$

We estimate $g$ in two ways. **(1) Distance-based (nonparametric):** feed the pairwise
shape-distance matrix into the Nadaraya–Watson kernel regressor `fregre_np`, letting
similar-shaped curves borrow strength. **(2) Shape-PC (linear):** align all curves to the
shape mean, run FPCA on the aligned curves to obtain warping-invariant *shape scores*,
and regress the response on those scores with `fregre_lm`.

## Building the response

To make the example honest, we generate a scalar response that is genuinely a functional
of the curves plus noise. The two pipelines below are then evaluated against it.

```python
import numpy as np
from fdars.simulation import simulate

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=30, argvals=t, n_basis=6, efun_type="fourier", seed=1))

beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))
```

## Pipeline 1 — distance-based shape regression

`shape_self_distance_matrix` computes the full $n \times n$ matrix of pairwise shape
distances. Passing it to `fregre_np` gives a kernel regression whose geometry is defined
by shape similarity, not pointwise amplitude.

```python
import numpy as np
from fdars.alignment import shape_self_distance_matrix
from fdars.regression import fregre_np

D = np.asarray(shape_self_distance_matrix(X, t))   # (n, n) shape distances
np_fit = fregre_np(D, y, h=0.0)                    # h=0 -> automatic bandwidth

print(f"shape-NP R²:        {np_fit['r_squared']:.3f}")
print(f"selected bandwidth: {np_fit['h_func']:.3f}")
```

| Function | Signature | Returns |
|----------|-----------|---------|
| `shape_self_distance_matrix` | `(data, argvals, quotient="reparameterization", lambda_=0.0)` | `ndarray (n, n)` |
| `fregre_np` | `(dist_matrix, response, h=0.0)` | dict: `fitted_values`, `residuals`, `h_func`, `r_squared` |

## Pipeline 2 — shape-PC linear regression

Aligning to the shape mean removes phase variation; FPCA on the aligned curves then
yields *shape scores*. Regressing the response on these scores with `fregre_lm` gives an
interpretable linear model whose coefficient function lives in the shape space.

```python
import numpy as np
from fdars.alignment import shape_mean
from fdars.regression import fpca, fregre_lm

sm = shape_mean(X, t)
aligned = np.asarray(sm["aligned_data"])          # phase removed

lm_fit = fregre_lm(aligned, y, n_comp=4)          # FPC regression on shape
print(f"shape-PC R²: {lm_fit['r_squared']:.3f}")
```

The two figures below show the shape principal modes (how the aligned curves vary around
the shape mean) and the predicted-vs-actual scatter for the shape-PC model.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.alignment import shape_mean
from fdars.regression import fpca

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=30, argvals=t, n_basis=6, efun_type="fourier", seed=1))
sm = shape_mean(X, t)
aligned = np.asarray(sm["aligned_data"])
mean = np.asarray(sm["mean"])

pc = fpca(aligned, t, n_comp=3)
rot = np.asarray(pc["rotation"])            # (m, 3) shape modes
sv = np.asarray(pc["singular_values"])

f, ax = fig()
colors = ["#3f51b5", "#e8710a", "#198754"]
for k in range(3):
    scale = 1.5 * sv[k] / np.sqrt(len(X))
    ax.plot(t, mean + scale * rot[:, k], color=colors[k], lw=2,
            label=f"mean + PC{k+1}")
ax.plot(t, mean, color="#6c757d", lw=2.5, ls="--", label="shape mean")
ax.set(title="Shape principal modes of variation", xlabel="t", ylabel="X(t)")
ax.legend(fontsize=8)
print(render(f))
```

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.alignment import shape_mean, shape_self_distance_matrix
from fdars.regression import fregre_lm, fregre_np

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=30, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

aligned = np.asarray(shape_mean(X, t)["aligned_data"])
lm_fit = fregre_lm(aligned, y, n_comp=4)
yhat = np.asarray(lm_fit["fitted_values"])

D = np.asarray(shape_self_distance_matrix(X, t))
np_r2 = fregre_np(D, y, h=0.0)["r_squared"]

f, ax = fig()
ax.scatter(y, yhat, color="#3f51b5", s=32, alpha=0.85)
lim = [min(y.min(), yhat.min()), max(y.max(), yhat.max())]
ax.plot(lim, lim, color="#6c757d", ls="--", lw=1.5)
ax.set(title=f"Shape-PC fit (R² = {lm_fit['r_squared']:.2f}; shape-NP R² = {np_r2:.2f})",
       xlabel="observed y", ylabel="predicted y")
print(render(f))
```

!!! tip "Which pipeline?"
    Use the **distance-based** route (`fregre_np`) when the shape–response relationship is
    nonlinear or you already have a shape distance matrix from another analysis. Use the
    **shape-PC** route (`fpca` + `fregre_lm`) when you want an interpretable linear
    coefficient function and the response varies smoothly with a few dominant shape modes.

!!! note "Amplitude vs. phase"
    Scalar-on-shape regression discards phase by construction. If the *timing* of features
    carries signal — e.g. when a peak occurs, not just that it occurs — model amplitude and
    phase jointly instead, or predict from phase features directly. See
    [shape analysis](../align/shape-analysis.md) for the amplitude/phase decomposition.

## Related pages

- [Scalar-on-function regression](scalar-on-function.md) — amplitude-based predictors.
- [Robust regression](robust-regression.md) — outlier-resistant scalar-on-function fits.
- [Cross-validation](cross-validation.md) — choosing the number of shape components honestly.
