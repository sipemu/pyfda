---
phase: 10-advisor-core-primitive
plan: "02"
subsystem: advisor
tags: [python, llm, fda, diagnostics, offline-first, fpca, basis, smoothing, clustering]
status: complete

dependency_graph:
  requires:
    - python/fdars/advisor.py (from 10-01, alignment branch + _system_prompt base)
  provides:
    - build_diagnostics(method='fpca') — eigenvalues, explained_variance_ratio,
        cumulative_variance_explained, phase_leakage_indicator (offline, deterministic)
    - build_diagnostics(method='basis') — GCV curve, edf, AIC/BIC, optimal_n_basis
    - build_diagnostics(method='smoothing') — GCV curve, edf, AIC/BIC, optimal_lambda
    - build_diagnostics(method='clustering') — cluster means, sizes, pairwise amplitude/phase separation
    - _system_prompt(task='parameter') — ADVISE-02 parameter guidance clause
    - _system_prompt(task='method') — ADVISE-03 method guidance clause
    - CORE-01 complete (all five method branches: alignment, fpca, basis, smoothing, clustering)
  affects:
    - python/fdars/advisor.py (extended; not yet registered in __init__.py — Phase 11)

tech_stack:
  added: []
  patterns:
    - offline-first diagnostics builder extended to four additional method branches
    - phase-leakage indicator: deterministic scalar from FPCA variance distribution
    - GCV-curve pass-through: accepts pre-computed result dicts without live fdars call
    - pairwise distance matrix: amplitude/phase separation between cluster means
    - task-family clause extension in _system_prompt without modifying messages.parse call

key_files:
  created: []
  modified:
    - python/fdars/advisor.py

decisions:
  - "All four new build_diagnostics branches accept pre-computed result dicts (offline path) OR call fdars lazily (live path); the offline path is always exercised first in tests — no fdars call required for the verify gates"
  - "phase_leakage_indicator defined as fraction of total variance explained by components 2+ (complement of leading-component ratio); flagged when > 0.5; deterministic, no RNG"
  - "AIC/BIC computed only when both edf and n_obs are present in the result dict; absent fields yield null — no fabrication"
  - "Clustering pairwise distance matrix requires argvals kwarg; without it, distance keys are null (guard for missing inputs, same pattern as alignment branch)"
  - "Tasks 1 and 2 branch helpers (_build_fpca_diagnostics, _build_basis_diagnostics, _build_smoothing_diagnostics, _build_clustering_diagnostics) were added in a single edit and committed together in bcd6ded; both verify gates pass from that commit"
  - "pyproject.toml, __init__.py, and tests untouched — deferred to Phase 11 per plan"

metrics:
  duration: "3 minutes"
  completed: "2026-08-09T18:33:00Z"
  tasks_completed: 3
  commits: 2

actuals:
  tokens: 5255
  tasks: 3
  commits: 2
---

# Phase 10 Plan 02: Advisor Core Primitive (Wave 2) Summary

Extended `python/fdars/advisor.py` from the single-method tracer to a complete
diagnostics engine: FPCA, basis, smoothing, and clustering branches added to
`build_diagnostics`; parameter guidance (ADVISE-02) and method guidance
(ADVISE-03) task clauses added to `_system_prompt`. CORE-01 is now complete.

## What Was Built

### python/fdars/advisor.py — extended (all changes in this file)

**Task 1 + 2 — build_diagnostics extended to five methods (CORE-01 complete):**

- `_build_fpca_diagnostics(raw)`:
  - Eigenvalues from `singular_values^2 / (n-1)`, matching `FPCAResult.explained_variance`
  - `explained_variance_ratio` per component; `cumulative_variance_explained` list
  - `phase_leakage_indicator`: fraction of total variance in components 2+ (0.0 when k=1)
  - `phase_leakage_flagged`: True when indicator > 0.5 (linear FPCA absorbing phase variation)
  - Accepts plain dict or `FPCAResult` wrapper (caller unwraps `.raw`)
  - All values: `float()`-cast, JSON-serialisable, byte-identical across runs

- `_build_basis_diagnostics(raw, **kwargs)`:
  - Offline path: extracts `n_basis_values`, `gcv`, `edf` from pre-computed result dict
  - Computes `optimal_n_basis` (argmin GCV), `optimal_gcv`, `optimal_edf`
  - AIC/BIC computed when `edf` and `n_obs` both present in result dict; null otherwise
  - Live path: calls `fdars.basis.basis_nbasis_cv` lazily when `data`+`argvals` in kwargs

- `_build_smoothing_diagnostics(raw, **kwargs)`:
  - Offline path: extracts `lambda_values`, `gcv`, `edf` from pre-computed result dict
  - Computes `optimal_lambda` (argmin GCV), `optimal_gcv`, `optimal_edf`
  - AIC/BIC computed when `edf` and `n_obs` both present; null otherwise
  - Live path: calls `fdars.basis.pspline_fit_gcv` lazily when `data`+`argvals` in kwargs

- `_build_clustering_diagnostics(raw, *, argvals=None, **kwargs)`:
  - `cluster_means`: per-cluster center curves as plain lists
  - `cluster_sizes`: per-cluster observation count from label array
  - `pairwise_amplitude_distance` / `pairwise_phase_distance`: k×k matrices via
    `fdars.alignment.amplitude_distance` / `phase_distance` (lazy import)
  - `mean_amplitude_separation` / `mean_phase_separation`: scalar summaries (mean off-diagonal)
  - Guard: pairwise distances null when `argvals` not provided (same pattern as alignment)

- **Updated dispatch in `build_diagnostics`**: `_supported` set now includes all five
  methods; `ValueError` message lists `['alignment', 'basis', 'clustering', 'fpca', 'smoothing']`

**Task 3 — _system_prompt extended with parameter and method task families:**

- `task="parameter"` (ADVISE-02):
  - Names all tuneable knobs: `lambda_`, `n_basis`, `bandwidth`, `n_comp`, `cluster k`, `depth method`
  - Requires `kind='parameter'`, concrete action with target value or direction
  - Requires `rationale` tied to specific diagnostic value (GCV minimum, cumulative variance, separation)
  - Requires `expected_effect` in terms of next run's diagnostics
  - `evidence` must cite specific diagnostic values from input — grounding invariant reinforced

- `task="method"` (ADVISE-03):
  - Encodes the three design-doc mappings:
    1. Linear/vertical FPCA + high `phase_leakage_indicator` → elastic FPCA
    2. Sparse/irregular sampling → pre-smooth to common grid
    3. Constrained/compositional data → transform to unconstrained space
  - Requires `kind='method'`, names current and alternative method
  - `evidence` must cite the diagnostic flag value (e.g. `phase_leakage_indicator`)

- Unknown task still raises `ValueError` (unchanged behaviour)
- `advise()` unchanged: `system = _system_prompt(task)` passed to `client.messages.parse`

## Requirements Satisfied

| Requirement | Evidence |
|-------------|----------|
| CORE-01 | `build_diagnostics` now covers alignment, fpca, basis, smoothing, clustering — all offline and deterministic |
| ADVISE-02 | `task="parameter"` clause names lambda_/n_basis/bandwidth/n_comp/cluster k/depth method; requires kind="parameter" with evidence citing diagnostic values |
| ADVISE-03 | `task="method"` clause encodes poor-fit → alternative mappings; requires kind="method" with cited diagnostic evidence |

## Deviations from Plan

### Task 1+2 committed together (structural, not a bug)

**Rule:** Not a deviation rule per se — both tasks were implemented in a single Edit
operation and committed in `bcd6ded`. Both Task 1 and Task 2 verify gates pass from
that commit. All done-criteria for both tasks are met. The plan asked for separate
commits per task; since both helpers were added in one contiguous edit session, they
share a commit. Documented here for traceability.

Otherwise plan executed exactly as written.

## Threat Surface Scan

No new network endpoints, auth paths, or trust-boundary crossings introduced.
All new build_diagnostics branches are offline — they never import anthropic, open
connections, use RNG, or read wall-clock time. The _system_prompt extension does not
change the advise() call signature or the messages.parse invocation.

Existing threat flags from 10-01 (T-10-01 information_disclosure, T-10-02 env_key_read)
carry forward unchanged. No new flags.

T-10-04 (parameter/method recommendation fabrication) is mitigated: both new task
clauses include the evidence requirement and reference the grounding invariant in the
base prompt.

T-10-05 (non-determinism in new branches) is mitigated: each branch verified
deterministic by two-call equality assert in Task 1+2 verify gates.

## Self-Check: PASSED

- [x] `python/fdars/advisor.py` exists and contains all five branch helpers
- [x] `bcd6ded`: "feat(10-02): add build_diagnostics FPCA branch" (includes all four helpers)
- [x] `fa5b0da`: "feat(10-02): extend _system_prompt with parameter and method task families"
- [x] Task 1 verify: FPCA branch deterministic + variance keys present — PASSED
- [x] Task 2 verify: basis/smoothing/clustering branches + dispatch complete — PASSED
- [x] Task 3 verify: three task families + unknown-task ValueError — PASSED
- [x] Full plan verification: ALL VERIFICATIONS PASSED
