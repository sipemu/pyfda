# pyfda.conformal

Conformal prediction and inference methods for functional data: regression intervals, nonparametric intervals, and classification prediction sets.

## Functions

| Function | Description |
|----------|-------------|
| [`conformal_fregre_lm`](#conformal_fregre_lm) | Conformal prediction intervals for linear regression |
| [`conformal_fregre_np`](#conformal_fregre_np) | Conformal prediction intervals for nonparametric regression |
| [`conformal_classif`](#conformal_classif) | Conformal classification prediction sets |

---

### `conformal_fregre_lm`

```python
pyfda.conformal_fregre_lm(data, response, test_data, ncomp=3,
                          cal_fraction=0.25, alpha=0.1, seed=42)
```

Split conformal prediction intervals for scalar-on-function linear regression.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Training functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `test_data` | `ndarray (n_test, m)` | | Test functional predictors |
| `ncomp` | `int` | `3` | Number of FPC components |
| `cal_fraction` | `float` | `0.25` | Fraction of training data used for calibration |
| `alpha` | `float` | `0.1` | Miscoverage level (1 - confidence) |
| `seed` | `int` | `42` | Random seed for train/calibration split |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `lower` (n_test,), `upper` (n_test,), `predictions` (n_test,), `coverage` |

```python
result = pyfda.conformal_fregre_lm(X_train, y_train, X_test, ncomp=5, alpha=0.1)
for i in range(len(result["predictions"])):
    print(f"  [{result['lower'][i]:.2f}, {result['upper'][i]:.2f}]")
```

---

### `conformal_fregre_np`

```python
pyfda.conformal_fregre_np(data, response, test_data, argvals,
                          cal_fraction=0.25, alpha=0.1,
                          h_func=1.0, h_scalar=1.0, seed=42)
```

Split conformal prediction intervals for nonparametric kernel regression.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Training functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `test_data` | `ndarray (n_test, m)` | | Test functional predictors |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `cal_fraction` | `float` | `0.25` | Calibration fraction |
| `alpha` | `float` | `0.1` | Miscoverage level |
| `h_func` | `float` | `1.0` | Functional bandwidth |
| `h_scalar` | `float` | `1.0` | Scalar bandwidth |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `lower` (n_test,), `upper` (n_test,), `predictions` (n_test,), `coverage` |

```python
t = np.linspace(0, 1, 100)
result = pyfda.conformal_fregre_np(X_train, y_train, X_test, t, alpha=0.1)
```

---

### `conformal_classif`

```python
pyfda.conformal_classif(data, labels, test_data, ncomp=3,
                        classifier="lda", cal_fraction=0.25,
                        alpha=0.1, seed=42)
```

Conformal classification prediction sets. Returns a set of plausible classes for each test observation with guaranteed coverage.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Training functional data |
| `labels` | `ndarray (n,)` of `int64` | | Class labels |
| `test_data` | `ndarray (n_test, m)` | | Test functional data |
| `ncomp` | `int` | `3` | Number of FPC components |
| `classifier` | `str` | `"lda"` | `"lda"`, `"qda"`, or `"knn"` |
| `cal_fraction` | `float` | `0.25` | Calibration fraction |
| `alpha` | `float` | `0.1` | Miscoverage level |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `prediction_sets` (list of lists of int), `coverage` |

```python
result = pyfda.conformal_classif(X_train, y_train, X_test, classifier="lda")
for i, pset in enumerate(result["prediction_sets"]):
    print(f"  Obs {i}: possible classes = {pset}")
```
