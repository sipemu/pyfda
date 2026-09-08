# Phase 86: Single-Source-of-Truth Wiring + CI Gate — Research

**Researched:** 2026-09-08
**Domain:** Python scripting against committed JSON maps; BibTeX generation; GitHub Actions path-filtered workflow; tectonic PDF compile
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- JSON maps live at `python/fdars/_capability_map.json` and `python/fdars/_references_map.json` — scripts and the CI path-filter MUST reference those actual paths.
- Coverage macros emitted as `paper/coverage_counts.tex` consumed via `\input{coverage_counts.tex}`; the manuscript uses macros, never literal integers.
- Missing-`journal` strategy: default to emitting BibTeX `@misc` when a reference lacks a venue. Choose the approach that keeps `refs.bib` BibTeX-valid and citation-complete.
- CI uses `wtfjoke/setup-tectonic@v4`; the pipeline (`make paper`) runs offline as the hard gate BEFORE the tectonic PDF compile.
- New scripts belong under `paper/code/` alongside Phase 85's `paper_utils.py`/`gen_figures.py`.

### Claude's Discretion
Pure infrastructure phase — all implementation choices at Claude's discretion, guided by ROADMAP success criteria and existing repo conventions.

### Deferred Ideas (OUT OF SCOPE)
None — infrastructure phase. REF-FUT-01 uncurated-tail completion remains a v14+ future item, out of scope here.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PIPE-03 | `assert_coverage.py` derives coverage counts (public + total callables) from `_capability_map.json`, writes `coverage_counts.tex` macros consumed by the manuscript, and exits non-zero on drift (no hardcoded integers in `.tex`) | Counting semantics verified against capability map; drift mechanism designed below |
| PIPE-04 | `gen_refs_bib.py` generates `paper/refs.bib` from `_references_map.json` (paper-key → cite-key, authors joined, DOI/URL fields), with a resolved strategy for the missing `journal` field | Full map structure verified; BibTeX type mapping derived; @misc fallback strategy defined |
| GATE-01 | Standalone `.github/workflows/paper.yml` path-filtered to `paper/**` + `_capability_map.json` + `_references_map.json` + `docs/data/**`; runs the reproducible pipeline offline as a hard gate, then compiles the PDF via `tectonic` (`wtfjoke/setup-tectonic@v4`) | Existing workflow conventions read; tectonic BibTeX behavior confirmed from Phase 85 research |
</phase_requirements>

---

## Summary

Phase 86 wires the two committed JSON maps (`_capability_map.json`, `_references_map.json`) to the LaTeX manuscript by writing two generator scripts in `paper/code/` and a GitHub Actions workflow. No new Python packages or Rust compilation are needed for these scripts — both generators are stdlib-only (`json`, `pathlib`, `sys`, `textwrap`). The generated outputs (`coverage_counts.tex`, `refs.bib`) are consumed by `paper/paper.tex` and are the single source of truth for every number and citation in the manuscript.

The `_capability_map.json` file has been read this session. Its counting semantics are settled: 437 total callable entries across 31 top-level module keys (30 public non-underscore modules + the `_Fdata` class key), with 409 callables in the public modules and 27 public Fdata methods (non-dunder). The `_references_map.json` has 57 papers total (47 non-uncurated eligible for refs.bib emission; 10 `_uncurated_*` placeholders that must be skipped). No paper in the map carries a `journal`, `booktitle`, or `publisher` field — the `@misc` fallback applies to all entries.

The Phase 85 research already confirmed tectonic's BibTeX auto-run behavior and the `wtfjoke/setup-tectonic@v4` action signature; those findings are carried forward here unchanged and are not re-researched.

**Primary recommendation:** Write `assert_coverage.py` and `gen_refs_bib.py` as stdlib-only scripts under `paper/code/`, commit a generated `paper/coverage_counts.tex` and regenerated `paper/refs.bib`, and author `paper.yml` mirroring `docs.yml` conventions (actions/checkout@v4, actions/setup-python@v5 Python 3.12, pip install matplotlib numpy, then tectonic step with `github-token`).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Coverage count derivation | `paper/code/assert_coverage.py` | — | Script reads committed JSON and derives integers; manuscript consumes generated .tex |
| BibTeX generation | `paper/code/gen_refs_bib.py` | — | Script reads `_references_map.json`; outputs `paper/refs.bib` overwriting the stub |
| Drift detection (PIPE-03) | CI (`paper.yml`) | `assert_coverage.py --check` flag | CI re-runs the script in check mode; non-zero exit fails the workflow |
| PDF compile (GATE-01) | CI (`paper.yml`) | — | tectonic handles BibTeX passes automatically; no local LaTeX needed |
| Path-filtered trigger | `.github/workflows/paper.yml` | — | `on: push/pull_request: paths:` block |

---

## Capability Map: Verified Counting Semantics

**Source of truth file:** `python/fdars/_capability_map.json` [VERIFIED: python/fdars/_capability_map.json:1-1838]

The file is a single JSON object. Its structure and the authoritative counts are:

```
Top-level keys: 31 total
  30 public module keys (non-underscore): alignment, basis, classification, clustering,
    conformal, covariance, datasets, density_fda, depth, explain, famm, fdata, frechet,
    fts, inference, metric, metrics, multi_fdata, outliers, pace_fpca, regression,
    represent, scalar_on_function, scoring, seasonal, shapelet, simulation, smoothing,
    spm, tolerance
  1 class key: _Fdata  (underscore-prefixed — NOT a "public module"; it is the Fdata class)

Per-module callable counts (verbatim from json.load + len()):
  alignment: 68, basis: 16, classification: 9, clustering: 11, conformal: 7,
  covariance: 14, datasets: 7, density_fda: 5, depth: 18, explain: 46, famm: 3,
  fdata: 15, frechet: 4, fts: 13, inference: 11, metric: 26, metrics: 5,
  multi_fdata: 2, outliers: 8, pace_fpca: 3, regression: 29, represent: 4,
  scalar_on_function: 5, scoring: 5, seasonal: 18, shapelet: 7, simulation: 8,
  smoothing: 10, spm: 23, tolerance: 9
  _Fdata: 28 (includes __init__; 27 public non-dunder methods)

Total callable entries: 437  (sum of all 31 top-level values)
Public module callables: 409  (sum for the 30 non-underscore keys)
Fdata public methods: 27  (non-dunder, i.e. excluding __init__)
```

**Canonical counting definition** (from `scripts/generate_capability_dataset.py:_coverage_counts()`
[VERIFIED: scripts/generate_capability_dataset.py:507-528]):

```python
denominator = sum(len(v) for v in cap_data.values())  # = 437
```

The verbatim code for the numerator (callables covered by a curated paper) from that same function:

```python
curated_paper_keys = frozenset(
    pk for pk, p in papers_map.items() if p.get("curated", False) is True
)
numerator = sum(
    1 for _, pks in callable_index.items()
    if any(pk in curated_paper_keys for pk in pks)
)
```

Current values (derived this session): denominator = 437, numerator = 28.

**assert_coverage.py MUST mirror this exact logic.** The `_Fdata` key MUST be included in the total (it is an entry in the map, and `sum(len(v) for v in cap.values())` includes it). Do not subtract `__init__` from the total — the existing `_coverage_counts` function does not.

**Macro set for `coverage_counts.tex`** — these are the values the manuscript will cite:

| Macro name | Value | Derivation |
|------------|-------|------------|
| `\nsubmodules` | 30 | `len([k for k in cap if not k.startswith("_")])` |
| `\ncallables` | 437 | `sum(len(v) for v in cap.values())` |
| `\npubliccallables` | 409 | sum for non-underscore module keys |
| `\nfdata` | 27 | public non-dunder `_Fdata` methods |
| `\ncoverage` | 28 | callables with at least one curated paper |
| `\ndocpapers` | 47 | non-`_uncurated` papers in `_references_map.json` |

The exact macro names are at Claude's discretion — the above names are a recommendation. Use `\newcommand` form so the manuscript can call `\ncallables{}` inline.

---

## References Map: Verified Structure and BibTeX Strategy

**Source of truth file:** `python/fdars/_references_map.json` [VERIFIED: python/fdars/_references_map.json:1-57-papers]

```
Top-level keys: "papers", "callable_index"

papers: 57 total
  curated: 6 (curated: true)
  not curated: 51 (curated: false)
  uncurated placeholders (_uncurated_* keys): 10 — MUST be skipped in refs.bib

Per-paper fields (all 57 have all of these):
  title, authors (list of "Last, F." strings), year (int), type (str),
  callables (list), notes (str), curated (bool), url (str)

  doi: present in 46/57 papers; absent (key missing) in 11; empty string "" in 4

No paper has a "journal", "booktitle", "venue", or "publisher" field.
```

**Type values** (from `type` field, verbatim):

| `type` value | Count | BibTeX entry type | Required BibTeX fields |
|---|---|---|---|
| `"journal"` | 47 | `@misc` (no `journal` field in map) | author, title, year |
| `"preprint"` | 2 | `@misc` | author, title, year |
| `"book"` | 3 | `@misc` (no `publisher`) | author, title, year |
| `"conference"` | 4 | `@misc` (no `booktitle`) | author, title, year |
| `"book_chapter"` | 1 | `@misc` (no `booktitle`/`publisher`) | author, title, year |

**Decision: emit `@misc` for all 47 non-uncurated entries.** This is the locked strategy from CONTEXT.md. `@misc` is always BibTeX-valid with only author + title + year, and the additional fields (doi, url) can be placed in `note` or as standard optional fields. BibTeX does not require a `journal` field on `@misc`.

**Recommended `@misc` template:**

```bibtex
@misc{fraiman_muniz_2001,
  author = {Fraiman, R. and Muniz, G.},
  title  = {Trimmed means for functional data},
  year   = {2001},
  doi    = {10.1007/BF02595706},
  url    = {https://link.springer.com/article/10.1007/BF02595706},
  note   = {Type: journal},
}
```

When `doi` is absent (key missing) or an empty string, omit the `doi` line. When `url` is an empty string, omit it. The `note` field carries the original `type` for human readers.

**Authors field derivation** — verbatim author strings are already in `"Last, F."` form; join with `" and "`:

```python
" and ".join(paper["authors"])
# e.g. "Fraiman, R. and Muniz, G."
```

**Cite-key derivation** — the paper-key IS the BibTeX cite-key (no transformation):

```python
bibtex_key = paper_key  # e.g. "fraiman_muniz_2001" -> \cite{fraiman_muniz_2001}
```

**Uncurated skip rule** — skip any paper whose key starts with `_uncurated`:

```python
if paper_key.startswith("_uncurated"):
    continue
```

**Non-uncurated papers to emit:** 47 (57 total minus 10 `_uncurated_*` entries).

**callable_index structure** (from `_references_map.json`):

```python
callable_index: {
  "depth.fraiman_muniz_1d": ["fraiman_muniz_2001"],
  "depth.fraiman_muniz_2d": ["fraiman_muniz_2001"],
  "_Fdata.depth": ["fraiman_muniz_2001"],
  ...
}  # 243 total entries
```

`assert_coverage.py` uses `callable_index` to derive `numerator` (callables with a curated paper). `gen_refs_bib.py` does NOT use `callable_index` — it iterates `papers` only.

---

## Standard Stack

### Core (no new packages — stdlib only)

Both new scripts are stdlib-only: `json`, `pathlib`, `sys`, `textwrap`. No installation needed.

The paper pipeline (`make paper`) uses `matplotlib` + `numpy` (already in the docs/dev environment). The paper.yml CI step must install these:

```bash
pip install matplotlib numpy
```

No `fdars` install (no `maturin develop`) needed for Phase 86 scripts. The case study scripts in Phase 89 will need fdars, but paper.yml will be extended then.

### Supporting

| Tool | Version | Purpose | Source |
|------|---------|---------|--------|
| `wtfjoke/setup-tectonic@v4` | v4 | Install tectonic in CI for PDF compile | [CITED: 85-RESEARCH.md Finding 8] |
| `tectonic` | auto (action) | Compile `paper/paper.tex` with BibTeX auto-passes | [CITED: 85-RESEARCH.md Finding 8] |
| `actions/checkout@v4` | v4 | Repo checkout (mirror existing workflows) | [VERIFIED: .github/workflows/ci.yml:5] |
| `actions/setup-python@v5` | v5 | Python 3.12 setup (mirror docs.yml) | [VERIFIED: .github/workflows/docs.yml:24] |

---

## Architecture Patterns

### System Architecture Diagram

```
_capability_map.json ──→ assert_coverage.py ──→ paper/coverage_counts.tex
                               │                        │
                               │ exit 1 if drift        ↓
                               └──────────────── paper/paper.tex (\input{coverage_counts.tex})
                                                        │
_references_map.json ──→ gen_refs_bib.py ──→ paper/refs.bib
                               │                        │
                               │ skip _uncurated_*      ↓
                               └──────────────── paper/paper.tex (\bibliography{refs})
                                                        │
paper/code/gen_figures.py ──→ paper/figures/*.pdf       │
                                                        ↓
.github/workflows/paper.yml: [gen_figures] → [assert_coverage --check] → [gen_refs_bib] → [tectonic paper/paper.tex] → PDF
```

### Recommended Project Structure

```
paper/
├── code/
│   ├── paper_utils.py          # Phase 85 (exists)
│   ├── gen_figures.py          # Phase 85 (exists)
│   ├── assert_coverage.py      # Phase 86 NEW
│   └── gen_refs_bib.py         # Phase 86 NEW
├── figures/
│   └── smoke.pdf               # Phase 85 (exists)
├── sections/                   # Phase 85 (exists)
├── paper.tex                   # Phase 85 (exists)
├── refs.bib                    # Phase 85 stub → Phase 86 overwrites with 47 entries
└── coverage_counts.tex         # Phase 86 NEW (generated + committed)
.github/
└── workflows/
    └── paper.yml               # Phase 86 NEW
```

### Pattern 1: assert_coverage.py — generate + check modes

The script operates in two modes selected by a CLI flag:

```python
# paper/code/assert_coverage.py
"""Generate or check paper/coverage_counts.tex from _capability_map.json.

Usage:
    python paper/code/assert_coverage.py           # generate (write coverage_counts.tex)
    python paper/code/assert_coverage.py --check   # check: exit 1 if generated != committed
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_CAP_MAP = _REPO / "python" / "fdars" / "_capability_map.json"
_REF_MAP = _REPO / "python" / "fdars" / "_references_map.json"
_OUT = _REPO / "paper" / "coverage_counts.tex"


def _derive_counts() -> dict[str, int]:
    cap = json.loads(_CAP_MAP.read_text())
    refs = json.loads(_REF_MAP.read_text())
    papers = refs["papers"]
    callable_index = refs.get("callable_index", {})

    public_modules = [k for k in cap if not k.startswith("_")]
    fdata_public = [m for m in cap.get("_Fdata", {}) if not m.startswith("_")]

    curated_keys = frozenset(pk for pk, p in papers.items() if p.get("curated") is True)
    n_coverage = sum(
        1 for _, pks in callable_index.items()
        if any(pk in curated_keys for pk in pks)
    )
    n_docpapers = sum(1 for k in papers if not k.startswith("_uncurated"))

    return {
        "nsubmodules":      len(public_modules),
        "ncallables":       sum(len(v) for v in cap.values()),
        "npubliccallables": sum(len(cap[k]) for k in public_modules),
        "nfdata":           len(fdata_public),
        "ncoverage":        n_coverage,
        "ndocpapers":       n_docpapers,
    }


def _render(counts: dict[str, int]) -> str:
    lines = [
        "% Auto-generated by paper/code/assert_coverage.py — do not edit.",
        "% Source: python/fdars/_capability_map.json + _references_map.json",
    ]
    for macro, value in sorted(counts.items()):
        lines.append(f"\\newcommand{{\\{macro}}}{{{value}}}")
    return "\n".join(lines) + "\n"


def main() -> None:
    check_mode = "--check" in sys.argv
    counts = _derive_counts()
    content = _render(counts)

    if check_mode:
        if not _OUT.exists():
            print(f"DRIFT: {_OUT} does not exist — run without --check to generate.",
                  file=sys.stderr)
            sys.exit(1)
        committed = _OUT.read_text()
        if committed != content:
            print(f"DRIFT: {_OUT} is stale — re-run assert_coverage.py and commit.",
                  file=sys.stderr)
            sys.exit(1)
        print("assert_coverage: OK (no drift)")
    else:
        _OUT.write_text(content)
        print(f"Written {_OUT}")

if __name__ == "__main__":
    main()
```

### Pattern 2: gen_refs_bib.py — @misc for all entries

```python
# paper/code/gen_refs_bib.py
"""Generate paper/refs.bib from python/fdars/_references_map.json.

All entries use @misc (no journal/booktitle/publisher in the map).
Uncurated placeholder entries (_uncurated_* keys) are skipped.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_REF_MAP = _REPO / "python" / "fdars" / "_references_map.json"
_OUT = _REPO / "paper" / "refs.bib"

_HEADER = """\
% paper/refs.bib — auto-generated by paper/code/gen_refs_bib.py
% Source: python/fdars/_references_map.json
% Do not hand-edit; regenerate with: python paper/code/gen_refs_bib.py
"""


def _entry(key: str, paper: dict) -> str:
    authors = " and ".join(paper.get("authors", []))
    title   = paper.get("title", "").replace("{", "\\{").replace("}", "\\}")
    year    = paper.get("year", "")
    doi     = paper.get("doi") or ""
    url     = paper.get("url") or ""
    ptype   = paper.get("type", "")

    lines = [f"@misc{{{key},"]
    lines.append(f"  author = {{{authors}}},")
    lines.append(f"  title  = {{{{{title}}}}},")
    lines.append(f"  year   = {{{year}}},")
    if doi:
        lines.append(f"  doi    = {{{doi}}},")
    if url:
        lines.append(f"  url    = {{{url}}},")
    if ptype:
        lines.append(f"  note   = {{Type: {ptype}}},")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    refs = json.loads(_REF_MAP.read_text())
    papers = refs.get("papers", {})
    entries = []
    skipped = 0
    for key in sorted(papers):
        if key.startswith("_uncurated"):
            skipped += 1
            continue
        entries.append(_entry(key, papers[key]))
    content = _HEADER + "\n\n".join(entries) + "\n"
    _OUT.write_text(content)
    print(f"Written {_OUT} ({len(entries)} entries, {skipped} uncurated skipped)")

if __name__ == "__main__":
    main()
```

**Title double-bracing:** `{{{title}}}` in the BibTeX output preserves case in the rendered citation (BibTeX lowercases unbraced titles).

### Pattern 3: paper.yml path-filter + pipeline gate

```yaml
name: Paper

on:
  push:
    branches: [main]
    paths:
      - "paper/**"
      - "python/fdars/_capability_map.json"
      - "python/fdars/_references_map.json"
      - "docs/data/**"
  pull_request:
    paths:
      - "paper/**"
      - "python/fdars/_capability_map.json"
      - "python/fdars/_references_map.json"
      - "docs/data/**"

jobs:
  paper:
    name: Paper pipeline + PDF compile
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python dependencies
        run: pip install matplotlib numpy

      - name: Regenerate figures (PIPE-02 determinism gate)
        env:
          PYTHONPATH: scripts:paper/code
        run: python paper/code/gen_figures.py

      - name: Assert coverage macros (PIPE-03 drift gate)
        run: python paper/code/assert_coverage.py --check

      - name: Regenerate refs.bib (PIPE-04)
        run: python paper/code/gen_refs_bib.py

      - name: Setup tectonic
        uses: wtfjoke/setup-tectonic@v4
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Compile PDF (GATE-01)
        env:
          SOURCE_DATE_EPOCH: "0"
        run: tectonic paper/paper.tex
```

**Step ordering is load-bearing:**
1. `gen_figures.py` first (figures must exist before tectonic; validates PIPE-02 determinism side-by-side).
2. `assert_coverage.py --check` second — if `coverage_counts.tex` is stale or absent, fail before spending time on tectonic.
3. `gen_refs_bib.py` third — overwrites the stub `refs.bib` with real entries so tectonic sees them.
4. `tectonic` last — BibTeX auto-runs from the freshly written `refs.bib`.

**Note:** `gen_refs_bib.py` writes `paper/refs.bib` in the CI workspace but does NOT commit it. The `paper/paper.tex` manuscript references `\bibliography{refs}`, and tectonic resolves this to `paper/refs.bib` in the same directory. The CI workspace write is ephemeral — the committed `paper/refs.bib` (updated by Phase 86 locally and committed) is the durable copy.

**Alternative for refs.bib:** The step above regenerates refs.bib from the map every CI run, so the committed `paper/refs.bib` is always current after a local run and commit. This is the same pattern as `coverage_counts.tex`. Both generated files MUST be committed to the repo so that tectonic (and the Phase 90 offline `pdflatex + bibtex` gate) can find them without running the generators.

### Pattern 4: drift demonstration ("introduce a drift → CI fails")

To demonstrate PIPE-03 drift detection:
1. Edit `_capability_map.json` to add one dummy callable (or remove one) WITHOUT re-running `assert_coverage.py`.
2. Push to a branch.
3. CI runs `assert_coverage.py --check`, detects mismatch, exits 1 — workflow fails.
4. Revert the edit (or re-run `assert_coverage.py` and commit the updated `coverage_counts.tex`).

This is the recommended negative-test verification step in the plan.

### Anti-Patterns to Avoid

- **Hardcoded integers in coverage_counts.tex:** The file must be generated by the script, not hand-edited. If a developer edits it to add `\newcommand{\ncallables}{500}` manually, `assert_coverage.py --check` will catch the drift on the next CI run.
- **Emitting `@article{..., journal = {TODO}}` when the map has no journal field:** BibTeX tolerates `@misc` with no `journal` better than `@article` with a stub or empty `journal`. Stick with `@misc` for all entries.
- **Including `_uncurated_*` keys in refs.bib:** These are placeholders without verified titles/authors/DOIs. `gen_refs_bib.py` must skip them. If they leak into refs.bib, `tectonic` may warn about malformed entries and the manuscript prose may accidentally cite an uncurated stub.
- **`fetch-depth: 0` in paper.yml checkout:** Not needed here (no `git log`/`git diff` checks). The CI and sklearn workflows need it; paper.yml does not.
- **`biber-version` input in setup-tectonic:** Only for biber. Not needed for natbib + plain BibTeX. Providing it risks version pinning issues.
- **Calling `maturin develop` in paper.yml for Phase 86:** `assert_coverage.py` and `gen_refs_bib.py` are stdlib-only; `gen_figures.py` needs only matplotlib + numpy (docs_fig.py is matplotlib-only at the top level). No fdars compilation needed in Phase 86. When Phase 89 case study scripts are added, paper.yml will need a `maturin develop` step added.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF compile with BibTeX passes | Custom shell script calling `pdflatex` × N + `bibtex` | `tectonic paper/paper.tex` | tectonic auto-loops BibTeX and TeX until stable [CITED: 85-RESEARCH.md] |
| BibTeX cite-key derivation | Name-parsing logic | Direct use of `paper_key` as cite-key | Map keys ARE the cite-keys already; no transformation needed [VERIFIED: python/fdars/_references_map.json:3] |
| Coverage denominator | Custom counting heuristic | `sum(len(v) for v in cap.values())` | Exact formula from existing `_coverage_counts()` in generate_capability_dataset.py [VERIFIED: scripts/generate_capability_dataset.py:518] |

---

## Common Pitfalls

### Pitfall 1: coverage_counts.tex not committed — CI --check fails on first run

**What goes wrong:** `assert_coverage.py --check` exits 1 with "file does not exist" on the first CI run.
**Why it happens:** The script is added but the generated output is not committed before the CI gate is active.
**How to avoid:** Run `python paper/code/assert_coverage.py` locally, commit `paper/coverage_counts.tex` in the same PR that adds the script. The CI `--check` mode compares against the committed file.
**Warning signs:** CI log shows "DRIFT: paper/coverage_counts.tex does not exist".

### Pitfall 2: refs.bib stub replaced but \input{coverage_counts} missing from paper.tex

**What goes wrong:** `coverage_counts.tex` macros are generated but paper.tex doesn't `\input` them, so tectonic compiles successfully but coverage macros are undefined when prose tries to use them.
**Why it happens:** Phase 85 did not add the `\input{coverage_counts}` line (it wasn't needed yet).
**How to avoid:** Add `\input{coverage_counts}` to `paper/paper.tex` in Phase 86 (before `\begin{document}` or immediately after `\maketitle`).
**Warning signs:** `tectonic` warns about undefined control sequences like `\ncallables`.

### Pitfall 3: Title double-bracing in BibTeX

**What goes wrong:** `\bibliographystyle{plain}` lowercases all unbraced words in the title — "Functional Data Analysis" becomes "Functional data analysis".
**Why it happens:** Standard BibTeX style lowercases unbraced text in `title` fields.
**How to avoid:** Double-brace the title value: `title = {{Trimmed means for functional data}}`. The pattern `title = {{{title}}}` in the f-string produces `title = {{Trimmed means for functional data}}` in the output.
**Warning signs:** Proper nouns and acronyms appear lowercase in the compiled PDF reference list.

### Pitfall 4: Empty-string DOI vs absent DOI

**What goes wrong:** `@misc` entries have `doi = {},` (empty) which some BibTeX processors warn about.
**Why it happens:** Four papers in the map have `"doi": ""` (empty string) rather than a missing key.
**How to avoid:** In `gen_refs_bib.py`, normalize: `doi = paper.get("doi") or ""` and only emit the `doi` line when the value is non-empty. Same for `url`.
**Warning signs:** BibTeX warning "empty field" in CI log.

### Pitfall 5: Paper pipeline fails in CI because paper/ is the working directory

**What goes wrong:** `tectonic paper/paper.tex` fails to find `refs.bib` or `coverage_counts.tex` because tectonic resolves relative paths from the directory of the .tex file.
**Why it happens:** `paper/paper.tex` references `\bibliography{refs}` and `\input{coverage_counts}` as relative paths. Tectonic resolves these relative to the .tex file's directory (`paper/`), so `paper/refs.bib` must exist (not just `refs.bib` in the repo root).
**How to avoid:** Both generated files go into `paper/` (already the design). Confirm that `gen_refs_bib.py` writes to `paper/refs.bib` and `assert_coverage.py` writes to `paper/coverage_counts.tex`. Run from the repo root: `tectonic paper/paper.tex`.
**Warning signs:** `tectonic` error "file not found: refs.bib".

### Pitfall 6: path-filter missing the JSON map paths

**What goes wrong:** A developer updates `_capability_map.json` but paper.yml doesn't trigger, so the drift goes undetected until a separate paper change is pushed.
**Why it happens:** The path-filter only covers `paper/**` but not the JSON map files.
**How to avoid:** Include both `python/fdars/_capability_map.json` and `python/fdars/_references_map.json` in the `paths:` list — these are what GATE-01 specifies.
**Warning signs:** `_capability_map.json` updated in a commit, paper.yml not triggered.

---

## tectonic + natbib + BibTeX: Verified Behavior

**From Phase 85 research (carried forward):**

Tectonic auto-loops TeX and BibTeX passes — it reads the `.bib` file referenced in `\bibliography{refs}` and runs bibtex automatically until stable. No `--pass bibtex_first` flag or biber input needed for plain BibTeX with natbib.

`wtfjoke/setup-tectonic@v4` action:
- Input: `github-token: ${{ secrets.GITHUB_TOKEN }}` (avoids rate-limiting on package downloads)
- Input: NO `biber-version` (biber-version is for biber only)
- After the action runs: `tectonic` is on PATH
- Command: `tectonic paper/paper.tex` (run from repo root)
- `SOURCE_DATE_EPOCH: "0"` env var → deterministic PDF timestamps

[CITED: .planning/phases/85-manuscript-scaffold-pipeline-infrastructure/85-RESEARCH.md:530-547]

---

## Environment Availability Audit

| Dependency | Required By | Available | Fallback |
|------------|------------|-----------|---------|
| Python 3.12 | assert_coverage.py, gen_refs_bib.py | ✓ (CI: setup-python@v5) | — |
| json (stdlib) | assert_coverage.py, gen_refs_bib.py | ✓ | — |
| matplotlib | gen_figures.py | ✓ (pip install) | — |
| numpy | gen_figures.py | ✓ (pip install) | — |
| tectonic | PDF compile | ✓ (CI: wtfjoke/setup-tectonic@v4) | — |
| fdars / maturin | Phase 86 scripts | NOT NEEDED in Phase 86 | n/a |
| `paper/coverage_counts.tex` | assert_coverage.py --check | Must be committed | Run script first |
| `paper/refs.bib` | tectonic | Stub exists (committed); overwritten by gen_refs_bib.py | n/a |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Command |
|--------|----------|-----------|---------|
| PIPE-03 | assert_coverage.py writes correct macros | script verification | `python paper/code/assert_coverage.py; grep ncallables paper/coverage_counts.tex` |
| PIPE-03 | assert_coverage.py exits 1 on drift | negative test | modify `_capability_map.json`, then `python paper/code/assert_coverage.py --check`; expect exit 1 |
| PIPE-04 | gen_refs_bib.py emits 47 entries, skips 10 uncurated | script verification | `python paper/code/gen_refs_bib.py; grep -c '^@misc' paper/refs.bib` (expect 47) |
| PIPE-04 | gen_refs_bib.py produces valid BibTeX | tectonic compile | `tectonic paper/paper.tex` without warnings/errors |
| GATE-01 | paper.yml triggers on map file change | CI path-filter | Push a change to `_capability_map.json`; confirm paper.yml workflow runs |
| GATE-01 | paper.yml gates on drift | CI negative gate | Commit stale `coverage_counts.tex`; push; confirm CI fails at assert_coverage step |

### Sampling Rate

- **Per commit:** Run `python paper/code/assert_coverage.py` and `python paper/code/gen_refs_bib.py` locally.
- **Phase gate:** CI paper.yml green on the final commit.

### Wave 0 Gaps

- [ ] `paper/coverage_counts.tex` — generated and committed as part of Phase 86 plan execution.
- [ ] `paper/refs.bib` — overwritten from stub to 47-entry file as part of Phase 86 plan execution.
- [ ] `\input{coverage_counts}` line in `paper/paper.tex` — added in Phase 86.

---

## Security Domain

No user-supplied input; both scripts operate on committed JSON files in the repo. The `data_path()` path-traversal guard in `paper_utils.py` is the existing pattern [VERIFIED: paper/code/paper_utils.py:41-78]; Phase 86 scripts do not take user path arguments.

ASVS V5 (Input Validation) is satisfied by operating only on committed JSON artifacts with known schema.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `tectonic paper/paper.tex` resolves `\bibliography{refs}` relative to `paper/paper.tex`'s directory | tectonic behavior | refs.bib not found; add explicit path or cd into paper/ before running tectonic |
| A2 | `@misc` with `doi` and `url` fields is valid BibTeX (no warning from tectonic) | BibTeX generation | BibTeX may warn; move doi/url into `note` field as plain text |

**If this table is empty:** All claims verified. The two assumptions above are well-established BibTeX behavior but not verified by running tectonic locally this session.

---

## Sources

### Primary (HIGH confidence — verified by reading source files this session)

- `python/fdars/_capability_map.json` — full structure, counting semantics, top-level keys and per-module counts
- `python/fdars/_references_map.json` — full structure, 57 papers, type distribution, field inventory
- `scripts/generate_capability_dataset.py:507-528` — canonical `_coverage_counts()` function
- `.github/workflows/ci.yml`, `.github/workflows/docs.yml` — action versions and workflow conventions
- `paper/code/paper_utils.py`, `paper/code/gen_figures.py` — Phase 85 pipeline (imports, PYTHONPATH, save_figure)
- `paper/paper.tex` — confirms `\bibliography{refs}` and `\bibliographystyle{plain}`
- `paper/refs.bib` — confirms stub comment referencing Phase 86
- `Makefile` — PAPER_PYTHONPATH pattern: `scripts:paper/code`

### Secondary (MEDIUM confidence — cited from prior research)

- `.planning/phases/85-manuscript-scaffold-pipeline-infrastructure/85-RESEARCH.md:530-547` — tectonic BibTeX auto-run behavior, `wtfjoke/setup-tectonic@v4` action signature, `github-token` requirement, `SOURCE_DATE_EPOCH` for determinism

---

## Metadata

**Confidence breakdown:**
- Counting semantics: HIGH — derived by running `python3 -c "import json; ..."` against live files this session
- BibTeX generation strategy: HIGH — map structure fully read; @misc fallback is the locked decision from CONTEXT.md
- tectonic + GitHub Actions: MEDIUM — carried from Phase 85 research (cited, not re-run this session)
- Drift mechanism: HIGH — designed from the same pattern as the PIPE-02 determinism gate (established project pattern)

**Research date:** 2026-09-08
**Valid until:** End of v14.0 milestone (map schemas are stable; tectonic action tag is pinned to @v4)
