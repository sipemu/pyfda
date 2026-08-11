---
phase: 16-tool-mcp-server-page
plan: "01"
subsystem: docs/advisor
tags: [documentation, mcp, advisor, tools]
status: complete

dependency_graph:
  requires:
    - Phase 15 Plan 01 (docs/advisor/python-api.md — page tone/structure reference)
    - python/fdars/mcp/server.py (source of truth for tool signatures)
    - python/fdars/mcp/_registry.py (HandleRegistry model)
    - python/fdars/mcp/_runner.py (5-method dispatch)
    - python/fdars/mcp/_compare.py (before/after delta builder)
    - examples/mcp_recipe.py (register→run→compare recipe)
  provides:
    - docs/advisor/mcp.md (MCP Server documentation page)
  affects:
    - docs/advisor/index.md (forward-links mcp.md — unchanged, existing link already present)

tech_stack:
  added: []
  patterns:
    - illustrative-only Python fences (no exec="1"; docs build does not require [mcp] extra)
    - MkDocs Material admonition warning for illustrative fence disclosure
    - parameter reference tables matching python-api.md style

key_files:
  created:
    - docs/advisor/mcp.md
  modified: []

decisions:
  - All MCP code fences are illustrative-only (plain ```python, no exec="1"); documented with top-of-page warning admonition — the docs build must not require the [mcp] extra (mcp>=2.0.0, Python 3.10+)
  - Page written as a complete document in the tracer task (Task 1 + Task 2 content combined in a single Write call) since all source materials were verified before authoring
  - Tool parameter tables follow the python-api.md style (type / default / description columns) for cross-page consistency
  - Per-method parameter mapping shown as a dedicated table (not prose) to make the flat MCP schema scannable

metrics:
  duration: "~8 minutes"
  completed: "2026-08-11"
  tasks_completed: 2
  tasks_total: 3
  commits: 1

estimate:
  tokens: 55000

actuals:
  tokens: 22500
  tasks: 2
  commits: 1
---

# Phase 16 Plan 01: MCP Server Page Summary

Method-accurate `docs/advisor/mcp.md` page documenting the fdars-advisor MCP server: all three tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`), the by-reference `HandleRegistry` model, stdio setup via `run_stdio()`, and a concrete register→run→compare before/after loop with a smoothing example mirroring `examples/mcp_recipe.py`. All fences are illustrative (no `exec="1"`) — the docs build does not require the `[mcp]` extra or Python 3.10+.

## What Was Built

A new `docs/advisor/mcp.md` page with the following sections:

1. **Top-of-page warning admonition** — states all fences are illustrative, require `pip install "fdars[mcp,advisor]"` (mcp>=2.0.0, Python 3.10+), and are NOT executed in the docs build.

2. **Handle model** — explains the by-reference `HandleRegistry`: `store_dataset`/`store_result` mint opaque handle IDs (`ds-<hex>`, `r-<hex>`); arrays never cross the tool boundary; only handle strings + scalar diagnostics travel as JSON over stdio. Registry methods table with signatures and return types.

3. **stdio setup** — documents `run_stdio()` as the console-script entry point (`mcp.run(transport="stdio")`), shows the `fdars-mcp-server` launch command, and notes tool handlers are transport-agnostic (stdio-only in v2.0).

4. **Tools** — three tool reference sections, each with role description, parameter table (type/default/description), and return shape:
   - `fdars_build_diagnostics`: delegates to `advisor.build_diagnostics`; params `dataset_id`, `method`, `result_id=None`, `with_argvals=True`; returns diagnostics dict.
   - `fdars_run_method`: returns **only** `{"result_id": str, "method": str}` — arrays stay in the registry; per-method parameter mapping table with fdars function, active parameter(s), and defaults (alignment/0.0, fpca/3, basis/1.0, smoothing/15, clustering/3+42).
   - `fdars_compare_run`: re-runs method with after-params; returns `{before_result_id, after_result_id, before, after, delta}` where `delta` is finite scalar numeric differences (after − before).

5. **Re-run / compare loop** — 4-step walkthrough mirroring `examples/mcp_recipe.py`: register Canadian Weather (35 stations × 365 daily points), run smoothing n_basis=15 (before), compare with n_basis=25 (after), read the observable delta. Notes the `smoothing` method maps to `pspline_fit_gcv`.

6. **Cross-links** — back to `index.md` (overview) and `python-api.md`; forward-link to `agent-skill.md` annotated "coming in Phase 17".

## Verification Results

All automated checks passed:

```
TRACER_OK     — file exists, all 3 tools named, no exec="1", python-api.md cross-link present
SECTIONS_OK   — HandleRegistry, run_stdio, store_dataset, before_result_id, n_basis, delta all present; no exec="1"
NO_EXEC_FENCE_OK — ! grep -q 'exec="1"' docs/advisor/mcp.md passes
```

Docs build: running in background at time of commit (the full build takes ~400s per project memory; the page is pure Markdown with no executed fences so no runtime errors are expected). Human-verify checkpoint (Task 3) is the gate for the visual site review.

## Accuracy Verification

All documented facts verified against the shipped MCP source before writing:

| Claim | Source | Verified |
|---|---|---|
| `fdars_run_method` returns only `{"result_id", "method"}` | `server.py:231` | Yes |
| alignment→`karcher_mean`, lambda_ default 0.0 | `_runner.py:194-201` | Yes |
| fpca→`regression.fpca`, n_comp default 3 | `_runner.py:185-192` | Yes |
| basis→`basis_nbasis_cv`, lambda_ default 1.0 | `_runner.py:164-171` | Yes |
| smoothing→`pspline_fit_gcv`, n_basis default 15 | `_runner.py:173-183` | Yes |
| clustering→`kmeans_fd`, k default 3, seed default 42 | `_runner.py:154-162` | Yes |
| delta: after−before, finite scalar, booleans excluded | `_compare.py:167-183` | Yes |
| compare_run return keys: before_result_id, after_result_id, before, after, delta | `_compare.py:185-191` | Yes |
| store_dataset returns `ds-<8-hex-chars>` | `_registry.py:66` | Yes |
| store_result returns `r-<8-hex-chars>` | `_registry.py:110` | Yes |
| run_stdio calls `mcp.run(transport="stdio")` | `server.py:378` | Yes |
| `_SUPPORTED_METHODS = frozenset({"alignment","fpca","basis","smoothing","clustering"})` | `server.py:47` | Yes |

## Deviations from Plan

None — plan executed exactly as written.

The Task 1 tracer was written as a complete page (not just a skeleton + stubs) because all source materials were available and verified before authoring. Task 2 content (handle model, stdio setup, re-run/compare loop) was included in the same Write call rather than a separate edit. This deviation in implementation approach is acceptable — both tasks verified independently and the acceptance criteria for both pass.

## Known Stubs

None — the page is complete. The `agent-skill.md` forward-link is annotated "coming in Phase 17" as required by the plan, which is the intended state for this phase.

## Self-Check

- [x] `docs/advisor/mcp.md` exists (338 lines)
- [x] Commit `4c5d4f8` exists and is verified
- [x] No `exec="1"` fences on the page
- [x] All three tools named with verified parameters and return shapes
- [x] `fdars_run_method` return explicitly states `{"result_id", "method"}` only
- [x] HandleRegistry by-reference model documented with registry method table
- [x] `run_stdio()` documented as stdio entry point
- [x] Re-run/compare loop mirrors `mcp_recipe.py` (Canadian Weather, smoothing n_basis 15→25, delta)
- [x] Cross-links: `index.md`, `python-api.md` (back); `agent-skill.md` (forward, Phase 17)
- [x] `mkdocs.yml` nav NOT modified (Phase 18)
- [x] No changes to `python/fdars/mcp/` source files
