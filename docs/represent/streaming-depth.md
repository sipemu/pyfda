# Streaming Depth Computation

Functional [depth](depth-functions.md) is a batch computation: you hand it a fixed sample and it scores every curve against that sample. But many applications produce curves *over time* -- sensor traces, daily load profiles, per-request latency curves -- and you want to know, as each new curve arrives, whether it looks like the recent past or has drifted out of distribution. This page describes a **streaming pattern** built on the existing batch depth primitives: keep a rolling *reference window* of recent curves, and score each incoming curve's depth against that window. A sudden drop in depth flags an anomaly.

!!! warning "No streaming binding in fdars"
    `fdars` has **no** streaming-specific depth function. Every depth routine in `fdars.depth` is batch. What follows is a **usage pattern** implemented in numpy on top of those batch primitives -- specifically by calling `modified_band_1d(new_batch, reference_window)`, which is exactly what the `data` / `ref_data` split is designed for.

## The key idea: `data` vs `ref_data`

Every `fdars.depth` function takes two arguments: the curves to *score* (`data`) and the reference sample to score *against* (`ref_data`). In the batch setting these are usually the same array (self-depth). Streaming simply keeps them **different**:

```python
from fdars.depth import modified_band_1d

# score the newly arrived curve(s) against the reference window
depth = modified_band_1d(new_curves, reference_window)
```

| Argument | Streaming role |
|----------|----------------|
| `data` | The just-arrived curve(s) to score |
| `ref_data` | The rolling window of recent "normal" curves |

Low depth means the new curve sits at the edge of, or outside, the distribution described by the window.

## The streaming loop

The pattern is a loop with three moves per arriving curve:

1. **Score** the new curve against the current window.
2. **Decide** whether it is anomalous by comparing its depth to a threshold derived from the window's own depth distribution.
3. **Update** the window -- append the new curve and drop the oldest, so the reference tracks slow, legitimate drift. Crucially, curves flagged as anomalies are **not** folded in, otherwise the window would be contaminated and future anomalies would look normal.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.depth import modified_band_1d

t = np.linspace(0, 1, 80)

def new_curve(seed, shift=0.0):
    """One incoming curve; `shift` injects an out-of-distribution anomaly."""
    return np.asarray(
        simulate(n=1, argvals=t, n_basis=5, efun_type="fourier", seed=seed)
    ) + shift

# Seed the reference window with recent-history curves.
window = np.asarray(
    simulate(n=25, argvals=t, n_basis=5, efun_type="fourier", seed=1))
MAX_WINDOW = 25

depths, flags = [], []
for step in range(60):
    shift = 4.0 if 30 <= step < 34 else 0.0        # anomaly burst
    x = new_curve(200 + step, shift)

    # 1. score the new curve against the window
    d = float(np.asarray(modified_band_1d(x, window))[0])
    depths.append(d)

    # 2. threshold = low quantile of the window's own self-depth
    self_depth = np.asarray(modified_band_1d(window, window))
    threshold = np.quantile(self_depth, 0.05)
    is_anomaly = d < threshold
    flags.append(is_anomaly)

    # 3. update the window only with in-distribution curves
    if not is_anomaly:
        window = np.vstack([window, x])[-MAX_WINDOW:]

depths = np.asarray(depths)
flags = np.asarray(flags)

f, ax = fig()
ax.plot(depths, "-", color="#3f51b5", lw=1.6, label="streaming depth")
ax.scatter(np.where(flags)[0], depths[flags],
           color="#dc3545", zorder=5, s=40, label="flagged anomaly")
ax.axvspan(30, 34, color="#e8710a", alpha=0.15, label="injected anomaly")
ax.set(title="Depth over time drops sharply during the anomaly burst",
       xlabel="arrival index", ylabel="depth vs reference window")
ax.legend()
print(render(f))
```

The depth trace hovers in a normal band, then collapses during the injected burst; the low-quantile threshold catches every anomalous arrival while the window stays uncontaminated.

## Choosing the threshold

Two simple, robust rules work well:

- **Quantile of window self-depth** (used above): compute `modified_band_1d(window, window)` and flag any new curve below, say, the 5th percentile. This adapts automatically as the window's spread changes.
- **Depth boxplot rule**: with $q_1$ and $\mathrm{IQR}$ the first quartile and interquartile range of the window's self-depth, flag curves below $q_1 - 1.5\,\mathrm{IQR}$ -- the same rule the [functional boxplot](../analyze/outlier-detection.md) uses.

$$
\text{flag if} \quad D(x \mid W) < q_{1} - 1.5\,\mathrm{IQR}\bigl(D(W \mid W)\bigr)
$$

Recomputing the window self-depth every step is $O(\lvert W\rvert^2 m)$; for a modest window (a few dozen curves) this is negligible, which is what makes the pattern practical online.

## Window size and drift

The window length trades responsiveness against stability.

| Window | Behavior |
|--------|----------|
| Short (10--20) | Tracks drift quickly; noisier thresholds, more false alarms |
| Long (50--100) | Stable thresholds; slower to accept legitimate regime changes |

Because the loop refreshes the window with accepted curves, slow legitimate drift is absorbed -- a curve that would have been anomalous against last month's window becomes normal once the window has migrated. Sudden shifts still spike because the window has not yet caught up. The panel below contrasts a short and a long window on the same stream with a permanent regime change at step 30.

```python exec="1" html="1"
import numpy as np
from docs_fig import fig, render
from fdars.simulation import simulate
from fdars.depth import modified_band_1d

t = np.linspace(0, 1, 80)

def new_curve(seed, shift=0.0):
    return np.asarray(
        simulate(n=1, argvals=t, n_basis=5, efun_type="fourier", seed=seed)) + shift

def run_stream(max_window):
    window = np.asarray(
        simulate(n=max_window, argvals=t, n_basis=5, efun_type="fourier", seed=1))
    depths = []
    for step in range(60):
        shift = 2.5 if step >= 30 else 0.0          # permanent regime change
        x = new_curve(300 + step, shift)
        d = float(np.asarray(modified_band_1d(x, window))[0])
        depths.append(d)
        window = np.vstack([window, x])[-max_window:]  # absorb everything
    return np.asarray(depths)

short = run_stream(12)
long = run_stream(60)

f, ax = fig()
ax.plot(short, color="#e8710a", lw=1.6, label="short window (12)")
ax.plot(long, color="#3f51b5", lw=1.6, label="long window (60)")
ax.axvline(30, ls="--", color="#6c757d", lw=1, label="regime change")
ax.set(title="Short windows re-normalize faster after a permanent shift",
       xlabel="arrival index", ylabel="depth vs reference window")
ax.legend()
print(render(f))
```

The short window's depth recovers quickly as it fills with post-shift curves; the long window stays depressed far longer because it still remembers the old regime.

## Process monitoring: a depth control chart

The same pattern powers a functional statistical-process-control (SPC) chart. In **phase 1** you establish a reference from an in-control process and set a control limit from a low quantile of the reference self-depth. In **phase 2** you score each incoming curve against that fixed reference and raise an alarm whenever its depth falls below the limit. Unlike a univariate control chart, this monitors the *entire curve shape* at once.

```python exec="1" html="1" source="above"
import numpy as np
from docs_fig import fig, render
from fdars.depth import modified_band_1d

rng = np.random.default_rng(42)
t = np.linspace(0, 1, 100)
m = t.size

def in_control(k):
    return np.sin(2 * np.pi * t) + rng.normal(0, 0.2) + 0.05 * rng.standard_normal(m)

# Phase 1: reference from an in-control process; control limit = 2nd percentile.
ref = np.array([in_control(i) for i in range(60)])
d_ref = np.asarray(modified_band_1d(ref, ref))
control_limit = np.quantile(d_ref, 0.02)

# Phase 2: monitor 50 curves; the process mean shifts up at curve 35.
n_new, shift_point = 50, 35
depths = []
for i in range(n_new):
    x = in_control(i)
    if i >= shift_point:
        x = x + 0.8                                   # out-of-control shift
    depths.append(float(np.asarray(modified_band_1d(x[None, :], ref))[0]))
depths = np.asarray(depths)
alarm = depths < control_limit

f, ax = fig()
ax.plot(depths, color="#6c757d", lw=0.8, zorder=1)
ax.scatter(np.where(~alarm)[0], depths[~alarm], color="#3f51b5", s=22,
           label="in control")
ax.scatter(np.where(alarm)[0], depths[alarm], color="#dc3545", s=36,
           zorder=5, label="alarm")
ax.axhline(control_limit, ls="--", color="#dc3545", lw=1, label="control limit")
ax.axvline(shift_point - 0.5, ls=":", color="#6c757d", lw=1, label="true shift")
ax.set(title="Streaming-depth control chart (shift at curve 35)",
       xlabel="curve index", ylabel="depth vs reference")
ax.legend(fontsize=8)
print(render(f))
```

Depth stays comfortably above the limit while the process is in control, then drops below it once the mean shifts, generating a run of alarms. The same $q_1 - 1.5\,\mathrm{IQR}$ rule from the [functional boxplot](../analyze/outlier-detection.md) can replace the fixed quantile for the control limit.

## Swapping the depth measure

Any 1D depth from `fdars.depth` slots into the loop -- just replace the call. `fraiman_muniz_1d` is a common alternative that is sensitive to magnitude shifts:

```python
from fdars.depth import fraiman_muniz_1d

d = fraiman_muniz_1d(new_curves, reference_window)   # same data / ref_data split
```

For shape anomalies rather than magnitude, `random_tukey_1d` or `modal_1d` are better choices; see the [depth comparison table](depth-functions.md#comparison-table).

!!! note "This is a pattern, not a primitive"
    Nothing here is special to `fdars` beyond the batch depth call. If you need genuine online efficiency (incremental band-depth updates, sketched references), you would implement that yourself; the value of the pattern is that a handful of numpy lines around a batch depth function already gives a usable out-of-distribution detector.

## API summary

| Component | Where | Role in the pattern |
|-----------|-------|---------------------|
| `modified_band_1d(data, ref_data)` | `fdars.depth` | Score new curves vs the window |
| `fraiman_muniz_1d(data, ref_data, scale)` | `fdars.depth` | Magnitude-sensitive alternative |
| rolling window + threshold | numpy (this page) | The streaming loop itself |
| `simulate(...)` | `fdars.simulation` | Generates the example stream |

## References

- Fraiman, R. and Muniz, G. (2001). Trimmed means for functional data. *Test* 10(2), 419-440.
- López-Pintado, S. and Romo, J. (2009). On the concept of depth for functional data. *JASA* 104(486), 718-734.
