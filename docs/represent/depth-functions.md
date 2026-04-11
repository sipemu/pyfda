# Depth Functions

Depth functions generalize the notion of quantiles and ranks to functional data. A depth measure assigns each curve a real number indicating how "central" it is relative to a reference sample. The deepest curve is the **functional median** -- a robust location estimator. Curves with low depth are potential outliers.

## Concepts

Given a sample of curves $X_1(t), \ldots, X_n(t)$, a functional depth $D(X_i \mid X_1, \ldots, X_n) \in [0, 1]$ satisfies:

- **Maximality at center**: the depth is maximized at some notion of center.
- **Monotonicity from center**: moving a curve away from the center decreases its depth.
- **Vanishing at infinity**: extreme curves have depth approaching zero.

The **functional median** is the observation with the largest depth:

$$
\hat{X}_{\mathrm{med}} = X_{i^*}, \quad i^* = \arg\max_i D(X_i \mid X_1, \ldots, X_n)
$$

## Available depth measures

All depth functions live in `pyfda.depth` and share a common interface:

```python
from pyfda.depth import fraiman_muniz_1d  # example

depths = fraiman_muniz_1d(data, ref_data)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `np.ndarray` (n, m) | Curves to evaluate |
| `ref_data` | `np.ndarray` (n_ref, m) | Reference sample (often the same as `data`) |

The return value is always a 1D array of length `n` with depth values.

!!! tip "Self-depth"
    To rank observations within their own sample, pass the same array as both `data` and `ref_data`:
    ```python
    depths = fraiman_muniz_1d(data, data)
    ```

---

### Fraiman-Muniz depth

```python
from pyfda.depth import fraiman_muniz_1d

depths = fraiman_muniz_1d(data, ref_data, scale=True)
```

Integrates univariate depth (based on the empirical CDF) across the domain:

$$
D_{\mathrm{FM}}(X) = \int_0^1 D_1\bigl(X(t) \mid X_1(t), \ldots, X_n(t)\bigr)\,dt
$$

where $D_1$ is the univariate simplicial depth $D_1(x) = 2 \min\bigl(F_n(x),\, 1 - F_n(x)\bigr)$.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scale` | `True` | Normalize depth values to $[0, 1]$ |

---

### Modified Band Depth

```python
from pyfda.depth import modified_band_1d

depths = modified_band_1d(data, ref_data)
```

Measures the proportion of time a curve lies within the band formed by pairs of reference curves. More robust than band depth because it uses the proportion of time inside the band rather than requiring full containment.

$$
D_{\mathrm{MBD}}(X) = \binom{n}{2}^{-1} \sum_{i < j} \lambda\bigl\{t : X_{(i)}(t) \le X(t) \le X_{(j)}(t)\bigr\}
$$

where $\lambda$ denotes the proportion of the domain.

---

### Band Depth

```python
from pyfda.depth import band_1d

depths = band_1d(data, ref_data)
```

The "strict" version of modified band depth: a curve gets credit only if it is **entirely** contained within the band formed by a pair of reference curves. This makes it more sensitive to outlying segments.

---

### Modified Epigraph Index

```python
from pyfda.depth import modified_epigraph_index_1d

depths = modified_epigraph_index_1d(data, ref_data)
```

Measures the proportion of curves in the reference sample that lie above the evaluated curve at each time point, integrated over the domain. Useful for detecting magnitude outliers.

---

### Random Projection Depth

```python
from pyfda.depth import random_projection_1d

depths = random_projection_1d(data, ref_data, n_proj=50)
```

Projects functional data onto random directions and averages univariate depth over many projections. Computationally efficient and consistent for detecting outliers in high dimensions.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_proj` | `50` | Number of random projections |

---

### Random Tukey Depth

```python
from pyfda.depth import random_tukey_1d

depths = random_tukey_1d(data, ref_data, n_proj=50)
```

Similar to random projection depth but uses Tukey (halfspace) depth for each univariate projection. More robust to skewed distributions.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_proj` | `50` | Number of random projections |

---

### Modal Depth

```python
from pyfda.depth import modal_1d

depths = modal_1d(data, ref_data, h=1.0)
```

Measures depth based on the local density of curves. The curve at the mode of the distribution has the highest modal depth.

$$
D_{\mathrm{modal}}(X) = \frac{1}{n} \sum_{j=1}^{n} K_h\bigl(\|X - X_j\|\bigr)
$$

where $K_h$ is a kernel function with bandwidth $h$.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `h` | `1.0` | Kernel bandwidth -- smaller values give sharper depth |

!!! warning "Bandwidth selection"
    The bandwidth `h` strongly affects results. A value too small yields noisy depth values; too large makes all depths similar. Experiment with different values or use the $L^2$ norm of your data to calibrate.

---

### Functional Spatial Depth

```python
from pyfda.depth import functional_spatial_1d

depths = functional_spatial_1d(data, ref_data, argvals=None)
```

Extension of multivariate spatial depth to functions. Based on the average spatial sign function:

$$
D_{\mathrm{sp}}(X) = 1 - \left\| \frac{1}{n} \sum_{j=1}^{n} S(X - X_j) \right\|
$$

where $S(f) = f / \|f\|$ is the spatial sign.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `argvals` | `None` | Evaluation points; if `None`, uses a uniform grid on $[0, 1]$ |

---

### Kernel Functional Spatial Depth

```python
from pyfda.depth import kernel_functional_spatial_1d

depths = kernel_functional_spatial_1d(data, ref_data, argvals, h=1.0)
```

A kernelized version of functional spatial depth that adds local weighting. Useful when the sample has heterogeneous density.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `argvals` | (required) | Evaluation points |
| `h` | `1.0` | Kernel bandwidth |

---

## 2D variants for surfaces

All depth measures that support surfaces (bivariate functional data) have `_2d` counterparts:

```python
from pyfda.depth import (
    fraiman_muniz_2d,
    modal_2d,
    random_projection_2d,
    random_tukey_2d,
    functional_spatial_2d,
    kernel_functional_spatial_2d,
)
```

For 2D data, `data` and `ref_data` are still 2D NumPy arrays of shape `(n, m)`, where each row is a flattened surface observed on a product grid.

## Comparison table

| Depth measure | Speed | Outlier sensitivity | Shape sensitive | Parameters |
|:---|:---:|:---:|:---:|:---|
| Fraiman-Muniz | Fast | Moderate | Low | `scale` |
| Modified Band | Fast | Good | Low | -- |
| Band | Fast | High | Low | -- |
| Modified Epigraph | Fast | Good (magnitude) | Low | -- |
| Random Projection | Moderate | Good | Moderate | `n_proj` |
| Random Tukey | Moderate | Very good | Moderate | `n_proj` |
| Modal | Moderate | Excellent | High | `h` |
| Functional Spatial | Moderate | Good | Moderate | `argvals` |
| Kernel Func. Spatial | Moderate | Very good | High | `argvals`, `h` |

!!! note "Which depth to choose?"
    - **General purpose**: Modified Band Depth (MBD) is the most widely used.
    - **Magnitude outliers**: Modified Epigraph Index or Fraiman-Muniz.
    - **Shape outliers**: Modal depth or Random Tukey.
    - **Skewed distributions**: Random Tukey depth handles asymmetry better.
    - **Speed priority**: Fraiman-Muniz and MBD scale well with $n$.

## Complete example: functional median and depth-based ordering

```python
import numpy as np
import matplotlib.pyplot as plt
from pyfda.simulation import simulate
from pyfda.depth import modified_band_1d, fraiman_muniz_1d, random_tukey_1d

# --- 1. Simulate data with an outlier ------------------------------------
argvals = np.linspace(0, 1, 150)
data = simulate(n=50, argvals=argvals, n_basis=5, seed=42)

# Inject 2 magnitude outliers
data[0] += 3.0
data[1] -= 2.5

# --- 2. Compute three different depths ------------------------------------
depths_mbd = modified_band_1d(data, data)
depths_fm  = fraiman_muniz_1d(data, data)
depths_rt  = random_tukey_1d(data, data, n_proj=100)

# --- 3. Functional median (deepest curve) ---------------------------------
median_idx = np.argmax(depths_mbd)
print(f"Functional median is curve {median_idx}")

# --- 4. Visualize depth ranking ------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for ax, depths, name in zip(axes,
                             [depths_mbd, depths_fm, depths_rt],
                             ["MBD", "Fraiman-Muniz", "Random Tukey"]):
    order = np.argsort(depths)  # low depth first (outliers)

    # Plot all curves, colored by depth
    for i in order:
        c = plt.cm.viridis(depths[i] / depths.max())
        ax.plot(argvals, data[i], color=c, alpha=0.5, lw=0.8)

    # Highlight median
    med = np.argmax(depths)
    ax.plot(argvals, data[med], "r-", lw=2.5, label=f"Median (#{med})")

    # Highlight two outliers
    for out_idx in order[:2]:
        ax.plot(argvals, data[out_idx], "k--", lw=1.5, alpha=0.7)

    ax.set_title(name)
    ax.legend(fontsize=8)

plt.suptitle("Depth-based ordering (bright = deep, dark = outlying)")
plt.tight_layout()
plt.show()
```

## Depth for outlier detection

Low depth values flag potential outliers. A common rule uses the boxplot of depth values:

```python
# Outlier detection via depth
q1 = np.percentile(depths_mbd, 25)
iqr = np.percentile(depths_mbd, 75) - q1
threshold = q1 - 1.5 * iqr

outlier_mask = depths_mbd < threshold
print(f"Detected outliers: {np.where(outlier_mask)[0]}")
```

!!! tip "Formal outlier detection"
    For production outlier detection, see the [Outlier Detection](../analyze/outlier-detection.md) guide which covers the functional boxplot, outliergram, and magnitude-shape plot -- all built on depth functions.

## Using depth as features

Depth values can serve as features for classification or as weights for robust estimation:

```python
# Weighted mean (depth-weighted, robust to outliers)
weights = depths_mbd / depths_mbd.sum()
robust_mean = np.average(data, axis=0, weights=weights)
```

## API summary

| Function | Extra parameters | Description |
|----------|-----------------|-------------|
| `fraiman_muniz_1d(data, ref_data, scale)` | `scale=True` | Integrated univariate depth |
| `modified_band_1d(data, ref_data)` | -- | Proportion of time inside bands |
| `band_1d(data, ref_data)` | -- | Full containment in bands |
| `modified_epigraph_index_1d(data, ref_data)` | -- | Epigraph-based depth |
| `random_projection_1d(data, ref_data, n_proj)` | `n_proj=50` | Averaged projected depth |
| `random_tukey_1d(data, ref_data, n_proj)` | `n_proj=50` | Projected Tukey halfspace depth |
| `modal_1d(data, ref_data, h)` | `h=1.0` | Kernel-based modal depth |
| `functional_spatial_1d(data, ref_data, argvals)` | `argvals=None` | Spatial sign depth |
| `kernel_functional_spatial_1d(data, ref_data, argvals, h)` | `argvals`, `h=1.0` | Kernelized spatial depth |

All `_1d` variants have `_2d` counterparts for surface data, imported from the same `pyfda.depth` module.
