#!/usr/bin/env python3
"""Deterministic mechanical assembly of a pilar consolidated draft.

Reads `briefing.md` + every approved pillar (`status: statements-approved`
or `complete`) + `lexicon.md` + `style-guide.md` from the engagement root
and writes `consolidated/<cd-id>.md`. Output bytes are determined by the
inputs — running twice on the same inputs produces identical output.

Per §6.7 of `scp-plugin-spec.md`: consolidation is deterministic mechanical
concatenation; it does not interpret, rewrite, or summarize. The source
pillars remain the canonical state of the engagement; the consolidated
draft is a derived view that is regenerated from the source pillars on
every consolidation. Whole-deliverable review (`/pilar:run-qc
--consolidated`) is read-only per §6.8 — findings are addressed by editing
source pillars and re-consolidating, not by editing the consolidated draft.

Body assembly:

  ## Briefing       — briefing.md body, all ATX headings demoted by 1 level
  ## Pillars        — each approved pillar in pillar-id order, as
                      `### Pillar <pillar-id>: <slug>` with the pillar body
                      reproduced verbatim, all ATX headings demoted by 2
                      levels (so `## Strategic Rationale` becomes `####`,
                      `### SS-NN` becomes `#####`, `#### RS-NN` becomes
                      `######`). Pillar frontmatter and the per-pillar
                      `# Pillar: <name>` H1 are dropped.
  ## Lexicon        — lexicon.md body verbatim (entries are already H3).
  ## Style Guide    — style-guide.md body, all ATX headings demoted by 1
                      level.

Open `GAP-NNN` and `ASP-NNN` register entries are deliberately excluded —
registers are working-state, not deliverable content.

Usage:
    consolidate.py [--engagement-root <path>] [--draft-id <cd-NNN>]
                   [--output <path>] [--dry-run]

Exit codes:
    0 on success
    1 on missing required input or no approved pillars
    2 on usage error (malformed --draft-id)
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent

# Reuse parse_frontmatter from validate-schemas.py. The hyphen in the
# filename prevents a normal `import`; load via importlib.util mirroring
# the pattern used by detect-gaps.py.
_VALIDATOR_PATH = REPO / "scripts" / "validate-schemas.py"
_spec = importlib.util.spec_from_file_location("pilar_validator", _VALIDATOR_PATH)
assert _spec is not None and _spec.loader is not None
_validator: Any = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validator)
parse_frontmatter = _validator.parse_frontmatter

APPROVED_STATUSES = {"statements-approved", "complete"}
ATX_HEADING_RE = re.compile(r"^#{1,6} ")
H1_RE = re.compile(r"^# [^#]")
DRAFT_ID_RE = re.compile(r"^cd-\d{3}$")
DRAFT_FILENAME_RE = re.compile(r"^cd-(\d{3})\.md$")


def demote_headings(text: str, levels: int) -> str:
    """Prepend `levels` `#` characters to every ATX heading line."""
    if levels <= 0:
        return text
    extra = "#" * levels
    lines = []
    for line in text.split("\n"):
        if ATX_HEADING_RE.match(line):
            lines.append(extra + line)
        else:
            lines.append(line)
    return "\n".join(lines)


def strip_h1(body: str) -> str:
    """Drop the first H1 line; also drop a blank line immediately following it."""
    lines = body.split("\n")
    h1_idx = None
    for i, line in enumerate(lines):
        if H1_RE.match(line):
            h1_idx = i
            break
    if h1_idx is None:
        return body
    drop_count = 1
    if h1_idx + 1 < len(lines) and lines[h1_idx + 1].strip() == "":
        drop_count = 2
    return "\n".join(lines[:h1_idx] + lines[h1_idx + drop_count :])


def next_draft_id(consolidated_dir: Path) -> str:
    """Return the next sequential cd-NNN id (highest existing + 1, or cd-001)."""
    if not consolidated_dir.exists():
        return "cd-001"
    nums: list[int] = []
    for f in consolidated_dir.glob("cd-*.md"):
        m = DRAFT_FILENAME_RE.match(f.name)
        if m:
            nums.append(int(m.group(1)))
    if not nums:
        return "cd-001"
    return f"cd-{max(nums) + 1:03d}"


def discover_approved_pillars(pillars_dir: Path) -> list[dict[str, Any]]:
    """Return [{pillar_id, slug, status, body, path}, ...] for approved pillars,
    sorted by pillar_id."""
    if not pillars_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for pf in sorted(pillars_dir.glob("*.md")):
        text = pf.read_text()
        fm, body = parse_frontmatter(text)
        if fm.get("status") not in APPROVED_STATUSES:
            continue
        out.append({
            "path": pf,
            "pillar_id": fm.get("pillar_id", ""),
            "slug": fm.get("slug", ""),
            "status": fm.get("status", ""),
            "body": body,
        })
    out.sort(key=lambda p: p["pillar_id"])
    return out


def assemble(engagement_root: Path, draft_id: str, today: str) -> str:
    briefing_path = engagement_root / "briefing.md"
    lexicon_path = engagement_root / "lexicon.md"
    style_guide_path = engagement_root / "style-guide.md"
    pillars_dir = engagement_root / "pillars"

    briefing_text = briefing_path.read_text()
    lexicon_text = lexicon_path.read_text()
    style_guide_text = style_guide_path.read_text()

    approved = discover_approved_pillars(pillars_dir)
    if not approved:
        raise ValueError(
            "no pillars at status: statements-approved or complete; "
            "consolidation refused (drive at least one pillar through "
            "/pilar:pillar-narrative + /pilar:pillar-statements first)"
        )

    briefing_fm, briefing_body = parse_frontmatter(briefing_text)
    _, lexicon_body = parse_frontmatter(lexicon_text)
    _, style_guide_body = parse_frontmatter(style_guide_text)

    project = briefing_fm.get("project", "unknown")
    pillar_ids = ", ".join(p["pillar_id"] for p in approved)

    parts: list[str] = []
    parts.append("---")
    parts.append("artifact: consolidated-draft")
    parts.append(f"draft_id: {draft_id}")
    parts.append(f"project: {project}")
    parts.append(f"created: {today}")
    parts.append("---")
    parts.append("")
    parts.append(f"# Consolidated Draft {draft_id}")
    parts.append("")
    parts.append(
        f"> Assembled on {today} from `briefing.md` + {len(approved)} "
        f"approved pillars + `lexicon.md` + `style-guide.md` per §6.7 of "
        f"scp-plugin-spec.md."
    )
    parts.append(
        f"> Source pillars: {pillar_ids} (status at assembly time: "
        f"`statements-approved` or `complete`)."
    )
    parts.append(
        "> Open `GAP-NNN` and `ASP-NNN` register entries are deliberately "
        "excluded — registers are working-state, not deliverable content."
    )
    parts.append(
        "> This file is a deterministic mechanical assembly produced by "
        "`scripts/consolidate.py`. It is not edited at the consolidated "
        "stage; whole-deliverable review (`/pilar:run-qc --consolidated`) "
        "is read-only per §6.8 and findings are addressed by editing source "
        "pillars and re-consolidating."
    )
    parts.append("")

    # Briefing — H2s demoted to H3
    parts.append("## Briefing")
    parts.append("")
    bb = strip_h1(briefing_body).strip()
    if bb:
        parts.append(demote_headings(bb, 1))
    parts.append("")

    # Pillars — each pillar's H2s demoted to H4 (and SS H3 → H5, RS H4 → H6)
    parts.append("## Pillars")
    parts.append("")
    for p in approved:
        parts.append(f"### Pillar {p['pillar_id']}: {p['slug']}")
        parts.append("")
        pb = strip_h1(p["body"]).strip()
        if pb:
            parts.append(demote_headings(pb, 2))
        parts.append("")

    # Lexicon — entries already at H3, no demotion
    parts.append("## Lexicon")
    parts.append("")
    lb = strip_h1(lexicon_body).strip()
    if lb:
        parts.append(lb)
    else:
        parts.append(
            "_No lexicon entries yet — to be developed during the engagement "
            "per §6.6._"
        )
    parts.append("")

    # Style guide — H2s demoted to H3 (cascading: ### Overrides → #### Overrides)
    parts.append("## Style Guide")
    parts.append("")
    sb = strip_h1(style_guide_body).strip()
    if sb:
        parts.append(demote_headings(sb, 1))
    parts.append("")

    return "\n".join(parts)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic mechanical assembly of a pilar consolidated draft. "
            "Reads briefing + approved pillars + lexicon + style guide; writes "
            "consolidated/<cd-id>.md."
        )
    )
    parser.add_argument(
        "--engagement-root",
        type=Path,
        default=Path.cwd(),
        help="Path to the engagement repo root (default: cwd).",
    )
    parser.add_argument(
        "--draft-id",
        default=None,
        help="cd-NNN id to assign (default: auto-detect highest existing + 1).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: <engagement-root>/consolidated/<cd-id>.md).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the assembled body to stdout instead of to a file.",
    )
    args = parser.parse_args(argv)

    root: Path = args.engagement_root.resolve()

    for fname in ("briefing.md", "lexicon.md", "style-guide.md"):
        if not (root / fname).exists():
            print(f"::error::missing required file: {root / fname}", file=sys.stderr)
            return 1

    consolidated_dir = root / "consolidated"
    draft_id = args.draft_id or next_draft_id(consolidated_dir)

    if not DRAFT_ID_RE.match(draft_id):
        print(
            f"::error::draft-id must match pattern cd-NNN (got '{draft_id}')",
            file=sys.stderr,
        )
        return 2

    today = datetime.date.today().isoformat()

    try:
        body = assemble(root, draft_id, today)
    except ValueError as e:
        print(f"::error::{e}", file=sys.stderr)
        return 1

    if args.dry_run:
        sys.stdout.write(body)
        return 0

    output_path: Path = args.output or (consolidated_dir / f"{draft_id}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body)

    print(
        f"wrote {output_path} ({len(body)} bytes; draft_id={draft_id}; "
        f"{len(discover_approved_pillars(root / 'pillars'))} pillar(s))",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
