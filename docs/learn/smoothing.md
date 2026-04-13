---
title: Smoothing
---

# Smoothing

Real-world curves are almost always corrupted by noise. Smoothing recovers the
underlying signal while respecting the functional nature of the data. fdars
provides two families of smoothers:

1. **Nonparametric kernel smoothers** (`fdars.smoothing`) -- Nadaraya-Watson,
   local linear, local polynomial, and k-NN.
2. **Basis smoothers** (`fdars.basis`) -- project noisy curves onto a smooth
   basis (B-spline or Fourier) with a roughness penalty.

This guide covers both, including automatic bandwidth and penalty selection.

---

## Setup: Noisy Curves

We start by simulating a clean signal and adding Gaussian noise:

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate

# Clean signal
argvals = np.linspace(0, 1, 200)
clean = simulate(n=1, argvals=argvals, n_basis=5, seed=42)
fd_clean = Fdata(clean, argvals=argvals)

# Add noise
rng = np.random.default_rng(0)
noise = rng.normal(0, 0.3, size=clean.shape)
fd_noisy = fd_clean + noise

# Extract single curve for 1D smoothing
x = fd_noisy.argvals
y = fd_noisy.data[0]
y_true = fd_clean.data[0]
```

---

## Nadaraya-Watson Kernel Smoother

The Nadaraya-Watson estimator computes a locally weighted average:

$$
\hat{m}(t) = \frac{\sum_{i=1}^{n} K_h(t - x_i)\, y_i}{\sum_{i=1}^{n} K_h(t - x_i)}
$$

where $K_h$ is a kernel function with bandwidth $h$.

```python
from fdars.smoothing import nadaraya_watson

y_hat = nadaraya_watson(x, y, x, bandwidth=0.05, kernel="gaussian")
```

### Available Kernels

| Kernel | `kernel=` | Shape |
|--------|-----------|-------|
| Gaussian | `"gaussian"` | $K(u) = \frac{1}{\sqrt{2\pi}} e^{-u^2/2}$ |
| Epanechnikov | `"epanechnikov"` | $K(u) = \frac{3}{4}(1 - u^2)_+$ |
| Tricube | `"tricube"` | $K(u) = \frac{70}{81}(1 - |u|^3)^3_+$ |

```python
y_gauss = nadaraya_watson(x, y, x, bandwidth=0.05, kernel="gaussian")
y_epan  = nadaraya_watson(x, y, x, bandwidth=0.05, kernel="epanechnikov")
y_tri   = nadaraya_watson(x, y, x, bandwidth=0.05, kernel="tricube")
```

!!! tip "Kernel choice"
    In practice, the bandwidth matters far more than the kernel shape. The
    Gaussian kernel is a safe default. Epanechnikov is theoretically optimal in
    terms of MSE efficiency.

---

## Local Linear Regression

The Nadaraya-Watson estimator can suffer from boundary bias. **Local linear
regression** fits a weighted least-squares line at each point, which
automatically corrects for boundary effects.

```python
from fdars.smoothing import local_linear

y_ll = local_linear(x, y, x, bandwidth=0.05, kernel="gaussian")
```

The interface is identical to `nadaraya_watson` -- same kernel options, same
bandwidth parameter.

!!! info "When to prefer local linear"
    If your data has curvature near the domain boundaries (e.g., $t = 0$ or
    $t = 1$), local linear will usually give better fits than Nadaraya-Watson.

---

## Local Polynomial Regression

Generalize local linear to higher polynomial degrees:

```python
from fdars.smoothing import local_polynomial

# Degree 0 = Nadaraya-Watson
y_d0 = local_polynomial(x, y, x, bandwidth=0.05, degree=0)

# Degree 1 = local linear
y_d1 = local_polynomial(x, y, x, bandwidth=0.05, degree=1)

# Degree 2 = local quadratic (useful for estimating derivatives)
y_d2 = local_polynomial(x, y, x, bandwidth=0.05, degree=2)

# Degree 3 = local cubic
y_d3 = local_polynomial(x, y, x, bandwidth=0.05, degree=3)
```

!!! warning "Higher degrees need wider bandwidths"
    Increasing `degree` adds flexibility, which can amplify noise. Compensate by
    using a slightly larger bandwidth or selecting it via cross-validation.

---

## k-Nearest Neighbors Smoother

Instead of a global bandwidth, the k-NN smoother adapts locally by averaging the
`k` nearest observations to each evaluation point:

```python
from fdars.smoothing import knn_smoother

y_knn = knn_smoother(x, y, x, k=15)
```

The effective bandwidth grows in sparse regions and shrinks in dense regions.

!!! tip "Choosing k"
    Typical values are $k \in [5, 30]$ for $n \approx 200$. Larger `k` produces
    smoother curves; smaller `k` follows local features more closely.

---

## Bandwidth Selection via Cross-Validation

Choosing the bandwidth $h$ is the most important decision in kernel smoothing.
fdars automates this with `optim_bandwidth`, which searches over a grid and
minimizes either cross-validation (CV) or generalized cross-validation (GCV).

### Generalized Cross-Validation (default)

```python
from fdars.smoothing import optim_bandwidth

result = optim_bandwidth(x, y, criterion="gcv", kernel="gaussian")
print(f"Optimal bandwidth: {result['h_opt']:.4f}")
print(f"GCV score:         {result['value']:.6f}")

# Now smooth with the optimal bandwidth
y_opt = nadaraya_watson(x, y, x, bandwidth=result["h_opt"])
```

### Leave-One-Out Cross-Validation

```python
result_cv = optim_bandwidth(x, y, criterion="cv", kernel="gaussian")
print(f"Optimal bandwidth (CV): {result_cv['h_opt']:.4f}")
```

### Controlling the Search Grid

```python
result_fine = optim_bandwidth(
    x, y,
    criterion="gcv",
    kernel="gaussian",
    n_grid=100,       # finer search grid
    h_min=0.01,       # lower bound
    h_max=0.5,        # upper bound
)
```

!!! info "GCV vs CV"
    GCV is an algebraic approximation to leave-one-out CV that avoids
    refitting the model $n$ times. It is faster and usually gives similar
    results.

---

## Basis Smoothing

An alternative to kernel methods is to represent each curve as a linear
combination of smooth basis functions and add a roughness penalty to prevent
overfitting. This is often called **penalized regression splines** or
**P-spline** smoothing.

### Smooth Basis with GCV

`smooth_basis_gcv` fits a basis expansion and automatically selects the
smoothing penalty $\lambda$ by GCV:

```python
from fdars.basis import smooth_basis_gcv

# Smooth all curves in a dataset at once
result = smooth_basis_gcv(
    fd_noisy.data,       # (n_obs, n_points) array
    fd_noisy.argvals,
    n_basis=20,          # number of B-spline basis functions
    basis_type="bspline",
    lfd_order=2,         # penalize second derivative (curvature)
)

fitted = result["fitted"]        # (n_obs, n_points) smoothed curves
coeffs = result["coefficients"]  # (n_obs, n_basis) basis coefficients
fd_fitted = Fdata(fitted, argvals=fd_noisy.argvals)
print(f"Effective df: {result['edf']:.2f}")
print(f"GCV score:    {result['gcv']:.6f}")
```

!!! tip "Choosing `n_basis`"
    For B-splines, a rule of thumb is `n_basis ~ n_points / 5` to `n_points / 4`.
    The penalty $\lambda$ will prevent overfitting even with many basis functions.

### Fourier Basis

For periodic data, use a Fourier basis:

```python
result_fourier = smooth_basis_gcv(
    fd_noisy.data, fd_noisy.argvals,
    n_basis=15,
    basis_type="fourier",
    lfd_order=2,
)
fd_fourier = Fdata(result_fourier["fitted"], argvals=fd_noisy.argvals)
```

### P-Spline Fit with Known Penalty

If you already know a good $\lambda$, skip the GCV search:

```python
from fdars.basis import pspline_fit_1d

result_ps = pspline_fit_1d(
    fd_noisy.data, fd_noisy.argvals,
    n_basis=20,
    lambda_=0.01,       # fixed smoothing parameter
    order=2,            # second-order difference penalty
)

print(f"RSS: {result_ps['rss']:.4f}")
print(f"AIC: {result_ps['aic']:.2f}")
print(f"BIC: {result_ps['bic']:.2f}")
```

### P-Spline Fit with GCV-Selected Penalty

```python
from fdars.basis import pspline_fit_gcv

result_auto = pspline_fit_gcv(fd_noisy.data, fd_noisy.argvals, n_basis=20, order=2)
print(f"Selected lambda -> GCV = {result_auto['gcv']:.6f}")
print(f"Effective df: {result_auto['edf']:.2f}")
```

---

## Comparing Smoothers

Here is a complete example comparing several smoothing methods on the same
noisy signal:

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate
from fdars.smoothing import nadaraya_watson, local_linear, knn_smoother, optim_bandwidth
from fdars.basis import smooth_basis_gcv

# Generate data
argvals = np.linspace(0, 1, 200)
clean = simulate(n=1, argvals=argvals, n_basis=5, seed=42)
fd_clean = Fdata(clean, argvals=argvals)

rng = np.random.default_rng(7)
fd_noisy = fd_clean + rng.normal(0, 0.25, size=clean.shape)
x, y, y_true = fd_noisy.argvals, fd_noisy.data[0], fd_clean.data[0]

# 1. Nadaraya-Watson with GCV bandwidth
bw = optim_bandwidth(x, y)
y_nw = nadaraya_watson(x, y, x, bandwidth=bw["h_opt"])

# 2. Local linear with the same bandwidth
y_ll = local_linear(x, y, x, bandwidth=bw["h_opt"])

# 3. k-NN smoother
y_knn = knn_smoother(x, y, x, k=20)

# 4. B-spline smoothing
result_bs = smooth_basis_gcv(fd_noisy.data, fd_noisy.argvals, n_basis=25)
y_bs = result_bs["fitted"][0]

# Compare MSEs
for name, y_hat in [("NW", y_nw), ("LocLin", y_ll), ("k-NN", y_knn), ("B-spline", y_bs)]:
    mse = np.mean((y_hat - y_true) ** 2)
    print(f"{name:8s}  MSE = {mse:.6f}")
```

---

## Smoothing Multivariate Functional Data

All basis smoothers accept a full `(n_obs, n_points)` matrix and smooth every
curve simultaneously:

```python
# Simulate and corrupt 50 curves
data_clean = simulate(n=50, argvals=argvals, n_basis=5, seed=99)
fd_clean_50 = Fdata(data_clean, argvals=argvals)
fd_noisy_50 = fd_clean_50 + rng.normal(0, 0.2, size=data_clean.shape)

# Smooth all 50 curves in one call
result = smooth_basis_gcv(fd_noisy_50.data, fd_noisy_50.argvals, n_basis=20)
fd_smooth_50 = Fdata(result["fitted"], argvals=fd_noisy_50.argvals)
print(fd_smooth_50)  # Fdata (1D)  –  50 obs × 200 points  –  range [0.0, 1.0]

# Check reconstruction quality
mse_per_curve = np.mean((fd_smooth_50.data - fd_clean_50.data) ** 2, axis=1)
print(f"Mean MSE across curves: {mse_per_curve.mean():.6f}")
```

---

## Summary

| Method | Module | Strengths |
|--------|--------|-----------|
| Nadaraya-Watson | `fdars.smoothing` | Simple, nonparametric, automatic bandwidth via GCV |
| Local linear | `fdars.smoothing` | Corrects boundary bias |
| Local polynomial | `fdars.smoothing` | Flexible, can estimate derivatives |
| k-NN | `fdars.smoothing` | Adapts to local density |
| B-spline / P-spline | `fdars.basis` | Smooth all curves at once, automatic penalty |
| Fourier basis | `fdars.basis` | Natural for periodic data |

---

## Next Steps

- [Working with Derivatives](derivatives.md) -- smooth first, then
  differentiate.
- [Basis Representation](../represent/basis-representation.md) -- deeper look
  at B-spline and Fourier basis expansions.
- [Simulation Toolbox](simulation.md) -- generate data to test your smoothing
  pipeline.
