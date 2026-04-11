# pyfda.outliers

Outlier detection methods for functional data.

## Functions

| Function | Description |
|----------|-------------|
| [`detect_outliers_lrt`](#detect_outliers_lrt) | LRT-based outlier detection with bootstrap |
| [`outliergram`](#outliergram) | Outliergram (MEI vs MBD) |
| [`magnitude_shape`](#magnitude_shape) | Magnitude-shape outlyingness |

---

### `detect_outliers_lrt`

```python
pyfda.detect_outliers_lrt(data, alpha=0.05, n_bootstrap=200, trim=0.1, smo=0.02)
```

Likelihood ratio test for outlier detection with bootstrap calibration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `alpha` | `float` | `0.05` | Significance level |
| `n_bootstrap` | `int` | `200` | Number of bootstrap samples |
| `trim` | `float` | `0.1` | Trimming proportion |
| `smo` | `float` | `0.02` | Smoothing parameter |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `outliers` (bool array of length n), `threshold` |

```python
result = pyfda.detect_outliers_lrt(data, alpha=0.05)
outlier_idx = np.where(result["outliers"])[0]
```

---

### `outliergram`

```python
pyfda.outliergram(data, factor=1.5)
```

Outliergram method. Computes Modified Epigraph Index (MEI) and Modified Band Depth (MBD), then flags outliers based on a parabolic rule.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `factor` | `float` | `1.5` | Outlier detection factor |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `mei` (n,), `mbd` (n,), `outliers` (bool array of length n) |

```python
result = pyfda.outliergram(data, factor=1.5)
```

---

### `magnitude_shape`

```python
pyfda.magnitude_shape(data)
```

Compute magnitude and shape outlyingness measures. Magnitude captures vertical outliers; shape captures curves with unusual patterns.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional data |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `magnitude` (n,), `shape` (n,) |

```python
result = pyfda.magnitude_shape(data)
# Flag observations with extreme magnitude or shape
outliers = (result["magnitude"] > 3) | (result["shape"] > 3)
```
