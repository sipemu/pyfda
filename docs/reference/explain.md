# fdars.explain

Explainability and interpretability methods for functional regression models. All functions internally fit a `fregre_lm` model and then compute explanations.

## Functions

| Function | Description |
|----------|-------------|
| [`fpc_permutation_importance`](#fpc_permutation_importance) | Permutation importance of FPC scores |
| [`functional_pdp`](#functional_pdp) | Partial dependence plot for an FPC |
| [`fpc_shap_values`](#fpc_shap_values) | SHAP values for FPC scores |
| [`significant_regions`](#significant_regions) | Identify significant regions of beta(t) |
| [`beta_decomposition`](#beta_decomposition) | Decompose beta(t) into FPC contributions |

---

### `fpc_permutation_importance`

```python
fdars.fpc_permutation_importance(data, response, ncomp=3, n_perm=10, seed=42)
```

Compute permutation importance of each FPC score. Measures the increase in prediction error when each FPC score column is randomly shuffled.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `ncomp` | `int` | `3` | Number of FPC components |
| `n_perm` | `int` | `10` | Number of permutation repeats |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `importance` (ncomp,), `baseline_metric`, `permuted_metric` (ncomp,) |

```python
result = fdars.fpc_permutation_importance(data, y, ncomp=5, n_perm=20)
for i, imp in enumerate(result["importance"]):
    print(f"FPC {i+1}: importance = {imp:.4f}")
```

---

### `functional_pdp`

```python
fdars.functional_pdp(data, response, ncomp=3, component=0, n_grid=50)
```

Partial dependence plot for a single FPC component. Shows the marginal effect of one FPC score on the predicted response.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `ncomp` | `int` | `3` | Number of FPC components |
| `component` | `int` | `0` | Which FPC to compute PDP for (0-indexed) |
| `n_grid` | `int` | `50` | Number of grid points for the PDP |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `grid_values` (n_grid,), `pdp_curve` (n_grid,), `component` |

```python
pdp = fdars.functional_pdp(data, y, ncomp=5, component=0)
# Plot: plt.plot(pdp["grid_values"], pdp["pdp_curve"])
```

---

### `fpc_shap_values`

```python
fdars.fpc_shap_values(data, response, ncomp=3)
```

Compute SHAP values for FPC scores in a linear regression model. For linear models, SHAP values have a closed-form solution.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `ncomp` | `int` | `3` | Number of FPC components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `values` (n, ncomp), `base_value` |

```python
shap = fdars.fpc_shap_values(data, y, ncomp=5)
# shap["values"][i, j] = contribution of FPC j for observation i
```

---

### `significant_regions`

```python
fdars.significant_regions(lower, upper)
```

Identify regions of the domain where the coefficient function beta(t) is significantly different from zero, based on confidence interval bounds.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lower` | `ndarray (m,)` | Lower confidence interval bounds |
| `upper` | `ndarray (m,)` | Upper confidence interval bounds |

| Returns | Type | Description |
|---------|------|-------------|
| regions | `list` | List of `(start_idx, end_idx, direction)` tuples where `direction` is `"positive"` or `"negative"` |

```python
regions = fdars.significant_regions(ci_lower, ci_upper)
for start, end, direction in regions:
    print(f"  [{start}:{end}] -> {direction}")
```

---

### `beta_decomposition`

```python
fdars.beta_decomposition(data, response, ncomp=3)
```

Decompose the estimated beta(t) function into contributions from each FPC.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `response` | `ndarray (n,)` | | Scalar response |
| `ncomp` | `int` | `3` | Number of FPC components |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `components` (list of ncomp arrays, each (m,)), `coefficients` (ncomp,), `variance_proportion` (ncomp,) |

```python
decomp = fdars.beta_decomposition(data, y, ncomp=5)
for i, comp in enumerate(decomp["components"]):
    print(f"FPC {i+1}: coeff={decomp['coefficients'][i]:.3f}, "
          f"var_prop={decomp['variance_proportion'][i]:.3f}")
```
