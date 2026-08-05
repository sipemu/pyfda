# Vendored datasets

Small, public classic functional-data datasets used by the pages under
`docs/examples/`. They are loaded at documentation build time through the
helper `scripts/docs_data.py` (importable as `docs_data` because `scripts/`
is on `PYTHONPATH` during the build, alongside `docs_fig`).

Each loader returns `(argvals, X, meta)`: a shared 1-D grid, an
`(n_obs, n_points)` array of curves (one observation per row), and a
`pandas.DataFrame` of per-observation labels aligned to the rows of `X`.

| File | Loader | Shape (obs × pts) | Source | License |
|------|--------|-------------------|--------|---------|
| `growth.csv` | `load_growth()` | 93 × 31 | `growth` dataset, R `fda` package | GPL-2/3 |
| `canadian_weather.csv` (+ `_precip`, `_meta`) | `load_canadian_weather()` | 35 × 365 | `CanadianWeather`, R `fda` package | GPL-2/3 |
| `tecator.csv` | `load_tecator()` | 240 × 100 | StatLib Tecator dataset | Public domain (redistributable) |
| `phoneme.csv` | `load_phoneme()` | 400 × 256 | ElemStatLearn phoneme data | Public / redistributable (ESL) |
| `wine.csv` | `load_wine()` | 178 × 13 | UCI Wine dataset | CC BY 4.0 (UCI) |
| `sonar.csv` | `load_sonar()` | 208 × 60 | UCI Connectionist Bench (Sonar) | CC BY 4.0 (UCI) |
| _(synthetic)_ | `load_penicillin()` | 46 × 200 | Simulated in `docs_data.py` | n/a (generated) |

## Details

### `growth.csv` — Berkeley Growth Study
Heights (cm) of **39 boys and 54 girls** measured at **31 ages** (1–18 years,
yearly to age 8 then biannual). Wide format: column `age` plus one column per
child (`M01…M39` boys, `F01…F54` girls). `load_growth()` returns ages,
`X` of shape `(93, 31)` (boys then girls), and `meta` with `id`, `sex`.

- Source: `data/growth.rda` from the R `fda` package
  (<https://github.com/cran/fda>, originally Ramsay & Silverman, *FDA*).
- License: GPL-2 | GPL-3 (the `fda` package license).

### `canadian_weather.csv` — Canadian Weather
Daily **mean temperature (°C)** for **35 Canadian weather stations** over a
365-day year (averaged over 1960–1994). Wide format: column `day` (1–365)
plus one column per station. Companion files:
`canadian_weather_precip.csv` (daily precipitation, mm) and
`canadian_weather_meta.csv` (`station`, `province`, `region`, `lat`, `lon`).
`load_canadian_weather(variable="temperature"|"precipitation")` returns the
day grid, `X` of shape `(35, 365)`, and the station metadata aligned to rows.

- Source: `data/CanadianWeather.rda` from the R `fda` package
  (<https://github.com/cran/fda>).
- License: GPL-2 | GPL-3.

### `tecator.csv` — Tecator NIR spectra
Near-infrared **absorbance spectra (100 channels, 850–1050 nm)** of **240
finely chopped meat samples**, with lab-measured `moisture`, `fat` and
`protein` content (percent). Columns: `sample`, `ch001…ch100`, then the three
contents. `load_tecator()` returns the 100 wavelengths, `X` of shape
`(240, 100)`, and `meta` with the contents.

- Source: StatLib, <https://lib.stat.cmu.edu/datasets/tecator>. Recorded on a
  Tecator Infratec Food and Feed Analyzer.
- License: Public domain — the StatLib note explicitly permits redistribution
  ("The data can be redistributed as long as this permission note is
  attached"); if used in a publication, mention the instrument/company
  (Tecator). Only the 100 absorbances + contents are vendored (the 22
  precomputed principal components in the original file are dropped).

### `phoneme.csv` — Phoneme log-periodograms
**Log-periodograms (256 frequencies)** of spoken phonemes. This is a
**balanced, seeded subset**: **80 curves from each** of 5 classes
(`aa`, `ao`, `iy`, `sh`, `dcl`) = **400 rows** (the full ElemStatLearn file
has 4509 rows across these classes; subset with `numpy` seed 0). Columns:
`phoneme` (class) then `f001…f256`. `load_phoneme()` returns the frequency
index, `X` of shape `(400, 256)`, and `meta` with `phoneme`.

- Source: `phoneme.data` from *The Elements of Statistical Learning*
  (<https://hastie.su.domains/ElemStatLearn/>), originally the TIMIT database.
- License: distributed with ESL for research/teaching; redistributable subset.

### `wine.csv` — Wine (UCI)
**13 chemical measurements** (alcohol, phenols, colour intensity, proline, …)
for **178 wines** from **3 cultivars**. This is a multivariate *table*, used as
the input to the Andrews transformation (feature vector → curve). Columns:
`class` (1/2/3) then the 13 features. `load_wine()` returns the 13 feature names
(not an `argvals` grid), `X` of shape `(178, 13)` (raw), and `meta` with `cultivar`.

- Source: UCI ML Repository, Wine (<https://archive.ics.uci.edu/dataset/109/wine>).
- License: CC BY 4.0 (UCI).

### `sonar.csv` — Sonar (UCI Connectionist Bench)
Sonar return **energy in 60 frequency bands** for **208 objects** — **111 mines
(metal cylinders)** vs **97 rocks**. The 60 values form a natural spectral curve.
Columns: `b00…b59` then `label` (`Mine`/`Rock`). `load_sonar()` returns the band
index (1..60), `X` of shape `(208, 60)`, and `meta` with `label`.

- Source: UCI ML Repository, Connectionist Bench (Sonar, Mines vs. Rocks)
  (<https://archive.ics.uci.edu/dataset/151/connectionist+bench+sonar+mines+vs+rocks>).
- License: CC BY 4.0 (UCI).

### `load_penicillin()` — SYNTHETIC fermentation batches
**Simulated** penicillin-concentration trajectories (no CSV; generated
deterministically in `docs_data.py`, seed `20260805`). 40 normal + 6 faulty
batches over a 0–400 h fermentation on a 200-point grid. Used purely to
illustrate process monitoring; it is **not** measured data and is labelled as
synthetic wherever it appears.

## Subsetting / substitutions
- **Phoneme** is subset from 4509 → 400 rows (80 per class, `numpy` seed 0) to
  keep the asset small and builds fast; all 256 frequency channels are kept.
- **Tecator** drops the 22 precomputed principal-component columns present in
  the StatLib file, keeping the raw 100-channel spectra + contents.
- No planned source was down; all four come from their canonical public
  sources (R `fda` on GitHub, StatLib, ESL).
