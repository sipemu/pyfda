---
phase: 75-deepen-analyze-family-thin-pages
reviewed: 2026-09-05T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - docs/analyze/functional-time-series.md
  - docs/analyze/density-fda.md
  - docs/analyze/multi-domain.md
  - docs/analyze/shapelets.md
  - docs/analyze/advanced-clustering.md
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: resolved
resolution: All 4 findings fixed 2026-09-05 — CR-01 (ftsm weights≠FVE; ncomp guidance now uses score variances), WR-01 (true 35×52 weekly means via reshape), WR-02 (DBSCAN k-dist index 4→3 for min_points=3), IN-01 (dropped unused sigma_gak import). Fence gates re-run green on all 3 touched pages.
---

# Phase 75: Code Review Report

**Reviewed:** 2026-09-05
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Five analyze-family documentation pages were reviewed against the verified API surface in
`75-RESEARCH.md` (all function signatures, parameter names, defaults, and return keys
verified from Rust binding sources). The phase successfully corrected all 14 known
pre-existing API discrepancies documented in the research (FTS arg orders, density-fda
`inverse_lqd` signature, multi-domain FAMM array vs handle, shapelets return types, etc.).
The corrected prose and fences are accurate for those known issues.

Three new issues were found: one critical (incorrect ncomp-selection guidance in
`functional-time-series.md` treats grid-point quadrature weights as per-component FVE),
one warning each for an inaccurate comment in the Canadian weather fence and a
one-off NN index in the DBSCAN eps-selection fence. One info item (unused import in a GAK
fence) rounds out the findings.

No API name, parameter name, or return key errors were found beyond those already fixed by
the phase. All exec fences contain `FDARS_FENCE_OK` sentinels. All pages have ≥3 exec
fences. The multi-domain, density-fda, shapelets, and advanced-clustering pages are clean
at Critical and Warning severity.

---

## Critical Issues

### CR-01: `ftsm` weights `(m,)` misidentified as per-component FVE — ncomp selection guidance is wrong

**File:** `docs/analyze/functional-time-series.md:57-60` and `docs/analyze/functional-time-series.md:434-441`

**Issue:** The `ftsm` return dict includes `weights (m,)` — a vector of integration
quadrature weights over the `m` evaluation grid points, not a per-component explained
variance array. The Rust source (`src/fts_mod.rs:73`) confirms the key is populated from
`result.weights` and the doc comment at line 38 says "weights (n_points,)".

The page makes two errors from this misidentification:

1. The `!!! tip "Choosing ncomp"` admonition (lines 57–60) claims "`weights`… gives
   the fraction of variance each component explains (analogous to FVE in standard FPCA)".
   This is false — with `m=30` grid points and `ncomp=3` components, a `(30,)` array
   cannot represent "fraction of variance per component".

2. The `### Choosing ncomp` code example (lines 438–441) applies `np.cumsum(weights)` to
   the `(m,)` array and thresholds against 0.85–0.90 to pick `ncomp`:
   ```python
   weights = np.asarray(fit["weights"])
   cumvar  = np.cumsum(weights)             # cumsum over 30 grid pts, NOT 3 components
   ncomp_choice = int(np.argmax(cumvar >= 0.90)) + 1  # returns a grid-point index
   ```
   For typical data with `m=30` and quadrature weights summing to ~1.0 over [0,1], the
   cumsum reaches 0.90 around grid point 27, returning `ncomp_choice ≈ 27` — a
   nonsensical component count. A user following this guidance would over-fit severely.

Note that the `ftsm` result does **not** expose per-component FVE or eigenvalues directly;
the page's stated goal of guiding `ncomp` selection via `weights` is not achievable with
the current API surface. A correct alternative is to inspect the variance of each score
column or rely on domain knowledge.

**Fix:**
```python
# REMOVE the cumsum guidance. Replace with a correct approach:

# Option 1: inspect score column variances as a proxy for per-component contribution
scores = np.asarray(fit["scores"])          # (n, ncomp)
col_var = np.var(scores, axis=0)            # (ncomp,) — variance per component
cumvar  = np.cumsum(col_var) / col_var.sum()
ncomp_choice = int(np.argmax(cumvar >= 0.90)) + 1

# Option 2 (simpler guidance): use the default ncomp=3 or increase ncomp
# and re-run ftsm, watching whether forecast quality (held-out MAE) improves.
```

Also update the tip box (lines 57–60) and the returns table (line 131) to remove the claim
that `weights` gives per-component explained variance. The correct description for
`weights (m,)` is "integration weights on the evaluation grid (used internally for the
weighted covariance matrix in FTSM)".

---

## Warnings

### WR-01: Canadian weather fence claims "35 × 52 weekly means" but slice produces (35, 53)

**File:** `docs/analyze/functional-time-series.md:183-201`

**Issue:** The fence uses `data = X_full[:, ::7]` to subsample the 365-column Canadian
weather array. A step-7 slice of 365 elements yields 53 values (indices 0, 7, 14, …, 364
— confirmed by `len(range(0, 365, 7)) == 53`), not 52 as stated.

Two places contain the wrong count:
- Line 184 comment: `# Subsample to weekly means: 35 obs × 52 weekly means for build speed`
- Lines 197–200 admonition: `"weekly means, 35 × 52"` and `"weekly means (35 × 52)"`.

Additionally, `::7` is subsampling (taking every 7th day), not computing weekly means
(which would require averaging within each 7-day window). The label "weekly means" is
therefore factually wrong.

The fence's `print(f"data shape: {data.shape} …")` will emit `(35, 53)` at runtime,
directly contradicting the surrounding prose.

**Fix:**
```python
# Line 184 comment:
# Subsample to every-7th-day: 35 obs × 53 time points for build speed

# Admonition body (lines 198-200):
# The full Canadian weather dataset is 35 × 365 (daily). Using `data[:, ::7]` (every
# 7th day, 35 × 53) keeps fence time well under one second while preserving the seasonal
# structure. This is a subsampling step, not a mean — for proper weekly means use
# `data.reshape(35, -1, 7)[:, :52, :].mean(axis=2)` (52 full weeks × 7 days).
# For production analysis use the full daily resolution.
```

### WR-02: DBSCAN eps-selection fence uses 4th-NN column for `min_points=3` — off by one

**File:** `docs/analyze/advanced-clustering.md:110-118`

**Issue:** The eps-selection fence (and the accompanying `!!! tip`) instructs users to
look at the 4th-nearest-neighbour distance to choose `eps` for a DBSCAN call with
`min_points=3`. Concretely:

```python
knn_dist = np.sort(dist, axis=1)[:, 4]   # col[4] = 4th NN (self is at col[0])
```

The standard DBSCAN elbow guidance is: sort by the `min_points`-th nearest neighbour
(excluding self). With the distance matrix sorted so that `col[0] = self (0.0)`, the
`min_points`-th NN is at `col[min_points]` = `col[3]`, not `col[4]`. Using `col[4]`
corresponds to `min_points=4` and systematically overestimates `eps` relative to the
`min_points=3` setting in the fence. A user who follows this guidance and applies the
returned `eps` to `dbscan_fd` with `min_points=3` will get fewer, larger clusters (some
true noise points absorbed as core-reachable).

The same off-by-one appears in the `75-RESEARCH.md` template code at line 901 (the
research doc originated the error and the phase implementation copied it faithfully).

**Fix:**
```python
# Correct: use col[min_points] when col[0] = self-distance = 0.0
min_pts = 3
knn_dist   = np.sort(dist, axis=1)[:, min_pts]   # 3rd-NN distance (excl self)
knn_sorted = np.sort(knn_dist)

# Also update title/label:
ax.set(title="3rd-NN distance (sorted): eps selection guide for min_points=3",
       xlabel="observation rank", ylabel="3rd-NN L² distance")
```

Also update the `!!! tip` text (line 125) from "Sort the 4th-nearest-neighbour distances
(or min_points-th NN distances)" to "Sort the `min_points`-th nearest-neighbour distances"
(and resolve the ambiguity by using `min_points` directly in code).

---

## Info

### IN-01: Unused `sigma_gak` import in GAK fence

**File:** `docs/analyze/shapelets.md:301`

**Issue:** The GAK exec fence imports `sigma_gak` from `fdars.metric` but never calls it:

```python
from fdars.metric import sigma_gak, gak_gram_matrix   # sigma_gak unused
```

The fence calls `gak_gram_matrix(X, sigma=None)` which triggers the heuristic internally.
The import of `sigma_gak` is dead code in the fence and may confuse readers who wonder why
it is imported if not used.

**Fix:** Remove `sigma_gak` from the fence's import line, or add a call that demonstrates
the heuristic explicitly:

```python
# Option A — remove unused import:
from fdars.metric import gak_gram_matrix

# Option B — show sigma_gak explicitly to teach the pattern:
from fdars.metric import sigma_gak, gak_gram_matrix
sig = sigma_gak(X)        # heuristic bandwidth
K   = gak_gram_matrix(X, sigma=sig)
```

Option B is more instructive since it exposes how `sigma=None` works under the hood.

---

_Reviewed: 2026-09-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
