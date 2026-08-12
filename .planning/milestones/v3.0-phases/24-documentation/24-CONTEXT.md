# Phase 24: Documentation - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous smart-discuss — docs-site work against the shipped v3.0 code; follows the established v2.1 advisor-docs pattern)

<domain>
## Phase Boundary

The published AI Advisor docs section reflects provider-agnostic operation and full-library coverage, with executed offline fences running against the real shipped implementation and the docs build staying offline.

In scope (REQ-IDs): DOCS-01, DOCS-02, DOCS-03. This is the FINAL phase of the v3.0 milestone.

Out of scope: any further code changes to the advisor/providers/aspects (Phases 19–23 shipped them); the actual PyPI release/version bump (ship-time).
</domain>

<decisions>
## Implementation Decisions

### Grounded in the existing docs pattern (v2.1) + shipped code

- **DOCS-01 — Provider setup guide.** New page `docs/advisor/providers.md` covering all four backends: Anthropic (default, `ANTHROPIC_API_KEY`), OpenAI + OpenAI-compatible (`base_url` for vLLM/LM Studio/LocalAI, `OPENAI_API_KEY`), Google Gemini (`google-genai`, 3.10+), and local Ollama (no API key). Document selection/precedence (`advise(provider=…, model=…)` params → env `FDARS_ADVISOR_PROVIDER`/`FDARS_ADVISOR_MODEL`/`FDARS_ADVISOR_BASE_URL` + per-provider keys; `provider=None` → Anthropic default) and the optional extras (`pip install fdars[openai|gemini|ollama|all-providers]`). Provider/advise fences are **illustrative only** (NOT executed — no keys/SDKs in the docs build), matching the existing python-api.md "Requires ANTHROPIC_API_KEY — not run in the docs build" convention.
- **DOCS-02 — Per-aspect advisor pages.** New page `docs/advisor/aspects.md` (or a small set) documenting, for every fdars aspect (clustering, smoothing, alignment, basis, fpca, represent, depth, outliers, classification, regression, regression_cv, spm): what `build_diagnostics` computes (the key diagnostics) and the three grounded task families (interpretation / parameter / method). Include a coverage table. Include **executed OFFLINE fences** (`python exec="1" html="1" source="above"` calling `build_diagnostics(...)` with a `FDARS_FENCE_OK` sentinel) for one or two representative aspects to prove the docs run against the real shipped code — keep them key-free/offline (build_diagnostics only, never advise()).
- **DOCS-03 — Overview + Python API updates + strict build.** Update `docs/advisor/index.md` (overview) to reflect provider-agnostic operation + full-library coverage (not just clustering/smoothing/FPCA/alignment/basis), and `docs/advisor/python-api.md` to document the `provider`/`model`/`aspect` params on `advise()` and the full aspect list. Wire the new pages into `mkdocs.yml` (AI Advisor nav section). **`mkdocs build --strict` must pass offline** with all executed fences green against the current implementation.

### Build recipe (from project memory: docs-diagram-verify-workflow)

- Build with the project venv + `PYTHONPATH=scripts` (canonical inline-figure mechanism) + `DOCS_FAST` where applicable, and `mkdocs build --strict`. The executed fences import the real `fdars` (editable install). Keep the build network-free and key-free — only `build_diagnostics` offline fences execute; anything needing a provider/key stays illustrative.

### Claude's Discretion

Whether per-aspect coverage is one consolidated `aspects.md` page vs a few grouped pages; which 1–2 aspects carry an executed fence; exact nav ordering — at Claude's discretion, guided by the existing advisor-docs structure and STYLE_SPEC.
</decisions>

<code_context>
## Existing Code Insights

- `docs/advisor/` — `index.md` (overview), `python-api.md` (recommend-only; has an executed offline `build_diagnostics` clustering fence printing `FDARS_FENCE_OK`; the advise()/LLM part is under a "not run in the docs build" warning), `mcp.md`, `agent-skill.md`.
- `mkdocs.yml:138` — `AI Advisor:` nav section (index / Python API / MCP Server / Agent Skill); `markdown-exec` plugin enabled (line 39).
- Executed fence convention: ```python exec="1" html="1" source="above"``` → import `fdars`, run `build_diagnostics`, print a value + `FDARS_FENCE_OK`. NO `ANTHROPIC_API_KEY`/provider needed.
- Shipped v3.0 code the docs describe: `advise(provider=, model=, aspect=)`; `build_diagnostics` supports 12 aspects; providers = anthropic/openai/gemini/ollama; env `FDARS_ADVISOR_PROVIDER`/`_MODEL`/`_BASE_URL`; extras `[openai]`/`[gemini]`/`[ollama]`/`[all-providers]`.
- `.claude/skills/fdars-advisor/SKILL.md` was updated in Phase 22 (Provider Selection section) — reuse its wording/env-var table for consistency in `providers.md`.
- Per-aspect diagnostics keys are documented in `.planning/research/FEATURES.md` + `.planning/phases/21-per-aspect-advisor-coverage/21-RESEARCH.md` and implemented in `python/fdars/advisor/aspects/*.py` — the source of truth for the per-aspect page.

## Note on branch
Work is on `release/0.3.0` (accumulating v3.0). Merge/rename + PyPI release are ship-time concerns after this final phase.
</code_context>

<specifics>
## Specific Ideas

- Reuse the Phase-22 SKILL.md Provider Selection wording + env-var table in `providers.md` for consistency.
- The per-aspect page's diagnostics tables must match the ACTUAL keys emitted by each `aspects/*.py` builder — derive them from the code, not from memory (FEATURES.md had 8 discrepancies vs the real bindings; trust the shipped builders).
- Verify the strict build: `PYTHONPATH=scripts .venv/bin/mkdocs build --strict` exits 0, offline, with executed fences producing `FDARS_FENCE_OK`.
- Keep every executed fence offline/key-free (build_diagnostics only). Provider/advise examples stay illustrative.
- Follow STYLE_SPEC + existing advisor-page tone; no new SVG diagrams required (this is prose/reference docs).

## Reality check
The strict offline build with executed fences is fully verifiable LOCALLY (unlike Phase 23's multi-Python matrix). Verify it actually runs.
</specifics>

<deferred>
## Deferred Ideas

- Publishing the docs site (gh-pages deploy) → handled by the existing docs CI workflow on merge, not this phase.
- PyPI release carrying the provider extras → ship-time.
</deferred>
