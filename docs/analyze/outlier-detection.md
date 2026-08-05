# Outlier Detection

Functional outliers come in three flavours:

| Type | Description | Example |
|---|---|---|
| **Magnitude** | The curve lies far above or below the bulk of the data | A temperature sensor reading 20 degrees higher than all others |
| **Shape** | The curve has an unusual pattern even if its overall level is normal | A growth curve that dips where all others rise |
| **Amplitude** | The curve has exaggerated peaks and troughs | A vibration signal with double the usual amplitude |

`fdars` provides three complementary methods that target different outlier types.

---

## LRT-based detection

A likelihood-ratio-test approach: each curve is scored by its distance from a robust
(trimmed) centre, and a bootstrap procedure builds the null distribution of the *maximum*
such distance under an outlier-free model. Curves whose distance exceeds the resulting
threshold are flagged. It targets **magnitude** outliers -- curves shifted up or down --
and is less sensitive to pure shape or amplitude anomalies.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.outliers import detect_outliers_lrt_with_dist

# Low-noise sinusoids with one magnitude outlier (curve 0 shifted up by 3)
rng = np.random.default_rng(1)
t = np.linspace(0, 1, 100)
X = np.array([np.sin(2 * np.pi * t) + rng.normal(0, 0.1, t.size) for _ in range(30)])
X[0] = np.sin(2 * np.pi * t) + 3.0

res = detect_outliers_lrt_with_dist(X, alpha=0.05, n_bootstrap=300, smo=0.1, seed=1)
null = np.asarray(res["null_distribution"])
thr = float(res["threshold"])
flagged = np.where(np.asarray(res["outliers"]))[0]

f, (a0, a1) = fig(1, 2, figsize=(11.0, 3.8))
for i, xi in enumerate(X):
    a0.plot(t, xi, color="#dc3545" if i in flagged else "#6c757d",
            lw=1.6 if i in flagged else 0.7, alpha=0.9 if i in flagged else 0.35)
a0.set(title=f"Curves (LRT flagged: {flagged.tolist()})", xlabel="t", ylabel="X(t)")

a1.hist(null, bins=25, color="#3f51b5", alpha=0.7)
a1.axvline(thr, color="#dc3545", ls="--", lw=1.6, label=f"threshold {thr:.1f}")
a1.set(title="Bootstrap null distribution of max distance",
       xlabel="max distance from robust centre", ylabel="count")
a1.legend()
print(render(f))
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Functional observations |
| `alpha` | `float` | `0.05` | Significance level |
| `n_bootstrap` | `int` | `200` | Number of bootstrap replicates for threshold estimation |
| `trim` | `float` | `0.1` | Trimming proportion for the robust mean |
| `smo` | `float` | `0.02` | Smoothing parameter for the likelihood ratio |

`detect_outliers_lrt` returns `{"outliers": bool[n], "threshold": float}`;
`detect_outliers_lrt_with_dist` additionally returns `null_distribution` (the bootstrap
max-distances used to set the threshold), as plotted above.

!!! warning "The LRT can mask a lone outlier at the default smoothing"
    Two behaviours are worth knowing before you trust a negative result:

    - **Smoothing matters.** With the default `smo=0.02`, even a large single magnitude
      outlier can go undetected; raising `smo` to about `0.1` restores detection in the
      example above. Sweep `smo` if the LRT reports nothing.
    - **Masking/swamping.** A single very extreme curve inflates the bootstrap null (it
      is resampled into the reference), pushing the threshold up so far that it hides
      itself. This is a known limitation of single-pass outlier tests; corroborate the LRT
      with the outliergram and the magnitude--shape plot below rather than relying on it
      alone.

!!! note "Depth-based detectors are R-only for now"
    The R reference also offers depth-based detectors (`outliers.depth.pond`,
    `outliers.depth.trim`) that flag curves with unusually low functional depth. These have
    **no Python binding** in the current `fdars` build. You can approximate the idea with
    `fdars.depth` (e.g. `modified_band_1d`) plus a quantile/MAD cutoff on the depths, but
    there is no packaged one-call equivalent yet.

---

## Outliergram (MEI vs MBD)

The outliergram plots the **Modified Epigraph Index** (MEI) against the **Modified Band Depth** (MBD) for every curve. Points that fall far from the parabolic relationship $\mathrm{MBD} = a_0 + a_1 \cdot \mathrm{MEI} + a_2 \cdot \mathrm{MEI}^2$ are flagged as shape outliers.

```python
from fdars.outliers import outliergram

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

The left panel shows the raw curves with a few injected anomalies; the right panel is
the outliergram itself, where flagged curves sit far from the central parabola.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.outliers import outliergram

t = np.linspace(0, 1, 100)
X = np.asarray(simulate(40, t, n_basis=5, seed=42))
X[0] += 6.0        # magnitude outlier
X[1] = -X[1]       # shape outlier (reversed)
X[2] *= 2.5        # amplitude outlier

og = outliergram(X, factor=1.5)
mei, mbd, flag = (np.asarray(og[k]) for k in ("mei", "mbd", "outliers"))

f, (a0, a1) = fig(1, 2, figsize=(11.0, 3.8))
for i, xi in enumerate(X):
    a0.plot(t, xi, color="#dc3545" if flag[i] else "#6c757d",
            lw=1.4 if flag[i] else 0.7, alpha=0.9 if flag[i] else 0.35)
a0.set(title="Curves (outliers in red)", xlabel="t", ylabel="X(t)")

a1.scatter(mei[~flag], mbd[~flag], s=22, color="#3f51b5", label="normal")
a1.scatter(mei[flag], mbd[flag], s=55, color="#dc3545", label="outlier")
a1.set(title="Outliergram (MEI vs MBD)", xlabel="MEI", ylabel="MBD")
a1.legend()
print(render(f))
```

!!! tip "Choosing the factor"
    A factor of 1.5 (the default) mirrors the classic boxplot rule. Increase it to 2.0 or 3.0 if you want to be more conservative and only flag extreme shape departures.

---

## Magnitude-shape outlyingness

This method decomposes each observation's outlyingness into a *magnitude* component and a *shape* component using the directional outlyingness framework. It is particularly effective at detecting curves that are unusual in shape even when their overall level is normal.

```python
from fdars.outliers import magnitude_shape

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

The magnitude-shape plot spreads outlyingness across two axes, so magnitude anomalies
separate horizontally and shape anomalies vertically.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.outliers import magnitude_shape

t = np.linspace(0, 1, 100)
X = np.asarray(simulate(40, t, n_basis=5, seed=42))
X[0] += 7.0        # magnitude outlier
X[1] = -X[1]       # shape outlier

ms = magnitude_shape(X)
mag, shp = np.asarray(ms["magnitude"]), np.asarray(ms["shape"])
flag = (mag > np.percentile(mag, 95)) | (shp > np.percentile(shp, 95))

f, ax = fig(figsize=(6.6, 4.2))
ax.scatter(mag[~flag], shp[~flag], s=26, color="#3f51b5", label="normal")
ax.scatter(mag[flag], shp[flag], s=60, color="#dc3545", label="flagged")
for i in (0, 1):
    ax.annotate(f"curve {i}", (mag[i], shp[i]), fontsize=9,
                color="#dc3545", xytext=(6, 4), textcoords="offset points")
ax.set(title="Magnitude-shape outlyingness",
       xlabel="magnitude outlyingness", ylabel="shape outlyingness")
ax.legend()
print(render(f))
```

---

## The three outlier types, in isolation

To see which method responds to which anomaly, inject a *single* outlier of each type
into an otherwise clean low-noise sinusoidal sample and show all three side by side: a
magnitude shift (+3), a shape inversion, and a 3x amplitude scaling.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render

t = np.linspace(0, 1, 100)

def clean(seed, n=30):
    rng = np.random.default_rng(seed)
    return np.array([np.sin(2 * np.pi * t) + rng.normal(0, 0.1, t.size) for _ in range(n)])

cases = [
    ("Magnitude (+3 shift)", lambda X: X.__setitem__(0, np.sin(2 * np.pi * t) + 3.0)),
    ("Shape (inverted)",     lambda X: X.__setitem__(0, -np.sin(2 * np.pi * t))),
    ("Amplitude (3x)",       lambda X: X.__setitem__(0, 3.0 * np.sin(2 * np.pi * t))),
]

f, axes = fig(1, 3, figsize=(12, 3.4), sharex=True)
for ax, (title, inject) in zip(axes, cases):
    X = clean(7)
    inject(X)
    ax.plot(t, X[1:].T, color="#6c757d", lw=0.6, alpha=0.4)
    ax.plot(t, X[0], color="#dc3545", lw=2.0, label="outlier")
    ax.set(title=title, xlabel="t")
    ax.legend(loc="upper right")
axes[0].set_ylabel("X(t)")
print(render(f))
```

The magnitude outlier stands off vertically (LRT territory), the shape outlier tracks the
same level but runs anti-phase (outliergram territory), and the amplitude outlier keeps
the same phase but oscillates harder. No single detector is best at all three, which is
why the recommendation below is to run more than one.

---

## Full example -- detect and visualize outliers

Run all three detectors on the same contaminated sample and compare what each flags.
We use a low-noise sinusoidal base (the regime where the LRT is well-behaved) with one
magnitude, one shape, and one amplitude outlier.

```python exec="1" source="above"
import numpy as np
from fdars.outliers import detect_outliers_lrt, outliergram, magnitude_shape

t = np.linspace(0, 1, 100)
rng = np.random.default_rng(42)
X = np.array([np.sin(2 * np.pi * t) + rng.normal(0, 0.1, t.size) for _ in range(30)])
X[0] = np.sin(2 * np.pi * t) + 3.0     # magnitude outlier
X[1] = -np.sin(2 * np.pi * t)          # shape outlier (inverted)
X[2] = 3.0 * np.sin(2 * np.pi * t)     # amplitude outlier

# LRT (raise smo so a lone magnitude outlier is not masked)
lrt = detect_outliers_lrt(X, alpha=0.05, n_bootstrap=300, smo=0.1)
print("LRT outliers        :", np.where(lrt["outliers"])[0].tolist())

# Outliergram (shape)
og = outliergram(X, factor=1.5)
print("Outliergram outliers:", np.where(np.asarray(og["outliers"]))[0].tolist())

# Magnitude-shape ranking
ms = magnitude_shape(X)
mag, shp = np.asarray(ms["magnitude"]), np.asarray(ms["shape"])
print("Top |magnitude| idx :", np.argsort(np.abs(mag))[-3:][::-1].tolist())
print("Top |shape| idx     :", np.argsort(np.abs(shp))[-3:][::-1].tolist())
```

!!! info "Which method to use?"
    - **LRT** (`detect_outliers_lrt`): magnitude outliers, but tune `smo` (≈0.1) and treat a
      negative result cautiously (masking). Use `detect_outliers_lrt_with_dist` when you
      want to see the bootstrap null.
    - **Outliergram** (`outliergram`): the go-to for shape outliers; interpretable 2D plot.
    - **Magnitude-shape** (`magnitude_shape`): decomposes outlyingness onto two axes, so you
      can tell *why* a curve is outlying.
    - Run at least two, and corroborate. No single functional detector catches every
      outlier type.

## See also

- [Tolerance bands](tolerance-bands.md) -- a curve outside a tolerance band is, by
  construction, an outlier relative to the fitted population.
- `fdars.depth` -- the band-depth and epigraph-index machinery underlying the outliergram.
