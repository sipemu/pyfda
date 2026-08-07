# External Integrations

**Analysis Date:** 2026-08-07

## APIs & External Services

**None detected.** This is a library package with no runtime API dependencies.

## Data Storage

**Databases:**
- Not applicable - this is a scientific computation library, not a service

**File Storage:**
- **Local filesystem only** - Vendored CSV datasets embedded in wheels via `include = ["python/fdars/data/*.csv"]`
- Dataset loading: `fdars.datasets` module reads from embedded resources via `importlib.resources`

**Caching:**
- No caching layer - library operates on in-memory NumPy arrays

## Authentication & Identity

**Auth Provider:**
- Not applicable - no authentication required

## Monitoring & Observability

**Error Tracking:**
- None configured

**Logs:**
- No structured logging
- Rust panics surface as Python exceptions via PyO3

## CI/CD & Deployment

**Hosting:**
- **PyPI** - Python Package Index (published wheels and sdist)
- **GitHub Pages** - Documentation site via GitHub Actions (ghp-import)
- **GitHub Actions** - CI/CD runner

**CI Pipeline:**
- `.github/workflows/ci.yml` - Main CI on `push` and `pull_request`
  - Rust `fmt` check (Rustfmt)
  - Rust `clippy` linting (`-D warnings`)
  - Rust tests (stable + MSRV 1.83)
  - Python tests (3.10, 3.12, 3.13)
- `.github/workflows/publish.yml` - Publish to PyPI on git tags matching `v*`
  - Builds wheels for Linux (x86_64, aarch64), macOS (x86_64, aarch64), Windows (x86_64)
  - Builds source distribution (sdist)
  - Uses PyO3/maturin-action for multi-platform compilation
  - Publishes to PyPI via `pypa/gh-action-pypi-publish`
- `.github/workflows/docs.yml` - Deploy docs to GitHub Pages on `main` push
  - Builds documentation with live code execution
  - Publishes via `ghp-import`

## Environment Configuration

**Required env vars:**
- None - library requires no external configuration

**Secrets location:**
- PyPI token managed via GitHub Actions environment `pypi` (OpenID Connect, no stored secrets)

## Webhooks & Callbacks

**Incoming:**
- GitHub webhooks for CI/CD (push, pull_request, tag push)

**Outgoing:**
- PyPI publish (authenticated via OIDC)
- GitHub Pages deployment (via git push to `gh-pages` branch via ghp-import)

## Dependency Management

**Rust Dependencies:**
- Pinned via `Cargo.lock` (committed to repo)
- fdars-core 0.14.0 from crates.io

**Python Dependencies:**
- Core runtime: numpy, pandas (pinned in `pyproject.toml`)
- Optional: matplotlib 3.6+
- Dev/test: pytest, maturin
- Docs build: mkdocs-material, markdown-exec, scipy, scikit-learn (pinned in `docs/requirements.txt`)
- Site docs: mkdocs-material, markdown-exec, matplotlib, numpy, pandas, scipy, scikit-learn (pinned in `site/requirements.txt`)

## Build & Release Process

**Development:**
- Local build: `maturin develop --release`
- Requires Rust 1.83+ and Python 3.9+

**Publishing:**
- Manual: Tag commit with `v*` pattern (e.g., `v0.2.0`)
- Automatic: GitHub Actions builds wheels for all platforms and publishes to PyPI
- Attestations: Disabled in publish workflow

---

*Integration audit: 2026-08-07*
