"""Type-mapping tables for RIS and EndNote XML export.

Single source of truth for both formats; helpers ``ris_ty`` and
``endnote_reftype`` derive values from these dicts so every caller stays DRY.

Harvested verbatim from CiteForge (export/types.py).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# RIS TY codes
# ---------------------------------------------------------------------------

#: Zotero item_type -> RIS TY tag.
RIS_TY: dict[str, str] = {
    "journalArticle": "JOUR",
    "book": "BOOK",
    "bookSection": "CHAP",
    "conferencePaper": "CONF",
    "thesis": "THES",
    "report": "RPRT",
    "magazineArticle": "MGZN",
    "newspaperArticle": "NEWS",
    "webpage": "ELEC",
    "blogPost": "ELEC",
    "manuscript": "UNPB",
    "patent": "PAT",
    "presentation": "CONF",
}

DEFAULT_RIS_TY: str = "GEN"

# ---------------------------------------------------------------------------
# EndNote numeric ref-type codes (verified against RefTypeTableEN9.xml).
# ---------------------------------------------------------------------------

#: Zotero item_type -> (numeric code, name attribute).
ENDNOTE_REFTYPE: dict[str, tuple[int, str]] = {
    "journalArticle": (0, "Journal Article"),
    "book": (1, "Book"),
    "thesis": (2, "Thesis"),
    "newspaperArticle": (5, "Newspaper Article"),
    "bookSection": (7, "Book Section"),
    "magazineArticle": (8, "Magazine Article"),
    "report": (10, "Report"),
    "patent": (15, "Patent"),
    "webpage": (16, "Electronic Source"),
    "blogPost": (16, "Electronic Source"),
    "manuscript": (20, "Manuscript"),
    "conferencePaper": (33, "Conference Paper"),
}

#: Edited Book code (id="9" in RefTypeTableEN9.xml).
_EDITED_BOOK: tuple[int, str] = (9, "Edited Book")

DEFAULT_ENDNOTE_REFTYPE: tuple[int, str] = (31, "Generic")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def ris_ty(item_type: str) -> str:
    """Return the RIS TY tag for *item_type*, falling back to ``DEFAULT_RIS_TY``."""
    return RIS_TY.get(item_type, DEFAULT_RIS_TY)


def endnote_reftype(item_type: str, has_authors: bool = True) -> tuple[int, str]:
    """Return the EndNote (code, name) for *item_type*.

    When *item_type* is ``"book"`` and *has_authors* is ``False``, the
    "Edited Book" code (9) is returned instead of the plain "Book" code.
    """
    if item_type == "book" and not has_authors:
        return _EDITED_BOOK
    return ENDNOTE_REFTYPE.get(item_type, DEFAULT_ENDNOTE_REFTYPE)
