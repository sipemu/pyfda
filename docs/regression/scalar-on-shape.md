# Scalar-on-Shape Regression

Ordinary [scalar-on-function regression](scalar-on-function.md) predicts a scalar
response from the *amplitude* of a curve — its value at each fixed $t$. But
sometimes the response depends on the curve's **shape**: the geometric pattern of
peaks and troughs, independent of how the curve is stretched or shifted along the
$t$-axis. Two curves that are warped versions of one another have the same shape
and, for a shape-driven response, should predict the same value.

Scalar-on-shape regression handles exactly this. We first quotient out warping
with the elastic (SRSF) machinery in `fdars.alignment`, then regress the response
on either a **shape distance matrix** (nonparametric) or **shape principal-component
scores** (linear). This page builds both pipelines on a seeded example.

!!! note "No single `scalar_on_shape` binding"
    The R package ships a purpose-built `scalar.on.shape()` estimator that jointly
    fits alignment and a penalised coefficient index. `fdars` for Python does not
    expose that one function; instead we compose the same idea from the shape
    primitives (`shape_mean`, `shape_self_distance_matrix`) plus the standard
    regressors. The results below are honest: the shape pipelines are competitive
    with, and often better than, naïve FPC regression on phase-variable data, but
    the margins depend on the problem.


![Scalar-on-Shape Regression — concept diagram](../assets/diagrams/scalar-on-shape.svg){ .fdars-diagram }

```python exec="1" html="1" source="above"
import numpy as np
from scipy.stats import beta as beta_dist
from docs_fig import fig, render
from fdars.alignment import shape_mean

def make_shape_data(seed, n=60, m=60):
    """Curves = phase-warped copies of a shape whose amplitude drives y."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    X = np.zeros((n, m)); y = np.zeros(n)
    for i in range(n):
        amp = rng.normal(0, 1)                              # shape signal
        base = amp * np.sin(2 * np.pi * t) + 0.4 * np.sin(4 * np.pi * t)
        a, b = rng.uniform(0.3, 3.0, size=2)               # phase nuisance
        gamma = beta_dist.cdf(t, a, b)
        X[i] = np.interp(gamma, t, base) + 0.05 * rng.standard_normal(m)
        y[i] = 2 * amp + rng.normal(0, 0.3)                # response from shape
    return t, X, y

t, X, y = make_shape_data(3)
sm = shape_mean(X, t)
mean = np.asarray(sm["mean"])
aligned = np.asarray(sm["aligned_data"])

f, (a0, a1) = fig(1, 2, figsize=(11, 4))
a0.plot(t, X[:20].T, color="#3f51b5", lw=0.8, alpha=0.4)
a0.set(title="Raw curves (phase-warped)", xlabel="t", ylabel="X(t)")
a1.plot(t, aligned.T, color="#198754", lw=0.8, alpha=0.4)
a1.plot(t, mean, color="#e8710a", lw=2.6, label="shape mean")
a1.set(title="After alignment to the shape mean", xlabel="t", ylabel="X(t)")
a1.legend()
print(render(f))
```

## Concepts

A functional observation $x(t)$ splits into an **amplitude** component (the shape
of the curve) and a **phase** component (a warping $\gamma$ of the $t$-axis). Two
curves $x_1, x_2$ share a shape when there is a warping $\gamma$ with
$x_1 \approx x_2 \circ \gamma$. The elastic (Fisher–Rao) framework makes this
precise through the square-root velocity function (SRVF); the resulting **shape
distance**

$$
d_{\text{shape}}(x_1, x_2) = \min_{\gamma}\;
  \big\lVert q_1 - (q_2 \circ \gamma)\sqrt{\dot\gamma}\big\rVert_2
$$

is invariant to warping. The scalar-on-shape model then assumes the response
depends on the curve *only through its shape*:

$$
y_i = g\!\left(\text{shape}(x_i)\right) + \varepsilon_i .
$$

We estimate $g$ in two ways. **(1) Distance-based (nonparametric):** feed the
pairwise shape-distance matrix into the Nadaraya–Watson kernel regressor
`fregre_np`, letting similar-shaped curves borrow strength. **(2) Shape-PC
(linear):** align all curves to the shape mean, run FPCA on the aligned curves to
obtain warping-invariant *shape scores*, and regress the response on those scores
with `fregre_lm`.

## Building the data

The predictor curves are phase-warped copies of a base shape whose amplitude
carries the signal; the response depends on that amplitude, not on the warping.
This is the regime where removing phase should help.

```python
import numpy as np
from scipy.stats import beta as beta_dist

def make_shape_data(seed, n=60, m=60):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    X = np.zeros((n, m)); y = np.zeros(n)
    for i in range(n):
        amp = rng.normal(0, 1)                              # shape signal
        base = amp * np.sin(2 * np.pi * t) + 0.4 * np.sin(4 * np.pi * t)
        a, b = rng.uniform(0.3, 3.0, size=2)               # phase nuisance
        gamma = beta_dist.cdf(t, a, b)
        X[i] = np.interp(gamma, t, base) + 0.05 * rng.standard_normal(m)
        y[i] = 2 * amp + rng.normal(0, 0.3)
    return t, X, y

t, X, y = make_shape_data(3)
```

## Pipeline 1 — distance-based shape regression

`shape_self_distance_matrix` computes the full $n \times n$ matrix of pairwise
shape distances. Passing it to `fregre_np` gives a kernel regression whose
geometry is defined by shape similarity, not pointwise amplitude.

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

Aligning to the shape mean removes phase variation; FPCA on the aligned curves
then yields *shape scores*. Regressing the response on these scores with
`fregre_lm` gives an interpretable linear model whose coefficient function lives
in the shape space.

```python
import numpy as np
from fdars.alignment import shape_mean
from fdars.regression import fregre_lm

sm = shape_mean(X, t)
aligned = np.asarray(sm["aligned_data"])          # phase removed

lm_fit = fregre_lm(aligned, y, n_comp=6)          # FPC regression on shape
print(f"shape-PC R²: {lm_fit['r_squared']:.3f}")
```

The two figures below show the shape principal modes (how the aligned curves vary
around the shape mean) and the predicted-vs-actual scatter for the shape-PC model.

```python exec="1" html="1"
import numpy as np
from scipy.stats import beta as beta_dist
from docs_fig import fig, render
from fdars.alignment import shape_mean
from fdars.regression import fpca

def make_shape_data(seed, n=60, m=60):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    X = np.zeros((n, m)); y = np.zeros(n)
    for i in range(n):
        amp = rng.normal(0, 1)
        base = amp * np.sin(2 * np.pi * t) + 0.4 * np.sin(4 * np.pi * t)
        a, b = rng.uniform(0.3, 3.0, size=2)
        gamma = beta_dist.cdf(t, a, b)
        X[i] = np.interp(gamma, t, base) + 0.05 * rng.standard_normal(m)
        y[i] = 2 * amp + rng.normal(0, 0.3)
    return t, X, y

t, X, y = make_shape_data(3)
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
from scipy.stats import beta as beta_dist
from docs_fig import fig, render
from fdars.alignment import shape_mean, shape_self_distance_matrix
from fdars.regression import fregre_lm, fregre_np

def make_shape_data(seed, n=60, m=60):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    X = np.zeros((n, m)); y = np.zeros(n)
    for i in range(n):
        amp = rng.normal(0, 1)
        base = amp * np.sin(2 * np.pi * t) + 0.4 * np.sin(4 * np.pi * t)
        a, b = rng.uniform(0.3, 3.0, size=2)
        gamma = beta_dist.cdf(t, a, b)
        X[i] = np.interp(gamma, t, base) + 0.05 * rng.standard_normal(m)
        y[i] = 2 * amp + rng.normal(0, 0.3)
    return t, X, y

t, X, y = make_shape_data(3)
aligned = np.asarray(shape_mean(X, t)["aligned_data"])
lm_fit = fregre_lm(aligned, y, n_comp=6)
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

## Comparison with naïve FPC regression

Does removing phase actually help? We compare the two shape pipelines against
plain `fregre_lm` on the *unaligned* curves, sweeping its component count. On this
phase-warped data the shape-PC route matches or beats naïve FPC regression while
using an interpretable low-rank shape representation; the distance-based route is
a nonparametric alternative that makes no linearity assumption.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.stats import beta as beta_dist
from docs_fig import fig, render
from fdars.alignment import shape_mean, shape_self_distance_matrix
from fdars.regression import fregre_lm, fregre_np

def make_shape_data(seed, n=60, m=60):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, m)
    X = np.zeros((n, m)); y = np.zeros(n)
    for i in range(n):
        amp = rng.normal(0, 1)
        base = amp * np.sin(2 * np.pi * t) + 0.4 * np.sin(4 * np.pi * t)
        a, b = rng.uniform(0.3, 3.0, size=2)
        gamma = beta_dist.cdf(t, a, b)
        X[i] = np.interp(gamma, t, base) + 0.05 * rng.standard_normal(m)
        y[i] = 2 * amp + rng.normal(0, 0.3)
    return t, X, y

t, X, y = make_shape_data(3)

ks = [2, 4, 6, 8, 10]
naive = [fregre_lm(X, y, n_comp=k)["r_squared"] for k in ks]

aligned = np.asarray(shape_mean(X, t)["aligned_data"])
shape_pc = fregre_lm(aligned, y, n_comp=6)["r_squared"]
D = np.asarray(shape_self_distance_matrix(X, t))
shape_np = fregre_np(D, y, h=0.0)["r_squared"]

f, ax = fig()
ax.plot(ks, naive, "-o", color="#3f51b5", label="naïve fregre_lm")
ax.axhline(shape_pc, color="#198754", ls="--", lw=2,
           label=f"shape-PC (R²={shape_pc:.2f})")
ax.axhline(shape_np, color="#e8710a", ls=":", lw=2,
           label=f"shape-NP (R²={shape_np:.2f})")
ax.set(title="Shape regression vs naïve FPC regression",
       xlabel="number of FPC components (naïve)", ylabel=r"$R^2$")
ax.legend(fontsize=8)
print(render(f))
```

!!! tip "Which pipeline?"
    Use the **distance-based** route (`fregre_np`) when the shape–response
    relationship is nonlinear or you already have a shape distance matrix from
    another analysis. Use the **shape-PC** route (`fpca` + `fregre_lm`) when you
    want an interpretable linear coefficient function and the response varies
    smoothly with a few dominant shape modes.

!!! note "Amplitude vs. phase"
    Scalar-on-shape regression discards phase by construction. If the *timing* of
    features carries signal — e.g. *when* a peak occurs, not just that it occurs —
    model amplitude and phase jointly instead
    ([elastic regression](elastic-regression.md)), or predict from phase features
    directly.

## Related pages

- [Scalar-on-function regression](scalar-on-function.md) — amplitude-based predictors.
- [Elastic regression](elastic-regression.md) — joint alignment + regression.
- [Cross-validation](cross-validation.md) — choosing the number of shape components honestly.
