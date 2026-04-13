# fdars.spm

Statistical Process Monitoring (SPM) for functional data using FPCA-based control charts.

## Functions

| Function | Description |
|----------|-------------|
| [`spm_phase1`](#spm_phase1) | Phase I estimation (in-control model) |
| [`spm_monitor`](#spm_monitor) | Phase II monitoring (new observations) |
| [`hotelling_t2`](#hotelling_t2) | Hotelling T-squared statistic |

---

### `spm_phase1`

```python
fdars.spm_phase1(data, argvals, ncomp=3, alpha=0.05)
```

Phase I: estimate the in-control model from historical data. Computes FPCA, T-squared, and SPE statistics with control limits.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `ndarray (n, m)` | | In-control functional data |
| `argvals` | `ndarray (m,)` | | Evaluation points |
| `ncomp` | `int` | `3` | Number of FPC components |
| `alpha` | `float` | `0.05` | Significance level for control limits |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `t2` (n,), `spe` (n,), `t2_limit`, `spe_limit`, `mean` (m,), `loadings` (m, ncomp), `weights` (m,), `eigenvalues` (ncomp,) |

```python
t = np.linspace(0, 1, 100)
phase1 = fdars.spm_phase1(data, t, ncomp=3, alpha=0.05)
print(f"T2 limit: {phase1['t2_limit']:.2f}")
print(f"SPE limit: {phase1['spe_limit']:.2f}")
```

---

### `spm_monitor`

```python
fdars.spm_monitor(mean, loadings, weights, eigenvalues,
                  t2_limit, spe_limit, new_data, argvals)
```

Phase II: monitor new observations against the in-control model from Phase I.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mean` | `ndarray (m,)` | FPCA mean from Phase I |
| `loadings` | `ndarray (m, ncomp)` | FPCA rotation matrix from Phase I |
| `weights` | `ndarray (m,)` | Integration weights from Phase I |
| `eigenvalues` | `ndarray (ncomp,)` | Eigenvalues from Phase I |
| `t2_limit` | `float` | T-squared upper control limit |
| `spe_limit` | `float` | SPE upper control limit |
| `new_data` | `ndarray (n_new, m)` | New observations to monitor |
| `argvals` | `ndarray (m,)` | Evaluation points |

| Returns | Type | Description |
|---------|------|-------------|
| result | `dict` | Keys: `t2` (n_new,), `spe` (n_new,), `t2_alarm` (bool array), `spe_alarm` (bool array) |

```python
monitor = fdars.spm_monitor(
    phase1["mean"], phase1["loadings"], phase1["weights"],
    phase1["eigenvalues"], phase1["t2_limit"], phase1["spe_limit"],
    new_data, t
)
if any(monitor["t2_alarm"]):
    print("T2 alarm triggered!")
```

---

### `hotelling_t2`

```python
fdars.hotelling_t2(scores, eigenvalues)
```

Compute the Hotelling T-squared statistic from FPC scores.

| Parameter | Type | Description |
|-----------|------|-------------|
| `scores` | `ndarray (n, p)` | FPC scores |
| `eigenvalues` | `ndarray (p,)` | Eigenvalues |

| Returns | Type | Description |
|---------|------|-------------|
| t2 | `ndarray (n,)` | T-squared statistics |

```python
pca = fdars.fpca(data, t, n_comp=3)
t2 = fdars.hotelling_t2(pca["scores"], pca["singular_values"]**2)
```
