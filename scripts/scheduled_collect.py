#!/usr/bin/env python3
"""
scheduled_collect.py — Automated & Incremental Ad Case Ingestion Runner
Periodically crawls new cases from Digitaling/TOPYS, deduplicates by URL/title,
and ingests high quality cases into via54_kb.db.
"""

import sys
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.digitaling_topys_collector import get_benchmarking_cases
from agents.master_linguistic_engine import MasterLinguisticEngine

def run_incremental_collection():
    db_path = PROJECT_ROOT / "via54_kb.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    engine = MasterLinguisticEngine()
    cases = get_benchmarking_cases()
    new_count = 0
    skipped_count = 0

    for c in cases:
        cursor.execute("SELECT case_id FROM creative_cases WHERE source_url = ? OR title = ?", (c.get("source_url"), c.get("title")))
        existing = cursor.fetchone()
        if existing:
            skipped_count += 1
            continue

        slogan = c.get("campaign_slogan") or c.get("brand_slogan") or c.get("title", "")
        # Run 3-D reverse-engineering analysis
        if slogan:
            analysis = engine.deep_reverse_engineer(slogan)
            analysis_summary = f"\n\n## 🎵 3-D 语言学与神经直觉逆向拆解\n- 读音节拍分析: {analysis.get('phonetic', {}).get('cadence', {}).get('pattern', '对称节奏')}\n- 语义张力对立: {analysis.get('semantic', {}).get('core_tension', {}).get('tension_formula', 'A != B')}\n- 0.5s人类直觉: {analysis.get('intuition', {}).get('neuro_trigger', {}).get('mechanism', '镜像神经元触发')}\n- 综合卓越度: {analysis.get('composite_score', 90)}/100"
            c["full_markdown"] = (c.get("full_markdown", "") + analysis_summary).strip()

        tags_str = json.dumps(c.get("social_meme_tags", []), ensure_ascii=False)
        cursor.execute("""
        INSERT INTO creative_cases (
            source, source_url, title, brand, industry, published_year, published_date, agency,
            brand_context, product_feature, market_competition, consumer_trend, consumer_insight,
            creative_target, viral_effect, memory_anchor, social_meme_tags, campaign_slogan, brand_slogan, full_markdown
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c.get("source", "digitaling"),
            c.get("source_url", ""),
            c.get("title", ""),
            c.get("brand", ""),
            c.get("industry", "Other"),
            c.get("published_year", 2026),
            c.get("published_date", datetime.now().strftime("%Y-%m-%d")),
            c.get("agency", ""),
            c.get("brand_context", ""),
            c.get("product_feature", ""),
            c.get("market_competition", ""),
            c.get("consumer_trend", ""),
            c.get("consumer_insight", ""),
            c.get("creative_target", ""),
            c.get("viral_effect", ""),
            c.get("memory_anchor", ""),
            tags_str,
            c.get("campaign_slogan", ""),
            c.get("brand_slogan", ""),
            c.get("full_markdown", "")
        ))
        new_count += 1

    conn.commit()
    conn.close()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Incremental collection complete: {new_count} new cases analyzed & added, {skipped_count} existing cases skipped.")
    return {"new_count": new_count, "skipped_count": skipped_count}

if __name__ == "__main__":
    run_incremental_collection()

