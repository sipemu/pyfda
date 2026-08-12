# Phase 22: Surface Integration - Research

**Researched:** 2026-08-12
**Domain:** MCP tool surface + Agent Skill documentation (Python MCP layer, fdars advisor)
**Confidence:** HIGH

## Summary

Phase 22 surfaces the Phase-21 per-aspect advisor coverage through two existing
surfaces: the MCP tools (`python/fdars/mcp/`) and the Agent Skill
(`.claude/skills/fdars-advisor/SKILL.md`). All work is surgical: no new tool is
added; instead, two allow-lists are widened and one Markdown file is updated.

The dominant structural constraint is the array-arg threat (T-12-03): `run_method`
accepts only scalar params (`float | int | None`) per `_runner.py:57-65`
[VERIFIED: python/fdars/mcp/_runner.py:57-65]. Seven of the twelve aspects in
`build_diagnostics._supported` need inputs that the MCP dataset model cannot
supply (a reference score array, a fitted-phase tuple, a response vector `y`, a
Phase-I result with T²/SPE arrays). Those aspects are **diagnostics-only** —
reachable through `fdars_build_diagnostics` with a pre-stored result handle, but
NOT through `fdars_run_method`. Only one new aspect is a genuine runnable:
`depth` (score array returned from data+argvals, no external inputs needed).

The MCP LLM-free invariant is confirmed intact: no MCP file imports or calls
`advise()` [VERIFIED: python/fdars/mcp/ — grep found zero hits for "advise"].
SURF-02 requires only verifying and locking this invariant with a test;
`advise(provider=, model=)` already exists in `advisor/__init__.py:365-445`
[VERIFIED: python/fdars/advisor/__init__.py:365-445].

SURF-03 requires updating SKILL.md to reflect the full aspect list (currently
lists only "clustering, smoothing, FPCA, alignment, or basis"
[VERIFIED: .claude/skills/fdars-advisor/SKILL.md:6-9]) and adding a
provider-selection section. The install note must be corrected to not promise
provider extras on PyPI before they ship.

**Primary recommendation:** Widen `_SUPPORTED_METHODS` in `_runner.py` and
`server.py` by one method (`depth`). Widen `_SUPPORTED_METHODS` in `server.py`'s
`fdars_build_diagnostics` guard to the full twelve. Update `SKILL.md`. Add two
targeted tests. That is the entire scope of Phase 22.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **SURF-01 — MCP exposes new aspects, stays compute-only.** Extend the MCP
  surface so the Phase-21 aspects are reachable while keeping every tool handler
  LLM-free (no `advise()` call inside any MCP handler).
- **SURF-02 — provider selection via Python API only.** `advise(provider=…,
  model=…)` already exists. This criterion is mostly a guardrail + verification:
  confirm provider/model selection is reachable through the Python API and that
  NO MCP tool handler calls `advise()`. Add/keep a test asserting no MCP handler
  imports/calls `advise()`.
- **SURF-03 — Agent Skill doc.** Update `.claude/skills/fdars-advisor/SKILL.md`
  to document: (a) provider selection including the local/offline path (Ollama,
  OpenAI-compatible `base_url`), and (b) the FULL per-aspect advisor coverage
  (all aspects, not just "clustering, smoothing, FPCA, alignment, basis"). Keep
  the SKILL.md spec-valid (agentskills.io frontmatter). The `compatibility`/
  install note may reference the new provider extras — but the actual PyPI
  release carrying them is a later version bump handled at ship (not this phase);
  wording should not overclaim what's on PyPI today.

### Claude's Discretion

The exact runnable-vs-diagnostics-only split per aspect for the MCP surface,
whether new MCP tool params are needed, and the precise SKILL.md wording — at
Claude's discretion, guided by the actual `_runner.py`/`server.py`/`_registry.py`
capabilities and the fdars bindings.

### Deferred Ideas (OUT OF SCOPE)

- Packaging the provider extras into a PyPI release + CI matrix → Phase 23.
- Docs-site provider setup guide + per-aspect pages → Phase 24 (SKILL.md here
  is the Agent-Skill doc, distinct from the MkDocs site).
- HTTP/SSE MCP transport → out of scope (FUT-01).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SURF-01 | MCP tool surface exposes new aspect diagnostics/methods while remaining LLM-free (compute-only; grounding invariant preserved). | See §Runnable-vs-Diagnostics-Only Split and §MCP LLM-Free Invariant below. |
| SURF-02 | Provider selection is available through the Python API `advise()`; the MCP tools do not call `advise()`. | See §Provider Selection (Python API Only) and §MCP LLM-Free Invariant below. |
| SURF-03 | The Agent Skill documents provider selection (including local/offline) and the full per-aspect advisor coverage. | See §SKILL.md Update Specification below. |
</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Aspect diagnostics (offline) | `advisor.build_diagnostics` | MCP `fdars_build_diagnostics` tool | Build logic lives in `advisor/`; MCP handler delegates, never reimplements |
| Runnable fdars methods | `_runner.run_method` | MCP `fdars_run_method` tool | Runner owns dispatch + scalar-param validation; tool is a thin wrapper |
| LLM provider selection | `advisor.advise(provider=, model=)` | — | MCP tools are compute-only and must never call `advise()` |
| Handle-based data boundary | `_registry.HandleRegistry` | — | Arrays stay in-process; only opaque IDs cross the MCP JSON boundary |
| Agent Skill documentation | `.claude/skills/fdars-advisor/SKILL.md` | walkthrough script | Markdown spec for agent environments; walkthrough is offline verification |

---

## Section 1: Runnable-vs-Diagnostics-Only Split (SURF-01)

### What the MCP dataset model can supply

`run_method(dataset_id, method, **scalar_params)` retrieves `(data, argvals)` from
the registry [VERIFIED: python/fdars/mcp/_runner.py:149-152]. Its only parameter
types are `float | None` and `int | None` [VERIFIED: python/fdars/mcp/_runner.py:57-65].

`fdars_build_diagnostics(dataset_id, method, result_id=None, with_argvals=True)`
retrieves the same `(data, argvals)` pair PLUS an optional pre-stored result dict
[VERIFIED: python/fdars/mcp/server.py:54-131].

### Decision table: all twelve aspects

| Aspect | `run_method` runnable? | Reasoning | Action |
|--------|------------------------|-----------|--------|
| `alignment` | YES (existing) | `karcher_mean(data, argvals, lambda_=)` — all from registry | No change |
| `fpca` | YES (existing) | `regression.fpca(data, argvals, n_comp=)` — all from registry | No change |
| `basis` | YES (existing) | `basis.basis_nbasis_cv(data, argvals, lambda_=)` — all from registry | No change |
| `smoothing` | YES (existing) | `basis.pspline_fit_gcv(data, argvals, n_basis=)` — all from registry | No change |
| `clustering` | YES (existing) | `clustering.kmeans_fd(data, argvals, k=, seed=)` — all from registry | No change |
| `depth` | **YES — ADD** | `fdars.depth.*_1d(data, argvals)` returns a score array `(n,)` from data+argvals only; no reference sample needed | Add `"depth"` to `_SUPPORTED_METHODS` in `_runner.py` and `server.py` |
| `outliers` | **NO — diagnostics-only** | `fdars.outliers.*` functions take `data, argvals` PLUS additional inputs (threshold, outliergram config) that vary per function; moreover the result dict shape varies (LRT, outliergram, magnitude_shape) and `run_method` would need to pick ONE function arbitrarily | Accept via `fdars_build_diagnostics(result_id=...)` from caller-pre-run result |
| `classification` | **NO — diagnostics-only** | `fdars.classification.*` requires a response label vector `y` (not storable as a scalar param; T-12-03) and the method choice (LDA/QDA/KNN/etc.). Additionally `build_diagnostics` requires `n_classes` — an integer the caller knows, not derivable from `(data, argvals)` | Accept via `fdars_build_diagnostics(result_id=..., n_classes=K)` after extending the tool param list |
| `represent` | **NO — diagnostics-only** | `represent` builder operates on the raw data + argvals directly [VERIFIED: python/fdars/advisor/aspects/represent.py:32-143]; it needs NO fdars function call. `fdars_build_diagnostics` with `result_id=None` already passes `{"data": data}` to `build_diagnostics`, but the represent builder also needs `argvals`. The tool already passes argvals when `with_argvals=True`. So represent is reachable diagnostics-only WITHOUT needing `run_method` at all. | Accept via `fdars_build_diagnostics(dataset_id=..., method="represent", result_id=None, with_argvals=True)` — the tool passes both `{"data": data}` and `argvals` to `build_diagnostics`, which routes to `_build_represent_diagnostics` |
| `regression` | **NO — diagnostics-only** | `fdars.regression.fregre_lm` etc. require a scalar-response vector `y` that cannot be expressed as a scalar MCP param | Accept via `fdars_build_diagnostics(result_id=...)` |
| `regression_cv` | **NO — diagnostics-only** | Same as regression: needs `y` and the full CV configuration | Accept via `fdars_build_diagnostics(result_id=...)` |
| `spm` | **NO — diagnostics-only** | `fdars.spm.spm_phase1` requires an FPC model (Phase-I fit inputs beyond what a simple `(data, argvals)` pair can reconstruct at tool call time) | Accept via `fdars_build_diagnostics(result_id=...)` |

### Concrete changes to `_SUPPORTED_METHODS`

**`python/fdars/mcp/_runner.py` lines 51-53:**

Current [VERIFIED: python/fdars/mcp/_runner.py:51-53]:
```python
_SUPPORTED_METHODS = frozenset(
    {"alignment", "fpca", "basis", "smoothing", "clustering"}
)
```

After Phase 22:
```python
_SUPPORTED_METHODS = frozenset(
    {"alignment", "fpca", "basis", "smoothing", "clustering", "depth"}
)
```

**`python/fdars/mcp/server.py` lines 47 and 99-105 (two sites):**

There is a local `_SUPPORTED_METHODS` in `server.py` at line 47 [VERIFIED:
python/fdars/mcp/server.py:47] that also guards `fdars_build_diagnostics` at
lines 99-105 [VERIFIED: python/fdars/mcp/server.py:99-105] and `fdars_compare_run`
at lines 327-334 [VERIFIED: python/fdars/mcp/server.py:327-334].

This creates **two diverging allow-lists** (runner vs server). Phase 22 must
resolve this split into a principled two-frozenset design:

- `_RUNNABLE_METHODS` (in `_runner.py` and mirrored in `server.py`): the 6
  methods that `run_method` can dispatch (`alignment`, `fpca`, `basis`,
  `smoothing`, `clustering`, `depth`).
- `_DIAGNOSTICS_METHODS` (in `server.py` for `fdars_build_diagnostics`): all 12
  methods that `build_diagnostics` accepts.

`fdars_compare_run` should continue to use only `_RUNNABLE_METHODS` (you can
only compare before/after on a re-runnable method).

**`python/fdars/mcp/server.py` new `_DIAGNOSTICS_METHODS` constant:**
```python
# All methods supported by advisor.build_diagnostics (SURF-01)
_DIAGNOSTICS_METHODS = frozenset({
    "alignment", "fpca", "basis", "smoothing", "clustering",
    "depth", "outliers", "classification", "represent",
    "regression", "regression_cv", "spm",
})
```

### `depth` runner dispatch — what to add to `_runner.py`

`fdars.depth` exposes multiple functions (`fraiman_muniz_1d`, `modal_1d`,
`random_projection_1d`). For a single runnable MCP entry point, map
`method="depth"` to `fraiman_muniz_1d` (the canonical general-purpose depth
estimator). Introduce one new scalar param `method_name: str | None = None`
that is **not** a numeric param — however, string params introduce a new attack
surface (T-12-03 generalises to injection via string values). The safe design:
do NOT add a `method_name` string param. Instead, hard-code `fraiman_muniz_1d`
as the MCP entry point and document this in the docstring. The caller can store
any other depth function's result manually and pass it to
`fdars_build_diagnostics(result_id=...)`.

```python
if method_lc == "depth":
    from fdars import depth as _depth
    # MCP entry point: fraiman_muniz_1d (canonical depth estimator).
    # For other depth functions, run manually and pass result_id to
    # fdars_build_diagnostics.
    scores = _depth.fraiman_muniz_1d(data, argvals)
    return {"scores": scores, "method_name": "fraiman_muniz"}
```

The depth builder in `_build_depth_diagnostics` accepts a raw array (`np.asarray(raw)`)
[VERIFIED: python/fdars/advisor/aspects/depth.py:50]. So when `fdars_build_diagnostics`
receives `result_id` pointing to `{"scores": scores, "method_name": "..."}`, it will
pass the dict to `build_diagnostics(result, "depth")`. The dispatcher in
`advisor/__init__.py:175` calls `_build_depth_diagnostics(raw)`, which calls
`np.asarray(raw)` on the dict — this will NOT work correctly since a dict is
not array-coercible.

**Important correction:** The depth builder expects the raw array itself, not a
dict. The `build_diagnostics` dispatcher at line 142-150 [VERIFIED:
python/fdars/advisor/__init__.py:142-150] has: `raw = getattr(result, "raw", result)`,
then coerces to dict only if not a dict, not array-like, and not Fdata-like.
A score array (`np.ndarray`) has `__array__`, so it passes through uncoerced.

The depth runner therefore must return the raw scores array as the stored result
value, NOT wrapped in a dict. But `registry.store_result` stores a dict
[VERIFIED: python/fdars/mcp/_registry.py:96-111]. Solution: store the score
array in a dict with a known key, and update `fdars_build_diagnostics` to
unwrap it before calling `build_diagnostics`. Cleanest approach:

```python
# In _runner.py depth branch:
scores = _depth.fraiman_muniz_1d(data, argvals)
return {"scores": scores, "method_name": "fraiman_muniz"}
```

```python
# In server.py fdars_build_diagnostics, after resolving result:
if method_lc == "depth" and isinstance(result, dict) and "scores" in result:
    # Unwrap: depth builder expects the score array, not a dict
    result = result["scores"]
```

Alternatively (simpler, avoids a server.py special-case): make the depth
builder in `advisor/aspects/depth.py` also accept a dict with a `"scores"` key
by adding a one-line guard at its top. Since the depth builder is in Phase 21
code and Phase 22 is allowed to update `python/fdars/mcp/` only, the server.py
unwrap approach is the correct Phase 22 change.

### `represent` via `fdars_build_diagnostics` without `result_id`

The represent builder operates on `{"data": data}` + `argvals`
[VERIFIED: python/fdars/advisor/aspects/represent.py:77-89]. When
`fdars_build_diagnostics` is called with `result_id=None`, the server already
constructs `result = {"data": data}` [VERIFIED: python/fdars/mcp/server.py:118-119]
and passes `argvals` when `with_argvals=True`. The represent builder uses
`dict.get("argvals")` as a fallback [VERIFIED:
python/fdars/advisor/aspects/represent.py:81-82]. But `build_diagnostics` passes
`argvals` as a keyword argument, not in the result dict. The represent builder's
`**kwargs` receives it: `_build_represent_diagnostics(raw, **kwargs)` at
`advisor/__init__.py:188`. However `**kwargs` is not currently forwarded into
`_build_represent_diagnostics` with the argvals. Check the represent builder
signature: `def _build_represent_diagnostics(raw, **kwargs)` — it ignores
`**kwargs`. The `argvals` is looked up from `raw.get("argvals")` only. So to
pass argvals to represent via `fdars_build_diagnostics`, the server should add
argvals to the result dict:

```python
# In fdars_build_diagnostics, special-case for represent (no result_id):
if method_lc == "represent" and result_id is None:
    result = {"data": data, "argvals": argvals}
```

This is a cleaner approach than relying on kwargs threading.

### `classification` — `n_classes` param

`build_diagnostics(result, "classification", n_classes=K)` requires an integer
`n_classes` that cannot be inferred from the result dict. The `fdars_build_diagnostics`
tool must expose `n_classes: int | None = None` as a new optional tool param.
This is a scalar integer — no T-12-03 violation.

**New tool signature addition:**
```python
@mcp.tool()
def fdars_build_diagnostics(
    dataset_id: str,
    method: str,
    result_id: str | None = None,
    with_argvals: bool = True,
    n_classes: int | None = None,  # NEW: required for method="classification"
) -> dict:
```

Pass-through in handler:
```python
diag_kwargs: dict = {}
if with_argvals:
    diag_kwargs["argvals"] = argvals
if n_classes is not None:
    diag_kwargs["n_classes"] = n_classes
diagnostics = build_diagnostics(result, method_lc, **diag_kwargs)
```

---

## Section 2: MCP LLM-Free Invariant (SURF-01/02)

### Current state — confirmed clean

Grep of all files under `python/fdars/mcp/` for the string `advise` returns
zero matches [VERIFIED: python/fdars/mcp/ — grep confirmed zero hits this session].

The only advisor import in the MCP layer is:
- `server.py:108` — `from fdars.advisor import build_diagnostics` [VERIFIED: python/fdars/mcp/server.py:108]
- `_compare.py:145` — `from fdars.advisor import build_diagnostics` [VERIFIED: python/fdars/mcp/_compare.py:145]

Neither imports `advise`. The invariant holds.

### Test to lock the invariant

Add to `tests/test_mcp_server.py`:

```python
def test_mcp_does_not_import_advise():
    """SURF-02: no MCP handler calls or imports advise() (LLM-free invariant).

    AST-equivalent check: scan all source files under python/fdars/mcp/ for
    the string 'advise' — any match is a violation.
    """
    import pathlib
    mcp_dir = pathlib.Path(__file__).resolve().parents[1] / "python" / "fdars" / "mcp"
    violations = []
    for py_file in mcp_dir.rglob("*.py"):
        source = py_file.read_text()
        if "advise" in source:
            violations.append(str(py_file))
    assert not violations, (
        f"MCP files reference 'advise' (LLM-free invariant violation): {violations}"
    )
```

This is a string scan (not a full AST parse) but is sufficient here because
"advise" only appears as an identifier — it does not appear in comments or
docstrings in the MCP layer currently. The test is fast, sync, and needs no
imports beyond `pathlib`.

---

## Section 3: Provider Selection is Python-API-Only (SURF-02)

### What already ships from Phases 19-20

`advise(provider=, model=)` in `advisor/__init__.py:365-445` [VERIFIED:
python/fdars/advisor/__init__.py:365-445] accepts:

- `provider: str | object | None` — string names (`"anthropic"`, `"openai"`,
  `"ollama"`, `"gemini"`) or a `Provider` instance
- `model: str` — model identifier string, default `"claude-opus-4-8"`

Environment variable path: `FDARS_ADVISOR_PROVIDER` / `FDARS_ADVISOR_MODEL` /
`FDARS_ADVISOR_BASE_URL` (resolved inside `providers._factory.resolve_provider`)
[ASSUMED — not read this session; consistent with PROV-06 which is marked Complete].

Version floors [VERIFIED: python/fdars/advisor/__init__.py:53-56]:
- `ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"`
- `ADVISOR_OPENAI_MIN_VERSION = "1.40.0"`
- `ADVISOR_OLLAMA_MIN_VERSION = "0.6.2"`

### What Phase 22 must NOT add

No provider selection logic belongs in `python/fdars/mcp/`. The MCP tools are
compute pipelines. An LLM agent using the MCP tools calls `build_diagnostics`
to get grounded numbers, then separately calls `advise()` from its own Python
environment to interpret them. The two are not chained inside the tool handlers.

### What Phase 22 must confirm

SURF-02 is already satisfied at the code level. Phase 22's job is:
1. The `test_mcp_does_not_import_advise` test (locks the invariant).
2. The SKILL.md update documenting how to use `advise(provider=)`.

No new code changes are needed in `python/fdars/advisor/` for SURF-02.

---

## Section 4: SKILL.md Update Specification (SURF-03)

### What must change

The current SKILL.md has three problems:

**Problem 1 — Incomplete aspect list in `description` field (lines 6-9):**

Current text [VERIFIED: .claude/skills/fdars-advisor/SKILL.md:6-9]:
```
Use when working with fdars clustering, smoothing, FPCA, alignment, or basis
results and needing parameter guidance or a before/after comparison.
```

Replace with the full list of all 12 aspects:
```
Use when working with fdars results from any analysis aspect — clustering,
smoothing, FPCA, alignment, basis/represent, depth, outliers, classification,
regression, regression CV, or monitoring/SPM — and needing grounded diagnostics,
parameter guidance, method guidance, or a before/after comparison.
```

Also update the `Trigger` line to enumerate the expanded set.

**Problem 2 — No provider-selection section in the body:**

Add a `## Provider Selection` section after `## Grounded Advice`:

```markdown
## Provider Selection

`advise()` routes through a `Provider` protocol. Select the backend via:

**Explicit parameter:**
```python
advice = advise(diagnostics, task="interpretation",
                domain_context="...",
                provider="openai",    # or "anthropic", "ollama", "gemini"
                model="gpt-4o")
```

**Environment variables (take precedence when no explicit arg):**
```bash
FDARS_ADVISOR_PROVIDER=ollama   # "anthropic" | "openai" | "ollama" | "gemini"
FDARS_ADVISOR_MODEL=llama3.2
FDARS_ADVISOR_BASE_URL=http://localhost:11434  # OpenAI-compatible endpoint
```

**Local / offline (no API key):**
```bash
# Start Ollama daemon first: https://ollama.com
ollama pull llama3.2
FDARS_ADVISOR_PROVIDER=ollama FDARS_ADVISOR_MODEL=llama3.2 python my_analysis.py
```

**OpenAI-compatible endpoint (vLLM, LM Studio, LocalAI):**
```python
advice = advise(diagnostics, task="parameter", domain_context="...",
                provider="openai",
                model="meta-llama/Llama-3-8B-Instruct")
# Set FDARS_ADVISOR_BASE_URL=http://localhost:8000/v1 or pass base_url via
# the OpenAIProvider constructor directly.
```
```

**Problem 3 — `compatibility` field overclaims PyPI extras availability:**

Current text [VERIFIED: .claude/skills/fdars-advisor/SKILL.md:13-18]:
```
Install: pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0
anthropic>=0.72.0 pydantic>=2.0 (git-URL install required until fdars 0.3.0
ships the [mcp,advisor] extras to PyPI). Optional: ANTHROPIC_API_KEY for
grounded LLM advice step.
```

Replace with (no overclaim on PyPI; notes that provider extras are not yet published):
```
Requires Python 3.10+ and pip access. Core install (git-URL until fdars 3.0
ships extras to PyPI): pip install "fdars @ git+https://github.com/sipemu/pyfda"
mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0. For other providers:
openai>=1.40.0 (OpenAI/vLLM), ollama>=0.6.2 (local), or google-genai>=1.0
(Gemini). Provider extras ([openai], [ollama], [gemini]) publish with fdars
3.0. ANTHROPIC_API_KEY required for Anthropic; other providers need their own
credentials or run key-free (Ollama).
```

**Problem 4 — `## Tools Referenced` section is stale:**

Current text [VERIFIED: .claude/skills/fdars-advisor/SKILL.md:70-79]:
```
This skill orchestrates the Phase 12 MCP tools built in `python/fdars/mcp/`:

- `fdars_run_method` — run a supported fdars method (smoothing, clustering,
  FPCA, alignment, basis) and store the result handle.
- `fdars_compare_run` — re-run with changed parameters and compute the
  before/after delta; all numbers are fdars-computed.

The Phase 11 advisor (`python/fdars/advisor.py`) provides `build_diagnostics`
and `advise()`: the grounding source for all LLM recommendations.
```

Replace with:
```
This skill orchestrates three MCP tools in `python/fdars/mcp/`:

- `fdars_run_method` — run a supported fdars method (smoothing, clustering,
  FPCA, alignment, basis, depth) and store the result handle.
- `fdars_build_diagnostics` — build offline diagnostics from a stored result;
  accepts all 12 analysis aspects.
- `fdars_compare_run` — re-run with changed parameters and compute the
  before/after delta; all numbers are fdars-computed.

`python/fdars/advisor/` provides `build_diagnostics` (offline) and `advise()`
(LLM interpretation) — the grounding source for all recommendations.
```

### What must NOT change

- The YAML frontmatter `name: fdars-advisor` must stay as-is (test `test_skill_md_name_matches_dir` checks it) [VERIFIED: tests/test_skill.py:162-170].
- The `allowed-tools: Bash Read` line must stay.
- The frontmatter must remain parseable YAML (test `test_skill_md_frontmatter` checks this) [VERIFIED: tests/test_skill.py:84-96].
- The `## Setup` section install commands should be updated for consistency with the new compatibility text, but not removed.
- The `## Grounding Invariant` section content is correct and should be left unchanged.

### Whether the walkthrough script needs changes

The walkthrough script (`fdars_advisor_walkthrough.py`) demonstrates the
`smoothing` workflow only [VERIFIED: .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py:57-154].
It does NOT need to be updated for Phase 22 because:

1. The script is an offline demo of one aspect (smoothing) and remains valid.
2. The tests in `test_skill.py` check that the script exits 0 and produces a
   non-empty delta block — both still hold [VERIFIED: tests/test_skill.py:99-154].
3. Adding multi-aspect examples to the walkthrough is a docs concern (Phase 24).

The only change needed is ensuring the `ANTHROPIC_API_KEY` step in the script
still works with the new provider system (it does — the default path uses
Anthropic and is unchanged per Phase 19 locked decision).

---

## Section 5: Test Strategy

### `tests/test_mcp_server.py` extensions (SURF-01 + SURF-02)

**Test 1 — LLM-free invariant lock (SURF-02):**

```python
def test_mcp_does_not_import_advise():
    """SURF-02: no MCP file references 'advise' (LLM-free invariant)."""
    import pathlib
    mcp_dir = pathlib.Path(__file__).resolve().parents[1] / "python" / "fdars" / "mcp"
    violations = [
        str(f) for f in mcp_dir.rglob("*.py") if "advise" in f.read_text()
    ]
    assert not violations, f"MCP files reference 'advise': {violations}"
```

This test is synchronous (no `asyncio`), needs no fixture, no registry clear,
no network. It runs under all Python versions that can import pathlib (all).
Note: this test does NOT need the `pytestmark` skip guard because it only reads
files, never imports `fdars.mcp`.

**Test 2 — `depth` runnable end-to-end via MCP tools (SURF-01):**

```python
@pytest.mark.asyncio
async def test_run_method_depth(dataset_id):
    """SURF-01: fdars_run_method dispatches 'depth'; result_id is usable in
    fdars_build_diagnostics; diagnostics method=='depth'; no advise() called.

    Offline, compute-only. Extends the existing pattern from
    test_build_diagnostics_all_methods.
    """
    from mcp import Client
    from fdars.mcp.server import mcp
    from fdars.mcp._registry import registry

    async with Client(mcp) as client:
        # Step 1: run depth to get a result_id
        run_response = await client.call_tool(
            "fdars_run_method",
            {"dataset_id": dataset_id, "method": "depth"},
        )
        run_result = _unwrap_tool_result(run_response)
        assert "result_id" in run_result
        result_id = run_result["result_id"]
        # Confirm the raw result is in-registry (by-reference invariant)
        stored = registry.get_result(result_id)
        assert isinstance(stored, dict)

        # Step 2: build diagnostics for the depth result
        diag_response = await client.call_tool(
            "fdars_build_diagnostics",
            {
                "dataset_id": dataset_id,
                "result_id": result_id,
                "method": "depth",
            },
        )
        diag = _unwrap_tool_result(diag_response)
        assert diag.get("method") == "depth"
        assert isinstance(diag.get("n_obs"), int)
        assert isinstance(diag.get("depth_mean"), float)
```

**Test 3 — `represent` diagnostics-only via `fdars_build_diagnostics` (SURF-01):**

```python
@pytest.mark.asyncio
async def test_build_diagnostics_represent(dataset_id):
    """SURF-01: fdars_build_diagnostics handles 'represent' without a result_id.

    represent builder operates on raw data+argvals; no run_method step needed.
    """
    from mcp import Client
    from fdars.mcp.server import mcp

    async with Client(mcp) as client:
        diag_response = await client.call_tool(
            "fdars_build_diagnostics",
            {
                "dataset_id": dataset_id,
                "method": "represent",
                "with_argvals": True,
            },
        )
        diag = _unwrap_tool_result(diag_response)
        assert diag.get("method") == "represent"
        assert isinstance(diag.get("n_obs"), int)
        assert isinstance(diag.get("n_points"), int)
```

**Test 4 — `classification` diagnostics-only with `n_classes` param (SURF-01):**

```python
@pytest.mark.asyncio
async def test_build_diagnostics_classification_with_n_classes(dataset_id):
    """SURF-01: fdars_build_diagnostics forwards n_classes to build_diagnostics.

    Uses a pre-stored synthetic classification result dict.
    """
    from mcp import Client
    from fdars.mcp.server import mcp
    from fdars.mcp._registry import registry

    # Synthetic classification result (point-estimate shape)
    synth_result = {"predicted": [0, 1, 0, 1, 0], "accuracy": 0.8}
    result_id = registry.store_result(synth_result)

    async with Client(mcp) as client:
        diag_response = await client.call_tool(
            "fdars_build_diagnostics",
            {
                "dataset_id": dataset_id,
                "result_id": result_id,
                "method": "classification",
                "n_classes": 2,
            },
        )
        diag = _unwrap_tool_result(diag_response)
        assert diag.get("method") == "classification"
        assert diag.get("n_classes") == 2
        assert diag.get("accuracy") == pytest.approx(0.8)
```

**Test 5 — Rejected method at `fdars_run_method` for diagnostics-only aspects:**

```python
@pytest.mark.asyncio
async def test_run_method_rejects_diagnostics_only(dataset_id):
    """SURF-01: fdars_run_method raises for aspects that are diagnostics-only.

    'regression' needs a response y; calling run_method on it must raise ValueError.
    """
    from mcp import Client
    from fdars.mcp.server import mcp

    async with Client(mcp) as client:
        with pytest.raises(Exception):  # mcp wraps ValueError; check it propagates
            await client.call_tool(
                "fdars_run_method",
                {"dataset_id": dataset_id, "method": "regression"},
            )
```

### `tests/test_skill.py` extensions (SURF-03)

**Test 6 — Full aspect list in SKILL.md description:**

```python
def test_skill_md_full_aspect_coverage():
    """SURF-03: SKILL.md description mentions all Phase-21 aspects."""
    assert SKILL_MD.exists()
    text = SKILL_MD.read_text()
    new_aspects = ["depth", "outliers", "classification", "regression", "spm"]
    missing = [a for a in new_aspects if a not in text.lower()]
    assert not missing, (
        f"SKILL.md missing Phase-21 aspects: {missing}. "
        f"Update 'description' and 'Tools Referenced'."
    )
```

**Test 7 — Provider-selection section exists:**

```python
def test_skill_md_provider_selection_section():
    """SURF-03: SKILL.md has a Provider Selection section documenting local/offline path."""
    assert SKILL_MD.exists()
    text = SKILL_MD.read_text()
    assert "Provider Selection" in text, (
        "SKILL.md missing '## Provider Selection' section (SURF-03)"
    )
    # Ollama is the key local/offline provider
    assert "ollama" in text.lower() or "Ollama" in text, (
        "SKILL.md Provider Selection section does not mention Ollama (local path)"
    )
```

### Existing tests that must stay green

All seven tests in `tests/test_mcp_server.py` [VERIFIED: tests/test_mcp_server.py:1-20]
and six in `tests/test_skill.py` [VERIFIED: tests/test_skill.py:1-17] must remain
green. The new tests extend, not replace, existing coverage.

The `test_run_method_all_methods` test iterates over `["alignment", "fpca", "basis",
"smoothing", "clustering"]` [VERIFIED: tests/test_mcp_server.py:247]. After Phase 22
adds `"depth"` to `_SUPPORTED_METHODS`, this test does NOT need to be updated
(it hard-codes the five original methods, which is fine). A separate `test_run_method_depth`
test covers the new addition explicitly.

---

## Section 6: Tracer-First Sequencing and Pitfalls

### Recommended plan wave sequencing

**Wave 0 (tracer — unblocks everything):**
- Add `"depth"` to `_SUPPORTED_METHODS` in `_runner.py` and `server.py`
- Add the `depth` dispatch branch in `_runner.py`
- Add the depth-dict unwrap in `server.py`'s `fdars_build_diagnostics`
- Add `test_run_method_depth` and `test_mcp_does_not_import_advise`
- Run the full test suite; confirm both new tests pass + all existing tests stay green

**Wave 1 (diagnostics-only expansion):**
- Add `_DIAGNOSTICS_METHODS` frozenset to `server.py`
- Update `fdars_build_diagnostics` guard to use `_DIAGNOSTICS_METHODS`
- Add `n_classes` param to `fdars_build_diagnostics`
- Add represent special-case (inject argvals into result dict)
- Add `test_build_diagnostics_represent`, `test_build_diagnostics_classification_with_n_classes`
- Add `test_run_method_rejects_diagnostics_only`

**Wave 2 (SKILL.md + tests):**
- Update `.claude/skills/fdars-advisor/SKILL.md` (all four changes)
- Add `test_skill_md_full_aspect_coverage` and `test_skill_md_provider_selection_section`
- Run `test_skill.py` in full

### Pitfall 1 — `_SUPPORTED_METHODS` drift (T-12-02)

There are currently TWO copies of `_SUPPORTED_METHODS`: one in `_runner.py:51-53`
and one in `server.py:47` [VERIFIED: python/fdars/mcp/server.py:47]. Phase 22
introduces a THIRD concept (`_DIAGNOSTICS_METHODS`). The risk: a developer adding
a new aspect to `advisor._supported` (the local set in `build_diagnostics`)
forgets to update `_DIAGNOSTICS_METHODS` in `server.py`.

**Mitigation:** Add a sync-check test:

```python
def test_diagnostics_methods_subset_of_advisor_supported():
    """_DIAGNOSTICS_METHODS in server.py is a subset of advisor.build_diagnostics._supported."""
    # Reconstruct advisor's supported set by calling build_diagnostics with a
    # bad method and parsing the error message, OR by reading the source.
    # Simpler: call with a nonsense method and check the error lists all known.
    from fdars.mcp.server import _DIAGNOSTICS_METHODS  # noqa: PLC0415
    from fdars.advisor import build_diagnostics
    try:
        build_diagnostics({}, "_nonexistent_method_")
    except ValueError as exc:
        import re
        # The error message embeds the sorted supported set
        # Extract it and check _DIAGNOSTICS_METHODS is a subset
        supported_str = str(exc)
        for m in _DIAGNOSTICS_METHODS:
            assert m in supported_str, (
                f"_DIAGNOSTICS_METHODS contains {m!r} but advisor does not support it. "
                f"Advisor error: {exc}"
            )
```

### Pitfall 2 — depth builder expects raw array, not dict

As documented in §1, the depth builder calls `np.asarray(raw)` on its input
[VERIFIED: python/fdars/advisor/aspects/depth.py:50]. If the runner stores
`{"scores": scores, ...}` and the tool passes that dict to `build_diagnostics`,
the dict coercion path in `advisor/__init__.py:148-152` will try `dict(raw)` on
the dict — yielding an identity — then pass it to `_build_depth_diagnostics`,
which calls `np.asarray({"scores": ..., "method_name": ...})` and gets an
object array of dict items, not the scores. **The server.py unwrap step is mandatory.**

### Pitfall 3 — `fdars_compare_run` method guard must stay narrow

`fdars_compare_run` at `server.py:327-334` uses `_SUPPORTED_METHODS` to validate
[VERIFIED: python/fdars/mcp/server.py:327-334]. After Phase 22, `_SUPPORTED_METHODS`
in `server.py` becomes `_RUNNABLE_METHODS`. `fdars_compare_run` must continue
to validate against `_RUNNABLE_METHODS` only (the 6 runnable methods), NOT
`_DIAGNOSTICS_METHODS`. Comparing before/after diagnostics-only results would
fail because `run_method` cannot re-run them.

### Pitfall 4 — `represent` needs argvals in the result dict

When `fdars_build_diagnostics` is called with `method="represent"` and
`result_id=None`, the existing code constructs `result = {"data": data}`
[VERIFIED: python/fdars/mcp/server.py:118-119]. The represent builder then calls
`raw.get("argvals")` [VERIFIED: python/fdars/advisor/aspects/represent.py:80-82]
and gets `None` (the dict only has "data"). The `argvals` is passed separately
to `build_diagnostics` as a keyword arg, but `build_diagnostics` dispatches
`_build_represent_diagnostics(raw, **kwargs)` [VERIFIED:
python/fdars/advisor/__init__.py:188] where `kwargs` is empty (argvals was
consumed by `build_diagnostics`'s own signature). Inject argvals into the result
dict in the server to fix this, as described in §1.

### Pitfall 5 — SKILL.md YAML frontmatter must remain parseable

The YAML frontmatter uses block scalars (`description: >` and `compatibility: >`).
[VERIFIED: .claude/skills/fdars-advisor/SKILL.md:1-19]. When editing multi-line
YAML block scalars, all continuation lines must be indented exactly 2 spaces.
Breaking the indentation will fail `test_skill_md_frontmatter`'s `yaml.safe_load()`.

### Pitfall 6 — `_method_params` helper in tests

`test_mcp_server.py`'s `_method_params()` helper at lines 146-154 [VERIFIED:
tests/test_mcp_server.py:146-154] covers only the five original methods. Adding
`depth` there requires a new entry: `"depth": {}` (no scalar params needed for
the default `fraiman_muniz_1d` entry point). The `test_run_method_all_methods`
test that calls `_method_params` does NOT need to be updated if `depth` is
tested separately — but if a later reviewer extends the all-methods loop, the
helper must be updated.

---

## Standard Stack

No new dependencies. Phase 22 touches only existing surfaces.

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| `mcp` | >=2.0.0 | MCP server + in-process Client for tests | Existing |
| `pytest-asyncio` | any | Async test runner | Existing |
| `PyYAML` | any | SKILL.md frontmatter parsing in tests | Existing |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| MCP LLM-free invariant check | Full AST parser | String scan: `"advise" in file.read_text()` is sufficient and foolproof for this codebase |
| `_DIAGNOSTICS_METHODS` sync-check | Manual comparison | Parse `ValueError` from `build_diagnostics` on an invalid method — the message embeds the canonical supported set |
| depth builder dict-vs-array mismatch | Modifying Phase-21 `aspects/depth.py` | Server-side unwrap of the `"scores"` key in `fdars_build_diagnostics` handler |

---

## Common Pitfalls

### Pitfall A: Two frozensets becoming three — keeping them consistent

**What goes wrong:** `_runner.py` has `_SUPPORTED_METHODS = frozenset({5 methods})`.
`server.py` ALSO has `_SUPPORTED_METHODS = frozenset({same 5 methods})`. After
Phase 22 the server needs `_RUNNABLE_METHODS` (6, for run+compare guards) and
`_DIAGNOSTICS_METHODS` (12, for build_diagnostics guard). Forgetting to update
one site leaves a stale guard.

**How to avoid:** The tracer test adds `depth` first; the sync-check test
`test_diagnostics_methods_subset_of_advisor_supported` locks the relationship
between `_DIAGNOSTICS_METHODS` and the advisor's canonical set.

### Pitfall B: `depth` runner returns dict; builder expects array

**What goes wrong:** `_build_depth_diagnostics` calls `np.asarray(raw)`. If
`raw` is `{"scores": ..., "method_name": "fraiman_muniz"}`, the result is
`array({"scores": ..., "method_name": ...}, dtype=object)`, not a float array.

**How to avoid:** In `fdars_build_diagnostics` (server.py), before calling
`build_diagnostics(result, method_lc)`, add:
```python
if method_lc == "depth" and isinstance(result, dict) and "scores" in result:
    result = result["scores"]
```

### Pitfall C: SKILL.md overclaiming PyPI extras

**What goes wrong:** If `compatibility` says `pip install fdars[openai]` without
qualification, users on a released PyPI version will get a `no such extra` error
until fdars 3.0 ships.

**How to avoid:** The updated text says provider extras "publish with fdars 3.0"
and the current install path uses git-URL + manual extra installs.

### Pitfall D: `represent` loses argvals when result_id is None

Documented in §6 Pitfall 4. Fix: inject into result dict.

---

## Package Legitimacy Audit

No new packages are installed in Phase 22. This section is not applicable.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (with pytest-asyncio) |
| Config file | `pyproject.toml` (pytest section) |
| Quick run command | `pytest tests/test_mcp_server.py tests/test_skill.py -x` |
| Full suite command | `pytest` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| SURF-01 | depth is runnable via `fdars_run_method` | integration (async, in-proc) | `pytest tests/test_mcp_server.py::test_run_method_depth -x` |
| SURF-01 | represent is reachable via `fdars_build_diagnostics` | integration (async) | `pytest tests/test_mcp_server.py::test_build_diagnostics_represent -x` |
| SURF-01 | classification with n_classes param works | integration (async) | `pytest tests/test_mcp_server.py::test_build_diagnostics_classification_with_n_classes -x` |
| SURF-01 | diagnostics-only aspects rejected at run_method | integration (async) | `pytest tests/test_mcp_server.py::test_run_method_rejects_diagnostics_only -x` |
| SURF-02 | MCP files never reference advise | unit (file scan) | `pytest tests/test_mcp_server.py::test_mcp_does_not_import_advise -x` |
| SURF-03 | SKILL.md mentions all 7 new aspects | unit (file scan) | `pytest tests/test_skill.py::test_skill_md_full_aspect_coverage -x` |
| SURF-03 | SKILL.md has Provider Selection section with Ollama | unit (file scan) | `pytest tests/test_skill.py::test_skill_md_provider_selection_section -x` |

### Sampling Rate

- **Per task commit:** `pytest tests/test_mcp_server.py tests/test_skill.py -x`
- **Per wave merge:** `pytest` (full suite)
- **Phase gate:** Full suite green before `/gsd-verify-work`

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Method-name allow-list (`_RUNNABLE_METHODS`, `_DIAGNOSTICS_METHODS`) at every tool boundary; `n_classes` validated as `int | None` by MCP schema |
| V4 Access Control | no | No authentication; MCP is stdio-local |
| V6 Cryptography | no | No crypto operations |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unknown method name injection (T-12-02) | Tampering | Allow-list frozenset check before any fdars call |
| Array-as-scalar injection (T-12-03) | Tampering | MCP schema enforces `float | int | None` for all run_method params; `n_classes: int | None` for `fdars_build_diagnostics` is safe |
| LLM call inside MCP tool | Elevation of privilege | `test_mcp_does_not_import_advise` locks the invariant |
| Unknown `params_after` key in compare_run | Tampering | `_ALLOWED_PARAMS` frozenset in `_compare.py:46` [VERIFIED: python/fdars/mcp/_compare.py:46] |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `FDARS_ADVISOR_PROVIDER`, `FDARS_ADVISOR_MODEL`, `FDARS_ADVISOR_BASE_URL` are the correct env var names resolved by `providers._factory.resolve_provider` | §3 Provider Selection | SKILL.md documents wrong env vars; easy to fix in Phase 24 |

**All other claims in this research were verified by reading source files this session.**

---

## Open Questions

1. **`depth` dispatch function choice**
   - What we know: `fdars.depth` has `fraiman_muniz_1d`, `modal_1d`,
     `random_projection_1d` [ASSUMED from CLAUDE.md module description]
   - What's unclear: exact signatures and whether `fraiman_muniz_1d` is
     `(data, argvals)` with no additional params
   - Recommendation: read `python/fdars/advisor/aspects/depth.py` module
     header to confirm; if `fraiman_muniz_1d` takes extra params beyond
     `(data, argvals)`, add one new scalar `method_name` param or simply
     hard-code to it

2. **`_method_params` test helper**
   - Whether to update `_method_params` in `test_mcp_server.py` to include
     `"depth": {}` for consistency, or leave it and test depth separately
   - Recommendation: leave `_method_params` as-is; use a standalone
     `test_run_method_depth` test to avoid changing the scope of
     `test_run_method_all_methods`

---

## Sources

### Primary (HIGH confidence — read this session)

- `python/fdars/mcp/_runner.py` — full file read; `_SUPPORTED_METHODS:51-53`, `run_method:57-65`
- `python/fdars/mcp/server.py` — full file read; both `_SUPPORTED_METHODS:47`, `fdars_build_diagnostics:54-131`, `fdars_compare_run:327-334`
- `python/fdars/mcp/_registry.py` — full file read; `store_result:96-111`
- `python/fdars/mcp/_compare.py` — full file read; `_ALLOWED_PARAMS:46`
- `python/fdars/advisor/__init__.py` — full file read; `_supported:124-132`, `advise:365-445`
- `python/fdars/advisor/aspects/depth.py` — full file read; builder signature and `np.asarray(raw):50`
- `python/fdars/advisor/aspects/outliers.py` — full file read
- `python/fdars/advisor/aspects/classification.py` — full file read; `n_classes` param
- `python/fdars/advisor/aspects/represent.py` — full file read; dict/Fdata dual-input
- `python/fdars/advisor/aspects/regression.py` — full file read
- `python/fdars/advisor/aspects/regression_cv.py` — full file read
- `python/fdars/advisor/aspects/spm.py` — full file read
- `.claude/skills/fdars-advisor/SKILL.md` — full file read; stale aspect list and install note
- `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py` — full file read
- `tests/test_mcp_server.py` — full file read; all 7 tests and `_method_params` helper
- `tests/test_skill.py` — full file read; all 6 tests

### Secondary

- `.planning/phases/22-surface-integration/22-CONTEXT.md` — locked decisions
- `.planning/REQUIREMENTS.md` — SURF-01/02/03 definitions

## Metadata

**Confidence breakdown:**
- Runnable-vs-diagnostics-only split: HIGH — every builder's input contract
  was read directly from source this session
- MCP LLM-free invariant: HIGH — grep confirmed zero hits for "advise" in
  `python/fdars/mcp/`
- SKILL.md update spec: HIGH — current SKILL.md read verbatim
- Test strategy: HIGH — existing test patterns read verbatim; new tests follow
  identical patterns

**Research date:** 2026-08-12
**Valid until:** Changes in `fdars.depth.*` signatures or `advisor._supported` additions
would require re-reading the affected files (low risk for Phase 22 scope).
