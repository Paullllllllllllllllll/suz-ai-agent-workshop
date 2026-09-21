"""zotero-curator metadata scanner: flag sparse or likely-wrong entries.

Read-only. Sweeps every top-level work via the Zotero local API, scores each on
metadata completeness and plausibility, resolves its attachment PDF paths
(via the local API), and emits a worklist sorted by severity. The worklist feeds
the metadata-research subagents described in SKILL.md; their confirmed fixes
become a plan applied through ``build_runjs.py``.

The scoring core (``evaluate``) is a pure function of one Zotero ``data`` dict
and is unit-testable offline.

Usage::

    python scripts/scan_metadata.py [--limit N] [--with-paths] [--out worklist.json]

Requires Zotero running (local API on port 23119).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

from zotero_read import all_items_raw, attachment_paths_map

# Windows consoles default to cp1252; titles carry non-Latin-1 characters.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

_YEAR_RE = re.compile(r"\b(\d{3,4})\b")

# The check assumes a library whose metadata is written in Latin script (e.g.
# English, German, French, Spanish, Italian). A letter from any other script -- Cyrillic,
# Greek, CJK, kana, Hangul, Arabic, Hebrew, Thai, Indic, ... -- in a title or
# creator name signals a mis-imported or wrong record. Detection keys on the
# leading token of a character's Unicode name (e.g. "CYRILLIC SMALL LETTER A").
_NON_LATIN_SCRIPTS = {
    "CYRILLIC",
    "GREEK",
    "COPTIC",
    "ARMENIAN",
    "HEBREW",
    "ARABIC",
    "SYRIAC",
    "THAANA",
    "NKO",
    "SAMARITAN",
    "DEVANAGARI",
    "BENGALI",
    "GURMUKHI",
    "GUJARATI",
    "ORIYA",
    "TAMIL",
    "TELUGU",
    "KANNADA",
    "MALAYALAM",
    "SINHALA",
    "THAI",
    "LAO",
    "TIBETAN",
    "MYANMAR",
    "GEORGIAN",
    "HANGUL",
    "ETHIOPIC",
    "CHEROKEE",
    "MONGOLIAN",
    "HIRAGANA",
    "KATAKANA",
    "BOPOMOFO",
    "CJK",
    "YI",
    "KHMER",
}
# Friendly labels for script tokens that do not title-case cleanly.
_SCRIPT_LABEL = {"CJK": "CJK", "NKO": "N'Ko"}

# item_type -> the Zotero field that should carry the container/venue title.
_CONTAINER_FIELD: dict[str, str] = {
    "journalArticle": "publicationTitle",
    "magazineArticle": "publicationTitle",
    "newspaperArticle": "publicationTitle",
    "bookSection": "bookTitle",
    "conferencePaper": "proceedingsTitle",
    "encyclopediaArticle": "encyclopediaTitle",
    "dictionaryEntry": "dictionaryTitle",
}

# item_type -> the field that should carry the publisher (or institution).
_PUBLISHER_FIELD: dict[str, str] = {
    "book": "publisher",
    "bookSection": "publisher",
    "conferencePaper": "publisher",
    "report": "institution",
    "thesis": "university",
    "map": "publisher",
}

# Severity weights per flag prefix.
_WEIGHTS = {
    "no title": 5,
    "no creators": 4,
    "no year": 3,
    "suspect title": 4,
    "implausible year": 3,
    "missing journal": 3,
    "missing book title": 3,
    "missing venue": 2,
    "missing publisher": 2,
    "duplicate creators": 2,
    "malformed creator": 2,
    "non-Latin script": 3,
    "all-caps title": 1,
}


def _year(date: str) -> int | None:
    best: int | None = None
    for m in _YEAR_RE.finditer(date or ""):
        v = int(m.group(1))
        if 1000 <= v <= 2100:
            best = v
            break
    return best


def _suspect_title(t: str) -> bool:
    """Conservative test for a genuinely garbled/junk title.

    Deliberately narrow to avoid flagging legitimate titles (year ranges,
    consonant-heavy words, non-English text). Fires only on the Unicode
    replacement character or a title that is mostly non-letters.
    """
    if not t:
        return False
    if "�" in t:
        return True  # mojibake replacement character
    letters = sum(c.isalpha() for c in t)
    return len(t) >= 8 and letters / len(t) < 0.45


def _all_caps_title(t: str) -> bool:
    """A multi-word title in all caps -- a metadata-quality issue, not garbling."""
    letters = [c for c in t if c.isalpha()]
    return (
        len(letters) >= 8 and all(c.isupper() for c in letters) and len(t.split()) >= 2
    )


def _non_latin_scripts(s: str) -> set[str]:
    """Return friendly labels of any non-Latin scripts found among *s*'s letters.

    ASCII and Latin-script letters (including accented Latin used by German,
    French, Spanish, and Italian) are expected and ignored; only characters
    belonging to a script in ``_NON_LATIN_SCRIPTS`` are reported. Letterlike
    symbols, ordinals, roman numerals, and digits are never flagged.
    """
    found: set[str] = set()
    for ch in s:
        if ch.isascii() or not ch.isalpha():
            continue
        token = unicodedata.name(ch, "").split(" ", 1)[0]
        if token in _NON_LATIN_SCRIPTS:
            found.add(_SCRIPT_LABEL.get(token, token.title()))
    return found


def _malformed_creator(creators: list) -> bool:
    """A creator that looks dirty: comma/digit in surname, single char, or overlong."""
    for c in creators:
        if not isinstance(c, dict):
            continue
        last = str(c.get("lastName") or "").strip()
        val = last or str(c.get("name") or "").strip()
        if not val:
            continue
        if "," in last:  # "Smith, John" stuffed into lastName
            return True
        if any(ch.isdigit() for ch in val):
            return True
        if len(val) == 1 or len(val) > 60:
            return True
    return False


def evaluate(data: dict) -> tuple[list[str], int]:
    """Return (flags, severity) for one Zotero ``data`` dict.

    Pure: no I/O. ``flags`` is human-readable; ``severity`` sums flag weights.
    """
    itype = str(data.get("itemType") or "")
    title = str(data.get("title") or "").strip()
    creators = data.get("creators") or []
    has_creator = any(
        (c.get("lastName") or c.get("name")) for c in creators if isinstance(c, dict)
    )
    seen_creators: set[tuple[str, str]] = set()
    dup_creators = False
    for c in creators:
        if not isinstance(c, dict):
            continue
        sig = (c.get("lastName") or c.get("name") or "", c.get("firstName") or "")
        if any(sig) and sig in seen_creators:
            dup_creators = True
        seen_creators.add(sig)
    date = str(data.get("date") or "").strip()
    year = _year(date)

    flags: list[str] = []

    if not title:
        flags.append("no title")
    elif _suspect_title(title):
        flags.append(f"suspect title: {title[:48]!r}")
    elif _all_caps_title(title):
        flags.append("all-caps title")

    if not has_creator:
        flags.append("no creators")
    else:
        if dup_creators:
            flags.append("duplicate creators")
        if _malformed_creator(creators):
            flags.append("malformed creator")

    creator_text = " ".join(
        str(c.get("lastName") or c.get("name") or c.get("firstName") or "")
        for c in creators
        if isinstance(c, dict)
    )
    title_scripts = _non_latin_scripts(title)
    creator_scripts = _non_latin_scripts(creator_text)
    if title_scripts:
        flags.append("non-Latin script in title: " + ", ".join(sorted(title_scripts)))
    elif creator_scripts:
        flags.append(
            "non-Latin script in creator: " + ", ".join(sorted(creator_scripts))
        )

    if not year:
        flags.append("no year")
    elif year < 1400 or year > 2027:
        flags.append(f"implausible year: {year}")

    container_field = _CONTAINER_FIELD.get(itype)
    if container_field and not str(data.get(container_field) or "").strip():
        if itype.endswith("Article"):
            flags.append("missing journal")
        elif itype == "bookSection":
            flags.append("missing book title")
        else:
            flags.append("missing venue")

    pub_field = _PUBLISHER_FIELD.get(itype)
    if pub_field and not str(data.get(pub_field) or "").strip():
        flags.append("missing publisher")

    severity = 0
    for f in flags:
        for prefix, weight in _WEIGHTS.items():
            if f.startswith(prefix):
                severity += weight
                break
    return flags, severity


def _creators_summary(creators: list) -> str:
    names = []
    for c in creators:
        if not isinstance(c, dict):
            continue
        names.append(c.get("lastName") or c.get("name") or "")
    return "; ".join(n for n in names if n)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Flag sparse/wrong Zotero metadata.")
    parser.add_argument("--limit", type=int, default=0, help="cap entries (0 = all)")
    parser.add_argument(
        "--with-paths",
        action="store_true",
        help="resolve each entry's attachment PDF paths (via the local API)",
    )
    parser.add_argument("--out", default="", help="write the worklist JSON here")
    args = parser.parse_args(argv)

    try:
        items = all_items_raw()
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"error: could not query Zotero local API ({exc}).\n"
            "Is Zotero running? The local API listens on port 23119.\n"
        )
        return 2

    paths_map = attachment_paths_map() if args.with_paths else {}
    entries: list[dict] = []
    for data in items:
        flags, severity = evaluate(data)
        if not flags:
            continue
        key = str(data.get("key") or "")
        entry = {
            "key": key,
            "item_type": data.get("itemType"),
            "title": data.get("title") or "",
            "creators": _creators_summary(data.get("creators") or []),
            "date": data.get("date") or "",
            "publisher": data.get("publisher")
            or data.get("institution")
            or data.get("university")
            or "",
            "container": data.get("publicationTitle")
            or data.get("bookTitle")
            or data.get("proceedingsTitle")
            or "",
            "isbn": data.get("ISBN") or "",
            "doi": data.get("DOI") or "",
            "language": data.get("language") or "",
            "flags": flags,
            "severity": severity,
        }
        if args.with_paths and key:
            entry["pdf_paths"] = paths_map.get(key, [])
        entries.append(entry)

    entries.sort(key=lambda e: -e["severity"])
    if args.limit:
        entries = entries[: args.limit]

    result = {
        "entries": entries,
        "stats": {
            "works_scanned": len(items),
            "flagged": len(entries),
        },
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        sys.stderr.write(f"Wrote metadata worklist to {args.out}\n")

    # Human summary to stdout.
    out = [
        f"Metadata scan: {len(entries)} of {len(items)} works flagged",
        "",
    ]
    for e in entries:
        out.append(
            f"[sev {e['severity']:>2}] {e['key']}  [{(e['item_type'] or '')[:4]}]  "
            f"{(e['title'] or '(no title)')[:56]}"
        )
        out.append(f"            flags: {'; '.join(e['flags'])}")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
