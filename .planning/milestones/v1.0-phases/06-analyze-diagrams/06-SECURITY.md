---
phase: 06
slug: analyze-diagrams
status: verified
threats_open: 0
asvs_level: 1
created: 2026-08-08
---

# Phase 06 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Local dev tooling → repo file | SVGO (`svgo@3.3.4`) and `mkdocs` run locally against version-controlled hand-authored SVG assets | Static SVG markup (no user data, no secrets) |

*No network endpoints, authentication, runtime user input, or data persistence. Static hand-authored SVG edits + local check-only tooling; ASVS L1 grep-depth is sufficient.*

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-06-01 | Tampering | SVGO gate reserialising a committed hand-authored SVG | low | mitigate | Gate invoked stdout-only (`--output -`); files edited only by hand + verified via `git diff` | closed |

*Only open threats at or above the `high` block threshold count toward `threats_open`.*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-08 | 1 | 1 | 0 | lean direct review (0 open, ASVS L1, static-asset phase) |

---

## Sign-Off

- [x] All threats have a disposition
- [x] Accepted risks documented
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set

**Approval:** verified 2026-08-08
