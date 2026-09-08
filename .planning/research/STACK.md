# Stack Research

**Domain:** Academic software paper authoring — arXiv preprint + reproducible figure/table pipeline
**Researched:** 2026-09-08
**Confidence:** MEDIUM (arXiv rules verified against official docs; tectonic CI verified against action README; matplotlib patterns from official docs + community)

---

## Scope

This stack covers exactly what v14.0 needs to add to the existing `fdars` / `pyfda` repo:

1. LaTeX manuscript in-repo (`paper/`)
2. PDF compile in CI — no local TeX toolchain installed
3. Reproducible figure/table pipeline in Python (one-command runner)
4. `paper/refs.bib` generated from `_references_map.json`
5. `CITATION.cff` at repo root

Nothing below changes the existing `fdars` package, docs build, or CI matrix.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| LaTeX `article` class | — | Document class | Plain `article` is what arXiv actually compiles; no extra `.sty` gymnastics, no venue lock-in, smaller submission zip |
| `natbib` + BibTeX | bundled with tectonic | Citations and bibliography | Tectonic handles BibTeX natively and reliably; natbib gives author-year or numeric cite styles with one option; no version-mismatch risk (unlike biber) |
| `graphicx` | bundled | Figure inclusion | Standard arXiv-required package for `\includegraphics` |
| `hyperref` | bundled | Clickable DOIs/URLs in PDF | Essential for a software paper; works transparently under PDFLaTeX |
| `booktabs` | bundled | Publication-quality tables | Single package, no dependencies; produces the horizontal-rule style expected in software papers |
| tectonic | 0.17.x (July 2026) | CI PDF compile | Single Rust binary; auto-downloads packages on first run; no local TeX install needed; the GitHub Action (`wtfjoke/setup-tectonic@v4`) is a fast JS action, not a slow Docker container |
| matplotlib | 3.6+ (already in `.venv`) | Figure generation | Already installed; Agg backend is headless and deterministic |
| Python | 3.9+ (repo standard) | Reproducible pipeline runner | No new runtime; uses the existing `.venv` |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `numpy` | already installed | Data generation, seeding, table values | All figure scripts |
| `scipy` | already installed | Statistical computations in figures | When figures need smoothing / PDF curves |
| `cffconvert` | latest PyPI | Validate `CITATION.cff` schema | Run once locally: `cffconvert --validate` |

No new runtime dependencies for the pipeline — it uses the existing `.venv`.

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `wtfjoke/setup-tectonic@v4` | GitHub Action — installs tectonic binary | Pin `tectonic-version: "0.17.1"` once tested; cache `~/.cache/Tectonic` |
| `actions/cache@v4` | Cache tectonic package downloads | Key on `${{ hashFiles('paper/**/*.tex') }}` — avoids re-downloading TeX packages |
| `actions/upload-artifact@v4` | Upload compiled PDF from CI | Allows downloading the PDF from the Actions UI |
| Makefile (single file) | One-command pipeline runner | `make paper-figures` generates all figures; `make paper-pdf` also builds bib + compiles |
| `python paper/code/gen_refs_bib.py` | Generate `paper/refs.bib` from `_references_map.json` | Pure stdlib, no deps beyond Python 3.9 |

---

## Detailed Decisions

### 1. Document Class: plain `article`, not an arXiv template

Use `\documentclass[12pt]{article}` with a minimal preamble. Rationale:

- arXiv compiles with TeX Live 2025 (default); plain `article` is always available
- The FDApy paper (arXiv:2101.11003, 18 pages, 11 figures) uses a plain class — the reference we are following
- Template packages like `arxiv.sty` (kourgeorge/arxiv-style) add cosmetic value only and introduce one more file to maintain
- Overleaf-friendly for human co-author editing: no custom `.sty` files to synchronize
- If submitting to a venue later, swapping `\documentclass` is a one-line change

Optional style helpers that are safe to add (all in TeX Live): `geometry` (margins), `microtype` (better line-breaking), `xcolor` (colored text/rules), `subcaption` (sub-figures).

### 2. Bibliography: natbib + BibTeX, NOT biblatex + biber

Use `\usepackage{natbib}` with `\bibliographystyle{plainnat}` (or `unsrtnat` for submission order).

Why natbib, not biblatex:

- **Tectonic limitation:** tectonic has no native biber integration; the `setup-tectonic` action's `biber-version` parameter has documented version-mismatch failures (biblatex/biber version pinning fragile as of 2026). natbib+bibtex works out of the box with tectonic — no extra setup.
- **arXiv (as of Nov 2025):** arXiv now accepts raw `.bib` files and runs bibtex/biber automatically — so both approaches compile on submission. But the CI path is simpler with natbib because tectonic calls bibtex internally without any extra action configuration.
- **Software paper context:** natbib's `\citet{}` / `\citep{}` author-year style is standard in scientific software papers; no biblatex feature is needed.

`paper/refs.bib` is generated from `_references_map.json` (see Section 4) and committed. Regenerate when `_references_map.json` changes.

### 3. Figures: PDF (vector) for line plots, PNG-300 for rasterized outputs

arXiv accepts `.pdf`, `.png`, `.jpg` under PDFLaTeX. No on-the-fly conversion.

Rule:
- Functional data line plots → save as `.pdf` (vector, scales perfectly in print)
- Heatmaps / images / rasterized outputs → save as `.png` at 300 dpi
- Never `.eps` (that requires DVI mode, not PDFLaTeX)

All figures committed to `paper/figures/` so the LaTeX source compiles without running the pipeline (human read-through gate can compile offline via tectonic if desired).

### 4. arXiv Self-Containment Rules (verified Nov 2025)

- Submit: `paper/main.tex` + `paper/refs.bib` + `paper/figures/*.pdf` or `*.png`
- arXiv now runs bibtex automatically from `.bib` — no need to pre-compile `.bbl`
- arXiv has no subdirectory support in the submission zip; flatten for submission or use `\graphicspath{{figures/}}` which arXiv resolves
- Do NOT include: `.aux`, `.log`, `.toc`, `.pdf` (the compiled output), unused files
- Avoid `minted.sty` — hidden `.pyg` directory structure breaks post-announcement processing; use `listings` or `verbatim` for code snippets in the paper

### 5. CI PDF Compile: tectonic via `wtfjoke/setup-tectonic@v4`

Tectonic is the right choice here because:
- Single binary, downloaded by the JS action in seconds (no Docker pull, no TeX Live apt-install)
- Auto-downloads only the TeX packages actually used — fast after first run with caching
- Actively maintained; v0.17.0 released July 2026
- bibtex backend works natively without extra configuration

TeX Live container (`xu-cheng/latex-action`) is the alternative — supports everything but takes 2–4 min just for the Docker image pull + TeX Live extraction. For a soft gate (CI PDF compile is secondary to the Python pipeline gate), tectonic's speed is the deciding factor.

**Minimal CI recipe** (add as a new job in `.github/workflows/paper.yml`):

```yaml
name: Paper PDF

on:
  push:
    paths:
      - "paper/**"

jobs:
  paper-pdf:
    name: Compile paper PDF
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with:
          path: ~/.cache/Tectonic
          key: ${{ runner.os }}-tectonic-${{ hashFiles('paper/**/*.tex', 'paper/**/*.bib') }}
          restore-keys: ${{ runner.os }}-tectonic-
      - uses: wtfjoke/setup-tectonic@v4
        with:
          tectonic-version: "0.17.1"   # pin after first green run
      - name: Compile paper
        run: tectonic --chatter minimal paper/main.tex
      - uses: actions/upload-artifact@v4
        with:
          name: paper-pdf
          path: paper/main.pdf
```

Notes:
- `tectonic paper/main.tex` places the output PDF next to the `.tex` file (`paper/main.pdf`)
- `--chatter minimal` suppresses package-download noise from logs
- Path filter (`paths: paper/**`) means this job only runs when paper files change — does not slow down every Rust/Python CI run
- Pin `tectonic-version` after the first green run to get reproducible builds

### 6. Reproducible Figure/Table Pipeline: plain Python script + Makefile

**Recommendation: a single `paper/code/build_figures.py` script invoked via a Makefile target.**

Why not Snakemake or DVC:
- Snakemake is a heavy dependency (adds ~20 deps) that brings no benefit for a linear, single-machine pipeline
- DVC requires a data remote; overkill for committed PNG/PDF outputs
- A plain Python script with explicit section ordering is self-documenting and requires only the existing `.venv`

Makefile at repo root wraps the pipeline:

```makefile
.PHONY: paper-figures paper-bib paper-pdf paper-check

paper-figures:
	. .venv/bin/activate && PYTHONPATH=. python paper/code/build_figures.py

paper-bib:
	. .venv/bin/activate && python paper/code/gen_refs_bib.py

paper-pdf: paper-bib paper-figures
	tectonic paper/main.tex   # requires tectonic on PATH; CI gate only

paper-check:
	. .venv/bin/activate && python -c "import fdars; print('fdars OK, version:', fdars.__version__)"
	. .venv/bin/activate && cffconvert --validate
```

**Determinism pattern for `build_figures.py`:**

```python
import matplotlib
matplotlib.use("Agg")                         # must be before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import os

# Shared style: fixed once at top, never overridden per-figure
plt.rcParams.update({
    "figure.figsize": (5.5, 3.5),             # fits single-column at 12pt
    "figure.dpi": 150,
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "lines.linewidth": 1.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

SEED = 42                                      # single global seed
OUT  = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUT, exist_ok=True)

def savefig(fig, name, fmt="pdf"):
    path = os.path.join(OUT, f"{name}.{fmt}")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path}")

# --- Each figure function resets seed at entry so order does not matter ---
def fig_canadian_curves():
    np.random.seed(SEED)
    import fdars
    fd = fdars.datasets.load_canadian_weather()
    fig, ax = plt.subplots()
    # ... plotting code ...
    savefig(fig, "fig_canadian_curves")

if __name__ == "__main__":
    fig_canadian_curves()
    # ... call all figure functions ...
```

Key rules for determinism:
1. `matplotlib.use("Agg")` before any `import matplotlib.pyplot`
2. `plt.rcParams.update({...})` once at module level — never inside per-figure functions
3. `np.random.seed(SEED)` at the top of each figure function (not once globally, so figure order is irrelevant)
4. `fig.savefig(..., dpi=300, bbox_inches="tight")` + `plt.close(fig)` — never `plt.show()`
5. Use `fdars.datasets.load_canadian_weather()` etc. — existing `docs/data/` datasets via the existing loader, not raw CSV reads

**LaTeX table emission pattern:**

```python
def emit_table(rows, headers, path):
    """Write a LaTeX tabular fragment to path (include via \input{} in main.tex)."""
    col_fmt = "l" + "r" * (len(headers) - 1)
    lines = [
        r"\begin{tabular}{" + col_fmt + "}",
        r"\toprule",
        " & ".join(headers) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(str(c) for c in row) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    with open(path, "w") as f:
        f.write("\n".join(lines))
```

Include in `main.tex` as `\input{tables/comparison}` (tectonic resolves relative to the `.tex` file).

### 7. Generating `paper/refs.bib` from `_references_map.json`

The `_references_map.json` (57 papers) has all fields needed for valid BibTeX entries. The paper key (e.g. `fraiman_muniz_2001`) becomes the BibTeX cite key — stable and human-readable.

JSON field → BibTeX mapping:

| JSON field | BibTeX field | Notes |
|-----------|-------------|-------|
| `title` | `title` | Direct |
| `authors` list | `author` | Join with ` and ` |
| `year` | `year` | Direct |
| `doi` | `doi` + `url` | `url = {https://doi.org/{doi}}` if doi present |
| `url` | `url` | Fallback if no doi |
| `type = "journal"` | `@article` | |
| `type = "book"` | `@book` | |
| `type = "conference"` | `@inproceedings` | |
| `type = "preprint"` | `@misc` | `howpublished = {\url{...}}` |

Journal/venue fields are absent from the JSON (the map is paper-centric, not publication-centric). For `@article` entries without a `journal` field in the JSON, either add a `journal` field to select JSON entries during curation, or use `@misc` uniformly — the curation step should add the venue during bib generation authoring. This is a one-time authoring task, not an automated gap.

Run `make paper-bib` to regenerate. Commit `paper/refs.bib` — it is the source of truth for the LaTeX source.

### 8. CITATION.cff

File location: `CITATION.cff` at repo root (GitHub auto-detects and shows "Cite this repository").

Schema version: `1.2.0` (current stable).

Minimal template for software-with-paper pattern:

```yaml
cff-version: 1.2.0
message: "If you use fdars, please cite both the software and the paper."
title: "fdars: Functional Data Analysis in Rust with Python bindings"
version: "0.12.0"
date-released: "2026-09-08"
authors:
  - family-names: Müller
    given-names: Simon
    email: sm@data-zoo.de
repository-code: "https://github.com/simonm/pyfda"
license: MIT
keywords:
  - functional data analysis
  - rust
  - python
  - pyO3
preferred-citation:
  type: article
  title: "fdars: A Rust-Backed Python Package for Functional Data Analysis"
  authors:
    - family-names: Müller
      given-names: Simon
  year: 2026
  url: "https://arxiv.org/abs/XXXX.XXXXX"   # fill in after arXiv submission
```

Validate locally: `pip install cffconvert && cffconvert --validate`.

Update `version` and `date-released` at each PyPI release. Fill in the arXiv `url` (and add `doi` if a Zenodo record is created) after first submission.

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| `article` class | `arxiv.sty` template | Adds a `.sty` file to maintain; no substantive gain for a preprint |
| `natbib` + bibtex | `biblatex` + biber | Tectonic's biber support fragile; version mismatches documented in setup-tectonic issues |
| tectonic + `setup-tectonic@v4` | `xu-cheng/latex-action` (TeX Live Docker) | Docker pull + TeX Live extraction takes 2–4 min; tectonic is faster for this use case |
| tectonic + `setup-tectonic@v4` | `apt-get install texlive-full` in CI | Full TeX Live is ~5 GB; excessively slow for a single-document gate |
| Plain Python script + Makefile | Snakemake | ~20 extra deps; linear pipeline gains nothing from DAG scheduling |
| Plain Python script + Makefile | `showyourwork` | Snakemake-based; same dependency overhead; designed for data-heavy reproducible papers |
| PDF figures (vector) | EPS figures | EPS requires DVI mode; PDFLaTeX requires PDF/PNG/JPEG |
| Committed `paper/refs.bib` | Runtime-only bib generation | Committed bib makes LaTeX source self-contained and human-reviewable without running Python |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `minted` package | Hidden `.pyg` directory breaks arXiv post-announcement processing | `listings` or `verbatim` |
| `biber` backend | Version-mismatch failures with tectonic; fragile in CI | natbib + bibtex |
| `plt.show()` in pipeline scripts | Hangs headless CI runners | `fig.savefig()` then `plt.close(fig)` only |
| EPS/PS figures | Requires DVI mode, not PDFLaTeX | PDF (vector) or PNG (300 dpi) |
| DVI mode LaTeX | arXiv uses PDFLaTeX by default | PDFLaTeX |
| `numpy.random.RandomState` legacy API | Deprecated path | `np.random.seed(42)` global or `np.random.default_rng(42)` |
| Figure generation inside `if __name__ != "__main__"` guards | Prevents running from Makefile | Always use `if __name__ == "__main__": main()` pattern |
| Global mutable rcParams state shared across figure calls | Non-deterministic if figures import each other | Set rcParams once at module top; never per-figure |

---

## Recommended `paper/` Directory Layout

```
paper/
├── main.tex                   # master document
├── refs.bib                   # generated by gen_refs_bib.py; committed
├── figures/                   # committed PNG/PDF outputs from build_figures.py
│   ├── fig_canadian_curves.pdf
│   ├── fig_capability_coverage.pdf
│   └── ...
├── tables/                    # committed .tex fragments from build_figures.py
│   ├── comparison.tex         # \input{tables/comparison} in main.tex
│   └── ...
└── code/
    ├── build_figures.py       # one-command runner: all figures + tables
    └── gen_refs_bib.py        # generates refs.bib from _references_map.json

# At repo root:
CITATION.cff
Makefile                       # paper-figures, paper-bib, paper-pdf, paper-check targets
```

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| tectonic 0.17.x | TeX Live ~2023 package snapshot (bundled) | Tectonic bundles its own package snapshot; pin version after first green CI run |
| `setup-tectonic@v4` | `actions/checkout@v4`, `actions/cache@v4` | All v4 for Node 20 runner compatibility |
| natbib | bibtex (bundled with tectonic) | No version constraints; stable for 20+ years |
| cff-version 1.2.0 | `cffconvert` ≥ 2.0 | `pip install cffconvert` for local validation |
| matplotlib 3.6+ | Python 3.9+ | Already satisfied by existing `.venv` |
| fdars 0.12.0 | numpy, scipy (already in `.venv`) | Pipeline uses existing package versions; no new installs |

---

## Sources

- [arXiv LaTeX submission page](https://info.arxiv.org/help/submit_tex.html) — TeX Live version, figure formats, .bib file support — LOW confidence (web, verified 2026-09-08)
- [arXiv blog: .bib file processing update Nov 2025](https://blog.arxiv.org/2025/11/05/attention-authors-updates-for-bib-file-processing-and-tex-in-arxiv-submissions) — .bib file processing change confirmed — LOW confidence (web)
- [setup-tectonic GitHub Action README](https://github.com/WtfJoke/setup-tectonic) — usage, biber-version param, caching — LOW confidence (web, verified 2026-09-08)
- [tectonic project homepage](https://tectonic-typesetting.github.io/en-US/) — version 0.17.0 confirmed July 2026 — LOW confidence (web)
- [tectonic issue #35](https://github.com/tectonic-typesetting/tectonic/issues/35), [discussion #930](https://github.com/tectonic-typesetting/tectonic/discussions/930), [setup-tectonic issue #194](https://github.com/WtfJoke/setup-tectonic/issues/194) — biber fragility confirmed — LOW confidence (web)
- [Citation File Format](https://citation-file-format.github.io/) + [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) — CFF 1.2.0 schema — LOW confidence (web)
- [Arbitrary-but-fixed: natbib vs biblatex](https://arbitrary-but-fixed.net/latex/latex%20alternatives/bibtex/2020/08/14/latex-alternatives-bibtex-part2-natbib-biblatex.html) — arXiv compatibility rationale — LOW confidence (web)
- [FDApy JOSS paper](https://joss.theoj.org/papers/10.21105/joss.07526) — reference paper structure (18pp, 11 figs) — LOW confidence (web)
- [matplotlib stable docs](https://matplotlib.org/stable/) — Agg backend, savefig, rcParams — MEDIUM confidence (context7)

---

*Stack research for: v14.0 fdars Software Paper — arXiv Preprint*
*Researched: 2026-09-08*
