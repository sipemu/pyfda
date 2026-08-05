# Canadian Temperature: Annual Cycle Detection & Decomposition

**Dataset:** Canadian Weather — daily mean temperature (°C) over a 365-day year
for 35 weather stations, each tagged with its climatic region (Atlantic,
Continental, Pacific, Arctic).

Every station traces the same story: cold in January, warm in July, cold again
by December. That is a **seasonal cycle** with a period of roughly one year. This
case study treats each station as a periodic signal and asks three questions
`fdars.seasonal` can answer directly from the curve: *what is the period?* (period
detection), *how strongly seasonal is it?* (seasonal strength), and *what is left
once the cycle is removed?* (STL decomposition).

## The signals

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather

day, X, meta = load_canadian_weather("temperature")
region = meta["region"].to_numpy()
colors = {"Atlantic": "#3f51b5", "Continental": "#e8710a",
          "Pacific": "#198754", "Arctic": "#dc3545"}

f, ax = fig()
for r, c in colors.items():
    ax.plot(day, X[region == r].T, color=c, lw=1, alpha=0.55)
for r, c in colors.items():
    ax.plot([], [], color=c, label=r)
ax.set(title="Daily mean temperature, 35 Canadian stations",
       xlabel="day of year", ylabel="temperature (°C)")
ax.legend(ncol=2)
print(render(f))
```

Each curve is a single pass through one annual cycle: one trough, one peak. That
single-cycle structure matters below — it is exactly enough to *measure* the
annual period, but not enough to *decompose against* it.

## Detecting the period

`fdars.seasonal` offers several period detectors. All take a data matrix of
shape `(n, m)` and the argument grid, and return a dict whose `period` is
expressed in the units of `argvals` — here, **days**. The simplest and most
robust is `estimate_period_fft`, which locates the dominant peak of the FFT
periodogram.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.seasonal import estimate_period_fft

day, X, meta = load_canadian_weather("temperature")
X = np.ascontiguousarray(X, dtype=np.float64)      # detectors want (n, m) float64
day = np.ascontiguousarray(day, dtype=np.float64)

res = estimate_period_fft(X, day)
period = res["period"]

# periodogram: power vs candidate period, built the same way the detector does
n, m = X.shape
freqs = np.fft.rfftfreq(m, d=day[1] - day[0])
power = (np.abs(np.fft.rfft(X - X.mean(axis=1, keepdims=True), axis=1)) ** 2).mean(0)
periods = np.where(freqs > 0, 1.0 / np.maximum(freqs, 1e-9), np.inf)

sel = (periods >= 20) & (periods <= 500)
f, ax = fig()
ax.plot(periods[sel], power[sel], color="#3f51b5", lw=1.6)
ax.axvline(period, color="#dc3545", ls="--",
           label=f"detected period = {period:.0f} days")
ax.set(title="FFT periodogram of the temperature curves",
       xlabel="candidate period (days)", ylabel="mean spectral power")
ax.legend()
print(render(f))
```

The periodogram has a single towering spike at **365 days** — the annual cycle,
recovered from the raw curves with no calendar information supplied. `res` also
reports the `frequency`, peak `power`, and a `confidence` score.

`fdars.seasonal` also ships the **autoperiod** family (`autoperiod`,
`cfd_autoperiod`), which refine FFT candidates against the autocorrelation
function. On clean single-frequency signals they agree with the FFT to the grid
resolution, but they are more sensitive to the strong harmonic content of real
temperature curves:

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.seasonal import estimate_period_fft, autoperiod, cfd_autoperiod

day, X, meta = load_canadian_weather("temperature")
X = np.ascontiguousarray(X, dtype=np.float64)
day = np.ascontiguousarray(day, dtype=np.float64)

# a clean synthetic sine with a known 60-day period, for reference
t = np.ascontiguousarray(np.linspace(0, 360, 360), dtype=np.float64)
sine = np.ascontiguousarray(np.sin(2 * np.pi * t / 60.0)[None, :], dtype=np.float64)

rows = [
    ("temperature (real)", X, day),
    ("sine, period 60 (synthetic)", sine, t),
]
labels, fft_p, ap_p, cfd_p = [], [], [], []
for name, data, grid in rows:
    labels.append(name)
    fft_p.append(estimate_period_fft(data, grid)["period"])
    ap_p.append(autoperiod(data, grid)["period"])
    cfd_p.append(cfd_autoperiod(data, grid)["period"])

x = np.arange(len(labels)); w = 0.26
f, ax = fig(figsize=(6.4, 4.0))
ax.bar(x - w, fft_p, w, color="#3f51b5", label="estimate_period_fft")
ax.bar(x,     ap_p, w, color="#e8710a", label="autoperiod")
ax.bar(x + w, cfd_p, w, color="#198754", label="cfd_autoperiod")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set(title="Period detectors: agreement on clean vs. real signals",
       ylabel="detected period")
ax.legend()
print(render(f))
```

!!! note "Which detector to trust"
    On the clean sine all three detectors return **60** to the grid resolution.
    On the real curves `estimate_period_fft` returns **365**, while the
    autoperiod variants lock onto shorter sub-annual features (the ACF
    validation step is thrown off by the curves' trend and harmonics). For a
    strongly periodic signal with a single dominant frequency, the FFT
    periodogram is the safest choice; reach for the autoperiod family when you
    need autocorrelation-based confirmation of a *cleaner* signal.

## How strongly seasonal is each station?

`seasonal_strength` quantifies what fraction of a curve's variation the seasonal
cycle explains, on a 0–1 scale (the variance-based measure of Wang, Smith &
Hyndman). We pass the detected 365-day period and evaluate one station at a time.

```python exec="1" html="1" source="above"
import numpy as np, pandas as pd
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.seasonal import seasonal_strength

day, X, meta = load_canadian_weather("temperature")
X = np.ascontiguousarray(X, dtype=np.float64)
day = np.ascontiguousarray(day, dtype=np.float64)

strength = np.array([
    seasonal_strength(X[i:i + 1], day, 365.0) for i in range(X.shape[0])
])
by_region = pd.Series(strength).groupby(meta["region"].to_numpy()).mean()

colors = {"Atlantic": "#3f51b5", "Continental": "#e8710a",
          "Pacific": "#198754", "Arctic": "#dc3545"}
order = by_region.sort_values(ascending=False).index
f, ax = fig(figsize=(6.0, 4.0))
ax.bar(range(len(order)), by_region[order].values,
       color=[colors[r] for r in order])
ax.set_xticks(range(len(order))); ax.set_xticklabels(order)
ax.set_ylim(0.98, 1.0)
ax.set(title="Mean seasonal strength by region",
       ylabel="seasonal strength (variance method)")
print(render(f))
```

Every station scores above **0.98** — Canadian temperature is overwhelmingly
seasonal everywhere. The differences are tiny but consistent: the swing between
summer and winter dwarfs day-to-day noise in every region, and marginally more
so in the far north, where the annual amplitude is largest.

For a curve whose seasonality *changes over the year*,
`seasonal_strength_windowed` returns a strength value at each time point (length
`m`), and `seasonal_strength_wavelet` gives a wavelet-based scalar alternative.

## STL decomposition of a station

STL (Seasonal–Trend decomposition using Loess) splits a signal into
**trend + seasonal + remainder**. Here each station spans just *one* annual
cycle, so decomposing against a 365-day period leaves nothing for the seasonal
term — the whole arc is "trend." Instead we decompose against a shorter
**~30-day** period: the slow annual arc becomes the trend, month-scale
oscillation becomes the seasonal term, and daily weather noise is the remainder.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_canadian_weather
from fdars.seasonal import stl_decompose

day, X, meta = load_canadian_weather("temperature")
X = np.ascontiguousarray(X, dtype=np.float64)

i = int(np.where(meta["station"].to_numpy() == "Resolute")[0][0])  # an Arctic station
dec = stl_decompose(X[i:i + 1], 30)
trend = np.asarray(dec["trend"])[0]
seasonal = np.asarray(dec["seasonal"])[0]
remainder = np.asarray(dec["remainder"])[0]

f, axes = fig(nrows=4, figsize=(6.4, 6.4), sharex=True)
axes[0].plot(day, X[i], color="#212529", lw=1.4); axes[0].set_ylabel("observed")
axes[1].plot(day, trend, color="#3f51b5", lw=1.8); axes[1].set_ylabel("trend")
axes[2].plot(day, seasonal, color="#198754", lw=1.0); axes[2].set_ylabel("seasonal")
axes[3].plot(day, remainder, color="#dc3545", lw=1.0); axes[3].set_ylabel("remainder")
axes[3].set_xlabel("day of year")
axes[0].set_title(f"STL decomposition — {meta['station'].iloc[i]} (period 30)")
print(render(f))
```

The **trend** recovers the smooth annual arc — a deep winter trough rising to a
short Arctic summer. The **seasonal** term captures the small, repeating
month-scale ripple, and the **remainder** holds the irregular weather. The three
components sum back to the observed curve exactly (STL is an additive,
lossless decomposition).

!!! tip "Choosing the STL period"
    STL needs the series to contain **several** full periods to separate trend
    from seasonality. With one year of daily data, a sub-annual period (weekly to
    monthly) is the natural choice. If you had multiple years per station, period
    `365` would isolate the true annual cycle as the seasonal term.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `estimate_period_fft(data, argvals)` | — | Dominant period from the FFT periodogram; returns `period, frequency, power, confidence` |
| `autoperiod(data, argvals, n_candidates, gradient_steps)` | `n_candidates` | FFT candidates validated by autocorrelation |
| `cfd_autoperiod(data, argvals, cluster_tolerance, min_cluster_size)` | `cluster_tolerance` | Clustered-FFT autoperiod; also returns a list of `periods` |
| `seasonal_strength(data, argvals, period, method)` | `period`, `method` | 0–1 seasonal strength (`"variance"` or `"spectral"`) |
| `seasonal_strength_windowed(data, argvals, period, window_size)` | `window_size` | Time-varying strength, one value per point |
| `stl_decompose(data, period, s_window, t_window, robust)` | `period`, `robust` | Additive trend / seasonal / remainder split |

!!! note "Input shape"
    Every `fdars.seasonal` routine expects a **2-D** `(n, m)` array — pass a
    single curve as `X[i:i+1]`, not `X[i]`. The `period` returned by the
    detectors is in the units of `argvals`.

## See also

- [Weather curves: FPCA and clustering](canadian-weather.md) — the same stations,
  analysed as modes of variation rather than periodic signals.
- [Canadian precipitation](canadian-precipitation.md) — geographic drivers of a
  second weather variable.
