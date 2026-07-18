"""Tests for via54_okf — OKF v0.1 parser, serializer & bundle scanner.

Run with:
  cd /Users/david/Desktop/developments/via54ADIdeahub
  /usr/bin/python3 -m pytest tests/test_okf.py -v

Tests are deliberately written to mirror the OKF v0.1 spec section
references so they double as documentation of the expected contract.
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from via54_okf import (
    OKFDocument,
    OKFDocumentError,
    OKFValidationError,
    iter_concept_files,
    load_concepts,
    extract_links,
)

# Repo root — used by CLI subprocess tests to resolve the package.
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent


# ────────────────────────────────────────────────────────────────────────
# OKFDocument.parse
# ────────────────────────────────────────────────────────────────────────


def test_parse_minimal() -> None:
    """Spec §4 — minimal valid document: just ``type`` and a body."""
    text = textwrap.dedent(
        """\
        ---
        type: Concept
        ---

        Hello world.
        """
    )
    doc = OKFDocument.parse(text)
    assert doc.frontmatter == {"type": "Concept"}
    assert doc.body.strip() == "Hello world."


def test_parse_with_full_frontmatter() -> None:
    """Spec §4.1 — full recommended frontmatter with all keys."""
    text = textwrap.dedent(
        """\
        ---
        type: BigQuery Table
        title: Customer Orders
        description: One row per completed customer order.
        resource: https://example.com/tables/orders
        tags: [sales, orders, revenue]
        timestamp: 2026-05-28T14:30:00Z
        ---

        # Schema

        | Column | Type | Description |
        | --- | --- | --- |
        """
    )
    doc = OKFDocument.parse(text)
    assert doc.frontmatter["type"] == "BigQuery Table"
    assert doc.frontmatter["title"] == "Customer Orders"
    assert doc.frontmatter["description"].startswith("One row per")
    assert doc.frontmatter["resource"] == "https://example.com/tables/orders"
    assert doc.frontmatter["tags"] == ["sales", "orders", "revenue"]
    assert doc.frontmatter["timestamp"] == "2026-05-28T14:30:00Z"
    assert "# Schema" in doc.body


def test_parse_missing_frontmatter() -> None:
    """Spec §9 conformance rule 1 — frontmatter is required."""
    text = "Just some body text without frontmatter.\n"
    with pytest.raises(OKFDocumentError) as exc_info:
        OKFDocument.parse(text)
    assert "frontmatter" in str(exc_info.value).lower()


def test_parse_invalid_yaml() -> None:
    """Invalid YAML in frontmatter must raise OKFDocumentError."""
    text = textwrap.dedent(
        """\
        ---
        type: Concept
        title: [unclosed bracket
        ---

        body
        """
    )
    with pytest.raises(OKFDocumentError) as exc_info:
        OKFDocument.parse(text)
    assert "yaml" in str(exc_info.value).lower()


def test_parse_unterminated_frontmatter() -> None:
    """An opening ``---`` with no closing fence is malformed."""
    text = textwrap.dedent(
        """\
        ---
        type: Concept

        Some content but no closing fence.
        """
    )
    with pytest.raises(OKFDocumentError) as exc_info:
        OKFDocument.parse(text)
    assert "unterminated" in str(exc_info.value).lower()


# ────────────────────────────────────────────────────────────────────────
# Serialize roundtrip
# ────────────────────────────────────────────────────────────────────────


def test_serialize_roundtrip() -> None:
    """serialize(parse(x)) should preserve frontmatter + body (modulo YAML
    quoting). Keys must round-trip; body must round-trip exactly."""
    original_text = textwrap.dedent(
        """\
        ---
        type: Playbook
        title: Incident response
        description: Triage steps for freshness alerts.
        tags: [oncall, incident]
        timestamp: 2026-04-12T09:00:00Z
        ---

        # Trigger

        A freshness alert fires when orders lag more than 30 minutes.

        # Steps

        1. Check the ingestion dashboard.
        2. Page the on-call.
        """
    )
    doc1 = OKFDocument.parse(original_text)
    text2 = doc1.serialize()
    doc2 = OKFDocument.parse(text2)

    # Frontmatter must be preserved exactly.
    assert doc2.frontmatter == doc1.frontmatter
    # Body must be preserved exactly (modulo leading-newline handling).
    assert doc2.body.strip() == doc1.body.strip()


def test_serialize_starts_with_fence_and_blank_line() -> None:
    """Spec example: ``---\\n<yaml>\\n---\\n\\n<body>``."""
    doc = OKFDocument({"type": "Concept", "title": "Demo"}, body="# Hi")
    out = doc.serialize()
    # Must start with `---` and contain the closing fence, blank line,
    # then body.
    lines = out.split("\n")
    assert lines[0] == "---"
    # Find the closing fence (first line == "---" after the opening).
    closing = next(i for i in range(1, len(lines)) if lines[i] == "---")
    # Blank line immediately after closing fence.
    assert lines[closing + 1] == ""
    assert lines[closing + 2] == "# Hi"


# ────────────────────────────────────────────────────────────────────────
# Validation
# ────────────────────────────────────────────────────────────────────────


def test_validate_requires_type() -> None:
    """Spec §9 conformance rule 2 — ``type`` field must be present & non-empty."""
    # Missing type entirely.
    doc = OKFDocument({"title": "No type here"}, body="body")
    with pytest.raises(OKFValidationError) as exc_info:
        doc.validate()
    assert "type" in str(exc_info.value).lower()

    # Empty type.
    doc2 = OKFDocument({"type": ""}, body="body")
    with pytest.raises(OKFValidationError) as exc_info:
        doc2.validate()
    assert "empty" in str(exc_info.value).lower()

    # Whitespace-only type.
    doc3 = OKFDocument({"type": "   "}, body="body")
    with pytest.raises(OKFValidationError) as exc_info:
        doc3.validate()
    assert "empty" in str(exc_info.value).lower()

    # Non-string type.
    doc4 = OKFDocument({"type": 42}, body="body")
    with pytest.raises(OKFValidationError):
        doc4.validate()

    # Valid type → no raise.
    OKFDocument({"type": "Concept"}, body="body").validate()
    # Unknown type values are still OK per spec §9.
    OKFDocument({"type": "My-Custom-Unknown-Type"}, body="body").validate()


# ────────────────────────────────────────────────────────────────────────
# concept_id
# ────────────────────────────────────────────────────────────────────────


def test_concept_id(tmp_path: Path) -> None:
    """Spec §2 — concept ID = path with .md removed; task says with leading /."""
    # Layout:
    #   <tmp>/tables/users.md      -> /tables/users
    #   <tmp>/root.md               -> /root
    #   <tmp>/a/b/c/deep.md         -> /a/b/c/deep
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    users = tables_dir / "users.md"
    users.write_text("---\ntype: Concept\n---\nbody\n", encoding="utf-8")

    root_md = tmp_path / "root.md"
    root_md.write_text("---\ntype: Concept\n---\nbody\n", encoding="utf-8")

    deep_dir = tmp_path / "a" / "b" / "c"
    deep_dir.mkdir(parents=True)
    deep = deep_dir / "deep.md"
    deep.write_text("---\ntype: Concept\n---\nbody\n", encoding="utf-8")

    doc = OKFDocument({"type": "Concept"}, body="body")
    assert doc.concept_id(tmp_path, users) == "/tables/users"
    assert doc.concept_id(tmp_path, root_md) == "/root"
    assert doc.concept_id(tmp_path, deep) == "/a/b/c/deep"

    # File outside the bundle root raises.
    outside = Path("/tmp/somewhere_else.md")
    with pytest.raises(OKFDocumentError):
        doc.concept_id(tmp_path, outside)


# ────────────────────────────────────────────────────────────────────────
# Link extraction
# ────────────────────────────────────────────────────────────────────────


def test_extract_links_three_kinds() -> None:
    """Spec §5 — three link forms: bundle-relative (/), relative
    (./ ../), external (http(s)://)."""

    body = textwrap.dedent(
        """\
        See the [orders table](/tables/orders.md) for the join key.

        See the [neighboring concept](./other.md).

        See also [parent](../parent.md).

        External reference: [Cannes](https://www.canneslions.com/).

        Plain http: [old link](http://example.com/foo).
        """
    )
    links = extract_links(body)
    # Order should be preserved.
    assert len(links) == 5

    kinds = [k for k, _t, _x in links]
    assert kinds == [
        "bundle-relative",  # /tables/orders.md
        "relative",         # ./other.md
        "relative",         # ../parent.md
        "external",         # https://...
        "external",         # http://...
    ]

    # Targets should be returned verbatim.
    assert links[0] == ("bundle-relative", "/tables/orders.md", "orders table")
    assert links[1] == ("relative", "./other.md", "neighboring concept")
    assert links[2] == ("relative", "../parent.md", "parent")
    assert links[3][1] == "https://www.canneslions.com/"
    assert links[3][2] == "Cannes"
    assert links[4][0] == "external"
    assert links[4][1] == "http://example.com/foo"


def test_extract_links_ignores_image_syntax_and_unusual() -> None:
    """Image syntax ``![alt](src)`` MUST NOT be matched as a link.
    Reference-style links ``[text][ref]`` are also out of scope."""
    body = "![logo](/img/logo.png) and ![](http://example.com/x.png)\n"
    assert extract_links(body) == []

    body2 = "[ref-style][1] and bare URL <https://example.com>."
    # No inline links here.
    assert extract_links(body2) == []


# ────────────────────────────────────────────────────────────────────────
# Bundle scanning
# ────────────────────────────────────────────────────────────────────────


def test_load_concepts_skip_reserved(tmp_path: Path) -> None:
    """Spec §3.1 — ``index.md`` and ``log.md`` MUST NOT be loaded as
    concepts, even though they exist in the tree."""

    # Build a mini-bundle:
    #   <tmp>/index.md            (reserved — skip)
    #   <tmp>/log.md              (reserved — skip)
    #   <tmp>/root_concept.md     (load as concept, id=/root_concept)
    #   <tmp>/tables/orders.md    (load as concept, id=/tables/orders)
    #   <tmp>/tables/users.md     (load as concept, id=/tables/users)
    #   <tmp>/tables/index.md     (reserved — skip)
    (tmp_path / "index.md").write_text(
        "# Index\n\n- [orders](tables/orders.md)\n", encoding="utf-8"
    )
    (tmp_path / "log.md").write_text(
        "# Log\n\n## 2026-05-22\n* Initial.\n", encoding="utf-8"
    )
    (tmp_path / "root_concept.md").write_text(
        "---\ntype: Reference\n---\nbody\n", encoding="utf-8"
    )
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "orders.md").write_text(
        "---\ntype: BigQuery Table\n---\nbody\n", encoding="utf-8"
    )
    (tables / "users.md").write_text(
        "---\ntype: BigQuery Table\n---\nbody\n", encoding="utf-8"
    )
    (tables / "index.md").write_text("# Tables index\n", encoding="utf-8")

    # iter_concept_files should yield 3 non-reserved files.
    files = list(iter_concept_files(tmp_path))
    names = sorted(p.name for p in files)
    assert names == ["orders.md", "root_concept.md", "users.md"]

    # load_concepts should yield 3 parsed triples with correct ids.
    triples = list(load_concepts(tmp_path))
    assert len(triples) == 3
    ids = sorted(cid for _p, _d, cid in triples)
    assert ids == ["/root_concept", "/tables/orders", "/tables/users"]

    for path, doc, cid in triples:
        assert isinstance(doc, OKFDocument)
        assert doc.frontmatter.get("type"), f"missing type for {cid}"
        assert cid.startswith("/")


def test_iter_concept_files_skips_hidden_dirs(tmp_path: Path) -> None:
    """Hidden dirs (.git, .venv, etc.) MUST NOT be traversed."""
    (tmp_path / "ok.md").write_text("---\ntype: Concept\n---\n", encoding="utf-8")
    hidden = tmp_path / ".git"
    hidden.mkdir()
    (hidden / "config.md").write_text("---\ntype: Concept\n---\n", encoding="utf-8")
    dotdir = tmp_path / ".cache"
    dotdir.mkdir()
    (dotdir / "x.md").write_text("---\ntype: Concept\n---\n", encoding="utf-8")

    names = sorted(p.name for p in iter_concept_files(tmp_path))
    assert names == ["ok.md"]


# ────────────────────────────────────────────────────────────────────────
# CLI smoke test
# ────────────────────────────────────────────────────────────────────────


def test_cli_validate_reports_failures(tmp_path: Path) -> None:
    """``python -m via54_okf validate <dir>`` reports per-file status and
    exits non-zero when there are problems."""
    import subprocess

    (tmp_path / "good.md").write_text(
        "---\ntype: Good\n---\nbody\n", encoding="utf-8"
    )
    (tmp_path / "missing_type.md").write_text(
        "---\ntitle: no type here\n---\nbody\n", encoding="utf-8"
    )
    (tmp_path / "no_frontmatter.md").write_text("just a body\n", encoding="utf-8")
    (tmp_path / "bad_yaml.md").write_text(
        "---\ntype: [unclosed\n---\nbody\n", encoding="utf-8"
    )
    (tmp_path / "index.md").write_text("# Index\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "via54_okf", "validate", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=str(_REPO),
    )

    assert result.returncode == 1, f"expected exit 1, got {result.returncode}\nstderr: {result.stderr}"
    combined = result.stdout + result.stderr
    assert "good.md" in combined
    assert "missing-type" in combined
    assert "missing-frontmatter" in combined
    assert "bad-yaml" in combined
    assert "index.md" in combined


def test_cli_validate_clean_bundle_exits_zero(tmp_path: Path) -> None:
    """A bundle with only valid concepts (and reserved files) exits 0."""
    import subprocess

    (tmp_path / "concept.md").write_text(
        "---\ntype: Concept\n---\nbody\n", encoding="utf-8"
    )
    (tmp_path / "index.md").write_text("# Index\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "via54_okf", "validate", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=str(_REPO),
    )
    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
    assert "OK" in result.stdout


def test_parse_preserves_unknown_keys() -> None:
    """Spec §4.1 / §9 — unknown frontmatter keys MUST be preserved."""
    text = textwrap.dedent(
        """\
        ---
        type: Concept
        custom_field: 42
        nested:
          deep: value
        tags_extra: [foo, bar]
        ---

        body
        """
    )
    doc = OKFDocument.parse(text)
    assert doc.frontmatter["custom_field"] == 42
    assert doc.frontmatter["nested"] == {"deep": "value"}
    assert doc.frontmatter["tags_extra"] == ["foo", "bar"]

    # Round-trip preserves them.
    doc2 = OKFDocument.parse(doc.serialize())
    assert doc2.frontmatter == doc.frontmatter