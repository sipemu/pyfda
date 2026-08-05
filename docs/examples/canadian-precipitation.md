# Canadian Precipitation: Geographic Effects on Rainfall Profiles

**Dataset:** Canadian Weather — daily precipitation (mm, log-scaled and
smoothed) over a 365-day year for 35 weather stations, each tagged with its
climatic region (Atlantic, Continental, Pacific, Arctic) and its geographic
coordinates (latitude, longitude).

Rain, unlike temperature, is driven less by the calendar than by *place*: an
Atlantic port and an Arctic outpost receive wildly different amounts, on
different schedules. Each station is a precipitation *curve*, and the question
is how **geography shapes its shape**. We use `fdars` to find the dominant modes
of variation across stations (FPCA), relate those modes to latitude, and then
model the whole profile as a function of region with function-on-scalar
regression.

## Precipitation curves by region

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("precipitation")
region = meta["region"].to_numpy()
colors = {"Atlantic": "#3f51b5", "Continental": "#e8710a",
          "Pacific": "#198754", "Arctic": "#dc3545"}

f, ax = fig()
for r, c in colors.items():
    ax.plot(day, X[region == r].T, color=c, lw=1, alpha=0.55)
for r, c in colors.items():
    ax.plot([], [], color=c, label=r)
ax.set(title="Daily precipitation, 35 Canadian stations",
       xlabel="day of year", ylabel="precipitation (mm)")
ax.legend(ncol=2)
print(render(f))
```

The regions separate by **level** and by **timing**. Pacific and Atlantic
stations sit high (wet coasts), Arctic stations hug the bottom (a polar desert),
and Continental stations fall in between with a distinct summer-rain hump. The
shapes differ, not just the averages — exactly what functional methods are built
to exploit.

## FPCA: dominant modes of rainfall variation

`fdars.regression.fpca` decomposes the curves into a mean plus a few orthogonal
**principal component functions** $\phi_k(t)$, so each station is

$$
x_i(t) \;\approx\; \bar x(t) \;+\; \sum_{k=1}^{K} \xi_{ik}\,\phi_k(t),
$$

with `scores` $\xi_{ik}$, `rotation` columns $\phi_k$, and `singular_values`
setting each component's share of variance.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.regression import fpca

day, X, meta = load_canadian_weather("precipitation")
pc = fpca(X, day, n_comp=3)
mean = np.asarray(pc["mean"])
phi = np.asarray(pc["rotation"])                  # (365, 3)
sv = np.asarray(pc["singular_values"])
ve = sv ** 2 / np.sum(sv ** 2)                    # variance explained

f, ax = fig()
scores_sd = np.asarray(pc["scores"]).std(axis=0)
for k, c in zip(range(2), ["#3f51b5", "#e8710a"]):
    ax.plot(day, mean + scores_sd[k] * phi[:, k], color=c, lw=1.6,
            label=f"mean + PC{k+1} ({ve[k]*100:.0f}%)")
    ax.plot(day, mean - scores_sd[k] * phi[:, k], color=c, lw=1.6, ls="--")
ax.plot(day, mean, color="#6c757d", lw=2.4, label="mean")
ax.set(title="FPCA modes: mean ± each component",
       xlabel="day of year", ylabel="precipitation (mm)")
ax.legend(ncol=2)
print(render(f))
```

**PC1 (≈84% of variance)** raises or lowers the whole curve — an overall
*wetness* axis separating soaked coasts from the dry Arctic. **PC2 (≈9%)** shifts
rain between the summer and the cooler months — a *seasonality-of-rainfall* axis.
Together the first two components carry more than 90% of the variation between
stations.

## Do the modes track latitude?

If wetness is geographic, the PC1 score should vary with **latitude** — high
northern stations are drier. We plot each station's first two scores against its
latitude.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.regression import fpca

day, X, meta = load_canadian_weather("precipitation")
pc = fpca(X, day, n_comp=3)
scores = np.asarray(pc["scores"])
lat = meta["lat"].to_numpy()
region = meta["region"].to_numpy()
colors = {"Atlantic": "#3f51b5", "Continental": "#e8710a",
          "Pacific": "#198754", "Arctic": "#dc3545"}

r1 = np.corrcoef(scores[:, 0], lat)[0, 1]
f, ax = fig(figsize=(6.0, 4.4))
for r, c in colors.items():
    m = region == r
    ax.scatter(lat[m], scores[m, 0], color=c, s=42, alpha=0.85,
               edgecolor="white", label=r)
b, a = np.polyfit(lat, scores[:, 0], 1)
xs = np.linspace(lat.min(), lat.max(), 50)
ax.plot(xs, a + b * xs, color="#212529", lw=1.4, ls="--")
ax.set(title=f"PC1 score vs. latitude (r = {r1:.2f})",
       xlabel="latitude (°N)", ylabel="PC1 score (wetness)")
ax.legend()
print(render(f))
```

PC1 falls with latitude ($r \approx -0.52$): the further north a station, the
lower its wetness score. The relationship is real but loose — the Pacific
stations are wet *and* fairly northern, sitting above the trend line, because
coastal exposure competes with latitude. Geography drives the leading mode, but
not through latitude alone.

## Function-on-scalar regression: region profiles

To model the *whole curve* as a function of geography, `fdars.regression.fosr`
fits a **function-on-scalar regression**: a functional response (the
precipitation profile) on scalar predictors (region indicators). Each
coefficient $\beta_p(t)$ is itself a curve. We use an intercept plus three
region dummies (Arctic as the baseline) and a small roughness penalty.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.regression import fosr, predict_fosr

day, X, meta = load_canadian_weather("precipitation")
X = np.ascontiguousarray(X, dtype=np.float64)
region = meta["region"].to_numpy()

# design matrix: intercept + Atlantic/Continental/Pacific (Arctic = baseline)
names = ["Atlantic", "Continental", "Pacific"]
Z = np.column_stack([np.ones(len(region))]
                    + [(region == r).astype(float) for r in names])
Z = np.ascontiguousarray(Z, dtype=np.float64)

model = fosr(X, Z, lambda_=1.0)                   # fitted, beta, residuals, r_squared

# predict a representative profile for each region
new = np.ascontiguousarray(np.array([
    [1, 0, 0, 0],   # Arctic (baseline)
    [1, 1, 0, 0],   # Atlantic
    [1, 0, 1, 0],   # Continental
    [1, 0, 0, 1],   # Pacific
], dtype=np.float64))
profiles = np.asarray(predict_fosr(X, Z, new, lambda_=1.0))

colors = ["#dc3545", "#3f51b5", "#e8710a", "#198754"]
labels = ["Arctic", "Atlantic", "Continental", "Pacific"]
f, ax = fig()
for i, (lab, c) in enumerate(zip(labels, colors)):
    ax.plot(day, profiles[i], color=c, lw=2.0, label=lab)
ax.set(title=f"FOSR fitted precipitation profile by region "
             f"(R² = {model['r_squared']:.2f})",
       xlabel="day of year", ylabel="precipitation (mm)")
ax.legend(ncol=2)
print(render(f))
```

The fitted region profiles rank exactly as the raw curves do — **Atlantic and
Pacific wettest, Continental drier with a summer hump, Arctic driest of all** —
and they smooth away station-to-station noise into one clean curve per region.
Region alone explains about a third of the total curve variation
($R^2 \approx 0.33$); the rest is within-region differences that a coarse
four-region factor cannot capture. The model exposes `beta` (the $\beta_p(t)$
coefficient curves) and `residuals` for further diagnostics.

!!! note "Predictor shape"
    `fosr` expects the scalar predictors as a 2-D `(n, p)` design matrix and the
    response as `(n, m)`. Categorical predictors like region must be encoded as
    dummy columns yourself, as above. `predict_fosr` takes the same fitted
    design plus a `(k, p)` matrix of new predictor rows and returns the `(k, m)`
    fitted profiles.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `fpca(data, argvals, n_comp)` | `n_comp` | Functional PCA; returns `scores`, `rotation`, `singular_values`, `mean` |
| `fosr(response, predictors, lambda_)` | `lambda_` | Function-on-scalar regression; returns `fitted`, `beta`, `residuals`, `r_squared` |
| `predict_fosr(response, predictors, new_predictors, lambda_)` | `new_predictors` | Fitted response curves for new scalar predictor rows |

!!! tip "Penalty selection"
    Pass a **negative** `lambda_` to `fosr` / `predict_fosr` to select the
    roughness penalty automatically by generalized cross-validation instead of
    fixing it by hand.

## See also

- [Weather curves: FPCA and clustering](canadian-weather.md) — FPCA and
  clustering on the temperature curves for the same stations.
- [Canadian temperature: annual cycle](canadian-seasonal.md) — period detection
  and STL on the seasonal signal.
- [Functional PCA](../represent/fpca.md) for the decomposition in depth.
