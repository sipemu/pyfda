---
phase: 10-advisor-core-primitive
plan: "01"
subsystem: advisor
tags: [python, llm, pydantic, anthropic, fda, alignment, offline-first]
status: complete

dependency_graph:
  requires: []
  provides:
    - python/fdars/advisor.py
    - Advice schema (Pydantic + offline fallback)
    - build_diagnostics(alignment) — offline, deterministic
    - advise() — grounded LLM call via client.messages.parse
    - _require_anthropic() — ImportError guard for CORE-04
    - ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0" — Phase 10 open decision resolved
  affects:
    - python/fdars/ (new module, not yet registered in __init__.py — Phase 11)

tech_stack:
  added:
    - pydantic (optional; fallback stubs defined inline for offline use)
    - anthropic>=0.72.0 (optional; gated behind _require_anthropic())
  patterns:
    - offline-first diagnostics builder (no LLM/network in build_diagnostics)
    - lazy import guard (_require_anthropic) for optional heavy dependency
    - Pydantic structured output via client.messages.parse(output_format=Advice)
    - grounding invariant enforced by schema (required evidence[]) + system prompt

key_files:
  created:
    - python/fdars/advisor.py
  modified: []

decisions:
  - "ADVISOR_ANTHROPIC_MIN_VERSION = '0.72.0' — RESOLVED Phase 10 open decision: minimum anthropic SDK version supporting messages.parse + claude-opus-4-8"
  - "Pydantic offline fallback: define plain Python stand-in classes (Recommendation, Advice) when pydantic is not installed, so importing fdars.advisor and calling build_diagnostics work fully offline without [advisor] extra"
  - "build_diagnostics uses lazy import of fdars.alignment inside the function body — advisor import never forces a heavy import chain"
  - "advise() uses adaptive thinking: thinking={'type': 'adaptive'} per design doc"
  - "pyproject.toml, __init__.py, and tests untouched — deferred to Phase 11 per plan"

metrics:
  duration: "3 minutes"
  completed: "2026-08-09T18:23:00Z"
  tasks_completed: 3
  commits: 1

actuals:
  tokens: 3975
  tasks: 3
  commits: 1
---

# Phase 10 Plan 01: Advisor Core Primitive Summary

Delivered `python/fdars/advisor.py` — the end-to-end tracer for the fdars AI advisor: Pydantic schema + deterministic offline diagnostics for alignment + grounded Claude call via `client.messages.parse`.

## What Was Built

### python/fdars/advisor.py (531 lines, new file)

**Schema (Task 1 — tracer):**
- `Recommendation` model: `action`, `kind` (`Literal["parameter","method","none"]`), `rationale`, `expected_effect`, `evidence: list[str]`
- `Advice` model: `interpretation`, `recommendations: list[Recommendation]`, `caveats: list[str]`
- Both defined via Pydantic when available; plain Python stand-in classes when pydantic is absent — so importing advisor and calling `build_diagnostics` work without any optional dependency installed (CORE-04)

**Offline diagnostics builder (Task 1 — tracer):**
- `build_diagnostics(result, method, *, argvals=None, **kwargs) -> dict`
  - Alignment branch: Karcher/template mean summary (length, min, max, avg, curve), per-observation amplitude_distance and phase_distance vs the mean (via lazy `from fdars import alignment` inside the function), convergence flag and n_iter
  - Returns only plain Python types (float, list, bool, int, None) — JSON-serialisable, byte-identical across runs
  - Accepts both plain dicts and fdars.results wrapper objects (reads `.raw`)
  - Raises clear ValueError for unsupported methods

**Anthropic import guard (Task 1 — tracer):**
- `_require_anthropic()`: tries `import anthropic`, re-raises ImportError with `pip install fdars[advisor]` hint and `anthropic>=0.72.0` version-floor note (CORE-04)

**advise function (Task 1 — tracer):**
- `advise(diagnostics, *, task, domain_context, model="claude-opus-4-8") -> Advice`
- Calls `_require_anthropic()` first, then `anthropic.Anthropic()` (API key from env, never hardcoded)
- Calls `client.messages.parse(model=model, max_tokens=16000, thinking={"type": "adaptive"}, system=..., output_format=Advice, messages=[...])`
- User content built from `json.dumps(diagnostics, sort_keys=True)` + domain_context + task — stable, deterministic ordering

**Grounding-invariant system prompt (Task 2):**
- `_system_prompt(task: str) -> str`
- Encodes grounding invariant verbatim: "reason only from diagnostics provided", "every evidence item must cite a specific diagnostic value", "omit any claim not supported", "never fabricate numbers or invent values not present"
- FDA primer: amplitude variation, phase variation, Karcher mean, warp penalty (lambda_), GCV, variance explained
- Interpretation task clause: explain result in domain terms; set kind="none" unless a concrete change is clearly warranted
- Case-insensitive task dispatch; raises ValueError for unknown tasks

**Version-floor decision + offline check (Task 3):**
- `ADVISOR_ANTHROPIC_MIN_VERSION = "0.72.0"` — RESOLVES the Phase 10 open decision
- `_selfcheck_alignment_diagnostics()`: constructs a fixed synthetic alignment result dict (no RNG), calls `build_diagnostics` twice, asserts equality — importable, side-effect-free offline determinism proof
- Module docstring records version-floor decision and Phase-10/11 split

## Requirements Satisfied

| Requirement | Evidence |
|-------------|----------|
| CORE-01 (alignment) | `build_diagnostics(method="alignment")` computes mean summary + amplitude/phase distances offline |
| CORE-02 | `advise()` calls `client.messages.parse(output_format=Advice)` → schema-validated |
| CORE-03 | `Recommendation` carries action, kind, rationale, expected_effect, evidence[] |
| CORE-04 | Without anthropic: import succeeds, `build_diagnostics` works, `advise` raises ImportError with `pip install fdars[advisor]` |
| ADVISE-01 | `task="interpretation"` clause in `_system_prompt`; `advise(task="interpretation")` supported |

## Deviations from Plan

None — plan executed exactly as written.

The Pydantic offline fallback (plain Python stand-in classes) was anticipated by the plan's CORE-04 requirement and implemented as specified. No surprises.

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| threat_flag: information_disclosure | python/fdars/advisor.py | advise() sends diagnostics + domain_context to Anthropic API over the network — as accepted in T-10-01 (user explicitly calls advise with their own data) |
| threat_flag: env_key_read | python/fdars/advisor.py | ANTHROPIC_API_KEY read from env by anthropic.Anthropic() — T-10-02 mitigated: never hardcoded, never logged, never passed as argument |

Both flags are present in the plan's threat model (T-10-01 accepted, T-10-02 mitigated). No new surface discovered.

## Self-Check: PASSED

- [x] `python/fdars/advisor.py` exists (531 lines)
- [x] Commit `0c1cb3a` exists: "feat(10-01): add fdars.advisor"
- [x] All required symbols present: Advice, Recommendation, build_diagnostics, advise, _require_anthropic
- [x] Task 1 verify: AST symbol check passes
- [x] Task 2 verify: _system_prompt present, grounding invariant text present
- [x] Task 3 verify: ADVISOR_ANTHROPIC_MIN_VERSION present, build_diagnostics deterministic, ImportError contains install hint
