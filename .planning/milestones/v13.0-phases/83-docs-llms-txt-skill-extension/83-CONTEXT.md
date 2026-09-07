# Phase 83: Docs, llms.txt & Skill Extension - Context

**Gathered:** 2026-09-07
**Status:** Ready for planning
**Mode:** Auto-generated (well-specified docs+skill phase — offline-emit + hybrid-protocol design locked in ROADMAP; success criteria concrete/technical; no grey areas warrant a user decision)

<domain>
## Phase Boundary

Make the Phase-81 provenance surface public and consumable. Delivers DOCS-01..03 + SKILL-01/02:

1. **DOCS-01** — `scripts/generate_capability_dataset.py` gains a `--references` flag that reads `python/fdars/_references_map.json` OFFLINE (NO `fdars` import) and emits `docs/references.md`: a family-grouped method→paper→implementation cross-index with a prominent Coverage section stating `N of 437 callables have curated entries` (honest derived denominator — see correction below).
2. **DOCS-02** — the `llms.txt` emit gains a `## Scientific Provenance & Cross-Language Implementations` section: per-entry `module.function — Authors (Year) doi:… ; R/Python/Matlab pointers`, an explicit coverage fraction, and the "uncurated methods are absent; a consumer MAY synthesize but MUST flag as ungrounded" note — emitted OFFLINE from the committed JSON.
3. **DOCS-03** — `docs/references.md` wired into `mkdocs.yml` nav under the existing AI/capability section (near `AI Capability Map: ai-capability-map.md`, ~line 169), and the page renders under `mkdocs build --strict` offline.
4. **SKILL-01** — `.claude/skills/fdars-capabilities/SKILL.md` gains a `## Scientific Provenance Protocol` section encoding the hybrid: prefer curated (`fdars_method_references` / references page / `llms.txt`); on `curated:true` return verbatim; on `curated:false`/sentinel the consumer MAY synthesize but MUST structurally flag it ungrounded (machine-readable `grounded: bool` per citation, not prose-only), never presenting synthesized provenance as curated. Does NOT duplicate the `fdars-advisor` boundary.
5. **SKILL-02** — the SKILL.md walkthrough demonstrates BOTH paths (a curated hit AND an uncurated, visibly-labelled ungrounded fallback), and skill tests exercise both branches.

Out of scope: the whole-site `mkdocs build --strict` (~25 min) close, guard-sync/DOI gate close, and the BLOCKING human citation review → Phase 84.

</domain>

<decisions>
## Implementation Decisions

### Locked by ROADMAP / STATE decision log
- Docs + `llms.txt` emit OFFLINE from the committed JSON — the `--references` path, like the existing `--llmstxt` path, reads `_references_map.json` directly and does NOT import `fdars` (so it works without a compiled install and under CI/build).
- The skill's hybrid curated/ungrounded fallback lives ONLY in the skill (the MCP tool stays LLM-free per Phase 82); the `grounded: bool` flag is machine-readable per citation, never presenting synthesized provenance as curated. Do NOT duplicate the `fdars-advisor` boundary.
- Coverage is partial-but-honest; uncurated methods are absent from curated output; the "synthesize but flag ungrounded" note is explicit.

### Correction carried from Phases 81/82 (honest denominator)
- The Coverage line in `docs/references.md` and the `llms.txt` provenance section MUST use the DERIVED real denominator (**N/437**, computed from the live `_capability_map.json` the same way the CURATE-05 guard and the MCP tool do), NOT the stale "409" that appears verbatim in the DOCS-01/DOCS-02 requirement text. Authoring-time value is 28/437. Do NOT hardcode. Note the 409→437 correction in the SUMMARY so Phase 84 reconciles requirement text.

### Full --strict deferral
- The WHOLE-SITE `mkdocs build --strict` (~25 min, executed fences) is the Phase-84 close gate (standing decision). This phase must ensure `docs/references.md` is nav-wired and renders cleanly (a targeted/offline strict check of the page + nav validity is sufficient here); the full-site strict pass runs once at Phase 84.

### Claude's Discretion
- The exact family-grouping and visual layout of `docs/references.md` (headings per family, the per-method paper + cross-language table/list shape), guided by the existing `ai-capability-map.md` style and the `_references_map.json` structure.
- The precise `llms.txt` provenance line format (within the DOCS-02 template) and the skill walkthrough's concrete example callables (pick one curated hit e.g. `depth.fraiman_muniz_1d`, and one uncurated/all-false or sentinel e.g. `clustering.align_cluster_fd` or `explain.shap_values`).
- How skill "tests" are expressed (matching the existing `fdars-capabilities` skill's test convention).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/generate_capability_dataset.py` — the `--llmstxt` offline path (dispatch via `if "--llmstxt" in sys.argv`, ~line 502; `emit_docs()` ~line 472; helpers `_emit_llmstxt`/`_emit_ai_capability_map` read the committed `_capability_map.json` WITHOUT importing fdars, ~lines 238-490). Mirror this exactly for a `--references` path that reads `_references_map.json` and emits `docs/references.md`; extend the `llms.txt` emitter with the provenance section.
- `python/fdars/_references_map.json` — the data source (57 papers, 243 callable_index entries, 28/437 curated).
- `python/fdars/_capability_map.json` — the 437 denominator (derive the same way the guard/tool do).
- `mkdocs.yml` — nav at line 82; AI section with `AI Advisor:` (~159) and `AI Capability Map: ai-capability-map.md` (~169). Add `References:` (or similar) near there.
- `.claude/skills/fdars-capabilities/SKILL.md` (97 lines) — add the `## Scientific Provenance Protocol` section + both-path walkthrough + tests, in the skill's existing style. Reference the concrete Phase-82 tool `fdars_method_references`.
- `docs/ai-capability-map.md` — style precedent for the new `docs/references.md`.

### Established Patterns
- Offline docs emitters read committed JSON and do NOT import fdars (so CI/build works without a compiled extension). The dispatch is a simple `sys.argv` check.
- mkdocs Material nav is a YAML list; adding a page = one nav entry + the file rendering under strict (no broken links/refs).

### Integration Points
- `docs/references.md` + the `llms.txt` provenance section are generated from `_references_map.json`; the skill points at `fdars_method_references` (Phase 82) + these docs. Phase 84 runs the whole-site strict build + human citation review over all of it.

</code_context>

<specifics>
## Specific Ideas

- Coverage denominator is 437 (derived), not the stale 409 in DOCS-01/02 text.
- `grounded: bool` is per-citation and machine-readable — the skill's ungrounded fallback must be visibly labelled, never passed off as curated.
- The `--references` emitter and the extended `llms.txt` section both run OFFLINE (no fdars import), consistent with the `--llmstxt` path.

</specifics>

<deferred>
## Deferred Ideas

- Whole-site `mkdocs build --strict` (~25 min) + guard-sync + DOI gate close + BLOCKING human citation-accuracy review → Phase 84 (autonomous run STOPS there).
- Completing the uncurated N/437 tail + a coverage floor → REF-FUT-01.

</deferred>
