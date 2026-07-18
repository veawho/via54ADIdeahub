"""OKF v0.1 bundle scanner & link extractor.

A *bundle* is a directory of .md files. Reserved filenames ``index.md``
and ``log.md`` have spec-defined meaning (directory listing & update log)
and MUST NOT be treated as concept documents.

Link classification (per task spec):
  - ``bundle-relative``: target starts with ``/``           e.g. ``/tables/users.md``
  - ``relative``:        target starts with ``./`` or ``../``  e.g. ``../sibling.md``
  - ``external``:        target starts with ``http://`` or ``https://``
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

from .document import OKFDocument


# ── Constants ───────────────────────────────────────────────────────────

# Spec §3.1: filenames with reserved meaning. MUST NOT be concepts.
RESERVED_NAMES = ("index.md", "log.md")


class LinkKind:
    """String constants for link classification."""

    BUNDLE_RELATIVE = "bundle-relative"
    RELATIVE = "relative"
    EXTERNAL = "external"


# ── Bundle scanning ────────────────────────────────────────────────────


def iter_concept_files(bundle_root: Path) -> Iterator[Path]:
    """Recursively yield all non-reserved .md files under ``bundle_root``.

    Skips:
      - ``index.md`` and ``log.md`` at any level (spec §3.1)
      - Hidden directories (anything starting with ``.``) such as
        ``.git``, ``.venv``, ``node_modules``-style folders
      - Non-markdown files

    Yields paths in sorted, deterministic order so consumers can rely
    on a stable traversal.
    """
    bundle_root = Path(bundle_root).resolve()
    if not bundle_root.is_dir():
        return

    # Walk sorted for determinism. Path.rglob sorts by default in modern
    # Python, but we sort explicitly to be safe across versions.
    for path in sorted(bundle_root.rglob("*.md")):
        # Skip if any parent component starts with "." (hidden dir).
        if any(part.startswith(".") for part in path.relative_to(bundle_root).parts[:-1]):
            continue
        # Skip reserved filenames.
        if path.name in RESERVED_NAMES:
            continue
        yield path


def load_concepts(
    bundle_root: Path,
) -> Iterator[Tuple[Path, OKFDocument, str]]:
    """Parse every concept file under ``bundle_root``.

    Yields ``(file_path, document, concept_id)`` triples for each
    successfully parsed file. Files that fail to parse are *skipped*
    (the spec mandates permissive consumption); callers that want to
    surface errors should call :func:`iter_concept_files` directly
    and wrap with their own parser.

    Note: parse failures are intentionally silent here. Use the CLI
    ``validate`` subcommand if you need a per-file error report.
    """
    from .document import OKFDocumentError  # local import to avoid cycle

    for file_path in iter_concept_files(bundle_root):
        try:
            text = file_path.read_text(encoding="utf-8")
            doc = OKFDocument.parse(text)
        except (OKFDocumentError, UnicodeDecodeError, OSError):
            # Permissive: skip broken files per spec §9.
            continue
        cid = doc.concept_id(bundle_root, file_path)
        yield file_path, doc, cid


# ── Link extraction ────────────────────────────────────────────────────

# Match markdown inline links: [text](target) — also handles title
# suffixes like [text](target "title") (the title is ignored for kind
# classification but kept as part of the target string for fidelity).
#
# Notes:
#  - We deliberately do NOT match reference-style links [text][ref] or
#    bare URLs <https://...>. Spec §5 talks only about inline links.
#  - We require non-whitespace, non-`[` text inside the brackets so we
#    don't match image syntax by accident (images start with `!`).
#  - Target can contain parens when escaped; for simplicity we accept
#    non-whitespace targets.
_LINK_RE = re.compile(
    r"(?<!\!)\[([^\]\n]+)\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)"
)


def extract_links(
    body: str,
    bundle_root: Optional[Path] = None,
    src_path: Optional[Path] = None,
) -> List[Tuple[str, str, str]]:
    """Extract markdown inline links from ``body``.

    Returns a list of ``(kind, target, text)`` tuples in document order.

    ``kind`` is one of:
      - ``"bundle-relative"`` — target starts with ``/``
      - ``"relative"``        — target starts with ``./`` or ``../``
      - ``"external"``        — target starts with ``http://`` or ``https://``

    Any target that doesn't match one of those patterns (e.g. an anchor
    ``#section``, an absolute filesystem path, an email, or a non-http
    scheme like ``mailto:``) is classified as ``"external"`` and
    returned as-is — OKF consumers MUST tolerate unknown link kinds.

    ``bundle_root`` and ``src_path`` are accepted for API symmetry /
    future use (e.g. resolving relative links to absolute concept IDs),
    but classification itself only depends on the target string per
    the task spec.
    """
    results: List[Tuple[str, str, str]] = []
    for match in _LINK_RE.finditer(body):
        text = match.group(1).strip()
        target = match.group(2)
        kind = _classify_link(target)
        results.append((kind, target, text))
    return results


def _classify_link(target: str) -> str:
    """Classify a link target by its leading characters."""
    if not target:
        return LinkKind.EXTERNAL
    if target.startswith("/"):
        return LinkKind.BUNDLE_RELATIVE
    if target.startswith("./") or target.startswith("../"):
        return LinkKind.RELATIVE
    if target.startswith("http://") or target.startswith("https://"):
        return LinkKind.EXTERNAL
    # Unknown scheme (mailto:, ftp:, fragment-only #anchor, etc.)
    # — surface as external so consumers see it.
    return LinkKind.EXTERNAL