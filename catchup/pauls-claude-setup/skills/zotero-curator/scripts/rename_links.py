"""zotero-curator: rename misnamed linked-file PDFs and emit Zotero relink actions.

When a tagging (Mode C) or dedup (Mode A) subagent finds a PDF whose filename
substantively misnames the work, it proposes a corrected ``Author YYYY
Title.pdf`` name. After the user approves the rename list, this script:

  1. renames the PDF on disk (linked files only, inside the library root
     given by the required ``LIT_ROOT`` environment variable),
  2. renames any AutoExcerpter companion files beside it to match the new stem
     (.txt / .md / .docx / _summary.md / _short_summary.md / _summary.docx), so
     the companion linkage survives,
  3. writes a reversible ``rename_log.csv`` (old,new), and
  4. emits ``relink_map.json`` -- {parent_key: [{att, path, title}]} -- which
     ``tag_plan.py --relink`` (or a dedup plan) folds into the Run-JS plan so
     ``build_runjs.py`` updates each Zotero attachment's path via the API.

SAFE BY DEFAULT: a dry run that only reports. Pass ``--apply`` to move files.
Imported attachments (inside Zotero ``storage/``) are skipped -- Zotero manages
those filenames itself.

Approved renames JSON: a list of objects::

    [{"key": "<parent work key>", "att_key": "<attachment key>",
      "current_path": "<abs path>", "suggested_filename": "Author YYYY Title.pdf",
      "reason": "..."}]

Usage::

    python scripts/rename_links.py --renames renames.json            # dry run
    python scripts/rename_links.py --renames renames.json --apply \
        --out-relink relink_map.json --log rename_log.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

_COMPANION_SUFFIXES = (
    ".txt",
    ".md",
    ".docx",
    "_summary.md",
    "_short_summary.md",
    "_summary.docx",
)
_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _lib_root() -> Path:
    """Return the literature folder from ``LIT_ROOT``; exit if it is unset."""
    env = os.environ.get("LIT_ROOT", "").strip()
    if not env:
        raise SystemExit(
            "error: LIT_ROOT is not set. Set it to the folder that holds your "
            "linked PDFs (e.g. LIT_ROOT=~/Literature) and re-run."
        )
    return Path(env).expanduser().resolve()


def _storage_dir() -> Path:
    env = os.environ.get("ZOTERO_DATA_DIR")
    return (Path(env) if env else Path.home() / "Zotero").resolve() / "storage"


def sanitize_filename(name: str) -> str:
    name = _ILLEGAL.sub(" ", name).strip()
    name = re.sub(r"\s+", " ", name)
    if not name.lower().endswith(".pdf"):
        name = name + ".pdf"
    return name


def _companions_for(stem_path: Path) -> list[tuple[Path, str]]:
    """Return (existing_companion_path, suffix) for a PDF stem."""
    out = []
    for suf in _COMPANION_SUFFIXES:
        cand = (
            Path(str(stem_path) + suf)
            if suf.startswith("_")
            else stem_path.with_suffix(suf)
        )
        if cand.exists():
            out.append((cand, suf))
    return out


def process(
    entries: list[dict], apply: bool
) -> tuple[dict, list[tuple[str, str]], list[str]]:
    lib_root: Path | None = None  # resolved on first use; LIT_ROOT is required
    storage = _storage_dir()
    relink_map: dict[str, list[dict]] = defaultdict(list)
    log: list[tuple[str, str]] = []
    notes: list[str] = []

    for e in entries:
        cur = Path(str(e.get("current_path") or "")).resolve()
        att_key = str(e.get("att_key") or "")
        parent = str(e.get("key") or e.get("parent_key") or "")
        suggested = str(e.get("suggested_filename") or "")

        if not cur or cur.suffix.lower() != ".pdf":
            notes.append(f"SKIP (not a pdf): {cur}")
            continue
        if not att_key or not parent:
            notes.append(f"SKIP (missing att_key/key): {cur}")
            continue
        if not cur.exists():
            notes.append(f"SKIP (file missing): {cur}")
            continue
        if lib_root is None:
            lib_root = _lib_root()
        try:
            cur.relative_to(lib_root)
        except ValueError:
            notes.append(f"SKIP (outside library root): {cur}")
            continue
        if str(storage).lower() in str(cur).lower():
            notes.append(f"SKIP (imported/storage attachment): {cur}")
            continue
        if not suggested.strip():
            notes.append(f"SKIP (no suggested name): {cur}")
            continue

        new_name = sanitize_filename(suggested)
        target_folder = str(e.get("target_folder") or "").strip()
        new_dir = (lib_root / target_folder) if target_folder else cur.parent
        new_path = new_dir / new_name
        if new_path.resolve() == cur:
            notes.append(f"SKIP (path unchanged): {cur.name}")
            continue
        if not new_dir.exists():
            notes.append(f"SKIP (target folder missing): {target_folder}")
            continue
        if new_path.exists():
            notes.append(f"SKIP (target exists): {new_path.name}")
            continue

        new_stem = new_path.with_suffix("")
        cur_stem = cur.with_suffix("")
        companions = _companions_for(cur_stem)

        if apply:
            shutil.move(str(cur), str(new_path))
            log.append((str(cur), str(new_path)))
            for comp_path, suf in companions:
                comp_new = (
                    Path(str(new_stem) + suf)
                    if suf.startswith("_")
                    else new_stem.with_suffix(suf)
                )
                if comp_new.exists():
                    notes.append(f"  companion target exists, left: {comp_path.name}")
                    continue
                shutil.move(str(comp_path), str(comp_new))
                log.append((str(comp_path), str(comp_new)))

        relink_map[parent].append(
            {"att": att_key, "path": str(new_path), "title": new_stem.name}
        )
        verb = "RENAME" if apply else "WOULD RENAME"
        comp_n = f" (+{len(companions)} companions)" if companions else ""
        notes.append(f"{verb}: {cur.name}  ->  {new_name}{comp_n}")

    return relink_map, log, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rename misnamed linked PDFs + emit relink map."
    )
    parser.add_argument("--renames", required=True, help="approved renames JSON")
    parser.add_argument(
        "--apply", action="store_true", help="actually move files (default: dry run)"
    )
    parser.add_argument("--out-relink", default="relink_map.json")
    parser.add_argument("--log", default="rename_log.csv")
    args = parser.parse_args(argv)

    with open(args.renames, encoding="utf-8") as fh:
        entries = json.load(fh)
    if isinstance(entries, dict):
        entries = entries.get("renames", [])

    relink_map, log, notes = process(entries, apply=args.apply)

    for n in notes:
        print(n)
    renamed = sum(1 for n in notes if n.startswith(("RENAME", "WOULD RENAME")))
    skipped = sum(1 for n in notes if n.startswith("SKIP"))
    print(
        f"\n{'applied' if args.apply else 'dry run'}: {renamed} rename(s), {skipped} skipped"
    )

    if args.apply:
        with open(args.out_relink, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(relink_map), fh, ensure_ascii=False, indent=2)
        with open(args.log, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["old_path", "new_path"])
            w.writerows(log)
        print(f"relink map -> {args.out_relink}")
        print(f"rename log -> {args.log}")
    else:
        print("(dry run: pass --apply to move files and write the relink map)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
