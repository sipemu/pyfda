# Phase 34: Advisor Extension - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — grey area accepted by user

<domain>
## Phase Boundary

Extend the grounded advisor with a new `inference` diagnostics aspect that summarizes fdars-computed `TestResult` values (statistic / p_value / n_perm) from the Phase 31 `fdars.inference` functions, preserving the grounding invariant, offline determinism, and the advisor↔MCP guard-sync. Covers ADV-03. Depends on Phase 31 (the inference bindings the aspect consumes). Does NOT include docs (Phase 35, which documents the new aspect in `aspects.md`) and does NOT add functional-boxplot outlier diagnostics (deferred to docs / a future milestone per the accepted grey-area decision).

</domain>

<decisions>
## Implementation Decisions (accepted grey area)

### New `inference` aspect
- Add a NEW dedicated aspect module `python/fdars/advisor/aspects/inference.py` with a deterministic offline `build_diagnostics`-style builder (mirror the `scoring` aspect #13 pattern — the v4.0 precedent for a diagnostics-only aspect). Register `"inference"` in the advisor `_supported` set (`python/fdars/advisor/__init__.py` ~line 124) and dispatch, AND in the MCP `_DIAGNOSTICS_METHODS` frozenset (`python/fdars/mcp/server.py` ~line 63) — these two edits + the aspect wiring land in a SINGLE atomic commit so `test_diagnostics_methods_match_advisor_supported` stays green throughout.
- Diagnostics-only: do NOT add `"inference"` to `_RUNNABLE_METHODS` (like `scoring`; the inference tests need two groups / a fitted model, not a single-array re-run). The MCP LLM-free boundary is preserved.

### What the diagnostics summarize
- `build_diagnostics(test_result, method="inference")` accepts an fdars-computed `TestResult`-shaped input (the dict returned by the Phase 31 bindings: `{statistic, p_value, n_perm}`, or the SCB `ToleranceBand` dict where relevant) and produces a grounded diagnostics dict summarizing: `statistic`, `p_value`, `n_perm`, plus DERIVED significance flags at α = 0.01 / 0.05 / 0.10 (each simply `p_value < α` — trivially derived from the fdars-computed p_value, no fabrication). Optionally include a short grounded note field that cites the p_value/statistic (the LLM interpretation layer, not the builder, does any prose). Grounding invariant: the builder only summarizes numbers fdars computed; it never recomputes a statistic or invents a value.
- The caller passes the fdars-computed result in (same pattern as the `scoring` aspect, which takes caller-supplied metrics) — the builder does not call the inference functions itself.

### Determinism & guard-sync (hard constraints)
- Offline-deterministic: no numpy scalars in the output (convert to plain Python float/int/bool); byte-identical `json.dumps(..., sort_keys=True)` across two calls. Add an offline determinism test (like the other aspects').
- The `_supported` / `_DIAGNOSTICS_METHODS` guard-sync test (`tests/test_mcp_server.py::test_diagnostics_methods_match_advisor_supported`) MUST remain green — hence the single atomic commit for all guard edits.
- No network / no API key needed for `build_diagnostics` (the LLM `advise()` path stays env-gated, as for every other aspect).

### Claude's Discretion
- The exact `_ASPECT_PRIMERS` / prompt-primer entry text for the `inference` aspect (interpretation/parameter/method-guidance task families) is at Claude's discretion, following the existing per-aspect primers in `_prompts.py`.
- Exact input-shape handling (single TestResult dict vs a small collection of named test results) is at Claude's discretion — keep it consistent with how `scoring` accepts caller-supplied values; support at least a single test result robustly.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets (the analog to copy)
- `python/fdars/advisor/aspects/scoring.py` — the closest analog: a diagnostics-only aspect added in v4.0 Phase 28. Copy its structure (offline builder, plain-Python output, determinism).
- `python/fdars/advisor/__init__.py` (~line 124) — the `_supported` set + the `build_diagnostics` dispatch to per-aspect builders; add `"inference"`.
- `python/fdars/advisor/aspects/__init__.py` — aspect registry/exports.
- `python/fdars/advisor/_prompts.py` — `_ASPECT_PRIMERS` (per-aspect interpretation/parameter/method primers); add an `inference` entry.
- `python/fdars/mcp/server.py` (~lines 48–63) — `_RUNNABLE_METHODS` (leave unchanged), `_SUPPORTED_METHODS`, `_DIAGNOSTICS_METHODS` (add `"inference"`).
- `tests/test_mcp_server.py::test_diagnostics_methods_match_advisor_supported` — the drift-lock test that forces the single atomic commit.
- The Phase 31 `fdars.inference` functions produce the `TestResult`/`ToleranceBand` dicts this aspect summarizes.

### Established Patterns (v3.0/v4.0)
- One shared schema/prompt across all 12→13→(now 14) aspects; each aspect contributes a deterministic `build_diagnostics` + an `_ASPECT_PRIMERS` entry. Grounding invariant enforced by the Pydantic `Advice` schema + `_check_grounding` guard.
- Offline `build_diagnostics` tests (real values, determinism, ImportError-free) + env-gated `advise()` integration tests.

### Integration Points
- `python/fdars/advisor/` (aspect + registration + prompts), `python/fdars/mcp/server.py` (guard set). Build not required (pure Python) but run the full pytest suite; the advisor tests + guard-sync test must pass.

</code_context>

<specifics>
## Specific Ideas

- Model the `inference` diagnostics on a realistic example: e.g. a `t_perm_test` result on Growth (boys vs girls) → summarize `{statistic, p_value, n_perm, significant_at_0.05: true, ...}`. Use small/synthetic fixture values in tests (do not run 999-perm computations inside the advisor tests — pass in a canned fdars-computed TestResult dict).
- Keep the aspect count bookkeeping consistent: this becomes the 14th aspect (12 in v3.0 + `scoring` #13 in v4.0 + `inference` #14).

</specifics>

<deferred>
## Deferred Ideas

- Functional-boxplot outlier diagnostics (from Phase 32's `functional_boxplot`) → deferred (docs-only / future); NOT added to the advisor this phase, per the accepted grey-area decision.
- Making `inference` runnable in MCP (`_RUNNABLE_METHODS`) → out of scope (diagnostics-only).
- Docs update for the new aspect (`aspects.md`) → Phase 35 (DOCS-06).

</deferred>
