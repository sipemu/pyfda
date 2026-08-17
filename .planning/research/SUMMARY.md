# Project Research Summary

**Project:** pyfda v5.0 — fdars-core 0.17.0 → 0.20.0 upgrade (functional inference + depth/boxplot + basis/smoothing)
**Domain:** PyO3 binding layer upgrade for functional data analysis library
**Researched:** 2026-08-17
**Confidence:** HIGH — all signatures verified against docs.rs; codebase patterns extracted directly; v4.0 retrospective validated

---

## Executive Summary

The v5.0 milestone is a structured binding upgrade that adds three groups of new functionality to pyfda while bumping its upstream dependency (fdars-core) from 0.17.0 to 0.20.0. The upgrade requires exactly one Cargo.toml change (version pin), zero new Rust/Python dependencies, and three parallelizable binding phases (inference, depth/boxplot, basis/smoothing) plus an advisor extension and documentation overhaul. The critical blocker before any new work: the existing `optim_bandwidth` binding's `CvCriterion` match requires a wildcard arm to accommodate the `Aic` variant now present in 0.20.0. Once that one-line fix lands in the crate-bump phase, the path is clear for 13 new bindings organized into 4 parallel execution groups. Risk is well-understood and mitigated by established v4.0 patterns (atomic commits, transposition round-trip tests, guard-sync enforcement).

---

## Key Findings

### Recommended Stack

The existing stack (Rust 1.83, PyO3 0.28, NumPy 0.28, Maturin 1.x) remains unchanged. The upgrade path is:

**Cargo.toml single change:**
```toml
fdars-core = { version = "0.20.0", features = ["parallel"] }  # was 0.17.0
```

**Why this is safe:**
- MSRV: pyfda 1.83 > fdars-core 0.20.0 MSRV 1.81 — no breaking requirement.
- Dependencies: The full dependency tree for `["parallel"]` is identical across 0.17.0, 0.19.0, 0.20.0 (nalgebra 0.33, rand 0.8, rustfft 6.2, rayon 1.10).
- **Do NOT enable `linalg` feature** — requires Rust 1.84 (breaks MSRV), pulls in faer+anofox-regression (not needed for v5.0 targets).
- No PyPI dependency changes required; all new result types decompose to PyDict (established pattern).

### Expected Features

The v5.0 launch surface contains **13 new bindings** across three groups:

**Group A — Functional Inference** (8 functions, NEW `fdars.inference` submodule):
- `t_perm_test`, `f_perm_test` — two-sample permutation tests
- `two_sample_mean_test` — asymptotic Hotelling T-squared on FPC basis
- `mean_scb`, `scb_two_sample_test` — simultaneous confidence bands (Degras multiplier-bootstrap)
- `flm_f_test`, `flm_gof_test` — FLM post-hoc inference (re-fit internally)
- `oneway_anova_vstat` — asymptotic one-way functional ANOVA

**Group B — Depth and Boxplot** (2 functions, extend `fdars.depth`):
- `functional_depth` — unified self-depth dispatcher
- `functional_boxplot` — Lopez-Pintado–Romo outlier detection

**Group C — Basis and Smoothing Quick Wins** (3 functions, extend `fdars.basis` + `fdars.smoothing`):
- `constant_basis` — all-ones intercept column
- `smooth_basis_aic` — AIC-optimal smoothing parameter selection
- `CvCriterion::Aic` extension — adds AIC to criterion dispatch

### Architecture Approach

Binding organization preserves three-layer architecture (Python → PyO3 → fdars-core):

1. **`src/inference_mod.rs`** — NEW file for Group A (8 functions). Follows `represent_mod.rs` (v4.0) precedent.
2. **`src/depth_mod.rs`** — EXTEND with `functional_depth` + `functional_boxplot` (Group B).
3. **`src/basis_mod.rs`** — EXTEND with `constant_basis` (Group C).
4. **`src/smoothing_mod.rs`** — EXTEND with AIC smoothing + `CvCriterion::Aic` arm (Group C).
5. **`src/lib.rs`** — ADD `mod inference_mod;` and `register_submodule!` call.
6. **`python/fdars/__init__.py`** — ADD `"inference"` to `_submodule_names` tuple.
7. **Advisor & MCP** — Atomic commit: add `"inference"` to `_supported` and `_DIAGNOSTICS_METHODS` (diagnostics-only, not runnable).

**Key patterns:**
- All result types decompose to PyDict (established v4.0 pattern).
- FLM inference re-fits internally via `fdars_core::scalar_on_function::fregre_lm` — no Python handle needed.
- String-to-enum dispatch with wildcard fallback for `#[non_exhaustive]` enums.

### Critical Pitfalls (Top 3)

**1. `CvCriterion` Non-Exhaustive Wildcard (Phase 1 blocker)**
Existing `optim_bandwidth` binding has no fallback arm. The 0.20.0 bump adds `CvCriterion::Aic`. **Fix in Phase 1:** add `_ => return Err(PyValueError...)` to match. One-line fix unblocks downstream phases.

**2. FLM Re-Fit Strategy (Phase 2 design lock-in)**
`flm_f_test` takes `&FregreLmResult` (non-exhaustive Rust struct). Python cannot reconstruct it. **Solution:** Accept `data + response + n_comp`, re-run `fregre_lm` inside wrapper. Matches existing `predict_fregre_lm` pattern.

**3. Seed Determinism for Permutation Tests (Phase 2+3 tests)**
`t_perm_test`, `f_perm_test`, and `functional_depth(method="random_projection")` require reproducibility. Python signature: `seed: Option<u64> = None` (default `42`). **Determinism test required:** two calls with same seed must return byte-identical `json.dumps` output.

---

## Implications for Roadmap

### Suggested Phase Structure

**Phase 1: Crate Bump + Regression Gate (2 days)**
- Cargo.toml: fdars-core 0.17.0 → 0.20.0
- Fix `optim_bandwidth` `CvCriterion` match wildcard arm
- `cargo test` and `pytest` all pass (426+ tests)

**Phase 2: Group A — Functional Inference Bindings (5 days)**
- `src/inference_mod.rs` (new file) with 8 functions
- `TestResult`, `ToleranceBand` to PyDict decomposition
- Determinism, shape assertion, input validation tests
- Research spike: Verify `MultiplierDistribution` variants and `ToleranceBand` fields (docs.rs 404 at research time)

**Phase 3: Group B — Depth/Boxplot Extensions (3 days)**
- `src/depth_mod.rs`: `functional_depth` + `functional_boxplot`
- `DepthMethod` string-dispatch with per-variant fields
- Transposition round-trip test (v4.0 guard pattern)
- Self-depth consistency test

**Phase 4: Group C — Basis/Smoothing Quick Wins (1 day)**
- `constant_basis` (trivial): returns `(m, 1)` array
- `smooth_basis_aic`: copy-paste of GCV binding
- `CvCriterion::Aic` extension: one match arm

**Phase 5: Advisor Extension (2 days)**
- `python/fdars/advisor/__init__.py` + `aspects/inference.py`
- `python/fdars/mcp/server.py` `_DIAGNOSTICS_METHODS` update
- **Atomic commit:** guard-sync test `test_diagnostics_methods_match_advisor_supported` enforces this
- Inference diagnostics-only (not in `_RUNNABLE_METHODS`)

**Phase 6: Docs Overhaul (8-10 days)**
- Hand-authored SVG diagrams (permutation test, SCB, boxplot)
- 5-6 worked examples (t-test, boxplot, FLM, ANOVA, AIC smoothing, basis construction)
- All executed fences: `n_perm <= 19`, `nb <= 50`, synthetic/subset data
- `mkdocs build --strict` gate

### Phase Ordering Rationale

1. **Phase 1 first:** Regression gate isolates bump risk from new-code issues (v4.0 pattern).
2. **Phases 2–4 sequential or parallel:** Independent binding groups; sequential recommended for focused review.
3. **Phase 5 after Phase 2:** Advisor needs inference bindings to exist.
4. **Phase 6 last:** Docs depend on all bindings + advisor stability.

### Research Flags

**Phases requiring plan-time research spike:**
- **Phase 2:** Verify `MultiplierDistribution` variants, `ToleranceBand` fields (docs.rs 404)
- **Phase 2:** Confirm FLM combined `fit_and_test` function or re-fit approach

**Phases with standard patterns (no spike needed):**
- **Phase 1:** Straightforward version pin + lock regeneration
- **Phase 3:** `DepthMethod` variants confirmed; round-trip test pattern from v4.0
- **Phase 4:** Copy-paste + one-line extension
- **Phase 5:** Atomic guard-sync pattern established in v4.0
- **Phase 6:** SVG/example development are creative tasks

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | HIGH | MSRV safety verified; dependency tree identical across versions; version history confirmed (0.18 never published). |
| **Features** | HIGH | All 13 function signatures verified against docs.rs 0.20.0. `MultiplierDistribution` variants and `constant_basis` signature flagged (docs.rs 404) — plan-time spike required. |
| **Architecture** | HIGH | Patterns extracted directly from codebase. Precedent established in v4.0 (`represent_mod.rs`, `scoring_mod.rs`). Guard-sync test verified in code. |
| **Pitfalls** | HIGH | 15 pitfalls from docs.rs, codebase, and v4.0 retrospective. Each has recovery strategy. Pitfall 12 (drift) validated by v4.0 (zero drift observed). |

**Overall confidence:** HIGH — Upgrade of established v4.0 pattern with well-verified upstream API and zero architectural unknowns.

### Gaps to Address

1. **`MultiplierDistribution` variants:** Research blocked by docs.rs 404. Action: Fetch from crates.io source during Phase 2 planning.
2. **`smooth_basis_aic` existence:** Listed in context but unverified. Action: Confirm against 0.20.0 source during Phase 4 planning.
3. **`constant_basis` signature:** Parameter name and return type unverified. Action: Confirm via docs.rs before coding.
4. **FLM combined fit+test:** Unknown if 0.20.0 exposes combined function. Action: Verify during Phase 2 planning.
5. **`DepthMethod` non-exhaustive status:** Inferred but not explicitly confirmed. Action: Verify wildcard arm requirement during Phase 3 planning.

---

## Sources

### Primary (HIGH confidence)
- **crates.io v1 API:** fdars-core version history, MSRV metadata
- **docs.rs fdars-core 0.20.0:** Function signatures, struct fields, enum variants and `#[non_exhaustive]` status

### Secondary (HIGH confidence)
- `/home/simonm/projects/rust/pyfda/Cargo.toml` — current pin, MSRV
- `/home/simonm/projects/rust/pyfda/src/` — binding patterns, conversions, module registration
- `/home/simonm/projects/rust/pyfda/python/fdars/` — advisor, MCP guard-sync patterns
- `/home/simonm/projects/rust/pyfda/tests/test_mcp_server.py` — guard-sync test enforcement

### Tertiary (MEDIUM confidence)
- **`.planning/RETROSPECTIVE.md` (v4.0):** Bump isolation, build cost, atomic commit requirements
- **Project conventions (CLAUDE.md):** Hand-authored diagrams, env var checks, method-accuracy validation

---

*Research completed: 2026-08-17*
*Ready for roadmap: yes*
