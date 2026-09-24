#!/usr/bin/env python3
"""
ingest_books_to_kb.py
Ingests all knowledge corpora into concepts, concept_chunks,
chunk_terms, chunk_vector_meta, and chunk_vector_blob tables:
  1. Masterclass copywriting books (27 books)
  2. Divine translations (18 items)
  3. Classical Chinese full texts (53 items)
  4. Classical Chinese golden quotes (52 items)
  5. Master Writers Originals (24 items)
  6. Master Writers Translations (24 items)
  7. Master Writers Golden Epigrams (26 items)
"""

import sys
import os
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from via54_store.embedding import hash_embed, encode_blob, _tokenize


def _ingest_concept(
    cursor,
    bundle_id: int,
    rel_path: str,
    c_type: str,
    title: str,
    desc: str,
    resource: str,
    tags: List[str],
    full_text: str,
    db_path: Path
):
    """Helper to upsert a concept and compute chunks, terms, and vectors."""
    body_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
    tags_json = json.dumps(tags, ensure_ascii=False)

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
        c_type,
        title,
        desc,
        resource,
        tags_json,
        str(db_path),
        time.time(),
        len(full_text.encode("utf-8")),
        body_hash
    ))

    cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
    row = cursor.fetchone()
    if not row:
        return
    concept_id = row[0]

    # Clear old chunks
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


def ingest_all():
    db_path = PROJECT_ROOT / "via54_kb.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    bundle_id = 1

    # 1. Master copywriting books
    json_path = PROJECT_ROOT / "knowledge" / "master_copywriting_books.json"
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
        books = data.get("books", [])
        for b in books:
            title = f"《{b['title']}》— {b['author']} (大师文案与策略心法)"
            rel_path = f"master_books/{b['book_id']}.md"
            desc = f"【{b['school']}】{b['core_theory']}"
            tags = ["文案书籍", "广告大师", b["school"], b["author"], "策略模型"]
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
            _ingest_concept(
                cursor, bundle_id, rel_path, "book_methodology", title, desc,
                f"knowledge/books/{b['book_id']}.md", tags, full_text, db_path
            )
        print(f"✅ Ingested {len(books)} master books into concepts & vector store.")

    # 2. Divine translations
    from knowledge.divine_translations_corpus import DIVINE_TRANSLATIONS_DATA
    for item in DIVINE_TRANSLATIONS_DATA:
        title = f"【神仙翻译】{item['divine_translation']} (译者: {item['translator']})"
        rel_path = f"divine_translations/{item['id']}.md"
        desc = f"【{item['category']}】原文: {item['original_text']} | {item['reconstruction_mechanism'][:80]}"
        tags = ["神仙翻译", "双语金句", item["category"], item["translator"], "语言二次重构"]
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
        _ingest_concept(
            cursor, bundle_id, rel_path, "divine_translation", title, desc,
            f"knowledge/divine_translations/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(DIVINE_TRANSLATIONS_DATA)} divine translations into concepts & vector store.")

    # 3. Classical Chinese Fulltexts
    from knowledge.build_classical_chinese_full_kb import FULLTEXT_RECORDS, GOLDEN_QUOTES_DATA as CLASSICAL_QUOTES
    for item in FULLTEXT_RECORDS:
        title = f"【中华原典全文】《{item['title']}》— {item['author']} ({item['dynasty']}·{item['genre']})"
        rel_path = f"classical_fulltext/{item['id']}_{item['title']}.md"
        desc = f"【{item['genre']} · {item['dynasty']}】{item['author']}《{item['title']}》| {item['aesthetic_features'][:80]}"
        tags = ["古典全文", item["genre"], item["dynasty"], item["author"], "中华文脉", item["title"]]
        full_text = f"""# {title}
体裁: {item['genre']} | 朝代: {item['dynasty']} | 作者: {item['author']}
曲调/篇题: {item.get('subtitle_or_tune', '')}

## 名篇全文
{item['full_text']}

## 背景题解与注释
{item['background_and_annotation']}

## 美学特质与文气韵律
{item['aesthetic_features']}
"""
        _ingest_concept(
            cursor, bundle_id, rel_path, "classical_fulltext", title, desc,
            f"knowledge/classical_fulltext/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(FULLTEXT_RECORDS)} Classical Chinese Fulltexts into concepts & vector store.")

    # 4. Classical Chinese Golden Quotes
    for item in CLASSICAL_QUOTES:
        title = f"【千古金句密码】{item['quote_text'][:30]}... ({item['work_title']})"
        rel_path = f"classical_golden_quote/{item['id']}.md"
        desc = f"【{item['genre']} · {item['emotional_archetype']}】{item['work_title']} | {item['rhetorical_mechanisms'][:80]}"
        tags = ["古典金句", item["genre"], item["dynasty"], item["author"], item["emotional_archetype"], "文案母体"]
        full_text = f"""# {title}
出处: 《{item['work_title']}》 | 朝代: {item['dynasty']} | 作者: {item['author']} | 体裁: {item['genre']}
情感原型: {item['emotional_archetype']}

## 传世千古金句
{item['quote_text']}

## 修辞与美学机制
{item['rhetorical_mechanisms']}

## 当代文案与品牌主张应用密码
{item['copywriting_application']}
"""
        _ingest_concept(
            cursor, bundle_id, rel_path, "classical_golden_quote", title, desc,
            f"knowledge/classical_golden_quotes/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(CLASSICAL_QUOTES)} Classical Chinese Golden Quotes into concepts & vector store.")

    # 5. Master Writers Originals
    from knowledge.build_master_writers_triplet_kb import ORIGINALS_DATA, TRANSLATIONS_DATA, GOLDEN_QUOTES_DATA as WRITER_QUOTES
    for item in ORIGINALS_DATA:
        title = f"【大师原著外文】{item['work_title_en']} — {item['writer_name_en']} ({item['work_title_cn']})"
        rel_path = f"writer_original/{item['id']}.md"
        desc = f"【{item['source_language']} · {item['genre']}】{item['writer_name_cn']}《{item['work_title_cn']}》| {item['themes_and_philosophy'][:80]}"
        tags = ["大师原作", item["writer_name_cn"], item["writer_name_en"], item["source_language"], item["genre"]]
        full_text = f"""# {title}
作家: {item['writer_name_cn']} ({item['writer_name_en']})
原著名: {item['work_title_en']} ({item['work_title_cn']})
语种: {item['source_language']} | 体裁: {item['genre']}

## 外文原版章节节选 (Original Text Extract)
{item['original_text_extract']}

## 主题思潮与哲学内核 (Themes & Philosophy)
{item['themes_and_philosophy']}
"""
        _ingest_concept(
            cursor, bundle_id, rel_path, "writer_original", title, desc,
            f"knowledge/writer_originals/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(ORIGINALS_DATA)} Master Writers Originals into concepts & vector store.")

    # 6. Master Writers Translations
    for item in TRANSLATIONS_DATA:
        title = f"【名家译本文选】《{item['work_title_cn']}》— 译者: {item['translator']}"
        rel_path = f"writer_translation/{item['id']}.md"
        desc = f"【{item['translator']}名译】《{item['work_title_cn']}》| {item['translation_school_and_style'][:80]}"
        tags = ["名家译本", item["translator"], item["work_title_cn"], "翻译美学", "经典译文"]
        full_text = f"""# {title}
作品: 《{item['work_title_cn']}》 | 权威译者: {item['translator']}

## 名家译文正文 (Translation Text)
{item['translation_text']}

## 翻译流派与句式美学 (Translation School & Style)
{item['translation_school_and_style']}

## 译者手记与美学评注 (Translator Commentary)
{item['translator_commentary']}
"""
        _ingest_concept(
            cursor, bundle_id, rel_path, "writer_translation", title, desc,
            f"knowledge/writer_translations/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(TRANSLATIONS_DATA)} Master Writers Translations into concepts & vector store.")

    # 7. Master Writers Golden Epigrams
    for item in WRITER_QUOTES:
        tags_list = json.loads(item["theme_tags_json"])
        title = f"【大师金句双语】{item['translated_quote_cn'][:30]}... ({item['writer_name_cn']}《{item['source_work']}》)"
        rel_path = f"writer_golden_quote/{item['id']}.md"
        desc = f"【{item['writer_name_cn']}】{item['original_quote_lang'][:80]} | {item['rhetorical_and_paradox_mechanism'][:80]}"
        tags = ["大师金句", item["writer_name_cn"], item["writer_name_en"], item["translator"]] + tags_list
        full_text = f"""# {title}
作家: {item['writer_name_cn']} ({item['writer_name_en']})
出处作品: {item['source_work']} | 译者: {item['translator']}
主题标签: {item['theme_tags_json']}

## 原文与经典汉译
外文原句: {item['original_quote_lang']}
经典汉译: {item['translated_quote_cn']}

## 悖论、反转与修辞机制 (Paradox & Rhetorical Mechanism)
{item['rhetorical_and_paradox_mechanism']}

## 现代广告文案与品牌主张实战应用
{item['copywriting_application']}
"""
        _ingest_concept(
            cursor, bundle_id, rel_path, "writer_golden_quote", title, desc,
            f"knowledge/writer_golden_quotes/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(WRITER_QUOTES)} Master Writers Golden Epigrams into concepts & vector store.")

    # 8. Psycholinguistic Activation Canon
    from knowledge.build_psycholinguistic_activation_kb import PSYCHOLINGUISTIC_CANON
    for item in PSYCHOLINGUISTIC_CANON:
        title = f"【认知心理学与神经语言学】{item['school_name_cn']} ({item['school_name_en']})"
        rel_path = f"psycholinguistic_canon/{item['id']}.md"
        desc = f"【{item['school_name_cn']}】核心代表: {item['key_figures']} | 机制: {item['core_psychological_mechanism'][:80]}"
        tags = ["心理语言学", "神经营销学", "认知科学", "文案转化", item["school_name_cn"]]
        papers_list = json.loads(item["seminal_papers_and_books"])
        papers_md = "\n".join([f"- {p}" for p in papers_list])
        full_text = f"""# {title}
学派与理论: {item['school_name_cn']} ({item['school_name_en']})
核心学者与奠基人: {item['key_figures']}
激活大脑神经区域: {item['neural_regions_activated']}

## 核心心理学与神经认知机制
{item['core_psychological_mechanism']}

## 经典专著与顶会/顶刊奠基论文 (Seminal Papers & Books)
{papers_md}

## 算法度量与量化计算公式
`{item['algorithmic_metric_formula']}`

## 文案实战转化启示与心法
{item['copywriting_application_insight']}

## 标杆案例对标
{item['canonical_benchmark_cases']}
"""
        _ingest_concept(
            cursor, bundle_id, rel_path, "psycholinguistic_canon", title, desc,
            f"knowledge/psycholinguistic_canon/{item['id']}.md", tags, full_text, db_path
        )
    print(f"✅ Ingested {len(PSYCHOLINGUISTIC_CANON)} Psycholinguistic Activation Canon items into concepts & vector store.")

    conn.commit()
    conn.close()
    print("🌟 All Knowledge Corpora successfully ingested and indexed into concepts and Blake2b-256 vector store!")


if __name__ == "__main__":
    ingest_all()
