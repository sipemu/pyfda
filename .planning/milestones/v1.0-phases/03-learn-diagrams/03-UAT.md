---
status: passed
phase: 03-learn-diagrams
source: [03-VERIFICATION.md]
started: 2026-08-08
updated: 2026-08-08
audit_acknowledged:
  milestone: v6.0
  at: 2026-08-22
  gap_snapshot: "passed::scenarios=0"
---

## Current Test

number: —
name: All tests passed
expected: |
  Test 1 passed after GAP-03-UAT-01 fix (commit dfc925a): smooth curve now threads the
  redrawn ghost (verified via rasterized render; user confirmed on fresh image). The
  earlier "still broken" report was a stale live-server/browser-cache view. Test 2 passed.
awaiting: none — phase ready to seal

## Tests

### 1. Smoothing ghost visual distinctness (Plan 01, Task 3)

expected: |
  On /learn/smoothing/, Panel 3's faint blue "before" ghost is a genuinely distinct
  jagged shape from Panel 1's noisy input (not a copy shifted down); the bold smooth
  curve reads as a clean before/after contrast; all other elements unchanged.
result: pass
resolved_by: dfc925a
note: |
  Initially failed — bold smooth curve sat too high above the redrawn ghost (Plan 03-01
  moved the ghost but left the curve). Fixed in dfc925a by redrawing the ghost so its
  jitter straddles the curve's midline at each x (11 vertices below, 10 above; verified by
  rasterized render). User's "same as before" retry was a stale server/cache view; user
  confirmed pass on the freshly-rendered image.

### 2. Section-wide learn/ diagram accuracy (Plan 02, Task 4)

expected: |
  Open all 6 learn/ pages — /learn/introduction/, /learn/custom-plotting/,
  /learn/simulation/, /learn/smoothing/, /learn/derivatives/, /learn/irregular-sampling/.
  For each, the concept diagram renders (no broken image), is legible, and faithfully
  depicts the method described on the page (accurate, non-generic). This is the learn/
  section review gate before Phase 4 begins.
result: pass

## Summary

total: 2
passed: 2
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

### GAP-03-UAT-01: Smooth curve does not thread the redrawn Panel 3 ghost — RESOLVED (dfc925a)

status: resolved
severity: medium
source_test: 1
file: docs/assets/diagrams/smoothing.svg
symptom: |
  On /learn/smoothing/, the bold smooth blue curve (Panel 3) sits too high and does not
  pass through the noisy "before" signal — the before/after contrast reads as wrong.
diagnosis: |
  Plan 03-01 redrew the ghost noisy path (line 48) but left the smooth Bézier (line 49)
  as-is. The new ghost's vertical center (min y≈44-50) sits ~10-17px below the curve,
  which was tuned to the old ghost's deeper dips (min y≈34-38). The curve no longer
  threads the noise midline.
fix: |
  Redraw ONLY the Panel 3 ghost path (line 48) so its per-vertex jitter oscillates
  above/below the smooth curve's y at each x (curve y: 86→~55→38→50 across x=0→120→156),
  with ±9-12px amplitude, while keeping every vertex distinct from Panel 1's sequence
  (no multi-vertex run may match Panel 1). Do NOT touch the smooth curve, style block,
  viewBox, role, or aria-label. Re-run the SVGO idempotence gate and mkdocs build.
