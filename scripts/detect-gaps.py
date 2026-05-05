#!/usr/bin/env python3
"""Detect orphan reference statements (RS) in pillar artifacts.

A reference statement is "orphan" — and therefore a candidate for an entry
in `registers/evidence-gaps.md` — when any of the following is true:

  * its `sources:` line is missing entirely;
  * its `sources:` value is the empty list `[]` or whitespace;
  * its `sources: [<ref-id>, ...]` list cites one or more ref-ids that
    do not exist in `knowledge-base/manifest.md`.

This script is the orphan-RS predicate that `/pilar:ingest-kb` invokes to
propose `GAP-NNN` candidates after manifest changes. It is also runnable
ad-hoc to scan pillars without ingesting:

    python3 scripts/detect-gaps.py pillars knowledge-base/manifest.md

It does not write to evidence-gaps.md. It emits candidates on stdout
(markdown by default; JSON via `--format json`); the caller composes
final `GAP-NNN` entries (the Librarian fills `proposed_search:` from
briefing/audience context, which a Python script cannot do).

Reuses the markdown parsing primitives in `validate-schemas.py`. The
filename's hyphen prevents a normal `import`, hence `importlib.util`.

Exit codes:
  0 — scan completed (orphan count is reported on stderr regardless).
  2 — scan failed (paths invalid, etc.).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "validate_schemas", SCRIPT_DIR / "validate-schemas.py"
)
if _spec is None or _spec.loader is None:
    raise ImportError(
        f"Cannot load validate-schemas.py from {SCRIPT_DIR}"
    )
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)


def extract_manifest_refs(manifest_path: Path) -> set[str]:
    """Return the set of ref-ids in the kb-manifest at `manifest_path`.

    Returns an empty set if the manifest file is missing, has no Entries
    section, or contains only malformed headings — in which case every RS
    is an orphan, the correct behavior when scanning against an empty KB.
    """
    if not manifest_path.is_file():
        return set()
    text = manifest_path.read_text()
    _, body = vs.parse_frontmatter(text)
    entries = vs.section_body(body, "Entries")
    if entries is None:
        return set()
    refs: set[str] = set()
    for title, _ in vs.find_headings(entries, 3):
        rid = vs.heading_id(title)
        if re.match(vs.ID_PATTERNS["ref"], rid):
            refs.add(rid)
    return refs


def check_rs_orphan(
    rs_body: str, composite_id: str, manifest_refs: set[str]
) -> dict | None:
    """Inspect a single RS body. Return an orphan record or None."""
    sources_match = re.search(r"^- sources:\s*(.*?)\s*$", rs_body, re.MULTILINE)

    if sources_match is None:
        return {
            "composite_id": composite_id,
            "reason": "missing sources field",
            "current_sources": [],
            "unresolved_refs": [],
        }

    raw = sources_match.group(1).strip()
    if raw in ("", "[]", "[ ]"):
        return {
            "composite_id": composite_id,
            "reason": "empty sources list",
            "current_sources": [],
            "unresolved_refs": [],
        }

    list_match = re.match(r"^\[(.*)\]$", raw)
    if list_match is None:
        return {
            "composite_id": composite_id,
            "reason": f"malformed sources value: {raw!r}",
            "current_sources": [],
            "unresolved_refs": [],
        }

    refs = [r.strip() for r in list_match.group(1).split(",") if r.strip()]
    if not refs:
        return {
            "composite_id": composite_id,
            "reason": "empty sources list",
            "current_sources": [],
            "unresolved_refs": [],
        }

    unresolved = [r for r in refs if r not in manifest_refs]
    if unresolved:
        joined = ", ".join(unresolved)
        return {
            "composite_id": composite_id,
            "reason": f"unresolved ref-id(s): {joined}",
            "current_sources": refs,
            "unresolved_refs": unresolved,
        }

    return None


def parse_pillar_orphans(
    pillar_path: Path, manifest_refs: set[str]
) -> list[dict]:
    """Walk a pillar's SS/RS structure; return orphan records (possibly empty)."""
    text = pillar_path.read_text()
    fm, body = vs.parse_frontmatter(text)
    pillar_id = fm.get("pillar_id", "")
    if not re.match(vs.ID_PATTERNS["pillar"], pillar_id):
        return []

    ss_section = vs.section_body(body, "Scientific Statements")
    if ss_section is None:
        return []

    ss_headings = vs.find_headings(ss_section, 3)
    orphans: list[dict] = []

    for i, (ss_title, ss_offset) in enumerate(ss_headings):
        ss_id = vs.heading_id(ss_title)
        if not re.match(vs.ID_PATTERNS["ss"], ss_id):
            continue

        ss_body_start = ss_offset + len(f"### {ss_title}")
        ss_body_end = (
            ss_headings[i + 1][1] if i + 1 < len(ss_headings) else len(ss_section)
        )
        ss_body = ss_section[ss_body_start:ss_body_end]

        rs_headings = vs.find_headings(ss_body, 4)
        for j, (rs_title, rs_offset) in enumerate(rs_headings):
            rs_id = vs.heading_id(rs_title)
            if not re.match(vs.ID_PATTERNS["rs"], rs_id):
                continue

            rs_body_start = rs_offset + len(f"#### {rs_title}")
            rs_body_end = (
                rs_headings[j + 1][1] if j + 1 < len(rs_headings) else len(ss_body)
            )
            rs_body = ss_body[rs_body_start:rs_body_end]

            composite_id = f"{pillar_id}.{ss_id}.{rs_id}"
            orphan = check_rs_orphan(rs_body, composite_id, manifest_refs)
            if orphan is not None:
                orphan["pillar_path"] = str(pillar_path)
                orphans.append(orphan)

    return orphans


def collect_pillar_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return [p for p in sorted(target.rglob("*.md")) if p.name != "manifest.md"]
    return []


def render_markdown(orphans: list[dict]) -> str:
    if not orphans:
        return "No orphan reference statements detected.\n"

    lines = [
        f"# Orphan Reference Statements ({len(orphans)})",
        "",
        "Each block below is a candidate `GAP-NNN` for `registers/evidence-gaps.md`. The Librarian fills `proposed_search:` per orphan from briefing/audience context.",
        "",
    ]
    for o in orphans:
        lines.append(f"## {o['composite_id']}")
        lines.append("")
        lines.append(f"- linked_to: {o['composite_id']}")
        lines.append(f"- reason: {o['reason']}")
        if o["current_sources"]:
            lines.append(f"- current_sources: {o['current_sources']}")
        if o["unresolved_refs"]:
            lines.append(f"- unresolved_refs: {o['unresolved_refs']}")
        lines.append(f"- pillar_path: {o['pillar_path']}")
        lines.append("")
    return "\n".join(lines)


def render_json(orphans: list[dict]) -> str:
    return json.dumps(
        {"orphan_count": len(orphans), "orphans": orphans}, indent=2
    ) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Detect orphan reference statements in pillars (P6 Librarian predicate).",
    )
    parser.add_argument(
        "pillars",
        type=Path,
        help="pillars directory or single pillar file",
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="path to knowledge-base/manifest.md",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="stdout format (default: markdown)",
    )
    args = parser.parse_args(argv)

    pillar_files = collect_pillar_files(args.pillars)
    if not pillar_files:
        print(
            f"::error::pillars target is not a file or directory containing pillars: {args.pillars}",
            file=sys.stderr,
        )
        return 2

    manifest_refs = extract_manifest_refs(args.manifest)

    all_orphans: list[dict] = []
    for pf in pillar_files:
        all_orphans.extend(parse_pillar_orphans(pf, manifest_refs))

    if args.format == "json":
        sys.stdout.write(render_json(all_orphans))
    else:
        sys.stdout.write(render_markdown(all_orphans))

    print(
        f"detect-gaps: scanned {len(pillar_files)} pillar(s); "
        f"manifest has {len(manifest_refs)} entries; "
        f"{len(all_orphans)} orphan(s)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
