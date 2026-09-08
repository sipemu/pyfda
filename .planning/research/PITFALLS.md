# Pitfalls Research

**Domain:** Software-description paper (arXiv preprint) + reproducible figure/table artifact for a functional data analysis library (v14.0)
**Researched:** 2026-09-08
**Confidence:** HIGH (grounded in: shipped codebase patterns, official arXiv submission docs, tectonic GitHub issue tracker, matplotlib determinism documentation, FDApy paper as style target; LOW-confidence items from web search cross-checked against multiple sources)

---

## Critical Pitfalls

### Pitfall 1: Stale API Snippets — Code in the Paper That No Longer Runs

**What goes wrong:**
A manuscript code snippet that worked at write time fails silently against the current `fdars` API by the time the paper is submitted or cited. The FDApy paper (arXiv:2101.11003) is the canonical example: submitted 2021, revised 2024, with a three-year gap during which the API evolved. Readers attempting to reproduce examples find `AttributeError` or wrong output. For `fdars`, the risk is concrete: the PyO3 binding layer is under active development; argument names, dict-key names (e.g., result dict keys from `functional_boxplot`, `pace_fpca`, ITP), and method signatures have changed across v4–v11 milestones.

**Why it happens:**
Snippets are written once and committed to LaTeX source without a test harness. When the paper is revised or the code is bumped, the snippets are not re-executed. "It compiled" is confused with "it runs correctly." The paper's source is in `paper/` and the code is in `paper/code/` — if these are not wired together (i.e., if snippets in the `.tex` file are copy-pasted rather than executed-and-inlined), they drift independently.

**How to avoid:**
- Every manuscript code snippet must be extracted from the same `paper/code/` scripts that power the reproducible pipeline. No copy-paste from a REPL. Use a `\lstinputlisting` or `\verbatiminput` pattern to include code fragments directly from the validated scripts — if the script changes, the paper updates automatically.
- The reproducible pipeline gate (`paper/code/run_all.py` or equivalent) must be a hard local gate that runs every snippet script against the current installed `fdars` and asserts no error. This gate must pass before any LaTeX work is reviewed.
- Add a CI job that installs the current `fdars` wheel from the repo (via `maturin develop`) and runs all snippet scripts. If a script fails, the CI gate fails.
- Before close, run `python -c "exec(open('paper/code/snippet_X.py').read())"` for every code block that appears in the manuscript. Machine-check, not eyeball.

**Warning signs:**
- Any snippet in `.tex` that uses a function signature not present in `python/fdars/`.
- A `paper/code/` directory that exists but whose scripts are not wired into a runner that CI can invoke.
- Snippets that import `fdars` but do not assert any output (cannot detect silent breakage).
- Dict-key accesses on result dicts (e.g., `result["scores"]`, `result["mean_curve"]`) that are not validated against the current binding's return shape.

**Phase to address:**
The reproducible artifact phase (the earliest phase that creates `paper/code/`). The runner + CI job are the foundation; snippets must flow from runner outputs, not be authored independently in `.tex`. The close gate must re-run the pipeline from scratch in a clean virtualenv.

---

### Pitfall 2: Coverage-Count Drift — Hardcoded Numbers in the Manuscript

**What goes wrong:**
The manuscript says "fdars exposes 437 callables across 31 modules" (or some coverage fraction). At submission time that number is correct. A future crate bump or new binding phase (e.g., a v15.0 upgrade) changes the callable count, but the paper's hardcoded number is not updated. The paper cites a stale count; the comparison table says "N methods in family X" when Y are now present. For software papers cited and read for years, stale counts erode trust in the whole paper.

**Why it happens:**
Coverage numbers feel like facts at write time. They are not: `_capability_map.json` is the live ground truth (31 modules, 437 callables as of v14.0) and it evolves. If the paper hardcodes "437" instead of deriving it from the JSON at build time, the two will diverge on the next milestone.

**How to avoid:**
- Derive all coverage numbers in the manuscript from `_capability_map.json` at paper-build time. Write a `paper/code/gen_counts.py` that reads `_capability_map.json`, counts callables per module family, and writes a LaTeX `\newcommand` file (e.g., `paper/counts.tex`) with macros like `\FdarsCallableCount{437}` and `\FdarsModuleCount{31}`. Include this file in `paper.tex` via `\input{counts}`.
- The `gen_counts.py` script is part of the reproducible pipeline and is re-run on every build. If the capability map changes, the counts auto-update.
- The comparison table (feature comparison vs scikit-fda, FDApy, R fda, fda.usc, refund) must NOT hardcode method counts for competitor packages. State the version of each competitor at comparison time and note that counts reflect that version.
- Do not use "all" or "complete" without qualification — use the machine-derived fraction.

**Warning signs:**
- Any literal integer in `paper.tex` that represents a callable count, module count, or coverage fraction.
- Coverage numbers that differ between the manuscript and what `python -c "import json; cm=json.load(open('python/fdars/_capability_map.json')); print(sum(len(v) for v in cm.values()))"` reports.
- A `paper/` build that does not re-read `_capability_map.json` as part of its pipeline.

**Phase to address:**
The manuscript scaffold phase (the first phase that creates `paper.tex`). Establish the `\input{counts}` pattern before any coverage claims are written. The pipeline gate must regenerate `counts.tex` before every LaTeX compile.

---

### Pitfall 3: Inaccurate Competitor Comparison Table — Wrong Feature Claims

**What goes wrong:**
The comparison-with-related-software table claims that scikit-fda "does not support irregular grids" when in fact it has since added `IrregularFunctionalData`. Or the table says FDApy "lacks sklearn compatibility" when FDApy has sklearn-compatible estimators. Or the table marks R's `refund` as having no functional PCA when `fpca.sc()` exists. Wrong negative claims about competitors are a primary peer review rejection reason for software papers.

**Why it happens:**
Comparison tables are authored at one point in time against the author's knowledge of competitor packages, without systematic verification. Competitor packages evolve faster than the paper revision cycle. The pressure to highlight differentiators leads to over-claiming limitations of alternatives. The FDApy and scikit-fda papers (arXiv:2101.11003 and arXiv:2211.02566) themselves are the primary peer documents — claims that contradict their stated feature sets are immediately checkable by reviewers.

**How to avoid:**
- For every "no" / "partial" cell in the comparison table, record the evidence: the competitor version checked, the specific function or absence of function, and the URL or paper section. This evidence must live in `paper/code/comparison_evidence.md` or similar, separate from the `.tex` source. A human reviewer must check this evidence against the competitor's current docs before the table is finalized.
- Use qualifier language: "as of version X.Y (checked YYYY-MM-DD)" in a table footnote. This turns a potentially-wrong claim into a timestamped, verifiable observation.
- The comparison table must cover: scikit-fda (JSS 2024, arXiv:2211.02566), FDApy (arXiv:2101.11003), R `fda` (Ramsay & Silverman), R `fda.usc`, R `refund`. For each, check the CRAN/PyPI page and the paper's feature list, not just the author's recall.
- Never claim a competitor "cannot" do something based on absence of a named function. Check the docs, not just the function list.
- The grounding invariant applies here: coverage claims for fdars must come from `_capability_map.json`; coverage claims for competitors must cite a specific verifiable source.

**Warning signs:**
- A comparison table cell with no cited source for a competitor limitation.
- Claims about competitor packages that are more than 6 months stale.
- The word "only" applied to competitor capability without a version-qualified citation.
- Any comparison claim that contradicts what the competitor's own arXiv paper states.

**Phase to address:**
The comparison table phase (whichever phase writes the comparison section). The evidence file must be written and human-reviewed before the `.tex` comparison table is finalized. This is analogous to the blocking human citation-accuracy review from v13.0 — the same discipline applies.

---

### Pitfall 4: matplotlib Non-Determinism — Figures That Change on Every Run

**What goes wrong:**
Figures committed to `paper/figures/` show up as modified on every CI run (`git diff` is non-empty for committed PNGs/PDFs). Or: the figure generated on the author's macOS laptop looks pixel-different from the figure generated in CI on Ubuntu, causing the committed figure to not match the pipeline output. Or: a figure shows random data (e.g., a simulated functional dataset) without a fixed seed, so every run produces a different curve arrangement. These failures make "committed figures match pipeline output" unverifiable.

**Why it happens:**
PNG files are byte-deterministic IF AND ONLY IF: (a) the data is seeded, (b) no RNG is called without a prior seed, (c) the FreeType version is identical, (d) the system fonts are identical, (e) `MPLBACKEND=Agg` is set. In practice, FreeType version differs between macOS and Ubuntu CI, causing visually-identical but byte-different PNG output even with a fixed seed. PDF output from matplotlib embeds a `CreationDate` timestamp by default, making PDFs byte-different across runs. SVG output uses random identifiers by default.

**How to avoid:**
- Set `MPLBACKEND=Agg` at the top of every figure script (or in `conftest.py` / pipeline runner). Never rely on the default backend in CI.
- Seed all RNG at the top of every figure script: `np.random.seed(42); rng = np.random.default_rng(42)`. Do not call any numpy random function before seeding.
- Commit figures as PDF (not PNG): PDF with `metadata={'CreationDate': None}` is byte-stable for fixed content, and FreeType differences do not affect PDF vector output. Use `fig.savefig("paper/figures/X.pdf", metadata={"CreationDate": None}, bbox_inches="tight")`.
- If PNG is required (e.g., arXiv prefers PNG for raster content), pin FreeType in the CI requirements file (`freetype` system package version or use a Docker image with a pinned freetype). The pipeline's `requirements.txt` must specify matplotlib and numpy versions exactly (not ranges).
- Use only DejaVu fonts (bundled with matplotlib, version-independent) in all paper figures. Never use system fonts that may differ across environments.
- Generate all figures sequentially in the runner (not in parallel), to avoid shared global `rcParams` state corruption.
- After pipeline runs, assert that `git diff paper/figures/` is empty (add this check to the CI gate). A non-empty diff means a figure is non-deterministic.

**Warning signs:**
- `git status` shows `paper/figures/*.pdf` as modified after a pipeline re-run.
- Any figure script that calls `np.random` before `np.random.seed(...)`.
- A figure script that does not set `matplotlib.use('Agg')` or check `MPLBACKEND`.
- Figures that look correct visually but differ byte-for-byte between macOS and CI Ubuntu.
- Any figure using a non-bundled font (check with `matplotlib.font_manager.findSystemFonts()`).

**Phase to address:**
The reproducible artifact phase (same as Pitfall 1). Determinism requirements must be in the pipeline runner's design spec before any figure scripts are written. A determinism gate (`git diff --exit-code paper/figures/`) must be part of the CI job.

---

### Pitfall 5: tectonic biblatex Failure — Silent Unprocessed References

**What goes wrong:**
The LaTeX source uses `\usepackage{biblatex}` with `\addbibresource{refs.bib}` (the modern bibliography pattern). Tectonic compiles without error but produces a PDF with `[?]` citations or empty bibliography — because tectonic does not invoke `biber` (biblatex's required backend). There is no error message indicating the problem. The PDF looks complete but citations are broken.

**Why it happens:**
biblatex requires `biber` as its bibliography processor, not `bibtex`. Tectonic has longstanding open issues (#35, #53, #866) documenting that `biblatex+biber` is not fully supported. Tectonic silently skips the biber pass, producing a PDF with unprocessed citations. This is invisible to a CI job that only checks for exit code 0.

**How to avoid:**
- Use `natbib` + standard `bibtex` as the bibliography system, not `biblatex`. The `paper/refs.bib` file (generated from `_references_map.json`) is plain BibTeX format and works with both systems. Switch: replace `\usepackage{biblatex}` with `\usepackage[numbers,sort&compress]{natbib}` and `\bibliography{refs}` instead of `\printbibliography`.
- Verify that the tectonic CI output contains at least N references (where N is the expected citation count). A simple check: `pdftotext paper.pdf - | grep -c '^\[' || wc -l < paper.bbl`. If the bbl file is empty or the PDF has no resolved references, the gate fails.
- The `refs.bib` must be committed to `paper/` (not only the generated `.bbl`) so arXiv can reprocess it on their system with standard pdflatex.
- Do not use `\today` in the manuscript — arXiv recompiles sources on submission and the date will change. Hard-code the submission date or use a version macro.
- Before arXiv submission, test the source package with standard `pdflatex + bibtex` (not tectonic) to verify arXiv-server compatibility. arXiv uses its own TeX installation, not tectonic.

**Warning signs:**
- `\usepackage{biblatex}` anywhere in `paper.tex`.
- A compiled PDF where in-text citations show `[?]` or `??`.
- An empty or missing `.bbl` file after tectonic runs.
- The CI job for PDF compile that only checks exit code and not bibliography content.
- A `\today` macro in the title block or date field.

**Phase to address:**
The manuscript scaffold phase (same as coverage counts). The bibliography system choice (natbib vs biblatex) must be decided before the first `paper.tex` commit, and the tectonic CI job must include a reference-count sanity check. The arXiv-compatibility test (pdflatex + bibtex) belongs in the close gate.

---

### Pitfall 6: arXiv Source Package Not Self-Contained — Missing Files or Wrong Formats

**What goes wrong:**
The arXiv submission fails or produces a broken PDF because: (a) a figure file is referenced but not included in the zip (e.g., `paper/figures/case_study.pdf` is in `.gitignore` and not committed); (b) a figure is in EPS format, which requires LaTeX DVI mode but the source uses PDFLaTeX; (c) custom macro files or bibliography files are missing from the submission package; (d) intermediate build artifacts (`.aux`, `.log`) are included, confusing the arXiv TeX processor.

**Why it happens:**
Authors prepare the PDF locally (where all files are present) without testing the submission package in isolation. arXiv recompiles the submitted source on their servers — it must compile cleanly without any file from the author's local machine. Figures committed to git are fine; figures that are pipeline outputs not committed to the repo will be absent.

**How to avoid:**
- Commit all figures to `paper/figures/` in the repo. Pipeline-generated figures must be committed before submission (the pipeline is the source of truth; figures are its outputs, versioned).
- Use only PDFLaTeX-compatible figure formats: PDF (vector, preferred), PNG, or JPEG. Do not use EPS. arXiv explicitly states no on-the-fly figure conversion.
- Test the submission package by extracting the arXiv zip into a clean temporary directory and running `pdflatex + bibtex` from that directory. If it fails, the submission will fail on arXiv.
- Exclude `.aux`, `.log`, `.toc`, `.out`, `.blg`, `.bbl` (if derived) from the zip. Include: `paper.tex`, all `\input{}` files, `refs.bib`, `paper/figures/*.pdf`, any custom style files.
- Ancillary files (the `paper/code/` scripts) go in `anc/` in the arXiv submission, not at the root. These are not compiled by arXiv's TeX processor. Total submission size limit is 50MB.

**Warning signs:**
- Any figure file in `paper/figures/` that is listed in `.gitignore` or not tracked by git.
- EPS files in `paper/figures/`.
- A local build that uses absolute paths to figures (`/home/user/paper/figures/`) rather than relative paths.
- The arXiv submission zip containing `.aux` or `.log` files.
- A `paper/code/` directory that is not in `anc/` in the submission package.

**Phase to address:**
The close gate (the final gate phase before arXiv submission). A submission-package test — extract the arXiv zip into a temp directory and compile with pdflatex + bibtex from scratch — must be an explicit close-gate step. Figures committed to the repo must be verified as the pipeline's committed outputs.

---

### Pitfall 7: "Works on My Machine" Reproducible Pipeline — Environment-Dependent Numbers

**What goes wrong:**
The pipeline produces different numerical outputs (or fails outright) in CI vs. the author's development environment because: (a) `fdars` is installed from a different wheel (PyPI vs. `maturin develop`); (b) scipy/numpy version differences cause numerically equivalent but floating-point-distinct outputs; (c) a dataset path is hardcoded to `../../docs/data/` relative to the script, which works from the author's tree but fails in CI; (d) an internet fetch is needed for a dataset that is supposed to come from `docs/data/`.

**Why it happens:**
The milestone constraint explicitly requires offline operation using existing `docs/data/` datasets. But if dataset loading uses a path relative to a hardcoded working directory, the pipeline fails when run from a different cwd. If the pipeline checks `fdars` version at runtime but the CI wheel version differs (e.g., CI uses a PyPI wheel while the paper is written against a dev build with new bindings), assertions or outputs differ.

**How to avoid:**
- All dataset paths in `paper/code/` must be resolved relative to the script's `__file__`, not relative to the working directory. Use `pathlib.Path(__file__).parent.parent.parent / "docs" / "data"` (or pass the repo root as an argument). The pipeline runner must accept a `--repo-root` flag and pass it to all scripts.
- Pin ALL Python dependency versions in `paper/requirements.txt` (numpy, scipy, matplotlib, fdars version). Use exact pins (`==`), not ranges. The CI job must install from this file, not from the global environment.
- `fdars` must be installed via `maturin develop` from the repo (not from PyPI) to guarantee the paper runs against the exact current codebase. Document this explicitly in `paper/README.md`.
- The pipeline runner must emit a preamble: `python -c "import fdars; print(fdars.__version__)"` so the CI log records the exact fdars version the figures were generated against.
- No network access in the pipeline. All datasets come from `docs/data/`. If a dataset is needed that is not there, it must be added to `docs/data/` in the same phase.

**Warning signs:**
- Any `open("../../docs/data/canadian_weather.json")` style relative path in a script.
- A `requirements.txt` with unpinned versions (`numpy>=1.21`).
- A pipeline that requires `import requests` or any network call.
- A CI job that installs `fdars` from PyPI rather than `maturin develop`.
- Different numerical outputs between CI and local runs (check with `assert np.allclose(result, expected_values)` after seeding).

**Phase to address:**
The reproducible artifact phase. The runner design must include: repo-root resolution, version-pinned requirements, and a CI job that installs from `maturin develop`. These requirements must be in the phase plan before any scripts are written.

---

### Pitfall 8: Coverage-Map Sync Drift — Comparison Claims Outrun the Source of Truth

**What goes wrong:**
The comparison table claims fdars covers "functional PCA (dense + PACE sparse), elastic alignment, functional GLM, FTS forecasting" while scikit-fda covers "dense FPCA only". These claims were correct at write time. A future milestone changes something — or the author writes the comparison before finishing the `paper/code/` scripts that test each claim — and the comparison table is never re-grounded against the live `_capability_map.json`. The paper ships with a comparison that is partially wrong.

**Why it happens:**
The comparison table is written from memory or from a prior audit, not from the live capability map. The capability map (`_capability_map.json`) is the source of truth for what fdars can do, but the comparison table author does not consult it. Similarly, competitor feature claims are made from memory rather than from a checked evidence file.

**How to avoid:**
- The `gen_counts.py` script (from Pitfall 2) must also emit the per-family breakdowns used in the comparison table. For example: `FPCA_COUNT = number of entries in capability_map with "fpca" in the key`. The comparison table derives its fdars claims from these generated values, not from prose.
- For each row in the comparison table, record in `paper/code/comparison_evidence.md`: the fdars callable(s) that provide the feature (with a link to `_capability_map.json`), and the competitor evidence (function name, docs URL, version). This file is human-reviewed at the close gate.
- The close gate must include: (1) `gen_counts.py` runs without error; (2) comparison table values match the generated output; (3) human reviews the evidence file.

**Warning signs:**
- A comparison table row with a "yes" for fdars that does not correspond to any key in `_capability_map.json`.
- A comparison table row with a "no" for a competitor that is not backed by `comparison_evidence.md`.
- The `gen_counts.py` script not existing or not being run as part of the pipeline.

**Phase to address:**
The comparison table phase. Treat it as a data pipeline output, not a prose-authored section. The evidence file is the human-review artifact for this section, equivalent to the blocking citation review in v13.0.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Copy-paste snippets from a REPL into `.tex` | Fast initial draft | Snippets diverge from tested code; stale on next API change | Never. Use `\verbatiminput` or `\lstinputlisting` from the validated script. |
| Hardcode coverage counts (437, 31) in prose | No setup overhead | Counts drift silently on every future milestone | Never. Derive via `gen_counts.py` from `_capability_map.json`. |
| Use biblatex + biber with tectonic | Modern bibliography system | Silent empty bibliography in tectonic CI; undetected until human reads the PDF | Never with tectonic. Use natbib + BibTeX. |
| Commit figures as PNG | Smaller files, simpler pipeline | Byte-non-deterministic across FreeType versions; spurious CI diffs | Acceptable only if the CI environment is Docker-pinned with an exact FreeType version. Otherwise, prefer PDF with `metadata={'CreationDate': None}`. |
| Use `np.random` without seeding before figure generation | Faster initial prototyping | Different figure on every run; non-reproducible artifact | Never in `paper/code/`. Always seed at the top of every script. |
| Skip the arXiv source-package test (clean-dir pdflatex run) | Saves one build step | Submission fails on arXiv with a missing-file or format error | Never. This test costs 5 minutes and prevents a submission failure. |
| Use relative paths (`../../docs/data/`) in pipeline scripts | Works locally immediately | Fails in CI when cwd differs | Never. Use `pathlib.Path(__file__).parent`-relative resolution. |
| Write comparison table from memory, no evidence file | Fast initial draft | Wrong negative claims about competitors; peer review rejection | Never. The evidence file is required before the table is finalized. |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| tectonic + bibliography | Using `\usepackage{biblatex}` → silent unprocessed citations | Use natbib (`\usepackage[numbers]{natbib}`, `\bibliography{refs}`); commit `refs.bib` (not just `.bbl`) |
| arXiv submission package | Including intermediate files (`.aux`, `.log`) or EPS figures | Include only `.tex`, `refs.bib`, `paper/figures/*.pdf`, custom `.sty`; exclude all build artifacts |
| matplotlib + CI | Using default backend (non-Agg) in headless CI | Set `MPLBACKEND=Agg` in the CI environment or call `matplotlib.use('Agg')` before any other matplotlib import |
| matplotlib + PDF determinism | PDF output contains `CreationDate` timestamp | `fig.savefig("out.pdf", metadata={"CreationDate": None})` |
| matplotlib + fonts | Using system fonts that differ between macOS and Ubuntu | Use only DejaVu fonts (bundled with matplotlib); verify with `matplotlib.get_cachedir()` |
| `_capability_map.json` + paper counts | Hardcoding counts derived from the map | Write `gen_counts.py` that reads the map and emits `\newcommand` macros; include in LaTeX via `\input{counts}` |
| `_references_map.json` + bibliography | Manually curating `refs.bib` independently of `_references_map.json` | Generate `refs.bib` from `_references_map.json` via a script; regenerate on every pipeline run |
| maturin dev install + CI | CI installing fdars from PyPI (stale wheel) | CI job must run `maturin develop` before running the pipeline; lock to the exact repo state |

---

## "Looks Done But Isn't" Checklist

- [ ] **Snippet execution gate:** Every code block in `paper.tex` has a corresponding executed script in `paper/code/`. Run `python paper/code/run_all.py` in a clean venv with `maturin develop` — zero errors required.
- [ ] **Coverage counts derived:** `paper/code/gen_counts.py` runs and emits `paper/counts.tex`; the pipeline runs `gen_counts.py` before LaTeX compile; no literal integer callable/module counts appear in `paper.tex`.
- [ ] **Comparison table evidence file:** `paper/code/comparison_evidence.md` exists with a row for every comparison table cell, citing the source (URL + version + date checked). Human-reviewed at close gate.
- [ ] **Bibliography compiles with bibtex (not biber):** `tectonic paper.tex` produces a PDF where `grep -c '^\[\|^\\bibitem' paper.bbl` returns > 0; no `[?]` citations visible.
- [ ] **Figure determinism gate:** After running `python paper/code/run_all.py` twice from scratch, `git diff paper/figures/` is empty.
- [ ] **No PNG committing without FreeType pin:** If PNG figures are committed, the CI Docker image's FreeType version is pinned and documented.
- [ ] **arXiv package test:** The arXiv zip is extracted into a clean temp directory; `pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex` succeeds from that directory.
- [ ] **No absolute or cwd-relative dataset paths:** Every `open(...)` or `np.loadtxt(...)` in `paper/code/` uses a path anchored to `pathlib.Path(__file__).parent`.
- [ ] **No `\today` in manuscript:** The submission date is hardcoded or uses a version macro.
- [ ] **Figures committed in PDF format:** `ls paper/figures/*.eps` returns nothing; `ls paper/figures/*.pdf` returns all figure files.
- [ ] **RNG seeded in every figure script:** `grep -L 'np.random.seed\|default_rng' paper/code/*.py` returns empty (all scripts seed RNG before use).
- [ ] **`MPLBACKEND=Agg` enforced:** The runner sets `os.environ['MPLBACKEND'] = 'Agg'` before importing matplotlib, or the CI job sets `MPLBACKEND=Agg` in the environment.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Stale snippet discovered post-submission | HIGH (requires arXiv replacement) | Fix the snippet script, re-run the pipeline to regenerate figures, update the paper.tex fragment, submit a v2 replacement to arXiv; if peer review is in progress, notify the editor |
| Coverage count drift discovered | LOW | Regenerate `counts.tex` via `gen_counts.py`, recompile, re-submit the arXiv v2; no code change needed if the `\input{counts}` pattern was established correctly |
| Wrong competitor comparison claim discovered | MEDIUM | Update the evidence file, correct the table cell, add the version qualifier, resubmit; if already cited, issue an arXiv replacement with a note in the revision history |
| biblatex/biber silent failure discovered | MEDIUM | Switch to natbib + BibTeX (a structural change but localised to the bibliography sections); regenerate the bib file; re-run tectonic; verify PDF bibliography is populated |
| Non-deterministic figures discovered | MEDIUM | Identify the non-deterministic source (seed, font, backend); apply the fix; re-run the pipeline; commit updated figures; verify `git diff paper/figures/` is empty before re-submission |
| arXiv package fails on submission | LOW-MEDIUM | Run the clean-dir pdflatex test locally to reproduce the error; add the missing file or convert the wrong-format figure; repackage and resubmit |
| "Works on my machine" environment failure in CI | MEDIUM | Audit the requirements.txt for unpinned deps; add `maturin develop` to CI job; fix any relative path issues; re-run the full pipeline in CI |

---

## Pitfall-to-Phase Mapping

| Pitfall | Severity | Prevention Phase | Verification |
|---------|----------|------------------|--------------|
| Stale API snippets | CRITICAL — invalidates reproducibility claim | Reproducible artifact phase: establish runner + `\verbatiminput` pattern before any snippets are written | Pipeline runs clean from fresh venv; `run_all.py` zero errors in CI |
| Coverage-count drift | HIGH | Manuscript scaffold phase: `gen_counts.py` + `\input{counts}` pattern before any coverage claims are written | `counts.tex` regenerated in every pipeline run; no literal integers for callable/module counts in `.tex` |
| Inaccurate competitor comparison | HIGH — peer review rejection risk | Comparison table phase: evidence file written and human-reviewed before `.tex` table is finalized | Blocking human review of `comparison_evidence.md` against current competitor docs |
| matplotlib non-determinism | HIGH | Reproducible artifact phase: determinism requirements in phase plan before scripts are written | `git diff paper/figures/` is empty after two fresh pipeline runs; CI gate checks this |
| tectonic biblatex silent failure | HIGH | Manuscript scaffold phase: choose natbib + BibTeX before first commit | PDF has no `[?]` citations; `.bbl` file is non-empty; reference count asserted in CI |
| arXiv package not self-contained | MEDIUM | Close gate: arXiv package test as explicit close-gate step | Clean-dir `pdflatex + bibtex` succeeds from extracted submission zip |
| "Works on my machine" environment | HIGH | Reproducible artifact phase: repo-root path resolution + pinned requirements + `maturin develop` in phase plan | CI runs the full pipeline with `maturin develop`; outputs match committed figures |
| Coverage-map sync drift | MEDIUM | Comparison table phase: `gen_counts.py` derives comparison claims; evidence file gated | `gen_counts.py` runs as part of pipeline; evidence file human-reviewed at close |

---

## Sources

- arXiv submission requirements: [Submit TeX/LaTeX — arXiv info](https://info.arxiv.org/help/submit_tex.html) (MEDIUM confidence — official arXiv documentation)
- arXiv format policies: [Policies for Format Requirements — arXiv info](https://info.arxiv.org/help/policies/format_requirements.html)
- tectonic biblatex issues: [GitHub issue #35](https://github.com/tectonic-typesetting/tectonic/issues/35), [#53](https://github.com/tectonic-typesetting/tectonic/issues/53), [#866](https://github.com/tectonic-typesetting/tectonic/issues/866) (MEDIUM confidence — verified against multiple tectonic issues describing the same failure)
- matplotlib determinism: [New in Matplotlib 2.1.0 — svg.hashsalt + PDF CreationDate](https://matplotlib.org/stable/users/prev_whats_new/whats_new_2.1.0.html); matplotlib FreeType pinning for image tests (from matplotlib source and docs) (MEDIUM confidence — official matplotlib documentation)
- matplotlib fonts: [Fonts in Matplotlib](https://matplotlib.org/stable/users/explain/text/fonts.html) — FreeType version determines glyph rasterization
- FDApy paper (style target): [arXiv:2101.11003](https://arxiv.org/abs/2101.11003), Golovkine 2021/2024 — 18 pages, 11 figures; revised 3 years after submission (LOW confidence — abstract-level analysis only, full PDF not parsed)
- scikit-fda paper: [arXiv:2211.02566](https://arxiv.org/pdf/2211.02566) — used for competitor comparison baseline (MEDIUM confidence)
- JOSS review criteria: [Review criteria — JOSS](https://joss.readthedocs.io/en/latest/review_criteria.html) — requires explicit comparison with related software (MEDIUM confidence)
- Project history: v13.0 code-review loop caught 9 citation bugs; v6.0 blocking human diagram review caught inverted hypograph/epigraph asymmetry — established pattern for human-gate effectiveness at catching accuracy errors that automated gates miss
- Codebase: `python/fdars/_capability_map.json` — 31 modules, 437 callables (verified 2026-09-08 via `python3 -c "import json; cm=json.load(...)"`)
- Codebase: `python/fdars/_references_map.json` — source of truth for bibliography; `gen_refs_bib.py` (or equivalent) must be the paper's `.bib` generation path

---
*Pitfalls research for: Software paper + reproducible artifact (v14.0 — fdars arXiv preprint)*
*Researched: 2026-09-08*
