---
phase: 81-curation-paper-registry
plan: "05"
subsystem: references-registry
tags: [bibliography, curation, guard-tests, anti-feature-families, curate-04, curate-05, coverage]
dependency_graph:
  requires: [81-04]
  provides: [references-map-anti-feature-sentinel, references-map-coverage-final, guard-anti-feature-absence]
  affects: [python/fdars/_references_map.json, tests/test_guard_sync_version_independent.py]
tech_stack:
  added: []
  patterns: [absence-as-sentinel, curated-false-sentinel, honest-coverage-emission, curate-05-numerator]
key_files:
  created: []
  modified:
    - python/fdars/_references_map.json
    - tests/test_guard_sync_version_independent.py
decisions:
  - "_uncurated_spm_tail_2026-09 removed entirely — CURATE-04 sentinel is ABSENCE from callable_index, not a curated:false placeholder entry"
  - "22 non-mfpca SPM callable_index entries removed; spm.mfpca retained (Happ & Greven 2018, Pitfall 7)"
  - "explain, metrics, scoring, conformal, seasonal were already absent — no change needed"
  - "depth.functional_depth was already absent — no change needed"
  - "coverage test semantics confirmed correct from 81-01: curated:true numerator only, live-derived denominator (437)"
  - "no _meta key added to _references_map.json (would break GATE-05 A shape check); coverage is test-emitted only"
metrics:
  duration: "~4 minutes"
  completed: "2026-09-07"
  tasks_completed: 2
  tasks_total: 2
  commits: 2
status: complete
actuals:
  tokens: 12000
  tasks: 2
  commits: 2
---

# Phase 81 Plan 05: Anti-Feature Sentinel + Honest Coverage Summary

**One-liner:** Six anti-feature families wired to the absence sentinel in callable_index (CURATE-04); SPM tail placeholder removed; guard test added; coverage finalized at 31/437 (7.1% curated:true, honest per CURATE-05).

## What Was Built

### Task 1: Wire Six Anti-Feature Families to Absence Sentinel + Add Guard

**Reconciliation audit result:**

| Anti-Feature Family | Status Before | Action | Status After |
|---|---|---|---|
| `explain` (46 callables) | Already absent from callable_index | None | Absent (correct) |
| `metrics` (5 callables) | Already absent from callable_index | None | Absent (correct) |
| `scoring` (5 callables) | Already absent from callable_index | None | Absent (correct) |
| `conformal` (7 callables) | Already absent from callable_index | None | Absent (correct) |
| `seasonal` (18 callables) | Already absent from callable_index | None | Absent (correct) |
| `spm.*` EXCEPT `spm.mfpca` (22 callables) | PRESENT via `_uncurated_spm_tail_2026-09` | Removed paper + 22 index entries | Absent (correct) |
| `depth.functional_depth` | Already absent from callable_index | None | Absent (correct) |
| `spm.mfpca` | Present (happ_greven_2018) | None | Present (correct, Pitfall 7) |

**Key finding:** Plans 81-03/81-04 added `_uncurated_spm_tail_2026-09` whose `callables` included all 22 non-mfpca SPM callables, creating 22 corresponding `callable_index` entries. This violated CURATE-04 — the sentinel is ABSENCE from callable_index, not a curated:false paper listing the callables. The fix removes both the paper entry and the 22 callable_index entries.

**New guard test added:** `test_references_map_anti_feature_families_absent` in Guard Group 3 of `tests/test_guard_sync_version_independent.py`:
- Asserts no `explain.*`, `metrics.*`, `scoring.*`, `conformal.*`, `seasonal.*` key in callable_index
- Asserts no `spm.*` key except `spm.mfpca`
- Asserts `depth.functional_depth` is not a key
- On violation: names the offending key, references "CURATE-04 / 81-RESEARCH §2"
- Positive assertion: `spm.mfpca` IS present

**callable_index after Task 1:** 243 entries (was 265 in 81-04 — 22 SPM anti-feature entries removed).

### Task 2: Finalize CURATE-05 Honest Coverage Reporting

The coverage test `test_references_map_coverage_fraction` was already established in 81-01 with the correct semantics. Task 2 verified and annotated:

1. **Numerator logic confirmed correct:** counts ONLY callable_index keys where at least one referenced paper has `curated:true`. Callables backed only by `curated:false` papers do NOT count. Anti-feature families are absent so cannot inflate the numerator.

2. **Denominator confirmed derived:** `sum(len(v) for v in cap_data.values())` from the live `_capability_map.json`. Never hardcoded. Drift tripwire asserts `== 437` (update if capability map legitimately grows).

3. **No `_meta` key added** to `_references_map.json` — would break GATE-05 A's two-key shape assertion (`papers` + `callable_index` only). Coverage is emitted by the guard test only.

4. **CURATE-05 inline comments added** to the test, making the numerator semantics machine-readable:
   - numerator comment: "curated:false entries do NOT count; anti-feature families are absent so cannot inflate the numerator"
   - curated_paper_keys comment: "no LLM-synthesized placeholder ships as curated"

## Final Coverage

```
COVERAGE: 31/437 callables curated (7.1% of fdars callable surface)
```

| Metric | Value |
|---|---|
| Callable denominator | 437 (derived from live `_capability_map.json`) |
| Callables with curated:true attribution | 31 |
| Coverage fraction | 7.1% |
| Total papers | 54 |
| curated:true papers | 6 |
| curated:false papers | 48 |
| callable_index entries | 243 / 437 indexed |

The 7.1% curated:true coverage reflects strict author-verification discipline across phases 81-01 through 81-05. The curated:true entries are those from Phase 80 seeds (fraiman_muniz_2001, lopez_pintado_romo_2009, srivastava_et_al_2011, ramsay_dalzell_1991, eilers_marx_1996) plus `cuturi_blondel_2017` (PMLR page checked via web search in 81-04).

The 57% gap between indexed (243/437 = 55.6%) and curated (31/437 = 7.1%) is intentional and honest — it reflects the difference between "attribution known with CITED confidence" and "attribution author-verified with curated:true confidence." No LLM-synthesized placeholder ships as curated.

## GATE-05 Status

| Gate | Result |
|---|---|
| A — Internal consistency (callable_index ↔ papers[*].callables) | PASS |
| B — Cross-file resolution (all 243 keys resolve in _capability_map.json) | PASS |
| C — Structural DOI/URL gate | PASS |
| Coverage-emission test (CURATE-05) | PASS (31/437 emitted) |
| Anti-feature-absence guard (CURATE-04) | PASS |

Full test run: `10/10 passed` in `tests/test_guard_sync_version_independent.py`.

## Deviations from Plan

### Auto-fixed Issues

**[Rule 2 - Missing Critical Functionality] `_uncurated_spm_tail_2026-09` violated CURATE-04 sentinel contract**
- **Found during:** Task 1 reconciliation audit
- **Issue:** Plans 81-04 added `_uncurated_spm_tail_2026-09` with 22 SPM callables in `callables` list, creating 22 corresponding entries in `callable_index`. CURATE-04 requires ABSENCE from callable_index as the sentinel — a curated:false entry that lists callables PLACES those callables in callable_index, which is the wrong sentinel path.
- **Fix:** Removed `_uncurated_spm_tail_2026-09` paper entirely and removed all 22 `spm.*` callable_index entries. `spm.mfpca` retained (happ_greven_2018, curated:false).
- **Files modified:** `python/fdars/_references_map.json`
- **Commit:** c180b45

## Known Stubs

None — this plan adds only guard tests and removes JSON data; no rendered UI stubs.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. This plan is data and test edits only.

## Self-Check: PASSED

- `_references_map.json` exists: FOUND at `/home/simonm/projects/rust/pyfda/python/fdars/_references_map.json`
- commit `c180b45` (Task 1 — anti-feature sentinel) exists: FOUND
- commit `0a1db81` (Task 2 — CURATE-05 annotations) exists: FOUND
- GATE-05: 10/10 tests pass
- Anti-feature families absent from callable_index: PASS
- spm.mfpca in callable_index: PASS
- Coverage: 31/437 (7.1% curated:true)
- CURATE-04 requirement: SATISFIED
- CURATE-05 requirement: SATISFIED

## Commits

| Task | Commit | Description |
|---|---|---|
| 1 — Anti-feature sentinel + guard | `c180b45` | feat(81-05): wire six anti-feature families to absence sentinel + add guard |
| 2 — CURATE-05 coverage annotations | `0a1db81` | feat(81-05): finalize CURATE-05 honest coverage reporting with inline annotations |
