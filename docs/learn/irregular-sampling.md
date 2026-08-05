---
title: Irregular / Sparse Sampling
---

# Working with Irregular / Sparsely Sampled Functional Data

Textbook functional data arrives as a tidy `(n_obs, n_points)` matrix: every
curve observed at the *same* grid of points. Real data rarely obliges. Growth
studies measure children at whatever ages they happened to visit the clinic;
sensors drop samples; longitudinal records are sparse and misaligned. Each curve
then lives on its **own** grid, and the neat matrix disappears.

`Fdata` -- and every pointwise operation built on it (means, distances, depth,
FPCA) -- assumes a shared grid. This guide shows why, and how to recover one:
smooth each curve onto a common grid with kernel smoothers or a basis
expansion, then proceed as usual.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate

t_fine = np.linspace(0, 1, 200)
truth = np.asarray(simulate(n=4, argvals=t_fine, n_basis=5, seed=7))
rng = np.random.default_rng(0)

f, ax = fig()
for i, col in enumerate(["#3f51b5", "#e8710a", "#198754", "#6f42c1"]):
    m = rng.integers(10, 18)                       # each curve, different count...
    ti = np.sort(rng.uniform(0, 1, size=m))        # ...on its own irregular grid
    yi = np.interp(ti, t_fine, truth[i]) + rng.normal(0, 0.12, size=m)
    ax.plot(ti, yi, "o-", color=col, lw=0.8, ms=5, alpha=0.8)
ax.set(title="Four curves, four different sparse grids",
       xlabel="t", ylabel="X(t)")
print(render(f))
```

---

## Why pointwise operations need a common grid

The pointwise mean $\bar{X}(t) = \frac{1}{n}\sum_i X_i(t)$ is only defined if
every $X_i$ is evaluated at the *same* $t$. With curve $i$ observed at grid
$\{t^{(i)}_1, \dots, t^{(i)}_{m_i}\}$ and curve $j$ at a different grid, the sum
$X_i(t) + X_j(t)$ has no meaning at a shared column -- the columns do not line
up, and $m_i \neq m_j$ so they cannot even be stacked into a rectangle.

Everything downstream inherits this requirement:

| Operation | Why it needs a common grid |
|-----------|-----------------------------|
| Pointwise mean / centering | sums curves column-by-column |
| $L^p$ distances / depth | compares $X_i(t)$ to $X_j(t)$ at each $t$ |
| FPCA | eigen-decomposes a `(n_points, n_points)` covariance |
| Basis smoothing of a *batch* | one `(n_obs, n_points)` matrix in, one out |

The fix is always the same: **reconstruct each curve as a smooth function, then
evaluate all reconstructions on one shared grid.** This is a modelling step, not
mere interpolation -- it borrows the smoothness assumption of FDA to fill the
gaps between sparse observations.

$$
X_i(t) \;\approx\; \hat{m}_i(t), \qquad
\text{then sample } \hat{m}_i \text{ on the common grid } t_1, \dots, t_M .
$$

---

## Smoothing onto a common grid: kernel smoothers

The kernel smoothers in `fdars.smoothing` are the natural tool: they take the
*observed* points `(x, y)` and a *target* grid `x_new`, and return the fit at
`x_new`. Because `x` and `x_new` are independent, a single call moves a curve
from its own sparse grid onto any common grid you choose.

```python
from fdars.smoothing import nadaraya_watson, local_linear, optim_bandwidth

bw = optim_bandwidth(ti, yi)["h_opt"]              # GCV-select on this curve
y_common = nadaraya_watson(ti, yi, common_grid, bandwidth=bw)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | `np.ndarray` `(m,)` | the curve's own (irregular) grid |
| `y` | `np.ndarray` `(m,)` | observed, possibly noisy values |
| `x_new` | `np.ndarray` `(M,)` | shared target grid for **all** curves |
| `bandwidth` | `float` | smoothing bandwidth (from `optim_bandwidth`) |
| `kernel` | `str` | `"gaussian"`, `"epanechnikov"`, `"tricube"` |

Below, one sparse noisy curve is reconstructed on a dense common grid. Note that
`optim_bandwidth` chooses the bandwidth per curve, so sparser curves get more
smoothing automatically:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.smoothing import nadaraya_watson, local_linear, optim_bandwidth

t_fine = np.linspace(0, 1, 200)
truth = np.asarray(simulate(n=1, argvals=t_fine, n_basis=5, seed=7))[0]

rng = np.random.default_rng(1)
ti = np.sort(rng.uniform(0, 1, size=22))           # sparse, irregular grid
yi = np.interp(ti, t_fine, truth) + rng.normal(0, 0.15, size=22)

common = np.linspace(0, 1, 200)                     # shared target grid
bw = optim_bandwidth(ti, yi)["h_opt"]
y_nw = np.asarray(nadaraya_watson(ti, yi, common, bandwidth=bw))
y_ll = np.asarray(local_linear(ti, yi, common, bandwidth=bw))

f, ax = fig()
ax.plot(t_fine, truth, color="#198754", lw=2.0, alpha=0.7, label="true signal")
ax.scatter(ti, yi, s=32, color="#6c757d", zorder=3, label="sparse observations")
ax.plot(common, y_nw, color="#3f51b5", lw=2.2, label=f"Nadaraya-Watson (h={bw:.3f})")
ax.plot(common, y_ll, color="#e8710a", lw=2.0, ls="--", label="local linear")
ax.set(title="Sparse points reconstructed on a common grid",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

!!! info "Local linear near the boundaries"
    On sparse grids the ends of the domain are the weakest spot -- few points to
    average. `local_linear` corrects the boundary bias that `nadaraya_watson`
    suffers there, so it is usually the safer default for sparse data. See
    [Smoothing](smoothing.md) for the full comparison.

---

## Regridding a whole sample

Once you can move one curve, regridding the sample is a loop that stacks the
reconstructions into the `(n_obs, M)` matrix `Fdata` wants. After this step the
data is rectangular and every pointwise operation is valid again.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars import Fdata
from fdars.simulation import simulate
from fdars.smoothing import nadaraya_watson, optim_bandwidth

t_fine = np.linspace(0, 1, 200)
truth = np.asarray(simulate(n=20, argvals=t_fine, n_basis=5, seed=7))
rng = np.random.default_rng(3)

common = np.linspace(0, 1, 120)                    # one grid to rule them all
recon = np.empty((truth.shape[0], common.size))
for i in range(truth.shape[0]):
    m = rng.integers(15, 30)                       # each curve: its own sparse grid
    ti = np.sort(rng.uniform(0, 1, size=m))
    yi = np.interp(ti, t_fine, truth[i]) + rng.normal(0, 0.12, size=m)
    bw = optim_bandwidth(ti, yi)["h_opt"]
    recon[i] = nadaraya_watson(ti, yi, common, bandwidth=bw)

fd = Fdata(recon, argvals=common)                  # now a valid Fdata
mu = np.asarray(fd.mean())                         # pointwise mean is defined again

f, ax = fig()
ax.plot(common, recon.T, color="#3f51b5", lw=1, alpha=0.35)
ax.plot(common, mu, color="#e8710a", lw=2.8, label="pointwise mean")
ax.set(title="20 sparse curves regridded, with their mean",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

!!! tip "Choose the common grid deliberately"
    A common grid finer than your typical per-curve sampling wastes nothing, but
    do not extrapolate: keep the grid inside the range actually covered by each
    curve's observations, or the reconstruction at the edges is a guess.

---

## Basis smoothing onto a common grid

Kernel smoothers evaluate wherever you ask, which makes regridding trivial. A
**basis expansion** takes a slightly different route: `fdars.basis` first fits
coefficients on the observed grid, and you then *evaluate the same
coefficients on the common grid*. The two-step pair is:

- `fdata_to_basis_1d(y, ti, n_basis, basis_type)` -> `(coefficients, n_basis)`
  fits a B-spline (or Fourier) expansion to the sparse observations.
- `basis_to_fdata_1d(coefficients, common, n_basis, basis_type)` evaluates that
  expansion on **any** grid -- here the shared one.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.basis import fdata_to_basis_1d, basis_to_fdata_1d

t_fine = np.linspace(0, 1, 200)
truth = np.asarray(simulate(n=1, argvals=t_fine, n_basis=5, seed=7))[0]

rng = np.random.default_rng(1)
ti = np.sort(rng.uniform(0, 1, size=22))
yi = np.interp(ti, t_fine, truth) + rng.normal(0, 0.15, size=22)

common = np.linspace(0, 1, 200)

# 1. fit coefficients on the sparse, irregular grid
coef, nb = fdata_to_basis_1d(yi[None, :], ti, n_basis=10, basis_type="bspline")
# 2. evaluate the fitted expansion on the common grid
recon = np.asarray(basis_to_fdata_1d(np.asarray(coef), common, nb, basis_type="bspline"))[0]

f, ax = fig()
ax.plot(t_fine, truth, color="#198754", lw=2.0, alpha=0.7, label="true signal")
ax.scatter(ti, yi, s=32, color="#6c757d", zorder=3, label="sparse observations")
ax.plot(common, recon, color="#6f42c1", lw=2.4, label="B-spline reconstruction")
ax.set(title="Basis reconstruction of a sparse curve on a common grid",
       xlabel="t", ylabel="X(t)")
ax.legend()
print(render(f))
```

| Function | Purpose | Key arguments |
|----------|---------|---------------|
| `fdata_to_basis_1d` | fit coefficients to observed points | `data`, `argvals`, `n_basis`, `basis_type` |
| `basis_to_fdata_1d` | evaluate coefficients on a target grid | `coefficients`, `argvals`, `n_basis`, `basis_type` |
| `pspline_fit_1d` | penalized fit *at the observed grid* | `data`, `argvals`, `n_basis`, `lambda_`, `order` |
| `fourier_fit_1d` | Fourier fit *at the observed grid* | `data`, `argvals`, `nbasis` |

!!! note "`pspline_fit_1d` / `fourier_fit_1d` return the fit on the input grid"
    These convenience fitters return `fitted` **at the same `argvals` you pass
    in**, so they denoise a curve in place but do not, by themselves, move it to
    a new grid. To regrid with a penalized fit, take the `coefficients` they
    return and feed them to `basis_to_fdata_1d` on the common grid -- exactly the
    two-step pattern above. For a periodic signal swap `basis_type="fourier"`.

Basis smoothing shines when you want the same expansion for a *whole batch* of
curves that already share a grid (`smooth_basis_gcv` does the batch fit with an
automatically chosen penalty -- see [Smoothing](smoothing.md)). For genuinely
sparse data on *different* grids, fit each curve's coefficients separately as
above, then evaluate them all on the common grid.

---

## Kernel vs. basis: which to reach for

| | Kernel smoothers | Basis expansion |
|---|---|---|
| Regrids directly? | yes -- `x_new` is a free grid | via `fdata_to_basis_1d` -> `basis_to_fdata_1d` |
| Very sparse curves | robust, `local_linear` fixes edges | needs `n_basis` below the point count |
| Derivatives afterwards | use `local_polynomial(degree=2)` | differentiate the basis fit |
| Periodic data | any kernel | `basis_type="fourier"` |
| Cost per curve | one GCV bandwidth search | one linear solve |

A practical default: `local_linear` with a GCV bandwidth for regridding sparse,
noisy curves; switch to a Fourier basis when the signal is periodic, or to
B-splines when you need coefficients for a downstream model.

---

## Next Steps

- [Smoothing](smoothing.md) -- the full menu of kernel and basis smoothers, and
  automatic bandwidth / penalty selection.
- [Basis Representation](../represent/basis-representation.md) -- what the
  B-spline and Fourier coefficients mean.
- [Custom Plotting](custom-plotting.md) -- visualise raw sparse points against
  the smoothed reconstruction.
- [Introduction to fdars](introduction.md) -- the `Fdata` container the common
  grid feeds into.
