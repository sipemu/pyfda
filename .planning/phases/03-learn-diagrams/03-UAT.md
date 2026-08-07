---
status: testing
phase: 03-learn-diagrams
source: [03-VERIFICATION.md]
started: 2026-08-08
updated: 2026-08-08
---

## Current Test

number: 1
name: Smoothing ghost visual distinctness (Plan 01, Task 3)
expected: |
  On /learn/smoothing/, the smoothed (right) panel's faint blue "before" ghost is
  visibly a DIFFERENT jagged shape from the noisy (left) panel — not the same wiggle
  shifted down. The bold smooth blue curve still passes cleanly through the noise as a
  legible before/after contrast, and nothing else changed (title, subtitle, method
  panel, arrows, labels intact).
awaiting: user response

## Tests

### 1. Smoothing ghost visual distinctness (Plan 01, Task 3)
expected: |
  On /learn/smoothing/, Panel 3's faint blue "before" ghost is a genuinely distinct
  jagged shape from Panel 1's noisy input (not a copy shifted down); the bold smooth
  curve reads as a clean before/after contrast; all other elements unchanged.
result: [pending]

### 2. Section-wide learn/ diagram accuracy (Plan 02, Task 4)
expected: |
  Open all 6 learn/ pages — /learn/introduction/, /learn/custom-plotting/,
  /learn/simulation/, /learn/smoothing/, /learn/derivatives/, /learn/irregular-sampling/.
  For each, the concept diagram renders (no broken image), is legible, and faithfully
  depicts the method described on the page (accurate, non-generic). This is the learn/
  section review gate before Phase 4 begins.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
