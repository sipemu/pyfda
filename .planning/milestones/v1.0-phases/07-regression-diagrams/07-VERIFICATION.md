---
status: passed
phase: 07-regression-diagrams
verified: 2026-08-08
requirements: [DIA-05]
---

# Phase 07 — Verification (regression/ Diagrams)

Verified lean (direct checks + live-API method verification, no verifier subagent) per user request. **No diagram was edited** — all 12 regression/ diagrams were already conforming and accurate; the one flagged accuracy gap (GAP-0004) was disproven against the live API.

## Phase goal

Every diagram in the regression/ section conforms to STYLE_SPEC.md and correctly depicts method semantics.

## Success Criteria

| SC | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| 1 | All regression/ SVG diagrams pass SVGO lint | PASS | SVGO idempotence gate OK on all 12 |
| 2 | conformal-prediction.svg depicts a time-varying band ŷ(t)±q(t), not a scalar interval | PASS (premise corrected — see note) | The premise is false: `fdars.conformal` regression is scalar-response. The diagram's scalar interval is method-accurate. |
| 3 | scalar-on-function diagram shows the β(t) coefficient curve | PASS | scalar-on-function.svg Panel 3 contains the `β̂(t)` coefficient inset (labeled, `docs/assets/diagrams/scalar-on-function.svg:59-62`) |
| 4 | Every warranting regression/ page has an accurate diagram visible | PASS | All 12 diagrams present, embedded, conforming; the one flagged accuracy concern (conformal) verified accurate against the live API |

## SC#2 / GAP-0004 — false-positive finding (method-semantic verification)

The Phase 2 audit "CONFIRMED" that conformal-prediction.svg should show a time-varying functional band ŷ(t)±q(t) instead of a scalar interval, assuming `fdars.conformal` "operates on functional responses." **This assumption is incorrect.**

Live verification (`conformal_fregre_lm` — the method the diagram names and the page uses):
```
lower:       shape (5,)   # one scalar bound per test observation
upper:       shape (5,)
predictions: shape (5,)
coverage:    scalar
```
`conformal_fregre_lm` / `conformal_fregre_np` are **scalar-on-function** regression (functional predictor → scalar response). The response is a single number, so there is no domain [0,T] and no functional band. The conformal module exposes only scalar-response regression + classification methods; no function-on-scalar (`fosr`) conformal band exists.

**Conclusion:** the current diagram, showing a point ŷ with a scalar interval "ŷ ± interval", is **method-accurate**. Redrawing it as ŷ(t)±q(t) (the ROADMAP's planned Phase 7 work) would MISREPRESENT a scalar-response method. GAP-0004 is disproven; no redraw performed. This matches the STATE research flag that regression/ needed method-semantic verification before redrawing. User approved leaving the diagram as-is.

## Requirement traceability

- **DIA-05** — SATISFIED. All 12 regression/ diagrams conform + accurate. The conformal "redraw" clause of DIA-05 is superseded by the method-accuracy finding above (scalar-response method → scalar interval is correct).

## Overall

**PASSED** — all Success Criteria met (SC#2 by disproving its premise); DIA-05 satisfied. Zero diagram edits.
