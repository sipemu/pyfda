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

---

## DTW toolkit and elastic time-series distances

Signatures only; see the guide pages for parameters, semantics and worked examples. Every function with `window=` also takes `radius=`, `window_fraction=` and `max_slope=` (see [DTW Search & Averaging](../represent/dtw-toolkit.md#global-windows)).

| Function | Returns | Guide |
|----------|---------|-------|
| `dtw_path(x, y, p=2.0, window="none")` | `{"path", "cost"}` | [DTW toolkit](../represent/dtw-toolkit.md#paths-and-windowed-distances) |
| `dtw_distance_windowed(x, y, p=2.0, window="none")` | `float` | [DTW toolkit](../represent/dtw-toolkit.md#paths-and-windowed-distances) |
| `dtw_window_mask(n, m, window="none")` | bool `(n, m)` | [DTW toolkit](../represent/dtw-toolkit.md#global-windows) |
| `soft_dtw_distance_windowed(x, y, gamma=1.0, window="none")` | `float` | [DTW toolkit](../represent/dtw-toolkit.md#paths-and-windowed-distances) |
| `soft_dtw_alignment(x, y, gamma=1.0, window="none")` | `{"value", "alignment"}` | [DTW toolkit](../represent/dtw-toolkit.md#paths-and-windowed-distances) |
| `soft_dtw_barycenter(data, gamma=1.0, max_iter=100, tol=1e-6, n_restarts=10, seed=0)` | `{"barycenter", "n_iter", "converged"}` | [DTW toolkit](../represent/dtw-toolkit.md#averaging-under-dtw) |
| `dtw_barycenter_averaging(data, max_iter=30, tol=1e-5, window="none", init=None, barycenter_size=None, weights=None)` | `{"barycenter", "cost", "n_iter", "converged"}` | [DTW toolkit](../represent/dtw-toolkit.md#averaging-under-dtw) |
| `lb_kim(x, y, p=2.0)`, `lb_keogh(query, candidate, ...)`, `lb_improved(x, y, ...)`, `lb_webb(x, y, ...)`, `lb_enhanced(x, y, v, ...)` | `float` | [DTW toolkit](../represent/dtw-toolkit.md#lower-bounds-and-early-abandoning) |
| `lb_envelope(x, radius)`, `lb_envelope_windowed(y, query_len, window="none")` | `{"lower", "upper"}` | [DTW toolkit](../represent/dtw-toolkit.md#lower-bounds-and-early-abandoning) |
| `dtw_distance_early_abandon(x, y, cutoff, p=2.0, window="none")` | `float` or `None` | [DTW toolkit](../represent/dtw-toolkit.md#lower-bounds-and-early-abandoning) |
| `dtw_nearest_neighbor(queries, references, p=2.0, window="none")` | `{"indices", "distances", "stats"}` | [DTW toolkit](../represent/dtw-toolkit.md#exact-nearest-neighbour-search) |
| `dtw_k_nearest_neighbors(queries, references, k=1, p=2.0, window="none")` | `{"indices", "distances", "stats"}` | [DTW toolkit](../represent/dtw-toolkit.md#exact-nearest-neighbour-search) |
| `gak_triangular(x, y, sigma, triangular=0)` | `float` | [DTW toolkit](../represent/dtw-toolkit.md#triangular-global-alignment-kernel) |
| `dtw_distance_multivariate`, `dtw_path_multivariate`, `dtw_pairwise_distance_multivariate`, `dtw_barycenter_averaging_multivariate` | as the univariate versions, on `(d, m)` series | [DTW toolkit](../represent/dtw-toolkit.md#multichannel-dtw) |
| `elastic_ts_distance(x, y, metric, ...)` | `float` | [Elastic distances](../represent/elastic-ts-distances.md) |
| `elastic_ts_pairwise_distance(data, metric, other=None, ...)` | `(n, n)` or `(n, n_other)` | [Elastic distances](../represent/elastic-ts-distances.md) |
| `elastic_ts_cost_matrix(x, y, metric, ...)` | cost matrix | [Elastic distances](../represent/elastic-ts-distances.md) |
| `elastic_ts_alignment_path(x, y, metric, ...)` | `{"path", "distance"}` | [Elastic distances](../represent/elastic-ts-distances.md) |
| `elastic_ts_*_multivariate(...)` | as above, on `(d, m)` series | [Elastic distances](../represent/elastic-ts-distances.md#multichannel-series) |
| `sbd(x, y)` | `{"distance", "shift"}` | [Elastic distances](../represent/elastic-ts-distances.md#shape-based-distance-sbd) |
| `sbd_distance_matrix(data)` | `(n, n)` | [Elastic distances](../represent/elastic-ts-distances.md#shape-based-distance-sbd) |

`gak_gram_matrix(data, sigma=None, triangular=0)` and `gak_gram_train(data, sigma=None, triangular=0)` take the triangular band parameter `T` as well; `gak_gram_predict` reuses the training value.
