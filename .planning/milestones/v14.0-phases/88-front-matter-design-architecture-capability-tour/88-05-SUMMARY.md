---
phase: 88-front-matter-design-architecture-capability-tour
plan: "05"
subsystem: documentation
tags: [latex, fdars, software-paper, availability, conclusion, manu-07]

requires:
  - phase: 88-front-matter-design-architecture-capability-tour
    provides: "88-01 created availability.tex and conclusion.tex stubs and wired \\input{sections/availability} and \\input{sections/conclusion} in paper.tex"

provides:
  - "paper/sections/availability.tex: PyPI install, plot+sklearn extras, Python 3.9-3.14, MIT licence, repository/docs URLs"
  - "paper/sections/conclusion.tex: honest 4-sentence close citing breadth macros + advisor + provenance + comparison table; roadmap-agnostic"

affects: [88-phase-final-review, phase-90-gate]

actuals:
  tokens: 851
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Availability section: all facts verified against pyproject.toml before writing; no invented extras or licences"
    - "Coverage counts in prose referenced only via machine-derived macros (\\nsubmodules, \\npubliccallables, \\ndocpapers, \\nsklearnestimators); no hardcoded integers"

key-files:
  created: []
  modified:
    - paper/sections/availability.tex
    - paper/sections/conclusion.tex

key-decisions:
  - "Used \\nsklearnestimators macro (already in coverage_counts.tex) rather than hardcoding 28 in the availability section"
  - "Included the sklearn extra in availability.tex (verified in pyproject.toml) alongside the plot extra, as it is a user-facing optional install"
  - "Conclusion framed as four sentences (breadth + differentiators + development status); avoided future-commitment language"
  - "Conclusion cites Table~\ref{tab:comparison} for comparison evidence; does not repeat the table contents"

patterns-established:
  - "Availability facts-check pattern: every claim (package name, extras, Python range, licence) traced to pyproject.toml before writing"
  - "Conclusion macro pattern: use \\npubliccallables, \\nsubmodules, \\ndocpapers — never inline integers — for counts that can drift"

requirements-completed: [MANU-07]

coverage:
  - id: D1
    description: "availability.tex states PyPI install, plot extra, sklearn extra, Python 3.9-3.14 (abi3-py39), MIT licence, and repository/documentation URLs — all facts verified against pyproject.toml"
    requirement: MANU-07
    verification:
      - kind: automated_ui
        ref: "grep checks: section header, pip install, PyPI, 3.9, plot, licence; no placeholder/benchmark/venue/timestamp — AVAILABILITY_OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "conclusion.tex closes the paper with breadth (\\npubliccallables/\\nsubmodules macros), advisor differentiator, provenance differentiator, and comparison-table citation; roadmap-agnostic; no benchmark/venue/hardcoded-count/timestamp"
    requirement: MANU-07
    verification:
      - kind: automated_ui
        ref: "grep checks: section header, \\nsubmodules/\\npubliccallables macros, no placeholder/benchmark/venue/hardcoded-count/timestamp — CONCLUSION_OK"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-09
status: complete
---

# Phase 88 Plan 05: Availability and Conclusion Summary

**Availability section (PyPI/plot/sklearn extras/Python 3.9-3.14/MIT) and conclusion (breadth macros + advisor + provenance, roadmap-agnostic) written and verified against pyproject.toml.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-09T00:00:00Z
- **Completed:** 2026-09-09T00:12:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `paper/sections/availability.tex`: states `pip install fdars` (PyPI), the `plot` extra (matplotlib), the `sklearn` extra (scikit-learn + `\nsklearnestimators` estimators via macro), Python 3.9--3.14 with abi3-py39 stable ABI and prebuilt wheels for Linux/macOS/Windows, MIT licence, and the GitHub source and documentation URLs -- every fact verified against `pyproject.toml`
- `paper/sections/conclusion.tex`: closes the paper in four sentences summarising breadth via `\npubliccallables` and `\nsubmodules` macros, naming the grounded advisor and scientific-provenance layer (`\ndocpapers` papers via macro) as differentiators absent from peers, citing `Table~\ref{tab:comparison}`, and noting active development; no benchmark claims, no JOSS/JSS venue promises, no hardcoded integers, no timestamps

## Task Commits

1. **Task 1: availability.tex -- PyPI, extras, Python 3.9-3.14, license** - `5aa5461` (docs)
2. **Task 2: conclusion.tex -- honest, roadmap-agnostic closing** - `38ef630` (docs)

## Files Created/Modified

- `paper/sections/availability.tex` - PyPI install instructions, extras, Python version range, licence, and URLs
- `paper/sections/conclusion.tex` - Four-sentence honest close using coverage macros; roadmap-agnostic framing

## Decisions Made

- Used `\nsklearnestimators` macro (already present in `coverage_counts.tex`) rather than hardcoding 28 in the availability section
- Included the `sklearn` extra in `availability.tex` (verified in `pyproject.toml`) alongside the `plot` extra
- Conclusion cites `Table~\ref{tab:comparison}` for comparison evidence rather than restating facts inline
- Framed development status as "active development" with a URL pointer -- roadmap-agnostic, no timeline commitments

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes introduced (documentation-only changes).

## Issues Encountered

None.

## Next Phase Readiness

- Plan 88-05 satisfies MANU-07; both sections are LaTeX-compilable `\input` fragments with no placeholders
- Phase 90 GATE-04 human read-through remains the backstop for correctness review of all prose sections including these two
- No open items from this plan

---
*Phase: 88-front-matter-design-architecture-capability-tour*
*Completed: 2026-09-09*
