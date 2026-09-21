"""zotero-curator import placer (Mode D3): file loose PDFs + build a create plan.

Takes the approved Mode D research results and, for each PDF: sanitizes the
``suggested_filename``, moves the file (and any AutoExcerpter companions beside
it) into the literature folder (the required ``LIT_ROOT`` environment
variable), optionally into a ``subfolder``, resolving name collisions with a numbered suffix. It writes a
reversible ``import_move_log.csv`` and emits ``import_plan.json`` --
``{"creates": [...]}`` -- where each entry's ``path`` is the file's final
absolute location, ready for ``build_runjs.py``.

SAFE BY DEFAULT: a dry run that only reports and writes the plan with the
intended target paths. Pass ``--apply`` to actually move files. Existing files
are never overwritten.

Approved imports JSON: a list (or ``{"imports": [...]}``) of objects::

    [{"current_path": "<abs path to the loose PDF>",
      "suggested_filename": "Author YYYY Short Title.pdf",
      "itemType": "journalArticle",
      "fields": {"title": "...", "date": "1990", "publicationTitle": "..."},
      "creators": [{"creatorType": "author", "firstName": "J", "lastName": "Doe"}],
      "add_tags": ["topic::migration"],
      "subfolder": ""}]

Usage::

    python scripts/place_imports.py --imports approved.json            # dry run
    python scripts/place_imports.py --imports approved.json --apply \
        --out-plan import_plan.json --log import_move_log.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

from rename_links import _companions_for, _lib_root, sanitize_filename

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass


def _unique_target(directory: Path, filename: str) -> Path:
    """Return a non-existing path in *directory* for *filename* (numbered if taken)."""
    target = directory / filename
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    n = 2
    while True:
        cand = directory / f"{stem} ({n}){suffix}"
        if not cand.exists():
            return cand
        n += 1


def process(
    entries: list[dict], apply: bool
) -> tuple[list[dict], list[tuple[str, str]], list[str]]:
    lib_root: Path | None = None  # resolved on first use; LIT_ROOT is required
    creates: list[dict] = []
    log: list[tuple[str, str]] = []
    notes: list[str] = []

    for e in entries:
        cur = Path(str(e.get("current_path") or "")).resolve()
        suggested = str(e.get("suggested_filename") or "").strip()
        subfolder = str(e.get("subfolder") or "").strip()

        if cur.suffix.lower() != ".pdf":
            notes.append(f"SKIP (not a pdf): {cur}")
            continue
        if not cur.exists():
            notes.append(f"SKIP (file missing): {cur}")
            continue
        if not suggested:
            notes.append(f"SKIP (no suggested name): {cur}")
            continue

        new_name = sanitize_filename(suggested)
        if lib_root is None:
            lib_root = _lib_root()
        target_dir = (lib_root / subfolder) if subfolder else lib_root
        new_path = _unique_target(target_dir, new_name)

        companions = _companions_for(cur.with_suffix(""))

        if apply:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(cur), str(new_path))
            log.append((str(cur), str(new_path)))
            new_stem = new_path.with_suffix("")
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

        create = {
            "itemType": e.get("itemType") or "document",
            "fields": e.get("fields") or {},
            "path": str(new_path),
        }
        if e.get("creators"):
            create["creators"] = e["creators"]
        if e.get("add_tags"):
            create["add_tags"] = e["add_tags"]
        creates.append(create)

        verb = "MOVE" if apply else "WOULD MOVE"
        comp_n = f" (+{len(companions)} companions)" if companions else ""
        notes.append(f"{verb}: {cur.name}  ->  {new_path.name}{comp_n}")

    return creates, log, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="File loose PDFs into the library and emit a Zotero create plan."
    )
    parser.add_argument("--imports", required=True, help="approved imports JSON")
    parser.add_argument(
        "--apply", action="store_true", help="actually move files (default: dry run)"
    )
    parser.add_argument("--out-plan", default="import_plan.json")
    parser.add_argument("--log", default="import_move_log.csv")
    args = parser.parse_args(argv)

    with open(args.imports, encoding="utf-8") as fh:
        entries = json.load(fh)
    if isinstance(entries, dict):
        entries = entries.get("imports", [])

    creates, log, notes = process(entries, apply=args.apply)

    for n in notes:
        print(n)
    moved = sum(1 for n in notes if n.startswith(("MOVE", "WOULD MOVE")))
    skipped = sum(1 for n in notes if n.startswith("SKIP"))
    print(
        f"\n{'applied' if args.apply else 'dry run'}: {moved} move(s), {skipped} skipped"
    )

    with open(args.out_plan, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"creates": creates}, fh, ensure_ascii=False, indent=2)
    print(f"create plan -> {args.out_plan}")

    if args.apply:
        with open(args.log, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["old_path", "new_path"])
            w.writerows(log)
        print(f"move log -> {args.log}")
    else:
        print("(dry run: pass --apply to move files; the plan above uses target paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
