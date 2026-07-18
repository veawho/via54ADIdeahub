"""via54_store.store — SQLite-backed knowledge base wrapper.

Encapsulates all CRUD on the 9-table schema in `schema.sql`. Designed to be
used both as a library (via `KBStore(db_path)`) and by `via54_store.cli`.
"""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# Resolved at import time so callers get a stable path even from CLIs run
# outside the package root.
_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def _now_iso() -> str:
    """UTC ISO timestamp, second precision, sortable."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _body_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest()


class KBStore:
    """Thin wrapper around sqlite3 with the via54_store schema.

    All public mutators accept and return rows as plain dicts / sequences so
    callers don't have to deal with sqlite3.Row if they don't want to.
    """

    def __init__(self, db_path: str = "via54_kb.db") -> None:
        self.db_path = db_path
        # `check_same_thread=False` allows a single KBStore to be shared; we
        # still create one connection per public call below so we stay
        # thread-safe with the stdlib sqlite module.
        self._conn: sqlite3.Connection = sqlite3.connect(db_path, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        # Foreign keys are off by default in pysqlite; enable them so the
        # `ON DELETE CASCADE` we wrote into the schema behaves.
        self._conn.execute("PRAGMA foreign_keys = ON")
        # Each `with KBStore.transaction()` savepoint path benefits from WAL.
        self._conn.execute("PRAGMA journal_mode = WAL")

    # ── lifecycle ──
    def close(self) -> None:
        try:
            self._conn.close()
        except sqlite3.ProgrammingError:
            pass

    def __enter__(self) -> "KBStore":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def init_schema(self) -> None:
        """Execute schema.sql (idempotent)."""
        sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        self._conn.executescript(sql)
        self._conn.commit()

    # ── transactions ──
    def transaction(self):
        """Context manager: BEGIN IMMEDIATE / COMMIT / ROLLBACK."""
        return _Tx(self._conn)

    # ── bundles ──
    def upsert_bundle(
        self,
        name: str,
        root_path: str,
        version: str = "",
        description: str = "",
    ) -> int:
        """Insert or update a bundle row. Returns bundle_id."""
        now = _now_iso()
        row = self._conn.execute(
            "SELECT bundle_id FROM bundles WHERE name = ?", (name,)
        ).fetchone()
        if row:
            bid = row["bundle_id"]
            self._conn.execute(
                """UPDATE bundles
                   SET root_path = ?, version = ?, description = ?,
                       updated_at = ?
                   WHERE bundle_id = ?""",
                (root_path, version, description, now, bid),
            )
            self._conn.commit()
            return bid
        cur = self._conn.execute(
            """INSERT INTO bundles (name, root_path, version, description,
                                    created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, root_path, version, description, now, now),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    # ── concepts ──
    def upsert_concept(
        self,
        bundle_id: int,
        rel_path: str,
        type: str,
        title: str = "",
        description: str = "",
        resource: str = "",
        tags: Optional[Sequence[str]] = None,
        timestamp: str = "",
        source_path: str = "",
        mtime: Optional[float] = None,
        body_size: int = 0,
        body_hash: str = "",
    ) -> int:
        """Insert or replace concept. Returns concept_id (always replaces by
        (bundle_id, rel_path) so callers can re-ingest idempotently)."""
        tags_json = json.dumps(list(tags or []), ensure_ascii=False)
        # Check existing id first so we can UPDATE vs INSERT.
        row = self._conn.execute(
            "SELECT concept_id FROM concepts WHERE bundle_id = ? AND rel_path = ?",
            (bundle_id, rel_path),
        ).fetchone()
        if row:
            cid = int(row["concept_id"])
            self._conn.execute(
                """UPDATE concepts SET
                       type = ?, title = ?, description = ?, resource = ?,
                       tags_json = ?, timestamp = ?, source_path = ?,
                       mtime = ?, body_size = ?, body_hash = ?
                   WHERE concept_id = ?""",
                (
                    type, title, description, resource,
                    tags_json, timestamp, source_path,
                    mtime, body_size, body_hash, cid,
                ),
            )
            self._conn.commit()
            return cid
        cur = self._conn.execute(
            """INSERT INTO concepts
                  (bundle_id, rel_path, type, title, description, resource,
                   tags_json, timestamp, source_path, mtime, body_size, body_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                bundle_id, rel_path, type, title, description, resource,
                tags_json, timestamp, source_path, mtime, body_size, body_hash,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    # ── links ──
    def add_link(
        self,
        src_concept_id: int,
        target_path: str,
        link_kind: str,
        link_text: str = "",
        position: int = 0,
    ) -> int:
        cur = self._conn.execute(
            """INSERT INTO concept_links
                  (src_concept_id, target_path, link_kind, link_text, position)
               VALUES (?, ?, ?, ?, ?)""",
            (src_concept_id, target_path, link_kind, link_text, position),
        )
        return int(cur.lastrowid)

    # ── chunks ──
    def add_chunk(
        self,
        concept_id: int,
        chunk_idx: int,
        text: str,
        char_start: int,
        char_end: int,
        tokens: Optional[Sequence[str]] = None,
        commit: bool = True,
    ) -> int:
        """Insert or update a chunk. `commit=False` lets the caller run this
        inside a `KBStore.transaction()` block without auto-commits breaking
        the outer transaction's atomicity."""
        tokens_json = json.dumps(list(tokens or []), ensure_ascii=False)
        row = self._conn.execute(
            "SELECT chunk_id FROM concept_chunks WHERE concept_id = ? AND chunk_idx = ?",
            (concept_id, chunk_idx),
        ).fetchone()
        if row:
            chunk_id = int(row["chunk_id"])
            self._conn.execute(
                """UPDATE concept_chunks
                   SET text = ?, char_start = ?, char_end = ?, tokens_json = ?
                   WHERE chunk_id = ?""",
                (text, char_start, char_end, tokens_json, chunk_id),
            )
            if commit:
                self._conn.commit()
            # (re)insert chunk_terms
            self._replace_chunk_terms(chunk_id, tokens)
            return chunk_id
        cur = self._conn.execute(
            """INSERT INTO concept_chunks
                  (concept_id, chunk_idx, text, char_start, char_end, tokens_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (concept_id, chunk_idx, text, char_start, char_end, tokens_json),
        )
        chunk_id = int(cur.lastrowid)
        self._replace_chunk_terms(chunk_id, tokens)
        if commit:
            self._conn.commit()
        return chunk_id

    def _replace_chunk_terms(
        self, chunk_id: int, tokens: Optional[Sequence[str]]
    ) -> None:
        """Replace all term entries for a chunk.  Idempotent per chunk."""
        self._conn.execute("DELETE FROM chunk_terms WHERE chunk_id = ?", (chunk_id,))
        if not tokens:
            return
        from .embedding import _tokenize as compute_local_tf

        # Use tf (term frequency within this chunk) as the weight.
        freq: Dict[str, float] = {}
        for t in tokens:
            freq[t] = freq.get(t, 0.0) + 1.0
        total = len(tokens)
        for term, count in freq.items():
            tf = count / total if total > 0 else 0.0
            self._conn.execute(
                """INSERT INTO chunk_terms (term, chunk_id, tf) VALUES (?, ?, ?)""",
                (term, chunk_id, tf),
            )

    def add_chunk_vector(
        self,
        chunk_id: int,
        vector: Sequence[float],
        model: str = "hash-256",
        commit: bool = True,
    ) -> None:
        """Persist a per-chunk vector (BLOB float32) with meta rows.

        `commit=False` defers commit when the caller is running inside
        `KBStore.transaction()` — otherwise we open a nested BEGIN which
        pysqlite rejects.
        """
        if not vector:
            return
        from .embedding import encode_blob, l2_normalize
        vec = list(vector)
        # Always store the unit-normalized form so cosine == dot.
        unit = l2_normalize(vec)
        blob = encode_blob(unit)
        norm = math.sqrt(sum(x * x for x in unit))
        self._conn.execute(
            """INSERT INTO chunk_vector_meta (chunk_id, dim, norm, model)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(chunk_id) DO UPDATE SET
                   dim = excluded.dim, norm = excluded.norm,
                   model = excluded.model""",
            (chunk_id, len(unit), norm, model),
        )
        self._conn.execute(
            """INSERT INTO chunk_vector_blob (chunk_id, vec, model)
               VALUES (?, ?, ?)
               ON CONFLICT(chunk_id) DO UPDATE SET
                   vec = excluded.vec, model = excluded.model""",
            (chunk_id, blob, model),
        )
        if commit:
            self._conn.commit()

    # ── aggregation ──
    def term_count_doc(self, tokens: Sequence[str]) -> Dict[str, int]:
        """Map term -> its term-frequency in *one* document's token list.

        Used by retrievers to compute TF for a query or chunk. Pulled out so
        HybridRetriever doesn't have to import into the private internals of
        via54_rag.
        """
        freq: Dict[str, int] = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        return freq

    def doc_count_for_terms(self, terms: Sequence[str]) -> Dict[str, int]:
        """For each term, count how many chunks hold it (= doc freq)."""
        if not terms:
            return {}
        placeholders = ",".join("?" for _ in terms)
        rows = self._conn.execute(
            f"SELECT term, COUNT(DISTINCT chunk_id) AS c "
            f"FROM chunk_terms WHERE term IN ({placeholders}) GROUP BY term",
            tuple(terms),
        ).fetchall()
        return {r["term"]: int(r["c"]) for r in rows}

    def chunk_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(*) AS c FROM concept_chunks").fetchone()["c"]
        )

    def vector_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(*) AS c FROM chunk_vector_blob").fetchone()["c"]
        )

    def concept_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(*) AS c FROM concepts").fetchone()["c"]
        )

    def bundle_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(*) AS c FROM bundles").fetchone()["c"]
        )

    def link_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(*) AS c FROM concept_links").fetchone()["c"]
        )

    def term_row_count(self) -> int:
        return int(
            self._conn.execute("SELECT COUNT(*) AS c FROM chunk_terms").fetchone()["c"]
        )

    def upsert_aggregate(
        self,
        concept_id: int,
        link_count: int,
        chunk_count: int,
        has_vector: bool,
        term_count: int,
    ) -> None:
        self._conn.execute(
            """INSERT INTO concept_index_aggr
                  (concept_id, link_count, chunk_count, has_vector, term_count,
                   last_indexed_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(concept_id) DO UPDATE SET
                   link_count = excluded.link_count,
                   chunk_count = excluded.chunk_count,
                   has_vector = excluded.has_vector,
                   term_count = excluded.term_count,
                   last_indexed_at = excluded.last_indexed_at""",
            (
                concept_id, link_count, chunk_count,
                1 if has_vector else 0, term_count, _now_iso(),
            ),
        )

    # ── ingest log ──
    def log_ingest_start(
        self,
        kind: str,
        source_path: str = "",
        notes: str = "",
    ) -> int:
        cur = self._conn.execute(
            """INSERT INTO ingest_log (kind, source_path, notes)
               VALUES (?, ?, ?)""",
            (kind, source_path, notes),
        )
        return int(cur.lastrowid)

    def log_ingest_end(
        self,
        ingest_id: int,
        inserted: int = 0,
        updated: int = 0,
        skipped: int = 0,
        errors: int = 0,
        notes: str = "",
    ) -> None:
        self._conn.execute(
            """UPDATE ingest_log
               SET ended_at = ?, inserted = ?, updated = ?, skipped = ?,
                   errors = ?, notes = ?
               WHERE ingest_id = ?""",
            (_now_iso(), inserted, updated, skipped, errors, notes, ingest_id),
        )

    # ── atomic concept rebuild ──
    def replace_concept_atomic(
        self,
        concept_id: int,
        doc: Dict,
        chunks: List[Dict],
        links: List[Dict],
        vectors: Optional[Dict[int, Sequence[float]]] = None,
        token_extractor=None,
    ) -> None:
        """Replace one concept's chunks, links, term-rows, and vectors in a
        single transaction (used by ingestors to keep the DB self-consistent).

        `doc` is metadata override (title/description/tags/body_size/body_hash).
        `chunks` is a list of dicts: {chunk_idx, text, char_start, char_end, tokens}.
        `links` is a list of dicts: {target_path, link_kind, link_text, position}.
        `vectors` (optional) keyed by **the `chunk_idx` of each chunk in
        `chunks`** — the caller passes the chunk_idx (deterministic per
        concept) instead of the auto-generated chunk_id which would be
        invalidated when we wipe & re-insert.
        `token_extractor` (callable text->list[str]) lets the caller reuse
        whatever tokenizer they like; defaults to embedding._tokenize.
        """
        if token_extractor is None:
            from .embedding import _tokenize
            token_extractor = lambda txt: _tokenize(txt)

        with self.transaction():
            # 1) update concept row
            tags_json = json.dumps(list(doc.get("tags") or []), ensure_ascii=False)
            self._conn.execute(
                """UPDATE concepts SET
                       title = ?, description = ?, resource = ?, tags_json = ?,
                       timestamp = ?, mtime = ?, body_size = ?, body_hash = ?
                   WHERE concept_id = ?""",
                (
                    doc.get("title", ""),
                    doc.get("description", ""),
                    doc.get("resource", ""),
                    tags_json,
                    doc.get("timestamp", ""),
                    doc.get("mtime"),
                    doc.get("body_size", 0),
                    doc.get("body_hash", ""),
                    concept_id,
                ),
            )
            # 2) wipe + re-insert chunks/links/terms/vectors for this concept.
            #    ON DELETE CASCADE prunes term rows and vector rows via FK.
            self._conn.execute("DELETE FROM concept_chunks WHERE concept_id = ?", (concept_id,))
            self._conn.execute("DELETE FROM concept_links WHERE src_concept_id = ?", (concept_id,))

            new_chunk_ids: List[int] = []
            for ch in chunks:
                cid = self.add_chunk(
                    concept_id=concept_id,
                    chunk_idx=ch["chunk_idx"],
                    text=ch.get("text", ""),
                    char_start=ch.get("char_start", 0),
                    char_end=ch.get("char_end", 0),
                    tokens=ch.get("tokens"),
                    commit=False,  # part of outer tx
                )
                new_chunk_ids.append(cid)

            for lk in links:
                self.add_link(
                    src_concept_id=concept_id,
                    target_path=lk["target_path"],
                    link_kind=lk.get("link_kind", "markdown"),
                    link_text=lk.get("link_text", ""),
                    position=lk.get("position", 0),
                )

            # 3) terms — per-chunk TF using the chunk's tokens
            term_count_per_chunk: Dict[int, int] = {}
            for cid, ch in zip(new_chunk_ids, chunks):
                tokens = ch.get("tokens") or token_extractor(ch.get("text", ""))
                if not tokens:
                    continue
                tf_map = self.term_count_doc(tokens)
                for term, tf in tf_map.items():
                    self._conn.execute(
                        """INSERT OR REPLACE INTO chunk_terms (term, chunk_id, tf)
                           VALUES (?, ?, ?)""",
                        (term, cid, tf / max(1, len(tokens))),
                    )
                term_count_per_chunk[cid] = len(tf_map)

            # 4) vectors (optional) — keyed by chunk_idx, mapped to new chunk_id
            has_vector = False
            if vectors:
                for ch, new_cid in zip(chunks, new_chunk_ids):
                    v = vectors.get(ch["chunk_idx"])
                    if v:
                        self.add_chunk_vector(new_cid, v, commit=False)
                        has_vector = True

            # 5) aggregate row
            self.upsert_aggregate(
                concept_id=concept_id,
                link_count=len(links),
                chunk_count=len(new_chunk_ids),
                has_vector=has_vector,
                term_count=sum(term_count_per_chunk.values()),
            )


class _Tx:
    """Context manager wrapping a manual SQLite transaction."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def __enter__(self):
        self._conn.execute("BEGIN IMMEDIATE")
        return self._conn

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._conn.execute("COMMIT")
        else:
            try:
                self._conn.execute("ROLLBACK")
            except sqlite3.OperationalError:
                pass
        return False
