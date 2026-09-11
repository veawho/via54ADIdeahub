#!/usr/bin/env python3
"""
pun_db_builder.py — Pun & Double Entendre Creative Cases Database Builder
Stores and evaluates wordplays, puns, and conceptual double entendres.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "via54_kb.db"

def init_pun_table(db_path: Path = DB_PATH):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pun_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        industry TEXT,
        pun_text TEXT NOT NULL,
        surface_meaning TEXT,
        hidden_meaning TEXT,
        phonetic_pair TEXT,
        audience_type TEXT DEFAULT "default",
        quality_score REAL DEFAULT 4.0,
        critique_notes TEXT,
        example_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def insert_pun_case(data: Dict[str, Any], db_path: Path = DB_PATH):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pun_cases (
        brand, industry, pun_text, surface_meaning, hidden_meaning, phonetic_pair, audience_type, quality_score, critique_notes, example_link
    ) VALUES (:brand, :industry, :pun_text, :surface_meaning, :hidden_meaning, :phonetic_pair, :audience_type, :quality_score, :critique_notes, :example_link)
    """, data)
    conn.commit()
    conn.close()

def get_pun_cases(audience_type: str = "", min_score: float = 4.0, limit: int = 10, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if audience_type and audience_type != "default":
        cursor.execute("""
        SELECT * FROM pun_cases 
        WHERE (audience_type = ? OR audience_type = "default") AND quality_score >= ?
        ORDER BY quality_score DESC
        LIMIT ?
        """, (audience_type, min_score, limit))
    else:
        cursor.execute("""
        SELECT * FROM pun_cases 
        WHERE quality_score >= ?
        ORDER BY quality_score DESC
        LIMIT ?
        """, (min_score, limit))
        
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_pun_table()
    cases = get_pun_cases()
    print(f"Total pun cases available: {len(cases)}")
    for c in cases:
        b_name = c['brand']
        p_text = c['pun_text']
        q_score = c['quality_score']
        print(f"- [{b_name}] {p_text} (评分: {q_score})")
