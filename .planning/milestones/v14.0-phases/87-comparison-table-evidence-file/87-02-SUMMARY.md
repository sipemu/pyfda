---
phase: 87-comparison-table-evidence-file
plan: "02"
subsystem: paper
tags: [comparison-table, grounding, ci-gate, traceability, capability-map]
status: complete

dependency_graph:
  requires:
    - 87-01 (check_comparison.py SC-3 gate, comparison_table.tex, comparison_evidence.md)
    - 86-02 (paper.yml offline gate pattern)
  provides:
    - paper/code/check_comparison.py (extended: SC-3 peer-traceability + COMP-02 fdars-grounding)
    - Makefile paper-check (check_comparison.py wired as third gate)
    - .github/workflows/paper.yml (check_comparison.py step before Setup tectonic)
  affects:
    - paper.yml CI pipeline (new failing gate before tectonic PDF compile)
    - make paper-check (new local gate)

tech_stack:
  added: []
  patterns:
    - DIMENSION_SUBMODULES hard-coded mapping: 14 normalized labels → _capability_map.json submodule key tuples
    - Capability map grounding: submodule key exists AND has ≥1 public (non-underscore) callable
    - Offline stdlib-only gate before tectonic (Phase 86 pattern applied to COMP-02)
    - Negative-test mutation + restore in verify: empty fts dict → GROUNDING_GATE_FIRES → \cp restore

key_files:
  created: []
  modified:
    - paper/code/check_comparison.py (DIMENSION_SUBMODULES, _load_cap_map, _check_fdars_grounding, main updated)
    - Makefile (paper-check recipe extended with check_comparison.py)
    - .github/workflows/paper.yml (new step after gen_refs_bib, before Setup tectonic)

decisions:
  - "DIMENSION_SUBMODULES transcribed from RESEARCH.md §fdars Column Derivation verbatim — 14 dimension labels exactly as parsed by _parse_table() (Frechet not Fréchet, because _norm() strips LaTeX accents)"
  - "Grounding check counts non-underscore keys in submodule dict (not list items) — _capability_map.json stores submodule as {callable_name: metadata} dict"
  - "check_comparison.py added to paper-check recipe only, not to paper: generation target (it is a gate, not a generator)"
  - "paper.yml step placed after gen_refs_bib and before Setup tectonic, stdlib-only, no maturin — matches Phase 86 offline gate pattern"

metrics:
  duration: "~5 minutes"
  completed: "2026-09-08"
  tasks_completed: 2
  tasks_total: 2
  commits: 2

actuals:
  tokens: 4500
  tasks: 2
  commits: 2
---

# Phase 87 Plan 02: Comparison Table + Evidence File (Wave 2) Summary

COMP-02 fdars-column grounding and SC-3 traceability wired into CI: `check_comparison.py` now machine-asserts every fdars ✓ cell has a backing submodule with ≥1 public callable in `_capability_map.json`, before the tectonic PDF compile.

## What Was Built

**Task 1 — fdars-column grounding assertion in check_comparison.py (COMPARISON_TRACE_OK + GROUNDING_GATE_FIRES)**

Extended `paper/code/check_comparison.py` (stdlib-only, no fdars import) with two additions:

1. **`DIMENSION_SUBMODULES` mapping** — 14 normalized dimension-label strings (matching `_parse_table()` output after `_norm()` strips LaTeX accents) mapped to tuples of `_capability_map.json` submodule keys, transcribed verbatim from RESEARCH.md §fdars Column Derivation:
   - `"Representation / basis smoothing"` → `("basis", "represent", "smoothing")`
   - `"Registration / alignment"` → `("alignment",)`
   - ... (all 14 dimensions)
   - `"Grounded advisor + scientific provenance"` → `("explain",)`

2. **`_load_cap_map()` + `_check_fdars_grounding()`** — loads `_capability_map.json` (dict of submodule → callable-name dict), iterates 14 rows, asserts (a) fdars cell is `\checkmark` (else `FDARS_NOT_CHECK`), and (b) at least one backing submodule has ≥1 public callable (else `UNGROUNDED`). Public = non-underscore key in the submodule dict.

3. **`main()` updated** — runs SC-3 peer-traceability + COMP-02 grounding checks; prints all failures to stderr; `COMPARISON_TRACE_OK` only when both gates pass.

Verify:
- Positive: `python paper/code/check_comparison.py` → `COMPARISON_TRACE_OK` ✓
- Negative: empty `fts` dict in map → `UNGROUNDED: Functional time series (submodules=('fts',))` → `GROUNDING_GATE_FIRES` ✓; map restored byte-for-byte via `\cp` (bypassing German locale alias) ✓

**Task 2 — Wire check_comparison.py into make paper-check and paper.yml (WIRED_OK)**

- **Makefile `paper-check`:** added `PYTHONPATH=$(PAPER_PYTHONPATH) python paper/code/check_comparison.py` as the third recipe line (after `assert_coverage --check` and `gen_refs_bib --check`). The `paper:` generation target is unchanged.
- **`.github/workflows/paper.yml`:** added step `"Check comparison traceability + fdars grounding (COMP)"` running `python paper/code/check_comparison.py`, placed after `Regenerate refs.bib (PIPE-04)` and before `Setup tectonic`. No maturin install added; step-order verified by `awk` gate.

Full `WIRED_OK` verify passed:
- `check_comparison.py` present in paper-check recipe ✓
- `check_comparison.py` absent from `paper:` generation target ✓
- `paper.yml` is valid YAML ✓
- `check_comparison.py` step after `gen_refs_bib.py` steps and before `Setup tectonic` ✓
- No maturin in paper.yml ✓

## Deviations from Plan

**1. [Rule 1 - Bug] Capability map values are dicts not lists**
- **Found during:** Task 1 implementation
- **Issue:** Initial draft used `sum(1 for c in callables if isinstance(c, dict) and not c.get("name", "_").startswith("_"))` assuming a list-of-dicts structure, but `_capability_map.json` stores each submodule as `{callable_name: {purpose: ..., sig: ...}}` (dict keyed by callable name)
- **Fix:** Changed public callable count to `sum(1 for k in mod_entry if not k.startswith("_"))` for dict entries, with defensive list fallback
- **Files modified:** paper/code/check_comparison.py
- **Commit:** 54eb6bc (inline fix before commit)

## Known Stubs

None.

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes. `check_comparison.py` remains stdlib-only, reads only local files. CI step adds no new network access (no pip install). No threat flags.

## Self-Check: PASSED

All modified files confirmed on disk:
- FOUND: paper/code/check_comparison.py (extended)
- FOUND: Makefile (paper-check recipe extended)
- FOUND: .github/workflows/paper.yml (new offline step)

All commits confirmed in git log:
- FOUND: 54eb6bc (feat(87-02): extend check_comparison.py with fdars-column grounding assertion)
- FOUND: 1408339 (feat(87-02): wire check_comparison.py into make paper-check and paper.yml)
