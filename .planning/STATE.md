---
gsd_state_version: 1.0
milestone: v12.0
milestone_name: Docs Depth, Card Coverage & AI Capability Skill
current_phase: 79
current_phase_name: Close Gate
status: executing
stopped_at: Completed 79-02-PLAN.md (GATE-04 advisor/MCP tests)
last_updated: "2026-09-06T20:43:19.755Z"
last_activity: 2026-09-06
last_activity_desc: Phase 79 execution started
state_head: 91c05cce5553f8101f06c70112d23327ed471c7a
progress:
  total_phases: 6
  completed_phases: 5
  total_plans: 27
  completed_plans: 24
  percent: 83
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-05)

**Core value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.
**Current focus:** Phase 79 — Close Gate

## Current Position

Phase: 79 (Close Gate) — EXECUTING
Plan: 3 of 5
Status: Ready to execute
Last activity: 2026-09-06 — Phase 79 execution started

## Performance Metrics

**Velocity:**

- Total plans completed (v11.0): 29; prior: 7 (v10.0), 17 (v9.0), 16 (v8.0), 11 (v6.0)
- Average duration: -
- Total execution time (v12.0): 0 hours

**By Phase (v12.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 74 | 5 | - | - |
| 75 | 5 | - | - |
| 76 | 3 | - | - |
| 77 | 5 | - | - |
| 78 | 4 | - | - |
| 79 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 74 P01 | 3 | 1 tasks | 1 files |
| Phase 74 P02 | 2 | 1 tasks | 1 files |
| Phase 74 P03 | 214 | 1 tasks | 1 files |
| Phase 74 P04 | 2 | 1 tasks | 1 files |
| Phase 74 P05 | 4 | 1 tasks | 1 files |
| Phase 75-deepen-analyze-family-thin-pages P01 | 203 | 1 tasks | 1 files |
| Phase 75 P02 | 2 | 1 tasks | 1 files |
| Phase 75 P03 | 3 | 1 tasks | 1 files |
| Phase 75-deepen-analyze-family-thin-pages P04 | 2 | 1 tasks | 1 files |
| Phase 75-deepen-analyze-family-thin-pages P05 | 2 | 1 tasks | 1 files |
| Phase 76-flagship-end-to-end-example-pages P01 | 3 | 1 tasks | 3 files |
| Phase 76-flagship-end-to-end-example-pages P02 | 3 | 1 tasks | 3 files |
| Phase 76-flagship-end-to-end-example-pages P03 | 180 | 1 tasks | 3 files |
| Phase 77-section-landing-card-coverage P01 | 12 | 1 tasks | 3 files |
| Phase 77 P02 | 155 | 1 tasks | 4 files |
| Phase 77 P03 | 2 | 1 tasks | 6 files |
| Phase 77 P04 | 20 | 1 tasks | 9 files |
| Phase 77-section-landing-card-coverage P05 | 4 | 1 tasks | 4 files |
| Phase 78 P01 | 315 | 3 tasks | 4 files |
| Phase 78 P02 | 150 | 2 tasks | 1 files |
| Phase 78 P03 | 5min | 2 tasks | 4 files |
| Phase 78-ai-capability-discovery-skill P04 | 5 | 3 tasks | 3 files |
| Phase 79-close-gate P01 | 7 | 1 tasks | 0 files |
| Phase 79 P02 | 2 | 1 tasks | 0 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v12.0 roadmap]: Phase numbering CONTINUES from v11.0 (starts at Phase 74; v11.0 ended at Phase 73) — no reset
- [v12.0 roadmap]: 6 phases (74–79), 20 requirements, fine granularity — DEPTH split into two disjoint page-family phases (74 regression-family / 75 analyze-family) → EXMP flagship examples (76) → CARD thumbnails/cards (77) → SKILL capability skill (78) → GATE close (79)
- [v12.0 roadmap]: Docs + skill only — NO `fdars-core` bump, NO new PyO3 bindings (v7.0/v10.0 precedent); package version may tick at close (release handoff stays human-gated)
- [v12.0 roadmap]: ALL content/doc phases run SEQUENTIALLY on `main` with `use_worktrees: false` — doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path; a worktree executor builds the wrong tree and fails verification (v6.0/v11.0 standing decision; config already set)
- [v12.0 roadmap]: The whole-site `mkdocs build --strict` gate (GATE-01), the SVGO/determinism gate (GATE-02), and the blocking human diagram review (GATE-03) run ONCE, consolidated in the final Phase 79 — NOT per content phase (~25-min build; v10.0 whole-set-review-beats-fragmented lesson)
- [v12.0 roadmap]: DEPTH-03 (offline-fence + method-accuracy sweep for the DEPTH pages) mapped to the close phase (79) where all fences are proven green at once via the whole-site strict build; Phases 74/75 still carry per-page FDARS_FENCE_OK success criteria
- [v12.0 roadmap]: SKILL work (Phase 78) is code+docs and independent of the DEPTH/CARD content work; scheduled before the gate to keep Phase 79 a pure close phase. SKILL-04's MCP capability tool must stay provably LLM-free with guard/tests updated (GATE-04)
- [v12.0 roadmap]: Card gaps are all missing thumbnails — each new card needs a hand-authored inline SVG at `docs/assets/thumb/<page-slug>.svg` + a `fdars-gallery` card entry in the section `index.md`; concept SVGs for the thin pages already exist (thumbnails are the smaller decorative versions)
- [v12.0 roadmap]: Advisor (7) + sklearn (5) landing-page galleries are DEFERRED (CARD-FUT-01) — deliberate no-gallery text pattern, separate design call
- [standing v6.0]: Blocking human diagram method-accuracy review before milestone close (the hypograph/epigraph lesson) — consolidated into Phase 79 (GATE-03)
- [Phase 74]: frechet-regression.md restructured as DEPTH-01 tracer; pattern proven end-to-end: When-to-use + numbered sections + FDARS_FENCE_OK fences + html figure + See-also; all 6 API errors corrected
- [Phase 74]: predict_fof arg order: new_x is THIRD positional arg (before argvals); fof_cv uses ncomp_x_max/ncomp_y_max; fof_re_regression has max_iter/tol and 13-key return dict
- [Phase 74]: additive-sof.md rewritten to parity: corrected fam/gsam auto defaults (ncomp=0/bandwidth=0.0), fixed model_selection_ncomp max_comp param, expanded variable_selection to 9-key dict, added GKAM iterations+r_squared
- [Phase 74]: concurrent-regression.md: manual prediction via beta_curve matrix algebra (no predict_ function); bandwidth-CV must be coded manually (no fregre_np_cv for concurrent model)
- [Phase 74]: Phase 74 COMPLETE: all 5 regression-family thin pages at full parity (DEPTH-01) — frechet-regression, function-on-function, additive-sof, concurrent-regression, functional-glm; API accuracy corrected; 4+ fences + 3+ admonitions + When-to-use + See-also per page
- [Phase 74]: functional-glm.md gaussian fence: use FPC-score construction (scores @ phi basis) instead of ad-hoc sin+cos curves to avoid Cholesky singularity in fregre_lm; correlation of fitted values proves equivalence
- [Phase 75]: functional-time-series.md restructured to UNNUMBERED mature analyze template; all 8 FTS API errors corrected (ftsm_update arg order, max_lag, ACF/PACF return dict, ar_models, spectral_density full-spectrum, dpca no-order, long_run_covariance default None); 3 exec fences + 8 admonitions + When-to-use + See-also; both verify gates pass (DEPTH-02 tracer proven)
- [Phase 75]: inverse_lqd documented with 3-argument signature (psi, t_grid, target_argvals) — no 2-argument form
- [Phase 75]: quantile-grid mismatch addressed in warning admonition, prose, and round-trip fence shape print
- [Phase 75]: multi-domain.md: dense_flmm/multi_famm take plain numpy arrays; PyMultiFunData is standalone container only in fdars-core 0.33
- [Phase 75]: shapelets.md (DEPTH-02): discover_shapelets returns summary dict {n_shapelets, quality} — NOT a list of arrays; shapelet_distance returns (float, int) tuple (min_distance, best_offset) — NOT scalar; full search-space params documented; ncomp PCA documented for shapelet_classifier_fit
- [Phase 75]: DBSCAN eps selection via sorted k-NN distances from result distances matrix — the natural visual for advanced clustering
- [Phase 75]: FunFEM ncomp=10 default (not 3) documented; soft membership rows sum to 1 contrasts with KCFC hard labels
- [Phase 75]: align_cluster_fd use_amplitude_only=True default and warning on False performance added
- [Phase 76]: wasserstein_barycenter (not frechet_mean) is the correct density unconditional mean — frechet_mean does not support space='density' in the current binding
- [Phase 76]: EXMP-02 tracer complete: all three fences emit FDARS_FENCE_OK offline; np.asarray(result['predicted']) + xout.reshape(-1,1) + np.clip before normalize_density pattern established
- [Phase 76]: EXMP-01: PVE for FTSM components computed from scores.var(axis=0), not fit['weights'] (quadrature vector) — verified by structural antipattern gate in node check
- [Phase 76]: 3-class phoneme subset (aa/sh/dcl, 30/class, max_candidates=200) for fast offline fences with honest 72-78% accuracy framing
- [Phase 77]: Align gallery carded to 100% as tracer: banded-alignment (Sakoe-Chiba band corridor) and shift-registration (dual-offset hump + arrow) thumbnails authored in #fd7e14, both SVGO-idempotent and render clean
- [Phase 77]: interpolation.svg simplified from 1667 to 1150 bytes: filled circles + vertical tick lines replace separate open-circle + tick-mark elements
- [Phase 77]: Functional-GLM two-panel split at x=115/168 fits the predictor-arrow-outcome sketch under 1200 bytes
- [Phase 77]: Function-on-function: contour arcs in bounding rectangle represent bivariate β(s,t) surface with minimal element count
- [Phase 77]: functional-boxplot: solid fill-opacity paths instead of linearGradient to stay under 1300 byte limit
- [Phase 77]: No ex- prefix on 3 new example thumbnails — verified against mkdocs.yml nav slugs
- [Phase 77]: Used fill-opacity instead of linearGradient in tolerance-vs-conformal.svg to stay under 1300-byte limit
- [Phase 78]: _Fdata entry in capability map uses __init__ key + sorted public methods on fdars.Fdata class; no-drift test strips when curation fields to avoid spurious failures
- [Phase 78]: SKILL.md body avoids fdars.plot / fdars.advisor dotted notation in Optional Extras — verify gate rejects fdars.<mod> tokens not in capability map keys
- [Phase 78]: docs-emit path reads committed _capability_map.json (no fdars import at build time) — docs build stays independent of compiled extension
- [Phase 78]: AI Capability Map placed as top-level nav entry adjacent to AI Advisor; llms.txt gets no nav entry (static passthrough only)
- [Phase 78]: fdars_list_capabilities is LLM-free: loads committed JSON via importlib.resources, no model call, no provider/model keys in return, frozenset allowlist enforced before load (T-78-08)
- [Phase 78]: GATE-04 three-way literal mirror: server._CAPABILITY_MODULES == JSON submodule keys == test _EXPECTED_CAPABILITY_MODULES, enforced by Py3.9-safe primary guard-sync test
- [Phase 79]: GATE-02 PASS: 0/21 thumbnails unstable, 0/101 diagrams unstable under npx svgo@3.3.4 two-pass idempotence check
- [Phase 79]: GATE-04 passes on current HEAD before version bump: 76 advisor/MCP/guard-sync tests green (0 failed); grounding invariant + MCP LLM-free boundary confirmed intact after SKILL-04

### Pending Todos

None yet.

### Blockers/Concerns

- [milestone shape]: Docs + skill ONLY — no `fdars-core` bump, no new bindings. Crosses `docs/`, `docs/assets/thumb/`, `.claude/skills/` (new non-advisor skill), `python/fdars/mcp/` (capability tool only), tests.
- [build time]: whole-site `mkdocs build --strict` is ~25 min with executed fences — keep fence datasets small; the `--strict` gate runs only at the Phase-79 close, once.
- [grounding invariant / MCP LLM-free]: SKILL-04's MCP capability tool must stay provably LLM-free (describes the static surface only; NO new LLM logic); advisor/MCP guard-sync tests must stay green after it lands (GATE-04).
- [capability-skill non-duplication]: the new capability-discovery skill is the FIRST non-advisor skill — it must complement, not duplicate, the existing narrow `fdars-advisor` skill/MCP surface.
- [card pattern]: new thumbnails must match the existing `aria-hidden` decorative-accessible card pattern and pass SVGO idempotence + build-determinism (CARD-06 / GATE-02).
- [EXMP dataset fit]: EXMP-03 (third flagship example) is conditional on a strong `docs/data/` fit; if none exists, satisfy the "2–3" range with EXMP-01/02 and record the decision.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260905-htx | Add resample/upsample/downsample convenience methods to the Fdata class that build a target evaluation grid and delegate to the existing interpolate() method, then document them (docstrings + MkDocs docs page) | 2026-09-05 | 364910b | [260905-htx-add-resample-upsample-downsample-conveni](./quick/260905-htx-add-resample-upsample-downsample-conveni/) |

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Documentation | CARD-FUT-01: gallery/card grid for the Advisor (7 pages) + sklearn (5 pages) landing pages — deliberate no-gallery pattern today; conversion is a separate design call | future | v12.0 init |
| Documentation | DEPTH-FUT-01: depth sweep of any older thin pages beyond the v11.0-era set surfaced during work | future | v12.0 init |
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
| Release | v11.0 PyPI tag `v0.10.0` push + `/gsd-complete-milestone` + `/gsd-cleanup` handed to user (pending at v12.0 start) | pending | v11.0 close |

## Session Continuity

Last session: 2026-09-06T20:43:19.623Z
Stopped at: Completed 79-02-PLAN.md (GATE-04 advisor/MCP tests)
Resume file: None

## Operator Next Steps

- Review the v12.0 roadmap (`.planning/ROADMAP.md`), then plan the first phase with `/gsd-plan-phase 74`
