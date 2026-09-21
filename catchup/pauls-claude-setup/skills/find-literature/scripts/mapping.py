"""Pure mapping functions: Zotero + CSL-JSON -> CitationItem.

No network calls; no side effects. Harvested from CiteForge (zotero/mapping.py);
``from core.models`` rewritten to the skill-local ``models`` module.
"""

from __future__ import annotations

from models import CitationItem, Creator


def csl_names_to_creators(
    csl: dict[str, object],
    field: str,
    role: str,
) -> list[Creator]:
    """Convert CSL name objects from *csl[field]* into ``Creator`` instances."""
    raw = csl.get(field)
    if not isinstance(raw, list):
        return []
    out: list[Creator] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        literal = str(entry.get("literal", "")).strip()
        if literal:
            out.append(Creator(literal=literal, role=role))
            continue
        family = str(entry.get("family", "")).strip()
        given = str(entry.get("given", "")).strip()
        if not family and not given:
            continue
        out.append(Creator(last=family, first=given, role=role))
    return out


def _year_from_csl(csl: dict[str, object]) -> int | None:
    """Extract the four-digit year from the CSL ``issued`` field."""
    issued = csl.get("issued")
    if not isinstance(issued, dict):
        return None
    dp = issued.get("date-parts")
    if isinstance(dp, list) and dp and isinstance(dp[0], list):
        parts = dp[0]
        if parts:
            try:
                return int(parts[0])
            except (ValueError, TypeError):
                return None
    raw = issued.get("raw")
    if isinstance(raw, str) and len(raw) >= 4:
        try:
            return int(raw[:4])
        except ValueError:
            return None
    literal = issued.get("literal")
    if isinstance(literal, str) and len(literal) >= 4:
        try:
            return int(literal[:4])
        except ValueError:
            return None
    return None


def _date_str_from_csl(csl: dict[str, object]) -> str:
    """Build a human-readable date string from the CSL ``issued`` field."""
    issued = csl.get("issued")
    if not isinstance(issued, dict):
        return ""
    dp = issued.get("date-parts")
    if isinstance(dp, list) and dp and isinstance(dp[0], list):
        parts = [str(p) for p in dp[0] if str(p).strip()]
        if len(parts) >= 2:
            parts[1] = parts[1].zfill(2)
        if len(parts) >= 3:
            parts[2] = parts[2].zfill(2)
        return "-".join(parts)
    raw = issued.get("raw")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    literal = issued.get("literal")
    if isinstance(literal, str) and literal.strip():
        return literal.strip()
    return ""


def csl_to_item(
    csl: dict[str, object],
    zotero_json: dict[str, object],
    citekey: str,
) -> CitationItem:
    """Build a ``CitationItem`` from a CSL-JSON object, a pyzotero item, and a citekey."""
    data: dict[str, object] = {}
    raw_data = zotero_json.get("data")
    if isinstance(raw_data, dict):
        data = raw_data

    zotero_key = str(data.get("key") or zotero_json.get("key") or "")
    raw_version = data.get("version") or 0
    version = int(raw_version) if isinstance(raw_version, int | str) else 0
    item_type = str(data.get("itemType") or "document")

    title = str(csl.get("title") or "").strip()

    creators: list[Creator] = []
    creators += csl_names_to_creators(csl, "author", "author")
    creators += csl_names_to_creators(csl, "editor", "editor")
    creators += csl_names_to_creators(csl, "translator", "translator")

    year = _year_from_csl(csl)
    date = _date_str_from_csl(csl)

    container = str(csl.get("container-title") or "").strip()
    publisher = str(csl.get("publisher") or "").strip()
    place = str(csl.get("publisher-place") or "").strip()
    volume = str(csl.get("volume") or "").strip()
    issue = str(csl.get("issue") or "").strip()
    pages = str(csl.get("page") or "").strip()
    doi = str(csl.get("DOI") or "").strip()
    isbn = str(csl.get("ISBN") or "").strip()
    issn = str(csl.get("ISSN") or "").strip()
    url = str(csl.get("URL") or "").strip()
    language = str(csl.get("language") or "").strip()
    edition = str(csl.get("edition") or "").strip()
    series = str(csl.get("collection-title") or "").strip()
    abstract = str(csl.get("abstract") or "").strip()

    raw_tags = data.get("tags")
    tags: list[str] = []
    if isinstance(raw_tags, list):
        for t in raw_tags:
            if isinstance(t, dict):
                tag_val = t.get("tag")
                if isinstance(tag_val, str) and tag_val.strip():
                    tags.append(tag_val.strip())

    raw_collections = data.get("collections")
    collections: list[str] = []
    if isinstance(raw_collections, list):
        collections = [str(c) for c in raw_collections if c]

    date_added = str(data.get("dateAdded") or "").strip()
    date_modified = str(data.get("dateModified") or "").strip()

    return CitationItem(
        key=citekey,
        zotero_key=zotero_key,
        version=version,
        item_type=item_type,
        title=title,
        creators=creators,
        year=year,
        date=date,
        container=container,
        publisher=publisher,
        place=place,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        isbn=isbn,
        issn=issn,
        url=url,
        language=language,
        edition=edition,
        series=series,
        abstract=abstract,
        tags=tags,
        collections=collections,
        csl_json=dict(csl),
        date_added=date_added,
        date_modified=date_modified,
    )
