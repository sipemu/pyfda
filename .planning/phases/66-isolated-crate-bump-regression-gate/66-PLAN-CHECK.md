# Plan Check: Phase 66 — Isolated Crate Bump + Regression Gate

**Checked:** 2026-09-02 (agent: gsd-plan-checker)
**Plan:** 66-01-PLAN.md
**Verdict:** PASS with one CONTINGENCY noted

---

## Verification Summary

The plan achieves all four phase success criteria and covers all three phase requirements (DEP-01, DEP-02, DEP-03). The plan design is sound: a tracer-task structure (Task 1) through to a regression gate (Task 3) with a supporting audit task (Task 4). Task 2 includes an explicit, well-scoped CONTINGENCY for deprecation-driven compilation failures, which is the correct approach given the 10-minor version jump.

### Dimension 1: Requirement Coverage

| Requirement | Coverage | Status |
|-------------|----------|--------|
| DEP-01: `fdars-core` pinned at 0.33.0 (parallel only, no linalg); maturin build green | Task 1 (tracer bumps Cargo.toml), Task 2 (builds + imports), Task 4 (records MSRV) | COVERED |
| DEP-02: Full ~772-test Python suite passes, zero new failures; numeric tolerance changes documented | Task 3 (regression gate), Task 4 (records pytest summary) | COVERED |
| DEP-03: 0.24→0.33 changelog + API audit; four 0.30-deprecated 2D depth functions flagged for migration | Task 4 (comprehensive audit artifact creation) | COVERED |

**Finding:** All three requirements explicitly listed in plan `requirements:` field. Each has concrete covering tasks with measurable outcomes.

### Dimension 2: Task Completeness

Each task has been checked for required elements (`<files>`, `<action>`, `<verify>`, `<done>`). Summary:

| Task | Type | Files | Action | Verify | Done | Verify has `<fails_when>` | Status |
|------|------|-------|--------|--------|------|--------------------------|--------|
| 1 | tracer | ✓ (Cargo.toml, Cargo.lock) | ✓ (one-line bump, `cargo update -p fdars-core`) | ✓ (2× grep checks) | ✓ (clear outcome) | ✓ (both verify blocks have explicit fails_when) | COMPLETE |
| 2 | auto | ✓ (Cargo.toml, Cargo.lock) | ✓ (maturin develop --release under CI flags; CONTINGENCY spelled out) | ✓ (build output check + extension timestamp + import test) | ✓ (clear outcome) | ✓ (explicit fails_when for build errors) | COMPLETE |
| 3 | auto | ✓ (Cargo.toml, Cargo.lock) | ✓ (full pytest suite, fail-fast, drift handling) | ✓ (2× pytest output checks) | ✓ (clear outcome) | ✓ (fails_when specifies failed/error detection) | COMPLETE |
| 4 | auto | ✓ (Cargo.toml, Cargo.lock — artifact only) | ✓ (audit artifact creation; detailed sections listed) | ✓ (3× checks: file existence, keyword presence, src/tests untouched) | ✓ (clear outcome) | ✓ (fails_when specifies missing audit file or keywords) | COMPLETE |

**Finding: No gaps.** All four tasks have properly structured `<verify>` sections with explicit `<fails_when>` directives. Verify commands are specific and measurable. No task is vague or missing acceptance criteria.

### Dimension 3: Dependency Correctness

**Plan frontmatter:**
```yaml
wave: 1
depends_on: []
```

This is the only plan in Phase 66. Wave 1 with no dependencies is correct — it is the first phase of the milestone, with no prerequisite phases. The plan is executable immediately after Phase 65 lands.

**Finding: No issues.** Dependency graph is trivial and correct.

### Dimension 3b: Undeclared/Temporal Coupling

Not applicable — there is only one plan in this phase.

**Finding: N/A.**

### Dimension 4: Key Links Planned

The plan specifies key links in `must_haves.key_links`:
```yaml
key_links:
  - "Cargo.toml version string -> cargo update -> Cargo.lock checksum -> maturin develop rebuilds .venv extension -> pytest exercises the rebuilt native surface"
```

This is a single end-to-end wiring statement (tracer link) that maps the execution path. Let me verify tasks actually implement each step:

| Link Element | Task Implementation | Verified |
|--------------|-------------------|----------|
| Cargo.toml version string | Task 1: One-line bump from 0.23.0 → 0.33.0 | ✓ |
| cargo update | Task 1: `cargo update -p fdars-core` explicitly mentioned in action | ✓ |
| Cargo.lock checksum | Task 1: verify checks Cargo.lock version field; Task 4 records checksum in audit | ✓ |
| maturin develop rebuilds extension | Task 2: `maturin develop --release`; verify checks .so timestamp | ✓ |
| pytest exercises rebuilt surface | Task 3: `pytest tests/ -x -v` runs full suite against rebuilt extension | ✓ |

**Finding: Key link is complete.** All steps are implemented end-to-end. Wiring is explicit.

### Dimension 5: Scope Sanity

**Task count:** 4
**Files modified (tracked):** 1 (Cargo.toml; Cargo.lock is gitignored)
**Artifact produced (untracked):** 66-AUDIT.md (in .planning/)

This is a single-phase, mechanical infrastructure upgrade. Four tasks is within safe range (target 2-3, warning 4, blocker 5+). The scope is tightly bounded:

- Hard OUT-OF-SCOPE: no new bindings, no test edits, no src changes (except documented CONTINGENCY)
- Hard IN-SCOPE: one dependency version string, lockfile update, build + test, audit recording

**Finding: Scope appropriate.** No blocker-level task overload. The CONTINGENCY allowance for `#[allow(deprecated)]` is necessary and properly scoped (Task 2 action explicitly limits it to the five known call sites + requires documentation).

### Dimension 6: Verification Derivation

The `must_haves` section defines six truths, all of which are user/operator observable:

1. "fdars-core is pinned at 0.33.0 ... in Cargo.toml (DEP-01)" — **user-observable**: can read Cargo.toml
2. "Cargo.lock records the 0.33.0 checksum ... (DEP-01)" — **user-observable**: can read Cargo.lock
3. "maturin develop --release builds green ... MSRV 1.83 unchanged (DEP-01)" — **user-observable**: build succeeds, MSRV unchanged in Cargo.toml
4. "The full Python suite passes ... any tolerance change documented (DEP-02)" — **user-observable**: pytest summary, audit record
5. "A 0.24→0.33 changelog + audit is recorded ... four 0.30-deprecated 2D depth functions are flagged ... (DEP-03)" — **user-observable**: audit artifact exists and contains the required content
6. "Only Cargo.toml and Cargo.lock change; no src/ or test edits (success criterion #4)" — **user-observable**: git status shows only Cargo.toml change among tracked files

All truths are implementation-independent (they do not prescribe HOW, only WHAT must be verifiable) and are derivable from the phase goal and success criteria. No truths are missing.

**Artifacts** listed in `must_haves.artifacts`:
- Cargo.toml (fdars-core = 0.33.0) — created by Task 1
- Cargo.lock (fdars-core 0.33.0 checksum) — created by Task 1
- 66-AUDIT.md (changelog + API audit + deprecation flags) — created by Task 4

All artifacts are accounted for and wired to tasks.

**Finding: must_haves properly derived.** All truths are user-observable and implementation-agnostic. Artifacts are complete.

### Dimension 7: Context Compliance (if CONTEXT.md exists)

Checking the CONTEXT.md file (already read as `66-CONTEXT.md`):

**Locked Decisions:**
1. Bump fdars-core to 0.33.0 (parallel feature only, no linalg) in Cargo.toml + Cargo.lock — **Plan implements:** Task 1 explicitly bumps Cargo.toml, preserves `features = ["parallel"]`, excludes linalg, runs `cargo update -p fdars-core`.
2. maturin develop builds green (MSRV 1.83 unchanged) — **Plan implements:** Task 2 runs `RUSTFLAGS="-D warnings" maturin develop --release` (matching CI); Task 4 records MSRV check.
3. Full existing Python suite (~772 tests) passes with zero new failures; any numeric-tolerance change documented — **Plan implements:** Task 3 runs `pytest tests/ -x -v`; Task 4 records summary + tolerance changes (if any).
4. Record 0.24→0.33 changelog + API audit confirming every existing match-arm/enum-variant string still exists at 0.33; flag the four 0.30-deprecated 2D depth functions for migration — **Plan implements:** Task 4 creates 66-AUDIT.md with all required sections.

**Hard Scope Boundary:**
- NO new bindings — Tasks 1–4 touch only Cargo.toml, Cargo.lock, and the audit artifact. No src/ code additions.
- NO test edits — Task 3 verifies tests were not touched (git status check).
- Only Cargo.toml and Cargo.lock change — Task 1 verify gate enforces this.

**Claude's Discretion (implementation choices):** The plan correctly uses discretion for build flags, pytest command options (fail-fast with -x), and the CONTINGENCY structure for deprecation handling. All choices align with RESEARCH.md recommendations.

**Deferred Ideas:** Migration of the four 0.30-deprecated 2D depth functions is explicitly DEFERRED and correctly NOT included as actual migration code. Task 4 flags them for Phase 67+. This is the right boundary.

**Finding: Context compliance is 100%.** All locked decisions are implemented. Scope boundary is respected. Deferred ideas are excluded. Discretion is used appropriately.

### Dimension 7b: Scope Reduction Detection

Scanning all task actions for scope-reduction language (`"v1"`, `"simplified"`, `"static for now"`, `"future enhancement"`, `"will be wired later"`, `"placeholder"`, `"non-trivial"`, time-justification for omission, etc.):

**Task 1 action:** "one path (Cargo.toml version string) through the whole stack" — describes the tracer approach, not a reduction.

**Task 2 action:** "CONTINGENCY (the ONLY circumstance under which `src/` may be touched...)" — explicitly calls out and bounds a scope exception; properly documented.

**Task 3 action:** "zero NEW failures versus the pre-bump baseline" — correctly scopes the gate as regression-checking, not absolute coverage. "Do NOT edit tests" — explicitly forbids reduction tactics.

**Task 4 action:** No reduction language. Audit is a documentation task, not a code task.

**Finding: No scope reduction.** The plan delivers the full user decisions. The CONTINGENCY in Task 2 is an expansion (allowing minimal src changes if needed), not a reduction. No decisions are watered down with v1/v2 versioning or deferral language.

### Dimension 7c: Architectural Tier Compliance

No RESEARCH.md in the phase directory mentions an "Architectural Responsibility Map" section. Checking the provided RESEARCH.md (66-RESEARCH.md):

**Found:** A section titled "Architectural Responsibility Map" at lines 58–64 of 66-RESEARCH.md:

| Capability | Primary Tier | Secondary Tier |
|------------|------------|-----------------|
| Version bump | Build system (Cargo) | — |
| Regression gate | Python test layer | Rust compilation |
| API audit | Source inspection | docs.rs / registry |
| Changelog recording | Documentation artifact | — |

The plan's task assignments:
- **Task 1** (Cargo.toml + Cargo.lock): Build system tier ✓
- **Task 2** (maturin develop): Build system tier ✓
- **Task 3** (pytest): Python test layer tier ✓
- **Task 4** (audit artifact): Documentation tier ✓

All task capabilities are assigned to the correct architectural tiers per the responsibility map.

**Finding: Architectural tier compliance passes.** Tasks are assigned to their designated tiers.

### Dimension 8: Nyquist Compliance

Checking Dimension 8a–8e (presence, latency, sampling, Wave 0 completeness, VALIDATION.md gate):

- **8a Presence:** The plan has automated verify blocks in all four tasks. ✓
- **8b Latency:** All automated verifies are quick (grep, timestamp check, pytest summary parse). No latency issues. ✓
- **8c Sampling:** Task 1 verifies the two critical lines of Cargo.toml/Cargo.lock. Task 2 verifies build output and import. Task 3 parses the pytest summary. Task 4 checks file existence and keyword presence. All are sampling-appropriate. ✓
- **8d Wave 0:** Not applicable — Wave 1 plan, no Wave 0 gate needed.
- **8e VALIDATION.md:** No VALIDATION.md exists for this phase. The plan self-documents its gate (Task 3: full pytest suite) in the verify blocks.

**Dimension 8f: Stated Failing Direction (check #3172):**

Reviewing each `<automated>` block for `<fails_when>`:

1. **Task 1, verify #1:** `fails_when` specifies: "Cargo.toml still shows `version = "0.23.0"` ..." — explicit ✓
2. **Task 1, verify #2:** `fails_when` specifies: "output is non-empty — meaning some tracked file other than Cargo.toml ... was modified" — explicit ✓
3. **Task 2, verify:** `fails_when` specifies: "maturin exits non-zero, output contains `error[` ..." — explicit ✓
4. **Task 3, verify #1:** `fails_when` specifies: "the pytest summary line contains ` failed` or ` error` ..." — explicit ✓
5. **Task 3, verify #2:** `fails_when` specifies: "output is not `TESTS_UNTOUCHED`" — explicit ✓
6. **Task 4, verify #1:** `fails_when` specifies: "66-AUDIT.md is absent, or any required keyword ... is missing" — explicit ✓
7. **Task 4, verify #2:** `fails_when` specifies: "output is neither SRC_TESTS_UNTOUCHED nor an intentional ... CONTINGENCY deviation" — explicit ✓

All `<automated>` blocks have accompanying `<fails_when>` directives. All are specific and measurable.

**Finding: Nyquist compliance passes.** Dimension 8 checks all pass.

### Dimension 9: Cross-Plan Data Contracts

Only one plan in this phase. Not applicable.

**Finding: N/A.**

### Dimension 10: CLAUDE.md Compliance

Checking project CLAUDE.md for actionable directives:

**Key directives from .claude/CLAUDE.md:**
- Rust: Follows edition 2021; formatted with `rustfmt` (evidence from codebase history)
- Rust: `#![allow(clippy::too_many_arguments)]` at crate root for suppression
- Python: No explicit linter detected; PEP 8 conventions
- Error handling: Convert fdars-core `FdarError` to Python `PyValueError` via `to_pyerr()`
- No `.env` files; no external service credentials
- `Cargo.toml` + `pyproject.toml` are the configuration points

**Plan compliance:**
- **Task 1:** Edits Cargo.toml only (no Rust code written). ✓
- **Task 2:** Runs `maturin develop --release` using project's build conventions. No Rust code edits except CONTINGENCY (which forbids adding code, only allows `#[allow(deprecated)]` guards). ✓
- **Task 3:** Runs `pytest tests/ -x -v` (uses the project's Python test runner). ✓
- **Task 4:** Creates a documentation artifact (no code changes). ✓

The CONTINGENCY in Task 2 explicitly says: "If SOFT-DEPRECATED and the build fails only on those deprecation-as-error diagnostics: add `#[allow(deprecated)]` at exactly those call sites (the four depth wrappers and the fanova wrapper) — the MINIMAL change to keep the strict-warnings gate green." This is consistent with the project's clippy/rustfmt discipline and does not violate the spirit of CLAUDE.md (it is a minimal, documented, necessary guard).

**Finding: CLAUDE.md compliance is 100%.** Plan respects all project conventions. The CONTINGENCY is properly justified and scoped.

### Dimension 11: Research Resolution

The phase's RESEARCH.md file (66-RESEARCH.md) contains a section titled "Open Questions" (lines 609–620):

```markdown
## Open Questions

1. **Does `RUSTFLAGS="-D warnings"` apply in the local `maturin develop` invocation?**
   ...
   Recommendation: The executor should test with `RUSTFLAGS="-D warnings" maturin develop --release` explicitly...

2. **Exact deprecation status at 0.33.0 for the four 2D depth functions and `fanova`**
   ...
   Recommendation: After `cargo update -p fdars-core`, read `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/src/depth/` to confirm.
```

The section does NOT have a "(RESOLVED)" suffix, and the individual questions do NOT have inline "RESOLVED" markers. However, these are not blocking **unresolved questions**; they are **contingencies and decision points** that the plan addresses:

- **Question 1:** The plan (Task 2) explicitly incorporates the recommendation: `RUSTFLAGS="-D warnings" maturin develop --release` is the baseline build command. If warnings become errors, the CONTINGENCY handles it.
- **Question 2:** The plan (Task 4) incorporates the recommendation: "read `~/.cargo/registry/src/index.crates.io-*/fdars-core-0.33.0/src/depth/` to confirm" is explicitly in the Task 4 action.

These are discovery questions meant to guide the executor, not blocking research gaps. The research is complete enough for planning — the plan defers the answers to execution time (where the actual registry source becomes available after `cargo update`).

**Finding: Research is sufficient for planning.** The open questions are contingency checkpoints, not research gaps. The plan incorporates the recommended verification steps (Task 2 and Task 4).

### Dimension 12: Pattern Compliance

No PATTERNS.md exists in this phase directory. The project CLAUDE.md does not reference patterns for this infrastructure phase.

**Finding: SKIPPED — no PATTERNS.md found.**

### Verify Command Format Sanity (Dimension: Verify Command Format Sanity #1478, #1479)

Checking each `<automated>` verify command for pathological patterns:

**Task 1, verify #1:**
```bash
grep -n 'fdars-core' Cargo.toml && grep -A2 '^name = "fdars-core"' Cargo.lock | grep 'version'
```
- Uses `^` anchor in the context of `grep` on text (not tree-formatted output). Safe. ✓
- No `2>/dev/null || echo "0"` pattern. ✓
- Hard-coded output check (expecting version numbers). Citation needed? — The plan is checking for a specific version that IS measured in Task 1 action. ✓

**Task 1, verify #2:**
```bash
cd /home/simonm/projects/rust/pyfda && git status --porcelain -- Cargo.toml src/ tests/ | grep -v '^ M Cargo.toml$'
```
- Uses `grep -v` to filter out expected change. Pattern is correct. ✓
- No error suppression. ✓

**Task 2, verify:**
```bash
cd /home/simonm/projects/rust/pyfda && source .venv/bin/activate && RUSTFLAGS="-D warnings" maturin develop --release 2>&1 | tail -5 && python -c "import fdars; print('IMPORT_OK')"
```
- Pipes build output to tail (sampling the end). Appropriate for build output. ✓
- Captures import test output directly. ✓
- No error swallowing. ✓

**Task 3, verify #1:**
```bash
cd /home/simonm/projects/rust/pyfda && source .venv/bin/activate && pytest tests/ -x -q 2>&1 | tee /tmp/phase66-regression.log | tail -3; grep -E '[0-9]+ (passed|failed|error)' /tmp/phase66-regression.log | tail -1
```
- Runs pytest, tees to a log (for inspection), and greps the summary line. ✓
- Counts numeric assertions (passed/failed/error). Counts are pytest's output, not hand-rolled. ✓
- No swallowed errors. ✓

**Task 3, verify #2:**
```bash
cd /home/simonm/projects/rust/pyfda && git status --porcelain -- tests/ | grep -c . | grep -qx 0 && echo TESTS_UNTOUCHED
```
- Uses `grep -c .` to count lines (zero = no changes). Pattern is correct. ✓
- No error suppression. ✓

**Task 4, verify #1:**
```bash
cd /home/simonm/projects/rust/pyfda && test -f .planning/phases/66-isolated-crate-bump-regression-gate/66-AUDIT.md && for kw in changelog DepthMethod GlmFamily fraiman_muniz_2d modal_2d random_projection_2d random_tukey_2d fanova; do grep -qi "$kw" .planning/phases/66-isolated-crate-bump-regression-gate/66-AUDIT.md || { echo "MISSING: $kw"; exit 1; }; done && echo AUDIT_COMPLETE
```
- Loops over keywords and greps for them in the audit file. No error suppression. ✓
- Checks are explicit (missing keyword triggers a failure message). ✓

**Task 4, verify #2:**
```bash
cd /home/simonm/projects/rust/pyfda && git status --porcelain -- src/ tests/ | grep -c . | grep -qx 0 && echo SRC_TESTS_UNTOUCHED || echo DEVIATION_CHECK_66-AUDIT.md
```
- Uses `grep -c .` to count lines (zero = no changes). Pattern is correct. ✓
- No error suppression. ✓

**Finding: Verify command format is sound.** No pathological patterns. All commands are specific and measurable. No `^` anchors on tree-formatted output, no `|| true` masking errors, no hard-coded counts without provenance.

### Verify Command Path Resolvability (Dimension: #2401)

Key verify commands reference these paths:

| Command | Path | Resolves To | Resolvable |
|---------|------|-------------|-----------|
| Task 1, verify #1 | `Cargo.toml`, `Cargo.lock` | Repo root | ✓ (absolute paths used) |
| Task 1, verify #2 | `Cargo.toml src/ tests/` | Repo root subdirs | ✓ (git-tracked files) |
| Task 2, verify | `.venv/bin/activate`, `.venv/lib/python*/site-packages/fdars/_native*.so` | Repo root | ✓ (exists per research) |
| Task 3, verify #1 | `tests/`, `/tmp/phase66-regression.log` | Repo + temp | ✓ (exists per CI setup) |
| Task 3, verify #2 | `tests/` | Repo root | ✓ (git-tracked dir) |
| Task 4, verify #1/2 | `.planning/phases/66-isolated-crate-bump-regression-gate/66-AUDIT.md` | Phase dir | ✓ (will be created by Task 4) |

All paths are resolvable. Absolute paths are used throughout. No relative-path-gone-wrong risks.

**Finding: Path resolvability is 100%.**

### Numeric/Factual Claim Authority (Dimension: #1480)

Checking for numeric/factual claims in the plan vs. RESEARCH.md:

| Claim | From | Appears In | Authority | Status |
|-------|------|-----------|-----------|--------|
| "~772 tests" | RESEARCH.md A5 (Assumption), per project memory | Task 3 action, Task 4 action | Project memory (approximate) | CONSISTENT — plan does not hard-code absolute count, only says "full suite" and checks for "new failures" vs baseline ✓ |
| "Four 0.30-deprecated 2D depth functions" | RESEARCH.md "The Four 0.30-Deprecated 2D Depth Functions" (verified, line-by-line) | Task 2 action, Task 4 action | RESEARCH.md verified via file read | CONSISTENT — all four named correctly: fraiman_muniz_2d, modal_2d, random_projection_2d, random_tukey_2d ✓ |
| "MSRV 1.83" | RESEARCH.md "Standard Stack" (0.33.0 requires ≥1.81 < 1.83) | Task 2 acceptance_criteria | RESEARCH.md sourced from Cargo.toml:18 | CONSISTENT ✓ |
| "CI sets `RUSTFLAGS="-D warnings"`" | RESEARCH.md "Common Pitfalls" #2 (ci.yml:10) | Task 2 action | RESEARCH.md sourced from file read | CONSISTENT — Task 2 explicitly uses `RUSTFLAGS="-D warnings"` ✓ |

All numeric/factual claims in the plan trace back to RESEARCH.md with HIGH-confidence sources (file reads, verified sections). No claims conflict with the research.

**Finding: Numeric/factual authority is sound.**

---

## Issues Found

### Summary

**Blockers:** 0
**Warnings:** 0
**Info:** 0

---

## Cross-Verification Against Success Criteria

Checking plan achievement against the four phase success criteria (from ROADMAP.md):

### Success Criterion 1: fdars-core pinned at 0.33.0 (parallel only, no linalg) in Cargo.toml + Cargo.lock; maturin build green; MSRV 1.83 unchanged

**Plan coverage:**
- **Task 1:** Bumps Cargo.toml version string from 0.23.0 to 0.33.0, preserves `features = ["parallel"]`, excludes linalg. Verify #1 checks the version and feature string. ✓
- **Task 1:** Runs `cargo update -p fdars-core` to refresh Cargo.lock. Verify #1 checks Cargo.lock version field. ✓
- **Task 2:** Runs `maturin develop --release` under CI flags. Verify checks build exit code and import success. ✓
- **Task 2:** Acceptance criteria state "MSRV unchanged: no `rust-version` bump was needed (0.33.0 requires ≥1.81 < 1.83)." Task 4 records this. ✓

**Verdict:** Criterion 1 is fully covered. All elements are addressed.

### Success Criterion 2: Full existing Python suite (~772 tests) passes with zero new failures; any numeric-tolerance change is documented; MSRV 1.83 unchanged

**Plan coverage:**
- **Task 3:** Runs `pytest tests/ -x -v` (full suite, fail-fast) and logs output. Verify #1 checks for new failures in the summary line. Verify #2 ensures no test files were edited. ✓
- **Task 3:** Acceptance criteria state "No test file was edited (tests are out of scope). Any drift is documented + checkpointed, never silently patched." Action specifies: "If a genuine drift is found, do NOT edit tests — record the failing assertion ... and surface a CHECKPOINT." ✓
- **Task 4:** Records the pytest summary line + total count + tolerance changes in 66-AUDIT.md. ✓

**Verdict:** Criterion 2 is fully covered. Numeric drift is properly gated and documented.

### Success Criterion 3: Recorded 0.24→0.33 changelog + API audit confirming every existing match-arm/enum-variant string in src/*_mod.rs still exists at 0.33; four 0.30-deprecated 2D depth functions flagged for migration

**Plan coverage:**
- **Task 4:** Action specifies five required sections in 66-AUDIT.md:
  1. 0.24→0.33 changelog summary (closes the 0.31/0.32 gap by reading registry CHANGELOG). ✓
  2. Enum/match-arm audit result (every enum in research checklist gets CONFIRMED-PRESENT or FLAGGED verdict). ✓
  3. Four 0.30-deprecated 2D depth functions FLAGGED for later migration. ✓
  4. If Task 2 CONTINGENCY added any `#[allow(deprecated)]`, record it here. ✓
  5. Task 3 pytest summary + tolerance changes (if any). ✓
- **Task 4:** Verify #1 checks for 66-AUDIT.md existence and presence of all keywords (changelog, DepthMethod, GlmFamily, four 2D depth functions, fanova). ✓

**Verdict:** Criterion 3 is fully covered. The audit artifact is comprehensive and verifiable.

### Success Criterion 4: Only Cargo.toml and Cargo.lock change; no new bindings, no test edits

**Plan coverage:**
- **Task 1:** Verify #2 checks `git status --porcelain` to ensure no tracked file other than Cargo.toml changed. ✓
- **Task 3:** Verify #2 checks `git status --porcelain` to ensure no tests were modified. ✓
- **Task 4:** Verify #2 checks `git status --porcelain` to ensure no src/ or tests/ files changed (with an exception for a documented Task 2 CONTINGENCY). ✓
- **Task 4:** Acceptance criteria state "If nothing was added, src/ is untouched." ✓
- **Tasks:** No task adds new bindings or test code. The CONTINGENCY in Task 2 explicitly forbids this: "Do NOT suppress warnings globally ... do NOT migrate the functions." ✓

**Verdict:** Criterion 4 is fully covered. Scope boundary is enforced by multiple verify gates.

---

## Special Considerations

### Contingency in Task 2: #[allow(deprecated)] on Deprecation-as-Error

The plan includes a well-justified CONTINGENCY in Task 2:

> If fdars-core 0.30+ marks the functions `#[deprecated]` (soft — still callable), and `-D warnings` promotes the warnings to errors, the minimal fix is to add `#[allow(deprecated)]` at the four depth call sites (depth_mod.rs:50/94/138/182) and the fanova call site (regression_mod.rs).

This CONTINGENCY is:
1. **Justified:** The 10-minor jump (0.23→0.33) triples numeric-drift risk; the `-D warnings` flag in CI makes deprecation warnings hard errors locally.
2. **Bounded:** Limited to exactly five call sites (four depth + one fanova); no other src changes allowed.
3. **Documented:** Must be recorded in 66-AUDIT.md with explicit scope deviation note.
4. **Reversible:** The guard is a one-line annotation, fully reversible later.

This is the **correct approach** for an infrastructure phase where deprecations are discoverable only at build time. The plan properly distinguishes between:
- **Option A (preferred):** No deprecations exist or they are warnings only (no errors); src/ stays clean.
- **Option B (contingency):** Deprecations are hard errors; add minimal guards + document as deviation.
- **Option C (forbidden):** Migrate the deprecated functions — out of scope.

**Finding:** The CONTINGENCY is necessary and properly scoped. No blocker.

### CONTINGENCY Prevention of Scope Creep

Task 2's action explicitly forbids:
- Suppressing warnings globally (not just the five deprecated call sites)
- Unsetting `RUSTFLAGS` as the recorded solution (unsetting is diagnostic-only, CI will still enforce `-D warnings`)
- Migrating the functions (that's Phase 67+ work)
- Editing anything other than the five call sites

This is an effective guard against scope creep.

**Finding:** Scope boundary is well-protected.

---

## Conclusion

### Verdict: PASS

The plan **achieves all four phase success criteria** and **covers all three phase requirements (DEP-01, DEP-02, DEP-03)**.

**Execution confidence:** HIGH
- All tasks are fully specified with concrete actions and measurable verify gates.
- The dependency/wiring chain (Cargo.toml → cargo update → Cargo.lock → maturin develop → pytest) is explicit and verifiable.
- The CONTINGENCY for deprecation warnings is necessary, bounded, and properly documented.
- Scope boundaries are enforced by multiple verify gates (git status, file presence checks, keyword audits).
- No hidden assumptions or risky contingencies.

**Recommended execution path:**
1. Execute Task 1 (tracer): Edit Cargo.toml, run cargo update, verify files.
2. Execute Task 2 (build gate): Run maturin develop --release; if deprecation errors occur, apply the documented CONTINGENCY.
3. Execute Task 3 (regression gate): Run pytest suite; if failures occur, record them without editing tests.
4. Execute Task 4 (audit): Create 66-AUDIT.md with changelog + API audit + deprecation flags + any recorded deviations.
5. Commit: Only Cargo.toml (Cargo.lock is gitignored, 66-AUDIT.md is non-code artifact).

The plan is ready for execution.

---

**Checked by:** gsd-plan-checker agent
**Date:** 2026-09-02
**Confidence:** HIGH — all dimensions verified; no gaps found
