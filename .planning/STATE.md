---
gsd_state_version: 1.0
milestone: v12.0
milestone_name: Docs Depth, Card Coverage & AI Capability Skill
status: planning
last_updated: "2026-09-05T00:00:00.000Z"
last_activity: 2026-09-05
progress:
  total_phases: 6
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-05)

**Core value:** The documentation — diagrams first, examples second — must make functional data analysis in `fdars` visually clear and provably correct: every diagram faithfully depicts what the method actually does, and every example runs against the current API.
**Current focus:** v12.0 roadmap created (Phases 74–79) — docs + skill milestone. Next: plan Phase 74 via `/gsd-plan-phase 74`.

## Current Position

Phase: 74 — Deepen Regression-Family Thin Pages (not started)
Plan: —
Status: Roadmap created; ready to plan Phase 74
Last activity: 2026-09-05 — v12.0 roadmap written (6 phases, 20 requirements mapped, 100% coverage)

## Performance Metrics

**Velocity:**

- Total plans completed (v11.0): 29; prior: 7 (v10.0), 17 (v9.0), 16 (v8.0), 11 (v6.0)
- Average duration: -
- Total execution time (v12.0): 0 hours

**By Phase (v12.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 74 | TBD | - | - |
| 75 | TBD | - | - |
| 76 | TBD | - | - |
| 77 | TBD | - | - |
| 78 | TBD | - | - |
| 79 | TBD | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

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

Last session: 2026-09-05
Stopped at: v12.0 roadmap created (Phases 74–79)
Resume file: None

## Operator Next Steps

- Review the v12.0 roadmap (`.planning/ROADMAP.md`), then plan the first phase with `/gsd-plan-phase 74`
