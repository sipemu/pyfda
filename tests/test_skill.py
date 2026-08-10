"""Tests for the fdars-advisor agent skill (Phase 13, Plans 13-01 and 13-02).

Requires: fdars[mcp] (mcp>=2.0.0, Python >=3.10) and PyYAML.

All tests in this module are skipped on Python <3.10 via the module-level
``pytestmark``.  No ``ANTHROPIC_API_KEY`` and no network are required.

Plan 13-01 (tracer):
  - test_skill_md_frontmatter
  - test_walkthrough_script_offline
  - test_walkthrough_delta_nonempty

Plan 13-02 (expansion):
  - test_skill_md_name_matches_dir
  - test_skill_md_compatibility
  - test_walkthrough_py39_exit0
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest
import yaml

# ---------------------------------------------------------------------------
# Module-level skip guard: Python 3.9 CI runners skip cleanly
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="mcp requires Python 3.10+",
)

# ---------------------------------------------------------------------------
# Module-level path constants — resolved from the repo root
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

SKILL_MD: pathlib.Path = _REPO_ROOT / ".claude" / "skills" / "fdars-advisor" / "SKILL.md"
SCRIPT_PATH: pathlib.Path = (
    _REPO_ROOT
    / ".claude"
    / "skills"
    / "fdars-advisor"
    / "scripts"
    / "fdars_advisor_walkthrough.py"
)

# ---------------------------------------------------------------------------
# Helper: parse YAML frontmatter from a SKILL.md file
# ---------------------------------------------------------------------------


def _parse_frontmatter(path: pathlib.Path) -> dict:
    """Parse the YAML frontmatter block from a SKILL.md file.

    Parameters
    ----------
    path : pathlib.Path
        Path to the SKILL.md file.

    Returns
    -------
    dict
        Parsed frontmatter as a Python dict.
    """
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert m, f"No YAML frontmatter found in {path}"
    return yaml.safe_load(m.group(1))


# ---------------------------------------------------------------------------
# Plan 13-01 tracer tests (SKILL.md frontmatter + offline walkthrough)
# ---------------------------------------------------------------------------


def test_skill_md_frontmatter():
    """SKILL.md parses and has required 'name' and 'description' fields.

    Verifies SKILL-01: SKILL.md is spec-valid with required frontmatter.
    """
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"
    fm = _parse_frontmatter(SKILL_MD)
    assert isinstance(fm.get("name"), str) and fm["name"], (
        f"frontmatter 'name' missing or empty; got: {fm.get('name')!r}"
    )
    assert isinstance(fm.get("description"), str) and fm["description"], (
        f"frontmatter 'description' missing or empty; got: {fm.get('description')!r}"
    )


def test_walkthrough_script_offline():
    """Walkthrough script exits 0 when run offline (ANTHROPIC_API_KEY absent).

    Verifies SKILL-01: the offline path works end-to-end without credentials.
    """
    assert SCRIPT_PATH.exists(), f"Walkthrough script not found at {SCRIPT_PATH}"
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert result.returncode == 0, (
        f"Walkthrough script exited {result.returncode}.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


def test_walkthrough_delta_nonempty():
    """Walkthrough script stdout contains a Delta header with >=1 value line.

    Verifies SKILL-01 + Success Criterion 3 (offline portion): the script
    prints a non-empty deterministic before/after delta block.
    """
    assert SCRIPT_PATH.exists(), f"Walkthrough script not found at {SCRIPT_PATH}"
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert result.returncode == 0, (
        f"Script failed (exit {result.returncode}); cannot check delta.\n"
        f"stderr: {result.stderr}"
    )
    stdout = result.stdout
    # The script prints a line starting with "  Delta (" — grep for header
    assert "Delta (" in stdout, (
        f"Delta header 'Delta (' not found in script output.\n"
        f"stdout: {stdout!r}"
    )
    # After the Delta header there must be at least one value line containing ": "
    header_idx = stdout.index("Delta (")
    remainder = stdout[header_idx:]
    lines_after = [ln for ln in remainder.splitlines()[1:] if ": " in ln]
    assert len(lines_after) >= 1, (
        f"Delta block is empty — expected >=1 value lines after header.\n"
        f"stdout after header: {remainder!r}"
    )


# ---------------------------------------------------------------------------
# Plan 13-02 expansion tests (added in Plan 02 — stubs for collection only)
# ---------------------------------------------------------------------------


def test_skill_md_name_matches_dir():
    """SKILL.md 'name' field equals its parent directory name 'fdars-advisor'.

    Verifies SKILL-01 + agentskills.io discovery requirement.
    """
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"
    fm = _parse_frontmatter(SKILL_MD)
    expected = SKILL_MD.parent.name  # "fdars-advisor"
    assert fm.get("name") == expected, (
        f"'name' field {fm.get('name')!r} does not match directory name {expected!r}"
    )


def test_skill_md_compatibility():
    """SKILL.md 'compatibility' field documents Python >=3.10 and pip requirement.

    Verifies SKILL-02: execution environment is documented clearly.
    """
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"
    fm = _parse_frontmatter(SKILL_MD)
    compat = fm.get("compatibility", "") or ""
    assert "3.10" in compat or "Python" in compat, (
        f"'compatibility' does not mention Python 3.10+: {compat!r}"
    )
    assert "pip" in compat or "install" in compat, (
        f"'compatibility' does not document pip/install step: {compat!r}"
    )


def test_walkthrough_py39_exit0():
    """Walkthrough script exits 0 and prints informative message on Python 3.9.

    Verifies SKILL-02: the version guard works gracefully below 3.10.
    This test is inherently a static-code check on Python >=3.10 runners
    (we cannot actually run under 3.9 from the 3.10+ venv); instead we
    assert the version guard text appears in the script source.
    """
    assert SCRIPT_PATH.exists(), f"Walkthrough script not found at {SCRIPT_PATH}"
    source = SCRIPT_PATH.read_text()
    # The version guard must appear BEFORE any fdars.mcp import line
    guard_match = re.search(r"sys\.version_info\s*<\s*\(3,\s*10\)", source)
    assert guard_match, "Version guard 'sys.version_info < (3, 10)' not found in script"
    # Guard must appear before the first 'from fdars.mcp' import
    mcp_import_match = re.search(r"from fdars\.mcp", source)
    assert mcp_import_match, "'from fdars.mcp' import not found in script"
    assert guard_match.start() < mcp_import_match.start(), (
        "Version guard appears AFTER 'from fdars.mcp' import — "
        "this will raise ImportError on Python 3.9 (Pitfall 4)"
    )
