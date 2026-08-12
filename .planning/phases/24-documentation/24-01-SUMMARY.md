---
phase: 24-documentation
plan: "01"
subsystem: docs/advisor
tags: [docs, advisor, providers, mkdocs]
status: complete

depends_on: []
provides: [docs/advisor/providers.md]
affects: [docs/advisor/]

tech_stack:
  added: []
  patterns:
    - illustrative-fence convention (not-run warning admonition + plain python fence)

key_files:
  created:
    - docs/advisor/providers.md
  modified: []

decisions:
  - "Used GEMINI_API_KEY (not GOOGLE_API_KEY) — method-accurate against _factory.py _KEY_ENV table; plan spec mentioned GOOGLE_API_KEY but code is the authoritative source."
  - "Split examples into three separate admonition+fence blocks (explicit params, Ollama env, OpenAI-compatible base_url) for clarity, matching SKILL.md Provider Selection section shapes."
  - "Offline core note placed in the install-extras table section as an info admonition — mirrors the pattern in index.md."

metrics:
  duration_seconds: 65
  completed: "2026-08-12"
  tasks_completed: 2
  commits: 1
  files_created: 1
  files_modified: 0

actuals:
  tokens: 5400   # ~21600 chars / 4 over docs/advisor/providers.md
  tasks: 2
  commits: 1
---

# Phase 24 Plan 01: Provider Setup Guide Summary

Created `docs/advisor/providers.md` — a single-page provider setup reference documenting all four advisor backends, selection/precedence rules, and install extras for fdars v3.0.

## What Was Built

**`docs/advisor/providers.md`** — Provider Setup guide (216 lines):

1. **Intro** — explains `Provider` protocol, `advise()` as the sole entry point for provider selection, MCP tools as compute-only.
2. **Backends section** — one subsection per backend with provider name string, install extra, credential, and default model:
   - Anthropic (default) — `[advisor]`, `ANTHROPIC_API_KEY`, `claude-opus-4-8`
   - OpenAI + OpenAI-compatible — `[openai]`, `OPENAI_API_KEY`, `gpt-4o`; `FDARS_ADVISOR_BASE_URL` for vLLM/LM Studio/LocalAI
   - Google Gemini — `[gemini]`, `GEMINI_API_KEY`, `gemini-2.0-flash`; Python 3.10+ note
   - Local Ollama — `[ollama]`, no key required, `http://localhost:11434`
   - `[all-providers]` umbrella extra
3. **Selection and precedence section** — explicit params > env vars > Anthropic default; full env-var table (`FDARS_ADVISOR_PROVIDER`, `FDARS_ADVISOR_MODEL`, `FDARS_ADVISOR_BASE_URL`) plus per-provider API-key variable table; consistent with SKILL.md.
4. **Install extras reference table** — provider → extra → API-key variable → notes.
5. **Examples section** — three illustrative blocks (explicit params, Ollama env path, OpenAI-compatible `base_url`), each preceded by a Material `!!! warning` admonition stating the fence is not run in the docs build.

## Verification

- `docs/advisor/providers.md` exists.
- Contains `FDARS_ADVISOR_PROVIDER`, `FDARS_ADVISOR_BASE_URL`, `all-providers`, `ollama`, `gemini`.
- Zero `exec="1"` fences present.
- Contains `not run in the docs build` text (three occurrences — one per example block).
- Contains `provider="openai"` in the explicit-parameters example.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Accuracy] Used GEMINI_API_KEY instead of GOOGLE_API_KEY**

- **Found during:** Task 1 — reading `_factory.py:_KEY_ENV`
- **Issue:** The plan spec (DOCS-01 action text) stated `GOOGLE_API_KEY` for the Gemini credential. However, the shipped `_factory.py` `_KEY_ENV` dict maps `"gemini"` to `"GEMINI_API_KEY"`, and the `GeminiProvider` docstring says the same. The must_have truths say "keep every value method-accurate against SKILL.md and __init__.py".
- **Fix:** Documented `GEMINI_API_KEY` throughout providers.md (env-var table, install-extras table, per-provider API-key table). The code is the authoritative source.
- **Files modified:** `docs/advisor/providers.md`
- **Commit:** 849565d

## Known Stubs

None — this page is purely prose/reference documentation. All values are derived from shipped code.

## Self-Check: PASSED

- `docs/advisor/providers.md` — FOUND
- Commit 849565d — FOUND
- Zero `exec="1"` fences in providers.md — CONFIRMED
- `not run in the docs build` in providers.md — CONFIRMED (3 occurrences)
