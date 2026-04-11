# Scalar-on-Function Regression

Scalar-on-function regression predicts a scalar response $y_i$ from a functional predictor $x_i(t)$:

$$
y_i = \alpha + \int_{\mathcal{T}} x_i(t)\,\beta(t)\,dt + \varepsilon_i
$$

The coefficient function $\beta(t)$ reveals *which regions* of the functional predictor drive the response. `pyfda` provides five complementary approaches to estimate this model.

---

## 1. FPC regression

The most common approach: project the functional predictors onto their principal components, then regress the response on the FPC scores.

```python
import numpy as np
from pyfda.regression import fregre_lm

# Simulate data
np.random.seed(42)
n, m = 100, 81
t = np.linspace(0, 1, m)
beta_true = np.sin(4 * np.pi * t)

# Generate functional predictors (smooth random curves)
data = np.zeros((n, m))
for i in range(n):
    data[i] = (
        np.random.randn() * np.sin(2 * np.pi * t)
        + np.random.randn() * np.cos(2 * np.pi * t)
        + np.random.randn() * np.sin(4 * np.pi * t)
        + 0.3 * np.random.randn(m)
    )

# Scalar response = integral of data * beta + noise
response = np.trapz(data * beta_true, t, axis=1) + 0.5 * np.random.randn(n)

# Fit the model
result = fregre_lm(data, response, n_comp=3)

fitted   = result["fitted_values"]   # (n,)
resid    = result["residuals"]       # (n,)
beta_hat = result["beta_t"]          # (m,) -- estimated beta(t)
r2       = result["r_squared"]       # scalar
coefs    = result["coefficients"]    # FPC coefficients
intercept = result["intercept"]      # scalar

print(f"R-squared: {r2:.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `fitted_values` | `ndarray (n,)` | Predicted response values |
| `residuals` | `ndarray (n,)` | Residuals $y - \hat{y}$ |
| `beta_t` | `ndarray (m,)` | Estimated coefficient function $\hat{\beta}(t)$ |
| `r_squared` | `float` | Coefficient of determination |
| `coefficients` | `ndarray (k,)` | Regression coefficients on FPC scores |
| `intercept` | `float` | Intercept $\hat{\alpha}$ |

!!! note "Number of components"
    The choice of `n_comp` controls the bias-variance trade-off. Too few components under-fit; too many over-fit. Use `model_selection_ncomp` (below) for automatic selection.

---

## 2. PLS regression

**Partial Least Squares** finds components that maximize the covariance between the functional predictor and the response, often performing better than FPCA when the dominant modes of variation are not the most predictive.

```python
from pyfda.regression import fregre_pls

result = fregre_pls(data, t, response, n_comp=3)

print(f"PLS R-squared: {result['r_squared']:.4f}")
print(f"Beta shape:    {result['beta_t'].shape}")
```

| Key | Type | Description |
|-----|------|-------------|
| `fitted_values` | `ndarray (n,)` | Fitted values |
| `residuals` | `ndarray (n,)` | Residuals |
| `beta_t` | `ndarray (m,)` | PLS coefficient function |
| `r_squared` | `float` | $R^2$ |

!!! tip "PLS vs. FPC regression"
    PLS is preferable when the response depends on modes of variation with small eigenvalues. FPC regression may miss these because FPCA is unsupervised.

---

## 3. Nonparametric regression

When the relationship between $x(t)$ and $y$ is nonlinear, use **kernel regression** based on a pre-computed distance matrix. This avoids any linearity assumption.

```python
from pyfda.regression import fregre_np
from pyfda.metric import lp_self_distance_matrix

# Compute L2 distance matrix
D = lp_self_distance_matrix(data, t, p=2.0)

result = fregre_np(D, response, h=0.0)  # h=0.0 -> automatic bandwidth

print(f"NP R-squared: {result['r_squared']:.4f}")
print(f"Bandwidth:    {result['h_func']:.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `fitted_values` | `ndarray (n,)` | Fitted values |
| `residuals` | `ndarray (n,)` | Residuals |
| `h_func` | `float` | Selected or user-specified bandwidth |
| `r_squared` | `float` | $R^2$ |

!!! info "Distance choice matters"
    The distance metric used to build `D` determines the geometry of the regression. Try $L^2$, elastic, or DTW distances depending on the application.

---

## 4. Model selection

Automatically select the optimal number of FPC components using **GCV**, **AIC**, or **BIC**.

```python
from pyfda.regression import model_selection_ncomp

result = model_selection_ncomp(data, response, max_comp=10, criterion="gcv")

best_k = result["best_ncomp"]
print(f"Best number of components: {best_k}")

# Inspect all criteria
for ncomp, aic, bic, gcv in result["criteria"]:
    print(f"  k={ncomp}: AIC={aic:.2f}, BIC={bic:.2f}, GCV={gcv:.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `best_ncomp` | `int` | Optimal number of components |
| `criteria` | `list[tuple]` | `(ncomp, AIC, BIC, GCV)` for each $k$ tested |

---

## 5. FPCA-then-regression pattern

For maximum control, run FPCA explicitly and feed the scores into your own regression pipeline.

```python
from pyfda.regression import fpca
import numpy as np

# Step 1: FPCA
pca = fpca(data, t, n_comp=5)
scores   = pca["scores"]       # (n, 5)
rotation = pca["rotation"]     # (m, 5)
mean_fn  = pca["mean"]         # (m,)

# Step 2: OLS on the scores (using numpy)
X = np.column_stack([np.ones(n), scores])
beta_hat = np.linalg.lstsq(X, response, rcond=None)[0]
fitted = X @ beta_hat
r2 = 1 - np.sum((response - fitted)**2) / np.sum((response - response.mean())**2)
print(f"Manual FPC regression R-squared: {r2:.4f}")

# Step 3: Reconstruct beta(t) in function space
beta_t = rotation @ beta_hat[1:]
```

---

## Full example: predicting material strength from stress curves

```python
import numpy as np
from pyfda.regression import fregre_lm, fregre_pls, fregre_np, model_selection_ncomp
from pyfda.metric import lp_self_distance_matrix

# --- Simulate stress-strain curves and tensile strength ---
np.random.seed(99)
n, m = 120, 101
t = np.linspace(0, 1, m)

# True coefficient: tensile strength depends on the late-stage behavior
beta_true = np.where(t > 0.6, 5 * (t - 0.6), 0.0)

data = np.zeros((n, m))
for i in range(n):
    c1, c2, c3 = np.random.randn(3)
    data[i] = c1 * t + c2 * t**2 + c3 * np.sin(np.pi * t) + 0.2 * np.random.randn(m)

response = np.trapz(data * beta_true, t, axis=1) + 0.3 * np.random.randn(n)

# --- Model selection ---
sel = model_selection_ncomp(data, response, max_comp=8, criterion="gcv")
print(f"Optimal components: {sel['best_ncomp']}")

# --- FPC regression ---
lm_result = fregre_lm(data, response, n_comp=sel["best_ncomp"])
print(f"FPC R-squared:  {lm_result['r_squared']:.4f}")

# --- PLS regression ---
pls_result = fregre_pls(data, t, response, n_comp=sel["best_ncomp"])
print(f"PLS R-squared:  {pls_result['r_squared']:.4f}")

# --- Nonparametric regression ---
D = lp_self_distance_matrix(data, t, p=2.0)
np_result = fregre_np(D, response)
print(f"NP  R-squared:  {np_result['r_squared']:.4f}")
print(f"NP  bandwidth:  {np_result['h_func']:.4f}")

# --- Compare beta estimates ---
print(f"\nBeta(t) correlation with truth:")
print(f"  FPC: {np.corrcoef(beta_true, lm_result['beta_t'])[0,1]:.4f}")
print(f"  PLS: {np.corrcoef(beta_true, pls_result['beta_t'])[0,1]:.4f}")
```
