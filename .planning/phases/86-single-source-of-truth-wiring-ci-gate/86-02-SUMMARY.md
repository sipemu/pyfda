---
phase: 86-single-source-of-truth-wiring-ci-gate
plan: "02"
subsystem: paper-pipeline-ci
status: complete
tags: [gate-01, ci, paper-yml, tectonic, drift-gate, path-filter]

dependency_graph:
  requires:
    - "86-01: assert_coverage.py, gen_refs_bib.py, coverage_counts.tex, refs.bib, gen_figures.py"
    - "python/fdars/_capability_map.json (path-filter trigger)"
    - "python/fdars/_references_map.json (path-filter trigger)"
  provides:
    - ".github/workflows/paper.yml — path-filtered CI workflow (GATE-01)"
    - "GATE-01: drift fails loudly in CI (assert_coverage --check as hard gate before tectonic)"
  affects:
    - "Phase 89: paper.yml will be extended with maturin develop for case-study scripts"

tech_stack:
  added:
    - "wtfjoke/setup-tectonic@v4 — CI action to install tectonic for PDF compile"
    - "paper.yml path-filter on paper/**, both JSON maps, docs/data/**"
  patterns:
    - "Step ordering load-bearing: offline pipeline gate (gen_figures → assert_coverage --check → gen_refs_bib) runs BEFORE tectonic PDF compile"
    - "SOURCE_DATE_EPOCH=0 for deterministic PDF timestamps"
    - "No fetch-depth, no biber-version, no maturin in Phase 86 workflow"

key_files:
  created:
    - .github/workflows/paper.yml
  modified: []

decisions:
  - "Used wtfjoke/setup-tectonic@v4 with github-token only — no biber-version (natbib + plain BibTeX needs none)"
  - "Step ordering mirrors the research Pattern 3 exactly — offline pipeline before tectonic so drift fails fast without spending PDF-compile time"
  - "Path-filter includes both JSON map paths (python/fdars/_capability_map.json, python/fdars/_references_map.json) so a map edit triggers the workflow (GATE-01 Pitfall 6)"
  - "No maturin/fdars install — Phase 86 scripts are stdlib-only; gen_figures needs only matplotlib+numpy"

metrics:
  duration: "~2 minutes"
  completed: "2026-09-08"
  tasks_completed: 2
  tasks_total: 2
  commits: 1
  files_created: 1
  files_modified: 0

actuals:
  tokens: 4000
  tasks: 2
  commits: 1
---

# Phase 86 Plan 02: Single-Source-of-Truth Wiring + CI Gate Summary

**One-liner:** Standalone `paper.yml` GitHub Actions workflow path-filtered to the paper and both JSON maps, running the offline pipeline (gen_figures → assert_coverage --check → gen_refs_bib) as a hard gate before `tectonic paper/paper.tex`, making GATE-01 a live CI check.

## Objective

Author `.github/workflows/paper.yml` — the CI gate that turns Plan 86-01's drift tripwires into enforced CI failures. A stale `coverage_counts.tex` or broken pipeline must fail CI rather than pass silently.

## What Was Built

### Task 1: .github/workflows/paper.yml

The workflow satisfies GATE-01 in full:

**Triggers:**
- `push` to `main` and `pull_request`, both path-filtered to:
  - `paper/**`
  - `python/fdars/_capability_map.json`
  - `python/fdars/_references_map.json`
  - `docs/data/**`

**Job `paper` on `ubuntu-latest` — step order (load-bearing):**

| # | Step | Purpose |
|---|------|---------|
| 1 | `actions/checkout@v4` | Checkout (no fetch-depth — no git-history checks) |
| 2 | `actions/setup-python@v5` (3.12) | Python environment |
| 3 | `pip install matplotlib numpy` | Pipeline deps (no maturin/fdars) |
| 4 | `python paper/code/gen_figures.py` | Regenerate figures (PYTHONPATH: scripts:paper/code) |
| 5 | `python paper/code/assert_coverage.py --check` | **HARD GATE** — exits 1 on drift |
| 6 | `python paper/code/gen_refs_bib.py` | Regenerate refs.bib |
| 7 | `wtfjoke/setup-tectonic@v4` (github-token only) | Install tectonic |
| 8 | `tectonic paper/paper.tex` (SOURCE_DATE_EPOCH=0) | Compile PDF |

Steps 4–6 (offline, stdlib-only) always precede steps 7–8 (tectonic) — a drift fails fast without spending PDF-compile time.

### Task 2: Negative test — drift gate fires (GATE-01 verification)

Demonstrated locally that the exact command paper.yml runs at step 5 (`assert_coverage.py --check`) exits non-zero on a deliberate mutation:

1. Appended `% drift-injection` line to `paper/coverage_counts.tex`
2. Ran `python paper/code/assert_coverage.py --check` → exit 1, stderr: "DRIFT: paper/coverage_counts.tex is stale — re-run assert_coverage.py and commit."
3. Restored `coverage_counts.tex` byte-for-byte
4. Confirmed repo clean (`git diff --quiet` passes)

**Result: GATE_FIRES** — the drift tripwire paper.yml invokes exits non-zero on deliberate mutation, and the repo was left clean.

## Verification Gates Passed

| Gate | Command | Result |
|------|---------|--------|
| YAML_VALID | `yaml.safe_load(open('paper.yml'))` | PASS |
| PAPER_YML_OK | All 14 structural grep checks | PASS |
| STEP_ORDER_OK | awk line-number ordering: gen_figures < assert_coverage < gen_refs_bib < tectonic | PASS |
| GATE_FIRES | Negative test: --check exits non-zero on mutation, file restored clean | PASS |

Forbidden tokens confirmed absent: `fetch-depth`, `biber-version`, `maturin`.

## Commits

| Hash | Task | Description |
|------|------|-------------|
| `d627775` | Task 1 | feat(86-02): add .github/workflows/paper.yml — path-filtered offline pipeline gate + tectonic compile (GATE-01) |

Task 2 produces no commit (read-only negative test; mutation restored).

## Deviations from Plan

**Minor: interactive cp prompt during initial negative test run.** The zsh `cp` alias prompted for overwrite confirmation (interactive shell alias). Fixed by using `\cp` (bypasses alias) and then `git checkout -- paper/coverage_counts.tex` to restore. The final negative test run confirmed GATE_FIRES cleanly.

No architectural or behavioral deviations. Plan executed exactly as specified.

## Known Stubs

None. The CI workflow is complete and gates on real artifacts committed in Plan 86-01.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. The workflow consumes only committed repo scripts and maps. T-86-04 (drift passes silently) is mitigated by the assert_coverage --check step at position 5 (verified by Task 2 negative test). T-86-05 (tectonic rate-limiting) mitigated by github-token. T-86-06 (pinned action) accepted at @v4.

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| .github/workflows/paper.yml | FOUND |
| commit d627775 | FOUND |
| coverage_counts.tex restored clean | CONFIRMED (git diff --quiet) |
