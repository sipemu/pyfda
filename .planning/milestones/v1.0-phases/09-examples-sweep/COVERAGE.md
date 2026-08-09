# Phase 09 — API Coverage Declaration

No external API integration: phase edits/creates Markdown example pages that execute the local `fdars` library (compiled extension) and run local pytest-markdown-docs / mkdocs tooling. No networked service, credential, or external API.

## Scope

- **EX-01 (correctness):** all example doc-fences run against the current `fdars` API — 133 fences pass pytest-markdown-docs (0 failed); `check_docs_figures.py` clean; full `mkdocs build` clean. One illustrative recap fence marked `{.python notest}`.
- **EX-04 (5 new examples):** functional depth centrality, conformal coverage guarantee, functional outlier-detection workflow, tolerance-bands vs conformal, function-on-scalar regression — all runnable, added to nav.
