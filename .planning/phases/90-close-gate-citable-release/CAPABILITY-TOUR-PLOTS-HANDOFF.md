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

## ALSO PENDING: remaining line overflows (GATE-04 feedback 2026-09-09)
Underscore-break fix landed (`\renewcommand{\_}{\textunderscore\allowbreak}` in paper.tex)
— overfull hboxes dropped 36→18; the cited `python/fdars/_references_map.json` now wraps.
~3 larger overflows remain (magnitudes ~30/61/76pt), almost certainly slash-only paths
(e.g. `docs/references/`, `paper/code/casestudyN.py`) or long DOIs/URLs in the bibliography
that lack an underscore break point. Fix options (pick one):
- Make `/` breakable inside `\texttt` WITHOUT globally activating `/` (a global active `/`
  broke math/URLs — do not do that). Cleanest: wrap the offending path tokens in the `url`
  package's `\path{...}` (url/xurl already loaded; breaks at `/._`), or add explicit
  `\allowbreak` after slashes in just the offending tokens.
- Identify the exact culprits from CI: `gh run view <paper-run-id> --log | grep -A2 'Overfull \\hbox'`
  — the line after each warning shows the offending text/font run.
- Long bib DOIs/URLs: xurl should break them; if one still overflows, confirm the entry uses
  `\url`/the generated `url =` field, not a raw `\texttt`.
Re-verify with the same CI loop; target 0 large (>20pt) overfull hboxes.

## ALSO PENDING: arXiv submission compliance (https://info.arxiv.org/help/submit)
DONE now: guarded `\ifdefined\pdfoutput\pdfoutput=1\fi` added to paper.tex line 1
(forces pdflatex/PDF mode on arXiv; no-op under tectonic/XeTeX in CI).

TODO for arXiv-readiness (build an `arxiv` bundle target + verify):
1. SUBMIT SOURCE, not PDF: arXiv requires LaTeX source for TeX papers. Build a clean
   tarball containing ONLY: paper.tex, sections/*.tex, snippets/*.tex, coverage_counts.tex,
   refs.bib, refs_manual.bib, figures/*.pdf, and the generated **paper.bbl**. Exclude
   paper/code/, .aux/.log/.out/.synctex, _ci_pdf/, comparison_evidence.md, *.md.
   Add a `make arxiv` target producing `paper/arxiv-submission.tar.gz`.
2. INCLUDE THE .bbl: arXiv does not reliably run bibtex for `\bibliography{refs,refs_manual}`
   (two databases). Generate `paper.bbl` (tectonic `--keep-intermediate-files`, or a
   pdflatex+bibtex pass) and include it in the bundle so references render without arXiv
   re-running bibtex. Verify the .bbl resolves all 24+ \cite keys.
3. PACKAGES: all used packages (tikz, pgf, listings, natbib, hyperref, xurl, booktabs,
   adjustbox, amsmath, amssymb, graphicx, inputenc, fontenc) are in arXiv's TeX Live — OK.
   Do NOT add exotic/local .sty files.
4. FIGURES: matplotlib PDFs + TikZ (compiled) — pdflatex-compatible. OK. Keep relative paths
   (`figures/...`, `sections/...`) — no absolute paths. Confirmed OK.
5. arXiv compiles with pdflatex+bibtex (NOT tectonic). RESIDUAL RISK: our GATE-03 proxy is
   tectonic. Ideally do one real pdflatex+bibtex compile of the bundle (Docker texlive image,
   or arXiv's own sanity check on upload) before announcing. At minimum, the guarded
   \pdfoutput + standard packages make this low-risk.
6. METADATA/LICENSE (user does at upload): title, authors (Simon Müller), abstract, primary
   category (suggest cs.MS "Mathematical Software" or stat.CO), license selection, and the
   real arXiv id/DOI — then replace the CITATION.cff `PLACEHOLDER` arXiv URL post-assignment.
7. Size < 50 MB (ours is well under). No `\input`/`\include` of files outside the bundle.
Verify the bundle compiles clean and references appear, then it is arXiv-ready.
