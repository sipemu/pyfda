---
phase: 47-diagram-coverage-advisor
plan: "01"
subsystem: docs/advisor
tags: [diagrams, advisor, grounding-invariant, svg, style-spec]
dependency_graph:
  requires: []
  provides: [DIACOV-02]
  affects: [docs/advisor/python-api.md, docs/advisor/mcp.md, docs/advisor/providers.md, docs/advisor/agent-skill.md, docs/advisor/aspects.md]
tech_stack:
  added: []
  patterns: [hand-authored-inline-svg, style-spec-conformant, svgo-idempotence-gate, check-adv-gate]
key_files:
  created:
    - docs/assets/diagrams/advisor-python-api.svg
    - docs/assets/diagrams/advisor-mcp.svg
    - docs/assets/diagrams/advisor-providers.svg
    - docs/assets/diagrams/advisor-agent-skill.svg
    - docs/assets/diagrams/advisor-aspects.svg
    - .planning/phases/47-diagram-coverage-advisor/check-adv.sh
  modified:
    - docs/advisor/python-api.md
    - docs/advisor/mcp.md
    - docs/advisor/providers.md
    - docs/advisor/agent-skill.md
    - docs/advisor/aspects.md
decisions:
  - All 5 diagrams use viewBox 0 0 720 480 (480-height; all needed the space for accurate multi-stage flows)
  - advisor-mcp.svg draws the Agent/LLM OUTSIDE the MCP boundary as a caller; only handles + scalars cross stdio (grounding invariant non-negotiable constraint, verified against server.py)
  - advisor-aspects.svg lists all 14 aspects from __init__.py build_diagnostics._supported (correct count; prose says 12+ which is an undercount — code is authoritative)
  - advisor-mcp.svg lists 6 _RUNNABLE_METHODS exactly per server.py (alignment/fpca/basis/smoothing/clustering/depth) — the prose at docs/advisor/mcp.md says 5 but the code has 6 (depth was added in Plan 22-01 per comments in server.py); diagram follows the code
metrics:
  duration: "~7 minutes"
  completed: "2026-08-22"
  tasks_completed: 2
  commits: 2
  files_changed: 11
status: complete
actuals:
  tokens: 12000
  tasks: 2
  commits: 2
---

# Phase 47 Plan 01: Advisor Surface Diagrams Summary

One method-accurate, STYLE_SPEC-conformant hand-authored inline concept SVG added to each of the 5 advisor surface pages (DIACOV-02), all embedded via `.fdars-diagram` near page top, all passing `check-adv.sh` (SVGO idempotence + rsvg PNG gate).

## Diagrams Authored

### 1. advisor-python-api.svg (tracer)

**Method accuracy:** Depicts Stage 1 `build_diagnostics(result, method, argvals=…)` as offline/deterministic/no-LLM, Stage 2 `advise(diagnostics, task=…, domain_context=…)` as LLM-only (interprets and cites, never fabricates), and the full `Advice` schema with all fields (interpretation / recommendations with action+kind+rationale+expected_effect+evidence / caveats). "Returns Advice and STOPS" banner at bottom clarifies the recommend-only boundary explicitly.

**Grounding invariant:** Stage 1 labeled "no network · no RNG · no LLM"; Stage 2 labeled "interprets · cites · never fabricates". No element implies the LLM computes diagnostics.

**Render check:** Clean two-column layout, boundary divider, all text within x∈[8,712], no clipping.

### 2. advisor-mcp.svg (ISOLATED — grounding-critical)

**Method accuracy:** Agent/LLM placed OUTSIDE the orange MCP boundary box as a caller. Inside the boundary: 3 tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`) + `HandleRegistry` (in-process). Arrow labels: "call" (agent→tools), "handle + scalars" (tools→agent). Footer: "NumPy arrays NEVER cross the stdio boundary — only opaque handles and scalar diagnostics." Tool descriptions: `fdars_build_diagnostics` labeled "offline · deterministic · no API key"; `fdars_run_method` shows all 6 runnable methods per `server.py _RUNNABLE_METHODS`: `alignment fpca basis smoothing clustering depth`. Handle formats `ds-<hex>` and `r-<hex>` shown in HandleRegistry.

**Grounding invariant:** The panel header reads "MCP Boundary — fdars computes every number". The Agent/LLM box says "never computes diagnostics (no arrays)". No element inside the boundary implies LLM involvement in computation. Verified against `server.py` — all tool names and method counts correct.

**Code vs. prose discrepancy surfaced:** `docs/advisor/mcp.md` says "Supported methods (all three tools): alignment, fpca, basis, smoothing, clustering (5)" but `server.py _RUNNABLE_METHODS` has 6 (depth was added in Plan 22-01 per inline comments). The diagram follows the code (6 methods). **This is surfaced for Phase 49 human review** — the prose needs updating.

**Render check:** Agent box left of stdio line, MCP boundary panel right, clear visual separation. All text within bounds.

### 3. advisor-providers.svg

**Method accuracy:** `advise(diagnostics, task=…, provider=…, model=…)` at top as sole entry point. `resolve_provider()` shows 3-tier precedence (explicit arg → FDARS_ADVISOR_PROVIDER/FDARS_ADVISOR_MODEL env → anthropic default). Fan-out to 4 adapter boxes: Anthropic (orange, default, `fdars[advisor]`, ANTHROPIC_API_KEY, claude-opus-4-8), OpenAI (`fdars[openai]`, OPENAI_API_KEY, gpt-4o), Gemini (Python 3.10+, `fdars[gemini]`, GEMINI_API_KEY, gemini-2.0-flash), Ollama (local·key-free, `fdars[ollama]`, llama3.2). Subtitle states "MCP tools are compute-only and never call advise()".

**Render check:** Top-down flow diagram, 4 adapter boxes balanced across bottom, all within bounds.

### 4. advisor-agent-skill.svg

**Method accuracy:** Install banner at top (git-URL until fdars 3.0 ships extras). Agentic loop panel: Step 1+3 interpret (`build_diagnostics`, offline/deterministic), Step 4 recommend (`advise()`, labeled "optional · ANTHROPIC_API_KEY"), Step 2+5 re-run (`run_method(ds_id, …)`, returns r-`<hex>`), Step 5 compare (`compare_run(…)`, before/after delta fdars-computed). Loop-back arrow at bottom. Python API contrast panel on right: build_diagnostics → advise() → Advice (returns and STOPS, no re-run, no delta).

**Grounding invariant:** advise() step is marked optional and API-key-gated. The compare_run box notes "fdars-computed" for the delta. No fabricated numbers.

**Render check:** Clear two-panel layout (agentic loop left, Python API contrast right), all text within bounds.

### 5. advisor-aspects.svg

**Method accuracy:** Left column: 14 aspects from `advisor/__init__.py build_diagnostics._supported` (alignment, fpca, basis, smoothing, clustering, depth, outliers, classification, represent, regression, regression_cv, scoring, spm, inference) arranged in two sub-columns. "auto-detect: never / always caller-supplied" note. Below: 6 runnable (supported by `fdars_run_method`) vs 8 diagnostics-only correctly distinguished per `server.py _RUNNABLE_METHODS`. Center: shared pipeline (`build_diagnostics` → `advise` → `Advice`). Right column: 3 task families (interpretation/parameter/method) with examples.

**Prose vs. code:** The aspects.md Coverage Table header says "12+" aspects, but the code has 14. The diagram follows the code. **Surfaced for Phase 49 review.**

**Render check:** Three-column layout clean, all 14 aspects visible, no text bleed.

## Grounding Invariant — How Each Diagram Stays LLM-Free

| Diagram | How LLM-free compute is shown |
|---------|-------------------------------|
| python-api | Stage 1 labeled "no network · no RNG · no LLM"; Stage 2 labeled "interprets · cites · never fabricates" |
| mcp | Agent/LLM drawn OUTSIDE MCP boundary; all compute inside (fdars); footer: "NumPy arrays NEVER cross the stdio boundary" |
| providers | advise() is the only LLM entry point; MCP tools noted as compute-only in subtitle |
| agent-skill | advise() marked "optional · ANTHROPIC_API_KEY"; delta labeled "fdars-computed" |
| aspects | Stage 1 labeled "offline · no LLM · deterministic"; Stage 2 labeled "grounded LLM interpretation" (interprets only) |

## Gate Results

All 5 diagrams pass `check-adv.sh`:
- viewBox `0 0 720 480` — all 5
- `role="img"` + `aria-label` — all 5
- Five CSS classes (`.ttl .sub .lab .sm .mono`) — all 5
- `.fdars-diagram` embed line on page — all 5
- `svgo@3.3.4` idempotence (2nd pass byte-identical) — all 5
- `rsvg-convert` PNG non-empty — all 5
- No whole-site `mkdocs build` run

## Deviations from Plan

### Auto-fixed Issues

None. Plan executed exactly as specified.

### Surfaced for Phase 49 Human Review (judgment-call discrepancies)

**1. [prose vs. code] MCP page says 5 supported methods, server.py has 6**
- File: `docs/advisor/mcp.md` (prose) vs. `python/fdars/mcp/server.py _RUNNABLE_METHODS`
- The MCP page's "Supported methods (all three tools)" list says `alignment, fpca, basis, smoothing, clustering` (5). `server.py _RUNNABLE_METHODS` is `{"alignment", "fpca", "basis", "smoothing", "clustering", "depth"}` (6). `depth` was added in Plan 22-01 per inline comments.
- Diagram follows code (6 methods). Prose update required on docs/advisor/mcp.md.
- Resolution: Phase 49 reviewer to update mcp.md prose to include `depth`.

**2. [prose vs. code] aspects.md Coverage Table header says "12+" aspects, code has 14**
- File: `docs/advisor/aspects.md` vs. `python/fdars/advisor/__init__.py build_diagnostics._supported`
- The code has 14 supported aspects: alignment, fpca, basis, smoothing, clustering, depth, outliers, classification, represent, regression, regression_cv, spm, scoring, inference. The Coverage Table lists all 14 rows correctly, but the intro says "12+".
- Diagram follows code (14 aspects listed). Intro text correction required.
- Resolution: Phase 49 reviewer to update the intro "12+" reference to "14".

## Known Stubs

None — diagrams are method-accurate to the shipped code.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. New SVGs are static documentation assets. The mcp and python-api diagrams actively mitigate T-47-01 (misrepresentation of LLM compute path).

## Self-Check: PASSED

All 11 created/modified files exist on disk. Both commits exist in git log:
- `ae9de9b` feat(47-01): tracer — advisor-python-api.svg + embed + check-adv.sh
- `a7b1b09` feat(47-01): advisor diagrams — mcp, providers, agent-skill, aspects
