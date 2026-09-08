"""SC-3 traceability gate + COMP-02 fdars-column grounding gate.

Parses ``paper/sections/comparison_table.tex`` and ``paper/comparison_evidence.md``
to verify:

1. **SC-3 peer-traceability:** Every non-fdars covered cell (``\\checkmark`` or
   ``\\textit{partial}``) in the comparison table has at least one matching claim
   line in the evidence file.
2. **COMP-02 fdars-grounding:** Every fdars column cell is ``\\checkmark`` AND is
   backed by at least one real submodule in ``python/fdars/_capability_map.json``
   that contains ≥1 public (non-underscore) callable.

Usage
-----
Run from the repository root::

    python paper/code/check_comparison.py

Exits 0 and prints ``COMPARISON_TRACE_OK`` when BOTH checks pass.
Exits 1 and prints one or more of:
  - ``UNSOURCED: <column> / <dimension> (<state>)`` for SC-3 peer gaps.
  - ``STATE_MISMATCH: <column> / <dimension> (table=checkmark, best_evidence=partial)``
    when the table claims full support but every evidence entry is only partial.
  - ``FDARS_NOT_CHECK: <dimension>`` when an fdars cell is not ``\\checkmark``.
  - ``UNGROUNDED: <dimension> (submodules=<tuple>)`` when no backing submodule
    has ≥1 public callable in the map.

Notes
-----
- The first data column (fdars) is grounded from ``_capability_map.json``
  (COMP-02), not from the evidence file.
- The trailing ``sklearn-compatible API`` and ``Language`` rows are excluded from
  both checks (they are not capability dimensions).
- Dimension labels are matched by exact normalized string equality (whitespace
  stripped, ``\\&`` replaced with ``&``).
- A family cell is considered evidenced if AT LEAST ONE member package has a
  matching (dimension-label, state != —) claim line in its section.
- A dimension is grounded if AT LEAST ONE of its listed submodule keys exists
  in the top-level capability map AND has ≥1 public callable entry.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_TABLE = _REPO / "paper" / "sections" / "comparison_table.tex"
_EVIDENCE = _REPO / "paper" / "comparison_evidence.md"
_CAP_MAP = _REPO / "python" / "fdars" / "_capability_map.json"

# ── Column definitions ────────────────────────────────────────────────────────
# Order matches the tabular column order in comparison_table.tex (0-indexed).
# Col 0: Capability label (not a data column)
# Col 1: fdars  — SKIPPED (grounded from _capability_map.json)
# Cols 2-6: peer families
_PEER_COLS: list[tuple[str, list[str]]] = [
    ("scikit-fda", ["scikit-fda"]),
    ("FDApy", ["FDApy"]),
    ("R (fda / fda.usc / refund)", ["fda", "fda.usc", "refund"]),
    ("funData / tidyfun", ["funData", "tidyfun"]),
    ("Matlab (fdaM / PACE)", ["fdaM", "PACE"]),
]

# ── fdars-column grounding map ────────────────────────────────────────────────
# Maps each normalized dimension label (as returned by _norm(), matching what
# the table parser produces) to the tuple of _capability_map.json top-level
# submodule keys that back the fdars ✓ cell for that dimension.
# Transcribed from RESEARCH.md §fdars Column Derivation.
# A dimension is grounded if AT LEAST ONE listed submodule exists in the map
# with ≥1 public (non-underscore) callable.
DIMENSION_SUBMODULES: dict[str, tuple[str, ...]] = {
    "Representation / basis smoothing": ("basis", "represent", "smoothing"),
    "Registration / alignment": ("alignment",),
    "Depth & outlier detection": ("depth", "outliers"),
    "FPCA / covariance / PACE sparse FPCA": ("pace_fpca", "covariance"),
    "Clustering": ("clustering",),
    "Classification": ("classification", "shapelet"),
    "Functional regression (SoF / FoF)": ("regression", "scalar_on_function", "famm"),
    "Functional time series": ("fts",),
    "Statistical process monitoring": ("spm",),
    "Inference / hypothesis testing": ("inference",),
    "Conformal prediction & tolerance bands": ("conformal", "tolerance"),
    "Density / Frechet / metric-space": ("density_fda", "frechet", "metric"),
    "Simulation & datasets": ("simulation", "datasets"),
    "Grounded advisor + scientific provenance": ("explain",),
}

# Rows that are NOT capability dimensions — excluded from traceability check.
_NON_CAPABILITY_ROWS = {
    "sklearn-compatible api",
    "language",
}

# ── Normalization helpers ─────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Normalize a dimension label for comparison.

    Strips surrounding whitespace, replaces ``\\&`` with ``&``, and removes
    LaTeX accent macros such as ``\\'{e}`` → ``e``.

    Parameters
    ----------
    s : str
        Raw label string (from LaTeX or Markdown).

    Returns
    -------
    str
        Normalized label suitable for equality comparison.
    """
    t = s.strip()
    t = t.replace(r"\&", "&")
    # Remove LaTeX accent macros: \'{X}, \`{X}, \"{X}, \^{X}, \~{X}, \={X}
    t = re.sub(r"\\[`'^\"~=]?\{([a-zA-Z])\}", r"\1", t)
    # Also handle non-braced forms: \'e → e
    t = re.sub(r"\\[`'^\"~=]([a-zA-Z])", r"\1", t)
    return t


def _cell_state(cell: str) -> str:
    """Determine the coverage state of a LaTeX table cell token.

    Parameters
    ----------
    cell : str
        Stripped cell content from the LaTeX tabular row.

    Returns
    -------
    str
        One of ``"checkmark"``, ``"partial"``, or ``"none"``.
    """
    if r"\checkmark" in cell:
        return "checkmark"
    if r"\textit{partial}" in cell or "partial" in cell.lower():
        return "partial"
    return "none"


# ── Table parser ─────────────────────────────────────────────────────────────

def _parse_table(path: Path) -> list[tuple[str, list[str]]]:
    """Parse the LaTeX comparison table into (dimension_label, [cell_states]) rows.

    Only returns rows for capability dimensions (excludes trailing metadata rows).
    Cell states are returned for ALL columns including fdars (col index 1).

    Parameters
    ----------
    path : Path
        Path to ``comparison_table.tex``.

    Returns
    -------
    list of (label, states)
        Each element is a (normalized dimension label, list of cell states) tuple.
        The list has six entries: [fdars, scikit-fda, FDApy, R-family, fun/tidy, Matlab].
    """
    text = path.read_text(encoding="utf-8")

    # Collect raw row lines — lines ending with \\ that are NOT header/rule lines
    # and appear between \midrule ... \bottomrule.
    # We use a line-by-line state machine: collect cells after the first \midrule,
    # stop at \bottomrule.

    rows: list[tuple[str, list[str]]] = []
    in_body = False
    current_cells: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if r"\toprule" in line or r"\midrule" in line:
            in_body = True
            current_cells = []
            continue
        if r"\bottomrule" in line:
            break
        if not in_body:
            continue

        # Skip structural lines (empty, comment, begin/end)
        if not line or line.startswith("%") or line.startswith("\\begin") or line.startswith("\\end"):
            continue

        # Accumulate cells; a row ends when a line contains \\
        current_cells.append(line)

        if line.rstrip().endswith("\\\\"):
            # Reconstruct the full row text and split on unescaped &
            row_text = " ".join(current_cells)
            current_cells = []

            # Remove trailing \\
            row_text = row_text.rstrip()
            if row_text.endswith("\\\\"):
                row_text = row_text[:-2]

            # Split on & that is NOT preceded by \ (escaped ampersands in labels)
            # Replace \& with a sentinel, split on &, then restore sentinel.
            _SENTINEL = "\x00AMP\x00"
            row_text_safe = row_text.replace(r"\&", _SENTINEL)
            raw_parts = row_text_safe.split("&")
            parts = [p.replace(_SENTINEL, r"\&") for p in raw_parts]
            if len(parts) < 2:
                continue

            raw_label = _norm(parts[0])
            # Strip \textbf{} from label for comparison
            clean_label = re.sub(r"\\textbf\{([^}]+)\}", r"\1", raw_label).strip()
            if clean_label.lower() in _NON_CAPABILITY_ROWS:
                continue
            # Also skip header rows (e.g. the column-header row)
            if clean_label.lower() in {"capability", "\\textbf{capability}"}:
                continue
            label = clean_label

            cell_states = [_cell_state(p) for p in parts[1:]]
            rows.append((label, cell_states))

    return rows


# ── Evidence parser ───────────────────────────────────────────────────────────

def _parse_evidence(path: Path) -> dict[str, dict[str, str]]:
    """Parse the evidence file into a mapping of package → dimension → state.

    Parameters
    ----------
    path : Path
        Path to ``comparison_evidence.md``.

    Returns
    -------
    dict[str, dict[str, str]]
        Outer key: package section name (e.g. ``"scikit-fda"``).
        Inner key: normalized dimension label.
        Value: one of ``"checkmark"``, ``"partial"``, or ``"none"``.
    """
    text = path.read_text(encoding="utf-8")
    result: dict[str, dict[str, str]] = {}
    current_pkg: str | None = None
    in_claims = False

    for line in text.splitlines():
        # Package section header: ## <name> (not ###)
        m_pkg = re.match(r"^## +(.+)$", line)
        if m_pkg:
            raw_pkg = m_pkg.group(1).strip()
            # Skip sub-section headers that look like package names but aren't
            # (e.g. "## scikit-fda" is a top-level package section)
            current_pkg = raw_pkg
            in_claims = False
            if current_pkg not in result:
                result[current_pkg] = {}
            continue

        # Claims sub-section
        if re.match(r"^### +Claims", line):
            in_claims = True
            continue

        # Another ### sub-section resets claims mode
        if re.match(r"^### ", line) and not re.match(r"^### +Claims", line):
            in_claims = False
            continue

        # Parse claim table rows: | Dimension | Cell | ... |
        if in_claims and current_pkg and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            # parts[0] is empty (before first |), parts[-1] is empty (after last |)
            if len(parts) < 4:
                continue
            dim_raw = parts[1]
            cell_raw = parts[2]

            # Skip header and separator rows
            if not dim_raw or dim_raw.startswith("-") or dim_raw.lower() == "dimension":
                continue

            dim = _norm(dim_raw)
            if "checkmark" in cell_raw.lower() or cell_raw.strip() == "✓":
                state = "checkmark"
            elif "partial" in cell_raw.lower():
                state = "partial"
            else:
                state = "none"

            result[current_pkg][dim] = state

    return result


# ── Traceability check ────────────────────────────────────────────────────────

def _check(
    rows: list[tuple[str, list[str]]],
    evidence: dict[str, dict[str, str]],
) -> list[str]:
    """Return a sorted list of unsourced cell descriptions.

    Parameters
    ----------
    rows : list of (label, states)
        Parsed table rows from :func:`_parse_table`.
    evidence : dict
        Parsed evidence from :func:`_parse_evidence`.

    Returns
    -------
    list[str]
        Each entry describes one unsourced or state-mismatched cell:
        ``"UNSOURCED: <column> / <dimension> (<state>)"`` or
        ``"STATE_MISMATCH: <column> / <dimension> (table=checkmark, best_evidence=partial)"``.
    """
    misses: list[str] = []

    for dim_label, states in rows:
        # states[0] = fdars (skip), states[1..5] = peer families
        for col_idx, (col_name, member_pkgs) in enumerate(_PEER_COLS):
            # col_idx 0 → table states index 1+0 = 1 (fdars already in states[0])
            state_idx = col_idx + 1  # offset by 1 for fdars col
            if state_idx >= len(states):
                continue
            state = states[state_idx]
            if state not in ("checkmark", "partial"):
                continue

            # A family cell is evidenced if AT LEAST ONE member package has a
            # claim for this dimension with a non-none state.
            # Also track the *best* evidence state to detect STATE_MISMATCH when
            # the table shows checkmark but all evidence is only partial.
            evidenced = False
            best_state = "none"
            for pkg in member_pkgs:
                # Direct lookup
                ev_direct = evidence.get(pkg, {}).get(dim_label, "none")
                if ev_direct != "none":
                    evidenced = True
                    if ev_direct == "checkmark":
                        best_state = "checkmark"
                    elif ev_direct == "partial" and best_state != "checkmark":
                        best_state = "partial"
                # Case-insensitive and prefix match (e.g. "fda 6.3.0" for "fda")
                for ek, eclaims in evidence.items():
                    # Match if evidence section name equals pkg or starts with pkg
                    # (handles "fda 6.3.0" matching package key "fda")
                    ek_lower = ek.lower()
                    pkg_lower = pkg.lower()
                    if ek_lower == pkg_lower or ek_lower.startswith(pkg_lower + " "):
                        ev = eclaims.get(dim_label, "none")
                        if ev != "none":
                            evidenced = True
                            if ev == "checkmark":
                                best_state = "checkmark"
                            elif ev == "partial" and best_state != "checkmark":
                                best_state = "partial"

            if not evidenced:
                state_label = "checkmark" if state == "checkmark" else "partial"
                misses.append(f"UNSOURCED: {col_name} / {dim_label} ({state_label})")
            elif state == "checkmark" and best_state == "partial":
                # Table claims full support but every evidence entry is only partial —
                # this is a state-level mismatch: the evidence does not justify checkmark.
                misses.append(
                    f"STATE_MISMATCH: {col_name} / {dim_label} "
                    f"(table=checkmark, best_evidence=partial)"
                )

    return sorted(misses)


# ── fdars-column grounding check ─────────────────────────────────────────────

def _load_cap_map(path: Path) -> dict[str, list[object]]:
    """Load and return the capability map JSON.

    Parameters
    ----------
    path : Path
        Path to ``_capability_map.json``.

    Returns
    -------
    dict[str, list]
        Mapping of submodule key → list of callable entries.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def _check_fdars_grounding(
    rows: list[tuple[str, list[str]]],
    cap_map: dict[str, list[object]],
) -> tuple[list[str], list[str]]:
    """Verify that every fdars cell is ✓ and backed by the capability map.

    Parameters
    ----------
    rows : list of (label, states)
        Parsed table rows from :func:`_parse_table`.
        ``states[0]`` is the fdars cell state.
    cap_map : dict
        The loaded capability map from ``_capability_map.json``.

    Returns
    -------
    tuple[list[str], list[str]]
        ``(not_check_misses, ungrounded_misses)`` — both sorted.
        ``not_check_misses``: dimensions whose fdars cell is not ``\\checkmark``.
        ``ungrounded_misses``: dimensions that have no backing submodule with
        ≥1 public callable in the map.
    """
    not_check: list[str] = []
    ungrounded: list[str] = []

    for dim_label, states in rows:
        # states[0] = fdars cell
        fdars_state = states[0] if states else "none"

        # (a) fdars cell must be ✓
        if fdars_state != "checkmark":
            not_check.append(f"FDARS_NOT_CHECK: {dim_label}")

        # (b) grounding: at least one backing submodule has ≥1 public callable.
        # The map stores each submodule as a dict of {callable_name: metadata},
        # so public callables are keys that do not start with "_".
        submodules = DIMENSION_SUBMODULES.get(dim_label, ())
        grounded = False
        for mod in submodules:
            mod_entry = cap_map.get(mod)
            if not mod_entry:
                continue
            if isinstance(mod_entry, dict):
                public_count = sum(1 for k in mod_entry if not k.startswith("_"))
            else:
                # Defensive: treat as sequence of dicts with a "name" key
                public_count = sum(
                    1 for c in mod_entry
                    if not (isinstance(c, dict) and c.get("name", "").startswith("_"))
                )
            if public_count > 0:
                grounded = True
                break
        if not grounded:
            ungrounded.append(
                f"UNGROUNDED: {dim_label} (submodules={submodules})"
            )

    return sorted(not_check), sorted(ungrounded)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """Run the SC-3 traceability gate + COMP-02 fdars-grounding gate."""
    rows = _parse_table(_TABLE)
    evidence = _parse_evidence(_EVIDENCE)
    cap_map = _load_cap_map(_CAP_MAP)

    # SC-3 peer-traceability check
    misses = _check(rows, evidence)

    # COMP-02 fdars-grounding check
    not_check_misses, ungrounded_misses = _check_fdars_grounding(rows, cap_map)

    all_failures = sorted(misses) + sorted(not_check_misses) + sorted(ungrounded_misses)

    if all_failures:
        for failure in all_failures:
            print(failure, file=sys.stderr)
        sys.exit(1)

    print("COMPARISON_TRACE_OK")


if __name__ == "__main__":
    main()
