"""EndNote XML export.

Converts ``CitationItem`` objects to the EndNote 9 XML format understood by
EndNote 2025 and older. Harvested from CiteForge (export/endnote_xml.py);
imports rewritten to skill-local modules.

- ``item_to_record``    -- single item to an ``ElementTree.Element``.
- ``write_endnote_xml`` -- a list of items to an ``<xml><records>`` document.
"""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from export_types import endnote_reftype
from models import CitationItem

# Item types that carry a periodical and therefore also need a
# <periodical><full-title> element.
_PERIODICAL_TYPES: frozenset[str] = frozenset(
    {"journalArticle", "magazineArticle", "newspaperArticle"}
)


def _sub(parent: ET.Element, tag: str, text: str) -> ET.Element:
    """Append a child element with *text* content and return it."""
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


def item_to_record(item: CitationItem) -> ET.Element:
    """Return a ``<record>`` element for *item* (DTD element order)."""
    record = ET.Element("record")

    # --- ref-type (REQUIRED name attribute) ---
    has_authors = bool(item.creators_by_role("author"))
    code, name = endnote_reftype(item.item_type, has_authors=has_authors)
    rt = ET.SubElement(record, "ref-type")
    rt.set("name", name)
    rt.text = str(code)

    # --- contributors ---
    authors = item.creators_by_role("author")
    editors = item.creators_by_role("editor")
    translators = item.creators_by_role("translator")

    if authors or editors or translators:
        contributors = ET.SubElement(record, "contributors")
        if authors:
            authors_el = ET.SubElement(contributors, "authors")
            for c in authors:
                _sub(authors_el, "author", c.display())
        if editors:
            sec_authors = ET.SubElement(contributors, "secondary-authors")
            for c in editors:
                _sub(sec_authors, "author", c.display())
        if translators:
            sub_authors = ET.SubElement(contributors, "subsidiary-authors")
            for c in translators:
                _sub(sub_authors, "author", c.display())

    # --- titles ---
    titles = ET.SubElement(record, "titles")
    if item.title:
        _sub(titles, "title", item.title)
    if item.container:
        _sub(titles, "secondary-title", item.container)

    # --- periodical (journal/magazine/newspaper only) ---
    if item.container and item.item_type in _PERIODICAL_TYPES:
        periodical = ET.SubElement(record, "periodical")
        _sub(periodical, "full-title", item.container)

    # --- pages, volume, number (DTD order) ---
    if item.pages:
        _sub(record, "pages", item.pages)
    if item.volume:
        _sub(record, "volume", item.volume)
    if item.issue:
        _sub(record, "number", item.issue)

    # --- edition ---
    if item.edition:
        _sub(record, "edition", item.edition)

    # --- keywords ---
    if item.tags:
        keywords = ET.SubElement(record, "keywords")
        for tag in item.tags:
            _sub(keywords, "keyword", tag)

    # --- dates ---
    if item.year is not None:
        dates = ET.SubElement(record, "dates")
        _sub(dates, "year", str(item.year))

    # --- publisher location / publisher ---
    if item.place:
        _sub(record, "pub-location", item.place)
    if item.publisher:
        _sub(record, "publisher", item.publisher)

    # --- isbn ---
    if item.isbn:
        _sub(record, "isbn", item.isbn)
    elif item.issn:
        _sub(record, "isbn", item.issn)

    # --- abstract ---
    if item.abstract:
        _sub(record, "abstract", item.abstract)

    # --- language ---
    if item.language:
        _sub(record, "language", item.language)

    # --- urls ---
    if item.url:
        urls = ET.SubElement(record, "urls")
        web_urls = ET.SubElement(urls, "web-urls")
        _sub(web_urls, "url", item.url)

    # --- custom1: embedded identifiers ---
    _sub(record, "custom1", f"citekey: {item.key}; zotero: {item.zotero_key}")

    # --- electronic-resource-num (DOI) ---
    if item.doi:
        _sub(record, "electronic-resource-num", item.doi)

    return record


def write_endnote_xml(items: list[CitationItem], path: str | Path) -> None:
    """Write *items* as an EndNote XML document to *path* (UTF-8)."""
    root = ET.Element("xml")
    records = ET.SubElement(root, "records")
    for item in items:
        records.append(item_to_record(item))

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(
        str(Path(path)),
        encoding="utf-8",
        xml_declaration=True,
    )


def endnote_xml_string(items: list[CitationItem]) -> str:
    """Return the EndNote XML document for *items* as a string."""
    root = ET.Element("xml")
    records = ET.SubElement(root, "records")
    for item in items:
        records.append(item_to_record(item))
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")
