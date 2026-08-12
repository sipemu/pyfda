---
phase: 19-provider-foundation-grounding-contract
plan: "01"
subsystem: advisor
tags: [provider-protocol, refactor, grounding, anthropic, pure-python]
requirements:
  - PROV-01
  - PROV-02
  - PROV-06
  - GROUND-01
  - GROUND-02
  - GROUND-03
  - GROUND-04
depends_on: []
provides:
  - advisor/ package with Provider protocol
  - AnthropicProvider adapter
  - ValidateAndRetry wrapper
  - _check_grounding centralized validator
  - resolve_provider factory
affects:
  - python/fdars/advisor/
  - tests/test_advisor.py (unchanged, stays green)
tech_stack:
  added:
    - typing.Protocol (runtime_checkable) for Provider interface
  patterns:
    - Deferred import tower: advise() -> resolve_provider() -> AnthropicProvider.__init__() -> _require_anthropic()
    - ValidateAndRetry proxy pattern (native path: direct; non-native: validate+repair up to MAX_RETRIES=2)
    - Centralized grounding check in advise() caller, not in adapter
key_files:
  created:
    - python/fdars/advisor/__init__.py (moved from advisor.py, then wired to providers/)
    - python/fdars/advisor/providers/__init__.py
    - python/fdars/advisor/providers/_protocol.py
    - python/fdars/advisor/providers/_validate.py
    - python/fdars/advisor/providers/_factory.py
    - python/fdars/advisor/providers/anthropic.py
  modified:
    - python/fdars/advisor/__init__.py (advise() wired through Provider; describe_cluster_differences gets provider= param)
decisions:
  - "Kept all non-provider code in advisor/__init__.py (prompt, schema, builders) — structural split deferred to 19-02 as planned"
  - "providers/__init__.py imports AnthropicProvider at module level (safe: anthropic.py has no top-level SDK import; SDK is deferred to __init__)"
  - "The _require_anthropic()/_require_pydantic() guards stay in advisor/__init__.py (not moved) so AnthropicProvider imports them from there — preserves the sys.modules monkeypatch chain"
metrics:
  duration: "~46 minutes"
  completed: "2026-08-12"
  tasks: 3
  commits: 3
  files_changed: 6
status: complete
actuals:
  tokens: 52000
  tasks: 3
  commits: 3
---

# Phase 19 Plan 01: Provider Foundation Tracer Summary

**One-liner:** Convert `advisor.py` to `advisor/` package and wire `advise()` end-to-end through `Provider` protocol + `AnthropicProvider` + `ValidateAndRetry` + `_check_grounding`, with `pytest tests/test_advisor.py` green throughout.

## What Changed

### Task 1 — advisor.py → advisor/ package (commit `ed121f6`)

`python/fdars/advisor.py` was moved verbatim to `python/fdars/advisor/__init__.py` and the original deleted. No logic changed. The `sys.modules["fdars.advisor"] = advisor` injection in `python/fdars/__init__.py` continues to resolve automatically because Python resolves `from fdars import advisor` to `advisor/__init__` when `advisor/` is a directory.

### Task 2 — providers/ layer (commit `00c73b7`)

Five new files under `python/fdars/advisor/providers/`:

- `_protocol.py`: `@runtime_checkable Provider(Protocol)` with `name`, `model`, `supports_native_structured_output`, and `complete_structured(schema, messages, system)`.
- `anthropic.py`: `AnthropicProvider` — `name="anthropic"`, `supports_native_structured_output=True`. `__init__` calls `_require_anthropic()` (deferred via `from fdars.advisor import _require_anthropic` inside the method body — the `sys.modules["anthropic"]=None` monkeypatch fires here). `complete_structured` calls `client.messages.parse(model=..., max_tokens=16000, thinking={"type": "adaptive"}, system=..., output_format=schema, messages=...)` — identical parameters to the old inline block. Raises `ValueError` on `response.parsed_output is None` (GROUND-04).
- `_validate.py`: `ValidateAndRetry(provider)` — native path returns result directly; non-native path runs Pydantic `model_validate` + repair retry up to `MAX_RETRIES=2`, then raises deterministically (GROUND-02). Also exports `_check_grounding(advice, diagnostics)`, `GroundingViolationError`, and the numeric-extraction helpers.
- `_factory.py`: `resolve_provider(provider, model, api_key, base_url)` — precedence: explicit params > `FDARS_ADVISOR_PROVIDER`/`FDARS_ADVISOR_MODEL`/`FDARS_ADVISOR_BASE_URL` env > Anthropic default. Unknown provider names raise `ValueError`. Returns `ValidateAndRetry(adapter)`.
- `__init__.py`: Exports `Provider`, `AnthropicProvider`, `ValidateAndRetry`, `resolve_provider`, `_check_grounding`, `GroundingViolationError`.

### Task 3 — Wire advise() (commit `c556a5d`)

`advise()` in `advisor/__init__.py`:
- Gains `provider: "str | object | None" = None` keyword parameter after `model`.
- Replaces the inline Anthropic call block with `resolve_provider(provider=provider, model=model)` → `p.complete_structured(Advice, messages, system)`.
- Calls `_check_grounding(advice, diagnostics)` immediately after `complete_structured` returns — centralized, runs on every provider path (GROUND-03).
- `_require_pydantic()` still called eagerly; `resolve_provider` and `_check_grounding` imported lazily inside the function body so `import fdars` never touches an LLM SDK.

`describe_cluster_differences()` gains `provider=None` parameter forwarded to `advise()`.

## Test Results

```
pytest tests/test_advisor.py -x -q
4 passed, 1 skipped in 2.43s
```

All 4 offline tests pass including `test_advise_raises_importerror_without_anthropic` (sys.modules monkeypatch). Integration test skipped (no `ANTHROPIC_API_KEY` in CI).

## Deviations from Plan

### Known Deviation: grep "reason only from" returns 2, not 1

**Found during:** Task 3 verification.

**Issue:** The plan's `<verify>` check `grep -rn "reason only from" python/fdars/advisor/ | wc -l | grep -qx 1` expects 1 match. The original `advisor.py` (now `advisor/__init__.py`) contains the phrase at two locations:
1. Line 836: system prompt sentence "You reason only from the diagnostics provided in the user message."
2. Line 1002: user content label "Diagnostics (reason only from these values):\n"

**Root cause:** The plan was written assuming the `_prompts.py` / user-content split (Phase 19-02) would precede this check. In the tracer (19-01), both strings remain in `__init__.py` because the structural split is deferred to 19-02.

**Impact:** None on correctness or tests. The system prompt invariant sentence IS unique (only one copy of the full invariant). The user-content label is a different phrase. The grep check is a proxy for "no duplicate system prompt invariant" that happens to also match the user label.

**Resolution:** Phase 19-02 will extract `_system_prompt()` into `_prompts.py` and the user content format into its own location, after which the grep count will be 1 as intended.

**Tracking:** None — this is a known, intentional tracer limitation, not a defect.

## Architecture Verified

- `advise()` end-to-end path: `advise()` → `resolve_provider()` → `AnthropicProvider.complete_structured()` → `ValidateAndRetry` (native pass-through) → `_check_grounding()` → return `Advice`.
- `provider=None` produces `ValidateAndRetry(AnthropicProvider(model="claude-opus-4-8"))` — identical to old inline behavior.
- `import fdars` with `anthropic` absent: succeeds. `build_diagnostics()` works fully offline.
- `advise()` with `sys.modules["anthropic"]=None`: raises `ImportError("pip install fdars[advisor]")` — monkeypatch chain intact through `_require_anthropic()` in `advisor/__init__.py` called from `AnthropicProvider.__init__`.

## Self-Check: PASSED

All artifacts confirmed present on disk; all 3 commits exist in git history. Final `pytest tests/test_advisor.py`: 4 passed, 1 skipped.
