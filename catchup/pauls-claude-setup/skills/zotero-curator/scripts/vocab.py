"""Load and validate the faceted tag vocabulary (zotero-curator Mode C).

The vocabulary (``tag_vocabulary.yaml`` at the skill root) is the single source
of truth for facet values. Agents map a work to EXISTING ``facet::value`` tags;
anything not present is classified as a proposal (held for review), never
applied silently. Free-form (un-prefixed) tags are the escape hatch.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

_DEFAULT = Path(__file__).resolve().parent.parent / "tag_vocabulary.yaml"


def vocab_path() -> Path:
    env = os.environ.get("TAG_VOCAB")
    return Path(env) if env else _DEFAULT


def load_vocab(path: str | os.PathLike | None = None) -> dict:
    with open(Path(path) if path else vocab_path(), encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def valid_values(vocab: dict) -> dict[str, set[str]]:
    """facet -> set(allowed values)."""
    return {f: set(vals or []) for f, vals in (vocab.get("facets") or {}).items()}


def rules(vocab: dict) -> dict:
    return vocab.get("rules") or {}


def split_tag(tag: str) -> tuple[str | None, str]:
    """'facet::value' -> (facet, value); free-form -> (None, value)."""
    if "::" in tag:
        facet, _, value = tag.partition("::")
        return facet.strip(), value.strip()
    return None, tag.strip()


def normalize_tag(tag: str) -> str:
    """Canonicalize a tag's casing/spacing.

    Facet lowercased; value lowercased and space-hyphenated, EXCEPT ``project``
    values which are uppercased. Free-form tags are lowercased and
    space-hyphenated so the whole tag scheme stays uniform.
    """
    facet, value = split_tag(tag)
    if facet is None:
        return "-".join(value.lower().split())
    facet = facet.lower()
    value = value.upper() if facet == "project" else "-".join(value.lower().split())
    return f"{facet}::{value}"


def classify_tag(tag: str, vv: dict[str, set[str]]) -> tuple[str, str | None, str]:
    """Return (status, facet, value).

    status in {valid, unknown_value, unknown_facet, freeform}.
    """
    facet, value = split_tag(tag)
    if facet is None:
        return "freeform", None, value
    if facet not in vv:
        return "unknown_facet", facet, value
    if value not in vv[facet]:
        return "unknown_value", facet, value
    return "valid", facet, value
