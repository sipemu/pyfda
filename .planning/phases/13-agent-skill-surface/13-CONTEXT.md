---
phase: 13-agent-skill-surface
type: CONTEXT
source: plan-phase inline (no discuss-phase; captured via planning gate)
date: 2026-08-10
---

# Phase 13 Context — Agent Skill Surface

## Goal

Package the interpret→recommend→re-run→compare workflow (built as the Phase 12
MCP surface + Phase 11 advisor) as a **runnable Anthropic Agent Skill**: a
`SKILL.md` + accompanying script that an agent can load and execute end-to-end
against a real dataset, producing grounded advice and a before/after diagnostics
comparison.

## Locked Decisions (captured at planning gate)

- **D1 — No discuss-phase.** Design context captured inline here; plan from
  RESEARCH.md + REQUIREMENTS.md + this file.
- **D2 — Research first.** The Anthropic Agent Skills authoring spec (SKILL.md
  frontmatter, progressive disclosure, bundled scripts/resources) and the skill
  execution-environment options are external, evolving Anthropic docs — ground
  the plan in current docs before authoring.
- **D3 — Execution target = Managed Agents env with `allow_package_managers`
  (ROADMAP-recommended).** At skill run time, `fdars` is made available by
  pip-installing it (`pip install "fdars[mcp]"`, Python ≥3.10) inside the
  Managed Agents execution environment, which permits package managers / network.
  - Rejected: **bundled wheel** (pins platform/Python ABI, bloats package),
    **code-execution container / no-internet** (cannot guarantee fdars presence).
  - The skill's script and SKILL.md must document this runtime clearly enough
    that the skill actually runs (SKILL-02 / Success Criterion 2).

## What Phase 13 builds on (Phase 12 + 11 deliverables)

- `python/fdars/mcp/` — `_registry` (HandleRegistry), `_runner.run_method`
  (5-method dispatch), `_compare.compare_run(dataset_id, method,
  before_result_id, params_after) -> {before, after, delta}`, `server.py`
  (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`,
  `run_stdio`).
- `python/fdars/advisor.py` — `build_diagnostics` (offline, deterministic,
  JSON-serialisable diagnostics for 5 methods) — the grounding source.
- `examples/mcp_recipe.py` — offline end-to-end compare recipe (Python 3.10+,
  no API key, no network) — the closest existing analog to the skill's script.
- Grounding invariant (from Phase 11/12): fdars does every number; the model
  only orchestrates and must cite diagnostics.

## Requirements in scope

- **SKILL-01**: A `SKILL.md` + script packages the interpret→recommend→re-run→
  compare workflow.
- **SKILL-02**: The skill's execution environment (fdars availability) is
  documented so the skill actually runs.

## Success Criteria (from ROADMAP)

1. A `SKILL.md` + accompanying script package the full interpret→recommend→
   re-run→compare loop and reference the Phase 12 tools.
2. The skill's execution environment (how `fdars` is made available at run time)
   is documented clearly enough that the skill actually runs end-to-end.
3. A recorded/dry-run walkthrough shows the skill producing grounded advice and
   a before/after comparison against a real dataset.

## Constraints / notes for the planner

- Python ≥3.10 for the `[mcp]` extra (mcp>=2.0.0); the walkthrough dataset should
  be one already present in `docs/data/` / `fdars.datasets` (e.g. Canadian
  Weather, as `mcp_recipe.py` uses).
- Keep the compute path deterministic; the skill orchestrates the existing tools
  rather than reimplementing any numerics.
- Out of scope (v2.0): HTTP/REST surface, non-Anthropic providers, autonomous
  mutation of user data.
