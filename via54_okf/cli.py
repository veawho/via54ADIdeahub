"""CLI entry point for via54_okf.

Usage:
  python -m via54_okf validate <bundle_dir>

Subcommands:
  validate  — scan a bundle, parse every concept file, report status
              (OK / missing-type / bad-yaml / reserved-name misuse /
              not-a-concept).  Exits 0 if every concept is OK,
              1 otherwise.
  export    — NOT IMPLEMENTED (planned for v0.2)
  import    — NOT IMPLEMENTED (planned for v0.2)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from . import __version__
from .bundle import (
    RESERVED_NAMES,
    LinkKind,
    iter_concept_files,
    load_concepts,
)
from .document import OKFDocument, OKFDocumentError, OKFValidationError


# Status codes for the validate subcommand.
STATUS_OK = "OK"
STATUS_MISSING_TYPE = "missing-type"
STATUS_BAD_YAML = "bad-yaml"
STATUS_MISSING_FRONTMATTER = "missing-frontmatter"
STATUS_UNTERMINATED = "unterminated-frontmatter"
STATUS_RESERVED = "reserved-name"
STATUS_PARSE_ERROR = "parse-error"


def cmd_validate(bundle_dir: Path) -> int:
    """Scan ``bundle_dir``, report per-file status. Returns process exit code."""
    bundle_dir = Path(bundle_dir).resolve()
    if not bundle_dir.is_dir():
        print(f"ERROR: bundle directory not found: {bundle_dir}", file=sys.stderr)
        return 2

    rows: List[Tuple[str, str, str]] = []  # (status, rel_path, note)
    counts: Dict[str, int] = {}

    def bump(status: str) -> None:
        counts[status] = counts.get(status, 0) + 1

    # 1) Walk every .md file (including reserved) so we can flag
    #    reserved-name usage as well as missing frontmatter.
    for md_path in sorted(bundle_dir.rglob("*.md")):
        # Skip hidden directories.
        rel = md_path.relative_to(bundle_dir)
        if any(part.startswith(".") for part in rel.parts[:-1]):
            continue

        name = md_path.name
        rel_str = rel.as_posix()

        if name in RESERVED_NAMES:
            # Reserved files have spec-defined purpose (§6, §7) and are
            # permitted — we just confirm they exist; we don't parse
            # their frontmatter (spec says index.md MAY have one in
            # bundle-root only; log.md never).
            rows.append((STATUS_OK, rel_str, "reserved file (index/log)"))
            bump(STATUS_OK)
            continue

        # Non-reserved .md file — it MUST be a concept with frontmatter.
        try:
            text = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            rows.append((STATUS_PARSE_ERROR, rel_str, f"read error: {exc}"))
            bump(STATUS_PARSE_ERROR)
            continue

        try:
            doc = OKFDocument.parse(text)
        except OKFDocumentError as exc:
            msg = str(exc)
            if "missing opening frontmatter fence" in msg:
                status = STATUS_MISSING_FRONTMATTER
            elif "unterminated frontmatter fence" in msg:
                status = STATUS_UNTERMINATED
            elif "invalid YAML" in msg:
                status = STATUS_BAD_YAML
            else:
                status = STATUS_PARSE_ERROR
            rows.append((status, rel_str, msg))
            bump(status)
            continue

        # Parsed successfully — now validate spec requirements.
        try:
            doc.validate()
        except OKFValidationError as exc:
            rows.append((STATUS_MISSING_TYPE, rel_str, str(exc)))
            bump(STATUS_MISSING_TYPE)
            continue

        rows.append((STATUS_OK, rel_str, f"type={doc.frontmatter.get('type')!r}"))
        bump(STATUS_OK)

    # 2) Print a tabular report.
    print(f"\nvia54_okf validate — bundle: {bundle_dir}")
    print(f"version: {__version__}\n")

    status_w = max(len(s) for s, _, _ in rows) if rows else 8
    status_w = max(status_w, len("STATUS"))
    path_w = max(len(p) for _, p, _ in rows) if rows else 8
    path_w = max(path_w, len("PATH"))

    print(f"  {'STATUS':<{status_w}}  {'PATH':<{path_w}}  NOTE")
    print(f"  {'-' * status_w}  {'-' * path_w}  {'-' * 40}")
    for status, path, note in rows:
        print(f"  {status:<{status_w}}  {path:<{path_w}}  {note}")

    print("\nSummary:")
    for status in sorted(counts.keys()):
        print(f"  {status:<24}  {counts[status]}")
    print(f"  {'TOTAL':<24}  {sum(counts.values())}")

    # Exit code: 0 only if no failures.
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
    return 0 if failures == 0 else 1


def main(argv=None) -> int:  # type: ignore[assignment]
    parser = argparse.ArgumentParser(
        prog="via54_okf",
        description="Open Knowledge Format v0.1 — bundle scanner & validator",
    )
    parser.add_argument(
        "--version", action="version", version=f"via54_okf {__version__}"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_validate = sub.add_parser(
        "validate", help="scan a bundle and report per-file OK/error status"
    )
    p_validate.add_argument(
        "bundle_dir", type=Path, help="path to the bundle directory"
    )

    # export/import are stubs for v0.2 — registered so `python -m via54_okf export`
    # gives a clean error rather than "unrecognized command".
    p_export = sub.add_parser(
        "export", help="NOT IMPLEMENTED (planned for v0.2)"
    )
    p_export.add_argument("bundle_dir", type=Path)
    p_import = sub.add_parser(
        "import", help="NOT IMPLEMENTED (planned for v0.2)"
    )
    p_import.add_argument("bundle_dir", type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "validate":
        return cmd_validate(args.bundle_dir)
    if args.cmd == "export":
        print(
            "ERROR: 'export' is not implemented in via54_okf v0.1. "
            "Planned for v0.2.",
            file=sys.stderr,
        )
        return 2
    if args.cmd == "import":
        print(
            "ERROR: 'import' is not implemented in via54_okf v0.1. "
            "Planned for v0.2.",
            file=sys.stderr,
        )
        return 2

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())