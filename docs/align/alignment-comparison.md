# Comparing Alignment Methods

Which registration method should you use? This page runs three approaches on **one** phase-varying dataset and compares what they do to the mean and to the cross-sectional variance:

- **No alignment** -- the raw cross-sectional mean, blurred by phase spread.
- **Elastic** ([`karcher_mean`](elastic-alignment.md#group-alignment-karcher-mean)) -- finds smooth warps automatically under the Fisher-Rao metric.
- **Landmark** (numpy, from [Landmark Registration](landmark-registration.md)) -- maps detected peaks onto common target times with a piecewise-linear warp.

The headline result: both alignment methods collapse the phase spread and recover a sharp two-peak mean, while the naive mean stays flattened. The figure shows all three side by side.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import karcher_mean

rng = np.random.default_rng(9)
n, m = 16, 140
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)

# One phase-varying dataset for all three methods
data = np.zeros((n, m))
for i in range(n):
    w = t ** rng.uniform(0.7, 1.5)
    data[i] = np.interp(t, (w - w.min()) / np.ptp(w), base)

# --- Elastic ---
km = karcher_mean(data, t, lambda_=0.0, max_iter=20, tol=1e-4)
elastic = np.asarray(km["aligned_data"])

# --- Landmark (numpy) ---
def landmarks(y):
    ii = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
    return np.sort(t[ii[np.argsort(y[ii])[::-1]][:2]])

L = np.array([landmarks(r) for r in data])
target = L.mean(0)

def register(y, s):
    kt = np.concatenate(([0.0], target, [1.0]))
    ks = np.concatenate(([0.0], s, [1.0]))
    return np.interp(np.interp(t, kt, ks), t, y)

landmark = np.array([register(data[i], L[i]) for i in range(n)])

panels = [("No alignment", data, "#3f51b5", "#dc3545"),
          ("Elastic (Karcher)", elastic, "#198754", "#e8710a"),
          ("Landmark (numpy)", landmark, "#6f42c1", "#e8710a")]

f, axes = fig(ncols=3, figsize=(11.5, 3.6))
for ax, (title, arr, c, cm) in zip(axes, panels):
    ax.plot(t, arr.T, color=c, lw=0.9, alpha=0.4)
    ax.plot(t, arr.mean(0), color=cm, lw=2.4, label="mean")
    ax.set(title=title, xlabel="t", ylim=(-0.1, 2.0))
    ax.legend(fontsize=8)
axes[0].set(ylabel="f(t)")
print(render(f))
```

---

## Quantifying alignment quality

Sharper means come from lower cross-sectional variance. `alignment_quality` runs the elastic alignment internally and reports a suite of diagnostics -- how much variance the alignment removes and how the total splits into amplitude and phase.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import karcher_mean, alignment_quality

rng = np.random.default_rng(9)
n, m = 16, 140
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)
data = np.zeros((n, m))
for i in range(n):
    w = t ** rng.uniform(0.7, 1.5)
    data[i] = np.interp(t, (w - w.min()) / np.ptp(w), base)

elastic = np.asarray(karcher_mean(data, t, max_iter=20)["aligned_data"])

def landmarks(y):
    ii = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
    return np.sort(t[ii[np.argsort(y[ii])[::-1]][:2]])
L = np.array([landmarks(r) for r in data]); target = L.mean(0)
def register(y, s):
    kt = np.concatenate(([0.0], target, [1.0])); ks = np.concatenate(([0.0], s, [1.0]))
    return np.interp(np.interp(t, kt, ks), t, y)
landmark = np.array([register(data[i], L[i]) for i in range(n)])

# Mean cross-sectional variance = how blurred the mean is
def cs_var(a):
    return float(np.var(a, axis=0).mean())
vars_ = {"none": cs_var(data), "elastic": cs_var(elastic), "landmark": cs_var(landmark)}

# fdars diagnostic on the elastic alignment
q = alignment_quality(data, t, lambda_=0.0, max_iter=15)

f, ax = fig()
names = list(vars_.keys())
ax.bar(names, [vars_[k] for k in names],
       color=["#3f51b5", "#198754", "#6f42c1"])
ax.set(title="Cross-sectional variance (lower = sharper mean)",
       ylabel="mean pointwise variance")
for i, k in enumerate(names):
    ax.text(i, vars_[k], f"{vars_[k]:.4f}", ha="center", va="bottom", fontsize=8)
print(render(f))

print()
print(f"alignment_quality (elastic):")
print(f"  mean variance reduction : {float(q['mean_variance_reduction']):.4f}")
print(f"  phase / amplitude ratio : {float(q['phase_amplitude_ratio']):.4f}")
print(f"  mean warp complexity    : {float(q['mean_warp_complexity']):.4f}")
```

Both aligners drive the cross-sectional variance far below the unaligned baseline. The elastic method typically goes furthest because its warp is a free smooth diffeomorphism; the landmark method is limited to piecewise-linear warps through the detected peaks, but is fully interpretable and needs no optimization.

| `alignment_quality` key | Meaning |
|-------------------------|---------|
| `mean_variance_reduction` | Fraction of pointwise variance removed by alignment |
| `total_variance` | Total variance before decomposition |
| `amplitude_variance` | Variance attributable to amplitude |
| `phase_variance` | Variance attributable to phase (timing) |
| `phase_amplitude_ratio` | Phase share of total variance -- high means phase-dominated |
| `mean_warp_complexity` | Average geodesic distance of warps from the identity |
| `mean_warp_smoothness` | Average bending energy of the warps |
| `pointwise_variance_ratio` | Per-point post/pre variance ratio, shape `(m,)` |

A high `phase_amplitude_ratio` (near 1) confirms the dataset's variation is mostly timing -- precisely the case where alignment helps most.

---

## Warp diagnostics with `warp_statistics`

To summarize the *warps themselves* -- the phase that alignment extracted -- pass the estimated `gammas` to `warp_statistics`. It returns a mean warp and a confidence band, useful for reporting how much timing distortion the sample carries.

```python
import numpy as np
from fdars.alignment import karcher_mean, warp_statistics

km = karcher_mean(data, t, max_iter=20)
gammas = np.asarray(km["gammas"])            # (n, m)

ws = warp_statistics(gammas, t, confidence_level=0.95)
mean_warp = ws["mean"]           # (m,) Karcher-mean warp
lower      = ws["lower_band"]     # (m,) pointwise lower confidence band
upper      = ws["upper_band"]     # (m,) pointwise upper confidence band
geo_dist   = ws["geodesic_distances"]   # (n,) per-warp distance from identity
```

| Key | Type | Description |
|-----|------|-------------|
| `mean` | `ndarray (m,)` | Mean warp |
| `variance` / `std_dev` | `ndarray (m,)` | Pointwise spread of the warps |
| `lower_band` / `upper_band` | `ndarray (m,)` | Confidence band around the mean warp |
| `karcher_mean_warp` | `ndarray (m,)` | Karcher-mean warp under the warp geometry |
| `geodesic_distances` | `ndarray (n,)` | Each warp's distance from the identity |

---

## Which method to reach for

| Situation | Recommended |
|-----------|-------------|
| Clear, reliable landmarks (known peak, stimulus onset) | Landmark registration |
| No obvious landmarks / want a fully automatic fit | Elastic (`karcher_mean`) |
| Need smooth warps and amplitude/phase separation | Elastic + [Shape Analysis](shape-analysis.md) |
| Landmarks known but rest of curve matters too | [`elastic_align_pair_constrained`](advanced-alignment.md#landmark-constrained) |
| Downstream linear statistics on aligned curves | Elastic + [TSRVF](tsrvf.md) |

!!! tip "Report the phase share"
    Before aligning, check `alignment_quality`'s `phase_amplitude_ratio`. If it is small, most of your variation is amplitude and alignment will change little; if it is large, alignment is doing real work and you should report the variance reduction it achieves.

See [Elastic Alignment](elastic-alignment.md), [Advanced Elastic Alignment](advanced-alignment.md), and [Landmark Registration](landmark-registration.md) for the individual methods.
