---
phase: 07-regression-diagrams
plan: 01
status: complete
completed: 2026-08-08
requirements: [DIA-05]
---

# 07-01 SUMMARY — regression/ diagrams sweep (lean, verify-only)

Executed lean per user request. **Zero diagram edits** — all 12 regression/ diagrams were already conforming; the one scheduled redraw (GAP-0004) was disproven by live method verification.

## Key finding — GAP-0004 is a false positive

The ROADMAP scheduled a redraw of conformal-prediction.svg from a scalar interval to a functional band ŷ(t)±q(t). Live verification of `conformal_fregre_lm` (the method the diagram names) returns `lower`/`upper`/`predictions` of shape `(n,)` — **one scalar interval per test observation**. It is scalar-on-function regression (scalar response); there is no functional band. The current scalar-interval depiction is method-accurate. Redrawing would have made it wrong. User approved leaving it as-is. Full evidence in 07-VERIFICATION.md.

## Verification (all 12 regression/ diagrams)

- SVGO idempotence gate: all 12 OK (SC#1).
- STYLE_SPEC markers: all 12 conform (viewBox 0 0 720 300, five classes, system-ui, role=img, aria-label).
- SC#3: scalar-on-function.svg shows the β̂(t) coefficient inset (labeled).
- R-era: clean.

## Files

- No diagram files modified.
- Created: `.planning/phases/07-regression-diagrams/COVERAGE.md`, `07-VERIFICATION.md`
