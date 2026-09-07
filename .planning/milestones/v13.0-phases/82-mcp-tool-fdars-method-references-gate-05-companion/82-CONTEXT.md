# Phase 82: MCP Tool `fdars_method_references` + GATE-05 Companion - Context

**Gathered:** 2026-09-07
**Status:** Ready for planning
**Mode:** Auto-generated (well-specified code phase — LLM-free design fully locked in ROADMAP decision log; success criteria concrete/technical; no grey areas warrant a user decision)

<domain>
## Phase Boundary

Ship the LLM-free `fdars_method_references()` MCP tool in `python/fdars/mcp/server.py`, alongside the existing `fdars_list_capabilities`, plus its GATE-05 companion guard tests — closing the provable LLM-free boundary. Delivers MCP-01..04:

1. `fdars_method_references(method)` — a synchronous `@mcp.tool()` handler added immediately after `fdars_list_capabilities`. Loads the committed `python/fdars/_references_map.json` via `importlib.resources`. Accepts `"module.callable"` (preferred) or a bare `"callable"` (suffix-resolved; if ambiguous, ALL matches returned). Makes NO model/provider call and NO synthesis — pure static lookup.
2. Return contract:
   - Hit: `{"method", "curated": true, "papers": [...with cross-language implementations...], "coverage": "N/437", "version"}`.
   - Miss: `{"method", "curated": false, "sentinel": "NO_CURATED_ENTRY", "message", "version"}` — an explicit first-class uncurated signal, NEVER an empty dict and NEVER an error.
3. `_REFERENCES_MODULES` is DERIVED from / asserted equal to `_CAPABILITY_MODULES` (not independently re-declared), and gates input (frozenset check) BEFORE any JSON load.
4. GATE-05 companion tests (Python 3.10+, importing `mcp`) land in `tests/test_guard_sync_version_independent.py` as Guard Group 3, in the SAME commit as the tool (GATE-04 lesson):
   - (C) LLM-free boundary: a known callable's result has no `provider`/`model` keys and has `curated`; a known-absent callable returns `curated:false` with no `doi`; the handler imports no advisor/provider module.
   - (D) frozenset literal mirror: `_REFERENCES_MODULES == _EXPECTED_REFERENCES_MODULES == _CAPABILITY_MODULES`.

Out of scope: docs/llms.txt/skill (Phase 83), the whole-site strict gate + human citation review (Phase 84).

</domain>

<decisions>
## Implementation Decisions

### Locked by ROADMAP / STATE decision log
- The tool stays PROVABLY LLM-free (GATE-04 → GATE-05): static `importlib.resources` load, `_REFERENCES_MODULES` DERIVED from `_CAPABILITY_MODULES`, no `provider`/`model` keys anywhere in the response, explicit `{"curated": false, "sentinel": "NO_CURATED_ENTRY"}` for the tail. The hybrid curated/ungrounded fallback lives ONLY in the skill (Phase 83), never here.
- Guard tests land in the SAME commit as the tool handler (GATE-04 lesson).
- Guard Group 3 companion tests are Py3.10+ (they import `mcp`), matching the existing companion-test split (primary Py3.9+/no-mcp from Phase 80; companion Py3.10+/imports-mcp here).
- `_Fdata` is special-cased consistently with `fdars_list_capabilities` / the Phase-80 cross-file resolution.

### Correction carried from Phase 81 (honest denominator)
- The `coverage` string MUST use the DERIVED real denominator (**N/437**, computed from the live `_capability_map.json`), NOT the stale roadmap-estimate "409" that appears verbatim in the MCP-02 requirement text. Phase 81 already established 437 as the true callable count and the CURATE-05 coverage test emits `COVERAGE: N/437`. Keep the tool consistent with the committed data — do not hardcode; derive or read the same way the guard test does. Note the 409→437 correction in the SUMMARY so Phase 84 reconciles the requirement text.

### Claude's Discretion
- Exact `papers[...]` projection shape returned on a hit (which fields to surface — title/authors/year/doi/url/type/cross_language) and the exact `message` wording on a miss, guided by the `_references_map.json` schema and the `fdars_list_capabilities` return style.
- Suffix-resolution algorithm for a bare `"callable"` (how to enumerate candidate `module.callable` keys and return all matches when ambiguous).
- Whether `coverage` is computed at call time from `_capability_map.json` + `_references_map.json` or read from a coverage field, provided it is honest and matches the guard-emitted fraction.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/mcp/server.py` — mirror `fdars_list_capabilities` (defined ~line 762): the `@mcp.tool()` decorator, the `importlib.resources` load pattern (`resources.files("fdars") / "_capability_map.json"`, ~line 813), the `_CAPABILITY_MODULES` frozenset (~line 751) with its maintenance comment, and the input-validation-before-load discipline. Add the new tool immediately after it.
- `python/fdars/_references_map.json` — the curated data the tool reads (57 papers, 243 callable_index entries, honest N/437 coverage from Phase 81).
- `python/fdars/_capability_map.json` — the module list source for `_REFERENCES_MODULES` derivation and the 437 denominator.
- `tests/test_guard_sync_version_independent.py` — Guard Group 3 home; primary A/B (Py3.9+) from Phase 80, coverage + anti-feature-absence from Phase 81; add the companion C/D (Py3.10+, import mcp) here. There is an `_EXPECTED_CAPABILITY_MODULES` literal + a version-split (`sys.version_info`) pattern to mirror for `_EXPECTED_REFERENCES_MODULES`.

### Established Patterns
- LLM-free tools load committed JSON statically via `importlib.resources`; validate input against a frozenset before any load; raise a descriptive error on unknown module (for `list_capabilities`) — but this tool returns the `curated:false` sentinel on a miss rather than erroring (per MCP-02).
- Guard-sync tests assert a hand-maintained frozenset literal equals the derived one so a future crate-bump adding a submodule can't silently desync.

### Integration Points
- `_REFERENCES_MODULES` DERIVED from `_CAPABILITY_MODULES` (single source of truth) → the (D) frozenset mirror guard proves they stay equal.
- The tool is consumed by the Phase-83 skill (which adds the ungrounded hybrid fallback on top) and surfaced in docs/llms.txt.

</code_context>

<specifics>
## Specific Ideas

- Miss response is a first-class signal: `{"method", "curated": false, "sentinel": "NO_CURATED_ENTRY", "message", "version"}` — never `{}`, never raise.
- The LLM-free boundary is milestone-gating: the (C) guard must assert no `provider`/`model` keys in a hit response and that the handler imports no advisor/provider module.
- Coverage denominator is 437 (derived), not the stale 409 in the requirement text.

</specifics>

<deferred>
## Deferred Ideas

- The skill's hybrid curated/ungrounded fallback (flagged ungrounded) → Phase 83.
- References docs page + llms.txt provenance section → Phase 83.
- Whole-site strict build + guard-sync close + human citation review → Phase 84.
- HTTP/SSE MCP transport → future (stdio only).

</deferred>
