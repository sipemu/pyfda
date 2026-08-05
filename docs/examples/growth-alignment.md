# Growth curve alignment

**Dataset:** Berkeley Growth Study — heights of 39 boys and 54 girls measured
at 31 ages between 1 and 18 years.

The pubertal growth spurt is the defining feature of a child's height
trajectory, but it happens at a *different age* for every child. If we simply
average the raw curves, the spurts land at different times and cancel out,
blurring the very feature we care about. This is **phase variation**, and it is
exactly what elastic alignment is built to separate from **amplitude
variation** (how big each spurt is).

This case study works with **growth velocity** — the derivative of height with
respect to age — where the spurt shows up as a sharp peak, and aligns the
velocity curves with `fdars.alignment`.

## Growth velocity curves

We differentiate each height curve with `fdars.fdata.deriv_1d` to obtain
velocity (cm/year). The peak of each curve marks that child's growth spurt.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_growth
from fdars.fdata import deriv_1d

age, X, meta = load_growth()
V = np.asarray(deriv_1d(X, age, nderiv=1))     # (93, 31) velocity curves

f, ax = fig()
male = meta["sex"].to_numpy() == "male"
ax.plot(age, V[male].T, color="#3f51b5", lw=1, alpha=0.35)
ax.plot(age, V[~male].T, color="#e8710a", lw=1, alpha=0.35)
ax.plot([], [], color="#3f51b5", label="boys")
ax.plot([], [], color="#e8710a", label="girls")
ax.set(title="Growth velocity — the spurt peaks at different ages",
       xlabel="age (years)", ylabel="velocity (cm/year)")
ax.legend()
print(render(f))
```

The spurts are smeared across roughly ages 10–16. A pointwise (cross-sectional)
mean of these curves under-states the true spurt because the peaks do not line
up.

## The elastic-alignment idea

Two curves $f$ and $g$ differing only in *timing* are related by a **warping
function** $\gamma$ — a smooth, increasing bijection of the time axis — via
$g \approx f \circ \gamma$. The elastic framework compares curves through their
**square-root velocity functions (SRSF)**

$$
q(t) = \operatorname{sign}\!\big(f'(t)\big)\,\sqrt{\lvert f'(t)\rvert},
$$

and defines the distance between $f$ and $g$ as the smallest
$L^2$ distance between their SRSFs achievable over all warpings $\gamma$. The
optimal $\gamma$ is the **phase** (timing) difference; the residual SRSF
distance is the **amplitude** difference. `fdars` exposes this through
`elastic_align_pair` (pairwise) and `karcher_mean` (a template + all warpings).

## Aligning a single pair

`elastic_align_pair(curve1, curve2, argvals)` warps `curve2` onto `curve1` and
returns the aligned curve, the warping function `gamma`, and the elastic
`distance`.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_growth
from fdars.fdata import deriv_1d
from fdars.alignment import elastic_align_pair

age, X, meta = load_growth()
V = np.asarray(deriv_1d(X, age, nderiv=1))
a, b = V[60], V[70]                              # two girls, offset spurts
res = elastic_align_pair(a, b, age)
b_aligned, gamma = np.asarray(res["f_aligned"]), np.asarray(res["gamma"])

f, (ax1, ax2) = fig(1, 2, figsize=(9.5, 3.8))
ax1.plot(age, a, color="#3f51b5", lw=2, label="target")
ax1.plot(age, b, color="#e8710a", lw=2, ls="--", label="before")
ax1.plot(age, b_aligned, color="#198754", lw=2, label="after")
ax1.set(title="Velocity: before vs after warping", xlabel="age", ylabel="cm/year")
ax1.legend()
ax2.plot(age, age, color="#6c757d", lw=1, ls=":")     # identity = no warp
ax2.plot(age, gamma, color="#6f42c1", lw=2)
ax2.set(title="Warping function $\\gamma$", xlabel="age", ylabel="warped age")
print(render(f))
```

The warping function bends away from the diagonal exactly where the second
child's spurt has to be shifted to match the first; the aligned green curve now
peaks together with the blue target.

## Karcher mean: aligning the whole sample

`karcher_mean` estimates the elastic (Fréchet) mean template and, as a
by-product, warps every curve onto it. We run it on a seeded subset of 30
curves to keep the build fast.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_growth
from fdars.fdata import deriv_1d
from fdars.alignment import karcher_mean

age, X, meta = load_growth()
V = np.asarray(deriv_1d(X, age, nderiv=1))
rng = np.random.default_rng(1)
sel = np.sort(rng.choice(V.shape[0], 30, replace=False))
Vs = V[sel]

km = karcher_mean(Vs, age, max_iter=50)
aligned = np.asarray(km["aligned_data"])     # curves registered to the template
aligned_mean = aligned.mean(axis=0)          # sharpened template = mean of registered curves
xsec_mean = Vs.mean(axis=0)                   # naive cross-sectional mean of raw curves

f, (ax1, ax2) = fig(1, 2, figsize=(9.5, 3.8), sharey=True)
ax1.plot(age, Vs.T, color="#3f51b5", lw=1, alpha=0.3)
ax1.plot(age, xsec_mean, color="#dc3545", lw=2.5, label="cross-sectional mean")
ax1.set(title="Raw velocity + naive mean", xlabel="age", ylabel="cm/year")
ax1.legend()
ax2.plot(age, aligned.T, color="#198754", lw=1, alpha=0.3)
ax2.plot(age, aligned_mean, color="#e8710a", lw=2.5, label="aligned mean (template)")
ax2.set(title="Aligned velocity + template mean", xlabel="age")
ax2.legend()
print(render(f))
```

After registration the peaks stack up, so the **mean of the aligned curves**
(orange) is a sharp, tall template that tracks the registered sample — whereas
the naive cross-sectional mean of the *raw* curves (red) is lower and smeared
because it averages peaks that occur at different ages.

!!! note "Which mean to plot"
    `karcher_mean` also returns `km["mean"]`, the elastic (Fréchet) mean
    reconstructed in SRSF space. On this coarse, unequally-spaced 31-point grid
    that reconstruction does **not** converge (`km["converged"]` stays `False`
    even at large `max_iter`) and is unreliable, so we plot the pointwise mean
    of the registered curves `km["aligned_data"]` — the standard sharpened
    template. Smoothing onto a finer, regular grid first makes the SRSF
    reconstruction well-behaved. (Tracked upstream:
    [fdars-core](https://github.com/sipemu/fdars/issues).)

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `deriv_1d(data, argvals, nderiv)` | `nderiv` | Order of numerical derivative (1 = velocity, 2 = acceleration) |
| `elastic_align_pair(c1, c2, argvals, lambda_)` | `lambda_` | Roughness penalty on the warping (0 = unpenalized) |
| `karcher_mean(data, argvals, lambda_, max_iter, tol)` | `max_iter`, `tol` | Iteration budget and convergence tolerance for the template |

## See also

- [Curve alignment concepts](../align/elastic-alignment.md) for the SRSF theory.
- [FPCA & clustering of weather curves](canadian-weather.md) — the same
  amplitude/phase distinction applied to temperature.
