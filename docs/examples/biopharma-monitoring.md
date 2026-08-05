# Biopharmaceutical Batch Monitoring: Penicillin Fermentation

**Dataset:** Penicillin — 46 fed-batch fermentation runs, each a biomass /
product trajectory sampled at 200 time points over a 400-hour cultivation. Every
batch carries a `status` label, `normal` (40 batches) or `faulty` (6 batches).

!!! warning "Synthetic dataset"
    This penicillin dataset is **synthetic** — the trajectories are generated to
    mimic the shape of a fed-batch fermentation, not measured from a real
    bioreactor. It is included so the monitoring workflow can be demonstrated
    end-to-end on labelled normal/faulty batches. Treat the numbers as
    illustrative.

In biopharmaceutical manufacturing, a batch that goes wrong is expensive: raw
materials, reactor time, and often the whole downstream campaign are lost. The
goal of **batch monitoring** is to notice a deviating batch *while it is still
running*, so it can be corrected or abandoned early. Each batch is a whole
**trajectory**, so this is a [functional process-monitoring](../monitoring/spm.md)
problem: learn the in-control trajectory distribution from known-good batches
(Phase I), then track every batch against that model (Phase II).

## The batches

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin

t, X, meta = load_penicillin()
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

f, ax = fig()
ax.plot(t, X[normal].T, color="#3f51b5", lw=0.7, alpha=0.4)
ax.plot(t, X[faulty].T, color="#dc3545", lw=1.4, alpha=0.9)
ax.plot([], [], color="#3f51b5", label="normal")
ax.plot([], [], color="#dc3545", label="faulty")
ax.set(title="Penicillin fermentation trajectories (synthetic)",
       xlabel="time (h)", ylabel="concentration")
ax.legend(loc="lower right")
print(render(f))
```

The normal batches (indigo) rise to a plateau near 1.4; the faulty batches
(red) grow more slowly and level off well below the healthy band. The separation
is clear by eye at the end — the question is how early, and how automatically, a
control chart can flag it.

## Phase I — the in-control envelope

We fit the FPCA control model on 30 randomly chosen normal batches with
`spm_phase1` (4 components, $\alpha = 0.01$), holding out the remaining 10 normal
batches to check the false-alarm behaviour. The Phase I model gives us the mean
trajectory and a control envelope; batches inside it are in-control.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin
from fdars.spm import spm_phase1

t, X, meta = load_penicillin()
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

rng = np.random.default_rng(1)
nidx = np.where(normal)[0]
rng.shuffle(nidx)
phase1_idx = nidx[:30]

p1 = spm_phase1(X[phase1_idx], t, ncomp=4, alpha=0.01)
mean = np.asarray(p1["mean"])
# a 2-sigma pointwise band from the Phase I batches (illustrative envelope)
sd = X[phase1_idx].std(axis=0)

f, ax = fig()
ax.fill_between(t, mean - 2 * sd, mean + 2 * sd, color="#3f51b5", alpha=0.15,
                label="Phase I ±2σ envelope")
ax.plot(t, mean, color="#3f51b5", lw=2, label="in-control mean")
ax.plot(t, X[faulty].T, color="#dc3545", lw=1.2, alpha=0.9)
ax.plot([], [], color="#dc3545", label="faulty batches")
ax.set(title="In-control envelope with faulty batches overlaid",
       xlabel="time (h)", ylabel="concentration")
ax.legend(loc="lower right")
print(render(f))
```

The faulty batches leave the ±2σ envelope in the growth phase and never rejoin
it — a functional deviation the control chart is built to quantify.

## Phase II — monitoring every batch

With the Phase I model fixed, `spm_monitor` projects each batch onto the FPCA
subspace and returns its Hotelling $T^2$ and SPE (Q) statistics plus alarm
flags. A batch is out-of-control if either statistic crosses its limit.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin
from fdars.spm import spm_phase1, spm_monitor

t, X, meta = load_penicillin()
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

rng = np.random.default_rng(1)
nidx = np.where(normal)[0]
rng.shuffle(nidx)
phase1_idx = nidx[:30]

p1 = spm_phase1(X[phase1_idx], t, ncomp=4, alpha=0.01)
p2 = spm_monitor(
    mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
    eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
    spe_limit=p1["spe_limit"], new_data=X, argvals=t,
)

t2 = np.asarray(p2["t2"])
alarm = np.asarray(p2["t2_alarm"]) | np.asarray(p2["spe_alarm"])
batch = np.arange(len(X))

f, ax = fig()
ax.vlines(batch, 0, t2, color="#c7cbe0", lw=1)
ax.scatter(batch[normal], t2[normal], s=26, color="#3f51b5", zorder=3, label="normal")
ax.scatter(batch[faulty], t2[faulty], s=44, color="#dc3545", zorder=3,
           marker="D", label="faulty")
ax.axhline(p1["t2_limit"], color="#e8710a", ls="--", lw=1.3, label="control limit")
ax.set(title="Per-batch Hotelling $T^2$ (whole-trajectory monitoring)",
       xlabel="batch index", ylabel="Hotelling $T^2$")
ax.legend(loc="upper left", ncol=3, fontsize=8)
print(render(f))

det = int((alarm & faulty).sum())
fa = int((alarm & normal).sum())
print(f"faulty flagged: {det}/{int(faulty.sum())} | "
      f"false alarms on normal: {fa}/{int(normal.sum())}")
```

On the full trajectory the six faulty batches sit far above the control limit
while every normal batch stays below it — all six are caught, with no false
alarms. But whole-batch monitoring only tells us *after* the run finishes. The
manufacturing value is in catching it sooner.

## When does a batch breach the limit?

To answer *when*, we monitor **partial trajectories**: at a sequence of
checkpoints during the run we refit the Phase I model on the same window of the
normal batches and monitor each batch up to that point. The first checkpoint at
which a batch alarms is its **time-to-detection**.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin
from fdars.spm import spm_phase1, spm_monitor

t, X, meta = load_penicillin()
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

rng = np.random.default_rng(1)
nidx = np.where(normal)[0]
rng.shuffle(nidx)
phase1_idx = nidx[:30]
heldout = nidx[30:]                       # normal batches not used for fitting
faulty_idx = np.where(faulty)[0]
stream = np.concatenate([heldout, faulty_idx])

checkpoints = np.arange(20, 201, 20)      # grid indices at which we test
first_alarm = np.full(len(X), -1.0)
for k in checkpoints:
    tw, Xw = t[:k], X[:, :k]
    p1 = spm_phase1(Xw[phase1_idx], tw, ncomp=4, alpha=0.01)
    p2 = spm_monitor(
        mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
        eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
        spe_limit=p1["spe_limit"], new_data=Xw[stream], argvals=tw,
    )
    al = np.asarray(p2["t2_alarm"]) | np.asarray(p2["spe_alarm"])
    fa = first_alarm[stream]
    fa[al & (fa < 0)] = t[k - 1]
    first_alarm[stream] = fa

f, ax = fig()
# healthy plateau reference
ax.plot(t, X[phase1_idx].mean(0), color="#6c757d", lw=1, ls=":",
        label="in-control mean")
for i in faulty_idx:
    ax.plot(t, X[i], color="#dc3545", lw=1.2, alpha=0.9)
    ta = first_alarm[i]
    if ta >= 0:
        ax.axvline(ta, color="#e8710a", lw=0.8, alpha=0.5)
ax.plot([], [], color="#dc3545", label="faulty batches")
ax.plot([], [], color="#e8710a", label="first-alarm time")
ax.set(title="Faulty batches are flagged early in the run",
       xlabel="time (h)", ylabel="concentration")
ax.legend(loc="lower right")
print(render(f))

fa_times = first_alarm[faulty_idx]
n_ho = int((first_alarm[heldout] >= 0).sum())
print(f"faulty first-alarm times (h): {sorted(int(x) for x in fa_times)}")
print(f"held-out normal batches ever flagged: {n_ho}/{len(heldout)}")
```

All six faulty batches breach the limit around $t \approx 38$ h — early in the
growth phase, roughly a tenth of the way through a 400-hour run, long before the
trajectories visibly separate at the plateau. A couple of held-out normal
batches trip a transient early flag when the window is very short and the model
is estimated from few points; in practice one would require a run of consecutive
alarms (see the [run rules](../monitoring/advanced-spm.md#run-rules)) before
stopping a batch.

!!! tip "Refitting the window vs. a landmark-registered model"
    Here we refit Phase I at each checkpoint so the model always matches the
    observed window length. An alternative is to register batches to a common
    phase (e.g. by a maturity index) and monitor against a single model, or to
    restrict the analysis to a sub-interval of the run — see
    [Profile and Partial-Domain Monitoring](../monitoring/profile-partial-monitoring.md).

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `spm_phase1(data, argvals, ncomp, alpha)` | `ncomp`, `alpha` | Fit the in-control FPCA model and control limits |
| `spm_monitor(mean, loadings, weights, eigenvalues, t2_limit, spe_limit, new_data, argvals)` | `new_data` | Project and flag batches |

## See also

- [Statistical Process Monitoring](../monitoring/spm.md) — the two-phase workflow
  and the $T^2$ / SPE statistics.
- [Advanced Statistical Process Monitoring](../monitoring/advanced-spm.md) —
  EWMA charts for slow drifts, run rules, and ARL analysis.
- [Inline Quality Monitoring](inline-monitoring.md) — detection power and
  false-alarm trade-offs on this same dataset.
