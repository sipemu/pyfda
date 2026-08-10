# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.0 — Grounded AI analysis advisor

**Shipped:** 2026-08-10
**Phases:** 4 (10–13) | **Plans:** 11 | **Sessions:** ~2 (2026-08-09 → 2026-08-10)

### What Was Built
- A deterministic, offline `build_diagnostics(result, method, …)` core (five method branches: alignment, fpca, basis, smoothing, clustering) that computes every diagnostic with fdars — no LLM/network dependency.
- A grounded `advise()` layer returning a schema-validated `Advice` via Claude structured outputs (`claude-opus-4-8`), with every recommendation carrying `action`/`kind`/`rationale`/`expected_effect`/`evidence` and citing diagnostic values.
- Four surfaces over that one core: Python API (recommend-only, `[advisor]` extra), Tool/MCP (`fdars.mcp`, `[mcp]` extra, stdio server + `HandleRegistry` by-reference + agentic re-run/compare loop), and an Anthropic Agent Skill (`.claude/skills/fdars-advisor/`).

### What Worked
- **Tracer-first plans.** Every phase opened with an end-to-end tracer plan (e.g. 10-01 schema+one-branch+advise, 12-01 in-process `Client(mcp)` list+invoke) that de-risked integration before breadth was added. Phase 13's tracer even pre-built the Plan 02 deliverables, so wave-2 was green on first run.
- **One deterministic core, many surfaces.** Deciding early that fdars owns all numbers and the LLM only interprets kept the grounding invariant enforceable by a single Pydantic schema + system prompt across all four surfaces — no per-surface re-litigation.
- **Offline-by-default testing.** `[advisor]`/`[mcp]` as optional extras + env-gated LLM tests meant CI stayed network-free and key-free while the real-key path was still covered by human UAT.

### What Was Inefficient
- **Stale CONTEXT artifacts surfaced at close.** Phase 12's "Open questions for research" were answered during execution but never checked off, tripping the pre-close audit and forcing an override_closeout. Marking research questions resolved at phase transition would have avoided it.
- **v1.0 was never formally closed** via `/gsd-complete-milestone`, so its phases lingered as "unstarted" in ROADMAP.md and the v2.0 close needed `--force`. Closing each milestone with the tool keeps the roadmap honest.
- A couple of smoothing-diagnostics edge cases (empty `gcv_values`, single-fit scalars) needed follow-up branches (Branch A-prime) discovered only when the compare loop demanded a non-empty delta.

### Patterns Established
- **Grounding invariant as a hard contract:** schema (`Advice`/`Recommendation`) + system prompt, verified by human UAT — the reusable template for any future LLM surface in this repo.
- **By-reference data passing across tool boundaries** (`HandleRegistry`: dataset/result IDs, never raw arrays through the model) — the pattern for any future MCP/tool work.
- **Optional-extra + env-gate** as the standard way to add an LLM/network dependency without breaking offline CI.

### Key Lessons
1. Resolve and check off phase CONTEXT "open questions" at phase transition — unchecked research questions read as open blockers at milestone close.
2. Close every milestone through `/gsd-complete-milestone` so ROADMAP/REQUIREMENTS stay collapsed and the next milestone doesn't inherit stale state.
3. A single deterministic compute core behind a thin, schema-validated LLM layer is the cheapest way to keep "no fabricated numbers" true across many surfaces.

### Cost Observations
- Model mix: adaptive profile (`claude-opus-4-8` for the advisor runtime + planning; sonnet/haiku for mechanical steps).
- Sessions: ~2 across 2026-08-09 → 2026-08-10; 67 commits.
- Notable: pre-building Plan 02 work inside the Plan 01 tracer (Phase 13) collapsed two waves into one green run.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 — Documentation Overhaul | ~2 | 1–9 | Section-by-section sweeps with per-section review gates; style/determinism/doc-test guardrails established first |
| v2.0 — Grounded AI analysis advisor | ~2 | 10–13 | Tracer-first per phase; one deterministic core fanned out to four surfaces; offline-by-default + env-gated LLM tests |

### Cumulative Quality

| Milestone | Verification | Zero-Dep Additions |
|-----------|-------------|--------------------|
| v1.0 | All diagram/example sections reviewed on built site; SVGO idempotence gate (43 diagrams) | Hand-authored inline SVG only (no new runtime deps) |
| v2.0 | Phase 10 5/5, Phase 11 9/9, Phase 12 4/4 must-haves (111 tests), Phase 13 6 skill tests + human UAT (1 passed, 0 issues) | `anthropic`/`pydantic`/`mcp` all optional extras; core stays offline |

### Top Lessons (Verified Across Milestones)

1. Tracer-first, guardrails-first: prove the end-to-end path (or the CI gate) before adding breadth.
2. Keep the deterministic core dependency-free and gate everything optional (network, LLM, heavy extras) so CI stays fast and offline.
