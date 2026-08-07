# Pitfalls Research

**Domain:** Documentation overhaul — hand-authored SVG concept diagrams + reproducible code examples for a scientific FDA library (pyfda / fdars)
**Researched:** 2026-08-07
**Confidence:** HIGH (primary-source: direct inspection of ~45 SVG files, 17 example pages, CI workflow, build scripts, `docs_fig.py`, `docs_data.py`)

---

## Critical Pitfalls

### Pitfall 1: Diagram Depicts Wrong Method Semantics

**What goes wrong:**
A diagram illustrates a valid-looking conceptual shape but misrepresents what the underlying algorithm actually computes. For example: the `smoothing.svg` "smooth curve" panel re-uses the same jagged path from the noisy-input panel (Panel 3's path is identical to Panel 1's path with a different stroke color and an overlaid smooth curve layered on top), implying the smoother merely traces over the original data rather than extracting the signal. A reader who studies the SVG closely will see the noisy path still present behind the smooth one — the diagram shows overlay rather than replacement.

More dangerous variants: an FPCA modes-of-variation diagram showing mean ± mode curves where the ± perturbation is symmetric but the drawn curves are not actually ± 2√λₖ · φₖ (just decorative wiggles); a warping function panel where the warp curve shown does not start and end at the identity diagonal endpoints (violating γ(0)=0, γ(T)=T); a conformal-prediction interval drawn as a symmetric band around a point rather than an asymmetric residual quantile region.

**Why it happens:**
Hand-authored SVGs are drawn by eye to look plausible, not derived from actual computed values. An author who understands the method knows what "roughly" looks right. The error is invisible to visual inspection by someone unfamiliar with the mathematical constraint; it only surfaces during expert peer review. The pressure to ship a complete, polished set of diagrams discourages iteration time.

**How to avoid:**
For each diagram class, write a one-sentence "mathematical invariant" the SVG paths must satisfy: warp functions must be monotone-increasing, start at (0,0), end at (T,T); FPCA panels must label axes with the formula μ̂ ± c·φₖ and the drawn curve must match the described perturbation direction; a smoother output must not share path geometry with the input. Review each diagram against its invariant checklist, not just visual impression.

**Warning signs:**
- "Looks good to me" sign-off without reading the SVG source to verify path coordinates
- Reviewer who created the diagram is also the sole reviewer
- Diagrams showing SRSF/elastic methods without an explicit identity-diagonal reference line in the warping panel
- Any panel where the input and output `<path d="...">` share identical coordinate sequences

**Phase to address:**
Style spec phase (before rollout). Invariant checklist should be codified in the shared style spec so each diagram draft is checked against it. Expert review gate (built-site review) is the verification step.

---

### Pitfall 2: Stale R-Centric Content in Diagrams

**What goes wrong:**
Two SVG files (`spm.svg` and `basis-representation.svg`) contain R-specific content — "powered by Rust / R" branding, `extendr` references, R function signatures — that belongs to the R package (`fdars`), not the Python package (`fdars` / pyfda). These were ported from the R documentation without updating the language layer. A user reading the Python docs encounters "Rust Backend (extendr)" (extendr is the R↔Rust bridge) and R function calls like `autoplot()`. This actively misleads Python users about what they are using.

**Why it happens:**
The project started as an R package; pyfda is the newer Python binding. SVGs were created once and reused across documentation layers. The error is textual, not visual, so it survives visual-only review.

**How to avoid:**
During the nav + reference-API audit phase, explicitly grep SVG source for R-specific identifiers: `extendr`, `autoplot`, `R ↔ Rust`, `fclassif` (R name), and any reference to CRAN. Flag every hit for replacement. The style spec should require that all function-name labels in diagrams are verified against the current Python API surface.

**Warning signs:**
- Any SVG showing `extendr` in the text content
- Function labels using R-style names (e.g., `autoplot()`, `fclassif()`) rather than Python API names
- The hero/introduction diagram listing R-only methods not exposed in `fdars` Python
- `viewBox="0 0 720 480"` combined with `font-family="'Segoe UI', system-ui, sans-serif"` (the legacy pre-spec style applied to overview diagrams not yet updated)

**Phase to address:**
Nav + reference-API audit (first phase). Flag all such files before diagram revision begins. Fixing them during style-spec rollout is correct; discovering them during the final review gate is too late.

---

### Pitfall 3: Visual Consistency Drift Across the 45-SVG Set

**What goes wrong:**
With ~45 hand-authored SVGs, authoring drift accumulates across the rollout: different stroke widths for the same semantic (e.g., `stroke-width="1.3"` vs `1.6` vs `2.4` for "secondary curve"), different font sizes for labels, slightly different `rx` values for panel corners, inconsistent color usage (the orange `#fd7e14` in some diagrams, `#e8710a` in the palette spec, `#E6A020` in the legacy overview diagram), and caption y-positions that vary per diagram.

The existing diagram set already shows this: `smoothing.svg` uses `stroke-width="1.3"` for the noisy path, while `elastic-alignment.svg` uses `stroke-width="1.8"` for comparable secondary curves. The legacy `spm.svg` / `basis-representation.svg` files use `font-family="'Segoe UI', system-ui, sans-serif"` with `font-size="12"` attributes directly on `<text>` elements, while the modern spec uses a `<style>` block with named classes (`.ttl`, `.sub`, `.lab`, `.sm`, `.mono`). Both conventions will coexist across the set until explicitly harmonised.

**Why it happens:**
Authors working section-by-section copy an existing "similar" diagram as a starting template. The template they copy is whichever one they opened, not necessarily the canonical one. Without a machine-checkable linter, no one notices that `rx="8"` became `rx="12"` in the next batch.

**How to avoid:**
The shared style spec must be a normative, machine-verifiable reference: one authoritative palette constant per color role, one `stroke-width` value per semantic role ("primary curve", "secondary curve", "axis line", "dashed reference"), one `rx` for panels, one viewBox aspect ratio per diagram layout type. Write a Python or shell linter (e.g., an xmllint + grep script) that checks each SVG in `docs/assets/diagrams/` against the spec. Run it in CI on every PR. Do not rely on human visual comparison across 45 files.

**Warning signs:**
- Reviewer notes "this looks slightly different from the others" more than twice per section
- Any new SVG drafted from a `docs/assets/cards/` or `docs/assets/thumb/` file (those are separate conventions)
- Hex colors in SVG source that are not in the approved palette (`#3f51b5`, `#e8710a`, `#198754`, `#dc3545`, `#6f42c1`, `#0dcaf0`, `#6c757d`, `#1a1a2e`, `#f8f9fa`, `#ced4da`, `#adb5bd`, `#495057`)
- Diagrams where the font size on `.sm` label elements differs from 11px

**Phase to address:**
Style spec phase. The linter should be built and green before any diagram is revised. Running it retroactively after 20 diagrams have been revised is the wrong order.

---

### Pitfall 4: Example Rot — Silent API Drift

**What goes wrong:**
A `markdown-exec` code block calls a function with parameters that silently changed. The existing `check_docs_figures.py` script catches `ModuleNotFoundError` and `.exec-error` tracebacks, but it does NOT catch: (a) API changes that produce the wrong output without raising, (b) changed return-dict keys (e.g., if `karcher_mean()` stops returning `"aligned_data"` and returns `"registered_data"` instead, `np.asarray(km["aligned_data"])` raises a `KeyError`, which IS caught — but if the key name changes to return an extra field and the old key is kept for backward compat, the example may produce silently wrong figures), (c) numeric changes in output values (e.g., default `lambda_` fix in issue #37 changed outputs without a visible error).

The deeper risk is the `load_penicillin` function in `docs_data.py`: it is seeded-synthetic data using `np.random.default_rng(20260805)` — but if the NumPy random generator semantics change between minor versions (as they have in past NumPy releases for some distributions), the generated curves shift shape, and the monitoring example shows different figures than were reviewed.

**Why it happens:**
`markdown-exec` builds execute the code but do not assert on output values — they only detect hard exceptions. The `check_docs_figures.py` script is exception-only. There is no golden-output comparison. API changes in `fdars` that affect defaults (like the `lambda_=1.0 → 0.0` fix in issue #37) propagate silently into all figure outputs.

**How to avoid:**
(1) For deterministic outputs (scalar metrics printed alongside figures), add an assertion or print the value and document the expected range in a `!!! note` admonition — a reviewer can catch drift during section review. (2) For seeded-synthetic data, pin the NumPy version in `docs/requirements.txt` with a minimum version and document the seed contract in `docs_data.py`. (3) After any `fdars` API change, explicitly rebuild the docs and diff figure outputs before marking a section done. (4) For functions whose return keys may change (like `karcher_mean`, `fpca`, `equivalence_test`), add an explicit dict-key assertion at the top of each exec block: `assert "aligned_data" in km, f"unexpected keys: {list(km.keys())}"` — this converts silent drift to a caught error.

**Warning signs:**
- `fdars` version in `pyproject.toml` or `Cargo.toml` is bumped without rebuilding docs
- A function-result dict accessed by string key without assertion
- `np.random.default_rng` with a date-based seed (e.g., `20260805`) — signals the seed was chosen arbitrarily and may not be stable across NumPy minor versions
- No pinned minimum NumPy version in `docs/requirements.txt`
- Example output prose ("about 8 cm/yr", "R² of 0.94–0.98") that was manually transcribed from a past build and not rechecked

**Phase to address:**
Examples phase. The dict-key assertions and output-range notes should be added during example authoring, not retroactively. The NumPy pin should be addressed in the foundation/audit phase.

---

### Pitfall 5: Non-Deterministic Figures from Random Splits

**What goes wrong:**
Several examples use `np.random.default_rng(42)` for train/test splits (e.g., `tecator-regression.md` uses `rng.permutation(X.shape[0])`). These are correctly seeded. However, two specific risks exist: (1) `equivalence_test(..., nb=500, seed=42)` in `growth-alignment.md` — if the fdars binding does not thread the seed through to Rust's RNG correctly, the bootstrap will produce different p-values across builds. (2) The `scatter` jitter in the same example (`np.random.default_rng(0).uniform(-.08, .08, ...)`) is correctly seeded, but the RNG is created inline — if the call is executed multiple times (e.g., during local `mkdocs serve` with hot-reload), the second RNG state will differ if there are upstream side effects. Neither will fail CI but both will produce visually different figures across builds.

**Why it happens:**
Seeds in Python code are per-object, not global. The Rust side of `equivalence_test` may use its own RNG state unless the `seed` parameter is explicitly passed. Markdown-exec re-executes all blocks in a fresh process for each build, so top-level state is reset — but any mutable global state (matplotlib rcParams modified by a prior block) persists within a single page build.

**How to avoid:**
(1) Verify that every `nb=` bootstrap call also passes `seed=` explicitly. (2) Each exec block that produces a plot should start with an explicit `rng = np.random.default_rng(<fixed_int>)` and use it for all random operations. (3) For blocks that call `np.random.default_rng(0)` inline, move the RNG construction to the top of the block. (4) Do not rely on matplotlib global state from a prior block — each block should call `plt.rcParams.update(...)` if it needs non-default settings, or use `docs_fig.fig()` exclusively.

**Warning signs:**
- `nb=` argument to bootstrap functions without an accompanying `seed=`
- `np.random.default_rng()` called without arguments (non-deterministic)
- A figure that looks different on two consecutive local builds
- Any use of `random.seed()` (stdlib random) instead of `np.random.default_rng`

**Phase to address:**
Examples phase. Each example page review should include a "two consecutive builds produce identical SVG output" check as a UAT criterion.

---

### Pitfall 6: Hidden State Between Exec Blocks on the Same Page

**What goes wrong:**
`markdown-exec` runs all exec blocks on a page in the same Python process (within a single page build). This means variables defined in Block 1 are visible in Block 2. The existing examples intentionally exploit this (e.g., `growth-alignment.md` reloads `age, X, meta` in every block for independence) — but a reviewer editing Block 4 to use a variable from Block 3 creates a fragile ordering dependency. If the block order in the markdown file is later rearranged, Block 4 breaks silently (produces a NameError, which `check_docs_figures.py` would catch) or — worse — uses a stale value from a prior block with the same variable name.

The specific risk here: `karcher_mean()` is called three times in `growth-alignment.md` with `max_iter=25`. If an editor consolidates those calls by caching `km` at the top of the page, subsequent blocks may silently pick up the cached `km` even after the code in those blocks appears to recompute it, because the `km = karcher_mean(...)` line is now in a prior block.

**Why it happens:**
`markdown-exec` shares the Python interpreter namespace across blocks on one page to allow progressive example building. This is a deliberate feature, but it makes each block's preconditions implicit. Authors who copy a block from one page to another may not copy the necessary setup blocks.

**How to avoid:**
Each exec block that produces a self-contained output must either (a) re-import and recompute all inputs from scratch (current pattern in `growth-alignment.md` — good), or (b) be documented in a comment at the top: `# requires: km defined in block above`. Add a convention to the style spec: "standalone figure blocks always reload from `docs_data`; dependent blocks label their dependency explicitly." The per-section review should open the page in a fresh build and verify that removing Block N-1 from the markdown causes Block N to fail (proving it does not silently depend on prior state).

**Warning signs:**
- A block that does not call a `load_*` function but uses data-shaped variables (`X`, `V`, `age`, etc.)
- Any block where the only `import` statements are for matplotlib/numpy but not fdars or docs_data
- Variable names repeated across blocks on the same page without re-assignment

**Phase to address:**
Examples phase. Convention should be established in the audit phase; enforced in examples authoring; verified in per-section review.

---

### Pitfall 7: Build-Time Figure Errors That Slip Past `check_docs_figures.py`

**What goes wrong:**
`check_docs_figures.py` scans the built HTML for three string markers: `Traceback (most recent call last)`, `ModuleNotFoundError`, and `class="exec-error"`. It misses: (a) warnings printed to stderr (not embedded in HTML), (b) figures that rendered but produced an empty SVG (`<svg></svg>` or a figure with no data lines), (c) `UserWarning` from matplotlib about missing data, (d) a `KeyError` that markdown-exec catches and renders as plain text (not a traceback div), and (e) `DeprecationWarning` from fdars that signals an API change but does not raise.

Concretely: if `fpca()` returns a dict where `"singular_values"` is renamed, `np.asarray(pc["singular_values"])` raises `KeyError` — but `KeyError` is a Python exception with a traceback, so it IS caught. However, if `fpca()` returns an empty list for a singular_values key, `np.asarray([])` silently produces a zero-length array, `s / s.sum()` raises `ZeroDivisionError`... which IS caught. The gap is specifically silent wrong-but-not-erroring cases.

**Why it happens:**
The check script was designed to catch the most common failure mode (import errors, hard exceptions). Soft failures (wrong shape, empty output, matplotlib warning) are harder to detect without output assertions.

**How to avoid:**
(1) Add shape assertions after each key API call: `assert scores.shape == (n, n_comp), scores.shape`. (2) Add a figure content check: each `render(f)` call can be preceded by `assert any(len(ax.get_lines()) > 0 or len(ax.collections) > 0 for ax in f.axes), "empty figure"`. (3) Extend `check_docs_figures.py` to also scan for empty `<svg>` tags with no child elements. These checks should be added to `docs_fig.py`'s `render()` function as a debug-mode assertion.

**Warning signs:**
- A figure block that calls `print(render(f))` without any preceding data-shape check
- A figure shown in the docs that has axes but no visible data series
- A build that passes CI but a reviewer notices a blank or axis-only figure

**Phase to address:**
Foundation/audit phase. The `render()` function and `check_docs_figures.py` improvements should be done before example authoring begins.

---

### Pitfall 8: SVG Accessibility Gaps — Missing or Wrong `aria-label`, No Font Fallback

**What goes wrong:**
The modern diagram convention correctly uses `role="img"` and `aria-label` on the root `<svg>`. However: (1) two legacy diagrams (`spm.svg`, `basis-representation.svg`) have neither `role="img"` nor `aria-label` — they will be announced as "unlabelled image" by screen readers. (2) Several diagrams render text using `system-ui,-apple-system,sans-serif` — this renders differently on Linux (Noto Sans), macOS (San Francisco), and Windows (Segoe UI), causing different character widths that can cause text overflow or clipping inside fixed-width `<rect>` containers. The CI build runs on Ubuntu; the deployed site is served to all OS users. (3) No SVG diagram uses `<title>` or `<desc>` elements (only the root `aria-label`), so embedded inline SVG in HTML lacks a DOM-accessible text alternative for assistive tech that reads inline SVG differently from `<img>`.

**Why it happens:**
Accessibility is typically treated as a post-hoc concern. The root `aria-label` was added to the modern convention but not backported to the two oldest overview diagrams. Font rendering differences across OS are invisible in the CI environment.

**How to avoid:**
(1) The style spec linter should assert `role="img"` and `aria-label` are present on the root `<svg>` element of every diagram. (2) Review each diagram at 80% zoom on a narrow viewport (600px width) to catch text overflow before it ships. (3) For the two legacy overview diagrams, add `role="img"` and `aria-label` during the style-spec harmonisation phase. (4) If a diagram's text content is critical for comprehension, add a `<title>` child element (immediately inside `<svg>`) with the same text as `aria-label` — this improves inline SVG accessibility in browsers that do not surface `aria-label` on inline SVGs.

**Warning signs:**
- Any SVG file that does not contain `role="img"` in its root element
- Text elements positioned within 8px of a `<rect>` boundary (clipping risk)
- A diagram reviewed only on macOS by an author who will deploy to users on all platforms

**Phase to address:**
Style spec phase (linter catches missing role/aria-label). Per-section review should include a cross-platform spot-check on at least one diagram per section.

---

### Pitfall 9: Slow Builds Blocking Local Iteration

**What goes wrong:**
Each `markdown-exec` exec block runs live Python code at build time. The full docs build with `mkdocs build --strict` runs all blocks in all 17 example pages plus concept pages. Slow operations — `karcher_mean(..., max_iter=25)` on 93 growth curves, `equivalence_test(..., nb=500)` — execute on every full build. This can push `mkdocs build` to 3–10 minutes locally, making the per-section review loop painfully slow. Authors start skipping local builds and doing visual review only after pushing to CI, which delays error discovery.

In `growth-alignment.md`, `karcher_mean(Vp, ap, max_iter=25)` is called four times across four separate exec blocks on the same page, each time reloading and recomputing from scratch. Each call is O(n · max_iter) elastic alignment.

**Why it happens:**
`markdown-exec` re-executes all blocks on every build. The "each block is self-contained" convention (correct for correctness) conflicts with performance because it prevents caching.

**How to avoid:**
(1) Add a `DOCS_FAST=1` environment variable check in expensive blocks to skip computation and render a placeholder: `if os.environ.get("DOCS_FAST"): print("<p>Figure skipped in fast mode</p>"); sys.exit(0)`. (2) For multi-call heavy pages, document in a comment that the block is slow and give a `--no-exec` workaround for section review. (3) Consider adding a Makefile target `docs-fast` that sets `DOCS_FAST=1` for local review. (4) The four separate `karcher_mean` calls in `growth-alignment.md` should be consolidated to one block that stores the result, with subsequent blocks referencing the cached variable — this requires accepting the cross-block dependency (acceptable on a single page if explicitly documented).

**Warning signs:**
- A single page with more than two calls to alignment, bootstrap, or FPCA functions
- Build time exceeding 2 minutes locally on the author's machine
- Authors reporting they "just push to CI to check" rather than building locally

**Phase to address:**
Foundation/audit phase. The `DOCS_FAST` mechanism should be in place before example authoring begins. Heavy call consolidation is a per-example decision made during examples phase.

---

### Pitfall 10: Section-by-Section Rollout Letting Inconsistencies Accumulate

**What goes wrong:**
The defined rollout order is `learn/ → align/ → analyze/ → regression/ → monitoring/ → represent/ → examples/`. If the style spec is not fully finalised before `learn/` begins, then every subsequent section inherits the spec-as-it-was, and any spec refinements made after reviewing `align/` must be backported to `learn/`. This has happened in previous doc overhauls: the "last section" always looks more polished than the first, creating a visible quality gradient.

Specific risk for this project: the conformal prediction interval visual in `conformal-prediction.svg` shows a scalar prediction interval (a symmetric band around a point ŷ) rather than a functional prediction band (a time-varying region around a curve). For conformal functional regression this is methodologically wrong. If the conformal diagram is revised in the `regression/` section after `analyze/` has already been reviewed, the reviewer for `analyze/` may not re-review the updated methodology when it lands.

**Why it happens:**
Review gates are per-section. A correction to a concept that spans sections (e.g., "conformal" appears in both `analyze/tolerance-bands.md` and `regression/`) may be reviewed and approved in one section without the cross-section correctness check.

**How to avoid:**
(1) Before the rollout begins, hold a single "cross-section diagram map" review: for every method that appears in multiple sections, verify that the diagrams in all sections use a consistent representation. (2) The style spec must be frozen before the first section begins, not "largely finalised." Any spec change after rollout start requires a re-sweep of all previously reviewed sections. (3) For the specific conformal pitfall: the `conformal-prediction.svg` and `conformal-classification.svg` diagrams should depict functional bands (y-axis = function value at each time t, shaded region = interval around ŷ(t)), not scalar point intervals. This must be corrected before the regression/analyze sections are reviewed.

**Warning signs:**
- A method name (e.g., "conformal", "FPCA", "basis") appearing in diagrams in more than two section directories
- Style spec document with "TBD" or "to be decided" items at the start of any section
- A reviewer signing off on a section without checking whether any diagram in that section also appears (or is closely related to a diagram) in a not-yet-reviewed section

**Phase to address:**
Foundation/audit phase (cross-section map). Style spec phase (freeze before rollout). Per-section reviews should reference the cross-section map.

---

### Pitfall 11: Conformal and Tolerance Band Diagrams Conflating Interval Types

**What goes wrong:**
`conformal-prediction.svg` currently shows a scalar prediction interval — a horizontal shaded rectangle around a single point ŷ, with horizontal boundary lines at `ŷ ± interval`. This correctly depicts scalar conformal prediction (one number in, one number out). However, `fdars`'s `conformal_fregre_lm()` produces a **functional** prediction band — a time-varying region around a predicted curve ŷ(t). The current diagram is correct only for the scalar-response conformal use case, not the functional one.

Similarly, `tolerance-bands.svg` shows a static shaded region around a mean curve, which correctly represents a tolerance band. But the method box says "Conformal · elastic" — mixing two distinct ideas (distribution-free conformal regions vs. elastic-amplitude tolerance regions) without distinguishing them. A reader will not understand when to use `fpca_tolerance_band()` vs. `conformal_fregre_lm()`.

**Why it happens:**
Scalar examples are easier to draw and generalise visually. The distinction between "interval for one scalar prediction" and "band for one functional prediction" requires depicting a 2D functional output, which is harder to sketch in the 720×300 three-panel layout.

**How to avoid:**
The conformal prediction diagram must be split into two versions or redesigned to depict the functional output: the Panel 3 "Prediction Interval" should show a time axis with a shaded region ŷ(t) ± q, not a point ŷ ± interval. The tolerance band diagram should separate its method box into two sub-rows: one for FPCA-based tolerance (with a note "population coverage") and one for conformal (with a note "marginal coverage guarantee"). The method distinction caption should be added to the `aria-label`.

**Warning signs:**
- Any diagram Panel 3 showing a scalar value when the API returns an array or curve
- Method box listing two unrelated methods (e.g., "Conformal · elastic") without distinguishing when each applies
- `aria-label` text that describes the output as a "point" when the function returns a band

**Phase to address:**
Analyze/regression section review. The cross-section diagram map (from the audit phase) should flag this pair for joint review before either section is approved.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Copy an existing SVG as template for a new diagram | Fast start, already-consistent structure | Inherits any errors in the template; palette constants duplicated rather than referenced | Never: always start from the frozen style spec template, not an arbitrary existing file |
| Reuse R-era diagram with just text label changes | No redraw needed | R API names and `extendr` branding mislead Python users | Never for the Python docs |
| Skip `aria-label` update when diagram content changes | Saves one edit | Screen-reader users get stale description; fails accessibility linter | Never |
| Set `max_iter` high for "better" results in examples | More accurate output | Build time 3–10x longer; blocks local iteration loop | Only in the final published version, not during authoring |
| Write example output values as prose ("about 8 cm/yr") without an assertion | Easier to write | Silently wrong when API defaults change (e.g., lambda_ fix) | Acceptable if the page has a version-pinned rebuild guarantee; otherwise, always add the assertion |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `markdown-exec` + `docs_fig.py` | Calling `plt.show()` inside an exec block — it blocks the build process or produces no output | Always use `print(render(f))` and never call `plt.show()` |
| `markdown-exec` + `docs_fig.py` | Forgetting `plt.close(figure)` — `render()` does close it, but any figure created with `plt.figure()` directly rather than `fig()` may leak state | Always use `docs_fig.fig()` wrapper or explicitly call `plt.close()` |
| `markdown-exec` + `PYTHONPATH` | Running `mkdocs serve` locally without `PYTHONPATH=scripts` — `docs_fig` import fails silently via `hooks.py` fallback if `sys.path` was already populated | Always use `PYTHONPATH=scripts mkdocs serve` or the Makefile target |
| `fdars` API + exec blocks | Using `np.asarray(result["key"])` without checking that `result` is not `None` or that "key" exists | Add `assert "key" in result` before array conversion |
| inline SVG in MkDocs Material | SVGs with `<defs><marker id="...">` — if the same marker id appears in two SVGs on the same page, the second definition silently shadows the first | Use diagram-name-prefixed marker IDs (e.g., `id="arr-smoothing"` not `id="arr"`) |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Multiple `karcher_mean()` calls on the same page | Full `mkdocs build` takes 5+ minutes; CI timeout | Consolidate to one call per page; use cross-block variable | Any page with 3+ alignment calls |
| `equivalence_test(nb=500)` per build | Each bootstrap adds ~2–5s to build | Use `nb=200` for doc builds; note "nb=500 for publication" | Not a threshold issue — cumulative across many pages |
| `fpca()` called once per comparison method per example | Fine for 2–3 methods; slow at 6+ | Pre-compute FPCA once, pass scores to all methods | 4+ fpca calls on one page |
| `mkdocs build --strict` runs all blocks unconditionally | No skip mechanism | Add `DOCS_FAST` env var gate in heavy blocks | Always a risk on developer machines |

---

## "Looks Done But Isn't" Checklist

- [ ] **Diagram updated for style spec:** Verify the SVG source uses the `<style>` block with `.ttl/.sub/.lab/.sm/.mono` classes — not inline `font-size` attributes
- [ ] **Diagram uses correct viewBox:** Standard concept diagrams must have `viewBox="0 0 720 300"` — any other height requires explicit justification in the spec
- [ ] **Diagram has `role="img"` and `aria-label`:** Check the root `<svg>` tag, not just visual output
- [ ] **Method box shows Python API names:** Verify against `fdars` Python API reference, not R docs
- [ ] **Example seeds all RNG uses:** Every `np.random.default_rng()` call has an explicit integer seed
- [ ] **Example re-loads data in each block:** No block uses a variable defined only in a prior block without a comment saying so
- [ ] **Conformal diagrams show functional output:** Panel 3 depicts a time-varying band, not a scalar interval
- [ ] **Warp function diagrams show identity diagonal:** The reference line (γ(t) = t) must be present and labeled
- [ ] **FPCA modes diagram labels the formula:** The ± perturbation is labeled `μ̂ ± c·φₖ` with the scaling factor explicit
- [ ] **CI passes `check_docs_figures.py`:** Not just `mkdocs build --strict` — the figure-error scan must also pass

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Diagram misrepresents method semantics | MEDIUM | Reopen SVG, correct path coordinates against mathematical invariant, re-review; 1–4 hours per diagram |
| Stale R branding in SVG | LOW | Text replacement in SVG source; 15 min per file; verify against Python API reference |
| Visual consistency drift across 20+ diagrams | HIGH | Requires a pass over all already-delivered diagrams; 1–2 days; justifies the linter investment in advance |
| Example rot (silent API drift) | LOW-MEDIUM | Rebuild docs after each `fdars` version bump; add dict-key assertions; update prose values |
| Non-deterministic figures | LOW | Add explicit seeds to every RNG call; two-consecutive-build check |
| Slow build blocking review | LOW | Add `DOCS_FAST` gate; rebuild without heavy blocks for section review |
| Section-by-section quality gradient | MEDIUM | Backport style spec changes to reviewed sections; requires second pass |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Diagram method semantics wrong | Style spec + invariant checklist (before rollout) | Expert peer review of each diagram against its mathematical invariant |
| Stale R content in SVGs | Nav + reference-API audit (first phase) | Grep SVG sources for R-specific identifiers; zero hits required |
| Visual consistency drift | Style spec (linter, before rollout) | CI linter passes on all SVGs before any section is approved |
| Example API rot | Examples phase + foundation (dict-key assertions) | Rebuild docs after each `fdars` bump; `check_docs_figures.py` passes |
| Non-deterministic figures | Examples phase | Two consecutive local builds produce bit-identical SVG output |
| Hidden cross-block state | Examples authoring convention + per-section review | Block-isolation check: removing Block N-1 causes Block N to fail or reload correctly |
| Build-time figure check gaps | Foundation/audit phase | `check_docs_figures.py` extended; shape assertions added to `render()` |
| SVG accessibility gaps | Style spec (linter) | `role="img"` and `aria-label` present on all SVG root elements |
| Slow build blocking iteration | Foundation/audit phase | `DOCS_FAST=1` build completes in under 30s |
| Cross-section quality gradient | Foundation/audit (cross-section diagram map) | Frozen style spec before first section; spec changes trigger re-sweep |
| Conformal/tolerance band conflation | Analyze + regression section review | Functional-output requirement verified: Panel 3 shows time-varying band |

---

## Sources

- Direct inspection of `docs/assets/diagrams/*.svg` (all 45 files including `smoothing.svg`, `fpca.svg`, `elastic-alignment.svg`, `conformal-prediction.svg`, `tolerance-bands.svg`, `spm.svg`, `elastic-fpca.svg`, `landmark-registration.svg`, `basis-representation.svg`) — HIGH confidence (first-party source code)
- Direct inspection of `docs/examples/growth-alignment.md`, `docs/examples/tecator-regression.md` — HIGH confidence
- Direct inspection of `scripts/docs_fig.py`, `scripts/docs_data.py`, `scripts/check_docs_figures.py`, `docs/hooks.py` — HIGH confidence
- Direct inspection of `.github/workflows/docs.yml`, `mkdocs.yml`, `docs/requirements.txt` — HIGH confidence
- Direct inspection of `.planning/codebase/CONCERNS.md` (known API instability patterns, fdars-core version pinning, result wrapper fragility) — HIGH confidence

---

*Pitfalls research for: pyfda documentation overhaul (SVG diagrams + reproducible examples)*
*Researched: 2026-08-07*
