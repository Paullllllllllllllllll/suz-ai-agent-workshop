"""RIS export.

Converts ``CitationItem`` objects to the RIS 2001 tag format (CRLF line
endings, UTF-8). Harvested from CiteForge (export/ris.py); imports rewritten to
skill-local modules.

- ``item_to_ris`` -- convert a single item to an in-memory string.
- ``write_ris``   -- write a list of items to a file path.
"""

from __future__ import annotations

import re
from pathlib import Path

from export_types import ris_ty
from models import CitationItem

# Regex that matches a hyphen or en-dash used as a page-range separator.
_PAGE_SEP = re.compile(r"–|-")

# Two-space, hyphen, space separator used in every RIS line.
_SEP = "  - "


def _line(tag: str, value: str) -> str:
    """Format one ``TAG  - value`` line (no newline appended)."""
    return f"{tag}{_SEP}{value}"


def _split_pages(pages: str) -> tuple[str, str]:
    """Return (start, end) from a pages string."""
    parts = _PAGE_SEP.split(pages, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return pages.strip(), ""


def item_to_ris(item: CitationItem) -> str:
    """Convert a single ``CitationItem`` to a RIS record string (CRLF)."""
    lines: list[str] = []

    def add(tag: str, value: str) -> None:
        if value:
            lines.append(_line(tag, value))

    # --- TY (type) ---
    lines.append(_line("TY", ris_ty(item.item_type)))

    # --- contributors ---
    for creator in item.creators_by_role("author"):
        add("AU", creator.display())
    for creator in item.creators_by_role("editor"):
        add("A2", creator.display())
    for creator in item.creators_by_role("translator"):
        add("A4", creator.display())

    # --- titles ---
    add("TI", item.title)
    add("T2", item.container)

    # --- date ---
    if item.year is not None:
        add("PY", str(item.year))
    add("DA", item.date)

    # --- volume / issue ---
    add("VL", item.volume)
    add("IS", item.issue)

    # --- pages ---
    if item.pages:
        start, end = _split_pages(item.pages)
        add("SP", start)
        add("EP", end)

    # --- publication info ---
    add("PB", item.publisher)
    add("CY", item.place)

    # --- identifiers (ISBN preferred over ISSN) ---
    if item.isbn:
        add("SN", item.isbn)
    elif item.issn:
        add("SN", item.issn)

    # --- DOI: emit bare without "https://doi.org/" prefix ---
    if item.doi:
        doi = item.doi
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if doi.startswith(prefix):
                doi = doi[len(prefix) :]
                break
        add("DO", doi)

    add("UR", item.url)
    add("LA", item.language)
    add("ET", item.edition)

    # --- keywords (one tag per entry) ---
    for tag in item.tags:
        add("KW", tag)

    # --- abstract ---
    add("AB", item.abstract)

    # --- embedded identifiers ---
    lines.append(_line("N1", f"citekey: {item.key}; zotero: {item.zotero_key}"))

    # --- end-of-record ---
    lines.append(_line("ER", ""))

    return "\r\n".join(lines) + "\r\n"


def write_ris(items: list[CitationItem], path: str | Path) -> None:
    """Write *items* as RIS to *path* (UTF-8, CRLF)."""
    output = "\r\n".join(item_to_ris(item) for item in items)
    Path(path).write_text(output, encoding="utf-8", newline="")
