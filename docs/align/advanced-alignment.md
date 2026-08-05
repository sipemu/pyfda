# Advanced Elastic Alignment

The basic [`elastic_align_pair`](elastic-alignment.md#pairwise-alignment) finds the warp that minimizes the elastic distance between two curves with a single smoothness knob, `lambda_`. Real problems often need more: closed curves whose parameterization has no fixed start, warps pinned to known landmarks, penalties that control *what kind* of warp is allowed, or a coarse-to-fine solver for long grids. `fdars` provides a family of pairwise aligners for exactly these cases, plus `lambda_cv` to pick the regularization strength by cross-validation instead of by hand.

The figure below shows the central trade-off these variants control: how the regularization parameter $\lambda$ moves the estimated warp between an unconstrained fit and the identity.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.alignment import elastic_align_pair_penalized

t = np.linspace(0, 1, 120)
base = np.exp(-((t - 0.4) ** 2) / 0.01) + 0.7 * np.exp(-((t - 0.75) ** 2) / 0.006)
warp = t ** 1.5
warp = (warp - warp.min()) / np.ptp(warp)
target = base                         # reference
source = np.interp(t, warp, base)     # phase-shifted curve to register

f, ax = fig()
colors = {"0.0": "#dc3545", "0.05": "#e8710a", "0.5": "#198754", "5.0": "#6f42c1"}
for lam_s, c in colors.items():
    res = elastic_align_pair_penalized(source, target, t, lambda_=float(lam_s))
    label = {"0.0": "under (λ=0)", "0.05": "well (λ=0.05)",
             "0.5": "strong (λ=0.5)", "5.0": "over (λ=5)"}[lam_s]
    ax.plot(t, np.asarray(res["gamma"]), color=c, lw=1.8, label=label)
ax.plot([0, 1], [0, 1], color="#6c757d", lw=1.3, ls="--", label="identity")
ax.set(title="Warp $\\gamma$ vs. penalty $\\lambda$", xlabel="t",
       ylabel="$\\gamma(t)$", aspect="equal")
ax.legend(fontsize=8)
print(render(f))
```

As $\lambda$ grows the warp is pulled toward the diagonal: too small and it over-fits noise, too large and it collapses to the identity (no alignment). The variants below differ in *how* they constrain or penalize this warp.

---

## Concepts

Every pairwise aligner minimizes an elastic objective in SRSF space,

$$
\gamma^\* \;=\; \arg\min_{\gamma}\;\big\lVert q_1 - (q_2 \circ \gamma)\sqrt{\dot\gamma}\,\big\rVert_{L^2}^2 \;+\; \lambda\,\mathcal{P}(\gamma),
$$

where $q_i$ is the SRSF of curve $i$ and $\mathcal{P}(\gamma)$ is a roughness penalty. The variants change one piece each:

- **Closed** aligners additionally optimize over a starting-point rotation, because a closed curve has no canonical origin.
- **Constrained** aligners require $\gamma$ to map specified source landmarks exactly onto target landmarks, combining hard landmark matching with elastic optimization elsewhere.
- **Penalized** aligners let you pick the form of $\mathcal{P}$ (first- vs. second-order roughness), shaping the character of admissible warps.
- **Multiresolution** aligners solve on a coarsened grid first, then refine -- faster and more robust on long, wiggly curves.

---

## Pairwise variants

### Unconstrained

The baseline. Returns the aligned curve, the warp, and the elastic distance.

```python
import numpy as np
from fdars.alignment import elastic_align_pair

t = np.linspace(0, 1, 101)
f1 = np.sin(2 * np.pi * t)
f2 = np.sin(2 * np.pi * (t - 0.1))

res = elastic_align_pair(f2, f1, t, lambda_=0.0)
f_aligned = res["f_aligned"]   # (m,)  f2 warped onto f1
gamma     = res["gamma"]       # (m,)  optimal warp
distance  = res["distance"]    # float
```

### Closed curves

For periodic or closed curves, `elastic_align_pair_closed` also searches over the parameterization start, returning the optimal cyclic offset alongside the warp.

```python
from fdars.alignment import elastic_align_pair_closed

res = elastic_align_pair_closed(f1, f2, t, lambda_=0.0)
rotation = res["optimal_rotation"]   # cyclic start-point offset
gamma    = res["gamma"]
distance = res["distance"]
```

| Key | Type | Description |
|-----|------|-------------|
| `f_aligned` | `ndarray (m,)` | `f2` aligned to `f1` |
| `gamma` | `ndarray (m,)` | Optimal warp |
| `distance` | `float` | Elastic distance after alignment |
| `optimal_rotation` | `float`/`int` | Best cyclic start-point offset |

### Landmark-constrained

When you already know that specific features must correspond (e.g. a shared peak), pin them. The warp is forced through the given `(source, target)` landmark pairs and optimized elastically between them.

```python
import numpy as np
from fdars.alignment import elastic_align_pair_constrained

# landmark arrays MUST be ndarrays (a Python list raises TypeError)
src = np.array([0.55])   # landmark location in f2
tgt = np.array([0.50])   # where it should map to in f1

res = elastic_align_pair_constrained(f1, f2, t, tgt, src, lambda_=0.0)
gamma = res["gamma"]     # satisfies gamma(src) = tgt at the knots
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `f1`, `f2` | `ndarray (m,)` | Target and source curves |
| `argvals` | `ndarray (m,)` | Evaluation grid |
| `landmark_targets` | `ndarray (k,)` | Target landmark locations (must be `ndarray`) |
| `landmark_sources` | `ndarray (k,)` | Source landmark locations (must be `ndarray`) |
| `lambda_` | `float` | Warp regularization |

!!! note "For automatic, whole-dataset landmark warping"
    `elastic_align_pair_constrained` pins landmarks within an *elastic* pairwise fit. If you instead want a pure monotone time-warp that only maps landmarks to a common target (no elastic optimization), see [Landmark Registration](landmark-registration.md).

### Penalized

Choose the penalty functional. `first_order` penalizes the warp's departure from the identity in slope; `second_order` penalizes curvature (favoring smoother, gently bending warps). `second_order_weight` blends the two.

```python
from fdars.alignment import elastic_align_pair_penalized

res = elastic_align_pair_penalized(
    f2, f1, t,
    lambda_=0.1,
    penalty_type="second_order",   # or "first_order"
    second_order_weight=0.1,
)
gamma = res["gamma"]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `lambda_` | `float` | Overall penalty strength |
| `penalty_type` | `str` | `"first_order"` (default) or `"second_order"` |
| `second_order_weight` | `float` | Weight on the curvature term (default `0.1`) |

### Multiresolution

Solve coarse-to-fine. The curve is coarsened by `coarsen_factor`, aligned, then refined over `n_refine_steps` gradient steps. This is faster and less prone to local minima on long, oscillatory curves.

```python
from fdars.alignment import elastic_align_pair_multires

res = elastic_align_pair_multires(
    f2, f1, t,
    coarsen_factor=4,
    n_refine_steps=10,
    step_size=0.01,
    lambda_=0.0,
)
gamma = res["gamma"]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `coarsen_factor` | `int` | Grid downsampling factor for the coarse solve (default `4`) |
| `n_refine_steps` | `int` | Gradient refinement steps (default `10`) |
| `step_size` | `float` | Refinement step size (default `0.01`) |
| `lambda_` | `float` | Warp regularization |

All four variants return at least `f_aligned`, `gamma`, and `distance`; `closed` adds `optimal_rotation`.

---

## Choosing $\lambda$ by cross-validation

Rather than guessing, `lambda_cv` scores a grid of regularization values by $K$-fold cross-validation over the whole dataset and reports the best one.

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

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Sample of curves |
| `argvals` | `ndarray (m,)` | Evaluation grid |
| `lambdas` | `ndarray` | Candidate values (must be `ndarray`; `None` uses a default grid) |
| `n_folds` | `int` | Number of CV folds (default `5`) |
| `max_iter` | `int` | Karcher-mean iterations per fit (default `15`) |
| `tol` | `float` | Convergence tolerance (default `1e-3`) |
| `seed` | `int` | Fold-splitting seed (default `42`) |

| Key | Type | Description |
|-----|------|-------------|
| `best_lambda` | `float` | Regularization minimizing the CV score |
| `cv_scores` | `ndarray` | Mean CV score for each candidate |
| `lambdas` | `ndarray` | The candidate grid that was scored |

!!! tip "Feed the result straight into alignment"
    Use `best_lambda` as the `lambda_` argument to `karcher_mean` or any pairwise variant. Values that are too small over-fit phase noise; too large and the warps collapse to the identity, defeating alignment.

!!! warning "Landmark arrays must be `ndarray`"
    `elastic_align_pair_constrained` and `lambda_cv` reject plain Python lists for their array arguments (`landmark_targets`, `landmark_sources`, `lambdas`) with a `TypeError`. Wrap them with `np.array(...)`.

See [Elastic Alignment](elastic-alignment.md) for the baseline aligner and Karcher mean, [TSRVF](tsrvf.md) for linearized statistics, and [Comparing Alignment Methods](alignment-comparison.md) for how these fits stack up against landmark registration.
