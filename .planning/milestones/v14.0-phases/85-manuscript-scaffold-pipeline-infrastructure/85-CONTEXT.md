# Phase 85: Manuscript Scaffold + Pipeline Infrastructure - Context

**Gathered:** 2026-09-08
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — discuss skipped)

<domain>
## Phase Boundary

A `paper/` project exists with a compiling minimal manuscript skeleton and a deterministic reproducible-code framework, locking every tooling decision (plain `article`, natbib+BibTeX, no timestamp macros, `Agg`/seeded matplotlib, data reuse) that later phases depend on.

Delivers: `paper/paper.tex` (article class, natbib+BibTeX, `\input` section stubs → minimal PDF via CI tectonic); `CITATION.cff` v1.2.0 (`cffconvert`-valid, `preferred-citation` block, author placeholder Simon Müller <sm@data-zoo.de>); `paper/code/paper_utils.py` (reuses `scripts/docs_fig.py` `fig()`/colors, `data_path()` → `docs/data/`, no dataset duplication); one-command Makefile regenerating all pipeline outputs deterministically (Agg backend, module-top rcParams, per-figure `np.random.seed`, suppressed `CreationDate`, empty `git diff paper/figures/` on re-run).

Requirements: MANU-01, MANU-08, PIPE-01, PIPE-02.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase. The tooling decisions are already locked by the ROADMAP goal and success criteria (plain `article` documentclass; natbib+BibTeX, NOT biblatex/biber; no `\today`/timestamp macros; CI-only tectonic PDF build with no local TeX assumed; matplotlib `Agg` backend with module-top rcParams and per-figure seeding; deterministic PDF with suppressed `CreationDate`; datasets resolved via `data_path()` to `docs/data/` with zero duplication). Follow ROADMAP success criteria, the v14.0 milestone locks, and existing codebase conventions.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/docs_fig.py` — existing figure helper (`fig()` factory + color palette) that `paper/code/paper_utils.py` must import and reuse rather than reimplement.
- `docs/data/` — canonical dataset location; `data_path()` resolves against it, no copying.

### Established Patterns
- Deterministic-figure conventions already used in the docs build (seeded RNG, fixed rcParams) — mirror them in the paper pipeline.
- CI-driven build (no local toolchain assumed) — consistent with the tectonic-in-CI decision.

### Integration Points
- `paper/` is a new top-level project directory; figures land in `paper/figures/`, code in `paper/code/`.
- Later phases (86 CI gate, 88 prose, 89 case studies) consume the scaffold, utils, and Makefile targets established here.

</code_context>

<specifics>
## Specific Ideas

Tooling locks are non-negotiable per the v14.0 milestone: natbib+BibTeX (biber/tectonic incompatibility avoidance), CI-only tectonic, deterministic matplotlib. Author block placeholder: Simon Müller <sm@data-zoo.de>.

</specifics>

<deferred>
## Deferred Ideas

None — infrastructure phase.

</deferred>
