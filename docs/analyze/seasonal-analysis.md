# Seasonal Analysis

Many real-world functional datasets exhibit periodic patterns -- daily temperature cycles, weekly traffic flows, annual growth curves. The seasonal analysis module provides tools for detecting, decomposing, and measuring periodicity in functional data.

---

![Seasonal Analysis — concept diagram](../assets/diagrams/seasonal-analysis.svg){ .fdars-diagram }

## Period detection

`fdars` offers three period-detection algorithms, each with different strengths:

### SAZED

SAZED (Seasonal And Zero-crossing Estimation of Periodicity via Distance) combines multiple period estimates from different signal features (zero crossings, peaks, autocorrelation) and returns a consensus period.

```python
import numpy as np
from fdars import Fdata
from fdars.seasonal import sazed

argvals = np.linspace(0, 10, 500)
# Create data with a known period
fd = Fdata(
    np.sin(2 * np.pi * argvals / 2.5)[None, :] + np.random.default_rng(1).normal(0, 0.1, (10, 500)),
    argvals=argvals,
)

result = sazed(fd.data, fd.argvals, tolerance=0.05)
print(f"Detected period: {result['period']:.3f}")
print(f"Confidence:      {result['confidence']:.3f}")
print(f"Agreeing comps:  {result['agreeing_components']}")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation points |
| `tolerance` | `float` | `0.05` | Relative tolerance for period matching |

**Returns** a dictionary:

| Key | Type | Description |
|---|---|---|
| `period` | `float` | Estimated period |
| `confidence` | `float` | Confidence score (fraction of agreeing components) |
| `agreeing_components` | `int` | Number of estimation methods that agree |

### Autoperiod

Uses FFT peak detection followed by autocorrelation validation. Best for clean, well-defined periodic signals.

```python
from fdars.seasonal import autoperiod

result_ap = autoperiod(fd.data, fd.argvals, n_candidates=5, gradient_steps=10)
print(f"Period: {result_ap['period']:.3f}")
print(f"FFT power: {result_ap['fft_power']:.3f}")
print(f"ACF validation: {result_ap['acf_validation']:.3f}")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation points |
| `n_candidates` | `int` | `5` | Maximum number of FFT peaks to consider |
| `gradient_steps` | `int` | `10` | Gradient ascent refinement steps |

**Returns** a dictionary:

| Key | Type | Description |
|---|---|---|
| `period` | `float` | Estimated period |
| `confidence` | `float` | Confidence score |
| `fft_power` | `float` | Spectral power at the detected frequency |
| `acf_validation` | `float` | Autocorrelation validation score |

### CFD Autoperiod

A cluster-based variant of autoperiod that can detect *multiple* periodicities simultaneously.

```python
from fdars.seasonal import cfd_autoperiod

result_cfd = cfd_autoperiod(fd.data, fd.argvals, cluster_tolerance=0.1, min_cluster_size=1)
print(f"Primary period: {result_cfd['period']:.3f}")
print(f"All periods:    {result_cfd['periods']}")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation points |
| `cluster_tolerance` | `float` | `0.1` | Tolerance for clustering candidate periods |
| `min_cluster_size` | `int` | `1` | Minimum cluster size to keep |

**Returns** a dictionary:

| Key | Type | Description |
|---|---|---|
| `period` | `float` | Primary (strongest) period |
| `confidence` | `float` | Confidence for the primary period |
| `periods` | `ndarray` | All detected periods |
| `confidences` | `ndarray` | Confidence for each detected period |

---

## Peak detection

Locate peaks in each functional observation, optionally smoothing the data first. The function also estimates the mean period from inter-peak distances.

```python
from fdars.seasonal import detect_peaks

peaks = detect_peaks(
    fd.data, fd.argvals,
    min_distance=0.5,
    min_prominence=0.1,
    smooth_first=True,
    smooth_nbasis=20,
)
print(f"Mean period from peaks: {peaks['mean_period']:.3f}")

# Peaks for the first observation: list of (time, value, prominence) tuples
for t, v, p in peaks["peaks"][0]:
    print(f"  t={t:.2f}  value={v:.3f}  prominence={p:.3f}")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `min_distance` | `float` | `None` | Minimum distance between consecutive peaks |
| `min_prominence` | `float` | `None` | Minimum peak prominence |
| `smooth_first` | `bool` | `False` | Smooth data before detection |
| `smooth_nbasis` | `int` | `None` | Number of basis functions for smoothing |

**Returns** a dictionary:

| Key | Type | Description |
|---|---|---|
| `peaks` | `list[list[tuple]]` | Per-observation list of `(time, value, prominence)` tuples |
| `mean_period` | `float` | Mean inter-peak distance across all observations |

---

## STL decomposition

Seasonal and Trend decomposition using Loess (STL) splits each functional observation into trend, seasonal, and remainder components.

```python
from fdars.seasonal import stl_decompose

decomp = stl_decompose(fd.data, period=25, robust=False)
# decomp["trend"]     shape (n, m)
# decomp["seasonal"]  shape (n, m)
# decomp["remainder"] shape (n, m)
```

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.seasonal import stl_decompose

rng = np.random.default_rng(1)
t = np.linspace(0, 12, 300)
signal = 0.15 * t + 1.5 * np.sin(2 * np.pi * t / 2.0)
X = signal[None, :] + rng.normal(0, 0.15, (6, 300))

period_pts = int(round(2.0 / (t[1] - t[0])))
d = stl_decompose(X, period=period_pts)
trend, seasonal, remainder = (np.asarray(d[k])[0] for k in
                              ("trend", "seasonal", "remainder"))

f, axes = fig(4, 1, figsize=(8.0, 6.4), sharex=True)
rows = [("Original", X[0], "#3f51b5"), ("Trend", trend, "#e8710a"),
        ("Seasonal", seasonal, "#198754"), ("Remainder", remainder, "#6c757d")]
for ax, (name, y, color) in zip(axes, rows):
    ax.plot(t, y, color=color, lw=1.1)
    ax.set_ylabel(name)
axes[0].set_title("STL decomposition of a seasonal curve")
axes[-1].set_xlabel("t")
print(render(f))
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `period` | `int` | -- | Seasonal period (in grid points) |
| `s_window` | `int` | `None` | Seasonal smoothing window (auto if `None`) |
| `t_window` | `int` | `None` | Trend smoothing window (auto if `None`) |
| `robust` | `bool` | `False` | Use robust (re-weighted) fitting |

**Returns** a dictionary:

| Key | Shape | Description |
|---|---|---|
| `trend` | `(n, m)` | Trend component |
| `seasonal` | `(n, m)` | Seasonal component |
| `remainder` | `(n, m)` | Remainder (residual) |

---

## Seasonal strength

Quantify how strongly seasonal a signal is, using either a variance-based or spectral method. The returned value lies in $[0, 1]$, where 0 means no seasonality and 1 means a purely periodic signal.

```python
from fdars.seasonal import seasonal_strength

strength = seasonal_strength(fd.data, fd.argvals, period=2.5, method="variance")
print(f"Seasonal strength (variance): {strength:.3f}")

strength_spec = seasonal_strength(fd.data, fd.argvals, period=2.5, method="spectral")
print(f"Seasonal strength (spectral): {strength_spec:.3f}")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `argvals` | `ndarray (m,)` | -- | Evaluation points |
| `period` | `float` | -- | Estimated period |
| `method` | `str` | `"variance"` | `"variance"` or `"spectral"` |

**Returns** a `float` -- the seasonal strength.

Scanning the candidate period reveals sharp peaks at the true period and its harmonics,
which is exactly how period-detection methods locate the dominant cycle.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.seasonal import seasonal_strength

rng = np.random.default_rng(5)
t = np.linspace(0, 12, 400)
X = (1.5 * np.sin(2 * np.pi * t / 2.0))[None, :] + rng.normal(0, 0.2, (8, 400))

periods = np.linspace(0.75, 4.5, 60)
strength = [float(seasonal_strength(X, t, period=float(p), method="variance"))
            for p in periods]

f, ax = fig(figsize=(7.4, 3.6))
ax.plot(periods, strength, color="#3f51b5", lw=1.8)
ax.axvline(2.0, color="#e8710a", ls="--", lw=1.4, label="true period = 2.0")
ax.set(title="Seasonal strength vs. candidate period",
       xlabel="candidate period", ylabel="seasonal strength")
ax.legend()
print(render(f))
```

---

## Detrend first: trends mask seasonality

A strong trend swamps the periodic component: period detection returns the series length
(or `nan`) and seasonal strength collapses to near zero. **Detrend before analysing.** The
current Python build has no packaged `detrend`, so we remove a linear trend by hand with a
least-squares fit -- after which the period and strength are recovered.

```python exec="1" source="above"
import numpy as np
from fdars.seasonal import sazed, seasonal_strength

rng = np.random.default_rng(1)
t = np.linspace(0, 20, 400)
X = 5 + 2 * t + np.sin(2 * np.pi * t / 2.5) + rng.normal(0, 0.3, t.size)  # strong trend

# Without detrending: period and strength are wrong
p_raw = sazed(X[None, :], t)["period"]
s_raw = seasonal_strength(X[None, :], t, period=2.5, method="variance")
print(f"With trend   -> period={p_raw:.3f} (true 2.5), strength={s_raw:.3f}")

# Manual linear detrend: subtract the least-squares line
A = np.vstack([t, np.ones_like(t)]).T
X_det = X - A @ np.linalg.lstsq(A, X, rcond=None)[0]

p_det = sazed(X_det[None, :], t)["period"]
s_det = seasonal_strength(X_det[None, :], t, period=2.5, method="variance")
print(f"Detrended    -> period={p_det:.3f} (true 2.5), strength={s_det:.3f}")
```

!!! warning "No packaged detrend binding"
    The R reference ships a `detrend()` helper (linear / polynomial / LOESS / differencing
    / auto) and a `detrend_method` argument on many functions. Those are **not** exposed in
    the current Python build. Detrend manually (a least-squares line as above, a polynomial
    fit, or first differences) before calling the seasonal routines when a trend is present.

---

## Time-varying seasonal strength

For a long record whose periodicity switches on or off, a single strength number is
misleading. `seasonal_strength_windowed` slides a window along the series and reports the
local strength, exposing exactly when the seasonality appears or vanishes.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.seasonal import seasonal_strength_windowed

rng = np.random.default_rng(1)
t = np.linspace(0, 40, 800)
# Seasonal for t < 20, then pure noise
X = np.where(t < 20,
             np.sin(2 * np.pi * t / 2.5) + rng.normal(0, 0.2, t.size),
             rng.normal(0, 0.5, t.size))

strength = np.asarray(
    seasonal_strength_windowed(X[None, :], t, period=2.5, window_size=10.0, method="variance"))

f, (a0, a1) = fig(2, 1, figsize=(8.0, 4.6), sharex=True)
a0.plot(t, X, color="#6c757d", lw=0.7)
a0.axvline(20, color="#dc3545", ls="--", lw=1.4)
a0.set(ylabel="signal", title="Seasonality stops at t = 20")
a1.plot(t, strength, color="#3f51b5", lw=1.8)
a1.axvline(20, color="#dc3545", ls="--", lw=1.4, label="cessation")
a1.set(xlabel="t", ylabel="seasonal strength", ylim=(0, 1.02))
a1.legend()
print(render(f))
```

The strength curve stays high while the sinusoid is present and drops sharply once the
signal becomes noise -- a direct read-out of *when* seasonality is active.

---

## Classifying the seasonality

`classify_seasonality` combines seasonal strength with peak-timing variability to label a
series as `StableSeasonal`, `VariableTiming`, `IntermittentSeasonal`, or `NonSeasonal`.

```python exec="1" source="above"
import numpy as np
from fdars.seasonal import classify_seasonality

rng = np.random.default_rng(0)
t = np.linspace(0, 20, 400)

signals = {
    "clean sinusoid": np.sin(2 * np.pi * t / 2.0) + rng.normal(0, 0.05, t.size),
    "half seasonal":  0.5 * np.sin(2 * np.pi * t / 2.0) + 0.5 * rng.normal(0, 1, t.size),
    "pure noise":     rng.normal(0, 1, t.size),
}

for name, X in signals.items():
    r = classify_seasonality(X[None, :], t, period=2.0)
    print(f"{name:15s} -> {r['classification']:20s} "
          f"strength={r['seasonal_strength']:.2f}  seasonal={r['is_seasonal']}")
```

The returned dictionary also carries `timing_variability`, `has_stable_timing`, and
per-cycle `cycle_strengths`, so you can dig into *why* a series earned its label. For the
raw timing analysis alone, `analyze_peak_timing` reports the mean, spread, and trend of
peak positions across cycles; for smoothly drifting frequencies, `instantaneous_period`
returns a Hilbert-based period at every time point (unreliable near the series ends).

---

## Full example -- detect period, decompose, and measure strength

```python
import numpy as np
from fdars import Fdata
from fdars.seasonal import sazed, stl_decompose, seasonal_strength, detect_peaks

# ── 1. Create seasonal data ──────────────────────────────────
rng = np.random.default_rng(42)
argvals = np.linspace(0, 20, 1000)
trend = 0.05 * argvals
seasonal = np.sin(2 * np.pi * argvals / 4.0)
fd = Fdata(
    (trend + seasonal)[None, :] + rng.normal(0, 0.15, (15, 1000)),
    argvals=argvals,
)

# ── 2. Detect the period ─────────────────────────────────────
detected = sazed(fd.data, fd.argvals)
print(f"Detected period: {detected['period']:.2f}  (true = 4.0)")

# ── 3. Decompose ─────────────────────────────────────────────
period_pts = int(round(detected["period"] / (fd.argvals[1] - fd.argvals[0])))
decomp = stl_decompose(fd.data, period=period_pts)
print(f"Trend range:     [{decomp['trend'][0].min():.2f}, {decomp['trend'][0].max():.2f}]")
print(f"Seasonal range:  [{decomp['seasonal'][0].min():.2f}, {decomp['seasonal'][0].max():.2f}]")

# ── 4. Measure strength ──────────────────────────────────────
s = seasonal_strength(fd.data, fd.argvals, period=detected["period"])
print(f"Seasonal strength: {s:.3f}")

# ── 5. Find peaks ────────────────────────────────────────────
pk = detect_peaks(fd.data, fd.argvals, smooth_first=True, smooth_nbasis=30)
print(f"Mean inter-peak distance: {pk['mean_period']:.2f}")
```

## See also

- [Covariance functions](covariance-functions.md) -- the second-order structure of a
  functional sample, complementary to the periodic structure analysed here.
- `fdars.basis` -- Fourier bases for smoothing periodic signals before peak detection.
