# fdars.tolerance

Tolerance bands, confidence bands, and equivalence testing for functional data.

## Functions

| Function | Description |
|----------|-------------|
| [`fpca_tolerance_band`](#fpca_tolerance_band) | FPCA-based simultaneous tolerance band |
| [`conformal_prediction_band`](#conformal_prediction_band) | Conformal prediction band |
| [`scb_mean_degras`](#scb_mean_degras) | Simultaneous confidence band for the mean (Degras) |
| [`equivalence_test`](#equivalence_test) | Functional equivalence test (TOST) |

---

### `fpca_tolerance_band`

```python
fdars.fpca_tolerance_band(data, ncomp=3, nb=1000, coverage=0.95, seed=42)
```

FPCA-based simultaneous tolerance band via bootstrap.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `ncomp` | `int` | `3` | Number of FPC components |
| `nb` | `int` | `1000` | Number of bootstrap replicates |
| `coverage` | `float` | `0.95` | Coverage level |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `upper` (m,), `lower` (m,), `center` (m,), `half_width` (m,) |

```python
band = fdars.fpca_tolerance_band(data, ncomp=3, coverage=0.95)
```

---

### `conformal_prediction_band`

```python
fdars.conformal_prediction_band(data, coverage=0.95, cal_fraction=0.25, seed=42)
```

Distribution-free conformal prediction band.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `coverage` | `float` | `0.95` | Target coverage level |
| `cal_fraction` | `float` | `0.25` | Fraction used for calibration |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `upper` (m,), `lower` (m,), `center` (m,), `half_width` (m,) |

```python
band = fdars.conformal_prediction_band(data, coverage=0.90)
```

---

### `scb_mean_degras`

```python
fdars.scb_mean_degras(data, argvals, bandwidth=0.0, nb=1000, confidence=0.95)
```

Simultaneous confidence band for the mean function using the Degras (2011) multiplier bootstrap method.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `bandwidth` | `float` | `0.0` | Kernel smoothing bandwidth; `0.0` for auto |
| `nb` | `int` | `1000` | Number of bootstrap samples |
| `confidence` | `float` | `0.95` | Confidence level |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `upper` (m,), `lower` (m,), `center` (m,), `half_width` (m,) |

```python
t = np.linspace(0, 1, 100)
scb = fdars.scb_mean_degras(data, t, confidence=0.95)
```

---

### `equivalence_test`

```python
fdars.equivalence_test(data1, data2, delta, alpha=0.05, nb=1000, seed=42)
```

Functional equivalence test (TOST procedure). Tests whether two groups of curves are equivalent within a margin delta.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First group |
| `data2` | `ndarray (n2, m)` | | Second group |
| `delta` | `float` | | Equivalence margin |
| `alpha` | `float` | `0.05` | Significance level |
| `nb` | `int` | `1000` | Number of bootstrap replicates |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `equivalent` (bool), `p_value`, `test_statistic` |

```python
result = fdars.equivalence_test(group1, group2, delta=0.5, alpha=0.05)
if result["equivalent"]:
    print(f"Groups are equivalent (p={result['p_value']:.4f})")
```
