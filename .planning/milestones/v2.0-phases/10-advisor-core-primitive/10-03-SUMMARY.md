---
phase: 10-advisor-core-primitive
plan: "03"
subsystem: advisor
tags: [python, llm, fda, diagnostics, clustering, offline-first, specialization]
status: complete

dependency_graph:
  requires:
    - python/fdars/advisor.py (from 10-01 + 10-02: all five build_diagnostics branches + advise + three task families)
  provides:
    - describe_cluster_differences — Stage 1 (offline clustering feature report via build_diagnostics) + Stage 2 (grounded LLM interpretation via advise)
    - CORE-05 complete: cluster-difference specialization is a build_diagnostics specialization, not a reimplementation
    - Phase 10 core surface complete: build_diagnostics + advise + describe_cluster_differences + Advice/Recommendation
  affects:
    - python/fdars/advisor.py (describe_cluster_differences added; __all__ updated)

tech_stack:
  added: []
  patterns:
    - specialization-on-diagnostics-builder: describe_cluster_differences calls build_diagnostics(method='clustering') internally, then advise(task='interpretation') — the pattern all later surfaces follow
    - offline escape hatch: run_llm=False returns the raw diagnostics dict; run_llm=True (default) calls advise

key_files:
  created: []
  modified:
    - python/fdars/advisor.py

decisions:
  - "describe_cluster_differences is a thin two-line body: build_diagnostics call + conditional advise call; no reimplementation of clustering diagnostics"
  - "run_llm=False offline path returns the raw diagnostics dict directly (no anthropic import); satisfies CI-without-key requirement"
  - "run_llm=True passes task='interpretation' to advise — inheriting the interpretation clause from _system_prompt (grounding invariant applies)"
  - "__all__ updated to exactly {build_diagnostics, advise, describe_cluster_differences, Advice, Recommendation}"
  - "Task 2 self-consistency pass required zero code changes — all five build_diagnostics branches were already deterministic and the ImportError guard was already in place from 10-01/10-02"

metrics:
  duration: "2 minutes"
  completed: "2026-08-09T18:43:59Z"
  tasks_completed: 2
  commits: 1

actuals:
  tokens: 1800
  tasks: 2
  commits: 1
---

# Phase 10 Plan 03: Advisor Core Primitive (Wave 3) Summary

Added `describe_cluster_differences` to `python/fdars/advisor.py` as the
cluster-difference specialization built on `build_diagnostics(method="clustering")`
plus `advise`. Closes Phase 10 and satisfies CORE-05.

## What Was Built

### python/fdars/advisor.py — describe_cluster_differences added

**Task 1 — describe_cluster_differences specialization (CORE-05):**

- `describe_cluster_differences(result, *, argvals=None, domain_context="", model="claude-opus-4-8", run_llm=True, **kwargs)`:
  - **Stage 1 (offline, deterministic):** calls `build_diagnostics(result, method="clustering", argvals=argvals, **kwargs)` to produce the cluster feature report (per-cluster Karcher means, pairwise amplitude/phase distance, cluster sizes, scalar separation summaries)
  - **Stage 2 (LLM, optional):** when `run_llm=True` (default), passes the feature report to `advise(task="interpretation", domain_context=domain_context, model=model)` and returns the schema-validated `Advice` object
  - **Offline escape hatch:** `run_llm=False` returns the raw clustering diagnostics dict; no anthropic import, no network call — fully exercisable in CI without an API key
  - `__all__` updated to include `describe_cluster_differences` (exact set: `{build_diagnostics, advise, describe_cluster_differences, Advice, Recommendation}`)
  - Full NumPy-style docstring documents both paths, notes the specialization pattern, and includes an offline `>>>` example

**Task 2 — Phase 10 surface self-consistency pass:**

- All five `build_diagnostics` method branches verified deterministic (two-call equality) for: `alignment`, `fpca`, `basis`, `smoothing`, `clustering`
- All five method outputs are JSON-serialisable
- `advise` and `describe_cluster_differences` both raise `ImportError` naming `pip install fdars[advisor]` when `anthropic` is absent
- Grounding invariant text and install hint present
- Zero code changes required — implementation was already consistent from 10-01 + 10-02

## Requirements Satisfied

| Requirement | Evidence |
|-------------|----------|
| CORE-05 | `describe_cluster_differences` calls `build_diagnostics(method='clustering')` internally (static AST check + runtime verify pass); exported in `__all__` |

## Phase 10 Core Surface — Complete

| Export | Role | Offline? |
|--------|------|---------|
| `build_diagnostics` | Deterministic feature report for all 5 methods | Yes (fully offline) |
| `advise` | Grounded LLM interpretation — schema-validated `Advice` | No (requires anthropic) |
| `describe_cluster_differences` | Cluster-difference specialization (Stage 1 + Stage 2) | Stage 1 yes; Stage 2 requires anthropic |
| `Advice` | Schema-validated advice container | Yes (pydantic or fallback) |
| `Recommendation` | Schema-validated recommendation | Yes (pydantic or fallback) |

## Deviations from Plan

**Task 2 required zero code changes** — this is expected. The Task 2 action says "adjusting the module only if a gap is found"; no gap was found. The full surface was consistent from 10-01 + 10-02's implementation. Documented here for traceability.

Otherwise plan executed exactly as written.

## Threat Surface Scan

No new network endpoints, auth paths, or trust-boundary crossings introduced.

`describe_cluster_differences` with `run_llm=False` is fully offline — never imports `anthropic`, no network, no RNG, no wall-clock.

With `run_llm=True`, `describe_cluster_differences` calls `advise`, which is the existing trust boundary (Python process -> Anthropic API). This boundary was already present in 10-01 and is covered by T-10-01 (information disclosure) and T-10-02 (env key read).

T-10-06 (tampering / fabricated numbers in cluster-difference interpretation): mitigated — `describe_cluster_differences` passes the feature report to `advise(task="interpretation")`, so the grounding invariant (evidence cites diagnostic values; no fabricated numbers) applies unchanged from the base `advise` implementation.

T-10-07 (information disclosure in advise call): offline by default up to `advise`; `run_llm=False` fully avoids the network.

No new threat flags.

## Self-Check: PASSED

- [x] `python/fdars/advisor.py` contains `describe_cluster_differences`
- [x] `f39aece`: "feat(10-03): add describe_cluster_differences cluster-difference specialization"
- [x] Task 1 verify: `describe_cluster_differences` exported; offline path returns `{"method": "clustering", ...}`; AST check confirms `build_diagnostics` call — PASSED
- [x] Task 2 verify: `__all__` exact; all five methods deterministic; ImportError-guarded (anthropic absent) — PASSED
- [x] No accidental file deletions in commit
- [x] `config.json`, `.gsd/`, `examples/`, `partial_prediction_demo.png` untouched
