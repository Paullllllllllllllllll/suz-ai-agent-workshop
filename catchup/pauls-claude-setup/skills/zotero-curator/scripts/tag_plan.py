"""zotero-curator Mode C: validate subagent tag results into an apply plan.

Reads the JSON files the tagging subagents produced, validates every proposed
``facet::value`` tag against the controlled vocabulary, caps the free-form
``additional`` tags, and assembles:

  * ``plan.json``      -- ready for build_runjs.py (per work: clear_auto_tags +
                          add_tags), feeding the Run-JS apply path;
  * ``proposals.json`` -- unknown facet values and recurring free-form tags, for
                          the user to review and fold into tag_vocabulary.yaml;
  * ``tag_progress.json`` -- the running done-keys checkpoint (merged across
                          calls) so the batch run can pause/resume.

Each subagent result is an object (or a list of them, or {"results": [...]})::

    {"key": "ABCD1234",
     "add_tags": ["topic::migration", "region::switzerland", "period::post-1990",
                  "source-type::secondary-literature", "lang::de", "project::DISS"],
     "additional": ["asylum-policy", "naturalization"],
     "proposed_new_values": [{"facet": "topic", "value": "citizenship",
                              "why": "..."}]}

Usage::

    python scripts/tag_plan.py --results <dir-or-file> [--out-plan plan.json]
        [--out-proposals proposals.json] [--progress tag_progress.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

from vocab import classify_tag, load_vocab, normalize_tag, rules, valid_values

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass


def _iter_results(path: Path):
    """Yield result objects from a file or directory of JSON files."""
    files: list[Path] = []
    if path.is_dir():
        files = [Path(p) for p in glob.glob(str(path / "*.json"))]
    elif path.is_file():
        files = [path]
    else:
        files = [Path(p) for p in glob.glob(str(path))]
    for fp in sorted(files):
        try:
            with open(fp, encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"warn: skipping unreadable {fp}: {exc}\n")
            continue
        if isinstance(doc, dict) and "results" in doc:
            doc = doc["results"]
        if isinstance(doc, dict):
            doc = [doc]
        if not isinstance(doc, list):
            continue
        for obj in doc:
            if isinstance(obj, dict) and obj.get("key"):
                yield obj


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble a Mode C tag plan.")
    parser.add_argument(
        "--results", required=True, help="dir, file, or glob of subagent result JSON"
    )
    parser.add_argument("--out-plan", default="plan.json")
    parser.add_argument("--out-proposals", default="proposals.json")
    parser.add_argument("--progress", default="tag_progress.json")
    parser.add_argument("--out-renames", default="renames.json")
    parser.add_argument(
        "--relink", default=None, help="relink_map.json from rename_links.py to fold in"
    )
    parser.add_argument("--vocab", default=None)
    args = parser.parse_args(argv)

    vocab = load_vocab(args.vocab)
    vv = valid_values(vocab)
    max_additional = int(rules(vocab).get("max_additional", 5))

    per_key_tags: dict[str, set[str]] = defaultdict(set)
    new_values: Counter[str] = Counter()
    new_value_why: dict[str, str] = {}
    additional_freq: Counter[str] = Counter()
    renames: list[dict] = []
    dropped = 0
    n_results = 0

    for obj in _iter_results(Path(args.results)):
        n_results += 1
        key = str(obj["key"]).strip()

        # facet tags
        for raw in obj.get("add_tags") or []:
            norm = normalize_tag(str(raw))
            status, facet, value = classify_tag(norm, vv)
            if status == "valid":
                per_key_tags[key].add(norm)
            elif status in ("unknown_value", "unknown_facet"):
                new_values[f"{facet}::{value}"] += 1
                dropped += 1
            else:  # freeform slipped into add_tags
                additional_freq[norm] += 1
                per_key_tags[key].add(norm)

        # free-form additional tags (capped per work)
        added_extra = 0
        for raw in obj.get("additional") or []:
            if added_extra >= max_additional:
                break
            norm = normalize_tag(str(raw))
            if not norm:
                continue
            additional_freq[norm] += 1
            per_key_tags[key].add(norm)
            added_extra += 1

        # proposed new controlled values (held for review)
        for pv in obj.get("proposed_new_values") or []:
            if not isinstance(pv, dict):
                continue
            f = str(pv.get("facet") or "").strip().lower()
            v = str(pv.get("value") or "").strip()
            if not f or not v:
                continue
            tag = f"{f}::{v}"
            new_values[tag] += 1
            if pv.get("why") and tag not in new_value_why:
                new_value_why[tag] = str(pv["why"])

        # misnamed-PDF rename proposal (held for review; applied via rename_links.py)
        rn = obj.get("rename")
        if (
            isinstance(rn, dict)
            and rn.get("suggested_filename")
            and rn.get("att_key")
            and rn.get("current_path")
        ):
            renames.append(
                {
                    "key": key,
                    "att_key": str(rn["att_key"]),
                    "current_path": str(rn["current_path"]),
                    "suggested_filename": str(rn["suggested_filename"]),
                    "reason": str(rn.get("reason") or ""),
                }
            )

    actions = [
        {"keep": key, "clear_auto_tags": True, "add_tags": sorted(tags)}
        for key, tags in sorted(per_key_tags.items())
        if tags
    ]

    # fold approved disk renames into the plan as relink actions
    if args.relink and os.path.exists(args.relink):
        with open(args.relink, encoding="utf-8") as fh:
            relink_map = json.load(fh)
        by_key = {a["keep"]: a for a in actions}
        for pk, links in relink_map.items():
            if pk in by_key:
                by_key[pk]["relink"] = links
            else:
                actions.append({"keep": pk, "relink": links})
        actions.sort(key=lambda a: a["keep"])

    plan = {"actions": actions}
    with open(args.out_plan, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=2)

    proposals = {
        "new_facet_values": [
            {"tag": t, "count": c, "why": new_value_why.get(t, "")}
            for t, c in new_values.most_common()
        ],
        "additional_tags": [
            {"tag": t, "count": c} for t, c in additional_freq.most_common()
        ],
    }
    with open(args.out_proposals, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(proposals, fh, ensure_ascii=False, indent=2)

    with open(args.out_renames, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"renames": renames}, fh, ensure_ascii=False, indent=2)

    # merge the done-keys checkpoint
    done = set()
    if os.path.exists(args.progress):
        try:
            with open(args.progress, encoding="utf-8") as fh:
                done = set(json.load(fh).get("done_keys", []))
        except Exception:  # noqa: BLE001
            done = set()
    done.update(per_key_tags.keys())
    with open(args.progress, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"count": len(done), "done_keys": sorted(done)}, fh, indent=2)

    total_facet = sum(1 for tags in per_key_tags.values() for t in tags if "::" in t)
    total_extra = sum(
        1 for tags in per_key_tags.values() for t in tags if "::" not in t
    )
    print(f"results read:           {n_results}")
    print(f"works with tags:        {len(actions)}")
    print(f"facet tags applied:     {total_facet}")
    print(f"additional tags:        {total_extra}")
    print(
        f"unknown values dropped: {dropped} ({len(new_values)} distinct -> proposals)"
    )
    print(f"rename proposals:       {len(renames)}")
    print(f"checkpoint done_keys:   {len(done)}")
    print(f"plan -> {args.out_plan}")
    print(f"proposals -> {args.out_proposals}")
    print(f"renames -> {args.out_renames}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
