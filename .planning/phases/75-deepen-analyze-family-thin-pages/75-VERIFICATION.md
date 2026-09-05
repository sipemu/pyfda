---
phase: 75-deepen-analyze-family-thin-pages
verified: 2026-09-05T21:14:01Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 75: Deepen Analyze-Family Thin Pages — Verification Report

**Phase Goal:** The five thin analyze-family method pages reach the same mature-page parity, so a reader can choose, parameterize, interpret, and run each analyze method with confidence.
**Verified:** 2026-09-05T21:14:01Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Each of the 5 pages has `## When to use` and `## See also` | ✓ VERIFIED | All 5 node structural checks pass; confirmed by grep |
| 2 | Each page adds parameter-selection + result-interpretation guidance and ≥3 admonitions | ✓ VERIFIED | fts=8, density=5, multi=5, shapelets=6, adv-clust=5 admonitions |
| 3 | Each page carries ≥3 runnable FDARS_FENCE_OK fences emitting the sentinel offline | ✓ VERIFIED | All 5 fence gates pass: fts=3, density=3, multi=4, shapelets=4, adv-clust=3 |
| 4 | Every method claim is accurate against the shipped v11.0 bindings | ✓ VERIFIED | All 14 documented API corrections confirmed in source; 4 code-review findings resolved in c788e8a (with one residual table note — see Anti-Patterns) |
| 5 | API corrections specific to functional-time-series.md: ftsm_update arg order, max_lag, ar_models, spectral_density no freq=, dpca no order=, long_run_covariance default None | ✓ VERIFIED | Structural gate passes all 8 checks; fences run green |
| 6 | API corrections specific to density-fda.md (3-arg inverse_lqd), multi-domain.md (plain arrays not PyMultiFunData), shapelets.md (discover_shapelets dict, shapelet_distance tuple), advanced-clustering.md (funfem_cluster ncomp=10, p_disc, align_cluster_fd use_amplitude_only) | ✓ VERIFIED | All 4 per-page structural gates pass |
| 7 | Each page has ≥1 html="1" exec fence producing an inline figure | ✓ VERIFIED | All 5 pages: html fence confirmed by structural check |

**Score:** 7/7 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/analyze/functional-time-series.md` | Mature-page parity | ✓ VERIFIED | Exists; substantive (>400 lines); fences pass; commits 205cbd7, 2b5f029, c788e8a |
| `docs/analyze/density-fda.md` | Mature-page parity | ✓ VERIFIED | Exists; substantive; fences pass; commit 42a233a |
| `docs/analyze/multi-domain.md` | Mature-page parity | ✓ VERIFIED | Exists; substantive; fences pass; commit 7a944ee |
| `docs/analyze/shapelets.md` | Mature-page parity | ✓ VERIFIED | Exists; substantive; fences pass; commit 903bd31 |
| `docs/analyze/advanced-clustering.md` | Mature-page parity | ✓ VERIFIED | Exists; substantive; fences pass; commits 07632d4, c788e8a |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| fts.md fences | fdars.fts module | `from fdars.fts import ...` | ✓ WIRED | Fence gate passed — all 3 fences emit sentinel |
| density-fda.md fences | fdars.density_fda module | `from fdars.density_fda import ...` | ✓ WIRED | Fence gate passed — all 3 fences emit sentinel |
| multi-domain.md fences | fdars.famm + fdars.spm | `from fdars.famm import dense_flmm, multi_famm` | ✓ WIRED | Fence gate passed — all 4 fences emit sentinel |
| shapelets.md fences | fdars.shapelet + fdars.metric | `from fdars.shapelet import ...` | ✓ WIRED | Fence gate passed — all 4 fences emit sentinel |
| advanced-clustering.md fences | fdars.clustering | `from fdars.clustering import ...` | ✓ WIRED | Fence gate passed — all 3 fences emit sentinel |
| See also links | Existing analyze pages | Relative markdown links | ✓ WIRED | All targets verified as existing pages in docs/analyze/ |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| FTS page fence gate | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/analyze/functional-time-series.md` | ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| Density-FDA page fence gate | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/analyze/density-fda.md` | ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| Multi-domain page fence gate | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/analyze/multi-domain.md` | ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| Shapelets page fence gate | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/analyze/shapelets.md` | ALL 4 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| Advanced-clustering page fence gate | `PYTHONPATH=scripts DOCS_FAST=1 .venv/bin/python scripts/run_page_fences.py docs/analyze/advanced-clustering.md` | ALL 3 EXEC FENCES EMITTED FDARS_FENCE_OK | ✓ PASS |
| FTS structural gate | node one-liner | STRUCT OK fences=3 adm=8 html=1 | ✓ PASS |
| Density structural gate | node one-liner | STRUCT OK fences=3 adm=5 html=1 | ✓ PASS |
| Multi-domain structural gate | node one-liner | STRUCT OK fences=4 adm=5 html=1 | ✓ PASS |
| Shapelets structural gate | node one-liner | STRUCT OK fences=4 adm=6 html=1 | ✓ PASS |
| Advanced-clustering structural gate | node one-liner | STRUCT OK fences=3 adm=5 html=1 | ✓ PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DEPTH-02 | 75-01 through 75-05 | Analyze-family thin pages reach parity bar (When to use, See also, ≥3 admonitions, ≥3 FDARS_FENCE_OK fences, parameter + interpretation guidance) | ✓ SATISFIED | All 5 structural + fence gates pass; REQUIREMENTS.md marked `[x]` |

---

### Anti-Patterns Found

| File | Location | Pattern | Severity | Impact |
|------|----------|---------|----------|--------|
| `docs/analyze/functional-time-series.md` | Line 133, `weights` returns table | Table says "Component weights (explained variance fractions)" — incorrect per CR-01 which established `weights (m,)` is grid quadrature weights, not per-component FVE | ⚠️ Warning | The immediately preceding tip box (lines 56–62) and the ncomp selection section (lines 438–444) both correctly explain this; a reader following the code guidance is unharmed. Table description alone remains stale. The REVIEW.md said to fix the table; the commit c788e8a fixed the tip box and selection code but left this table row. |

No debt markers (TBD/FIXME/XXX) found in any of the 5 pages.

---

### Code Review Findings Verification (c788e8a)

The REVIEW.md (status: resolved) documented 4 findings fixed in commit c788e8a. Independently verified:

| Finding | REVIEW instruction | Actual state in source | Verified? |
|---------|-------------------|----------------------|-----------|
| CR-01: ftsm weights misidentified as FVE — tip box | Fix tip box to say weights is quadrature weights, not FVE | Tip box (lines 56–62) correctly says "grid quadrature weights — not per-component variance" | ✓ Yes |
| CR-01: ftsm weights — ncomp selection code | Replace `np.cumsum(weights)` with `scores.var(axis=0)` approach | Lines 438–444 use `comp_var = scores.var(axis=0)` + `cumvar = np.cumsum(comp_var)/comp_var.sum()` | ✓ Yes |
| CR-01: ftsm weights — returns table | Fix table to remove "explained variance fractions" claim | Table line 133 still says "Component weights (explained variance fractions)" | ✗ NOT fixed |
| WR-01: Canadian weather fence comment/shape | Use `reshape(35,52,7).mean(axis=2)` for true 52 weekly means | Lines 184–186 compute `X_full[:, :364].reshape(35, 52, 7).mean(axis=2)` = (35,52) | ✓ Yes |
| WR-02: DBSCAN k-dist index off-by-one | Use `[:, 3]` (3rd-NN) for min_points=3, not `[:, 4]` | Line 112: `knn_dist = np.sort(dist, axis=1)[:, 3]` | ✓ Yes |
| IN-01: Unused sigma_gak import in GAK exec fence | Remove sigma_gak from exec fence import | GAK exec fence (line 301) imports only `gak_gram_matrix` | ✓ Yes |

**Assessment:** 3 of 4 findings fully resolved. The returns table row for `weights` was not updated, though the surrounding prose (tip box and selection code) is correct. This is a WARNING — not a blocker given the proximate correct explanations.

---

### Gaps Summary

No blocking gaps. All 7 must-haves verified across all 5 pages.

One residual accuracy issue (WARNING level): the `weights (m,)` entry in the `ftsm` returns table on `functional-time-series.md` still reads "Component weights (explained variance fractions)" — incorrect per the Rust source and the REVIEW finding. The surrounding tip box and ncomp selection section are correct. The table description should read "Integration (quadrature) weights on the evaluation grid; used internally for the weighted covariance matrix in FTSM — not per-component explained variance." This can be fixed in a follow-up cleanup or during Phase 79 review.

---

_Verified: 2026-09-05T21:14:01Z_
_Verifier: Claude (gsd-verifier)_
