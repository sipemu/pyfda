# Landmark Registration

Landmark registration is the oldest and most transparent way to remove phase variation: identify a handful of *landmarks* on each curve -- a peak, a valley, a zero-crossing, an event onset -- and time-warp every curve so that its landmarks land at common target locations. Unlike elastic alignment, which searches for an optimal warp automatically under the Fisher-Rao metric, landmark registration lets you *dictate* the correspondence. That makes it interpretable and cheap, at the cost of needing the landmarks up front.

!!! warning "Implemented in numpy on this page (no binding)"
    `fdars` has no landmark-registration binding. The warp here is a plain **piecewise-linear monotone interpolation** built with `numpy.interp`, applied to an `Fdata` object. Everything shown runs, but the registration itself is numpy, not a library call. For an elastic aligner that can *pin* landmarks inside a Fisher-Rao fit, see [`elastic_align_pair_constrained`](advanced-alignment.md#landmark-constrained).

The figure below shows a two-peak sample whose peaks drift in time (left), and the same curves after each peak has been warped onto the sample-mean peak location (right). The cross-sectional mean sharpens because the phase spread is gone.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars import Fdata

rng = np.random.default_rng(3)
n, m = 12, 150
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)

# Phase-varying sample: compose the base with random monotone warps of argvals
data = np.zeros((n, m))
for i in range(n):
    warp = t ** rng.uniform(0.7, 1.5)
    warp = (warp - warp.min()) / np.ptp(warp)
    data[i] = np.interp(t, warp, base)

def landmarks(y):
    """Two highest interior local maxima, sorted by time."""
    interior = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
    top = interior[np.argsort(y[interior])[::-1]][:2]
    return np.sort(t[top])

L = np.array([landmarks(data[i]) for i in range(n)])   # (n, 2)
target = L.mean(0)                                       # common peak times

def register(y, src_lm):
    """Piecewise-linear monotone warp mapping src_lm -> target."""
    knots_tgt = np.concatenate(([0.0], target, [1.0]))
    knots_src = np.concatenate(([0.0], src_lm, [1.0]))
    src_time = np.interp(t, knots_tgt, knots_src)   # target time -> source time
    return np.interp(src_time, t, y)

registered = np.array([register(data[i], L[i]) for i in range(n)])
fd_reg = Fdata(registered, argvals=t)

f, (a1, a2) = fig(ncols=2, figsize=(9.5, 4.0))
a1.plot(t, data.T, color="#3f51b5", lw=1, alpha=0.5)
a1.plot(t, data.mean(0), color="#dc3545", lw=2.4, label="cross-sec. mean")
for x in target:
    a1.axvline(x, color="#6c757d", ls=":", lw=1)
a1.set(title="Unregistered (peaks drift)", xlabel="t", ylabel="f(t)")
a1.legend(fontsize=8)

a2.plot(t, np.asarray(fd_reg.data).T, color="#198754", lw=1, alpha=0.5)
a2.plot(t, np.asarray(fd_reg.data).mean(0), color="#e8710a", lw=2.4, label="mean")
for x in target:
    a2.axvline(x, color="#6c757d", ls=":", lw=1)
a2.set(title="Landmark-registered", xlabel="t")
a2.legend(fontsize=8)
print(render(f))
```

---

## Concepts

### The piecewise-linear landmark warp

Suppose curve $i$ has landmarks at times $\ell_{i,1} < \dots < \ell_{i,K}$ and we want them at common **target** times $\tau_1 < \dots < \tau_K$ (often the sample mean of each landmark). Define the warp $\gamma_i$ by interpolating linearly between the matched knots, anchored at the domain endpoints:

$$
\gamma_i(\tau_k) = \ell_{i,k}, \qquad \gamma_i(0) = 0, \quad \gamma_i(1) = 1,
$$

and linear in between. The registered curve is the original sampled through the warp,

$$
f_i^{\text{reg}}(\tau) = f_i\big(\gamma_i(\tau)\big).
$$

Because the knots are increasing on both axes, $\gamma_i$ is a **monotone** (order-preserving) time transformation -- it never folds time back on itself. Concretely, `np.interp` between the knot pairs gives $\gamma_i$, and a second `np.interp` samples the curve at those warped times. This is exactly the classic "landmark registration by linear interpolation" of Ramsay & Silverman, done in two lines.

### Choosing landmarks

Landmarks must be *structurally comparable* across curves: the "first peak" on one curve must correspond to the "first peak" on another. Common choices:

- **Extrema** -- peaks and valleys (used above).
- **Zero-crossings** or fixed-level crossings.
- **Event onsets** -- e.g. the time a growth curve exceeds a threshold.
- **Inflection points** from the second derivative.

The detector below simply takes the two highest interior local maxima, but any rule that yields one time per landmark per curve works.

---

## Usage

The registration is three self-contained numpy steps: detect landmarks, choose targets, warp.

```python
import numpy as np
from fdars import Fdata

t = np.linspace(0, 1, 150)
# ... `data` is an (n, m) array of phase-varying curves ...

# 1) detect one time per landmark per curve  ->  L has shape (n, K)
def landmarks(y):
    interior = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
    top = interior[np.argsort(y[interior])[::-1]][:2]
    return np.sort(t[top])

L = np.array([landmarks(row) for row in data])

# 2) target locations: sample-mean of each landmark (any fixed target works)
target = L.mean(axis=0)

# 3) piecewise-linear monotone warp, applied to every curve
def register(y, src_lm):
    knots_tgt = np.concatenate(([0.0], target, [1.0]))
    knots_src = np.concatenate(([0.0], src_lm, [1.0]))
    src_time = np.interp(t, knots_tgt, knots_src)
    return np.interp(src_time, t, y)

registered = np.array([register(data[i], L[i]) for i in range(len(data))])
fd_reg = Fdata(registered, argvals=t)   # back into an fdars container
```

| Step | numpy primitive | Role |
|------|-----------------|------|
| Detect | boolean mask + `argsort` | One landmark time per curve per feature |
| Target | `mean(axis=0)` | Common location every curve maps onto |
| Warp | `np.interp` (twice) | Monotone $\gamma_i$, then resample $f_i \circ \gamma_i$ |
| Wrap | `Fdata(...)` | Registered curves as functional data |

!!! note "Endpoint anchoring matters"
    Always include the domain endpoints `0` and `1` as fixed knots. Without them the warp is undefined outside the outermost landmarks and the registered curves lose their edges.

---

## Landmark warps as phase

The warps themselves *are* the phase variation that registration removes. Plotting $\gamma_i$ against the identity shows how much each curve's clock had to be stretched or compressed to bring its landmarks into register -- exactly the interpretation used for elastic warps in [Elastic Alignment](elastic-alignment.md#interpreting-warping-functions), but here obtained deterministically from the landmarks.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render

rng = np.random.default_rng(3)
n, m = 12, 150
t = np.linspace(0, 1, m)
base = np.exp(-((t - 0.35) ** 2) / 0.006) + 0.8 * np.exp(-((t - 0.70) ** 2) / 0.006)
data = np.zeros((n, m))
for i in range(n):
    w = t ** rng.uniform(0.7, 1.5)
    data[i] = np.interp(t, (w - w.min()) / np.ptp(w), base)

def landmarks(y):
    interior = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
    return np.sort(t[interior[np.argsort(y[interior])[::-1]][:2]])

L = np.array([landmarks(row) for row in data])
target = L.mean(0)

f, ax = fig()
for i in range(n):
    knots_tgt = np.concatenate(([0.0], target, [1.0]))
    knots_src = np.concatenate(([0.0], L[i], [1.0]))
    gamma = np.interp(t, knots_tgt, knots_src)     # gamma(target time)
    ax.plot(t, gamma, color="#6f42c1", lw=1.1, alpha=0.7)
ax.plot([0, 1], [0, 1], color="#6c757d", ls="--", lw=1.4, label="identity")
for x in target:
    ax.axvline(x, color="#adb5bd", ls=":", lw=0.9)
ax.set(title="Landmark warps $\\gamma_i$", xlabel="registered time $\\tau$",
       ylabel="original time $\\gamma_i(\\tau)$", aspect="equal")
ax.legend(fontsize=8)
print(render(f))
```

The warps kink at the landmark times (dotted verticals) -- a signature of piecewise-linear registration. Between landmarks the warp is a straight segment, so timing is distorted uniformly within each inter-landmark interval.

---

## Landmark vs. elastic registration

| | Landmark (numpy) | Elastic ([`karcher_mean`](elastic-alignment.md#group-alignment-karcher-mean)) |
|---|---|---|
| Correspondence | You specify it (landmarks) | Found automatically (Fisher-Rao) |
| Warp shape | Piecewise-linear, kinked at knots | Smooth diffeomorphism |
| Needs feature detection | Yes | No |
| Cost | Trivial (`np.interp`) | Iterative optimization |
| Best when | Landmarks are obvious and reliable | Landmarks are ambiguous or absent |

Landmark registration is ideal when the features to align are unambiguous (a clear systolic peak, a known stimulus onset). When landmarks are noisy, hard to detect, or the curves have no obvious features, prefer the elastic aligners -- they optimize the whole curve rather than a few points. A middle ground is [`elastic_align_pair_constrained`](advanced-alignment.md#landmark-constrained), which *pins* landmarks but fills in the rest elastically.

See [Comparing Alignment Methods](alignment-comparison.md) for a head-to-head on the same dataset.
