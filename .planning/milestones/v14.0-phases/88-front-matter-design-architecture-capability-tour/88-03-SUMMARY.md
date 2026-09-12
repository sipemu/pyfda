---
phase: 88-front-matter-design-architecture-capability-tour
plan: "03"
subsystem: paper/sections
tags: [documentation, latex, front-matter, abstract, introduction, statement-of-need]
status: complete

dependency_graph:
  requires:
    - 88-01 (stubs wired into paper.tex)
    - phase-87 (comparison_evidence.md + comparison_table.tex, comparison label tab:comparison)
    - phase-86 (coverage_counts.tex macros: \nsubmodules, \npubliccallables, \nsklearnestimators)
  provides:
    - paper/sections/abstract.tex (filled)
    - paper/sections/intro.tex (filled)
  affects:
    - paper.tex (abstract and intro \input already wired)

tech_stack:
  added: []
  patterns:
    - macro-derived breadth claims (no hardcoded counts)
    - evidence-grounded peer positioning (comparison_evidence.md + Table~\ref{tab:comparison})
    - resolving \citep keys (all keys verified in refs.bib before use)

key_files:
  created: []
  modified:
    - paper/sections/abstract.tex
    - paper/sections/intro.tex

decisions:
  - "Abstract scoped to 5 sentences: FDA motivation, breadth via macros, sklearn compat via \\nsklearnestimators, advisor+provenance differentiator, mission statement — no benchmark claim"
  - "scikit-fda cited in intro using \\citep{ramsay_silverman_2005} (the reference for the broader field is appropriate; the scikit-fda arXiv key is not in refs.bib — honest citation with existing key)"
  - "Introduction subdivided into three logical subsections: statement of need, FDA background, contributions — avoids one monolithic wall of prose"
  - "FDA background cites 8 keys all verified in refs.bib: ramsay_silverman_2005, ramsay_dalzell_1991, yao_muller_wang_2005, srivastava_klassen_2016, marron_..._2015, hormann_kokoszka_2010, hyndman_ullah_2007, ferraty_vieu_2006"

metrics:
  duration_seconds: 90
  completed: 2026-09-09
  tasks_completed: 2
  commits: 2
  files_modified: 2

actuals:
  tokens: 1505
  tasks: 2
  commits: 2
---

# Phase 88 Plan 03: Front Matter (Abstract + Introduction) Summary

**One-liner:** Concise 5-sentence abstract + 3-part introduction grounding the Python FDA gap in Phase 87 evidence, with 8 resolving \citep keys and breadth via \nsubmodules/\npubliccallables macros.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | abstract.tex — concise positioning, no benchmarks | bd1178a | paper/sections/abstract.tex |
| 2 | intro.tex — statement of need, FDA background, contributions | 54847a7 | paper/sections/intro.tex |

## Verification Results

Both automated verification checks passed:

- `ABSTRACT_OK`: abstract.tex has no placeholder, no benchmark claim, no hardcoded count, no venue promise, no \section; cites breadth via \nsubmodules / \npubliccallables / \nsklearnestimators macros
- `INTRO_OK`: intro.tex has \section{Introduction}, Table~\ref{tab:comparison} citation, scikit-fda mention, breadth macros, no hardcoded counts, no benchmark/timestamp/placeholder; all \citep keys resolve in refs.bib

## Content Summary

### abstract.tex

Five sentences:
1. FDA motivation (curves as unit of observation, method families named)
2. fdars breadth: \nsubmodules{} submodules, \npubliccallables{} callables, Rust-accelerated via PyO3 with row-major/column-major conversion
3. sklearn compatibility: \nsklearnestimators{} estimators passing check\_estimator
4. Novel contributions: grounded advisor (fdars.advisor) + machine-readable scientific-provenance layer
5. Mission statement

### intro.tex

Three logical subsections:

**Statement of need:** Frames the Python FDA gap. scikit-fda~0.10.1 is strong but lacks FTS, SPM, conformal, density/Fréchet, sparse PACE, advisor/provenance (grounded in comparison_evidence.md + Table~\ref{tab:comparison}). FDApy~1.0.3 is narrow. R ecosystem fragmented across fda/fda.usc/refund/funData/tidyfun with no single package spanning the surface. Matlab fdaM/PACE partially maintained. fdars positions as the only Python library spanning all families + sklearn + advisor + provenance.

**FDA background:** 5 sentences citing canonical references: random process framing (ramsay_silverman_2005, ramsay_dalzell_1991), basis/sparse PACE (yao_muller_wang_2005), FPCA (ramsay_silverman_2005), elastic registration (srivastava_klassen_2016, marron_ramsay_sangalli_srivastava_2015), FTS + comprehensive surveys (hormann_kokoszka_2010, hyndman_ullah_2007, ferraty_vieu_2006, ramsay_silverman_2005).

**Contributions and roadmap:** Points forward to design (§sec:design), data representation (§sec:represent), capability tour (§sec:capabilities), advisor/provenance (§sec:advisor), availability (§sec:availability).

## Deviations from Plan

None — plan executed exactly as written.

## Threat Mitigations Applied

- T-88-08 (prose asserts unverified peer claim): all peer claims traced to comparison_evidence.md; breadth via macros; no benchmarks
- T-88-09 (unresolved \citep key breaks bibliography): all 8 cite keys verified in refs.bib before use; automated gate passed (INTRO_OK)

## Self-Check: PASSED

- paper/sections/abstract.tex: FOUND
- paper/sections/intro.tex: FOUND
- commit bd1178a: present in git log
- commit 54847a7: present in git log
