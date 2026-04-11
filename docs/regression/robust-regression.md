# Robust Regression

Standard FPC regression (`fregre_lm`) uses ordinary least squares, which is sensitive to outliers in the response. Robust regression methods replace the squared loss with loss functions that down-weight extreme residuals, yielding estimators that resist contamination.

`pyfda` provides two robust alternatives:

| Method | Loss function | Breakdown point | Notes |
|--------|--------------|-----------------|-------|
| **L1 regression** | $\lvert r \rvert$ | 50% | Median regression; completely ignores outlier magnitude |
| **Huber M-estimation** | Quadratic near 0, linear in tails | Depends on $k$ | Smooth compromise between L2 and L1 |

---

## L1 regression

**L1 (least absolute deviations)** regression minimizes $\sum_i |y_i - \hat{y}_i|$ instead of $\sum_i (y_i - \hat{y}_i)^2$. This is equivalent to estimating the conditional median rather than the conditional mean.

```python
import numpy as np
from pyfda.regression import fregre_l1

# --- Simulate data with outliers ---
np.random.seed(42)
n, m = 100, 81
t = np.linspace(0, 1, m)
beta_true = np.sin(4 * np.pi * t)

data = np.zeros((n, m))
for i in range(n):
    data[i] = (
        np.random.randn() * np.sin(2 * np.pi * t)
        + np.random.randn() * np.cos(2 * np.pi * t)
        + 0.2 * np.random.randn(m)
    )

response = np.trapz(data * beta_true, t, axis=1) + 0.3 * np.random.randn(n)

# Add 10% outliers
n_outliers = 10
outlier_idx = np.random.choice(n, n_outliers, replace=False)
response[outlier_idx] += 10 * np.random.randn(n_outliers)

# --- Fit L1 regression ---
result = fregre_l1(data, response, n_comp=3)

fitted  = result["fitted_values"]  # (n,)
resid   = result["residuals"]      # (n,)
beta_l1 = result["beta_t"]         # (m,) -- estimated beta(t)

print(f"L1 median absolute residual: {np.median(np.abs(resid)):.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `fitted_values` | `ndarray (n,)` | Fitted values |
| `residuals` | `ndarray (n,)` | Residuals |
| `beta_t` | `ndarray (m,)` | Estimated coefficient function |

---

## Huber M-estimation

**Huber regression** uses the Huber loss, which behaves like squared error for small residuals and like absolute error for large residuals:

$$
\rho_k(r) = \begin{cases}
\frac{1}{2} r^2 & \text{if } |r| \leq k \\
k|r| - \frac{1}{2} k^2 & \text{if } |r| > k
\end{cases}
$$

The tuning constant $k$ controls the transition point. The default $k = 1.345$ gives 95% efficiency relative to OLS when the errors are truly Gaussian.

```python
from pyfda.regression import fregre_huber

result = fregre_huber(data, response, n_comp=3, huber_k=1.345)

fitted     = result["fitted_values"]  # (n,)
resid      = result["residuals"]      # (n,)
beta_huber = result["beta_t"]         # (m,)

print(f"Huber median absolute residual: {np.median(np.abs(resid)):.4f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `fitted_values` | `ndarray (n,)` | Fitted values |
| `residuals` | `ndarray (n,)` | Residuals |
| `beta_t` | `ndarray (m,)` | Estimated coefficient function |

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_comp` | 3 | Number of FPC components |
| `huber_k` | 1.345 | Huber tuning constant |

!!! tip "Choosing `huber_k`"
    | `huber_k` | Behavior | Efficiency (Gaussian) |
    |-----------|----------|----------------------|
    | 0.5 | Very robust, low efficiency | ~60% |
    | 1.0 | Moderate robustness | ~89% |
    | 1.345 | Standard choice | ~95% |
    | 2.0 | Mild robustness | ~99% |
    | $\to \infty$ | Equivalent to OLS | 100% |

---

## Comparing OLS, L1, and Huber

```python
import numpy as np
from pyfda.regression import fregre_lm, fregre_l1, fregre_huber

np.random.seed(0)
n, m = 120, 101
t = np.linspace(0, 1, m)
beta_true = np.exp(-((t - 0.5)**2) / 0.02)

# Clean data
data = np.zeros((n, m))
for i in range(n):
    data[i] = sum(
        np.random.randn() * np.sin((2*k+1) * np.pi * t)
        for k in range(4)
    ) + 0.15 * np.random.randn(m)

response_clean = np.trapz(data * beta_true, t, axis=1) + 0.3 * np.random.randn(n)

# Contaminated response (15% outliers)
response = response_clean.copy()
contaminated = np.random.choice(n, int(0.15 * n), replace=False)
response[contaminated] += 8 * np.random.choice([-1, 1], size=len(contaminated))

# --- Fit all three ---
ols   = fregre_lm(data, response, n_comp=4)
l1    = fregre_l1(data, response, n_comp=4)
huber = fregre_huber(data, response, n_comp=4, huber_k=1.345)

# --- Evaluate beta recovery ---
corr_ols   = np.corrcoef(beta_true, ols["beta_t"])[0, 1]
corr_l1    = np.corrcoef(beta_true, l1["beta_t"])[0, 1]
corr_huber = np.corrcoef(beta_true, huber["beta_t"])[0, 1]

print("Beta(t) correlation with truth:")
print(f"  OLS:   {corr_ols:.4f}")
print(f"  L1:    {corr_l1:.4f}")
print(f"  Huber: {corr_huber:.4f}")

# --- Evaluate prediction on clean observations ---
clean_idx = np.setdiff1d(np.arange(n), contaminated)
for name, res in [("OLS", ols), ("L1", l1), ("Huber", huber)]:
    mse = np.mean((res["fitted_values"][clean_idx] - response_clean[clean_idx])**2)
    print(f"  {name:>5s} MSE (clean): {mse:.4f}")
```

---

## When to use robust methods

| Scenario | Recommendation |
|----------|---------------|
| Clean data, no outliers | `fregre_lm` (OLS) -- most efficient |
| Suspected outliers in response | `fregre_huber` with default $k=1.345$ |
| Known heavy contamination ($>10\%$) | `fregre_l1` |
| Outliers in predictors (leverage points) | Pre-filter with [outlier detection](../analyze/outlier-detection.md), then use any method |
| Heteroscedastic errors | `fregre_huber` with smaller $k$ (e.g., 1.0) |

!!! warning
    Robust methods protect against outliers in the **response** $y_i$. They do not guard against leverage points (outlying $x_i(t)$). For high-leverage outliers, consider depth-based trimming before fitting.
