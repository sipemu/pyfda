# Predicting fat from NIR spectra

**Dataset:** Tecator — near-infrared absorbance spectra (100 channels,
850–1050 nm) of 240 meat samples, each with a lab-measured fat content.

Measuring fat content by wet chemistry is slow and destructive; a near-infrared
(NIR) spectrometer is fast and cheap. Can we predict the fat percentage
*directly from the spectrum*? Each observation here is a whole absorbance
**curve**, and the response is a single number — a textbook **scalar-on-function
regression** problem.

## The spectra, colored by fat

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_tecator

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
order = np.argsort(fat)
norm = (fat - fat.min()) / np.ptp(fat)

import matplotlib.cm as cm
f, ax = fig()
for i in order:
    ax.plot(wl, X[i], color=cm.viridis(norm[i]), lw=0.8, alpha=0.7)
ax.set(title="Tecator spectra, colored by fat content (dark = lean)",
       xlabel="wavelength (nm)", ylabel="absorbance $-\\log_{10}T$")
sm = cm.ScalarMappable(cmap="viridis")
sm.set_array(fat)
f.colorbar(sm, ax=ax, label="fat (%)")
print(render(f))
```

The spectra look almost parallel — the dominant variation is a vertical
*baseline shift*, not shape. The fat signal lives in subtle curvature around the
930–970 nm fat-absorption band, largely hidden under that baseline.

## Working on the second derivative

A standard NIR preprocessing trick removes the baseline by differentiating
twice: a constant or linear offset vanishes under `d²/dλ²`, exposing the
absorption peaks. We do this with `fdars.fdata.deriv_1d`.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_tecator
from fdars.fdata import deriv_1d

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))       # baseline-corrected spectra
norm = (fat - fat.min()) / np.ptp(fat)

import matplotlib.cm as cm
f, ax = fig()
for i in np.argsort(fat):
    ax.plot(wl, D2[i], color=cm.viridis(norm[i]), lw=0.8, alpha=0.7)
ax.set(title="Second derivative separates lean from fatty",
       xlabel="wavelength (nm)", ylabel="$d^2A/d\\lambda^2$")
print(render(f))
```

Now the curves fan out by fat content — the derivative has turned an invisible
signal into a visible one.

## Functional PLS regression

A functional linear model writes the response as an integral against a
**coefficient curve** $\beta(\lambda)$:

$$
\hat y_i \;=\; \alpha \;+\; \int \beta(\lambda)\, x_i(\lambda)\, d\lambda .
$$

Because neighbouring channels are highly collinear, we cannot fit $\beta$
freely. Functional **partial least squares** (`fregre_pls`) projects the curves
onto a few components chosen to covary with the response, then reconstructs a
smooth $\beta(\lambda)$. We hold out 70 samples to measure honest predictive
accuracy.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_tecator
from fdars.fdata import deriv_1d
from fdars.regression import fregre_pls, predict_fregre_pls

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))

rng = np.random.default_rng(0)
idx = rng.permutation(X.shape[0])
tr, te = idx[:170], idx[170:]

n_comp = 5
fit = fregre_pls(D2[tr], wl, fat[tr], n_comp=n_comp)
pred = np.asarray(predict_fregre_pls(D2[tr], wl, fat[tr], D2[te], n_comp=n_comp))
rmse = float(np.sqrt(np.mean((fat[te] - pred) ** 2)))
r2 = 1 - np.sum((fat[te] - pred) ** 2) / np.sum((fat[te] - fat[te].mean()) ** 2)

f, ax = fig(figsize=(5.2, 5.0))
lim = [fat.min() - 2, fat.max() + 2]
ax.plot(lim, lim, color="#6c757d", ls=":", lw=1)
ax.scatter(fat[te], pred, color="#3f51b5", s=28, alpha=0.8, edgecolor="white")
ax.set(title=f"Held-out fit: $R^2$={r2:.3f}, RMSE={rmse:.2f}%",
       xlabel="measured fat (%)", ylabel="predicted fat (%)",
       xlim=lim, ylim=lim)
print(render(f))
```

With 5 PLS components on the second-derivative spectra the model explains about
94% of the held-out fat variance (RMSE ≈ 3.5%). For comparison, the same PLS on
the *raw* (un-differentiated) spectra reaches only $R^2 \approx 0.87$ — the
baseline correction is doing real work.

## The coefficient curve

`fregre_pls` returns `beta_t`, the estimated $\beta(\lambda)$. Reading it tells
us *where in the spectrum* the model looks.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_tecator
from fdars.fdata import deriv_1d
from fdars.regression import fregre_pls

wl, X, meta = load_tecator()
fat = meta["fat"].to_numpy()
D2 = np.asarray(deriv_1d(X, wl, nderiv=2))
fit = fregre_pls(D2, wl, fat, n_comp=5)
beta = np.asarray(fit["beta_t"])

f, ax = fig()
ax.axhline(0, color="#6c757d", lw=0.8)
ax.plot(wl, beta, color="#e8710a", lw=2)
ax.fill_between(wl, 0, beta, color="#e8710a", alpha=0.15)
ax.set(title="Coefficient curve $\\beta(\\lambda)$ — where fat shows up",
       xlabel="wavelength (nm)", ylabel="$\\beta$")
print(render(f))
```

The strongest weights cluster around the 920–970 nm region, consistent with the
known C–H overtone absorption band of fat.

!!! tip "A nonparametric alternative"
    `fregre_np` regresses on a **distance matrix** rather than a coefficient
    curve — build one with `fdars.metric.lp_self_1d(D2, wl, 2.0)` and pass it to
    `fregre_np(dist_matrix, fat)`. It fits the training data very tightly
    (in-sample $R^2 \approx 0.98$) but, being a kernel smoother in curve space,
    needs its own held-out evaluation to compare fairly with PLS.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `deriv_1d(data, argvals, nderiv)` | `nderiv` | Derivative order (2 removes a linear baseline) |
| `fregre_pls(data, argvals, response, n_comp)` | `n_comp` | Number of PLS components |
| `predict_fregre_pls(data, argvals, response, new_data, n_comp)` | `new_data` | Spectra to predict |
| `fregre_np(dist_matrix, response, h)` | `h` | Kernel bandwidth (0 = auto) |

!!! warning "Binding note"
    `fregre_pls` raises a Cholesky error (`matrix is singular or
    near-singular`) once `n_comp` gets large relative to the effective rank of
    these highly collinear spectra (here around `n_comp ≥ 7`). Keep the
    component count modest, or select it by cross-validation.

## See also

- [Scalar-on-function regression](../regression/scalar-on-function.md) for the
  functional linear model in general.
- [Basis representation](../represent/basis-representation.md) for smoothing
  spectra before differentiating.
