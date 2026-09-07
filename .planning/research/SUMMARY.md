# Project Research Summary

**Project:** pyfda — v13.0 Scientific Provenance & Cross-Language Implementations
**Domain:** Curated scientific-citation + cross-language-implementation reference data over the existing `fdars` capability-discovery system (LLM-free MCP tool + Agent Skill + MkDocs/`llms.txt`)
**Researched:** 2026-09-07
**Confidence:** HIGH (stack/architecture/pitfalls grounded in the shipped v12.0 code; features MEDIUM — canonical papers web-verified, some contested attributions flagged)

## Executive Summary

v13.0 extends fdars so that for every public callable (~409 across ~30 submodules) the AI surfaces return **grounded scientific provenance** — foundational papers with author-verified DOIs/URLs — plus **cross-language implementation pointers** (R, Python, Matlab). The decisive insight across all four research streams is that **curation is paper-level, not callable-level**: the ~409 callables collapse onto ~40–100 foundational papers, so the authoring unit is the paper (with a callable index), not 409 separate entries. Attribution must, however, be keyed at the **sub-method** level — 14+ distinct paper lineages span the surface, so module-level citation is insufficient (e.g. band depth vs. modified band depth are different papers within `depth`).

The recommended approach is a **direct extension of v12.0's proven GATE-04 pattern**, not a new architecture: a committed static side-file `python/fdars/_references_map.json` (mirroring `_capability_curation.json`), paper-keyed with a `callable_index` for O(1) lookup, read by a new **LLM-free** MCP tool `fdars_method_references()` via `importlib.resources`. A GATE-05 three-way guard-sync (mirroring GATE-04) keeps the references index, the frozenset, and the tests synchronized. The hybrid "curated-preferred, LLM-fallback-flagged-as-ungrounded" protocol lives **only in the extended `fdars-capabilities` skill** — the MCP tool itself never synthesizes. Zero new runtime dependencies (`json` + `importlib.resources` are stdlib).

The milestone-gating risk is **citation correctness**: a wrong attribution (crediting a variant to the wrong paper, wrong year/authors, textbook where a primary source belongs) is a correctness failure against the project's "provably correct" core value — not a style nit. Research already surfaced one such trap: **Fraiman & Muniz depth is 2001 (TEST), not the widely-miscited 1991.** Prevention is an author-verification workflow (each entry checked against its DOI landing page before commit) plus a **blocking human citation-accuracy review** before the docs surface ships. The secondary gating risks are LLM-free-boundary erosion (structural guards, not promises) and coverage dishonesty (report `N/409` explicitly; uncovered callables return `{"curated": false}`, never silence).

## Key Findings

### Recommended Stack

A **bespoke minimal JSON** (`_references_map.json`) with two top-level keys — `papers` (slug-keyed: title/authors/year/doi/url/venue) and a `callable_index` (`"module.callable"` → paper keys + cross-language pointers) — consistent with the existing `_capability_map.json` / `_capability_curation.json` shapes. CSL-JSON (citation-rendering, over-nested) and BibTeX (string format needing a parser) are both wrong for a lookup store. **No new dependencies.**

**Core technologies:**
- **Plain JSON + `importlib.resources.files()`**: data home + offline load — the exact pattern shipped at `fdars_list_capabilities` (server.py). Stdlib, 3.9-safe.
- **`re` + `urllib.parse` (stdlib)**: offline DOI structural gate (`^10\.\d{4,9}/\S+$`) + URL well-formedness for CI; an optional online resolve is gated behind `FDARS_ONLINE_CHECKS=1` and must never run in `pytest`/`mkdocs build`.
- **`maturin [tool.maturin] include`**: ship the new package-data JSON (existing `data/*.csv` include confirms the syntax).
- **pytest (no `jsonschema`)**: schema validity, callable-index-vs-capability-map completeness, LLM-free boundary, structural DOI/URL gate.

### Expected Features

The FDA literature landscape (see FEATURES.md — 24 family sections + 3 cross-language tables) is the authoring backbone.

**Must have (table stakes):**
- Foundational paper(s) with author-verified DOI/year for each family with a clear single root — FPCA (Ramsay & Silverman; Yao–Müller–Wang 2005 PACE), depth (Fraiman & Muniz **2001**; López-Pintado & Romo 2009 band depth; Tukey 1975 halfspace), Fréchet regression (Petersen & Müller 2019), elastic registration (Srivastava/Marron), GAK (Cuturi 2011), shapelets (Ye & Keogh 2009), FTS (Hyndman & Shang; Aue et al.).
- Cross-language pointers per family: R (`fda`, `fda.usc`, `refund`, `funData`/`MFPCA`, `fdapace`, `elasticFDA`, `funFEM`, `fdaoutlier`), Python (`scikit-fda`, with honest gaps), Matlab (`fdaM`, PACE) — package + representative function + stable URL.

**Should have (differentiators):**
- 13 families where fdars' provenance is uniquely valuable because implementations are scattered/research-code-only or cross-language gaps exist (Fréchet regression, density/LQD FDA, ITP, MFPCA, FTS — no mature Python; depth/outlier/MFPCA/FTS — no Matlab toolbox).
- Explicit "no implementation in language X" statements — honest gaps are a feature.

**Defer / anti-features:**
- Six families are **anti-features for single citation** and must return an explicit "no curated entry — ungrounded synthesis permitted, flag it" sentinel: functional depth (category, 7+ variants), scoring metrics (no FDA root), SPM (extension not primary), seasonal (heterogeneous: STL/SSA/Lomb–Scargle/Matrix Profile), XAI/explain (standard ML), conformal (frontier, no consensus root).
- Full 100% callable coverage — partial-but-honest `N/409` is acceptable this milestone; the tail rides the flagged LLM fallback.

### Architecture Approach

A separate committed side-file, not a capability-map extension (extending the auto-generated map would break the SKILL no-drift boundary). Paper-keyed schema + flat `callable_index` in the same identifier space as `_capability_curation.json`. The MCP tool is a pure static lookup returning `{"curated": true, papers[], cross_language[], coverage: "N/409"}` or `{"curated": false, "sentinel": "NO_CURATED_ENTRY"}`. Docs/`llms.txt` emit offline from the committed JSON via a `--references` flag on `generate_capability_dataset.py` (no `fdars` import at build). The skill carries the hybrid protocol.

**Major components:**
1. **`python/fdars/_references_map.json`** — curated data home (papers + callable_index + cross-language pointers).
2. **`fdars_method_references()` MCP tool** — LLM-free static lookup alongside `fdars_list_capabilities`; `_REFERENCES_MODULES` derived from `_CAPABILITY_MODULES` (not re-declared).
3. **GATE-05 guard-sync** (in `test_guard_sync_version_independent.py`) — internal index consistency, callable-index ⊆ capability map, LLM-free boundary (no `provider`/`model` keys), frozenset literal mirror.
4. **Docs emit** — `docs/references.md` + per-method References blocks + `llms.txt` provenance section (with coverage fraction), generated offline.
5. **Extended `fdars-capabilities` SKILL.md** — hybrid curated/flagged-ungrounded protocol; no advisor-skill duplication.

### Critical Pitfalls

1. **Wrong citation / variant conflation (milestone-gating)** — a resolving DOI ≠ correct attribution. Author-verify every entry against its DOI landing page before commit; blocking human citation-accuracy review before docs ship; flag contested attributions rather than forcing one (F&M 2001-not-1991 is the canonical trap).
2. **LLM-free boundary erosion (milestone-gating)** — the tool must never synthesize; keep it a static `importlib.resources` load with a `curated:false` sentinel, guard-sync asserting no `provider`/`model` keys. Hybrid fallback lives only in the skill, with a machine-readable `grounded: bool` per citation, not prose caveats.
3. **Coverage dishonesty** — silently-partial coverage read as complete. Report `N/409` in docs, `llms.txt`, and the tool response; uncovered callables signal `{"curated": false}`, never empty/error.
4. **Guard-sync drift** — derive `_REFERENCES_MODULES` from `_CAPABILITY_MODULES` at import so a future crate-bump adding a submodule can't silently desync; write the guard test in the SAME commit as the tool handler.
5. **Cross-language inaccuracy / link rot** — fabricated foreign implementations or wrong function names; mark Matlab (fdaM/PACE) pointers `confidence: low` unless individually verified; point URLs at specific function docs, not homepages; structural link gate now, online resolve opt-in only.

## Implications for Roadmap

> Phase numbering **continues from v12.0** (which ended at Phase 79) — suggested phases below are **80–84**. Curation is the critical path; the MCP tool can run parallel to it.

### Phase 80: Schema + Data Home + Primary Guard Tests
**Rationale:** Everything downstream depends on the schema; build it first with a 3–5 paper stub.
**Delivers:** `_references_map.json` stub, JSON schema + author-verification workflow doc, `pyproject.toml` maturin `include`, GATE-05 **primary** tests (internal consistency + callable-index ⊆ capability map), offline DOI/URL structural gate.
**Uses:** plain JSON + `importlib.resources`; mirrors `_capability_curation.json`.
**Avoids:** guard-sync drift (frozenset derived from `_CAPABILITY_MODULES`).

### Phase 81: Curation — Paper Registry (bulk / critical path)
**Rationale:** The milestone's substantive work; longest phase.
**Delivers:** hand-authored paper-level entries across the families with clear roots + callable_index + R/Python/Matlab pointers; the six anti-feature families wired to the `curated:false` sentinel; explicit `N/409` coverage. Family-by-family, with a small verified sample per family before moving on. Start with one family (depth, ~5 papers/~15 callables) to calibrate authoring velocity.
**Addresses:** table-stakes + differentiator families from FEATURES.md.
**Avoids:** citation-correctness pitfall (author-verification before each commit).

### Phase 82: MCP Tool + GATE-05 Complete
**Rationale:** Can start right after Phase 80's schema; run parallel to Phase 81.
**Delivers:** `fdars_method_references()` LLM-free lookup, `_REFERENCES_MODULES`, GATE-05 **companion** tests (LLM-free boundary + frozenset mirror), curated/sentinel return shape.
**Implements:** components 2 + 3.
**Avoids:** LLM-free boundary erosion.

### Phase 83: Docs + llms.txt + Skill Extension
**Rationale:** Needs Phase 81 at a meaningful coverage threshold.
**Delivers:** `docs/references.md` (family-grouped method→paper→implementation), `llms.txt` provenance section w/ coverage fraction, extended `fdars-capabilities` SKILL.md (hybrid protocol), `mkdocs.yml` nav wiring — all emitted offline from committed JSON.
**Implements:** components 4 + 5.

### Phase 84: Close Gate + Blocking Citation-Accuracy Review
**Rationale:** Validation only — no new curation/tool work.
**Delivers:** whole-site `mkdocs build --strict` green offline; GATE-05 all groups green; DOI/URL structural gate green; **blocking human citation-accuracy review** (sample verified against DOI landing pages by a human, not an LLM); coverage report reviewed; grounding invariant + guard-sync confirmed.
**Avoids:** citation-correctness + coverage-dishonesty pitfalls as the hard close gate.

### Phase Ordering Rationale
- Schema first unblocks tool + curation in parallel (mirrors v12.0 sequencing).
- Curation is the critical path and the correctness surface — it gets its own phase with per-family verification, not folded into the tool phase.
- Guard tests land with the code they guard (GATE-04 lesson), not bolted on later.
- The blocking human review sits between curation/docs and close — citations are correctness claims, parallel to the standing v6.0 blocking diagram review.

### Research Flags
Phases likely needing deeper research during planning:
- **Phase 81 (Curation):** cross-reference `fdars-core` source per family to confirm method→paper mapping; resolve the flagged open attributions — `oneway_anova_vstat` (V-stat, tentatively Zhang & Liang 2014), `elastic_changepoint` (root unclear), `align_cluster_fd` (Sangalli 2010 vs. Tucker 2013 — flag, don't pick).
- **Phase 83 (Docs emit):** test `generate_capability_dataset.py --references` against the Phase 80 stub before finalizing.

Phases with standard patterns (skip research-phase):
- **Phase 80 (Schema):** direct application of `_capability_map.json` / `_capability_curation.json`.
- **Phase 82 (GATE-05):** direct replication of the GATE-04 three-way mirror.
- **Phase 84 (Close gate):** standard `mkdocs build --strict` + pytest.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Format/packaging/testing derived from shipped v12.0 code (server.py, guard-sync tests); stdlib-only |
| Features | MEDIUM | Canonical papers web-verified + DOI spot-checked; some contested attributions & active-research areas flagged |
| Architecture | HIGH | GATE-05 is a structural mirror of read-in-full GATE-04; side-file pattern confirmed against `_capability_curation.json` |
| Pitfalls | HIGH | Grounded in the shipped grounding-invariant culture; band-depth/modified-band-depth is a concrete in-repo example |

**Overall confidence:** HIGH

### Gaps to Address
- **Contested attributions** (`align_cluster_fd`, `elastic_changepoint`, `oneway_anova_vstat`): resolve during Phase 81 curation against fdars-core source; where genuinely contested, flag in-JSON rather than forcing a single citation.
- **Matlab pointer verification**: fdaM/PACE function-level stability not individually verified — mark `confidence: low` until checked in Phase 81.
- **Coverage target**: exact `N/409` threshold for "done" is a Phase-81 decision; partial-but-honest is acceptable, remainder deferrable to a future milestone.
- **Citation-accuracy reviewer**: the blocking Phase-84 review needs a human domain check (not LLM) — identify the reviewer/sample size at planning.

## Sources

### Primary (HIGH confidence)
- Shipped v12.0 code: `python/fdars/mcp/server.py` (`fdars_list_capabilities`, `importlib.resources`), `tests/test_guard_sync_version_independent.py` (GATE-04), `_capability_map.json` / `_capability_curation.json`, `scripts/generate_capability_dataset.py` (`--llmstxt`/`--references` emit).
- FDA canonical papers verified against publisher pages (Ramsay & Silverman; Petersen & Müller 2019; López-Pintado & Romo 2009 JASA; Cuturi 2011; Ye & Keogh 2009; Yao–Müller–Wang 2005).

### Secondary (MEDIUM confidence)
- CRAN / PyPI / CTAN package inventories for R/Python/Matlab cross-language pointers (stable but function-level naming to be reconfirmed in curation).
- Fraiman & Muniz **2001 (TEST)** attribution — corrects a widespread 1991 miscitation.

### Tertiary (LOW confidence)
- Matlab research-code implementations (elastic FDA, PACE variants) — enumeration incomplete; mark low-confidence pending per-entry verification.
- Frontier-area root papers (conformal, XAI/explain) — no consensus; classified as anti-features for single citation.

---
*Research completed: 2026-09-07*
*Ready for roadmap: yes*
