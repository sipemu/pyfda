# Pitfalls Research

**Domain:** Multi-provider LLM advisor — provider-agnostic structured output, grounding invariant, per-aspect advisors, offline/CI testing (fdars v3.0)
**Researched:** 2026-08-12
**Confidence:** MEDIUM (cross-checked against existing advisor.py, provider SDK docs, community issue trackers)

---

## Critical Pitfalls

### Pitfall 1: Schema Features That Don't Port Across Providers

**What goes wrong:**
A Pydantic schema that works perfectly with Anthropic's `client.messages.parse(output_format=Advice)` silently breaks or coerces incorrectly when the same schema is serialised for OpenAI `json_schema`, Gemini `response_schema`, or Ollama `format`. Specific failure modes per provider:

- **OpenAI (`json_schema`)**: All fields must appear in `required`. `Optional[str]` is not handled as "omissible" — the model will always emit the field. Use `str | None` with `null` type in the schema, not `Optional[...]` without `required`. The `nullable` keyword is silently ignored on some model versions, so `Union[str, None]` expressed as two type alternatives is safer than `nullable: true`. `additionalProperties` must be `false` (closed schema). Schemas above ~30 total fields increase latency and refusal risk. Deeply nested objects (5+ levels) are valid but increase constrained-decoding error rates.
- **Gemini (`response_schema`)**: The `google-genai` SDK rejects schemas containing `additionalProperties` at the client-validation layer, even though the API now supports it. Polymorphic schemas (type-discriminated unions — e.g., a `kind` field that changes the schema of sibling fields) are not supported. When prior tool calls are in the message history, structured output fails on Gemini 2.5 models but not 2.0 models. `json_mode` and `response_schema` behave inconsistently between model families.
- **Ollama (`format`)**: Since 0.3.0, passing a JSON schema to `format` enables GBNF-grammar constrained decoding. However, `format` and `think` (thinking/reasoning mode) are **mutually exclusive** — they cannot be used simultaneously. When `think=false` is set on some models (e.g., gemma4), the format constraint is silently ignored rather than raising an error. The `/api/chat` endpoint without `format` produces natural language only.
- **Cross-provider coercion**: The `Literal["parameter", "method", "none"]` on `kind` maps to an enum in every provider's schema, but enum enforcement is soft on weaker local models — the model emits an out-of-enum string that passes JSON parse but fails Pydantic validation. The `evidence: List[str]` field is frequently coerced to a single string on smaller Ollama models (type coercion without a type error).

**Why it happens:**
Developers author and test the schema against one provider (here, Anthropic) and assume JSON Schema is a universal standard. It is not: each provider serialises Pydantic models differently, enforces a different subset of JSON Schema Draft 2020-12, and applies different constraints at inference time vs. SDK validation time. The mismatch is invisible until the alternate provider is wired in.

**How to avoid:**
Define the canonical schema once in Pydantic (`Advice`, `Recommendation`) and write a `schema_for(provider)` serialiser per adapter. Each serialiser handles the provider's idiosyncratic requirements: OpenAI needs all-required + nullable union; Gemini needs `additionalProperties` stripped; Ollama needs a flat, non-nested JSON schema passed as `format`. Write a `test_schema_round_trip[anthropic|openai|gemini|ollama]` test for each provider that constructs the schema, serialises it via the adapter, then deserialises a known-good JSON response fixture through the same Pydantic model. These tests are all offline (no API calls) and must pass in CI.

**Warning signs:**
- A single `model_json_schema()` call whose output is passed to all four providers without per-provider transformation
- An integration test for provider X that passes but no corresponding test for providers Y and Z
- `Optional[str]` fields in `Recommendation` or `Advice` that are not explicitly marked `required` with a null union
- Gemini adapter code that includes `additionalProperties: false` in the serialised schema (triggers SDK-side `ValidationError` before the API call)
- Ollama adapter that passes `think=True` alongside `format=schema` (silently disabled constraint)

**Phase to address:**
Provider abstraction phase (the one introducing the `Provider` protocol and per-backend adapters). Schema portability tests belong in the same phase — do not defer to a later phase.

---

### Pitfall 2: Validate-and-Retry Without a Hard Contract

**What goes wrong:**
The retry loop for weaker/local models lacks a ceiling, a deterministic error state, or a fabrication check. Three sub-failures:

1. **Infinite retry loop**: The model repeatedly emits structurally invalid JSON (missing brace, trailing comma, markdown fence wrapping the object) and each attempt triggers another call. Without a max-retry cap, the caller blocks indefinitely. With a max-retry cap but no terminal exception, the caller silently receives `None` or a partially-valid dict.
2. **Silent fabrication on repair**: The repair step ("here is the invalid JSON, please correct it") gives the model an opportunity to invent new field values. A `rationale` field that was previously truncated gets "helpfully" extended with invented text. The repaired output is now structurally valid but contains fabricated content not derived from the diagnostics. This is invisible to Pydantic schema validation, which checks structure only.
3. **Cost/latency surprise on Ollama**: Ollama runs locally and has no monetary cost, but a 3-retry loop on a large local model can take 30–90s per `advise()` call. If the retry loop is triggered by a structural validation failure (which happens frequently on 3B–7B models without constrained decoding), the caller hangs. The pattern "retry with feedback" reliably triggers a second full generation.

**Why it happens:**
Retry logic is typically added reactively when a provider first fails in testing. The "correct the JSON" repair prompt is an easy reach, but it bypasses the grounding invariant because the correction prompt does not include the original diagnostics, so the model re-generates content from memory rather than from the supplied evidence. Max-retry is a config value that gets set once and never revisited as new providers are added with different failure rates.

**How to avoid:**
The `Provider` protocol's `generate(diagnostics, task, ...) -> Advice` method must define an explicit retry contract:
- `max_retries: int = 2` (never more than 2 structural retries — on the third attempt, raise `ProviderStructuralError(provider, attempts=3)`).
- On retry, the feedback prompt must re-include the full diagnostics blob from the original call — never repair without the original grounding input.
- After a successful structural parse, run the grounding check (see Pitfall 3) before returning. A structurally valid but grounding-failed response does not trigger another retry — it raises `GroundingViolationError` immediately. Retrying on grounding failure rewards fabrication.
- Ollama and other constrained-decoding providers should have `max_retries=0` when `format=schema` is enabled, because constrained decoding makes structural failure impossible by construction; retries on constrained providers are a sign of a schema serialisation bug, not a model reliability issue.
- Expose a `_validate_structure(raw: str) -> Advice` hook per adapter (not per call site) so the validation+retry logic is adapter-owned and testable in isolation.

**Warning signs:**
- `while attempts < max_retries` without a `finally: raise` branch
- A repair prompt that does not include `json.dumps(diagnostics)` from the original call
- `max_retries` set to 5 or higher (practically no ceiling given real model failure rates)
- An `except (json.JSONDecodeError, ValidationError): continue` that swallows all parse errors without logging the provider and attempt number
- A retry that runs on Ollama in `format=schema` mode (signals the schema serialiser is wrong, not the model)

**Phase to address:**
Provider abstraction phase (same as Pitfall 1). The retry contract must be written into the `Provider` protocol spec before any adapter is implemented.

---

### Pitfall 3: Grounding-Invariant Leaks Introduced by New Providers

**What goes wrong:**
The grounding invariant — "fdars computes every number; the LLM only interprets and cites" — is enforced in the existing Anthropic adapter through the system prompt and the `evidence: List[str]` required field. When new adapters are added, two leak paths emerge:

1. **System prompt suppression**: Provider adapters omit or truncate the grounding system prompt because the new provider's API passes system messages differently (Gemini uses `system_instruction`, OpenAI uses the `system` role in messages, Anthropic has a top-level `system` parameter). An adapter that wires the system prompt incorrectly (e.g., injects it as the first `user` message instead of the system role) may still produce structurally valid output, but the model is no longer constrained by the grounding instructions.
2. **Fallback prompt computation**: The "repair" prompt or the "retry with feedback" prompt does not reproduce the constraint "reason only from the diagnostics provided." A model receiving just "fix this JSON" will re-generate evidence entries from its parametric memory, inventing diagnostic values not present in the original dict.
3. **Provider-specific schema enforcement gap**: Anthropic's `client.messages.parse` rejects `parsed_output=None` and the adapter raises a clear error. OpenAI's structured output mode returns `refusal` strings rather than `None` in some refusal cases. Gemini returns an empty response on some safety-filter triggers. If an adapter treats an empty/refusal response as a non-error, the caller receives a blank `Advice` with empty evidence — the grounding invariant is vacuously satisfied (there is nothing to cite) but the output is useless.

**Why it happens:**
The grounding check lives in the system prompt and in the schema's `required: evidence` field. These are necessary but not sufficient: a model that ignores the system prompt produces required-but-fabricated evidence strings. Adding providers means each adapter must independently re-implement the prompt injection, and there is no centralised grounding check that all adapters pass through. The first provider (Anthropic) had human UAT to verify; subsequent providers have no equivalent gate.

**How to avoid:**
Centralise the grounding check as a post-generation validator that runs in the base `Provider` call path, not in each adapter:

```python
def _check_grounding(advice: Advice, diagnostics: dict) -> None:
    """Raise GroundingViolationError if any evidence item cites a value
    not present in the diagnostics dict (string repr match).
    """
    diag_values = {str(v) for v in _flatten_values(diagnostics)}
    for rec in advice.recommendations:
        for ev in rec.evidence:
            if not any(val in ev for val in diag_values):
                raise GroundingViolationError(
                    f"Evidence item cites no diagnostic value: {ev!r}"
                )
```

This is not a perfect semantic check but catches fabricated numbers. Run this check after every successful parse, before returning `Advice` to the caller. The test suite must include a `test_grounding_check_catches_fabrication` test per provider adapter (use a mock adapter that returns an `Advice` with invented evidence values and assert the check raises).

For system prompt injection: the `Provider` protocol defines `_system_prompt(task)` as a shared method that returns the exact grounding invariant string. Each adapter's `generate()` must call `_system_prompt(task)` and inject it using the provider's correct system-role mechanism — never inline the system prompt text in an adapter.

**Warning signs:**
- An adapter that passes the system prompt as the first `user` message (not the system role)
- A repair/retry prompt that does not reproduce the grounding instruction verbatim
- An adapter where `parsed_output is None` is treated as an empty `Advice()` rather than a raised exception
- No `test_grounding_check_catches_fabrication` test in the test suite
- A new adapter's integration test that only checks `isinstance(result, Advice)` without checking that `evidence` entries cite real diagnostic values

**Phase to address:**
Provider abstraction phase. The `_check_grounding` function must be part of the `Provider` base class before any adapter is added. Every adapter integration test must include one grounding-violation fixture.

---

### Pitfall 4: Offline/CI Testing Traps for Four Providers

**What goes wrong:**
Adding four providers creates four separate `import` paths, each guarded by an optional extra. The test suite breaks in three ways:

1. **Import-at-module-level pollution**: If `adapter/openai.py` imports `openai` at the top of the file, running `pytest tests/` in an environment without `[openai]` installed fails with `ImportError` at collection time — not at the test that needs it. The existing advisor.py pattern (`_require_anthropic()` inside the function body) is correct but easy to break when adding adapters.
2. **Python 3.9 vs. 3.10+ typing**: The `Provider` protocol uses `match/case` (structural pattern matching, Python 3.10+) or `X | Y` union syntax in type hints (Python 3.10+). Since fdars targets Python 3.9–3.14, any adapter that uses these features without `from __future__ import annotations` fails on Python 3.9. The existing codebase uses `from __future__ import annotations` correctly in `advisor.py`, but new adapter files may omit it.
3. **No recorded-fixture path for CI**: Each provider adapter requires a live API key to test the generate path. Without a fixture-replay mechanism, provider tests are either skipped in CI (acceptable) or make real API calls (expensive, flaky, secret-dependent). The existing pattern (`pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), ...)`) is correct for the Anthropic adapter, but replicating it for four providers leads to four separate env-var gates that are easy to misconfigure. An env var like `OPENAI_API_KEY` may be set in the developer's environment for a different project, causing the OpenAI integration test to unexpectedly run in CI.

**How to avoid:**
- All provider adapters must use deferred import: no `import openai` at module top level. Use `_require_openai()`, `_require_gemini()`, `_require_ollama()` guards identical in structure to the existing `_require_anthropic()`.
- Add a CI smoke test that imports `fdars.advisor` (and each adapter module by name) in a bare venv with only the core `fdars` package installed (no provider extras). This test must pass in zero-key CI.
- Use recorded response fixtures for offline adapter unit tests: store a `tests/fixtures/adapter_responses/<provider>/advice_response.json` per provider. The fixture is the raw API response. The adapter test loads the fixture, passes it through the adapter's `_parse_response()` method, and asserts the resulting `Advice`. No network call. No API key.
- For Python 3.9 compatibility: add a CI matrix entry for Python 3.9 that runs all offline advisor tests. Any `X | Y` union or `match/case` in advisor code must be caught by this matrix entry.
- Gate integration tests strictly: use `pytest.mark.integration` on all live-key tests. The CI job that runs integration tests must explicitly set `FDARS_INTEGRATION=1` and fail fast if the required key is missing, rather than silently skipping. This prevents the "key set from another project" silent run.

**Warning signs:**
- `import openai` or `import google.generativeai` at the top level of any adapter file
- `X | Y` union syntax in function signatures in files that do not have `from __future__ import annotations`
- Integration tests that use `skipif(not os.environ.get("OPENAI_API_KEY"))` without also asserting `FDARS_INTEGRATION=1` is set
- No `tests/fixtures/adapter_responses/` directory with at least one fixture per adapter
- A bare-venv import test that is not in the CI matrix

**Phase to address:**
Provider abstraction phase for the import guard and Python 3.9 compat. Fixture infrastructure should be established before the first adapter is implemented, not retroactively.

---

### Pitfall 5: Dependency and Config Traps Across 3–4 Provider SDKs

**What goes wrong:**
Managing four provider SDKs in one package introduces compounding configuration and versioning problems:

1. **Version drift**: The `openai` SDK breaks its API surface frequently (v0.x → v1.x was a complete rewrite; `AsyncOpenAI` vs. `OpenAI`, `response_format` parameter shape changes between minor versions). Pinning `openai>=1.40.0` is necessary because structured outputs were added in 1.40. Failing to pin means a user with `openai==1.30` installs the `[openai]` extra and gets a runtime `AttributeError` on `.parse()` with no clear error message.
2. **`base_url` / auth confusion for OpenAI-compatible endpoints**: The OpenAI Python SDK reads `OPENAI_API_KEY` from the environment unconditionally when using `OpenAI()` without explicit `api_key`. For local/compatible endpoints (vLLM, LM Studio, LocalAI), the user sets `base_url` but may not set a dummy `api_key`, causing a `openai.AuthenticationError` from the SDK's own validation before the request is sent. The error message says "provide an API key" but the underlying endpoint doesn't require one. The adapter must accept `api_key=None` and pass `api_key="none"` (a non-empty dummy) to the SDK when the user configures a local base URL without a key.
3. **`OPENAI_API_KEY` env var bleeds into Ollama adapter**: If the user has `OPENAI_API_KEY` set in their shell (for another project), and the Ollama adapter uses `openai.OpenAI(base_url="http://localhost:11434/v1")` (Ollama's OpenAI-compatible endpoint), the SDK reads the env var and sends it as a Bearer token. This is harmless for Ollama (it ignores auth) but creates confusion when debugging: the log shows an OpenAI-style auth header sent to a local Ollama instance.
4. **Extras that accidentally become hard deps**: If `pyproject.toml` lists `[project.dependencies]` instead of `[project.optional-dependencies]` for provider SDKs, or if an `__init__.py` imports from an adapter at module load time, the provider SDK becomes a hard requirement. Users who `pip install fdars` without any provider extra get an `ImportError` on the first `import fdars.advisor` call if any adapter module is imported at package init time.
5. **Gemini SDK namespace collision**: The `google-generativeai` SDK and the `google-genai` SDK coexist on PyPI with overlapping namespace (`import google.generativeai` vs. `import google.genai`). The newer `google-genai` is the supported one as of late 2025, but many tutorials still reference `google-generativeai`. Listing the wrong one in `[gemini]` extra installs the deprecated package, which imports successfully but has a completely different API surface.

**How to avoid:**
- Pin minimum versions for all provider extras: `openai>=1.40.0`, `anthropic>=0.72.0`, `google-genai>=1.0`, `ollama>=0.3.0`. Document the minimum version and why (what feature it unlocks) in a comment in `pyproject.toml`.
- The OpenAI-compatible adapter must accept `api_key: str | None = None` and map `None` to `"none"` (dummy) when constructing the client with a custom `base_url`. Document this in the adapter docstring and the user-facing configuration docs.
- Use `google-genai` (not `google-generativeai`) in the `[gemini]` extra. Add a comment and a CI check that `google.generativeai` is not importable in the gemini test environment.
- No provider SDK may be imported at `fdars` package init time. The pattern to verify: `python -c "import fdars; print('ok')"` must succeed with zero provider extras installed.
- Add a `test_no_hard_deps` test that mocks all provider extras as absent (using `sys.modules` patching) and asserts `import fdars.advisor; fdars.advisor.build_diagnostics(...)` succeeds.

**Warning signs:**
- `import openai` in `python/fdars/__init__.py` or `python/fdars/advisor.py` at module scope
- `[project.dependencies]` in `pyproject.toml` containing `openai` or `anthropic`
- An adapter that constructs `OpenAI()` without `api_key` when `base_url` is set to a local endpoint
- `import google.generativeai` anywhere in the codebase (use `google.genai` instead)
- A user bug report saying "I got an AuthenticationError when using Ollama"

**Phase to address:**
Provider abstraction phase for the `pyproject.toml` extras definitions and import guards. Configuration documentation (base_url, key handling) should be in the same phase. The `google-genai` vs. `google-generativeai` call must be made before writing the Gemini adapter.

---

### Pitfall 6: Scaling to ~7 Per-Aspect Advisors — Prompt Sprawl and Test Explosion

**What goes wrong:**
Each per-aspect advisor (clustering, smoothing, FPCA/regression, alignment, basis, depth/outliers, monitoring/SPM) needs its own `build_diagnostics` branch, its own system prompt task clause, and its own suite of task families (interpretation, parameter, method). With 7 aspects × 3 task families × 4 providers, the naive approach produces 84 integration test cases, 21 prompt templates, and 7 diagnostics builders that share no code and drift from each other. Concrete failure modes:

1. **Divergent diagnostic key names**: `alignment` uses `amplitude_mean` but `depth` uses `mean_amplitude` (or `amplitude_distance_mean`). Downstream grounding checks that look for diagnostic values by key cannot be shared. The system prompt for one aspect references a key name that does not exist in the diagnostics dict of another.
2. **Prompt sprawl**: Each `_system_prompt(task)` variant grows independently. The FDA primer (currently shared in the base string) gets duplicated-and-diverged. The grounding invariant sentence in one aspect's prompt drifts from another's. The `evidence` instruction becomes weaker in later aspects because the author shortens it for brevity.
3. **Task family contracts not shared**: `interpretation` in the alignment advisor means "explain amplitude vs phase split." `interpretation` in the monitoring advisor means "explain control-limit exceedances." If these return `Advice` objects with the same schema but incompatible semantic content of the `interpretation` field, callers that handle both become inconsistent.
4. **Combinatorial test explosion**: 7 aspects × 4 providers × 3 task families = 84 integration test paths. Running all live is expensive and slow. Running none offline means a broken aspect+provider combination can ship undetected.

**How to avoid:**

**DRY diagnostics contract**: Define a shared `DiagnosticsKeys` namespace (a frozen dataclass or module-level constants) that specifies the key names for values shared across aspects. All `_build_*_diagnostics` functions must use `DiagnosticsKeys.AMPLITUDE_MEAN` (not the string literal) for the same concept. Write a `test_diagnostics_key_consistency` test that imports all aspect builders, calls them with synthetic inputs, and asserts that shared concept keys are spelled identically.

**Shared prompt scaffold**: `_system_prompt(task)` must remain a single function (not 7 copies). The base grounding invariant and FDA primer do not change per aspect. Each aspect adds a narrow **aspect clause** (what this aspect's diagnostics mean, what parameters are tunable) and nothing else. The grounding invariant sentence is a module-level constant, never inlined.

**Task family contracts are aspect-agnostic**: `interpretation`, `parameter`, and `method` have the same `Advice` output schema regardless of aspect. The task clause tells the model how to interpret within that aspect, but the output structure (and the grounding requirement on `evidence`) is identical. This means a single `_validate_advice(advice, task, diagnostics)` function works for all aspects.

**Test strategy — two-layer**: Layer 1 is offline aspect tests (7 aspects × fixtures = 7 tests, no API calls, no provider). Layer 2 is provider adapter tests (4 providers × 1 fixture response per provider = 4 tests, no aspect-specific logic). The combinatorial cross is not tested in CI — it is covered by the contract that adapters are aspect-agnostic and aspects are provider-agnostic. A single live integration test per provider (using one aspect, typically clustering as the canonical example) covers the end-to-end path. This keeps the live test count at 4, not 84.

**Warning signs:**
- A second copy of the grounding invariant string anywhere in the codebase
- A `_system_prompt_alignment()`, `_system_prompt_depth()`, etc. (per-aspect system prompt functions rather than a single function with an aspect clause)
- A `build_diagnostics` function that raises `ValueError` for a newly-added aspect because no branch was added (signals the aspect was not integrated into the shared dispatcher)
- More than one `test_advise_returns_advice_schema` test class that differs only in the aspect used (signals the test is not using the provider-fixture abstraction correctly)
- Diagnostic key names that differ by aspect for the same concept (e.g., `amplitude_mean` vs. `mean_amplitude`)

**Phase to address:**
Shared prompt scaffold and DRY diagnostics contract: provider abstraction phase (before per-aspect advisors are built). Per-aspect advisor implementation: per-aspect advisor phase(s). Test strategy definition: provider abstraction phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Copy `_system_prompt()` per aspect and edit | Fast to implement new aspect | Grounding invariant sentence drifts; 7 copies to update on every prompt revision | Never: use a single function with an aspect clause parameter |
| Use `json.loads(response.content)` without schema validation | Works immediately on happy path | Silent fabrication, type coercions, missing fields — all accepted | Never for production; only in one-off debugging scripts |
| Import provider SDK at module level in adapter | Simpler code | Breaks `import fdars.advisor` in bare envs; import-time `ImportError` collection failures in pytest | Never |
| Set `max_retries=5` for local models | Handles flaky small models | 5× latency on every structural failure; no deterministic failure mode | Never: use constrained decoding (`format=schema`) instead and set `max_retries=0` |
| Hardcode `api_key="none"` for all local endpoints | Works for most setups | Masks auth misconfiguration for endpoints that do require a key | Acceptable only as a default when `base_url` points to localhost; make configurable |
| Inline the full diagnostics dict in the retry/repair prompt without grounding instruction | Quick repair | Model regenerates evidence from memory, not from diagnostics | Never |
| One provider adapter, skip the others until needed | Ship faster | Provider protocol ossifies around the first adapter's assumptions; retrofitting the 2nd provider is harder than designing for 4 from the start | Never: define the protocol for all 4 before writing any adapter |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenAI `response_format` + Pydantic | Passing `model.model_json_schema()` directly — includes `title` and `$defs` keys that the OpenAI API rejects in strict mode | Strip `title` at schema root, inline `$defs` references before passing to `response_format` |
| Gemini `response_schema` + `additionalProperties` | Pydantic's default schema includes `additionalProperties: false` which the `google-genai` SDK's client-side validator rejects | Use `response_json_schema` (raw dict) and remove `additionalProperties` from the serialised schema before passing |
| Ollama `format` + thinking models | Setting `think=True` alongside `format=schema` — format constraint silently disabled on some models | Never set `think=True` with a format schema; use two-stage: think first (no format), then format-constrained extraction call |
| OpenAI-compatible `base_url` (vLLM/LM Studio) + `OpenAI()` | `OpenAI()` reads `OPENAI_API_KEY` from env and sends it to the local endpoint; if unset, SDK raises `AuthenticationError` before the request | Pass `api_key="none"` explicitly when constructing `OpenAI(base_url=local_url, api_key="none")` |
| `ANTHROPIC_API_KEY` env var present in developer shell | OpenAI integration tests run unexpectedly if the test skip logic checks the wrong env var | Gate each provider integration test on `FDARS_INTEGRATION=1` AND the provider-specific key; both must be set |
| Pydantic v1 vs. v2 | `Advice.schema()` (v1) vs. `Advice.model_json_schema()` (v2) — calling v1 method in a v2 environment silently returns a deprecated schema | Always use `model_json_schema()` and add a `pydantic>=2.0` pin in `[advisor]` extra |
| Gemini function-call history + structured output | Structured output fails on Gemini 2.5 if prior tool calls are in the message history | For Gemini adapter, use fresh conversation context per `advise()` call; do not reuse session history |

---

## "Looks Done But Isn't" Checklist

- [ ] **Provider abstraction tested offline**: Each adapter has a fixture-based test that parses a stored response JSON through `_parse_response()` without any API call — verify this test runs in CI without keys
- [ ] **Grounding check wired on every adapter**: `_check_grounding(advice, diagnostics)` is called after every `_parse_response()` call — grep for `_check_grounding` in each adapter file
- [ ] **System prompt grounding invariant not duplicated**: There is exactly one copy of the "reason only from the diagnostics provided" sentence — verify with `grep -r "reason only from" python/`
- [ ] **All four adapters implement the same `Provider` protocol**: Run `mypy --strict` on each adapter and verify the `@runtime_checkable Protocol` check passes
- [ ] **Python 3.9 CI matrix entry passes**: A 3.9 matrix entry runs all offline advisor tests — check the CI matrix in `.github/workflows/`
- [ ] **Bare-venv import test passes**: `python -c "import fdars.advisor; fdars.advisor.build_diagnostics({'centers': [[1,2]],'cluster':[0],'k':1}, method='clustering')"` succeeds with zero provider extras installed
- [ ] **`max_retries` cap is enforced**: Every adapter's retry loop raises `ProviderStructuralError` on the third failure — check that no adapter has a bare `while True:` or unbounded retry
- [ ] **OpenAI-compatible adapter handles missing api_key**: When `base_url` is set to a localhost URL and no `api_key` is given, the adapter passes `"none"` not `None` to `OpenAI()` — verify with a unit test
- [ ] **`google-genai` not `google-generativeai`**: `grep -r "google.generativeai" python/` returns no hits
- [ ] **All per-aspect `build_diagnostics` branches dispatched**: `build_diagnostics(..., method="depth")` does not raise `ValueError` — verify each new aspect has a dispatch branch
- [ ] **Grounding violation test per adapter**: Each adapter has a `test_grounding_check_catches_fabrication` test with a fixture that contains invented evidence values — verify it raises `GroundingViolationError`

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Schema feature incompatibility discovered in production for a provider | MEDIUM | Add `schema_for(provider)` serialiser to the adapter; write the round-trip test; re-validate with the provider's sandbox |
| Infinite retry loop in production | LOW | Add `max_retries` cap at the `Provider` base class level; deploy hotfix; check if constrained decoding can replace retry for the affected provider |
| Grounding violation discovered via user report | HIGH | Audit all adapters for system prompt injection correctness; add `_check_grounding` if missing; add per-adapter grounding violation tests; run live integration tests to verify |
| Optional dep became a hard dep (broke bare installs) | LOW | Move to `[project.optional-dependencies]`; add deferred import guard; add bare-venv smoke test to CI |
| Per-aspect diagnostic key names diverged | MEDIUM | Define `DiagnosticsKeys` constants; update all builders to use constants; update all system prompt task clauses that reference key names; run `test_diagnostics_key_consistency` |
| Gemini SDK namespace wrong (`google-generativeai`) | LOW | Swap to `google-genai` in extras; update import; re-run adapter tests |
| Ollama thinking+format conflict causes silent grounding bypass | MEDIUM | Disable `think=True` in Ollama adapter; document the constraint; add a test that asserts `think` is never passed with `format` |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Schema portability across providers | Provider abstraction phase | `test_schema_round_trip[provider]` tests pass offline for all four providers |
| Validate-and-retry without a hard contract | Provider abstraction phase | Every adapter raises `ProviderStructuralError` after `max_retries` in a unit test |
| Grounding-invariant leaks via new providers | Provider abstraction phase | `test_grounding_check_catches_fabrication` per adapter; system prompt not duplicated (grep) |
| Offline/CI testing traps (import errors, 3.9 compat) | Provider abstraction phase | Python 3.9 CI matrix passes; bare-venv smoke test passes |
| Dependency and config traps (version pins, base_url, namespace) | Provider abstraction phase | No hard deps in `[project.dependencies]`; `test_no_hard_deps` passes; `google-generativeai` grep returns zero hits |
| Prompt sprawl / diagnostic key divergence across aspects | Provider abstraction phase (define scaffold); per-aspect phases (enforce it) | Single `_system_prompt` function; `DiagnosticsKeys` constants used by all builders; `test_diagnostics_key_consistency` passes |
| Combinatorial test explosion | Provider abstraction phase | Two-layer test strategy documented; live integration test count capped at 4 (one per provider); aspect-specific tests are offline |

---

## Sources

- Direct inspection of `python/fdars/advisor.py` (existing Anthropic-only implementation: `_require_anthropic()`, `_system_prompt()`, `advise()`, `build_diagnostics()` branches) — HIGH confidence (first-party)
- Direct inspection of `tests/test_advisor.py` (existing test pattern: offline vs. env-gated integration) — HIGH confidence (first-party)
- OpenAI Structured Outputs official docs and GitHub issue #1049 (nullable modifier silently ignored) — MEDIUM confidence (verified against source)
- Gemini `google-genai` SDK GitHub issues #1815 (additionalProperties), #706 (2.0 vs. 2.5 inconsistency) — MEDIUM confidence (verified against source)
- Ollama GitHub issue #10929 (thinking mode + structured output conflict), issue #15260 (think=false silently disabling format) — MEDIUM confidence (verified against source)
- Community writeups on validate-and-retry JSON repair (60%→97% success, +200ms latency) — LOW confidence (web, not verified against first-party source)
- Community writeups on OpenAI-compatible `base_url` / dummy `api_key` pattern for local endpoints — LOW confidence (web)
- `logic.inc/resources/structured-outputs-guide` (cross-provider JSON Schema comparison) — LOW confidence (web)

---

*Pitfalls research for: fdars v3.0 — provider-agnostic advisor with per-aspect coverage*
*Researched: 2026-08-12*
