# Sonar: Mine vs Rock — when does elastic alignment help?

**Dataset:** Sonar — 208 sonar returns, each a 60-band energy spectrum, bounced
off either a metal cylinder (a "Mine") or a roughly cylindrical rock (a "Rock").
The task is the classic Gorman–Sejnowski benchmark: classify the object from its
spectrum.

Each observation is a 60-point **curve** — energy as a function of frequency
band. A natural question for functional data is whether the curves should be
**aligned** before comparing them. Elastic alignment (via the transported
square-root velocity framework, TSRVF) factors out phase, comparing curves by
*shape* alone. That is a powerful idea for data where features drift along the
$x$-axis — but is sonar such a case? This study builds the two representations
side by side and lets the accuracy numbers decide. The honest answer here turns
out to be **no**: on sonar, elastic alignment *removes* discriminative signal.

## The two classes

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_sonar

band, X, meta = load_sonar()
is_mine = meta["label"].to_numpy() == "Mine"

f, ax = fig()
ax.plot(band, X[is_mine].T, color="#e8710a", lw=0.6, alpha=0.15)
ax.plot(band, X[~is_mine].T, color="#3f51b5", lw=0.6, alpha=0.15)
ax.plot(band, X[is_mine].mean(0), color="#e8710a", lw=2.6, label="Mine (mean)")
ax.plot(band, X[~is_mine].mean(0), color="#3f51b5", lw=2.6, label="Rock (mean)")
ax.set(title="Sonar spectra: Mine vs Rock",
       xlabel="frequency band (1–60)", ylabel="energy")
ax.legend()
print(render(f))
```

The two class-mean spectra (bold) differ mostly in **level and curvature** in
the mid-frequency bands, not in the *position* of a feature. The individual
curves are noisy and heavily overlapping — this is a genuinely hard problem
(published accuracies hover around 80% for nearest-neighbour methods). Crucially,
band $k$ means the same physical frequency for every return: the spectra are
already registered on a common axis.

## Two distance geometries

We compare curves two ways, both as **distance matrices** that we feed to the
same $k$-nearest-neighbour classifier so the *only* thing that changes is the
geometry:

- **$L^2$ distance** — `fdars.metric.lp_self_1d(X, band, 2.0)` — the ordinary
  functional distance $\lVert x_i - x_j\rVert_2$, comparing curves band by band.
- **Elastic distance** — `fdars.alignment.elastic_self_distance_matrix` — the
  amplitude (shape) distance after optimally warping the frequency axis, i.e. the
  TSRVF geodesic distance. Two curves are close if one can be *reparameterised*
  into the other.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_sonar
from fdars.metric import lp_self_1d
from fdars.alignment import elastic_self_distance_matrix

band, X, meta = load_sonar()
order = np.argsort(meta["label"].to_numpy())   # group Mine/Rock for block structure
DL2 = np.asarray(lp_self_1d(X, band, 2.0))[order][:, order]
DEL = np.asarray(elastic_self_distance_matrix(X, band))[order][:, order]

f, axes = fig(ncols=2, figsize=(9.0, 4.0))
for ax, D, name in zip(axes, [DL2, DEL], ["$L^2$ distance", "elastic distance"]):
    im = ax.imshow(D, cmap="magma_r", aspect="auto")
    ax.set(title=name, xlabel="curve (sorted by class)", ylabel="curve")
    ax.grid(False)
    f.colorbar(im, ax=ax, fraction=0.046)
print(render(f))
```

Both matrices are sorted so the first block is one class and the second the
other. Under $L^2$ the two diagonal blocks are visibly darker (within-class pairs
are closer) than the off-diagonal blocks — the class structure is *in* the
geometry. Under the elastic distance that block contrast is much fainter: warping
the frequency axis lets a Rock spectrum bend into a Mine-like shape, washing out
the between-class gap.

## TSRVF as a representation

The TSRVF (`fdars.alignment.tsrvf_transform`) makes the alignment explicit: it
iteratively estimates a Karcher-mean shape and returns each curve's
**tangent vector** — its shape residual in the aligned space — together with the
warping functions $\gamma_i$ that carried each curve onto the mean.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_sonar
from fdars.alignment import tsrvf_transform

band, X, meta = load_sonar()
is_mine = meta["label"].to_numpy() == "Mine"
ts = tsrvf_transform(X, band, max_iter=15)
gammas = np.asarray(ts["gammas"])            # (n, m) warping functions
mean_shape = np.asarray(ts["mean"])

f, axes = fig(ncols=2, figsize=(9.0, 4.0))
axes[0].plot(band, gammas[is_mine].T, color="#e8710a", lw=0.5, alpha=0.25)
axes[0].plot(band, gammas[~is_mine].T, color="#3f51b5", lw=0.5, alpha=0.25)
axes[0].plot([band[0], band[-1]], [band[0], band[-1]], color="#6c757d", ls=":", lw=1)
axes[0].set(title="Warping functions $\\gamma_i$", xlabel="band", ylabel="$\\gamma(band)$")
axes[1].plot(band, mean_shape, color="#198754", lw=2.4)
axes[1].set(title="Karcher-mean shape", xlabel="band", ylabel="aligned energy")
print(render(f))
```

The warping functions depart substantially from the diagonal (dotted) — the
algorithm *is* finding phase to remove. But because the bands are already
physically registered, that "phase" is mostly fitting **noise**: it lets curves
of either class flex toward the common mean, and in doing so it discards exactly
the level-and-curvature differences the class-mean plot showed.

## Does elastic alignment help classification?

We run 5-fold cross-validated $k$-NN on each distance matrix. To be fair, both
sides use the identical fold splits and the same neighbour rule — a small
majority-vote classifier written on the page — so any accuracy gap is due to the
geometry, not the classifier. (The built-in `knn_classify_from_distances` reports
*resubstitution* accuracy, which is optimistic; we want a held-out estimate.)

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_sonar
from fdars.metric import lp_self_1d
from fdars.alignment import elastic_self_distance_matrix

band, X, meta = load_sonar()
y = (meta["label"].to_numpy() == "Mine").astype(int)
DL2 = np.asarray(lp_self_1d(X, band, 2.0))
DEL = np.asarray(elastic_self_distance_matrix(X, band))

def cv_knn(D, y, k, folds=5, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    accs = []
    for fold in range(folds):
        te = idx[fold::folds]
        tr = np.setdiff1d(idx, te)
        hit = 0
        for i in te:
            nn = tr[np.argsort(D[i, tr])[:k]]     # k nearest training curves
            hit += int(round(y[nn].mean())) == y[i]
        accs.append(hit / len(te))
    return float(np.mean(accs))

ks = [1, 3, 5, 7]
accL2 = [cv_knn(DL2, y, k) for k in ks]
accEL = [cv_knn(DEL, y, k) for k in ks]

f, ax = fig()
w = 0.36
xpos = np.arange(len(ks))
ax.bar(xpos - w/2, accL2, w, color="#3f51b5", label="$L^2$ kNN")
ax.bar(xpos + w/2, accEL, w, color="#e8710a", label="elastic kNN")
ax.axhline(max(y.mean(), 1 - y.mean()), color="#6c757d", ls="--", lw=1,
           label="majority baseline")
ax.set(title="5-fold CV accuracy: L2 vs elastic distance",
       xlabel="k (neighbours)", ylabel="accuracy", ylim=(0.5, 0.9))
ax.set_xticks(xpos); ax.set_xticklabels([f"k={k}" for k in ks])
ax.legend()
print(render(f))
```

The verdict is unambiguous. Plain $L^2$ $k$-NN reaches about **83%** at
$k=3$ — in line with the literature — while elastic $k$-NN sits **10–13 points
lower** at every $k$, barely above the majority baseline. Warping the frequency
axis does not help; it actively hurts.

!!! note "Why elastic alignment loses here"
    Elastic methods pay off when the *same feature* appears at a **shifted or
    stretched location** across curves — misaligned peaks in growth-velocity
    curves, phase-drifting gait cycles, ROI-registered spectra. Sonar bands are
    already a fixed physical frequency grid, so there is no phase to remove. The
    discriminative signal lives in **amplitude at fixed bands**, which is exactly
    what $L^2$ preserves and what elastic alignment throws away. This is the
    honest, negative result: a more sophisticated representation is not a free
    lunch — it must match the structure of the data.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `lp_self_1d(data, argvals, p)` | `p` | Order of the $L^p$ functional distance ($p=2$ is $L^2$) |
| `elastic_self_distance_matrix(data, argvals, lambda_)` | `lambda_` | Roughness penalty on the warping (0 = unpenalised) |
| `tsrvf_transform(data, argvals, max_iter, tol, lambda_)` | `max_iter` | Karcher-mean iterations; returns `gammas`, `mean`, `tangent_vectors` |
| `knn_classify_from_distances(dist_matrix, labels, k)` | `k` | Neighbour count (resubstitution accuracy) |

## See also

- [Elastic alignment](../align/elastic-alignment.md) for the TSRVF machinery in
  depth, including where it *does* help.
- [Growth curve alignment](growth-alignment.md) for a case study where phase
  removal is the whole point.
- [Classification](../regression/classification.md) for the functional
  classifiers used here.
