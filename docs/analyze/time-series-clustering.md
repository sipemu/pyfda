---
title: Time-Series Clustering
---

# Time-Series Clustering

[Clustering](clustering.md) groups curves by their $L^2$ distance to a mean curve. That works when curves in a group are close **pointwise**. Many sensor and signal datasets are not: members of a group share a *shape* but differ in gain, offset or timing. `fdars.clustering` has three clusterers from the time-series literature for this case. Each is built on a distance that factors out one of these nuisances.

| Method | Function | Distance | Centroid | Invariant to |
|---|---|---|---|---|
| k-Shape | `kshape_fd` | shape-based distance (SBD) | shape extraction (eigenvector) | offset, positive scaling, shift |
| SBD k-medoids | `sbd_kmedoids` | SBD | an actual curve (medoid) | offset, positive scaling, shift |
| DTW k-means | `dtw_kmeans`, `dtw_kmeans_multivariate` | DTW (optionally windowed) | DTW barycenter (DBA) | local time warping |

For phase-aware clustering in the elastic (SRSF) framework, see [Elastic Clustering](elastic-clustering.md) and `align_cluster_fd` in [Advanced Clustering](advanced-clustering.md#align-and-cluster-simultaneous-alignment-and-clustering).

## k-Shape

k-Shape (Paparrizos & Gravano 2015) is a Lloyd-type algorithm on the [shape-based distance](../represent/elastic-ts-distances.md#shape-based-distance-sbd). Curves are z-normalised, so gain and offset play no role, and every comparison slides one curve over the other to the best-correlated lag.

1. **Assignment:** each curve joins the centroid with the smallest SBD.
2. **Shape extraction:** each centroid is recomputed as the curve that maximises the sum of squared normalised cross-correlations with the cluster members. The members are first shifted to their best lag against the old centroid and stacked into $X$ ($n_k \times m$). The new centroid is the top eigenvector of $M = Q^\top X^\top X\, Q$, where $Q = I_m - \tfrac{1}{m}\mathbf{1}\mathbf{1}^\top$ centres over time. Its sign is chosen to minimise the total SBD to the members, and it is z-normalised. It is *not* an arithmetic mean, which would blur members that are still misaligned.

`kshape_fd(data, n_clusters=2, n_init=10, max_iter=100, tol=1e-6, seed=0)` runs `n_init` restarts from random partitions (restart $r$ is seeded `seed + r`) and keeps the lowest-inertia run. It returns `centroids` `(k, m)` (z-normalised), `cluster`, `inertia`, `iter`, `converged`, `n_init_best` (the winning restart) and `model`, whose `predict(new_data)` assigns new curves to the nearest centroid by SBD.

**SBD k-medoids.** `sbd_kmedoids(data, k=2, max_iter=100, seed=42)` builds the SBD matrix and clusters it with k-medoids. It is equivalent to `alignment.kmedoids_from_distances(metric.sbd_distance_matrix(data), ...)` and returns the same keys (`labels`, `medoid_indices`, `within_distances`, `total_within_distance`, `n_iter`, `converged`). The cluster representatives are real curves, not synthesised shapes.

The 24 curves below come from two shapes, a sine and a square wave. Each curve has a random gain (0.5–3), offset (−2 to 2) and circular shift.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from sklearn.metrics import adjusted_rand_score
import fdars.clustering as fc

rng = np.random.default_rng(3)
m = 64
t = np.linspace(0, 1, m)
def member(k):                                   # shape family k, random gain/offset/shift
    base = np.sin(2 * np.pi * t) if k == 0 else 0.8 * np.sign(np.sin(2 * np.pi * t))
    y = rng.uniform(0.5, 3) * base + rng.uniform(-2, 2)
    return np.roll(y, rng.integers(-8, 8)) + 0.1 * rng.standard_normal(m)

truth = np.repeat([0, 1], 12)
X = np.array([member(k) for k in truth])

ks = fc.kshape_fd(X, n_clusters=2, seed=0)
km = fc.kmeans_fd(X, t, 2, seed=0)
sk = fc.sbd_kmedoids(X, k=2)
dk = fc.dtw_kmeans(X, n_clusters=2, window="sakoe_chiba", radius=8, seed=0)

f, (a0, a1) = fig(1, 2, figsize=(12, 3.8))
for xi, k in zip(X, truth):
    a0.plot(t, xi, color=["#3f51b5", "#e8710a"][k], lw=1.1, alpha=0.7)
a0.set(title="24 curves: two shapes, random gain, offset and shift", xlabel="t")
for c, col in zip(ks["centroids"], ["#198754", "#6f42c1"]):
    a1.plot(t, c, color=col, lw=2.4)
a1.set(title="k-Shape centroids (z-normalised)", xlabel="t")
print(render(f))
rows = [("k-Shape", ks["cluster"]), ("SBD k-medoids", sk["labels"]),
        ("DTW k-means", dk["cluster"]), ("L2 k-means", km["cluster"])]
print("<p>Adjusted Rand index against the true shapes: " + ", ".join(
    f"{name} {adjusted_rand_score(truth, lab):.2f}" for name, lab in rows) + "</p>")
print("FDARS_FENCE_OK")
```

k-Shape recovers both shapes exactly (ARI 1.00), and its centroids are a clean sine and square wave. SBD k-medoids uses the same distance but only lets real, noisy curves act as centres, and reaches ARI 0.54. DTW k-means and $L^2$ k-means are near chance (ARI 0.14 and 0.03): the gain and offset differences dominate their distances.

## DTW k-means

`dtw_kmeans` is tslearn's `TimeSeriesKMeans(metric="dtw")`: Lloyd iterations where assignment uses the DTW cost and each centroid is the [DTW barycenter (DBA)](../represent/dtw-toolkit.md#averaging-under-dtw) of its members. Each DBA update is warm-started from the previous centroid. Initial centroids come from k-means++ seeding on DTW costs (or pass `init=` a `(k, m)` array), `n_init` restarts are seeded `seed + r`, and an empty cluster is re-seeded in place. `inertia` is the mean DTW cost of each curve to its centroid.

| Parameter | Default | Meaning |
|---|---|---|
| `n_clusters` | 2 | number of clusters |
| `n_init`, `seed` | 10, 0 | restarts; the lowest-inertia run is kept |
| `max_iter`, `tol` | 50, 1e-6 | Lloyd iterations and inertia tolerance |
| `window`, `radius`, `window_fraction`, `max_slope` | `"none"` | DTW window for assignment and DBA |
| `init` | `None` = `"k-means++"` | or a `(k, m)` array of initial centroids |
| `dba_max_iter`, `dba_tol` | 30, 1e-5 | DBA iterations per centroid update |

Use it when group members have the same amplitude but their features occur at different times. Below, one group has one bump and the other two bumps, all at random positions.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from sklearn.metrics import adjusted_rand_score
import fdars.clustering as fc

rng = np.random.default_rng(4)
m = 80
t = np.linspace(0, 1, m)
g = lambda c: np.exp(-0.5 * ((t - c) / 0.05) ** 2)
def member(k):                       # one bump vs. two bumps, at random positions
    if k == 0:
        return g(rng.uniform(0.25, 0.75)) + 0.03 * rng.standard_normal(m)
    c = rng.uniform(0.25, 0.6)
    return g(c) + g(c + 0.18) + 0.03 * rng.standard_normal(m)

truth = np.repeat([0, 1], 10)
X = np.array([member(k) for k in truth])
dk = fc.dtw_kmeans(X, n_clusters=2, window="sakoe_chiba", radius=20, seed=0)
km = fc.kmeans_fd(X, t, 2, seed=0)

f, (a0, a1) = fig(1, 2, figsize=(12, 3.6))
for xi, k in zip(X, truth):
    a0.plot(t, xi, color=["#3f51b5", "#e8710a"][k], lw=1.1, alpha=0.7)
a0.set(title="One bump vs. two bumps, random positions", xlabel="t")
for c, col in zip(dk["centroids"], ["#198754", "#6f42c1"]):
    a1.plot(t, c, color=col, lw=2.4)
for c in km["centers"]:
    a1.plot(t, c, color="#6c757d", lw=1.4, ls="--")
a1.set(title="DTW k-means (solid) vs. L2 k-means (dashed) centres", xlabel="t")
print(render(f))
new = np.array([member(0), member(1)])
print(f"<p>ARI: DTW k-means {adjusted_rand_score(truth, dk['cluster']):.2f}, "
      f"L2 k-means {adjusted_rand_score(truth, km['cluster']):.2f}; "
      f"inertia {dk['inertia']:.4f}, converged={dk['converged']}; "
      f"predict(one-bump, two-bump) = {dk['model'].predict(new).tolist()}</p>")
print("FDARS_FENCE_OK")
```

The DBA centroids are a sharp single bump and a sharp double bump. The $L^2$ centres are smeared averages that mix both groups (ARI near 0). `model.predict` assigns new curves by DTW to the stored centroids, using the same window; cluster numbers are arbitrary, so here "one bump" happens to be cluster 1.

**Multichannel series.** `dtw_kmeans_multivariate` takes a list of `(d, m)` arrays or an `(n, d, m)` array (channels as rows) and uses dependent multichannel DTW with multivariate DBA centroids. `centroids` is a list of `(d, m)` arrays and `init` may be a list of `(d, m)` arrays or a `(k, d, m)` array. With $d = 1$ the result is bit-identical to `dtw_kmeans`.

```python exec="1" source="above" result="text"
import numpy as np
from sklearn.metrics import adjusted_rand_score
import fdars.clustering as fc

rng = np.random.default_rng(4)
t = np.linspace(0, 1, 80)
g = lambda c: np.exp(-0.5 * ((t - c) / 0.05) ** 2)
def series(k):                       # channel 0: the curve, channel 1: its slope
    c = rng.uniform(0.25, 0.6)
    x = g(c) if k == 0 else g(c) + g(c + 0.18)
    return np.vstack([x, np.gradient(x, t) / 10])

truth = np.repeat([0, 1], 10)
S = np.stack([series(k) for k in truth])          # (20, 2, 80)
res = fc.dtw_kmeans_multivariate(S, n_clusters=2, window="sakoe_chiba", radius=20)
print("ARI:", round(adjusted_rand_score(truth, res["cluster"]), 2))
print("centroid shapes:", [c.shape for c in res["centroids"]])
print("FDARS_FENCE_OK")
```

## Choosing a method

- **Gain and offset are nuisance, shapes are rigid:** k-Shape. It is fast (FFT cross-correlations) and its centroids are interpretable shapes.
- **You need actual curves as representatives, or a precomputed SBD matrix for other tools:** SBD k-medoids.
- **Amplitude matters, timing varies locally:** DTW k-means. Use a window (`radius` or `window_fraction`) to stop degenerate warps and to speed it up. Z-normalise beforehand if gain should not matter.
- **Timing variation should be modelled explicitly, with phase and amplitude separated:** elastic clustering ([Elastic Clustering](elastic-clustering.md), `align_cluster_fd`).

All three return an int64 label vector, so the cluster-quality tools of [Clustering](clustering.md) apply. Score them with `silhouette_score(dist_matrix, labels)` on the distance the method actually uses (e.g. `metric.sbd_distance_matrix`) rather than on $L^2$ distances.

## References

1. Paparrizos, J. & Gravano, L. (2015). k-Shape: efficient and accurate clustering of time series. *Proceedings of the 2015 ACM SIGMOD International Conference on Management of Data*, 1855–1870.
2. Petitjean, F., Ketterlin, A. & Gançarski, P. (2011). A global averaging method for dynamic time warping, with applications to clustering. *Pattern Recognition*, 44(3), 678–693.
3. Arthur, D. & Vassilvitskii, S. (2007). k-means++: the advantages of careful seeding. *Proceedings of the 18th Annual ACM-SIAM Symposium on Discrete Algorithms (SODA)*, 1027–1035.
4. Tavenard, R. et al. (2020). Tslearn, a machine learning toolkit for time series data. *Journal of Machine Learning Research*, 21(118), 1–6.
