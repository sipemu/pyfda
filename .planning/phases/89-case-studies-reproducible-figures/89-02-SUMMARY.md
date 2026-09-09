---
phase: 89-case-studies-reproducible-figures
plan: "02"
subsystem: paper/case-studies
tags: [case-study, registration, regression, functional-data, reproducible-figures]
status: complete
completed: "2026-09-09"

dependency_graph:
  requires: ["89-01"]
  provides: [paper/code/casestudy2.py, paper/figures/cs2_tecator_align.pdf, paper/figures/cs2_tecator_fit.pdf, paper/sections/casestudy2.tex]
  affects: [paper/sections/casestudies.tex]

tech_stack:
  added: []
  patterns:
    - casestudy module pattern (from __future__ import annotations, _FIGURES_DIR, main())
    - save_figure with CreationDate=None for byte-stable PDFs
    - karcher_mean subset (30 curves) + align_to_target (all 240)
    - fregre_lm with n_comp + fitted_values key (not "fitted")
    - FPCRegressor with n_components (sklearn convention; different from n_comp)

key_files:
  created:
    - paper/code/casestudy2.py
    - paper/figures/cs2_tecator_align.pdf
    - paper/figures/cs2_tecator_fit.pdf
    - paper/sections/casestudy2.tex
  modified: []

decisions:
  - "Used karcher_mean on 30-curve subset for speed; align_to_target applied to all 240; converged=False printed informally, not asserted"
  - "Reported CV fold scores [0.903, 0.405, 0.883, 0.922, 0.914] honestly — weak fold 0.405 included in mean 0.805; not hidden"
  - "Two separate figures: cs2_tecator_align.pdf (registration) + cs2_tecator_fit.pdf (fitted vs actual scatter)"

metrics:
  duration_minutes: 5
  tasks_completed: 2
  commits: 2
  files_created: 4
  files_modified: 0

estimate:
  tokens: 55000

actuals:
  tokens: 8200
  tasks: 2
  commits: 2
---

# Phase 89 Plan 02: Registration + Scalar-on-Function Regression (Tecator) Summary

Study 2 (CASE-02): elastic registration via karcher_mean/align_to_target + scalar-on-function
FPC regression via fregre_lm on tecator near-infrared spectra, with two byte-stable committed
figures and an honest narrative reporting training R²=0.929 and 5-fold CV R²=0.805 (mean).

## What Was Built

### Task 1: casestudy2.py + two deterministic figures

`paper/code/casestudy2.py` implements the validated Study-2 pipeline from 89-RESEARCH verbatim:

1. **Data loading:** tecator.csv (240 × 100 spectra + fat response) via `data_path("tecator.csv")`.
2. **Registration:** `fdars.alignment.karcher_mean(Xt[:30], ARGt, max_iter=20)` → `align_to_target(Xt, km["mean"], ARGt)` aligns all 240 curves. `converged=False` is printed but not checked.
3. **Scalar-on-function regression:** `fdars.regression.fregre_lm(Xt, yfat, n_comp=5)` — uses `sof["fitted_values"]` (not "fitted"), `sof["r_squared"]` → training R²=0.929.
4. **Cross-validation:** `cross_val_score(FPCRegressor(n_components=5), Xt, yfat, cv=5, scoring="r2")` → fold scores [0.903, 0.405, 0.883, 0.922, 0.914], mean 0.805.

**Figures produced:**
- `cs2_tecator_align.pdf`: raw spectra (grey) + aligned spectra (coloured) + Karcher mean (bold), 30 curves.
- `cs2_tecator_fit.pdf`: actual vs fitted fat content scatter with R²=0.929 annotated; y=x reference line.

Both figures verified byte-stable: two consecutive runs produce identical PDFs (diff -q empty).

### Task 2: casestudy2.tex narrative subsection

`paper/sections/casestudy2.tex` is a `\subsection` titled "Registration and Scalar-on-Function
Regression: Tecator Data" that:
- Frames the problem (240 NIR spectra, fat content 0.9–58.5%).
- Describes registration honestly (iterations capped at 20; convergence not required).
- Reports training R²=0.929 and CV fold scores [0.903, 0.405, 0.883, 0.922, 0.914] (mean 0.805).
- Mentions weak fold 2 (0.405) explicitly without adjustment.
- Includes `\includegraphics` for both cs2 figures with captions and labels.
- Cites `ramsay_silverman_2005`, `srivastava_klassen_2016`, `preda_saporta_2005` (all resolved).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Comment text matched `assert .*converged` grep pattern in verify block**
- **Found during:** Task 1 verify
- **Issue:** The docstring contained the phrase "does NOT assert km[\"converged\"]" — the words "assert" and "converged" appeared in sequence and matched the plan's `! grep -qE 'assert .*converged'` check.
- **Fix:** Rephrased all comments referencing the converged assertion to avoid the literal sequence; moved the concept to prose that doesn't trigger the grep. No logic change.
- **Files modified:** `paper/code/casestudy2.py`
- **Commit:** 38c77ce (included in Task 1 commit after fix)

None of these modified any 89-01-owned file (casestudies.tex, gen_figures.py, gen_snippets.py, Makefile, paper.yml).

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1 | 38c77ce | paper/code/casestudy2.py, paper/figures/cs2_tecator_align.pdf, paper/figures/cs2_tecator_fit.pdf |
| Task 2 | 5994fe1 | paper/sections/casestudy2.tex |

## Real Output Numbers (Captured Live)

| Metric | Value |
|--------|-------|
| karcher_mean converged | False (expected; max_iter=20) |
| Training R² (fregre_lm, 5 comp) | 0.929 |
| CV fold R² [0..4] | [0.903, 0.405, 0.883, 0.922, 0.914] |
| 5-fold CV mean R² | 0.805 |

## Success Criteria Check

- [x] casestudy2.py runs against fdars 0.12.0 without error
- [x] train R²=0.929; CV mean R²=0.805 (honest, fold scores printed)
- [x] converged=False printed informally; not asserted
- [x] cs2_tecator_align.pdf and cs2_tecator_fit.pdf exist and are byte-stable (re-run diff empty)
- [x] casestudy2.tex uses `\subsection` (not `\section`)
- [x] Both `\includegraphics` paths present; all cites resolve
- [x] No 89-01-owned file (casestudies.tex, gen_figures.py, Makefile, paper.yml) modified

## Known Stubs

None — figures and narrative are complete with live computed numbers.

## Self-Check: PASSED

All created files exist on disk and all task commits exist in git log.
