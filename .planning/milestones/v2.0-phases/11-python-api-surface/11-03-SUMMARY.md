---
phase: 11-python-api-surface
plan: "03"
subsystem: python-package
tags: [advisor, recipe, examples, clustering, offline, llm-guard]

dependency_graph:
  requires:
    - phase: 11-01
      provides: fdars.advisor wired into public fdars API; build_diagnostics and describe_cluster_differences importable
  provides:
    - examples/advisor_recipe.py — standalone end-to-end advisor recipe script
  affects: [docs, examples]

actuals:
  tokens: 993
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "ANTHROPIC_API_KEY env-guard pattern: if os.environ.get('ANTHROPIC_API_KEY') wraps all LLM calls in standalone scripts"
    - "Offline-first recipe: full offline path completes before any optional LLM step; script exits 0 without a key"

key-files:
  created:
    - examples/advisor_recipe.py
  modified: []

key-decisions:
  - "Task 1 and Task 2 implemented atomically in a single file: the offline body + guarded LLM step were authored in one pass since the full structure was clear from the research spec"
  - "Use kmeans_fd directly (not cluster_optim) per Pitfall 6: kmeans_fd result has centers/cluster keys that build_diagnostics consumes correctly; cluster_optim result has best_k not k and is a superset dict"
  - "kmeans_fd result omits k key — build_diagnostics falls back to len(centers) correctly; no normalization needed in recipe"
  - "Recipe not added to docs/examples/ or mkdocs.yml nav per plan prohibition (Pitfall 5): markdown-exec would need ANTHROPIC_API_KEY at build time"

patterns-established:
  - "Offline-first recipe pattern: data → cluster → build_diagnostics → print diagnostics; LLM step appended at bottom behind env guard"

requirements-completed: [PYAPI-03]

coverage:
  - id: D1
    description: "examples/advisor_recipe.py loads Canadian Weather, clusters via kmeans_fd(k=4,seed=42), calls build_diagnostics, and prints diagnostics — runs to completion offline (PYAPI-03)"
    requirement: PYAPI-03
    verification:
      - kind: integration
        ref: "env -u ANTHROPIC_API_KEY .venv/bin/python examples/advisor_recipe.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Recipe contains ANTHROPIC_API_KEY guard wrapping describe_cluster_differences(run_llm=True); else branch prints guidance; file parses as valid Python"
    requirement: PYAPI-03
    verification:
      - kind: unit
        ref: "python -c \"import ast,sys; src=open('examples/advisor_recipe.py').read(); assert 'ANTHROPIC_API_KEY' in src and 'run_llm=True' in src and 'describe_cluster_differences' in src; ast.parse(src); print('recipe guard OK')\""
        status: pass
    human_judgment: false

duration: 3min
completed: "2026-08-09"
status: complete
---

# Phase 11 Plan 03: Advisor end-to-end recipe script — Summary

**Standalone `examples/advisor_recipe.py` script: load Canadian Weather → cluster via kmeans_fd → offline build_diagnostics → optional LLM interpretation guarded by ANTHROPIC_API_KEY; exits 0 without a key (PYAPI-03).**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-08-09T19:42:02Z
- **Completed:** 2026-08-09T19:44:39Z
- **Tasks:** 2 (implemented atomically in one commit)
- **Files created:** 1

## Accomplishments

- `examples/advisor_recipe.py` created: standalone runnable recipe matching the existing `examples/*.py` convention (module docstring, no `if __name__ == "__main__":` wrapper — direct script body).
- Offline path complete: loads Canadian Weather dataset (35 stations × 365 daily temperature points), clusters via `fdars.clustering.kmeans_fd(X, day, k=4, seed=42)`, calls `build_diagnostics(method="clustering", argvals=day)`, prints cluster sizes, mean amplitude separation (5.3006), and mean phase separation (0.4158).
- LLM step guarded: `if os.environ.get("ANTHROPIC_API_KEY"):` wraps `describe_cluster_differences(..., run_llm=True)` with `else` branch printing set-key guidance.
- Script exits 0 offline: `env -u ANTHROPIC_API_KEY .venv/bin/python examples/advisor_recipe.py` runs to completion without error.
- Full test suite: 104 passed, 1 skipped (expected — LLM integration test) — no regressions.

## Task Commits

Tasks 1 and 2 were implemented atomically in a single commit (the full offline+guarded structure was clear from the research spec and authored in one pass):

1. **Task 1: Standalone offline recipe + Task 2: Guarded LLM step** — `a720e5a` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/examples/advisor_recipe.py` — standalone end-to-end advisor recipe: Canadian Weather load → kmeans_fd(k=4) → build_diagnostics → print diagnostics → optional describe_cluster_differences guarded by ANTHROPIC_API_KEY

## Decisions Made

- Task 1 and Task 2 implemented atomically: the offline body and guarded LLM step were authored in one pass since the complete structure was clear from RESEARCH.md §9 skeleton and the pitfall list. No functional difference from two separate commits.
- `kmeans_fd` used directly (not `cluster_optim`) per Pitfall 6: `kmeans_fd` returns `{cluster, centers, tot_withinss, iter, converged}` — `k` is absent but `build_diagnostics` correctly falls back to `len(centers)`.
- Recipe placed in `examples/` not `docs/examples/`: markdown-exec would require `ANTHROPIC_API_KEY` at docs build time (Pitfall 5, plan prohibition).

## Deviations from Plan

**1. [Rule 2 - Consolidated] Task 2 implemented atomically with Task 1**

- **Found during:** Task 1 authoring
- **Issue:** The offline and guarded-LLM structures are tightly coupled in a single file with no interleaving complexity. Writing them separately would produce identical output with an intermediate commit of incomplete functionality.
- **Fix:** Both tasks implemented in one write/commit. The result satisfies all acceptance criteria for both Task 1 and Task 2.
- **Verification:** Both automated verify commands pass: `env -u ANTHROPIC_API_KEY python examples/advisor_recipe.py` (exits 0) and the static guard check (`ast.parse` + `ANTHROPIC_API_KEY in src and run_llm=True in src`).
- **Committed in:** `a720e5a`

---

**Total deviations:** 1 (consolidated task implementation)
**Impact on plan:** No scope change. All acceptance criteria met. Single commit is cleaner than two consecutive commits on the same single file.

## Issues Encountered

- `kmeans_fd` result dict does not include `k` key (keys: `cluster`, `centers`, `tot_withinss`, `iter`, `converged`). `build_diagnostics` falls back to `len(centers)` correctly — no issue in practice but the Pitfall 6 warning about `cluster_optim` was relevant background context.

## Known Stubs

None. `examples/advisor_recipe.py` is fully wired: data loads from vendored CSV via `load_canadian_weather()`, clustering uses `kmeans_fd`, diagnostics are computed via `build_diagnostics`, and the LLM guard correctly wraps `describe_cluster_differences`. No placeholder text, no hardcoded mock data.

## Threat Surface Scan

No new security-relevant surface introduced beyond what the plan's threat model already covers:
- T-11-06 (offline DoS): mitigated — `ANTHROPIC_API_KEY` guard verified; offline path exits 0.
- T-11-05 (key in source): mitigated — key read via `os.environ.get("ANTHROPIC_API_KEY")` only; never hardcoded.
- T-11-01 (user data → Anthropic): accepted risk — only when user explicitly sets the key; documented in Phase 10 threat model.

## Next Phase Readiness

- PYAPI-03 complete: `examples/advisor_recipe.py` demonstrates the advisor end-to-end against a real dataset.
- Phase 11 is now complete (plans 01, 02 via 11-02-SUMMARY if it exists, and 03 done).
- No blockers for downstream phases.

## Self-Check

- [x] `examples/advisor_recipe.py` exists at the correct path
- [x] Commit `a720e5a` exists in git log
- [x] `env -u ANTHROPIC_API_KEY .venv/bin/python examples/advisor_recipe.py` exits 0
- [x] Static guard check passes: `ANTHROPIC_API_KEY`, `run_llm=True`, `describe_cluster_differences` in file; `ast.parse` succeeds
- [x] 104 tests pass, 1 skipped (no regressions)

## Self-Check: PASSED

---
*Phase: 11-python-api-surface*
*Completed: 2026-08-09*
