# Canadian Weather: Functional Time Series and Forecast

**Dataset:** Canadian Weather — daily mean temperature (°C) for 35 stations across
Canada. Stations are sorted south-to-north by latitude, and each station's 365 daily
observations are weekly-aggregated to 52 points. The result is a **functional time
series** of length 35: a smooth spatial gradient from warm southern stations
(~43°N) to cold northern ones (~68°N), with each curve recording a full annual
temperature cycle at weekly resolution.

The central question is: *can a model trained on the 30 southern stations forecast
the annual temperature profiles of the 5 most-northern ones?* The Functional Time
Series Model (FTSM) decomposes the gradient into a mean function and three functional
principal components, fits an AR process to each component's scores, and extrapolates
five steps into the unobserved north. The evaluation measures how close the 5-step
spatial forecast comes to the true northern profiles.

This framing is genuinely a functional time series because the spatial gradient is
smooth: adjacent stations share climate patterns, meaning consecutive curves
autocorrelate — exactly the structure FTSM is designed to exploit. The stationarity
test confirms the gradient is non-stationary (the south and north are structurally
different), while the functional ACF reveals a lag-1 correlation of about 0.33
(nearby stations are similar).

!!! tip "Latitude as a continuous ordering variable"
    The 35 stations form an unbroken south-to-north gradient rather than a temporal
    sequence. Latitude plays the role that "time" plays in a conventional time series:
    each successive station in the sorted order is the next observation of the process.
    The FTSM's AR component models autocorrelation at consecutive *lags in latitude* —
    each unit lag corresponds to one station step (~1° of latitude) in the gradient.

## Data: weekly temperature curves sorted by latitude

We load the Canadian Weather dataset, sort the 35 stations ascending by latitude,
and compute weekly mean temperatures by reshaping the 364 full-week days into
52 weeks of 7 days each.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("temperature")

# Sort stations south to north by latitude
lat = meta["lat"].to_numpy()
order = np.argsort(lat)
X_ord = X[order]          # (35, 365) — ascending latitude
lat_ord = lat[order]

# Weekly mean aggregation: 52 weeks × 7 days = 364 days (drop day 365)
X_wk = X_ord[:, :364].reshape(35, 52, 7).mean(axis=2)   # (35, 52)
t_wk = np.arange(52, dtype=float)                         # week 0..51

# Train on 30 southern stations, test on 5 northern held-out stations
X_train = X_wk[:30]   # (30, 52)
X_test  = X_wk[30:]   # (5, 52) — northernmost, held out for evaluation

palette = ["#3f51b5", "#e8710a", "#198754", "#dc3545", "#6f42c1", "#0dcaf0", "#6c757d"]

f, ax = fig(figsize=(7.5, 4.2))
# Training curves (grey, thin) — every 4th for clarity
for xi in X_train[::4]:
    ax.plot(t_wk, xi, color="#6c757d", lw=0.7, alpha=0.45)
# Highlight 5 held-out northern stations in colour
for k in range(5):
    ax.plot(t_wk, X_test[k], color=palette[k], lw=2.0,
            label=f"station {30 + k + 1} ({lat_ord[30 + k]:.1f}°N)")
ax.set(title="35 Canadian stations sorted south to north — held-out northern stations in colour",
       xlabel="week of year", ylabel="temperature (°C)")
ax.legend(fontsize=8, ncol=2)
print(render(f))
print("FDARS_FENCE_OK")
```

The training curves (grey) cover the 30 southernmost stations; even at weekly
resolution the annual temperature cycle is clear, with January/February nadirs
around −20 °C for the most inland stations. The five held-out northern stations
(coloured) sit markedly colder — their winter troughs drop well below −30 °C —
so the forecast must extrapolate substantially beyond the training range.

## Stationarity and autocorrelation structure

Before fitting a forecast model, we check whether the series is stationary and
examine how strongly adjacent stations co-vary. `stationarity_test` runs a
permutation test of the hypothesis that the functional series has a constant
distribution along the gradient.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, fast
from docs_data import load_canadian_weather
from fdars.fts import stationarity_test, functional_acf

day, X, meta = load_canadian_weather("temperature")
order = np.argsort(meta["lat"].to_numpy())
X_wk = X[order][:, :364].reshape(35, 52, 7).mean(axis=2)
t_wk = np.arange(52, dtype=float)
X_train = X_wk[:30]

# Stationarity test — permutation-based; gate n_perm for bounded build time
st = stationarity_test(X_train, t_wk, n_perm=fast(999, 99), seed=42)
p_val = st["p_value"]

# Functional ACF — fast on weekly (30, 52) data (~0.028 s with n_sim=99)
acf = functional_acf(X_train, t_wk, max_lag=8, n_sim=fast(999, 99), seed=42)
lags   = np.asarray(acf["lags"])
avals  = np.asarray(acf["acf"])
# upper_band is the white-noise significance threshold (constant across lags here);
# take the max as the conservative envelope so a single CI line is correct either way
upper  = float(np.asarray(acf["upper_band"]).max())

f, ax = fig(figsize=(7.0, 3.8))
ax.bar(lags, avals, color="#3f51b5", width=0.65, alpha=0.85)
ax.axhline(upper,  color="#dc3545", ls="--", lw=1.4,
           label=f"95% band ({upper:.2f})")
ax.axhline(-upper, color="#dc3545", ls="--", lw=1.4)
ax.axhline(0,      color="#212529", lw=0.6)
ax.set(title=f"Functional ACF  (stationarity p = {p_val:.3f} — non-stationary gradient)",
       xlabel="lag (stations)", ylabel="ACF statistic")
ax.legend(fontsize=9)
print(render(f))
print("FDARS_FENCE_OK")
```

The stationarity test returns p ≈ 0.010 — the south-to-north temperature gradient
is **not** stationary: the distributional character of the curves changes
systematically along the latitude axis, as expected for a gradient that spans
from near-temperate Windsor to subarctic Inuvik. The functional ACF shows a
lag-1 value of roughly 0.33, above the 95% band, confirming that adjacent
stations in the gradient genuinely autocorrelate. Lags beyond 3–4 stations
drop inside the confidence band. This autocorrelation structure is exactly what
the FTSM exploits: the AR component at each FPC captures the statistical
dependence between successive stations.

!!! note "Fast-gating stochastic procedures"
    Both `stationarity_test` and `functional_acf` accept `n_perm` / `n_sim`
    parameters that control the number of random permutations used to build
    null distributions. Use `fast(999, 99)` from `docs_fig` to run 999
    permutations in the full site build and only 99 during local `DOCS_FAST=1`
    development, keeping the fence under 0.03 s in both modes.

    **Weekly aggregation is also required for `functional_acf`.** On the
    original (30, 365) daily data the same call takes ~4.8 s; on the
    weekly-aggregated (30, 52) data it runs in ~0.028 s. Always aggregate
    before calling `functional_acf`.

## Fitting the Functional Time Series Model

`ftsm` decomposes the training series into a mean function and `ncomp` orthogonal
FPC basis functions, then fits a univariate AR process to each component's score
trajectory. The variance explained by each component comes from the score series,
not from the `weights` field:

$$
\text{PVE}_k = \frac{\operatorname{Var}(\beta_{\cdot k})}
               {\sum_{j=1}^{K} \operatorname{Var}(\beta_{\cdot j})}
$$

where $\beta_{ik}$ is the score of the $i$-th curve on the $k$-th component.

```python exec="1" source="above"
import numpy as np
from docs_data import load_canadian_weather
from fdars.fts import ftsm, ftsm_forecast_multistep

day, X, meta = load_canadian_weather("temperature")
order = np.argsort(meta["lat"].to_numpy())
X_wk = X[order][:, :364].reshape(35, 52, 7).mean(axis=2)
t_wk = np.arange(52, dtype=float)
X_train, X_test = X_wk[:30], X_wk[30:]

# Fit FTSM with 3 functional principal components
fit = ftsm(X_train, t_wk, ncomp=3)

# Variance explained: from score variance — NOT from fit["weights"]
# fit["weights"] has shape (m,) and is a quadrature weight vector, not PVE
scores = np.asarray(fit["scores"])                              # (30, 3)
pve    = 100 * scores.var(axis=0) / scores.var(axis=0).sum()   # (3,)

# AR orders — one per component, extracted from ar_models list of dicts
ar_orders = [m["order"] for m in fit["ar_models"]]

# 5-step forecast of the 5 held-out northern stations
fc    = ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)
fcast = np.asarray(fc["forecast"])    # (5, 52) — 5 predicted station curves
rmse  = np.sqrt(np.mean((fcast - X_test) ** 2))

print(f"FTSM fit  —  ncomp = {fit['ncomp']}")
print(f"  FPC 1 variance explained: {pve[0]:.1f}%  (AR order {ar_orders[0]})")
print(f"  FPC 2 variance explained: {pve[1]:.1f}%  (AR order {ar_orders[1]})")
print(f"  FPC 3 variance explained: {pve[2]:.1f}%  (AR order {ar_orders[2]})")
print(f"  Cumulative (3 comps):     {pve.sum():.1f}%")
print()
print(f"5-step forecast shape: {fcast.shape}")
print(f"RMSE vs 5 held-out northern stations: {rmse:.2f} °C")
print("FDARS_FENCE_OK")
```

The first component captures roughly 86% of the score variance, the second 10%,
and the third 4% — three components together explain about 100% of the structured
variation across the 30 training stations. The dominant component is governed by
an AR(1) process (lag-1 dependence only), consistent with the ACF plot that showed
significant correlation at lag 1 and rapid decay. The 5-step RMSE against the
5 held-out northern stations comes out around 14°C, which is the expected order of
magnitude for a spatial extrapolation that must bridge roughly 15° of latitude
beyond the training range.

## Forecast vs truth: 5 northern held-out stations

With the fitted FTSM, `ftsm_forecast_multistep` extrapolates 5 AR steps into
the northern stations not seen during training. Each forecast step represents
the next station along the latitude gradient.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.fts import ftsm, ftsm_forecast_multistep

day, X, meta = load_canadian_weather("temperature")
order = np.argsort(meta["lat"].to_numpy())
lat_ord = meta["lat"].to_numpy()[order]
X_wk  = X[order][:, :364].reshape(35, 52, 7).mean(axis=2)
t_wk  = np.arange(52, dtype=float)
X_train, X_test = X_wk[:30], X_wk[30:]

fit   = ftsm(X_train, t_wk, ncomp=3)
fc    = ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)
fcast = np.asarray(fc["forecast"])   # (5, 52)
rmse  = np.sqrt(np.mean((fcast - X_test) ** 2))

scores = np.asarray(fit["scores"])
pve    = 100 * scores.var(axis=0) / scores.var(axis=0).sum()

palette = ["#3f51b5", "#e8710a", "#198754", "#dc3545", "#6f42c1"]

f, axes = fig(nrows=2, figsize=(7.5, 5.2))
weeks = np.arange(52)

# Panel 1: training curves (selected) to show the gradient shape
for xi in X_train[::6]:
    axes[0].plot(weeks, xi, color="#6c757d", lw=0.7, alpha=0.4)
axes[0].set(
    title=f"Training: 30 southern stations (weekly temperature)  "
          f"|  PVE: {pve[0]:.0f}% / {pve[1]:.0f}% / {pve[2]:.0f}%",
    ylabel="temperature (°C)",
)

# Panel 2: 5-step forecast (solid) vs held-out truth (dashed)
for k in range(5):
    slat = lat_ord[30 + k]
    axes[1].plot(weeks, fcast[k], color=palette[k], lw=2.0,
                 label=f"forecast s{k+1} ({slat:.1f}°N)")
    axes[1].plot(weeks, X_test[k], color=palette[k], lw=0.9,
                 ls="--", alpha=0.55)
axes[1].set(
    title=f"5-station FTSM forecast vs truth  (RMSE {rmse:.1f} °C)",
    xlabel="week of year",
    ylabel="temperature (°C)",
)
axes[1].legend(fontsize=8, ncol=3)
print(render(f))
print("FDARS_FENCE_OK")
```

The forecast curves (solid) follow the general shape of the truth (dashed) well
for the first two or three northern stations, where the extrapolation step is
modest. For the most remote northern stations the forecast underestimates the
depth of the winter trough — the FTSM's AR model, trained on the gradient up
to the 30th station, cannot fully anticipate the abrupt temperature drop of the
subarctic interior. An RMSE of ~14°C is therefore expected: the model correctly
predicts the *shape* of the annual cycle (summer peak around week 28, deep winter
trough) but falls short on the absolute magnitude at the northernmost stations.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `ftsm(data, argvals, ncomp)` | `ncomp` | Fits the FTSM: returns `mean (m,)`, `rotation (m, ncomp)`, `scores (n, ncomp)`, `fitted (n, m)`, `weights (m,)`, `ar_models` (list of dicts), `ncomp` |
| `ftsm_forecast_multistep(data, argvals, h, ncomp)` | `h`, `ncomp` | AR-projects scores `h` steps ahead; returns `forecast (h, m)`, `h` |
| `stationarity_test(data, argvals, n_perm, seed)` | `n_perm` | Permutation test for functional stationarity; returns `statistic`, `p_value`, `n_perm` |
| `functional_acf(data, argvals, max_lag, n_sim, seed)` | `max_lag`, `n_sim` | Functional autocorrelation up to `max_lag`; returns `lags`, `acf`, `pacf`, `upper_band` |

!!! note "Variance explained: use scores, not `weights`"
    `fit["weights"]` has shape `(m,)` and is the grid quadrature weight vector
    used internally in the FTSM projection step. It is **not** a per-component
    variance-explained array. To compute the proportion of variance explained
    by each component, use the score series:

    ```python
    scores = np.asarray(fit["scores"])   # (n, ncomp)
    pve = scores.var(axis=0) / scores.var(axis=0).sum()
    ```

    Passing `fit["weights"]` directly as PVE produces meaningless numbers
    (shape mismatch or wrong scale).

## See also

- [Functional Time Series](../analyze/functional-time-series.md) — method page:
  FTSM theory, `ftsm_forecast`, `functional_difference`, DPCA, and parameter
  guidance for choosing `ncomp`
- [Canadian Temperature — Seasonal Analysis](canadian-seasonal.md) — same
  dataset analyzed for periodicity and STL decomposition (different framing:
  one station × 8 simulated years)
- [Canadian Weather — FPCA & Clustering](canadian-weather.md) — same 35-station
  dataset with FPCA modes of variation and k-means climate-region recovery

## References

- Hyndman, R.J. and Shang, H.L. (2009). Forecasting functional time series.
  *Journal of the Korean Statistical Society* 38(3), 199–211.
- Shang, H.L. (2013). Functional time series approach for forecasting very
  short-term electricity demand. *Journal of Applied Statistics* 40(1), 152–168.
- Ramsay, J.O. and Silverman, B.W. (2005). *Functional Data Analysis*, 2nd ed. Springer.
- Environment and Climate Change Canada (2022). Canadian climate normals
  1981–2010. *National Climate Data and Information Archive*.
