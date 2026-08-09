---
phase: 1
slug: foundation
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-07
---

# Phase 1 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

This is a documentation-tooling phase: no networked service, no authentication, no user input path, no cryptography. Threats are limited to build/dev-time supply chain and build-time code substitution. Register authored at plan time across all four plans; verified against committed artifacts at ASVS L1 (grep depth).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| npm registry → CI runner | `npx svgo@3.3.4` fetches a package into CI | build tool binary |
| PyPI → CI/local pip | `pytest-markdown-docs==0.9.2` fetched into docs build env | build/test dependency |
| committed SVG files → svgo process | hand-authored diagrams read (never written) by the lint gate | in-repo static assets |
| docs/includes/ committed fragments → markdown-exec / pytest | included Python textually substituted into exec fences at build/test time | in-repo authored content |
| DOCS_FAST env var → build behavior | developer-set env var toggles iteration counts at build time | local dev signal |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-SC | Tampering | npm install of svgo (supply chain) | high | mitigate | Blocking-human legitimacy checkpoint cleared (user-approved after npm verification: svg/svgo, ~36M wk downloads, `postinstall: null`); pinned `svgo@3.3.4` (4× in docs.yml, never latest/v4) | closed |
| T-01-04 | Tampering | pip install pytest-markdown-docs (supply chain) | high | mitigate | Blocking-human legitimacy checkpoint cleared (independent PyPI verification: Modal Labs, repo github.com/modal-labs/pytest-markdown-docs); pinned `==0.9.2` in docs/requirements.txt | closed |
| T-01-01 | Tampering | `npx svgo@3.3.4` postinstall | low | mitigate | Exact version pin; audit confirms `postinstall: null` | closed |
| T-01-02 | Tampering | svgo `--input` path handling | low | accept | Hardcoded `docs/assets/diagrams/*.svg` globs in CI; no user-supplied paths | closed |
| T-01-03 | Tampering | committed hand-authored SVGs (rewrite) | low | mitigate | Gate runs stdout `--output -` + diff only (confirmed; no `-o <file>` in docs.yml); D-02 source of truth never rewritten | closed |
| T-01-02a | Tampering | DOCS_FAST figures mistaken for publishable output | low | mitigate | Helper docstring + D-07: fast mode is speed-only, never the source of truth (confirmed in docs_fig.py) | closed |
| T-01-02b | Information disclosure | svg.hashsalt static string | low | accept | Build-determinism salt for element IDs, not a secret; fixed value is intended matplotlib behavior | closed |
| T-01-03a | Tampering | markdown-exec code injection via snippets | low | mitigate | docs/includes/ committed to git (5 tracked files); author-only, no runtime/user content | closed |
| T-01-03b | Denial of service | empty/malformed include blanks a preamble | low | mitigate | `mkdocs build --strict` fails on the resulting error rather than shipping a blank figure | closed |
| T-01-04b | Tampering | example fence code executed by pytest | low | mitigate | Fences are committed in-repo docs content; same trust level as existing markdown-exec build | closed |
| T-01-04c | Denial of service | fences silently skipped (missing syntax flag) | low | mitigate | `--markdown-docs-syntax=superfences` present in docs.yml (2×); Gate B collected + passed 8/8 fences | closed |

*Status: open · closed · open — below high threshold (non-blocking)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-01 | T-01-02 | svgo input paths are hardcoded CI globs, not user input — no practical path-traversal surface at ASVS L1 | Simon Müller | 2026-08-07 |
| R-02 | T-01-02b | svg.hashsalt is a documented determinism salt, not a secret — a fixed value is the intended behavior | Simon Müller | 2026-08-07 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-07 | 11 | 11 | 0 | gsd-secure-phase (orchestrator, L1 grep-depth short-circuit) |

Both high-severity supply-chain threats (T-01-SC, T-01-04) were mitigated by blocking-human legitimacy checkpoints that were cleared during execution; the block-on-high threshold is satisfied (0 open threats at or above high).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-07
