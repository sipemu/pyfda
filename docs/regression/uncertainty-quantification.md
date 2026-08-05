# Uncertainty Quantification

A point estimate of the coefficient function $\hat\beta(t)$ or a single predicted response
$\hat y$ tells you *what* the model believes, but not *how much* to trust it. **Uncertainty
quantification** attaches error bars: a confidence band around $\beta(t)$ that shows where
the predictor genuinely drives the response, and prediction intervals around $\hat y$ that
bracket where a new observation is likely to fall.

`fdars` supports two complementary routes. **Bootstrapping** (`bootstrap_ci_fregre_lm`)
resamples the data to trace the sampling distribution of the whole coefficient function,
producing both pointwise and simultaneous bands. **Analytic prediction intervals**
(`fdars.explain.prediction_intervals`) propagate residual variance through the fitted model
to bracket new responses. Neither requires distributional assumptions beyond the model
itself — for *distribution-free* guarantees, see [conformal prediction](conformal-prediction.md).

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.regression import bootstrap_ci_fregre_lm

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=40, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

ci = bootstrap_ci_fregre_lm(X, y, n_comp=4, n_boot=200, alpha=0.05, seed=1)
center = np.asarray(ci["center"])
lo, hi = np.asarray(ci["lower"]), np.asarray(ci["upper"])
slo, shi = np.asarray(ci["sim_lower"]), np.asarray(ci["sim_upper"])

f, ax = fig()
ax.fill_between(t, slo, shi, color="#3f51b5", alpha=0.12, label="95% simultaneous")
ax.fill_between(t, lo, hi, color="#3f51b5", alpha=0.28, label="95% pointwise")
ax.plot(t, center, color="#3f51b5", lw=2, label=r"$\hat\beta(t)$")
ax.axhline(0, color="#6c757d", lw=1, ls=":")
ax.set(title="Bootstrap confidence band for the coefficient function",
       xlabel="t", ylabel=r"$\beta(t)$")
ax.legend(fontsize=8)
print(render(f))
```

Where the band excludes zero, the predictor's contribution at that $t$ is statistically
distinguishable from none — a functional analogue of a significant coefficient.

## Concepts

**Bootstrap confidence bands.** Refit the model on $B$ resamples of the data to obtain
$\hat\beta^{(1)}(t),\dots,\hat\beta^{(B)}(t)$. At each $t$, the $\alpha/2$ and $1-\alpha/2$
quantiles across the resamples give a **pointwise** band with $1-\alpha$ coverage *at every
fixed $t$*. But a pointwise band under-covers the *whole curve*: the chance that $\beta(t)$
falls inside the band at **all** $t$ simultaneously is well below $1-\alpha$. A
**simultaneous** band widens the interval by a common factor so that the entire true curve
lies inside with probability $1-\alpha$ — the honest choice when you want to make statements
about $\beta$ as a function.

**Prediction intervals.** For a new curve $x^*$, the predicted response
$\hat y^* = \hat\alpha + \int x^*(t)\hat\beta(t)\,dt$ carries two sources of error:
uncertainty in the estimated model and the irreducible noise $\varepsilon$. The prediction
interval

$$
\hat y^* \pm t_{n-p,\,1-\alpha/2}\,\hat\sigma\sqrt{1 + z^{*\top}(Z^\top Z)^{-1}z^*}
$$

accounts for both (the leading $1$ under the root is the noise term), and is therefore wider
than a confidence interval for the mean response.

## Bootstrap bands — `bootstrap_ci_fregre_lm`

```python
import numpy as np
from fdars.simulation import simulate
from fdars.regression import bootstrap_ci_fregre_lm

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=40, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

ci = bootstrap_ci_fregre_lm(X, y, n_comp=4, n_boot=200, alpha=0.05, seed=1)
width = np.asarray(ci["upper"]) - np.asarray(ci["lower"])
print(f"mean pointwise band width: {width.mean():.3f}")
print(f"successful bootstrap fits: {int(ci['n_boot_success'])}")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional predictors |
| `response` | `ndarray (n,)` | Scalar response |
| `n_comp` | `int` | Number of FPC components |
| `n_boot` | `int` | Bootstrap resamples (default 200) |
| `alpha` | `float` | Miscoverage level; $1-\alpha$ coverage |
| `seed` | `int` | Random seed |

| Return key | Type | Description |
|------------|------|-------------|
| `center` | `ndarray (m,)` | Point estimate $\hat\beta(t)$ |
| `lower`, `upper` | `ndarray (m,)` | Pointwise $1-\alpha$ band |
| `sim_lower`, `sim_upper` | `ndarray (m,)` | Simultaneous $1-\alpha$ band |
| `n_boot_success` | `float` | Number of resamples that fit successfully |

## Prediction intervals — `prediction_intervals`

Given held-out curves, `prediction_intervals` returns a bracketed prediction for each,
using the residual scale and design leverage of the *new* points.

```python
import numpy as np
from fdars.explain import prediction_intervals

# fit on the first 30, predict-with-intervals on the last 10
pi = prediction_intervals(X[:30], y[:30], X[30:], ncomp=4, confidence_level=0.95)
covered = np.mean((y[30:] >= pi["lower"]) & (y[30:] <= pi["upper"]))
print(f"empirical coverage on held-out: {covered:.2f}")
```

| Return key | Type | Description |
|------------|------|-------------|
| `predictions` | `ndarray (n_new,)` | Point predictions $\hat y^*$ |
| `lower`, `upper` | `ndarray (n_new,)` | Prediction interval bounds |
| `prediction_se` | `ndarray (n_new,)` | Standard error of each prediction |
| `confidence_level` | `float` | Nominal coverage |
| `t_critical` | `float` | $t$ quantile used |
| `residual_se` | `float` | Residual scale $\hat\sigma$ |

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.explain import prediction_intervals

np.random.seed(0)
t = np.linspace(0, 1, 60)
X = np.asarray(simulate(n=40, argvals=t, n_basis=6, efun_type="fourier", seed=1))
beta_true = np.sin(2 * np.pi * t)
y = np.trapezoid(X * beta_true, t, axis=1) + 0.3 * np.random.randn(len(X))

pi = prediction_intervals(X[:30], y[:30], X[30:], ncomp=4, confidence_level=0.95)
pred = np.asarray(pi["predictions"])
lo, hi = np.asarray(pi["lower"]), np.asarray(pi["upper"])
obs = y[30:]
order = np.argsort(pred)
idx = np.arange(len(pred))

f, ax = fig()
ax.errorbar(idx, pred[order], yerr=[pred[order] - lo[order], hi[order] - pred[order]],
            fmt="o", color="#3f51b5", ecolor="#3f51b5", elinewidth=1.5,
            capsize=3, label="95% prediction interval")
ax.scatter(idx, obs[order], color="#e8710a", s=45, zorder=3, label="observed")
ax.set(title="Prediction intervals on held-out curves",
       xlabel="held-out observation (sorted by prediction)", ylabel="y")
ax.legend(fontsize=8)
print(render(f))
```

!!! tip "Pointwise or simultaneous?"
    Use the **pointwise** band to ask "is $\beta$ nonzero *here*?" at a pre-specified $t$.
    Use the **simultaneous** band whenever you scan the whole curve for regions of
    significance — otherwise multiple-comparison inflation makes spurious excursions look
    real.

!!! note "Bootstrap vs. conformal"
    Bootstrap bands and analytic intervals are only as valid as the model and its noise
    assumptions. [Conformal prediction](conformal-prediction.md) instead wraps any fitted
    model in a calibration step that delivers **finite-sample, distribution-free** coverage —
    at the cost of holding out calibration data. The two are complementary: bootstrap for
    *interpreting* $\beta(t)$, conformal for *guaranteed* predictive coverage.

## Related pages

- [Conformal prediction](conformal-prediction.md) — distribution-free predictive intervals.
- [Regression diagnostics](regression-diagnostics.md) — check for influential points before
  trusting a band.
- [Scalar-on-function regression](scalar-on-function.md) — the underlying model being
  quantified.
