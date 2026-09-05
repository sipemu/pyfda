# Phase 72: Advisor Extension — Plan Verification Report

**Date:** 2026-09-04  
**Verification Gate:** Revision Gate  
**Status:** ISSUES FOUND — 3 blockers + 1 warning

---

## Executive Summary

The four plans for Phase 72 are otherwise well-structured and cover the phase requirements (ADV-01, ADV-02, SC3), but they exhibit a consistent verification gap: **precondition verification is deferred to execution time**, creating risk of silent failures.

**Specific Issues:**

1. **BLOCKER (Plan 72-01):** Guard-sync atomicity is declared but not proactively verified. The three frozenset edits must land in a single atomic commit; the verify section does not check this.

2. **BLOCKER (Plan 72-02/03):** "read_first" steps (reading exact PyDict key names from Rust source files) are marked as preconditions but have no verify gate. If keys are guessed incorrectly, KeyError and numpy-scalar leaks occur at runtime, not during verification.

3. **BLOCKER (Plan 72-03 Task 2):** Shapelet opaque-handle coercion guard placement is undefined. The plan says "add BEFORE dict(raw)" but does not verify the guard lands before, not after.

4. **WARNING (Plan 72-04):** LLM-free assertion relies on subprocess; no fallback if subprocess is unavailable.

**Recommendation:** Return to planner with these three blockers. Fixes are minimal (add ~20 lines of verify-section grep/bash checks across the three plans).

---

## Detailed Findings

### Dimension 1: Requirement Coverage

**PASS** — All four plans explicitly map to ADV-01 and ADV-02:

- ADV-01 (new/extended aspects): Plans 72-01 (fts tracer), 72-02 (frechet), 72-03 (regression/classification/spm extensions)
- ADV-02 (guard-sync + grounding + LLM-free): Plans 72-01 (atomic registration), 72-02/03 (grounding tests), 72-04 (comprehensive gate)

SC3 (frechet/fts diagnostics-only): Plan 72-01 explicitly guards against adding to _RUNNABLE_METHODS; plans 72-02/03 respect this.

### Dimension 2: Task Completeness

**PASS with caveats** — All tasks have required fields (files, action, verify, done), but verification lacks depth:

- **Task structure:** 2 tasks in 72-01, 2 in 72-02, 3 in 72-03, 1 in 72-04 (total 8 tasks) — reasonable granularity.
- **Spec clarity:** Actions are detailed (field names, cast rules, discriminators specified).
- **Verification gap:** The `<read_first>` blocks specify lines to read (e.g., "src/frechet_mod.rs:95-110") but the `<verify>` sections do not confirm the read happened or that expected keys were found.

### Dimension 3: Dependency Correctness

**PASS** — Dependency graph is acyclic and well-ordered:

- Wave 1: 72-01 (no deps)
- Wave 2: 72-02 (depends 72-01)
- Wave 3: 72-03 (depends 72-01)
- Wave 4: 72-04 (depends 72-01, 72-02, 72-03)

**Implicit inter-commit dependency (not documented):** Plan 72-01's atomic commit is a prerequisite for all others to pass the guard-sync test. If 72-01 lands with the three frozenset edits split across commits, the guard-sync test is broken between commits.

### Dimension 4: Key Links Planned

**PASS** — Wiring is explicit:

- fts/frechet method strings wired to dispatch branches in __init__.py (72-01)
- frechet registered stub in 72-01, body filled in 72-02 (clean handoff)
- shapelet opaque handle → coercion guard in __init__.py → classification builder (72-03)
- All aspects → per-aspect tests + grounding test + combined gate (72-04)

### Dimension 5: Scope Sanity

**PASS** — Task counts per plan are reasonable:

| Plan | Tasks | Files Modified | Complexity |
|------|-------|-----------------|-----------|
| 72-01 | 2 | 6 (fts.py, frechet.py, __init__.py, server.py, test, guard-sync literal) | Tracer — new aspect + register both |
| 72-02 | 2 | 2 (frechet.py, test file) | Single aspect build-out |
| 72-03 | 3 | 7 (3 aspects, __init__.py guard, 3 test files) | Three parallel extensions |
| 72-04 | 1 | 1 (test file) | Gate/verification only |

No plan exceeds 3 tasks; files modified are cohesive. Within context budget.

### Dimension 6: Verification Derivation

**PASS** — must_haves are grounded and user-observable:

- "build_diagnostics(ftsm_result, method='fts') returns dict with method=='fts'" — user-visible
- "Every value is native Python float/int/bool/list/None — no numpy scalar" — verifiable via check_no_numpy
- "json.dumps(diag) succeeds" — observable

### Dimension 7: Context Compliance

**PASS** — Plans strictly honor CONTEXT.md decisions:

- ✅ "Exactly ADV-01: new fts + frechet aspects; extend regression/classification/spm" — all four plans implement exactly this scope
- ✅ "Grounding invariant (hard): every diagnostic value native Python, no numpy scalars, cast every value" — all builders implement this pattern
- ✅ "Guard-sync atomicity: edits across all three mcp files land in ONE commit (ADV-02)" — Plan 72-01 declares this; see Blocker #1
- ✅ "fts + frechet are DIAGNOSTICS-ONLY" — Plan 72-01 explicitly guards against adding to _RUNNABLE_METHODS
- ✅ "No LLM in number path" — Plans declare and Plan 72-04 tests this

**Deferred ideas honored:** No plans include clustering advisor coverage, density_fda advisor coverage, or FRE-RUN-01 (promoting frechet to runnable) — all correctly deferred.

### Dimension 8: Nyquist Compliance (Automated Verify Specificity)

**PASS with note** — All `<automated>` blocks have `<fails_when>` clauses:

- Plan 72-01 Task 1: `grep -vE '^\s*#' ... | grep -Ec 'fts|frechet' | grep -qx 0` — counts fts/frechet in _RUNNABLE_METHODS, asserts count==0 (SC3)
- Plan 72-02 Task 1: `python -c "...assert d['has_frechet_mean'] is True..."` — live test of array path
- Plan 72-03 Task 2: `python -c "...assert d['method']=='classification'..."` — shapelet handle acceptance
- Plan 72-04 Task 1: `pytest tests/test_advisor_grounding.py ... -q` — combined gate

**Limitation:** The verify steps test outputs AFTER plans are written, but do not verify preconditions (like "read_first" steps) were met beforehand. See Blockers #2 and #3 below.

### Dimension 10: CLAUDE.md Compliance

**PASS** — No project-specific violations detected:

- No forbidden libraries introduced
- Aspect builders use only numpy (no anthropic/provider at build_diagnostics level)
- Grounding pattern mirrors existing regression.py discipline exactly
- Test structure mirrors existing test_advisor_*.py patterns

### Dimension 11: Research Resolution

**RESEARCH.md Status:** Open Questions 1-5 are explicitly flagged as HIGH-RISK assumptions requiring reading Rust source files before builder implementation:

1. Exact 9-key set for frechet_anova
2. Exact 3-key set for frechet_global_reg / frechet_local_reg
3. Exact 7-key set for fam / fregre_gsam
4. fof_re_regression 13 keys beyond random_effects/sigma2_u/n_subjects
5. mfpca scales type and grid_sizes type

Plans 72-02 and 72-03 declare "READ src/frechet_mod.rs" and "READ src/scalar_on_function_mod.rs" as preconditions but do not verify the reads happened. **This is Blocker #2.**

---

## Blockers (Must Fix Before Execution)

### BLOCKER #1: Guard-Sync Atomicity Not Proactively Verified (Plan 72-01)

**Plan Statement:**
```
ATOMICITY: all five files (fts.py, frechet.py, __init__.py, server.py, guard-sync test)
land in ONE commit per ADV-02 — the guard-sync test must never observe advisor._supported
and _EXPECTED_DIAGNOSTICS_METHODS disagreeing.
```

**What the Plan Does:**
- Action: Creates all five files
- Verify: Runs `pytest tests/test_guard_sync_version_independent.py` after all files are modified

**What the Plan Doesn't Do:**
- Does NOT check that all five files were staged/committed together
- Does NOT prevent an executor from committing them in two stages:
  - Stage 1: fts.py + frechet.py + test files
  - Stage 2: __init__.py + server.py + guard-sync literal

**Runtime Consequence:**
- Between stages, the guard-sync test will FAIL
- CI pipeline breaks (or rollback required)
- The verify step in the plan only runs AFTER all edits, masking the inter-stage failure window

**Severity:** MEDIUM — The guard-sync test will eventually catch the mistake (when all files are present), but the phase execution timeline is broken if stages separate.

**Required Fix:**

Add an explicit commit-stage verification to Plan 72-01's verify section:

```xml
<verify>
  <automated>
\
git log -1 --pretty=format:%B | grep -Eq 'ADV-01|Phase 72|Advisor.*fts.*frechet' && \
git show HEAD:python/fdars/advisor/__init__.py | grep -q '"fts"' && \
git show HEAD:python/fdars/mcp/server.py | grep -q '"fts"' && \
git show HEAD:tests/test_guard_sync_version_independent.py | grep -q '"fts"' && \
echo "Atomicity verified: all 3 guard-sync locations in same HEAD commit"
  </automated>
  <fails_when>Not all three guard-sync locations (advisor __init__.py, mcp server.py, guard-sync literal) appear in the same commit.</fails_when>
</verify>
```

This check runs AFTER the commit is landed, ensuring the commit message + all three frozenset edits arrived together.

---

### BLOCKER #2: "read_first" Preconditions Not Verified (Plans 72-02, 72-03)

**Plan Statements:**

Plan 72-02 Task 1:
```
<read_first>
- src/frechet_mod.rs:95-110 (frechet_anova 9 keys — CONFIRMED: statistic, p_value_asymptotic, ...)
```

Plan 72-03 Task 1:
```
<read_first>
- src/regression_mod.rs:1295-1304 (fof_regression keys — CONFIRMED: beta_surface, fitted, ...)
- src/scalar_on_function_mod.rs:107-117 (fam keys — CONFIRMED: fitted_values, residuals, ...)
```

**What the Plans Do:**
- Action: Describe the builder branches using the keys listed in `<read_first>`
- Verify: Run live tests (frechet_mean(space='spd'), fof_regression(data), fam(data)) and assert build_diagnostics produces correct output

**What the Plans Don't Do:**
- Do NOT verify that the keys listed in `<read_first>` actually exist in the Rust source
- Do NOT assert "I read the file and confirmed these exact keys are present"

**Runtime Consequence:**

If a key name has drifted since research time (e.g., Rust now has `"p_value_perm"` but plan assumes `"p_value_permutation"`):

1. The plan's verify runs the live test
2. frechet_mean returns a dict with actual keys `{"p_value_perm": 0.05, ...}`
3. The builder tries `has_anova = "p_value_permutation" in raw and ...`
4. Discriminator is False (key not found)
5. Builder returns `{"method": "frechet", has_anova: False, anova_p_value: None, ...}`
6. The test checks `assert d['has_frechet_mean'] is True` (a different result path)
7. Test passes (but wrong branch was taken)

The grounding test (check_no_numpy + json.dumps) would pass, and the numpy-scalar protection holds, but the diagnostic dict is _silently wrong_ (all anova fields are None when they shouldn't be).

**Severity:** HIGH — Silent failures: the plan's verify passes locally (because it's testing a different result shape), but the grounding invariant is maintained (all values are native Python). The _wrong_ path is taken without noise.

**Required Fix:**

Add a read_first verification gate to each task's verify section:

**Plan 72-02 Task 1:**
```xml
<verify>
  <automated>
cd /home/simonm/projects/rust/pyfda && \
grep -q 'set_item.*"p_value_permutation"' src/frechet_mod.rs && \
grep -q 'set_item.*"group_labels"' src/frechet_mod.rs && \
grep -q 'set_item.*"bandwidth"' src/frechet_mod.rs && \
grep -q 'set_item.*"predicted"' src/frechet_mod.rs && \
grep -q 'set_item.*"x_bar"' src/frechet_mod.rs && \
echo "All frechet discriminator keys confirmed in source"
  </automated>
  <fails_when>One or more keys expected by the builder are not found in src/frechet_mod.rs — indicates read_first precondition was not satisfied.</fails_when>
</verify>
```

**Plan 72-03 Task 1:**
```xml
<verify>
  <automated>
cd /home/simonm/projects/rust/pyfda && \
grep -q 'set_item.*"beta_surface"' src/regression_mod.rs && \
grep -q 'set_item.*"component_fits"' src/scalar_on_function_mod.rs && \
grep -q 'set_item.*"converged"' src/scalar_on_function_mod.rs && \
echo "All discriminator keys confirmed in regression/sof sources"
  </automated>
  <fails_when>Expected keys not found — read_first precondition was not satisfied.</fails_when>
</verify>
```

---

### BLOCKER #3: Shapelet Opaque-Handle Guard Placement Not Verified (Plan 72-03 Task 2)

**Plan Statement:**
```
In __init__.py: add a coercion guard in the block at lines 159-171, BEFORE 
the dict(raw) call, that converts the shapelet opaque handle to a dict.
```

**What the Plan Does:**
- Action: Describes what to add (hasattr check + dict conversion)
- Verify: Runs a live test building diagnostics from a shapelet_classifier_fit handle

**What the Plan Doesn't Do:**
- Does NOT specify the exact code location or line number
- Does NOT verify the guard is placed BEFORE dict(raw), not after

**Current Code at __init__.py:159-171:**
```python
if (
    not isinstance(raw, dict)
    and not hasattr(raw, "__array__")  # numpy arrays pass through unchanged
    and not hasattr(raw, "data")       # Fdata-like objects pass through unchanged
):
    raw = dict(raw)
```

**Risk Scenario:**

An executor adds the guard AFTER line 171:

```python
# ... existing code ...
if (...):
    raw = dict(raw)

# WRONG LOCATION: guard added here
if hasattr(raw, "train_accuracy") and hasattr(raw, "n_shapelets"):
    raw = {"train_accuracy": float(raw.train_accuracy), ...}
```

When `raw` is a PyShapeletClassifierFit opaque handle:
1. `isinstance(raw, dict)` → False
2. `hasattr(raw, "__array__")` → False
3. `hasattr(raw, "data")` → False
4. **Execute:** `raw = dict(raw)` ← **TypeError** (opaque PyO3 object, not convertible to dict)
5. Guard below never runs

Result: **The plan's verify catches the error** (live test fails with TypeError), but the error is due to incorrect placement, which could have been caught during verification if we checked the guard position.

**Severity:** MEDIUM — The live test will catch this (verify will fail), but it's an execution-time failure that verification should have prevented.

**Required Fix:**

Add an acceptance criterion and verify that checks guard placement:

```xml
<acceptance_criteria>
- __init__.py contains a shapelet opaque-handle coercion guard using `hasattr(raw, "train_accuracy")`
- The guard is placed BEFORE the `raw = dict(raw)` line, not after
- grep confirms: guard line number < dict(raw) line number
</acceptance_criteria>

<verify>
  <automated>
cd /home/simonm/projects/rust/pyfda && \
GUARD_LINE=$(grep -n 'hasattr.*train_accuracy' python/fdars/advisor/__init__.py | cut -d: -f1 | head -1) && \
DICT_LINE=$(grep -n 'raw = dict(raw)' python/fdars/advisor/__init__.py | cut -d: -f1 | head -1) && \
if [ -z "$GUARD_LINE" ]; then echo "Guard not found"; exit 1; fi && \
if [ -z "$DICT_LINE" ]; then echo "dict(raw) not found"; exit 1; fi && \
if [ "$GUARD_LINE" -lt "$DICT_LINE" ]; then \
  echo "Guard placement OK: line $GUARD_LINE < dict(raw) at line $DICT_LINE"; \
else \
  echo "Guard placement WRONG: line $GUARD_LINE >= dict(raw) at line $DICT_LINE"; \
  exit 1; \
fi
  </automated>
  <fails_when>The shapelet guard is not found, or it appears after the dict(raw) line.</fails_when>
</verify>
```

---

## Warnings (Should Fix)

### WARNING: LLM-Free Assertion May Lack Fallback (Plan 72-04)

**Plan Statement:**
```
add an explicit LLM-free assertion: in a fresh subprocess 
(subprocess.run(...)) import fdars.advisor, call build_diagnostics 
on an fts result, and assert "anthropic" not in sys.modules afterward
```

**What the Plan Does:**
- Uses subprocess.run() to run a fresh Python process
- Asserts "anthropic" not in sys.modules after calling build_diagnostics

**What the Plan Doesn't Do:**
- No fallback if subprocess is unavailable or subprocess.run() fails silently

**Risk Scenario (low probability but possible in CI):**

- Subprocess.run() is unavailable (e.g., containerized CI with sandboxing)
- Test silently skips or passes without running the subprocess check
- Plan verify passes locally, but CI LLM-free proof is incomplete

**Severity:** LOW — Very unlikely; Python's subprocess module is standard. But it's good practice to have a fallback.

**Recommended Fix (not required for execution):**

Add a module-load-time fallback check in test_advisor_grounding.py:

```python
def test_llm_free_import():
    """Fallback: assert build_diagnostics does not import anthropic at module load."""
    import sys
    # Clear anthropic if it's somehow loaded
    if "anthropic" in sys.modules:
        del sys.modules["anthropic"]
    
    # Import build_diagnostics — should not trigger anthropic import
    from fdars.advisor import build_diagnostics
    
    assert "anthropic" not in sys.modules, \
        "anthropic module should not be imported by build_diagnostics"
```

---

## Summary Table

| Issue | Severity | Plan | Category | Fix Complexity |
|-------|----------|------|----------|-----------------|
| Guard-sync atomicity not verified | BLOCKER | 72-01 | Process | 1 verify step, ~10 lines |
| frechet_anova keys not read_first verified | BLOCKER | 72-02 | Verification | 1 verify step, ~5 lines |
| fof/fam/mfpca keys not read_first verified | BLOCKER | 72-03 | Verification | 1 verify step, ~5 lines |
| Shapelet guard placement not verified | BLOCKER | 72-03 | Verification | 1 verify step, ~8 lines |
| LLM-free assertion lacks fallback | WARNING | 72-04 | Robustness | 1 test, ~5 lines (optional) |

**Total fix effort:** ~35 lines of shell/Python across 4 plans. Low risk; all fixes are additive verification, no logic changes.

---

## Recommendation

**RETURN TO PLANNER** with these three blockers.

The plans are otherwise well-designed:
- Clear tracer/build-out/extend/gate pattern ✅
- Comprehensive test coverage ✅
- Grounding discipline matched to regression.py ✅
- Guard-sync and SC3 constraints acknowledged ✅
- Dependency graph clean ✅

But the three blockers prevent confident execution:
1. Atomic commit atomicity can be split across stages without catching it until the gate runs
2. Key names are assumed based on research, not verified to actually exist in source
3. Shapelet guard placement is described but not verified

After fixes, proceed to execution.

**Next Step:** Planner revises PLAN.md files to add the three verify sections, re-submits to checker.

---

*Verification completed: 2026-09-04*  
*Gate Type: Revision Gate — plans returned for rework*  
*Iteration: 1 of 3 (bounded loop)*

---

## RE-VERIFICATION RESULT — Iteration 2

**Date:** 2026-09-04  
**Verification Gate:** Revision Gate — Re-Check After Planner Revisions  
**Status:** PASS — All four blockers resolved

### Finding 1: Guard-Sync Atomicity (Blocker 1, Plan 72-01)

**Prior Issue:** Verify section did not check that all three guard-sync files landed in a single atomic commit.

**Resolution:** Plan 72-01, Task 1 now includes a second `<automated>` block in the verify section that:
- Iterates over the three guard-sync file paths (advisor __init__.py, mcp server.py, test)
- Confirms each file exists in HEAD commit: `git show HEAD --stat --name-only | grep -qx "$f"`
- Confirms each file contains both 'fts' and 'frechet': `git show "HEAD:$f" | grep -q '"fts"'` and similar
- Fails with explicit "ATOMICITY FAIL" message if any file is missing or lacks the strings

**Verification Result:** ✓ **CLOSED** — Atomicity check now prevents split commits across stages.

---

### Finding 2: Key Drift Verification (Blocker 2, Plans 72-02 & 72-03)

**Prior Issue:** Plans declared `<read_first>` preconditions but had no verify gate confirming keys existed in Rust sources. Silent failures would occur if keys drifted.

**Resolutions:**

- **Plan 72-02, Task 1 verify section:** Added `<automated>` block that greps src/frechet_mod.rs for each discriminator key (p_value_permutation, group_labels, bandwidth, predicted, x_bar). Fails with "KEY DRIFT" message if any key is absent.

- **Plan 72-03, Task 1 verify section:** Added `<automated>` block that greps src/regression_mod.rs and src/scalar_on_function_mod.rs for fof/fam/gkam discriminator keys (beta_surface, random_effects, n_subjects, component_fits, fitted_values, converged, bandwidths).

- **Plan 72-03, Task 3 verify section:** Added `<automated>` block that greps src/spm_mod.rs for mfpca keys (eigenfunctions, scales, eigenvalues).

**Verification Result:** ✓ **CLOSED** — All three key-drift gates now verify preconditions before running live tests.

---

### Finding 3: Shapelet Guard Placement (Blocker 3, Plan 72-03 Task 2)

**Prior Issue:** Task 2 declared "add BEFORE dict(raw)" but did not verify the guard line number < dict(raw) line number.

**Resolution:** Plan 72-03, Task 2 verify section now includes an `<automated>` block that:
- Extracts the line number of the shapelet handle guard: `grep -n 'hasattr(raw, "train_accuracy")'`
- Extracts the line number of dict(raw): `grep -n 'raw = dict(raw)'`
- Compares: fails with explicit "Guard placement WRONG" message if guard line >= dict(raw) line
- Succeeds and outputs "Guard placement OK" if guard < dict(raw)

**Verification Result:** ✓ **CLOSED** — Guard placement is now verified at execution time.

---

### Finding 4: LLM-Free Assertion Fallback (Warning 4, Plan 72-04)

**Prior Issue:** LLM-free assertion relied only on subprocess with no fallback if subprocess was unavailable.

**Resolution:** Plan 72-04, Task 1 action section now includes:
- Explicit requirement to add a same-process fallback: "in-process, drop any pre-loaded provider modules (pop 'anthropic'/'openai' from sys.modules if present), call build_diagnostics(...) directly, then assert neither is in sys.modules afterward. Keep BOTH the subprocess assertion and the in-process fallback."

- The verify section now includes an `<automated>` block that confirms presence of both mechanisms via grep:
  - Checks for 'subprocess' string (subprocess assertion present)
  - Checks for 'sys.modules.pop\|del sys.modules' pattern (in-process module-clearing present)
  - Checks for '"openai"' string (fallback covers both openai and anthropic)

**Verification Result:** ✓ **CLOSED** — LLM-free proof now has dual fallback coverage.

---

### Revision Quality Confirmation

**Additive Only:** All revisions are purely additive:
- No task `<action>` logic changed
- No grounding field lists modified
- No guard-set contents changed
- No wave structure altered
- All new `<automated>` blocks carry `<fails_when>` clauses

**Blockers → Verification Gates:** Each prior blocker was resolved by adding an execution-time verification gate, not by changing phase logic or builders. The guards are narrow, specific, and fail loudly on precondition violations.

---

## Summary

| Issue | Prior Severity | Resolution | Status |
|-------|---|---|---|
| Guard-sync atomicity | BLOCKER | HEAD commit triple-check gate added to 72-01 Task 1 verify | CLOSED ✓ |
| Key drift (frechet/regression/spm) | BLOCKER | Discriminator key grep gates added to 72-02 Task 1, 72-03 Tasks 1 & 3 | CLOSED ✓ |
| Shapelet guard placement | BLOCKER | Line-number comparison gate added to 72-03 Task 2 verify | CLOSED ✓ |
| LLM-free fallback | WARNING | Subprocess + in-process dual fallback required in 72-04 Task 1; verify confirms both | CLOSED ✓ |

---

## FINAL VERDICT: **PASS**

All four prior findings are now **RESOLVED**. The plans are ready for execution.

- Requirements: All four plans still map to ADV-01, ADV-02, SC3 ✓
- Task completeness: Now includes precondition verification gates ✓
- Dependency correctness: Wave structure unchanged ✓
- Key links: Wiring still explicit, guard placement now verified ✓
- Scope sanity: No change ✓
- Verification derivation: Strengthened with precondition gates ✓
- Context compliance: No changes to logic, only verification gates ✓
- Nyquist compliance: All new `<automated>` blocks have `<fails_when>` ✓
- CLAUDE.md compliance: No changes to implementation patterns ✓
- Research resolution: Preconditions now verified ✓

**No regressions detected.** Proceed to `/gsd-execute-phase 72`.

---

*Re-verification completed: 2026-09-04*  
*Gate Type: Revision Gate — plans approved*  
*Iteration: 2 of 3 (final iteration)*
