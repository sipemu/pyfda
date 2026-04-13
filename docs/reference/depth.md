# fdars.depth

Depth measures for functional data. All functions compute depth values for observations in `data` relative to a reference sample `ref_data`.

## Functions

| Function | Description |
|----------|-------------|
| [`fraiman_muniz_1d`](#fraiman_muniz_1d) | Fraiman-Muniz depth for 1D data |
| [`fraiman_muniz_2d`](#fraiman_muniz_2d) | Fraiman-Muniz depth for 2D data |
| [`modal_1d`](#modal_1d) | Modal depth for 1D data |
| [`modal_2d`](#modal_2d) | Modal depth for 2D data |
| [`random_projection_1d`](#random_projection_1d) | Random projection depth for 1D data |
| [`random_projection_2d`](#random_projection_2d) | Random projection depth for 2D data |
| [`random_tukey_1d`](#random_tukey_1d) | Random Tukey depth for 1D data |
| [`random_tukey_2d`](#random_tukey_2d) | Random Tukey depth for 2D data |
| [`band_1d`](#band_1d) | Band depth for 1D data |
| [`modified_band_1d`](#modified_band_1d) | Modified band depth for 1D data |
| [`modified_epigraph_index_1d`](#modified_epigraph_index_1d) | Modified epigraph index for 1D data |
| [`functional_spatial_1d`](#functional_spatial_1d) | Functional spatial depth for 1D data |
| [`functional_spatial_2d`](#functional_spatial_2d) | Functional spatial depth for 2D data |
| [`kernel_functional_spatial_1d`](#kernel_functional_spatial_1d) | Kernel functional spatial depth for 1D data |
| [`kernel_functional_spatial_2d`](#kernel_functional_spatial_2d) | Kernel functional spatial depth for 2D data |

---

### `fraiman_muniz_1d`

```python
fdars.fraiman_muniz_1d(data, ref_data, scale=True)
```

Fraiman-Muniz integrated depth for 1D functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `scale` | `bool` | `True` | Whether to scale depth values |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.fraiman_muniz_1d(data, data)  # self-referencing
```

---

### `fraiman_muniz_2d`

```python
fdars.fraiman_muniz_2d(data, ref_data, scale=True)
```

Fraiman-Muniz depth for 2D (surface) functional data. Same interface as `fraiman_muniz_1d`.

---

### `modal_1d`

```python
fdars.modal_1d(data, ref_data, h=1.0)
```

Modal depth for 1D functional data. Uses kernel density estimation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `h` | `float` | `1.0` | Kernel bandwidth |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.modal_1d(data, data, h=0.5)
```

---

### `modal_2d`

```python
fdars.modal_2d(data, ref_data, h=1.0)
```

Modal depth for 2D data. Same interface as `modal_1d`.

---

### `random_projection_1d`

```python
fdars.random_projection_1d(data, ref_data, n_proj=50)
```

Random projection depth for 1D functional data. Projects onto random directions and averages univariate depth.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `n_proj` | `int` | `50` | Number of random projections |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.random_projection_1d(data, data, n_proj=100)
```

---

### `random_projection_2d`

```python
fdars.random_projection_2d(data, ref_data, n_proj=50)
```

Random projection depth for 2D data. Same interface as `random_projection_1d`.

---

### `random_tukey_1d`

```python
fdars.random_tukey_1d(data, ref_data, n_proj=50)
```

Random Tukey (halfspace) depth for 1D functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `n_proj` | `int` | `50` | Number of random projections |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.random_tukey_1d(data, data, n_proj=50)
```

---

### `random_tukey_2d`

```python
fdars.random_tukey_2d(data, ref_data, n_proj=50)
```

Random Tukey depth for 2D data. Same interface as `random_tukey_1d`.

---

### `band_1d`

```python
fdars.band_1d(data, ref_data)
```

Band depth for 1D functional data. Measures the proportion of bands (defined by pairs of reference curves) that contain the target curve.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | Reference sample |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.band_1d(data, data)
```

---

### `modified_band_1d`

```python
fdars.modified_band_1d(data, ref_data)
```

Modified band depth for 1D data. Relaxed version of band depth that measures the proportion of time a curve is inside each band.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | Reference sample |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.modified_band_1d(data, data)
```

---

### `modified_epigraph_index_1d`

```python
fdars.modified_epigraph_index_1d(data, ref_data)
```

Modified epigraph index for 1D data. Measures how often each curve lies above the reference curves.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | Reference sample |

| Returns | Type | Description |
|---------|------|-------------|
| index | `ndarray (n,)` | Epigraph index values |

```python
mei = fdars.modified_epigraph_index_1d(data, data)
```

---

### `functional_spatial_1d`

```python
fdars.functional_spatial_1d(data, ref_data, argvals=None)
```

Functional spatial depth for 1D data. Extends multivariate spatial depth to functional setting.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `argvals` | `ndarray (m,)` or `None` | `None` | Evaluation points; if `None`, uses uniform [0,1] grid |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
t = np.linspace(0, 1, 100)
depth = fdars.functional_spatial_1d(data, data, argvals=t)
```

---

### `functional_spatial_2d`

```python
fdars.functional_spatial_2d(data, ref_data)
```

Functional spatial depth for 2D data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | Reference sample |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.functional_spatial_2d(data, data)
```

---

### `kernel_functional_spatial_1d`

```python
fdars.kernel_functional_spatial_1d(data, ref_data, argvals, h=1.0)
```

Kernel functional spatial depth for 1D data. Uses a Gaussian kernel with bandwidth `h`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `h` | `float` | `1.0` | Kernel bandwidth |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
t = np.linspace(0, 1, 100)
depth = fdars.kernel_functional_spatial_1d(data, data, t, h=0.5)
```

---

### `kernel_functional_spatial_2d`

```python
fdars.kernel_functional_spatial_2d(data, ref_data, h=1.0)
```

Kernel functional spatial depth for 2D data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Data to compute depth for |
| `ref_data` | `ndarray (n_ref, m)` | | Reference sample |
| `h` | `float` | `1.0` | Kernel bandwidth |

| Returns | Type | Description |
|---------|------|-------------|
| depth | `ndarray (n,)` | Depth values |

```python
depth = fdars.kernel_functional_spatial_2d(data, data, h=0.5)
```
