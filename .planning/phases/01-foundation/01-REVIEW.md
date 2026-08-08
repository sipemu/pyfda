---
phase: 01-foundation
reviewed: 2026-08-07T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - scripts/docs_fig.py
  - conftest.py
  - svgo.config.mjs
  - .github/workflows/docs.yml
  - mkdocs.yml
  - docs/requirements.txt
  - docs/assets/diagrams/STYLE_SPEC.md
  - docs/includes/load-canadian-weather.md
  - docs/includes/load-canadian-weather-precip.md
  - docs/includes/load-growth.md
  - docs/includes/load-phoneme.md
  - docs/includes/load-tecator.md
  - docs/examples/canadian-weather.md
findings:
  critical: 1
  warning: 4
  info: 2
  total: 7
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-08-07
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Reviewed the Phase 1 Foundation tooling: the `docs_fig.py` build helper, `conftest.py`
pytest harness, `svgo.config.mjs` idempotency config, the CI workflow in `docs.yml`,
`mkdocs.yml`, `docs/requirements.txt`, the five snippet-include preambles, and the
`canadian-weather.md` example page (the only gated doc-test page at this phase).

The include preambles are clean pure-Python (no fence delimiters, no non-ASCII). The
`docs_fig.py` rcParam setup and `fast()` helper are mechanically correct. The `conftest.py`
snippet-expansion logic is correct for the double-quoted include syntax used throughout the
codebase.

One critical issue was found: `check_docs_figures.py` (referenced but not in the formal
review list — reviewed because it is called directly from the CI workflow under review) will
silently exit 0 and report "no errors" if the `site_dir` argument does not exist or contains
no `index.html` files. Because this script is the only gate against silently-deployed broken
figures, a false-negative here would ship traceback content to production without CI catching
it. Four warnings cover: an incorrect prose description in `STYLE_SPEC.md`, an implicit
transitive dependency on `markdown-it-py` that is not pinned in `docs/requirements.txt`, the
unhandled `FileNotFoundError` in the snippet expander when an include path does not exist,
and the resource-leak pattern in `check_docs_figures.py`.

## Critical Issues

### CR-01: `check_docs_figures.py` silently exits 0 when `site_dir` is missing or empty

**File:** `scripts/check_docs_figures.py:22-35`

**Issue:** `glob.glob(os.path.join(site_dir, "**", "index.html"), recursive=True)` returns
an empty list (no error) when `site_dir` does not exist on disk, or when it exists but
contains no HTML. In either case `bad` is empty, the function prints "OK" and returns 0 —
a false-negative exit code. The CI step runs this immediately after `mkdocs build --strict`
in the same `run:` block, so `set -e` prevents the script from running if the build fails.
However, if `mkdocs build` produces a site directory with an unexpected layout (e.g. a
custom `docs_dir` change, a future refactor) the gate goes silent rather than failing.
The current 43-page site is fine, but the gate's integrity rests on an untested assumption
about directory structure rather than an explicit assertion.

**Fix:**

```python
def main(site_dir: str) -> int:
    if not os.path.isdir(site_dir):
        print(f"ERROR: site directory does not exist: {site_dir!r}", file=sys.stderr)
        return 2

    html_files = glob.glob(
        os.path.join(site_dir, "**", "index.html"), recursive=True
    )
    if not html_files:
        print(f"ERROR: no index.html files found in {site_dir!r} — "
              "was the site built?", file=sys.stderr)
        return 2

    bad = []
    for html in html_files:
        with open(html, encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
        hits = [m for m in MARKERS if m in txt]
        if hits:
            rel = os.path.relpath(os.path.dirname(html), site_dir)
            bad.append((rel, hits))
    ...
```

---

## Warnings

### WR-01: `STYLE_SPEC.md` line 27 contradicts the actual gate implementation

**File:** `docs/assets/diagrams/STYLE_SPEC.md:27`

**Issue:** The "SVGO Invocation" section states: *"The gate is check-only: it diffs stdout
against the source file. A zero diff means the diagram is conforming."* This is factually
wrong. The actual CI gate (and the correct description at line 167 of the same file, and in
`docs.yml` lines 47-51) performs an **idempotency check** (pass 1 == pass 2), not a diff
against the hand-authored source. The discrepancy means the "SVGO Invocation" section is
misleading to anyone hand-editing diagrams: they might expect conformance means their source
matches svgo output (it does not, because svgo always normalises whitespace and attribute
order), and might waste time trying to pre-normalise their source.

**Fix:** Replace line 27 with the accurate description:

```markdown
The gate is **check-only** (idempotence check, not source diff): it runs svgo twice and
diffs pass 2 against pass 1. A zero diff means the diagram is stable under the config.
The gate **never rewrites** a committed hand-authored SVG (D-02).
```

---

### WR-02: `markdown-it-py` is an implicit transitive dependency — not pinned in `docs/requirements.txt`

**File:** `docs/requirements.txt:16` / `conftest.py:91`

**Issue:** `conftest.py` does `from markdown_it import MarkdownIt` inside
`pytest_markdown_docs_markdown_it()`. The `markdown-it-py` package that provides
`markdown_it` is NOT listed in `docs/requirements.txt`. It is currently available only as a
transitive dependency of `pytest-markdown-docs==0.9.2`. If `pytest-markdown-docs` drops or
changes its dependency on `markdown-it-py` in a future compatible release (or if the pin is
changed), the conftest hook will fail with `ModuleNotFoundError` at test collection time,
silently breaking the D-04 snippet-expansion mechanism. Because `pytest-markdown-docs` is
pinned to an exact version (`==0.9.2`) the risk is contained for now, but the dependency is
invisible to future maintainers.

**Fix:** Add an explicit, minimum-version pin to `docs/requirements.txt`:

```
markdown-it-py>=3.0          # conftest.py: pytest_markdown_docs_markdown_it hook
```

---

### WR-03: `_expand_snippet_includes` raises bare `FileNotFoundError` on a missing include path

**File:** `conftest.py:66`

**Issue:** `include_path.read_text("utf8")` raises `FileNotFoundError` if the resolved path
does not exist (e.g. a typo in an `--8<--` directive, or a future rename of an include
file). The exception propagates out of `_snippet_expand_rule` with no indication of which
fence or which include path caused the failure. Under `pytest-markdown-docs` this surfaces as
a confusing traceback inside the markdown-it core-rule execution rather than as a clear test
failure pointing at the offending doc file.

**Fix:** Wrap the read with a descriptive error:

```python
try:
    file_text = include_path.read_text("utf8")
except FileNotFoundError:
    raise FileNotFoundError(
        f"Snippet include not found: {include_path!r} "
        f"(referenced as {m.group('path')!r})"
    ) from None
included = _expand_snippet_includes(file_text, _depth + 1)
```

---

### WR-04: `check_docs_figures.py` opens HTML files without a `with` statement

**File:** `scripts/check_docs_figures.py:25`

**Issue:** `open(html, encoding="utf-8", errors="replace").read()` does not close the file
handle explicitly. CPython's reference-counting GC will close it immediately in practice, but
this pattern is incorrect and will cause resource-handle leaks under any non-CPython
implementation (PyPy, GraalPy) or if the site grows large enough that the open-file-handle
limit is hit during the scan. The file handle is already wrapped by the `open()` call, so
the fix is a two-line change.

**Fix:**

```python
with open(html, encoding="utf-8", errors="replace") as fh:
    txt = fh.read()
```

---

## Info

### IN-01: `load_canadian_weather` raises an opaque `KeyError` on invalid `variable` argument

**File:** `scripts/docs_data.py:77-80`

**Issue:** Passing an unsupported value (e.g. `load_canadian_weather("temp")`) raises
`KeyError: 'temp'` — a bare dict-lookup error with no guidance on valid values. The public
docstring documents the accepted literals, so a human reading an error in a failing doc-test
exec block gets no actionable message.

**Fix:**

```python
try:
    fname = {
        "temperature": "canadian_weather.csv",
        "precipitation": "canadian_weather_precip.csv",
    }[variable]
except KeyError:
    raise ValueError(
        f"Unknown variable {variable!r}; expected 'temperature' or 'precipitation'."
    ) from None
```

---

### IN-02: `render()` silently wraps non-SVG content when `<svg` tag is absent

**File:** `scripts/docs_fig.py:103-106`

**Issue:** If `figure.savefig(buf, format="svg", ...)` produces output that for any reason
does not contain `<svg` (format change, matplotlib version difference, backend quirk), the
`start = svg.find("<svg")` returns `-1` and the branch is skipped, leaving the full raw
content — including XML declaration and doctype preamble — wrapped in
`<div class="fdars-figure">...</div>`. The result is broken HTML embedded in the docs page.
`check_docs_figures.py` would not catch this because it only looks for `Traceback` and
`exec-error` markers. The `<xml` or `<!DOCTYPE` preamble content would pass all CI gates
and ship silently.

**Fix:** Assert that the SVG tag was found, or log a warning:

```python
start = svg.find("<svg")
if start == -1:
    raise RuntimeError(
        "render(): matplotlib savefig produced output with no <svg tag; "
        "check backend and matplotlib version."
    )
svg = svg[start:]
```

---

_Reviewed: 2026-08-07_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
