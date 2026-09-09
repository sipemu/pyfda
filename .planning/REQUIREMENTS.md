# Requirements: pyfda — v14.0 fdars Software Paper (arXiv Preprint)

**Defined:** 2026-09-08
**Core Value:** A submission-ready arXiv software paper that makes `fdars`'s breadth and method-accuracy provably clear — every code snippet runs against the current API, every number is machine-derived from the live capability/reference maps, and every figure/table is regenerable by a single command.

## v14.0 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase. A writing + reproducible-code milestone — no `fdars-core` bump, no new numerical bindings.

### Manuscript (MANU)

- [x] **MANU-01**: `paper/` LaTeX manuscript exists using plain `\documentclass{article}` with **natbib + BibTeX** (not biblatex/biber), authored as `paper.tex` + per-section files, no `\today`/timestamp macros
- [x] **MANU-02**: Front matter — Abstract, Introduction & statement of need (the Python FDA gap), and a brief FDA-background section
- [x] **MANU-03**: Software design & architecture section — Rust core + PyO3 zero-copy, module map, `Fdata` container, sklearn estimator layer (qualitative; no benchmarks)
- [x] **MANU-04**: Data-representation model section — `Fdata`, argvals/grids, irregular/sparse (`IrregFdata`) representation
- [x] **MANU-05**: Capability tour by method family with minimal runnable code snippets, each snippet sourced from an executed `paper/code/` script (never hand-copied)
- [x] **MANU-06**: Dedicated section presenting the grounded **AI advisor + scientific-provenance** layer as a novel contribution absent from peer FDA packages
- [x] **MANU-07**: Availability & installation section (PyPI, extras, Python 3.9–3.14) + Conclusion
- [x] **MANU-08**: `CITATION.cff` (v1.2.0, `cffconvert`-valid) with a `preferred-citation` block for the arXiv preprint, author block placeholdered to Simon Müller <sm@data-zoo.de>

### Pipeline & Single-Source-of-Truth (PIPE)

- [x] **PIPE-01**: `paper/code/` reproducible pipeline with a one-command runner (Makefile target) that regenerates every figure and table; `paper_utils.py` reuses `scripts/docs_fig.py` (`fig()`/colors) and resolves `docs/data/` via a `data_path()` helper (no data duplication)
- [x] **PIPE-02**: Deterministic figure generation — `matplotlib` `Agg` backend, module-top rcParams, per-figure `np.random.seed`, PDF output with suppressed `CreationDate` metadata; re-running the pipeline leaves `git diff paper/figures/` empty
- [x] **PIPE-03**: `assert_coverage.py` derives coverage counts (public + total callables) from `_capability_map.json`, writes `coverage_counts.tex` macros consumed by the manuscript, and exits non-zero on drift (no hardcoded integers in `.tex`)
- [x] **PIPE-04**: `gen_refs_bib.py` generates `paper/refs.bib` from `_references_map.json` (paper-key → cite-key, authors joined, DOI/URL fields), with a resolved strategy for the missing `journal` field (add venue during a curation pass, or emit `@misc`)

### Comparison (COMP)

- [x] **COMP-01**: `comparison_evidence.md` — every peer-package claim backed by a version-stamped source (package, version, URL, date) for scikit-fda, FDApy, R fda/fda.usc/refund, funData/tidyfun, Matlab fdaM/PACE; ≥1 peer package spot-checked against CRAN/PyPI/arXiv
- [x] **COMP-02**: Comparison-with-related-software table (`\input`-ed) — capability-dimension rows × peer-package columns; the fdars column grounded from `_capability_map.json`; coverage stated honestly (✓/partial/—)

### Case Studies (CASE)

- [x] **CASE-01**: Study 1 — smooth + FPCA + classification on phoneme/growth (`docs/data/`), with reproducible figures
- [x] **CASE-02**: Study 2 — registration + functional/scalar-on-function regression on tecator/canadian_weather, with reproducible figures
- [x] **CASE-03**: Study 3 — functional-time-series forecast on `canadian_weather_precip` (dataset structure verified to support the slicing), with reproducible figures
- [x] **CASE-04**: Study 4 — sklearn `Pipeline` + `GridSearchCV` on wine/sonar showcasing the estimator layer, with reproducible figures

### Build, CI & Close Gate (GATE)

- [x] **GATE-01**: Standalone `.github/workflows/paper.yml` — path-filtered to `paper/**` + `_capability_map.json` + `_references_map.json` + `docs/data/**`; runs the reproducible pipeline offline as a hard gate, then compiles the PDF via `tectonic` (`wtfjoke/setup-tectonic@v4`)
- [ ] **GATE-02**: Correctness gate — every manuscript code snippet executes against the current `fdars`; `assert_coverage.py` re-run green (catches late binding additions); determinism check passes (byte-identical figures on re-run)
- [ ] **GATE-03**: arXiv self-containment — a clean-directory `pdflatex + bibtex` compile of the submission sources succeeds with all figures committed under `paper/figures/`
- [ ] **GATE-04**: Blocking human manuscript read-through approved (accuracy of prose, comparison table, and citations) before close

### Release (REL)

- [ ] **REL-01**: Citable **0.13.0** package release paired with the paper — version bump (`Cargo.toml`/`pyproject.toml`/`__version__`), `CITATION.cff` + arXiv/Zenodo DOI wiring, semver `v0.13.0` tag prepared/handed to user for PyPI publish

## Future Requirements

Deferred — tracked, not in this roadmap.

### Venue

- **VENUE-01**: JOSS short-form draft (750–1750 words, "state of the field" section) derived from the arXiv manuscript
- **VENUE-02**: JSS/SoftwareX full-template reshaping with complete API reference

## Out of Scope

Explicitly excluded, with reasoning.

| Feature | Reason |
|---------|--------|
| Performance benchmarks vs peers | User chose breadth & correctness as the differentiators; benchmark wars invite scope creep and are excluded |
| `fdars-core` crate bump / new numerical bindings | Writing + reproducible-code milestone; the paper documents the current surface |
| Local LaTeX toolchain setup | None installed; PDF compile is CI-only (tectonic) or Overleaf — the local hard gate is the Python pipeline |
| biblatex + biber | tectonic silently breaks biber in CI (`[?]` citations); natbib + BibTeX chosen instead |
| New datasets / downloads | Reuse existing `docs/data/` datasets per the compatibility constraint |
| Snakemake/DVC pipeline framework | 20+ deps for zero benefit on a linear figure pipeline; a Makefile + Python runner suffices |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| MANU-01 | Phase 85 | Complete |
| MANU-02 | Phase 88 | Complete |
| MANU-03 | Phase 88 | Complete |
| MANU-04 | Phase 88 | Complete |
| MANU-05 | Phase 88 | Complete |
| MANU-06 | Phase 88 | Complete |
| MANU-07 | Phase 88 | Complete |
| MANU-08 | Phase 85 | Complete |
| PIPE-01 | Phase 85 | Complete |
| PIPE-02 | Phase 85 | Complete |
| PIPE-03 | Phase 86 | Complete |
| PIPE-04 | Phase 86 | Complete |
| COMP-01 | Phase 87 | Complete |
| COMP-02 | Phase 87 | Complete |
| CASE-01 | Phase 89 | Complete |
| CASE-02 | Phase 89 | Complete |
| CASE-03 | Phase 89 | Complete |
| CASE-04 | Phase 89 | Complete |
| GATE-01 | Phase 86 | Complete |
| GATE-02 | Phase 90 | Pending |
| GATE-03 | Phase 90 | Pending |
| GATE-04 | Phase 90 | Pending |
| REL-01 | Phase 90 | Pending |

**Coverage:**

- v14.0 requirements: 23 total
- Mapped to phases: 23 ✓
- Unmapped: 0

**Per-phase distribution:**

- Phase 85 (Scaffold + Pipeline Infra): MANU-01, MANU-08, PIPE-01, PIPE-02 (4)
- Phase 86 (SSoT Wiring + CI Gate): PIPE-03, PIPE-04, GATE-01 (3)
- Phase 87 (Comparison Table + Evidence): COMP-01, COMP-02 (2)
- Phase 88 (Front Matter, Design & Capability Tour): MANU-02..07 (6)
- Phase 89 (Case Studies + Figures): CASE-01..04 (4)
- Phase 90 (Close Gate + Citable Release): GATE-02, GATE-03, GATE-04, REL-01 (4)

---
*Requirements defined: 2026-09-08*
*Last updated: 2026-09-08 after roadmap creation (phases 85–90 mapped)*
