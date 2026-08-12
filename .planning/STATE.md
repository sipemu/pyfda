---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Provider-Agnostic Advisor, Full-Library Coverage
status: Awaiting next milestone
stopped_at: Completed 24-03-PLAN.md (final plan of Phase 24 / v3.0 milestone)
last_updated: "2026-08-12T14:33:33.980Z"
last_activity: 2026-08-12
last_activity_desc: v3.0 roadmap created (Phases 19–24), 28/28 requirements mapped
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 19
  completed_plans: 19
current_phase: 24
current_phase_name: Documentation
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-12)

**Core value:** The fdars AI advisor must work with any LLM backend — cloud or local — while the grounding invariant holds everywhere: fdars computes every number, the LLM only interprets and cites it. Every fdars analysis aspect gets advisor coverage on par with clustering.
**Current focus:** Phase 19 — Provider Foundation & Grounding Contract

## Current Position

Phase: Milestone v3.0 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-08-12 — Milestone v3.0 completed and archived

## Performance Metrics

**Velocity:**

- Total plans completed: 19 (v1.0–v2.1)
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 19 | 3 | - | - |
| 20 | 3 | - | - |
| 21 | 5 | - | - |
| 22 | 3 | - | - |
| 23 | 2 | - | - |
| 24 | 3 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 19 P01 | 46m | 3 tasks | 6 files |
| Phase 19-provider-foundation-grounding-contract P02 | 424 | 3 tasks | 9 files |
| Phase 19 P03 | 8 | 3 tasks | 1 files |
| Phase 20-additional-provider-adapters P01 | 35 | 3 tasks | 6 files |
| Phase 20-additional-provider-adapters P02 | 3 | 2 tasks | 4 files |
| Phase 20 P03 | 6 | 3 tasks | 5 files |
| Phase 21-per-aspect-advisor-coverage P01 | 5m | 3 tasks | 4 files |
| Phase 21 P02 | 4 | 3 tasks | 4 files |
| Phase 21 P03 | 35 | 3 tasks | 5 files |
| Phase 21 P04 | 20m | 3 tasks | 4 files |
| Phase 21-per-aspect-advisor-coverage P05 | 3 | 3 tasks | 3 files |
| Phase 22-surface-integration P01 | 15 | 3 tasks | 3 files |
| Phase 22 P03 | 128 | 2 tasks | 2 files |
| Phase 22 P02 | 243 | 3 tasks | 2 files |
| Phase 23-packaging-ci P01 | 139 | 3 tasks | 2 files |
| Phase 23 P02 | 2 | 2 tasks | 1 files |
| Phase 24 P01 | 65 | 2 tasks | 1 files |
| Phase 24 P03 | 752 | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v3.0 roadmap]: Phase numbering CONTINUES from v2.1 (starts at Phase 19; v2.1 ended at Phase 18)
- [v3.0 roadmap]: Foundation FIRST — `Provider` protocol + Anthropic refactor + validate-and-retry + `_check_grounding` (Phase 19) is the single blocking prerequisite; must ship the base grounding/retry machinery before any adapter or aspect so aspects don't each inherit unchecked grounding vulnerabilities
- [v3.0 roadmap]: Adapters (Phase 20) and per-aspect diagnostics (Phase 21) are INDEPENDENT and parallel-eligible after Phase 19
- [v3.0 roadmap]: MCP boundary stays LLM-free (SURF-01); provider selection lives only in the Python `advise()` (SURF-02)
- [v3.0 roadmap]: Packaging/CI (Phase 23) and Docs (Phase 24) come after code ships; docs LAST so executed offline fences run against the real implementation
- [v3.0 roadmap]: Custom `Provider` protocol only — no LiteLLM / pydantic-ai / LangChain; aspect always caller-specified (never auto-detected from result keys)
- [v2.0]: One deterministic `build_diagnostics` core shared by all surfaces; grounding invariant enforced by Pydantic schema + system prompt (fdars computes numbers, LLM only interprets/cites)
- [v2.0]: MCP transport = stdio only; HTTP/SSE deferred
- [Phase ?]: Kept _require_anthropic/_require_pydantic in advisor/__init__.py (not moved to providers/) so the sys.modules monkeypatch chain for ImportError tests remains intact through Phase 19-02 split
- [Phase ?]: providers/__init__.py imports AnthropicProvider at module level (safe: anthropic SDK deferred to AnthropicProvider.__init__ — no SDK import at module load)
- [Phase ?]: _GROUNDING_INVARIANT single constant in _prompts.py; build_diagnostics dispatches to aspects/ lazily; _selfcheck kept in __init__.py per RESEARCH.md Open Q2
- [Phase ?]: Fake providers defined at module level in test_advisor_providers.py for isolation — not conftest.py
- [Phase ?]: FakeFallbackProvider accepts response list for deterministic retry-sequence testing
- [Phase ?]: resolve_provider precedence tested via local _patched_resolve closure to avoid lazy-import-chain monkeypatching
- [Phase ?]: OpenAI pin >=1.40,<2.0: floor resolves STACK/PITFALLS version disagreement; <2.0 keeps Python 3.9 compatibility
- [Phase ?]: OpenAI _openai_schema passes $defs/$ref as-is: OpenAI strict mode supports them since 2024-08
- [Phase ?]: gemini/ollama factory branches wrap ImportError as ValueError to keep Phase 19 test_unknown_provider_raises green until plans 02/03 land
- [Phase ?]: OllamaProvider.supports_native_structured_output=False routes through ValidateAndRetry._fallback_with_retry
- [Phase ?]: Factory shim removal: ollama branch raises actionable ImportError not ValueError once ollama.py exists
- [Phase ?]: Client cached on self._client in GeminiProvider.__init__; simpler sync approach
- [Phase ?]: gemini factory shim removed; ImportError from _require_gemini() surfaces directly naming pip install fdars[gemini]
- [Phase ?]: depth branch accepts raw ndarray (not dict) — all fdars depth functions return PyArray1<f64>
- [Phase ?]: _ASPECT_PRIMERS dict in _prompts.py; aspect='' preserves backward compat
- [Phase ?]: Array-coercion guard uses __array__ + .data checks to protect ndarray and Fdata inputs
- [Phase ?]: n_classes as explicit keyword param on build_diagnostics() (BLOCKER #5); forwarded only to classification branch
- [Phase ?]: RESEARCH corrections #2+#6 applied: CV key is error_rate not cv_error_rate; accuracy guarded
- [21-03]: _utils.py shared helper extracted — fpca refactor uses it, spm.py (plan 21-05) will import it too
- [21-03]: represent is a new method string (not basis/fpca extension) — operates on INPUT data, not method output
- [21-03]: represent input resolution: attribute-first (Fdata .data/.argvals), then dict fallback — no dict(raw) coercion
- [Phase ?]: regression/regression_cv aspects use guarded key access for variably-shaped result dicts; pure-NumPy skewness and elbow detection (no scipy)
- [Phase ?]: spe_kurtosis_excess renamed from excess_kurtosis per RESEARCH correction #8 for LLM clarity
- [Phase ?]: arl0_t2 excluded from SPM builder: stochastic Monte Carlo breaks offline determinism guarantee (FUT-02)
- [Phase ?]: fraiman_muniz_1d(data, data) self-depth for MCP: ref_data is a data matrix not argvals; hard-coded to avoid string injection
- [Phase ?]: _RUNNABLE_METHODS frozenset as single source of truth across runner+server; _SUPPORTED_METHODS kept as backward-compat alias
- [Phase ?]: Four surgical edits to SKILL.md only — no rewrite; all frontmatter keys and existing sections preserved
- [Phase ?]: Provider selection documented in SKILL.md body only; MCP tools remain compute-only (advise() not called from any MCP handler)
- [Phase ?]: SKILL.md install note corrected: provider extras ([openai]/[ollama]/[gemini]) publish with fdars 3.0, not current PyPI; git-URL install documented
- [Phase ?]: _DIAGNOSTICS_METHODS (12) guards fdars_build_diagnostics; _RUNNABLE_METHODS (6) guards run_method — clear split enforced at tool boundary
- [Phase ?]: Guard/advisor sync locked by test_diagnostics_methods_match_advisor_supported (parses advisor error message, asserts set equality)
- [Phase ?]: Version-gated CI extras via two if: steps (3.9 vs !=3.9); gemini+mcp excluded on 3.9 since both require Python 3.10+
- [Phase ?]: smoke-bare-venv CI job uses Python 3.12 (single version, mid-matrix); no extras installed to prove base-package self-sufficiency
- [Phase ?]: Evidence construction uses a generic helper that scans built diagnostics for the first numeric value to cite in grounding-safe evidence strings — robust across all 12 aspects
- [Phase ?]: Used GEMINI_API_KEY (not GOOGLE_API_KEY) in providers.md — method-accurate against _factory.py _KEY_ENV table
- [Phase ?]: index.md: listed all 12 aspects inline in build_diagnostics description for direct verify coverage
- [Phase ?]: mkdocs.yml: Provider Setup before Per-Aspect Coverage, both after Python API and before MCP Server

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 20 research flag]: Schema portability across providers (OpenAI nullable unions, Gemini `additionalProperties` rejection, Ollama `think+format` conflict) — confirm during Phase 20 planning
- [Phase 21 research flag]: SPM diagnostics are highest-complexity; validate `spe_moment_match_diagnostic` fdars signature during Phase 21 planning

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Accessibility | A11Y-01: Long-form `<title>`/`<desc>` + aria-labelledby for complex diagrams | v2 | Init |
| Examples | EX2-01: Editorial consolidation (sonar-tsrvf vs phoneme-shape; Andrews-wine series) | v2 | Init |
| Transport | HTTP-01: HTTP/SSE MCP transport for the fdars-advisor server (stdio shipped in v2.0) | v3.x (FUT-01) | v2.0 close |

## Session Continuity

Last session: 2026-08-12T14:15:24.853Z
Stopped at: Completed 24-03-PLAN.md (final plan of Phase 24 / v3.0 milestone)
Resume file: None

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
