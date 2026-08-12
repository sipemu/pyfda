---
phase: 20-additional-provider-adapters
plan: "02"
subsystem: advisor-providers
tags: [ollama, provider-adapters, structured-output, offline-tests, shim-cleanup, non-native-path]
status: complete

depends_on: [20-01]
provides:
  - ollama-adapter
  - non-native-validate-retry-path-coverage
  - factory-shim-cleanup-ollama
affects:
  - python/fdars/advisor/providers/ollama.py
  - python/fdars/advisor/providers/_factory.py
  - tests/test_advisor_ollama.py
  - tests/test_advisor_providers.py

tech_stack:
  added:
    - "ollama>=0.6.2 (extra, not installed in venv; SDK absent = deferred guard fires)"
  patterns:
    - "supports_native_structured_output=False path through ValidateAndRetry._fallback_with_retry"
    - "format=json_schema constrained decoding (grammar-constrained, no conflicting params)"
    - "sys.modules fake-module injection for offline tests (absent SDK, no @patch)"
    - "host threaded from resolved_base_url in factory → OllamaProvider.__init__(host=...)"
    - "actionable ImportError from _require_ollama() (names pip install fdars[ollama])"

key_files:
  created:
    - python/fdars/advisor/providers/ollama.py
    - tests/test_advisor_ollama.py
  modified:
    - python/fdars/advisor/providers/_factory.py
    - tests/test_advisor_providers.py

decisions:
  - "supports_native_structured_output=False: grammar-constrained decoding is structurally reliable but field-type coercion can still fail for small models; ValidateAndRetry handles the rest"
  - "No conflicting generation-control params alongside format=: Ollama issue #10929 documents that certain params silently disable the grammar constraint on some builds"
  - "Raw dict return: complete_structured returns json.loads(content) dict so ValidateAndRetry._fallback_with_retry owns schema validation (clean separation)"
  - "factory shim removal: ollama.py now exists so try/except ImportError→ValueError in _factory.py was wrong; _require_ollama() inside OllamaProvider.__init__ surfaces the actionable ImportError"
  - "test_unknown_provider_raises updated from 'ollama' to 'bogus': ollama is now a recognised provider; using 'bogus' tests the genuine unknown-provider path"
  - "Schema hint appended to last user message: nudges small local models toward the required JSON structure without risking format= constraint bypass"

metrics:
  completed_date: "2026-08-12"
  duration_minutes: 3
  tasks_completed: 2
  commits: 2
  files_changed: 4

actuals:
  tokens: 6286     # 25141 chars / 4 over realized diff
  tasks: 2
  commits: 2
---

# Phase 20 Plan 02: Ollama Adapter Summary

Expansion slice for Phase 20: delivered `OllamaProvider` — the first backend to exercise
the `supports_native_structured_output=False` path through `ValidateAndRetry._fallback_with_retry`.
Cleaned up the Wave-1 factory shim and updated the Phase-19 unknown-provider test to use
a genuinely-unknown name now that 'ollama' is a recognised provider.

## One-liner

OllamaProvider with format= grammar-constrained decoding, raw-dict return routing through
ValidateAndRetry, factory shim removed, and full offline test coverage (16 tests, 0 SDK needed).

## What Was Built

### Task 1: OllamaProvider adapter

`python/fdars/advisor/providers/ollama.py`:
- `OllamaProvider.name = "ollama"`, `supports_native_structured_output = False`
- `__init__(model="llama3.2", host=None)`: deferred `_require_ollama()` + `_require_pydantic()`; stores `self.model` and `self._host`; no API key
- `complete_structured(schema, messages, system)`: deferred `import ollama` + `import json`; prepends system as `{"role":"system", ...}` message; appends JSON-schema hint to last user message; calls `ollama.chat(model=..., messages=..., format=json_schema, options={"temperature":0})` with `host=self._host` only when non-None; returns `json.loads(content)` (raw dict, NOT Pydantic instance)
- Empty content → `ValueError` (GROUND-04 parity)
- No conflicting generation-control params alongside `format=` (T-20-05 mitigated)

### Task 2 (+ shim cleanup): Offline tests + factory correction

**`python/fdars/advisor/providers/_factory.py`** — removed `try/except ImportError → ValueError` shim from the ollama branch. The shim was correct during plan 20-01 (ollama.py didn't exist) but wrong now: `resolve_provider("ollama")` with the `[ollama]` extra absent must raise the actionable `ImportError` from `_require_ollama()` (naming `pip install fdars[ollama]`), not a generic `ValueError("unknown provider")`.

**`tests/test_advisor_providers.py`** — updated `test_unknown_provider_raises` to use `provider="bogus"` instead of `provider="ollama"`. The ollama branch is now a valid recognised provider that raises `ImportError` (not `ValueError`) when the extra is absent.

**`tests/test_advisor_ollama.py`** — 16 offline tests in 9 groups:
1. Returns raw dict: asserts `isinstance(result, dict)` and `not isinstance(result, Advice)` on the direct OllamaProvider call
2. No conflicting generation params: `"think" not in chat.call_args[1].kwargs` and `"format" in kwargs`
3. ValidateAndRetry validates raw dict: wrapper returns a validated `Advice` (non-native fallback path e2e)
4. Retry then raise: invalid dict always fails; `chat.call_count == MAX_RETRIES == 2`; `ValueError` with "failed to return valid structured output"
5. Empty content → ValueError: parametrized `(None, "", b"", 0)` + explicit "empty" message check
6. Missing-extra ImportError: `sys.modules["ollama"] = None`; `ImportError` matching `pip install fdars[ollama]`
7. Grounding rejection/pass: `_check_grounding` rejects fabricated k=999, passes k=4
8. resolve_provider wiring: name, default model, supports_native_structured_output assertions
9. resolve_provider without extra: `sys.modules["ollama"] = None`; `ImportError` from factory path

## Verification Results

```
pytest tests/test_advisor_ollama.py -q
16 passed in 0.29s

pytest tests/test_advisor.py tests/test_advisor_providers.py tests/test_advisor_openai.py -q
37 passed, 1 skipped in 2.48s

grep -nv '^\s*#' python/fdars/advisor/providers/ollama.py | grep -c 'think'
0
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] spy-based host test failed due to module cache invalidation**

- **Found during:** Task 2 test run
- **Issue:** The original test for host threading used `monkeypatch.setattr(OllamaProvider, "__init__", _spy_init)` then cleared `sys.modules` so the factory re-imported the adapter module — getting a fresh `OllamaProvider` class that bypassed the spy.
- **Fix:** Replaced the spy approach with a direct inspect-the-adapter approach: call `resolve_provider(provider="ollama", base_url=...)` and inspect `wrapper._provider._host` directly (the `ValidateAndRetry._provider` attribute gives access to the underlying adapter).
- **Files modified:** `tests/test_advisor_ollama.py`
- **Commit:** `429ce94`

## Known Stubs

None. All implemented behavior is fully wired and tested.

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| T-20-04 mitigated | providers/ollama.py | format= constrained decoding + ValidateAndRetry (≤2 repair retries) + centralized _check_grounding |
| T-20-05 mitigated | providers/ollama.py | No conflicting generation-control params alongside format=; test asserts their absence |
| T-20-06 mitigated | providers/ollama.py | Non-native path re-validates every dict; deterministic raise after MAX_RETRIES, never fabricates |

No new unplanned threat surface introduced.

## Self-Check: PASSED

- `python/fdars/advisor/providers/ollama.py` present ✓
- `tests/test_advisor_ollama.py` present ✓
- Commit `b744ca4` (Task 1 adapter) verified in git log ✓
- Commit `429ce94` (Task 2 tests + shim cleanup) verified in git log ✓
- All 16 ollama tests pass ✓
- All 37+1skipped prior tests unchanged ✓
- No `think` in executable lines (grep count = 0) ✓
