# Elastic Time-Series Distances

Beyond plain DTW, the time-series literature has produced a family of *elastic* distances. Each allows the time axis to stretch, but they differ in how they price a stretch, a gap or a mismatch. `fdars.metric` implements the family as found in **aeon 1.6** (derivative, weighted and amerced DTW, ERP, EDR, TWE, MSM, LCSS and shape-DTW), golden-tested against aeon to $10^{-10}$, plus the **shape-based distance** (SBD) of k-Shape.

For the DTW toolkit itself (windows, lower bounds, nearest-neighbour search, barycenters) see [DTW Search & Averaging](dtw-toolkit.md). For the elastic **SRSF** distances, which factor out warping by alignment rather than by a dynamic-programming edit cost, see [Distance Metrics](distance-metrics.md#elastic-distances).

## One interface for ten distances

Four dispatchers cover the family; `metric=` selects the distance:

| Function | Returns |
|---|---|
| `elastic_ts_distance(x, y, metric, ...)` | float |
| `elastic_ts_pairwise_distance(data, metric, other=None, ...)` | `(n, n)` self matrix, or `(n, n_other)` with `other` |
| `elastic_ts_cost_matrix(x, y, metric, ...)` | aeon's accumulated cost matrix |
| `elastic_ts_alignment_path(x, y, metric, ...)` | `{"path": int64 (L, 2), "distance": float}` |

Each has a `_multivariate` twin taking `(d, m)` series (channels as rows); see [Multichannel series](#multichannel-series). All accept the global window keywords of the DTW toolkit (`window=`, `radius=`, `window_fraction=`, `max_slope=`). aeon's `window=<fraction>` is `window="sakoe_chiba_fraction", window_fraction=<fraction>`, and its `itakura_max_slope=<fraction>` is `window="itakura_fraction", max_slope=<fraction>`. Parameters that the chosen metric does not use are ignored.

| `metric=` | Distance | Local cost and moves | Parameters (aeon defaults) | Returned value |
|---|---|---|---|---|
| `"ddtw"` | Derivative DTW (Keogh & Pazzani 2001) | DTW on the average-of-slopes derivative (length $n-2$) | — | accumulated cost |
| `"wdtw"` | Weighted DTW (Jeong et al. 2011) | squared cost × logistic weight of $\lvert i-j\rvert$ | `g=0.05` (steepness) | accumulated cost |
| `"wddtw"` | Weighted derivative DTW | WDTW on the derivative | `g=0.05` | accumulated cost |
| `"adtw"` | Amerced DTW (Herrmann & Webb 2023) | squared cost + `warp_penalty` per non-diagonal step | `warp_penalty=1.0` | accumulated cost |
| `"erp"` | Edit distance with real penalty (Chen & Ng 2004) | absolute cost; a gap costs $\lvert x - g\rvert$ | `g=0.0` (gap value) | accumulated cost |
| `"edr"` | Edit distance on real sequences (Chen et al. 2005) | 0 if $\lvert x-y\rvert \le \varepsilon$, else 1 | `epsilon=None` → $\max(\mathrm{sd}\,x, \mathrm{sd}\,y)/4$ | edits / $\max(n, m)$ |
| `"twe"` | Time warp edit distance (Marteau 2009) | absolute cost + stiffness on time gaps + edit penalty | `nu=0.001`, `lmbda=1.0` | accumulated cost |
| `"msm"` | Move-split-merge (Stefan et al. 2013) | absolute moves; split/merge cost `c` | `c=1.0`, `independent=True` | accumulated cost |
| `"lcss"` | Longest common subsequence (Vlachos et al. 2002) | match if $\lvert x-y\rvert \le \varepsilon$ | `epsilon=1.0` | $1 - \mathrm{LCSS}/\min(n, m)$ |
| `"shape_dtw"` | Shape DTW (Zhao & Itti 2018) | DTW on subsequence shape descriptors | `descriptor="identity"`, `reach=15` | raw squared cost along the descriptor alignment |

Notes on the less obvious parameters:

- **WDTW** weights the cost of matching $x_i$ to $y_j$ by $1/(1 + e^{-g(\lvert i-j\rvert - \max(n,m)/2)})$, so off-diagonal matches cost more. A large `g` makes the weight close to a step at $\lvert i - j\rvert = \max(n, m)/2$; `g=0` gives a constant weight of one half, i.e. half the DTW cost.
- **ADTW** adds a fixed penalty for every horizontal or vertical step. `warp_penalty=0` is plain DTW; a very large penalty forbids warping and approaches the squared Euclidean distance.
- **EDR** and **LCSS** threshold the pointwise difference, so a single extreme value counts as at most one edit. Their `epsilon` is in data units. `epsilon=1.0` (aeon's LCSS default) is wide for data of unit amplitude; set it from the noise level.
- **MSM** with `independent=False` uses squared rather than absolute costs (for univariate input). For multichannel input it switches between summing per-channel MSM costs (`True`) and a vector split/merge cost (`False`).
- **Shape-DTW** describes each time point by the length-$(2\,\mathrm{reach}+1)$ subsequence around it, mapped through `descriptor`: `"identity"` (the raw subsequence, aeon's only descriptor), or sktime's `"paa"` (piecewise aggregate approximation, `descriptor_param` intervals, default 8), `"dwt"` (wavelet levels, default 3), `"slope"` (default 8 intervals) and `"derivative"`. DTW aligns the descriptor sequences, and the distance is the squared cost of the *raw* samples along that alignment. Non-injective descriptors can give $d(x, x) > 0$.

Cost-matrix shapes follow aeon: `(n, m)` in general, `(n-2, m-2)` for `ddtw`/`wddtw` (derivative coordinates), and the padded `(n+1, m+1)` table for `lcss`. Out-of-window cells hold aeon's fill value (`inf`, or 0 for LCSS). LCSS paths contain only the matched pairs and may be empty.

## What each distance responds to

The heatmap compares a sine with five perturbed copies. Each row is scaled by that metric's largest value, so read it across a row: it shows which perturbation the metric treats as large, not how metrics compare with each other.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
import fdars.metric as fm

rng = np.random.default_rng(2)
t = np.linspace(0, 1, 60)
x = np.sin(2 * np.pi * t)
probes = {
    "time shift": np.sin(2 * np.pi * (t - 0.08)),
    "local warp": np.sin(2 * np.pi * t ** 1.4),
    "amplitude x1.5": 1.5 * x,
    "noise": x + 0.3 * rng.standard_normal(60),
    "spike": x + 4.0 * (np.abs(t - 0.5) < 0.01),
}
metrics = ["dtw", "ddtw", "wdtw", "adtw", "erp", "edr", "twe", "msm", "lcss", "sbd"]
rows = []
for met in metrics:
    if met == "dtw":
        d = [fm.dtw_distance_windowed(x, y) for y in probes.values()]
    elif met == "sbd":
        d = [fm.sbd(x, y)["distance"] for y in probes.values()]
    else:
        d = [fm.elastic_ts_distance(x, y, met) for y in probes.values()]
    rows.append(np.asarray(d) / max(d))
R = np.array(rows)

f, ax = fig(figsize=(7.5, 4.6))
im = ax.imshow(R, cmap="viridis", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(probes)), list(probes), rotation=20)
ax.set_yticks(range(len(metrics)), metrics)
ax.grid(False)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        ax.text(j, i, f"{R[i, j]:.2f}", ha="center", va="center", fontsize=8,
                color="white" if R[i, j] < 0.6 else "black")
ax.set_title("Distance to a sine, scaled by each metric's largest value")
f.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
print(render(f))
print("FDARS_FENCE_OK")
```

The distances fall into three groups.

- **Squared-cost DTW variants** (`dtw`, `wdtw`, `adtw`, `ddtw`) absorb the shift and the warp almost completely, and a single spike dominates them because its cost is squared. ADTW is the least warp-tolerant of the group, because every non-diagonal step pays `warp_penalty`.
- **Edit distances** (`erp`, `edr`, `twe`, `msm`) use absolute costs or 0/1 matches, so the spike counts for much less. They react most to the amplitude change and the noise, which affect every sample. EDR barely notices the spike: one sample outside $\varepsilon$ is one edit.
- **LCSS** with the default `epsilon=1.0` sees *only* the spike: every other perturbation stays within one unit of the sine and counts as a match. **SBD** is blind to the amplitude change by construction (see below).

## Shape-based distance (SBD)

SBD (Paparrizos & Gravano 2015) z-normalises both series, slides one over the other and keeps the lag $w$ with the largest normalised cross-correlation. The cross-correlation is zero-padded and computed with the FFT in $O(m \log m)$:

$$
\mathrm{SBD}(x, y) = 1 - \max_{w}\, \frac{\mathrm{CC}_w(x, y)}{\lVert x\rVert\,\lVert y\rVert} \in [0, 2].
$$

The z-normalisation makes SBD exactly invariant to **offset and positive scaling**. A **shift** is absorbed by the lag search, at the price of the samples that slide past the end, so a shifted copy is close but not at distance 0. SBD does not tolerate *local* warping beyond what one global lag explains. `sbd(x, y)` returns `{"distance", "shift"}`, where `shift` is the signed lag; `sbd_distance_matrix(data)` gives the symmetric `(n, n)` matrix. SBD is the distance behind [k-Shape clustering](../analyze/time-series-clustering.md#k-shape).

```python exec="1" source="above" result="text"
import numpy as np
from fdars.metric import sbd, sbd_distance_matrix

t = np.linspace(0, 1, 60, endpoint=False)
x = np.sin(2 * np.pi * t)
shifted = np.roll(x, 5)                   # circular shift by 5 samples
rescaled = 3.0 * x + 2.0                  # different gain and offset
flipped = -x                              # negative scaling is NOT ignored

for name, y in [("shifted", shifted), ("rescaled", rescaled), ("flipped", flipped)]:
    r = sbd(x, y)
    print(f"{name:9s} distance={r['distance']:.4f}  shift={r['shift']}")
D = sbd_distance_matrix(np.vstack([x, shifted, rescaled, flipped]))
print("matrix diagonal:", np.diag(D).round(6))
print("FDARS_FENCE_OK")
```

The rescaled copy is at distance 0. The copy shifted by 5 samples is at distance 0.02 (the 5 samples that slide past the end no longer overlap), and `shift` recovers the lag as $-5$. Flipping the sign is not a positive scaling: $-\sin$ is half a period away from $\sin$, so the best lag is 30 samples, where only half of each series overlaps, giving distance 0.5.

## Multichannel series

The `_multivariate` twins (`elastic_ts_distance_multivariate`, `elastic_ts_pairwise_distance_multivariate`, `elastic_ts_cost_matrix_multivariate`, `elastic_ts_alignment_path_multivariate`) take each series as a `(d, m)` array with channels as rows; collections are a list of `(d, m_i)` arrays or an `(n, d, m)` array. They reproduce aeon's multichannel semantics:

- pointwise costs are **dependent**: the squared Euclidean distance across channels, or its root for ERP, EDR, TWE and LCSS;
- `ddtw`/`wddtw` differentiate every channel;
- `msm` with `independent=True` sums the per-channel MSM costs.

With $d = 1$ the results are bit-identical to the univariate functions.

```python exec="1" source="above" result="text"
import numpy as np
import fdars.metric as fm

t = np.linspace(0, 1, 60)
x = np.vstack([np.sin(2 * np.pi * t), np.cos(2 * np.pi * t)])               # (2, 60)
y = np.vstack([np.sin(2 * np.pi * (t - 0.08)), np.cos(2 * np.pi * (t - 0.08))])
for met in ("erp", "twe", "msm"):
    d2 = fm.elastic_ts_distance_multivariate(x, y, met)
    d1 = fm.elastic_ts_distance_multivariate(x[:1], y[:1], met)
    same = d1 == fm.elastic_ts_distance(x[0], y[0], met)
    print(f"{met}: 2-channel {d2:.4f}   channel 0 alone {d1:.4f}   (= univariate: {same})")
print("FDARS_FENCE_OK")
```

## Choosing a distance

| Situation | Suggested distance |
|---|---|
| Timing varies, amplitudes comparable, no outliers | `dtw` with a window ([DTW Search & Averaging](dtw-toolkit.md)) |
| Curves differ by an offset you want to ignore | `ddtw` / `wddtw` (they compare slopes) |
| Warping should be possible but discouraged | `wdtw` (penalise far-off-diagonal matches) or `adtw` (penalise every warping step) |
| Occasional spikes or dropouts | `edr`, `lcss` (thresholded), `erp`, `twe`, `msm` (absolute costs) |
| A true metric is needed (triangle inequality) | `erp`, `twe`, `msm` |
| Shape matters, gain/offset/phase shift do not | `sbd` |
| Local shape context should drive the alignment | `shape_dtw` with a `"paa"` or `"slope"` descriptor |

The distance matrices feed straight into `alignment.kmedoids_from_distances`, DBSCAN and the kernel and k-NN tools; see [Time-Series Clustering](../analyze/time-series-clustering.md) for clusterers built on SBD and DTW.

## References

1. Keogh, E. & Pazzani, M. (2001). Derivative dynamic time warping. *Proceedings of the 2001 SIAM International Conference on Data Mining (SDM)*.
2. Jeong, Y.-S., Jeong, M. K. & Omitaomu, O. A. (2011). Weighted dynamic time warping for time series classification. *Pattern Recognition*, 44(9), 2231–2240.
3. Herrmann, M. & Webb, G. I. (2023). Amercing: an intuitive and effective constraint for dynamic time warping. *Pattern Recognition*, 137, 109333.
4. Chen, L. & Ng, R. (2004). On the marriage of Lp-norms and edit distance. *Proceedings of the 30th International Conference on Very Large Data Bases (VLDB)*, 792–803.
5. Chen, L., Özsu, M. T. & Oria, V. (2005). Robust and fast similarity search for moving object trajectories. *Proceedings of the 2005 ACM SIGMOD International Conference on Management of Data*, 491–502.
6. Marteau, P.-F. (2009). Time warp edit distance with stiffness adjustment for time series matching. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 31(2), 306–318.
7. Stefan, A., Athitsos, V. & Das, G. (2013). The move-split-merge metric for time series. *IEEE Transactions on Knowledge and Data Engineering*, 25(6), 1425–1438.
8. Vlachos, M., Kollios, G. & Gunopulos, D. (2002). Discovering similar multidimensional trajectories. *Proceedings of the 18th International Conference on Data Engineering (ICDE)*, 673–684.
9. Zhao, J. & Itti, L. (2018). shapeDTW: shape dynamic time warping. *Pattern Recognition*, 74, 171–184.
10. Paparrizos, J. & Gravano, L. (2015). k-Shape: efficient and accurate clustering of time series. *Proceedings of the 2015 ACM SIGMOD International Conference on Management of Data*, 1855–1870.
