# Weather curves: FPCA and clustering

**Dataset:** Canadian Weather — daily mean temperature (°C) over a 365-day year
for 35 weather stations, each tagged with its climatic region (Atlantic,
Continental, Pacific, Arctic).

Each station is a temperature *curve*. Two questions follow naturally: what are
the dominant **modes of variation** across stations (functional PCA), and do
stations fall into **groups** that recover Canada's climate regions
(functional clustering)? This case study answers both with `fdars`, using only
the curves — never the region labels — until the very end, where we check them.

## Temperature curves by region

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("temperature")
region = meta["region"].to_numpy()
colors = {"Atlantic": "#3f51b5", "Continental": "#e8710a",
          "Pacific": "#198754", "Arctic": "#dc3545"}

f, ax = fig()
for r, c in colors.items():
    ax.plot(day, X[region == r].T, color=c, lw=1, alpha=0.55)
for r, c in colors.items():
    ax.plot([], [], color=c, label=r)
ax.set(title="Daily mean temperature, 35 Canadian stations",
       xlabel="day of year", ylabel="temperature (°C)")
ax.legend(ncol=2)
print(render(f))
```

Every station shows the same summer-peaked annual cycle, but they differ in
**level** (Arctic stations sit far below Pacific ones) and in **amplitude**
(coastal Pacific stations are mild year-round; Continental ones swing hard
between summer and winter).

## Functional PCA: modes of variation

`fdars.regression.fpca` decomposes the curves into a mean plus a few orthogonal
**principal component functions** $\phi_k(t)$, so each station is

$$
x_i(t) \;\approx\; \bar x(t) \;+\; \sum_{k=1}^{K} \xi_{ik}\,\phi_k(t),
$$

with `scores` $\xi_{ik}$ and `rotation` columns $\phi_k$. The
`singular_values` give each component's share of variance.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.regression import fpca

day, X, meta = load_canadian_weather("temperature")
pc = fpca(X, day, n_comp=3)
mean = np.asarray(pc["mean"])
phi = np.asarray(pc["rotation"])                 # (365, 3)
sv = np.asarray(pc["singular_values"])
ve = sv ** 2 / np.sum(sv ** 2)                    # variance explained

f, ax = fig()
sd = np.asarray(pc["scores"]).std(axis=0)
for k, c in zip(range(2), ["#3f51b5", "#e8710a"]):
    ax.plot(day, mean + sd[k] * phi[:, k], color=c, lw=1.6,
            label=f"mean + PC{k+1} ({ve[k]*100:.0f}%)")
    ax.plot(day, mean - sd[k] * phi[:, k], color=c, lw=1.6, ls="--")
ax.plot(day, mean, color="#6c757d", lw=2.4, label="mean")
ax.set(title="FPCA modes: mean ± each component",
       xlabel="day of year", ylabel="temperature (°C)")
ax.legend(ncol=2)
print(render(f))
```

**PC1 (≈89% of variance)** shifts the whole curve up or down — it is an overall
*warmth* axis separating Arctic from temperate stations. **PC2 (≈9%)** widens or
narrows the summer-to-winter gap — a *continentality* axis. Two numbers per
station already capture nearly all of the variation.

The FPCA **scores** give each station a coordinate in this 2-D space:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.regression import fpca

day, X, meta = load_canadian_weather("temperature")
pc = fpca(X, day, n_comp=3)
sc = np.asarray(pc["scores"])
region = meta["region"].to_numpy()
colors = {"Atlantic": "#3f51b5", "Continental": "#e8710a",
          "Pacific": "#198754", "Arctic": "#dc3545"}

f, ax = fig(figsize=(6.0, 4.6))
for r, c in colors.items():
    m = region == r
    ax.scatter(sc[m, 0], sc[m, 1], color=c, s=40, alpha=0.85,
               edgecolor="white", label=r)
ax.set(title="Stations in FPCA score space",
       xlabel="PC1 (overall warmth)", ylabel="PC2 (continentality)")
ax.legend()
print(render(f))
```

The regions separate cleanly along these two axes even though FPCA never saw
the labels.

## Clustering the curves

`fdars.clustering.kmeans_fd` groups the curves directly (using an
$L^2$ metric in function space). We ask for 4 clusters and score the partition
with `silhouette_score_data`.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.clustering import kmeans_fd, silhouette_score_data

day, X, meta = load_canadian_weather("temperature")
km = kmeans_fd(X, day, k=4, seed=0)
labels = np.asarray(km["cluster"])
centers = np.asarray(km["centers"])
sil = float(np.mean(np.asarray(silhouette_score_data(X, day, labels))))

palette = ["#3f51b5", "#e8710a", "#198754", "#dc3545"]
f, ax = fig()
for k in range(4):
    ax.plot(day, X[labels == k].T, color=palette[k], lw=0.8, alpha=0.35)
    ax.plot(day, centers[k], color=palette[k], lw=2.6)
ax.set(title=f"k-means on temperature curves (mean silhouette {sil:.2f})",
       xlabel="day of year", ylabel="temperature (°C)")
print(render(f))
```

The four cluster-mean curves (bold) are a clean summary: a cold low-amplitude
Arctic group, a mild Pacific group, and warmer/cooler Continental–Atlantic
groups in between.

Finally, do the unsupervised clusters line up with the known regions?

```python exec="1" html="1" source="above"
import numpy as np, pandas as pd
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.clustering import kmeans_fd

day, X, meta = load_canadian_weather("temperature")
labels = np.asarray(kmeans_fd(X, day, k=4, seed=0)["cluster"])
tab = pd.crosstab(meta["region"], pd.Series(labels, name="cluster"))

f, ax = fig(figsize=(5.4, 4.0))
im = ax.imshow(tab.values, cmap="Blues", aspect="auto")
ax.set_xticks(range(tab.shape[1])); ax.set_xticklabels(tab.columns)
ax.set_yticks(range(tab.shape[0])); ax.set_yticklabels(tab.index)
for i in range(tab.shape[0]):
    for j in range(tab.shape[1]):
        ax.text(j, i, tab.values[i, j], ha="center", va="center",
                color="#222", fontsize=11)
ax.set(title="Clusters vs. climate region", xlabel="k-means cluster",
       ylabel="region")
ax.grid(False)
print(render(f))
```

Each region concentrates in one or two clusters — the geography is largely
recovered from temperature shape alone.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `fpca(data, argvals, n_comp)` | `n_comp` | Number of principal components |
| `kmeans_fd(data, argvals, k, max_iter, tol, seed)` | `k`, `seed` | Number of clusters and RNG seed |
| `silhouette_score_data(data, argvals, labels)` | `labels` | Per-observation silhouette; average for a quality score |

## See also

- [Functional PCA](../represent/fpca.md) for the decomposition in depth.
- [Clustering functional data](../analyze/clustering.md) for other clustering
  methods (fuzzy c-means, GMM) and choosing `k`.
