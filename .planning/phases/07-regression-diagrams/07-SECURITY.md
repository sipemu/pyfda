---
phase: 07
slug: regression-diagrams
status: verified
threats_open: 0
asvs_level: 1
created: 2026-08-08
---

# Phase 07 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Local dev tooling → repo file | SVGO / mkdocs / local `fdars` calls run against version-controlled assets | Static SVG markup + synthetic verification arrays (no user data, no secrets) |

*Verify-only phase: no diagram files were modified. No network endpoints, authentication, runtime user input, or data persistence. ASVS L1 grep-depth is sufficient.*

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-07-01 | Tampering | SVGO gate reserialising a committed hand-authored SVG | low | mitigate | Gate invoked stdout-only (`--output -`); no files edited this phase | closed |

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
| 2026-08-08 | 1 | 1 | 0 | lean direct review (verify-only phase, 0 edits, ASVS L1) |

---

## Sign-Off

- [x] All threats have a disposition
- [x] Accepted risks documented
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set

**Approval:** verified 2026-08-08
