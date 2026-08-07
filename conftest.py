"""pytest-markdown-docs globals + snippet expansion for fdars doc fences.

Injects ``np``, ``plt``, and ``fdars`` into every markdown code fence executed
by ``pytest-markdown-docs`` (FND-05, D-06). The example exec blocks still
perform their own imports explicitly (self-documenting build-time figures);
these globals are a fallback so isolated fences don't fail on a bare ``np``.

``matplotlib.use("Agg")`` MUST precede ``import matplotlib.pyplot as plt`` --
CI has no display, so the non-interactive backend must be selected before
pyplot binds a backend. Same ordering as ``scripts/docs_fig.py`` (lines 37-40).

Note: ``docs_fig`` / ``docs_data`` are NOT injected here. Those resolve via
``PYTHONPATH=scripts`` (set by the CI Gate B step and by local smoke-test runs).

D-04 harness decision (recorded 2026-08-07):
    ``pytest-markdown-docs`` is LOCKED IN as THE doc-test harness. The RESEARCH
    cross-fence-state risk did NOT materialise -- 7/8 canadian-weather.md fences
    are self-contained and pass in isolation. The one failure was a *different*
    interaction: FND-04's ``pymdownx.snippets`` ``--8<--`` include directive
    (plan 01-03) is a MkDocs *build-time* preprocessor that pytest-markdown-docs
    does not run, so a raw ``--8<-- "includes/..."`` line reached Python and
    raised ``TypeError: bad operand type for unary -: 'str'``.

    Rather than the CONTEXT fallbacks (custom fence-exec harness / consolidate-
    fences), which target cross-fence state and don't apply here, we teach the
    harness to expand snippet includes via the documented
    ``pytest_markdown_docs_markdown_it()`` hook below. This keeps
    pytest-markdown-docs as the harness, leaves every example ``.md`` untouched
    (page rewrites are Phase 9's domain), and mirrors mkdocs.yml's snippets
    ``base_path: [docs]`` so ``--8<-- "includes/x.md"`` -> ``docs/includes/x.md``.
"""
import pathlib
import re

import matplotlib

matplotlib.use("Agg")  # non-interactive backend; must precede the pyplot import
import matplotlib.pyplot as plt  # noqa: E402

import numpy as np  # noqa: E402
import fdars  # noqa: E402

# Snippet base directory -- mirrors mkdocs.yml `pymdownx.snippets: base_path: [docs]`.
_SNIPPET_BASE = pathlib.Path(__file__).parent / "docs"
# pymdownx.snippets include line, e.g. `--8<-- "includes/load-canadian-weather.md"`.
_INCLUDE_RE = re.compile(r'^(?P<indent>\s*)-{1,}8<-{1,}\s+"(?P<path>[^"]+)"\s*$')


def _expand_snippet_includes(text, _depth=0):
    """Expand ``--8<-- "path"`` include lines within a code fence's content.

    Mirrors pymdownx.snippets file-inclusion semantics (base_path=docs) so a
    fence that relies on a MkDocs build-time include still runs under pytest.
    Nested includes are supported up to a small depth guard.
    """
    if _depth > 10:
        return text
    out = []
    for line in text.splitlines():
        m = _INCLUDE_RE.match(line)
        if not m:
            out.append(line)
            continue
        include_path = _SNIPPET_BASE / m.group("path")
        indent = m.group("indent")
        included = _expand_snippet_includes(include_path.read_text("utf8"), _depth + 1)
        out.extend(indent + inc_line for inc_line in included.splitlines())
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _snippet_expand_rule(state):
    """markdown_it core rule: rewrite fence-token content, expanding includes."""
    for token in state.tokens:
        if token.type == "fence" and "8<" in token.content:
            token.content = _expand_snippet_includes(token.content)


def pytest_markdown_docs_globals():
    """Return globals injected into every markdown code fence during testing."""
    return {"np": np, "plt": plt, "fdars": fdars}


def pytest_markdown_docs_markdown_it():
    """Return a MarkdownIt parser that expands pymdownx.snippets includes.

    Without this, a fence using ``--8<-- "includes/..."`` (FND-04) would fail
    under pytest-markdown-docs, which does not run MkDocs' build-time snippet
    preprocessor. The added core rule expands those includes in-place (D-04).
    """
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    md.core.ruler.push("fdars_snippet_expand", _snippet_expand_rule)
    return md
