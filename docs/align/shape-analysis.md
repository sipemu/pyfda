# Shape Analysis

Shape analysis studies the *geometry* of functional data after removing nuisance transformations (translation, scaling, reparameterization). `pyfda` provides tools for shape distances, elastic depth measures, and elastic FPCA that decomposes variability into amplitude and phase components.

---

## Shape distance (quotient space)

The **shape distance** measures how different two curves are in the quotient space obtained by modding out the group of warping functions. Unlike the raw elastic distance, the shape distance factors out both amplitude scaling and phase variation, leaving only the intrinsic "shape" of the curve.

```python
import numpy as np
from pyfda.alignment import shape_distance

t = np.linspace(0, 1, 101)
f1 = np.sin(2 * np.pi * t)
f2 = 1.5 * np.sin(2 * np.pi * (t - 0.1))  # scaled and shifted

result = shape_distance(f1, f2, t)

d          = result["distance"]     # shape distance (scalar)
gamma      = result["gamma"]        # optimal warping function
f2_aligned = result["f2_aligned"]   # f2 after alignment
```

| Key | Type | Description |
|-----|------|-------------|
| `distance` | `float` | Shape distance in quotient space |
| `gamma` | `ndarray (m,)` | Optimal warping function |
| `f2_aligned` | `ndarray (m,)` | Second curve aligned to first |

!!! info "Shape vs. elastic distance"
    The elastic distance preserves amplitude differences. The shape distance removes them, so two curves with identical shape but different heights have shape distance near zero.

---

## Elastic depth

**Elastic depth** ranks functional observations from center to periphery using the elastic metric. It decomposes into amplitude and phase components, enabling separate outlier detection in each source of variability.

```python
import numpy as np
from pyfda.alignment import elastic_depth

np.random.seed(0)
n, m = 40, 101
t = np.linspace(0, 1, m)
data = np.array([
    np.sin(2 * np.pi * (t - 0.1 * np.random.randn()))
    + 0.3 * np.random.randn()
    for _ in range(n)
])

result = elastic_depth(data, t, lambda_=0.0)

amp_depth  = result["amplitude_depth"]    # (n,)
ph_depth   = result["phase_depth"]        # (n,)
comb_depth = result["combined_depth"]     # (n,)
amp_dists  = result["amplitude_distances"]  # (n, n)
ph_dists   = result["phase_distances"]      # (n, n)

# Most central curve (highest combined depth)
median_idx = np.argmax(comb_depth)
print(f"Elastic median: curve {median_idx}")
print(f"  Amplitude depth: {amp_depth[median_idx]:.4f}")
print(f"  Phase depth:     {ph_depth[median_idx]:.4f}")

# Potential outliers (lowest depth)
outlier_idx = np.argmin(comb_depth)
print(f"Most outlying:  curve {outlier_idx}")
```

| Key | Type | Description |
|-----|------|-------------|
| `amplitude_depth` | `ndarray (n,)` | Depth based on amplitude distances |
| `phase_depth` | `ndarray (n,)` | Depth based on phase distances |
| `combined_depth` | `ndarray (n,)` | Joint amplitude+phase depth |
| `amplitude_distances` | `ndarray (n, n)` | Pairwise amplitude distance matrix |
| `phase_distances` | `ndarray (n, n)` | Pairwise phase distance matrix |

!!! tip "Diagnostic plots"
    Plot amplitude depth vs. phase depth in a scatter plot. Curves far from the cluster center in either dimension are outlying in that specific source of variability.

---

## Elastic FPCA

Standard FPCA conflates amplitude and phase variation into a single set of principal components. **Elastic FPCA** performs PCA in the aligned (elastic) space, yielding separate decompositions of amplitude and phase variability.

### Vertical (amplitude) FPCA

Extracts the principal modes of **amplitude** variation from the aligned curves.

```python
from pyfda.alignment import vert_fpca

result = vert_fpca(data, t, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4)

scores      = result["scores"]              # (n, 3) -- amplitude PC scores
eigfun_q    = result["eigenfunctions_q"]     # (3, m+1) -- eigenfunctions in SRSF space
eigfun_f    = result["eigenfunctions_f"]     # (3, m) -- eigenfunctions in original space
eigenvalues = result["eigenvalues"]          # (3,)
cum_var     = result["cumulative_variance"]  # (3,)
mean_q      = result["mean_q"]              # (m+1,) -- mean SRSF

print(f"Amplitude variance explained: {cum_var[-1]*100:.1f}%")
```

| Key | Type | Description |
|-----|------|-------------|
| `scores` | `ndarray (n, k)` | Amplitude FPC scores |
| `eigenfunctions_q` | `ndarray (k, m+1)` | Eigenfunctions in SRSF space |
| `eigenfunctions_f` | `ndarray (k, m)` | Eigenfunctions in function space |
| `eigenvalues` | `ndarray (k,)` | Eigenvalues |
| `cumulative_variance` | `ndarray (k,)` | Cumulative proportion of variance |
| `mean_q` | `ndarray (m+1,)` | Mean SRSF |

### Horizontal (phase) FPCA

Extracts the principal modes of **phase** variation from the estimated warping functions.

```python
from pyfda.alignment import horiz_fpca

result = horiz_fpca(data, t, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4)

scores      = result["scores"]                # (n, 3) -- phase PC scores
eigfun_psi  = result["eigenfunctions_psi"]     # (3, m) -- in psi space
eigfun_gam  = result["eigenfunctions_gam"]     # (3, m) -- in gamma space
eigenvalues = result["eigenvalues"]            # (3,)
cum_var     = result["cumulative_variance"]    # (3,)
mean_psi    = result["mean_psi"]               # (m,) -- mean psi
shooting    = result["shooting_vectors"]       # (n, m) -- shooting vectors

print(f"Phase variance explained: {cum_var[-1]*100:.1f}%")
```

| Key | Type | Description |
|-----|------|-------------|
| `scores` | `ndarray (n, k)` | Phase FPC scores |
| `eigenfunctions_psi` | `ndarray (k, m)` | Eigenfunctions in $\psi$ representation |
| `eigenfunctions_gam` | `ndarray (k, m)` | Eigenfunctions as warping functions |
| `eigenvalues` | `ndarray (k,)` | Eigenvalues |
| `cumulative_variance` | `ndarray (k,)` | Cumulative proportion of variance |
| `mean_psi` | `ndarray (m,)` | Mean $\psi$ |
| `shooting_vectors` | `ndarray (n, m)` | Shooting vectors (tangent space) |

### Joint FPCA

Combines amplitude and phase variation into a **single joint decomposition**, weighting the two sources via a balance parameter $c$.

```python
from pyfda.alignment import joint_fpca

result = joint_fpca(data, t, n_comp=3, lambda_=0.0, max_iter=20, tol=1e-4)

scores     = result["scores"]              # (n, 3)
eigenvalues = result["eigenvalues"]        # (3,)
cum_var    = result["cumulative_variance"]  # (3,)
balance_c  = result["balance_c"]           # automatic balance parameter
vert_comp  = result["vert_component"]      # (k, m) -- amplitude part
horiz_comp = result["horiz_component"]     # (k, m) -- phase part

print(f"Balance parameter c = {balance_c:.4f}")
print(f"Joint variance explained: {cum_var[-1]*100:.1f}%")
```

| Key | Type | Description |
|-----|------|-------------|
| `scores` | `ndarray (n, k)` | Joint FPC scores |
| `eigenvalues` | `ndarray (k,)` | Eigenvalues |
| `cumulative_variance` | `ndarray (k,)` | Cumulative proportion of variance |
| `balance_c` | `float` | Balance between amplitude and phase |
| `vert_component` | `ndarray (k, m)` | Amplitude part of each eigenfunction |
| `horiz_component` | `ndarray (k, m)` | Phase part of each eigenfunction |

!!! info "When to use which?"
    - **Vertical FPCA** -- when you care only about amplitude variability (e.g., peak heights).
    - **Horizontal FPCA** -- when you care only about timing variability (e.g., event onset).
    - **Joint FPCA** -- when you want a unified low-dimensional representation for downstream tasks like regression or clustering.

---

## Full example: amplitude vs. phase decomposition

```python
import numpy as np
from pyfda.alignment import (
    karcher_mean,
    vert_fpca,
    horiz_fpca,
    elastic_depth,
)

# --- Simulate ---
np.random.seed(123)
n, m = 60, 151
t = np.linspace(0, 1, m)

data = np.zeros((n, m))
for i in range(n):
    amp = 1.0 + 0.4 * np.random.randn()           # amplitude variation
    shift = 0.08 * np.random.randn()               # phase variation
    t_warp = np.clip(t + shift * np.sin(np.pi * t), 0, 1)
    data[i] = amp * np.sin(2 * np.pi * np.interp(t, t_warp, t))

# --- Alignment ---
km = karcher_mean(data, t, lambda_=0.05)
print(f"Karcher mean converged: {km['converged']}")

# --- Amplitude FPCA ---
vfpca = vert_fpca(data, t, n_comp=3, lambda_=0.05)
print(f"Amplitude variance (3 PCs): {vfpca['cumulative_variance'][-1]*100:.1f}%")

# --- Phase FPCA ---
hfpca = horiz_fpca(data, t, n_comp=3, lambda_=0.05)
print(f"Phase variance (3 PCs):     {hfpca['cumulative_variance'][-1]*100:.1f}%")

# --- Elastic depth ---
depth = elastic_depth(data, t)
median_idx = np.argmax(depth["combined_depth"])
print(f"Elastic median: curve {median_idx}")
print(f"  Amp depth:  {depth['amplitude_depth'][median_idx]:.4f}")
print(f"  Phase depth: {depth['phase_depth'][median_idx]:.4f}")
```
