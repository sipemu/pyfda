---
phase: 89-case-studies-reproducible-figures
fixed_at: 2026-09-09T00:00:00Z
review_path: .planning/phases/89-case-studies-reproducible-figures/89-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 89: Code Review Fix Report

**Fixed at:** 2026-09-09
**Source review:** `.planning/phases/89-case-studies-reproducible-figures/89-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 6
- Fixed: 6
- Skipped: 0

## Fixed Issues

### CR-01: Figure cs1_phoneme_smooth.pdf overlays smoothed curves from wrong phoneme classes

**Files modified:** `paper/code/casestudy1.py`, `paper/figures/cs1_phoneme_smooth.pdf`, `paper/figures/cs1_phoneme_fpca.pdf`
**Commit:** f9fc58c
**Applied fix:** Replaced the positional-block approach (`X[:20]` with `ci * 4` offsets) with per-class index selection by actual label membership. Now builds `class_rows_pre` dict mapping each class to its row indices in the full 400-obs dataset, then takes the first 4 rows per class in sorted class order to form `selected` (20 indices). `smooth_basis_gcv` is called on `X[selected]`, giving `sm["fitted"]` ordered class-by-class (rows 0-3 = aa, 4-7 = ao, 8-11 = dcl, 12-15 = iy, 16-19 = sh). The `ci * 4` offset in the plot loop is now correct. Both figures regenerated; determinism verified (git diff empty on second run).

---

### CR-02: casestudy1.tex reports a CV accuracy and fold-score vector that conflicts with casestudy1.py

**Files modified:** `paper/code/casestudy1.py`, `paper/sections/casestudy1.tex`, `paper/figures/cs1_phoneme_fpca.pdf`
**Commit:** f9fc58c
**Applied fix:** Reconciled all accuracy references to the single live value:

- **Live output confirmed:** `acc = 0.8625`, `round(acc, 3) = 0.863`, fold scores `[0.850, 0.850, 0.8625, 0.875, 0.875]`.
- **casestudy1.py:** Updated `REAL OUTPUT` comment to `[0.850, 0.850, 0.8625, 0.875, 0.875] mean: 0.8625`. Added `print("CV fold scores:", ...)`. Figure title now uses `round(round(acc, 3) * 100, 1)` = 86.3% (consistent with printed "CV accuracy: 0.863").
- **casestudy1.tex:** Updated fold-score vector from `[0.850, 0.850, 0.862, 0.875, 0.875]` to `[0.850, 0.850, 0.863, 0.875, 0.875]` (third fold: `round(0.8625, 3) = 0.863`). Body text and caption retain "86.3%" which is now consistent with the figure title.

**Reconciled Study-1 accuracy:** `0.863` (86.3%) — stable across all runs.

---

### WR-01: FPCA variance-explained percentages in casestudy1.py axis labels are hardcoded magic numbers

**Files modified:** `paper/code/casestudy1.py`, `paper/figures/cs1_phoneme_fpca.pdf`
**Commit:** f9fc58c
**Applied fix:** Replaced hardcoded `0.693` and `0.230` constants with live computation from `pc["singular_values"]`: `prop_var = sv ** 2 / float(np.sum(sv ** 2))`. Axis labels now use f-strings with `round(float(prop_var[0]) * 100, 1)` and `round(float(prop_var[1]) * 100, 1)`. Added `print("Variance explained:", ...)` for cross-checking against tex. Live values confirmed: PC1 = 69.3%, PC2 = 23.0% — matching the `casestudy1.tex` paragraph (no tex change needed). Figure regenerated; determinism verified.

---

### WR-02: gen_figures.py silently swallows ImportError for casestudy2-4

**Files modified:** `paper/code/gen_figures.py`
**Commit:** f769246
**Applied fix:** Removed all three `try/except ImportError: pass` blocks for casestudy2, casestudy3, and casestudy4. Now imports and calls each module directly (`import casestudy2; casestudy2.main()` etc.) so any import-time or runtime failure propagates as a hard error. Verified: `gen_figures.py` exits 0 with all 4 studies running; `git diff --exit-code paper/figures/` empty on second run.

---

### IN-01: casestudy3.py fits ftsm twice (once explicit, once inside ftsm_forecast)

**Files modified:** `paper/code/casestudy3.py`
**Commit:** 73bba5d
**Applied fix:** Added explanatory comment before `ftsm_forecast` call noting that it internally re-fits ftsm from raw data (Rust API), that the explicit `ftsm()` call above is used only for Figure 1 (mean curve), and that both fits are byte-identical given identical inputs. No logic or figure changes.

---

### IN-02: casestudy4.py Figure 2 uses an independent FPCATransformer fit but tex says "best estimator"

**Files modified:** `paper/code/casestudy4.py`
**Commit:** 73bba5d
**Applied fix:** Added comment explaining that the independent `FPCATransformer(n_components=best_nc).fit_transform(Xw)` is equivalent to `gs.best_estimator_.named_steps["fpca"].transform(Xw)` since FPCATransformer is deterministic and GridSearchCV `refit=True` re-fits on the full dataset. No logic or figure changes; casestudy4.tex framing remains acceptable given the comment clarifies equivalence.

---

## Post-Fix Verification

**Verification ran in:** main checkout (workflow.use_worktrees=false)

1. **All 4 studies run:** `PYTHONPATH=scripts:paper/code .venv/bin/python paper/code/gen_figures.py` exits 0 — all figures regenerated.
2. **Determinism:** Second run of gen_figures.py → `git diff --exit-code paper/figures/` empty (all 9 figures byte-identical).
3. **Study-1 reconciled accuracy:** 0.863 (86.3%) — consistent across script print, figure title, tex body, and tex caption. Fold scores [0.850, 0.850, 0.863, 0.875, 0.875] now match live output.
4. **No silent ImportError swallow:** gen_figures.py imports casestudy2/3/4 directly; any future failure is fatal.
5. **Variance fractions:** computed live from `pc["singular_values"]`; confirmed PC1=69.3%, PC2=23.0%.

---

_Fixed: 2026-09-09_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
