# Align

**Register and align curves to separate amplitude from phase variability.**

Functional observations often exhibit two fundamentally different sources of variation: *amplitude* (how tall or deep the features are) and *phase* (when those features occur). Standard statistical methods conflate the two, leading to washed-out means and inflated variance estimates. The Align module provides elastic alignment tools built on the Fisher-Rao metric and the Square Root Slope Function (SRSF) framework to cleanly decompose these sources of variability.

<div class="grid cards" markdown>

-   :material-swap-horizontal:{ .lg .middle } **Elastic Alignment**

    ---

    Pairwise and group alignment via the SRSF transform, Karcher mean, and elastic distances. Separate amplitude from phase, compute warping functions, and build elastic distance matrices.

    [:octicons-arrow-right-24: Elastic Alignment](elastic-alignment.md)

-   :material-shape:{ .lg .middle } **Shape Analysis**

    ---

    Quotient-space shape distances, elastic depth measures, and elastic FPCA. Decompose functional data into amplitude and phase principal components for downstream modeling.

    [:octicons-arrow-right-24: Shape Analysis](shape-analysis.md)

</div>
