---
phase: 74-deepen-regression-family-thin-pages
plan: "04"
subsystem: documentation
tags: [mkdocs, fdars, concurrent-regression, varying-coefficient, docs-depth]

requires:
  - phase: 74-deepen-regression-family-thin-pages
    provides: "74-01 tracer established the parity pattern (When-to-use + numbered sections + FDARS_FENCE_OK fences + html figure + See-also)"

provides:
  - "concurrent-regression.md at full parity: When-to-use decision section, manual prediction fence, manual bandwidth-CV fence, formal No-built-in-bandwidth-CV warning, See also block, 3 exec fences all emitting FDARS_FENCE_OK"

affects:
  - "74-05 (functional-glm.md — last regression page)"
  - "Phase 79 (GATE — whole-site --strict build)"

actuals:
  tokens: 2404
  tasks: 1
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Manual prediction by beta_curve matrix algebra: y_pred = intercept + sum_k(beta_curve[k] * x_k_new) — no predict_ function"
    - "Manual bandwidth-CV: held-out MSE loop over candidate bandwidths (no built-in fregre_np_cv-style helper)"

key-files:
  created: []
  modified:
    - docs/regression/concurrent-regression.md

key-decisions:
  - "No predict_concurrent_regression exists — explicitly avoided referencing this non-existent symbol; prediction section uses manual matrix algebra with beta_curve and intercept"
  - "Bandwidth-CV warning uses two separate admonitions: one naming the gap (No built-in bandwidth CV) and one giving variance/bias intuition — combined they satisfy the formal warning requirement while keeping the bias/variance guidance separate"
  - "Existing html=1 figure (Section 1) preserved intact; two new non-html exec fences added (prediction, bandwidth-CV) to reach 3-fence total"
  - "Restructured page into numbered sections (1. Fitting, 2. Out-of-sample prediction, 3. Bandwidth selection and Caveats) matching the parity template without rewiring the correct existing content"

patterns-established:
  - "Manual prediction pattern for models with no predict_ function: beta_curve @ new_x via row-wise element-wise multiply, then add intercept"

requirements-completed: [DEPTH-01]

coverage:
  - id: D1
    description: "concurrent-regression.md has a '## When to use' decision section with a comparison table (concurrent vs FoF vs SoF) and a quick rule"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural check: /##\\s+When to use/i.test(s) => true"
        status: pass
    human_judgment: false
  - id: D2
    description: "Page includes a manual out-of-sample prediction fence using beta_curve (p,m) + intercept"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural check: /beta_curve/.test(s) => true, !/predict_concurrent_regression/.test(s) => true"
        status: pass
      - kind: other
        ref: "PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/regression/concurrent-regression.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "Page includes a manual bandwidth-CV fence and a formal !!! warning admonition about no built-in CV"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural check: /^!!! warning[^\\n]*(bandwidth|CV)/mi.test(s) => true; fences_ge3: true"
        status: pass
    human_judgment: false
  - id: D4
    description: "Page carries >=3 admonitions and >=3 runnable FDARS_FENCE_OK fences, >=1 with html=1; all fences pass offline"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural: fences=3 adm=5 html=1 (ALL OK)"
        status: pass
      - kind: other
        ref: "run_page_fences.py: ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK"
        status: pass
    human_judgment: false
  - id: D5
    description: "Page has a '## See also' block linking FoF, SoF, FoScalar, diagnostics, and regression index"
    requirement: DEPTH-01
    verification:
      - kind: other
        ref: "node structural check: /##\\s+See also/i.test(s) => true"
        status: pass
    human_judgment: false

duration: 2min
completed: "2026-09-05"
status: complete
---

# Phase 74 Plan 04: concurrent-regression.md Summary

**concurrent-regression.md brought to full parity: When-to-use table (concurrent vs FoF vs SoF), manual beta_curve prediction example, manual bandwidth-CV fence, formal No-built-in-bandwidth-CV warning, See also block — all 3 exec fences emit FDARS_FENCE_OK**

## Performance

- **Duration:** 2 min
- **Started:** 2026-09-05T19:44:57Z
- **Completed:** 2026-09-05T19:47:39Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added `## When to use` section with method-comparison table (concurrent vs FoF vs SoF), same-grid `!!! info` admonition, and a quick rule with inline links to `function-on-function.md` and `scalar-on-function.md`
- Added Section 2 (Out-of-sample prediction) with manual formula prose and a runnable fence showing `y_pred = intercept + beta[0] * x_new` plus a `!!! tip` generalising to p predictors
- Added manual bandwidth-CV fence in Section 3 (held-out MSE loop over 5 candidate bandwidths, no built-in predict or CV needed)
- Added formal `!!! warning "No built-in bandwidth CV"` admonition (previously only in prose)
- Added `## See also` block with 5 links: FoF, SoF, FoScalar, diagnostics, regression index
- Preserved all existing correct content verbatim: theory, parameters table, returns table, kernel table, beta_curve (p,m) note, existing html=1 figure, existing bias/variance warning, model-scope section, and all three references
- Both verify gates pass: structural check (fences=3, adm=5, html=1) and fence runner (ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK)

## Task Commits

1. **Task 1: Bring concurrent-regression.md to full parity** - `fafe2f1` (docs)

**Plan metadata:** TBD (docs: complete plan)

## Files Created/Modified

- `/home/simonm/projects/rust/pyfda/docs/regression/concurrent-regression.md` — extended from ~50% to full parity; added When-to-use, prediction section, bandwidth-CV section, warning admonition, See also block; 123 net insertions

## Decisions Made

- No `predict_concurrent_regression` symbol referenced anywhere — the page describes prediction as "no dedicated predict function" and uses manual matrix algebra on `beta_curve` and `intercept`
- Used two warning admonitions in the bandwidth section: one naming the gap ("No built-in bandwidth CV") and one covering bias/variance trade-off (kept from existing page, preserved verbatim)
- Restructured the page into explicit numbered sections without rewriting the existing body prose

## Deviations from Plan

None — plan executed exactly as written. The only adaptation was rephrasing one mention of the non-existent function symbol to satisfy the structural check's no_predict_symbol assertion, which the PLAN.md itself required ("does NOT reference a predict_concurrent_regression symbol").

## Issues Encountered

- First structural check run failed `no_predict_symbol` because the prose said "There is no `predict_concurrent_regression` function" (exact symbol name appeared in the text). Fixed by rephrasing to "no dedicated predict function" — which is both cleaner prose and satisfies the check.

## Known Stubs

None.

## Threat Flags

None — docs-only edit to one markdown file; no new network surface, no auth paths.

## Self-Check: PASSED

- `/home/simonm/projects/rust/pyfda/docs/regression/concurrent-regression.md` — FOUND (git tracked, committed in fafe2f1)
- Commit fafe2f1 — FOUND in git log
- Both verify gates passed (structural + fence runner)

## Next Phase Readiness

- concurrent-regression.md is at full parity; plan 74-05 (functional-glm.md) is the final regression-family page
- No blockers

---
*Phase: 74-deepen-regression-family-thin-pages*
*Completed: 2026-09-05*
