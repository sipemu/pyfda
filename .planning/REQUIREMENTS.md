# Requirements: pyfda — v2.1 Document the AI Advisor

**Defined:** 2026-08-11
**Core Value:** The documentation must make functional data analysis in `fdars` visually clear and provably correct — every diagram faithfully depicts what the method does, every example runs against the current API.

## v1 Requirements

Requirements for milestone v2.1. Each maps to roadmap phases. All docs must stay
method-accurate against the shipped v2.0 code (`python/fdars/advisor.py`,
`python/fdars/mcp/`, `.claude/skills/fdars-advisor/`) and use existing datasets
in `docs/data/`.

### Concept & Overview

- [ ] **CONCEPT-01**: Reader can open a top-level "AI Advisor" overview page explaining what the advisor is, the three surfaces (Python / MCP / Agent Skill), and when to use it
- [ ] **CONCEPT-02**: Overview page explains the grounding invariant — fdars computes every number, the LLM only interprets and cites diagnostic values
- [ ] **CONCEPT-03**: Overview page documents installation extras (`[advisor]`, `[mcp]`) and the offline-core vs. env-gated LLM (`ANTHROPIC_API_KEY`) boundary

### Python API

- [ ] **PYDOC-01**: Reader can follow a Python API page covering `build_diagnostics`, `advise`, and `describe_cluster_differences` (signatures, arguments, returns)
- [ ] **PYDOC-02**: Page includes a worked example that runs in the docs build — offline `build_diagnostics` against a `docs/data/` dataset
- [ ] **PYDOC-03**: Page documents the recommend-only nature and the `Advice` schema fields (`action` / `kind` / `rationale` / `expected_effect` / `evidence`)

### Tool / MCP Server

- [ ] **MCPDOC-01**: Reader can follow an MCP server page listing the three tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`) and their roles
- [ ] **MCPDOC-02**: Page documents stdio setup (`run_stdio`) and the by-reference handle model (arrays stay in the registry)
- [ ] **MCPDOC-03**: Page walks the agentic re-run / compare before-after loop with a concrete example

### Agent Skill

- [ ] **SKILLDOC-01**: Reader can follow an Agent Skill page covering git-URL install and the interpret→recommend→re-run→compare walkthrough
- [ ] **SKILLDOC-02**: Page documents the skill's execution environment / compatibility requirements (Python 3.10+, package-manager access)

### Diagrams

- [ ] **ADVDIA-01**: New hand-authored inline SVG diagram of the grounding invariant, to `STYLE_SPEC` standard, passing the SVGO/determinism CI gate
- [ ] **ADVDIA-02**: New hand-authored inline SVG diagram of the advisor loop (interpret→recommend→re-run→compare), to `STYLE_SPEC` standard

### Nav & Build Integration

- [ ] **NAVDOC-01**: New top-level "AI Advisor" section wired into `mkdocs.yml` nav, containing the pages above
- [ ] **NAVDOC-02**: All new pages build cleanly and every executable code fence runs against the current API in the docs build

## v2 Requirements

Deferred to future releases. Tracked but not in this roadmap.

### Accessibility

- **A11Y-01**: Long-form `<title>`/`<desc>` + `aria-labelledby` for complex diagrams

### Examples

- **EX2-01**: Editorial consolidation of worked examples (sonar-tsrvf vs phoneme-shape; Andrews-wine series)

### Transport

- **HTTP-01**: HTTP/SSE MCP transport for the fdars-advisor server (stdio-only shipped in v2.0)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Advisor code changes | Docs milestone — code changes only if the docs expose a genuine binding bug |
| HTTP/SSE MCP transport | Deferred from v2.0; not a documentation deliverable |
| Programmatic/tool-generated diagrams | Diagrams stay hand-authored inline SVG (project constraint) |
| Dark-mode / theming rework of SVGs | Not part of this milestone's intent |
| New advisor capabilities / task families | Documenting the shipped v2.0 surface, not extending it |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONCEPT-01 | Phase 14 | Pending |
| CONCEPT-02 | Phase 14 | Pending |
| CONCEPT-03 | Phase 14 | Pending |
| ADVDIA-01 | Phase 14 | Pending |
| ADVDIA-02 | Phase 14 | Pending |
| PYDOC-01 | Phase 15 | Pending |
| PYDOC-02 | Phase 15 | Pending |
| PYDOC-03 | Phase 15 | Pending |
| MCPDOC-01 | Phase 16 | Pending |
| MCPDOC-02 | Phase 16 | Pending |
| MCPDOC-03 | Phase 16 | Pending |
| SKILLDOC-01 | Phase 17 | Pending |
| SKILLDOC-02 | Phase 17 | Pending |
| NAVDOC-01 | Phase 18 | Pending |
| NAVDOC-02 | Phase 18 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15 ✓
- Unmapped: 0

---
*Requirements defined: 2026-08-11*
*Last updated: 2026-08-11 after roadmap creation (Phases 14–18)*
