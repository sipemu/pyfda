# Feature Research

**Domain:** Documentation set for a scientific/statistical Python library (fdars — functional data analysis)
**Researched:** 2026-08-07
**Confidence:** MEDIUM (web survey of comparable libraries; cross-checked against existing fdars docs and codebase)

---

## Scope note

The "features" here are **documentation features** — components, patterns, and content types that belong in a best-in-class doc set for a scientific Python library at the level of scikit-learn, statsmodels, or scikit-fda. The three categories map directly to the fdars documentation overhaul deliverables: SVG concept diagrams and worked example pages.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Missing any of these makes the doc set feel incomplete or untrustworthy compared to peer libraries.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| One concept diagram per method page | Every page in scikit-learn's user guide, scikit-fda's examples, and statsmodels has at least one figure explaining the method — textual-only pages feel like stubs | LOW per diagram, HIGH cumulative | fdars already has ~50 SVGs; the gap is accuracy and coverage completeness |
| Diagram accurately depicts the method | A diagram that shows the wrong geometry or wrong data flow undermines trust in the whole site; scikit-learn treats inaccurate figures as bugs | MEDIUM (requires domain review) | Highest-priority table-stake for this milestone per PROJECT.md |
| Shared visual style across all diagrams | Peer libraries have consistent palette, font, and layout — inconsistency signals unmaintained docs | MEDIUM (style spec + rollout) | fdars has an informal baseline; formalizing it is the first milestone task |
| Problem → Data → Method → Interpretation narrative in examples | The gold-standard worked-example structure used by statsmodels, GPyTorch tutorials, and scikit-fda examples — users learn by following a complete story, not isolated code snippets | MEDIUM per example | fdars already follows this pattern (e.g., tecator-regression.md, growth-alignment.md); needs consistent application across all 17 pages |
| Executable, reproducible example code | Examples must run against the current API and produce shown output — broken examples are the most common complaint in scientific library docs | MEDIUM (CI or manual sweep) | fdars uses markdown-exec for build-time execution; main risk is API drift |
| Cross-links from example pages to API reference | Every function or class used in an example should link to its API reference page — scikit-learn and scikit-fda both do this systematically | LOW per link, MEDIUM to audit all 17 pages | `docs/reference/` exists; cross-links are inconsistently applied |
| Cross-links from concept pages to worked examples | Concept pages (e.g., `fpca.md`) should link to the relevant worked example — guides discovery and reinforces understanding | LOW | Currently inconsistent |
| Inline figures with captions | Figures need a descriptive caption explaining what is shown, not just a filename — scikit-fda always captions figures | LOW per figure | Some fdars example figures lack captions |
| Meaningful axis labels and titles on all figures | Unlabeled axes are a recurring quality complaint in scientific docs; makes figures uninterpretable in isolation | LOW per figure | Check all `markdown-exec` outputs |

### Differentiators (Competitive Advantage)

Features that elevate fdars docs above the scikit-fda / statsmodels baseline.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Diagrams that show before/after transformations, not just static states | Registration/alignment and smoothing both involve a transformation — showing the before state, the transformation (warp), and the after state in one diagram teaches the concept instantly; scikit-fda and most FDA docs do not do this systematically | MEDIUM per diagram | Elastic alignment, landmark registration, and smoothing diagrams are natural candidates |
| Phase-vs-amplitude split diagram (registration context) | The single most abstract concept in FDA is that variation decomposes into phase (timing) and amplitude (magnitude) — a diagram showing two example curves with the same amplitude but different phase, and the warping function that aligns them, resolves the confusion that causes most beginner errors | MEDIUM | One high-quality diagram here is worth more than five generic ones |
| Eigenfunction ± score diagram for FPCA | The standard FPCA visualization (mean ± weighted eigenfunction) shows what each PC *means* for real curves — this is the textbook visual that scikit-fda's FPCA example produces as a figure but fdars docs have as a static SVG; making the static SVG faithfully represent this pattern raises it to reference quality | MEDIUM | fpca.svg needs to show concrete mean ± φ effect, not an abstract ellipse |
| Coefficient surface β(t) diagram for scalar-on-function regression | The estimated coefficient function is non-obvious to a new user — a diagram showing the spectral domain (x-axis), the coefficient curve above zero where frequency matters more for prediction, and its relationship to the raw spectra makes the regression interpretable | MEDIUM | scalar-on-function.md and the Tecator example both need this |
| Dataset-matched diagrams | Diagrams that use the actual fdars built-in datasets (Canadian weather, Tecator spectra, Berkeley growth, phoneme) as their illustrative substrate — so the diagram matches what users will see in the worked examples | HIGH per diagram (need to design from data) | Differentiates from generic statistical textbook diagrams |
| Depth / functional boxplot diagram showing centrality ordering | A diagram showing several curves ordered by depth score, with the most central highlighted and the outliers flagged, teaches functional depth in one glance in a way that no formula can | MEDIUM | depth-functions.svg is a candidate; needs concrete curve geometry |
| SPM Phase I / Phase II workflow diagram | Control-chart monitoring workflow (Phase I: estimate baseline, compute UCL/LCL; Phase II: test new observations) — almost no Python library docs draw this cleanly; a single diagram makes the spm.md page instantly usable by engineers unfamiliar with FDA-specific monitoring | MEDIUM | spm.svg exists; check whether it shows the Phase I/II distinction |
| Conformal prediction band diagram | Showing a functional prediction set (upper and lower bounding curves) around a test curve, versus a classical regression confidence interval, communicates the coverage guarantee visually | MEDIUM | conformal-prediction.svg exists; check accuracy |
| Elastic vs landmark registration side-by-side comparison diagram | Showing two alignment strategies on the same dataset resolves a common "which to use?" question without forcing users to read two separate pages | HIGH | alignment-comparison.svg exists; check whether it actually shows both strategies on shared data |
| Worked example using a domain the target user recognizes (pharma/food/climate) | fdars already has Tecator (food NIR), biopharma-monitoring, Canadian weather — extending to SPM for inline process data or growth for pediatrics is differentiating because most FDA libraries only use the canonical Berkeley/Canadian examples | MEDIUM per new example | biopharma-monitoring.md and inline-monitoring.md are differentiators; needs strong narrative |

### Anti-Features (Deliberately Do NOT Build)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Generic "logo-style" SVG diagrams (shapes + brand colors, no data) | Looks polished at a glance; fast to author | Adds ink without adding information — a diagram of coloured ellipses labelled "input" → "FPCA" → "scores" teaches nothing that the text does not already say; the data/ink ratio is near zero | Replace with a diagram that shows concrete curve geometry: actual curves going in, actual PC scores coming out |
| Over-long worked examples (>500 lines of rendered markdown) | Comprehensiveness feels thorough | Users stop reading; the worked example becomes a reference dump rather than a teaching tool; harder to keep API-current | Split into a short primary example (full narrative) and one or two shorter follow-on examples for advanced topics; the Andrews wine series is already well-structured this way |
| Duplicating API reference content in concept pages | Feels complete | Creates maintenance burden — when the API changes, both the reference and the concept page need updating; common source of staleness | Concept pages explain the why and the intuition; link to API reference for parameter details rather than repeating them |
| Decorative color variation across SVGs for visual interest rather than semantic distinction | Makes the diagram gallery look varied | Colors carry meaning in scientific diagrams — different colors for groups, states, or categories; using colors only for aesthetics trains users to ignore color, which then fails when color IS semantically needed | Establish palette conventions (e.g., blue = observed, orange = estimated, red = outlier) and apply them consistently across all diagrams |
| Auto-generated gallery thumbnails without context | Modern documentation practice; low effort | Without a clear problem statement per example, gallery thumbnails are opaque — users cannot identify which example is relevant without clicking every one | Each example should have a one-sentence problem statement in the index visible without clicking through |
| Interactive widgets (plotly, bokeh, ipywidgets) | Impressive demos; scikit-learn some widgets | Adds a JS dependency to a static MkDocs site; breaks the build-time execution model; increases maintenance surface significantly; fdars PROJECT.md explicitly keeps diagrams as hand-authored SVG | Keep figures as static matplotlib output (SVG or PNG) embedded by markdown-exec; reserve interactivity for external notebooks/examples/ directory |
| Dark-mode SVG variants | Professional look; Material theme supports dark mode | PROJECT.md explicitly excludes dark-mode rework; maintaining two SVG variants per diagram doubles authoring cost | Note the gap; address in a future milestone; for now ensure base SVGs have sufficient contrast for both modes |

---

## Feature Dependencies

```
Shared SVG style spec
    └──required for──> Diagram accuracy sweep (cannot audit 50 diagrams to one bar without a spec)
                           └──required for──> Diagram coverage gap fill (new diagrams must match the style)

API correctness check
    └──required for──> Example narrative enrichment (cannot rewrite the why/interpretation text
                       around code that is broken)
                           └──enables──> New worked examples (validates patterns before adding pages)

Cross-link audit (API ref ↔ concept ↔ examples)
    └──enhances──> Both diagram pages and example pages (all benefit, but neither requires it)
```

### Dependency Notes

- **Style spec required before diagram accuracy sweep:** Reviewing all 50 SVGs without a standard to measure against produces inconsistent corrections. The spec is the shared ruler.
- **API correctness before narrative enrichment:** If `markdown-exec` blocks are silently broken, the narrative built around them becomes fiction. Run/verify all examples first.
- **Coverage gap fill depends on style spec + accuracy sweep:** New diagrams should be authored in the finalized style, not the pre-spec baseline, to avoid a third pass.

---

## Diagram Coverage Analysis by FDA Method Area

This maps which FDA topics most need clear visual explanation and whether the existing diagram is likely sufficient or needs rework.

| FDA Topic | Visual Explanation Need | Existing SVG | Assessment |
|-----------|------------------------|--------------|------------|
| **Smoothing / basis representation** | HIGH — abstract idea of approximating a noisy discrete signal as a smooth function | `smoothing.svg`, `basis-representation.svg` | Likely needs rework: must show raw noisy observations + smooth fit overlaid, with basis expansion inset |
| **FPCA (functional PCA)** | HIGH — eigenfunction concept is non-obvious; ± component effect visualization is canonical | `fpca.svg` | Likely needs rework: must show mean ± φ effect on concrete curves, not abstract ellipse |
| **Elastic registration / alignment** | VERY HIGH — phase vs amplitude split is the most abstract FDA concept; before/after warp is essential | `elastic-alignment.svg`, `alignment-comparison.svg` | Priority rework targets; must show actual misaligned curves + warping function + aligned result |
| **Landmark registration** | HIGH — shows discrete landmarks being matched; different from elastic | `landmark-registration.svg` | Check whether landmarks are visually distinct from the elastic alignment diagram |
| **TSRVF / shape analysis** | HIGH — Fisher-Rao metric and SRVF transformation are opaque without a diagram showing the transform | `tsrvf.svg`, `shape-analysis.svg` | High risk of inaccuracy; these are among the most mathematically complex |
| **Functional regression (scalar-on-function)** | HIGH — coefficient function β(t) is the key output; most users do not know how to read it | `scalar-on-function.svg` | Must show: functional predictor curves + scalar response + β(t) with annotation |
| **Functional regression (function-on-scalar)** | MEDIUM — regression coefficient functions are slightly more intuitive than scalar-on-function | `function-on-scalar.svg` | Check that it shows the fitted curve family, not just an abstract arrow |
| **Elastic regression** | MEDIUM — builds on elastic alignment; the regression in shape space is abstract | `elastic-regression.svg` | Likely needs alignment-aware representation showing pre-aligned inputs |
| **Depth functions / outlier detection** | HIGH — centrality ordering of curves is non-obvious; functional boxplot is the canonical visual | `depth-functions.svg`, `outlier-detection.svg` | Must show actual curves ordered by depth, most central vs extreme, analogous to a box plot |
| **Functional clustering** | MEDIUM — shows groups of curves; similar to classical clustering but in function space | `clustering.svg`, `elastic-clustering.svg`, `gmm-clustering.svg` | Three separate SVGs — check for redundancy and whether they are differentiated clearly |
| **SPM / monitoring** | HIGH — Phase I / Phase II workflow and control chart components (CL, UCL, LCL) are engineering concepts that need a process diagram | `spm.svg`, `advanced-spm.svg`, `profile-partial-monitoring.svg` | Must show the Phase I training → Phase II monitoring two-stage workflow |
| **Conformal prediction** | HIGH — prediction bands (as functional objects) are conceptually different from scalar CIs; needs a diagram of the band geometry | `conformal-prediction.svg`, `conformal-classification.svg` | Check whether diagram shows a functional prediction band vs a scalar CI; often confused |
| **Tolerance bands** | MEDIUM — similar to conformal; the band wraps all future curves with some coverage guarantee | `tolerance-bands.svg` | Check distinction from conformal is clear in the diagram |
| **Equivalence testing** | MEDIUM — needs a diagram showing null hypothesis (curves are equivalent within δ) vs alternative | `equivalence-testing.svg` | Lower coverage risk than the alignment/regression topics |
| **Covariance functions** | MEDIUM — covariance surface C(s,t) is a 2D function over the domain; a heatmap-style illustration | `covariance-functions.svg` | Likely needs to show the covariance surface as a grid or contour |
| **Andrews transformation** | LOW — mostly a visualization technique; the transformation is mechanical | `andrews-transformation.svg` | Lower priority |
| **Seasonal analysis** | LOW — familiar time series concept adapted to functions; the diagram augments but is not essential | `seasonal-analysis.svg` | Lower priority |

---

## Worked Example Coverage Analysis

Existing 17 examples mapped against method coverage gaps.

| Existing Example | Method Covered | Narrative Quality | Gap |
|-----------------|----------------|-------------------|-----|
| `growth-alignment.md` | Elastic alignment, FPCA before/after | Strong (problem-data-method-interpretation) | Check warping function interpretation section |
| `tecator-regression.md` | Scalar-on-function regression | Strong | Check β(t) interpretation section |
| `canadian-weather.md` | Overview / introduction | Strong | — |
| `canadian-precipitation.md` | Precipitation depth / functional boxplot | Check | Depth interpretation |
| `canadian-seasonal.md` | Seasonal decomposition | Check | — |
| `phoneme-shape.md` | Shape analysis / TSRVF | Check | High complexity; interpretation risk |
| `sonar-tsrvf.md` | TSRVF on sonar data | Check | Duplicate of phoneme? Needs distinct narrative |
| `andrews-wine.md` | Andrews transformation | Check | — |
| `andrews-wine-clustering.md` | Clustering | Check | — |
| `andrews-wine-intro.md` | Introduction via wine | Check | Possibly redundant with canadian-weather intro |
| `andrews-wine-qc.md` | Quality control / outliers | Check | — |
| `biopharma-monitoring.md` | SPM in pharma context | Strong domain relevance | Check Phase I/II workflow explicitness |
| `inline-monitoring.md` | Online/streaming monitoring | Check | Explain streaming depth concept |
| `cross-validation.md` | CV for functional models | Check | Needs interpretation of CV scores |
| `explainability-regions.md` | Model explainability | Check | Interpretation of influence regions |
| `tecator-monitoring.md` | SPM on NIR spectra | Check | — |

**Under-documented capabilities (candidates for new worked examples):**

| Capability | Rationale | Suggested Dataset |
|------------|-----------|-------------------|
| Functional clustering (GMM) | GMM clustering page exists but no dedicated worked example with interpretation of cluster means | Andrews wine or simulation |
| Conformal prediction coverage guarantee | Conformal page exists; no example that walks through the coverage guarantee empirically | Tecator or Canadian weather |
| Tolerance bands (vs conformal) | Tolerance bands and conformal bands are easily confused; a worked comparison example resolves this | Canadian weather |
| Outlier detection workflow | `outlier-detection.md` concept page exists; no worked example that shows the full detection → investigation workflow | Simulation or phoneme |
| Function-on-scalar regression with interpretation | Only scalar-on-function has a worked example (Tecator); function-on-scalar (e.g., predict growth curves from sex/age group) is under-represented | Berkeley growth |

---

## MVP Definition

The milestone scope from PROJECT.md is a full sweep, not a selective one. Within that, priority ordering:

### Phase 1 — Foundation (do first, everything depends on it)

- [ ] SVG style spec — defines the ruler for all subsequent diagram work
- [ ] API correctness sweep — verifies all `markdown-exec` blocks produce valid output
- [ ] Nav + reference-API audit — systematic list of diagram gaps and new-example candidates

### Phase 2 — Diagram accuracy and coverage (primary deliverable)

- [ ] Rework highest-risk diagrams: elastic-alignment, fpca, basis-representation, scalar-on-function, depth-functions, spm, conformal-prediction (see Diagram Coverage Analysis above)
- [ ] Close verified coverage gaps identified in the audit
- [ ] Apply shared style spec to all existing diagrams

### Phase 3 — Example narrative and coverage (secondary deliverable)

- [ ] Audit and enrich interpretation sections in existing 17 examples
- [ ] Add new worked examples for the identified under-documented capabilities
- [ ] Verify cross-links from examples to API reference and concept pages

### Defer (v2+)

- [ ] Dark-mode SVG variants — excluded from this milestone
- [ ] Interactive figures (plotly/bokeh) — excluded from this milestone
- [ ] Full Diataxis restructure of nav — would require content reorganization beyond scope

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| SVG style spec | HIGH — enables all other diagram work | LOW | P1 |
| Rework elastic-alignment diagram (before/after warp) | HIGH — most-queried FDA concept | MEDIUM | P1 |
| Rework FPCA diagram (mean ± eigenfunction) | HIGH — canonical FDA visualization | MEDIUM | P1 |
| Rework scalar-on-function diagram (β(t) annotated) | HIGH — regression interpretation | MEDIUM | P1 |
| Rework depth-functions / outlier diagram | HIGH — centrality is non-obvious | MEDIUM | P1 |
| Rework SPM diagram (Phase I/II workflow) | HIGH — engineers need the workflow | MEDIUM | P1 |
| Fix broken example code (API correctness) | HIGH — broken examples destroy trust | LOW–MEDIUM | P1 |
| Rework basis-representation diagram | HIGH — conceptual foundation | MEDIUM | P1 |
| Add interpretation prose to existing examples | MEDIUM — improves but not critical to usability | MEDIUM | P2 |
| Rework TSRVF / shape-analysis diagrams | MEDIUM — complex, risk of inaccuracy | HIGH | P2 |
| Cross-link audit (example ↔ API ↔ concept) | MEDIUM — improves discoverability | LOW | P2 |
| New worked example: conformal prediction coverage | MEDIUM — differentiates | MEDIUM | P2 |
| New worked example: function-on-scalar regression | MEDIUM — coverage gap | MEDIUM | P2 |
| New worked example: outlier detection workflow | MEDIUM — coverage gap | MEDIUM | P2 |
| Rework covariance-functions diagram | LOW — niche use | MEDIUM | P3 |
| New worked example: GMM clustering | LOW — already 3 clustering examples | MEDIUM | P3 |
| Andrews / seasonal diagram refinements | LOW — lower complexity topics | LOW | P3 |

---

## Competitor Feature Analysis

| Doc Feature | scikit-learn | scikit-fda | statsmodels | fdars current | fdars target |
|-------------|-------------|------------|-------------|---------------|--------------|
| Concept diagram per method page | Yes (most pages) | Inline plots via sphinx-gallery | Some | Yes (~50 SVGs) | Yes, all pages, accurate |
| Shared visual style | Yes (matplotlib defaults) | sphinx-gallery auto-style | Inconsistent | Informal baseline | Formalized spec |
| Problem → Data → Method → Interpretation narrative | Partial (user guide focused on method) | Yes (examples) | Yes (notebooks) | Yes (best examples) | Consistent across all 17 |
| Executable examples at build time | sphinx-gallery | sphinx-gallery | nbconvert | markdown-exec | markdown-exec (existing) |
| Cross-links concept ↔ API ↔ examples | Dense and bidirectional | Moderate | Partial | Sparse | Systematic |
| Dataset-specific diagram (vs generic) | Rarely | Yes (uses real datasets) | Rarely | Rarely | Target for top-priority diagrams |
| Phase I/II SPM workflow diagram | N/A (no SPM) | No | Partial (time series) | Partial | Explicit Phase I/II diagram |
| Conformal prediction visual | No | No | No | Yes (SVG exists) | Check accuracy; differentiator |
| Functional boxplot / depth diagram | No | Yes (sphinx-gallery plot) | No | Partial | Full centrality ordering diagram |

---

## Sources

- [scikit-fda examples index](https://fda.readthedocs.io/en/latest/auto_examples/index.html) — MEDIUM confidence (web)
- [scikit-fda FPCA example](https://fda.readthedocs.io/en/stable/auto_examples/plot_fpca.html) — MEDIUM confidence (web)
- [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html) — MEDIUM confidence (web)
- [Scientific Python Development Guide — documentation](https://learn.scientific-python.org/development/guides/docs/) — MEDIUM confidence (web)
- [Diátaxis framework](https://diataxis.fr/) — MEDIUM confidence (web)
- [statsmodels examples](https://www.statsmodels.org/stable/examples/index.html) — MEDIUM confidence (web)
- [Sphinx-Gallery structuring guide](https://sphinx-gallery.github.io/stable/syntax.html) — MEDIUM confidence (web)
- [GPyTorch regression tutorial](https://docs.gpytorch.ai/en/stable/examples/01_Exact_GPs/Simple_GP_Regression.html) — MEDIUM confidence (web)
- Research into elastic FDA (Fisher-Rao metric, SRVF framework) from arxiv.org/pdf/1103.3817 — MEDIUM confidence (web)
- Existing fdars docs survey (`docs/examples/`, `docs/represent/`, `docs/assets/diagrams/`) — HIGH confidence (direct inspection)

---

*Feature research for: fdars documentation overhaul (diagrams + examples)*
*Researched: 2026-08-07*
