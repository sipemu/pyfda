---
phase: 14-advisor-concept-diagrams
plan: "01"
subsystem: docs/advisor
tags: [documentation, svg, advisor, grounding-invariant, diagrams]
status: complete

dependency_graph:
  requires: []
  provides:
    - docs/advisor/index.md
    - docs/assets/diagrams/advisor-grounding-invariant.svg
    - docs/assets/diagrams/advisor-loop.svg
  affects:
    - docs site (Phase 18 nav wiring will add the AI Advisor section)

tech_stack:
  added: []
  patterns:
    - hand-authored inline SVG conforming to STYLE_SPEC (viewBox 0 0 720 300)
    - SVGO@3.3.4 idempotence gate (pass2 == pass1)
    - MkDocs Material `{ .fdars-diagram }` image include idiom
    - `!!! info` admonition for boundary/install callouts

key_files:
  created:
    - docs/advisor/index.md
    - docs/assets/diagrams/advisor-grounding-invariant.svg
    - docs/assets/diagrams/advisor-loop.svg
  modified: []

decisions:
  - Grounding-invariant diagram uses two-lane metaphor (fdars computes / LLM cites) with explicit "cites" arrow from computed diagnostics into Advice.evidence — matches shipped invariant wording verbatim
  - Advisor-loop diagram: cyclic 4-node flow (interpret→recommend→re-run→compare); Python API exit drawn as dashed grey path from recommend node, visually distinct from orange agentic loop
  - compare node annotated with before/after delta sub-box referencing fdars_compare_run output
  - Overview page stays conceptual/diagram-led; no runnable code fence (first worked example deferred to Phase 15 Python API page)
  - Installation section split into two `!!! info` admonitions: extras table and offline-vs-env-gated boundary

metrics:
  duration: 4min
  completed: 2026-08-11
  tasks_completed: 4
  tasks_total: 4
  commits: 4

estimate:
  tokens: 70000
  raw_tokens: 40000
  tasks: 4
  confidence: med

actuals:
  tokens: 12000
  tasks: 4
  commits: 4
---

# Phase 14 Plan 01: Advisor Concept Diagrams Summary

**One-liner:** Two STYLE_SPEC-conformant inline SVGs (grounding invariant two-lane + advisor loop with Python API exit branch) and a complete AI Advisor overview page method-accurate against `advisor.py`, `mcp/server.py`, and `SKILL.md`.

## What Was Built

### Task 1: Grounding-invariant SVG + minimal page (tracer)

Created `docs/assets/diagrams/advisor-grounding-invariant.svg` — a two-lane diagram:

- **Left lane** (neutral `#f8f9fa`/`#ced4da` panel): fdars computes numbers — data → `build_diagnostics` → numeric diagnostics dict (offline, deterministic, no network/LLM)
- **Right lane** (orange `#fff4ea`/`#fd7e14` accent panel): LLM interprets and cites — `advise()` → `Advice` with `evidence` field highlighted
- **Cites arrow** (orange, curved): drawn from the computed diagnostics into the `Advice.evidence` field, making the invariant literal
- **Divider**: dashed vertical line labelled "boundary / no fabrication"
- `.mono` class labels on all API names: `build_diagnostics`, `advise`, `Advice`, `evidence`

Created `docs/advisor/index.md` as a minimal placeholder embedding the grounding-invariant diagram.

SVGO idempotence gate: PASS (pass2 == pass1).

**Commit:** `5d6a9c6`

### Task 2: Advisor-loop SVG

Created `docs/assets/diagrams/advisor-loop.svg` — cyclic 4-node flow:

- interpret → recommend → re-run → compare → (loop back to interpret)
- Agentic loop enclosed in orange accent panel labelled "MCP / Agent Skill — agentic loop"
- **compare node** annotated with a "before / after delta" sub-box (referencing `fdars_compare_run` output)
- **Python API exit**: dashed grey path from the recommend node, looping above the diagram to a "Python API / recommend-only" box with label "returns Advice, does not re-run"
- `.mono` labels: `advise()`, `fdars_run_method`, `_compare_run`

SVGO idempotence gate: PASS.

**Commit:** `323d0ee`

### Task 3: Full overview prose

Extended `docs/advisor/index.md` with:

- "What the Advisor Does" section — two-stage pattern (offline `build_diagnostics` + grounded `advise`)
- Three-surfaces section: Python API (recommend-only), MCP Server (three tools: `fdars_build_diagnostics` / `fdars_run_method` / `fdars_compare_run` over stdio), Agent Skill (full agentic loop)
- "When to Use" bulleted list: parameter tuning, method choice, interpreting diagnostics, before/after comparison
- "How It Works" section embeds advisor-loop diagram, explains Python API exits after recommend while MCP/Skill continue through re-run and compare
- Installation section with `[advisor]` and `[mcp]` extras and ANTHROPIC_API_KEY boundary

No runnable python/py/pycon code fence — page stays conceptual.

**Commit:** `4d03590`

### Task 4: Grounding-invariant and install-extras prose

Expanded the grounding-invariant section with explicit enforcement details:

- Schema-level enforcement: `Recommendation.evidence` is `list[str]` required by Pydantic — LLM cannot omit it
- System prompt enforcement: instructs model to cite specific values, omit unsupported claims, never fabricate numbers
- Installation: `[advisor]` installs `anthropic>=0.72.0` + `pydantic>=2.0`; `[mcp]` installs `mcp>=2.0.0`, requires Python 3.10+
- Offline boundary: `build_diagnostics` and `run_llm=False` paths work fully offline; `advise` requires `ANTHROPIC_API_KEY`
- Presented as `!!! info` admonitions matching site idiom

**Commit:** `aea9a9a`

## Task 5: Human-verify gate

PENDING — see `## CHECKPOINT` section below. The per-section review gate is the blocking next step before Phase 15 begins.

## Deviations from Plan

None — plan executed exactly as written. Tasks 1–4 completed in order; all SVGO gate checks, acceptance criteria checks, and the task verification commands passed.

## Known Stubs

None — the page has no hardcoded placeholder data or fabricated values. Surface-specific pages are linked as "(coming soon — Phase 15/16/17)" which is accurate and intentional per the plan scope.

## Self-Check

- [x] `docs/assets/diagrams/advisor-grounding-invariant.svg` exists and passes SVGO idempotence gate
- [x] `docs/assets/diagrams/advisor-loop.svg` exists and passes SVGO idempotence gate
- [x] `docs/advisor/index.md` exists, embeds both diagrams, names all three surfaces, documents `[advisor]`/`[mcp]` extras + ANTHROPIC_API_KEY boundary, contains no runnable python fence
- [x] No advisor source code modified (`git diff HEAD~4 --name-only` shows only docs/ and .planning/ files)
- [x] All four commits exist in git log

## Self-Check: PASSED
