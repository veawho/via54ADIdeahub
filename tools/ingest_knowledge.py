#!/usr/bin/env python3
"""Ingest ~/Desktop/Knowledge .md files into via54 KBStore (SQLite + vectors).

Usage:
    python tools/ingest_knowledge.py [--knowledge-root PATH] [--db PATH]
        [--chunk-size 300] [--chunk-overlap 50] [--limit N] [--verbose]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import time
from pathlib import Path

# Add repo root to sys.path so imports work from subdirs
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
sys.path.insert(0, str(_REPO))

from via54_store import KBStore, hash_embed
from via54_store.embedding import _tokenize


# ── helpers ────────────────────────────────────────────────────────────

_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_URL_RE = re.compile(r"https?://[^\s)）\"']+")
_SKIPPED_EXT = {".json", ".html", ".pdf", ".jpg", ".png", ".jpeg", ".cms", ".f0bdnp", ".DS_Store"}


def _extract_title(text: str, filename: str) -> str:
    m = _H1_RE.search(text)
    if m:
        return m.group(1).strip()
    return Path(filename).stem


def _extract_first_url(text: str) -> str:
    m = _URL_RE.search(text)
    return m.group(0) if m else ""


def _mtime_iso(path: Path) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.stat(path).st_mtime))


def _chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    """Split markdown into overlapping chunks by paragraph."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current = ""
    start = 0
    for para in paragraphs:
        para = para.strip()
        if not para:
            start += len(para) + 2
            continue
        if len(current) + len(para) < chunk_size:
            if current:
                current += "\n\n"
            current += para
        else:
            if len(current.strip()) >= 50:
                chunks.append({"text": current.strip(), "start": start})
            start += len(current) + 2
            current = para
    if len(current.strip()) >= 50:
        chunks.append({"text": current.strip(), "start": start})
    return chunks


# ── type mapping from filename ────────────────────────────────────────

_FILENAME_TYPE = {
    "01_案例深度报告.md": "Case Study",
    "00_案例概述.md": "Case Overview",
    "03_videos.md": "Video Catalog",
    "creative_mixed.md": "Creative Mix",
    "_FOLDER_README.md": "Folder README",
    "视觉插图引用.md": "Visual References",
    "README.md": "Reference",
    "视频清单.md": "Video List",
    "_index.md": "Reference",
    "_视频清单_legacy.md": "Reference",
    "creative_mixed": "Creative Mix",
}


def _file_type(filename: str) -> str:
    return _FILENAME_TYPE.get(filename, "Reference")


def _is_case_md(filename: str) -> bool:
    """Files that describe a case rather than auxiliary metadata."""
    return filename in ("01_案例深度报告.md", "00_案例概述.md")

# ── main ──────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    parser = argparse.ArgumentParser(description="Ingest Knowledge .md files into KBStore")
    parser.add_argument("--knowledge-root", default=os.path.expanduser(
        "~/Desktop/Knowledge/Idea/By_Industry"))
    parser.add_argument("--db", default="via54_kb.db")
    parser.add_argument("--chunk-size", type=int, default=300)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    parser.add_argument("--limit", type=int, default=0, help="Only process N cases (for testing)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    root = Path(args.knowledge_root)
    if not root.is_dir():
        print(f"❌ Knowledge root not found: {root}")
        sys.exit(1)

    store = KBStore(args.db)
    store.init_schema()
    bundle_id = store.upsert_bundle(
        name="knowledge",
        root_path=str(root),
        version="1.0.0",
        description=f"via54ADIdeahub Knowledge bundle from {root}",
    )
    print(f"📦 Bundle ID: {bundle_id}")

    # ── scan: group files by case ──
    case_dirs: list[Path] = []
    for industry_dir in sorted(root.iterdir()):
        if not industry_dir.is_dir():
            continue
        for brand_dir in sorted(industry_dir.iterdir()):
            if not brand_dir.is_dir():
                continue
            for case_dir in sorted(brand_dir.iterdir()):
                if not case_dir.is_dir():
                    continue
                case_dirs.append(case_dir)

    if args.limit > 0:
        case_dirs = case_dirs[:args.limit]

    total_cases = len(case_dirs)
    print(f"📂 Found {total_cases} case directories under {root}")

    processed = skipped = errors = 0
    case_idx = 0
    chunk_total = 0

    for case_dir in case_dirs:
        case_idx += 1
        rel = case_dir.relative_to(root)
        parts = rel.parts  # (industry, brand, case_name)
        industry = parts[0]
        brand = parts[1] if len(parts) > 1 else "Unknown"
        case_name = parts[2] if len(parts) > 2 else "Unknown"
        tags = [industry, brand, case_name]

        if args.verbose:
            print(f"  [{case_idx}/{total_cases}] {industry}/{brand}/{case_name}")

        # Collect .md files in this case dir
        md_files = sorted(f for f in case_dir.iterdir() if f.suffix == ".md" and f.name not in _SKIPPED_EXT)

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                if args.verbose:
                    print(f"    ⚠ skip {md_file.name}: {e}")
                skipped += 1
                continue

            if not content.strip():
                skipped += 1
                continue

            ftype = _file_type(md_file.name)
            title = _extract_title(content, md_file.name)
            description = content.split("\n")[0].strip().lstrip("#> \t")[:200]
            resource = _extract_first_url(content)
            mtime_iso = _mtime_iso(md_file)
            body_size = len(content)
            body_hash = hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()

            # Build rel_path like knowledge/<industry>/<brand>/<case>/<file.md>
            rel_path = f"knowledge/{industry}/{brand}/{case_name}/{md_file.name}"

            cid = store.upsert_concept(
                bundle_id=bundle_id,
                rel_path=rel_path,
                type=ftype,
                title=title,
                description=description,
                resource=resource,
                tags=tags,
                timestamp=mtime_iso,
                source_path=str(md_file),
                mtime=os.stat(md_file).st_mtime,
                body_size=body_size,
                body_hash=body_hash,
            )

            # upsert_concept always returns cid; we track all as processed
            processed += 1

            # ── chunk + embed ──
            chunks = _chunk_text(content, args.chunk_size, args.chunk_overlap)
            for ci, chunk in enumerate(chunks):
                text = chunk["text"]
                tokens = _tokenize(text)
                char_start = chunk["start"]
                char_end = char_start + len(text)

                chunk_id = store.add_chunk(
                    concept_id=cid,
                    chunk_idx=ci,
                    text=text,
                    char_start=char_start,
                    char_end=char_end,
                    tokens=tokens,
                    commit=False,  # batch commit
                )
                chunk_total += 1

                # ── vector ──
                vec = hash_embed(text, dim=256)
                store.add_chunk_vector(chunk_id, vec, model="hash-256", commit=False)

            # Commit per case
            store._conn.commit()

        if args.verbose and case_idx % 50 == 0:
            elapsed = time.time() - t0
            rate = case_idx / elapsed if elapsed > 0 else 0
            eta = (total_cases - case_idx) / rate if rate > 0 else 0
            print(f"  ... {case_idx}/{total_cases} cases ({rate:.0f}/s, ETA {eta:.0f}s)")

    # ── final stats ──
    elapsed = time.time() - t0
    print(f"\n✅ Ingest completed in {elapsed:.1f}s")
    print(f"   Cases: {total_cases}")
    print(f"   Processed: {processed}  Skipped: {skipped}  Errors: {errors}")
    print(f"   Chunks: {chunk_total}")

    # ── ingest_log ──
    store._conn.execute(
        "INSERT INTO ingest_log (started_at, ended_at, kind, source_path, inserted, updated, skipped, errors, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "full-import",
            str(root),
            processed, 0, skipped, errors,
            f"{total_cases} cases, {chunk_total} chunks, {elapsed:.0f}s",
        ),
    )
    store._conn.commit()
    store.close()

    # Print stats via store CLI
    print()
    from via54_store.cli import cmd_stats
    class FakeArgs: db = args.db
    cmd_stats(FakeArgs())


if __name__ == "__main__":
    main()
