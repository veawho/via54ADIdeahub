#!/usr/bin/env python3
"""Print vector statistics for a via54 KBStore.

Usage:
    python tools/vector_stats.py [--db via54_kb.db]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
sys.path.insert(0, str(_REPO))

from via54_store import KBStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="via54_kb.db")
    args = parser.parse_args()

    store = KBStore(args.db)
    conn = store._conn

    total_chunks = int(conn.execute("SELECT COUNT(*) FROM concept_chunks").fetchone()[0])
    vec_count = int(conn.execute("SELECT COUNT(*) FROM chunk_vector_blob").fetchone()[0])
    meta_count = int(conn.execute("SELECT COUNT(*) FROM chunk_vector_meta").fetchone()[0])

    if meta_count == 0:
        print(f"📊 Vector Statistics for {args.db}")
        print(f"   Chunks: {total_chunks}")
        print(f"   Vectors: {vec_count}")
        print("   Coverage: 0% (no vectors)")
        store.close()
        return

    dim_row = conn.execute("SELECT dim FROM chunk_vector_meta LIMIT 1").fetchone()
    dim = int(dim_row[0]) if dim_row else 0

    zero_count = int(conn.execute(
        "SELECT COUNT(*) FROM chunk_vector_meta WHERE norm = 0.0"
    ).fetchone()[0])

    avg_norm = float(conn.execute(
        "SELECT AVG(norm) FROM chunk_vector_meta"
    ).fetchone()[0])

    models = conn.execute(
        "SELECT model, COUNT(*) FROM chunk_vector_meta GROUP BY model"
    ).fetchall()

    coverage = 100.0 * vec_count / total_chunks if total_chunks > 0 else 0.0

    print(f"📊 Vector Statistics for {args.db}")
    print(f"   Chunks:           {total_chunks}")
    print(f"   Vectors:          {vec_count}")
    print(f"   Coverage:         {coverage:.1f}%")
    print(f"   Dimension:        {dim}")
    print(f"   Avg L2 norm:      {avg_norm:.4f}")
    print(f"   Zero vectors:     {zero_count}")
    print(f"   Per model:        {', '.join(f'{r[0]}: {r[1]}' for r in models)}")

    store.close()


if __name__ == "__main__":
    main()
