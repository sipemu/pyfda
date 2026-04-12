# Basis Representation

Representing functional data in a finite basis -- B-splines, Fourier, or P-splines -- converts a discrete set of evaluations into a compact coefficient vector. This enables smoothing, differentiation, integration, and dimensionality reduction, all while preserving the continuous nature of the underlying functions.

## When to use basis representations

- **Smoothing noisy data** -- P-spline penalties remove high-frequency noise while preserving shape.
- **Dimension reduction** -- a curve with 500 grid points can be faithfully captured by 15-20 basis coefficients.
- **Derivative computation** -- analytic derivatives come for free from the basis expansion.
- **Regularization** -- roughness penalties in the basis domain prevent overfitting in regression.

## B-spline vs Fourier basis

| Property | B-spline | Fourier |
|----------|----------|---------|
| Support | Local (compact) | Global |
| Best for | Non-periodic data, local features | Periodic / seasonal data |
| Boundary behavior | Handles edges naturally | Assumes periodicity |
| Derivative stability | Excellent | Excellent |
| Basis count rule of thumb | ~1 per interior knot + order | Must be odd ($2k + 1$) |

## Quick start: project and reconstruct

```python
import numpy as np
from pyfda import Fdata
from pyfda.basis import fdata_to_basis_1d, basis_to_fdata_1d

# Simulate some data
argvals = np.linspace(0, 1, 200)
data = np.column_stack([np.sin(2 * np.pi * argvals) + 0.2 * np.random.randn(200)
                        for _ in range(30)]).T  # shape (30, 200)
fd = Fdata(data, argvals=argvals)

# Project onto a B-spline basis with 15 functions
coeffs, actual_nbasis = fdata_to_basis_1d(fd.data, fd.argvals, n_basis=15,
                                           basis_type="bspline")
print(f"Coefficients shape: {coeffs.shape}")   # (30, 15)
print(f"Actual n_basis used: {actual_nbasis}")

# Reconstruct back to the evaluation grid
reconstructed = basis_to_fdata_1d(coeffs, fd.argvals, n_basis=actual_nbasis,
                                   basis_type="bspline")
print(f"Reconstructed shape: {reconstructed.shape}")  # (30, 200)
```

### Fourier basis for periodic data

```python
# Periodic data: use Fourier basis
argvals_p = np.linspace(0, 2 * np.pi, 200)
periodic_data = np.column_stack([
    np.sin(argvals_p) + 0.5 * np.cos(3 * argvals_p) + 0.15 * np.random.randn(200)
    for _ in range(30)
]).T
fd_p = Fdata(periodic_data, argvals=argvals_p)

coeffs_f, nbasis_f = fdata_to_basis_1d(fd_p.data, fd_p.argvals, n_basis=11,
                                         basis_type="fourier")
reconstructed_f = basis_to_fdata_1d(coeffs_f, fd_p.argvals, n_basis=nbasis_f,
                                     basis_type="fourier")
```

## Evaluating basis matrices directly

For advanced use (e.g., building your own penalty matrices), you can evaluate the raw basis matrix.

### B-spline basis

```python
from pyfda.basis import bspline_basis

argvals = np.linspace(0, 1, 100)
B = bspline_basis(argvals, nknots=10, order=4)
print(B.shape)  # (100, 14) -- nknots + order = 14 basis functions
```

| Parameter | Description |
|-----------|-------------|
| `argvals` | Evaluation points |
| `nknots` | Number of equally spaced interior knots |
| `order` | Spline order: 4 = cubic (default), 3 = quadratic |

### Fourier basis

```python
from pyfda.basis import fourier_basis

argvals = np.linspace(0, 2 * np.pi, 100)
F = fourier_basis(argvals, n_basis=11)
print(F.shape)  # (100, 11)
```

The Fourier basis consists of $1, \sin(\omega t), \cos(\omega t), \sin(2\omega t), \cos(2\omega t), \ldots$ where $\omega = 2\pi / T$ and $T$ is the period (range of `argvals`).

!!! info "Fourier n_basis"
    `n_basis` should be odd. If an even value is given, it will be adjusted to the next odd number so the basis contains matched sine-cosine pairs plus the constant function.

## P-spline smoothing

P-splines combine a rich B-spline basis with a discrete roughness penalty on the coefficients. The penalty parameter $\lambda$ controls the trade-off between fit and smoothness.

$$
\hat{\mathbf{c}} = \arg\min_{\mathbf{c}} \left\| \mathbf{y} - B\mathbf{c} \right\|^2 + \lambda \left\| D^d \mathbf{c} \right\|^2
$$

where $B$ is the B-spline basis matrix, $D^d$ is the $d$-th order difference matrix, and $\lambda \ge 0$.

### Fixed lambda

```python
from pyfda.basis import pspline_fit_1d

result = pspline_fit_1d(fd.data, fd.argvals, n_basis=25, lambda_=1e-2, order=2)

print(result.keys())
# dict_keys(['fitted', 'coefficients', 'edf', 'rss', 'gcv', 'aic', 'bic'])
```

| Key | Description |
|-----|-------------|
| `fitted` | Smoothed curves, shape (n, m) |
| `coefficients` | B-spline coefficients, shape (n, n_basis) |
| `edf` | Effective degrees of freedom |
| `rss` | Residual sum of squares |
| `gcv` | Generalized cross-validation score |
| `aic` | Akaike information criterion |
| `bic` | Bayesian information criterion |

### Automatic lambda via GCV

When you do not know the right smoothing level, let GCV choose:

```python
from pyfda.basis import pspline_fit_gcv

result = pspline_fit_gcv(fd.data, fd.argvals, n_basis=25, order=2)
print(f"GCV score: {result['gcv']:.6f}")
print(f"Effective degrees of freedom: {result['edf']:.1f}")
```

!!! tip "Choosing n_basis for P-splines"
    With P-splines the exact number of basis functions matters less because the penalty controls smoothness. A safe rule is to use a generous basis (e.g., 20-40 functions for 100-500 grid points) and rely on $\lambda$ to prevent overfitting.

### Comparing smoothing levels

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
idx = 0  # curve to visualize

for ax, lam in zip(axes, [1e-6, 1e-2, 1e2]):
    res = pspline_fit_1d(fd.data, fd.argvals, n_basis=25, lambda_=lam)
    ax.plot(fd.argvals, fd.data[idx], ".", ms=2, alpha=0.4, label="Raw")
    ax.plot(fd.argvals, res["fitted"][idx], "r-", lw=2,
            label=f"edf={res['edf']:.1f}")
    ax.set_title(f"$\\lambda$ = {lam:.0e}")
    ax.legend(fontsize=8)

plt.suptitle("P-spline smoothing with different penalty strengths")
plt.tight_layout()
plt.show()
```

## Automatic basis selection

`select_basis_auto_1d` jointly selects:

1. **Basis type** -- B-spline or Fourier (optionally using an FFT-based seasonality hint).
2. **Number of basis functions** -- optimizing GCV, AIC, or BIC.
3. **P-spline penalty** -- when using B-splines.

```python
from pyfda.basis import select_basis_auto_1d

selections = select_basis_auto_1d(fd.data, fd.argvals, criterion="gcv")

# Each element corresponds to one curve
for i, sel in enumerate(selections[:3]):
    print(f"Curve {i}: basis={sel['basis_type']}, nbasis={sel['nbasis']}, "
          f"score={sel['score']:.4f}, seasonal={sel['seasonal_detected']}")
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `criterion` | `"gcv"` | `"gcv"`, `"aic"`, or `"bic"` |
| `nbasis_min` | 0 (auto) | Lower bound for basis count search |
| `nbasis_max` | 0 (auto) | Upper bound for basis count search |
| `lambda_pspline` | -1.0 (auto) | P-spline penalty; negative triggers GCV selection |
| `use_seasonal_hint` | `True` | Use FFT to detect periodicity and prefer Fourier |

Each element of the returned list is a dict with:

| Key | Description |
|-----|-------------|
| `basis_type` | `"bspline"` or `"fourier"` |
| `nbasis` | Optimal number of basis functions |
| `score` | Information criterion score |
| `coefficients` | Basis coefficients for this curve |
| `fitted` | Fitted values for this curve |
| `edf` | Effective degrees of freedom |
| `seasonal_detected` | Whether the FFT hint detected periodicity |
| `lambda_val` | Selected P-spline penalty (if B-spline) |

## Cross-validated basis count

When you want to fix the basis type and only search over the number of basis functions:

```python
from pyfda.basis import basis_nbasis_cv

cv_result = basis_nbasis_cv(
    fd.data, fd.argvals,
    nbasis_min=4,
    nbasis_max=30,
    basis_type="bspline",
    criterion="gcv",
    n_folds=5,
    lambda_=1.0,
)

print(f"Optimal n_basis: {cv_result['optimal_nbasis']}")
print(f"Criterion used:  {cv_result['criterion']}")
```

### Plotting the CV curve

```python
nbasis_range = cv_result["nbasis_range"]
scores = cv_result["scores"]

plt.figure(figsize=(7, 4))
plt.plot(nbasis_range, scores, "o-", color="steelblue")
plt.axvline(cv_result["optimal_nbasis"], ls="--", color="coral",
            label=f"Optimal = {cv_result['optimal_nbasis']}")
plt.xlabel("Number of basis functions")
plt.ylabel(f"{cv_result['criterion'].upper()} score")
plt.title("Basis count selection")
plt.legend()
plt.tight_layout()
plt.show()
```

## Information criteria reference

| Criterion | Formula | Tends to select |
|-----------|---------|-----------------|
| GCV | $\displaystyle\frac{n^{-1}\,\text{RSS}}{(1 - \text{edf}/n)^2}$ | Moderate smoothness |
| AIC | $n\log(\text{RSS}/n) + 2\,\text{edf}$ | Slightly more complex models |
| BIC | $n\log(\text{RSS}/n) + \log(n)\,\text{edf}$ | Simpler (sparser) models |

!!! note "GCV vs CV"
    GCV is a leave-one-out cross-validation approximation that avoids refitting. For small samples, explicit $k$-fold CV (set `criterion="cv"` in `basis_nbasis_cv`) may be more reliable.

## Full workflow: noisy data to smooth representation

```python
import numpy as np
import matplotlib.pyplot as plt
from pyfda import Fdata
from pyfda.simulation import simulate
from pyfda.basis import pspline_fit_gcv, basis_nbasis_cv, fdata_to_basis_1d

# 1. Generate noisy data
argvals = np.linspace(0, 1, 300)
clean = simulate(n=50, argvals=argvals, n_basis=5, seed=7)
noisy = clean + 0.3 * np.random.randn(*clean.shape)
fd_noisy = Fdata(noisy, argvals=argvals)
fd_clean = Fdata(clean, argvals=argvals)

# 2. Find optimal basis count
cv = basis_nbasis_cv(fd_noisy.data, fd_noisy.argvals, nbasis_min=5, nbasis_max=35,
                     basis_type="bspline", criterion="gcv")
print(f"Optimal basis count: {cv['optimal_nbasis']}")

# 3. Smooth with P-splines using optimal basis count
smooth = pspline_fit_gcv(fd_noisy.data, fd_noisy.argvals, n_basis=cv["optimal_nbasis"])

# 4. Visualize
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for ax, idx in zip(axes, [0, 10, 25]):
    ax.plot(fd_noisy.argvals, fd_noisy.data[idx], ".", ms=1, alpha=0.3, color="gray", label="Noisy")
    ax.plot(fd_clean.argvals, fd_clean.data[idx], "k-", lw=1, alpha=0.5, label="True")
    ax.plot(fd_noisy.argvals, smooth["fitted"][idx], "r-", lw=2, label="P-spline")
    ax.set_title(f"Curve {idx}")
    if idx == 0:
        ax.legend(fontsize=8)

plt.suptitle(f"P-spline smoothing (n_basis={cv['optimal_nbasis']}, "
             f"edf={smooth['edf']:.1f})")
plt.tight_layout()
plt.show()
```

## API summary

| Function | Description |
|----------|-------------|
| `fdata_to_basis_1d(data, argvals, n_basis, basis_type)` | Project curves onto a basis |
| `basis_to_fdata_1d(coeffs, argvals, n_basis, basis_type)` | Reconstruct curves from coefficients |
| `bspline_basis(argvals, nknots, order)` | Evaluate raw B-spline basis matrix |
| `fourier_basis(argvals, n_basis)` | Evaluate raw Fourier basis matrix |
| `pspline_fit_1d(data, argvals, n_basis, lambda_, order)` | P-spline fit with fixed $\lambda$ |
| `pspline_fit_gcv(data, argvals, n_basis, order)` | P-spline fit with GCV-selected $\lambda$ |
| `select_basis_auto_1d(data, argvals, ...)` | Automatic basis type + count selection |
| `basis_nbasis_cv(data, argvals, ...)` | Cross-validated basis count selection |
| `smooth_basis_gcv(data, argvals, n_basis, ...)` | Basis smoothing with GCV penalty selection |

All functions are imported from `pyfda.basis`.
