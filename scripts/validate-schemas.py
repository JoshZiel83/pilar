#!/usr/bin/env python3
"""Validate engagement-level pilar artifacts against schema templates.

Given one or more target paths (files or directories), parses each file's
YAML frontmatter to find its `artifact:` type, looks up the matching schema
template in `schemas/<artifact>.md`, and asserts:

  - every frontmatter key declared in the schema is present in the target;
  - no frontmatter value in the target is a `<placeholder>` left over from
    the template;
  - every H2 heading declared in the schema is present in the target.

Exits non-zero if any check fails. Errors are emitted in GitHub Actions
`::error::` workflow-command format so they surface as PR annotations.

Designed to be dependency-free: parses the strict-subset YAML used by pilar
artifact frontmatter (one `key: value` per line, no nesting) without PyYAML.
Phase 3 may swap in PyYAML if richer schemas demand it.
"""

from __future__ import annotations

import sys
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body) for a markdown document with YAML frontmatter."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5 :]
    fm: dict[str, str] = {}
    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        fm[key.strip()] = value.strip()
    return fm, body


def extract_h2_headings(body: str) -> list[str]:
    return [line[3:].strip() for line in body.split("\n") if line.startswith("## ")]


def is_placeholder(value: str) -> bool:
    return value.startswith("<") and value.endswith(">") and len(value) > 2


def validate(target: Path, schema_dir: Path) -> list[str]:
    if not target.exists():
        return [f"{target}: file does not exist"]

    text = target.read_text()
    fm, body = parse_frontmatter(text)

    if "artifact" not in fm:
        return [f"{target}: missing 'artifact' key in frontmatter"]

    artifact = fm["artifact"]
    schema_path = schema_dir / f"{artifact}.md"
    if not schema_path.exists():
        return [f"{target}: no schema for artifact '{artifact}' (expected {schema_path})"]

    schema_fm, schema_body = parse_frontmatter(schema_path.read_text())

    errors: list[str] = []

    for key in schema_fm:
        if key not in fm:
            errors.append(f"{target}: missing frontmatter key '{key}'")
        elif is_placeholder(fm[key]):
            errors.append(
                f"{target}: frontmatter key '{key}' still has placeholder value '{fm[key]}'"
            )

    schema_headings = set(extract_h2_headings(schema_body))
    target_headings = set(extract_h2_headings(body))
    for h in sorted(schema_headings - target_headings):
        errors.append(f"{target}: missing required H2 heading '## {h}'")

    return errors


def collect_targets(args: list[str]) -> list[Path]:
    targets: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            targets.extend(sorted(p.glob("*.md")))
        else:
            targets.append(p)
    return targets


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: validate-schemas.py <target-file-or-dir>...", file=sys.stderr)
        return 2

    schema_dir = Path(__file__).resolve().parent.parent / "schemas"
    if not schema_dir.is_dir():
        print(f"::error::schemas directory not found: {schema_dir}", file=sys.stderr)
        return 2

    targets = collect_targets(argv)
    if not targets:
        print("::error::no target files found", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for t in targets:
        errors = validate(t, schema_dir)
        all_errors.extend(errors)

    for e in all_errors:
        print(f"::error::{e}")

    summary = f"Validated {len(targets)} file(s); {len(all_errors)} error(s)"
    print(summary, file=sys.stderr)

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
