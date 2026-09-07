---
gsd_state_version: 1.0
milestone: v13.0
milestone_name: Scientific Provenance & Cross-Language Implementations
current_phase: 82
current_phase_name: MCP Tool `fdars_method_references` + GATE-05 Companion
status: planning
stopped_at: Phase 81 complete, ready to plan Phase 82
last_updated: "2026-09-07T14:13:07.881Z"
last_activity: 2026-09-07
last_activity_desc: Phase 81 complete, transitioned to Phase 82
state_head: ca843c3e7eb4e36e369bfdda937ea749c1f1af7d
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 7
  completed_plans: 7
  percent: 40
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-07)

**Core value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.
**Current focus:** Phase 81 — Curation — Paper Registry

## Current Position

Phase: 82 — MCP Tool `fdars_method_references` + GATE-05 Companion
Plan: Not started
Status: Ready to plan
Last activity: 2026-09-07 — Phase 81 complete, transitioned to Phase 82

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**

- Total plans completed (v12.0): 27; prior: 29 (v11.0), 7 (v10.0), 17 (v9.0), 16 (v8.0)
- Average duration: -
- Total execution time (v13.0): 0 hours

**By Phase (v13.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 80 | 2 | - | - |
| 81 | 5 | - | - |
| 82 | TBD | - | - |
| 83 | TBD | - | - |
| 84 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 80 P01 | 5 | 3 tasks | 2 files |
| Phase 80 P02 | 2 | 1 tasks | 1 files |
| Phase 81 P01 | 308 | 3 tasks | 2 files |
| Phase 81-curation-paper-registry P02 | 12m | 3 tasks | 1 files |
| Phase 81 P03 | 15 | 3 tasks | 1 files |
| Phase 81 P04 | 9 | 3 tasks | 1 files |
| Phase 81-curation-paper-registry P05 | 289 | 2 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v13.0 roadmap]: Phase numbering CONTINUES from v12.0 (starts at Phase 80; v12.0 ended at Phase 79) — no reset
- [v13.0 roadmap]: 5 phases (80–84), 22 requirements (SCHEMA/CURATE/MCP/DOCS+SKILL/GATE), fine granularity — schema-first (80) unblocks curation (81, critical path) + MCP tool (82, parallelizable) → docs+skill (83) → close gate (84), mirroring the v12.0 sequencing and ARCHITECTURE.md build order
- [v13.0 roadmap]: Code + docs + skill only — NO `fdars-core` bump, NO new PyO3/numerical bindings. Touches `python/fdars/_references_map.json` (NEW), `python/fdars/mcp/server.py`, `.claude/skills/fdars-capabilities/SKILL.md`, `docs/`, `scripts/generate_capability_dataset.py`, `tests/`, maturin include
- [v13.0 roadmap]: References map is a SEPARATE committed side-file (`_references_map.json`), paper-keyed + flat `callable_index`, NOT merged into the auto-generated `_capability_map.json` (preserves the SKILL-02 no-drift boundary; mirrors `_capability_curation.json`)
- [v13.0 roadmap]: MCP tool `fdars_method_references` stays provably LLM-free (GATE-04 → GATE-05): static `importlib.resources` load, `_REFERENCES_MODULES` DERIVED from `_CAPABILITY_MODULES`, no `provider`/`model` keys, explicit `{"curated": false, "sentinel": "NO_CURATED_ENTRY"}` for the tail. Hybrid fallback lives ONLY in the skill, flagged ungrounded
- [v13.0 roadmap]: Curation is PAPER-LEVEL (~40–100 papers, N << 409) with a sub-method-keyed callable index — NOT 409 separate entries, NOT one paper mapped blindly across a family (band depth ≠ modified band depth)
- [v13.0 roadmap]: Six anti-feature families (functional depth as a category, scoring metrics, SPM, seasonal, XAI/explain, conformal) return the `curated:false` sentinel — no forced module-level citation (per-sub-method depth papers may still be curated where a clear root exists)
- [v13.0 roadmap]: Coverage is partial-but-honest — report `N/409` explicitly in tool response, docs, and `llms.txt`; uncovered callables signal `curated:false`, never silence. GATE-05 emits the fraction (informational, not a hard floor this milestone)
- [v13.0 roadmap]: Author-verification is a hard authoring rule — every paper entry checked against its DOI landing page before commit (F&M is 2001, not 1991; a resolving DOI is NOT proof of correct attribution)
- [v13.0 roadmap]: Docs/`llms.txt` emit OFFLINE from committed JSON via `--references` flag (no `fdars` import at build), consistent with the v12.0 `generate_capability_dataset.py --llmstxt` path
- [v13.0 roadmap]: GATE-05 guard tests land in the SAME commit as the tool they guard (GATE-04 lesson); Guard Group 3 (primary A/B Py3.9+, companion C/D Py3.10+) in `tests/test_guard_sync_version_independent.py`
- [standing v6.0]: BLOCKING HUMAN citation-accuracy review before milestone close — parallel to the standing diagram review; consolidated into Phase 84 (GATE-03), autonomous execution stops there
- [standing v6.0/v11.0]: ALL content/doc phases run SEQUENTIALLY on `main` with `use_worktrees: false` — doc-build fences hardcode the main-tree `.venv/bin/mkdocs`; whole-site `--strict` (~25 min) + guard-sync + DOI/link gates run ONCE at the Phase-84 close
- [Phase 80]: GATE-04 atomic commit: _references_map.json + GATE-05 A/B/C guard tests land in one commit (guard tests and artifact cannot be split across CI runs)
- [Phase 80]: FDARS_ONLINE_CHECKS=1 pattern: structural DOI/URL gate runs always in CI; opt-in live-resolve skips the structural gate (inverts the FDARS_INTEGRATION pattern)
- [Phase 80]: docs/authoring/references-schema.md documents the ACTUAL shipped _references_map.json shape (5-paper seed, 11 callable_index entries) with verbatim examples — curators author against what is live
- [Phase 80]: docs/authoring/ not added to mkdocs nav this phase — Phase 83 wires the references docs surface per plan spec
- [Phase 81]: curated:false for ramsay_silverman_2005/gervini_2008/craven_wahba_1979/nadaraya_watson_1964 — DOIs [ASSUMED]/[CITED] not landing-page-verified; eligible for curated:true promotion at Phase 84 human review
- [Phase 81]: _ALLOWED_DOMAINS extended with 9 domains (6 minimum + 3 conditional); coverage denominator derived from live _capability_map.json (437), not hardcoded
- [Phase 81]: All new entries curated:false — personal DOI landing-page verification deferred to Phase 84 GATE-03 human review
- [Phase 81]: fdars-core 0.33 source check: extremal.rs confirms Narisetty & Nair 2016; spatial.rs has no paper attribution; tvdmss cites Huang & Sun 2019 by name
- [Phase 81]: flm_f_test/flm_gof_test curated:false — fdars-core uses classical FPC R² F-test and RESET GoF, not Shen & Faraway 2004
- [Phase 81]: oneway_anova_vstat contested flag: cuesta_albertos_febrero_2010 entry with notes citing both 2010 and Górecki & Smaga 2015 as candidates; curated:false pending Phase 84
- [Phase 81]: clustering.align_cluster_fd wired as co-primary to srivastava_et_al_2011 (callable is in clustering module, not alignment) — fdars-core alignment/clustering.rs cites arXiv:1103.3817
- [Phase 81]: cuturi_blondel_2017 soft-DTW: doi:'' curated:true — PMLR proceedings have no journal DOI; GATE-05 C skips empty doi on curated:true entries
- [Phase 81]: spm.mfpca curated (happ_greven_2018) despite spm anti-feature module — callable has clear paper root per Pitfall 7
- [Phase 81]: _uncurated_spm_tail_2026-09 removed: CURATE-04 sentinel is ABSENCE from callable_index, not a curated:false placeholder entry listing the callables
- [Phase 81]: Coverage finalized at 31/437 (7.1% curated:true) — honest per CURATE-05; no LLM-synthesized placeholder ships as curated

### Pending Todos

None yet.

### Blockers/Concerns

- [milestone shape]: Code + docs + skill ONLY — no `fdars-core` bump, no new bindings. Crosses `python/fdars/_references_map.json` (NEW), `python/fdars/mcp/server.py`, `.claude/skills/fdars-capabilities/`, `docs/`, `scripts/generate_capability_dataset.py`, `tests/`.
- [citation correctness — MILESTONE-GATING]: a wrong attribution (variant conflation, wrong year/authors, textbook where a primary source belongs) is a correctness failure against the "provably correct" core value. Author-verify against DOI landing pages; blocking human review at Phase 84.
- [LLM-free boundary — MILESTONE-GATING]: the MCP tool must never synthesize — static load + `curated:false` sentinel; guard-sync asserts no `provider`/`model` keys and no advisor import. Hybrid fallback lives only in the skill.
- [guard-sync drift]: derive `_REFERENCES_MODULES` from `_CAPABILITY_MODULES` so a future crate-bump adding a submodule cannot silently desync; write the guard test in the same commit as the tool handler.
- [coverage honesty]: report `N/409` in tool, docs, and `llms.txt`; uncovered callables return `curated:false`, never an empty dict.
- [cross-language accuracy / link rot]: mark Matlab (fdaM/PACE) pointers `confidence: low` unless verified; point URLs at specific function docs; pin `version`; structural link gate in CI, online resolve opt-in only.
- [build time]: whole-site `mkdocs build --strict` is ~25 min with executed fences — the `--strict` gate runs only at the Phase-84 close, once.
- [contested attributions — research flag]: `align_cluster_fd`, `elastic_changepoint`, `oneway_anova_vstat`, FAMM lineage — resolve during Phase 81 against fdars-core source; where genuinely contested, flag in-JSON rather than force-pick.

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
| References | REF-FUT-01: complete the uncurated `N/409` tail + a coverage floor once curation stabilizes (partial-but-honest accepted this milestone) | future | v13.0 init |
| References | REF-FUT-02: opt-in live DOI/URL liveness resolve (`scripts/check_doi_liveness.py`, `FDARS_ONLINE_CHECKS=1`) run before close — never in CI | future | v13.0 init |

## Session Continuity

Last session: 2026-09-07T13:51:38.711Z
Stopped at: Phase 81 complete, ready to plan Phase 82
Resume file: None

## Operator Next Steps

- Review the v13.0 roadmap, then plan the first phase with `/gsd-plan-phase 80`
