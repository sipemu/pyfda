# Phase 36: Crate Bump + Regression Gate — Research

**Researched:** 2026-08-20
**Domain:** Cargo dependency bump + PyO3 binding compile-correctness + regression gate
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

All implementation choices are at Claude's discretion — pure infrastructure phase (crate upgrade + regression gate). Guided by the ROADMAP phase goal, success criteria, the research SUMMARY.md, and codebase conventions.

Established facts from research (`.planning/research/STACK.md`, `SUMMARY.md`):
- Bump is a single-field `Cargo.toml` change: `fdars-core = { version = "0.23.0", features = ["parallel"] }` (from `0.20.0`). Keep `parallel`, do NOT enable `linalg` (still gates only `ridge_regression_fit`; still wants Rust 1.84+ > MSRV 1.83).
- MSRV of fdars-core 0.23.0 is 1.81 (≤ pyfda 1.83) — bump is unblocked.
- Upstream 0.21/0.22/0.23 changes are additive/non-breaking; transitive dependency graph is additive-only (single-field diff upstream).
- Any upstream enum reached by *existing* pyfda code that became `#[non_exhaustive]` at 0.23 needs a wildcard `_ => PyValueError` fallback arm (the crate will not compile without it) — v5.0 Phase 30 hit this with `CvCriterion`.
- The full existing binding + advisor suite (~560 tests) passing unchanged is the sole success criterion.

### Claude's Discretion

Pure infrastructure phase — all choices within the framing above.

### Deferred Ideas (OUT OF SCOPE)

None — infrastructure phase. All new-binding work is scoped to Phases 37–41.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DEP-05 | `fdars-core` bumped 0.20.0 → 0.23.0 in `Cargo.toml` with `features = ["parallel"]` (do NOT enable `linalg`); `maturin develop` build green. | STACK.md confirmed single-field Cargo.toml diff; `git diff v0.20.0 v0.23.0` read this session — additive-only; MSRV 1.81 ≤ pyfda 1.83 verified. |
| DEP-06 | Regression gate — the full existing binding + advisor suite passes unchanged as the sole success criterion, with any new `#[non_exhaustive]` upstream enums reached by existing code given wildcard fallback arms. Isolated commit before any new binding work. | Exhaustive audit of every match-on-enum site in `src/*_mod.rs` performed this session — result: ZERO new wildcard arms required (all matches on string dispatchers or already-wildcarded enum matches). Test count confirmed 604 via `.venv/bin/python -m pytest tests/ --collect-only -q`. |
</phase_requirements>

---

## Summary

Phase 36 is a pure infrastructure phase with a single source change (one field in `Cargo.toml`), a `maturin develop` rebuild, and a full test suite pass as the gate. The milestone-level research (`STACK.md`, `SUMMARY.md`) established all the macro facts — MSRV compatibility, dependency-graph additivity, feature-flag policy. This phase-specific research answers the one genuine unknown: **does the 0.20.0 → 0.23.0 bump introduce any compile break in existing pyfda binding code?**

**Finding: NO wildcard arms need to be added in Phase 36.** The v5.0 Phase 30 precedent (0.17→0.20) required two wildcard arms on `CvCriterion` in `src/smoothing_mod.rs`. Those arms were added in v5.0 and are already present in the codebase today (`_ => "unknown"` at `smoothing_mod.rs:214`). The 0.20.0→0.23.0 diff introduces no new `#[non_exhaustive]` annotations on any existing enum matched by existing pyfda binding code. All new `#[non_exhaustive]` annotations in the diff are attached to NEW types introduced in 0.21–0.23 (`TvdMssOutliers`, `MuodResult`, `SeqTransformOutliers`, `GlmFamily`, `FunctionalGlmResult`, etc.) — types not touched by any existing `src/*_mod.rs` code.

The actual test count at time of research is **604 tests collected** (the research SUMMARY.md said ~560 — that figure is stale from a point before the v5.0 suite grew). The regression gate must pass 604 tests.

**Primary recommendation:** Change line 18 of `Cargo.toml` from `"0.20.0"` to `"0.23.0"`, run `maturin develop`, run `.venv/bin/python -m pytest tests/ -q`, confirm green. No other source files need editing.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cargo dependency pin | Build layer (`Cargo.toml`) | — | Single-field version string; no application logic |
| Extension rebuild | Build layer (`maturin develop`) | Rust compiler | Regenerates `Cargo.lock` and compiled `.so`; not committed |
| Compile-correctness gate | Rust compiler (`cargo build`) | — | Catches `#[non_exhaustive]` match exhaustiveness at compile time |
| Regression gate | Test layer (`pytest`) | Binding layer | 604-test suite runs against the rebuilt extension |

---

## The Compile-Break Audit (the key Phase 36 research question)

### What was examined

Every `src/*.rs` file that contains a `match` expression operating on an fdars-core enum **value** (not a string dispatch) was read this session. The question for each: did the matched enum gain variants between v0.20.0 and v0.23.0, and does the existing match have a wildcard arm?

### Findings per match site

All five enum-value match sites read directly from source this session:

**1. `src/smoothing_mod.rs:210–214` — `CvCriterion` enum-to-string match**
- `match result.criterion { Cv => "cv", Gcv => "gcv", Aic => "aic", _ => "unknown" }`
- Wildcard `_ => "unknown"` already present — added in v5.0 Phase 30.
- `smoothing.rs` is byte-for-byte identical between v0.20.0 and v0.23.0 (zero diff lines).
- [VERIFIED: src/smoothing_mod.rs:210-215] — quote: `fdars_core::smoothing::CvCriterion::Cv => "cv", fdars_core::smoothing::CvCriterion::Gcv => "gcv", fdars_core::smoothing::CvCriterion::Aic => "aic", _ => "unknown"`
- **Status: NO action required.**

**2. `src/basis_mod.rs:272–276` — `ProjectionBasisType` match (returns string)**
- `match sel.basis_type { Bspline => "bspline", Fourier => "fourier", _ => "unknown" }`
- Wildcard `_ => "unknown"` already present.
- `basis/projection.rs` diff: only added `#[cfg_attr(feature = "serde", ...)]` — no new variants.
- [VERIFIED: src/basis_mod.rs:272-276] — quote: `fdars_core::basis::ProjectionBasisType::Bspline => "bspline", fdars_core::basis::ProjectionBasisType::Fourier => "fourier", _ => "unknown"`
- **Status: NO action required.**

**3. `src/basis_mod.rs:565–570` — `BasisCriterion` enum-to-string match**
- Exhaustive: `match result.criterion { Gcv => "gcv", Cv => "cv", Aic => "aic", Bic => "bic" }` — no wildcard.
- `smooth_basis.rs` is byte-for-byte identical between v0.20.0 and v0.23.0 (zero diff lines).
- `BasisCriterion` is NOT `#[non_exhaustive]` (confirmed: `git show v0.20.0:fdars-core/src/smooth_basis.rs` has no `#[non_exhaustive]` on lines 680-691). The `#[non_exhaustive]` at line 46 in that file belongs to `SmoothBasisResult` struct, not the enum.
- [VERIFIED: src/basis_mod.rs:565-570] — quote: `fdars_core::smooth_basis::BasisCriterion::Gcv => "gcv", fdars_core::smooth_basis::BasisCriterion::Cv => "cv", fdars_core::smooth_basis::BasisCriterion::Aic => "aic", fdars_core::smooth_basis::BasisCriterion::Bic => "bic"`
- **Status: NO action required.** (Non-exhaustive annotation absent; enum unchanged.)

**4. `src/explain_mod.rs:168,348` — `SignificanceDirection` enum matches**
- Both match sites have `_ => "unknown"` wildcard.
- `explain` module not in the changed-file list between v0.20.0 and v0.23.0.
- [VERIFIED: src/explain_mod.rs:168-172] — quote: `fdars_core::explain::SignificanceDirection::Positive => "positive", fdars_core::explain::SignificanceDirection::Negative => "negative", _ => "unknown"`
- **Status: NO action required.**

**5. `src/spm_mod.rs:698,702` — `Option<FdMatrix>` matches (Some/None)**
- These match on `Option<T>`, not on a fdars-core enum — `#[non_exhaustive]` does not apply.
- [VERIFIED: src/spm_mod.rs:698-705]
- **Status: NOT applicable.**

### String-dispatch matches (not affected by `#[non_exhaustive]`)

All other `match` expressions in the codebase operate on `&str` (e.g., `match method { "fraiman_muniz" => ..., other => Err(...) }`). These are not affected by `#[non_exhaustive]` enums — the string-to-enum conversion is a runtime dispatch, not a compile-time exhaustiveness check. Files confirmed: `depth_mod.rs`, `fdata_mod.rs`, `alignment_mod.rs`, `conformal_mod.rs`, `regression_mod.rs`, `represent_mod.rs`, `tolerance_mod.rs`, `inference_mod.rs`.

### New `#[non_exhaustive]` types in 0.20.0→0.23.0 diff

The following new `#[non_exhaustive]` annotations appear in the diff — all on **new types** introduced in 0.21–0.23, none matched by existing pyfda code:

| New type | Added in | Relevant to Phase |
|----------|----------|-------------------|
| `GlmFamily` (enum) | 0.23 | Phase 37 (new binding) |
| `FunctionalGlmResult` (struct) | 0.23 | Phase 37 |
| `ConcurrentRegrResult` (struct) | 0.21 | Phase 37 |
| `PaceFpcaResult` (struct) | 0.22 | Phase 38 |
| `ElasticMultinomialResult` (struct) | 0.23 | Phase 38 |
| `TvdMssOutliers` (struct) | 0.23 | Phase 39 |
| `MuodResult` (struct) | 0.23 | Phase 39 |
| `SeqTransform` (enum) | 0.23 | Phase 39 |
| `SeqTransformOutliers` (struct) | 0.23 | Phase 39 |
| `ItpResult` (struct) | 0.23 | Phase 39 |

**None of these are referenced by any existing `src/*_mod.rs` file** — they are new public surface, not extensions to existing matched enums. Phase 36 does not bind them.

**Conclusion: Phase 36 requires only a single-line `Cargo.toml` edit. No `src/*.rs` files need modification.**

---

## Standard Stack

### Core (unchanged from STACK.md — cited, not re-derived)

| Component | Version | Change |
|-----------|---------|--------|
| `fdars-core` | **0.23.0** (from 0.20.0) | One-field `Cargo.toml` bump |
| PyO3 | 0.28 (abi3-py39) | No change |
| numpy crate | 0.28 | No change |
| maturin | 1.0–2.0 | No change |
| Rust toolchain | 1.83 (pyfda MSRV) | No change; fdars-core MSRV dropped to 1.81 |

[CITED: .planning/research/STACK.md — single-field diff confirmed from `git diff v0.20.0 v0.23.0 -- fdars-core/Cargo.toml` performed in the milestone research session]

### The exact `Cargo.toml` change

```toml
# Before (line 18 of /home/simonm/projects/rust/pyfda/Cargo.toml)
fdars-core = { version = "0.20.0", features = ["parallel"] }

# After
fdars-core = { version = "0.23.0", features = ["parallel"] }
```

[VERIFIED: Cargo.toml:18] — quote: `fdars-core = { version = "0.20.0", features = ["parallel"] }`

Do NOT add `linalg`. Do NOT change `pyo3`, `numpy`, or any other dependency.

---

## Architecture Patterns

### System Architecture (this phase only)

```
Cargo.toml (line 18 version string)
        |
        v
cargo build / maturin develop  ←  Cargo.lock regenerated on disk (NOT committed)
        |
        v
.venv/lib/.../fdars/_native.so  ←  rebuilt extension installed in venv
        |
        v
.venv/bin/python -m pytest tests/ -q  ←  604-test regression gate
```

### v5.0 Phase 30 Precedent

The immediately prior identical bump (0.17.0→0.20.0, Phase 30) required TWO wildcard arms on `CvCriterion` in `src/smoothing_mod.rs` — both are now already present in the codebase. The 0.20.0→0.23.0 bump, as established by the enum-site audit above, requires ZERO such fixes.

**Direct template from Phase 30:** `.planning/milestones/v5.0-phases/30-crate-bump-regression-gate/30-01-PLAN.md` — the task structure is a 2-task plan (build tracer → regression gate). Phase 36 can use the identical shape but with the tracer task simplified to a single Cargo.toml edit (no `smoothing_mod.rs` fix).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Extension rebuild | Manual `cargo build --lib` | `maturin develop` — installs into the active venv correctly |
| Test execution | Custom test runner | `.venv/bin/python -m pytest tests/ -q` — picks up the compiled extension |
| Cargo.lock update | Manual edit | Automatic on `cargo build` / `maturin develop` — regenerated in place |

---

## Common Pitfalls

### Pitfall 1: Committing Cargo.lock
**What goes wrong:** `Cargo.lock` is gitignored by repo policy (`pyfda/.gitignore`). Including it in the bump commit adds 1000+ lines of noise and violates the "one isolated commit, only `Cargo.toml`" gate.
**How to avoid:** Explicitly stage only `Cargo.toml` (`git add Cargo.toml`), never `git add -A` or `git add Cargo.lock`.
**Warning signs:** `git status` shows `Cargo.lock` as untracked after `maturin develop` — that is expected and correct; do not stage it.

### Pitfall 2: Accidentally enabling `linalg`
**What goes wrong:** `linalg` activates `faer 0.23` and `anofox-regression 0.4`, which require Rust 1.84+ (above pyfda's MSRV 1.83). Build fails with `error[E0554]: #![feature(trait_alias)]` or similar nightly-only feature errors.
**How to avoid:** After editing, grep the final `Cargo.toml` for `linalg` — it must not appear.
**Warning signs:** Compiler error referencing `faer` or `anofox` after the bump.

### Pitfall 3: Assuming the test count from SUMMARY.md
**What goes wrong:** The milestone research SUMMARY.md cited ~560 tests — stale from before the v5.0 suite grew. The actual count via `--collect-only` is **604 tests collected**; the live run excluding the 4 live-provider files (`test_advisor_live_integration.py`, `test_advisor_gemini.py`, `test_advisor_openai.py`, `test_advisor_ollama.py` — which require network credentials) produced **558 passed, 1 skipped** in a full execution this session. A plan that asserts "426 passed" (v4.0 count from Phase 30 plan) will fail its own acceptance criteria.
**How to avoid:** The acceptance criterion should be "0 failures; passes/skips matching the pre-bump baseline". Run `.venv/bin/python -m pytest tests/ -q` and accept whatever pass/skip count the current suite produces — the sole gate is zero failures (not an exact number).
[VERIFIED: `.venv/bin/python -m pytest tests/ --collect-only -q` → `604 tests collected in 0.73s`; live run with 4 live-provider files excluded → `558 passed, 1 skipped in 187.36s`]

### Pitfall 4: Running `cargo build` instead of `maturin develop`
**What goes wrong:** `cargo build --lib` builds the cdylib but does NOT install it into the venv. Subsequent `pytest` calls run against the OLD extension binary, silently passing against v0.20.0 while the new Cargo.lock resolves v0.23.0. The regression gate is not actually exercised.
**How to avoid:** Always use `maturin develop` to rebuild and install in one step.

### Pitfall 5: Running pytest without the venv
**What goes wrong:** System `pytest` or a different Python may not have the compiled `fdars._native` extension installed.
**How to avoid:** Use the project venv explicitly: `.venv/bin/python -m pytest tests/ -q` from the project root.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (installed in `.venv/lib/python3.14/site-packages/`) |
| Config file | `conftest.py` in project root (markdown-exec globals, snippet expansion) |
| Quick run command | `.venv/bin/python -m pytest tests/ -q` |
| Full suite command | `.venv/bin/python -m pytest tests/ -q` (same — no separate quick/full split) |

### Phase Regression Gate (all observable checks)

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Cargo pin correct | `grep 'fdars-core' Cargo.toml` | Prints `fdars-core = { version = "0.23.0", features = ["parallel"] }` |
| No `linalg` token | `grep -c linalg Cargo.toml` | Prints `0` |
| Rust build green | `cargo build 2>&1 \| tail -5` | Exits 0; no `non-exhaustive patterns` error |
| Extension installs | `maturin develop` (in `.venv`) | Exits 0; reports `Installed fdars-0.6.0` or similar |
| Regression gate | `.venv/bin/python -m pytest tests/ -q` | Exits 0; 604 collected, 0 failed |
| Rust linting | `cargo fmt --check && cargo clippy -- -D warnings` | Both exit 0 (no source Rust changes, so trivially clean) |
| Cargo.lock NOT staged | `git diff --cached --name-only` | Shows only `Cargo.toml`; `Cargo.lock` absent |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/ -q` (full suite — there is only one task commit in this phase)
- **Phase gate:** Same — full suite green before `/gsd-verify-work`

### Wave 0 Gaps

None — existing test infrastructure covers the phase requirements. This phase adds NO new test files.

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | no | Phase adds no new input paths |
| V6 Cryptography | no | No cryptographic operations |
| V2 Authentication | no | Library, no auth |

### Threat Register

| Threat | STRIDE | Mitigation |
|--------|--------|------------|
| Compromised `fdars-core 0.23.0` crate on crates.io | Tampering | Same first-party dependency as v0.20.0 (sipemu/fdars, same maintainer as pyfda). Version bump of an already-trusted dep; not a new package introduction. Cargo.lock pins exact resolved versions post-bump. |

---

## Package Legitimacy Audit

> Phase installs no NEW packages — only version-bumps a pre-existing dependency.

| Package | Registry | Verdict | Disposition |
|---------|----------|---------|-------------|
| `fdars-core` 0.23.0 | crates.io | OK (pre-existing dep, same maintainer) | Approved — version bump only |

The Package Legitimacy Gate (which applies to newly installed packages) is not triggered. The STACK.md crates.io provenance verification covers the bump.

**Packages removed due to SLOP verdict:** none
**Packages flagged as suspicious:** none

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `cargo clippy -- -D warnings` will pass with no source changes to Rust files | Validation Architecture | Extremely low risk — no Rust source files modified in this phase; clippy gates only on changed code in CI. If clippy surface changes because of a new transitive dep, it would be a new error unrelated to our change. |

**All other claims in this document are verified** from file reads and git diffs performed this session.

---

## Open Questions

None. The compile-break audit is complete and the answer is unambiguous: no wildcard arms need to be added. The only question the phase opens is numeric drift in the test suite (whether any existing test tolerances break against 0.23.0 numerics) — the plan must document this as a contingency, but the v5.0 Phase 30 precedent (zero tolerance changes needed for the 0.17→0.20 bump) makes this low-risk.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Rust toolchain (`stable`) | `maturin develop` / `cargo build` | ✓ | checked via `rust-version = "1.83"` in Cargo.toml | — |
| Python 3.14 venv | `maturin develop` target | ✓ | `.venv/bin/python3.14` exists | — |
| `maturin` | Extension rebuild | ✓ | in `.venv/bin/` | — |
| `pytest` | Regression gate | ✓ | in `.venv/bin/` (604 tests collected) | — |

---

## Sources

### Primary (HIGH confidence — read this session)

- `/home/simonm/projects/rust/pyfda/Cargo.toml:18` — current version pin; verbatim quote above
- `/home/simonm/projects/rust/pyfda/src/smoothing_mod.rs:193–215` — `CvCriterion` string-to-enum and enum-to-string matches; wildcard confirmed present
- `/home/simonm/projects/rust/pyfda/src/basis_mod.rs:250–276, 536–572` — `BasisCriterion` (exhaustive, non-`#[non_exhaustive]`); `ProjectionBasisType` (wildcard present)
- `/home/simonm/projects/rust/pyfda/src/explain_mod.rs:160–177, 340–357` — `SignificanceDirection` matches (wildcard present)
- `/home/simonm/projects/rust/pyfda/src/spm_mod.rs:698–705` — `Option<T>` matches (not enum exhaustiveness)
- `git diff v0.20.0 v0.23.0 -- fdars-core/src/depth/dispatch.rs` — `DepthMethod` new variants (existing pyfda code does NOT match on `DepthMethod` enum values directly — only string dispatch)
- `git diff v0.20.0 v0.23.0 -- fdars-core/src/smooth_basis.rs` — empty diff (file unchanged)
- `git diff v0.20.0 v0.23.0 -- fdars-core/src/smoothing.rs` — empty diff (file unchanged)
- `git diff v0.20.0 v0.23.0 -- fdars-core/src/basis/projection.rs` — only `serde` derive added; no new variants
- `.venv/bin/python -m pytest tests/ --collect-only -q` — 604 tests collected

### Cited (MEDIUM confidence — from milestone research, not re-derived)

- `.planning/research/STACK.md` — bump verdict, MSRV, linalg, dependency-additivity
- `.planning/research/SUMMARY.md` — executive summary, phase ordering rationale
- `.planning/milestones/v5.0-phases/30-crate-bump-regression-gate/30-01-PLAN.md` — Phase 30 precedent: task structure, CvCriterion wildcard arm history

---

## Metadata

**Confidence breakdown:**
- Compile-break audit: HIGH — every enum match site read directly from source this session; diffs between v0.20.0 and v0.23.0 read from local fdars-core checkout
- Standard stack: HIGH — re-confirmed from STACK.md (already HIGH)
- Test count: HIGH — collected live from `.venv/bin/python -m pytest --collect-only`
- Pitfalls: HIGH — v5.0 Phase 30 plan read directly + enumerated from code review

**Research date:** 2026-08-20
**Valid until:** Until the next fdars-core bump — no web lookups needed; all facts are local
