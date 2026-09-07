---
phase: 81-curation-paper-registry
plan: "01"
subsystem: references-registry
tags: [bibliography, curation, guard-tests, basis, smoothing, functional-statistics]
dependency_graph:
  requires: []
  provides: [references-map-basis-smoothing, references-map-func-stats, gate05-coverage-emission]
  affects: [python/fdars/_references_map.json, tests/test_guard_sync_version_independent.py]
tech_stack:
  added: []
  patterns: [curated-false-sentinel, sub-method-attribution, callable-index-papers-sync]
key_files:
  created: []
  modified:
    - python/fdars/_references_map.json
    - tests/test_guard_sync_version_independent.py
decisions:
  - "ramsay_silverman_2005 and gervini_2008 set curated:false — DOIs are [CITED]/[ASSUMED] and cannot be landing-page-verified in autonomous session; Phase 84 human review will set curated:true"
  - "nadaraya_watson_1964 curated:false — 1964 Soviet-era journals with no DOIs; both Nadaraya and Watson 1964 authors listed together"
  - "craven_wahba_1979 curated:false — DOI 10.1007/BF01404567 is [ASSUMED], not verified"
  - "Matlab fdaM cross_language entry omitted for ramsay_silverman_2005 — McGill URL (www.psych.mcgill.ca) is not in _ALLOWED_DOMAINS and the entry adds low-confidence value; cleaner to omit than extend allowlist for a low-confidence entry"
  - "_ALLOWED_DOMAINS extended with 9 domains: 6 minimum-set + 3 conditionally-needed for later batches (same-commit rule satisfied)"
metrics:
  duration: "5m 8s"
  completed: "2026-09-07"
  tasks_completed: 3
  tasks_total: 3
  commits: 3
status: complete
actuals:
  tokens: 14500
  tasks: 3
  commits: 3
---

# Phase 81 Plan 01: Curation Tracer — Paper Registry Summary

**One-liner:** End-to-end curation loop established for basis/smoothing + functional-statistics families, with honest N/437 coverage-emission test and 9-domain allowlist extension.

## What Was Built

This plan (the tracer) wired one full path through every layer Phase 81 touches:

1. **`_ALLOWED_DOMAINS` extended (Task 1)** — 9 new publisher and package-doc domains added to the frozenset in `tests/test_guard_sync_version_independent.py`. Six are the minimum set needed for Phase 81 URLs; three are conditionally needed for later batches. All future batches can add JSON without touching the test file.

2. **Coverage-emission guard test added (Task 1)** — `test_references_map_coverage_fraction` (GATE-05) loads both JSON files via `importlib.resources`, computes the denominator as `sum(len(v) for v in cap_data.values())` (never hardcoded), and emits `COVERAGE: N/437` under `pytest -s`. Includes a drift tripwire (`assert denominator == 437`) with a message explaining how to update it when the capability map legitimately grows.

3. **Basis/smoothing family curated (Task 2)** — `eilers_marx_1996` extended from 1 to 7 callables (all P-spline and basis callables); cross_language pointers added (R mgcv, Python scikit-fda); `craven_wahba_1979` added for GCV callables; `nadaraya_watson_1964` added for the N-W kernel smoother.

4. **Functional-statistics family curated (Task 3)** — `ramsay_silverman_2005` added for 11 functional statistics callables (mean, covariance, variance, std, norm, deriv, center, trim_mean, normalize); `gervini_2008` added for 3 geometric median callables.

## Coverage Emitted

```
COVERAGE: 16/437 callables curated (3.7% of fdars callable surface)
```

The numerator is 16 — the 5 seed papers from Phase 80 (10 callables) plus the 6 new callables from the `eilers_marx_1996` extension that carry `curated:true`. The new `ramsay_silverman_2005`, `gervini_2008`, `craven_wahba_1979`, and `nadaraya_watson_1964` entries are all `curated:false` and do not count in the numerator. The denominator is 437, derived at test-time from the live `_capability_map.json`.

## Domains Added to `_ALLOWED_DOMAINS`

| Domain | Purpose |
|---|---|
| `www3.stat.sinica.edu.tw` | Statistica Sinica (Degras 2011, Shen & Faraway 2004) |
| `proceedings.mlr.press` | PMLR (Cuturi & Blondel 2017 soft-DTW) |
| `journals.sagepub.com` | SAGE Journals (Volkmann et al. 2023 multiFAMM) |
| `tslearn.readthedocs.io` | tslearn Python cross-language pointers |
| `fda.readthedocs.io` | scikit-fda Python cross-language pointers |
| `www.sktime.net` | sktime Python cross-language pointer |
| `epubs.siam.org` | SIAM (Agueh & Carlier 2011, conditionally needed) |
| `icml.cc` | ICML alternative URL (conditionally needed) |
| `www.stat.ucdavis.edu` | UC Davis PACE Matlab tool (conditionally needed) |

## Papers: `curated:false` Entries and Reasons

| paper_key | Reason for curated:false |
|---|---|
| `craven_wahba_1979` | DOI `10.1007/BF01404567` is [ASSUMED] — not landing-page-verified this session |
| `nadaraya_watson_1964` | 1964 Soviet-era journals; no DOI exists for these papers |
| `ramsay_silverman_2005` | DOI `10.1007/b98888` is [CITED] but not personally verified on the landing page this session |
| `gervini_2008` | DOI `10.1093/biomet/asn031` is [ASSUMED] — not landing-page-verified this session |

All four will be eligible for `curated:true` promotion at Phase 84 blocking human citation review (GATE-03).

## GATE-05 Status

| Gate | Result |
|---|---|
| A — Internal consistency (`callable_index` ↔ `papers[*].callables`) | PASS |
| B — Cross-file resolution (all keys resolve in `_capability_map.json`) | PASS |
| C — Structural DOI/URL (regex + domain allowlist) | PASS |
| Coverage-emission test | PASS (`COVERAGE: 16/437`) |

Full test run: `9/9 passed` in `tests/test_guard_sync_version_independent.py`.

## Commits

| Task | Commit | Description |
|---|---|---|
| 1 — _ALLOWED_DOMAINS + coverage test | `c5e15b1` | feat(81-01): extend _ALLOWED_DOMAINS + add N/437 coverage-emission guard test |
| 2 — Basis/smoothing family | `1b2de9d` | feat(81-01): curate basis/smoothing family — P-splines, GCV, N-W kernel |
| 3 — Functional-statistics family | `6a64d3d` | feat(81-01): curate functional-statistics family — Ramsay-Silverman 2005 + Gervini 2008 |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Intentional Adjustments (not deviations)

1. **Matlab entry for `ramsay_silverman_2005` omitted** — The research listed a McGill URL (`www.psych.mcgill.ca`) as the Matlab `fdaM` cross-language pointer. Adding that domain to `_ALLOWED_DOMAINS` solely for a `confidence:low` Matlab entry would expand the allowlist with a personal/institutional website susceptible to link rot. Per the schema ("simply omit that language key"), the Matlab entry was omitted. This is correct schema behavior, not a deviation.

2. **`arxiv.org` URL used for `srivastava_et_al_2011` Matlab entry** — The Matlab tool has no standalone docs URL in the allowlist; using the arXiv preprint URL with `confidence:low` avoids adding a GitHub raw URL (prohibited by Pitfall 9 in the schema).

## Self-Check: PASSED

- `_references_map.json` exists: FOUND
- `test_guard_sync_version_independent.py` exists: FOUND
- `81-01-SUMMARY.md` exists: FOUND
- commit `c5e15b1` exists: FOUND
- commit `1b2de9d` exists: FOUND
- commit `6a64d3d` exists: FOUND
