"""Tests for via54_store — SQLite schema + embedding + retriever."""

from __future__ import annotations

import json
import math
import os
import sqlite3
from pathlib import Path

import pytest

from via54_store import (
    KBStore,
    HybridRetriever,
    cosine,
    decode_blob,
    encode_blob,
    hash_embed,
    l2_normalize,
    tokenize,
)
from via54_store.embedding import _tokenize


# ─────────────────────────── fixtures ───────────────────────────
@pytest.fixture()
def tmp_db(tmp_path: Path) -> str:
    db = tmp_path / "kb.db"
    return str(db)


@pytest.fixture()
def store(tmp_db: str) -> KBStore:
    s = KBStore(tmp_db)
    s.init_schema()
    yield s
    s.close()


def _ingest_demo(store: KBStore, n_concepts: int = 3) -> dict:
    """Seed the store with `n_concepts` toy concepts & chunks & vectors."""
    bid = store.upsert_bundle(
        name="demo-bundle",
        root_path="/tmp/demo",
        version="0.1",
        description="unit-test bundle",
    )
    concept_ids = []
    bodies = [
        (
            "alpha-concept",
            "Alpha brand fitness wearable ad spot",
            ["branding", "fitness"],
        ),
        (
            "beta-concept",
            "Beta cancer awareness social campaign",
            ["healthcare", "awareness"],
        ),
        (
            "gamma-concept",
            "Gamma perfume luxury print campaign",
            ["luxury", "beauty"],
        ),
    ][:n_concepts]
    for rel, title, tags in bodies:
        cid = store.upsert_concept(
            bundle_id=bid,
            rel_path=f"{rel}.md",
            type="concept",
            title=title,
            description=title,
            resource=f"res://{rel}",
            tags=tags,
            timestamp="2024-01-01T00:00:00Z",
            source_path=f"/tmp/demo/{rel}.md",
            mtime=0.0,
            body_size=len(title),
            body_hash="deadbeef",
        )
        # Each concept gets 1 chunk + 1 vector + 1 link.
        text = f"{title} content body for tokenization."
        tokens = _tokenize(text)
        ch_id = store.add_chunk(
            concept_id=cid,
            chunk_idx=0,
            text=text,
            char_start=0,
            char_end=len(text),
            tokens=tokens,
        )
        # Write terms into inverted index too
        tf = store.term_count_doc(tokens)
        for term, cnt in tf.items():
            with store.transaction():
                store._conn.execute(
                    "INSERT OR REPLACE INTO chunk_terms (term, chunk_id, tf) VALUES (?, ?, ?)",
                    (term, ch_id, cnt / max(1, len(tokens))),
                )
        store.add_chunk_vector(ch_id, hash_embed(text, dim=256))
        store.add_link(
            src_concept_id=cid,
            target_path="brand.md",
            link_kind="markdown",
            link_text="see brand",
            position=0,
        )
        store.replace_concept_atomic(
            concept_id=cid,
            doc={
                "title": title,
                "description": title,
                "tags": tags,
                "resource": f"res://{rel}",
                "timestamp": "2024-01-01T00:00:00Z",
                "mtime": 0.0,
                "body_size": len(text),
                "body_hash": "newhash",
            },
            chunks=[{
                "chunk_idx": 0,
                "text": text,
                "char_start": 0,
                "char_end": len(text),
                "tokens": tokens,
            }],
            links=[{
                "target_path": "brand.md",
                "link_kind": "markdown",
                "link_text": "see brand",
                "position": 0,
            }],
            # Keyed by chunk_idx (0), not the now-stale auto chunk_id:
            vectors={0: hash_embed(text, dim=256)},
        )
        concept_ids.append(cid)
    return {"bundle_id": bid, "concept_ids": concept_ids}


# ───────── schema / store ─────────
def test_init_schema_creates_tables(store: KBStore):
    rows = store._conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    names = {r["name"] for r in rows}
    expected = {
        "bundles", "concepts", "concept_links", "concept_chunks",
        "chunk_terms", "chunk_vector_meta", "chunk_vector_blob",
        "concept_index_aggr", "ingest_log",
    }
    assert expected <= names, f"missing: {expected - names}"


def test_upsert_concept_idempotent(store: KBStore):
    bid = store.upsert_bundle("b1", "/tmp/b1")
    cid1 = store.upsert_concept(
        bundle_id=bid, rel_path="a.md", type="concept", title="A",
    )
    cid2 = store.upsert_concept(
        bundle_id=bid, rel_path="a.md", type="concept", title="A-v2",
    )
    assert cid1 == cid2
    row = store._conn.execute(
        "SELECT title FROM concepts WHERE concept_id = ?", (cid1,)
    ).fetchone()
    assert row["title"] == "A-v2"


# ───────── embedding ─────────
def test_hash_embed_deterministic():
    a = hash_embed("hello world", dim=128)
    b = hash_embed("hello world", dim=128)
    assert a == b


def test_hash_embed_unit_norm():
    for txt in ["", "short", "a longer phrase with several words", "中文测试 alpha omega"]:
        v = hash_embed(txt, dim=64)
        norm = math.sqrt(sum(x * x for x in v))
        assert abs(norm - 1.0) < 1e-9 or norm == 0.0, f"norm={norm} for {txt!r}"


def test_hash_embed_dim():
    assert len(hash_embed("hi", dim=8)) == 8
    assert len(hash_embed("hi")) == 256


def test_cosine_identical():
    v = hash_embed("the same string", dim=64)
    assert abs(cosine(v, v) - 1.0) < 1e-6


def test_cosine_orthogonal():
    # Hash collisions are inevitable but on average two random unit vectors
    # are nearly orthogonal. We accept |cos| < 0.5 here.
    a = hash_embed("apple banana cherry", dim=256)
    b = hash_embed("truck engine piston", dim=256)
    assert abs(cosine(a, b)) < 0.5


def test_blob_roundtrip():
    v = hash_embed("round trip", dim=64)
    blob = encode_blob(v)
    assert isinstance(blob, (bytes, bytearray))
    assert len(blob) == len(v) * 4
    out = decode_blob(blob)
    for x, y in zip(v, out):
        assert abs(x - y) < 1e-6


def test_tokenize_basic():
    out = tokenize("Hello World — 42! 北京上海 OK")
    assert any(t in out for t in ("hello", "world", "beijing"))
    assert "ok" in out


# ───────── retriever ─────────
def test_search_returns_ranked_hits(store: KBStore):
    info = _ingest_demo(store, n_concepts=3)
    r = HybridRetriever(store)
    out = r.search("fitness wearable ad", top_k=5)
    assert len(out) > 0
    # alpha should be top
    assert out[0]["title"].lower().startswith("alpha")
    # Each hit carries both scores
    for h in out:
        assert "score" in h and "score_vec" in h and "score_txt" in h
        assert "concept_id" in h and "type" in h


def test_replace_concept_atomic(store: KBStore):
    info = _ingest_demo(store, n_concepts=1)
    cid = info["concept_ids"][0]
    # wipe chunks then re-add via replace_concept_atomic with no vectors
    store.replace_concept_atomic(
        concept_id=cid,
        doc={
            "title": "Alpha brand fitness wearable ad spot",
            "description": "regen",
            "tags": ["branding"],
            "resource": "res://alpha",
            "timestamp": "2024-02-01T00:00:00Z",
            "mtime": 0.0,
            "body_size": 0,
            "body_hash": "x",
        },
        chunks=[],
        links=[],
        vectors=None,
    )
    # Should now have 0 chunks for that concept
    n = store._conn.execute(
        "SELECT COUNT(*) AS c FROM concept_chunks WHERE concept_id = ?",
        (cid,),
    ).fetchone()["c"]
    assert n == 0


def test_link_aggregation(store: KBStore):
    info = _ingest_demo(store, n_concepts=2)
    for cid in info["concept_ids"]:
        n = store._conn.execute(
            "SELECT COUNT(*) AS c FROM concept_links WHERE src_concept_id = ?",
            (cid,),
        ).fetchone()["c"]
        assert n == 1  # one link inserted via _ingest_demo

    # Aggregate row is in place and counts include the rebuild
    row = store._conn.execute(
        "SELECT chunk_count, link_count FROM concept_index_aggr WHERE concept_id = ?",
        (info["concept_ids"][0],),
    ).fetchone()
    assert row["link_count"] == 1
    assert row["chunk_count"] == 1


def test_ingest_log_writes(store: KBStore):
    ing = store.log_ingest_start("bundle", source_path="/tmp/demo", notes="unit-test")
    store.log_ingest_end(ing, inserted=2, updated=0, skipped=1, notes="done")
    row = store._conn.execute(
        "SELECT inserted, skipped, ended_at, notes FROM ingest_log WHERE ingest_id = ?",
        (ing,),
    ).fetchone()
    assert row["inserted"] == 2
    assert row["skipped"] == 1
    assert row["notes"] == "done"
    assert row["ended_at"] is not None


def test_upsert_bundle_idempotent(store: KBStore):
    b1 = store.upsert_bundle("X", "/tmp/x", version="0.1")
    b2 = store.upsert_bundle("X", "/tmp/x", version="0.2")
    assert b1 == b2
    row = store._conn.execute(
        "SELECT version FROM bundles WHERE bundle_id = ?", (b1,)
    ).fetchone()
    assert row["version"] == "0.2"


# ───────── CLI sanity ─────────
def test_cli_init_and_stats(tmp_db: str, capsys):
    from via54_store.cli import main as cli_main
    rc = cli_main(["--db", tmp_db, "init"])
    assert rc == 0
    rc = cli_main(["--db", tmp_db, "stats"])
    out = capsys.readouterr().out
    assert "bundles" in out and "chunks" in out
    rc = cli_main(["--db", tmp_db, "vectors-stats"])
    assert rc == 0


def test_cli_search_smoke(store: KBStore, tmp_db: str, capsys):
    _ingest_demo(store, n_concepts=3)
    from via54_store.cli import main as cli_main
    rc = cli_main(["--db", tmp_db, "search", "fitness wearable", "--top-k", "3"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "alpha" in out.lower()
