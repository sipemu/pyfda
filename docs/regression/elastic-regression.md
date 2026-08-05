# Elastic Regression

Standard scalar-on-function regression assumes the functional predictors are
observed on a common, meaningful time scale. When curves carry **phase
variability** (differences in the *timing* of features), least-squares methods
blend amplitude and phase variation: the FPCs waste directions on the
misalignment, $\hat\beta(t)$ gets blurred, and predictive accuracy collapses.

Elastic regression fixes this by *jointly* estimating warping functions
$\gamma_i$ and a coefficient function $\beta(t)$ under the Fisher–Rao metric.
The model is fitted by alternating two steps:

1. **Alignment step** — fix $\beta$, update each $\gamma_i$ to reduce the
   residual, warping curves in the square-root-velocity (SRVF) domain.
2. **Regression step** — fix the warpings, re-estimate $\alpha$ and $\beta(t)$
   from the aligned curves.

The model is phase-invariant: the prediction is unchanged if a predictor is
time-warped.

$$
y_i = \alpha + \int_0^1 \tilde X_i(t)\,\beta(t)\,dt + \varepsilon_i,
\qquad \tilde X_i = X_i \circ \gamma_i .
$$

---

## When alignment actually matters

The key scenario is: **the response is driven by an amplitude feature, and phase
is pure nuisance.** The worked example below (ported from the R reference)
makes this precise. Every curve is a nonlinearly time-warped copy of one
template, scaled by a random amplitude perturbation $\delta_i$; the response
depends only on $\delta_i$:

$$
X_i(t) = (1 + 0.2\,\delta_i)\;\text{template}(\gamma_i(t)) + \text{noise},
\qquad y_i = 2\,\delta_i + \text{noise}.
$$

Because the informative signal ($\delta_i$) lives in amplitude while the
dominant *variance* is phase, ordinary FPC regression latches onto the warping
and fails. Elastic regression aligns the phase away and recovers the amplitude
signal.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.stats import beta as beta_dist
from docs_fig import fig, render
from fdars.regression import fregre_lm
from fdars.alignment import elastic_regression

rng = np.random.default_rng(42)
n, m = 60, 80
t = np.linspace(0, 1, m)

def template(s):
    return np.sin(2 * np.pi * s) + 0.3 * np.sin(6 * np.pi * s)

def random_warp(rng, t):
    # A nonlinear, monotone warp of [0,1] onto itself: a Beta CDF.
    a, b = rng.uniform(0.5, 2.0, size=2)
    return beta_dist.cdf(t, a, b)

X = np.zeros((n, m))
y = np.zeros(n)
for i in range(n):
    gamma = random_warp(rng, t)
    delta = rng.normal(0, 0.4)                      # amplitude signal
    X[i] = (1 + 0.2 * delta) * np.interp(gamma, t, template(t)) \
           + 0.1 * rng.standard_normal(m)
    y[i] = 2 * delta + rng.normal(0, 0.3)           # response depends on delta

lm = fregre_lm(X, y, n_comp=5)
el = elastic_regression(X, t, y, ncomp_beta=5, lambda_=0.01, max_iter=20, tol=1e-3)

f, (a0, a1) = fig(1, 2, figsize=(11, 4))
a0.plot(t, X[:20].T, color="#3f51b5", lw=0.7, alpha=0.4)
a0.set(title="Predictors: warped copies of one template", xlabel="t", ylabel="X(t)")

for name, res, c in [(f"standard FPC (R²={lm['r_squared']:.2f})", lm["fitted_values"], "#dc3545"),
                     (f"elastic (R²={el['r_squared']:.2f})", el["fitted_values"], "#198754")]:
    a1.scatter(y, np.asarray(res), s=26, alpha=0.75, color=c, label=name)
lim = [y.min(), y.max()]
a1.plot(lim, lim, color="#6c757d", ls="--", lw=1.5)
a1.set(title="Observed vs fitted", xlabel="observed y", ylabel="fitted y")
a1.legend(fontsize=8)
print(render(f))
```

Standard FPC regression explains almost none of the response, while elastic
regression recovers it: the misalignment that dominated the raw curves is
removed before fitting.

---

## Elastic scalar-on-function regression

`elastic_regression(data, argvals, response, ...)` fits the joint model and
returns the intercept, aligned coefficient function, fit statistics, and the
estimated warping functions.

```python
import numpy as np
from scipy.stats import beta as beta_dist
from fdars import Fdata
from fdars.alignment import elastic_regression

# --- Simulate warped template + amplitude-driven response ---
rng = np.random.default_rng(42)
n, m = 60, 80
t = np.linspace(0, 1, m)

def template(s):
    return np.sin(2 * np.pi * s) + 0.3 * np.sin(6 * np.pi * s)

def random_warp(rng, t):
    a, b = rng.uniform(0.5, 2.0, size=2)       # Beta-CDF warp of [0,1]
    return beta_dist.cdf(t, a, b)

raw = np.zeros((n, m))
response = np.zeros(n)
for i in range(n):
    gamma = random_warp(rng, t)
    delta = rng.normal(0, 0.4)
    raw[i] = (1 + 0.2 * delta) * np.interp(gamma, t, template(t)) \
             + 0.1 * rng.standard_normal(m)
    response[i] = 2 * delta + rng.normal(0, 0.3)
fd = Fdata(raw, argvals=t)

# --- Fit elastic regression ---
result = elastic_regression(
    fd.data, fd.argvals, response,
    ncomp_beta=5,   # basis dimension for beta
    lambda_=0.01,   # regularization on warping
    max_iter=20,
    tol=1e-3,
)

alpha    = result["alpha"]           # intercept
beta     = result["beta"]            # (m,) -- estimated beta(t) in aligned space
fitted   = result["fitted_values"]   # (n,)
resid    = result["residuals"]       # (n,)
sse      = result["sse"]             # sum of squared errors
r2       = result["r_squared"]       # R-squared
gammas   = result["gammas"]          # (n, m) -- estimated warping functions
n_iter   = result["n_iter"]          # iterations used

print(f"R-squared:  {r2:.4f}")
print(f"Iterations: {n_iter}")
```

| Key | Type | Description |
|-----|------|-------------|
| `alpha` | `float` | Intercept |
| `beta` | `ndarray (m,)` | Estimated coefficient function |
| `fitted_values` | `ndarray (n,)` | Predicted response |
| `residuals` | `ndarray (n,)` | Residuals |
| `sse` | `float` | Sum of squared errors |
| `r_squared` | `float` | Coefficient of determination |
| `gammas` | `ndarray (n, m)` | Estimated warping functions |
| `n_iter` | `int` | Number of iterations |

!!! info "Comparison with standard regression"
    Elastic regression outperforms `fregre_lm` when the predictors carry
    substantial phase variability. If curves are already well aligned, the two
    give similar results and `fregre_lm` is much faster.

---

## Elastic logistic regression

For binary classification under phase variability. The model jointly aligns the
curves and estimates the decision boundary in the aligned (SRVF) domain:

$$
\log\frac{P(G=1 \mid x)}{P(G=0 \mid x)} = \alpha + \int_0^1 \tilde X(t)\,\beta(t)\,dt .
$$

Continuing the example above, we threshold the response at its median to make a
binary label. Elastic logistic recovers the classes with high accuracy because
the amplitude sign that determines the label survives alignment, while the phase
nuisance is removed.

```python
import numpy as np
from fdars.alignment import elastic_logistic

labels = (response > np.median(response)).astype(np.int64)

result = elastic_logistic(
    fd.data, fd.argvals, labels,
    ncomp_beta=5,
    lambda_=0.01,
    max_iter=15,
    tol=1e-3,
)

probs     = result["probabilities"]       # (n,)
predicted = result["predicted_classes"]   # (n,)
accuracy  = result["accuracy"]            # scalar
beta      = result["beta"]                # (m,)
gammas    = result["gammas"]              # (n, m)
loss      = result["loss"]                # final loss value

print(f"Accuracy:   {accuracy:.2%}")
print(f"Final loss: {loss:.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `alpha` | `float` | Intercept |
| `beta` | `ndarray (m,)` | Coefficient function |
| `probabilities` | `ndarray (n,)` | Predicted class probabilities |
| `predicted_classes` | `ndarray (n,)` | Predicted labels |
| `accuracy` | `float` | Classification accuracy |
| `loss` | `float` | Final logistic loss |
| `gammas` | `ndarray (n, m)` | Estimated warping functions |
| `n_iter` | `int` | Number of iterations |

---

## Align-then-regress: a cheaper alternative

Joint estimation is expensive. A pragmatic middle ground is to align the curves
once with `karcher_mean` (which returns `aligned_data`) and feed the aligned
curves into ordinary `fregre_lm`. Both alignment strategies dramatically beat the
unaligned baseline; which of the two wins depends on the data — align-then-regress
is a fast, strong default, while joint elastic optimisation lets the response
guide the warping.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.stats import beta as beta_dist
from docs_fig import fig, render
from fdars.regression import fregre_lm
from fdars.alignment import elastic_regression, karcher_mean

rng = np.random.default_rng(42)
n, m = 60, 80
t = np.linspace(0, 1, m)

def template(s):
    return np.sin(2 * np.pi * s) + 0.3 * np.sin(6 * np.pi * s)

def random_warp(rng, t):
    a, b = rng.uniform(0.5, 2.0, size=2)
    return beta_dist.cdf(t, a, b)

X = np.zeros((n, m)); y = np.zeros(n)
for i in range(n):
    gamma = random_warp(rng, t)
    delta = rng.normal(0, 0.4)
    X[i] = (1 + 0.2 * delta) * np.interp(gamma, t, template(t)) \
           + 0.1 * rng.standard_normal(m)
    y[i] = 2 * delta + rng.normal(0, 0.3)

r_std = fregre_lm(X, y, n_comp=5)["r_squared"]
km = karcher_mean(X, t, lambda_=0.01)
r_align = fregre_lm(np.asarray(km["aligned_data"]), y, n_comp=5)["r_squared"]
r_elastic = elastic_regression(X, t, y, ncomp_beta=5, lambda_=0.01)["r_squared"]

methods = ["standard\nfregre_lm", "align-then\n-regress", "elastic\nregression"]
r2s = [r_std, r_align, r_elastic]

f, ax = fig()
ax.bar(methods, r2s, color=["#dc3545", "#e8710a", "#198754"], alpha=0.85)
for i, v in enumerate(r2s):
    ax.text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=10)
ax.set(title="R² by alignment strategy", ylabel=r"$R^2$", ylim=(0, 1))
print(render(f))
```

---

## When to use elastic regression

| Scenario | Recommended method |
|----------|--------------------|
| Predictors pre-aligned / no phase variability | `fregre_lm`, `fregre_pls` |
| Moderate phase shifts | `elastic_regression` with small $\lambda$ |
| Large, nonlinear phase distortions | `elastic_regression` with moderate $\lambda$ |
| Fast approximation for large $n$ | align with `karcher_mean`, then `fregre_lm` |
| Binary classification with phase variability | `elastic_logistic` |
| Binary classification without phase variability | `functional_logistic`, `fclassif_lda` |

!!! warning "Computational cost"
    Elastic regression is far more expensive than standard functional regression
    because it re-optimises the warping functions at every iteration. For large
    datasets, pre-align once with `karcher_mean` and use `fregre_lm`.

!!! note "Elastic PCR and amplitude/phase attribution (R-only)"
    The R reference additionally documents `elastic.pcr` (regression on vertical,
    horizontal, or joint elastic-FPCA scores) and `elastic.attribution`
    (permutation importance of amplitude vs. phase). There is no single packaged
    `fdars` Python binding for either. You can assemble the PCR variants from the
    elastic-FPCA primitives in `fdars.alignment` — `vert_fpca`, `horiz_fpca`, and
    `joint_fpca` — and regress the resulting scores yourself; and
    `fdars.conformal.conformal_elastic_pcr` provides an elastic-PCR *conformal
    prediction* routine. These are documented on their own pages rather than
    duplicated here.

## References

- Srivastava & Klassen (2016), *Functional and Shape Data Analysis*, Springer.
- Tucker, Wu & Srivastava (2013), Generative models for functional data using
  phase and amplitude separation, *Comput. Stat. Data Anal.* 61, 50–66.
