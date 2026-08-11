# Architecture Research

**Domain:** Provider-agnostic LLM advisor layer + per-aspect advisor coverage (fdars v3.0)
**Researched:** 2026-08-12
**Confidence:** HIGH (derived from direct codebase analysis of advisor.py, mcp/server.py, mcp/_runner.py, mcp/_compare.py, mcp/_registry.py, __init__.py, .claude/skills/fdars-advisor/SKILL.md)

---

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CONSUMER SURFACES                                 │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐  │
│  │  Python API       │  │  MCP / Tool Server   │  │  Agent Skill         │  │
│  │  fdars.advisor    │  │  fdars.mcp.server    │  │  .claude/skills/     │  │
│  │  advise()         │  │  fdars_build_diag    │  │  fdars-advisor/      │  │
│  │  build_diag_*()   │  │  fdars_run_method    │  │  SKILL.md            │  │
│  │  (public API)     │  │  fdars_compare_run   │  │  (orchestration)     │  │
│  └────────┬─────────┘  └──────────┬───────────┘  └──────────┬───────────┘  │
└───────────┼─────────────────────────┼──────────────────────────┼─────────────┘
            │                         │                          │
            ▼                         ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ADVISOR CORE  (python/fdars/advisor/)             │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Schema layer (Advice, Recommendation — Pydantic / fallback stubs)   │  │
│  │  _system_prompt(task, aspect)   grounding invariant + FDA primer      │  │
│  │  advise(diagnostics, *, task, domain_context, provider=…) → Advice   │  │
│  └────────────────────────────────────┬─────────────────────────────────┘  │
│                                       │                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  PROVIDER LAYER  (advisor/providers/)                │  │
│  │                                                                      │  │
│  │  Provider (Protocol)                                                 │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │  │
│  │  │ AnthropicAdapter│  │ OpenAIAdapter     │  │ GeminiAdapter      │  │  │
│  │  │ (structured out)│  │ (structured out   │  │ (structured out /  │  │  │
│  │  │  parse() path)  │  │  / json fallback) │  │  json fallback)    │  │  │
│  │  └─────────────────┘  └──────────────────┘  └────────────────────┘  │  │
│  │  ┌─────────────────┐  ┌──────────────────────────────────────────┐  │  │
│  │  │ OllamaAdapter   │  │ ValidateAndRetry wrapper (all adapters)  │  │  │
│  │  │ (json fallback) │  │ schema-validate → repair-prompt → retry  │  │  │
│  │  └─────────────────┘  └──────────────────────────────────────────┘  │  │
│  │  resolve_provider(config/env) → Provider                            │  │
│  └────────────────────────────────────┬─────────────────────────────────┘  │
│                                       │                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  DIAGNOSTICS LAYER  (advisor/aspects/)               │  │
│  │                                                                      │  │
│  │  build_diagnostics(result, method, **kw) → dict  ← UNCHANGED API    │  │
│  │  (dispatcher; routes to per-aspect builder below)                   │  │
│  │                                                                      │  │
│  │  Aspects:                                                            │  │
│  │  ┌───────────────┐ ┌──────────────┐ ┌────────────────────────────┐  │  │
│  │  │ represent/    │ │ smoothing/   │ │ alignment/                  │  │  │
│  │  │ basis         │ │ pspline/gcv  │ │ karcher/srsf                │  │  │
│  │  └───────────────┘ └──────────────┘ └────────────────────────────┘  │  │
│  │  ┌───────────────┐ ┌──────────────┐ ┌────────────────────────────┐  │  │
│  │  │ depth/        │ │ regression/  │ │ monitoring/                 │  │  │
│  │  │ outliers      │ │ fpca/fosr    │ │ spm/tolerance/conformal     │  │  │
│  │  └───────────────┘ └──────────────┘ └────────────────────────────┘  │  │
│  │  ┌───────────────┐                                                   │  │
│  │  │ classification│                                                   │  │
│  │  └───────────────┘                                                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPUTE LAYER  (unchanged)                                │
│  fdars-core (Rust) ← PyO3 bindings ← fdars native submodules               │
│  fdars computes all numbers; advisor layer only interprets                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | File (new/modified) |
|-----------|---------------|---------------------|
| `Provider` protocol | Defines `complete_structured(schema, messages) -> dict` + capability flags | NEW `advisor/providers/_protocol.py` |
| `AnthropicAdapter` | Wraps existing `client.messages.parse()` path; moves inline call out of `advise()` | NEW `advisor/providers/anthropic.py` (REFACTORS existing code in `advisor.py`) |
| `OpenAIAdapter` | `client.chat.completions.parse()` for structured output; json fallback | NEW `advisor/providers/openai.py` |
| `GeminiAdapter` | Gemini structured output or json-mode + schema injection | NEW `advisor/providers/gemini.py` |
| `OllamaAdapter` | Local http `/api/chat` JSON mode; no API key | NEW `advisor/providers/ollama.py` |
| `ValidateAndRetry` | Schema-validates provider output; repair-prompt retry loop; wraps all adapters | NEW `advisor/providers/_validate.py` |
| `resolve_provider()` | Factory: reads config/env → returns instantiated Provider | NEW `advisor/providers/_factory.py` |
| `advise()` | Grounded call; refactored to accept `provider=` instead of inline Anthropic | MODIFIED `advisor/__init__.py` (was `advisor.py`) |
| `_system_prompt()` | Grounding prompt; gains aspect-awareness for new aspects | MODIFIED `advisor/__init__.py` |
| `Advice` / `Recommendation` | Pydantic schema; unchanged surface; centralized here | STAYS in `advisor/__init__.py` |
| `build_diagnostics()` | Dispatcher; gains new aspect method strings | MODIFIED `advisor/__init__.py` |
| `_build_*_diagnostics()` | Per-aspect builders; existing 5 stay; 2+ new aspects added | NEW/MODIFIED in `advisor/aspects/` |
| `mcp/server.py` | `_SUPPORTED_METHODS` set extended; `provider` param added to tool signatures | MODIFIED |
| `mcp/_runner.py` | `run_method()` dispatch extended to new aspects | MODIFIED |
| `mcp/_compare.py` | `_ALLOWED_PARAMS` extended; no structural change | MODIFIED |
| `.claude/skills/fdars-advisor/SKILL.md` | `description` extended to cover new aspects + provider selection | MODIFIED |

---

## Recommended Project Structure

```
python/fdars/
├── advisor/                      # NEW: package replaces advisor.py
│   ├── __init__.py               # Re-exports build_diagnostics, advise, describe_cluster_differences,
│   │                             # Advice, Recommendation — public API unchanged
│   ├── _schema.py                # Advice + Recommendation pydantic models + fallback stubs
│   │                             # (moved out of __init__ for clarity)
│   ├── _prompts.py               # _system_prompt(task, aspect) — grounding prompt
│   │                             # gains aspect-specific FDA primer extensions
│   │
│   ├── providers/                # NEW: Provider protocol + per-backend adapters
│   │   ├── __init__.py           # exports: Provider, resolve_provider, AnthropicAdapter, …
│   │   ├── _protocol.py          # Provider Protocol (runtime_checkable) + CapabilityFlags
│   │   ├── _validate.py          # ValidateAndRetry wrapper: schema-validate → repair-prompt → retry
│   │   ├── _factory.py           # resolve_provider(provider=, model=, api_key=, base_url=, **kw)
│   │   ├── anthropic.py          # AnthropicAdapter — wraps messages.parse(); native structured output
│   │   ├── openai.py             # OpenAIAdapter — chat.completions.parse() + json fallback
│   │   ├── gemini.py             # GeminiAdapter — structured output or json-mode
│   │   └── ollama.py             # OllamaAdapter — local /api/chat; no API key; json-mode only
│   │
│   └── aspects/                  # NEW: per-aspect diagnostic builders
│       ├── __init__.py           # exports: build_diagnostics_<aspect> for each aspect
│       ├── _base.py              # shared helpers: _to_float_list, _safe_float, etc.
│       ├── smoothing.py          # _build_smoothing_diagnostics (moved from advisor.py)
│       ├── basis.py              # _build_basis_diagnostics (moved from advisor.py)
│       ├── alignment.py          # _build_alignment_diagnostics (moved from advisor.py)
│       ├── fpca.py               # _build_fpca_diagnostics (moved from advisor.py)
│       ├── clustering.py         # _build_clustering_diagnostics (moved from advisor.py)
│       ├── depth.py              # NEW: depth + outlier diagnostics
│       ├── regression.py         # NEW: FOSR, FANOVA, PLS, robust regression diagnostics
│       ├── monitoring.py         # NEW: SPM / tolerance / conformal / seasonal diagnostics
│       └── classification.py     # NEW: LDA, QDA, k-NN classification diagnostics
│
├── mcp/
│   ├── __init__.py               # unchanged
│   ├── _registry.py              # unchanged
│   ├── _runner.py                # extended: new aspect methods added to dispatch
│   ├── _compare.py               # extended: _ALLOWED_PARAMS gains new aspect params
│   └── server.py                 # extended: _SUPPORTED_METHODS set expanded;
│                                 #   fdars_build_diagnostics + fdars_run_method gain
│                                 #   optional `provider` param (str, passed to resolve_provider)
│
└── __init__.py                   # unchanged: advisor already registered via sys.modules injection
                                  #   advisor/ package __init__ re-exports same public names

.claude/skills/fdars-advisor/
├── SKILL.md                      # description + compatibility updated; walkthrough unchanged
└── scripts/
    └── fdars_advisor_walkthrough.py  # unchanged (uses public API only)
```

### Structure Rationale

- **`advisor/` package (not `advisor.py`):** Splitting into a package is required because the provider layer and aspect layer each need their own submodules, and Python's import system requires a directory for subpackages. The public API (`build_diagnostics`, `advise`, `Advice`, `Recommendation`) is re-exported from `advisor/__init__.py` — callers see no change.
- **`advisor/providers/`:** All LLM-backend code lives here and is isolated from the diagnostic computation. This keeps the offline determinism test (`build_diagnostics`) free of any LLM import. No provider code is imported at module level in `advisor/__init__.py`; it is imported lazily inside `advise()` exactly as the anthropic import is today.
- **`advisor/aspects/`:** Each aspect's `_build_*_diagnostics` function moves into a dedicated file. The dispatcher in `advisor/__init__.py` grows the aspect name to module routing. This structure makes it straightforward to add a new aspect without touching existing aspect files. Shared utility functions (`_safe_float`, `_to_float_list`) live in `_base.py` and are imported by each aspect module.
- **`_schema.py` and `_prompts.py`:** Separating schema and prompt from the dispatch logic keeps `advisor/__init__.py` readable. Pydantic models stay in `_schema.py`; the grounding prompt system (with FDA primer extensions per aspect) lives in `_prompts.py`.

---

## Architectural Patterns

### Pattern 1: Provider Protocol with Capability Flags

**What:** Define `Provider` as a `typing.Protocol` with a single required method `complete_structured(schema: type, messages: list[dict]) -> dict`. Additionally, each adapter exposes a `CapabilityFlags` named tuple with `native_structured_output: bool` so the `ValidateAndRetry` wrapper knows whether to trust the raw output or always run schema validation.

**When to use:** Every LLM backend is accessed through this protocol. The `advise()` function accepts a `Provider` instance (or a string resolved by `resolve_provider()`). No `advise()` code path directly imports `anthropic`, `openai`, `google.generativeai`, or `ollama` — those imports live exclusively in their adapter files.

**Concrete protocol surface:**

```python
# advisor/providers/_protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class Provider(Protocol):
    name: str          # e.g. "anthropic", "openai", "gemini", "ollama"
    model: str         # e.g. "claude-opus-4-8", "gpt-4o", "gemini-2.0-flash"

    def complete_structured(
        self,
        schema: type,          # Pydantic model class (Advice)
        messages: list[dict],  # [{"role": "user", "content": "..."}]
        system: str,           # system prompt
    ) -> dict:
        """Return a dict conforming to schema's JSON schema. Raises on failure."""
        ...

    @property
    def supports_native_structured_output(self) -> bool:
        """True if the backend handles schema enforcement natively."""
        ...
```

**Trade-offs:** A Protocol (not ABC) lets adapters be duck-typed, which simplifies testing via simple mock objects. The `system` argument is passed explicitly rather than embedded in `messages` because Anthropic's API treats system as a top-level field while OpenAI/Ollama embed it in messages — the adapter handles this translation.

### Pattern 2: ValidateAndRetry Wrapper (Grounding Preservation Across Backends)

**What:** A wrapper class that takes any `Provider` and adds schema validation + repair retry on top. After a `complete_structured()` call, it attempts `Advice.model_validate(raw_dict)`. On failure it sends a repair prompt (`"The previous output did not conform to schema. Errors: {errors}. Re-output only the valid JSON."`) and retries once. If the second attempt also fails it raises `ValueError` with the full error.

**When to use:** Wrap every adapter at construction time via `ValidateAndRetry(adapter, max_retries=1)`. Adapters with `supports_native_structured_output = True` (Anthropic, OpenAI with `strict=True`) still route through the wrapper but the first pass is unlikely to fail — the wrapper is a safety net, not the primary path.

**Why this design (not per-adapter retry):** Centralizing retry logic in one place means the grounding invariant is enforced identically for every backend. Local models (Ollama) and Gemini (when falling back to json-mode) benefit most, but even Claude benefits from a uniform failure mode.

**Key constraint:** The repair prompt must NOT inject new numbers or diagnostic values. It only describes schema errors. The grounding invariant (fdars computes every number) is preserved because the repair prompt re-sends the original user message (which contains the diagnostics dict) alongside the error description.

### Pattern 3: Per-Aspect Diagnostic Builder with Shared Dispatcher

**What:** Every aspect exposes a `build_diagnostics_<aspect>(raw: dict, **kwargs) -> dict` function. The top-level `build_diagnostics(result, method, **kwargs)` dispatcher maps method strings to aspect modules. Aspect functions are imported lazily inside the dispatcher to avoid import overhead when building diagnostics for a different aspect.

**When to use:** When adding a new aspect (e.g., `depth`, `monitoring`), write a new `advisor/aspects/depth.py` with a `build_diagnostics_depth(raw, **kwargs) -> dict` function, add the method string to the dispatcher's lookup dict, and add the string to `_SUPPORTED_METHODS` in `mcp/server.py` and `mcp/_runner.py`.

**Shared utilities via `_base.py`:** Functions like `_safe_float(v) -> float | None` and `_to_float_list(arr) -> list[float]` are used by every aspect builder. They already exist inline in the current `advisor.py` private functions. Moving them to `_base.py` eliminates duplication across the 9 aspect files.

**Grounding machinery stays centralized:** The `Advice` schema, `_system_prompt()`, and the `advise()` call are NOT duplicated per aspect. Per-aspect advisors are achieved purely by:
1. A per-aspect `build_diagnostics_<aspect>()` function that computes the right diagnostic keys.
2. `_system_prompt(task, aspect)` gains an `aspect` argument that appends an aspect-specific FDA primer clause to the base prompt (e.g., for `depth`, it explains Fraiman-Muniz depth, modal depth, and outlier flagging). The base grounding invariant text is unchanged.
3. The caller passes the right `method` string; `build_diagnostics` and `_system_prompt` do the rest.

### Pattern 4: Provider Resolution via Config / Environment

**What:** `resolve_provider(provider=None, model=None, api_key=None, base_url=None, **kw) -> Provider` reads provider identity from (in priority order): explicit `provider=` argument, `FDARS_PROVIDER` env var, fallback to `"anthropic"` (preserving current behavior). Model defaults per provider: `anthropic` → `claude-opus-4-8`, `openai` → `gpt-4o`, `gemini` → `gemini-2.0-flash`, `ollama` → `llama3.2`.

**API key resolution per adapter:**
- `anthropic`: `api_key` arg → `ANTHROPIC_API_KEY` env
- `openai`: `api_key` arg → `OPENAI_API_KEY` env; `base_url` arg → `OPENAI_BASE_URL` env (enables vLLM/LM Studio/LocalAI compatibility)
- `gemini`: `api_key` arg → `GEMINI_API_KEY` or `GOOGLE_API_KEY` env
- `ollama`: no API key; `base_url` arg → `OLLAMA_BASE_URL` env (default `http://localhost:11434`)

**Import isolation:** Each adapter file is only imported inside `resolve_provider()` after the provider is identified. Importing `fdars.advisor` with no extras installed is still side-effect-free (same as today). The `[advisor]` extra remains for Anthropic; `[openai]`, `[gemini]`, `[ollama]` are new extras each installing only the required SDK.

### Pattern 5: MCP Tool Layer — Provider as Optional String Param

**What:** The existing MCP tools (`fdars_build_diagnostics`, `fdars_run_method`, `fdars_compare_run`) gain an optional `provider: str | None = None` parameter. When non-None, the tool calls `resolve_provider(provider)` and passes the resolved `Provider` to `advise()`. When None (default), behavior is identical to today — `advise()` uses its own default resolution (Anthropic).

**Note:** `fdars_build_diagnostics` is offline and does NOT call `advise()` — it has no `provider` parameter. Only `fdars_run_method` and `fdars_compare_run` would optionally accept `provider` if those tools are extended to return advice alongside the result handle. If the decision is to keep the MCP tools purely computational (no LLM in the tool boundary), then `provider` selection belongs only in the Python API surface, and the MCP tools remain provider-agnostic. Recommend keeping the MCP tools LLM-free for now (same as today), with a `fdars_advise` tool added in a later phase if needed. This keeps the change surface minimal.

---

## Data Flow

### advise() Call Path (v3.0)

```
User calls advise(diagnostics, task="interpretation", aspect="clustering",
                  domain_context="...", provider="anthropic")
    │
    ▼
resolve_provider("anthropic") → AnthropicAdapter(model="claude-opus-4-8")
    │
    ▼
ValidateAndRetry(adapter)
    │
    ▼
_system_prompt(task="interpretation", aspect="clustering")
  → base grounding invariant text
  + FDA primer (common)
  + aspect-specific clause (clustering: k-means, amplitude/phase separation, ...)
  + task-family clause (interpretation: explain what result means)
    │
    ▼
provider.complete_structured(
    schema=Advice,
    messages=[{"role": "user", "content": "Domain context: ...\nDiagnostics: {...}"}],
    system=<prompt>,
)
    │
    ├── Anthropic: client.messages.parse(output_format=Advice, ...)
    │   → raw Advice object returned directly (native structured output)
    │
    ├── OpenAI: client.chat.completions.parse(response_format=Advice, ...)
    │   → raw Advice object
    │
    ├── Gemini: client.generate_content(..., generation_config={response_schema: ...})
    │   → json string → json.loads → dict
    │
    └── Ollama: POST /api/chat (format=json, schema injected in prompt)
        → json string → json.loads → dict
    │
    ▼
ValidateAndRetry.validate(raw) → Advice.model_validate(raw)
    ├── success → return Advice
    └── failure → send repair prompt, retry once → Advice or raise ValueError
    │
    ▼
return Advice  ← same schema as v2.0; callers unchanged
```

### build_diagnostics() Call Path (v3.0)

```
build_diagnostics(result, method="depth", argvals=av, ...)
    │
    ▼
method_lc = "depth"
_supported = {"alignment", "fpca", "basis", "smoothing", "clustering",
              "depth", "regression", "monitoring", "classification"}
    │
    ▼
lazy import: from advisor.aspects.depth import build_diagnostics_depth
    │
    ▼
build_diagnostics_depth(raw, argvals=av) → dict  (offline, deterministic)
    │
    ▼
return dict  ← JSON-serialisable, no numpy scalars
```

### MCP Tool Call Path (unchanged for offline tools)

```
fdars_build_diagnostics(dataset_id, method="depth")
    │
    ├── registry.get_dataset(dataset_id) → data, argvals
    ├── build_diagnostics(result, "depth", argvals=argvals)
    └── return diagnostics dict   ← no LLM, no provider, offline
```

---

## Component Boundaries — New vs Modified

### New Components

| Component | File | What It Does |
|-----------|------|-------------|
| `Provider` protocol | `advisor/providers/_protocol.py` | Runtime-checkable protocol; all adapters satisfy it |
| `AnthropicAdapter` | `advisor/providers/anthropic.py` | Lifts inline anthropic call from `advise()`; `supports_native_structured_output = True` |
| `OpenAIAdapter` | `advisor/providers/openai.py` | `openai` SDK; `base_url` support for vLLM/LM Studio; `supports_native_structured_output = True` when `strict=True` |
| `GeminiAdapter` | `advisor/providers/gemini.py` | `google-genai` SDK; structured output where supported, json-mode fallback |
| `OllamaAdapter` | `advisor/providers/ollama.py` | Local `requests.post` to `/api/chat`; json-mode; `supports_native_structured_output = False` |
| `ValidateAndRetry` | `advisor/providers/_validate.py` | Schema-validate + repair-prompt retry; wraps any Provider |
| `resolve_provider()` | `advisor/providers/_factory.py` | Config/env factory returning a `ValidateAndRetry`-wrapped adapter |
| `_base.py` (aspects) | `advisor/aspects/_base.py` | Shared `_safe_float`, `_to_float_list`, `_safe_int` helpers |
| `depth.py` (aspect) | `advisor/aspects/depth.py` | Depth + outlier diagnostics: FM depth scores, outlier flags, median depth, trimmed mean |
| `regression.py` (aspect) | `advisor/aspects/regression.py` | FPCA scores variance, FOSR coefficient norms, PLS component count, prediction residuals |
| `monitoring.py` (aspect) | `advisor/aspects/monitoring.py` | Control chart statistics (UCL/LCL, in-control rate), tolerance coverage, conformal efficiency |
| `classification.py` (aspect) | `advisor/aspects/classification.py` | CV accuracy, class separation, confusion matrix diagonal summary |

### Modified Components

| Component | File | What Changes |
|-----------|------|-------------|
| `advisor.py` → `advisor/__init__.py` | `python/fdars/advisor/__init__.py` | Becomes package init; re-exports same public names; `advise()` gains `provider=` param; `build_diagnostics()` dispatcher gains new aspect strings |
| `_system_prompt()` → `advisor/_prompts.py` | `advisor/_prompts.py` | Gains `aspect` parameter; aspect-specific FDA primer clauses added per new aspect; base invariant text unchanged |
| Aspect builders | `advisor/aspects/{smoothing,basis,alignment,fpca,clustering}.py` | Moved verbatim from `advisor.py`; no logic changes |
| `Advice`, `Recommendation` | `advisor/_schema.py` | Moved from `advisor.py`; schema unchanged |
| `mcp/server.py` | `python/fdars/mcp/server.py` | `_SUPPORTED_METHODS` extended; no structural change |
| `mcp/_runner.py` | `python/fdars/mcp/_runner.py` | `run_method()` dispatch extended to new aspect methods |
| `mcp/_compare.py` | `python/fdars/mcp/_compare.py` | `_ALLOWED_PARAMS` extended for new aspect params |
| `SKILL.md` | `.claude/skills/fdars-advisor/SKILL.md` | Description covers new aspects + provider selection; compatibility adds new extras |
| `__init__.py` | `python/fdars/__init__.py` | No change — `advisor` is already registered via `sys.modules["fdars.advisor"] = advisor` |

---

## Dependency-Ordered Build Sequence

This is the critical output for the roadmapper. Each phase depends on the prior.

**Phase A — Provider Protocol + Anthropic Adapter Refactor** (foundation, no new features)

Dependencies: none beyond existing `advisor.py`.

1. Create `advisor/` package directory with `__init__.py` that re-exports existing public names.
2. Move `Advice` + `Recommendation` pydantic models + fallback stubs to `advisor/_schema.py`.
3. Move `_system_prompt()` to `advisor/_prompts.py`.
4. Create `advisor/providers/_protocol.py` — `Provider` Protocol + `supports_native_structured_output` property.
5. Create `advisor/providers/anthropic.py` — `AnthropicAdapter` wrapping the existing `client.messages.parse()` call extracted from `advise()`.
6. Create `advisor/providers/_validate.py` — `ValidateAndRetry` wrapper.
7. Create `advisor/providers/_factory.py` — `resolve_provider()` returning `ValidateAndRetry(AnthropicAdapter(...))`.
8. Refactor `advise()` in `advisor/__init__.py` to accept `provider: str | Provider | None = None` and call `resolve_provider()`. Default path must be byte-identical to today: `provider=None` → Anthropic adapter → same Claude call.
9. Move existing 5 aspect builders to `advisor/aspects/` verbatim; update dispatcher in `__init__.py`.
10. Tests: all existing advisor tests pass unchanged (offline + env-gated integration). Add adapter-level unit tests with mocks. Add `ValidateAndRetry` repair-path test.

**Phase B — Additional Provider Adapters** (depends on Phase A)

Dependencies: Provider Protocol + ValidateAndRetry must exist.

1. `advisor/providers/openai.py` — OpenAIAdapter with `base_url` support. Mock tests + env-gated real call.
2. `advisor/providers/gemini.py` — GeminiAdapter. Mock tests + env-gated real call.
3. `advisor/providers/ollama.py` — OllamaAdapter (local; uses `requests`). Mock-server test.
4. Extend `_factory.py` to route `"openai"`, `"gemini"`, `"ollama"` strings.
5. Extend `pyproject.toml` optional extras: `[openai]`, `[gemini]`, `[ollama]`.
6. Extend `FDARS_PROVIDER` env var handling in `_factory.py`.

**Phase C — Per-Aspect Diagnostics** (depends on Phase A; parallel to Phase B)

Dependencies: `advisor/aspects/` directory and `_base.py` must exist (from Phase A step 9).

1. `advisor/aspects/_base.py` — shared helpers extracted from existing aspect builders.
2. `advisor/aspects/depth.py` — depth + outlier diagnostics. Offline determinism test.
3. `advisor/aspects/regression.py` — FOSR / PLS / robust regression diagnostics. Offline test.
4. `advisor/aspects/monitoring.py` — SPM / tolerance / conformal diagnostics. Offline test.
5. `advisor/aspects/classification.py` — classification diagnostics. Offline test.
6. Extend `build_diagnostics()` dispatcher in `advisor/__init__.py` with new aspect method strings.
7. Extend `_system_prompt()` in `_prompts.py` with per-aspect FDA primer clauses.
8. Extend `mcp/server.py`, `mcp/_runner.py`, `mcp/_compare.py` with new aspect support.

**Phase D — Surface Updates + Packaging** (depends on B + C)

Dependencies: All adapters and all aspect builders complete.

1. Update `SKILL.md` description + compatibility block.
2. Finalize `pyproject.toml` extras matrix.
3. Update CI to env-gate per-provider integration tests.

**Phase E — Documentation** (depends on D)

Dependencies: Shipped code; existing AI Advisor docs section exists (v2.1).

1. Provider setup page (new): how to configure each provider via env vars / params.
2. Per-aspect advisor pages (one per new aspect, matching the existing clustering/smoothing/fpca pages structure established in v2.1).
3. Update overview page to reference provider selection.

---

## Anti-Patterns

### Anti-Pattern 1: Importing Provider SDKs at Module Level in `advisor/__init__.py`

**What people do:** Add `import anthropic; import openai` at the top of the advisor module to have them ready.

**Why it's wrong:** Breaks the offline guarantee. `import fdars.advisor` must succeed with zero extras installed. The grounding invariant requires that `build_diagnostics` be callable without any LLM SDK.

**Do this instead:** All SDK imports stay inside the adapter files. The adapter file is only imported inside `resolve_provider()`, which is only called from `advise()`. `advise()` is only called by the user explicitly. The offline path (`build_diagnostics` only) never touches adapter files.

### Anti-Pattern 2: Duplicating the Grounding System Prompt Per Aspect

**What people do:** Create `advise_clustering()`, `advise_depth()`, `advise_regression()` functions each with their own inline system prompt.

**Why it's wrong:** The grounding invariant text ("reason only from diagnostics provided", "every evidence item must cite a specific value") must be byte-identical across all aspects. Duplicating it risks drift — a future edit to one copy misses the others, weakening grounding.

**Do this instead:** `_system_prompt(task, aspect)` is the single function that builds all prompts. It always starts with the invariant base. It appends a common FDA primer. It then appends an aspect-specific clause (a few lines describing the relevant FDA concepts for that aspect). `advise()` calls `_system_prompt(task, aspect)` and that is the only call site.

### Anti-Pattern 3: Putting LLM Logic in the MCP Tool Handlers

**What people do:** Call `advise()` inside `fdars_build_diagnostics` or `fdars_run_method`.

**Why it's wrong:** MCP tools are supposed to be deterministic and callable without an API key. Embedding `advise()` in a tool handler breaks the offline guarantee and the by-reference invariant (the tool must not make network calls during normal MCP dispatch).

**Do this instead:** MCP tools remain compute-only. If an agentic flow wants grounded advice, it calls `build_diagnostics` (via MCP tool), then calls `advise()` directly (via Python API) with the returned diagnostics dict. The Skill orchestrates this two-step flow, not the tools.

### Anti-Pattern 4: Embedding Schema JSON in the Repair Prompt

**What people do:** When the repair prompt describes schema errors, they include the full JSON Schema specification of `Advice` in the message to "help" the model fix its output.

**Why it's wrong:** The schema JSON contains no diagnostic values, so including it is harmless from a grounding perspective — but it bloats the context and trains the model to focus on schema rather than the actual diagnostic evidence. The repair prompt should only describe the structural error, not re-introduce the schema.

**Do this instead:** The repair prompt is minimal: `"Your previous response did not conform to the required JSON structure. Errors: {validation_errors}. Return only a valid JSON object matching the schema."` The original user message (which contains the diagnostics) is retained in the conversation history, so the model can re-read the values it needs for evidence.

### Anti-Pattern 5: Flat `advisor.py` with All Aspects Inlined

**What people do:** Add `_build_depth_diagnostics`, `_build_regression_diagnostics`, etc. directly into the existing `advisor.py`, growing it to 2000+ lines.

**Why it's wrong:** Seven new aspect builders added to one file makes the file unnavigable, makes test isolation difficult, and creates a merge-conflict hotspot for parallel development. The 5 existing builders already occupy ~500 lines of the 1161-line `advisor.py`.

**Do this instead:** The refactor to `advisor/aspects/` in Phase A is a prerequisite for Phase C. One file per aspect, one test file per aspect. The public `build_diagnostics()` dispatcher remains the single entry point.

---

## Integration Points

### advisor/ ↔ mcp/ Boundary

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `mcp/server.py` → `advisor` | Direct import of `build_diagnostics`; no `advise()` call in tools | Tools stay LLM-free; grounding is enforced by keeping compute and interpretation separate |
| `mcp/_runner.py` → `fdars.*` | Direct import of fdars submodule functions | Dispatcher extended but pattern unchanged |
| `mcp/_compare.py` → `advisor` | Direct import of `build_diagnostics` | No change to pattern |
| `advisor/providers/` ↔ LLM SDKs | Each adapter file imports its SDK at module load | Import failures are caught in `resolve_provider()`; missing extra → `ImportError` with install hint |

### advisor/ ↔ Python public API

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `fdars/__init__.py` → `advisor/` | `import fdars.advisor` + `sys.modules["fdars.advisor"] = advisor` | No change — advisor package `__init__` re-exports same names; `sys.modules` injection works identically |
| User code → `fdars.advisor.advise()` | Direct call; gains optional `provider=` param | Default (`provider=None`) is Anthropic — backward compatible |
| User code → `fdars.advisor.build_diagnostics()` | Direct call; gains new `method` strings | Existing method strings unchanged; new strings added |

### SKILL.md ↔ Provider Layer

The walkthrough script in `.claude/skills/fdars-advisor/scripts/` uses the Python API only. It gains a `--provider` CLI flag that passes through to `advise()`. No structural change to the skill orchestration — the interpret→recommend→re-run→compare loop is provider-agnostic by construction (it only calls `build_diagnostics` and `advise`).

---

## Scaling Considerations

This is a library, not a networked service. "Scaling" here means adding more aspects and providers without degrading correctness or testability.

| Concern | With 5 aspects (today) | With 9 aspects (v3.0) | With 4 providers |
|---------|----------------------|----------------------|-----------------|
| Offline test coverage | 5 determinism tests | 9 determinism tests (one per aspect) | 4 mock adapter tests + per-provider env-gated |
| Import overhead at `import fdars` | Negligible (no SDK imports) | Negligible (aspects lazy-imported) | Negligible (adapters lazy-imported) |
| System prompt length | ~1KB per task | ~1.5KB per task (aspect clause adds ~200 chars) | Same — provider does not affect prompt |
| Maintenance | One 1161-line file | 9 focused files + package init | 4 adapter files, each ~100 lines |

---

## Sources

- Direct codebase analysis: `python/fdars/advisor.py` (1161 lines), `python/fdars/mcp/server.py`, `mcp/_runner.py`, `mcp/_compare.py`, `mcp/_registry.py`, `python/fdars/__init__.py`, `.claude/skills/fdars-advisor/SKILL.md` (HIGH confidence — primary source)
- `python/fdars/__init__.py` — registration pattern for `sys.modules` injection of `advisor` confirms the package refactor is drop-in compatible (HIGH confidence)
- `advisor.py` lines 940–1007 — existing inline Anthropic call in `advise()` confirms exactly what AnthropicAdapter must encapsulate (HIGH confidence)
- `.planning/PROJECT.md` — v3.0 requirements (provider list, grounding invariant, per-aspect advisor scope) (HIGH confidence)

---

*Architecture research for: fdars v3.0 provider-agnostic advisor + full-library advisor coverage*
*Researched: 2026-08-12*
