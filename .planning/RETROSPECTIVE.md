# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.0 — Grounded AI analysis advisor

**Shipped:** 2026-08-10
**Phases:** 4 (10–13) | **Plans:** 11 | **Sessions:** ~2 (2026-08-09 → 2026-08-10)

### What Was Built
- A deterministic, offline `build_diagnostics(result, method, …)` core (five method branches: alignment, fpca, basis, smoothing, clustering) that computes every diagnostic with fdars — no LLM/network dependency.
- A grounded `advise()` layer returning a schema-validated `Advice` via Claude structured outputs (`claude-opus-4-8`), with every recommendation carrying `action`/`kind`/`rationale`/`expected_effect`/`evidence` and citing diagnostic values.
- Four surfaces over that one core: Python API (recommend-only, `[advisor]` extra), Tool/MCP (`fdars.mcp`, `[mcp]` extra, stdio server + `HandleRegistry` by-reference + agentic re-run/compare loop), and an Anthropic Agent Skill (`.claude/skills/fdars-advisor/`).

### What Worked
- **Tracer-first plans.** Every phase opened with an end-to-end tracer plan (e.g. 10-01 schema+one-branch+advise, 12-01 in-process `Client(mcp)` list+invoke) that de-risked integration before breadth was added. Phase 13's tracer even pre-built the Plan 02 deliverables, so wave-2 was green on first run.
- **One deterministic core, many surfaces.** Deciding early that fdars owns all numbers and the LLM only interprets kept the grounding invariant enforceable by a single Pydantic schema + system prompt across all four surfaces — no per-surface re-litigation.
- **Offline-by-default testing.** `[advisor]`/`[mcp]` as optional extras + env-gated LLM tests meant CI stayed network-free and key-free while the real-key path was still covered by human UAT.

### What Was Inefficient
- **Stale CONTEXT artifacts surfaced at close.** Phase 12's "Open questions for research" were answered during execution but never checked off, tripping the pre-close audit and forcing an override_closeout. Marking research questions resolved at phase transition would have avoided it.
- **v1.0 was never formally closed** via `/gsd-complete-milestone`, so its phases lingered as "unstarted" in ROADMAP.md and the v2.0 close needed `--force`. Closing each milestone with the tool keeps the roadmap honest.
- A couple of smoothing-diagnostics edge cases (empty `gcv_values`, single-fit scalars) needed follow-up branches (Branch A-prime) discovered only when the compare loop demanded a non-empty delta.

### Patterns Established
- **Grounding invariant as a hard contract:** schema (`Advice`/`Recommendation`) + system prompt, verified by human UAT — the reusable template for any future LLM surface in this repo.
- **By-reference data passing across tool boundaries** (`HandleRegistry`: dataset/result IDs, never raw arrays through the model) — the pattern for any future MCP/tool work.
- **Optional-extra + env-gate** as the standard way to add an LLM/network dependency without breaking offline CI.

### Key Lessons
1. Resolve and check off phase CONTEXT "open questions" at phase transition — unchecked research questions read as open blockers at milestone close.
2. Close every milestone through `/gsd-complete-milestone` so ROADMAP/REQUIREMENTS stay collapsed and the next milestone doesn't inherit stale state.
3. A single deterministic compute core behind a thin, schema-validated LLM layer is the cheapest way to keep "no fabricated numbers" true across many surfaces.

### Cost Observations
- Model mix: adaptive profile (`claude-opus-4-8` for the advisor runtime + planning; sonnet/haiku for mechanical steps).
- Sessions: ~2 across 2026-08-09 → 2026-08-10; 67 commits.
- Notable: pre-building Plan 02 work inside the Plan 01 tracer (Phase 13) collapsed two waves into one green run.

---

## Milestone: v2.1 — Document the AI Advisor

**Shipped:** 2026-08-11
**Phases:** 5 (14–18) | **Plans:** 5 | **Tasks:** ~16 | **Commits:** 37

### What Was Built
A new top-level "AI Advisor" docs-site section documenting the shipped v2.0 advisor: a concept/grounding-invariant overview with two hand-authored inline SVG diagrams (grounding invariant, advisor loop), per-surface pages (Python API with an offline worked example that executes in the docs build; Tool/MCP with the 3 tools + by-reference handle model + re-run/compare loop; Agent Skill with git-URL install + walkthrough), all wired into `mkdocs.yml` nav and passing a `mkdocs build --strict` gate.

### What Worked
- **Run entirely autonomously via `/gsd-autonomous`** — full discuss→plan→plan-check→execute→verify→transition per phase, then audit→complete→cleanup, with the orchestrator self-serving the per-page human-review gates (reading the built page + source, rendering diagrams) rather than pausing.
- **Source-of-truth grounding** — every page planned/executed with `read_first` pointed at `advisor.py`/`mcp/server.py`/`SKILL.md`; the plan-checker caught a weak "text-present ≠ executed" verify on Phase 15 and forced an execution-sentinel (`FDARS_FENCE_OK`) gate.
- **Pre-scouting the next phase while a background agent ran** kept the pipeline moving with no idle wall-clock.
- **Offline-build discipline** — only the Python API page carries an executed fence; MCP/Skill fences are illustrative, so the build never needs the `[mcp]`/`[advisor]` extras, Python 3.10+, or an API key.

### What Was Inefficient
- The full markdown-exec build is slow (~7 min), so build-based verifies dominated phase wall-clock and repeatedly exceeded a 2-minute shell timeout (had to background them).
- Sibling pages forward-linked not-yet-authored pages with "coming in Phase N" annotations; those went stale once all pages existed — caught only by the milestone integration checker, then fixed inline (7 edits).

### Patterns Established
- **Execution-sentinel doc-test:** prove a docs fence actually executed by printing a unique marker and grepping the *built HTML*, not the source.
- **Illustrative-vs-executed fence split** to keep an optional-dependency feature documented without making the build depend on it.
- **Orchestrator-self-served review gates** for autonomous doc runs: automated accuracy greps + rendered-diagram inspection + source spot-checks stand in for the human gate, fixing defects inline.

### Key Lessons
- A diagram label-overlap (advisor-loop Python-API box) and 7 stale cross-refs both slipped past automated gates but were caught by visual/integration review — objective build gates don't replace a semantic once-over.
- The `--strict` build validates links but not stale "coming soon" prose; a dedicated integration pass is worth it at milestone close.

### Cost Observations
- Model mix: planners/roadmapper opus; executors/verifier/integration sonnet; plan-checkers haiku.
- Sessions: 1 (single autonomous run).
- Notable: background subagents + next-phase pre-scouting overlapped planning with execution, so orchestrator context stayed lean across all 5 phases.

---

## Milestone: v4.0 — fdars-core 0.17 Upgrade — New Bindings, Advisor & Docs

**Shipped:** 2026-08-17
**Phases:** 5 (25–29) | **Plans:** 11 | **Tasks:** 16

### What Was Built
Upgraded `fdars-core` 0.14.0 → 0.17.0 and bound the new upstream surface: `fdars.represent` (spline interpolation + `ExtrapolationPolicy` + `impute_missing_values`), functional statistics + `depth_based_median`/`trim_mean` in `fdars.fdata` with six new `Fdata` methods, a new `fdars.scoring` submodule (5 Simpson-integrated metrics), and `fdars.alignment` additions (least-squares shift registration + `fd.shift_register()`, 3 registration-quality scores, banded elastic alignment). Extended the advisor with a `scoring` aspect (#13) + imputation/registration diagnostics, and shipped 6 new docs pages + 6 method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples. Suite grew 259 → 426 passed / 4 skipped; whole-site `mkdocs build --strict` green offline.

### What Worked
- **Crate-bump-as-isolated-gate first.** Landing 0.17.0 + a full regression pass before any new binding work meant the one numeric change (faer FPCA SVD) was measured in isolation — and it turned out to need zero tolerance changes, so all later phases built on a proven-green baseline.
- **Milestone-level research reused across binding phases.** The four research reports (STACK/FEATURES/ARCHITECTURE/PITFALLS) pre-resolved exact 0.17 signatures, the #33 transposition trap, and the guard-sync/atomic-commit requirement — so per-phase research was skipped and planners/executors worked from accurate specs.
- **Tracer-first + multi-curve transposition tests** caught the column-major class deterministically; `depth_based_median` returning the observed curve and `trim_mean(α=0)==mean` were asserted exactly.
- **Self-review of diagrams via rsvg-convert PNG rendering** let the orchestrator catch/confirm method-accuracy (rigid-shift-vs-warp, depth-median-vs-synthetic, Sakoe–Chiba corridor) before the human sign-off gate.

### What Was Inefficient
- **Docs build is ~18 min** because executed worked-example fences run genuine fdars compute; multiple concurrent builds piled up and needed manual cleanup. Lighter fence datasets / figure caching would make CI docs builds far cheaper.
- **One executor process was interrupted mid-run** (26-02) — recovered cleanly because it had made zero partial commits (safe-resume gate), but confirms the value of the clean-tree + no-partial-work check before re-dispatch.
- Executor commit granularity occasionally coarser than the task structure (27-02) — work was fully committed, but per-task commits aid traceability.

### Patterns Established
- New public API namespaces mirror upstream fdars-core modules where it reads cleanly (`fdars.represent`, `fdars.scoring`) rather than bloating existing modules — decided per-milestone via smart-discuss.
- Advisor guard-sync (`_supported` ↔ MCP `_DIAGNOSTICS_METHODS`) edits must land in ONE atomic commit; offline-determinism tests assert byte-identical `json.dumps` + no numpy scalars.

### Key Lessons
- For a dependency-catch-up milestone, an isolated bump+regression phase is worth its own phase — it de-risks everything downstream for a small cost.
- Executed-fence docs are powerful (examples provably run against the real API) but their build cost scales with the compute in each fence — keep fence data small by design.

### Cost Observations
- Model mix: planners/roadmapper opus; executors/verifiers/integration sonnet; plan-checkers haiku.
- Sessions: 1 (single autonomous `/gsd-autonomous` run across all 5 phases).
- Notable: background subagents kept orchestrator context lean; the ~18-min docs builds dominated wall-clock in Phase 29.

---

## Milestone: v6.0 — fdars-core 0.23 Upgrade — Regression, PACE-FPCA, Depth/Outliers/Interval Inference

**Shipped:** 2026-08-22
**Phases:** 6 (36–41) | **Plans:** 11

### What Was Built
Bumped `fdars-core` 0.20.0 → 0.23.0 (parallel-only, no linalg) and exposed the new surface across three groups: Group A regression (`concurrent_regression`, `functional_glm`), Group B PACE-FPCA over a novel sparse/irregular `IrregFdata` input + `elastic_multinomial`, Group C 9 depth methods + 4 outlier detectors + 3 interval-wise ITP tests. Extended four advisor aspects with grounded scalars, and documented everything with 6 method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` fences. 23/23 requirements; 772 passed / 4 skipped; whole-site strict build green.

### What Worked
- The now-standard shape (crate bump + regression gate → independent binding groups → advisor → docs) held for the third milestone running.
- The **blocking human diagram review** earned its keep: it caught an inverted hypograph/epigraph asymmetry in the functional-outliers diagram *and* the depth-functions prose that both the executor and the goal verifier had passed. Ground truth was settled by running the shipped `fdars` bindings directly rather than trusting the plan text.
- Resuming a partially-executed plan (41-02, salvaged from a prior stalled session) worked cleanly via the executor's per-task git-history skip.

### What Was Inefficient
- A prior stalled session left ~2 cores of orphaned `mkdocs` builds running for 4.5 hours; they silently slowed the active build until reaped. Docs builds detach past the 2-min tool timeout, so orphan hygiene between waves matters.
- The full whole-site strict build (~22 min, all fences at full size) dominated Phase 41 wall-clock; two of them were needed (initial gate + re-verify after the diagram fix).
- The ITP closure direction was mis-stated in RESEARCH/PLAN (adjusted ≤ raw); corrected to adjusted ≥ raw only via empirical API testing.

### Patterns Established
- **Worktree isolation off for docs phases:** doc-build fences hardcode the main-tree `.venv/bin/mkdocs` path, so executors must run sequentially on main — a worktree builds the wrong tree.
- **Build discipline for long docs builds:** one build at a time, backgrounded to a log and polled; finish all edits before launching the verifying build (MkDocs snapshots file content at build start).

### Key Lessons
- Automated verification + a goal verifier are necessary but not sufficient for *method-accuracy* — a human (or empirical ground-truth check against the shipped library) remains the backstop for "does this diagram actually depict what the method does."

### Cost Observations
- Model mix: orchestrator opus; executors/verifier/integration sonnet.
- Sessions: 1 autonomous `/gsd-autonomous --from 41` run (Phase 41 + full milestone lifecycle).
- Notable: two ~22-min whole-site builds dominated wall-clock; orphaned-build reaping recovered ~2 cores mid-run.

---

## Milestone: v9.0 — scikit-learn API Compatibility

**Shipped:** 2026-09-02
**Phases:** 5 (55–59) | **Plans:** 17

### What Was Built
`fdars.sklearn` — a pure-Python scikit-learn-compatible estimator layer over the current bindings: a shared `_BaseFdarsEstimator` (BaseEstimator contract, `argvals` constructor param, float32→64 cast, tags-API 1.3–1.8 feature-detect shim), a reason-coded `EXCLUDED_METHODS` coverage registry, and **28 estimators** across five families (transformers, regressors, classifiers, clusterers, outlier detectors) each passing the full `check_estimator` battery with zero exemptions. Native `Pipeline`/`GridSearchCV`/`cross_val_score` integration + interop with native sklearn estimators. New "scikit-learn API" docs section. Package 0.8.0 → 0.9.0, released to PyPI.

### What Worked
- **Triage-first scope discovery under a no-exemptions bar.** Phase 55 skeletoned ~30 candidates and ran the full check battery *before* implementing, turning "which methods can comply?" from a guess into a recorded PASS/EXCLUDE verdict. Reclassifying skeleton predict-quality failures as PASS-WITH-FIXES (not EXCLUDE) kept all six families in scope.
- **Stored-reference depth scoring** (`modified_band_1d(X, X_fit_)`) solved `check_methods_subset_invariance` for all six outlier detectors — a single pattern that unblocked the whole family.
- **FPCATransformer-first ordering** — building the central grid-changing hub before the predictors that consume it made the Pipeline story fall out naturally.
- **Feature-detect over version-compare** for the sklearn tags API let one shim span 1.3–1.8 (dev/CI runs 1.8; the `<1.7` cap only bites the Python-3.9 wheel).

### What Was Inefficient
- **Milestone close ran late and out-of-band.** The user drove straight to ship (docs/PyPI/green-CI) and the GSD lifecycle (audit → complete → cleanup) was skipped, leaving STATE.md at "Phase 59 in_progress / 80%" and no MILESTONES.md entry until a later, separate close pass.
- **Phase 59 shipped without a VERIFICATION.md**, forcing an override closeout — the deliverables were provably shipped, but the phase record had to be reconstructed from SUMMARYs + the live site.
- **Stale `deferred-items.md` triage snapshot** (9 Phase-56-era rows) surfaced as "open" at close even though Phases 57–58 had resolved them; the table-row form is un-acknowledgeable via the CLI and had to be resolved by editing the file directly.

### Patterns Established
- Under a "full compliance, no exemptions" bar, EXCLUDE is reserved for genuinely-structural mismatch; implementation-quality failures are PASS-WITH-FIXES deferred to the owning family phase.
- A full-matrix `parametrize_with_checks` gate over *all* wrapped estimators (1387 checks) as the milestone lock, with `test_no_pass_with_fixes_remaining` asserting the registry is clean.

### Key Lessons
- **Close the milestone in-band even when shipping is driven manually.** Skipping audit/complete leaves the planning record inconsistent with reality and forces an expensive reconstruction later. A shipped PyPI release is necessary but not sufficient for a clean GSD close.
- **Table-form `deferred-items.md` entries can't be CLI-acknowledged** — resolve them in-file with a `Status: Resolved` column (or a `- **Status:** resolved` field bullet) at the source.

### Cost Observations
- Model mix: orchestrator opus; executors/verifier sonnet.
- Notable: milestone-close CI/Docs went red on false-failures (advisor fences need pydantic in the docs env; FND-02 guard needs `fetch-depth:0`) — local `--strict` green ≠ CI green when the dev venv is a superset.

---

## Milestone: v10.0 — Diagram Quality & Accessibility Pass

**Shipped:** 2026-09-02
**Phases:** 6 (60–65) | **Plans:** 7 | **Tasks:** 9

### What Was Built
Docs-only diagram-quality successor to v7.0. A scored 156-SVG audit (`60-AUDIT.md`) gated the milestone; 90 concept diagrams were corrected (universal long-form `<title>`/`<desc>`/`aria-labelledby` + title-matching `aria-label`; 5 Major geometry/method-accuracy fixes incl. an elastic-clustering full redraw and shift-registration "elastic warp" removal); 3 new sklearn concept diagrams (COVER-01); elastic-clustering thumb re-synced; 58 gallery thumbs made decorative-accessible; STYLE_SPEC.md refreshed to the 93-diagram reality. Whole-site `--strict` + SVGO/determinism gates green; blocking human diagram review approved.

### What Worked
- **Audit-first gating.** The scored inventory turned "which diagrams are bad?" into an evidence-backed, per-section worklist — every downstream phase executed against data, not guesswork (same lesson as v7.0, reaffirmed).
- **Parallel worktree execution for disjoint work.** Running the three correction phases (61/62/63) concurrently in isolated git worktrees — disjoint SVG sets, merged to main with zero conflicts — cut wall-clock ~3× and proved that the v6.0 "sequential-on-main" rule is scoped to doc-build phases, not pure-SVG edits.
- **Method-accuracy discipline caught an audit error.** The audit speculated the outlier taxonomy should be "Phase"; the planner checked the docs prose, found canonical Magnitude/Shape/Amplitude, and mandated keeping "Amplitude." The verifier-vs-source cross-check works.
- **Consolidated human review at the final gate.** Per-phase verifiers flag visual items for diagram work by nature; carrying them into one GATE-03 review over the whole corrected set was cleaner than fragmenting the human gate.

### What Was Inefficient
- **Session-quota interruption mid-Phase-64.** An executor hit the account limit part-way; recovery required reconciling committed-vs-uncommitted work and finishing inline. Cost some orchestration overhead.
- **Stale STYLE_SPEC status lines** ("34 of 43") had drifted three milestones without being refreshed — SPEC-02 finally corrected them; a periodic spec-freshness check would prevent this.

### Patterns Established
- **Parallel-worktree correction batches** for disjoint-file docs work: manual `git worktree` off HEAD, one executor per worktree, sequential clean merge back. Reusable whenever phases touch non-overlapping file sets and run no shared build.
- **Inline quota-fallback close:** when quota blocks subagents, the orchestrator finishes concrete/automated gate work inline while preserving the one irreducible human gate.

### Key Lessons
- The "sequential-on-main / no-worktrees" docs constraint is really "no-worktrees *for doc-build phases*" — pure-SVG-edit phases parallelize safely. Encode constraints with their actual reason so they can be scoped correctly later.
- Refresh living spec docs (STYLE_SPEC) as part of any milestone that changes their subject, or the counts rot silently.

### Cost Observations
- Model mix: planners/verifiers opus+sonnet, executors sonnet, plan-checker haiku.
- Notable: parallel worktree execution was the single biggest wall-clock saver; the whole-site `--strict` build (~21 min) dominated the Phase-65 automated cost.

---

## Milestone: v11.0 — fdars-core 0.33 Upgrade — New Bindings, Advisor & Docs

**Shipped:** 2026-09-05
**Phases:** 8 (66–73) | **Plans:** 29 | **Tasks:** 65

### What Was Built
The fourth crate-upgrade wave (after v4/v5/v6) and the largest — a 10-minor jump `fdars-core` 0.23.0 → 0.33.0 absorbed as one isolated regression gate (zero numeric drift, 6 deprecated call sites suppressed, full changelog/match-arm audit in `66-AUDIT.md`), then six new binding families exposed through PyO3 + the Python API: `fdars.fts` (13 functional-time-series functions), function-on-function + additive scalar-on-function regression (`fdars.regression` extensions + new `fdars.scalar_on_function`), Fréchet regression + density FDA (`fdars.frechet` + new `fdars.density_fda`), multi-domain data + FAMM + advanced clustering (`PyMultiFunData`/`fdars.multi_fdata`, `fdars.famm`, `mfpca`/`spe_multivariate`, DBSCAN/KCFC/FunFEM/elastic), and shapelets + GAK metric (`fdars.shapelet` + 5 GAK functions in `fdars.metric`). Advisor extended with `fts`/`frechet` aspects + grounded diagnostics for the new methods (grounding invariant + atomic MCP guard-sync). Documented with new pages + 8 method-accurate hand-authored SVGs + offline `FDARS_FENCE_OK` worked examples; whole-site `--strict` green; blocking human diagram review approved. Suite 5650 passed / 10 skipped; package 0.9.0 → 0.10.0.

### What Worked
- **Isolated-bump gate at 10× the usual jump.** The v4/v5/v6 "bump alone on a green baseline first" play held even across a breaking-change-risk 10-minor jump — the changelog/match-arm audit front-loaded the risk into Phase 66, and every downstream binding family landed without an upgrade regression hiding underneath it.
- **Parallel worktree fan-out for the binding families.** Phases 67–71 are additive, disjoint-file binding groups; running them in isolated worktrees (with Phase 70 as the sole `spm_mod.rs` writer kept separate) parallelized the bulk of the milestone — the v10.0 disjoint-worktree pattern reused on Rust binding code, not just SVGs.
- **Atomic advisor guard-sync, again.** Adding `fts`/`frechet` method strings across advisor `_supported`, MCP `_DIAGNOSTICS_METHODS`, and the guard-sync test literal in single commits kept the LLM-free compute boundary provable — the same discipline from v4/v5/v6 Phase-28/34/40.
- **Transposition-guarded fixtures caught layout bugs early.** Every new binding was proven on a non-square fixture (e.g. 40×25, 30×25×18), so column-major round-trip errors surfaced in-phase rather than at integration.

### What Was Inefficient
- **Executor deaths mid-run required resume reconciliation.** The autonomous run lost executors part-way and had to reconcile committed-vs-uncommitted work before continuing — recurring autonomous-run overhead (also seen in v10.0's quota interruption).
- **Long whole-site `--strict` docs build (~22–35 min).** The executed fences run real compute; the single whole-site gate dominates Phase-73 wall-clock. Keeping fence data small helps but the floor is high.

### Patterns Established
- **Isolated-bump gate scales to large jumps.** A single green regression gate is worth proportionally *more* the bigger the jump — encode it as the standard opening phase for any crate-upgrade milestone regardless of minor-count.
- **Worktree fan-out for additive binding groups** (extending the v10.0 SVG pattern to `src/*_mod.rs`): one executor per disjoint module set, with any shared-file writer (here `spm_mod.rs`) held to a single phase.

### Key Lessons
- The breaking-change *risk* of a 10-minor jump turned out to be absorbable with an audit + deprecation-suppression pass — the fear (research flagged possible breaking changes) exceeded the reality (zero drift, only deprecations). Front-load the audit, don't front-load the dread.
- Autonomous runs need robust executor-death resume; treat mid-run reconciliation as expected, not exceptional.

### Cost Observations
- Model mix: planners/verifiers opus+sonnet, executors sonnet, plan-checker haiku.
- Notable: parallel-worktree binding fan-out was the biggest wall-clock saver; the ~22–35 min whole-site `--strict` build dominated Phase-73.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 — Documentation Overhaul | ~2 | 1–9 | Section-by-section sweeps with per-section review gates; style/determinism/doc-test guardrails established first |
| v2.0 — Grounded AI analysis advisor | ~2 | 10–13 | Tracer-first per phase; one deterministic core fanned out to four surfaces; offline-by-default + env-gated LLM tests |
| v2.1 — Document the AI Advisor | 1 | 14–18 | Fully autonomous run (discuss→…→cleanup); orchestrator self-served per-page review gates; execution-sentinel doc-tests; illustrative-vs-executed fence split |
| v9.0 — scikit-learn API Compatibility | ~3 | 55–59 | Triage-first scope discovery under a no-exemptions bar; full-matrix `parametrize_with_checks` gate as milestone lock; out-of-band manual ship forced a later in-band close (override for the unverified docs phase) |
| v10.0 — Diagram Quality & Accessibility Pass | ~2 | 60–65 | Parallel worktree correction batches for disjoint SVG sets; consolidated human review at the final gate; inline quota-fallback close |
| v11.0 — fdars-core 0.33 Upgrade | autonomous | 66–73 | Isolated-bump gate absorbed a 10-minor jump; parallel-worktree fan-out extended from SVGs to `src/*_mod.rs` binding groups; executor-death resume reconciliation |

### Cumulative Quality

| Milestone | Verification | Zero-Dep Additions |
|-----------|-------------|--------------------|
| v1.0 | All diagram/example sections reviewed on built site; SVGO idempotence gate (43 diagrams) | Hand-authored inline SVG only (no new runtime deps) |
| v2.0 | Phase 10 5/5, Phase 11 9/9, Phase 12 4/4 must-haves (111 tests), Phase 13 6 skill tests + human UAT (1 passed, 0 issues) | `anthropic`/`pydantic`/`mcp` all optional extras; core stays offline |

### Top Lessons (Verified Across Milestones)

1. Tracer-first, guardrails-first: prove the end-to-end path (or the CI gate) before adding breadth.
2. Keep the deterministic core dependency-free and gate everything optional (network, LLM, heavy extras) so CI stays fast and offline.
