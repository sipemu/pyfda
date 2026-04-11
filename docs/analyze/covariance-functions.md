# Covariance Functions

Covariance functions (kernels) describe the correlation structure of a stochastic process. They are the building blocks for Gaussian process simulation, Kriging, and kernel-based smoothing. `pyfda` provides kernel-based covariance matrix construction and Gaussian process sample generation, all computed in Rust.

---

## Available kernels

| Kernel | Formula | Character |
|---|---|---|
| **Gaussian** (squared exponential) | $C(s,t) = \sigma^2 \exp\!\bigl(-\tfrac{(s-t)^2}{2\ell^2}\bigr)$ | Infinitely smooth sample paths |
| **Exponential** | $C(s,t) = \sigma^2 \exp\!\bigl(-\tfrac{|s-t|}{\ell}\bigr)$ | Continuous but non-differentiable (Ornstein-Uhlenbeck) |
| **Matern** ($\nu=1.5$) | $C(s,t) = \sigma^2 \bigl(1 + \tfrac{\sqrt{3}\,|s-t|}{\ell}\bigr) \exp\!\bigl(-\tfrac{\sqrt{3}\,|s-t|}{\ell}\bigr)$ | Once-differentiable; realistic for physical processes |
| **Periodic** | $C(s,t) = \sigma^2 \exp\!\bigl(-\tfrac{2\sin^2(\pi|s-t|/p)}{\ell^2}\bigr)$ | Repeating patterns with period $p$ |

In all formulas, $\ell$ is the **length scale** and $\sigma^2$ is the **variance**.

---

## Computing a covariance matrix

```python
import numpy as np
from pyfda.simulation import covariance_matrix

argvals = np.linspace(0, 1, 100)

# Gaussian kernel
cov_gauss = covariance_matrix(argvals, kernel="gaussian", length_scale=0.2, variance=1.0)

# Exponential kernel
cov_exp = covariance_matrix(argvals, kernel="exponential", length_scale=0.2, variance=1.0)

print(f"Shape: {cov_gauss.shape}")           # (100, 100)
print(f"Symmetric: {np.allclose(cov_gauss, cov_gauss.T)}")  # True
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `kernel` | `str` | `"gaussian"` | `"gaussian"` or `"exponential"` |
| `length_scale` | `float` | `0.2` | Kernel length scale $\ell$ |
| `variance` | `float` | `1.0` | Kernel variance $\sigma^2$ |

**Returns** an `ndarray` of shape `(m, m)`.

!!! tip "Effect of length scale"
    A small $\ell$ produces rapidly varying (wiggly) functions; a large $\ell$ produces smooth, slowly varying functions. Try values from 0.05 to 0.5 on $[0,1]$ to build intuition.

---

## Generating Gaussian process samples

`gaussian_process` draws $n$ sample paths from a zero-mean GP with the specified kernel. The function internally constructs the covariance matrix and performs a Cholesky decomposition.

```python
from pyfda.simulation import gaussian_process

argvals = np.linspace(0, 1, 200)

# 50 smooth curves (Gaussian kernel)
samples_gauss = gaussian_process(50, argvals, kernel="gaussian", length_scale=0.15, seed=1)

# 50 rough curves (exponential kernel)
samples_exp = gaussian_process(50, argvals, kernel="exponential", length_scale=0.15, seed=1)

# 50 Matern curves
samples_mat = gaussian_process(50, argvals, kernel="matern", length_scale=0.15, seed=1)

# 50 periodic curves
samples_per = gaussian_process(50, argvals, kernel="periodic", length_scale=0.15, seed=1)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `n` | `int` | -- | Number of sample paths |
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `kernel` | `str` | `"gaussian"` | `"gaussian"`, `"exponential"`, `"matern"`, or `"periodic"` |
| `length_scale` | `float` | `0.2` | Kernel length scale |
| `variance` | `float` | `1.0` | Kernel variance |
| `seed` | `int` | `None` | Random seed (omit for non-deterministic) |

**Returns** an `ndarray` of shape `(n, m)`.

---

## Comparing kernel shapes

The following script visualizes the covariance structure and sample paths for each kernel side by side.

```python
import numpy as np
from pyfda.simulation import covariance_matrix, gaussian_process

argvals = np.linspace(0, 1, 200)
kernels = ["gaussian", "exponential"]

try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for col, kern in enumerate(kernels):
        # Covariance row from the midpoint
        cov = covariance_matrix(argvals, kernel=kern, length_scale=0.15)
        mid = len(argvals) // 2
        axes[0, col].plot(argvals, cov[mid, :])
        axes[0, col].set_title(f"{kern.title()} kernel — C(0.5, t)")
        axes[0, col].set_xlabel("t")

        # Sample paths
        samples = gaussian_process(10, argvals, kernel=kern, length_scale=0.15, seed=42)
        for s in samples:
            axes[1, col].plot(argvals, s, linewidth=0.7, alpha=0.7)
        axes[1, col].set_title(f"{kern.title()} — 10 sample paths")
        axes[1, col].set_xlabel("t")

    plt.tight_layout()
    plt.savefig("covariance_kernels.png", dpi=150)
    plt.show()
except ImportError:
    pass
```

---

## Using GP samples for simulation studies

GP samples provide a convenient way to create realistic synthetic functional data for benchmarking FDA methods. Here is a complete example that generates data from two different kernels and compares clustering results.

```python
import numpy as np
from pyfda.simulation import gaussian_process
from pyfda.clustering import kmeans_fd, silhouette_score
from pyfda.metric import lp_self_1d

argvals = np.linspace(0, 1, 150)

# Group 1: smooth Gaussian kernel
g1 = gaussian_process(30, argvals, kernel="gaussian", length_scale=0.25, seed=1)

# Group 2: rough exponential kernel + vertical shift
g2 = gaussian_process(30, argvals, kernel="exponential", length_scale=0.10, seed=2) + 2.0

data = np.vstack([g1, g2])

# Cluster
km = kmeans_fd(data, argvals, k=2, seed=42)
print(f"Converged: {km['converged']}, iterations: {km['iter']}")

# Evaluate
dist = lp_self_1d(data, argvals)
labels = km["cluster"].astype(np.int64)
sil = silhouette_score(dist, labels)
print(f"Mean silhouette: {np.mean(sil):.3f}")
```

!!! info "Performance"
    Generating 1000 GP samples on a 500-point grid takes roughly 50 ms. The bottleneck is the Cholesky decomposition of the $m \times m$ covariance matrix, which is $O(m^3)$.
