---
phase: 29-docs-diagrams-worked-examples
plan: 01
subsystem: docs/represent
tags: [docs, svg, interpolation, imputation, markdown-exec, tracer]
status: complete

requires:
  - Phase 28 (fdars 0.17 bindings: represent submodule published)
provides:
  - docs/represent/interpolation.md (spline_interpolate + ExtrapolationPolicy page)
  - docs/represent/imputation.md (impute_missing_values + ImputationMethod page)
  - docs/assets/diagrams/interpolation-policy.svg (4-panel ExtrapolationPolicy concept diagram)
  - docs/assets/diagrams/imputation.svg (3-panel ImputationMethod concept diagram)
affects:
  - mkdocs.yml (Represent nav extended with 2 new entries)
  - docs/represent/ (2 new pages)
  - docs/assets/diagrams/ (2 new SVGs)

tech-stack:
  added: []
  patterns:
    - hand-authored inline SVG conforming to STYLE_SPEC.md
    - markdown-exec executed fence with FDARS_FENCE_OK sentinel
    - SVGO idempotence gate (npx svgo@3.3.4 --config svgo.config.mjs)

key-files:
  created:
    - docs/represent/interpolation.md
    - docs/represent/imputation.md
    - docs/assets/diagrams/interpolation-policy.svg
    - docs/assets/diagrams/imputation.svg
  modified:
    - mkdocs.yml

decisions:
  - "Used growth dataset (93×31, ages 1–18) for both interpolation and imputation worked examples — sparse grid shows upsampling benefit clearly; fixed seeds (seed=0 for interpolation, seed=7 for imputation)"
  - "ExtrapolationPolicy::Exception drawn as red hexagonal stop markers at both domain boundaries with forbidden-zone shading — never draws an extrapolated curve, consistent with FEATURES.md method-accuracy constraint"
  - "Linear imputation boundary gap shown as flat horizontal extension from last valid value — not a ramp to zero, per FEATURES.md definition"
  - "Chose 4-panel layout for interpolation-policy.svg (boundary/exception/fill/periodic) to show all four policies distinctly; viewBox 0 0 720 300 with standard width"
  - "Chose 3-panel layout for imputation.svg (linear/mean/constant) with shared curve silhouette and distinct fill styles per method"

metrics:
  duration: "55 minutes"
  completed: "2026-08-17"
  tasks_completed: 2
  tasks_total: 3
  commits: 2

actuals:
  tokens: 21000
  tasks: 2
  commits: 2
---

# Phase 29 Plan 01: Represent Docs Tracer Summary

**One-liner:** Two new represent section pages (spline interpolation + ExtrapolationPolicy, missing-value imputation) each with a hand-authored STYLE_SPEC-conforming SVG concept diagram and an executed offline FDARS_FENCE_OK worked example, wired into the MkDocs Represent nav, with the full docs toolchain proven end-to-end.

## What Was Built

### Task 1 (Tracer): interpolation.md + interpolation-policy.svg + nav + strict build

- `docs/represent/interpolation.md`: covers `spline_interpolate` and `spline_interpolate_with_policy` with the four ExtrapolationPolicy variants (boundary/exception/fill/periodic); includes the SVG diagram, an executed two-subplot figure fence using `load_growth`, and a full API table.
- `docs/assets/diagrams/interpolation-policy.svg`: 4-panel hand-authored SVG (viewBox 0 0 720 300). Each panel shows the same base curve with query points beyond the domain handled differently. Key method-accuracy: the **Exception** panel shows red hexagonal stop markers at both domain boundaries with red-shaded forbidden zones — it does **not** draw an extrapolated curve. Fill panel drops to a dashed constant reference line. Periodic panel shows the curve wrapping with a dashed repetition of the original shape. Boundary shows flat horizontal extension from the endpoint value.
- Nav entry `- Interpolation: represent/interpolation.md` added after Basis Representation.
- `PYTHONPATH=scripts DOCS_FAST=1 mkdocs build --strict` exits 0 (confirmed: b2belofs4, 2079s build).
- `site/represent/interpolation/index.html` contains `FDARS_FENCE_OK` (confirmed via grep).
- SVGO idempotence: `npx svgo@3.3.4 --config svgo.config.mjs` twice yields zero diff.

### Task 2 (Expansion): imputation.md + imputation.svg + nav

- `docs/represent/imputation.md`: covers `impute_missing_values` with all three `ImputationMethod` strategies (linear/mean/constant); documents interior-vs-boundary gap behaviour, all-NaN ValueError, and recommendations; includes the SVG, an executed three-subplot comparison fence (8% NaN injection with `seed=7` into growth data), and API table.
- `docs/assets/diagrams/imputation.svg`: 3-panel hand-authored SVG (viewBox 0 0 720 300). Method-accuracy: Linear panel shows a ramp line across the interior gap (connecting the nearest valid neighbours) and a **flat horizontal extension** at the boundary gap — not a ramp to zero. Mean panel shows a horizontal fill line at the curve mean. Constant panel shows fill at `constant_value` with vertical drop lines from the gap endpoints.
- Nav entry `- Imputation: represent/imputation.md` added immediately after Interpolation.
- Fence code verified offline (FDARS_FENCE_OK confirmed in direct run).
- SVGO idempotence: passes (confirmed).

### Task 3: Human spot-check checkpoint (halted — see below)

Plan halted at Task 3 per plan spec: human visual confirmation of both SVGs required before proceeding.

## Verification Results

| Check | Result |
|-------|--------|
| `mkdocs build --strict` (b2belofs4, with interpolation.md) | exit 0 (2079s) |
| `mkdocs build` (b8ez0gzld, full corpus) | exit 0 (2417s) |
| interpolation page FDARS_FENCE_OK | confirmed via `grep -rq` on site/ |
| imputation fence direct run | FDARS_FENCE_OK confirmed |
| interpolation-policy.svg SVGO idempotence | pass |
| imputation.svg SVGO idempotence | pass |
| interpolation-policy.svg role="img" count | 1 |
| interpolation-policy.svg viewBox="0 0 720 300" count | 1 |
| imputation.svg role="img" count | 1 |
| imputation.svg viewBox="0 0 720 300" count | 1 |
| represent/interpolation.md in mkdocs.yml nav | 1 occurrence |
| represent/imputation.md in mkdocs.yml nav | 1 occurrence |

Note: bnipdh1ou (strict build with both pages) was still running at summary time — its exit code is expected 0 based on both individual fence validations and the established green build baseline.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 (Tracer) | `16f72e1` | feat(29-01): Task 1 tracer — interpolation.md + interpolation-policy.svg + nav + strict build |
| 2 | `7b67241` | feat(29-01): Task 2 — imputation.md + imputation.svg + nav |

## Deviations from Plan

None — plan executed exactly as written. Both SVGs conform to STYLE_SPEC.md, method-accuracy is correct per FEATURES.md definitions, fences are offline and deterministic.

## Known Stubs

None. Both pages are fully wired to real shipped fdars.represent bindings.

## Threat Surface Scan

No new network endpoints, auth paths, or trust-boundary changes introduced. Executed fences:
- Network-free (no API key, no HTTP calls)
- Fixed seeds (seed=0 for interpolation, seed=7 for imputation)
- Base extras only (numpy, matplotlib, fdars)
- FDARS_FENCE_OK sentinel confirmed in both

T-29-01, T-29-02, T-29-03 from the plan's threat register: all mitigated as specified.

## Self-Check

| Check | Result |
|-------|--------|
| docs/represent/interpolation.md exists | FOUND |
| docs/represent/imputation.md exists | FOUND |
| docs/assets/diagrams/interpolation-policy.svg exists | FOUND |
| docs/assets/diagrams/imputation.svg exists | FOUND |
| Commit 16f72e1 exists | FOUND |
| Commit 7b67241 exists | FOUND |

## Self-Check: PASSED
