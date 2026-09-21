"""zotero-curator authoritative metadata lookup (OpenAlex + Crossref).

Deterministic retrieval of bibliographic metadata from live scholarly catalogs so
the Mode B / Mode D subagents NEVER invent a DOI, year, venue, or author list from
memory. Given a DOI or a free-text query (title, optionally author/year), it queries
OpenAlex first and Crossref as an independent cross-check, then maps each candidate
to Zotero field names. The subagent compares these candidates against the PDF's
title page (the ground truth) and adopts only fields an authority confirms.

Both APIs are free and need no key; set ``CONTACT_EMAIL`` to send an identifying
``mailto`` and join the "polite pool". Network failures degrade to an empty
candidate list with a note --
the subagent must then fall back to reading the PDF and a manual catalog search,
and must still not guess.

Usage::

    python scripts/fetch_metadata.py --doi 10.3386/w34777
    python scripts/fetch_metadata.py --query "AI and the Quality of Creative Products" \
        --author Waldfogel --year 2026
    python scripts/fetch_metadata.py --query "..." --source openalex   # one source only

Output: JSON ``{"candidates": [...], "notes": [...]}`` on stdout (and to --out).
Each candidate carries ``source``, ``match``, a Zotero-mapped ``fields`` dict,
``creators`` (first/last split), ``itemType``, and the raw record id/doi so the
agent can verify against the document.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Optional contact address for the OpenAlex/Crossref "polite pool".
_MAILTO = os.environ.get("CONTACT_EMAIL", "").strip()
_POLITE: dict = {"mailto": _MAILTO} if _MAILTO else {}
_TIMEOUT = 20.0

# OpenAlex / Crossref work types -> Zotero item types.
_TYPE_MAP = {
    "article": "journalArticle",
    "journal-article": "journalArticle",
    "preprint": "preprint",
    "posted-content": "preprint",
    "report": "report",
    "working-paper": "report",
    "book": "book",
    "monograph": "book",
    "reference-book": "book",
    "edited-book": "book",
    "book-chapter": "bookSection",
    "book-section": "bookSection",
    "book-part": "bookSection",
    "proceedings-article": "conferencePaper",
    "dissertation": "thesis",
    "dataset": "dataset",
    "paratext": "document",
    "other": "document",
}

# Zotero item type -> the field that carries the container/venue title.
_CONTAINER_FIELD = {
    "journalArticle": "publicationTitle",
    "conferencePaper": "proceedingsTitle",
    "bookSection": "bookTitle",
}


def _client():
    import httpx

    return httpx.Client(
        timeout=_TIMEOUT,
        follow_redirects=True,
        headers={
            "User-Agent": f"zotero-curator (mailto:{_MAILTO})"
            if _MAILTO
            else "zotero-curator"
        },
    )


def _bare_doi(doi: str | None) -> str:
    if not doi:
        return ""
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", str(doi).strip(), flags=re.I)


def _split_name(display: str) -> tuple[str, str]:
    """Naive first/last split of a display name; the subagent verifies against the PDF."""
    parts = (display or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return "", parts[0]
    return " ".join(parts[:-1]), parts[-1]


def _zotero_type(raw_type: str | None) -> str:
    return _TYPE_MAP.get(str(raw_type or "").lower(), "document")


# --------------------------------------------------------------------------- #
# OpenAlex
# --------------------------------------------------------------------------- #
def _openalex_to_candidate(work: dict) -> dict:
    item_type = _zotero_type(work.get("type"))
    creators = []
    for a in work.get("authorships") or []:
        name = (a.get("author") or {}).get("display_name") or a.get("raw_author_name")
        if not name:
            continue
        first, last = _split_name(name)
        creators.append({"creatorType": "author", "firstName": first, "lastName": last})

    loc = work.get("primary_location") or {}
    source = loc.get("source") or {}
    venue = source.get("display_name") or ""
    publisher = source.get("host_organization_name") or ""

    fields: dict = {"title": work.get("title") or work.get("display_name") or ""}
    if work.get("publication_date"):
        fields["date"] = work["publication_date"]
    elif work.get("publication_year"):
        fields["date"] = str(work["publication_year"])
    doi = _bare_doi(work.get("doi"))
    if doi:
        fields["DOI"] = doi
    if work.get("language"):
        fields["language"] = work["language"]
    url = loc.get("landing_page_url") or (f"https://doi.org/{doi}" if doi else "")
    if url:
        fields["url"] = url
    if venue:
        fields[_CONTAINER_FIELD.get(item_type, "publicationTitle")] = venue
    if publisher:
        fields["publisher" if item_type != "journalArticle" else "publisher"] = (
            publisher
        )
    biblio = work.get("biblio") or {}
    if biblio.get("volume"):
        fields["volume"] = biblio["volume"]
    if biblio.get("issue"):
        fields["issue"] = biblio["issue"]
    if biblio.get("first_page"):
        last_pg = biblio.get("last_page")
        fields["pages"] = (
            f"{biblio['first_page']}-{last_pg}" if last_pg else biblio["first_page"]
        )

    return {
        "source": "openalex",
        "id": work.get("id"),
        "itemType": item_type,
        "raw_type": work.get("type"),
        "fields": fields,
        "creators": creators,
    }


def _query_openalex(client, doi: str, query: str, per_page: int) -> list[dict]:
    if doi:
        url = f"https://api.openalex.org/works/doi:{doi}"
        r = client.get(url, params=_POLITE)
        if r.status_code == 200:
            return [_openalex_to_candidate(r.json())]
        return []
    params = {
        "search": query,
        "per-page": per_page,
        **_POLITE,
        "select": (
            "id,doi,title,display_name,publication_year,publication_date,type,"
            "language,authorships,primary_location,biblio"
        ),
    }
    r = client.get("https://api.openalex.org/works", params=params)
    if r.status_code != 200:
        return []
    return [_openalex_to_candidate(w) for w in (r.json().get("results") or [])]


# --------------------------------------------------------------------------- #
# Crossref (independent cross-check; gives explicit given/family names)
# --------------------------------------------------------------------------- #
def _crossref_to_candidate(item: dict) -> dict:
    item_type = _zotero_type(item.get("type"))
    creators = []
    for a in item.get("author") or []:
        first = a.get("given") or ""
        last = a.get("family") or a.get("name") or ""
        if not (first or last):
            continue
        creators.append({"creatorType": "author", "firstName": first, "lastName": last})

    title = (item.get("title") or [""])[0]
    fields: dict = {"title": title}
    issued = (item.get("issued") or {}).get("date-parts") or [[]]
    if issued and issued[0]:
        fields["date"] = "-".join(str(p) for p in issued[0])
    doi = _bare_doi(item.get("DOI"))
    if doi:
        fields["DOI"] = doi
        fields["url"] = f"https://doi.org/{doi}"
    container = (item.get("container-title") or [""])[0]
    if container:
        fields[_CONTAINER_FIELD.get(item_type, "publicationTitle")] = container
    if item.get("publisher"):
        fields["publisher"] = item["publisher"]
    if item.get("volume"):
        fields["volume"] = item["volume"]
    if item.get("issue"):
        fields["issue"] = item["issue"]
    if item.get("page"):
        fields["pages"] = item["page"]
    if item.get("language"):
        fields["language"] = item["language"]

    return {
        "source": "crossref",
        "id": doi,
        "itemType": item_type,
        "raw_type": item.get("type"),
        "fields": fields,
        "creators": creators,
    }


def _query_crossref(client, doi: str, query: str, author: str, rows: int) -> list[dict]:
    if doi:
        r = client.get(f"https://api.crossref.org/works/{doi}", params=_POLITE)
        if r.status_code == 200:
            return [_crossref_to_candidate(r.json().get("message") or {})]
        return []
    params: dict = {"rows": rows, **_POLITE, "query.bibliographic": query}
    if author:
        params["query.author"] = author
    r = client.get("https://api.crossref.org/works", params=params)
    if r.status_code != 200:
        return []
    items = ((r.json().get("message") or {}).get("items")) or []
    return [_crossref_to_candidate(it) for it in items]


def lookup(
    doi: str = "",
    query: str = "",
    author: str = "",
    year: str = "",
    source: str = "both",
    limit: int = 5,
) -> dict:
    doi = _bare_doi(doi)
    if query and year and year not in query:
        query = f"{query} {year}"
    candidates: list[dict] = []
    notes: list[str] = []
    client = _client()
    try:
        if source in ("both", "openalex"):
            try:
                candidates += _query_openalex(client, doi, query, limit)
            except Exception as exc:  # noqa: BLE001
                notes.append(f"OpenAlex lookup failed: {exc}")
        if source in ("both", "crossref"):
            try:
                candidates += _query_crossref(client, doi, query, author, limit)
            except Exception as exc:  # noqa: BLE001
                notes.append(f"Crossref lookup failed: {exc}")
    finally:
        client.close()
    if not candidates and not notes:
        notes.append(
            "no matches; read the PDF and search a catalog manually -- do not guess"
        )
    return {
        "query": {"doi": doi, "query": query, "author": author, "year": year},
        "candidates": candidates,
        "notes": notes,
    }


def main(argv: list[str] | None = None) -> int:
    for _stream in (sys.stdout, sys.stderr):
        rec = getattr(_stream, "reconfigure", None)
        if rec is not None:
            try:
                rec(encoding="utf-8")
            except Exception:  # noqa: BLE001
                pass

    parser = argparse.ArgumentParser(
        description="Look up authoritative metadata from OpenAlex + Crossref."
    )
    parser.add_argument("--doi", default="", help="exact DOI (skips the text search)")
    parser.add_argument("--query", default="", help="title / bibliographic text")
    parser.add_argument(
        "--author", default="", help="an author surname (narrows search)"
    )
    parser.add_argument("--year", default="", help="publication year (narrows search)")
    parser.add_argument(
        "--source", choices=["both", "openalex", "crossref"], default="both"
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="max candidates per source"
    )
    parser.add_argument("--out", default="", help="also write the JSON result here")
    args = parser.parse_args(argv)

    if not args.doi and not args.query:
        sys.stderr.write("error: pass --doi or --query.\n")
        return 2

    result = lookup(
        doi=args.doi,
        query=args.query,
        author=args.author,
        year=args.year,
        source=args.source,
        limit=args.limit,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload)
    sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
