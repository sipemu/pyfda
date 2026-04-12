# pyfda.fdata

Core functional data container and operations.

---

## `Fdata` class

```python
from pyfda import Fdata
```

The **main entry point** for working with functional data in pyfda. Bundles
observation data, evaluation grid, identifiers, and metadata into a single
object — mirroring the R package's `fdata` class.

### Constructor

```python
Fdata(data, argvals=None, rangeval=None, names=None, id=None, metadata=None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `array_like` | | `(n, m)` matrix, `(n, m1, m2)` 3-D array (surfaces), or 1-D array (single curve) |
| `argvals` | `ndarray` or `(ndarray, ndarray)` | `arange(m)` | Evaluation grid. Tuple of two arrays for 2-D surfaces. |
| `rangeval` | `tuple` | auto | Domain range |
| `names` | `dict` | auto | Plot labels (`main`, `xlab`, `ylab`, `zlab`) |
| `id` | `list[str]` | `["obs_1", …]` | Observation identifiers |
| `metadata` | `DataFrame` or `dict` | `None` | Per-observation covariates |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `n_obs` | `int` | Number of observations |
| `n_points` | `int` | Number of evaluation points |
| `shape` | `tuple` | Shape of the data matrix |
| `fdata2d` | `bool` | Whether this is 2-D surface data |
| `dims` | `tuple` or `None` | `(m1, m2)` grid dimensions (2-D only) |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `mean()` | `ndarray` | Pointwise mean across observations |
| `center()` | `Fdata` | Subtract the pointwise mean |
| `deriv(nderiv=1)` | `Fdata` | Numerical derivatives |
| `norm(p=2.0)` | `ndarray` | Lp norms per observation |
| `normalize(method)` | `Fdata` | Normalize (center, autoscale, pareto, …) |
| `geometric_median()` | `ndarray` | L1 geometric median |
| `depth(method, **kw)` | `ndarray` | Depth values (fraiman_muniz, modal, band, …) |
| `distance(other, method, **kw)` | `ndarray` | Distance matrix (lp, dtw, hausdorff, …) |
| `copy()` | `Fdata` | Deep copy |
| `summary()` | `None` | Print detailed summary |

### Subsetting

```python
fd[0:5]           # first 5 observations — metadata preserved
fd[[0, 3, 7]]     # specific observations by index
fd[0:5, 10:50]    # observations + grid points (1-D only)
```

### Arithmetic

`Fdata` supports element-wise `+`, `-`, `*`, `/` with other `Fdata` objects
or scalars:

```python
fd_centered = fd - fd.mean()
fd_scaled = fd * 2.0
fd_sum = fd1 + fd2
```

### Example

```python
import numpy as np
from pyfda import Fdata

t = np.linspace(0, 1, 100)
X = np.random.randn(20, 100)
fd = Fdata(X, argvals=t, id=[f"s_{i}" for i in range(20)],
           metadata={"group": ["A"] * 10 + ["B"] * 10})

fd_c = fd.center()          # centered, metadata preserved
depths = fd.depth("band")   # band depth values
D = fd.distance(method="lp") # L2 distance matrix
```

---

## Low-level functions

The functions below operate on raw NumPy arrays. They are called internally
by `Fdata` methods but can also be used directly.

| Function | Description |
|----------|-------------|
| [`mean_1d`](#mean_1d) | Pointwise mean of 1D functional data |
| [`mean_2d`](#mean_2d) | Pointwise mean of 2D functional data |
| [`center_1d`](#center_1d) | Center data by subtracting pointwise mean |
| [`deriv_1d`](#deriv_1d) | Numerical derivatives of 1D functional data |
| [`deriv_2d`](#deriv_2d) | Partial derivatives of 2D functional data |
| [`norm_lp_1d`](#norm_lp_1d) | Lp norms of 1D functional data |
| [`geometric_median_1d`](#geometric_median_1d) | Geometric (L1) median for 1D data |
| [`geometric_median_2d`](#geometric_median_2d) | Geometric (L1) median for 2D data |
| [`normalize`](#normalize) | Normalize functional data (multiple methods) |

---

### `mean_1d`

```python
pyfda.fdata.mean_1d(data)
```

Compute the pointwise mean of 1D functional data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional data matrix |

| Returns | Type | Description |
|---------|------|-------------|
| mean | `ndarray (m,)` | Pointwise mean across observations |

```python
import numpy as np, pyfda
data = np.random.randn(50, 100)
mu = pyfda.mean_1d(data)  # shape (100,)
```

---

### `mean_2d`

```python
pyfda.mean_2d(data)
```

Compute the pointwise mean of 2D (surface) functional data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m1*m2)` | Flattened 2D functional data |

| Returns | Type | Description |
|---------|------|-------------|
| mean | `ndarray (m1*m2,)` | Pointwise mean |

```python
data = np.random.randn(30, 400)  # 30 surfaces on 20x20 grid
mu = pyfda.mean_2d(data)
```

---

### `center_1d`

```python
pyfda.center_1d(data)
```

Center functional data by subtracting the pointwise mean.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m)` | Functional data matrix |

| Returns | Type | Description |
|---------|------|-------------|
| centered | `ndarray (n, m)` | Centered data |

```python
centered = pyfda.center_1d(data)
assert np.allclose(centered.mean(axis=0), 0)
```

---

### `deriv_1d`

```python
pyfda.deriv_1d(data, argvals, nderiv=1)
```

Compute numerical derivatives of 1D functional data using finite differences.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data matrix |
| `argvals` | `ndarray (m,)` | | Evaluation grid points |
| `nderiv` | `int` | `1` | Derivative order |

| Returns | Type | Description |
|---------|------|-------------|
| derivatives | `ndarray (n, m)` | Derivative data |

```python
t = np.linspace(0, 1, 100)
data = np.sin(2 * np.pi * t).reshape(1, -1)
d1 = pyfda.deriv_1d(data, t, nderiv=1)
```

---

### `deriv_2d`

```python
pyfda.deriv_2d(data, argvals_s, argvals_t)
```

Compute partial derivatives of 2D functional data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `ndarray (n, m1*m2)` | Flattened 2D functional data |
| `argvals_s` | `ndarray (m1,)` | Grid points in first dimension |
| `argvals_t` | `ndarray (m2,)` | Grid points in second dimension |

| Returns | Type | Description |
|---------|------|-------------|
| `(ds, dt, dsdt)` | `tuple of ndarray (n, m1*m2)` | Partial derivatives w.r.t. s, t, and mixed |

```python
s = np.linspace(0, 1, 20)
t = np.linspace(0, 1, 20)
ds, dt, dsdt = pyfda.deriv_2d(data, s, t)
```

---

### `norm_lp_1d`

```python
pyfda.norm_lp_1d(data, argvals, p=2.0)
```

Compute Lp norms of 1D functional data via numerical integration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data matrix |
| `argvals` | `ndarray (m,)` | | Evaluation grid for integration |
| `p` | `float` | `2.0` | Norm order (use `float('inf')` for sup-norm) |

| Returns | Type | Description |
|---------|------|-------------|
| norms | `ndarray (n,)` | Lp norm per observation |

```python
t = np.linspace(0, 1, 100)
norms = pyfda.norm_lp_1d(data, t, p=2.0)
```

---

### `geometric_median_1d`

```python
pyfda.geometric_median_1d(data, argvals, max_iter=100, tol=1e-8)
```

Compute the geometric (L1) median of 1D functional data via Weiszfeld's algorithm.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data matrix |
| `argvals` | `ndarray (m,)` | | Evaluation grid for integration |
| `max_iter` | `int` | `100` | Maximum iterations |
| `tol` | `float` | `1e-8` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| median | `ndarray (m,)` | Geometric median function |

```python
t = np.linspace(0, 1, 100)
med = pyfda.geometric_median_1d(data, t)
```

---

### `geometric_median_2d`

```python
pyfda.geometric_median_2d(data, argvals_s, argvals_t, max_iter=100, tol=1e-8)
```

Compute the geometric (L1) median of 2D functional data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m1*m2)` | | Flattened 2D functional data |
| `argvals_s` | `ndarray (m1,)` | | Grid points in first dimension |
| `argvals_t` | `ndarray (m2,)` | | Grid points in second dimension |
| `max_iter` | `int` | `100` | Maximum iterations |
| `tol` | `float` | `1e-8` | Convergence tolerance |

| Returns | Type | Description |
|---------|------|-------------|
| median | `ndarray (m1*m2,)` | Geometric median surface |

```python
s, t = np.linspace(0, 1, 20), np.linspace(0, 1, 20)
med = pyfda.geometric_median_2d(data, s, t)
```

---

### `normalize`

```python
pyfda.normalize(data, method="center")
```

Normalize functional data using one of several methods.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | Functional data matrix |
| `method` | `str` | `"center"` | Normalization method (see below) |

**Methods:**

| Method | Description |
|--------|-------------|
| `"center"` | Subtract pointwise mean |
| `"autoscale"` | Subtract mean, divide by std |
| `"pareto"` | Subtract mean, divide by sqrt(std) |
| `"range"` | Scale to [0, 1] per time point |
| `"curve_center"` | Subtract each curve's own mean |
| `"curve_standardize"` | Center and scale each curve individually |
| `"curve_range"` | Scale each curve to [0, 1] |

| Returns | Type | Description |
|---------|------|-------------|
| normalized | `ndarray (n, m)` | Normalized data |

```python
normed = pyfda.normalize(data, method="autoscale")
```
