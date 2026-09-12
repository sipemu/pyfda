---
phase: 89-case-studies-reproducible-figures
reviewed: 2026-09-09T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - paper/code/casestudy1.py
  - paper/code/casestudy2.py
  - paper/code/casestudy3.py
  - paper/code/casestudy4.py
  - paper/code/gen_figures.py
  - Makefile
  - .github/workflows/paper.yml
  - paper/sections/casestudy1.tex
  - paper/sections/casestudy2.tex
  - paper/sections/casestudy3.tex
  - paper/sections/casestudy4.tex
  - paper/sections/casestudies.tex
findings:
  critical: 2
  warning: 2
  info: 2
  total: 6
status: issues_found
---

# Phase 89: Code Review Report

**Reviewed:** 2026-09-09
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Phase 89 delivered four executed case-study scripts with deterministic committed figures and
corresponding LaTeX narrative sections for an arXiv paper. The pipeline infrastructure
(gen_figures.py, Makefile, paper.yml) is largely correct. The critical problems are
concentrated in Study 1: the smoothing figure plots the wrong curves under each class colour
(a data-ordering assumption that is factually false for this dataset), and the tex narrative
reports a CV accuracy and fold-score vector that conflicts with the script's own REAL OUTPUT
comment. Both defects are visible to any reviewer who reads the compiled PDF. Studies 2, 3,
and 4 are structurally sound with consistent narrative numbers.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Figure cs1_phoneme_smooth.pdf overlays smoothed curves from wrong phoneme classes

**File:** `paper/code/casestudy1.py:107-113`

**Issue:** The code assigns smoothed curves to phoneme classes by block-of-4 row index:
`smooth_start = ci * 4` for `ci` in `[0..4]` (classes `aa`, `ao`, `dcl`, `iy`, `sh`).
This assumes the first 20 rows of the phoneme CSV are laid out in sorted-class blocks of 4.
They are not. The actual label sequence for rows 0-19 in `phoneme.csv` is:
`sh, aa, sh, sh, aa, aa, iy, iy, dcl, sh, ao, aa, ao, aa, sh, dcl, aa, ao, aa, dcl`.

Consequence: every class colour in Figure 1 overlays smoothed curves from the wrong
phonemes:

| ci | Claimed class | Actual labels in rows ci*4 .. ci*4+3 |
|----|---------------|--------------------------------------|
| 0  | aa            | sh, aa, sh, sh                       |
| 1  | ao            | aa, aa, iy, iy                       |
| 2  | dcl           | dcl, sh, ao, aa                      |
| 3  | iy            | ao, aa, sh, dcl                      |
| 4  | sh            | aa, ao, aa, dcl                      |

The paper caption describes these as "smoothed curves per class" — a factually incorrect
claim. A peer reviewer running the script and examining the raw data would detect this.

**Fix:** Select rows for smoothing by class membership rather than by positional block.
Replace the `smooth_start` / `smooth_end` block approach with per-class index selection:

```python
# Build per-class index lists from the FULL 400-obs label list
class_rows = {cls: [j for j, l in enumerate(labels_str) if l == cls] for cls in uniq}

# Smooth 4 observations per class (first 4 in the sorted CSV order)
import itertools
selected = list(itertools.chain.from_iterable(class_rows[cls][:4] for cls in uniq))
sm = fdars.basis.smooth_basis_gcv(X[selected], ARG, n_basis=15, basis_type="bspline")

# In the plotting loop, map ci -> rows 0-3 of sm["fitted"] (now correct)
for ci, (cls, col) in enumerate(zip(uniq, colors)):
    for row in range(ci * 4, ci * 4 + 4):
        label = cls if row == ci * 4 else None
        ax1.plot(ARG, sm["fitted"][row], color=col, linewidth=1.4, label=label)
```

---

### CR-02: casestudy1.tex reports a CV accuracy and fold-score vector that conflicts with casestudy1.py

**File:** `paper/sections/casestudy1.tex:39-41` and `paper/sections/casestudy1.tex:63-65`

**Issue:** The LaTeX narrative states:

> "The pipeline achieves a mean CV accuracy of **86.3%** on held-out data
> (fold scores: $[0.850, 0.850, 0.862, 0.875, 0.875]$)"

and the figure caption reads:

> "consistent with the **86.3%** 5-fold CV classification accuracy"

However, `casestudy1.py` line 83 carries the comment:

```python
# REAL OUTPUT: [0.900, 0.875, 0.813, 0.938, 0.888]  mean: 0.882
```

and `acc` (which is live-computed and embedded in the figure title) would therefore render
as **88.2%** in the actual PDF figure. A reader opening the compiled paper sees 86.3% in
the body text and caption, but ~88.2% in the figure title — a direct contradiction within a
single page. The fold vectors are also entirely different (none of the five fold values
match).

One of these results is stale or fabricated. The tex appears to carry numbers from a
previous experimental run that was later superseded.

**Fix:** Reconcile by running the script and updating the tex to match the live output.
If the script's REAL OUTPUT comment is correct, the tex changes are:

```latex
% casestudy1.tex line 39-40 — replace:
The pipeline achieves a mean CV accuracy of 86.3\% on held-out data
(fold scores: $[0.850, 0.850, 0.862, 0.875, 0.875]$)
% with:
The pipeline achieves a mean CV accuracy of 88.2\% on held-out data
(fold scores: $[0.900, 0.875, 0.813, 0.938, 0.888]$)

% casestudy1.tex lines 63-65 — replace:
consistent with the 86.3\% 5-fold CV classification accuracy
% with:
consistent with the 88.2\% 5-fold CV classification accuracy
```

If the tex values are correct (from a different run), then the script comment is stale and
the committed figures may already embed the wrong number. In either case the mismatch must
be resolved before submission: run the script from a clean environment, capture live output,
and update whichever side is wrong.

---

## Warnings

### WR-01: FPCA variance-explained percentages in casestudy1.py axis labels are hardcoded magic numbers

**File:** `paper/code/casestudy1.py:132-133`

**Issue:** The PC1/PC2 axis labels are built from literal float constants:

```python
ax2.set_xlabel("PC1 (" + str(round(0.693 * 100, 1)) + "% var. explained)")
ax2.set_ylabel("PC2 (" + str(round(0.230 * 100, 1)) + "% var. explained)")
```

The `to_pc` / `fdars.regression.fpca` return dict contains `scores`, `rotation`,
`singular_values`, `mean`, `centered`, `weights` — no `variance_explained` or `prop_var`
key. Variance fractions must be derived from `singular_values` (proportion =
`sv_i^2 / sum(sv^2)`). If a future fdars-core update changes FPCA normalisation or the
phoneme dataset is updated, the axis labels will silently display wrong numbers while the
figure binary passes the git-diff determinism gate unchanged.

The tex narrative (`casestudy1.tex:29`) hardcodes the same values
`$[69.3, 23.0, 5.4, 2.3]\%$`, so both break together without any CI signal.

**Fix:** Compute variance fractions from the returned `singular_values` and use them in
both the axis labels and, ideally, expose them as a printed annotation for tex cross-check:

```python
sv = pc["singular_values"]           # shape (4,)
prop_var = sv**2 / np.sum(sv**2)     # variance fractions
ax2.set_xlabel(f"PC1 ({round(float(prop_var[0]) * 100, 1)}% var. explained)")
ax2.set_ylabel(f"PC2 ({round(float(prop_var[1]) * 100, 1)}% var. explained)")
print("Variance explained:", [round(float(v), 3) for v in prop_var])
```

Update `casestudy1.tex:29` to match the printed output.

---

### WR-02: gen_figures.py silently swallows ImportError for casestudy2-4, undermining the determinism gate

**File:** `paper/code/gen_figures.py:53-67`

**Issue:** Studies 2, 3, and 4 are wrapped in `try/except ImportError`:

```python
try:
    import casestudy2
    casestudy2.main()
except ImportError:
    pass
```

These modules are now committed and present. Any import-time failure — a removed or renamed
symbol (e.g., `FPCRegressor` moved or `FPCATransformer` renamed in `fdars.sklearn._skeletons`)
— is silently swallowed. When this happens:

1. The affected study's `main()` never runs.
2. The committed figures are not regenerated.
3. `git diff paper/figures/` shows no change.
4. The CI determinism gate passes — reporting a false green.

The result is stale figures published under a passing CI badge.

**Fix:** Since all three modules are now permanently committed, remove the try/except and
let import failures surface as hard errors. If graceful degradation is still desired for
dev convenience, at minimum print a warning:

```python
try:
    import casestudy2
    casestudy2.main()
except ImportError as e:
    import warnings
    warnings.warn(f"casestudy2 skipped (ImportError): {e}", stacklevel=2)
```

A hard failure (`raise`) is preferable for CI; a warning is acceptable for interactive use
only if a separate CI-mode flag is added.

---

## Info

### IN-01: casestudy3.py fits ftsm twice (once explicit, once inside ftsm_forecast)

**File:** `paper/code/casestudy3.py:61-72`

**Issue:** `fdars.fts.ftsm_forecast` internally re-fits the FTSM model from raw data (per
`fts_mod.rs:125`). The script calls `ftsm` explicitly to obtain `model["mean"]` for Figure
1, then calls `ftsm_forecast` which repeats the fit. This is two full FTSM fits on the same
35-station matrix.

This is not a correctness bug (both fits use identical inputs and produce identical outputs),
but it doubles compute time and may confuse a reader of the script into thinking the model
passed to the forecast is the one already fitted.

**Fix:** No action required for correctness. For clarity, add a comment noting that
`ftsm_forecast` internally re-fits rather than consuming `model`:

```python
# NOTE: ftsm_forecast re-fits ftsm internally (Rust API); model above is for
# Figure 1 only. The two fits are byte-identical given the same inputs + seed.
```

---

### IN-02: casestudy4.py Figure 2 uses an independent FPCATransformer fit, not the GridSearchCV best estimator

**File:** `paper/code/casestudy4.py:130-131`

**Issue:** The scatter plot for Figure 2 is produced by fitting a fresh `FPCATransformer`:

```python
fpca_best = FPCATransformer(n_components=best_nc)
Xw_transformed = fpca_best.fit_transform(Xw)
```

`casestudy4.tex:62` describes these as "FPCA scores of the best estimator", but they are
from an independent estimator object, not `gs.best_estimator_.named_steps["fpca"]`. Because
`FPCATransformer` is deterministic and the data is the same, the outputs are numerically
identical. The framing in the tex is nonetheless slightly misleading for a peer reviewer
inspecting the code.

**Fix:** Either use the actual best estimator from the grid search, or add a comment noting
the equivalence:

```python
# Equivalent to gs.best_estimator_.named_steps["fpca"].transform(Xw) since
# FPCATransformer is deterministic given same data and n_components.
fpca_best = FPCATransformer(n_components=best_nc)
Xw_transformed = fpca_best.fit_transform(Xw)
```

Alternatively, use `gs.best_estimator_.named_steps["fpca"].transform(Xw)` directly (the
pipeline's best estimator was refit on all data by `GridSearchCV(refit=True)`).

---

_Reviewed: 2026-09-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
