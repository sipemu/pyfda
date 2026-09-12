# Phase 85: Manuscript Scaffold + Pipeline Infrastructure — Research

**Researched:** 2026-09-08
**Domain:** LaTeX scaffold (article + natbib + BibTeX), CITATION.cff v1.2.0, matplotlib deterministic PDF pipeline, Makefile one-command runner
**Confidence:** HIGH (all critical mechanics verified against repo files or official sources)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
All implementation choices are at Claude's discretion — pure infrastructure phase. The tooling decisions are already locked by the ROADMAP goal and success criteria:
- Plain `article` documentclass (NOT `amsart`, NOT `joss`, NOT `acmart`)
- natbib + BibTeX (NOT biblatex/biber — tectonic silently breaks biber in CI with `[?]` citations)
- No `\today`/timestamp macros in `paper.tex`
- CI-only tectonic PDF build via `wtfjoke/setup-tectonic@v4` (no local TeX toolchain assumed)
- matplotlib `Agg` backend, module-top rcParams, per-figure `np.random.seed`
- Deterministic PDF figures with suppressed `CreationDate` metadata
- Datasets resolved via `data_path()` helper pointing at `docs/data/` — zero duplication
- Author block: Simon Müller <sm@data-zoo.de>

### Claude's Discretion
All implementation choices not listed above. Follow ROADMAP success criteria and existing codebase conventions.

### Deferred Ideas (OUT OF SCOPE)
None — infrastructure phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MANU-01 | `paper/paper.tex` using `\documentclass{article}` with natbib + BibTeX, per-section `\input` stubs, no `\today`/timestamp macros, compiles to minimal PDF via CI tectonic | LaTeX scaffold structure; tectonic compile with BibTeX pass; `wtfjoke/setup-tectonic@v4` action |
| MANU-08 | `CITATION.cff` (v1.2.0, `cffconvert`-valid) with `preferred-citation` block for arXiv preprint, author block placeholdered to Simon Müller <sm@data-zoo.de> | CFF v1.2.0 schema; `preferred-citation` field types and required fields; `cffconvert --validate` command |
| PIPE-01 | `paper/code/paper_utils.py` reusing `scripts/docs_fig.py` `fig()`/colors and `data_path()` → `docs/data/`; one-command Makefile target; no data duplication | `scripts/docs_fig.py` API verified; `scripts/docs_data.py` path resolution pattern verified; Makefile structure |
| PIPE-02 | Deterministic figure generation: `Agg` backend, module-top rcParams, per-figure `np.random.seed`, PDF output with suppressed `CreationDate`; re-run leaves `git diff paper/figures/` empty | matplotlib PDF `metadata={"CreationDate": None}` verified; `svg.hashsalt` pattern from `docs_fig.py`; determinism gate design |
</phase_requirements>

---

## Summary

Phase 85 is a pure infrastructure / scaffold phase. It creates:
1. A `paper/` directory with a compiling minimal LaTeX manuscript skeleton (`paper.tex` + per-section `\input` stubs + `refs.bib`).
2. A `CITATION.cff` v1.2.0 file with a `preferred-citation` block for the forthcoming arXiv preprint.
3. A `paper/code/paper_utils.py` pipeline helper that reuses the established `scripts/docs_fig.py` API and resolves datasets from `docs/data/` without copying.
4. A Makefile target that regenerates all pipeline outputs deterministically in one command.

Every tooling decision is already locked (see User Constraints). The research task is to verify the exact mechanics so the planner can write correct tasks — not to choose among options.

**Primary recommendation:** Follow the established `scripts/docs_fig.py` determinism pattern exactly (Agg backend set at module top, `metadata={"Date": None}` for SVG / `metadata={"CreationDate": None}` for PDF, `svg.hashsalt` rcParam, per-figure `np.random.seed`). For the LaTeX PDF produced by tectonic in CI, determinism is achieved via `SOURCE_DATE_EPOCH` env var or tectonic's `-Z deterministic-mode` flag, not via `\pdfinfo` hacks.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| LaTeX manuscript skeleton | `paper/` (new top-level) | CI (compile gate) | Self-contained author artifact; CI only validates it compiles |
| Figure generation pipeline | `paper/code/` scripts | `paper/figures/` committed output | Scripts produce deterministic PDFs; committed figures are the artifact checked by `git diff` |
| Dataset access | `docs/data/` (existing canonical) | `paper/code/paper_utils.py` resolver | No copying; `data_path()` returns absolute path into `docs/data/` |
| Style / color palette | `scripts/docs_fig.py` (existing) | `paper/code/paper_utils.py` (imports) | Reuse, do not reimplement |
| CITATION.cff metadata | repo root | None | GitHub auto-surfaces root CITATION.cff; `cffconvert` validates in place |
| Makefile target | repo root `Makefile` (existing) | None | Extend existing Makefile; add `paper` targets |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| matplotlib | 3.10.8 (installed in `.venv`) | Deterministic figure generation to PDF | Already used throughout docs pipeline; Agg backend + `metadata` parameter suppresses CreationDate [VERIFIED: .venv] |
| numpy | (project dep) | RNG seeding, data arrays | Already a core dep; `np.random.seed` is the established docs seeding pattern |
| pandas | (project dep) | Dataset loading | `docs_data.py` loaders return `meta` as DataFrames; already a dep |

### Paper Pipeline
| Tool | Source | Purpose | Install |
|------|--------|---------|---------|
| `scripts/docs_fig.py` | repo — existing | `fig()` factory + FDARS_COLORS + rcParams + render() | No install — already on `PYTHONPATH` in docs build; `paper_utils.py` imports it directly |
| `scripts/docs_data.py` | repo — existing | Dataset loaders (`load_growth`, `load_canadian_weather`, etc.) | No install — same `PYTHONPATH=scripts` pattern |
| `cffconvert` | PyPI (`cffconvert==2.0.0`) | Validate CITATION.cff | `pip install cffconvert` — validation-only, not a runtime dep |
| `wtfjoke/setup-tectonic@v4` | GitHub Actions | CI PDF compile | Action step in `paper.yml` — no local install needed |

### CI BibTeX Workflow (wtfjoke/setup-tectonic@v4)
tectonic supports BibTeX natively via its `--pass bibtex_first` flag (V2 CLI) or by default in the V1 CLI. The `setup-tectonic@v4` action only requires `biber-version` if biber is used; for plain BibTeX, the action installs tectonic with no extra inputs. Tectonic downloads required TeX packages on-demand and caches them at `~/.cache/Tectonic` (Linux). [CITED: https://github.com/WtfJoke/setup-tectonic]

---

## Package Legitimacy Audit

> These are all existing, established packages — no new npm packages introduced. Python packages used are cffconvert (validation only, dev tool) and the project's existing matplotlib/numpy/pandas deps.

| Package | Registry | Age | Verdict | Disposition |
|---------|----------|-----|---------|-------------|
| matplotlib | PyPI | 20+ yrs | OK | Approved — core project dep |
| numpy | PyPI | 20+ yrs | OK | Approved — core project dep |
| pandas | PyPI | 15+ yrs | OK | Approved — core project dep |
| cffconvert | PyPI | ~5 yrs (2021) | OK | Approved — validation-only dev tool, official CFF project |

**Packages removed due to SLOP verdict:** none
**Packages flagged as suspicious (SUS):** none

---

## Architecture Patterns

### System Architecture Diagram

```
  ┌─────────────────────────────────────────────────────┐
  │  paper/code/paper_utils.py                          │
  │  (imports scripts/docs_fig.py via PYTHONPATH)       │
  │  - fig() + FDARS_COLORS + rcParams                  │
  │  - data_path() → docs/data/                         │
  └─────────────┬───────────────────────────────────────┘
                │ import
  ┌─────────────▼───────────────────────────────────────┐
  │  paper/code/<figure_script>.py                      │
  │  np.random.seed(N)  [per-figure]                    │
  │  f, ax = fig(); ...; savefig("../figures/X.pdf",    │
  │     metadata={"CreationDate": None})                │
  └─────────────┬───────────────────────────────────────┘
                │ writes
  ┌─────────────▼────┐    ┌────────────────────────────┐
  │ paper/figures/   │    │  paper/paper.tex           │
  │  X.pdf (committed│    │  \documentclass{article}   │
  │  deterministic)  │    │  \usepackage{natbib}       │
  └──────────────────┘    │  \input{sections/intro}    │
                          │  \bibliographystyle{plain} │
                          │  \bibliography{refs}       │
                          └─────────────┬──────────────┘
                                        │ compiled by
                          ┌─────────────▼──────────────┐
                          │  CI: tectonic (BibTeX pass)│
                          │  wtfjoke/setup-tectonic@v4 │
                          │  SOURCE_DATE_EPOCH or      │
                          │  -Z deterministic-mode     │
                          └────────────────────────────┘

  make paper  (one command)
  ├── python paper/code/<script>.py   (for each figure)
  └── tectonic paper/paper.tex        (CI only)
```

### Recommended Project Structure
```
paper/
├── paper.tex              # root manuscript (article class, natbib, \input stubs)
├── refs.bib               # generated in Phase 86 by gen_refs_bib.py; stub here
├── figures/               # committed deterministic PDFs
│   └── .gitkeep
├── sections/              # per-section stub .tex files \input-ed from paper.tex
│   ├── intro.tex
│   ├── design.tex
│   ├── represent.tex
│   ├── capabilities.tex
│   ├── comparison.tex
│   ├── casestudies.tex
│   └── availability.tex
└── code/                  # reproducible pipeline scripts
    ├── paper_utils.py     # shared helper: fig()/colors from docs_fig.py + data_path()
    └── .gitkeep           # figure scripts added in Phases 88/89

CITATION.cff               # at repo root (new)
```

### Pattern 1: paper_utils.py — Reuse docs_fig.py
**What:** Import `scripts/docs_fig.py` rather than reimplementing its fig factory, color palette, and rcParam block. Set up a `data_path()` helper that returns paths into `docs/data/`.
**When to use:** In every `paper/code/` figure script.
**Example:**
```python
# Source: scripts/docs_fig.py API (verified by reading the file)
# paper/code/paper_utils.py
"""Shared helpers for the paper figure pipeline.

Reuses scripts/docs_fig.py for figure style and docs/data/ for datasets.
This module must be importable with PYTHONPATH=scripts:paper/code.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make scripts/ importable when running from paper/code/ or repo root
_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Re-export the established docs_fig surface
from docs_fig import fig, FDARS_COLORS  # noqa: E402  [VERIFIED: scripts/docs_fig.py:43-84]

import matplotlib
matplotlib.use("Agg")  # already set in docs_fig import; explicit for clarity
import matplotlib.pyplot as plt  # noqa: E402


def data_path(name: str) -> Path:
    """Return absolute path to a dataset in docs/data/.

    No dataset is copied — the paper pipeline resolves against the
    canonical docs/data/ directory in the repository.
    """
    root = Path(__file__).resolve().parent.parent.parent
    p = root / "docs" / "data" / name
    if not p.exists():
        raise FileNotFoundError(f"dataset not found: {p}")
    return p


def save_figure(fig, path: str | Path) -> None:
    """Save figure as deterministic PDF (suppressed CreationDate).

    Equivalent of docs_fig.render() for the paper pipeline (file output
    instead of inline SVG). Sets metadata={"CreationDate": None} so that
    git diff paper/figures/ is empty on re-run.
    """
    fig.savefig(
        path,
        format="pdf",
        bbox_inches="tight",
        metadata={"CreationDate": None},  # [VERIFIED: matplotlib 3.10.8 PdfFile.__init__]
    )
    plt.close(fig)
```

### Pattern 2: CITATION.cff v1.2.0 with preferred-citation
**What:** A root `CITATION.cff` that describes the software (fdars) but directs citation to the arXiv preprint via the `preferred-citation` block.
**When to use:** Once; at repo root; validated with `cffconvert --validate`.

```yaml
# Source: CFF schema v1.2.0 — https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md
# [CITED: https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md]
cff-version: 1.2.0
message: "If you use fdars, please cite the software paper."
type: software
title: fdars
version: 0.12.0
date-released: "2026-09-08"
license: MIT
repository-code: "https://github.com/sipemu/pyfda"
url: "https://sipemu.github.io/pyfda/"
abstract: >
  fdars is a Python package for functional data analysis backed by a
  Rust computation core (fdars-core) via PyO3 zero-copy bindings.
  It covers FDA representation, smoothing, alignment, depth, inference,
  regression, clustering, and monitoring, with a scikit-learn-compatible
  estimator layer and a grounded AI advisor.
authors:
  - family-names: "Müller"
    given-names: "Simon"
    email: "sm@data-zoo.de"
keywords:
  - functional-data-analysis
  - FDA
  - Rust
  - PyO3
  - scikit-learn
preferred-citation:
  type: article          # use "article" for arXiv preprints / JOSS [CITED: CFF schema-guide]
  title: "fdars: Functional Data Analysis in Rust with Python Bindings"
  authors:
    - family-names: "Müller"
      given-names: "Simon"
      email: "sm@data-zoo.de"
  year: 2026
  # journal/doi/url populated when arXiv ID assigned (Phase 90)
  # Placeholder identifiers:
  identifiers:
    - type: url
      value: "https://github.com/sipemu/pyfda"
      description: "Repository (arXiv URL added at submission)"
```

> **Note on `preferred-citation` type:** The CFF schema-guide shows `type: generic` in its minimal example. For a journal article or arXiv preprint, use `type: article`. Valid types include: `article`, `book`, `software`, `conference-paper`, `report`, `generic`. [CITED: https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md]

### Pattern 3: Makefile target for paper pipeline
**What:** Extend the existing repo `Makefile` with `paper` targets. Mirror the existing `docs` / `docs-serve` pattern.
**When to use:** The one-command runner required by PIPE-01.

```makefile
# Add to existing Makefile — mirrors the docs targets above
# PYTHONPATH must include both scripts/ (for docs_fig) and paper/code/ (for paper_utils)
PAPER_PYTHONPATH := scripts:paper/code

.PHONY: paper paper-figures paper-validate-cff

paper-figures:  ## Regenerate all paper figures deterministically
    PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/gen_figures.py

paper-validate-cff:  ## Validate CITATION.cff with cffconvert
    cffconvert --validate

paper: paper-figures paper-validate-cff  ## Full one-command paper pipeline (figures + validation)
```

> **Note:** The PDF compile (`tectonic paper/paper.tex`) is CI-only (GATE-01, Phase 86). The local hard gate is `make paper` — figures regenerate deterministically, `git diff paper/figures/` must be empty. No local TeX toolchain is required. [VERIFIED: .planning/PROJECT.md, STATE.md decisions]

### Pattern 4: Deterministic matplotlib PDF
**What:** Suppress the `CreationDate` field in PDF metadata so re-runs produce byte-identical files.
**When to use:** In every `savefig` call that writes to `paper/figures/`.

The key parameter is `metadata={"CreationDate": None}` on `savefig`. This was introduced in matplotlib 2.1.0 and is confirmed in the installed version (3.10.8). [VERIFIED: /home/simonm/projects/rust/pyfda/.venv/lib/python3.14/site-packages/matplotlib/backends/backend_pdf.py — `PdfFile.__init__` docstring: "They can be removed by setting them to `None`." — `CreationDate` explicitly listed]

The SVG analog already used in `docs_fig.py` is `metadata={"Date": None}` on `figure.savefig(..., format="svg")`. [VERIFIED: scripts/docs_fig.py:99-104]

Additional rcParams that must be set at module top (already done in `docs_fig.py`, reused via import):
```python
# Already set by docs_fig.py — reused by paper_utils.py import:
# [VERIFIED: scripts/docs_fig.py:53-79]
plt.rcParams.update({
    "figure.figsize": (7.5, 4.0),
    "figure.dpi": 110,
    "savefig.transparent": True,
    "axes.prop_cycle": plt.cycler(color=FDARS_COLORS),  # FDARS_COLORS = ["#3f51b5", ...]
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.alpha": 0.22,
    "grid.linewidth": 0.7,
    "font.size": 11,
    "axes.titlesize": 12.5,
    "axes.titleweight": "600",
    "legend.frameon": False,
    "legend.fontsize": 9.5,
    "figure.autolayout": True,
    "svg.hashsalt": "fdars-docs",  # SVG determinism — not needed for PDF but harmless
})
```

### Pattern 5: LaTeX skeleton (MANU-01)
**What:** Minimal `paper.tex` with `\documentclass{article}`, natbib, BibTeX, section stubs, no timestamp macros.
**Key rules:**
- Never use `\today` — dates must be hardcoded strings or omitted.
- Use `\usepackage[numbers]{natbib}` (numeric style) or `\usepackage{natbib}` with `\bibliographystyle{plain}`.
- Use `\input{sections/<section>}` for each section stub — each stub file is an empty (or placeholder) `.tex` file for now.
- `refs.bib` is a stub for Phase 85; populated by `gen_refs_bib.py` in Phase 86.

```latex
% paper/paper.tex — minimal compiling skeleton
\documentclass[12pt,a4paper]{article}

% Bibliography: natbib + BibTeX (NOT biblatex/biber)
\usepackage[numbers,sort&compress]{natbib}

% Basic packages for a software paper
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{url}
\usepackage{graphicx}
\usepackage{amsmath}

\title{fdars: Functional Data Analysis in Rust with Python Bindings}
\author{Simon M\"{u}ller\\
  \texttt{sm@data-zoo.de}}
% No \date{\today} — no timestamp macros.
\date{}

\begin{document}
\maketitle
\begin{abstract}
  Placeholder abstract — expanded in Phase 88.
\end{abstract}

\input{sections/intro}
\input{sections/design}
\input{sections/represent}
\input{sections/capabilities}
\input{sections/comparison}
\input{sections/casestudies}
\input{sections/availability}

\bibliographystyle{plain}
\bibliography{refs}

\end{document}
```

Each `sections/*.tex` stub contains only a `\section{...}` heading and a placeholder paragraph — enough to compile without errors.

### Anti-Patterns to Avoid
- **`\usepackage{biblatex}` + `\addbibresource{}`:** Biber silently fails in tectonic CI producing `[?]` citations. Use `natbib` + `\bibliography{}` only. [CITED: PROJECT.md STATE.md decisions]
- **`\date{\today}` or `\pdfinfo{\CreationDate}`:** Embeds system time → non-deterministic. Use `\date{}` or a hardcoded string.
- **Copying CSVs into `paper/data/`:** Violates PIPE-01. Use `data_path()` to resolve into `docs/data/` at runtime.
- **Calling `plt.rcParams.update(...)` inside figure scripts instead of at module top:** RNG seeding must be per-figure (`np.random.seed`), but rcParams must be set at module import time for full reproducibility.
- **Using tectonic locally as the local gate:** The local gate is the Python pipeline only (`make paper` → `git diff paper/figures/` empty). PDF compile is CI-only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Figure style / color palette | Custom rcParams in each script | Import `fig`, `FDARS_COLORS` from `docs_fig.py` | Already established, maintained, and deterministic per FND-03 |
| Dataset loading | CSV reading inline in each script | `data_path()` + reuse `docs_data.py` loader pattern | Loaders already handle all 7 datasets with correct dtype and metadata alignment [VERIFIED: scripts/docs_data.py] |
| BibTeX bibliography | Hand-authored `refs.bib` | `gen_refs_bib.py` (Phase 86) from `_references_map.json` | `_references_map.json` has 57 papers, 243 callable→paper entries [VERIFIED: python/fdars/_references_map.json]; stub `refs.bib` in Phase 85, generate in Phase 86 |
| PDF metadata suppression | `\pdfinfo` LaTeX commands | `savefig(..., metadata={"CreationDate": None})` | Matplotlib-native; tested in 3.10.8; no LaTeX magic needed |
| CITATION.cff validation | Bespoke YAML validator | `cffconvert --validate` | Official tool from the CFF project; supports v1.2.0 |

**Key insight:** The docs pipeline already solved every reproducibility problem this phase needs. Copy the pattern, don't reinvent it.

---

## Critical Technical Findings

### Finding 1: `scripts/docs_fig.py` API (verified in-file)
[VERIFIED: scripts/docs_fig.py:1-131]

The file exposes exactly:
- `fig(nrows=1, ncols=1, **kwargs)` → returns `(figure, axes)` via `plt.subplots()` [VERIFIED: scripts/docs_fig.py:82-84]
- `render(figure=None) -> str` → saves to SVG with `metadata={"Date": None}`, strips preamble, wraps in `<div class="fdars-figure">` [VERIFIED: scripts/docs_fig.py:87-111]
- `fast(full, fast_value)` → returns `fast_value` if `DOCS_FAST` env var is set [VERIFIED: scripts/docs_fig.py:114-131]
- `FDARS_COLORS` → list of 7 hex colors: `["#3f51b5", "#e8710a", "#198754", "#dc3545", "#6f42c1", "#0dcaf0", "#6c757d"]` [VERIFIED: scripts/docs_fig.py:43-51]
- Module-level `matplotlib.use("Agg")` call (before plt import) [VERIFIED: scripts/docs_fig.py:38-39]
- Module-level `plt.rcParams.update({...})` with all the style settings [VERIFIED: scripts/docs_fig.py:53-79]

**For paper_utils.py:** Import `fig` and `FDARS_COLORS` directly. The SVG-specific `render()` function is NOT needed — the paper pipeline writes PDF files. Define a new `save_figure()` that calls `savefig(..., format="pdf", metadata={"CreationDate": None})`.

The `render()` function in `docs_fig.py` already demonstrates the suppression pattern: `metadata={"Date": None}` for SVG. The PDF equivalent is `metadata={"CreationDate": None}`.

### Finding 2: matplotlib PDF metadata suppression
[VERIFIED: /home/simonm/projects/rust/pyfda/.venv — matplotlib 3.10.8, backend_pdf.py, PdfFile.__init__ docstring]

Verbatim from `PdfFile.__init__` docstring (line 13-15 of extracted source):
```
'Creator', 'Producer', 'CreationDate', 'ModDate', and
...
and 'CreationDate'. They can be removed by setting them to `None`.
```

Exact call: `fig.savefig("output.pdf", format="pdf", bbox_inches="tight", metadata={"CreationDate": None})`

This makes the PDF byte-identical across re-runs (no timestamp variation). FreeType/font variance is mitigated by using matplotlib's bundled fonts (Agg backend doesn't render to screen, avoiding system font substitution).

### Finding 3: Tectonic determinism for CI PDF
[CITED: https://tectonic-typesetting.github.io/book/latest/v2cli/compile.html]

Two mechanisms:
1. **`SOURCE_DATE_EPOCH` env var** (recommended): sets the compilation timestamp to a fixed Unix epoch value. Tectonic respects this variable. Set in the `paper.yml` workflow step: `SOURCE_DATE_EPOCH: 0` (or the git commit time via `$(git log -1 --pretty=%ct)`).
2. **`-Z deterministic-mode` flag**: forces deterministic build environment at the cost of breaking SyncTeX auxiliary files.

**For this project:** The local gate is `git diff paper/figures/` (Python pipeline, no tectonic). The CI PDF compile via tectonic is a correctness gate (does it compile?), not a byte-identity gate. Setting `SOURCE_DATE_EPOCH` in the CI step is sufficient and recommended for good practice.

**No `\pdfinfo` hacks needed** — the LaTeX-level suppression is unnecessary because matplotlib handles figure determinism, and tectonic handles PDF timestamp via `SOURCE_DATE_EPOCH`.

### Finding 4: docs/data/ dataset structure
[VERIFIED: scripts/docs_data.py:1-231, docs/data/README.md:1-107]

All datasets return `(argvals, X, meta)` tuples:

| Dataset | Loader | Shape | Notes |
|---------|--------|-------|-------|
| `growth.csv` | `load_growth()` | X: (93, 31) | 39 boys + 54 girls, ages |
| `canadian_weather.csv` / `canadian_weather_precip.csv` | `load_canadian_weather(variable=)` | X: (35, 365) | temperature or precipitation; 35 stations, 365 days |
| `tecator.csv` | `load_tecator()` | X: (240, 100) | NIR spectra; 850-1050 nm |
| `phoneme.csv` | `load_phoneme()` | X: (400, 256) | Balanced 80/class × 5 classes |
| `wine.csv` | `load_wine()` | X: (178, 13) | feature_names (not argvals); 3 cultivars |
| `sonar.csv` | `load_sonar()` | X: (208, 60) | 60 frequency bands; Mine/Rock labels |
| (synthetic) | `load_penicillin()` | X: (46, 200) | Deterministic, seed 20260805 |

`canadian_weather_precip.csv` structure: 365 rows × 36 columns (col `day` + 35 station names). The `load_canadian_weather(variable="precipitation")` loader handles it via `fname` dict dispatch. [VERIFIED: scripts/docs_data.py:59-88, docs/data/canadian_weather_precip.csv header row]

**`data_path()` implementation:** Resolve relative to `paper/code/paper_utils.py` → `../../../docs/data/`. Use `Path(__file__).resolve().parent.parent.parent / "docs" / "data" / name`. This matches the pattern in `docs_data.py` which uses `Path(__file__).resolve().parent.parent / "docs" / "data"` from `scripts/`. [VERIFIED: scripts/docs_data.py:27-28]

### Finding 5: _capability_map.json structure
[VERIFIED: python/fdars/_capability_map.json — read this session]

```
{
  "<module_name>": {
    "<callable_name>": {
      "purpose": "...",
      "sig": "...",
      "when": "..."
    }
  }
}
```

31 modules, 437 total callables. Module names: `['_Fdata', 'alignment', 'basis', 'classification', 'clustering', 'conformal', 'covariance', 'datasets', 'density_fda', 'depth', 'explain', 'famm', 'fdata', 'frechet', 'fts', 'inference', 'metric', 'metrics', 'multi_fdata', 'outliers', 'pace_fpca', 'regression', 'represent', 'scalar_on_function', 'scoring', 'seasonal', 'shapelet', 'simulation', 'smoothing', 'spm', 'tolerance']`

Coverage counts (needed by Phase 86's `assert_coverage.py`):
- Public modules: 30 (all except `_Fdata`)
- Total callables: 437 (all entries across all modules)
- `_Fdata` callable count: `len(d['_Fdata'])` = number of Fdata methods

### Finding 6: _references_map.json structure
[VERIFIED: python/fdars/_references_map.json — read this session]

```
{
  "papers": {
    "<paper_key>": {
      "title": "...",
      "authors": [...],
      "year": ...,
      "doi": "...",
      "url": "...",
      "type": "journal|preprint|...",
      "callables": [...],
      "cross_language": {...},
      "notes": "...",
      "curated": true|false
    }
  },
  "callable_index": {
    "<callable>": "<paper_key>"
  }
}
```

57 papers, 243 callable_index entries. This is the source for Phase 86's `gen_refs_bib.py`. In Phase 85, `refs.bib` is a stub file (empty or single placeholder entry).

### Finding 7: CITATION.cff v1.2.0 preferred-citation schema
[CITED: https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md]

Required fields in `preferred-citation`:
- `type` — one of: `article`, `book`, `software`, `conference-paper`, `report`, `generic`
- `authors` — list of author objects (each with `family-names`, `given-names`)
- `title` — string

Optional fields for an arXiv preprint (type: article):
- `year`, `journal` (use "arXiv preprint" as placeholder), `doi`, `url`
- `identifiers` — list of `{type: url, value: ..., description: ...}` for the arXiv link

Validation command: `cffconvert --validate` (reads `./CITATION.cff` by default) [CITED: https://pypi.org/project/cffconvert/]

### Finding 8: wtfjoke/setup-tectonic@v4 for BibTeX
[CITED: https://github.com/WtfJoke/setup-tectonic]

For plain BibTeX (not biber), the action needs no special inputs:
```yaml
- uses: WtfJoke/setup-tectonic@v4
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
- name: Compile PDF
  env:
    SOURCE_DATE_EPOCH: 0
  run: |
    tectonic paper/paper.tex
```

Tectonic runs multiple passes automatically (including BibTeX when a `.bib` file is referenced) in its default V1 CLI mode. The GitHub token is needed to avoid rate-limiting when downloading TeX packages. Tectonic caches packages at `~/.cache/Tectonic` (Linux); the action sets up caching automatically using `hashFiles('**/*.tex')` as the cache key. [CITED: https://github.com/WtfJoke/setup-tectonic/blob/main/README.md]

**No `biber-version` input is needed** for BibTeX (biber-version is only for biber). This is a deliberate choice documented in the project decisions. [VERIFIED: STATE.md decisions]

---

## Common Pitfalls

### Pitfall 1: biblatex/biber instead of natbib/BibTeX
**What goes wrong:** tectonic in CI produces `[?]` for all citations — silently, no error.
**Why it happens:** tectonic's bundle does not ship biber, and biber requires a separate install step. Even with `wtfjoke/setup-tectonic@v4`'s `biber-version` input, the tectonic+biber integration is fragile.
**How to avoid:** Use `\usepackage{natbib}` + `\bibliographystyle{plain}` + `\bibliography{refs}`. Never use `\usepackage{biblatex}` or `\addbibresource`.
**Warning signs:** `[?]` in compiled PDF; biber errors in CI log.

### Pitfall 2: matplotlib PDF timestamp non-determinism
**What goes wrong:** `git diff paper/figures/` is always non-empty even when figure code is unchanged. `git status` shows all PDFs modified.
**Why it happens:** matplotlib embeds `CreationDate` (current timestamp) in PDF metadata by default.
**How to avoid:** Always call `savefig(..., metadata={"CreationDate": None})`. Never call `savefig` without this parameter for committed PDF figures.
**Warning signs:** `git diff --stat` shows `.pdf` files changing on every `make paper` run.

### Pitfall 3: RNG seeding at wrong scope
**What goes wrong:** Figure output is non-deterministic between runs (different random sampling, different layout).
**Why it happens:** `np.random.seed` is called inside a loop or after the random operations have already begun.
**How to avoid:** `np.random.seed(N)` at the top of each figure script (module top or immediately before the first stochastic call). Use a different but fixed seed per figure script.
**Warning signs:** `git diff` shows figures changing even though no code changed.

### Pitfall 4: PYTHONPATH not including both `scripts/` and `paper/code/`
**What goes wrong:** `from docs_fig import fig` raises `ModuleNotFoundError` when running figure scripts.
**Why it happens:** `scripts/docs_fig.py` is only importable when `scripts/` is on `PYTHONPATH`. Paper scripts live in `paper/code/`, which is a different directory.
**How to avoid:** Set `PYTHONPATH=scripts:paper/code` in the Makefile target (or use the sys.path injection pattern in `paper_utils.py`). The Makefile's existing `export PYTHONPATH := scripts` only covers docs targets; paper targets need the extended path.
**Warning signs:** `ModuleNotFoundError: No module named 'docs_fig'` when running `make paper-figures`.

### Pitfall 5: Absolute CITATION.cff validation failure on placeholder DOI
**What goes wrong:** `cffconvert --validate` fails because the `preferred-citation` DOI or identifier value doesn't conform to the schema.
**Why it happens:** The DOI/arXiv ID is not assigned yet at Phase 85; placeholder strings like `"TBD"` may not be valid URL syntax.
**How to avoid:** Either (a) omit the `doi` field entirely until Phase 90 when the arXiv ID is assigned, or (b) use a valid `identifiers` entry with `type: url` pointing to the repository. Do not put `"TBD"` as a DOI value — it will fail schema validation.
**Warning signs:** `cffconvert --validate` exits non-zero with a schema error mentioning `doi` or `identifiers`.

### Pitfall 6: `\today` in section stubs
**What goes wrong:** Section stub files compiled by tectonic embed the current date — determinism broken at the LaTeX level.
**Why it happens:** Authors habitually write `\date{\today}` or reference `\today` in headers.
**How to avoid:** All section stub `.tex` files must not contain `\today`, `\currenttime`, or any dynamic date/time macro. Use `\date{}` (empty date) in `paper.tex`.

---

## Runtime State Inventory

> SKIPPED — this is a greenfield phase creating new files only. No rename/refactor/migration involved.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python + venv | Figure pipeline | ✓ | 3.14 (venv) | — |
| matplotlib | PIPE-02 figure output | ✓ | 3.10.8 (in .venv) | — |
| numpy | RNG seeding, data arrays | ✓ | (project dep) | — |
| pandas | Dataset loading | ✓ | (project dep) | — |
| tectonic | MANU-01 PDF compile | ✗ (not local) | — | CI-only via wtfjoke/setup-tectonic@v4 — by design |
| cffconvert | MANU-08 validation | ✗ (not local) | — | Install dev-only: `pip install cffconvert` |
| biber | Not needed | ✗ | — | Not required — using BibTeX |

**Missing dependencies with no fallback:** none (tectonic is intentionally CI-only per locked decision)

**Missing dependencies with fallback / installation step:**
- `cffconvert` — not installed; one-off `pip install cffconvert` in the dev venv for local validation; not needed in production.

---

## Security Domain

> `security_enforcement: true` in config.json. This phase creates no network services, no authentication, no user input handling, and no dynamic code execution. It is a file-creation phase (LaTeX, YAML, Python helpers, Makefile).

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | n/a (no auth surface) |
| V3 Session Management | No | n/a |
| V4 Access Control | No | n/a |
| V5 Input Validation | Partial | `data_path()` validates file existence before returning path; no user-controlled input |
| V6 Cryptography | No | n/a |

**Applicable threat patterns:**
- Path traversal in `data_path(name)`: mitigate by rejecting `name` values containing `..` or absolute paths. The helper should only resolve names against the fixed `docs/data/` directory.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `biber` bibliography processor | `BibTeX` (plain) | Locked at v14.0 init (tectonic incompatibility) | Simpler, tectonic-compatible |
| `\date{\today}` in papers | `\date{}` (empty) | v14.0 MANU-01 requirement | Deterministic compiled PDF |
| Manual bibliography | `gen_refs_bib.py` from `_references_map.json` (Phase 86) | v14.0 | Single-source-of-truth |
| PDF with embedded timestamp | `metadata={"CreationDate": None}` | matplotlib 2.1.0+ | Byte-identical git-committable figures |

**Deprecated/outdated:**
- `pdfprivacy` LaTeX package: older approach to suppress PDF metadata via LaTeX; superseded by matplotlib's `metadata` parameter for figure files and `SOURCE_DATE_EPOCH` for the compiled LaTeX PDF.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `wtfjoke/setup-tectonic@v4` is the latest stable version at execution time | Standard Stack / Pattern 3 | A newer version (v5) might have different input names — verify action version before writing `paper.yml` |
| A2 | Tectonic automatically runs BibTeX when a `.bib` file is referenced, without requiring explicit `-b` or `--pass bibtex_first` flag in V1 CLI mode | Finding 8 | May need explicit `--pass bibtex_first` if auto-detection fails — testable in CI |
| A3 | `cffconvert` v2.0.0 (2021) validates CFF v1.2.0 (it explicitly states support for 1.0.1–1.2.0) | Package Legitimacy / Finding 7 | Version 2.0.0 is the PyPI current version — if a v3.x has breaking CLI changes, validation command may differ. LOW risk given the tool's stability. |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed. → Table above has 3 low-risk assumptions.

---

## Open Questions

1. **Tectonic BibTeX auto-detection**
   - What we know: Tectonic V1 CLI runs multiple compile passes; `--pass bibtex_first` exists in V2 CLI.
   - What's unclear: Whether a plain `tectonic paper/paper.tex` invocation automatically runs BibTeX when `\bibliography{refs}` is present and `refs.bib` exists.
   - Recommendation: Include a `tectonic --pass bibtex_first paper/paper.tex` fallback in the CI step comment; let the Phase 86 CI gate validate actual compilation.

2. **arXiv identifier in `preferred-citation`**
   - What we know: `identifiers` field accepts `{type: url, value: ..., description: ...}` entries; the arXiv ID is not assigned until submission.
   - What's unclear: Whether `cffconvert --validate` is satisfied by an identifier with `type: url` pointing to the repository (vs. a real arXiv URL).
   - Recommendation: Use `identifiers: []` (empty list) or a repository URL in Phase 85; update to arXiv URL in Phase 90.

---

## Sources

### Primary (HIGH confidence)
- `scripts/docs_fig.py` (this repo) — `fig()` API, `FDARS_COLORS`, rcParams, `render()` SVG determinism pattern [VERIFIED: this session]
- `scripts/docs_data.py` (this repo) — dataset loaders, `_DATA_DIR` resolution pattern [VERIFIED: this session]
- `python/fdars/_capability_map.json` (this repo) — 31 modules, 437 callables, entry schema [VERIFIED: this session]
- `python/fdars/_references_map.json` (this repo) — 57 papers, 243 callable_index entries, field schema [VERIFIED: this session]
- matplotlib 3.10.8 `backend_pdf.PdfFile.__init__` — `metadata={"CreationDate": None}` suppression [VERIFIED: .venv this session]
- `docs/data/canadian_weather_precip.csv` — 365 rows × 36 columns (day + 35 stations) [VERIFIED: this session]

### Secondary (MEDIUM confidence)
- [CFF schema guide v1.2.0](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md) — `preferred-citation` field types, required fields [CITED]
- [wtfjoke/setup-tectonic README](https://github.com/WtfJoke/setup-tectonic) — action inputs, caching, BibTeX support [CITED]
- [tectonic compile docs](https://tectonic-typesetting.github.io/book/latest/v2cli/compile.html) — `-Z deterministic-mode`, `SOURCE_DATE_EPOCH` [CITED]
- [cffconvert PyPI](https://pypi.org/project/cffconvert/) — v2.0.0, `cffconvert --validate` command [CITED]
- [Debian wiki: Timestamps in PDF generated by LaTeX](https://wiki.debian.org/ReproducibleBuilds/TimestampsInPDFGeneratedByLaTeX) — `SOURCE_DATE_EPOCH`, `\pdfinfo` workarounds [CITED]

### Tertiary (LOW confidence)
- WebSearch results on tectonic SOURCE_DATE_EPOCH — confirmed env var respected; exact tectonic V1 CLI BibTeX auto-detection unverified [ASSUMED: A2]

---

## Metadata

**Confidence breakdown:**
- docs_fig.py API: HIGH — read the file directly this session
- matplotlib PDF metadata suppression: HIGH — inspected installed source code this session
- dataset structure: HIGH — read scripts/docs_data.py and csv headers this session
- CITATION.cff schema: MEDIUM — cited from official CFF schema guide
- tectonic CI mechanics: MEDIUM — cited from official tectonic docs; BibTeX auto-detection assumed (A2)
- LaTeX skeleton: HIGH — standard article+natbib pattern; locked decisions verified against STATE.md/PROJECT.md

**Research date:** 2026-09-08
**Valid until:** 2027-03-08 (stable tooling; matplotlib/tectonic/cffconvert APIs are stable)
