# Outlier Detection

Functional outliers come in three flavours:

| Type | Description | Example |
|---|---|---|
| **Magnitude** | The curve lies far above or below the bulk of the data | A temperature sensor reading 20 degrees higher than all others |
| **Shape** | The curve has an unusual pattern even if its overall level is normal | A growth curve that dips where all others rise |
| **Amplitude** | The curve has exaggerated peaks and troughs | A vibration signal with double the usual amplitude |

`pyfda` provides three complementary methods that target different outlier types.

---

## LRT-based detection

A likelihood-ratio test approach that compares the likelihood of the data with and without each candidate outlier. A bootstrap procedure determines the rejection threshold.

```python
import numpy as np
from pyfda import Fdata
from pyfda.simulation import simulate
from pyfda.outliers import detect_outliers_lrt

argvals = np.linspace(0, 1, 100)
fd = Fdata(simulate(50, argvals, n_basis=5, seed=1), argvals=argvals)

# Inject two magnitude outliers
fd.data[0] += 8.0
fd.data[1] -= 8.0

result = detect_outliers_lrt(fd.data, alpha=0.05, n_bootstrap=200, trim=0.1, smo=0.02)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `alpha` | `float` | `0.05` | Significance level |
| `n_bootstrap` | `int` | `200` | Number of bootstrap replicates for threshold estimation |
| `trim` | `float` | `0.1` | Trimming proportion for the robust mean |
| `smo` | `float` | `0.02` | Smoothing parameter for the likelihood ratio |

**Returns** a dictionary:

| Key | Type | Description |
|---|---|---|
| `outliers` | `ndarray (n,)` bool | `True` for each detected outlier |
| `threshold` | `float` | Computed rejection threshold |

```python
outlier_ids = np.where(result["outliers"])[0]
print(f"Outlier indices: {outlier_ids}")
print(f"Threshold: {result['threshold']:.4f}")
```

---

## Outliergram (MEI vs MBD)

The outliergram plots the **Modified Epigraph Index** (MEI) against the **Modified Band Depth** (MBD) for every curve. Points that fall far from the parabolic relationship $\mathrm{MBD} = a_0 + a_1 \cdot \mathrm{MEI} + a_2 \cdot \mathrm{MEI}^2$ are flagged as shape outliers.

```python
from pyfda.outliers import outliergram

result_og = outliergram(fd.data, factor=1.5)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `factor` | `float` | `1.5` | Outlier factor (analogous to the IQR multiplier in a boxplot) |

**Returns** a dictionary:

| Key | Shape | Description |
|---|---|---|
| `mei` | `(n,)` | Modified Epigraph Index |
| `mbd` | `(n,)` | Modified Band Depth |
| `outliers` | `(n,)` bool | Outlier flags |

!!! tip "Choosing the factor"
    A factor of 1.5 (the default) mirrors the classic boxplot rule. Increase it to 2.0 or 3.0 if you want to be more conservative and only flag extreme shape departures.

---

## Magnitude-shape outlyingness

This method decomposes each observation's outlyingness into a *magnitude* component and a *shape* component using the directional outlyingness framework. It is particularly effective at detecting curves that are unusual in shape even when their overall level is normal.

```python
from pyfda.outliers import magnitude_shape

result_ms = magnitude_shape(fd.data)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |

**Returns** a dictionary:

| Key | Shape | Description |
|---|---|---|
| `magnitude` | `(n,)` | Magnitude outlyingness score for each curve |
| `shape` | `(n,)` | Shape outlyingness score for each curve |

You can flag outliers by thresholding either component (e.g., values above the 97.5th percentile):

```python
mag_threshold = np.percentile(result_ms["magnitude"], 97.5)
shape_threshold = np.percentile(result_ms["shape"], 97.5)
mag_outliers = result_ms["magnitude"] > mag_threshold
shape_outliers = result_ms["shape"] > shape_threshold
print(f"Magnitude outliers: {np.where(mag_outliers)[0]}")
print(f"Shape outliers:     {np.where(shape_outliers)[0]}")
```

---

## Full example -- detect and visualize outliers

```python
import numpy as np
from pyfda import Fdata
from pyfda.simulation import simulate
from pyfda.outliers import detect_outliers_lrt, outliergram, magnitude_shape

# ── 1. Generate clean data + outliers ─────────────────────────
argvals = np.linspace(0, 1, 100)
fd = Fdata(simulate(50, argvals, n_basis=5, seed=42), argvals=argvals)

# Magnitude outlier
fd.data[0] += 7.0

# Shape outlier (reversed curve)
fd.data[1] = -fd.data[1]

# Amplitude outlier (exaggerated)
fd.data[2] *= 3.0

# ── 2. LRT detection ─────────────────────────────────────────
lrt = detect_outliers_lrt(fd.data, alpha=0.05, n_bootstrap=200)
print("LRT outliers:", np.where(lrt["outliers"])[0])

# ── 3. Outliergram ───────────────────────────────────────────
og = outliergram(fd.data, factor=1.5)
print("Outliergram outliers:", np.where(og["outliers"])[0])

# ── 4. Magnitude-shape ──────────────────────────────────────
ms = magnitude_shape(fd.data)
print(f"Top magnitude scores: indices {np.argsort(ms['magnitude'])[-3:][::-1]}")
print(f"Top shape scores:     indices {np.argsort(ms['shape'])[-3:][::-1]}")

# ── 5. Visualize (optional) ─────────────────────────────────
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Panel 1: data with LRT outliers highlighted
    ax = axes[0]
    for i in range(len(fd)):
        color = "red" if lrt["outliers"][i] else "steelblue"
        alpha = 1.0 if lrt["outliers"][i] else 0.15
        ax.plot(fd.argvals, fd.data[i], color=color, alpha=alpha, linewidth=0.8)
    ax.set_title("LRT outliers")

    # Panel 2: outliergram
    ax = axes[1]
    colors = ["red" if o else "steelblue" for o in og["outliers"]]
    ax.scatter(og["mei"], og["mbd"], c=colors, s=20)
    ax.set_xlabel("MEI")
    ax.set_ylabel("MBD")
    ax.set_title("Outliergram")

    # Panel 3: magnitude vs shape
    ax = axes[2]
    ax.scatter(ms["magnitude"], ms["shape"], s=20, c="steelblue")
    for idx in [0, 1, 2]:
        ax.annotate(str(idx), (ms["magnitude"][idx], ms["shape"][idx]),
                    fontsize=8, color="red")
    ax.set_xlabel("Magnitude outlyingness")
    ax.set_ylabel("Shape outlyingness")
    ax.set_title("Magnitude-Shape plot")

    plt.tight_layout()
    plt.savefig("outlier_detection.png", dpi=150)
    plt.show()
except ImportError:
    pass
```

!!! info "Which method to use?"
    - **LRT**: best all-round choice for magnitude outliers in moderate samples.
    - **Outliergram**: effective for shape outliers; provides an interpretable 2D plot.
    - **Magnitude-shape**: decomposes outlyingness into two axes, useful when you need to distinguish *why* a curve is outlying.
