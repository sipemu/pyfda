# Profile and Partial-Domain Monitoring

Functional control charts summarise a whole curve into a single $T^2$ or SPE number. That
global view is a liability when a fault is **localised** — a defect confined to a short
sub-interval of the domain. Averaged over the full curve, a small local bump barely moves
the global statistic and slips past the limit. The remedy is simple and powerful:
**restrict the monitoring model to the sub-interval that matters**. This page shows how
to slice the argument grid and rerun the ordinary `fdars.spm` Phase I / Phase II workflow
on a partial domain, and quantifies the sensitivity gain.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate

argvals = np.linspace(0, 1, 120)
ic = np.asarray(simulate(100, argvals, n_basis=6, seed=7))     # Phase I reference

# Phase II: 20 in-control curves + 8 with a bump localised near t = 0.78
ok = np.asarray(simulate(20, argvals, n_basis=6, seed=21))
loc = np.asarray(simulate(8, argvals, n_basis=6, seed=33))
bump = np.exp(-0.5 * ((argvals - 0.78) / 0.035) ** 2) * 1.8
loc = loc + bump
new = np.vstack([ok, loc])

lo, hi = 0.68, 0.88          # the sub-domain of interest

f, ax = fig()
ax.plot(argvals, ic.T, color="#6c757d", lw=0.5, alpha=0.30)
ax.plot(argvals, ok.T, color="#3f51b5", lw=0.7, alpha=0.5)
ax.plot(argvals, loc.T, color="#dc3545", lw=1.0, alpha=0.8)
ax.axvspan(lo, hi, color="#e8710a", alpha=0.12, label="monitored sub-domain")
ax.set(title="A fault localised near t = 0.78 (red); grey = Phase I, indigo = in-control Phase II",
       xlabel="t", ylabel="x(t)")
ax.legend(loc="upper left", fontsize=8)
print(render(f))
```

Away from the shaded window the faulty curves (red) are indistinguishable from the
in-control ones. Only inside the window does the bump appear.

---

## Concepts

### Why the full domain hides local faults

The FPCA $T^2$ statistic weights every point of the curve. If the fault occupies a
fraction $\rho$ of the domain, its contribution to a full-domain score is diluted roughly
in proportion to $\rho$, while in-control variability over the *whole* domain still counts
against the control limit. The signal-to-noise ratio therefore scales like

$$
\frac{\text{fault energy on } [a,b]}{\text{in-control variance on } [0,1]} .
$$

Restricting the analysis to $[a,b]$ replaces the denominator with the in-control variance
*on the sub-domain only*, sharpening the ratio and — provided the fault truly lives there
— dramatically improving detection.

### Partial-domain monitoring is just monitoring on a slice

There is no special API: a partial-domain chart is an ordinary chart built on sliced
arrays. Pick the index set of the sub-domain, slice both `argvals` and the data columns,
and run the usual `spm_phase1` / `spm_monitor`. Because the integration weights are
recomputed on the restricted grid, the resulting statistics are proper functional
statistics *on the sub-domain*.

```python exec="1" html="1" source="above"
import numpy as np

argvals = np.linspace(0, 1, 120)
lo, hi = 0.68, 0.88
mask = (argvals >= lo) & (argvals <= hi)
idx = np.where(mask)[0]
print(f"full domain : {argvals.size} points")
print(f"sub-domain  : {idx.size} points on [{lo}, {hi}]")
```

!!! note "Slicing must stay contiguous and aligned"
    Slice `argvals` and every data matrix with the **same** index set, and pass
    C-contiguous arrays (`np.ascontiguousarray`) to the Rust functions. The reference and
    stream must share the grid, so slice them identically.

---

## Full-domain vs partial-domain

We wrap the workflow in a small helper and run it twice: once on the whole grid, once on
the sub-domain. Everything else — `ncomp`, `alpha` — is held fixed for a fair comparison.

```python exec="1" html="1" source="above"
import numpy as np
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor

argvals = np.linspace(0, 1, 120)
ic = np.asarray(simulate(100, argvals, n_basis=6, seed=7))
ok = np.asarray(simulate(20, argvals, n_basis=6, seed=21))
loc = np.asarray(simulate(8, argvals, n_basis=6, seed=33))
loc = loc + np.exp(-0.5 * ((argvals - 0.78) / 0.035) ** 2) * 1.8
new = np.vstack([ok, loc])
idx = np.where((argvals >= 0.68) & (argvals <= 0.88))[0]

def monitor_on(index):
    a = np.ascontiguousarray(argvals[index])
    ref = np.ascontiguousarray(ic[:, index])
    stream = np.ascontiguousarray(new[:, index])
    p1 = spm_phase1(ref, a, ncomp=4, alpha=0.01)
    p2 = spm_monitor(
        mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
        eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
        spe_limit=p1["spe_limit"], new_data=stream, argvals=a,
    )
    t2 = np.asarray(p2["t2"])
    alarm = np.asarray(p2["t2_alarm"]) | np.asarray(p2["spe_alarm"])
    return t2, p1["t2_limit"], alarm

full_idx = np.arange(argvals.size)
t2_full, ucl_full, alarm_full = monitor_on(full_idx)
t2_part, ucl_part, alarm_part = monitor_on(idx)

fault = slice(20, 28)     # the 8 faulty observations
print(f"full-domain    : {alarm_full[fault].sum()}/8 faults caught, "
      f"{alarm_full[:20].sum()}/20 false alarms")
print(f"partial-domain : {alarm_part[fault].sum()}/8 faults caught, "
      f"{alarm_part[:20].sum()}/20 false alarms")
```

The full-domain chart misses every localised fault; the partial-domain chart catches all
eight, with no false alarms on the in-control observations. The figure makes the gap
visible: on the full domain the faulty points (red) sit comfortably below the limit,
while on the sub-domain they jump far above it.

```python exec="1" html="1"
import numpy as np
from docs_fig import render, plt
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor

argvals = np.linspace(0, 1, 120)
ic = np.asarray(simulate(100, argvals, n_basis=6, seed=7))
ok = np.asarray(simulate(20, argvals, n_basis=6, seed=21))
loc = np.asarray(simulate(8, argvals, n_basis=6, seed=33))
loc = loc + np.exp(-0.5 * ((argvals - 0.78) / 0.035) ** 2) * 1.8
new = np.vstack([ok, loc])
idx = np.where((argvals >= 0.68) & (argvals <= 0.88))[0]

def monitor_on(index):
    a = np.ascontiguousarray(argvals[index])
    ref = np.ascontiguousarray(ic[:, index])
    stream = np.ascontiguousarray(new[:, index])
    p1 = spm_phase1(ref, a, ncomp=4, alpha=0.01)
    p2 = spm_monitor(
        mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
        eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
        spe_limit=p1["spe_limit"], new_data=stream, argvals=a,
    )
    return np.asarray(p2["t2"]), p1["t2_limit"]

t2_full, ucl_full = monitor_on(np.arange(argvals.size))
t2_part, ucl_part = monitor_on(idx)

obs = np.arange(1, len(new) + 1)
fmask = np.zeros(len(new), bool); fmask[20:28] = True

f, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.6), sharey=False)
for ax, t2, ucl, title in [
    (ax1, t2_full, ucl_full, "Full domain [0, 1]"),
    (ax2, t2_part, ucl_part, "Sub-domain [0.68, 0.88]"),
]:
    ax.vlines(obs, 0, t2, color="#c7cbe0", lw=1)
    ax.scatter(obs[~fmask], t2[~fmask], s=20, color="#3f51b5", zorder=3, label="in-control")
    ax.scatter(obs[fmask], t2[fmask], s=28, color="#dc3545", zorder=3, label="localised fault")
    ax.axhline(ucl, color="#e8710a", ls="--", lw=1.3, label="control limit")
    ax.set(title=title, xlabel="observation index", ylim=(0, None))
ax1.set_ylabel("Hotelling $T^2$")
ax1.legend(loc="upper left", fontsize=7)
f.suptitle("Same fault, two monitoring domains", y=1.02)
print(render(f))
```

!!! tip "Where do the sub-domain bounds come from?"
    Domain knowledge (a known critical region — a curing window, a specific frequency
    band) is the usual source. When the location is unknown, a sliding-window scan — run
    the partial-domain chart over a series of overlapping windows — turns detection into
    localisation, at the cost of a multiplicity correction on `alpha`.

---

## Profile-by-profile monitoring

*Profile monitoring* treats each functional observation as a "profile" and asks whether
it conforms to the reference shape. The Phase II loop above already does this one
observation at a time; the partial-domain twist simply changes **which part** of each
profile is judged. The two ideas compose cleanly: monitor each incoming profile, but
score it only on the sub-domain where the specification is tight.

| Parameter | Type | Description |
|---|---|---|
| `data` / `new_data` | `(n, m)` array | Reference / stream profiles, already sliced to the sub-domain |
| `argvals` | `(m,)` array | Sub-domain grid, sliced identically |
| `ncomp` | int | FPC components retained on the sub-domain |
| `alpha` | float | Per-chart false-alarm rate |

!!! note "Matrix Profile is a different \"profile\""
    `fdars.seasonal.matrix_profile_fdata` also has *profile* in its name, but it solves an
    unrelated problem — finding repeated subsequences / periodicity within a series
    (`profile`, `primary_period`, `confidence`) rather than SPC-style conformance of one
    curve to a reference. Reach for it for motif and period discovery, not process
    monitoring.

---

## See also

- [Statistical Process Monitoring](spm.md) — the Phase I / Phase II fundamentals used here.
- [Advanced Statistical Process Monitoring](advanced-spm.md) — EWMA charts, run rules,
  ARL analysis, and per-PC fault diagnosis, all of which apply unchanged on a sub-domain.

!!! note "Where this differs from the R vignette"
    The R article implements three dedicated engines that have no `fdars` Python binding
    yet: covariate-aware **profile monitoring** (`spm.profile.phase1` / `.monitor`, built
    on sliding-window function-on-scalar regression), **conditional-completion** partial
    monitoring (`spm.monitor.partial` with BLUP / projection / zero-pad tails for
    curves seen only up to some fraction of the domain), and **elastic SPM**
    (`spm.elastic.phase1` / `.monitor`, which splits amplitude from phase variation). The
    sub-domain slicing shown on this page reproduces the *spirit* of partial-domain
    monitoring using only the exposed `spm_phase1` / `spm_monitor` primitives — it charts a
    fixed critical window rather than completing an unobserved tail. Amplitude/phase
    separation is available through the [elastic alignment](../align/elastic-alignment.md)
    tools (SRSF alignment, Karcher mean) if you want to build an elastic chart by hand.
