# Tecator Spectra: Inline Quality Monitoring

**Dataset:** Tecator — near-infrared absorbance spectra (100 channels,
850–1050 nm) of 240 finely minced meat samples, each with a lab-measured fat
content.

A meat processor wants to run its near-infrared (NIR) spectrometer *inline*:
every sample that comes off the line is scanned, and the operator needs an
automatic flag whenever a spectrum drifts away from the on-spec product. Because
each measurement is a whole absorbance **curve**, this is a
[functional statistical-process-monitoring](../monitoring/spm.md) problem — we
learn the in-control curve distribution from a reference batch (Phase I), then
project every incoming curve onto that model and watch two control statistics
(Phase II).

Here we treat samples in a tight fat band (5–15 %) as the **on-spec reference**
product and ask whether the FPCA control chart flags spectra that fall outside
that band — without ever being told the fat value.

## The reference product and the incoming stream

A standard NIR preprocessing step removes the dominant baseline shift by
differentiating twice: a constant or linear offset vanishes under
$d^2/d\lambda^2$, exposing the fat-absorption curvature the monitor should react
to. We do this with `fdars.fdata.deriv_1d` and work on the second-derivative
spectra throughout.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_tecator
from fdars.fdata import deriv_1d

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))       # baseline-corrected spectra

onspec = (fat >= 5) & (fat <= 15)                # the reference quality band
f, ax = fig()
ax.plot(wl, D2[onspec].T, color="#3f51b5", lw=0.6, alpha=0.35)
ax.plot(wl, D2[fat > 25].T, color="#dc3545", lw=0.7, alpha=0.5)
ax.plot([], [], color="#3f51b5", label="on-spec (fat 5–15 %)")
ax.plot([], [], color="#dc3545", label="off-spec (fat > 25 %)")
ax.set(title="Second-derivative spectra: on-spec band vs high-fat samples",
       xlabel="wavelength (nm)", ylabel="$d^2A/d\\lambda^2$")
ax.legend(loc="upper right")
print(render(f))
```

The high-fat spectra (red) fan away from the on-spec band (indigo) around the
930–970 nm fat-absorption region. A monitor built on the on-spec curves should
register that departure as an out-of-control signal.

## Phase I — learning the on-spec model

We take 70 randomly chosen on-spec spectra as the Phase I reference and fit an
FPCA control model with `spm_phase1` (4 components, per-chart $\alpha = 0.01$).
The remaining on-spec spectra become the in-control part of the monitoring
stream; a set of clearly off-spec, high-fat spectra (> 25 %) are interleaved as
the faults to catch.

```python exec="1" html="1" source="above"
import numpy as np
from docs_data import load_tecator
from fdars.fdata import deriv_1d
from fdars.spm import spm_phase1

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))

rng = np.random.default_rng(0)
ref_idx = np.where((fat >= 5) & (fat <= 15))[0]
rng.shuffle(ref_idx)
phase1_idx = ref_idx[:70]                         # reference sample

p1 = spm_phase1(D2[phase1_idx], wl, ncomp=4, alpha=0.01)
print(f"T2  limit: {p1['t2_limit']:.3f}")
print(f"SPE limit: {p1['spe_limit']:.5f}")
```

`spm_phase1` returns the estimated mean function, the FPCA loadings, the
integration `weights`, the `eigenvalues`, and the two control limits `t2_limit`
and `spe_limit`. The Hotelling $T^2$ statistic watches for shifts *inside* the
retained FPC subspace; the SPE (Q) statistic watches the reconstruction
residual — structure the on-spec model cannot represent. Monitoring both covers
the two ways a spectrum can go off-spec.

## Phase II — the control chart

`spm_monitor` projects each incoming spectrum onto the Phase I model and returns
its $T^2$ and SPE values together with boolean alarm flags. We flag a spectrum
out-of-control if *either* statistic exceeds its limit.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render, plt
from docs_data import load_tecator
from fdars.fdata import deriv_1d
from fdars.spm import spm_phase1, spm_monitor

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))

rng = np.random.default_rng(0)
ref_idx = np.where((fat >= 5) & (fat <= 15))[0]
rng.shuffle(ref_idx)
phase1_idx, onspec_mon = ref_idx[:70], ref_idx[70:]
offspec = np.where(fat > 25)[0]

stream = np.concatenate([onspec_mon, rng.choice(offspec, 12, replace=False)])
rng.shuffle(stream)

p1 = spm_phase1(D2[phase1_idx], wl, ncomp=4, alpha=0.01)
p2 = spm_monitor(
    mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
    eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
    spe_limit=p1["spe_limit"], new_data=D2[stream], argvals=wl,
)

obs = np.arange(1, len(stream) + 1)
t2, spe = np.asarray(p2["t2"]), np.asarray(p2["spe"])
t2_alarm, spe_alarm = np.asarray(p2["t2_alarm"]), np.asarray(p2["spe_alarm"])
alarm = t2_alarm | spe_alarm

f, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 5.2), sharex=True)
for ax, stat, al, lim, name in [
    (ax1, t2,  t2_alarm,  p1["t2_limit"],  "Hotelling $T^2$"),
    (ax2, spe, spe_alarm, p1["spe_limit"], "SPE (Q)"),
]:
    ax.vlines(obs, 0, stat, color="#c7cbe0", lw=1)
    ax.scatter(obs[~al], stat[~al], s=22, color="#3f51b5", zorder=3, label="in-control")
    ax.scatter(obs[al],  stat[al],  s=34, color="#dc3545", zorder=3, label="out-of-control")
    ax.axhline(lim, color="#e8710a", ls="--", lw=1.3, label="control limit")
    ax.set_ylabel(name)
    ax.set_ylim(bottom=0)
ax1.legend(loc="upper left", ncol=3, fontsize=8)
ax2.set_xlabel("sample index (arrival order)")
f.suptitle("Inline monitoring of the Tecator stream", y=0.98)
print(render(f))

# summary against the (held-out) fat labels
truth = fat[stream] > 25
det = int((alarm & truth).sum())
fa = int((alarm & ~truth).sum())
print(f"off-spec detected: {det}/{int(truth.sum())} | "
      f"false alarms on on-spec: {fa}/{int((~truth).sum())}")
```

Every off-spec high-fat spectrum crosses at least one limit, and only a handful
of on-spec samples false-alarm — consistent with running two charts each at
$\alpha = 0.01$. The chart never sees the fat value; it reacts purely to the
shape of the second-derivative curve relative to the on-spec model.

## Localizing the fault: per-PC contributions

When a sample alarms, the operator wants to know *why*. Because
$T^2 = \sum_k \xi_k^2/\lambda_k$ is a sum over principal components, each term is
an interpretable **contribution**. `t2_pc_contributions` returns the per-PC
breakdown and `t2_pc_significance` flags which components are individually
significant. `spm_monitor` returns statistics but not the raw scores, so we
reproduce them by projecting the centered curves onto the loadings —
`(Xc * weights) @ loadings` — exactly as the monitor does internally.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_tecator
from fdars.fdata import deriv_1d
from fdars.spm import spm_phase1, t2_pc_contributions, t2_pc_significance

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))

rng = np.random.default_rng(0)
ref_idx = np.where((fat >= 5) & (fat <= 15))[0]
rng.shuffle(ref_idx)
phase1_idx, onspec_mon = ref_idx[:70], ref_idx[70:]
offspec = np.where(fat > 25)[0]
stream = np.concatenate([onspec_mon, rng.choice(offspec, 12, replace=False)])
rng.shuffle(stream)

p1 = spm_phase1(D2[phase1_idx], wl, ncomp=4, alpha=0.01)
scores = ((D2[stream] - np.asarray(p1["mean"])) * np.asarray(p1["weights"])) @ np.asarray(p1["loadings"])
ev = np.asarray(p1["eigenvalues"])

contrib = np.asarray(t2_pc_contributions(scores, ev))       # (n, ncomp)
sig = np.asarray(t2_pc_significance(contrib, alpha=0.05))    # 0/1 flags

worst = int(np.argmax(contrib.sum(axis=1)))
c = contrib[worst]
flags = sig[worst].astype(bool)
pcs = np.arange(1, len(c) + 1)

f, ax = fig()
ax.bar(pcs, c, color=["#dc3545" if fl else "#3f51b5" for fl in flags])
ax.set(title=f"$T^2$ contribution breakdown (most extreme sample, fat = {fat[stream][worst]:.1f} %)",
       xlabel="principal component", ylabel="contribution $\\xi_k^2/\\lambda_k$")
ax.set_xticks(pcs)
ax.text(0.97, 0.95, f"total $T^2$ = {c.sum():.0f}", transform=ax.transAxes,
        ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="#f4f4fb", ec="#c7cbe0"))
print(render(f))
```

The contribution plot pins most of the $T^2$ mass on a single dominant
component — the mode of variation that carries the fat signal. Red bars mark
components flagged as significant, telling the operator *which* aspect of the
spectrum moved, not merely *that* it moved.

!!! note "This is a stand-in for a real quality band"
    Tecator ships fat labels, so we can define "on-spec" by fat and check the
    monitor against a known truth. In a live line the labels are unavailable —
    the point of the control chart is exactly to reproduce that judgement from
    the spectrum alone. The 5–15 % band and the 25 % off-spec cutoff here are
    illustrative choices, not a process specification.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `deriv_1d(data, argvals, nderiv)` | `nderiv` | Derivative order (2 removes a linear baseline) |
| `spm_phase1(data, argvals, ncomp, alpha)` | `ncomp`, `alpha` | Fit the in-control FPCA model and control limits |
| `spm_monitor(mean, loadings, weights, eigenvalues, t2_limit, spe_limit, new_data, argvals)` | `new_data` | Project and flag incoming curves |
| `t2_pc_contributions(scores, eigenvalues)` | — | Per-PC breakdown of $T^2$ |
| `t2_pc_significance(contributions, alpha)` | `alpha` | Bonferroni-flag significant components |

## See also

- [Statistical Process Monitoring](../monitoring/spm.md) — the Phase I / Phase II
  workflow and the two control statistics.
- [Advanced Statistical Process Monitoring](../monitoring/advanced-spm.md) —
  EWMA charts, run rules, ARL, and fault diagnosis in depth.
- [Predicting fat from NIR spectra](tecator-regression.md) — the same dataset
  as a scalar-on-function regression problem.
