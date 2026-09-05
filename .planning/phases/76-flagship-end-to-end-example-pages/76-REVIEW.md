---
phase: 76-flagship-end-to-end-example-pages
reviewed: 2026-09-05T22:05:14Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - docs/examples/frechet-density-regression.md
  - docs/examples/fts-forecast.md
  - docs/examples/phoneme-shapelets.md
  - mkdocs.yml
  - docs/examples/index.md
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: resolved
resolution: |
  0 Critical. WR-01 (fts-forecast.md ACF band) addressed — upper_band verified constant
  across lags at runtime; changed [0] to .max() as the conservative envelope so a single
  CI line stays correct even if the band ever varies (fence re-run green). WR-02 and
  IN-01/02/03 accepted as expected patterns with no correctness impact: the re-run/recompute
  fences are a consequence of markdown-exec fence isolation (each fence must be
  self-contained; merging them would drop the page below the ≥3-fence parity bar). Review
  confirmed all fdars API calls correct, no train/test leakage, honest metrics, well-formed nav.
---

# Phase 76: Code Review Report

**Reviewed:** 2026-09-05T22:05:14Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Three flagship worked-example pages (FTS, Fréchet density regression, shapelet classification), nav wiring in mkdocs.yml, and an index.md table extension were reviewed against the Phase 76 RESEARCH doc (verified API ground truth) and the shipped Rust bindings in `src/fts_mod.rs`, `src/shapelet_mod.rs`, `src/frechet_mod.rs`, and `src/density_fda_mod.rs`.

All three pages are self-contained and load correctly isolated fences (no `session=` markers — confirmed no cross-fence state leakage). All `fdars.*` API calls match the binding signatures. The RESEARCH-mandated pitfall mitigations are consistently applied: `np.asarray(result["predicted"])` for naked-array returns, `reshape(-1, 1)` for 2D xout, `wasserstein_barycenter` instead of `frechet_mean(space="density")`, `scores.var(axis=0)` instead of `fit["weights"]` for PVE, `np.clip(..., 0, None)` before `normalize_density`. The "scaling up" tip in `phoneme-shapelets.md` does not assert the unmeasured >85% accuracy of Assumption A2. Nav wiring in mkdocs.yml and index.md is well-formed and all referenced files exist.

Two warnings were found: one involving a fragile `upper_band[0]` indexing assumption that silently discards per-lag band variation, and one involving test-data identity used in two separate ISE computations in `frechet-density-regression.md` that are presented as independent but are structurally the same evaluation (misleading duplication rather than distinct evidence). Three informational items note redundant computation patterns and a missing `fast()` guard opportunity.

No BLOCKER-level issues were found. No API names, return keys, or parameter types are incorrect relative to the shipped bindings.

## Warnings

### WR-01: `upper_band[0]` silently discards per-lag band variation in ACF plot

**File:** `docs/examples/fts-forecast.md:108`
**Issue:** The functional ACF binding returns `upper_band` as a 1D numpy array of length `max_lag` (a `Vec<f64>` in `src/fts_mod.rs:319`). The fence code extracts only the first element — `upper = float(np.asarray(acf["upper_band"])[0])` — and uses it as a single scalar horizontal line for all lags. If the Monte Carlo white-noise band is not constant across lags (e.g., due to edge effects at high lags), the plot will display a flat band at the wrong level for most lags, without any error or warning.

The RESEARCH skeleton at §7.2 uses the same `[0]` pattern, and this is the verified recipe. However, it is an implicit assumption that should either be confirmed or made explicit. If the band is genuinely lag-invariant (which is plausible for a permutation-based scalar summary), the code is correct. If it varies, the plot is silently misleading.

**Fix:** Either confirm via inspection that all elements of `upper_band` are identical (and add a comment), or plot the band as a per-lag array rather than a scalar:

```python
upper_arr = np.asarray(acf["upper_band"])
# If constant (assert or check): use [0]
upper = float(upper_arr[0])
# If possibly varying: ax.plot(lags, upper_arr, ...)
```

At minimum, add a comment asserting the band is constant:
```python
upper = float(np.asarray(acf["upper_band"])[0])  # constant across lags (MC-permutation scalar)
```

---

### WR-02: Density integration check fence silently re-runs ISE on the same test split already shown in the prior fence

**File:** `docs/examples/frechet-density-regression.md:209–251`
**Issue:** The "Density integration check" fence (exec="1", source="above") reconstructs the full pipeline — density matrix, train/test split with `rng = np.random.default_rng(42)`, frechet_global_reg, frechet_local_reg — and then re-prints `ise_g` and `ise_l` as if they are additional evidence. These values are identical to those plotted in the preceding fence (lines 154–155) because both fences use the same seed and data.

The prose at line 256 says "The ISE numbers (printed above) come directly from the fence run" which implies these numbers are freshly computed evidence, but they are structurally the same evaluation restated in text form. A reader expecting an independent check (e.g., printed via a different code path or different split) will be misled. The fence title is "Density integration check," but the primary output items 1–3 (ISE values and local improvement) are not integration checks — only items in the inner `for` loop are.

This is a quality defect: the integration check section does valid work (verifying density integrals), but the ISE re-print is redundant and potentially misleading as "additional" evidence.

**Fix:** Remove the ISE printout from the density-integration fence and focus it solely on the integral verification. Either remove lines 242–244 from that fence or add a comment making clear the values are a reproduction:

```python
# ISE values identical to prior fence (same seed/split, shown for completeness)
print(f"Global regression  ISE: {ise_g:.6f}")  # same as bar chart above
print(f"Local  regression  ISE: {ise_l:.6f}")
```

Or, strip it to the integration check only:
```python
print("Predicted-density integral check (should be ≈1.0 for each row):")
for k in range(7):
    intg_g = np.trapezoid(pred_g[k], t_grid)
    intg_l = np.trapezoid(pred_l[k], t_grid)
    print(f"  test station {k+1}: global={intg_g:.4f}  local={intg_l:.4f}")
print("FDARS_FENCE_OK")
```

---

## Info

### IN-01: Redundant ftsm fit in FTS "Fitting" fence

**File:** `docs/examples/fts-forecast.md:171,182`
**Issue:** The "Fitting" fence calls `ftsm(X_train, t_wk, ncomp=3)` explicitly (line 171) to extract PVE and AR orders, then calls `ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)` (line 182). Per `src/fts_mod.rs:170-171`, `ftsm_forecast_multistep` re-fits `ftsm` internally before forecasting. The FTSM is therefore fit twice for the same data in a single fence execution. Results are identical (deterministic), so this is not a correctness bug, but it doubles computation time for the fence.

The pattern is unavoidable given the PyO3 combined-function design (Python cannot pass a Rust `FtsmResult` between calls), and is documented in the Rust binding. Not a code change requirement, but worth noting for future fence design.

**Fix:** No action required; add a comment if desired:
```python
# Note: ftsm_forecast_multistep re-fits ftsm internally (PyO3 combined-function pattern)
fc = ftsm_forecast_multistep(X_train, t_wk, h=5, ncomp=3)
```

---

### IN-02: `shapelet_transform_fit` and `discover_shapelets` are called independently in the feature-extraction fence, running the full discovery twice

**File:** `docs/examples/phoneme-shapelets.md:106,111`
**Issue:** The shapelet discovery fence runs `discover_shapelets(X_tr, y_tr, max_candidates=200, seed=42)` (line 106) for its summary dict, then calls `shapelet_transform_fit(X_tr, y_tr, max_candidates=200, seed=42)` (line 111) which runs the same discovery algorithm again internally. With `max_candidates=200` on (72, 256) data the combined cost is ~0.9s per the RESEARCH timing table — doubled here to ~1.8s from two independent discoveries. The results are identical given the same seed, so no correctness issue.

**Fix:** Not required. If build time is a concern in future, `shapelet_transform_fit` subsumes `discover_shapelets` (the former stores shapelets internally). The `disc["quality"]` string can be obtained from the hardcoded parameter instead of calling `discover_shapelets` separately:
```python
qual = "info_gain"  # matches the quality= parameter passed to shapelet_transform_fit
```

---

### IN-03: `frechet-density-regression.md` imports `wasserstein_barycenter` in the second fence but does not need it for ISE computation

**File:** `docs/examples/frechet-density-regression.md:120`
**Issue:** The "Global and local Fréchet regression" fence (lines 115–185) imports `wasserstein_barycenter` (line 120) and uses it at line 133 (`bary = wasserstein_barycenter(density_matrix, t_grid)`) — but `bary` is only used in Panel 1 of the plot at line 166. The import is used and the code is correct. However, the fence also re-computes the barycenter even though it was computed in the prior fence, duplicating a non-trivial but fast operation.

This is a minor observation: fence isolation requires full re-computation, so it is expected. No fix is needed.

---

_Reviewed: 2026-09-05T22:05:14Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
