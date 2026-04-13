# Tolerance Bands

Tolerance bands define a region that is expected to contain a specified proportion of future functional observations. They are the functional analogue of prediction intervals and are widely used in quality control, clinical trials, and environmental monitoring.

`fdars` provides three complementary approaches plus a functional equivalence test.

---

## FPCA bootstrap tolerance band

This method uses the FPCA representation of the sample to generate bootstrap replicates, from which a simultaneous tolerance band is constructed.

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate
from fdars.tolerance import fpca_tolerance_band

argvals = np.linspace(0, 1, 100)
fd = Fdata(simulate(60, argvals, n_basis=5, seed=1), argvals=argvals)

band = fpca_tolerance_band(fd.data, ncomp=3, nb=1000, coverage=0.95, seed=42)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Observed functional data |
| `ncomp` | `int` | `3` | Number of FPC components to retain |
| `nb` | `int` | `1000` | Number of bootstrap replicates |
| `coverage` | `float` | `0.95` | Desired coverage probability |
| `seed` | `int` | `42` | Random seed |

**Returns** a dictionary:

| Key | Shape | Description |
|---|---|---|
| `upper` | `(m,)` | Upper boundary of the band |
| `lower` | `(m,)` | Lower boundary of the band |
| `center` | `(m,)` | Pointwise center (mean) |
| `half_width` | `(m,)` | Half-width at each grid point |

---

## Conformal prediction band

A distribution-free alternative that splits the data into a proper training set and a calibration set, then uses the calibration residuals to determine the band width.

```python
from fdars.tolerance import conformal_prediction_band

band_cp = conformal_prediction_band(fd.data, coverage=0.95, cal_fraction=0.25, seed=42)
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Observed functional data |
| `coverage` | `float` | `0.95` | Target coverage |
| `cal_fraction` | `float` | `0.25` | Fraction of data reserved for calibration |
| `seed` | `int` | `42` | Random seed |

**Returns** a dictionary with the same keys as the FPCA band (`upper`, `lower`, `center`, `half_width`).

!!! note "When to prefer conformal bands"
    Conformal bands make no distributional assumptions. They are especially useful when the underlying process is non-Gaussian or when the sample size is small enough that the FPCA bootstrap may be unreliable.

---

## Simultaneous confidence band (Degras)

Constructs a simultaneous confidence band for the **mean function** using the Gaussian multiplier bootstrap method of Degras (2011).

```python
from fdars.tolerance import scb_mean_degras

band_scb = scb_mean_degras(fd.data, fd.argvals, bandwidth=0.0, nb=1000, confidence=0.95)
```

Setting `bandwidth=0.0` enables automatic bandwidth selection.

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `ndarray (n, m)` | -- | Observed data |
| `argvals` | `ndarray (m,)` | -- | Evaluation grid |
| `bandwidth` | `float` | `0.0` | Kernel bandwidth (`0.0` = auto) |
| `nb` | `int` | `1000` | Number of bootstrap samples |
| `confidence` | `float` | `0.95` | Confidence level |

**Returns** the same dictionary structure (`upper`, `lower`, `center`, `half_width`).

!!! info "Tolerance band vs. confidence band"
    A **tolerance band** targets individual future curves (analogous to a prediction interval). A **confidence band** targets the mean function (analogous to a confidence interval). Use `fpca_tolerance_band` or `conformal_prediction_band` for the former, and `scb_mean_degras` for the latter.

---

## Equivalence test

Test whether two groups of functional observations are *equivalent* -- i.e., their mean functions differ by no more than a margin $\delta$ -- using a functional TOST (two one-sided tests) procedure.

```python
from fdars.tolerance import equivalence_test

# Two groups with similar means
fd_a = Fdata(simulate(40, argvals, n_basis=5, seed=10), argvals=argvals)
fd_b = Fdata(simulate(40, argvals, n_basis=5, seed=20) + 0.1, argvals=argvals)  # small shift

result = equivalence_test(fd_a.data, fd_b.data, delta=0.5, alpha=0.05, nb=1000, seed=42)
print(f"Equivalent: {result['equivalent']}")
print(f"p-value:    {result['p_value']:.4f}")
print(f"Test stat:  {result['test_statistic']:.4f}")
```

**Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data1` | `ndarray (n1, m)` | -- | First group |
| `data2` | `ndarray (n2, m)` | -- | Second group |
| `delta` | `float` | -- | Equivalence margin |
| `alpha` | `float` | `0.05` | Significance level |
| `nb` | `int` | `1000` | Bootstrap replicates |
| `seed` | `int` | `42` | Random seed |

**Returns** a dictionary:

| Key | Type | Description |
|---|---|---|
| `equivalent` | `bool` | `True` if equivalence is established at level $\alpha$ |
| `p_value` | `float` | Bootstrap p-value |
| `test_statistic` | `float` | Observed test statistic |

---

## Full example -- comparing all three band methods

```python
import numpy as np
from fdars import Fdata
from fdars.simulation import simulate
from fdars.tolerance import (
    fpca_tolerance_band,
    conformal_prediction_band,
    scb_mean_degras,
)

# ── Data ──────────────────────────────────────────────────────
argvals = np.linspace(0, 1, 100)
fd = Fdata(simulate(80, argvals, n_basis=5, seed=7), argvals=argvals)

# ── Bands ─────────────────────────────────────────────────────
tol_fpca = fpca_tolerance_band(fd.data, ncomp=3, nb=2000, coverage=0.95, seed=1)
tol_conf = conformal_prediction_band(fd.data, coverage=0.95, cal_fraction=0.25, seed=1)
scb      = scb_mean_degras(fd.data, fd.argvals, bandwidth=0.0, nb=2000, confidence=0.95)

# ── Visualize (optional) ─────────────────────────────────────
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    titles = ["FPCA tolerance", "Conformal prediction", "Degras SCB (mean)"]
    bands  = [tol_fpca, tol_conf, scb]

    for ax, title, b in zip(axes, titles, bands):
        ax.plot(fd.argvals, fd.data.T, color="0.85", linewidth=0.5)
        ax.fill_between(fd.argvals, b["lower"], b["upper"], alpha=0.25, label="band")
        ax.plot(fd.argvals, b["center"], "k-", linewidth=1.5, label="center")
        ax.set_title(title)
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig("tolerance_bands.png", dpi=150)
    plt.show()
except ImportError:
    pass
```
