"""
via54_okf — OKF (Open Knowledge Format) bundle handler for via54ADIdeahub.

OKF = structured bundle of markdown documents with YAML frontmatter.
A bundle is a directory with:
  - bundle.yaml          (manifest)
  - case_studies/*.md    (content documents with frontmatter)
  - index.md             (bundle-level TOC)
  - log.md               (change log)

Public surface (re-exported):
    OKFDocument, OKFDocumentError, OKFValidationError
    Document, parse_document, parse_frontmatter   (aliases for v0.1 docstring)
    Bundle, BundleManifest                         (placeholder aliases)
    LinkKind, RESERVED_NAMES
    iter_concept_files, load_concepts, extract_links

Note: the v0.1 docstring also promised `load_bundle`, `write_bundle`, `validate`,
and a `render_document` helper. These are not implemented in v0.1 — see
`via54_okf.cli` for `validate`, and use `OKFDocument.serialize()` for rendering.
"""
from .document import (
    OKFDocument,
    OKFDocumentError,
    OKFValidationError,
)
from .bundle import (
    LinkKind,
    RESERVED_NAMES,
    iter_concept_files,
    load_concepts,
    extract_links,
)

# Aliases — the symbols this package's v0.1 docstring originally promised.
# The canonical names live in .document / .bundle above; these keep earlier
# callers (and the docstring) honest without breaking imports.
Document = OKFDocument
parse_document = OKFDocument.parse
parse_frontmatter = OKFDocument.parse  # whole-document parse; frontmatter is dict
render_document = OKFDocument.serialize

# Real implementations live in `bundle_io.py` to avoid editing the sibling's
# bundle.py. Re-export them here so `from via54_okf import load_bundle` works.
from .bundle_io import (  # noqa: E402
    Bundle as _BundleImpl,
    BundleManifest,
    load_bundle,
    write_bundle,
    validate,
)

# Legacy alias kept for early example code.
Bundle = _BundleImpl  # type: ignore[misc]


def __getattr__(name):
    """Late-bound re-exports for legacy names (load_bundle/write_bundle/validate)."""
    if name in ("load_bundle", "write_bundle", "validate"):
        from . import bundle_io
        return getattr(bundle_io, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "OKFDocument",
    "OKFDocumentError",
    "OKFValidationError",
    "Document",
    "parse_document",
    "render_document",
    "parse_frontmatter",
    "Bundle",
    "BundleManifest",
    "load_bundle",
    "write_bundle",
    "validate",
    "LinkKind",
    "RESERVED_NAMES",
    "iter_concept_files",
    "load_concepts",
    "extract_links",
]

__version__ = "0.1.0"
