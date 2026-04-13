# fdars.clustering

Clustering methods for functional data with cluster quality metrics.

## Functions

| Function | Description |
|----------|-------------|
| [`kmeans_fd`](#kmeans_fd) | K-means clustering |
| [`fuzzy_cmeans_fd`](#fuzzy_cmeans_fd) | Fuzzy C-means clustering |
| [`gmm_cluster`](#gmm_cluster) | Gaussian mixture model clustering |
| [`silhouette_score`](#silhouette_score) | Silhouette score from distance matrix |
| [`calinski_harabasz`](#calinski_harabasz) | Calinski-Harabasz index from distance matrix |

---

### `kmeans_fd`

```python
fdars.kmeans_fd(data, argvals, k, max_iter=100, tol=1e-6, seed=42)
```

K-means clustering for functional data using L2 distance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `k` | `int` | | Number of clusters |
| `max_iter` | `int` | `100` | Maximum iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `cluster` (n,), `centers` (k, m), `tot_withinss`, `iter`, `converged` |

```python
t = np.linspace(0, 1, 100)
result = fdars.kmeans_fd(data, t, k=3)
labels = result["cluster"]
```

---

### `fuzzy_cmeans_fd`

```python
fdars.fuzzy_cmeans_fd(data, argvals, k, fuzziness=2.0, max_iter=100,
                      tol=1e-6, seed=42)
```

Fuzzy C-means clustering for functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `k` | `int` | | Number of clusters |
| `fuzziness` | `float` | `2.0` | Fuzziness parameter (m > 1) |
| `max_iter` | `int` | `100` | Maximum iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `cluster` (n,), `membership` (n, k), `centers` (k, m) |

```python
result = fdars.fuzzy_cmeans_fd(data, t, k=3, fuzziness=2.0)
soft_labels = result["membership"]  # shape (n, 3)
```

---

### `gmm_cluster`

```python
fdars.gmm_cluster(data, argvals, k_range, nbasis=5, max_iter=200,
                  tol=1e-6, seed=42)
```

Gaussian mixture model clustering via basis projection. Tries multiple values of k and selects the best by BIC.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `k_range` | `list[int]` | | List of cluster counts to try |
| `nbasis` | `int` | `5` | Number of basis functions for projection |
| `max_iter` | `int` | `200` | Maximum EM iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |
| `seed` | `int` | `42` | Random seed |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `cluster` (n,), `membership` (n, k), `bic_values` (list of (k, bic)), `icl_values` (list of (k, icl)) |

```python
result = fdars.gmm_cluster(data, t, k_range=[2, 3, 4, 5])
best_labels = result["cluster"]
```

---

### `silhouette_score`

```python
fdars.silhouette_score(dist_matrix, labels)
```

Compute per-observation silhouette scores from a precomputed distance matrix.

| Parameter | Type | Description |
|-----------|------|-------------|
| `dist_matrix` | `ndarray (n, n)` | Pairwise distance matrix |
| `labels` | `ndarray (n,)` of `int64` | Cluster assignments |

| Returns | Type | Description |
|---------|------|-------------|
| scores | `ndarray (n,)` | Per-observation silhouette scores in [-1, 1] |

```python
D = fdars.lp_self_1d(data, t)
scores = fdars.silhouette_score(D, result["cluster"].astype(np.int64))
print(f"Mean silhouette: {scores.mean():.3f}")
```

---

### `calinski_harabasz`

```python
fdars.calinski_harabasz(dist_matrix, labels)
```

Calinski-Harabasz index (variance ratio criterion) from a precomputed distance matrix. Higher values indicate better-defined clusters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `dist_matrix` | `ndarray (n, n)` | Pairwise distance matrix |
| `labels` | `ndarray (n,)` of `int64` | Cluster assignments |

| Returns | Type | Description |
|---------|------|-------------|
| score | `float` | Calinski-Harabasz score |

```python
ch = fdars.calinski_harabasz(D, result["cluster"].astype(np.int64))
```
