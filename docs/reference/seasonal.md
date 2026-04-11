# pyfda.seasonal

Seasonal analysis: period detection, peak detection, STL decomposition, and seasonal strength.

## Functions

| Function | Description |
|----------|-------------|
| [`sazed`](#sazed) | SAZED period detection |
| [`autoperiod`](#autoperiod) | Autoperiod algorithm |
| [`cfd_autoperiod`](#cfd_autoperiod) | CFD autoperiod with clustering |
| [`detect_peaks`](#detect_peaks) | Peak detection in functional data |
| [`stl_decompose`](#stl_decompose) | STL seasonal decomposition |
| [`seasonal_strength`](#seasonal_strength) | Seasonal strength measure |

---

### `sazed`

```python
pyfda.sazed(data, argvals, tolerance=None)
```

SAZED period detection algorithm. Combines multiple approaches (ACF, zero-crossings, extrema, etc.) and returns a consensus period.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `tolerance` | `float` or `None` | `None` | Relative tolerance for period matching; `None` defaults to 0.05 |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `period`, `confidence`, `agreeing_components` |

```python
t = np.linspace(0, 10, 500)
result = pyfda.sazed(data, t)
print(f"Period: {result['period']:.2f}, confidence: {result['confidence']:.2f}")
```

---

### `autoperiod`

```python
pyfda.autoperiod(data, argvals, n_candidates=None, gradient_steps=None)
```

Autoperiod algorithm: uses FFT to find candidate periods, then validates with ACF.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_candidates` | `int` or `None` | `None` | Max FFT peaks to consider; `None` defaults to 5 |
| `gradient_steps` | `int` or `None` | `None` | Gradient ascent refinement steps; `None` defaults to 10 |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `period`, `confidence`, `fft_power`, `acf_validation` |

```python
result = pyfda.autoperiod(data, t)
print(f"Detected period: {result['period']:.2f}")
```

---

### `cfd_autoperiod`

```python
pyfda.cfd_autoperiod(data, argvals, cluster_tolerance=None, min_cluster_size=None)
```

CFD autoperiod with clustering-based consensus among per-curve period estimates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `cluster_tolerance` | `float` or `None` | `None` | Clustering tolerance; `None` defaults to 0.1 |
| `min_cluster_size` | `int` or `None` | `None` | Minimum cluster size; `None` defaults to 1 |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `period`, `confidence`, `periods` (array), `confidences` (array) |

```python
result = pyfda.cfd_autoperiod(data, t)
```

---

### `detect_peaks`

```python
pyfda.detect_peaks(data, argvals, min_distance=None, min_prominence=None,
                   smooth_first=False, smooth_nbasis=None)
```

Detect peaks in functional data curves.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `min_distance` | `float` or `None` | `None` | Minimum distance between peaks |
| `min_prominence` | `float` or `None` | `None` | Minimum peak prominence |
| `smooth_first` | `bool` | `False` | Whether to smooth before detection |
| `smooth_nbasis` | `int` or `None` | `None` | Number of basis functions for smoothing |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `peaks` (list of lists of (time, value, prominence) tuples), `mean_period` |

```python
result = pyfda.detect_peaks(data, t, min_prominence=0.5)
for curve_peaks in result["peaks"]:
    for time, value, prominence in curve_peaks:
        print(f"  t={time:.2f}, val={value:.2f}")
```

---

### `stl_decompose`

```python
pyfda.stl_decompose(data, period, s_window=None, t_window=None, robust=False)
```

STL (Seasonal and Trend decomposition using Loess) for functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `period` | `int` | | Seasonal period in grid points |
| `s_window` | `int` or `None` | `None` | Seasonal smoothing window; `None` for auto |
| `t_window` | `int` or `None` | `None` | Trend smoothing window; `None` for auto |
| `robust` | `bool` | `False` | Use robust weights to downweight outliers |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `trend` (n, m), `seasonal` (n, m), `remainder` (n, m) |

```python
result = pyfda.stl_decompose(data, period=24, robust=True)
trend = result["trend"]
```

---

### `seasonal_strength`

```python
pyfda.seasonal_strength(data, argvals, period, method="variance")
```

Compute the strength of seasonality in functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `period` | `float` | | Estimated period |
| `method` | `str` | `"variance"` | `"variance"` or `"spectral"` |

| Returns | Type | Description |
|---------|------|-------------|
| strength | `float` | Seasonal strength in [0, 1]; higher means stronger seasonality |

```python
strength = pyfda.seasonal_strength(data, t, period=2*np.pi)
print(f"Seasonal strength: {strength:.3f}")
```
