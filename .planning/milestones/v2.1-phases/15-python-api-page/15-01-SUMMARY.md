---
phase: 15-python-api-page
plan: "01"
subsystem: docs/advisor
tags: [documentation, advisor, python-api, exec-fence, mkdocs]
status: complete

dependency_graph:
  requires:
    - "Phase 14 Plan 01 (docs/advisor/index.md — overview + grounding invariant)"
  provides:
    - "docs/advisor/python-api.md — method-accurate Python API reference with offline executed fence"
  affects:
    - "docs/advisor/ — advisor section (python-api page now authored)"

tech_stack:
  added: []
  patterns:
    - "markdown-exec offline fence with FDARS_FENCE_OK execution sentinel"
    - "PYTHONPATH=scripts docs_data.load_canadian_weather pattern (matches existing exec-fence pages)"

key_files:
  created:
    - docs/advisor/python-api.md
  modified: []

decisions:
  - "FDARS_FENCE_OK sentinel printed inline with a real computed diagnostic value (mean_amplitude_separation) — proves fence executed vs. just being source text"
  - "Schema table rows use plain text field names (not backtick-wrapped) to match acceptance-criteria grep patterns exactly"
  - "Illustrative advise() fence kept as plain ```python (no exec attribute) with explicit ANTHROPIC_API_KEY warning in a !!! warning admonition"
  - "Forward cross-links to mcp.md and agent-skill.md added; build warns but does not fail (pages arrive in Phases 16-17, which is correct)"

metrics:
  duration: 13min
  completed_date: "2026-08-11"
  tasks_completed: 2
  tasks_total: 3
  commits: 2

actuals:
  tokens: 9500
  tasks: 2
  commits: 2
---

# Phase 15 Plan 01: Python API Page Summary

## One-liner

Offline `build_diagnostics` exec fence (Canadian Weather → kmeans_fd(k=4) → clustering diagnostics, FDARS_FENCE_OK sentinel proven in built HTML) plus full API reference — three functions with source-accurate signatures, Recommendation/Advice schema tables, illustrative advise() fence marked not-run.

## What Was Built

A new `docs/advisor/python-api.md` page documenting the recommend-only Python advisor surface:

**Task 1 (tracer): Page skeleton + offline executed fence**

- Created `docs/advisor/python-api.md` with H1 ("Python API"), intro paragraph naming the recommend-only surface, and a "Worked example" section.
- Offline executed fence using the exact `exec="1" html="1" source="above"` directive (copied from `docs/analyze/gmm-clustering.md`).
- Fence loads Canadian Weather via `docs_data.load_canadian_weather("temperature")`, clusters with `kmeans_fd(X, day, k=4, seed=42)`, builds diagnostics with `build_diagnostics(result, method="clustering", argvals=day)`, and prints `k`, `cluster_sizes`, `mean_amplitude_separation` (with `FDARS_FENCE_OK` sentinel), and `mean_phase_separation`.
- Build verified: `FDARS_FENCE_OK` appears in `site/advisor/python-api/index.html` — proving the fence executed at build time.
- Fence body contains no `advise(`/`anthropic`/`ANTHROPIC_API_KEY` (verified offline).

**Task 2 (auto): API reference prose, schema tables, illustrative fence**

- "Functions" section documents all three functions (`build_diagnostics`, `advise`, `describe_cluster_differences`) with source-accurate signatures, argument tables, and return descriptions.
- Five supported `build_diagnostics` method values listed: `"alignment"`, `"fpca"`, `"basis"`, `"smoothing"`, `"clustering"`.
- `run_llm=False` offline escape hatch documented explicitly for `describe_cluster_differences`.
- "Schema" section with two pipe-tables:
  - `Recommendation` table: `action | str`, `kind | Literal["parameter", "method", "none"]`, `rationale | str`, `expected_effect | str`, `evidence | list[str]` — field names and types verified verbatim against `python/fdars/advisor.py`.
  - `Advice` table: `interpretation | str`, `recommendations | list[Recommendation]`, `caveats | list[str]`.
- "Recommend-only surface" section stating the Python API returns `Advice` and stops (does not re-run fdars).
- One illustrative non-executed `advise()` fence (plain ```python, no `exec` attribute), preceded by a `!!! warning` admonition stating it requires `ANTHROPIC_API_KEY` and is not run in the docs build.
- Cross-links: back to `index.md` (overview), forward to `mcp.md` and `agent-skill.md` (Phases 16-17).

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 (tracer) | 4247968 | Page skeleton + offline build_diagnostics fence (FDARS_FENCE_OK proven) |
| Task 2 (auto) | 3a45d1e | Expand API reference — schema tables, advise/describe_cluster_differences, illustrative fence |

## Verification Results

All pre-checkpoint automated checks pass:

| Check | Result |
|-------|--------|
| `grep -c 'exec="1"' docs/advisor/python-api.md` == 1 | PASS |
| `FDARS_FENCE_OK` in `site/advisor/python-api/index.html` | PASS |
| Exec fence body contains no `advise(`/`anthropic`/`ANTHROPIC_API_KEY` | PASS |
| All three functions documented | PASS |
| Recommendation table: all 5 rows with correct types | PASS |
| Advice table: all 3 rows with correct types | PASS |
| Table separator row present | PASS |
| `ANTHROPIC_API_KEY` present (illustrative fence warning) | PASS |
| `run_llm` documented | PASS |
| Cross-links to `index.md`, `mcp.md`, `agent-skill.md` | PASS |
| `domain_context` and `task` parameters documented | PASS |
| `model="claude-opus-4-8"` default documented | PASS |
| `advisor.py` source unmodified | PASS |
| Task 2 full verify: `API_SECTIONS_OK` | PASS |
| Task 1 re-verify after Task 2: `FENCE_EXECUTED_OFFLINE` | PASS |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written, except one fix during Task 2:

**[Rule 1 - Bug] Schema table rows used backtick-wrapped types**

- **Found during:** Task 2 acceptance check
- **Issue:** Initial implementation wrote `` `str` ``, `` `list[str]` `` etc. with backticks in schema table cells. The acceptance-criteria grep patterns expect plain `str`, `list[str]`, `Literal[...]` without backtick wrapping.
- **Fix:** Changed schema table type cells from `` `str` `` to `str`, `` `list[str]` `` to `list[str]`, etc.
- **Files modified:** `docs/advisor/python-api.md`
- **Included in commit:** 3a45d1e

## Known Stubs

None. The page cross-links forward to `mcp.md` and `agent-skill.md` with `*(coming in Phase 16)*` / `*(coming in Phase 17)*` annotations. These are intentional forward links, not stubs — they will resolve when those pages are authored.

Build produces expected `WARNING` for the unresolved forward links but does not fail. This is the intended state for Phase 15.

## Threat Flags

None — this is a documentation-only change. No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Self-Check: PASSED

- `docs/advisor/python-api.md` exists: CONFIRMED
- Commit `4247968` exists: CONFIRMED
- Commit `3a45d1e` exists: CONFIRMED
- `FDARS_FENCE_OK` in built HTML: CONFIRMED
