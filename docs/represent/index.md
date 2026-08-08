# Represent

<div class="fdars-section-hero fdars-sec-represent" markdown>
<img src="../assets/cards/represent.svg" alt="Represent illustration: a curve decomposed into basis components and coefficients">
<div class="fdars-section-hero__text" markdown>
**Decompose, transform, rank, and measure functional data.**

The Represent module brings together the core tools for analyzing functional data beyond simple summary statistics. Whether you need to extract the dominant modes of variation, project curves onto a finite basis, rank observations by their centrality, or quantify how different two functional samples are, this section has you covered.
</div>
</div>

<div class="fdars-gallery fdars-sec-represent">
<a class="fdars-gallery-item" href="fpca/">
<img class="fdars-gallery-thumb" src="../assets/thumb/fpca.svg" alt="">
<div class="fdars-gallery-title">Functional PCA</div>
<div class="fdars-gallery-desc">Extract dominant modes of variation with weighted FPCA.</div>
</a>
<a class="fdars-gallery-item" href="elastic-fpca/">
<img class="fdars-gallery-thumb" src="../assets/thumb/elastic-fpca.svg" alt="">
<div class="fdars-gallery-title">Elastic FPCA</div>
<div class="fdars-gallery-desc">Separate amplitude and phase with horizontal, vertical, and joint FPCA.</div>
</a>
<a class="fdars-gallery-item" href="basis-representation/">
<img class="fdars-gallery-thumb" src="../assets/thumb/basis-representation.svg" alt="">
<div class="fdars-gallery-title">Basis Representation</div>
<div class="fdars-gallery-desc">B-spline, Fourier, and P-spline expansions with automatic selection.</div>
</a>
<a class="fdars-gallery-item" href="andrews-transformation/">
<img class="fdars-gallery-thumb" src="../assets/thumb/andrews-transformation.svg" alt="">
<div class="fdars-gallery-title">Andrews Transformation</div>
<div class="fdars-gallery-desc">Turn multivariate tables into curves for visual exploration.</div>
</a>
<a class="fdars-gallery-item" href="depth-functions/">
<img class="fdars-gallery-thumb" src="../assets/thumb/depth-functions.svg" alt="">
<div class="fdars-gallery-title">Depth Functions</div>
<div class="fdars-gallery-desc">Fraiman-Muniz, band, modal, random projection, Tukey, and spatial depth.</div>
</a>
<a class="fdars-gallery-item" href="streaming-depth/">
<img class="fdars-gallery-thumb" src="../assets/thumb/streaming-depth.svg" alt="">
<div class="fdars-gallery-title">Streaming Depth</div>
<div class="fdars-gallery-desc">Flag out-of-distribution curves online against a reference window.</div>
</a>
<a class="fdars-gallery-item" href="distance-metrics/">
<img class="fdars-gallery-thumb" src="../assets/thumb/distance-metrics.svg" alt="">
<div class="fdars-gallery-title">Distance Metrics</div>
<div class="fdars-gallery-desc">Lp, Hausdorff, DTW, Soft-DTW, Fourier, and horizontal-shift distances.</div>
</a>
</div>

!!! info "Scope & limitations"

    The Represent tools assume **real-valued functions sampled on a single shared grid**. Keep these boundaries in mind:

    - **FPCA and basis representation are linear.** They fit the best linear subspace of $L^2$ and assume the data lies near it. Strong nonlinear or phase (warping) variation is captured poorly — use [Elastic FPCA](elastic-fpca.md) (align first, then separate amplitude and phase) instead.
    - **Basis systems are B-spline and Fourier only** (with optional P-spline penalization); there are no density-specific bases.
    - **Constrained-range or density data is not supported.** Data that must stay nonnegative, integrate to 1, or remain bounded/monotone can be pushed out of its valid range by linear FPCA and means — transform to an unconstrained space (e.g. CLR or log-quantile-density) first.
    - **Sparse or irregular per-curve sampling is not supported.** Pre-smooth each curve onto the common grid first.
    - **Manifold-valued data is out of scope.**
