# Seasonal Analysis

Many real-world functional datasets exhibit periodic patterns -- daily temperature cycles, weekly traffic flows, annual growth curves. The seasonal analysis module provides tools for detecting, decomposing, and measuring periodicity in functional data.

---

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

# ── 6. Visualize (optional) ──────────────────────────────────
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    i = 0  # show first observation

    axes[0].plot(fd.argvals, fd.data[i], linewidth=0.7)
    axes[0].set_ylabel("Original")

    axes[1].plot(fd.argvals, decomp["trend"][i])
    axes[1].set_ylabel("Trend")

    axes[2].plot(fd.argvals, decomp["seasonal"][i])
    axes[2].set_ylabel("Seasonal")

    axes[3].plot(fd.argvals, decomp["remainder"][i])
    axes[3].set_ylabel("Remainder")
    axes[3].set_xlabel("t")

    fig.suptitle("STL Decomposition")
    plt.tight_layout()
    plt.savefig("seasonal_analysis.png", dpi=150)
    plt.show()
except ImportError:
    pass
```
