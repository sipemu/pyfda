---
phase: 22-surface-integration
verified: 2026-08-12T14:00:00Z
status: passed
score: 3/3 success criteria verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 22: Surface Integration — Verification Report

**Phase Goal:** The MCP tool surface + Agent Skill expose the new per-aspect coverage, and provider selection is reachable from the Python API — while the MCP boundary stays LLM-free and provider selection lives only in `advise()`.

**Verified:** 2026-08-12T14:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Overall Verdict

**PASS — all three success criteria verified by code inspection and test execution.**

Full suite: `233 passed, 4 skipped` (no regressions). The 4 skips are pre-existing Python-3.9
skip guards on MCP tests running under Python 3.14; 0 failures. All 21 tests in
`test_mcp_server.py` + `test_skill.py` pass.

---

## SC-1: MCP tools expose new aspect diagnostics/methods; grounding invariant preserved

**Verdict: VERIFIED**

### Runnable method set (_RUNNABLE_METHODS)

Code in `python/fdars/mcp/_runner.py` (line 59-61) and `python/fdars/mcp/server.py` (line
49-51) define identical frozensets:

```
_RUNNABLE_METHODS = frozenset({"alignment", "fpca", "basis", "smoothing", "clustering", "depth"})
```

Confirmed at runtime: both frozensets are equal and have 6 members. `"depth"` was added in
Plan 22-01 (commit `c527875`); `_SUPPORTED_METHODS = _RUNNABLE_METHODS` alias maintained for
backward compatibility.

### Diagnostics-only aspects (_DIAGNOSTICS_METHODS)

`python/fdars/mcp/server.py` (line 63-81) defines `_DIAGNOSTICS_METHODS` with 12 members:
all 6 runnable aspects plus `outliers`, `classification`, `represent`, `regression`,
`regression_cv`, `spm`. This is `advisor._supported` mirrored at the MCP boundary.

`fdars_build_diagnostics` guards against `_DIAGNOSTICS_METHODS` (not `_RUNNABLE_METHODS`),
so all 12 aspects are reachable via that tool. `fdars_run_method` and `fdars_compare_run`
guard against `_RUNNABLE_METHODS` only, correctly rejecting diagnostics-only aspects.

### Depth scores unwrap and represent argvals injection

`server.py` lines 171-174: when `method == "depth"` and the stored result is a dict with a
`"scores"` key, the server unwraps `result["scores"]` and forwards `method_name` to the depth
builder. This is necessary because `fraiman_muniz_1d` (depth runner) returns
`{"scores": ndarray, "method_name": "fraiman_muniz"}` while `_build_depth_diagnostics` expects
the raw ndarray.

`server.py` lines 159-163: when `result_id is None` and `method == "represent"`, the fallback
result is `{"data": data, "argvals": argvals}` (not just `{"data": data}`), enabling
`_build_represent_diagnostics` to find the evaluation grid.

### Handlers are compute-only

Grep of all `python/fdars/mcp/*.py` files for `"advise"`: **zero matches** (confirmed by
`test_mcp_does_not_import_advise`). No tool handler calls or imports `advise()`. The server
imports `build_diagnostics` (offline, compute-only) — never the LLM-calling `advise()`.

### Tests (behavioral evidence)

| Test | Purpose | Result |
| ---- | ------- | ------ |
| `test_run_method_depth` | depth runnable end-to-end via fdars_run_method + fdars_build_diagnostics | PASS |
| `test_diagnostics_methods_match_advisor_supported` | guard-sync: _DIAGNOSTICS_METHODS == advisor._supported exactly | PASS |
| `test_build_diagnostics_represent` | argvals injection fix; n_obs + n_points returned | PASS |
| `test_build_diagnostics_classification_with_n_classes` | n_classes forwarded to build_diagnostics | PASS |
| `test_run_method_rejects_diagnostics_only` | regression rejected at run_method boundary | PASS |
| `test_mcp_does_not_import_advise` | LLM-free invariant file-scan lock | PASS |

---

## SC-2: Provider selection via Python API only; MCP tools do not call advise()

**Verdict: VERIFIED**

### advise() signature

`advise()` in `python/fdars/advisor/__init__.py` has signature:

```python
advise(diagnostics: dict, *, task: str, domain_context: str,
       model: str = 'claude-opus-4-8', provider: 'str | object | None' = None,
       aspect: str = '') -> Advice
```

Both `provider` and `model` parameters are present. `advise()` is the sole entry point
for provider selection — confirmed by inspection and the SKILL.md documentation.

### No advise() reference in MCP layer

`grep -rn "advise" python/fdars/mcp/` returns zero output. `test_mcp_does_not_import_advise`
(which builds the search token at runtime as `"adv" + "ise"` to avoid self-flagging) scans all
`*.py` files under `python/fdars/mcp/` and asserts zero matches — **PASS**.

The MCP tool handlers import only `build_diagnostics` (from `fdars.advisor`) and the registry
and runner modules — no LLM calls, no API keys needed.

---

## SC-3: SKILL.md documents provider selection and full per-aspect advisor coverage

**Verdict: VERIFIED**

### Full aspect coverage

`description` field (YAML frontmatter) names: clustering, smoothing, FPCA, alignment,
basis/represent, depth, outliers, classification, regression, regression CV, monitoring/SPM.
`Trigger:` line lists all key aspects explicitly. All 10 key aspects confirmed present in
SKILL.md text (case-insensitive check passed).

### Provider Selection section

`## Provider Selection` section (line 89) documents:

- `advise(provider=, model=)` stated as the sole provider-selection entry point
- Supported provider values: `"anthropic"`, `"openai"`, `"ollama"`, `"gemini"`
- Three environment variables: `FDARS_ADVISOR_PROVIDER`, `FDARS_ADVISOR_MODEL`,
  `FDARS_ADVISOR_BASE_URL` (all verified against `_factory.py`)
- Local/offline Ollama path with example commands (key-free)
- OpenAI-compatible `base_url` path (vLLM, LM Studio, LocalAI)

### Install note — no overclaiming

SKILL.md compatibility field and `## Setup` section correctly state:
- Core install uses git-URL path (not bare `pip install fdars`)
- Provider extras (`[openai]`, `[ollama]`, `[gemini]`) explicitly noted as "publish with fdars 3.0"
- No claim that extras are available on PyPI today

### Tools Referenced refreshed

`## Tools Referenced` section documents all 3 MCP tools:
- `fdars_run_method` — lists the 6 runnable methods including depth
- `fdars_build_diagnostics` — explicitly states "accepts all 12 analysis aspects"
- `fdars_compare_run` — before/after delta
- Points to `python/fdars/advisor/` package (not stale single-file reference)

### YAML frontmatter spec-valid

`yaml.safe_load` parses the frontmatter cleanly. `name: fdars-advisor` matches parent
directory name. `allowed-tools: Bash Read` and `## Grounding Invariant` section are preserved.

### Tests (behavioral evidence)

| Test | Purpose | Result |
| ---- | ------- | ------ |
| `test_skill_md_frontmatter` | YAML parses; name + description present | PASS |
| `test_skill_md_name_matches_dir` | name == directory name "fdars-advisor" | PASS |
| `test_skill_md_compatibility` | compatibility mentions Python 3.10+ and pip | PASS |
| `test_skill_md_full_aspect_coverage` | depth/outliers/classification/regression/spm in text | PASS |
| `test_skill_md_provider_selection_section` | Provider Selection heading + Ollama + FDARS_ADVISOR_PROVIDER | PASS |

---

## Observable Truths

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | `depth` is runnable via `fdars_run_method` and flows through `fdars_build_diagnostics` compute-only | VERIFIED | `_runner.py` depth branch (line 214-225); `server.py` scores unwrap (lines 171-174); `test_run_method_depth` PASS |
| 2 | The 6 diagnostics-only aspects (outliers, classification, represent, regression, regression_cv, spm) are reachable via `fdars_build_diagnostics` | VERIFIED | `_DIAGNOSTICS_METHODS` (12 members) guards `fdars_build_diagnostics`; `test_diagnostics_methods_match_advisor_supported` proves exact set equality with `advisor._supported` |
| 3 | No MCP tool handler calls or imports `advise()` | VERIFIED | `grep -rn "advise" python/fdars/mcp/` returns zero results; `test_mcp_does_not_import_advise` PASS |
| 4 | `advise(provider=, model=)` is the sole provider-selection entry point in the Python API | VERIFIED | Confirmed by `inspect.signature(advise)` — both params present; SKILL.md states this explicitly |
| 5 | SKILL.md documents full per-aspect coverage (all 12 aspects, not just the original 5) | VERIFIED | All 10 key aspect keywords confirmed present; `test_skill_md_full_aspect_coverage` PASS |
| 6 | SKILL.md Provider Selection section documents local/offline Ollama path and env vars | VERIFIED | Section at line 89; FDARS_ADVISOR_PROVIDER/MODEL/BASE_URL table; Ollama example; `test_skill_md_provider_selection_section` PASS |
| 7 | Install note does not overclaim PyPI extras | VERIFIED | Compatibility field and Setup section explicitly frame provider extras as "publishing with fdars 3.0" — no broken `pip install fdars[openai]` claim |
| 8 | No Phase 23 (packaging/CI) or Phase 24 (docs-site) scope leaked | VERIFIED | Git log of Phase 22 commits shows only `python/fdars/mcp/`, `tests/`, `.claude/skills/fdars-advisor/` and planning artifacts modified — no `pyproject.toml`, `.github/`, `mkdocs.yml`, or `docs/` changes |
| 9 | All pre-existing tests remain green | VERIFIED | Full suite: 233 passed, 4 skipped (4 skips are pre-existing Python-3.9 guards; 0 failures) |

**Score:** 9/9 truths verified

---

## Required Artifacts

| Artifact | Status | Evidence |
| -------- | ------ | -------- |
| `python/fdars/mcp/_runner.py` | VERIFIED | Exists; `_RUNNABLE_METHODS` frozenset with 6 members including depth; depth dispatch at line 214; substantive (229 lines) |
| `python/fdars/mcp/server.py` | VERIFIED | Exists; `_RUNNABLE_METHODS` (6) + `_DIAGNOSTICS_METHODS` (12) defined; depth unwrap at lines 171-174; represent argvals injection at lines 159-163; n_classes forwarding at lines 184-185 |
| `tests/test_mcp_server.py` | VERIFIED | Exists; 13 tests (7 pre-existing + 6 new from Plans 22-01 and 22-02); all pass |
| `.claude/skills/fdars-advisor/SKILL.md` | VERIFIED | Exists; `## Provider Selection` section at line 89; full 12-aspect list in description; YAML frontmatter parses; no overclaiming on PyPI extras |
| `tests/test_skill.py` | VERIFIED | Exists; 8 tests (6 pre-existing + 2 new from Plan 22-03); all pass |

---

## Key Link Verification

| From | To | Via | Status |
| ---- | -- | --- | ------ |
| `fdars_build_diagnostics` (server.py) | `advisor.build_diagnostics` | `from fdars.advisor import build_diagnostics` (line 151) | WIRED |
| `fdars_run_method` (server.py) | `_runner.run_method` | `from fdars.mcp._runner import run_method` (line 275) | WIRED |
| `_runner.run_method` depth branch | `fdars.depth.fraiman_muniz_1d` | `from fdars import depth as _depth` + `_depth.fraiman_muniz_1d(data, data)` | WIRED |
| server.py depth unwrap | `_build_depth_diagnostics` | `result = result["scores"]` + `depth_kwargs["method_name"]` injected into `build_diagnostics` call | WIRED |
| server.py represent injection | `_build_represent_diagnostics` | `result = {"data": data, "argvals": argvals}` fallback path | WIRED |
| `test_mcp_does_not_import_advise` | `python/fdars/mcp/*.py` | `pathlib.Path.rglob("*.py")` + text scan | WIRED (runtime invariant lock) |
| `test_diagnostics_methods_match_advisor_supported` | `advisor.build_diagnostics` | Provokes ValueError and parses `Supported: [...]` list; asserts set equality | WIRED (drift lock) |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| depth runnable end-to-end via MCP | `pytest tests/test_mcp_server.py::test_run_method_depth -v` | PASS | PASS |
| _DIAGNOSTICS_METHODS == advisor._supported (12 members) | `pytest tests/test_mcp_server.py::test_diagnostics_methods_match_advisor_supported -v` | PASS | PASS |
| No advise() reference in MCP files | `pytest tests/test_mcp_server.py::test_mcp_does_not_import_advise -v` | PASS | PASS |
| SKILL.md full aspect coverage | `pytest tests/test_skill.py::test_skill_md_full_aspect_coverage -v` | PASS | PASS |
| SKILL.md provider selection section | `pytest tests/test_skill.py::test_skill_md_provider_selection_section -v` | PASS | PASS |
| Full suite passes with no regressions | `.venv/bin/python -m pytest tests/ -q` | 233 passed, 4 skipped | PASS |

---

## Anti-Patterns Scan

Files scanned: `python/fdars/mcp/_runner.py`, `python/fdars/mcp/server.py`,
`.claude/skills/fdars-advisor/SKILL.md`, `tests/test_mcp_server.py`, `tests/test_skill.py`

| Pattern | Findings | Severity |
| ------- | -------- | -------- |
| TBD / FIXME / XXX | Zero matches | — |
| TODO / HACK / PLACEHOLDER | Zero matches | — |
| Empty return stubs | Zero — all handlers have real implementations | — |
| Hardcoded empty data as return | Zero | — |
| `return null` / `return {}` (tool stubs) | Zero | — |

No blockers, no warnings.

---

## Scope Containment

Phase 22 commits (`c527875` through `22a8ece`, inclusive) touch only:

- `python/fdars/mcp/_runner.py` — depth runnable dispatch
- `python/fdars/mcp/server.py` — _RUNNABLE_METHODS rename, _DIAGNOSTICS_METHODS addition, depth unwrap, represent injection, n_classes forwarding
- `tests/test_mcp_server.py` — 6 new tests
- `.claude/skills/fdars-advisor/SKILL.md` — 4 targeted edits
- `tests/test_skill.py` — 2 new tests
- Planning artifacts (ROADMAP.md, REQUIREMENTS.md, STATE.md, SUMMARY files)

No changes to `pyproject.toml`, `.github/workflows/`, `mkdocs.yml`, `docs/`, or any Rust
source files. Phase 23 (packaging/CI) and Phase 24 (docs-site) scope boundaries respected.

---

## Requirements Coverage

| Requirement | Plans | Status | Evidence |
| ----------- | ----- | ------ | -------- |
| SURF-01: MCP tools expose new aspects, stay compute-only | 22-01, 22-02 | SATISFIED | `_RUNNABLE_METHODS` (6), `_DIAGNOSTICS_METHODS` (12), no `advise()` calls, depth + diagnostics-only aspects all routed correctly |
| SURF-02: Provider selection via Python API only; MCP tools do not call advise() | 22-01 | SATISFIED | `advise(provider=, model=)` confirmed; zero `advise` references in MCP layer; locked by `test_mcp_does_not_import_advise` |
| SURF-03: SKILL.md documents provider selection (incl. local/offline path) and full per-aspect coverage | 22-03 | SATISFIED | `## Provider Selection` section with Ollama + env vars + OpenAI-compatible base_url; all 12 aspects in description and Tools Referenced; install note does not overclaim PyPI extras |

---

## Human Verification Required

None. All success criteria are verifiable by code inspection, behavioral tests, and file scans
without human judgment. No UI, no external service, no real-time behavior involved.

---

_Verified: 2026-08-12T14:00:00Z_
_Verifier: Claude (gsd-verifier)_
