---
phase: 51-comparative-method-selection
reviewed: 2026-08-24T00:00:00Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - python/fdars/advisor/_compare_methods.py
  - python/fdars/advisor/__init__.py
  - python/fdars/advisor/_prompts.py
  - python/fdars/mcp/_compare_methods.py
  - python/fdars/mcp/server.py
  - tests/test_compare_methods.py
  - tests/test_compare_methods_advise.py
  - tests/test_mcp_compare_methods.py
findings:
  critical: 3
  warning: 5
  info: 0
  total: 8
status: resolved
---

# Phase 51: Code Review Report

**Reviewed:** 2026-08-24
**Depth:** deep
**Files Reviewed:** 7 source + 3 test files (10 total reviewed; 8 are production source)
**Status:** issues_found

## Summary

Phase 51 delivers the deterministic comparative method-selection feature: `compare_methods()` (advisor entry point + LLM narration path), `compare_methods_mcp()` (LLM-free MCP helper), and the `fdars_compare_methods` MCP tool registration. The grounding invariant (winner fixed before any LLM call) is structurally sound, and the incommensurability guard fires correctly for mixed task families and missing metrics. The MCP tool is provably LLM-free and the method allowlist is enforced before any run.

Three blockers require fixes before this ships. Five warnings degrade robustness or correctness of edge-case paths.

---

## Critical Issues

### CR-01: `argvals` and `**kwargs` accepted but silently dropped — raw clustering/alignment results produce wrong diagnostics

**File:** `python/fdars/advisor/_compare_methods.py:316-317, 182`

**Issue:** `compare_methods()` accepts `argvals` and `**kwargs` in its public signature (lines 316–317), documented as "forwarded to `build_diagnostics` when building diagnostics from raw result dicts." But `_normalize_candidates()` — the only code path that calls `build_diagnostics` — calls it at line 182 without those arguments:

```python
diag = build_diagnostics(value, method)   # argvals and **kwargs not forwarded
```

For clustering and alignment raw results, `build_diagnostics` uses `argvals` to compute amplitude/phase distance metrics (e.g. `mean_amplitude_separation`). Without `argvals`, these keys are `None`. Because `mean_amplitude_separation` is the default ranking metric for clustering, a caller who supplies `argvals` and raw clustering result dicts will silently get `None` for every candidate's metric, triggering the incommensurability guard with a confusing "metric absent" error even though the data is valid and `argvals` was correctly passed.

**Fix:**
```python
# _normalize_candidates signature
def _normalize_candidates(
    candidates: "dict | list",
    method: "str | None",
    argvals=None,
    **kwargs,
) -> "list[dict]":
    ...
    # line 182
    diag = build_diagnostics(value, method, argvals=argvals, **kwargs)
```

And in `compare_methods()`, forward `argvals` and `kwargs` to `_normalize_candidates`:
```python
blocks = _normalize_candidates(candidates, method, argvals=argvals, **kwargs)
```

---

### CR-02: Bare `assert` in production code in `_rank()` — disabled by `-O`, corrupts sort under optimization

**File:** `python/fdars/advisor/_compare_methods.py:281`

**Issue:** The sort key function inside `_rank()` contains:

```python
assert val is not None  # guard already ran; this must hold
```

Python's `-O` (optimize) flag strips all `assert` statements. In an optimized build (e.g. production wheels compiled with `-OO`), this assertion is silently omitted. If `val` is `None` — which can happen if the diagnostics dict is mutated between the guard check and the sort (e.g. by a threaded caller or a shared mutable dict) — the code proceeds to:

```python
sort_val = -val if reverse else val   # -None raises TypeError silently in sort
```

This produces a `TypeError` deep inside `list.sort()` with an opaque message, not a guarded `ValueError`. More critically, the comment "guard already ran; this must hold" creates false confidence: `assert` is the wrong mechanism to enforce an invariant in library code.

**Fix:**
```python
def sort_key(item: tuple[int, dict]) -> tuple[float, int]:
    idx, block = item
    val = _extract_metric_value(block["diagnostics"], metric)
    if val is None:
        raise ValueError(
            f"compare_methods: internal error — metric {metric!r} became None "
            f"for candidate {block['label']!r} during sort. "
            "Do not mutate diagnostics dicts while compare_methods() is running."
        )
    sort_val = -val if reverse else val
    return (sort_val, idx)
```

---

### CR-03: `IndexError` on empty `candidates` when `metric` is explicitly supplied

**File:** `python/fdars/advisor/_compare_methods.py:299`

**Issue:** When `candidates` is `{}` or `[]` and a `metric` is explicitly passed (bypassing the family-lookup branch that would catch the empty family), the execution path is:

1. `_normalize_candidates({})` → `blocks = []`
2. `families = set()` → `len(families)` is 0 → mixed-family guard skipped
3. `family = ""` (no families)
4. `metric` is not `None` → registered metric check passes (e.g. `"mean_amplitude_separation"` is valid)
5. `_assert_commensurable([], resolved_metric)` → no offenders, no families → passes without error
6. `_rank([], resolved_metric)` → `ranking = []` → `ranking[0]` → **`IndexError: list index out of range`**

The error message is opaque and does not name the actual cause (empty candidate set).

**Fix:** Add an early guard after normalisation:
```python
blocks = _normalize_candidates(candidates, method)

if not blocks:
    raise ValueError(
        "compare_methods: 'candidates' is empty. "
        "Pass at least two candidates for a valid comparison."
    )
```

---

## Warnings

### WR-01: Label uniquification in `compare_methods_mcp()` produces duplicate labels in an edge case

**File:** `python/fdars/mcp/_compare_methods.py:164-173`

**Issue:** The deduplication loop counts raw label occurrences using `raw_labels.count(raw)`. This is O(n²) per label but more critically, when a label that already contains a bracket suffix (e.g. `"clustering[0]"`) appears alongside two identical bare labels (e.g. `["a[0]", "a", "a"]`), the suffix appended to the bare labels collides with the pre-existing label:

```python
# raw_labels = ['a[0]', 'a', 'a']
# Loop output:
#   'a[0]': count==1, appends 'a[0]'  (no suffix)
#   'a': count==2, first → 'a[0]'     <- COLLISION
#   'a': count==2, second → 'a[1]'
# labels = ['a[0]', 'a[0]', 'a[1]']  — duplicate!
```

The duplicate label then silently overwrites the first `labeled_result_ids["a[0]"]` entry, so the first candidate's `result_id` is lost and the ranking entry for `"a[0]"` points to the wrong stored result.

Verified to produce duplicates:
```
Labels: ['a[0]', 'a[0]', 'a[1]']
len(labels) != len(set(labels)): True
```

In practice this only triggers when user-controlled MCP `method` strings contain bracket characters, which is unusual for the six allowed runnable methods. But the label derivation also calls `_make_label(method, {}, index)` which produces `"clustering[0]"` — so two empty-param candidates plus one with conflicting label would trigger it.

**Fix:** Use a two-pass deduplication approach that guarantees uniqueness regardless of suffix collisions:
```python
# First pass: count occurrences per raw label
from collections import Counter
count_per_raw = Counter(raw_labels)
seen = {}
labels = []
for raw in raw_labels:
    if count_per_raw[raw] > 1:
        n = seen.get(raw, 0)
        seen[raw] = n + 1
        candidate = f"{raw}[{n}]"
    else:
        candidate = raw
    # Guarantee uniqueness even against pre-existing labels
    while candidate in labels:
        candidate = f"{candidate}_dup"
    labels.append(candidate)
```

---

### WR-02: Docstring falsely declares `NotImplementedError` for `run_llm=True`

**File:** `python/fdars/advisor/_compare_methods.py:389-390`

**Issue:** The public docstring's `Raises` section states:

```
NotImplementedError
    When ``run_llm=True`` (Plan 02 not yet implemented).
```

The LLM path is fully implemented in the same file (lines 451–505). This is a copy-paste from an earlier stub that was not removed after Plan 02 was completed. Any caller reading the docstring will conclude `run_llm=True` raises and will not attempt to use it.

**Fix:** Remove the `NotImplementedError` entry from the `Raises` block. The `run_llm=True` path raises `GroundingViolationError` (propagated from `_check_grounding`) if the LLM fabricates values — that is the only additional raise path compared to `run_llm=False`, and it should be documented instead.

---

### WR-03: Per-candidate grounding check always fails for any recommendation with candidate-specific numeric evidence

**File:** `python/fdars/advisor/_compare_methods.py:498-499`

**Issue:** The per-candidate grounding loop (lines 498–499):

```python
for block in provenance_blocks:
    _check_grounding(advice, block["diagnostics"])
```

calls `_check_grounding(advice, diag_for_candidate_X)` for **all** candidates in sequence. `_check_grounding` iterates **all** `advice.recommendations` and checks **every** evidence string against the single candidate's diagnostics numbers. This means:

- A recommendation whose evidence legitimately says `"candidate_A amplitude separation = 0.91"` passes the check against `diag_A` (0.91 is present).
- The same evidence string then fails the check against `diag_B` (0.91 is not in B's diagnostics) and raises `GroundingViolationError`.

Any real LLM narration that includes candidate-specific numbers in recommendation evidence strings — which is the expected output of a comparative narration — will always raise `GroundingViolationError` in the second (or later) pass, making the `run_llm=True` path unusable in practice for the core comparison use case.

The tests avoid detecting this because the mock `_make_advice()` fixtures use `recommendations=[]` (no evidence strings) — so the loop body is never entered.

**Fix:** The grounding check for a multi-candidate comparison must be scoped per recommendation, matching each recommendation's evidence against the diagnostics of the candidate it discusses. The simplest safe alternative is to check all evidence against the union of all candidates' diagnostics:

```python
# Build the union of all diagnostic numbers across all candidates
merged_diagnostics = {}
for block in provenance_blocks:
    merged_diagnostics.update(block["diagnostics"])
_check_grounding(advice, merged_diagnostics)
```

This preserves the intent (evidence must cite a real number from some candidate's diagnostics) while not false-positiving on cross-candidate narration. Alternatively, route per-recommendation grounding by label-matching the recommendation text to one candidate's block, but that requires more structural changes.

---

### WR-04: `_assert_commensurable` Guard 1 is dead code

**File:** `python/fdars/advisor/_compare_methods.py:212-220`

**Issue:** `_assert_commensurable()` contains Guard 1 (mixed task families check, lines 212–220). However, `compare_methods()` performs an identical mixed-family check at lines 402–408 **before** calling `_assert_commensurable()`. Guard 1 in `_assert_commensurable` is therefore unreachable — the `compare_methods()` caller always raises first.

This is not a runtime bug but creates false confidence: `_assert_commensurable` appears to be a self-contained safety function but silently delegates its primary guard responsibility to its caller. If `_assert_commensurable` is ever called from another code path (e.g. a future refactor), Guard 1 will appear to work but Guard 2 (metric presence) could still execute on mixed-family blocks, producing a misleading "metric absent" error instead of "mixed families."

**Fix:** Either remove Guard 1 from `_assert_commensurable` (making clear the function only checks metric presence) and update the docstring, or remove the duplicate check from `compare_methods()` and rely solely on `_assert_commensurable`. Given the function's name, the cleaner fix is to keep all commensurability logic in `_assert_commensurable` and call it before the metric resolution step in `compare_methods()`.

---

### WR-05: `candidate_params: list` in `fdars_compare_methods` tool loses MCP JSON schema specificity

**File:** `python/fdars/mcp/server.py:431`

**Issue:** The MCP tool handler uses `candidate_params: list` (bare, unparameterized). The MCP framework reflects Python type annotations to generate the JSON schema used for tool input validation. `list` generates `{"type": "array"}` with no item constraint; `list[dict]` would generate `{"type": "array", "items": {"type": "object"}}`. Without the element type, MCP clients have no schema-level guidance that each entry must be a JSON object, and the allowlist validation inside `compare_methods_mcp()` is the only enforcement layer — which runs server-side and produces an error rather than a schema-level rejection at the client.

**Fix:**
```python
def fdars_compare_methods(
    dataset_id: str,
    method: str,
    candidate_params: list[dict],   # was: list
    metric: str | None = None,
) -> dict:
```

Note: the `compare_methods_mcp()` signature in `_compare_methods.py` already correctly uses `list[dict]` — this is only a fix needed for the server.py tool boundary.

---

## Structural Findings (fallow)

No structural pre-pass was provided for this review.

---

_Reviewed: 2026-08-24_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
