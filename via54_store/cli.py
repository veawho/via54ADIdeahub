"""via54_store CLI — `python -m via54_store <sub>`.

Subcommands:
    init           Create the schema in a fresh DB (default path: via54_kb.db)
    stats          Print row counts for every table
    search "q"     Hybrid search; --top-k N (default 5), --db PATH
    vectors-stats  Show vector coverage / dim mean / zero-vector ratio
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from .embedding import decode_blob
from .retrieval import HybridRetriever
from .store import KBStore


def cmd_init(args) -> int:
    store = KBStore(args.db)
    store.init_schema()
    store.close()
    print(f"✓ initialized schema in {args.db}")
    return 0


def cmd_stats(args) -> int:
    store = KBStore(args.db)
    store.init_schema()  # no-op if already present
    rows = {
        "bundles":   store.bundle_count(),
        "concepts":  store.concept_count(),
        "chunks":    store.chunk_count(),
        "links":     store.link_count(),
        "terms":     store.term_row_count(),
        "vectors":   store.vector_count(),
    }
    store.close()
    width = max(len(k) for k in rows) + 1
    print(f"DB: {args.db}")
    for k, v in rows.items():
        print(f"  {k.ljust(width)} {v}")
    return 0


def cmd_vectors_stats(args) -> int:
    store = KBStore(args.db)
    store.init_schema()
    conn = store._conn
    n_vec = int(conn.execute("SELECT COUNT(*) AS c FROM chunk_vector_blob").fetchone()["c"])
    n_chunks = int(conn.execute("SELECT COUNT(*) AS c FROM concept_chunks").fetchone()["c"])
    if n_vec == 0:
        print("no vectors stored")
        store.close()
        return 0
    rows = conn.execute(
        "SELECT vec, dim FROM chunk_vector_blob JOIN chunk_vector_meta USING(chunk_id)"
    ).fetchall()
    total_dim = 0
    zero_count = 0
    for r in rows:
        vec = decode_blob(bytes(r["vec"]))
        total_dim += r["dim"]
        if all(v == 0.0 for v in vec):
            zero_count += 1
    coverage = n_vec / max(1, n_chunks)
    avg_dim = total_dim / max(1, n_vec)
    zero_ratio = zero_count / max(1, n_vec)
    print(f"DB: {args.db}")
    print(f"  chunks with vectors : {n_vec}/{n_chunks}  (coverage {coverage:.1%})")
    print(f"  avg dimension       : {avg_dim:.0f}")
    print(f"  zero-vector ratio   : {zero_ratio:.1%}")
    store.close()
    return 0


def cmd_search(args) -> int:
    store = KBStore(args.db)
    store.init_schema()
    retriever = HybridRetriever(store, dim=args.dim, vec_weight=args.vec_weight, txt_weight=args.txt_weight)
    results = retriever.search(args.query, top_k=args.top_k)
    store.close()
    print(f"query: {args.query!r}")
    print(f"hits : {len(results)}")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] (score={r['score']}  vec={r['score_vec']}  txt={r['score_txt']})")
        print(f"     {r['title']} [{r['type']}]")
        if r.get("resource"):
            print(f"     res : {r['resource']}")
        if r.get("tags"):
            print(f"     tags: {','.join(r['tags'])}")
        if r.get("snippet"):
            snip = r["snippet"].replace("\n", " ")[:200]
            print(f"     snip: {snip}…")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m via54_store")
    p.add_argument("--db", default="via54_kb.db", help="Path to SQLite DB (default: via54_kb.db)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create schema tables")
    p_init.set_defaults(func=cmd_init)

    p_stats = sub.add_parser("stats", help="Show row counts")
    p_stats.set_defaults(func=cmd_stats)

    p_vs = sub.add_parser("vectors-stats", help="Vector coverage stats")
    p_vs.set_defaults(func=cmd_vectors_stats)

    p_search = sub.add_parser("search", help="Hybrid search")
    p_search.add_argument("query")
    p_search.add_argument("--top-k", type=int, default=5)
    p_search.add_argument("--dim", type=int, default=256)
    p_search.add_argument("--vec-weight", type=float, default=0.6)
    p_search.add_argument("--txt-weight", type=float, default=0.4)
    p_search.set_defaults(func=cmd_search)

    return p


def _resolve_db(args, parser) -> str:
    """Top-level --db is the single source of truth."""
    return getattr(args, "db", "via54_kb.db")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
