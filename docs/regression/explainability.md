# Model Explainability

After fitting a functional regression model, the natural question is: *why does the model make the predictions it does?* The explainability module provides tools to decompose, visualize, and interpret functional regression models at both the global and observation level.

---

## Permutation importance

**Permutation importance** measures how much the prediction error increases when a single FPC score is randomly shuffled. A large increase means that component carries important predictive information.

```python
import numpy as np
from pyfda.explain import fpc_permutation_importance

# --- Setup ---
np.random.seed(42)
n, m = 100, 81
t = np.linspace(0, 1, m)
beta_true = np.sin(4 * np.pi * t)

data = np.zeros((n, m))
for i in range(n):
    data[i] = (
        np.random.randn() * np.sin(2 * np.pi * t)
        + np.random.randn() * np.cos(2 * np.pi * t)
        + np.random.randn() * np.sin(4 * np.pi * t)
        + 0.2 * np.random.randn(m)
    )
response = np.trapz(data * beta_true, t, axis=1) + 0.3 * np.random.randn(n)

# --- Compute importance ---
result = fpc_permutation_importance(data, response, ncomp=5, n_perm=20, seed=42)

importance = result["importance"]        # (5,) -- importance per FPC
baseline   = result["baseline_metric"]   # baseline MSE
permuted   = result["permuted_metric"]   # (5,) -- MSE after permuting each FPC

print(f"Baseline MSE: {baseline:.4f}")
for i in range(5):
    print(f"  FPC {i+1}: importance = {importance[i]:.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `importance` | `ndarray (k,)` | Importance score for each FPC |
| `baseline_metric` | `float` | MSE of the unpermuted model |
| `permuted_metric` | `ndarray (k,)` | MSE after permuting each FPC |

!!! note
    The model is fit internally using `fregre_lm`. The importance scores reflect the marginal contribution of each FPC to the prediction accuracy.

---

## Partial dependence plots (PDP)

A **partial dependence plot** shows the marginal effect of a single FPC score on the prediction, averaging over the values of all other components.

```python
from pyfda.explain import functional_pdp

result = functional_pdp(data, response, ncomp=5, component=0, n_grid=50)

grid    = result["grid_values"]  # (50,) -- score values on the x-axis
pdp     = result["pdp_curve"]    # (50,) -- partial dependence on the y-axis
comp_id = result["component"]    # 0

print(f"PDP for FPC {comp_id + 1}:")
print(f"  Score range: [{grid.min():.2f}, {grid.max():.2f}]")
print(f"  PDP range:   [{pdp.min():.2f}, {pdp.max():.2f}]")
```

| Key | Type | Description |
|-----|------|-------------|
| `grid_values` | `ndarray (n_grid,)` | Grid of FPC score values |
| `pdp_curve` | `ndarray (n_grid,)` | Partial dependence values |
| `component` | `int` | Index of the FPC being analyzed |

!!! tip
    Generate PDPs for all components to identify which FPCs have linear vs. nonlinear relationships with the response. In a linear FPC model, all PDPs will be straight lines.

---

## SHAP values

**SHAP (SHapley Additive exPlanations)** values decompose each individual prediction into additive contributions from each FPC score.

$$
\hat{y}_i = \phi_0 + \sum_{j=1}^{k} \phi_{ij}
$$

where $\phi_0$ is the base value (mean prediction) and $\phi_{ij}$ is the SHAP value of FPC $j$ for observation $i$.

```python
from pyfda.explain import fpc_shap_values

result = fpc_shap_values(data, response, ncomp=5)

shap_vals  = result["values"]      # (n, 5) -- SHAP values per observation
base_value = result["base_value"]  # mean prediction

# For a single observation
i = 0
print(f"Observation {i}:")
print(f"  Prediction:  {base_value + shap_vals[i].sum():.4f}")
print(f"  Base value:  {base_value:.4f}")
for j in range(5):
    print(f"  FPC {j+1} SHAP: {shap_vals[i, j]:+.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `values` | `ndarray (n, k)` | SHAP values for each observation and FPC |
| `base_value` | `float` | Base value (mean prediction) |

### Global SHAP summary

Aggregate SHAP values across observations for a global view:

```python
# Mean absolute SHAP value per FPC (global importance)
mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
for j in range(5):
    print(f"FPC {j+1}: mean |SHAP| = {mean_abs_shap[j]:.4f}")
```

---

## Beta decomposition

The estimated coefficient function $\hat{\beta}(t)$ is a weighted sum of eigenfunctions. **Beta decomposition** shows the contribution of each eigenfunction (FPC) to $\hat{\beta}(t)$:

$$
\hat{\beta}(t) = \sum_{j=1}^{k} c_j \, \phi_j(t)
$$

```python
from pyfda.explain import beta_decomposition

result = beta_decomposition(data, response, ncomp=5)

components  = result["components"]           # list of 5 arrays, each (m,)
coefficients = result["coefficients"]        # (5,) -- the c_j values
var_prop    = result["variance_proportion"]  # (5,) -- proportion of beta variance

for j in range(5):
    print(f"FPC {j+1}: coef = {coefficients[j]:+.4f}, "
          f"var proportion = {var_prop[j]:.2%}")
```

| Key | Type | Description |
|-----|------|-------------|
| `components` | `list[ndarray]` | Each FPC's contribution to $\hat{\beta}(t)$, i.e., $c_j \phi_j(t)$ |
| `coefficients` | `ndarray (k,)` | Regression coefficients $c_j$ |
| `variance_proportion` | `ndarray (k,)` | Proportion of $\hat{\beta}$ variance attributable to each FPC |

---

## Significant regions

Identify the regions of the domain where $\beta(t)$ is significantly different from zero, based on confidence interval bounds.

```python
from pyfda.explain import significant_regions

# Assume you have bootstrap or asymptotic CI bounds for beta(t)
# Here we create simple illustrative bounds
from pyfda.regression import fregre_lm

fit = fregre_lm(data, response, n_comp=5)
beta_hat = fit["beta_t"]

# Approximate confidence bounds (illustrative)
se = 0.5 * np.ones(m)  # placeholder standard errors
lower = beta_hat - 1.96 * se
upper = beta_hat + 1.96 * se

regions = significant_regions(lower, upper)
print(f"Found {len(regions)} significant regions:")
for start, end, direction in regions:
    t_start = t[start] if start < len(t) else 1.0
    t_end = t[end] if end < len(t) else 1.0
    print(f"  t in [{t_start:.3f}, {t_end:.3f}]: {direction}")
```

Each region is a tuple `(start_idx, end_idx, direction)` where `direction` is `"positive"` or `"negative"`.

---

## Full example: explaining a functional regression model

```python
import numpy as np
from pyfda.regression import fregre_lm
from pyfda.explain import (
    fpc_permutation_importance,
    functional_pdp,
    fpc_shap_values,
    beta_decomposition,
)

np.random.seed(99)
n, m = 150, 101
t = np.linspace(0, 1, m)

# Beta that is significant only in [0.3, 0.7]
beta_true = np.where((t > 0.3) & (t < 0.7), np.sin(4 * np.pi * t), 0.0)

data = np.zeros((n, m))
for i in range(n):
    data[i] = sum(
        np.random.randn() * np.sin((2*k+1) * np.pi * t)
        for k in range(5)
    ) + 0.15 * np.random.randn(m)

response = np.trapz(data * beta_true, t, axis=1) + 0.2 * np.random.randn(n)

# --- Fit model ---
fit = fregre_lm(data, response, n_comp=5)
print(f"R-squared: {fit['r_squared']:.4f}")

# --- Permutation importance ---
imp = fpc_permutation_importance(data, response, ncomp=5, n_perm=30, seed=0)
print("\nPermutation importance:")
for j in range(5):
    print(f"  FPC {j+1}: {imp['importance'][j]:.4f}")

# --- SHAP ---
shap = fpc_shap_values(data, response, ncomp=5)
print(f"\nMean |SHAP| per FPC: {np.mean(np.abs(shap['values']), axis=0)}")

# --- Beta decomposition ---
decomp = beta_decomposition(data, response, ncomp=5)
print("\nBeta decomposition:")
for j in range(5):
    print(f"  FPC {j+1}: coef={decomp['coefficients'][j]:+.3f}, "
          f"var%={decomp['variance_proportion'][j]:.1%}")

# --- PDP for the most important component ---
most_important = int(np.argmax(imp["importance"]))
pdp = functional_pdp(data, response, ncomp=5, component=most_important, n_grid=40)
print(f"\nPDP for FPC {most_important + 1}:")
print(f"  Score range: [{pdp['grid_values'].min():.2f}, {pdp['grid_values'].max():.2f}]")
print(f"  PDP range:   [{pdp['pdp_curve'].min():.2f}, {pdp['pdp_curve'].max():.2f}]")
```
