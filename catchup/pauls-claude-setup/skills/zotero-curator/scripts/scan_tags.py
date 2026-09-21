"""zotero-curator Mode C detection: build a per-work tagging worklist.

Read-only. Pulls every top-level work via the Zotero local API (reusing
``zotero_read``), resolves each work's attachment PDF path(s) and any
AutoExcerpter companion files beside them (.txt / _summary.md /
_short_summary.md / _summary.docx), and records the work's existing automatic
(type=1) tags as hints. The worklist feeds the subagent tagging pass described
in SKILL.md (Mode C); validated results are turned into a plan by
``tag_plan.py`` and applied via ``build_runjs.py``.

Re-run AFTER deduplication so the worklist naturally covers survivors only.

Usage::

    python scripts/scan_tags.py --out tag_worklist.json
    python scripts/scan_tags.py --out tag_worklist.json --untagged-only

Requires Zotero running (local API on port 23119).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from zotero_read import all_attachments_detailed, all_items_raw

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

_COMPANION_SUFFIXES = (
    ".txt",
    "_summary.md",
    "_short_summary.md",
    "_summary.docx",
)


def _companions(pdf_path: str) -> list[str]:
    p = Path(pdf_path)
    if p.suffix.lower() != ".pdf":
        return []
    stem_path = p.with_suffix("")  # drops .pdf
    found: list[str] = []
    for suf in _COMPANION_SUFFIXES:
        cand = (
            Path(str(stem_path) + suf)
            if suf.startswith("_")
            else stem_path.with_suffix(suf)
        )
        if cand.exists():
            found.append(str(cand))
    return found


def _creator_summary(data: dict) -> tuple[str, str]:
    raw = data.get("creators")
    if not isinstance(raw, list):
        return "", ""
    names = []
    for c in raw:
        if not isinstance(c, dict):
            continue
        last = str(c.get("lastName") or c.get("name") or "").strip()
        if last:
            names.append(last)
    first = names[0] if names else ""
    return first, "; ".join(names)


def build_worklist(untagged_only: bool = False) -> dict:
    works = all_items_raw()

    att_map: dict[str, list[dict]] = defaultdict(list)
    for a in all_attachments_detailed():
        att_map[a["parent_key"]].append(a)

    out_works = []
    for data in works:
        key = str(data.get("key") or "")
        if not key:
            continue
        tags = data.get("tags") or []
        auto_tags = [
            str(t.get("tag") or "")
            for t in tags
            if isinstance(t, dict) and int(t.get("type", 0) or 0) == 1 and t.get("tag")
        ]
        manual_tags = [
            str(t.get("tag") or "")
            for t in tags
            if isinstance(t, dict) and int(t.get("type", 0) or 0) == 0 and t.get("tag")
        ]
        if untagged_only and manual_tags:
            continue

        atts = att_map.get(key, [])
        pdf_atts = [
            {"att_key": a["att_key"], "path": a["path"], "link_mode": a["link_mode"]}
            for a in atts
            if a["path"].lower().endswith(".pdf")
        ]
        pdf_paths = [a["path"] for a in pdf_atts]
        companion_paths: list[str] = []
        for p in pdf_paths:
            companion_paths.extend(_companions(p))

        first_author, authors = _creator_summary(data)
        out_works.append(
            {
                "key": key,
                "item_type": str(data.get("itemType") or ""),
                "title": str(data.get("title") or "").strip(),
                "first_author": first_author,
                "authors": authors,
                "date": str(data.get("date") or "").strip(),
                "language": str(data.get("language") or "").strip(),
                "abstract": str(data.get("abstractNote") or "").strip()[:1500],
                "pdf_paths": pdf_paths,
                "pdf_atts": pdf_atts,
                "companion_paths": companion_paths,
                "existing_auto_tags": auto_tags,
                "existing_manual_tags": manual_tags,
            }
        )

    return {"count": len(out_works), "works": out_works}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Mode C tagging worklist.")
    parser.add_argument("--out", default="tag_worklist.json", help="output JSON path")
    parser.add_argument(
        "--untagged-only",
        action="store_true",
        help="skip works that already have >=1 manual (type 0) tag",
    )
    args = parser.parse_args(argv)

    try:
        result = build_worklist(untagged_only=args.untagged_only)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"error: could not query Zotero local API ({exc}).\n"
            "Is Zotero running? The local API listens on port 23119.\n"
        )
        return 2

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    works = result["works"]
    with_pdf = sum(1 for w in works if w["pdf_paths"])
    with_comp = sum(1 for w in works if w["companion_paths"])
    with_auto = sum(1 for w in works if w["existing_auto_tags"])
    print(f"works in worklist:        {result['count']}")
    print(f"  with >=1 PDF:           {with_pdf}")
    print(f"  with >=1 companion:     {with_comp}")
    print(f"  with existing autotags: {with_auto}")
    print(f"worklist -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
