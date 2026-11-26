# Align

<div class="fdars-section-hero fdars-sec-align" markdown>
<img src="../assets/cards/align.svg" alt="Align illustration: two phase-shifted curves warped onto a shared template">
<div class="fdars-section-hero__text" markdown>
**Register and align curves to separate amplitude from phase variability.**

Functional observations vary in two ways: *amplitude* (how tall or deep the features are) and *phase* (when those features occur). Methods that ignore phase blur the mean and inflate the variance. The Align module estimates a warping function per curve, so that the registered curves $x_i(h_i(t))$ carry the amplitude and the warps $h_i$ carry the phase. It covers rigid shifts, affine and landmark warps, smooth Ramsay–Li registration, elastic (Fisher–Rao / SRSF) alignment with several optimisers, shape spaces of curves, likelihood-based registration of non-Gaussian curves, Bayesian alignment and template-free synchronisation.
</div>
</div>

**Not sure where to start?** Read [Choosing an Alignment Method](choosing-a-method.md): it matches the kind of phase variability in your data to a method, and shows on simulated data why the smallest matching warp class wins.

## Start here

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="choosing-a-method/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/choosing-a-method.svg" alt="">
<div class="fdars-gallery-title">Choosing a Method</div>
<div class="fdars-gallery-desc">Decision tree, comparison table, recommendations and pitfalls for every aligner.</div>
</a>
<a class="fdars-gallery-item" href="alignment-comparison/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/alignment-comparison.svg" alt="">
<div class="fdars-gallery-title">Comparing Methods</div>
<div class="fdars-gallery-desc">No alignment vs elastic vs landmark, side by side.</div>
</a>
</div>

## Rigid &amp; parametric warps

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="shift-registration/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/shift-registration.svg" alt="">
<div class="fdars-gallery-title">Shift Registration</div>
<div class="fdars-gallery-desc">One time delay per curve: least-squares, iterative Newton and landmark shifts.</div>
</a>
<a class="fdars-gallery-item" href="affine-registration/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/affine-registration.svg" alt="">
<div class="fdars-gallery-title">Affine Registration</div>
<div class="fdars-gallery-desc">Shift plus dilation of time, h(t) = a·t + b, with three criteria.</div>
</a>
<a class="fdars-gallery-item" href="landmark-registration/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/landmark-registration.svg" alt="">
<div class="fdars-gallery-title">Landmark Registration</div>
<div class="fdars-gallery-desc">Pin detected features with monotone cubic warps, or elastically between them.</div>
</a>
<a class="fdars-gallery-item" href="continuous-registration/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/continuous-registration.svg" alt="">
<div class="fdars-gallery-title">Continuous Registration</div>
<div class="fdars-gallery-desc">Ramsay–Li smooth monotone warps with a scale-free criterion.</div>
</a>
</div>

## Elastic (Fisher–Rao)

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="elastic-alignment/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/elastic-alignment.svg" alt="">
<div class="fdars-gallery-title">Elastic Alignment</div>
<div class="fdars-gallery-desc">SRSF registration, Karcher mean, and amplitude/phase separation.</div>
</a>
<a class="fdars-gallery-item" href="elastic-optimisers/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/elastic-optimisers.svg" alt="">
<div class="fdars-gallery-title">Elastic Optimisers &amp; Penalties</div>
<div class="fdars-gallery-desc">DP, DP2 and RBFGS, warp penalties, the λ scale and the band.</div>
</a>
<a class="fdars-gallery-item" href="banded-alignment/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/banded-alignment.svg" alt="">
<div class="fdars-gallery-title">Banded Elastic Alignment</div>
<div class="fdars-gallery-desc">A Sakoe–Chiba corridor around the diagonal for long curves.</div>
</a>
<a class="fdars-gallery-item" href="advanced-alignment/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/advanced-alignment.svg" alt="">
<div class="fdars-gallery-title">Advanced Elastic Alignment</div>
<div class="fdars-gallery-desc">Closed curves, partial matching, multiresolution, geodesics, generative models.</div>
</a>
<a class="fdars-gallery-item" href="tsrvf/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/tsrvf.svg" alt="">
<div class="fdars-gallery-title">TSRVF</div>
<div class="fdars-gallery-desc">Linearised elastic analysis in the tangent space at the mean.</div>
</a>
<a class="fdars-gallery-item" href="shape-analysis/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/shape-analysis.svg" alt="">
<div class="fdars-gallery-title">Shape Analysis (1-D)</div>
<div class="fdars-gallery-desc">Shape quotients, shape means and elastic FPCA for real-valued curves.</div>
</a>
</div>

## Shapes

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="curve-shapes/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/curve-shapes.svg" alt="">
<div class="fdars-gallery-title">Shapes of Curves in R^d</div>
<div class="fdars-gallery-desc">Outlines and trajectories modulo translation, scale, rotation, speed and start point.</div>
</a>
</div>

## Special data

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="sparse-elastic/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/sparse-elastic.svg" alt="">
<div class="fdars-gallery-title">Sparse &amp; Irregular Curves</div>
<div class="fdars-gallery-desc">Elastic distances and spline means from a few irregular points per curve.</div>
</a>
<a class="fdars-gallery-item" href="expfam-registration/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/expfam-registration.svg" alt="">
<div class="fdars-gallery-title">Non-Gaussian Registration</div>
<div class="fdars-gallery-desc">Binary and count curves registered on the likelihood scale, with GFPCA.</div>
</a>
</div>

## Template-free &amp; probabilistic

<div class="fdars-gallery fdars-sec-align">
<a class="fdars-gallery-item" href="pairwise-synchronization/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/pairwise-synchronization.svg" alt="">
<div class="fdars-gallery-title">Pairwise Synchronisation</div>
<div class="fdars-gallery-desc">Tang–Müller: each warp is the inverted average of pairwise warps.</div>
</a>
<a class="fdars-gallery-item" href="bayesian-alignment/">
<img class="fdars-gallery-thumb" aria-hidden="true" src="../assets/thumb/bayesian-alignment.svg" alt="">
<div class="fdars-gallery-title">Bayesian Alignment</div>
<div class="fdars-gallery-desc">Posterior warps and template by pCN or infHMC, with R̂, ESS and tempering.</div>
</a>
</div>

!!! info "Scope"

    - **Real-valued curves on one shared grid** (`argvals`) are supported by every family on these pages.
    - **Irregular or incomplete grids** are handled by `register_fpca` (curves observed on their own grids, optionally cut off at the start or end) and by the sparse elastic functions `sparse_elastic_align_pair` / `sparse_elastic_mean`. `elastic_partial_match` matches a short curve to a sub-interval of a longer one.
    - **Curves in $\mathbb{R}^d$**: the shape-space functions `curve_shape_*` quotient out translation, scale, rotation, reparametrisation and (for closed curves) the starting point; `karcher_mean_nd_with_config` and the other `*_nd_with_config` functions share one warp across coordinates without rotation or scale invariance.
    - **Non-Gaussian values** (binary, counts, positive-skewed): `register_fpca(family=...)`.
    - **Time series of different lengths** for search and classification: the DTW family in `fdars.metric`.
    - **Still unsupported:** manifold-valued trajectories other than the shape space (sphere-, SPD- or rotation-valued curves) and density-valued curves. Transform them to an unconstrained space first.
