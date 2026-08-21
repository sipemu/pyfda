# PACE — FPCA for Sparse, Irregular Data

PACE (Principal Analysis by Conditional Expectation) extends functional PCA to the realistic setting where each curve is observed at its **own sparse, irregular grid** — not on a shared dense grid. Clinical longitudinal studies, sensor networks with missed readings, and ecological monitoring data all produce this kind of input. Standard FPCA requires a common grid and breaks when curves have different numbers of observations at different locations. PACE handles it correctly.

The key idea: PACE first estimates the population mean and covariance surface nonparametrically from all available observation pairs, then recovers individual FPC scores via conditional expectation given the sparse observations. The result is a set of **smooth eigenfunctions** on a common work grid, plus scores and fitted curves for every observation — even those with only a handful of measurement points.

![PACE FPCA — sparse irregular observations recovered as smooth eigenfunctions](../assets/diagrams/pace-fpca.svg){ .fdars-diagram }

## Theory

Every square-integrable random function $X_i(t)$ admits the Karhunen-Loève expansion

$$
X_i(t) = \mu(t) + \sum_{k=1}^{\infty} \xi_{ik}\,\phi_k(t)
$$

where $\mu(t)$ is the population mean, $\phi_k(t)$ the $k$-th eigenfunction of the covariance operator, and $\xi_{ik}$ the corresponding score. With dense, regular observations we estimate the covariance directly from the data matrix. With sparse, irregular observations we cannot: different curves are observed at different time points, so the sample covariance matrix is largely missing.

PACE estimates the covariance surface $C(s,t)$ by local linear smoothing of all cross-product pairs $(X_i(s_j),\, X_i(t_k))$ at distinct time pairs $(s_j, t_k)$ within each curve, pooled across curves. The diagonal (measurement error) is handled separately. Eigen-decomposition of the estimated surface yields $\hat\phi_k$ and $\hat\lambda_k$ on the common work grid.

Scores are then recovered by conditional expectation:

$$
\hat\xi_{ik} = \hat\lambda_k\,\hat\phi_k^\top \boldsymbol{\Sigma}_i^{-1}\bigl(\mathbf{y}_i - \hat\boldsymbol{\mu}_i\bigr)
$$

where $\mathbf{y}_i$ is the vector of observed values for curve $i$, $\hat\boldsymbol{\mu}_i$ is the mean evaluated at those time points, and $\boldsymbol{\Sigma}_i = \hat\lambda_k\hat\phi_k\hat\phi_k^\top + \hat\sigma^2 I$ is the marginal covariance at the observed locations.

### `irreg_fdata_from_lists` — building the sparse input handle

| Parameter | Type | Description |
|---|---|---|
| `argvals_list` | `list[ndarray (n_i,)]` | List of 1-D arrays — evaluation grid for curve $i$ (ragged; lengths may differ) |
| `values_list` | `list[ndarray (n_i,)]` | List of 1-D arrays — observed values for curve $i$ (must match `argvals_list[i]` in length) |

Returns an opaque `PyIrregFdata` handle for use with `pace_fpca`.

!!! warning "2-D numpy arrays are rejected"
    `irreg_fdata_from_lists` requires **two Python lists of 1-D arrays** — one list per curve for the grid and one for the values. Passing a dense 2-D numpy array `(n, m)` raises a `ValueError`. Build the lists explicitly before calling the function.

### `pace_fpca` — fitting PACE-FPCA

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `PyIrregFdata` | — | Handle from `irreg_fdata_from_lists` |
| `ncomp` | `int` | `3` | Number of principal components to request |
| `bandwidth` | `float` | `0.1` | Kernel bandwidth for covariance surface smoothing; increase for sparser data (≥ 0.15 recommended for data on [0, 1] with few points per curve) |
| `sigma2` | `float` | `0.01` | Measurement error variance; increase if observations are noisy |
| `work_grid` | `list[float] \| None` | `None` | Evaluation grid for mean and eigenfunctions; `None` → 51 uniformly spaced points on [0, 1] |
| `alpha` | `float` | `0.05` | Significance level for pointwise confidence bands |

### Returns

| Key | Shape | Description |
|---|---|---|
| `mean` | `(m,)` | Estimated mean function on the work grid |
| `eigenvalues` | `(ncomp,)` | Eigenvalues $\hat\lambda_1 \ge \hat\lambda_2 \ge \cdots$ |
| `eigenfunctions` | `(m, ncomp)` | Estimated eigenfunctions; **column $k$ is the $k$-th eigenfunction** $\hat\phi_{k+1}(t)$ |
| `scores` | `(n, ncomp)` | Conditional-expectation FPC scores $\hat\xi_{ik}$ |
| `fitted` | `(n, m)` | Fitted curves $\hat\mu(t) + \sum_k \hat\xi_{ik}\hat\phi_k(t)$ on the work grid |
| `fitted_lower` | `(n, m)` | Lower pointwise confidence band for each fitted curve |
| `fitted_upper` | `(n, m)` | Upper pointwise confidence band for each fitted curve |
| `argvals` | `(m,)` | Work grid used for all function evaluations |
| `sigma2` | `float` | Estimated measurement error variance (may differ from the input if re-estimated) |
| `ncomp` | `int` | **Actual** number of components retained (may be less than requested if the covariance estimate has fewer positive eigenvalues) |

!!! note "Actual component count"
    The `ncomp` value in the returned dict is the **actual** count of components retained and may be less than the requested `ncomp` parameter. Always read `res["ncomp"]` to determine the true length of the `eigenvalues` array and the number of columns in `eigenfunctions` and `scores`.

## Example — synthetic sparse irregular data

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
import fdars.pace_fpca as pf

rng = np.random.default_rng(42)
n = 15  # sparse curves; each has only 5-8 observations

# Build ragged per-curve grids: different number of points, different positions per curve
argvals_list = [np.sort(rng.uniform(0, 1, rng.integers(5, 9))) for _ in range(n)]
values_list  = [np.sin(2 * np.pi * av) + rng.normal(0, 0.15, len(av))
                for av in argvals_list]

# IMPORTANT: pass Python lists of 1-D arrays — NOT a 2-D numpy array
handle = pf.irreg_fdata_from_lists(argvals_list, values_list)
res = pf.pace_fpca(handle, ncomp=2, bandwidth=0.2, sigma2=0.05)

ef = np.asarray(res["eigenfunctions"])   # shape (m, ncomp) — column k is PC k
argvals_out = np.asarray(res["argvals"]) # common work grid

f, (a0, a1) = fig(1, 2, figsize=(11.0, 3.8))

# Left: scatter sparse observations per curve + PACE mean
for av, vl in zip(argvals_list, values_list):
    a0.scatter(av, vl, s=18, color="#3f51b5", alpha=0.45)
a0.plot(argvals_out, np.asarray(res["mean"]), color="#e8710a", lw=2.4, label="PACE mean")
a0.set(title=f"Sparse irregular observations (n={n}, ragged grids)", xlabel="t")
a0.legend(fontsize=9)

# Right: recovered smooth eigenfunctions on common work grid
a1.plot(argvals_out, ef[:, 0], color="#3f51b5", lw=2.4, label="PC 1")
a1.plot(argvals_out, ef[:, 1], color="#e8710a", lw=2.4, label="PC 2")
a1.axhline(0, color="#ced4da", lw=0.8, ls="--")
a1.set(title="PACE eigenfunctions recovered on work grid", xlabel="t")
a1.legend(fontsize=9)

print(render(f))
print(f"actual ncomp={res['ncomp']}  scores shape={np.asarray(res['scores']).shape}")
print("FDARS_FENCE_OK")
```

## References

1. Yao, F., Müller, H.-G. & Wang, J.-L. (2005). Functional data analysis for sparse longitudinal data. *Journal of the American Statistical Association*, 100(470), 577–590.
2. Hall, P., Müller, H.-G. & Wang, J.-L. (2006). Properties of principal component methods for functional and longitudinal data analysis. *The Annals of Statistics*, 34(3), 1493–1517.
