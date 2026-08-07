#!/usr/bin/env python3
"""A+ documentation scorecard for the fdars docs.

Checks every content page (learn/represent/align/regression/monitoring/analyze/
examples) against the mechanically-checkable A+ criteria and prints a per-page
checklist + summary. Substance-oriented where possible (e.g. every figure needs a
nearby interpretive sentence, every documented function wants a table).

Usage:
    python scripts/a_plus_scorecard.py              # report
    python scripts/a_plus_scorecard.py --gate       # exit 1 if any page is not A+
    python scripts/a_plus_scorecard.py --md file    # single file

A+ (mechanical) = ALL hard criteria pass. Coverage-vs-R and figure-interpretation
quality still warrant human/agent review; this gate stops regressions and padding.
"""
from __future__ import annotations
import argparse, glob, re, sys

SECTIONS = ("learn", "represent", "align", "regression", "monitoring", "analyze", "examples")


def check(path: str) -> dict:
    t = open(path).read()
    figs = len(re.findall(r"print\(render\(", t))
    # each exec figure block should have prose within ~2 lines after it
    exec_blocks = re.findall(r'```python exec="1".*?```', t, re.S)
    math = t.count("$$") // 2
    refs_hdr = bool(re.search(r"##+\s*References", t))
    refs_n = len(re.findall(r"\(\d{4}[a-z]?\)", t.split("References", 1)[-1])) if refs_hdr else 0
    table = bool(re.search(r"\n\|[^\n]*\|\n\|[ :|-]+\|", t))
    validation = bool(re.search(r"\bassert\b|match(?:es)? R\b|reproduc|R.reference|vs\.? R\b|ground truth", t, re.I))
    crosslink = bool(re.search(r"##+\s*See also|\]\(\.\./", t))
    # deterministic: uses a real dataset, seeds its RNG, or draws no randomness at all
    uses_rng = bool(re.search(r"np\.random|default_rng|rand", t))
    real = bool(re.search(r"load_(growth|canadian_weather|tecator|phoneme|wine|sonar|penicillin)", t))
    seeded = real or (not uses_rng) or bool(
        re.search(r"default_rng\(\d|seed\s*=\s*\d|np\.random\.seed\(\d", t))
    # every figure block should have a nearby interpretive sentence (prose within 3 lines after the fence)
    interp = True
    for mobj in re.finditer(r'```python exec="1".*?```', t, re.S):
        after = t[mobj.end():mobj.end() + 240].lstrip("\n")
        if not re.match(r"[A-Za-z*`]", after):   # next non-blank should be prose, not another fence/heading
            interp = False; break
    diagram = "assets/diagrams/" in t

    hard = {
        ">=5 figures": figs >= 5,
        "figures interpreted": interp,
        "math ($$>=2)": math >= 2,
        ">=3 references": refs_n >= 3,
        "numeric validation": validation,
        "param/return table": table,
        "cross-links": crosslink,
        "deterministic": seeded,
    }
    soft = {"concept diagram": diagram, "figures": figs, "refs": refs_n, "math": math}
    return {"path": path, "hard": hard, "soft": soft, "a_plus": all(hard.values())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="exit 1 if any page is not A+")
    ap.add_argument("--md", help="check a single file")
    a = ap.parse_args()

    paths = ([a.md] if a.md else sorted(
        p for p in glob.glob("docs/**/*.md", recursive=True)
        if not p.endswith("index.md") and "assets" not in p
        and any(f"docs/{s}/" in p for s in SECTIONS)))

    results = [check(p) for p in paths]
    npass = sum(r["a_plus"] for r in results)
    print(f"A+ scorecard — {npass}/{len(results)} pages meet all hard criteria\n")
    fails = [r for r in results if not r["a_plus"]]
    for r in sorted(fails, key=lambda r: sum(r["hard"].values())):
        miss = [k for k, v in r["hard"].items() if not v]
        print(f"  ✗ {r['path'][5:]:44} missing: {', '.join(miss)}")
    if not fails:
        print("  ✓ all pages A+")
    # aggregate criterion coverage
    print("\ncriterion coverage:")
    for k in results[0]["hard"]:
        c = sum(r["hard"][k] for r in results)
        print(f"  {k:22} {c:2}/{len(results)}")
    if a.gate and fails:
        print(f"\nGATE FAILED: {len(fails)} page(s) below A+.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
