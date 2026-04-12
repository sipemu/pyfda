---
title: Simulation Toolbox
---

# Simulation Toolbox

Synthetic functional data is essential for benchmarking, validating methods, and
building intuition. pyfda provides two complementary generators:

1. **Karhunen-Loeve (KL) simulation** -- construct curves as random linear
   combinations of basis eigenfunctions.
2. **Gaussian process (GP) generation** -- sample from a zero-mean GP with a
   specified covariance kernel.

Both live in the `pyfda.simulation` module and return a 2D NumPy array of shape
`(n, m)` where `n` is the number of curves and `m` is the number of grid points.
Wrapping the result in an `Fdata` object bundles the data with its evaluation
grid and unlocks convenience methods for depth, distances, derivatives, and more.

```python
import numpy as np
from pyfda import Fdata
from pyfda.simulation import simulate, gaussian_process
```

---

## Karhunen-Loeve Simulation

The Karhunen-Loeve theorem states that any square-integrable random function can
be expanded as:

$$
X(t) = \mu(t) + \sum_{k=1}^{\infty} \xi_k \, \phi_k(t)
$$

where $\phi_k$ are orthonormal eigenfunctions and $\xi_k$ are uncorrelated
random scores with $\operatorname{Var}(\xi_k) = \lambda_k$.

`simulate()` truncates this expansion to `n_basis` terms. You control the shape
of the curves through the **eigenfunction type** and the variance structure
through the **eigenvalue decay**.

### Basic Usage

```python
argvals = np.linspace(0, 1, 100)

data = simulate(
    n=50,              # number of curves
    argvals=argvals,   # evaluation grid
    n_basis=5,         # number of KL terms
    efun_type="fourier",  # eigenfunction family
    eval_type="linear",   # eigenvalue decay
    seed=42,           # reproducibility
)
fd = Fdata(data, argvals=argvals)
print(fd)  # Fdata (1D)  –  50 obs × 100 points  –  range [0.0, 1.0]
```

---

### Eigenfunction Types

The `efun_type` parameter controls the shape of the basis functions $\phi_k$.

#### `"fourier"` (default)

Sines and cosines of increasing frequency. Produces smooth, oscillatory curves.

```python
data_fourier = simulate(
    n=30, argvals=argvals, n_basis=7,
    efun_type="fourier", seed=1,
)
fd_fourier = Fdata(data_fourier, argvals=argvals)
```

#### `"poly"`

Legendre-like polynomial eigenfunctions. Curves tend to show broad trends
without rapid oscillation.

```python
data_poly = simulate(
    n=30, argvals=argvals, n_basis=5,
    efun_type="poly", seed=1,
)
fd_poly = Fdata(data_poly, argvals=argvals)
```

#### `"poly_high"`

Higher-degree polynomial eigenfunctions that introduce more local variation
than `"poly"`.

```python
data_poly_high = simulate(
    n=30, argvals=argvals, n_basis=5,
    efun_type="poly_high", seed=1,
)
fd_poly_high = Fdata(data_poly_high, argvals=argvals)
```

#### `"wiener"`

Eigenfunctions of the Wiener process (Brownian motion). Useful for simulating
non-stationary, drifting paths.

```python
data_wiener = simulate(
    n=30, argvals=argvals, n_basis=5,
    efun_type="wiener", seed=1,
)
fd_wiener = Fdata(data_wiener, argvals=argvals)
```

!!! tip "Choosing an eigenfunction type"
    Use `"fourier"` for periodic or oscillatory data, `"poly"` for smooth
    monotonic trends, and `"wiener"` for random-walk-like behavior.

---

### Eigenvalue Decay Patterns

The `eval_type` parameter governs how fast the eigenvalues $\lambda_k$ decay,
which controls the effective dimensionality of the data.

#### `"linear"` (default)

$\lambda_k = 1/k$. Slow decay means higher-order components still carry
substantial variance, producing more complex curves.

```python
data_linear = simulate(
    n=30, argvals=argvals, n_basis=10,
    eval_type="linear", seed=2,
)
fd_linear = Fdata(data_linear, argvals=argvals)
```

#### `"exponential"`

$\lambda_k = e^{-k}$. Fast decay concentrates variance in the first few
components, yielding smoother, lower-dimensional data.

```python
data_exp = simulate(
    n=30, argvals=argvals, n_basis=10,
    eval_type="exponential", seed=2,
)
fd_exp = Fdata(data_exp, argvals=argvals)
```

#### `"wiener"`

$\lambda_k = 1/(k - 0.5)^2 \pi^2$. The eigenvalue pattern of a Brownian
motion covariance.

```python
data_wiener_eval = simulate(
    n=30, argvals=argvals, n_basis=10,
    eval_type="wiener", seed=2,
)
fd_wiener_eval = Fdata(data_wiener_eval, argvals=argvals)
```

---

### Combining Options

You can mix any eigenfunction type with any eigenvalue decay:

```python
# Fourier shapes with fast exponential decay -> very smooth oscillatory curves
smooth_osc = simulate(
    n=40, argvals=argvals, n_basis=7,
    efun_type="fourier", eval_type="exponential", seed=10,
)
fd_smooth_osc = Fdata(smooth_osc, argvals=argvals)

# Polynomial shapes with linear decay -> complex trending curves
complex_trend = simulate(
    n=40, argvals=argvals, n_basis=7,
    efun_type="poly", eval_type="linear", seed=10,
)
fd_complex_trend = Fdata(complex_trend, argvals=argvals)
```

### Effect of `n_basis`

Increasing `n_basis` adds higher-frequency variation:

```python
# Low complexity
simple = simulate(n=20, argvals=argvals, n_basis=3, seed=0)
fd_simple = Fdata(simple, argvals=argvals)

# High complexity
complex_ = simulate(n=20, argvals=argvals, n_basis=15, seed=0)
fd_complex = Fdata(complex_, argvals=argvals)
```

!!! info "Reproducibility"
    Pass a fixed `seed` to get identical results across runs. When `seed` is
    `None`, a different random sample is produced each time.

---

## Gaussian Process Generation

For more control over the local correlation structure, generate samples from a
zero-mean Gaussian process with a specified covariance kernel.

### Basic Usage

```python
argvals = np.linspace(0, 1, 100)

gp_data = gaussian_process(
    n=40,              # number of curves
    argvals=argvals,
    kernel="gaussian",
    length_scale=0.2,
    variance=1.0,
    seed=42,
)
fd_gp = Fdata(gp_data, argvals=argvals)
print(fd_gp)  # Fdata (1D)  –  40 obs × 100 points  –  range [0.0, 1.0]
```

---

### Covariance Kernels

#### `"gaussian"` (squared exponential)

$$
C(s, t) = \sigma^2 \exp\!\left( -\frac{(s - t)^2}{2 \ell^2} \right)
$$

Produces infinitely differentiable (very smooth) sample paths.

```python
gp_gauss = gaussian_process(
    n=30, argvals=argvals,
    kernel="gaussian", length_scale=0.15, variance=1.0, seed=1,
)
fd_gp_gauss = Fdata(gp_gauss, argvals=argvals)
```

#### `"exponential"` (Ornstein-Uhlenbeck)

$$
C(s, t) = \sigma^2 \exp\!\left( -\frac{|s - t|}{\ell} \right)
$$

Sample paths are continuous but not differentiable -- rougher than Gaussian.

```python
gp_exp = gaussian_process(
    n=30, argvals=argvals,
    kernel="exponential", length_scale=0.15, variance=1.0, seed=1,
)
fd_gp_exp = Fdata(gp_exp, argvals=argvals)
```

#### `"matern"`

The Matern kernel with smoothness parameter $\nu = 1.5$:

$$
C(s, t) = \sigma^2 \left(1 + \frac{\sqrt{3}\,|s - t|}{\ell}\right)
\exp\!\left( -\frac{\sqrt{3}\,|s - t|}{\ell} \right)
$$

A middle ground between Gaussian (too smooth) and exponential (too rough).

```python
gp_matern = gaussian_process(
    n=30, argvals=argvals,
    kernel="matern", length_scale=0.15, variance=1.0, seed=1,
)
fd_gp_matern = Fdata(gp_matern, argvals=argvals)
```

#### `"periodic"`

$$
C(s, t) = \sigma^2 \exp\!\left( -\frac{2 \sin^2(\pi |s - t| / p)}{\ell^2} \right)
$$

Generates sample paths with a repeating pattern (period $p = 1.0$ by default).

```python
gp_periodic = gaussian_process(
    n=30, argvals=argvals,
    kernel="periodic", length_scale=0.3, variance=1.0, seed=1,
)
fd_gp_periodic = Fdata(gp_periodic, argvals=argvals)
```

---

### Controlling Smoothness with `length_scale`

The length scale $\ell$ determines how quickly the correlation decays with
distance. Smaller values produce more wiggly paths; larger values yield
smoother, slowly varying curves.

```python
# Short length scale -> rough
rough = gaussian_process(
    n=20, argvals=argvals,
    kernel="gaussian", length_scale=0.05, seed=0,
)
fd_rough = Fdata(rough, argvals=argvals)

# Long length scale -> smooth
smooth = gaussian_process(
    n=20, argvals=argvals,
    kernel="gaussian", length_scale=0.5, seed=0,
)
fd_smooth = Fdata(smooth, argvals=argvals)
```

### Controlling Amplitude with `variance`

The `variance` parameter $\sigma^2$ scales the overall amplitude of the curves.

```python
low_var = gaussian_process(
    n=20, argvals=argvals,
    kernel="gaussian", length_scale=0.2, variance=0.1, seed=0,
)
fd_low_var = Fdata(low_var, argvals=argvals)

high_var = gaussian_process(
    n=20, argvals=argvals,
    kernel="gaussian", length_scale=0.2, variance=5.0, seed=0,
)
fd_high_var = Fdata(high_var, argvals=argvals)
```

---

## Computing a Covariance Matrix

If you need the raw covariance matrix $C(s_i, t_j)$ for custom purposes (e.g.,
feeding into your own sampler), use `covariance_matrix`:

```python
from pyfda.simulation import covariance_matrix

argvals = np.linspace(0, 1, 50)
cov = covariance_matrix(
    argvals, kernel="gaussian", length_scale=0.2, variance=1.0,
)
print(cov.shape)  # (50, 50)
print(f"Diagonal (should be ~1.0): {cov[0, 0]:.4f}")
```

---

## Full Example: Simulate, Analyze, Cluster

Bringing it all together in a realistic workflow:

```python
import numpy as np
import pandas as pd
from pyfda import Fdata
from pyfda.simulation import simulate
from pyfda.clustering import kmeans_fd

# -- Step 1: Generate two groups with different eigenfunction types --
argvals = np.linspace(0, 1, 150)
group_a = simulate(n=40, argvals=argvals, n_basis=5, efun_type="fourier", seed=10)
group_b = simulate(n=40, argvals=argvals, n_basis=5, efun_type="poly", seed=20)

# Wrap each group in Fdata; shift group_b upward so the groups are distinguishable
fd_a = Fdata(group_a, argvals=argvals)
fd_b = Fdata(group_b, argvals=argvals) + 2.0

# Stack into a single dataset with metadata tracking the true group
data = np.vstack([fd_a.data, fd_b.data])  # (80, 150)
true_labels = np.array([0] * 40 + [1] * 40)
fd = Fdata(
    data, argvals=argvals,
    metadata=pd.DataFrame({"group": true_labels}),
)

# -- Step 2: Summary statistics (Fdata convenience methods) --
mu = fd.mean()
norms = fd.norm()
print(f"Grand mean range: [{mu.min():.2f}, {mu.max():.2f}]")
print(f"Norm range: [{norms.min():.2f}, {norms.max():.2f}]")

# -- Step 3: Depth ranking --
depths = fd.depth("fraiman_muniz")
median_idx = np.argmax(depths)
print(f"Deepest curve: index {median_idx}, depth {depths[median_idx]:.4f}")

# -- Step 4: Clustering --
result = kmeans_fd(fd.data, fd.argvals, k=2, seed=0)
pred_labels = result["cluster"]

# Compare with truth (up to label permutation)
agreement = max(
    (pred_labels == true_labels).mean(),
    (pred_labels != true_labels).mean(),
)
print(f"Clustering agreement: {agreement:.1%}")
```

---

## Next Steps

- [Introduction to pyfda](introduction.md) -- if you haven't read it yet.
- [Smoothing](smoothing.md) -- apply smoothing to your simulated data.
- [Working with Derivatives](derivatives.md) -- differentiate your curves.
- [Covariance Functions](../analyze/covariance-functions.md) -- deeper look at
  kernel functions.
