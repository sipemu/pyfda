---
type: quick
slug: paper-review-fixes
status: complete
created: 2026-09-24
completed: 2026-09-24
---

# Summary: pre-arXiv referee-style review fixes (all 11 items)

Fixes from a full referee-style re-read of the fdars paper, each verified against code or source:

1. FTSM described as VAR -> corrected to independent univariate AR per score (Yule-Walker, AIC), per fdars-core src/fts/forecast.rs.
2. Abstract overclaims (provenance "each callable", "full" sklearn, "without hallucinating", "absent from existing") rewritten; coverage 28/437 stated.
3. Misattributed citations replaced with Crossref/arXiv-verified refs (FDApy->Golovkine 2021; k-means->Tarpey & Kinateder 2003; MUOD->Azcorra et al. 2018; FoF->Yao, Mueller & Wang 2005 AoS; LQD/Frechet keys swapped; PLS cite removed from FPC-LDA/FPC regression/LDA; Reiss & Ogden 2007 for FPCR/FPLS).
4. Bibliography: venues from Crossref (fetch_bib_venues.py -> bib_venues.json), gen_refs_bib emits @article/@book/@inproceedings; stray "Type: journal." removed.
5. Inconsistencies fixed (CS1 classifier, to_pc n_comp, "stateless", Gemini provider, "30 method families").
6. Comparison reframed: specialised packages cited; density/Frechet row narrowed (metric distances exist in scikit-fda / fda.usc); evidence + gate updated.
7. New cross-implementation agreement table vs fda.usc/roahd/fdasrvf/fdapace (crossimpl_ref.R frozen refs + crossimpl.py live, CI drift gate). Found: fda.usc metric.lp = trapezoid; fdars rule exact for quadratics.
8. Case Study 4 wine replaced by Berkeley growth sex classification (nested CV 0.970 vs final-height baseline 0.862).
9. Case Study 2 reframed: registration destroys NIR signal (CV R2 0.916 -> -0.017); honest raw baseline (CV 0.916 vs 0.928).
10. Advisor: guard described accurately (numeric-citation check in advise; Goodhart guard in auto_tune); evaluation-and-limits subsection.
11. Limitations section; validation facts (fdars-core 3,260 tests; binding crate has no Rust tests; 5,700 Python tests); CS3 rolling-origin (30 origins); dataset citations; 11pt; case-study floats [tbp].

Library fix: fdars.sklearn now re-exports the 28 estimators (documented import path was broken) + test.
