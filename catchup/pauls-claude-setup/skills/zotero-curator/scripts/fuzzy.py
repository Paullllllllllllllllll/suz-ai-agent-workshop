"""Refined fuzzy duplicate clustering for top-level works.

Design goal: avoid the transitive over-merge that fuses a distinct series
(e.g. "Linear Algebra for Dummies" / "Algebra I for Dummies" / "Algebra II
Workbook for Dummies") into one cluster. Two guards do this:

1. A pair is "strong" only when titles are (near-)identical AND authors agree --
   so dissimilar series titles never form a strong link.
2. Clusters are the connected components of strong pairs ONLY. Because every
   internal link must clear the high bar, a chain of merely-similar titles
   cannot pull unrelated works together.

Weaker title matches (0.80-0.90 with author agreement) are reported separately
as ``review_pairs`` -- candidates for a human/subagent to judge, never
auto-clustered.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from zotero_read import Work

# Tokens too generic to carry matching signal.
_STOP = {
    "a",
    "an",
    "the",
    "of",
    "and",
    "or",
    "in",
    "on",
    "for",
    "to",
    "de",
    "la",
    "le",
    "el",
    "der",
    "die",
    "das",
    "und",
    "von",
    "zu",
    "los",
    "las",
    "vol",
    "volume",
    "edition",
    "ausgabe",
    "nouvelle",
    "new",
    "i",
    "ii",
    "iii",
    "iv",
}

# Thresholds. Strong = auto-cluster (kept strict to avoid over-merging); review
# = surfaced for subagent judgment (kept loose to over-report borderline pairs).
_STRONG_TITLE = 0.90
_AUTHOR_AGREE = 0.85
_REVIEW_TITLE = 0.72
_REVIEW_AUTHOR = 0.50

# Tokens that denote a volume/part/edition number: digits or roman numerals.
# Two titles that agree textually but disagree on these are almost always
# distinct volumes (e.g. "Algebra I" vs "Algebra II") and must not auto-cluster.
_NUM_RE = re.compile(r"^(?:\d+|[ivxlcdm]+)$")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"<[^>]+>", " ", s)  # strip stray HTML tags (e.g. <i>)
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def _tokens(norm_title: str) -> frozenset[str]:
    return frozenset(t for t in norm_title.split() if t not in _STOP and len(t) > 1)


def _title_numbers(norm_title: str) -> frozenset[str]:
    """Volume/part/edition number tokens (digits or roman numerals) in a title."""
    return frozenset(t for t in norm_title.split() if _NUM_RE.match(t))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _author_sim(a: str, b: str) -> float:
    """Agreement between two first-author surnames.

    Returns 1.0 on exact normalized match, the string ratio otherwise, and a
    neutral 0.6 when both are missing (anonymous works can still be dupes).
    """
    na, nb = _norm(a), _norm(b)
    if not na and not nb:
        return 0.6
    if not na or not nb:
        return 0.3
    if na == nb:
        return 1.0
    return _ratio(na, nb)


class _Prepared:
    __slots__ = ("work", "ntitle", "tokens", "numbers", "block")

    def __init__(self, work: Work) -> None:
        self.work = work
        self.ntitle = _norm(work.title)
        self.tokens = _tokens(self.ntitle)
        self.numbers = _title_numbers(self.ntitle)
        # Block key: first author surname initial + first meaningful token,
        # used only to prune the O(n^2) sweep cheaply.
        self.block = _norm(work.first_author)[:4]


def _title_sim(a: _Prepared, b: _Prepared) -> float:
    return max(_jaccard(a.tokens, b.tokens), _ratio(a.ntitle, b.ntitle))


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def find_duplicates(works: list[Work]) -> dict:
    """Cluster *works* into duplicate groups plus weaker review pairs.

    Returns a dict with ``clusters``, ``review_pairs`` and ``stats``.
    """
    prepared = [_Prepared(w) for w in works if w.title]
    n = len(prepared)

    uf = _UnionFind()
    strong_links: list[tuple[str, str, float, float]] = []
    review_pairs: list[dict] = []

    for i in range(n):
        pi = prepared[i]
        for j in range(i + 1, n):
            pj = prepared[j]
            # Cheap prefilter: require a shared meaningful token OR a shared
            # author block; otherwise the pair cannot be a near-duplicate.
            if not (pi.tokens & pj.tokens) and pi.block != pj.block:
                continue
            ts = _title_sim(pi, pj)
            if ts < _REVIEW_TITLE:
                continue
            a_sim = _author_sim(pi.work.first_author, pj.work.first_author)
            identical = pi.ntitle == pj.ntitle and pi.ntitle != ""
            numbers_match = pi.numbers == pj.numbers
            if (
                (identical or ts >= _STRONG_TITLE)
                and a_sim >= _AUTHOR_AGREE
                and numbers_match
            ):
                uf.union(pi.work.key, pj.work.key)
                strong_links.append((pi.work.key, pj.work.key, ts, a_sim))
            elif ts >= _REVIEW_TITLE and a_sim >= _REVIEW_AUTHOR:
                note = "similar but below the auto-cluster bar; judge by hand"
                if not numbers_match:
                    note = "titles differ by a volume/edition number; likely distinct"
                review_pairs.append(
                    {
                        "a": pi.work.as_dict(),
                        "b": pj.work.as_dict(),
                        "title_sim": round(ts, 3),
                        "author_sim": round(a_sim, 3),
                        "note": note,
                    }
                )

    # Assemble clusters from the union-find over strong links.
    by_key = {p.work.key: p.work for p in prepared}
    groups: dict[str, list[str]] = {}
    for key in by_key:
        if key in uf.parent:
            groups.setdefault(uf.find(key), []).append(key)

    clusters: list[dict] = []
    for cid, (_, members) in enumerate(
        sorted(groups.items(), key=lambda kv: -len(kv[1])), start=1
    ):
        if len(members) < 2:
            continue
        member_works = [by_key[k] for k in members]
        # Reason: identical titles vs near-identical.
        ntitles = {_norm(w.title) for w in member_works}
        reason = (
            "identical normalized title"
            if len(ntitles) == 1
            else "near-identical titles, same author"
        )
        # Surface a likely type/year fix when members disagree on type or year.
        types = {w.item_type for w in member_works}
        years = {w.year for w in member_works if w.year}
        flags: list[str] = []
        if len(types) > 1:
            flags.append(f"mixed item types: {sorted(types)}")
        if len(years) > 1:
            flags.append(f"mixed years: {sorted(years)}")
        if any(w.year is None for w in member_works) and years:
            flags.append("some members missing a year")
        clusters.append(
            {
                "cluster_id": cid,
                "size": len(member_works),
                "reason": reason,
                "flags": flags,
                "members": [w.as_dict() for w in member_works],
            }
        )

    return {
        "clusters": clusters,
        "review_pairs": review_pairs,
        "stats": {
            "works_scanned": n,
            "clusters": len(clusters),
            "items_in_clusters": sum(c["size"] for c in clusters),
            "review_pairs": len(review_pairs),
            "strong_links": len(strong_links),
        },
    }
