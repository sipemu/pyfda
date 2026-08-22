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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 — Documentation Overhaul | ~2 | 1–9 | Section-by-section sweeps with per-section review gates; style/determinism/doc-test guardrails established first |
| v2.0 — Grounded AI analysis advisor | ~2 | 10–13 | Tracer-first per phase; one deterministic core fanned out to four surfaces; offline-by-default + env-gated LLM tests |
| v2.1 — Document the AI Advisor | 1 | 14–18 | Fully autonomous run (discuss→…→cleanup); orchestrator self-served per-page review gates; execution-sentinel doc-tests; illustrative-vs-executed fence split |

### Cumulative Quality

| Milestone | Verification | Zero-Dep Additions |
|-----------|-------------|--------------------|
| v1.0 | All diagram/example sections reviewed on built site; SVGO idempotence gate (43 diagrams) | Hand-authored inline SVG only (no new runtime deps) |
| v2.0 | Phase 10 5/5, Phase 11 9/9, Phase 12 4/4 must-haves (111 tests), Phase 13 6 skill tests + human UAT (1 passed, 0 issues) | `anthropic`/`pydantic`/`mcp` all optional extras; core stays offline |

### Top Lessons (Verified Across Milestones)

1. Tracer-first, guardrails-first: prove the end-to-end path (or the CI gate) before adding breadth.
2. Keep the deterministic core dependency-free and gate everything optional (network, LLM, heavy extras) so CI stays fast and offline.
