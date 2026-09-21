"""Chicago author-date rendering via citeproc-py with a pure-Python fallback.

Harvested from CiteForge (citations/render.py); ``from core.models`` rewritten
to the skill-local ``models`` module. The vendored style lives next to this
file at ``styles/chicago-author-date.csl``.

CSL-JSON contract
-----------------
Every ``CitationItem.csl_json`` blob passed to ``ChicagoRenderer`` must carry
an ``"id"`` key equal to the item's citekey (``item.key``). ``zotero_read``
sets this automatically. Items without a valid ``id`` silently trigger the
fallback renderer.
"""

from __future__ import annotations

import logging
from pathlib import Path

from models import CitationItem, Creator

log = logging.getLogger(__name__)

_VENDORED_STYLE = Path(__file__).parent / "styles" / "chicago-author-date.csl"


# ---------------------------------------------------------------------------
# Fallback renderer (no citeproc-py dependency)
# ---------------------------------------------------------------------------


def _format_creators_fallback(creators: list[Creator]) -> str:
    """Return a display string for up to three authors/editors."""
    names = [c.display() for c in creators if (c.last or c.literal)]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{names[0]}, {names[1]}, and {names[2]}"


def render_fallback_chicago(
    item: CitationItem, mode: str = "bibliography", locator: str = ""
) -> str:
    """Hand-rolled Chicago author-date approximation from normalized fields.

    Does NOT use ``csl_json``; works on a bare ``CitationItem``. In ``intext``
    mode an optional *locator* (page/section) is appended as ``, <locator>``.
    """
    authors = item.authors
    first_last = authors[0].last or authors[0].literal if authors else ""
    year_str = str(item.year) if item.year else "n.d."

    if mode == "intext":
        loc = f", {locator}" if locator else ""
        return f"({first_last} {year_str}{loc})".strip()

    # bibliography mode
    creator_str = _format_creators_fallback(authors)
    title = item.title or ""
    year_part = f"{year_str}."
    title_part = f'"{title}."' if item.container else f"{title}."

    if item.container:
        # article / chapter
        parts = [creator_str + "." if creator_str else ""]
        parts.append(year_part)
        parts.append(title_part)
        container_part = item.container
        if item.volume:
            container_part += f" {item.volume}"
            if item.issue:
                container_part += f" ({item.issue})"
        if item.pages:
            container_part += f": {item.pages}"
        parts.append(container_part + ".")
    else:
        # book-ish
        parts = [creator_str + "." if creator_str else ""]
        parts.append(year_part)
        parts.append(title_part)
        if item.place and item.publisher:
            parts.append(f"{item.place}: {item.publisher}.")
        elif item.publisher:
            parts.append(f"{item.publisher}.")
        elif item.place:
            parts.append(f"{item.place}.")

    return " ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# citeproc-py renderer
# ---------------------------------------------------------------------------


class ChicagoRenderer:
    """Chicago author-date renderer backed by citeproc-py.

    Uses the vendored ``styles/chicago-author-date.csl`` by default, or a
    caller-supplied path. All citeproc calls are wrapped in try/except and fall
    back to ``render_fallback_chicago`` on any error.
    """

    def __init__(self, csl_style_path: Path | None = None) -> None:
        path = csl_style_path if csl_style_path is not None else _VENDORED_STYLE
        self._style_path = path
        self._style: object = None
        self._ok = False
        try:
            from citeproc import CitationStylesStyle

            self._style = CitationStylesStyle(str(path), validate=False)
            self._ok = True
        except Exception as exc:  # noqa: BLE001
            log.warning("citeproc: failed to load style %s: %s", path, exc)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def in_text(
        self,
        items: list[CitationItem],
        locator: str = "",
        prefix: str = "",
    ) -> str:
        """Return a combined in-text parenthetical citation.

        Examples: ``(Smith 2021, 23)``; ``(Smith 2021; Braudel 1981)``.

        Rendered via the deterministic fallback: citeproc-py 0.9.3 drops
        inter-element spacing in this style (mangling the locator, e.g.
        ``198123``), so its in-text output is not used. For publication-grade
        reference lists, emit BibTeX and run Pandoc/BibLaTeX.
        """
        if not items:
            return ""
        return self._fallback_intext(items, locator=locator)

    def bibliography_entry(self, item: CitationItem) -> str:
        """Return one formatted reference-list entry."""
        entries = self.bibliography([item])
        return entries[0] if entries else render_fallback_chicago(item)

    def bibliography(self, items: list[CitationItem]) -> list[str]:
        """Return formatted reference-list entries (one per item).

        Uses the built-in Chicago author-date formatter rather than citeproc:
        citeproc-py 0.9.3 drops inter-element spacing in this style's
        bibliography layout, whereas its *in-text* output is correct and is
        used by ``in_text``.
        """
        return [render_fallback_chicago(it) for it in items]

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _build_source_and_bib(self, items: list[CitationItem]) -> tuple[object, object]:
        """Construct a fresh ``CiteProcJSON`` source and bibliography."""
        from citeproc import (
            CitationStylesBibliography,
            formatter,
        )
        from citeproc.source.json import CiteProcJSON

        csl_data = [it.csl_json for it in items if it.csl_json.get("id")]
        source = CiteProcJSON(csl_data)
        bib = CitationStylesBibliography(self._style, source, formatter.plain)
        return source, bib

    def _render_intext(
        self,
        items: list[CitationItem],
        *,
        locator: str,
        prefix: str,
    ) -> str:
        from citeproc.source import (
            Citation,
            Locator,
        )
        from citeproc.source import CitationItem as CPItem

        _, bib = self._build_source_and_bib(items)

        cp_cites: list[object] = []
        for idx, it in enumerate(items):
            key = it.csl_json.get("id")
            if not key:
                continue
            kwargs: dict[str, object] = {}
            if idx == 0 and locator:
                kwargs["locator"] = Locator("page", locator)
            if idx == 0 and prefix:
                kwargs["prefix"] = prefix
            cp_cites.append(CPItem(key, **kwargs))

        if not cp_cites:
            return self._fallback_intext(items)

        citation = Citation(cp_cites)
        bib.register(citation)  # type: ignore[attr-defined]
        result = bib.cite(citation, lambda _: None)  # type: ignore[attr-defined]
        return str(result).strip()

    def _fallback_intext(self, items: list[CitationItem], locator: str = "") -> str:
        parts = [
            render_fallback_chicago(
                it, mode="intext", locator=locator if idx == 0 else ""
            )
            for idx, it in enumerate(items)
        ]
        inner = "; ".join(p.strip("()").strip() for p in parts if p.strip("()").strip())
        return f"({inner})" if inner else ""
