# Regression Diagnostics

A fitted regression summarizes the *average* relationship between predictor and response,
but a handful of unusual observations can dominate that summary. **Regression diagnostics**
identify which observations exert outsized influence on the fit, so you can decide whether
they are valuable signal or corrupting noise. In functional regression the same logic
applies to the FPC-score design: an observation can be a high-**leverage** point (unusual
predictor shape), a large-**residual** point (unusual response), or — most dangerously —
both, which makes it **influential**.

`fdars.explain` provides the standard diagnostic toolkit adapted to functional
scalar-on-function models: leverage and Cook's distance (`influence_diagnostics`), the
per-coefficient DFBETAS and per-fit DFFITS (`dfbetas_dffits`), and leave-one-out PRESS
(`loo_cv_press`).

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.explain import influence_diagnostics

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=36, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

# Inject one influential point: unusual response
y[5] += 4.0

diag = influence_diagnostics(X, y, ncomp=3)
lev = np.asarray(diag["leverage"])
cook = np.asarray(diag["cooks_distance"])

f, ax = fig()
ax.scatter(lev, cook, color="#3f51b5", s=36, alpha=0.85)
thr = 4 / len(y)                                  # common Cook's-D cutoff
flag = np.where(cook > thr)[0]
ax.scatter(lev[flag], cook[flag], color="#dc3545", s=70,
           edgecolor="k", zorder=3, label="flagged")
for i in flag:
    ax.annotate(str(i), (lev[i], cook[i]), fontsize=8,
                xytext=(4, 4), textcoords="offset points")
ax.axhline(thr, color="#6c757d", ls="--", lw=1, label=f"4/n = {thr:.3f}")
ax.set(title="Influence plot: Cook's distance vs. leverage",
       xlabel="leverage", ylabel="Cook's distance")
ax.legend()
print(render(f))
```

The injected point (index 5) jumps out as high Cook's distance — it moves the fit far more
than a typical observation.

## Concepts

Write the FPC-score regression in matrix form $y = Z\beta + \varepsilon$, where $Z$ stacks
the intercept and FPC scores. The **hat matrix** $H = Z(Z^\top Z)^{-1}Z^\top$ maps observed
to fitted values, $\hat y = Hy$. Its diagonal $h_{ii}$ is the **leverage** of observation
$i$ — how strongly its own response pulls its own fitted value. Leverage depends only on the
predictors; a curve with an unusual FPC-score profile has high leverage regardless of its
response.

**Cook's distance** combines leverage and residual size into a single influence measure —
how much all fitted values shift when observation $i$ is deleted:

$$
D_i = \frac{r_i^2}{p\,\hat\sigma^2}\cdot\frac{h_{ii}}{(1-h_{ii})^2},
$$

where $r_i$ is the residual, $p$ the number of parameters, and $\hat\sigma^2$ the residual
variance. A common rule flags $D_i > 4/n$. Two finer-grained measures localize the effect:
**DFFITS** measures the change in observation $i$'s own fitted value when it is deleted,
while **DFBETAS** measures the change in each *coefficient*, revealing *which* direction of
the model a point distorts.

## Leverage and Cook's distance — `influence_diagnostics`

```python
import numpy as np
from fdars.simulation import simulate
from fdars.explain import influence_diagnostics

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=36, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

diag = influence_diagnostics(X, y, ncomp=3)
high_lev = np.where(diag["leverage"] > 2 * diag["p"] / len(y))[0]
print(f"high-leverage indices: {high_lev.tolist()}")
```

| Return key | Type | Description |
|------------|------|-------------|
| `leverage` | `ndarray (n,)` | Hat-matrix diagonal $h_{ii}$ |
| `cooks_distance` | `ndarray (n,)` | Cook's distance $D_i$ |
| `p` | `float` | Number of model parameters (intercept + components) |
| `mse` | `float` | Residual mean squared error |

## DFBETAS and DFFITS — `dfbetas_dffits`

```python
from fdars.explain import dfbetas_dffits

infl = dfbetas_dffits(X, y, ncomp=3)
print("DFFITS cutoff:  ", round(infl["dffits_cutoff"], 3))
print("DFBETAS cutoff: ", round(infl["dfbetas_cutoff"], 3))
```

| Return key | Type | Description |
|------------|------|-------------|
| `dfbetas` | `ndarray (n, p)` | Per-coefficient influence of each observation |
| `dffits` | `ndarray (n,)` | Change in own fitted value when deleted |
| `studentized_residuals` | `ndarray (n,)` | Externally studentized residuals |
| `p` | `float` | Number of parameters |
| `dfbetas_cutoff` | `float` | $2/\sqrt{n}$ suggested threshold |
| `dffits_cutoff` | `float` | $2\sqrt{p/n}$ suggested threshold |

The studentized residuals against leverage give the second classic diagnostic view. Points
in the upper corners — large residual *and* high leverage — are the ones to scrutinize.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.explain import influence_diagnostics, dfbetas_dffits

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=36, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))
y[5] += 4.0                                       # same injected point

lev = np.asarray(influence_diagnostics(X, y, ncomp=3)["leverage"])
infl = dfbetas_dffits(X, y, ncomp=3)
sr = np.asarray(infl["studentized_residuals"])

f, ax = fig()
ax.scatter(lev, sr, color="#3f51b5", s=36, alpha=0.85)
ax.axhline(2, color="#6c757d", ls=":", lw=1)
ax.axhline(-2, color="#6c757d", ls=":", lw=1)
big = np.where(np.abs(sr) > 2)[0]
ax.scatter(lev[big], sr[big], color="#dc3545", s=70, edgecolor="k", zorder=3)
for i in big:
    ax.annotate(str(i), (lev[i], sr[i]), fontsize=8,
                xytext=(4, 4), textcoords="offset points")
ax.set(title="Studentized residual vs. leverage",
       xlabel="leverage", ylabel="studentized residual")
print(render(f))
```

## Leave-one-out PRESS — `loo_cv_press`

The **PRESS** statistic sums the squared leave-one-out residuals, and `loo_r_squared`
rescales it to an out-of-sample $R^2$. Unlike the training $R^2$, PRESS penalizes models
that fit any single point too tightly — an honest complement to the leverage plot.

```python
from fdars.explain import loo_cv_press

press = loo_cv_press(X, y, ncomp=3)
print(f"PRESS:        {press['press']:.3f}")
print(f"LOO R²:       {press['loo_r_squared']:.3f}")
```

| Return key | Type | Description |
|------------|------|-------------|
| `loo_residuals` | `ndarray (n,)` | Leave-one-out residuals |
| `press` | `float` | Predicted residual sum of squares |
| `loo_r_squared` | `float` | Out-of-sample $R^2$ from LOO residuals |
| `leverage` | `ndarray (n,)` | Hat-matrix diagonal |
| `tss` | `float` | Total sum of squares of the response |

!!! note "Flagging is not deleting"
    A flagged point is a point to *investigate*, not automatically remove. High influence may
    reflect a genuine, informative extreme observation. When influential points are truly
    contaminating, prefer a principled remedy — [robust regression](robust-regression.md)
    down-weights outliers without hand-deleting data.

!!! tip "Leverage vs. influence"
    High leverage alone is harmless if the point follows the trend (large $h_{ii}$, tiny
    Cook's $D$). It only becomes influential when paired with a large residual. Always read
    the two diagnostic plots together.

## Related pages

- [Robust regression](robust-regression.md) — fitting that resists the outliers found here.
- [Cross-validation](cross-validation.md) — fold-based honest error, the resampling analogue
  of PRESS.
- [Uncertainty quantification](uncertainty-quantification.md) — confidence bands on the
  coefficient function once influential points are handled.
