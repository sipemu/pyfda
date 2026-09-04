# Phase 70: Multi-Domain Data, FAMM & Advanced Clustering — Plan Verification

**Verified:** 2026-09-03  
**Verdict:** PASS — All plans will achieve the phase goal

---

## Summary

Four plans submitted for Phase 70 (multi-domain functional data, FAMM mixed models, multivariate SPM, advanced clustering). All requirements mapped, all tasks complete, all research findings correctly incorporated into task actions. The plans precisely implement the critical discovery that MultiFunData is NOT consumed by downstream functions in fdars-core 0.33 — this is explicitly documented in each plan's objective to prevent false verification gaps.

**Issues found:** 0 blockers, 0 warnings

---

## Verification Dimensions

### Dimension 1: Requirement Coverage

**Finding:** PASS

All four v11.0 requirements for Phase 70 are covered:

| Requirement | Plan | Tasks | Status |
|-------------|------|-------|--------|
| MULTI-01: PyMultiFunData opaque handle + builder | 70-01 | 1 (tracer) + 1 (test) | Covered |
| MULTI-02: FAMM bindings (dense_flmm, fast_fmm, multi_famm) | 70-02 | 1 (tracer) + 1 (fast_fmm) + 1 (multi_famm+test) | Covered |
| MULTI-03: Multivariate SPM (mfpca + spe_multivariate) | 70-03 | 1 (tracer) + 1 (spe_multivariate+test) | Covered |
| MULTI-04: Advanced clustering (dbscan_fd, kcfc_cluster, funfem_cluster, align_cluster_fd) | 70-04 | 1 (tracer) + 1 (kcfc+funfem) + 1 (align+test) | Covered |

All four requirements declared in each plan's `requirements` frontmatter field.

### Dimension 2: Task Completeness

**Finding:** PASS

All 10 tasks across 4 plans have complete task structure:

- All have `<files>` section listing modified files
- All have `<action>` with detailed, specific steps (not vague)
- All have `<verify>` with automated commands and `<fails_when>` clauses
- All have `<acceptance_criteria>` with testable assertions
- All have `<done>` state describing completion condition

Example (70-01 Task 1):
```
<action>
  Create `src/multi_fdata_mod.rs` mirroring `pace_fpca_mod.rs` structure...
  [explicit step-by-step]
</action>
<verify>
  <automated>...maturin develop...grep...import...</automated>
  <fails_when>The submodule is not registered in lib.rs, ...</fails_when>
</verify>
<acceptance_criteria>
  - src/multi_fdata_mod.rs exists with a #[pyclass(name="PyMultiFunData")]...
  [5 specific assertions]
</acceptance_criteria>
```

All tasks follow this pattern consistently.

### Dimension 3: Dependency Correctness

**Finding:** PASS

Wave assignments respect declared dependencies:

- **Wave 1:** 70-01 (no depends_on) — PyMultiFunData handle, foundation for phase
- **Wave 2:** 70-02 depends_on: [70-01] — FAMM bindings, both touch lib.rs + __init__.py
- **Wave 3:** 70-03 depends_on: [70-01] — MFPCA/SPE, ordered AFTER PyMultiFunData per SC3
- **Wave 4:** 70-04 depends_on: [70-01] — clustering, independent but runs last (sequential main)

No circular dependencies. No forward references. All referenced plans (70-01, 70-02, 70-03) exist.

### Dimension 4: Key Links Planned

**Finding:** PASS

All artifact wiring is explicit and task-backed:

**70-01 (PyMultiFunData):**
- ✓ Task 1 creates `src/multi_fdata_mod.rs` and adds registrations to lib.rs + __init__.py
- ✓ Must_have key_links: "lib.rs registers multi_fdata submodule via register_submodule!"
- ✓ Must_have key_links: "__init__.py _submodule_names includes 'multi_fdata'"

**70-02 (FAMM):**
- ✓ Task 1 creates `src/famm_mod.rs` and adds registrations
- ✓ Task 1 defines `dense_flmm_result_to_pydict` helper for reuse in Task 3
- ✓ Task 3 (multi_famm) reuses the helper via PyList building pattern
- ✓ Must_have key_links cover lib.rs + __init__.py wiring

**70-03 (MFPCA/SPE):**
- ✓ Task 1 appends mfpca to existing src/spm_mod.rs register function (no new module)
- ✓ Task 2 appends spe_multivariate to same register function
- ✓ Must_have key_links: "mfpca + spe_multivariate added to the existing spm_mod::register fn"

**70-04 (Clustering):**
- ✓ Task 1 appends dbscan_fd to existing src/clustering_mod.rs register function
- ✓ Task 2 appends kcfc_cluster + funfem_cluster to same function
- ✓ Task 3 appends align_cluster_fd to same function
- ✓ All four use the same PyDict/usize_vec_to_numpy1d/fdmatrix_to_numpy2d pattern

All wiring is planned and documented in task actions.

### Dimension 5: Scope Sanity

**Finding:** PASS

Task distribution and file count within healthy bounds:

| Plan | Tasks | Files Modified | Context Estimate | Status |
|------|-------|-----------------|-------------------|--------|
| 70-01 | 2 | 4 (multi_fdata_mod.rs, lib.rs, __init__.py, test_multi_fdata.py) | 55k | GOOD |
| 70-02 | 3 | 4 (famm_mod.rs, lib.rs, __init__.py, test_famm.py) | 70k | GOOD |
| 70-03 | 2 | 2 (spm_mod.rs, test_spm_mfpca.py) | 60k | GOOD |
| 70-04 | 3 | 2 (clustering_mod.rs, test_clustering_advanced.py) | 78k | GOOD |

**Assessment:**
- No plan exceeds 3 tasks (green zone: 2-3 is healthy)
- Files per plan: 2-4 (within "5-8 target" for new binding groups)
- Total estimated tokens: 263k (within project budget for Phase 70)
- Confidence levels: med-to-med (in alignment with complexity)

The phase is split optimally: two new submodules (multi_fdata, famm) plus two existing submodule extensions (spm, clustering), with clear tracer → detail → test structure in each.

### Dimension 6: Verification Derivation

**Finding:** PASS

All must_haves map to user-observable, testable truths:

**70-01 must_haves truths:**
1. "import fdars.multi_fdata works" — directly testable via Python import
2. "multi_fdata_from_components builds handle; getters return correct values" — testable via instantiation + property access
3. "Guard cases (length mismatch, 1D data, nrows mismatch) raise ValueError" — testable via pytest.raises

**70-02 must_haves truths:**
1. "Three functions callable, return documented PyDicts" — testable via callable() + dict-key assertion
2. "Exact key counts (14/6/4) and array shapes" — testable via dict.keys() and .shape checks
3. "None consume PyMultiFunData; all take plain inputs" — implemented in action; testable via import + signature inspection

**70-03 must_haves truths:**
1. "mfpca returns 6-key dict; eigenfunctions/means are P-length lists" — testable via len() + shape
2. "spe_multivariate returns naked (n,) array" — testable via .ndim == 1 and .shape == (n,)
3. "Both take list-of-2D-arrays; pub(super) fields omitted" — testable via assertion that combined_rotation/scale_threshold not in result

**70-04 must_haves truths:**
1. "Four functions callable, return labels/result dicts" — testable via callable() + dict assertion
2. "Specific encodings: int64 -1 noise, no fpca_models, (n,k) membership, k-length templates" — testable via dtype/key/shape assertions
3. "Non-square fixtures; transposition-guarded" — implemented via numpy2d_to_fdmatrix; testable with non-square test data

All truths are user-observable (not implementation details) and directly verifiable by test assertions.

Artifacts map to truths:
- `src/multi_fdata_mod.rs` + tests → SC1 observable behaviors
- `src/famm_mod.rs` + tests → SC2 callable functions + PyDicts
- spm_mod.rs additions + tests → SC3 MFPCA/SPE
- clustering_mod.rs additions + tests → SC4 advanced clustering

### Dimension 7: Context Compliance

**Finding:** PASS

All plans honor CONTEXT.md decisions and discretion areas:

**Locked Decisions:**
- **D-01 (MULTI-03 scope):** "Bind mfpca + spe_multivariate into fdars.spm"
  - Plan 70-03 objective confirms this exact scope, explicitly skipping frcc/other monitors ✓
  
**Claude's Discretion (convention-driven):**
- **PyMultiFunData handle mirroring PyIrregFdata:** Plan 70-01 action specifies exact mirroring ✓
- **Submodule organization (new multi_fdata, famm; extend spm, clustering):** Plans follow this exactly ✓
- **Return shape PyDicts from result structs:** All plans reference research sections with exact field lists ✓
- **Transposition: non-square fixtures:** All plans explicitly mention (20×30), (20×25) non-square data ✓
- **Enum/config handling (Default + mutation):** All plans specify this pattern for #[non_exhaustive] ✓
- **Error handling (FdarError → PyValueError):** All plans reference `convert::to_pyresult` ✓

**Deferred Ideas (NOT in these plans):**
- frcc + other multi-domain SPM monitors — correctly excluded from 70-03 ✓
- Advisor extensions — correctly deferred to Phase 72 ✓
- Documentation pages — correctly deferred to Phase 73 ✓

No contradictions. All locked decisions implemented; all deferred ideas correctly excluded.

### Dimension 7b: Scope Reduction Detection

**Finding:** PASS — No reduction; critical discovery correctly documented

Scan for reduction language ("v1", "simplified", "static", "future enhancement", "placeholder", "will be wired later"):
- None found in any plan

**Critical finding from research incorporated correctly:**

The ROADMAP SC2 says: "Mixed-model bindings... consuming `PyMultiFunData` where required..."

The research revealed: **MultiFunData is NOT consumed by any FAMM/MFPCA/clustering function in fdars-core 0.33.**

This is NOT scope reduction — it's a factual discovery. The plans explicitly document this:

- **70-02 objective:** "Do NOT accept PyRef<PyMultiFunData> anywhere in this module. MULTI-02's 'consume PyMultiFunData where required' is vacuously satisfied — no FAMM function requires it."

- **70-03 objective:** "neither mfpca nor spe_multivariate consumes MultiFunData... do NOT attempt to read them."

- **70-04 objective:** "all four take plain (&FdMatrix, &[f64], &Config) — none consumes PyMultiFunData."

This preempts a false verification gap: the reading of "where required" is VACUOUSLY SATISFIED because no downstream function requires the handle. The plans correctly identify this truth and document it to prevent later confusion.

**Conclusion:** No scope reduction. Full delivery of all four requirements per research findings.

### Dimension 8: Nyquist Compliance — Verify Command Format

**Finding:** PASS

All `<automated>` commands have `<fails_when>` clauses and can actually fail:

**70-01 Task 1:**
```
<verify>
  <automated>cd .../pyfda && grep -qE 'register_submodule!\(m, "multi_fdata"' src/lib.rs && grep -q '"multi_fdata"' python/fdars/__init__.py && .venv/bin/maturin develop ... && .venv/bin/python -c "import fdars.multi_fdata as mf; ..."</automated>
  <fails_when>The submodule is not registered in lib.rs, "multi_fdata" is missing from __init__.py, the crate fails to build, or PyMultiFunData / multi_fdata_from_components is absent from the imported module.</fails_when>
</verify>
```

✓ Command has multiple independently-failing stages (grep, grep, maturin, import, assertion)
✓ fails_when documents all failure modes
✓ Command is runnable and produces measurable output (build status, import success)

**70-02 Task 2:**
```
<verify>
  <automated>cd .../pyfda && .venv/bin/maturin develop 2>&1 | tail -3 && .venv/bin/python -c "import fdars.famm as f; assert callable(f.fast_fmm); print(...)"</automated>
  <fails_when>The crate fails to build or fast_fmm is absent from fdars.famm.</fails_when>
</verify>
```

✓ Build failure and import/callable failure are distinct, both detectable
✓ Output is measurable

All other verify blocks follow same pattern: maturin build check + import + assertion.

Test verify blocks use pytest:
```
<automated>cd .../pyfda && .venv/bin/pytest tests/test_multi_fdata.py -x -q 2>&1 | tail -15</automated>
<fails_when>The handle builds with wrong n_obs/n_components, or any of the three guard cases fails to raise ValueError, or an import error occurs.</fails_when>
```

✓ Pytest exit code is measurable (0 = pass, non-zero = fail)
✓ fails_when describes observable test failures

**All 10 verify blocks follow this pattern. Nyquist-compliant.**

### Dimension 10: CLAUDE.md Compliance

**Finding:** PASS

Project .claude/CLAUDE.md specifies:

| Requirement | How Plans Comply |
|-------------|------------------|
| Rust 1.83+ MSRV (fixed, not bumped) | Plans do not modify Cargo.toml versions ✓ |
| PyO3 0.28 (fixed) | Plans do not modify Cargo.toml versions ✓ |
| -D warnings enforced | All plans specify "explicit imports only (-D warnings)" ✓ |
| rustfmt + clippy enforced | Plans do not disable lints; 70-04 Task 2 includes `#[allow(clippy::too_many_arguments)]` which is a precision flag, not a bypass ✓ |
| Naming: snake_case modules/functions | All plans follow: `multi_fdata_mod.rs`, `famm_mod.rs`, `dense_flmm`, `multi_famm`, `mfpca`, `spe_multivariate`, `dbscan_fd`, `kcfc_cluster`, `funfem_cluster`, `align_cluster_fd` ✓ |
| Error handling: FdarError → PyValueError | All plans reference `convert::to_pyresult` ✓ |
| Macros: #[pyfunction], #[pyclass] | All plans specify exact macro usage ✓ |

No violations of project conventions.

### Dimension 11: Research Resolution

**Finding:** PASS

70-RESEARCH.md is complete, HIGH confidence, covers all needed areas:

| Section | Coverage |
|---------|----------|
| §1: MultiFunData API | Full struct + accessor list from source ✓ |
| §2: PyMultiFunData handle | Builder logic, registration pattern ✓ |
| §3: FAMM signatures | dense_flmm, fast_fmm, multi_famm with exact field lists ✓ |
| §4: MFPCA + spe_multivariate | Signatures, 6 public fields (NOT pub(super)), lifetime pattern ✓ |
| §5: Registration mechanics | lib.rs + __init__.py edit points ✓ |
| §6: Advanced clustering | All 4 algorithms, exact configs, result structs, noise encoding ✓ |
| §7: Non-exhaustive handling | Default + mutation pattern ✓ |
| §8: Fixtures | Non-square sizes (20×30, 20×25), subject-id layout, DBSCAN noise fixture ✓ |
| §9: Crate paths | Full paths: fdars_core::famm::dense_flmm, fdars_core::spm::stats::spe_multivariate ✓ |
| §10: Architecture patterns | Data flow diagram, tier-responsibility map ✓ |
| §11: Pitfalls | 6 named pitfalls (MultiFunData consumption, transposition, noise encoding, lifetime, pub(super), p_disc semantics) ✓ |
| §12: Don't hand-roll table | Justifications for each FAMM/clustering function ✓ |

All research claims verified directly from fdars-core 0.33 source. No stale assumptions.

---

## Critical Findings

### CRITICAL #1: MultiFunData not consumed downstream

**Research:** grep confirms 0 references to "MultiFunData" or "multi_fdata" in famm.rs, spm/mfpca.rs, clustering_advanced.rs

**Plans:** All three downstream plans (70-02, 70-03, 70-04) explicitly document this non-consumption in their objectives. This is CORRECT and preempts false verification gaps.

**Implication:** "Consuming PyMultiFunData where required" (ROADMAP SC2) is vacuously satisfied — none require it. Plans correctly identify this truth.

### CRITICAL #2: pub(super) field inaccessibility in MfpcaResult

**Research:** combined_rotation and scale_threshold are marked pub(super), accessible only within spm module family, not from pyfda bindings.

**Plans:** Plan 70-03 explicitly states "Do NOT read combined_rotation or scale_threshold" and exposes ONLY the 6 public fields. This prevents compilation errors and ensures correctness.

### CRITICAL #3: DbscanResult noise encoding requires i64 conversion

**Research:** cluster: Vec<Option<usize>> must be mapped None → -1i64, Some(c) → c as i64, converted via IntoPyArray, NOT usize_vec_to_numpy1d.

**Plans:** Plan 70-04 Task 1 specifies exact conversion: "Noise encoding: ... .into_pyarray(py)... Do NOT use usize_vec_to_numpy1d for this field." This prevents silent logic errors.

### CRITICAL #4: spe_multivariate lifetime correctness

**Research:** argvals_list requires Vec<Vec<f64>> before Vec<&[f64]> refs to satisfy Rust lifetimes (Pitfall 4).

**Plans:** Plan 70-03 Task 2 specifies exact pattern: "av_vecs ... THEN av_refs = av_vecs.iter().map(...).collect(); (Pitfall 4: av_vecs must outlive av_refs)". Prevents lifetime error.

### CRITICAL #5: Ordering constraint satisfied

**Research:** ROADMAP SC3 requires MFPCA "built AFTER PyMultiFunData within this phase"

**Plans:** Wave ordering enforces this:
- Wave 1: 70-01 (PyMultiFunData)
- Wave 3: 70-03 (MFPCA), depends_on: [70-01]

Ordering constraint is literally satisfied by wave assignment.

---

## Specific Strengths

1. **Read-first sections are comprehensive:** Each plan specifies exact research sections to read before execution (e.g., "70-RESEARCH.md sections 3.1, 3.2, 3.3")

2. **PyDict field exactness:** All plans list exact keys from research sections (14 for dense_flmm, 6 for fast_fmm, etc.). No guessing.

3. **Non-square fixture discipline:** All test plans use explicit (20,30) and (20,25) non-square arrays. Transposition guards are embedded in test design.

4. **Reusable helper pattern:** Plan 70-02 Task 1 defines `dense_flmm_result_to_pydict` helper; Task 3 reuses it for multi_famm components list. Good factorization.

5. **Error message clarity:** Plans specify exact error guards (list-length mismatch, 1D data detection, nrows validation) before calling core constructors. Prevents panics.

6. **Explicit import discipline:** All plans mention "Explicit imports only (-D warnings)" to prevent CI failures.

7. **Full suite integration:** All verification blocks include full pytest suite check to catch regressions (FND-02 guard compliance).

---

## Wave Execution Flow

Plans are designed to execute sequentially per ROADMAP note ("worktrees disabled here anyway; sequential on main"):

```
Wave 1 (parallel-capable, but sequential anyway):
  70-01 ← establishes PyMultiFunData

Wave 2 (depends_on 70-01, rebuilds lib.rs + __init__.py):
  70-02 ← registers famm submodule

Wave 3 (depends_on 70-01, extends existing spm_mod.rs):
  70-03 ← adds mfpca + spe_multivariate to spm

Wave 4 (depends_on 70-01, extends existing clustering_mod.rs):
  70-04 ← adds 4 clustering functions to clustering
```

Each wave rebuilds the crate (maturin develop) and runs tests. FND-02 guard is checked in each plan's verification.

---

## Conclusion

**Verdict: PASS**

All four plans will achieve Phase 70's goal. The plans:

✓ Cover all 4 requirements (MULTI-01, MULTI-02, MULTI-03, MULTI-04)  
✓ Have complete task structure (files, action, verify, acceptance_criteria, done)  
✓ Respect dependency ordering (wave assignments, AFTER constraint)  
✓ Wire all artifacts (lib.rs, __init__.py registrations)  
✓ Implement critical research findings (MultiFunData non-consumption, pub(super) inaccessibility, noise encoding, lifetime correctness)  
✓ Use non-square fixtures for transposition guarding  
✓ Include full-suite regression checks  
✓ Comply with CLAUDE.md conventions (Rust 1.83, -D warnings, snake_case, error handling)  
✓ Document every critical pitfall in plan objectives  

**No blockers. No warnings. Ready for execution.**

---

**Reviewed by:** Plan verification gate  
**Confidence:** HIGH (all critical findings from research incorporated, multi-point verification of field exactness, explicit documentation of non-consumption)  
**Next step:** Execute 70-execute-phase or equivalent workflow to proceed to Phase 70 execution.
