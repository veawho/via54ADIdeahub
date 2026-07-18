"""via54_store — unified SQLite + vector (TF-IDF + hash-embed) data model.

Public API:
    KBStore              ── SQLite CRUD wrapper
    HybridRetriever      ── dense+sparse fusion search
    hash_embed           ── pure-stdlib deterministic embedding
    cosine / l2_normalize ── vector math helpers
    encode_blob / decode_blob ── float32 packing
"""

from .embedding import (
    hash_embed,
    l2_normalize,
    cosine,
    encode_blob,
    decode_blob,
)
from .store import KBStore
from .retrieval import HybridRetriever, tokenize

__all__ = [
    "KBStore",
    "HybridRetriever",
    "hash_embed",
    "l2_normalize",
    "cosine",
    "encode_blob",
    "decode_blob",
    "tokenize",
]
