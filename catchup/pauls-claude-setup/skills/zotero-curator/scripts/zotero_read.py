"""Read layer for the curator scans over the Zotero local HTTP API.

Pulls every top-level work, and every attachment, as Zotero JSON in a single
call each: the local API (port 23119) does not cap ``limit``, so a whole
library of a few thousand records returns in well under a second. Only the
fields the scans need are extracted, so no CSL round trip is required. Zotero
must be running.

The server's cost is per request, not per byte, and it serves requests
concurrently; ``LocalApi.map`` fans unavoidable per-item calls out over a
thread pool. Always address ``127.0.0.1``: ``localhost`` first tries IPv6 and
adds ~2 s per call on Windows.

Environment overrides: ZOTERO_DATA_DIR (default ~/Zotero),
ZOTERO_BASE_DIR, ZOTERO_LIBRARY_ID (default "0"), ZOTERO_LIBRARY_TYPE
(default "user"), ZOTERO_API_WORKERS (default 8).
"""

from __future__ import annotations

import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

_NON_WORK_TYPES = frozenset({"attachment", "note", "annotation"})
_YEAR_RE = re.compile(r"\b(1[0-9]{3}|2[01][0-9]{2})\b")
_PAGE = 5000  # the local API does not cap page size; one call fetches the library
_LOCAL_API = "http://127.0.0.1:23119/api"


def _workers() -> int:
    try:
        return max(1, int(os.environ.get("ZOTERO_API_WORKERS", "8")))
    except ValueError:
        return 8


def _data_dir() -> Path:
    env = os.environ.get("ZOTERO_DATA_DIR")
    return Path(env) if env else Path.home() / "Zotero"


def _storage_dir() -> Path:
    return _data_dir() / "storage"


def _base_dir() -> Path | None:
    """Resolve the Zotero linked-attachment base directory (fallback only).

    Honors ``ZOTERO_BASE_DIR`` first, else reads
    ``extensions.zotero.baseAttachmentPath`` from the most recent profile
    ``prefs.js``. The local API normally returns linked paths already absolute.
    """
    env = os.environ.get("ZOTERO_BASE_DIR")
    if env:
        return Path(env)
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    candidates = sorted(
        glob.glob(
            os.path.join(appdata, "Zotero", "Zotero", "Profiles", "*", "prefs.js")
        ),
        key=os.path.getmtime,
        reverse=True,
    )
    pat = re.compile(
        r'user_pref\("extensions\.zotero\.baseAttachmentPath",\s*"(.*?)"\s*\)'
    )
    for prefs in candidates:
        try:
            with open(prefs, encoding="utf-8", errors="ignore") as fh:
                m = pat.search(fh.read())
        except OSError:
            continue
        if m:
            return Path(m.group(1).replace("\\\\", "\\"))
    return None


def _resolve_attachment(d: dict, storage: Path, base: Path | None) -> str | None:
    """Map one attachment ``data`` dict to an absolute file path, or None."""
    link_mode = d.get("linkMode")
    path = str(d.get("path") or "")
    akey = str(d.get("key") or "")
    if link_mode == "linked_url":
        return None
    if link_mode in ("imported_file", "imported_url"):
        fname = d.get("filename") or (
            path[len("storage:") :] if path.startswith("storage:") else path
        )
        return str(storage / akey / fname) if fname else None
    if path.startswith("attachments:"):
        rel = path[len("attachments:") :]
        return str(base / rel) if base else path
    return path or None


@dataclass(slots=True)
class Work:
    """A minimal top-level work record for duplicate detection."""

    key: str
    item_type: str
    title: str
    first_author: str
    authors: str
    year: int | None
    date: str
    collections: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "item_type": self.item_type,
            "title": self.title,
            "first_author": self.first_author,
            "authors": self.authors,
            "year": self.year,
            "date": self.date,
        }


class LocalApi:
    """Thin, thread-safe client for Zotero's local read API (HTTP/1.1 only)."""

    def __init__(self) -> None:
        import httpx

        library_id = os.environ.get("ZOTERO_LIBRARY_ID", "0")
        library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")
        prefix = "users" if library_type == "user" else "groups"
        self.base = f"{_LOCAL_API}/{prefix}/{library_id}"
        self._http = httpx.Client(
            transport=httpx.HTTPTransport(http1=True, http2=False),
            follow_redirects=True,
            timeout=120.0,
        )

    def get(self, path: str, **params) -> tuple[list | dict, int | None]:
        clean = {k: v for k, v in params.items() if v is not None and v != ""}
        r = self._http.get(f"{self.base}/{path.lstrip('/')}", params=clean)
        r.raise_for_status()
        total = r.headers.get("Total-Results")
        return r.json(), (int(total) if total and total.isdigit() else None)

    def get_all(self, path: str, **params) -> list:
        """Fetch every row of a list endpoint; extra pages, if any, in parallel."""
        first, total = self.get(path, limit=_PAGE, start=0, **params)
        rows = list(first) if isinstance(first, list) else []
        if not total or len(rows) >= total:
            return rows
        starts = list(range(_PAGE, total, _PAGE))

        def fetch(start: int) -> list:
            data, _ = self.get(path, limit=_PAGE, start=start, **params)
            return list(data) if isinstance(data, list) else []

        with ThreadPoolExecutor(max_workers=_workers()) as ex:
            for chunk in ex.map(fetch, starts):
                rows.extend(chunk)
        return rows

    def map(self, fn, keys: list[str]) -> list:
        if not keys:
            return []
        with ThreadPoolExecutor(max_workers=_workers()) as ex:
            return list(ex.map(fn, keys))


def _client() -> LocalApi:
    return LocalApi()


def _creator_names(data: dict) -> tuple[str, str]:
    """Return (first_author_lastname, 'A; B; C' summary) from item creators."""
    raw = data.get("creators")
    if not isinstance(raw, list):
        return "", ""
    names: list[str] = []
    first_author = ""
    for c in raw:
        if not isinstance(c, dict):
            continue
        last = str(c.get("lastName") or c.get("name") or "").strip()
        if not last:
            continue
        names.append(last)
        if not first_author and c.get("creatorType") in (None, "author"):
            first_author = last
    if not first_author and names:
        first_author = names[0]
    return first_author, "; ".join(names)


def _year_from_date(date: str) -> int | None:
    m = _YEAR_RE.search(date or "")
    return int(m.group(1)) if m else None


def all_items_raw() -> list[dict]:
    """Return the raw Zotero ``data`` dict for every non-deleted top-level work."""
    api = _client()
    out: list[dict] = []
    for zj in api.get_all("items/top", format="json"):
        data = zj.get("data", {}) if isinstance(zj, dict) else {}
        itype = str(data.get("itemType") or "")
        if itype in _NON_WORK_TYPES or not itype:
            continue
        if not str(data.get("key") or zj.get("key") or ""):
            continue
        out.append(data)
    return out


def all_works() -> list[Work]:
    """Return every non-deleted top-level work in the library."""
    works: list[Work] = []
    for data in all_items_raw():
        key = str(data.get("key") or "")
        date = str(data.get("date") or "").strip()
        first_author, authors = _creator_names(data)
        works.append(
            Work(
                key=key,
                item_type=str(data.get("itemType") or ""),
                title=str(data.get("title") or "").strip(),
                first_author=first_author,
                authors=authors,
                year=_year_from_date(date),
                date=date,
                collections=[str(c) for c in (data.get("collections") or []) if c],
            )
        )
    return works


def all_attachments_detailed() -> list[dict]:
    """One dict per resolvable child attachment, from a single API call::

        {"parent_key", "att_key", "path", "link_mode", "content_type"}

    Orphans and web links are skipped. ``link_mode`` tells whether a file is a
    linked file (renameable on disk) or an imported file (inside ``storage/``).
    """
    api = _client()
    storage = _storage_dir()
    base = _base_dir()
    out: list[dict] = []
    for c in api.get_all("items", format="json", itemType="attachment"):
        d = c.get("data", {}) if isinstance(c, dict) else {}
        parent = d.get("parentItem")
        if not parent:
            continue
        resolved = _resolve_attachment(d, storage, base)
        if not resolved:
            continue
        out.append(
            {
                "parent_key": str(parent),
                "att_key": str(d.get("key") or ""),
                "path": resolved,
                "link_mode": str(d.get("linkMode") or ""),
                "content_type": str(d.get("contentType") or ""),
            }
        )
    return out


def all_attachments() -> list[tuple[str, str]]:
    """Return (parent_key, absolute_path) for every resolvable attachment."""
    return [(a["parent_key"], a["path"]) for a in all_attachments_detailed()]


def attachment_paths_map() -> dict[str, list[str]]:
    """Return {parent_key: [absolute paths]} for the whole library in one call.

    Prefer this over ``attachment_paths`` whenever more than a handful of
    works need their files resolved.
    """
    out: dict[str, list[str]] = {}
    for a in all_attachments_detailed():
        out.setdefault(a["parent_key"], []).append(a["path"])
    return out


def attachment_paths(zotero_key: str, zot=None) -> list[str]:
    """Return absolute file paths of one item's attachment children.

    One API call per item; pass an existing ``LocalApi`` as *zot* to reuse its
    connection pool, or use ``attachment_paths_map`` for bulk resolution.
    """
    api = zot if isinstance(zot, LocalApi) else _client()
    try:
        kids, _ = api.get(f"items/{zotero_key}/children", format="json")
    except Exception:  # noqa: BLE001
        return []
    storage = _storage_dir()
    base = _base_dir()
    out: list[str] = []
    for c in kids if isinstance(kids, list) else []:
        d = c.get("data", {}) if isinstance(c, dict) else {}
        if d.get("itemType") != "attachment":
            continue
        resolved = _resolve_attachment(d, storage, base)
        if resolved:
            out.append(resolved)
    return out
