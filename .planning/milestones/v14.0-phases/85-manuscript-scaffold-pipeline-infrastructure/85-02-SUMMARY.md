---
phase: 85-manuscript-scaffold-pipeline-infrastructure
plan: "02"
subsystem: paper
tags: [latex, manuscript, citation, natbib, bibtex, cff]
dependency_graph:
  requires: [85-01]
  provides: [paper/paper.tex, paper/refs.bib, paper/sections/*.tex, CITATION.cff]
  affects: [phase-86-ci-gate, phase-87-comparison, phase-88-prose, phase-89-casestudies, phase-90-close]
tech_stack:
  added: [natbib, BibTeX, cffconvert]
  patterns: [LaTeX article class, CFF v1.2.0 preferred-citation, section stubs via \input]
key_files:
  created:
    - paper/paper.tex
    - paper/refs.bib
    - paper/sections/intro.tex
    - paper/sections/design.tex
    - paper/sections/represent.tex
    - paper/sections/capabilities.tex
    - paper/sections/comparison.tex
    - paper/sections/casestudies.tex
    - paper/sections/availability.tex
    - CITATION.cff
  modified: []
decisions:
  - "natbib+BibTeX only (NOT biblatex/biber) — tectonic silently emits [?] citations under biber; locked before first paper.tex commit"
  - "\\date{} left empty — no \\today or any timestamp macro anywhere in paper.tex or section stubs"
  - "CITATION.cff preferred-citation uses identifiers.type=url pointing to repo; doi field omitted entirely until Phase 90 assigns arXiv ID"
  - "refs.bib is a stub with a single placeholder entry; gen_refs_bib.py regenerates from _references_map.json in Phase 86"
metrics:
  duration_minutes: 2
  completed_date: "2026-09-08"
  tasks_completed: 2
  tasks_total: 2
  commits: 2
status: complete
actuals:
  tokens: 4500
  tasks: 2
  commits: 2
---

# Phase 85 Plan 02: LaTeX Manuscript Skeleton + CITATION.cff Summary

Authored the minimal LaTeX manuscript skeleton (`paper/paper.tex` using `article` class, natbib + plain BibTeX, seven `\input` section stubs, empty `\date{}`), a stub `paper/refs.bib`, and a `cffconvert`-valid `CITATION.cff` v1.2.0 with a `preferred-citation` block and the Simon Müller author entry.

## What Was Built

### Task 1: LaTeX manuscript skeleton

**paper/paper.tex** — root manuscript file:
- `\documentclass[12pt,a4paper]{article}`
- `\usepackage[numbers,sort&compress]{natbib}` (plain BibTeX, no biblatex/biber)
- Standard packages: `fontenc` T1, `inputenc` utf8, `hyperref`, `url`, `graphicx`, `amsmath`
- Title: "fdars: Functional Data Analysis in Rust with Python Bindings"
- Author: Simon Müller (`\texttt{sm@data-zoo.de}`)
- `\date{}` — intentionally empty, no `\today` or timestamp macro
- Body: `\maketitle`, placeholder abstract, then seven `\input{sections/...}` calls
- Closes with `\bibliographystyle{plain}` and `\bibliography{refs}`

**Seven section stubs** (paper/sections/):
- `intro.tex` — Introduction
- `design.tex` — Software Design and Architecture
- `represent.tex` — Data Representation
- `capabilities.tex` — Capabilities
- `comparison.tex` — Comparison with Related Software
- `casestudies.tex` — Case Studies
- `availability.tex` — Availability and Installation

Each stub contains only a `\section{}` heading and one placeholder sentence. No timestamp macros in any stub.

**paper/refs.bib** — stub with a single valid placeholder BibTeX `@misc` entry. A comment notes that Phase 86's `gen_refs_bib.py` regenerates this file from `_references_map.json`.

Verification gate: `TEX_OK` — all checks passed.

### Task 2: CITATION.cff

**CITATION.cff** — repo-root citation metadata file:
- `cff-version: "1.2.0"`
- `type: software`, `title: fdars`, `version: "0.12.0"`, `date-released: "2026-09-08"`
- `license: MIT`, `repository-code` and `url` pointing to sipemu/pyfda
- Single author: family-names Müller, given-names Simon, email sm@data-zoo.de
- `preferred-citation` block: `type: article`, paper title, same author, `year: 2026`
- `identifiers` entry with `type: url` pointing to the repository (placeholder; arXiv URL added at Phase 90)
- No placeholder `doi` field (omitted entirely to avoid schema validation failure)

Verification gate: `CFF_OK` — `cffconvert --validate` exits zero.

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 | c1a2a9d | feat(85-02): author LaTeX manuscript skeleton and section stubs |
| 2 | 2cfa12f | feat(85-02): add CITATION.cff v1.2.0 with preferred-citation block |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed comment lines that triggered negative grep gates**
- **Found during:** Task 1 verification
- **Issue:** The plan's automated verify gate uses `! grep -qE 'biblatex|...'` and `! grep -rlE '\\today|...'` — both matched comment lines in paper.tex (e.g. `% NOT biblatex/biber` and `% No \date{\today}`).
- **Fix:** Replaced these comment lines with neutral wording that does not mention the forbidden strings but still communicates intent.
- **Files modified:** paper/paper.tex
- **Outcome:** `TEX_OK` gate passes cleanly.

None beyond the comment adjustment above. Plan executed as written.

## Requirements Satisfied

- **MANU-01**: `paper/paper.tex` (article + natbib + BibTeX, seven `\input` stubs, no timestamp macros) authored and verified; CI tectonic compile is the Phase 86 backstop.
- **MANU-08**: `CITATION.cff` v1.2.0 with `preferred-citation` block, author Simon Müller `sm@data-zoo.de`, passes `cffconvert --validate`.

## Known Stubs

The following stubs are intentional and tracked. They are not plan-blocking because the plan's goal is to create the skeleton for later phases to fill:

| Stub | File | Reason |
|------|------|--------|
| Abstract placeholder paragraph | paper/paper.tex (abstract env) | Prose expanded in Phase 88 |
| Intro section placeholder | paper/sections/intro.tex | Prose expanded in Phase 88 |
| Design section placeholder | paper/sections/design.tex | Prose expanded in Phase 88 |
| Represent section placeholder | paper/sections/represent.tex | Prose expanded in Phase 88 |
| Capabilities section placeholder | paper/sections/capabilities.tex | Prose expanded in Phase 88 |
| Comparison section placeholder | paper/sections/comparison.tex | Table + evidence expanded in Phase 87 |
| Case studies section placeholder | paper/sections/casestudies.tex | Figures + narrative expanded in Phase 89 |
| Availability section placeholder | paper/sections/availability.tex | Prose expanded in Phase 88 |
| refs.bib placeholder entry | paper/refs.bib | gen_refs_bib.py regenerates in Phase 86 |

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan creates static files only (LaTeX, YAML, BibTeX). Threat model items T-85-03 and T-85-04 are mitigated:
- T-85-03 (biblatex in paper.tex): verified absent via automated gate
- T-85-04 (timestamp macro in PDF): `\date{}` is empty; no `\today`/`\currenttime` in paper.tex or any section stub; verified via automated gate

## Self-Check: PASSED

- [x] paper/paper.tex exists and passes TEX_OK gate
- [x] paper/refs.bib exists
- [x] paper/sections/ has exactly 7 .tex stubs, each with a `\section{}` heading
- [x] CITATION.cff exists and passes CFF_OK gate (`cffconvert --validate` exits zero)
- [x] Commit c1a2a9d exists (Task 1)
- [x] Commit 2cfa12f exists (Task 2)
