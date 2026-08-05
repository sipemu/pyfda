---
title: Custom Plotting
---

# Custom Plotting

fdars deliberately ships **no plotting layer** -- an `Fdata` object is just a
grid (`argvals`), a `(n_obs, n_points)` data matrix, and optional metadata, so
you draw it with plain matplotlib. That gives you full control over styling,
but a functional sample is a *family of curves* rather than a scatter of points,
so a few idioms recur: plotting whole curve families, colouring by metadata or
depth, drawing mean±sd envelopes, and highlighting the functional median. This
guide collects those recipes.

Every curve family reduces to one call -- `ax.plot(argvals, data.T)` plots each
row as its own line:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate

t = np.linspace(0, 1, 120)
X = np.asarray(simulate(n=30, argvals=t, n_basis=6, efun_type="fourier", seed=1))
fd = Fdata(X, argvals=t)

f, ax = fig()
ax.plot(t, np.asarray(fd.data).T, color="#3f51b5", lw=1, alpha=0.5)
ax.plot(t, np.asarray(fd.mean()), color="#e8710a", lw=2.6, label="pointwise mean")
ax.set(title="A functional sample: 30 curves and their mean",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

---

## The data behind a plot

Three attributes of an `Fdata` cover almost every plot you will draw:

| Attribute | Shape | Role in a plot |
|-----------|-------|----------------|
| `fd.argvals` | `(n_points,)` | the x-axis (shared grid) |
| `fd.data` | `(n_obs, n_points)` | one row per curve -- transpose to plot |
| `fd.metadata` | `DataFrame` `(n_obs, ...)` | per-curve colour / group keys |

The single most important idiom is the **transpose**. matplotlib's `ax.plot`
draws one line per *column* of a 2-D array, but fdars stores one curve per
*row*, so you plot `data.T`:

```python
ax.plot(fd.argvals, np.asarray(fd.data).T, lw=1, alpha=0.4)
```

!!! note "Wrap returns with `np.asarray`"
    `Fdata` accessors and most `fdars` functions return Rust-backed sequences.
    Wrapping with `np.asarray(...)` before `.T`, slicing, or arithmetic keeps
    the examples robust and lets you use full NumPy indexing.

---

## Colouring by group metadata

When curves carry a categorical label, colour each group separately and build
the legend from the group names rather than from individual curves. Iterate over
the unique groups, mask the data matrix, and give the whole block one label:

```python exec="1" html="1" source="above"
import numpy as np
import pandas as pd
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate

t = np.linspace(0, 1, 120)
# Two populations: a baseline and a shifted+steeper variant
A = np.asarray(simulate(n=18, argvals=t, n_basis=6, seed=3))
B = np.asarray(simulate(n=18, argvals=t, n_basis=6, seed=9)) + 1.5 * t
X = np.vstack([A, B])
meta = pd.DataFrame({"group": ["control"] * 18 + ["treatment"] * 18})
fd = Fdata(X, argvals=t, metadata=meta)

palette = {"control": "#3f51b5", "treatment": "#e8710a"}
groups = np.asarray(fd.metadata["group"])
data = np.asarray(fd.data)

f, ax = fig()
for name, col in palette.items():
    rows = data[groups == name]
    ax.plot(t, rows.T, color=col, lw=1, alpha=0.35)
    ax.plot(t, rows.mean(axis=0), color=col, lw=2.6, label=f"{name} mean")
ax.set(title="Curves coloured by group, with per-group means",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

The trick with the legend is to attach the label only to the bold group-mean
line, so matplotlib does not add 36 entries for the individual curves.

---

## Mean ± standard-deviation bands

A cleaner summary of a group is a shaded envelope: the pointwise mean with a
band at $\pm k$ standard deviations. Compute both statistics along the
observation axis (`axis=0`) and draw the band with `ax.fill_between`:

$$
\bar{X}(t) = \frac{1}{n}\sum_{i=1}^{n} X_i(t), \qquad
s(t) = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}\bigl(X_i(t) - \bar{X}(t)\bigr)^2}
$$

```python exec="1" html="1" source="above"
import numpy as np
import pandas as pd
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate

t = np.linspace(0, 1, 120)
A = np.asarray(simulate(n=25, argvals=t, n_basis=6, seed=3))
B = np.asarray(simulate(n=25, argvals=t, n_basis=6, seed=9)) + 1.5 * t
X = np.vstack([A, B])
meta = pd.DataFrame({"group": ["control"] * 25 + ["treatment"] * 25})
fd = Fdata(X, argvals=t, metadata=meta)

palette = {"control": "#3f51b5", "treatment": "#e8710a"}
groups = np.asarray(fd.metadata["group"])
data = np.asarray(fd.data)

f, ax = fig()
for name, col in palette.items():
    rows = data[groups == name]
    mu = rows.mean(axis=0)
    sd = rows.std(axis=0, ddof=1)
    ax.fill_between(t, mu - sd, mu + sd, color=col, alpha=0.20)
    ax.plot(t, mu, color=col, lw=2.4, label=f"{name}  (mean ± sd)")
ax.set(title="Mean ± 1 sd envelope per group",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

!!! tip "Bands vs. spaghetti"
    Overlaying dozens of raw curves ("spaghetti plots") hides the central
    tendency. A mean±sd band scales to hundreds of curves and makes group
    differences pop out. Use `fill_between(..., alpha=0.2)` so overlapping bands
    stay legible.

---

## Highlighting the functional median

The **functional median** is the deepest curve -- the most central member of the
sample under a chosen depth. Compute depths with `Fdata.depth`, take the
`argmax`, and draw that curve on top of a faint spaghetti backdrop. Shading the
background curves by their depth turns the plot into a centrality map:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate

t = np.linspace(0, 1, 120)
X = np.asarray(simulate(n=30, argvals=t, n_basis=6, efun_type="fourier", seed=1))
fd = Fdata(X, argvals=t)

depth = np.asarray(fd.depth("modified_band"))     # centrality of each curve
order = np.argsort(depth)                          # shallow first, deep last
rng = np.ptp(depth) + 1e-9
data = np.asarray(fd.data)

f, ax = fig()
for i in order:                                    # faint = shallow, bold = deep
    ax.plot(t, data[i], color="#3f51b5", lw=1.1,
            alpha=0.12 + 0.7 * (depth[i] - depth.min()) / rng)
med = order[-1]
ax.plot(t, data[med], color="#e8710a", lw=2.8, label=f"functional median (#{med})")
ax.set(title="Curves shaded by depth, functional median highlighted",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

The alpha of each background curve scales linearly with its depth, so central
curves are opaque and outlying curves fade out. See
[Depth Functions](../represent/depth-functions.md) for the full menu of depth
measures you can pass to `fd.depth(...)`.

!!! tip "A depth-tinted colormap"
    For a continuous colour scale instead of a fixed hue, map depth through a
    matplotlib colormap: `plt.cm.viridis(depth[i] / depth.max())`. Bright curves
    are then the deep ones.

---

## Small multiples

When you want to compare several conditions without overplotting, give each its
own panel. `fig(nrows, ncols, sharey=True)` returns a grid of axes; keep the
y-axis shared so magnitudes are comparable across panels:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate

t = np.linspace(0, 1, 120)
seeds = [1, 7, 21, 42]

f, axes = fig(2, 2, figsize=(9.0, 5.4), sharex=True, sharey=True)
for ax, s in zip(axes.ravel(), seeds):
    fd = Fdata(np.asarray(simulate(n=20, argvals=t, n_basis=6, seed=s)), argvals=t)
    data = np.asarray(fd.data)
    ax.plot(t, data.T, color="#6c757d", lw=0.9, alpha=0.35)
    ax.plot(t, data.mean(axis=0), color="#3f51b5", lw=2.4)
    ax.set_title(f"sample seed={s}")
for ax in axes[-1]:
    ax.set_xlabel("t")
for ax in axes[:, 0]:
    ax.set_ylabel("X(t)")
print(render(f))
```

Small multiples are the honest way to show four samples: nothing is hidden
behind anything else, and the shared axes make the panels directly comparable.

---

## Phase-plane plots

Some questions are about the *shape* of the dynamics rather than the value at a
given `t`. A **phase-plane plot** trades the time axis for a second signal --
plotting one curve against another (classically a function against its
derivative). Here we plot two coordinate functions against each other; the
[Derivatives](derivatives.md) guide shows the velocity-vs-value variant.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate

t = np.linspace(0, 1, 200)
Xx = np.asarray(simulate(n=8, argvals=t, n_basis=5, seed=2))
Xy = np.asarray(simulate(n=8, argvals=t, n_basis=5, seed=8))

f, ax = fig(figsize=(5.2, 5.0))
for i in range(Xx.shape[0]):
    ax.plot(Xx[i], Xy[i], lw=1.4, alpha=0.8)
ax.set(title="Phase-plane view: one signal against another",
       xlabel="X(t)", ylabel="Y(t)")
ax.set_aspect("equal", adjustable="datalim")
print(render(f))
```

!!! note "Argvals disappear on the axes"
    In a phase-plane plot `t` is no longer an axis -- it is the *parameter*
    tracing each loop. Time is implicit in the direction of travel, so add
    arrows or a start marker if the direction matters.

---

## A reusable helper

Most of the recipes above are one-liners once you have `argvals` and `data`.
This small function bundles the spaghetti-plus-mean idiom so you are not
retyping the transpose every time:

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_fdata(fd, ax=None, color="#3f51b5", show_mean=True, **kw):
    """Plot every curve in an Fdata, optionally with its pointwise mean."""
    ax = ax or plt.gca()
    t = np.asarray(fd.argvals)
    data = np.asarray(fd.data)
    ax.plot(t, data.T, color=color, lw=1, alpha=0.35, **kw)
    if show_mean:
        ax.plot(t, data.mean(axis=0), color=color, lw=2.6)
    ax.set(xlabel="t", ylabel="X(t)")
    return ax
```

---

## Next Steps

- [Depth Functions](../represent/depth-functions.md) -- the depth measures that
  drive the functional-median highlight.
- [Working with Derivatives](derivatives.md) -- velocity/acceleration curves and
  true phase-plane plots.
- [Outlier Detection](../analyze/outlier-detection.md) -- functional boxplots and
  outliergrams built on the same depth values.
- [Simulation Toolbox](simulation.md) -- generate the curve families you plot.
