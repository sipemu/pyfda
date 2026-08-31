# Phase 50: Deferred Advisor Aspects (+ compat pre-flight) - Context

**Gathered:** 2026-08-23
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — all three grey areas accepted as recommended

<domain>
## Phase Boundary

The three deferred advisor aspects — PACE-FPCA, elastic-multinomial, and ITP interval-inference — emit grounded, fdars-computed scalars with extended `_ASPECT_PRIMERS`, so every later LLM call this milestone targets richer, accurate diagnostics. Blocking compatibility fixes on the *existing* advisor/MCP surface land first as an isolated pre-flight so the advisor keeps importing on Python 3.9 and the guard-sync assertion runs on every Python version. Requirements: COMPAT-01..03, ASPECT-01..05.

Out of boundary: comparative selection, pipeline report, auto-tuning (later phases); any new `build_diagnostics` method slot (guard-sync is a no-op here); `fdars-core` bump / new Rust bindings.

</domain>

<decisions>
## Implementation Decisions

### Deferred-aspect scalar sets
- **PACE-FPCA** aspect emits three grounded scalars from the fdars `pace_fpca` result: `sigma2` noise/signal ratio, a truncated-rank flag, and mean prediction-band width — all native `float`/`int` (no numpy scalars).
- **elastic-multinomial** aspect emits grounded classification scalars: overfitting gap (train vs holdout/CV accuracy) + class-count flag.
- **ITP** interval-inference reduces the vector-valued adjusted-p-curve to **both** detection **and** localisation scalars together: min adjusted p-value + detected-at-α (detection); count + proportion of significant intervals + first significant basis (localisation). Never a single global scalar.
- ITP significance threshold **α = 0.05** (matches the existing inference pages); no configurable α this phase.

### Grounding & primer integration
- Scalars computed by **extending the existing per-aspect builders** (`aspects/fpca.py`, `aspects/classification.py`, `aspects/inference.py`) via detection-by-result-key branches; native float/int, offline-deterministic, no numpy scalars.
- Primers: **extend the existing** fpca/classification/inference `_ASPECT_PRIMERS` entries — **no new aspect keys** (guard-sync stays a no-op; `_DIAGNOSTICS_METHODS` unchanged).
- Grounding verified via the offline aspect×provider grounding matrix **plus** env-gated live, for the three aspects.
- The ITP primer explicitly teaches the whether-vs-where distinction (min-p = detection/whether; interval count + first-significant-basis = localisation/where) to prevent the LLM treating local significance as global.

### Compat pre-flight scope
- **COMPAT-01**: pin `anthropic>=0.72.0,<1.0` in the `[advisor]` extra (`pyproject.toml:42`); full anthropic 1.0 migration deferred to its own milestone (1.0 drops Python 3.9).
- **COMPAT-02**: MCP import is **verify-only** — `python/fdars/mcp/server.py:35` already uses `from mcp.server import MCPServer`; add a regression test asserting the server imports and its 3 tools load over stdio. No import change needed.
- **COMPAT-03**: split the guard-sync assertion (`_DIAGNOSTICS_METHODS` ↔ `build_diagnostics._supported`) out of the Py<3.10-skipped `tests/test_mcp_server.py` into a **version-independent** test (pure dict-key comparison; must not import `mcp`, so it runs on Python 3.9).
- Land the compat fixes as an **isolated first plan/commit** (pre-flight), then the aspect work.

### Claude's Discretion
- Exact scalar field names, primer wording, and test-fixture datasets (small/synthetic or subsampled) at Claude's discretion, consistent with the v4.0 Phase 28 / v6.0 Phase 40 aspect-extension precedent and the grounding invariant.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/advisor/aspects/` — one builder per aspect; `fpca.py`, `classification.py`, `inference.py` already have detection branches (`has_pace_fpca`, `has_elastic_multinomial`) to extend.
- `python/fdars/advisor/_prompts.py` — `_ASPECT_PRIMERS` (14 aspects) to extend for the three.
- `python/fdars/advisor/_schema.py` — `Advice` schema + `_check_grounding` guard (flat numeric scan).
- `src/inference_mod.rs` — `itp_result_to_pydict` returns `adjusted_pvalues`/`raw_pvalues` as numpy **arrays** (per basis function) — the source of the ITP vector→scalar reduction.

### Established Patterns
- Aspect-extension + atomic guard-sync precedent: v4.0 Phase 28, v5.0 Phase 34, v6.0 Phase 40.
- Grounding invariant: every emitted scalar is fdars-computed native `float`/`int`; the LLM only interprets/cites.
- Provider-agnostic; offline-deterministic core; env-gated LLM tests; no network in CI.

### Integration Points
- `pyproject.toml:42` — `[advisor]` extra (anthropic pin).
- `python/fdars/mcp/server.py:35,41` — `MCPServer` import + instance (verify-only).
- `tests/test_mcp_server.py:45` (module skip on Py<3.10), `:503` (`test_diagnostics_methods_match_advisor_supported`) — guard-sync test to split out version-independently.

</code_context>

<specifics>
## Specific Ideas

- ITP scalar reduction must emit detection AND localisation together — a lone `min_p` misleads the LLM into treating local significance as global (research PITFALLS #1).
- The version-independent guard-sync test must NOT import `mcp` (so it runs on Python 3.9) — a pure comparison of `_DIAGNOSTICS_METHODS` against `build_diagnostics._supported`.

</specifics>

<deferred>
## Deferred Ideas

- PACE reconstruction-error scalar from `fitted` trajectories — considered, not selected for this phase (may revisit if the three chosen scalars prove insufficient).
- Configurable / multi-α ITP flags (e.g. also @0.01) — deferred; α=0.05 only this phase.
- Full `anthropic` 1.x migration — its own milestone (drops Python 3.9).

</deferred>
