# Phase 81: Curation — Paper Registry - Context

**Gathered:** 2026-09-07
**Status:** Ready for planning
**Mode:** Smart discuss (autonomous) — grey areas accepted by user; remaining shape locked in ROADMAP/STATE decision log

<domain>
## Phase Boundary

Populate `python/fdars/_references_map.json` (schema locked in Phase 80) with author-verified, sub-method-accurate paper provenance + cross-language pointers across the table-stakes and differentiator families — the substantive, correctness-critical body of v13.0. Anti-feature families are wired to the `curated:false` sentinel; coverage is measured and reported honestly as `N/409`.

Delivers (CURATE-01..05):
1. Paper-level entries for the clear-root families (basis/smoothing, functional statistics, FM/band/modified-band depth, functional boxplot, dense FPCA + PACE, scalar-on-function & FLM, Fréchet regression, density/LQD FDA, elastic/SRSF registration, shift/landmark registration, metrics incl. GAK/DTW/soft-DTW, clustering, classification, inference incl. ITP/SCB, FTS incl. DPCA, shapelets, MFPCA/FAMM) — each entry's authors/year/title verified against its DOI landing page.
2. `callable_index` records sub-method-level attribution (`band_1d` vs `modified_band_1d` → distinct papers); contested/multi-primary cases list co-primaries or are flagged in-JSON, never force-picked.
3. Cross-language pointers (R / Python / Matlab) with package + representative function + `version` + specific-function URL per covered paper; Matlab `confidence: low` unless verified; honest "no implementation in language X" gaps recorded explicitly.
4. Six anti-feature families (functional depth as a category via `functional_depth` dispatcher, scoring metrics, SPM, seasonal, XAI/explain, conformal) wired to the `curated:false` sentinel — absent from `callable_index` at the module-category level (per-sub-method depth papers may still be curated where a clear root exists).
5. Coverage measured + honest: the achieved `N/409` fraction recorded (in-JSON coverage metadata and/or `not_yet_curated` derivation) and emitted by the primary guard test; only author-verified entries carry provenance — NO LLM-synthesized placeholder ships as curated.

Out of scope: the MCP tool handler (Phase 82, parallelizable), docs/llms.txt/skill (Phase 83), the whole-site strict gate + blocking human citation review (Phase 84).

</domain>

<decisions>
## Implementation Decisions

### Curation scope & verification (user-accepted this pass)
- **Breadth = ALL clear-root families now.** Curate every table-stakes + differentiator family that has a clear primary root. Genuinely-unclear callables get `curated:false` rather than a forced citation. Anti-feature families → sentinel. Widest HONEST coverage in one pass (partial-but-honest is accepted; the remaining tail is deferred to REF-FUT-01).
- **Verification = best-effort autonomous verify + flag.** For each paper, web-check authors/year/title against its DOI landing page; mark `curated:true` ONLY on a match; flag anything uncertain `curated:false` or contested-in-JSON. This maximizes what lands verified now. The standing BLOCKING human citation-accuracy review at Phase 84 (GATE-03) still gates final sign-off regardless — autonomous execution proceeds through 81→82→83 and STOPS at 84 for that human review.
- **Contested attributions = resolve vs fdars-core source, co-primary or flag.** For `align_cluster_fd`, `elastic_changepoint`, `oneway_anova_vstat`, and the FAMM lineage: check each against the fdars-core implementation; list co-primary papers where lineage is clear; flag in-JSON as contested (NOT force-picked) where genuinely ambiguous.

### Locked by ROADMAP / STATE decision log
- Curation is PAPER-LEVEL (~40–100 papers, N << 409) with a sub-method-keyed callable index — NOT 409 separate entries, NOT one paper mapped blindly across a family (band depth ≠ modified band depth).
- F&M depth is 2001 (DOI 10.1007/BF02595706), not 1991 — the canonical example of why DOI-landing-page verification is mandatory.
- Cross-language: R (fda, fda.usc, refund, funData/MFPCA, fdapace, fdasrvf, funFEM, fdaoutlier, ftsa, freqdom.fda), Python (scikit-fda, fdasrsf, tslearn, sktime), Matlab (fdaM, PACE, fdasrvf_MATLAB); each with package + representative function + `version` + specific-function URL; Matlab `confidence: low` unless individually verified; honest no-implementation gaps recorded explicitly.
- Every entry MUST keep the Phase-80 GATE-05 invariants green as curation grows: internal consistency (`callable_index` keys == union of `papers[*].callables`), cross-file resolution (every key resolves in `_capability_map.json`, `_Fdata` special-cased), and the structural DOI/URL gate (DOI regex, URL well-formedness + domain allowlist; new cross-language domains must be added to the allowlist).
- Coverage is partial-but-honest; report `N/409` explicitly; uncovered callables signal `curated:false`, never silence or an empty dict.

### Claude's Discretion
- The specific papers per family and their exact DOIs/URLs (author-verified per the decision above).
- In-JSON coverage-metadata shape for the `N/409` fraction and the `not_yet_curated` derivation, consistent with the Phase-80 schema and what the guard test can emit.
- Batching strategy across families (the executor may curate family-by-family), provided each committed batch keeps GATE-05 green.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `python/fdars/_references_map.json` — the locked Phase-80 schema + 5-paper seed (depth, band depth, SRSF, FPCA, P-splines) to build on. Currently 5 papers / 10 callable_index entries.
- `python/fdars/_capability_map.json` — nested dict keyed by module (`_Fdata`, `alignment`, `basis`, `classification`, `clustering`, `conformal`, `covariance`, `datasets`, …); the cross-file resolution target and the source of the 409-callable denominator.
- `python/fdars/_capability_curation.json` — the identifier space (`module.callable`, `_Fdata.*` special-cased) curation keys must match.
- `docs/authoring/references-schema.md` — the Phase-80 authoring guide governing entry shape + the author-verification bar; follow it verbatim and keep its shipped example in sync if the seed shape changes.
- `tests/test_guard_sync_version_independent.py` — Group-3 GATE-05 A/B/C guards that validate every new entry; run after each curation batch.

### Established Patterns
- Data side-files live in `python/fdars/` and ship in the wheel automatically (no maturin `include` needed).
- The DOI/URL structural gate enforces a domain allowlist — adding cross-language pointers to new domains requires extending the allowlist in the guard test (same commit as the data).

### Integration Points
- Phase 82's MCP tool reads this JSON; Phase 83's docs/llms.txt generate offline from it; Phase 84 gates the whole thing. Correctness here is the milestone's core value.

</code_context>

<specifics>
## Specific Ideas

- The `functional_depth` dispatcher (category-level) is an anti-feature family → sentinel; but per-sub-method depth papers (FM 2001, band/modified-band LP&R 2009) ARE curated where a clear root exists.
- Six anti-feature families = functional depth as a category, scoring metrics, SPM, seasonal, XAI/explain, conformal.
- Contested set to resolve against fdars-core source: `align_cluster_fd`, `elastic_changepoint`, `oneway_anova_vstat`, FAMM lineage.
- Coverage fraction is informational this milestone (no hard floor) — GATE-05 emits it; a coverage floor is deferred to REF-FUT-01.

</specifics>

<deferred>
## Deferred Ideas

- Completing the uncurated `N/409` tail + a coverage floor once curation stabilizes → REF-FUT-01 (future milestone).
- Opt-in live DOI/URL liveness resolve (`scripts/check_doi_liveness.py`, `FDARS_ONLINE_CHECKS=1`) → REF-FUT-02.
- The MCP tool handler + GATE-05 companion mirror → Phase 82.
- References docs page, llms.txt provenance section, skill hybrid protocol → Phase 83.
- Whole-site strict build + guard-sync + DOI gate close + BLOCKING human citation-accuracy review → Phase 84 (autonomous run stops here).

</deferred>
