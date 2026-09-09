---
gsd_state_version: 1.0
milestone: v14.0
milestone_name: fdars Software Paper — arXiv Preprint
current_phase: 88
current_phase_name: Front Matter, Design/Architecture & Capability Tour
status: executing
stopped_at: "Completed 88-01-PLAN.md (tracer: gen_snippets.py + represent.tex + nsklearnestimators macro + paper scaffold + make/CI wiring)"
last_updated: "2026-09-09T06:04:33.001Z"
last_activity: 2026-09-09
last_activity_desc: Phase 88 execution started
state_head: 3d2315c58348c4f8e4520364a0fcf7f84b20bb74
progress:
  total_phases: 6
  completed_phases: 3
  total_plans: 11
  completed_plans: 7
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-08)

**Core value:** A submission-ready arXiv software paper that makes `fdars`'s breadth and method-accuracy provably clear — every code snippet runs against the current API, every number is machine-derived from the live capability/reference maps, and every figure/table is regenerable by a single command.
**Current focus:** Phase 88 — Front Matter, Design/Architecture & Capability Tour

## Current Position

Phase: 88 (Front Matter, Design/Architecture & Capability Tour) — EXECUTING
Plan: 2 of 5
Status: Ready to execute
Last activity: 2026-09-09 — Phase 88 execution started

## Performance Metrics

**Velocity:**

- Total plans completed (v13.0): 11; prior: 27 (v12.0), 29 (v11.0), 7 (v10.0), 17 (v9.0)
- Average duration: -
- Total execution time (v14.0): 0 hours

**By Phase (v14.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 85 | 2 | - | - |
| 86 | 2 | - | - |
| 87 | 2 | - | - |
| 88 | - | - | - |
| 89 | - | - | - |
| 90 | - | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 85 P01 | 2 | 3 tasks | 5 files |
| Phase 85 P85-02 | 3 | 2 tasks | 10 files |
| Phase 86 P86-01 | 3 | 3 tasks | 6 files |
| Phase 86-single-source-of-truth-wiring-ci-gate P02 | 2 | 2 tasks | 1 files |
| Phase 87 P87-01 | 10 | 3 tasks | 5 files |
| Phase 87 P02 | 5min | 2 tasks | 3 files |
| Phase 88 P01 | 22 | 3 tasks | 10 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v14.0 roadmap]: Phase numbering CONTINUES from v13.0 (starts at Phase 85; v13.0 ended at Phase 84) — no reset
- [v14.0 roadmap]: 6 phases (85–90), 23 requirements (MANU/PIPE/COMP/CASE/GATE/REL), fine granularity — infrastructure-first: scaffold+pipeline (85) → SSoT wiring + CI gate (86, drift tripwires functional before any prose cites a number) → comparison table + evidence (87, highest peer-review-rejection risk, precedes the tour that cites it) → front-matter/design/capability-tour prose (88) → case studies + figures (89, experiment-dependent) → close gate + citable release (90)
- [v14.0 roadmap]: Writing + reproducible-code milestone — NO `fdars-core` bump, NO new numerical bindings. New tree `paper/` at repo root (peer to `docs/`), plus `.github/workflows/paper.yml`, `CITATION.cff`, `comparison_evidence.md`. Reuses `scripts/docs_fig.py`, `docs/data/`, `_capability_map.json`, `_references_map.json`
- [v14.0 roadmap]: REL-01 (citable 0.13.0 release) folds into the close phase (90) alongside GATE-02/03/04 — the release is gated on human read-through approval + metadata finalization, not a standalone ship phase
- [v14.0 roadmap]: natbib + BibTeX (NOT biblatex/biber) — tectonic silently breaks biber in CI (`[?]` citations); decided before the first `paper.tex` commit (locked in Phase 85)
- [v14.0 roadmap]: NO local LaTeX — PDF compile is CI-only via tectonic (`wtfjoke/setup-tectonic@v4`); the local hard gate is the Python reproducible pipeline (empty `git diff paper/figures/` on re-run)
- [v14.0 roadmap]: Every numeric claim machine-derived — coverage counts from `_capability_map.json` via `assert_coverage.py` → `coverage_counts.tex` macros (non-zero on drift, no hardcoded `.tex` integers); bibliography from `_references_map.json` via `gen_refs_bib.py`; every snippet sourced from an executed `paper/code/` script, never hand-copied
- [v14.0 roadmap]: Deterministic matplotlib — `Agg` backend, module-top rcParams, per-figure `np.random.seed`, PDF with suppressed `CreationDate`; determinism gate = empty `git diff paper/figures/`
- [standing v6.0]: BLOCKING HUMAN manuscript read-through before milestone close (GATE-04, Phase 90) — same shape as the standing diagram/citation reviews; autonomous execution stops there
- [standing v6.0/v11.0]: ALL content phases run SEQUENTIALLY on `main` with `use_worktrees: false`
- [Phase 85]: Import fig/FDARS_COLORS from docs_fig (not reimplemented) — reuses established Agg+rcParams block via import side-effect
- [Phase 85]: save_figure() passes metadata={"CreationDate": None} suppressing PDF timestamp so git diff paper/figures/ is empty on re-run (PIPE-02)
- [Phase 85]: Makefile paper targets use plain python (same convention as docs targets); no tectonic invocation — PDF compile is CI-only (Phase 86)
- [Phase 85]: natbib+BibTeX only (NOT biblatex/biber) — tectonic silently emits [?] citations under biber; locked before first paper.tex commit
- [Phase 85]: \date{} left empty in paper.tex — no timestamp macros anywhere in paper.tex or section stubs; deterministic output enforced
- [Phase 85]: CITATION.cff preferred-citation doi field omitted entirely until Phase 90 assigns arXiv ID; identifiers.type=url used instead to avoid schema validation failure
- [Phase 86]: assert_coverage.py mirrors _coverage_counts() from generate_capability_dataset.py exactly; sorted macro keys ensure byte-identical re-runs (PIPE-03)
- [Phase 86]: gen_refs_bib.py emits @misc for all 47 non-uncurated entries (no journal/booktitle in map); cite-key = paper-key verbatim; double-braced titles; conditional doi/url (PIPE-04)
- [Phase 86]: paper.yml step order load-bearing: offline pipeline (gen_figures → assert_coverage --check → gen_refs_bib) before tectonic PDF compile so drift fails fast
- [Phase 86]: wtfjoke/setup-tectonic@v4 with github-token only (no biber-version for natbib+plain BibTeX)
- [Phase 86]: No maturin/fdars install in paper.yml Phase 86 — stdlib-only scripts; Phase 89 will extend for case study scripts
- [Phase 87]: evidence-first authoring: comparison_evidence.md before table; cells from RESEARCH.md dossiers verbatim, not from memory
- [Phase 87]: \FdarsVersion{0.12.0} macro in comparison_table.tex for single-point Phase 90 update to 0.13.0
- [Phase 87]: check_comparison.py SC-3 gate: escaped-ampersand sentinel split + prefix-match evidence lookup for fda 6.3.0 → fda
- [Phase 87]: DIMENSION_SUBMODULES transcribed from RESEARCH.md §fdars Column Derivation — dimension labels match _parse_table() output after _norm() strips LaTeX accents
- [Phase 87]: check_comparison.py added to paper-check recipe only (not paper: generation target); paper.yml step placed after gen_refs_bib and before Setup tectonic
- [Phase 88]: Use LaTeX listings (not minted) for snippet fragments: no -shell-escape, no pygments CI dependency, tectonic-friendly; proven in Phase 88 Plan 01
- [Phase 88]: Add python/fdars/** + src/** to paper.yml path filter so API changes re-trigger snippet drift gate (Pitfall 5 prevention, Phase 88 Plan 01)

### Pending Todos

None yet.

### Blockers/Concerns

- [milestone shape]: Writing + reproducible-code ONLY — no crate bump, no new bindings. New tree `paper/` (`paper.tex` + `sections/` + `refs.bib` + `figures/` + `code/`), `.github/workflows/paper.yml`, `CITATION.cff`, `comparison_evidence.md`.
- [stale API snippets — HIGHEST RISK]: every `.tex` snippet must flow from an executed `paper/code/` script (never copy-pasted); the pipeline runner is the hard local gate, re-verified at Phase 90 (GATE-02).
- [hardcoded coverage counts — MILESTONE-GATING]: derive all numbers as `\input{coverage_counts.tex}` macros; `assert_coverage.py` exits non-zero on drift; wired into CI before figures are committed (Phase 86).
- [inaccurate peer-comparison rows — reviewer-rejection risk]: ground every competitor cell in `comparison_evidence.md` (URL + version + date); ≥1 peer package spot-checked; blocking human review at Phase 90.
- [non-deterministic matplotlib]: `Agg` + fixed rcParams + per-figure seed + suppressed `CreationDate`; FreeType/font variance across platforms is the residual risk — generate/verify figures in CI (Phase 86/89 determinism gate).
- [tectonic + biblatex silent bib failure]: natbib + BibTeX only; locked before the first `paper.tex` commit (Phase 85).
- [arXiv self-containment]: close gate must test a clean-dir `pdflatex + bibtex` build with all figures committed under `paper/figures/` (GATE-03, Phase 90).
- [`journal` field missing in `_references_map.json`]: `gen_refs_bib.py` needs a resolved strategy (add venue during a curation pass, or emit `@misc`) — resolve in Phase 86.
- [FTS dataset structure]: verify `canadian_weather_precip.csv` slicing supports the forecast case study before the figure script — resolve in Phase 89.
- [package tick]: reversible 0.12.0 → 0.13.0 pairs with the citable release (REL-01); semver `v0.13.0` tag triggers PyPI publish — handed to user at Phase 90 close.

### Research Flags (from SUMMARY.md)

- Phase 86: verify tectonic caching + path-filter behavior (cache hit/miss when the library changes but `paper/` doesn't) before deploying `paper.yml`.
- Phase 87: spot-check peer-package coverage facts (scikit-fda `check_estimator` status, FDApy v1.x, R refund) against CRAN/PyPI/arXiv before finalizing the table.
- Phase 89: confirm `canadian_weather_precip.csv` structure supports multi-year slicing for the FTS case study before writing the figure script.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Venue | VENUE-01: JOSS short-form draft (750–1750 words, "state of the field") derived from the arXiv manuscript | future | v14.0 init |
| Venue | VENUE-02: JSS/SoftwareX full-template reshaping with complete API reference | future | v14.0 init |
| References | REF-FUT-01: complete the uncurated `N/437` tail + a coverage floor once curation stabilizes | future | v13.0 init |
| References | REF-FUT-02: opt-in live DOI/URL liveness resolve (`FDARS_ONLINE_CHECKS=1`) run before close — never in CI | future | v13.0 init |
| Documentation | CARD-FUT-01: gallery/card grid for the Advisor + sklearn landing pages | future | v12.0 init |
| Documentation | DEPTH-FUT-01: depth sweep of any older thin pages beyond the v11.0-era set | future | v12.0 init |
| verification_gap | Phase 59 closed via override — no formal `59-VERIFICATION.md`; deliverables shipped | acknowledged | v9.0 close |
| diagram_review | DOCS-03 blocking human diagram review never explicitly approved — now moot (SVG live) | acknowledged | v9.0 close |
| Diagrams | DIAG-FUT-01b: full dark-mode / theming adaptation of the diagram set | future | v10.0 init |
| Diagrams | DIAG-FUT-03: palette / typography re-theme | future | v10.0 init |
| sklearn | FUT-01: `set_output(transform="pandas")` / DataFrame output API | future | v9.0 init |
| sklearn | FUT-02: re-evaluate EXCLUDED methods if fdars-core exposes stored-model/template-free variants | future | v9.0 init |
| sklearn | FUT-03: sklearn 1.7+ support once Python 3.9 is dropped | future | v9.0 init |
| SDK | ANTHROPIC-1X: full `anthropic` 1.x migration (drops Python 3.9) — its own milestone | future | v8.0 init |
| Transport | HTTP-01 / FUT-01: HTTP/SSE MCP transport (stdio shipped v2.0) | v3.x/future | v2.0 close |
| Core | `linalg`-gated `ridge_regression_fit` (Rust 1.84+ > MSRV 1.83) | out of scope | v6.0 init |

## Session Continuity

Last session: 2026-09-09T06:04:32.921Z
Stopped at: Completed 88-01-PLAN.md (tracer: gen_snippets.py + represent.tex + nsklearnestimators macro + paper scaffold + make/CI wiring)
Resume file: None

## Operator Next Steps

- Review the roadmap (`.planning/ROADMAP.md`), then plan Phase 85 with `/gsd-plan-phase 85`
