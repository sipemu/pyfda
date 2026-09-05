---
phase: quick-260905-htx
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - python/fdars/fdata_class.py
  - docs/represent/interpolation.md
  - tests/test_represent.py
autonomous: true
requirements: [QUICK-RESAMPLE]
estimate:
  tokens: 45000
  raw_tokens: 30000
  tasks: 3
  confidence: med
must_haves:
  truths:
    - "fd.upsample(2) returns an Fdata with more evaluation points than the source"
    - "fd.downsample(2) returns an Fdata with fewer evaluation points than the source (>= 2)"
    - "fd.resample(n_points=N) returns an Fdata whose grid has exactly N uniform points spanning the original rangeval"
    - "resample raises ValueError when both/neither of n_points/factor given, or target n_points < 2"
    - "the interpolation.md docs page documents resample/upsample/downsample with a runnable markdown-exec example"
  artifacts:
    - python/fdars/fdata_class.py
    - docs/represent/interpolation.md
    - tests/test_represent.py
  key_links:
    - "resample/upsample/downsample delegate to the existing self.interpolate() method (no new Rust)"
    - "target grid built with np.linspace over self.rangeval spanning target n_points"
---

<objective>
Add three pure-Python convenience methods — `resample`, `upsample`, `downsample` — to the `Fdata` class that build a uniform target evaluation grid and delegate to the existing `interpolate()` method, then document and test them.

Purpose: Give users a one-call resampling API on `Fdata` instead of hand-building a linspace grid and calling `interpolate()`. Mirrors the existing convenience-method pattern (`deriv`, `center`, `interpolate`, `impute`).
Output: Three new methods with NumPy-style docstrings, an extended `docs/represent/interpolation.md` page, and pytest coverage in `tests/test_represent.py`.
</objective>

<execution_context>
@~/.claude/gsd-core/workflows/execute-plan.md
@~/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.claude/CLAUDE.md

# The Fdata class — study existing interpolate() (line 630) and the n_points / rangeval properties (lines 261, and rangeval stored on the instance)
@python/fdars/fdata_class.py

# Existing interpolation docs page to extend, and its markdown-exec worked-example pattern
@docs/represent/interpolation.md

# Existing represent tests — append to TestFdataInterpolateMethods conventions (fixtures at line 313+)
@tests/test_represent.py
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: Add resample() + upsample()/downsample() delegating to interpolate()</name>
  <files>python/fdars/fdata_class.py, tests/test_represent.py</files>
  <behavior>
    - resample(n_points=5) on an 11-point curve -> new Fdata, n_points == 5, argvals == np.linspace(rangeval[0], rangeval[1], 5)
    - resample(factor=2) on an 11-point curve -> new Fdata, n_points == 22 (round of 11*2)
    - upsample(2) on an 11-point curve -> n_points == 22 (ceil of 11*2), strictly greater than source
    - downsample(2) on a 10-point curve -> n_points == 5, strictly fewer than source
    - resample() with neither n_points nor factor -> ValueError
    - resample(n_points=5, factor=2) (both) -> ValueError
    - resample(n_points=1) -> ValueError (target < 2)
    - upsample(1.0) and upsample(0.5) -> ValueError (factor must be > 1)
    - downsample(1.0) -> ValueError (factor must be > 1)
    - returned Fdata preserves n_obs and is a distinct object
  </behavior>
  <action>Add three methods to the `Fdata` class in `python/fdars/fdata_class.py`, placed immediately after the existing `interpolate()` method (ends ~line 682) in the "represent convenience" section, following the exact style of `interpolate()` (NumPy docstring with Parameters/Returns/Raises/Examples, delegates, returns a new Fdata).

`resample(self, n_points=None, factor=None, policy="boundary", **kwargs) -> "Fdata"`: Validate that exactly one of `n_points` / `factor` is not None — raise `ValueError` describing that exactly one of the two must be given when both or neither are provided. When `factor` is given, compute `target = round(self.n_points * factor)` as an int. When `n_points` is given, `target = int(n_points)`. If `target < 2`, raise `ValueError` stating the target point count must be at least 2. Build the grid with `np.linspace(self.rangeval[0], self.rangeval[1], target)` and return `self.interpolate(grid, policy=policy, **kwargs)`. Use `"boundary"` as the default policy because the linspace endpoints coincide with the domain edges and boundary avoids floating-point edge exceptions (confirmed: `interpolate()` forwards policy to `spline_interpolate_with_policy`, which supports the `"boundary"` value per docs/represent/interpolation.md policy table).

`upsample(self, factor, policy="boundary", **kwargs) -> "Fdata"`: Raise `ValueError` if `factor` is not a number greater than 1. Compute `target = ceil(self.n_points * factor)` using `math.ceil` (import `math` at top of file if not already imported — verify existing imports first). Return `self.resample(n_points=target, policy=policy, **kwargs)`.

`downsample(self, factor, policy="boundary", **kwargs) -> "Fdata"`: Raise `ValueError` if `factor` is not a number greater than 1. Compute `target = max(2, int(self.n_points / factor))`. Return `self.resample(n_points=target, policy=policy, **kwargs)`.

Note: these methods target 1-D Fdata (same limitation as `interpolate()`); do not add 2-D handling. `self.rangeval` for 1-D is a `(min, max)` tuple — index `[0]` / `[1]` directly (confirmed by `__repr__` at line 283).

Then append a `TestFdataResampleMethods` class to `tests/test_represent.py` (after `TestFdataInterpolateMethods`, ~line 362), reusing the same `fd_linear` fixture style (two curves `y_i = (i+1)*t` on a uniform grid). Cover every case in <behavior> above using `pytest.raises(ValueError)` for the error paths and `assert out.n_points ==` / `out.n_obs ==` for the shape assertions.</action>
  <verify>
    <automated>.venv/bin/python -m pytest tests/test_represent.py -k "Resample" -q</automated>
  </verify>
  <done>All new resample/upsample/downsample tests pass; methods return new Fdata objects with correct n_points and raise ValueError on the invalid-argument cases.</done>
</task>

<task type="auto">
  <name>Task 2: Document resample/upsample/downsample in interpolation.md</name>
  <files>docs/represent/interpolation.md</files>
  <action>Add a new `## Resampling convenience methods` section to `docs/represent/interpolation.md`, placed after the existing "## Worked example" section (ends at line 101) and before "## API summary" (line 103).

Write prose explaining that `Fdata.resample()`, `Fdata.upsample()`, and `Fdata.downsample()` are thin convenience wrappers that build a uniform grid over the current `rangeval` and delegate to `Fdata.interpolate()` — no new numerics, just grid construction. State that the default `policy="boundary"` is chosen because the uniform grid's endpoints coincide with the domain edges, so boundary safely handles floating-point edge cases. Note that exactly one of `n_points` / `factor` must be passed to `resample`, and that `upsample`/`downsample` require `factor > 1`.

Add a small method-summary table (columns: Method | Signature | Effect) covering the three methods.

Add a runnable markdown-exec worked example fenced block using the SAME fence header and helpers as the existing example (`\`\`\`python exec="1" html="1" source="above"`, importing `from docs_data import load_growth` and `from docs_fig import fig, render`, printing `render(f)` and a trailing `FDARS_FENCE_OK` sentinel line — mirror lines 50-101). The example must: load growth data via `load_growth()`, wrap it into an `Fdata` (`from fdars import Fdata`; construct `Fdata(X, argvals=age)`), then demonstrate `fd.upsample(4)` and `fd.downsample(3)`, plotting a few curves from each and printing the resulting `.n_points` for both alongside the sentinel. Code must run against the current fdars API and the existing `docs/data/growth.csv` dataset — do not invent new datasets or API calls.

Do NOT wire a new nav entry: this extends the existing `Interpolation: represent/interpolation.md` page already in `mkdocs.yml` (line 98), so no `mkdocs.yml` change is required.</action>
  <verify>
    <automated>grep -q "Resampling convenience methods" docs/represent/interpolation.md &amp;&amp; grep -c "FDARS_FENCE_OK" docs/represent/interpolation.md | grep -qv '^0$' &amp;&amp; echo OK</automated>
  </verify>
  <done>interpolation.md contains a "Resampling convenience methods" section documenting all three methods with a runnable markdown-exec example that uses load_growth() and Fdata.upsample()/downsample(); no mkdocs.yml nav change needed.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking-human">
  <name>Task 3: Verify docs page renders and example runs on built site</name>
  <action>Per project CLAUDE.md, docs correctness is validated by section review on the built site, not assumed. Build the interpolation docs page and confirm the new resampling example fence executes without error and renders sensible plots.

Build recipe (per project memory docs-diagram-verify-workflow): activate the docs venv, set PYTHONPATH so `docs_data`/`docs_fig` helpers resolve, and build the site (DOCS_FAST is acceptable for a single-page check). Then open `docs/represent/interpolation.md`'s rendered output and confirm: (1) the new "Resampling convenience methods" section renders, (2) the markdown-exec fence executed (the `FDARS_FENCE_OK` sentinel appears and figures rendered, no traceback), (3) the upsample/downsample n_points printout is sensible (upsample > source points, downsample < source points).</action>
  <verify>
    <human-check>Built interpolation.md page shows the resampling section, the example fence ran cleanly (figures + FDARS_FENCE_OK, no traceback), and printed n_points values are sensible.</human-check>
  </verify>
  <done>Human confirms the docs page renders correctly and the resampling example runs against the current API on the built site.</done>
</task>

</tasks>

<verification>
- `.venv/bin/python -m pytest tests/test_represent.py -k "Resample" -q` passes
- `python -c "from fdars import Fdata; import numpy as np; fd=Fdata(np.random.randn(3,11)); assert fd.upsample(2).n_points>11 and fd.downsample(2).n_points<11"` runs clean
- interpolation.md contains the new section and a runnable fence
- docs build renders the page and executes the example (human checkpoint)
</verification>

<success_criteria>
- resample/upsample/downsample exist on Fdata, delegate to interpolate(), with NumPy-style docstrings
- Correct ValueError behavior for both/neither args, target < 2, and factor <= 1
- No new Rust/PyO3 code; no extension rebuild required
- Docs page extended and human-verified on the built site
</success_criteria>

<output>
Create `.planning/quick/260905-htx-add-resample-upsample-downsample-conveni/260905-htx-SUMMARY.md` when done
</output>
