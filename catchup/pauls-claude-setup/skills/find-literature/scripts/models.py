"""The normalized bibliographic record shared across the skill.

``CitationItem`` is the single in-memory representation of a reference. It
carries flat, normalized columns (which drive RIS/EndNote/BibTeX export) *and*
the original CSL-JSON object (the authoritative payload for Chicago rendering
via citeproc-py). ``zotero_read`` builds these from the Zotero local API.

Harvested verbatim from CiteForge (core/models.py); self-contained, no deps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Companion-file roles, in surfacing-preference order.
COMPANION_ROLES: tuple[str, ...] = (
    "pdf",
    "transcription",
    "summary_md",
    "summary_docx",
    "short_summary_md",
)

# Creator roles we distinguish when exporting (everything else collapses to
# "author" at the call site).
CREATOR_ROLES: tuple[str, ...] = ("author", "editor", "translator")


@dataclass(slots=True)
class Creator:
    """A single contributor.

    Either ``last``/``first`` are set (a personal name) or ``literal`` holds a
    single-field corporate/organization name, in which case ``last``/``first``
    are empty.
    """

    last: str = ""
    first: str = ""
    role: str = "author"
    literal: str = ""

    @property
    def is_literal(self) -> bool:
        return bool(self.literal) and not (self.last or self.first)

    def display(self) -> str:
        """``Last, First`` (or the literal name) for RIS/EndNote output."""
        if self.is_literal:
            return self.literal
        if self.first:
            return f"{self.last}, {self.first}"
        return self.last


@dataclass(slots=True)
class CompanionFiles:
    """Absolute paths to AutoExcerpter reading artifacts for one record."""

    pdf: str = ""
    transcription: str = ""
    summary_md: str = ""
    summary_docx: str = ""
    short_summary_md: str = ""

    @property
    def has_transcription(self) -> bool:
        return bool(self.transcription)

    @property
    def has_summary(self) -> bool:
        return bool(self.summary_md or self.summary_docx or self.short_summary_md)

    def as_dict(self) -> dict[str, str]:
        return {role: getattr(self, role) for role in COMPANION_ROLES}

    def items(self) -> list[tuple[str, str]]:
        """(role, path) pairs for the roles that are populated."""
        return [
            (role, getattr(self, role))
            for role in COMPANION_ROLES
            if getattr(self, role)
        ]


@dataclass(slots=True)
class CitationItem:
    """A normalized bibliographic record.

    ``zotero_key`` is the stable sync identity. ``key`` is the user-facing
    citekey handle used in documents (here derived from author+year+title when
    Better BibTeX is unavailable).
    """

    # --- identity / sync ---
    key: str
    zotero_key: str
    version: int = 0
    item_type: str = "document"
    # --- core bibliographic ---
    title: str = ""
    creators: list[Creator] = field(default_factory=list)
    year: int | None = None
    date: str = ""
    container: str = ""
    publisher: str = ""
    place: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    # --- identifiers ---
    doi: str = ""
    isbn: str = ""
    issn: str = ""
    url: str = ""
    # --- descriptive ---
    language: str = ""
    edition: str = ""
    series: str = ""
    abstract: str = ""
    tags: list[str] = field(default_factory=list)
    collections: list[str] = field(default_factory=list)
    # --- rendering source of truth ---
    csl_json: dict[str, Any] = field(default_factory=dict)
    # --- timestamps ---
    date_added: str = ""
    date_modified: str = ""
    # --- linked reading artifacts (populated on read) ---
    files: CompanionFiles = field(default_factory=CompanionFiles)
    # --- absolute attachment paths (populated by --with-paths) ---
    attachment_paths: list[str] = field(default_factory=list)

    def creators_by_role(self, role: str) -> list[Creator]:
        return [c for c in self.creators if c.role == role]

    @property
    def authors(self) -> list[Creator]:
        """Authors, falling back to editors when an item has no authors."""
        authors = self.creators_by_role("author")
        return authors or self.creators_by_role("editor")

    def short_authors(self, limit: int = 3) -> str:
        """A compact ``Smith, Jones et al.`` label for display."""
        names = [c.last or c.literal for c in self.authors if (c.last or c.literal)]
        if not names:
            return ""
        if len(names) > limit:
            return f"{', '.join(names[:limit])} et al."
        return ", ".join(names)
