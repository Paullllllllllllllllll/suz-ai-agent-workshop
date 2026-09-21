"""zotero-curator import scanner (Mode D1): gather loose PDFs for accession.

Read-only. Given PDF paths, folders, or globs, records each candidate's identity
(absolute path, size, MD5, page count), any embedded title/author, and a
first-page text snippet, then checks it against the existing Zotero library so
nothing is imported twice:

  * ``already_in_library`` -- a byte-identical MD5 match against a current
    attachment (the same file is already attached to a work), and
  * ``possible_duplicate`` -- a fuzzy title match against an existing work.

The worklist feeds the Mode D research subagents (see SKILL.md); their confirmed
metadata becomes an import plan placed by ``place_imports.py`` and applied
through ``build_runjs.py``. This script never moves a file or writes to Zotero.

Usage::

    python scripts/scan_imports.py <pdf-or-folder-or-glob> [...] \
        [--recursive] [--no-library-check] [--out import_worklist.json]

Requires Zotero running (local API on port 23119) unless --no-library-check.
"""

from __future__ import annotations

import argparse
import glob as globmod
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from hash_pass import _md5

# Windows consoles default to cp1252; titles carry non-Latin-1 characters.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

# Fuzzy title match at or above this similarity flags a possible duplicate.
_DUP_TITLE_SIM = 0.80


def _expand(inputs: list[str], recursive: bool) -> list[Path]:
    """Resolve paths/folders/globs to a de-duplicated list of PDF files."""
    seen: dict[str, Path] = {}
    for raw in inputs:
        matches = (
            globmod.glob(raw, recursive=True)
            if any(ch in raw for ch in "*?[")
            else [raw]
        )
        for m in matches:
            p = Path(m)
            if p.is_dir():
                it = p.rglob("*.pdf") if recursive else p.glob("*.pdf")
                for f in it:
                    seen[str(f.resolve()).lower()] = f.resolve()
            elif p.suffix.lower() == ".pdf" and p.exists():
                seen[str(p.resolve()).lower()] = p.resolve()
    return sorted(seen.values(), key=lambda x: str(x).lower())


def _extract_pdf(path: Path) -> dict:
    """Best-effort embedded title/author, page count, first-page snippet."""
    out: dict = {
        "page_count": None,
        "embedded_title": "",
        "embedded_author": "",
        "snippet": "",
    }
    try:
        from pypdf import PdfReader
    except ImportError:
        return out
    try:
        reader = PdfReader(str(path))
        out["page_count"] = len(reader.pages)
        meta = reader.metadata or {}
        out["embedded_title"] = str(meta.get("/Title") or "").strip()
        out["embedded_author"] = str(meta.get("/Author") or "").strip()
        if reader.pages:
            text = reader.pages[0].extract_text() or ""
            out["snippet"] = " ".join(text.split())[:800]
    except Exception:  # noqa: BLE001
        pass  # encrypted/corrupt PDFs degrade to identity-only
    return out


def _candidate_title(info: dict) -> str:
    """Best available title for the fuzzy library check (embedded, else snippet)."""
    if info.get("embedded_title"):
        return info["embedded_title"]
    snippet = info.get("snippet") or ""
    return snippet[:120]


def _library_matches(candidates: list[dict]) -> None:
    """Annotate each candidate in place with library duplicate flags.

    Byte-identical: hash existing attachments only within sizes a candidate
    shares (most library files are never read). Fuzzy title: compare each
    candidate title against every existing work via the Mode A similarity core.
    """
    from fuzzy import _Prepared, _title_sim
    from zotero_read import Work, all_attachments, all_works

    cand_sizes = {c["size"] for c in candidates if c.get("size") is not None}

    # Byte-identical pass against existing attachments.
    existing_by_size: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for parent_key, path in all_attachments():
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        if size in cand_sizes:
            existing_by_size[size].append((parent_key, path))
    existing_md5: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for size, members in existing_by_size.items():
        for parent_key, path in members:
            digest = _md5(path)
            if digest:
                existing_md5[digest].append((parent_key, path))

    # Fuzzy title pass against existing works.
    works = all_works()
    prepared = [(_Prepared(w), w) for w in works if w.title]

    for c in candidates:
        if c.get("md5") and c["md5"] in existing_md5:
            hits = existing_md5[c["md5"]]
            c["flags"].append("already_in_library")
            c["library_matches"] = {
                "byte_identical": [{"parent_key": pk, "path": pth} for pk, pth in hits]
            }
            continue
        title = _candidate_title(c)
        if not title:
            continue
        cand_work = Work(
            key="",
            item_type="",
            title=title,
            first_author=c.get("embedded_author") or "",
            authors="",
            year=None,
            date="",
        )
        cp = _Prepared(cand_work)
        best: tuple[float, Work] | None = None
        for ep, w in prepared:
            sim = _title_sim(cp, ep)
            if sim >= _DUP_TITLE_SIM and (best is None or sim > best[0]):
                best = (sim, w)
        if best is not None:
            c["flags"].append("possible_duplicate")
            c.setdefault("library_matches", {})["fuzzy_title"] = {
                "key": best[1].key,
                "title": best[1].title,
                "year": best[1].year,
                "title_sim": round(best[0], 3),
            }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gather loose PDFs for import into Zotero (Mode D1)."
    )
    parser.add_argument(
        "inputs", nargs="+", help="PDF paths, folders, or globs to scan"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="recurse into sub-folders when an input is a directory",
    )
    parser.add_argument(
        "--no-library-check",
        action="store_true",
        help="skip the duplicate check against the existing library",
    )
    parser.add_argument("--out", default="", help="write the worklist JSON here")
    args = parser.parse_args(argv)

    files = _expand(args.inputs, args.recursive)
    if not files:
        sys.stderr.write("No PDF files matched the given inputs.\n")
        return 2

    candidates: list[dict] = []
    for f in files:
        try:
            size = f.stat().st_size
        except OSError:
            size = None
        info = _extract_pdf(f)
        candidates.append(
            {
                "path": str(f),
                "size": size,
                "md5": _md5(str(f)),
                "page_count": info["page_count"],
                "embedded_title": info["embedded_title"],
                "embedded_author": info["embedded_author"],
                "snippet": info["snippet"],
                "flags": [],
            }
        )

    note = ""
    if not args.no_library_check:
        try:
            _library_matches(candidates)
        except Exception as exc:  # noqa: BLE001
            note = (
                f"library check skipped ({exc}); is Zotero running on port "
                "23119? Re-run with --no-library-check to silence this."
            )

    result = {
        "candidates": candidates,
        "stats": {
            "scanned": len(candidates),
            "already_in_library": sum(
                1 for c in candidates if "already_in_library" in c["flags"]
            ),
            "possible_duplicate": sum(
                1 for c in candidates if "possible_duplicate" in c["flags"]
            ),
        },
    }
    if note:
        result["note"] = note

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        sys.stderr.write(f"Wrote import worklist to {args.out}\n")

    out = [f"Import scan: {len(candidates)} PDF(s)"]
    if note:
        out.append(f"  ! {note}")
    for c in candidates:
        flag = f"  [{', '.join(c['flags'])}]" if c["flags"] else ""
        title = c["embedded_title"] or "(no embedded title)"
        out.append(f"- {Path(c['path']).name}  {title[:48]}{flag}")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
