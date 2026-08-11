# Roadmap: pyfda

## Milestones

- ✅ **v1.0 — Documentation Overhaul** — Phases 1–9 (shipped 2026-08-08)
- ✅ **v2.0 — Grounded AI analysis advisor** — Phases 10–13 (shipped 2026-08-10)
- 🔵 **v2.1 — Document the AI Advisor** — Phases 14–18 (active)

## Phases

<details>
<summary>✅ v1.0 Documentation Overhaul (Phases 1–9) — SHIPPED 2026-08-08</summary>

Reworked the MkDocs site's hand-authored SVG diagrams and worked example pages to a consistently high, method-accurate standard, on top of new style/determinism/doc-test guardrails.

- [x] Phase 1: Foundation — SVG style spec, SVGO lint gate, deterministic builds, snippets, pytest-markdown-docs, DOCS_FAST (completed 2026-08-07)
- [x] Phase 2: Audit — nav + reference-API audit → diagram coverage map + ranked gap list (completed 2026-08-07)
- [x] Phase 3: learn/ Diagrams — conform, fix coordinate-reuse bug, close gaps (completed 2026-08-08)
- [x] Phase 4: represent/ Diagrams — remove R-era content, conform, close gaps (completed 2026-08-08)
- [x] Phase 5: align/ Diagrams — conform, fix phase-vs-amplitude split, close gaps (completed 2026-08-08)
- [x] Phase 6: analyze/ Diagrams — migrate legacy outliers, conform, close gaps (completed 2026-08-08)
- [x] Phase 7: regression/ Diagrams — redraw conformal band, conform, close gaps (completed 2026-08-08)
- [x] Phase 8: monitoring/ Diagrams — remove R-era content, redraw control limits, close gaps (completed 2026-08-08)
- [x] Phase 9: Examples Sweep — all pages correct against current API, enriched narrative, improved figures, five new examples (completed 2026-08-08)

</details>

<details>
<summary>✅ v2.0 Grounded AI analysis advisor (Phases 10–13) — SHIPPED 2026-08-10</summary>

A deterministic, offline diagnostics core + grounded LLM advisor (interpret → recommend → explain-why) exposed across four surfaces, with the grounding invariant enforced throughout (fdars computes the numbers; the LLM only interprets and cites them).

- [x] Phase 10: Advisor Core Primitive — offline `build_diagnostics` + grounded `advise` (Claude structured outputs) + cluster-difference specialization + `[advisor]` extra (completed 2026-08-09)
- [x] Phase 11: Python API Surface — recommend-only advisor on the public `fdars` API, offline + env-gated tests, `examples/advisor_recipe.py` (completed 2026-08-09)
- [x] Phase 12: Tool / MCP Surface — coarse-grained tools + stdio MCP server + agentic re-run/compare loop (completed 2026-08-09)
- [x] Phase 13: Agent Skill Surface — `SKILL.md` + walkthrough packaging the interpret→recommend→re-run→compare workflow, documented execution environment (completed 2026-08-10)

</details>

### v2.1 — Document the AI Advisor (active)

Give the published MkDocs site first-class, method-accurate coverage of the shipped v2.0 grounded AI advisor. Documentation-only: no advisor code changes unless the docs expose a genuine bug. Every page must stay method-accurate against `python/fdars/advisor.py`, `python/fdars/mcp/`, and `.claude/skills/fdars-advisor/`, use existing datasets in `docs/data/`, and every executable fence must run in the docs build. Work proceeds page-by-page with a per-section review gate.

- [x] **Phase 14: Advisor Concept & Diagrams** - Overview page (what it is, three surfaces, when to use, grounding invariant, install extras) plus both new inline SVG diagrams (completed 2026-08-11)
- [x] **Phase 15: Python API Page** - `build_diagnostics` / `advise` / `describe_cluster_differences` with a runnable offline worked example and the `Advice` schema (completed 2026-08-11)
- [x] **Phase 16: Tool / MCP Server Page** - the three tools, stdio setup, by-reference handle model, and the re-run/compare before-after loop (completed 2026-08-11)
- [ ] **Phase 17: Agent Skill Page** - git-URL install, the interpret→recommend→re-run→compare walkthrough, and execution-environment requirements
- [ ] **Phase 18: Nav & Build Integration** - wire the "AI Advisor" section into `mkdocs.yml` and verify the whole section builds cleanly with all fences executing

## Phase Details

### Phase 14: Advisor Concept & Diagrams

**Goal**: A reader landing on a new top-level "AI Advisor" overview page understands what the advisor is, its three surfaces, when to use it, and the grounding invariant — reinforced by two new hand-authored SVG diagrams that pass the style/determinism gate.
**Depends on**: Nothing (first phase of v2.1)
**Requirements**: CONCEPT-01, CONCEPT-02, CONCEPT-03, ADVDIA-01, ADVDIA-02
**Success Criteria** (what must be TRUE):

  1. The overview page explains what the advisor is, names the three surfaces (Python API / MCP / Agent Skill), and states when to use it, matching the shipped `python/fdars/advisor.py` and `python/fdars/mcp/` behavior
  2. The page explains the grounding invariant in plain terms — fdars computes every number, the LLM only interprets and cites diagnostic values
  3. The page documents the `[advisor]` and `[mcp]` install extras and the offline-core vs. env-gated LLM (`ANTHROPIC_API_KEY`) boundary
  4. A new inline SVG diagram of the grounding invariant renders on the page and passes the SVGO idempotence + determinism CI gate to `STYLE_SPEC` standard
  5. A new inline SVG diagram of the advisor loop (interpret→recommend→re-run→compare) renders on the page and passes the same gate

**Plans**: 1 plan

- [x] 14-01-PLAN.md — Overview page + grounding-invariant & advisor-loop SVGs (SVGO-gated)

**UI hint**: yes

### Phase 15: Python API Page

**Goal**: A reader can follow a Python API page that documents the recommend-only advisor surface and run a worked example that executes offline in the docs build.
**Depends on**: Phase 14
**Requirements**: PYDOC-01, PYDOC-02, PYDOC-03
**Success Criteria** (what must be TRUE):

  1. The page covers `build_diagnostics`, `advise`, and `describe_cluster_differences` with signatures, arguments, and returns accurate against `python/fdars/advisor.py`
  2. The page includes a worked example that runs during the docs build — an offline `build_diagnostics` call against a `docs/data/` dataset (no API key required)
  3. The page documents the recommend-only nature and the `Advice` schema fields (`action` / `kind` / `rationale` / `expected_effect` / `evidence`)
  4. The page builds cleanly and every executable code fence runs against the current API

**Plans**: 1 plan

- [x] 15-01-PLAN.md — Python API page: offline `build_diagnostics` worked example + `advise`/`describe_cluster_differences` reference + `Advice`/`Recommendation` schema tables

### Phase 16: Tool / MCP Server Page

**Goal**: A reader can follow an MCP server page that lists the tools, explains stdio setup and the by-reference handle model, and walks a concrete re-run/compare loop.
**Depends on**: Phase 14
**Requirements**: MCPDOC-01, MCPDOC-02, MCPDOC-03
**Success Criteria** (what must be TRUE):

  1. The page lists the three tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`) and their roles, accurate against `python/fdars/mcp/`
  2. The page documents stdio setup (`run_stdio`) and the by-reference handle model (arrays stay in the registry, tools exchange handles)
  3. The page walks the agentic re-run / compare before-after loop with a concrete example matching the shipped `_runner.py` / `_compare.py` behavior
  4. The page builds cleanly and any executable code fence runs against the current API

**Plans**: 1 plan

- [x] 16-01-PLAN.md — MCP page: three-tool reference + by-reference HandleRegistry model + stdio (run_stdio) setup + concrete re-run/compare before/after loop (illustrative, non-executed fences)

### Phase 17: Agent Skill Page

**Goal**: A reader can follow an Agent Skill page that covers git-URL install, the full interpret→recommend→re-run→compare walkthrough, and the skill's execution-environment requirements.
**Depends on**: Phase 14
**Requirements**: SKILLDOC-01, SKILLDOC-02
**Success Criteria** (what must be TRUE):

  1. The page covers git-URL install and the interpret→recommend→re-run→compare walkthrough, accurate against `.claude/skills/fdars-advisor/` (SKILL.md + walkthrough)
  2. The page documents the skill's execution-environment / compatibility requirements (Python 3.10+, package-manager access)
  3. The page builds cleanly and any executable code fence runs against the current API

**Plans**: 1 plan

- [ ] 17-01-PLAN.md — Agent Skill page: git-URL + future install, Python 3.10+/API-key compatibility, and the interpret→recommend→re-run→compare walkthrough (illustrative, non-executed fences)

### Phase 18: Nav & Build Integration

**Goal**: The "AI Advisor" section is wired into the site nav and the entire section builds cleanly with every executable fence running against the current API.
**Depends on**: Phase 14, Phase 15, Phase 16, Phase 17
**Requirements**: NAVDOC-01, NAVDOC-02
**Success Criteria** (what must be TRUE):

  1. A new top-level "AI Advisor" section appears in `mkdocs.yml` nav containing the overview, Python API, MCP, and Agent Skill pages
  2. The full docs build succeeds with the new section and every new page's executable code fence runs against the current API
  3. All new inline SVG diagrams still pass the SVGO/determinism CI gate in the full build

**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 14. Advisor Concept & Diagrams | 1/1 | Complete    | 2026-08-11 |
| 15. Python API Page | 1/1 | Complete    | 2026-08-11 |
| 16. Tool / MCP Server Page | 1/1 | Complete    | 2026-08-11 |
| 17. Agent Skill Page | 0/1 | Not started | - |
| 18. Nav & Build Integration | 0/? | Not started | - |

---

_Full phase detail for prior milestones is archived in `.planning/milestones/v2.0-ROADMAP.md`. Phase directories are archived under `.planning/milestones/v1.0-phases/` and `.planning/milestones/v2.0-phases/`._
