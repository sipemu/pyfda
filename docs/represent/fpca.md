# Functional PCA

Functional Principal Component Analysis (FPCA) is the workhorse of functional data analysis. It decomposes a sample of curves into a mean function plus a linear combination of orthogonal eigenfunctions, providing an optimal low-rank approximation of the covariance structure.

## The Karhunen-Loeve decomposition

Every square-integrable random function $X_i(t)$ with finite second moments admits the expansion

$$
X_i(t) = \mu(t) + \sum_{k=1}^{\infty} \xi_{ik}\,\phi_k(t)
$$

where

| Symbol | Meaning |
|--------|---------|
| $\mu(t)$ | Population mean function |
| $\phi_k(t)$ | $k$-th eigenfunction (functional principal component) |
| $\xi_{ik}$ | $k$-th score for observation $i$, with $\mathrm{E}[\xi_{ik}]=0$, $\mathrm{Var}(\xi_{ik})=\lambda_k$ |
| $\lambda_1 \ge \lambda_2 \ge \cdots$ | Eigenvalues (variance explained by each component) |

In practice the sum is truncated at $K$ components, giving the best rank-$K$ approximation in $L^2$.

The figure below decomposes a sample of curves: the mean function $\hat\mu(t)$ plus the leading eigenfunctions $\phi_k(t)$, each scaled by $2\sqrt{\lambda_k}$ to show the mode of variation it captures.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.regression import fpca

t = np.linspace(0, 1, 150)
X = np.asarray(simulate(n=60, argvals=t, n_basis=5, efun_type="fourier", seed=7))
res = fpca(X, t, n_comp=3)
mean = np.asarray(res["mean"])
rot = np.asarray(res["rotation"])
sv = np.asarray(res["singular_values"])
ev = sv ** 2 / (X.shape[0] - 1)

f, (a0, a1) = fig(1, 2, figsize=(10, 3.8))
a0.plot(t, X.T, color="#3f51b5", lw=0.8, alpha=0.25)
a0.plot(t, mean, color="#dc3545", lw=2.4, label="mean $\\hat\\mu(t)$")
a0.set(title="60 curves and their mean", xlabel="t", ylabel="X(t)")
a0.legend()

for k in range(3):
    a1.plot(t, mean + 2 * np.sqrt(ev[k]) * rot[:, k], lw=1.8,
            label=f"$\\phi_{{{k+1}}}$ ({ev[k]/ev.sum()*100:.0f}%)")
a1.plot(t, mean, color="#6c757d", lw=1.2, ls="--", label="mean")
a1.set(title="Modes of variation $\\hat\\mu + 2\\sqrt{\\lambda_k}\\,\\phi_k$",
       xlabel="t", ylabel="X(t)")
a1.legend()
print(render(f))
```

## Quick start

FPCA lives in the **regression** module because principal component scores are the primary features for scalar-on-function regression.

```python
from fdars.regression import fpca
```

The function signature is:

```python
result = fpca(data, argvals, n_comp=3)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `np.ndarray` (n, m) | Discretized curves -- $n$ observations at $m$ grid points |
| `argvals` | `np.ndarray` (m,) | The common evaluation grid, e.g. `np.linspace(0, 1, 100)` |
| `n_comp` | `int` | Number of principal components to retain (default 3) |

**Returns** a `dict` with keys:

| Key | Shape | Description |
|-----|-------|-------------|
| `scores` | (n, n_comp) | FPC scores $\xi_{ik}$ |
| `rotation` | (m, n_comp) | Eigenfunctions $\phi_k(t)$ evaluated on the grid |
| `singular_values` | (n_comp,) | Singular values from the SVD |
| `mean` | (m,) | Sample mean function $\hat\mu(t)$ |
| `centered` | (n, m) | Mean-centered data |
| `weights` | (m,) | Quadrature weights used for the $L^2$ inner product |

## Complete working example

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate
from fdars.regression import fpca

# --- 1. Simulate 80 curves on a fine grid ---------------------------------
np.random.seed(42)
argvals = np.linspace(0, 1, 200)
data = simulate(n=80, argvals=argvals, n_basis=5, efun_type="fourier",
                eval_type="linear", seed=42)
fd = Fdata(data, argvals=argvals)

# --- 2. Run FPCA keeping 4 components ------------------------------------
result = fpca(fd.data, fd.argvals, n_comp=4)

print("Score matrix shape:", result["scores"].shape)      # (80, 4)
print("Eigenfunction shape:", result["rotation"].shape)    # (200, 4)
print("Singular values:", result["singular_values"])
```

## Variance explained and scree plots

The singular values returned by `fpca` relate to the eigenvalues (variance per component) by

$$
\lambda_k = \frac{s_k^2}{n - 1}
$$

where $s_k$ is the $k$-th singular value and $n$ is the number of observations. The proportion of variance explained (PVE) by the first $K$ components is

$$
\text{PVE}(K) = \frac{\sum_{k=1}^{K} \lambda_k}{\sum_{k=1}^{K_{\max}} \lambda_k}
$$

### Scree plot example

```python
import matplotlib.pyplot as plt

sv = result["singular_values"]
eigenvalues = sv ** 2 / (fd.data.shape[0] - 1)
pve = np.cumsum(eigenvalues) / np.sum(eigenvalues)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Individual variance
axes[0].bar(range(1, len(eigenvalues) + 1), eigenvalues, color="steelblue")
axes[0].set_xlabel("Component")
axes[0].set_ylabel("Eigenvalue")
axes[0].set_title("Scree plot")

# Cumulative PVE
axes[1].plot(range(1, len(pve) + 1), pve, "o-", color="coral")
axes[1].axhline(0.95, ls="--", color="gray", label="95 %")
axes[1].set_xlabel("Number of components")
axes[1].set_ylabel("Cumulative PVE")
axes[1].set_title("Variance explained")
axes[1].legend()

plt.tight_layout()
plt.show()
```

Running the same computation on a simulated sample produces the paired scree / cumulative-variance view below -- the elbow and the 95 % line are the two most common rules for choosing $K$.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.regression import fpca

t = np.linspace(0, 1, 150)
X = np.asarray(simulate(n=80, argvals=t, n_basis=5, efun_type="fourier", seed=7))
sv = np.asarray(fpca(X, t, n_comp=8)["singular_values"])
ev = sv ** 2 / (X.shape[0] - 1)
pve = np.cumsum(ev) / ev.sum()
ks = np.arange(1, len(ev) + 1)

f, (a0, a1) = fig(1, 2, figsize=(10, 3.8))
a0.bar(ks, ev, color="#3f51b5")
a0.set(title="Scree plot", xlabel="Component", ylabel="Eigenvalue $\\lambda_k$")

a1.plot(ks, pve, "o-", color="#e8710a")
a1.axhline(0.95, ls="--", color="#6c757d", lw=1, label="95 %")
a1.set(title="Cumulative variance explained", xlabel="Number of components",
       ylabel="PVE", ylim=(0, 1.02))
a1.legend()
print(render(f))
```

## Visualizing eigenfunctions

Each eigenfunction describes a mode of variation. Plotting $\mu(t) \pm c\,\phi_k(t)$ (where $c = 2\sqrt{\lambda_k}$) reveals how the $k$-th component deforms the mean.

```python
fig, axes = plt.subplots(1, 4, figsize=(16, 3), sharey=True)
mean = result["mean"]

for k in range(4):
    ax = axes[k]
    phi = result["rotation"][:, k]
    spread = 2 * np.sqrt(eigenvalues[k])
    ax.plot(fd.argvals, mean, "k-", label="mean")
    ax.plot(fd.argvals, mean + spread * phi, "r--", label=f"+2 SD")
    ax.plot(fd.argvals, mean - spread * phi, "b--", label=f"-2 SD")
    ax.set_title(f"PC {k + 1} ({eigenvalues[k]/eigenvalues.sum()*100:.1f} %)")
    if k == 0:
        ax.legend(fontsize=8)

plt.tight_layout()
plt.show()
```

## Score plots

FPC scores summarize each curve as a point in $\mathbb{R}^K$. Scatter plots of score pairs reveal clusters, outliers, and structure.

```python
scores = result["scores"]

fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(scores[:, 0], scores[:, 1], s=30, alpha=0.7)
ax.set_xlabel("PC 1 score")
ax.set_ylabel("PC 2 score")
ax.set_title("FPC score plot")
ax.axhline(0, color="gray", lw=0.5)
ax.axvline(0, color="gray", lw=0.5)
plt.tight_layout()
plt.show()
```

## Reconstruction and denoising

A truncated reconstruction acts as a smoother -- high-frequency noise lives in the discarded components.

```python
# Reconstruct from K components
K = 3
reconstructed = result["mean"] + result["scores"][:, :K] @ result["rotation"][:, :K].T

# Compare original vs reconstructed for one curve
idx = 0
plt.figure(figsize=(8, 3))
plt.plot(fd.argvals, fd.data[idx], "gray", alpha=0.6, label="Original")
plt.plot(fd.argvals, reconstructed[idx], "steelblue", lw=2, label=f"K={K} reconstruction")
plt.legend()
plt.title("FPCA denoising")
plt.tight_layout()
plt.show()
```

## Using FPCA for feature extraction

FPC scores are the standard features for downstream supervised learning.

```python
from fdars.regression import fregre_lm

# Suppose we have a scalar response
response = np.random.randn(80)

# Option A: let fregre_lm handle PCA internally
result_lm = fregre_lm(fd.data, response, n_comp=4)

# Option B: use pre-computed scores as features in any model
from sklearn.linear_model import LinearRegression

scores = fpca(fd.data, fd.argvals, n_comp=4)["scores"]
model = LinearRegression().fit(scores, response)
print("R^2:", model.score(scores, response))
```

## Choosing the number of components

!!! tip "Model selection"

    Use `model_selection_ncomp` from `fdars.regression` to choose $K$ via GCV, AIC, or BIC when the goal is regression:

    ```python
    from fdars.regression import model_selection_ncomp

    sel = model_selection_ncomp(fd.data, response, max_comp=10, criterion="gcv")
    print("Best K:", sel["best_ncomp"])

    # Inspect all criteria
    for ncomp, aic, bic, gcv in sel["criteria"]:
        print(f"  K={ncomp}: AIC={aic:.2f}, BIC={bic:.2f}, GCV={gcv:.4f}")
    ```

When the goal is pure representation (no response), a common rule is to retain enough components to explain at least 95 % of variance, or to look for an "elbow" in the scree plot.

## FPCA on smoothed data

Smoothing before FPCA often improves results, especially with noisy data. Use P-splines or basis smoothing first:

```python
from fdars.basis import pspline_fit_gcv

# Smooth with GCV-selected P-splines
smooth = pspline_fit_gcv(fd.data, fd.argvals, n_basis=25)
fd_smooth = Fdata(smooth["fitted"], argvals=fd.argvals)

# Then run FPCA on the smoothed curves
result_smooth = fpca(fd_smooth.data, fd_smooth.argvals, n_comp=4)
```

!!! note "FPCA in the alignment module"

    For data with significant phase variation (horizontal shifts), consider **elastic FPCA** via `vert_fpca`, `horiz_fpca`, or `joint_fpca` from `fdars.alignment`. These separate amplitude and phase variation before extracting components. See the [Elastic Alignment](../align/elastic-alignment.md) guide.

## API summary

| Function | Module | Purpose |
|----------|--------|---------|
| `fpca(data, argvals, n_comp)` | `fdars.regression` | Standard FPCA |
| `model_selection_ncomp(data, response, ...)` | `fdars.regression` | Cross-validated component selection |
| `vert_fpca(data, argvals, n_comp, ...)` | `fdars.alignment` | Amplitude FPCA (elastic) |
| `horiz_fpca(data, argvals, n_comp, ...)` | `fdars.alignment` | Phase FPCA (elastic) |
| `joint_fpca(data, argvals, n_comp, ...)` | `fdars.alignment` | Joint amplitude-phase FPCA |
