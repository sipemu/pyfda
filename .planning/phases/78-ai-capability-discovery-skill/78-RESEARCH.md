# Phase 78: AI Capability-Discovery Skill — Research

**Researched:** 2026-09-06
**Domain:** Python introspection, MCP tool authoring, agent skill design, llms.txt generation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Single generator = one source of truth**
- A generator script introspects the LIVE `fdars` package (public submodules + their
  public callables, signatures via `inspect.signature`, one-line purpose from docstrings)
  and emits ONE capability dataset. That dataset feeds all three surfaces: the skill
  `SKILL.md` capability map, the `docs/llms.txt` page, and the MCP
  `fdars_list_capabilities` tool. This makes the surfaces impossible to drift apart
  and makes SKILL-02 trivial (regenerate → assert no diff + everything importable).
- Where a curated one-liner ("what it does / when to use") is needed beyond what
  docstrings give, keep that curation in a data file the generator merges in — so
  re-generation never clobbers hand-written guidance, and the accuracy test still
  catches a method that was renamed/removed.

**New, distinct skill**
- Ship a NEW standalone skill `fdars-capabilities` (name TBD by research/planner —
  must be spec-valid and not collide with `fdars-advisor`). Its trigger is **capability
  discovery** ("what can fdars do?", "which method for X?", "how do I call Y?") —
  explicitly disjoint from `fdars-advisor`'s tune/diagnose/compare loop. The SKILL.md
  description must make the boundary clear so an agent picks the right skill
  (non-duplication is a hard constraint / GATE-04 concern).

**llms.txt page**
- Generate `docs/llms.txt` (the standard agent-readable root path) as the whole-library
  API digest, AND wire an in-nav digest page so humans and site-search reach it too.
  Follow the llms.txt convention (concise, machine-friendly, links into the method docs).

**MCP tool (LLM-free)**
- Add ONE `@mcp.tool()` `fdars_list_capabilities` to `python/fdars/mcp/server.py`
  returning the static generated capability surface (optional `module` filter arg). It
  is provably LLM-free: it returns pre-generated/introspected static data — NO model
  call, no new LLM logic in the compute boundary.
- Extend the guard-sync test(s) (`tests/test_guard_sync_version_independent.py` pattern)
  so the new tool's surface stays literal-synced with the generator, keeping the
  grounding-invariant / LLM-free boundary provable (GATE-04). Follow the existing
  "hard-coded frozenset mirror + regenerate-to-check" discipline; respect the Python 3.9
  constraint (guard test must not import `mcp` at module level).

### Claude's Discretion

None specified — all implementation decisions above are locked.

### Deferred Ideas (OUT OF SCOPE)

- Any change to the advisor loop / advisor MCP tool behavior.
- New `fdars-core` bindings / crate bump.
- The consolidated close gate — whole-site `--strict`, SVGO/determinism, human diagram
  review, GATE-04 guard-sync-green confirmation → Phase 79.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SKILL-01 | Standalone capability-discovery Agent Skill with spec-valid SKILL.md mapping whole fdars surface | SKILL.md schema verified from fdars-advisor; new skill dir, trigger, and boundary all specified |
| SKILL-02 | Automated test/harness verifying capability map against live package | Test skeleton verified RAN against live fdars 0.4.0; 0 import errors, JSON stable |
| SKILL-03 | LLM-oriented docs page (llms.txt-style API digest) wired into site | MkDocs static passthrough confirmed (requirements.txt -> site/); nav wiring pattern shown |
| SKILL-04 | MCP capability tool added, LLM-free, guard/tests updated | Tool signature designed; guard-sync pattern (Py3.9 safe) verified against existing test; 30-module frozenset confirmed |
| GATE-04 | Grounding invariant + MCP LLM-free boundary preserved | Guard-sync discipline extended; sentinel-parse replaced by JSON-load approach; Py3.9 no-mcp constraint verified |
</phase_requirements>

---

## Summary

Phase 78 wires a single introspection generator to three non-duplicating surfaces:
an agent skill SKILL.md, a `docs/llms.txt` page, and an MCP capability tool. Every
surface is fed from one pre-committed JSON file (`python/fdars/_capability_map.json`)
so they cannot drift apart. The SKILL-02 accuracy test simply regenerates that JSON
and diffs it against the committed copy, then verifies every documented callable is
importable.

The live `fdars` package (0.4.0) exposes 30 enumerable modules containing 409 public
callables. `inspect.signature` works on all of them — PyO3 native functions in this
codebase DO expose `inspect.signature` (confirmed by running against `fdars.depth` and
every other module). The `__all__` attribute is present on every module (both native
and pure-Python) and is the correct filter — using `__all__` avoids accidentally
including re-exported stdlib constructs in the pure-Python modules (`fdars.datasets`
has `Any`, `Dict`, `List` from typing otherwise).

The MCP guard-sync for the new tool uses the generated JSON file directly as the
Py3.9-accessible source of truth (load JSON without importing `mcp`) rather than the
sentinel-parse pattern used for `_DIAGNOSTICS_METHODS`, because the module list is
derivable from the JSON itself. The companion test (Py 3.10+) calls the tool and asserts
no `provider`/`model` keys in the return value, proving the LLM-free boundary.

**Primary recommendation:** Generate `python/fdars/_capability_map.json` first via
`scripts/generate_capability_dataset.py`, commit it, then build all three surfaces
(SKILL.md, docs/llms.txt, MCP tool) on top of it. The SKILL-02 and guard-sync tests
validate drift continuously.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Capability dataset generation | Script (`scripts/`) | Committed JSON artifact | Generator runs at dev time; output is committed source of truth |
| SKILL.md content | Agent Skill (`~/.claude/skills/`) | Generated JSON (embedded) | Consumed by agents at invocation time; references the committed JSON |
| llms.txt digest | Docs (`docs/`) | Generator script | MkDocs copies to site root automatically (static passthrough) |
| MCP fdars_list_capabilities | MCP server (`python/fdars/mcp/`) | Committed JSON (loaded at call time) | importlib.resources loads the committed JSON; LLM-free |
| Guard-sync tests | Tests (`tests/`) | Generated JSON (Py 3.9 guard) | Py 3.9 path loads JSON without mcp import; Py 3.10+ companion calls tool |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `inspect` | stdlib | `inspect.signature()` for all callables | Works on PyO3 native callables in this codebase — CONFIRMED |
| `importlib.resources` | stdlib (3.9+) | Load committed JSON from package | `resources.files('fdars') / '_capability_map.json'` — CONFIRMED |
| `json` | stdlib | Serialize/deserialize capability dataset | `sort_keys=True` for stable diff |
| `mcp.server.MCPServer` | 2.0.0 | `@mcp.tool()` decorator | Already in server.py; requires Python 3.10+ |

### No Additional Packages Required
The entire Phase 78 implementation uses only existing dependencies: stdlib for the
generator and tests, `mcp` (already installed) for the tool, `fdars` itself for
introspection.

**Installation:** No new packages needed.

---

## Package Legitimacy Audit

No new packages are installed in this phase. All surfaces use existing project
dependencies (stdlib `inspect`, `json`, `importlib.resources`; `mcp` already in
`pyproject.toml`; `fdars` itself).

**Packages removed due to SLOP verdict:** none
**Packages flagged as suspicious SUS:** none

---

## Architecture Patterns

### System Architecture Diagram

```
scripts/generate_capability_dataset.py
  |-- imports fdars (live)
  |-- uses __all__ per module + inspect.signature()
  |-- emits python/fdars/_capability_map.json  (sorted, stable)
        |
        +-- scripts/generate_capability_dataset.py --skill
        |     --> .claude/skills/fdars-capabilities/SKILL.md (capability map body)
        |
        +-- scripts/generate_capability_dataset.py --llmstxt
        |     --> docs/llms.txt (llms.txt convention output)
        |         --> mkdocs static passthrough --> site/llms.txt
        |
        +-- python/fdars/mcp/server.py fdars_list_capabilities()
              --> importlib.resources loads _capability_map.json at call time
              --> returns {"modules": {...}, "version": "0.4.0"}
              [NO model call, NO advise(), LLM-free]

tests/test_capability_accuracy.py (SKILL-02)
  +-- primary (Py 3.9+): regenerate dataset -> diff against committed JSON
  +-- importability: getattr(fdars.<mod>, <fn>) for every entry
  +-- no mcp import at module level

tests/test_guard_sync_version_independent.py (GATE-04 extension)
  +-- primary (Py 3.9+): load JSON -> assert frozenset(keys) == _EXPECTED_CAPABILITY_MODULES
  +-- companion (Py 3.10+): call fdars_list_capabilities() -> assert no provider/model keys

.claude/skills/fdars-capabilities/SKILL.md  (SKILL-01)
  +-- frontmatter: name, description (capability-discovery trigger), compatibility
  +-- body: embedding or referencing the capability map from docs/llms.txt
```

### Recommended Project Structure

```
python/fdars/
├── _capability_map.json         # committed generated dataset (source of truth)
scripts/
├── generate_capability_dataset.py  # generator: introspect -> JSON -> SKILL.md -> llms.txt
.claude/skills/
├── fdars-capabilities/
│   └── SKILL.md                 # new capability-discovery skill (SKILL-01)
docs/
├── llms.txt                     # machine-readable digest (SKILL-03)
├── ai-capability-map.md         # human-readable in-nav digest (SKILL-03)
tests/
├── test_capability_accuracy.py  # SKILL-02: no-drift + importability
└── test_guard_sync_version_independent.py  # extended for GATE-04
python/fdars/mcp/
└── server.py                    # fdars_list_capabilities added (SKILL-04)
```

### Pattern 1: Capability Dataset Generation (VERIFIED)

This prototype RAN against live fdars 0.4.0. Output: 30 modules, 409 callables, 0 errors.

```python
# scripts/generate_capability_dataset.py
# Source: verified running in .venv with fdars 0.4.0 on 2026-09-06

import fdars
import inspect
import json
import sys

_SUBMODULE_NAMES = [
    'fdata', 'depth', 'metric', 'basis', 'smoothing', 'clustering', 'regression',
    'alignment', 'outliers', 'seasonal', 'spm', 'classification', 'tolerance',
    'conformal', 'simulation', 'explain', 'represent', 'scoring', 'inference',
    'pace_fpca', 'fts', 'scalar_on_function', 'frechet', 'density_fda',
    'multi_fdata', 'famm', 'shapelet',
    'datasets', 'metrics', 'covariance',
]
# EXCLUDED intentionally:
#   fdars.advisor  — the LLM/advisor layer; non-duplication boundary
#   fdars.plot     — matplotlib-dependent plotting helpers
#   fdars.results  — internal result-wrapper types (not user-facing callables)

def get_signature_str(obj: object, name: str) -> str:
    """Portable signature extractor: inspect.signature first, then fallbacks."""
    try:
        return str(inspect.signature(obj))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        # PyO3 fallback (not needed in current codebase — all pass inspect.signature)
        ts = getattr(obj, '__text_signature__', None)
        if ts:
            return ts
        return '(...)'

def get_purpose(obj: object) -> str:
    """First non-blank line of docstring, max 120 chars."""
    doc = getattr(obj, '__doc__', None) or ''
    lines = [line.strip() for line in doc.splitlines() if line.strip()]
    return lines[0][:120] if lines else ''

def generate_capability_dataset() -> dict:
    """Enumerate the live fdars public surface and return a stable, sorted dict."""
    dataset: dict = {}
    for mod_name in _SUBMODULE_NAMES:
        mod = getattr(fdars, mod_name, None)
        if mod is None:
            print(f"WARNING: fdars.{mod_name} not found", file=sys.stderr)
            continue
        # __all__ is the authoritative public filter for all modules
        all_ = getattr(mod, '__all__', None)
        if all_:
            names = sorted(n for n in all_ if not n.startswith('_'))
        else:
            # Fallback: public non-underscore callables (should not be reached)
            names = sorted(
                n for n in dir(mod)
                if not n.startswith('_') and callable(getattr(mod, n, None))
            )
        callables: dict = {}
        for fn_name in names:
            obj = getattr(mod, fn_name, None)
            if obj is None or not callable(obj):
                continue
            callables[fn_name] = {
                "purpose": get_purpose(obj),
                "sig": get_signature_str(obj, fn_name),
            }
        if callables:
            dataset[mod_name] = callables
    return dataset


if __name__ == '__main__':
    dataset = generate_capability_dataset()
    output_path = 'python/fdars/_capability_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, sort_keys=True, ensure_ascii=False)
    print(
        f"Written {len(dataset)} modules, "
        f"{sum(len(v) for v in dataset.values())} callables to {output_path}"
    )
```

**Key finding:** `inspect.signature()` works on ALL PyO3 native callables in this codebase
(`fdars.depth`, `fdars.alignment`, etc.). The `__text_signature__` fallback is present
but not needed. [VERIFIED: ran against .venv fdars 0.4.0]

**Key finding:** `__all__` is defined on every module (native and pure-Python). Use it as
the canonical public-API filter. It avoids stdlib re-exports (`Any`, `Dict`, `List`, etc.)
that appear in `dir()` for pure-Python modules like `fdars.datasets`. [VERIFIED: ran
against .venv fdars 0.4.0]

**Key finding:** JSON output is stable across repeated calls because `sort_keys=True` and
`_SUBMODULE_NAMES` is a static ordered list. Two runs produce identical bytes.
[VERIFIED: ran `generate_capability_dataset()` twice, compared json.dumps output]

### Pattern 2: MCP Tool `fdars_list_capabilities` (SKILL-04)

```python
# Add to python/fdars/mcp/server.py, after fdars_auto_tune

# Frozenset of module names covered by the capability map.
# MAINTENANCE: must equal frozenset(json.loads(_capability_map.json).keys())
# Update in one atomic commit when adding a new submodule to fdars.__init__.py.
_CAPABILITY_MODULES: frozenset[str] = frozenset({
    "alignment", "basis", "classification", "clustering", "conformal",
    "covariance", "datasets", "density_fda", "depth", "explain", "famm",
    "fdata", "frechet", "fts", "inference", "metric", "metrics", "multi_fdata",
    "outliers", "pace_fpca", "regression", "represent", "scalar_on_function",
    "scoring", "seasonal", "shapelet", "simulation", "smoothing", "spm",
    "tolerance",
})


@mcp.tool()
def fdars_list_capabilities(module: str | None = None) -> dict:
    """Return the pre-generated fdars capability surface.  LLM-free.

    Loads ``python/fdars/_capability_map.json`` (committed at generate time)
    and returns all or a filtered slice.  **No network call; no model invoked;
    no ANTHROPIC_API_KEY required.**  The compute path is provably LLM-free:
    this tool only reads pre-generated static data.

    Parameters
    ----------
    module : str, optional
        If given, return only the capability entry for that module.
        Must be one of the 30 modules in ``_CAPABILITY_MODULES``.
        If ``None`` (default), return all modules.

    Returns
    -------
    dict
        ``{"modules": {<module>: {<fn>: {"sig": str, "purpose": str}}},
           "version": str, "module_count": int, "callable_count": int}``

    Raises
    ------
    ValueError
        If ``module`` is given but not in ``_CAPABILITY_MODULES``.
        Message format: ``"fdars_list_capabilities: unknown module '<x>'. "``
        ``"Known: ['alignment', 'basis', ...]."``  (sorted list, parseable by
        guard-sync test via ast.literal_eval).
    """
    if module is not None and module not in _CAPABILITY_MODULES:
        raise ValueError(
            f"fdars_list_capabilities: unknown module {module!r}. "
            f"Known: {sorted(_CAPABILITY_MODULES)!r}."
        )

    import json
    from importlib import resources  # stdlib — no mcp dependency

    cap_file = resources.files('fdars') / '_capability_map.json'
    data: dict = json.loads(cap_file.read_text(encoding='utf-8'))

    if module is not None:
        modules = {module: data.get(module, {})}
    else:
        modules = data

    return {
        "modules": modules,
        "version": "0.4.0",   # fdars.__version__ at generate time
        "module_count": len(modules),
        "callable_count": sum(len(v) for v in modules.values()),
    }
```

**LLM-free boundary proof:** No `advise()`, no `provider`, no `model` arg, no
`ANTHROPIC_API_KEY`. Returns pre-generated static JSON data. The companion guard test
asserts `"provider" not in result` and `"model" not in result`. [ASSUMED — design,
not yet committed]

**ValueError format** matches the sentinel-parse pattern: `Known: [sorted list]` so
the guard test can recover it via `ast.literal_eval` if needed.

### Pattern 3: SKILL.md for `fdars-capabilities` (SKILL-01)

**Schema** (copied from `fdars-advisor/SKILL.md`, which is the spec-valid reference):
[VERIFIED: `.claude/skills/fdars-advisor/SKILL.md:1-28`]

Required frontmatter keys:
- `name` (string)
- `description` (block scalar `>` with trigger phrasing)
- `compatibility` (block scalar `>`)
- `allowed-tools` (space-separated list)

```yaml
# .claude/skills/fdars-capabilities/SKILL.md
---
name: fdars-capabilities
description: >
  Discover the full fdars functional data analysis capability surface:
  list every public submodule and callable, get the call signature and
  one-line purpose, and find the right method for a task.
  Use this skill to answer: "what can fdars do?", "which method for X?",
  "how do I call Y?", "list the fdars clustering/depth/regression/...
  methods", or "browse the fdars API".
  Trigger: whenever the user asks what fdars can do, wants to find a
  method by task description, needs a method's signature or purpose, or
  wants to explore any part of the fdars capability surface.
  Do NOT use this skill for parameter tuning, diagnostics, or before/after
  comparison — use fdars-advisor for those tasks.
compatibility: >
  Requires fdars installed (Python 3.9+).  No API key required.
  pip install fdars
  The capability map is available as docs/llms.txt at
  https://sipemu.github.io/pyfda/llms.txt or via the fdars_list_capabilities
  MCP tool (Python 3.10+, mcp>=2.0.0).
allowed-tools: Bash Read WebFetch
---
```

**Trigger boundary (NON-DUPLICATION):**

| fdars-capabilities trigger | fdars-advisor trigger |
|---------------------------|----------------------|
| "what can fdars do?" | "parameter tuning" |
| "which method for X?" | "smoothing basis selection" |
| "how do I call Y?" | "cluster k guidance" |
| "list fdars methods" | "before/after diagnostics" |
| "browse fdars API" | "grounded recommendations" |
| "explore capabilities" | "FPCA component count" |

The SKILL.md description explicitly says `"Do NOT use this skill for parameter tuning,
diagnostics, or before/after comparison — use fdars-advisor for those tasks."` This
makes the boundary machine-readable for any agent parsing the skill description.

**No validator/linter found** in this repo for SKILL.md files. The format is validated
by reading it against the spec-valid `fdars-advisor/SKILL.md` frontmatter keys.
[VERIFIED: searched `.claude/` — no validator script present]

### Pattern 4: SKILL.md Body Structure

The SKILL.md body should NOT inline the full 409-callable map (too large for the
SKILL.md itself). Instead:

1. Reference `docs/llms.txt` (canonical agent URL) for the full surface.
2. Embed a per-module summary table in the SKILL.md body (module name + 1-line purpose).
3. Show a usage example for each module category.
4. The MCP tool `fdars_list_capabilities` provides programmatic access.

```markdown
## Capability Map

The full fdars API digest is at:
- **Agent URL:** https://sipemu.github.io/pyfda/llms.txt
- **MCP tool (Python 3.10+):** `fdars_list_capabilities(module="depth")`
- **Offline:** `python -m fdars._capability_index` (or run the generator)

## Module Overview

| Module | Purpose | Example |
|--------|---------|---------|
| `fdars.fdata` | Functional data ops: mean, deriv, norm | `fdars.fdata.mean_1d(data)` |
| `fdars.depth` | Depth measures (FM, band, modal, etc.) | `fdars.depth.fraiman_muniz_1d(data, ref)` |
| `fdars.alignment` | Elastic alignment, SRSF, Karcher mean | `fdars.alignment.elastic_align_pair(...)` |
...

## How to Find a Method

```bash
# List all methods in a module
python -c "import fdars; print([n for n in dir(fdars.depth) if not n.startswith('_')])"

# Or via MCP tool (requires mcp>=2.0.0):
# fdars_list_capabilities(module="depth")
```
```

### Pattern 5: `docs/llms.txt` Convention (SKILL-03)

The llms.txt convention (from llmstxt.org): [ASSUMED — based on training knowledge of the spec, not fetched this session]

```markdown
# fdars — Functional Data Analysis for Python

> High-performance functional data analysis toolkit powered by Rust. Provides
> depth measures, basis representations, smoothing, clustering, regression,
> elastic alignment, outlier detection, time series, scalar-on-function regression,
> Fréchet regression, density FDA, and more via PyO3 bindings to fdars-core 0.14.

## Core Modules

- [fdars.fdata](https://sipemu.github.io/pyfda/reference/fdata.md): Functional data operations — mean, deriv, norm, integrate
- [fdars.depth](https://sipemu.github.io/pyfda/reference/depth.md): Depth measures — Fraiman-Muniz, band, modal, random projection
- [fdars.alignment](https://sipemu.github.io/pyfda/reference/alignment.md): Elastic alignment — SRSF, Karcher mean, elastic FPCA
...

## Full API Reference

Each entry: `module.function_name(signature)` — one-line purpose

### fdars.depth (18 methods)
- `band_1d(data, ref_data)` — Band depth for 1D functional data.
- `fraiman_muniz_1d(data, ref_data, scale=True)` — Fraiman-Muniz depth for 1D functional data.
...
```

**MkDocs static passthrough — VERIFIED:** Non-Markdown files placed in `docs/` are
copied verbatim to `site/`. Confirmed by checking `site/requirements.txt` (exists at
site root) from `docs/requirements.txt`. `docs/llms.txt` → `site/llms.txt` →
served at `https://sipemu.github.io/pyfda/llms.txt`. [VERIFIED: `site/requirements.txt`
exists after build; `site/hooks.py` also present]

**Nav wiring** — add an in-nav human-readable page `docs/ai-capability-map.md` which
MkDocs renders as HTML at `/pyfda/ai-capability-map/`. Wire it into `mkdocs.yml` nav.
The `docs/llms.txt` is raw/static; the `docs/ai-capability-map.md` is the human page.

### Anti-Patterns to Avoid

- **Generating `docs/llms.txt` at docs-build time** (via `markdown-exec` hook): Do NOT
  execute `generate_capability_dataset.py` during `mkdocs build`. The site build must
  not depend on `fdars` being importable in the docs environment (DOCS_FAST builds may
  lack the compiled extension). Generate offline and commit `docs/llms.txt` as a static
  file. [ASSUMED]
- **Importing `mcp` at module level in Py 3.9 guard tests:** Fatal on Python 3.9 where
  `mcp` is absent. Use `if sys.version_info < (3, 10): pytest.skip(...)` or the JSON-load
  approach for the primary guard. [VERIFIED: existing pattern in
  `test_guard_sync_version_independent.py:142-143`]
- **Using `dir(mod)` without `__all__` filter for pure-Python modules:** `fdars.datasets`
  exposes `Any`, `Dict`, `List` (from typing), `dataclass`, `field`, `files`, etc. via
  `dir()`. Always prefer `mod.__all__` when present. [VERIFIED: ran against live fdars]
- **Non-deterministic JSON output:** Always use `json.dumps(..., sort_keys=True)`. The
  generator's `_SUBMODULE_NAMES` list is ordered; combined with `sort_keys=True`, the
  output is byte-stable across repeated runs. [VERIFIED: two runs compared equal]
- **Putting `fdars.advisor` in the capability map:** The advisor is the LLM/diagnostics
  layer — including it in the capability map would blur the non-duplication boundary
  with `fdars-advisor` skill. `advisor` is explicitly excluded from `_SUBMODULE_NAMES`
  in the generator. [VERIFIED: `__init__.py` line 81 — advisor is a pure-Python module,
  NOT in `_submodule_names`]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Signature extraction | Custom docstring parser | `inspect.signature()` | Works on all PyO3 callables in this codebase; battle-tested |
| Package data loading | File-path construction | `importlib.resources.files('fdars') / 'file'` | Python 3.9+ compatible; survives wheel installation |
| JSON stability | Random dict ordering | `json.dumps(sort_keys=True)` | Required for byte-stable diffs in SKILL-02 test |
| Module filter | Manual `dir()` loop | `mod.__all__` | Already defined on every fdars module |

---

## Common Pitfalls

### Pitfall 1: PyO3 `inspect.signature` — Actually Works

**What goes wrong:** Assuming `inspect.signature()` fails on PyO3-wrapped callables
(a common pitfall documented in PyO3 0.x literature).

**What actually happens:** In this codebase (PyO3 0.28, pyo3 `#[pyo3(signature = (...))]`
annotations), `inspect.signature()` returns the correct signature for ALL public
callables. Verified against `fdars.depth`, `fdars.alignment`, `fdars.regression`, and
all other modules — zero failures.

**Keep the `__text_signature__` fallback in the generator** anyway (it is free, correct,
and future-proofs against any module that switches to lower-level `#[pyfunction]` without
`#[pyo3(signature = (...))]`). [VERIFIED: tested all native modules]

### Pitfall 2: Non-deterministic JSON breaks SKILL-02

**What goes wrong:** `json.dumps` on a dict without `sort_keys=True` produces different
byte sequences on different Python versions or dict insertion orders.

**How to avoid:** Always use `json.dumps(dataset, sort_keys=True, indent=2)`. The
`_SUBMODULE_NAMES` list is a static ordered tuple in the generator, so top-level key
order is deterministic too. [VERIFIED: JSON stability test confirmed]

### Pitfall 3: `mcp` import in Python 3.9 guard test

**What goes wrong:** `from fdars.mcp.server import ...` at module level pulls in
`mcp`, which is absent on Python 3.9. The test module then fails to import at all,
and the guard is silently broken.

**How to avoid:** The PRIMARY guard test (Py 3.9+) must load `_capability_map.json`
via `importlib.resources` — no mcp import. The companion test guards itself with
`if sys.version_info < (3, 10): pytest.skip(...)`. Pattern is already established in
`test_guard_sync_version_independent.py:142-143`. [VERIFIED: read source]

### Pitfall 4: `docs/llms.txt` generated during docs build

**What goes wrong:** A `markdown-exec` hook that calls `generate_capability_dataset.py`
at `mkdocs build` time fails in CI docs environments where `fdars` is not importable
(e.g., missing compiled extension, DOCS_FAST mode).

**How to avoid:** Pre-generate and commit `docs/llms.txt` as a static file. The generator
is run manually (or in a CI step that has fdars built), not by the docs build.
[ASSUMED — based on existing DOCS_FAST pattern in the project]

### Pitfall 5: Stale `_CAPABILITY_MODULES` frozenset in server.py

**What goes wrong:** A new submodule is added to `fdars/__init__.py` but
`_CAPABILITY_MODULES` in `server.py` is not updated. The guard test catches this on
Py 3.9+ (JSON keys vs frozenset mismatch), but only if the JSON is also regenerated.

**How to avoid:** The guard test PRIMARY asserts `frozenset(json.keys()) ==
_EXPECTED_CAPABILITY_MODULES`. The generator script must be re-run whenever
`_submodule_names` in `__init__.py` changes. Document this in the generator script's
module docstring. [ASSUMED — design decision]

### Pitfall 6: SKILL.md body embedding the full 409-callable map

**What goes wrong:** Embedding 409 entries inline in SKILL.md makes it thousands of
lines long — agents will hit context limits when loading it. MkDocs won't parse it
for the nav page either.

**How to avoid:** SKILL.md body shows a per-module summary table (30 rows) and
references `docs/llms.txt` for the full surface. The `fdars_list_capabilities` MCP
tool provides programmatic per-module lookup. [ASSUMED — design decision]

---

## Code Examples

### Generator: Verified Running Prototype

```python
# Source: verified running in .venv fdars 0.4.0, 2026-09-06
# Output: 30 modules, 409 callables, 0 import errors, stable JSON

import fdars, inspect, json, sys

_SUBMODULE_NAMES = [
    'fdata', 'depth', 'metric', 'basis', 'smoothing', 'clustering', 'regression',
    'alignment', 'outliers', 'seasonal', 'spm', 'classification', 'tolerance',
    'conformal', 'simulation', 'explain', 'represent', 'scoring', 'inference',
    'pace_fpca', 'fts', 'scalar_on_function', 'frechet', 'density_fda',
    'multi_fdata', 'famm', 'shapelet', 'datasets', 'metrics', 'covariance',
]

def generate_capability_dataset() -> dict:
    dataset: dict = {}
    for mod_name in _SUBMODULE_NAMES:
        mod = getattr(fdars, mod_name, None)
        if mod is None:
            continue
        all_ = getattr(mod, '__all__', None)
        names = sorted(n for n in (all_ or dir(mod)) if not n.startswith('_'))
        callables: dict = {}
        for fn_name in names:
            obj = getattr(mod, fn_name, None)
            if obj is None or not callable(obj):
                continue
            try:
                sig = str(inspect.signature(obj))
            except (ValueError, TypeError):
                sig = getattr(obj, '__text_signature__', '(...)')
            doc = getattr(obj, '__doc__', None) or ''
            purpose_lines = [l.strip() for l in doc.splitlines() if l.strip()]
            callables[fn_name] = {
                "purpose": purpose_lines[0][:120] if purpose_lines else '',
                "sig": sig,
            }
        if callables:
            dataset[mod_name] = callables
    return dataset
```

### SKILL-02 Accuracy Test Skeleton

```python
# tests/test_capability_accuracy.py
# SKILL-02: verify capability map has no drift from live fdars

from __future__ import annotations
import json
import sys
from importlib import resources

import pytest

import fdars

# ---------------------------------------------------------------------------
# The same _SUBMODULE_NAMES list as the generator — kept in sync manually
# (same discipline as _EXPECTED_DIAGNOSTICS_METHODS in guard-sync test)
# ---------------------------------------------------------------------------
_SUBMODULE_NAMES = [
    'fdata', 'depth', 'metric', 'basis', 'smoothing', 'clustering', 'regression',
    'alignment', 'outliers', 'seasonal', 'spm', 'classification', 'tolerance',
    'conformal', 'simulation', 'explain', 'represent', 'scoring', 'inference',
    'pace_fpca', 'fts', 'scalar_on_function', 'frechet', 'density_fda',
    'multi_fdata', 'famm', 'shapelet', 'datasets', 'metrics', 'covariance',
]


def _load_committed() -> dict:
    """Load the committed _capability_map.json via importlib.resources (Py 3.9+)."""
    cap_file = resources.files('fdars') / '_capability_map.json'
    return json.loads(cap_file.read_text(encoding='utf-8'))


def _generate_live() -> dict:
    """Regenerate from live fdars — mirrors generate_capability_dataset.py."""
    import inspect
    dataset: dict = {}
    for mod_name in _SUBMODULE_NAMES:
        mod = getattr(fdars, mod_name, None)
        if mod is None:
            continue
        all_ = getattr(mod, '__all__', None)
        names = sorted(n for n in (all_ or dir(mod)) if not n.startswith('_'))
        callables: dict = {}
        for fn_name in names:
            obj = getattr(mod, fn_name, None)
            if obj is None or not callable(obj):
                continue
            try:
                sig = str(inspect.signature(obj))
            except (ValueError, TypeError):
                sig = getattr(obj, '__text_signature__', '(...)')
            doc = getattr(obj, '__doc__', None) or ''
            lines = [l.strip() for l in doc.splitlines() if l.strip()]
            callables[fn_name] = {
                "purpose": lines[0][:120] if lines else '',
                "sig": sig,
            }
        if callables:
            dataset[mod_name] = callables
    return dataset


def test_capability_map_no_drift():
    """SKILL-02 (a): regenerate matches committed — no drift allowed.

    If this fails, run `python scripts/generate_capability_dataset.py` and
    commit the updated _capability_map.json.
    """
    committed = _load_committed()
    live = _generate_live()

    committed_json = json.dumps(committed, sort_keys=True, indent=2)
    live_json = json.dumps(live, sort_keys=True, indent=2)

    assert committed_json == live_json, (
        "Capability map has drifted from the live fdars package.\n"
        "Run: python scripts/generate_capability_dataset.py\n"
        "Then commit python/fdars/_capability_map.json."
    )


def test_capability_map_all_importable():
    """SKILL-02 (b): every documented callable is importable via fdars.<module>.<fn>.

    If this fails, a method was renamed or removed. Update the capability map.
    """
    committed = _load_committed()
    missing = []
    for mod_name, entries in committed.items():
        mod = getattr(fdars, mod_name, None)
        if mod is None:
            missing.append(f"fdars.{mod_name} (module not found)")
            continue
        for fn_name in entries:
            if getattr(mod, fn_name, None) is None:
                missing.append(f"fdars.{mod_name}.{fn_name}")

    assert not missing, (
        f"SKILL-02: {len(missing)} documented callables are not importable:\n"
        + "\n".join(f"  {m}" for m in missing[:20])
    )
```

### Guard-Sync Extension Skeleton (GATE-04)

```python
# tests/test_guard_sync_version_independent.py — ADDITIONS (extend existing file)
# Add BELOW the existing _EXPECTED_DIAGNOSTICS_METHODS block

from __future__ import annotations
import json
import sys
from importlib import resources

import pytest

# ---------------------------------------------------------------------------
# Expected capability modules — hard-coded mirror of _CAPABILITY_MODULES in
# fdars.mcp.server AND the keys of python/fdars/_capability_map.json.
#
# MAINTENANCE NOTE: update when a new submodule is added to fdars/__init__.py,
# regenerate _capability_map.json, and update _CAPABILITY_MODULES in server.py
# — all in one atomic commit.
# ---------------------------------------------------------------------------

_EXPECTED_CAPABILITY_MODULES: frozenset[str] = frozenset({
    "alignment", "basis", "classification", "clustering", "conformal",
    "covariance", "datasets", "density_fda", "depth", "explain", "famm",
    "fdata", "frechet", "fts", "inference", "metric", "metrics", "multi_fdata",
    "outliers", "pace_fpca", "regression", "represent", "scalar_on_function",
    "scoring", "seasonal", "shapelet", "simulation", "smoothing", "spm",
    "tolerance",
})


# PRIMARY TEST — runs on Python 3.9+ (no mcp import)
def test_capability_map_modules_match_expected():
    """Guard-sync: JSON keys == _EXPECTED_CAPABILITY_MODULES (Python 3.9+).

    Loads the committed _capability_map.json directly (no mcp dependency) and
    asserts its top-level keys equal the hard-coded expected frozenset.

    Fails if:
    - A new module was added to fdars but the JSON was not regenerated.
    - _EXPECTED_CAPABILITY_MODULES is stale (update it + regenerate JSON + update
      _CAPABILITY_MODULES in server.py in one atomic commit).
    """
    cap_file = resources.files('fdars') / '_capability_map.json'
    data = json.loads(cap_file.read_text(encoding='utf-8'))
    actual = frozenset(data.keys())

    assert actual == _EXPECTED_CAPABILITY_MODULES, (
        f"_capability_map.json keys != _EXPECTED_CAPABILITY_MODULES.\n"
        f"  In JSON only:     {actual - _EXPECTED_CAPABILITY_MODULES}\n"
        f"  In expected only: {_EXPECTED_CAPABILITY_MODULES - actual}\n"
        "Regenerate: python scripts/generate_capability_dataset.py\n"
        "Then update _EXPECTED_CAPABILITY_MODULES here and _CAPABILITY_MODULES "
        "in fdars.mcp.server in one atomic commit."
    )


# COMPANION TEST — internally guarded to Python 3.10+ (keeps MCP literal honest)
def test_capability_tool_llm_free_boundary():
    """Guard-sync companion: fdars_list_capabilities returns LLM-free result.

    Internally guarded to Python 3.10+ (mcp requires 3.10+).  Asserts:
    - The tool is callable.
    - Result has 'modules' key.
    - Result has no 'provider' or 'model' key (LLM-free boundary).
    - Result module keys == _EXPECTED_CAPABILITY_MODULES.
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    pytest.importorskip("mcp")  # skip if mcp not installed

    from fdars.mcp.server import fdars_list_capabilities  # noqa: PLC0415

    result = fdars_list_capabilities(module=None)

    # Shape assertions
    assert "modules" in result, "fdars_list_capabilities must return 'modules' key"
    assert isinstance(result["modules"], dict)

    # LLM-free boundary: no model/provider keys
    assert "provider" not in result, (
        "fdars_list_capabilities must NOT expose 'provider' key (LLM-free boundary)"
    )
    assert "model" not in result, (
        "fdars_list_capabilities must NOT expose 'model' key (LLM-free boundary)"
    )

    # Module set consistency
    returned_modules = frozenset(result["modules"].keys())
    assert returned_modules == _EXPECTED_CAPABILITY_MODULES, (
        f"fdars_list_capabilities returned modules != _EXPECTED_CAPABILITY_MODULES.\n"
        f"  Returned only:    {returned_modules - _EXPECTED_CAPABILITY_MODULES}\n"
        f"  Expected only:    {_EXPECTED_CAPABILITY_MODULES - returned_modules}"
    )


def test_capability_mcp_server_frozenset_matches():
    """Guard-sync companion: server._CAPABILITY_MODULES == expected frozenset.

    Internally guarded to Python 3.10+ via pytest.importorskip.
    """
    if sys.version_info < (3, 10):
        pytest.skip("mcp requires Python 3.10+")

    pytest.importorskip("mcp")

    from fdars.mcp.server import _CAPABILITY_MODULES  # noqa: PLC0415

    assert _CAPABILITY_MODULES == _EXPECTED_CAPABILITY_MODULES, (
        f"server._CAPABILITY_MODULES != _EXPECTED_CAPABILITY_MODULES.\n"
        f"  In server only:   {_CAPABILITY_MODULES - _EXPECTED_CAPABILITY_MODULES}\n"
        f"  In expected only: {_EXPECTED_CAPABILITY_MODULES - _CAPABILITY_MODULES}\n"
        "Update _CAPABILITY_MODULES in server.py to match."
    )
```

---

## Runtime State Inventory

Not applicable — this is a greenfield feature phase (no rename/refactor).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python venv `.venv` | Generator, tests | ✓ | 3.14.7 | — |
| `fdars` package | Generator, tests | ✓ | 0.4.0 | — |
| `mcp` | MCP tool (Py 3.10+ only) | ✓ | 2.0.0 | tests skip on Py 3.9 |
| `inspect` (stdlib) | Generator | ✓ | stdlib | — |
| `importlib.resources` (stdlib 3.9+) | Guard test, MCP tool | ✓ | stdlib | — |
| `mkdocs` | docs/llms.txt passthrough | ✓ | 1.6.1 | — |

All dependencies available. No blocking gaps.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `pytest tests/test_capability_accuracy.py tests/test_guard_sync_version_independent.py -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SKILL-02 (a) | No JSON drift from live fdars | unit | `pytest tests/test_capability_accuracy.py::test_capability_map_no_drift -x` | ❌ Wave 0 |
| SKILL-02 (b) | Every documented callable importable | unit | `pytest tests/test_capability_accuracy.py::test_capability_map_all_importable -x` | ❌ Wave 0 |
| GATE-04 | JSON keys == expected frozenset (Py 3.9+) | unit | `pytest tests/test_guard_sync_version_independent.py::test_capability_map_modules_match_expected -x` | ❌ Wave 0 (add to existing file) |
| GATE-04 | LLM-free boundary (Py 3.10+) | unit | `pytest tests/test_guard_sync_version_independent.py::test_capability_tool_llm_free_boundary -x` | ❌ Wave 0 |
| GATE-04 | `_CAPABILITY_MODULES` frozenset honest | unit | `pytest tests/test_guard_sync_version_independent.py::test_capability_mcp_server_frozenset_matches -x` | ❌ Wave 0 |
| SKILL-04 | MCP tool importable, callable | smoke | `pytest tests/test_mcp_import_smoke.py -x` (extend existing) | ❌ extend existing |

### Sampling Rate

- Per task commit: `pytest tests/test_capability_accuracy.py tests/test_guard_sync_version_independent.py -q`
- Per wave merge: `pytest tests/ -q`
- Phase gate: SKILL-02 + guard-sync tests green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_capability_accuracy.py` — covers SKILL-02 (a) and (b)
- [ ] `python/fdars/_capability_map.json` — generated committed dataset (run generator first)
- [ ] `scripts/generate_capability_dataset.py` — the generator itself
- [ ] `.claude/skills/fdars-capabilities/SKILL.md` — new skill (SKILL-01)
- [ ] `docs/llms.txt` — static digest (SKILL-03)
- [ ] `docs/ai-capability-map.md` — in-nav human page (SKILL-03)
- [ ] Extension to `tests/test_guard_sync_version_independent.py` — GATE-04 additions
- [ ] Extension to `tests/test_mcp_import_smoke.py` — add `fdars_list_capabilities` to smoke

---

## Security Domain

`security_enforcement` not explicitly set to false, so this section is included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No auth in this feature |
| V3 Session Management | No | No sessions |
| V4 Access Control | No | Public read-only tool |
| V5 Input Validation | Yes | `fdars_list_capabilities`: validate `module` arg against `_CAPABILITY_MODULES` frozenset before loading JSON |
| V6 Cryptography | No | No cryptography |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `module` arg | Tampering | Frozenset allowlist check before `importlib.resources` load — file path is fixed, not derived from input |
| JSON injection from committed file | Tampering | JSON is committed in-repo (git trust boundary); no user input touches file path |
| LLM-free boundary erosion | Spoofing | Guard test asserts no `provider`/`model` in return value; test runs on every PR |

**Note:** The `module` arg cannot cause path traversal because the JSON file path is
hardcoded (`resources.files('fdars') / '_capability_map.json'`) — the arg only filters
the returned dict keys. The frozenset check prevents invalid module names from even
reaching the JSON parse. [VERIFIED: tool design reviewed]

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual SKILL.md capability tables | Generator-driven from live introspection | Phase 78 | Zero drift between skill and live API |
| No agent-discoverable capability surface | llms.txt + MCP tool + SKILL.md | Phase 78 | Agents can discover fdars capabilities without human docs |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `docs/llms.txt` generated offline and committed (not at build time) | Architecture Patterns, Pitfall 4 | If generated at build time, docs build fails in DOCS_FAST mode |
| A2 | SKILL.md body shows 30-row summary table referencing llms.txt, not full 409-entry inline | Pattern 3 | If inlined, SKILL.md becomes too large for agent context windows |
| A3 | `fdars.plot`, `fdars.results`, `fdars.advisor` excluded from capability map | Generator design | If included, non-duplication boundary with fdars-advisor is blurred |
| A4 | No SKILL.md validator/linter exists in this repo; validated by manual comparison with fdars-advisor/SKILL.md | Pattern 3 | If a validator exists, SKILL.md may fail a required check |
| A5 | llms.txt convention: H1 title, blockquote, ## sections, markdown links | Pattern 5 | If spec changed, the generated file may not be parsed by agents expecting the standard format |

---

## Open Questions

1. **Should `fdars.results` be in the capability map?**
   - What we know: `results.__all__` has 9 entries (wrapper classes + wrap functions)
   - What's unclear: are these user-facing enough to document in the skill?
   - Recommendation: Exclude for now (internal wrapper types); include on request

2. **Should `fdars.plot` be in the capability map?**
   - What we know: `plot.__all__` has 8 plotting functions (`plot_fdata`, etc.)
   - What's unclear: matplotlib dependency makes it optional; not all users have it
   - Recommendation: Exclude from the primary map; note in SKILL.md as an optional extra

3. **Where does `Fdata` class appear in the capability map?**
   - What we know: `fdars.Fdata` is the top-level OOP class, not a submodule
   - What's unclear: should it get its own entry in the capability map?
   - Recommendation: Add a special `"_Fdata"` entry to the generator (class + its public methods)

---

## Wiring + Verification Commands

```bash
# Step 1: Generate the capability dataset
source .venv/bin/activate
python scripts/generate_capability_dataset.py
# Output: python/fdars/_capability_map.json (30 modules, 409 callables)

# Step 2: Run SKILL-02 accuracy tests
pytest tests/test_capability_accuracy.py -q

# Step 3: Run guard-sync tests (Py 3.9+ primary + Py 3.10+ companion)
pytest tests/test_guard_sync_version_independent.py -q

# Step 4: MCP import smoke (after extending test_mcp_import_smoke.py)
pytest tests/test_mcp_import_smoke.py -q

# Step 5: Full suite
pytest tests/ -q

# Note: whole-site mkdocs build is deferred to Phase 79
# docs/llms.txt static passthrough verified: docs/requirements.txt -> site/requirements.txt
```

---

## Sources

### Primary (HIGH confidence)

- [VERIFIED: .venv fdars 0.4.0] — Generator prototype RAN: 30 modules, 409 callables, 0 import errors, stable JSON
- [VERIFIED: python/fdars/__init__.py:40-68] — Authoritative `_submodule_names` tuple (27 native entries)
- [VERIFIED: python/fdars/__init__.py:78-89] — Pure-Python modules: datasets, results, plot, metrics, covariance, advisor
- [VERIFIED: .claude/skills/fdars-advisor/SKILL.md:1-28] — SKILL.md frontmatter schema: name, description, compatibility, allowed-tools
- [VERIFIED: python/fdars/mcp/server.py:32-88] — MCP server pattern: `@mcp.tool()`, `_RUNNABLE_METHODS`, `_DIAGNOSTICS_METHODS` frozensets
- [VERIFIED: tests/test_guard_sync_version_independent.py:38-155] — Guard-sync pattern: hard-coded frozenset + sentinel-parse; Py 3.9 no-mcp constraint
- [VERIFIED: tests/test_mcp_import_smoke.py:29-32] — `pytestmark = pytest.mark.skipif` pattern for Py 3.10+ guard
- [VERIFIED: site/requirements.txt exists] — MkDocs static passthrough confirmed; docs/*.txt → site/*.txt
- [VERIFIED: .venv inspect.signature on all depth/fts/alignment callables] — PyO3 0.28 native callables all expose inspect.signature

### Secondary (MEDIUM confidence)

- [CITED: mkdocs.org] — MkDocs copies all non-Markdown files from docs_dir to site_dir verbatim

### Tertiary (LOW confidence)

- [ASSUMED] — llms.txt convention format (H1, blockquote, ## sections, markdown links)
- [ASSUMED] — docs/llms.txt should be committed as static, not generated at build time

---

## Metadata

**Confidence breakdown:**
- Generator design: HIGH — prototype RAN against live fdars 0.4.0, 0 errors
- SKILL.md schema: HIGH — read from existing spec-valid fdars-advisor/SKILL.md
- MkDocs passthrough: HIGH — confirmed by site/requirements.txt existence
- MCP tool design: HIGH — pattern mirrors existing tools; LLM-free boundary explicit
- Guard-sync tests: HIGH — Py 3.9 constraint verified against existing test source
- llms.txt convention: LOW — training knowledge, not fetched this session

**Research date:** 2026-09-06
**Valid until:** 2026-10-06 (stable codebase; fdars submodule list changes slowly)
