# TSRVF: Linearized Elastic Analysis

Elastic alignment lives on a curved manifold: the space of functions modulo warping is not a vector space, so ordinary sums, means, and PCA do not apply directly. The **Transported Square-Root Velocity Function (TSRVF)** representation solves this by parallel-transporting every curve's SRVF to a single reference point -- the Karcher mean -- so that the resulting tangent vectors live in a common linear (Euclidean) space. Once curves are represented as TSRVF tangent vectors, standard linear statistics -- means, covariances, principal components -- become valid again.

The figure below shows a phase-varying sample, its SRSF representation (where the elastic metric becomes the $L^2$ metric), and the mean SRSF recovered by the TSRVF procedure.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import tsrvf_transform, srsf_transform

rng = np.random.default_rng(4)
n, m = 16, 120
t = np.linspace(0, 1, m)
base = np.sin(2 * np.pi * t) + 0.5 * np.sin(4 * np.pi * t)

# Phase-varying sample: compose the base with random monotone warps
data = np.zeros((n, m))
for i in range(n):
    warp = t ** rng.uniform(0.7, 1.5)
    warp = (warp - warp.min()) / np.ptp(warp)
    data[i] = np.interp(t, warp, base)

res = tsrvf_transform(data, t, max_iter=20, tol=1e-4)
mean_srsf = np.asarray(res["mean_srsf"])
q = np.array([srsf_transform(data[i], t) for i in range(n)])

f, (a1, a2) = fig(ncols=2, figsize=(9.5, 4.0))
a1.plot(t, data.T, color="#3f51b5", lw=1, alpha=0.5)
a1.set(title="Phase-varying curves $f_i$", xlabel="t", ylabel="f(t)")

a2.plot(t, q.T, color="#6f42c1", lw=1, alpha=0.35)
a2.plot(t, mean_srsf, color="#e8710a", lw=2.6, label="mean SRSF $\\mu_q$")
a2.set(title="SRSF representation", xlabel="t", ylabel="q(t)")
a2.legend(fontsize=8)
print(render(f))
```

---

## Concepts

### From SRSF to a shared tangent space

The **Square-Root Velocity Function (SRVF)**, also called the SRSF, maps a function $f$ to

$$
q(t) = \operatorname{sign}\!\big(\dot f(t)\big)\,\sqrt{\lvert \dot f(t)\rvert}.
$$

Under this map the Fisher-Rao elastic metric becomes the ordinary $L^2$ metric, so distances and geodesics can be computed with straightforward $L^2$ geometry. However, SRVFs of *misaligned* curves still differ by their warping, so their $L^2$ average blurs phase structure just like a cross-sectional mean.

The TSRVF construction fixes this in two steps:

1. **Align.** Compute the Karcher mean $\mu$ under the elastic metric and the optimal warp $\gamma_i$ that registers each curve to $\mu$.
2. **Transport.** Represent each aligned curve by its SRVF and parallel-transport it to the tangent space at $\mu_q$ (the mean's SRVF). The transported vectors

   $$
   v_i \;=\; \log_{\mu_q}\!\big(q_i \circ \gamma_i\big)
   $$

   are the **tangent vectors** returned by the transform. They live in a single Euclidean space $T_{\mu_q}$, so their sample mean, covariance, and principal components are meaningful.

Because $v_i$ are ordinary vectors, downstream analysis -- regression on scores, Gaussian modelling, hypothesis tests -- can proceed with classical multivariate tools while still respecting the elastic geometry that generated the data.

### Log-map vs. shooting representation

`tsrvf_transform_with_method` exposes the choice of how curves are mapped into the tangent space. The `log_map` method uses the Riemannian logarithm at $\mu_q$ (the default, geometrically exact for the sphere of unit SRSFs); alternative shooting-based representations trade a small amount of fidelity for speed and are useful when only the linear scores matter.

---

## Usage

`tsrvf_transform(data, argvals, ...)` returns the mean, its SRSF, and the transported tangent vectors in one call.

```python
import numpy as np
from fdars.alignment import tsrvf_transform

t = np.linspace(0, 1, 120)
# ... build an (n, m) array `data` of phase-varying curves ...

res = tsrvf_transform(data, t, max_iter=20, tol=1e-4, lambda_=0.0)

V          = res["tangent_vectors"]   # (n, m) -- transported tangent vectors
mu         = res["mean"]              # (m,)   -- Karcher mean function
mu_q       = res["mean_srsf"]         # (m,)   -- mean in SRSF space
srsf_norms = res["srsf_norms"]        # (n,)   -- ||q_i|| for each curve
gammas     = res["gammas"]            # (n, m) -- warps to the mean
converged  = res["converged"]         # bool
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Sample of $n$ curves on a common grid |
| `argvals` | `ndarray (m,)` | Evaluation grid (strictly increasing) |
| `max_iter` | `int` | Maximum Karcher-mean iterations (default `20`) |
| `tol` | `float` | Convergence tolerance (default `1e-4`) |
| `lambda_` | `float` | Warp regularization (default `0.0`) |

| Key | Type | Description |
|-----|------|-------------|
| `tangent_vectors` | `ndarray (n, m)` | Transported SRVF tangent vectors $v_i$ |
| `mean` | `ndarray (m,)` | Karcher mean function $\mu$ |
| `mean_srsf` | `ndarray (m,)` | Mean SRSF $\mu_q$ (the tangent-space origin) |
| `mean_srsf_norm` | `float` | Norm of the mean SRSF |
| `srsf_norms` | `ndarray (n,)` | SRSF norm of each curve |
| `initial_values` | `ndarray (n,)` | Recovered $f_i(0)$ (SRSF drops the offset) |
| `gammas` | `ndarray (n, m)` | Optimal warps to the mean |
| `converged` | `bool` | Whether the Karcher mean converged |

To select the tangent-space mapping explicitly, use the method variant:

```python
from fdars.alignment import tsrvf_transform_with_method

res = tsrvf_transform_with_method(data, t, method="log_map")   # or a shooting method
V = res["tangent_vectors"]     # same keys as tsrvf_transform
```

---

## Linear statistics in the tangent space

The point of the TSRVF is that the transported vectors behave like ordinary data. Their sample covariance has interpretable eigenvectors, and an SVD of the stacked tangent vectors yields **elastic principal components** -- a linear PCA that nonetheless respects the warping geometry, because it operates *after* transport.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import tsrvf_transform

rng = np.random.default_rng(11)
n, m = 24, 120
t = np.linspace(0, 1, m)
base = np.sin(2 * np.pi * t) + 0.5 * np.sin(4 * np.pi * t)
data = np.zeros((n, m))
for i in range(n):
    warp = t ** rng.uniform(0.6, 1.6)
    warp = (warp - warp.min()) / np.ptp(warp)
    data[i] = (1.0 + 0.2 * rng.standard_normal()) * np.interp(t, warp, base)

res = tsrvf_transform(data, t, max_iter=20, tol=1e-4)
V = np.asarray(res["tangent_vectors"])
mu_q = np.asarray(res["mean_srsf"])

# Linear PCA on the transported tangent vectors
Vc = V - V.mean(0)
U, S, Wt = np.linalg.svd(Vc, full_matrices=False)
var_ratio = S**2 / np.sum(S**2)
pc1, pc2 = Wt[0], Wt[1]

f, (a1, a2) = fig(ncols=2, figsize=(9.5, 4.0))
a1.plot(t, mu_q, color="#e8710a", lw=2.2, label="$\\mu_q$")
a1.plot(t, pc1, color="#3f51b5", lw=1.8, label="PC1")
a1.plot(t, pc2, color="#198754", lw=1.8, label="PC2")
a1.set(title="Elastic PCs (tangent space)", xlabel="t", ylabel="component")
a1.legend(fontsize=8)

scores = Vc @ np.vstack([pc1, pc2]).T
a2.scatter(scores[:, 0], scores[:, 1], color="#6f42c1", s=28, alpha=0.8)
a2.set(title=f"Scores (PC1 {var_ratio[0]*100:.0f}%, PC2 {var_ratio[1]*100:.0f}%)",
       xlabel="PC1 score", ylabel="PC2 score")
print(render(f))
```

The scores are ordinary coordinates: cluster them, regress a response on them, or feed them to a Gaussian model. Because they were computed after transport to $T_{\mu_q}$, distances between scores approximate elastic distances between the original curves.

!!! info "Relationship to elastic FPCA"
    `tsrvf_transform` supplies the transported representation that vertical (amplitude) FPCA operates on. If you want ready-made eigenfunctions and cumulative-variance summaries, use [`vert_fpca`](shape-analysis.md#elastic-fpca); use the raw tangent vectors here when you need full control over the downstream linear model.

!!! tip "Why transport at all?"
    Averaging SRVFs without alignment reintroduces phase blur. Transport to a *common* base point is what makes the tangent vectors comparable -- it is the step that turns a curved problem into a flat one.

See also [Elastic Alignment](elastic-alignment.md) for the underlying SRSF machinery and Karcher mean, and [Shape Analysis](shape-analysis.md) for the amplitude/phase decomposition built on this representation.
