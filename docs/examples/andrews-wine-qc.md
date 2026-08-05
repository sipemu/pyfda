# Andrews Wine: Quality Control

**Dataset:** UCI Wine — 13 chemical measurements for 178 wines from three
cultivars, encoded as [Andrews curves](andrews-wine-intro.md).

Quality control asks a different question from clustering: given a batch of wines
we *know* are good, would a new bottle raise a flag? We turn the three-cultivar
wine data into a QC scenario by declaring **cultivar 1 the in-control reference**
— the wine we are supposed to be producing — and asking whether wines from the
other cultivars would be caught as **out-of-spec**. Once each wine is an Andrews
curve, `fdars` gives two complementary monitors: a **tolerance band** (a coverage
region for good curves) and a **statistical process-control** chart (Hotelling
$T^2$ and squared prediction error on functional PCA scores).

!!! warning "No `andrews` binding in fdars"
    The transform is the numpy helper from the
    [intro page](andrews-wine-intro.md). We z-score the 13 columns first so no
    single feature dominates the curve. Note the standardization uses the *whole*
    data set's column statistics — a real deployment would fix them from the
    reference batch alone.

## The reference process

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.fdata import mean_1d

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

ref = curves[cultivar == 1]                  # in-control reference batch
mu = np.asarray(mean_1d(ref))

f, ax = fig()
ax.plot(t, ref.T, color="#3f51b5", lw=0.8, alpha=0.4)
ax.plot(t, mu, color="#0d1b52", lw=2.4, label="reference mean")
ax.set(title=f"In-control reference: {ref.shape[0]} cultivar-1 wines",
       xlabel="t", ylabel=r"$f_x(t)$")
ax.legend()
print(render(f))
```

These are the "good" wines. Everything downstream is calibrated on this bundle.

## A tolerance band from functional PCA

`fpca_tolerance_band` builds a band that, with confidence, covers a target
fraction (`coverage`) of curves from the same process. It decomposes the
reference curves into `ncomp` functional principal components and bootstraps the
band width. A new wine whose curve leaves the band is flagged.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.tolerance import fpca_tolerance_band

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

ref = curves[cultivar == 1]
test = curves[cultivar == 3]                 # a different grape = off-spec

band = fpca_tolerance_band(ref, ncomp=3, nb=800, coverage=0.95)
lo, hi = np.asarray(band["lower"]), np.asarray(band["upper"])

def breaches(C):
    return np.mean([(C[i] > hi).any() or (C[i] < lo).any() for i in range(len(C))])

f, ax = fig()
ax.fill_between(t, lo, hi, color="#3f51b5", alpha=0.18,
                label="95% tolerance band (cultivar 1)")
ax.plot(t, np.asarray(band["center"]), color="#0d1b52", lw=1.6)
for i in range(test.shape[0]):
    ax.plot(t, test[i], color="#dc3545", lw=0.7, alpha=0.5)
ax.set(title=f"Cultivar-3 wines vs cultivar-1 band "
             f"({breaches(test)*100:.0f}% breach)",
       xlabel="t", ylabel=r"$f_x(t)$")
ax.legend()
print(render(f))
```

The band covers about 98% of the reference wines themselves (close to its 95%
target), but **every** cultivar-3 wine leaves it — their curves sit visibly below
the reference band near $t=0$. As a go/no-go gate, the tolerance band cleanly
rejects the wrong grape.

## Statistical process control: $T^2$ and SPE charts

A tolerance band flags pointwise excursions; SPC instead reduces each curve to a
few functional-PCA scores and monitors two summary statistics:

- **Hotelling $T^2$** — how far the in-model scores are from the reference
  centre (a deviation *within* the principal-component subspace).
- **SPE** (squared prediction error, or $Q$) — how much of the curve lies
  *outside* that subspace (a new kind of variation the reference never showed).

`spm_phase1` calibrates the model and both control limits on the reference batch;
`spm_monitor` then scores new wines against those fixed limits.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.spm import spm_phase1, spm_monitor

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

ref = curves[cultivar == 1]
new = curves[cultivar == 3]

ph1 = spm_phase1(ref, t, ncomp=3, alpha=0.05)
mon = spm_monitor(ph1["mean"], ph1["loadings"], ph1["weights"],
                  ph1["eigenvalues"], ph1["t2_limit"], ph1["spe_limit"],
                  new, t)

t2_ref, spe_ref = np.asarray(ph1["t2"]), np.asarray(ph1["spe"])
t2_new, spe_new = np.asarray(mon["t2"]), np.asarray(mon["spe"])
t2_lim, spe_lim = ph1["t2_limit"], ph1["spe_limit"]

f, (axT, axS) = fig(ncols=2, figsize=(9.4, 3.6))
n_ref = t2_ref.size
xr = np.arange(n_ref)
xn = np.arange(n_ref, n_ref + t2_new.size)
for ax, ref_s, new_s, lim, name in [
        (axT, t2_ref, t2_new, t2_lim, "Hotelling $T^2$"),
        (axS, spe_ref, spe_new, spe_lim, "SPE (Q)")]:
    ax.scatter(xr, ref_s, color="#3f51b5", s=16, label="reference (cult 1)")
    ax.scatter(xn, new_s, color="#dc3545", s=16, label="monitored (cult 3)")
    ax.axhline(lim, color="#6c757d", ls="--", lw=1.2, label="control limit")
    ax.axvline(n_ref - 0.5, color="#adb5bd", ls=":", lw=1)
    ax.set(title=name, xlabel="wine index", ylabel="statistic")
axT.legend(fontsize=7)
print(render(f))
```

To the left of the dotted divider are the reference wines, mostly under both
limits (a few cross, consistent with the nominal 5% false-alarm rate). To the
right, the cultivar-3 wines: **every** one exceeds the SPE limit and roughly two
thirds exceed $T^2$. SPE is the more decisive alarm here — cultivar 3 varies in
directions the cultivar-1 model has no component for, which is exactly what SPE
is designed to catch.

## How many wines are caught?

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_wine
from fdars.spm import spm_phase1, spm_monitor

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

ref = curves[cultivar == 1]
ph1 = spm_phase1(ref, t, ncomp=3, alpha=0.05)

def alarm_rate(batch):
    mon = spm_monitor(ph1["mean"], ph1["loadings"], ph1["weights"],
                      ph1["eigenvalues"], ph1["t2_limit"], ph1["spe_limit"],
                      batch, t)
    return float((np.asarray(mon["t2_alarm"]) |
                  np.asarray(mon["spe_alarm"])).mean())

# reference self-rate from phase 1 (should be near alpha)
self_rate = float(((np.asarray(ph1["t2"]) > ph1["t2_limit"]) |
                   (np.asarray(ph1["spe"]) > ph1["spe_limit"])).mean())
rates = {"cultivar 1\n(reference)": self_rate,
         "cultivar 2": alarm_rate(curves[cultivar == 2]),
         "cultivar 3": alarm_rate(curves[cultivar == 3])}

f, ax = fig()
bars = ax.bar(list(rates), [100 * v for v in rates.values()],
              color=["#3f51b5", "#e8710a", "#198754"])
ax.axhline(5, color="#dc3545", ls="--", lw=1.2, label="nominal 5% false alarm")
for b, v in zip(bars, rates.values()):
    ax.text(b.get_x() + b.get_width() / 2, 100 * v + 1.5,
            f"{100*v:.0f}%", ha="center", fontsize=9)
ax.set(title="Out-of-spec alarm rate vs the cultivar-1 monitor",
       ylabel="% wines alarmed", ylim=(0, 108))
ax.legend()
print(render(f))
```

The monitor built on cultivar 1 alarms on only a handful of its own reference
wines (near the 5% nominal rate) but on **essentially all** cultivar-2 and
cultivar-3 wines. As a QC gate for "is this the wine we meant to make?", the
Andrews-curve control chart is decisive.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `fpca_tolerance_band(data, ncomp, nb, coverage)` | `coverage` | Target fraction of good curves inside the band |
| `spm_phase1(data, argvals, ncomp, alpha)` | `alpha`, `ncomp` | Calibrate model + $T^2$/SPE limits on the reference |
| `spm_monitor(mean, loadings, weights, eigenvalues, t2_limit, spe_limit, new_data, argvals)` | — | Score new curves; returns `t2`, `spe`, `t2_alarm`, `spe_alarm` |

!!! tip "Diagnosing *why* a wine alarmed"
    When SPE or $T^2$ fires you usually want to know which measurement caused it.
    `fdars.spm.t2_pc_contributions` decomposes a $T^2$ statistic into its
    principal-component contributions; combined with the FPCA loadings (which are
    themselves Andrews curves, hence linear in the 13 features) this points back
    to the offending chemistry.

## See also

- [Andrews Wine intro](andrews-wine-intro.md) — the transform and class structure.
- [Outlier detection](andrews-wine.md) — depth and outliergram, an unsupervised
  counterpart to this supervised QC view.
- [Tolerance bands](../analyze/tolerance-bands.md) and
  [statistical process monitoring](../monitoring/spm.md) for the general
  monitoring tools.
