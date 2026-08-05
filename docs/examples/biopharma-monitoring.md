# Biopharmaceutical Batch Monitoring: Penicillin Fermentation

**Dataset:** Penicillin — 46 fed-batch fermentation runs, each a penicillin
concentration trajectory sampled at 200 time points over a 400-hour cultivation.
Every batch carries a `status` label, `normal` (40 batches) or `faulty` (6).

!!! warning "Synthetic, single-variable dataset"
    This penicillin dataset is **synthetic** — deterministic, seeded logistic
    trajectories that mimic a fed-batch fermentation, not measured data. It is
    included so the monitoring workflow runs end-to-end on labelled
    normal/faulty batches. The R reference uses the real, *multivariate*
    IndPenSim data (temperature, dissolved O₂, sugar feed, pH, …); our loader
    carries only the penicillin trajectory, so this page mirrors the R page's
    **monitoring and yield-prediction** structure but **omits its multivariate
    variable-screening / yield-driver sections**, which have no faithful analogue
    here (see the note at the end). Treat the numbers as illustrative.

In biopharmaceutical manufacturing a batch that goes wrong is expensive: raw
materials, reactor time, and often a whole downstream campaign are lost. The goal
of **batch monitoring** is to notice a deviating batch *while it is still
running*. Each batch is a whole **trajectory**, so this is a
[functional process-monitoring](../monitoring/spm.md) problem: learn the
in-control trajectory distribution from known-good batches (Phase I), then track
every batch against that model (Phase II).

## Batch trajectory exploration

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
ax.plot(t, X[normal].mean(0), color="black", lw=1.6, label="normal mean")
ax.plot([], [], color="#3f51b5", label="normal batches")
ax.plot([], [], color="#dc3545", label="faulty batches")
ax.set(title="Penicillin fermentation trajectories (synthetic)",
       xlabel="time (h)", ylabel="concentration (g/L)")
ax.legend(loc="lower right")
print(render(f))
```

The normal batches (indigo) rise to a plateau near 1.4 g/L; the faulty batches
(red) grow more slowly and level off well below the healthy band. The separation
is clear by eye at the end — the question is how early, and how automatically, a
control chart can flag it.

## FPCA: modes of batch variation

Functional PCA characterises how batches vary around their mean.
`fdars.regression.fpca` returns the mean trajectory, the principal-component
functions (`rotation`), and the per-batch `scores`. Plotting the first two scores
shows where each batch sits in the dominant modes of variation.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render, plt
from docs_data import load_penicillin
from fdars.regression import fpca
from fdars.spm import spm_phase1, select_ncomp

t, X, meta = load_penicillin()
t = np.ascontiguousarray(t)
status = meta["status"].to_numpy()
normal = status == "normal"
Xn = np.ascontiguousarray(X[normal])

eig = np.asarray(spm_phase1(Xn, t, ncomp=8, alpha=0.01)["eigenvalues"])
cum = np.cumsum(eig) / eig.sum()
ncomp = int(select_ncomp(np.ascontiguousarray(eig),
                         method="cumulative_variance", threshold=0.90))
pc = fpca(Xn, t, n_comp=3)
scores = np.asarray(pc["scores"])

f, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.8))
pcs = np.arange(1, len(eig) + 1)
a1.plot(pcs, cum, "o-", color="#3f51b5")
a1.axhline(0.90, color="#e8710a", ls="--")
a1.axvline(ncomp + 0.5, color="#e8710a", ls="--", alpha=0.5)
a1.set(title=f"Cumulative variance (picks {ncomp} PCs)", xlabel="component",
       ylabel="variance explained", ylim=(0, 1.02))
a2.scatter(scores[:, 0], scores[:, 1], s=40, color="#3f51b5",
           alpha=0.8, edgecolor="white")
a2.set(title="FPC score plot (normal batches)",
       xlabel="FPC 1 (yield level)", ylabel="FPC 2 (growth timing)")
print(render(f))
```

A couple of components capture almost all the between-batch variation: **PC1**
tracks the overall yield level and **PC2** the timing of the growth phase.
Concentrating the variation in a low-dimensional subspace is exactly what makes
the FPCA control chart below both sensitive and interpretable.

## Phase I — the in-control model

We fit the FPCA control model on 30 randomly chosen normal batches with
`spm_phase1` (component count from the variance-90 % rule, $\alpha = 0.01$),
holding out the remaining normal batches to check false-alarm behaviour. The
Phase I model gives a mean trajectory and a control envelope.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin
from fdars.spm import spm_phase1, select_ncomp

t, X, meta = load_penicillin()
t = np.ascontiguousarray(t)
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

eig = np.asarray(spm_phase1(np.ascontiguousarray(X[normal]), t, ncomp=8,
                            alpha=0.01)["eigenvalues"])
ncomp = int(select_ncomp(np.ascontiguousarray(eig),
                         method="cumulative_variance", threshold=0.90))

rng = np.random.default_rng(1)
nidx = np.where(normal)[0]; rng.shuffle(nidx)
phase1_idx = nidx[:30]

p1 = spm_phase1(np.ascontiguousarray(X[phase1_idx]), t, ncomp=ncomp, alpha=0.01)
mean = np.asarray(p1["mean"])
sd = X[phase1_idx].std(axis=0)

f, ax = fig()
ax.fill_between(t, mean - 2 * sd, mean + 2 * sd, color="#3f51b5", alpha=0.15,
                label="Phase I ±2σ envelope")
ax.plot(t, mean, color="#3f51b5", lw=2, label="in-control mean")
ax.plot(t, X[faulty].T, color="#dc3545", lw=1.2, alpha=0.9)
ax.plot([], [], color="#dc3545", label="faulty batches")
ax.set(title=f"In-control envelope with faulty batches overlaid (ncomp = {ncomp})",
       xlabel="time (h)", ylabel="concentration (g/L)")
ax.legend(loc="lower right")
print(f"T2 limit : {p1['t2_limit']:.3f}")
print(f"SPE limit: {p1['spe_limit']:.4f}")
print(render(f))
```

The faulty batches leave the ±2σ envelope in the growth phase and never rejoin
it — a functional deviation the control chart is built to quantify.

## Fault detection — monitoring the faulty batches

With the Phase I model fixed, we monitor the faulty batches with two charts: the
**Shewhart** $T^2$/SPE chart (`spm_monitor`) and an **EWMA** chart on the FPC
scores (`ewma_scores`, scored with the MEWMA variance factor
$\lambda/(2-\lambda)$). A batch is out-of-control if a statistic crosses its
limit.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render, plt
from docs_data import load_penicillin
from fdars.spm import (spm_phase1, spm_monitor, select_ncomp,
                       ewma_scores, t2_control_limit)

t, X, meta = load_penicillin()
t = np.ascontiguousarray(t)
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

eig = np.asarray(spm_phase1(np.ascontiguousarray(X[normal]), t, ncomp=8,
                            alpha=0.01)["eigenvalues"])
ncomp = int(select_ncomp(np.ascontiguousarray(eig),
                         method="cumulative_variance", threshold=0.90))
rng = np.random.default_rng(1)
nidx = np.where(normal)[0]; rng.shuffle(nidx)
p1 = spm_phase1(np.ascontiguousarray(X[nidx[:30]]), t, ncomp=ncomp, alpha=0.01)
ev = np.asarray(p1["eigenvalues"])

Xf = np.ascontiguousarray(X[faulty])
mon = spm_monitor(mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
                  eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
                  spe_limit=p1["spe_limit"], new_data=Xf, argvals=t)
t2 = np.asarray(mon["t2"])
shew = np.asarray(mon["t2_alarm"]) | np.asarray(mon["spe_alarm"])

lam = 0.2; factor = lam / (2 - lam)
scores = np.ascontiguousarray(
    ((Xf - np.asarray(p1["mean"])) * np.asarray(p1["weights"]))
    @ np.asarray(p1["loadings"]))
z = np.asarray(ewma_scores(scores, lam))
ew_stat = (z ** 2 / (factor * ev)).sum(axis=1)
ucl_e = t2_control_limit(ncomp, 0.01)["ucl"]
ew = ew_stat > ucl_e

b = np.arange(1, len(t2) + 1)
f, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.6))
for ax, stat, al, lim, name in [
    (a1, t2, shew, p1["t2_limit"], "Shewhart $T^2$"),
    (a2, ew_stat, ew, ucl_e, "EWMA statistic"),
]:
    ax.bar(b, stat, color=["#dc3545" if a else "#3f51b5" for a in al], width=0.6)
    ax.axhline(lim, color="#e8710a", ls="--", lw=1.2)
    ax.set(title=name, xlabel="faulty batch"); ax.set_xticks(b)
f.suptitle("Monitoring the faulty batches", y=1.02)
print(f"Shewhart detected: {int(shew.sum())}/{len(t2)}  |  "
      f"EWMA detected: {int(ew.sum())}/{len(t2)}")
print(render(f))
```

On these synthetic batches the deviation is strong enough that **both charts
catch all six faulty batches** on the full trajectory. (The R reference, on its
harder real-data faults, finds single-variable penicillin monitoring *misses*
them — a reminder that detectability depends entirely on how strongly the fault
manifests in the monitored signal, and that multivariate monitoring is sometimes
essential.)

## False-positive check, precision, recall, F1

Detection rate (recall) alone is incomplete: a chart that flags everything scores
100 % recall but is useless. We estimate false positives on the **held-out
normal** batches, then combine with the fault detections into precision, recall,
and F1.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin
from fdars.spm import (spm_phase1, spm_monitor, select_ncomp,
                       ewma_scores, t2_control_limit)

t, X, meta = load_penicillin()
t = np.ascontiguousarray(t)
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

eig = np.asarray(spm_phase1(np.ascontiguousarray(X[normal]), t, ncomp=8,
                            alpha=0.01)["eigenvalues"])
ncomp = int(select_ncomp(np.ascontiguousarray(eig),
                         method="cumulative_variance", threshold=0.90))
rng = np.random.default_rng(1)
nidx = np.where(normal)[0]; rng.shuffle(nidx)
p1 = spm_phase1(np.ascontiguousarray(X[nidx[:30]]), t, ncomp=ncomp, alpha=0.01)
ev = np.asarray(p1["eigenvalues"])
lam = 0.2; factor = lam / (2 - lam); ucl_e = t2_control_limit(ncomp, 0.01)["ucl"]

def eval_set(idx):
    d = np.ascontiguousarray(X[idx])
    mon = spm_monitor(mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
                      eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
                      spe_limit=p1["spe_limit"], new_data=d, argvals=t)
    shew = np.asarray(mon["t2_alarm"]) | np.asarray(mon["spe_alarm"])
    sc = np.ascontiguousarray(
        ((d - np.asarray(p1["mean"])) * np.asarray(p1["weights"]))
        @ np.asarray(p1["loadings"]))
    z = np.asarray(ewma_scores(sc, lam))
    ew = (z ** 2 / (factor * ev)).sum(axis=1) > ucl_e
    return shew, ew

held = nidx[30:]                                   # held-out normal batches
fault_idx = np.where(faulty)[0]
sh_f, ew_f = eval_set(fault_idx)
sh_h, ew_h = eval_set(held)

methods = {"Shewhart": (sh_f, sh_h), "EWMA": (ew_f, ew_h)}
labels = ["precision", "recall", "F1"]
f, ax = fig()
x = np.arange(len(labels)); w = 0.38
for j, (name, (det, fa)) in enumerate(methods.items()):
    tp = int(det.sum()); fp = int(fa.sum()); n = len(det)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / n
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    ax.bar(x + (j - 0.5) * w, [prec, rec, f1], w,
           color=["#3f51b5", "#198754"][j], label=name)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set(title="Fault detection: precision, recall, F1",
       ylabel="score", ylim=(0, 1.05))
ax.legend()
print(f"held-out normal false alarms — Shewhart: {int(sh_h.sum())}/{len(held)}, "
      f"EWMA: {int(ew_h.sum())}/{len(held)}")
print(render(f))
```

Both charts reach high recall (all faults caught) with few false alarms on the
held-out normal batches, so precision and F1 stay high. On harder faults the
picture would be more nuanced — precision and recall would diverge and F1 would
locate the smallest reliably-detectable fault, as in the
[inline-monitoring study](inline-monitoring.md).

## When does a batch breach the limit?

Whole-batch monitoring only tells us *after* the run finishes. The manufacturing
value is in catching a fault sooner. We monitor **partial trajectories**: at a
sequence of checkpoints we refit the Phase I model on the same window of the
normal batches and monitor each batch up to that point. The first checkpoint at
which a batch alarms is its **time-to-detection**.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from docs_data import load_penicillin
from fdars.spm import spm_phase1, spm_monitor

t, X, meta = load_penicillin()
t = np.ascontiguousarray(t)
status = meta["status"].to_numpy()
normal, faulty = status == "normal", status == "faulty"

rng = np.random.default_rng(1)
nidx = np.where(normal)[0]; rng.shuffle(nidx)
phase1_idx = nidx[:30]
heldout = nidx[30:]
faulty_idx = np.where(faulty)[0]
stream = np.concatenate([heldout, faulty_idx])

checkpoints = np.arange(20, 201, 20)
first_alarm = np.full(len(X), -1.0)
for k in checkpoints:
    tw = np.ascontiguousarray(t[:k]); Xw = np.ascontiguousarray(X[:, :k])
    p1 = spm_phase1(np.ascontiguousarray(Xw[phase1_idx]), tw, ncomp=4, alpha=0.01)
    p2 = spm_monitor(mean=p1["mean"], loadings=p1["loadings"], weights=p1["weights"],
                     eigenvalues=p1["eigenvalues"], t2_limit=p1["t2_limit"],
                     spe_limit=p1["spe_limit"],
                     new_data=np.ascontiguousarray(Xw[stream]), argvals=tw)
    al = np.asarray(p2["t2_alarm"]) | np.asarray(p2["spe_alarm"])
    fa = first_alarm[stream]
    fa[al & (fa < 0)] = t[k - 1]
    first_alarm[stream] = fa

f, ax = fig()
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
       xlabel="time (h)", ylabel="concentration (g/L)")
ax.legend(loc="lower right")

fa_times = first_alarm[faulty_idx]
n_ho = int((first_alarm[heldout] >= 0).sum())
print(f"faulty first-alarm times (h): {sorted(int(x) for x in fa_times)}")
print(f"held-out normal batches ever flagged: {n_ho}/{len(heldout)}")
print(render(f))
```

The faulty batches breach the limit early in the growth phase — roughly a tenth
of the way through a 400-hour run, long before the trajectories visibly separate
at the plateau. A couple of held-out normal batches trip a transient early flag
when the window is very short and the model is estimated from few points; in
practice one would require a run of consecutive alarms (see the
[run rules](../monitoring/advanced-spm.md#run-rules)) before stopping a batch.

## Yield prediction from early process data

Beyond raising alarms, we can *predict* the final penicillin concentration from
the **early** part of the trajectory (first 200 h) — useful for screening and
early intervention. `fdars.regression.fregre_lm` fits a scalar-on-function
(principal-component) regression, and `fregre_cv` picks the component count by
cross-validation.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render, plt
from docs_data import load_penicillin
from fdars.regression import fregre_lm, fregre_cv

t, X, meta = load_penicillin()
t = np.ascontiguousarray(t)
status = meta["status"].to_numpy()
normal = status == "normal"

early = t <= 200
Xe = np.ascontiguousarray(X[normal][:, early])
te = np.ascontiguousarray(t[early])
y = np.ascontiguousarray(X[:, -1][normal])          # final concentration

# R2 vs number of components
ncomps = [1, 2, 3, 4, 5]
r2 = [float(fregre_lm(Xe, y, n_comp=nc)["r_squared"]) for nc in ncomps]

cv = fregre_cv(Xe, y, k_min=1, k_max=6, n_folds=5)
kopt = int(cv["optimal_k"])
fit = fregre_lm(Xe, y, n_comp=kopt)
yhat = np.asarray(fit["fitted_values"])

f, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.8))
a1.plot(ncomps, r2, "o-", color="#3f51b5")
a1.axvline(kopt, color="#e8710a", ls="--", label=f"CV-optimal k = {kopt}")
a1.set(title="R² vs. number of components", xlabel="FPC components",
       ylabel="R²", ylim=(0, 1.02)); a1.legend(loc="lower right")
lim = [y.min() - 0.03, y.max() + 0.03]
a2.plot(lim, lim, ls="--", color="#6c757d")
a2.scatter(y, yhat, s=40, color="#198754", alpha=0.8, edgecolor="white")
a2.set(title=f"Observed vs. fitted (k = {kopt}, R² = {fit['r_squared']:.3f})",
       xlabel="observed final conc. (g/L)", ylabel="predicted (g/L)",
       xlim=lim, ylim=lim)
print(render(f))
```

R² climbs as components are added — more of the yield-relevant variation in the
early trajectory is captured — and the CV-selected model tracks the final
concentration closely. On this synthetic data the relationship is nearly
deterministic, so R² is very high; on the real IndPenSim data the R page reports
a more realistic R² ≈ 0.49, still useful for early screening but far from exact.
The `beta_t` coefficient function returned by `fregre_lm` shows which time
windows of the early trajectory carry the most predictive weight — the critical
control windows.

!!! tip "Refitting the window vs. a landmark-registered model"
    The time-to-detection section refits Phase I at each checkpoint so the model
    always matches the observed window length. An alternative is to register
    batches to a common phase (e.g. by a maturity index) and monitor against a
    single model — see
    [Profile and Partial-Domain Monitoring](../monitoring/profile-partial-monitoring.md).

!!! note "Binding / dataset gaps vs. the R reference"
    The R vignette runs on the **multivariate** IndPenSim data and includes a
    variable-screening / yield-driver analysis across temperature, dissolved O₂,
    sugar feed, pH, and aeration, plus **CUSUM** and **MEWMA** charts. Our
    synthetic loader carries only the single penicillin trajectory, and this
    build has no CUSUM or packaged MEWMA binding — so those sections are omitted
    rather than faked, and the second monitoring chart here is an EWMA assembled
    transparently from `ewma_scores`.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `fpca(data, argvals, n_comp)` | `n_comp` | Modes of batch variation; returns `scores`, `rotation`, `mean` |
| `spm_phase1(data, argvals, ncomp, alpha)` | `ncomp`, `alpha` | Fit the in-control FPCA model and control limits |
| `select_ncomp(eigenvalues, method, threshold)` | `method`, `threshold` | Choose the number of components |
| `spm_monitor(mean, loadings, weights, eigenvalues, t2_limit, spe_limit, new_data, argvals)` | `new_data` | Project and flag batches |
| `ewma_scores(scores, lambda_)` | `lambda_` | Smooth FPC-score vectors for an EWMA chart |
| `fregre_lm(data, response, n_comp)` | `n_comp` | Scalar-on-function (PCR) regression; returns `r_squared`, `beta_t` |
| `fregre_cv(data, response, k_min, k_max, n_folds)` | `k_max`, `n_folds` | Cross-validate the component count |

## See also

- [Statistical Process Monitoring](../monitoring/spm.md) — the two-phase workflow
  and the $T^2$ / SPE statistics.
- [Advanced Statistical Process Monitoring](../monitoring/advanced-spm.md) —
  EWMA charts for slow drifts, run rules, and ARL analysis.
- [Inline Quality Monitoring](inline-monitoring.md) — detection power and
  false-alarm trade-offs, with precision/recall/F1 over fault severity.
