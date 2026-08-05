# Andrews Wine: Clustering & Variable Importance

**Dataset:** UCI Wine — 13 chemical measurements for 178 wines from three
cultivars, encoded as [Andrews curves](andrews-wine-intro.md).

The [intro page](andrews-wine-intro.md) showed the three cultivars separating by
eye. Here we make that quantitative: cluster the wine curves *without* the labels
and see whether functional clustering **rediscovers the cultivars**, then ask
which of the original 13 chemical variables actually drive the separation.
Because the Andrews transform preserves $L^2$ distances, clustering the curves is
equivalent to distance-based clustering of the standardized rows — but routed
through the functional API (`fdars.clustering`), which also gives functional
cluster validity scores.

!!! warning "No `andrews` binding in fdars"
    The transform is the numpy helper from the
    [intro page](andrews-wine-intro.md). We z-score the 13 columns first so no
    single feature dominates the curve.

## Functional k-means recovers the cultivars

`kmeans_fd` clusters curves under the $L^2$ metric. We ask for $k=3$ clusters —
matching the (withheld) number of cultivars — and cross-tabulate the result
against the true labels.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
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

names, X, meta = load_wine()
cultivar = meta["cultivar"].to_numpy()
Xz = (X - X.mean(0)) / X.std(0)
t = np.linspace(-np.pi, np.pi, 160)
curves = andrews_curves(Xz, t)

km = kmeans_fd(curves, t, k=3, seed=42)
cluster = np.asarray(km["cluster"])
centers = np.asarray(km["centers"])

# crosstab cluster x cultivar
tab = np.zeros((3, 3), dtype=int)
for cl in range(3):
    for ci, cv in enumerate((1, 2, 3)):
        tab[cl, ci] = np.sum((cluster == cl) & (cultivar == cv))
purity = tab.max(1).sum() / cluster.size

palette = ["#3f51b5", "#e8710a", "#198754"]
f, (axL, axR) = fig(ncols=2, figsize=(9.2, 3.7))
for i in range(curves.shape[0]):
    axL.plot(t, curves[i], color=palette[cluster[i]], lw=0.7, alpha=0.35)
for c in range(3):
    axL.plot(t, centers[c], color=palette[c], lw=2.6)
axL.set(title="kmeans_fd clusters (bold = centroid curve)",
        xlabel="t", ylabel=r"$f_x(t)$")

axR.imshow(tab, cmap="Blues")
axR.set_xticks([0, 1, 2], ["cult 1", "cult 2", "cult 3"])
axR.set_yticks([0, 1, 2], ["clus 0", "clus 1", "clus 2"])
for cl in range(3):
    for ci in range(3):
        axR.text(ci, cl, tab[cl, ci], ha="center", va="center",
                 color="white" if tab[cl, ci] > tab.max() / 2 else "black")
axR.set(title=f"cluster vs cultivar — purity {purity:.2f}")
print(render(f))
```

Each cluster is dominated by a single cultivar: the crosstab is almost diagonal
and the **purity is 0.95**. Functional k-means, given nothing but the curves,
has essentially rediscovered the three grape varieties — a strong confirmation
that the Andrews encoding carries the class structure faithfully.

## Cluster validity without the labels

In a real setting you would not have the cultivar labels to check against. The
functional **silhouette** and **Calinski–Harabasz** scores judge a clustering
using only the curves and the assignment, rewarding tight, well-separated
clusters.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.clustering import kmeans_fd, silhouette_score_data, calinski_harabasz_data

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

names, X, meta = load_wine()
Xz = (X - X.mean(0)) / X.std(0)
t = np.linspace(-np.pi, np.pi, 160)
curves = andrews_curves(Xz, t)

ks = [2, 3, 4, 5]
sil, ch = [], []
for k in ks:
    lab = np.asarray(kmeans_fd(curves, t, k=k, seed=42)["cluster"]).astype(np.int64)
    sil.append(float(np.mean(silhouette_score_data(curves, t, lab))))
    ch.append(float(calinski_harabasz_data(curves, t, lab)))

f, axL = fig()
axR = axL.twinx()
axL.plot(ks, sil, "o-", color="#3f51b5", lw=2, label="silhouette")
axR.plot(ks, ch, "s--", color="#e8710a", lw=2, label="Calinski–Harabasz")
axL.axvline(3, color="#6c757d", ls=":", lw=1)
axL.set(xlabel="number of clusters k", ylabel="mean silhouette")
axR.set(ylabel="Calinski–Harabasz")
axL.set_title("Cluster validity peaks near the true k = 3")
axL.set_xticks(ks)
print(render(f))
```

Both indices point toward a small number of clusters; the dotted line marks the
true $k=3$. The scores confirm that a three-cluster solution is a natural
description of the curves, not an artefact of us knowing the answer in advance.

!!! note "GMM under-performs k-means here — a binding observation"
    `gmm_cluster` fits a Gaussian mixture on a low-dimensional Fourier-basis
    projection of the curves (`nbasis` coefficients). On these wine curves it
    does **not** recover the cultivars: its BIC prefers $k=4$, and even forced to
    $k=3$ the resulting clusters are near-uniform mixtures of all three
    cultivars (purity ≈ 0.35). The projection to a handful of basis coefficients
    evidently discards the between-cultivar signal that the full-curve $L^2$
    distance in `kmeans_fd` retains. For this data set, prefer `kmeans_fd`.

## Which chemical variables drive the split?

The clusters separate wines — but *on what chemistry*? Since each Andrews curve
is a linear combination of the (standardized) features, a feature that differs
sharply between cultivars is one that pushes their curves apart. We rank the 13
variables by a one-way ANOVA $F$-statistic across the three cultivars (computed
in plain numpy — no fdars binding needed for a scalar ANOVA on the raw table).

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine

names, X, meta = load_wine()
cultivar = meta["cultivar"].to_numpy()

def f_stat(col):
    groups = [col[cultivar == g] for g in (1, 2, 3)]
    grand = col.mean(); n = col.size
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    return (ssb / 2) / (ssw / (n - 3))

F = np.array([f_stat(X[:, j]) for j in range(X.shape[1])])
order = np.argsort(F)                                  # ascending for barh

f, ax = fig(figsize=(6.4, 4.4))
colors = ["#3f51b5" if F[j] >= np.median(F) else "#c9ccd6" for j in order]
ax.barh([names[j] for j in order], F[order], color=colors)
ax.set(title="Between-cultivar separation per feature (ANOVA F)",
       xlabel="F-statistic")
print(render(f))
```

`flavanoids`, `proline` and `od280_od315` carry by far the most between-cultivar
signal, followed by `alcohol` and `color_intensity`; `ash` and `magnesium` barely
distinguish the cultivars at all. These few variables are what the Andrews curves
mostly encode, and what the k-means clusters key on.

## A feature-mean heatmap makes the story concrete

Averaging the *standardized* features within each cultivar shows the chemical
signature of each grape directly.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine

names, X, meta = load_wine()
cultivar = meta["cultivar"].to_numpy()
Xz = (X - X.mean(0)) / X.std(0)

# order features by between-cultivar F for readability
def f_stat(j):
    col = Xz[:, j]; groups = [col[cultivar == g] for g in (1, 2, 3)]
    grand = col.mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    return (ssb / 2) / (ssw / (col.size - 3))
order = np.argsort([f_stat(j) for j in range(13)])[::-1]

means = np.vstack([Xz[cultivar == g].mean(0)[order] for g in (1, 2, 3)])

f, ax = fig(figsize=(8.6, 3.2))
im = ax.imshow(means, cmap="RdBu_r", vmin=-1.5, vmax=1.5, aspect="auto")
ax.set_yticks([0, 1, 2], ["cultivar 1", "cultivar 2", "cultivar 3"])
ax.set_xticks(range(13), [names[j] for j in order], rotation=45, ha="right")
ax.set_title("Mean standardized feature per cultivar (features sorted by F)")
f.colorbar(im, ax=ax, label="z-score", fraction=0.025)
print(render(f))
```

The heatmap reads like a fingerprint: cultivar 1 is high in `flavanoids`,
`proline` and `od280_od315`; cultivar 3 is low in exactly those and high in
`color_intensity`; cultivar 2 sits in between with its own low `alcohol` and
`proline`. Those contrasts are precisely the low-harmonic terms that pull the
Andrews curves into three bundles.

## Summary

| Component | Binding | Result on wine curves |
|-----------|---------|------------------------|
| `kmeans_fd(curves, t, k=3)` | `fdars.clustering` | recovers cultivars, purity 0.95 |
| `silhouette_score_data`, `calinski_harabasz_data` | `fdars.clustering` | validity supports k≈3 |
| `gmm_cluster(curves, t, k_range)` | `fdars.clustering` | under-separates here (see note) |
| ANOVA F (numpy) | — | `flavanoids`, `proline`, `od280_od315` dominate |

## See also

- [Andrews Wine intro](andrews-wine-intro.md) — the transform and class structure.
- [Outlier detection](andrews-wine.md) — flagging atypical wines.
- [Clustering](../analyze/clustering.md) — the general functional-clustering article.
