---
status: resolved
trigger: "AI advisor grounding guard STILL rejects valid grounded answers — two more false-positive classes surfaced by FPCA on Tecator NIR spectra (array subscripts + scientific notation), not covered by the first fix (commit d427da5)"
created: 2026-08-19
updated: 2026-08-19
slug: advisor-grounding-fp-part2
---

# Debug Session: advisor-grounding-fp-part2

## Symptoms

<!-- Gathered from a live FPCA run on 2026-08-19, AFTER the first grounding fix (d427da5) landed. Treat as data. -->

- **Expected behavior:** `advise(diag, aspect="fpca", ...)` returns a schema-validated `Advice` for an FPCA result. The model produced excellent, correct component-count guidance (retain 3–4 comps, PC1=98.62% baseline, don't select on variance alone) with evidence citing values that ARE present in the diagnostics.
- **Actual behavior:** `advise()` still raises `GroundingViolationError`, because the model cited grounded values using two notations the first fix did not anticipate.
- **Error message:** `fdars.advisor.providers._validate.GroundingViolationError: Evidence item cites value '2' not found in diagnostics: 'cumulative_variance_explained[2]=0.9986859982552292'`
- **Timeline:** First grounding fix `d427da5` (this same session lineage, earlier today) fixed negatives / 1-decimal rounding / dict-key index integers. These TWO NEW classes were surfaced 2026-08-19 by the first real FPCA/spectroscopy example (Tecator NIR, `regression.fpca(X, wl, n_comp=10)`), whose diagnostics use list-valued fields (`cumulative_variance_explained`, `explained_variance_ratio`, `eigenvalues`) and very small numbers in scientific notation. The flagship clustering/inference examples never exercised either notation.
- **Reproduction:**
  - `regression.fpca(X, wl, n_comp=10)` on `datasets.load_tecator()` → `build_diagnostics(result, method="fpca")` → `advise(diag, task="interpretation", aspect="fpca", domain_context=...)`.
  - Read-only token analysis via `_extract_numbers` + `_flatten_diagnostics_numbers` + `_is_grounded_number` (scratchpad `fpca_show.py`).

## Prior investigation (main-thread, pre-session) — two NEW false-positive classes

Guard code: `python/fdars/advisor/providers/_validate.py` (`_extract_numbers`, `_is_grounded_number`, `_flatten_diagnostics_numbers`, `_check_grounding`) — as rewritten by commit `d427da5`.

Read-only token analysis of the live FPCA advice showed these tokens TRIP the current guard:

| Class | Evidence string | Bad token(s) | Why it is a false positive |
|---|---|---|---|
| **4. Array subscript index** | `cumulative_variance_explained[2]=0.9986859982552292` | `2`, `3`, `4` | `[2]` is a positional list index, not a cited value. The value `0.9987` IS grounded; only the subscript trips. First fix grounded dict-key indices, NOT positional list subscripts. |
| **5. Scientific notation** | `explained_variance_ratio[4]=5.2269939358072166e-05` | `5.2269939358072166` and `-05` | `_extract_numbers` regex splits `5.22…e-05` into mantissa + exponent; neither equals the true float `5.22e-05`, which IS in the diagnostics. |

Both notations cite values that are genuinely present in the diagnostics lists — the guard's number extraction/matching simply doesn't understand them.

**Diagnostics dict actually returned (for reference):**
`{method: fpca, n_components: 10, n_obs: 240, eigenvalues:[52.91, 0.4685, ...], explained_variance_ratio:[0.9862, 0.0087, 0.0038, 0.0012, 5.22e-05, ...], cumulative_variance_explained:[0.9862, 0.9949, 0.9987, 0.9999, 1.0, ...], total_variance: 53.653, phase_leakage_indicator: 0.01384, phase_leakage_flagged: False}`

**Constraint — preserve prior behavior & intent:** The guard must still (a) reject genuine fabrications (`silhouette = 0.87`, `k=7`) — the true-positive case; and (b) keep passing the three classes fixed in `d427da5` (negatives, 1-decimal rounding, dict-key index integers) — do NOT regress `tests/test_advisor_grounding.py` (14 tests). Extend that same test file with the two new classes.

**Fix direction (candidate):**
1. **Scientific notation** — extend the number regex to match `\d*\.?\d+[eE][+-]?\d+` as a SINGLE token (before the plain-decimal alternative), so `5.22e-05` is parsed whole and compared numerically.
2. **Array subscripts** — strip / ignore integer tokens occurring in subscript position `identifier[ int ]` (treat as positional references, not cited values). Simplest robust approach: remove `\[\s*\d+\s*\]` substrings from each evidence string BEFORE number extraction, OR skip a bare integer token whose immediately-surrounding characters are `[` … `]`. Alternatively ground a subscript integer if it is a valid index (0 ≤ i < len) of the referenced list field — but the strip approach is simpler and lower-risk.

## Current Focus

hypothesis: The `d427da5` guard still false-positives on (4) positional array subscripts `field[i]` (integer index read as a cited value) and (5) scientific-notation floats (`_extract_numbers` splits mantissa/exponent so the real value never matches), because number extraction neither understands `e` notation nor distinguishes subscript indices from cited values.
test: read-only reproduce both classes on the Tecator FPCA advice; confirm a fix passes both while still rejecting fabricated `0.87`/`k=7` and keeping all 14 existing grounding tests green.
expecting: after fix, `advise()` on the Tecator FPCA diagnostics returns Advice without raising; fabricated values still raise.
next_action: apply fix to _extract_numbers (strip subscripts + sci-notation single-token) and _is_grounded_number (relative-tolerance path for sci-notation); extend tests; run pytest -k advisor.
reasoning_checkpoint:
  hypothesis: "The d427da5 guard false-positives on (4) positional subscripts `field[i]` — the integer index is extracted as a cited value — and (5) scientific-notation floats, which fail at TWO points: `_extract_numbers` splits `5.22e-05` into mantissa+exponent, AND even a whole sci token would misfire in `_is_grounded_number` because its decimal-place string-count yields decimals=20 (counting mantissa digits + exponent chars) instead of a meaningful precision."
  confirming_evidence:
    - "Live regex reproduction: `[2]` yields spurious token '2'; `5.2269939358072166e-05` yields ['5.2269939358072166','-05'] — neither equals the true float."
    - "_is_grounded_number trace: token '5.2269939358072166e-05' → decimals computed as 20 → round(value,20) != round(diag,20) even when floats are equal, so sci tokens never match via the plain-decimal path."
  falsification_test: "If, after the fix, `_extract_numbers('field[4]=5.22e-05')` returned anything other than ['5.22e-05'], or a fabricated '9.99e-05' grounded, the hypothesis/fix would be wrong."
  fix_rationale: "Root cause is number extraction+matching not understanding two notations. (1) strip `\\[\\s*\\d+\\s*\\]` before extraction removes positional indices at the source (they are references, not values). (2) match sci-notation `\\d*\\.?\\d+[eE][+-]?\\d+` as ONE token, ordered before the plain-decimal alt. (3) route sci tokens through a relative-tolerance comparison keyed off mantissa precision, because decimal-place counting is meaningless for `e` notation. Each change addresses a mechanism, not a symptom."
  blind_spots: "Positive exponents (5.22e+05) and bare sci citations without subscript; a subscript larger than 9 (multi-digit index) — regex \\d+ handles these. Not testing: sci notation without a decimal point (e.g. '5e-05') — added to test matrix."
  candidate_causes:
    - "code: _extract_numbers regex lacks sci-notation alternative and treats subscript integers as values"
    - "code: _is_grounded_number decimal-precision logic is undefined for sci-notation tokens (string-count over-counts)"
    - "data: FPCA diagnostics are the first to use list-valued fields (subscript notation) and sub-1e-4 magnitudes (sci notation) — the flagship examples never exercised either, so the gap was latent"
  and_gate: "yes — the FPCA false positive requires BOTH a code gap (extraction/matching notation-blind) AND the data shape (list fields + tiny magnitudes) to co-occur; clustering data had neither notation so the code gap stayed dormant. Both new classes are independent code gaps that must each be fixed (subscript strip AND sci-notation extract+match), so root_cause is a set."
tdd_checkpoint:

## Evidence

- 2026-08-19 (read-only `fpca_show.py`): The live FPCA Advice is valid and grounded; guard token analysis shows TRIPS on `2`/`3`/`4` (from `field[2]`/`[3]`/`[4]` subscripts) and on `5.2269939358072166` + `-05` (from `...=5.2269939358072166e-05`). All plain-decimal citations (0.9862, 52.91, 53.65, etc.) grounded fine — confirming ONLY subscripts + sci-notation are the gap.

## Eliminated

- (none yet)

## Resolution

root_cause: >
  TWO independent code gaps in the d427da5 grounding guard, latent until the first
  FPCA example produced list-valued diagnostics + sub-1e-4 magnitudes (AND-gate: code
  gap × data shape). (a) `_extract_numbers` treats a positional array subscript
  `field[2]` integer as a cited value; (b) `_extract_numbers` splits sci-notation
  `5.22e-05` into mantissa+exponent, AND `_is_grounded_number` has no meaningful
  precision path for sci-notation (its decimal-place string-count yields ~20, so even
  a whole sci token never matches its true diagnostic float).
fix: >
  _validate.py: (1) strip `\[\s*\d+\s*\]` subscripts before number extraction;
  (2) add a scientific-notation alternative `\d*\.?\d+[eE][+-]?\d+` ordered BEFORE the
  plain-decimal alternative so sci floats parse as one token; (3) route sci-notation
  tokens in `_is_grounded_number` through a relative-tolerance comparison
  (math.isclose, rel_tol = one unit in the last mantissa decimal place) instead of the
  decimal-place rounding used for plain decimals.
verification: >
  pytest tests/test_advisor_grounding.py — 28 passed (14 original preserved + 14 new).
  pytest -k advisor — 201 passed, 4 skipped (API-only), 0 failed. Revert-test: with
  _validate.py reverted, 9 of the new tests fail (both reported classes); restoring the
  fix makes them pass — confirms causality. No Anthropic API credit used during
  investigation. Live end-to-end confirmation (user-run, 2026-08-19): real Tecator FPCA
  advise() returned a full Advice with NO GroundingViolationError; evidence citations
  included both previously-failing notations — cumulative_variance_explained[2]=0.9986…
  (array subscript) and explained_variance_ratio[4]=5.2269939358072166e-05 (scientific
  notation) — now grounded cleanly.
oracle_type: derived  # contract: cited value must equal a diagnostic scalar within its stated precision
files_changed:
  - python/fdars/advisor/providers/_validate.py
  - tests/test_advisor_grounding.py
