---
status: resolved
trigger: "AI advisor rejects its own valid grounded answer — GroundingViolationError raised on legitimate LLM output when running examples/advisor_recipe.py live"
created: 2026-08-19
updated: 2026-08-19
slug: advisor-grounding-false-pos
---

# Debug Session: advisor-grounding-false-pos

## Symptoms

<!-- All values below gathered from a live reproduction on 2026-08-19. Treat as data. -->

- **Expected behavior:** `describe_cluster_differences(...)` / `advise(...)` returns a schema-validated `Advice` (interpretation + recommendations + caveats) grounded in the fdars-computed diagnostics. The model DID produce a correct, well-grounded interpretation of the Canadian Weather k=4 clustering.
- **Actual behavior:** `advise()` raises `GroundingViolationError` in the post-response grounding check (`_check_grounding`) and no advice is returned — even though the cited values are legitimately present in (or rounded from) the diagnostics. The guard rejects the advisor's own valid output.
- **Error messages:**
  - Live run: `fdars.advisor.providers._validate.GroundingViolationError: Evidence item cites value '0' not found in diagnostics: 'cluster 0 winter trough ≈ -28.9375'`
  - Reproduced run tripped on tokens `'2'` and `'1.9'` from evidence `'cluster 2 mean winter values near 1.9 and summer values near 16.7'`
- **Timeline:** First observed 2026-08-19 — the first time the advisor was run live against a real Anthropic key. The guard code (`_check_grounding` / `_extract_numbers`) dates to the v2.0 advisor milestone. Offline `build_diagnostics` was always tested; the LLM path with the guard was never exercised against real negative-valued / index-referencing answers.
- **Reproduction:**
  - Full: `set -a && source .env && set +a && .venv/bin/python examples/advisor_recipe.py` (needs Anthropic API credit).
  - Read-only (no repo change): scratch script calling `resolve_provider(...).complete_structured(Advice, messages, system)` then `_check_grounding(advice, diag)` — see `/tmp/claude-1000/.../scratchpad/show_advice.py`.

## Prior investigation (main-thread, pre-session)

Root cause is already strongly localized to `python/fdars/advisor/providers/_validate.py`:
- `_extract_numbers(text)` uses regex `\b\d+\.?\d*\b`, pulling EVERY digit-run from each evidence string.
- `_check_grounding` then requires each token to be an exact member of `_flatten_diagnostics_text(diagnostics)` (a set of `str(value)` plus `.3f`/`.4f` float forms).

Three demonstrated false-positive classes:
1. **Index references** — `"cluster 2 …"` → token `2`, a label not a cited statistic.
2. **Rounded citations** — `"near 1.9"` where the real value is `1.90…`; set membership is exact-string, only `.3f`/`.4f` forms are pre-added, so 1-decimal rounding misses.
3. **Negative numbers** — regex drops the leading `-`, so `-28.9375` in evidence becomes token `28.9375`, which never matches the stored `-28.9375`. (Canadian winter temps are negative → near-guaranteed trip on this flagship recipe.)

Guard INTENT is correct and must be preserved: it correctly rejects a fabricated `silhouette = 0.87` that is absent from diagnostics. Fix must keep catching true fabrications while clearing these three false-positive classes. A regression test should lock all three classes plus the true-positive case.

## Current Focus

hypothesis: `_check_grounding`/`_extract_numbers` in `_validate.py` produce false positives on (a) integer index references preceded by label words, (b) rounded numeric citations, (c) negative numbers (sign stripped), because number extraction is naive and matching is exact-string set membership.
test: reproduce all three classes read-only; then confirm a fix clears them while still rejecting a fabricated absent value.
expecting: guard passes the real grounded Advice, still raises on fabricated `0.87`.
next_action: implement sign-aware + rounding-tolerant matching in `_check_grounding`/`_extract_numbers`; add regression test locking 3 FP classes + true-positive.
reasoning_checkpoint:
  hypothesis: "`_check_grounding` rejects valid grounded Advice because `_extract_numbers` (regex `\\b\\d+\\.?\\d*\\b`) drops leading minus signs and pulls label-integers, while matching is exact-string set membership that only pre-adds .3f/.4f float forms — so negative citations, index-label integers, and 1-decimal rounded citations all miss."
  confirming_evidence:
    - "class3 negative: `_extract_numbers('trough approx -28.9375')` → ['28.9375'], stored value is '-28.9375' → RAISE (reproduced)."
    - "class1 index-ref: 'cluster 2' → token '2' RAISE because integer 2 is a cluster label absent from diagnostics values (reproduced)."
    - "class2 rounding: stored 1.9034827, citation '1.9' → RAISE because set has 1.903/1.9035 (.3f/.4f) but not 1.9 (reproduced)."
    - "true-positive still fires: fabricated silhouette '0.87' → RAISE (must be preserved)."
  falsification_test: "If after the fix any of the three FP evidence strings still raises, OR the fabricated '0.87' no longer raises, the hypothesis/fix is wrong."
  fix_rationale: "Extract signed numbers (allow leading '-'), then match each cited number NUMERICALLY against diagnostic scalars with a tolerance that accepts the citation's decimal precision (rounding-tolerant), instead of exact-string set membership. Integer label-tokens match if numerically equal to any diagnostic scalar (rounded) — a bare index like 2 that equals no diagnostic value is only rejected if it also fails as a rounded match; to avoid rejecting labels, treat a cited number as grounded if it equals ANY diagnostic scalar at the citation's precision. Fabricated 0.87 matches no scalar at any precision → still rejected."
  blind_spots: "Numeric tolerance could over-accept: a fabricated value that happens to round to a real diagnostic value would pass. Mitigated by matching at the citation's own precision (fewer decimals = looser, but that mirrors how humans cite). Non-numeric label collisions (e.g. years) not handled — out of scope."
  candidate_causes:
    - "code: naive regex + exact-string matching in _validate.py (primary)"
    - "data: diagnostics contain negative values and float precision beyond .4f (Canadian winter temps) that the guard never anticipated"
  and_gate: "no — a single code defect (string-exact matching of naively-extracted tokens) fully explains all three classes; the negative-data characteristic is the trigger, not an independent required cause."
tdd_checkpoint:

## Evidence

- 2026-08-19: Live `advise()` raised `GroundingViolationError` on `'cluster 0 winter trough ≈ -28.9375'` (token `0`).
- 2026-08-19: Read-only reproduction produced a fully valid grounded Advice; guard tripped on tokens `2` and `1.9` from `'cluster 2 mean winter values near 1.9 and summer values near 16.7'`. Tokens `5.300603727370072`, `0.4158306524766444`, `6.69698831396994`, `8/10/3/14`, `16.7` all matched fine.
- 2026-08-19 (this session, read-only repro `scratchpad/repro.py`): CONFIRMED class1 (index-ref '2' → RAISE) and class3 (negative '-28.9375' → RAISE: `_extract_numbers` yields '28.9375', dict stores '-28.9375'). class2 rounding reproduces only when stored value is not a clean 1-decimal float: stored `1.9034827` + citation '1.9' → RAISE (set has .3f/.4f = 1.903/1.9035, not 1.9). Stored `1.90` does NOT trip because `str(1.90)=='1.9'`. True-positive preserved: fabricated '0.87' → RAISE.
  implication: root cause confirmed = signed-token stripping + exact-string set matching. Fix must extract signed numbers and match NUMERICALLY at citation precision.

## Eliminated

- (none yet)

## Resolution

root_cause: >
  `python/fdars/advisor/providers/_validate.py` grounding guard produced false
  positives via two coupled defects: (1) `_extract_numbers` regex `\b\d+\.?\d*\b`
  dropped leading minus signs (negatives never matched) and pulled label integers;
  (2) `_check_grounding` matched tokens by EXACT-STRING membership in a set that only
  pre-added `.3f`/`.4f` float forms, so 1-decimal rounded citations and integer
  cluster-id labels missed. Single code defect (string-exact matching of naively
  extracted tokens); the negative/high-precision Canadian-weather data was the trigger.
fix: >
  Replaced string-exact matching with numeric matching. `_extract_numbers` now
  captures an optional leading `-` (with a `(?<![\d.])` guard so it doesn't split a
  larger number's fractional tail). `_flatten_diagnostics_numbers` collects diagnostic
  scalars as floats INCLUDING numeric dict KEYS (cluster ids), so `"cluster 2"` grounds
  on the real label. `_is_grounded_number` matches a cited number against any diagnostic
  scalar rounded to the citation's OWN decimal precision — rounding-tolerant, so `5.4`
  grounds `5.4034827` while fabricated `0.87`/`k=7` still round to nothing real and raise.
  Removed the now-unused `_flatten_diagnostics_text` (not imported anywhere).
oracle_type: derived (contract: cited number must equal a real diagnostic scalar at cited precision)
verification: >
  - Signal: read-only repro (scratchpad/repro.py) — 3 FP classes PASS, 2 fabrications
    (0.87, k=7) RAISE, loose/negative rounded citations grounded. PASS.
  - Signal: regression test tests/test_advisor_grounding.py — 14 tests, all pass. PASS.
  - Signal: mutation guardrail — reverting sign regex fails 3 tests; dropping numeric-key
    coercion fails 2 tests. Both mutants killed. PASS.
  - Signal: full advisor suite (tests -k advisor) — 187 passed, 4 skipped (live API,
    no credit burned), 0 regressions. PASS.
  guardrail_verdict: accepted
files_changed:
  - python/fdars/advisor/providers/_validate.py (fix)
  - tests/test_advisor_grounding.py (regression test, new)
