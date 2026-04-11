# pyfda.regression

Regression and dimensionality reduction for functional data: FPCA, FPLS, scalar-on-function, function-on-scalar, ANOVA, and logistic regression.

## Functions

| Function | Description |
|----------|-------------|
| [`fpca`](#fpca) | Functional principal component analysis |
| [`fpls`](#fpls) | Functional partial least squares |
| [`fregre_lm`](#fregre_lm) | Scalar-on-function linear regression |
| [`fregre_pls`](#fregre_pls) | Scalar-on-function PLS regression |
| [`fregre_np`](#fregre_np) | Nonparametric kernel regression |
| [`fregre_l1`](#fregre_l1) | L1 (robust) regression |
| [`fregre_huber`](#fregre_huber) | Huber M-estimation regression |
| [`functional_logistic`](#functional_logistic) | Functional logistic regression |
| [`fosr`](#fosr) | Function-on-scalar regression |
| [`fanova`](#fanova) | Functional ANOVA |
| [`model_selection_ncomp`](#model_selection_ncomp) | Cross-validated component selection |

---

### `fpca`

```python
pyfda.fpca(data, argvals, n_comp=3)
```

Functional principal component analysis with integration-weighted covariance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_comp` | `int` | `3` | Number of principal components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `scores` (n, n_comp), `rotation` (m, n_comp), `singular_values` (n_comp,), `mean` (m,), `centered` (n, m), `weights` (m,) |

```python
t = np.linspace(0, 1, 100)
pca = pyfda.fpca(data, t, n_comp=5)
scores = pca["scores"]  # project new data via these loadings
```

---

### `fpls`

```python
pyfda.fpls(data, argvals, response, n_comp=3)
```

Functional partial least squares. Finds directions that maximize covariance between functional predictors and scalar response.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `response` | `ndarray (n,)` | | Scalar response |
| `n_comp` | `int` | `3` | Number of PLS components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `scores` (n, n_comp), `loadings` (m, n_comp), `weights` (m, n_comp), `x_means` (m,), `integration_weights` (m,) |

```python
pls = pyfda.fpls(data, t, y, n_comp=3)
```

---

### `fregre_lm`

```python
pyfda.fregre_lm(data, response, n_comp=3)
```

Scalar-on-function linear regression via FPC scores. Projects data onto FPCs, then fits OLS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `n_comp` | `int` | `3` | Number of FPC components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted_values` (n,), `residuals` (n,), `beta_t` (m,), `r_squared`, `coefficients` (n_comp,), `intercept` |

```python
fit = pyfda.fregre_lm(data, y, n_comp=5)
print(f"R-squared: {fit['r_squared']:.3f}")
```

---

### `fregre_pls`

```python
pyfda.fregre_pls(data, argvals, response, n_comp=3)
```

Scalar-on-function regression via PLS components.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `response` | `ndarray (n,)` | | Scalar response |
| `n_comp` | `int` | `3` | Number of PLS components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted_values` (n,), `residuals` (n,), `beta_t` (m,), `r_squared` |

```python
fit = pyfda.fregre_pls(data, t, y, n_comp=3)
```

---

### `fregre_np`

```python
pyfda.fregre_np(dist_matrix, response, h=0.0)
```

Nonparametric kernel regression from a precomputed distance matrix.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dist_matrix` | `ndarray (n, n)` | | Pairwise distance matrix |
| `response` | `ndarray (n,)` | | Scalar response |
| `h` | `float` | `0.0` | Bandwidth; `0.0` for automatic selection |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted_values` (n,), `residuals` (n,), `h_func`, `r_squared` |

```python
D = pyfda.lp_self_1d(data, t)
fit = pyfda.fregre_np(D, y)
print(f"Selected bandwidth: {fit['h_func']:.3f}")
```

---

### `fregre_l1`

```python
pyfda.fregre_l1(data, response, n_comp=3)
```

L1 (least absolute deviations) robust regression for functional data via FPCs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `n_comp` | `int` | `3` | Number of FPC components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted_values` (n,), `residuals` (n,), `beta_t` (m,) |

```python
fit = pyfda.fregre_l1(data, y, n_comp=3)
```

---

### `fregre_huber`

```python
pyfda.fregre_huber(data, response, n_comp=3, huber_k=1.345)
```

Huber M-estimation robust regression for functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `n_comp` | `int` | `3` | Number of FPC components |
| `huber_k` | `float` | `1.345` | Huber tuning constant |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted_values` (n,), `residuals` (n,), `beta_t` (m,) |

```python
fit = pyfda.fregre_huber(data, y, n_comp=3, huber_k=1.345)
```

---

### `functional_logistic`

```python
pyfda.functional_logistic(data, labels, n_comp=3, max_iter=25, tol=1e-6)
```

Functional logistic regression for binary classification via IRLS.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `labels` | `ndarray (n,)` of `float64` | | Binary labels (0.0/1.0) |
| `n_comp` | `int` | `3` | Number of FPC components |
| `max_iter` | `int` | `25` | Maximum IRLS iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `probabilities` (n,), `predicted_classes` (n,), `beta_t` (m,), `intercept`, `coefficients` (n_comp,) |

```python
fit = pyfda.functional_logistic(data, labels.astype(float), n_comp=3)
pred = fit["predicted_classes"]
```

---

### `fosr`

```python
pyfda.fosr(response, predictors, lambda_=0.0)
```

Function-on-scalar regression. Models a functional response as a linear combination of scalar predictors.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `response` | `ndarray (n, m)` | | Functional response |
| `predictors` | `ndarray (n, p)` | | Scalar predictors |
| `lambda_` | `float` | `0.0` | Roughness penalty; negative for GCV selection |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `fitted` (n, m), `beta` (p, m), `residuals` (n, m), `r_squared` |

```python
fit = pyfda.fosr(Y_func, X_scalar, lambda_=-1.0)  # GCV selection
beta = fit["beta"]  # coefficient functions
```

---

### `fanova`

```python
pyfda.fanova(data, groups, n_perm=999)
```

Functional ANOVA with permutation-based p-values.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `groups` | `ndarray (n,)` of `int64` | | Group labels |
| `n_perm` | `int` | `999` | Number of permutations |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `f_statistic_t` (m,), `p_value`, `group_means` (k, m), `global_statistic` |

```python
result = pyfda.fanova(data, groups.astype(np.int64), n_perm=999)
print(f"p-value: {result['p_value']:.4f}")
```

---

### `model_selection_ncomp`

```python
pyfda.model_selection_ncomp(data, response, max_comp=10, criterion="gcv")
```

Cross-validated selection of the number of FPC components for scalar-on-function regression.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `max_comp` | `int` | `10` | Maximum number of components to test |
| `criterion` | `str` | `"gcv"` | `"gcv"`, `"aic"`, or `"bic"` |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `best_ncomp`, `criteria` (list of (ncomp, aic, bic, gcv) tuples) |

```python
result = pyfda.model_selection_ncomp(data, y, max_comp=10, criterion="bic")
print(f"Best n_comp: {result['best_ncomp']}")
```
