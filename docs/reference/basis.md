# pyfda.basis

Basis representations for functional data: projection, reconstruction, P-spline fitting, automatic basis selection, and smoothing.

## Functions

| Function | Description |
|----------|-------------|
| [`fdata_to_basis_1d`](#fdata_to_basis_1d) | Project data onto a B-spline or Fourier basis |
| [`basis_to_fdata_1d`](#basis_to_fdata_1d) | Reconstruct data from basis coefficients |
| [`pspline_fit_1d`](#pspline_fit_1d) | P-spline fit with fixed smoothing parameter |
| [`pspline_fit_gcv`](#pspline_fit_gcv) | P-spline fit with GCV-selected smoothing |
| [`select_basis_auto_1d`](#select_basis_auto_1d) | Automatic basis type and size selection |
| [`bspline_basis`](#bspline_basis) | Evaluate a B-spline basis matrix |
| [`fourier_basis`](#fourier_basis) | Evaluate a Fourier basis matrix |
| [`smooth_basis_gcv`](#smooth_basis_gcv) | Smooth data using penalized basis with GCV |
| [`basis_nbasis_cv`](#basis_nbasis_cv) | Cross-validated selection of number of basis functions |

---

### `fdata_to_basis_1d`

```python
pyfda.fdata_to_basis_1d(data, argvals, n_basis, basis_type="bspline")
```

Project functional data onto a basis system.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_basis` | `int` | | Number of basis functions |
| `basis_type` | `str` | `"bspline"` | `"bspline"` or `"fourier"` |

| Returns | Type | Description |
|---------|------|-------------|
| `(coefficients, actual_n_basis)` | `(ndarray (n, n_basis), int)` | Basis coefficients and actual number of basis functions used |

```python
t = np.linspace(0, 1, 100)
coefs, nb = pyfda.fdata_to_basis_1d(data, t, n_basis=10, basis_type="bspline")
```

---

### `basis_to_fdata_1d`

```python
pyfda.basis_to_fdata_1d(coefficients, argvals, n_basis, basis_type="bspline")
```

Reconstruct functional data from basis coefficients.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coefficients` | `ndarray (n, n_basis)` | | Basis coefficients |
| `argvals` | `ndarray (m,)` | | Evaluation points for reconstruction |
| `n_basis` | `int` | | Number of basis functions |
| `basis_type` | `str` | `"bspline"` | `"bspline"` or `"fourier"` |

| Returns | Type | Description |
|---------|------|-------------|
| reconstructed | `ndarray (n, m)` | Reconstructed functional data |

```python
reconstructed = pyfda.basis_to_fdata_1d(coefs, t, n_basis=10)
```

---

### `pspline_fit_1d`

```python
pyfda.pspline_fit_1d(data, argvals, n_basis, lambda_, order=2)
```

Fit P-splines to 1D functional data with a fixed smoothing parameter.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_basis` | `int` | | Number of B-spline basis functions |
| `lambda_` | `float` | | Smoothing penalty parameter |
| `order` | `int` | `2` | Penalty difference order |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted` (n, m), `coefficients` (n, n_basis), `edf`, `rss`, `gcv`, `aic`, `bic` |

```python
result = pyfda.pspline_fit_1d(data, t, n_basis=20, lambda_=1.0, order=2)
smoothed = result["fitted"]
```

---

### `pspline_fit_gcv`

```python
pyfda.pspline_fit_gcv(data, argvals, n_basis, order=2)
```

P-spline fit with GCV-selected smoothing parameter.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_basis` | `int` | | Number of B-spline basis functions |
| `order` | `int` | `2` | Penalty difference order |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted` (n, m), `coefficients` (n, n_basis), `edf`, `rss`, `gcv`, `aic`, `bic` |

```python
result = pyfda.pspline_fit_gcv(data, t, n_basis=20)
```

---

### `select_basis_auto_1d`

```python
pyfda.select_basis_auto_1d(data, argvals, criterion="gcv", nbasis_min=0,
                           nbasis_max=0, lambda_pspline=-1.0,
                           use_seasonal_hint=True)
```

Automatic basis selection using GCV, AIC, or BIC. Optionally detects seasonality via FFT to choose between B-spline and Fourier bases.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `criterion` | `str` | `"gcv"` | `"gcv"`, `"aic"`, or `"bic"` |
| `nbasis_min` | `int` | `0` | Minimum nbasis to try; `0` for auto |
| `nbasis_max` | `int` | `0` | Maximum nbasis to try; `0` for auto |
| `lambda_pspline` | `float` | `-1.0` | Smoothing param; negative for auto-select |
| `use_seasonal_hint` | `bool` | `True` | Use FFT to detect seasonality |

| Returns | Type | Description |
|---------|------|-------------|
| selections | `list[dict]` | Per-curve results with keys: `basis_type`, `nbasis`, `score`, `coefficients`, `fitted`, `edf`, `seasonal_detected`, `lambda_val` |

```python
results = pyfda.select_basis_auto_1d(data, t, criterion="bic")
print(results[0]["basis_type"], results[0]["nbasis"])
```

---

### `bspline_basis`

```python
pyfda.bspline_basis(argvals, nknots, order=4)
```

Evaluate a B-spline basis at given points.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `nknots` | `int` | | Number of interior knots |
| `order` | `int` | `4` | Spline order (4 = cubic) |

| Returns | Type | Description |
|---------|------|-------------|
| basis | `ndarray (m, nbasis)` | Basis matrix; `nbasis = nknots + order` |

```python
t = np.linspace(0, 1, 100)
B = pyfda.bspline_basis(t, nknots=10, order=4)  # shape (100, 14)
```

---

### `fourier_basis`

```python
pyfda.fourier_basis(argvals, n_basis)
```

Evaluate a Fourier basis at given points.

| Parameter | Type | Description |
|-----------|------|-------------|
| `argvals` | `ndarray (m,)` | Evaluation points |
| `n_basis` | `int` | Number of basis functions (should be odd) |

| Returns | Type | Description |
|---------|------|-------------|
| basis | `ndarray (m, n_basis)` | Fourier basis matrix |

```python
F = pyfda.fourier_basis(t, n_basis=7)  # shape (100, 7)
```

---

### `smooth_basis_gcv`

```python
pyfda.smooth_basis_gcv(data, argvals, n_basis, basis_type="bspline",
                       lfd_order=2, log_lambda_min=-8.0,
                       log_lambda_max=4.0, n_grid=25)
```

Smooth functional data using a penalized basis expansion with GCV-selected smoothing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_basis` | `int` | | Number of basis functions |
| `basis_type` | `str` | `"bspline"` | `"bspline"` or `"fourier"` |
| `lfd_order` | `int` | `2` | Derivative order for the penalty |
| `log_lambda_min` | `float` | `-8.0` | Minimum log10(lambda) for search |
| `log_lambda_max` | `float` | `4.0` | Maximum log10(lambda) for search |
| `n_grid` | `int` | `25` | Number of grid points for lambda search |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted` (n, m), `coefficients` (n, nbasis), `edf`, `gcv`, `aic`, `bic`, `nbasis` |

```python
result = pyfda.smooth_basis_gcv(data, t, n_basis=20, basis_type="bspline")
```

---

### `basis_nbasis_cv`

```python
pyfda.basis_nbasis_cv(data, argvals, nbasis_min=4, nbasis_max=20,
                      basis_type="bspline", criterion="gcv",
                      n_folds=5, lambda_=1.0)
```

Cross-validated selection of the number of basis functions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `nbasis_min` | `int` | `4` | Minimum nbasis to test |
| `nbasis_max` | `int` | `20` | Maximum nbasis to test |
| `basis_type` | `str` | `"bspline"` | `"bspline"` or `"fourier"` |
| `criterion` | `str` | `"gcv"` | `"gcv"`, `"cv"`, `"aic"`, or `"bic"` |
| `n_folds` | `int` | `5` | Number of folds for CV criterion |
| `lambda_` | `float` | `1.0` | Smoothing parameter |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `optimal_nbasis`, `scores` (array), `nbasis_range` (array), `criterion` |

```python
result = pyfda.basis_nbasis_cv(data, t, nbasis_min=5, nbasis_max=30)
print(f"Best: {result['optimal_nbasis']} basis functions")
```
