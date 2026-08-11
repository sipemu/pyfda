# Align

<div class="fdars-section-hero fdars-sec-align" markdown>
<img src="../assets/cards/align.svg" alt="Align illustration: two phase-shifted curves warped onto a shared template">
<div class="fdars-section-hero__text" markdown>
**Register and align curves to separate amplitude from phase variability.**

Functional observations often exhibit two fundamentally different sources of variation: *amplitude* (how tall or deep the features are) and *phase* (when those features occur). Standard statistical methods conflate the two, leading to washed-out means and inflated variance estimates. The Align module provides elastic alignment tools built on the Fisher-Rao metric and the Square Root Slope Function (SRSF) framework to cleanly decompose these sources of variability.
</div>
</div>

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="elastic-alignment/">
<img class="fdars-gallery-thumb" src="../assets/thumb/elastic-alignment.svg" alt="">
<div class="fdars-gallery-title">Elastic Alignment</div>
<div class="fdars-gallery-desc">SRSF registration, Karcher mean, and amplitude/phase separation.</div>
</a>
<a class="fdars-gallery-item" href="advanced-alignment/">
<img class="fdars-gallery-thumb" src="../assets/thumb/advanced-alignment.svg" alt="">
<div class="fdars-gallery-title">Advanced Elastic Alignment</div>
<div class="fdars-gallery-desc">Closed, constrained, penalized, and multi-resolution alignment.</div>
</a>
<a class="fdars-gallery-item" href="landmark-registration/">
<img class="fdars-gallery-thumb" src="../assets/thumb/landmark-registration.svg" alt="">
<div class="fdars-gallery-title">Landmark Registration</div>
<div class="fdars-gallery-desc">Align curves by matching landmark locations with monotone warps.</div>
</a>
<a class="fdars-gallery-item" href="tsrvf/">
<img class="fdars-gallery-thumb" src="../assets/thumb/tsrvf.svg" alt="">
<div class="fdars-gallery-title">TSRVF</div>
<div class="fdars-gallery-desc">Linearized elastic analysis in a transported tangent space.</div>
</a>
<a class="fdars-gallery-item" href="alignment-comparison/">
<img class="fdars-gallery-thumb" src="../assets/thumb/alignment-comparison.svg" alt="">
<div class="fdars-gallery-title">Comparing Methods</div>
<div class="fdars-gallery-desc">No alignment vs elastic vs landmark, side by side.</div>
</a>
<a class="fdars-gallery-item" href="shape-analysis/">
<img class="fdars-gallery-thumb" src="../assets/thumb/shape-analysis.svg" alt="">
<div class="fdars-gallery-title">Shape Analysis</div>
<div class="fdars-gallery-desc">Shape-preserving registration and geodesic computations.</div>
</a>
</div>

!!! info "Scope & limitations"

    fdars alignment operates on **real-valued curves sampled on a single shared grid** (`argvals`) common to every observation — the `Fdata` constructor and `stack` enforce this. Keep these boundaries in mind:

    - **Sparse or irregular per-curve sampling is not supported.** Pre-smooth each curve onto the shared grid first. The one exception is `elastic_partial_match`, which accepts two mismatched grids but is strictly pairwise.
    - **The elastic machinery is 1-D (SRSF / Fisher–Rao).** For ordinary real-valued curves in Euclidean space, TSRVF collapses to SRVF. Genuinely *manifold-valued* trajectories (sphere, SPD/covariance-over-time, shapes, rotations) are **not supported** — there are no exp/log maps, geodesic mean, or PGA.
    - **Constrained-range or density-valued curves are not supported.** Transform them to an unconstrained space before aligning.
    - **Supported beyond the basics:** closed/periodic curves (`elastic_align_pair_closed`, `karcher_mean_closed`) and landmark-constrained alignment (`elastic_align_pair_constrained`).
