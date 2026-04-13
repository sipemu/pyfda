# fdars.alignment

Elastic alignment, shape analysis, and warping operations for functional data using the Fisher-Rao metric and SRSF representation.

## Functions

| Function | Description |
|----------|-------------|
| [`elastic_align_pair`](#elastic_align_pair) | Pairwise elastic alignment of two curves |
| [`karcher_mean`](#karcher_mean) | Karcher (Frechet) mean under elastic metric |
| [`karcher_median`](#karcher_median) | Karcher median under elastic metric |
| [`robust_karcher_mean`](#robust_karcher_mean) | Trimmed robust Karcher mean |
| [`elastic_distance`](#elastic_distance) | Elastic (Fisher-Rao) distance between two curves |
| [`elastic_self_distance_matrix`](#elastic_self_distance_matrix) | Elastic self-distance matrix |
| [`elastic_cross_distance_matrix`](#elastic_cross_distance_matrix) | Elastic cross-distance matrix |
| [`srsf_transform`](#srsf_transform) | Square Root Slope Function transform |
| [`srsf_inverse`](#srsf_inverse) | Inverse SRSF transform |
| [`compose_warps`](#compose_warps) | Compose two warping functions |
| [`invert_warp`](#invert_warp) | Invert a warping function |
| [`warp_smoothness`](#warp_smoothness) | Warp smoothness (bending energy) |
| [`warp_complexity`](#warp_complexity) | Warp complexity (geodesic distance from identity) |
| [`amplitude_distance`](#amplitude_distance) | Amplitude distance between two curves |
| [`phase_distance`](#phase_distance) | Phase distance between two curves |
| [`elastic_depth`](#elastic_depth) | Depth under the elastic metric |
| [`shape_distance`](#shape_distance) | Shape (quotient space) distance |
| [`vert_fpca`](#vert_fpca) | Vertical (amplitude) FPCA on aligned data |
| [`horiz_fpca`](#horiz_fpca) | Horizontal (phase) FPCA |
| [`joint_fpca`](#joint_fpca) | Joint amplitude + phase FPCA |
| [`elastic_regression`](#elastic_regression) | Elastic scalar-on-function regression |
| [`elastic_logistic`](#elastic_logistic) | Elastic logistic regression |

---

### `elastic_align_pair`

```python
fdars.elastic_align_pair(curve1, curve2, argvals, lambda_=0.0)
```

Align `curve2` to `curve1` using elastic (Fisher-Rao) alignment.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `curve1` | `ndarray (m,)` | | Target curve |
| `curve2` | `ndarray (m,)` | | Curve to be aligned |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization parameter |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `f_aligned` (m,), `gamma` (m,), `distance` |

```python
t = np.linspace(0, 1, 100)
result = fdars.elastic_align_pair(f1, f2, t, lambda_=0.0)
aligned = result["f_aligned"]
```

---

### `karcher_mean`

```python
fdars.karcher_mean(data, argvals, lambda_=0.0, max_iter=20, tol=1e-4)
```

Compute the Karcher (Frechet) mean under the elastic metric. Iteratively aligns all curves and updates the mean.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Maximum iterations |
| `tol` | `float` | `1e-4` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `mean` (m,), `mean_srsf` (m,), `aligned_data` (n, m), `gammas` (n, m), `n_iter`, `converged` |

```python
km = fdars.karcher_mean(data, t, lambda_=0.0)
mean_curve = km["mean"]
```

---

### `karcher_median`

```python
fdars.karcher_median(data, argvals, lambda_=0.0, max_iter=20, tol=1e-3)
```

Karcher median under the elastic metric.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Maximum iterations |
| `tol` | `float` | `1e-3` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `mean` (m,), `mean_srsf` (m,), `aligned_data` (n, m), `gammas` (n, m), `weights` (n,), `n_iter`, `converged` |

```python
result = fdars.karcher_median(data, t)
```

---

### `robust_karcher_mean`

```python
fdars.robust_karcher_mean(data, argvals, lambda_=0.0, max_iter=20,
                          tol=1e-3, trim_fraction=0.1)
```

Trimmed robust Karcher mean. Down-weights outlying curves.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Maximum iterations |
| `tol` | `float` | `1e-3` | Convergence tolerance |
| `trim_fraction` | `float` | `0.1` | Fraction of curves to trim |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `mean` (m,), `mean_srsf` (m,), `aligned_data` (n, m), `gammas` (n, m), `weights` (n,), `n_iter`, `converged` |

```python
result = fdars.robust_karcher_mean(data, t, trim_fraction=0.15)
```

---

### `elastic_distance`

```python
fdars.elastic_distance(curve1, curve2, argvals, lambda_=0.0)
```

Compute the elastic (Fisher-Rao) distance between two curves.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `curve1` | `ndarray (m,)` | | First curve |
| `curve2` | `ndarray (m,)` | | Second curve |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| distance | `float` | Elastic distance |

```python
d = fdars.elastic_distance(f1, f2, t)
```

---

### `elastic_self_distance_matrix`

```python
fdars.elastic_self_distance_matrix(data, argvals, lambda_=0.0)
```

Pairwise elastic distance matrix for a single dataset.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n, n)` | Symmetric distance matrix |

```python
D = fdars.elastic_self_distance_matrix(data, t)
```

---

### `elastic_cross_distance_matrix`

```python
fdars.elastic_cross_distance_matrix(data1, data2, argvals, lambda_=0.0)
```

Elastic cross-distance matrix between two datasets.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data1` | `ndarray (n1, m)` | | First dataset |
| `data2` | `ndarray (n2, m)` | | Second dataset |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| dist | `ndarray (n1, n2)` | Distance matrix |

---

### `srsf_transform`

```python
fdars.srsf_transform(curve, argvals)
```

Compute the Square Root Slope Function (SRSF) of a curve.

| Parameter | Type | Description |
|-----------|------|-------------|
| `curve` | `ndarray (m,)` | Input curve |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| srsf | `ndarray (m,)` | SRSF representation |

```python
q = fdars.srsf_transform(f, t)
```

---

### `srsf_inverse`

```python
fdars.srsf_inverse(srsf, argvals, initial_value=0.0)
```

Reconstruct a curve from its SRSF representation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `srsf` | `ndarray (m,)` | | SRSF values |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `initial_value` | `float` | `0.0` | Starting value f(t_0) |

| Returns | Type | Description |
|---------|------|-------------|
| curve | `ndarray (m,)` | Reconstructed curve |

```python
f_rec = fdars.srsf_inverse(q, t, initial_value=f[0])
```

---

### `compose_warps`

```python
fdars.compose_warps(warp1, warp2, argvals)
```

Compose two warping functions: result = warp1(warp2(t)).

| Parameter | Type | Description |
|-----------|------|-------------|
| `warp1` | `ndarray (m,)` | Outer warping function |
| `warp2` | `ndarray (m,)` | Inner warping function |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| composed | `ndarray (m,)` | Composed warping function |

```python
gamma_composed = fdars.compose_warps(gamma1, gamma2, t)
```

---

### `invert_warp`

```python
fdars.invert_warp(warp, argvals)
```

Compute the inverse of a warping function.

| Parameter | Type | Description |
|-----------|------|-------------|
| `warp` | `ndarray (m,)` | Warping function |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| inverse | `ndarray (m,)` | Inverse warp |

```python
gamma_inv = fdars.invert_warp(gamma, t)
```

---

### `warp_smoothness`

```python
fdars.warp_smoothness(warp, argvals)
```

Compute the smoothness (bending energy) of a warping function.

| Parameter | Type | Description |
|-----------|------|-------------|
| `warp` | `ndarray (m,)` | Warping function |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| smoothness | `float` | Bending energy |

```python
s = fdars.warp_smoothness(gamma, t)
```

---

### `warp_complexity`

```python
fdars.warp_complexity(warp, argvals)
```

Geodesic distance of a warping function from the identity.

| Parameter | Type | Description |
|-----------|------|-------------|
| `warp` | `ndarray (m,)` | Warping function |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| complexity | `float` | Geodesic distance from identity |

```python
c = fdars.warp_complexity(gamma, t)
```

---

### `amplitude_distance`

```python
fdars.amplitude_distance(curve1, curve2, argvals, lambda_=0.0)
```

Amplitude (vertical) component of the elastic distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `curve1` | `ndarray (m,)` | | First curve |
| `curve2` | `ndarray (m,)` | | Second curve |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| distance | `float` | Amplitude distance |

```python
da = fdars.amplitude_distance(f1, f2, t)
```

---

### `phase_distance`

```python
fdars.phase_distance(curve1, curve2, argvals, lambda_=0.0)
```

Phase (horizontal) component of the elastic distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `curve1` | `ndarray (m,)` | | First curve |
| `curve2` | `ndarray (m,)` | | Second curve |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| distance | `float` | Phase distance |

```python
dp = fdars.phase_distance(f1, f2, t)
```

---

### `elastic_depth`

```python
fdars.elastic_depth(data, argvals, lambda_=0.0)
```

Depth under the elastic metric, decomposed into amplitude and phase components.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `amplitude_depth` (n,), `phase_depth` (n,), `combined_depth` (n,), `amplitude_distances` (n, n), `phase_distances` (n, n) |

```python
ed = fdars.elastic_depth(data, t)
deepest = np.argmax(ed["combined_depth"])
```

---

### `shape_distance`

```python
fdars.shape_distance(curve1, curve2, argvals, lambda_=0.0)
```

Shape distance in the quotient space (invariant to translation, scaling, and reparameterization).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `curve1` | `ndarray (m,)` | | First curve |
| `curve2` | `ndarray (m,)` | | Second curve |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `lambda_` | `float` | `0.0` | Regularization |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `distance`, `gamma` (m,), `f2_aligned` (m,) |

```python
sd = fdars.shape_distance(f1, f2, t)
print(f"Shape distance: {sd['distance']:.4f}")
```

---

### `vert_fpca`

```python
fdars.vert_fpca(data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4)
```

Vertical (amplitude) FPCA. Aligns data via Karcher mean, then performs PCA on the aligned SRSFs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_comp` | `int` | `3` | Number of components |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Karcher mean iterations |
| `tol` | `float` | `1e-4` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `scores` (n, n_comp), `eigenfunctions_q` (n_comp, m+1), `eigenfunctions_f` (n_comp, m), `eigenvalues` (n_comp,), `cumulative_variance` (n_comp,), `mean_q` (m+1,) |

```python
vfpca = fdars.vert_fpca(data, t, n_comp=3)
```

---

### `horiz_fpca`

```python
fdars.horiz_fpca(data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4)
```

Horizontal (phase) FPCA. Analyzes the warping functions from elastic alignment.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_comp` | `int` | `3` | Number of components |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Karcher mean iterations |
| `tol` | `float` | `1e-4` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `scores` (n, n_comp), `eigenfunctions_psi` (n_comp, m), `eigenfunctions_gam` (n_comp, m), `eigenvalues` (n_comp,), `cumulative_variance` (n_comp,), `mean_psi` (m,), `shooting_vectors` (n, m) |

```python
hfpca = fdars.horiz_fpca(data, t, n_comp=3)
```

---

### `joint_fpca`

```python
fdars.joint_fpca(data, argvals, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4)
```

Joint amplitude + phase FPCA. Combines vertical and horizontal variability into a single decomposition.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `n_comp` | `int` | `3` | Number of components |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Karcher mean iterations |
| `tol` | `float` | `1e-4` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `scores` (n, n_comp), `eigenvalues` (n_comp,), `cumulative_variance` (n_comp,), `balance_c`, `vert_component` (n_comp, ...), `horiz_component` (n_comp, ...) |

```python
jfpca = fdars.joint_fpca(data, t, n_comp=3)
```

---

### `elastic_regression`

```python
fdars.elastic_regression(data, argvals, response, ncomp_beta=10,
                         lambda_=0.0, max_iter=20, tol=1e-4)
```

Elastic scalar-on-function regression. Simultaneously aligns and regresses.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `response` | `ndarray (n,)` | | Scalar response |
| `ncomp_beta` | `int` | `10` | Number of basis functions for beta |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Maximum iterations |
| `tol` | `float` | `1e-4` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `alpha`, `beta` (m,), `fitted_values` (n,), `residuals` (n,), `sse`, `r_squared`, `gammas` (n, m), `n_iter` |

```python
fit = fdars.elastic_regression(data, t, y, ncomp_beta=10)
print(f"R-squared: {fit['r_squared']:.3f}")
```

---

### `elastic_logistic`

```python
fdars.elastic_logistic(data, argvals, labels, ncomp_beta=10,
                       lambda_=0.0, max_iter=20, tol=1e-4)
```

Elastic logistic regression for binary classification.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional predictors |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `labels` | `ndarray (n,)` of `int64` | | Binary labels (0/1) |
| `ncomp_beta` | `int` | `10` | Number of basis functions for beta |
| `lambda_` | `float` | `0.0` | Regularization |
| `max_iter` | `int` | `20` | Maximum iterations |
| `tol` | `float` | `1e-4` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `alpha`, `beta` (m,), `probabilities` (n,), `predicted_classes` (n,), `accuracy`, `loss`, `gammas` (n, m), `n_iter` |

```python
fit = fdars.elastic_logistic(data, t, labels, ncomp_beta=10)
print(f"Accuracy: {fit['accuracy']:.3f}")
```
