# Milestone Context — v5.0 (proposed): fdars-core 0.20 Upgrade — Functional Inference + Depth/Boxplot Bindings & Docs

**Captured:** 2026-08-17 (pre-research checkpoint; scope confirmed with user)
**Status:** Ready for `/gsd-new-milestone` to consume → research → requirements → roadmap. (Questioning already done — do NOT re-ask; present the summary below for confirmation, then proceed.)

## Goal (one sentence)

Upgrade the pinned `fdars-core` from **0.17.0 → 0.20.0**, expose the new upstream functional-inference + depth/boxplot + basis/smoothing capabilities through PyO3 bindings + the Python API, extend the v3.0 AI advisor where relevant, and document everything to the project's method-accurate standard (hand-authored inline SVG diagrams + runnable offline worked examples). Same shape as the v4.0 milestone.

## Version target (user-decided)

- **0.20.0** (the true latest). Note: 0.18.0 was an audit-only release (no code); 0.19.0 added the inference suite; 0.20.0 added table-stakes quick wins. Both 0.19 and 0.20 are **additive / non-breaking, no new Rust or Python dependencies** (upstream release notes explicitly state existing signatures unchanged).
- Cargo pin `fdars-core = "0.17.0"` caret-locks to <0.18, so an explicit bump to `"0.20.0"` is required. Keep `features = ["parallel"]`; do NOT enable `linalg` (needs Rust 1.84 > pyfda MSRV 1.83, per v4.0 Phase 25).

## New upstream API surface to bind (from release notes v0.19.0 + v0.20.0)

### Group A — Functional inference (NEW `inference/` module; fdars' first inference surface)
Two-sample tests (permutation tests default 999 perms + deterministic `seed`; all return `TestResult { statistic, p_value, n_perm }`):
- `t_perm_test` — integrated L2-of-difference permutation test
- `f_perm_test` — integrated-F permutation test
- `two_sample_mean_test` — Hotelling T² on a shared FPC basis
- `mean_scb` — Degras simultaneous confidence bands for the mean
- `scb_two_sample_test` — SCB around the mean difference

Functional-linear-model inference (operate on a fitted `FregreLmResult`):
- `flm_f_test` — overall-significance F-test
- `flm_gof_test` — Ramsey–RESET-style residual lack-of-fit GOF
- `oneway_anova_vstat` — asymptotic one-way functional ANOVA V-statistic (Satterthwaite scaled-χ²), alongside the existing permutation `fanova`

### Group B — Depth & functional boxplot
- `functional_depth(data, method: DepthMethod)` — unified self-depth dispatcher; `DepthMethod { FraimanMuniz{scale}, Band, ModifiedBand, RandomProjection{nproj, seed} }`
- `functional_boxplot(data, method, factor) -> FunctionalBoxplotResult` — canonical López-Pintado–Romo functional boxplot: numeric median / 50% central region / fence / outlier-flag outputs (no plotting)

### Group C — Basis & smoothing quick wins
- `constant_basis(t) -> Vec<f64>` — m×1 all-ones intercept column
- AIC smoothing-parameter selection: `CvCriterion::Aic` + `aic_smoother` (kernel bandwidth) + `smooth_basis_aic` (basis roughness λ), reusing the GCV hat-matrix trace. Note `CvCriterion` is now `#[non_exhaustive]` → wrappers need a forward-compatible fallback arm.

## Proposed shape (for the roadmapper — mirrors v4.0)

- **Phase 1 — Crate bump + regression gate** (bump 0.17→0.20, rebuild, full suite green; the 426-test suite is the regression gate; additive/non-breaking expected). Blocks everything.
- **Phase(s) 2–3 — New bindings** (parallel-eligible after the gate):
  - Group A: NEW `fdars.inference` submodule (new `src/inference_mod.rs`, registered via `register_submodule!` in lib.rs + `_submodule_names`), mirroring the v4.0 `fdars.represent`/`fdars.scoring` new-submodule pattern. `TestResult` → PyDict (established convention). Confirm exact 0.20 signatures + which take an `FregreLmResult` handle vs raw arrays.
  - Group B: `functional_depth` (unified dispatcher — string `method` param + `#[non_exhaustive]` fallback arm; DepthMethod variant params like `scale`/`nproj`/`seed`) extends `fdars.depth`; `functional_boxplot` → `FunctionalBoxplotResult` PyDict (median/region/fence/outliers).
  - Group C: `constant_basis` + AIC smoothing (`aic_smoother`, `smooth_basis_aic`, `CvCriterion::Aic` string) extend `fdars.basis` / `fdars.smoothing`.
- **Phase — Advisor extension (where relevant):** an `inference` diagnostics aspect (summarize `TestResult` p-values/statistics — grounded, fdars-computed) and/or functional-boxplot outlier diagnostics on an outliers/depth aspect; keep the grounding invariant + MCP `_DIAGNOSTICS_METHODS` guard-sync (single atomic commit) exactly as v4.0 Phase 28. Confirm advisor scope during discuss/research.
- **Phase — Docs:** new dedicated pages + method-accurate hand-authored inline SVG diagrams + runnable offline `FDARS_FENCE_OK` worked examples for inference (two-sample tests, SCB bands, functional ANOVA), functional boxplot, and the basis/smoothing additions; whole-site `mkdocs build --strict` green. Note: docs build is ~18 min (executed fences run real compute) — keep fence data small.

## Reuse from v4.0 (don't re-derive)

- New public API namespaces mirror upstream module names where clean (`fdars.inference` for the new `inference/` module) — the v4.0 `fdars.represent`/`fdars.scoring` precedent.
- Binding conventions: string enums + `match` + `#[non_exhaustive]` fallback arm; compound results → PyDict; matrix returns via `fdmatrix_to_numpy2d` with a multi-curve transposition round-trip test (#33 class); fallible fns via `to_pyresult()`, no `.unwrap()`; `pytest.raises(ValueError)` for degenerate inputs.
- Advisor: full grounded treatment (`build_diagnostics` + `_ASPECT_PRIMERS` entry), offline-determinism tests (byte-identical `json.dumps`, no numpy scalars), guard-sync atomic commit.
- CI now green on `main` (v4.0 post-release fixes: pyyaml + pytest-asyncio in CI install/`[dev]`; gemini `skipif<3.10`; `fail-fast: false`; rustfmt). Package is 0.5.0 on PyPI.
- Docs/diagram recipe: STYLE_SPEC.md, SVGO idempotence + determinism gates, `PYTHONPATH=scripts DOCS_FAST=1 mkdocs build --strict`, `rsvg-convert` for PNG method-accuracy review, human-verify diagram checkpoint.

## Open questions for research / discuss (fresh session)

- Exact 0.20.0 signatures + return-struct field names (`TestResult`, `FunctionalBoxplotResult`) — verify against docs.rs/fdars-core/0.20.0 or the crate source before writing wrappers.
- How the FLM inference functions consume a fitted model — does the Python side pass a `FregreLmResult` handle, or re-fit? (affects the `fdars.inference` API ergonomics.)
- Advisor scope: which of inference/boxplot deserve a grounded advisor aspect vs docs-only.
- Datasets for worked examples (two-sample tests need two groups — e.g. growth by sex, phoneme classes, canadian_weather regions).

## Key context

- Crosses back into binding + advisor + docs code (`Cargo.toml`, `src/*_mod.rs`, `python/fdars/`, `python/fdars/advisor`, `python/fdars/mcp`, `docs/`). Grounding invariant is the hard constraint on any advisor work. Large scope — the roadmap phases it (bump → bindings ∥ → advisor → docs), same as v4.0.
