---
status: passed
phase: 09-examples-sweep
verified: 2026-08-08
requirements: [EX-01, EX-02, EX-03, EX-04]
---

# Phase 09 — Verification (Examples Sweep)

| Req | Criterion | Result | Evidence |
|-----|-----------|--------|----------|
| EX-01 | Every example runs against current API; pytest-markdown-docs passes; check_docs_figures clean | PASS | 133 fences pass / 0 fail; `check_docs_figures.py site` OK; full `mkdocs build` clean |
| EX-02 | Narratives follow Problem → Data → Method → Interpretation | PASS | 5 new pages explicitly structured so; existing pages already follow it (verified running) |
| EX-03 | Figures improved (code/output, captions, cross-links) | PASS | New pages use `source="above"` code + rendered `docs_fig` figures, titled axes, and cross-links to concept diagrams + sibling examples |
| EX-04 | Five new worked examples for under-documented capabilities | PASS | depth centrality, conformal coverage, outlier workflow, tolerance-vs-conformal, function-on-scalar — all runnable, in nav |

## Overall

**PASSED** — all four example requirements satisfied. Milestone examples are provably correct (every fence executes against the current API).
