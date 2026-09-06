---
phase: 78-ai-capability-discovery-skill
verified: 2026-09-06T00:00:00Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 78: AI Capability Discovery Skill Verification Report

**Phase Goal:** AI agents can discover the whole fdars capability surface across three selected surfaces — a standalone Agent Skill, an LLM-oriented docs page, and an LLM-free MCP capability tool — distinct from and non-duplicating the existing narrow fdars-advisor skill/MCP.
**Verified:** 2026-09-06
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python scripts/generate_capability_dataset.py` reproduces the committed `_capability_map.json` byte-for-byte (SKILL-02) | ✓ VERIFIED | `git diff --quiet python/fdars/_capability_map.json` → clean; generator runs to completion outputting "Written 31 modules (437 callables)" |
| 2 | Every callable in `_capability_map.json` is importable via `fdars.<module>.<fn>` (SKILL-02) | ✓ VERIFIED | `test_capability_map_all_importable` PASSED; `test_capability_curation_keys_resolve` PASSED (WR-01 fix) |
| 3 | Map excludes advisor/plot/results and includes `_Fdata` entry (SKILL-02 non-duplication boundary) | ✓ VERIFIED | Python check: `_Fdata` in keys, `{'advisor','plot','results'} & keys == empty`; 31 top-level entries |
| 4 | `.claude/skills/fdars-capabilities/SKILL.md` has spec-valid frontmatter (name, description, compatibility, allowed-tools) with explicit disjoint boundary from fdars-advisor (SKILL-01) | ✓ VERIFIED | Frontmatter YAML parses with all 4 keys; name == `fdars-capabilities`; description contains "fdars-advisor" and "Do NOT use" pattern |
| 5 | SKILL.md body maps every public fdars module via map-grounded overview table, references docs/llms.txt + fdars_list_capabilities MCP tool, stays a summary not a full dump (SKILL-01) | ✓ VERIFIED | 30 `fdars.<mod>` mentions all in map keys (0 phantom); `llms.txt` referenced; `fdars_list_capabilities` referenced; 30 call sites < 100 threshold |
| 6 | `docs/llms.txt` follows llms.txt convention (H1, blockquote, module sections) and lists every capability-map module (SKILL-03) | ✓ VERIFIED | H1 present; blockquote present; all 30 non-`_`-prefixed map modules present in file; 62,262 chars |
| 7 | `docs/ai-capability-map.md` is in-nav in mkdocs.yml, valid Markdown, non-empty (SKILL-03) | ✓ VERIFIED | `mkdocs.yml` references `ai-capability-map.md` exactly once; YAML parses valid; file 64,398 chars; backtick fence count is even |
| 8 | Both docs artifacts regenerate deterministically from `_capability_map.json` — no git diff on re-run (SKILL-03) | ✓ VERIFIED | `python scripts/generate_capability_dataset.py --llmstxt && git diff --quiet docs/llms.txt docs/ai-capability-map.md` → clean |
| 9 | `fdars_list_capabilities` MCP tool: registered, LLM-free (no provider/model keys, no model call), allowlist-validated, filtered, version dynamic (SKILL-04) | ✓ VERIFIED | Tool returns `{modules, version, module_count, callable_count}`; no provider/model keys; module="depth" slices; bogus module raises ValueError listing knowns; version matches `fdars.__version__ == 0.4.0` dynamically (WR-02 fix confirmed) |
| 10 | Guard-sync extended: Py3.9-safe primary (JSON keys == frozenset, no mcp import) + Py3.10+ LLM-free companion + three-way literal mirror; existing advisor/MCP tests unchanged (SKILL-04/GATE-04) | ✓ VERIFIED | All 9 tests pass: 3 capability-accuracy + 5 guard-sync (incl. 3 new GATE-04 tests) + 1 smoke; 67 advisor/MCP regression tests pass; three-way mirror: `_EXPECTED_CAPABILITY_MODULES == _CAPABILITY_MODULES == map submodule keys` all 30 entries |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/generate_capability_dataset.py` | Introspects live fdars → byte-stable JSON | ✓ VERIFIED | Exists; 437 callables / 31 modules; byte-stable on regenerate; --llmstxt path for docs emit; lazy fdars import for docs-build independence |
| `python/fdars/_capability_map.json` | 31-entry committed map (30 modules + _Fdata, 437 callables) | ✓ VERIFIED | Exists; 31 top-level keys; excludes advisor/plot/results; 20 `when` fields merged from curation |
| `python/fdars/_capability_curation.json` | Hand-authored when-to-use guidance, >=6 entries, all <=120 chars | ✓ VERIFIED | Exists; 27 entries (all <=120 chars); no stale keys (test_capability_curation_keys_resolve passes) |
| `tests/test_capability_accuracy.py` | SKILL-02: no-drift + all-importable + stale-curation guard; no mcp import | ✓ VERIFIED | 3 tests all pass; no mcp import at module level (Py3.9-safe); WR-01 stale-curation guard present and green |
| `.claude/skills/fdars-capabilities/SKILL.md` | Spec-valid frontmatter, disjoint trigger, map-grounded body | ✓ VERIFIED | Exists; 4 frontmatter keys; name=fdars-capabilities; disjoint boundary present; body grounded |
| `docs/llms.txt` | llms.txt convention, all modules, offline-generated, committed | ✓ VERIFIED | Exists; 62 KB; H1 + blockquote + module sections; all 30 modules present; byte-stable on regen |
| `docs/ai-capability-map.md` | Valid Markdown, in-nav, non-empty | ✓ VERIFIED | Exists; 64 KB; wired in mkdocs.yml nav; valid markdown (no unclosed fences) |
| `python/fdars/mcp/server.py` (fdars_list_capabilities + _CAPABILITY_MODULES) | LLM-free tool, frozenset, additive-only | ✓ VERIFIED | Tool registered after fdars_auto_tune; _CAPABILITY_MODULES = 30 submodule keys; _RUNNABLE_METHODS and _DIAGNOSTICS_METHODS unchanged (2 defs each) |
| `tests/test_guard_sync_version_independent.py` (GATE-04 extensions) | _EXPECTED_CAPABILITY_MODULES + 3 new tests, no module-level mcp import | ✓ VERIFIED | 5 guard tests total (2 existing + 3 new GATE-04); no module-level mcp import; all green |
| `tests/test_mcp_import_smoke.py` (fdars_list_capabilities added) | All 7 MCP tools covered | ✓ VERIFIED | All 7 tools in expected_tool_names; WR-03 fix confirmed; 1 test passes |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `generate_capability_dataset.py` | `python/fdars/_capability_map.json` | introspects live fdars `__all__` + inspect.signature → sorted JSON | ✓ WIRED | Generator runs clean; no drift on regenerate |
| `generate_capability_dataset.py --llmstxt` | `docs/llms.txt` + `docs/ai-capability-map.md` | reads committed `_capability_map.json` (offline, no fdars import) | ✓ WIRED | Both files byte-stable on regen; lazy fdars import verified |
| `_capability_map.json` | `SKILL.md` body table | module names in body all exist as map keys (no phantom modules) | ✓ WIRED | 30 `fdars.<mod>` mentions all validated against map keys |
| `_capability_map.json` | `mkdocs.yml` nav | `ai-capability-map.md` nav entry present | ✓ WIRED | Exactly 1 reference in mkdocs.yml; YAML parses valid |
| `_capability_map.json` | `fdars_list_capabilities` | importlib.resources load in tool body | ✓ WIRED | Tool loads at call time via `importlib.resources.files('fdars') / '_capability_map.json'` |
| `_CAPABILITY_MODULES` (server) | `_EXPECTED_CAPABILITY_MODULES` (test) | three-way literal mirror: server frozenset == JSON submodule keys == test frozenset | ✓ WIRED | All three = 30 entries; `test_capability_mcp_server_frozenset_matches` passes |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `fdars_list_capabilities` | `modules` dict | `importlib.resources.files('fdars') / '_capability_map.json'` (committed JSON, no model call) | Yes — real introspected API surface | ✓ FLOWING |
| `docs/llms.txt` | Module/callable listing | `python/fdars/_capability_map.json` via `--llmstxt` path (offline, committed, deterministic) | Yes — 30 modules, 409 callables | ✓ FLOWING |
| `SKILL.md` body table | Module overview rows | derived from `_capability_map.json` keys at author time | Yes — 30 map-grounded rows | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Generator runs clean + map byte-stable | `.venv/bin/python scripts/generate_capability_dataset.py && git diff --quiet python/fdars/_capability_map.json` | exit 0; "Written 31 modules (437 callables)" | ✓ PASS |
| SKILL-02 accuracy tests | `.venv/bin/pytest tests/test_capability_accuracy.py -q` | 3 passed in 0.33s | ✓ PASS |
| Docs-emit stable on regen | `.venv/bin/python scripts/generate_capability_dataset.py --llmstxt && git diff --quiet docs/llms.txt docs/ai-capability-map.md` | exit 0 | ✓ PASS |
| GATE-04 guard-sync + smoke tests | `.venv/bin/pytest tests/test_guard_sync_version_independent.py tests/test_mcp_import_smoke.py -q` | 6 passed in 0.73s + 1 passed in 0.75s (9 total) | ✓ PASS |
| MCP tool LLM-free + allowlist + filter | Python import + call fdars_list_capabilities | Returns {modules,version,module_count,callable_count}; no provider/model keys; module="depth" slices; bogus raises ValueError | ✓ PASS |
| Version dynamic (WR-02 fix) | tool `version` == `fdars.__version__` | Both == "0.4.0" (dynamic) | ✓ PASS |
| Advisor/MCP regression | `.venv/bin/pytest tests/test_mcp_server.py tests/test_advisor_grounding.py -q` | 67 passed in 87.86s | ✓ PASS |
| Three-way literal mirror | Python: `_EXPECTED == _CAPABILITY_MODULES == map_keys` | All 30 entries match | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SKILL-01 | 78-02 | Standalone capability-discovery Agent Skill with spec-valid SKILL.md | ✓ SATISFIED | `.claude/skills/fdars-capabilities/SKILL.md` exists, frontmatter valid, body map-grounded, disjoint boundary present |
| SKILL-02 | 78-01 | Capability map accuracy test — documented methods exist and importable | ✓ SATISFIED | `tests/test_capability_accuracy.py` — 3 tests pass (no-drift, all-importable, stale-curation guard) |
| SKILL-03 | 78-03 | LLM-oriented docs page (llms.txt-style digest) wired into site | ✓ SATISFIED | `docs/llms.txt` (H1+blockquote+sections, 62KB) + `docs/ai-capability-map.md` (64KB) in mkdocs.yml nav |
| SKILL-04 | 78-04 | LLM-free MCP capability tool; guard/tests updated | ✓ SATISFIED | `fdars_list_capabilities` registered; no model call; GATE-04 guard-sync 3 new tests; all 9 tests pass |

Note: GATE-04 (final MCP LLM-free confirmation + whole-site `--strict` build) is explicitly deferred to Phase 79 per all four plan verification sections.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `scripts/generate_capability_dataset.py` | 104 | "literal placeholder" in docstring | ℹ️ Info | Describes the `'(...)'` fallback sig used when inspect.signature is unavailable — not a code stub; benign docstring text |

No TBD/FIXME/XXX markers in any phase-modified file. No unresolved debt markers.

### Code Review Findings (78-REVIEW.md) — Confirmed Resolved

All 5 findings from 78-REVIEW.md confirmed resolved in commit 9bd2ea7:

| Finding | Resolution | Confirmed |
|---------|------------|-----------|
| WR-01: Stale curation keys had no test | `test_capability_curation_keys_resolve` added; caught 8 real stale keys (corrected to live names) | ✓ Test passes; 0 stale curation keys |
| WR-02: Hardcoded "0.4.0" version in tool | `fdars.__version__` read dynamically | ✓ tool version == fdars.__version__ == "0.4.0" |
| WR-03: Smoke test missed 3 tools | All 7 tools now in expected_tool_names | ✓ compare_methods, build_pipeline_report, auto_tune all present |
| IN-01: Unused sys/Path imports | Removed from test_capability_accuracy.py | ✓ Neither import found in file |
| IN-02: Generator docstring overstated protection | Original false claim removed; stale curation behavior now documented | ✓ Original claim absent from file |

---

_Verified: 2026-09-06_
_Verifier: Claude (gsd-verifier)_
