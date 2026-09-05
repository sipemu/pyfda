# Canadian Weather: Fréchet Regression on Temperature Distributions

**Dataset:** Canadian Weather — daily mean temperature (°C) for 35 stations across
Canada. Each station's 365 daily observations are converted into a **probability
density** over the temperature axis, giving one density curve per station. These
density-valued responses are then regressed on station latitude using Fréchet
regression in Wasserstein space.

The central question is: *how does the shape of a Canadian weather station's
temperature distribution change with latitude?* Warmer southern stations (43–50°N)
produce right-shifted, narrower distributions whose mass concentrates in the mild
range; colder northern stations (58–68°N) produce left-shifted, broader distributions
that spread down to −40 °C. Fréchet regression estimates this shift as a smooth
function of latitude — and the predicted output at any latitude is itself a valid
probability density.

Standard regression cannot answer this question directly because density curves
cannot be averaged pointwise: the pointwise mean of two valid densities may not
integrate to one, may go negative, and loses the distributional geometry that
makes the Wasserstein metric natural for this problem. Fréchet regression operates
directly in Wasserstein-2 space, where the conditional mean at a predictor value
minimises a weighted sum of squared Wasserstein distances to the observed responses.

## Temperature distributions by station

We build one KDE density per station on a shared 60-point temperature grid, then
normalize each row so it integrates to 1. The Wasserstein barycenter gives the
overall "mean distribution" across all stations.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.stats import gaussian_kde
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.density_fda import normalize_density, wasserstein_barycenter

day, X, meta = load_canadian_weather("temperature")
lat = meta["lat"].to_numpy()

# Common temperature grid wide enough to cover all stations
t_grid = np.linspace(X.min() - 2, X.max() + 2, 60)

# One KDE density per station; clip then normalize so each row integrates to 1
density_matrix = np.vstack([
    normalize_density(np.clip(gaussian_kde(X[i], bw_method="silverman")(t_grid), 0, None), t_grid)
    for i in range(35)
])  # (35, 60)

# Wasserstein barycenter = the "Fréchet mean" distribution across all stations
bary = wasserstein_barycenter(density_matrix, t_grid)  # (60,)

# Show 6 representative stations colored by latitude (south→north)
order = np.argsort(lat)
sample_idx = order[[0, 7, 14, 21, 28, 34]]  # evenly spaced south to north
lat_colors = ["#e8710a", "#dc3545", "#198754", "#0dcaf0", "#6f42c1", "#3f51b5"]

f, ax = fig(figsize=(7.5, 4.2))
for k, si in enumerate(sample_idx):
    slat = lat[si]
    ax.plot(t_grid, density_matrix[si], color=lat_colors[k], lw=1.8,
            alpha=0.9, label=f"{meta['station'].iloc[si]} ({slat:.0f}°N)")
ax.fill_between(t_grid, bary, alpha=0.18, color="#6c757d")
ax.plot(t_grid, bary, color="#6c757d", lw=2.0, ls="--", label="barycenter (all 35)")
ax.set(title="Temperature distributions shift left and widen toward the north",
       xlabel="temperature (°C)", ylabel="density")
ax.legend(fontsize=8, ncol=2)
print(render(f))
print("FDARS_FENCE_OK")
```

Southern stations (orange, red) pack most of their mass above 0 °C; northern
stations (purple, blue) spread broadly into extreme cold. The Wasserstein
barycenter (dashed grey) is the distribution that sits geometrically in the
middle of all 35 — it is bimodal, reflecting both the continental interior and
the mild coastal stations.

!!! note "Two gotchas for density construction"
    **Clip before normalizing.** `gaussian_kde` can produce tiny negative
    values far into the tails. Pass the KDE output through `np.clip(..., 0, None)`
    before calling `normalize_density` — the binding raises `ValueError` on
    negative inputs (RESEARCH pitfall 7).

    **Use `wasserstein_barycenter`, not `frechet_mean`.** The `frechet_mean`
    function supports `space="spd"`, `space="spherical"`, and
    `space="correlation"` — it does **not** accept `space="density"`. For a
    density-valued unconditional mean, use `wasserstein_barycenter` from
    `fdars.density_fda` (RESEARCH pitfall 3).

## Why Fréchet regression?

The Fréchet conditional mean at predictor value $x$ minimises a weighted sum of
squared Wasserstein-2 distances to the observed density responses:

$$
\hat{m}(x) = \operatorname{arg\,min}_{y \in \mathcal{W}} \sum_{i=1}^{n} w_i(x)\, W_2(y,\, f_i)^2
$$

where $f_i$ is the density of station $i$, $W_2$ is the Wasserstein-2 distance,
and $w_i(x)$ are polynomial (global) or kernel (local) weights centred at $x$.
The resulting prediction is guaranteed to live in Wasserstein space — it is itself
a valid density.

`fdars` exposes two variants:

- **`frechet_global_reg`** — polynomial weights; linear predictor–response
  relationship; no bandwidth to tune.
- **`frechet_local_reg`** — Gaussian kernel weights; captures nonlinear effects;
  requires a `bandwidth` parameter (in the same units as the predictor).

## Global and local Fréchet regression

We split into 28 training and 7 test stations, fit both models, and evaluate with
the Integrated Squared Error (ISE) on held-out densities.

```python exec="1" html="1" source="above"
import numpy as np
from scipy.stats import gaussian_kde
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.density_fda import normalize_density, wasserstein_barycenter
from fdars.frechet import frechet_global_reg, frechet_local_reg

day, X, meta = load_canadian_weather("temperature")
lat = meta["lat"].to_numpy()
t_grid = np.linspace(X.min() - 2, X.max() + 2, 60)

density_matrix = np.vstack([
    normalize_density(np.clip(gaussian_kde(X[i], bw_method="silverman")(t_grid), 0, None), t_grid)
    for i in range(35)
])

# Wasserstein barycenter for reference
bary = wasserstein_barycenter(density_matrix, t_grid)

# Reproducible 28/7 train–test split
rng = np.random.default_rng(42)
idx = rng.permutation(35)
tr, te = idx[:28], idx[28:]

pred_tr = lat[tr].reshape(-1, 1)   # (28, 1) — xout MUST be 2D even for p=1
pred_te = lat[te].reshape(-1, 1)   # (7, 1)
resp_tr = density_matrix[tr]       # (28, 60)
resp_te = density_matrix[te]       # (7, 60)

# Global Fréchet regression
result_g = frechet_global_reg(pred_tr, resp_tr, t_grid, pred_te)
pred_g = np.asarray(result_g["predicted"])   # (7, 60) — naked-array access required

# Local Fréchet regression (bandwidth in degrees of latitude)
result_l = frechet_local_reg(pred_tr, resp_tr, t_grid, pred_te, bandwidth=5.0)
pred_l = np.asarray(result_l["predicted"])   # (7, 60)

# ISE = Integrated Squared Error on held-out densities
ise_g = np.trapezoid((pred_g - resp_te) ** 2, t_grid, axis=1).mean()
ise_l = np.trapezoid((pred_l - resp_te) ** 2, t_grid, axis=1).mean()

# Predicted densities at three reference latitudes (2D xout required)
xout_ref = np.array([[45.0], [55.0], [65.0]])
pred_ref = np.asarray(
    frechet_global_reg(pred_tr, resp_tr, t_grid, xout_ref)["predicted"]
)  # (3, 60)

f, axes = fig(ncols=2, figsize=(9.5, 4.2))

# Panel 1: global predicted densities at 45/55/65°N vs barycenter
axes[0].fill_between(t_grid, bary, alpha=0.18, color="#6c757d", label="barycenter")
for k, (xlat, col) in enumerate(zip([45, 55, 65],
                                     ["#e8710a", "#3f51b5", "#198754"])):
    axes[0].plot(t_grid, pred_ref[k], color=col, lw=2.2, label=f"{xlat}°N")
axes[0].set(title="Global Fréchet: predicted densities by latitude",
            xlabel="temperature (°C)", ylabel="density")
axes[0].legend(fontsize=8)

# Panel 2: ISE bar chart
labels = ["global", "local\n(bw = 5°)"]
vals = [ise_g, ise_l]
bars = axes[1].bar(labels, vals, color=["#3f51b5", "#e8710a"], width=0.45)
for b, v in zip(bars, vals):
    axes[1].text(b.get_x() + b.get_width() / 2, v * 1.02, f"{v:.5f}",
                 ha="center", fontsize=9)
axes[1].set(title="Test ISE: local regression wins on spatially heterogeneous data",
            ylabel="mean integrated squared error")
print(render(f))
print("FDARS_FENCE_OK")
```

The predicted densities shift left and broaden as latitude increases — the model
captures the genuine climatological gradient. Local regression (bandwidth = 5°
latitude) achieves lower ISE than global because the latitude–distribution
relationship is not perfectly linear: subarctic stations deviate more sharply
from the trend than a linear model expects.

!!! note "Accessing predicted outputs"
    `result["predicted"]` returns a Python list-of-lists, **not** a numpy
    array. Always wrap it with `np.asarray(result["predicted"])` before
    indexing or arithmetic. Calling `.shape` on the raw value raises
    `AttributeError` (RESEARCH pitfall 1).

    `xout` must be **2-D** even for a scalar predictor. Use
    `lat[idx].reshape(-1, 1)` (shape `(n, 1)`), not a 1-D array — the binding
    raises a shape error on 1-D input (RESEARCH pitfall 2).

## Density integration check

A key property of Fréchet regression in Wasserstein space is that the prediction
at any predictor value is itself a valid probability density. We verify this for
the 7 held-out test predictions.

```python exec="1" source="above"
import numpy as np
from scipy.stats import gaussian_kde
from docs_data import load_canadian_weather
from fdars.density_fda import normalize_density
from fdars.frechet import frechet_global_reg, frechet_local_reg

day, X, meta = load_canadian_weather("temperature")
lat = meta["lat"].to_numpy()
t_grid = np.linspace(X.min() - 2, X.max() + 2, 60)

density_matrix = np.vstack([
    normalize_density(np.clip(gaussian_kde(X[i], bw_method="silverman")(t_grid), 0, None), t_grid)
    for i in range(35)
])

rng = np.random.default_rng(42)
idx = rng.permutation(35)
tr, te = idx[:28], idx[28:]
pred_tr = lat[tr].reshape(-1, 1)
pred_te = lat[te].reshape(-1, 1)
resp_tr = density_matrix[tr]
resp_te = density_matrix[te]

result_g = frechet_global_reg(pred_tr, resp_tr, t_grid, pred_te)
pred_g = np.asarray(result_g["predicted"])

result_l = frechet_local_reg(pred_tr, resp_tr, t_grid, pred_te, bandwidth=5.0)
pred_l = np.asarray(result_l["predicted"])

ise_g = np.trapezoid((pred_g - resp_te) ** 2, t_grid, axis=1).mean()
ise_l = np.trapezoid((pred_l - resp_te) ** 2, t_grid, axis=1).mean()

print(f"Global regression  ISE: {ise_g:.6f}")
print(f"Local  regression  ISE: {ise_l:.6f}")
print(f"Local improvement:      {(ise_g - ise_l) / ise_g * 100:.1f}%")
print()
print("Predicted-density integral check (should be ≈1.0 for each row):")
for k in range(7):
    intg_g = np.trapezoid(pred_g[k], t_grid)
    intg_l = np.trapezoid(pred_l[k], t_grid)
    print(f"  test station {k+1}: global={intg_g:.4f}  local={intg_l:.4f}")
print("FDARS_FENCE_OK")
```

Both global and local predictions integrate to approximately 1 for each held-out
station, confirming that Fréchet regression preserves the density constraint. The
ISE numbers (printed above) come directly from the fence run — local regression
outperforms global for this spatially heterogeneous dataset.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `gaussian_kde(data, bw_method)` | `bw_method="silverman"` | scipy KDE; Silverman's rule adapts bandwidth to sample spread |
| `normalize_density(density, argvals)` | — | Normalizes a non-negative array to integrate to 1 over `argvals`; raises `ValueError` on negative input |
| `wasserstein_barycenter(density_matrix, argvals)` | — | Wasserstein-2 barycenter of the rows of `density_matrix`; returns `(m,)` density curve |
| `frechet_global_reg(predictors, responses, argvals, xout)` | — | Polynomial-weighted global Fréchet regression; returns `dict` with `predicted`, `xout`, `x_bar` |
| `frechet_local_reg(predictors, responses, argvals, xout, bandwidth)` | `bandwidth` | Kernel-weighted local Fréchet regression; returns `dict` with `predicted`, `xout`, `bandwidth` (no `x_bar`) |

!!! tip "Choosing the local regression bandwidth"
    Start with `bandwidth ≈ std(predictors)`. For this dataset `std(lat) ≈ 8°`,
    so `bandwidth=5` concentrates on a ~±10° latitude window. Too small a
    bandwidth makes predictions erratic; too large converges toward the
    unconditional barycenter. Inspect the predicted curves row-by-row — adjacent
    predictor values should produce smoothly varying densities.

## See also

- [Fréchet Regression](../regression/frechet-regression.md) — method page:
  signed-weight quantile averaging, `frechet_global_reg` / `frechet_local_reg`
  parameter reference, bandwidth guidance, and `frechet_mean` for SPD/spherical
  spaces
- [Density FDA](../analyze/density-fda.md) — LQD transform, Wasserstein distance,
  `normalize_density`, `wasserstein_barycenter`, and `frechet_anova` background
- [Canadian Weather: FPCA & Clustering](canadian-weather.md) — same dataset
  analyzed with FPCA and k-means on the raw temperature curves

## References

- Petersen, A. and Müller, H.-G. (2019). Fréchet regression for random objects with
  Euclidean predictors. *Annals of Statistics* 47(2), 691–719.
- Villani, C. (2009). *Optimal Transport: Old and New.* Springer, Berlin.
- Ramsay, J.O. and Silverman, B.W. (2005). *Functional Data Analysis*, 2nd ed. Springer.
