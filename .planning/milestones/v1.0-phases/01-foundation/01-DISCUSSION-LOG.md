# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-07
**Phase:** 1-Foundation
**Areas discussed:** SVGO toolchain footprint, Test-harness commitment, DOCS_FAST behavior, Enforcement & verification

---

## SVGO Toolchain Footprint

### Install / invocation
| Option | Description | Selected |
|--------|-------------|----------|
| Zero-install via npx | `npx svgo@<pinned>`; no package.json / node_modules; keeps repo Rust/Python; needs network first run | ✓ |
| Commit package.json + lockfile | svgo as devDependency; reproducible/offline but adds Node toolchain | |
| Wrap in Makefile/script | `make lint-svg` ergonomics; still needs one of the above underneath | |

**User's choice:** Zero-install via npx (pin version).

### Linter mode
| Option | Description | Selected |
|--------|-------------|----------|
| Check-only (lint gate) | Fails if not optimized; never rewrites committed SVGs | ✓ |
| Optimize-in-place | Rewrites each SVG to optimized form; diffs on every diagram | |
| Hybrid: optimize once then check | One-time normalization pass, then check-only | |

**User's choice:** Check-only lint gate.

### Enforcement scope
| Option | Description | Selected |
|--------|-------------|----------|
| Optimization-safety only | Preserve style/IDs/desc/viewBox/aria (FND-02); style-spec conformance = human review | ✓ |
| Add lightweight spec checks | Also assert viewBox 720, allowed heights, role/aria/desc present | |
| You decide | Claude recommends leanest guarding | |

**User's choice:** Optimization-safety only.
**Notes:** STYLE_SPEC conformance (viewBox width, allowed heights, class names) stays a human review-gate concern this phase.

---

## Test-Harness Commitment

### Handling the cross-fence state risk
| Option | Description | Selected |
|--------|-------------|----------|
| Smoke-test first, then lock | Validate pytest-markdown-docs cross-fence state on one real page before committing | ✓ |
| Commit to it outright | Trust FND-05; wire it up; deal with issues in Phase 9 | |
| Custom conftest fence-exec | Skip plugin; own harness guaranteeing shared per-page state | |

**User's choice:** Smoke-test first, then lock.
**Notes:** STATE.md flagged this exact risk (var defined in one fence, used in the next).

### Fallback if smoke-test fails
| Option | Description | Selected |
|--------|-------------|----------|
| Custom conftest fence-exec | Own harness execing all fences in one shared namespace | |
| Consolidate fences per page | Authoring convention: runnable code self-contained per fence/page | |
| You decide at the time | Pick based on how pytest-markdown-docs actually fails | ✓ |

**User's choice:** You decide at the time (candidate space = custom conftest fence-exec OR consolidate-fences).

### Smoke-test target page
| Option | Description | Selected |
|--------|-------------|----------|
| canadian-weather.md | 8 fences, canonical dataset, representative | |
| canadian-seasonal.md | 9 fences, strongest multi-block stress | |
| You decide | Planner picks page with genuine early-define/late-use state dependency | ✓ |

**User's choice:** You decide (state-dependency over fence count).

---

## DOCS_FAST Behavior

### May fast mode change figure output?
| Option | Description | Selected |
|--------|-------------|----------|
| Speed-only, output may differ | Local convenience; figures may look rougher; full build is source of truth | ✓ (Claude, on "you decide") |
| Must stay visually identical | Only reduce cost without changing look; limits which knobs qualify | |
| You decide | Claude recommends | ✓ |

**User's choice:** You decide → Claude locked "speed-only, output may differ; full build is source of truth; FND-03 determinism only required in full build."

### Wiring
| Option | Description | Selected |
|--------|-------------|----------|
| Central helper in docs_fig.py | Reads DOCS_FAST once; pages call it; DRY | ✓ (Claude, on "you decide") |
| Per-block os.environ checks | Scattered inline branches | |
| You decide | Claude picks DRY approach | ✓ |

**User's choice:** You decide → Claude locked central helper in `docs_fig.py`.

---

## Enforcement & Verification

### CI wiring timing
| Option | Description | Selected |
|--------|-------------|----------|
| Create + verify manually now | Deliver configs, verify locally, defer CI wiring | |
| Wire into CI now | Add SVGO lint + doc-tests to CI this phase; gated from day one | ✓ |
| CI-ready but off | Build job defs, leave non-blocking until sweeps begin | |

**User's choice:** Wire into CI now.

### Doc-test gate scope (examples not fixed until Phase 9)
| Option | Description | Selected |
|--------|-------------|----------|
| Gate grows with coverage | SVGO blocks all diagrams now; doc-tests block only smoke page now, expand as Phase 9 fixes each | ✓ |
| Doc-tests non-blocking until Phase 9 | Informational/allow-failure now; flip to required after Phase 9 | |
| Gate all pages now | Blocking on every example immediately (pulls Phase 9 work forward) | |

**User's choice:** Gate grows with coverage.
**Notes:** Keeps CI green through Phases 1–8 without prematurely fixing examples.

---

## Claude's Discretion

- Test-harness fallback selection (if smoke-test fails) — decided at the time.
- Smoke-test page selection — planner's choice among state-dependent pages.
- DOCS_FAST semantics + wiring — Claude decided on "you decide"; locked in CONTEXT.md.
- `pymdownx.snippets` / `docs/includes/` organization — standard approach, planner discretion.
- Pre-commit hooks — optional; CI is the agreed gate.
- Determinism mechanics (svg.hashsalt, RNG seeding) — standard implementation.

## Deferred Ideas

- A11Y-01: long-form `<title>`/`<desc>` + `aria-labelledby` for complex diagrams — v2.
- EX2-01: editorial consolidation of overlapping example pages — v2.
- Method-semantic accuracy research (β(t), conformal bands, SPM Phase I/II) — Phases 7–8.
- Fixing all example pages against current API — Phase 9 (deliberately out of Phase 1's doc-test gate scope).
