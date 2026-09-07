---
phase: 83-docs-llms-txt-skill-extension
plan: "01"
subsystem: docs-emit
tags: [references, llms-txt, provenance, offline-emit, scientific-references]
status: complete

dependency_graph:
  requires: []
  provides:
    - docs/references.md
    - docs/llms.txt (extended with provenance section)
    - scripts/generate_capability_dataset.py --references dispatch
  affects:
    - Phase 83 Plan 02 (mkdocs.yml nav wiring requires docs/references.md)
    - Phase 83 Plan 03 (skill references the provenance docs)
    - Phase 84 (whole-site --strict build gate over docs/references.md)

tech_stack:
  added: []
  patterns:
    - offline-emit: read committed JSON, no fdars import, same pattern as --llmstxt
    - coverage-derivation: mirror server.py:1032-1040 — sum(len(v) for v in cap_data.values()) NEVER hardcoded
    - sentinel-filtering: if paper_key.startswith("_uncurated"): continue in all emit loops

key_files:
  created:
    - docs/references.md
  modified:
    - scripts/generate_capability_dataset.py
    - docs/llms.txt

decisions:
  - Extended _emit_llmstxt with optional ref_data/cap_data args (inline append)
    rather than a separate _extend_llmstxt_provenance function — avoids two-pass
    read-then-modify; backward compat preserved (emit_docs() caller passes no args)
  - --references re-emits the full docs/llms.txt (not just appends) so both
    surfaces stay in sync — clean single-pass write
  - _Fdata group heading is "Fdata Class Methods" (not "fdars._Fdata") for readability
  - Cross-language table/list omitted entirely when paper.cross_language is empty
    (honest gap, not a placeholder row)

metrics:
  duration: "~5 minutes"
  completed: 2026-09-07
  tasks_completed: 3
  tasks_total: 3
  commits: 2

actuals:
  tokens: 18500
  tasks: 3
  commits: 2
---

# Phase 83 Plan 01: Offline References Emitter Summary

Added the `--references` offline emit path to `scripts/generate_capability_dataset.py`, producing a family-grouped `docs/references.md` scientific references page and extending `docs/llms.txt` with a `## Scientific Provenance & Cross-Language Implementations` section — both derived from committed JSON with a `28/437` coverage fraction, no sentinel leakage, and no fdars import.

## What Was Built

### scripts/generate_capability_dataset.py

Five additions to the offline emit toolkit:

1. **`_coverage_counts(ref_data, cap_data) -> tuple[int, int]`** — mirrors `server.py:1032-1040` exactly. Denominator = `sum(len(v) for v in cap_data.values())`. Numerator = callables in `callable_index` backed by at least one `curated:true` paper. No hardcoded values.

2. **`_callable_purpose(callable_key, cap_data) -> str`** — purpose lookup for callable rendering; handles `_Fdata` module prefix.

3. **`_emit_references_page(ref_data, cap_data, repo_root) -> Path`** — writes `docs/references.md`. Family-grouped by primary module (first callable's module prefix). Sentinel papers (`_uncurated*`) filtered. Coverage section states derived fraction. Cross-language tables only when non-empty. Plain Markdown only (no attr_list anchors, no HTML).

4. **`_provenance_section_lines(ref_data, cap_data) -> list[str]`** — builds the `## Scientific Provenance & Cross-Language Implementations` block for `docs/llms.txt`. Curated-only callables. Per-entry format: `` - `module.callable` — Authors (Year) doi:DOI ; R: pkg::fn / Python: pkg.fn ``. Closes with verbatim `grounded: false` note.

5. **`emit_references(repo_root)`** — top-level dispatch function; loads both JSON files, calls `_emit_references_page` then `_emit_llmstxt` (with ref/cap args), prints both written paths.

**`_emit_llmstxt` signature extended** to `(data, repo_root, ref_data=None, cap_data=None)`. When both optional args are provided, `_provenance_section_lines()` is appended before writing. Existing `emit_docs()` caller passes no optional args — output byte-identical.

**`__main__` dispatch** now has `elif "--references" in sys.argv: emit_references(repo_root)` inserted before the `else:` live-introspection branch.

### docs/references.md (new)

Family-grouped scientific references page:
- Intro blockquote + `## Coverage` section: derived `28 of 437` (never hardcoded)
- `## Methods by Module` with H3 per module family (alphabetical)
- `Fdata Class Methods` heading for `_Fdata` group
- H4 per paper (Authors Year — Title), metadata table, callables list with purpose, cross-language table (when non-empty)
- No `_uncurated` sentinel papers

### docs/llms.txt (extended)

Added `## Scientific Provenance & Cross-Language Implementations` section at end:
- Derived `28 of 437` coverage line
- `grounded: false` note (machine-readable per-citation flag for consumers)
- Per-module H3 subsections with curated callables only
- Closing uncurated-count blockquote

## Deviations from Plan

### Auto-noted: Verify Command Scope Issue (Task 3 — not a code fix)

**Found during:** Task 3
**Issue:** The Task 3 verify command `! grep -q "clustering.align_cluster_fd" docs/llms.txt` checks the whole file, but `clustering.align_cluster_fd` legitimately appears in the Full API Reference section (line 150) of `docs/llms.txt` as a normal callable listing. The callable is correctly ABSENT from the provenance section (verified by section-specific check).

**Root cause:** The verify command's grep scope is broader than the `fails_when` clause's actual intent ("leaked into the provenance section"). The requirement is fully met.

**Resolution:** Verified the provenance section specifically — `clustering.align_cluster_fd` is absent from the `## Scientific Provenance` section (confirmed by Python section-scoped check). The plan's honesty property holds. No code change needed — the verify command's grep pattern is a test-scope limitation, not a production bug.

**Evidence:**
```
OK: align_cluster_fd absent from provenance section
OK: fraiman_muniz_1d found in provenance section
OK: grounded flag found in provenance section
```

## 409 → 437 Denominator Correction (for Phase 84 requirement reconciliation)

The DOCS-01 and DOCS-02 requirement text in ROADMAP/REQUIREMENTS.md contains the stale figure "409 callables." The actual `_capability_map.json` denominator is **437** (verified by `sum(len(v) for v in cap_data.values())`).

- All emitted artifacts use the derived `437` figure (never the stale `409`)
- No `437` or `409` literal appears in `scripts/generate_capability_dataset.py` source
- Phase 84 should update the requirement text to replace "409" with the honest derived figure

## Must-Haves Verification

| Truth | Status |
|-------|--------|
| `python ... --references` runs with NO fdars import and exits 0 | PASS — `PYTHONPATH= python scripts/generate_capability_dataset.py --references` exits 0 |
| docs/references.md regenerated with Coverage `28 of 437` (derived) | PASS — grep confirms |
| docs/llms.txt gains `## Scientific Provenance...` section with same `437` denominator | PASS — grep confirms |
| Sentinel papers never appear in either artifact | PASS — `! grep -q "_uncurated" docs/references.md` and `docs/llms.txt` both pass |
| Provenance section carries the `grounded: false` note | PASS — grep confirms |

## Self-Check

### Files exist
- `docs/references.md` — FOUND
- `docs/llms.txt` — FOUND (extended)
- `scripts/generate_capability_dataset.py` — FOUND (modified)

### Commits exist
- `ae95ced` — feat(83-01): add --references offline emitter to generate_capability_dataset.py
- `f19c4f0` — feat(83-01): regenerate docs/references.md + docs/llms.txt with provenance section

## Self-Check: PASSED
