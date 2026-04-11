# Clustering

Partition a set of functional observations into homogeneous groups. `pyfda` provides three clustering algorithms -- hard (k-means), soft (fuzzy c-means), and model-based (GMM) -- together with two cluster-quality indices for selecting the number of clusters.

---

## K-means for functional data

The functional k-means algorithm minimises the total within-cluster $L^2$ distance, iterating between assignment and centroid update until convergence.

```python
import numpy as np
from pyfda.simulation import simulate
from pyfda.clustering import kmeans_fd

# Two well-separated groups
argvals = np.linspace(0, 1, 100)
group_a = simulate(30, argvals, n_basis=5, seed=1)
group_b = simulate(30, argvals, n_basis=5, seed=2) + 3.0
data = np.vstack([group_a, group_b])

result = kmeans_fd(data, argvals, k=2, max_iter=100, tol=1e-6, seed=42)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `k` | `int` | -- | Number of clusters |
| `max_iter` | `int` | `100` | Maximum iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |
| `seed` | `int` | `42` | Random seed for initialisation |

**Returns** a dictionary:

| Key | Shape / Type | Description |
|---|---|---|
| `cluster` | `(n,)` int | Cluster label for each observation |
| `centers` | `(k, m)` | Cluster centroid curves |
| `tot_withinss` | `float` | Total within-cluster sum of squares |
| `iter` | `int` | Number of iterations performed |
| `converged` | `bool` | Whether the algorithm converged |

---

## Fuzzy C-means

Fuzzy c-means assigns each observation a *membership degree* for every cluster rather than a hard label, controlled by the fuzziness parameter $m$ (default 2).

```python
from pyfda.clustering import fuzzy_cmeans_fd

result_fcm = fuzzy_cmeans_fd(
    data, argvals, k=2, fuzziness=2.0, max_iter=100, tol=1e-6, seed=42
)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `k` | `int` | -- | Number of clusters |
| `fuzziness` | `float` | `2.0` | Fuzziness exponent ($> 1$) |
| `max_iter` | `int` | `100` | Maximum iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |
| `seed` | `int` | `42` | Random seed |

**Returns** a dictionary:

| Key | Shape / Type | Description |
|---|---|---|
| `cluster` | `(n,)` int | Hard assignment (argmax of membership) |
| `membership` | `(n, k)` | Membership degree matrix |
| `centers` | `(k, m)` | Cluster centroid curves |

!!! tip "Interpreting membership"
    A membership value of 0.95 for cluster 1 and 0.05 for cluster 2 indicates a clearly assigned point. Values near 0.50/0.50 indicate boundary observations that sit between clusters.

---

## Gaussian Mixture Model (GMM)

The GMM approach projects the functional data onto a B-spline basis, fits a multivariate Gaussian mixture in the coefficient space, and selects the best number of components via BIC.

```python
from pyfda.clustering import gmm_cluster

result_gmm = gmm_cluster(
    data, argvals,
    k_range=[2, 3, 4],
    nbasis=5,
    max_iter=200,
    tol=1e-6,
    seed=42,
)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `k_range` | `list[int]` | -- | Candidate numbers of components |
| `nbasis` | `int` | `5` | Number of B-spline basis functions |
| `max_iter` | `int` | `200` | Maximum EM iterations |
| `tol` | `float` | `1e-6` | Convergence tolerance |
| `seed` | `int` | `42` | Random seed |

**Returns** a dictionary:

| Key | Shape / Type | Description |
|---|---|---|
| `cluster` | `(n,)` int | Cluster labels from the best model |
| `membership` | `(n, k_best)` | Posterior membership probabilities |
| `bic_values` | `list[(k, bic)]` | BIC for each candidate $k$ |
| `icl_values` | `list[(k, icl)]` | ICL for each candidate $k$ |

!!! info "BIC vs ICL"
    BIC penalises model complexity; ICL adds an entropy penalty that favours well-separated clusters. When both agree, the choice is clear. When they disagree, ICL tends to prefer fewer, crisper clusters.

---

## Cluster quality indices

### Silhouette score

The silhouette score measures how similar each observation is to its own cluster compared with the nearest neighbouring cluster. Values range from $-1$ (misclassified) to $+1$ (perfectly clustered).

```python
from pyfda.clustering import silhouette_score
from pyfda.metric import lp_self_1d

dist_matrix = lp_self_1d(data, argvals, p=2.0)
labels = result["cluster"].astype(np.int64)
sil = silhouette_score(dist_matrix, labels)
print(f"Mean silhouette: {np.mean(sil):.3f}")
```

### Calinski-Harabasz index

A higher Calinski-Harabasz index indicates better-defined clusters (larger between-cluster variance relative to within-cluster variance).

```python
from pyfda.clustering import calinski_harabasz

ch = calinski_harabasz(dist_matrix, labels)
print(f"Calinski-Harabasz: {ch:.1f}")
```

---

## Selecting the optimal number of clusters

A common strategy is to run k-means for several values of $k$ and pick the one that maximises the mean silhouette score.

```python
import numpy as np
from pyfda.simulation import simulate
from pyfda.clustering import kmeans_fd, silhouette_score
from pyfda.metric import lp_self_1d

# Three-group data
argvals = np.linspace(0, 1, 100)
g1 = simulate(25, argvals, n_basis=5, seed=1)
g2 = simulate(25, argvals, n_basis=5, seed=2) + 3.0
g3 = simulate(25, argvals, n_basis=5, seed=3) - 3.0
data = np.vstack([g1, g2, g3])

dist = lp_self_1d(data, argvals, p=2.0)

scores = {}
for k in range(2, 9):
    res = kmeans_fd(data, argvals, k=k, seed=42)
    labels = res["cluster"].astype(np.int64)
    sil = silhouette_score(dist, labels)
    scores[k] = float(np.mean(sil))
    print(f"k={k}  silhouette={scores[k]:.3f}")

best_k = max(scores, key=scores.get)
print(f"\nOptimal k = {best_k}")
```

---

## Using different distance metrics

The clustering functions use $L^2$ distance internally. To cluster with a different metric you can compute the distance matrix first, then pass the resulting labels to the quality indices.

```python
from pyfda.metric import dtw_self_1d, hausdorff_self_1d

# DTW-based distance matrix
dist_dtw = dtw_self_1d(data, p=2.0, w=10)

# Hausdorff distance matrix
dist_haus = hausdorff_self_1d(data, argvals)
```

You can then use these matrices with `silhouette_score` and `calinski_harabasz` to evaluate how well a given labeling fits under an alternative metric.

---

## Full example -- three-group simulation

```python
import numpy as np
from pyfda.simulation import simulate
from pyfda.clustering import kmeans_fd, fuzzy_cmeans_fd, gmm_cluster

# ── Simulate three groups ─────────────────────────────────────
argvals = np.linspace(0, 1, 100)
g1 = simulate(30, argvals, n_basis=5, seed=10)
g2 = simulate(30, argvals, n_basis=5, seed=20) + 4.0
g3 = simulate(30, argvals, n_basis=5, seed=30) - 4.0
data = np.vstack([g1, g2, g3])
true_labels = np.array([0]*30 + [1]*30 + [2]*30)

# ── K-means ───────────────────────────────────────────────────
km = kmeans_fd(data, argvals, k=3, seed=42)
print("K-means converged:", km["converged"])

# ── Fuzzy C-means ─────────────────────────────────────────────
fcm = fuzzy_cmeans_fd(data, argvals, k=3, seed=42)
# Show membership entropy per observation
entropy = -np.sum(fcm["membership"] * np.log(fcm["membership"] + 1e-12), axis=1)
print(f"Mean membership entropy: {entropy.mean():.3f}")

# ── GMM (auto-select k) ──────────────────────────────────────
gm = gmm_cluster(data, argvals, k_range=[2, 3, 4, 5], nbasis=7, seed=42)
print("BIC values:", gm["bic_values"])

# ── Visualize cluster centers (optional) ──────────────────────
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    methods = [("K-means", km), ("Fuzzy C-means", fcm), ("GMM", gm)]

    for ax, (name, res) in zip(axes, methods):
        for i in range(3):
            mask = res["cluster"] == i
            ax.plot(argvals, data[mask].T, alpha=0.15)
        if "centers" in res:
            for c in res["centers"]:
                ax.plot(argvals, c, "k-", linewidth=2)
        ax.set_title(name)

    plt.tight_layout()
    plt.savefig("clustering.png", dpi=150)
    plt.show()
except ImportError:
    pass
```
