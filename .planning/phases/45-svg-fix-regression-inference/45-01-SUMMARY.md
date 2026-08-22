---
phase: 45-svg-fix-regression-inference
plan: 01
subsystem: docs/assets/diagrams
tags: [svg, diagrams, regression, inference, style-spec, method-accuracy]
status: complete

depends_on: []
provides:
  - corrected elastic-multinomial.svg (720x480 de-cramped)
  - improved scalar-on-function.svg (β̂(t) prominence)
  - functional-glm.svg Gamma-link method-accuracy verified
  - inference-permutation-test.svg confirmed byte-unchanged
affects:
  - docs/assets/diagrams/elastic-multinomial.svg
  - docs/assets/diagrams/scalar-on-function.svg

tech_stack:
  added: []
  patterns:
    - Per-diagram SVGO idempotence gate (svgo@3.3.4 --config svgo.config.mjs, 2-pass cmp)
    - rsvg-convert PNG render eyeball
    - Intentional-override policy (inline font-size ≠ class value → keep; == class value → strip)

key_files:
  created: []
  modified:
    - docs/assets/diagrams/elastic-multinomial.svg
    - docs/assets/diagrams/scalar-on-function.svg

decisions:
  - "elastic-multinomial.svg height bumped 300→480 (canonical STYLE_SPEC allowed height); OvR rows re-spaced to h=74 each with ~24px gaps; method content preserved verbatim"
  - "scalar-on-function.svg β̂(t) inset enlarged conservatively (40→52px, .lab label, 'coefficient function' annotation, dc3545 border); other panels unchanged; surfaced for Phase 49 human review"
  - "functional-glm.svg: BYTE-UNCHANGED — Gamma inverse g(μ)=1/μ annotation confirmed correct vs shipped fdars sources; no redundant overrides"
  - "inference-permutation-test.svg: BYTE-UNCHANGED — lone font-size=11 on .mono (class=12) is intentional; no redundant overrides"
  - "inference/ section: no diagram commit required (all inference diagrams byte-unchanged — mirrors Phase 44 monitoring/advisor precedent)"

metrics:
  duration_seconds: 159
  completed: 2026-08-22T16:53:18Z
  tasks_completed: 3
  commits: 1

actuals:
  tokens: 8500
  tasks: 3
  commits: 1
---

# Phase 45 Plan 01: SVG Fix — Regression / Inference Summary

**One-liner:** De-cramped elastic-multinomial.svg to 720×480, improved scalar-on-function β̂(t) inset prominence, and confirmed functional-glm Gamma inverse-link annotation correct; zero redundant overrides across all four diagrams.

## Per-Diagram Outcomes

### functional-glm.svg — CONFIRMED CORRECT, BYTE-UNCHANGED

**Method-accuracy verification (SVGFIX-04):** The Gamma branch annotation `inverse   g(μ) = 1/μ` and `≠ log-link (R default)` is **VERIFIED CORRECT** against the shipped fdars GLM binding.

Source-line evidence (four independent confirmations):
1. `src/regression_mod.rs:1091` (internal DOCS caveat block): "Gamma uses inverse canonical link g(μ)=1/μ, NOT log-link (unlike R default)."
2. `src/regression_mod.rs:1143` (public docstring for `functional_glm`): family `"gamma"` → "(inverse link, NOT log)".
3. `docs/regression/functional-glm.md:34` (Link functions table): `"gamma"` → **inverse (canonical)** → `1/μ` → "NOT log-link".
4. `docs/regression/functional-glm.md:36-37` (warning admonition): "uses the **inverse canonical link** g(μ) = 1/μ, not the log-link that R's glm(..., family=Gamma) defaults to."

**Annotation is pedagogically accurate:** The `≠ log-link (R default)` note contrasts with R precisely because fdars differs from R — the diagram is not misleading.

**XML override tally (SVGFIX-03):** 6 `.mono` elements with `font-size="10"` (class `.mono`=12) → all DISTINCT → all INTENTIONAL → ZERO strips. The `fill="#dc3545"` on the Gamma row is a presentation attribute carrying the canonical FDARS_COLORS red → semantic, not a style override → KEEP.

**Gate results:** SVGO idempotence PASS; rsvg-convert PNG non-empty; viewBox 720×300, role="img", aria-label all present.

---

### elastic-multinomial.svg — CHANGED (de-cramped, 720×480)

**Visual fix (SVGFIX-01):** Bumped viewBox height 300→480 (width stays 720 — STYLE_SPEC canonical allowed height). The three OvR panels (previously h=42 each with ~8px gaps, cramped) are now:
- OvR 1: y=108, h=74
- OvR 2: y=206, h=74
- OvR 3: y=304, h=74
- Gap between rows: ~24px
- OvR outer panel: y=68, h=306
- Input panel: y=68, h=306 (also extended)
- Softmax panel: y=118, h=196; Output panel: y=118, h=196
- Arrow centers: y=221 (panel midpoints)

**Method content preserved verbatim:** class 0 (aa)/class 1 (ao)/class 2 (dcl) labels; scores s₁/s₂/s₃; softmax formula P(y=k|x)=exp(sₖ)/Σexp(sⱼ); (n,K) probs / argmax→class / train accuracy / proba (n,K) output.

**XML override tally:** 6 `.mono` elements with `font-size="10"` (class 12) → all DISTINCT → all INTENTIONAL → ZERO strips.

**Gate results:** SVGO idempotence PASS; rsvg-convert PNG non-empty and renders cleanly (three OvR rows well-spaced, no cramping, arrows connect panel centers, all text readable); viewBox `0 0 720 480`, role="img", aria-label preserved; method content grep-confirmed.

---

### scalar-on-function.svg — CHANGED (conservative β̂(t) prominence improvement)

**Pedagogical judgment applied (SVGFIX-04):** The β̂(t) coefficient function inset at the bottom of Panel 3 was previously a small 164×40 rect with a `.sm` class label, secondary to the fitted-vs-actual scatter. The page prose (`docs/regression/scalar-on-function.md:11`) calls β(t) "the object of interest."

**Conservative improvement applied:**
- Rect height enlarged: 40→52px (inset top remains at y≈206, bottom stays within panel)
- Border upgraded: `stroke="#f1c2c8"` → `stroke="#dc3545" stroke-width="1.5"` (matches panel accent color, visually prominent)
- Label promoted: `.sm` → `.lab` class (`β̂(t)` now rendered in 700-weight 13px)
- Added "coefficient function" annotation in `.sm` next to the label
- Coefficient curve: unchanged in shape, stroke-width raised 2→2.2

**Unchanged:** Panel 3 outer rect, position, fitted-vs-actual scatter, all other panels, viewBox (stays 720×300).

**XML override tally:** Zero inline font-size attributes in this file (unchanged from pre-edit).

**Gate results:** SVGO idempotence PASS; rsvg-convert PNG non-empty; renders with β̂(t) label visually prominent alongside the coefficient curve.

**SURFACED FOR PHASE 49 HUMAN REVIEW:** The β̂(t) inset is conservatively improved but still co-located with the fitted-vs-actual scatter in Panel 3. The Phase 49 blocking human review should evaluate whether the coefficient function warrants a dedicated panel at peer prominence with the scatter (a structural decision deferred here per scope). The current state is: β̂(t) occupies the lower 52px of Panel 3 with a red border and bold label; the scatter occupies the upper ~86px of Panel 3.

---

### inference-permutation-test.svg — CONFIRMED BYTE-UNCHANGED

**XML override tally (SVGFIX-03):** Sole inline override: `<text class="mono" ... font-size="11">T_obs</text>` (line 58). Class `.mono`=12; inline value=11; 11 ≠ 12 → INTENTIONAL per-element size reduction for the T_obs observed-statistic label → KEEP.

**Gate results:** SVGO idempotence PASS; rsvg-convert PNG non-empty; viewBox 720×300, role="img", aria-label present.

---

## Redundant-Override Tally (All Four Files)

| File | Inline font-size elements | Stripped (redundant) | Kept (intentional) |
|------|--------------------------|---------------------|---------------------|
| functional-glm.svg | 6 `.mono` at font-size=10 (class=12) | 0 | 6 |
| elastic-multinomial.svg | 6 `.mono` at font-size=10 (class=12) | 0 | 6 |
| scalar-on-function.svg | 0 | — | — |
| inference-permutation-test.svg | 1 `.mono` at font-size=11 (class=12) | 0 | 1 |

**Total strips across Phase 45: ZERO.** All inline values differ from their class value — consistent with the Phase 43/44 precedent that confirmed 5 and then several files byte-unchanged.

---

## No-Churn Guard (15 OK Regression/Inference Diagrams)

`git diff --name-only -- docs/assets/diagrams` at end of phase lists ONLY:
- `docs/assets/diagrams/elastic-multinomial.svg` ✓
- `docs/assets/diagrams/scalar-on-function.svg` ✓

The 15 OK diagrams (function-on-scalar, classification, elastic-regression, scalar-on-shape, concurrent-regression, cross-validation, regression-diagnostics, uncertainty-quantification, explainability, conformal-prediction, conformal-classification, robust-regression, inference-anova, inference-scb, itp-interval-inference) are **byte-unchanged**.

---

## Inference/ Section: No Diagram Commit Required

inference-permutation-test.svg is byte-unchanged (lone font-size=11 intentional). No other inference diagram changed. The inference/ section has no diagram commit — per the Phase 44 precedent where monitoring/advisor had nothing to commit.

---

## Phase 45 Completion: Final Section of 61-Diagram Sweep

This plan completes the full 61-diagram sweep across Phases 43–45:
- **Phase 43:** learn/ + represent/ + align/ (25 diagrams) — complete
- **Phase 44:** analyze/ + monitoring/ + advisor/ (17 diagrams) — complete
- **Phase 45:** regression/ + inference/ (19 diagrams) — complete (this plan)

All AUDIT-01 fix-list items addressed. Any remaining design judgment (scalar-on-function β̂(t) prominence) is surfaced for the Phase 49 blocking human diagram review.

---

## Commits

| Commit | Message | Files |
|--------|---------|-------|
| d2fb3e9 | fix(diagrams): regression/ — elastic-multinomial de-cramp (720x480), scalar-on-function β(t) prominence, functional-glm Gamma-link verified | elastic-multinomial.svg, scalar-on-function.svg |

---

## Deviations from Plan

None — plan executed exactly as written. functional-glm.svg and inference-permutation-test.svg were byte-unchanged as predicted; elastic-multinomial.svg was de-cramped to 720×480 as planned; scalar-on-function.svg received a conservative β̂(t) prominence improvement as planned.

---

## Items for Phase 49 Human Review

1. **scalar-on-function.svg β̂(t) prominence (DESIGN JUDGMENT):** Conservative improvement applied (52px inset, .lab label, red border, "coefficient function" annotation). Phase 49 reviewer should assess whether the coefficient function warrants promotion to a peer-level panel in Panel 3, or whether the current co-location with the fitted-vs-actual scatter adequately communicates that β̂(t) is "the object of interest" per `docs/regression/scalar-on-function.md:11`.

---

## Self-Check: PASSED

- elastic-multinomial.svg exists and modified: VERIFIED
- scalar-on-function.svg exists and modified: VERIFIED
- functional-glm.svg: byte-unchanged: VERIFIED (git diff --quiet passes)
- inference-permutation-test.svg: byte-unchanged: VERIFIED (git diff --quiet passes)
- Commit d2fb3e9 exists: VERIFIED
- No-churn guard: 0 non-flagged SVG changes: VERIFIED
- SVGO idempotence: PASS on all changed files
- rsvg-convert: non-empty PNG on all files
