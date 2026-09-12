# v14 Phase 90 — Pre-Release Manuscript Audit (scientific-writing skill)

**Re-scoped 2026-09-12** from the former "PROPOSED v15.0" milestone into a v14
close-out step, per user preference to audit **before** releasing. This runs as
part of Phase 90, **before GATE-04 approval and the `v0.13.0` tag** — auditing a
citable artifact before it goes public (arXiv/PyPI) is the safer order and avoids
an arXiv v2 / patched release.

GSD note: v14.0 is the active milestone (`milestone.lock`), so do NOT
`/gsd-new-milestone`. Resume this inside Phase 90 (e.g. `/gsd-resume-work` or
`/gsd-quick`), then close v14 normally.

## Ordering (updated close-out sequence)

1. **This audit** → build registries, run the three CLIs, fix findings, keep CI green.
2. Regenerate the PDF; user reviews the (possibly revised) `paper/_ci_pdf/paper.pdf`.
3. **GATE-04** human approval.
4. REL-01: create annotated tag `v0.13.0`; user runs `git push origin v0.13.0`
   (fires PyPI). Replace CITATION.cff arXiv-URL PLACEHOLDER post-assignment.
5. `/gsd-complete-milestone`.

## Skill (already installed)

`k-dense-ai/scientific-writing` via dhub-cli — global at
`~/.claude/skills/scientific-writing` → `~/.dhub/skills/k-dense-ai/scientific-writing`.
Offline, network-free, stdlib-only; audit grade C = only "unscanned files"; its 9
python CLIs vetted clean. Loadable as `/scientific-writing`. CLI ref:
`references/cli_reference.md` in the skill dir.

## First pass — DONE (this session)

Ran `validate_manifest` + `check_references` over a bib→manifest converter (from
`paper/refs.bib` + `paper/refs_manual.bib`, 52 refs): **no duplicate DOIs/URLs/titles**.
One real finding — uncited `nadaraya_watson_1964` had an empty title — **FIXED**
(title added in `_references_map.json` from its verified notes; `refs.bib`
regenerated; drift gates + CI green, run 34715668228).

## Deeper audit — TODO (the work)

1. **Registries** under `paper/audit/` (commit them for reproducibility):
   - `source_manifest.json` — E-IDs from the bib (re-derive the converter; the
     draft double-brace-misparsed `{{...}}` titles — fix that).
   - `claims.csv` — headers `claim_id,section,claim_kind,claim_text_sha256,`
     `evidence_ids,verification_status,uncertainty,analysis_intent`. Extract the
     paper's factual/numeric claims (coverage counts; tour numbers — R²/RMSE, CV,
     cluster sizes, MUOD counts, FPCA var%, DTW, PM10 RMSE, dataset shapes; case
     studies) and bind each to its live source (script output / dataset / cited paper).
   - `consistency_manifest.json` — repeated numeric facts + method↔result maps.
2. Run `audit_claims.py manuscript.md claims.csv source_manifest.json`
   (needs a Markdown rendering of the paper — numeric content lacking a claim
   marker is flagged), `check_consistency.py consistency_manifest.json`
   (same number stated differently across §4 / case studies / captions / abstract),
   and `lint_manuscript.py manuscript.md` (placeholder/language lint).
3. Fix real findings; keep `paper.yml` CI green (tectonic + real-pdflatex arxiv,
   drift gates, 0 overfull>20pt). Honor the skill's **no-fabrication** rule.
4. Optionally wire a lightweight subset into `make paper-check`.

See memory `deeper-manuscript-audit-backlog` and `v14-milestone-state`.
