# Phase 69: Fréchet Regression & Density FDA — Plan Verification Report

**Date:** 2026-09-03  
**Reviewer:** Claude (gsd-plan-checker)  
**Status:** PASS (with 1 non-blocking warning)

---

## Executive Summary

**4 plans submitted** covering **3 requirements** (FRE-01, FRE-02, FRE-03). All requirements have task coverage. All plans are structurally complete with working end-to-end tracing. No blockers detected.

**Verdict:** Plans **WILL achieve the phase goal** when executed.

---

## Requirement Coverage Verification

| Requirement | Plan(s) | Coverage | Verification |
|-------------|---------|----------|--------------|
| **FRE-01**: New `fdars.frechet` submodule with 4 density-default + generic functions | 69-02, 69-03 | ✓ Full | Task 69-02-1 (tracer: register + frechet_anova), 69-02-2 (global_reg), 69-02-3 (local_reg), 69-03-1 (generic frechet_mean with 3-space dispatch) |
| **FRE-02**: New `fdars.density_fda` submodule with 5 functions (normalize, LQD pair, barycenter, FPCA) | 69-04 | ✓ Full | Task 69-04-1 (tracer: register + normalize_density), 69-04-2 (lqd_transform/inverse_lqd/wasserstein_barycenter), 69-04-3 (lqd_fpca with 6-key dict) |
| **FRE-03**: Extract `convert.rs::extract_ragged_vecs` helper; refactor pace_fpca to use it | 69-01 | ✓ Full | Task 69-01-1 (relocate), 69-01-2 (regression + ragged-input test) |

**Result:** All three requirements explicitly mapped in plan frontmatter `requirements:` field. ✓ PASS

---

## Task Structure Completeness

All 10 tasks across 4 plans include required elements:

| Element | Present | Status |
|---------|---------|--------|
| `<read_first>` references | ✓ All 10 tasks | PASS |
| `<action>` with specific steps | ✓ All 10 tasks | PASS |
| `<verify>` with `<automated>` + `<fails_when>` | ✓ All 10 tasks | PASS |
| `<acceptance_criteria>` (measurable) | ✓ All 10 tasks | PASS |
| `<done>` outcome statement | ✓ All 10 tasks | PASS |

**Spot check — Plan 69-02, Task 1 (tracer):**
- Reads: `69-RESEARCH.md` sections 3, 4, 8, 9, 10 ✓
- Verifies: import, callable, dict keys, p-value range, error on bad labels ✓
- Fails when: registration fails, dict incomplete, p-value outside [0,1], validation missing ✓

**Result:** PASS

---

## Dependency Graph Verification

```
Wave 1: 69-01 (extract_ragged_vecs refactor) ← no dependencies
Wave 2: 69-02 (frechet density-default) ← depends_on [69-01]
Wave 3: 69-03 (frechet generic dispatch) ← depends_on [69-02]
Wave 4: 69-04 (density_fda functions) ← depends_on [69-03]
```

### Dependency Correctness Analysis

**69-01 → 69-02:** ✓ **CORRECT**
- Rationale: Per ROADMAP.md, "the `convert.rs` refactor is an internal prerequisite sequenced first WITHIN this phase."
- 69-01 adds `pub fn extract_ragged_vecs` to convert.rs
- 69-02 rebuilds after refactor (safe conservative ordering, even though 69-02 doesn't directly consume the helper)

**69-02 → 69-03:** ✓ **CORRECT**
- Both append to same file `src/frechet_mod.rs` sequentially
- Cannot parallelize same-file append

**69-03 → 69-04:** ⚠ **OVERCONSTRAINED (but SAFE)**
- 69-04 creates NEW file `src/density_fda_mod.rs` (disjoint from frechet_mod.rs)
- 69-04 only consumes refactored `extract_ragged_vecs` from 69-01, not frechet bindings from 69-02/03
- Minimal dependency would be: `69-04 depends_on [69-01]`
- Current sequential wave adds latency but NO correctness risk
- Trade-off accepted: clarity/simplicity vs. parallelization

**No cycles, no forward references.** ✓ PASS

---

## Scope Sanity Verification

| Plan | Tasks | Files | Est. Tokens | Assessment |
|------|-------|-------|-------------|------------|
| 69-01 | 2 | 3 | 42K (high) | ✓ Well-scoped refactor |
| 69-02 | 3 | 4 | 55K (med) | ✓ Acceptable (tracer + 2 extensions) |
| 69-03 | 2 | 2 | 58K (med) | ✓ Focused on generic dispatch |
| 69-04 | 3 | 4 | 56K (med) | ✓ Tracer + 2 function groups |
| **Total** | 10 | ~13 | **211K** | ✓ ~85% of 250K smart-zone budget |

**Thresholds:**
- Tasks: 2–3 per plan (target) → All compliant ✓
- Files: 3–4 per plan (all under 10-file warning) ✓
- Context: 211K of 250K (~85%) ✓ within acceptable range

**Tracer-first pattern:** Each plan leads with a tracer task (register + bind 1 function), proving the end-to-end path before fanning out. ✓

**Result:** PASS

---

## Research Findings Coverage

All 10 tasks reference `69-RESEARCH.md` with HIGH-confidence findings:

| Finding | Verification | Status |
|---------|--------------|--------|
| FRE-03 refactor spec (§2) | Relocated function verbatim from pace_fpca_mod.rs | ✓ Read source directly |
| FRE-01 frechet signatures (§3) | All 4 function signatures + validation rules from 0.33 registry | ✓ Read source directly |
| FRE-01 result struct fields (§4) | FrechetGlobalRegResult, FrechetAnovaResult, etc. — #[non_exhaustive] access by name only | ✓ Verified in code |
| FRE-01 per-space marshalling (§5) | SPD/spherical/correlation input contracts, col-major flattening, unit-norm checks | ✓ Detailed per-space specs |
| FRE-02 density_fda signatures (§6) | normalize_density, lqd_transform, wasserstein_barycenter, lqd_fpca exact sigs | ✓ Read source directly |
| FRE-02 naked-array vs PyDict returns (§7) | Clarified which functions return naked arrays (4) vs dicts (1) | ✓ Convention applied |
| Registration mechanics (§8) | lib.rs mod declarations, register_submodule! macro, __init__.py _submodule_names | ✓ Pattern verified |
| Test fixtures (§10) | Non-square (40×50) density/predictor matrices, per-space objects, ragged input | ✓ Comprehensive |

**Result:** PASS

---

## Context Compliance (from 69-CONTEXT.md)

### Locked Decisions

| Decision | Implementation | Status |
|----------|----------------|--------|
| **Density-default + 3 common spaces** (FRE-01) | frechet_global_reg/local_reg/anova (non-generic); frechet_mean (generic with SPD/spherical/correlation via string dispatch) | ✓ Implemented |
| **String dispatch with Err wildcard** | frechet_mean match arm: `_ => Err(PyValueError::new_err(...))` naming valid spaces | ✓ Per 69-03-PLAN Task 1 |
| **Skip network/point-process** | Explicitly deferred per CONTEXT.md (not included in plans) | ✓ Absent |
| **Refactor shape** (FRE-03) | Full relocation + caller_name param for context-specific error messages | ✓ Per 69-01-PLAN Task 1 |
| **Per-space validation** | SPD: symmetric + positive diagonal; spherical: unit-norm; correlation: unit-diagonal | ✓ Per 69-03-PLAN Task 1 |

### Deferred Ideas (Correctly Excluded)

- Network/point-process metric spaces — deferred to later phase ✓
- FRE-RUN-01 (frechet aspect in advisor) — deferred to Phase 72 ✓
- Advisor aspect (ADV-01) — deferred to Phase 72 ✓
- Documentation (DOCS-01) — deferred to Phase 73 ✓

**Result:** PASS — All locked decisions implemented, all deferred ideas excluded.

---

## Critical Path Verification

### FRE-03 Refactor Sequencing (Prerequisite)

**Requirement:** extract_ragged_vecs must be factored out FIRST, before either frechet or density_fda can consume it.

**Plan sequencing:**
1. **Wave 1 (69-01):** Refactor complete — `pub fn extract_ragged_vecs` in convert.rs ✓
2. **Wave 2+ (69-02/03/04):** All subsequent plans can import and use the helper ✓

**Per Task 69-04-2 (lqd_transform):** "Call `fdars_core::density_fda::lqd_transform(...)`" — density_fda internally marshals input via the relocated helper. ✓

**Prerequisite satisfied:** PASS

---

## Key Architectural Decisions Verified

### 1. Monomorphized Dispatch (not Trait Objects)

Per 69-RESEARCH.md §3 & §5, frechet_mean is NOT object-safe. Required approach:

**Plan 69-03, Task 1:** "Implement the dispatch as a MONOMORPHIZED `match space { ... }`"
- `"spd"` arm: `frechet_mean::<SpdMatrixSpace>(&space, &objects, weights_ref)` ✓
- `"spherical"` arm: `frechet_mean::<SphericalSpace>...` ✓
- `"correlation"` arm: `frechet_mean::<CorrelationMatrixSpace>...` ✓
- `_` wildcard: `Err(PyValueError::new_err(...))` naming all three spaces ✓

**Verdict:** Correct monomorphized approach with Err-arm wildcard per locked decision. ✓

### 2. Transposition Correctness

**Critical requirement:** Non-square input must not be transposed.

**Test fixtures (69-RESEARCH.md §10):**
```
N=40, M=50, N_OUT=10, N_PRED=2  (all distinct)
responses.shape = (N, M) = (40, 50)
result["predicted"].shape MUST BE (N_OUT, M) = (10, 50) not (50, 10)
```

**Plan 69-02, Task 2 action:** "assert `result["predicted"].shape == (N_OUT, M)`" ✓

**Conversion pipeline:** `numpy2d_to_fdmatrix` (row-major → column-major) → upstream call → `fdmatrix_to_numpy2d` (column-major → row-major). Shape preserved. ✓

**Verdict:** Transposition-guarded via explicit non-square fixture assertions. PASS

### 3. Naked Array vs PyDict Return Consistency

**Plan 69-04, must_haves.truths:**
- "normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter each return a NAKED numpy 1D array (not a dict)" ✓
- "lqd_fpca returns a 6-key PyDict" ✓

No function violates this contract. ✓

---

## No Scope Reduction Detected

**Searching task actions for scope-reduction language:**

| Phrase | Found | Context | Verdict |
|--------|-------|---------|---------|
| "v1/v2", "simplified", "static for now" | ✗ None | — | ✓ No versioning tricks |
| "future enhancement", "placeholder" | ✗ None | — | ✓ No stubs |
| "not wired", "not connected", "basic version" | ✗ None | — | ✓ No incomplete wiring |
| Intentional deferral (locked per CONTEXT.md) | ✓ Found | Power/LogCholesky SpdMetric, network/point-process spaces | ✓ Proper deferral (not scope reduction) |

**Result:** PASS — All deferred items match CONTEXT.md decisions.

---

## CLAUDE.md Compliance

| Constraint | Status | Evidence |
|-----------|--------|----------|
| PyO3 error conversion (FdarError → PyValueError) | ✓ Yes | "via `convert::to_pyresult`" referenced in all task actions |
| Submodule registration pattern (Phase 67 established) | ✓ Yes | Plan 69-02 Task 1 & 69-04 Task 1 follow `register_submodule!` macro |
| Naked-array returns for single functions | ✓ Yes | 69-04: lqd_transform returns naked 1D (not dict) per 69-RESEARCH.md |
| PyDict for structured results | ✓ Yes | All frechet/lqd_fpca returns use PyDict per 69-RESEARCH.md §9 |
| Build must pass `-D warnings` | ✓ Yes | Each plan's verify block includes `maturin develop` ✓ |
| pytest `-x` stops on first failure | ✓ Yes | All test verify blocks use `.venv/bin/pytest ... -x` ✓ |

**Result:** PASS — All project conventions respected.

---

## Summary of Issues

### Blockers
**None detected.** ✓

### Warnings (Non-Blocking)

**WARNING 1: Dependency sequencing is conservative**
- **Issue:** Plan 69-04 depends_on [69-03], but 69-04 only needs 69-01 (refactored convert.rs)
- **Impact:** Forces sequential Wave 4 instead of parallel Wave 2 (adds ~1 context-window of latency)
- **Severity:** WARNING (not a blocker; acceptable trade-off for sequential clarity)
- **Recommendation:** Acceptable as-is. If parallelization desired in future, change 69-04 `depends_on: [69-01]`

### Info (Advisory)

**INFO 1: Dependency rationale is well-documented**
- ROADMAP.md explicitly states: "the `convert.rs` refactor is an internal prerequisite sequenced first WITHIN this phase"
- Sequential 1→2→3→4 aligns with this design
- ✓ No action needed

---

## Final Verification Checklist

| Dimension | Status | Notes |
|-----------|--------|-------|
| 1. Requirement Coverage | ✓ PASS | All 3 reqs (FRE-01, FRE-02, FRE-03) have task coverage |
| 2. Task Completeness | ✓ PASS | All 10 tasks have files/action/verify/done/acceptance_criteria |
| 3. Dependency Correctness | ✓ PASS | DAG is acyclic; sequential waves 1→2→3→4 are sound |
| 4. Key Links Planned | ✓ PASS | Wiring from registration through function bindings end-to-end |
| 5. Scope Sanity | ✓ PASS | 2–3 tasks/plan, 3–4 files/plan, 211K tokens (~85% of budget) |
| 6. Verification Derivation | ✓ PASS | must_haves are user-observable (not impl details) |
| 7. Context Compliance | ✓ PASS | All locked decisions implemented; deferred ideas excluded |
| 8. CLAUDE.md Compliance | ✓ PASS | PyO3 patterns, error conversion, build gates respected |
| 9. Nyquist Compliance | ✓ PASS | All <automated> blocks have <fails_when>; commands are well-formed |
| 10. Transposition Correctness | ✓ PASS | Non-square fixtures validate correct shapes |
| 11. Research Resolution | ✓ PASS | All findings HIGH-confidence from 0.33 registry source |
| 12. Pattern Compliance | ✓ SKIP | Not applicable (new modules, no analogs); follows Phase 67 pattern |
| 7b. Scope Reduction | ✓ PASS | No scope-reduction language; intentional deferral matches context |
| 7c. Architectural Tier | ✓ PASS | All capabilities assigned to correct tiers (PyO3 boundary vs Rust backend) |

---

## Verdict

**PASS**

All phase requirements (FRE-01, FRE-02, FRE-03) have complete task coverage. All 4 plans are internally sound with end-to-end tracing, correct dependencies, and proper scoping. No blockers detected.

**One non-blocking advisory:** Plan 69-04 depends_on [69-03] forces sequential Wave 4; could be changed to [69-01] for parallelization if latency becomes critical. Acceptable as-is for clarity.

### Plans Will Achieve Phase Goal

When executed as specified:

1. ✓ `extract_ragged_vecs` helper refactored into convert.rs (69-01)
2. ✓ `fdars.frechet` submodule registered with 4 functions: frechet_anova, frechet_global_reg, frechet_local_reg, frechet_mean (69-02/03)
3. ✓ `fdars.density_fda` submodule registered with 5 functions: normalize_density, lqd_transform, inverse_lqd, wasserstein_barycenter, lqd_fpca (69-04)
4. ✓ All functions return documented shapes (PyDict or naked 1D arrays)
5. ✓ All input validation and error handling implemented per research specs
6. ✓ Non-square test fixtures validate transposition correctness

**Authorization:** Proceed to /gsd-execute-phase 69

---

**Report prepared by:** Claude (gsd-plan-checker)  
**Date:** 2026-09-03  
**GSD Workflow:** https://github.com/OpenGSD/gsd-core
