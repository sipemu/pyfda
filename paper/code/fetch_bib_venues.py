"""Fetch bibliographic venue metadata from Crossref into paper/code/bib_venues.json.

``python/fdars/_references_map.json`` records title/authors/year/DOI for each paper
but no venue (journal, volume, pages).  Without a venue every generated entry is an
``@misc`` and the rendered bibliography lacks journal names.  This script resolves
each DOI against the Crossref REST API **once, manually** and commits the result;
``gen_refs_bib.py`` then reads the overlay offline, so the paper build and the CI
drift gate stay network-free and deterministic.

Values are copied verbatim from Crossref (no hand-typing), so a venue is only ever
as good as the DOI registered for the paper.

Usage (network required)::

    python paper/code/fetch_bib_venues.py
"""
from __future__ import annotations

import html
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_REF_MAP = _REPO / "python" / "fdars" / "_references_map.json"
_OUT = Path(__file__).resolve().parent / "bib_venues.json"

# Crossref work type -> BibTeX entry type.
_TYPE_MAP = {
    "journal-article": "article",
    "book": "book",
    "monograph": "book",
    "edited-book": "book",
    "book-chapter": "incollection",
    "proceedings-article": "inproceedings",
}


def _crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(
        url, headers={"User-Agent": "fdars-paper-bib/1.0 (mailto:sm@data-zoo.de)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["message"]


def _venue(msg: dict) -> dict:
    etype = _TYPE_MAP.get(msg.get("type", ""), "misc")
    out: dict = {"entry_type": etype, "crossref_type": msg.get("type", "")}
    container = html.unescape((msg.get("container-title") or [""])[0])
    if etype == "article" and container:
        out["journal"] = container
    elif etype in ("incollection", "inproceedings") and container:
        out["booktitle"] = container
    for src, dst in (("volume", "volume"), ("issue", "number"), ("page", "pages")):
        if msg.get(src):
            out[dst] = str(msg[src]).replace("-", "--")
    if etype in ("book", "incollection") and msg.get("publisher"):
        out["publisher"] = html.unescape(msg["publisher"])
    return out


def main() -> None:
    papers = json.loads(_REF_MAP.read_text())["papers"]
    venues: dict = {}
    for key in sorted(papers):
        doi = (papers[key].get("doi") or "").strip()
        if key.startswith("_uncurated") or not doi:
            continue
        try:
            venues[key] = _venue(_crossref(doi))
            print(f"ok   {key}: {venues[key].get('journal') or venues[key].get('publisher') or venues[key]['entry_type']}")
        except Exception as exc:  # noqa: BLE001 -- report and continue
            print(f"FAIL {key} ({doi}): {exc}", file=sys.stderr)
        time.sleep(0.2)
    _OUT.write_text(json.dumps(venues, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"Wrote {_OUT} ({len(venues)} entries)")


if __name__ == "__main__":
    main()
