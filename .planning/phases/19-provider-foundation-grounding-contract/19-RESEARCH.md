# Phase 19: Provider Foundation & Grounding Contract — Research

**Researched:** 2026-08-12
**Domain:** Python refactor — `Provider` protocol, `AnthropicProvider` adapter, centralized `ValidateAndRetry` / `_check_grounding` machinery
**Confidence:** HIGH (all findings derived from direct Read of source files this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- `advisor.py` becomes a package `advisor/` with `providers/` and `aspects/` subpackages. `advisor/__init__.py` re-exports the current public names so the existing `sys.modules["fdars.advisor"] = advisor` injection in `python/fdars/__init__.py` keeps working with zero public-API change.
- Extraction point: the inline Anthropic call currently in `advise()` (≈ lines 980–1007 of the existing `advisor.py`) moves into `AnthropicProvider.complete_structured(...)`. Everything else (schema, prompt builder, dispatcher, offline diagnostics builders) moves file-to-file unchanged.
- `Provider` protocol surface (PROV-01): `complete_structured(schema, messages, system) -> dict`, plus `name: str`, `model: str`, and a `supports_native_structured_output: bool` capability flag.
- Grounding centralized (GROUND-03): a single `_check_grounding(advice, diagnostics)` validator (in the base provider layer) runs on **every** provider path — it rejects any `Advice` whose recommendations cite numbers absent from the diagnostics. Not per-adapter.
- Validate-and-retry (GROUND-02): one shared `ValidateAndRetry` wrapper. Native path used when `supports_native_structured_output` is true; otherwise prompt-JSON → Pydantic validate → repair-retry with the **full diagnostics re-included**, `max_retries=2` hardcoded, deterministic failure after the cap (raise, never fabricate).
- Refusal/empty handling (GROUND-04): a provider refusal or empty response raises a clear error, never a vacuously-valid `Advice()`.
- Selection/precedence (PROV-06): a `resolve_provider()` factory reads explicit `advise(provider=…, model=…)` params first, then env vars (`FDARS_ADVISOR_PROVIDER` / `FDARS_ADVISOR_MODEL` / `FDARS_ADVISOR_BASE_URL` + per-provider API keys). `provider=None` reproduces today's Anthropic default (backward compatible).
- `anthropic` stays a deferred import via the existing `_require_anthropic()` pattern; base package still imports with no provider installed.

### Claude's Discretion

Exact module/file names within `advisor/providers/` and `advisor/base.py`, the precise `_check_grounding` numeric-citation matching heuristic, and test organization — at Claude's discretion, guided by existing conventions and `test_advisor.py`.

### Deferred Ideas (OUT OF SCOPE)

Real OpenAI/Ollama/Gemini adapters → Phase 20 (this phase only needs the protocol + Anthropic adapter + a test-only fake provider to exercise the fallback/grounding paths).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROV-01 | `Provider` protocol: `complete_structured(schema, messages, system)`, `name`, `model`, `supports_native_structured_output` | Protocol design section; exact surface confirmed by reading `advisor.py` lines 991–998 (the Anthropic call that drives the interface shape) |
| PROV-02 | Existing Anthropic path refactored into `AnthropicProvider` adapter; `advise()` public behavior/outputs unchanged; existing tests stay green | Extraction map section; guardrail test analysis |
| PROV-06 | Provider/model selection via `advise(provider=…, model=…)` and env vars with documented precedence | Selection/precedence section |
| GROUND-01 | Native structured output path for providers with `supports_native_structured_output=True` | Grounding contract section; Anthropic native path analysis |
| GROUND-02 | Validate-and-retry/repair path for non-native providers; `max_retries=2`; deterministic raise after cap | ValidateAndRetry design section |
| GROUND-03 | Centralized `_check_grounding` on every provider path | Grounding check design section |
| GROUND-04 | Provider refusals or empty responses raise a clear error | Refusal handling section; existing `parsed is None` check at line 1000–1007 |
</phase_requirements>

---

## Summary

Phase 19 is a pure structural refactor: zero change to `advise()` public behavior, zero change to the `Advice`/`Recommendation` schema, and the existing `tests/test_advisor.py` suite must pass byte-identically before and after. The work converts `python/fdars/advisor.py` (a single 1161-line module) into a package `python/fdars/advisor/` and introduces three new internal modules: a `Provider` protocol, an `AnthropicProvider` adapter that lifts the inline Anthropic call out of `advise()`, and a `ValidateAndRetry` wrapper plus `_check_grounding` validator that centralize grounding enforcement so every future provider inherits them automatically.

The critical constraint is that `python/fdars/__init__.py` line 72 (`_sys.modules["fdars.advisor"] = advisor`) [VERIFIED: python/fdars/__init__.py:72] must continue to resolve after the `advisor.py` → `advisor/__init__.py` rename. Because Python resolves `import fdars.advisor` through the package `__init__.py` when `advisor/` is a directory, and the `sys.modules` injection happens with the already-imported `advisor` object pointing at `advisor/__init__`, this transition is drop-in with no change to `__init__.py`.

The tracer-first sequencing principle applies: wire one complete end-to-end path (`advise()` → `resolve_provider()` → `AnthropicProvider` → `ValidateAndRetry` → `_check_grounding` → return `Advice`) and prove `pytest tests/test_advisor.py` green before moving schema/prompt/diagnostics builders into their final submodule locations. Doing the structural split first and the behavioral wiring second makes rollback trivial if a test fails.

**Primary recommendation:** Extract the Anthropic call block (lines 978–1007) into `AnthropicProvider.complete_structured()` first as a tracer, prove both test classes pass, then perform the file-splitting moves as pure mechanical refactors.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Provider protocol definition | `advisor/providers/_protocol.py` | — | Protocol is the contract all adapters satisfy; lives with the adapters |
| Anthropic SDK call | `advisor/providers/anthropic.py` | — | Isolates SDK import from all other advisor code |
| Schema validation + retry | `advisor/providers/_validate.py` | — | Centralized; wraps any Provider; not per-adapter |
| Grounding check | `advisor/providers/_validate.py` | — | Runs after every successful parse; same location as retry |
| Provider selection / factory | `advisor/providers/_factory.py` | — | Reads env/params; returns wrapped adapter |
| `advise()` dispatch | `advisor/__init__.py` | — | Public API entry point; calls `resolve_provider()` |
| Schema (Advice, Recommendation) | `advisor/_schema.py` | — | Pydantic models + fallback stubs; unchanged from today |
| System prompt | `advisor/_prompts.py` | — | Single function; no per-aspect duplication |
| Offline diagnostics dispatch | `advisor/__init__.py` | `advisor/aspects/*.py` | Dispatcher in init; builders in aspects/ |
| `sys.modules` injection | `python/fdars/__init__.py` | — | Unchanged; works automatically with advisor/ package |

---

## Exact Extraction Map

### 1. `advise()` Current Signature

**File:** `python/fdars/advisor.py`, lines 940–1007 [VERIFIED: python/fdars/advisor.py:940-1007]

```python
def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
) -> Advice:
```

**What changes in Phase 19:** The signature gains `provider: str | Provider | None = None`. The `model` parameter stays with its default `"claude-opus-4-8"` as a convenience shorthand passed to `resolve_provider()`. The new signature:

```python
def advise(
    diagnostics: dict,
    *,
    task: str,
    domain_context: str,
    model: str = "claude-opus-4-8",
    provider: "str | Provider | None" = None,
) -> "Advice":
```

Because `provider` defaults to `None` and `model` retains its default, all existing call sites (`advise(diag, task="parameter", domain_context="NIR spectroscopy")`) are unchanged. [VERIFIED: python/fdars/advisor.py:940-946]

### 2. Inline Anthropic Call Block — Exact Extraction Point

**File:** `python/fdars/advisor.py`, lines 978–1007 [VERIFIED: python/fdars/advisor.py:978-1007]

This is the complete block that moves into `AnthropicProvider.complete_structured()`:

```python
# Lines 978–1007 (verbatim from advisor.py):
anthropic = _require_anthropic()          # line 978
_require_pydantic()                       # line 979
client = anthropic.Anthropic()            # line 980
                                          # line 981 (blank)
system = _system_prompt(task)             # line 982
                                          # line 983 (blank)
user_content = (                          # line 984
    f"Domain context: {domain_context}\n\n"
    f"Task: {task}\n\n"
    "Diagnostics (reason only from these values):\n"
    + json.dumps(diagnostics, sort_keys=True, indent=2)
)

response = client.messages.parse(         # line 991
    model=model,
    max_tokens=16000,
    thinking={"type": "adaptive"},
    system=system,
    output_format=Advice,
    messages=[{"role": "user", "content": user_content}],
)

parsed = response.parsed_output           # line 1000
if parsed is None:                        # line 1001
    raise ValueError(                     # line 1002
        "advise: the Anthropic API did not return a parseable Advice object. "
        "The model may have responded with only a thinking block or a refusal. "
        f"Raw response stop_reason: {response.stop_reason!r}"
    )
return parsed                             # line 1007
```

**What moves where:**
- The `_require_anthropic()` / `_require_pydantic()` guards → `AnthropicProvider.__init__()` (called once at construction via `resolve_provider()`)
- `client = anthropic.Anthropic()` → `AnthropicProvider.__init__()`
- `system = _system_prompt(task)` → stays in `advise()` (system is built in the caller and passed to `complete_structured(schema, messages, system)`)
- `user_content` construction → stays in `advise()` (the messages list is built in the caller)
- `client.messages.parse(...)` → `AnthropicProvider.complete_structured()`
- `response.parsed_output is None` check → moves into `AnthropicProvider.complete_structured()` — it becomes the GROUND-04 refusal guard that raises before returning to `ValidateAndRetry`

**After extraction, `advise()` body becomes:**

```python
def advise(diagnostics, *, task, domain_context, model="claude-opus-4-8", provider=None):
    _require_pydantic()  # still guard pydantic — needed for Advice.model_validate
    p = resolve_provider(provider=provider, model=model)
    system = _system_prompt(task)
    user_content = (
        f"Domain context: {domain_context}\n\n"
        f"Task: {task}\n\n"
        "Diagnostics (reason only from these values):\n"
        + json.dumps(diagnostics, sort_keys=True, indent=2)
    )
    messages = [{"role": "user", "content": user_content}]
    advice = p.complete_structured(Advice, messages, system)
    _check_grounding(advice, diagnostics)
    return advice
```

### 3. Schema Location

`Advice` and `Recommendation` (Pydantic models + fallback stubs): lines 67–181 of `advisor.py`. [VERIFIED: python/fdars/advisor.py:67-181]

These move verbatim to `advisor/_schema.py`. `advisor/__init__.py` imports them:

```python
from advisor._schema import Advice, Recommendation
```

The fallback stubs (plain-Python classes when pydantic is absent) move together — both branches of the `try/except ImportError` block.

**`__all__` stays unchanged:** [VERIFIED: python/fdars/advisor.py:175-181]
```python
__all__ = [
    "build_diagnostics",
    "advise",
    "describe_cluster_differences",
    "Advice",
    "Recommendation",
]
```

### 4. `_system_prompt()` Location

Lines 809–933. [VERIFIED: python/fdars/advisor.py:809-933]

Moves verbatim to `advisor/_prompts.py`. The function signature gains `aspect: str = ""` as an unused-for-now parameter (Phase 21 will add per-aspect clauses). Today it has no aspect parameter and that is what Phase 19 preserves.

**Grounding invariant sentence (must remain byte-identical, never duplicated):** [VERIFIED: python/fdars/advisor.py:835-842]

> "You are a functional data analysis (FDA) advisor. You reason only from the diagnostics provided in the user message. Every evidence item in each Recommendation must cite a specific diagnostic value that appears in the input — do not omit this. Omit any claim not supported by a provided value. Never fabricate numbers or invent values not present in the diagnostics. Never estimate or assume numerical results that are not explicitly given."

This exact text becomes a module-level constant `_GROUNDING_INVARIANT` in `advisor/_prompts.py` so grep can verify there is exactly one copy.

### 5. Diagnostics Builders — What Moves Where

All five `_build_*_diagnostics` functions plus their helpers move verbatim to `advisor/aspects/`:

| Function | Current lines | Destination |
|----------|--------------|-------------|
| `_build_alignment_diagnostics` | 258–342 | `advisor/aspects/alignment.py` |
| `_build_fpca_diagnostics` | 349–419 | `advisor/aspects/fpca.py` |
| `_build_basis_diagnostics` | 426–516 | `advisor/aspects/basis.py` |
| `_build_smoothing_diagnostics` | 519–625 | `advisor/aspects/smoothing.py` |
| `_build_clustering_diagnostics` | 632–740 | `advisor/aspects/clustering.py` |

[VERIFIED: python/fdars/advisor.py:258-342, 349-419, 426-516, 519-625, 632-740]

The `build_diagnostics()` dispatcher (lines 188–255) [VERIFIED: python/fdars/advisor.py:188-255] stays in `advisor/__init__.py` and imports each builder lazily:

```python
if method_lc == "alignment":
    from advisor.aspects.alignment import _build_alignment_diagnostics
    return _build_alignment_diagnostics(raw, argvals=argvals)
```

**Supported set (unchanged, verbatim):** [VERIFIED: python/fdars/advisor.py:226]
```python
_supported = {"alignment", "fpca", "basis", "smoothing", "clustering"}
```

Phase 19 does NOT add new method strings to this set (that is Phase 21).

### 6. `describe_cluster_differences()` Location

Lines 1014–1126. [VERIFIED: python/fdars/advisor.py:1014-1126]

Stays in `advisor/__init__.py` — it is a thin orchestrator that calls `build_diagnostics` then `advise`. It gains a `provider=` parameter forwarded to `advise()`:

```python
def describe_cluster_differences(
    result, *, argvals=None, domain_context="", model="claude-opus-4-8",
    run_llm=True, provider=None, **kwargs,
):
    diagnostics = build_diagnostics(result, method="clustering", argvals=argvals, **kwargs)
    if not run_llm:
        return diagnostics
    return advise(diagnostics, task="interpretation", domain_context=domain_context,
                  model=model, provider=provider)
```

### 7. `_selfcheck_alignment_diagnostics()` Location

Lines 1132–1161. [VERIFIED: python/fdars/advisor.py:1132-1161]

Moves to `advisor/aspects/alignment.py` (it tests the alignment builder). Or stays in `advisor/__init__.py` if moving it would risk test disruption — safer to leave it in `__init__.py` for Phase 19 since it is not imported externally.

---

## Package-Conversion Mechanics

### Directory Structure for Phase 19

```
python/fdars/
├── advisor/                        # NEW package — replaces advisor.py
│   ├── __init__.py                 # re-exports: build_diagnostics, advise,
│   │                               #   describe_cluster_differences, Advice, Recommendation
│   │                               #   __all__ = same list as today
│   ├── _schema.py                  # Advice + Recommendation Pydantic models + fallback stubs
│   ├── _prompts.py                 # _system_prompt(task, aspect="") + _GROUNDING_INVARIANT const
│   ├── providers/                  # NEW: provider layer (Phase 19 scope)
│   │   ├── __init__.py             # exports: Provider, AnthropicProvider, resolve_provider
│   │   ├── _protocol.py            # Provider Protocol (runtime_checkable)
│   │   ├── _validate.py            # ValidateAndRetry + _check_grounding
│   │   ├── _factory.py             # resolve_provider()
│   │   └── anthropic.py            # AnthropicProvider
│   └── aspects/                    # builders — verbatim moves
│       ├── __init__.py             # (empty or re-exports)
│       ├── alignment.py
│       ├── fpca.py
│       ├── basis.py
│       ├── smoothing.py
│       └── clustering.py
└── __init__.py                     # UNCHANGED — line 72 keeps working
```

Phase 20 adds `providers/openai.py`, `providers/gemini.py`, `providers/ollama.py`.
Phase 21 adds `aspects/depth.py`, `aspects/regression.py`, etc.

### `sys.modules` Injection — Why It Still Works

`python/fdars/__init__.py` line 64: `from fdars import advisor` [VERIFIED: python/fdars/__init__.py:64]
`python/fdars/__init__.py` line 72: `_sys.modules["fdars.advisor"] = advisor` [VERIFIED: python/fdars/__init__.py:72]

When `advisor/` is a directory containing `__init__.py`, Python's import system resolves `from fdars import advisor` to `advisor/__init__` — the `advisor` name bound is the `advisor/__init__` module object. The subsequent `_sys.modules["fdars.advisor"] = advisor` then registers that module object. No change to `fdars/__init__.py` is required.

**Verification command:** `python -c "from fdars import advisor; print(advisor.__file__)"` — after the rename, this should print `…/fdars/advisor/__init__.py`.

### Import-Cycle and Lazy-Import Considerations

- `advisor/__init__.py` must NOT import from `advisor/providers/` at module load time. The entire providers layer is imported lazily inside `advise()` via `resolve_provider()`.
- `advisor/_schema.py` imports only `pydantic` (inside a try/except) and `typing`. No fdars imports. Safe to import at module load time from `advisor/__init__.py`.
- `advisor/_prompts.py` imports only `typing`. No pydantic, no anthropic, no fdars. Safe at load time.
- `advisor/aspects/*.py` are imported lazily inside `build_diagnostics()` (already the pattern for `fdars.alignment` and `fdars.basis` inside the existing builders). [VERIFIED: python/fdars/advisor.py:293, 499, 609, 671]
- `advisor/providers/anthropic.py` imports `anthropic` at module level (within the file itself) — this is fine because the file is only imported inside `resolve_provider()`, which is only called from `advise()`.

**The offline guarantee:** `import fdars` → `from fdars import advisor` → imports `advisor/__init__.py` → imports `_schema.py` (try/except pydantic) + `_prompts.py` — no LLM SDK touched. `build_diagnostics()` can be called. `advise()` is callable but immediately hits `_require_pydantic()` if pydantic is absent, or `resolve_provider()` → `AnthropicProvider.__init__()` → `_require_anthropic()` if anthropic is absent.

---

## Provider Protocol Design

### Protocol Surface

```python
# advisor/providers/_protocol.py
from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class Provider(Protocol):
    name: str          # e.g. "anthropic"
    model: str         # e.g. "claude-opus-4-8"

    def complete_structured(
        self,
        schema: type,           # Pydantic model class (Advice)
        messages: list[dict],   # [{"role": "user", "content": "..."}]
        system: str,            # system prompt (grounding invariant)
    ) -> "Advice":
        """Return a validated Advice. Raises on failure or refusal."""
        ...

    @property
    def supports_native_structured_output(self) -> bool:
        """True if the backend enforces schema natively (no repair needed)."""
        ...
```

Using `Protocol` (not ABC) enables duck-typed test fakes — a simple class with the right attributes passes `isinstance(fake, Provider)` at runtime via `@runtime_checkable`.

**Why `system` is a separate parameter (not embedded in messages):** The Anthropic API takes `system` as a top-level field; OpenAI and Ollama embed it as the first message with `role="system"`. Each adapter translates the `system` argument into the correct wire format. `advise()` always builds the system prompt the same way regardless of provider.

### `AnthropicProvider` Design

```python
# advisor/providers/anthropic.py
from __future__ import annotations

class AnthropicProvider:
    name = "anthropic"
    supports_native_structured_output = True

    def __init__(self, model: str = "claude-opus-4-8", api_key: "str | None" = None):
        # Deferred import — only called from resolve_provider(), never at module load
        from advisor._require import _require_anthropic, _require_pydantic
        self._anthropic = _require_anthropic()
        _require_pydantic()
        import anthropic as _ant
        self.model = model
        self._client = _ant.Anthropic(api_key=api_key) if api_key else _ant.Anthropic()

    def complete_structured(self, schema, messages, system):
        response = self._client.messages.parse(
            model=self.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=system,
            output_format=schema,
            messages=messages,
        )
        parsed = response.parsed_output
        if parsed is None:
            raise ValueError(
                "AnthropicProvider: the API did not return a parseable output. "
                "The model may have responded with only a thinking block or a refusal. "
                f"Raw response stop_reason: {response.stop_reason!r}"
            )
        return parsed
```

**Key mapping from today's `advise()`:**
- `client.messages.parse(model=model, max_tokens=16000, thinking={"type": "adaptive"}, system=system, output_format=Advice, messages=messages)` [VERIFIED: python/fdars/advisor.py:991-998] → identical call inside `complete_structured()`, with `schema` in place of `Advice` (same object — `advise()` passes `Advice` as the `schema` argument).
- `response.parsed_output is None` → raises in the adapter, not the caller. [VERIFIED: python/fdars/advisor.py:1000-1007]

### Test-Only Fake Provider

A `FakeProvider` class satisfies the `Provider` protocol and exercises both native and fallback paths with no network:

```python
# tests/test_advisor_provider.py (or conftest.py)
class FakeNativeProvider:
    """Simulates a native-structured-output provider (e.g. Anthropic)."""
    name = "fake-native"
    model = "fake-model"
    supports_native_structured_output = True

    def __init__(self, response: dict):
        self._response = response  # pre-baked Advice-shaped dict

    def complete_structured(self, schema, messages, system):
        return schema.model_validate(self._response)


class FakeFallbackProvider:
    """Simulates a non-native provider (e.g. Ollama) that returns raw dict."""
    name = "fake-fallback"
    model = "fake-model"
    supports_native_structured_output = False

    def __init__(self, response: dict):
        self._response = response

    def complete_structured(self, schema, messages, system):
        # Returns raw dict — ValidateAndRetry must validate
        return self._response


class FakeRefusalProvider:
    """Simulates a provider refusal."""
    name = "fake-refusal"
    model = "fake-model"
    supports_native_structured_output = True

    def complete_structured(self, schema, messages, system):
        raise ValueError("FakeRefusalProvider: simulated refusal")
```

---

## Grounding + Retry Contract

### `ValidateAndRetry` Wrapper

```python
# advisor/providers/_validate.py
from __future__ import annotations

class ValidateAndRetry:
    """Wraps any Provider to add schema validation and repair retry."""

    MAX_RETRIES = 2  # hardcoded; never exceed 2 structural retries

    def __init__(self, provider: "Provider"):
        self._provider = provider

    @property
    def name(self) -> str:
        return self._provider.name

    @property
    def model(self) -> str:
        return self._provider.model

    @property
    def supports_native_structured_output(self) -> bool:
        return self._provider.supports_native_structured_output

    def complete_structured(self, schema, messages, system):
        if self._provider.supports_native_structured_output:
            # Native path: provider handles schema enforcement
            # ValidateAndRetry is still the call boundary but does not repair
            result = self._provider.complete_structured(schema, messages, system)
            # result is already a validated schema instance (e.g. Advice)
            return result
        else:
            # Non-native path: JSON string/dict → Pydantic validate → repair-retry
            return self._fallback_with_retry(schema, messages, system)

    def _fallback_with_retry(self, schema, messages, system):
        from pydantic import ValidationError
        attempt = 0
        last_error = None
        current_messages = list(messages)
        while attempt < self.MAX_RETRIES:
            raw = self._provider.complete_structured(schema, current_messages, system)
            try:
                if isinstance(raw, dict):
                    return schema.model_validate(raw)
                return schema.model_validate(raw)  # already validated by native
            except ValidationError as exc:
                last_error = exc
                attempt += 1
                if attempt < self.MAX_RETRIES:
                    # Repair prompt — must re-include original user message (grounding)
                    repair_msg = {
                        "role": "user",
                        "content": (
                            f"Your previous response did not conform to the required "
                            f"JSON structure. Errors:\n{exc}\n\n"
                            "Return only a valid JSON object. "
                            "Reason only from the diagnostics in the earlier message."
                        ),
                    }
                    current_messages = list(messages) + [repair_msg]
        raise ValueError(
            f"Provider {self._provider.name!r} failed to return valid structured output "
            f"after {self.MAX_RETRIES} attempts. Last error: {last_error}"
        )
```

**Contract guarantees:**
1. `max_retries=2`: after 2 failed attempts, `raise ValueError` — never fabricate. [LOCKED]
2. Repair prompt re-uses `messages` (the original list containing diagnostics) so the model re-reads the grounding evidence. The repair message is appended, not replacing.
3. Native providers route through the wrapper but skip `_fallback_with_retry` — the wrapper is a safety boundary, not dead weight.
4. `AnthropicProvider.complete_structured()` returns an `Advice` instance (via `messages.parse(output_format=Advice)`), not a dict. The `ValidateAndRetry` native path returns it directly without calling `model_validate` again.

### `_check_grounding` — Numeric-Citation Check

```python
# advisor/providers/_validate.py  (same file)
import re

def _check_grounding(advice: "Advice", diagnostics: dict) -> None:
    """Raise GroundingViolationError if any evidence item cites a numeric value
    absent from the diagnostics dict.

    Strategy: collect all numeric tokens (integers and floats) that appear
    in every evidence string. For each such token, verify it appears (as a
    substring of the string representation) in the flattened diagnostics
    values. Evidence strings that contain no numeric tokens pass unchecked
    (they are qualitative statements, which is fine).
    """
    diag_text = _flatten_diagnostics_text(diagnostics)
    for rec in advice.recommendations:
        for ev in rec.evidence:
            nums = _extract_numbers(ev)
            for n in nums:
                if n not in diag_text:
                    raise GroundingViolationError(
                        f"Evidence item cites value {n!r} not found in diagnostics: {ev!r}"
                    )


class GroundingViolationError(ValueError):
    """Raised when an Advice recommendation cites a value absent from diagnostics."""


def _flatten_diagnostics_text(d: dict) -> set:
    """Return a set of string representations of all scalar values in a dict."""
    result = set()
    def _recurse(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                _recurse(v)
        elif obj is not None:
            result.add(str(obj))
            # Also add truncated float representations (e.g. "0.312" for 0.3124...)
            if isinstance(obj, float):
                result.add(f"{obj:.3f}")
                result.add(f"{obj:.4f}")
    _recurse(d)
    return result


def _extract_numbers(text: str) -> list:
    """Extract numeric tokens from an evidence string."""
    return re.findall(r'\b\d+\.?\d*\b', text)
```

**Heuristic rationale (Claude's Discretion):**
- Numbers are extracted from evidence strings as decimal tokens (`\b\d+\.?\d*\b`).
- Each number must appear somewhere in the flattened string representation of the diagnostics dict.
- Qualitative evidence items ("The alignment converged quickly") pass unchecked.
- This is a lightweight heuristic, not a semantic check. Its purpose is to catch clearly fabricated numeric values (e.g., `"k=7 clusters"` when diagnostics has `k=4`). It is not expected to catch subtle paraphrasing.
- `_check_grounding` runs after `ValidateAndRetry` validates structure. Grounding failure raises `GroundingViolationError` immediately — it does NOT trigger a repair retry (retrying on grounding failure would reward fabrication).

**Location:** `_check_grounding` lives in `advisor/providers/_validate.py`. It is called from `advise()` (in `advisor/__init__.py`) after `p.complete_structured(...)` returns, so it runs on every provider path regardless of whether the path is native or fallback.

```python
# In advise() after complete_structured():
advice = p.complete_structured(Advice, messages, system)
_check_grounding(advice, diagnostics)   # GROUND-03: centralized, runs always
return advice
```

---

## Selection / Precedence

### `resolve_provider()` Factory

```python
# advisor/providers/_factory.py
from __future__ import annotations
import os

def resolve_provider(
    provider: "str | Provider | None" = None,
    model: "str | None" = None,
    api_key: "str | None" = None,
    base_url: "str | None" = None,
    **kw,
) -> "ValidateAndRetry":
    """Return a ValidateAndRetry-wrapped Provider.

    Precedence (highest → lowest):
    1. explicit provider= argument
    2. FDARS_ADVISOR_PROVIDER env var
    3. fallback: "anthropic" (backward compatible with today's behavior)

    Model precedence (highest → lowest):
    1. explicit model= argument
    2. FDARS_ADVISOR_MODEL env var
    3. provider default (anthropic → "claude-opus-4-8")
    """
    from advisor.providers._validate import ValidateAndRetry
    from advisor.providers._protocol import Provider as _ProviderProtocol

    # If already a Provider instance, wrap and return immediately
    if isinstance(provider, _ProviderProtocol):
        return ValidateAndRetry(provider)

    provider_name = (
        provider
        or os.environ.get("FDARS_ADVISOR_PROVIDER")
        or "anthropic"
    )
    resolved_model = (
        model
        or os.environ.get("FDARS_ADVISOR_MODEL")
        or _DEFAULT_MODELS.get(provider_name, "")
    )
    resolved_key = api_key or os.environ.get(_KEY_ENV.get(provider_name, ""))
    resolved_base_url = base_url or os.environ.get("FDARS_ADVISOR_BASE_URL")

    if provider_name == "anthropic":
        from advisor.providers.anthropic import AnthropicProvider
        adapter = AnthropicProvider(model=resolved_model, api_key=resolved_key)
    else:
        raise ValueError(
            f"resolve_provider: unknown provider {provider_name!r}. "
            f"Supported in Phase 19: 'anthropic'. "
            f"Additional providers added in Phase 20."
        )
    return ValidateAndRetry(adapter)


_DEFAULT_MODELS = {
    "anthropic": "claude-opus-4-8",
    # Phase 20 will add: "openai": "gpt-4o", "gemini": "gemini-2.0-flash", "ollama": "llama3.2"
}

_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    # Phase 20: "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"
}
```

**Precedence table (PROV-06):**

| Priority | Source | Provider | Model | Key |
|----------|--------|----------|-------|-----|
| 1 (highest) | `advise(provider=..., model=...)` | explicit string or Provider instance | explicit string | `api_key=` argument |
| 2 | Environment | `FDARS_ADVISOR_PROVIDER` | `FDARS_ADVISOR_MODEL` | per-provider key env (e.g. `ANTHROPIC_API_KEY`) |
| 3 (lowest) | Default | `"anthropic"` | `"claude-opus-4-8"` | env `ANTHROPIC_API_KEY` |

**`provider=None` backward-compatibility guarantee:** With no provider argument and no `FDARS_ADVISOR_PROVIDER` env var, `resolve_provider()` returns `ValidateAndRetry(AnthropicProvider(model="claude-opus-4-8"))`. The Anthropic adapter calls `client.messages.parse(model="claude-opus-4-8", max_tokens=16000, thinking={"type": "adaptive"}, ...)` — identical to the current `advise()` behavior. [VERIFIED: python/fdars/advisor.py:991-998]

---

## Test Strategy

### Guardrail: Existing Tests Must Stay Green Unchanged

`tests/test_advisor.py` [VERIFIED: tests/test_advisor.py:1-91] contains two test classes:

**`TestBuildDiagnosticsOffline`** (lines 18–69) — four tests, no LLM, no anthropic:
- `test_clustering_offline_with_synthetic` — calls `build_diagnostics(..., method="clustering")`
- `test_clustering_with_real_dataset` — loads Canadian weather, calls `build_diagnostics`
- `test_build_diagnostics_deterministic` — calls `build_diagnostics(..., method="basis")` twice
- `test_advise_raises_importerror_without_anthropic` — monkeypatches `sys.modules["anthropic"] = None`, asserts `ImportError` with `"pip install fdars\\[advisor\\]"`

**`TestAdvisorIntegration`** (lines 72–91) — one live test, skipped without `ANTHROPIC_API_KEY`:
- `test_advise_returns_advice_schema` — calls `advise(diag, task="parameter", domain_context="NIR spectroscopy")`

All four offline tests must pass with zero changes to their source. The monkeypatch test for `ImportError` is the most sensitive: it patches `sys.modules["anthropic"]` to `None` and calls `advise()`. After the refactor, `advise()` calls `_require_pydantic()` then `resolve_provider()` → `AnthropicProvider.__init__()` → `_require_anthropic()`. The `_require_anthropic()` guard must still see the monkeypatched `None` and raise `ImportError`. Verify that `_require_anthropic()` does `import anthropic` (not `from advisor.providers.anthropic import ...`) so the monkeypatch intercept still works.

### New Offline Unit Tests for Phase 19

All tests are offline — no API calls, no keys.

**File:** `tests/test_advisor_providers.py`

```
TestProviderProtocol
    test_fake_native_satisfies_protocol — isinstance(FakeNativeProvider(...), Provider) is True
    test_fake_fallback_satisfies_protocol

TestValidateAndRetry
    test_native_path_returns_advice_directly
        — FakeNativeProvider with valid Advice dict; assert result is Advice
    test_fallback_path_validates_raw_dict
        — FakeFallbackProvider with valid Advice dict; assert Advice returned
    test_fallback_retry_on_bad_json
        — FakeFallbackProvider that returns malformed dict first, valid second
        — assert Advice returned (one retry consumed)
    test_fallback_raises_after_max_retries
        — FakeFallbackProvider that always returns malformed dict
        — assert ValueError raised (not Advice, not fabrication)
    test_refusal_raises
        — FakeRefusalProvider; assert ValueError raised

TestCheckGrounding
    test_grounding_passes_when_all_numbers_in_diagnostics
        — build Advice with evidence citing values present in diag dict
        — assert no exception
    test_grounding_rejects_fabricated_number
        — build Advice with evidence citing "k=7" when diag has k=4
        — assert GroundingViolationError
    test_grounding_passes_qualitative_evidence
        — evidence string with no numbers ("Alignment converged quickly")
        — assert no exception
    test_grounding_runs_on_native_path
        — FakeNativeProvider; call advise() with controlled diagnostics
        — assert GroundingViolationError raised when evidence fabricates

TestResolveProvider
    test_default_returns_anthropic_wrapped
        — monkeypatch anthropic available; resolve_provider() returns ValidateAndRetry
        — assert result.name == "anthropic"
    test_explicit_provider_instance_passthrough
        — pass FakeNativeProvider instance directly; assert it is wrapped
    test_env_var_provider_selection
        — monkeypatch FDARS_ADVISOR_PROVIDER="anthropic"; assert anthropic selected
    test_env_var_model_override
        — monkeypatch FDARS_ADVISOR_MODEL="claude-haiku-4-5"; assert model used
    test_unknown_provider_raises
        — resolve_provider(provider="ollama") raises ValueError with helpful message

TestAdviseIntegration (offline, uses FakeNativeProvider)
    test_advise_with_fake_provider_returns_advice
        — call advise(diag, task="interpretation", domain_context="x", provider=fake)
        — assert isinstance(result, Advice)
    test_advise_provider_none_constructs_anthropic_adapter
        — with anthropic monkeypatched to fake; provider=None; assert correct adapter
```

### Test Organization Principle

Keep `tests/test_advisor.py` exactly as-is (the refactor guardrail). Put all new tests in `tests/test_advisor_providers.py`. This makes the guardrail immediately visible: if `test_advisor.py` fails, the refactor broke something; if `test_advisor_providers.py` fails, the new code is wrong.

---

## Risks and Pitfalls Specific to Phase 19

### Risk 1: `_require_anthropic()` Monkeypatch Breaks

**What can go wrong:** `test_advise_raises_importerror_without_anthropic` patches `sys.modules["anthropic"] = None`. After the refactor, `_require_anthropic()` is called inside `AnthropicProvider.__init__()`, which is called inside `resolve_provider()`, which is called inside `advise()`. The indirection chain is longer but the monkeypatch should still work because `_require_anthropic()` does `import anthropic` (which goes through `sys.modules`). The risk is if `_require_anthropic()` is moved to a location where it is called at module load time (before the monkeypatch is set up).

**Mitigation:** `_require_anthropic()` must only be called inside functions, never at module load. Move it to `advisor/_require.py` or keep it in `advisor/__init__.py`. Confirm the test passes in isolation: `pytest tests/test_advisor.py::TestBuildDiagnosticsOffline::test_advise_raises_importerror_without_anthropic -v` after each structural move.

### Risk 2: `advisor/__init__.py` Circular Import

**What can go wrong:** `advisor/__init__.py` imports `_schema` and `_prompts`. If `_schema.py` or `_prompts.py` imports anything from `advisor/` (e.g., `from advisor import something`), a circular import results.

**Mitigation:** `_schema.py` must import only `pydantic` and `typing`. `_prompts.py` must import only `typing`. Enforce with a module-level comment and a test: `python -c "from fdars.advisor._schema import Advice; print('ok')"`.

### Risk 3: `describe_cluster_differences()` Docstring Cites `advise()` Signature

**What can go wrong:** The docstring of `describe_cluster_differences` (line 1014–1126) [VERIFIED: python/fdars/advisor.py:1014-1126] says `model=model` is forwarded to `advise()`. After the refactor, `advise()` also accepts `provider=`. The docstring needs updating to mention the new parameter. Minor, but affects documentation accuracy.

**Mitigation:** Add `provider=` to the Parameters section of `describe_cluster_differences`'s docstring as part of the Phase 19 changes.

### Risk 4: `ValidateAndRetry` on the Native Path Returns Wrong Type

**What can go wrong:** `AnthropicProvider.complete_structured()` returns an `Advice` instance (from `messages.parse(output_format=Advice)`). If `ValidateAndRetry` on the native path calls `schema.model_validate(result)` on an already-validated instance, it may fail or produce a copy.

**Mitigation:** The native path in `ValidateAndRetry.complete_structured()` calls `self._provider.complete_structured(schema, messages, system)` and returns the result directly — no `model_validate` call. The Pydantic model instance is already valid. The `_check_grounding` call in `advise()` then runs on the returned instance.

### Risk 5: `_check_grounding` False-Positive on Floating-Point Representations

**What can go wrong:** `0.3124` in diagnostics vs. `0.31` in evidence — the truncated representation fails the substring check.

**Mitigation:** `_flatten_diagnostics_text` adds multiple representations of each float: `str(obj)`, `f"{obj:.3f}"`, `f"{obj:.4f}"` [see grounding section above]. Additionally, `_extract_numbers` uses `r'\b\d+\.?\d*\b'` which matches both `0.31` and `0.3124`. A false positive (grounding check rejects valid evidence) will surface immediately in the `test_advise_returns_advice_schema` integration test if it runs. The heuristic is deliberately lenient.

### Sequencing Recommendation: Tracer-First

The plan should sequence work in this order to minimize risk:

1. **Wave 0: package skeleton** — create `advisor/` directory with `__init__.py` that just does `from advisor._legacy import *` pointing at the original module code. Confirm `pytest tests/test_advisor.py` green.
2. **Wave 1: protocol + adapter** — create `_protocol.py`, `anthropic.py`, `_validate.py`, `_factory.py`. Wire `advise()` to call `resolve_provider()`. Run `pytest tests/test_advisor.py` green.
3. **Wave 2: file splits** — move `_schema.py`, `_prompts.py`, aspect builders to their final locations. Update imports. Run `pytest tests/test_advisor.py` green.
4. **Wave 3: new tests** — write `tests/test_advisor_providers.py` with all new offline tests. All must pass.

Doing the behavioral wire (wave 1) before the structural split (wave 2) means: if wave 1 breaks a test, you know the wiring is wrong, not the file structure.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `anthropic` | `>=0.72.0` | Anthropic SDK with `messages.parse()` | Already declared in `[advisor]` extra; provides native structured output [VERIFIED: pyproject.toml:41] |
| `pydantic` | `>=2.0` | Schema validation for `Advice`/`Recommendation` | Already declared; `model_validate()` is the validation path [VERIFIED: pyproject.toml:41] |
| `typing.Protocol` | stdlib | `Provider` protocol | Standard Python protocol pattern; `runtime_checkable` enables `isinstance` checks in tests |

### No New Dependencies in Phase 19

Phase 19 introduces zero new packages. `pyproject.toml` is unchanged. The `[advisor]` extra (`anthropic>=0.72.0, pydantic>=2.0`) remains the only provider extra. Phase 20 will add `[openai]`, `[gemini]`, `[ollama]`.

---

## Package Legitimacy Audit

No new packages are introduced in Phase 19. All dependencies are already declared in `pyproject.toml` [VERIFIED: pyproject.toml:38-43]:

```toml
[project.optional-dependencies]
advisor = ["anthropic>=0.72.0", "pydantic>=2.0"]
```

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### Pattern: Thin `advise()` Dispatcher

`advise()` becomes a 12-line function: build system prompt, build messages, call `resolve_provider()`, call `complete_structured()`, call `_check_grounding()`, return. All API complexity lives in the provider layer.

### Pattern: Deferred Import Tower

```
advise()
  └─ resolve_provider()                       (imported lazily inside advise())
       └─ AnthropicProvider.__init__()         (module imported inside resolve_provider())
            └─ _require_anthropic()            (import anthropic inside function body)
```

No provider SDK is ever imported at module load time. This is the same tower that exists today (`_require_anthropic()` inside `advise()`), but formalized into a factory pattern so all future providers follow the same structure.

### Anti-Patterns to Avoid

- **Do not call `_require_anthropic()` at `advisor/__init__.py` module scope.** The offline guarantee breaks.
- **Do not duplicate the grounding invariant string.** Make it `_GROUNDING_INVARIANT` constant in `_prompts.py` and use it as the base of `_system_prompt()`. Grep verification: `grep -r "reason only from" python/fdars/` must return exactly one location.
- **Do not call `_check_grounding()` inside `AnthropicProvider`.** It belongs in `advise()` (the caller), so it runs on every provider, not just Anthropic.
- **Do not add repair-retry on grounding failure.** A grounding-violated result raises immediately — retrying rewards fabrication.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Schema validation | Custom JSON field checker | `pydantic.BaseModel.model_validate()` | Already in codebase; handles type coercion, required fields, literals |
| Native structured output | Manual JSON parsing of Anthropic response | `client.messages.parse(output_format=Advice)` | Anthropic SDK handles this natively; already in use [VERIFIED: python/fdars/advisor.py:991] |
| Protocol duck typing | Hand-written ABC with `__subclasshook__` | `typing.Protocol` with `@runtime_checkable` | Standard pattern; no inheritance required from adapters |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already in use) [VERIFIED: pyproject.toml:40] |
| Config file | none detected — uses defaults |
| Quick run command | `pytest tests/test_advisor.py tests/test_advisor_providers.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| PROV-01 | Provider protocol satisfied by `AnthropicProvider` and fakes | unit | `pytest tests/test_advisor_providers.py::TestProviderProtocol -x` |
| PROV-02 | Existing `advise()` behavior unchanged | guardrail | `pytest tests/test_advisor.py -x` |
| PROV-06 | `resolve_provider()` precedence | unit | `pytest tests/test_advisor_providers.py::TestResolveProvider -x` |
| GROUND-01 | Native path returns validated `Advice` | unit | `pytest tests/test_advisor_providers.py::TestValidateAndRetry::test_native_path_returns_advice_directly` |
| GROUND-02 | Retry cap → deterministic raise | unit | `pytest tests/test_advisor_providers.py::TestValidateAndRetry::test_fallback_raises_after_max_retries` |
| GROUND-03 | `_check_grounding` rejects fabricated number | unit | `pytest tests/test_advisor_providers.py::TestCheckGrounding::test_grounding_rejects_fabricated_number` |
| GROUND-04 | Refusal → ValueError (not empty Advice) | unit | `pytest tests/test_advisor_providers.py::TestValidateAndRetry::test_refusal_raises` |

### Wave 0 Gaps

- [ ] `tests/test_advisor_providers.py` — covers PROV-01, PROV-06, GROUND-01–04 (new file, Wave 3)

---

## Security Domain

The advisor layer makes outbound HTTPS calls to the Anthropic API. No user input is executed as code; diagnostics dicts are serialized via `json.dumps`. No auth credentials are stored in code — they are read from environment variables at runtime via `os.environ.get("ANTHROPIC_API_KEY")`. The grounding check is a defense against LLM-fabricated content leaking into the output, not a security control against adversarial inputs.

No ASVS categories apply to this pure-Python refactor (no auth, no session management, no web surface, no cryptography). Input validation is provided by Pydantic schema enforcement on `Advice`/`Recommendation`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `client.messages.parse(output_format=Advice)` returns `Advice` instance (not dict) so native path in `ValidateAndRetry` returns it directly without `model_validate` | Grounding contract | If it returns a dict, the native path needs `model_validate` — low risk, easy to detect in integration test |
| A2 | `thinking={"type": "adaptive"}` is the correct SDK parameter name in `anthropic>=0.72.0` | Extraction map | If renamed in a newer SDK version, the Anthropic adapter would fail at runtime — but this is the current production code so it works today |

**All other claims are `[VERIFIED]` from direct Read of source files this session.**

---

## Open Questions

1. **`_require_anthropic()` and `_require_pydantic()` — where do they live in the package?**
   - What we know: they currently live at module level in `advisor.py` [VERIFIED: python/fdars/advisor.py:747-802]
   - What's unclear: whether they go into `advisor/__init__.py`, `advisor/_require.py`, or inline inside `advisor/providers/anthropic.py`
   - Recommendation: Put them in `advisor/__init__.py` for Phase 19 (they're already there effectively); add `advisor/_require.py` as a separate module only if needed. The monkeypatch test patches `sys.modules["anthropic"]` so any function that does `import anthropic` inside its body will be caught correctly regardless of location.

2. **`_selfcheck_alignment_diagnostics()` — keep or drop from public module?**
   - What we know: it's a private function (`_`-prefixed) at the bottom of `advisor.py` [VERIFIED: python/fdars/advisor.py:1132-1161]; not in `__all__`; not imported anywhere in tests
   - What's unclear: is it called from any CLI or build script?
   - Recommendation: Move to `advisor/aspects/alignment.py` where it tests the alignment builder directly. If any external caller exists, it would be a private call and can be updated.

---

## Sources

### Primary (HIGH confidence — direct Read this session)

- `python/fdars/advisor.py` (1161 lines) — extraction map, exact line ranges, existing signatures, `_require_anthropic()` guard pattern
- `python/fdars/__init__.py` (87 lines) — `sys.modules` injection pattern, `from fdars import advisor` at line 64
- `tests/test_advisor.py` (91 lines) — guardrail test details, monkeypatch pattern, integration test structure
- `pyproject.toml` (52 lines) — `[advisor]` extra declaration, Python version range
- `.planning/phases/19-provider-foundation-grounding-contract/19-CONTEXT.md` — locked decisions
- `.planning/REQUIREMENTS.md` — REQ-IDs and descriptions
- `.planning/research/ARCHITECTURE.md` — milestone-level component map, build sequence, patterns
- `.planning/research/PITFALLS.md` — grounding-leak, retry-contract, offline-testing pitfalls

### Secondary (MEDIUM confidence — milestone research, cross-checked against code)

- `ARCHITECTURE.md` `advisor.py` line 940–1007 citation — confirmed by direct Read this session
- `PITFALLS.md` retry-contract and grounding-violation heuristic recommendations — incorporated into design

---

## Metadata

**Confidence breakdown:**
- Extraction map: HIGH — every line range confirmed by Read this session
- Protocol design: HIGH — driven by locked decisions in CONTEXT.md + existing code structure
- Grounding heuristic: MEDIUM — the numeric-substring approach is Claude's Discretion; exact regex and float-repr handling may need tuning after first integration test run
- Package conversion mechanics: HIGH — `sys.modules` injection pattern confirmed by reading `__init__.py`

**Research date:** 2026-08-12
**Valid until:** This research covers a pure-refactor with no external dependencies — valid until `advisor.py` changes significantly.
