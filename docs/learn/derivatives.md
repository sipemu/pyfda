---
title: Working with Derivatives
---

# Working with Derivatives

Derivatives of functional data reveal *how* curves change -- velocity,
acceleration, curvature, and higher-order dynamics. pyfda computes numerical
derivatives for both 1D and 2D functional data through the `pyfda.fdata` module.

```python
import numpy as np
from pyfda.fdata import deriv_1d, deriv_2d
```

---

## Why Derivatives Matter

Many scientific questions are naturally about rates of change rather than
absolute levels:

- **Growth curves** -- velocity (first derivative) and acceleration (second
  derivative) of growth.
- **Spectroscopy** -- first and second derivatives enhance peaks and remove
  baseline drift.
- **Motion capture** -- velocity and acceleration from position trajectories.
- **Process monitoring** -- rate-of-change charts detect shifts earlier than
  level charts.

!!! note "Notation"
    For a functional observation $x_i(t)$, the $r$-th derivative is
    $x_i^{(r)}(t) = \frac{d^r x_i}{dt^r}$.

---

## First Derivative (1D)

`deriv_1d` computes numerical derivatives using finite differences. It requires
the data matrix and the evaluation grid `argvals`.

```python
from pyfda.simulation import simulate

# Simulate smooth curves
argvals = np.linspace(0, 1, 200)
data = simulate(n=30, argvals=argvals, n_basis=5, seed=42)
print(data.shape)  # (30, 200)

# First derivative
d1 = deriv_1d(data, argvals)
print(d1.shape)  # (30, 200)
```

The result is a 2D array of the same shape: each row is the first derivative of
the corresponding input curve, evaluated at the same grid points.

### Interpreting the Output

```python
from pyfda.fdata import mean_1d

# Mean of the original curves
mu = mean_1d(data)

# Mean of the first derivatives
mu_deriv = mean_1d(d1)

# At a point where mu_deriv ~ 0, the mean function has a local extremum
zero_crossings = np.where(np.diff(np.sign(mu_deriv)))[0]
print(f"Approximate extrema of the mean at t = {argvals[zero_crossings]}")
```

---

## Higher-Order Derivatives

Use the `nderiv` parameter to compute second, third, or higher derivatives in
a single call:

```python
# Second derivative (acceleration / curvature)
d2 = deriv_1d(data, argvals, nderiv=2)
print(d2.shape)  # (30, 200)

# Third derivative
d3 = deriv_1d(data, argvals, nderiv=3)
```

!!! warning "Numerical instability"
    Each successive derivative amplifies noise. On raw noisy data, higher-order
    derivatives can become meaningless. **Always smooth first** (see the section
    below).

### Comparing Derivative Orders

```python
# Compute derivatives of orders 1 through 4
derivs = {}
for order in range(1, 5):
    derivs[order] = deriv_1d(data, argvals, nderiv=order)

# Show the range of values -- note how it grows with order
for order, d in derivs.items():
    r = d[0]  # first curve
    print(f"Order {order}: range = [{r.min():.2f}, {r.max():.2f}]")
```

---

## 2D Functional Data Derivatives

For functional data observed on a 2D domain (surfaces), `deriv_2d` computes
partial derivatives in both directions plus the mixed partial derivative.

### Data Layout for 2D

A 2D functional observation is a surface $x_i(s, t)$ evaluated on an
$m_1 \times m_2$ grid. In pyfda, this is stored as a 2D array of shape
`(n_obs, m1 * m2)` -- each surface is flattened into a single row.

```python
# Create a simple 2D functional dataset
m1, m2 = 30, 40
argvals_s = np.linspace(0, 1, m1)
argvals_t = np.linspace(0, 1, m2)
S, T = np.meshgrid(argvals_s, argvals_t, indexing="ij")

# 10 surfaces: sin(a*s) * cos(b*t) with random a, b
rng = np.random.default_rng(0)
n_obs = 10
data_2d = np.zeros((n_obs, m1 * m2))
for i in range(n_obs):
    a, b = rng.uniform(1, 5, size=2)
    surface = np.sin(a * S) * np.cos(b * T)
    data_2d[i] = surface.ravel()

print(data_2d.shape)  # (10, 1200)
```

### Computing Partial Derivatives

```python
ds, dt, dsdt = deriv_2d(data_2d, argvals_s, argvals_t)

print(f"d/ds shape:    {ds.shape}")    # (10, 1200)
print(f"d/dt shape:    {dt.shape}")    # (10, 1200)
print(f"d2/dsdt shape: {dsdt.shape}")  # (10, 1200)
```

The three returned arrays are:

| Array | Meaning |
|-------|---------|
| `ds` | $\partial x_i / \partial s$ -- partial derivative w.r.t. the first dimension |
| `dt` | $\partial x_i / \partial t$ -- partial derivative w.r.t. the second dimension |
| `dsdt` | $\partial^2 x_i / \partial s \, \partial t$ -- mixed partial derivative |

### Reshaping for Visualization

To inspect a single surface, reshape back to the grid:

```python
# Partial derivative of the first surface w.r.t. s
ds_surface = ds[0].reshape(m1, m2)
print(ds_surface.shape)  # (30, 40)
```

---

## Combining Derivatives with Smoothing

Differentiating noisy data amplifies the noise. The standard workflow is:

1. **Smooth** the raw curves.
2. **Differentiate** the smoothed curves.

### Kernel Smoothing + Derivative

```python
from pyfda.simulation import simulate
from pyfda.smoothing import nadaraya_watson, optim_bandwidth
from pyfda.fdata import deriv_1d

# Noisy data
argvals = np.linspace(0, 1, 200)
clean = simulate(n=20, argvals=argvals, n_basis=5, seed=42)
rng = np.random.default_rng(0)
noisy = clean + rng.normal(0, 0.3, size=clean.shape)

# Smooth each curve with an optimal bandwidth
smoothed = np.zeros_like(noisy)
for i in range(noisy.shape[0]):
    bw = optim_bandwidth(argvals, noisy[i])
    smoothed[i] = nadaraya_watson(argvals, noisy[i], argvals, bandwidth=bw["h_opt"])

# Now differentiate the smooth curves
d1_smooth = deriv_1d(smoothed, argvals)
d1_noisy  = deriv_1d(noisy, argvals)

# Compare noise levels
print(f"Std of d1(noisy):   {d1_noisy.std():.2f}")
print(f"Std of d1(smooth):  {d1_smooth.std():.2f}")
```

### Basis Smoothing + Derivative

Basis smoothing is more efficient for large datasets because you smooth all
curves at once:

```python
from pyfda.basis import smooth_basis_gcv

# Smooth all 20 curves simultaneously
result = smooth_basis_gcv(noisy, argvals, n_basis=25)
smoothed_basis = result["fitted"]

# Differentiate
d1_basis = deriv_1d(smoothed_basis, argvals)
d2_basis = deriv_1d(smoothed_basis, argvals, nderiv=2)

print(f"d1 range: [{d1_basis.min():.2f}, {d1_basis.max():.2f}]")
print(f"d2 range: [{d2_basis.min():.2f}, {d2_basis.max():.2f}]")
```

!!! tip "Recommended pipeline"
    For most applications, **basis smoothing followed by numerical
    differentiation** gives the best balance of speed, smoothness, and accuracy.
    Use `smooth_basis_gcv` with enough basis functions and let GCV choose
    the penalty.

---

## Full Example: Growth Curve Analysis

A classic FDA application is analyzing human growth data. Here we simulate
growth-like curves and extract velocity and acceleration:

```python
import numpy as np
from pyfda.simulation import simulate
from pyfda.basis import smooth_basis_gcv
from pyfda.fdata import deriv_1d, mean_1d

# Simulate growth-like curves (monotone, decelerating)
age = np.linspace(1, 18, 200)   # ages 1 to 18
argvals_01 = np.linspace(0, 1, 200)  # simulation on [0,1]

raw = simulate(n=40, argvals=argvals_01, n_basis=4,
               efun_type="poly", eval_type="exponential", seed=7)

# Transform to look like growth: cumulative sum + scaling
growth = np.cumsum(np.abs(raw), axis=1)
growth = 50 + 130 * (growth - growth.min(axis=1, keepdims=True)) / \
    (growth.max(axis=1, keepdims=True) - growth.min(axis=1, keepdims=True))

# Smooth
result = smooth_basis_gcv(growth, age, n_basis=20)
smooth_growth = result["fitted"]

# Velocity (cm/year)
velocity = deriv_1d(smooth_growth, age)
mean_vel = mean_1d(velocity)

# Acceleration (cm/year^2)
acceleration = deriv_1d(smooth_growth, age, nderiv=2)
mean_acc = mean_1d(acceleration)

# Find the age of peak velocity
peak_age_idx = np.argmax(mean_vel)
print(f"Mean peak growth velocity at age {age[peak_age_idx]:.1f}")

# Find where acceleration crosses zero (inflection points)
zero_crossings = np.where(np.diff(np.sign(mean_acc)))[0]
print(f"Growth acceleration sign changes at ages: {age[zero_crossings].round(1)}")
```

---

## Summary

| Function | Module | Description |
|----------|--------|-------------|
| `deriv_1d(data, argvals, nderiv=1)` | `pyfda.fdata` | Numerical derivative of 1D functional data |
| `deriv_2d(data, argvals_s, argvals_t)` | `pyfda.fdata` | Partial derivatives of 2D functional data |

Key points:

- **Smooth before differentiating** -- raw derivatives of noisy data are
  unreliable.
- **`nderiv`** -- set to 2 or 3 for second/third derivatives in a single call.
- **2D data** -- returns $\partial/\partial s$, $\partial/\partial t$, and
  $\partial^2/\partial s \, \partial t$.

---

## Next Steps

- [Smoothing](smoothing.md) -- choose the right smoother before differentiating.
- [Functional PCA](../represent/fpca.md) -- decompose derivatives into principal
  components.
- [Basis Representation](../represent/basis-representation.md) -- smooth with
  basis expansions for optimal pre-processing.
