# Phase 80: Schema, Data Home & Primary Guard Tests - Context

**Gathered:** 2026-09-07
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure phase — schema/data-home/guard-test scaffolding; grey areas already locked in ROADMAP/STATE decision log)

<domain>
## Phase Boundary

Establish the references data home so all downstream v13.0 curation/tool/docs work validates from day one — the schema is never authored free-form. Delivers four things and nothing more:

1. A committed `python/fdars/_references_map.json` — paper-keyed `papers` object + flat `callable_index`, in the SAME identifier space as `_capability_curation.json` (`module.callable`, `_Fdata.*` special-cased). Packaged as wheel data (maturin `include`), loadable via `importlib.resources`. Seeded with a small **3–5 paper author-verified stub** spanning distinct capability families.
2. A documented **author-verification workflow + JSON schema doc** governing curation: paper-level unit, sub-method-keyed callable claims, cross-language entry shape carrying `version` + Matlab `confidence`, the `curated:false` tail convention, and the personal DOI-landing-page verification bar.
3. **Primary GATE-05 tests** (Python 3.9+, no `mcp` import): internal consistency (`callable_index` keys == union of `papers[*].callables`) and cross-file (every `callable_index` key resolves to a real callable in `_capability_map.json`, `_Fdata` special-cased).
4. An **offline structural DOI/URL gate**: DOI regex `^10\.\d{4,9}/\S+$`; URL well-formedness + domain allowlist. Runs in CI with NO live network resolve. Any live resolve is opt-in (`FDARS_ONLINE_CHECKS=1`) and never runs under `pytest`/`mkdocs build`.

Explicitly OUT of scope this phase: broad curation (that is Phase 81), the MCP tool handler (Phase 82), docs/llms.txt/skill (Phase 83), the whole-site strict gate (Phase 84).

</domain>

<decisions>
## Implementation Decisions

### Locked by ROADMAP / STATE decision log (not re-litigated here)
- References map is a SEPARATE committed side-file `_references_map.json`, paper-keyed + flat `callable_index`, NOT merged into the auto-generated `_capability_map.json` (preserves the SKILL-02 no-drift boundary; mirrors `_capability_curation.json`).
- Identifier space is IDENTICAL to `_capability_curation.json`: `module.callable`, with `_Fdata.*` special-cased against `_capability_map.json`.
- Curation is PAPER-LEVEL with a sub-method-keyed callable index — not one paper blindly mapped across a family (band depth ≠ modified band depth).
- Author-verification is a HARD authoring rule — every paper entry checked against its DOI landing page before commit (F&M is 2001, not 1991; a resolving DOI is NOT proof of correct attribution).
- The `curated:false` / `{"sentinel": "NO_CURATED_ENTRY"}` tail convention is defined here so Phase 82's tool and Phase 81's curation share one shape.
- Cross-language entry shape carries `version` + Matlab `confidence: low` unless verified; point URLs at specific function docs.
- DOI gate is STRUCTURAL only in CI (regex + URL well-formedness + domain allowlist); live resolve is opt-in via `FDARS_ONLINE_CHECKS=1`, never under pytest/mkdocs.
- Guard tests land in the SAME commit as the artifact they guard (GATE-04 lesson).

### Claude's Discretion
- Exact 3–5 seed papers, provided they are author-verified against DOI landing pages and span DISTINCT capability families (e.g. depth, alignment/SRSF, FPCA/basis, clustering). Choose clear-provenance roots to avoid contested attributions this early.
- Precise JSON schema field names/nesting for `papers[*]` (title, authors, year, doi, url, callables, cross_language, notes) and the exact domain allowlist, guided by the mirrored `_capability_curation.json` structure and the cross-language shape above.
- Where the schema doc lives (docs/ page vs. a `docs/`-adjacent authoring note) and test file placement, following existing `tests/` and guard-sync conventions.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/_capability_curation.json` — flat `module.callable` → description map; the identifier space and packaging pattern to mirror for `_references_map.json`.
- `python/fdars/_capability_map.json` — auto-generated capability surface; the cross-file resolution target for GATE-05 (every `callable_index` key must resolve here).
- `python/fdars/mcp/server.py` — where the LLM-free tool pattern lives (Phase 82 consumer; not touched this phase beyond understanding the load pattern).
- `scripts/generate_capability_dataset.py` — the offline `--llmstxt` generation precedent; the `--references` offline path (Phase 83) will mirror it.
- `tests/test_guard_sync_version_independent.py` — existing guard-sync group home; primary GATE-05 tests (Group 3 A/B, Py3.9+) belong alongside.

### Established Patterns
- Data side-files live in `python/fdars/` and load via `importlib.resources`; wheel data packaged through maturin `include` in `pyproject.toml` (currently `python/fdars/data/*.csv` — extend as needed for the JSON side-file).
- Guard-sync tests derive module lists from a single source (`_REFERENCES_MODULES` DERIVED from `_CAPABILITY_MODULES`) so a future crate-bump adding a submodule cannot silently desync.

### Integration Points
- `_references_map.json` cross-validates against `_capability_map.json` (GATE-05 cross-file test).
- CI test suite (`pytest`) picks up the new guard + DOI-structural tests; `FDARS_ONLINE_CHECKS` env gate keeps live resolve out of CI/build.

</code_context>

<specifics>
## Specific Ideas

- DOI regex is fixed: `^10\.\d{4,9}/\S+$`.
- Online liveness resolve is deferred (REF-FUT-02): `scripts/check_doi_liveness.py`, `FDARS_ONLINE_CHECKS=1`, never in CI — a stub/placeholder boundary is acceptable this phase as long as the structural gate is real.
- Coverage is reported as `N/409` downstream; this phase only needs the shape + stub, not broad coverage.

</specifics>

<deferred>
## Deferred Ideas

- Broad paper curation across all table-stakes/differentiator families → Phase 81.
- `fdars_method_references` MCP tool handler + full GATE-05 companion mirror → Phase 82.
- References docs page, `llms.txt` provenance section, skill hybrid protocol → Phase 83.
- Whole-site strict build + guard-sync + DOI gate close + human citation review → Phase 84.
- REF-FUT-01 (complete the uncurated tail + coverage floor) and REF-FUT-02 (opt-in live DOI liveness) → future milestone.

</deferred>
