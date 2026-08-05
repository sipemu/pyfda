# Examples

End-to-end case studies on **real, classic functional-data datasets**. Each
page loads a vendored dataset, runs a genuine `fdars` analysis, and generates
its figures at build time — so the code you read is exactly the code that
produced the plots.

The datasets (Berkeley Growth, Canadian Weather, Tecator, Phoneme) live under
`docs/data/` with sources and licenses documented in the
[data README](../data/README.md); they are loaded through the small helper
`docs_data`.

<div class="fdars-gallery" markdown>

<a class="fdars-gallery-item" href="growth-alignment/">
<div class="fdars-gallery-title">Growth curve alignment</div>
<div class="fdars-gallery-desc">Berkeley Growth Study: separate the timing of the pubertal growth spurt from its size with elastic alignment and the Karcher mean.</div>
</a>

<a class="fdars-gallery-item" href="tecator-regression/">
<div class="fdars-gallery-title">Predicting fat from NIR spectra</div>
<div class="fdars-gallery-desc">Tecator: scalar-on-function PLS regression predicts meat fat content from 100-channel absorbance spectra, with an interpretable coefficient curve.</div>
</a>

<a class="fdars-gallery-item" href="canadian-weather/">
<div class="fdars-gallery-title">Weather curves: FPCA & clustering</div>
<div class="fdars-gallery-desc">Canadian Weather: functional PCA finds the dominant modes of temperature variation, and k-means recovers Canada's climate regions from the curves alone.</div>
</a>

</div>

## What each example shows

| Example | Dataset | fdars techniques |
|---------|---------|------------------|
| [Growth curve alignment](growth-alignment.md) | Berkeley Growth | `deriv_1d`, `elastic_align_pair`, `karcher_mean` |
| [Predicting fat from NIR spectra](tecator-regression.md) | Tecator | `deriv_1d`, `fregre_pls`, `predict_fregre_pls`, `fregre_np` |
| [Weather curves: FPCA & clustering](canadian-weather.md) | Canadian Weather | `fpca`, `kmeans_fd`, `silhouette_score_data` |

!!! tip "Reproducing locally"
    Every dataset is loadable outside the docs too:

    ```python
    import sys; sys.path.insert(0, "scripts")
    from docs_data import load_growth, load_canadian_weather, load_tecator, load_phoneme

    age, X, meta = load_growth()          # (argvals, curves, labels)
    ```
