"""Hybrid retriever — sparse (TF-IDF) + dense (hash-embed cosine) fusion.

Implementation notes
--------------------
* No numpy / sklearn / sqlite-vec / faiss available. Vector math is in pure
  Python, dense path uses our `hash_embed` + `decode_blob`, sparse path is a
  textbook TF-IDF cosine using inverted-list data already in `chunk_terms`.
* Both paths aggregate from chunks to concepts by taking the **max** chunk
  score so that a long document with one strong match ranks above one with
  many weak ones.
* `load_all_vectors()` caches vector BLOBs in memory the first time a search
  runs; subsequent searches are fast. `invalidate_vector_cache()` should be
  called after any ingest that adds/removes vectors.

Quality is documented in `embed-quality-note.md` — hash embeddings are a
fallback, not a substitute for sentence-transformers.
"""

from __future__ import annotations

import json
import math
import sqlite3
from typing import Dict, List, Optional, Sequence
from .embedding import (
    _tokenize,
    cosine,
    decode_blob,
    hash_embed,
)
from .store import KBStore

# Re-import for public use in case downstream tests rely on it.
__all__ = ["HybridRetriever", "tokenize"]


def tokenize(text: str) -> List[str]:
    """Public tokenizer — same rule as `embedding._tokenize`."""
    return _tokenize(text)


def _term_doc_freq(conn: sqlite3.Connection, terms: Sequence[str]) -> Dict[str, int]:
    if not terms:
        return {}
    placeholders = ",".join("?" for _ in terms)
    rows = conn.execute(
        f"SELECT term, COUNT(DISTINCT chunk_id) AS c "
        f"FROM chunk_terms WHERE term IN ({placeholders}) GROUP BY term",
        tuple(terms),
    ).fetchall()
    return {r[0]: int(r[1]) for r in rows}


def _idf(N: int, df: int) -> float:
    """Smoothed IDF; matches the formula in via54_rag/__init__.py."""
    return math.log(N / (df + 1)) + 1.0


class HybridRetriever:
    """Combines a hash-projected dense cosine with TF-IDF sparse cosine."""

    DEFAULT_DIM = 256

    def __init__(
        self,
        store: KBStore,
        dim: int = DEFAULT_DIM,
        vec_weight: float = 0.6,
        txt_weight: float = 0.4,
    ) -> None:
        self.store = store
        self.dim = dim
        self.vec_weight = vec_weight
        self.txt_weight = txt_weight
        self._vec_cache: Optional[Dict[int, List[float]]] = None

    # ── vector cache ──
    def load_all_vectors(self) -> Dict[int, List[float]]:
        """Pull every (chunk_id, BLOB) into memory once. Memoized."""
        if self._vec_cache is not None:
            return self._vec_cache
        cache: Dict[int, List[float]] = {}
        rows = self.store._conn.execute(
            "SELECT chunk_id, vec FROM chunk_vector_blob"
        ).fetchall()
        for r in rows:
            cache[int(r["chunk_id"])] = decode_blob(bytes(r["vec"]))
        self._vec_cache = cache
        return cache

    def invalidate_vector_cache(self) -> None:
        self._vec_cache = None

    # ── dense path ──
    def _dense_scores(self, q_vec: List[float]) -> Dict[int, float]:
        """Return {concept_id: max chunk cosine} for the query."""
        cache = self.load_all_vectors()
        if not cache or all(v == 0.0 for v in q_vec):
            return {}
        # Per-chunk cosine (query is unit-norm, vectors are unit-norm)
        chunk_scores: Dict[int, float] = {}
        for cid, vec in cache.items():
            if not vec:
                continue
            sim = cosine(q_vec, vec)
            if sim > 0:
                chunk_scores[cid] = sim
        if not chunk_scores:
            return {}
        # Map chunk_id -> concept_id, then take max per concept.
        ids = list(chunk_scores.keys())
        placeholders = ",".join("?" for _ in ids)
        rows = self.store._conn.execute(
            f"SELECT chunk_id, concept_id FROM concept_chunks "
            f"WHERE chunk_id IN ({placeholders})",
            tuple(ids),
        ).fetchall()
        concept_max: Dict[int, float] = {}
        for r in rows:
            cid = int(r["concept_id"])
            s = chunk_scores[int(r["chunk_id"])]
            if s > concept_max.get(cid, 0.0):
                concept_max[cid] = s
        return concept_max

    # ── sparse path ──
    def _sparse_scores(self, query: str) -> Dict[int, float]:
        """Return {concept_id: max TF-IDF cosine over chunks}."""
        tokens = _tokenize(query)
        if not tokens:
            return {}
        conn = self.store._conn
        N = int(conn.execute("SELECT COUNT(*) AS c FROM concept_chunks").fetchone()["c"]) or 1
        df_map = _term_doc_freq(conn, tokens)
        idf_map = {t: _idf(N, df) for t, df in df_map.items()}
        # Pull candidate chunks via inverted index.
        relevant = [t for t in tokens if t in idf_map]
        if not relevant:
            return {}
        placeholders = ",".join("?" for _ in relevant)
        rows = conn.execute(
            f"SELECT DISTINCT chunk_id FROM chunk_terms "
            f"WHERE term IN ({placeholders})",
            tuple(relevant),
        ).fetchall()
        chunk_ids = [int(r["chunk_id"]) for r in rows]
        if not chunk_ids:
            return {}

        # Compute query TF
        q_tf: Dict[str, float] = {}
        for t in tokens:
            q_tf[t] = q_tf.get(t, 0) + 1
        q_len = len(tokens)
        q_tf = {t: c / q_len for t, c in q_tf.items()}
        q_norm_sq = sum((q_tf.get(t, 0.0) * idf_map.get(t, 0.0)) ** 2 for t in tokens)
        q_norm = math.sqrt(q_norm_sq)
        if q_norm == 0.0:
            return {}

        # Load candidate chunk tokens + their TF-IDF norms
        placeholders2 = ",".join("?" for _ in chunk_ids)
        chunk_rows = conn.execute(
            f"SELECT chunk_id, tokens_json FROM concept_chunks "
            f"WHERE chunk_id IN ({placeholders2})",
            tuple(chunk_ids),
        ).fetchall()
        # Per-chunk TF
        chunk_tf: Dict[int, Dict[str, float]] = {}
        for r in chunk_rows:
            cid = int(r["chunk_id"])
            toks = json.loads(r["tokens_json"] or "[]")
            if not toks:
                continue
            tf: Dict[str, float] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            n = len(toks)
            tf = {t: c / n for t, c in tf.items()}
            chunk_tf[cid] = tf

        concept_max: Dict[int, float] = {}
        for cid, toks_tf in chunk_tf.items():
            dot = sum(
                q_tf.get(t, 0.0) * tf_val * idf_map.get(t, 0.0) ** 2
                for t, tf_val in toks_tf.items()
            )
            d_norm_sq = sum(
                (toks_tf.get(t, 0.0) * idf_map.get(t, 0.0)) ** 2 for t in toks_tf
            )
            d_norm = math.sqrt(d_norm_sq)
            if d_norm == 0.0:
                continue
            score = dot / (q_norm * d_norm)
            if score > 0:
                # map chunk -> its concept
                row = conn.execute(
                    "SELECT concept_id FROM concept_chunks WHERE chunk_id = ?",
                    (cid,),
                ).fetchone()
                if not row:
                    continue
                concept_id = int(row["concept_id"])
                if score > concept_max.get(concept_id, 0.0):
                    concept_max[concept_id] = score
        return concept_max

    # ── fusion ──
    def search(
        self,
        query: str,
        top_k: int = 10,
        vec_weight: Optional[float] = None,
        txt_weight: Optional[float] = None,
    ) -> List[Dict]:
        vw = vec_weight if vec_weight is not None else self.vec_weight
        tw = txt_weight if txt_weight is not None else self.txt_weight

        q_vec = hash_embed(query, dim=self.dim)
        dense = self._dense_scores(q_vec)
        sparse = self._sparse_scores(query)

        all_ids = set(dense) | set(sparse)
        if not all_ids:
            return []
        placeholders = ",".join("?" for _ in all_ids)
        rows = self.store._conn.execute(
            f"""SELECT c.concept_id, c.title, c.type, c.description,
                       c.resource, c.tags_json,
                       ci.text AS snippet_text
                  FROM concepts c
             LEFT JOIN concept_chunks ci
                    ON ci.chunk_id = (
                        SELECT chunk_id FROM concept_chunks
                         WHERE concept_id = c.concept_id
                         ORDER BY chunk_idx ASC LIMIT 1
                    )
                 WHERE c.concept_id IN ({placeholders})""",
            tuple(all_ids),
        ).fetchall()
        # Index by id
        meta: Dict[int, Dict] = {}
        for r in rows:
            cid = int(r["concept_id"])
            tags = []
            if r["tags_json"]:
                try:
                    tags = json.loads(r["tags_json"])
                except (TypeError, ValueError):
                    tags = []
            meta[cid] = {
                "concept_id": cid,
                "title": r["title"] or "",
                "type": r["type"] or "",
                "description": r["description"] or "",
                "resource": r["resource"] or "",
                "tags": tags,
                "snippet": (r["snippet_text"] or "")[:300],
            }

        results: List[Dict] = []
        for cid in all_ids:
            sv = max(0.0, dense.get(cid, 0.0))
            st = max(0.0, sparse.get(cid, 0.0))
            score = sv * vw + st * tw
            item = dict(meta.get(cid, {"concept_id": cid}))
            item["score_vec"] = round(sv, 4)
            item["score_txt"] = round(st, 4)
            item["score"] = round(score, 4)
            results.append(item)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
