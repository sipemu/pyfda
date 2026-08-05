# Advanced Elastic Alignment

The baseline [`karcher_mean`](elastic-alignment.md#group-alignment-karcher-mean) and [`elastic_align_pair`](elastic-alignment.md#pairwise-alignment) cover the common case: a smooth warp minimizing the elastic distance with a single smoothness knob, `lambda_`. Real problems ask for more -- robust estimation under outliers, uncertainty quantification, specialized geometries (closed curves, partial matches), cross-population transfer, generative models, and automatic regularization selection. `fdars` provides a family of advanced aligners for exactly these cases. Every one operates on the elastic manifold through the SRSF representation $q(t)=\operatorname{sign}(\dot f(t))\sqrt{|\dot f(t)|}$, which turns the Fisher-Rao metric into the $L^2$ metric on the Hilbert sphere.

We build a working sample once and reuse it throughout.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import karcher_mean, karcher_median, robust_karcher_mean

rng = np.random.default_rng(42)
n, m = 30, 160
t = np.linspace(0, 1, m)

# Amplitude + phase variability, plus two gross outliers
data = np.zeros((n, m))
for i in range(n):
    amp = rng.normal(3.0, 0.5)
    shift = rng.normal(0.5, 0.08)
    data[i] = amp * np.exp(-((t - shift) ** 2) / (2 * 0.12 ** 2))
data[0] += 2.0 * np.exp(-((t - 0.2) ** 2) / 0.002)   # spurious early spike
data[1] *= -0.6                                        # flipped, depressed

mean = np.asarray(karcher_mean(data, t, max_iter=15)["mean"])
median = np.asarray(karcher_median(data, t, max_iter=15)["mean"])
trimmed = np.asarray(robust_karcher_mean(data, t, trim_fraction=0.1, max_iter=15)["mean"])

f, ax = fig()
ax.plot(t, data.T, color="#adb5bd", lw=0.7, alpha=0.4)
ax.plot(t, mean, color="#dc3545", lw=2.2, label="Karcher mean")
ax.plot(t, median, color="#3f51b5", lw=2.2, label="Karcher median")
ax.plot(t, trimmed, color="#198754", lw=2.2, ls="--", label="trimmed mean (10%)")
ax.set(title="Robust vs. standard elastic central shape",
       xlabel="t", ylabel="f(t)")
ax.legend(fontsize=9)
print(render(f))
```

The two outliers pull the plain Karcher mean off the true bump; the median and trimmed mean resist them. The rest of this page walks through the advanced tools, grouped as the R reference organizes them.

---

## 1. Robust central shape: median and trimmed mean

The standard Karcher mean minimizes the *sum of squared* elastic distances and is therefore sensitive to outliers. Two robust alternatives:

- **Karcher median** minimizes the sum of *unsquared* distances via a Weiszfeld iteration on the manifold -- the functional analog of the geometric median.
- **Trimmed Karcher mean** discards the `trim_fraction` most distant curves before averaging.

$$
\tilde\mu = \arg\min_{\mu}\sum_{i=1}^n d_e(\mu, f_i)
\qquad\text{vs.}\qquad
\mu^\* = \arg\min_{\mu}\sum_{i=1}^n d_e(\mu, f_i)^2.
$$

```python
from fdars.alignment import karcher_median, robust_karcher_mean

kmed = karcher_median(data, t, max_iter=15)              # robust to outliers
ktrim = robust_karcher_mean(data, t, trim_fraction=0.1)  # drop 10% most distant

mu_median = kmed["mean"]      # elastic median
weights   = kmed["weights"]   # iteratively reweighted per-curve weight
mu_trim   = ktrim["mean"]
kept      = ktrim["weights"]  # 0 for trimmed curves
```

Both return the same keys as `karcher_mean` plus `weights`. See [Elastic Alignment](elastic-alignment.md#karcher-median-robust-central-shape) for the baseline discussion.

---

## 2. Elastic depth (phase-aware centrality)

Ordinary functional depth ignores phase: two curves can look equally "central" even though one is a time-warped copy of the other. **Elastic depth** measures centrality under the elastic metric and decomposes into amplitude and phase parts, so you can spot a curve that is central in shape but outlying in timing.

```python
from fdars.alignment import elastic_depth

ed = elastic_depth(data, t, lambda_=0.0)
amp_depth  = ed["amplitude_depth"]   # (n,)
ph_depth   = ed["phase_depth"]       # (n,)
comb_depth = ed["combined_depth"]    # (n,)
deepest = int(np.argmax(comb_depth))
print(f"Deepest (most central) curve: {deepest}")
```

Elastic depth is covered in detail, with figures, on the [Shape Analysis](shape-analysis.md#elastic-depth) page.

---

## 3. Outlier detection (amplitude vs. phase)

`elastic_outlier_detection` flags curves whose elastic distance to a robust reference exceeds a Tukey-style fence, and returns the amplitude and phase distance matrices so you can classify each outlier by *type* -- unusual shape, unusual timing, or both.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import elastic_outlier_detection

rng = np.random.default_rng(7)
n, m = 28, 120
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.5) ** 2) / (2 * 0.12 ** 2))
data = np.array([rng.normal(1, 0.05) * np.interp(
    t, np.clip(t + rng.normal(0, 0.03), 0, 1), base) for _ in range(n)])
data[3] *= 1.8                       # amplitude outlier
data[7] = np.interp(t, np.clip(t - 0.18, 0, 1), base)  # phase outlier

out = elastic_outlier_detection(data, t, alpha=0.05, use_median=True)
idx = list(np.asarray(out["outlier_indices"], dtype=int))
dist = np.asarray(out["distances"])
thr = float(out["threshold"])

f, ax = fig()
mask = np.zeros(n, bool); mask[idx] = True
ax.plot(t, data[~mask].T, color="#adb5bd", lw=0.8, alpha=0.5)
for i in idx:
    ax.plot(t, data[i], color="#dc3545", lw=2.0, label=f"outlier {i}")
ax.set(title=f"Elastic outliers (threshold d={thr:.3f})",
       xlabel="t", ylabel="f(t)")
ax.legend(fontsize=8)
print(render(f))

print("outlier indices:", idx)
```

| Key | Description |
|-----|-------------|
| `outlier_indices` | Indices flagged as outliers |
| `distances` | Elastic distance of each curve to the reference, shape `(n,)` |
| `threshold` | Tukey fence used |
| `amplitude_distances` / `phase_distances` | Pairwise decomposed distances, shape `(n, n)` |

---

## 4. Shape confidence intervals

After computing the Karcher mean, how certain is its shape? `shape_confidence_interval` gives a bootstrap band: resample the curves, recompute the Karcher mean of each resample, **align** the bootstrap means to the original mean, and take pointwise percentiles. The alignment step is essential -- without it, phase variability between bootstrap means inflates the band.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import shape_confidence_interval

rng = np.random.default_rng(3)
n, m = 25, 120
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.5) ** 2) / (2 * 0.12 ** 2))
data = np.array([rng.normal(3, 0.4) * np.interp(
    t, np.clip(t + rng.normal(0, 0.06), 0, 1), base) for _ in range(n)])

ci = shape_confidence_interval(data, t, n_bootstrap=60, confidence_level=0.95,
                               max_iter=10)
mu = np.asarray(ci["mean"])
lo = np.asarray(ci["lower_band"])
hi = np.asarray(ci["upper_band"])

f, ax = fig()
ax.fill_between(t, lo, hi, color="#3f51b5", alpha=0.18, label="95% band")
ax.plot(t, mu, color="#3f51b5", lw=2.2, label="Karcher mean")
ax.set(title="Bootstrap shape confidence interval",
       xlabel="t", ylabel="f(t)")
ax.legend(fontsize=9)
print(render(f))
```

| Key | Description |
|-----|-------------|
| `mean` | The Karcher mean the band is centered on |
| `lower_band` / `upper_band` | Pointwise percentile bands, shape `(m,)` |
| `bootstrap_means` | All bootstrap Karcher means, shape `(n_bootstrap, m)` |

---

## 5. Bayesian pairwise alignment

Dynamic-programming alignment gives a *point* estimate of the warp. `bayesian_align_pair` returns a *posterior* over warping functions via a Metropolis MCMC sampler on the Hilbert sphere, yielding credible bands and an acceptance rate for diagnostics.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import bayesian_align_pair

t = np.linspace(0, 1, 120)
base = np.exp(-((t - 0.5) ** 2) / (2 * 0.10 ** 2))
f1 = base
f2 = np.interp(t, np.clip(t + 0.08, 0, 1), base)   # phase-shifted target

ba = bayesian_align_pair(f1, f2, t, n_samples=500, burn_in=100, seed=0)
f2_aligned = np.asarray(ba["f_aligned_mean"])
gam_lo = np.asarray(ba["credible_lower"])
gam_hi = np.asarray(ba["credible_upper"])
gam_mean = np.asarray(ba["posterior_mean_gamma"])

f, (a1, a2) = fig(ncols=2, figsize=(9.5, 4.0))
a1.plot(t, f1, color="#6c757d", lw=2, label="f1 (reference)")
a1.plot(t, f2, color="#dc3545", lw=1.6, ls="--", label="f2 (original)")
a1.plot(t, f2_aligned, color="#3f51b5", lw=2, label="f2 (aligned)")
a1.set(title=f"Bayesian alignment (accept. {float(ba['acceptance_rate']):.2f})",
       xlabel="t", ylabel="f(t)")
a1.legend(fontsize=8)

a2.fill_between(t, gam_lo, gam_hi, color="#6f42c1", alpha=0.2, label="95% credible")
a2.plot(t, gam_mean, color="#6f42c1", lw=2, label="posterior mean $\\gamma$")
a2.plot([0, 1], [0, 1], color="#6c757d", ls="--", lw=1.2)
a2.set(title="Posterior over the warp", xlabel="t",
       ylabel="$\\gamma(t)$", aspect="equal")
a2.legend(fontsize=8)
print(render(f))
```

| Key | Description |
|-----|-------------|
| `posterior_gammas` | MCMC draws of the warp, shape `(n_samples, m)` |
| `posterior_mean_gamma` | Posterior mean warp |
| `credible_lower` / `credible_upper` | Pointwise credible band on the warp |
| `acceptance_rate` | MCMC acceptance rate (aim for ~0.2--0.8) |
| `f_aligned_mean` | `f2` aligned under the posterior-mean warp |

!!! tip "Tuning the sampler"
    If the acceptance rate is too low, reduce `step_size`; if too high, raise it. Increase `n_samples`/`burn_in` for smoother credible bands.

---

## 6. Multiresolution alignment (long curves)

Dynamic programming is $O(m^2)$ per pair, slow for long grids. `elastic_align_pair_multires` aligns a coarsened copy first, then refines on the full grid -- faster and more robust to local minima on long, oscillatory curves.

```python
from fdars.alignment import elastic_align_pair_multires

res = elastic_align_pair_multires(
    f2, f1, t,
    coarsen_factor=4,    # downsample by 4x for the coarse solve
    n_refine_steps=10,   # gradient refinement steps
    step_size=0.01,
    lambda_=0.0,
)
gamma = res["gamma"]; distance = res["distance"]
```

| Parameter | Description |
|-----------|-------------|
| `coarsen_factor` | Grid downsampling factor for the coarse solve (default `4`) |
| `n_refine_steps` | Gradient refinement steps (default `10`) |
| `step_size` | Refinement step size (default `0.01`) |

Returns `f_aligned`, `gamma`, `distance`. The coarse-to-fine result is an approximation of the exact DP solution: it trades a little fidelity for speed, so on short curves prefer the exact `elastic_align_pair`.

---

## 7. Closed and periodic curve alignment

A closed curve has no canonical starting point: the same shape can be parameterized from any point on its boundary. `elastic_align_pair_closed` optimizes over a cyclic start-point rotation $\theta$ in addition to the warp,

$$
d(f_1, f_2) = \min_{\gamma,\theta}\big\lVert q_1 - (q_2\circ R_\theta\circ\gamma)\sqrt{\dot\gamma}\big\rVert_{L^2},
$$

using a coarse-to-fine search over rotations.

```python
from fdars.alignment import elastic_align_pair_closed

c1 = np.sin(2 * np.pi * t) + 0.3 * np.sin(4 * np.pi * t)
c2 = np.sin(2 * np.pi * (t - 0.1)) + 0.4 * np.sin(4 * np.pi * (t - 0.1))

res = elastic_align_pair_closed(c1, c2, t, lambda_=0.0)
rotation = res["optimal_rotation"]   # best cyclic start-point offset
gamma    = res["gamma"]
distance = res["distance"]
```

Returns the usual `f_aligned`, `gamma`, `distance`, plus `optimal_rotation`.

!!! note "No group `periodic=True` mode"
    The R package also exposes a `periodic=True` circular-rotation mode inside `karcher_mean`/`elastic.align`. The Python bindings provide the *pairwise* closed aligner shown here but no group periodic mode. For a full periodic Karcher mean, pre-rotate each curve (e.g. so its global maximum sits at a fixed grid position) and then call the ordinary `karcher_mean`.

---

## 8. Partial matching (subsequence search)

When only a *portion* of a longer target matches a shorter query, full alignment is wrong. `elastic_partial_match` finds the best-aligned sub-interval of the target.

```python
from fdars.alignment import elastic_partial_match

template = data[0][:60]     # a short query
target   = data[1]          # a longer curve to search

pm = elastic_partial_match(template, target, t[:60], t, min_span=0.2)
print(f"Match: index {pm['start_index']}..{pm['end_index']} "
      f"({pm['domain_fraction']:.1%} of the target), d={pm['distance']:.4f}")
```

| Key | Description |
|-----|-------------|
| `start_index` / `end_index` | Best-matching sub-interval of the target |
| `domain_fraction` | Fraction of the target domain that matched |
| `gamma` | Warp on the matched segment |
| `distance` | Elastic distance of the match |

`min_span` sets the smallest fraction of the target the match may cover, guarding against trivial tiny matches.

---

## 9. Transfer alignment across populations

When curves come from two populations (healthy vs. diseased, two sites), the population-level shape difference confounds within-subject warping. `transfer_alignment` maps target curves into the source population's coordinate frame through a bridging warp: align the two Karcher means to get $\gamma_B$, then compose each target's within-population warp with $\gamma_B$.

```python
from fdars.alignment import transfer_alignment

source = data[:15]
target = data[15:]

tr = transfer_alignment(source, target, t, max_iter=10)
aligned  = tr["aligned_data"]    # target curves in the source frame
bridging = tr["bridging_gamma"]  # source<-target bridge warp
print(f"Aligned {np.asarray(aligned).shape[0]} target curves to the source frame")
```

| Key | Description |
|-----|-------------|
| `source_mean` | Karcher mean of the source population |
| `aligned_data` | Target curves placed in the source frame |
| `gammas` | Per-curve composed warps $\gamma_B\circ\gamma_i^T$ |
| `bridging_gamma` | The bridge warp aligning target mean to source mean |
| `distances` | Elastic distances after transfer |

---

## 10. Geodesic interpolation between curves

A **geodesic** on the elastic manifold is the shortest path between two shapes -- a natural morph that blends amplitude (in SRSF space) and phase (on the diffeomorphism group). `curve_geodesic` returns intermediate curves at parameters $\alpha\in[0,1]$.

```python exec="1" html="1" source="above"
import numpy as np
import matplotlib.cm as cm
from docs_fig import fig, render
from fdars.alignment import curve_geodesic

t = np.linspace(0, 1, 140)
f1 = np.exp(-((t - 0.35) ** 2) / 0.01)
f2 = 0.8 * np.exp(-((t - 0.7) ** 2) / 0.006) + 0.4 * np.exp(-((t - 0.3) ** 2) / 0.01)

geo = curve_geodesic(f1, f2, t, n_points=9)
curves = np.asarray(geo["curves"])
alphas = np.asarray(geo["parameter_values"])

f, ax = fig()
for c, a in zip(curves, alphas):
    ax.plot(t, c, color=cm.viridis(a), lw=1.4)
ax.plot(t, f1, color="#3f51b5", lw=2.4, label="$f_1$ ($\\alpha$=0)")
ax.plot(t, f2, color="#dc3545", lw=2.4, label="$f_2$ ($\\alpha$=1)")
ax.set(title="Elastic geodesic: smooth morph $f_1 \\to f_2$",
       xlabel="t", ylabel="f(t)")
ax.legend(fontsize=9)
print(render(f))
```

| Key | Description |
|-----|-------------|
| `curves` | Interpolated curves, shape `(n_points, m)` |
| `warps` | The intermediate warps |
| `distances` | Cumulative elastic distance along the path |
| `parameter_values` | The $\alpha\in[0,1]$ for each curve |

---

## 11. Gaussian generative model

After separating amplitude and phase, you can *generate* new curves by sampling from the estimated score distributions -- useful for augmentation and simulation. `gauss_model` fits Gaussians to the vertical (amplitude) and horizontal (phase) FPC scores and draws new samples; `joint_gauss_model` fits a joint Gaussian that preserves amplitude-phase correlation.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import gauss_model

rng = np.random.default_rng(1)
n, m = 30, 120
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.5) ** 2) / (2 * 0.12 ** 2))
data = np.array([rng.normal(3, 0.4) * np.interp(
    t, np.clip(t + rng.normal(0, 0.06), 0, 1), base) for _ in range(n)])

gm = gauss_model(data, t, ncomp=3, n_samples=20, max_iter=15, seed=0)
synth = np.asarray(gm["samples"])

f, ax = fig()
ax.plot(t, data.T, color="#3f51b5", lw=0.8, alpha=0.35)
ax.plot(t, synth.T, color="#e8710a", lw=0.8, alpha=0.5)
ax.plot([], [], color="#3f51b5", lw=2, label="original")
ax.plot([], [], color="#e8710a", lw=2, label="generated")
ax.set(title="Gaussian generative model: original vs. synthetic",
       xlabel="t", ylabel="f(t)")
ax.legend(fontsize=9)
print(render(f))
```

| Key | Description |
|-----|-------------|
| `samples` | Synthetic curves, shape `(n_samples, m)` |
| `warps` | Warps applied to the synthetic amplitudes |
| `scores` | Sampled FPC scores |

---

## 12. Peak persistence for automatic $\lambda$

Choosing the regularization $\lambda$ is usually ad hoc. **Peak persistence** offers a topological criterion: sweep $\lambda$, track when peaks in the Karcher mean are born and die, and pick the $\lambda$ where persistent (genuine) peaks survive but transient (noise) peaks have merged away.

```python
from fdars.alignment import peak_persistence

lambdas = np.linspace(0.0, 3.0, 15)   # must be an ndarray
pers = peak_persistence(data, t, lambdas=lambdas, max_iter=8)
print(f"Optimal lambda: {float(pers['optimal_lambda']):.3f}")
print(f"Peak counts:    {list(np.asarray(pers['peak_counts'], dtype=int))}")
```

| Key | Description |
|-----|-------------|
| `lambdas` | The swept grid |
| `peak_counts` | Number of Karcher-mean peaks at each $\lambda$ |
| `optimal_lambda` / `optimal_index` | Selected regularization and its grid index |

Cross-validation (next section) optimizes a reconstruction score; peak persistence optimizes topological stability. They answer slightly different questions -- use CV when you have a clear predictive target, persistence when you care about recovering the right *number of features*.

---

## 13. Choosing $\lambda$ by cross-validation

`lambda_cv` scores a grid of regularization values by $K$-fold cross-validation over the whole dataset and reports the best one.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import lambda_cv

rng = np.random.default_rng(7)
n, m = 20, 100
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.01) + 0.6 * np.exp(-((t - 0.7) ** 2) / 0.008)
data = np.zeros((n, m))
for i in range(n):
    warp = t ** rng.uniform(0.7, 1.5)
    warp = (warp - warp.min()) / np.ptp(warp)
    data[i] = np.interp(t, warp, base)

lambdas = np.array([0.0, 0.001, 0.01, 0.05, 0.1, 0.5])   # must be an ndarray
cv = lambda_cv(data, t, lambdas=lambdas, n_folds=3, max_iter=10, tol=1e-3)

best = float(cv["best_lambda"])
f, ax = fig()
ax.plot(cv["lambdas"], cv["cv_scores"], "o-", color="#3f51b5", lw=1.8)
ax.axvline(best, color="#e8710a", ls="--", lw=1.5, label=f"best $\\lambda$={best:g}")
ax.set(title="Cross-validated warp regularization", xlabel="$\\lambda$",
       ylabel="CV score (lower is better)")
ax.legend(fontsize=9)
print(render(f))
```

| Key | Description |
|-----|-------------|
| `best_lambda` | Regularization minimizing the CV score |
| `cv_scores` | Mean CV score for each candidate |
| `lambdas` | The candidate grid that was scored |

!!! warning "Array arguments must be `ndarray`"
    `lambda_cv`, `peak_persistence`, and `elastic_align_pair_constrained` reject plain Python lists for their array arguments (`lambdas`, `landmark_targets`, `landmark_sources`) with a `TypeError`. Wrap them with `np.array(...)`.

---

## Pairwise variants and their penalties

Beyond the specialized aligners above, `fdars` exposes the pairwise objective's regularization *directly*. Every pairwise aligner minimizes an elastic objective in SRSF space,

$$
\gamma^\* = \arg\min_{\gamma}\;\big\lVert q_1 - (q_2\circ\gamma)\sqrt{\dot\gamma}\big\rVert_{L^2}^2 \;+\; \lambda\,\mathcal{P}(\gamma),
$$

and the variants differ in the roughness penalty $\mathcal{P}$ and the constraints on $\gamma$. The figure shows how $\lambda$ moves the estimated warp between an unconstrained fit and the identity.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import elastic_align_pair_penalized

t = np.linspace(0, 1, 120)
base = np.exp(-((t - 0.4) ** 2) / 0.01) + 0.7 * np.exp(-((t - 0.75) ** 2) / 0.006)
warp = t ** 1.5
warp = (warp - warp.min()) / np.ptp(warp)
target = base
source = np.interp(t, warp, base)

f, ax = fig()
colors = {"0.0": "#dc3545", "0.05": "#e8710a", "0.5": "#198754", "5.0": "#6f42c1"}
labels = {"0.0": "under (λ=0)", "0.05": "well (λ=0.05)",
          "0.5": "strong (λ=0.5)", "5.0": "over (λ=5)"}
for lam_s, c in colors.items():
    res = elastic_align_pair_penalized(source, target, t, lambda_=float(lam_s))
    ax.plot(t, np.asarray(res["gamma"]), color=c, lw=1.8, label=labels[lam_s])
ax.plot([0, 1], [0, 1], color="#6c757d", lw=1.3, ls="--", label="identity")
ax.set(title="Warp $\\gamma$ vs. penalty $\\lambda$", xlabel="t",
       ylabel="$\\gamma(t)$", aspect="equal")
ax.legend(fontsize=8)
print(render(f))
```

As $\lambda$ grows the warp is pulled toward the diagonal: too small and it over-fits noise, too large and it collapses to the identity (no alignment).

### Penalized

Choose the penalty functional. `first_order` penalizes the warp's departure from the identity in slope; `second_order` penalizes curvature (favoring smoother, gently bending warps); `second_order_weight` blends the two.

```python
from fdars.alignment import elastic_align_pair_penalized

res = elastic_align_pair_penalized(
    f2, f1, t, lambda_=0.1,
    penalty_type="second_order",   # or "first_order" (default)
    second_order_weight=0.1,
)
gamma = res["gamma"]
```

### Landmark-constrained

When you already know that specific features correspond (a shared peak), pin them. The warp is forced through the given `(source, target)` landmark pairs and optimized elastically between them.

```python
from fdars.alignment import elastic_align_pair_constrained

# landmark arrays MUST be ndarrays (a Python list raises TypeError)
src = np.array([0.55])   # landmark location in f2
tgt = np.array([0.50])   # where it should map to in f1

res = elastic_align_pair_constrained(f1, f2, t, tgt, src, lambda_=0.0)
gamma = res["gamma"]     # satisfies gamma(tgt) = src at the knots
```

| Parameter | Description |
|-----------|-------------|
| `landmark_targets` | Target landmark locations (must be `ndarray`) |
| `landmark_sources` | Source landmark locations (must be `ndarray`) |
| `lambda_` | Warp regularization |

!!! note "For pure landmark warping"
    `elastic_align_pair_constrained` pins landmarks within an *elastic* fit. For a pure monotone landmark warp with no elastic optimization, see [Landmark Registration](landmark-registration.md).

All pairwise variants return at least `f_aligned`, `gamma`, and `distance`; `closed` adds `optimal_rotation`.

---

## Binding gaps vs. the R reference

Two R advanced features have **no** Python binding and are omitted here rather than faked:

- **Multivariate (vector-valued) alignment** -- `karcher.mean.nd` / `pca.nd`. Even in R these are noted as "wrappers pending"; the `fdars` Python surface is scalar-curve only.
- **Group periodic mode** -- `periodic=True` inside `karcher_mean`. The pairwise [closed aligner](#7-closed-and-periodic-curve-alignment) is available; the group periodic Karcher mean is not (workaround noted there).

Horizontal FPNS (`horiz_fpns`) *is* bound and is covered on the [Shape Analysis](shape-analysis.md) page alongside horizontal FPCA.

---

See [Elastic Alignment](elastic-alignment.md) for the baseline aligner and the SRSF/Karcher-mean machinery, [TSRVF](tsrvf.md) for linearized statistics, [Shape Analysis](shape-analysis.md) for elastic FPCA and depth, and [Comparing Alignment Methods](alignment-comparison.md) for how these fits stack up against landmark registration.

## References

- Fletcher, P.T., Venkatasubramanian, S., Joshi, S. (2009). *The geometric median on Riemannian manifolds.* NeuroImage 45(1):S143-S152.
- Cheng, W., Dryden, I.L., Huang, X. (2016). *Bayesian registration of functions and curves.* Bayesian Analysis 11(2):447-481.
- Tucker, J.D., Wu, W., Srivastava, A. (2013). *Generative models for functional data using phase and amplitude separation.* Computational Statistics & Data Analysis 61:50-66.
- Srivastava, A., Klassen, E. (2016). *Functional and Shape Data Analysis.* Springer.
