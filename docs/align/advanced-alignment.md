# Advanced Elastic Alignment

The baseline [`karcher_mean`](elastic-alignment.md#group-alignment-karcher-mean) and [`elastic_align_pair`](elastic-alignment.md#pairwise-alignment) cover the common case: curves on one interval, aligned by a warp that minimises the elastic (Fisher–Rao) distance. This page collects the variants for special situations: **closed or periodic** curves, a short curve that matches only **part** of a longer one, **multiresolution** alignment, alignment **across two populations**, **geodesic** paths between curves, **generative** models built on the amplitude/phase split, and **automatic choice of $\lambda$**. It also keeps, for now, elastic depth, outlier detection, shape confidence intervals and Bayesian pairwise alignment. Every tool works on the SRSF $q(t)=\operatorname{sign}(\dot f(t))\sqrt{|\dot f(t)|}$, under which the Fisher–Rao metric becomes the $L^2$ metric.

![Advanced Elastic Alignment — concept diagram](../assets/diagrams/advanced-alignment.svg){ .fdars-diagram }

Robust centres (the Karcher median and the trimmed Karcher mean) now live on the [Elastic Alignment](elastic-alignment.md#robust-centres-karcher-median-and-trimmed-mean) page; warp optimisers, penalties and the band on [Elastic Optimisers & Penalties](elastic-optimisers.md). For which aligner to use in the first place, see [Choosing an Alignment Method](choosing-a-method.md).

The non-executed snippets below refer to this simulated sample:

```python
import numpy as np

rng = np.random.default_rng(42)
n, m = 30, 160
t = np.linspace(0, 1, m)
data = np.zeros((n, m))
for i in range(n):
    data[i] = rng.normal(3.0, 0.5) * np.exp(-((t - rng.normal(0.5, 0.08)) ** 2) / (2 * 0.12 ** 2))
```

---

## 1. Elastic depth (phase-aware centrality)

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

## 2. Outlier detection (amplitude vs. phase)

`elastic_outlier_detection` returns, for every curve, its **amplitude distance** (how unusual its *shape* is) and its **phase distance** (how unusual its *timing* is) relative to a robust reference. Classifying by type means fencing each of these separately -- a plain elastic-distance fence alone will not do it.

!!! warning "The elastic distance is phase-invariant"
    `out["distances"]` (and the default `out["outlier_indices"]`) measure the **amplitude** distance, which is invariant to time-warping. A curve that is only *shifted in time* has a near-zero amplitude distance, so it slips through that fence. To catch timing outliers you must look at `out["phase_distances"]`. Below we inject one amplitude outlier (curve 3, an enlarged bump) and one phase outlier (curve 7, a time-shifted copy) and recover **both** from the amplitude-vs-phase plane.

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
data[3] *= 1.8                                         # amplitude (shape) outlier
data[7] = np.interp(t, np.clip(t - 0.18, 0, 1), base)  # phase (timing) outlier

out = elastic_outlier_detection(data, t, alpha=0.05, use_median=True)
amp = np.asarray(out["amplitude_distances"])   # (n,) shape distance to the reference
pha = np.asarray(out["phase_distances"])       # (n,) timing distance to the reference

def fence(x):                                  # Tukey upper fence (2.0·IQR)
    q1, q3 = np.percentile(x, [25, 75]); return q3 + 2.0 * (q3 - q1)
fa, fp = fence(amp), fence(pha)
amp_out = np.where(amp > fa)[0]                 # unusual shape
pha_out = np.where(pha > fp)[0]                 # unusual timing

f, ax = fig()
ax.scatter(amp, pha, s=26, color="#adb5bd", zorder=2)
ax.axvline(fa, color="#3f51b5", ls="--", lw=1, label="amplitude fence")
ax.axhline(fp, color="#e8710a", ls="--", lw=1, label="phase fence")
for i in amp_out:
    ax.scatter(amp[i], pha[i], s=70, color="#3f51b5", zorder=3)
    ax.annotate(f"{i} · shape", (amp[i], pha[i]), (6, 4),
                textcoords="offset points", fontsize=8, color="#3f51b5")
for i in pha_out:
    ax.scatter(amp[i], pha[i], s=70, color="#e8710a", zorder=3)
    ax.annotate(f"{i} · timing", (amp[i], pha[i]), (6, -11),
                textcoords="offset points", fontsize=8, color="#e8710a")
ax.set(title="Outlier type: amplitude (shape) vs phase (timing)",
       xlabel="amplitude distance", ylabel="phase distance")
ax.legend(fontsize=8)
print(render(f))

print("shape (amplitude) outliers:", list(amp_out),
      " | timing (phase) outliers:", list(pha_out))
```

Curve 3 lands far to the right (large amplitude distance -> a **shape** outlier) while curve 7 lands high up (large phase distance -> a **timing** outlier). Neither fence alone finds both; the amplitude-vs-phase plane separates them cleanly.

| Key | Description |
|-----|-------------|
| `outlier_indices` | Curves past the **amplitude** fence (shape outliers only) |
| `distances` | Amplitude (elastic) distance of each curve to the reference, shape `(n,)` |
| `threshold` | Tukey fence on `distances` |
| `amplitude_distances` / `phase_distances` | Per-curve shape / timing distance to the reference, each shape `(n,)` |

---

## 3. Shape confidence intervals

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

The shaded band is the pointwise 95% bootstrap envelope around the Karcher mean: where it is narrow the mean shape is well determined, and where it fans out the sample disagrees about amplitude. Because the resampling happens *after* alignment, the band reflects shape uncertainty rather than leftover phase spread.

| Key | Description |
|-----|-------------|
| `mean` | The Karcher mean the band is centered on |
| `lower_band` / `upper_band` | Pointwise percentile bands, shape `(m,)` |
| `bootstrap_means` | All bootstrap Karcher means, shape `(n_bootstrap, m)` |

---

## 4. Bayesian pairwise alignment

Dynamic-programming alignment gives a *point* estimate of the warp. `bayesian_align_pair` returns a *posterior* over warping functions from a preconditioned Crank–Nicolson (pCN) sampler on the tangent space of the $\psi=\sqrt{\dot\gamma}$ sphere, with credible bands and an acceptance rate for diagnostics.

!!! note "Limits of the pairwise sampler"
    The noise variance is fixed at 1, so the band width depends on the scale of the data (rescale the curves and the band changes). It runs a single chain with no convergence diagnostics. For calibrated group-level uncertainty use `bayesian_align_group`, which samples the noise variance, runs several chains and reports $\hat R$ and ESS.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import bayesian_align_pair

t = np.linspace(0, 1, 120)
base = np.exp(-((t - 0.5) ** 2) / (2 * 0.10 ** 2))
f1 = base
f2 = np.interp(t, np.clip(t + 0.08, 0, 1), base)   # phase-shifted target

ba = bayesian_align_pair(f1, f2, t, n_samples=500, burn_in=100, seed=0, step_size=0.85)
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

The left panel shows the aligned `f2` tracking the reference, while the right panel replaces the single point-estimate warp with a full posterior: the purple band is the 95% credible region around the posterior-mean $\gamma$. Where the band hugs the diagonal the timing is confidently identity; where it widens the data are ambiguous about how much to warp -- uncertainty a point estimate simply cannot express.

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

## 5. Multiresolution alignment (long curves)

Dynamic programming costs $O(m^2)$ per pair. `elastic_align_pair_multires` runs the DP on a grid coarsened by `coarsen_factor`, upsamples the warp, and then takes `n_refine_steps` gradient steps on the full grid.

!!! warning "Gradient refinement is under review"
    In fdars-core 0.48 the refinement steps can make the alignment *worse* rather than better, and they ignore `lambda_`. On a 400-point oscillatory pair the coarse DP alone (`n_refine_steps=0`) reaches an elastic distance of 0.20, the default 10 refinement steps raise it to 1.56, and exact DP gives 0.10. Until this is resolved, use `n_refine_steps=0` (a pure coarse-to-fine DP) and compare against `elastic_align_pair`, or use [RBFGS](elastic-optimisers.md#rbfgs-a-smooth-local-optimiser) or a [band](banded-alignment.md) for long curves.

```python exec="1" source="above" result="text"
import numpy as np
from time import perf_counter
from fdars.alignment import elastic_align_pair_multires, elastic_align_pair

m = 400
t = np.linspace(0, 1, m)
f1 = np.sin(2 * np.pi * 2 * t) + 0.5 * np.sin(2 * np.pi * 5 * t)
f2 = np.interp(t, np.clip(t + 0.09 * np.sin(np.pi * t), 0, 1), f1)   # non-linear phase distortion

for steps in (0, 10):
    t0 = perf_counter()
    r = elastic_align_pair_multires(f1, f2, t, coarsen_factor=4, n_refine_steps=steps)
    rms = np.sqrt(np.mean((np.asarray(r["f_aligned"]) - f1) ** 2))
    print(f"multires, n_refine_steps={steps:2d}: distance {r['distance']:.3f}  RMS {rms:.4f}  {1e3 * (perf_counter() - t0):5.1f} ms")
t0 = perf_counter()
r = elastic_align_pair(f1, f2, t)
rms = np.sqrt(np.mean((np.asarray(r["f_aligned"]) - f1) ** 2))
print(f"exact DP:                     distance {r['distance']:.3f}  RMS {rms:.4f}  {1e3 * (perf_counter() - t0):5.1f} ms")
print("FDARS_FENCE_OK")
```

The coarse DP is more than ten times faster than the exact DP at about twice its distance; the refinement steps then make the result worse. Returns `f_aligned`, `gamma` and `distance`.

| Parameter | Description |
|-----------|-------------|
| `coarsen_factor` | Grid downsampling factor for the coarse DP (default `4`) |
| `n_refine_steps` | Gradient refinement steps on the full grid (default `10`; see the warning) |
| `step_size` | Refinement step size (default `0.01`) |
| `lambda_` | Used by the coarse DP only |

---

## 6. Closed and periodic curves

A periodic signal (a gait cycle, a daily temperature cycle, a contour traced as a 1-D function) has no canonical starting point: the same cycle can start anywhere. `elastic_align_pair_closed` searches over a circular shift of the start index $\theta$ in addition to the warp,

$$
d(f_1, f_2) = \min_{\theta}\;\min_{\gamma\in\Gamma}\big\lVert q_1 - (q_2^{(\theta)}\circ\gamma)\sqrt{\dot\gamma}\big\rVert_{L^2},
$$

where $q_2^{(\theta)}$ is the SRSF of $f_2$ rotated by $\theta$ grid points. Two details matter:

- **The start-point search is heuristic**: a coarse search over shifts, then a fine search around the best one. It is not guaranteed to find the global optimum.
- **The warp is an ordinary interval warp** ($\gamma(0)=0$, $\gamma(1)=1$) applied after the rotation, not a diffeomorphism of the circle.

`karcher_mean_closed` (and `karcher_mean_closed_with_config`, which takes the [optimiser options](elastic-optimisers.md)) runs the Karcher iteration with this aligner and also returns the per-curve `rotations`.

```python exec="1" source="above" result="text"
import numpy as np
from fdars.alignment import elastic_align_pair_closed, karcher_mean_closed, karcher_mean, elastic_distance

m = 101
t = np.linspace(0, 1, m)
cycle = lambda s: np.sin(2 * np.pi * s) + 0.5 * np.cos(4 * np.pi * s)

r = elastic_align_pair_closed(cycle(t), cycle(t - 0.2), t)
print(f"pair: start shift {r['optimal_rotation']} grid points (true 20), closed distance {r['distance']:.3f}, "
      f"open distance {elastic_distance(cycle(t), cycle(t - 0.2), t):.3f}")

rng = np.random.default_rng(1)
X = np.array([rng.uniform(0.9, 1.1) * cycle(t - rng.uniform(-0.3, 0.3)) for _ in range(8)])
ratio = lambda R: np.var(R, 0).mean() / np.var(X, 0).mean()
closed = karcher_mean_closed(X, t, max_iter=10)
opened = karcher_mean(X, t, max_iter=10)
print(f"variance after/before: closed {ratio(np.asarray(closed['aligned_data'])):.3f}, "
      f"interval-only {ratio(np.asarray(opened['aligned_data'])):.3f}")
print("FDARS_FENCE_OK")
```

The closed aligner recovers the 0.2-cycle start shift exactly and removes almost all the variance; the interval aligner, which must keep $\gamma(0)=0$, cannot move features across the boundary. The start-point search costs roughly $(20 + m/10)$ ordinary alignments per pair, so the closed Karcher mean is about 40 times slower than `karcher_mean` at $m = 101$. Returns `f_aligned`, `gamma`, `distance`, `optimal_rotation` (pair) and `mean`, `aligned_data`, `gammas`, `rotations`, `n_iter`, `converged` (Karcher).

For curves in the plane (outlines), where rotation and scale are also nuisance, use the shape-space functions `curve_shape_*(closed=True)` instead.

---

## 7. Partial matching (subsequence search)

When only a *portion* of a longer target matches a shorter query, full alignment is wrong. `elastic_partial_match` finds the best-aligned sub-interval of the target. Here a short query pattern is hidden (time-warped and buried in noise) inside a longer target, and the search recovers exactly where it sits.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import elastic_partial_match

# short query pattern on its own grid
tt = np.linspace(0, 1, 80)
template = np.exp(-((tt - 0.5) ** 2) / (2 * 0.14 ** 2)) * np.sin(2 * np.pi * 2 * tt)

# longer, noisy target; the pattern is embedded (warped) on the sub-interval [0.45, 0.75]
tg = np.linspace(0, 1, 300)
rng = np.random.default_rng(0)
target = 0.15 * rng.standard_normal(300)
seg = (tg >= 0.45) & (tg <= 0.75); s = (tg[seg] - 0.45) / 0.30
target[seg] += 1.2 * np.interp(np.clip(s + 0.05 * np.sin(np.pi * s), 0, 1), tt, template)

pm = elastic_partial_match(template, target, tt, tg, min_span=0.25)
i0, i1 = pm["start_index"], pm["end_index"]

f, ax = fig()
ax.plot(tg, target, color="#adb5bd", lw=1, label="target (long)")
ax.plot(tg[i0:i1 + 1], target[i0:i1 + 1], color="#fd7e14", lw=2.4, label="matched sub-interval")
ax.axvspan(tg[i0], tg[i1], color="#fd7e14", alpha=0.10)
ax.axvspan(0.45, 0.75, color="#198754", alpha=0.06)     # true location (green)
ax.set(title=f"Query found in {pm['domain_fraction']:.0%} of the target  (d={pm['distance']:.2f})",
       xlabel="t", ylabel="f(t)")
ax.legend(fontsize=8)
print(render(f))

print(f"matched target indices {i0}..{i1}  (t = {tg[i0]:.2f}..{tg[i1]:.2f}; planted at 0.45..0.75)")
```

The orange sub-interval that the search selects overlaps the green planted region almost exactly, and the printed indices confirm it recovers the buried pattern despite the noise and time-warping. Crucially the match spans only a fraction of the target (see `domain_fraction`), which is what distinguishes partial matching from forcing a full-length alignment.

| Key | Description |
|-----|-------------|
| `start_index` / `end_index` | Best-matching sub-interval of the target |
| `domain_fraction` | Fraction of the target domain that matched |
| `gamma` | Warp on the matched segment |
| `distance` | Elastic distance of the match |

`min_span` sets the smallest fraction of the target the match may cover, guarding against trivial tiny matches. The search over windows is heuristic, and **distances of matches of different lengths are not comparable** (a shorter window has less curve to mismatch), so do not rank candidate matches across window lengths by `distance` alone.

---

## 8. Transfer alignment across populations

When curves come from two populations (two sites, two devices), `transfer_alignment` is meant to map the target curves into the source population's time frame: it computes both Karcher means, a bridging warp $\gamma_B$ that aligns the target mean to the source mean, and each target curve's within-population warp $\gamma_i$, and composes them.

!!! warning "Warp composition order is wrong in fdars-core 0.48"
    The total warp should be $\gamma_i \circ \gamma_B$ (first move into the target mean's frame, then across the bridge), but 0.48 composes $\gamma_B\circ\gamma_i$. On a simple test, the aligned curves miss the source mean by 0.14–0.18 in sup norm, against 0.05–0.07 with the correct order. The reported `distances` re-optimise the warp and hide the error. Until this is fixed upstream, do not use `aligned_data` or `gammas` from `transfer_alignment`; instead align the target curves directly to the source Karcher mean with `align_to_target(target_data, source_mean, t)`.

```python
from fdars.alignment import karcher_mean, align_to_target

source_mean = karcher_mean(source, t)["mean"]
res = align_to_target(target, source_mean, t)   # target curves in the source frame
aligned, gammas = res["aligned_data"], res["gammas"]
```

| `transfer_alignment` key | Description |
|-----|-------------|
| `source_mean` | Karcher mean of the source population |
| `aligned_data` | Target curves in the source frame (affected by the warning) |
| `gammas` | Composed warps (affected by the warning) |
| `bridging_gamma` | Warp aligning the target mean to the source mean |
| `distances` | Elastic distances after transfer (re-optimised) |

---

## 9. Geodesic interpolation between curves

A **geodesic** on the elastic manifold is the shortest path between two curves. `curve_geodesic` first aligns $f_2$ to $f_1$ and then interpolates the *amplitude*: the intermediate curves are built from a path in SRSF space between $q_1$ and the aligned $(q_2\circ\gamma)\sqrt{\dot\gamma}$, in $f_1$'s time frame. The last curve is therefore the **aligned** $f_2\circ\gamma$, not $f_2$ itself, and the phase part of the path is carried by the returned `warps`.

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

The viridis-graded intermediates start at $f_1$ and end at $f_2$ *aligned to $f_1$*: features stay at $f_1$'s times and their heights and widths change along the path. The returned `distances` grow linearly in $\alpha$, the signature of a constant-speed geodesic.

| Key | Description |
|-----|-------------|
| `curves` | Interpolated curves in $f_1$'s time frame, shape `(n_points, m)` |
| `warps` | The intermediate warps |
| `distances` | Cumulative elastic distance along the path |
| `parameter_values` | The $\alpha\in[0,1]$ for each curve |

---

## 10. Gaussian generative model

After separating amplitude and phase, you can *generate* new curves by sampling from the estimated score distributions -- useful for augmentation and simulation. `gauss_model` fits Gaussians to the vertical (amplitude) and horizontal (phase) FPC scores and draws new samples.

!!! warning "`joint_gauss_model` does not keep amplitude–phase correlation"
    `joint_gauss_model` is documented as sampling the joint [amplitude | phase] scores, but in fdars-core 0.48 it draws each score from an independent (diagonal) Gaussian. On training data where peak height and peak location are correlated at 0.999, its samples show a correlation of −0.02. Treat its samples as amplitude and phase drawn *independently*; if the coupling matters, fit `jfpca_fit` and sample its scores with their full covariance yourself.

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

The orange synthetic curves occupy the same amplitude-and-timing envelope as the blue originals: the model samples amplitude and phase scores and recombines them, rather than memorising individual curves. Because the two score sets are sampled independently, any dependence between how tall and how late a feature is in the data is not reproduced.

| Key | Description |
|-----|-------------|
| `samples` | Synthetic curves, shape `(n_samples, m)` |
| `warps` | Warps applied to the synthetic amplitudes |
| `scores` | Sampled FPC scores |

---

## 11. Peak persistence for automatic $\lambda$

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

## 12. Choosing $\lambda$ by cross-validation

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

The orange line marks the selected $\lambda$. Treat it as a lower bound rather than an optimum: the held-out criterion of `lambda_cv` favours flexible warps, so it is **biased toward small $\lambda$** and often returns the smallest candidate. Combine it with `peak_persistence`, with the warp diagnostics on the [Elastic Alignment](elastic-alignment.md#alignment-quality-diagnostics) page, and with a look at the warps. Note also that a numeric $\lambda$ means different things on different grids and optimisers (see [the λ scale](elastic-optimisers.md#the-scale-of-lambda)).

| Key | Description |
|-----|-------------|
| `best_lambda` | Regularization minimizing the CV score |
| `cv_scores` | Mean CV score for each candidate |
| `lambdas` | The candidate grid that was scored |

!!! warning "Array arguments must be `ndarray`"
    `lambda_cv`, `peak_persistence`, and `elastic_align_pair_constrained` reject plain Python lists for their array arguments (`lambdas`, `landmark_targets`, `landmark_sources`) with a `TypeError`. Wrap them with `np.array(...)`.

---

## Pairwise variants

Penalised and landmark-constrained pairwise alignment have moved:

- **Warp penalties** ($\lambda P(\gamma)$ with `penalty="l2gam" | "l2psi" | "roughness" | "geodesic"`) are part of the objective of every `*_with_config` aligner and are documented on [Elastic Optimisers & Penalties](elastic-optimisers.md#warp-penalties).
- `elastic_align_pair_penalized(penalty_type="second_order" | "combined")` is **deprecated**: those options smooth the DP warp *after* the fact instead of penalising it in the objective. Use `elastic_align_pair_with_config(method="rbfgs", penalty="roughness", lambda_=...)` instead. Its default `penalty_type="first_order"` equals `elastic_align_pair` with the same `lambda_`.
- **Landmark-constrained** elastic alignment (`elastic_align_pair_constrained`, `elastic_align_pair_constrained_with_config`) is on [Landmark Registration](landmark-registration.md#landmarks-elastic-between-them).

---

See [Elastic Alignment](elastic-alignment.md) for the baseline aligner and the SRSF/Karcher-mean machinery, [Elastic Optimisers & Penalties](elastic-optimisers.md) for DP, RBFGS and penalties, [TSRVF](tsrvf.md) for linearised statistics, [Shape Analysis](shape-analysis.md) for elastic FPCA, and [Choosing an Alignment Method](choosing-a-method.md) for when to use which aligner.

## References

- Cheng, W., Dryden, I.L., Huang, X. (2016). *Bayesian registration of functions and curves.* Bayesian Analysis 11(2):447-481.
- Tucker, J.D., Wu, W., Srivastava, A. (2013). *Generative models for functional data using phase and amplitude separation.* Computational Statistics & Data Analysis 61:50-66.
- Srivastava, A., Klassen, E. (2016). *Functional and Shape Data Analysis.* Springer.
