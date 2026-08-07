---
status: testing
phase: 01-foundation
source: [01-VERIFICATION.md]
started: 2026-08-07
updated: 2026-08-07
---

## Current Test

number: 1
name: Two consecutive full mkdocs builds produce byte-identical SVG (FND-03, ROADMAP SC #3)
expected: |
  With DOCS_FAST unset, running `mkdocs build` twice and diffing the generated SVG
  output from docs_fig.py exec blocks shows no differences (svg.hashsalt makes element
  IDs deterministic). Note: differences confined to example pages with unseeded RNG are
  a later-phase (per-block seed audit) concern, NOT a Phase 1 docs_fig.py-seam defect.
awaiting: user response

## Tests

### 1. Two-build byte-identical SVG (FND-03)
expected: Two consecutive `mkdocs build` runs (DOCS_FAST unset) produce byte-identical SVG output from docs_fig.py exec blocks.
test: |
  rm -rf site s1
  mkdocs build && cp -r site s1 && mkdocs build
  diff -r s1 site   # focus on generated *.svg / inline SVG in exec-block pages
why_human: Requires the compiled fdars wheel + a full mkdocs build; the svg.hashsalt code seam is verified present, but end-to-end determinism across two real builds is a runtime invariant not confirmable from source alone.
result: [pending]

### 2. DOCS_FAST=1 materially faster build (FND-06, ROADMAP SC #6)
expected: On a page using fast() for expensive params, `DOCS_FAST=1 mkdocs build` completes materially faster than a full build.
test: |
  time mkdocs build
  time DOCS_FAST=1 mkdocs build
why_human: Requires a full mkdocs build with compiled fdars. The fast() helper is functionally verified (returns fast_value when DOCS_FAST is set), but end-to-end speedup is a runtime property. NOTE: no example exec block currently calls fast() with expensive params — the helper is ready for adoption in Phases 3–8, so a measurable speedup is not demonstrable until at least one expensive block is wired to fast(). Decide whether "helper-ready" satisfies FND-06 for Phase 1 or whether a demonstrator block should be added now.
result: [pending]

### 3. CI gates pass on GitHub Actions (FND-02, FND-05, D-09)
expected: On a real CI run, Gate A (SVGO idempotence lint on all 43 diagrams) and Gate B (doc-test smoke on canadian-weather.md) both pass, and the SVGO gate runs before mkdocs build.
test: Push the branch / open a PR and confirm the docs workflow's two new gates pass in GitHub Actions.
why_human: CI run confirmation requires actual GitHub Actions execution; cannot be observed from the local working tree.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
