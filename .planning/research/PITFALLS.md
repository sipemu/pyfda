# Pitfalls Research

**Domain:** fdars-core 0.23 → 0.33 bump + new PyO3 bindings + advisor extension + docs (pyfda v11.0)
**Researched:** 2026-09-02
**Confidence:** HIGH — derived entirely from verified project history (PROJECT.md Key Decisions table,
shipped milestone retrospectives v4.0–v6.0, memory notes, and direct inspection of the current
codebase). Every pitfall below has either already occurred in this repo or is a direct structural
consequence of the codebase's design. Nothing here is speculative general risk.

---

## Scope

This file covers the **five risk areas** for v11.0: (1) crate bump regression risk across a 10-minor
jump, (2) binding-correctness patterns specific to pyfda's layout and PyO3 conventions, (3) the
advisor grounding invariant and guard-sync discipline, (4) docs method-accuracy and fence-build
constraints, and (5) process/execution constraints that caused failures in prior milestones.

Each pitfall maps to a specific phase guardrail and a concrete verification check.

---

## Critical Pitfalls

### Pitfall 1: Silent Numeric Drift Across a Large Minor-Version Jump

**What goes wrong:**
`cargo build` and `maturin develop` succeed after bumping `fdars-core` 0.23 → 0.33 — the Rust API
compiles clean. But one or more existing tests fail with values that are numerically correct but
outside their `approx::assert_relative_eq!` / `np.testing.assert_allclose` tolerances. In a 10-minor
jump, the upstream crate may have switched a linear algebra backend (e.g. the faer SVD migration that
appeared in 0.17 — zero drift observed then, but the risk of a second such migration increases over
10 releases) or tightened a convergence loop in a way that changes final floating-point values by
more than the tests' tolerances admit. Because the change is **numeric**, not structural, `cargo test`
alone does not catch it — only running the full Python test suite against the rebuilt wheel does.

**Why it happens:**
A 10-minor jump is unlike the 3-minor additive waves of v4.0/v5.0/v6.0. Over 10 releases, fdars-core
may have absorbed algorithm improvements that shift numerical outputs. The faer FPCA SVD migration
(0.15→0.17, tracked during v4.0 Phase 25) was the prior precedent — zero drift observed, but the
concern was real enough to gate Phase 25 on the full Python suite before any new bindings. The same
gate is mandatory here because the search space is ~3x larger.

**How to avoid:**
Land the bump alone in a dedicated regression-gate phase (Phase 66 per v11.0 convention). Run
`pytest` (full ~772-test Python suite) after `maturin develop --release` before committing any new
binding work. If tolerance failures appear, tighten or loosen tolerances only where the new value is
provably correct — do NOT silently suppress failures. Document any tolerance changes in the phase
VERIFICATION.md.

**Warning signs:**
- `cargo build` succeeds but `pytest tests/ -x` fails on a numeric assertion in an existing test.
- FPCA-related tests (test_fdata_stats.py, test_pace_fpca.py) differ by ~1e-8 or less in eigenvalues
  or scores — the signature of a backend change, not a real regression.
- Test count drops (a test that was skipped now crashes, or a fixture fixture no longer builds).

**Phase to address:**
Phase 66 (Bump regression gate) — the bump is its own isolated phase; no new bindings may be added
until the full Python suite is green.

---

### Pitfall 2: Silently Changed Default Parameters or Removed Algorithm Variants

**What goes wrong:**
A function that existed at 0.23 has the same name at 0.33 but a changed default parameter value or a
removed algorithm variant. The existing binding compiles and the existing tests pass (the test may
call the function with explicit parameters that still work), but a user calling with defaults gets a
different result. The most dangerous case: an enum variant that was valid at 0.23 (e.g. a
`DepthMethod`, `CvCriterion`, or `GlmFamily` string variant) was renamed or removed in a patch
between 0.24 and 0.33. The `#[non_exhaustive]` wildcard arms in the existing bindings would silently
route to the `ValueError` branch at runtime rather than at compile time.

**Why it happens:**
In Rust, a `#[non_exhaustive]` enum wildcard arm (`_ => return Err(...)`) means the binding continues
to compile even when the variant string it dispatches on changes name upstream. The Python test for
the old variant name would pass if the test catches `ValueError` — but a user who passes the same
variant name now gets an error where they previously got a result.

**How to avoid:**
Read the fdars-core 0.24–0.33 changelogs exhaustively during research, not just at point-of-binding.
Flag any renamed or removed variants in the research STACK.md. During the bump phase, verify that
every string dispatched in existing `match` arms still maps to a live enum variant: grep all
`match str_arg {` in `src/*_mod.rs`, then verify each arm string against the 0.33 API docs.
Also grep for any new `#[deprecated]` attributes in the fdars-core 0.33 source.

**Warning signs:**
- `cargo build` succeeds but `maturin develop` panics at runtime when calling an existing function
  with a variant string that used to work.
- A test that was skipped (e.g. a `pytest.mark.skip` awaiting upstream fix) now needs updating
  because the upstream fixed it differently than expected.
- `_DIAGNOSTICS_METHODS` in `server.py` lists an aspect string that no longer matches a live
  fdars-core method name.

**Phase to address:**
Phase 66 (Bump regression gate) — changelog audit is part of the bump phase pre-work, not deferred
to the binding phases.

---

### Pitfall 3: Row-Major / Column-Major Transposition Bug Invisible on Square Inputs

**What goes wrong:**
A new binding passes an `(n, n)` test (n observations, n grid points — a square matrix) and the
result looks correct. But in production with `n_obs != n_points`, the result is transposed: curves
appear as grid points and vice versa. The existing `convert.rs:numpy2d_to_fdmatrix` is correct for
the established functions, but any new binding that introduces a second matrix argument (e.g. a
reference dataset, a second group for two-sample tests, or a covariance kernel matrix) must also go
through the same converter. If the developer passes the second argument raw (via `as_array()` without
the column-major conversion), the result is silently wrong on non-square inputs.

The `beta_curve` transposition guard in `test_regression.py` (p=3 predictors, n=10 observations) is
the established precedent. Every new multi-array binding must have an equivalent non-square fixture.

**Why it happens:**
The `convert.rs` entry point is obvious for the first (data) argument. For secondary matrix arguments
(reference curves, kernel output, coefficient matrices), developers may reach for `arr.as_array()`
directly because the argument is already a numpy array and the conversion step "looks redundant" when
the input is square during development.

**How to avoid:**
For every new function that accepts a 2D numpy input: (a) route it through `numpy2d_to_fdmatrix`,
and (b) write a test where `n_obs != n_points`. The existing pattern is `n=30, m=21` (PACE-FPCA test)
or `p=3, n=10` (regression). Use dimensions that are coprime so an accidental transpose is caught
on shape alone. Assert the output array's shape is `(n_obs, ...)` not `(n_points, ...)` for the
row dimension.

**Warning signs:**
- A new binding test uses `n == m` (e.g. a 50×50 matrix) — the transposition is invisible.
- The test fixture is 1D or the function returns a scalar — transposition cannot be detected.
- A new multi-array function is tested only with the Canadian Weather dataset (35 curves × 365 points)
  which is rectangular but only tested via shape checks, not off-diagonal value checks.

**Phase to address:**
Each binding phase (67–69 per the anticipated v11.0 grouping) — each plan must include a non-square
transposition test for every 2D input argument in every new function.

---

### Pitfall 4: Forgetting argvals When the Core Function Does Not Take It — or Passing It When It Does

**What goes wrong:**
Two mirror-image mistakes exist in this codebase. (1) A new binding omits `argvals` from its Python
signature because the developer assumes the user always passes a default grid — but the fdars-core
function DOES require an explicit grid and produces wrong results or a Rust panic when the default
`[0, 1]` uniform grid is used on data with non-uniform spacing. (2) The binding passes `argvals` to a
core function that does NOT accept it (e.g. `functional_glm` at 0.23 takes no argvals per the
v6.0 Phase 37 discovery), causing a Rust compile error or a silently ignored argument.

The `default_grid` helper in `convert.rs` exists precisely because this distinction is not always
obvious from the function signature — some fdars-core functions accept optional `argvals`, others
have it baked in, others infer it from the data shape.

**Why it happens:**
For a 10-minor jump, the new upstream functions span a wide variety of capability families. Some
families (smoothing, depth) require argvals; others (classification, inference from fitted objects)
operate on transformed representations where the grid is no longer relevant. Developers default to
copying the nearest existing binding's signature without checking whether the core function takes
argvals.

**How to avoid:**
For every new function to be bound: read the fdars-core 0.33 API docs for the exact signature before
writing a single line of Rust binding code. Confirm explicitly whether the function takes argvals
and, if so, whether it is optional or mandatory. Annotate the binding with a comment `// argvals:
optional (default_grid) | mandatory | absent` on the first line.

**Warning signs:**
- A binding test passes a 1-point argvals `[0.0]` (the default_grid fallback) and the result is
  numerically plausible — but only because the test data happens to be normalized to [0, 1].
- A new binding compiles but `cargo test` fails at runtime with a fdars-core error about grid
  length mismatch.
- `functional_glm` or any fitting-from-handle function receives an argvals argument that never
  appears in the core signature.

**Phase to address:**
Each binding phase — the PLAN.md for each binding group must list, per function, whether argvals is
expected and what the default strategy is.

---

### Pitfall 5: Missing `#[non_exhaustive]` Wildcard Arms on New Enum Dispatch

**What goes wrong:**
A new capability introduces a string-dispatched enum (e.g. a new `DistanceKind`, `SmoothingFamily`,
or `BasisType` parameter). The binding encodes the known variants as match arms but omits the
wildcard arm `_ => Err(PyValueError::new_err(...))`. This compiles only if the enum is not
`#[non_exhaustive]` in the core crate. If it is `#[non_exhaustive]`, the missing wildcard arm is a
**compile error** — caught immediately. But if the developer adds a wildcard arm that silently
returns `Ok(None)` instead of `Err`, the user gets a silent `None` result for any unrecognized
variant string passed at runtime — a silent correctness failure, not a noisy error.

The established pattern (inference_mod.rs line 223, regression_mod.rs line 1120, depth_mod.rs
line 408) is: wildcard arm raises `PyValueError` with a descriptive message listing the supported
variant strings.

**How to avoid:**
Every new `match method_str { "variant_a" => ..., "variant_b" => ..., _ => Err(...) }` must use
the `Err` path in the wildcard, not `Ok(None)` or `Ok(Default::default())`. Add a test that passes
an invalid variant string and asserts `pytest.raises(ValueError)` with a message containing the
function name and "supported".

**Warning signs:**
- A new match block has `_ => Ok(None)` or `_ => Ok(vec![])`.
- A test for an invalid variant string expects `None` return rather than `ValueError`.
- The wildcard arm's error message does not list the valid variants (making it impossible for users
  to recover without reading source code).

**Phase to address:**
Each binding phase — code review criterion: grep new `*_mod.rs` files for `match` blocks and verify
every wildcard arm raises `PyValueError`.

---

### Pitfall 6: Breaking the Grounding Invariant — LLM Cites a Number fdars Did Not Compute

**What goes wrong:**
A new advisor aspect (or an extended existing aspect) produces a diagnostic dict that contains a
value the LLM mentions in its evidence string — but that value was computed in Python (e.g.
`len(result["outlier_indices"])`) rather than returned directly from fdars-core. The grounding
guard (`_check_grounding` in `providers/_validate.py`) only validates that numbers in the evidence
string appear in the diagnostic dict. If the diagnostic dict itself contains a computed-in-Python
derived value (not a fdars-computed scalar), the invariant is silently violated: the LLM is citing
a number that fdars did NOT compute, only Python did.

The invariant is: **fdars-core computes every number; the LLM only interprets and cites**. This
means `build_diagnostics` must pass through fdars-computed scalars verbatim, not transform them
first (e.g. rounding, percentage conversion, count-of-outliers derived from a list length).

**Why it happens:**
When binding a new function that returns a list of indices (e.g. outlier indices, change-point
locations), it is tempting to add `"n_outliers": len(result["outlier_indices"])` to the diagnostic
dict because `n_outliers` is the most useful scalar for the LLM to cite. But this number was derived
in Python, not returned by fdars-core, so the invariant is violated.

**How to avoid:**
In `build_diagnostics`, only include scalars that come directly from fdars-core result fields.
For list-valued fields (index lists, p-curves), reduce to a scalar via a method that fdars-core
itself would compute (e.g. a summary statistic that appears in the result struct). If no such scalar
exists, omit the field from diagnostics or leave it as metadata rather than a cited value.
Document the derivation chain for every diagnostic field in the aspect file.

**Warning signs:**
- A diagnostic dict field is computed as `len(x)`, `sum(x)`, `x[0]`, or `np.mean(x)` where `x`
  is a Python-layer derived value, not a raw fdars result field.
- The LLM evidence string cites a value that appears in the diagnostic dict but not in the raw
  fdars result dict (verifiable by comparing `build_diagnostics` output to the raw function output).
- `_check_grounding` passes but the number cited is a Python derivation.

**Phase to address:**
Advisor extension phase (Phase 70 per anticipated numbering) — every new diagnostic field must have
a comment `# fdars-computed: result["field_name"]` or `# Python-derived: NOT for LLM citation`.

---

### Pitfall 7: MCP `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` Guard Out of Sync with Advisor Aspects

**What goes wrong:**
A new advisor aspect is added to `build_diagnostics` in `advisor/aspects/`, the aspect is wired
into `_ASPECT_PRIMERS`, and tests pass for `advise()`. But `server.py:_DIAGNOSTICS_METHODS` is NOT
updated to include the new aspect string. The MCP `fdars_build_diagnostics` tool silently rejects
calls to the new aspect with a "method not supported" error, even though the Python API works fine.
The advisor phase verifier does not catch this because it only tests the Python API path.

The prior milestones treated guard-sync as a hard constraint: v4.0 Phase 28, v5.0 Phase 34, and
v6.0 Phase 40 each updated `_DIAGNOSTICS_METHODS` in the same atomic commit as the new aspect.
When v6.0 Phase 40 added four aspects, it confirmed that guard-sync was a no-op (no new runnable
methods, only diagnostics-only aspects) — but the check was still mandatory.

The mirror risk: `_RUNNABLE_METHODS` in both `server.py` and `_runner.py` must stay identical
(T-12-02 constraint). If a new method is added to `_runner._RUNNABLE_METHODS` but not to
`server._RUNNABLE_METHODS`, the MCP `fdars_run_method` tool accepts it in runner but rejects it in
the server dispatch — a runtime error that unit tests miss because they test runner and server
separately.

**How to avoid:**
Every commit that adds or removes an advisor aspect string MUST also update `_DIAGNOSTICS_METHODS`
in `server.py`. Every commit that adds or removes a runnable method string MUST also update both
`_runner._RUNNABLE_METHODS` and `server._RUNNABLE_METHODS` in the same commit. No split commits.
Run `test_guard_sync_version_independent.py` as the explicit verification check — this test exists
specifically for this invariant.

**Warning signs:**
- `build_diagnostics("new_aspect", ...)` passes in Python tests but `fdars_build_diagnostics` MCP
  tool returns "method not supported" for the same aspect string.
- `server._RUNNABLE_METHODS` and `runner._RUNNABLE_METHODS` have different frozenset contents —
  grep both files and diff the sets.
- The advisor phase plan does not mention guard-sync as an explicit task.

**Phase to address:**
Advisor extension phase — guard-sync is a mandatory task in the phase plan, not optional. The phase
VERIFICATION.md must confirm `_DIAGNOSTICS_METHODS` set equality by pasting both frozenset literals.

---

### Pitfall 8: numpy Scalars Leaking into `json.dumps` in Diagnostic Dicts

**What goes wrong:**
`json.dumps(diagnostics)` raises `TypeError: Object of type float64 is not JSON serializable` at
runtime when the advisor passes the diagnostic dict to the LLM prompt. The error does not appear
during `build_diagnostics` (which returns a Python dict, not JSON), only when the advisor actually
calls `json.dumps` to build the system prompt. This causes a silent failure in the advisor where the
method returns no advice rather than a grounded recommendation.

The existing aspects guard against this by converting fdars-returned values via `float(x)` or
`int(x)` before inserting them into the diagnostic dict. The `fpca.py` aspect documents the issue
explicitly ("json.dumps emits bare NaN (invalid JSON) into the LLM prompt" — line 137). New aspects
that bind new functions returning `np.float64` or `np.int64` values will reintroduce this bug.

**Why it happens:**
fdars-core returns numpy arrays via PyO3. When you do `result["eigenvalue"]` on a PyDict returned
from a `#[pyfunction]`, you get a Python float (not numpy). But when you do
`np.array(result["scores"])[0, 0]`, you get `np.float64`. New aspects that index into converted
numpy arrays rather than reading raw PyDict values will produce numpy scalars.

**How to avoid:**
In every new aspect's `build_diagnostics` implementation: wrap every scalar with `float(x)` or
`int(x)` before inserting into the output dict. Never insert a raw numpy scalar. Add a test that
calls `json.dumps(build_diagnostics(result, ...))` and asserts it succeeds without error — this is a
cheap check that catches the bug before the LLM path is ever invoked.

**Warning signs:**
- A new aspect's test calls `build_diagnostics` and checks the dict contents but never calls
  `json.dumps` on the result.
- The aspect code indexes a numpy array: `scores_array[0]` or `eigvals[i]`.
- `advise()` returns an empty or error response on the first call but works after restarting (because
  the error is in JSON serialization, not the LLM call itself).

**Phase to address:**
Advisor extension phase — every new aspect must include a `test_json_serializable` test case.
The phase plan must list "JSON-serializable diagnostics" as a task acceptance criterion.

---

### Pitfall 9: Method-Inaccurate Diagrams That Pass Automated Verification

**What goes wrong:**
A hand-authored SVG diagram for a new method looks plausible, passes SVGO idempotence, builds in the
site, and is not flagged by the automated verifier — but depicts the method INCORRECTLY in a way that
only becomes visible when a domain expert compares the diagram to the shipped binding's behavior. The
v6.0 precedent: an inverted hypograph/epigraph asymmetry in `functional-outliers.svg` was caught
ONLY during the blocking human diagram review (Phase 41). A top-of-bundle curve has HIGH
`hypograph_index` (many curves below it) and LOW `epigraph_index` — the diagram had these
relationships inverted. Both the executor and the verifier passed the phase before the human review.

For v11.0, the new capability families (10 minor releases of new methods) bring unfamiliar concepts
where diagram-method alignment cannot be assumed from the method name alone.

**Why it happens:**
Automated verifiers check SVG validity, SVGO idempotence, and that the file exists — not that the
geometry in the diagram faithfully depicts the algorithm. Method-accuracy requires reading the
diagram and cross-checking it against the shipped binding's actual behavior (e.g. calling the
function on known data and verifying that what the diagram shows matches the numerical output).

**How to avoid:**
Every new SVG must be reviewed against the shipped binding by running the actual function on a
small example and verifying the diagram's claims match the output. The blocking human diagram review
must happen BEFORE the docs phase closes — not as a post-hoc check. The reviewer must run the
relevant fdars function and confirm the diagram is consistent with its output, not just confirm the
diagram "looks reasonable."

The `rsvg-convert -w 1440 -h 600 <svg> -o out.png` + Read workflow (from the docs-diagram-verify
memory) enables fast visual checks without triggering a full site rebuild.

**Warning signs:**
- A diagram is reviewed only for style (STYLE_SPEC.md conformance) but not for method accuracy
  against the shipped binding.
- The diagram uses a convention (e.g. "high value at top") that the author assumed but did not verify
  against the function's return values.
- The phase VERIFICATION.md records "SVG reviewed" without specifying which function call was used
  to verify accuracy.

**Phase to address:**
Docs phase (final docs phase) — the blocking human diagram review is a hard gate before the phase
closes. The VERIFICATION.md must record the verification command used for each new diagram.

---

### Pitfall 10: Worked-Example Fences That Are Too Heavy for the Build Budget

**What goes wrong:**
A new worked-example fence runs real fdars compute on a dataset that is too large, causing the fence
to take >60 seconds for a single page. The full-site build accumulates these costs: at ~19–25 min
currently (772-test baseline), one heavy fence can push the build past the 2-minute tool-call timeout
and cause orphaned `mkdocs` processes. Multiple orphaned builds silently compete for CPU and slow
subsequent builds (v6.0 lesson: 4.5h of zombie builds observed after a stale session).

The second risk: a fence uses a dataset that is not in `docs/data/` and calls `fdars.datasets.load_*`
which fetches from the network — the docs build environment must be fully offline.

**How to avoid:**
Keep fence datasets small. For worked examples, subsample the existing `docs/data/` datasets to
≤50 observations and ≤100 grid points wherever the method allows it. Never introduce network fetches
in a fence. Run `DOCS_FAST=1 PYTHONPATH=scripts .venv/bin/mkdocs build` on the new page in
isolation (using the DOCS_FAST flag that fast-paths expensive per-page figures) before running the
full-site build. Reap orphaned `mkdocs` processes with `pkill -f mkdocs` before starting a new
build.

Always emit `FDARS_FENCE_OK` at the end of every `exec` fence so the verifier can confirm
execution completed rather than being truncated.

**Warning signs:**
- A fence runs on the full `canadian_weather` dataset (35 curves × 365 points) without subsampling.
- A fence calls a network function (`requests.get`, `fdars.datasets.load_` with a URL argument).
- The build time for a single page exceeds 30 seconds in isolation.
- `FDARS_FENCE_OK` is absent from the fence output.

**Phase to address:**
Docs phase — each new fence must be tested in isolation with DOCS_FAST before being included in
the full-site build. The phase PLAN.md must include "fence timing check" as a mandatory task.

---

### Pitfall 11: Docs Phases Run in Worktrees Instead of Sequentially on Main

**What goes wrong:**
A docs phase executor runs in a harness worktree (the GSD default when `shouldDegrade=false`). The
worktree's `.venv/bin/mkdocs` is the symlink in the main checkout, not the worktree. When the
executor runs `PYTHONPATH=scripts .venv/bin/mkdocs build` from the worktree directory, it builds
the WRONG tree (the main tree, not the worktree with the new docs). The build succeeds (because the
main tree has no broken references) but the new pages are never exercised. Verification passes on a
stale build.

This is the established hard constraint from v6.0 Phase 41: "Worktree isolation must be OFF for
docs phases." The operative reason is that `mkdocs` resolves relative paths from its CWD, and the
main-tree `.venv` is not mirrored in worktrees.

Note: This constraint does NOT apply to SVG-correction phases that do not run a doc build (as
demonstrated in v10.0 where three SVG-correction phases ran in parallel worktrees safely). The
constraint is specifically about phases that include fence execution or a `mkdocs build`.

**How to avoid:**
Set `workflow.use_worktrees=false` in `.claude/settings.json` (or confirm it is already set) before
dispatching any docs-build phase. Run docs phase executors sequentially on main. If the harness
tries to use a worktree for a docs phase, abort, recover via `git worktree remove --force` +
`git branch -D`, and re-dispatch sequentially.

**Warning signs:**
- The executor's working directory is not the main repo root during `mkdocs build`.
- The verifier confirms `--strict` green but the built site does not contain the new pages.
- `ls site/` from the main tree shows stale content timestamps matching before the docs phase started.

**Phase to address:**
Docs phase — the phase PLAN.md must include an explicit note: "Executors: sequential on main, no
worktrees (`workflow.use_worktrees=false`)." The phase kickoff checklist includes confirming the
setting before dispatching wave 1.

---

### Pitfall 12: Stale Cross-References to Sections Whose URLs Changed During the Upgrade

**What goes wrong:**
New pages added during v11.0 reference existing pages by relative path (e.g.
`[alignment](../align/shift-registration.md)`). If a prior milestone or the current one renamed a
section directory (unlikely but possible when a new submodule gets a dedicated nav section), existing
relative links on OTHER pages become broken. `mkdocs build --strict` catches these as warnings
promoted to errors. The issue is not introduced by the new pages themselves but by the restructuring
that created the new section.

The secondary risk: internal page anchors (`#some-header`) break silently if a header is renamed,
because MkDocs `--strict` does not validate anchor references.

**How to avoid:**
After adding new nav sections, run `grep -r "relative-path-fragment" docs/` to find all inbound
links to renamed paths and update them. For anchor references, run `mkdocs build --strict` and
check the browser console for 404s on anchor links during a manual review. Do not rely on
`--strict` alone to catch anchor rot.

**Warning signs:**
- `mkdocs build --strict` emits "page not found" or "link not found" errors after adding new nav
  entries.
- An existing page has a cross-reference using a directory name that matches a newly added submodule
  (e.g. `../pace_fpca/` was previously a section of `represent/` but now has its own top-level nav).
- A header that previously had a stable anchor is renamed during the docs cleanup work.

**Phase to address:**
Docs phase — run `mkdocs build --strict` as the final gate before closing the phase. Cross-reference
audit is part of the docs phase acceptance criteria.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Bumping the crate and adding new bindings in the same commit | Saves one phase | Numeric drift from the bump is confounded with new-binding correctness bugs; impossible to isolate the cause of a test failure | Never — bump is always its own isolated phase |
| Using a square test fixture (n_obs == n_points) for a new 2D binding | Simpler fixture | Transposition bugs are invisible; ship with a silent correctness defect | Never — always use n_obs != n_points |
| Adding a diagnostic dict field derived in Python (e.g. `len(list)`) | Convenient for the LLM | Violates the grounding invariant; the LLM cites a Python-computed value | Never — only fdars-computed scalars go into the diagnostic dict |
| Split commits for aspect + guard-sync | Easier to review | `_DIAGNOSTICS_METHODS` and aspect are briefly out of sync; CI may pass between the two commits with the guard broken | Never — aspect + guard-sync must be one atomic commit |
| Skipping the blocking human diagram review and relying on the automated verifier | Saves ~30 min of human time | Method-accuracy errors survive all automated checks; v6.0 caught an inverted asymmetry this way | Never — human review is the only method-accuracy gate |
| Running a fence on the full canonical dataset without subsampling | Realistic example output | Build time inflates; orphaned processes accumulate; CI build may time out | Only for offline examples scripts (`examples/`), never for fence-executed doc pages |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `maturin develop` vs `maturin develop --release` | Using debug build for timing benchmarks | Use `--release` for any build where performance matters; debug builds can be 10× slower for Rust FPCA |
| `fdars-core` features in `Cargo.toml` | Adding `linalg` feature alongside `parallel` | Do NOT enable `linalg` — it raises MSRV above 1.83 and has historically been excluded; keep `features = ["parallel"]` only |
| `json.dumps` of diagnostic dict | Passing the dict directly without type verification | Run `json.dumps(diag)` in a test before any LLM call; this catches numpy scalar contamination immediately |
| `_DIAGNOSTICS_METHODS` frozenset in `server.py` | Adding an aspect to the advisor but not the frozenset | The test `test_guard_sync_version_independent.py` catches this; run it explicitly after any advisor aspect addition |
| `mkdocs build --strict` with `markdown-exec` fences | Running with `DOCS_FAST=1` for the gate check | `DOCS_FAST=1` skips fence execution; the gate build must run WITHOUT `DOCS_FAST` to actually execute the fences |
| `maturin develop` in the wrong virtualenv | Running `maturin develop` in the `.venv-puncc` instead of `.venv` | The docs build uses `.venv/bin/mkdocs`; always rebuild into `.venv` |

---

## "Looks Done But Isn't" Checklist

- [ ] **Bump regression gate:** `pytest tests/ -x` (full ~772-test suite, no -k filter) is green after
  `maturin develop --release` on the bumped crate — not just `cargo test`.
- [ ] **Transposition guard:** every new 2D-input binding has a test where `n_obs != n_points` and
  the result's row dimension equals `n_obs`, verified by asserting `result.shape[0] == n_obs`.
- [ ] **argvals presence/absence:** every new binding's signature comment documents `# argvals: optional
  (default_grid) | mandatory | absent`. The test exercises the no-argvals path explicitly.
- [ ] **Wildcard arms raise:** every new `match` block on a string-dispatched enum has `_ => Err(PyValueError::new_err(...))`
  not `_ => Ok(None)`. A test passes an invalid variant string and asserts `pytest.raises(ValueError)`.
- [ ] **Grounding invariant:** every new diagnostic dict field has a comment tracing it to a specific
  fdars-core result field. `json.dumps(build_diagnostics(result, "new_aspect"))` runs without TypeError.
- [ ] **Guard-sync:** `_DIAGNOSTICS_METHODS` in `server.py` matches the set of all aspect strings in
  `advisor/aspects/`. `test_guard_sync_version_independent.py` passes.
- [ ] **Docs fence timing:** each new `exec` fence was tested in isolation with
  `PYTHONPATH=scripts .venv/bin/mkdocs build` on the single page and completes in < 45 seconds.
- [ ] **FDARS_FENCE_OK sentinel:** every new exec fence emits `FDARS_FENCE_OK` on the final output line.
- [ ] **Diagrams method-accurate:** each new SVG was cross-checked by running the relevant fdars
  function on a small example and comparing the output to the diagram's claims. The VERIFICATION.md
  records the function call used.
- [ ] **Sequential execution for docs phases:** `workflow.use_worktrees=false` is confirmed in
  `.claude/settings.json` before the docs phase executor is dispatched.
- [ ] **`mkdocs build --strict` gate:** the full-site build (WITHOUT `DOCS_FAST`) is green before
  the docs phase closes.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Numeric drift discovered post-binding | HIGH | Bisect which bump point introduced it; decide whether to tighten tolerance or revert; existing tests are the arbiter of what is correct |
| Transposition bug discovered in shipped binding | HIGH | Add non-square test; fix the converter call; bump package minor version; re-release |
| Grounding invariant violation discovered in production | MEDIUM | Identify the non-fdars-computed field; remove it or replace with a pure pass-through; re-release advisor |
| Guard out-of-sync discovered post-release | LOW | Update `_DIAGNOSTICS_METHODS` frozenset; re-release (no binding changes needed) |
| Method-inaccurate diagram discovered post-publish | MEDIUM | Correct the SVG; rebuild and deploy docs; no package version bump needed |
| Fence too slow discovered during full-site build | LOW | Subsample the dataset; rebuild |
| Docs phase ran in worktree, built wrong tree | MEDIUM | `git worktree remove --force` + `git branch -D`; cherry-pick additive files onto main; re-run sequentially |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1: Numeric drift across 10 minors | Phase 66 (bump gate) | Full `pytest tests/` green before any new binding committed |
| P2: Changed defaults / removed variants | Phase 66 (bump + changelog audit) | Grep all `match` arm strings against 0.33 API; confirm no `deprecated` attributes |
| P3: Transposition bug on non-square inputs | Each binding phase (67–69) | Every 2D-input binding has `n_obs != n_points` test asserting output row dim == n_obs |
| P4: argvals presence/absence | Each binding phase | Binding comment documents argvals status; no-argvals path tested explicitly |
| P5: Missing wildcard arms | Each binding phase | Grep new `*_mod.rs` for match blocks; invalid variant string test asserts ValueError |
| P6: Grounding invariant violation | Advisor phase (70) | All diagnostic fields traced to fdars result; `json.dumps(diag)` succeeds |
| P7: Guard out of sync | Advisor phase (70) | `test_guard_sync_version_independent.py` passes; atomic commit for aspect + guard-sync |
| P8: numpy scalar in JSON | Advisor phase (70) | `json.dumps(build_diagnostics(...))` test in each new aspect's test file |
| P9: Method-inaccurate diagram | Docs phase (71) | Blocking human diagram review with verification command recorded per diagram |
| P10: Fence too heavy | Docs phase (71) | Per-page isolation build < 45s; no network fetches; FDARS_FENCE_OK present |
| P11: Docs phase in worktree | Docs phase (71) | `workflow.use_worktrees=false` confirmed; executor CWD is main repo root |
| P12: Stale cross-references | Docs phase (71) | `mkdocs build --strict` green; manual anchor check on renamed headers |

---

## Sources

- PROJECT.md Key Decisions table — v4.0 Phase 25 (bump isolation precedent), v6.0 Phase 41
  (hypograph/epigraph human review catch, worktrees-off for docs phases)
- v6.0 autonomous run state memory — zombie mkdocs process lesson, worktrees operatively blocked
  by venv path hardcoding
- v4.0 Phase 28 / v5.0 Phase 34 / v6.0 Phase 40 retrospectives — guard-sync atomic commit
  discipline
- advisor-grounding-guard-false-positives memory — `_check_grounding` design, digits-in-identifier
  FP root cause, `_NUMBER_RE` lookbehind fix
- docs-diagram-verify-workflow memory — rsvg-convert UAT technique, DOCS_FAST semantics, orphaned
  process discipline
- `src/convert.rs` — numpy2d_to_fdmatrix column-major conversion pattern
- `src/inference_mod.rs`, `src/regression_mod.rs`, `src/depth_mod.rs`, `src/outliers_mod.rs` —
  `#[non_exhaustive]` wildcard arm pattern (inspected directly)
- `python/fdars/mcp/server.py` — `_DIAGNOSTICS_METHODS` / `_RUNNABLE_METHODS` frozenset structure
  and T-12-02 mirror constraint
- `python/fdars/advisor/aspects/fpca.py` — numpy NaN / json.dumps warning (line 137)
- `tests/test_pace_fpca.py`, `tests/test_regression.py`, `tests/test_classification.py`,
  `tests/test_depth.py` — established transposition guard test patterns

---
*Pitfalls research for: pyfda v11.0 fdars-core 0.23 → 0.33 upgrade (bump + bindings + advisor + docs)*
*Researched: 2026-09-02*
