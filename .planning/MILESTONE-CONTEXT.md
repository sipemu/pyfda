# Milestone Context — captured for the next `/gsd-new-milestone`

**Captured:** 2026-08-23 (questioning done; requirements + roadmap deferred to a fresh context window)
**Proposed version:** v8.0 · **Phase numbering continues from 49 → starts at Phase 50**
**Proposed name:** Advisor — New Capabilities

## Milestone goal

Extend the fdars **AI advisor** beyond its current *single-shot, recommend-only, per-result interpretation* surface with four new capabilities (user selected ALL FOUR). The **grounding invariant is the hard constraint throughout**: fdars computes every number; the LLM only interprets/cites — no fabricated values. Provider-agnostic + MCP-LLM-free boundaries must be preserved.

## Current advisor surface (build on this — do NOT re-build)

- `build_diagnostics(result, method=…)` — offline, deterministic, **14 aspects** (`python/fdars/advisor/__init__.py`, `_prompts.py _ASPECT_PRIMERS`).
- `advise(diagnostics, task=…)` — grounded LLM, **3 task families**: interpretation / parameter-guidance / method-guidance; `describe_cluster_differences` specialization; schema `_schema.py` (`Advice`).
- Provider-agnostic: Anthropic / OpenAI(-compatible) / Gemini / Ollama (`advisor/providers/`).
- **MCP** surface (`python/fdars/mcp/`): 3 tools (`fdars_build_diagnostics`, `fdars_run_method` over 6 runnable methods, `fdars_compare_run`), **provably LLM-free**, stdio only (HTTP/SSE deferred).
- **Agent Skill** (`.claude/skills/fdars-advisor/`).

## The four target capabilities (all in scope)

1. **Closed-loop auto-tuning** — turn today's *manual* recommend → re-run → compare (MCP `fdars_compare_run`) into an **autonomous, bounded loop**: "optimize this diagnostic" — advisor proposes a parameter/method change, applies it, re-runs, compares, and iterates until a target diagnostic improves or a step budget is hit. Grounding + LLM-free-compute-path invariants must hold; fdars runs every computation, the loop just orchestrates. Likely the capstone / highest-novelty.

2. **Fill deferred advisor aspects** — dedicated grounded coverage for **PACE-FPCA**, **elastic-multinomial** (both DEFERRED at v6.0 init as `PACE-ADV`/`MULTINOM-ADV`), and **ITP interval-inference** (deferred at v6.0 as vector-valued). Extends the existing `_ASPECT_PRIMERS` / diagnostics pattern; needs a grounded-scalar reduction for the vector-valued ITP p-curves. Foundational — do early.

3. **Comparative method-selection** — a recommender that **ranks/picks among candidate methods** from comparative diagnostics (e.g. "scalar-on-function: FPC-LM vs PLS vs kernel — which & why"; "which clustering method fits best"), not just per-result advice on one method. Likely a new task family or a new entry point over multiple `build_diagnostics` runs.

4. **Pipeline diagnostic report** — generate a **multi-aspect narrative report/dashboard** for an end-to-end analysis (represent → smooth → cluster/regress → monitor …), aggregating diagnostics across stages, instead of single-result interpretation.

## Suggested roadmap shape (roadmapper's call)

Foundation-first: deferred aspects (#2) → comparative selection (#3) → pipeline report (#4) → closed-loop auto-tuning (#1, capstone) → docs + eval. Each capability carries: (a) grounded diagnostics/offline core, (b) grounded `advise`/report surface, (c) MCP + Agent-Skill surface updates where relevant (guard-sync atomic, LLM-free preserved), (d) tests + docs (new pages + method-accurate hand-authored SVG per the v7.0 standard, offline `FDARS_FENCE_OK` examples, `mkdocs build --strict` green).

## Constraints carried forward

- **Grounding invariant** (fdars computes numbers, LLM cites) — non-negotiable; MCP boundary stays LLM-free.
- Provider-agnostic; offline core; env-gated LLM tests (no network in CI).
- Package currently `0.7.0`; a code milestone would bump it (semver `vX.Y.Z` tag triggers PyPI publish) — decide the bump at close.
- Docs standard from v7.0: hand-authored inline SVG, STYLE_SPEC-conformant, offline executable fences, per-section + blocking human diagram review.
- Open question for research/requirements: eval strategy for auto-tuning + comparative advice (how to measure "good advice"?), and the exact grounded-scalar reduction for ITP interval inference.

## Open decisions to resolve in requirements

- Version confirmation (v8.0) + whether all four ship in one milestone or the capstone auto-tuning splits to its own.
- Whether closed-loop auto-tuning lives Python-API-only or also gets an MCP agentic surface.
- Research toggle: this milestone has genuine unknowns (agentic-loop design, eval strategy) → research likely warranted (unlike v7.0's docs-only skip).
