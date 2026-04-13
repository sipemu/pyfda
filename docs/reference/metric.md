# fdars.metric

Distance metrics for functional data. "Self" functions compute an n-by-n distance matrix from a single dataset. "Cross" functions compute an n1-by-n2 matrix between two datasets.

## Functions

| Function | Description |
|----------|-------------|
| [`lp_self_1d`](#lp_self_1d) | Lp self-distance matrix, 1D |
| [`lp_cross_1d`](#lp_cross_1d) | Lp cross-distance matrix, 1D |
| [`lp_self_2d`](#lp_self_2d) | Lp self-distance matrix, 2D |
| [`lp_cross_2d`](#lp_cross_2d) | Lp cross-distance matrix, 2D |
| [`hausdorff_self_1d`](#hausdorff_self_1d) | Hausdorff self-distance, 1D |
| [`hausdorff_cross_1d`](#hausdorff_cross_1d) | Hausdorff cross-distance, 1D |
| [`hausdorff_self_2d`](#hausdorff_self_2d) | Hausdorff self-distance, 2D |
| [`hausdorff_cross_2d`](#hausdorff_cross_2d) | Hausdorff cross-distance, 2D |
| [`dtw_self_1d`](#dtw_self_1d) | Dynamic time warping self-distance |
| [`dtw_cross_1d`](#dtw_cross_1d) | Dynamic time warping cross-distance |
| [`soft_dtw_self_1d`](#soft_dtw_self_1d) | Soft-DTW self-distance |
| [`soft_dtw_cross_1d`](#soft_dtw_cross_1d) | Soft-DTW cross-distance |
| [`soft_dtw_div_self_1d`](#soft_dtw_div_self_1d) | Soft-DTW divergence self-distance |
| [`soft_dtw_div_cross_1d`](#soft_dtw_div_cross_1d) | Soft-DTW divergence cross-distance |
| [`fourier_self_1d`](#fourier_self_1d) | Fourier coefficient self-distance |
| [`fourier_cross_1d`](#fourier_cross_1d) | Fourier coefficient cross-distance |
| [`hshift_self_1d`](#hshift_self_1d) | Horizontal shift self-distance |
| [`hshift_cross_1d`](#hshift_cross_1d) | Horizontal shift cross-distance |

---

### `lp_self_1d`

```python
fdars.lp_self_1d(data, argvals, p=2.0)
```

Lp distance matrix for a single 1D functional dataset.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data matrix |
| `argvals` | `ndarray (m,)` | | Evaluation points for integration |
| `p` | `float` | `2.0` | Lp exponent; use `float('inf')` for L-infinity |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Symmetric distance matrix |

```python
t = np.linspace(0, 1, 100)
D = fdars.lp_self_1d(data, t, p=2.0)
```

---

### `lp_cross_1d`

```python
fdars.lp_cross_1d(data1, data2, argvals, p=2.0)
```

Lp distance matrix between two 1D functional datasets.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First dataset |
| `data2` | `ndarray (n2, m)` | | Second dataset |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `p` | `float` | `2.0` | Lp exponent |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

```python
D = fdars.lp_cross_1d(train, test, t, p=2.0)
```

---

### `lp_self_2d`

```python
fdars.lp_self_2d(data, argvals_s, argvals_t, p=2.0)
```

Lp self-distance matrix for 2D functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m1*m2)` | | Flattened 2D data |
| `argvals_s` | `ndarray (m1,)` | | First dimension grid |
| `argvals_t` | `ndarray (m2,)` | | Second dimension grid |
| `p` | `float` | `2.0` | Lp exponent |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

```python
D = fdars.lp_self_2d(data, s_grid, t_grid, p=2.0)
```

---

### `lp_cross_2d`

```python
fdars.lp_cross_2d(data1, data2, argvals_s, argvals_t, p=2.0)
```

Lp cross-distance matrix for 2D functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m1*m2)` | | First dataset |
| `data2` | `ndarray (n2, m1*m2)` | | Second dataset |
| `argvals_s` | `ndarray (m1,)` | | First dimension grid |
| `argvals_t` | `ndarray (m2,)` | | Second dimension grid |
| `p` | `float` | `2.0` | Lp exponent |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `hausdorff_self_1d`

```python
fdars.hausdorff_self_1d(data, argvals)
```

Hausdorff distance matrix for 1D functional data. Treats each curve as a set of (t, y(t)) points.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional data |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

```python
D = fdars.hausdorff_self_1d(data, t)
```

---

### `hausdorff_cross_1d`

```python
fdars.hausdorff_cross_1d(data1, data2, argvals)
```

Hausdorff cross-distance for 1D data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data1` | `ndarray (n1, m)` | First dataset |
| `data2` | `ndarray (n2, m)` | Second dataset |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `hausdorff_self_2d`

```python
fdars.hausdorff_self_2d(data, argvals_s, argvals_t)
```

Hausdorff self-distance for 2D data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m1*m2)` | Flattened 2D data |
| `argvals_s` | `ndarray (m1,)` | First dimension grid |
| `argvals_t` | `ndarray (m2,)` | Second dimension grid |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

---

### `hausdorff_cross_2d`

```python
fdars.hausdorff_cross_2d(data1, data2, argvals_s, argvals_t)
```

Hausdorff cross-distance for 2D data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data1` | `ndarray (n1, m1*m2)` | First dataset |
| `data2` | `ndarray (n2, m1*m2)` | Second dataset |
| `argvals_s` | `ndarray (m1,)` | First dimension grid |
| `argvals_t` | `ndarray (m2,)` | Second dimension grid |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `dtw_self_1d`

```python
fdars.dtw_self_1d(data, p=2.0, w=0)
```

Dynamic Time Warping self-distance matrix for 1D data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `p` | `float` | `2.0` | Lp exponent for pointwise cost |
| `w` | `int` | `0` | Sakoe-Chiba band width; `0` means no constraint |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

```python
D = fdars.dtw_self_1d(data, p=2.0, w=10)
```

---

### `dtw_cross_1d`

```python
fdars.dtw_cross_1d(data1, data2, p=2.0, w=0)
```

DTW cross-distance for 1D data (curves may have different lengths).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m1)` | | First dataset |
| `data2` | `ndarray (n2, m2)` | | Second dataset |
| `p` | `float` | `2.0` | Lp exponent |
| `w` | `int` | `0` | Sakoe-Chiba band width |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `soft_dtw_self_1d`

```python
fdars.soft_dtw_self_1d(data, gamma=1.0)
```

Soft-DTW distance matrix (differentiable approximation to DTW).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `gamma` | `float` | `1.0` | Smoothing parameter (smaller = closer to DTW) |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

```python
D = fdars.soft_dtw_self_1d(data, gamma=0.1)
```

---

### `soft_dtw_cross_1d`

```python
fdars.soft_dtw_cross_1d(data1, data2, gamma=1.0)
```

Soft-DTW cross-distance for 1D data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First dataset |
| `data2` | `ndarray (n2, m)` | | Second dataset |
| `gamma` | `float` | `1.0` | Smoothing parameter |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `soft_dtw_div_self_1d`

```python
fdars.soft_dtw_div_self_1d(data, gamma=1.0)
```

Soft-DTW divergence self-distance. Bias-corrected version of Soft-DTW that is a proper divergence.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `gamma` | `float` | `1.0` | Smoothing parameter |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Divergence matrix |

```python
D = fdars.soft_dtw_div_self_1d(data, gamma=1.0)
```

---

### `soft_dtw_div_cross_1d`

```python
fdars.soft_dtw_div_cross_1d(data1, data2, gamma=1.0)
```

Soft-DTW divergence cross-distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First dataset |
| `data2` | `ndarray (n2, m)` | | Second dataset |
| `gamma` | `float` | `1.0` | Smoothing parameter |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Divergence matrix |

---

### `fourier_self_1d`

```python
fdars.fourier_self_1d(data, n_basis=5)
```

Distance based on Fourier coefficients. Projects curves onto a Fourier basis and computes Euclidean distances in coefficient space.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `n_basis` | `int` | `5` | Number of Fourier basis functions |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

```python
D = fdars.fourier_self_1d(data, n_basis=7)
```

---

### `fourier_cross_1d`

```python
fdars.fourier_cross_1d(data1, data2, n_basis=5)
```

Fourier coefficient cross-distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First dataset |
| `data2` | `ndarray (n2, m)` | | Second dataset |
| `n_basis` | `int` | `5` | Number of Fourier basis functions |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `hshift_self_1d`

```python
fdars.hshift_self_1d(data, argvals, max_shift=0)
```

Horizontal shift distance. Finds the optimal horizontal translation minimizing L2 distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `max_shift` | `int` | `0` | Maximum shift in grid points; `0` means `m/4` |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Distance matrix |

```python
D = fdars.hshift_self_1d(data, t, max_shift=20)
```

---

### `hshift_cross_1d`

```python
fdars.hshift_cross_1d(data1, data2, argvals, max_shift=0)
```

Horizontal shift cross-distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First dataset |
| `data2` | `ndarray (n2, m)` | | Second dataset |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `max_shift` | `int` | `0` | Maximum shift in grid points; `0` means `m/4` |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |
