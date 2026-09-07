# Phase 84: Close Gate — Strict Build, Guard-Sync, DOI Gate & Blocking Citation-Accuracy Review - Context

**Gathered:** 2026-09-07
**Status:** Ready for planning
**Mode:** Auto-generated (gate/validation phase — runs existing gates + a BLOCKING human review; autonomous execution STOPS at GATE-03 per standing decision)

<domain>
## Phase Boundary

Prove the whole v13.0 milestone correct and shippable in ONE pass, then hand off the human-gated close. Delivers GATE-01..04:

1. **GATE-01** — whole-site `mkdocs build --strict` green OFFLINE with the new References page rendering and executed fences emitting `FDARS_FENCE_OK`. (~25 min; executes live fdars fences via markdown-exec; needs the compiled extension + `PYTHONPATH=scripts`.)
2. **GATE-02** — all GATE-05 groups (primary A/B + companion C/D + coverage + anti-feature absence) green AND the offline structural DOI/URL gate green; the coverage fraction reported and reviewed.
3. **GATE-03** — a BLOCKING HUMAN citation-accuracy review approved before close: a sample of curated entries verified against DOI landing pages BY A HUMAN (not an LLM) — authors/year/title match, sub-method attribution correct, cross-language pointers resolve. **Autonomous execution STOPS at this gate.**
4. **GATE-04** — grounding invariant + MCP LLM-free boundary intact (full advisor/MCP/guard-sync suite incl. Guard Group 3 green); any REVERSIBLE package-version tick committed; any IRREVERSIBLE publish (tag/PyPI) stays human-gated and is HANDED OFF, not executed autonomously.

</domain>

<decisions>
## Implementation Decisions

### Locked by ROADMAP / STATE decision log
- The whole-site `--strict` build + guard-sync + DOI gate run ONCE here at the close (standing v6.0/v11.0 exec constraint); runs on `main`, `use_worktrees: false`.
- GATE-03 is a BLOCKING HUMAN gate — autonomous execution stops; the human verifies citation accuracy against DOI landing pages personally (this is where the ~48 `curated:false` entries can be promoted to `curated:true` after human sign-off — see the honest-posture note below).
- Irreversible publish (git tag / PyPI) is NEVER executed autonomously — reversible in-repo version tick may be committed; the tag/publish is handed off (per [[pyfda-release-versioning]]: PyPI fires only on semver `vX.Y.Z` tags; package 0.x is decoupled from the milestone number — v12.0 shipped as pkg 0.11.0 / tag v0.11.0).

### Reconciliation carried from Phases 81–83 (honest denominator)
- The real callable denominator is **437** (= 409 public-module callables + 28 `_Fdata` class methods), DERIVED from `_capability_map.json`. The "N/409" in the PROJECT/REQUIREMENTS/ROADMAP text is the public-module count and is the milestone's original estimate. Phase 84 reconciles the requirement/roadmap text to state `N/437 total (409 public + 28 Fdata)` so the shipped coverage (`28/437`) and the docs/tool/llms.txt all agree. This is an editorial reconciliation, not a code change.

### Autonomous vs human split (the stop point)
- **Autonomous (this phase, before the stop):** run GATE-01 (strict build), GATE-02 (guard-sync + DOI + coverage), GATE-04's automated half (full advisor/MCP/guard-sync suite + LLM-free/grounding re-confirm); prepare the GATE-03 citation-review sample; reconcile the 409→437 text; recommend (but do not execute) the version tick.
- **Human (the handoff, after autonomous stops):** GATE-03 citation-accuracy sign-off; approve/commit the reversible version tick if desired; execute any irreversible tag/PyPI publish.

### Claude's Discretion
- The exact GATE-03 sample to present (recommend: ALL 6 current `curated:true` papers — they ship authoritatively — plus a spread of high-value `curated:false` candidates the human may promote).
- Whether to recommend a package-version bump (0.11.0 → 0.12.0) as the reversible tick, presented for user confirmation.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Makefile` `docs` target: `mkdocs build --strict` + `python scripts/check_docs_figures.py site` (fence-error gate). `export PYTHONPATH := scripts`. Needs the compiled `fdars` (maturin develop) — `.venv` has fdars 0.11.0 + mkdocs 1.6.1 + maturin 1.13.1 installed.
- `tests/test_guard_sync_version_independent.py` — all GATE-05 groups (12 tests currently green): primary A/B, companion C/D, coverage, anti-feature absence, structural DOI/URL gate.
- `scripts/check_references_render.py` — the fast references-page validity checker (5/5 incl. sentinel absence).
- `python/fdars/_references_map.json` — 57 papers, 243 callable_index entries, 6 `curated:true` papers (28/437 coverage) — the GATE-03 review target.
- `FDARS_FENCE_OK` sentinel — printed by executed docs fences; `check_docs_figures.py site` gates on figure/fence errors.

### Established Patterns
- Docs build EXECUTES live fdars code (markdown-exec) → requires the extension + PYTHONPATH=scripts; the references page itself is plain markdown (0 exec fences).
- Version is dual-pinned: `pyproject.toml` + `Cargo.toml` both `0.11.0`. A reversible tick edits both; the tag/PyPI is separate + human-gated.

### Integration Points
- The strict build renders `docs/references.md` (nav-wired) alongside the whole existing site; the guard suite + DOI gate + LLM-free boundary all validate the Phase 80–83 outputs together.

</code_context>

<specifics>
## Specific Ideas

- GATE-03 is the ONLY point where `curated:false` entries populated in Phase 81 can be promoted to `curated:true` — the human opens the DOI landing pages and confirms. Present this clearly so the user knows their review both (a) validates the 6 shipped curated entries and (b) can unlock more coverage.
- The full-site strict build is the single expensive gate (~25 min); it re-executes pre-existing fences unrelated to v13.0 (those passed at v12.0 close) plus the new plain-markdown references page.
- Do NOT push a tag or publish to PyPI autonomously.

</specifics>

<deferred>
## Deferred Ideas

- Completing the uncurated N/437 tail + a coverage floor → REF-FUT-01.
- Opt-in live DOI/URL liveness resolve (`FDARS_ONLINE_CHECKS=1`) → REF-FUT-02.
- Milestone lifecycle (audit → complete → cleanup) runs AFTER the human GATE-03 approval, not autonomously.

</deferred>
