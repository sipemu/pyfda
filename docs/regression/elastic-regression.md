# Elastic Regression

Standard scalar-on-function regression assumes that the functional predictors are observed on a common time scale. When predictors exhibit **phase variability** (timing differences), the estimated $\beta(t)$ gets blurred and predictive accuracy suffers. Elastic regression solves this by jointly aligning the curves and estimating the regression model under the Fisher-Rao metric.

---

## Elastic scalar-on-function regression

The model simultaneously finds warping functions $\gamma_i$ and a coefficient function $\beta(t)$ such that:

$$
y_i = \alpha + \langle q_i \circ \gamma_i,\, \beta_q \rangle + \varepsilon_i
$$

where $q_i$ is the SRSF of the $i$-th predictor. This is phase-invariant: the prediction does not change if a predictor is time-warped.

```python
import numpy as np
from pyfda.alignment import elastic_regression

# --- Simulate data with phase variability ---
np.random.seed(42)
n, m = 80, 101
t = np.linspace(0, 1, m)

beta_true = np.sin(4 * np.pi * t)
data = np.zeros((n, m))
for i in range(n):
    shift = 0.08 * np.random.randn()
    t_warped = np.clip(t + shift * np.sin(np.pi * t), 0, 1)
    c = np.random.randn() * np.sin(2 * np.pi * t) + np.random.randn() * t
    data[i] = np.interp(t_warped, t, c)

response = np.trapz(data * beta_true, t, axis=1) + 0.5 * np.random.randn(n)

# --- Fit elastic regression ---
result = elastic_regression(
    data, t, response,
    ncomp_beta=10,  # basis dimension for beta
    lambda_=0.1,    # regularization on warping
    max_iter=20,
    tol=1e-4,
)

alpha    = result["alpha"]           # intercept
beta     = result["beta"]           # (m,) -- estimated beta(t) in aligned space
fitted   = result["fitted_values"]  # (n,)
resid    = result["residuals"]      # (n,)
sse      = result["sse"]            # sum of squared errors
r2       = result["r_squared"]      # R-squared
gammas   = result["gammas"]         # (n, m) -- estimated warping functions
n_iter   = result["n_iter"]         # iterations used

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
    Elastic regression typically outperforms `fregre_lm` when the predictors have substantial phase variability. If curves are already well-aligned, the two methods produce similar results but `fregre_lm` is faster.

---

## Elastic logistic regression

For binary classification under phase variability. The model jointly aligns curves and estimates the decision boundary.

$$
\log\frac{P(G=1 \mid x)}{P(G=0 \mid x)} = \alpha + \langle q \circ \gamma,\, \beta_q \rangle
$$

```python
import numpy as np
from pyfda.alignment import elastic_logistic

# --- Simulate two classes with phase variability ---
np.random.seed(7)
n, m = 100, 101
t = np.linspace(0, 1, m)

data = np.zeros((n, m))
labels = np.zeros(n, dtype=np.int64)

for i in range(n):
    shift = 0.06 * np.random.randn()
    t_warped = np.clip(t + shift * np.sin(np.pi * t), 0, 1)
    if i < n // 2:
        base = np.sin(2 * np.pi * t)
        labels[i] = 0
    else:
        base = np.cos(2 * np.pi * t)
        labels[i] = 1
    data[i] = np.interp(t_warped, t, base) + 0.2 * np.random.randn(m)

# --- Fit elastic logistic regression ---
result = elastic_logistic(
    data, t, labels,
    ncomp_beta=10,
    lambda_=0.1,
    max_iter=20,
    tol=1e-4,
)

probs     = result["probabilities"]      # (n,)
predicted = result["predicted_classes"]   # (n,)
accuracy  = result["accuracy"]           # scalar
beta      = result["beta"]              # (m,)
gammas    = result["gammas"]            # (n, m)
loss      = result["loss"]             # final loss value

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

## When to use elastic regression

| Scenario | Recommended method |
|----------|--------------------|
| Predictors are pre-aligned or have no phase variability | `fregre_lm`, `fregre_pls` |
| Predictors have moderate phase shifts | `elastic_regression` with small $\lambda$ |
| Predictors have large, nonlinear phase distortions | `elastic_regression` with moderate $\lambda$ |
| Binary classification with phase variability | `elastic_logistic` |
| Binary classification without phase variability | `functional_logistic`, `fclassif_lda` |

!!! warning "Computational cost"
    Elastic regression is significantly more expensive than standard functional regression because it jointly optimizes warping functions and regression coefficients at each iteration. For large datasets, consider pre-aligning with `karcher_mean` and then using `fregre_lm`.

---

## Full example: elastic vs. standard regression

```python
import numpy as np
from pyfda.regression import fregre_lm
from pyfda.alignment import elastic_regression, karcher_mean

np.random.seed(55)
n, m = 100, 101
t = np.linspace(0, 1, m)

# Generate curves with increasing phase variability
beta_true = np.exp(-((t - 0.5)**2) / 0.02)
data = np.zeros((n, m))
for i in range(n):
    shift = 0.12 * np.random.randn()  # substantial phase noise
    t_warped = np.clip(t + shift * np.sin(np.pi * t), 0, 1)
    c = np.random.randn() * np.sin(2 * np.pi * t) + np.random.randn() * t**2
    data[i] = np.interp(t_warped, t, c)

response = np.trapz(data * beta_true, t, axis=1) + 0.3 * np.random.randn(n)

# --- Standard FPC regression (no alignment) ---
lm_result = fregre_lm(data, response, n_comp=5)
print(f"Standard FPC R-squared: {lm_result['r_squared']:.4f}")

# --- Pre-align then regress ---
km = karcher_mean(data, t, lambda_=0.1)
lm_aligned = fregre_lm(km["aligned_data"], response, n_comp=5)
print(f"Align-then-regress R-squared: {lm_aligned['r_squared']:.4f}")

# --- Elastic regression (joint alignment + regression) ---
elastic = elastic_regression(data, t, response, ncomp_beta=10, lambda_=0.1)
print(f"Elastic regression R-squared: {elastic['r_squared']:.4f}")
```
