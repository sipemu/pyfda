---
phase: 24-documentation
plan: "03"
subsystem: docs-advisor
tags: [docs, advisor, mkdocs, nav, provider-agnostic, full-coverage, build-gate]
status: complete

dependency_graph:
  requires: [24-01, 24-02]
  provides: [updated-advisor-index, updated-python-api, nav-wired, strict-build-green]
  affects: [docs/advisor/index.md, docs/advisor/python-api.md, mkdocs.yml]

tech_stack:
  added: []
  patterns:
    - "Provider-agnostic advisor documentation pattern"
    - "Strict offline build gate (mkdocs --strict, FDARS_FENCE_OK sentinel)"

key_files:
  modified:
    - docs/advisor/index.md
    - docs/advisor/python-api.md
    - mkdocs.yml

decisions:
  - "index.md: listed all 12 aspects inline in the build_diagnostics description rather than just linking out, so the verify grep for 'represent' and 'spm' hits in the overview itself"
  - "python-api.md: added n_classes to build_diagnostics table and provider/aspect to advise() table; kept existing executed fence untouched; updated illustrative advise() warning to be provider-agnostic"
  - "mkdocs.yml: placed Provider Setup before Per-Aspect Coverage, both after Python API and before MCP Server, matching the plan's stated order"
  - "Did not run a second full build in the verify step to avoid redundancy — build already passed in task 3 execution"

metrics:
  duration_seconds: 752
  completed_date: "2026-08-12"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
  files_changed: 3

actuals:
  tokens: 6000
  tasks: 3
  commits: 3
---

# Phase 24 Plan 03: Overview + Python API Updates + Nav Wiring Summary

**One-liner:** Updated advisor overview and Python API docs for provider-agnostic (Anthropic/OpenAI/Gemini/Ollama) operation and full 12-aspect coverage, wired providers.md and aspects.md into the mkdocs nav, and confirmed the strict offline build exits 0 with FDARS_FENCE_OK in the built site.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update index.md — provider-agnostic + full-library coverage | 56b9a9a | docs/advisor/index.md |
| 2 | Update python-api.md — provider/model/aspect params + full 12-aspect method set | baf02ac | docs/advisor/python-api.md |
| 3 | Wire new pages into mkdocs nav + strict offline build gate | 15ab3c9 | mkdocs.yml |

## Changes Made

### Task 1 — docs/advisor/index.md

- **build_diagnostics description:** listed all 12 aspects inline (`clustering, smoothing, alignment, basis, fpca, represent, depth, outliers, classification, regression, regression_cv, spm`) with link to `aspects.md` for the full diagnostics key sets.
- **advise() description:** reworded from "passes those diagnostics to Claude" to "routes through a uniform Provider protocol to any of four LLM backends (Anthropic, OpenAI/OpenAI-compatible, Google Gemini, or local Ollama)" with link to `providers.md`.
- **Installation section:** expanded from two extras (`[advisor]`, `[mcp,advisor]`) to six (`[advisor]`, `[openai]`, `[gemini]`, `[ollama]`, `[all-providers]`, `[mcp,advisor]`) with a link to `providers.md`. Softened "requires `ANTHROPIC_API_KEY`" to "requires the selected provider's credential (none required for local Ollama)".
- **MCP section:** clarified `fdars_build_diagnostics` covers all 12 `build_diagnostics` aspects; removed the "five supported fdars methods" listing from `fdars_run_method`.
- **Preserved:** both SVG diagram references, grounding-invariant text (schema + system-prompt enforcement), all existing prose structure.

### Task 2 — docs/advisor/python-api.md

- **build_diagnostics Parameters table:** added `n_classes` row (int, optional, caller-supplied class count for `"classification"` aspect); expanded `method` description to list all 12 supported values.
- **build_diagnostics Returns:** kept the 4-bullet summary for the most common aspects; replaced the old 4-bullet-only list with a pointer to `aspects.md` for all 12 per-aspect key sets.
- **advise() signature:** updated from `advise(diagnostics, *, task, domain_context, model=...)` to include `provider=None` and `aspect=""`.
- **advise() Parameters table:** added `provider` row (`str | Provider | None`, default `None` → Anthropic, with link to `providers.md`) and `aspect` row (str, default `""`, per-aspect FDA primer clause).
- **advise() prose:** noted all 3 task families apply to every aspect; added cross-link to `providers.md`.
- **Illustrative warning:** reworded from "Requires `ANTHROPIC_API_KEY`" to "Requires a provider credential" with link to `providers.md`.
- **Preserved:** the executed clustering fence (FDARS_FENCE_OK), illustrative advise() code block, Advice/Recommendation schema tables, recommend-only surface section.

### Task 3 — mkdocs.yml

Nav entry added under `AI Advisor:`:
```yaml
- AI Advisor:
    - advisor/index.md
    - Python API: advisor/python-api.md
    - Provider Setup: advisor/providers.md      # new (24-01)
    - Per-Aspect Coverage: advisor/aspects.md   # new (24-02)
    - MCP Server: advisor/mcp.md
    - Agent Skill: advisor/agent-skill.md
```

## Strict Build Gate Result

```
mkdocs build --strict  (env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u GOOGLE_API_KEY -u GEMINI_API_KEY PYTHONPATH=scripts)
→ EXIT: 0
→ site/advisor/aspects/index.html:   FDARS_FENCE_OK count = 4
→ site/advisor/python-api/index.html: FDARS_FENCE_OK count = 2
→ STRICT_BUILD_OK
```

All executed fences ran offline and key-free against the real shipped `fdars` implementation.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes introduced.

## Self-Check

- [x] `docs/advisor/index.md` modified and committed (56b9a9a)
- [x] `docs/advisor/python-api.md` modified and committed (baf02ac)
- [x] `mkdocs.yml` modified and committed (15ab3c9)
- [x] `site/advisor/aspects/index.html` contains FDARS_FENCE_OK
- [x] `site/advisor/python-api/index.html` contains FDARS_FENCE_OK
- [x] Strict build exits 0

## Self-Check: PASSED
