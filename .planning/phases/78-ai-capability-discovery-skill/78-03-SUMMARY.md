---
phase: 78-ai-capability-discovery-skill
plan: "03"
subsystem: docs
tags: [llms.txt, mkdocs, capability-map, docs-emit, ai-discovery]

requires:
  - phase: 78-01
    provides: committed python/fdars/_capability_map.json (the source the docs digest reads from)

provides:
  - docs/llms.txt — llms.txt-convention whole-library API digest (30 modules, 409 callables), static, committed, served at /pyfda/llms.txt
  - docs/ai-capability-map.md — human-readable in-nav digest page (per-module tables), wired into mkdocs.yml
  - mkdocs.yml — AI Capability Map top-level nav entry
  - scripts/generate_capability_dataset.py — extended with --llmstxt docs-emit path (reads committed JSON, no fdars import required)

affects:
  - 78-04 (MCP capability tool also consumes _capability_map.json)
  - 79 (close gate; whole-site --strict build verifies static passthrough of llms.txt)

actuals:
  tokens: 39066
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Offline docs generation: emit deterministic docs artifacts from committed JSON (no fdars import at build time)"
    - "llms.txt convention: H1 title + blockquote + ## Core Modules + ## Full API Reference per module"
    - "MkDocs static passthrough: docs/llms.txt → site/llms.txt (non-Markdown files copied verbatim)"

key-files:
  created:
    - docs/llms.txt
    - docs/ai-capability-map.md
  modified:
    - scripts/generate_capability_dataset.py
    - mkdocs.yml

key-decisions:
  - "docs-emit path reads committed _capability_map.json (not live fdars); no fdars import required — docs build stays independent of compiled extension"
  - "fdars import made lazy inside generate_capability_dataset() and _build_fdata_entry() so --llmstxt path runs without fdars installed"
  - "AI Capability Map placed as a top-level nav entry adjacent to AI Advisor — simplest placement per plan guidance"
  - "llms.txt gets no nav entry (static passthrough, served raw); only ai-capability-map.md is in nav"

patterns-established:
  - "Offline doc generation pattern: --flag reads committed artifact → emits docs → determinism via sorted iteration → re-run produces no git diff"

requirements-completed:
  - SKILL-03

coverage:
  - id: D1
    description: "docs/llms.txt generated from committed capability map, follows llms.txt convention (H1, blockquote, ## Core Modules, ## Full API Reference), lists all 30 modules, 409 callables"
    requirement: SKILL-03
    verification:
      - kind: automated_ui
        ref: "python -c assert txt.startswith('#'); assert re.search(r'^>'); assert all modules present"
        status: pass
      - kind: unit
        ref: "python scripts/generate_capability_dataset.py --llmstxt && git diff --quiet docs/llms.txt docs/ai-capability-map.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/ai-capability-map.md valid Markdown with module index table and per-module function tables, non-empty, no unclosed code fences"
    requirement: SKILL-03
    verification:
      - kind: automated_ui
        ref: "python -c assert md.strip(); assert md.count('```')%2==0"
        status: pass
    human_judgment: false
  - id: D3
    description: "mkdocs.yml nav references ai-capability-map.md exactly once; no nav entry for llms.txt; YAML parses valid"
    requirement: SKILL-03
    verification:
      - kind: automated_ui
        ref: "yaml.load(mkdocs.yml); raw.count('ai-capability-map.md')==1; 'llms.txt' not in nav"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both docs artifacts regenerate deterministically from committed JSON — re-running --llmstxt produces no git diff"
    requirement: SKILL-03
    verification:
      - kind: unit
        ref: "python scripts/generate_capability_dataset.py --llmstxt && git diff --quiet -- docs/llms.txt docs/ai-capability-map.md"
        status: pass
    human_judgment: false

duration: 4min
completed: "2026-09-06"
status: complete
---

# Phase 78 Plan 03: SKILL-03 llms.txt Digest + In-Nav Human Page Summary

**llms.txt whole-library API digest (30 modules, 409 callables) and human-readable capability page generated offline from committed JSON and wired into mkdocs.yml nav**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-06T19:18:06Z
- **Completed:** 2026-09-06T19:22:xx Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Extended `scripts/generate_capability_dataset.py` with a `--llmstxt` docs-emit path that reads the committed `python/fdars/_capability_map.json` (offline; no `fdars` import required in docs-build environments)
- Generated and committed `docs/llms.txt` — llms.txt-convention machine-readable digest: H1 title, blockquote summary, `## Core Modules` bullet list with per-module summaries and reference-docs links, `## Full API Reference` with per-module sections (`module.fn(sig) — purpose`, curated `when` notes where present)
- Generated and committed `docs/ai-capability-map.md` — human-readable in-nav MkDocs page: module index table (30 rows) and per-module function tables (signature + purpose); references `llms.txt` for the machine-readable form
- Added a top-level `AI Capability Map: ai-capability-map.md` nav entry to `mkdocs.yml` adjacent to the AI Advisor section
- All 3 verification gates passed: deterministic regen (no git diff on re-run), llms.txt convention compliance + module completeness, mkdocs.yml YAML validity + nav wiring

## Task Commits

1. **Task 1: Extend the generator to emit docs/llms.txt + docs/ai-capability-map.md** - `6b19fc7` (feat)
2. **Task 2: Wire the human capability page into mkdocs.yml nav** - `da94fb8` (feat)

## Files Created/Modified

- `docs/llms.txt` — llms.txt-convention machine-readable digest (62 KB); served as static passthrough at `/pyfda/llms.txt`
- `docs/ai-capability-map.md` — human-readable MkDocs page (64 KB); rendered at `/pyfda/ai-capability-map/`
- `scripts/generate_capability_dataset.py` — extended with `--llmstxt` flag, `emit_docs()`, `_emit_llmstxt()`, `_emit_ai_capability_map()` functions; `fdars` import made lazy so the docs-emit path works without a live fdars install
- `mkdocs.yml` — one top-level nav entry added: `AI Capability Map: ai-capability-map.md`

## Decisions Made

- **Lazy fdars import:** Moved `import fdars` inside `generate_capability_dataset()` and `_build_fdata_entry()` (two `# noqa: PLC0415` lazy imports) so `--llmstxt` path can run in docs-build environments where the compiled extension is absent. This satisfies the T-78-06 threat mitigation (docs build never imports fdars).
- **Nav placement:** Added `AI Capability Map` as a standalone top-level nav entry immediately after `AI Advisor` — the plan stated "a dedicated top-level entry is acceptable and simplest", and this placement reads naturally alongside the other AI-capability-related sections.
- **Module summaries:** Added a `_MODULE_SUMMARIES` dict in the generator (not in the JSON) to provide human-readable one-liners for each module in both llms.txt and the human page — this data belongs in the emit layer, not the capability map itself.
- **Reference page URLs:** Added `_MODULE_REF_PAGES` dict mapping modules with dedicated reference pages (17 of 30) to their correct docs URLs; remainder fall back to `reference/index.md`.

## Deviations from Plan

None — plan executed exactly as written. Both tasks completed in sequence with all verification gates passing.

## Threat Surface Scan

No new network endpoints, auth paths, or trust-boundary schema changes introduced. `docs/llms.txt` contains only public API signatures already in `python/fdars/_capability_map.json` (already public); no secrets. T-78-06 mitigated: docs build does not import fdars (offline emit from committed JSON). T-78-07 accepted (public surface).

## Known Stubs

None — both docs files are fully populated from the committed capability map (30 modules, 409 callables).

## Issues Encountered

None.

## Next Phase Readiness

- SKILL-03 complete: `docs/llms.txt` and `docs/ai-capability-map.md` are committed and stable.
- Phase 79 (close gate): `mkdocs build --strict` will verify static passthrough (site/llms.txt) — this is the deferred whole-site build gate.
- 78-04 (MCP capability tool): also reads `_capability_map.json`; no changes required to the map itself.

---
*Phase: 78-ai-capability-discovery-skill*
*Completed: 2026-09-06*

## Self-Check: PASSED
