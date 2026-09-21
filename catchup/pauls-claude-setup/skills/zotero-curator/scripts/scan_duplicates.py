"""zotero-curator detection CLI: read the library and emit a duplicate worklist.

Reads every top-level work via the Zotero local API, clusters likely duplicates
(refined fuzzy matching), optionally runs a byte-identical attachment pass, and
writes a structured worklist (JSON) plus a human-readable summary. Read-only:
this never writes to Zotero. The worklist feeds the adjudication step described
in SKILL.md; the approved plan is then turned into a Run-JS snippet by
``build_runjs.py``.

Usage::

    python scripts/scan_duplicates.py [--hash] [--out worklist.json]

Requires Zotero running (local API on port 23119).
"""

from __future__ import annotations

import argparse
import json
import sys

from fuzzy import find_duplicates
from zotero_read import all_works

# Windows consoles default to cp1252; titles carry non-Latin-1 characters.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass


def _summary(result: dict, hash_groups: list[dict] | None) -> str:
    s = result["stats"]
    lines = [
        "Zotero duplicate scan",
        f"  works scanned:      {s['works_scanned']}",
        f"  clusters:           {s['clusters']} ({s['items_in_clusters']} items)",
        f"  review pairs:       {s['review_pairs']}",
    ]
    if hash_groups is not None:
        lines.append(f"  byte-identical sets: {len(hash_groups)}")
    lines.append("")
    for c in result["clusters"]:
        flag = f"  [{'; '.join(c['flags'])}]" if c["flags"] else ""
        lines.append(f"CLUSTER {c['cluster_id']} ({c['size']}) - {c['reason']}{flag}")
        for m in c["members"]:
            lines.append(
                f"    {m['key']}  [{m['item_type'][:4]}] "
                f"{(m['first_author'] or '?'):16.16s} {m['year'] or '----'}  "
                f"{m['title'][:64]}"
            )
        lines.append("")
    if hash_groups:
        lines.append("BYTE-IDENTICAL FILES ACROSS DIFFERENT WORKS")
        for g in hash_groups:
            lines.append(
                f"  md5 {g['md5'][:12]} -> works {', '.join(g['parent_keys'])}"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan the Zotero library for duplicates."
    )
    parser.add_argument(
        "--hash",
        action="store_true",
        help="also run the byte-identical attachment pass (reads files; slower)",
    )
    parser.add_argument(
        "--out", default="", help="write the worklist JSON to this path"
    )
    args = parser.parse_args(argv)

    try:
        works = all_works()
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"error: could not query Zotero local API ({exc}).\n"
            "Is Zotero running? The local API listens on port 23119.\n"
        )
        return 2

    result = find_duplicates(works)

    hash_groups: list[dict] | None = None
    if args.hash:
        from hash_pass import byte_identical_groups

        hash_groups = byte_identical_groups()
        result["byte_identical"] = hash_groups

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        sys.stderr.write(f"Wrote worklist to {args.out}\n")

    sys.stdout.write(_summary(result, hash_groups) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
