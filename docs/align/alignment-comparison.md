# Comparing Alignment Methods

Which registration method should you reach for? `fdars` (via its Python bindings and a little numpy) gives you four strategies with different trade-offs:

- **Elastic alignment** ([`karcher_mean`](elastic-alignment.md#group-alignment-karcher-mean)) -- global optimization by dynamic programming in SRSF space; smooth warps, no feature detection.
- **Landmark registration** (numpy, from [Landmark Registration](landmark-registration.md)) -- feature-based piecewise-linear warping; interpretable, needs reliable landmarks.
- **Constrained elastic** ([`elastic_align_pair_constrained`](advanced-alignment.md#landmark-constrained)) -- elastic optimization that passes *through* landmark anchors; smooth *and* feature-aware.
- **TSRVF** ([`tsrvf_transform`](tsrvf.md)) -- not an alignment per se, but a linearization of elastic alignment for downstream PCA/regression/clustering.

This page runs the first three on the same datasets, quantifies what they do to the mean and the variance, and gives a decision guide.

The headline result: on phase-varying data all three collapse the phase spread and sharpen the mean, while the naive cross-sectional mean stays flattened.

```python exec="1" html="1"
import numpy as np
from scipy.signal import find_peaks
from docs_fig import fig, render
from fdars.alignment import karcher_mean, elastic_align_pair_constrained

rng = np.random.default_rng(9)
n, m = 16, 150
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)

data = np.zeros((n, m))
for i in range(n):
    w = t ** rng.uniform(0.7, 1.5)
    data[i] = np.interp(t, (w - w.min()) / np.ptp(w), base)

# --- Elastic ---
elastic = np.asarray(karcher_mean(data, t, lambda_=0.0, max_iter=20, tol=1e-4)["aligned_data"])

# --- Landmark (numpy) ---
def top_peaks(y, k, mp=0.2):
    idx, props = find_peaks(y, prominence=mp)
    order = np.argsort(props["prominences"])[::-1][:k]
    return np.sort(t[idx[order]])

L = np.array([top_peaks(r, 2) for r in data])
target = L.mean(0)

def register(y, s):
    kt = np.concatenate(([0.0], target, [1.0]))
    ks = np.concatenate(([0.0], s, [1.0]))
    return np.interp(np.interp(t, kt, ks), t, y)

landmark = np.array([register(data[i], L[i]) for i in range(n)])

# --- Constrained elastic (pin peaks, optimize between) ---
ref = data[0]
constrained = np.array([
    np.asarray(elastic_align_pair_constrained(ref, data[i], t, target, L[i], lambda_=0.0)["f_aligned"])
    for i in range(n)])

panels = [("No alignment", data, "#3f51b5", "#dc3545"),
          ("Elastic (Karcher)", elastic, "#198754", "#e8710a"),
          ("Landmark (numpy)", landmark, "#6f42c1", "#e8710a"),
          ("Constrained elastic", constrained, "#0dcaf0", "#e8710a")]

f, axes = fig(ncols=4, figsize=(13.5, 3.4))
for ax, (title, arr, c, cm) in zip(axes, panels):
    ax.plot(t, arr.T, color=c, lw=0.9, alpha=0.4)
    ax.plot(t, arr.mean(0), color=cm, lw=2.2, label="mean")
    ax.set(title=title, xlabel="t", ylim=(-0.1, 2.0))
    ax.legend(fontsize=8)
axes[0].set(ylabel="f(t)")
print(render(f))
```

The three aligners each recover a sharp two-peak mean; the constrained method matches the elastic one here because the peaks are the dominant features.

---

## Warping functions: the mechanism differs

The warps expose the fundamental difference. Elastic produces smooth diffeomorphisms; landmark produces piecewise-linear paths kinked at the landmarks; constrained is smooth *but passes through the landmark anchors*.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.signal import find_peaks
from docs_fig import fig, render
from fdars.alignment import karcher_mean, elastic_align_pair_constrained

rng = np.random.default_rng(9)
n, m = 16, 150
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)
data = np.zeros((n, m))
for i in range(n):
    w = t ** rng.uniform(0.7, 1.5)
    data[i] = np.interp(t, (w - w.min()) / np.ptp(w), base)

# elastic warps
gam_el = np.asarray(karcher_mean(data, t, max_iter=20)["gammas"])

# landmark warps
def top_peaks(y, k, mp=0.2):
    idx, props = find_peaks(y, prominence=mp)
    return np.sort(t[idx[np.argsort(props["prominences"])[::-1][:k]]])
L = np.array([top_peaks(r, 2) for r in data]); target = L.mean(0)
gam_lm = np.array([np.interp(t, np.concatenate(([0.], target, [1.])),
                             np.concatenate(([0.], L[i], [1.]))) for i in range(n)])

# constrained warps
ref = data[0]
gam_c = np.array([np.asarray(elastic_align_pair_constrained(
    ref, data[i], t, target, L[i], lambda_=0.0)["gamma"]) for i in range(n)])

f, axes = fig(ncols=3, figsize=(12, 3.6))
for ax, (g, title, c) in zip(axes, [
        (gam_el, "Elastic (smooth)", "#198754"),
        (gam_lm, "Landmark (kinked)", "#6f42c1"),
        (gam_c, "Constrained (smooth + anchored)", "#0dcaf0")]):
    ax.plot(t, g.T, color=c, lw=1.0, alpha=0.6)
    ax.plot([0, 1], [0, 1], color="#6c757d", ls="--", lw=1.2)
    for x in target:
        ax.axvline(x, color="#adb5bd", ls=":", lw=0.8)
    ax.set(title=title, xlabel="t", aspect="equal")
axes[0].set(ylabel="$\\gamma(t)$")
print(render(f))
```

The landmark warps have visible corners at the landmark times (dotted verticals); the elastic and constrained warps are smooth, but only the constrained one is pinned to pass through those same times.

---

## Quantifying alignment quality

Sharper means come from lower cross-sectional variance. The **variance reduction** VR $=1-\overline{\operatorname{Var}}_{\text{aligned}}/\overline{\operatorname{Var}}_{\text{original}}$ measures how much pointwise variance each method removes. We compare all three on **two** datasets: smooth global phase shifts, and distinct independently-shifting features.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.signal import find_peaks
from docs_fig import fig, render
from fdars.alignment import karcher_mean, elastic_align_pair_constrained

t = np.linspace(0, 1, 160)

def make_smooth(seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((15, len(t)))
    for i in range(15):
        s = rng.uniform(-0.1, 0.1); a = rng.normal(1, 0.15)
        out[i] = a * np.sin(2 * np.pi * (t - s)) + 0.4 * a * np.sin(4 * np.pi * (t - 0.7 * s))
    return out

def make_features(seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((15, len(t)))
    for i in range(15):
        p1 = rng.uniform(0.15, 0.35); p2 = rng.uniform(0.55, 0.75)
        out[i] = rng.normal(1, 0.2) * np.exp(-200 * (t - p1) ** 2) + \
                 rng.normal(0.8, 0.15) * np.exp(-200 * (t - p2) ** 2)
    return out

def vr(orig, aligned):
    return 1 - np.var(aligned, axis=0).mean() / np.var(orig, axis=0).mean()

def top_peaks(y, k, mp):
    idx, props = find_peaks(y, prominence=mp)
    if len(idx) == 0:
        return np.array([t[np.argmax(y)]] * k)
    o = np.argsort(props["prominences"])[::-1][:k]
    pk = np.sort(t[idx[o]])
    return np.pad(pk, (0, k - len(pk)), constant_values=pk[-1]) if len(pk) < k else pk

def landmark_align(data, k, mp):
    L = np.array([top_peaks(r, k, mp) for r in data]); target = L.mean(0)
    def reg(y, s):
        kt = np.concatenate(([0.], target, [1.])); ks = np.concatenate(([0.], s, [1.]))
        return np.interp(np.interp(t, kt, ks), t, y)
    return np.array([reg(data[i], L[i]) for i in range(len(data))]), L, target

def constrained_align(data, L, target):
    ref = data[0]
    return np.array([np.asarray(elastic_align_pair_constrained(
        ref, data[i], t, target, L[i], lambda_=0.0)["f_aligned"]) for i in range(len(data))])

results = {}
for name, mk, k, mp in [("smooth", make_smooth, 1, 0.3), ("features", make_features, 2, 0.2)]:
    data = mk(42)
    el = np.asarray(karcher_mean(data, t, max_iter=20)["aligned_data"])
    lm, L, target = landmark_align(data, k, mp)
    cn = constrained_align(data, L, target)
    results[name] = {"Elastic": vr(data, el), "Landmark": vr(data, lm), "Constrained": vr(data, cn)}

methods = ["Elastic", "Landmark", "Constrained"]
x = np.arange(len(methods)); w = 0.38
f, ax = fig()
ax.bar(x - w / 2, [results["smooth"][m] for m in methods], w,
       color="#3f51b5", label="smooth shifts")
ax.bar(x + w / 2, [results["features"][m] for m in methods], w,
       color="#e8710a", label="distinct features")
ax.set(title="Variance reduction by method and dataset",
       ylabel="VR (higher = better)", xticks=x, ylim=(0, 1.05))
ax.set_xticklabels(methods)
ax.legend(fontsize=9)
print(render(f))

for ds in ("smooth", "features"):
    print(ds, {m: round(results[ds][m], 3) for m in methods})
```

The pattern mirrors the R reference: on **smooth global shifts**, elastic and constrained lead and landmark trails (broad oscillations give it few clean anchors); on **distinct features**, all three do well, with elastic and constrained excellent because the peaks are unambiguous.

### Elastic diagnostics

For the elastic method, `alignment_quality` decomposes the variance and `warp_statistics` summarizes the warps -- reporting *how much* work alignment did and *how* the total splits into amplitude and phase.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import karcher_mean, alignment_quality, warp_statistics

rng = np.random.default_rng(9)
n, m = 16, 140
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)
data = np.zeros((n, m))
for i in range(n):
    w = t ** rng.uniform(0.7, 1.5)
    data[i] = np.interp(t, (w - w.min()) / np.ptp(w), base)

q = alignment_quality(data, t, lambda_=0.0, max_iter=15)
km = karcher_mean(data, t, max_iter=20)
ws = warp_statistics(np.asarray(km["gammas"]), t, confidence_level=0.95)

f, ax = fig()
labels = ["amplitude\nvariance", "phase\nvariance"]
vals = [float(q["amplitude_variance"]), float(q["phase_variance"])]
ax.bar(labels, vals, color=["#198754", "#6f42c1"])
for i, v in enumerate(vals):
    ax.text(i, v, f"{v:.4f}", ha="center", va="bottom", fontsize=9)
ax.set(title=f"Variance decomposition "
             f"(phase share {float(q['phase_amplitude_ratio']):.0%})",
       ylabel="variance")
print(render(f))

print(f"mean variance reduction : {float(q['mean_variance_reduction']):.4f}")
print(f"phase / amplitude ratio : {float(q['phase_amplitude_ratio']):.4f}")
print(f"mean warp complexity    : {float(q['mean_warp_complexity']):.4f}")
print(f"mean geodesic dist warps: {np.asarray(ws['geodesic_distances']).mean():.4f}")
```

| `alignment_quality` key | Meaning |
|-------------------------|---------|
| `mean_variance_reduction` | Fraction of pointwise variance removed (the VR metric) |
| `total_variance` | Total variance before decomposition |
| `amplitude_variance` / `phase_variance` | Variance attributed to amplitude / to phase |
| `phase_amplitude_ratio` | Phase share of total -- high means phase-dominated |
| `mean_warp_complexity` / `mean_warp_smoothness` | Average warp magnitude / roughness |
| `pointwise_variance_ratio` | Per-point post/pre variance ratio, shape `(m,)` |

A high `phase_amplitude_ratio` (near 1) confirms the variation is mostly timing -- precisely where alignment helps most.

---

## When each method succeeds -- and fails

Real data is messier than tidy examples. These scenarios show where each method shines and where it breaks.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.signal import find_peaks
from docs_fig import fig, render
from fdars.alignment import karcher_mean

t = np.linspace(0, 1, 200)

# Scenario A: smooth global warp -- no clean features (elastic wins, landmark struggles)
rng = np.random.default_rng(101)
smooth = np.zeros((12, 200))
for i in range(12):
    ws_ = rng.uniform(-0.15, 0.15)
    tw = t + ws_ * np.sin(np.pi * t)
    tw = (tw - tw.min()) / np.ptp(tw)
    smooth[i] = np.sin(2 * np.pi * tw) + 0.3 * np.cos(6 * np.pi * tw)

# Scenario B: mixed 1-peak & 2-peak curves (elastic handles, landmark forced-template fails)
rng = np.random.default_rng(7)
mixed = np.zeros((12, 200))
for i in range(12):
    if i < 6:
        mixed[i] = 1.5 * np.exp(-300 * (t - rng.uniform(0.3, 0.5)) ** 2)
    else:
        mixed[i] = np.exp(-300 * (t - rng.uniform(0.2, 0.35)) ** 2) + \
                   np.exp(-300 * (t - rng.uniform(0.6, 0.75)) ** 2)

# Scenario C: noisy -- raw vs pre-smoothed elastic
rng = np.random.default_rng(3)
noisy = np.array([np.sin(2 * np.pi * (t - rng.uniform(-0.08, 0.08))) + rng.normal(0, 0.35, 200)
                  for _ in range(12)])
# simple moving-average pre-smoothing
kern = np.ones(11) / 11
smoothed = np.array([np.convolve(y, kern, mode="same") for y in noisy])

el_smooth = np.asarray(karcher_mean(smooth, t, max_iter=20)["aligned_data"])
el_mixed = np.asarray(karcher_mean(mixed, t, max_iter=20)["aligned_data"])
el_noisy_raw = np.asarray(karcher_mean(noisy, t, max_iter=20)["aligned_data"])
el_noisy_sm = np.asarray(karcher_mean(smoothed, t, max_iter=20)["aligned_data"])

f, axes = fig(ncols=3, figsize=(12.5, 3.6))
axes[0].plot(t, el_smooth.T, color="#198754", lw=0.9, alpha=0.5)
axes[0].plot(t, el_smooth.mean(0), color="#e8710a", lw=2.2)
axes[0].set(title="A: smooth warp -> elastic aligns cleanly", xlabel="t", ylabel="f(t)")

axes[1].plot(t, el_mixed.T, color="#3f51b5", lw=0.9, alpha=0.5)
axes[1].plot(t, el_mixed.mean(0), color="#e8710a", lw=2.2)
axes[1].set(title="B: mixed 1-/2-peak -> elastic copes", xlabel="t")

axes[2].plot(t, el_noisy_raw.mean(0), color="#dc3545", lw=2.0, label="raw (over-warps)")
axes[2].plot(t, el_noisy_sm.mean(0), color="#198754", lw=2.0, label="smooth then align")
axes[2].set(title="C: noisy -> smooth first", xlabel="t")
axes[2].legend(fontsize=8)
print(render(f))
```

- **A -- elastic excels on smooth warping.** Broad overlapping oscillations have no clear anchors, so landmark detection has nothing to grab; the Fisher-Rao metric captures the continuous phase change naturally.
- **B -- elastic copes with a variable feature count.** Half the curves have one peak, half have two. Elastic makes no template assumption; a landmark method with a fixed `expected_count=2` would force a spurious second peak onto the single-peak curves.
- **C -- smooth before aligning noisy data.** The SRSF differentiates the curve, so noise drives over-warping. Pre-smoothing (here a moving average; splines or a kernel smoother work too) or a larger `lambda_` tames it.

### Scenario summary

| Scenario | Best method | Why |
|----------|-------------|-----|
| Smooth global warping | Elastic | No features to anchor; optimal continuous warp |
| Independent feature shifts | Landmark | Guarantees feature-to-feature correspondence |
| Noisy data | Elastic (with `lambda_`) or pre-smoothing | Penalty / smoothing controls over-warping |
| Variable number of features | Elastic | No feature template required |
| Features + smooth variation between them | Constrained elastic | Anchors features *and* smooths between them |

---

## Decision guide

| | Warping | Automation | Cost | Smoothness | Feature control |
|--|---------|-----------|------|-----------|-----------------|
| **Elastic** | Smooth diffeomorphism | Fully automatic | $O(nm^2)$ | High | None |
| **Landmark** | Piecewise-linear | Needs feature type | $O(nm+nk)$ | Low (corners) | Full |
| **Constrained** | Smooth with anchors | Needs feature type | $O(nm^2/k)$ | High between anchors | Partial |
| **TSRVF** | (uses elastic) | Fully automatic | $O(nm^2)$ + PCA | High | None |

| Situation | Recommended |
|-----------|-------------|
| No prior on which features correspond; smooth timing differences | **Elastic** (`karcher_mean`) |
| Want a principled metric / amplitude-phase decomposition | **Elastic** + [Shape Analysis](shape-analysis.md) |
| Well-defined, domain-meaningful features; need guaranteed correspondence | **Landmark** ([Landmark Registration](landmark-registration.md)) |
| Features must align exactly *and* the warp between them should be smooth | **Constrained** ([`elastic_align_pair_constrained`](advanced-alignment.md#landmark-constrained)) |
| PCA / regression / clustering on aligned curves | **Elastic** + [TSRVF](tsrvf.md) |

### Pitfalls

| Method | Common pitfall | Mitigation |
|--------|----------------|-----------|
| Elastic | Over-warping ("pinching") on noisy data | Increase `lambda_`, or pre-smooth |
| Landmark | Mismatched landmark correspondence | Use a fixed count, raise the prominence threshold |
| Constrained | Too few landmarks = barely constrained | Detect more / multiple landmark types |
| TSRVF | Linearization error for curves far from the mean | Check reconstruction quality |

---

## A worked workflow

A typical analysis chains the methods: explore, detect features to *understand structure*, align with the method the structure suggests, then linearize with TSRVF for downstream statistics.

```python
import numpy as np
from scipy.signal import find_peaks
from fdars.alignment import karcher_mean, tsrvf_transform

# 1) explore, 2) understand structure via landmark counts
counts = [len(find_peaks(row, prominence=0.2)[0]) for row in data]
print("peaks per curve:", counts)   # variable count -> prefer elastic

# 3) align (elastic here, since the feature count varies)
km = karcher_mean(data, t, max_iter=15)

# 4) linearize for PCA on the tangent vectors
V = np.asarray(tsrvf_transform(data, t, max_iter=15)["tangent_vectors"])
Vc = V - V.mean(0)
s = np.linalg.svd(Vc, compute_uv=False)
cum = np.cumsum(s ** 2) / np.sum(s ** 2)
print("variance explained (first 3 PCs):", (cum[:3] * 100).round(1))
```

---

See [Elastic Alignment](elastic-alignment.md), [Advanced Elastic Alignment](advanced-alignment.md), [Landmark Registration](landmark-registration.md), and [TSRVF](tsrvf.md) for the individual methods, and [Shape Analysis](shape-analysis.md) for the amplitude/phase decomposition that alignment enables.
