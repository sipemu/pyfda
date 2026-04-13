# Elastic Alignment

## The problem: amplitude vs. phase variability

When functional observations are observed over a common domain, variation between curves comes in two flavors:

- **Amplitude variability** -- differences in the *height* of features (peaks, valleys).
- **Phase variability** -- differences in the *timing* of features (shifted or stretched along the domain axis).

Classical statistics (cross-sectional mean, FPCA) treats both sources identically. The result is a blurred mean and artificially inflated variance. Elastic alignment resolves this by finding time-warping functions $\gamma$ that register each curve to a common template, isolating amplitude variation in the aligned curves and phase variation in the warps.

$$
f_{\text{aligned}}(t) = (f \circ \gamma)(t) = f(\gamma(t))
$$

!!! info "Fisher-Rao framework"
    All alignment in `fdars` is performed under the **elastic (Fisher-Rao) metric**, which is the unique Riemannian metric on the function space that is invariant to simultaneous reparameterization. This guarantees that the alignment is *proper* -- the distance between two functions does not depend on how they are parameterized.

---

## SRSF transform

The **Square Root Slope Function (SRSF)** maps a function $f$ into a representation where the elastic metric becomes the standard $L^2$ metric, making optimization tractable.

$$
q(t) = \operatorname{sign}(\dot{f}(t)) \, \sqrt{|\dot{f}(t)|}
$$

```python
import numpy as np
from fdars.alignment import srsf_transform, srsf_inverse

# Create a simple curve
t = np.linspace(0, 1, 101)
f = np.sin(2 * np.pi * t)

# Forward transform
q = srsf_transform(f, t)
print("SRSF shape:", q.shape)  # (101,)

# Inverse transform (recover original up to a constant)
f_recovered = srsf_inverse(q, t, initial_value=f[0])
print("Max reconstruction error:", np.max(np.abs(f - f_recovered)))
```

!!! note
    The SRSF transform loses the initial value $f(0)$. Pass `initial_value` to `srsf_inverse` to recover the original function exactly.

---

## Pairwise alignment

Align a single curve to a reference curve. The optimizer finds the warping function $\gamma^*$ that minimizes the elastic distance.

```python
from fdars.alignment import elastic_align_pair

# Two curves that differ in phase
t = np.linspace(0, 1, 101)
f1 = np.sin(2 * np.pi * t)
f2 = np.sin(2 * np.pi * (t - 0.1))  # shifted version

result = elastic_align_pair(f1, f2, t, lambda_=0.0)

f2_aligned = result["f_aligned"]   # f2 warped to match f1, shape (101,)
gamma      = result["gamma"]       # warping function, shape (101,)
distance   = result["distance"]    # elastic distance (scalar)

print(f"Elastic distance: {distance:.4f}")
print(f"Max alignment residual: {np.max(np.abs(f1 - f2_aligned)):.6f}")
```

| Key | Type | Description |
|-----|------|-------------|
| `f_aligned` | `ndarray (m,)` | Second curve warped to match the first |
| `gamma` | `ndarray (m,)` | Optimal warping function $\gamma^*$ |
| `distance` | `float` | Elastic distance after alignment |

!!! tip "Regularization"
    Increase `lambda_` to penalize complex warping functions and obtain smoother alignments. A value of `0.0` allows unconstrained warping; values around `0.01`--`1.0` are typical for moderate regularization.

---

## Group alignment: Karcher mean

The **Karcher mean** (Frechet mean under the elastic metric) simultaneously aligns all curves in a dataset and computes their elastic average. The algorithm iterates between:

1. Aligning every curve to the current mean estimate.
2. Recomputing the mean from the aligned curves.

```python
from fdars import Fdata
from fdars.alignment import karcher_mean

# Simulate 30 curves with random phase shifts
np.random.seed(0)
n, m = 30, 101
t = np.linspace(0, 1, m)
shifts = np.random.uniform(-0.15, 0.15, n)
fd = Fdata(np.array([np.sin(2 * np.pi * (t - s)) for s in shifts]), argvals=t)

result = karcher_mean(fd.data, t, lambda_=0.0, max_iter=20, tol=1e-4)

mu          = result["mean"]          # Karcher mean, shape (m,)
mu_srsf     = result["mean_srsf"]     # mean in SRSF space, shape (m,)
aligned     = result["aligned_data"]  # aligned curves, shape (n, m)
gammas      = result["gammas"]        # warping functions, shape (n, m)
n_iter      = result["n_iter"]        # iterations used
converged   = result["converged"]     # bool

print(f"Converged in {n_iter} iterations: {converged}")
```

| Key | Type | Description |
|-----|------|-------------|
| `mean` | `ndarray (m,)` | Karcher mean function |
| `mean_srsf` | `ndarray (m,)` | Mean in SRSF representation |
| `aligned_data` | `ndarray (n, m)` | All curves aligned to the mean |
| `gammas` | `ndarray (n, m)` | Warping functions for each curve |
| `n_iter` | `int` | Number of iterations performed |
| `converged` | `bool` | Whether the algorithm converged |

---

## Karcher median

The Karcher **median** replaces the squared elastic distance with the unsquared distance, producing a more robust central tendency estimate.

```python
from fdars.alignment import karcher_median

result = karcher_median(fd.data, t, lambda_=0.0, max_iter=20, tol=1e-3)

mu_median = result["mean"]       # elastic median
weights   = result["weights"]    # observation weights, shape (n,)
```

The result dictionary has the same keys as `karcher_mean`, plus `weights` -- the iteratively reweighted importance of each observation.

---

## Robust Karcher mean

When the dataset contains outliers, the **robust (trimmed) Karcher mean** down-weights or excludes the most extreme observations.

```python
from fdars.alignment import robust_karcher_mean

result = robust_karcher_mean(
    fd.data, t,
    lambda_=0.0,
    max_iter=20,
    tol=1e-3,
    trim_fraction=0.1,  # discard the 10% most distant curves
)

mu_robust = result["mean"]
weights   = result["weights"]  # zero for trimmed observations
```

!!! warning
    Setting `trim_fraction` too high removes legitimate variation. Start with `0.05`--`0.10` and increase only if diagnostics confirm heavy contamination.

---

## Interpreting warping functions

A warping function $\gamma: [0,1] \to [0,1]$ is a monotonically increasing diffeomorphism. Its slope encodes local timing distortions:

| Slope of $\gamma$ | Interpretation |
|--------------------|----------------|
| $\gamma'(t) > 1$ | The original curve is **compressed** at time $t$ -- features happen faster than in the template |
| $\gamma'(t) < 1$ | The original curve is **stretched** at time $t$ -- features happen slower than in the template |
| $\gamma'(t) = 1$ | No timing distortion at $t$ |

```python
# Inspect warping for the first curve
gamma_0 = gammas[0]

# Where is the curve compressed?
compressed = t[np.gradient(gamma_0, t) > 1.2]
print(f"Compressed regions: {compressed[[0, -1]]}")
```

---

## Elastic distance

Compute the elastic (Fisher-Rao) distance between two curves without explicitly returning the warping function.

```python
from fdars.alignment import elastic_distance

d = elastic_distance(f1, f2, t)
print(f"Elastic distance: {d:.4f}")
```

---

## Distance matrices

Compute pairwise elastic distances for an entire dataset. These matrices can be fed into nonparametric regression, clustering, or classification.

```python
from fdars.alignment import elastic_self_distance_matrix, elastic_cross_distance_matrix

# Self-distance matrix (symmetric, zero diagonal)
D = elastic_self_distance_matrix(fd.data, fd.argvals, lambda_=0.0)
print("Distance matrix shape:", D.shape)  # (30, 30)

# Cross-distance matrix between two datasets
fd_train = fd[:20]
fd_test  = fd[20:]
D_cross = elastic_cross_distance_matrix(fd_train.data, fd_test.data, fd.argvals, lambda_=0.0)
print("Cross-distance shape:", D_cross.shape)  # (20, 10)
```

---

## Warp utilities

Warping functions form a group under composition. `fdars` provides utilities for working with them.

### Compose warps

Apply warp $\gamma_2$ after $\gamma_1$:

```python
from fdars.alignment import compose_warps

gamma_composed = compose_warps(gamma_1, gamma_2, t)
```

### Invert a warp

Find $\gamma^{-1}$ such that $\gamma \circ \gamma^{-1} = \text{id}$:

```python
from fdars.alignment import invert_warp

gamma_inv = invert_warp(gamma_0, t)
```

### Warp smoothness

The **bending energy** quantifies how far $\gamma$ deviates from smooth:

```python
from fdars.alignment import warp_smoothness

energy = warp_smoothness(gamma_0, t)
print(f"Bending energy: {energy:.4f}")
```

### Warp complexity

The **geodesic distance from the identity** measures the overall magnitude of the warp:

```python
from fdars.alignment import warp_complexity

complexity = warp_complexity(gamma_0, t)
print(f"Warp complexity: {complexity:.4f}")
```

---

## Amplitude vs. phase distance

After alignment, the total elastic distance decomposes into two orthogonal components:

$$
d_{\text{elastic}}^2 = d_{\text{amplitude}}^2 + d_{\text{phase}}^2
$$

```python
from fdars.alignment import amplitude_distance, phase_distance

d_amp   = amplitude_distance(f1, f2, t)
d_phase = phase_distance(f1, f2, t)
d_total = elastic_distance(f1, f2, t)

print(f"Amplitude distance: {d_amp:.4f}")
print(f"Phase distance:     {d_phase:.4f}")
print(f"Total (elastic):    {d_total:.4f}")
print(f"Check: {d_amp**2 + d_phase**2:.4f} ~ {d_total**2:.4f}")
```

---

## Full example: aligning time-warped growth curves

```python
import numpy as np
from fdars import Fdata
from fdars.alignment import (
    karcher_mean,
    elastic_distance,
    elastic_self_distance_matrix,
    amplitude_distance,
    phase_distance,
    warp_complexity,
)

# --- Simulate data ---
np.random.seed(42)
n, m = 50, 201
t = np.linspace(0, 1, m)

# Base signal: a double-peak growth curve
base = 3 * np.exp(-((t - 0.3) ** 2) / 0.01) + 2 * np.exp(-((t - 0.7) ** 2) / 0.02)

# Random amplitude and phase perturbations
data = np.zeros((n, m))
for i in range(n):
    amp = 1.0 + 0.2 * np.random.randn()
    shift = 0.05 * np.random.randn()
    t_warped = np.clip(t + shift * np.sin(2 * np.pi * t), 0, 1)
    data[i] = amp * np.interp(t, t_warped, base) + 0.1 * np.random.randn(m)

fd = Fdata(data, argvals=t)

# --- Align ---
result = karcher_mean(fd.data, fd.argvals, lambda_=0.1, max_iter=30, tol=1e-5)
print(f"Karcher mean converged: {result['converged']} ({result['n_iter']} iters)")

aligned = result["aligned_data"]
gammas  = result["gammas"]

# --- Analyze warps ---
complexities = np.array([warp_complexity(gammas[i], fd.argvals) for i in range(n)])
print(f"Mean warp complexity: {complexities.mean():.4f}")
print(f"Max  warp complexity: {complexities.max():.4f}")

# --- Variance reduction ---
var_before = np.mean(np.var(fd.data, axis=0))
var_after  = np.mean(np.var(aligned, axis=0))
print(f"Cross-sectional variance: {var_before:.4f} -> {var_after:.4f}")
print(f"Variance reduction: {100 * (1 - var_after / var_before):.1f}%")

# --- Distance decomposition ---
D = elastic_self_distance_matrix(fd.data, fd.argvals)
d_a = amplitude_distance(fd.data[0], fd.data[1], fd.argvals)
d_p = phase_distance(fd.data[0], fd.data[1], fd.argvals)
print(f"\nCurves 0 vs 1:")
print(f"  Amplitude distance: {d_a:.4f}")
print(f"  Phase distance:     {d_p:.4f}")
print(f"  Elastic distance:   {D[0, 1]:.4f}")
```
