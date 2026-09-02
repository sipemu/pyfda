# Phase 61: SVG Corrections — learn / represent / align - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning
**Mode:** Audit-driven (the 60-AUDIT.md worklist is the spec)

<domain>
## Phase Boundary

Correct the 24 concept diagrams in the learn/ + represent/ + align/ buckets on the defect, accessibility, and STYLE_SPEC axes, per the ranked worklist in `.planning/phases/60-diagram-quality-audit/60-AUDIT.md` (§1 concept scoring table + §5 Phase-61 worklist). Delivers requirements DEFECT-01, DEFECT-02, DEFECT-03, A11Y-01, A11Y-02, SPEC-01 for THIS bucket only. Cards/thumbs sync (SYNC) and new coverage (COVER) are Phase 64; STYLE_SPEC.md refresh + whole-site --strict gate + human review are Phase 65 — NOT this phase.

**The 24 diagrams (all in `docs/assets/diagrams/`):**
- learn (6): introduction, custom-plotting, simulation, smoothing, derivatives, irregular-sampling
- represent (10): fpca, elastic-fpca, basis-representation, andrews-transformation, depth-functions, streaming-depth, distance-metrics, pace-fpca, imputation, interpolation-policy
- align (8): elastic-alignment, advanced-alignment, landmark-registration, tsrvf, alignment-comparison, shape-analysis, banded-alignment, shift-registration

</domain>

<decisions>
## Implementation Decisions

### Accessibility (A11Y-01, A11Y-02) — applies to every diagram in the bucket
- **A11Y-02:** add a long-form `<title>` + `<desc>` to each complex/multi-panel diagram and wire them with `aria-labelledby="<titleId> <descId>"` on the root `<svg>`. `<title>` = concise name; `<desc>` = 1–2 sentences describing what the diagram depicts and the method it illustrates. This is the universal gap the audit flagged (zero concept diagrams currently have long-form desc).
- **A11Y-01:** where the audit flagged an `aria-label` paraphrase mismatch, make the root `aria-label` match the diagram's visible title text (`.ttl` element content).

### Design/geometry + layout (DEFECT-01, DEFECT-02) — only where the audit flagged a defect
- **shift-registration.svg** (method-accuracy + crowding): the "elastic warp" arrow/label implies an elastic step, but `shift_register` is purely rigid (scalar δ argmin). Remove or clarify the "elastic warp" label so the diagram does NOT imply elastic warping is part of shift registration. Also relieve the crowded inter-panel gap (two arrows+labels in a 44px gap).
- **banded-alignment.svg**: relieve edge crowding flagged in the audit.
- **pace-fpca.svg**: address the subtitle-overflow risk flagged in the audit.
- Any other Minor design/geometry flags in the §1 table for these 24 diagrams: fix if clearly improving (mismatched lines, misaligned endpoints, overlap, clipping); otherwise leave.

### Method-accuracy (DEFECT-03) — hard gate
- Every correction MUST preserve or improve method-accuracy. A fix must never make a diagram misdepict the method. For the shift-registration "elastic warp" relabel, verify against the actual `shift_register` behavior (rigid scalar shift) — the corrected diagram must depict rigid shift only. When unsure whether a relabel is method-accurate, keep the change conservative and note it for the Phase 65 human review rather than guessing.

### STYLE_SPEC conformance (SPEC-01)
- Keep every diagram conformant to the CURRENT `docs/assets/diagrams/STYLE_SPEC.md` (viewBox conventions, canonical `<style>` block, palette, stroke weights, panel patterns). The audit found 0 STYLE_SPEC defects in these diagrams, so this is mostly "do not regress." NO palette/typography change (that is explicitly out of scope for v10.0). Do NOT edit STYLE_SPEC.md itself (that is Phase 65).

### Constraints
- Diagrams stay hand-authored inline SVG (locked). Edit the SVG source directly by hand.
- Docs-only: no fdars-core/binding/advisor/package changes. Do NOT run the whole-site build here (Phase 65); verify by rendering changed SVGs to PNG with `rsvg-convert` and visually confirming.
- Keep SVGO idempotence in mind (Phase 65 runs the gate) — do not introduce non-idempotent constructs.

### Claude's Discretion
- Exact `<desc>` wording, id naming, and how each specific geometry defect is resolved (widen gap vs reduce font vs reposition) are at the executor's discretion, guided by STYLE_SPEC and method-accuracy.

</decisions>

<code_context>
## Existing Code Insights
- 60-AUDIT.md §1 (concept scoring table, learn/represent/align rows) and §5 (ranked Phase-61 worklist) carry the per-diagram findings — READ FIRST.
- `docs/assets/diagrams/STYLE_SPEC.md` — conformance rubric + the canonical accessibility pattern to extend for long-form title/desc.
- `rsvg-convert` (/usr/bin/rsvg-convert v2.62.3) for render-verify.
</code_context>

<specifics>
## Specific Ideas
- This phase edits ONLY the 24 listed SVG files under `docs/assets/diagrams/`. It does NOT touch thumbs/cards (Phase 64), STYLE_SPEC.md (Phase 65), or any docs page prose.
</specifics>

<deferred>
## Deferred Ideas
- Thumb re-sync for any redrawn diagram → Phase 64 (SYNC-01).
- STYLE_SPEC.md status/count refresh → Phase 65 (SPEC-02).
</deferred>
