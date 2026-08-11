---
phase: 10-advisor-core-primitive
verified: 2026-08-09T19:03:45Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 10: Advisor Core Primitive Verification Report

**Phase Goal:** A single deterministic diagnostics engine plus a grounded LLM advisor exists in `python/fdars/advisor.py` — the shared core every downstream surface builds on.
**Verified:** 2026-08-09T19:03:45Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `build_diagnostics` covers all five methods (alignment, fpca, basis, smoothing, clustering), is offline, deterministic, and JSON-serialisable — two runs on the same input return an identical dict | VERIFIED | Runtime: all five branches pass two-call equality assert; `json.dumps` succeeds on every branch output; all values are plain Python types (float, list, bool, int, None) |
| 2 | With `anthropic` uninstalled, importing `fdars.advisor` and calling `build_diagnostics` both succeed; calling `advise` raises `ImportError` whose message names `pip install fdars[advisor]` | VERIFIED | Runtime confirm: `_require_anthropic()` raises `ImportError` with message "Install it with: pip install fdars[advisor]" and "anthropic>=0.72.0"; module imports cleanly; `build_diagnostics` runs without anthropic; full surface gate passes |
| 3 | `advise(diagnostics, task, domain_context)` is wired to `client.messages.parse(model="claude-opus-4-8", output_format=Advice, thinking={"type": "adaptive"})` and returns `response.parsed_output` | VERIFIED | AST: `advise()` calls `_require_anthropic()` first; `client.messages.parse` call found with `model=model`, `max_tokens=16000`, `thinking={'type': 'adaptive'}`, `output_format=Advice`; return value is `parsed` (which is `response.parsed_output`); null guard added (CR-02 fix) |
| 4 | Every `Recommendation` carries `action`, `kind` (Literal["parameter","method","none"]), `rationale`, `expected_effect`, `evidence: list[str]`; `Advice` carries `interpretation`, `recommendations`, `caveats` — the grounding invariant is encoded by both schema and system prompt | VERIFIED | Code: Pydantic `Recommendation` fields (action, kind, rationale, expected_effect, evidence) and `Advice` fields (interpretation, recommendations, caveats) confirmed; fallback plain-Python classes have identical fields; `_system_prompt` encodes invariant: "reason only from diagnostics provided", "every evidence item must cite a specific diagnostic value", "Omit any claim not supported", "Never fabricate numbers or invent values not present" — all greppable |
| 5 | `describe_cluster_differences` is a specialization built on `build_diagnostics(method='clustering')` (not a reimplementation); exported in `__all__`; offline with `run_llm=False`; calls `advise(task='interpretation')` with `run_llm=True` | VERIFIED | AST confirms `describe_cluster_differences` body calls only `build_diagnostics` and `advise`; runtime `run_llm=False` returns `{"method": "clustering", ...}` dict; in `__all__`; function does not re-implement distance or mean computation |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `python/fdars/advisor.py` | New pure-Python module with Advice/Recommendation Pydantic models, `build_diagnostics` (all 5 methods), `advise`, `describe_cluster_differences`, `__all__` | VERIFIED | File exists, 1135 lines; all public symbols present; `__all__` is exactly `{'build_diagnostics', 'advise', 'describe_cluster_differences', 'Advice', 'Recommendation'}` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `advise` | lazy anthropic import guard | `_require_anthropic()` called first inside `advise` before any other work | WIRED | AST verified: `_require_anthropic()` is the first call in `advise()` |
| `advise` | `client.messages.parse(output_format=Advice)` | `anthropic.Anthropic().messages.parse(...)` | WIRED | AST verified: call present with all required kwargs |
| `advise` | `.parsed_output` | `response.parsed_output` + null guard | WIRED | Code line 975: `parsed = response.parsed_output`; null check on line 976 (CR-02 fix) |
| `_system_prompt` | grounding invariant text | string literals with "reason only", "every evidence item must cite", "Never fabricate numbers" | WIRED | Grep confirms all invariant tokens present verbatim |
| `describe_cluster_differences` | `build_diagnostics(method='clustering')` | direct call in function body | WIRED | AST: function body calls only `build_diagnostics` and `advise` |
| `_require_anthropic` | `ImportError` with `pip install fdars[advisor]` | try/except ImportError with message construction | WIRED | Runtime confirms message text |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Plan Task 1 gate: all symbols present | AST symbol check (from 10-01-PLAN) | "OK all symbols present" | PASS |
| Plan Task 2 gate: grounding prompt | AST + string check (from 10-01-PLAN) | "OK grounding prompt present" | PASS |
| Plan Task 2 gate (10-03): full surface deterministic + ImportError-guarded | Runtime five-method determinism loop | "OK full surface deterministic + ImportError-guarded (anthropic absent)" | PASS |
| Plan Task 3 gate (10-02): three task families + unknown-task ValueError | Runtime `_system_prompt` checks | "OK three task families + unknown-task ValueError" | PASS |
| alignment build_diagnostics | Two-call equality on synthetic dict | Equal, JSON-serialisable, method="alignment" | PASS |
| fpca build_diagnostics | Two-call equality | Equal, JSON-serialisable, variance/eigenvalue keys present | PASS |
| basis build_diagnostics | Two-call equality | Equal, JSON-serialisable, GCV/optimal_n_basis keys present | PASS |
| smoothing build_diagnostics | Two-call equality | Equal, JSON-serialisable, GCV/optimal_lambda keys present | PASS |
| clustering build_diagnostics | Two-call equality | Equal, JSON-serialisable, cluster_means/pairwise keys present | PASS |
| unsupported-method ValueError lists all 5 | `build_diagnostics({}, method='bogus')` | "Supported: ['alignment', 'basis', 'clustering', 'fpca', 'smoothing']" | PASS |
| describe_cluster_differences offline path | `run_llm=False` | Returns dict with `method='clustering'`; JSON-serialisable | PASS |
| describe_cluster_differences specialization | AST: calls `build_diagnostics` | Confirmed — only calls `build_diagnostics` and `advise` | PASS |
| CORE-04 ImportError message | `_require_anthropic()` with anthropic absent | "pip install fdars[advisor]" + "anthropic>=0.72.0" present | PASS |
| Anthropic not imported at module top level | Top-level AST import scan | Only `__future__`, `json`, `typing`, `numpy` at module top level | PASS |
| No hardcoded API key | `grep api_key` in advisor.py | No matches — API key read from env by `anthropic.Anthropic()` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| CORE-01 | 10-01-PLAN, 10-02-PLAN | `build_diagnostics` deterministic + offline for alignment, fpca, basis, smoothing, clustering | SATISFIED | All five branches verified deterministic and JSON-serialisable at runtime |
| CORE-02 | 10-01-PLAN | `advise` returns schema-validated `Advice` via `client.messages.parse(model="claude-opus-4-8")` | SATISFIED | AST confirms `messages.parse` with `output_format=Advice`, `model=model` (default "claude-opus-4-8") |
| CORE-03 | 10-01-PLAN | Every `Recommendation` carries action, kind, rationale, expected_effect, evidence[] | SATISFIED | Pydantic model fields confirmed; fallback class has identical constructor signature |
| CORE-04 | 10-01-PLAN | Import succeeds without anthropic; `build_diagnostics` works; `advise` raises clear `ImportError` | SATISFIED | Runtime: ImportError raised with "pip install fdars[advisor]" + version floor; module imports without anthropic; build_diagnostics runs offline |
| CORE-05 | 10-03-PLAN | `describe_cluster_differences` is a specialization built on `build_diagnostics` | SATISFIED | AST: function body calls only `build_diagnostics` + `advise`; does not re-implement diagnostics |
| ADVISE-01 | 10-01-PLAN | Interpretation task family: explains what a result means in domain terms | SATISFIED | `_system_prompt('interpretation')` returns 1863-char prompt with FDA primer and interpretation task clause; `task="interpretation"` is a valid path through `advise` |
| ADVISE-02 | 10-02-PLAN | Parameter guidance: recommends lambda_, n_basis, bandwidth, n_comp, cluster k, depth method | SATISFIED | `_system_prompt('parameter')` contains all named knobs; parameter clause present and greppable |
| ADVISE-03 | 10-02-PLAN | Method guidance: flags poor-fit methods and suggests alternatives | SATISFIED | `_system_prompt('method')` contains all three mappings (elastic, pre-smooth, transform) |

**Note on REQUIREMENTS.md checkbox state:** CORE-02, CORE-03, CORE-04, and ADVISE-01 show `[ ]` (Pending) in REQUIREMENTS.md and the traceability table. This is a tracking discrepancy — the implementations are verified in the codebase. The CORE-04 partial-delivery split (the `[advisor]` extra in `pyproject.toml` is Phase 11; the version floor and ImportError behaviour are Phase 10) is documented in the ROADMAP Phase 10 notes, and the scope note for this verification explicitly excludes the `pyproject.toml` extra from Phase 10's scope. The REQUIREMENTS.md checkboxes should be updated when Phase 11 completes.

### Anti-Patterns Found

| File | Pattern | Severity | Assessment |
|------|---------|----------|------------|
| `python/fdars/advisor.py` line 142, 171 | `return NotImplemented` | Info | These are `__eq__` dunder methods on the fallback Pydantic stand-in classes — `NotImplemented` is the correct Python protocol return for type mismatch. Not a stub; not a blocker. |

No TBD, FIXME, XXX, or unreferenced debt markers found in `advisor.py`.

### Deferred Items (Not Phase 10 scope)

Items explicitly deferred to later phases per ROADMAP and scope notes — not counted as gaps:

| Item | Addressed In | Evidence |
|------|-------------|----------|
| `[advisor]` optional-dependency extra in `pyproject.toml` (declaring `anthropic>=0.72.0`) | Phase 11 | ROADMAP Phase 10 notes + Phase 11 SC #2: "`pip install fdars[advisor]` installs `anthropic`; the extra is declared in `pyproject.toml`" |
| Public API registration of `fdars.advisor` in `__init__.py` | Phase 11 | Phase 11 SC #1: "build_diagnostics, advise, and describe_cluster_differences are reachable from the public fdars API" |
| Unit tests and integration tests | Phase 11 | Phase 11 SC #3 and #4 |
| Recipe page in `examples/` | Phase 11 | Phase 11 SC #5 |

### Gaps Summary

No gaps. All five roadmap success criteria are met by the implementation in `python/fdars/advisor.py`.

---

_Verified: 2026-08-09T19:03:45Z_
_Verifier: Claude (gsd-verifier)_
