---
phase: 86-single-source-of-truth-wiring-ci-gate
plan: "01"
subsystem: paper-pipeline
status: complete
tags: [pipe-03, pipe-04, bibtex, coverage-macros, single-source-of-truth]

dependency_graph:
  requires:
    - "85-01: paper scaffold (paper/paper.tex, paper/refs.bib stub, Makefile paper targets)"
    - "85-02: gen_figures.py + PIPE-02 determinism gate (paper/code/gen_figures.py)"
    - "python/fdars/_capability_map.json (committed map, counting semantics)"
    - "python/fdars/_references_map.json (committed map, 57 papers, callable_index)"
  provides:
    - "paper/code/assert_coverage.py — generate + --check drift tripwire (PIPE-03)"
    - "paper/code/gen_refs_bib.py — BibTeX generator (PIPE-04)"
    - "paper/coverage_counts.tex — 6 \\newcommand macros, committed baseline"
    - "paper/refs.bib — 47 @misc entries, overwrites Phase 85 stub"
    - "\\input{coverage_counts} in paper/paper.tex preamble"
    - "make paper: paper-figures paper-coverage paper-refs one-command pipeline"
  affects:
    - "86-02: CI gate (paper.yml) consumes committed coverage_counts.tex + refs.bib"

tech_stack:
  added:
    - "assert_coverage.py: stdlib (json, pathlib, sys); generate + --check modes"
    - "gen_refs_bib.py: stdlib (json, pathlib, sys); @misc for all 47 entries"
    - "paper-coverage + paper-refs Makefile phony targets"
    - "\\input{coverage_counts} in paper.tex preamble"
  patterns:
    - "Counting semantics mirror scripts/generate_capability_dataset.py:_coverage_counts() exactly"
    - "Cite-key IS the paper-key verbatim (no transformation)"
    - "Title double-bracing {{...}} preserves case under \\bibliographystyle{plain}"
    - "Conditional doi/url emission (no empty-field BibTeX warnings)"
    - "Sorted key order in both generators ensures byte-identical re-runs"

key_files:
  created:
    - paper/code/assert_coverage.py
    - paper/code/gen_refs_bib.py
    - paper/coverage_counts.tex
  modified:
    - paper/refs.bib
    - paper/paper.tex
    - Makefile

decisions:
  - "assert_coverage.py uses frozenset(curated_keys) + callable_index iteration — exact mirror of _coverage_counts(); no reimplementation"
  - "Macro names in sorted order ensure coverage_counts.tex is byte-identical across re-runs"
  - "_render() sorts dict keys alphabetically: ncallables, ncoverage, ndocpapers, nfdata, npubliccallables, nsubmodules"
  - "gen_refs_bib.py iterates sorted(papers) keys for deterministic output"
  - "All 47 non-uncurated entries use @misc (no journal/booktitle/publisher in map — locked strategy from CONTEXT.md)"
  - "paper-coverage and paper-refs targets use PYTHONPATH=$(PAPER_PYTHONPATH) consistent with existing paper-figures"
  - "No tectonic/pdflatex in Makefile — PDF compile is CI-only (GATE-01, Plan 86-02)"

metrics:
  duration: "~3 minutes"
  completed: "2026-09-08"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
  files_created: 3
  files_modified: 3

actuals:
  tokens: 8000
  tasks: 3
  commits: 3
---

# Phase 86 Plan 01: Single-Source-of-Truth Wiring + CI Gate Summary

**One-liner:** Two stdlib-only generator scripts wire `_capability_map.json` + `_references_map.json` to the manuscript — six `\newcommand` macros via `coverage_counts.tex` (PIPE-03 drift tripwire) and 47 `@misc` BibTeX entries in `refs.bib` (PIPE-04), consumed via `\input{coverage_counts}` and `\bibliography{refs}`, regenerable with `make paper`.

## Objective

Wire the two committed JSON maps to the LaTeX manuscript by writing two stdlib-only generator scripts under `paper/code/`, committing their generated outputs (`paper/coverage_counts.tex`, `paper/refs.bib`), consuming those outputs from `paper/paper.tex`, and extending the `make paper` pipeline to regenerate everything in one command.

## What Was Built

### Task 1: assert_coverage.py + coverage_counts.tex (PIPE-03)

`paper/code/assert_coverage.py` mirrors the canonical `_coverage_counts()` from `scripts/generate_capability_dataset.py` exactly:

- **Generate mode**: derives six macros from the committed JSON maps and writes `paper/coverage_counts.tex`
- **`--check` mode**: regenerates content in memory, compares byte-for-byte against the committed file; exits 0 on match, exits 1 on mismatch or absent file

Verified macro values (live against the current maps):
- `\ncallables{437}` — `sum(len(v) for v in cap.values())`
- `\npubliccallables{409}` — sum for non-underscore module keys
- `\nsubmodules{30}` — count of non-underscore top-level keys
- `\nfdata{27}` — non-dunder `_Fdata` methods
- `\ncoverage{28}` — callables backed by at least one curated paper
- `\ndocpapers{47}` — non-`_uncurated` papers in `_references_map.json`

Drift tripwire proven: `--check` exits 1 after deliberate mutation of `coverage_counts.tex` (DRIFT_DETECTED); exits 0 against clean committed file.

### Task 2: gen_refs_bib.py + refs.bib (PIPE-04)

`paper/code/gen_refs_bib.py` generates `paper/refs.bib`:

- Iterates `sorted(papers)` — deterministic output
- Skips 10 `_uncurated_*` placeholder keys
- Emits exactly 47 `@misc` entries (cite-key = paper-key verbatim)
- Double-braced titles (`{{...}}`) preserve case under `\bibliographystyle{plain}`
- Conditional `doi`/`url` emission — no empty-field BibTeX warnings
- `note = {Type: <type>}` carries original paper type for human readers

Overwrites the Phase 85 stub `refs.bib`. Deterministic: re-run leaves empty `git diff`.

### Task 3: paper.tex + Makefile wiring

`paper/paper.tex`: `\input{coverage_counts}` added in preamble before `\begin{document}` — macros defined document-wide; no literal coverage integer in any `.tex` file.

`Makefile`:
- `paper-coverage`: runs `assert_coverage.py` (generate mode)
- `paper-refs`: runs `gen_refs_bib.py`
- `paper`: now depends on `paper-figures paper-coverage paper-refs`
- Both new targets added to `.PHONY`
- No tectonic/pdflatex — PDF compile remains CI-only (GATE-01, Plan 86-02)

## Verification Gates Passed

| Gate | Command | Result |
|------|---------|--------|
| GEN_OK | assert_coverage.py + 6 macro grep + --check | PASS |
| DRIFT_DETECTED | --check after deliberate mutation | PASS (exit 1) |
| REFS_OK | 47 @misc count + no _uncurated + double-braced titles + no empty doi/url | PASS |
| REFS_DETERMINISTIC | re-run after commit → empty git diff | PASS |
| WIRED_OK | \input position + Makefile deps + phony targets + no tectonic | PASS |
| PIPELINE_DETERMINISTIC | full pipeline re-run → empty git diff on all artifacts | PASS |

## Commits

| Hash | Task | Description |
|------|------|-------------|
| `a1337cd` | Task 1 | feat(86-01): add assert_coverage.py + generate coverage_counts.tex (PIPE-03) |
| `7a02aa1` | Task 2 | feat(86-01): add gen_refs_bib.py + regenerate refs.bib with 47 @misc entries (PIPE-04) |
| `e9cc50a` | Task 3 | feat(86-01): wire \input{coverage_counts} into paper.tex + extend make paper |

## Deviations from Plan

None — plan executed exactly as written. The research patterns (Pattern 1 and Pattern 2) were followed verbatim.

## Known Stubs

None. All generated outputs contain real derived values from the committed JSON maps. No hardcoded integers anywhere in `.tex` files.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. Both scripts operate exclusively on committed JSON files in the repo (no user-supplied input). STRIDE mitigations T-86-01 (coverage drift), T-86-02 (_uncurated leak), T-86-03 (empty doi/url) all verified by the automated gates above.

## Self-Check: PASSED

All created files exist on disk. All three task commits found in git log.

| Check | Result |
|-------|--------|
| paper/code/assert_coverage.py | FOUND |
| paper/code/gen_refs_bib.py | FOUND |
| paper/coverage_counts.tex | FOUND |
| paper/refs.bib | FOUND |
| commit a1337cd | FOUND |
| commit 7a02aa1 | FOUND |
| commit e9cc50a | FOUND |
