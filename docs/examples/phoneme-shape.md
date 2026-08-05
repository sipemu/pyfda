# Phoneme recognition: shape-based sound classification

**Dataset:** Phoneme — 400 log-periodograms (256 frequencies each) of spoken
sounds, 80 examples of each of five phonemes: **aa** (as in *dark*), **ao** (as
in *water*), **dcl** (the *d* closure), **iy** (as in *she*), and **sh** (as in
*she*). The label is the phoneme; the curve is the sound's frequency spectrum.

Each observation is a spectrum — energy across 256 frequency bins. The
information that distinguishes an *iy* from an *sh* lives in the **shape** of the
spectrum (where the energy concentrates), not in any single frequency. That makes
this a textbook **functional classification** problem: the periodograms are
noisy, so we first smooth them into clean curves, then classify by shape and
measure honest cross-validated accuracy. All 400 curves are used — no
subsampling.

## Raw periodograms are noisy

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()

f, ax = fig()
for cls, c in zip(["iy", "sh"], ["#3f51b5", "#e8710a"]):
    ax.plot(freq, X[ph == cls][:6].T, color=c, lw=0.7, alpha=0.5)
    ax.plot([], [], color=c, label=cls)
ax.set(title="Raw log-periodograms (6 curves each) — noisy",
       xlabel="frequency bin", ylabel="log-periodogram")
ax.legend()
print(render(f))
```

The raw curves are jagged: adjacent frequency bins jitter wildly even though the
underlying spectral envelope is smooth. Feeding these directly to a classifier
wastes effort modelling noise. The functional-data move is to **smooth** first —
treat each periodogram as a rough sample of an underlying smooth spectral curve.

## Smoothing with a penalised spline

We fit each curve with a penalised B-spline
(`fdars.basis.pspline_fit_1d`), which trades data fidelity against a roughness
penalty `lambda_`. The returned `fitted` array is the smoothed curve matrix.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme
from fdars.basis import pspline_fit_1d

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()
Xs = np.asarray(pspline_fit_1d(X, freq, n_basis=20, lambda_=1.0)["fitted"])

i = np.where(ph == "sh")[0][0]
f, ax = fig()
ax.plot(freq, X[i], color="#adb5bd", lw=0.9, label="raw")
ax.plot(freq, Xs[i], color="#dc3545", lw=2.4, label="P-spline smooth")
ax.set(title="One 'sh' periodogram: raw vs smoothed",
       xlabel="frequency bin", ylabel="log-periodogram")
ax.legend()
print(render(f))
```

The penalised spline keeps the broad spectral envelope — the peaks and valleys
that identify the phoneme — while discarding bin-to-bin noise. Every curve from
here on is a smoothed spectrum.

## Class-mean spectra

The five phonemes have visibly different spectral **shapes** — this is what makes
shape-based classification work.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme
from fdars.basis import pspline_fit_1d

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()
Xs = np.asarray(pspline_fit_1d(X, freq, n_basis=20, lambda_=1.0)["fitted"])

palette = {"aa": "#3f51b5", "ao": "#e8710a", "dcl": "#198754",
           "iy": "#dc3545", "sh": "#6f42c1"}
f, ax = fig()
for cls, c in palette.items():
    ax.plot(freq, Xs[ph == cls].mean(0), color=c, lw=2.4, label=cls)
ax.set(title="Mean spectrum per phoneme",
       xlabel="frequency bin", ylabel="log-periodogram")
ax.legend(ncol=3)
print(render(f))
```

The nasal-closure **dcl** sits low across the board; **iy** and **sh** carry
energy into the high bins where the vowels **aa** and **ao** have dropped off.
The two back vowels **aa** and **ao** are the closest pair — and, as the
confusion matrix below confirms, the ones the classifier most often mixes up.

## Classifying by shape

`fdars.classification` offers several functional classifiers. Each first
projects the smoothed curves onto their leading functional principal components
(`ncomp`), then classifies in that low-dimensional score space. We evaluate them
honestly with `fclassif_cv` (5-fold cross-validation), which reports an
`error_rate` rather than the optimistic resubstitution accuracy.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme
from fdars.basis import pspline_fit_1d
from fdars.classification import fclassif_cv

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()
classes = sorted(set(ph))
y = np.array([classes.index(p) for p in ph], dtype=np.int64)
Xs = np.asarray(pspline_fit_1d(X, freq, n_basis=20, lambda_=1.0)["fitted"])

methods = ["lda", "qda", "knn"]
acc = [1.0 - float(fclassif_cv(Xs, freq, y, method=m, ncomp=8, nfold=5)["error_rate"])
       for m in methods]

f, ax = fig()
ax.bar(methods, acc, color=["#3f51b5", "#e8710a", "#198754"], width=0.6)
for i, a in enumerate(acc):
    ax.text(i, a + 0.005, f"{a:.0%}", ha="center", fontsize=11)
ax.axhline(0.2, color="#6c757d", ls="--", lw=1, label="chance (5 classes)")
ax.set(title="5-fold CV accuracy by classifier (ncomp=8)",
       xlabel="method", ylabel="accuracy", ylim=(0, 1))
ax.legend()
print(render(f))
```

All three classifiers land near **90%** on a five-way problem where chance is
20% — the smoothed spectral shape is highly discriminative. **LDA** (linear
discriminant analysis on 8 FPCA scores) edges out the others: with only eight
numbers per curve it separates the five phonemes almost perfectly.

## Where do the errors go?

A confusion matrix shows *which* phonemes get mixed up. We build it from
out-of-fold predictions so it reflects genuine generalisation, not memorisation.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from docs_data import load_phoneme
from fdars.basis import pspline_fit_1d
from fdars.classification import fclassif_lda

freq, X, meta = load_phoneme()
ph = meta["phoneme"].to_numpy()
classes = sorted(set(ph))
y = np.array([classes.index(p) for p in ph], dtype=np.int64)
Xs = np.asarray(pspline_fit_1d(X, freq, n_basis=20, lambda_=1.0)["fitted"])

# out-of-fold predictions: train LDA on 4 folds, predict the 5th
rng = np.random.default_rng(0)
idx = rng.permutation(len(y))
pred = np.empty_like(y)
for fold in range(5):
    te = idx[fold::5]
    tr = np.setdiff1d(idx, te)
    # fit on train, then classify train+test together and read test rows
    both = np.vstack([Xs[tr], Xs[te]])
    res = fclassif_lda(both, np.concatenate([y[tr], y[te]]), ncomp=8)
    pred[te] = np.asarray(res["predicted"])[len(tr):]

K = len(classes)
cm = np.zeros((K, K), int)
for t_, p_ in zip(y, pred):
    cm[t_, p_] += 1

f, ax = fig(figsize=(5.2, 4.4))
im = ax.imshow(cm, cmap="Blues", aspect="auto")
ax.set_xticks(range(K)); ax.set_xticklabels(classes)
ax.set_yticks(range(K)); ax.set_yticklabels(classes)
for i in range(K):
    for j in range(K):
        ax.text(j, i, cm[i, j], ha="center", va="center",
                color="#222" if cm[i, j] < cm.max() * 0.6 else "white")
ax.set(title="Confusion matrix (out-of-fold LDA)",
       xlabel="predicted", ylabel="true phoneme")
ax.grid(False)
print(render(f))
```

The diagonal dominates — most predictions are correct. The largest off-diagonal
cell is the **aa ↔ ao** confusion the class-mean plot foreshadowed: two back
vowels with nearly parallel spectra. Everything else (**dcl**, **iy**, **sh**) is
recognised almost flawlessly.

!!! note "Smoothing is not cosmetic"
    Smoothing before classification is not just for prettier plots. The FPCA step
    inside each classifier is sensitive to high-frequency noise; smoothing
    concentrates the leading components on the spectral *envelope*, which is where
    the phoneme identity lives. Try lowering `n_basis` or raising `lambda_` to see
    accuracy trade off against how much detail survives.

## Parameters

| Function | Key parameters | Description |
|----------|----------------|-------------|
| `pspline_fit_1d(data, argvals, n_basis, lambda_, order)` | `n_basis`, `lambda_` | Penalised-spline smoothing; `fitted` is the smoothed matrix |
| `fclassif_cv(data, argvals, labels, method, ncomp, nfold)` | `method`, `ncomp`, `nfold` | Cross-validated `error_rate` for `lda`/`qda`/`knn` |
| `fclassif_lda(data, labels, ncomp)` | `ncomp` | LDA on `ncomp` FPCA scores; returns `predicted`, `accuracy` |
| `fclassif_knn(data, labels, ncomp, k)` | `k` | k-NN in FPCA score space |

## See also

- [Classification](../regression/classification.md) for LDA/QDA/k-NN and
  depth-based classifiers in general.
- [Basis smoothing](../represent/basis-representation.md) for penalised splines
  and choosing `n_basis`/`lambda_`.
- [Cross-validation](../regression/cross-validation.md) for honest model
  assessment.
