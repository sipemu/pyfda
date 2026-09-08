# Phase 86: Single-Source-of-Truth Wiring + CI Gate - Context

**Gathered:** 2026-09-08
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — discuss skipped)

<domain>
## Phase Boundary

The drift tripwires are functional before any prose cites a number — coverage counts and the bibliography are machine-derived from the committed JSON maps, and a standalone CI workflow runs the pipeline offline and compiles the PDF.

Delivers:
- `assert_coverage.py` — derives public + total callable counts from `python/fdars/_capability_map.json`, writes `coverage_counts.tex` macros consumed by the manuscript, exits non-zero on drift (no coverage integer hardcoded in any `.tex`).
- `gen_refs_bib.py` — generates `paper/refs.bib` from `python/fdars/_references_map.json` (paper-key → cite-key, authors joined, DOI/URL fields) with a resolved strategy for the missing `journal` field.
- `.github/workflows/paper.yml` — path-filtered to `paper/**` + the two JSON maps + `docs/data/**`; runs the reproducible pipeline offline as a hard gate, then compiles the PDF via `tectonic` (`wtfjoke/setup-tectonic@v4`).
- A drift (stale hardcoded count / missing ref) makes the CI gate fail, not pass silently.

Requirements: PIPE-03, PIPE-04, GATE-01.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
Pure infrastructure phase — all implementation choices at Claude's discretion, guided by ROADMAP success criteria and existing repo conventions. Key locked/derived points:
- JSON maps live at `python/fdars/_capability_map.json` and `python/fdars/_references_map.json` (NOT repo root) — scripts and the CI path-filter must reference those actual paths.
- Coverage macros are emitted as `\input{coverage_counts.tex}` (or an equivalent generated `.tex`); the manuscript consumes macros, never literal integers.
- Missing-`journal` strategy: default to emitting a BibTeX `@misc` entry when a reference lacks a venue (standard fallback), unless the map already supplies a venue during a curation pass. Choose the approach that keeps `refs.bib` BibTeX-valid and citation-complete.
- CI uses `wtfjoke/setup-tectonic@v4`; the pipeline (`make paper`, established in Phase 85) runs offline as the hard gate BEFORE the tectonic PDF compile. This is the phase where the Phase 85 `verification: backstop` tectonic-compile item becomes a live CI check.
- New scripts belong under `paper/code/` alongside Phase 85's `paper_utils.py`/`gen_figures.py`, reusing `data_path()` conventions where relevant.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `paper/code/paper_utils.py`, `paper/code/gen_figures.py`, `make paper` target (Phase 85) — the pipeline the CI gate runs.
- `python/fdars/_capability_map.json` — source of truth for coverage counts (public + total callables).
- `python/fdars/_references_map.json` — source of truth for the bibliography (paper-key → cite-key, authors, DOI/URL).
- Existing CI workflows: `.github/workflows/{ci,docs,publish}.yml` — mirror their conventions (checkout, python setup, caching) in the new `paper.yml`.

### Established Patterns
- Deterministic pipeline + CI-only tectonic (from Phase 85 + v14.0 milestone locks).
- Machine-derived numbers via generated `.tex` macros (milestone-gating: no hardcoded coverage counts).

### Integration Points
- `paper.yml` path-filters on `paper/**`, `python/fdars/_capability_map.json`, `python/fdars/_references_map.json`, `docs/data/**`.
- `coverage_counts.tex` + `refs.bib` are consumed by the manuscript authored in Phase 88.

</code_context>

<specifics>
## Specific Ideas

Milestone-gating constraint: `assert_coverage.py` must exit non-zero on drift and be wired into CI BEFORE any figures/prose are committed. The "introduce a drift → CI fails" success criterion should be demonstrable (a negative test).

</specifics>

<deferred>
## Deferred Ideas

None — infrastructure phase. (REF-FUT-01 uncurated-tail completion remains a v14+ future item, out of scope here.)

</deferred>
