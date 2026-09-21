"""BibTeX and CSL-JSON serialization for ``CitationItem``.

Self-contained (stdlib only). BibTeX entry-type mapping mirrors the RIS/EndNote
tables in ``export_types``; the citekey generator produces a stable
``AuthorYYYYword`` handle when Better BibTeX is unavailable (the common case
here, since the local BBT key store is empty).
"""

from __future__ import annotations

import json
import re
import unicodedata

from models import CitationItem

# Zotero item_type -> BibTeX entry type.
_BIBTEX_TYPE: dict[str, str] = {
    "journalArticle": "article",
    "book": "book",
    "bookSection": "incollection",
    "conferencePaper": "inproceedings",
    "thesis": "phdthesis",
    "report": "techreport",
    "manuscript": "unpublished",
    "magazineArticle": "article",
    "newspaperArticle": "article",
    "webpage": "misc",
    "blogPost": "misc",
    "patent": "patent",
}
_DEFAULT_BIBTEX_TYPE = "misc"


def _ascii_slug(text: str) -> str:
    """Lower-case ASCII-only token (letters/digits) from *text*."""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]", "", norm)


def make_citekey(item: CitationItem) -> str:
    """Derive a ``AuthorYYYYword`` citekey from author, year, and title.

    Used when ``item.key`` is empty or not a usable handle. Deterministic.
    """
    authors = item.authors
    if authors:
        first = authors[0].last or authors[0].literal
    else:
        first = ""
    author_part = _ascii_slug(first) or "anon"
    year_part = str(item.year) if item.year else "nd"
    title_word = ""
    for tok in item.title.split():
        slug = _ascii_slug(tok)
        if len(slug) > 3:  # skip short stopwords-ish tokens
            title_word = slug.lower()
            break
    return f"{author_part}{year_part}{title_word}"


def _bibtex_names(creators: list) -> str:
    """Join creators with ' and ' in BibTeX ``Last, First`` form."""
    out = []
    for c in creators:
        if c.is_literal:
            out.append(f"{{{c.literal}}}")
        elif c.first:
            out.append(f"{c.last}, {c.first}")
        else:
            out.append(c.last)
    return " and ".join(out)


def _escape(value: str) -> str:
    """Minimal BibTeX escaping for special characters."""
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("$", r"\$")
    )


def item_to_bibtex(item: CitationItem, citekey: str | None = None) -> str:
    """Render *item* as a single BibTeX entry string."""
    entry_type = _BIBTEX_TYPE.get(item.item_type, _DEFAULT_BIBTEX_TYPE)
    key = citekey or item.key or make_citekey(item)

    fields: list[tuple[str, str]] = []
    authors = item.creators_by_role("author")
    editors = item.creators_by_role("editor")
    if authors:
        fields.append(("author", _bibtex_names(authors)))
    if editors:
        fields.append(("editor", _bibtex_names(editors)))
    if item.title:
        fields.append(("title", _escape(item.title)))
    if item.container:
        field_name = "booktitle" if entry_type == "incollection" else "journal"
        fields.append((field_name, _escape(item.container)))
    if item.year is not None:
        fields.append(("year", str(item.year)))
    if item.volume:
        fields.append(("volume", item.volume))
    if item.issue:
        fields.append(("number", item.issue))
    if item.pages:
        fields.append(("pages", item.pages.replace("-", "--")))
    if item.publisher:
        fields.append(("publisher", _escape(item.publisher)))
    if item.place:
        fields.append(("address", _escape(item.place)))
    if item.edition:
        fields.append(("edition", _escape(item.edition)))
    if item.series:
        fields.append(("series", _escape(item.series)))
    if item.doi:
        fields.append(("doi", item.doi))
    if item.isbn:
        fields.append(("isbn", item.isbn))
    if item.issn:
        fields.append(("issn", item.issn))
    if item.url:
        fields.append(("url", item.url))
    if item.language:
        fields.append(("language", item.language))

    body = ",\n".join(f"  {name} = {{{value}}}" for name, value in fields)
    return f"@{entry_type}{{{key},\n{body}\n}}"


def items_to_bibtex(items: list[CitationItem]) -> str:
    """Render *items* as a BibTeX file body."""
    return "\n\n".join(item_to_bibtex(it) for it in items) + "\n"


def items_to_csljson(items: list[CitationItem]) -> str:
    """Return the CSL-JSON array (the authoritative payload) for *items*."""
    return json.dumps([it.csl_json for it in items], ensure_ascii=False, indent=2)
