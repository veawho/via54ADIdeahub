#!/usr/bin/env python3
"""Export KBStore → OKF v0.1 bundle directory.

Usage:
    python tools/export_okf.py --db via54_kb.db --out ./via54_kb_okf_bundle
                              [--limit 50] [--include-types Case Study,Reference]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
sys.path.insert(0, str(_REPO))

import yaml  # type: ignore
from via54_store import KBStore

# Mapping from type field → output subdirectory
_TYPE_DIR = {
    "Case Study": "case_studies",
    "Case Overview": "case_overviews",
    "Video Catalog": "videos",
    "Creative Mix": "creatives",
    "Folder README": "folder_readmes",
    "Visual References": "visual_references",
    "Reference": "references",
    "Video List": "references",
}

# Characters illegal in filenames (Windows-safe subset)
_ILLEGAL_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_filename(name: str, max_len: int = 200) -> str:
    name = _ILLEGAL_CHARS_RE.sub("_", name)
    name = name.strip(". _")
    if len(name) > max_len:
        base, ext = os.path.splitext(name)
        name = base[: max_len - len(ext) - 1] + ext
    return name or "unnamed.md"


def main():
    parser = argparse.ArgumentParser(description="Export KBStore to OKF bundle")
    parser.add_argument("--db", default="via54_kb.db")
    parser.add_argument("--out", default="via54_kb_okf_bundle", type=str)
    parser.add_argument("--limit", type=int, default=0, help="Max concepts to export (0 = all)")
    parser.add_argument("--include-types", type=str, default="",
                        help="Comma-separated type filter (empty = all)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    store = KBStore(args.db)
    conn = store._conn

    # Build filter
    type_filter = set()
    if args.include_types:
        type_filter = {t.strip() for t in args.include_types.split(",")}

    # Read all concepts
    where = ""
    params = []
    if type_filter:
        placeholders = ",".join("?" * len(type_filter))
        where = f"WHERE type IN ({placeholders})"
        params = list(type_filter)

    rows = conn.execute(
        f"SELECT concept_id, rel_path, type, title, description, resource, "
        f"tags_json, source_path, body_size, body_hash "
        f"FROM concepts {where} ORDER BY concept_id",
        tuple(params),
    ).fetchall()

    if args.limit > 0:
        rows = rows[:args.limit]

    if not rows:
        print("❌ No concepts to export")
        return

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    stats = {"Case Study": 0, "Video Catalog": 0, "Creative Mix": 0, "Folder README": 0, "Reference": 0}
    total = 0

    for row in rows:
        cid = int(row["concept_id"])
        rel_path = row["rel_path"] or ""
        ftype = row["type"] or "Reference"
        title = row["title"] or Path(rel_path).stem
        description = row["description"] or ""
        resource = row["resource"] or ""
        tags_json = row["tags_json"] or "[]"
        source_path = row["source_path"] or ""

        # Determine output subdirectory
        subdir_name = _TYPE_DIR.get(ftype, "other")
        subdir = out_dir / subdir_name
        subdir.mkdir(parents=True, exist_ok=True)

        # Build filename from rel_path or title
        if rel_path:
            raw_name = Path(rel_path).stem
            # Extract just the final meaningful part
            parts = rel_path.split("/")
            if len(parts) >= 4:
                raw_name = f"{parts[-3]}_{parts[-2]}_{parts[-1]}".replace(".md", "")
            safe = _safe_filename(raw_name) + ".md"
        else:
            safe = _safe_filename(title) + ".md"

        file_path = subdir / safe

        # Read body from source file
        body = ""
        if source_path and os.path.isfile(source_path):
            try:
                body = Path(source_path).read_text(encoding="utf-8", errors="replace")
            except Exception:
                body = f"(original source not readable: {source_path})"
        else:
            body = f"(source not available: {source_path})"

        # Parse tags
        try:
            tags = json.loads(tags_json) if tags_json else []
        except (json.JSONDecodeError, TypeError):
            tags = []

        # Build frontmatter
        frontmatter = {
            "type": ftype,
            "title": title,
            "description": description,
            "resource": resource,
            "tags": tags if tags else None,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        # Remove None values
        frontmatter = {k: v for k, v in frontmatter.items() if v is not None}

        doc_text = f"---\n{yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()}\n---\n\n{body}"

        file_path.write_text(doc_text, encoding="utf-8")
        total += 1
        stats[ftype] = stats.get(ftype, 0) + 1

        if args.verbose and total % 100 == 0:
            print(f"  {total} concepts written...")

    # ── index.md ──
    index_lines = ["# via54ADIdeahub Knowledge Bundle", "", "## Concepts by Type", ""]
    for ftype, subdir_name in sorted(set((k, v) for k, v in _TYPE_DIR.items())):
        subdir = out_dir / subdir_name
        if not subdir.exists():
            continue
        entries = sorted(subdir.iterdir())
        relevant = [e for e in entries if e.suffix == ".md"]
        if not relevant:
            continue
        index_lines.append(f"## {ftype}")
        for ep in relevant:
            desc = ""
            # Try reading frontmatter for description
            try:
                text = ep.read_text(encoding="utf-8", errors="replace")
                if text.startswith("---"):
                    parts = text.split("---", 2)
                    if len(parts) >= 3:
                        fm = yaml.safe_load(parts[1]) or {}
                        desc = fm.get("description", "")
            except Exception:
                pass
            name = ep.stem.replace("_", " ").title()
            rel = f"{subdir_name}/{ep.name}"
            if desc:
                index_lines.append(f"* [{name}]({rel}) - {desc}")
            else:
                index_lines.append(f"* [{name}]({rel})")
        index_lines.append("")
    out_dir.joinpath("index.md").write_text("\n".join(index_lines), encoding="utf-8")

    # ── log.md ──
    log_text = f"""# Directory Update Log

## {time.strftime("%Y-%m-%d")}
* **Initialization**: Exported {total} concepts from via54_kb.db to {out_dir}
  * Case Studies: {stats.get('Case Study', 0)}
  * Video Catalogs: {stats.get('Video Catalog', 0)}
  * Creative Mixes: {stats.get('Creative Mix', 0)}
  * Folder READMEs: {stats.get('Folder README', 0)}
  * References: {stats.get('Reference', 0)}
  * Other: {total - sum(stats.values())}
"""
    out_dir.joinpath("log.md").write_text(log_text.strip() + "\n", encoding="utf-8")

    # ── bundle.yaml ──
    bundle_yaml = {
        "name": "via54-knowledge",
        "version": "0.1.0",
        "description": f"via54ADIdeahub Knowledge bundle ({total} concepts)",
        "maintainer": "veawho (via54)",
    }
    out_dir.joinpath("bundle.yaml").write_text(
        yaml.dump(bundle_yaml, allow_unicode=True, sort_keys=False).strip() + "\n",
        encoding="utf-8",
    )

    store.close()
    print(f"\n✅ OKF bundle exported to {out_dir}")
    print(f"   {total} concepts | {sum(1 for p in out_dir.rglob('case_studies/*.md'))} case studies")
    print(f"   bundle.yaml | index.md | log.md")
    print(f"   Subdirs: {', '.join(sorted(set(_TYPE_DIR.values())))}")


if __name__ == "__main__":
    main()
