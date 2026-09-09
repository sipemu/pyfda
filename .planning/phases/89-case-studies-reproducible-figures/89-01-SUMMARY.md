---
phase: 89-case-studies-reproducible-figures
plan: "01"
subsystem: paper/code, paper/figures, paper/sections, CI
tags: [case-studies, fpca, classification, determinism, latex, ci-gate]
status: complete

dependency_graph:
  requires:
    - "paper/code/paper_utils.py (Phase 85 harness)"
    - "scripts/docs_fig.py (Agg backend + rcParams)"
    - "docs/data/phoneme.csv (Study 1 dataset)"
    - "fdars 0.12.0 (.venv compiled)"
  provides:
    - "paper/code/casestudy1.py (Study-1 pipeline, reusable by Wave-2)"
    - "paper/figures/cs1_phoneme_smooth.pdf (deterministic committed figure)"
    - "paper/figures/cs1_phoneme_fpca.pdf (deterministic committed figure)"
    - "paper/sections/casestudy1.tex (Study-1 narrative subsection)"
    - "paper/sections/casestudies.tex (finalized four-input shell)"
    - "gen_figures.py main() wired to casestudy1 + lazy stubs for 2-4"
    - "Makefile paper-verify target (local SC-5 gate)"
    - "paper.yml Assert figures byte-stable step (CI SC-5 gate)"
  affects:
    - "paper/code/gen_figures.py (casestudy1 import added)"
    - "Makefile (.PHONY + paper-verify)"
    - ".github/workflows/paper.yml (determinism gate step inserted)"

tech_stack:
  added:
    - "FPCATransformer + FPCLDAClassifier from fdars.sklearn._skeletons"
    - "sklearn Pipeline + cross_val_score for 5-fold CV"
  patterns:
    - "casestudyN.py module pattern: main() seeds seed(42), runs pipeline, saves figures via paper_utils.save_figure"
    - "gen_figures.py lazy try/except ImportError stubs for Wave-2 modules"
    - "git diff --exit-code paper/figures/ as the machine-enforced SC-5 determinism gate"

key_files:
  created:
    - paper/code/casestudy1.py
    - paper/figures/cs1_phoneme_smooth.pdf
    - paper/figures/cs1_phoneme_fpca.pdf
    - paper/sections/casestudy1.tex
  modified:
    - paper/sections/casestudies.tex (stub replaced with four-input shell)
    - paper/code/gen_figures.py (casestudy1 import + lazy stubs for 2-4)
    - Makefile (paper-verify target added)
    - .github/workflows/paper.yml (Assert figures byte-stable step added)

decisions:
  - "Reported CV accuracy as 0.863 (live computed) not 0.882 (research value) — honest live result per T-89-02 mitigation"
  - "casestudies.tex is finalized here; Wave-2 plans add only casestudyN.tex subfiles, not the shell"
  - "gen_figures.py edited once: casestudy1 imported at module top, Wave-2 modules via lazy try/except so no shared-file race in Wave 2"
  - "paper-verify Makefile target: two-step (regenerate then git diff) so it can be run locally for SC-5 verification"
  - "CI gate ordered: Regenerate figures -> Assert byte-stable -> Assert coverage macros -> tectonic"

metrics:
  duration_seconds: 399
  completed: 2026-09-09
  tasks: 3
  commits: 3
  files_created: 5
  files_modified: 4

actuals:
  tokens: 15000
  tasks: 3
  commits: 3
---

# Phase 89 Plan 01: Case Study 1 (Phoneme smooth+FPCA+classification) + determinism gate machinery Summary

**One-liner:** GCV B-spline smoothing + 4-component FPCA + FPCATransformer/FPCLDAClassifier 5-fold CV (86.3% accuracy) on phoneme data, with two deterministic committed figures and a git diff --exit-code paper/figures/ gate established in CI.

## What Was Built

### Task 1: casestudy1.py — validated pipeline + two deterministic figures

Created `paper/code/casestudy1.py` following the `gen_figures.py` module pattern. The `main()` function:

1. Seeds `np.random.seed(42)` for determinism
2. Loads `phoneme.csv` (400 × 256); computes `ARG = np.arange(1, 257)`
3. Smooths a 20-curve subset: `fdars.basis.smooth_basis_gcv(X[:20], ARG, n_basis=15, basis_type="bspline")`
4. Runs FPCA: `fd = fdars.Fdata(X, argvals=ARG); pc = fd.to_pc(n_comp=4)` — variance explained [0.693, 0.230, 0.054, 0.023]
5. Builds int64 labels via sorted lut over `ph.index.tolist()`
6. Evaluates `Pipeline([("fpca", FPCATransformer(n_components=4)), ("lda", FPCLDAClassifier(ncomp=4))])` with `cross_val_score(..., cv=5)` — reports live CV accuracy
7. Writes `cs1_phoneme_smooth.pdf` and `cs1_phoneme_fpca.pdf` via `save_figure`

Re-run byte-stability verified: two back-to-back executions produce identical PDFs (`diff -q` clean).

### Task 2: casestudy1.tex + casestudies.tex

- `casestudies.tex`: replaced placeholder stub with `\section{Case Studies}`, one framing paragraph describing the reproduced-script approach, then exactly four `\input` lines. No `\subsection` or `\includegraphics` in the shell file. **This file is finalized — Wave-2 plans add only their own casestudyN.tex.**
- `casestudy1.tex`: `\subsection{Smoothing, FPCA, and Classification: Phoneme Data}` with honest narrative (reports live 86.3% CV accuracy, fold scores, FPCA variance breakdown 69.3/23.0/5.4/2.3%); two `\begin{figure}` environments with `\includegraphics` for both committed PDFs; cite keys `craven_wahba_1979`, `eilers_marx_1996`, `ramsay_silverman_2005`, `preda_saporta_2005`, `ferraty_vieu_2006` — all resolve in refs.bib.

### Task 3: gen_figures.py + Makefile + paper.yml

- `gen_figures.py`: added `import casestudy1` at module top; `main()` calls `casestudy1.main()` after `_smoke()`; lazy `try/except ImportError` stubs for `casestudy2`, `casestudy3`, `casestudy4` so Wave-2 modules auto-register once their files exist
- `Makefile`: added `paper-verify` phony target — runs `gen_figures.py` then `git diff --exit-code paper/figures/` (SC-5 local hard gate)
- `paper.yml`: inserted "Assert figures byte-stable (PIPE-02 / CASE SC-5 determinism gate)" step with `git diff --exit-code paper/figures/` ordered after "Regenerate figures" and before "Setup tectonic" — SC-5 is now machine-enforced in CI

## Deviations from Plan

### Auto-fixed Issues

None.

### Documented Deviations

**1. [Data] CV accuracy 0.863 vs research-expected 0.882**
- **Found during:** Task 1 execution
- **Issue:** Live `cross_val_score` against fdars 0.12.0 + current sklearn returns fold scores `[0.850, 0.850, 0.862, 0.875, 0.875]`, mean 0.863 — not the 0.882 from 89-RESEARCH.md
- **Fix:** Reported the live computed value (0.863) in both `casestudy1.tex` narrative and figure annotation per T-89-02 mitigation (numbers computed live, never invented). The plan explicitly states the code must NOT hardcode 0.882.
- **Impact:** casestudy1.tex reports 86.3% CV accuracy (not 88.2%). This is the honest, reproducible number.
- **Root cause:** Minor version-to-version variation in sklearn KFold splitting or fdars FPCA internals between research session and execution session.

## Commits

| Hash | Message |
|------|---------|
| 21849ad | feat(89-01): casestudy1.py — validated smooth+FPCA+LDA pipeline + two deterministic figures |
| 4078ccf | feat(89-01): casestudy1.tex narrative + casestudies.tex four-input shell |
| a399177 | feat(89-01): wire casestudy1 into gen_figures.py + establish git diff --exit-code determinism gate |

## Known Stubs

None. The per-study casestudy2/3/4.tex subfiles do not yet exist (casestudies.tex `\input` lines for 2–4 point to absent files). These are intentionally deferred to Wave-2 plans (89-02, 89-03, 89-04). LaTeX compilation with those inputs missing will fail until Wave 2 delivers the subfiles — this is expected and documented.

## Threat Flags

None. No new network endpoints, auth paths, or schema changes introduced.

## Self-Check: PASSED

- paper/code/casestudy1.py: FOUND
- paper/figures/cs1_phoneme_smooth.pdf: FOUND
- paper/figures/cs1_phoneme_fpca.pdf: FOUND
- paper/sections/casestudy1.tex: FOUND
- paper/sections/casestudies.tex: FOUND (four \input lines present, no Placeholder)
- paper/code/gen_figures.py: casestudy1 import FOUND, casestudy1.main() call FOUND
- Makefile paper-verify: FOUND, git diff --exit-code assertion FOUND
- paper.yml Assert figures byte-stable step: FOUND, ordered after regenerate and before tectonic
- Commits 21849ad, 4078ccf, a399177: all verified in git log
