---
phase: 13-agent-skill-surface
type: RESEARCH
date: 2026-08-10
---

# Phase 13: Agent Skill Surface — Research

**Researched:** 2026-08-10
**Domain:** Anthropic Agent Skills authoring + fdars offline compute + Python packaging
**Confidence:** MEDIUM (SKILL.md spec from official agentskills.io + codebase fully read; execution env partially assumed)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D1 — No discuss-phase.** Design context captured inline in CONTEXT.md; plan from RESEARCH.md + REQUIREMENTS.md + CONTEXT.md.
- **D2 — Research first.** The Anthropic Agent Skills authoring spec (SKILL.md frontmatter, progressive disclosure, bundled scripts/resources) and the skill execution-environment options are external, evolving Anthropic docs — ground the plan in current docs before authoring.
- **D3 — Execution target = Managed Agents env with `allow_package_managers` (ROADMAP-recommended).** At skill run time, `fdars` is made available by pip-installing it (`pip install "fdars[mcp]"`, Python ≥3.10) inside the Managed Agents execution environment, which permits package managers / network.
  - Rejected: **bundled wheel** (pins platform/Python ABI, bloats package), **code-execution container / no-internet** (cannot guarantee fdars presence).
  - The skill's script and SKILL.md must document this runtime clearly enough that the skill actually runs (SKILL-02 / Success Criterion 2).

### Claude's Discretion

None explicitly stated. The planner may decide: (1) whether the skill's walkthrough is recorded as a captured transcript or as an inline expected-output block; (2) exact location of the skill package in the repo (`.claude/skills/` vs `skills/`).

### Deferred Ideas (OUT OF SCOPE)

- HTTP/REST surface
- Non-Anthropic providers
- Autonomous mutation of user data
- Bundled-wheel approach
- No-internet code-execution container
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SKILL-01 | A `SKILL.md` + script packages the interpret→recommend→re-run→compare workflow | Sec. "Standard Stack", "Architecture Patterns", "Code Examples" — exact SKILL.md frontmatter, script invocation, fdars API signatures |
| SKILL-02 | The skill's execution environment (fdars availability) is documented so the skill actually runs | Sec. "Execution Environment", "Pitfall 3: fdars[mcp] not on PyPI", "Standard Stack" — install command, Python constraint, CI fallback |
</phase_requirements>

---

## Summary

Phase 13 packages the `fdars` advisor workflow as an **Anthropic Agent Skill**: a `SKILL.md` + a companion Python script that drives the interpret→recommend→re-run→compare loop using the `fdars.mcp` helpers built in Phases 11–12.

The skill's format is governed by the open [agentskills.io specification](https://agentskills.io/specification) (2025/2026). A skill is a directory with a required `SKILL.md` (YAML frontmatter + Markdown body) and optional `scripts/`, `references/`, and `assets/` subdirectories. The frontmatter defines five fields: `name` (required), `description` (required), `allowed-tools` (optional, experimental), `compatibility` (optional), and `metadata` (optional). The directory name must match the `name` field exactly.

The critical execution environment finding: the published PyPI package `fdars 0.2.0` does **not** include the `[mcp]` or `[advisor]` extras — those extras are defined in the local `pyproject.toml` but not yet published. The skill's install step must therefore either (a) install from the git repository (`pip install "fdars[mcp] @ git+https://github.com/sipemu/pyfda"`), or (b) install `fdars` and `mcp>=2.0.0` separately, until a new PyPI release ships the extras. This is the single most important constraint for SKILL-02.

The script itself should call `fdars.mcp` helpers **directly** (not over stdio transport) — exactly as `examples/mcp_recipe.py` does. This is confirmed correct: the recipe runs offline, exits 0, and produces a deterministic 4-key delta block in under 5 seconds. The grounding invariant is already enforced by the existing `advisor.build_diagnostics` + `advise()` pipeline.

**Primary recommendation:** Author the skill as `.claude/skills/fdars-advisor/` with a single `SKILL.md` and a `scripts/fdars_advisor_walkthrough.py` that mirrors `mcp_recipe.py` but adds the `advise()` call. Document the install step in both `SKILL.md`'s `compatibility` field and a `scripts/setup.sh` helper.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Skill discovery (name + description) | Agent runtime | — | Loaded at session start; 50–100 tokens per skill |
| Offline diagnostics (`build_diagnostics`) | Python / fdars layer | — | Deterministic, no LLM; fdars-core computes every number |
| Grounded LLM advice (`advise`) | Python / advisor layer | Anthropic API | LLM reasons over diagnostics; does not fabricate |
| Before/after compare loop (`compare_run`) | Python / fdars.mcp layer | — | All computation in-process; no MCP transport needed for skill script |
| Skill script invocation | Skill execution env (Claude / Claude Code) | — | Agent reads SKILL.md body, runs script via Bash |
| Package installation | Skill execution env | PyPI / GitHub | `pip install fdars mcp>=2.0.0` at run time |
| Walkthrough capture / dry-run | CI / local shell | — | Script exits 0 without API key; LLM call env-gated |

---

## Standard Stack

### Core (all already in repo — no new dependencies for the skill package itself)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fdars` | 0.2.0 (local editable) | Core FDA computation + advisor + mcp helpers | This is the package the skill wraps |
| `mcp` | ≥2.0.0 | Python ≥3.10 async MCP protocol (needed for `fdars.mcp` imports) | Required by `fdars.mcp._runner`, `_compare`, `_registry` at import time |
| `anthropic` | ≥0.72.0 | Claude API client for `advise()` call | Required by `fdars[advisor]` extra; `messages.parse` + adaptive thinking |
| `pydantic` | ≥2.0 | Schema validation for `Advice` output | Required by `fdars[advisor]` extra alongside `anthropic` |
| `numpy` | ≥1.23 | Array handling in script | Core fdars dependency |

### Supporting (for the skill script's setup step)

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `uv` | ≥0.9 | PEP 723 inline dependency management — preferred when available | When agent environment has `uv`; enables `uv run scripts/...` invocation |
| `pip` | ≥22.0 | Fallback package installer | When `uv` not guaranteed; explicit `pip install` in script preamble |

### Installation (for the skill's runtime environment)

The skill `SKILL.md` and companion script must document this two-step install because `fdars[mcp]` is **not yet published to PyPI** as an extra on `fdars 0.2.0`:

```bash
# Option A — once fdars 0.3.0+ ships the [mcp] and [advisor] extras to PyPI:
pip install "fdars[mcp,advisor]"

# Option B — current workaround (install from git + extras separately):
pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0

# Option C — minimal (mcp_recipe.py path only, no LLM call):
pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0
# Then: ANTHROPIC_API_KEY not required; python scripts/fdars_advisor_walkthrough.py
```

**Python constraint:** Python ≥3.10 required. The `mcp` package does not support Python 3.9.
The skill script MUST include the same version guard as `mcp_recipe.py`:

```python
# [VERIFIED: examples/mcp_recipe.py:37-44]
if sys.version_info < (3, 10):
    print("Python 3.10+ required for fdars[mcp] ...")
    sys.exit(0)
```

---

## Package Legitimacy Audit

The skill does not introduce new packages beyond what Phases 11–12 already declared. This section audits the packages the skill script will `pip install` at runtime.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `fdars` | PyPI | ~1 yr | low (research lib) | github.com/sipemu/pyfda | OK | Approved — this project's own package |
| `mcp` | PyPI | ~1 yr | growing | github.com/modelcontextprotocol/python-sdk | OK | Approved — established Anthropic protocol lib |
| `anthropic` | PyPI | ~2 yr | high | github.com/anthropics/anthropic-sdk-python | OK | Approved — official Anthropic SDK |
| `pydantic` | PyPI | ~8 yr | very high | github.com/pydantic/pydantic | OK | Approved — industry standard |

**Packages removed due to SLOP verdict:** none
**Packages flagged as suspicious (SUS):** none

*Note: `fdars[mcp]` and `fdars[advisor]` extras are defined in the local `pyproject.toml` but absent from the published PyPI 0.2.0 release. This is not a legitimacy concern — it is a release gap that the planner must address (see Pitfall 3).*

---

## Architecture Patterns

### System Architecture Diagram

```
Agent (Claude / Claude Code)
  │
  ├─ reads SKILL.md body → understands workflow steps
  │
  └─ runs scripts/fdars_advisor_walkthrough.py via Bash
       │
       ├─ [setup] pip install fdars mcp anthropic pydantic   ← network (Managed Agents)
       │
       ├─ Step 1: datasets.load_canadian_weather()
       │           └→ X (35×365), day (365,)
       │
       ├─ Step 2: registry.store_dataset(X, day)  → dataset_id
       │
       ├─ Step 3: run_method(dataset_id, "smoothing", n_basis=15)
       │           └→ before_result (dict with gcv, edf, ...)
       │           registry.store_result(before_result) → before_result_id
       │
       ├─ Step 4: build_diagnostics(before_result, "smoothing")
       │           └→ diagnostics dict (offline, deterministic)
       │
       ├─ Step 5: advise(diagnostics, task="parameter", ...)  ← Anthropic API
       │           └→ Advice(interpretation, recommendations, caveats)
       │           (env-gated: skipped if ANTHROPIC_API_KEY absent)
       │
       └─ Step 6: compare_run(dataset_id, "smoothing", before_result_id, {"n_basis": 25})
                   └→ {before, after, delta}  ← 4 scalar keys, all fdars-computed
                   PRINT: before/after diagnostics + delta
```

### Recommended Skill Package Structure

```
.claude/skills/fdars-advisor/
├── SKILL.md                          # Required: frontmatter + workflow instructions
└── scripts/
    └── fdars_advisor_walkthrough.py  # Offline-runnable end-to-end script
```

The directory name `fdars-advisor` matches the `name:` field in SKILL.md. This location makes the skill available to GSD agents via the standard project-skills-discovery mechanism (`.claude/skills/` is the first discovery path). [VERIFIED: /home/simonm/.claude/gsd-core/references/project-skills-discovery.md:1-8]

### Pattern 1: SKILL.md Frontmatter (agentskills.io spec)

**What:** The frontmatter block controls how the agent discovers and gates the skill.
**When to use:** Every skill requires exactly this structure.

```yaml
# Source: agentskills.io/specification (2026)
---
name: fdars-advisor                    # max 64 chars; must match directory name
description: >                         # max 1024 chars; what + when
  Run the fdars functional data analysis advisor: interpret a computed
  result, get parameter recommendations grounded in fdars diagnostics,
  re-run the method with suggested parameters, and compare before/after.
  Use when working with fdars clustering, smoothing, FPCA, alignment, or
  basis results and wanting grounded parameter guidance.
compatibility: >
  Requires Python 3.10+ and pip access to install fdars and mcp>=2.0.0.
  Optionally requires ANTHROPIC_API_KEY for grounded LLM advice step.
  Designed for Claude Code and Managed Agents environments.
allowed-tools: Bash Read Write
---
```

**Key constraints verified against spec:** [CITED: agentskills.io/specification]
- `name`: lowercase, hyphens only, max 64 chars, must match directory name exactly
- `description`: 1–1024 chars; both "what it does" AND "when to use it" required for discovery
- `compatibility`: 1–500 chars; document Python version + network requirements here
- `allowed-tools`: experimental; space-separated; `Bash(pip:*)` or `Bash` are valid forms
- No other frontmatter keys permitted (validation error if unknown key appears)

### Pattern 2: Script Invocation (direct helpers, not stdio MCP)

**What:** The skill script calls `fdars.mcp` helpers directly rather than spawning a stdio MCP server.
**Recommendation:** Direct import (as in `mcp_recipe.py`) — this is correct for a self-contained skill script.

**Rationale:**
- The stdio server is for external LLM clients that cannot import Python; the skill script IS the Python client
- Direct import avoids asyncio subprocess management, port binding, and the MCP handshake overhead
- `mcp_recipe.py` already proves this path offline in < 5 seconds
- Transport-agnostic design of `server.py` means adding stdio is a separate concern (Phase 12's `run_stdio()`)

**Exact function signatures confirmed from codebase:**

```python
# [VERIFIED: python/fdars/mcp/_registry.py:51-67]
dataset_id: str = registry.store_dataset(data: np.ndarray, argvals: np.ndarray) -> str
# dataset_id format: "ds-<8-hex-chars>"

# [VERIFIED: python/fdars/mcp/_runner.py:56-64]
result: dict = run_method(
    dataset_id: str,
    method: str,          # "alignment"|"fpca"|"basis"|"smoothing"|"clustering"
    *,
    lambda_: float | None = None,
    n_basis: int | None = None,
    n_comp: int | None = None,
    k: int | None = None,
    seed: int | None = None,
) -> dict

# [VERIFIED: python/fdars/mcp/_compare.py:49-54]
result: dict = compare_run(
    dataset_id: str,
    method: str,
    before_result_id: str,
    params_after: dict,   # keys must be subset of {"lambda_", "n_basis", "n_comp", "k", "seed"}
) -> dict
# Returns: {before_result_id, after_result_id, before: dict, after: dict, delta: dict}

# [VERIFIED: python/fdars/advisor.py:188-195]
diagnostics: dict = build_diagnostics(
    result,               # dict or AlignmentResult
    method: str,          # "alignment"|"fpca"|"basis"|"smoothing"|"clustering"
    *,
    argvals=None,
    **kwargs,
) -> dict

# [VERIFIED: python/fdars/advisor.py:940-946]
advice: Advice = advise(
    diagnostics: dict,
    *,
    task: str,            # "interpretation"|"parameter"|"method"
    domain_context: str,
    model: str = "claude-opus-4-8",
) -> Advice
```

### Pattern 3: Supported Methods and Default Parameters

Verbatim from `_runner.py` and `_compare.py`:

```python
# [VERIFIED: python/fdars/mcp/_runner.py:51-53]
_SUPPORTED_METHODS = frozenset(
    {"alignment", "fpca", "basis", "smoothing", "clustering"}
)

# [VERIFIED: python/fdars/mcp/_compare.py:46]
_ALLOWED_PARAMS = frozenset({"lambda_", "n_basis", "n_comp", "k", "seed"})
```

Method → runner mapping [VERIFIED: python/fdars/mcp/_runner.py:154-204]:
- `"alignment"` → `fdars.alignment.karcher_mean(data, argvals, lambda_=0.0)`
- `"fpca"` → `fdars.regression.fpca(data, argvals, n_comp=3)`
- `"basis"` → `fdars.basis.basis_nbasis_cv(data, argvals, lambda_=1.0)`
- `"smoothing"` → `fdars.basis.pspline_fit_gcv(data, argvals, n_basis=15)`
- `"clustering"` → `fdars.clustering.kmeans_fd(data, argvals, k=3, seed=42)`

### Pattern 4: Grounding Invariant in Walkthrough

The grounding invariant is: every recommendation cites a `diagnostics` value computed by fdars; the LLM never fabricates. This is enforced by:
1. The `Advice` Pydantic schema requiring non-empty `evidence` list in each `Recommendation` [VERIFIED: python/fdars/advisor.py:81-87]
2. The system prompt forbidding fabrication [VERIFIED: python/fdars/advisor.py:836-845]
3. The `advise()` call receiving only the diagnostics dict as user content [VERIFIED: python/fdars/advisor.py:984-998]

The walkthrough script must demonstrate this by printing both the diagnostics dict AND the resulting `Advice.recommendations[*].evidence` items side by side.

### Pattern 5: Offline / CI Dry-Run Without API Key

```python
# Pattern for env-gating the LLM step (mirrors test_advisor.py):
import os
RUN_LLM = bool(os.environ.get("ANTHROPIC_API_KEY"))

diagnostics = build_diagnostics(before_result, "smoothing")

if RUN_LLM:
    advice = advise(diagnostics, task="parameter",
                    domain_context="35 Canadian weather stations, smoothing comparison")
    # print advice.interpretation, recommendations, caveats
else:
    print("[offline mode] skipping advise() — set ANTHROPIC_API_KEY to enable")

# compare_run always runs (no API key needed):
compare_result = compare_run(dataset_id, "smoothing", before_result_id, {"n_basis": 25})
```

This pattern ensures:
- CI runs exit 0 without `ANTHROPIC_API_KEY` (satisfies Success Criterion 3 for dry-run)
- The delta block is always printed (deterministic, observable)
- The full walkthrough runs when an API key is present

### Anti-Patterns to Avoid

- **Nesting `params_after` as a dict argument to `compare_run` via MCP tool:** The MCP tool schema flattens params as top-level args. The skill script calls `compare_run()` directly so pass `params_after={"n_basis": 25}` — do not replicate the flat-arg pattern [VERIFIED: python/fdars/mcp/_compare.py:49-54]
- **Using `mcp.Client` transport in the skill script:** Unnecessary; the skill script can import helpers directly. Reserve stdio transport for external agent use.
- **Description that only says "what":** A description like "runs fdars advisor" is insufficient for discovery. Must include "when to use it" (trigger keywords like "clustering", "smoothing", "parameter guidance", "before/after comparison").
- **Importing `fdars.mcp` on Python 3.9:** `_runner.py`, `_compare.py`, and `server.py` all raise `ImportError` on `sys.version_info < (3, 10)`. The script must version-guard before any `fdars.mcp` import.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Offline diagnostics | Custom metric computation | `advisor.build_diagnostics` | 5-branch dispatcher, branch A-prime fix, all edge cases handled |
| Before/after delta | Manual diff loop | `compare_run` from `_compare.py` | Allowlist validation, scalar-finite filter, bool exclusion all in place |
| LLM grounding | Custom prompt engineering | `advisor.advise()` + `_system_prompt()` | Grounding invariant, evidence schema, task-family clauses already authored |
| Handle registry | dict + random IDs | `HandleRegistry` singleton | Registry clear pattern for tests already established |
| MCP transport | Custom stdio framing | `server.run_stdio()` | Available but not needed for skill script |

**Key insight:** The skill script is a thin orchestrator. All hard problems are solved in the Phase 11–12 libraries. The script's job is to call them in the right order and format the output for human reading.

---

## Runtime State Inventory

> This phase is not a rename/refactor phase — no runtime state inventory needed.

---

## Common Pitfalls

### Pitfall 1: Description Too Vague for Discovery

**What goes wrong:** Agent does not activate the skill because description matches too few task keywords.
**Why it happens:** Short descriptions like "fdars advisor" give the agent no signal about when to use it.
**How to avoid:** Description must name the workflow steps AND the trigger scenarios. Include "functional data analysis", "clustering", "smoothing", "FPCA", "alignment", "parameter guidance", "before/after comparison", "grounded advice".
**Warning signs:** Agent answers fdars questions without mentioning the skill.

### Pitfall 2: Body Over 500 Lines

**What goes wrong:** Skill body exceeds the recommended 500-line / 5000-token limit; activating it consumes excessive context.
**Why it happens:** Trying to document every API signature in SKILL.md instead of referencing bundled files.
**How to avoid:** SKILL.md body = concise workflow steps + script invocation command. Detail goes in `scripts/` or `references/`. [CITED: agentskills.io/specification — progressive disclosure]

### Pitfall 3: `fdars[mcp]` Not Published to PyPI

**What goes wrong:** `pip install "fdars[mcp]"` installs `fdars 0.2.0` without the `mcp` dependency because the `[mcp]` extra is not in the published PyPI metadata for 0.2.0.
**Why it happens:** The extras (`mcp`, `advisor`) are defined in the local `pyproject.toml` but the PyPI release predates them. [VERIFIED: curl https://pypi.org/pypi/fdars/0.2.0/json — provides_extra: ['dev', 'plot'] only]
**How to avoid:** The skill's install step must be:
```bash
pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0
```
OR: the planner must add a task to publish `fdars 0.3.0` to PyPI with the extras before the skill's install step can use the `fdars[mcp,advisor]` syntax.
**Warning signs:** `import fdars.mcp` raises `ModuleNotFoundError: No module named 'mcp'` after `pip install fdars[mcp]`.

### Pitfall 4: Python 3.9 Import Failure

**What goes wrong:** Importing `fdars.mcp._runner` or `_compare` on Python 3.9 raises `ImportError` before the version guard runs.
**Why it happens:** The version guard is inside each module file, but `from fdars.mcp._runner import run_method` triggers the module-level `raise ImportError` on Python 3.9.
**How to avoid:** The skill script MUST check `sys.version_info < (3, 10)` and `sys.exit(0)` BEFORE any `from fdars.mcp import ...` line. This matches the existing pattern in `mcp_recipe.py`. [VERIFIED: examples/mcp_recipe.py:37-44]

### Pitfall 5: `name` Field Mismatch with Directory Name

**What goes wrong:** SKILL.md validation fails; skill not discovered.
**Why it happens:** agentskills.io spec requires `name` to exactly match the parent directory name after NFKC normalization. [CITED: agentskills.io/specification]
**How to avoid:** If the directory is `.claude/skills/fdars-advisor/`, the frontmatter must be `name: fdars-advisor`.

### Pitfall 6: Using `async` in Skill Script for MCP Client

**What goes wrong:** Script hangs or raises event-loop errors in CLI context.
**Why it happens:** `mcp.Client` is async; using it requires `asyncio.run()` and proper transport setup.
**How to avoid:** Do not use `mcp.Client` in the skill script. Call `registry`, `run_method`, `compare_run`, `build_diagnostics`, `advise` directly as synchronous Python. [VERIFIED: python/fdars/mcp/server.py:359-378 — `run_stdio()` is only needed for external clients]

### Pitfall 7: Registry State Between Script Runs

**What goes wrong:** Stale handles from a previous run are in the registry if the singleton persists.
**Why it happens:** `registry` is a module-level singleton. If the same Python process runs the script twice, IDs from run 1 remain in run 2.
**How to avoid:** Call `registry.clear()` at the top of `main()`. This is the same pattern used in tests. [VERIFIED: python/fdars/mcp/_registry.py:140-148]

---

## Code Examples

### Full Skill Script Skeleton (fdars_advisor_walkthrough.py)

```python
# Source: pattern from examples/mcp_recipe.py + advisor.py signatures
"""fdars advisor skill — interpret→recommend→re-run→compare walkthrough.

Run offline (no API key):
    python scripts/fdars_advisor_walkthrough.py

Run with LLM advice (requires ANTHROPIC_API_KEY):
    ANTHROPIC_API_KEY=sk-... python scripts/fdars_advisor_walkthrough.py
"""
from __future__ import annotations
import os, sys

# Version guard MUST precede fdars.mcp imports
if sys.version_info < (3, 10):
    print("Python 3.10+ required for fdars[mcp]. Exiting 0.")
    sys.exit(0)

import numpy as np
from fdars import datasets
from fdars.mcp._registry import registry
from fdars.mcp._runner import run_method
from fdars.mcp._compare import compare_run
from fdars.advisor import build_diagnostics, advise

def main() -> None:
    registry.clear()                              # Pitfall 7: clear singleton

    # Step 1: Load dataset
    ds = datasets.load_canadian_weather()
    X = np.asarray(ds.data.data, dtype=float)    # (35, 365)
    day = np.asarray(ds.argvals, dtype=float)    # (365,)
    dataset_id = registry.store_dataset(X, day)

    # Step 2: Run method (before)
    before_result = run_method(dataset_id, "smoothing", n_basis=15)
    before_result_id = registry.store_result(before_result)

    # Step 3: Build diagnostics + (optional) grounded advice
    diagnostics = build_diagnostics(before_result, "smoothing")
    if os.environ.get("ANTHROPIC_API_KEY"):
        advice = advise(diagnostics, task="parameter",
                        domain_context="35 Canadian weather stations, daily temperature curves")
        # print advice.interpretation, recommendations, caveats
    else:
        print("[offline] ANTHROPIC_API_KEY not set — skipping advise()")

    # Step 4: Compare (always runs — deterministic, no API key)
    compare_result = compare_run(
        dataset_id, "smoothing", before_result_id, {"n_basis": 25}
    )
    delta = compare_result["delta"]
    print(f"Delta ({len(delta)} scalar keys):")
    for k, v in delta.items():
        print(f"  {k}: {v:+.6f}")

if __name__ == "__main__":
    main()
```

### SKILL.md Body — Minimal Prescriptive Form

```markdown
---
name: fdars-advisor
description: >
  Run the fdars functional data analysis advisor workflow: interpret a
  computed result, get grounded parameter recommendations, re-run with
  suggested parameters, and compare before/after diagnostics. Use when
  working with fdars clustering, smoothing, FPCA, alignment, or basis
  results and needing parameter guidance or a before/after comparison.
compatibility: >
  Requires Python 3.10+ and network access (pip install).
  Optional: ANTHROPIC_API_KEY for grounded LLM advice step.
allowed-tools: Bash Read
---

## Setup

Install dependencies (run once):

```bash
pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0
```

Or, once fdars 0.3.0+ is on PyPI:

```bash
pip install "fdars[mcp,advisor]"
```

## Offline Walkthrough (no API key needed)

Run the compare loop against the Canadian Weather dataset:

```bash
python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py
```

Expected output: 4-key delta block (gcv_aic_approx, gcv_bic_approx, optimal_gcv, optimal_edf).

## Grounded Advice (requires ANTHROPIC_API_KEY)

```bash
ANTHROPIC_API_KEY=sk-... python .claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py
```

Expected output: interpretation + recommendations with cited evidence values + before/after delta.

## Grounding Invariant

Every recommendation cites a diagnostics value computed by fdars. The LLM never fabricates numbers.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Skills as single-file prompts | Skills as directories (`SKILL.md` + `scripts/`) | 2025 (agentskills.io spec) | Progressive disclosure; scripts loaded on demand |
| Embedding all docs in SKILL.md body | Splitting into `SKILL.md` + `references/` + `scripts/` | 2025 | Context efficiency; agents load detail only when needed |
| `pip install pkg` at skill run time | PEP 723 `uv run scripts/foo.py` (self-contained deps) | 2024–2025 | No venv setup; uv caches deps; portable |
| MCP via network (SSE/HTTP) | MCP via stdio (local process) or direct import | 2024–2025 | Direct import is simplest for skill scripts |

**Deprecated/outdated:**
- Single-file SKILL.md with all instructions inline: still valid but discouraged for complex skills; use `references/` for detail.
- Skill-level `dependencies:` frontmatter field: not in the agentskills.io spec; use `compatibility:` to document what is needed and handle installation in `scripts/setup.sh` or script preamble.

---

## Walkthrough Determinism

The Canadian Weather dataset is the correct choice for the walkthrough because:
1. It is bundled in `fdars.datasets` (no network fetch at run time) [VERIFIED: pyproject.toml:48-50 — `include = ["python/fdars/data/*.csv"]`]
2. `mcp_recipe.py` already proves it produces a stable 4-key delta (run confirmed 2026-08-10):

```
Delta (after - before) [4 scalar keys]:
  gcv_aic_approx: -2181.912236
  gcv_bic_approx: -2108.448571
  optimal_gcv: -0.068405
  optimal_edf: +9.853957
```

[VERIFIED: ran `examples/mcp_recipe.py` against `.venv` with mcp 2.0.0 and editable fdars install, 2026-08-10]

The delta is deterministic: `pspline_fit_gcv` is seeded via GCV optimization (no RNG), so two runs on the same data produce the same values. The `advise()` call is NOT deterministic (LLM output varies) — the walkthrough transcript should show the diagnostics and delta as the fixed ground truth; the advice is illustrative.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Managed Agents `allow_package_managers` permits `pip install` of git-URL packages, not just PyPI packages | Execution Environment, Pitfall 3 | Skill cannot install fdars until PyPI extras are published; must use PyPI-only workaround |
| A2 | `allowed-tools: Bash Read` in SKILL.md frontmatter restricts tool access (Experimental) | SKILL.md Pattern | Tool restriction may be unenforced (GitHub issue #37683 reports this); skill still runs |
| A3 | `uv` is not guaranteed to be present in the Managed Agents execution environment | Standard Stack | Falls back to `pip install`; no functional impact |
| A4 | Once `fdars 0.3.0` is published to PyPI with `[mcp]` and `[advisor]` extras, the one-liner install works | Standard Stack | Users must use the git-URL workaround until then |
| A5 | `datasets.load_canadian_weather()` returns `argvals` as a 1D array directly accessible as `ds.argvals` | Code Examples | Script fails at `np.asarray(ds.argvals, ...)` — check actual return type from datasets module |

---

## Open Questions

1. **When will fdars 0.3.0 ship to PyPI with `[mcp]` and `[advisor]` extras?**
   - What we know: pyproject.toml already declares them; publish.yml triggers on `v*` git tags
   - What's unclear: whether a v0.3.0 tag will be cut before Phase 13 is done
   - Recommendation: Plan the skill with the git-URL install fallback; note the simpler install command as a TODO

2. **`datasets.load_canadian_weather()` return type — does `ds.argvals` exist directly?**
   - What we know: `mcp_recipe.py` uses `ds.argvals` and `ds.data.data` — it ran offline and exited 0
   - What's unclear: exact type of `ds` (named tuple? dataclass?)
   - Recommendation: Keep the same access pattern as `mcp_recipe.py` exactly; it is verified to work

3. **Does `compatibility:` field need to state `ANTHROPIC_API_KEY` requirement explicitly?**
   - What we know: the spec says `compatibility` is for environment requirements
   - What's unclear: whether Claude's skill runner surfaces this to users before activation
   - Recommendation: Include in `compatibility` AND in the SKILL.md body under "Setup"

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.10+ | `fdars.mcp` (mcp>=2.0.0) | ✓ (system Python 3.14.5) | 3.14.5 | Exit 0 gracefully on 3.9 |
| `mcp` ≥2.0.0 | `fdars.mcp._runner` imports | ✓ (in project `.venv`) | 2.0.0 | Not available without `pip install mcp` |
| `uv` | PEP 723 script invocation | ✓ (0.9.28 at /home/simonm/.cargo/bin/uv) | 0.9.28 | Use `pip install` instead |
| `fdars[mcp]` (PyPI extra) | Skill runtime install | ✗ (not on PyPI 0.2.0) | — | Use git-URL install: see Pitfall 3 |
| `ANTHROPIC_API_KEY` | `advise()` LLM call | Unknown (env-gated) | — | Skip with `[offline]` message |
| Canadian Weather CSV | `datasets.load_canadian_weather()` | ✓ (bundled in wheel/editable) | — | — |

**Missing dependencies with no fallback:**
- `fdars[mcp]` on PyPI — the `[mcp]` extra is not published. The skill install step must use the git-URL form until a new PyPI release ships.

**Missing dependencies with fallback:**
- `ANTHROPIC_API_KEY` — advise() step is skipped; the script still exits 0 and prints the delta.
- `uv` — falls back to `pip install` in script preamble.

---

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` — treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x (already in `.venv`) |
| Config file | `pyproject.toml` (no pytest section; defaults) |
| Quick run command | `pytest tests/test_skill.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SKILL-01 | SKILL.md parses — has required frontmatter (`name`, `description`) | unit | `pytest tests/test_skill.py::test_skill_md_frontmatter -x` | ❌ Wave 0 |
| SKILL-01 | Script exits 0 offline (no API key, Python ≥3.10) | smoke | `pytest tests/test_skill.py::test_walkthrough_script_offline -x` | ❌ Wave 0 |
| SKILL-01 | Script prints non-empty delta with ≥1 numeric key | smoke | `pytest tests/test_skill.py::test_walkthrough_delta_nonempty -x` | ❌ Wave 0 |
| SKILL-02 | SKILL.md `compatibility` field documents Python ≥3.10 and pip requirement | unit | `pytest tests/test_skill.py::test_skill_md_compatibility -x` | ❌ Wave 0 |
| SKILL-02 | Script exits 0 on Python 3.9 with informative message (not error) | unit | existing `pytestmark` pattern from `test_mcp_server.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_skill.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_skill.py` — new test module: SKILL.md parse, frontmatter validation, offline script run, delta assertions, Python 3.9 exit-0 check
- [ ] No new framework install needed — pytest already present

*(Note: SKILL.md frontmatter parsing in tests can be done with `yaml.safe_load` from the stdlib's PyYAML or the vendored `frontmatter` package — ASSUMED since neither is listed as a test dependency yet.)*

---

## Security Domain

> `security_enforcement: true` confirmed in `.planning/config.json`; ASVS level 1.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No user auth in skill script |
| V3 Session Management | No | No sessions; stateless script |
| V4 Access Control | Minimal | `_ALLOWED_PARAMS` allowlist in `compare_run` enforces param-injection boundary [VERIFIED: python/fdars/mcp/_compare.py:46] |
| V5 Input Validation | Yes | `params_after` allowlist validation; method allowlist (T-12-02, T-12-03) already in place |
| V6 Cryptography | No | No crypto; `ANTHROPIC_API_KEY` read from env (not file) |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Param injection via `params_after` | Tampering | `_ALLOWED_PARAMS` frozenset blocks unknown keys [VERIFIED: python/fdars/mcp/_compare.py:136-141] |
| Method name injection | Tampering | `_SUPPORTED_METHODS` frozenset at tool boundary [VERIFIED: python/fdars/mcp/_runner.py:51-53] |
| API key in script | Information Disclosure | NEVER hardcode; always `os.environ.get("ANTHROPIC_API_KEY")` |
| Unbounded pip install at skill run time | Tampering | Only install known packages (fdars, mcp, anthropic, pydantic); no user-supplied package names |
| Large-array injection via `params_after` | Tampering | Only scalar params accepted (`float|None`, `int|None`) — enforced by `_runner.py` type hints and fdars call |

**Security note for SKILL.md body:** The `compatibility` field and setup instructions must NOT include credentials, API keys, or sensitive values. The `ANTHROPIC_API_KEY` is read from the environment only, never from the skill package.

---

## Sources

### Primary (MEDIUM confidence — verified against official spec and codebase)

- `agentskills.io/specification` — SKILL.md frontmatter fields, constraints, progressive disclosure model, scripts/ conventions [CITED: agentskills.io/specification]
- `github.com/anthropics/skills` — official Anthropic skills repository confirming format [CITED: github.com/anthropics/skills]
- `python/fdars/mcp/_registry.py` (lines 51–67, 96–110, 140–148) — `store_dataset`, `store_result`, `clear` signatures [VERIFIED]
- `python/fdars/mcp/_runner.py` (lines 51–53, 56–64, 154–204) — `_SUPPORTED_METHODS`, `run_method` signature, dispatch [VERIFIED]
- `python/fdars/mcp/_compare.py` (lines 46, 49–54, 136–141) — `_ALLOWED_PARAMS`, `compare_run` signature, allowlist check [VERIFIED]
- `python/fdars/mcp/server.py` (lines 47, 359–378) — `_SUPPORTED_METHODS`, `run_stdio()` [VERIFIED]
- `python/fdars/advisor.py` (lines 53, 81–87, 188–195, 836–845, 940–946, 984–998) — `ADVISOR_ANTHROPIC_MIN_VERSION`, `Recommendation` schema, `build_diagnostics`, system prompt, `advise` signature [VERIFIED]
- `examples/mcp_recipe.py` (lines 37–44, 48–51) — version guard pattern, direct import pattern [VERIFIED]
- `pyproject.toml` (lines 39–44, 48–50) — `[advisor]`, `[mcp]` extras, CSV include [VERIFIED]
- Live run of `examples/mcp_recipe.py` confirming delta output (2026-08-10) [VERIFIED]
- `curl https://pypi.org/pypi/fdars/0.2.0/json` — confirms `[mcp]` and `[advisor]` extras absent from PyPI 0.2.0 [VERIFIED]

### Secondary (LOW confidence)

- Web search results on SKILL.md format and PEP 723 script invocation patterns [websearch, LOW]

---

## Metadata

**Confidence breakdown:**
- SKILL.md frontmatter spec: MEDIUM — confirmed via official agentskills.io spec and real SKILL.md examples in `~/.claude/skills/`
- Script signatures (exact API): HIGH — read directly from source files this session
- PyPI gap (fdars[mcp] not published): HIGH — confirmed via live pypi.org API query
- Managed Agents `allow_package_managers` behavior: LOW — assumed from CONTEXT.md D3; not independently verified via Anthropic docs
- Walkthrough delta values: HIGH — confirmed by running `mcp_recipe.py` this session

**Research date:** 2026-08-10
**Valid until:** 2026-09-10 (30 days — agentskills.io spec is stable; PyPI status may change sooner if fdars 0.3.0 ships)

---

## Project Constraints (from CLAUDE.md)

Extracted actionable directives the planner must verify:

| Directive | Source | Implication for Phase 13 |
|-----------|--------|--------------------------|
| GSD workflow enforcement: use `/gsd-quick` for small tasks, `/gsd-execute-phase` for phase work | `.claude/CLAUDE.md` | All file edits must go through GSD workflow |
| No Python linter in CI (no ruff/black/pylint) | CLAUDE.md tech stack | No linting step needed; follow PEP 8 by convention |
| NumPy/Sphinx docstring format for all public functions | CLAUDE.md conventions | Skill script's `main()` and any helpers need NumPy docstrings |
| Private helpers prefixed with underscore | CLAUDE.md naming | Any helper functions in the script: `_setup_deps()`, `_print_delta()` etc. |
| `from __future__ import annotations` | CLAUDE.md import convention | Required at top of skill script |
| pytest is the test runner | CLAUDE.md tech stack | New `tests/test_skill.py` uses pytest |
| Python 3.9–3.13 compatibility for main library | CLAUDE.md runtime | Skill SCRIPT needs Python ≥3.10; library itself stays 3.9+ |
| Examples in `examples/` not `docs/examples/` | Phase 12-01 decision in STATE.md | `fdars_advisor_walkthrough.py` goes in `examples/` OR in `.claude/skills/fdars-advisor/scripts/` — skill packaging takes precedence |
