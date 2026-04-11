# pyfda.smoothing

Nonparametric smoothing methods for scalar-valued data.

## Functions

| Function | Description |
|----------|-------------|
| [`nadaraya_watson`](#nadaraya_watson) | Nadaraya-Watson kernel smoother |
| [`local_linear`](#local_linear) | Local linear regression smoother |
| [`local_polynomial`](#local_polynomial) | Local polynomial regression smoother |
| [`knn_smoother`](#knn_smoother) | K-nearest neighbors smoother |
| [`optim_bandwidth`](#optim_bandwidth) | Optimal bandwidth selection via cross-validation |

---

### `nadaraya_watson`

```python
pyfda.nadaraya_watson(x, y, x_new, bandwidth, kernel="gaussian")
```

Nadaraya-Watson kernel regression estimator.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | `ndarray (n,)` | | Predictor values |
| `y` | `ndarray (n,)` | | Response values |
| `x_new` | `ndarray (m,)` | | Points at which to evaluate the smoother |
| `bandwidth` | `float` | | Kernel bandwidth |
| `kernel` | `str` | `"gaussian"` | `"gaussian"`, `"epanechnikov"`, or `"tricube"` |

| Returns | Type | Description |
|---------|------|-------------|
| smoothed | `ndarray (m,)` | Smoothed values at `x_new` |

```python
x, y = np.sort(np.random.rand(100)), np.random.randn(100)
x_new = np.linspace(0, 1, 200)
y_hat = pyfda.nadaraya_watson(x, y, x_new, bandwidth=0.1)
```

---

### `local_linear`

```python
pyfda.local_linear(x, y, x_new, bandwidth, kernel="gaussian")
```

Local linear regression smoother. Fits a linear model in a kernel-weighted neighborhood around each evaluation point.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | `ndarray (n,)` | | Predictor values |
| `y` | `ndarray (n,)` | | Response values |
| `x_new` | `ndarray (m,)` | | Evaluation points |
| `bandwidth` | `float` | | Kernel bandwidth |
| `kernel` | `str` | `"gaussian"` | `"gaussian"`, `"epanechnikov"`, or `"tricube"` |

| Returns | Type | Description |
|---------|------|-------------|
| smoothed | `ndarray (m,)` | Smoothed values at `x_new` |

```python
y_hat = pyfda.local_linear(x, y, x_new, bandwidth=0.1)
```

---

### `local_polynomial`

```python
pyfda.local_polynomial(x, y, x_new, bandwidth, degree=1, kernel="gaussian")
```

Local polynomial regression smoother of arbitrary degree.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | `ndarray (n,)` | | Predictor values |
| `y` | `ndarray (n,)` | | Response values |
| `x_new` | `ndarray (m,)` | | Evaluation points |
| `bandwidth` | `float` | | Kernel bandwidth |
| `degree` | `int` | `1` | Polynomial degree |
| `kernel` | `str` | `"gaussian"` | `"gaussian"`, `"epanechnikov"`, or `"tricube"` |

| Returns | Type | Description |
|---------|------|-------------|
| smoothed | `ndarray (m,)` | Smoothed values at `x_new` |

```python
y_hat = pyfda.local_polynomial(x, y, x_new, bandwidth=0.1, degree=2)
```

---

### `knn_smoother`

```python
pyfda.knn_smoother(x, y, x_new, k)
```

K-nearest neighbors smoother. Averages the response of the k closest observations.

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | `ndarray (n,)` | Predictor values |
| `y` | `ndarray (n,)` | Response values |
| `x_new` | `ndarray (m,)` | Evaluation points |
| `k` | `int` | Number of nearest neighbors |

| Returns | Type | Description |
|---------|------|-------------|
| smoothed | `ndarray (m,)` | Smoothed values at `x_new` |

```python
y_hat = pyfda.knn_smoother(x, y, x_new, k=10)
```

---

### `optim_bandwidth`

```python
pyfda.optim_bandwidth(x, y, criterion="gcv", kernel="gaussian",
                      n_grid=50, h_min=None, h_max=None)
```

Select optimal bandwidth for kernel smoothing via cross-validation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | `ndarray (n,)` | | Predictor values |
| `y` | `ndarray (n,)` | | Response values |
| `criterion` | `str` | `"gcv"` | `"gcv"` or `"cv"` |
| `kernel` | `str` | `"gaussian"` | `"gaussian"`, `"epanechnikov"`, or `"tricube"` |
| `n_grid` | `int` | `50` | Number of grid points for bandwidth search |
| `h_min` | `float` or `None` | `None` | Minimum bandwidth; `None` for auto |
| `h_max` | `float` or `None` | `None` | Maximum bandwidth; `None` for auto |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `h_opt` (optimal bandwidth), `criterion`, `value` (criterion value) |

```python
result = pyfda.optim_bandwidth(x, y, criterion="gcv")
y_hat = pyfda.nadaraya_watson(x, y, x_new, bandwidth=result["h_opt"])
```
