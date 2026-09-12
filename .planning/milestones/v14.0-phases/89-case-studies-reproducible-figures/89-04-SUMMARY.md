---
phase: 89-case-studies-reproducible-figures
plan: "04"
subsystem: paper/code, paper/figures, paper/sections
tags: [case-studies, sklearn-pipeline, gridsearchcv, fpca, determinism, latex]
status: complete

dependency_graph:
  requires:
    - "paper/code/paper_utils.py (Phase 85 harness: fig, FDARS_COLORS, save_figure, data_path)"
    - "scripts/docs_fig.py (Agg backend + rcParams)"
    - "docs/data/wine.csv (Study 4 dataset, 178x13, index=class)"
    - "fdars 0.12.0 (.venv compiled)"
    - "89-01 (casestudies.tex four-input shell + gen_figures.py lazy import for casestudy4)"
  provides:
    - "paper/code/casestudy4.py (Study-4 Pipeline+GridSearchCV pipeline)"
    - "paper/figures/cs4_wine_gridsearch.pdf (deterministic committed figure)"
    - "paper/figures/cs4_wine_scores.pdf (deterministic committed figure)"
    - "paper/sections/casestudy4.tex (Study-4 narrative subsection)"
  affects: []

tech_stack:
  added:
    - "FPCATransformer from fdars.sklearn._skeletons composed with sklearn LinearDiscriminantAnalysis"
    - "sklearn GridSearchCV(n_jobs=1) over fpca__n_components for hyperparameter tuning"
  patterns:
    - "casestudy4.py mirrors casestudy1.py module pattern: main() seeds seed(42), runs pipeline, saves via save_figure"
    - "casestudy4.tex is a self-contained \\subsection wired by 89-01's casestudies.tex \\input; touches no 89-01-owned file"
    - "gen_figures.py auto-picks up casestudy4 via 89-01's lazy try/except ImportError stub (no shared-file edit)"

key_files:
  created:
    - paper/code/casestudy4.py
    - paper/figures/cs4_wine_gridsearch.pdf
    - paper/figures/cs4_wine_scores.pdf
    - paper/sections/casestudy4.tex
  modified: []

decisions:
  - "Pipeline is FPCATransformer -> sklearn LinearDiscriminantAnalysis (NOT FPCKNNClassifier) — Pitfall 2: FPCKNNClassifier re-applies FPCA internally, double-FPCA degrades accuracy to 0.467"
  - "Live grid results EXACTLY match 89-RESEARCH: mean CV accuracy [0.697, 0.759, 0.916, 0.961] for n_components {2,3,5,8}, best 0.961 at n=8 — no deviation from research numbers"
  - "Figure 2 fits an independent FPCATransformer(n_components=best_nc) for a clean deterministic scores scatter (per plan action note — cleaner than extracting from the fitted GridSearchCV estimator)"
  - "Cited ramoscarreno_scikitfda_2024 for the sklearn-estimator-layer story (no scikit-learn/pedregosa bib key exists); ramsay_silverman_2005 (FPCA) + preda_saporta_2005 (functional discriminant) for methods"
  - "Referenced sklearn estimator count via \\nsklearnestimators macro (machine-derived); did not hardcode 28"

metrics:
  duration_seconds: 1950
  completed: 2026-09-09
  tasks: 2
  commits: 2
  files_created: 4
  files_modified: 0

actuals:
  tokens: 16000
  tasks: 2
  commits: 2
---

# Phase 89 Plan 04: Case Study 4 (Wine sklearn Pipeline + GridSearchCV) Summary

**One-liner:** A composable `FPCATransformer` + sklearn `LinearDiscriminantAnalysis` pipeline tuned by `GridSearchCV(n_jobs=1)` over FPCA dimensionality on the wine dataset (best 5-fold CV accuracy 0.961 at n_components=8), with two deterministic committed figures and an honest narrative subsection showcasing the `fdars` scikit-learn estimator layer.

## What Was Built

### Task 1: casestudy4.py — Pipeline + GridSearchCV + two deterministic figures

Created `paper/code/casestudy4.py` following the `casestudy1.py` module pattern. The `main()` function:

1. Seeds `np.random.seed(42)` FIRST for determinism.
2. Loads `wine.csv` (178 × 13); `Xw = wn.values.astype(np.float64)`; `yw = np.array(wn.index.tolist(), dtype=np.int64) - 1` (1,2,3 → 0,1,2 int64; Pitfall 5). Class counts 59/71/48.
3. Builds `Pipeline([("fpca", FPCATransformer(n_components=3)), ("lda", LinearDiscriminantAnalysis())])` — FPCATransformer → plain sklearn LDA, **NOT** FPCKNNClassifier (Pitfall 2: double-FPCA).
4. Tunes via `GridSearchCV(pipe, {"fpca__n_components": [2,3,5,8]}, cv=5, scoring="accuracy", refit=True, n_jobs=1)` — `n_jobs=1` for deterministic split ordering (Pitfall 7).
5. `gs.fit(Xw, yw)` → prints `best: {'fpca__n_components': 8} 0.961` (computed live).
6. Writes `cs4_wine_gridsearch.pdf` (mean CV accuracy bar chart vs n_components, each bar annotated with its rounded accuracy) and `cs4_wine_scores.pdf` (FPCA scores scatter PC1 vs PC2 of an independent `FPCATransformer(n_components=8).fit_transform(Xw)`, coloured by class).

**Live grid results (exactly match 89-RESEARCH):** mean CV accuracy `[0.697, 0.759, 0.916, 0.961]` for n_components `{2, 3, 5, 8}`; best 0.961 at n=8.

Determinism confirmed by the orchestrator (byte-identical figures across two consecutive runs) and re-confirmed post-commit via `git diff --exit-code paper/figures/` (empty on re-run).

### Task 2: casestudy4.tex — narrative subsection

Created `paper/sections/casestudy4.tex` as a `\subsection{Composable scikit-learn Pipelines: Wine Data}`:

- Problem framing: 178 wine samples, 13 chemical measurements, 3 cultivar classes (59/71/48); an `fdars` `FPCATransformer` composed with a vanilla sklearn `LinearDiscriminantAnalysis`, tuned by `GridSearchCV`.
- Honest methods framing: the estimator layer plugs natively into `Pipeline`/`GridSearchCV`; the 13-feature "functional preprocessing" framing is stated explicitly as **not** a traditional-FDA interpretation (no overclaim).
- Honest grid results: mean CV accuracy 0.697/0.759/0.916/0.961 for n_components 2/3/5/8; best CV accuracy 0.961 at n_components=8.
- Two `\begin{figure}` environments with `\includegraphics` for both committed PDFs, each with caption + `\label`.
- sklearn estimator count via the `\nsklearnestimators` macro (not hardcoded 28).
- Cites: `ramoscarreno_scikitfda_2024`, `ramsay_silverman_2005`, `preda_saporta_2005` — all resolve.
- References the reproducing script `paper/code/casestudy4.py` in prose.

## Deviations from Plan

### Auto-fixed Issues

None.

### Documented Deviations

None — the plan executed exactly as written. The live grid results matched 89-RESEARCH numbers verbatim (unlike 89-01 where the CV accuracy drifted); best CV accuracy is 0.961 at n_components=8 as specified.

## Commits

| Hash | Message |
|------|---------|
| 248bb24 | feat(89-04): casestudy4.py — wine sklearn Pipeline + GridSearchCV + two deterministic figures |
| baef6cd | feat(89-04): casestudy4.tex — wine sklearn pipeline case study narrative |

## Known Stubs

None. `casestudy4.py` runs the full validated pipeline end-to-end against fdars 0.12.0; both figures are real committed artifacts; `casestudy4.tex` reports live-computed numbers with no placeholders.

## Threat Flags

None. No new network endpoints, auth paths, or schema changes. Both threat-register mitigations were honoured: T-89-08 (nondeterminism) via `n_jobs=1` + `save_figure` CreationDate=None + git-diff gate; T-89-09 (accuracy honesty) via `best_score_` computed live and full grid reported honestly (0.697..0.961).

## Self-Check: PASSED

- paper/code/casestudy4.py: FOUND
- paper/figures/cs4_wine_gridsearch.pdf: FOUND
- paper/figures/cs4_wine_scores.pdf: FOUND
- paper/sections/casestudy4.tex: FOUND (\subsection, both \includegraphics, \nsklearnestimators, no hardcoded 28)
- Commit 248bb24: verified in git log
- Commit baef6cd: verified in git log
- No 89-01-owned file modified (casestudies.tex, gen_figures.py, gen_snippets.py, Makefile, paper.yml all clean)
