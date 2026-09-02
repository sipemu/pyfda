---
phase: 66-isolated-crate-bump-regression-gate
reviewed: 2026-09-02T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - src/depth_mod.rs
  - src/fdata_mod.rs
  - src/regression_mod.rs
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: clean
---

# Phase 66: Code Review Report

**Reviewed:** 2026-09-02
**Depth:** standard
**Files Reviewed:** 3
**Status:** clean (one informational note)

## Summary

Phase 66 introduced exactly two kinds of changes across three files: (1) a Cargo.toml version bump from `fdars-core = "0.23.0"` to `"0.33.0"`, and (2) six `#[allow(deprecated)]` outer attributes added at PyO3 wrapper function sites that call soft-deprecated upstream functions.

The review checked four specific questions mandated by the scope:

1. **Attribute scope — function-level, not crate/module-wide.** All six `#[allow(deprecated)]` attributes are outer item attributes (`#[...]`, not `#![...]`) placed immediately above the `#[pyfunction]` line of the affected `pub fn` declaration. They suppress deprecation lint only within the body of the decorated function. `lib.rs` was also inspected: its two crate-level bang attributes (`#![allow(clippy::too_many_arguments)]` and `#![allow(clippy::type_complexity)]`) are unchanged and do not mention `deprecated`. No crate-wide or module-wide deprecated suppression was introduced.

2. **Guard correctness — each attribute is at a real deprecated call site.** Cross-referencing the attributes against the 66-AUDIT.md table of deprecated upstream functions:

   | File | Decorated function | Deprecated call inside |
   |------|--------------------|------------------------|
   | `src/depth_mod.rs:40` | `fraiman_muniz_2d` | `fdars_core::depth::fraiman_muniz_2d` (line 51) |
   | `src/depth_mod.rs:85` | `modal_2d` | `fdars_core::depth::modal_2d` (line 96) |
   | `src/depth_mod.rs:130` | `random_projection_2d` | `fdars_core::depth::random_projection_2d` (line 141) |
   | `src/depth_mod.rs:175` | `random_tukey_2d` | `fdars_core::depth::random_tukey_2d` (line 186) |
   | `src/fdata_mod.rs:39` | `mean_2d` | `fdars_core::fdata::mean_2d` (line 46) |
   | `src/regression_mod.rs:394` | `fanova` | `fdars_core::function_on_scalar::fanova` (line 405) |

   All six suppressed calls are documented deprecated functions in fdars-core 0.33.0. There are no dead suppressions (no `#[allow(deprecated)]` above a function body that contains no deprecated call).

3. **No logic changes.** The diff is purely additive attribute annotation. Function signatures, bodies, and call arguments are byte-for-byte identical to the pre-bump state.

4. **No unguarded deprecated call sites.** Searching all three files for `fdars_core::` calls against the full list of deprecated symbols (the four 2D depth functions, `fanova`, and `mean_2d`) confirms every deprecated call site is now guarded. Remaining `_2d`-suffix functions that are NOT deprecated (e.g., `fdars_core::depth::functional_spatial_2d`, `fdars_core::depth::kernel_functional_spatial_2d`, `fdars_core::fdata::geometric_median_2d`, `fdars_core::fdata::deriv_2d`) carry no `#[allow(deprecated)]` attribute, which is correct — they are not deprecated.

The change is minimal, mechanically correct, and correctly scoped.

## Info

### IN-01: Migration of deprecated 2D-variant calls is deferred; plan should be tracked

**File:** `src/depth_mod.rs:40`, `src/depth_mod.rs:85`, `src/depth_mod.rs:130`, `src/depth_mod.rs:175`, `src/fdata_mod.rs:39`, `src/regression_mod.rs:394`

**Issue:** Six functions call soft-deprecated upstream APIs. The `#[allow(deprecated)]` attributes are correct short-term mitigations, but they permanently silence the compiler warning at these sites until a follow-up migration phase removes them. If the upstream functions are eventually hard-removed in a future `fdars-core` version (e.g., 0.4x+), the build will fail with "not found in scope" rather than the current deprecation warning — with no prior signal from the suppressed lint.

The comment text `// fdars-core 0.30: soft-deprecated; migration deferred (Phase 66 CONTINGENCY)` is clear intent documentation, but there is no corresponding open issue, roadmap entry, or TODO anchor that would surface this debt in future planning.

**Fix:** Add a phase to the v11.0 roadmap (or a GitHub issue) that tracks migration of these six call sites to their replacement APIs (`fraiman_muniz(…, Dim::Two)`, `modal(…, Dim::Two)`, `random_projection(…, Dim::Two)`, `random_tukey(…, Dim::Two)`, `mean(…, Dim::Two)`, and `fanova_seeded`). Optionally add a `TODO(phase-N):` marker to each `#[allow(deprecated)]` comment so it can be grepped at migration time:

```rust
#[allow(deprecated)] // fdars-core 0.30 CONTINGENCY — TODO(phase-67): migrate to fraiman_muniz(…, Dim::Two)
```

---

_Reviewed: 2026-09-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
