---
phase: 03
slug: learn-diagrams
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-08
---

# Phase 03 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Local dev tooling → repo file | SVGO (`svgo@3.3.4`) and `mkdocs build` run locally against version-controlled hand-authored SVG assets | Static SVG markup (no user data, no secrets) |

*No network endpoints, no authentication, no runtime user input, no data persistence. This phase edits static hand-authored SVG diagrams and runs local check-only tooling; ASVS L1 grep-depth verification is sufficient.*

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-03-01 | Tampering | SVGO gate rewriting the committed hand-authored `smoothing.svg` | low | mitigate | Gate invoked in stdout mode (`--output -`) only; `git diff --stat docs/assets/diagrams/smoothing.svg` confirms only the intended coordinate edits (1 insertion / 1 deletion per plan), not an SVGO reserialisation | closed |
| T-03-02 | Tampering | SVGO gate rewriting any committed hand-authored learn/ SVG | low | mitigate | Section-wide gate (all 6 diagrams) run stdout-only (`--output -`); `git diff --stat docs/assets/diagrams/` shows no reserialisation from the gate run | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-08 | 2 | 2 | 0 | gsd-secure-phase (short-circuit: 0 open, register authored at plan time, ASVS L1) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-08
