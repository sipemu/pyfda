# Project Research Summary

**Project:** pyfda — Advisor: New Capabilities (v8.0)
**Domain:** Grounded AI advisor over a functional-data-analysis library (FDA + LLM interpretation)
**Researched:** 2026-08-23
**Confidence:** HIGH

## Executive Summary

The v8.0 milestone adds four capabilities to the existing, shipped grounded FDA advisor: (1) filling deferred diagnostic aspects (PACE-FPCA, elastic-multinomial, ITP interval-inference), (2) comparative method-selection with deterministic ranking, (3) pipeline diagnostic aggregation across FDA stages, and (4) closed-loop auto-tuning with LLM-proposed parameter changes. All four build entirely on the existing stack — **zero new runtime dependencies**. Everything sits above or extends the existing `build_diagnostics` / `advise` / Provider-protocol surface plus the MCP tool layer.

The build strategy is **foundation-first**: deferred aspects first (they unblock richer, more accurate diagnostics for every later LLM call), then comparative selection and pipeline aggregation (no loop logic — straightforward extensions of the `build_diagnostics` + `advise` pattern), then closed-loop auto-tuning as the capstone (the only structurally novel component: a `_tuning.py` loop core, new schema types, and a new MCP tool). The two hard invariants hold throughout: the **grounding invariant** (fdars computes every number; the LLM only interprets/cites and proposes parameters) and the **MCP-LLM-free compute boundary**.

The primary execution risk is subtle boundary violations rather than missing functionality: LLM text re-entering the numeric path, provenance collapse in aggregated/comparative diagnostic dicts, a misleading scalar reduction of the vector-valued ITP result, and non-terminating/oscillating auto-tune loops. Each has a known, codebase-grounded mitigation (structured `parameter_delta` field, per-stage/namespaced keys, detection+localisation ITP scalars, `max_steps` + convergence/oscillation checks, injectable advisor for offline testability). Two blocking compatibility fixes on the *existing* surface must land before new work: pin `anthropic>=0.72.0,<1.0` (1.0 drops Python 3.9) and fix the `mcp` v2 import path; also make the guard-sync test Python-3.9-independent.

## Key Findings

### Recommended Stack

No new runtime dependency is justified. All four capabilities are built on the existing Provider protocol (`advisor/providers/`) + Pydantic 2 schemas + plain Python orchestration. An agent framework would break the provider-agnostic + LLM-free-compute invariants and is an explicit anti-add. See `STACK.md`.

**Core technologies (all already present):**
- **Provider protocol + 4 adapters** (Anthropic / OpenAI / Gemini / Ollama): the LLM proposal/narration path — reused as-is.
- **Pydantic 2 `BaseModel`**: structured LLM outputs; add `Optional` fields/schemas (`parameter_delta` on `Recommendation`; `TuneProposal`/`TuneResult`/`TuningTrace`) — backward-compatible only if optional.
- **`mcp` SDK (stdio)**: new agentic tools follow the existing sync-handler pattern; boundary stays LLM-free.
- **pytest (offline + env-gated)**: the entire eval strategy — no eval framework, no LLM-judge in CI.

**Blocking compat fixes on the existing surface (do first):**
- Pin `anthropic>=0.72.0,<1.0` — anthropic 1.0.0 (2026-08-20) drops Python 3.9, renames `output_format`→`output_config`, moves to httpx2. fdars is abi3-py39. Full 1.0 migration deferred out of v8.0.
- `mcp` v2.0.0 import rename (`mcp.server.fastmcp.FastMCP` → `mcp.server.mcpserver.MCPServer`); decorator API unchanged.
- Make `test_diagnostics_methods_match_advisor_supported` Python-3.9-independent (currently skipped on the CI baseline, so guard-sync drift can slip through).

### Expected Features

See `FEATURES.md`. Grounding invariant respected in all four: every new scalar is computed from arrays fdars already returns; the LLM never infers a numeric value.

**Must have (table stakes):**
- Deferred aspects — grounded scalars for PACE-FPCA (`sigma2_ratio`, `ncomp_truncated`, `mean_band_width`), elastic-multinomial (`overfitting_gap`, `n_classes_flag`), and ITP (see Critical Pitfalls — detection + localisation scalars together).
- Comparative selection — fdars-computed sort determines the winner; the LLM narrates only.
- Pipeline report — N `build_diagnostics` calls + one `advise` over stage-prefixed (flat, not nested) diagnostics.
- Auto-tuning — `max_steps` required; structured `parameter_delta` (not parsed from prose); shared loop core.

**Should have (differentiators):**
- Cross-stage signal detection in the pipeline report (e.g. high `imputed_fraction` → caveat for downstream FPCA).
- Optional guard diagnostics in auto-tuning (watch non-target metrics to catch Goodhart degradation).

**Anti-features (explicitly out):**
- An MCP tool that calls `advise()` internally (breaks LLM-free boundary).
- LLM-chosen comparative winner or weighted single-score aggregation.
- LLM text directly setting fdars parameters.

### Architecture Approach

See `ARCHITECTURE.md`. The deferred aspects are nearly done at the diagnostics layer — `fpca.py`/`classification.py` already have detection branches; the genuine gaps are a few PACE-FPCA fields, a new ITP vector→scalar reduction branch in `inference.py`, and two `_ASPECT_PRIMERS` entries. **Guard-sync is a no-op for all four capabilities** — none add a new `build_diagnostics` method slot, so `_DIAGNOSTICS_METHODS` does not change (atomic commits still apply per capability). Comparative + pipeline are new orchestration/aggregation layers over existing primitives. Auto-tuning is the only novel core.

**Major components:**
1. **Extended aspect builders** (`fpca.py`, `classification.py`, `inference.py`, `_prompts.py`) — deferred-aspect scalars + primers.
2. **`compare_methods()` + "comparison" task family + `fdars_compare_methods` MCP tool** — deterministic ranking, labeled candidates.
3. **`build_pipeline_report()` / `pipeline_report()` + "pipeline" task family + MCP tool** — per-stage isolation, stage-prefixed keys.
4. **`_tuning.py` loop core (shared) + `auto_tune()` Python API + `fdars_auto_tune` MCP tool** — Python API uses LLM proposal; MCP tool uses heuristic proposal (LLM-free); one core via injectable `proposal_fn`/`advisor_fn`.

### Critical Pitfalls

Top items from `PITFALLS.md` (13 total, all codebase-derived):

1. **ITP misleading scalar reduction** — `adjusted_pvalues` is a numpy array (per basis function). Emit detection AND localisation: `min_adjusted_pvalue`, `n_significant_intervals`, `proportion_significant`, `first_significant_basis`, `detected_at_0.05`. A lone `min_p` makes the LLM treat local significance as global. (Phase 50)
2. **MCP LLM-free boundary violation** — no new MCP tool may call `advise()`. The LLM client orchestrates existing tools; the `fdars_auto_tune` tool uses a heuristic proposal. (Phase 53)
3. **Provenance collapse in aggregated dicts** — `_check_grounding` does a flat numeric scan and can't tell which stage a value came from. Never `{**diag_a, **diag_b}`; use per-stage `Advice` calls or namespaced keys. (Phases 51 & 52)
4. **Guard-sync drift + Python-3.9-skipped test** — make the guard-sync test version-independent; keep `_ASPECT_PRIMERS`/`build_diagnostics`/`_DIAGNOSTICS_METHODS` changes atomic. (Phase 50)
5. **Auto-tune non-termination / oscillation / Goodhart** — `max_steps` required and enforced at the orchestrator; history + convergence check; optional guard diagnostics; injectable advisor so the whole loop is offline-testable without an API key. (Phase 53)

## Implications for Roadmap

Based on research, suggested phase structure (foundation-first; phase numbering continues from v7.0 → starts at **Phase 50**):

### Phase 50: Deferred Advisor Aspects (Foundational)
**Rationale:** Lowest risk; extends existing builders; unblocks richer/accurate diagnostics for every later LLM call. Must not be merged into a later phase. Folds in the blocking compat fixes (anthropic pin, mcp import, version-independent guard-sync test) as a pre-flight.
**Delivers:** PACE-FPCA scalars, ITP vector→scalar reduction (detection + localisation), elastic-multinomial review + `overfitting_gap`, extended `_ASPECT_PRIMERS`.
**Addresses:** deferred-aspect table stakes.
**Avoids:** ITP misleading reduction (count+fraction+min together), guard-sync drift (atomic commit + version-independent test), primer over-claiming.

### Phase 51: Comparative Method-Selection
**Rationale:** Builds on Phase 50's stable diagnostics; independent of pipeline/auto-tuning; no loop logic.
**Delivers:** `compare_methods()` API, deterministic ranking, "comparison" task family, `fdars_compare_methods` MCP tool.
**Uses:** existing `build_diagnostics` + `advise` + Provider protocol.
**Avoids:** incommensurable comparison (method-match enforcement), wrong-run citation (labeled-candidate structure).

### Phase 52: Pipeline Diagnostic Report
**Rationale:** Extends the Phase 51 pattern to the multi-stage case; proves per-stage isolation — a prerequisite for the capstone.
**Delivers:** `build_pipeline_report()` aggregator, `pipeline_report()` API, "pipeline" task family, MCP tool.
**Avoids:** provenance collapse (per-stage `Advice` OR namespaced keys, never flat merge).

### Phase 53: Closed-Loop Auto-Tuning (Capstone)
**Rationale:** Most complex; depends on Phases 50–52 for stable surfaces; introduces orchestration/convergence/guard logic.
**Delivers:** `_tuning.py` loop core (shared by Python API + MCP), `auto_tune()` API (LLM proposal), `fdars_auto_tune` MCP tool (heuristic, LLM-free), `TuningTrace`/`TuneProposal`/`TuneResult` schemas + `Recommendation.parameter_delta`, "parameter_proposal" task family.
**Avoids:** non-termination (`max_steps`), numeric fabrication (structured `parameter_delta` + dedicated loop system prompt), Goodhart (guard diagnostics), oscillation (history+convergence), non-determinism (injectable advisor), MCP boundary (heuristic-only MCP tool).

### Phase 54: Eval Strategy + Docs Gate
**Rationale:** Eval signals should be defined alongside the capstone, not after; docs + human review close the milestone (v7.0 standard).
**Delivers:** deterministic diagnostic-improvement + grounding-pass eval fixtures (env-gated LLM tests only); new docs pages + method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples; whole-site `mkdocs build --strict` green; blocking human diagram review.

### Phase Ordering Rationale
- Deferred aspects are foundational — later capabilities target and narrate the diagnostics they add.
- Comparative → pipeline → auto-tuning is a strict complexity/dependency gradient; each reuses the prior surface. Per-stage isolation proven in pipeline is a prerequisite for the loop.
- Ordering keeps the two invariants defendable at every step (guard-sync no-op; heuristic MCP tool last).
- Exact phase count/split (e.g. whether eval is its own phase or folds into 53/54) is the roadmapper's call.

### Research Flags
Phases likely needing deeper research during planning:
- **Phase 53 (Auto-tuning):** complex interaction of termination/oscillation/guard conditions; the loop orchestrator is the hardest piece. Recommend `gsd-plan-phase --research-phase` to stress-test convergence guarantees, param-range spec, and the static-allowlist-vs-kwargs MCP param schema decision.

Phases with standard patterns (skip research-phase):
- **Phase 50:** follows the proven v6.0 Phase 40 aspect-extension pattern.
- **Phase 51:** standard champion/candidate leaderboard pattern.
- **Phase 52:** standard ETL-style aggregation pattern.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | MCP v2.0 import + anthropic 1.0 Python-3.9 removal web-verified; zero-new-deps validated against existing surface |
| Features | HIGH | Derived from direct codebase read + v6.0 Phase 40 deferral notes; result shapes read from Rust bindings/tests |
| Architecture | HIGH | Direct source read of all advisor/MCP modules; guard-sync rules from v4/v5/v6 precedents |
| Pitfalls | HIGH | All 13 from codebase patterns + MEMORY history + direct code inspection (not generic ML advice) |

**Overall confidence:** HIGH

### Gaps to Address
- **Auto-tune convergence decision tree** — exact interaction of termination conditions unspecified; handle in Phase 53 planning/research.
- **Auto-tune param spec** — heuristic proposal grid width/steps per method; static allowlist vs `**kwargs` for the MCP tool; whether the 6 `_RUNNABLE_METHODS` suffice or regression/inference must become runnable; `max_steps` cost ceiling (≈20 suggested — confirm with user).
- **ITP edge cases** — small-sample (n_basis=2) behavior; handle in Phase 50 via primer note + unit test.
- **PACE quality scalar** — best scalar beyond `sigma2`/`ncomp` (reconstruction-quality from `fitted`?) — decide in Phase 50 plan.
- **Comparative common denominator** — whether a shared `fdars.scoring` metric always exists for a fair method-pair comparison.
- **Entry-point layout** — standalone functions in `advisor/__init__.py` vs a new `advisor/tasks/` sub-layer at 6+ task families.

## Sources

### Primary (HIGH confidence)
- Direct source read: `python/fdars/advisor/` (`__init__.py`, `_prompts.py`, `_schema.py`, aspect builders, `providers/`), `python/fdars/mcp/` (`server.py`, `_runner.py`, `_compare.py`), `src/inference_mod.rs` (`itp_result_to_pydict`).
- `.planning/PROJECT.md`, v4.0/v5.0/v6.0 guard-sync precedents (Phases 28/34/40), MEMORY history.
- Detailed research docs: `STACK.md`, `FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md`.

### Secondary (MEDIUM confidence)
- PyPI + official SDK changelogs/migration guides: anthropic 1.0.0 (Python 3.9 removal, `output_format`→`output_config`), `mcp` 2.0.0 (import rename, decorator continuity).
- AutoML/hyperparameter-tuning stopping-criteria literature (applied selectively; loop-divergence patterns).

---
*Research completed: 2026-08-23*
*Ready for roadmap: yes*
