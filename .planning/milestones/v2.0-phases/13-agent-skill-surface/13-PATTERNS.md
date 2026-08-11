---
phase: 13-agent-skill-surface
type: PATTERNS
date: 2026-08-10
---

# Phase 13: Agent Skill Surface — Pattern Map

**Mapped:** 2026-08-10
**Files analyzed:** 3 new files
**Analogs found:** 3 / 3

---

## File Classification

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `.claude/skills/fdars-advisor/SKILL.md` | config/manifest | request-response | `~/.claude/skills/graphify/SKILL.md` | role-match (same format spec) |
| `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py` | utility/script | request-response | `examples/mcp_recipe.py` | exact |
| `tests/test_skill.py` | test | request-response | `tests/test_mcp_server.py` | role-match |

---

## Pattern Assignments

### `.claude/skills/fdars-advisor/SKILL.md` (config/manifest, request-response)

**Analog:** `~/.claude/skills/graphify/SKILL.md`

The graphify SKILL.md uses a minimal frontmatter with `name`, `description`, and `trigger` fields. The agentskills.io spec (confirmed in RESEARCH.md) differs from that private convention: it requires `name` + `description` and permits `compatibility` and `allowed-tools`. The graphify skill demonstrates the progressive-disclosure body structure (workflow steps as numbered headings with fenced bash blocks).

**Frontmatter pattern** (graphify SKILL.md lines 1-5):
```yaml
---
name: graphify
description: any input (code, docs, papers, images) → knowledge graph → clustered communities → HTML + JSON + audit report
trigger: /graphify
---
```

**For fdars-advisor**, use the agentskills.io-compliant form from RESEARCH.md Pattern 1 instead (the graphify skill predates the spec and uses a non-standard `trigger` field):

```yaml
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
```

**Body structure pattern** (graphify SKILL.md lines 8-35 — progressive-disclosure approach):
- Top-level `## Usage` section with one-liner invocations
- `## What [skill] is for` explaining trigger scenarios
- `## What You Must Do When Invoked` with numbered Steps
- Each step contains a fenced `bash` block with executable code

**Apply to fdars-advisor body:** Same structure: `## Setup` → `## Offline Walkthrough` → `## Grounded Advice` → `## Grounding Invariant`. Keep body under 100 lines (graphify is ~1200 lines because it IS the implementation; fdars-advisor delegates to the script).

---

### `.claude/skills/fdars-advisor/scripts/fdars_advisor_walkthrough.py` (utility, request-response)

**Analog:** `examples/mcp_recipe.py`

**Module docstring pattern** (mcp_recipe.py lines 1-27):
```python
"""fdars MCP advisor — end-to-end compare recipe.

Demonstrates the full MCP tool workflow (register → run → compare) against
the Canadian Weather dataset, using the ``fdars.mcp`` helpers directly
(no live MCP transport required for the script — transport is only needed
when driving the tools from a language model via stdio).

Steps:

  1. Load the Canadian Weather dataset ...
  2. Run the ``smoothing`` method ...
  3. Compare: re-run smoothing with n_basis=25 via ``compare_run``.
  4. Print the observable ``delta`` ...

Run (offline — no API key; requires Python >=3.10):

    pip install "fdars[mcp]"
    python examples/mcp_recipe.py
"""
```

**Imports and version guard pattern** (mcp_recipe.py lines 29-51):
```python
from __future__ import annotations

import sys

# ---------------------------------------------------------------------------
# Python version guard — mcp requires >=3.10; exit 0 gracefully on 3.9
# ---------------------------------------------------------------------------

if sys.version_info < (3, 10):
    print(
        "Python 3.10+ required for fdars[mcp] (mcp>=2.0.0 does not support 3.9).\n"
        "This script will be skipped. "
        "Upgrade to Python 3.10+ and re-run:\n"
        "    pip install 'fdars[mcp]' && python examples/mcp_recipe.py"
    )
    sys.exit(0)

import numpy as np

from fdars import datasets
from fdars.mcp._registry import registry
from fdars.mcp._runner import run_method
from fdars.mcp._compare import compare_run
```

**Dataset load + registry pattern** (mcp_recipe.py lines 57-67):
```python
ds = datasets.load_canadian_weather()

# ds.data is an Fdata object (35 stations × 365 daily observations)
X = np.asarray(ds.data.data, dtype=float)    # shape (35, 365)
day = np.asarray(ds.argvals, dtype=float)    # shape (365,) — day-of-year grid

dataset_id = registry.store_dataset(X, day)
```

**run_method + store_result pattern** (mcp_recipe.py lines 73-77):
```python
before_result = run_method(dataset_id, "smoothing", n_basis=15)
before_result_id = registry.store_result(before_result)
print(f"  Before result handle: {before_result_id}")
print(f"  GCV (before): {before_result.get('gcv', 'n/a'):.6f}")
```

**compare_run pattern** (mcp_recipe.py lines 85-90):
```python
compare_result = compare_run(
    dataset_id,
    "smoothing",
    before_result_id,
    {"n_basis": 25},
)
```

**Delta printing loop** (mcp_recipe.py lines 110-117):
```python
delta = compare_result["delta"]
print(f"\n  Delta (after - before) [{len(delta)} scalar keys]:")
if delta:
    for k, v in delta.items():
        sign = "+" if v >= 0 else ""
        print(f"    {k}: {sign}{v:.6f}")
else:
    print("    (no scalar finite keys in common)")
```

**Addition for walkthrough (no analog in mcp_recipe.py — use RESEARCH.md Pattern 5):**
```python
# At top of main(), after registry import:
registry.clear()   # Pitfall 7: clear singleton between runs

# After before_result is obtained — env-gated LLM step:
from fdars.advisor import build_diagnostics, advise
import os

diagnostics = build_diagnostics(before_result, "smoothing")
if os.environ.get("ANTHROPIC_API_KEY"):
    advice = advise(
        diagnostics,
        task="parameter",
        domain_context="35 Canadian weather stations, daily temperature curves",
    )
    # print advice.interpretation, advice.recommendations, advice.caveats
else:
    print("[offline] ANTHROPIC_API_KEY not set — skipping advise()")
```

**Wrap in main() function** (CLAUDE.md convention — private helpers prefixed with underscore; public entry point named `main`):
```python
def main() -> None:
    """Run the fdars advisor walkthrough end-to-end."""
    # ... all steps ...

if __name__ == "__main__":
    main()
```

---

### `tests/test_skill.py` (test, request-response)

**Analog:** `tests/test_mcp_server.py`

**Module docstring pattern** (test_mcp_server.py lines 1-20):
```python
"""Tests for the fdars MCP server surface (Plans 12-01, 12-02, and 12-03).

Requires: fdars[mcp] (mcp>=2.0.0, Python >=3.10) and pytest-asyncio.

All tests in this module are skipped on Python <3.10 via the module-level
``pytestmark``.  No ``ANTHROPIC_API_KEY`` and no network are required.
"""
```

**Version-skip pattern** (test_mcp_server.py lines 34-37):
```python
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="mcp requires Python 3.10+",
)
```

**Registry-clear autouse fixture** (test_mcp_server.py lines 44-49):
```python
@pytest.fixture(autouse=True)
def _clear_registry():
    """Reset the handle registry after every test to prevent state leakage."""
    yield
    from fdars.mcp._registry import registry
    registry.clear()
```

**Canadian weather fixture** (test_mcp_server.py lines 57-66):
```python
@pytest.fixture()
def canadian_weather():
    from fdars import datasets
    ds = datasets.load_canadian_weather()
    X = np.asarray(ds.data.data, dtype=float)
    day = np.asarray(ds.argvals, dtype=float)
    return X, day
```

**Delta structural assertion pattern** (test_mcp_server.py lines 386-396):
```python
assert "before" in result, f"'before' key missing from {list(result.keys())}"
assert "after" in result, f"'after' key missing from {list(result.keys())}"
assert "delta" in result, f"'delta' key missing from {list(result.keys())}"
delta = result["delta"]
assert isinstance(delta, dict), f"delta is not a dict: {type(delta)}"
assert len(delta) > 0, "delta dict is empty — expected at least one scalar diff"
```

**Delta sign/value assertion pattern** (test_mcp_server.py lines 400-439 paraphrased):
```python
# Assert a known scalar key has the expected sign
assert delta.get("optimal_edf", 0) > 0, (
    f"Expected positive edf delta (more basis → more edf), got {delta}"
)
```

**For test_skill.py specifically — new test functions needed (no analog exists):**
- `test_skill_md_frontmatter`: read `.claude/skills/fdars-advisor/SKILL.md`, parse YAML frontmatter with `yaml.safe_load` after stripping the `---` fence, assert `name == "fdars-advisor"` and `description` is non-empty string.
- `test_skill_md_compatibility`: assert `"3.10"` (or `"Python"`) appears in the `compatibility` field.
- `test_walkthrough_script_offline`: invoke the walkthrough script via `subprocess.run([sys.executable, str(SCRIPT_PATH)], capture_output=True, timeout=120)`, assert `returncode == 0`.
- `test_walkthrough_delta_nonempty`: parse stdout of the subprocess call above, assert the line `"Delta ("` appears and at least one `": "` follows it (i.e., delta is non-empty).

YAML parsing approach (no external dependency — PyYAML ships with Python's stdlib-adjacent packages, but to avoid assuming it, use a simple regex split on `---` and parse with `yaml.safe_load` which is part of PyYAML, already available in `.venv`):
```python
import pathlib, re, yaml

SKILL_MD = pathlib.Path(".claude/skills/fdars-advisor/SKILL.md")

def _parse_frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert m, "No YAML frontmatter found"
    return yaml.safe_load(m.group(1))
```

---

## Shared Patterns

### Python 3.10 Version Guard
**Source:** `examples/mcp_recipe.py` lines 37-44
**Apply to:** `fdars_advisor_walkthrough.py` (before any `fdars.mcp` import), `tests/test_skill.py` (module-level `pytestmark`)

```python
# Script version (walkthrough):
if sys.version_info < (3, 10):
    print(
        "Python 3.10+ required for fdars[mcp] (mcp>=2.0.0 does not support 3.9).\n"
        "This script will be skipped."
    )
    sys.exit(0)

# Test version (test_skill.py):
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="mcp requires Python 3.10+",
)
```

### Registry Clear (Singleton Reset)
**Source:** `tests/test_mcp_server.py` lines 44-49; also mandated by RESEARCH.md Pitfall 7
**Apply to:** `fdars_advisor_walkthrough.py` (call `registry.clear()` at top of `main()`), `tests/test_skill.py` (autouse fixture)

```python
# Script — at top of main():
from fdars.mcp._registry import registry
registry.clear()

# Test autouse fixture:
@pytest.fixture(autouse=True)
def _clear_registry():
    yield
    from fdars.mcp._registry import registry
    registry.clear()
```

### `from __future__ import annotations`
**Source:** `examples/mcp_recipe.py` line 29; `tests/test_mcp_server.py` line 23
**Apply to:** Both new Python files (CLAUDE.md convention)

### ANTHROPIC_API_KEY Environment Gate
**Source:** RESEARCH.md Pattern 5 (no exact analog in repo yet — first use)
**Apply to:** `fdars_advisor_walkthrough.py`

```python
import os
RUN_LLM = bool(os.environ.get("ANTHROPIC_API_KEY"))
if RUN_LLM:
    advice = advise(diagnostics, task="parameter", ...)
else:
    print("[offline] ANTHROPIC_API_KEY not set — skipping advise()")
```

### Separator Comments for Script Sections
**Source:** `examples/mcp_recipe.py` throughout (e.g., lines 52-55)
**Apply to:** `fdars_advisor_walkthrough.py`

```python
# ---------------------------------------------------------------------------
# Step N: <description>
# ---------------------------------------------------------------------------
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| (none) | — | — | All three files have close analogs |

**Note on partial gaps:**
- `test_skill_md_frontmatter` / `test_skill_md_compatibility` have no direct analog (no existing SKILL.md parse tests in repo). Use the `yaml.safe_load` + `re.match` approach described above.
- The `advise()` call in the walkthrough has no existing script analog (only test coverage in `tests/test_advisor.py`). The RESEARCH.md Pattern 5 is the authoritative reference for this.

---

## Key Constraints for Planner

1. **Version guard position is critical:** The version guard (`if sys.version_info < (3, 10)`) MUST appear before any `from fdars.mcp import ...` line in the walkthrough script. This matches `mcp_recipe.py` exactly.
2. **Install step must use git-URL form:** `pip install "fdars @ git+https://github.com/sipemu/pyfda" mcp>=2.0.0 anthropic>=0.72.0 pydantic>=2.0` — not `pip install "fdars[mcp]"` until PyPI 0.3.0 ships.
3. **Directory name must match `name:` field:** `.claude/skills/fdars-advisor/` → `name: fdars-advisor`.
4. **Script wraps in `main()`:** CLAUDE.md convention requires a named entry-point function; `mcp_recipe.py` uses module-level statements, but the walkthrough should use `def main()` (CLAUDE.md: "Private helpers prefixed with underscore").
5. **Delta keys are known:** The deterministic 4-key delta from the verified run (RESEARCH.md Walkthrough Determinism section): `gcv_aic_approx`, `gcv_bic_approx`, `optimal_gcv`, `optimal_edf`. The test `test_walkthrough_delta_nonempty` can assert `len(delta) >= 1`; the sign test can assert `optimal_edf > 0` for n_basis 15→25.

---

## Metadata

**Analog search scope:** `examples/`, `tests/`, `~/.claude/skills/`
**Files scanned:** `examples/mcp_recipe.py`, `tests/test_mcp_server.py` (lines 1-80, 360-439), `~/.claude/skills/graphify/SKILL.md` (lines 1-50)
**Pattern extraction date:** 2026-08-10
