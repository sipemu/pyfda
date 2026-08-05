# Advanced Statistical Process Monitoring

The [basic control chart](spm.md) flags an observation whenever its $T^2$ statistic
crosses a limit. Real monitoring problems ask more: *How long until a small drift is
detected? Which principal component is responsible for a fault? Is a run of borderline
points a genuine trend or just noise?* This page covers the tools `fdars.spm` provides
for these questions — the **SPE / Q** statistic, **EWMA** charts for slow drifts,
**run rules** (Nelson, Western Electric), **average run length** (ARL) analysis, and
**per-PC contribution** diagnosis for locating faults.

All of the examples below build on a single Phase I model. The setup — 120 in-control
Phase I curves, then a Phase II stream of 30 in-control curves followed by a slow upward
drift — is reused throughout; each figure block below re-creates it for reproducibility.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor, ewma_scores, hotelling_t2

argvals = np.linspace(0, 1, 80)

# Phase I: 120 in-control curves
ic = np.asarray(simulate(120, argvals, n_basis=6, seed=7))
p1 = spm_phase1(ic, argvals, ncomp=4, alpha=0.01)

# Phase II: 30 in-control curves followed by a slow upward drift
ok = np.asarray(simulate(30, argvals, n_basis=6, seed=21))
drift = np.asarray(simulate(20, argvals, n_basis=6, seed=33))
drift = drift + np.linspace(0, 2.4, 20)[:, None]          # ramp: 0 -> 2.4
new = np.vstack([ok, drift])

f, ax = fig()
ax.plot(argvals, ic.T, color="#6c757d", lw=0.5, alpha=0.30)
ax.plot(argvals, ok.T, color="#3f51b5", lw=0.7, alpha=0.5)
ax.plot(argvals, drift.T, color="#e8710a", lw=0.9, alpha=0.7)
ax.set(title="Phase I baseline (grey), in-control Phase II (indigo), drifting stream (orange)",
       xlabel="t", ylabel="x(t)")
print(render(f))
```

---

## Concepts

### Two statistics, two failure modes

FPCA splits every centered curve $\tilde x_i(t) = x_i(t) - \hat\mu(t)$ into a part that
lives in the retained subspace and a residual orthogonal to it:

$$
\tilde x_i(t) = \underbrace{\sum_{k=1}^{K} \xi_{ik}\,\phi_k(t)}_{\text{modelled}}
              + \underbrace{e_i(t)}_{\text{residual}} .
$$

The **Hotelling $T^2$** statistic watches the modelled part; the **SPE** (squared
prediction error, also called the **Q** statistic) watches the residual:

$$
T^2_i = \sum_{k=1}^{K} \frac{\xi_{ik}^2}{\lambda_k},
\qquad
\mathrm{SPE}_i = \int e_i(t)^2\,dt .
$$

A shift *inside* the subspace (an amplitude change, a mean shift along a dominant
mode) inflates $T^2$. A departure the model *cannot* represent (new high-frequency
structure) inflates SPE. Monitoring both is standard practice.

### Control limits

Under the in-control model, $T^2 \sim \chi^2_K$, so
`t2_control_limit(ncomp, alpha)` returns the $1-\alpha$ chi-squared quantile. The SPE
distribution is heavier-tailed; `spe_control_limit` fits a moment-matched
$g\,\chi^2_h$ approximation to the Phase I SPE values.

```python exec="1" html="1" source="above"
import numpy as np
from fdars.simulation import simulate
from fdars.spm import spm_phase1, t2_control_limit, spe_control_limit

argvals = np.linspace(0, 1, 80)
p1 = spm_phase1(np.asarray(simulate(120, argvals, n_basis=6, seed=7)),
                argvals, ncomp=4, alpha=0.01)

t2_ucl = t2_control_limit(ncomp=4, alpha=0.01)
spe_ucl = spe_control_limit(np.asarray(p1["spe"]), alpha=0.01)
print("t2 :", t2_ucl)
print("spe:", spe_ucl)
```

Both return a dict with `ucl`, `alpha`, and a `description` string. In practice
`spm_phase1` has already stored `t2_limit` / `spe_limit`; these helpers are useful when
you want a limit for a different $\alpha$ or for a chart you are building by hand.

### Average run length (ARL)

The **ARL** is the expected number of observations until an alarm. In-control you want
it *large* ($\mathrm{ARL}_0$ = mean time between false alarms); out-of-control you want
it *small* ($\mathrm{ARL}_1$ = detection delay). `fdars.spm` estimates both by Monte
Carlo simulation from the eigenvalues.

| Function | Purpose |
|---|---|
| `arl0_t2(eigenvalues, ucl, ...)` | In-control ARL of the $T^2$ chart |
| `arl1_t2(eigenvalues, ucl, shift, ...)` | Detection delay for a given `shift` vector |
| `arl0_ewma_t2(eigenvalues, ucl, lambda_, ...)` | In-control ARL of the EWMA-$T^2$ chart |
| `arl0_spe(spe_df, spe_scale, ucl, ...)` | In-control ARL of the SPE chart |

Each returns `{arl, std_dev, median_rl}`.

```python exec="1" html="1" source="above"
import numpy as np
from fdars.simulation import simulate
from fdars.spm import spm_phase1, arl0_t2, arl1_t2

argvals = np.linspace(0, 1, 80)
p1 = spm_phase1(np.asarray(simulate(120, argvals, n_basis=6, seed=7)),
                argvals, ncomp=4, alpha=0.01)
ev = np.asarray(p1["eigenvalues"])
ucl = p1["t2_limit"]

a0 = arl0_t2(ev, ucl, n_simulations=3000, seed=1)
a1 = arl1_t2(ev, ucl, shift=np.array([2.0, 0.0, 0.0, 0.0]),
             n_simulations=3000, seed=1)
print(f"ARL0 (mean run to a false alarm): {a0['arl']:.1f}")
print(f"ARL1 (delay for a 2-sigma shift on PC1): {a1['arl']:.1f}")
```

!!! note "Interpreting the pair"
    A useful design targets a fixed $\mathrm{ARL}_0$ (say 200) by tuning `alpha`, then
    compares $\mathrm{ARL}_1$ across chart types. The chart with the smaller
    $\mathrm{ARL}_1$ at the same $\mathrm{ARL}_0$ detects the shift faster.

---

## EWMA charts for slow drifts

A Shewhart $T^2$ chart looks at each observation in isolation, so a shift much smaller
than the control limit can persist for a long time undetected. An **EWMA**
(exponentially weighted moving average) smooths the score vector,

$$
\mathbf z_i = \lambda\,\boldsymbol\xi_i + (1-\lambda)\,\mathbf z_{i-1},
\qquad 0 < \lambda \le 1,
$$

so that a sustained small drift accumulates. `ewma_scores(scores, lambda_)` returns the
smoothed score matrix; feeding it to `hotelling_t2` gives an EWMA-$T^2$ chart.

Because `spm_monitor` returns statistics but not the raw scores, we project the centered
Phase II curves onto the loadings ourselves. With integration weights $w(t)$ the score
of curve $i$ on component $k$ is $\xi_{ik} = \int \tilde x_i(t)\,\phi_k(t)\,dt \approx
\sum_t \tilde x_i(t)\,\phi_k(t)\,w(t)$, i.e. `(Xc * w) @ loadings`.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.spm import spm_phase1, ewma_scores, hotelling_t2

argvals = np.linspace(0, 1, 80)
p1 = spm_phase1(np.asarray(simulate(120, argvals, n_basis=6, seed=7)),
                argvals, ncomp=4, alpha=0.01)
ok = np.asarray(simulate(30, argvals, n_basis=6, seed=21))
drift = np.asarray(simulate(20, argvals, n_basis=6, seed=33))
drift = drift + np.linspace(0, 2.4, 20)[:, None]
new = np.vstack([ok, drift])

mean = np.asarray(p1["mean"])
loadings = np.asarray(p1["loadings"])
weights = np.asarray(p1["weights"])
ev = np.asarray(p1["eigenvalues"])

# scores of the Phase II stream (matches spm_monitor's internal T2 exactly)
scores = ((new - mean) * weights) @ loadings

lam = 0.2
z = np.asarray(ewma_scores(scores, lam))           # smoothed scores
t2_raw = np.asarray(hotelling_t2(scores, ev))      # Shewhart T2
t2_ewma = np.asarray(hotelling_t2(z, ev))          # EWMA T2

# EWMA control limit: variance of the EWMA is scaled by lam / (2 - lam)
ewma_ucl = p1["t2_limit"] * lam / (2 - lam)
obs = np.arange(1, len(new) + 1)

f, ax = fig()
ax.plot(obs, t2_raw, "o-", ms=3, lw=0.8, color="#c7cbe0", label="Shewhart $T^2$")
ax.plot(obs, t2_ewma, "o-", ms=4, lw=1.4, color="#3f51b5", label=f"EWMA $T^2$ ($\\lambda={lam}$)")
ax.axhline(ewma_ucl, color="#e8710a", ls="--", lw=1.3, label="EWMA control limit")
ax.axvline(30.5, color="#6c757d", ls=":", lw=1, label="drift starts")
ax.set(title="EWMA smooths a slow drift into a clear, sustained signal",
       xlabel="observation index", ylabel="$T^2$")
ax.legend(loc="upper left", fontsize=8)
print(render(f))
```

The Shewhart trace (grey) wanders around the drift without a decisive crossing; the
EWMA trace (indigo) ramps up smoothly once the drift begins and stays above its limit.

| Parameter | Type | Description |
|---|---|---|
| `scores` | `(n, ncomp)` array | FPC scores of the stream |
| `lambda_` | float in `(0, 1]` | Smoothing weight; smaller = more smoothing, slower response |

!!! tip "Choosing `λ`"
    Small $\lambda$ (0.05–0.2) is tuned for small persistent shifts; $\lambda \to 1$
    recovers the memoryless Shewhart chart. Use `arl0_ewma_t2(ev, ucl, lambda_)` to
    check the in-control ARL of your chosen $\lambda$ before deploying it.

---

## Run rules

Rather than looking only at limit crossings, **run rules** flag suspicious *patterns* —
several points on one side of the centre line, a monotone run, a point in the outer
zone. `fdars.spm` implements the two classic rule sets:

- `western_electric_rules(values, center, sigma)` — the four Western Electric zone rules.
- `nelson_rules(values, center, sigma)` — the eight Nelson rules (a superset).

Both take the monitoring statistic, a centre line, and a $\sigma$ estimate, and return a
`list[dict]`, each `{"rule": <name>, "indices": [...]}`.

```python exec="1" html="1" source="above"
import numpy as np
from fdars.simulation import simulate
from fdars.spm import spm_phase1, hotelling_t2, western_electric_rules, nelson_rules

argvals = np.linspace(0, 1, 80)
p1 = spm_phase1(np.asarray(simulate(120, argvals, n_basis=6, seed=7)),
                argvals, ncomp=4, alpha=0.01)
ok = np.asarray(simulate(30, argvals, n_basis=6, seed=21))
drift = np.asarray(simulate(20, argvals, n_basis=6, seed=33))
drift = drift + np.linspace(0, 2.4, 20)[:, None]
new = np.vstack([ok, drift])
scores = ((new - np.asarray(p1["mean"])) * np.asarray(p1["weights"])) @ np.asarray(p1["loadings"])
ev = np.asarray(p1["eigenvalues"])

t2_stream = np.asarray(hotelling_t2(scores, ev))
center = float(np.median(np.asarray(p1["t2"])))
sigma = float(np.std(np.asarray(p1["t2"])))

we = western_electric_rules(t2_stream, center, sigma)
ns = nelson_rules(t2_stream, center, sigma)
print("Western Electric violations:")
for v in we:
    print(f"  {v['rule']:>4}  at indices {v['indices']}")
print(f"Nelson rules fired: {sorted({v['rule'] for v in ns})}")
```

| Parameter | Type | Description |
|---|---|---|
| `values` | `(n,)` array | Monitoring statistic to scan |
| `center` | float | Centre line (e.g. in-control median) |
| `sigma` | float | Standard-deviation estimate for the zone widths |

Run rules increase sensitivity to small shifts but also raise the false-alarm rate;
they are most useful layered on top of, not instead of, a limit-based chart.

---

## Fault diagnosis: per-PC contributions

When a point alarms, the next question is *why*. Because $T^2 = \sum_k \xi_k^2/\lambda_k$
is a sum over components, each component's term is an interpretable **contribution**.
`t2_pc_contributions(scores, eigenvalues)` returns the per-PC contributions (they sum to
the total $T^2$), and `t2_pc_significance(contributions, alpha)` flags which components
are individually significant under a Bonferroni-adjusted per-component test.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.spm import spm_phase1, t2_pc_contributions, t2_pc_significance

argvals = np.linspace(0, 1, 80)
p1 = spm_phase1(np.asarray(simulate(120, argvals, n_basis=6, seed=7)),
                argvals, ncomp=4, alpha=0.01)
ok = np.asarray(simulate(30, argvals, n_basis=6, seed=21))
drift = np.asarray(simulate(20, argvals, n_basis=6, seed=33))
drift = drift + np.linspace(0, 2.4, 20)[:, None]
new = np.vstack([ok, drift])
scores = ((new - np.asarray(p1["mean"])) * np.asarray(p1["weights"])) @ np.asarray(p1["loadings"])
ev = np.asarray(p1["eigenvalues"])

contrib = np.asarray(t2_pc_contributions(scores, ev))     # (n, ncomp)
sig = np.asarray(t2_pc_significance(contrib, alpha=0.05))  # 0/1 flags

# diagnose the most extreme drifting observation
worst = int(np.argmax(contrib.sum(axis=1)))
c = contrib[worst]
flags = sig[worst].astype(bool)
pcs = np.arange(1, len(c) + 1)

f, ax = fig()
colors = ["#dc3545" if fl else "#3f51b5" for fl in flags]
ax.bar(pcs, c, color=colors)
ax.set(title=f"$T^2$ contribution breakdown for observation #{worst + 1}",
       xlabel="principal component", ylabel="contribution $\\xi_k^2/\\lambda_k$")
ax.set_xticks(pcs)
# annotate the total
ax.text(0.97, 0.95, f"total $T^2$ = {c.sum():.1f}", transform=ax.transAxes,
        ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="#f4f4fb", ec="#c7cbe0"))
print(render(f))
```

Red bars mark components flagged as significant contributors — these localise the fault
to specific modes of variation, telling the operator *which* aspect of the process moved
rather than merely *that* it moved.

| Parameter | Type | Description |
|---|---|---|
| `scores` | `(n, ncomp)` array | FPC scores |
| `eigenvalues` | `(ncomp,)` array | Eigenvalues $\lambda_k$ |
| `contributions` | `(n, ncomp)` array | Output of `t2_pc_contributions`, input to `t2_pc_significance` |
| `alpha` | float | Family-wise significance level (Bonferroni-adjusted) |

---

## See also

- [Statistical Process Monitoring](spm.md) — the Phase I / Phase II basics and the
  two-fault control-chart example.
- [Profile and Partial-Domain Monitoring](profile-partial-monitoring.md) — restricting
  the analysis to a sub-interval of the domain to catch localised faults.

!!! info "Everything runs in Rust"
    Contributions, run rules, and the Monte-Carlo ARL simulations are all implemented in
    the compiled core; the projection step (`(Xc * w) @ loadings`) is the only piece done
    in NumPy on this page, and it reproduces `spm_monitor`'s internal $T^2$ to machine
    precision.
