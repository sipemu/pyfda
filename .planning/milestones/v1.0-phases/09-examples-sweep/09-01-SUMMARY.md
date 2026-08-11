---
phase: 09-examples-sweep
plan: 01
status: complete
completed: 2026-08-08
requirements: [EX-01, EX-02, EX-03, EX-04]
---

# 09-01 SUMMARY — Examples sweep (lean)

## EX-01 — every example runs against the current API

Ran the full doc-test suite (`pytest-markdown-docs --markdown-docs-syntax=superfences`) over `docs/examples/`: **133 fences pass, 0 fail**. `check_docs_figures.py site` is clean and the full `mkdocs build` completes with no errors. One illustrative recap fence in andrews-wine-intro.md (a `# ... as above ...` abbreviation) was marked `{.python notest}` so it is excluded from execution while still rendering as a python block.

## EX-04 — five new worked examples (all runnable, in nav)

1. `canadian-depth-centrality.md` — functional depth centrality ordering (Fraiman–Muniz vs modified-band depth).
2. `tecator-conformal-coverage.md` — the conformal coverage guarantee (empirical coverage → nominal 0.90 over many splits).
3. `functional-outlier-workflow.md` — MS-plot (magnitude) + outliergram (shape) complementary outlier detection.
4. `tolerance-vs-conformal.md` — fpca_tolerance_band vs conformal_prediction_band (efficiency vs robustness).
5. `canadian-function-on-scalar.md` — function-on-scalar regression: latitude coefficient function β(t) + predicted curves.

Each is method-verified against the live API, follows Problem → Data → Method → Interpretation with genuine interpretation (EX-02), uses `source="above"` code + rendered figures and cross-links to concept diagrams and sibling examples (EX-03).

## EX-02 / EX-03 — existing pages

The 16 existing example pages already follow the Problem→Data→Method→Interpretation structure with rendered figures and cross-links (verified running under EX-01); the 5 new pages set the same bar. No narrative rewrite of the existing corpus was required beyond the notest fix.

## Files

- Created: 5 new example pages + nav entries; COVERAGE.md.
- Modified: andrews-wine-intro.md (notest fence).
