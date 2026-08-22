---
phase: 41
slug: docs-diagrams-worked-examples
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-21
---

# Phase 41 — Validation Strategy

> Per-phase validation contract. DOCS-ONLY phase — validation is the docs build + SVG gates + human review, not pytest.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `mkdocs build --strict` (build-time fence execution via `markdown-exec`) + SVGO idempotence + `rsvg-convert` PNG render |
| **Config file** | `mkdocs.yml` |
| **Quick run command** | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/mkdocs build --strict` (fast iteration per page) |
| **Full suite command** | `PYTHONPATH=scripts .venv/bin/mkdocs build --strict` (no DOCS_FAST — the source-of-truth gate, ~19 min) |
| **SVGO** | `npx svgo@3.3.4 --config svgo.config.mjs` (idempotence — run twice, byte-identical) |
| **Human review** | `rsvg-convert new.svg -o new.png` → visual method-accuracy check |

---

## Sampling Rate

- **Per page (41-01..03):** `DOCS_FAST=1` strict build of the affected page(s) + `grep FDARS_FENCE_OK` in the built HTML; SVGO idempotence on each new SVG as it's authored.
- **Phase gate (41-04):** the FULL `mkdocs build --strict` (no DOCS_FAST, ~19 min) exits 0 with every new fence's `FDARS_FENCE_OK` present, all new SVGs SVGO-idempotent + determinism-clean, THEN the blocking human diagram review.
- **Build-cost note:** run the expensive full build ONCE in 41-04, not per plan. Use DOCS_FAST for 41-01..03 iteration.

---

## Per-Requirement Validation Map

| Req ID | Behavior | Automated Check |
|--------|----------|-----------------|
| DOCS-08 | concurrent-regression + functional-glm pages render; each fence emits `FDARS_FENCE_OK`; Gamma inverse-link + AIC caveat documented; nav wired | `DOCS_FAST=1 mkdocs build --strict` + grep FDARS_FENCE_OK |
| DOCS-09 | pace-fpca page (synthetic sparse fence, n ≤ 20) + elastic_multinomial in classification.md (phoneme 3-class, m ≤ 64); each fence emits FDARS_FENCE_OK; nav wired | `DOCS_FAST=1 mkdocs build --strict` + grep |
| DOCS-10 | 9 depth methods folded into depth-functions.md; 4 outlier detectors in outlier-detection.md; interval-inference.md (itp_*); each fence FDARS_FENCE_OK; nav wired | `DOCS_FAST=1 mkdocs build --strict` + grep |
| DOCS-11 | advisor/aspects.md updated (extended outliers/regression/classification/fpca diagnostics); whole-site `mkdocs build --strict` (no DOCS_FAST) exit 0; every new SVG SVGO-idempotent + determinism-clean | full `mkdocs build --strict` + SVGO twice |
| DOCS-11 | BLOCKING human diagram method-accuracy review (depth asymmetry, PACE irregular observations, ITP closure direction) | `rsvg-convert` each new SVG → PNG; user visual approval (NOT auto) |

*Status: ⬜ pending · ✅ green · ❌ red*

---

## Wave 0 Requirements

None — docs-only. No test files. The "tests" are executed fences + the strict build + SVG gates.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Diagram method-accuracy (7 new SVGs) | DOCS-11 | Faithfulness of a hand-authored concept diagram to the method cannot be auto-checked — it requires human judgment | `rsvg-convert docs/assets/diagrams/<new>.svg -o /tmp/<new>.png`; user inspects: depth hypograph/epigraph asymmetry, PACE ragged-obs→smooth-eigenfns, ITP closure-adjusted intervals (adjusted ≤ raw, correct closure direction), concurrent-regression time-varying β(t) curves |

*This is the blocking human gate — the orchestrator PAUSES here.*

---

## Validation Sign-Off

- [ ] All new fences emit `FDARS_FENCE_OK` (grep the built HTML)
- [ ] Whole-site `mkdocs build --strict` (no DOCS_FAST) exit 0
- [ ] Every new SVG SVGO-idempotent (run twice, byte-identical) + determinism-clean
- [ ] All new pages wired into mkdocs.yml nav
- [ ] Advisor aspects.md updated for the v6.0 diagnostics
- [ ] BLOCKING human diagram method-accuracy review approved
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
