# Andrews Wine: Outlier Detection

**Dataset:** UCI Wine — 13 chemical measurements for 178 wines from three
cultivars, encoded as [Andrews curves](andrews-wine-intro.md) so that
multivariate outlier detection can run through functional tools.

A wine is a *multivariate* outlier if its combination of 13 measurements is
atypical — not necessarily extreme in any single column, but unusual as a whole.
Detecting that directly in 13-D is awkward. Once each wine is an Andrews curve,
though, "atypical row" becomes "atypical curve", and `fdars` offers several
robust functional outlier detectors. Because the Andrews transform preserves
$L^2$ distances (Parseval), a curve that is central among the curves corresponds
to a wine that is central among the rows. This page runs functional **depth**,
**magnitude–shape** analysis, the **outliergram**, and a **likelihood-ratio**
test on the wine curves and cross-checks what they flag.

!!! warning "No `andrews` binding in fdars"
    The transform is the same numpy helper introduced on the
    [intro page](andrews-wine-intro.md); `fdars` handles everything after the
    curves exist. We z-score the 13 columns before transforming so no single
    feature dominates the curve.

## Depth ranks wines by centrality

Functional **depth** scores each curve by how central it is within the sample —
high depth is typical, low depth is outlying. We use `modified_band_1d` from
[`fdars.depth`](../represent/depth-functions.md), which computes the modified
band depth of every curve against the whole set.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.depth import modified_band_1d

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

names, X, meta = load_wine()
Xz = (X - X.mean(0)) / X.std(0)
t = np.linspace(-np.pi, np.pi, 160)
curves = andrews_curves(Xz, t)

depth = np.asarray(modified_band_1d(curves, curves))
order = np.argsort(depth)                       # shallow (outlying) first
rng_d = np.ptp(depth) + 1e-9

f, ax = fig()
for i in order:                                 # faint = shallow
    ax.plot(t, curves[i], color="#3f51b5", lw=1.0,
            alpha=0.12 + 0.75 * (depth[i] - depth.min()) / rng_d)
ax.plot(t, curves[order[-1]], color="#198754", lw=2.4, label="deepest (typical)")
ax.plot(t, curves[order[0]],  color="#dc3545", lw=2.4, label="shallowest")
ax.set(title="Modified band depth of the wine Andrews curves",
       xlabel="t", ylabel=r"$f_x(t)$")
ax.legend()
print(render(f))
```

The deepest curve is a thoroughly ordinary wine; the shallowest (red) rides the
edge of the bundle. Depth gives a *ranking*, not a yes/no verdict — for a
decision rule we turn to the magnitude–shape plot.

## Magnitude–shape: two axes of "unusual"

An outlying curve can be unusual in **magnitude** (shifted up or down) or in
**shape** (wiggling differently), and these call for different explanations.
`fdars.outliers.magnitude_shape` returns a magnitude outlyingness and a shape
outlyingness per curve; plotting one against the other separates the two failure
modes.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.outliers import magnitude_shape

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

names, X, meta = load_wine()
cultivar = meta["cultivar"].to_numpy()
Xz = (X - X.mean(0)) / X.std(0)
t = np.linspace(-np.pi, np.pi, 160)
curves = andrews_curves(Xz, t)

ms = magnitude_shape(curves)
mag = np.asarray(ms["magnitude"])
shp = np.asarray(ms["shape"])

# robust (median / MAD) combined score to rank the most extreme wines
def z(v):
    med = np.median(v)
    mad = np.median(np.abs(v - med)) * 1.4826 + 1e-9
    return (v - med) / mad
score = np.hypot(z(mag), z(shp))
flag = np.argsort(score)[-6:]                   # 6 most extreme

palette = {1: "#3f51b5", 2: "#e8710a", 3: "#198754"}
f, ax = fig()
ax.scatter(mag, shp, c=[palette[c] for c in cultivar], s=30,
           alpha=0.7, edgecolor="white", linewidth=0.4)
ax.scatter(mag[flag], shp[flag], facecolor="none", edgecolor="#dc3545",
           s=140, linewidth=1.8, label="6 most extreme")
for i in flag:
    ax.annotate(str(i), (mag[i], shp[i]), fontsize=8,
                xytext=(4, 3), textcoords="offset points")
ax.set(title="Magnitude–shape plot of the wine curves",
       xlabel="magnitude outlyingness", ylabel="shape outlyingness")
ax.legend()
print(render(f))
```

Most wines cluster in a dense blob; the flagged points sit far out on the
**shape** axis, meaning their curves bend differently from the crowd rather than
merely sitting high or low. The colours show these extreme wines are not
confined to one cultivar.

## The outliergram: a built-in decision rule

The **outliergram** plots each curve's modified band depth against its modified
epigraph index and derives a parabolic reference region; curves that fall below
it are flagged as **shape** outliers. Unlike the magnitude–shape score above, it
returns an explicit boolean flag, so it makes the actual call.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.outliers import outliergram

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

names, X, meta = load_wine()
cultivar = meta["cultivar"].to_numpy()
Xz = (X - X.mean(0)) / X.std(0)
t = np.linspace(-np.pi, np.pi, 160)
curves = andrews_curves(Xz, t)

og = outliergram(curves)
mei = np.asarray(og["mei"])
mbd = np.asarray(og["mbd"])
flagged = np.asarray(og["outliers"], dtype=int)   # indices of outlying curves

f, (axL, axR) = fig(ncols=2, figsize=(9.2, 3.6))
axL.scatter(mei, mbd, color="#3f51b5", s=26, alpha=0.7, edgecolor="white")
if flagged.size:
    axL.scatter(mei[flagged], mbd[flagged], color="#dc3545", s=60,
                label="flagged", zorder=3)
    axL.legend()
axL.set(title="Outliergram", xlabel="modified epigraph index",
        ylabel="modified band depth")

for i in range(curves.shape[0]):
    axR.plot(t, curves[i], color="#c9ccd6", lw=0.7, alpha=0.5)
for i in flagged:
    axR.plot(t, curves[i], color="#dc3545", lw=2.2)
axR.set(title=f"{flagged.size} outlying wines highlighted",
        xlabel="t", ylabel=r"$f_x(t)$")
print(render(f))
```

The outliergram flags a small number of wines (their curves shown in red on the
right). Reassuringly, these overlap with the shallowest-depth and highest
magnitude–shape wines from the previous figures — three different detectors
agreeing on the same handful of atypical bottles.

## A likelihood-ratio test for outliers

`detect_outliers_lrt` takes a more formal, hypothesis-testing route: it
bootstraps a null distribution and flags curves whose likelihood-ratio statistic
exceeds a data-driven threshold at level `alpha`.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.outliers import detect_outliers_lrt

def andrews_curves(features, t):
    features = np.asarray(features, float)
    n, p = features.shape
    out = np.full((n, t.size), features[:, [0]] / np.sqrt(2.0))
    for j in range(1, p):
        harmonic = (j + 1) // 2
        term = np.sin if j % 2 == 1 else np.cos
        out = out + features[:, [j]] * term(harmonic * t)
    return out

names, X, meta = load_wine()
Xz = (X - X.mean(0)) / X.std(0)
t = np.linspace(-np.pi, np.pi, 160)
curves = andrews_curves(Xz, t)

res = detect_outliers_lrt(curves, alpha=0.05, n_bootstrap=200)
mask = np.asarray(res["outliers"], dtype=bool)
n_flag = int(mask.sum())

f, ax = fig()
for i in range(curves.shape[0]):
    ax.plot(t, curves[i], color="#c9ccd6", lw=0.7, alpha=0.5)
for i in np.where(mask)[0]:
    ax.plot(t, curves[i], color="#dc3545", lw=2.2)
title = (f"LRT flags {n_flag} wines (threshold {res['threshold']:.2f})"
         if n_flag else
         f"LRT flags no wines at α=0.05 (threshold {res['threshold']:.2f})")
ax.set(title=title, xlabel="t", ylabel=r"$f_x(t)$")
print(render(f))
```

!!! note "A conservative test on a clean data set"
    On these curves `detect_outliers_lrt` flags **no** wines at $\alpha = 0.05$:
    the wine measurements are genuinely well-behaved once standardized, so no
    curve is extreme enough to reject the null of "same distribution". That is
    the honest result, not a failure — the LRT is a stricter, distributional
    test than the depth-based outliergram, which flags borderline *shape*
    anomalies that the LRT does not consider significant. When detectors
    disagree like this, the disagreement itself is informative: the flagged
    wines are mildly unusual in shape but not distributional outliers.

## What the detectors found

| Method | Binding | Output | On the wine curves |
|--------|---------|--------|--------------------|
| Modified band depth | `depth.modified_band_1d` | centrality score per curve | ranking; shallowest wines are borderline |
| Magnitude–shape | `outliers.magnitude_shape` | `magnitude`, `shape` per curve | extreme wines are *shape*-unusual |
| Outliergram | `outliers.outliergram` | `mei`, `mbd`, `outliers` (flags) | flags a small handful of shape outliers |
| LRT | `outliers.detect_outliers_lrt` | `outliers` mask, `threshold` | none significant at α=0.05 |

The picture is consistent: a *few* wines (the same ones across depth, MS and the
outliergram) are mildly atypical in curve **shape**, but none are strong enough
to register as distributional outliers. For a quality-control setting where you
*expect* some bottles to be off-spec, see the [QC page](andrews-wine-qc.md),
which monitors one cultivar against another with control charts.

## See also

- [Functional depth](../represent/depth-functions.md) — the depth measures used here.
- [Andrews Wine intro](andrews-wine-intro.md) — the transform and class structure.
- [Clustering & variable importance](andrews-wine-clustering.md) — recovering the cultivars.
