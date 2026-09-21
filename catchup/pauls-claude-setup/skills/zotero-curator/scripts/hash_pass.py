"""Optional byte-identical attachment pass (local API + file MD5).

Catches the duplicate class title matching misses: the same file (identical
bytes) attached to two different top-level works under divergent metadata. Reads
every attachment's resolved path from the local API (``all_attachments``), hashes
within same-size buckets (so most files are never read), and reports MD5 groups
whose member files hang off more than one parent work.
"""

from __future__ import annotations

import hashlib
import os
from collections import defaultdict

from zotero_read import all_attachments


def _md5(path: str, chunk: int = 1 << 20) -> str | None:
    try:
        h = hashlib.md5()
        with open(path, "rb") as fh:
            while block := fh.read(chunk):
                h.update(block)
        return h.hexdigest()
    except OSError:
        return None


def byte_identical_groups() -> list[dict]:
    """Return groups of byte-identical files spanning >1 parent work."""
    pairs = all_attachments()

    # Bucket by file size first; only hash within buckets of size > 1.
    by_size: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for parent_key, path in pairs:
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        by_size[size].append((parent_key, path))

    by_md5: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for group in by_size.values():
        if len(group) < 2:
            continue
        for parent_key, path in group:
            digest = _md5(path)
            if digest:
                by_md5[digest].append((parent_key, path))

    results: list[dict] = []
    for digest, members in by_md5.items():
        parents = {pk for pk, _ in members}
        if len(parents) < 2:
            continue  # same file under one work is not a cross-work dup
        results.append(
            {
                "md5": digest,
                "parent_keys": sorted(parents),
                "files": sorted({p for _, p in members}),
            }
        )
    return results
