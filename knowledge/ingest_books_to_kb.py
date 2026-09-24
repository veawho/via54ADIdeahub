#!/usr/bin/env python3
"""
ingest_books_to_kb.py
Ingests all 24 masterclass copywriting books into concepts, concept_chunks,
chunk_terms, chunk_vector_meta, and chunk_vector_blob tables.
"""

import sys
import os
import json
import sqlite3
import hashlib
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from via54_store.embedding import hash_embed, encode_blob, _tokenize

def ingest_books():
    db_path = PROJECT_ROOT / "via54_kb.db"
    json_path = PROJECT_ROOT / "knowledge" / "master_copywriting_books.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    books = data.get("books", [])

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    bundle_id = 1

    for b in books:
        title = f"《{b['title']}》— {b['author']} (大师文案与策略心法)"
        rel_path = f"master_books/{b['book_id']}.md"
        desc = f"【{b['school']}】{b['core_theory']}"
        tags = ["文案书籍", "广告大师", b["school"], b["author"], "策略模型"]
        tags_json = json.dumps(tags, ensure_ascii=False)

        cases_txt = "\n".join([f"- {c['case_name']}: {c['slogan']} ({c['insight']})" for c in b.get("classic_golden_cases", [])])
        methods_txt = "\n".join([f"- {m}" for m in b.get("writing_methods", [])])
        full_text = f"""# {title}
作者: {b['author']} | 学派: {b['school']}
核心理论: {b['core_theory']}
思考方式: {b['thinking_paradigm']}

## 战略策略框架
{json.dumps(b.get('strategy_framework', {}), ensure_ascii=False, indent=2)}

## 写作技法与修辞模型
{methods_txt}

## 经典金句与案例拆解
{cases_txt}

## 算法启发
{json.dumps(b.get('algorithmic_heuristics', {}), ensure_ascii=False, indent=2)}
"""
        body_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()

        cursor.execute("""
            INSERT INTO concepts (
                bundle_id, rel_path, type, title, description, resource,
                tags_json, timestamp, source_path, mtime, body_size, body_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
            ON CONFLICT(bundle_id, rel_path) DO UPDATE SET
                title=excluded.title,
                description=excluded.description,
                tags_json=excluded.tags_json,
                body_hash=excluded.body_hash,
                body_size=excluded.body_size
        """, (
            bundle_id,
            rel_path,
            "book_methodology",
            title,
            desc,
            f"knowledge/books/{b['book_id']}.md",
            tags_json,
            str(db_path),
            time.time(),
            len(full_text.encode("utf-8")),
            body_hash
        ))

        cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
        concept_id = cursor.fetchone()[0]

        # Chunks
        cursor.execute("DELETE FROM concept_chunks WHERE concept_id=?", (concept_id,))
        paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        for idx, p in enumerate(paragraphs):
            cursor.execute("""
                INSERT INTO concept_chunks (concept_id, chunk_idx, text, char_start, char_end, tokens_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (concept_id, idx, p, 0, len(p), json.dumps([], ensure_ascii=False)))
            chunk_id = cursor.lastrowid

            tokens = _tokenize(p)
            for tok in set(tokens):
                cursor.execute("""
                    INSERT OR IGNORE INTO chunk_terms (term, chunk_id, tf)
                    VALUES (?, ?, ?)
                """, (tok[:50], chunk_id, 1.0))

            vec = hash_embed(p, dim=256)
            blob = encode_blob(vec)

            cursor.execute("""
                INSERT OR REPLACE INTO chunk_vector_meta (chunk_id, dim, norm, model)
                VALUES (?, ?, ?, ?)
            """, (chunk_id, 256, 1.0, "blake2b-hash-256"))

            cursor.execute("""
                INSERT OR REPLACE INTO chunk_vector_blob (chunk_id, vec, model)
                VALUES (?, ?, ?)
            """, (chunk_id, blob, "blake2b-hash-256"))

    conn.commit()
    conn.close()
    print(f"✅ Successfully ingested all {len(books)} master books into concepts & vector store!")

if __name__ == "__main__":
    ingest_books()
