---
phase: 90-close-gate-citable-release
plan: "01"
subsystem: release
tags: [version-bump, maturin, paper, gate02, citable-release, citation]

# Dependency graph
requires:
  - phase: 89-gate02-correctness-completeness
    provides: GATE-02 correctness gate green; all paper artifacts committed and deterministic

provides:
  - "fdars 0.13.0 built and installed (maturin develop --release)"
  - "All 5 version references bumped: Cargo.toml, pyproject.toml, __init__.py, comparison_table.tex, CITATION.cff"
  - "CITATION.cff finalized: version 0.13.0, date-released 2026-09-09, arXiv URL stays PLACEHOLDER"
  - "GATE-02 proven green at 0.13.0: make paper-check + make paper-verify both pass, 0 dangling citations"
  - "Atomic release-prep commit 6f96975 on main; no tag, no push"

affects:
  - 90-02-PLAN.md (push, tag, CI GATE-03, GATE-04 read-through)

actuals:
  tokens: 489
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "make paper regeneration is idempotent; artifacts were already consistent so re-run produced no diff"
    - "paper-verify asserts git diff paper/figures/ empty — byte-stability confirmed at 0.13.0"

key-files:
  created: []
  modified:
    - Cargo.toml
    - pyproject.toml
    - python/fdars/__init__.py
    - paper/sections/comparison_table.tex
    - CITATION.cff

key-decisions:
  - "arXiv URL stays literal PLACEHOLDER in CITATION.cff — no fabricated DOI or arXiv ID (honesty constraint, T-90-02)"
  - "Paper artifacts unchanged by regeneration: snippets, figures, coverage, refs were already at 0.13.0-consistent state"
  - "Single atomic commit covers all 5 version-bump files; no separate commits per task (all gates passed before commit)"

patterns-established:
  - "Version bump order: Cargo.toml -> pyproject.toml -> __init__.py -> comparison_table.tex -> CITATION.cff, then maturin rebuild, then make paper"

requirements-completed: [GATE-02, REL-01]

coverage:
  - id: D1
    description: "All 5 version references read 0.13.0 with no residual 0.12.0 or TODO(REL-01) (REL-01)"
    requirement: REL-01
    verification:
      - kind: integration
        ref: "grep -rnF '0.12.0' Cargo.toml pyproject.toml python/fdars/__init__.py paper/sections/comparison_table.tex CITATION.cff → 0 matches"
        status: pass
    human_judgment: false
  - id: D2
    description: "import fdars reports __version__ == '0.13.0' after maturin rebuild (REL-01)"
    requirement: REL-01
    verification:
      - kind: integration
        ref: "python -c \"import fdars; assert fdars.__version__ == '0.13.0'\" → exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "CITATION.cff keeps arXiv URL as literal PLACEHOLDER (no fabricated DOI/arXiv ID) (REL-01)"
    requirement: REL-01
    verification:
      - kind: integration
        ref: "grep -F 'arxiv.org/abs/PLACEHOLDER' CITATION.cff → match found"
        status: pass
    human_judgment: false
  - id: D4
    description: "GATE-02 correctness gate green at 0.13.0: make paper-check + make paper-verify pass, 0 dangling citations (GATE-02)"
    requirement: GATE-02
    verification:
      - kind: integration
        ref: "make paper-check → assert_coverage OK, gen_refs_bib OK, COMPARISON_TRACE_OK, gen_snippets OK"
        status: pass
      - kind: integration
        ref: "make paper-verify → gen_figures + git diff paper/figures/ empty (exit 0)"
        status: pass
      - kind: integration
        ref: "dangling-citation scan over paper/paper.tex + paper/sections/*.tex vs refs.bib + refs_manual.bib → 0 dangling"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-09
status: complete
---

# Phase 90 Plan 01: Release Prep Summary

**Version bumped 0.12.0 -> 0.13.0 across all 5 source files, fdars rebuilt via maturin, GATE-02 proven green at 0.13.0 with 0 dangling citations and empty figure diff**

## Performance

- **Duration:** 3 min
- **Started:** 2026-09-09T09:55:08Z
- **Completed:** 2026-09-09T09:58:09Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Bumped version 0.12.0 -> 0.13.0 in all 5 source files: Cargo.toml (line 3), pyproject.toml (line 7), python/fdars/__init__.py (line 35 `__version__`), paper/sections/comparison_table.tex (`\FdarsVersion` + removed TODO(REL-01) comment), CITATION.cff (version + date-released 2026-09-09)
- Rebuilt fdars._native via `maturin develop --release` in ~63 seconds; `import fdars; fdars.__version__` reports `0.13.0`
- CITATION.cff arXiv URL preserved as literal `https://arxiv.org/abs/PLACEHOLDER` — no fabricated ID
- Regenerated all paper artifacts via `make paper` — snippets, coverage_counts.tex, refs.bib, and figures were already consistent so no diff produced
- GATE-02 proven green: `make paper-check` (4/4 checks pass), `make paper-verify` (git diff paper/figures/ empty), 0 dangling citations across all `\cite` keys

## Task Commits

All three tasks are captured in a single atomic release-prep commit:

1. **Task 1: Bump every 0.12.0 version reference to 0.13.0** - `6f96975` (chore)
2. **Task 2: Rebuild fdars at 0.13.0 and regenerate all paper artifacts** - `6f96975` (chore, same commit — artifacts unchanged)
3. **Task 3: Prove GATE-02 green at 0.13.0, then commit atomically** - `6f96975` (chore)

**Plan metadata:** (docs commit to follow)

## Files Created/Modified

- `Cargo.toml` - version bumped from 0.12.0 to 0.13.0
- `pyproject.toml` - version bumped from 0.12.0 to 0.13.0
- `python/fdars/__init__.py` - `__version__` bumped from 0.12.0 to 0.13.0
- `paper/sections/comparison_table.tex` - `\FdarsVersion` bumped to 0.13.0; TODO(REL-01) comment removed
- `CITATION.cff` - version 0.13.0, date-released 2026-09-09; arXiv PLACEHOLDER preserved

## Decisions Made

- arXiv URL stays the literal `https://arxiv.org/abs/PLACEHOLDER` in CITATION.cff — real arXiv ID only assigned at submission, fabricating would violate honesty constraint (T-90-02).
- Single atomic commit covers all 5 version-bump files plus the no-op regeneration confirmation; cleaner history than per-task commits when Task 2 produced no artifact diff.
- Paper artifacts were already at a 0.13.0-consistent state (GATE-02 was green from Phase 89), so `make paper` regeneration produced no changes. This is correct behavior — the version string does not embed in snippets or figures directly.

## Deviations from Plan

None - plan executed exactly as written. Paper artifacts did not change on regeneration (already consistent), which is the expected and correct outcome when GATE-02 was previously proven green.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 90-01 is complete. Ready for plan 90-02:
- Push ~112 unpushed commits to origin/main
- `paper.yml` CI runs and compiles the arXiv-equivalent PDF (GATE-03)
- Fetch CI PDF for blocking human read-through (GATE-04)
- On approval: user creates tag v0.13.0 and pushes to trigger PyPI publish

**No blockers.** The local tree is clean, GATE-02 is green, and the atomic release-prep commit is on main.

---
*Phase: 90-close-gate-citable-release*
*Completed: 2026-09-09*
