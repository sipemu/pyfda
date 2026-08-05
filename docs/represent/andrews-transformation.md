# Andrews Transformation: From Tables to Curves

An **Andrews transformation** maps each row of a multivariate data table -- a plain feature vector $x = (x_1, x_2, \ldots, x_p)$ -- to a smooth periodic curve. Introduced by David Andrews in 1972 as a way to *visualize* high-dimensional data, it turns out to be a bridge into functional data analysis: once every observation is a curve, the whole `fdars` toolbox (depth, distances, clustering, outlier detection) applies to ordinary tabular data. This page shows the transform explicitly in numpy, then analyzes the resulting curves with real `fdars` functions.

!!! warning "No `andrews` binding in fdars"
    There is **no** Andrews-curve function in `fdars`. The transform is a handful of lines of numpy, shown in full below. `fdars` enters only *after* the transform, once the curves are wrapped in `Fdata`.

## The transform

Andrews encodes the feature vector as the coefficients of a truncated Fourier series in a dummy variable $t \in [-\pi, \pi]$:

$$
f_x(t) = \frac{x_1}{\sqrt{2}}
        + x_2 \sin t + x_3 \cos t
        + x_4 \sin 2t + x_5 \cos 2t + \cdots
$$

Each observation becomes one curve $f_x(t)$. The construction has two properties that make it useful rather than arbitrary:

- **Distance preservation.** By Parseval's theorem, the $L^2$ distance between two Andrews curves is proportional to the Euclidean distance between their feature vectors: $\int_{-\pi}^{\pi} \bigl(f_x(t) - f_y(t)\bigr)^2\,dt = \pi\,\lVert x - y\rVert^2$. Curves that look similar correspond to observations that *are* similar.
- **Mean preservation.** The Andrews curve of the sample mean equals the mean of the Andrews curves, so a "central" curve is a central observation.

Here is the entire transform in numpy -- there is no hidden machinery:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render

def andrews_curves(features, t):
    """Map rows of a (n, p) table to Andrews curves evaluated at t.

    f_x(t) = x1/sqrt(2) + x2 sin t + x3 cos t + x4 sin 2t + x5 cos 2t + ...
    """
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2               # 1,1,2,2,3,3,...
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

# A small synthetic table: 3 groups in a 4-dimensional feature space.
rng = np.random.default_rng(7)
group_means = np.array([[ 2.0,  0.0,  1.0,  0.0],
                        [ 0.0,  2.0,  0.0,  1.0],
                        [-2.0, -1.0,  1.0, -1.0]])
features = np.vstack([mu + 0.4 * rng.standard_normal((10, 4))
                      for mu in group_means])
labels = np.repeat([0, 1, 2], 10)

t = np.linspace(-np.pi, np.pi, 120)
curves = andrews_curves(features, t)          # (30, 120)

colors = ["#3f51b5", "#e8710a", "#198754"]
f, ax = fig()
for i in range(curves.shape[0]):
    ax.plot(t, curves[i], color=colors[labels[i]], lw=1, alpha=0.6)
ax.set(title="Andrews curves of a 3-group feature table",
       xlabel="t", ylabel=r"$f_x(t)$")
print(render(f))
```

The three colored bundles are already visible: rows from the same group in feature space trace out similar curves, because the transform preserves distances.

## Wrapping curves in `Fdata`

From here on the data is functional. Bundle the curves into an `fdars.Fdata` object and every method of the class becomes available.

```python
import numpy as np
from fdars import Fdata

fd = Fdata(curves, argvals=t)
print(fd.n_obs(), "curves on", fd.n_points(), "points")
```

| Step | Object | Notes |
|------|--------|-------|
| Feature table | `np.ndarray` (n, p) | Any multivariate data set |
| `andrews_curves(...)` | `np.ndarray` (n, m) | Pure numpy, shown above |
| `Fdata(curves, argvals=t)` | `fdars.Fdata` | Enables depth, distance, clustering |

## Depth: finding the central observation and outliers

Because Andrews curves preserve distances, **functional depth** of a curve is a sensible centrality measure for the underlying feature vector. The deepest curve is the "most typical" row; shallow curves flag multivariate outliers. We use `modified_band_1d` from [`fdars.depth`](depth-functions.md).

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.depth import modified_band_1d

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

rng = np.random.default_rng(7)
group_means = np.array([[ 2.0,  0.0,  1.0,  0.0],
                        [ 0.0,  2.0,  0.0,  1.0],
                        [-2.0, -1.0,  1.0, -1.0]])
features = np.vstack([mu + 0.4 * rng.standard_normal((10, 4))
                      for mu in group_means])
# Inject one clear multivariate outlier
features = np.vstack([features, np.array([6.0, -5.0, 4.0, 5.0])])

t = np.linspace(-np.pi, np.pi, 120)
curves = andrews_curves(features, t)
depth = np.asarray(modified_band_1d(curves, curves))
order = np.argsort(depth)
rng_d = np.ptp(depth) + 1e-9

f, ax = fig()
for i in order:                                    # faint = shallow (outlying)
    ax.plot(t, curves[i], color="#3f51b5", lw=1.1,
            alpha=0.15 + 0.8 * (depth[i] - depth.min()) / rng_d)
ax.plot(t, curves[order[-1]], color="#198754", lw=2.4, label="deepest (typical)")
ax.plot(t, curves[order[0]], color="#dc3545", lw=2.4, label="shallowest (outlier)")
ax.set(title="Depth of Andrews curves flags a multivariate outlier",
       xlabel="t", ylabel=r"$f_x(t)$")
ax.legend()
print(render(f))
```

The injected outlier receives the lowest depth and stands out as the red curve -- multivariate outlier detection carried out entirely through the functional representation.

## Distances and clustering

The distance-preservation property means we can cluster the *curves* and recover the groups in the *feature table*. Using `kmeans_fd` from [`fdars.clustering`](../analyze/clustering.md) on the Andrews curves reproduces the three groups.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.clustering import kmeans_fd

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

rng = np.random.default_rng(7)
group_means = np.array([[ 2.0,  0.0,  1.0,  0.0],
                        [ 0.0,  2.0,  0.0,  1.0],
                        [-2.0, -1.0,  1.0, -1.0]])
features = np.vstack([mu + 0.4 * rng.standard_normal((10, 4))
                      for mu in group_means])
t = np.linspace(-np.pi, np.pi, 120)
curves = andrews_curves(features, t)

km = kmeans_fd(curves, t, k=3)
cluster = np.asarray(km["cluster"])
centers = np.asarray(km["centers"])

palette = ["#3f51b5", "#e8710a", "#198754"]
f, ax = fig()
for i in range(curves.shape[0]):
    ax.plot(t, curves[i], color=palette[cluster[i]], lw=0.9, alpha=0.4)
for c in range(3):
    ax.plot(t, centers[c], color=palette[c], lw=2.6)
ax.set(title="kmeans_fd on Andrews curves recovers the 3 feature-space groups",
       xlabel="t", ylabel=r"$f_x(t)$")
print(render(f))
```

The bold curves are the cluster centroids in curve space; each corresponds to one group centroid in the original 4-dimensional table. Because the transform is linear, the centroid curve is exactly the Andrews curve of the feature-space centroid.

!!! note "Ordering matters"
    Andrews curves are not invariant to the *order* of the features: $x_1$ (the constant term) and the low harmonics ($x_2, x_3$) dominate the curve's shape, while high-index features contribute fast wiggles that are easy to overlook. Put the most informative variables first, and standardize columns beforehand so no single feature swamps the rest.

## Why route through functional data analysis?

For a table you could of course cluster the rows directly. The Andrews route is worthwhile when you want the *functional* machinery: robust functional depth for outlier detection, functional boxplots, band depth, or the alignment tools -- all of which have no direct multivariate analogue but become available once the table is a set of curves. The transform is cheap, exact, and (up to the choice of feature order) loses no information for $p$ features when the series is kept to $\lceil p/2\rceil$ harmonics.

## API summary

| Component | Where | Purpose |
|-----------|-------|---------|
| `andrews_curves(features, t)` | numpy (this page) | Fourier encoding of a feature table |
| `Fdata(curves, argvals)` | `fdars` | Wrap curves for functional analysis |
| `modified_band_1d(data, ref_data)` | `fdars.depth` | Centrality / outlier scores |
| `kmeans_fd(data, argvals, k)` | `fdars.clustering` | Cluster the curves |
| `lp_self_1d(data, argvals, p)` | `fdars.metric` | $L^p$ distance matrix (distance preservation) |
