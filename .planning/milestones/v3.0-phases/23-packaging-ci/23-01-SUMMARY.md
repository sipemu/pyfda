---
phase: 23-packaging-ci
plan: "01"
subsystem: packaging-ci
tags: [ci, packaging, smoke-test, python-matrix, qual-03, qual-04]
status: complete

dependency_graph:
  requires: []
  provides:
    - scripts/bare_venv_smoke.py
    - ci.yml test-python matrix 3.9–3.14 with version-gated extras
    - ci.yml smoke-bare-venv job
  affects:
    - .github/workflows/ci.yml
    - scripts/bare_venv_smoke.py

tech_stack:
  added: []
  patterns:
    - Conditional CI step using `if: matrix.python-version == '3.9'` for version-gated extra install
    - Bare-venv smoke script pattern: 4-check offline proof (import, advisor, build_diagnostics, ImportError)

key_files:
  created:
    - scripts/bare_venv_smoke.py
  modified:
    - .github/workflows/ci.yml

decisions:
  - "Gating via two `if:` job-step conditions (3.9 vs !=3.9) rather than a matrix dimension or bash if-string — clearest YAML expression for a binary split"
  - "Used `pip install -e .[advisor,openai,ollama]` (NOT gemini/mcp) on 3.9 since gemini requires google-genai (3.10+ only) and mcp>=2.0 also requires 3.10+"
  - "smoke-bare-venv job uses Python 3.12 (mid-matrix, broadly available) as single version"
  - "Smoke script uses `provider='openai'` for the missing-provider check — openai is guaranteed absent in any bare venv; assertion prefix 'pip install fdars[' is adapter-agnostic"

metrics:
  duration: "~2.5 minutes (2026-08-12T13:27:51Z → 2026-08-12T13:30:11Z)"
  completed: "2026-08-12"
  tasks_completed: 3
  commits: 3

actuals:
  tokens: 8500
  tasks: 3
  commits: 3

requirements_satisfied:
  - QUAL-03
  - QUAL-04
---

# Phase 23 Plan 01: CI Matrix Expansion + Bare-Venv Smoke Summary

**One-liner:** Python 3.9–3.14 CI matrix with version-gated extras and an offline base-package smoke proof (no provider SDKs).

## What Was Built

### Task 1 — `scripts/bare_venv_smoke.py` (QUAL-04, tracer)

Created a 4-check offline smoke script proving the base `fdars` package works with
**zero provider extras** installed:

1. `import fdars` — extension module importable
2. `from fdars import advisor` — advisor importable, no provider SDK required
3. `advisor.build_diagnostics({"data": ones(20,50), "argvals": linspace(0,1,50)}, method="represent")` — offline deterministic call; `json.dumps` serialises the result (no NumPy scalars)
4. `advisor.advise(..., provider="openai")` inside `try/except ImportError` — raises `ImportError` whose message contains `"pip install fdars["` (adapter-agnostic prefix)

Exit code 0 on local interpreter. Structured with `main() -> int` + `sys.exit(main())` guard.

**Local verification:** `scripts/bare_venv_smoke.py` exits 0, prints `PASS: fdars base-package smoke (import, advisor, build_diagnostics, missing-provider ImportError)`

### Task 2 — ci.yml matrix expansion (QUAL-03)

`test-python` job matrix expanded from `["3.10","3.12","3.13"]` to
`["3.9","3.10","3.11","3.12","3.13","3.14"]`.

Two new conditional install steps after `maturin develop --release`:

```yaml
- name: Install provider extras (Python 3.9 — no gemini/mcp)
  if: matrix.python-version == '3.9'
  run: pip install -e ".[advisor,openai,ollama]"

- name: Install provider extras (Python 3.10+ — all-providers + mcp)
  if: matrix.python-version != '3.9'
  run: pip install -e ".[all-providers,mcp]"
```

`fmt`, `clippy`, `test-rust` jobs untouched.

**Local verification:** YAML parses; matrix is `['3.9','3.10','3.11','3.12','3.13','3.14']`; all 5 expected jobs present. True 6-version run is **verified-on-push (GitHub Actions)**.

### Task 3 — `smoke-bare-venv` CI job (QUAL-04)

New CI job added to `ci.yml`:

- `runs-on: ubuntu-latest`, Python 3.12 (single version, no matrix)
- Installs `maturin numpy pandas` ONLY — **zero extras**
- `maturin develop --release` (base package, no `[...]`)
- `python scripts/bare_venv_smoke.py` — gates on exit code

**Local verification:** YAML parses; `smoke-bare-venv` job present; job blob contains no `[advisor]`, `[openai]`, `all-providers`, or `[mcp]`. True fresh-venv proof is **verified-on-push (GitHub Actions)**.

## Verification Summary

| Check | Result | Method |
|-------|--------|--------|
| `scripts/bare_venv_smoke.py` exits 0 | PASS | Local (`.venv/bin/python`) |
| `ci.yml` parses as valid YAML | PASS | Local (PyYAML) |
| test-python matrix = 6 versions | PASS | Local (YAML parse + assertion) |
| `smoke-bare-venv` job present, zero extras | PASS | Local (YAML parse + assertion) |
| Rust jobs (fmt/clippy/test-rust) intact | PASS | Local (YAML parse) |
| Offline test suite baseline (233 passed, 4 skipped) | PASS | Local (`pytest tests/ -q`) |
| 6-version matrix actual run | **verified-on-push** | GitHub Actions |
| 3.9 gemini/mcp-absent gating behavior | **verified-on-push** | GitHub Actions |
| smoke-bare-venv fresh venv from wheel | **verified-on-push** | GitHub Actions |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | c8d7d74 | feat(23-01): add bare-venv smoke script for QUAL-04 base-package proof |
| 2 | 2886934 | feat(23-01): expand test-python matrix to 3.9–3.14 with version-gated extras (QUAL-03) |
| 3 | 0760a5a | feat(23-01): add smoke-bare-venv CI job wiring bare_venv_smoke.py (QUAL-04) |

## Self-Check: PASSED

- [x] `scripts/bare_venv_smoke.py` exists
- [x] `.github/workflows/ci.yml` modified
- [x] All 3 commits present in git log
- [x] Offline suite green (233 passed, 4 skipped)
