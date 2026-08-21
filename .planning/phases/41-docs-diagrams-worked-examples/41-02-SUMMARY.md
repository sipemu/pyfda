---
phase: 41-docs-diagrams-worked-examples
plan: "02"
subsystem: docs/regression + docs/represent
tags: [docs, svg, markdown-exec, classification, fpca, elastic-multinomial, pace-fpca]
depends_on:
  requires: [41-01]
  provides: [pace-fpca.md, classification-elastic-multinomial-section, pace-fpca.svg, elastic-multinomial.svg]
  affects: [mkdocs.yml, docs/regression/classification.md]
tech_stack:
  added: []
  patterns:
    - hand-authored inline SVG (STYLE_SPEC-conformant)
    - markdown-exec exec fence with FDARS_FENCE_OK sentinel
    - SVGO@3.3.4 idempotence gate
key_files:
  created:
    - docs/represent/pace-fpca.md
    - docs/assets/diagrams/pace-fpca.svg
    - docs/assets/diagrams/elastic-multinomial.svg
  modified:
    - docs/regression/classification.md
    - mkdocs.yml
decisions:
  - "Task 1 (PACE-FPCA page + SVG + nav) was done by a prior stalled agent and salvaged intact in commit 6418cc3; resume agent verified correctness and did not rewrite it"
  - "Task 2 fence initially used 240 obs (80 per class) which ran correctly in the built site (confirmed FDARS_FENCE_OK in HTML from prior build); updated to 20 obs per class (60 total) per plan's fallback guidance to keep elastic computation fast for future builds"
  - "Direct Python execution of the fence (PYTHONPATH=scripts) confirmed FDARS_FENCE_OK for both the n=60 (updated) and n=240 (built site evidence) versions"
  - "Task 3 SVGO idempotence verified before Task 2 commit — no separate Task 3 commit needed (verification-only task)"
metrics:
  duration: "~4 hours (cross-session, resumed from stalled agent)"
  completed: "2026-08-21"
  tasks_completed: 3
  commits: 1
status: complete
requirements: [DOCS-09]
actuals:
  tokens: 38000
  tasks: 3
  commits: 1
---

# Phase 41 Plan 02: DOCS-09 FPCA & Classification Summary

One new documentation page `docs/represent/pace-fpca.md` (PACE-FPCA for sparse irregular data) and a new section appended to `docs/regression/classification.md` (elastic multinomial classification), each with a method-accurate hand-authored inline SVG and an executed offline fence emitting `FDARS_FENCE_OK`.

## What Was Built

### Task 1: PACE-FPCA page — tracer (done by prior agent, commit 6418cc3)

**`docs/represent/pace-fpca.md`** — documents `fdars.irreg_fdata_from_lists` → `fdars.pace_fpca`:
- H1 "PACE — FPCA for Sparse, Irregular Data" with intro framing the PACE algorithm
- SVG included via `../assets/diagrams/pace-fpca.svg` with `.fdars-diagram` attribute
- KaTeX theory: Karhunen-Loeve expansion; PACE covariance surface estimation + conditional expectation for scores
- Parameter table for both functions (irreg_fdata_from_lists: argvals_list, values_list; pace_fpca: data handle, ncomp, bandwidth, sigma2, work_grid, alpha)
- Returns table (10 keys): mean, eigenvalues, eigenfunctions (m, ncomp), scores, fitted/lower/upper, argvals, sigma2, ncomp
- Admonition: eigenfunctions is (m, ncomp) — column k is the k-th eigenfunction; actual ncomp may be < requested
- Note (Pitfall 3): irreg_fdata_from_lists requires two Python lists of 1-D arrays and rejects 2-D numpy arrays
- Exec fence (n=15 sparse curves, 5-8 obs each, ragged grids) producing `FDARS_FENCE_OK`

**`docs/assets/diagrams/pace-fpca.svg`** — STYLE_SPEC-conformant SVG:
- viewBox "0 0 720 300", fill="none", role="img", aria-label, canonical 5-class style block
- Left panel: 5 curves shown as scattered dots at DIFFERENT x-positions per curve (ragged per-curve grids — method-accurate)
- Right panel: 2 smooth eigenfunction curves on the common 51-pt work grid (smooth recovery, NOT raw data resampled)
- PACE mean shown as dashed orange curve on left panel
- Central arrow labelled "PACE" conveying the recovery direction
- SVGO@3.3.4 idempotent: PASSED

**`mkdocs.yml`**: "PACE FPCA: represent/pace-fpca.md" added after "Elastic FPCA: represent/elastic-fpca.md" in Represent nav section.

Commit: `6418cc3`

### Task 2: Elastic Multinomial section in classification.md (commit 8e758aa)

**`docs/regression/classification.md`** — new `## Elastic Multinomial Classification` section appended:
- Short intro (K-class OvR elastic classifier in the SRSF/elastic domain)
- SVG included via `../assets/diagrams/elastic-multinomial.svg` with `.fdars-diagram` attribute
- Theory paragraph with softmax formula
- Parameter table (data, labels dtype int64, argvals, ncomp_beta, lambda_, max_iter, tol)
- Returns table (n_classes, classes, train_probabilities (n,K), predicted_classes, train_accuracy)
- Admonition (Pitfall 7): labels must be 0-indexed contiguous int64; negative or non-contiguous labels raise ValueError
- Exec fence: phoneme aa/ao/dcl (3 classes, 20 obs/class=60 total, m=64 columns); direct execution confirmed `FDARS_FENCE_OK`; built site evidence also confirms `FDARS_FENCE_OK` (from prior build with 80 obs/class=240 total — both versions work)

**`docs/assets/diagrams/elastic-multinomial.svg`** — STYLE_SPEC-conformant SVG:
- viewBox "0 0 720 300", fill="none", role="img", aria-label, canonical 5-class style block
- Input functional data panel (left, neutral)
- K=3 OvR binary classifier panel (orange accent): 3 rows each showing one OvR model with distinct class colours (indigo/orange/green) and score s₁/s₂/s₃
- Softmax aggregation panel showing exp(sₖ)/Σexp(sⱼ) formula
- Output panel showing predicted classes, train accuracy, probabilities (n, K)
- Conveys the one-vs-rest + softmax structure explicitly — NOT LDA
- SVGO@3.3.4 idempotent: PASSED

Commit: `8e758aa`

### Task 3: SVGO-idempotence gate (verification-only, no separate commit)

Both new SVGs passed the svgo@3.3.4 idempotence check:
- `pace-fpca.svg`: IDEMPOTENT (byte-identical second pass)
- `elastic-multinomial.svg`: IDEMPOTENT (byte-identical second pass)
- Neither SVG contains embedded timestamp/date metadata

## Verification Evidence

### Task 1 (PACE-FPCA page)

Built site (prior build b3tm2c1ij, exit 0, 3061s):
- `site/represent/pace-fpca/index.html` contains `FDARS_FENCE_OK`
- `pace-fpca.svg` referenced in built HTML

### Task 2 (Elastic Multinomial)

Direct Python execution (PYTHONPATH=scripts):
```
X3: (60, 64) y3 dtype: int64 unique: [0 1 2]
n_classes= 3
train_accuracy= 1.0
proba shape: (60, 3)
FDARS_FENCE_OK
```

Built site (b3tm2c1ij with original 240-obs code, exit 0):
```
n_classes=3  train_accuracy=1.000
train_probabilities shape: (240, 3)
FDARS_FENCE_OK
```

MULTINOM_OK verification:
```bash
grep -q "elastic-multinomial.svg" site/regression/classification/index.html && echo SVG_REF_OK  # => SVG_REF_OK
grep -c FDARS_FENCE_OK site/regression/classification/index.html  # => 2 (>= 1 passes)
echo MULTINOM_OK  # => MULTINOM_OK
```

### Task 3 (SVGO)

```
IDEMPOTENT: docs/assets/diagrams/pace-fpca.svg
IDEMPOTENT: docs/assets/diagrams/elastic-multinomial.svg
```

### API facts confirmed (from direct execution)

- `irreg_fdata_from_lists` requires Python lists of 1-D arrays (not 2-D numpy arrays) — confirmed by Pitfall 3 guard in src/pace_fpca_mod.rs
- `pace_fpca` returns eigenfunctions shape (m, ncomp) — column k is the k-th eigenfunction
- `elastic_multinomial` requires labels dtype int64 with 0-indexed contiguous values — confirmed by Pitfall 7 guard
- `elastic_multinomial` returns train_probabilities (n, K) — shape confirmed
- phoneme.csv has 5 classes each with 80 rows (aa, ao, dcl, iy, sh)

## Deviations from Plan

### Task 1 done by prior agent (salvaged, not rewritten)

The prior stalled agent committed `docs/represent/pace-fpca.md`, `docs/assets/diagrams/pace-fpca.svg`, and the `mkdocs.yml` nav entry in commit `6418cc3`. The resume agent verified all acceptance criteria and treated Task 1 as complete without rewriting.

### Fence row-count update (deviation from blueprint)

The plan's DOCS-09 blueprint used all 240 phoneme observations (80 per class × 3 classes). The fence was updated to 20 observations per class (60 total) after direct testing showed elastic alignment takes >120s with 240 obs. Both versions are confirmed to produce `FDARS_FENCE_OK` — the built site shows the 240-obs run succeeded; the direct test confirms the 60-obs run also succeeds. This is consistent with the plan's A4 fallback guidance.

## Known Stubs

None. Both fences execute against the shipped fdars bindings and produce FDARS_FENCE_OK.

## Threat Flags

None — DOCS-ONLY plan; fences use only in-process phoneme CSV data and synthetic sparse data with no I/O, no secrets.

## Self-Check: PASSED

- [x] `docs/represent/pace-fpca.md` exists (commit 6418cc3)
- [x] `docs/assets/diagrams/pace-fpca.svg` exists, SVGO-idempotent (commit 6418cc3)
- [x] `mkdocs.yml` has "PACE FPCA" entry after "Elastic FPCA" (commit 6418cc3)
- [x] `docs/regression/classification.md` has `## Elastic Multinomial Classification` section (commit 8e758aa)
- [x] `docs/assets/diagrams/elastic-multinomial.svg` exists, SVGO-idempotent (commit 8e758aa)
- [x] PACE-FPCA fence: `grep -q FDARS_FENCE_OK site/represent/pace-fpca/index.html` passes
- [x] Elastic-multinomial fence: direct execution confirmed `FDARS_FENCE_OK`; built HTML confirms `FDARS_FENCE_OK`
- [x] MULTINOM_OK verification passes: `elastic-multinomial.svg` in built HTML + FDARS_FENCE_OK count >= 1
- [x] Both SVGs: SVGO@3.3.4 idempotent, no timestamp metadata
- [x] No `src/*.rs` files modified
- [x] Built site `mkdocs build --strict` exit 0 (confirmed from prior build b3tm2c1ij)
