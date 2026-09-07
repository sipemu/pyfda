# Pitfalls Research

**Domain:** Scientific-provenance + cross-language-reference data layer for a functional data analysis library (v13.0 — curated references map + LLM-free MCP tool + hybrid skill)
**Researched:** 2026-09-07
**Confidence:** HIGH (grounded in the shipped codebase: GATE-04 guard-sync pattern in `tests/test_guard_sync_version_independent.py`, MCP LLM-free pattern in `python/fdars/mcp/server.py`, grounding invariant in PROJECT.md; no speculative stack choices required)

---

## Critical Pitfalls

### Pitfall 1: Subtly Wrong Citation — Method-Variant Attribution

**What goes wrong:**
A callable is linked to the wrong foundational paper. The most dangerous form is a variant-to-base conflation: `modified_band_depth` mapped to the Band Depth paper (López-Pintado & Romo 2009) instead of the Modified Band Depth paper (López-Pintado & Romo 2011, JCGS). A DOI that resolves is no proof of correct attribution — the DOI can be real and still be the wrong paper (a survey, a companion paper, the wrong author group's independent derivation). Because the documentation's core value is "provably correct", a wrong citation is a correctness failure on the primary deliverable.

**Why it happens:**
LLMs trained on FDA literature confuse closely related papers (multiple authors publish "band depth" variants); the correct DOI is often findable on first search but the first hit is not always the primary source. Survey textbooks (Ramsay & Silverman 2005, Ferraty & Vieu 2006) are cited as primary sources for methods that have earlier journal papers. Human curation rushed under coverage pressure skips author verification and settles for the first plausible-sounding citation.

**How to avoid:**
- Author-verified workflow: for every paper entry in the JSON, the author name + year + title must be cross-checked against the DOI landing page before commit. Do not accept DOI-only as proof.
- Distinguish method variants explicitly: the callable→paper index must record the exact claim (e.g., "this callable implements Modified Band Depth, not Band Depth"), not just a pointer.
- Flag contested attributions: where multiple groups published the same method independently (e.g., Fraiman-Muniz depth), record all co-primary papers and note the attribution is shared.
- Never cite a textbook/survey where the primary journal paper exists; the textbook can be listed as a secondary reference but not as the foundational paper.
- Structural DOI gate in CI: all DOIs must match the regex `^10\.\d{4,}/` (structural validity only — offline, no live resolve); this catches fabricated or obviously wrong DOIs but is not sufficient alone.

**Warning signs:**
- Curated entries where "authors" is a single generic name (e.g., "López-Pintado") without distinguishing which of their several papers is meant.
- Multiple callables sharing the exact same DOI when the methods are visibly different variants (e.g., `band_depth_1d` and `modified_band_depth_1d` pointing to the same paper).
- Year mismatches between the title field and the DOI landing page.
- A survey or textbook DOI as the sole reference for a method that has a journal-primary source.

**Phase to address:**
The curation phase (the first authoring phase, likely Phase 80). The author-verification workflow must be defined before any entries are committed, not retroactively. The CI structural gate belongs in the same phase as the JSON schema definition. A separate review gate (analogous to the blocking human diagram review used in v1.0–v10.0) should cover citation accuracy before the docs surface phase.

---

### Pitfall 2: Grounding-Boundary Erosion — The MCP Tool Starting to Synthesize

**What goes wrong:**
The `fdars_method_references` MCP tool begins returning synthesized or interpolated answers for the "tail" callables (those without a curated entry). Instead of returning an explicit `"no_curated_entry": true` signal, the tool returns a best-guess citation it assembled at query time — either from LLM-generated content embedded in the JSON at curation time, or from inline synthesis logic added to the tool handler. This collapses the LLM-free boundary that GATE-04 and the existing tests prove.

**Why it happens:**
Pressure to give the user something rather than a clean "no entry" response leads to embedding synthesized content into the curated JSON during the authoring phase ("this is just placeholder, we'll fix it later"). The placeholder never gets reviewed and ships as curated fact. Alternatively, a tool-handler branch is added to "handle the tail gracefully" by calling an LLM inside the tool — mirroring the hybrid skill's behavior but inside the MCP boundary where it must not appear.

**How to avoid:**
- The MCP tool must only read the committed static JSON via `importlib.resources`. No model call, no provider import, no synthesis logic inside the tool handler. This is the same pattern as `fdars_list_capabilities`.
- The JSON schema must encode absence explicitly: a callable not present in the references map MUST be absent from the JSON, not present with empty or synthesized fields. The tool returns the absence signal (`{"curated": false, "ungrounded_synthesis_permitted": true}`) as a first-class response, not a fallback error.
- The guard-sync test (mirror of GATE-04) must check: (a) the tool returns no `"provider"` or `"model"` keys; (b) for a known absent callable the response contains `"curated": false` and does not contain a `"doi"` key; (c) the tool does not import any advisor or LLM provider module.
- The "hybrid" protocol (curated preferred, LLM fallback flagged) lives exclusively in the `fdars-capabilities` skill, not in the MCP tool.

**Warning signs:**
- Any `import` of `fdars.advisor`, any provider class, or `anthropic` / `openai` appearing in `python/fdars/mcp/server.py` or the new references tool module.
- A `"doi"` or `"paper"` key present in the tool response for a callable that is not in the curated JSON.
- The guard-sync test not asserting the absence of `"provider"` / `"model"` keys on the references tool response.
- The curated JSON containing a field like `"synthesized": true` or `"llm_generated": true` — these are red flags that LLM content entered the static data at authoring time.

**Phase to address:**
The MCP tool implementation phase (the phase that writes `fdars_method_references`). The guard-sync test asserting LLM-free boundary must be written in the same commit as the tool, not added later. The GATE-04 three-way mirror pattern (JSON keys == server frozenset == test expected frozenset) should be replicated for the references map: `_REFERENCES_MODULES` frozenset + test assertion + JSON key set, all updated atomically.

---

### Pitfall 3: Grounding-Boundary Erosion — Ungrounded Fallback Not Flagged in the Skill

**What goes wrong:**
The `fdars-capabilities` skill answers "what is the scientific root of X?" for a callable that has no curated entry, but the LLM-generated answer is not marked as ungrounded. The skill's prose or structured output presents the synthesized citation alongside curated ones without visual or structural differentiation. A user reading the answer cannot tell which citations are verified and which are synthesized.

**Why it happens:**
The skill's system prompt says "flag ungrounded answers" but the LLM's response elides the flag when it is confident (hallucination + overconfidence). The skill does not structurally enforce a flag — it relies on prose wording, which can be dropped. The consuming LLM (in an agentic loop) receives the answer and passes it through without preserving the flag.

**How to avoid:**
- The skill's protocol must require a structural `"grounded": bool` field per citation in the output, not just a prose caveat. The SKILL.md walkthrough must demonstrate both paths (curated and ungrounded).
- The MCP tool's explicit `"curated": false` signal is the machine-readable gate: the skill receives this signal and MUST include it structurally in its output before any synthesis.
- The skill should refuse to present synthesized citations with the same formatting as curated ones. A concrete pattern: curated entries return DOI + authors in a formatted block; synthesized entries return only a hedged prose summary with a visible `[UNGROUNDED — not from curated data]` label.
- This is analogous to the existing `_check_grounding` guard in the advisor: the guard must check for the citation's provenance, not just the presence of a number.

**Warning signs:**
- A skill response where DOIs appear for callables not present in `_references_map.json`.
- A skill walkthrough in SKILL.md that only demonstrates the curated path and omits the ungrounded-fallback path.
- Test coverage that only calls the skill for callables with curated entries.

**Phase to address:**
The skill extension phase (the phase that extends `fdars-capabilities`). The SKILL.md must explicitly document the hybrid protocol and include a worked example of the ungrounded path. Tests must exercise both branches.

---

### Pitfall 4: Guard-Sync Tests Going Stale — The Three-Way Mirror Breaks Silently

**What goes wrong:**
A new phase adds a callable or module to `fdars` but does not update the references map and its associated frozenset guard. The guard-sync test still passes (because it only checks the existing set against itself), but the references map is silently incomplete for the new callable. Alternatively: the `_REFERENCES_MODULES` frozenset in `server.py` is updated but `_EXPECTED_REFERENCES_MODULES` in the test file is not, causing a test failure — the inverse of silent staleness.

**Why it happens:**
The GATE-04 pattern works because all three points (JSON, server frozenset, test frozenset) are updated in one atomic commit. When a future crate-bump milestone adds a new submodule (as v11.0 added `fdars.fts`, `fdars.density_fda`, etc.), the references-map frozenset must also be updated. If the update is forgotten, the guard passes silently because the missing module is absent from both the JSON and the frozenset — the test cannot detect what it does not know to expect.

**How to avoid:**
- The guard-sync test for references must check against the SAME `_EXPECTED_CAPABILITY_MODULES` frozenset used in GATE-04, not a separate references-specific frozenset. This way, when a new submodule is added and GATE-04's frozenset is updated (as required by the existing guard), the references guard also fails if the references map is not updated.
- Alternatively: the references tool's frozenset can be derived from `_CAPABILITY_MODULES` at import time rather than re-declared, making drift structurally impossible rather than test-detected.
- The maintenance note in the test file must explicitly state: "when adding a new fdars submodule, update both GATE-04 frozensets AND the references map."

**Warning signs:**
- A new fdars submodule (e.g., added in a future v14.0 crate bump) whose callables are absent from the references map with no `"not_covered"` record or coverage report.
- The `_REFERENCES_MODULES` frozenset diverging from `_CAPABILITY_MODULES` without a documented reason.

**Phase to address:**
The MCP tool implementation phase (define the frozenset relationship). Then every future crate-bump milestone must include a references-map coverage review in its close gate.

---

### Pitfall 5: Coverage Dishonesty — Partial Coverage Presented as Complete

**What goes wrong:**
The references map covers 200 of ~409 callables (because many share one foundational paper and paper-level curation is tractable, but the callable→paper index is not complete). The docs page and `llms.txt` entry say "fdars references" without stating that ~209 callables have no curated entry. A user or agent asks about a callable in the uncovered tail and receives either silence or a confusingly empty response, without understanding that the gap is known and intentional.

**Why it happens:**
Coverage numbers are never stated; the docs page lists covered methods without noting what is not covered. The `llms.txt` digest says "409 callables" (from the capability map) but the references section covers only the subset with curated entries. The gap between the capability count and the references count is invisible.

**How to avoid:**
- The `fdars_method_references` tool must always report coverage metadata in its response: `{"callable_count": 409, "covered_count": N, "coverage_fraction": N/409}`. This makes the tail visible to every consumer.
- The docs References page must include a prominent "Coverage" section: "N of 409 callables have curated entries. Remaining callables return an explicit 'no curated entry' signal." Do not omit this.
- `llms.txt` must have a separate `## References Coverage` section that states the fraction, not just "references available."
- The callable→paper index must include an explicit `"not_yet_curated"` list or a coverage report generated at build time so the tail is machine-readable.

**Warning signs:**
- A docs References page with no coverage fraction stated.
- `llms.txt` references section that claims to cover "all callables" or omits a coverage number.
- The MCP tool response for an uncovered callable returning `{}` (empty dict) rather than an explicit `{"curated": false}` signal.

**Phase to address:**
The docs surface phase (the phase that writes the References page and `llms.txt` entry). The coverage fraction must be computed and displayed as part of the docs build, not manually maintained.

---

### Pitfall 6: Cross-Language Accuracy — Fabricated or Stale Implementation Pointers

**What goes wrong:**
The references map lists `fda::fbplot` (R, fda package) as the cross-language implementation for `functional_boxplot`, but the function has been renamed or its signature changed in a recent version. Or: an R package is listed that does not implement the method at all (e.g., a package listed for "elastic alignment" that only has basic registration). Or: a Python (scikit-fda) function is listed by name but the function does not exist in the current version of scikit-fda. The user follows the pointer and finds nothing, eroding trust in the entire references layer.

**Why it happens:**
Cross-language implementation data is harder to verify than DOIs: a DOI is stable by design, but a package function can be renamed, removed, or its behavior changed. LLM-generated cross-language pointers are plausible-sounding but frequently hallucinate function names. Even curated entries go stale as packages evolve (R's `fda` package, scikit-fda, and Matlab's fdaM all have active development).

**How to avoid:**
- For each cross-language entry, record: package name, function/class name, version pinned at curation time, URL to the specific function's docs/source (not just the package homepage). Version pinning makes staleness detectable.
- The structural CI gate must check that all cross-language URLs match the declared domain allowlist (e.g., `cran.r-project.org`, `scikit-fda.readthedocs.io`, `github.com/SCRFpublic/fdaM`). A URL pointing to an unrelated domain is a red flag.
- Distinguish "function-level" from "package-level" coverage honestly: if R's `fda.usc` package implements the same family but not the exact function, say "family-level coverage" not "function `fda.usc::fdata.comp`".
- Do not claim feature parity where the implementation differs materially (e.g., scikit-fda's FPCA uses a different basis expansion than fdars's). A `"differences"` field in the cross-language entry should note known behavioral differences.
- Treat Matlab pointers conservatively: the Ramsay fdaM and PACE toolboxes are less maintained and function availability is harder to verify. Mark Matlab entries as `"confidence": "low"` unless individually verified.

**Warning signs:**
- Cross-language entries with no `version` field.
- URLs pointing to package homepages rather than specific function documentation.
- `"function"` field values that include generic names like `"compute"` or `"fit"` without the package-qualified name.
- Multiple cross-language entries all pointing to the same package URL (a sign of bulk-generated rather than individually verified entries).

**Phase to address:**
The curation phase. A separate verification checklist for cross-language pointers (parallel to the author-verification checklist for citations) must be completed before entries are committed.

---

### Pitfall 7: Scope Underestimate — LLM Quietly Becomes the Primary Curation Path

**What goes wrong:**
The 409-callable scope feels tractable at the paper level (many callables share one root paper), but the callable→paper index is still a large authoring task. Under time pressure, the team uses LLM-generated first-pass entries as the primary source rather than as a candidate list for human verification. The review step is reduced to spot-checking, and LLM hallucinations ship as curated fact. Coverage pressure ("we need to cover all 409") compounds the problem: partial coverage honestly declared is better than full coverage dishonestly assembled.

**Why it happens:**
The paper-level curation unit is correctly chosen to keep effort tractable, but the callable→paper index still requires individually deciding which paper applies to each callable. LLM tools are fast and produce plausible output, making it tempting to trust them without verification. The "hybrid" framing (curated preferred, LLM fallback permitted) can be misread as permission to use LLM output in the curated layer.

**How to avoid:**
- Phase the curation explicitly by method family (depth methods, smoothing methods, regression methods, etc.) with a stated target and a human-reviewed sample per batch. Do not attempt all 409 in one pass.
- Define a minimum bar for "curated" at the start of the curation phase: author name + year match the DOI landing page, verified by the curator personally (not delegated to the LLM). LLM output is input to the verification workflow, not the output of it.
- Track and report the authoring velocity honestly: if the depth family (15 callables, ~5 root papers) takes 2 hours to verify, project the remaining families accordingly before committing to a milestone scope.
- The "curated" field in the JSON schema is a promise; only entries that have been author-verified should have `"curated": true`. A partial milestone that covers 200 of 409 callables with honest coverage reporting is better than a "complete" milestone with 409 unverified entries.

**Warning signs:**
- Curation proceeding faster than one entry per 10 minutes (author verification takes time; speed is a red flag).
- The curator cannot name the journal and year for a given entry without re-looking it up (indicates the entry was copy-pasted, not verified).
- Coverage advancing faster than the review gate can keep up.

**Phase to address:**
Roadmap planning (before Phase 80). The curation phase plan must include an explicit authoring-velocity estimate based on a trial curation of one method family (e.g., depth methods), a stated coverage target that is honest about what can be fully verified in the milestone's scope, and a defined minimum bar for "curated."

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Use LLM to generate first-pass citations, then "spot-check" a sample | Dramatically faster initial coverage | Unchecked entries ship as curated fact; wrong DOIs and wrong attributions accumulate silently | Never for the curated JSON. Acceptable for generating a candidate list that is then fully author-verified before commit. |
| Map one paper to all callables in a family without checking each callable's actual method variant | Tractable curation across 409 callables | Variant-level attribution errors (band depth vs. modified band depth); over-broad mapping erodes precision | Never. Paper-level curation is fine; the callable→paper index must still record the specific variant claim per callable. |
| Leave cross-language `version` field empty at "fix later" | Faster initial authoring | Staleness is undetectable; entries drift without anyone noticing | Never. Pin the version at curation time, even if it requires one lookup. |
| Omit the `"curated": false` signal and return empty dict for uncovered callables | Simpler tool implementation | Consuming agents cannot distinguish "no entry" from "tool error"; coverage is invisible | Never. The explicit signal is required for the LLM-free boundary to be machine-provable. |
| Add `"grounded": true` to LLM-synthesized skill output without structural enforcement | Looks correct in the happy path | LLM overconfidence drops the flag when it "knows" the answer; ground truth is lost | Never. Structural enforcement (MCP tool returns `curated: false` BEFORE LLM synthesis) is required. |
| Add a live DOI resolve check to the default CI path | Catches dead DOIs automatically | Network dependency makes CI flaky; also biases against recently-published papers with propagation lag | Never in CI. Run as an opt-in script before milestone close. |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| DOI resolution in CI | Adding a live DOI resolve check to the default test/build path | Keep the CI gate structural only (`^10\.\d{4,}/` regex); add live resolve as an opt-in script (`scripts/check_doi_liveness.py`) run manually before milestone close, not in CI |
| `importlib.resources` for `_references_map.json` | Using `pkg_resources` or a relative path import | Use `resources.files("fdars") / "_references_map.json"` exactly as `fdars_list_capabilities` uses `_capability_map.json`; ensures the JSON is included in wheel builds |
| Guard-sync frozenset for new references tool | Declaring a separate `_REFERENCES_MODULES` frozenset independent of `_CAPABILITY_MODULES` | Derive the references frozenset from `_CAPABILITY_MODULES` at import time, or enforce a test that asserts the two sets are equal; prevents the two frozensets from diverging silently across future crate-bump milestones |
| Skill hybrid protocol | Mixing curated and synthesized output in the same prose paragraph without structural separation | Structure the skill output so curated entries and synthesized entries are in separate sections with explicit labels; the MCP tool's `"curated": bool` field is the machine-readable gate |

---

## "Looks Done But Isn't" Checklist

- [ ] **Citation author-verification:** Every entry in `_references_map.json` has been verified against the DOI landing page (authors match, year matches, title matches). Do not ship without this step.
- [ ] **Method-variant attribution:** For closely related callables (e.g., `band_depth_1d` vs. `modified_band_depth_1d`), the callable→paper index records the specific paper for each variant, not a shared pointer to the same entry.
- [ ] **MCP tool LLM-free boundary test:** A guard-sync test (analogous to GATE-04's `test_capability_tool_llm_free_boundary`) asserts no `"provider"` / `"model"` keys in the references tool response and that the tool does not import any advisor module.
- [ ] **Coverage fraction stated:** The docs References page and `llms.txt` both state the coverage fraction (`N / 409`), not just "references available."
- [ ] **Uncovered callable signal:** A test calls `fdars_method_references` for a known-absent callable and asserts the response contains `"curated": false` (not an empty dict, not an error).
- [ ] **Cross-language version pinned:** Every cross-language entry has a `version` field recording the package version at curation time.
- [ ] **Structural DOI gate in CI:** The CI build validates all DOIs match the structural pattern; this gate is offline and does not depend on live network access.
- [ ] **Skill ungrounded-path tested:** The SKILL.md walkthrough includes a worked example of the ungrounded fallback path (callable not in the curated map) and the output is visibly labelled as ungrounded.
- [ ] **Three-way mirror complete:** `_REFERENCES_MODULES` frozenset in `server.py`, `_EXPECTED_REFERENCES_MODULES` in the test file, and the JSON key set are equal and updated atomically.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong citation discovered post-ship | MEDIUM | Correct the entry in `_references_map.json`, update the docs build, issue a patch release; the static JSON means corrections propagate to the MCP tool immediately on next install |
| Grounding boundary violated (tool synthesizes) | HIGH | Revert the synthesizing tool handler; regenerate the guard-sync test; the existing GATE-04 pattern makes the fix straightforward but the reputational cost of shipping a "LLM-free" tool that synthesized is high |
| Coverage dishonesty discovered (docs implied completeness) | MEDIUM | Add coverage fraction to docs and `llms.txt`; no code change required; the MCP tool already returns `curated: false` for uncovered callables if the tool was correctly implemented |
| Stale cross-language pointer (function renamed/removed) | LOW | Update the entry in `_references_map.json` and pin the new version; the structural URL gate in CI will not catch renames but the opt-in liveness script will |
| Guard-sync frozenset drift (test fails on new module) | LOW | Update the three-way mirror in one atomic commit exactly as the GATE-04 maintenance note instructs |
| LLM-generated citations shipped without verification | HIGH | Full audit of the curated JSON against DOI landing pages; entries that cannot be verified are moved to an explicit `"unverified"` tier or removed; patch release required |

---

## Pitfall-to-Phase Mapping

| Pitfall | Severity | Prevention Phase | Verification |
|---------|----------|------------------|--------------|
| Wrong citation / method-variant attribution | CRITICAL — milestone-gating | Curation phase: define author-verification workflow before first entry is committed | Blocking human review of citation sample; DOI structural gate in CI |
| MCP tool synthesizes (grounding boundary erosion) | CRITICAL — milestone-gating | MCP tool phase: guard-sync test written in same commit as tool | `test_references_tool_llm_free_boundary` passes; no advisor import in tool handler |
| Ungrounded fallback not flagged in skill | HIGH | Skill extension phase: SKILL.md must include ungrounded-path worked example | Test calls skill for uncovered callable; response has visible `[UNGROUNDED]` label |
| Guard-sync tests going stale | HIGH | MCP tool phase: derive frozenset from `_CAPABILITY_MODULES` or enforce equality test | Future crate-bump milestone: guard-sync test catches missing update |
| Coverage dishonesty | HIGH | Docs surface phase: coverage fraction in docs and `llms.txt` | `mkdocs build --strict`; docs References page contains a coverage fraction statement |
| Cross-language accuracy (fabricated/stale pointers) | MEDIUM | Curation phase: cross-language verification checklist; `version` field required | Sample of cross-language entries manually verified against target package version |
| Scope underestimate / LLM as primary curation path | MEDIUM | Roadmap planning: trial one method family first; set honest coverage target | Authoring-velocity estimate from trial; coverage target stated in phase plan |

---

## Sources

- Codebase: `python/fdars/mcp/server.py` — GATE-04 LLM-free pattern; `_CAPABILITY_MODULES` frozenset; `fdars_list_capabilities` static JSON tool (the direct predecessor pattern for `fdars_method_references`)
- Codebase: `tests/test_guard_sync_version_independent.py` — three-way mirror guard-sync pattern; LLM-free boundary assertion (`test_capability_tool_llm_free_boundary`); COMPAT-03 + GATE-04 reference implementations
- Codebase: `.planning/PROJECT.md` — grounding invariant definition (v2.0); v13.0 milestone goal and hybrid protocol; callable→paper curation unit rationale; GATE-04 as the v13.0 close gate
- Domain knowledge: FDA literature attribution complexity — the López-Pintado & Romo 2009/2011 band-depth/modified-band-depth distinction is a canonical example of variant-attribution risk in this specific domain; the Fraiman-Muniz depth has independent parallel publications that require explicit multi-primary attribution
- Project history: v12.0 GATE-04 implementation (committed `_capability_map.json` via `importlib.resources`, frozenset-gated, three-way guard-sync test in `test_guard_sync_version_independent.py`) — the direct predecessor pattern whose structure v13.0 must replicate for the references tool

---
*Pitfalls research for: Scientific-provenance + cross-language-reference data layer (v13.0)*
*Researched: 2026-09-07*
