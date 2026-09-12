# Pre-release manuscript audit (v14.0 Phase 90)

Offline, network-free audit of the fdars software paper run **before** GATE-04
and the `v0.13.0` release, using the `k-dense-ai/scientific-writing` skill
(stdlib-only CLIs). See `.planning/phases/90-close-gate-citable-release/PRE-RELEASE-AUDIT-HANDOFF.md`.

## Registries (reproducibility artifacts)

| File | What |
|------|------|
| `manuscript.md` | `pandoc paper.tex -o audit/manuscript.md --wrap=none`, run from `paper/`. All `\input` sections + coverage macros expand; TikZ figures dropped (not text-auditable); `\_` in code identifiers collapses (markdown-only artifact, PDF unaffected). |
| `source_manifest.json` | 53 E-IDs (52 from `refs.bib`+`refs_manual.bib`, plus `E100` fdars self-source). |
| `_keymap.json` | cite-key → E-ID helper map. |
| `consistency_manifest.json` | 55 repeated numeric facts + method↔result maps. |
| `claims.csv` | 32-claim inventory, each bound to a live source (script output / dataset / cited E-ID). |

## Regenerate

```bash
cd paper && pandoc paper.tex -o audit/manuscript.md --wrap=none
SW=~/.claude/skills/scientific-writing/scripts
python3 $SW/validate_manifest.py paper/audit/source_manifest.json --kind source
python3 $SW/check_references.py   paper/audit/source_manifest.json
python3 $SW/check_consistency.py  paper/audit/consistency_manifest.json
python3 $SW/audit_claims.py       paper/audit/manuscript.md paper/audit/claims.csv paper/audit/source_manifest.json
python3 $SW/lint_manuscript.py    paper/audit/manuscript.md
```

## Results (this pass)

- `validate_manifest` / `check_references` / `check_consistency` / `lint_manuscript` → **exit 0**.
  No cross-section value/unit/sample-size mismatches; no DOI/URL/title duplicates.
- `audit_claims` exits 1 = **all noise**: the paper uses no inline `[claim:]/[evidence:]`
  markers, so every number flags `UNTAGGED_NUMERIC_CONTENT`; sources are honestly marked
  `unverified` (no source-opening pass in an offline audit). The deliverable is the claim
  inventory, not a green exit.
- Live spot-check: every headline number reproduces exactly against `paper/code/` script
  output (phoneme CV 0.863; tecator train R² 0.974 / CV R² 0.928; PM10 RMSE 13.68/15.52/17.17;
  wine 0.697/0.759/0.916/0.961) and coverage macros match live introspection. No number was
  unbindable to a live source.

## Findings acted on

1. **[fixed] `design.tex`** — stated `fdars-core 0.14.0 is the minimum required version
   declared in Cargo.toml`; `Cargo.toml` pins `0.33.0`. Corrected to `0.33.0`.
2. **[fixed] `refs.bib`** — `dabo_gijbels_2010` (a `curated:false` stub with empty
   title/authors/year) emitted a malformed `@misc` carrying only a `note`. `gen_refs_bib.py`
   now skips empty-payload records; the entry is dropped (46 entries). It was never `\cite`d,
   so it never rendered in the compiled bibliography.

Not acted on (no fabrication): missing DOIs on foundational/manual refs
(`nadaraya_watson_1964`, the four JSS/JMLR/JASA manual entries) — a citation-completeness
nicety tracked under the deferred `REF-FUT-01` curation pass, not a correctness issue.
