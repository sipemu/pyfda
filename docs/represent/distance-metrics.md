# Distance Metrics

Distance (and dissimilarity) measures between curves are fundamental building blocks for clustering, classification, nonparametric regression, and outlier detection. pyfda provides a comprehensive set of metrics -- from classical $L^p$ norms to elastic distances that factor out time warping.

## Self vs cross distances

Every metric comes in two flavors:

| Variant | Signature | Output shape | Description |
|---------|-----------|:---:|-------------|
| **self** | `*_self_1d(data, ...)` | $(n, n)$ | Pairwise distances within one sample |
| **cross** | `*_cross_1d(data1, data2, ...)` | $(n_1, n_2)$ | Distances between two samples |

Both return a NumPy array. Self-distance matrices are symmetric with zeros on the diagonal.

## $L^p$ distances

The most common functional distances, defined as

$$
d_p(X, Y) = \left( \int_{\mathcal{T}} |X(t) - Y(t)|^p \, dt \right)^{1/p}
$$

with numerical integration via the trapezoidal rule.

```python
import numpy as np
from pyfda.metric import lp_self_1d, lp_cross_1d

argvals = np.linspace(0, 1, 200)

# L2 distance (default)
D_l2 = lp_self_1d(data, argvals, p=2.0)

# L1 distance (more robust to spikes)
D_l1 = lp_self_1d(data, argvals, p=1.0)

# L-infinity (supremum norm)
D_linf = lp_self_1d(data, argvals, p=float('inf'))
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `data` | (required) | Curves, shape (n, m) |
| `argvals` | (required) | Evaluation grid, length m |
| `p` | `2.0` | $L^p$ exponent. Use `float('inf')` for the sup norm |

### Cross distance example

```python
# Distance between training and test curves
D_cross = lp_cross_1d(train_data, test_data, argvals, p=2.0)
print(D_cross.shape)  # (n_train, n_test)
```

### 2D variants

For surface data observed on a product grid:

```python
from pyfda.metric import lp_self_2d, lp_cross_2d

D_2d = lp_self_2d(surface_data, argvals_s, argvals_t, p=2.0)
```

---

## Hausdorff distance

The Hausdorff distance treats each curve as a set of points in $(t, X(t))$ space and measures the worst-case mismatch:

$$
d_H(X, Y) = \max\!\left(\sup_t \inf_s \bigl\|(t, X(t)) - (s, Y(s))\bigr\|,\; \sup_s \inf_t \bigl\|(t, X(t)) - (s, Y(s))\bigr\|\right)
$$

```python
from pyfda.metric import hausdorff_self_1d, hausdorff_cross_1d

D_haus = hausdorff_self_1d(data, argvals)
```

| Property | Value |
|----------|-------|
| Metric | Yes (true metric) |
| Shift invariant | No |
| Robust to phase variation | Somewhat |

!!! info "When to use Hausdorff"
    Hausdorff distance is useful when curves have different support or when you care about the worst-case pointwise discrepancy. It is less sensitive to small localized differences than $L^2$.

### 2D variants

```python
from pyfda.metric import hausdorff_self_2d, hausdorff_cross_2d
```

---

## Dynamic Time Warping (DTW)

DTW finds the optimal nonlinear alignment between two sequences that minimizes the total cost. Unlike $L^p$ distances, DTW is invariant to local time shifts.

$$
d_{\mathrm{DTW}}(X, Y) = \min_{\pi} \left( \sum_{(i,j) \in \pi} |X(t_i) - Y(t_j)|^p \right)^{1/p}
$$

where $\pi$ is a monotone warping path.

```python
from pyfda.metric import dtw_self_1d, dtw_cross_1d

# Unconstrained DTW
D_dtw = dtw_self_1d(data, p=2.0)

# With Sakoe-Chiba band (limits warping to w grid points)
D_dtw_sc = dtw_self_1d(data, p=2.0, w=10)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `p` | `2.0` | Cost exponent |
| `w` | `0` | Sakoe-Chiba band width. `0` = no constraint (full warping) |

!!! tip "Sakoe-Chiba band"
    Setting `w` to a small value (e.g., 5-20 % of the sequence length) serves two purposes:

    1. **Speed** -- constrains the DP search from $O(m^2)$ to $O(m \cdot w)$.
    2. **Prevents pathological warps** -- disallows extreme temporal distortions.

---

## Soft-DTW

Soft-DTW replaces the hard `min` in DTW with a differentiable soft-minimum, making it suitable as a loss function for gradient-based optimization.

$$
d_{\mathrm{SDTW}}^{\gamma}(X, Y) = \mathrm{soft\text{-}min}_{\pi}^{\gamma} \sum_{(i,j) \in \pi} |X(t_i) - Y(t_j)|^2
$$

where $\mathrm{soft\text{-}min}^{\gamma}$ uses the log-sum-exp with smoothing parameter $\gamma$.

```python
from pyfda.metric import soft_dtw_self_1d, soft_dtw_cross_1d

D_sdtw = soft_dtw_self_1d(data, gamma=1.0)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `gamma` | `1.0` | Smoothing parameter. As $\gamma \to 0$, Soft-DTW $\to$ DTW |

!!! warning "Soft-DTW is not a metric"
    Soft-DTW does not satisfy the triangle inequality. If you need a proper metric, use the **Soft-DTW divergence** instead:

    ```python
    from pyfda.metric import soft_dtw_div_self_1d, soft_dtw_div_cross_1d

    D_div = soft_dtw_div_self_1d(data, gamma=1.0)
    ```

    The divergence is defined as $\tilde{d}_{\gamma}(X, Y) = d_{\gamma}(X, Y) - \frac{1}{2}\bigl[d_{\gamma}(X, X) + d_{\gamma}(Y, Y)\bigr]$ and is non-negative with zero diagonal.

---

## Fourier coefficient distance

Compares curves through their Fourier representations. Two curves are close if their first `n_basis` Fourier coefficients are similar.

$$
d_F(X, Y) = \left\| \hat{X} - \hat{Y} \right\|_2
$$

where $\hat{X}, \hat{Y} \in \mathbb{R}^{n_{\text{basis}}}$ are truncated Fourier coefficient vectors.

```python
from pyfda.metric import fourier_self_1d, fourier_cross_1d

D_fourier = fourier_self_1d(data, n_basis=5)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_basis` | `5` | Number of Fourier coefficients to compare |

| Property | Value |
|----------|-------|
| Metric | Yes |
| Shift invariant | Depends on `n_basis` |
| Best for | Periodic data, frequency-domain comparison |

---

## Horizontal shift distance

Finds the uniform horizontal shift that best aligns two curves and reports the residual:

$$
d_{\mathrm{shift}}(X, Y) = \min_{|\delta| \le \Delta} \|X(t) - Y(t - \delta)\|_2
$$

```python
from pyfda.metric import hshift_self_1d, hshift_cross_1d

D_shift = hshift_self_1d(data, argvals, max_shift=0)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_shift` | `0` | Maximum shift in grid points. `0` = $m/4$ |

| Property | Value |
|----------|-------|
| Metric | Semimetric (triangle inequality may fail) |
| Shift invariant | Yes (by construction) |
| Best for | Data with simple horizontal misalignment |

---

## Elastic distances

The elastic (Fisher-Rao) framework separates **amplitude** (vertical) and **phase** (horizontal) variation via the Square Root Slope Function (SRSF) transform. These distances live in the `pyfda.alignment` module.

```python
from pyfda.alignment import elastic_distance, amplitude_distance, phase_distance
```

### Elastic distance

The total elastic distance combines amplitude and phase:

```python
d = elastic_distance(curve1, curve2, argvals, lambda_=0.0)
```

### Amplitude distance

Measures only the vertical shape difference after optimal alignment:

```python
d_amp = amplitude_distance(curve1, curve2, argvals, lambda_=0.0)
```

### Phase distance

Measures only the warping needed to align two curves:

```python
d_phase = phase_distance(curve1, curve2, argvals, lambda_=0.0)
```

### Elastic distance matrices

For pairwise computations across a full sample:

```python
from pyfda.alignment import elastic_self_distance_matrix, elastic_cross_distance_matrix

D_elastic = elastic_self_distance_matrix(data, argvals, lambda_=0.0)
D_cross   = elastic_cross_distance_matrix(train_data, test_data, argvals)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `lambda_` | `0.0` | Regularization -- penalizes extreme warping |

!!! note "Performance"
    Elastic distance matrices require $O(n^2)$ pairwise alignments, each involving a dynamic programming step. For large datasets, consider using a subset or the Sakoe-Chiba-constrained DTW as a faster alternative.

---

## Metric properties comparison

| Metric | True metric | Shift invariant | Scale invariant | Handles phase variation | Speed |
|:---|:---:|:---:|:---:|:---:|:---:|
| $L^p$ | Yes | No | No | No | Very fast |
| Hausdorff | Yes | No | No | Partially | Fast |
| DTW | Yes | No | No | Yes | Moderate |
| Soft-DTW | No | No | No | Yes | Moderate |
| Soft-DTW Divergence | Semi | No | No | Yes | Moderate |
| Fourier | Yes | Partially | No | No | Fast |
| Horizontal Shift | Semi | Yes | No | Yes (rigid) | Moderate |
| Elastic (Fisher-Rao) | Yes | No | No | Yes (optimal) | Slow |
| Amplitude | Semi | No | No | Yes | Slow |
| Phase | Yes | No | No | Yes | Slow |

---

## Method selection guide

```
Is your data periodic?
  YES --> Fourier coefficient distance
  NO  --> continue

Is there significant horizontal misalignment?
  NO  --> L2 distance (fast, standard choice)
  YES --> continue

Is the misalignment a simple global shift?
  YES --> Horizontal shift distance
  NO  --> continue

Do you need a true metric?
  YES --> DTW (with Sakoe-Chiba band) or Elastic distance
  NO  --> Soft-DTW (differentiable, good for optimization)

Do you need amplitude/phase decomposition?
  YES --> Elastic framework (amplitude_distance + phase_distance)
  NO  --> DTW is simpler and faster
```

## Complete example: comparing metrics

```python
import numpy as np
import matplotlib.pyplot as plt
from pyfda.simulation import simulate
from pyfda.metric import lp_self_1d, dtw_self_1d, hausdorff_self_1d, fourier_self_1d

# --- 1. Simulate data with phase variation --------------------------------
argvals = np.linspace(0, 1, 150)
data = simulate(n=30, argvals=argvals, n_basis=3, seed=123)

# Add random horizontal shifts to half the curves
shifted_data = data.copy()
for i in range(15, 30):
    shift = np.random.randint(-10, 10)
    shifted_data[i] = np.roll(data[i], shift)

# --- 2. Compute distance matrices ----------------------------------------
D_l2      = lp_self_1d(shifted_data, argvals, p=2.0)
D_dtw     = dtw_self_1d(shifted_data, p=2.0, w=15)
D_haus    = hausdorff_self_1d(shifted_data, argvals)
D_fourier = fourier_self_1d(shifted_data, n_basis=7)

# --- 3. Visualize --------------------------------------------------------
fig, axes = plt.subplots(1, 4, figsize=(18, 4))

for ax, D, name in zip(axes,
                        [D_l2, D_dtw, D_haus, D_fourier],
                        ["L2", "DTW (w=15)", "Hausdorff", "Fourier"]):
    im = ax.imshow(D, cmap="viridis", aspect="auto")
    ax.set_title(name)
    plt.colorbar(im, ax=ax, fraction=0.046)

plt.suptitle("Distance matrix comparison")
plt.tight_layout()
plt.show()
```

## Using distance matrices downstream

Distance matrices plug directly into several pyfda methods:

```python
from pyfda.regression import fregre_np
from pyfda.clustering import kmeans_fd

# Nonparametric kernel regression from distances
D = lp_self_1d(data, argvals, p=2.0)
reg = fregre_np(D, response, h=0.0)  # h=0 -> automatic bandwidth

# Functional k-means also accepts precomputed distances
# (see the clustering documentation)
```

## API summary

### `pyfda.metric`

| Function | Key parameters | Description |
|----------|---------------|-------------|
| `lp_self_1d(data, argvals, p)` | `p=2.0` | $L^p$ self distances |
| `lp_cross_1d(data1, data2, argvals, p)` | `p=2.0` | $L^p$ cross distances |
| `lp_self_2d(data, argvals_s, argvals_t, p)` | `p=2.0` | $L^p$ self for surfaces |
| `lp_cross_2d(...)` | `p=2.0` | $L^p$ cross for surfaces |
| `hausdorff_self_1d(data, argvals)` | -- | Hausdorff self |
| `hausdorff_cross_1d(data1, data2, argvals)` | -- | Hausdorff cross |
| `hausdorff_self_2d(data, argvals_s, argvals_t)` | -- | Hausdorff self for surfaces |
| `hausdorff_cross_2d(...)` | -- | Hausdorff cross for surfaces |
| `dtw_self_1d(data, p, w)` | `p=2.0`, `w=0` | DTW self |
| `dtw_cross_1d(data1, data2, p, w)` | `p=2.0`, `w=0` | DTW cross |
| `soft_dtw_self_1d(data, gamma)` | `gamma=1.0` | Soft-DTW self |
| `soft_dtw_cross_1d(data1, data2, gamma)` | `gamma=1.0` | Soft-DTW cross |
| `soft_dtw_div_self_1d(data, gamma)` | `gamma=1.0` | Soft-DTW divergence self |
| `soft_dtw_div_cross_1d(data1, data2, gamma)` | `gamma=1.0` | Soft-DTW divergence cross |
| `fourier_self_1d(data, n_basis)` | `n_basis=5` | Fourier coefficient self |
| `fourier_cross_1d(data1, data2, n_basis)` | `n_basis=5` | Fourier coefficient cross |
| `hshift_self_1d(data, argvals, max_shift)` | `max_shift=0` | Horizontal shift self |
| `hshift_cross_1d(data1, data2, argvals, max_shift)` | `max_shift=0` | Horizontal shift cross |

### `pyfda.alignment` (elastic distances)

| Function | Key parameters | Description |
|----------|---------------|-------------|
| `elastic_distance(c1, c2, argvals, lambda_)` | `lambda_=0.0` | Pairwise elastic distance |
| `amplitude_distance(c1, c2, argvals, lambda_)` | `lambda_=0.0` | Amplitude component only |
| `phase_distance(c1, c2, argvals, lambda_)` | `lambda_=0.0` | Phase component only |
| `elastic_self_distance_matrix(data, argvals, lambda_)` | `lambda_=0.0` | Full elastic distance matrix |
| `elastic_cross_distance_matrix(d1, d2, argvals, lambda_)` | `lambda_=0.0` | Cross elastic distance matrix |
