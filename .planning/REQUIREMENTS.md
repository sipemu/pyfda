# Requirements: pyfda — v8.0 Advisor: New Capabilities

**Defined:** 2026-08-23
**Core Value:** Extend the fdars AI advisor with new agentic capabilities while holding the grounding invariant (fdars computes every number; the LLM only interprets/cites) and the MCP-LLM-free compute boundary as hard constraints.

## v8.0 Requirements

Four new advisor capabilities built on the existing surface (no new runtime deps), foundation-first. Requirements map to roadmap phases (continue numbering from Phase 49 → start at Phase 50).

### Compatibility (pre-flight)

- [x] **COMPAT-01**: `anthropic` dependency pinned `>=0.72.0,<1.0` so the existing advisor keeps importing on Python 3.9 (abi3-py39); anthropic 1.0 migration deferred out of v8.0
- [x] **COMPAT-02**: MCP server uses the `mcp` v2 import path (`MCPServer`); the existing 3 tools import and run over stdio unchanged
- [x] **COMPAT-03**: the guard-sync test (`_DIAGNOSTICS_METHODS` ↔ `build_diagnostics._supported`) runs on all supported Python versions (no longer skipped on the 3.9 CI baseline)

### Deferred Advisor Aspects

- [x] **ASPECT-01**: the PACE-FPCA aspect emits grounded scalars (noise/signal `sigma2` ratio, truncated-rank flag, mean prediction-band width) computed from fdars `pace_fpca` results
- [x] **ASPECT-02**: the elastic-multinomial aspect emits grounded classification scalars (e.g. overfitting gap, class-count flag) computed from fdars results
- [x] **ASPECT-03**: the ITP interval-inference aspect reduces the vector-valued p-curve to grounded **detection AND localisation** scalars (min adjusted p-value; count + proportion of significant intervals; first significant basis; detected-at-0.05) — never a single misleading scalar
- [x] **ASPECT-04**: `_ASPECT_PRIMERS` extended for the three aspects; grounding invariant + guard-sync preserved in atomic commits; diagnostics offline-deterministic with native float/int (no numpy scalars)
- [x] **ASPECT-05**: `advise()` returns grounded interpretation for each new aspect, verified across providers (offline grounding matrix + env-gated live)

### Comparative Method-Selection

- [x] **COMPARE-01**: `compare_methods()` runs `build_diagnostics` over N candidate methods and returns a deterministic, **fdars-computed** ranking (the LLM does not choose the winner)
- [x] **COMPARE-02**: a "comparison" advise task family narrates the ranking, citing each candidate's grounded diagnostics with correct per-candidate provenance (labeled candidates, never flat-merged dicts)
- [x] **COMPARE-03**: comparison guards against incommensurable comparisons — only comparable candidates are ranked, on a shared metric
- [x] **COMPARE-04**: an `fdars_compare_methods` MCP tool exposes the comparison and stays provably LLM-free (re-runs via existing runnable methods)

### Pipeline Diagnostic Report

- [x] **PIPE-01**: `build_pipeline_report()` aggregates diagnostics across end-to-end stages (represent → smooth → cluster/regress → monitor) with per-stage provenance (stage-prefixed keys / per-stage objects, never flat-merged)
- [x] **PIPE-02**: `pipeline_report()` produces a grounded multi-aspect narrative report over the aggregated stages
- [x] **PIPE-03**: cross-stage signal detection surfaces downstream caveats (e.g. high imputed fraction → FPCA caveat)
- [x] **PIPE-04**: an `fdars_build_pipeline_report` MCP tool exposes the report and stays LLM-free

### Closed-Loop Auto-Tuning (capstone)

- [x] **TUNE-01**: a shared `_tuning.py` loop core (propose → apply → re-run fdars → compare → check target-vs-budget → iterate) with an injectable proposal/advisor function, fully offline-testable without an API key
- [x] **TUNE-02**: bounded termination — required `max_steps`, plus convergence and oscillation detection; the loop never runs unbounded
- [ ] **TUNE-03**: `auto_tune()` Python API uses the LLM for proposals via a structured, schema-validated numeric `parameter_delta` — never parsed from prose; the LLM never sets a number directly in the numeric path
- [ ] **TUNE-04**: an `fdars_auto_tune` MCP tool uses a **heuristic (LLM-free)** proposal, preserving the provably-LLM-free MCP boundary
- [x] **TUNE-05**: optional guard diagnostics detect off-target degradation (Goodhart) during tuning
- [x] **TUNE-06**: `TuningTrace` / `TuneProposal` / `TuneResult` schemas + an optional `Recommendation.parameter_delta` field, backward-compatible with the 3 existing task families

### Evaluation

- [ ] **EVAL-01**: deterministic eval fixtures where the correct comparative ranking or auto-tune convergence direction is known from the data; assert diagnostic improvement + grounding-pass
- [ ] **EVAL-02**: no LLM-as-judge in CI; live LLM eval is env-gated (skips without a key; CI stays network-free)

### Docs & Gate

- [ ] **DOCS-01**: new/updated docs pages for the four capabilities with method-accurate hand-authored inline SVG diagrams (v7.0 STYLE_SPEC standard)
- [ ] **DOCS-02**: runnable offline `FDARS_FENCE_OK` worked examples (small/synthetic data; the auto-tune example uses the offline/injectable path — no network in the docs build)
- [ ] **DOCS-03**: whole-site `mkdocs build --strict` green offline; blocking human diagram method-accuracy review before close

## Future Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Transport

- **HTTP-01 / FUT-01**: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0)

### SDK

- **ANTHROPIC-1X**: full `anthropic` 1.x migration (drops Python 3.9; `output_config`, httpx2) — its own milestone once Python 3.9 is dropped

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Any agent-framework dependency (LangChain/LangGraph/etc.) | Would break the provider-agnostic + LLM-free-compute invariants; a plain loop on the Provider protocol suffices |
| An LLM anywhere in the MCP compute path | Violates the provably-LLM-free MCP boundary; the MCP auto-tune tool uses a heuristic proposal |
| LLM-chosen comparative winner or weighted single-score aggregation | Breaks the grounding invariant; fdars-computed sort determines the winner |
| LLM text directly setting fdars parameters | Grounding-invariant breach; proposals must flow through a schema-validated numeric `parameter_delta` |
| `fdars-core` bump / new Rust bindings | v8.0 is an advisor-capability milestone on the existing 0.23.0 surface |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| COMPAT-01 | Phase 50 | Complete |
| COMPAT-02 | Phase 50 | Complete |
| COMPAT-03 | Phase 50 | Complete |
| ASPECT-01 | Phase 50 | Complete |
| ASPECT-02 | Phase 50 | Complete |
| ASPECT-03 | Phase 50 | Complete |
| ASPECT-04 | Phase 50 | Complete |
| ASPECT-05 | Phase 50 | Complete |
| COMPARE-01 | Phase 51 | Complete |
| COMPARE-02 | Phase 51 | Complete |
| COMPARE-03 | Phase 51 | Complete |
| COMPARE-04 | Phase 51 | Complete |
| PIPE-01 | Phase 52 | Complete |
| PIPE-02 | Phase 52 | Complete |
| PIPE-03 | Phase 52 | Complete |
| PIPE-04 | Phase 52 | Complete |
| TUNE-01 | Phase 53 | Complete |
| TUNE-02 | Phase 53 | Complete |
| TUNE-03 | Phase 53 | Pending |
| TUNE-04 | Phase 53 | Pending |
| TUNE-05 | Phase 53 | Complete |
| TUNE-06 | Phase 53 | Complete |
| EVAL-01 | Phase 54 | Pending |
| EVAL-02 | Phase 54 | Pending |
| DOCS-01 | Phase 54 | Pending |
| DOCS-02 | Phase 54 | Pending |
| DOCS-03 | Phase 54 | Pending |

**Coverage:**

- v8.0 requirements: 27 total
- Mapped to phases: 27 ✓ (Phase 50: COMPAT-01..03 + ASPECT-01..05; Phase 51: COMPARE-01..04; Phase 52: PIPE-01..04; Phase 53: TUNE-01..06; Phase 54: EVAL-01..02 + DOCS-01..03)
- Unmapped: 0

---
*Requirements defined: 2026-08-23*
*Last updated: 2026-08-23 after roadmap creation (traceability populated; 27/27 mapped across Phases 50–54)*
