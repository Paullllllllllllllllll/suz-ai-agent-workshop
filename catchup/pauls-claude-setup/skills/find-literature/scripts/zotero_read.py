"""Read layer over the Zotero local HTTP API (port 23119).

Everything is read through Zotero's local API (Zotero must be running): item
metadata as clean CSL-JSON, and attachment file paths from the item's
children. The API returns ``linked_file`` paths already resolved to absolute
-- Zotero applies the linked-attachment base directory itself -- so reads stay
live and lock-free and never touch ``zotero.sqlite``.

Performance model: the local server's cost is per request, not per byte, it
does not cap ``limit``, and it serves requests concurrently. The layer
therefore minimizes round trips (one bulk CSL-JSON call per search instead of
one per hit) and issues the unavoidable per-item calls (attachment children)
in parallel. Always address ``127.0.0.1``: ``localhost`` first tries IPv6 and
adds ~2 s per call on Windows.

Environment overrides:
    ZOTERO_DATA_DIR        Zotero data directory (default ~/Zotero),
                           used to resolve imported (storage/) attachments
    ZOTERO_BASE_DIR        linked-attachment base dir; only a fallback for
                           ``attachments:`` relative paths the API leaves relative
    ZOTERO_LIBRARY_ID      library id (default "0")
    ZOTERO_LIBRARY_TYPE    "user" (default) or "group"
    ZOTERO_API_WORKERS     parallel request workers (default 8)
"""

from __future__ import annotations

import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from bibtex import make_citekey
from mapping import csl_to_item
from models import CitationItem

_NON_WORK_TYPES = frozenset({"attachment", "note", "annotation"})
_PAGE = 5000  # the local API does not cap page size; one call fetches the library
_LOCAL_API = "http://127.0.0.1:23119/api"


def _workers() -> int:
    try:
        return max(1, int(os.environ.get("ZOTERO_API_WORKERS", "8")))
    except ValueError:
        return 8


def _data_dir() -> Path:
    env = os.environ.get("ZOTERO_DATA_DIR")
    if env:
        return Path(env)
    return Path.home() / "Zotero"


def _storage_dir() -> Path:
    return _data_dir() / "storage"


def _base_dir() -> Path | None:
    """Resolve the Zotero linked-attachment base directory.

    Honors ``ZOTERO_BASE_DIR`` first, else reads
    ``extensions.zotero.baseAttachmentPath`` from the most recent profile
    ``prefs.js``. Only needed as a fallback: the local API normally returns
    linked paths already absolute.
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
        return None  # web link, no local file
    if link_mode in ("imported_file", "imported_url"):
        fname = d.get("filename") or (
            path[len("storage:") :] if path.startswith("storage:") else path
        )
        return str(storage / akey / fname) if fname else None
    # linked_file (or unknown): API usually gives an absolute path.
    if path.startswith("attachments:"):
        rel = path[len("attachments:") :]
        return str(base / rel) if base else path
    return path or None


# ---------------------------------------------------------------------------
# Local API client (httpx, HTTP/1.1-pinned)
# ---------------------------------------------------------------------------


class LocalApi:
    """Thin, thread-safe client for Zotero's local read API.

    Pinned to HTTP/1.1: Zotero's local server rejects HTTP/2 negotiation with
    502. ``httpx.Client`` is safe to share across threads, which the parallel
    helpers rely on.
    """

    def __init__(self) -> None:
        import httpx

        library_id = os.environ.get("ZOTERO_LIBRARY_ID", "0")
        library_type = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")
        prefix = "users" if library_type == "user" else "groups"
        self.base = f"{_LOCAL_API}/{prefix}/{library_id}"
        self._http = httpx.Client(
            transport=httpx.HTTPTransport(http1=True, http2=False),
            follow_redirects=True,
            timeout=60.0,
        )

    def get(self, path: str, **params) -> tuple[list | dict, int | None]:
        """GET ``<base>/<path>``; return (parsed JSON, Total-Results or None)."""
        clean = {k: v for k, v in params.items() if v is not None and v != ""}
        r = self._http.get(f"{self.base}/{path.lstrip('/')}", params=clean)
        r.raise_for_status()
        total = r.headers.get("Total-Results")
        return r.json(), (int(total) if total and total.isdigit() else None)

    def get_all(self, path: str, limit: int | None = None, **params) -> list:
        """Fetch a list endpoint up to *limit* rows (all rows when None).

        The first page reveals ``Total-Results``; the remaining pages are then
        requested concurrently.
        """
        page = _PAGE if limit is None else min(_PAGE, limit)
        first, total = self.get(path, limit=page, start=0, **params)
        rows = list(first) if isinstance(first, list) else []
        want = total if limit is None else min(total or 0, limit)
        if not want or len(rows) >= want:
            return rows[:want] if want else rows
        starts = list(range(page, want, page))

        def fetch(start: int) -> list:
            data, _ = self.get(path, limit=page, start=start, **params)
            return list(data) if isinstance(data, list) else []

        with ThreadPoolExecutor(max_workers=_workers()) as ex:
            for chunk in ex.map(fetch, starts):
                rows.extend(chunk)
        return rows[:want]

    def map(self, fn, keys: list[str]) -> list:
        """Apply *fn(key)* to every key concurrently, preserving order."""
        if not keys:
            return []
        with ThreadPoolExecutor(max_workers=_workers()) as ex:
            return list(ex.map(fn, keys))


def _client() -> LocalApi:
    return LocalApi()


def _norm_title(s: str | None) -> str:
    return re.sub(r"\W+", "", (s or "").lower())[:60]


def _csl_for(api: LocalApi, key: str) -> dict:
    """Fetch the CSL-JSON object for one item key (fallback path)."""
    res, _ = api.get(f"items/{key}", format="csljson")
    if isinstance(res, dict):
        if "items" in res:
            arr = res["items"]
            return arr[0] if arr else {}
        return res
    if isinstance(res, list):
        return res[0] if res else {}
    return {}


# ---------------------------------------------------------------------------
# Public read functions
# ---------------------------------------------------------------------------


def search(
    term: str,
    limit: int = 50,
    with_paths: bool = False,
    tags: list[str] | None = None,
) -> list[CitationItem]:
    """Search the library and return mapped ``CitationItem`` records.

    *term* is a quicksearch over title/creator/year (Zotero's default). *tags*
    is a list of exact tag names (e.g. ``["topic::migration", "region::europe"]``)
    that are AND-combined and combinable with *term*; the faceted controlled
    vocabulary applied by ``zotero-curator`` Mode C makes these the precise way to
    slice the library by topic, period, region, source-type, method, discipline,
    project, or language. An empty *term* with no *tags* returns the most recent
    top-level items (up to *limit*). Attachments and notes are excluded. When
    *with_paths* is true, each item's ``attachment_paths`` is resolved through
    the local API (its attachment children, fetched in parallel).

    Round trips: two list calls (Zotero JSON and CSL-JSON, run concurrently
    and aligned by an explicit ``dateAdded`` sort) plus, with *with_paths*,
    one children call per hit issued in parallel. Any hit whose CSL row does
    not align by title falls back to a single-item CSL fetch.
    """
    api = _client()
    tags = tags or []
    path = "items" if (term or tags) else "items/top"
    params: dict = {"sort": "dateAdded", "direction": "desc"}
    if term:
        params["q"] = term
    if tags:
        params["tag"] = tags

    with ThreadPoolExecutor(max_workers=2) as ex:
        f_json = ex.submit(api.get_all, path, limit, format="json", **params)
        f_csl = ex.submit(api.get_all, path, limit, format="csljson", **params)
        raw = f_json.result()
        csl_rows = f_csl.result()

    aligned = len(csl_rows) == len(raw)
    picked: list[tuple[str, dict, dict | None]] = []
    for idx, zj in enumerate(raw):
        data = zj.get("data", {}) if isinstance(zj, dict) else {}
        itype = data.get("itemType")
        if itype in _NON_WORK_TYPES:
            continue
        key = str(data.get("key") or zj.get("key") or "")
        if not key:
            continue
        csl = csl_rows[idx] if aligned and isinstance(csl_rows[idx], dict) else None
        if csl is not None and _norm_title(csl.get("title")) != _norm_title(
            data.get("title")
        ):
            csl = None
        picked.append((key, zj, csl))

    missing = [k for k, _, c in picked if c is None]
    if missing:
        fetched = dict(zip(missing, api.map(lambda k: _csl_for(api, k), missing)))
        picked = [
            (k, zj, c if c is not None else fetched.get(k, {})) for k, zj, c in picked
        ]

    paths_by_key: dict[str, list[str]] = {}
    if with_paths:
        keys = [k for k, _, _ in picked]
        paths_by_key = dict(
            zip(keys, api.map(lambda k: attachment_paths(k, api), keys))
        )

    items: list[CitationItem] = []
    for key, zj, csl in picked:
        csl = csl or {}
        item = csl_to_item(csl, zj, "")
        # Prefer the Better BibTeX citekey embedded in the CSL, then the CSL id,
        # then a derived AuthorYYYYword handle.
        citekey = str(csl.get("citation-key") or csl.get("id") or "").strip()
        item.key = citekey or make_citekey(item)
        item.csl_json = dict(csl)
        if not item.csl_json.get("id"):
            item.csl_json["id"] = item.key
        if with_paths:
            item.attachment_paths = paths_by_key.get(key, [])
        items.append(item)
    return items


def list_facet_tags(prefix: str | None = None, zot=None) -> list[str]:
    """Return the library's faceted tags (those containing ``::``), sorted.

    Filters to tags carrying the ``facet::value`` shape written by the
    ``zotero-curator`` Mode C vocabulary; free-form un-prefixed tags are skipped.
    Pass *prefix* (e.g. ``"region::"`` or ``"topic"``) to narrow to one facet.
    """
    api = zot if isinstance(zot, LocalApi) else _client()
    try:
        raw = api.get_all("tags", format="json")
    except Exception:  # noqa: BLE001
        return []
    out: list[str] = []
    for t in raw:
        name = (
            t
            if isinstance(t, str)
            else (t.get("tag", "") if isinstance(t, dict) else str(t))
        )
        if "::" not in name:
            continue
        if prefix and not name.startswith(prefix):
            continue
        out.append(name)
    return sorted(set(out))


def attachment_paths(zotero_key: str, zot=None) -> list[str]:
    """Return absolute file paths of *zotero_key*'s attachment children.

    Reads the item's children through the local API. Zotero resolves
    ``linked_file`` paths to absolute (applying its base directory), imported
    files resolve to ``storage/<key>/<filename>``, and web links are skipped.
    Pass an existing ``LocalApi`` as *zot* to reuse its connection pool.
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
