---
gsd_state_version: 1.0
milestone: v11.0
milestone_name: fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs
current_phase: 69
current_phase_name: Fréchet Regression & Density FDA
status: executing
stopped_at: Completed 69-01-PLAN.md
last_updated: "2026-09-03T19:33:11.925Z"
last_activity: 2026-09-03
last_activity_desc: Phase 69 execution started
state_head: 8dc8799c5f15865d1da6a127a1ac5cb8cc42a156
progress:
  total_phases: 8
  completed_phases: 3
  total_plans: 13
  completed_plans: 10
  percent: 38
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-02)

**Core value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.
**Current focus:** Phase 69 — Fréchet Regression & Density FDA

## Current Position

Phase: 69 (Fréchet Regression & Density FDA) — EXECUTING
Plan: 2 of 4
Status: Ready to execute
Last activity: 2026-09-03 — Phase 69 execution started

## Performance Metrics

**Velocity:**

- Total plans completed: 9 (this milestone); prior: 7 (v10.0), 17 (v9.0), 16 (v8.0), 11 (v6.0)
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 66 | 1 | - | - |
| 67 | 5 | - | - |
| 68 | 3 | - | - |
| 69 | TBD | - | - |
| 70 | TBD | - | - |
| 71 | TBD | - | - |
| 72 | TBD | - | - |
| 73 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| — | - | - | - |
| Phase 66-isolated-crate-bump-regression-gate P01 | 9min | 4 tasks | 5 files |
| Phase 67-functional-time-series-fts P01 | 3 min | 2 tasks | 4 files |
| Phase 67-functional-time-series-fts P02 | 3 min | 2 tasks | 2 files |
| Phase 67-functional-time-series-fts P03 | 3min | 2 tasks | 2 files |
| Phase 67-functional-time-series-fts P04 | 2min | 2 tasks | 2 files |
| Phase 67-functional-time-series-fts P67-05 | 8min | 1 tasks | 1 files |
| Phase 68-function-on-function-scalar-on-function-regression P01 | 2min | 2 tasks | 2 files |
| Phase 68-function-on-function-scalar-on-function-regression P02 | 3min | 3 tasks | 2 files |
| Phase 68-function-on-function-scalar-on-function-regression P03 | 4 min | 3 tasks | 4 files |
| Phase 69-frechet-regression-density-fda P01 | 2min | 2 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v11.0 roadmap]: Phase numbering CONTINUES from v10.0 (starts at Phase 66; v10.0 ended at Phase 65) — no reset
- [v11.0 roadmap]: Isolated-bump → parallel-binding-groups → advisor → docs shape, mirroring v4.0/v5.0/v6.0 scaled to 5 binding families; 8 phases (66–73), 24 requirements, fine granularity
- [v11.0 roadmap]: Phase 66 is an ISOLATED crate bump + regression gate (DEP-01/02/03) — NO new bindings; gates on the full ~772-test suite for 10-minor numeric-drift detection; only Cargo.toml + Cargo.lock change
- [v11.0 roadmap]: Five binding families in separate phases — 67 fts, 68 fof/sof regression, 69 frechet+density, 70 multi-domain/FAMM/clustering, 71 shapelet+GAK; each maps its requirement family 1:1
- [v11.0 roadmap]: Phase 70 (multi-domain/FAMM/SPM) is the ONLY group touching `spm_mod.rs` and has an internal sequential dependency (PyMultiFunData builder MUST precede SPM multivariate extensions) — never share a worktree with another binding phase
- [v11.0 roadmap]: Phase 69 sequences the `extract_ragged_vecs` `convert.rs` refactor (FRE-03) FIRST within the phase, as a prerequisite for the density/Fréchet ragged inputs
- [v11.0 roadmap]: Phases 67/68/69/71 are worktree-parallelizable after 66 lands (disjoint module sets); annotated per-phase in ROADMAP so the executor knows
- [v11.0 roadmap]: Advisor (Phase 72, ADV-01/02) comes AFTER all binding phases — needs the new functions callable; grounding invariant + atomic MCP guard-sync are hard constraints; `frechet` stays diagnostics-only (not `_RUNNABLE_METHODS`)
- [v11.0 roadmap]: Docs (Phase 73, DOCS-01/02/03) is LAST and SEQUENTIAL on `main` (`use_worktrees: false`) — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path; REL-01 (pkg 0.9.0 → 0.10.0 + tag v0.10.0) folds into this close phase
- [standing v6.0]: Blocking human diagram method-accuracy review before milestone close (the hypograph/epigraph lesson)
- [Phase 67-01]: argvals is required positional param in all fts bindings (not Option<...> with default_grid) — upstream validates argvals.len() == n_points — Matches fdars-core fts API contract; avoids silent wrong-grid bugs
- [Phase 67]: 67-02: Combined-function pattern for &FtsmResult inputs — re-fit ftsm internally; private ftsm_result_to_dict helper factored for ftsm+ftsm_update consistency
- [Phase 67]: 67-03: Vec<u32> lags cast to i64; functional_difference returns naked array; col-major cov_matrix reshaped via FdMatrix::from_column_major; FTS-02 complete with 21 passing tests
- [Phase 67]: spectral_density re/im returned as Python lists of (m,m) arrays rather than 3D numpy — users can np.stack() for the 3D form
- [Phase 67-functional-time-series-fts]: FND-02 refactored to subset+registration invariant — parse _submodule_names from git source (not live module), assert Phase-55 baseline subset of current, assert per-name import/attribute registration intact
- [Phase 68-01]: Exclude fpca_x/fpca_y from fof_regression PyDict — internal FPCA state; test asserts key-set
- [Phase 68]: All 5 sof bindings in single file; VarSelectResult.coefficients len relaxed (P+1 upstream); model_selection_ncomp copied verbatim from regression_mod.rs
- [Phase 69-01]: No length-uniformity validation inside extract_ragged_vecs — ragged lengths intentional; caller validates per own contract

### Pending Todos

None yet.

### Blockers/Concerns

- [milestone-wide]: This is a CODE milestone — `fdars-core` bump + new PyO3 bindings + advisor + docs + package bump (v4/v5/v6 precedent), NOT docs-only. Crosses `Cargo.toml`, `src/*_mod.rs`, `src/lib.rs`, `python/fdars/`, `advisor`, `mcp`, `docs/`.
- [numeric drift]: 10-minor jump (0.23→0.33, vs prior 3-minor waves) triples silent-drift risk — Phase 66 isolates the bump and gates on the full ~772-test suite before any binding work; `cargo build` alone is insufficient.
- [research gap]: 0.31/0.32 changelog absent from published CHANGELOG + some 0.33 config-struct fields returned docs.rs 404 — confirm result-struct/config field names against 0.33 source per binding group before writing PyDict converters (research flagged this).
- [transposition]: every new 2D binding needs a non-square (`n_obs ≠ n_points`) fixture — square fixtures hide row-major↔column-major bugs; route all 2D args through `numpy2d_to_fdmatrix`.
- [enum arms]: new `#[non_exhaustive]` enums (`QualityMeasure`, `ShapeletClassifier`, Fréchet metric-space) need an `Err`-returning wildcard arm from day one that raises `ValueError` listing valid variants.
- [grounding invariant]: advisor diagnostics must be fdars-computed native `float`/`int` only (no Python-derived / numpy scalars into `json.dumps`); atomic guard-sync commit; `test_guard_sync_version_independent.py` must pass; MCP compute path stays provably LLM-free.
- [linalg]: stay `parallel`-only (no `linalg`) — user decision; no v11.0 capability needs it (LINALG-01 deferred to Future).
- [build time]: whole-site `mkdocs build --strict` is ~19–25 min with executed fences (5 new submodules add ~10 min) — keep fence datasets small; `--strict` gate runs only at the Phase-73 close.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| verification_gap | Phase 59 (Documentation & Docs Gate) closed via override — no formal `59-VERIFICATION.md`; deliverables shipped (docs live, `--strict` green, tag `v0.9.0` on PyPI) | acknowledged | v9.0 close |
| diagram_review | DOCS-03 blocking human diagram review never explicitly approved — pre-verified method-accurate, now moot (SVG live on published site) | acknowledged | v9.0 close |
| Diagrams | DIAG-FUT-01b: full dark-mode / theming adaptation of the diagram set | future | v10.0 init |
| Diagrams | DIAG-FUT-03: palette / typography re-theme (beyond consistency + defect-fix) | future | v10.0 init |
| sklearn | FUT-01: `set_output(transform="pandas")` / DataFrame output API | future | v9.0 init |
| sklearn | FUT-02: re-evaluate EXCLUDED methods if fdars-core exposes stored-model/template-free variants | future | v9.0 init |
| sklearn | FUT-03: sklearn 1.7+ support once Python 3.9 is dropped (single tags-API path) | future | v9.0 init |
| SDK | ANTHROPIC-1X: full `anthropic` 1.x migration (drops Python 3.9) — its own milestone | future | v8.0 init |
| Transport | HTTP-01 / FUT-01: HTTP/SSE MCP transport (stdio shipped v2.0) | v3.x/future | v2.0 close |
| Core | `linalg`-gated `ridge_regression_fit` (Rust 1.84+ > MSRV 1.83) + HEAD 0.24-bound work | out of scope | v6.0 init |

## Session Continuity

Last session: 2026-09-03T19:33:11.844Z
Stopped at: Completed 69-01-PLAN.md
Resume file: None

## Operator Next Steps

- Plan Phase 66 (isolated crate bump) with /gsd-plan-phase 66
