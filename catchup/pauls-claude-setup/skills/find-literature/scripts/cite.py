"""find-literature CLI: search the Zotero library and emit citations.

Usage
-----
    python scripts/cite.py "<search term>" [options]

Options
    --format {chicago,bibtex,csljson,ris,endnote,all}   default: chicago
    --with-paths        append absolute attachment file paths per hit
    --limit N           max results (default 50)
    --out FILE          write the chosen format to FILE instead of stdout
                        (ris/endnote/bibtex/csljson/chicago-bibliography)

Requires Zotero running (local API on port 23119). Run from the skill venv:
    uv run python scripts/cite.py "Bourdieu" --format all

If the API is down, the script starts Zotero from its default install location
(Windows, macOS) or from ``zotero`` on PATH; set ZOTERO_EXE to override.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

import bibtex as bib
import endnote_xml
import ris
from models import CitationItem
from render import ChicagoRenderer
from zotero_read import list_facet_tags, search

# Windows consoles default to cp1252; bibliographic data carries non-Latin-1
# characters (umlauts, accents, dashes).
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass


def _zotero_exe() -> str | None:
    """Return the Zotero executable to auto-start, or None if not found.

    ``ZOTERO_EXE`` overrides the per-OS default install location.
    """
    env = os.environ.get("ZOTERO_EXE")
    if env:
        return env if Path(env).exists() else None
    if sys.platform == "win32":
        exe = Path(r"C:\Program Files\Zotero\zotero.exe")
        return str(exe) if exe.exists() else None
    if sys.platform == "darwin":
        exe = Path("/Applications/Zotero.app/Contents/MacOS/zotero")
        return str(exe) if exe.exists() else None
    return shutil.which("zotero")


_API_PING = "http://127.0.0.1:23119/api/"
_START_WAIT_SECONDS = 30.0


def _api_reachable(timeout: float = 2.0) -> bool:
    try:
        urllib.request.urlopen(_API_PING, timeout=timeout)
    except urllib.error.HTTPError:
        return True  # the server answered; any HTTP status means it is up
    except Exception:  # noqa: BLE001
        return False
    return True


def _query_with_autostart[T](query: Callable[[], T]) -> T:
    """Run *query*; if Zotero's local API is down, start Zotero and retry once."""
    try:
        return query()
    except Exception:
        exe = _zotero_exe()
        if _api_reachable() or exe is None:
            raise
        sys.stderr.write("Zotero is not running; starting it...\n")
        subprocess.Popen(
            [exe],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + _START_WAIT_SECONDS
        while time.monotonic() < deadline:
            if _api_reachable():
                return query()
            time.sleep(1.0)
        raise


def _chicago_block(items: list[CitationItem], renderer: ChicagoRenderer) -> str:
    lines: list[str] = []
    for it in items:
        lines.append(f"[{it.key}]  ({it.item_type}, {it.year or 'n.d.'})")
        lines.append(f"  in-text:      {renderer.in_text([it])}")
        lines.append(f"  bibliography: {renderer.bibliography_entry(it)}")
        if it.attachment_paths:
            for p in it.attachment_paths:
                lines.append(f"  file:         {p}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _chicago_bibliography(items: list[CitationItem], renderer: ChicagoRenderer) -> str:
    return "\n".join(renderer.bibliography(items)) + "\n"


def _paths_block(items: list[CitationItem]) -> str:
    lines: list[str] = []
    for it in items:
        if it.attachment_paths:
            lines.append(f"[{it.key}]")
            for p in it.attachment_paths:
                lines.append(f"  {p}")
    return "\n".join(lines) + ("\n" if lines else "")


def _render_all(items: list[CitationItem], renderer: ChicagoRenderer) -> str:
    out: list[str] = []
    out.append("=== Chicago author-date ===")
    out.append(_chicago_block(items, renderer))
    out.append("=== BibTeX ===")
    out.append(bib.items_to_bibtex(items))
    out.append("=== CSL-JSON ===")
    out.append(bib.items_to_csljson(items))
    out.append("=== RIS ===")
    out.append("".join(ris.item_to_ris(it) for it in items))
    out.append("=== EndNote XML ===")
    out.append(endnote_xml.endnote_xml_string(items))
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search Zotero and emit citations.")
    parser.add_argument("term", nargs="?", default="", help="quicksearch term")
    parser.add_argument(
        "--format",
        choices=["chicago", "bibtex", "csljson", "ris", "endnote", "all"],
        default="chicago",
    )
    parser.add_argument("--with-paths", action="store_true")
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        metavar="FACET::VALUE",
        help="filter by a facet tag (e.g. topic::migration); repeatable, "
        "AND-combined, and combinable with the search term",
    )
    parser.add_argument(
        "--list-tags",
        nargs="?",
        const="",
        default=None,
        metavar="PREFIX",
        help="list the library's facet tags (optionally by prefix like "
        "'region::' or 'topic') and exit",
    )
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)

    if args.list_tags is not None:
        try:
            tags = _query_with_autostart(
                lambda: list_facet_tags(args.list_tags or None)
            )
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(
                f"error: could not query Zotero local API ({exc}).\n"
                "Is Zotero running? The local API listens on port 23119.\n"
            )
            return 2
        if not tags:
            sys.stderr.write("No facet tags found.\n")
            return 1
        facet = ""
        for t in tags:
            f = t.split("::", 1)[0]
            if f != facet:
                facet = f
                sys.stdout.write(f"\n{facet}::\n")
            sys.stdout.write(f"  {t}\n")
        return 0

    try:
        items = _query_with_autostart(
            lambda: search(
                args.term,
                limit=args.limit,
                with_paths=args.with_paths,
                tags=args.tag,
            )
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"error: could not query Zotero local API ({exc}).\n"
            "Is Zotero running? The local API listens on port 23119.\n"
        )
        return 2

    if not items:
        crit = args.term and f"{args.term!r}" or ""
        if args.tag:
            crit = (crit + " " if crit else "") + "tags " + ", ".join(args.tag)
        sys.stderr.write(f"No matches for {crit or 'recent items'}.\n")
        return 1

    renderer = ChicagoRenderer()

    if args.format == "chicago":
        body = (
            _chicago_bibliography(items, renderer)
            if args.out
            else _chicago_block(items, renderer)
        )
    elif args.format == "bibtex":
        body = bib.items_to_bibtex(items)
    elif args.format == "csljson":
        body = bib.items_to_csljson(items)
    elif args.format == "ris":
        body = "".join(ris.item_to_ris(it) for it in items)
    elif args.format == "endnote":
        body = endnote_xml.endnote_xml_string(items)
    else:  # all
        body = _render_all(items, renderer)

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
        sys.stderr.write(f"Wrote {len(items)} record(s) to {args.out}\n")
        if args.with_paths:
            sys.stdout.write(_paths_block(items))
    else:
        sys.stdout.write(body if body.endswith("\n") else body + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
