# Handoff: Add plots + deeper explanations to Capability-Tour sections (4.x)

**Requested by user during Phase 90 GATE-04 review (2026-09-09).** Not yet done.
The milestone is otherwise complete and green; this is an additive manuscript enhancement.

## Goal
For each Capability-Tour subsection in `paper/sections/capabilities.tex` (4.1 Data
Representation, 4.2 Basis/Smoothing, 4.3 Depth/Outliers, 4.4 FPCA, 4.5 Clustering,
4.6 Classification, 4.7 Regression, 4.8 FTS, 4.9 SPM, 4.10 Conformal/Tolerance,
4.11 Metrics/Density/Fréchet, 4.12 Alignment, 4.13 Grounded Advisor):
1. Add a **plot** visualising that family's example output.
2. **Expand the prose** to explain the example in more detail (what the method does,
   what the snippet computes, how to read the plot, honest interpretation).

## How (reuse the proven harness — do NOT invent a new mechanism)
- Figures: add a `tour_<family>()` function per family in a new
  `paper/code/gen_tour_figures.py` (or extend `gen_figures.py`), reusing
  `paper_utils` (`fig`, `FDARS_COLORS`, `save_figure` with `metadata={"CreationDate": None}`,
  `data_path`). Seed every figure (`np.random.seed(42)`). Write to `paper/figures/tour_<family>.pdf`.
- Wire the new script into `gen_figures.py main()` so `make paper` regenerates them and
  the determinism gate (`git diff --exit-code paper/figures/`, `make paper-verify`) covers them.
- Use the EXACT validated call shapes from `89-RESEARCH.md` and `88-RESEARCH.md`
  (signature gotchas: FPCATransformer `n_components` vs FPCLDAClassifier `ncomp`;
  `ftsm_forecast` raw data; int64 labels; `spm_monitor` unpacked; `fpca_tolerance_band`
  `coverage=` not `alpha=`; advisor `build_diagnostics`; `pace_fpca.PyIrregFdata`).
  Every figure must actually run against fdars 0.13.0 (confirmed importable in `.venv`).
- Each subsection: `\begin{figure}[htbp] \includegraphics[width=...]{figures/tour_<family>}
  \caption{...} \label{fig:tour-<family>} \end{figure}`, referenced from the prose.
- Report REAL numbers computed live (no fabrication). Counts via macros. No benchmarks.
  Peer-review-safe, honest. No hardcoded integers in `.tex`.

## Determinism caveat (already handled milestone-wide)
- SC-5 is SAME-ENVIRONMENT: matplotlib PDFs differ across platforms. The CI figure gate
  (`.github/workflows/paper.yml` "Assert figures byte-stable") already checks same-runner
  determinism (regenerate twice, compare) and restores committed figures for the compile.
  New tour figures ride this automatically.

## Verify each round
- `make paper && git diff --exit-code paper/figures/` (deterministic same-env).
- `make paper-check` (all --check gates green), 0 dangling citations, cffconvert valid.
- Push to `origin/main` → watch `paper.yml` CI (`gh run watch <id> --exit-status`) → the
  tectonic PDF compile is GATE-03. Download the `paper-pdf` artifact
  (`gh run download <id> -n paper-pdf -D paper/_ci_pdf`) and VISUALLY inspect each new
  figure with `pdftoppm -png` + Read the image (TikZ/matplotlib render bugs only show visually).
- LaTeX pitfalls seen this milestone: `\\` in a TikZ node needs `align=`; raw U+00B7/U+2194
  mis-render (use `$\cdot$`/`$\leftrightarrow$`); long signatures overflow in `\item[]`
  labels (use `\paragraph{}` + `lstlisting`); listing frame width (framesep/xrightmargin).
- NEVER bare `cp` (aliased to `cp -i`; hangs) — use `git diff`/`install`.

## State at handoff
- Branch `main` pushed to origin (github.com/sipemu/pyfda), CI green, PDF = 35 pp.
- Package at 0.13.0 (rebuilt); CITATION.cff 0.13.0 (arXiv DOI = PLACEHOLDER).
- GATE-02 green, GATE-03 green (CI tectonic compile), GATE-04 (human read-through) STILL OPEN
  — do NOT create the `v0.13.0` tag / mark milestone complete until the user approves the PDF.
- REL-01 remaining: after GATE-04 approval, create annotated tag `v0.13.0` and hand the user
  `git push origin v0.13.0` (triggers PyPI publish) — the USER publishes, not the agent.
- Phase 90 plans: `.planning/phases/90-close-gate-citable-release/90-0{1,2}-PLAN.md`.
- Latest CI PDF: `paper/_ci_pdf/paper.pdf` (untracked scratch; clean up at close).
