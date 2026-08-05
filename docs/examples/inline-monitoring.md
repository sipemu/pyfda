# Inline Quality Monitoring: Detection Power & False-Alarm Analysis

Every control chart lives on a trade-off. Loosen the limit and you catch more
faults but cry wolf on good product; tighten it and false alarms vanish but small
faults slip through. This page quantifies that trade-off for the FPCA-based
[functional control chart](../monitoring/spm.md): we establish limits from a set
of in-control curves, then measure **detection power** on faulty streams and
**false-alarm rate** on fresh in-control streams as we sweep the significance
level $\alpha$ — the functional analogue of a ROC / ARL study.

!!! note "Simulated data, by design"
    To trace a smooth detection-power curve we need many faulty and many fresh
    in-control observations at a *controllable* fault severity. We therefore use
    `fdars.simulation.simulate` here rather than a fixed labelled dataset, so we
    can dial the fault magnitude and generate large fresh samples. The
    [biopharma page](biopharma-monitoring.md) runs the same machinery on the
    (also synthetic, but fixed) penicillin batches.

## The signal we are trying to catch

The fault we inject is an **amplitude inflation**: faulty curves are in-control
curves scaled up, which shifts them along the dominant modes of variation the
FPCA subspace tracks — exactly the departure the Hotelling $T^2$ statistic is
designed to see. We show a moderate (×2.0) fault against the in-control band.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate

t = np.linspace(0, 1, 80)
ic = np.asarray(simulate(60, t, n_basis=6, seed=7))
faulty = np.asarray(simulate(12, t, n_basis=6, seed=202)) * 2.0

f, ax = fig()
ax.plot(t, ic.T, color="#3f51b5", lw=0.6, alpha=0.35)
ax.plot(t, faulty.T, color="#dc3545", lw=1.0, alpha=0.8)
ax.plot([], [], color="#3f51b5", label="in-control")
ax.plot([], [], color="#dc3545", label="faulty (amplitude ×2)")
ax.set(title="In-control band and amplitude-inflated faulty curves",
       xlabel="t", ylabel="x(t)")
ax.legend(loc="upper right")
print(render(f))
```

The faulty curves swing wider than the in-control band but overlap it heavily —
no single fault is obviously out of range, which is what makes the statistical
trade-off non-trivial.

## Detection power vs. false-alarm rate

We fit the Phase I model once per $\alpha$, then run `spm_monitor` on two fresh
streams: 400 in-control curves (to estimate the **false-alarm rate**, the
fraction wrongly flagged) and 400 faulty curves (to estimate **detection
power**, the fraction correctly flagged). A curve is flagged if *either* the
$T^2$ or the SPE limit is crossed.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render, plt
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor

t = np.linspace(0, 1, 80)
ic = np.asarray(simulate(200, t, n_basis=6, seed=7))           # Phase I reference
fresh = np.asarray(simulate(400, t, n_basis=6, seed=101))      # fresh in-control
faulty = np.asarray(simulate(400, t, n_basis=6, seed=202)) * 2.0

alphas = np.array([0.40, 0.30, 0.20, 0.10, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001])

def flagged(model, data):
    r = spm_monitor(
        mean=model["mean"], loadings=model["loadings"], weights=model["weights"],
        eigenvalues=model["eigenvalues"], t2_limit=model["t2_limit"],
        spe_limit=model["spe_limit"], new_data=data, argvals=t,
    )
    return np.asarray(r["t2_alarm"]) | np.asarray(r["spe_alarm"])

far, power = [], []
for a in alphas:
    m = spm_phase1(ic, t, ncomp=4, alpha=a)
    far.append(flagged(m, fresh).mean())
    power.append(flagged(m, faulty).mean())
far, power = np.asarray(far), np.asarray(power)

f, ax = fig()
ax.plot(alphas, power, "o-", color="#198754", lw=1.6, label="detection power")
ax.plot(alphas, far, "s-", color="#dc3545", lw=1.6, label="false-alarm rate")
ax.plot(alphas, alphas, ":", color="#6c757d", lw=1, label="nominal $\\alpha$")
ax.set_xscale("log")
ax.set(title="Tightening $\\alpha$ trades detection power for fewer false alarms",
       xlabel="significance level $\\alpha$ (log scale)", ylabel="rate")
ax.legend(loc="upper left")
print(render(f))
```

As $\alpha$ shrinks the two curves fall together: the false-alarm rate tracks the
nominal $\alpha$ closely (the chart is well-calibrated in-control), while
detection power decays more slowly at first, then steeply. The gap between the
green and red curves *is* the useful sensitivity of the chart at each operating
point.

## The ROC view — and how it sharpens with fault size

Plotting detection power directly against false-alarm rate gives a **ROC curve**:
each point is one $\alpha$. A chart with no discriminating power would sit on the
diagonal; the further the curve bows toward the top-left, the better. Larger
faults are easier to catch, so their ROC curves bow more.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor

t = np.linspace(0, 1, 80)
ic = np.asarray(simulate(200, t, n_basis=6, seed=7))
fresh = np.asarray(simulate(400, t, n_basis=6, seed=101))
alphas = np.array([0.40, 0.30, 0.20, 0.10, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001])

def flagged(model, data):
    r = spm_monitor(
        mean=model["mean"], loadings=model["loadings"], weights=model["weights"],
        eigenvalues=model["eigenvalues"], t2_limit=model["t2_limit"],
        spe_limit=model["spe_limit"], new_data=data, argvals=t,
    )
    return np.asarray(r["t2_alarm"]) | np.asarray(r["spe_alarm"])

f, ax = fig()
ax.plot([0, 1], [0, 1], ":", color="#6c757d", lw=1, label="no skill")
for mult, color, name in [(1.4, "#3f51b5", "subtle ×1.4"),
                          (2.0, "#e8710a", "moderate ×2.0"),
                          (2.5, "#198754", "severe ×2.5")]:
    faulty = np.asarray(simulate(400, t, n_basis=6, seed=202)) * mult
    far, power = [], []
    for a in alphas:
        m = spm_phase1(ic, t, ncomp=4, alpha=a)
        far.append(flagged(m, fresh).mean())
        power.append(flagged(m, faulty).mean())
    ax.plot(far, power, "o-", color=color, lw=1.6, ms=4, label=name)

ax.set(title="ROC curves: detection power vs. false-alarm rate",
       xlabel="false-alarm rate", ylabel="detection power",
       xlim=(-0.02, 0.55), ylim=(0, 1.02))
ax.legend(loc="lower right", title="fault severity")
print(render(f))
```

The ×2.5 curve reaches high detection at a very low false-alarm rate; the ×1.4
curve sits closer to the diagonal — a subtle fault simply cannot be caught
reliably without accepting more false alarms. This is the honest ceiling of the
chart for a given fault size, independent of how the limit is set.

## Choosing an operating point

An ARL-style reading of the same experiment makes the design choice concrete.
The in-control **average run length** $\mathrm{ARL}_0 \approx 1/\text{FAR}$ is the
mean number of good observations between false alarms; the out-of-control
$\mathrm{ARL}_1 \approx 1/\text{power}$ is the mean number of faulty observations
before an alarm. We tabulate both for the moderate fault.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor

t = np.linspace(0, 1, 80)
ic = np.asarray(simulate(200, t, n_basis=6, seed=7))
fresh = np.asarray(simulate(400, t, n_basis=6, seed=101))
faulty = np.asarray(simulate(400, t, n_basis=6, seed=202)) * 2.0
alphas = np.array([0.20, 0.10, 0.05, 0.02, 0.01, 0.005])

def flagged(model, data):
    r = spm_monitor(
        mean=model["mean"], loadings=model["loadings"], weights=model["weights"],
        eigenvalues=model["eigenvalues"], t2_limit=model["t2_limit"],
        spe_limit=model["spe_limit"], new_data=data, argvals=t,
    )
    return np.asarray(r["t2_alarm"]) | np.asarray(r["spe_alarm"])

arl0, arl1 = [], []
for a in alphas:
    m = spm_phase1(ic, t, ncomp=4, alpha=a)
    far = flagged(m, fresh).mean()
    power = flagged(m, faulty).mean()
    arl0.append(1 / max(far, 1e-3))
    arl1.append(1 / max(power, 1e-3))

x = np.arange(len(alphas))
f, ax = fig()
w = 0.38
ax.bar(x - w / 2, arl0, w, color="#198754", label="$\\mathrm{ARL}_0$ (between false alarms)")
ax.bar(x + w / 2, arl1, w, color="#dc3545", label="$\\mathrm{ARL}_1$ (delay to detect)")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels([f"{a:g}" for a in alphas])
ax.set(title="Run-length trade-off across operating points (moderate fault)",
       xlabel="significance level $\\alpha$", ylabel="average run length (log scale)")
ax.legend(loc="upper left")
print(render(f))
```

Tightening $\alpha$ pushes $\mathrm{ARL}_0$ up (rarer false alarms — good) but
also $\mathrm{ARL}_1$ up (slower detection — bad). A common design fixes a target
$\mathrm{ARL}_0$ (say 100–200 good observations between false alarms) and picks
the $\alpha$ that meets it, then reports the resulting detection delay.

!!! tip "Model-based ARL without a fault stream"
    When you can characterise a fault as a **shift vector** in FPC-score space,
    `fdars.spm.arl1_t2(eigenvalues, ucl, shift, ...)` estimates the detection
    delay by Monte-Carlo directly from the Phase I eigenvalues — no faulty data
    required. See [Advanced SPM](../monitoring/advanced-spm.md#average-run-length-arl).

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `simulate(n, argvals, n_basis, seed)` | `n`, `seed` | Generate in-control functional data |
| `spm_phase1(data, argvals, ncomp, alpha)` | `alpha` | Fit the in-control model at a given significance level |
| `spm_monitor(..., new_data, argvals)` | `new_data` | Return $T^2$/SPE statistics and alarm flags |

## See also

- [Statistical Process Monitoring](../monitoring/spm.md) — the Phase I / Phase II
  workflow.
- [Advanced Statistical Process Monitoring](../monitoring/advanced-spm.md) — EWMA
  charts, run rules, and model-based ARL estimation.
- [Biopharmaceutical Batch Monitoring](biopharma-monitoring.md) — the same
  workflow applied to labelled fermentation batches.
