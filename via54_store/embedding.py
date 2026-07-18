"""Pure-stdlib vector embedding via token hashing.

Goal: produce a deterministic, fixed-dim, unit-normalized dense vector for any
piece of text, without numpy, sklearn, faiss, or sqlite-vec. Quality is not
competitive with real transformer embeddings — it is a TF-IDF fallback that
matches the spec's "vss" requirement using nothing but `hashlib` + `struct`.

Design:
  1. Tokenize: split into small whitespace/punct-separated tokens. Keep CJK
     bigrams so Chinese text still produces useful distinct features.
  2. For each token, hash it with blake2b -> 8 bytes, interpret as little-endian
     uint64, and use two halves of that to pick a feature index and a signed
     contribution (sign bit). Add the contribution to a dense float vector of
     length `dim`. Use a second feature index alongside to reduce collisions
     and give each token a "spread".
  3. L2-normalize the final vector to unit norm so cosine == dot product.

This is essentially the "hashing trick" with random sign projection (Weinberger
et al., 2009), but driven by a hash function instead of a random seed so
vectors are stable across processes.
"""

from __future__ import annotations

import hashlib
import math
import re
import struct
from typing import List

# Same tokenizer regex used in via54_rag for English-style tokens; we add a
# CJK bigram pass to keep Chinese content meaningful.
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,3}")
_DEFAULT_DIM = 256


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [t.lower() for t in _TOKEN_RE.findall(text) if len(t) >= 2]


def hash_embed(text: str, dim: int = _DEFAULT_DIM) -> List[float]:
    """Deterministic hash-projected embedding. Same text → same vector.

    Args:
        text: input string (any language)
        dim:  output vector length (default 256)

    Returns:
        list of `dim` floats, L2-normalized to unit norm.
    """
    if dim <= 0:
        raise ValueError(f"dim must be positive, got {dim}")
    tokens = _tokenize(text)
    vec = [0.0] * dim
    if not tokens:
        return l2_normalize(vec)
    for tok in tokens:
        # 8-byte digest interpreted as uint64 (little-endian).
        digest = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
        (h,) = struct.unpack("<Q", digest)
        idx1 = h % dim
        # Mix bits so we get a second index in a different region of the vector.
        idx2 = ((h >> 17) ^ (h * 2654435761 & 0xFFFFFFFFFFFFFFFF)) % dim
        sign = 1.0 if (h & 1) else -1.0
        sign2 = 1.0 if (h >> 1) & 1 else -1.0
        vec[idx1] += sign
        vec[idx2] += sign2
    return l2_normalize(vec)


def l2_normalize(v: List[float]) -> List[float]:
    """Return v divided by its L2 norm. Zero vector stays zero."""
    if not v:
        return v
    norm = math.sqrt(sum(x * x for x in v))
    if norm <= 0.0:
        return [0.0] * len(v)
    inv = 1.0 / norm
    return [x * inv for x in v]


def cosine(a: List[float], b: List[float]) -> float:
    """Cosine similarity for two equally-sized vectors."""
    if not a or len(a) != len(b):
        raise ValueError("cosine: vectors must be same non-zero length")
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def encode_blob(v: List[float]) -> bytes:
    """Pack a list of floats into a binary BLOB (little-endian float32)."""
    if not v:
        return b""
    return struct.pack("<%df" % len(v), *v)


def decode_blob(blob: bytes) -> List[float]:
    """Inverse of encode_blob — unpack a float32 BLOB back to a list."""
    if not blob:
        return []
    n = len(blob) // 4
    if n == 0:
        return []
    return list(struct.unpack("<%df" % n, blob))
