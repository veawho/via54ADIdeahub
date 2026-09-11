#!/usr/bin/env python3
"""
creative_enricher.py
Enricher & Ingestion pipeline for Creative Cases into via54_kb.db.
"""

import sys
import os
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from via54_store.embedding import hash_embed, encode_blob, _tokenize


def format_case_markdown(c: Dict[str, Any]) -> str:
    """Format a case into standardized OKF markdown with complete dimensions."""
    meme_tags = c.get("social_meme_tags", [])
    if isinstance(meme_tags, list):
        meme_tags_str = ", ".join(meme_tags)
    else:
        meme_tags_str = str(meme_tags)

    md = f"""# {c.get('brand', '未知品牌')} — {c.get('title', '创意案例')}

> **案例来源**: {c.get('source', 'digitaling')} ({c.get('source_url', '')})
> **所属行业**: {c.get('industry', 'Other')}
> **发布年份**: {c.get('published_year', 2024)} | **发布日期**: {c.get('published_date', '')}
> **创意代理/团队**: {c.get('agency', '待查证')}
> **社交热梗/网感标签**: {meme_tags_str}

---

## 🎯 核心口号资产
- **战役/创意口号 (Campaign Slogan)**: {c.get('campaign_slogan', '暂无')}
- **品牌定位口号 (Brand Slogan)**: {c.get('brand_slogan', '暂无')}

---

## 💡 创意原点 (Creative Origin)
1. **对品牌 (Brand Context)**:
   {c.get('brand_context', '')}
2. **对产品 (Product Features)**:
   {c.get('product_feature', '')}
3. **对市场竞争 (Market Competition)**:
   {c.get('market_competition', '')}
4. **对消费趋势 (Consumer Trend)**:
   {c.get('consumer_trend', '')}
5. **对消费者洞察 (Consumer Insight)**:
   {c.get('consumer_insight', '')}

---

## 🚀 核心洞察与传播 (Core Insight & Execution)
1. **创意核心目标**:
   {c.get('creative_target', '')}
2. **传播裂变机制与社交效果**:
   {c.get('viral_effect', '')}
3. **品牌/产品记忆度提升机制**:
   {c.get('memory_anchor', '')}

---

## 📝 详细内容与物料
{c.get('full_markdown', c.get('content', ''))}
"""
    return md.strip()


def ingest_creative_case(db_path: Path, c: Dict[str, Any]) -> int:
    """Ingest a single case into SQL and Vector tables."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    social_memes = c.get("social_meme_tags", [])
    social_memes_json = json.dumps(social_memes, ensure_ascii=False)
    md_content = format_case_markdown(c)

    cursor.execute("""
        INSERT INTO creative_cases (
            source, source_url, title, brand, industry, published_year, published_date,
            agency, brand_context, product_feature, market_competition,
            consumer_trend, consumer_insight, creative_target, viral_effect,
            memory_anchor, social_meme_tags, campaign_slogan, brand_slogan,
            raw_content, full_markdown, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
        )
        ON CONFLICT(source_url) DO UPDATE SET
            title=excluded.title,
            brand=excluded.brand,
            industry=excluded.industry,
            published_year=excluded.published_year,
            brand_context=excluded.brand_context,
            product_feature=excluded.product_feature,
            market_competition=excluded.market_competition,
            consumer_trend=excluded.consumer_trend,
            consumer_insight=excluded.consumer_insight,
            creative_target=excluded.creative_target,
            viral_effect=excluded.viral_effect,
            memory_anchor=excluded.memory_anchor,
            social_meme_tags=excluded.social_meme_tags,
            campaign_slogan=excluded.campaign_slogan,
            brand_slogan=excluded.brand_slogan,
            full_markdown=excluded.full_markdown,
            updated_at=CURRENT_TIMESTAMP
    """, (
        c.get("source", "digitaling"),
        c.get("source_url", f"custom_{time.time()}"),
        c.get("title", ""),
        c.get("brand", ""),
        c.get("industry", "Other"),
        int(c.get("published_year", 2024)),
        c.get("published_date", ""),
        c.get("agency", ""),
        c.get("brand_context", ""),
        c.get("product_feature", ""),
        c.get("market_competition", ""),
        c.get("consumer_trend", ""),
        c.get("consumer_insight", ""),
        c.get("creative_target", ""),
        c.get("viral_effect", ""),
        c.get("memory_anchor", ""),
        social_memes_json,
        c.get("campaign_slogan", ""),
        c.get("brand_slogan", ""),
        c.get("content", ""),
        md_content,
    ))
    case_id = cursor.lastrowid
    conn.commit()

    bundle_id = 1
    rel_path = f"creative_cases/{c.get('brand')}_{c.get('published_year')}_{case_id}.md"
    body_hash = hashlib.sha256(md_content.encode("utf-8")).hexdigest()

    cursor.execute("""
        INSERT INTO concepts (
            bundle_id, rel_path, type, title, description, resource,
            tags_json, timestamp, source_path, mtime, body_size, body_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(bundle_id, rel_path) DO UPDATE SET
            title=excluded.title,
            body_hash=excluded.body_hash,
            body_size=excluded.body_size
    """, (
        bundle_id,
        rel_path,
        "case_study",
        c.get("title", ""),
        f"【{c.get('brand')}】{c.get('campaign_slogan', '')}",
        c.get("source_url", ""),
        social_memes_json,
        c.get("published_date", ""),
        str(db_path),
        time.time(),
        len(md_content.encode("utf-8")),
        body_hash,
    ))
    
    cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
    row = cursor.fetchone()
    concept_id = row[0] if row else cursor.lastrowid

    paragraphs = [p.strip() for p in md_content.split("\n\n") if p.strip()]
    cursor.execute("DELETE FROM concept_chunks WHERE concept_id=?", (concept_id,))

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
    return case_id


def ingest_batch_benchmark(db_path: Path):
    """Ingest standard benchmark cases into DB."""
    from tools.digitaling_topys_collector import get_benchmarking_cases
    cases = get_benchmarking_cases()
    print(f"Ingesting {len(cases)} benchmark cases into {db_path}...")
    for c in cases:
        cid = ingest_creative_case(db_path, c)
        print(f" -> Ingested case #{cid}: [{c.get('source')}] {c.get('brand')} - {c.get('title')}")
    print("Ingestion complete.")


if __name__ == "__main__":
    db = PROJECT_ROOT / "via54_kb.db"
    ingest_batch_benchmark(db)
