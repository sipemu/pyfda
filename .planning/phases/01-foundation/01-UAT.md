---
status: complete
phase: 01-foundation
source: [01-VERIFICATION.md]
started: 2026-08-07
updated: 2026-08-07
---

## Current Test

[testing complete]

## Tests

### 1. Two-build byte-identical SVG (FND-03)
expected: Two consecutive `mkdocs build` runs (DOCS_FAST unset) produce byte-identical SVG output from docs_fig.py exec blocks.
test: |
  PYTHONPATH=scripts mkdocs build -d s1 --clean && PYTHONPATH=scripts mkdocs build -d s2 --clean && diff -r s1 s2
result: pass
reason: |
  Verified by two real mkdocs builds. Initial run found a genuine FND-03 tooling defect: matplotlib
  stamped a wall-clock <dc:date> into every SVG, so ~65 pages differed build-to-build (svg.hashsalt
  itself was confirmed working — 0 differing element IDs). Fixed in scripts/docs_fig.py by passing
  metadata={"Date": None} to savefig (commit bf54db8, gap G-01-1). Re-verified: differing pages dropped
  from ~65 to 1, with 0 remaining <dc:date> diffs and no non-RNG page differing. The one residual page
  (represent/depth-functions.md) differs solely due to unseeded example RNG (random_projection_1d /
  random_tukey_1d called without a seed) — the per-block seed audit explicitly deferred to Phases 3–8
  (research Pitfall 3, D-07). The Phase-1 determinism tooling (svg.hashsalt + date suppression) is
  verified working end-to-end; user accepted deferring the example-RNG seeding.

### 2. DOCS_FAST=1 materially faster build (FND-06, ROADMAP SC #6)
expected: On a page using fast() for expensive params, `DOCS_FAST=1 mkdocs build` completes materially faster than a full build.
result: pass
reason: "User accepted 'helper-ready' as satisfying FND-06 for Phase 1 (2026-08-07). The fast() helper is verified correct (returns 50 with DOCS_FAST=1, 500 unset; single _os.environ.get call, DRY per D-08) and speed-only per D-07. End-to-end speedup will be demonstrable once Phases 3–8 wire fast() into expensive exec blocks."

### 3. CI gates pass (FND-02, FND-05, D-09)
expected: Gate A (SVGO idempotence lint on all 43 diagrams) and Gate B (doc-test smoke on canadian-weather.md) both pass; the SVGO gate runs before mkdocs build.
test: |
  # Gate A (per docs.yml): svgo twice, diff pass 2 vs pass 1, for each docs/assets/diagrams/*.svg
  # Gate B (per docs.yml): PYTHONPATH=scripts pytest --markdown-docs --markdown-docs-syntax=superfences docs/examples/canadian-weather.md
result: pass
reason: "Both gate commands run locally against the current tree. Gate A: 43/43 diagrams idempotent under svgo.config.mjs (0 non-idempotent). Gate B: 8/8 fences pass (2.05s). The GitHub Actions run will confirm on next push, but the gate logic is verified working."

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Deferred Follow-Ups

- test: 1
  idea: "Seed the unseeded stochastic example blocks (e.g. represent/depth-functions.md random_projection_1d / random_tukey_1d, and any other pages using fdars internal RNG without a seed) so that full site-wide two-build byte-identity holds. This is the per-section RNG-seed audit scoped to Phases 3–8 (research Pitfall 3); Phase 1 delivers the determinism mechanism (svg.hashsalt + <dc:date> suppression), not the per-block seeding."
  deferred_at: 2026-08-07

## Gaps

- gap_id: G-01-1
  truth: "Two consecutive mkdocs builds produce byte-identical SVG output from docs_fig.py exec blocks (FND-03)"
  status: resolved
  reason: "matplotlib embedded a wall-clock <dc:date> in every SVG, breaking build determinism across all figure pages."
  resolved_by: "scripts/docs_fig.py — savefig metadata={'Date': None} (commit bf54db8)"
  resolved_at: 2026-08-07
  severity: major
  test: 1
