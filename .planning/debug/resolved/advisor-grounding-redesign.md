---
status: resolved
trigger: "Advisor grounding guard has a DESIGN flaw: _extract_numbers pulls digits from the whole evidence free-text, including identifier names (t2, q90, q10, field[i]). Two prior patches (d427da5, fec531e) treated symptoms; a third class (digits-in-field-names) surfaced on depth + spm. Redesign to value-position extraction."
created: 2026-08-20
updated: 2026-08-20
slug: advisor-grounding-redesign
---

# Debug Session: advisor-grounding-redesign

## Symptoms

<!-- Gathered from live/read-only advisor runs across 6 aspects on 2026-08-19/20. Treat as data. -->

- **Expected behavior:** `advise(diag, aspect=..., ...)` returns a schema-validated `Advice` whenever the model's evidence cites values that are genuinely present in the diagnostics. The grounding guard should reject ONLY fabricated numbers.
- **Actual behavior:** The guard raises `GroundingViolationError` on legitimate grounded answers whenever an evidence string contains a digit that is part of an IDENTIFIER rather than the cited value. Confirmed on the `depth` and `spm` aspects.
- **Error messages (latest):**
  - Depth: `GroundingViolationError: Evidence item cites value '90' not found in diagnostics: 'depth_q90=0.7845009784735811'` (also `'10'` from `depth_q10`).
  - SPM: `GroundingViolationError: Evidence item cites value '2' not found in diagnostics: 't2_max: 22.451286505855457'` (the `2` in Hotelling **T2** field names `t2_max`/`t2_limit`/`t2_mean`).
- **Timeline:** Two prior fixes on the SAME guard: `d427da5` (negatives, 1-decimal rounding, dict-key index integers) and `fec531e` (array subscripts `field[2]`, scientific notation `5.22e-05`). Each patched a symptom; the underlying design — regex over the WHOLE evidence string requiring every digit-run to equal a diagnostic value — keeps leaking because this domain's field names embed digits.
- **Reproduction (read-only, no API credit needed for the guard logic):** construct any `Advice` whose evidence cites `t2_max=...`, `depth_q90=...`, or `field[2]=...`, then call `_check_grounding(advice, diag)`. Live end-to-end repro via `scratchpad/batch2.py` (depth + spm trip; regression passes clean).

## Root cause (design-level) — one general class

Guard: `python/fdars/advisor/providers/_validate.py` — `_extract_numbers`, `_is_grounded_number`, `_flatten_diagnostics_numbers`, `_check_grounding`.

`_extract_numbers(text)` pulls every numeric token from the ENTIRE evidence string and `_check_grounding` requires each to match a diagnostic scalar. But evidence strings are `identifier = value` / `identifier: value` / `identifier[i] = value` citations, and the IDENTIFIER routinely contains digits that are not cited values:

- `t2_max`, `t2_limit`, `t2_mean` → spurious `2` (Hotelling T²)
- `depth_q90`, `depth_q10` → spurious `90`, `10` (quantile labels)
- `field[2]` → spurious `2` (positional index; patched in fec531e by stripping `[\d+]`)
- `cluster 2` → spurious `2` (patched in d427da5 by grounding dict-key ints)
- domain is full of such names: `arl0`, `chi2`, `spe`, `_1d`/`_2d` suffixes, `fpca`/`pc1` component labels, `significant_at_0.05`.

The two prior patches (dict-key grounding; subscript stripping) are band-aids for special cases of ONE general problem: **numbers that belong to identifiers, not values, are being validated as if they were cited values.**

## Fix direction — value-position extraction (redesign)

Parse each evidence string as an `identifier <sep> value` citation and ground ONLY the value portion:
- Split on the FIRST `=` or `:` (the value is on the right). If no separator, treat the whole string as free-text and extract only standalone numeric literals not attached to a leading identifier.
- Alternative / complementary: before extraction, strip identifier tokens — any run matching `[A-Za-z_]\w*` (starts with a letter/underscore) removes `t2`, `q90`, `depth_q10`, `field` etc. A pure numeric literal (`0.87`, `-28.9`, `5.22e-05`) never starts with a letter, so it survives; `e`-notation must be matched as one token FIRST so the `e` isn't treated as an identifier start.
- Keep the value-matching logic from the prior fixes intact: signed numbers, rounding tolerance at citation precision, scientific-notation via relative tolerance.

Prefer the approach that most cleanly eliminates the whole digits-in-identifier category while keeping the existing 28 tests green. The debugger should choose and justify between (a) value-position split and (b) identifier-token stripping (or a combination), whichever is simplest and most robust.

## HARD CONSTRAINTS

- Preserve BOTH prior fixes: do NOT regress the existing 28 tests in `tests/test_advisor_grounding.py` (negatives, rounding, dict-key indices, array subscripts, scientific notation).
- Still reject genuine fabrications — these MUST still raise: `silhouette = 0.87`, `k=7`, fabricated `9.99e-05`, and a fabricated value inside a value position (e.g. `t2_max = 999.9` when no diagnostic equals 999.9). Add an explicit test that a fabricated VALUE (right of `=`) is still caught even though the identifier is legitimate — this proves value-position extraction didn't blind the guard.
- Extend `tests/test_advisor_grounding.py` with regression tests for the digits-in-field-names class (`t2_*`, `depth_q90`, `depth_q10`) plus the fabricated-value-in-value-position case.
- Verify via `pytest -k advisor`, NOT by burning API credit. A read-only harness constructing Advice objects is the correct test vehicle.

## Current Focus

hypothesis: The guard false-positives on any evidence whose IDENTIFIER contains digits, because `_extract_numbers` extracts from the whole string and `_check_grounding` validates identifier-digits as if cited values. The two prior patches only special-cased dict-key ints and array subscripts. Fix = ground only the VALUE portion of each `identifier<sep>value` citation.
test: read-only reproduce `t2_max=..`, `depth_q90=..`; confirm redesign passes them AND still raises on a fabricated value-position number and on `0.87`/`k=7`; keep 28 existing tests green.
expecting: after redesign, live depth + spm `advise()` return Advice with no GroundingViolationError; fabrications still raise.
next_action: apply lookbehind widening to _NUMBER_RE in _validate.py; extend tests; run pytest -k advisor.
reasoning_checkpoint:
  hypothesis: "The guard false-positives because _NUMBER_RE extracts any digit-run whose only guard is a lookbehind of (?<![\\d.]) — which blocks gluing to a preceding digit/dot but NOT to a preceding letter/underscore. So digit-runs embedded in identifiers (t2, depth_q90, depth_q10) are extracted and validated as cited values. Root cause: the extraction lookbehind does not treat identifier characters (letters, underscore) as 'part of a name, not a value'."
  confirming_evidence:
    - "Prototype: widening lookbehind to (?<![A-Za-z0-9_.]) makes depth_q90=.. -> ['0.7845...'], t2_max: 22.45 -> ['22.45...'], while cluster 2 -> ['2','5.4'] and k=7 -> ['7'] survive (space/= before them)."
    - "All 17 prototype cases pass including every existing-test citation (negatives, subscripts, sci-notation) AND all new digits-in-identifier cases AND the fabricated-value case t2_max=999.9 -> ['999.9']."
    - "Debug file evidence: depth trips on depth_q90->'90'/depth_q10->'10'; spm trips on t2_*->'2'; regression (no digit field names) passes clean — exactly the digits-in-identifier signature."
  falsification_test: "If widening the lookbehind blinded the guard to any real cited value, a fabricated value in value position (t2_max = 999.9) would stop raising, OR an existing green test (0.87, k=7, 9.99e-05, subscript, sci-notation, negative) would flip. Running pytest -k advisor must stay green AND the new fabricated-value-position test must raise."
  fix_rationale: "Widening the extraction lookbehind is the single-point realization of identifier-token stripping (approach b): a numeric literal is extracted only when its first char is not glued to an identifier char. This subsumes both prior band-aids (subscript strip still applies; cluster-N numeric-key path unaffected since standalone N survives) and eliminates the WHOLE digits-in-identifier class rather than another special case. Value-matching logic (_is_grounded_number, sci-notation rel-tol, rounding) is untouched, so fabrications still raise."
  blind_spots: "A number glued to the RIGHT of an identifier with no separator and no space, e.g. 'abc123' (letters then digits) — '123' would now be rejected. This is correct for identifier-embedded digits but could in theory drop a legitimately-glued value; no such citation pattern exists in the diagnostics domain (values are always separated by =, :, or whitespace). Also: a value immediately following a '.' e.g. 'v1.5' — but the existing (?<![.]) already handled that and remains."
  candidate_causes:
    - "code: _NUMBER_RE lookbehind too narrow — does not exclude identifier chars (letter/underscore) before a digit-run (PRIMARY, confirmed)."
    - "data: diagnostics field names in depth/spm aspects embed digits (t2_*, depth_q90/q10) — a domain property, not a defect, but the trigger surface. Not fixable in the guard's favor by changing data; the guard must tolerate it."
  and_gate: "no — single root cause (the narrow lookbehind). The digit-embedding field names are a standing domain condition, not a second independent fault: the guard must be robust to them, so the only thing to change is the extraction. One code change fully resolves the class."
tdd_checkpoint:

## Evidence

- 2026-08-20 (read-only `batch2.py`): DEPTH trips on `depth_q90`→'90', `depth_q10`→'10'; SPM trips on `t2_max`/`t2_limit`/`t2_mean`→'2'. REGRESSION (`r_squared=..`, `residual_*`) passes clean — field names there have no embedded digits. Guidance content in all three is correct and grounded; ONLY identifier-digit extraction is the defect.
- 2026-08-20 (prototype): the ONLY change needed is widening `_NUMBER_RE`'s lookbehind from `(?<![\d.])` to `(?<![A-Za-z0-9_.])`. Verified against 17 citation cases — every existing-test citation (negatives, subscripts, sci-notation, cluster/index) AND all new digits-in-identifier cases pass, and the fabricated value-position case `t2_max = 999.9` → `['999.9']` (still checked, still raises).
- 2026-08-20 (pre-fix-regex proof): under the OLD regex, `depth_q90=..`→`['90', '0.7845..']`, `depth_q10=..`→`['10','0.5']`, `t2_max: ..`→`['2','22.45..']`, `arl0=200`→`['0','200']`. The new tests therefore BITE — they fail on the old code, pass on the fix. `t2_max = 999.9` extracts `999.9` under both, confirming value-position extraction did not blind the guard.
- 2026-08-20 (verification): `pytest -k advisor` → 213 passed, 4 skipped, 387 deselected (was 201 passed / 4 skipped before; +12 new tests, zero regressions). `tests/test_advisor_grounding.py` alone → 40 passed (28 existing + 12 new).

## Eliminated

- hypothesis: value-position split on first `=`/`:` (approach a). evidence: many valid citations are in PROSE with no separator (`cluster 2 shows winter mean near 5.4`, `trough is approximately -28.9375`, `the fifth component explains only 5.22e-05`); (a) alone would force a free-text branch that STILL needs identifier-aware extraction, adding branching for no gain. Rejected in favor of the single-lookbehind realization of approach (b). timestamp: 2026-08-20
- hypothesis: separate identifier-stripping pass (`_IDENT_RE.sub`). evidence: a naive `[A-Za-z_]\w*` strip breaks scientific notation — the `e` of `5.22e-05` is a letter start, splitting the token into `5.22` + `-05` (prototyped and observed). The lookbehind approach avoids this entirely by keeping sci-notation matched as one token FIRST. timestamp: 2026-08-20

## Resolution

root_cause: `_NUMBER_RE`'s extraction lookbehind was `(?<![\d.])` — it prevented gluing a numeric literal to a preceding digit or dot, but NOT to a preceding letter or underscore. So digit-runs embedded in identifiers (`t2`→'2', `depth_q90`→'90', `depth_q10`→'10', `arl0`→'0') were extracted and validated by `_check_grounding` as if they were cited values, raising `GroundingViolationError` on legitimately-grounded advice. The two prior patches (dict-key int grounding; array-subscript stripping) were special cases of this one general class: numbers belonging to identifiers, not values, treated as cited values.
fix: Widen the lookbehind on both alternatives of `_NUMBER_RE` to `(?<![A-Za-z0-9_.])`, so a numeric literal is extracted only when its first char is not glued to an identifier char (letter/digit/underscore/dot). This is identifier-token stripping realized as a single guard, with sci-notation still matched as one token first. `_is_grounded_number`, `_flatten_diagnostics_numbers`, and `_SUBSCRIPT_RE` are unchanged; the two prior fixes are subsumed (subscripts still stripped; standalone `cluster 2`→'2' still survives and grounds via the numeric-key path). Docstrings updated to document the sixth (general) cleared class.
verification: guardrail 5/5 — (1) `pytest -k advisor` green 213/4, no regressions; (2) new depth/spm tests bite (fail on old regex, pass on fix); (3) fabrications still raise — `0.87`, `k=7`, `9.99e-05`, and fabricated value-position `999.9`/`0.99`/`77.7`; (4) minimal one-lookbehind diff; (5) eliminates whole class, not a third band-aid. Live end-to-end confirmation PASSED (2026-08-20): real advisor run across depth/regression/spm (`batch2.py`) — DEPTH guard clean (was tripping on depth_q90/depth_q10), REGRESSION clean, SPM clean (was tripping on t2_max/t2_limit/t2_mean).
files_changed:
  - python/fdars/advisor/providers/_validate.py — widen _NUMBER_RE lookbehind; update _extract_numbers / _check_grounding docstrings
  - tests/test_advisor_grounding.py — +12 tests: TestGroundingDigitsInIdentifierCleared (7), TestGroundingFabricatedValueInValuePositionStillRaises (4), plus glued-trailing-digits unit
