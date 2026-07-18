"""OKF v0.1 document parser & serializer.

Spec reference:
  https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

Only Python stdlib + PyYAML are used. Unknown frontmatter keys / types are
preserved verbatim — the spec mandates permissive consumption.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


# ── Exceptions ──────────────────────────────────────────────────────────


class OKFDocumentError(Exception):
    """Raised when an OKF document cannot be parsed."""


class OKFValidationError(Exception):
    """Raised when an OKF document fails spec validation (missing `type`, etc.)."""


# ── Helpers ──────────────────────────────────────────────────────────────


def _convert_datetime(obj: Any) -> Any:
    """Recursively walk a YAML-parsed structure; convert datetime → ISO string."""
    if isinstance(obj, dict):
        return {k: _convert_datetime(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_convert_datetime(i) for i in obj]
    if isinstance(obj, datetime):
        # RFC 3339 / ISO 8601 with Z suffix (UTC).
        return obj.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return obj


# ── Document ────────────────────────────────────────────────────────────


class OKFDocument:
    """A single OKF concept document: frontmatter (dict) + body (markdown).

    Construct via :meth:`parse` from raw text, or instantiate directly with
    already-extracted ``frontmatter`` / ``body``.
    """

    def __init__(
        self,
        frontmatter: Optional[Dict[str, Any]] = None,
        body: str = "",
    ) -> None:
        # Always store a fresh dict so callers can mutate freely.
        self.frontmatter: Dict[str, Any] = dict(frontmatter) if frontmatter else {}
        # Body is the raw markdown after the frontmatter, with a single
        # leading newline trimmed if present (spec example shows blank line).
        self.body: str = body

    # ── Class methods ────────────────────────────────────────────────────

    @classmethod
    def parse(cls, text: str) -> "OKFDocument":
        """Parse an OKF document from raw markdown text.

        Strict spec-conformant parsing:
          1. First line MUST be exactly ``---`` (with optional trailing
             whitespace; we strip the line).
          2. Frontmatter YAML block ends at the next line whose stripped
             content equals ``---``.
          3. Everything after the closing fence (minus one optional
             leading newline) is the body.

        Raises :class:`OKFDocumentError` if the frontmatter fence is
        missing or unterminated.  Raises :class:`OKFDocumentError` on
        invalid YAML as well — the spec says producers should tolerate
        broken consumers, but parsers should still surface failures.
        """
        if text is None:
            raise OKFDocumentError("document text is None")

        # Normalize: splitlines handles \n, \r\n, \r uniformly.
        # Use splitlines(keepends=True) only for body; for header detection
        # we just need line contents.
        # Special-case: file might start with a UTF-8 BOM.
        if text.startswith("\ufeff"):
            text = text[1:]

        lines = text.split("\n")

        # Spec §4: frontmatter block delimited by --- at top.
        # We require the very first line (after any BOM) to be the fence.
        if not lines or lines[0].strip() != "---":
            raise OKFDocumentError(
                "missing opening frontmatter fence: first line must be '---'"
            )

        # Scan for closing fence.
        closing_idx: Optional[int] = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_idx = i
                break

        if closing_idx is None:
            raise OKFDocumentError("unterminated frontmatter fence")

        yaml_text = "\n".join(lines[1:closing_idx])

        # Parse YAML — strict.  yaml.safe_load returns None for empty docs,
        # which we'll normalize to {} below.
        try:
            parsed = yaml.safe_load(yaml_text)
        except yaml.YAMLError as exc:
            raise OKFDocumentError(f"invalid YAML frontmatter: {exc}") from exc

        if parsed is None:
            frontmatter: Dict[str, Any] = {}
        elif isinstance(parsed, dict):
            frontmatter = _convert_datetime(parsed)
        else:
            raise OKFDocumentError(
                f"frontmatter must be a YAML mapping, got {type(parsed).__name__}"
            )

        # Body = everything after the closing fence.
        # Per spec example: "---\n<yaml>\n---\n\n<body>"; we keep a
        # single leading newline if present, drop the blank-line separator
        # before content. To round-trip nicely we preserve the body
        # exactly minus the initial "\n" that follows the closing fence.
        body_text = "\n".join(lines[closing_idx + 1 :])
        # Strip exactly one leading newline if present (the blank line
        # between fence and body in the spec example).
        if body_text.startswith("\n"):
            body_text = body_text[1:]

        return cls(frontmatter=frontmatter, body=body_text)

    # ── Instance methods ─────────────────────────────────────────────────

    def serialize(self) -> str:
        """Render to canonical OKF text: ``---\\n<yaml>\\n---\\n\\n<body>``.

        YAML is emitted with the default_flow_style=False and sorted keys
        so output is deterministic & diff-friendly. Unknown keys are
        preserved verbatim.  ``None`` values are dropped (YAML
        ``key: null`` is rare and noisy in concept files).
        """
        cleaned = {
            k: v for k, v in self.frontmatter.items() if v is not None
        }
        buf = io.StringIO()
        buf.write("---\n")
        yaml.safe_dump(
            cleaned,
            buf,
            default_flow_style=False,
            sort_keys=True,
            allow_unicode=True,
            width=4096,
        )
        # safe_dump ends with "\n"; strip it then add our own fence.
        yaml_body = buf.getvalue()
        # buf currently is "---\n<yaml>\n"; we need "---\n<yaml>---\n\n<body>".
        yaml_body = yaml_body[len("---\n"):]
        if yaml_body.endswith("\n"):
            yaml_body = yaml_body[:-1]

        out = ["---", yaml_body, "---", ""]
        if self.body:
            out.append(self.body)
        # Ensure trailing newline for POSIX-friendly files.
        text = "\n".join(out)
        if not text.endswith("\n"):
            text += "\n"
        return text

    def validate(self) -> None:
        """Validate that frontmatter conforms to OKF v0.1 minimum requirements.

        Raises :class:`OKFValidationError` if:
          - frontmatter is not a dict (shouldn't happen after parse, but
            constructor allows manual construction),
          - ``type`` field is missing,
          - ``type`` field is empty string or otherwise falsy.

        Per spec, *unknown* keys and *unknown* type values are NOT
        rejected — they're passed through.
        """
        if not isinstance(self.frontmatter, dict):
            raise OKFValidationError(
                f"frontmatter must be a dict, got {type(self.frontmatter).__name__}"
            )

        type_value = self.frontmatter.get("type")
        if type_value is None:
            raise OKFValidationError("frontmatter is missing required 'type' field")
        if not isinstance(type_value, str):
            raise OKFValidationError(
                f"'type' field must be a string, got {type(type_value).__name__}"
            )
        if not type_value.strip():
            raise OKFValidationError("'type' field is empty")

    def concept_id(self, bundle_root: Path, file_path: Path) -> str:
        """Compute the canonical concept ID for this document.

        Per spec §2: the concept ID is the path of the concept's file
        within the bundle, with the ``.md`` suffix removed. The task
        spec further requires a leading ``/`` (bundle-relative absolute
        form, e.g. ``tables/users`` → ``/tables/users``).
        """
        bundle_root = Path(bundle_root).resolve()
        file_path = Path(file_path).resolve()

        try:
            rel = file_path.relative_to(bundle_root)
        except ValueError as exc:
            raise OKFDocumentError(
                f"{file_path} is not inside bundle root {bundle_root}"
            ) from exc

        # Convert OS separators to forward slashes for portability
        # (OKF links are POSIX-style, see §5.1).
        rel_posix = rel.as_posix()
        if rel_posix.endswith(".md"):
            rel_posix = rel_posix[:-3]
        return "/" + rel_posix

    # ── Dunders ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        keys = list(self.frontmatter.keys())
        type_str = self.frontmatter.get("type", "<no-type>")
        body_preview = self.body[:40].replace("\n", " ")
        return (
            f"OKFDocument(type={type_str!r}, "
            f"keys={keys}, body={body_preview!r}…)"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OKFDocument):
            return NotImplemented
        return self.frontmatter == other.frontmatter and self.body == other.body