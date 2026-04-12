# Function-on-Scalar Regression

Function-on-scalar regression models a **functional response** $y_i(t)$ as a function of **scalar predictors** $x_{i1}, \dots, x_{ip}$:

$$
y_i(t) = \beta_0(t) + \sum_{j=1}^{p} x_{ij}\,\beta_j(t) + \varepsilon_i(t)
$$

Each coefficient function $\beta_j(t)$ describes how predictor $j$ influences the response curve at every time point $t$.

---

## Function-on-Scalar Regression (FOSR)

`fosr` fits the model pointwise (or with a roughness penalty) and returns coefficient functions, fitted curves, and residuals.

```python
import numpy as np
from pyfda import Fdata
from pyfda.regression import fosr

# --- Simulate data ---
np.random.seed(0)
n, m, p = 80, 101, 3
t = np.linspace(0, 1, m)

# Scalar predictors
predictors = np.random.randn(n, p)

# True coefficient functions
beta_true = np.zeros((p, m))
beta_true[0] = np.sin(2 * np.pi * t)          # predictor 1 effect
beta_true[1] = 0.5 * np.cos(4 * np.pi * t)    # predictor 2 effect
beta_true[2] = t * (1 - t)                     # predictor 3 effect

# Functional response
fd = Fdata(predictors @ beta_true + 0.2 * np.random.randn(n, m), argvals=t)

# --- Fit FOSR ---
result = fosr(fd.data, predictors, lambda_=-1.0)  # lambda < 0 => GCV selection

fitted    = result["fitted"]      # (n, m) -- fitted functional responses
beta_hat  = result["beta"]        # (p, m) -- estimated coefficient functions
residuals = result["residuals"]   # (n, m)
r2        = result["r_squared"]   # scalar

print(f"R-squared: {r2:.4f}")
print(f"Beta shape: {beta_hat.shape}")
```

| Key | Type | Description |
|-----|------|-------------|
| `fitted` | `ndarray (n, m)` | Fitted functional responses |
| `beta` | `ndarray (p, m)` | Estimated coefficient functions |
| `residuals` | `ndarray (n, m)` | Residual curves |
| `r_squared` | `float` | Global $R^2$ |

!!! tip "Roughness penalty"
    Set `lambda_=0.0` for ordinary least squares at each time point. Set `lambda_` to a positive value for a fixed penalty, or use a negative value (e.g., `lambda_=-1.0`) to trigger automatic GCV-based smoothing parameter selection.

### Interpreting coefficient functions

Each $\hat{\beta}_j(t)$ describes the effect of predictor $j$ on the response at time $t$:

- $\hat{\beta}_j(t) > 0$: increasing predictor $j$ raises the response at time $t$.
- $\hat{\beta}_j(t) < 0$: increasing predictor $j$ lowers the response at time $t$.
- $\hat{\beta}_j(t) \approx 0$: predictor $j$ has no effect at time $t$.

```python
# Check recovery of true coefficients
for j in range(p):
    corr = np.corrcoef(beta_true[j], beta_hat[j])[0, 1]
    print(f"  Predictor {j}: correlation with truth = {corr:.4f}")
```

---

## Functional ANOVA

**Functional ANOVA** tests whether group means differ across the domain. It is the functional analog of one-way ANOVA: the null hypothesis is that all $k$ group mean functions are equal.

$$
H_0: \mu_1(t) = \mu_2(t) = \cdots = \mu_k(t) \quad \text{for all } t \in \mathcal{T}
$$

A pointwise $F$-statistic $F(t)$ is computed at each $t$, and a permutation test yields an overall $p$-value.

```python
import numpy as np
from pyfda import Fdata
from pyfda.regression import fanova

# --- Simulate three groups ---
np.random.seed(1)
n_per_group = 30
m = 101
t = np.linspace(0, 1, m)

group_means = [
    np.sin(2 * np.pi * t),
    np.sin(2 * np.pi * t) + 0.5 * t,         # shifted group
    np.sin(2 * np.pi * t) - 0.3 * (1 - t),   # another shifted group
]

fd = Fdata(
    np.vstack([
        mean + 0.3 * np.random.randn(n_per_group, m)
        for mean in group_means
    ]),
    argvals=t,
)
groups = np.array([0]*n_per_group + [1]*n_per_group + [2]*n_per_group, dtype=np.int64)

# --- Run FANOVA ---
result = fanova(fd.data, groups, n_perm=999)

print(f"Global F-statistic: {result['global_statistic']:.4f}")
print(f"Permutation p-value: {result['p_value']:.4f}")
print(f"Group means shape: {result['group_means'].shape}")  # (3, 101)
print(f"Pointwise F(t) shape: {result['f_statistic_t'].shape}")  # (101,)
```

| Key | Type | Description |
|-----|------|-------------|
| `f_statistic_t` | `ndarray (m,)` | Pointwise $F$-statistic |
| `p_value` | `float` | Permutation-based $p$-value |
| `group_means` | `ndarray (k, m)` | Estimated group mean functions |
| `global_statistic` | `float` | Global (integrated) $F$-statistic |

!!! info "Permutation test"
    The `n_perm` parameter controls the number of random permutations. More permutations yield a more precise $p$-value but take longer. For publication-quality results, use `n_perm=4999` or higher.

---

## Full example: treatment effect on functional responses

```python
import numpy as np
from pyfda import Fdata
from pyfda.regression import fosr, fanova

np.random.seed(77)
n, m = 90, 121
t = np.linspace(0, 1, m)

# Two-group design: treatment (1) vs control (0)
treatment = np.array([0]*45 + [1]*45, dtype=np.int64)
predictors = treatment.reshape(-1, 1).astype(np.float64)

# True treatment effect peaks in the middle of the domain
effect = 2.0 * np.exp(-((t - 0.5)**2) / 0.02)

# Simulate response
raw = np.zeros((n, m))
for i in range(n):
    baseline = np.sin(2 * np.pi * t) + 0.5 * np.random.randn() * np.cos(np.pi * t)
    raw[i] = baseline + treatment[i] * effect + 0.4 * np.random.randn(m)
fd = Fdata(raw, argvals=t)

# --- FOSR: estimate the treatment effect curve ---
fosr_result = fosr(fd.data, predictors, lambda_=-1.0)
beta_treatment = fosr_result["beta"][0]  # estimated effect of treatment
print(f"FOSR R-squared: {fosr_result['r_squared']:.4f}")
print(f"Peak treatment effect at t={fd.argvals[np.argmax(beta_treatment)]:.2f}")

# --- FANOVA: test whether groups differ ---
fanova_result = fanova(fd.data, treatment, n_perm=999)
print(f"FANOVA p-value: {fanova_result['p_value']:.4f}")
if fanova_result["p_value"] < 0.05:
    print("Significant treatment effect detected.")
else:
    print("No significant treatment effect.")
```
