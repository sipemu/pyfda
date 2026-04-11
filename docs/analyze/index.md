# Analyze

**Infer, cluster, detect outliers, and test functional data.**

The Analyze module collects the tools you reach for once your curves are represented and aligned: find groups via clustering, flag anomalous observations, construct tolerance bands, test whether two populations are equivalent, decompose seasonal patterns, and explore covariance structure. Every algorithm runs in Rust for maximum throughput.

<div class="grid cards" markdown>

-   :material-chart-bell-curve:{ .lg .middle } **Tolerance Bands**

    ---

    Construct simultaneous tolerance bands (FPCA bootstrap, conformal prediction, Degras SCB) and test functional equivalence between two groups.

    [:octicons-arrow-right-24: Tolerance Bands](tolerance-bands.md)

-   :material-scatter-plot:{ .lg .middle } **Clustering**

    ---

    Partition functional observations with k-means, fuzzy c-means, and Gaussian mixture models. Assess cluster quality with silhouette and Calinski-Harabasz indices.

    [:octicons-arrow-right-24: Clustering](clustering.md)

-   :material-alert-circle-outline:{ .lg .middle } **Outlier Detection**

    ---

    Identify magnitude, shape, and amplitude outliers via LRT tests, the outliergram, and magnitude-shape outlyingness plots.

    [:octicons-arrow-right-24: Outlier Detection](outlier-detection.md)

-   :material-sine-wave:{ .lg .middle } **Seasonal Analysis**

    ---

    Detect periods with SAZED, autoperiod, and CFD-autoperiod. Decompose curves with STL, find peaks, and measure seasonal strength.

    [:octicons-arrow-right-24: Seasonal Analysis](seasonal-analysis.md)

-   :material-approximately-equal:{ .lg .middle } **Equivalence Testing**

    ---

    Determine whether two groups of curves are practically equivalent within a tolerance margin using functional TOST.

    [:octicons-arrow-right-24: Equivalence Testing](equivalence-testing.md)

-   :material-grid:{ .lg .middle } **Covariance Functions**

    ---

    Build covariance matrices from Gaussian, exponential, Matern, and periodic kernels. Generate Gaussian process samples for simulation studies.

    [:octicons-arrow-right-24: Covariance Functions](covariance-functions.md)

</div>
