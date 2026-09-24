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

    print(f"✅ Successfully ingested all {len(books)} master books into concepts & vector store!")

    # Ingest divine translations
    from knowledge.divine_translations_corpus import DIVINE_TRANSLATIONS_DATA
    for item in DIVINE_TRANSLATIONS_DATA:
        title = f"【神仙翻译】{item['divine_translation']} (译者: {item['translator']})"
        rel_path = f"divine_translations/{item['id']}.md"
        desc = f"【{item['category']}】原文: {item['original_text']} | {item['reconstruction_mechanism'][:80]}"
        tags = ["神仙翻译", "双语金句", item["category"], item["translator"], "语言二次重构"]
        tags_json = json.dumps(tags, ensure_ascii=False)

        full_text = f"""# {title}
分类: {item['category']} | 语言: {item['source_language']} -> {item['target_language']}
原文: {item['original_text']} (出处: {item['original_author_or_source']})
神仙译文: {item['divine_translation']} (译者: {item['translator']})
直译对照: {item['literal_translation']}

## 语言二次重构美学密码
{item['reconstruction_mechanism']}

## 文案创作启示
{item['copywriting_insight']}
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
            "divine_translation",
            title,
            desc,
            f"knowledge/divine_translations/{item['id']}.md",
            tags_json,
            str(db_path),
            time.time(),
            len(full_text.encode("utf-8")),
            body_hash
        ))

        cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
        concept_id = cursor.fetchone()[0]

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

    print(f"✅ Successfully ingested all {len(DIVINE_TRANSLATIONS_DATA)} divine translations into concepts & vector store!")

    # Ingest Classical Chinese Masterpieces
    from knowledge.classical_chinese_corpus import CLASSICAL_CHINESE_DATA
    for item in CLASSICAL_CHINESE_DATA:
        title = f"《{item['title']}》— {item['author']} ({item['dynasty']})"
        rel_path = f"classical_chinese/{item['id']}_{item['title']}.md"
        desc = f"【{item['genre']} · {item['emotional_archetype']}】{item['golden_lines'][:80]}"
        tags = ["古诗词", "古文名篇", item["author"], item["dynasty"], item["emotional_archetype"], "经典文学"]
        tags_json = json.dumps(tags, ensure_ascii=False)

        full_text = f"""# {title}
体裁: {item['genre']} | 朝代: {item['dynasty']} | 作者: {item['author']}
情感原型: {item['emotional_archetype']}

## 传世千古金句
{item['golden_lines']}

## 原典全文
{item['full_text']}

## 修辞与美学机制
{item['rhetorical_mechanisms']}

## 当代文案与品牌主张应用密码
{item['copywriting_application']}
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
            "classical_chinese",
            title,
            desc,
            f"knowledge/classical_chinese/{item['id']}.md",
            tags_json,
            str(db_path),
            time.time(),
            len(full_text.encode("utf-8")),
            body_hash
        ))

        cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
        concept_id = cursor.fetchone()[0]

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

    print(f"✅ Successfully ingested all {len(CLASSICAL_CHINESE_DATA)} Classical Chinese Masterpieces into concepts & vector store!")

    # Ingest Oscar Wilde Epigrams
    from knowledge.oscar_wilde_corpus import OSCAR_WILDE_DATA
    for item in OSCAR_WILDE_DATA:
        title = f"【王尔德金句】{item['chinese_translation']} ({item['work']})"
        rel_path = f"oscar_wilde/{item['id']}.md"
        desc = f"【{item['theme']}】{item['english_quote']} | {item['paradox_mechanism'][:80]}"
        tags = ["奥斯卡王尔德", "唯美主义", "悖论金句", item["theme"], item["work"], "反常识修辞"]
        tags_json = json.dumps(tags, ensure_ascii=False)

        full_text = f"""# {title}
出处: {item['work']} | 主题: {item['theme']}
英文原文: {item['english_quote']}
经典汉译: {item['chinese_translation']}

## 悖论与修辞机制
{item['paradox_mechanism']}

## 现代广告文案与品牌主张应用
{item['copywriting_application']}
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
            "wilde_epigram",
            title,
            desc,
            f"knowledge/oscar_wilde/{item['id']}.md",
            tags_json,
            str(db_path),
            time.time(),
            len(full_text.encode("utf-8")),
            body_hash
        ))

        cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
        concept_id = cursor.fetchone()[0]

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
    print(f"✅ Successfully ingested all {len(OSCAR_WILDE_DATA)} Oscar Wilde Epigrams into concepts & vector store!")

if __name__ == "__main__":
    ingest_books()
