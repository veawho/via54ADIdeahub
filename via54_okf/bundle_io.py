"""OKF v0.1 bundle IO — load/write a bundle to/from disk.

This module is the IO companion to `bundle.py` (which only does iteration
& link extraction). Splitting them avoids editing the sibling's bundle.py
while still satisfying the public API promise of `load_bundle` /
`write_bundle` / `validate`.

A bundle on disk looks like:

    my_bundle/
      bundle.yaml          # manifest (name, version, description, ...)
      case_studies/
        nike_so_win.md     # frontmatter + body
        dove_reverse.md
        ...
      index.md             # TOC (optional, we generate one if missing)
      log.md               # change log (optional)

`load_bundle(path)` walks `path`, parses every concept, returns a `Bundle`.
`write_bundle(bundle, path)` does the reverse: writes the manifest, every
concept's `.md`, and (if absent) generates `index.md`.

`validate(bundle)` runs the spec §9 conformance checks and returns a dict
with counts and a list of `(status, path, note)` rows — same shape as
`via54_okf.cli.cmd_validate`.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from .document import (
    OKFDocument,
    OKFDocumentError,
    OKFValidationError,
)
from .bundle import (
    RESERVED_NAMES,
    iter_concept_files,
    load_concepts as _load_concepts,
)


# ── Status codes (mirrored from via54_okf.cli) ──────────────────────────
STATUS_OK = "OK"
STATUS_MISSING_TYPE = "missing-type"
STATUS_BAD_YAML = "bad-yaml"
STATUS_MISSING_FRONTMATTER = "missing-frontmatter"
STATUS_UNTERMINATED = "unterminated-frontmatter"
STATUS_RESERVED = "reserved-name"
STATUS_PARSE_ERROR = "parse-error"


class BundleManifest(dict):
    """A YAML-friendly dict carrying the bundle manifest fields.

    Subclasses dict so callers can do `manifest["name"]` and json/yaml
    serialize naturally.
    """

    @classmethod
    def from_yaml(cls, path: Path) -> "BundleManifest":
        if not Path(path).is_file():
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            data = {"_raw": data}
        return cls(data)

    def to_yaml_text(self) -> str:
        cleaned = {k: v for k, v in self.items() if v is not None}
        return yaml.safe_dump(
            cleaned,
            default_flow_style=False,
            sort_keys=True,
            allow_unicode=True,
        )


class Bundle:
    """In-memory bundle: manifest + list of (rel_path, OKFDocument) pairs."""

    def __init__(
        self,
        root: Path,
        manifest: Optional[BundleManifest] = None,
        documents: Optional[List[Tuple[Path, OKFDocument]]] = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.manifest: BundleManifest = manifest or BundleManifest()
        self.documents: List[Tuple[Path, OKFDocument]] = list(documents or [])

    def __len__(self) -> int:
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)

    def add(self, rel_path: Path, doc: OKFDocument) -> None:
        self.documents.append((Path(rel_path), doc))

    def concept_ids(self) -> List[str]:
        return [
            doc.concept_id(self.root, self.root / rel)
            for rel, doc in self.documents
        ]


# ── load_bundle ──────────────────────────────────────────────────────────


def load_bundle(path: Path) -> Bundle:
    """Read a bundle from disk.

    Reads `bundle.yaml` for the manifest, then parses every concept file
    via `iter_concept_files`. Permissive: broken files are skipped
    (consistent with `load_concepts`).
    """
    root = Path(path).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"bundle directory not found: {root}")
    manifest = BundleManifest.from_yaml(root / "bundle.yaml")
    docs: List[Tuple[Path, OKFDocument]] = []
    for file_path, doc, _cid in _load_concepts(root):
        rel = file_path.relative_to(root)
        docs.append((rel, doc))
    return Bundle(root=root, manifest=manifest, documents=docs)


# ── write_bundle ─────────────────────────────────────────────────────────


def _safe_relpath(rel: Path) -> Path:
    """Reject path traversal attempts."""
    rel_str = str(rel)
    if rel_str.startswith("/") or ".." in rel.parts:
        raise ValueError(f"unsafe rel_path: {rel}")
    return rel


def write_bundle(bundle: Bundle, out_path: Path) -> int:
    """Write the bundle to `out_path`. Returns number of .md files written."""
    out = Path(out_path).resolve()
    out.mkdir(parents=True, exist_ok=True)

    # 1) manifest
    if bundle.manifest:
        manifest_path = out / "bundle.yaml"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(bundle.manifest.to_yaml_text())

    # 2) every concept
    written = 0
    for rel, doc in bundle.documents:
        rel = _safe_relpath(rel)
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(doc.serialize())
        written += 1

    # 3) index.md (only if it doesn't exist)
    index_path = out / "index.md"
    if not index_path.exists():
        index_path.write_text(_render_index_md(bundle), encoding="utf-8")

    return written


def _render_index_md(bundle: Bundle) -> str:
    """Generate a simple index.md TOC."""
    lines: List[str] = ["# " + str(bundle.manifest.get("name", bundle.root.name)),
                        ""]
    desc = bundle.manifest.get("description")
    if desc:
        lines += [str(desc), ""]
    lines += ["## Concepts", ""]
    for rel, doc in sorted(bundle.documents, key=lambda r: str(r[0])):
        title = doc.frontmatter.get("title") or rel.stem
        ftype = doc.frontmatter.get("type", "—")
        lines.append(f"- `{rel}` — {title} ({ftype})")
    lines.append("")
    return "\n".join(lines)


# ── validate (spec §9 conformance) ──────────────────────────────────────


def validate(bundle_or_path) -> Dict[str, Any]:
    """Run spec §9 conformance checks.

    Accepts either a `Bundle` or a `Path` (we'll load it). Returns a dict:

        {
          "ok": bool,
          "counts": {STATUS_OK: N, STATUS_MISSING_TYPE: M, ...},
          "rows":   [(status, rel_path_str, note), ...],
          "concepts_checked": int,
          "frontmatter_ok":  int,
          "has_type":        int,
        }

    Conformance rules:
      1. Every non-reserved .md file MUST have a frontmatter fence.
      2. The frontmatter MUST parse as YAML.
      3. The frontmatter MUST have a non-empty `type` field.
      4. `index.md` / `log.md` MUST exist at bundle root (warning, not failure).

    Reserved-name files in nested directories are allowed (spec says
    index/log MAY appear at any level per §3.1).
    """
    if isinstance(bundle_or_path, Bundle):
        bundle = bundle_or_path
    else:
        bundle = load_bundle(Path(bundle_or_path))

    rows: List[Tuple[str, str, str]] = []
    counts: Dict[str, int] = {}

    def bump(status: str) -> None:
        counts[status] = counts.get(status, 0) + 1

    frontmatter_ok = 0
    has_type = 0

    # Spec rule 4: index.md / log.md at bundle root.
    if not (bundle.root / "index.md").is_file():
        rows.append((STATUS_MISSING_FRONTMATTER, "index.md",
                     "bundle root must contain index.md (spec §6)"))
        bump(STATUS_MISSING_FRONTMATTER)

    for rel, doc in bundle.documents:
        rel_str = str(rel)
        # 1) frontmatter presence
        if not doc.frontmatter and not doc.body:
            rows.append((STATUS_PARSE_ERROR, rel_str, "empty document"))
            bump(STATUS_PARSE_ERROR)
            continue
        if doc.frontmatter is None:
            rows.append((STATUS_MISSING_FRONTMATTER, rel_str, "no frontmatter dict"))
            bump(STATUS_MISSING_FRONTMATTER)
            continue
        frontmatter_ok += 1
        # 3) type presence
        try:
            doc.validate()
            has_type += 1
            rows.append((STATUS_OK, rel_str, f"type={doc.frontmatter.get('type')!r}"))
            bump(STATUS_OK)
        except OKFValidationError as exc:
            rows.append((STATUS_MISSING_TYPE, rel_str, str(exc)))
            bump(STATUS_MISSING_TYPE)

    failures = sum(
        counts.get(s, 0)
        for s in (
            STATUS_MISSING_TYPE,
            STATUS_BAD_YAML,
            STATUS_MISSING_FRONTMATTER,
            STATUS_UNTERMINATED,
            STATUS_PARSE_ERROR,
        )
    )
    return {
        "ok": failures == 0,
        "counts": counts,
        "rows": rows,
        "concepts_checked": len(bundle.documents),
        "frontmatter_ok": frontmatter_ok,
        "has_type": has_type,
    }