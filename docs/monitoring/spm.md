# Statistical Process Monitoring

Monitor streams of functional data for out-of-control behavior using FPCA-based control charts. The workflow has two phases:

1. **Phase I** -- Estimate the in-control distribution from historical data and compute control limits.
2. **Phase II** -- Project each incoming observation onto the learned subspace and check whether its $T^2$ or SPE statistic exceeds the limits.

---

## Concepts

### FPCA-based monitoring

Each curve $x_i(t)$ is centered by subtracting the mean $\hat\mu(t)$ and projected onto the first $K$ functional principal components, yielding a score vector $\boldsymbol\xi_i \in \mathbb{R}^K$. Two complementary statistics capture different kinds of departure:

| Statistic | What it measures | Formula |
|---|---|---|
| **Hotelling $T^2$** | Systematic shift in the FPC subspace | $T^2 = \sum_{k=1}^{K} \xi_k^2 / \lambda_k$ |
| **SPE (Q)** | Residual variation outside the subspace | $\mathrm{SPE} = \int [\tilde x(t)]^2 \, dt$ where $\tilde x$ is the reconstruction residual |

Control limits for both are estimated from the Phase I data so that the in-control false-alarm rate is approximately $\alpha$.

---

## Phase I -- estimating the baseline

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate
from fdars.spm import spm_phase1

# Generate 80 in-control curves on a 100-point grid
argvals = np.linspace(0, 1, 100)
fd_ic = Fdata(simulate(80, argvals, n_basis=5, seed=1), argvals=argvals)

# Phase I estimation (3 components, alpha = 0.05)
p1 = spm_phase1(fd_ic.data, fd_ic.argvals, ncomp=3, alpha=0.05)
```

`spm_phase1` returns a dictionary with the following keys:

| Key | Shape | Description |
|---|---|---|
| `t2` | `(n,)` | $T^2$ statistic for every Phase I observation |
| `spe` | `(n,)` | SPE statistic for every Phase I observation |
| `t2_limit` | scalar | Upper control limit for $T^2$ |
| `spe_limit` | scalar | Upper control limit for SPE |
| `mean` | `(m,)` | Estimated mean function $\hat\mu(t)$ |
| `loadings` | `(m, ncomp)` | FPCA rotation matrix (eigenfunctions) |
| `weights` | `(m,)` | Integration weights for the inner product |
| `eigenvalues` | `(ncomp,)` | Eigenvalues $\lambda_1, \dots, \lambda_K$ |

!!! tip "Choosing `ncomp`"
    A common rule of thumb is to retain enough components to explain 90--95 % of the total variance. Too few components make the SPE chart over-sensitive; too many inflate the $T^2$ chart.

---

## Phase II -- monitoring new observations

```python
from fdars.spm import spm_monitor

# Simulate 20 new in-control observations + 10 faulty ones
data_new_ic = simulate(20, argvals, n_basis=5, seed=2)

# Inject a mean shift into the last 10 curves
data_fault = simulate(10, argvals, n_basis=5, seed=3) + 2.0
fd_new = Fdata(np.vstack([data_new_ic, data_fault]), argvals=argvals)

# Monitor
p2 = spm_monitor(
    mean=p1["mean"],
    loadings=p1["loadings"],
    weights=p1["weights"],
    eigenvalues=p1["eigenvalues"],
    t2_limit=p1["t2_limit"],
    spe_limit=p1["spe_limit"],
    new_data=fd_new.data,
    argvals=fd_new.argvals,
)
```

The returned dictionary contains:

| Key | Shape | Description |
|---|---|---|
| `t2` | `(n_new,)` | $T^2$ for each new observation |
| `spe` | `(n_new,)` | SPE for each new observation |
| `t2_alarm` | `(n_new,)` bool | `True` where $T^2$ exceeds the limit |
| `spe_alarm` | `(n_new,)` bool | `True` where SPE exceeds the limit |

```python
# How many faults were caught?
n_t2_alarms = int(p2["t2_alarm"].sum())
n_spe_alarms = int(p2["spe_alarm"].sum())
print(f"T2 alarms: {n_t2_alarms}, SPE alarms: {n_spe_alarms}")
```

---

## Hotelling $T^2$ from scores

If you already have FPC scores (e.g., from your own FPCA), you can compute the $T^2$ statistic directly:

```python
from fdars.spm import hotelling_t2

# scores: (n, p) array of FPC scores
# eigenvalues: (p,) array
t2_values = hotelling_t2(scores, eigenvalues)
```

---

## Full worked example

The script below ties everything together: simulate in-control data, run Phase I, introduce a fault, monitor in Phase II, and visualize the control chart.

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate
from fdars.spm import spm_phase1, spm_monitor

# ── 1. Simulate in-control data ──────────────────────────────
argvals = np.linspace(0, 1, 100)
fd_ic = Fdata(simulate(100, argvals, n_basis=5, seed=10), argvals=argvals)

# ── 2. Phase I ───────────────────────────────────────────────
p1 = spm_phase1(fd_ic.data, fd_ic.argvals, ncomp=3, alpha=0.05)
print(f"T2 limit : {p1['t2_limit']:.3f}")
print(f"SPE limit: {p1['spe_limit']:.3f}")

# ── 3. Simulate Phase II data (in-control + fault) ──────────
data_ok  = simulate(30, argvals, n_basis=5, seed=20)
data_bad = simulate(20, argvals, n_basis=5, seed=30) + 3.0  # mean shift
fd_new = Fdata(np.vstack([data_ok, data_bad]), argvals=argvals)

# ── 4. Phase II monitoring ───────────────────────────────────
p2 = spm_monitor(
    mean=p1["mean"],
    loadings=p1["loadings"],
    weights=p1["weights"],
    eigenvalues=p1["eigenvalues"],
    t2_limit=p1["t2_limit"],
    spe_limit=p1["spe_limit"],
    new_data=fd_new.data,
    argvals=fd_new.argvals,
)

# ── 5. Report ────────────────────────────────────────────────
obs_ids = np.arange(1, len(fd_new) + 1)
alarm_idx = obs_ids[p2["t2_alarm"] | p2["spe_alarm"]]
print(f"Alarm observations: {alarm_idx}")

# ── 6. Visualize (optional, requires matplotlib) ─────────────
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    axes[0].plot(obs_ids, p2["t2"], "o-", markersize=3)
    axes[0].axhline(p1["t2_limit"], color="red", linestyle="--", label="UCL")
    axes[0].set_ylabel("Hotelling T²")
    axes[0].legend()

    axes[1].plot(obs_ids, p2["spe"], "o-", markersize=3)
    axes[1].axhline(p1["spe_limit"], color="red", linestyle="--", label="UCL")
    axes[1].set_ylabel("SPE (Q)")
    axes[1].set_xlabel("Observation index")
    axes[1].legend()

    fig.suptitle("FPCA-based Control Charts")
    plt.tight_layout()
    plt.savefig("spm_control_chart.png", dpi=150)
    plt.show()
except ImportError:
    pass
```

!!! info "Performance note"
    Both `spm_phase1` and `spm_monitor` delegate all linear algebra to Rust. Phase I on 500 curves of length 200 typically completes in under 10 ms.
