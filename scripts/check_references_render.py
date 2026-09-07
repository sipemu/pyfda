#!/usr/bin/env python3
"""Fast render/nav-validity checker for docs/references.md.

Stdlib-only (pathlib, re, sys) — runs without a compiled fdars extension.
Does NOT execute markdown-exec fences.  The whole-site ``mkdocs build --strict``
(~25 min, executed fences) is the Phase-84 close gate; this script is the
Phase-83 fast gate.

Checks performed:
  1. docs/references.md exists at the expected path.
  2. Code-fence markers in references.md are balanced (even count of
     triple-backtick lines — an odd count means an unclosed fence).
  3. mkdocs.yml contains ``Scientific References: references.md`` directly
     after the ``AI Capability Map: ai-capability-map.md`` entry.
  4. Every relative ``.md`` link inside docs/references.md resolves to an
     existing file under docs/ (http/https links are skipped).

Exits 0 with ``RENDER_VALIDITY_OK`` on success, non-zero with a descriptive
error message on any failure.
"""

import pathlib
import re
import sys


def _repo_root() -> pathlib.Path:
    """Return the repository root (parent of this script's directory)."""
    return pathlib.Path(__file__).parent.parent.resolve()


def check_file_exists(docs_dir: pathlib.Path) -> None:
    """Assert docs/references.md exists."""
    page = docs_dir / "references.md"
    if not page.exists():
        print(f"ERROR: docs/references.md not found at {page}", file=sys.stderr)
        sys.exit(1)
    print(f"  [1] docs/references.md exists: OK ({page})")


def check_balanced_fences(docs_dir: pathlib.Path) -> None:
    """Assert code-fence markers (lines starting with ```) are balanced."""
    page = docs_dir / "references.md"
    text = page.read_text(encoding="utf-8")
    fence_lines = re.findall(r"^```", text, re.MULTILINE)
    count = len(fence_lines)
    if count % 2 != 0:
        print(
            f"ERROR: Unbalanced code fences in docs/references.md — "
            f"found {count} opening/closing markers (must be even).",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"  [2] Code-fence balance: OK ({count} markers, all paired)")


def check_nav_placement(repo_root: pathlib.Path) -> None:
    """Assert mkdocs.yml has Scientific References directly after AI Capability Map."""
    mkdocs_path = repo_root / "mkdocs.yml"
    if not mkdocs_path.exists():
        print(f"ERROR: mkdocs.yml not found at {mkdocs_path}", file=sys.stderr)
        sys.exit(1)

    lines = mkdocs_path.read_text(encoding="utf-8").splitlines()

    cap_map_line = None
    for i, line in enumerate(lines):
        if "AI Capability Map: ai-capability-map.md" in line:
            cap_map_line = i
            break

    if cap_map_line is None:
        print(
            "ERROR: mkdocs.yml does not contain 'AI Capability Map: ai-capability-map.md'.",
            file=sys.stderr,
        )
        sys.exit(1)

    next_line_idx = cap_map_line + 1
    if next_line_idx >= len(lines):
        print(
            "ERROR: mkdocs.yml ends immediately after AI Capability Map entry — "
            "no room for Scientific References entry.",
            file=sys.stderr,
        )
        sys.exit(1)

    next_line = lines[next_line_idx]
    if "Scientific References: references.md" not in next_line:
        print(
            f"ERROR: Expected 'Scientific References: references.md' on line "
            f"{next_line_idx + 1} of mkdocs.yml (immediately after AI Capability Map), "
            f"but found: {next_line!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"  [3] Nav placement: OK ('Scientific References: references.md' "
        f"at mkdocs.yml line {next_line_idx + 1}, directly after AI Capability Map)"
    )


def check_internal_links(docs_dir: pathlib.Path) -> None:
    """Assert every relative .md link in references.md resolves under docs/."""
    page = docs_dir / "references.md"
    text = page.read_text(encoding="utf-8")

    # Match markdown links: [text](target)
    # Skip http/https links; only check .md relative links.
    link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    broken = []
    checked = []

    for match in link_pattern.finditer(text):
        target = match.group(2)
        # Skip absolute URLs
        if target.startswith("http://") or target.startswith("https://"):
            continue
        # Strip fragment anchors for file resolution
        path_part = target.split("#")[0]
        if not path_part.endswith(".md"):
            continue
        resolved = (docs_dir / path_part).resolve()
        if not resolved.exists():
            broken.append((target, resolved))
        else:
            checked.append(target)

    if broken:
        for target, resolved in broken:
            print(
                f"ERROR: Internal link '{target}' in docs/references.md does not "
                f"resolve to an existing file (looked for {resolved}).",
                file=sys.stderr,
            )
        sys.exit(1)

    print(
        f"  [4] Internal links: OK ({len(checked)} relative .md link(s) resolve: "
        + ", ".join(checked)
        + ")"
    )


def main() -> None:
    repo_root = _repo_root()
    docs_dir = repo_root / "docs"

    print("Running fast render/nav-validity check for docs/references.md ...")
    check_file_exists(docs_dir)
    check_balanced_fences(docs_dir)
    check_nav_placement(repo_root)
    check_internal_links(docs_dir)
    print("RENDER_VALIDITY_OK")


if __name__ == "__main__":
    main()
